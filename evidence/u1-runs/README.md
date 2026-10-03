# User 1 generated runs

Model `deepseek/deepseek-v4.1-flash` via OpenRouter for every run; real API calls with API-reported usage. Command:
`python agent.py --input CASE --output DIR --model deepseek/deepseek-v4.1-flash` plus the condition flags below, fresh
output directory per run, Python 3.11 venv with pinned `requirements.txt`. Each retained directory holds the unchanged
generated `index.html`, the sanitized `trace.jsonl` and `spec.json` taken verbatim from the page's `runtime-data` script
(compute ships as the interpreter AST, so compute source text is not recoverable; pre-repair specs are not persisted).
The `oracle` column is a development check (page AST run in `templates/interpreter.js` versus Python-computed values),
not a certification.

## Final evidence (User 1 core `93f7521`)

The core freeze later moved to `2fe1fd2` (prompt-only teaching-quality rules, offline tests only), so the runs
below are earlier-SHA evidence; no live run exists at `2fe1fd2`.

`final-93f7521/attention/`: Attention with every flag at its default (single flow, `--reasoning auto` = low,
`--provider-sort auto` = throughput), produced from tree `8fd5c6b` (differs from `93f7521` only in documentation and
evidence files). Exit 0, 1 request, 0 repairs, finish `stop`; 7,070 prompt + 14,884 completion (11,502 reasoning,
within completion) = 21,954 tokens; 53.4 s; all six checks pass, not degraded; User 1 oracle pass with scaling on and
off. Full provenance in `run.json`. Known wording issue: one control help text says Q changes row sums.

`final-f0ce993/attention/`: the same command on the earlier freeze `f0ce993` (exit 0, 1 request, 0 repairs, 22,196
tokens, not degraded, oracle 7 trials x 6 outputs pass); retained because User 3's review `evidence/reviews/attention.md`
independently rechecked it.

`stage2/T-attention-4/`: retained because `tests/test_evidence_scripts.py`, User 3's Attention review and the browser QA
in `evidence/browser_qa_20261003/` use it.

## Routing, flow and reasoning comparison (`fbb880d` stage 1, `fc2844f` stage 2)

Cases: Attention, entropy, exponential decay (stage 1); Attention, Bayes, least squares, logistic (stage 2). A cut-off
is a call that ended with `finish_reason: length`. These runs decided the defaults: single flow, low reasoning,
throughput routing for this model.

| Condition | Runs | Exit 0 | Runs with a cut-off | Mean requests | Mean tokens | Max completion | Mean wall s |
|---|---:|---:|---:|---:|---:|---:|---:|
| single, default routing | 9 | 8/9 | 2 | 1.3 | 20,711 | 24,523 | 95.8 |
| single, throughput routing | 11 | 11/11 | 0 | 1.3 | 17,781 | 14,332 | 47.2 |
| planned, default routing | 4 | 3/4 | 2 | 2.5 | 34,590 | 30,000 | 100.0 |
| single, throughput, reasoning budget8k (rejected) | 3 | 3/3 | 1 | 1.7 | 29,136 | 23,962 | 78.7 |
| single, throughput, reasoning minimal (rejected) | 2 | 2/2 | 0 | 1.5 | 19,308 | 12,915 | 48.3 |

Per-run data follows. Only `stage2/T-attention-4` is retained as files; the other run directories, the superseded
`5f3cddc` Attention run and eleven older unverified runs (13:20 baseline, `*_live`, early reasoning probes, most with
numerical checks skipped) were pruned from the submission and remain in Git history at commit `9d0717a`
(`git show 9d0717a:evidence/u1-runs/README.md`).

