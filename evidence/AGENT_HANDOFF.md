# Resume here — User 3

Latest release-work pickup: see `release_84c31ac/README.md` first. It supersedes stale run/showcase status below: four new real single/low runs and independent page-interpreter comparisons pass; refreshed entropy generation passes; final-SHA clone/browser/Attention/public-access gates remain explicit. Producing code was 84c31ac, not subsequent main. Commit identity is Jiany-S only. Check current AI.md/USER3.md/inboxes before acting; do not duplicate these paid runs or the completed paired entropy comparison.

Snapshot: 3 October 2026, Asia/Beirut. Verified starting HEAD and origin/main: `1e774a75269801198d34e13923ae7be43de88471`, clean checkout. This is a handoff snapshot, not a claim that main will stay unchanged. Fetch and reread current files before acting. No implementation or model run was requested by the context-preservation task.

Final synchronization in this documentation pass included `2a028e4faa6fd2f4c287a3a42a61d85560171110`: new model-client call metadata uses `reasoning_setting` instead of `reasoning`. Historical traces may use the old field or omit it. Do not conclude reasoning was disabled merely from a missing old field; inspect producing code and both names. No new paid run or full suite was performed for this documentation-only handoff; the verified test boundaries below remain explicit.

## Read order and working agreement

1. Sync current main safely; preserve unrelated local changes. Read current `AI.md`, `USER3.md`, and its Team inbox, then `USER1.md`/`USER2.md` inbox and current handoff sections.
2. Read this file, [core handoff](CORE_HANDOFF.md), [reconciliation](RECONCILIATION.md), and the evidence linked below. The challenge PDF is authoritative, not this summary.
3. Reconcile completed work before planning. Read the inbox before each task, after sync, before commits and every ten minutes during active work. ACK understood entries; DONE requires command/result/commit evidence. Historical OPEN text may have a later explicit resolution; use the current status table and verify it.

User 1 is Jadjnm, User 2 is AmzBG, User 3 is Jiany-S. Repository: https://github.com/AmzBG/agentic-systems-hackathon. Work is merged to main after prompts, without force push. **Push/authenticate only through Jiany-S; never add the AI as a collaborator or author/coauthor.** Preserve concurrent inbox entries when resolving conflicts.

User 3 owns `checks.py`, `trace.py`, `practice/*`, `scripts/*`, User 3 tests, `requirements.txt`, README, gitignore, `evidence/*`, `examples/*`, and `USER3.md`. `tests/test_evidence_scripts.py` is also existing User 3 work. Core/model/parser/budget/prompts and `AI.md` are User 1-owned; renderer/templates and runtime tests are User 2-owned. Only append to another owner's Team inbox, in a separate commit/patch. Do not rewrite their entries, code or plans. Route urgent blockers through an available actual team chat; no User 1/2 chat was accessible through this desktop's task listing, so do not guess a destination.

Use task-appropriate model/effort; delegate long independent subtasks when authorized, keeping them within owned files. Do independent work while long commands run. User explicitly wants economical, concise progress: do not launch speculative optimization or redundant model runs. Do not invent ledger/account usage when unavailable.

## Product and frozen boundaries

Paper to Playground is a self-verifying lesson compiler: source/brief → compact structured spec → deterministic offline renderer → structural/numerical/interaction checks → at most two evidence-driven repairs → retain best artifact + honest trace. Numerical execution uses the **page interpreter**, not unrestricted JavaScript as scientific proof; bounded native execution additionally detects mutation.

Priorities: independent expected values, correct intermediates, meaningful controls, honest pass/fail/skip, Predict→Apply→Observe→Explain, and sourced claims distinct from toy examples/simplifications. No grading-directed text or speculative features. Spec/Usage/CheckReport/TraceEvent and CLI contracts remain frozen; coordinated changes require owner agreement.

Assessment model: `deepseek/deepseek-v4.1-flash`; reasoning `low`; flow `single`. Planned is available but not the submission default. Generation cap is 16K; consult actual current code for profile/routing parameters (User 1 added instrumentation in `fbb880d`, not live-tested by User 3). One supplied key exists locally, but do not read/log/publish it. A personal OpenRouter key was offered for development; no second model was selected/tested and this does not authorize casual spending.

