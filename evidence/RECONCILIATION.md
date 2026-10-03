# Current-main reconciliation — 3 October 2026

No production functions changed and no paid model calls made. U1-U3-007 is already closed by `ba4c462` and the core interpreter check; U1-U3-008 is already closed by `df66028`. Reasoning support in `scripts/run_all.py` already exists. These were inspected, not reimplemented. `agent.DEFAULT_REASONING` remains `low`; single is the submission flow per current AI.md.

## Command evidence

| Command (Python executable `.venv/Scripts/python.exe`) | Result |
|---|---|
| `-m unittest discover -s tests -q` at `faa6de3` | PASS, 126 tests, 32.779 s |
| Same at newly synced `84aa039` | PASS, 133 tests, 32.074 s |
| `scripts/verify_install.py` | First attempt failed: Windows `py -3.11` launcher did not find installed Python |
| `scripts/verify_install.py --python .venv/Scripts/python.exe` | Sandbox network failure at pip install; retry with approved network access PASS: Python 3.11, pinned wheels, QuickJS limit and suite |
| Clean temporary clone of `faa6de33688f010d8effaaa3c3cd383c38eaafce`, same verify command with absolute launcher | PASS, fresh venv, pinned wheel-only install, QuickJS limits and tests; audit and showcase validator PASS |
| `scripts/audit_repo.py` | PASS; no failures |
| `scripts/validate_output.py --output examples/entropy` | PASS; complete 18-event trace, 3 requests, verified usage |
| `scripts/check_entropy_oracle.py --output examples/entropy` | PASS; probabilities, contributions and total for uniform/certainty (six comparisons) |

The temporary clone was fast-forwarded to `84aa039` for an additional fresh-install check after upstream core changes: PASS for Python 3.11, pinned wheel-only install, QuickJS execution limits and unittest. Final clean-clone generation and offline browser proof are NOT implied by an install/suite check. No model requests were issued by these checks. Expected failure-path messages printed by unittest are not failing tests.

## Retained evidence and limits

The tracked showcase remains the real earlier production run: 64.156 s, 12,632 prompt + 14,583 completion = 27,215 scored tokens; 10,063 reasoning tokens are a completion subset. First targeted repair failed parsing; second was accepted. No current-main regeneration is claimed. Paired entropy evidence retains all four traces and independent validations; planning added requests/tokens without demonstrated gain for this case only.

Manual source findings and honest browser SKIPs are recorded in `reviews/entropy.md` and `reviews/attention.md`. Entropy's scoped science review passes. Attention's scoped fixture review passes, but its generated output is unavailable here. Browser access was previously denied by an administrator security barrier; no bypass or harness-as-browser claim.

U1-U3-010/011 warn that earlier decay, least-squares and Attention baseline runs skipped numerical execution. Treat these as reported degraded results, not verified six-case success. `rg --files` and the local output inventory expose only hidden-like inputs, not their generated HTML/spec/trace bundles. Repair commentary and 156.2 s Attention timing are attributed to User 1, not independently reproduced. The existing independent decay identity checks a finite half-life; an arbitrary finite sentinel at zero decay rate must not be called the physical half-life.

Remaining owners: User 1 supplies existing generated outputs/specs/traces and resolves source/core issues; User 2 supplies real-browser evidence; User 3 reviews those artifacts without duplicate paid calls. Unfetched-source comparison remains interrupted/unknown usage. Optimization phase remains deferred until browser and generated scientific reviews are complete.
