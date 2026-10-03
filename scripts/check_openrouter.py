"""Make one tiny development-only call to verify a key and model ID."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from paper_playground.budget import ApiBudget
from paper_playground.config import load_local_env
from paper_playground.openrouter import OpenRouterClient
from paper_playground.trace import TraceWriter


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="OpenRouter model ID to verify")
    args = parser.parse_args()

    load_local_env()
    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        print("OPENROUTER_API_KEY is empty; add it to .env first.")
        return 1

    started = time.monotonic()
    trace = TraceWriter(Path("tmp/openrouter-check.jsonl"), started)
    budget = ApiBudget(started_at=started, max_calls=1, max_completion_tokens=32, max_seconds=60)
    client = OpenRouterClient(api_key, args.model, budget, trace)
    response = client.chat(
        [
            {"role": "system", "content": "Reply with exactly OK."},
            {"role": "user", "content": "Connection check."},
        ],
        purpose="development_connection_check",
        max_tokens=16,
        temperature=0,
    )
    print(
        f"OpenRouter responded with {response.completion_tokens} completion tokens: "
        f"{response.content.strip()[:40]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

