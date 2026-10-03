"""End-to-end command-line pipeline."""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from .budget import ApiBudget
from .case_input import load_case
from .config import (
    MAX_API_CALLS,
    MAX_COMPLETION_TOKENS,
    MAX_RUNTIME_SECONDS,
    load_local_env,
)
from .openrouter import OpenRouterClient
from .prompts import generation_messages, repair_messages
from .sources import load_source
from .trace import TraceWriter
from .validation import failed_checks, validate_html


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a self-contained interactive explanation from a research paper."
    )
    parser.add_argument("--input", required=True, type=Path, help="UTF-8 case JSON")
    parser.add_argument("--output", required=True, type=Path, help="Output directory")
    parser.add_argument("--model", required=True, help="OpenRouter model ID")
    return parser


def _strip_code_fence(content: str) -> str:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        cleaned = cleaned[first_newline + 1 :] if first_newline >= 0 else cleaned
        if cleaned.rstrip().endswith("```"):
            cleaned = cleaned.rstrip()[:-3]
    return cleaned.strip()


def _write_atomic(path: Path, content: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def run(input_path: Path, output_dir: Path, model: str) -> int:
    started_at = time.monotonic()
    output_dir.mkdir(parents=True, exist_ok=True)
    trace = TraceWriter(output_dir / "trace.jsonl", started_at)
    trace.emit("run", "start", "ok", model=model)
    try:
        load_local_env()
        case = load_case(input_path)
        trace.emit(
            "input",
            "validate",
            "ok",
            fields=["source_url", "focus", "audience", *sorted(case.extra)],
        )
        api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not set; add it to the environment or local .env.")

        source = load_source(case, trace)
        budget = ApiBudget(
            started_at=started_at,
            max_calls=MAX_API_CALLS,
            max_completion_tokens=MAX_COMPLETION_TOKENS,
            max_seconds=MAX_RUNTIME_SECONDS,
        )
        client = OpenRouterClient(api_key, model, budget, trace)
        response = client.chat(
            generation_messages(case, source),
            purpose="generate_artifact",
            max_tokens=12_000,
        )
        html = _strip_code_fence(response.content)
        checks = validate_html(html, case.source_url)
        failures = failed_checks(checks)
        trace.emit(
            "validation",
            "check_generated_html",
            "ok" if not failures else "failed",
            checks=checks,
            failure_count=len(failures),
        )

        if failures:
            response = client.chat(
                repair_messages(case, source, html, failures),
                purpose="repair_failed_checks",
                max_tokens=12_000,
                temperature=0.1,
            )
            html = _strip_code_fence(response.content)
            checks = validate_html(html, case.source_url)
            failures = failed_checks(checks)
            trace.emit(
                "validation",
                "check_revised_html",
                "ok" if not failures else "failed",
                checks=checks,
                failure_count=len(failures),
            )

        _write_atomic(output_dir / "index.html", html)
        if failures:
            trace.emit(
                "run",
                "finish",
                "failed",
                reason="generated artifact still fails deterministic checks",
                api_calls=budget.calls,
                prompt_tokens=budget.prompt_tokens,
                completion_tokens=budget.completion_tokens,
            )
            return 1

        trace.emit(
            "run",
            "finish",
            "ok",
            api_calls=budget.calls,
            prompt_tokens=budget.prompt_tokens,
            completion_tokens=budget.completion_tokens,
        )
        return 0
    except Exception as exc:
        trace.emit(
            "run",
            "finish",
            "failed",
            error=type(exc).__name__,
            message=str(exc)[:500],
        )
        print(f"error: {exc}", file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    return run(args.input, args.output, args.model)

