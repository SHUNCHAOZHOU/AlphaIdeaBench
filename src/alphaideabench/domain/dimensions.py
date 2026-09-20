from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

from alphaideabench.paths import resolve_path

#: ``yes`` on a positive item is evidence *for* a higher score; ``yes`` on a
#: negative item is evidence *against* it. Declaring this explicitly keeps the
#: judge from having to infer polarity from the wording of each question.
POLARITIES = ("positive", "negative")


class ChecklistItem(BaseModel):
    """One checklist question, with the direction its ``yes`` answer points."""

    text: str
    polarity: str = "positive"
    note: str = ""

    @field_validator("polarity")
    @classmethod
    def _known_polarity(cls, value: str) -> str:
        if value not in POLARITIES:
            raise ValueError(f"polarity must be one of {POLARITIES}, got {value!r}")
        return value

    def prompt_line(self) -> str:
        marker = "yes = good" if self.polarity == "positive" else "yes = problem"
        line = f"- {self.text}  [{marker}]"
        if self.note:
            line += f"\n  - note: {' '.join(self.note.split())}"
        return line


class DimensionSpec(BaseModel):
    id: str
    index: int
    group: str
    name: str
    question: str
    scores: dict[str, str]
    checklist: list[ChecklistItem] = Field(default_factory=list)

    @field_validator("checklist", mode="before")
    @classmethod
    def _accept_plain_strings(cls, value: Any) -> Any:
        """Allow legacy ``checklist: [str, ...]`` YAML to keep loading."""
        if not isinstance(value, list):
            return value
        return [{"text": item} if isinstance(item, str) else item for item in value]

    @property
    def checklist_texts(self) -> list[str]:
        return [item.text for item in self.checklist]

    def rubric_markdown(self) -> str:
        lines = [
            f"## {self.index}. {self.name} (`{self.id}`)",
            "",
            self.question.strip(),
            "",
            "### Scoring rubric",
        ]
        for score in sorted(self.scores, key=lambda x: int(x)):
            lines.append(f"- **{score}**: {self.scores[score].strip()}")
        lines.extend(["", "### Checklist"])
        for item in self.checklist:
            lines.append(item.prompt_line())
        return "\n".join(lines)


class GroupSpec(BaseModel):
    id: str
    name: str
    description: str = ""
    dimensions: list[str] = Field(default_factory=list)


class DimensionCatalog(BaseModel):
    groups: dict[str, GroupSpec]
    dimensions: dict[str, DimensionSpec]

    def ordered(self) -> list[DimensionSpec]:
        return sorted(self.dimensions.values(), key=lambda d: d.index)

    def group_of(self, dimension_id: str) -> str:
        return self.dimensions[dimension_id].group


@lru_cache(maxsize=4)
def load_catalog(path: str = "prompts/dimensions.yaml") -> DimensionCatalog:
    raw: dict[str, Any] = yaml.safe_load(resolve_path(path).read_text(encoding="utf-8"))
    groups = {gid: GroupSpec(id=gid, **g) for gid, g in (raw.get("groups") or {}).items()}
    dimensions: dict[str, DimensionSpec] = {}
    for did, spec in (raw.get("dimensions") or {}).items():
        dimensions[did] = DimensionSpec(id=did, **spec)
    return DimensionCatalog(groups=groups, dimensions=dimensions)
