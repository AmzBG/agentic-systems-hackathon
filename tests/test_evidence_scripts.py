"""Focused evidence checks that distinguish real usage from missing evidence."""

from __future__ import annotations

import json
import math
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from run_all import summarize_repeats  # noqa: E402
from check_entropy_oracle import _near_active_vector  # noqa: E402
from validate_output import validate_output  # noqa: E402
from check_practice_oracles import verify_page  # noqa: E402
from check_attention_oracle import expected_attention, verify_attention_page  # noqa: E402


def _event(stage: str, *, result: str = "pass", details: dict | None = None) -> dict:
    return {"stage": stage, "action": stage, "result": result,
            "prompt_tokens": None, "completion_tokens": None, "elapsed_seconds": 1.0,
            "checks": [], "failures": [], "revisions": [], "details": details or {}}


class EvidenceScriptTests(unittest.TestCase):
    def test_attention_fixture_exploration_isolates_scaling(self) -> None:
        from runtime import merge_inputs, render
        spec = json.loads((ROOT / 'practice/specs/attention.json').read_text(encoding='utf-8'))
        preset = spec['explorations'][0]['preset']
        self.assertEqual(preset, {'scale': False})
        defaults = {c['id']: c['default'] for c in spec['controls']}
        trial = merge_inputs(spec['controls'], preset)
        for key in ('queries', 'keys', 'values'):
            self.assertEqual(trial[key], defaults[key])
        with tempfile.TemporaryDirectory() as temp:
            page = Path(temp) / 'index.html'
            page.write_text(render(spec), encoding='utf-8')
            for scaled in (True, False):
                diagonal = 1 / math.sqrt(2) if scaled else 1
                weight = math.exp(diagonal) / (math.exp(diagonal) + 1)
                expected = {'score_matrix': [[diagonal, 0], [0, diagonal]],
                            'attention_weights': [[weight, 1-weight], [1-weight, weight]],
                            'attended_values': [[weight, 1-weight], [1-weight, weight]]}
                report = verify_page(page, {'scale': scaled}, expected)
                self.assertTrue(report['ok'], report)

    def test_entropy_fixture_exposes_normalization_and_contribution_equations(self) -> None:
        spec = json.loads((ROOT / 'practice/specs/entropy.json').read_text(encoding='utf-8'))
        explanation = spec['starting_point']['explanation']
        for equation in ('p_i = w_i / sum(w)', 'c_i = -p_i log2(p_i)', 'H = sum(c_i)', 'p_i = 1/n'):
            self.assertIn(equation, explanation)

    def test_independent_attention_uniform_and_scaled_identity(self) -> None:
        inputs = {'q': [[0, 0], [0, 0]], 'k': [[1, 0], [0, 1]],
                  'v': [[2, 0], [0, 4]], 'dk': 2, 'scale_on': True}
        self.assertEqual(expected_attention(inputs)['output'], [[1, 2], [1, 2]])
        identity = {**inputs, 'q': [[1, 0], [0, 1]]}
        self.assertAlmostEqual(expected_attention(identity)['weights'][0][0], 0.6697615493266569)
        report = verify_attention_page(ROOT / 'evidence/u1-runs/stage2/T-attention-4/index.html')
        self.assertTrue(report['ok'], report)
        self.assertEqual(len(report['trials']), 6)

    def test_attention_oracle_infers_key_width_without_dk_control(self) -> None:
        inputs = {'q': [[1, 0], [0, 1]], 'k': [[1, 0], [0, 1]],
                  'v': [[2, 0], [0, 4]], 'scale_on': True}
        self.assertAlmostEqual(expected_attention(inputs)['scores'][0][0], 1 / math.sqrt(2))
        report = verify_attention_page(ROOT / 'evidence/u1-runs/final-93f7521/attention/index.html')
        self.assertTrue(report['ok'], report)
        self.assertEqual(len(report['trials']), 6)
        self.assertEqual(set(report['trials']['default']['checks']),
                         {'scores', 'weights', 'row_sums', 'output'})

    def test_page_oracle_rejects_wrong_independent_expectation(self) -> None:
        from runtime import render
        spec = json.loads((ROOT / 'practice/specs/entropy.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            page = Path(temp) / 'index.html'
            page.write_text(render(spec), encoding='utf-8')
            # Test the comparison machinery, not a model-provided expected value.
            payload = __import__('check_entropy_oracle')._runtime_payload(page.read_text(encoding='utf-8'))
            output_id = payload['spec']['outputs'][0]['id']
            self.assertFalse(verify_page(page, {}, {output_id: 999999})['ok'])
            self.assertFalse(verify_page(page, {}, {})['ok'])

    def test_decay_oracle_uses_independent_finite_rate_math(self) -> None:
        cases = json.loads((ROOT / "practice" / "oracles" / "core_identities.json").read_text(
            encoding="utf-8"))["cases"]
        self.assertEqual(len(cases), 6)
        reference = cases["exponential_decay"]["finite_rate_reference"]
        inputs = reference["inputs"]
        expected = reference["expected"]
        self.assertEqual((inputs["initial"], inputs["lambda"], inputs["time"]), (80, 0.2, 5))
        self.assertAlmostEqual(expected["half_life"], math.log(2) / inputs["lambda"])
        self.assertAlmostEqual(expected["remaining_fraction"], math.exp(-inputs["lambda"] * inputs["time"]))
        self.assertAlmostEqual(expected["amount"], inputs["initial"] * expected["remaining_fraction"])

    def test_decay_oracle_zero_rate_is_infinite_not_finite_sentinel(self) -> None:
        reference = json.loads((ROOT / "practice" / "oracles" / "core_identities.json").read_text(
            encoding="utf-8"))["cases"]["exponential_decay"]["zero_rate_reference"]
        self.assertEqual(reference["inputs"]["lambda"], 0)
        self.assertEqual(reference["expected"]["half_life"], "infinity")
        self.assertEqual(reference["expected"]["remaining_fraction"], math.exp(0))
        self.assertEqual(reference["expected"]["amount"], reference["inputs"]["initial"])

    def test_independent_oracle_allows_only_zero_inactive_slots(self) -> None:
        self.assertTrue(_near_active_vector([0.5, 0.5, 0, 0], [0.5, 0.5]))
        self.assertFalse(_near_active_vector([0.5, 0.5, 0.1], [0.5, 0.5]))

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

    def test_repeat_summary_keeps_reasoning_modes_separate(self) -> None:
        rows = [
            {"case": "case.json", "model_id": "test/model", "flow": "single",
             "reasoning": mode, "repeat": 1, "status": "pass", "usage": {}}
            for mode in ("low", "off")
        ]
        summary = summarize_repeats(rows)
        self.assertEqual({item["reasoning_requested"] for item in summary}, {"low", "off"})
        self.assertTrue(all(item["passed"] == 1 for item in summary))

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
