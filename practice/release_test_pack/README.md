# Paper to Playground: release test pack

Seven valid five-string inputs, two invalid-input diagnostics, and 31 independent numerical probes. Four mechanisms are outside your original six-case set. No generated answers or application changes are included. This is development evidence, not the hidden assessment set or a grade prediction.

## Start here: three cases

Run **01_batch_norm**, **02_gaussian_kl**, and **07_offline_unknown_field** first. They exercise a new vector mechanism, a sign-sensitive mathematical formula, and source-independent input handling. Coordinate with User 1's current release session; this pack does not require another paid Attention run.

Extract this folder beside your repository. Activate the repository's installed Python 3.11 venv and set OPENROUTER_API_KEY normally. Use the actual supplied model ID in place of MODEL_ID:

```bash
python release_test_pack/reference_math.py
python release_test_pack/run_suite.py --repo ./agentic-systems-hackathon --model MODEL_ID
```

The first command checks the pack's reference identities only. The second makes REAL PAID calls through your agent, sequentially, for the three default cases. It uses only the required input/output/model flags and inherits the API key from your environment. It does not change application files or select reasoning/routing settings. Nothing has been run against your actual agent by the author of this pack.

One case directly, from your repo root:

```bash
python agent.py --input ../release_test_pack/cases/01_batch_norm.json --output out/release_batch_norm --model MODEL_ID
python scripts/validate_output.py --output out/release_batch_norm
```

Use a new output directory for every attempt. For more coverage:

```bash
python release_test_pack/run_suite.py --repo ./agentic-systems-hackathon --model MODEL_ID --cases 03_focal_loss 04_adam
python release_test_pack/run_suite.py --repo ./agentic-systems-hackathon --model SECOND_MODEL_ID --cases 01_batch_norm 02_gaussian_kl
```

`--cases all` runs all seven; `--repeat 2` repeats selected cases; `--negative` adds two invalid inputs that should fail before API calls. Do not run the full matrix merely to fill a table before submission. Each valid case has a 600-second watchdog. A batch can take much longer; preserve your 3:45 feature freeze and 4:45–5:15 final verification window.

## What each case catches

| Input | Probe to inspect | Expected result | Common defect |
|---|---|---|---|
| 01_batch_norm | Default x=[1,2,3,4], gamma=1, beta=0 | mean=2.5; variance=1.25; y≈[-1.34163542,-0.44721181,0.44721181,1.34163542] | Uses sample variance, forgets epsilon or mixes gamma/beta |
| 02_gaussian_kl | mu=[1,0], sigma=[1,2] | contributions≈[0.5,0.8068528194]; positive total≈1.3068528194 nats | Wrong sign, standard deviation confused with variance |
| 03_focal_loss | p_t=0.9, gamma=2 | CE≈0.1053605157; modulation=0.01; FL≈0.001053605157 | Ignores gamma, uses log2 or confuses true-class probability |
| 04_adam | g=[2,2,2], alpha=0.1, one step | m=0.2; v=0.004; corrected m=2, v=4; theta≈0.9000000005 | Missing bias correction, wrong timestep or epsilon placement |
| 05_attention_stability | Default identity Q/K, V=[[10],[20]], scaling on | weights≈[[0.66976155,0.33023845],[0.33023845,0.66976155]]; output≈[[13.30238451],[16.69761549]] | Softmax wrong axis, wrong scaling, wrong matrix product |
| 06_entropy_edges | Four equal weights | four contributions of 0.5 bits; total=2 bits | Natural log instead of log2, ignored active count |
| 07_offline_unknown_field | p_t=0.9, gamma=2 | base FL≈0.001053605157; modified example≈0.003898339079 | Ignores unknown field or depends on source fetching |

The JSON inputs provide formulas and demonstration scope, not these numerical answer keys. Supplied passages are original paraphrases, not verbatim paper excerpts. The paper/section is supplied for grounding; all chosen input values are our examples. Case 07 adds an explicitly artificial multiplier available only in `mechanism_note_7`, so merely recalling the original paper cannot satisfy it.

## Numerical review

Open `expected_results.json`; set the page to each probe's conceptual inputs and compare the displayed values or page interpreter outputs. Control/output IDs may differ: map by mathematical meaning, not by string equality. This pack does not silently assume a generated DOM or spec format.

For machine values use `abs(actual-expected) <= 1e-6 + 1e-6*abs(expected)`. Display rounding is acceptable within half a displayed last-digit unit; inspect underlying values when precision is insufficient. Do not increase tolerances to hide a wrong calculation. The independent values come from Python math in `reference_math.py`, with closed-form sanity checks. They do not use generated tests or the application's interpreter.

Critical probes:

