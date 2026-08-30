from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ResourcePlan(BaseModel):
    gpu: str = ""
    estimated_gpu_hours: float = 0
    estimated_api_usd: float = 0
    estimated_human_hours: float = 0
    calendar_weeks: float = 0
    notes: str = ""


class ResearchIdea(BaseModel):
    idea_id: str | None = None
    topic_id: str | None = None
    title: str
    research_question: str = ""
    hypothesis: str = ""
    problem: str = ""
    motivation: str = ""
    method: str = ""
    experiments: str = ""
    baselines: str = ""
    success_criteria: str = ""
    related_work: str = ""
    limitations: str = ""
    resource_plan: ResourcePlan = Field(default_factory=ResourcePlan)
    extra: dict[str, Any] = Field(default_factory=dict)

    def embedding_text(self) -> str:
        parts = [
            self.title,
            self.research_question,
            self.problem,
            self.motivation,
            self.method,
            self.experiments,
        ]
        return "\n".join(p.strip() for p in parts if p and p.strip())

    def to_markdown(self) -> str:
        rp = self.resource_plan
        return (
            f"# {self.title}\n\n"
            f"**Research question:** {self.research_question}\n\n"
            f"**Hypothesis:** {self.hypothesis}\n\n"
            f"## Problem\n{self.problem}\n\n"
            f"## Motivation\n{self.motivation}\n\n"
            f"## Method\n{self.method}\n\n"
            f"## Experiments\n{self.experiments}\n\n"
            f"## Baselines\n{self.baselines}\n\n"
            f"## Success criteria\n{self.success_criteria}\n\n"
            f"## Related work\n{self.related_work}\n\n"
            f"## Limitations\n{self.limitations}\n\n"
            f"## Resource plan\n"
            f"- GPU: {rp.gpu}\n"
            f"- GPU hours: {rp.estimated_gpu_hours}\n"
            f"- API USD: {rp.estimated_api_usd}\n"
            f"- Human hours: {rp.estimated_human_hours}\n"
            f"- Calendar weeks: {rp.calendar_weeks}\n"
            f"- Notes: {rp.notes}\n"
        )
