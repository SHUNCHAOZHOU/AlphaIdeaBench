from __future__ import annotations

import json
import os
import re
import threading
import time
import uuid
from typing import Any

from openai import OpenAI

from alphaideabench.core.types import ChatResult, LLMBackend, Message, ToolCallRequest

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
_OPENAI_COMPAT = {"openai", "openai_compat", "gemini_openai", "openrouter", "deepseek", "gemini", "google"}
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


class LLMError(RuntimeError):
    pass


def resolve_base_url(explicit: str | None, env_name: str | None = None) -> str | None:
    if env_name:
        from_env = os.getenv(env_name)
        if from_env:
            return from_env
    return explicit or None


def openrouter_headers(http_referer: str | None = None, app_title: str | None = None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if http_referer:
        headers["HTTP-Referer"] = http_referer
    if app_title:
        headers["X-Title"] = app_title
    return headers


def build_openai_client(
    *,
    api_key: str | None,
    base_url: str | None,
    timeout_s: float = 120,
    default_headers: dict[str, str] | None = None,
) -> OpenAI:
    if not api_key:
        raise LLMError("Missing API key for OpenAI-compatible backend.")
    kwargs: dict[str, Any] = {"api_key": api_key, "timeout": timeout_s}
    if base_url:
        kwargs["base_url"] = base_url
    if default_headers:
        kwargs["default_headers"] = default_headers
    return OpenAI(**kwargs)


def _messages_to_openai(messages: list[Message]) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for msg in messages:
        if msg.role == "tool":
            payload.append(
                {
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id or "",
                    "content": msg.content,
                }
            )
            continue
        item: dict[str, Any] = {"role": msg.role, "content": msg.content}
        if msg.extra:
            item.update(msg.extra)
        if msg.role == "assistant" and msg.tool_calls:
            tc_list = []
            for tc in msg.tool_calls:
                tc_data = {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments, ensure_ascii=False),
                    },
                }
                if tc.extra:
                    tc_data.update(tc.extra)
                tc_list.append(tc_data)
            item["tool_calls"] = tc_list
        payload.append(item)
    return payload


