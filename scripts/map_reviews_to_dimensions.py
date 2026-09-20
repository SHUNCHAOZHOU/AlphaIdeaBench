#!/usr/bin/env python
"""Map human ICLR peer reviews onto the 12 AlphaIdeaBench dimensions.

This builds a human-anchored reference for Track 1. The agent here is not a judge:
it never evaluates a paper itself, it only reads what human reviewers already wrote
and expresses that judgement on the rubric in prompts/dimensions.yaml. Dimensions
the reviewers never touched come back as `covered: false` with a null score, which
keeps the reference honest instead of dense.

Two granularities, selected with --mode:

- ``review`` (default): one mapping call per individual review. Keeps the reviewers
  apart, so the aggregate carries inter-reviewer agreement — the ceiling any LLM judge
  can be expected to hit on this data. Paper-level scores are averaged offline.
- ``paper``: one call per paper with all of its reviews at once. The agent reconciles
  the reviewers itself, which resolves cross-cutting arguments that averaging cannot,
  at the cost of losing the spread. Cheaper by roughly the mean review count.

Both write the same record schema, so ``--mode paper`` doubles as a control condition
for the averaged ``--mode review`` numbers.

Examples:
    # inspect the rendered prompt before spending anything
    python scripts/map_reviews_to_dimensions.py --limit 1 --print-prompt

    # per-review mapping over the 200-paper subset
    python scripts/map_reviews_to_dimensions.py --mode review --concurrency 8

    # paper-level control run
    python scripts/map_reviews_to_dimensions.py --mode paper --out outputs/review_mapping/paper
"""

from __future__ import annotations

import argparse
import json
import re
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from statistics import median, pstdev
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPERS = REPO_ROOT / "examples/reviews/sample_papers.json"
DEFAULT_OUT = REPO_ROOT / "outputs/review_mapping"

SYSTEM_PROMPT = "prompts/review_mapper_system.md"
USER_PROMPT = "prompts/review_mapper_user.md"

_FORUM_ID = re.compile(r"[?&]id=([A-Za-z0-9_-]+)")


# --------------------------------------------------------------------------- data


def paper_id_of(paper: dict[str, Any], index: int) -> str:
    match = _FORUM_ID.search(paper.get("url") or "")
    if match:
        return match.group(1)
    return paper.get("_bibkey") or f"paper_{index:04d}"


def review_id_of(review: dict[str, Any], index: int) -> str:
    return str(review.get("review_id") or f"r{index}")


def review_view(review: dict[str, Any], label: str, with_rating: bool) -> dict[str, Any]:
    """Shape one review for the prompt template.

    The venue rating is withheld by default. It anchors the mapping — a rating of 2
    drags every dimension down — and it is far more useful as an independent variable
    to correlate the mapped scores against afterwards.
    """
    return {
        "label": label,
        "rating": review.get("rating") if with_rating else None,
        "confidence": review.get("confidence") if with_rating else None,
        "summary": (review.get("summary") or "").strip(),
        "strengths": (review.get("strengths") or "").strip(),
        "weaknesses": (review.get("weaknesses") or "").strip(),
        # The upstream `review` field is empty throughout this dump, but keep it in
        # case a future export fills it in.
        "body": (review.get("review") or "").strip(),
    }


@dataclass
class Task:
    key: str
    paper_id: str
    title: str
    abstract: str
    reviews: list[dict[str, Any]]
    review_ids: list[str]
    ratings: list[int | None]
    confidences: list[int | None]
    n_reviews_total: int


def build_tasks(
    papers: list[dict[str, Any]],
    mode: str,
    with_rating: bool,
    max_reviews: int | None,
) -> list[Task]:
    tasks: list[Task] = []
    for index, paper in enumerate(papers):
        pid = paper_id_of(paper, index)
        reviews = [r for r in (paper.get("reviews") or []) if _has_text(r)]
        n_total = len(reviews)
        if max_reviews is not None:
            reviews = reviews[:max_reviews]
        if not reviews:
            continue
        title = (paper.get("title") or "").strip()
        abstract = (paper.get("abstract") or "").strip()
        if mode == "review":
            for ri, review in enumerate(reviews):
                rid = review_id_of(review, ri)
                tasks.append(
                    Task(
                        key=f"{pid}::{rid}",
                        paper_id=pid,
                        title=title,
                        abstract=abstract,
                        reviews=[review_view(review, f"Review {ri + 1}", with_rating)],
                        review_ids=[rid],
                        ratings=[review.get("rating")],
                        confidences=[review.get("confidence")],
                        n_reviews_total=n_total,
                    )
                )
        else:
            tasks.append(
                Task(
                    key=f"{pid}::all",
                    paper_id=pid,
                    title=title,
                    abstract=abstract,
                    reviews=[
                        review_view(r, f"Review {i + 1}", with_rating)
                        for i, r in enumerate(reviews)
                    ],
                    review_ids=[review_id_of(r, i) for i, r in enumerate(reviews)],
                    ratings=[r.get("rating") for r in reviews],
                    confidences=[r.get("confidence") for r in reviews],
                    n_reviews_total=n_total,
                )
            )
    return tasks


