#!/usr/bin/env python
"""Build review-derived reference scores for the four novelty dimensions.

Two LLM stages, run in order, over ICLR papers that already carry human reviews:

    paper + all its reviews
        -> [1 extract]  novelty remarks, quoted and attributed per reviewer
        -> [2 score]    a 1-5 score per novelty facet, on the AlphaIdeaBench rubric

Splitting the work in two is what makes the output auditable. Stage 2 is given only
stage 1's remarks -- never the paper, never the reviews -- so it cannot quietly review
the paper itself and pass its own opinion off as the reviewers'. Anything stage 2 cites
has to appear in stage 1's output, which is on disk and checkable.

The result is a *review-derived reference*, not ground truth. It inherits whatever the
reviewers got wrong, plus two LLM passes.

Reviewer attribution
--------------------
Stage 1 tags every quote with the reviewer it came from and is told not to deduplicate
across reviewers. This is the one thing NovBench's pipeline discards: it pools every
reviewer's sentences into a flat list and then asks an LLM to "deduplicate and
consolidate" them into one label per paper, after which reviewer boundaries are gone.
Keeping them costs nothing here and is what makes the human-human ceiling computable --
without it there is no way to ask how much two reviewers of the same paper disagree,
and so no way to know what agreement an LLM judge could even aspire to.

`--mode` controls the unit of work:

- ``paper`` (default): one extract + one score call per paper, all reviewers together.
  Yields the reference score. Reviewer attribution is preserved inside the remarks.
- ``reviewer``: each reviewer handled independently end to end. Costs ~4x more and is
  only needed for the ceiling, where reviewers must never see each other.

Examples:
    # see the stage-1 prompt without spending anything
    python scripts/novelty_reference.py --limit 1 --print-prompt extract

    # walk both stages on the mock backend
    python scripts/novelty_reference.py --limit 2 --dry-run

    # the real run
    python scripts/novelty_reference.py --concurrency 6

    # per-reviewer pass, for the human-human ceiling
    python scripts/novelty_reference.py --mode reviewer --out outputs/novelty_reference/by_reviewer

    # recompute aggregates from records already on disk
    python scripts/novelty_reference.py --aggregate-only
"""

from __future__ import annotations

import argparse
import json
import re
import statistics as st
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPERS = REPO_ROOT / "examples/reviews/sample_papers.json"
DEFAULT_OUT = REPO_ROOT / "outputs/novelty_reference"

EXTRACT_SYSTEM = "prompts/novelty_extract_system.md"
EXTRACT_USER = "prompts/novelty_extract_user.md"
SCORE_SYSTEM = "prompts/novelty_score_system.md"
SCORE_USER = "prompts/novelty_score_user.md"

NOVELTY_GROUP = "novelty"
STANCES = ("positive", "negative", "mixed", "neutral")

_FORUM_ID = re.compile(r"[?&]id=([A-Za-z0-9_-]+)")

#: ICLR 2026 ratings are 2/4/6/8/10 in this dump; a 0 marks a missing score rather
#: than a real one, so it must not enter any mean. See scripts/sample_iclr_subset.py.
VALID_RATINGS = (2, 4, 6, 8, 10)


# ----------------------------------------------------------------------- data


def paper_id_of(paper: dict[str, Any], index: int) -> str:
    match = _FORUM_ID.search(paper.get("url") or "")
    if match:
        return match.group(1)
    return paper.get("_bibkey") or f"paper_{index:04d}"


def has_text(review: dict[str, Any]) -> bool:
    fields = ("summary", "strengths", "weaknesses", "review")
    return any((review.get(f) or "").strip() for f in fields)


