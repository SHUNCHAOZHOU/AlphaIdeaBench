from __future__ import annotations

from typing import Any

import numpy as np


def pairwise_cosine(embeddings: np.ndarray) -> np.ndarray:
    if embeddings.size == 0:
        return np.zeros((0, 0), dtype=np.float64)
    x = np.asarray(embeddings, dtype=np.float64)
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-12, None)
    x = x / norms
    return x @ x.T


def upper_triangle_values(sim: np.ndarray) -> np.ndarray:
    n = sim.shape[0]
    if n < 2:
        return np.array([], dtype=np.float64)
    iu = np.triu_indices(n, k=1)
    return sim[iu]


def diversity_metrics(embeddings: np.ndarray, taus: list[float] | None = None) -> dict[str, Any]:
    taus = taus or [0.85, 0.90]
    sim = pairwise_cosine(embeddings)
    pairs = upper_triangle_values(sim)
    n = int(sim.shape[0])
    n_pairs = int(pairs.size)
    mean_sim = float(pairs.mean()) if n_pairs else 0.0
    max_sim = float(pairs.max()) if n_pairs else 0.0
    duplicate_rates = {f"{tau:.2f}": float((pairs >= tau).mean()) if n_pairs else 0.0 for tau in taus}
    return {
        "n_ideas": n,
        "n_pairs": n_pairs,
        "mean_pairwise_similarity": mean_sim,
        "max_pairwise_similarity": max_sim,
        "semantic_diversity": 1.0 - mean_sim,
        "duplicate_rate": duplicate_rates,
        "pairwise_similarities": pairs.tolist(),
    }


def spearman_correlation(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("spearman_correlation requires two equal-length sequences with n>=2")
    rx = _rank(np.asarray(x, dtype=np.float64))
    ry = _rank(np.asarray(y, dtype=np.float64))
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    denom = float(np.sqrt((rx**2).sum() * (ry**2).sum()))
    if denom == 0:
        return 0.0
    return float((rx * ry).sum() / denom)


def _rank(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(1, len(values) + 1, dtype=np.float64)
    # average ties
    _, inverse, counts = np.unique(values, return_inverse=True, return_counts=True)
    if np.any(counts > 1):
        sums = np.bincount(inverse, weights=ranks)
        ranks = sums[inverse] / counts[inverse]
    return ranks