def _has_text(review: dict[str, Any]) -> bool:
    return any(
        (review.get(field) or "").strip()
        for field in ("summary", "strengths", "weaknesses", "review")
    )


# ---------------------------------------------------------------------- mapping


def normalize_dimensions(
    payload: dict[str, Any], dimension_ids: list[str]
) -> tuple[dict[str, Any], list[str]]:
    """Coerce the model's `dimensions` list into one entry per known dimension."""
    flags: list[str] = []
    raw = payload.get("dimensions")
    if not isinstance(raw, list):
        return {}, ["no_dimensions"]

    by_id: dict[str, dict[str, Any]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        did = str(item.get("dimension_id") or "").strip()
        if did not in dimension_ids:
            if did:
                flags.append(f"unknown_dimension:{did}")
            continue
        by_id[did] = item

    out: dict[str, Any] = {}
    for did in dimension_ids:
        item = by_id.get(did)
        if item is None:
            flags.append(f"missing_dimension:{did}")
            out[did] = {
                "covered": False,
                "score": None,
                "evidence": [],
                "reviewer_stance": "",
                "reasoning": "",
                "confidence": None,
            }
            continue
        score, covered, dim_flags = _score_of(item, did)
        flags.extend(dim_flags)
        out[did] = {
            "covered": covered,
            "score": score,
            "evidence": _evidence_of(item.get("evidence")),
            "reviewer_stance": str(item.get("reviewer_stance") or "").strip(),
            "reasoning": str(item.get("reasoning") or "").strip(),
            "confidence": _float_or_none(item.get("confidence")),
        }
    return out, flags


def _score_of(item: dict[str, Any], did: str) -> tuple[int | None, bool, list[str]]:
    flags: list[str] = []
    covered = item.get("covered")
    covered = bool(covered) if covered is not None else None
    raw = item.get("score")

    if raw is None or raw == "":
        if covered:
            flags.append(f"covered_without_score:{did}")
        return None, False, flags

    try:
        numeric = float(raw)
    except (TypeError, ValueError):
        flags.append(f"score_invalid:{did}")
        return None, False, flags

    score = int(round(numeric))
    if score != numeric:
        flags.append(f"score_rounded:{did}")
    if not 1 <= score <= 5:
        flags.append(f"score_out_of_range:{did}")
        score = min(5, max(1, score))
    if covered is False:
        flags.append(f"scored_while_uncovered:{did}")
    return score, True, flags


def _evidence_of(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value)]


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def run_task(
    task: Task,
    *,
    backend: Any,
    dimensions: list[Any],
    dimension_ids: list[str],
    mode: str,
    model: str | None,
    temperature: float,
    json_mode: bool,
) -> dict[str, Any]:
    from alphaideabench.core.agent import Agent
    from alphaideabench.core.prompt import render_file

    system = render_file(SYSTEM_PROMPT, dimensions=dimensions)
    user = render_file(
        USER_PROMPT,
        paper_id=task.paper_id,
        title=task.title,
        abstract=task.abstract,
        reviews=task.reviews,
    )
    agent = Agent(
        name=f"review_mapper:{task.key}",
        backend=backend,
        system_prompt=system,
        tools=None,
        temperature=temperature,
        max_rounds=3,
        require_json=True,
        json_mode=json_mode,
        model=model,
    )
    result = agent.run(user)
    payload = result.parsed or {}
    mapped, flags = normalize_dimensions(payload, dimension_ids)
    return {
        "key": task.key,
        "paper_id": task.paper_id,
        "title": task.title,
        "mode": mode,
        "model": model,
        "review_ids": task.review_ids,
        "n_reviews_in_call": len(task.reviews),
        "n_reviews_total": task.n_reviews_total,
        "venue_ratings": task.ratings,
        "venue_confidences": task.confidences,
        "dimensions": mapped,
        "disagreement": str(payload.get("disagreement") or "").strip(),
        "overall_notes": str(payload.get("overall_notes") or "").strip(),
        "flags": flags,
        "usage": result.usage,
    }


