import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    path = ROOT / "scripts/align_judge_to_human.py"
    spec = importlib.util.spec_from_file_location("align_judge_to_human", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_example_alignment_files():
    mod = _load()
    judge = mod.load_score_map(ROOT / "examples/alignment/judge_scores.json")
    human = mod.load_score_map(ROOT / "examples/alignment/human_scores.json")
    summary = mod.align(judge, human)
    assert summary["n_pairs"] == 6
    assert summary["by_dimension"]["method_novelty"]["mad"] == 0.0
    assert summary["by_dimension"]["scenario_novelty"]["mad"] == 1.0
