# Low vs off reasoning screening at `27f581a` (U1-U3-018)

Six real runs, one per ID, all on candidate `27f581a` from a clean `git archive` tree; Python 3.11.9 venv with pinned
requirements; model `deepseek/deepseek-v4.1-flash`; provider `{require_parameters: true, sort: throughput}`; fresh
output directories; condition order alternated per case. Command: `python agent.py --input CASE --output DIR --model
deepseek/deepseek-v4.1-flash --reasoning MODE`. Inputs carry supplied excerpts. Usage is API-reported (verified).
`oracle` = `oracle_screen.py`: every independently computed quantity must equal some page output when the page's own
AST runs in `templates/interpreter.js`, on defaults, presets, tests and extra edge inputs. Screening only, not a
ten-run quality estimate. No skipped checks in any run.

| Run | Case | Reasoning | Exit | checks_ok | Degraded | Requests | Repairs att/acc | Prompt | Completion | Reasoning | Total | Agent s | Oracle | Input sha256 |
|---|---|---|---:|---|---|---:|---|---:|---:|---:|---:|---:|---|---|
| SCR-1 | 05_attention_stability.json | low | 0 | True | False | 1 | 0/0 | 7156 | 15948 | 12404 | 23104 | 56.687 | True | 917efe4f3e53 |
| SCR-2 | 05_attention_stability.json | off | 1 | False | False | 3 | 2/0 | 19827 | 8224 | 0 | 28051 | 29.5 | n/a (exit 1) | 917efe4f3e53 |
| SCR-3 | 06_entropy_edges.json | off | 0 | True | False | 1 | 0/0 | 6669 | 2491 | 0 | 9160 | 12.188 | True | f09ffb7023b5 |
| SCR-4 | 06_entropy_edges.json | low | 0 | True | False | 1 | 0/0 | 8041 | 7548 | 4981 | 15589 | 29.485 | True | f09ffb7023b5 |
| SCR-5 | least_squares_loss.json | low | 0 | True | False | 1 | 0/0 | 9992 | 11333 | 9068 | 21325 | 46.282 | True | 4ba0f81f9b3d |
| SCR-6 | least_squares_loss.json | off | 0 | True | False | 2 | 1/1 | 13893 | 3053 | 0 | 16946 | 15.734 | True | 4ba0f81f9b3d |

Totals: low 3/3 exit 0, 3 requests, 60018 tokens (26453 reasoning), 132.5 s;
off 2/3 exit 0, 6 requests, 54157 tokens, 57.4 s.

User 1 observations for User 3's review (not certification):
- SCR-2 (attention, off) FAILED: visual output shape wrong, then page compute and the model-written Q K^T expectation disagreed by a transpose
  (measured [[1,0],[100,1]] vs expected [[1,100],[0,1]]); two repairs rejected; 28,051 tokens spent for no valid page.
- SCR-6 (least squares, off) exits 0 and computes correctly, but its first exploration text is false and
  self-contradictory: it says sse rises "from 0 at slope = 1 to 8 at slope = 2" and q_2 "from 0 to 4", then "2 to 5",
  while its own tests show sse = 2 and q_2 = 1 at both slopes; the observe field also contains a stray question. The
  single repair corrected only a test value.
- SCR-3 (entropy, off) is correct and cheapest (9,160 tokens, 12 s).
- Low runs: one request each, no repairs, oracle pass; SCR-1 states Q/K/V roles, d_k = 2 with 1/sqrt(d_k), A = P V as a
  convex combination, both requested explorations, requested shapes/ranges/defaults, stable softmax (oracle passes
  +/-1000 inputs with scaling off). SCR-3/SCR-4 implement the four weights as four scalar controls, not one vector.
User 1 decision: keep `low` for the DeepSeek V4.1 Flash profile. Off saves ~10% tokens and ~57% time over these three
cases, but lost one run outright and shipped one scientifically false explanation.
