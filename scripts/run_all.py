"""Run practice cases through the real CLI and retain per-run evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from validate_output import validate_output


ROOT = Path(__file__).resolve().parents[1]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:80] or "item"


def _safe_error(message: str) -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if key:
        message = message.replace(key, "[redacted]")
    return re.sub(r"\bsk-or-[A-Za-z0-9_-]+\b", "[redacted]", message)[-1500:]


def _default_cases() -> list[Path]:
    return sorted({*ROOT.glob("examples/*/case.json"), *ROOT.glob("practice/cases/*.json")})


def _supports_flow(agent: Path) -> bool:
    try:
        help_result = subprocess.run([sys.executable, str(agent), "--help"], cwd=ROOT,
                                     capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return help_result.returncode == 0 and "--flow" in help_result.stdout


def summarize_repeats(rows: list[dict]) -> list[dict]:
    """Keep each repeated run's outcome visible in the group summary."""
    groups: dict[tuple[str, str, str], list[dict]] = {}
    for row in rows:
        key = (row["case"], row["model_id"], row["flow"])
        groups.setdefault(key, []).append(row)
    summaries = []
    for (case, model, flow), group in sorted(groups.items()):
        summaries.append({
            "case": case,
            "model_id": model,
            "flow_requested": flow,
            "runs": [{
                "repeat": row["repeat"],
                "status": row["status"],
                "exit_code": row.get("exit_code"),
                "elapsed_seconds": row.get("elapsed_seconds"),
                "trace_elapsed_seconds": row.get("trace_elapsed_seconds"),
                "attempts": row.get("attempts"),
                "scored_tokens": row.get("usage", {}).get("scored_tokens"),
                "failures": row.get("failures", []),
                "repairs": row.get("repairs", []),
                "flow_evidence": row.get("flow_evidence"),
            } for row in sorted(group, key=lambda item: item["repeat"])],
            "passed": sum(row["status"] == "pass" for row in group),
            "failed": sum(row["status"] != "pass" for row in group),
        })
    return summaries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", required=True, nargs="+", help="Real OpenRouter model IDs")
    parser.add_argument("--flows", nargs="+", choices=("single", "planned"), default=["single"])
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cases", nargs="+", type=Path, help="Explicit case JSON paths")
    parser.add_argument("--timeout", type=int, default=650, help="Per-run wall timeout in seconds")
    parser.add_argument("--agent", type=Path, default=ROOT / "agent.py")
    parser.add_argument("--dry-run", action="store_true", help="List planned runs without calling the model")
    args = parser.parse_args()
    if args.repeats < 1 or args.timeout < 1:
        parser.error("repeats and timeout must be positive")
    if len(args.models) != len(set(args.models)):
        parser.error("model IDs must be distinct")
    cases = args.cases if args.cases is not None else _default_cases()
    if not cases:
        parser.error("no practice cases found")
    for case in cases:
        if not case.is_file():
            parser.error(f"case not found: {case}")
    if args.dry_run:
        print(json.dumps({
            "planned_runs": len(cases) * len(args.models) * len(args.flows) * args.repeats,
            "cases": [str(case) for case in cases],
            "models": args.models,
            "flows": args.flows,
            "repeats": args.repeats,
            "live_calls_made": 0,
        }, indent=2))
        return 0
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    agent = args.agent.resolve()
    supports_flow = _supports_flow(agent)
    rows: list[dict] = []
    for case in cases:
        for model in args.models:
            for flow in args.flows:
                for repeat in range(1, args.repeats + 1):
                    run_dir = output / "runs" / _slug(case.stem if case.stem != "case" else case.parent.name) / _slug(model) / flow / str(repeat)
                    row = {"case": str(case.resolve()), "model_id": model, "flow": flow,
                           "repeat": repeat, "output": str(run_dir),
                           "flow_evidence": {"requested": flow, "cli_flag_sent": supports_flow}}
                    if run_dir.exists() and any(run_dir.iterdir()):
                        row.update({"exit_code": None, "elapsed_seconds": 0, "status": "output_exists",
                                    "failures": ["run directory already contains files; choose a fresh --output"],
                                    "attempts": 0, "usage": {"verified": False, "unknown_calls": 0}})
                    elif flow == "planned" and not supports_flow:
                        row.update({"exit_code": None, "elapsed_seconds": 0, "status": "unsupported_flow",
                                    "failures": ["agent.py does not expose --flow planned"], "attempts": 0,
                                    "usage": {"verified": False, "unknown_calls": 0}})
                    else:
                        run_dir.mkdir(parents=True, exist_ok=True)
                        command = [sys.executable, str(agent), "--input", str(case.resolve()),
                                   "--output", str(run_dir), "--model", model]
                        if supports_flow:
                            command.extend(["--flow", flow])
                        started = time.monotonic()
                        try:
                            process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                                     timeout=args.timeout)
                            exit_code = process.returncode
                            stderr_tail = _safe_error(process.stderr)
                        except subprocess.TimeoutExpired as exc:
                            exit_code = None
                            stderr_tail = "run exceeded wall timeout"
                        except OSError as exc:
                            exit_code = None
                            stderr_tail = type(exc).__name__
                        elapsed = round(time.monotonic() - started, 3)
                        report = validate_output(run_dir, expected_model=model)
                        failures = list(report["failures"])
                        if exit_code != 0:
                            failures.insert(0, f"agent exit code: {exit_code}")
                        row.update({"exit_code": exit_code, "elapsed_seconds": elapsed,
                                    "status": "pass" if not failures else "fail", "failures": failures,
                                    "attempts": report["attempts"], "usage": report["usage"],
                                    "events": report["events"], "repairs": report["repairs"],
                                    "trace_elapsed_seconds": report["elapsed_seconds"],
                                    "flow_evidence": {**row["flow_evidence"], **report["flow_evidence"]},
                                    "stderr_tail": stderr_tail})
                    rows.append(row)
                    print(f"{row['status']}: {case.name} {model} {flow} #{repeat}", flush=True)
    with (output / "runs.jsonl").open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = {"runs": len(rows), "passed": sum(row["status"] == "pass" for row in rows),
               "failed": sum(row["status"] != "pass" for row in rows),
               "models": args.models, "flows": args.flows,
               "cases": [str(case.resolve()) for case in cases],
               "repeated_runs": summarize_repeats(rows),
               "report": str(output / "runs.jsonl")}
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
