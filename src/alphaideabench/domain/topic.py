from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class Budget(BaseModel):
    gpu: str = ""
    gpu_hours: float | None = None
    calendar_weeks: float | None = None
    api_usd: float | None = None
    annotator_hours: float | None = None
    notes: str = ""

    def to_markdown(self) -> str:
        lines = ["## Budget constraints (must be respected)"]
        if self.gpu:
            lines.append(f"- GPU: {self.gpu}")
        if self.gpu_hours is not None:
            lines.append(f"- GPU hours: {self.gpu_hours}")
        if self.calendar_weeks is not None:
            lines.append(f"- Calendar weeks: {self.calendar_weeks}")
        if self.api_usd is not None:
            lines.append(f"- API budget (USD): {self.api_usd}")
        if self.annotator_hours is not None:
            lines.append(f"- Annotator / human hours: {self.annotator_hours}")
        if self.notes:
            lines.append(f"- Notes: {self.notes}")
        return "\n".join(lines)


class Topic(BaseModel):
    id: str
    field: str = ""
    title: str = ""
    keywords: list[str] = Field(default_factory=list)
    budget: Budget = Field(default_factory=Budget)
    body: str = ""
    path: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

    def to_markdown(self) -> str:
        header = [
            f"# {self.title or self.id}",
            f"- id: {self.id}",
            f"- field: {self.field}",
        ]
        if self.keywords:
            header.append(f"- keywords: {', '.join(self.keywords)}")
        return "\n".join(header) + "\n\n" + self.budget.to_markdown() + "\n\n" + self.body.strip() + "\n"

    @classmethod
    def from_markdown(cls, path: str | Path) -> Topic:
        text = Path(path).read_text(encoding="utf-8")
        meta, body = _split_frontmatter(text)
        known = {"id", "field", "title", "keywords", "budget"}
        extra = {k: v for k, v in meta.items() if k not in known}
        topic_id = str(meta.get("id") or Path(path).stem)
        budget_raw = meta.get("budget") or {}
        if not isinstance(budget_raw, dict):
            budget_raw = {"notes": str(budget_raw)}
        return cls(
            id=topic_id,
            field=str(meta.get("field") or ""),
            title=str(meta.get("title") or topic_id),
            keywords=list(meta.get("keywords") or []),
            budget=Budget.model_validate(budget_raw),
            body=body,
            path=str(Path(path).resolve()),
            extra=extra,
        )


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return {}, text
    rest = stripped[3:]
    end = rest.find("\n---")
    if end == -1:
        return {}, text
    raw_fm = rest[:end]
    body = rest[end + 4 :]
    meta = yaml.safe_load(raw_fm) or {}
    if not isinstance(meta, dict):
        return {}, text
    return meta, body.lstrip("\n")
