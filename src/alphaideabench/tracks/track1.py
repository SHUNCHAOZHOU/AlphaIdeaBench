from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from alphaideabench.agents.judge import DimensionJudge
from alphaideabench.config import Settings
from alphaideabench.core.llm import LLMBackend
from alphaideabench.domain.dimensions import load_catalog
from alphaideabench.domain.idea import ResearchIdea
from alphaideabench.domain.score import DimensionJudgment, RepeatedJudgment, Track1Result
from alphaideabench.domain.topic import Topic


class Track1Runner:
    def __init__(self, settings: Settings, backend: LLMBackend) -> None:
        self.settings = settings
        self.judge = DimensionJudge(settings, backend)
        self.catalog = load_catalog()
        self.repeats = max(1, settings.agents.judge.repeats)
        self.workers = max(1, settings.agents.judge.workers)

    def evaluate(
        self,
        topic: Topic,
        idea: ResearchIdea,
        out_dir: Path | None = None,
        dimension_ids: list[str] | None = None,
    ) -> Track1Result:
        dims = dimension_ids or [d.id for d in self.catalog.ordered()]
        jobs = [
            (di, dim_id, r)
            for di, dim_id in enumerate(dims, 1)
            for r in range(self.repeats)
        ]

        def run_one(di: int, dim_id: str, r: int) -> tuple[str, int, DimensionJudgment]:
            print(
                f"[track1] {idea.idea_id} {dim_id} ({di}/{len(dims)}) repeat {r + 1}/{self.repeats}",
                flush=True,
            )
            judgment, agent_result = self.judge.judge(topic, idea, dim_id, repeat_index=r)
            if out_dir is not None:
                dim_dir = out_dir / dim_id
                dim_dir.mkdir(parents=True, exist_ok=True)
                (dim_dir / f"repeat_{r}.json").write_text(
                    json.dumps(
                        {
                            "judgment": judgment.model_dump(),
                            "transcript": agent_result.to_dict(),
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                    encoding="utf-8",
                )
            return dim_id, r, judgment

        collected: list[tuple[str, int, DimensionJudgment]] = []
        n_workers = min(self.workers, len(jobs)) if jobs else 1
        if n_workers <= 1:
            collected = [run_one(*job) for job in jobs]
        else:
            print(
                f"[track1] parallel workers={n_workers} jobs={len(jobs)} "
                f"(dimensions={len(dims)} repeats={self.repeats})",
                flush=True,
            )
            with ThreadPoolExecutor(max_workers=n_workers) as pool:
                futures = [pool.submit(run_one, *job) for job in jobs]
                for fut in as_completed(futures):
                    collected.append(fut.result())

        grouped: dict[str, list[tuple[int, DimensionJudgment]]] = {dim_id: [] for dim_id in dims}
        for dim_id, r, judgment in collected:
            grouped[dim_id].append((r, judgment))
        by_dimension: dict[str, RepeatedJudgment] = {}
        for dim_id in dims:
            grouped[dim_id].sort(key=lambda item: item[0])
            by_dimension[dim_id] = RepeatedJudgment.from_repeats(
                dim_id, [judgment for _, judgment in grouped[dim_id]]
            )

        group_means: dict[str, float] = {}
        for gid, group in self.catalog.groups.items():
            vals = [by_dimension[did].mean for did in group.dimensions if did in by_dimension]
            if vals:
                group_means[gid] = sum(vals) / len(vals)

        readiness = by_dimension["research_readiness"].mean if "research_readiness" in by_dimension else 0.0
        result = Track1Result(
            idea_id=idea.idea_id or "unknown",
            topic_id=topic.id,
            by_dimension=by_dimension,
            group_means=group_means,
            research_readiness=readiness,
        )
        if out_dir is not None:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "aggregate.json").write_text(
                result.model_dump_json(indent=2),
                encoding="utf-8",
            )
        return result
