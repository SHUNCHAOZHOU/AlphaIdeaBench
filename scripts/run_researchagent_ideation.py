#!/usr/bin/env python
"""Run ResearchAgent ideation on an AlphaIdeaBench topic, through OpenRouter.

The baseline is used as-is; nothing under baseline/ is modified. ResearchAgent
originally starts from a Semantic Scholar paper. To compare it with
AI-Scientist-v2 on the same topic we:

- render the topic (including Budget) as the seed "paper"
- retrieve related papers via the Semantic Scholar search API
- wrap the LLM client so OpenRouter + reasoning models work
- map the problem / method / experiment triple onto ResearchIdea JSON

Example:
    python scripts/run_researchagent_ideation.py \
        --topic data/topics/icbinb.md \
        --model deepseek/deepseek-v4-flash-0731 \
        --n 1 --iterations 3
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
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
DEFAULT_BASELINE = REPO_ROOT / "baseline/ResearchAgent"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
S2_BASE = "https://api.semanticscholar.org/graph/v1"


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
    """Drop-in for ResearchAgent's OpenAIClient.call(messages=...)."""

    def __init__(
        self,
        model: str,
        api_key: str,
        *,
        timeout_s: float = 180,
        max_tokens: int = 8192,
        temperature: float = 1.25,
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

    def _complete(
        self,
        messages: list[dict[str, str]],
        max_tokens: int,
        *,
        temperature: float | None = None,
        reasoning_tokens: int = 512,
    ):
        return self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=self.temperature if temperature is None else temperature,
            extra_body={"reasoning": {"max_tokens": reasoning_tokens, "exclude": False}},
        )

    def _extract_text(self, response) -> str:
        message = response.choices[0].message
        content = (message.content or "").strip()
        reasoning = _reasoning_of(message)
        if not content:
            content = reasoning.strip()
        elif "Problem:" not in content and "Method:" not in content and "Experiment:" not in content and "Review:" not in content:
            if any(marker in reasoning for marker in ("Problem:", "Method:", "Experiment:", "Review:")):
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
        return content

    def _reformat(self, kind: str, raw: str) -> str:
        if kind == "review":
            instruction = (
                "Rewrite the text into exactly this format:\n"
                "Review: <short review>\nFeedback: <short feedback>\nRating (1-5): <integer 1-5>\n"
            )
        else:
            label = {"problem": "Problem", "method": "Method", "experiment": "Experiment"}[kind]
            instruction = (
                f"Rewrite the text into exactly this format:\n"
                f"{label}: <one or two short paragraphs>\n"
                f"Rationale: <one or two short paragraphs>\n"
            )
        messages = [
            {"role": "system", "content": "You only rewrite text into the requested format. No markdown."},
            {"role": "user", "content": f"{instruction}\n\nText:\n{raw[:8000]}"},
        ]
        print(f"[llm] reformatting as {kind}", flush=True)
        future = self._pool.submit(
            self._complete, messages, 800, temperature=0.2, reasoning_tokens=256
        )
        response = future.result(timeout=min(90, self.timeout_s))
        return self._extract_text(response)

    def call(self, messages: list[dict[str, str]], max_retries: int = 3) -> str:
        last_error: Exception | None = None
        last_user = next((m.get("content") or "" for m in reversed(messages) if m.get("role") == "user"), "")
        kind = _requested_format(last_user)
        max_tokens = 2048 if kind == "review" else min(self.max_tokens, 4096)
        for attempt in range(1, max_retries + 1):
            print(
                f"[llm] calling {self.model} attempt {attempt}/{max_retries} "
                f"(timeout={self.timeout_s:.0f}s max_tokens={max_tokens})",
                flush=True,
            )
            try:
                future = self._pool.submit(self._complete, messages, max_tokens)
                try:
                    response = future.result(timeout=self.timeout_s)
                except FuturesTimeoutError as exc:
                    raise TimeoutError(f"LLM call exceeded {self.timeout_s:.0f}s") from exc
                content = self._extract_text(response)
                if not content:
                    raise RuntimeError("empty LLM content")
                if kind and not _matches_format(kind, content):
                    try:
                        repaired = self._reformat(kind, content)
                        if _matches_format(kind, repaired):
                            return repaired
                    except Exception as exc:  # noqa: BLE001
                        print(f"[llm] reformat failed: {exc}", flush=True)
                return content
            except Exception as exc:  # noqa: BLE001 — retry then surface
                last_error = exc
                wait = min(2**attempt, 16)
                print(f"[llm] failed attempt {attempt}: {exc}\n[llm] retry in {wait}s", flush=True)
                time.sleep(wait)
        raise RuntimeError(f"LLM request failed after {max_retries} retries: {last_error}") from last_error


