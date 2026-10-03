# Teaching-review corrections — 3 October 2026, 16:33 Beirut

Scope: the user paused the broader screening/release pass to fix the reported fixture teaching failures. No paid calls. These are deterministic practice-fixture renders, NOT fresh model generations, and they do not replace any original generated artifact or trace.

Renderer base: `7b27144b590d0fc4426b425b644e5bb802250062` (U2 visual-system changes). Fixture revisions: the commit containing this report. No compute_js, tests or invariant was removed or numerically changed in either fixture.

## Adopted corrections

- U2's upstream renderer opens notation initially; simplifies dashboard-like chrome; places the explanation before the result; fixes probability heatmap domains to 0–1 when an output has the corresponding range invariant; uses symmetric mixed-sign domains with brown negatives, neutral zero and blue positives. One-sided data intentionally stays sequential, with a visible current-domain caption. These changes were already on main; U3 did not duplicate them.
- U3 Entropy explanation now exposes weights → normalization → individual entropy contributions → sum, with equations and the existing honest uniform fallback for all-zero active weights. Computation is unchanged.
- U3 Attention first exploration now changes only `scale: false` relative to the identity defaults. Q/K/V remain fixed; observations correctly compare 0.670/0.330 scaled weights with 0.731/0.269 unscaled weights and unchanged unit row sums. The independent equal-score/averaging identity test is retained, not deleted.
- Added two focused fixture regressions in tests/test_evidence_scripts.py, including independent page-interpreter expectations for both scaling conditions.

## Verification

Python 3.11.9 with the pinned dependencies: focused evidence suite 14 PASS; full unittest discovery 170 PASS in 36.438 seconds; repository audit ok true/no failures; git diff --check clean. Expected failure-path messages in unittest output are mocked regression evidence, not paid failures.

Real Codex In-app Browser Chromium on loopback HTTP, freshly rendered pages under ignored out/teaching-fixes:

- Both pages loaded with open notation, formula/pipeline before results, FROM PAPER/SIMPLIFICATION labels, limitation and the explicit self-check caveat.
- Entropy presets yielded 0 and 2 bits; 12 checks pass. Attention keyboard Enter/Space presets yielded independent expected 0.7310585786300049 and 0.9441927807928303 diagonal weights; 10 checks pass. The probability scale stayed fixed0–1 in both.
- Native keyboard Q11 = -1 produced scores [[-1/sqrt(2),0],[0,1/sqrt(2)]]. The browser showed symmetric +/-0.7071068 bounds; negative rgb(185,140,105), zero rgb(245,246,246), positive rgb(110,157,166). The current/preset invariants still passed.
- Both pages at 390px viewport: client/scroll widths375/375 (15px scrollbar), no document overflow. Matrix controls remained readable; explicit focus outline observed. This is sampled mobile/keyboard verification, not a complete accessibility audit.
- Console capture returned no warnings/errors. Full network-disabled behavior was NOT exercised in this U3 pass; retain U2's separately scoped offline evidence without relabeling it.

Hashes (SHA256, recorded before the evidence-only commit):

| Artifact | SHA256 |
|---|---|
| practice/specs/attention.json | cf1044d045da975318b24013e3f397768a6067c5ab2caedd76bac6353267cb48 |
| practice/specs/entropy.json | 4015f2726187f395161ece418ad778508f058fa32270a9c6b9802d30c51fd343 |
| out/teaching-fixes/attention/index.html | 50852dcf5c1cf9004a05bf524378af9bac8c225ee31830106e106abd25ea4adf |
| out/teaching-fixes/entropy/index.html | f916ca8225b119be3ecfa0e738439e9c8f007d52310844adb121ed9188e17c8f |

## Remaining boundaries

The prior read-only fixture failures are addressed at this renderer/fixture boundary. This does not establish current model-generation quality, grade/efficiency, final owner freeze, public access or exact-final-SHA clean installation. U1 remains sole operator of SCR-1..6; no duplicate generation or reasoning-default change by U3. Resume the broader review only after this correction task, reconcile current inbox/main, and preserve all failed screening costs and original producing SHAs.
