"""Development-only page-interpreter comparison against reviewed independent values."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from check_entropy_oracle import _near, _runtime_payload
from runtime import merge_inputs


def verify_page(path: Path, inputs: dict, expected: dict) -> dict:
    import quickjs

    payload = _runtime_payload(path.read_text(encoding="utf-8"))
    trial = merge_inputs(payload["spec"]["controls"], inputs)
    context = quickjs.Context()
    context.set_memory_limit(16 * 1024 * 1024)
    context.set_time_limit(0.08)
    context.eval((ROOT / "templates" / "interpreter.js").read_text(encoding="utf-8"))
    observed = json.loads(context.eval("JSON.stringify(NumericRuntime.run(" +
        json.dumps(payload["ast"]) + "," + json.dumps(trial) + "))"))
    checks = {key: key in observed and _near(observed[key], value) for key, value in expected.items()}
    return {"ok": bool(checks) and all(checks.values()), "checks": checks,
            "inputs": trial, "expected": expected,
            "observed": {key: observed.get(key) for key in expected}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--inputs", required=True, type=json.loads)
    parser.add_argument("--expected", required=True, type=json.loads)
    args = parser.parse_args()
    try:
        report = verify_page(args.output / "index.html", args.inputs, args.expected)
    except Exception as exc:
        report = {"ok": False, "error": type(exc).__name__, "detail": str(exc)[:300]}
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
