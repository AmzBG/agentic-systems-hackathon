"""Enforce the assessment's request, completion-token, and wall-clock limits."""

from __future__ import annotations

import time
from dataclasses import dataclass


class BudgetExceeded(RuntimeError):
    """Raised before an API request that would violate an assessment limit."""


@dataclass
class ApiBudget:
    started_at: float
    max_calls: int = 10
    max_completion_tokens: int = 30_000
    max_seconds: float = 600.0
    calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def elapsed_seconds(self) -> float:
        return time.monotonic() - self.started_at

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, self.max_seconds - self.elapsed_seconds)

    @property
    def remaining_completion_tokens(self) -> int:
        return max(0, self.max_completion_tokens - self.completion_tokens)

    def start_call(self, requested_max_tokens: int) -> tuple[int, int]:
        if self.calls >= self.max_calls:
            raise BudgetExceeded(f"API call limit reached ({self.max_calls}).")
        if self.remaining_seconds < 15:
            raise BudgetExceeded("Less than 15 seconds remain in the runtime budget.")
        allowed_tokens = min(requested_max_tokens, self.remaining_completion_tokens)
        if allowed_tokens <= 0:
            raise BudgetExceeded("Completion-token budget is exhausted.")
        self.calls += 1
        return self.calls, allowed_tokens

    def record_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens += max(0, prompt_tokens)
        self.completion_tokens += max(0, completion_tokens)
        if self.completion_tokens > self.max_completion_tokens:
            raise BudgetExceeded("OpenRouter reported completion usage above the allowed limit.")

