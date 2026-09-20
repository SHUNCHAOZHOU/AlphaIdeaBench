import pytest

from alphaideabench.domain.dimensions import ChecklistItem, DimensionSpec, load_catalog


def test_twelve_dimensions_loaded():
    catalog = load_catalog()
    ordered = catalog.ordered()
    assert len(ordered) == 12
    assert ordered[0].id == "context_grounding"
    assert ordered[-1].id == "verification_feasibility"
    assert "budget_feasibility" in catalog.dimensions
    assert "research_readiness" not in catalog.dimensions
    assert "readiness" not in catalog.groups
    assert catalog.groups["feasibility"].dimensions[-1] == "verification_feasibility"
    rubric = catalog.dimensions["budget_feasibility"].rubric_markdown()
    assert "Is GPU/CPU capacity sufficient" in rubric


def test_every_checklist_item_declares_a_known_polarity():
    """Polarity must be explicit so the judge never has to infer it."""
    for spec in load_catalog().ordered():
        assert spec.checklist, f"{spec.id} has no checklist"
        for item in spec.checklist:
            assert item.polarity in ("positive", "negative"), (spec.id, item.text)


def test_rubric_markdown_exposes_polarity_to_the_judge():
    rubric = load_catalog().dimensions["context_grounding"].rubric_markdown()
    assert "Is the idea relevant to the given research direction  [yes = good]" in rubric
    assert "Are there factual errors about the papers  [yes = problem]" in rubric


def test_no_open_ended_checklist_items_remain():
    """``What ...`` style items cannot be answered with yes/no/partial/n-a."""
    for spec in load_catalog().ordered():
        for item in spec.checklist:
            first = item.text.split()[0].lower()
            assert first not in {"what", "which", "how", "why"}, (spec.id, item.text)


def test_budget_is_only_scored_by_budget_feasibility():
    """Avoid double-penalising one budget overrun across several dimensions."""
    catalog = load_catalog()
    offenders = {
        spec.id
        for spec in catalog.ordered()
        if spec.id != "budget_feasibility"
        for item in spec.checklist
        if "budget" in item.text.lower()
    }
    assert not offenders, f"budget leaked into {offenders}"


def test_legacy_plain_string_checklist_still_loads():
    spec = DimensionSpec(
        id="d",
        index=1,
        group="validity",
        name="D",
        question="q",
        scores={"1": "bad", "5": "good"},
        checklist=["Is there a baseline"],
    )
    assert spec.checklist == [ChecklistItem(text="Is there a baseline")]
    assert spec.checklist_texts == ["Is there a baseline"]
    assert spec.checklist[0].polarity == "positive"


def test_unknown_polarity_is_rejected():
    with pytest.raises(ValueError):
        ChecklistItem(text="x", polarity="sideways")
