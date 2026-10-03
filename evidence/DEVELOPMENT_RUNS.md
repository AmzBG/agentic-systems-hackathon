# Development run evidence

These are development observations, not scores or a claim that a generated page passed browser review. Each live run must keep its own outcome, including failures. Reasoning tokens are already within completion tokens.

| Run | Input / model | Flow and renderer | Attempts | Prompt / completion / reasoning subset | Elapsed | Result and repairs |
|---|---|---|---:|---:|---:|---|
| U1 2026-10-03 12:49 Beirut | `examples/entropy/case.json`; `deepseek/deepseek-v4.1-flash` (served model matched) | Real agent, repairs disabled; stand-in page, no `runtime.py`. Planning status not recorded. | 1 | 6,916 / 9,002 / 6,126; verified scored total 15,918 | 117 s process; 114 s model call; fetch 3.0 s | Exit 1. Wire parsed on first response, then `spec_schema` rejected blank `units` on toggle control `equalize`; numerical checks skipped. No repair was attempted. This is **not** a validated page result. |

Source: User 1's `U1-U3-006` inbox report, recorded before core fix `fe80fca`. The fix requires nonblank strings, prompts `unitless` when appropriate, raises generation/repair ceilings, and permits field-level repairs. Re-run with the real renderer to learn whether those changes reach and pass numerical and browser checks. Do not count this one failed development run as repeated-run or flow-comparison evidence.

No second live repeat, planned-flow comparison, scientific-critic comparison, or real-browser result is recorded yet. A flow decision remains provisional until paired runs have measured quality and cost.

## Offline integration after renderer merge

On the synchronized `main`, both `scripts/smoke_runtime.py` fixture commands exit 0 and write ignored `out/entropy/index.html` and `out/attention/index.html`. The project Python 3.11 environment runs `python -m unittest discover -s tests -q` with 110 tests passing. User 2 separately reports entropy 12 and attention 10 self-check passes in a bounded JavaScript/DOM test harness; those are not Chromium results.

Real-browser review was attempted via a localhost server, but the available browser denied access because its admin-enforced security check could not be verified. No browser networking, layout, keyboard, console, or clipping result is claimed; do not work around that browser policy. A verified agent-generated public example output is also still missing (`scripts/audit_repo.py` reports only `no public example output HTML`).
