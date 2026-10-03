# Attention review — 3 October 2026

Reviewed repository implementation: `faa6de3`. This extends `evidence/REVIEW_TEMPLATE.md`; it is not a generated-output or browser pass.

| Field | Evidence |
|---|---|
| Case | `examples/attention/case.json` |
| Reviewed content | `practice/specs/attention.json` and its local rendered `out/attention/index.html` |
| Artifact provenance | Handwritten practice fixture, NOT User 1's successful generated Attention output |
| Model / reasoning / requests / usage / elapsed / repair | N/A for fixture; generated-run evidence unavailable locally |
| Generated-output validation / repeats | SKIP; no supplied production artifact and trace to inspect |

## Independent scientific review

Compared fixture explanation, symbols and examples with [Vaswani et al., Section 3.2.1, equation (1)](https://arxiv.org/html/1706.03762v7). PASS for fixture fidelity: row-wise softmax of scaled query/key dot products mixes value rows. Q, K, V and key dimension are defined; scores and normalized weights are explicit intermediates. Independent arithmetic with identity matrices and key dimension 2 gives diagonal score 0.7071067812 and diagonal weight 0.6697615493. Without scaling the weight becomes 0.7310585786. Equal scores give weights 0.5/0.5 and, for values [2,0] and [0,4], output [1,2]. A score gap 4/sqrt(2) gives first-key weight 0.9441927808. These agree with fixture expectations.

The fixed 2x2 matrices are marked as simplifications; masking, learned projections, multiple heads and training are explicitly excluded. Both explorations request predictions and explain the resulting mixtures. No fixture science defect identified; generated Attention fidelity remains unverified.

## Browser checks

BLOCKED: earlier in-app-browser access was denied by an administrator-enforced security policy. No browser was exercised in this reconciliation and no bypass was attempted.

All template browser checks remain SKIP: offline Chromium loading; initial layout/units; Q/K/V edits and scaling toggle visibly affecting results; both preset buttons; updated intermediates; invalid/extreme edits; console; keyboard/focus; desktop/tablet/mobile widths; network activity. A JavaScript harness is not browser QA.

## Estimate and unresolved warnings

No rubric score or efficiency winner assigned. User 1 must supply the existing successful generated Attention page/trace and four hidden-like case artifacts; no duplicate paid calls requested. User 2 owns browser verification. A fixture review cannot close the generated-output requirement.
