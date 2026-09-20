"""Load research ideas produced by external idea agents.

AlphaIdeaBench does not generate ideas. Ideas come from whatever agent is under
evaluation, in one of five shapes:

- native ``ResearchIdea`` JSON (this repo's schema, e.g. re-judging a past run)
- AI-Scientist-v2 ideation JSON (``Name`` / ``Title`` / ``Abstract`` / ...)
- ResearchAgent pipeline context (``problem`` / ``method`` / ``experiment``)
- CoI-Agent result JSON (``idea`` / ``experiment`` / ``idea_chain`` / ``trend``)
- Virtual-Scientists team_info JSON (``teammate`` / ``topic`` / ``idea`` / ``abstract``)

All are normalised to ``ResearchIdea`` so the 13 judges never care about the
source agent.
"""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any

from alphaideabench.domain.idea import ResearchIdea, ResourcePlan
from alphaideabench.domain.topic import Topic

_NATIVE_KEYS = ("research_question", "hypothesis", "problem", "motivation", "method", "idea_id")


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    return str(value).strip()


def _to_float(val: Any, fallback: float = 0.0) -> float:
    if val is None:
        return fallback
    try:
        if isinstance(val, (int, float)):
            return float(val)
        match = re.search(r"[-+]?(?:\d*\.\d+|\d+)", str(val))
        if match:
            return float(match.group(0))
    except Exception:
        pass
    return fallback


def _resource_plan_from_topic(topic: Topic) -> ResourcePlan:
    budget = topic.budget
    return ResourcePlan(
        gpu=budget.gpu,
        estimated_gpu_hours=float(budget.gpu_hours or 0),
        estimated_api_usd=float(budget.api_usd or 0),
        estimated_human_hours=float(budget.annotator_hours or 0),
        calendar_weeks=float(budget.calendar_weeks or 0),
        notes=budget.notes,
    )


def _resource_plan_from_raw_and_topic(raw_budget: Any, topic: Topic) -> ResourcePlan:
    budget = topic.budget
    if not raw_budget:
        return _resource_plan_from_topic(topic)
    if isinstance(raw_budget, dict):
        gpu = str(raw_budget.get("gpu") or raw_budget.get("GPU") or budget.gpu or "").strip()
        gpu_hours = _to_float(
            raw_budget.get("gpu_hours") or raw_budget.get("estimated_gpu_hours") or raw_budget.get("GPU hours"),
            fallback=float(budget.gpu_hours or 0),
        )
        api_usd = _to_float(
            raw_budget.get("api_usd") or raw_budget.get("estimated_api_usd") or raw_budget.get("API budget (USD)") or raw_budget.get("api_budget"),
            fallback=float(budget.api_usd or 0),
        )
        annotator_hours = _to_float(
            raw_budget.get("annotator_hours") or raw_budget.get("estimated_human_hours") or raw_budget.get("human_hours"),
            fallback=float(budget.annotator_hours or 0),
        )
        calendar_weeks = _to_float(
            raw_budget.get("calendar_weeks") or raw_budget.get("estimated_calendar_weeks"),
            fallback=float(budget.calendar_weeks or 0),
        )
        notes = str(raw_budget.get("notes") or budget.notes or "").strip()
        return ResourcePlan(
            gpu=gpu,
            estimated_gpu_hours=gpu_hours,
            estimated_api_usd=api_usd,
            estimated_human_hours=annotator_hours,
            calendar_weeks=calendar_weeks,
            notes=notes,
        )
    if isinstance(raw_budget, str):
        return ResourcePlan(
            gpu=budget.gpu,
            estimated_gpu_hours=float(budget.gpu_hours or 0),
            estimated_api_usd=float(budget.api_usd or 0),
            estimated_human_hours=float(budget.annotator_hours or 0),
            calendar_weeks=float(budget.calendar_weeks or 0),
            notes=raw_budget.strip(),
        )
    return _resource_plan_from_topic(topic)


def _title_from_text(text: str, fallback: str = "Untitled idea") -> str:
    cleaned = " ".join(_as_text(text).split())
    if not cleaned:
        return fallback
    for sep in (". ", "? ", "! "):
        if sep in cleaned:
            cleaned = cleaned.split(sep, 1)[0]
            break
    if len(cleaned) > 140:
        cleaned = cleaned[:137].rstrip() + "..."
    return cleaned


