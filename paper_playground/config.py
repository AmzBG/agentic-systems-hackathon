"""Runtime limits and local development configuration."""

from __future__ import annotations

import os
from pathlib import Path


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MAX_API_CALLS = 10
MAX_COMPLETION_TOKENS = 30_000
MAX_RUNTIME_SECONDS = 600.0
SOURCE_MAX_BYTES = 12 * 1024 * 1024
SOURCE_EXCERPT_CHARS = 55_000


def load_local_env(path: Path = Path(".env")) -> None:
    """Load simple KEY=VALUE entries without overriding real environment values."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"").strip("'")
        if key:
            os.environ.setdefault(key, value)

