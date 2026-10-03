# USER3.md — checks and evidence

## Live User 3 work plan (3 October 2026)

The committed starter is on `main`; User 3 works on `user3-evidence` and owns only the paths listed below. The assessment model is `deepseek/deepseek-v4.1-flash`. The local ignored `.env` already has a key; no key value belongs in chat, traces, or Git. The team is User 1 `Jadjnm`, User 2 `AmzBG`, and User 3 `Jiany-S`. Repository access is confirmed for User 1 and User 3; User 2 owns the repository. Instructor access still needs a username or explicit visibility decision.

Current dependency order:

1. Publish the `run_checks` and `write_trace` contracts, entropy fixture, and offline smoke script. User 2 can render `practice/specs/entropy.json` without waiting for model calls. User 1 can integrate against the interfaces immediately.
2. Make checks real: validate schema references and HTML locality, then run generated `compute` under a bounded JavaScript engine. Report `skip`/`degraded` if execution cannot be safely enforced. Keep scientific identities independent of model supplied tests.
3. Add attention and four other focused cases, with verified source locators and small independent numerical oracles. Review actual browser controls and cite concrete defects to their file owner.
4. Run paired evidence with DeepSeek V4.1 Flash first. A second model comparison is useful only if it exposes a distinct failure mode; it must not displace assessment-model testing or consume the development key casually.
5. Finish README names, architecture, exact pins, credits, example input/output pair, clean-clone proof, and repository access check. User 1 integrates named commits and freezes the final SHA.

Differentiator to propose to User 2 after the baseline works: a compact **before/after result readout** beside the visual. It compares the current calculation with the default or selected exploration preset using the same local `compute` function, so learners see the effect of each control immediately without extra model tokens. This is optional polish; scientific correctness, source claims, and working controls take priority.

Sync rule: User 3 sends User 1 and User 2 only a failing command, one minimal case, expected behavior, and the owner path. No edits to their files. The old committed `paper_playground/*` HTML-generation pipeline differs from the frozen compact-spec architecture; User 1 must decide whether to replace or disconnect it, while User 3 keeps requirements compatible until that decision lands.

Current handoff: `from checks import run_checks` and `from trace import write_trace` are available on `user3-evidence`. `practice/specs/entropy.json` is the first offline renderer target. `python scripts/smoke_runtime.py --spec practice/specs/entropy.json --output out/entropy` is ready for User 2 once `runtime.py` lands. The checker now executes bounded numerical probes, compares declarative tests and invariants, and requires two controls to be read and change a result or visual. `python -m unittest tests.test_checks tests.test_trace -v` verifies these contracts. `scripts/validate_output.py` validates the final artifact and trace; `scripts/audit_repo.py` is expected to fail until a real example output is generated. No live OpenRouter call has been made from this branch.

## Mission
Prove the generator works on fresh inputs with honest numerical, structural and browser evidence. Own the reproducible fixtures, pinned installation, trace writer, README and final clean-clone submission so the other two can focus on implementation.

