import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

AISCIENTIST_BASELINE = ROOT / "baseline/AI-Scientist-v2/ai_scientist/ideas"


@pytest.fixture(autouse=True)
def _set_root(monkeypatch):
    monkeypatch.setenv("ALPHAIDEABENCH_ROOT", str(ROOT))
    monkeypatch.chdir(ROOT)


@pytest.fixture
def aiscientist_ideas_dir(tmp_path):
    """A directory of AI-Scientist-v2 style ideas, with one duplicated Name."""
    first = [
        {
            "Name": "compositional_regularization_nn",
            "Title": "Compositional regularization for seq2seq models",
            "Short Hypothesis": "A compositional penalty improves systematic generalization.",
            "Related Work": "SCAN and COGS studies.",
            "Abstract": "We add a compositional regularization term.",
            "Experiments": ["Train on SCAN", "Ablate the penalty weight"],
            "Risk Factors and Limitations": ["The penalty may be hard to tune."],
        },
        {
            "Name": "interpretability_failure_modes",
            "Title": "When interpretability methods fail",
            "Short Hypothesis": "Saliency methods disagree under distribution shift.",
            "Related Work": "Grad-CAM, integrated gradients.",
            "Abstract": "We audit interpretability methods.",
            "Experiments": ["Apply Grad-CAM and IG", "Compare agreement"],
            "Risk Factors and Limitations": ["Ground truth explanations are unclear."],
        },
    ]
    second = [
        dict(first[0]),
        {
            "Name": "real_world_pest_detection",
            "Title": "Pest detection in the field",
            "Short Hypothesis": "Detectors degrade outside curated datasets.",
            "Related Work": "YOLO family.",
            "Abstract": "We study real-world pest detection.",
            "Experiments": ["Collect field images", "Report mAP"],
            "Risk Factors and Limitations": ["Field data is expensive."],
        },
    ]
    ideas_dir = tmp_path / "aiscientist_ideas"
    ideas_dir.mkdir()
    (ideas_dir / "batch_a.json").write_text(json.dumps(first), encoding="utf-8")
    (ideas_dir / "batch_b.json").write_text(json.dumps(second), encoding="utf-8")
    return ideas_dir
