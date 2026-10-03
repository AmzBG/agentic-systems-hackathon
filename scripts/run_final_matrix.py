"""Bounded live release evidence using the ordinary required CLI and defaults."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))
from agent import load_dotenv
from validate_output import validate_output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--env-file', type=Path, required=True)
    parser.add_argument('--deadline-seconds', type=int, default=1200)
    args = parser.parse_args()
    load_dotenv(args.env_file)
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    args.output.mkdir(parents=True, exist_ok=False)
    cases = [('attention-1','examples/attention/case.json'),
             ('attention-2','examples/attention/case.json'),
             ('entropy','examples/entropy/case.json'),
             ('attention-strict','practice/release_test_pack/cases/05_attention_stability.json'),
             ('least-squares','practice/cases/least_squares_loss.json')]
    deadline = time.monotonic() + args.deadline_seconds
    rows = []
    for name, relative in cases:
        remaining = deadline - time.monotonic()
        if remaining < 60:
            rows.append(dict(name=name,status='skip',reason='release window',code_sha=sha))
            continue
        target = args.output / name
        source = ROOT / relative
        started = time.monotonic()
        command = [sys.executable, str(ROOT/'agent.py'), '--input', str(source),
                   '--output', str(target), '--model', 'deepseek/deepseek-v4.1-flash']
        try:
            process = subprocess.run(command, cwd=ROOT, env=dict(os.environ),
                                     timeout=min(600,remaining), capture_output=True, text=True)
            code = process.returncode
        except subprocess.TimeoutExpired:
            code = None
        report = validate_output(target, expected_model='deepseek/deepseek-v4.1-flash')
        row = dict(name=name, input=relative, code_sha=sha, python=sys.version.split()[0],
                   input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   exit_code=code, elapsed_seconds=round(time.monotonic()-started,3),
                   cli='python agent.py --input case.json --output out --model deepseek/deepseek-v4.1-flash',
                   defaults='single / reasoning auto -> profile low; adaptive truncation recovery allowed',
                   status='pass' if code == 0 and report['ok'] else 'fail', validation=report)
        target.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target/'case.json')
        row['hashes'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in target.iterdir() if p.is_file()}
        (target/'run.json').write_text(json.dumps(row,indent=2),encoding='utf-8')
        rows.append(row)
        (args.output/'summary.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
        print(json.dumps({k:row[k] for k in ('name','status','exit_code','elapsed_seconds')}) ,flush=True)
    (args.output/'summary.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    return 0 if all(row['status']=='pass' for row in rows) else 1

if __name__ == '__main__':
    raise SystemExit(main())
