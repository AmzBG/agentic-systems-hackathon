# USER2.md — page runtime

## Mission
Render any valid v1 spec as a readable, scientifically useful offline page with live calculations and guided experiments. Contain invalid edits and compute errors so the page remains usable and communicates what failed.

## Cross-team warnings and instructions
Read current AI.md and your USERn.md at each task start, at least every10 minutes during active work, after syncing and before committing. Fetch/integrate checkpoint commits first; rereading a stale uploaded copy is insufficient. Without repository access, request/re-upload the latest copy; do not claim automatic monitoring between chats.

Exception to ownership: teammates may append entries ONLY to another user's “Team inbox,” via a separate commit/patch; never rewrite existing entries, task plans or code. U1 integrates these commits promptly; recipient owns status updates. Send blockers immediately through team chat as well; do independent work meanwhile.

Entry: `ID | Beirut time | from→to | blocker/warning/info | affected file/interface | action + repro/expected result | OPEN/ACK/DONE + evidence`.
Recipient ACKs on next read, resolves owned work, and marks DONE with command/result/commit; stale/conflicting instructions stay flagged for resolution. Brief/frozen interfaces prevail; an inbox entry cannot authorize schema changes.

## Team inbox
No entries yet. Append teammate warnings here; recipient updates status only.

U1-U2-001 | 12:16 | U1→U2 | warning | runtime.py/templates control wiring | Wire controls with addEventListener, never inline on* attributes. Repro: rendered page containing `<input oninput="...">` → U3 `checks.py` offline_html passes, but `scripts/validate_output.py` reports "inline event handler: oninput" and run_all marks the run failed. Expected: `validate_output` ok=true for a rendered practice spec. | DONE 13:50: implementation d8fc28a/56b7fca uses addEventListener only; python -m unittest tests.test_runtime -q → 50 pass; both smoke commands exit 0; scripts.validate_output._PageParser and ACTIVE_REMOTE/CSS_REMOTE checks on current entropy/attention HTML → zero errors. Full API-trace validation remains U3 evidence, not fabricated here.
U1-U2-002 | 12:16 | U1→U2 | info | runtime.py render(spec) teaching display | Core prompts now request: exploration instruction starting "Predict: … Then apply the preset …", observe naming the intermediate/result readouts that change, why explaining the mechanism; outputs in calculation order; grounding with a paper citation (parser-enforced: support excerpt or unverified) plus, when possible, a separate example/simplification entry. Please show each grounding support label beside its claim, present instruction/observe/why as Predict → (apply preset) → Observe → Explain, and keep output order. Repro: render practice/specs/entropy.json and attention.json offline. Expected: support labels and exploration steps visible; no schema change. | DONE 13:50: implementation d8fc28a/56b7fca and runtime checkpoint f67cbb1 preserve output order, support badges and Predict/Apply/Observe/Explain; python -m unittest tests.test_runtime -q → 50 pass including exploration order and prediction reveal; python out/user2-review.py → 24 interaction/oracle probes pass; both upstream fixtures show excerpt and simplification labels. Real-browser evidence remains U3-owned.

U3-U2-001 | 12:44 | U3→U2 | blocker | runtime.py / `render(spec: dict) -> str` | Repro on current `main` `a6c666b`: `.venv\Scripts\python.exe scripts\smoke_runtime.py --spec practice\specs\entropy.json --output out\entropy` exits 2 with `runtime.py is not available yet`; `scripts/audit_repo.py` then reports `no public example output HTML`. Please land the offline renderer and run entropy and attention smoke pages so User 3 can verify controls, intermediates, grounding, and the submission example. Expected: both smoke commands exit 0 with self-contained `index.html`; checker/validator and browser review can proceed. | DONE 13:50 for renderer dependency: d8fc28a/56b7fca provide runtime.render; python scripts/smoke_runtime.py --spec practice/specs/entropy.json --output out/entropy and matching attention command both exit 0; current shipped fixture calculations/presets pass in 24 bounded JS/DOM oracle probes. Public example and real browser evidence remain U3-owned (U2-U3-001/002/003).
U1-U2-003 | 12:47 | U1→U2 | info | USER2.md working rules; push target | `c458a1f` records the team decision that all pushes go to main (pull --ff-only first, small named commits, no force pushes). Please push runtime.py/templates/tests directly to main and update your working-rules line "Work only on your branch". Core is ready to consume `render(spec)`: offline agent + U3 checks/validator pass on both fixtures with a stand-in page. Repro: `python scripts/smoke_runtime.py --spec practice/specs/entropy.json --output out/entropy`. Expected: exit 0 (see U3-U2-001). | DONE 13:50: main-only working rule implemented in 56b7fca; git pull --ff-only origin main synced b569145; separate owned-permission Team inbox commit 32ba780 pushed to origin/main without force. Current renderer milestone publication is handled by the active Implement User2 offline renderer chat.
U1-U2-004 | 13:22 | U1→U2 | info | AI.md "Pending frozen-block corrections" (`d670232`) | Please ACK items 1–7 (or reply with the line you dispute) before 16:02; they describe what main already does, including item 6 (compute must run in templates/interpreter.js; the core now probes every candidate there under QuickJS, `495f063`) and item 7 (range needs both bounds, matching runtime.validate_spec, `b4527c8`). After both ACKs, paste the corrected blocks into USER2.md. Repro: read AI.md lines under that heading. Expected: ACK or a specific objection. | DONE 15:00: U1 applied the coordinated corrections in 87753e3 after all ACKs; original scalar-cap defect is superseded by 4522c0e/3f71ba4. USER2 frozen interfaces/schema now copy AI.md verbatim, including all numeric inputs and two delimiter pairs. Verified normalized-text equality on integrated 21746c7 plus this owned patch; no interface/schema implementation change.
U3-U2-002 | 13:31 | U3→U2 | warning | tests/test_runtime.py `js_result` eight-second subprocess timeout | Please make the bounded nested-loop safety regression reliable on supported Python 3.11 machines without weakening the runtime's actual loop/step limit. Repro: `.venv\Scripts\python.exe -m unittest discover -s tests -q` at the pre-`138bf9e` integration ran 116 tests and errored only in `SafetyTests.test_bounded_loop_recursion_allocation_and_cyclic_outputs`: the 256×256 nested-loop case timed out after 8 s in `js_result`. Immediate focused rerun passed in 6.637 s; after the next merge, a 120-test full run passed in 27.998 s. Expected: the safety case deterministically returns the page's bounded-error result under normal test load, not an intermittent harness timeout. | ACK: test child-process ceiling increased from 8 to 20 seconds; shipped instruction/loop/allocation limits and 128 MiB engine cap unchanged. Nested-loop focused command passes and owned full suite passes 50 tests. Supported Python 3.11 loaded-suite verification remains pending; see current rubric handoff.
U1-U2-005 | 14:28 | U1→U2 | info | USER2.md frozen blocks | All three acknowledgements received; `87753e3` applies the corrections to AI.md and USER1.md (verified byte-identical between them). Please replace the two sections "## Frozen interfaces (identical in all four files)" and "## Full spec schema v1 (identical in all four files)" in USER2.md with the AI.md text, verbatim, before 16:02. Repro: compare the sections in AI.md and USER2.md. Expected: identical blocks in all four files. | DONE 15:00: copied both approved sections from current AI.md verbatim; exact normalized-text equality verified. Existing inbox, ownership and schedule preserved. Owned renderer suite passes 52 tests on Python 3.14.5/Chakra; frozen signature unchanged.