def idea_from_aiscientist(raw: dict[str, Any], topic: Topic) -> ResearchIdea:
    """Map one AI-Scientist-v2 idea dict onto ``ResearchIdea``.

    If the idea contains a ``Budget`` field, it is parsed into the resource plan;
    otherwise it falls back to the topic budget constraints.
    """
    hypothesis = _as_text(raw.get("Short Hypothesis"))
    abstract = _as_text(raw.get("Abstract"))
    budget_raw = raw.get("Budget") or raw.get("budget") or raw.get("Resource Plan") or raw.get("resource_plan")
    return ResearchIdea(
        title=_as_text(raw.get("Title")) or _as_text(raw.get("Name")) or "Untitled idea",
        research_question=hypothesis,
        hypothesis=hypothesis,
        problem=abstract,
        motivation=abstract,
        method=abstract,
        experiments=_as_text(raw.get("Experiments")),
        related_work=_as_text(raw.get("Related Work")),
        limitations=_as_text(raw.get("Risk Factors and Limitations")),
        resource_plan=_resource_plan_from_raw_and_topic(budget_raw, topic),
        extra={"generator": "ai-scientist-v2", "ai_scientist_v2": raw},
    )


def idea_from_researchagent(raw: dict[str, Any], topic: Topic) -> ResearchIdea:
    """Map one ResearchAgent pipeline context onto ``ResearchIdea``.

    ResearchAgent emits a problem / method / experiment triple grounded in a
    seed paper. The topic budget fills ``resource_plan`` the same way as for
    AI-Scientist-v2, so Budget Feasibility stays well-defined.
    """
    extra = raw.get("extra") if isinstance(raw.get("extra"), dict) else {}
    inner = extra.get("researchagent") if isinstance(extra.get("researchagent"), dict) else {}
    ctx = inner if inner.get("problem") or inner.get("method") else raw

    problem = _as_text(ctx.get("problem"))
    rationale = _as_text(ctx.get("problem_rationale"))
    method = _as_text(ctx.get("method"))
    method_rationale = _as_text(ctx.get("method_rationale"))
    experiment = _as_text(ctx.get("experiment")) or _as_text(ctx.get("experiments"))
    experiment_rationale = _as_text(ctx.get("experiment_rationale"))

    paper = ctx.get("paper") if isinstance(ctx.get("paper"), dict) else {}
    references = ctx.get("references") if isinstance(ctx.get("references"), list) else []
    related_titles = [
        _as_text(item.get("title"))
        for item in references
        if isinstance(item, dict) and item.get("title")
    ]
    name = _as_text(inner.get("Name") or ctx.get("Name")) or _slug(_title_from_text(problem))[:60].strip("_")
    title = (
        _as_text(raw.get("title"))
        or _as_text(inner.get("Title"))
        or _title_from_text(problem)
        or _as_text(paper.get("title"))
        or "Untitled ResearchAgent idea"
    )
    method_block = method
    if method_rationale:
        method_block = f"{method}\n\nRationale: {method_rationale}".strip()
    experiment_block = experiment
    if experiment_rationale:
        experiment_block = f"{experiment}\n\nRationale: {experiment_rationale}".strip()

    compact = {
        "Name": name,
        "problem": problem,
        "problem_rationale": rationale,
        "method": method,
        "method_rationale": method_rationale,
        "experiment": experiment,
        "experiment_rationale": experiment_rationale,
        "seed_paper": {k: paper.get(k) for k in ("title", "abstract") if paper.get(k)},
        "related_titles": related_titles,
    }
    return ResearchIdea(
        title=title,
        research_question=problem,
        hypothesis=rationale,
        problem=problem,
        motivation=rationale,
        method=method_block,
        experiments=experiment_block,
        related_work=_as_text(raw.get("related_work")) or "; ".join(related_titles),
        limitations=_as_text(raw.get("limitations")),
        resource_plan=_resource_plan_from_topic(topic),
        extra={"generator": "researchagent", "researchagent": compact},
    )


_COI_HEADINGS = (
    "title",
    "origins and motivation",
    "origins",
    "motivation",
    "novelty and contributions",
    "novelty",
    "methodology",
    "method",
    "step-by-step methodology",
    "challenges and solutions",
    "challenges",
    "conclusion",
)