def review_view(review: dict[str, Any], label: str, with_rating: bool) -> dict[str, Any]:
    """Shape one review for the stage-1 template.

    The venue rating is withheld by default. Showing it anchors the extraction -- a
    rating of 2 colours every remark negative -- and it is far more valuable kept back
    as an independent variable to correlate the finished scores against.
    """
    return {
        "label": label,
        "rating": review.get("rating") if with_rating else None,
        "confidence": review.get("confidence") if with_rating else None,
        "summary": (review.get("summary") or "").strip(),
        "strengths": (review.get("strengths") or "").strip(),
        "weaknesses": (review.get("weaknesses") or "").strip(),
        # Empty for all 50,977 reviews in the current dump, kept for future exports.
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
    reviewer_label: str | None = None


def build_tasks(
    papers: list[dict[str, Any]],
    mode: str,
    with_rating: bool,
    max_reviews: int | None,
) -> list[Task]:
    tasks: list[Task] = []
    for index, paper in enumerate(papers):
        pid = paper_id_of(paper, index)
        reviews = [r for r in (paper.get("reviews") or []) if has_text(r)]
        n_total = len(reviews)
        if max_reviews is not None:
            reviews = reviews[:max_reviews]
        if not reviews:
            continue

        title = (paper.get("title") or "").strip()
        abstract = (paper.get("abstract") or "").strip()
        labels = [f"Review {i + 1}" for i in range(len(reviews))]

        if mode == "reviewer":
            for i, review in enumerate(reviews):
                rid = str(review.get("review_id") or f"r{i}")
                tasks.append(
                    Task(
                        key=f"{pid}::{rid}",
                        paper_id=pid,
                        title=title,
                        abstract=abstract,
                        reviews=[review_view(review, labels[i], with_rating)],
                        review_ids=[rid],
                        ratings=[review.get("rating")],
                        confidences=[review.get("confidence")],
                        n_reviews_total=n_total,
                        reviewer_label=labels[i],
                    )
                )
        else:
            tasks.append(
                Task(
                    key=pid,
                    paper_id=pid,
                    title=title,
                    abstract=abstract,
                    reviews=[review_view(r, labels[i], with_rating) for i, r in enumerate(reviews)],
                    review_ids=[str(r.get("review_id") or f"r{i}") for i, r in enumerate(reviews)],
                    ratings=[r.get("rating") for r in reviews],
                    confidences=[r.get("confidence") for r in reviews],
                    n_reviews_total=n_total,
                )
            )
    return tasks


# ------------------------------------------------------------- normalisation


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _clip_confidence(value: Any) -> float:
    try:
        num = float(value)
    except (TypeError, ValueError):
        return 0.0
    return min(1.0, max(0.0, num))


def normalise_facets(
    payload: dict[str, Any],
    dimension_ids: list[str],
    valid_labels: set[str],
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    """Validate stage-1 output into one remark list per dimension.

    Flags are recorded rather than raised: a run of several hundred papers should not
    die because one response invented a reviewer label. Each flag names a specific
    defect so a bad batch can be found later instead of silently averaging in.
    """
    flags: list[str] = []
    facets: dict[str, list[dict[str, Any]]] = {did: [] for did in dimension_ids}

    raw = payload.get("facets")
    if not isinstance(raw, list):
        return facets, ["facets_missing"]

    seen: set[str] = set()
    for entry in raw:
        if not isinstance(entry, dict):
            flags.append("facet_not_object")
            continue
        did = _text(entry.get("dimension_id"))
        if did not in facets:
            flags.append(f"unknown_dimension:{did or '?'}")
            continue
        if did in seen:
            flags.append(f"duplicate_dimension:{did}")
            continue
        seen.add(did)

        for item in entry.get("remarks") or []:
            if not isinstance(item, dict):
                flags.append(f"remark_not_object:{did}")
                continue
            quote = _text(item.get("quote"))
            if not quote:
                # A remark with no quote cannot be checked against the review, and
                # stage 2 is told to cite only what it was given. Drop it.
                flags.append(f"remark_without_quote:{did}")
                continue

            reviewer = _text(item.get("reviewer"))
            if reviewer not in valid_labels:
                # Keep the remark: the quote is still real and traceable. Only the
                # attribution is unusable, and that is what the flag records.
                flags.append(f"unknown_reviewer:{reviewer or '?'}")
                reviewer = reviewer or "unknown"

            stance = _text(item.get("stance")).lower()
            if stance not in STANCES:
                flags.append(f"bad_stance:{stance or '?'}")
                stance = "neutral"

            facets[did].append(
                {
                    "reviewer": reviewer,
                    "quote": quote,
                    "stance": stance,
                    "note": _text(item.get("note")),
                }
            )

    missing = [d for d in dimension_ids if d not in seen]
    if missing:
        flags.append("facets_absent:" + ",".join(missing))
    return facets, flags


def normalise_scores(
    payload: dict[str, Any],
    dimension_ids: list[str],
    allowed_quotes: set[str],
) -> tuple[dict[str, Any], list[str]]:
    """Validate stage-2 output into one scored entry per dimension."""
    flags: list[str] = []
    scored: dict[str, Any] = {}

    raw = payload.get("dimensions")
    by_id: dict[str, dict[str, Any]] = {}
    if isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, dict):
                did = _text(entry.get("dimension_id"))
                if did in dimension_ids and did not in by_id:
                    by_id[did] = entry
    else:
        flags.append("dimensions_missing")

    for did in dimension_ids:
        entry = by_id.get(did)
        if entry is None:
            flags.append(f"dimension_absent:{did}")
            scored[did] = {
                "covered": False,
                "score": None,
                "evidence": [],
                "reviewer_stance": "neutral",
                "reasoning": "",
                "confidence": 0.0,
            }
            continue

        covered = bool(entry.get("covered"))
        score: int | None = None
        rawscore = entry.get("score")
        if rawscore not in (None, ""):
            try:
                score = int(round(float(rawscore)))
            except (TypeError, ValueError):
                flags.append(f"score_unparsable:{did}")
            else:
                if not 1 <= score <= 5:
                    flags.append(f"score_out_of_range:{did}:{score}")
                    score = min(5, max(1, score))

        # covered/score must agree, or the aggregate silently mixes real scores with
        # placeholders. Trust whichever field carries information.
        if covered and score is None:
            flags.append(f"covered_without_score:{did}")
            covered = False
        elif not covered and score is not None:
            flags.append(f"score_without_covered:{did}")
            covered = True

        evidence: list[str] = []
        for quote in entry.get("evidence") or []:
            text = _text(quote)
            if not text:
                continue
            # Stage 2 never sees the reviews, so any quote it produces that was not in
            # its input is fabricated. Flag it and keep it visible for inspection.
            if allowed_quotes and not _quote_seen(text, allowed_quotes):
                flags.append(f"evidence_not_in_input:{did}")
            evidence.append(text)

        if covered and not evidence:
            flags.append(f"covered_without_evidence:{did}")

        stance = _text(entry.get("reviewer_stance")).lower()
        if stance not in STANCES:
            if stance:
                flags.append(f"bad_stance:{did}:{stance}")
            stance = "neutral"

        scored[did] = {
            "covered": covered,
            "score": score if covered else None,
            "evidence": evidence,
            "reviewer_stance": stance,
            "reasoning": _text(entry.get("reasoning")),
            "confidence": _clip_confidence(entry.get("confidence")),
        }
    return scored, flags


def _normalise_quote(text: str) -> str:
    """Collapse whitespace and quote marks so cosmetic edits do not read as fabrication."""
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def _quote_seen(quote: str, allowed: set[str]) -> bool:
    """True when the quote appears in stage 1's output.

    Substring either way: stage 2 legitimately trims a long quote to the relevant
    clause, and occasionally pads one with a few surrounding words.
    """
    needle = _normalise_quote(quote)
    if not needle:
        return True
    return any(needle in hay or hay in needle for hay in allowed)


# ------------------------------------------------------------------- stages


def run_extract(
    task: Task,
    *,
    backend: Any,
    dimensions: list[Any],
    dimension_ids: list[str],
    model: str | None,
    temperature: float,
    json_mode: bool,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any], list[str]]:
    from alphaideabench.core.agent import Agent
    from alphaideabench.core.prompt import render_file

    system = render_file(EXTRACT_SYSTEM, dimensions=dimensions)
    user = render_file(
        EXTRACT_USER,
        paper_id=task.paper_id,
        title=task.title,
        abstract=task.abstract,
        reviews=task.reviews,
    )
    agent = Agent(
        name=f"novelty_extract:{task.key}",
        backend=backend,
        system_prompt=system,
        tools=None,
        temperature=temperature,
        max_rounds=3,
        require_json=True,
        json_mode=json_mode,
        model=model,
    )
    payload = agent.run(user).parsed or {}
    labels = {r["label"] for r in task.reviews}
    facets, flags = normalise_facets(payload, dimension_ids, labels)
    meta = {
        "disagreement": _text(payload.get("disagreement")),
        "overall_notes": _text(payload.get("overall_notes")),
    }
    return facets, meta, flags


