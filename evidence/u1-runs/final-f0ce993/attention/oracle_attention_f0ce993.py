"""Independent oracle for the f0ce993 Attention page (1 query x d_k=4, 2 keys, 2-dim values, scaling toggle)."""
import json, math, sys
from pathlib import Path
from check_practice_oracles import verify_page
from check_entropy_oracle import _runtime_payload

def expected(i):
    q, k, v, on = i["q"][0], i["k"], i["v"], i["scaling"]
    dk = len(q)
    raw = [sum(a * b for a, b in zip(q, key)) for key in k]
    factor = 1 / math.sqrt(dk) if on else 1.0
    scores = [r * factor for r in raw]
    m = max(scores); ex = [math.exp(s - m) for s in scores]; w = [e / sum(ex) for e in ex]
    out = [sum(w[j] * v[j][c] for j in range(len(v))) for c in range(len(v[0]))]
    return {"raw_dot": raw, "scale_factor": factor, "scores": scores, "weights": w, "weight_sum": sum(w), "output": out}

page = Path(sys.argv[1])
spec = _runtime_payload(page.read_text(encoding="utf-8"))["spec"]
defaults = {c["id"]: c["default"] for c in spec["controls"]}
trials = [("default", defaults)] + [(f"preset_{n + 1}", {**defaults, **e["preset"]}) for n, e in enumerate(spec["explorations"])]
trials += [
    ("negative_mixed_scaled", {"q": [[-1.5, 2, 0.5, -3]], "k": [[2, -1, 0, 1.5], [-0.5, 3, -2, 1]], "v": [[3, -2], [-1, 4]], "scaling": True}),
    ("negative_mixed_unscaled", {"q": [[-1.5, 2, 0.5, -3]], "k": [[2, -1, 0, 1.5], [-0.5, 3, -2, 1]], "v": [[3, -2], [-1, 4]], "scaling": False}),
    ("zero_query_value_average", {"q": [[0, 0, 0, 0]], "k": [[5, -5, 5, -5], [1, 2, 3, 4]], "v": [[2, 5], [4, -2]], "scaling": True}),
    ("extreme_bounds_unscaled", {"q": [[5, 5, 5, 5]], "k": [[5, 5, 5, 5], [-5, -5, -5, -5]], "v": [[5, -5], [-5, 5]], "scaling": False}),
]
results = {name: verify_page(page, vals, expected({**defaults, **vals})) for name, vals in trials}
report = {"ok": all(r["ok"] for r in results.values()), "page": str(page.name),
          "mapping": "q[1x4]/k[2x4]/v[2x2]/scaling -> raw_dot/scale_factor/scores/weights/weight_sum/output; d_k = 4",
          "trials": {n: {"ok": r["ok"], "checks": r["checks"]} for n, r in results.items()}}
print(json.dumps(report, indent=1))
sys.exit(0 if report["ok"] else 1)