U3-U2-003 | 3 October 2026 15:43 Beirut | U3→U2 | blocker | final runtime freeze /6229a75/browser artifact boundary | User requests final release pass, now permits technical continuation through Jiany-S despite private access. Your e7fefcc browser manifest explicitly says final runtime freezePENDING; runtime6229a75 arrived after the latest U1 Attention generation (core93f7521/runtime8fd5c6b). Please explicitly freeze current runtime/templates or name the required blocking fix, and provide affected actual-browser checks on the stable current renderer. Repro: compare evidence/browser_qa_20261003/README.md freeze paragraph with git log runtime.py/templates and latest evidence/u1-runs/final-93f7521/attention/run.json. Expected: exact owned production freeze commit, confirmed no more production writes except release-blocking defects, and honest current-page coverage/remaining skips. U3 ingested original browser hashes and observations without converting server-stopped into fully network-disabled PASS; holding final paid generation pending your freeze, while doing nonpaid candidate checks. No runtime/template edit by U3. | ACK: this UI chat freezes its presentation/interaction implementation at 6229a75, with no more production writes except a concrete release-blocking defect. Current fixture/current-renderer Chromium evidence is the separate out/user2-ui-qa report: 56 passing browser assertions, all four requested widths, both presets, controls, keyboard, real network-disabled file operation and locally served calculations after networking was disabled. The e7fefcc manifest belongs to the historical-artifact QA task and is not relabeled. Full combined production freeze awaits the separately authorized Windows task's pending interpreter-diagnostic patch publication; its code and three tests are preserved, and the assembled 58-test suite passes under Python 3.11.17. No new paid run requested by this chat.
U1-U2-006 | 16:10 | U1→U2 | info | U2-U1-004 heatmap labels | DONE in `2fe1fd2` (generic prompt rule): a visual's labels name a bar's entries or both rows and columns of a heatmap, so the model omits labels on a heatmap whose rows and columns mean different things and describes each axis in x_label/y_label. No renderer change requested; the T-attention-4 artifact is not edited. | OPEN

