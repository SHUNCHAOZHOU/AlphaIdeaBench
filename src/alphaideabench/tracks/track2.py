from __future__ import annotations

import hashlib
import os
from typing import Iterable, Protocol

import numpy as np

from alphaideabench.config import EmbeddingSettings
from alphaideabench.core.llm import (
    OPENROUTER_BASE_URL,
    build_openai_client,
    openrouter_headers,
    resolve_base_url,
)
from alphaideabench.metrics import diversity_metrics


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray: ...


class MockEmbedder:
    def __init__(self, dim: int = 768) -> None:
        self.dim = dim

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            seed = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)
            rng = np.random.default_rng(seed)
            vec = rng.normal(size=self.dim)
            vectors.append(vec / (np.linalg.norm(vec) + 1e-12))
        return np.stack(vectors, axis=0)


class GeminiEmbedder:
    """Native Gemini API. Prefer OpenRouter (`google/gemini-embedding-2`) unless you have a Google key."""

    def __init__(self, settings: EmbeddingSettings) -> None:
        from google import genai
        from google.genai import types

        api_key = os.getenv(settings.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing embedding API key in env `{settings.api_key_env}`.")
        self._client = genai.Client(api_key=api_key)
        self._types = types
        self.model = settings.model
        self.dim = settings.output_dim
        self.prefix = settings.task_prefix

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            payload = f"{self.prefix}{text}" if self.prefix else text
            result = self._client.models.embed_content(
                model=self.model,
                contents=payload,
                config=self._types.EmbedContentConfig(output_dimensionality=self.dim),
            )
            values = result.embeddings[0].values
            vec = np.asarray(values, dtype=np.float64)
            vectors.append(vec / (np.linalg.norm(vec) + 1e-12))
        return np.stack(vectors, axis=0)


class OpenAICompatEmbedder:
    """OpenRouter / OpenAI embeddings. Embeds one text at a time for gemini-embedding-2."""

    def __init__(self, settings: EmbeddingSettings) -> None:
        api_key = os.getenv(settings.api_key_env) or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = resolve_base_url(settings.base_url, settings.base_url_env)
        if settings.provider == "openrouter" and not base_url:
            base_url = OPENROUTER_BASE_URL
        self.client = build_openai_client(
            api_key=api_key,
            base_url=base_url,
            timeout_s=120,
            default_headers=openrouter_headers(settings.http_referer, settings.app_title) or None,
        )
        self.model = settings.model
        self.dim = settings.output_dim
        self.prefix = settings.task_prefix
        self._one_at_a_time = "gemini-embedding-2" in settings.model

    def embed(self, texts: list[str]) -> np.ndarray:
        payloads = [f"{self.prefix}{t}" if self.prefix else t for t in texts]
        if self._one_at_a_time:
            vectors = [self._embed_one(p) for p in payloads]
            return np.stack(vectors, axis=0)
        resp = self.client.embeddings.create(**self._create_kwargs(payloads))
        stacked = np.stack([np.asarray(item.embedding, dtype=np.float64) for item in resp.data], axis=0)
        norms = np.clip(np.linalg.norm(stacked, axis=1, keepdims=True), 1e-12, None)
        return stacked / norms

    def _embed_one(self, text: str) -> np.ndarray:
        resp = self.client.embeddings.create(**self._create_kwargs(text))
        vec = np.asarray(resp.data[0].embedding, dtype=np.float64)
        return vec / (np.linalg.norm(vec) + 1e-12)

    def _create_kwargs(self, inputs: str | list[str]) -> dict:
        # OpenAI SDK defaults encoding_format to base64; Gemini via OpenRouter
        # only accepts float (or omitted). Always request float.
        kwargs: dict = {
            "model": self.model,
            "input": inputs,
            "encoding_format": "float",
        }
        if self.dim:
            kwargs["dimensions"] = self.dim
        return kwargs


def build_embedder(settings: EmbeddingSettings, dry_run: bool = False) -> Embedder:
    if dry_run or settings.provider == "mock":
        return MockEmbedder(dim=settings.output_dim)
    if settings.provider == "gemini":
        return GeminiEmbedder(settings)
    if settings.provider in {"openai", "openrouter", "openai_compat"}:
        return OpenAICompatEmbedder(settings)
    raise RuntimeError(f"Unknown embedding provider: {settings.provider}")


def evaluate_diversity(
    idea_texts: Iterable[str],
    embedder: Embedder,
    taus: list[float] | None = None,
) -> dict:
    texts = list(idea_texts)
    embeddings = embedder.embed(texts)
    metrics = diversity_metrics(embeddings, taus=taus)
    metrics["texts"] = texts
    return metrics
