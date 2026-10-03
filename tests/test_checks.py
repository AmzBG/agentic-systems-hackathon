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
        self.assertTrue(any("expected entropy_bits failed" in failure for failure in report["failures"]))

    def test_ambient_api_is_rejected_before_execution(self) -> None:
        spec = copy.deepcopy(self.spec)
        spec["compute_js"] = "function compute(inputs) { fetch('https://example.com'); return {}; }"
        report = run_checks(spec, self.html)
        self.assertFalse(report["ok"])
        self.assertIn("compute_safety", {c["id"] for c in report["checks"] if c["status"] == "fail"})

    def test_remote_asset_is_not_an_offline_page(self) -> None:
        html = self.html.replace("<script>", '<script src="https://cdn.example/x.js"></script><script>')
        report = run_checks(self.spec, html)
        self.assertFalse(report["ok"])
        self.assertIn("offline_html", {c["id"] for c in report["checks"] if c["status"] == "fail"})

    def test_attention_public_identities_and_four_live_controls(self) -> None:
        path = Path(__file__).resolve().parents[1] / "practice" / "specs" / "attention.json"
        spec = json.loads(path.read_text(encoding="utf-8"))
        report = run_checks(spec, self.html)
        self.assertTrue(report["ok"], report["failures"])
        influence = next(check for check in report["checks"] if check["id"] == "two_meaningful_controls")
        self.assertEqual(influence["status"], "pass")