def _requested_format(user: str) -> str | None:
    if "Rating (1-5):" in user:
        return "review"
    if "format of \nProblem:" in user or "format of \nProblem: \nRationale:" in user:
        return "problem"
    if "format of \nMethod:" in user:
        return "method"
    if "format of \nExperiment:" in user:
        return "experiment"
    return None


def _matches_format(kind: str, text: str) -> bool:
    if kind == "review":
        return bool(re.search(r"Review:\s*.+\s*Rating", text, re.DOTALL | re.IGNORECASE))
    label = {"problem": "Problem", "method": "Method", "experiment": "Experiment"}[kind]
    return bool(re.search(rf"{label}:\s*.+?\s*Rationale:\s*.+", text, re.DOTALL))


def _shorten_references(references: list[dict[str, Any]], limit: int = 400) -> list[dict[str, Any]]:
    shortened = []
    for paper in references:
        item = dict(paper)
        abstract = item.get("abstract") or ""
        if len(abstract) > limit:
            item["abstract"] = abstract[:limit].rstrip() + "…"
        shortened.append(item)
    return shortened


def _pick_best(items: list[dict], key: str):
    from utils.evaluation import get_avg_feedbacks_score, get_num_feedbacks_scores

    def score(item: dict) -> float:
        feedbacks = item.get("feedbacks") or {}
        if get_num_feedbacks_scores(feedbacks) > 0:
            return get_avg_feedbacks_score(feedbacks)
        return -1.0

    if not items:
        return {}
    best = max(items, key=score)
    return {
        key: best.get(key),
        f"{key}_rationale": best.get("rationale"),
        f"{key}_feedbacks": best.get("feedbacks"),
    }


def _save_progress(context: dict, topic, out: Path, raw_path: Path) -> None:
    from alphaideabench.ideas_io import idea_from_researchagent

    raw_path.write_text(json.dumps(_jsonable(context), ensure_ascii=False) + "\n", encoding="utf-8")
    idea = idea_from_researchagent(context, topic)
    extra = idea.extra.setdefault("researchagent", {})
    name = extra.get("Name") or "idea"
    extra["Name"] = name
    idea.topic_id = topic.id
    idea.idea_id = f"{topic.id}-{name}"
    out.write_text(json.dumps([idea.model_dump()], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"[checkpoint] wrote {out} "
        f"(problem={bool(idea.problem)} method={bool(idea.method)} experiments={bool(idea.experiments)})",
        flush=True,
    )


def run_pipeline_checkpointed(pipeline, context: dict, topic, out: Path, raw_path: Path) -> dict:
    """Same 3-stage loop as ResearchPipeline, but write after every stage and never drop work."""
    history = {"problems": [], "methods": [], "experiments": []}
    context = dict(context)

    def save() -> None:
        context["history"] = history
        _save_progress(context, topic, out, raw_path)

    stages = [
        ("problem", "problems", pipeline.problem_identifier, pipeline.problem_validator, "problem"),
        ("method", "methods", pipeline.method_developer, pipeline.method_validator, "method"),
        ("experiment", "experiments", pipeline.experiment_designer, pipeline.experiment_validator, "experiment"),
    ]
    try:
        for label, hist_key, identifier, validator, field in stages:
            for i in range(pipeline.iterations):
                print(f"[pipeline] {label} {i + 1}/{pipeline.iterations}", flush=True)
                try:
                    context.update(identifier.run(context))
                except Exception as exc:  # noqa: BLE001
                    print(f"[pipeline] {label} generate failed: {exc}", flush=True)
                try:
                    context.update(validator.run(context))
                except Exception as exc:  # noqa: BLE001
                    print(f"[pipeline] {label} validate failed: {exc}", flush=True)
                    context.setdefault(f"{field}_feedbacks", {})
                history[hist_key].append(
                    {
                        field: context.get(field),
                        "rationale": context.get(f"{field}_rationale"),
                        "feedbacks": context.get(f"{field}_feedbacks"),
                    }
                )
                save()
            picked = _pick_best(history[hist_key], field)
            context.update(picked)
            save()
    finally:
        save()
    return context


def topic_to_paper(topic) -> dict[str, str]:
    """Render an AlphaIdeaBench topic as ResearchAgent's seed paper."""
    keywords = ", ".join(topic.keywords) if topic.keywords else topic.field
    abstract = (
        f"Keywords: {keywords}\n\n"
        f"TL;DR: Propose research ideas under this topic. "
        f"Every experiment must fit the budget below.\n\n"
        f"{topic.budget.to_markdown()}\n\n"
        f"{topic.body.strip()}\n"
    )
    return {"title": topic.title, "abstract": abstract}


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
            "fields": "paperId,corpusId,title,abstract,year,citationCount",
        },
        api_key,
    )
    papers = []
    for item in payload.get("data") or []:
        if not isinstance(item, dict):
            continue
        if not item.get("title") or not item.get("abstract"):
            continue
        papers.append(
            {
                "paperId": item.get("paperId"),
                "corpusId": item.get("corpusId"),
                "title": item.get("title"),
                "abstract": item.get("abstract"),
                "year": item.get("year"),
            }
        )
    print(f"[s2] related papers with abstract: {len(papers)}", flush=True)
    return papers


