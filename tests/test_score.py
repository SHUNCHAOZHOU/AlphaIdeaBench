from alphaideabench.domain.dimensions import load_catalog
from alphaideabench.domain.score import DimensionJudgment, normalise_judgment


def _expected(dimension_id: str = "verification_feasibility") -> list[str]:
    return load_catalog().dimensions[dimension_id].checklist_texts


def _notes(items: list[str], judgment: str = "yes") -> list[dict[str, str]]:
    return [{"item": item, "judgment": judgment, "evidence": "ev"} for item in items]


def test_normalise_judgment_accepts_the_four_labels():
    for label in ("yes", "no", "partial", "n/a"):
        assert normalise_judgment(label) == (label, False)
    assert normalise_judgment("NO") == ("no", False)


def test_normalise_judgment_repairs_common_aliases():
    assert normalise_judgment("Y") == ("yes", True)
    assert normalise_judgment("not applicable") == ("n/a", True)
    assert normalise_judgment("partially") == ("partial", True)


def test_normalise_judgment_drops_unknown_labels():
    assert normalise_judgment("resource") == ("", True)
    assert normalise_judgment("banana") == ("", True)


def test_complete_valid_checklist_produces_no_flags():
    expected = _expected()
    judgment = DimensionJudgment.from_llm(
        {"score": 4, "checklist_notes": _notes(expected)},
        "verification_feasibility",
        expected_checklist=expected,
    )
    assert judgment.flags == []
    assert judgment.missing_checklist_items == []


def test_invalid_label_is_flagged_and_not_silently_kept():
    """Regression: a judge once answered 'resource' and it reached the output."""
    expected = _expected()
    notes = _notes(expected)
    notes[-1]["judgment"] = "resource"
    judgment = DimensionJudgment.from_llm(
        {"score": 3, "checklist_notes": notes},
        "verification_feasibility",
        expected_checklist=expected,
    )
    assert "checklist_label_invalid" in judgment.flags
    assert judgment.checklist_notes[-1].judgment == ""


def test_missing_checklist_items_are_flagged_and_listed():
    expected = _expected()
    judgment = DimensionJudgment.from_llm(
        {"score": 4, "checklist_notes": _notes(expected[:5])},
        "verification_feasibility",
        expected_checklist=expected,
    )
    assert "checklist_incomplete" in judgment.flags
    assert judgment.missing_checklist_items == expected[5:]


def test_item_matching_tolerates_whitespace_case_and_punctuation():
    expected = _expected()
    notes = _notes([f"  {item.upper()}?  " for item in expected])
    judgment = DimensionJudgment.from_llm(
        {"score": 4, "checklist_notes": notes},
        "verification_feasibility",
        expected_checklist=expected,
    )
    assert judgment.missing_checklist_items == []
    assert "checklist_incomplete" not in judgment.flags


def test_verbatim_copy_including_polarity_tag_is_accepted():
    """Regression: judges copy the whole rendered line, tag included."""
    expected = _expected()
    notes = _notes([f"{item}  [yes = good]" for item in expected])
    judgment = DimensionJudgment.from_llm(
        {"score": 4, "checklist_notes": notes},
        "verification_feasibility",
        expected_checklist=expected,
    )
    assert judgment.missing_checklist_items == []
    assert "checklist_incomplete" not in judgment.flags
    # The tag must not survive into the stored item text.
    assert judgment.checklist_notes[0].item == expected[0]


def test_small_typo_in_copied_item_still_matches():
    """Regression: a judge wrote 'hyothesis' but answered the right question."""
    expected = _expected("testability")
    notes = _notes(expected)
    notes[0]["item"] = "Is there an explicit hyothesis"
    judgment = DimensionJudgment.from_llm(
        {"score": 4, "checklist_notes": notes},
        "testability",
        expected_checklist=expected,
    )
    assert judgment.missing_checklist_items == []


def test_smart_quotes_in_copied_item_still_match():
    expected = _expected("testability")
    notes = _notes([item.replace('"', "'") for item in expected])
    judgment = DimensionJudgment.from_llm(
        {"score": 4, "checklist_notes": notes},
        "testability",
        expected_checklist=expected,
    )
    assert judgment.missing_checklist_items == []


def test_omitted_checklist_is_still_caught():
    """The real failure mode: model returns reasoning but no checklist at all."""
    expected = _expected("insight_novelty")
    judgment = DimensionJudgment.from_llm(
        {"score": 3, "reasoning": "long prose", "checklist_notes": []},
        "insight_novelty",
        expected_checklist=expected,
    )
    assert "checklist_incomplete" in judgment.flags
    assert judgment.missing_checklist_items == expected


def test_blank_item_text_does_not_satisfy_coverage():
    """A truncated item must not be credited to some expected question."""
    expected = _expected("technical_feasibility")
    notes = _notes(expected[:-1]) + [{"item": "", "judgment": "yes", "evidence": ""}]
    judgment = DimensionJudgment.from_llm(
        {"score": 3, "checklist_notes": notes},
        "technical_feasibility",
        expected_checklist=expected,
    )
    assert judgment.missing_checklist_items == [expected[-1]]


def test_translated_checklist_items_are_flagged():
    expected = _expected("context_grounding")
    judgment = DimensionJudgment.from_llm(
        {"score": 4, "checklist_notes": _notes(["idea 是否与给定研究方向相关"])},
        "context_grounding",
        expected_checklist=expected,
    )
    assert "checklist_language_drift" in judgment.flags


def test_unanswered_item_does_not_count_as_covered():
    expected = _expected()
    notes = _notes(expected)
    notes[0]["judgment"] = ""
    judgment = DimensionJudgment.from_llm(
        {"score": 3, "checklist_notes": notes},
        "verification_feasibility",
        expected_checklist=expected,
    )
    assert judgment.missing_checklist_items == [expected[0]]


def test_score_is_clamped_and_rounded_as_before():
    assert DimensionJudgment.from_llm({"score": 9}, "testability").score == 5
    assert DimensionJudgment.from_llm({"score": 0}, "testability").score == 1
    rounded = DimensionJudgment.from_llm({"score": 3.6}, "testability")
    assert rounded.score == 4
    assert "score_rounded" in rounded.flags
    invalid = DimensionJudgment.from_llm({"score": "abc"}, "testability")
    assert invalid.score == 3
    assert "score_invalid_defaulted" in invalid.flags


def test_no_expected_checklist_means_no_coverage_check():
    judgment = DimensionJudgment.from_llm({"score": 3, "checklist_notes": []}, "testability")
    assert judgment.flags == []
    assert judgment.missing_checklist_items == []
