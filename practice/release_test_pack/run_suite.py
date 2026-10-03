"""Developer-only harness. Runs the required CLI; it does not grade science or operate a browser."""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
REQUIRED = {'stage','action','result','prompt_tokens','completion_tokens',
            'elapsed_seconds','checks','failures','revisions'}


def inspect_output(folder):
    page, trace = folder/'index.html', folder/'trace.jsonl'
    events, issues = [], []
    if not page.is_file() or not page.stat().st_size:
        issues.append('index.html missing/empty')
    if trace.is_file():
        for n,line in enumerate(trace.read_text(encoding='utf-8').splitlines(),1):
            try:
                event=json.loads(line)
                if not isinstance(event,dict) or not REQUIRED.issubset(event):
                    issues.append(f'trace line {n}: missing event keys')
                else:
                    events.append(event)
            except (ValueError,TypeError):
                issues.append(f'trace line {n}: invalid JSON')
    else:
        issues.append('trace.jsonl missing')
    if not events:
        issues.append('no valid trace events')
    calls={}
    checks=[]
    last_elapsed=-1
    for event in events:
        elapsed=event.get('elapsed_seconds')
        if not isinstance(elapsed,(int,float)) or not math.isfinite(elapsed) or elapsed < last_elapsed:
            issues.append('invalid or decreasing elapsed_seconds')
        else:
            last_elapsed=elapsed
        details=event.get('details') or {}
        if not isinstance(details,dict):
            details={}
        request=details.get('request_number')
        if request is not None:
            usage=(event.get('prompt_tokens'),event.get('completion_tokens'))
            if request not in calls or all(isinstance(x,int) and not isinstance(x,bool) and x>=0 for x in usage):
                calls[request]=usage
        for check in event.get('checks') or []:
            if isinstance(check,dict):
                checks.append({k:check.get(k) for k in ('id','status','detail')})
    final=next((e for e in reversed(events) if e.get('stage')=='final'),None)
    if final is None:
        issues.append('final event missing')
    verified=bool(calls) and all(all(isinstance(x,int) and not isinstance(x,bool) and x>=0 for x in pair) for pair in calls.values())
    prompt=sum(x[0] for x in calls.values()) if verified else None
    completion=sum(x[1] for x in calls.values()) if verified else None
    if len(calls)>10:
        issues.append('more than 10 recorded requests')
    if completion is not None and completion>30000:
        issues.append('completion token cap exceeded')
    return dict(artifact_issues=sorted(set(issues)),recorded_requests=len(calls),
                usage_status='recorded per-request usage' if verified else 'unverifiable by this harness; inspect trace',
                prompt_tokens=prompt,completion_tokens=completion,
                scored_tokens=(prompt+completion) if verified else None,
                checks=checks,final_result=final.get('result') if final else None,
                scientific_review='NOT_RUN',browser_review='NOT_RUN')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',required=True,type=Path)
    ap.add_argument('--model',required=True)
    ap.add_argument('--cases',nargs='+',help='Case stems; default 01_batch_norm 02_gaussian_kl 07_offline_unknown_field; use all for all seven')
    ap.add_argument('--repeat',type=int,default=1)
    ap.add_argument('--negative',action='store_true',help='Also run two invalid inputs; these should fail before a model call')
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    if not 1<=args.repeat<=3:
        ap.error('--repeat must be 1, 2 or 3')
    repo=args.repo.resolve()
    if not (repo/'agent.py').is_file():
        ap.error('--repo must contain agent.py')
    names=args.cases or ['01_batch_norm','02_gaussian_kl','07_offline_unknown_field']
    if names==['all']:
        names=[x.stem for x in sorted((ROOT/'cases').glob('*.json'))]
    cases=[]
    for name in names:
        path=ROOT/'cases'/f'{name}.json'
        if path.parent != ROOT/'cases' or not path.is_file():
            ap.error('unknown case: '+name)
        cases.append((path,False))
    if args.negative:
        cases += [(x,True) for x in sorted((ROOT/'invalid_inputs').glob('*.json'))]
    output=(args.output or ROOT/'results'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')).resolve()
    output.mkdir(parents=True,exist_ok=False)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=repo,capture_output=True,text=True)
    status=subprocess.run(['git','status','--porcelain'],cwd=repo,capture_output=True,text=True)
    manifest=dict(sha=git.stdout.strip() if git.returncode==0 else 'unknown',
                  dirty=bool(status.stdout.strip()) if status.returncode==0 else None,
                  model=args.model,python=sys.version,started=datetime.datetime.now(datetime.timezone.utc).isoformat())
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    bad=False
    for path,negative in cases:
        for rep in range(1,args.repeat+1):
            folder=output/f'{path.stem}_{rep}'
            command=[sys.executable,str(repo/'agent.py'),'--input',str(path),'--output',str(folder),'--model',args.model]
            start=time.monotonic()
            timeout=30 if negative else 600
            timed_out=False
            print(f'Running {path.stem} repeat {rep}; model={args.model}',flush=True)
            try:
                process=subprocess.run(command,cwd=repo,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=timeout)
                code=process.returncode
            except subprocess.TimeoutExpired:
                code=None; timed_out=True
            elapsed=time.monotonic()-start
            row=dict(case=path.stem,repeat=rep,negative_input=negative,
                     input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     code_sha=manifest['sha'],dirty=manifest['dirty'],model=args.model,
                     elapsed_seconds=round(elapsed,3),exit_code=code,timed_out=timed_out,output=str(folder))
            row.update(inspect_output(folder))
            row['exit_expectation_met']=(code is not None and (code!=0 if negative else code==0))
            # Artifact creation on invalid input is diagnostic, not a valid-case release requirement.
            if negative:
                row['invalid_input_output_notes']=row['artifact_issues']
                row['artifact_issues']=[]
            # Invalid inputs should fail promptly without API traffic; inspect trace if counts are absent.
            if negative and row['recorded_requests']:
                row['artifact_issues'].append('invalid input made a recorded API request')
            if elapsed>600:
                row['artifact_issues'].append('wall-clock limit exceeded')
            bad |= not row['exit_expectation_met'] or bool(row['artifact_issues'])
            with (output/'summary.jsonl').open('a',encoding='utf-8') as f:
                f.write(json.dumps(row,allow_nan=False)+'\n')
            print(json.dumps({k:row[k] for k in ('case','exit_code','elapsed_seconds','completion_tokens','artifact_issues')}),flush=True)
    print('Evidence:',output,'; numerical and browser reviews still required.',flush=True)
    return 1 if bad else 0


if __name__=='__main__':
    raise SystemExit(main())
