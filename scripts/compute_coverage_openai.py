#!/usr/bin/env python
"""Compute NovBench Coverage using OpenAI text-embedding-3-small via OpenRouter.

Coverage metric definition from NovBench:
For each human-written novelty remark g in G:
  sim(g, m) = cos(emb(g), emb(m)) for all generated sentences m in M
  g is considered 'covered' if max_{m in M} cos(emb(g), emb(m)) >= tau (default tau = 0.70)
Coverage = (1 / |G|) * sum_{g in G} 1[max_{m in M} cos(emb(g), m) >= tau]
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any
import httpx
import numpy as np
from dotenv import load_dotenv

load_dotenv(".env")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
EMBEDDING_MODEL = "openai/text-embedding-3-small"


def split_sentences(text: str) -> list[str]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    sents = []
    for line in lines:
        if line.startswith("#") or line.startswith("Step"):
            line = re.sub(r"^(#+|\bStep\s*\d+\s*\[[^\]]+\]:?)", "", line).strip()
        if not line:
            continue
        parts = re.split(r"(?<=[.!?。！？])\s+", line)
        for p in parts:
            p = p.strip()
            if len(p) > 15:
                sents.append(p)
    return sents if sents else [text]


async def fetch_embeddings_batch(
    client: httpx.AsyncClient,
    texts: list[str],
    batch_size: int = 100,
    concurrency: int = 5,
) -> np.ndarray:
    url = f"{OPENROUTER_BASE_URL.rstrip('/')}/embeddings"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    chunks = [texts[i : i + batch_size] for i in range(0, len(texts), batch_size)]
    results: list[list[float]] = [None] * len(texts)  # type: ignore
    sem = asyncio.Semaphore(concurrency)

    async def get_chunk(chunk_idx: int, chunk_texts: list[str]):
        async with sem:
            for attempt in range(4):
                try:
                    resp = await client.post(
                        url,
                        headers=headers,
                        json={"model": EMBEDDING_MODEL, "input": chunk_texts},
                        timeout=30.0,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        items = sorted(data["data"], key=lambda x: x["index"])
                        start = chunk_idx * batch_size
                        for offset, item in enumerate(items):
                            results[start + offset] = item["embedding"]
                        return
                    else:
                        print(f"Warning: chunk {chunk_idx} status {resp.status_code}: {resp.text[:100]}")
                        await asyncio.sleep(2 ** attempt)
                except Exception as e:
                    print(f"Error chunk {chunk_idx} attempt {attempt+1}: {e}")
                    await asyncio.sleep(2 ** attempt)
            raise RuntimeError(f"Failed to fetch embeddings for chunk {chunk_idx}")

    tasks = [get_chunk(i, c) for i, c in enumerate(chunks)]
    await asyncio.gather(*tasks)
    arr = np.array(results, dtype=np.float32)
    # L2 normalize
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return arr / norms


async def evaluate_dataset(
    client: httpx.AsyncClient,
    ref_path: str,
    judge_path: str,
    thresholds: tuple[float, ...] = (0.60, 0.65, 0.70, 0.75, 0.80),
) -> dict[str, Any]:
    ref_by_id = {}
    with open(ref_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            ref_by_id[rec["paper_id"]] = rec

    judge_by_id = {}
    with open(judge_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            judge_by_id[rec["paper_id"]] = rec

    dims = ["problem_novelty", "method_novelty", "scenario_novelty", "insight_novelty"]

    all_texts = []
    text_to_idx = {}

    def get_idx(t: str) -> int:
        if t not in text_to_idx:
            text_to_idx[t] = len(all_texts)
            all_texts.append(t)
        return text_to_idx[t]

    dim_paper_data = {d: [] for d in dims}

    for pid, rrec in ref_by_id.items():
        if pid not in judge_by_id:
            continue
        jrec = judge_by_id[pid]
        extracted = rrec.get("extracted", {})

        for dim in dims:
            remarks = extracted.get(dim, [])
            g_texts = [
                r.get("quote", "").strip()
                for r in remarks
                if len(r.get("quote", "").strip()) > 10
            ]
            if not g_texts:
                continue

            j_reasoning = jrec.get("dimensions", {}).get(dim, {}).get("reasoning", "")
            if not j_reasoning:
                continue
            m_texts = split_sentences(j_reasoning)

            g_idxs = [get_idx(t) for t in g_texts]
            m_idxs = [get_idx(t) for t in m_texts]
            dim_paper_data[dim].append((pid, g_idxs, m_idxs))

    print(f"Total unique texts to embed: {len(all_texts)}")
    if not all_texts:
        return {}

    embeddings = await fetch_embeddings_batch(client, all_texts, batch_size=80, concurrency=8)

    results = {}
    for dim in dims:
        paper_data = dim_paper_data[dim]
        if not paper_data:
            continue

        all_max_sims = []
        for pid, g_idxs, m_idxs in paper_data:
            g_embs = embeddings[g_idxs]
            m_embs = embeddings[m_idxs]
            sim_matrix = np.dot(g_embs, m_embs.T)
            paper_max_sims = np.max(sim_matrix, axis=1)
            all_max_sims.extend(paper_max_sims.tolist())

        all_max_sims = np.array(all_max_sims)
        cov_dict = {}
        for tau in thresholds:
            cov_dict[f"tau_{tau:.2f}"] = round(float(np.mean(all_max_sims >= tau) * 100), 2)

        results[dim] = {
            "n_papers": len(paper_data),
            "n_human_remarks": len(all_max_sims),
            "mean_max_similarity": round(float(np.mean(all_max_sims)), 4),
            "coverage_%": cov_dict,
        }

    return results


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Coverage of human novelty remarks by judge reasoning (OpenAI embeddings)."
    )
    parser.add_argument("--human", required=True, help="JSONL from novelty_reference.py")
    parser.add_argument("--judge", required=True, help="JSONL from judge_iclr_novelty.py")
    parser.add_argument("--out", default="outputs/coverage_openai_results.json")
    parser.add_argument("--name", default="run")
    args = parser.parse_args()

    async with httpx.AsyncClient() as client:
        result = await evaluate_dataset(client, args.human, args.judge)

    payload = {args.name: result}
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
