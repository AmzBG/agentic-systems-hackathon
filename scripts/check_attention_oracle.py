"""Independent matrix Attention review for supplied pages (no API calls)."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from check_entropy_oracle import _runtime_payload
from check_practice_oracles import verify_page


def expected_attention(inputs: dict) -> dict:
    q, k, v = inputs['q'], inputs['k'], inputs['v']
    divisor = math.sqrt(inputs.get('dk', len(q[0]))) if inputs['scale_on'] else 1
    scores = [[sum(a * b for a, b in zip(query, key)) / divisor for key in k] for query in q]
    weights = []
    for row in scores:
        exponentials = [math.exp(value - max(row)) for value in row]
        weights.append([value / sum(exponentials) for value in exponentials])
    output = [[sum(row[j] * v[j][column] for j in range(len(v)))
               for column in range(len(v[0]))] for row in weights]
    return {'scores': scores, 'weights': weights, 'rowsums': [sum(row) for row in weights],
            'top_weight': max(weights[0]), 'output': output}


def verify_attention_page(page: Path) -> dict:
    spec = _runtime_payload(page.read_text(encoding='utf-8'))['spec']
    defaults = {control['id']: control['default'] for control in spec['controls']}
    trials = [('default', defaults)]
    trials += [('preset_' + str(i + 1), {**defaults, **item['preset']})
               for i, item in enumerate(spec['explorations'])]
    identity = {'q': [[1, 0], [0, 1]], 'k': [[1, 0], [0, 1]],
                'v': [[2, 0], [0, 4]], 'dk': 2, 'scale_on': True}
    if 'dk' not in defaults:
        identity.pop('dk')
    trials += [('identity_scaled', identity), ('identity_unscaled', {**identity, 'scale_on': False}),
               ('zero_scores_value_average', {**identity, 'q': [[0, 0], [0, 0]]})]
    output_ids = [output['id'] for output in spec['outputs']]
    results = {}
    for name, values in trials:
        expected = expected_attention(values)
        expected['row_sums'] = expected['rowsums']
        # Explicit mathematical aliases for the two supplied matrix-page schemas.
        # Unknown IDs fail rather than silently omit an output comparison.
        results[name] = verify_page(page, values, {key: expected[key] for key in output_ids})
    return {'ok': all(result['ok'] for result in results.values()), 'page': str(page),
            'mapping': 'q/k/v + scale_on; divisor from dk control or key width; rowsums/row_sums aliases',
            'trials': results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = verify_attention_page(args.output / 'index.html')
    except Exception as exc:
        report = {'ok': False, 'error': type(exc).__name__, 'detail': str(exc)[:300]}
    print(json.dumps(report, indent=2))
    return 0 if report['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
