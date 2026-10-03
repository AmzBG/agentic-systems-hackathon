# Retained breadth review — 3 October 2026 release stabilization

Reviewed on main after `d5bab9e` (U1 bundles) and `671805b` (U2 test/contract changes). These four pages were generated on `84c31ac4b76d570566f4f4732cebf08ef25ba9a6`, single/low; review on newer code does not change their provenance. No paid calls, optimization, new planning experiment, browser session or final clone occurred. U3 inspected visible text and embedded controls/outputs/tests/presets; a second read-only reviewer independently checked Bayes/LS. No rubric scores are assigned.

Numerical PASS is separate from scientific/teaching approval. All four retained pages pass current output validation and the independently calculated identities in `oracles_rechecked.json` via bounded QuickJS/page interpreter. The oracle maps the conceptual identity names to each page's actual IDs; it does not feed model-written test expectations back into the comparison.

## Bayes updating

Scientific/static PASS with a wording caveat. The Beta-Binomial update and defined symbols are correct: alpha'=alpha+k, beta'=beta+failures; prior/posterior mean and shift expose the mechanism. Positive shape-parameter bounds keep denominators valid; observation controls have integer steps. Parameter bars compare prior/posterior rather than claiming to display the full density. Both meaningful presets are correct: weak Beta(1,1) +18/2 yields19/22≈.864; strong Beta(20,20) yields38/60≈.633. Language fits the stated elementary-probability audience, though “conjugate” could use a short explanation.

