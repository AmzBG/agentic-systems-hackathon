"""Independent, explicit-output numerical review of the six retained screening runs.

Development evidence only; no model calls or production imports of case knowledge.
Prints JSON without changing the retained HTML, specs or traces.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from check_entropy_oracle import _runtime_payload, _near_active_vector
from check_practice_oracles import verify_page
from runtime import merge_inputs
from validate_output import validate_output


def reference(run: str, inputs: dict) -> dict:
    if run in ('SCR-1', 'SCR-2'):
        if run == 'SCR-1':
            q, k, v = (inputs[x] for x in ('q', 'k', 'v'))
        else:
            q = [[inputs['q11'], inputs['q12']], [inputs['q21'], inputs['q22']]]
            k = [[inputs['k11'], inputs['k12']], [inputs['k21'], inputs['k22']]]
            v = [[inputs['v1']], [inputs['v2']]]
        raw = [[sum(a*b for a, b in zip(row, key)) for key in k] for row in q]
        divisor = math.sqrt(len(k[0])) if inputs['scaling'] else 1
        scores = [[x/divisor for x in row] for row in raw]
        exp = [[math.exp(x-max(row)) for x in row] for row in scores]
        weights = [[x/sum(row) for x in row] for row in exp]
        output = [[sum(row[j]*v[j][c] for j in range(len(v)))
                   for c in range(len(v[0]))] for row in weights]
        if run == 'SCR-1':
            return dict(raw_scores=raw, scaled_scores=scores,
                        row_max=[max(row) for row in scores], weights=weights, attn_output=output)
        return dict(scores_raw=raw, scores_scaled=scores, exp_shifted=exp,
                    weights=weights, output=output)
    if run in ('SCR-3', 'SCR-4'):
        n = int(inputs['n'])
        w = [inputs[f'w{i}'] for i in range(1, n+1)]
        total = sum(w)
        p = [x/total for x in w] if total else [1/n]*n
        contributions = [-x*math.log2(x) if x else 0 for x in p]
        return {('total' if run == 'SCR-3' else 'active_sum'): total,
                'probs': p, 'contribs': contributions, 'entropy': sum(contributions)}
    if run == 'SCR-5':
        x, y = inputs['obs_x'], inputs['obs_y']
        prediction_id, square_id = 'y_hat', 'sq'
    else:
        x, y = [inputs['x1'], inputs['x2']], [inputs['y1'], inputs['y2']]
        prediction_id, square_id = 'yhat', 'sqresid'
    prediction = [inputs['intercept']+inputs['slope']*a for a in x]
    residual = [a-b for a, b in zip(y, prediction)]
    squares = [x*x for x in residual]
    return {prediction_id: prediction, 'resid': residual, square_id: squares, 'sse': sum(squares)}


def edge_inputs(run: str) -> list[dict]:
    if run == 'SCR-1':
        return [dict(q=[[1000,-1000],[-1000,1000]], k=[[1000,-1000],[-1000,1000]],
                     v=[[-20],[20]], scaling=False),
                dict(q=[[0,0],[0,0]], v=[[-20],[20]], scaling=False)]
    if run == 'SCR-2':
        return [dict(k12=100, scaling=True)]
    if run in ('SCR-3','SCR-4'):
        return [dict(w1=0,w2=0,w3=0,w4=0,n=n) for n in (1,4)] + [dict(w1=4,w2=1,w3=0,w4=4,n=3)]
    if run == 'SCR-5':
        return [dict(obs_x=[-5,5],obs_y=[8,-8],slope=5,intercept=5),
                dict(obs_x=[0,2],obs_y=[1,3],slope=.5,intercept=2.5)]
    return [dict(slope=1), dict(slope=2), dict(x1=-4,x2=4,y1=4,y2=-4,slope=4,intercept=4)]


def main() -> int:
    base = ROOT/'evidence/u1-runs/screen-27f581a'
    report = {}
    for folder in sorted(base.glob('SCR-*')):
        run = folder.name
        page = folder/'index.html'
        payload = _runtime_payload(page.read_text(encoding='utf-8'))
        spec = payload['spec']
        meta = json.loads((folder/'run.json').read_text(encoding='utf-8'))
        trials = [('default', {})] + [(f'preset_{i+1}', e['preset']) for i,e in enumerate(spec['explorations'])]
        trials += [(f'test_{i+1}', t['inputs']) for i,t in enumerate(spec['tests'])]
        trials += [(f'edge_{i+1}', p) for i,p in enumerate(edge_inputs(run))]
        results = {}
        for name, patch in trials:
            try:
                expected = reference(run, merge_inputs(spec['controls'], patch))
                result = verify_page(page, patch, expected)
                # Declared inactive slots may be retained as zeros; this does not
                # admit missing active values or reuse some unrelated output.
                if run in ('SCR-3','SCR-4'):
                    for key in ('probs','contribs'):
                        result['checks'][key] = _near_active_vector(result['observed'][key], expected[key])
                    result['ok'] = all(result['checks'].values())
                results[name] = dict(ok=result['ok'], checks=result['checks'],
                                     expected=expected, observed=result['observed'])
            except Exception as exc:
                results[name] = dict(ok=False, error=f'{type(exc).__name__}: {exc}')
        validator = validate_output(folder, expected_model='deepseek/deepseek-v4.1-flash')
        report[run] = dict(producing_commit=meta['producing_commit'],
                           input_sha256=meta['input_sha256'],
                           html_sha256=hashlib.sha256(page.read_bytes()).hexdigest(),
                           trace_sha256=hashlib.sha256((folder/'trace.jsonl').read_bytes()).hexdigest(),
                           exit_code=meta['exit_code'], reasoning=meta['reasoning_mode'],
                           attempts=validator['attempts'], usage=validator['usage'],
                           elapsed_seconds=validator['elapsed_seconds'],
                           validator_ok=validator['ok'], validator_failures=validator['failures'],
                           numerical_ok=all(r['ok'] for r in results.values()), trials=results)
    print(json.dumps(report, indent=2))
    # Failed runs are expected evidence, not grounds for suppressing the report.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
