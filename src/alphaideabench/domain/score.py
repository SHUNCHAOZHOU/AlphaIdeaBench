from __future__ import annotations

from statistics import median
from typing import Any

from pydantic import BaseModel, Field


class ChecklistNote(BaseModel):
    item: str
    judgment: str = ""
    evidence: str = ""


class DimensionJudgment(BaseModel):
    dimension_id: str
    score: int
    reasoning: str = ""
    checklist_notes: list[ChecklistNote] = Field(default_factory=list)
    confidence: float | None = None
    flags: list[str] = Field(default_factory=list)
    repeat_index: int = 0

    @classmethod
    def from_llm(cls, payload: dict[str, Any], dimension_id: str, repeat_index: int = 0) -> DimensionJudgment:
        raw = payload.get("score", 3)
        flags = list(payload.get("flags") or [])
        try:
            numeric = float(raw)
            score = int(round(numeric))
            if score != numeric:
                flags.append("score_rounded")
        except (TypeError, ValueError):
            score = 3
            flags.append("score_invalid_defaulted")
        score = min(5, max(1, score))
        notes_raw = payload.get("checklist_notes") or payload.get("checklist") or []
        notes: list[ChecklistNote] = []
        if isinstance(notes_raw, list):
            for item in notes_raw:
                if isinstance(item, dict):
                    notes.append(
                        ChecklistNote(
                            item=str(item.get("item") or item.get("check") or ""),
                            judgment=str(item.get("judgment") or item.get("result") or ""),
                            evidence=str(item.get("evidence") or item.get("note") or ""),
                        )
                    )
                else:
                    notes.append(ChecklistNote(item=str(item)))
        return cls(
            dimension_id=str(payload.get("dimension_id") or dimension_id),
            score=score,
            reasoning=str(payload.get("reasoning") or ""),
            checklist_notes=notes,
            confidence=_as_float(payload.get("confidence")),
            flags=flags,
            repeat_index=repeat_index,
        )


class RepeatedJudgment(BaseModel):
    dimension_id: str
    repeats: list[DimensionJudgment]
    mean: float
    std: float
    median: float
    exact_agreement: float
    mean_abs_diff: float

    @classmethod
    def from_repeats(cls, dimension_id: str, repeats: list[DimensionJudgment]) -> RepeatedJudgment:
        scores = [r.score for r in repeats]
        n = len(scores)
        mean = sum(scores) / n if n else 0.0
        var = sum((s - mean) ** 2 for s in scores) / n if n else 0.0
        exact, mad, pairs = 0.0, 0.0, 0
        for i in range(n):
            for j in range(i + 1, n):
                pairs += 1
                exact += float(scores[i] == scores[j])
                mad += abs(scores[i] - scores[j])
        return cls(
            dimension_id=dimension_id,
            repeats=repeats,
            mean=mean,
            std=var**0.5,
            median=float(median(scores)) if scores else 0.0,
            exact_agreement=(exact / pairs) if pairs else 1.0,
            mean_abs_diff=(mad / pairs) if pairs else 0.0,
        )


class Track1Result(BaseModel):
    idea_id: str
    topic_id: str
    by_dimension: dict[str, RepeatedJudgment]
    group_means: dict[str, float]
    research_readiness: float


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
