import importlib.util
import sys
from pathlib import Path

from alphaideabench.domain.dimensions import load_catalog

ROOT = Path(__file__).resolve().parents[1]


def _load_script():
    path = ROOT / "scripts/map_reviews_to_dimensions.py"
    spec = importlib.util.spec_from_file_location("map_reviews_to_dimensions", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load_script()


def _paper(forum_id: str, n_reviews: int = 3, extra: dict | None = None) -> dict:
    reviews = [
        {
            "review_id": f"r{i}",
            "rating": 4 + (i % 3),
            "confidence": 3,
            "summary": f"summary {i}",
            "strengths": f"strength {i}",
            "weaknesses": f"weakness {i}",
            "review": "",
        }
        for i in range(n_reviews)
    ]
    paper = {
        "title": f"Paper {forum_id}",
        "abstract": "An abstract.",
        "url": f"https://openreview.net/forum?id={forum_id}",
        "reviews": reviews,
    }
    if extra:
        paper.update(extra)
    return paper


def test_paper_id_from_openreview_url():
    assert mod.paper_id_of({"url": "https://openreview.net/forum?id=CRWd9MgCl2"}, 0) == "CRWd9MgCl2"


def test_review_view_withholds_rating_by_default():
    view = mod.review_view(
        {"rating": 8, "confidence": 5, "summary": "ok", "strengths": "s", "weaknesses": "w"},
        "Review 1",
        with_rating=False,
    )
    assert view["rating"] is None
    assert view["confidence"] is None
    assert view["summary"] == "ok"


def test_build_tasks_review_mode_is_one_call_per_review():
    papers = [_paper("abc", n_reviews=4)]
    tasks = mod.build_tasks(papers, mode="review", with_rating=False, max_reviews=2)
    assert len(tasks) == 2
    assert tasks[0].n_reviews_total == 4
    assert len(tasks[0].reviews) == 1
    assert tasks[0].key == "abc::r0"
    assert tasks[0].ratings == [4]


def test_build_tasks_paper_mode_is_one_call_per_paper():
    papers = [_paper("abc", n_reviews=4), _paper("xyz", n_reviews=3)]
    tasks = mod.build_tasks(papers, mode="paper", with_rating=True, max_reviews=None)
    assert len(tasks) == 2
    assert tasks[0].key == "abc::all"
    assert len(tasks[0].reviews) == 4
    assert tasks[0].reviews[0]["rating"] == 4
    assert tasks[1].n_reviews_total == 3


def test_skips_empty_reviews():
    papers = [
        _paper(
            "empty",
            n_reviews=0,
            extra={"reviews": [{"summary": "", "strengths": "", "weaknesses": "", "review": ""}]},
        )
    ]
    assert mod.build_tasks(papers, mode="review", with_rating=False, max_reviews=None) == []


def test_normalize_dimensions_covers_missing_and_invalid():
    ids = ["context_grounding", "method_novelty", "budget_feasibility"]
    payload = {
        "dimensions": [
            {
                "dimension_id": "context_grounding",
                "covered": True,
                "score": 4,
                "evidence": "quoted",
                "reviewer_stance": "positive",
                "reasoning": "ok",
                "confidence": 0.7,
            },
            {"dimension_id": "method_novelty", "covered": False, "score": None},
            {"dimension_id": "invented", "covered": True, "score": 5},
            {"dimension_id": "budget_feasibility", "covered": True, "score": "not-a-number"},
        ]
    }
    mapped, flags = mod.normalize_dimensions(payload, ids)
    assert mapped["context_grounding"]["score"] == 4
    assert mapped["context_grounding"]["evidence"] == ["quoted"]
    assert mapped["method_novelty"]["score"] is None
    assert mapped["budget_feasibility"]["score"] is None
    assert "unknown_dimension:invented" in flags
    assert "score_invalid:budget_feasibility" in flags


def test_aggregate_review_mode_preserves_disagreement():
    catalog = load_catalog()
    records = [
        {
            "paper_id": "p1",
            "title": "T",
            "mode": "review",
            "model": "mock",
            "venue_ratings": [4],
            "venue_confidences": [3],
            "n_reviews_total": 2,
            "dimensions": {
                "method_novelty": {"score": 2, "confidence": 0.5},
                "context_grounding": {"score": None},
            },
            "flags": [],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        },
        {
            "paper_id": "p1",
            "title": "T",
            "mode": "review",
            "model": "mock",
            "venue_ratings": [8],
            "venue_confidences": [4],
            "n_reviews_total": 2,
            "dimensions": {
                "method_novelty": {"score": 4, "confidence": 0.8},
                "context_grounding": {"score": 5, "confidence": 0.6},
            },
            "flags": ["score_rounded:x"],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        },
    ]
    # fill remaining dimensions so aggregate doesn't KeyError
    for rec in records:
        for dim in catalog.ordered():
            rec["dimensions"].setdefault(dim.id, {"score": None})

    papers, summary = mod.aggregate(records, catalog)
    novelty = papers["p1"]["by_dimension"]["method_novelty"]
    assert novelty["n_covered"] == 2
    assert novelty["mean"] == 3.0
    assert novelty["mean_abs_diff"] == 2.0
    assert papers["p1"]["venue_rating_mean"] == 6.0
    assert summary["mode"] == "review"
    assert summary["dimensions"]["method_novelty"]["reviewer_mean_abs_diff"] == 2.0
    assert summary["flags"]["score_rounded"] == 1
