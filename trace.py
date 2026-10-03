"""Append a bounded, sanitized event to the required JSONL trace."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any


_ALLOWED_RESULTS = {"pass", "fail", "skip", "info"}
_BLOCKED_KEYS = re.compile(
    r"(?:api.?key|authorization|credential|password|secret|raw.?prompt|"
    r"raw.?response|chain.?of.?thought|hidden.?reasoning)",
    re.IGNORECASE,
)
_BEARER = re.compile(r"\bBearer\s+\S+", re.IGNORECASE)
_KEY_LIKE = re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b")
_MAX_TEXT = 500
_MAX_LIST = 80


def _clean(value: Any, depth: int = 0) -> Any:
    if depth > 6:
        return "[truncated]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        redacted = _BEARER.sub("Bearer [redacted]", value)
        redacted = _KEY_LIKE.sub("[redacted]", redacted)
        local_key = os.environ.get("OPENROUTER_API_KEY", "")
        if local_key:
            redacted = redacted.replace(local_key, "[redacted]")
        return redacted[:_MAX_TEXT]
    if isinstance(value, (list, tuple)):
        return [_clean(item, depth + 1) for item in value[:_MAX_LIST]]
    if isinstance(value, dict):
        return {
            str(key)[:80]: _clean(item, depth + 1)
            for key, item in value.items()
            if not _BLOCKED_KEYS.search(str(key))
            and str(key).lower() not in {
                "prompt", "messages", "response", "completion", "reasoning",
                "thoughts", "content",
            }
        }
    return str(value)[:_MAX_TEXT]


def write_trace(path: str, event: dict) -> None:
    """Write one complete event; never persist raw prompts or credentials."""
    if not isinstance(event, dict):
        raise TypeError("trace event must be a dictionary")
    result = event.get("result", "info")
    if result not in _ALLOWED_RESULTS:
        raise ValueError("trace result must be pass, fail, skip, or info")
    normalized = {
        "stage": _clean(str(event.get("stage", "unknown"))),
        "action": _clean(str(event.get("action", "unknown"))),
        "result": result,
        "prompt_tokens": event.get("prompt_tokens"),
        "completion_tokens": event.get("completion_tokens"),
        "elapsed_seconds": float(event.get("elapsed_seconds", 0.0)),
        "checks": _clean(event.get("checks", [])),
        "failures": _clean(event.get("failures", [])),
        "revisions": _clean(event.get("revisions", [])),
        "details": _clean(event.get("details", {})),
    }
    for field in ("prompt_tokens", "completion_tokens"):
        token_count = normalized[field]
        if token_count is not None and (
            not isinstance(token_count, int)
            or isinstance(token_count, bool)
            or token_count < 0
        ):
            raise ValueError(f"{field} must be a nonnegative integer or null")
    if normalized["elapsed_seconds"] < 0:
        raise ValueError("elapsed_seconds must be nonnegative")
    line = json.dumps(normalized, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(line + "\n")
        stream.flush()

