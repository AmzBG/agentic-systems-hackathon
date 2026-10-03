"""Mapping-free oracle: every reference quantity must equal some page output (page AST in templates/interpreter.js)."""
import json, math, sys
from pathlib import Path
sys.path[:0] = ["scripts", "."]
from check_practice_oracles import verify_page
from check_entropy_oracle import _runtime_payload
from runtime import merge_inputs
import quickjs

def run_page(page, inputs):
    p = _runtime_payload(page.read_text(encoding="utf-8")); trial = merge_inputs(p["spec"]["controls"], inputs)
    c = quickjs.Context(); c.set_time_limit(1); c.set_memory_limit(64 << 20)
    c.eval(Path("templates/interpreter.js").read_text(encoding="utf-8"))
    return trial, json.loads(c.eval("JSON.stringify(NumericRuntime.run(" + json.dumps(p["ast"]) + "," + json.dumps(trial) + "))"))

def near(a, b):
    if isinstance(b, list): return isinstance(a, list) and len(a) == len(b) and all(near(x, y) for x, y in zip(a, b))
    return isinstance(a, (int, float)) and abs(a - b) <= 1e-6 + 1e-6 * abs(b)

def attention(i):
    ids = {c: [k for k in i if k.lower().startswith(c)] for c in "qkv"}
    Q, K, V = (i[ids[c][0]] for c in "qkv"); on = next(v for v in i.values() if isinstance(v, bool))
    dk = len(Q[0]); f = 1 / math.sqrt(dk) if on else 1
    S = [[sum(a * b for a, b in zip(q, k)) for k in K] for q in Q]; Ss = [[x * f for x in r] for r in S]
    P = [[math.exp(x - max(r)) / sum(math.exp(y - max(r)) for y in r) for x in r] for r in Ss]
    A = [[sum(p[j] * V[j][c] for j in range(len(V))) for c in range(len(V[0]))] for p in P]
    return {"S": S, "S_scaled": Ss, "P": P, "A": A}

def entropy(i):
    lists = [v for v in i.values() if isinstance(v, list)]
    w = lists[0] if lists else [i[k] for k in sorted(k for k in i if k[0] == "w" and k[1:].isdigit())]
    n = int(next(v for k, v in i.items() if k in ("n", "count", "n_active", "active") or (not isinstance(v, (list, bool)) and not (k[0] == "w" and k[1:].isdigit()))))
    a = w[:n]; t = sum(a); p = [x / t for x in a] if t > 0 else [1 / n] * n
    c = [-x * math.log2(x) if x > 0 else 0 for x in p]
    pad = len(w) - n
    return {"p": p, "contrib": c, "H": sum(c)} if False else {"p": p, "contrib": c, "H": sum(c), "_pad": pad}

def lsq(i):
    xs = next((v for k, v in i.items() if isinstance(v, list) and "x" in k), None)
    ys = next((v for k, v in i.items() if isinstance(v, list) and "y" in k), None)
    x1, y1, x2, y2 = (xs[0], ys[0], xs[1], ys[1]) if xs else (i[k] for k in ("x1", "y1", "x2", "y2"))
    a = next(v for k, v in i.items() if "intercept" in k or k in ("a", "b0")); b = next(v for k, v in i.items() if "slope" in k or k in ("m", "b1"))
    yh = [a + b * x1, a + b * x2]; r = [y1 - yh[0], y2 - yh[1]]; s = [v * v for v in r]
    return {"yhat": yh, "resid": r, "sq": s, "sse": sum(s)}

page, kind = Path(sys.argv[1]), sys.argv[2]
ref = {"attention": attention, "entropy": entropy, "lsq": lsq}[kind]
spec = _runtime_payload(page.read_text(encoding="utf-8"))["spec"]
trials = [("default", {})] + [(f"preset_{n+1}", e["preset"]) for n, e in enumerate(spec["explorations"])] + [(f"test_{n+1}", t["inputs"]) for n, t in enumerate(spec["tests"])]
extra = json.loads(sys.argv[3]) if len(sys.argv) > 3 else []
trials += [(f"extra_{n+1}", x) for n, x in enumerate(extra)]
ok = True; out = {}
for name, inp in trials:
    try:
        trial, obs = run_page(page, inp); exp = ref(trial)
        pad = exp.pop("_pad", 0)
        for q in ("p", "contrib"):
            if q in exp and pad and not any(isinstance(o, list) and len(o) == len(exp[q]) for o in obs.values()):
                exp[q] = exp[q] + [0] * pad
        miss = [q for q, v in exp.items() if not any(near(o, v) or near(o, [v]) or (isinstance(v, list) and near(o, [[x] for x in v])) for o in obs.values())]
    except Exception as e:
        miss = [f"error {type(e).__name__}: {str(e)[:120]}"]
    out[name] = miss or "pass"; ok &= not miss
print(json.dumps({"ok": ok, "trials": out}))
