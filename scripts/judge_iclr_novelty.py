#!/usr/bin/env python
"""Run the production novelty judges on ICLR title+abstract ideas.

The review-derived reference in ``outputs/novelty_reference/paper`` is the
comparison target. This script never shows those reviews to the judge: each
paper becomes a ``ResearchIdea`` from title and abstract only.

Spearman is computed per dimension, and only on papers whose reference score
is ``covered`` (reviewers actually spoke to that facet). Uncovered facets are
skipped, not filled with 3.

Examples:
    python scripts/judge_iclr_novelty.py --limit 5 --concurrency 4 --repeats 1
    python scripts/judge_iclr_novelty.py --limit 20 --concurrency 4 --repeats 1
    python scripts/judge_iclr_novelty.py --related-work-dir paper_dataset/related_work \\
        --topic data/topics/iclr_idea_related.md --out outputs/judge_iclr_novelty_related --limit 20
    python scripts/judge_iclr_novelty.py --correlate-only
"""

from __future__ import annotations

import argparse
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAPERS = REPO_ROOT / "paper_dataset/subset-200.json"
DEFAULT_REFERENCE = REPO_ROOT / "outputs/novelty_reference/paper/papers.json"
DEFAULT_TOPIC = REPO_ROOT / "examples/topics/icbinb.md"
DEFAULT_OUT = REPO_ROOT / "outputs/judge_iclr_novelty"

NOVELTY_GROUP = "novelty"
_FORUM_ID = re.compile(r"[?&]id=([A-Za-z0-9_-]+)")


def paper_id_of(paper: dict[str, Any], index: int = 0) -> str:
    match = _FORUM_ID.search(paper.get("url") or "")
    if match:
        return match.group(1)
    return paper.get("_bibkey") or f"paper_{index:04d}"


def load_related_work(related_dir: Path | None, paper_id: str) -> str:
    if related_dir is None:
        return ""
    path = related_dir / f"{paper_id}.json"
    if not path.exists():
        return ""
    payload = json.loads(path.read_text(encoding="utf-8"))
    return str(payload.get("text") or "").strip()


def paper_to_idea(
    paper: dict[str, Any],
    topic: Any,
    index: int = 0,
    related_work: str = "",
):
    """Map one ICLR record onto a ResearchIdea. Reviews are dropped."""
    from alphaideabench.domain.idea import ResearchIdea

    pid = paper_id_of(paper, index)
    abstract = (paper.get("abstract") or "").strip()
    title = (paper.get("title") or "").strip() or pid
    return ResearchIdea(
        idea_id=pid,
        topic_id=topic.id,
        title=title,
        problem=abstract,
        method=abstract,
        related_work=related_work,
        extra={
            "source": "iclr_abstract_related" if related_work else "iclr_abstract",
            "url": paper.get("url") or "",
            "venue": paper.get("venue") or "",
        },
    )


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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 4) if values else None


def correlate(
    records: list[dict[str, Any]],
    reference: dict[str, Any],
    dimension_ids: list[str],
) -> dict[str, Any]:
    from alphaideabench.metrics import spearman_correlation

    per_dim: dict[str, Any] = {}
    for did in dimension_ids:
        pairs: list[tuple[str, float, float]] = []
        for rec in records:
            pid = rec["paper_id"]
            judge = (rec.get("dimensions") or {}).get(did) or {}
            jscore = judge.get("score")
            href = ((reference.get(pid) or {}).get("by_dimension") or {}).get(did) or {}
            hscore = href.get("mean")
            if jscore is None or hscore is None:
                continue
            pairs.append((pid, float(jscore), float(hscore)))

        n = len(pairs)
        diffs = [abs(j - h) for _, j, h in pairs]
        rho = spearman_correlation([j for _, j, _ in pairs], [h for _, _, h in pairs]) if n >= 2 else None
        per_dim[did] = {
            "n": n,
            "rho": rho,
            "exact_agreement": _mean([float(d == 0) for d in diffs]),
            "within_one": _mean([float(d <= 1) for d in diffs]),
            "mean_abs_diff": _mean(diffs),
            "judge_mean": _mean([j for _, j, _ in pairs]),
            "human_mean": _mean([h for _, _, h in pairs]),
        }

    n_any = sum(
        1
        for rec in records
        if rec["paper_id"] in reference
        and any(
            ((rec.get("dimensions") or {}).get(d) or {}).get("score") is not None
            and ((reference[rec["paper_id"]].get("by_dimension") or {}).get(d) or {}).get("mean") is not None
            for d in dimension_ids
        )
    )
    return {
        "n_judge_records": len(records),
        "n_papers_with_any_matched_facet": n_any,
        "by_dimension": per_dim,
        "rule": "pairs only where the review-derived reference has a covered score",
    }