def run_score(
    task: Task,
    facets: dict[str, list[dict[str, Any]]],
    meta: dict[str, Any],
    *,
    backend: Any,
    dimensions: list[Any],
    dimension_ids: list[str],
    model: str | None,
    temperature: float,
    json_mode: bool,
) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    from alphaideabench.core.agent import Agent
    from alphaideabench.core.prompt import render_file

    system = render_file(SCORE_SYSTEM, dimensions=dimensions)
    user = render_file(
        SCORE_USER,
        paper_id=task.paper_id,
        n_reviewers=len(task.reviews),
        facets=[{"dimension_id": d, "remarks": facets[d]} for d in dimension_ids],
        disagreement=meta.get("disagreement", ""),
        overall_notes=meta.get("overall_notes", ""),
    )
    agent = Agent(
        name=f"novelty_score:{task.key}",
        backend=backend,
        system_prompt=system,
        tools=None,
        temperature=temperature,
        max_rounds=3,
        require_json=True,
        json_mode=json_mode,
        model=model,
    )
    payload = agent.run(user).parsed or {}
    allowed = {_normalise_quote(r["quote"]) for rs in facets.values() for r in rs}
    scored, flags = normalise_scores(payload, dimension_ids, allowed)

    # A facet that arrived with remarks but came back uncovered means stage 2 threw
    # away evidence stage 1 found; the reverse means it scored from nothing. Both
    # break the audit trail between the stages, so both are recorded.
    for did in dimension_ids:
        if facets[did] and not scored[did]["covered"]:
            flags.append(f"remarks_ignored:{did}")
        if not facets[did] and scored[did]["covered"]:
            flags.append(f"scored_without_remarks:{did}")

    score_meta = {
        "disagreement": _text(payload.get("disagreement")) or meta.get("disagreement", ""),
        "overall_notes": _text(payload.get("overall_notes")),
    }
    return scored, score_meta, flags


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
    facets, extract_meta, extract_flags = run_extract(
        task,
        backend=backend,
        dimensions=dimensions,
        dimension_ids=dimension_ids,
        model=model,
        temperature=temperature,
        json_mode=json_mode,
    )
    scored, score_meta, score_flags = run_score(
        task,
        facets,
        extract_meta,
        backend=backend,
        dimensions=dimensions,
        dimension_ids=dimension_ids,
        model=model,
        temperature=temperature,
        json_mode=json_mode,
    )
    return {
        "key": task.key,
        "paper_id": task.paper_id,
        "title": task.title,
        "mode": mode,
        "model": model,
        "reviewer_label": task.reviewer_label,
        "review_ids": task.review_ids,
        "n_reviews_in_call": len(task.reviews),
        "n_reviews_total": task.n_reviews_total,
        "venue_ratings": task.ratings,
        "venue_confidences": task.confidences,
        # Stage 1's output is kept in full: it is the evidence stage 2's scores rest on,
        # and the only way to check them after the fact.
        "extracted": {did: facets[did] for did in dimension_ids},
        "n_remarks": {did: len(facets[did]) for did in dimension_ids},
        "dimensions": scored,
        "disagreement": score_meta["disagreement"],
        "extract_notes": extract_meta.get("overall_notes", ""),
        "score_notes": score_meta["overall_notes"],
        "flags": extract_flags + score_flags,
    }


