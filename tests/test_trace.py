import json
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from paper_playground.trace import TraceWriter
from trace import write_trace


def test_trace_is_jsonl_with_required_fields(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    trace = TraceWriter(path, time.monotonic())
    trace.emit("test", "write", "ok", count=1)
    event = json.loads(path.read_text(encoding="utf-8"))
    assert event["stage"] == "test"
    assert event["action"] == "write"
    assert event["result"] == "ok"
    assert event["count"] == 1


class ContractTests(unittest.TestCase):
    def test_event_shape_append_and_redaction(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "trace.jsonl"
            for action in ("start", "finish"):
                write_trace(
                    str(path),
                    {
                        "stage": "run",
                        "action": action,
                        "result": "info",
                        "elapsed_seconds": 1.5,
                        "details": {
                            "model": "deepseek/deepseek-v4.1-flash",
                            "Authorization": "Bearer should-not-appear",
                            "note": "Bearer should-also-not-appear",
                            "reasoning": "private reasoning should-not-appear",
                            "prompt": "raw prompt should-not-appear",
                        },
                    },
                )
            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            events = [json.loads(line) for line in lines]
            required = {
                "stage", "action", "result", "prompt_tokens", "completion_tokens",
                "elapsed_seconds", "checks", "failures", "revisions", "details",
            }
            self.assertEqual(set(events[0]), required)
            self.assertIsNone(events[0]["prompt_tokens"])
            self.assertNotIn("Authorization", events[0]["details"])
            self.assertNotIn("should-not-appear", "\n".join(lines))
            self.assertNotIn("should-also-not-appear", "\n".join(lines))

