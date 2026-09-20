from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from alphaideabench.paths import repo_root, resolve_path

_CHAT_MODEL_ENVS = ("OPENROUTER_MODEL", "LLM_MODEL", "MODEL", "model")
_JUDGE_MODEL_ENVS = ("JUDGE_MODEL", "OPENROUTER_JUDGE_MODEL")
_EMBEDDING_MODEL_ENVS = ("EMBEDDING_MODEL", "OPENROUTER_EMBEDDING_MODEL")
_DEEPSEEK_DEFAULT_BASE = "https://api.deepseek.com"
_GEMINI_DEFAULT_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"


def _env_first(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


class LLMSettings(BaseModel):
    provider: str = "openrouter"
    model: str = "google/gemini-2.5-flash"
    api_key_env: str = "OPENROUTER_API_KEY"
    base_url: str = "https://openrouter.ai/api/v1"
    base_url_env: str = "OPENROUTER_BASE_URL"
    timeout_s: float = 120
    max_retries: int = 4
    json_mode: bool = False
    http_referer: str = "https://github.com/alphaideabench"
    app_title: str = "AlphaIdeaBench"


class EmbeddingSettings(BaseModel):
    provider: str = "openrouter"
    model: str = "google/gemini-embedding-2"
    api_key_env: str = "OPENROUTER_API_KEY"
    base_url: str = "https://openrouter.ai/api/v1"
    base_url_env: str = "OPENROUTER_BASE_URL"
    output_dim: int = 768
    task_prefix: str = "task: sentence similarity | query: "
    http_referer: str = "https://github.com/alphaideabench"
    app_title: str = "AlphaIdeaBench"


class AgentSettings(BaseModel):
    name: str
    system_prompt: str
    user_prompt: str
    tools: list[str] = Field(default_factory=list)
    temperature: float = 0.4
    max_rounds: int = 8
    repeats: int = 1
    workers: int = 1
    model: str | None = None


class AgentsSettings(BaseModel):
    judge: AgentSettings


class Track2Settings(BaseModel):
    taus: list[float] = Field(default_factory=lambda: [0.85, 0.90])


class Settings(BaseModel):
    language: str = "en"
    llm: LLMSettings = Field(default_factory=LLMSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    agents: AgentsSettings
    track2: Track2Settings = Field(default_factory=Track2Settings)

    @classmethod
    def load(cls, path: str | Path | None = None) -> Settings:
        load_dotenv(repo_root() / ".env")
        load_dotenv()
        config_path = resolve_path(path or "configs/default.yaml")
        with config_path.open(encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}
        settings = cls.model_validate(data)
        settings._apply_env_overrides()
        settings._config_path = config_path  # type: ignore[attr-defined]
        return settings

    def _apply_env_overrides(self) -> None:
        # dotenv keeps the name as written; accept the unofficial lowercase alias.
        if not os.getenv("DEEPSEEK_API_KEY") and os.getenv("deepseek_api_key"):
            os.environ["DEEPSEEK_API_KEY"] = os.environ["deepseek_api_key"]
        if not os.getenv("GEMINI_API_KEY") and os.getenv("Gemini_API_KEY"):
            os.environ["GEMINI_API_KEY"] = os.environ["Gemini_API_KEY"]

        provider = _env_first("LLM_PROVIDER")
        if provider:
            self.llm.provider = provider
        if self.llm.provider == "deepseek":
            self.llm.api_key_env = _env_first("LLM_API_KEY_ENV") or "DEEPSEEK_API_KEY"
            self.llm.base_url = (
                _env_first("LLM_BASE_URL", "DEEPSEEK_BASE_URL") or _DEEPSEEK_DEFAULT_BASE
            )
            # Stop OPENROUTER_BASE_URL from hijacking a DeepSeek chat client.
            self.llm.base_url_env = "DEEPSEEK_BASE_URL"
        elif self.llm.provider in {"gemini", "google", "gemini_openai"}:
            self.llm.api_key_env = _env_first("LLM_API_KEY_ENV", "GEMINI_API_KEY", "Gemini_API_KEY", "GOOGLE_API_KEY") or "GEMINI_API_KEY"
            self.llm.base_url = (
                _env_first("LLM_BASE_URL", "GEMINI_BASE_URL") or _GEMINI_DEFAULT_BASE
            )
            self.llm.base_url_env = "GEMINI_BASE_URL"
        else:
            key_env = _env_first("LLM_API_KEY_ENV")
            if key_env:
                self.llm.api_key_env = key_env
            base_url = _env_first("LLM_BASE_URL")
            if base_url:
                self.llm.base_url = base_url

        chat_model = _env_first(*_CHAT_MODEL_ENVS)
        if chat_model:
            self.llm.model = chat_model
        judge_model = _env_first(*_JUDGE_MODEL_ENVS)
        if judge_model:
            self.agents.judge.model = judge_model
        embedding_model = _env_first(*_EMBEDDING_MODEL_ENVS)
        if embedding_model:
            self.embedding.model = embedding_model
        workers = _env_first("JUDGE_WORKERS")
        if workers:
            self.agents.judge.workers = max(1, int(workers))

    @property
    def root(self) -> Path:
        return repo_root()
