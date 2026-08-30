from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from alphaideabench.core.jsonutil import extract_json_object
from alphaideabench.core.llm import LLMBackend
from alphaideabench.core.tools import RunContext, ToolRegistry
from alphaideabench.core.types import ChatResult, Message


class AgentError(RuntimeError):
    pass


@dataclass
class AgentResult:
    content: str
    parsed: dict[str, Any] | None
    messages: list[Message]
    usage: dict[str, int] = field(default_factory=dict)
    tool_trace: list[dict[str, Any]] = field(default_factory=list)
    rounds: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "parsed": self.parsed,
            "messages": [m.to_dict() for m in self.messages],
            "usage": self.usage,
            "tool_trace": self.tool_trace,
            "rounds": self.rounds,
        }


class Agent:
    """Generic tool-calling agent. Specialize by swapping prompt + tools."""

    def __init__(
        self,
        name: str,
        backend: LLMBackend,
        system_prompt: str,
        tools: ToolRegistry | None = None,
        ctx: RunContext | None = None,
        temperature: float = 0.4,
        max_rounds: int = 8,
        require_json: bool = True,
        json_mode: bool = False,
        model: str | None = None,
    ) -> None:
        self.name = name
        self.backend = backend
        self.system_prompt = system_prompt
        self.tools = tools or ToolRegistry()
        self.ctx = ctx or RunContext()
        self.temperature = temperature
        self.max_rounds = max_rounds
        self.require_json = require_json
        self.json_mode = json_mode
        self.model = model

    def run(self, user_message: str) -> AgentResult:
        messages = [
            Message(role="system", content=self.system_prompt),
            Message(role="user", content=user_message),
        ]
        usage_acc = {"prompt_tokens": 0, "completion_tokens": 0}
        tool_trace: list[dict[str, Any]] = []
        schemas = self.tools.openai_schemas() or None
        repair_used = False

        for round_i in range(1, self.max_rounds + 1):
            result: ChatResult = self.backend.chat(
                messages,
                tools=schemas,
                temperature=self.temperature,
                json_mode=self.json_mode and not schemas,
                model=self.model,
            )
            for key in usage_acc:
                usage_acc[key] += int(result.usage.get(key, 0))

            if result.tool_calls:
                messages.append(
                    Message(role="assistant", content=result.content or "", tool_calls=result.tool_calls)
                )
                for tc in result.tool_calls:
                    output = self.tools.execute(tc.name, tc.arguments, self.ctx)
                    truncated = output if len(output) <= 20000 else output[:20000] + "\n...[truncated]"
                    tool_trace.append({"name": tc.name, "arguments": tc.arguments, "output": truncated})
                    messages.append(
                        Message(role="tool", content=truncated, tool_call_id=tc.id, name=tc.name)
                    )
                continue

            content = (result.content or "").strip()
            parsed = extract_json_object(content)
            if parsed is None and self.require_json and not repair_used:
                messages.append(Message(role="assistant", content=content))
                messages.append(
                    Message(
                        role="user",
                        content=(
                            "Your last reply was not valid JSON. Output a single JSON object only, "
                            "with no markdown fences and no extra commentary."
                        ),
                    )
                )
                repair_used = True
                continue
            if parsed is None and self.require_json:
                raise AgentError(f"Agent `{self.name}` did not return valid JSON after {round_i} rounds.")
            return AgentResult(
                content=content,
                parsed=parsed,
                messages=messages + [Message(role="assistant", content=content)],
                usage=usage_acc,
                tool_trace=tool_trace,
                rounds=round_i,
            )

        raise AgentError(f"Agent `{self.name}` exceeded max_rounds={self.max_rounds}.")
