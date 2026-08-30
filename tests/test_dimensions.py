from alphaideabench.domain.dimensions import load_catalog


def test_thirteen_dimensions_loaded():
    catalog = load_catalog()
    ordered = catalog.ordered()
    assert len(ordered) == 13
    assert ordered[0].id == "context_grounding"
    assert ordered[-1].id == "research_readiness"
    assert "budget_feasibility" in catalog.dimensions
    assert catalog.groups["feasibility"].dimensions[-1] == "verification_feasibility"
    rubric = catalog.dimensions["budget_feasibility"].rubric_markdown()
    assert "Is GPU/CPU capacity sufficient" in rubric
