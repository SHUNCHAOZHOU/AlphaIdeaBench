import json

import pytest

from alphaideabench.domain.topic import Budget, Topic
from alphaideabench.ideas_io import (
    idea_from_aiscientist,
    idea_from_coi_agent,
    idea_from_researchagent,
    idea_from_virtualscientists,
    load_ideas,
)
from tests.conftest import AISCIENTIST_BASELINE


def _topic() -> Topic:
    return Topic(
        id="t1",
        title="Demo",
        budget=Budget(gpu="1x 4090", gpu_hours=40, api_usd=0, notes="public only"),
        body="gap",
    )


def test_map_aiscientist_json_to_research_idea():
    idea = idea_from_aiscientist(
        {
            "Name": "cache_tta",
            "Title": "A cache-based TTA method",
            "Short Hypothesis": "A confidence cache beats TPT under 40 GPU hours.",
            "Related Work": "TPT, TDA",
            "Abstract": "We propose a cache.",
            "Experiments": ["Compare TPT", "Ablate cache size"],
            "Risk Factors and Limitations": ["May fail on ImageNet-A"],
        },
        _topic(),
    )
    assert idea.title.startswith("A cache")
    assert "TPT" in idea.related_work
    assert "Ablate cache size" in idea.experiments
    assert idea.resource_plan.gpu == "1x 4090"
    assert idea.extra["generator"] == "ai-scientist-v2"


def test_load_aiscientist_dir_dedupes_by_name(aiscientist_ideas_dir):
    topic = Topic.from_markdown("examples/topics/icbinb.md")
    ideas = load_ideas(aiscientist_ideas_dir, topic)
    names = [i.extra["ai_scientist_v2"]["Name"] for i in ideas]
    assert names == [
        "compositional_regularization_nn",
        "interpretability_failure_modes",
        "real_world_pest_detection",
    ]
    assert all(i.topic_id == "icbinb" for i in ideas)
    assert ideas[0].idea_id == "icbinb-compositional_regularization_nn"
    assert "SCAN" in ideas[0].experiments


def test_load_native_research_idea(tmp_path):
    payload = {
        "idea_id": "custom-01",
        "title": "Native idea",
        "research_question": "Does it hold?",
        "problem": "A gap.",
        "method": "An adapter.",
        "experiments": "One baseline, one ablation.",
        "resource_plan": {"gpu": "1x A100", "estimated_gpu_hours": 12},
    }
    (tmp_path / "idea.json").write_text(json.dumps(payload), encoding="utf-8")
    ideas = load_ideas(tmp_path / "idea.json", _topic())
    assert len(ideas) == 1
    assert ideas[0].idea_id == "custom-01"
    assert ideas[0].topic_id == "t1"
    assert ideas[0].method == "An adapter."
    assert ideas[0].resource_plan.estimated_gpu_hours == 12


