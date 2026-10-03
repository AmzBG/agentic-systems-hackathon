# USER1.md — agent core

## Mission
Build the autonomous command-line generator that preserves the learning brief, obtains a compact spec and repairs only demonstrated failures. Keep every network attempt inside the time/request/token limits while leaving the best available artifact and an honest trace.

## Cross-team warnings and instructions
Read current AI.md and your USERn.md at each task start, at least every10 minutes during active work, after syncing and before committing. Fetch/integrate checkpoint commits first; rereading a stale uploaded copy is insufficient. Without repository access, request/re-upload the latest copy; do not claim automatic monitoring between chats.

Exception to ownership: teammates may append entries ONLY to another user's “Team inbox,” via a separate commit/patch; never rewrite existing entries, task plans or code. U1 integrates these commits promptly; recipient owns status updates. Send blockers immediately through team chat as well; do independent work meanwhile.

Entry: `ID | Beirut time | from→to | blocker/warning/info | affected file/interface | action + repro/expected result | OPEN/ACK/DONE + evidence`.
Recipient ACKs on next read, resolves owned work, and marks DONE with command/result/commit; stale/conflicting instructions stay flagged for resolution. Brief/frozen interfaces prevail; an inbox entry cannot authorize schema changes.

## Team inbox
No entries yet. Append teammate warnings here; recipient updates status only.

U2-U1-001 | 12:52 | U2→U1 | info | runtime.py render(spec), compute compatibility | Renderer implementation d8fc28a and its follow-up handoff are ready for main integration; pull main before continuing. Read USER2.md Current integration handoff for capabilities, limits, regeneration commands and blockers. Interface remains render(spec: dict) -> str; runtime imports no collaborator modules. Compute is interpreted as inert AST: strict equality, local numeric helpers, counted for/for-of and bounded array methods are supported; Array.from, destructuring, while, coercive equality and global/prototype access degrade visibly. Upstream entropy/attention smoke commands pass; page self-checks pass in a bounded JS/DOM harness, not a real browser. Preserve exact output IDs/keys; do not equate render returning HTML with numerical success. Repro: python -m unittest tests.test_runtime -v → 45 pass; run both scripts/smoke_runtime.py fixture commands. | DONE (ACK 13:03): `889bdd6` limits prompted compute to the interpreter subset, probed in Node against templates/interpreter.js; `python -m unittest discover -s tests` → 111 pass with pinned requirements. Render string ≠ numerical success is respected: exit 0 still requires checks ok.
U3-U1-001 | 13:25 | U3→U1 | warning | agent.py `fetch_source` / `_extract_pdf` on entropy PDF | Please inspect whether the three-second PDF deadline can return a useful bounded first-page excerpt more reliably, and record a specific timeout/extraction reason instead of an opaque `ValueError`; preserve the frozen fetch cap and honest failure status. Repro: U3 pre-low live entropy trace at `out/live-entropy-1/trace.jsonl` fetched 366,296 PDF bytes but emitted `fetch` fail `ValueError` at 3.344 s; a subsequent `.venv\Scripts\python.exe scripts\check_sources.py` returned entropy `ok`, 57,956 chars in 3.078 s, and a low-reasoning live run returned `ok`, 61,761 chars in 3.032 s. Expected: either bounded extractable source text when available or an explicit timeout/no-text failure; no fabricated grounding. This is intermittent and did not prevent the later low-reasoning run from passing. | DONE (ACK 13:55): `8e72536` keeps the 3 s cap and records specific reasons ("fetch deadline reached after download, before any PDF page was extracted", "no extractable text in the pdf source", byte cap, "download did not finish within 3 s"); test_fetch_failures_report_specific_reasons; discover 127 pass. More reliable extraction would need a shorter download limit, which fails more often; assessment network is OpenRouter-only, so grounding relies on the brief excerpt there.