def report(summary: dict[str, Any], dimension_ids: list[str]) -> None:
    print("\n[judge] matched Spearman vs review-derived reference:")
    for did in dimension_ids:
        s = summary["by_dimension"][did]
        rho = s["rho"]
        rho_s = f"{rho:+.3f}" if rho is not None else "  n/a"
        print(
            f"  {did:<18} n={s['n']:<4} rho={rho_s}  "
            f"exact={s['exact_agreement'] if s['exact_agreement'] is not None else 'n/a'}  "
            f"±1={s['within_one'] if s['within_one'] is not None else 'n/a'}  "
            f"MAD={s['mean_abs_diff'] if s['mean_abs_diff'] is not None else 'n/a'}"
        )


def run_one(
    idea: Any,
    topic: Any,
    *,
    settings: Any,
    backend: Any,
    dimension_ids: list[str],
    repeats: int,
) -> dict[str, Any]:
    from alphaideabench.tracks.track1 import Track1Runner

    runner = Track1Runner(settings, backend)
    runner.repeats = repeats
    runner.workers = 1
    result = runner.evaluate(topic, idea, out_dir=None, dimension_ids=dimension_ids)
    scored: dict[str, Any] = {}
    for did, block in result.by_dimension.items():
        # repeats=1 for the pilot; still store the aggregate so later repeats work.
        scored[did] = {
            "score": block.mean,
            "std": block.std,
            "exact_agreement": block.exact_agreement,
            "n_repeats": len(block.repeats),
            "confidence": block.repeats[0].confidence if block.repeats else None,
            "flags": [f for r in block.repeats for f in r.flags],
            "reasoning": block.repeats[0].reasoning if block.repeats else "",
        }
    return {
        "paper_id": idea.idea_id,
        "title": idea.title,
        "mode": "judge",
        "model": settings.agents.judge.model or settings.llm.model,
        "dimensions": scored,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--papers", default=str(DEFAULT_PAPERS))
    parser.add_argument("--reference", default=str(DEFAULT_REFERENCE))
    parser.add_argument("--topic", default=str(DEFAULT_TOPIC))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--model", help="覆盖 chat 模型")
    parser.add_argument("--provider", help="覆盖 LLM provider (如 openrouter, gemini, deepseek)")
    parser.add_argument("--dimensions", nargs="+", help="只评这些维度，默认 novelty 组四维")
    parser.add_argument("--repeats", type=int, default=1, help="每维重复次数，校准先用 1")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--limit", type=int, help="只跑前 N 篇")
    parser.add_argument("--paper-id", action="append", default=[])
    parser.add_argument(
        "--related-work-dir",
        help="paper_dataset/related_work：把抽出的 Related Work 填进 idea",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--correlate-only", action="store_true")
    args = parser.parse_args()

    from alphaideabench.config import Settings
    from alphaideabench.core.llm import build_backend
    from alphaideabench.domain.dimensions import load_catalog
    from alphaideabench.domain.topic import Topic

    settings = Settings.load(args.config)
    if args.provider:
        settings.llm.provider = args.provider
    elif args.model and "/" in args.model:
        settings.llm.provider = "openrouter"

    if args.model:
        settings.llm.model = args.model
        settings.agents.judge.model = args.model
    catalog = load_catalog()
    dimension_ids = [d.id for d in catalog.ordered() if (getattr(d, "group", "") or "") == NOVELTY_GROUP]
    if args.dimensions:
        wanted = list(args.dimensions)
        known = {d.id for d in catalog.ordered()}
        missing = [d for d in wanted if d not in known]
        if missing:
            raise SystemExit(f"unknown dimension(s): {missing}")
        dimension_ids = wanted
    if not dimension_ids:
        raise SystemExit(f"no dimension in group '{NOVELTY_GROUP}'")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    records_path = out_dir / "records.jsonl"
    errors_path = out_dir / "errors.jsonl"
    summary_path = out_dir / "summary.json"

    reference: dict[str, Any] = {}
    ref_path = Path(args.reference)
    if ref_path.exists():
        reference = json.loads(ref_path.read_text(encoding="utf-8"))

    if args.correlate_only:
        records = read_jsonl(records_path)
        if not records:
            raise SystemExit(f"no records in {records_path}")
        summary = correlate(records, reference, dimension_ids)
        write_json(summary_path, summary)
        report(summary, dimension_ids)
        return 0

    topic = Topic.from_markdown(args.topic)
    raw = json.loads(Path(args.papers).read_text(encoding="utf-8"))
    if args.paper_id:
        wanted = set(args.paper_id)
        raw = [p for i, p in enumerate(raw) if paper_id_of(p, i) in wanted]
    if args.limit:
        raw = raw[: args.limit]

    related_dir = Path(args.related_work_dir) if args.related_work_dir else None
    ideas = [
        paper_to_idea(p, topic, i, related_work=load_related_work(related_dir, paper_id_of(p, i)))
        for i, p in enumerate(raw)
    ]
    if related_dir:
        n_rw = sum(1 for idea in ideas if idea.related_work)
        print(f"[judge] related_work attached on {n_rw}/{len(ideas)} idea(s)", flush=True)
    backend = build_backend(settings, dry_run=args.dry_run)

    existing = [] if args.overwrite else read_jsonl(records_path)
    done = {r["paper_id"] for r in existing}
    pending = [idea for idea in ideas if idea.idea_id not in done]

    print(
        f"[judge] model={settings.agents.judge.model or settings.llm.model} "
        f"dims={len(dimension_ids)} papers={len(ideas)} pending={len(pending)} "
        f"repeats={args.repeats} out={out_dir}",
        flush=True,
    )
    if not pending:
        print("[judge] nothing to do; use --overwrite to redo")
        summary = correlate(existing, reference, dimension_ids)
        write_json(summary_path, summary)
        report(summary, dimension_ids)
        return 0

    records = list(existing)
    lock = threading.Lock()
    mode_flag = "w" if args.overwrite else "a"
    ok = 0
    fail = 0

    with records_path.open(mode_flag, encoding="utf-8") as sink, ThreadPoolExecutor(
        max_workers=max(1, args.concurrency)
    ) as pool:
        futures = {
            pool.submit(
                run_one,
                idea,
                topic,
                settings=settings,
                backend=backend,
                dimension_ids=dimension_ids,
                repeats=args.repeats,
            ): idea
            for idea in pending
        }
        for i, future in enumerate(as_completed(futures), 1):
            idea = futures[future]
            try:
                record = future.result()
            except Exception as exc:  # noqa: BLE001
                fail += 1
                with lock:
                    with errors_path.open("a", encoding="utf-8") as errsink:
                        errsink.write(
                            json.dumps(
                                {"paper_id": idea.idea_id, "error": f"{type(exc).__name__}: {exc}"},
                                ensure_ascii=False,
                            )
                            + "\n"
                        )
                print(f"[judge] {i}/{len(pending)} {idea.idea_id} FAILED {type(exc).__name__}: {exc}", flush=True)
                continue

            ok += 1
            with lock:
                records.append(record)
                sink.write(json.dumps(record, ensure_ascii=False) + "\n")
                sink.flush()
            scores = " ".join(
                f"{d}={record['dimensions'][d]['score']:.0f}"
                if record["dimensions"][d]["score"] is not None
                else f"{d}=-"
                for d in dimension_ids
            )
            print(f"[judge] {i}/{len(pending)} {idea.idea_id} {scores}", flush=True)

    print(f"\n[judge] ok={ok} fail={fail} records={len(records)}")
    if not records:
        return 1
    summary = correlate(records, reference, dimension_ids)
    write_json(summary_path, summary)
    print(f"[judge] wrote {records_path} and {summary_path}")
    report(summary, dimension_ids)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
