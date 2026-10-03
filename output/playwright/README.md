# Renderer visual-system quality pass — 2026-10-03

Latest origin/main was fetched before changes; HEAD matched it. Concurrent existing interpreter work was preserved and separately committed as 48b171c.

## UX and behavior

- Simplified eyebrow to Paper to Playground; Interactive workbench → Try it; Mechanism and result → Calculation; Guided explorations → Experiments; Grounding → Source and grounding.
- Removed the input/mechanism/result flow, repetitive edit instructions, preset placeholder instructions, and redundant successful-calculation labels. Errors, stale results, failed checks and verification disclaimer remain.
- White page and control background, smaller numeric readouts, reduced corner rounding, one highlighted result container, neutral technical check text, thin rules and whitespace.
- Symbols and units open initially. Escaped explanation appears before the result in larger serif text with preserved line breaks; no math parsing or execution added.
- Heatmaps use fixed 0–1 domains only when declared by a range invariant for that output. Otherwise mixed-sign values use symmetric bounds and a neutral zero; one-sided and constant values use sequential scales. No topic IDs or paper names are used.
- Scale captions remain visible below plots at mobile widths. Numeric tables expose full JavaScript numeric precision and align numbers right.
- Charts and numeric table scroll regions have explicit keyboard focus and accessible names. Internal chart scrolling retained.
- No schema, scientific calculation, model artifact, interpreter, or CSP changes in this pass. No paid model calls.

## Verification

- Runtime suite: 58/58 passed. New generic heatmap/table suite: 4/4 passed.
- Full suite: 168 tests, 9 failures, 5 errors, 4 skips in Windows Python 3.14 without QuickJS. Baseline 48b171c in a separate directory: 164 tests, identical 9 failures, 5 errors, 4 skips. Numerical checker/oracle failures are an existing environment limitation; full-suite green is not claimed.
- Real Edge browser QA: Entropy and Attention practice fixtures rendered locally without models. At 1440, 768 and 390px, document width exactly matched viewport width; no document overflow. At 390px, charts were 324px wide with a 600px internal scrolling surface.
- Entropy: 12 checks pass; both presets yield expected 0 and 2 bits. Attention: 10 checks pass; both presets and query matrix edits recalculate.
- Negative query edit produced scores with symmetric ±1.414214 domain and neutral zero. Probability domain remained 0–1 across edits/presets. Generic regression also verifies unchanged values retain identical colors after other cells change.
- Keyboard ArrowRight moved the focused chart 40px after scroll animation; visible solid focus outline. Numeric disclosure opened; exact values exposed. Invalid edit restored prior value and displayed an error. Offline preset recalculation passed all 10 Attention checks.
- Browser page errors: none; final console: zero errors and warnings. Existing runtime tests verify stale/error paths, escaping, bounded execution and CSP hashes.

## Screenshots

- [Attention desktop](attention-1440.png), [768px](attention-768.png), [390px](attention-390.png)
- [Entropy desktop](entropy-1440.png), [768px](entropy-768.png), [390px](entropy-390.png)

Reproduce fixture rendering with `python scripts/smoke_runtime.py --spec practice/specs/attention.json --output output/playwright/attention` (or entropy), then serve this directory locally. Existing published model artifacts were not regenerated.