| Run | Condition | Reasoning | Commit | Exit | Validator | Degraded | Oracle | Requests | Prompt | Completion | Reasoning tokens | Wall s | Finish reasons | Served providers |
|---|---|---|---|---:|---|---|---|---:|---:|---:|---:|---:|---|---|
| stage1/S-attention-1 | single, default routing | auto=low | `fbb880d` | 0 | True | False | pass | 1 | 6787 | 12018 | 8295 | 56.2 | stop | Together |
| stage1/T-attention-1 | single, provider sort throughput | auto=low | `fbb880d` | 0 | True | False | pass | 1 | 6787 | 14332 | 10967 | 62.3 | stop | Together |
| stage1/P-attention-1 | planned, default routing | auto=low | `fbb880d` | 1 | False | False | n/a | 3 | 19164 | 30000 | 27126 | 128.3 | stop, length, length | StreamLake; Together |
| stage1/S-entropy-1 | single, default routing | auto=low | `fbb880d` | 0 | True | False | pass | 1 | 5632 | 10694 | 7377 | 52.2 | stop | Together |
| stage1/T-entropy-1 | single, provider sort throughput | auto=low | `fbb880d` | 0 | True | False | pass | 1 | 6472 | 9972 | 7012 | 48.1 | stop | Together |
| stage1/S-decay-1 | single, default routing | auto=low | `fbb880d` | 0 | True | False | pass | 1 | 5372 | 11870 | 8607 | 125.9 | stop | DeepInfra |
| stage1/T-decay-1 | single, provider sort throughput | auto=low | `fbb880d` | 0 | True | False | pass | 1 | 5372 | 8910 | 6546 | 43.4 | stop | Together |
| stage1/P-decay-1 | planned, default routing | auto=low | `fbb880d` | 0 | True | False | pass | 2 | 9315 | 9447 | 6606 | 56.6 | stop, stop | StreamLake; Wafer |
| stage1/S-attention-2 | single, default routing | auto=low | `fbb880d` | 1 | False | False | pass | 2 | 13632 | 24523 | 20413 | 99.6 | length, stop | Together |
| stage1/T-attention-2 | single, provider sort throughput | auto=low | `fbb880d` | 0 | True | False | pass | 1 | 6787 | 11971 | 8695 | 54.0 | stop | Together |
| stage1/P-attention-2 | planned, default routing | auto=low | `fbb880d` | 0 | True | False | pass | 3 | 19178 | 29050 | 25596 | 144.5 | stop, length, stop | AtlasCloud; InferenceNet; Together |
| stage1/S-entropy-2 | single, default routing | auto=low | `fbb880d` | 0 | True | False | n/a | 2 | 10183 | 11135 | 6037 | 58.0 | stop, stop | StreamLake; Together |
| stage1/T-entropy-2 | single, provider sort throughput | auto=low | `fbb880d` | 0 | True | False | pass | 3 | 14677 | 14162 | 9934 | 68.4 | stop, stop, stop | Together |
| stage1/S-decay-2 | single, default routing | auto=low | `fbb880d` | 0 | True | False | pass | 1 | 5372 | 9596 | 5924 | 93.1 | stop | InferenceNet |
| stage1/T-decay-2 | single, provider sort throughput | auto=low | `fbb880d` | 0 | True | False | pass | 1 | 5372 | 5933 | 3323 | 32.7 | stop | Together |
| stage1/P-decay-2 | planned, default routing | auto=low | `fbb880d` | 0 | True | False | pass | 2 | 9330 | 12878 | 9556 | 70.8 | stop, stop | AtlasCloud; Together |
| stage2/T-attention-3 | single, provider sort throughput | auto=low | `fc2844f` | 0 | True | False | pass | 2 | 9365 | 12216 | 8552 | 53.1 | stop, stop | Together |
| stage2/T-attention-4 | single, provider sort throughput | auto=low | `fc2844f` | 0 | True | False | pass | 1 | 6787 | 9192 | 6034 | 44.6 | stop | Together |
| stage2/B-attention-1 | single, throughput, reasoning budget8k (experimental, rejected) | budget8k | `fc2844f` | 0 | True | False | pass | 2 | 13632 | 23962 | 17966 | 97.7 | length, stop | Together |
| stage2/B-attention-2 | single, throughput, reasoning budget8k (experimental, rejected) | budget8k | `fc2844f` | 0 | True | False | pass | 1 | 6787 | 15085 | 10051 | 67.0 | stop | Together |
| stage2/B-attention-3 | single, throughput, reasoning budget8k (experimental, rejected) | budget8k | `fc2844f` | 0 | True | False | pass | 2 | 10999 | 16942 | 11161 | 71.4 | stop, stop | BaseTen; Together |
| stage2/M-attention-1 | single, throughput, reasoning minimal (experimental, rejected) | minimal | `fc2844f` | 0 | True | False | pass | 2 | 9668 | 9245 | 6198 | 43.4 | stop, stop | Together |
| stage2/M-attention-2 | single, throughput, reasoning minimal (experimental, rejected) | minimal | `fc2844f` | 0 | True | False | pass | 1 | 6787 | 12915 | 10352 | 53.2 | stop | Together |
| stage2/S-bayes-1 | single, default routing | auto=low | `fc2844f` | 0 | True | False | n/a | 2 | 4306 | 21817 | 18988 | 283.3 | length, stop | DeepInfra; Sail Research |
| stage2/T-bayes-1 | single, provider sort throughput | auto=low | `fc2844f` | 0 | True | False | n/a | 1 | 2125 | 10256 | 7772 | 35.7 | stop | BaseTen |
| stage2/S-lsq-1 | single, default routing | auto=low | `fc2844f` | 0 | True | False | n/a | 1 | 9093 | 8285 | 5152 | 50.9 | stop | AtlasCloud |
| stage2/T-lsq-1 | single, provider sort throughput | auto=low | `fc2844f` | 0 | True | False | n/a | 1 | 9093 | 11620 | 9033 | 53.4 | stop | Together |
| stage2/S-logistic-1 | single, default routing | auto=low | `fc2844f` | 0 | True | False | n/a | 1 | 7090 | 8992 | 6729 | 42.8 | stop | Together |
| stage2/T-logistic-1 | single, provider sort throughput | auto=low | `fc2844f` | 0 | True | False | n/a | 1 | 7459 | 6736 | 4318 | 23.8 | stop | BaseTen |

