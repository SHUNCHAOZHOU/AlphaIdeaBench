import pytest

from alphaideabench.config import Settings
from alphaideabench.domain.score import DimensionJudgment, RepeatedJudgment
from alphaideabench.domain.topic import Topic
from alphaideabench.ideas_io import load_ideas
from alphaideabench.pipeline import BenchmarkPipeline


def test_repeated_judgment_agreement():
    reps = [
        DimensionJudgment(dimension_id="x", score=4, reasoning="a"),
        DimensionJudgment(dimension_id="x", score=4, reasoning="b"),
        DimensionJudgment(dimension_id="x", score=5, reasoning="c"),
    ]
    agg = RepeatedJudgment.from_repeats("x", reps)
    assert agg.mean == pytest.approx(13 / 3)
    assert agg.exact_agreement == pytest.approx(1 / 3)


def test_judge_ideas_dry_run(tmp_path, aiscientist_ideas_dir):
    settings = Settings.load()
    pipe = BenchmarkPipeline(settings, dry_run=True)
    topic = Topic.from_markdown("examples/topics/icbinb.md")
    ideas = load_ideas(aiscientist_ideas_dir, topic)
    summary = pipe.judge_ideas(topic, ideas, tmp_path, repeats=1)
    assert summary["n_ideas"] == 3
    assert len(summary["track1"]) == 3
    assert summary["track2"]["n_pairs"] == 3
    assert (tmp_path / "icbinb" / "ideas" / "icbinb-compositional_regularization_nn.json").exists()
    assert (tmp_path / "config.json").exists()


def test_judge_ideas_track2_only(tmp_path, aiscientist_ideas_dir):
    settings = Settings.load()
    pipe = BenchmarkPipeline(settings, dry_run=True)
    topic = Topic.from_markdown("examples/topics/icbinb.md")
    ideas = load_ideas(aiscientist_ideas_dir, topic)
    summary = pipe.judge_ideas(topic, ideas, tmp_path, skip_track1=True)
    assert summary["track1"] == []
    assert summary["track2"]["n_pairs"] == 3
    assert "mean_pairwise_similarity" in summary["track2"]


def test_judge_single_dimension_dry_run(tmp_path, aiscientist_ideas_dir):
    settings = Settings.load()
    pipe = BenchmarkPipeline(settings, dry_run=True)
    topic = Topic.from_markdown("examples/topics/icbinb.md")
    ideas = load_ideas(aiscientist_ideas_dir, topic)[:1]
    summary = pipe.judge_ideas(
        topic, ideas, tmp_path, repeats=1, dimension_ids=["data_feasibility"], skip_track2=True
    )
    assert list(summary["track1"][0]["by_dimension"]) == ["data_feasibility"]
    assert summary["track2"] is None


def test_judge_ideas_parallel_dimensions_dry_run(tmp_path, aiscientist_ideas_dir):
    settings = Settings.load()
    pipe = BenchmarkPipeline(settings, dry_run=True)
    topic = Topic.from_markdown("examples/topics/icbinb.md")
    ideas = load_ideas(aiscientist_ideas_dir, topic)[:1]
    summary = pipe.judge_ideas(
        topic, ideas, tmp_path, repeats=1, workers=8, skip_track2=True
    )
    dims = list(summary["track1"][0]["by_dimension"])
    assert len(dims) == 12
    assert dims[0] == "context_grounding"
    assert dims[-1] == "verification_feasibility"
    idea_id = ideas[0].idea_id
    assert (tmp_path / topic.id / "track1" / idea_id / "budget_feasibility" / "repeat_0.json").exists()


def test_default_config_uses_openrouter(monkeypatch):
    # load_dotenv will not overwrite vars that are already set.
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    for name in (
        "LLM_BASE_URL",
        "LLM_API_KEY_ENV",
        "DEEPSEEK_BASE_URL",
        "model",
        "MODEL",
        "LLM_MODEL",
        "OPENROUTER_MODEL",
    ):
        monkeypatch.setenv(name, "")
    settings = Settings.load()
    assert settings.llm.provider == "openrouter"
    assert "openrouter.ai" in settings.llm.base_url
    assert settings.llm.api_key_env == "OPENROUTER_API_KEY"
    assert settings.embedding.provider == "openrouter"
    assert settings.embedding.model == "google/gemini-embedding-2"
    assert settings.agents.judge.tools == [
        "load_topic",
        "load_budget",
        "load_idea",
        "load_rubric",
    ]


def test_env_model_overrides_chat_only(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.setenv("model", "stealth/ox-alpha")
    settings = Settings.load()
    assert settings.llm.model == "stealth/ox-alpha"
    assert settings.embedding.model == "google/gemini-embedding-2"


def test_llm_provider_deepseek_uses_official_api(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("model", "deepseek-v4-flash")
    monkeypatch.setenv("deepseek_api_key", "sk-test")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    settings = Settings.load()
    assert settings.llm.provider == "deepseek"
    assert settings.llm.model == "deepseek-v4-flash"
    assert settings.llm.api_key_env == "DEEPSEEK_API_KEY"
    assert settings.llm.base_url == "https://api.deepseek.com"
    assert settings.llm.base_url_env == "DEEPSEEK_BASE_URL"
    assert settings.embedding.provider == "openrouter"


def test_openrouter_model_env_wins_over_model(monkeypatch):
    monkeypatch.setenv("model", "stealth/ox-alpha")
    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemini-2.5-pro")
    settings = Settings.load()
    assert settings.llm.model == "google/gemini-2.5-pro"


def test_openrouter_embedder_requests_float_encoding():
    from alphaideabench.config import EmbeddingSettings
    from alphaideabench.tracks.track2 import OpenAICompatEmbedder

    settings = EmbeddingSettings(provider="openrouter", model="google/gemini-embedding-2")
    embedder = OpenAICompatEmbedder.__new__(OpenAICompatEmbedder)
    embedder.model = settings.model
    embedder.dim = settings.output_dim
    kwargs = OpenAICompatEmbedder._create_kwargs(embedder, "hello")
    assert kwargs["encoding_format"] == "float"
    assert kwargs["model"] == "google/gemini-embedding-2"
