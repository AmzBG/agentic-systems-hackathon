"""Development-only independent entropy check for a generated offline page."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _runtime_payload(html: str) -> dict:
    match = re.search(r'<script type="application/json" id="runtime-data">(.*?)</script>', html, re.S)
    if match is None:
        raise ValueError("page has no embedded runtime data")
    return json.loads(match.group(1))


def _near(actual: object, expected: object) -> bool:
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(_near(a, e) for a, e in zip(actual, expected))
    return (isinstance(actual, (int, float)) and not isinstance(actual, bool)
            and isinstance(expected, (int, float)) and not isinstance(expected, bool)
            and math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9))


def _near_active_vector(actual: object, expected: list) -> bool:
    """Allow an output to retain explicitly zero-valued inactive slots."""
    return (isinstance(actual, list) and len(actual) >= len(expected)
            and _near(actual[:len(expected)], expected)
            and all(_near(value, 0) for value in actual[len(expected):]))


def verify_entropy_page(path: Path) -> dict:
    import quickjs

    payload = _runtime_payload(path.read_text(encoding="utf-8"))
    spec = payload["spec"]
    controls = spec["controls"]
    outputs = spec["outputs"]
    count_ids = [c["id"] for c in controls if c["kind"] in {"slider", "number"}
                 and ("count" in c["id"] or "outcome" in (c["id"] + c["label"]).lower())]
    weight_ids = [c["id"] for c in controls if c["kind"] == "vector"
                  and ("weight" in (c["id"] + c["label"]).lower()
                       or "probab" in (c["id"] + c["label"]).lower())]
    if len(count_ids) != 1 or len(weight_ids) != 1:
        raise ValueError("cannot identify entropy count and weight controls")
    count_id, weight_id = count_ids[0], weight_ids[0]
    weight_default = next(c["default"] for c in controls if c["id"] == weight_id)
    if len(weight_default) < 4:
        raise ValueError("entropy weight vector has fewer than four outcomes")
    probability_ids = [o["id"] for o in outputs
                       if (o["id"] in {"q", "probs", "probabilities"} or "probab" in o["id"])
                       and "sum" not in o["id"]]
    contribution_ids = [o["id"] for o in outputs
                        if "contrib" in (o["id"] + o["label"]).lower()]
    entropy_ids = [o["id"] for o in outputs if o["role"] == "result"
                   and "entropy" in (o["id"] + o["label"]).lower()
                   and "max" not in (o["id"] + o["label"]).lower()]
    if any(len(group) != 1 for group in (probability_ids, contribution_ids, entropy_ids)):
        raise ValueError("cannot identify entropy intermediate/result outputs")
    probability_id, contribution_id, entropy_id = (
        probability_ids[0], contribution_ids[0], entropy_ids[0])

    inputs = {c["id"]: c["default"] for c in controls}
    inputs[count_id] = 4
    for control in controls:
        if "uniform" in control["id"]:
            inputs[control["id"]] = False if control["kind"] == "toggle" else 0

    context = quickjs.Context()
    context.set_memory_limit(16 * 1024 * 1024)
    context.set_time_limit(0.08)
    context.eval((ROOT / "templates" / "interpreter.js").read_text(encoding="utf-8"))
    ast = json.dumps(payload["ast"], ensure_ascii=True)

    def calculate(weights: list[int]) -> dict:
        trial = {**inputs, weight_id: weights + [0] * (len(weight_default) - 4)}
        raw = context.eval("JSON.stringify(NumericRuntime.run(" + ast + ","
                           + json.dumps(trial, ensure_ascii=True) + "))")
        return json.loads(raw)

    oracle = json.loads((ROOT / "practice" / "oracles" / "core_identities.json").read_text(
        encoding="utf-8"))["cases"]["entropy"]["expected"]
    equal = calculate([1, 1, 1, 1])
    certain = calculate([1, 0, 0, 0])
    checks = {
        "four_equal_probabilities": _near_active_vector(equal[probability_id], oracle["probabilities"]),
        "four_equal_contributions": _near_active_vector(equal[contribution_id], oracle["contributions"]),
        "four_equal_entropy": _near(equal[entropy_id], oracle["entropy_bits"]),
        "certain_probabilities": _near_active_vector(certain[probability_id], [1, 0, 0, 0]),
        "certain_contributions": _near_active_vector(certain[contribution_id], [0, 0, 0, 0]),
        "certain_entropy": _near(certain[entropy_id], 0),
    }
    result = {"ok": all(checks.values()), "checks": checks, "path": str(path)}
    if not result["ok"]:
        result["observed"] = {
            "four_equal": {"probabilities": equal[probability_id],
                           "contributions": equal[contribution_id], "entropy": equal[entropy_id]},
            "certain": {"probabilities": certain[probability_id],
                        "contributions": certain[contribution_id], "entropy": certain[entropy_id]},
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="Directory containing index.html")
    args = parser.parse_args()
    try:
        result = verify_entropy_page(args.output / "index.html")
    except Exception as exc:
        result = {"ok": False, "error": f"{type(exc).__name__}: {str(exc)[:180]}"}
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