# --------------------------------------------------------------- aggregation


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def _spread(scores: list[float]) -> dict[str, Any]:
    if not scores:
        return {"mean": None, "sd": None, "min": None, "max": None, "n": 0}
    return {
        "mean": round(st.mean(scores), 4),
        "sd": round(st.stdev(scores), 4) if len(scores) > 1 else 0.0,
        "min": min(scores),
        "max": max(scores),
        "n": len(scores),
    }


def _agreement(scores: list[float]) -> dict[str, Any]:
    """How far apart independent scorers of the same paper landed.

    Only defined with two or more scores, i.e. in ``--mode reviewer``. In paper mode
    the reviewers were reconciled inside a single call, so there is nothing to compare.
    """
    if len(scores) < 2:
        return {"exact_agreement": None, "mean_abs_diff": None, "within_one": None}
    pairs = [
        (scores[i], scores[j]) for i in range(len(scores)) for j in range(i + 1, len(scores))
    ]
    diffs = [abs(a - b) for a, b in pairs]
    return {
        "exact_agreement": round(sum(1 for d in diffs if d == 0) / len(diffs), 4),
        "within_one": round(sum(1 for d in diffs if d <= 1) / len(diffs), 4),
        "mean_abs_diff": round(sum(diffs) / len(diffs), 4),
    }


