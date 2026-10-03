# USER2.md — page runtime

## Mission
Render any valid v1 spec as a readable, scientifically useful offline page with live calculations and guided experiments. Contain invalid edits and compute errors so the page remains usable and communicates what failed.

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
