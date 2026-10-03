# Generated Attention review — 3 October 2026

This supersedes the fixture-only limitation of the prior review. Reviewed retained real generation: `evidence/u1-runs/stage2/T-attention-4/{index.html,trace.jsonl,spec.json}`, supplied by U1 at d5bab9e. U1's manifest identifies producing SHA `fc2844f5101ba343410929462246fb41e9c26f87`; the trace itself does not stamp Git SHA, so provenance is owner-reported, not independently recoverable from trace. It predates later prompt/repair/default-routing changes and is NOT a final-current-code generation.

## Trace and independent calculation

Current validator PASS:9 events, exit0, degraded=false, one request, zero repairs. Actual trace: model and served model `deepseek/deepseek-v4.1-flash`, low reasoning, provider sort throughput, served Together; prompt6787/completion9192/total15979, reasoning6034 already included in completion. API41.75s, final cumulative43.641s; U1's manifest wall44.6s is a different measure, not a contradiction. No planning request occurred.

`python scripts/check_attention_oracle.py --output evidence/u1-runs/stage2/T-attention-4` independently calculates QK^T/divisor, stable row-wise softmax and weights*V using Python math, then compares every declared output via bounded QuickJS on the delivered AST. Six trials PASS: defaults, both actual presets, scaled identity, unscaled identity, zero-query averaging. Detailed inputs/expected/observed are in `attention_oracle.json`; none of its expected values come from generated tests. Identity key dimension2 gives diagonal score.7071067812, weight.6697615493; scaling off gives.7310585786. Zero scores mix V=[[2,0],[0,4]] into [1,2] for each query.

## Scientific, teaching and grounding review

Compared visible teaching and grounding to [Vaswani et al., Section3.2.1 equation1](https://arxiv.org/html/1706.03762v7): core computation matches scaled scores→row-normalized weights→value mixture. Q/K/V,d_k,S,A,O and divisor are defined. Score/weight heatmaps, row-sum bars and peak-weight scale sweep are coherent. Editable matrices, scaling toggle and scale slider are meaningful for this toy setup. Equal-keys preset gives uniform rows; dominant unscaled first-row scores[6,0] give weights[.997527,.002473]. FROM PAPER claims about scaling and dot products are supported; 2x2 matrices/peak statistic are explicitly SIMPLIFICATION, not paper experiment results. The limitation honestly says varying d_k independently of fixed matrix width is a toy numerical-scale experiment, not true change in feature dimension; accept only under that disclosure. No invented source locator found in inspected entries.

Concrete warnings, routed to U1: A1 second exploration says the entire O is almost the first value vector, but only its FIRST query row is; second row is [.268941,.731059] for identity V. A2 K-help says it changes row sums, which should remain1; equal scores/d_k=1 are counterexamples to unconditional “sharper/falls” control help. A3 invariant named “each attention row sums to one” actually sums the rowsums vector to2: [0,2] could satisfy it without either row being1. Our independent comparisons check each weight/row sum, but that does not cure the invariant's misleading name/coverage. Prefer row_sum on weights or per-leaf range around1. These are generated teaching/validation-coverage warnings, not a failed interpreter or numeric run.

## Browser evidence — pending User2

No actual browser was exercised by U3 this turn. U2's current notes contain AST/DOM-double evidence, not real Chromium PASS. Offline/network/CSP, layout, keyboard/focus, matrix edits/toggle/preset buttons, invalid-edit state and narrow-width behavior stay SKIP/BLOCKED until U2 supplies observations with artifact path/hash, runtime/commit, browser/version, performed actions/results and screenshots/console/network evidence where available. Preserve U2's provenance separately from U3 static/numerical checks; an untested item remains SKIP.

No rubric score assigned. Historical generated-output availability and numerical proof are now resolved for this selected artifact; final-version Attention acceptance and browser QA remain gates. No paid Attention call or rerun was made by U3.
