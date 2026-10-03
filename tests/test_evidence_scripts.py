"""Focused evidence checks that distinguish real usage from missing evidence."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_all import summarize_repeats  # noqa: E402
from validate_output import validate_output  # noqa: E402


def _event(stage: str, *, result: str = "pass", details: dict | None = None) -> dict:
    return {"stage": stage, "action": stage, "result": result,
            "prompt_tokens": None, "completion_tokens": None, "elapsed_seconds": 1.0,
            "checks": [], "failures": [], "revisions": [], "details": details or {}}


class EvidenceScriptTests(unittest.TestCase):
    def test_usage_counts_request_once_and_reasoning_is_subset(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            (output / "index.html").write_text(
                '<html><body><a href="https://paper.example/source">Source</a>'
                '<img src="data:image/png;base64,AA=="><script>const x=1;</script></body></html>',
                encoding="utf-8")
            events = [_event(stage) for stage in ("read_input", "fetch", "identify", "plan")]
            events.append(_event("generate", result="info", details={"request_number": 1, "model_id": "test/model"}))
            events.append(_event("generate", details={"request_number": 1, "model_id": "test/model",
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30,
                          "reasoning_tokens": 5, "verified": True}}))
            events.extend([_event("check", result="fail"), _event("revision"), _event("check"),
                           _event("final", details={"exit_code": 0})])
            events[-1]["revisions"] = [
                {"number": 1, "accepted": True, "mode": "targeted", "requested": ["compute_js"]}
            ]
            (output / "trace.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
            report = validate_output(output, expected_model="test/model")
            self.assertTrue(report["ok"], report["failures"])
            self.assertEqual(report["attempts"], 1)
            self.assertEqual(report["usage"]["completion_tokens"], 20)
            self.assertEqual(report["usage"]["reasoning_tokens"], 5)
            self.assertEqual(report["usage"]["scored_tokens"], 30)
            self.assertEqual(report["repairs"][0]["outcome"], "accepted")

    def test_failed_planning_attempt_is_counted_as_unknown_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            (output / "index.html").write_text(
                "<html><body><script>const x=1;</script></body></html>", encoding="utf-8")
            events = [_event(stage) for stage in ("read_input", "fetch", "identify")]
            events.append(_event("plan", result="fail", details={
                "request_number": 1, "model_id": "test/model",
                "usage": {"verified": False},
            }))
            events.append(_event("generate", details={
                "request_number": 2, "model_id": "test/model",
                "usage": {"prompt_tokens": 7, "completion_tokens": 11,
                          "total_tokens": 18, "reasoning_tokens": 3, "verified": True},
            }))
            events.extend([_event("check"), _event("final", details={"exit_code": 0})])
            (output / "trace.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
            report = validate_output(output, expected_model="test/model")
            self.assertEqual(report["attempts"], 2)
            self.assertEqual(report["usage"]["unknown_calls"], 1)
            self.assertFalse(report["usage"]["verified"])
            self.assertIsNone(report["usage"]["scored_tokens"])
            self.assertEqual(report["flow_evidence"]["planning_attempts"], 1)
            self.assertFalse(report["flow_evidence"]["planning_response_received"])
            self.assertEqual(report["flow_evidence"]["effective_flow"], "single")

    def test_final_result_must_agree_with_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            (output / "index.html").write_text(
                "<html><body><script>const x=1;</script></body></html>", encoding="utf-8")
            events = [_event(stage) for stage in ("read_input", "fetch", "identify", "plan", "generate", "check")]
            events.append(_event("generate", details={"request_number": 1, "model_id": "test/model",
                "usage": {"prompt_tokens": 1, "completion_tokens": 2, "verified": True}}))
            events.append(_event("final", details={"exit_code": 1}))
            (output / "trace.jsonl").write_text(
                "".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
            report = validate_output(output)
            self.assertFalse(report["ok"])
            self.assertIn("final event result disagrees with exit_code", report["failures"])

    def test_repeat_summary_preserves_each_failure_repair_and_flow(self) -> None:
        rows = [
            {"case": "case.json", "model_id": "test/model", "flow": "planned", "repeat": 1,
             "status": "pass", "exit_code": 0, "elapsed_seconds": 12.5, "attempts": 3,
             "usage": {"scored_tokens": 42}, "failures": [],
             "repairs": [{"number": 1, "outcome": "accepted"}],
             "flow_evidence": {"effective_flow": "planned"}},
            {"case": "case.json", "model_id": "test/model", "flow": "planned", "repeat": 2,
             "status": "fail", "exit_code": 1, "elapsed_seconds": 8.25, "attempts": 1,
             "usage": {"scored_tokens": None}, "failures": ["check failed"],
             "repairs": [], "flow_evidence": {"effective_flow": "single"}},
        ]
        summary = summarize_repeats(rows)
        self.assertEqual((summary[0]["passed"], summary[0]["failed"]), (1, 1))
        self.assertEqual(summary[0]["runs"][1]["failures"], ["check failed"])
        self.assertEqual(summary[0]["runs"][0]["repairs"][0]["outcome"], "accepted")
        self.assertEqual(summary[0]["runs"][1]["flow_evidence"]["effective_flow"], "single")

    def test_remote_asset_and_missing_trace_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            (output / "index.html").write_text(
                '<html><body><script src="https://cdn.example/a.js"></script></body></html>',
                encoding="utf-8")
            report = validate_output(output)
            self.assertFalse(report["ok"])
            self.assertTrue(any("external" in failure for failure in report["failures"]))
            self.assertTrue(any("trace.jsonl" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main()
