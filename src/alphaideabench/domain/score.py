from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from statistics import median
from typing import Any

from pydantic import BaseModel, Field


#: The only judgements a checklist item may carry. Anything else is normalised
#: away and flagged, so a malformed label can never silently reach the output.
CHECKLIST_JUDGMENTS = ("yes", "no", "partial", "n/a")

#: Common ways models spell the four allowed labels.
_JUDGMENT_ALIASES = {
    "y": "yes",
    "true": "yes",
    "pass": "yes",
    "n": "no",
    "false": "no",
    "fail": "no",
    "partially": "partial",
    "partial yes": "partial",
    "mixed": "partial",
    "na": "n/a",
    "n.a.": "n/a",
    "not applicable": "n/a",
    "unknown": "n/a",
}


def normalise_judgment(raw: Any) -> tuple[str, bool]:
    """Map a raw checklist label onto :data:`CHECKLIST_JUDGMENTS`.

    Returns the normalised label plus whether the input had to be repaired. An
    unrecognisable label becomes ``""`` so downstream code can tell it apart
    from a genuine ``n/a``.
    """
    text = str(raw or "").strip().lower()
    if not text:
        return "", False
    if text in CHECKLIST_JUDGMENTS:
        return text, False
    if text in _JUDGMENT_ALIASES:
        return _JUDGMENT_ALIASES[text], True
    return "", True


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
    #: Checklist items the rubric asked for but the judge never answered.
    missing_checklist_items: list[str] = Field(default_factory=list)

    @classmethod
    def from_llm(
        cls,
        payload: dict[str, Any],
        dimension_id: str,
        repeat_index: int = 0,
        expected_checklist: list[str] | None = None,
    ) -> DimensionJudgment:
        raw = payload.get("score", 3)
        raw_flags = payload.get("flags") or []
        flags: list[str] = []
        if isinstance(raw_flags, list):
            for f in raw_flags:
                if isinstance(f, str):
                    flags.append(f)
                elif isinstance(f, dict):
                    flags.append(str(f.get("type") or f.get("name") or json.dumps(f, ensure_ascii=False)))
                else:
                    flags.append(str(f))
        elif isinstance(raw_flags, str):
            flags.append(raw_flags)
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
        bad_labels = 0
        if isinstance(notes_raw, list):
            for item in notes_raw:
                if isinstance(item, dict):
                    label, repaired = normalise_judgment(
                        item.get("judgment") or item.get("result")
                    )
                    if repaired:
                        bad_labels += 1
                    notes.append(
                        ChecklistNote(
                            item=_strip_polarity_tag(
                                item.get("item") or item.get("check") or ""
                            ),
                            judgment=label,
                            evidence=str(item.get("evidence") or item.get("note") or ""),
                        )
                    )
                else:
                    notes.append(ChecklistNote(item=_strip_polarity_tag(item)))
        if bad_labels:
            flags.append("checklist_label_invalid")

        missing = _missing_checklist_items(expected_checklist, notes)
        if missing:
            flags.append("checklist_incomplete")
        if _looks_non_english(notes):
            flags.append("checklist_language_drift")

        return cls(
            dimension_id=str(payload.get("dimension_id") or dimension_id),
            score=score,
            reasoning=str(payload.get("reasoning") or ""),
            checklist_notes=notes,
            confidence=_as_float(payload.get("confidence")),
            flags=flags,
            repeat_index=repeat_index,
            missing_checklist_items=missing,
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
    overall: float


#: The polarity hint the rubric appends to each prompt line. Judges often copy the
#: whole rendered line verbatim, so it has to be stripped before matching.
_POLARITY_TAG_RE = re.compile(r"\s*\[\s*yes\s*=\s*(?:good|problem)\s*\]\s*$", re.I)


def _strip_polarity_tag(text: Any) -> str:
    """Drop the ``[yes = good]`` hint a judge may have copied into the item text."""
    return _POLARITY_TAG_RE.sub("", str(text or "")).strip()


def _normalise_item(text: str) -> str:
    """Collapse cosmetic differences so item matching survives verbatim copying."""
    cleaned = _POLARITY_TAG_RE.sub("", str(text or ""))
    cleaned = " ".join(cleaned.split()).lower()
    for ch in ('"', "'", "\u201c", "\u201d", "\u2018", "\u2019", "`"):
        cleaned = cleaned.replace(ch, "")
    return cleaned.rstrip("?.:; ")


def _match_item(candidate: str, answered: dict[str, str]) -> bool:
    """Match an expected item against answered ones, tolerating small typos.

    Judges occasionally drop a letter (``hyothesis``) while otherwise copying the
    line correctly. Treating that as "unanswered" would produce false alarms, so
    fall back to a similarity ratio once exact matching fails.
    """
    if candidate in answered:
        return True
    for got in answered:
        if abs(len(got) - len(candidate)) > 8:
            continue
        if SequenceMatcher(None, candidate, got).ratio() >= 0.93:
            return True
    return False


def _missing_checklist_items(
    expected: list[str] | None, notes: list[ChecklistNote]
) -> list[str]:
    """Return the expected checklist items that no note answered."""
    if not expected:
        return []
    answered = {_normalise_item(n.item): n.item for n in notes if n.judgment}
    return [
        item for item in expected if not _match_item(_normalise_item(item), answered)
    ]


def _looks_non_english(notes: list[ChecklistNote]) -> bool:
    """Detect CJK characters in echoed checklist items (breaks cross-run alignment)."""
    return any(
        any("\u4e00" <= ch <= "\u9fff" for ch in (note.item or "")) for note in notes
    )


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