Grounding: [Bayes/Price's essay](https://bayes.wustl.edu/Manual/an.essay.pdf), introductory letter and Section II Proposition10/Rule1, support inference from repeated successes/failures. Modern arbitrary Beta parameters are correctly labeled SIMPLIFICATION, not attributed verbatim to Bayes; chosen numbers are TOY EXAMPLE. No invented locator found in inspected entries.

Defect B1 (minor, teaching): the opening blend-with-observed-fraction claim needs N>0. At zero observations k/N is undefined, although the page's limitation correctly says the posterior equals the prior. Request a conditional opening statement. No calculation failure.

## Least-squares loss

Mechanism/numerical PASS; teaching FAIL pending historical-artifact warning. Predictions a+bx, residuals y−prediction, squares and SSE are correct. Residual sign differs from the paper's X beta−y but squaring makes the loss identical. Symbols and non-optimization limitation are accurate, with useful prediction→residual→square→sum intermediates and squared-residual bars/SSE slope sweep. Default SSE10, horizontal-midpoint preset SSE8 and fitting-line preset SSE0 agree independently. Full presets reset the two points to (0,1),(2,5).

Grounding: [Chen/Price, Section1 finite-domain regression](https://arxiv.org/html/1711.10051v4) contains the cited squared-norm minimization. The page labels its chosen-line two-point evaluation SIMPLIFICATION, not the paper's optimizer or experimental result. Its spectral-sparsification claim has a real introductory source; UNVERIFIED is conservative, not fabricated. The linked v4 is a later revision of the 2017 paper, not evidence that the tutorial reproduces its results.

Defects: L1 known false test name “doubling the slope doubles every residual for a zero intercept”: slope1→residuals[1,3], slope2→[1,1] at x=[0,2],y=[1,5],a=0. Numeric expected values remain correct. L2 slope help promises both predictions/residuals change, but x1=0 makes the first prediction/residual independent of slope. L3 both preset instructions mention setting only intercept/slope while the payload resets all four observation coordinates too. This matters after learner edits. U1's `558d0cf` generic test-name/expectation prompt fix is acknowledged; its effect is UNMEASURED, and this existing artifact remains unchanged and defective.

## Logistic probability

Mechanism/numerical PASS; chart-title teaching FAIL. Defined score z=b0+b1*x, odds exp(z), sigmoid probability and symbols are accurate. Controls/intermediates and score/probability sweeps are coherent. Negative-weight preset z=−2 gives odds .135335 and p=.119203; saturation preset z10 gives odds22026.466 and p=.9999546. The why statement about negative weight is correct in its preset context b0=0, not a universal claim with arbitrary intercept. “Odds can be any positive number” should ideally say positive but bounded within this page's controls.

Grounding: [Are Logistic Models Really Interpretable?, PDF p2 Notation/Definition2.1 and Section2.1](https://arxiv.org/pdf/2406.13427v1) supports the sigmoid and LR odds interpretation. One-feature specialization is SIMPLIFICATION; preset values are TOY EXAMPLE, explicitly not user-study results. Inspected locators are real. The limitation correctly warns that weight is not a probability increment.

Defect G1: visual title “Linear score z rises linearly as input x increases” is false when weight<0 and flat when weight=0. For b0=0,b1=−2, x0→z0 and x1→z−2. Request “varies linearly”, or a sign-aware title. The “S-shaped” title also has a flat zero-weight edge; qualify it. These are prose defects, not runtime failures.

## Exponential decay

Mechanism/numerical PASS with source-derivation wording defect. N(t)=N0 exp(−lambda*t), fraction, half-life and elapsed-half-life intermediates are correct; symbols/units and curve/breakdown are coherent. Presets are useful and numerically right: t87.7,lambda.0079 approximates one half-life (not exact); t100,lambda.2 gives exp(−20). The first preset's “at one half-life” title should say “near” to match its own observation. Positive lambda≥.005 avoids infinity sentinels. Zero rate has no finite half-life; “undefined” is understandable as no solution to reaching half, but infinity is the extended limiting convention and should be stated clearly. “Bounded below 0.005” should read “bounded below by 0.005”.

Grounding: [Cooper, PDF p1](https://arxiv.org/pdf/0809.4248v1) contains the RTG thermal-power equation and 238Pu half-life87.7y. Those FROM PAPER facts are supported. The bulk curve versus random individual events is an honest limitation; toy outputs are not presented as measured Cassini power.

Defect D1: the SIMPLIFICATION explanation says setting energy/efficiency to one produces remaining amount. That leaves P=lambda*N(t), not N(t). Recovering amount requires dividing thermal power by lambda*E_d (and converting electrical power through efficiency), or explicitly selecting only the exponential survival factor. The supplied case context correctly says it removes energy AND rate factors. Request accurate derivation wording, not altered computation.

## Verification scope and gates

Commands/results on supported workspace Python3.11.9 (pypdf6.19.0,quickjs1.19.4), integrated fad2a24: `python -m unittest discover -s tests -q` →150 tests in27.519s OK, exit0 (includes new Attention regression and U2 Unicode tests). `python scripts/check_practice_oracles.py --output CASE_DIR --inputs INPUT_JSON --expected EXPECTED_JSON` →exit0 for each of four entries from oracles.json; bare command has required arguments and was not treated as a failed numerical run. `python scripts/check_attention_oracle.py --output evidence/u1-runs/stage2/T-attention-4` →six trials PASS/exit0. Entropy oracle →six identities PASS/exit0; `python scripts/audit_repo.py` →ok=true/no failures/exit0; `python scripts/validate_output.py --output examples/entropy` →ok=true/exit0; `git diff --check` →exit0. Audit before this new review file is staged sees195 tracked files; count is not a quality metric.

Hygiene: team Jadjnm/AmzBG/Jiany-S, Python3.11 setup, exact model ID, unittest workflow, current compiler architecture, pinned requirements, tracked input/HTML/trace pair and accurate stdlib/pypdf/QuickJS credits checked. No production TODO/stub found by targeted rg in all eight production modules/templates; audit credential scan and untracked-.env exclusion pass. Historical frozen stub examples in planning docs are labeled temporary, not shipped implementation. AI.md still has a contradictory old “default low” sentence despite the newer profile paragraph; correction routed to its owner U1, not edited by U3. No final clean clone was run this stabilization turn.

Both presets per case were statically inspected for meaningful contrasting inputs and their stated numbers independently calculated. Current interpreter/DOM tests are not evidence of browser buttons, layout, focus, invalid-edit handling or disabled-network CSP behavior. All such real-browser checks remain SKIP/BLOCKED pending U2's observed results; no browser PASS or score is inferred.

Remaining gates: U1 generic semantic corrections and their measured effect (old artifacts keep warnings); selected current-version Attention provenance/coverage acceptance; U2 genuine browser QA; public signed-out repository access; owner freeze; final exact-SHA clean clone/run/validation. Historical Attention is now independently reviewed at `../reviews/attention.md`, not absent. No second-model coverage exists. No freeze/submission was performed.