def fetch_paper(paper_id: str, api_key: str | None) -> dict[str, Any]:
    payload = s2_get(
        f"/paper/{urllib.parse.quote(paper_id, safe=':')}",
        {"fields": "paperId,corpusId,title,abstract,year,citationCount,referenceCount"},
        api_key,
    )
    if not payload.get("title") or not payload.get("abstract"):
        raise SystemExit(f"Semantic Scholar paper {paper_id} is missing title/abstract.")
    return payload


def fetch_references(paper_id: str, api_key: str | None, limit: int) -> list[dict[str, Any]]:
    payload = s2_get(
        f"/paper/{urllib.parse.quote(paper_id, safe=':')}/references",
        {
            "fields": "isInfluential,citedPaper.paperId,citedPaper.title,citedPaper.abstract,citedPaper.year",
            "limit": 100,
        },
        api_key,
    )
    scored: list[tuple[int, dict[str, Any]]] = []
    for item in payload.get("data") or []:
        cited = (item or {}).get("citedPaper") or {}
        if not cited.get("title") or not cited.get("abstract"):
            continue
        scored.append(
            (
                1 if item.get("isInfluential") else 0,
                {
                    "paperId": cited.get("paperId"),
                    "title": cited.get("title"),
                    "abstract": cited.get("abstract"),
                    "year": cited.get("year"),
                },
            )
        )
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [paper for _, paper in scored[:limit]]


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items() if k != "embedding"}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _ensure_tqdm() -> None:
    try:
        import tqdm  # noqa: F401
    except ImportError as exc:
        raise SystemExit("ResearchAgent needs tqdm. Install it with: pip install tqdm") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--topic", required=True, help="AlphaIdeaBench 课题 markdown")
    parser.add_argument(
        "--model",
        default=os.getenv("IDEATION_MODEL") or os.getenv("model") or "deepseek/deepseek-v4-flash-0731",
        help="OpenRouter slug，例如 deepseek/deepseek-v4-flash-0731",
    )
    parser.add_argument("--n", type=int, default=1, help="生成几条 idea（独立跑几次 pipeline）")
    parser.add_argument("--iterations", type=int, default=3, help="problem/method/experiment 各自迭代轮数")
    parser.add_argument("--related-k", type=int, default=5, help="检索多少篇相关论文")
    parser.add_argument("--search-query", help="覆盖默认的 Semantic Scholar 检索词")
    parser.add_argument(
        "--paper-id",
        help="改用真实 Semantic Scholar 论文作 seed（paperId / CorpusId:… / DOI:…）",
    )
    parser.add_argument("--out", help="输出 JSON，默认 outputs/researchagent/<topic_id>.json")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE), help="ResearchAgent 根目录")
    parser.add_argument("--max-tokens", type=int, default=8192, help="每次 LLM 调用的 max_tokens")
    parser.add_argument("--timeout", type=float, default=180, help="单次 LLM 超时秒数")
    parser.add_argument("--print-seed", action="store_true", help="只打印 seed paper 和相关论文后退出")
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
    from alphaideabench.ideas_io import idea_from_researchagent

    topic = Topic.from_markdown(args.topic)
    query = args.search_query or (
        " ".join(topic.keywords) if topic.keywords else topic.title
    )

    if args.paper_id:
        fetched = fetch_paper(args.paper_id, s2_key)
        seed = {
            "title": fetched["title"],
            "abstract": (
                f"{fetched['abstract']}\n\n"
                f"This idea must address the following topic and budget.\n"
                f"# {topic.title}\n\n{topic.budget.to_markdown()}\n"
            ),
        }
        references = fetch_references(fetched.get("paperId") or args.paper_id, s2_key, args.related_k)
        print(f"[ideation] seed paper from S2: {seed['title']}")
    else:
        seed = topic_to_paper(topic)
        references = []
        queries = [query]
        if topic.title and topic.title != query:
            queries.append(topic.title)
        for candidate in queries:
            try:
                references = search_related_papers(candidate, s2_key, args.related_k)
            except Exception as exc:  # noqa: BLE001
                print(f"[s2] search failed for {candidate!r} ({exc})")
                continue
            if references:
                break
            time.sleep(1.0)
        references = _shorten_references(references)
        print(f"[ideation] seed paper from topic: {seed['title']}")

    references = _shorten_references(references)
    entities = list(topic.keywords)
    for index, paper in enumerate(references, start=1):
        year = f" ({paper['year']})" if paper.get("year") else ""
        print(f"  related {index}. {paper.get('title')}{year}")

    if args.print_seed:
        print("\n--- seed abstract ---\n")
        print(seed["abstract"])
        return 0

    baseline = Path(args.baseline).resolve()
    code_dir = baseline / "code"
    if not (code_dir / "pipelines" / "research_pipeline.py").is_file():
        raise SystemExit(f"ResearchAgent not found at {baseline}")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set (put it in .env).")

    _ensure_tqdm()
    sys.path.insert(0, str(code_dir))
    from pipelines.research_pipeline import ResearchPipeline

    out = Path(args.out) if args.out else REPO_ROOT / "outputs" / "researchagent" / f"{topic.id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    raw_path = out.with_suffix(".raw.jsonl")

    client = OpenRouterClient(
        model=args.model,
        api_key=api_key,
        timeout_s=args.timeout,
        max_tokens=args.max_tokens,
    )

    print(
        f"[ideation] topic={topic.id} model={args.model} n={args.n} "
        f"iterations={args.iterations} out={out}"
    )

    ideas = []
    used_names: set[str] = set()
    for index in range(args.n):
        print(f"[pipeline] idea {index + 1}/{args.n}")
        pipeline = ResearchPipeline(api_client=client, iterations=args.iterations)
        context = run_pipeline_checkpointed(
            pipeline,
            {
                "paper": dict(seed),
                "references": list(references),
                "entities": list(entities),
            },
            topic,
            out if args.n == 1 else out.with_name(f"{out.stem}_{index + 1}{out.suffix}"),
            raw_path if args.n == 1 else raw_path.with_name(f"{raw_path.stem}_{index + 1}{raw_path.suffix}"),
        )
        idea = idea_from_researchagent(context, topic)
        name = (idea.extra.get("researchagent") or {}).get("Name") or f"idea_{index + 1}"
        if name in used_names:
            name = f"{name}_{index + 1}"
            idea.extra["researchagent"]["Name"] = name
        used_names.add(name)
        idea.topic_id = topic.id
        idea.idea_id = f"{topic.id}-{name}"
        if not idea.problem or not idea.method or not idea.experiments:
            print(
                f"[ideation] warning: incomplete idea {idea.idea_id} "
                f"(problem={bool(idea.problem)} method={bool(idea.method)} "
                f"experiments={bool(idea.experiments)})"
            )
        ideas.append(idea)
        print(f"[ideation] {idea.idea_id}: {idea.title}")

    if not ideas:
        print("[ideation] no idea was produced; nothing written.")
        return 1

    out.write_text(
        json.dumps([idea.model_dump() for idea in ideas], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"[ideation] wrote {len(ideas)} idea(s) to {out}")
    print(f"[ideation] raw pipeline context: {raw_path}")
    print("Next:")
    print(f"  alphaideabench judge --topic {args.topic} --ideas {out} --repeats 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