def aggregate(
    records: list[dict[str, Any]], dimension_ids: list[str]
) -> tuple[dict[str, Any], dict[str, Any]]:
    by_paper: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_paper.setdefault(record["paper_id"], []).append(record)

    papers: dict[str, Any] = {}
    for pid, recs in by_paper.items():
        mode = recs[0].get("mode")
        if mode == "paper":
            ratings = [r for r in (recs[0].get("venue_ratings") or []) if r in VALID_RATINGS]
            confs = [c for c in (recs[0].get("venue_confidences") or []) if c is not None]
        else:
            ratings = [
                r for rec in recs for r in (rec.get("venue_ratings") or []) if r in VALID_RATINGS
            ]
            confs = [
                c for rec in recs for c in (rec.get("venue_confidences") or []) if c is not None
            ]

        dims: dict[str, Any] = {}
        for did in dimension_ids:
            entries = [rec["dimensions"].get(did) or {} for rec in recs]
            scores = [float(e["score"]) for e in entries if e.get("score") is not None]
            dims[did] = {
                **_spread(scores),
                "n_records": len(entries),
                "coverage": round(len(scores) / len(entries), 4) if entries else 0.0,
                "scores": scores,
                "n_remarks": sum((rec.get("n_remarks") or {}).get(did, 0) for rec in recs),
                **_agreement(scores),
            }

        covered = [dims[d]["mean"] for d in dimension_ids if dims[d]["mean"] is not None]
        papers[pid] = {
            "title": recs[0].get("title", ""),
            "n_records": len(recs),
            "n_reviews_total": recs[0].get("n_reviews_total"),
            "venue_rating_mean": _mean([float(r) for r in ratings]),
            "venue_confidence_mean": _mean([float(c) for c in confs]),
            "by_dimension": dims,
            # Mean over the facets the reviewers actually addressed. Treating an
            # unaddressed facet as 3 would invent a judgement nobody made.
            "novelty_mean": _mean(covered),
            "n_dimensions_covered": len(covered),
        }

    return papers, _summarise(records, papers, dimension_ids)