- **Batch norm:** constant x=[3,3,3,3], gamma=2, beta=-1 gives variance=0, normalized zeros and y=[-1,-1,-1,-1]. With positive epsilon, normalized variance is v/(v+epsilon), not exactly 1. Negative gamma reverses order.
- **Gaussian KL:** matching the prior gives zero; mu=[2,0], sigma=[1,1] gives 2 nats. Sigma=0 is outside the declared domain. The displayed positive KL must not be confused with its negative contribution to the ELBO.
- **Focal loss:** gamma=0 recovers cross entropy. Increasing gamma suppresses easy examples more strongly. The domain excludes singular p_t=0.
- **Adam:** all-zero gradients leave theta at 1; alpha=0 also leaves theta unchanged. Negative gradients reverse update direction. Probe the sign-reversal sequence and multiple steps; a one-step-only implementation is insufficient.
- **Attention:** zero Q gives uniform rows and output [[15],[15]]. Q=[[1000,0],[0,1000]] must stay finite. Scaling divides scores by sqrt(2) in this example, not by 2. A mathematically false test name is a teaching defect even when the numbers pass.
- **Entropy:** certainty gives zero bits; n=3 equal active weights gives log2(3); n=1 gives zero. All-zero active weights invoke the explicitly requested uniform UI convention. Inactive entries must not enter normalization.
- **Offline case:** `.invalid` is deliberately unavailable. Expect a bounded failed-fetch trace and successful use of the supplied note. The value 3.7 is an example choice, never attributed to the focal-loss paper.

## Browser and teaching acceptance

Serve a generated output locally with your usual Chromium setup. Load it, disable network and operate its controls. For each reviewed page record:

1. At least two meaningful controls change the relevant calculation/visual, with correct labels and intermediate values.
2. Both exploration presets actually produce the described setting and observation. Compare test names and prose with numbers.
3. The requested control ranges are honored. Undisclosed narrowing is a failure; genuine invalid inputs are rejected clearly while preserving valid state.
4. Required idea/importance/symbols, limitation and paper/section grounding are present. Examples and simplifications are distinguished from source claims.
5. No missing assets, network dependency, exceptions, frozen controls, stale results presented as current, or fabricated green checks.

A reference fixture pass does not substitute for a newly generated page pass. Preserve failing artifacts; fix generator/runtime/checker code through the appropriate owner, then regenerate. Never hand-edit generated pages to pass.

## Evidence and interpretation

The harness writes a unique `results/` folder with code SHA, dirty status, input hash, model, wall time, exit code, trace checks and per-request usage when identifiable. It never puts secrets into the manifest and suppresses captured application console output. Inspect trace.jsonl for diagnostics. Missing/unrecognized usage stays unverified. It cannot prove that every API request was traced; reconcile suspicious counts with the agent's totals.

**30,000 is the COMPLETION-token cap**, including reasoning once. Prompt+completion is the efficiency total, not that cap. The other hard limits are 10 requests including retries and 600 seconds per case. The harness watchdog is diagnostic protection, not a substitute for the agent's budget controls. Stop any run reported as timed out; do not infer scientific success from exit 0.

The summary always starts `scientific_review=NOT_RUN` and `browser_review=NOT_RUN`. Add a separate review table with case/model/SHA, numerical verdict, browser verdict, teaching/source verdict, defects, reviewer and time. Engine execution skips mean degraded evidence, not numerical certification. Compare models on identical input files and record fetched-source differences.

The two invalid inputs test graceful rejection (nonzero, promptly, no API call). Missing artifacts on invalid input are diagnostic notes, not valid-input rubric failures. Test filenames and expected values are developer data; keep this pack outside production imports/prompts/templates and use your ownership rules if committing it under practice/evidence.

## Sources checked for this pack

- Ioffe & Szegedy, [Batch Normalization](https://arxiv.org/html/1502.03167v3), Section 3, Algorithm 1.
- Kingma & Welling, [Auto-Encoding Variational Bayes](https://arxiv.org/html/1312.6114v11), Appendix B. We negate the paper's negative-KL expression to test positive KL.
- Lin et al., [Focal Loss for Dense Object Detection](https://arxiv.org/html/1708.02002v2), Section 3.2, Equation 4 (unweighted).
- Kingma & Ba, [Adam](https://arxiv.org/pdf/1412.6980), Section 2, Algorithm 1.
- Vaswani et al., [Attention Is All You Need](https://arxiv.org/html/1706.03762v7), Section 3.2.1.
- Shannon, [A Mathematical Theory of Communication](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf), Section 6.

These are known mechanisms of comparable scope, not evidence about the instructor's hidden cases. Passing this pack increases confidence within its coverage; it does not establish an expected grade.