# -------------------------------------------------------------------- aggregate


def _stats(scores: list[int]) -> dict[str, Any]:
    if not scores:
        return {"n": 0, "mean": None, "median": None, "std": None}
    return {
        "n": len(scores),
        "mean": sum(scores) / len(scores),
        "median": float(median(scores)),
        "std": float(pstdev(scores)) if len(scores) > 1 else 0.0,
    }


def _agreement(scores: list[int]) -> dict[str, Any]:
    pairs = [(a, b) for i, a in enumerate(scores) for b in scores[i + 1 :]]
    if not pairs:
        return {"n_pairs": 0, "exact_agreement": None, "mean_abs_diff": None}
    return {
        "n_pairs": len(pairs),
        "exact_agreement": sum(a == b for a, b in pairs) / len(pairs),
        "mean_abs_diff": sum(abs(a - b) for a, b in pairs) / len(pairs),
    }


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def aggregate(
    records: list[dict[str, Any]],
    catalog: Any,
    dimension_ids: list[str] | None = None,
) -> tuple[dict, dict]:
    # When the run was restricted to a subset of dimensions (e.g. --group novelty),
    # report only those. Falling back to the full catalog would pad the summary with
    # 9 dimensions at coverage 0.00 that were never asked about.
    if dimension_ids is None:
        dimension_ids = [d.id for d in catalog.ordered()]

    by_paper: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_paper.setdefault(record["paper_id"], []).append(record)

    papers: dict[str, Any] = {}
    for pid, recs in by_paper.items():
        ratings = [r for rec in recs for r in (rec.get("venue_ratings") or []) if r is not None]
        # In paper mode every record already lists all ratings; in review mode each record
        # lists its own. Dedupe so the mean is per reviewer either way.
        if recs[0].get("mode") == "paper":
            ratings = [r for r in (recs[0].get("venue_ratings") or []) if r is not None]
        confidences = [
            c for rec in recs for c in (rec.get("venue_confidences") or []) if c is not None
        ]
        if recs[0].get("mode") == "paper":
            confidences = [c for c in (recs[0].get("venue_confidences") or []) if c is not None]

        dims: dict[str, Any] = {}
        for did in dimension_ids:
            entries = [rec["dimensions"].get(did) or {} for rec in recs]
            scores = [e["score"] for e in entries if e.get("score") is not None]
            dims[did] = {
                **_stats(scores),
                "n_records": len(entries),
                "n_covered": len(scores),
                "coverage": len(scores) / len(entries) if entries else 0.0,
                "scores": scores,
                **_agreement(scores),
            }

        # Skip groups with no mapped dimension in this run, so a novelty-only run
        # does not emit four null group means.
        group_means: dict[str, float | None] = {}
        for gid, group in catalog.groups.items():
            if not any(d in dims for d in group.dimensions):
                continue
            vals = [dims[d]["mean"] for d in group.dimensions if dims.get(d, {}).get("mean") is not None]
            group_means[gid] = _mean(vals)

        papers[pid] = {
            "title": recs[0].get("title", ""),
            "n_records": len(recs),
            "n_reviews_total": recs[0].get("n_reviews_total"),
            "venue_rating_mean": _mean([float(r) for r in ratings]),
            "venue_confidence_mean": _mean([float(c) for c in confidences]),
            "by_dimension": dims,
            "group_means": group_means,
        }

    summary = _summarize(records, papers, catalog, dimension_ids)
    return papers, summary


