"""Focused evidence checks that distinguish real usage from missing evidence."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
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
            events.extend([_event("check", result="fail"), _event("revision"), _event("check"), _event("final")])
            (output / "trace.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")
            report = validate_output(output, expected_model="test/model")
            self.assertTrue(report["ok"], report["failures"])
            self.assertEqual(report["attempts"], 1)
            self.assertEqual(report["usage"]["completion_tokens"], 20)
            self.assertEqual(report["usage"]["reasoning_tokens"], 5)

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