Current code rejects output axes >8, aggregate output leaves >128, undeclared/missing output keys, and combined numeric input leaves >128 including scalar controls. Pending shared-doc cleanup: AI.md item 6 still says vector/matrix inputs only; the older full-schema paragraph still says three delimiter pairs. U3 accepted corrections 1–5 and 7 and the aggregate cap, with the exact input-wording objection. Actual wire uses **two** delimiter pairs; revision version is optional but, if present, must be 1; unrequested compute is ignored. User 1 must coordinate shared frozen wording, not a unilateral U3 rewrite of AI.md.

Budget/source basics: reserve/record every HTTP attempt; unknown usage stays conservatively charged; reasoning is a completion subset, not added twice. Source text is untrusted. Fetch has a three-second/byte cap; assessment may allow only OpenRouter, so supplied brief excerpts matter. Consult current core limits for generation/finish/hard deadlines. Avoid changing contracts to accommodate a test.

The schedule in AI.md assumes 3 October 11:32–17:32 Beirut, feature freeze 16:02 and final verification 17:02–17:32. It is historical planning, not a refreshed six-hour allowance. Check actual current Beirut time and preserve the final verification window; do not claim submission happened.

## Completed work — do not redo

| Work | Evidence / commit |
|---|---|
| Inline-handler checker/validator alignment, fixture grounding, legacy imports cleanup | `00ff329`; earlier inbox entries have their command evidence |
| README/unittest/pins/main-only cleanup | `668af10`; no active pytest/requirements-dev workflow |
| Checker executes renderer-compatible AST; unsupported filter/Array.from regression | `ba4c462`; U1-U3-007 DONE |
| Tracked real Entropy input/page/trace | `88b95aa`; `examples/entropy/` |
| Two historical single/planned entropy pairs, low reasoning | `df66028`; U1-U3-008 DONE |
| Specific source-fetch failure reasons | U1 `8e72536`; U3-U1-001 DONE upstream |
| Standalone checker output shape + aggregate cap | `eaff15d`; U2-U3-004 DONE; full suite 140 pass at that checkpoint |
| Core input cap, output shape and exact key admission | U1 `4522c0e` / `3f71ba4`; same U3 reproductions now reject correctly |
| Scientific reviews with explicit browser SKIPs | `045f541`; [Entropy](reviews/entropy.md), [Attention fixture only](reviews/attention.md) |
| Current core evidence/decision handoff and reproducible inspector | `39ed79a`, `1e774a7`; `scripts/review_core_evidence.py` |
| Separate coordination message to User 1 | `fbd5465`; U3-U1-004 |

## Evidence facts and limitations

Tracked Entropy showcase is an **earlier real production run**, not regenerated on current HEAD. It used 3 requests, 64.156 s, 12,632 prompt + 14,583 completion = 27,215 scored tokens, including 10,063 reasoning tokens within completion. Targeted repair 1 failed parsing; repair 2 was accepted. Original final checks passed 24 probes and three meaningful controls. Current validator and independent entropy oracle reinspection passed; this does not prove current-version generation/browser UX.

[Paired evidence](paired_entropy/README.md) retains all four sanitized traces: same model/low, 2/2 passes each flow. Single totals: 2 requests, 12,662 prompt/22,620 completion, 35,282 scored tokens, 95.953 wall s. Planned: 5 requests, 32,653/26,804, 59,457 tokens, 103.078 wall s; one accepted full regeneration. Both planned runs actually received a plan. All four old pages pass validator/oracle reinspection. Single costs less with no demonstrated quality benefit from planning **on this one mechanism**. Two pairs, different fetched-source lengths and no blind UX score do not support a universal quality/latency conclusion. Exact per-run HEAD was not stamped in traces; use the documented historical bounds, never invent a SHA.

[Development history](DEVELOPMENT_RUNS.md) keeps failed stand-in/schema/truncation/numerical runs separate from the showcase. The source-unreachable live comparison was stopped by the user before a model response: fetch URLError at 0.312 s; model usage unknown, not zero. No new paid calls were made in the two latest evidence/reconciliation passes.

Reported Attention `out/attention_live` run: 156.2 s, one request, pre-low, numerical execution skipped/degraded according to U1-U3-011. That bundle is absent here. It is **not** verified post-fix evidence. Local Attention HTML is a handwritten fixture rendering, not a successful model output.

