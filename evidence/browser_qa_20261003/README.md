# Real browser QA handoff — User 2 to User 3

3 October 2026, approximately 14:56–15:24 Beirut. Actual UI tests used the permitted Codex In-app Browser Chromium surface over loopback HTTP, not a DOM double. No paid calls, generated artifact edits, or runtime fixes were made by this QA task. Full network-disabled verification remains **UNVERIFIED**, explicitly selected by the user. Final User 2 freeze is **PENDING**.

## Provenance and environment

- Entropy: unchanged tracked `examples/entropy/index.html`, generated on `84c31ac4b76d570566f4f4732cebf08ef25ba9a6` per the release manifest. Real DeepSeek single/low run, one request, no repairs, nondegraded exit 0; final trace 46.609 s. HTML SHA256 `ed4d813f62cb0d1fc2199803a5144cf89a8dc4902415b140a8a6591851d1723d`.
- Attention: unchanged U1-supplied `evidence/u1-runs/stage2/T-attention-4/index.html`. Producing SHA `fc2844f5101ba343410929462246fb41e9c26f87` is U1-manifest provenance, not stamped in the trace. DeepSeek single/low/throughput, one request, no repairs, nondegraded exit 0; final trace 43.641 s. HTML SHA256 `0bb9adee3e1a45b4cab2049d5395a7d91a5b9f2fba3ba1ba16a460deafdb064b`. This is retained generation, not generation by final main.
- Browser: Codex In-app Browser, Chromium. Actual inbound HTTP User-Agent reports **Chrome/154.0.0.0**, Windows. Binary patch version is not independently verified; internal version navigation was denied by URL policy and not bypassed. See `http-requests.jsonl`.
- Both original pages tested at **1440×1000, 768×1024, 390×844** CSS viewport sizes. Document client/scroll widths matched: **1425/1425, 753/753, 375/375** (scrollbar accounts for 15 pixels).
- Initial HEAD `5f3cddc28ee82ce85929e28b0efb45cc1bf88c42`; main advanced concurrently through `fad2a24` and `5bcd4e3`. Original embedded trusted JS matched the interpreter/runtime.js templates at that boundary. Artifact and runtime hashes are in `environment.json`; later renderer changes are not covered by the original artifact tests.
- HTTP: `python -m http.server 8765 --bind 127.0.0.1`; then a stdlib server on 8766 logged method/path/status/User-Agent. Both original pages returned HTTP 200. No external model/source fetch was performed.

## Required checklist on the original artifacts

| Check | Entropy | Generated Attention | Actual observation |
|---|---|---|---|
| Opens successfully | PASS | PASS | HTTP 200; teaching, native controls, SVGs, tables and computed outputs present. |
| Unexpected console errors | PASS | PASS | Browser console API returned zero warnings/errors throughout load, edits, presets, invalid edits and source-disconnected retests. |
| Runtime network dependency | PASS within observed setup | PASS within observed setup | Single-document load, embedded CSS/JS/SVG, validator locality PASS; interactions continued after the serving source was stopped. No external dependency identified. Full DevTools request capture was unavailable. |
| Fully network-disabled browser | UNVERIFIED | UNVERIFIED | API has no offline switch. User chose to keep this unverified. Stopping HTTP is separate evidence, not a substitute. |
| Initial values and visual | PASS | PASS | Entropy p=[.25,.25,.25,.25], c=[.5,.5,.5,.5], H=2; 13 self-checks pass. Attention scores=[[.7071068,0],[.7071068,.7071068]], weights/output=[[.6697615,.3302385],[.5,.5]], rowsums=[1,1]; 12 checks pass. |
| At least two meaningful controls | PASS | PASS | Entropy weight and count change values/bar geometry. Attention Q/K edits change scores, heatmap values/colors and output; V changes the weighted output. |
| Both explorations | PASS | PASS | Exact preset results below; prediction disclosures reveal Observe/Explain. |
| Intermediate coherence | PASS | PASS | Followed probabilities→contributions→H and scores→weights→row sums→weighted output using displayed values and independent arithmetic. |
| Invalid edits retain valid state | PASS | PASS | Empty and `1e309` edits restore the previous input, mark aria-invalid=true, show finite-number error, retain all prior readouts. |
| No NaN/Infinity | PASS for tested states | PASS for tested states | Defaults, edits, presets, Entropy all-zero convention and rejected nonfinite edits contain finite numeric readouts. |
| Source/toy/simplification/limitation readable | PASS | PASS | FROM PAPER and SIMPLIFICATION badges, paper/section citations, and limitation text readable at 390px. Toy choices are explicit prose; neither spec declares a separate example badge. |
| Tab/focus usable | PASS | PASS | Native Tab reaches sequential inputs, presets, disclosure summaries and overflowing chart containers; amber focus outline observed. No trap encountered. |
| Important controls usable by keyboard | PASS | PASS | Number edits commit on Tab; Entropy count Down works. Q/K/V typed edits, scaling Space, d_k Right, presets Enter/Space, disclosures Enter work. |
| Desktop layout | PASS | PASS | At 1440px controls/readouts/visuals readable; no essential overlap or document overflow. |
| Tablet layout | PASS | PASS | Same at 768px; charts and numeric tables remain readable. |
| Mobile layout / essential clipping | PASS | PASS, with label warning | At 390px input grid fits; prose/results wrap; 600px charts scroll internally. Tab and Right scroll charts (Attention scrollLeft 0→40); companion tables expose every value. No essential content is inaccessible. |

