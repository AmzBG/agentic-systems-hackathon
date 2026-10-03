"""Small OpenRouter client that makes every request and token visible in the trace."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

from .budget import ApiBudget
from .config import OPENROUTER_URL
from .trace import TraceWriter


class OpenRouterError(RuntimeError):
    """Raised for transport errors or malformed OpenRouter responses."""


@dataclass(frozen=True)
class ModelResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    reasoning_tokens: int | None


class OpenRouterClient:
    def __init__(
        self,
        api_key: str,
        model: str,
        budget: ApiBudget,
        trace: TraceWriter,
    ) -> None:
        if not api_key:
            raise OpenRouterError("OPENROUTER_API_KEY is not set.")
        self.api_key = api_key
        self.model = model
        self.budget = budget
        self.trace = trace

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        purpose: str,
        max_tokens: int,
        temperature: float = 0.2,
    ) -> ModelResponse:
        call_number, allowed_tokens = self.budget.start_call(max_tokens)
        request_started = time.monotonic()
        self.trace.emit(
            "model",
            "request",
            "started",
            call=call_number,
            purpose=purpose,
            model=self.model,
            max_completion_tokens=allowed_tokens,
        )
        timeout = max(10.0, min(180.0, self.budget.remaining_seconds - 5.0))
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/AmzBG/agentic-systems-hackathon",
                    "X-Title": "Paper to Playground",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": allowed_tokens,
                },
                timeout=timeout,
            )
        except requests.RequestException as exc:
            self.trace.emit(
                "model",
                "request",
                "failed",
                call=call_number,
                purpose=purpose,
                elapsed_seconds_for_call=round(time.monotonic() - request_started, 3),
                error=type(exc).__name__,
            )
            raise OpenRouterError(f"OpenRouter request failed: {type(exc).__name__}") from exc

        if not response.ok:
            self.trace.emit(
                "model",
                "request",
                "failed",
                call=call_number,
                purpose=purpose,
                status_code=response.status_code,
                elapsed_seconds_for_call=round(time.monotonic() - request_started, 3),
            )
            raise OpenRouterError(f"OpenRouter returned HTTP {response.status_code}.")

        try:
            payload: dict[str, Any] = response.json()
            raw_content = payload["choices"][0]["message"]["content"]
            if isinstance(raw_content, list):
                content = "".join(
                    item.get("text", "")
                    for item in raw_content
                    if isinstance(item, dict) and item.get("type") == "text"
                )
            else:
                content = str(raw_content)
            usage = payload.get("usage") or {}
            prompt_tokens = int(usage.get("prompt_tokens") or 0)
            completion_tokens = int(usage.get("completion_tokens") or 0)
            details = usage.get("completion_tokens_details") or {}
            reasoning_raw = details.get("reasoning_tokens")
            reasoning_tokens = int(reasoning_raw) if reasoning_raw is not None else None
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            self.trace.emit(
                "model",
                "parse_response",
                "failed",
                call=call_number,
                purpose=purpose,
                error=type(exc).__name__,
            )
            raise OpenRouterError("OpenRouter returned a malformed response.") from exc

        self.budget.record_usage(prompt_tokens, completion_tokens)
        self.trace.emit(
            "model",
            "request",
            "ok",
            call=call_number,
            purpose=purpose,
            status_code=response.status_code,
            elapsed_seconds_for_call=round(time.monotonic() - request_started, 3),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            reasoning_tokens=reasoning_tokens,
            cumulative_completion_tokens=self.budget.completion_tokens,
        )
        if not content.strip():
            raise OpenRouterError("OpenRouter returned empty content.")
        return ModelResponse(content, prompt_tokens, completion_tokens, reasoning_tokens)

