"""Minimal JSONL execution trace with no prompts, credentials, or hidden reasoning."""

from __future__ import annotations

import json
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class TraceWriter:
    def __init__(self, path: Path, started_at: float) -> None:
        self.path = path
        self.started_at = started_at
        self._lock = threading.Lock()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")

    def emit(self, stage: str, action: str, result: str, **details: Any) -> None:
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "elapsed_seconds": round(time.monotonic() - self.started_at, 3),
            "stage": stage,
            "action": action,
            "result": result,
            **details,
        }
        serialized = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with self._lock, self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(serialized + "\n")

