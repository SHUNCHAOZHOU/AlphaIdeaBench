from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    env = os.getenv("ALPHAIDEABENCH_ROOT")
    if env:
        return Path(env).expanduser().resolve()

    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "prompts" / "dimensions.yaml").exists():
            return candidate

    # src/alphaideabench/paths.py → repo root
    fallback = Path(__file__).resolve().parents[2]
    if (fallback / "prompts" / "dimensions.yaml").exists():
        return fallback
    return cwd


def resolve_path(path: str | Path) -> Path:
    p = Path(path).expanduser()
    if p.is_absolute():
        return p
    rooted = repo_root() / p
    if rooted.exists():
        return rooted
    cwd_path = Path.cwd() / p
    if cwd_path.exists():
        return cwd_path
    return rooted