def _coi_sections(text: str) -> dict[str, str]:
    """Split a CoI-Agent idea blob on ``**Heading:**`` / ``Heading:`` markers."""
    pattern = re.compile(
        r"^\s*(?:\*\*)?(" + "|".join(re.escape(h) for h in _COI_HEADINGS) + r")(?:\*\*)?\s*:\s*(.*)$",
        re.IGNORECASE | re.MULTILINE,
    )
    matches = list(pattern.finditer(text or ""))
    if not matches:
        return {}
    sections: dict[str, str] = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = " ".join((match.group(2) + "\n" + text[match.end() : end]).split()).strip()
        sections[match.group(1).strip("*").lower()] = body
    return sections


def _coi_paper_titles(idea_chain: str) -> list[str]:
    titles: list[str] = []
    for match in re.finditer(
        r"(?:^|\n)\s*\d+\.\s*Paper:\s*(.+?)\s+idea:",
        idea_chain or "",
        re.IGNORECASE,
    ):
        title = match.group(1).strip()
        if title:
            titles.append(title)
    return titles


def idea_from_coi_agent(raw: dict[str, Any], topic: Topic) -> ResearchIdea:
    """Map one CoI-Agent ``result.json`` object onto ``ResearchIdea``.

    CoI-Agent emits a free-form idea write-up plus an experiment plan, grounded
    in a literature chain. The topic budget fills ``resource_plan`` the same
    way as for the other generators, so Budget Feasibility stays well-defined.
    """
    extra = raw.get("extra") if isinstance(raw.get("extra"), dict) else {}
    inner = extra.get("coi_agent") if isinstance(extra.get("coi_agent"), dict) else {}
    src = inner if inner.get("idea") or inner.get("experiment") else raw

    idea_text = _as_text(src.get("idea") or raw.get("idea"))
    experiment = _as_text(src.get("experiment") or raw.get("experiment") or raw.get("experiments"))
    idea_chain = _as_text(src.get("idea_chain") or raw.get("idea_chain"))
    related_experiments = src.get("related_experiments")
    if related_experiments is None:
        related_experiments = raw.get("related_experiments")
    sections = _coi_sections(idea_text)
    paper_titles = _coi_paper_titles(idea_chain)

    title = (
        _as_text(raw.get("title"))
        or _as_text(inner.get("Title"))
        or sections.get("title")
        or _title_from_text(idea_text)
        or "Untitled CoI-Agent idea"
    )
    title = title.strip().strip("*").strip()
    name = _as_text(inner.get("Name") or src.get("Name") or raw.get("Name"))
    if not name:
        name = _slug(title)[:60].strip("_") or "coi_idea"

    motivation = (
        sections.get("origins and motivation")
        or sections.get("motivation")
        or sections.get("origins")
        or idea_text
    )
    novelty = sections.get("novelty and contributions") or sections.get("novelty")
    method = sections.get("methodology") or sections.get("method") or sections.get("step-by-step methodology") or idea_text
    if novelty and method and method != idea_text:
        method_block = f"{method}\n\nNovelty: {novelty}".strip()
    else:
        method_block = method
    limitations = sections.get("challenges and solutions") or sections.get("challenges") or _as_text(raw.get("limitations"))
    related_work = _as_text(raw.get("related_work")) or "; ".join(paper_titles) or idea_chain

    compact = {
        "Name": name,
        "idea": idea_text,
        "experiment": experiment,
        "idea_chain": idea_chain,
        "related_experiments": related_experiments,
        "entities": src.get("entities") or raw.get("entities"),
        "trend": src.get("trend") or raw.get("trend"),
        "future": src.get("future") or raw.get("future"),
        "paper_titles": paper_titles,
    }
    return ResearchIdea(
        title=title,
        research_question=motivation,
        hypothesis=novelty or motivation,
        problem=motivation,
        motivation=motivation,
        method=method_block,
        experiments=experiment,
        related_work=related_work,
        limitations=limitations,
        resource_plan=_resource_plan_from_topic(topic),
        extra={"generator": "coi-agent", "coi_agent": compact},
    )


_VIRSCI_IDEA_KEYS = ("Idea", "Title", "Experiment", "Clarity", "Feasibility", "Novelty")


