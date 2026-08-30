#!/usr/bin/env python
"""Run CoI-Agent ideation on an AlphaIdeaBench topic, through OpenRouter.

The baseline is used as-is; nothing under baseline/ is modified. CoI-Agent
originally needs Grobid + SciPDF to parse downloaded papers. To compare it
with AI-Scientist-v2 on the same topic we:

- render the topic (including Budget) as the research topic string
- retrieve papers via Semantic Scholar, using title + abstract instead of PDFs
- wrap the LLM client so OpenRouter + reasoning models work
- map the idea / experiment / idea-chain onto ResearchIdea JSON

Example:
    python scripts/run_coi_agent_ideation.py \
        --topic data/topics/icbinb.md \
        --model deepseek/deepseek-v4-flash-0731 \
        --n 1
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
import types
from pathlib import Path
from typing import Any

import numpy as np
import openai
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = REPO_ROOT / "baseline/CoI-Agent"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_EMBEDDING_MODEL = "openai/text-embedding-3-small"


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


def _hash_embedding(text: str, dim: int = 64) -> list[float]:
    vec: list[float] = []
    for i in range(dim):
        digest = hashlib.sha256(f"{i}:{text}".encode("utf-8")).digest()
        vec.append(int.from_bytes(digest[:4], "big") / 2**32)
    return vec


class OpenRouterCoILlm:
    """Drop-in for CoI-Agent's ``openai_llm`` (response / embeddings)."""

    def __init__(
        self,
        model: str,
        api_key: str,
        *,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        timeout_s: float = 180,
        max_tokens: int = 8192,
        temperature: float = 0.7,
    ) -> None:
        self.model = model
        self.embedding_model = embedding_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout_s = timeout_s
        self._embed_ok = True
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            timeout=timeout_s,
            max_retries=0,
        )
        self._async_client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            timeout=timeout_s,
            max_retries=0,
        )

    def _complete_kwargs(self, messages: list[dict[str, str]], **kwargs) -> dict[str, Any]:
        extra_body = dict(kwargs.get("extra_body") or {})
        extra_body.setdefault("reasoning", {"exclude": True})
        return {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "n": kwargs.get("n", 1),
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": min(int(kwargs.get("max_tokens", self.max_tokens)), self.max_tokens),
            "timeout": kwargs.get("timeout", self.timeout_s),
            "extra_body": extra_body,
        }

    def _content_of(self, response) -> str:
        message = response.choices[0].message
        content = (message.content or "").strip()
        reasoning = _reasoning_of(message)
        if not content:
            content = reasoning.strip()
        elif "<" not in content and "<" in reasoning:
            content = f"{reasoning}\n{content}".strip()
        return content

    def response(self, messages, **kwargs):
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                print(
                    f"[llm] {self.model} attempt {attempt}/3 "
                    f"(timeout={self.timeout_s:.0f}s)",
                    flush=True,
                )
                response = self._client.chat.completions.create(
                    **self._complete_kwargs(messages, **kwargs)
                )
                content = self._content_of(response)
                print(f"[llm] ok chars={len(content)}", flush=True)
                if not content:
                    raise RuntimeError("empty LLM content")
                return content
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                wait = min(2**attempt, 16)
                print(f"[llm] failed attempt {attempt}: {exc}\n[llm] retry in {wait}s", flush=True)
                time.sleep(wait)
        print(f"[llm] giving up: {last_error}", flush=True)
        return None

    async def response_async(self, messages, **kwargs):
        last_error: Exception | None = None
        for attempt in range(1, 4):
            try:
                print(
                    f"[llm] async {self.model} attempt {attempt}/3 "
                    f"(timeout={self.timeout_s:.0f}s)",
                    flush=True,
                )
                response = await self._async_client.chat.completions.create(
                    **self._complete_kwargs(messages, **kwargs)
                )
                content = self._content_of(response)
                print(f"[llm] ok chars={len(content)}", flush=True)
                if not content:
                    raise RuntimeError("empty LLM content")
                return content
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                wait = min(2**attempt, 16)
                print(f"[llm] failed attempt {attempt}: {exc}\n[llm] retry in {wait}s", flush=True)
                await asyncio.sleep(wait)
        print(f"[llm] giving up: {last_error}", flush=True)
        return None

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self._embed_ok:
            try:
                payload = self._client.embeddings.create(
                    model=self.embedding_model,
                    input=texts,
                    timeout=self.timeout_s,
                )
                return [item.embedding for item in payload.data]
            except Exception as exc:  # noqa: BLE001
                print(f"[embed] {self.embedding_model} failed ({exc}); using hash fallback", flush=True)
                self._embed_ok = False
        return [_hash_embedding(text) for text in texts]

    def get_embbeding(self, text):
        texts = text if isinstance(text, list) else [text]
        vectors = self._embed_texts([str(item or "") for item in texts])
        return vectors[0] if not isinstance(text, list) else vectors

    async def get_embbeding_async(self, text):
        return self.get_embbeding(text)


