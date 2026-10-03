"""Load and validate hackathon case files."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


class CaseInputError(ValueError):
    """Raised when a case file does not meet the known input contract."""


@dataclass(frozen=True)
class CaseInput:
    source_url: str
    focus: str
    audience: str
    extra: dict[str, str]

    def supplied_source_text(self) -> str | None:
        """Support likely excerpt fields until the five-field schema is clarified."""
        for name in ("excerpt", "source_text", "paper_excerpt"):
            value = self.extra.get(name, "").strip()
            if value:
                return value
        return None


def load_case(path: Path) -> CaseInput:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CaseInputError(f"Input file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CaseInputError(f"Input is not valid UTF-8 JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise CaseInputError("Input JSON must be an object.")

    non_strings = sorted(key for key, value in payload.items() if not isinstance(value, str))
    if non_strings:
        raise CaseInputError(
            "Every case field must be a string; invalid fields: " + ", ".join(non_strings)
        )

    required = ("source_url", "focus", "audience")
    missing = [name for name in required if not payload.get(name, "").strip()]
    if missing:
        raise CaseInputError("Missing required non-empty fields: " + ", ".join(missing))

    source_url = payload["source_url"].strip()
    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise CaseInputError("source_url must be an absolute HTTP(S) URL.")

    extra = {key: value for key, value in payload.items() if key not in required}
    return CaseInput(
        source_url=source_url,
        focus=payload["focus"].strip(),
        audience=payload["audience"].strip(),
        extra=extra,
    )

