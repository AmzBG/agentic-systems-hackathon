# Recovery update

Default Attention runs reproduced truncated model responses, malformed JSON, schema errors and numerical failures. This change retains parseable invalid regenerations, uses remaining hard-budget tokens for detected failures, and allows up to three repairs. For the profiled model in automatic mode, a truncated response switches subsequent recovery requests to reasoning disabled. Explicit reasoning choices remain authoritative.

The CLI, model ID, schema and safety checks remain intact. Hard limits remain 30,000 completion tokens, 10 requests and the existing deadlines. Normal optional calls keep the soft gate; bounded recovery records its allowance in the trace.

Validation: isolated Python 3.11 full suite passed 172 tests. Two live runs of the preceding two-repair adaptive version yielded one default pass and one page rejected by numerical checks after recovering from an empty truncated response. The new third-repair policy is covered by deterministic regressions and has not been tested in a fresh live run. No claim of guaranteed generation or scientific accuracy is made. Generated outputs were not manually edited.