## Repairs (first failure → requested keys → final tests/invariants)

- **stage1/P-attention-1**: first failures ['wire: missing END_SPEC', 'wire: missing compute block']; revisions [('full', ['version', 'plan', 'title', 'audience', 'starting_point', 'symbols', 'controls', 'outputs', 'visuals', 'explorations', 'limitation', 'grounding', 'tests', 'invariants', 'compute_js'], False)]; final tests None; final invariants None
- **stage1/S-attention-2**: first failures ['numerical_execution: test_3: expected scores failed (measured=[[0, 0.7071067811865475], [0.7071067811865475, 0]] expected=[[0, 0], [0, 0]] atol=1e-09 rtol=1e-09); test_3: expected weights failed (measured=[[0.3302384506733431, 0.669761549326']; revisions [('full', ['version', 'plan', 'title', 'audience', 'starting_point', 'symbols', 'controls', 'outputs', 'visuals', 'explorations', 'limitation', 'grounding', 'tests', 'invariants', 'compute_js'], True)]; final tests ['equal dot products give uniform weights', 'scaling divides each score by sqrt(dk)', 'orthogonal queries and keys give zero scores and uniform weights', 'dominant score keeps about 0.982 of the weight when scaling is off']; final invariants ['each row of the weights sums to one [row_sum ..]', 'weights lie between zero and one [range 0..1]', 'output entries stay finite [finite ..]']
- **stage1/P-attention-2**: first failures ['the previous response was cut off at the completion-token limit before END_COMPUTE; reason briefly and write compact JSON without indentation', 'wire: missing END_SPEC']; revisions [('full', ['version', 'plan', 'title', 'audience', 'starting_point', 'symbols', 'controls', 'outputs', 'visuals', 'explorations', 'limitation', 'grounding', 'tests', 'invariants', 'compute_js'], True)]; final tests ['equal scores give uniform weights and row sums one', 'scaling divides raw scores by sqrt of key dimension', 'exploration one preset keeps row sums one', 'exploration two preset row sums one']; final invariants ['weights_rows_sum_to_one [row_sum ..]', 'row_sums_near_one [range 0.999..1.001]', 'weights_in_unit_interval [range 0..1]', 'output_is_finite [finite ..]']
- **stage1/S-entropy-2**: first failures ['numerical_execution: test_2: expected contribs failed (measured=[0, 0.5, 0.5, 0.5, 0.5, 0] expected=[0, 0.25, 0.25, 0.25, 0.25, 0] atol=1e-09 rtol=1e-09)']; revisions [('targeted', ['compute_js', 'tests'], True)]; final tests ['Fair coin gives exactly one bit', 'Zero-weight outcome contributes nothing and four equal outcomes give two bits', 'Five equally likely outcomes', 'Six equally likely outcomes give log2 6 bits', 'All-zero weights fall back to three equally likely outcomes']; final invariants ['Probabilities of the six outcomes sum to one [sum ..]', 'Entropy stays between zero and log2 6 bits [range 0..2.584962500721156]', 'Every reported value is finite [finite ..]']
- **stage1/T-entropy-2**: first failures ['numerical_execution: default: undeclared outputs H, Hmax; default: h missing, nonfinite or outside bounded numeric shape; default: hmax missing, nonfinite or outside bounded numeric shape; default: visual line_entropy has wrong output shape;', "page_interpreter: default: page compute returns ['H', 'Hmax', 'c', 'q'], declared outputs are ['c', 'h', 'hmax', 'q']"]; revisions [('targeted', ['outputs', 'visuals', 'tests', 'invariants'], True), ('targeted', ['compute_js', 'outputs', 'visuals', 'invariants', 'tests'], True)]; final tests ['equal four outcomes', 'certain binary outcome', 'all active weights zero fallback', 'normalization of equal raw weights']; final invariants ['entropy bounds [range 0..2]', 'normalized probability sum [sum ..]', 'contribution bounds [range 0..0.6]', 'maximum entropy bounds [range 1..2]']
- **stage2/T-attention-3**: first failures ['invariants[1].rtol: must be a finite nonnegative number', 'invariants[2].rtol: must be a finite nonnegative number']; revisions [('targeted', ['invariants'], True)]; final tests ['equal_scores_uniform_weights', 'zero_scores_uniform_weights', 'unscaled_dominant_score']; final invariants ['weights_rows_sum_to_one [row_sum ..]', 'weights_in_unit_interval [range 0..1]', 'output_finite [finite ..]']
- **stage2/B-attention-1**: first failures ['the previous response was cut off at the completion-token limit before END_COMPUTE; reason briefly and write compact JSON without indentation', 'wire: missing END_SPEC']; revisions [('full', ['version', 'plan', 'title', 'audience', 'starting_point', 'symbols', 'controls', 'outputs', 'visuals', 'explorations', 'limitation', 'grounding', 'tests', 'invariants', 'compute_js'], True)]; final tests ['unscaled identity keys keep the raw dot products', 'equal scores preset gives uniform weights and averaged output', 'dominant score preset gives the sharp first weight', 'unscaled dominant score follows the sigmoid of two']; final invariants ['the two weight rows together sum to the query count [sum ..]', 'first weight is a probability [range 0..1]', 'similarity scores stay finite [finite ..]']
- **stage2/B-attention-3**: first failures ['numerical_execution: test_4: expected scores failed (measured=[[0.7071067811865475, 2.1213203435596424], [1.414213562373095, 2.82842712474619]] expected=[[0.7071067811865476, 1.4142135623730951], [2.121320343559643, 2.8284271247461903]] atol']; revisions [('targeted', ['compute_js', 'tests'], True)]; final tests ['equal keys give weights of one half and a scaled score of 1/sqrt(2)', 'dominant key with scaling off leaves raw scores 1 and 3', 'same dominant key with scaling on lowers the largest weight', 'scaling divides every score by the square root of the key dimension']; final invariants ['every attention weight row sums to one [row_sum ..]', 'the two row sums together equal two [sum ..]', 'largest attention weight stays between one half and one [range 0.5..1]', 'output entries stay finite [finite ..]']
- **stage2/M-attention-1**: first failures ['explorations[1].preset.v: every entry must be within [min, max]']; revisions [('targeted', ['explorations'], True)]; final tests ['zero scores give uniform weights and average value rows', 'identical value rows pass through unchanged']; final invariants ['attention weight rows sum to one [row_sum ..]', 'attention weights stay in the unit interval [range 0..1]', 'output values stay finite [finite ..]']
- **stage2/S-bayes-1**: first failures ['the previous response was cut off at the completion-token limit before END_COMPUTE; reason briefly and write compact JSON without indentation', 'wire: missing END_SPEC']; revisions [('full', ['version', 'plan', 'title', 'audience', 'starting_point', 'symbols', 'controls', 'outputs', 'visuals', 'explorations', 'limitation', 'grounding', 'tests', 'invariants', 'compute_js'], True)]; final tests ['no data leaves the prior unchanged', 'flat prior with three successes and one failure', 'weak prior preset gives posterior mean three quarters', 'strong prior preset gives posterior mean three fifths']; final invariants ['posterior mean is a probability [range 0..1]', 'prior mean is a probability [range 0..1]', 'shift stays inside the unit interval [range -1..1]', 'means readout stays finite [finite ..]']
