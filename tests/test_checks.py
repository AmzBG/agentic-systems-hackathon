"""Contract tests for the User 3 checker entry point."""

import copy
import json
import re
import unittest
from pathlib import Path

from checks import run_checks


class ContractTests(unittest.TestCase):
    def test_bad_schema_cannot_claim_success(self) -> None:
        report = run_checks({}, "")
        self.assertEqual(set(report), {"ok", "degraded", "checks", "failures", "revisions"})
        self.assertFalse(report["ok"])
        self.assertTrue(report["degraded"])
        self.assertTrue(report["failures"])


class NumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = Path(__file__).resolve().parents[1] / "practice" / "specs" / "entropy.json"
        cls.spec = json.loads(path.read_text(encoding="utf-8"))
        cls.html = (
            "<!doctype html><html><head><style>body{color:#123}</style></head>"
            "<body><h1>Entropy</h1><svg aria-label='probabilities'></svg>"
            "<script>document.addEventListener('input',()=>{});</script>"
            + "<p>Teaching explanation and local calculation.</p>" * 8
            + "</body></html>"
        )

    def test_independent_entropy_identities_and_control_influence(self) -> None:
        report = run_checks(self.spec, self.html)
        self.assertTrue(report["ok"], report["failures"])
        self.assertFalse(report["degraded"])
        self.assertIn("two_meaningful_controls", {c["id"] for c in report["checks"] if c["status"] == "pass"})

    def test_wrong_scientific_expectation_is_detected(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["tests"][1]["expected"]["entropy_bits"] = 3
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertTrue(any(
            "expected entropy_bits failed" in failure
            and "measured=2" in failure
            and "expected=3" in failure
            and "atol=1e-09" in failure
            for failure in report["failures"]
        ))

    def test_grounding_needs_a_paper_citation(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["grounding"] = [item for item in spec["grounding"]
                             if item["support"] in {"example", "simplification"}]
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertTrue(any("excerpt or unverified paper citation" in failure
                            for failure in report["failures"]))

    def test_failed_invariant_reports_measured_and_expected_sum(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["invariants"][0]["expected"] = 2
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertTrue(any(
            "invariant probabilities sum to one failed" in failure
            and "measured=1.0" in failure
            and "expected=2" in failure
            for failure in report["failures"]
        ))

    def test_ambient_api_is_rejected_before_execution(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["compute_js"] = "function compute(inputs) { fetch('https://example.com'); return {}; }"
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertIn("compute_safety", {c["id"] for c in report["checks"] if c["status"] == "fail"})

    def test_compute_cannot_mutate_input_matrix(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["compute_js"] = spec["compute_js"].replace(
            "const count =", "inputs.weights[0] = 0; const count ="
        )
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertTrue(any("mutated its inputs" in failure for failure in report["failures"]))

    def test_renderer_unsupported_filter_fails_numerical_execution(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["compute_js"] = spec["compute_js"].replace(
            "const count =", "const probe = [1, 2].filter(v => v > 1).length; const count ="
        )
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertTrue(any(
            check["id"] == "numerical_execution" and check["status"] == "fail"
            and "Unsupported array property: filter" in check["detail"]
            for check in report["checks"]
        ))

    def test_renderer_unsupported_array_from_fails_numerical_execution(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["compute_js"] = spec["compute_js"].replace(
            "const count =", "const probe = Array.from([1, 2]); const count ="
        )
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertTrue(any(
            check["id"] == "numerical_execution" and check["status"] == "fail"
            for check in report["checks"]
        ))

    def test_compute_cannot_return_undeclared_metadata(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["compute_js"] = spec["compute_js"].replace(
            "return { probabilities, contributions, entropy_bits };",
            "return { probabilities, contributions, entropy_bits, note: 42 };",
        )
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertTrue(any("undeclared outputs note" in failure for failure in report["failures"]))

    def test_stateful_compute_cannot_mimic_control_influence(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["compute_js"] = (
            "function compute(inputs) { const count=inputs.count; const weights=inputs.weights; "
            "compute.calls=(compute.calls||0)+1; return {probabilities:[1,0,0,0], "
            "contributions:[0,0,0,0], entropy_bits:compute.calls}; }"
        )
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertIn("compute_safety", {check["id"] for check in report["checks"] if check["status"] == "fail"})
        numerical = next(check for check in report["checks"] if check["id"] == "numerical_execution")
        self.assertEqual(numerical["status"], "skip")

    def test_remote_asset_is_not_an_offline_page(self) -> None:
        html = self.html.replace("<script>", '<script src="https://cdn.example/x.js"></script><script>')
        report = run_checks(self.spec, html)
        self.assertFalse(report["ok"])
        self.assertIn("offline_html", {c["id"] for c in report["checks"] if c["status"] == "fail"})

    def test_inline_event_handlers_are_rejected_consistently(self) -> None:
        html = self.html.replace("<svg", "<input oninput='f()'><svg")
        report = run_checks(self.spec, html)
        self.assertFalse(report["ok"])
        self.assertTrue(any("inline event handler" in failure for failure in report["failures"]))

    def test_attention_public_identities_and_four_live_controls(self) -> None:
        path = Path(__file__).resolve().parents[1] / "practice" / "specs" / "attention.json"
        spec = json.loads(path.read_text(encoding="utf-8"))
        report = run_checks(spec, self.html)
        self.assertTrue(report["ok"], report["failures"])
        influence = next(check for check in report["checks"] if check["id"] == "two_meaningful_controls")
        self.assertEqual(influence["status"], "pass")


class PublishedExampleTests(unittest.TestCase):
    def test_entropy_page_matches_independent_oracle(self) -> None:
        import quickjs

        root = Path(__file__).resolve().parents[1]
        html = (root / "examples" / "entropy" / "index.html").read_text(encoding="utf-8")
        payload = re.search(
            r'<script type="application/json" id="runtime-data">(.*?)</script>', html, re.S
        )
        self.assertIsNotNone(payload)
        ast = json.loads(payload.group(1))["ast"]
        oracle = json.loads((root / "practice" / "oracles" / "core_identities.json").read_text(
            encoding="utf-8"))["cases"]["entropy"]
        inputs = {
            "n_outcomes": oracle["inputs"]["count"],
            "weights": oracle["inputs"]["weights"] + [0, 0],
            "uniform": False,
        }
        context = quickjs.Context()
        context.set_memory_limit(16 * 1024 * 1024)
        context.set_time_limit(0.08)
        context.eval((root / "templates" / "interpreter.js").read_text(encoding="utf-8"))

        def calculate(values: dict) -> dict:
            result = context.eval("JSON.stringify(NumericRuntime.run(" + json.dumps(ast) + ","
                                  + json.dumps(values) + "))")
            return json.loads(result)

        actual = calculate(inputs)
        for measured, expected in zip(actual["probabilities"], oracle["expected"]["probabilities"]):
            self.assertAlmostEqual(measured, expected, places=9)
        for measured, expected in zip(actual["contributions"], oracle["expected"]["contributions"]):
            self.assertAlmostEqual(measured, expected, places=9)
        self.assertAlmostEqual(actual["entropy"], oracle["expected"]["entropy_bits"], places=9)

        certain = calculate({**inputs, "weights": [1, 0, 0, 0, 0, 0]})
        self.assertEqual(certain["probabilities"], [1, 0, 0, 0])
        self.assertEqual(certain["contributions"], [0, 0, 0, 0])
        self.assertEqual(certain["entropy"], 0)

