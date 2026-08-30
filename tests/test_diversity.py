import numpy as np
import pytest

from alphaideabench.metrics import diversity_metrics, pairwise_cosine, spearman_correlation


def test_identical_vectors_are_duplicates():
    x = np.ones((4, 8), dtype=np.float64)
    metrics = diversity_metrics(x, taus=[0.99])
    assert metrics["n_pairs"] == 6
    assert metrics["mean_pairwise_similarity"] == pytest.approx(1.0)
    assert metrics["max_pairwise_similarity"] == pytest.approx(1.0)
    assert metrics["duplicate_rate"]["0.99"] == pytest.approx(1.0)


def test_orthogonal_pair_has_zero_similarity():
    x = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float64)
    sim = pairwise_cosine(x)
    assert sim[0, 1] == pytest.approx(0.0)
    metrics = diversity_metrics(x, taus=[0.85])
    assert metrics["mean_pairwise_similarity"] == pytest.approx(0.0)
    assert metrics["duplicate_rate"]["0.85"] == pytest.approx(0.0)


def test_max_sim_not_hidden_by_mean():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(6, 16))
    x[1] = x[0]
    metrics = diversity_metrics(x, taus=[0.95])
    assert metrics["max_pairwise_similarity"] == pytest.approx(1.0)
    assert metrics["mean_pairwise_similarity"] < 0.95
    assert metrics["duplicate_rate"]["0.95"] > 0


def test_spearman_perfect_and_inverse():
    x = [1, 2, 3, 4, 5]
    assert spearman_correlation(x, x) == pytest.approx(1.0)
    assert spearman_correlation(x, list(reversed(x))) == pytest.approx(-1.0)
