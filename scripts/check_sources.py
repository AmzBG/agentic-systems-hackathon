"""Check whether the real agent can extract text from the six practice URLs.

This is a read-only, no-model-call development check. It does not equate a
successful fetch with verified scientific grounding; see each case's locator.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent import fetch_source  # noqa: E402


def main() -> int:
    # pypdf can emit verbose optional-font warnings for otherwise readable PDFs.
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    cases = sorted({*ROOT.glob("examples/*/case.json"), *ROOT.glob("practice/cases/*.json")})
    results = []
    for path in cases:
        case = json.loads(path.read_text(encoding="utf-8"))
        source = fetch_source(case["source_url"], case["focus"])
        results.append({
            "case": path.relative_to(ROOT).as_posix(),
            "status": source.get("status"),
            "kind": source.get("kind"),
            "chars": source.get("chars", 0),
            "truncated": source.get("truncated", False),
            "seconds": source.get("seconds"),
            "error": source.get("error"),
        })
    print(json.dumps(results, indent=2))
    return 0 if all(item["status"] == "ok" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
