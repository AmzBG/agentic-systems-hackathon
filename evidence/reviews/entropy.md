# Entropy review — 3 October 2026

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
