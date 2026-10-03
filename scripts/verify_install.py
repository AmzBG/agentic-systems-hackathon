"""Prove a clean Python 3.11, wheel-only install and bounded QuickJS execution."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROBE = r"""
import quickjs
context = quickjs.Context()
context.set_memory_limit(8 * 1024 * 1024)
context.set_time_limit(0.05)
assert context.eval('1 + 2') == 3
try:
    context.eval('while (true) {}')
except quickjs.JSException as exc:
    assert 'interrupted' in str(exc).lower() or 'timeout' in str(exc).lower(), str(exc)
else:
    raise AssertionError('infinite loop was not interrupted')
print('QuickJS calculation and execution limit passed')
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    default_python = ["py", "-3.11"] if sys.platform == "win32" else ["python3.11"]
    parser.add_argument("--python", nargs="+", default=default_python,
                        help="Python 3.11 launcher words, e.g. py -3.11")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if args.timeout < 1:
        parser.error("timeout must be positive")
    with tempfile.TemporaryDirectory(prefix="paper-playground-install-") as temp:
        venv = Path(temp) / "venv"
        commands = [
            [*args.python, "-m", "venv", str(venv)],
        ]
        for command in commands:
            try:
                subprocess.run(command, cwd=ROOT, check=True, timeout=args.timeout)
            except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                print(json.dumps({"ok": False, "step": "create_venv", "error": type(exc).__name__}))
                return 1
        python = venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        steps = [
            ("version", [str(python), "-c", "import sys; assert sys.version_info[:2] == (3, 11), sys.version"]),
            ("wheel_only_install", [str(python), "-m", "pip", "install", "--only-binary=:all:",
                                    "-r", str(ROOT / "requirements.txt")]),
            ("quickjs_limits", [str(python), "-c", PROBE]),
        ]
        for name, command in steps:
            try:
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                        timeout=args.timeout)
            except (OSError, subprocess.TimeoutExpired) as exc:
                print(json.dumps({"ok": False, "step": name, "error": type(exc).__name__}))
                return 1
            if result.returncode:
                print(json.dumps({"ok": False, "step": name, "exit_code": result.returncode,
                                  "stderr_tail": result.stderr[-2500:]}, indent=2))
                return 1
            print(f"{name}: pass", flush=True)
    print(json.dumps({"ok": True, "python": "3.11", "wheel_only": True,
                      "quickjs_time_limit": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
