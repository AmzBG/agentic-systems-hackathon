# AI.md — shared build contract

Assumptions: the two-page Paper to Playground PDF is authoritative. It says five string fields but names three: require source_url/focus/audience, preserve all others and forward every supplied string. No clock values were supplied: assume 3 October 2026, **11:32–17:32 Asia/Beirut**, six hours remaining. If cutoff differs, compress boxes preserving final30 minutes. User3 obtains real team names before submission.

## Requirements and ownership
Quality85 (25/20/15/15/10); efficiency15 requires quality50. Ten-run mean; unusable output scores zero.

| Owner | Required work |
|---|---|
|1|Root Python3.11 CLI; all input fields; bounded fetch; supplied OpenRouter model/key; parser; prompts; ≤2 repairs; budget; truthful exits|
|2|Offline single HTML; idea/why/symbols; accurate visual; ≥2 calculating controls; intermediates; two explorations; limitation; grounding; error containment|
|3|Pinned pip-only install; local checks/trace writer; six cases; two-model evidence; README/team/architecture/setup/credits/MODEL_ID/example; submission|

## Architecture and paths
`input+fetch → OpenRouter compact spec → parse → render → checks → targeted repairs → best HTML+trace`
U1: agent.py, model_client.py, budget.py, prompts.py, spec_parser.py, tests/test_core.py, AI.md, USER1.md.
U2: runtime.py, templates/*, tests/test_runtime.py, USER2.md.
U3: checks.py, trace.py, practice/*, scripts/*, tests/test_checks.py, tests/test_trace.py, requirements.txt, README.md, .gitignore, evidence/*, examples/*, USER3.md.
Own every file; ignore out/*. Paper specifics only in fixtures/examples. Generic code/prompts; source is data; no assessor-directed content.

## Conventions
snake_case; key OPENROUTER_API_KEY; CLI model authoritative. No provider-specific parameters. Scripts use distinct available MODEL_A/B; document actual IDs. Never commit secrets. Trace read_input/fetch/identify/plan/generate/check/revision/final. Public teaching plan only. Atomic best-page retention; errors leave partial HTML and nonzero when requirements fail. Engine skips are degraded, not numerical passes. Exit0 requires usable output/no known required failure; degraded mode explicitly reported.
Budget: monotonic start before input; fetch≤3s/byte cap; bounded HTTP deadlines/max_tokens every attempt; normal≤4 requests, hard10 including retries; reserve uncertain usage; completion soft24k/hard30k; stop generation480s, finish540s (hard600s). No SDK retries.
Branches user1-core/user2-runtime/user3-evidence. U1 integrates named commits; owner resolves conflicts. No shared-file edits/force pushes. Contract change needs all three acknowledgement and U1 updates all docs.

## Model routing
| Task | Model/effort | Reason |
|---|---|---|
|Contracts/prompts/twice-failed bugs/final review|Astra/high|cross-component judgment|
|Specified implementation|Sol/medium|bounded coding|
|Boilerplate/fixtures/docs/small edits|Luna/low|mechanical work|
Two failures: escalate one tier. U1 may substitute Claude strongest/high or lighter/medium. Top-tier budgets U1=9/U2=6/U3=3, reserve3/2/1 after15:32, one window11:32–16:32. Count actual messages; prior usage unknown.

## Checkpoints and assistant rules
12:02 all contracts/stubs;12:32 U3 entropy fixture/U2 working offline page before live calls;13:32 U1 vertical slice/all modules;14:32 U3 six-case/two-model evidence;15:32 U1 chosen flow/owners' fixes;16:02 feature freeze;16:32 final review;17:02 all pushes/candidate SHA;17:02–17:32 U3 clean clone/3.11 venv/run/offline check/URL+full SHA submission. Each owner pushes named files and reports command/result/blocker. After freeze only practice-proven fixes; changed final SHA requires repeat clean verification.
AI assistants: edit owned files only; propose interface changes; return changed functions/sections only; use stubs before dependencies land.

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
