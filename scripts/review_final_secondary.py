"""Explicit independent references for the retained final Entropy/LS schemas."""
import argparse,json,math,random
from check_entropy_oracle import _runtime_payload
from check_practice_oracles import verify_page
from pathlib import Path

def review(page,kind):
    spec=_runtime_payload(page.read_text(encoding='utf8'))['spec']
    defaults={c['id']:c['default'] for c in spec['controls']}
    trials=[('defaults',defaults)]+[(f'preset{i}',{**defaults,**e['preset']}) for i,e in enumerate(spec['explorations'])]
    rng=random.Random(503)
    for i in range(12):
        inputs=dict(defaults)
        for c in spec['controls']:
            if c['kind']=='toggle': inputs[c['id']]=bool(i%2)
            elif c['kind']=='vector': inputs[c['id']]=[rng.uniform(c['min'],c['max']) for _ in c['default']]
            elif c['units']=='count': inputs[c['id']]=rng.randint(int(c['min']),int(c['max']))
            else: inputs[c['id']]=rng.uniform(c['min'],c['max'])
        trials.append((f'seeded{i}',inputs))
    for side in ('min','max'):
        inputs=dict(defaults)
        for c in spec['controls']:
            if c['kind']=='toggle': inputs[c['id']]=False
            elif c['kind']=='vector': inputs[c['id']]=[c[side]]*len(c['default'])
            else: inputs[c['id']]=c[side]
        trials.append((side,inputs))
    results={}
    for name,inputs in trials:
        if kind=='entropy':
            n=int(inputs['n']);w=inputs['w'][:n];total=sum(w)
            p=[1/n]*n if inputs['uniform'] or total==0 else [v/total for v in w]
            c=[-v*math.log2(v) if v else 0 for v in p]
            expected=dict(p=p+[0]*(4-n),contrib=c+[0]*(4-n),h_max=math.log2(n),h=sum(c))
        else:
            prediction=[inputs['intercept']+inputs['slope']*x for x in inputs['xs']]
            residual=[y-p for y,p in zip(inputs['ys'],prediction)]
            squared=[v*v for v in residual]
            expected=dict(yhat=prediction,resid=residual,sq=squared,sse=sum(squared))
        if set(expected)!={o['id'] for o in spec['outputs']}: raise ValueError('unmapped schema outputs')
        results[name]=verify_page(page,inputs,expected)
    return dict(ok=all(r['ok'] for r in results.values()),trials=results)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--kind',choices=['entropy','least-squares'],required=True)
    args=p.parse_args()
    try:r=review(args.output/'index.html',args.kind)
    except Exception as e:r=dict(ok=False,error=type(e).__name__,detail=str(e))
    print(json.dumps(r,indent=2));raise SystemExit(0 if r['ok'] else 1)
