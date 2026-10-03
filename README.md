# Paper to Playground

Paper to Playground turns a research-paper source and a short learning brief into one self-contained, offline,
interactive HTML explanation of a single focused idea, plus a JSONL trace of how it was produced. The model designs a
compact teaching specification and a pure calculation function; deterministic code renders the page, runs the
calculations and checks them, and the agent asks the model to repair only demonstrated failures.

Built for the EECE503P / EECE798S agentic-systems hackathon.

## Team

1. **Jadjnm (User 1):** agent core: input and source handling, model calls, budgets, parsing, repairs, CLI.
2. **AmzBG (User 2):** offline page runtime: controls, visuals, numeric interpreter, browser behavior.
3. **Jiany-S (User 3):** checks, trace, practice evidence, installation and release verification.

## Setup

Python 3.11 is required.

If the Windows `py -3.11` launcher is unavailable, use the absolute path to your
Python 3.11 executable for the venv command; verify `python --version` after activation.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set `OPENROUTER_API_KEY` in the environment, or copy `.env.example` to `.env` (ignored by Git) and fill in the key.

## Run

```powershell
python agent.py --input case.json --output out --model deepseek/deepseek-v4.1-flash
```

- `--model` is authoritative: every model call goes to that model ID through OpenRouter, and nothing else is called.
  The tested model is `deepseek/deepseek-v4.1-flash`.
- `case.json` must contain the string fields `source_url`, `focus` and `audience`. Every other string field (for
  example a supplied excerpt) is forwarded to the model as brief context.
- Exit code `0` means the page passed its required checks; `1` means the run failed (the best safe page, or a
  "Generation incomplete" page, is still written); `2` means the input was invalid. Numerical checks run in the pinned
  QuickJS engine; if it were missing, the run would be reported as degraded with those checks skipped, never passed.

Outputs:

- `out/index.html`: one self-contained page with inline styles, script and SVG visuals. Its Content-Security-Policy
  blocks all network access (`default-src 'none'`, `connect-src 'none'`), so it works offline.
- `out/trace.jsonl`: one JSON event per line (read_input, fetch, identify, plan, generate, check, revision, final) with
  checks, repairs, elapsed time and API-reported token usage per call. No key, authorization header, raw prompt or
  hidden reasoning is written.

## Architecture

```text
case.json -> bounded source fetch -> one OpenRouter generation (spec JSON + compute function)
  -> parse and validate -> render offline page -> checks -> up to 3 bounded repairs -> best page + trace
```

| File | Role |
|---|---|
| `agent.py` | CLI, input loading, source fetch (3 s, byte cap; a failure is traced and generation continues from the brief), orchestration, repair targeting, best-candidate retention, page-interpreter probe |
| `prompts.py` | Generic generation and repair instructions; source text is treated as untrusted data |
| `spec_parser.py` | Wire-format parser and schema validation |
| `model_client.py`, `budget.py` | OpenRouter transport; hard limits of 10 requests including retries, 30,000 completion tokens and 10 minutes |
| `runtime.py`, `templates/` | Deterministic renderer and the page's bounded numeric interpreter |
| `checks.py` | Schema, offline HTML, compute safety, numerical execution (QuickJS), two meaningful controls |
| `trace.py` | Sanitized JSONL trace writer |

Each page shows the idea and why it matters, defined symbols, at least two controls, intermediate values and the
result, a visual, exactly two guided explorations, a limitation, and grounding labelled `FROM PAPER`, `TOY EXAMPLE`,
`SIMPLIFICATION` or `UNVERIFIED`. Generation and checking contain no paper-specific code.

For `deepseek/deepseek-v4.1-flash`, `--reasoning auto` resolves through the model profile
to low reasoning and throughput provider routing. Single is the submission flow;
planned is development/evidence only. After a truncated response, automatic-mode
recovery may disable reasoning; explicit CLI reasoning choices remain authoritative.
These use OpenRouter's unified `reasoning` and `provider` fields; measured runs are in `evidence/u1-runs/README.md` and
`evidence/paired_entropy/README.md`. Other model IDs use the generic path with no model-specific fields.

## Example

`examples/entropy/` holds a public example pair: [`case.json`](examples/entropy/case.json) and its real generated
[`index.html`](examples/entropy/index.html) and [`trace.jsonl`](examples/entropy/trace.jsonl) (1 request, no repairs,
all six checks passed, 17,917 tokens). The second public example pair is
[`examples/attention/case.json`](examples/attention/case.json),
[`index.html`](examples/attention/index.html) and [`trace.jsonl`](examples/attention/trace.jsonl).
It is the unchanged public Attention repeat generated at `14a5eaa`: one request,
23,686 total tokens, 65.2 seconds and 19 independent numerical trials passed.
See its provenance.json; the latest prompt correction has no new live-run evidence.
The six-run low/off comparison, failures and provenance are in
[`evidence/SCREENING_RELEASE_REVIEW.md`](evidence/SCREENING_RELEASE_REVIEW.md).
The exact-SHA clean install and five fresh CLI runs, including successful third
repair recovery and remaining scientific warnings, are in
[`evidence/FINAL_RELEASE.md`](evidence/FINAL_RELEASE.md). Execution PASS is not
a guarantee that generated explanatory prose is correct.
The Entropy showcase and trace remain unchanged historical generation; its exact
provenance is in `examples/entropy/provenance.json`. Current-renderer QA uses
separate re-rendered copies, never a relabelled generation trace.

## Validation

```powershell
python -m unittest discover -s tests -q
python scripts/verify_install.py
python scripts/audit_repo.py
python scripts/validate_output.py --output examples/entropy
python scripts/validate_output.py --output examples/attention
python scripts/check_entropy_oracle.py --output examples/entropy
```

Generated pages for other mechanisms with independent numerical comparisons are in `evidence/release_84c31ac/`, and
independent reviews are in `evidence/reviews/`. These are single-run results, not a guarantee for unseen papers.

Submission status and exact verification boundaries: [SUBMISSION.md](SUBMISSION.md).
Known limitation: numerical checks do not verify all generated prose or guarantee
that every requested exploration survives generation. Retained reviews document
remaining false explanations; no grade or hidden-case reliability is promised.

## Reuse credits

- Python standard library: HTTP transport to OpenRouter, HTML text extraction, JSON and unit tests.
- [pypdf](https://pypi.org/project/pypdf/): PDF text extraction from fetched sources.
- [quickjs](https://pypi.org/project/quickjs/) (QuickJS engine bindings): bounded execution of generated calculations
  during checks.
- [OpenRouter](https://openrouter.ai/): model API.
