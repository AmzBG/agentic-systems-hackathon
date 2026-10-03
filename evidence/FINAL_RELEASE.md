# Final release verification — 3 October 2026

**NOT READY for an unconditional correctness sign-off.** Technically runnable,
public and verified; generic scientific prose and full-network-disabled gates remain.
Repository: https://github.com/AmzBG/agentic-systems-hackathon
Tested production SHA: **14a5eaafc472a65b619e44db3db17016e57b0d0b**.
Final submitted SHA is returned in the handoff after evidence-only publication.

## Clean candidate

Fresh remote clone, detached exact SHA, Python **3.11.9**, clean virtual environment.
Pinned requirements installed with `pip install --only-binary=:all: -r requirements.txt`:
no compiler/system-package workaround. Full suite **195 PASS / 0 FAIL / 0 SKIP**,
48.116 seconds. `verify_install.py --python <Python311/python.exe> --timeout 120`
PASS: separate fresh venv, wheel install, QuickJS arithmetic/time interruption,
full unittest. Audit PASS (165 tracked files), `git diff --check` PASS.
Tracked Entropy validator PASS, one real historical request, 17917 tokens;
independent six certainty/equal-distribution identities PASS. Showcase remains
historical84c31ac, with input/HTML/trace hashes in its provenance.json.
Authenticated visibility PUBLIC; **unauthenticated HTTP GET 200**. Web-tool404
was stale/unreliable and is superseded by direct credential-free HTTP200.
No instructor contact. The PDF provides a six-hour submission window, not an
absolute17:32 time; this pass followed the repository's17:32 Beirut deadline.

## Fresh ordinary CLI on the clean candidate

Command for every run: `python agent.py --input case.json --output out --model deepseek/deepseek-v4.1-flash`.
No shortcut/fake client; fresh directories, single/default auto→low profile;
truncated automatic recovery can disable reasoning. All five exit0/validatorPASS,
no degraded/skipped execution. **Do not equate that with truthful prose.**

| Input | Requests | Prompt | Completion (reasoning subset) | Total tokens | Wall seconds | Repairs |
|---|---:|---:|---:|---:|---:|---|
| Public Attention1 | 4 | 25353 | 22183 (16000) | 47536 | 90.735 | full parse fail; targeted2/3 accepted |
| Public Attention2 | 1 | 7686 | 16000 (11975) | 23686 | 65.203 | none |
| Public Entropy | 1 | 8313 | 12644 (9936) | 20957 | 46.797 | none |
| Strict Attention | 2 | 12736 | 14828 (9950) | 27564 | 47.828 | one accepted |
| Least squares | 1 | 9992 | 9279 (6434) | 19271 | 54.063 | none |

All failed attempts/repairs retained. Prompt+completion totals include reasoning
once, not twice. Per-run completion<30000, requests<10, time<600. The first run
used actual third-repair recovery after a16000-token empty truncated initial
response, malformed regeneration, then wrong numerical expectations. No claim
this recovery is cheaper than an unrepaired run. Cache breakdown unavailable;
cached prompt tokens are not subtracted. Exact served model/provider/settings and
per-call usage appear in each trace; run.json/summary.json store all totals,
code/input/output hashes and exits. See `final_14a5eaa/` (original artifacts).

## Independent numerical/scientific review

Three Attention pages: **19 trials each**, explicit semantic output mappings;
two other pages: **17 trials each**. **91 numerical trials PASS**, covering all
declared intermediates/results, defaults, presets, seeded inputs and boundaries.
Mappings fail on ambiguity; no output dropped to make the oracle green.
Development entropy discovery now recognizes explicit p probability output;
regression covers metadata/return-key renaming without colliding with local p.
This is an oracle correction, not a production generator change.

Residual findings (retained, not hand-edited):

- Public Attention1: required equal-score exploration replaced by scaling.
  Scaling-off preset actual diagonal weight0.731059, not prose0.576; why still
  invokes exp(1/sqrt(d_k)) for unscaled scores. Dominant preset says query3
  orthogonal although its dot product is8; actual query3 dominance agrees with
  the later observation, so the explanation contradicts itself. K/V control
  labels say columns although vectors are rows. Computation is correct.
- Public Attention2: equal scores and row-specific dominant preset correct.
  Equal-score why says softmax removes common multiplicative scaling; only
  constant-within-row case is invariant, not arbitrary common scaling.
- Strict Attention: all requested dimensions/ranges/defaults/explorations pass.
  Limitation says scaled scores stay below1000: permitted two entries1000 give
  raw2e6 and scaled1.414e6. K changes all normalized weight columns in affected
  rows, not solely the directly changed raw-score column.
- Entropy: correct probabilities, contributions, certainty/uniform presets and
  no independence assumption. Equation text defines i=1..4 but uses i<n for
  the active prefix: off-by-one prose inconsistent with correct computation.
  h_max and p are not guaranteed to change on every count/weight edit.
- LS: zero-slope preset q1 stays0.25, not "falls to0.25"; SSE2.5→6.5 and q2
  2.25→6.25 correct. Help overlooks zero slope/x=0 and equal-loss changes.

No safe generic deterministic prose checker was invented in the last minutes.
Existing prompt rules do not prove prose correction; these failures remain OPEN.
No production branches recognizing papers/cases, new critic, planner or dependency.
The accepted screening decision remains single/low; efficiency points require
unknown hidden Tmin/Lmin and quality≥50/85. Earlier 64/75 is not reused.
Fresh-page accuracy/teaching receive only provisional confidence; visual15 and
interaction15 have scoped actual browser evidence in final_14a5eaa/browser.json,
not a claimed instructor score. Autonomy
has real execution/recovery evidence; tokens10/latency5 report measurements, not
invented hidden-case points. See SCREENING_RELEASE_REVIEW.md for category ranges
on the separately identified historical comparison.

## Browser and release limitations

Actual User3 Chromium exercised all six re-rendered screening pages on renderer
3bf3e9b: both presets, open symbols, calculations, mobile375px root no overflow,
no warning/error logs. New fbe113c rerenders additionally showed LS marker with
correct current0.5/2.5 coordinates and SSE previous2.5/current18; Attention
ordered steps and current/previous matrix tables rendered. Originals untouched.
Browser2 then disconnected; troubleshooting and current inventory identified its
replacement browser4. Actual User3 Chromium subsequently exercised **all five
unchanged fresh pages**: symbols open, both presets/current-previous readouts,
mobile375px no root overflow, no warning/error console logs. Desktop1265px on
four pages; Attention2 desktop observation remained375px and is SKIP.
Fresh LS keyboard slope1→1.1 yields SSE0.04, intercept1→1.1 yields0.1;
empty xs0 restored0 retains SSE0.1; xs0=2 recovers SSE5.38. Both LS presets still
compute SSE6.5/0 with the local serving source stopped. New generated Attention1
visual titled row sums actually displays the weight matrix: metadata defect.
Full network-disable remains SKIP (browser advertises visibility/viewport only),
not established by server disconnection. Preserve U2's fbe113c historical60 offline
assertions separately. No screenshots-only claim. See browser.json for scope.

Remaining gates: resolve generic prose/brief failures with fresh independent
evidence; full-network-disabled confirmation. Do not promise a
winning rank, hidden-case reliability, or full correctness. Public-access and
clean-install gates are now resolved. Optional production changes stopped before
17:02; no production edit followed the tested candidate.