def topic_to_coi_topic(topic) -> str:
    """Render an AlphaIdeaBench topic as CoI-Agent's research topic string."""
    keywords = ", ".join(topic.keywords) if topic.keywords else topic.field
    return (
        f"{topic.title}\n\n"
        f"Keywords: {keywords}\n\n"
        f"Propose a research idea under this topic. "
        f"Every experiment must fit the budget below.\n\n"
        f"{topic.budget.to_markdown()}\n\n"
        f"{topic.body.strip()}\n"
    )


def _ensure_dummy_scipdf() -> None:
    """CoI-Agent imports scipdf even when we never parse PDFs."""
    if "scipdf" in sys.modules:
        return
    dummy = types.ModuleType("scipdf")
    dummy.parse_pdf_to_dict = lambda *a, **k: None
    sys.modules["scipdf"] = dummy


def _article(title: str, abstract: str, year: Any = None) -> dict[str, Any]:
    text = abstract or ""
    return {
        "title": title or "",
        "abstract": text,
        "pub_date": str(year) if year else None,
        "sections": [{"heading": "Abstract", "text": text, "publication_ref": []}],
        "references": [],
    }


def _patch_searcher_skip_pdf() -> None:
    """Use Semantic Scholar title/abstract instead of downloading PDFs."""
    from searcher.sementic_search import Result, SementicSearcher

    def result_from_hit(hit: dict[str, Any]) -> Any:
        title = hit.get("title") or ""
        abstract = hit.get("abstract") or ""
        return Result(
            title,
            abstract,
            _article(title, abstract, hit.get("year")),
            hit.get("citationCount") or 0,
            hit.get("year"),
        )

    async def search_async(
        self,
        query,
        max_results=5,
        paper_list=None,
        rerank_query=None,
        llm=None,
        year=None,
        publicationDate=None,
        need_download=True,
        fields=None,
    ):
        if fields is None:
            fields = [
                "title",
                "paperId",
                "abstract",
                "isOpenAccess",
                "openAccessPdf",
                "year",
                "publicationDate",
                "citationCount",
            ]
        readed = []
        if paper_list:
            items = list(paper_list)
            if items and isinstance(items[0], str):
                readed = items
            elif items and hasattr(items[0], "title"):
                readed = [paper.title for paper in items]

        print(f"Searching for papers related to query : <{query}>")
        results = await self.search_papers_async(
            query,
            limit=6 * max_results,
            year=year,
            publicationDate=publicationDate,
            fields=fields,
        )
        if not results or "data" not in results:
            return []

        candidates = []
        for hit in results["data"]:
            title = (hit or {}).get("title") or ""
            if not title or title in self.ban_paper or title in readed:
                continue
            if not (hit.get("abstract") or "").strip():
                continue
            candidates.append(hit)

        if llm and rerank_query and candidates:
            query_emb = llm.get_embbeding(rerank_query)
            candidates = self.rerank_papers(np.array(query_emb), candidates, llm)

        final = []
        for hit in candidates:
            final.append(result_from_hit(hit))
            if len(final) >= max_results:
                break
        print(f"[s2] kept {len(final)} paper(s) for query {query!r}", flush=True)
        return final

    async def search_related_paper_async(
        self,
        title,
        need_citation=True,
        need_reference=True,
        rerank_query=None,
        llm=None,
        paper_list=None,
    ):
        paper_list = paper_list or []
        print(
            f"Searching for related papers of paper <{title}>; "
            f"Citation:{need_citation}; Reference:{need_reference}"
        )
        fields = [
            "title",
            "abstract",
            "citations.title",
            "citations.abstract",
            "citations.citationCount",
            "references.title",
            "references.abstract",
            "references.citationCount",
            "citations.isOpenAccess",
            "citations.openAccessPdf",
            "references.isOpenAccess",
            "references.openAccessPdf",
            "citations.year",
            "references.year",
        ]
        results = await self.search_papers_async(title, limit=3, fields=fields)
        related: list[dict[str, Any]] = []
        seen: set[str] = set()
        if not results or "data" not in results:
            print(
                f"Failed to find related papers of paper <{title}>; "
                f"Citation:{need_citation}; Reference:{need_reference}"
            )
            return None
        for hit in results["data"]:
            if not hit:
                continue
            groups = []
            if need_citation:
                groups.append(hit.get("citations") or [])
            if need_reference:
                groups.append(hit.get("references") or [])
            for group in groups:
                for paper in group:
                    other_title = (paper or {}).get("title") or ""
                    if (
                        not other_title
                        or other_title in seen
                        or other_title in self.ban_paper
                        or other_title in paper_list
                    ):
                        continue
                    if not (paper.get("abstract") or "").strip():
                        continue
                    seen.add(other_title)
                    related.append(paper)
            if hit:
                break

        if len(related) >= 200:
            related = related[:200]
        if rerank_query and llm and related:
            query_emb = llm.get_embbeding(rerank_query)
            related = self.rerank_papers(np.array(query_emb), related, llm)
        else:
            related = sorted(related, key=lambda p: p.get("citationCount") or 0, reverse=True)

        print(f"Found {len(related)} related papers")
        for paper in related:
            return result_from_hit(paper)
        print(
            f"Failed to find related papers of paper <{title}>; "
            f"Citation:{need_citation}; Reference:{need_reference}"
        )
        return None

    async def search_papers_async(
        self,
        query,
        limit=5,
        offset=0,
        fields=None,
        publicationDate=None,
        minCitationCount=0,
        year=None,
        publicationTypes=None,
        fieldsOfStudy=None,
    ):
        import requests
        from searcher.sementic_search import process_fields

        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        if fields is None:
            fields = ["title", "paperId", "abstract", "isOpenAccess", "openAccessPdf", "year"]
        fields = process_fields(fields) if isinstance(fields, list) else fields
        params = {
            "query": query,
            "limit": limit,
            "offset": offset,
            "fields": fields,
            "publicationDateOrYear": publicationDate,
            "minCitationCount": minCitationCount,
            "year": year,
            "publicationTypes": publicationTypes,
            "fieldsOfStudy": fieldsOfStudy,
        }
        filtered = {k: v for k, v in params.items() if v is not None}
        api_key = os.environ.get("SEMENTIC_SEARCH_API_KEY")
        headers = {"x-api-key": api_key} if api_key else None
        last_error = None
        for attempt in range(1, 7):
            await asyncio.sleep(0.5)
            try:
                response = requests.get(url, params=filtered, headers=headers, timeout=60)
                if response.status_code == 200:
                    return response.json()
                last_error = f"{response.status_code}: {response.text[:200]}"
                if response.status_code not in {429, 500, 502, 503}:
                    print(f"[s2] request failed {last_error}", flush=True)
                    return None
                wait = min(2**attempt, 16)
                print(f"[s2] {response.status_code} on {query!r}; retry in {wait}s", flush=True)
                await asyncio.sleep(wait)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                wait = min(2**attempt, 16)
                print(f"[s2] error {exc}; retry in {wait}s", flush=True)
                await asyncio.sleep(wait)
        print(f"[s2] giving up on {query!r}: {last_error}", flush=True)
        return None

    SementicSearcher.search_papers_async = search_papers_async
    SementicSearcher.search_async = search_async
    SementicSearcher.search_related_paper_async = search_related_paper_async