## Exact interaction observations

Entropy native edits: certainty preset n=2,w=[1,0,0,0,0,0] gives p=[1,0],c=[0,0],H=0. Setting the second weight to1 gives p=[.5,.5],H=1; then first weight .5 gives p=[.3333333,.6666667],c=[.5283208,.389975],H=.9182958. Uniform-four preset gives H=2; keyboard count 4→3 gives three probabilities .3333333, contributions .5283208 and H=1.584963. Bars change count/heights. All-zero active weights give p=[0,0],c=[0,0],H=0 under the prominently disclosed invalid-distribution teaching convention. Values above the declared weight max1 clamp to1. Empty/nonfinite edits preserve the last valid state.

Attention edits, sequentially from default: Q11 1→2 gives first score1.414214 and weight .8044297; K11 1→2 gives score2.828427 and weight .9441928; V11 1→2 preserves scores/weights and changes O11 to1.888386 (second output row [1,.5]). Scaling off gives scores[[4,0],[1,1]], weights[[.9820138,.01798621],[.5,.5]], O[[1.964028,.01798621],[1,.5]]. All row sums remain[1,1]. Equal-keys exploration gives scores .7071068 throughout, weights/output .5 throughout. Dominant-unscaled exploration gives scores[[6,0],[0,1]], weights/output[[.9975274,.002472623],[.2689414,.7310586]]. At default, keyboard d_k 2→3 gives first score .5773503 and weight .6404575; Tab advances to scaling. Heatmaps visibly change with scores/weights. Rounded readouts are not full-precision calculation evidence.

After the 8766 source server was stopped, already-loaded original pages still operated: Entropy uniform-four then first weight .5 gave p=[.1428571,.2857143,.2857143,.2857143], c=[.4010507,.5163871,.5163871,.5163871],H=1.950212. Attention both presets returned the exact values above, with rowsums[1,1]. `1e309` rejection still worked on both. Server connection probes timed out and netstat showed no listener; browser/OS internet access stayed enabled. Both validators also passed independently (9 trace events, one request each); those are supplemental static/trace checks.

## Defects, changes and freeze boundary

**No browser-proven User 2 runtime defect found; no runtime fix or new regression test was justified.** One generated Attention teaching warning was reproduced: `scores_heat` and `weights_heat` have y_label=`query index i` but shared labels=`["key 1","key 2"]`; the browser consequently names query rows “key1/key2”. Expected: neutral shared indices or otherwise correct query/key labeling within the frozen schema. This is U1-supplied spec content, preserved unchanged and routed to U1/U3. Existing U3 prose/invariant warnings in `../reviews/attention.md` also remain; successful browser mechanics do not resolve them.

A separate UI task concurrently published stylesheet redesign `ea0b76b` and workbench change `56ff71c`; this QA task neither authored nor reverted them. Supplemental copies at `out/browser-qa/current-css/{entropy,attention}/index.html` replaced ONLY the historical stylesheet with the `ea0b76b` stylesheet, preserving spec/AST/script/teaching. These copies passed all three width/overflow inspections, console checks and spot interaction checks; screenshots prefixed `current-css-` are **stylesheet retests, not generated artifacts or full latest-renderer certification**. Subsequent runtime/layout/JS refinements in that active chat need their own current-page browser tests.

User 2 remains feature-frozen **for this QA task**, with no implementation edits. **Do not declare the final renderer/runtime frozen or release-ready**: full network-disabled verification is explicitly unverified, current-main renderer work is still advancing, and retained generated Attention carries teaching warnings. Coordinate a stable final renderer/artifact boundary, rerun affected actual-browser checks, and retain the network gap unless explicitly tested. No paid regeneration is authorized by this task.

Screenshots: original `attention-{desktop,tablet,mobile}.jpg` and `entropy-mobile.jpg` are full-page captures; `attention-mobile-viewport.jpg` is the compact original-page keyboard-slider result. `environment.json` records hashes, scope and connection findings. The HTTP capture contains only loopback test requests and reported User-Agent.