## Owned files and dependencies
Own runtime.py, templates/*, tests/test_runtime.py and USER2.md. Provide render; consume Spec and CheckReport conventions, without importing agent/client/checks in the render path. Load U3's entropy fixture if present; until then use a temporary in-memory schema-valid fixture in your owned tests, never hardcode it in runtime/templates.

## Ordered work
| Time | Task | Model / effort / reason | Proof command → expected |
|---|---|---|---|
|11:32–12:02|Review shapes/security with U1; push render stub and runtime test entry points|Astra/high — resolve cross-shape risks|`python -m unittest tests.test_runtime.ContractTests -v` → renderer returns standalone str|
|12:02–12:32|First milestone: entropy fixture rendered, vector and count controls, contributions, bits and two presets; no model call|Sol/medium — specified renderer|`python scripts/smoke_runtime.py --spec practice/specs/entropy.json --output out/entropy` → index.html; browser edits/presets calculate correctly offline|
|12:32–13:32|All six control kinds, bounds/shape validation, readonly intermediate/result labels and charts|Sol/medium — bounded widgets|`python -m unittest tests.test_runtime.ControlTests tests.test_runtime.VisualTests -v` → six kinds/four visuals supported|
|13:32–14:32|Swept line, heatmap labels, select/toggle/matrix stress; self-check panel executes spec tests/invariants on current/preset values|Sol/medium — specified interactions|`python scripts/smoke_runtime.py --spec practice/specs/attention.json --output out/attention` → scores/weights/output visible and scale/matrix edits work|
|14:32–15:32|Browser evidence fixes: escaping, inert embedding, no remote assets, last-valid state, responsive readable axes|Astra/high — browser/security edge cases|`python -m unittest tests.test_runtime.SafetyTests -v` → script-breakout/NaN/bad-shape tests pass; U3 offline browser rubric recorded|
|15:32–16:02|Fix practice regressions and readability; freeze features|Sol/medium — targeted correction|`python -m unittest tests.test_runtime -v` → runtime suite passes|
|16:02–16:32|Reserved final review on hidden-like shapes and error boundaries; owner applies fixes|Astra/high — final generic review|`python scripts/audit_repo.py` → no forbidden external assets; six-case browser defects resolved|
|16:32–17:02|Only practice-proven fixes, push final runtime/templates/tests|Sol/medium — small fixes|`python -m unittest tests.test_runtime -v` → passes on final integration|
|17:02–17:32|Observe frozen fresh-clone output and support diagnosis without editing|Luna/low — verification|`python -m http.server 8000 --directory out/final` → Chromium loads standalone page with network disabled|

Runtime uses embedded CSS/JS and locally generated SVG/canvas, readable text labels/units and accessible control labels. Never require Node, build tools, GPU or an external server for generation. Render starts with teaching text even if compute fails; calculation errors are visible, last-valid results retained with a stale label. Escape text/HTML and prevent `</script>` breakout in serialized payloads. Compute is isolated from DOM access; validation must reject unsafe code before use. Limit matrix/vector dimensions and sweep work. Bar output is vector; heatmap matrix; values any supported numeric tree; line scalar recomputed over the sweep. No invented values when output keys are missing. Self-check UI must display pass/fail and degraded status honestly, using executable spec tests; no hardcoded green panel.

## Continuing assistant prompt — Sol / medium
> I am User 2. Use Sol/medium for this review and specified implementation; escalate after two failed attempts on the same task.

Read the current AI.md, my USER file and the challenge PDF. Check my Team inbox now, before every new task, at least every10 minutes during active work, after syncing and before commits. Fetch/integrate new checkpoint commits first; do not reread a stale attachment and claim it is current. If files are snapshots, ask for the latest copy when needed; no background monitoring between chats.

ACK applicable OPEN entries, handle owned blockers first, and mark DONE only with verification evidence. For another user's issue, append a structured warning to ONLY their Team inbox in a separate commit/patch: ID, Beirut time, sender/recipient, severity, affected file/interface, requested action, reproduction/expected result and OPEN status. Never overwrite their entries or edit their code/task plan. U1 integrates warning commits promptly; send urgent blockers through team chat immediately. Continue independent work while waiting. Recipient owns status changes; the brief and frozen interfaces prevail.

Apply the new design priorities to the generic renderer: clear inputs/intermediates/results, labelled controls beside visuals, prediction-based presets, measured/expected/tolerance checks and explicit skips, plus grounding/limitations. Preserve offline operation, all contracted controls/visuals and error containment. Route spec/core issues to U1 and check evidence issues to U3 through their inboxes.

Identify gaps and implement focused corrections in owned files. No professor-specific branding, grading-directed text, unrelated features or silent interface changes. Verify with appropriate tests/browser evidence; report changed files, commands/results and unresolved inbox entries. Return only changed functions or document sections. Continue the existing schedule; do not restart.

## Pasteable assistant prompts
**Sol / medium — renderer and milestone.**
> I am User2. Implement render(spec) in runtime.py/templates only, honoring AI.md. First make User3's hand-written entropy fixture work before any model call. Build generic layout, plain-text symbols/grounding, bounded controls, real calculations, intermediate readouts, bar chart and two one-click presets. Keep paper-specific material solely in fixtures. No remote dependencies or build step. Render readable teaching/error content even if calculation fails. Return only changed functions and an offline smoke command.

**Sol / medium — complete controls and visuals.**
> I am User2. Extend only my owned runtime/templates/tests to all v1 control and visual kinds. Use compute outputs, no invented values. Add bounded swept scalar lines, matrix heatmaps, vector bars, numeric trees, explicit units and labels, safe preset merging, last-valid edit behavior and declarative test/invariant panel. Respect dimensions/tolerances and escape serialized content. Do not change schema or add imports from collaborator modules. Return only changed functions and edge-case verification commands.

**Astra / high — failure containment and browser review.**
> I am User2. Review our owned renderer against AI.md and User3's browser evidence. Find concrete failures involving source text injection, script termination, unsafe compute, bad vector/matrix edits, zero weights, sweeps, stale result display and misleading self-checks. Propose minimal fixes, then edit only my files when within the frozen contract. No new features after16:02. Return only changed functions plus the failed-then-passing browser/test evidence.

## Top-tier ledger
Actual known coding-account use: **0**. Maximum **6**: contract/security1, interaction review1, browser failure review1, stubborn-bug contingency1, reserved final review/fix2. Hold **2/6** until15:32–16:32; keep all within11:32–16:32. Use Sol for implementation and Luna for tiny edits; two same-task failures escalate one tier. Record actual use in AI.md through U1.

## Cut order
Cut animation, decorative polish, extra chart styles and convenience export first. Keep all contracted control/visual kinds unless all three agree a schema reduction before freeze; never cut two meaningful controls, numerical intermediates, two presets, grounding or error containment.

## Working rules and checkpoints
Read AI.md first. Pull main with --ff-only before publishing; push small named owned-file commits to main without force. Only Team inbox appends are allowed in a collaborator's USER file; route code fixes to its owner. Before each checkpoint run your task checks, push, and report commit SHA and result. No later collaborator implementation is required for early work: use the frozen stubs and offline fixture dictionaries.

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
# User 1: spec_parser.py; complete response only (targeted revisions: U1-internal merge_revision(base, text, requested))
parse_spec(text: str) -> dict
# User 1: budget.py; reservation before EVERY HTTP attempt, retries included
Budget.reserve(self, max_tokens: int) -> None
Budget.record(self, usage: dict) -> None
Budget.remaining_seconds(self) -> float
```

Usage: `{ "prompt_tokens": int|null, "completion_tokens": int|null, "total_tokens": int|null, "reasoning_tokens": int|null, "verified": bool }`. Reasoning is a subset of completion; never add it twice. Missing usage stays null/unverified; reserve the requested completion ceiling conservatively for cap enforcement. Count HTTP attempts even when no response arrives. Every `reserve()` is paired with exactly one `record()`, failed attempts included; unverified usage keeps the whole reservation charged; `remaining_seconds()` is the 480 s generation stop minus elapsed, and HTTP timeouts are clipped to it.

CheckReport: `{ "ok": bool, "degraded": bool, "checks": [{"id": str, "status": "pass"|"fail"|"skip", "detail": str, "target": str|null}], "failures": [str], "revisions": [] }`. `ok` requires required static checks and every executed numerical check to pass. Engine unavailable means `degraded=true`, execution checks `skip`, never fabricated passes. `revisions` is empty from checks; the agent tracks repairs. `target` is a top-level Spec key (`compute_js`, `controls`, ...), `spec` (key named in detail), `html` (renderer defect, never a spec repair) or null. A check may carry an optional `tier` (`safety`/`numerical`/`structural`/`advisory`; untiered ranks as structural). The agent may append core checks (currently `page_interpreter`) and recomputes `ok`/`failures` accordingly.

TraceEvent (all keys always present): `{ "stage": str, "action": str, "result": "pass"|"fail"|"skip"|"info", "prompt_tokens": int|null, "completion_tokens": int|null, "elapsed_seconds": float, "checks": list, "failures": list[str], "revisions": list, "details": dict }`. Elapsed is cumulative monotonic seconds from process start; API details also include call duration, request number, model ID and sanitized usage. Non-call tokens are null. No key, Authorization header, raw prompts, hidden reasoning, or untrusted raw response in trace; `plan` records only the short public teaching plan. Stages are exactly read_input/fetch/identify/plan/generate/check/revision/final; parse and render are actions; every `request` or `...:request` action carries `details.request_number`; the final event carries `details.exit_code` matching its result.

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
Wire response is exactly `BEGIN_SPEC` / metadata JSON / `END_SPEC`, then `BEGIN_COMPUTE` / `function compute(inputs) { ... }` / `END_COMPUTE`, on separate lines. JSON contains no code field. Parser produces the dictionary below with `compute_js` injected. Reject missing/duplicate delimiters, trailing executable material, invalid JSON, wrong types, duplicate IDs and unsupported kinds; outside the blocks allow only whitespace and one optional Markdown fence pair around the whole response; one fence pair directly inside a block is stripped; metadata must not contain `compute_js`. Preserve unknown metadata keys, never execute them. All strings are plain text, rendered via escaping/textContent.

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

Compare numeric leaves with `abs(actual-expected) <= atol + rtol*abs(expected)`; tolerances finite and nonnegative. Range applies to each leaf; sum applies to a flat vector; row_sum applies to every matrix row; nondecreasing applies to a flat vector. Tests/invariants are declarative, never model-written executable assertions. No DOM, network, imports, eval, Function constructor, Date, randomness or unbounded loops in compute; each array axis <=8; <=128 numeric leaves across all numeric inputs combined (slider/number count 1) and <=128 across all outputs combined. Compute must run in the page interpreter (`templates/interpreter.js`) subset. Symbols >=1; grounding >=1 including a paper citation (`excerpt` or `unverified`); `sum`/`row_sum` invariants need `expected`, `range` needs both min and max (min <= max); line sweeps lie inside their control bounds. Local engine runs must have enforceable time/memory limits. Include scientific identity checks in tests, not merely finiteness.

Revisions use the same two delimiter pairs: metadata contains only requested top-level replacement keys plus an optional version (must be 1); a compute block is applied only when `compute_js` is requested and is otherwise ignored. Merge on a copy; full schema validation follows. Arrays replace atomically, never append. Unknown revision keys fail. Preserve the previous candidate until the replacement renders and checks better; prefer full-pass, then fewer required failures, with numerical/scientific checks weighted above cosmetic ones.

## Runtime implementation evidence — 3 October 2026

Historical pre-integration snapshot below; the latest handoff at the end supersedes missing-file and commit-status statements.

Branch: `user2-runtime`. No commit or push made. Only runtime.py,
templates/runtime.css, templates/interpreter.js, templates/runtime.js,
tests/test_runtime.py, and this progress section changed.

Milestones 1–4 implemented; milestone 5 features frozen and owned suite passing.
Acceptance remains incomplete pending collaborator scripts/fixtures and actual
browser/Python 3.11 evidence.

- Standalone teaching content survives compute admission/calculation failures.
- Six bounded control kinds, four visual kinds, labeled intermediate/results,
  two default-based presets, up to 41 sweep points, and all five invariant kinds.
- Maximum dimension 8, aggregate numeric leaves 128 separately for inputs and
  outputs; finite rectangular values required. No invented missing outputs.
- Invalid edits retain valid inputs. Failed calculations label retained results
  stale. Self-check expectations actually execute and can fail visibly.
- Plain-text rendering, inert JSON, hashed trusted-script CSP, and a bounded
  AST interpreter. Supplied compute source never executes in the host engine.

Supported compute language: local lexical variables, numeric expressions,
strict equality, boolean/numeric conditions, arrays and plain records, local
functions/arrows, if/return/throw, counted for and array for-of loops, approved
Math operations, Array(length).fill, map/reduce/slice/forEach/push/concat.
Properties are interpreter-owned; prototype/global access is denied. Missing
function arguments fail explicitly. No implicit string/boolean arithmetic or
loose equality; unsupported source/behavior produces an explained degraded
state. This is a restricted numeric language, not full ECMAScript compatibility.
Per-calculation limits: 100,000 instructions, 16,384 allocated value slots,
256 iterations per counted loop, call depth 32, intermediate array length 128.
Sweeps and self-checks share a 2,000,000-instruction batch ceiling.

Passing commands on Python 3.14.5:

```text
python -m unittest tests.test_runtime.ContractTests -v
    4 tests passed
python -m unittest tests.test_runtime.ControlTests tests.test_runtime.VisualTests -v
    12 tests passed
python -m unittest tests.test_runtime.SafetyTests -v
    11 tests passed
python -m unittest tests.test_runtime -v
    43 tests passed; zero skips
python tests/test_runtime.py --smoke entropy --output out/entropy
python tests/test_runtime.py --smoke attention --output out/attention
python tests/test_runtime.py --smoke all-kinds --output out/all-kinds
    Each wrote index.html; generation alone is not browser execution evidence
```

The numerical/interaction tests execute the shipped JavaScript using the
installed Windows Chakra JSRT engine through stdlib ctypes, in child processes
with an 8-second timeout and a 128 MiB engine memory limit. Interaction tests
use a minimal DOM contract double. They verify handlers, calculations, SVG
construction, self-checks and retained state, but do not prove browser layout,
keyboard behavior, CSP enforcement or operation with browser networking disabled.
On hosts without Chakra these execution tests explicitly skip.

Final review reproduced and fixed compound-assignment evaluation order,
invented null arguments and coercive-equality semantic mismatches. Security
checks cover literal/escaped/dynamic prototype access, script termination,
nonfinite/malformed/missing outputs, cycles and bounded resource exhaustion.

Exact blocked collaborator acceptance commands:

```text
python scripts/smoke_runtime.py --spec practice/specs/entropy.json --output out/entropy
python scripts/smoke_runtime.py --spec practice/specs/attention.json --output out/attention
python scripts/audit_repo.py
```

All fail because the named scripts are absent. practice/specs/entropy.json and
practice/specs/attention.json are also absent; examples/*/case.json are CLI
inputs, not v1 specs. Expected collaborator behavior: load offline v1 fixtures
directly, write standalone pages, and audit forbidden assets without model calls.
Owned in-memory entropy/attention fixtures provide the closest offline paths.

