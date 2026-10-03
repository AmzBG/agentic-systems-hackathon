# User 3 → User 1 core decisions — 3 October 2026

Initially inspected `c44e81bc9efdaa2d94ab4fff9e3a3a833a00a701`, then synced `3f71ba46124cf77a22addccfffad41cb7da9d71b` during review. No paid calls. Reproduction: `.venv/Scripts/python.exe scripts/review_core_evidence.py`; core regression suite: `.venv/Scripts/python.exe -m unittest tests.test_core -q` → initially 65 pass in 6.903 s; after sync 67 pass in 6.972 s. This is offline inspection, not a new model run or browser review.

Integrated suite at `3f71ba4`: 142 pass in 25.947 s. Later `fbb880d` model-profile/routing checkpoint was merged and the affected core suite rerun: 67 pass in 6.974 s. No live routing or model-quality result is inferred from those offline tests. Repository audit and diff whitespace checks pass. The prior clean-clone installation proof does not cover these new core revisions.

## Contract and inbox decisions

U1-U3-007/008 are already DONE (`ba4c462`, `df66028`); no duplicated implementation/runs. U3-U1-001 is now DONE upstream (`8e72536`); specific fetch-failure reasons replace the opaque error, so it is not a new blocker. U1-U3-009: accept corrections 1–5 and 7, including optional revision version=1 and ignoring unrequested compute. Accept item 6's aggregate output cap, but its current input wording is still inconsistent: **all numeric input leaves**, including number/slider controls, must count, not just vector/matrix leaves. Reproduction below establishes the conflict. U1 must coordinate this wording across frozen docs; AI.md's older full-schema paragraph also still says three delimiter pairs, whereas the accepted correction says two.

U1-U3-010/011 remain ACK, not DONE: scientific repair details and Attention provenance are reported by U1, but their artifact bundles are unavailable here. U3-U1-003 remains OPEN requesting those existing artifacts. U2-U3-004 is DONE (`eaff15d`): checker output shape/aggregate limits, real QuickJS regressions and 140-test suite verified. Do not reopen it as a current checker defect.

## Flow decision ready

Only model: `deepseek/deepseek-v4.1-flash`, reasoning `low`. Retain **single**; planned remains opt-in. Evidence published in `df6602887b6f0383337d812e88dbc68171688c2f`, with all four sanitized traces under `paired_entropy/`. Historical implementation is documented as after `7eaaeeed446197243f4e697170b9ce613712c94e`, before later `b569145`; a docs-only checkpoint occurred between pairs. Traces do not independently stamp exact run HEAD, so do not imply current-version generation or invent a more precise per-run SHA.

| Pair / flow | Requests | Prompt | Completion | Reasoning subset | Wall s | Trace s | Current offline reinspection |
|---|---:|---:|---:|---:|---:|---:|---|
| 1 single | 1 | 7,102 | 13,018 | 9,993 | 50.937 | 50.610 | Validator + entropy oracle PASS |
| 1 planned | 2 | 12,912 | 10,214 | 7,588 | 39.031 | 38.625 | Validator + entropy oracle PASS |
| 2 single | 1 | 5,560 | 9,602 | 7,403 | 45.016 | 43.938 | Validator + entropy oracle PASS |
| 2 planned | 3 | 19,741 | 16,590 | 9,959 | 64.047 | 63.578 | Validator + entropy oracle PASS; one accepted full regeneration |

Single totals: 2 requests, 12,662 prompt + 22,620 completion = 35,282 scored tokens, 95.953 wall s. Planned totals: 5 requests, 32,653 prompt + 26,804 completion = 59,457 scored tokens, 103.078 wall s. All usage verified, zero unknown calls; reasoning is included in completion. Both planned traces show received plans, not fallback-to-single. All four final traces report success; initial failure/repair history is retained, not erased by final success.

Limits: only two repetitions of one mechanism; unequal fetched source lengths; no blind teaching score, comprehensive source review or real-browser QA. No statistically reliable latency or generalization claim. Planning costs 68.5% more scored tokens without demonstrated benefit on these checks. Current validation/oracle reinspection of old pages does not test today's renderer generation.

## Attention: next action, not a certified success

Local inventory has the handwritten Attention fixture and rendered fixture page, but no `out/attention_live/trace.jsonl`, successful post-fix production page or raw/recoverable spec. U1-U3-011 explicitly reports its 156.2 s/one-request run as pre-`5f98617`, lacking the reasoning field, with numerical execution skipped/degraded. Therefore it does **not** prove the low-reasoning fix, current checker/renderer or browser UX.