def _json_from_text(text: str) -> dict[str, Any] | None:
    if not text or not isinstance(text, str):
        return None
    blocks = re.findall(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    candidates = [b.strip() for b in blocks] if blocks else [text.strip()]
    for blob in candidates:
        start = blob.find("{")
        end = blob.rfind("}")
        snippet = blob[start : end + 1] if start != -1 and end > start else blob
        try:
            parsed = json.loads(snippet)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _split_labeled_fields(text: str, labels: tuple[str, ...]) -> dict[str, str]:
    if not text:
        return {}
    pattern = re.compile(
        r"(?:^|[\n\"'])\s*(?:\*\*)?(" + "|".join(re.escape(label) for label in labels) + r")(?:\*\*)?\s*:\s*",
        re.IGNORECASE | re.MULTILINE,
    )
    matches = list(pattern.finditer(text))
    if not matches:
        return {}
    sections: dict[str, str] = {}
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[match.end() : end].strip().strip(",").strip().strip('"').strip()
        sections[match.group(1)] = body
    return sections


def _parse_virsci_idea_blob(raw: Any) -> dict[str, Any]:
    if isinstance(raw, list):
        for item in reversed(raw):
            parsed = _parse_virsci_idea_blob(item)
            if parsed.get("Title") or parsed.get("Idea") or parsed.get("Experiment"):
                return parsed
        return {}
    if isinstance(raw, dict):
        if any(raw.get(key) for key in _VIRSCI_IDEA_KEYS):
            return {key: raw.get(key) for key in _VIRSCI_IDEA_KEYS if raw.get(key) is not None}
        nested = raw.get("idea")
        if nested is not None and nested is not raw:
            return _parse_virsci_idea_blob(nested)
        return {}
    if isinstance(raw, str):
        parsed = _json_from_text(raw)
        if parsed:
            inner = _parse_virsci_idea_blob(parsed)
            if inner:
                return inner
        split = _split_labeled_fields(raw, _VIRSCI_IDEA_KEYS)
        return split
    return {}


def _parse_virsci_abstract(raw: Any) -> tuple[str, str]:
    if isinstance(raw, dict):
        return _as_text(raw.get("Title")), _as_text(raw.get("Abstract"))
    text = _as_text(raw)
    parsed = _json_from_text(text)
    if parsed:
        title = _as_text(parsed.get("Title"))
        abstract = _as_text(parsed.get("Abstract"))
        if title or abstract:
            return title, abstract
    split = _split_labeled_fields(text, ("Title", "Abstract"))
    return _as_text(split.get("Title")), _as_text(split.get("Abstract") or text)


def idea_from_virtualscientists(raw: dict[str, Any], topic: Topic) -> ResearchIdea:
    """Map one Virtual-Scientists team_info / idea blob onto ``ResearchIdea``.

    VirSci emits a team discussion trace: selected topic, idea JSON (Idea /
    Title / Experiment plus 1-10 ratings), and an abstract. The topic budget
    fills ``resource_plan`` the same way as for the other generators.
    """
    extra = raw.get("extra") if isinstance(raw.get("extra"), dict) else {}
    inner = extra.get("virtual_scientists") if isinstance(extra.get("virtual_scientists"), dict) else {}
    src = inner if inner.get("Idea") or inner.get("idea") or inner.get("Title") else raw

    parsed_idea = _parse_virsci_idea_blob(src.get("idea") if src.get("idea") is not None else src)
    abs_title, abstract = _parse_virsci_abstract(src.get("abstract") or raw.get("abstract"))
    title = (
        _as_text(raw.get("title"))
        or _as_text(inner.get("Title"))
        or _as_text(parsed_idea.get("Title"))
        or abs_title
        or _title_from_text(_as_text(parsed_idea.get("Idea")))
        or "Untitled Virtual-Scientists idea"
    )
    name = _as_text(inner.get("Name") or src.get("Name") or raw.get("Name"))
    if not name:
        name = _slug(title)[:60].strip("_") or "virsci_idea"

    idea_text = _as_text(parsed_idea.get("Idea"))
    experiment = _as_text(parsed_idea.get("Experiment")) or _as_text(src.get("experiment") or raw.get("experiments"))
    selected_topic = _as_text(src.get("topic") or raw.get("topic"))
    related_titles = src.get("related_titles") or raw.get("related_titles") or []
    if not isinstance(related_titles, list):
        related_titles = [related_titles] if related_titles else []
    related_titles = [_as_text(item) for item in related_titles if _as_text(item)]
    related_work = _as_text(raw.get("related_work")) or "; ".join(related_titles) or selected_topic
    limitations = _as_text(raw.get("limitations") or src.get("review") or src.get("paper_review"))

    compact = {
        "Name": name,
        "Title": title,
        "Idea": idea_text,
        "Experiment": experiment,
        "Clarity": parsed_idea.get("Clarity"),
        "Feasibility": parsed_idea.get("Feasibility"),
        "Novelty": parsed_idea.get("Novelty"),
        "topic": selected_topic,
        "abstract": abstract,
        "teammate": src.get("teammate") or raw.get("teammate"),
        "related_titles": related_titles,
    }
    return ResearchIdea(
        title=title,
        research_question=idea_text or abstract,
        hypothesis=idea_text or abstract,
        problem=idea_text or abstract,
        motivation=selected_topic or idea_text or abstract,
        method=idea_text or abstract,
        experiments=experiment,
        related_work=related_work,
        limitations=limitations,
        resource_plan=_resource_plan_from_topic(topic),
        extra={"generator": "virtual-scientists", "virtual_scientists": compact},
    )


def _is_native(data: dict[str, Any]) -> bool:
    if "ai_scientist_v2" in (data.get("extra") or {}):
        return True
    return "title" in data and any(key in data for key in _NATIVE_KEYS)


def _is_aiscientist(data: dict[str, Any]) -> bool:
    return bool(data.get("Title") or data.get("Name"))


def _is_researchagent(data: dict[str, Any]) -> bool:
    extra = data.get("extra") if isinstance(data.get("extra"), dict) else {}
    if extra.get("generator") == "researchagent" or extra.get("researchagent"):
        return True
    return data.get("problem_rationale") is not None and "experiment" in data


def _is_coi_agent(data: dict[str, Any]) -> bool:
    extra = data.get("extra") if isinstance(data.get("extra"), dict) else {}
    if extra.get("generator") == "coi-agent" or extra.get("coi_agent"):
        return True
    return bool(data.get("idea") and data.get("idea_chain") is not None and "experiment" in data)


def _is_virtualscientists(data: dict[str, Any]) -> bool:
    extra = data.get("extra") if isinstance(data.get("extra"), dict) else {}
    if extra.get("generator") == "virtual-scientists" or extra.get("virtual_scientists"):
        return True
    return bool(data.get("teammate") and data.get("idea") is not None and "abstract" in data)


def _dedup_key(idea: ResearchIdea) -> str:
    extra = idea.extra or {}
    aisci = (extra.get("ai_scientist_v2") or {}).get("Name")
    ra = (extra.get("researchagent") or {}).get("Name")
    coi = (extra.get("coi_agent") or {}).get("Name")
    virsci = (extra.get("virtual_scientists") or {}).get("Name")
    return str(aisci or ra or coi or virsci or idea.idea_id or idea.title)


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value or uuid.uuid4().hex[:8])