def _summarize(
    records: list[dict[str, Any]],
    papers: dict[str, Any],
    catalog: Any,
    dimension_ids: list[str],
) -> dict[str, Any]:
    from alphaideabench.metrics import spearman_correlation

    mode = records[0].get("mode") if records else None
    dim_summary: dict[str, Any] = {}

    for did in dimension_ids:
        entries = [rec["dimensions"].get(did) or {} for rec in records]
        scores = [e["score"] for e in entries if e.get("score") is not None]
        confs = [e["confidence"] for e in entries if e.get("confidence") is not None]

        # Reviewer agreement only exists when reviewers were mapped separately.
        agree_exact: list[float] = []
        agree_mad: list[float] = []
        for paper in papers.values():
            stat = paper["by_dimension"].get(did) or {}
            if stat.get("exact_agreement") is not None:
                agree_exact.append(stat["exact_agreement"])
                agree_mad.append(stat["mean_abs_diff"])

        xs: list[float] = []
        ys: list[float] = []
        for paper in papers.values():
            mean_score = (paper["by_dimension"].get(did) or {}).get("mean")
            rating = paper.get("venue_rating_mean")
            if mean_score is not None and rating is not None:
                xs.append(mean_score)
                ys.append(rating)

        dim_summary[did] = {
            "name": catalog.dimensions[did].name,
            "group": catalog.dimensions[did].group,
            "n_records": len(entries),
            "n_scored": len(scores),
            "coverage": len(scores) / len(entries) if entries else 0.0,
            "mean": _mean([float(s) for s in scores]),
            "std": float(pstdev(scores)) if len(scores) > 1 else 0.0,
            "distribution": {str(k): v for k, v in sorted(Counter(scores).items())},
            "mean_mapper_confidence": _mean(confs),
            "n_papers_with_score": len(xs),
            "spearman_with_venue_rating": (
                spearman_correlation(xs, ys) if len(xs) >= 2 else None
            ),
            "reviewer_exact_agreement": _mean(agree_exact) if mode == "review" else None,
            "reviewer_mean_abs_diff": _mean(agree_mad) if mode == "review" else None,
        }

    groups: dict[str, Any] = {}
    for gid, group in catalog.groups.items():
        vals = [
            paper["group_means"][gid]
            for paper in papers.values()
            if paper["group_means"].get(gid) is not None
        ]
        ratings = [
            paper["venue_rating_mean"]
            for paper in papers.values()
            if paper["group_means"].get(gid) is not None
            and paper.get("venue_rating_mean") is not None
        ]
        groups[gid] = {
            "name": group.name,
            "n_papers": len(vals),
            "mean": _mean(vals),
            "spearman_with_venue_rating": (
                spearman_correlation(vals, ratings)
                if len(vals) >= 2 and len(vals) == len(ratings)
                else None
            ),
        }

    flag_counter: Counter[str] = Counter()
    for rec in records:
        flag_counter.update(f.split(":")[0] for f in (rec.get("flags") or []))

    usage = Counter()
    for rec in records:
        for key, value in (rec.get("usage") or {}).items():
            usage[key] += int(value or 0)

    return {
        "mode": mode,
        "model": records[0].get("model") if records else None,
        "n_records": len(records),
        "n_papers": len(papers),
        "dimensions": dim_summary,
        "groups": groups,
        "flags": dict(flag_counter),
        "token_usage": dict(usage),
    }


