"""Contract tests for the User 3 checker entry point."""

import copy
import json
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
        influence = next(check for check in report["checks"] if check["id"] == "two_meaningful_controls")
        self.assertEqual(influence["status"], "fail")
        self.assertIn("0 distinct controls", influence["detail"])

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