class OpenAIBackend(LLMBackend):
    """OpenAI Chat Completions, including OpenRouter and other compatible endpoints."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_s: float = 120,
        max_retries: int = 4,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        self.model = model
        self.max_retries = max_retries
        self.timeout_s = timeout_s
        self.client = build_openai_client(
            api_key=api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"),
            base_url=base_url,
            timeout_s=timeout_s,
            default_headers=default_headers,
        )

    def chat(
        self,
        messages: list[Message],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.4,
        json_mode: bool = False,
        model: str | None = None,
    ) -> ChatResult:
        kwargs: dict[str, Any] = {
            "model": model or self.model,
            "messages": _messages_to_openai(messages),
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        elif json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        last_error: Exception | None = None
        model_name = kwargs["model"]
        for attempt in range(self.max_retries):
            print(
                f"[llm] calling {model_name} attempt {attempt + 1}/{self.max_retries} "
                f"(timeout={self.timeout_s:.0f}s)",
                flush=True,
            )
            try:
                resp = self.client.chat.completions.create(**kwargs)
                choice = resp.choices[0]
                message = choice.message
                tool_calls: list[ToolCallRequest] = []
                for tc in message.tool_calls or []:
                    try:
                        args = json.loads(tc.function.arguments or "{}")
                    except json.JSONDecodeError:
                        args = {}
                    if not isinstance(args, dict):
                        args = {}
                    tc_extra: dict[str, Any] = {}
                    extra_content = getattr(tc, "extra_content", None)
                    if extra_content:
                        tc_extra["extra_content"] = extra_content
                    tool_calls.append(ToolCallRequest(id=tc.id, name=tc.function.name, arguments=args, extra=tc_extra))
                usage = {}
                if resp.usage:
                    usage = {
                        "prompt_tokens": resp.usage.prompt_tokens or 0,
                        "completion_tokens": resp.usage.completion_tokens or 0,
                    }
                n_chars = len(message.content or "")
                reasoning = _extract_reasoning(message)
                print(
                    f"[llm] ok {model_name} chars={n_chars} "
                    f"reasoning_chars={len(reasoning or '')} tokens={usage}",
                    flush=True,
                )
                extra: dict[str, Any] = {}
                extra_content = getattr(message, "extra_content", None)
                if isinstance(extra_content, dict):
                    extra["extra_content"] = extra_content
                return ChatResult(
                    content=message.content,
                    tool_calls=tool_calls,
                    usage=usage,
                    raw=resp.model_dump() if hasattr(resp, "model_dump") else None,
                    reasoning=reasoning,
                    extra=extra,
                )
            except Exception as exc:  # noqa: BLE001 — retry then surface
                last_error = exc
                wait = min(2**attempt, 8)
                print(f"[llm] failed attempt {attempt + 1}: {exc}\n[llm] retry in {wait}s", flush=True)
                time.sleep(wait)
        raise LLMError(f"LLM request failed after {self.max_retries} retries: {last_error}") from last_error


def _extract_reasoning(message: Any) -> str | None:
    chunks: list[str] = []
    for attr in ("reasoning", "reasoning_content"):
        value = getattr(message, attr, None)
        if value:
            chunks.append(str(value))
    dump = message.model_dump() if hasattr(message, "model_dump") else {}
    if isinstance(dump, dict):
        for key in ("reasoning", "reasoning_content"):
            value = dump.get(key)
            if isinstance(value, str) and value.strip():
                chunks.append(value)
            elif isinstance(value, dict) and value.get("content"):
                chunks.append(str(value["content"]))
    seen: set[str] = set()
    unique: list[str] = []
    for item in chunks:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return "\n".join(unique) or None


_MAPPER_DIMENSION_IDS = (
    "context_grounding",
    "problem_formulation",
    "motivation_method_consistency",
    "testability",
    "problem_novelty",
    "method_novelty",
    "scenario_novelty",
    "insight_novelty",
    "technical_feasibility",
    "data_feasibility",
    "budget_feasibility",
    "verification_feasibility",
)


def _mock_review_mapping(user_blob: str) -> str:
    """A sparse mapping: only a few dimensions covered, matching real reviews."""
    quoted = "the method is a straightforward application"
    covered = {
        "method_novelty": (2, "negative", quoted),
        "problem_formulation": (4, "positive", "the research problem is clearly stated"),
        "verification_feasibility": (3, "mixed", "only evaluated on one small dataset"),
    }
    dimensions = []
    for did in _MAPPER_DIMENSION_IDS:
        if did in covered:
            score, stance, quote = covered[did]
            dimensions.append(
                {
                    "dimension_id": did,
                    "covered": True,
                    "score": score,
                    "evidence": [quote],
                    "reviewer_stance": stance,
                    "reasoning": "Mock mapping: no live LLM was called.",
                    "confidence": 0.2,
                }
            )
        else:
            dimensions.append(
                {
                    "dimension_id": did,
                    "covered": False,
                    "score": None,
                    "evidence": [],
                    "reviewer_stance": "",
                    "reasoning": "",
                    "confidence": None,
                }
            )
    return json.dumps(
        {
            "dimensions": dimensions,
            "disagreement": "Reviewers split on novelty." if "Review 2" in user_blob else "",
            "overall_notes": "Mock review mapping.",
        },
        ensure_ascii=False,
    )


#: Matches the rendered checklist lines, e.g. ``- Is there a baseline  [yes = good]``.
_MOCK_CHECKLIST_RE = re.compile(r"^- (?P<text>.+?)\s+\[yes = (?:good|problem)\]\s*$")


def _mock_checklist_notes(user_blob: str) -> list[dict[str, str]]:
    """Echo the checklist items found in the prompt, so dry-run passes coverage."""
    notes: list[dict[str, str]] = []
    seen: set[str] = set()
    for line in user_blob.splitlines():
        match = _MOCK_CHECKLIST_RE.match(line.strip())
        if not match:
            continue
        text = match.group("text").strip()
        if text in seen:
            continue
        seen.add(text)
        notes.append(
            {"item": text, "judgment": "partial", "evidence": "Mock judge: not evaluated."}
        )
    return notes


class MockBackend(LLMBackend):
    """Deterministic backend for dry-run and tests. Never calls a network."""

    def __init__(self, script: list[ChatResult] | None = None) -> None:
        self.script = list(script or [])
        self.calls: list[list[Message]] = []
        self._lock = threading.Lock()

    def chat(
        self,
        messages: list[Message],
        *,
        tools: list[dict[str, Any]] | None = None,
        temperature: float = 0.4,
        json_mode: bool = False,
        model: str | None = None,
    ) -> ChatResult:
        with self._lock:
            self.calls.append(list(messages))
            scripted = self.script.pop(0) if self.script else None
        if scripted is not None:
            return scripted

        user_blob = " ".join(m.content for m in messages if m.role in {"system", "user"})
        if "existing human peer reviews" in user_blob or "reviewer_stance" in user_blob:
            return ChatResult(content=_mock_review_mapping(user_blob))
        if "dimension_id" in user_blob or "Scoring rubric" in user_blob or "LLM-as-Judge" in user_blob:
            return ChatResult(
                content=json.dumps(
                    {
                        "dimension_id": "mock",
                        "score": 3,
                        "reasoning": "Mock judge: no live LLM was called.",
                        "checklist_notes": _mock_checklist_notes(user_blob),
                        "confidence": 0.2,
                        "flags": ["mock"],
                    },
                    ensure_ascii=False,
                )
            )
        idea_id = uuid.uuid4().hex[:8]
        return ChatResult(
            content=json.dumps(
                {
                    "title": f"Mock idea {idea_id}",
                    "research_question": "Can a constrained prototype validate the core claim?",
                    "hypothesis": "A simplified method will outperform the named baseline on the stated metric.",
                    "problem": "The background identifies a gap that is currently evaluated only at large scale.",
                    "motivation": "Existing methods ignore the stated budget and therefore are not comparable.",
                    "method": "Use a lightweight adapter on a frozen backbone and evaluate on a public split.",
                    "experiments": "Compare against the official baseline with 3 seeds on the public test set.",
                    "baselines": "The standard public baseline described in the topic document.",
                    "success_criteria": "A statistically meaningful gain on the primary metric without exceeding budget.",
                    "related_work": "Follows the papers listed in the topic document.",
                    "limitations": "Results may not transfer to larger models.",
                    "resource_plan": {
                        "gpu": "1x A100 40GB",
                        "estimated_gpu_hours": 20,
                        "estimated_api_usd": 10,
                        "estimated_human_hours": 8,
                        "calendar_weeks": 2,
                        "notes": "Mock resource plan.",
                    },
                },
                ensure_ascii=False,
            )
        )


def build_backend(settings: Any, dry_run: bool = False) -> LLMBackend:
    if dry_run or getattr(settings.llm, "provider", "") == "mock":
        return MockBackend()
    llm = settings.llm
    provider = llm.provider
    if provider in _OPENAI_COMPAT:
        api_key = (
            (os.getenv("OPENROUTER_API_KEY") if provider == "openrouter" else None)
            or os.getenv(llm.api_key_env)
            or (os.getenv("DEEPSEEK_API_KEY") or os.getenv("deepseek_api_key") if provider == "deepseek" else None)
            or (os.getenv("Gemini_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") if provider in {"gemini", "google", "gemini_openai"} else None)
            or os.getenv("OPENROUTER_API_KEY")
        )
        base_url = resolve_base_url(getattr(llm, "base_url", None), getattr(llm, "base_url_env", None))
        if provider == "openrouter":
            if not base_url or "generativelanguage" in base_url or "deepseek.com" in base_url:
                base_url = OPENROUTER_BASE_URL
        elif provider == "deepseek" and not base_url:
            base_url = DEEPSEEK_BASE_URL
        elif provider in {"gemini", "google", "gemini_openai"} and not base_url:
            base_url = GEMINI_BASE_URL
        return OpenAIBackend(
            model=llm.model,
            api_key=api_key,
            base_url=base_url,
            timeout_s=llm.timeout_s,
            max_retries=llm.max_retries,
            default_headers=openrouter_headers(
                getattr(llm, "http_referer", None),
                getattr(llm, "app_title", None),
            )
            or None,
        )
    raise LLMError(f"Unknown LLM provider: {provider}")