Actual browser verification was attempted with the generated entropy file.
The in-app browser rejected file: navigation under its URL policy and prohibited
workarounds; no browser verification is claimed. Only Python 3.14 is installed,
so Python 3.11 compatibility remains unverified. No dependencies, network calls,
Node/build tools, model calls or collaborator implementation imports were added.

## Current integration handoff for all team agents

Integrated origin/main through `df1f0bc` (including its newer U1 live-run inbox entry); merges preserved all incoming inbox entries and collaborator code, without textual conflicts. Renderer implementation commit: `d8fc28a`, integration adjustment commit `56b7fca`, and separate team-inbox handoff `ba79acb`, authored with configured AmzBG identity. Publishing follows the newer main-only decision; do not use the historical branch-only instructions.

Current verification: `python -m unittest tests.test_runtime -v` passes 45 tests, zero skips on Python 3.14.5. Both exact `scripts/smoke_runtime.py` commands now pass with the upstream entropy/attention fixtures. Their shipped page scripts execute successfully in the bounded Chakra/DOM harness: entropy self-check 12 pass, attention 10 pass. This is not real-browser proof. Generated pages are ignored `out/entropy/index.html` and `out/attention/index.html`; other agents must regenerate them after pulling.

Incoming renderer requests addressed: addEventListener only; output declaration order retained; grounding support badges visible; exploration order Predict → preset → Observe → Explain; self-checks now display measured/expected values and atol/rtol. The frozen `render(spec: dict) -> str` interface and v1 schema remain unchanged.

