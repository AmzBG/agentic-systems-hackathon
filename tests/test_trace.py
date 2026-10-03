import json
import time
from pathlib import Path

from paper_playground.trace import TraceWriter


def test_trace_is_jsonl_with_required_fields(tmp_path: Path) -> None:
    path = tmp_path / "trace.jsonl"
    trace = TraceWriter(path, time.monotonic())
    trace.emit("test", "write", "ok", count=1)
    event = json.loads(path.read_text(encoding="utf-8"))
    assert event["stage"] == "test"
    assert event["action"] == "write"
    assert event["result"] == "ok"
    assert event["count"] == 1