def test_load_ideas_skips_transcripts_and_requires_ideas(tmp_path):
    (tmp_path / "x.transcript.json").write_text(json.dumps({"Title": "T"}), encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        load_ideas(tmp_path, _topic())


def test_load_ideas_accepts_json_list(tmp_path):
    payload = [
        {"Name": "a", "Title": "Idea A", "Abstract": "x"},
        {"Name": "a", "Title": "Idea A duplicate", "Abstract": "x"},
        {"Name": "b", "Title": "Idea B", "Abstract": "y"},
    ]
    (tmp_path / "batch.json").write_text(json.dumps(payload), encoding="utf-8")
    ideas = load_ideas(tmp_path, _topic())
    assert [i.idea_id for i in ideas] == ["t1-a", "t1-b"]


def test_map_researchagent_context_to_research_idea():
    idea = idea_from_researchagent(
        {
            "paper": {
                "title": "ICBINB workshop",
                "abstract": "Negative results in applied deep learning.",
            },
            "problem": "Does label aggregation actually help lung nodule segmentation?",
            "problem_rationale": "Consensus labels are assumed better, but that is untested.",
            "method": "Train U-Net on each annotator versus STAPLE.",
            "method_rationale": "Keep the architecture fixed so the label source is the only factor.",
            "experiment": "Compare Dice and ECE on LIDC-IDRI within 200 GPU hours.",
            "experiment_rationale": "Public data, three seeds, one ablation.",
            "references": [{"title": "LIDC-IDRI", "year": 2011}],
        },
        _topic(),
    )
    assert "label aggregation" in idea.title
    assert idea.problem.startswith("Does label aggregation")
    assert "STAPLE" in idea.method
    assert "LIDC-IDRI" in idea.experiments
    assert "LIDC-IDRI" in idea.related_work
    assert idea.resource_plan.gpu == "1x 4090"
    assert idea.extra["generator"] == "researchagent"
    assert idea.extra["researchagent"]["Name"]


def test_load_researchagent_raw_context(tmp_path):
    payload = {
        "paper": {"title": "Seed", "abstract": "A paper."},
        "problem": "Can a tiny adapter beat the baseline under 40 GPU hours?",
        "problem_rationale": "Large methods ignore the budget.",
        "method": "Freeze the backbone and train a linear head.",
        "method_rationale": "This fits the GPU budget.",
        "experiment": "One public split, three seeds, one ablation.",
        "experiment_rationale": "Must include a baseline.",
        "references": [],
    }
    (tmp_path / "ra.json").write_text(json.dumps(payload), encoding="utf-8")
    ideas = load_ideas(tmp_path / "ra.json", _topic())
    assert len(ideas) == 1
    assert ideas[0].topic_id == "t1"
    assert ideas[0].extra["generator"] == "researchagent"
    assert ideas[0].method.startswith("Freeze the backbone")
    assert ideas[0].idea_id.startswith("t1-")


def test_map_coi_agent_result_to_research_idea():
    idea = idea_from_coi_agent(
        {
            "title": "",
            "idea": (
                "**Title: Failure Modes of Consensus Labels in Segmentation**\n\n"
                "**Origins and Motivation:**\n"
                "Aggregated labels are treated as better ground truth, but that is untested.\n\n"
                "**Novelty and Contributions:**\n"
                "A negative-result study of majority vote versus a single annotator.\n\n"
                "**Methodology:**\n"
                "Train a U-Net on each radiologist versus STAPLE.\n\n"
                "**Challenges and Solutions:**\n"
                "There is no true ground truth; evaluate against each annotator."
            ),
            "idea_chain": (
                "0.Paper:Multi-Annotator Consensus Networks idea:Learn from all annotators.\n \n"
                "1.Paper:LIDC-IDRI idea:Four radiologists label nodules.\n \n"
            ),
            "experiment": "Compare Dice and ECE on LIDC-IDRI within 200 GPU hours.",
            "related_experiments": ["Train U-Net on STAPLE masks."],
            "entities": "STAPLE, U-Net",
            "trend": "From consensus networks to questioning consensus itself.",
            "future": "Study whether aggregation hurts calibration.",
        },
        _topic(),
    )
    assert "Consensus Labels" in idea.title
    assert "Aggregated labels" in idea.problem
    assert "U-Net" in idea.method
    assert "LIDC-IDRI" in idea.experiments
    assert "Multi-Annotator Consensus Networks" in idea.related_work
    assert "no true ground truth" in idea.limitations
    assert idea.resource_plan.gpu == "1x 4090"
    assert idea.extra["generator"] == "coi-agent"
    assert idea.extra["coi_agent"]["Name"]


def test_load_coi_agent_raw_result(tmp_path):
    payload = {
        "idea": "**Title: Hash Fallback Rerank**\n\n**Motivation:**\nSkip PDF parsing.\n",
        "experiment": "Retrieve abstracts only, then generate one idea.",
        "idea_chain": "0.Paper:CoI-Agent idea:Build idea chains from literature.",
        "related_experiments": [],
        "entities": "Semantic Scholar",
        "trend": "From full-text parsing to abstracts.",
    }
    (tmp_path / "coi.json").write_text(json.dumps(payload), encoding="utf-8")
    ideas = load_ideas(tmp_path / "coi.json", _topic())
    assert len(ideas) == 1
    assert ideas[0].topic_id == "t1"
    assert ideas[0].extra["generator"] == "coi-agent"
    assert ideas[0].title.startswith("Hash Fallback")
    assert ideas[0].idea_id.startswith("t1-")


def test_map_virtualscientists_team_info_to_research_idea():
    idea = idea_from_virtualscientists(
        {
            "teammate": ["Scientist0", "Scientist1"],
            "topic": '```json{"Selected Topic": "Label aggregation failure in medical segmentation"}```',
            "idea": (
                "```json\n"
                "{\n"
                '  "Idea": "Aggregating radiologist masks may not beat a single annotator.",\n'
                '  "Title": "The Illusion of Consensus in Nodule Segmentation",\n'
                '  "Experiment": "Train U-Net on LIDC-IDRI with majority vote vs STAPLE vs each annotator.",\n'
                '  "Clarity": 8,\n'
                '  "Feasibility": 7,\n'
                '  "Novelty": 6\n'
                "}\n"
                "```"
            ),
            "abstract": (
                "```json{\n"
                "Title: The Illusion of Consensus in Nodule Segmentation\n\n"
                "Abstract: We test whether consensus labels help U-Net on LIDC-IDRI.\n"
                "} ```"
            ),
            "related_titles": ["LIDC-IDRI", "STAPLE"],
        },
        _topic(),
    )
    assert "Illusion of Consensus" in idea.title
    assert "single annotator" in idea.problem
    assert "LIDC-IDRI" in idea.experiments
    assert "STAPLE" in idea.related_work
    assert idea.resource_plan.gpu == "1x 4090"
    assert idea.extra["generator"] == "virtual-scientists"
    assert idea.extra["virtual_scientists"]["Name"]
    assert idea.extra["virtual_scientists"]["Clarity"] == 8


def test_load_virtualscientists_raw_team_info(tmp_path):
    payload = {
        "teammate": ["Scientist0"],
        "topic": "Negative results in applied deep learning",
        "idea": {
            "Idea": "Test-time augmentation can hurt calibration on shift.",
            "Title": "When TTA Makes Models Worse",
            "Experiment": "Compare TTA on ImageNet-C within 40 GPU hours.",
            "Novelty": 7,
        },
        "abstract": "Title: When TTA Makes Models Worse\nAbstract: We document when TTA fails.",
    }
    (tmp_path / "virsci.json").write_text(json.dumps(payload), encoding="utf-8")
    ideas = load_ideas(tmp_path / "virsci.json", _topic())
    assert len(ideas) == 1
    assert ideas[0].topic_id == "t1"
    assert ideas[0].extra["generator"] == "virtual-scientists"
    assert "TTA" in ideas[0].title
    assert ideas[0].idea_id.startswith("t1-")


@pytest.mark.skipif(
    not AISCIENTIST_BASELINE.is_dir(), reason="AI-Scientist-v2 baseline not checked out"
)
def test_load_real_aiscientist_baseline_ideas():
    topic = Topic.from_markdown("examples/topics/icbinb.md")
    ideas = load_ideas(AISCIENTIST_BASELINE, topic)
    assert ideas
    assert all(i.title and i.topic_id == "icbinb" for i in ideas)
