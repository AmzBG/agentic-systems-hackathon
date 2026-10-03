"""Offline evidence inspection and minimal core/runtime admission reproductions."""

from __future__ import annotations

import copy
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import agent
import runtime
from scripts.check_entropy_oracle import verify_entropy_page
from scripts.validate_output import validate_output
from spec_parser import validate_spec
from tests.test_core import toy_spec


def admission_reproductions() -> dict:
    spec = toy_spec()
    spec["controls"][1].update(kind="matrix", default=[[0] * 8 for _ in range(8)], shape=[8, 8])
    spec["controls"].append(dict(copy.deepcopy(spec["controls"][1]), id="second_matrix"))
    spec["explorations"][1]["preset"] = {"gain": 2}
    results = {}
    for label, validator in (("core_parser", validate_spec), ("runtime", runtime.validate_spec)):
        try:
            validator(spec)
            results[label] = "accepted"
        except ValueError as exc:
            results[label] = str(exc)
    axis = toy_spec()
    axis["compute_js"] = "function compute(inputs) { return {scaled:Array(9).fill(inputs.gain),total:6}; }"
    results["nine_axis_core_probe"] = agent.page_compute_check(axis)
    extra = toy_spec()
    extra["compute_js"] = extra["compute_js"].replace("return { scaled, total:", "return { note:42, scaled, total:")
    results["extra_output_core_probe"] = agent.page_compute_check(extra)
    return results


def main() -> None:
    rows = []
    for pair in (1, 2):
        report = ROOT / "out" / f"paired-entropy-{pair}" / "runs.jsonl"
        if not report.exists():
            rows.append({"pair": pair, "status": "unavailable locally"})
            continue
        for line in report.read_text(encoding="utf-8").splitlines():
            run = json.loads(line)
            output = Path(run["output"])
            validation = validate_output(output, expected_model=run["model_id"])
            oracle = verify_entropy_page(output / "index.html")
            rows.append({"pair": pair, "flow": run["flow"], "model": run["model_id"],
                         "reasoning": run["reasoning"], "wall_seconds": run["elapsed_seconds"],
                         "trace_seconds": validation["elapsed_seconds"], "requests": validation["attempts"],
                         "usage": validation["usage"], "validator": validation["ok"],
                         "oracle": oracle["ok"], "repairs": validation["repairs"],
                         "flow_evidence": validation["flow_evidence"]})
    print(json.dumps({"review_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                      "paired_runs": rows, "admission_reproductions": admission_reproductions(),
                      "independent_math": {"decay_half_life_lambda_0_2": math.log(2) / 0.2,
                                           "decay_fraction_time_5": math.exp(-0.2 * 5),
                                           "ratio_lambda_1_time_50": 50 / math.log(2),
                                           "two_residual_sse_bound": 2 * 35**2}}, indent=2))


if __name__ == "__main__":
    main()
