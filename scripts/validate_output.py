"""Validate a generated offline page and its auditable JSONL trace."""

from __future__ import annotations

import argparse
import json
import math
import re
from html.parser import HTMLParser
from pathlib import Path


STAGES = {"read_input", "fetch", "identify", "plan", "generate", "check", "revision", "final"}
FIELDS = {"stage", "action", "result", "prompt_tokens", "completion_tokens", "elapsed_seconds", "checks", "failures", "revisions", "details"}
REMOTE = re.compile(r"(?i)(?:https?:)?//")
ACTIVE_REMOTE = re.compile(r"(?i)\b(?:fetch|XMLHttpRequest|WebSocket|EventSource|importScripts)\s*\(|\bimport\s*\(")
CSS_REMOTE = re.compile(r"(?i)@import\s+(?!url\s*\(\s*['\"]?data:|['\"]?data:)|url\s*\(\s*['\"]?\s*(?:https?:)?//")


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.errors: list[str] = []
        self.scripts = 0
        self.body = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "body":
            self.body = True
        if tag == "script":
            self.scripts += 1
        if tag in {"iframe", "object", "embed"}:
            self.errors.append(f"embedded external-capable element: {tag}")
        for key, value in attrs:
            if key.startswith("on"):
                self.errors.append(f"inline event handler: {key}")
            if key in {"src", "href", "poster", "action", "formaction"} and value and REMOTE.match(value.strip()) and tag != "a":
                self.errors.append(f"external reference: {tag}[{key}]")
            if tag == "a" and key == "href" and value and value.strip().lower().startswith("javascript:"):
                self.errors.append("unsafe citation link")
        if tag == "script" and values.get("src") and not values["src"].strip().lower().startswith("data:"):
            self.errors.append("external script source")
        if tag == "link" and values.get("href") and not values["href"].strip().lower().startswith("data:"):
            self.errors.append("external linked asset")


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def _usage_from_event(event: dict) -> dict:
    details = event.get("details", {})
    usage = details.get("usage", {}) if isinstance(details, dict) else {}
    if not isinstance(usage, dict):
        usage = {}
    def number(key: str) -> int | None:
        value = usage.get(key, event.get(key))
        return value if _nonnegative_int(value) else None
    prompt = number("prompt_tokens")
    completion = number("completion_tokens")
    total = number("total_tokens")
    reasoning = number("reasoning_tokens")
    verified = usage.get("verified") is True and prompt is not None and completion is not None
    return {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total,
            "reasoning_tokens": reasoning, "verified": verified}


def validate_output(output: Path, *, expected_model: str | None = None) -> dict:
    failures: list[str] = []
    html_path = output / "index.html"
    trace_path = output / "trace.jsonl"
    html = ""
    if not html_path.is_file():
        failures.append("index.html is missing")
    else:
        html = html_path.read_text(encoding="utf-8", errors="replace")
        page = _PageParser()
        page.feed(html)
        failures.extend(page.errors)
        if not page.body or page.scripts == 0:
            failures.append("page needs a body and inline calculation script")
        if ACTIVE_REMOTE.search(html) or CSS_REMOTE.search(html):
            failures.append("page contains a remote-capable request or CSS asset")
    events: list[dict] = []
    if not trace_path.is_file():
        failures.append("trace.jsonl is missing")
    else:
        for line_number, line in enumerate(trace_path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                failures.append(f"trace line {line_number} is not JSON")
                continue
            if not isinstance(event, dict):
                failures.append(f"trace line {line_number} is not an object")
                continue
            events.append(event)
            missing = FIELDS - event.keys()
            if missing:
                failures.append(f"trace line {line_number} missing {', '.join(sorted(missing))}")
            if event.get("result") not in {"pass", "fail", "skip", "info"}:
                failures.append(f"trace line {line_number} has invalid result")
            elapsed = event.get("elapsed_seconds")
            if type(elapsed) not in {float, int} or not math.isfinite(elapsed) or elapsed < 0:
                failures.append(f"trace line {line_number} has invalid elapsed_seconds")
            for field in ("checks", "failures", "revisions"):
                if not isinstance(event.get(field), list):
                    failures.append(f"trace line {line_number} has invalid {field}")
            if not isinstance(event.get("details"), dict):
                failures.append(f"trace line {line_number} has invalid details")
        if not events:
            failures.append("trace has no events")
    stages = {event.get("stage") for event in events}
    for required in ("read_input", "fetch", "identify", "plan", "generate", "check", "final"):
        if required not in stages:
            failures.append(f"trace missing {required} stage")
    finals = [event for event in events if event.get("stage") == "final"]
    if not finals or finals[-1].get("result") != "pass":
        failures.append("trace has no passing final event")
    final_check = next((event for event in reversed(events) if event.get("stage") == "check"), None)
    if final_check and final_check.get("result") == "fail":
        failures.append("final check failed")
    if final_check and isinstance(final_check.get("checks"), list) and any(
        isinstance(check, dict) and check.get("status") == "fail"
        for check in final_check["checks"]
    ):
        failures.append("final check records a failed required check")
    if finals and finals[-1].get("failures"):
        failures.append("final event records failures")
    call_events = []
    for event in events:
        details = event.get("details")
        if not isinstance(details, dict):
            continue
        if "request_number" in details and ("usage" in details or event.get("stage") in {"generate", "revision"}):
            if expected_model and details.get("model_id") != expected_model:
                failures.append("trace API model differs from requested model")
            call_events.append({"request_number": details["request_number"], "model_id": details.get("model_id"),
                                "usage": _usage_from_event(event), "result": event.get("result")})
    # A request can have start and completion events. Count it once and use only
    # the completion event for its usage.
    calls_by_number: dict[str, dict] = {}
    for call in call_events:
        key = str(call["request_number"])
        if key not in calls_by_number or call["result"] == "pass":
            calls_by_number[key] = call
    attempts = len(calls_by_number)
    if attempts == 0:
        failures.append("trace records no numbered API attempts")
    completed = [call for call in calls_by_number.values() if call["result"] == "pass"]
    usage = {key: sum(call["usage"][key] for call in completed if call["usage"][key] is not None)
             for key in ("prompt_tokens", "completion_tokens", "total_tokens", "reasoning_tokens")}
    for key in usage:
        if not any(call["usage"][key] is not None for call in completed):
            usage[key] = None
    usage["verified"] = bool(completed) and all(call["usage"]["verified"] for call in completed)
    usage["unknown_calls"] = attempts - sum(call["usage"]["verified"] for call in completed)
    return {"ok": not failures, "failures": failures, "html": str(html_path), "trace": str(trace_path),
            "events": len(events), "attempts": attempts, "usage": usage,
            "elapsed_seconds": events[-1].get("elapsed_seconds") if events else None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", help="Expected OpenRouter model ID")
    args = parser.parse_args()
    report = validate_output(args.output, expected_model=args.model)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