# ------------------------------------------------------------------------- main


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--papers", default=str(DEFAULT_PAPERS), help="论文 JSON（默认 200 篇子集）")
    parser.add_argument(
        "--mode",
        choices=["review", "paper"],
        default="review",
        help="review=每份 review 单独映射（默认）；paper=一篇论文的所有 review 一次映射",
    )
    parser.add_argument("--out", help="输出目录，默认 outputs/review_mapping/<mode>")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--model", help="OpenRouter slug，默认取 judge 或 llm 的模型")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--limit", type=int, help="只处理前 N 篇论文")
    parser.add_argument("--paper-id", action="append", default=[], help="只处理指定论文（可重复）")
    parser.add_argument("--max-reviews", type=int, help="每篇论文最多用几份 review")
    parser.add_argument(
        "--with-rating",
        action="store_true",
        help="把 reviewer 的 rating/confidence 也给 agent 看（默认不给，避免锚定）",
    )
    parser.add_argument(
        "--group",
        action="append",
        default=[],
        help="只映射指定维度组（可重复），如 --group novelty。默认全部 12 个维度",
    )
    parser.add_argument("--overwrite", action="store_true", help="忽略已有结果，重跑全部")
    parser.add_argument("--print-prompt", action="store_true", help="打印第一个任务的 prompt 后退出")
    parser.add_argument("--dry-run", action="store_true", help="用 MockBackend 走通流程，不调 API")
    parser.add_argument("--aggregate-only", action="store_true", help="只根据已有 records.jsonl 重算聚合")
    args = parser.parse_args()

    from alphaideabench.config import Settings
    from alphaideabench.core.llm import build_backend
    from alphaideabench.core.prompt import render_file
    from alphaideabench.domain.dimensions import load_catalog

    settings = Settings.load(args.config)
    catalog = load_catalog()
    dimensions = catalog.ordered()
    if args.group:
        wanted_groups = {g.strip().lower() for g in args.group}
        dimensions = [d for d in dimensions if (getattr(d, "group", "") or "").lower() in wanted_groups]
        if not dimensions:
            available = sorted({getattr(d, "group", "") or "?" for d in catalog.ordered()})
            raise SystemExit(f"no dimension in group(s) {sorted(wanted_groups)}; available: {available}")
    dimension_ids = [d.id for d in dimensions]
    print(f"[map] {len(dimension_ids)} dimension(s): {', '.join(dimension_ids)}", flush=True)

    out_dir = Path(args.out) if args.out else DEFAULT_OUT / args.mode
    out_dir.mkdir(parents=True, exist_ok=True)
    records_path = out_dir / "records.jsonl"
    errors_path = out_dir / "errors.jsonl"

    if args.aggregate_only:
        records = read_jsonl(records_path)
        if not records:
            raise SystemExit(f"no records in {records_path}")
        papers, summary = aggregate(records, catalog, dimension_ids)
        write_json(out_dir / "papers.json", papers)
        write_json(out_dir / "summary.json", summary)
        print(f"[map] aggregated {len(records)} record(s) over {len(papers)} paper(s)")
        return 0

    raw = json.loads(Path(args.papers).read_text(encoding="utf-8"))
    if args.paper_id:
        wanted = set(args.paper_id)
        raw = [p for i, p in enumerate(raw) if paper_id_of(p, i) in wanted]
    if args.limit:
        raw = raw[: args.limit]

    tasks = build_tasks(raw, args.mode, args.with_rating, args.max_reviews)
    if not tasks:
        raise SystemExit("no reviews to map")

    if args.print_prompt:
        task = tasks[0]
        print(render_file(SYSTEM_PROMPT, dimensions=dimensions))
        print("\n" + "=" * 78 + " USER\n")
        print(
            render_file(
                USER_PROMPT,
                paper_id=task.paper_id,
                title=task.title,
                abstract=task.abstract,
                reviews=task.reviews,
            )
        )
        return 0

    if args.overwrite:
        records_path.unlink(missing_ok=True)
        errors_path.unlink(missing_ok=True)
    done = {rec["key"] for rec in read_jsonl(records_path)}
    pending = [t for t in tasks if t.key not in done]

    model = args.model or settings.agents.judge.model or settings.llm.model
    backend = build_backend(settings, dry_run=args.dry_run)
    print(
        f"[map] mode={args.mode} model={model} papers={len({t.paper_id for t in tasks})} "
        f"tasks={len(tasks)} pending={len(pending)} out={out_dir}"
    )

    lock = threading.Lock()
    counters = {"ok": 0, "fail": 0}

    def worker(task: Task) -> None:
        try:
            record = run_task(
                task,
                backend=backend,
                dimensions=dimensions,
                dimension_ids=dimension_ids,
                mode=args.mode,
                model=model,
                temperature=args.temperature,
                json_mode=settings.llm.json_mode,
            )
        except Exception as exc:  # noqa: BLE001 — one bad task must not sink the run
            with lock:
                counters["fail"] += 1
                with errors_path.open("a", encoding="utf-8") as f:
                    f.write(
                        json.dumps(
                            {"key": task.key, "error": f"{type(exc).__name__}: {exc}"},
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                print(f"[map] FAIL {task.key}: {type(exc).__name__}: {exc}", flush=True)
            return
        with lock:
            counters["ok"] += 1
            with records_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
            n_covered = sum(1 for d in record["dimensions"].values() if d["score"] is not None)
            print(
                f"[map] {counters['ok'] + counters['fail']}/{len(pending)} {task.key} "
                f"covered={n_covered}/{len(dimension_ids)}",
                flush=True,
            )

    if pending:
        with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
            futures = [pool.submit(worker, t) for t in pending]
            for future in as_completed(futures):
                future.result()

    records = read_jsonl(records_path)
    if not records:
        print("[map] nothing mapped")
        return 1
    papers, summary = aggregate(records, catalog, dimension_ids)
    write_json(out_dir / "papers.json", papers)
    write_json(out_dir / "summary.json", summary)

    print(f"\n[map] ok={counters['ok']} fail={counters['fail']} records={len(records)}")
    print(f"[map] wrote {records_path.name}, papers.json, summary.json in {out_dir}")
    print("\n[map] coverage by dimension:")
    for did, stat in summary["dimensions"].items():
        mean = stat["mean"]
        print(
            f"  {did:34s} coverage={stat['coverage']:.2f} "
            f"mean={'  n/a' if mean is None else f'{mean:.2f}'} "
            f"n={stat['n_scored']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
