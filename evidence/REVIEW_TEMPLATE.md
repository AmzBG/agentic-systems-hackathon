# Browser review record

Copy this page for each case and model after a real generator run. This is a team estimate, not a claim about the instructor's score.

| Field | Entry |
|---|---|
| Case / focus | |
| Source URL and checked section | |
| Model ID | |
| Commit SHA | |
| Output directory | |
| Run number / elapsed seconds | |
| API attempts / prompt tokens / completion tokens | |
| Usage verified against trace? | |
| Process exit / final trace result | |
| First failed check or run error | |
| Repair outcomes (accepted / rejected / call failed / parse failed) | |
| Requested flow / `--flow` passed? | |
| Planning attempts / plan response used / effective flow | |
| Scored tokens (prompt + completion; reasoning already inside completion) | |

## Repeat-run comparison

Fill one row per fresh output directory. Keep failures visible even when another repeat passes.

| Repeat | Exit | Status | Elapsed seconds | Attempts | Scored tokens or unknown | Repairs and outcomes | Effective flow | Failure(s) |
|---:|---:|---|---:|---:|---:|---|---|---|
| 1 | | | | | | | | |
| 2 | | | | | | | | |

Do not calculate an efficiency winner from an unverified token total. If a requested planned flow did not receive/use a planning response, record the effective flow as single and retain the planning failure/skip reason from the trace.

## Browser checks

- Opened `index.html` locally in Chromium with network disabled: 
- Initial visual, symbols, and units are readable: 
- Control 1 changed; observed calculation and visual: 
- Control 2 changed; observed calculation and visual: 
- Exploration 1 preset: expected / observed / why: 
- Exploration 2 preset: expected / observed / why: 
- Edge case operated (zero, equal, extreme, invalid edit): 
- Source claim compared with the cited section: 
- Simplification and limitation are clearly marked: 
- No remote asset, API key, console error, `NaN`, or `Infinity`: 

## Team estimate and defects

| Criterion | Max | Estimated score | Evidence / defect |
|---|---:|---:|---|
| Scientific accuracy and fidelity | 25 | | |
| Teaching clarity | 20 | | |
| Visual explanation | 15 | | |
| Working interaction | 15 | | |
| Autonomous generation and checks | 10 | | |

Quality subtotal (out of 85): 

Efficiency comparison is relevant only if the quality subtotal is at least 50. Record token and latency comparisons separately from the quality estimate.

| Defect ID | Minimal reproduction | Expected behavior | Owner path | Fix commit | Retest result |
|---|---|---|---|---|---|
| | | | | | |

