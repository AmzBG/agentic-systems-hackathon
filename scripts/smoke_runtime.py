"""Render a schema fixture through User 2's production renderer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    try:
        from runtime import render
    except ImportError:
        print("runtime.py is not available yet; User 2 owns the renderer.", file=sys.stderr)
        return 2
    html = render(spec)
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / "index.html"
    target.write_text(html, encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