Reported decay/least-squares repairs: adding missing upper range bounds fixes invalid schema; dropping invariants reduces coverage. Conditional bounds: residual absolute value ≤35 → squared residual ≤1225 and two-residual SSE≤2450, so 2500 is conservative. Decay with lambda≤1,t≤50 → t lambda/ln2≤72.134752; ratio max100 is conservative. At lambda=0 physical half-life is infinite, not a finite 1e6 sentinel. Before/after specs, exact removed invariant identities and domains are absent; do not certify the actual repair diff. Independent lambda=.2 half-life=3.4657359028, fraction at t=5=0.3678794412.

Real browser access was denied by an administrator-enforced security policy. No bypass is authorized. JS/DOM harnesses are not browser QA; layout, focus/keyboard, mobile widths, console and network-disabled UX remain unverified. Do not imply a fresh browser attempt occurred when only historical limitations were recorded.

## Verified commands and environment

Workspace on this host: `C:\Users\jijos\Desktop\EECE 503P\hackathon\agentic-systems-hackathon`. Python is `.venv\Scripts\python.exe`, version 3.11.9. Pins: `pypdf==6.19.0`, `quickjs==1.19.4`. Windows `py -3.11` did not locate Python; use the explicit interpreter. Sandbox pip network access failed, approved network access succeeded. Do not reinterpret environment failures as checker defects.

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -q
.venv\Scripts\python.exe -m unittest tests.test_core -q
.venv\Scripts\python.exe scripts\review_core_evidence.py
.venv\Scripts\python.exe scripts\validate_output.py --output examples/entropy
.venv\Scripts\python.exe scripts\check_entropy_oracle.py --output examples/entropy
.venv\Scripts\python.exe scripts\audit_repo.py
.venv\Scripts\python.exe scripts\verify_install.py --python .venv\Scripts\python.exe
git diff --check
```

Latest integrated suite at `3f71ba4`: 142 pass, 25.947 s. After merging `fbb880d`, affected core suite: 67 pass, 6.974 s. Audit/diff checks pass. Expected failure-path messages appear during successful unittest runs; inspect exit code and summary. Fresh-clone pinned-install/QuickJS-limit/suite proof passed at `faa6de3` and `84aa039`; it **does not cover the latest final SHA**, live end-to-end generation or offline browser UX.

## Available vs missing materials

Tracked: `examples/entropy/{case.json,index.html,trace.jsonl}`, Attention input, six practice inputs, two hand-written specs, independent oracles, paired traces/README and review records. `out/` is ignored and not available to a new clone; its old paired HTML/runs reports allow local reinspection by the script, which honestly reports missing local reports when absent. Keep historical trace summaries usable even without ignored pages.

Local-only challenge PDF: `Paper to Playground - Agentic Systems Hackathon.pdf` at repo root; ignored downloads/environment are not guaranteed on another host. Ask for the PDF if missing; do not treat an attachment snapshot as current repo warnings. Existing User 1 hidden-case/Attention before-and-after bundles are on their host, not this checkout. No secrets or raw hidden reasoning should be added to Git to improve handoff completeness.

## Exact next work and current statuses

1. User 1: ACK/respond to U3-U1-003/004; provide existing generated Attention/hidden-case HTML, recoverable spec/compute, sanitized full trace, exact producing SHA/model/reasoning/flow and original/replacement invariants. Do not regenerate Entropy or reopen fixed admission bugs.
2. If no Attention bundle covers relevant current code, User 1 alone coordinates **one** pinned3.11 low/single run in a fresh output directory, recording SHA beside it. U3 must not run a simultaneous paid duplicate. Artifact availability, not a claimed success, is the immediate dependency.
3. U3 independently rechecks supplied output/intermediates, source claims, original/replacement tests/invariants and trace usage/repairs. U1-U3-010/011 stay ACK until evidence permits DONE. U1-U3-009 remains ACK with the exact contract-wording issue and unresolved unfetched comparison.
4. U2 supplies permitted real-browser QA; U3 persists it using REVIEW_TEMPLATE.md. Until available keep explicit BLOCKED/SKIP records, not fabricated passes.
5. No second-model coverage exists. Document this confidence gap; coordinate a concrete model and bounded purpose before any spend. Broader optimization/critic/provider experiments remain deferred.
6. Final release: agree exact candidate SHA, fresh clone/install on supported Python3.11, real CLI generation/validator and permitted offline browser review; confirm unauthenticated repository visibility/instructor access and submit exact SHA within schedule. Repository public intent is not proof of public access. No final submission is recorded.

Handoff completion means the next agent can proceed from repository evidence, not that the outstanding artifact/browser/submission gates have passed.