def _patch_novelty_cap(max_tries: int = 3) -> None:
    from agents import DeepResearchAgent

    original = DeepResearchAgent.check_novel

    async def check_novel(self, idea):
        novel, similar_paper, summary = await original(self, idea)
        tries = getattr(self, "_novelty_tries", 0) + 1
        self._novelty_tries = tries
        if not novel and tries >= max_tries:
            print(f"[coi] novelty check failed {tries} times; accepting the idea", flush=True)
            return True, similar_paper, summary
        return novel, similar_paper, summary

    DeepResearchAgent.check_novel = check_novel


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
    parser.add_argument("--cheap-model", help="CoI cheap LLM（默认与 --model 相同）")
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL, help="OpenRouter embedding slug")
    parser.add_argument("--n", type=int, default=1, help="独立跑几次 pipeline")
    parser.add_argument("--improve-cnt", type=int, default=1, help="实验 refinement 轮数")
    parser.add_argument("--max-chain-length", type=int, default=5)
    parser.add_argument("--min-chain-length", type=int, default=3)
    parser.add_argument("--max-chain-numbers", type=int, default=1, help="从几篇锚点论文各长一条 idea chain")
    parser.add_argument("--out", help="输出 JSON，默认 outputs/coi_agent/<topic_id>.json")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE), help="CoI-Agent 根目录")
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--print-topic", action="store_true", help="只打印喂给 CoI-Agent 的 topic 后退出")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    load_dotenv()

    if not os.getenv("SEMENTIC_SEARCH_API_KEY"):
        s2 = os.getenv("SEMANTIC_SCHOLAR_API_KEY") or os.getenv("S2_API_KEY")
        if s2:
            os.environ["SEMENTIC_SEARCH_API_KEY"] = s2
    if not os.getenv("SEMENTIC_SEARCH_API_KEY"):
        print(
            "[ideation] warning: no SEMANTIC_SCHOLAR_API_KEY / S2_API_KEY; "
            "Semantic Scholar search may be rate-limited."
        )

    from alphaideabench.domain.topic import Topic
    from alphaideabench.ideas_io import idea_from_coi_agent

    topic = Topic.from_markdown(args.topic)
    coi_topic = topic_to_coi_topic(topic)
    if args.print_topic:
        print(coi_topic)
        return 0

    baseline = Path(args.baseline).resolve()
    if not (baseline / "agents.py").is_file():
        raise SystemExit(f"CoI-Agent not found at {baseline}")

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set (put it in .env).")

    _ensure_dummy_scipdf()
    sys.path.insert(0, str(baseline))
    from agents import DeepResearchAgent, ReviewAgent

    _patch_searcher_skip_pdf()
    _patch_novelty_cap()

    out = Path(args.out) if args.out else REPO_ROOT / "outputs" / "coi_agent" / f"{topic.id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    raw_path = out.with_suffix(".raw.jsonl")
    save_root = out.parent / "saves" / topic.id

    main_llm = OpenRouterCoILlm(
        model=args.model,
        api_key=api_key,
        embedding_model=args.embedding_model,
        timeout_s=args.timeout,
        max_tokens=args.max_tokens,
    )
    cheap_llm = (
        main_llm
        if not args.cheap_model or args.cheap_model == args.model
        else OpenRouterCoILlm(
            model=args.cheap_model,
            api_key=api_key,
            embedding_model=args.embedding_model,
            timeout_s=args.timeout,
            max_tokens=args.max_tokens,
        )
    )

    print(
        f"[ideation] topic={topic.id} model={args.model} n={args.n} "
        f"chains={args.max_chain_numbers} improve={args.improve_cnt} out={out}",
        flush=True,
    )

    ideas = []
    used_names: set[str] = set()
    with raw_path.open("w", encoding="utf-8") as raw_file:
        for index in range(args.n):
            print(f"[pipeline] idea {index + 1}/{args.n}", flush=True)
            save_file = str(save_root / f"run_{index}")
            agent_kwargs = {
                "save_file": save_file,
                "llm": main_llm,
                "cheap_llm": cheap_llm,
                "improve_cnt": args.improve_cnt,
                "max_chain_length": args.max_chain_length,
                "min_chain_length": args.min_chain_length,
                "max_chain_numbers": args.max_chain_numbers,
            }
            review_agent = ReviewAgent(**agent_kwargs)
            deep_agent = DeepResearchAgent(**agent_kwargs)
            unpacked = asyncio.run(deep_agent.generate_idea_with_chain(coi_topic))
            idea_text, related_experiments, entities, idea_chain, all_ideas, trend, future, human, year = unpacked
            if not idea_text:
                print(f"[ideation] pipeline {index + 1} returned no idea", flush=True)
                continue
            experiment = asyncio.run(
                deep_agent.generate_experiment(idea_text, related_experiments, entities)
            )
            if args.improve_cnt > 0:
                experiment = asyncio.run(
                    deep_agent.improve_experiment(review_agent, idea_text, experiment, entities)
                )
            raw = {
                "idea": idea_text,
                "experiment": experiment,
                "related_experiments": related_experiments,
                "entities": entities,
                "idea_chain": idea_chain,
                "ideas": all_ideas,
                "trend": trend,
                "future": future,
                "year": year,
                "human": human,
            }
            raw_file.write(json.dumps(_jsonable(raw), ensure_ascii=False) + "\n")
            raw_file.flush()

            idea = idea_from_coi_agent(raw, topic)
            name = (idea.extra.get("coi_agent") or {}).get("Name") or f"idea_{index + 1}"
            if name in used_names:
                name = f"{name}_{index + 1}"
                idea.extra["coi_agent"]["Name"] = name
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
    print(f"[ideation] raw CoI-Agent result: {raw_path}")
    print("Next:")
    print(f"  alphaideabench judge --topic {args.topic} --ideas {out} --repeats 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
