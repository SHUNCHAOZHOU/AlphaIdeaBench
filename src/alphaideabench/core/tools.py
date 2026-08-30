from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, get_args, get_origin, get_type_hints

from alphaideabench.domain.idea import ResearchIdea
from alphaideabench.domain.topic import Topic


@dataclass
class RunContext:
    """Per-run state injected into tools. Hidden from the LLM schema."""

    topic: Topic | None = None
    idea: ResearchIdea | None = None
    idea_text: str | None = None
    dimension_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., str]
    inject_ctx: bool = False

    def openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def execute(self, arguments: dict[str, Any], ctx: RunContext) -> str:
        kwargs = dict(arguments)
        if self.inject_ctx:
            kwargs["ctx"] = ctx
        try:
            result = self.handler(**kwargs)
        except TypeError as exc:
            return f"Tool `{self.name}` argument error: {exc}"
        except Exception as exc:  # noqa: BLE001
            return f"Tool `{self.name}` failed: {exc}"
        if result is None:
            return ""
        return result if isinstance(result, str) else str(result)


def _json_type(annotation: Any) -> dict[str, Any]:
    origin = get_origin(annotation)
    if origin is list:
        return {"type": "array", "items": _json_type(get_args(annotation)[0] if get_args(annotation) else str)}
    if annotation in {str, None}:
        return {"type": "string"}
    if annotation is int:
        return {"type": "integer"}
    if annotation is float:
        return {"type": "number"}
    if annotation is bool:
        return {"type": "boolean"}
    return {"type": "string"}


def tool_from_callable(fn: Callable[..., Any], name: str | None = None) -> Tool:
    hints = get_type_hints(fn)
    sig = inspect.signature(fn)
    inject_ctx = False
    properties: dict[str, Any] = {}
    required: list[str] = []
    for pname, param in sig.parameters.items():
        if pname in {"ctx", "context"} or hints.get(pname) is RunContext:
            inject_ctx = True
            continue
        schema = _json_type(hints.get(pname, str))
        if param.default is not inspect.Parameter.empty:
            schema["default"] = param.default
        else:
            required.append(pname)
        properties[pname] = schema
    description = (inspect.getdoc(fn) or "").strip() or f"Tool `{name or fn.__name__}`."
    parameters = {"type": "object", "properties": properties, "additionalProperties": False}
    if required:
        parameters["required"] = required
    return Tool(
        name=name or fn.__name__,
        description=description.split("\n")[0],
        parameters=parameters,
        handler=fn,
        inject_ctx=inject_ctx,
    )


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, fn: Callable[..., Any] | None = None, *, name: str | None = None):
        def deco(func: Callable[..., Any]) -> Callable[..., Any]:
            t = tool_from_callable(func, name=name)
            self._tools[t.name] = t
            return func

        if fn is not None:
            return deco(fn)
        return deco

    def add(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name]

    def names(self) -> list[str]:
        return list(self._tools)

    def subset(self, names: list[str]) -> "ToolRegistry":
        sub = ToolRegistry()
        for name in names:
            sub.add(self.get(name))
        return sub

    def openai_schemas(self) -> list[dict[str, Any]]:
        return [t.openai_schema() for t in self._tools.values()]

    def execute(self, name: str, arguments: dict[str, Any], ctx: RunContext) -> str:
        if name not in self._tools:
            unwrapped = _unwrap_nested_call(name, arguments)
            if unwrapped and unwrapped[0] in self._tools:
                inner_name, inner_args = unwrapped
                return self._tools[inner_name].execute(inner_args, ctx)
            # Never raise: a hallucinated tool name would otherwise abort a run
            # that is many dimensions deep. Tell the model and let it retry.
            return (
                f"Unknown tool `{name}`. Available tools: {', '.join(self.names())}. "
                "Call one of these by name, or answer with the required JSON directly."
            )
        return self._tools[name].execute(arguments, ctx)


_ENVELOPE_NAMES = {"invoke", "tool_call", "function_call", "call_tool", "multi_tool_use.parallel"}
_INNER_NAME_KEYS = ("name", "tool_name", "tool", "function", "recipient_name")
_INNER_ARG_KEYS = ("arguments", "parameters", "params", "input", "args")


def _unwrap_nested_call(name: str, arguments: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    """Recover the real call from an XML-style envelope.

    Some models wrap the call as `invoke(name="load_topic", parameters={...})`
    instead of calling `load_topic` directly.
    """
    if name not in _ENVELOPE_NAMES or not isinstance(arguments, dict):
        return None
    inner_name = next(
        (arguments[key] for key in _INNER_NAME_KEYS if isinstance(arguments.get(key), str)), None
    )
    if not inner_name:
        return None
    inner_args = next(
        (arguments[key] for key in _INNER_ARG_KEYS if isinstance(arguments.get(key), dict)), {}
    )
    return inner_name, inner_args


GLOBAL_REGISTRY = ToolRegistry()


def tool(fn: Callable[..., Any] | None = None, *, name: str | None = None):
    """Register a function as an agent tool on the global registry."""
    return GLOBAL_REGISTRY.register(fn, name=name)