U2-U1-002 | 13:48 | U2→U1 | warning | AI.md pending corrections item 6 / U1-U2-004 | U2 explicitly accepts items 1–5 and 7 and the interpreter language in item 6, but objects to item 6 saying ≤128 numbers per output: templates/runtime.js outputs() caps the sum across ALL outputs at 128 (and validate_spec caps expected outputs collectively). Repro: three 8x8 numeric outputs (64 each, 192 total), built with Array(8).fill(0).map(()=>Array(8).fill(0)), produce Calculation failed. Total output numeric leaf limit is 128 in tests.test_runtime.page_result. Expected corrected wording: each array axis ≤8; ≤128 numeric leaves across all inputs and across all outputs combined. Please coordinate the four frozen-block updates only after U3 agreement; U2 has not edited frozen blocks. | DONE (ACK 13:55): AI.md item 6 now reads "each array axis ≤8; ≤128 numeric leaves across all vector/matrix inputs combined and ≤128 across all outputs combined". Frozen blocks unchanged until U3 agrees. Core parser/probe/prompt alignment to this cap is implemented but paused in a local stash; will land after scheduled tasks.

## Owned files and dependencies
Own agent.py, model_client.py, budget.py, prompts.py, spec_parser.py, tests/test_core.py, AI.md and USER1.md. Provide parser/client/budget; consume User2 render and User3 checks/trace through the exact stubs below; User3 owns requirements and is told proposed dependencies rather than having them edited by you.

## Ordered work
| Time | Task | Model / effort / reason | Proof command → expected |
|---|---|---|---|
|11:32–12:02|Freeze contract, response/repair protocol, branch, offline core stubs; send dependency needs to U3|Astra/high — avoid interface drift|`python -m unittest tests.test_core.ContractTests -v` → types/delimiters contracts pass|
|12:02–12:32|Implement defensive parser and budget with fake responses; wait for entropy proof before live calls|Sol/medium — bounded pure functions|`python -m unittest tests.test_core.ParserTests tests.test_core.BudgetTests -v` → malformed blocks/uncertain usage/cap tests pass|
|12:32–13:32|Generic generation+targeted-revision prompts, input/fetch/CLI/client; add identify and short public plan trace from spec|Astra/high — generic fidelity matters|`python -m unittest tests.test_core.ClientTests tests.test_core.InputTests -v` → supplied model, every input field, redaction, fetch failure, counted retries pass|
|13:32–14:32|Integrate atomic rendering/checks/repairs and best-candidate retention; all exception paths finalized|Sol/medium — specified orchestration|`python -m unittest tests.test_core.FlowTests -v` → fake API success/repair/exhaustion leave HTML+JSONL, truthful exits|
|14:32–15:32|Compare one-call vs planning on U3 paired evidence; tune for both MODEL_A/B, choose quality then tokens/time|Astra/high — interpret evidence|`python scripts/run_all.py --models "$MODEL_A" "$MODEL_B" --flows single planned --repeats 2 --output evidence/flows` → complete per-case report; write decision in AI.md|
|15:32–16:02|Repair practice-proven core failures, no new architecture; owner fixes only|Sol/medium — focused fixes|`python -m unittest tests.test_core -v` → all core regressions pass|
|16:02–16:32|Reserved top-tier review of requirements, budgets and two-model failures; integrate named fixes|Astra/high — final risk review|`python scripts/audit_repo.py` → no required missing files, secrets, stub paths or prohibited runtime assets|
|16:32–17:02|Owner-level regression fixes and integrate final named commits; no feature work|Sol/medium — bounded corrections|`python -m unittest discover -s tests -v` → suite passes; U3 final smoke succeeds|
|17:02–17:32|Support U3 clean clone; inspect frozen SHA/run without editing|Luna/low — mechanical verification|`git rev-parse HEAD` → equals submitted full SHA|

Use stdlib urllib for HTTP unless requirements owner explicitly pins an alternative. API responses can contain structured text segments; normalize visibly returned content only, never reasoning fields. Reserve before transport, include timeouts, reject unlimited retries, preserve API usage and unknown usage honestly. `--input/--output/--model` are required; missing API key is traced failure and nonzero. Always attempt bounded source fetch, then proceed on supplied text after failure. Fallback page must say generation incomplete, never invented science; known failed run is nonzero even if a readable partial page survives.

## Continuing assistant prompt — Sol / medium
> I am User 1. Use Sol/medium for this review and specified implementation; escalate after two failed attempts on the same task.