def _summarise(
    records: list[dict[str, Any]],
    papers: dict[str, Any],
    dimension_ids: list[str],
) -> dict[str, Any]:
    from alphaideabench.metrics import spearman_correlation

    per_dim: dict[str, Any] = {}
    for did in dimension_ids:
        entries = [rec["dimensions"].get(did) or {} for rec in records]
        scores = [float(e["score"]) for e in entries if e.get("score") is not None]
        confs = [e["confidence"] for e in entries if e.get("confidence") is not None]

        exact: list[float] = []
        mad: list[float] = []
        within: list[float] = []
        for paper in papers.values():
            stat = paper["by_dimension"].get(did) or {}
            if stat.get("exact_agreement") is not None:
                exact.append(stat["exact_agreement"])
                mad.append(stat["mean_abs_diff"])
                within.append(stat["within_one"])

        # Reference score against the venue's own rating. A judge that tracks novelty
        # should show some positive relation here, but not a strong one -- rating folds
        # in soundness and clarity too, so a high rho would mean the pipeline is
        # picking up overall verdict rather than novelty specifically.
        paired = [
            (p["by_dimension"][did]["mean"], p["venue_rating_mean"])
            for p in papers.values()
            if p["by_dimension"][did]["mean"] is not None and p["venue_rating_mean"] is not None
        ]
        rho = spearman_correlation([a for a, _ in paired], [b for _, b in paired]) if len(paired) > 2 else None

        per_dim[did] = {
            "n_records": len(entries),
            "n_scored": len(scores),
            "coverage": round(len(scores) / len(entries), 4) if entries else 0.0,
            "distribution": {s: scores.count(s) for s in sorted(set(scores))},
            **_spread(scores),
            "mean_confidence": _mean(confs),
            "mean_remarks_per_record": _mean(
                [float((rec.get("n_remarks") or {}).get(did, 0)) for rec in records]
            ),
            "reviewer_agreement": {
                "n_papers": len(exact),
                "exact": _mean(exact),
                "within_one": _mean(within),
                "mean_abs_diff": _mean(mad),
            },
            "rho_vs_venue_rating": {"rho": rho, "n": len(paired)},
        }

    flags: dict[str, int] = {}
    for record in records:
        for flag in record.get("flags") or []:
            flags[flag.split(":")[0]] = flags.get(flag.split(":")[0], 0) + 1

    n_any = sum(
        1
        for rec in records
        if any((rec["dimensions"].get(d) or {}).get("covered") for d in dimension_ids)
    )
    return {
        "mode": records[0].get("mode") if records else None,
        "n_records": len(records),
        "n_papers": len(papers),
        "records_with_any_coverage": n_any,
        "by_dimension": per_dim,
        "flag_counts": flags,
    }


