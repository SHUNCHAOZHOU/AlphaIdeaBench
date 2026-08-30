#!/usr/bin/env python
"""Run AI-Scientist-v2 ideation on an AlphaIdeaBench topic, through OpenRouter.

The baseline is used as-is; nothing under baseline/ is modified. Two details
make that possible:

- ``ai_scientist.llm.create_client`` only knows a fixed model list and hardwires
  a base_url per provider, so we build the OpenAI-compatible client ourselves
  and call ``generate_temp_free_idea`` directly.
- ``get_response_from_llm`` dispatches on the model name. The ``ollama/`` branch
  is the only one that forwards an arbitrary slug unchanged (it just strips the
  prefix), so ``ollama/<openrouter-slug>`` is how we reach OpenRouter models.

The workshop description is rendered from the topic, so the ideation agent and
the AlphaIdeaBench judges see the same Budget.

Example:
    python scripts/run_aiscientist_ideation.py \
        --topic data/topics/icbinb.md \
        --model deepseek/deepseek-v4-flash-0731 \
        --n 1 --reflections 3
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import openai
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE = REPO_ROOT / "baseline/AI-Scientist-v2"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


_FENCE_LINE = re.compile(r"^[ \t]*```[a-zA-Z0-9_-]*[ \t]*$", re.MULTILINE)


def _reasoning_of(message) -> str:
    reasoning = getattr(message, "reasoning", None)
    if not reasoning:
        extra = getattr(message, "model_extra", None) or {}
        reasoning = extra.get("reasoning") or extra.get("reasoning_content")
    return reasoning or ""


class _Completions:
    """Keep the baseline's `ACTION:` / `ARGUMENTS:` protocol intact.

    Reasoning models on OpenRouter (DeepSeek in particular) split the answer:
    `ACTION:` ends up in `reasoning` and `content` starts mid-block, or
    `content` is empty outright. The baseline reads `content` only and then
    fails its regex parse. So ask OpenRouter to drop reasoning tokens from the
    response, and if a model still splits the answer, glue the two halves back
    together before the baseline sees them.

    Markdown fences get stripped too: the baseline runs `json.loads` on
    everything after `ARGUMENTS:`, so a wrapping ``` block breaks FinalizeIdea.
    """

    def __init__(self, inner) -> None:
        self._inner = inner

    def create(self, **kwargs):
        extra_body = dict(kwargs.pop("extra_body", None) or {})
        extra_body.setdefault("reasoning", {"exclude": True})
        response = self._inner.create(extra_body=extra_body, **kwargs)
        for choice in getattr(response, "choices", []) or []:
            message = getattr(choice, "message", None)
            if message is None:
                continue
            content = message.content or ""
            if "ACTION:" not in content:
                reasoning = _reasoning_of(message)
                if reasoning:
                    content = f"{reasoning}\n{content}".strip()
            message.content = _FENCE_LINE.sub("", content).strip()
        return response


class _Chat:
    def __init__(self, inner) -> None:
        self.completions = _Completions(inner.completions)


class MergeReasoningClient:
    """Thin proxy so the baseline stays untouched."""

    def __init__(self, inner) -> None:
        self._inner = inner
        self.chat = _Chat(inner.chat)

    def __getattr__(self, name):
        return getattr(self._inner, name)


def topic_to_workshop(topic) -> str:
    """Render an AlphaIdeaBench topic as an AI-Scientist-v2 workshop description."""
    keywords = ", ".join(topic.keywords) if topic.keywords else topic.field
    return (
        f"# Title: {topic.title}\n\n"
        f"## Keywords\n{keywords}\n\n"
        f"## TL;DR\nPropose research ideas under this topic. "
        f"Every experiment must fit the budget below.\n\n"
        f"{topic.budget.to_markdown()}\n\n"
        f"## Abstract\n{topic.body.strip()}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--topic", required=True, help="AlphaIdeaBench 课题 markdown")
    parser.add_argument(
        "--model",
        default=os.getenv("IDEATION_MODEL") or os.getenv("model") or "deepseek/deepseek-v4-flash-0731",
        help="OpenRouter slug，例如 deepseek/deepseek-v4-flash-0731",
    )
    parser.add_argument("--n", type=int, default=1, help="生成几条 idea")
    parser.add_argument("--reflections", type=int, default=3, help="每条 idea 的 reflection 轮数")
    parser.add_argument("--out", help="输出 JSON，默认 outputs/aiscientist/<topic_id>.json")
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE), help="AI-Scientist-v2 根目录")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=8192,
        help="覆盖 baseline 的 MAX_NUM_TOKENS（默认 4096，对推理模型不够）",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="沿用输出文件里已有的 idea 作为 previous proposals（默认从零开始）",
    )
    parser.add_argument("--print-workshop", action="store_true", help="只打印 workshop 描述后退出")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    load_dotenv()

    # The baseline reads S2_API_KEY; this repo's .env uses SEMANTIC_SCHOLAR_API_KEY.
    # Must happen before importing the baseline: it instantiates the search tool at
    # import time and caches the key. Without it, literature search hits the anonymous
    # rate limit and backoff retries forever (no max_tries upstream).
    if not os.getenv("S2_API_KEY") and os.getenv("SEMANTIC_SCHOLAR_API_KEY"):
        os.environ["S2_API_KEY"] = os.environ["SEMANTIC_SCHOLAR_API_KEY"]
    if not os.getenv("S2_API_KEY"):
        print("[ideation] warning: no S2_API_KEY / SEMANTIC_SCHOLAR_API_KEY; "
              "literature search will be rate-limited and may retry for a long time.")

    from alphaideabench.domain.topic import Topic

    topic = Topic.from_markdown(args.topic)
    workshop = topic_to_workshop(topic)
    if args.print_workshop:
        print(workshop)
        return 0

    baseline = Path(args.baseline).resolve()
    if not (baseline / "ai_scientist").is_dir():
        raise SystemExit(f"AI-Scientist-v2 not found at {baseline}")
    sys.path.insert(0, str(baseline))

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is not set (put it in .env).")

    import ai_scientist.llm as llm_mod
    from ai_scientist.perform_ideation_temp_free import generate_temp_free_idea

    if args.max_tokens != llm_mod.MAX_NUM_TOKENS:
        print(f"[ideation] MAX_NUM_TOKENS {llm_mod.MAX_NUM_TOKENS} -> {args.max_tokens}")
        llm_mod.MAX_NUM_TOKENS = args.max_tokens

    out = Path(args.out) if args.out else REPO_ROOT / "outputs" / "aiscientist" / f"{topic.id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    client = MergeReasoningClient(
        openai.OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL, timeout=600, max_retries=4)
    )

    print(f"[ideation] topic={topic.id} model={args.model} n={args.n} out={out}")
    ideas = generate_temp_free_idea(
        idea_fname=str(out),
        client=client,
        model=f"ollama/{args.model}",
        workshop_description=workshop,
        max_num_generations=args.n,
        num_reflections=args.reflections,
        reload_ideas=args.append,
    )
    if not ideas:
        print("[ideation] no idea was finalized; nothing written.")
        return 1
    print(f"[ideation] wrote {len(ideas)} idea(s) to {out}")
    print("Next:")
    print(f"  alphaideabench judge --topic {args.topic} --ideas {out} --repeats 1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
