"""Make one tiny development-only call to verify a key and model ID."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import load_dotenv
from budget import Budget
from model_client import ModelCallError, OpenRouterClient
from trace import write_trace


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="OpenRouter model ID to verify")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("OPENROUTER_API_KEY is empty; add it to .env first.")
        return 1

    started = time.monotonic()
    budget = Budget(start=started)
    client = OpenRouterClient(args.model, api_key, budget, timeout=20)
    result, failures = "pass", []
    try:
        content, usage = client.call_model(
            [
                {"role": "system", "content": "Reply with exactly OK."},
                {"role": "user", "content": "Connection check."},
            ],
            max_tokens=16,
        )
        if content.strip() != "OK":
            result, failures = "fail", ["model did not return the expected acknowledgement"]
    except ModelCallError as exc:
        result, failures, usage = "fail", [str(exc)], client.last_call.get("usage", {})
    trace_path = Path("tmp/openrouter-check.jsonl")
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    write_trace(str(trace_path), {
        "stage": "generate", "action": "development_connection_check", "result": result,
        "elapsed_seconds": time.monotonic() - started,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "failures": failures,
        "details": {"model": args.model, "usage": usage, "attempts": budget.attempts},
    })
    print("OpenRouter check:", result, f"({budget.attempts} attempt)")
    return 0 if result == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

