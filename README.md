# Paper to Playground

An agent for the EECE503P / EECE798S hackathon. It turns a focused research-paper source and learning brief into a single offline interactive HTML explanation, plus an auditable JSONL execution trace.

The current core generates a compact specification that a shared offline runtime will render and check. The frozen interface and ownership are in `AI.md`. The new core and User 3 checker are integrated on `main`; the User 2 renderer has not landed yet, so an end-to-end success claim would be premature.

**Assessment model:** DeepSeek V4.1 Flash via OpenRouter, using the pinned model ID `deepseek/deepseek-v4.1-flash`.

## Team

1. **Jadjnm (User 1):** agent core, source ingestion, model calls, budgets, and CLI integration.
2. **AmzBG (User 2):** offline page runtime, controls, visuals, and browser behavior.
3. **Jiany-S (User 3):** checks, trace, practice evidence, installation, and release verification.

## Setup

Python 3.11 is required.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

For tests:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

Copy `.env.example` to `.env` and place the development key only in the ignored `.env` file:

```text
OPENROUTER_API_KEY=your-development-key
```

Never commit the key or place it in an input, generated page, trace, prompt log, or screenshot.

Once a model ID and key are available, one small paid request can verify the connection:

```powershell
python scripts/check_openrouter.py --model deepseek/deepseek-v4.1-flash
```

## Required command

```powershell
python -m pip install -r requirements.txt
python agent.py --input case.json --output out --model deepseek/deepseek-v4.1-flash
```

Successful runs create:

- `out/index.html` - self-contained HTML with embedded styles, JavaScript, and visuals.
- `out/trace.jsonl` - one event per line, including checks, revisions, elapsed time, and per-call token usage.

Two public practice inputs are under `examples/attention/` and `examples/entropy/`.
Preview the six-case run plan without making an API request:

```powershell
python scripts/run_all.py --models deepseek/deepseek-v4.1-flash --repeats 1 --output evidence/baseline --dry-run
```

## Preliminary architecture

The pipeline validates the input and source, asks the command-line-selected OpenRouter model for a compact teaching specification plus a pure calculation function, renders that through one reusable offline HTML runtime, runs structural and numerical checks, and requests a targeted repair if a check fails. It writes the best artifact atomically and records actual stage events without credentials or hidden reasoning. The new CLI is `agent.py`; `paper_playground/` is a legacy path awaiting User 1's cleanup.

The shared contract sets hard guards at 10 API calls, 30,000 completion tokens, and 10 minutes. The normal strategy targets one generation call and at most two targeted repairs.

## Evidence status

Offline contract tests and a fresh Python 3.11 wheel-only installation have passed; the install check also confirmed that the pinned QuickJS engine interrupts an infinite loop. All six practice URLs yielded extractable source text through the real fetch path. These are development checks, not generated-page results.

No live repeated-run results, repair rates, API token totals, or end-to-end timings have been measured yet, so no single-vs-planned flow quality claim is made. The single flow is only the provisional low-call baseline. The User 2 renderer and a validated public example output pair are still required before final clean-clone and browser verification.

## Open specification questions

See `docs/QUESTIONS_FOR_INSTRUCTOR.md`. The current loader requires the three named fields (`source_url`, `focus`, and `audience`), accepts additional string fields, and can use an optional `excerpt`, `source_text`, or `paper_excerpt` field if paper downloads are unavailable.

## Repository access

The GitHub repository is currently private. The team plans to make it public before submission; verify that the instructor can open the final URL without signing in. Commits and pushes use the authorized team accounts only.

## Reuse credits

- Requests: HTTP transport.
- Beautiful Soup: HTML text extraction.
- pypdf: PDF text extraction.
- QuickJS: bounded local execution of generated numerical calculations during validation.
- pytest: development tests only.

No paper-specific generated answer or page is included in the agent.
