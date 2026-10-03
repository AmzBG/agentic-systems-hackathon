import time

import pytest

from paper_playground.budget import ApiBudget, BudgetExceeded


def test_budget_caps_calls_and_tokens() -> None:
    budget = ApiBudget(time.monotonic(), max_calls=1, max_completion_tokens=10)
    call, allowed = budget.start_call(50)
    assert (call, allowed) == (1, 10)
    budget.record_usage(7, 9)
    assert budget.prompt_tokens == 7
    assert budget.remaining_completion_tokens == 1
    with pytest.raises(BudgetExceeded):
        budget.start_call(1)


def test_budget_rejects_reported_token_overrun() -> None:
    budget = ApiBudget(time.monotonic(), max_completion_tokens=5)
    with pytest.raises(BudgetExceeded):
        budget.record_usage(1, 6)

