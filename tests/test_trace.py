import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from trace import write_trace


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

