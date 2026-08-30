"""Built-in tools. Agents pick a subset by name; the framework stays generic."""

from __future__ import annotations

import json

from alphaideabench.core.tools import GLOBAL_REGISTRY, RunContext, tool
from alphaideabench.domain.dimensions import load_catalog


@tool
def load_topic(ctx: RunContext) -> str:
    """Load the full research topic document, including background, related work, and budget."""
    if ctx.topic is None:
        return "No topic is bound to this run."
    return ctx.topic.to_markdown()


@tool
def load_budget(ctx: RunContext) -> str:
    """Load the structured budget constraints that judging must use."""
    if ctx.topic is None:
        return "No topic is bound to this run."
    budget = ctx.topic.budget.model_dump()
    return (
        ctx.topic.budget.to_markdown()
        + "\n\nJSON:\n"
        + json.dumps(budget, ensure_ascii=False, indent=2)
    )


@tool
def load_idea(ctx: RunContext) -> str:
    """Load the research idea currently being judged."""
    if ctx.idea is not None:
        return ctx.idea.to_markdown()
    if ctx.idea_text:
        return ctx.idea_text
    return "No idea is bound to this run."


@tool
def load_rubric(ctx: RunContext) -> str:
    """Load the scoring rubric and checklist for the current judge dimension."""
    if not ctx.dimension_id:
        return "No dimension_id is bound to this run."
    catalog = load_catalog()
    if ctx.dimension_id not in catalog.dimensions:
        return f"Unknown dimension: {ctx.dimension_id}"
    return catalog.dimensions[ctx.dimension_id].rubric_markdown()


def bound_registry(tool_names: list[str]):
    return GLOBAL_REGISTRY.subset(tool_names)