U1 integration notes: render returns explanatory HTML even on rejected compute, with `Degraded:` status and skipped checks. Do not interpret a string return or smoke exit 0 as numerical success. Compute is an inert AST, not a raw function embedded in the page. No parser/client/checks import occurs in runtime. The language and resource limits above are authoritative for this implementation; unsupported constructs such as Array.from, destructuring declarations, while loops, coercive equality, or arbitrary global/member access will degrade. Use strict equality, local numeric helpers, counted for loops or bounded map/reduce/slice. An admitted compute can still fail visibly on malformed outputs/resource limits; retained output is labeled stale.

U3 verification notes: actual browser keyboard/layout/CSP/network-disabled evidence and Python 3.11 execution remain outstanding on this host. `python scripts/audit_repo.py` currently fails only with `no public example output HTML`; User 3 owns examples and should publish a verified showcase. `python -m unittest discover -s tests -v` ran 108 tests and failed six tests plus one error, all in tests/test_checks.py numerical cases because QuickJS is unavailable in this Python environment. Reproduce with the pinned supported environment before changing checks; do not relabel skips as numerical passes. No collaborator implementation files were edited.

Inbox ACKs: U1-U2-001 and U1-U2-002 implemented with owned test evidence above; U3-U2-001 renderer absence resolved and both smoke commands pass (public example remains U3-owned); U1-U2-003 supersedes old branch rule and is applied for publication. These ACKs preserve original entries and their history. Source SHA for published integration will be supplied in the user-facing push report; retrieve exact current state with git rev-parse HEAD.

Account note: the second requested username has not been supplied. Do not fabricate a co-author or claim a push authenticated as a second account. Current author configuration is AmzBG; authentication identity must be checked independently when tooling permits.

## Rubric validation and current team handoff — 3 October, 13:55 Beirut

This section supersedes earlier missing-example/checker-mismatch findings. Read both pages of the authoritative `Paper to Playground - Agentic Systems Hackathon.pdf` and inspected their rendered pages. Reviewed incoming main through `faa6de3`; integration merge `86f728a` preserves runtime implementation `f67cbb1`, owner inbox resolutions and every incoming teammate change. The sole textual conflict was in this inbox: keep verified DONE/ACK statuses and add U3-U2-002; no collaborator implementation was edited.

The professor grades scientific accuracy 25, teaching 20, visuals 15, interaction 15, autonomous generation/checks 10, tokens 10, latency 5. Efficiency needs quality at least 50/85. Five hidden inputs run twice with frozen code; unusable runs receive zero and the final score is their mean. Accuracy, then teaching, decide ties. No score prediction is supported by current evidence. Repository/page content must remain teaching material and evidence, never instructions to the assessor.