Read the current AI.md, my USER file and the challenge PDF. Check my Team inbox now, before every new task, at least every10 minutes during active work, after syncing and before commits. Fetch/integrate new checkpoint commits first; do not reread a stale attachment and claim it is current. If files are snapshots, ask for the latest copy when needed; no background monitoring between chats.

ACK applicable OPEN entries, handle owned blockers first, and mark DONE only with verification evidence. For another user's issue, append a structured warning to ONLY their Team inbox in a separate commit/patch: ID, Beirut time, sender/recipient, severity, affected file/interface, requested action, reproduction/expected result and OPEN status. Never overwrite their entries or edit their code/task plan. U1 integrates warning commits promptly; send urgent blockers through team chat immediately. Continue independent work while waiting. Recipient owns status changes; the brief and frozen interfaces prevail.

Apply the new design priorities to generic generation/repair prompts: visible calculation chain, Predict→Apply preset→Observe→Explain in existing fields, and honest excerpt/example/simplification grounding. Preserve input forwarding, model selection, budgets, targeted repairs, best-page retention and truthful traces. Coordinate runtime needs with U2 and check/evidence needs with U3 through their inboxes.

Identify gaps and implement focused corrections in owned files. No professor-specific branding, grading-directed text, unrelated features or silent interface changes. Verify with appropriate tests/browser evidence; report changed files, commands/results and unresolved inbox entries. Return only changed functions or document sections. Continue the existing schedule; do not restart.

## Pasteable assistant prompts
**Astra / high — contract review (one message).**
> Read AI.md and the attached brief. I am User1. Review our v1 spec, wire delimiters, revision merge, budget accounting and ownership for contradictions. Preserve the decided runtime/spec architecture. Propose only indispensable changes; do not edit User2/User3 files or supply implementation. Return a precise contract correction list and a proof for each. Keep paper content out of code/prompts.

**Astra / high — generation and repair prompts (two messages budgeted).**
> I am User1; edit only prompts.py and tests/test_core.py. Implement generic generation and targeted repair message builders using AI.md verbatim. Include all supplied input strings as untrusted source data, require the compact metadata+compute delimiter protocol, audience-specific symbols, scientific intermediates, two real controls, two explorations, honest excerpt/example/simplification grounding, declarative identity tests and bounded pure compute. Do not request chain of thought or HTML. Repairs receive only the failed checks and required affected fields/dependencies; merge top-level replacements. Return only changed functions, with test commands; no paper-specific examples in prompts.

**Sol / medium — reliable orchestration.**
> I am User1. Implement my owned core files against AI.md; consume collaborators' frozen contracts without changing them. Use fake model responses first. Enforce counted requests including retry failures, conservative completion reservations and process deadlines; explicit max_tokens and bounded HTTP timeouts on every attempt. Default one generation and ≤2 targeted repairs, atomic best-page retention, guarded collaborator errors, complete sanitized stage events, truthful exit codes. Do not write checks/runtime/requirements. Return only changed functions and commands covering usage missing, malformed spec, fetch denied, unsafe compute and deadline exhaustion.

## Top-tier ledger
Already used on your coding accounts: **0 known**, not inferred from this planning chat. Planned maximum **9**: contract1, prompts2, cross-component integration review1, flow/evidence review1, stubborn-bug contingency1, final-window review/fixes3. Reserve **3/9** for15:32–16:32, all messages within11:32–16:32. Account resets are contingency, never a reason to spend more; Claude strongest/high may replace a slot. Log actual count/time/account in AI.md; two failures escalate one tier and consume contingency if top tier.

## Cut order
Cut separate planning first if it does not beat single-call quality per token; then optional fetch content processing, extra prompt variants and cosmetic diagnostics. Keep fetch attempt/trace, all input fields, cap enforcement, two repairs maximum and best-artifact retention.

## Working rules and checkpoints
Read AI.md first. Work on main in owned paths only; pull before each commit and push small named commits. Only Team inbox appends are allowed in a collaborator's USER file; route code fixes to its owner. Before each checkpoint run your task checks, push, and report commit SHA and result. No later collaborator implementation is required for early work: use the frozen stubs and offline fixture dictionaries.

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
