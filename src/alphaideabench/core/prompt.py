from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, StrictUndefined

from alphaideabench.paths import resolve_path


_ENV = Environment(undefined=StrictUndefined, autoescape=False, keep_trailing_newline=True)


def render_file(path: str | Path, **kwargs: Any) -> str:
    template_path = resolve_path(path)
    text = template_path.read_text(encoding="utf-8")
    return _ENV.from_string(text).render(**kwargs)


def render_string(template: str, **kwargs: Any) -> str:
    return _ENV.from_string(template).render(**kwargs)
