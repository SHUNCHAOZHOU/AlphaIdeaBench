#!/usr/bin/env python
"""Run Virtual-Scientists (VirSci) ideation on an AlphaIdeaBench topic.

The baseline is used as-is; nothing under baseline/ is modified. Original
VirSci needs an AMiner author graph, FAISS paper indexes, and Ollama. To
compare it with AI-Scientist-v2 on the same topic we:

- pin the workshop (including Budget) instead of letting agents pick a field
- retrieve related papers via Semantic Scholar instead of the private FAISS DB
- keep VirSci's two-scientist discussion, idea JSON, novelty vote, and abstract
- call OpenRouter so the same DeepSeek model can be used

Example:
    python scripts/run_virtualscientists_ideation.py \
        --topic data/topics/icbinb.md \
        --model deepseek/deepseek-v4-flash-0731 \
        --n 1
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import Any

import openai
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = REPO_ROOT / "baseline/Virtual-Scientists"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
S2_BASE = "https://api.semanticscholar.org/graph/v1"

SCIENTIST_SPECS = (
    {
        "name": "Scientist0",
        "role": (
            "You are Scientist0, a senior researcher in applied deep learning "
            "and medical / scientific imaging. You care about annotation noise, "
            "dataset bias, evaluation pitfalls, and negative results. You prefer "
            "public datasets and experiments that fit an academic-lab GPU budget. "
            "You are the team leader: integrate teammates' comments and keep the "
            "proposal inside the assigned workshop."
        ),
    },
    {
        "name": "Scientist1",
        "role": (
            "You are Scientist1, a researcher in robustness, calibration, and "
            "reliability of deep learning. You push the team toward honest "
            "failure-mode analysis, strong baselines, at least one ablation, "
            "and claims that can be tested within the stated budget."
        ),
    },
    {
        "name": "Scientist2",
        "role": (
            "You are Scientist2, a researcher in ML evaluation methodology. "
            "You question overclaimed SOTA numbers, leakage, and brittle "
            "benchmarks, and you insist that a negative result still needs a "
            "precise hypothesis and a reproducible protocol."
        ),
    },
)


def _reasoning_of(message) -> str:
    chunks: list[str] = []
    for attr in ("reasoning", "reasoning_content"):
        value = getattr(message, attr, None)
        if value:
            chunks.append(str(value))
    dump = message.model_dump() if hasattr(message, "model_dump") else {}
    if isinstance(dump, dict):
        for key in ("reasoning", "reasoning_content"):
            value = dump.get(key)
            if isinstance(value, str) and value.strip():
                chunks.append(value)
            elif isinstance(value, dict) and value.get("content"):
                chunks.append(str(value["content"]))
    seen: set[str] = set()
    unique: list[str] = []
    for item in chunks:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return "\n".join(unique)


class OpenRouterClient:
    def __init__(
        self,
        model: str,
        api_key: str,
        *,
        timeout_s: float = 180,
        max_tokens: int = 8192,
        temperature: float = 0.5,
    ) -> None:
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout_s = timeout_s
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            timeout=timeout_s,
            max_retries=0,
        )
        self._pool = ThreadPoolExecutor(max_workers=8)

    def _complete(self, messages: list[dict[str, str]], max_tokens: int):
        return self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=self.temperature,
            extra_body={"reasoning": {"max_tokens": 1024, "exclude": False}},
        )

    def call(self, messages: list[dict[str, str]], max_retries: int = 3) -> str:
        last_error: Exception | None = None
        for attempt in range(1, max_retries + 1):
            print(
                f"[llm] calling {self.model} attempt {attempt}/{max_retries} "
                f"(timeout={self.timeout_s:.0f}s max_tokens={self.max_tokens})",
                flush=True,
            )
            try:
                future = self._pool.submit(self._complete, messages, self.max_tokens)
                try:
                    response = future.result(timeout=self.timeout_s)
                except FuturesTimeoutError as exc:
                    raise TimeoutError(f"LLM call exceeded {self.timeout_s:.0f}s") from exc
                message = response.choices[0].message
                content = (message.content or "").strip()
                reasoning = _reasoning_of(message)
                if not content:
                    content = reasoning.strip()
                elif "```json" not in content and "```json" in reasoning:
                    content = f"{reasoning}\n{content}".strip()
                usage = {}
                if response.usage:
                    usage = {
                        "prompt_tokens": response.usage.prompt_tokens or 0,
                        "completion_tokens": response.usage.completion_tokens or 0,
                    }
                print(
                    f"[llm] ok {self.model} chars={len(content)} "
                    f"reasoning_chars={len(reasoning)} tokens={usage}",
                    flush=True,
                )
                if not content:
                    raise RuntimeError("empty LLM content")
                return content
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                wait = min(2**attempt, 16)
                print(f"[llm] failed attempt {attempt}: {exc}\n[llm] retry in {wait}s", flush=True)
                time.sleep(wait)
        raise RuntimeError(f"LLM request failed after {max_retries} retries: {last_error}") from last_error


def load_prompts(baseline: Path):
    prompt_path = baseline / "sci_platform" / "utils" / "prompt.py"
    if not prompt_path.is_file():
        raise SystemExit(f"Virtual-Scientists prompts not found at {prompt_path}")
    spec = importlib.util.spec_from_file_location("virsci_prompt", prompt_path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Could not load {prompt_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Prompts


def topic_to_workshop(topic) -> str:
    keywords = ", ".join(topic.keywords) if topic.keywords else topic.field
    return (
        f"# Title: {topic.title}\n\n"
        f"## Keywords\n{keywords}\n\n"
        f"## TL;DR\nPropose research ideas under this workshop. "
        f"Every experiment must fit the budget below.\n\n"
        f"{topic.budget.to_markdown()}\n\n"
        f"## Abstract\n{topic.body.strip()}\n"
    )


def _s2_headers(api_key: str | None) -> dict[str, str]:
    return {"x-api-key": api_key} if api_key else {}


def s2_get(path: str, params: dict[str, Any], api_key: str | None, timeout: int = 60) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    url = f"{S2_BASE}{path}?{query}" if query else f"{S2_BASE}{path}"
    req = urllib.request.Request(url, headers=_s2_headers(api_key))
    last_error: Exception | None = None
    for attempt in range(1, 5):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return payload if isinstance(payload, dict) else {}
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503}:
                raise
            time.sleep(min(2**attempt, 16))
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(min(2**attempt, 16))
    raise RuntimeError(f"Semantic Scholar request failed: {last_error}") from last_error


def search_related_papers(query: str, api_key: str | None, limit: int) -> list[dict[str, Any]]:
    print(f"[s2] search query={query!r} limit={limit}", flush=True)
    payload = s2_get(
        "/paper/search",
        {
            "query": query,
            "limit": max(1, limit),
            "fields": "paperId,title,abstract,year,citationCount",
        },
        api_key,
    )
    papers = []
    for item in payload.get("data") or []:
        if not isinstance(item, dict) or not item.get("title") or not item.get("abstract"):
            continue
        papers.append(
            {
                "paperId": item.get("paperId"),
                "title": item.get("title"),
                "abstract": item.get("abstract"),
                "year": item.get("year"),
            }
        )
    print(f"[s2] related papers with abstract: {len(papers)}", flush=True)
    return papers


def format_paper_reference(papers: list[dict[str, Any]]) -> str:
    if not papers:
        return "No retrieved papers."
    chunks = []
    for i, paper in enumerate(papers, start=1):
        year = f" ({paper['year']})" if paper.get("year") else ""
        chunks.append(
            f"Paper {i}:\nTitle: {paper.get('title')}{year}\n"
            f"Abstract: {paper.get('abstract')}"
        )
    return "\n".join(chunks)


def extract_json_block(text: str) -> str:
    blocks = re.findall(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if blocks:
        return blocks[0].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        return text[start : end + 1]
    return text


def parse_jsonish(text: str) -> dict[str, Any]:
    blob = extract_json_block(text or "")
    start = blob.find("{")
    end = blob.rfind("}")
    snippet = blob[start : end + 1] if start != -1 and end > start else blob
    try:
        parsed = json.loads(snippet)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _intish(value: Any) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    match = re.search(r"\d+", str(value))
    return int(match.group()) if match else None


def idea_mark(parsed: dict[str, Any]) -> int:
    clarity = _intish(parsed.get("Clarity")) or 0
    feasibility = _intish(parsed.get("Feasibility")) or 0
    novelty = _intish(parsed.get("Novelty")) or 0
    return clarity + feasibility + 2 * novelty


def scientist_sys_prompt(spec: dict[str, str], workshop: str, prompts) -> str:
    return (
        f"{spec['role']}\n\n{prompts.role}\n\n"
        "The team MUST stay inside this workshop and budget:\n\n"
        f"{workshop}"
    )


def chat(client: OpenRouterClient, sys_prompt: str, user: str) -> str:
    return client.call(
        [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user},
        ]
    )


def select_topic(client, scientists, workshop, prompts, discuss_iters: int) -> tuple[str, list[str]]:
    history: list[str] = []
    scoped = (
        f"{prompts.to_start_topic_discussion}\n\n"
        "The research topic MUST be a concrete direction inside the workshop "
        "below, not a different field.\n\n"
        f"{workshop}"
    )
    for turn in range(discuss_iters):
        for spec, sys_prompt in scientists:
            prior = "\n\n".join(history[-6:]) if history else "(none yet)"
            reply = chat(
                client,
                sys_prompt,
                f"{scoped}\n\nSummarizations of previous turns:\n{prior}\n\n"
                f"You are {spec['name']}. Continue the discussion.",
            )
            history.append(f"{spec['name']}: {reply}")
            print(f"[topic] {spec['name']} turn {turn + 1}/{discuss_iters} chars={len(reply)}", flush=True)

    leader_spec, leader_sys = scientists[0]
    topic_user = prompts.to_ask_topic.replace("[history_prompt]", "\n\n".join(history))
    topic_user += (
        "\n\nStay inside the assigned workshop. Output one Selected Topic only."
    )
    raw = chat(client, leader_sys, topic_user)
    parsed = parse_jsonish(raw)
    selected = (
        str(parsed.get("Selected Topic") or parsed.get("Selected Topics") or "").strip()
        or raw.strip()
    )
    print(f"[topic] selected: {selected[:200]}", flush=True)
    return selected, history


def generate_ideas(
    client,
    scientists,
    prompts,
    selected_topic: str,
    papers: list[dict[str, Any]],
    s2_key: str | None,
    cite_number: int,
    discuss_iters: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    paper_ref = format_paper_reference(papers)
    candidates: list[dict[str, Any]] = []
    marks: list[int] = []
    traces: list[str] = []
    old_idea = "None"

    for turn in range(discuss_iters):
        for spec, sys_prompt in scientists:
            user = (
                prompts.prompt_task
                + prompts.prompt_existing_idea.format(old_idea)
                + prompts.prompt_topic.format(selected_topic)
                + prompts.prompt_reference.format(paper_ref)
                + prompts.prompt_response
            )
            reply = chat(client, sys_prompt, user)
            traces.append(f"{spec['name']} idea turn {turn + 1}: {reply}")
            parsed = parse_jsonish(reply)
            if not parsed.get("Title") and not parsed.get("Idea"):
                print(f"[idea] {spec['name']} produced no parseable idea", flush=True)
                continue
            old_idea = json.dumps(parsed, ensure_ascii=False)
            mark = idea_mark(parsed)
            candidates.append(parsed)
            marks.append(mark)
            print(
                f"[idea] {spec['name']} {parsed.get('Title', '')!r} mark={mark}",
                flush=True,
            )
            query = str(parsed.get("Title") or parsed.get("Idea") or selected_topic)
            try:
                extra = search_related_papers(query[:180], s2_key, cite_number)
            except Exception as exc:  # noqa: BLE001
                print(f"[s2] idea-title search failed ({exc})", flush=True)
                extra = []
            seen = {p.get("title") for p in papers}
            for paper in extra:
                if paper.get("title") not in seen:
                    papers.append(paper)
                    seen.add(paper.get("title"))
            paper_ref = format_paper_reference(papers[:cite_number])

    if not candidates:
        raise RuntimeError("Virtual-Scientists produced no idea JSON.")
    ranked = sorted(range(len(candidates)), key=lambda i: marks[i], reverse=True)
    keep = [candidates[i] for i in ranked[:3]]
    return keep, papers, traces


def check_novelty(
    client,
    scientists,
    prompts,
    candidates: list[dict[str, Any]],
    papers: list[dict[str, Any]],
    discuss_iters: int,
) -> dict[str, Any]:
    if len(candidates) == 1:
        return candidates[0]
    idea_choices = ""
    for i, idea in enumerate(candidates):
        idea_choices += f"Idea {i}:\n{json.dumps(idea, ensure_ascii=False)}\n"
    paper_ref = format_paper_reference(papers[:8])
    votes: list[int] = []
    for turn in range(max(1, discuss_iters)):
        for spec, sys_prompt in scientists:
            user = prompts.prompt_idea_check + prompts.prompt_idea_check_response.replace(
                "{existing_idea}", idea_choices
            ).replace("{last_query_results}", paper_ref)
            reply = chat(client, sys_prompt, user)
            parsed = parse_jsonish(reply)
            decision = str(parsed.get("Decision Made") or reply)
            match = re.search(r"\d+", decision)
            choice = int(match.group()) if match else 0
            if choice < 0 or choice >= len(candidates):
                choice = 0
            votes.append(choice)
            print(f"[novelty] {spec['name']} chose Idea {choice}", flush=True)
    winner = max(set(votes), key=votes.count) if votes else 0
    return candidates[winner]


def generate_abstract(
    client,
    scientists,
    prompts,
    idea: dict[str, Any],
    discuss_iters: int,
) -> str:
    idea_blob = json.dumps(idea, ensure_ascii=False)
    old_abstract = None
    last = ""
    for turn in range(max(1, discuss_iters)):
        for spec, sys_prompt in scientists:
            if old_abstract is None:
                user = (
                    f"{prompts.prompt_abstract}\n{idea_blob}\n"
                    f"{prompts.prompt_abstract_requirement}\n"
                    f"{prompts.prompt_abstract_response}"
                )
            else:
                user = (
                    prompts.prompt_abstract_judgement.replace("[Insert abstract here]", old_abstract)
                    + prompts.prompt_abstract_revise_response
                )
            reply = chat(client, sys_prompt, user)
            last = reply
            blob = extract_json_block(reply)
            old_abstract = blob or reply
            print(f"[abstract] {spec['name']} turn {turn + 1} chars={len(old_abstract)}", flush=True)
    return old_abstract or last


def run_team(
    *,
    client: OpenRouterClient,
    prompts,
    workshop: str,
    topic_title: str,
    scientists,
    papers: list[dict[str, Any]],
    s2_key: str | None,
    cite_number: int,
    discuss_iters: int,
    skip_novelty: bool,
) -> dict[str, Any]:
    selected_topic, topic_trace = select_topic(
        client, scientists, workshop, prompts, discuss_iters
    )
    candidates, papers, idea_trace = generate_ideas(
        client,
        scientists,
        prompts,
        f"{selected_topic}\n\nWorkshop: {topic_title}",
        list(papers),
        s2_key,
        cite_number,
        discuss_iters,
    )
    if skip_novelty:
        idea = candidates[0]
    else:
        idea = check_novelty(client, scientists, prompts, candidates, papers, discuss_iters)
    abstract = generate_abstract(client, scientists, prompts, idea, discuss_iters)
    return {
        "teammate": [spec["name"] for spec, _ in scientists],
        "topic": selected_topic,
        "idea": idea,
        "candidates": candidates,
        "abstract": abstract,
        "related_titles": [p.get("title") for p in papers if p.get("title")],
        "related_papers": papers,
        "topic_discussion": topic_trace,
        "idea_discussion": idea_trace,
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--topic", required=True, help="AlphaIdeaBench 课题 markdown")
    parser.add_argument(
        "--model",
        default=os.getenv("IDEATION_MODEL") or os.getenv("model") or "deepseek/deepseek-v4-flash-0731",
        help="OpenRouter slug，例如 deepseek/deepseek-v4-flash-0731",
    )
    parser.add_argument("--n", type=int, default=1, help="独立跑几次团队 pipeline")
    parser.add_argument("--members", type=int, default=2, help="团队人数（含 leader），对应 VirSci max_team_member")
    parser.add_argument(
        "--discuss-iters",
        type=int,
        default=2,
        help="每个阶段的讨论轮数，对应 VirSci max_discuss_iteration",
    )
    parser.add_argument("--related-k", type=int, default=8, help="检索多少篇相关论文（VirSci cite_number）")
    parser.add_argument("--search-query", help="覆盖默认的 Semantic Scholar 检索词")
    parser.add_argument("--skip-novelty", action="store_true", help="跳过 novelty vote，直接用最高分 idea")
    parser.add_argument("--out", help="输出 JSON，默认 outputs/virtualscientists/<topic_id>.json")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE), help="Virtual-Scientists 根目录")
    parser.add_argument("--max-tokens", type=int, default=8192, help="每次 LLM 调用的 max_tokens")
    parser.add_argument("--timeout", type=float, default=180, help="单次 LLM 超时秒数")
    parser.add_argument("--print-seed", action="store_true", help="只打印 workshop 和相关论文后退出")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    load_dotenv()

    if not os.getenv("S2_API_KEY") and os.getenv("SEMANTIC_SCHOLAR_API_KEY"):
        os.environ["S2_API_KEY"] = os.environ["SEMANTIC_SCHOLAR_API_KEY"]
    s2_key = os.getenv("S2_API_KEY")
    if not s2_key:
        print(
            "[ideation] warning: no S2_API_KEY / SEMANTIC_SCHOLAR_API_KEY; "
            "Semantic Scholar search may be rate-limited."
        )

    from alphaideabench.domain.topic import Topic
    from alphaideabench.ideas_io import idea_from_virtualscientists

    topic = Topic.from_markdown(args.topic)
    workshop = topic_to_workshop(topic)
    query = args.search_query or (" ".join(topic.keywords) if topic.keywords else topic.title)
    members = max(1, min(args.members, len(SCIENTIST_SPECS)))

    references: list[dict[str, Any]] = []
    for candidate in [query, topic.title]:
        if not candidate:
            continue
        try:
            references = search_related_papers(candidate, s2_key, args.related_k)
        except Exception as exc:  # noqa: BLE001
            print(f"[s2] search failed for {candidate!r} ({exc})")
            continue
        if references:
            break
        time.sleep(1.0)

    print(f"[ideation] seed workshop: {topic.title}")
    for index, paper in enumerate(references, start=1):
        year = f" ({paper['year']})" if paper.get("year") else ""
        print(f"  related {index}. {paper.get('title')}{year}")

    if args.print_seed:
        print("\n--- workshop ---\n")
        print(workshop)
        return 0

    baseline = Path(args.baseline).resolve()
    prompts = load_prompts(baseline)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set (put it in .env).")

    out = Path(args.out) if args.out else REPO_ROOT / "outputs" / "virtualscientists" / f"{topic.id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    raw_path = out.with_suffix(".raw.jsonl")

    client = OpenRouterClient(
        model=args.model,
        api_key=api_key,
        timeout_s=args.timeout,
        max_tokens=args.max_tokens,
        temperature=0.5,
    )
    scientists = []
    for spec in SCIENTIST_SPECS[:members]:
        scientists.append((spec, scientist_sys_prompt(spec, workshop, prompts)))

    print(
        f"[ideation] topic={topic.id} model={args.model} n={args.n} "
        f"members={members} discuss_iters={args.discuss_iters} out={out}"
    )

    ideas = []
    used_names: set[str] = set()
    with raw_path.open("w", encoding="utf-8") as raw_file:
        for index in range(args.n):
            print(f"[pipeline] team {index + 1}/{args.n}", flush=True)
            context = run_team(
                client=client,
                prompts=prompts,
                workshop=workshop,
                topic_title=topic.title,
                scientists=scientists,
                papers=list(references),
                s2_key=s2_key,
                cite_number=args.related_k,
                discuss_iters=args.discuss_iters,
                skip_novelty=args.skip_novelty,
            )
            raw_file.write(json.dumps(_jsonable(context), ensure_ascii=False) + "\n")
            raw_file.flush()

            idea = idea_from_virtualscientists(context, topic)
            name = (idea.extra.get("virtual_scientists") or {}).get("Name") or f"idea_{index + 1}"
            if name in used_names:
                name = f"{name}_{index + 1}"
                idea.extra["virtual_scientists"]["Name"] = name
            used_names.add(name)
            idea.topic_id = topic.id
            idea.idea_id = f"{topic.id}-{name}"
            ideas.append(idea)
            print(f"[ideation] {idea.idea_id}: {idea.title}", flush=True)

    if not ideas:
        print("[ideation] no idea was produced; nothing written.")
        return 1

    out.write_text(
        json.dumps([idea.model_dump() for idea in ideas], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[ideation] wrote {len(ideas)} idea(s) to {out}")
    print(f"[ideation] raw team context: {raw_path}")
    print("Next:")
    print(f"  alphaideabench judge --topic {args.topic} --ideas {out} --repeats 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
