"""OpenRouter chat-completions client: exactly one HTTP attempt per call.

Retries are the caller's decision so each attempt is traced individually. The
budget is reserved before transport and recorded afterwards on every path.
Only visible message content is returned; reasoning fields are ignored.
"""

from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
from typing import Callable

from budget import Budget

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_TIMEOUT_SECONDS = 240.0
MAX_RESPONSE_BYTES = 4 * 1024 * 1024
RETRYABLE_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}


class ModelCallError(RuntimeError):
    """A failed attempt; the message never contains response bodies or keys."""

    def __init__(self, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable


def empty_usage() -> dict:
    return {"prompt_tokens": None, "completion_tokens": None, "total_tokens": None,
            "reasoning_tokens": None, "verified": False}


def _count(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


def parse_usage(raw: object) -> dict:
    usage = empty_usage()
    if not isinstance(raw, dict):
        return usage
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        usage[key] = _count(raw.get(key))
    details = raw.get("completion_tokens_details")
    if isinstance(details, dict):
        usage["reasoning_tokens"] = _count(details.get("reasoning_tokens"))
    usage["verified"] = usage["completion_tokens"] is not None
    return usage


def visible_text(message: object) -> str:
    """Concatenate visible text segments; never reasoning fields."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for segment in content:
            if isinstance(segment, str):
                parts.append(segment)
            elif isinstance(segment, dict) and segment.get("type") in (None, "text", "output_text") \
                    and isinstance(segment.get("text"), str):
                parts.append(segment["text"])
        return "".join(parts)
    return ""


class OpenRouterClient:
    def __init__(
        self,
        model_id: str,
        api_key: str,
        budget: Budget,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        *,
        url: str = OPENROUTER_URL,
        opener: Callable = urllib.request.urlopen,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not model_id or not api_key:
            raise ValueError("model_id and api_key are required")
        self.model_id = model_id
        self._api_key = api_key
        self.budget = budget
        self.timeout = timeout
        self._url = url
        self._opener = opener
        self._clock = clock
        self.last_call: dict = {}

    def __repr__(self) -> str:  # never expose the key
        return f"OpenRouterClient(model_id={self.model_id!r})"

    def call_model(self, messages: list[dict[str, str]], max_tokens: int) -> tuple[str, dict]:
        self.budget.reserve(max_tokens)  # raises BudgetExceeded before any traffic
        request_number = self.budget.attempts
        timeout = max(1.0, min(self.timeout, self.budget.remaining_seconds()))
        usage = empty_usage()
        started = self._clock()
        self.last_call = {"request_number": request_number, "model_id": self.model_id,
                          "max_tokens": max_tokens, "timeout_seconds": round(timeout, 1)}
        try:
            body = json.dumps({"model": self.model_id, "messages": messages,
                               "max_tokens": max_tokens}).encode("utf-8")
            request = urllib.request.Request(self._url, data=body, method="POST", headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            })
            try:
                with self._opener(request, timeout=timeout) as response:
                    raw = response.read(MAX_RESPONSE_BYTES + 1)
            except urllib.error.HTTPError as exc:
                retryable = exc.code in RETRYABLE_STATUS
                self.last_call["http_status"] = exc.code
                raise ModelCallError(f"HTTP {exc.code} from OpenRouter", retryable=retryable) from None
            except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError, OSError) as exc:
                raise ModelCallError(f"transport failure ({type(exc).__name__})", retryable=True) from None
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ModelCallError("response exceeded the size cap", retryable=False)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, ValueError):
                raise ModelCallError("response was not valid JSON", retryable=True) from None
            if not isinstance(payload, dict):
                raise ModelCallError("response was not a JSON object", retryable=True)
            usage = parse_usage(payload.get("usage"))
            if "error" in payload and not payload.get("choices"):
                raise ModelCallError("OpenRouter returned an error object", retryable=True)
            choices = payload.get("choices")
            choice = choices[0] if isinstance(choices, list) and choices and isinstance(choices[0], dict) else {}
            finish = choice.get("finish_reason")
            self.last_call["finish_reason"] = finish if isinstance(finish, str) else None
            served = payload.get("model")
            self.last_call["served_model"] = served[:120] if isinstance(served, str) else None
            return visible_text(choice.get("message")), usage
        finally:
            self.last_call["duration_seconds"] = round(self._clock() - started, 3)
            self.last_call["usage"] = dict(usage)
            self.budget.record(usage)
