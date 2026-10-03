# Acceptance checklist

## Required execution

- Python 3.11 installs all pinned packages from `requirements.txt`.
- `python agent.py --input case.json --output out --model MODEL_ID` is sufficient.
- The process exits `0` on success and nonzero on failure.
- A successful run creates `out/index.html` and `out/trace.jsonl`.
- The run stays below 10 minutes, 10 API requests including retries, and 30,000 completion tokens.
- Every model call uses the command-line `MODEL_ID` through OpenRouter.

## Generated explanation

- Introduces the focused idea, why it matters, and all important symbols.
- Uses language suitable for the requested audience.
- Contains a meaningful labeled diagram, plot, animation, or simulation.
- Provides at least two controls that change relevant calculations or visuals.
- Computes numerical values in executable JavaScript rather than using canned values or images.
- Shows useful intermediate values.
- Includes two guided explorations: change, observation, and explanation.
- States a limitation, assumption, or common misconception.
- Names the paper and relevant section or equation.
- Distinguishes paper-supported claims from toy examples and simplifications.
- Does not imply that a toy demonstration reproduces experimental results.

## Offline and browser behavior

- The page is one self-contained HTML file with embedded CSS, JavaScript, and visuals.
- No CDN, remote font, remote image, runtime fetch, API key, server, or build step is needed.
- Controls initialize and update correctly in local Chromium.
- Valid edge cases do not produce `NaN`, `Infinity`, broken layouts, or unreadable labels.
- Keyboard focus, labels, contrast, and responsive layout are usable.

## Trace evidence

- Each line is one valid JSON object with `stage`, `action`, and `result`.
- The trace records elapsed time, checks, failures, and revisions.
- Every API call records prompt and completion token usage.
- Credentials, prompts containing secrets, and hidden reasoning are never logged.

## Submission

- `agent.py`, `requirements.txt`, README, team members, architecture, setup, and reuse credits are present.
- A tracked example input/output pair is present.
- The instructor can read the private repository.
- The submitted full commit SHA is the intended frozen revision.

