# Independent screening and integration review — 3 October 2026

Decision: retain **single flow, auto → low reasoning**. No User 3 paid calls.
Six runs were generated at `27f581ae202f7681bc86db07a56326defa504ab9`,
not at subsequent recovery/renderer/checker revisions. Originals and traces remain
under `u1-runs/screen-27f581a/`. `screening_independent.json` maps each named
output to an independent Python calculation, including defaults, presets,
model tests and extra edge cases. Reproduce with `python scripts/review_screening.py`.

| Run | Condition | Exit | Requests | Repairs accepted/attempted | Prompt | Completion (reasoning subset) | Total | Seconds |
|---|---|---:|---:|---|---:|---:|---:|---:|
| SCR-1 Attention | low | 0 | 1 | 0/0 | 7156 | 15948 (12404) | 23104 | 56.687 |
| SCR-2 Attention | off | 1 | 3 | 0/2 | 19827 | 8224 (0) | 28051 | 29.500 |
| SCR-3 Entropy | off | 0 | 1 | 0/0 | 6669 | 2491 (0) | 9160 | 12.188 |
| SCR-4 Entropy | low | 0 | 1 | 0/0 | 8041 | 7548 (4981) | 15589 | 29.485 |
| SCR-5 Least squares | low | 0 | 1 | 0/0 | 9992 | 11333 (9068) | 21325 | 46.282 |
| SCR-6 Least squares | off | 0 | 2 | 1/1 | 13893 | 3053 (0) | 16946 | 15.734 |

All failure and repair costs are included. Low: 60018 tokens/132.454 seconds,
3/3 exits successful. Off: 54157 tokens/57.422 seconds, 2/3 successful.
Off saves 9.8% tokens and 56.6% time in this sample but has material compliance,
teaching and reliability regressions. One run per condition per case, not a
statistical reliability estimate; no second-model coverage. Cached prompts count
within prompt totals; cache-hit breakdown is unavailable. Reasoning is already
inside completion and is not added again.

## Scientific and brief findings

All six computational payloads match the independent references on the recorded
trials. This does **not** imply their teaching statements or model tests are true.

- Attention low: correct 2×2 Q/K, 2×1 V, ranges, stable row softmax, scaling and
  weighted values. Required equal-score/dominant presets present. At extreme
  scores exponentials can underflow to zero: limitation's `(0,1]` is too strong
  for floating-point execution. Toggle help overstates changes in P/A when scores
  are equal or values coincide.
- Attention off: compute correctly transposes K; its own test expectations and
  dominant-preset prose transpose the affected row incorrectly. `k12=100` affects
  row 2, not row 1. Equal-score exploration required by the brief is absent.
  Identity scores without scaling give outputs 12.6894/17.3106, not both 15.
  Claimed maximum score/overflow limits contradict permitted ±1000 inputs.
  Exit 1 and three visible failed page checks are honest; do not hide them.
- Entropy low: active prefix, nonnegative weights, all-zero uniform UI convention,
  zero contribution, certainty and four-way equal entropy 2 bits are correct.
- Entropy off: same mathematics/brief compliance. Contributions are bits, not
  probabilities; describing their scale as the same probability scale is misleading.
  Limitation claims only common rescaling is exercised despite individual controls.
- Least squares low: predictions, observed-minus-predicted residuals, squares and
  SSE correct; sign and exact-fit presets correct. Intercept help is false: moving
  away from exact fit changes SSE. At defaults b=0.5→2.5 leaves SSE=2.5 despite
  nonzero residuals. Changing predictions does not guarantee changing aggregate loss.
- Least squares off: accepted repair corrects test SSE 5→2, not the compute.
  First preset slope 1→2 leaves SSE=2 and second squared residual=1; explanatory
  claims 0→8/0→4/2→5 are false. Second exact-fit preset is correct.
  Bounded coefficients cannot produce arbitrarily large loss.

Grounding is reviewed against supplied excerpts, not claimed as a fresh retrieval
of every paper. Toy numbers are labelled as examples; LS additional abstract/meta
claims labelled UNVERIFIED remain unverified. No old trace proves fresh generation.

## Honest provisional rubric

Ranges below are independent estimates, not instructor grades. Historical 64/75
does not transfer. Visual/interaction estimates use actual Chromium observations
of **re-rendered retained payloads**, not the original producing revision.

| Run | Accuracy /25 | Teaching /20 | Visual /15 | Interaction /15 | Autonomy /10 | Quality /85 |
|---|---|---|---|---|---|---|
| SCR-1 | 22–24 | 16–18 | 11–13 | 12–14 | 8–9 | 69–78 |
| SCR-2 | 10–15 | 4–8 | 10–12 | 10–13 | 6–8 | 40–56 |
| SCR-3 | 22–24 | 15–17 | 10–12 | 12–14 | 8–9 | 67–76 |
| SCR-4 | 23–25 | 17–19 | 10–12 | 12–14 | 8–9 | 70–79 |
| SCR-5 | 21–23 | 15–17 | 11–13 | 12–14 | 8–9 | 67–76 |
| SCR-6 | 17–21 | 8–12 | 10–12 | 12–14 | 7–9 | 54–68 |

Tokens /10 and latency /5 cannot be awarded without hidden-case Tmin/Lmin.
For an explicitly hypothetical qualifying Entropy pair only, off at both minima
would receive 10+5 efficiency points; low receives 10×9160/15589 +
5×12.188/29.485. This is not a hidden-case prediction. Quality below 50/85
gets no efficiency points; SCR-2's range crosses that threshold, so qualification
cannot be assumed. No claim that exit 0 guarantees full scientific credit.

## Adopted changes and boundaries

Checker adds four deterministic legal combined-control boundaries inside its
existing 80-probe budget. Repro: entropy becomes -1 only for count=1 plus zero
weights; old one-control probes passed, new combined probe fails and targets
compute_js. Existing invariants and safety limits are unchanged.
Attention fixture restores the assignment-required equal-score exploration by
changing Q alone; identity K/V/scaling remain fixed. Historical scaling-only
fixture evidence is superseded, not silently relabelled.
Development rerender utility preserves original computational AST and all teaching
fields, records both revisions and never overwrites the retained source.

Autonomy: real failed/repaired traces retain costs and outcomes; model routing
matches DeepSeek/Together in these six runs. Regression tests cover request,
completion/time bounds, parse errors, retry/repair paths and sanitized trace.
Subsequent recovery policy allows three repairs and automatic truncation recovery
with reasoning disabled; explicit low/off remains authoritative. Its third repair
has mocked regression evidence, not a new live proof. Degraded missing-engine
exit 0 is possible and explicitly means numerical execution skipped, not PASS.

## Release gates

Repository URL: https://github.com/AmzBG/agentic-systems-hackathon
Unauthenticated URL returned 404; authenticated visibility was PRIVATE. Owner
AmzBG must make it accessible before submission. Do not report release GO yet.
Confirm final owner freezes and remote full SHA, then exact-SHA clean install,
suite/audit/showcase checks. Final SHA and results are returned separately after
integration. No additional paid run is authorized. Latest prompt/recovery changes
have no fresh six-run comparison; full network-disabled browser proof remains
unverified even where server-disconnected operation works.
