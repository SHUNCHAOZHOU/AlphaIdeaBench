#!/usr/bin/env python
"""Align LLM judge scores with scores mapped from human review comments.

This script does not re-score papers. It takes two already-written score dumps
and reports how close the judge is to the human-anchored reference:

- DistAcc: 1 minus half the L1 gap between the 1-5 histograms
- MAD: mean absolute difference
- Within +/- 1
- Exact agreement after rounding
- 3-class accuracy (1-2 / 3 / 4-5)
- Spearman rho

Human scores usually come from ``map_reviews_to_dimensions.py`` or
``novelty_reference.py``. Judge scores come from ``alphaideabench judge`` or
``judge_iclr_novelty.py``. Uncovered human facets (reviewers never mentioned
that dimension) are skipped, not filled with 3.

Examples:
    python scripts/align_judge_to_human.py \\
        --judge examples/alignment/judge_scores.json \\
        --human examples/alignment/human_scores.json

    python scripts/align_judge_to_human.py \\
        --judge outputs/judge_iclr_novelty/records.jsonl \\
        --human outputs/novelty_reference/paper/papers.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        rows = []
        for line in text.splitlines():
            line = line.strip()
            if line:
                rows.append(json.loads(line))
        return rows
    return json.loads(text)


def _three_class(score: float) -> str:
    if score <= 2:
        return "low"
    if score >= 4:
        return "high"
    return "mid"


def _histogram(scores: list[float]) -> list[float]:
    counts = Counter(int(round(s)) for s in scores)
    n = len(scores) or 1
    return [counts.get(i, 0) / n for i in range(1, 6)]


def _dist_acc(judge: list[float], human: list[float]) -> float:
    pj = _histogram(judge)
    ph = _histogram(human)
    return 1.0 - 0.5 * sum(abs(a - b) for a, b in zip(pj, ph))


def _pairs_from_simple(rows: list[dict[str, Any]]) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for row in rows:
        pid = str(row.get("id") or row.get("paper_id") or row.get("idea_id") or "")
        dim = str(row.get("dimension") or row.get("dimension_id") or "overall")
        score = row.get("score")
        if not pid or score is None:
            continue
        out[(pid, dim)] = float(score)
    return out


def _pairs_from_judge_records(rows: list[dict[str, Any]]) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for rec in rows:
        pid = str(rec.get("paper_id") or rec.get("idea_id") or "")
        dims = rec.get("dimensions") or rec.get("by_dimension") or {}
        if not pid or not isinstance(dims, dict):
            continue
        for did, block in dims.items():
            if not isinstance(block, dict):
                continue
            score = block.get("score", block.get("mean"))
            if score is None:
                continue
            out[(pid, did)] = float(score)
    return out


def _pairs_from_human_papers(payload: dict[str, Any]) -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    papers = payload.get("papers") if isinstance(payload.get("papers"), dict) else payload
    if not isinstance(papers, dict):
        return out
    for pid, rec in papers.items():
        if not isinstance(rec, dict):
            continue
        dims = rec.get("by_dimension") or rec.get("dimensions") or {}
        if not isinstance(dims, dict):
            continue
        for did, block in dims.items():
            if not isinstance(block, dict):
                continue
            if block.get("covered") is False:
                continue
            score = block.get("mean", block.get("score"))
            if score is None:
                continue
            out[(str(pid), did)] = float(score)
    return out


def load_score_map(path: Path) -> dict[tuple[str, str], float]:
    payload = _load(path)
    if isinstance(payload, list):
        if payload and isinstance(payload[0], dict) and (
            "dimensions" in payload[0] or "by_dimension" in payload[0]
        ):
            return _pairs_from_judge_records(payload)
        return _pairs_from_simple(payload)
    if isinstance(payload, dict):
        return _pairs_from_human_papers(payload)
    raise SystemExit(f"unrecognised score file: {path}")


def align(
    judge: dict[tuple[str, str], float],
    human: dict[tuple[str, str], float],
) -> dict[str, Any]:
    from alphaideabench.metrics import spearman_correlation

    keys = sorted(set(judge) & set(human))
    by_dim: dict[str, Any] = {}
    dims = sorted({dim for _, dim in keys})
    for dim in dims:
        pairs = [(pid, judge[(pid, dim)], human[(pid, dim)]) for pid, d in keys if d == dim]
        js = [j for _, j, _ in pairs]
        hs = [h for _, _, h in pairs]
        diffs = [abs(j - h) for j, h in zip(js, hs)]
        n = len(pairs)
        by_dim[dim] = {
            "n": n,
            "dist_acc": round(_dist_acc(js, hs), 4) if n else None,
            "mad": round(sum(diffs) / n, 4) if n else None,
            "within_one": round(sum(d <= 1 for d in diffs) / n, 4) if n else None,
            "exact_acc": round(sum(round(j) == round(h) for j, h in zip(js, hs)) / n, 4) if n else None,
            "three_class_acc": round(
                sum(_three_class(j) == _three_class(h) for j, h in zip(js, hs)) / n, 4
            )
            if n
            else None,
            "spearman": spearman_correlation(js, hs) if n >= 2 else None,
            "judge_mean": round(sum(js) / n, 4) if n else None,
            "human_mean": round(sum(hs) / n, 4) if n else None,
        }
    return {
        "n_pairs": len(keys),
        "n_dimensions": len(dims),
        "by_dimension": by_dim,
        "rule": "pairs only where both the judge and the human mapping produced a score",
    }


def report(summary: dict[str, Any]) -> None:
    print(f"n_pairs={summary['n_pairs']}  dimensions={summary['n_dimensions']}")
    for dim, block in summary["by_dimension"].items():
        rho = block["spearman"]
        rho_s = f"{rho:+.3f}" if rho is not None else "n/a"
        print(
            f"  {dim:<32} n={block['n']:<4} "
            f"DistAcc={block['dist_acc']}  "
            f"MAD={block['mad']}  "
            f"+/-1={block['within_one']}  "
            f"exact={block['exact_acc']}  "
            f"3-class={block['three_class_acc']}  "
            f"rho={rho_s}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--judge", required=True, help="Judge score JSON or JSONL")
    parser.add_argument("--human", required=True, help="Human-mapped score JSON or JSONL")
    parser.add_argument("--out", help="Optional summary JSON path")
    args = parser.parse_args()

    judge = load_score_map(Path(args.judge))
    human = load_score_map(Path(args.human))
    summary = align(judge, human)
    report(summary)
    if args.out:
        Path(args.out).write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
