"""Audit tracked release files, pins, examples, placeholders, and leaked keys."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEY = re.compile(rb"(?:sk-or-v1-[A-Za-z0-9_-]{20,}|OPENROUTER_API_KEY\s*[=:]\s*['\"]?sk-[A-Za-z0-9_-]{20,})")
PIN = re.compile(r"^[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?==[A-Za-z0-9_.+!-]+(?:\s*;.*)?$")


def audit(root: Path = ROOT) -> dict:
    failures: list[str] = []
    try:
        tracked = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True,
                                 check=True).stdout.decode("utf-8").split("\0")
    except (OSError, subprocess.CalledProcessError):
        tracked = []
        failures.append("cannot enumerate tracked files")
    tracked = [path for path in tracked if path]
    for name in ("AI.md", "README.md", "requirements.txt", "agent.py", "trace.py", "checks.py",
                 "scripts/run_all.py", "scripts/validate_output.py", "scripts/verify_install.py"):
        if not (root / name).is_file():
            failures.append(f"required file missing: {name}")
    if any(path == ".env" or path.endswith("/.env") for path in tracked):
        failures.append(".env is tracked")
    for name in tracked:
        file = root / name
        if file.is_file() and file.stat().st_size < 2_000_000 and KEY.search(file.read_bytes()):
            failures.append(f"possible credential in tracked file: {name}")
    readme = (root / "README.md").read_text(encoding="utf-8") if (root / "README.md").is_file() else ""
    for label, pattern in {
        "team": r"(?i)\bteam\b", "setup": r"(?i)\bsetup\b", "architecture": r"(?i)\barchitecture\b",
        "credits": r"(?i)\bcredits?\b", "model ID": r"deepseek/deepseek-v4\.1-flash",
        "CLI example": r"agent\.py\s+--input\b", "trace": r"trace\.jsonl",
    }.items():
        if not re.search(pattern, readme):
            failures.append(f"README missing {label}")
    requirements = (root / "requirements.txt").read_text(encoding="utf-8").splitlines() if (root / "requirements.txt").is_file() else []
    for line_number, line in enumerate(requirements, 1):
        line = line.strip()
        if line and not line.startswith("#") and not PIN.fullmatch(line):
            failures.append(f"requirements line {line_number} is not exactly pinned")
    if not any("quickjs==" in line.lower() for line in requirements):
        failures.append("QuickJS engine pin missing")
    review_template = root / "evidence" / "REVIEW_TEMPLATE.md"
    if not review_template.is_file():
        failures.append("evidence review template is missing")
    else:
        template = review_template.read_text(encoding="utf-8").lower()
        for label, marker in {
            "repeat-run outcomes": "repeat-run comparison",
            "repair outcomes": "repair outcomes",
            "flow-selection evidence": "effective flow",
            "verified scored tokens": "scored tokens",
            "run exit status": "process exit",
        }.items():
            if marker not in template:
                failures.append(f"evidence template missing {label}")
    example_inputs = list((root / "examples").glob("*/case.json"))
    if not example_inputs:
        failures.append("no public example input")
    for example in example_inputs:
        try:
            data = json.loads(example.read_text(encoding="utf-8"))
            if any(not isinstance(data.get(key), str) or not data[key].strip() for key in ("source_url", "focus", "audience")):
                failures.append(f"invalid example input: {example.relative_to(root)}")
        except (OSError, json.JSONDecodeError):
            failures.append(f"unreadable example input: {example.relative_to(root)}")
    if not list((root / "examples").glob("*/index.html")):
        failures.append("no public example output HTML")
    for name in ("checks.py", "trace.py"):
        file = root / name
        if file.is_file() and "checks not implemented" in file.read_text(encoding="utf-8"):
            failures.append(f"temporary stub remains in {name}")
    return {"ok": not failures, "failures": failures, "tracked_files": len(tracked),
            "example_inputs": len(example_inputs)}


def main() -> int:
    report = audit()
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
