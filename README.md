# Paper to Playground

Paper to Playground is a self-verifying lesson compiler. The model understands the paper and designs a focused teaching specification; deterministic software renders the interactive explanation and verifies its calculations; the agent revises only demonstrated failures.

Built for the EECE503P / EECE798S hackathon, it turns a focused research-paper source and learning brief into a single offline interactive HTML explanation, plus an auditable JSONL execution trace.

The current core generates a compact specification that the shared offline runtime renders and the checker verifies. The frozen interface and ownership are in `AI.md`. Core, renderer, and checker are integrated on `main`; an end-to-end success claim still awaits a verified live run and browser review.

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
python -m unittest discover -s tests -v
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

## Architecture status

The pipeline validates the input and source, asks the command-line-selected OpenRouter model for a compact teaching specification plus a pure calculation function, renders that through one reusable offline HTML runtime, runs structural and numerical checks, and requests a targeted repair if a check fails. It writes the best artifact atomically and records actual stage events without credentials or hidden reasoning. The CLI is `agent.py`; the former direct-HTML pipeline has been removed.

The shared contract sets hard guards at 10 API calls, 30,000 completion tokens, and 10 minutes. The normal strategy targets one generation call and at most two targeted repairs.

## Evidence status

Offline contract tests and a fresh Python 3.11 wheel-only installation have passed; the install check also confirmed that the pinned QuickJS engine interrupts an infinite loop. All six practice URLs yielded extractable source text through the real fetch path. These are development checks, not generated-page results.

One early live development run is recorded in `evidence/DEVELOPMENT_RUNS.md`: it used the assessment model but a stand-in page, parsed a spec, then failed schema validation before numerical checks. It is not a generated-page success. No live repeat set, repair rate, or single-vs-planned flow comparison has been measured, so the single flow remains only a provisional low-call baseline. The renderer is now integrated; a validated public example output pair and real browser verification are still required before final clean-clone verification.

## Open specification questions

See `docs/QUESTIONS_FOR_INSTRUCTOR.md`. The current loader requires the three named fields (`source_url`, `focus`, and `audience`), accepts additional string fields, and can use an optional `excerpt`, `source_text`, or `paper_excerpt` field if paper downloads are unavailable.

## Repository access

The GitHub repository is currently private. The team plans to make it public before submission; verify that the instructor can open the final URL without signing in. Commits and pushes use the authorized team accounts only.

## Reuse credits

- Python standard-library HTTP and HTML parsing: source ingestion and OpenRouter transport.
- pypdf: PDF text extraction.
- QuickJS: bounded local execution of generated numerical calculations during validation.

No paper-specific generated answer or page is included in the agent.