## Owned files and dependencies
Own checks.py, trace.py, practice/*, scripts/*, tests/test_checks.py, tests/test_trace.py, requirements.txt, README.md, .gitignore, evidence/*, examples/* and USER3.md. Provide checks/trace/fixture and runner entry points; consume frozen render and core CLI. Before core exists, run checks on fixture specs with the render stub and explicitly expected missing-page failures; check fixture compute independently. Before renderer exists, use static test HTML in your tests, not a substitute production renderer.

## Ordered work
| Time | Task | Model / effort / reason | Proof command → expected |
|---|---|---|---|
|11:32–12:02|Commit stubs, hand-written entropy spec, script entry points, shared-file ownership; investigate wheel engine|Luna/low — schema-driven fixtures|`python -m unittest tests.test_checks.ContractTests tests.test_trace.ContractTests -v` → report/event shapes pass; entropy fixture validates|
|12:02–12:32|Numerical entropy identities; implement smoke_runtime driver; trace append/redaction; wheel-only dependency validation|Sol/medium — execution boundaries|`python scripts/verify_install.py` → clean Python3.11 wheel installation plus JS execution/timeout proof; `python scripts/smoke_runtime.py --spec practice/specs/entropy.json --output out/entropy` → U2 milestone evidence|
|12:32–13:32|Checks: required structures, real input reads, extreme values, tests/invariants, offline HTML and engine fallback|Sol/medium — rigorous check logic|`python -m unittest tests.test_checks tests.test_trace -v` → malformed/unsafe/time-limited/degraded checks truthful|
|13:32–14:32|Six+ cases including public entropy/attention, four similar-scope cases; repeat both models; record rubric manually|Luna/low — fixtures and reports|`python scripts/run_all.py --models "$MODEL_A" "$MODEL_B" --flows single --repeats 2 --output evidence/baseline` → 24 run rows for six cases/two IDs/two repeats|
|14:32–15:32|Paired planning experiment, quality gate, token/latency summaries; send U1/U2 minimal repros|Sol/medium — evaluate differences|`python scripts/run_all.py --models "$MODEL_A" "$MODEL_B" --flows single planned --repeats 2 --output evidence/flows` →48 run rows; cached prior identical single runs allowed and labelled|
|15:32–16:02|README/example pair/credits/team names; fresh install practice; freeze evidence tools|Luna/low — mechanical documentation|`python scripts/audit_repo.py` → README has all required fields and example pair, pins/no stubs/secrets checks pass|
|16:02–16:32|Reserved final cross-repo review grounded in actual failures; route fixes to owners|Astra/high — final independent review|`python scripts/run_all.py --models "$MODEL_A" "$MODEL_B" --flows single --repeats 1 --output evidence/final` →12 rows, zero known required failures or documented blocking repros|
|16:32–17:02|Choose verified showcase, push all evidence/requirements/README, agree candidate SHA/access|Luna/low — release bookkeeping|`git rev-parse HEAD` → full SHA; remote push succeeds, instructor access checked|
|17:02–17:32|Fresh clone exact SHA, clean3.11 venv, pip-only install, one end-to-end run, offline Chromium, submit URL/full SHA|Luna/low — reproducible release|Commands below → exit0, usable page+valid trace and matching SHA|

Engine candidate: **quickjs**, but do not assume platform wheels exist. Select and pin an exact version only after `pip download --only-binary=:all:` succeeds under the target Python3.11/platform and API supports enforceable compute time limits. Pin every direct/transitive dependency used; generation must need no compiler/system package. Candidate rejection should trigger a verified wheel-backed alternative or deliberate guarded static mode, never compilation. Put engine import behind try/except; optional failure is traced skip/degraded, not silent numerical pass. Installation failure is distinct: requirements must itself install cleanly. Keep engine support optional if no universal target wheel can be verified; document reduced evidence and retain manual browser tests.

Checks need behavioral read tracking (instrument input properties and mutate one control), not regex-only “inputs.x” counts. At least two distinct controls must be read and produce a relevant output/visual change for some valid probe; extremes alone may coincide, so add interior probes. Exercise defaults, both merged presets, numeric low/high, select every option, toggle both, vector/matrix all-low/all-high and single-cell extremes, plus declared tests; report no exceptions/nonfinite results. Limit subprocess/engine execution; never run dangerous model code merely to see what happens. Block ambient globals, imports/network/DOM/eval; if sandbox cannot enforce limits safely, skip and report degraded rather than execute. Reject unsupported visual/output shapes and undefined output references. HTML checks forbid remote loads/fetches/CDN but permit escaped citation URL text, which is not a downloaded asset; no source hyperlink needs network to understand grounding.

Practice set: attention and entropy from the brief, plus Bayes updating, linear least-squares loss, logistic probability and exponential decay (or other independently sourced comparable excerpt mechanisms). Each file preserves known three fields plus two descriptive string fields for excerpt/section; these two names are fixture choices, not assumed assessment requirements. Verify accurate excerpts/locators; don't invent quotations. Include tiny independently hand-computed oracle identities outside generated tests. Manual evidence: accuracy/25, clarity/20, visual/15, interaction/15, autonomy/10, defects, controls operated and source comparison; report these as team estimates. Review each case/model output at least once, repeat-run defects separately. No efficiency claim for quality below50. Record API prompt/completion/reasoning-subset usage, attempts, unknown usage, elapsed, checks, exit and output paths per run. Record true tested model IDs in README, not environment-variable placeholders.

## Final clean-clone commands
Run in a separate temporary directory, with candidate URL/SHA recorded by17:02. Use the final chosen CLI flow, not a special shortcut.
```bash
git clone "$REPO_URL" fresh-final
cd fresh-final
git checkout --detach "$FINAL_SHA"
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python agent.py --input examples/case.json --output out/final --model "$MODEL_A"
python scripts/validate_output.py --output out/final
python -m http.server 8000 --directory out/final
```
Expected: installation needs no compiler/system steps, CLI exit0, validator checks JSONL/usage/event stages and self-contained HTML, offline Chromium controls/presets work. Stop server afterward. Confirm `git rev-parse HEAD` equals FINAL_SHA; submit readable repo URL and all40 SHA characters before17:32. Never commit OPENROUTER_API_KEY; supply it only in environment. If a critical fix changes SHA, rerun clone/install/run for that exact SHA and resubmit before cutoff.

## Pasteable assistant prompts
**Sol / medium — local checks and trace.**
> I am User3; edit only checks.py, trace.py and my tests/scripts. Implement AI.md contracts exactly: guarded wheel-backed JS engine with execution limits, safe-code rejection, required static parts and valid HTML asset checks, property read/probe evidence for two meaningful inputs, default/presets/extremes/tests/invariants and shape/finite checks. Trace one sanitized flushed JSON line per event; unavailable engine is skip/degraded, never pass. Use independent expected calculations and failure injection. No Node/system packages or changes to core/runtime. Return only changed functions and verification commands.

**Luna / low — practice suite and evidence.**
> I am User3. Create six schema-valid practice case files and hand-written entropy/attention spec fixtures in practice only; paper specifics never go into prompts/code/templates. Public examples must meet the PDF's exact outcomes. Four additional mechanisms need verified source excerpts/locators, tiny independent oracles and valid five-string inputs. Add run_all/smoke_runtime/validate_output/audit_repo scripts with stable options named in USER3.md; produce per-run tokens, time, failures, API model and exit reports, paired single/planned comparisons and manual browser rubric forms. Use collaborator stubs until they land. Return only changed functions or document sections.

**Astra / high — final independent review.**
> I am User3. Read the attached brief, AI.md, final repo and actual evidence. Audit numerical trust, guarded engine/import/install behavior, missed input fields, counting uncertain API attempts/usage, unsafe code, offline interaction and source claims. Only report concrete reproducible failures, then route them to the owning person. I may edit only my files, and after feature freeze only practice-evidenced fixes. Verify README, exact model IDs, example input/output pair, credits and final fresh-clone steps. Return concise owner/repro/expected/fix evidence, never grading-influence text.

## Top-tier ledger
Actual known coding-account use: **0**. Maximum **3**, fewest of team: checker/sandbox design contingency1, twice-failed blocker contingency1, reserved final review1 at16:02–16:32. Hold **1/3** until15:32; all inside11:32–16:32. If unnecessary, leave contingency unused. Luna handles fixtures/README, Sol handles checks; do not spend top tier on bookkeeping. Report actual ledger to U1.

## Cut order
Cut optional extra mechanisms beyond six, extra repeated planning runs once a clear loser emerges, report styling and redundant screenshots. Keep six cases, two model IDs, honest checks/trace, one browser review per case/model, exact pins/install proof, README/example pair and final30-minute clean verification. Report any untested scope explicitly.

## Working rules and checkpoints
Read AI.md first. Work only on your branch and owned paths; User 1 integrates pushed named commits. Do not edit a collaborator's file; send a precise failing command and expected behavior to its owner. Before each checkpoint run your task checks, push, and report commit SHA and result. No later collaborator implementation is required for early work: use the frozen stubs and offline fixture dictionaries.

Checkpoint pushes: **12:02** contracts/stubs/owned test entry points; **12:32** entropy fixture/runtime smoke evidence; **13:32** real owned modules and vertical-slice fixes; **14:32** six-case/two-model support; **15:32** flow decision and regressions; **16:02** feature freeze with no TODO on required paths; **16:32** final-review fixes; **17:02** all final artifacts pushed. **17:02–17:32** clean verification and submission only. Times are Beirut, 3 October 2026, under the stated six-hours-remaining assumption.

Commands below are acceptance targets for files you will create, not existing tools supplied by this plan. Use Python unittest (stdlib); tests must exercise behavior, not mirror implementation. No live call before the 12:32 entropy milestone. A failed check is a blocker to report, not a result to relabel.

## Frozen interfaces (identical in all four files)
Python 3.11 types below are structural contracts; `Spec`, `Usage`, `CheckReport`, and `TraceEvent` mean dictionaries with the shapes below. Implementations may use type aliases, not incompatible classes.

```python
# User 2: runtime.py
render(spec: dict) -> str
# User 3: checks.py; pure with respect to files/network
run_checks(spec: dict, html: str) -> dict
# User 3: trace.py; append one sanitized JSON line, flush
write_trace(path: str, event: dict) -> None
# User 1: model_client.py; instance holds model_id, key, budget, timeout
OpenRouterClient.call_model(self, messages: list[dict[str, str]], max_tokens: int) -> tuple[str, dict]
# User 1: spec_parser.py; complete response or merged revision
parse_spec(text: str) -> dict
# User 1: budget.py; reservation before EVERY HTTP attempt, retries included
Budget.reserve(self, max_tokens: int) -> None
Budget.record(self, usage: dict) -> None
Budget.remaining_seconds(self) -> float
```

Usage: `{ "prompt_tokens": int|null, "completion_tokens": int|null, "total_tokens": int|null, "reasoning_tokens": int|null, "verified": bool }`. Reasoning is a subset of completion; never add it twice. Missing usage stays null/unverified; reserve the requested completion ceiling conservatively for cap enforcement. Count HTTP attempts even when no response arrives.

CheckReport: `{ "ok": bool, "degraded": bool, "checks": [{"id": str, "status": "pass"|"fail"|"skip", "detail": str, "target": str|null}], "failures": [str], "revisions": [] }`. `ok` requires required static checks and every executed numerical check to pass. Engine unavailable means `degraded=true`, execution checks `skip`, never fabricated passes. `revisions` is empty from checks; the agent tracks repairs.

TraceEvent (all keys always present): `{ "stage": str, "action": str, "result": "pass"|"fail"|"skip"|"info", "prompt_tokens": int|null, "completion_tokens": int|null, "elapsed_seconds": float, "checks": list, "failures": list[str], "revisions": list, "details": dict }`. Elapsed is cumulative monotonic seconds from process start; API details also include call duration, request number, model ID and sanitized usage. Non-call tokens are null. No key, Authorization header, raw prompts, hidden reasoning, or untrusted raw response in trace; `plan` records only the short public teaching plan.

Until real modules land, each owner commits these exact temporary stubs in their own files. Never copy collaborators' modules into your branch. Stubs are deliberately unusable as final success evidence.

```python
# runtime.py
def render(spec: dict) -> str:
     return '<!doctype html><html><head><meta charset="utf-8"><title>Runtime stub</title></head><body><p>Runtime stub</p></body></html>'
# checks.py
def run_checks(spec: dict, html: str) -> dict:
     return {"ok": False, "degraded": True, "checks": [{"id": "stub", "status": "skip", "detail": "checks not implemented", "target": None}], "failures": ["checks not implemented"], "revisions": []}
# trace.py
def write_trace(path: str, event: dict) -> None:
     pass
# spec_parser.py
def parse_spec(text: str) -> dict:
     raise NotImplementedError("parser stub; use practice/specs/entropy.json directly")
# model_client.py (method inside OpenRouterClient)
 def call_model(self, messages: list[dict[str, str]], max_tokens: int) -> tuple[str, dict]:
     raise RuntimeError("client stub; offline fixture path only")
# budget.py (methods inside Budget)
 def reserve(self, max_tokens: int) -> None:
     raise RuntimeError("budget stub; no live calls permitted")
 def record(self, usage: dict) -> None:
     pass
 def remaining_seconds(self) -> float:
     return 0.0
```
Client/budget methods are class-body snippets; place them inside their named classes. Offline smoke drivers load fixture dictionaries directly; no model/parser/budget dependency.

## Full spec schema v1 (identical in all four files)
Wire response is exactly `BEGIN_SPEC` / metadata JSON / `END_SPEC`, then `BEGIN_COMPUTE` / `function compute(inputs) { ... }` / `END_COMPUTE`, on separate lines. JSON contains no code field. Parser produces the dictionary below with `compute_js` injected. Reject missing/duplicate delimiters, trailing executable material, invalid JSON, wrong types, duplicate IDs and unsupported kinds; permit harmless Markdown fences around the whole response. Preserve unknown metadata keys, never execute them. All strings are plain text, rendered via escaping/textContent.

```text
Spec = {
  version: 1,
  plan: string,                         # short public teaching plan, not reasoning
  title: string,
  audience: string,
  starting_point: {idea: string, why: string, explanation: string},
  symbols: [{symbol: string, meaning: string, units: string}],
  controls: [Control, ...],             # >=2 distinct meaningful inputs
  outputs: [{id: ID, label: string, units: string,
             role: "intermediate"|"result"}],
  visuals: [Visual, ...],               # >=1; outputs referenced must exist
  explorations: [{title: string, instruction: string, observe: string,
                  why: string, preset: {CONTROL_ID: InputValue, ...}}, ...], # exactly 2
  limitation: string,
  grounding: [{paper: string, locator: string,
               support: "excerpt"|"example"|"simplification"|"unverified",
               claim: string}],
  tests: [{name: string, inputs: {CONTROL_ID: InputValue, ...},
           expected: {OUTPUT_ID: NumericTree, ...}, atol: number, rtol: number}],
  invariants: [{name: string, output: OUTPUT_ID,
                kind: "finite"|"range"|"sum"|"row_sum"|"nondecreasing",
                min?: number, max?: number, expected?: number,
                atol: number, rtol: number}],
  compute_js: string                    # internal only; pure function declaration
}
ID = [a-z][a-z0-9_]*; globally unique controls, outputs and visual IDs.
InputValue = finite number | boolean | string | finite number[] | finite number[][].
NumericTree = finite number | nonempty rectangular arrays recursively of finite numbers.
Control = {
  id: ID, label: string, help: string, units: string,
  kind: "slider"|"number"|"toggle"|"select"|"vector"|"matrix",
  default: InputValue,
  min?: number, max?: number, step?: number,
  options?: [{value: string, label: string}],
  shape?: [positive integer] | [positive integer, positive integer]
}
Visual = {
  id: ID, kind: "bar"|"line"|"heatmap"|"values", title: string,
  output: OUTPUT_ID, x_label: string, y_label: string,
  labels?: string[],
  sweep?: {control: CONTROL_ID, min: number, max: number, points: integer}
}
compute(inputs) -> {OUTPUT_ID: NumericTree, ...}; no extra text or metadata outputs.
```
Numeric sliders/numbers require finite min/max/step and bounded defaults; vector/matrix controls require shape, finite min/max/step and exact dimensions. Toggle uses booleans; select defaults/options use strings. At least one intermediate and one result; tests >=2; invariants >=1. Every output is numeric and finite. A line visual requires a numeric swept slider/number, 2–41 points and scalar output; other visuals have shape-compatible outputs. Clamp UI values to bounds, reject bad edits without replacing last valid state. Control shape is fixed; a separate count control can select the active prefix of a vector. Presets and tests merge over defaults; each must resolve to valid complete inputs. Changing count must keep normalization well-defined even when active weights are all zero: compute defines and explains its chosen policy.

Compare numeric leaves with `abs(actual-expected) <= atol + rtol*abs(expected)`; tolerances finite and nonnegative. Range applies to each leaf; sum applies to a flat vector; row_sum applies to every matrix row; nondecreasing applies to a flat vector. Tests/invariants are declarative, never model-written executable assertions. No DOM, network, imports, eval, Function constructor, Date, randomness or unbounded loops in compute; cap dimensions to 8 and total leaves to 128. Local engine runs must have enforceable time/memory limits. Include scientific identity checks in tests, not merely finiteness.

Revisions use the same three delimiter pairs: metadata contains only requested top-level replacement keys plus version; compute block is required only when compute changes. Merge on a copy; full schema validation follows. Arrays replace atomically, never append. Unknown revision keys fail. Preserve the previous candidate until the replacement renders and checks better; prefer full-pass, then fewer required failures, with numerical/scientific checks weighted above cosmetic ones.