User 1 is the sole coordinator/executor of any necessary live rerun; User 3 will not start a simultaneous run. First supply the existing claimed post-fix bundle with producing SHA, model/reasoning/flow, full sanitized trace and recoverable spec. If none covers the relevant current code, perform exactly one Attention run on pinned Python 3.11 with `--reasoning low --flow single`, a fresh output directory and SHA recorded beside it. Validate and share that bundle. Admission fixes are now verified below. Numerical verification and permitted browser verification are separate gates; the known administrator browser denial must not be bypassed.

## Invariant repair analysis (conditional on U1's report)

Original/replacement specs and revision responses are missing. Exact original minima, removed invariant identities and producing SHAs cannot be independently recovered. The following is mathematical assessment of the reported changes, not certification of the actual repair diff.

| Mechanism | Reported original → replacement | Independent justification / verdict |
|---|---|---|
| Least squares | One-sided range(s), missing finite upper bound → maxima 1,225 / 2,500; invariant count ≥3 → 2 | If each of two residuals satisfies absolute value ≤35, its square ≤1,225 and SSE ≤2,450. A 2,500 SSE upper bound is conservative and valid. Adding a missing required bound repairs invalid schema, not a wrong scientific test. Dropping an invariant reduces coverage; without its identity, equivalence cannot be certified. The control-domain assumption still needs the actual spec. |
| Exponential decay | One-sided range(s) → remaining amount max 1,000, half-life max 1e6, ratio max 100; invariant count 5 → 4 | For N0≤1,000 and nonnegative rate/time, N=N0 exp(-lambda t)≤1,000. If lambda≤1 and t≤50, t/half-life=t lambda/ln(2)≤72.134752, so 100 is conservative. At lambda=0 the physical half-life is infinite, not 1e6. A finite sentinel and a test locking it in validate an artificial convention, not the physical quantity. Thus this repair fixes syntax but preserves a scientific problem unless that convention is explicitly separate from the half-life claim. Dropping an unknown invariant weakens unverified coverage. |

Independent finite checks: lambda=0.2 → half-life 3.4657359028; t=5 → remaining fraction exp(-1)=0.3678794412. These are computed directly by the inspection script, not taken from generated tests. Requested evidence: before/after invariants, controls/ranges, compute and tests; identify removed identities and zero-rate presentation before declaring the repairs scientifically sound.

## Core admission gaps — reproduced, then fixed upstream

Affected current code `c44e81b`; reproduction script uses real QuickJS for probes, no patched transport, network or model call. There is no API trace for these local function-level reproductions; the sanitized stdout is the evidence.

Resolution: `4522c0e` / test correction `3f71ba4` arrived during review. The same script now shows core and runtime both reject 129 input leaves, the core axis probe fails with bounded numeric shape, and the extra-key probe fails with returned versus declared IDs. These are no longer current implementation blockers. Contract wording still needs the coordinated all-numeric-input update; do not request duplicate fixes.

1. **Parser input cap:** neutral `toy_spec()` changed to two 8x8 matrix controls plus its scalar gain (129 numeric leaves), with shape-valid presets. `spec_parser.validate_spec` accepts; `runtime.validate_spec` rejects `Total input numeric leaf limit is 128`. Expected: core rejects before renderer; count all numeric controls. Already routed in U2-U1-003; not a new runtime defect.
2. **Core output axis:** `compute(inputs){return {scaled:Array(9).fill(inputs.gain),total:6};}` in neutral spec. `agent.page_compute_check` reports pass (five interpreter probes). Expected: output axis >8 rejected using runtime.numeric_shape. Current checker rejects bounded-shape violations, so this is a redundant core guard gap, not proof the integrated agent still exits successfully.
3. **Core exact output keys:** neutral compute with an extra `note:42` output also receives a passing core probe. Expected: set of returned keys equals declared outputs, not only a missing-key check. Standalone checker already rejects extra outputs. This is core/runtime admission disagreement, not a paid-run failure.

No new budget/client/repair-loop defect was established by the 65 passing core tests; this is bounded regression evidence, not an exhaustive audit. Source-unreachable model quality remains unmeasured: the previous live attempt was interrupted and usage unknown, not a zero-cost pass.

## Coverage and ownership

No second model ID has been selected or tested. Confidence in model-independent/generic prompts therefore rests on one model only; six input fixtures do not establish six verified generated successes. Do not invent MODEL_B or spend the personal key without coordination. Preserve this gap explicitly; prioritize current Attention and hidden-like artifact review first.

Next for User 1: coordinate the input-cap contract wording; supply existing Attention/repair bundles; run at most one coordinated current-version Attention generation only if existing evidence is insufficient. User 3 then verifies supplied artifacts; User 2 owns permitted real-browser QA. No speculative optimization is justified yet.