# ---------------------------------------------------------------------- io/cli


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--papers", default=str(DEFAULT_PAPERS), help="论文 JSON（默认 200 篇子集）")
    parser.add_argument(
        "--mode",
        choices=["paper", "reviewer"],
        default="paper",
        help="paper=一篇论文的所有 review 一起处理（默认）；reviewer=每位 reviewer 独立处理（算人类上限用）",
    )
    parser.add_argument("--out", help="输出目录，默认 outputs/novelty_reference/<mode>")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--model", help="OpenRouter slug，默认取 judge 或 llm 的模型")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument(
        "--concurrency",
        type=int,
        default=6,
        help="并发数。实测 12 会触发连接错误，6 稳定",
    )
    parser.add_argument("--limit", type=int, help="只处理前 N 篇论文")
    parser.add_argument("--paper-id", action="append", default=[], help="只处理指定论文（可重复）")
    parser.add_argument("--max-reviews", type=int, help="每篇论文最多用几份 review")
    parser.add_argument(
        "--with-rating",
        action="store_true",
        help="把 reviewer 的 rating/confidence 给模型看（默认不给，避免锚定）",
    )
    parser.add_argument("--overwrite", action="store_true", help="忽略已有结果，重跑全部")
    parser.add_argument(
        "--print-prompt",
        choices=["extract", "score"],
        help="打印第一个任务的 prompt 后退出（score 需先跑 extract）",
    )
    parser.add_argument("--dry-run", action="store_true", help="用 MockBackend 走通两阶段，不调 API")
    parser.add_argument("--aggregate-only", action="store_true", help="只根据已有 records.jsonl 重算聚合")
    args = parser.parse_args()

    from alphaideabench.config import Settings
    from alphaideabench.core.llm import build_backend
    from alphaideabench.core.prompt import render_file
    from alphaideabench.domain.dimensions import load_catalog

    settings = Settings.load(args.config)
    catalog = load_catalog()
    dimensions = [d for d in catalog.ordered() if (getattr(d, "group", "") or "") == NOVELTY_GROUP]
    if not dimensions:
        raise SystemExit(f"no dimension in group '{NOVELTY_GROUP}'")
    dimension_ids = [d.id for d in dimensions]

    out_dir = Path(args.out) if args.out else DEFAULT_OUT / args.mode
    out_dir.mkdir(parents=True, exist_ok=True)
    records_path = out_dir / "records.jsonl"
    errors_path = out_dir / "errors.jsonl"

    if args.aggregate_only:
        records = read_jsonl(records_path)
        if not records:
            raise SystemExit(f"no records in {records_path}")
        papers, summary = aggregate(records, dimension_ids)
        write_json(out_dir / "papers.json", papers)
        write_json(out_dir / "summary.json", summary)
        print(f"[nov] aggregated {len(records)} record(s) over {len(papers)} paper(s)")
        report(summary, dimension_ids)
        return 0

    raw = json.loads(Path(args.papers).read_text(encoding="utf-8"))
    if args.paper_id:
        wanted = set(args.paper_id)
        raw = [p for i, p in enumerate(raw) if paper_id_of(p, i) in wanted]
    if args.limit:
        raw = raw[: args.limit]

    tasks = build_tasks(raw, args.mode, args.with_rating, args.max_reviews)
    if not tasks:
        raise SystemExit("no reviews to process")

    model = args.model or settings.agents.judge.model or settings.llm.model
    backend = build_backend(settings, dry_run=args.dry_run)
    json_mode = bool(getattr(settings.llm, "json_mode", False))

    if args.print_prompt == "extract":
        task = tasks[0]
        print(render_file(EXTRACT_SYSTEM, dimensions=dimensions))
        print("\n" + "=" * 70 + " USER\n")
        print(
            render_file(
                EXTRACT_USER,
                paper_id=task.paper_id,
                title=task.title,
                abstract=task.abstract,
                reviews=task.reviews,
            )
        )
        return 0
    if args.print_prompt == "score":
        task = tasks[0]
        facets, meta, _ = run_extract(
            task,
            backend=backend,
            dimensions=dimensions,
            dimension_ids=dimension_ids,
            model=model,
            temperature=args.temperature,
            json_mode=json_mode,
        )
        print(render_file(SCORE_SYSTEM, dimensions=dimensions))
        print("\n" + "=" * 70 + " USER\n")
        print(
            render_file(
                SCORE_USER,
                paper_id=task.paper_id,
                n_reviewers=len(task.reviews),
                facets=[{"dimension_id": d, "remarks": facets[d]} for d in dimension_ids],
                disagreement=meta.get("disagreement", ""),
                overall_notes=meta.get("overall_notes", ""),
            )
        )
        return 0

    existing = [] if args.overwrite else read_jsonl(records_path)
    done = {r["key"] for r in existing}
    pending = [t for t in tasks if t.key not in done]

    print(
        f"[nov] mode={args.mode} model={model} dims={len(dimension_ids)} "
        f"papers={len({t.paper_id for t in tasks})} tasks={len(tasks)} "
        f"pending={len(pending)} out={out_dir}",
        flush=True,
    )
    if not pending:
        print("[nov] nothing to do; use --overwrite to redo")
        papers, summary = aggregate(existing, dimension_ids)
        write_json(out_dir / "papers.json", papers)
        write_json(out_dir / "summary.json", summary)
        report(summary, dimension_ids)
        return 0

    records = list(existing)
    lock = threading.Lock()
    mode_flag = "w" if args.overwrite else "a"
    ok = 0
    fail = 0

    # Append each record as it lands. A run of several hundred papers takes long enough
    # that a crash or an interrupt part way through must not cost the completed work --
    # rerunning without --overwrite picks up from here.
    with records_path.open(mode_flag, encoding="utf-8") as sink, ThreadPoolExecutor(
        max_workers=max(1, args.concurrency)
    ) as pool:
        futures = {
            pool.submit(
                run_task,
                task,
                backend=backend,
                dimensions=dimensions,
                dimension_ids=dimension_ids,
                mode=args.mode,
                model=model,
                temperature=args.temperature,
                json_mode=json_mode,
            ): task
            for task in pending
        }
        for i, future in enumerate(as_completed(futures), 1):
            task = futures[future]
            try:
                record = future.result()
            except Exception as exc:  # noqa: BLE001 - one bad paper must not sink the run
                fail += 1
                with lock:
                    with errors_path.open("a", encoding="utf-8") as errsink:
                        errsink.write(
                            json.dumps(
                                {"key": task.key, "error": f"{type(exc).__name__}: {exc}"},
                                ensure_ascii=False,
                            )
                            + "\n"
                        )
                print(f"[nov] {i}/{len(pending)} {task.key} FAILED {type(exc).__name__}: {exc}", flush=True)
                continue

            ok += 1
            with lock:
                records.append(record)
                sink.write(json.dumps(record, ensure_ascii=False) + "\n")
                sink.flush()
            n_cov = sum(1 for d in dimension_ids if record["dimensions"][d]["covered"])
            n_rem = sum(record["n_remarks"].values())
            note = f" flags={len(record['flags'])}" if record["flags"] else ""
            print(
                f"[nov] {i}/{len(pending)} {task.key} remarks={n_rem} "
                f"covered={n_cov}/{len(dimension_ids)}{note}",
                flush=True,
            )

    print(f"\n[nov] ok={ok} fail={fail} records={len(records)}")
    if not records:
        return 1
    papers, summary = aggregate(records, dimension_ids)
    write_json(out_dir / "papers.json", papers)
    write_json(out_dir / "summary.json", summary)
    print(f"[nov] wrote records.jsonl, papers.json, summary.json in {out_dir}")
    report(summary, dimension_ids)
    return 0


def report(summary: dict[str, Any], dimension_ids: list[str]) -> None:
    print("\n[nov] per dimension:")
    for did in dimension_ids:
        s = summary["by_dimension"][did]
        mean = f"{s['mean']:.2f}" if s["mean"] is not None else " n/a"
        rho = s["rho_vs_venue_rating"]["rho"]
        rho_s = f"{rho:+.3f}" if rho is not None else "  n/a"
        agree = s["reviewer_agreement"]
        agree_s = (
            f" agree={agree['exact']:.2f}/±1={agree['within_one']:.2f}"
            if agree["exact"] is not None
            else ""
        )
        print(
            f"  {did:<18} coverage={s['coverage']:.2f} mean={mean} "
            f"remarks/rec={s['mean_remarks_per_record'] or 0:.1f} "
            f"rho_vs_rating={rho_s}{agree_s}"
        )
    if summary["flag_counts"]:
        print(f"\n[nov] flags: {summary['flag_counts']}")


if __name__ == "__main__":
    raise SystemExit(main())
