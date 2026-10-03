"""Request, completion-token and wall-clock budget for one agent run.

Every HTTP attempt, retries included, is preceded by exactly one reserve() and
followed by exactly one record(). Unverified usage keeps the full reservation
charged, so the hard completion cap holds even when the provider reports
nothing.
"""

from __future__ import annotations

import time
from typing import Callable

MAX_ATTEMPTS = 10
NORMAL_ATTEMPTS = 4
HARD_COMPLETION_TOKENS = 30_000
SOFT_COMPLETION_TOKENS = 24_000
GENERATION_STOP_SECONDS = 480.0
FINISH_SECONDS = 540.0
HARD_SECONDS = 600.0
MIN_ATTEMPT_SECONDS = 20.0


class BudgetExceeded(RuntimeError):
    """Raised by reserve() before an attempt that would break a limit."""


def _count(value: object) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return value
    return None


class Budget:
    def __init__(self, start: float | None = None, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self.start = clock() if start is None else start
        self.attempts = 0
        self.charged_completion = 0
        self.verified_prompt_tokens = 0
        self.unverified_attempts = 0
        self._outstanding: int | None = None

    def elapsed(self) -> float:
        return max(0.0, self._clock() - self.start)

    def remaining_seconds(self) -> float:
        """Seconds left for API work; attempts must end by the generation stop."""
        return max(0.0, GENERATION_STOP_SECONDS - self.elapsed())

    def finish_seconds_left(self) -> float:
        return max(0.0, FINISH_SECONDS - self.elapsed())

    def reserve(self, max_tokens: int) -> None:
        if self._outstanding is not None:
            raise RuntimeError("previous attempt was reserved but never recorded")
        if _count(max_tokens) is None or max_tokens == 0:
            raise ValueError("max_tokens must be a positive integer")
        if self.attempts >= MAX_ATTEMPTS:
            raise BudgetExceeded(f"request limit reached ({MAX_ATTEMPTS} attempts)")
        if self.charged_completion + max_tokens > HARD_COMPLETION_TOKENS:
            raise BudgetExceeded("completion-token reservation would exceed the hard cap")
        if self.remaining_seconds() < MIN_ATTEMPT_SECONDS:
            raise BudgetExceeded("too little time remains before the generation stop")
        self.attempts += 1
        self._outstanding = max_tokens

    def record(self, usage: dict) -> None:
        if self._outstanding is None:
            raise RuntimeError("record() called without a matching reserve()")
        reserved, self._outstanding = self._outstanding, None
        completion = _count(usage.get("completion_tokens")) if usage.get("verified") else None
        if completion is None:
            # Unknown usage: keep the whole ceiling charged.
            self.charged_completion += reserved
            self.unverified_attempts += 1
        else:
            # Reasoning tokens are already inside completion_tokens.
            self.charged_completion += completion
        prompt = _count(usage.get("prompt_tokens"))
        if prompt is not None:
            self.verified_prompt_tokens += prompt

    def completion_left(self) -> int:
        """Completion tokens still reservable under the hard cap."""
        return max(0, HARD_COMPLETION_TOKENS - self.charged_completion)

    def allows_optional_call(self, max_tokens: int) -> bool:
        """Policy gate for repairs/plans: stay under the soft token cap.

        The flow itself bounds normal calls (plan + generation + two repairs =
        NORMAL_ATTEMPTS); retries are limited only by the hard request cap.
        """
        return (
            self._outstanding is None
            and self.attempts < MAX_ATTEMPTS
            and self.charged_completion + max_tokens <= SOFT_COMPLETION_TOKENS
            and self.remaining_seconds() >= MIN_ATTEMPT_SECONDS
        )

    def snapshot(self) -> dict:
        return {
            "attempts": self.attempts,
            "charged_completion_tokens": self.charged_completion,
            "verified_prompt_tokens": self.verified_prompt_tokens,
            "unverified_attempts": self.unverified_attempts,
            "elapsed_seconds": round(self.elapsed(), 3),
        }