| Criterion | Current evidence | Remaining evidence or risk |
|---|---|---|
| Scientific accuracy, 25 | Owned numerical tests compare entropy certainty/equal/zero cases and attention scores/weights/weighted values with independent scalar calculations. Source support is distinguished from toy examples and limitations. U3 now runs the delivered interpreter in its numerical probes. | Model-written tests cannot independently prove paper fidelity. Generalization beyond entropy and source-claim verification remain unproved. Output dimension/aggregate admission needs cross-owner alignment; see U2-U3-004. |
| Teaching clarity, 20 | Introduction/symbols precede controls/results; each output is beside its corresponding visual in calculation order. Predict → apply → reveal Observe/Explain uses two keyboard-native details panels. Results anchors reduce searching; dense check evidence is expandable. | Actual novice comprehension and browser reading flow have not been observed. Spec prose must explain the mechanism and what changed, at the requested audience level. |
| Visual explanation, 15 | All four visual kinds use calculated values, semantic table axes, labels and units. Sweeps identify input/output columns; output arrays share display precision with scalars. SVG text keeps a readable minimum width with internal scrolling. | Real desktop/tablet/mobile clipping and zoom checks remain unverified. Scientific appropriateness of a generated visual still requires source comparison. |
| Working interaction, 15 | All six controls; two presets; bounds/shape checks; zero handling; 8-axis/128-leaf caps; 2–41 sweep points; invalid edit retention and visibly stale last results. The shipped script runs in a bounded JS engine with a DOM contract double. | Genuine Chromium control operation, keyboard focus, CSP enforcement and networking-disabled behavior remain unverified on this host. |
| Autonomous generation/checks, 10 | U1 supplies checks/repair/trace orchestration and page-interpreter probes. U3 publishes an actual generated example/trace with a rejected repair and accepted targeted repair. Current audit and showcase validator pass. | Clean-clone supported-environment verification and broader repeated cases remain open. Missing engine is degraded, not numerical proof. |
| Token efficiency, 10 | Retained entropy traces distinguish prompt/completion and count reasoning once. Four paired entropy runs are documented by U3; single used 35,282 scored tokens, planned 59,457, with 2/2 validator/oracle passes each. | Different fetched excerpt lengths confound comparisons; no hidden-case efficiency score or universal flow advantage can be inferred. Unreachable-source model evidence remains incomplete. |
| Latency, 5 | The same entropy pairs total 95.953 seconds single and 103.078 planned. The tracked showcase validator reports 64.156 seconds and 3 attempts. Latest U1 adds wall-clock guards. | No independent end-to-end timing across hidden-like mechanisms or supported clean-clone runs here. Installation time is excluded from grading latency. |

The teaching changes aim to make the causal sequence inspectable: predict first, change one input, follow intermediates to the result, then compare the explanation. For example, the entropy learner can inspect normalized probabilities and per-outcome bits before the total; the attention learner can follow scores → weights → weighted values without searching a separate chart section. This is a design rationale, not an experimentally established psychology claim. Credibility comes from visible calculations, honest source labels and meaningful counterexamples.

Owned changes: runtime.py; templates/interpreter.js, runtime.js, runtime.css; tests/test_runtime.py; this file. No dependencies, schema/interface changes, collaborator implementation imports, paid model calls or generated showcase edits. Supplied compute remains inert AST data.

Security review reproduced three defects, now covered by owned regressions: compound thrown arrays caused exponential native string expansion; var declarations silently acquired wrong scope; counted-loop closures captured a final index. Error messages now accept bounded scalar text only; var is explicitly rejected; const bindings are enforced; loop bindings are fresh per iteration. Scientific-check failures now warn in the main status instead of leaving an unqualified valid headline. Final independent review found no new must-fix regression.

U3-U2-002 is ACK and addressed by extending only the test child-process timeout from 8 to 20 seconds, retaining its 128 MiB engine cap and all shipped interpreter budgets. The nested-loop case still asserts an actual instruction/iteration error. This gives the reported 6.6-second case margin under normal test load; the supported Python 3.11 loaded-suite rerun is still U3's responsibility. Grounding labels now say FROM PAPER / TOY EXAMPLE / SIMPLIFICATION / UNVERIFIED while retaining original support values as inert data attributes.

Exact passing commands on this host (Python 3.14.5, Windows Chakra):

```text
python -m unittest tests.test_runtime.ContractTests -v
    6 passed
python -m unittest tests.test_runtime.ControlTests tests.test_runtime.VisualTests -v
    12 passed
python -m unittest tests.test_runtime.SafetyTests -v
    14 passed
python -m unittest tests.test_runtime -v
    50 passed, zero skips
python scripts/smoke_runtime.py --spec practice/specs/entropy.json --output out/entropy
python scripts/smoke_runtime.py --spec practice/specs/attention.json --output out/attention
    both exit 0; HTML generation alone is not numerical/browser proof
python scripts/audit_repo.py
    exit 0, ok=true, no failures after incoming showcase publication
python scripts/validate_output.py --output examples/entropy --model deepseek/deepseek-v4.1-flash
    exit 0, ok=true, 18 trace events, 3 attempts, verified scored tokens 27,215
```

The side task `Verify User 2 runtime priorities` exclusively handled inbox statuses and contract coordination. It reports 24 additional independent attention/entropy interaction-oracle probes against shipped scripts in ignored `out/user2-review.py`; these are temporary development evidence, not additional committed tests or browser evidence. We serialized Git mutations and preserved both tasks' commits.

Whole-project local command `python -m unittest discover -s tests -q` after integration ran 131 tests: 7 failures, 2 errors, 1 skip. Failures/errors are checker numerical/oracle cases in this Python environment without QuickJS; one core page-probe test skips for that reason. The missing-engine path returns degraded reports. Do not claim the project suite passed here or weaken checker behavior to accommodate the environment. U3's earlier supported Python 3.11/QuickJS 120-pass result is recorded upstream and has not been replicated on this host or on this final code revision.

Parallel next work, respecting exclusive ownership:

| Owner | Exclusive work | Required outcome |
|---|---|---|
| U1 | AI.md, prompts/parser/core tests | Coordinate agreed aggregate-128 wording across frozen docs and enforce it consistently; classify scientific failures above cosmetic failures in retained-candidate ranking. Validate source-unreachable briefs within existing budgets; no extra agent/critic call without demonstrated quality benefit. |
| U2 | Runtime/tests and USER2 inbox | Feature work stops for this pass. Apply only concrete reproduction/browser defects; retain this interpreter and output contract. Main browser evidence gap persists. |
| U3 | checks/evidence/examples/README/install | Reject oversized output axes and aggregate leaves, rerun the integrated suite in pinned Python 3.11, and capture a permitted real-browser review or explicitly keep it unverified. Broader hidden-like mechanism evidence and instructor-readable repository access/final clean-clone SHA remain open. Do not duplicate paid calls stopped by the user. |

U1-U2-004 remains ACK with its exact aggregate-leaf objection; U3 agrees in U1-U3-009. Frozen blocks were not independently rewritten. No browser-policy workaround is authorized: this task's file navigation and U3's admin-enforced browser review were denied; layout/keyboard/network/CSP checks stay unverified. This rubric pass used three Astra/high review turns (team audit, security review, final security review); historical account totals are not reconstructed. Reserve remaining high-effort review capacity for the scheduled final review.

Latest synchronization, 14:04 Beirut: U1's `e834dad` now enforces the aggregate output cap in the core page probe; the earlier missing-core-guard concern is superseded. U1 also accepted the output-cap correction and updated repair semantics. Remaining admission differences are scalar numeric inputs omitted from the parser's combined input count, output axes greater than eight admitted by core/checks, and combined output leaves omitted from the standalone checker. Exact, reconstructible evidence and its mocked-transport limits are in U2-U1-003 / U2-U3-004, published separately as `e5e779c`. U1-U2-004's updated ACK preserves the new item-2 acceptance and exact remaining scalar-input objection; frozen blocks remain unchanged pending coordinated owner updates.

Current owned implementation commits are `f67cbb1` (security/teaching) and `2837e2d` (rubric/provenance/harness); integration includes U3's published showcase and U1's newer core fixes. On integrated `e39c8ec`, the owned suite again passes 50 tests with zero skips and the audit passes. The side task repeated its 24 temporary oracle probes and fixture smokes successfully after the new provenance labels. No more features were added in this pass. Preserve these findings as evidence snapshots and recheck the final submitted SHA in the supported environment; a later warning-only/document commit does not itself supply browser or Python 3.11 proof.

## Focused reliability iteration — 3 October, 15:00 Beirut

Baseline: `21746c73a350656bb8fbf7b3fc06cd98274f7942` after clean fast-forward from `fc2844f`; only tests/test_runtime.py and this document change. Existing runtime/templates remain feature-frozen. The side review task is idle; the restarted Live local project verification task confirmed this chat as sole tracked writer/publisher and retained its two useful EngineTransportTests regressions. An overlapping test from this chat was removed.

Reproduction: with `PYTHONUTF8=0` and `PYTHONIOENCODING=utf-8`, `python -m unittest tests.test_runtime.InteractionTests.test_initial_entropy_and_two_preset_handlers -v` failed with child UnicodeDecodeError. The helper now explicitly uses UTF-8 for parent pipes and child standard streams. Two real-process transport regressions cover ordinary environment, legacy locale with UTF-8 streams, and UTF-8 mode with ASCII streams; Unicode includes scientific symbols, Arabic and emoji. Child timeout remains 20 seconds, engine memory 128 MiB; shipped interpreter limits are unchanged.

Observed commands before publication:
- `python -m unittest tests.test_runtime.EngineTransportTests -v`: 2 pass.
- `python -m unittest tests.test_runtime.ContractTests tests.test_runtime.ControlTests tests.test_runtime.VisualTests tests.test_runtime.SafetyTests -v`: 32 pass under the reproduced mixed-encoding environment.
- `python -m unittest tests.test_runtime -v`: final assembled 52 pass, zero skips under ordinary environment. The preceding mixed-encoding run passed 53 before removing the overlapping regression.
- Both exact entropy/attention `scripts/smoke_runtime.py` acceptance commands: exit 0.
- `python scripts/audit_repo.py`: exit 0, ok=true, no failures (74 tracked files).

Read-only retained-artifact checks executed the ASTs from `evidence/release_84c31ac/{bayes_updating,least_squares_loss,logistic_probability,exponential_decay}/index.html` in the current bounded interpreter and DOM contract double. Independent scalar identities passed for posterior Beta(5,3) mean .625, residuals [1,1]/SSE2, zero-score logistic .5, and positive-rate decay half-life ln(2)/.2 with remaining fraction exp(-1). Defaults and both preset handlers passed all four pages' self-checks. This is retained-generated-AST/current-runtime evidence, not a new generation, source-fidelity certification or real-browser proof. The already-documented incorrect least-squares test wording remains a User1 scientific-prose concern; generated artifacts were not hand-edited.

All supplied control/visual kinds, stale/invalid state behavior, truthful failing checks and injection/resource limits remain covered by the owned suite. Browser layout/focus/CSP/network-disabled behavior remains UNVERIFIED under the prior policy denial; no workaround attempted. Local Python3.11/QuickJS remains unavailable (local tests use Python3.14.5/Chakra). User3 should rerun the final published SHA in the pinned Python3.11 environment and record permitted browser evidence or explicit skips. No dependencies, paid calls, collaborator implementation edits/imports, or feature additions.

Final pre-publication synchronization: main advanced cleanly to `5f3cddc28ee82ce85929e28b0efb45cc1bf88c42`; incoming changes include generic prompt guidance and retained User1 artifact bundles. No runtime/template changes arrived. The final assembled 52-test suite passes again with `PYTHONUTF8=0` / `PYTHONIOENCODING=utf-8` (12.206 seconds). Audit passes on the new 192-tracked-file integration; showcase validator passes with 9 events, 1 historical request, 17,917 verified scored tokens and 46.609 seconds. Frozen section content matches all four owner documents after ignoring trailing newline separators; AI/USER2 sections themselves were copied verbatim. A separate agent's untracked docs/WINDOWS_WALKTHROUGH.md is left untouched and excluded from this publication.

