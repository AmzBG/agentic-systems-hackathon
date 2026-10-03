"""Independent attention references; explicit semantic aliases fail on ambiguity."""
from __future__ import annotations
import argparse, json, math, random, re
from pathlib import Path
from check_entropy_oracle import _runtime_payload
from check_practice_oracles import verify_page

def review(page):
    spec = _runtime_payload(page.read_text(encoding='utf-8'))['spec']
    def select(pattern, kind=None):
        found=[c for c in spec['controls'] if (kind is None or c['kind']==kind)
               and re.search(pattern,c['id']+' '+c['label'],re.I)]
        if len(found)!=1: raise ValueError('ambiguous control: '+pattern)
        return found[0]
    q=select(r'query|queries|\bq\b|q_', 'matrix')
    k=select(r'key|keys|\bk\b|k_', 'matrix')
    v=select(r'value|values|\bv\b|v_', 'matrix')
    scaling=select(r'scal', 'toggle')
    defaults={c['id']:c['default'] for c in spec['controls']}
    def ref(inputs):
        Q,K,V=(inputs[c['id']] for c in (q,k,v))
        raw=[[sum(a*b for a,b in zip(row,key)) for key in K] for row in Q]
        scores=[[x/(math.sqrt(len(K[0])) if inputs[scaling['id']] else 1) for x in row] for row in raw]
        maxima=[max(row) for row in scores]
        exps=[[math.exp(x-max(row)) for x in row] for row in scores]
        weights=[[x/sum(row) for x in row] for row in exps]
        output=[[sum(row[j]*V[j][col] for j in range(len(V))) for col in range(len(V[0]))] for row in weights]
        values=dict(raw=raw,scaled=scores,exp=exps,max=maxima,weights=weights,output=output,rowsums=[sum(row) for row in weights])
        aliases={'scores':'raw','raw_scores':'raw','scores_raw':'raw','dot_products':'raw',
                 'scaled_scores':'scaled','scores_scaled':'scaled','score_matrix':'scaled',
                 'weights':'weights','attention_weights':'weights','attn_weights':'weights',
                 'output':'output','attn_output':'output','attention_output':'output','attended_values':'output',
                 'exp_shifted':'exp','shifted_exp':'exp','row_max':'max',
                 'rowsums':'rowsums','row_sums':'rowsums'}
        expected={}
        for o in spec['outputs']:
            if o['id'] not in aliases: raise ValueError('unmapped output '+o['id'])
            semantic = aliases[o['id']]
            if o['id']=='scores':
                if 'raw' in o['label'].lower(): semantic='raw'
                elif 'softmax' in o['label'].lower(): semantic='scaled'
                else: raise ValueError('ambiguous scores label')
            expected[o['id']]=values[semantic]
        return expected
    trials=[('defaults',defaults)]+[(f'preset{i}',{**defaults,**e['preset']}) for i,e in enumerate(spec['explorations'])]
    zero=[[0]*q['shape'][1] for _ in range(q['shape'][0])]
    trials += [('equal_scores',{**defaults,q['id']:zero}),('unscaled',{**defaults,scaling['id']:False})]
    rng=random.Random(503)
    for index in range(12):
        inputs=dict(defaults)
        for c in (q,k,v):
            inputs[c['id']]=[[rng.uniform(c['min'],c['max']) for _ in range(c['shape'][1])] for _ in range(c['shape'][0])]
        inputs[scaling['id']]=bool(index%2)
        trials.append((f'seeded{index}',inputs))
    for side in ('min','max'):
        inputs=dict(defaults)
        for c in (q,k,v): inputs[c['id']]=[[c[side]]*c['shape'][1] for _ in range(c['shape'][0])]
        trials.append(('boundary_'+side,inputs))
    results={name:verify_page(page,inputs,ref(inputs)) for name,inputs in trials}
    return dict(ok=all(r['ok'] for r in results.values()),mapping={'q':q['id'],'k':k['id'],'v':v['id'],'scaling':scaling['id']},trials=results)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    try: result=review(args.output/'index.html')
    except Exception as exc: result=dict(ok=False,error=type(exc).__name__,detail=str(exc))
    print(json.dumps(result,indent=2));return 0 if result['ok'] else 1

if __name__=='__main__': raise SystemExit(main())
