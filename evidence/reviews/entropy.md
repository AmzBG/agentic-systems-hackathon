# Entropy review — 3 October 2026

Current factual override: the refreshed tracked showcase is generation84c31ac, one request/no repairs,7995 prompt+9922 completion=17917 total (7055 reasoning included),46.609 trace seconds, exit0/nondegraded. Older three-request metrics below describe the superseded showcase, not the current file. U2's e7fefcc browser QA genuinely tested this refreshed page; U3 recomputed SHA256 `ed4d813f62cb0d1fc2199803a5144cf89a8dc4902415b140a8a6591851d1723d`, matching `../browser_qa_20261003/environment.json`. Tested load/controls/both presets/visuals/console/invalid retention/keyboard and three widths PASS as U2 observations. Fully network-disabled remains UNVERIFIED; original artifact/current-css-only retests do not certify newest runtime/workbench. U3 did not perform a new browser run. Details, screenshots and exact scope: `../browser_qa_20261003/README.md`. Prior BLOCKED/browser paragraphs below are historical and superseded only for those observed checks.

Reviewed repository implementation: `faa6de3`. This extends `evidence/REVIEW_TEMPLATE.md`; it is not a browser pass or an instructor score.

| Field | Evidence |
|---|---|
| Case / output | `examples/entropy/case.json`; `examples/entropy/index.html` |
| Model / reasoning / flow | `deepseek/deepseek-v4.1-flash`; low; single |
| Trace / attempts / elapsed | Tracked `trace.jsonl`; 3 requests; 64.156 s |
| Prompt / completion / reasoning subset | 12,632 / 14,583 / 10,063 tokens; verified by validator |
| Scored tokens | 27,215; reasoning is already inside completion |
| Repair outcomes | Targeted invariants repair 1 parse failed; repair 2 accepted |
| Final result | Original trace exit 0; current validator passes; independent page-interpreter oracle passes all six comparisons |
| Repeat evidence | See `../paired_entropy/README.md`; no new generation this review |

## Independent scientific review

Compared page text and readouts with [Shannon, Section 6, printed pages 10–11](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf). PASS within the stated discrete-distribution scope: the entropy equation, certainty condition and uniform maximum match the source. Symbols distinguish raw weights, probabilities, contributions and total bits. Hand calculation for four equal outcomes gives probabilities 0.25, contributions 0.5 bits each and total 2 bits; certainty gives zero. The independent interpreter oracle reproduces these, including zero contributions.

The normalization, six-slot vector, all-zero fallback and singleton redundancy convention are explicitly teaching choices, not source results. The two predictions lead to contrasting distributions and explain their intermediate contributions. No scientific correction identified in this narrow review; source coding, temporal dependence and general entropy rates were not reviewed.

## Browser checks

BLOCKED: earlier in-app-browser access was denied by an administrator-enforced security policy. No browser was exercised in this reconciliation; no alternative was used to bypass that denial.

All template browser checks remain SKIP: network-disabled Chromium loading; initial layout and units; visible response to controls 1 and 2; both exploration buttons; edge and invalid edits; console errors; keyboard/focus; desktop/tablet/mobile readability; runtime network activity. Source comparison above is a text/science check, not a browser observation. Static locality validation does not prove offline browser behavior.

## Estimate and unresolved warnings

No rubric score or quality-gated efficiency winner assigned without UX evidence. User 2 owns browser verification. The showcase is a real earlier production run, not a new `faa6de3` generation; current offline validation does not retroactively prove a current-generation run.