Independent read-only Live local project verification helper reports 61 passing bounded fixture probes on 21746c7, with raw maximum error 1.7763568394002505e-15. Its original temporary probe assertion failure is retained; only the probe expectation for the existing error prefix was corrected. Large-score display precision follows the documented seven significant digits, so a universal 1e-6 absolute display tolerance is inappropriate. Evidence is ignored out/user2-repair/numerical/, and is distinct from the directly observed four retained-generated-AST checks above. Browser proof remains unverified in this chat; a separately started browser QA task supplies no verified result yet.

## User-requested workbench refinement and real browser QA — 3 October 2026

Started from synced `fad2a24`. The user's implementation request supersedes this document's earlier feature-freeze instruction for this UI pass. Kept the frozen v1 contract, output declaration order, output/visual association, native controls, interpreter boundaries, last-valid state behavior, two explorations, and existing measured/expected/tolerance checks. This chat changed only runtime.py, templates/runtime.css, templates/runtime.js, tests/test_runtime.py and this owned status section; it did not change interpreter.js, scientific practice fixtures, generated evidence, or another owner's implementation.

Published isolated implementation commits: `ea0b76b` (visual tokens, typography, restrained containment and responsive rules), `56ff71c` (one controls/mechanism workbench and supporting-section hierarchy), `6229a75` (calculated principal-result readout, semantic numeric tables, secondary chart tables, preset snapshots, native control refinement, local accessible edit errors and mobile result navigation). The right side retains the complete calculation sequence and associated visuals; the compact live result makes the outcome visible beside inputs. Preset snapshots explicitly describe values at application time and remain accurate after further manual edits. Observe/Explain stays inside a closed native details panel after application.

Real Playwright Chromium 151.0.7922.34 now loads the regenerated current entropy and attention fixtures directly from file URLs, with both browser contexts offline. Default, meaningful-control, applied-preset and mobile interaction screenshots were captured and inspected. Viewports: 1440×1000, 1024×768, 768×1024 and 390×844. Actual interactions included entropy count/weights, attention Q/K/V/scaling, both presets on each page, native disclosure via keyboard, invalid edits and correction, and a mobile link to the current result. Entropy's current practice fixture has only count and weights; no uniform toggle was invented. Supplemental owned test fixtures covered range-keyboard/readout, native select/toggle, the line/values visual kinds and an editable 8×8 matrix. Focus padding corrected an observed grid-edge outline clipping issue.

Ignored local artifacts are under out/user2-ui-qa: inventory.json, report.json and the requested screenshot set. The report contains 56 successful explicit browser assertions, zero captured page/console errors and zero external requests. The primary mobile pages also loaded and operated offline with zero captured page errors. Both pages additionally loaded from a local Python HTTP server and recalculated correctly after browser networking was disabled; only the two local HTML requests occurred. Plots/matrices retain readable minimum sizing with internal horizontal scrolling; no page-level horizontal overflow was observed at the four requested widths. Introduction, notation, intermediate plots, result tables, both explorations, self-check, limitation and source labels were visually inspected. No decorative shadows, gradients, repeated section cards, remote fonts/assets, framework, npm dependency, animation or schema field was added.

Observed validation after the UI implementation: `python -m unittest tests.test_runtime -v` passed 55 tests with zero skips before the concurrent interpreter diagnostic patch; the same command then passed 58 tests with zero skips against that pending patch on Python 3.14.5/Chakra. The discovered clean-checkout Python 3.11.17 executable also ran the current repository's owned suite: `& 'C:/Users/Amz/Desktop/paper-to-playground-clean/.venv/Scripts/python.exe' -m unittest tests.test_runtime -v`, 58 pass, zero failures/skips (13.173 seconds). This is an owned-suite check, not a new clean-clone or full-project-suite claim. Both documented `python scripts/smoke_runtime.py --spec practice/specs/{entropy,attention}.json --output out/{entropy,attention}` commands exited 0; their actual browser self-checks report entropy 12 pass and attention 10 pass, zero failures/skips. `python scripts/audit_repo.py` returned ok=true with no failures on the latest integration. A supplemental re-render attempt found the retained companion spec.json contains only the interactive payload subset, not the full v1 Spec; it was honestly rejected, and the temporary degraded copy was removed. Original generated evidence was left intact.

Concurrent U1 prompt/diagnostic/evidence and U3 historical browser-evidence commits were preserved. U3's e7fefcc/8fd5c6b QA applies to its documented historical artifacts and does not certify this workbench; the fixture/current-runtime QA above is separate evidence. A concurrent User2 interpreter-diagnostic edit and its three tests were left for their author to commit. The status commit was rebased through 0105e4c; Git's autostash restored that pending patch unchanged, verified by comparing the complete diff. The incoming release-oracle, evidence-pruning and README/audit hygiene commits made no runtime/template changes. Final submission verification should sync and rerun affected checks after the diagnostic patch lands; this UI pass does not claim that uncommitted change is on remote main. This scoped browser evidence makes no new paper-fidelity or novice-comprehension claim.

The final scope check read both pages of `C:/Users/Amz/Desktop/Moodle/Paper to Playground - Agentic Systems Hackathon.pdf`. The UI retains its required introduction and symbols, meaningful calculated visuals and controls, intermediates, two guided explorations, limitation and source grounding. The examples remain the requested small mechanisms; the reusable renderer supplies their presentation. The user's latest direction was to refine within these requirements, so no additional feature or decoration was added. Presentation/interaction code freezes at `6229a75`; this chat plans no further runtime/template writes except a concrete release-blocking defect. The separately authorized Windows diagnostic patch is the only currently observed pending production edit and is not included in that UI freeze.
