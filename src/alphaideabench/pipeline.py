from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from alphaideabench.config import Settings
from alphaideabench.core.llm import LLMBackend, build_backend
from alphaideabench.domain.idea import ResearchIdea
from alphaideabench.domain.topic import Topic
from alphaideabench.tracks.track1 import Track1Runner
from alphaideabench.tracks.track2 import build_embedder, evaluate_diversity


def make_run_dir(out_root: str | Path | None = None) -> Path:
    root = Path(out_root or "outputs")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = root / f"run_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def dump_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(payload, "model_dump"):
        path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
    else:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class BenchmarkPipeline:
    """Judge-only pipeline: ideas come from an external idea agent."""

    def __init__(self, settings: Settings, dry_run: bool = False) -> None:
        self.settings = settings
        self.dry_run = dry_run
        self.backend: LLMBackend = build_backend(settings, dry_run=dry_run)
        self.track1 = Track1Runner(settings, self.backend)
        self.embedder = build_embedder(settings.embedding, dry_run=dry_run)

    def judge_ideas(
        self,
        topic: Topic,
        ideas: list[ResearchIdea],
        run_dir: Path,
        repeats: int | None = None,
        skip_track1: bool = False,
        skip_track2: bool = False,
        dimension_ids: list[str] | None = None,
        workers: int | None = None,
    ) -> dict[str, Any]:
        if repeats is not None:
            self.track1.repeats = max(1, repeats)
        if workers is not None:
            self.track1.workers = max(1, workers)

        dump_json(run_dir / "config.json", self.settings.model_dump())
        topic_dir = run_dir / topic.id
        topic_dir.mkdir(parents=True, exist_ok=True)
        dump_json(topic_dir / "topic.json", topic)
        for idea in ideas:
            dump_json(topic_dir / "ideas" / f"{idea.idea_id}.json", idea)
            print(f"[pipeline] loaded idea {idea.idea_id}", flush=True)

        track1_results = []
        if not skip_track1:
            print(f"[pipeline] Track 1 judging {len(ideas)} idea(s)", flush=True)
            for idea in ideas:
                t1_dir = topic_dir / "track1" / (idea.idea_id or "idea")
                track1_results.append(
                    self.track1.evaluate(topic, idea, out_dir=t1_dir, dimension_ids=dimension_ids)
                )

        track2 = None
        if not skip_track2 and len(ideas) >= 2:
            track2 = self._run_track2(ideas, topic_dir)

        summary = {
            "topic_id": topic.id,
            "n_ideas": len(ideas),
            "idea_ids": [i.idea_id for i in ideas],
            "track1": [r.model_dump() for r in track1_results],
            "track2": track2,
        }
        dump_json(topic_dir / "summary.json", summary)
        dump_json(run_dir / "run_summary.json", {"run_dir": str(run_dir), "topics": [summary]})
        return summary

    def _run_track2(self, ideas: list[ResearchIdea], topic_dir: Path) -> dict[str, Any]:
        try:
            track2 = evaluate_diversity(
                [idea.embedding_text() for idea in ideas],
                self.embedder,
                taus=self.settings.track2.taus,
            )
            dump_json(topic_dir / "track2.json", track2)
            return track2
        except Exception as exc:
            print(f"[pipeline] Track 2 failed: {exc}", flush=True)
            payload = {"error": str(exc)}
            dump_json(topic_dir / "track2.json", payload)
            return payload