def _idea_files(path: Path) -> list[Path]:
    if not path.is_dir():
        return [path]
    return [f for f in sorted(path.glob("*.json")) if not f.name.endswith(".transcript.json")]


def load_ideas(path: str | Path, topic: Topic) -> list[ResearchIdea]:
    """Load ideas from one JSON file or a directory of them, de-duplicated."""
    p = Path(path)
    ideas: list[ResearchIdea] = []
    seen: set[str] = set()

    for file in _idea_files(p):
        data = json.loads(file.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            if _is_native(item):
                idea = ResearchIdea.model_validate(item)
            elif _is_virtualscientists(item):
                idea = idea_from_virtualscientists(item, topic)
            elif _is_aiscientist(item):
                idea = idea_from_aiscientist(item, topic)
            elif _is_researchagent(item):
                idea = idea_from_researchagent(item, topic)
            elif _is_coi_agent(item):
                idea = idea_from_coi_agent(item, topic)
            else:
                continue
            key = _dedup_key(idea)
            if key in seen:
                continue
            seen.add(key)
            idea.topic_id = topic.id
            idea.idea_id = idea.idea_id or f"{topic.id}-{_slug(key)}"
            ideas.append(idea)

    if not ideas:
        raise FileNotFoundError(f"No ideas found in {p}")
    return ideas
