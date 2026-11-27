"""Qualify exact response exports against a prospectively frozen baseline.

Timing ratios describe one pair of native runs, not statistical or end-to-end
speedups. Physical accuracy remains outside this comparison.
"""
import argparse
import json
from pathlib import Path

from fetch_public_response_inputs import digest
from verify_refined_response import verify

EXPORTS = frozenset(('velocity-moments.txt', 'response-assignment.txt',
    'response-assignment.bin', 'response-symmetry.txt', 'cell-moments-raw.txt',
    'cell-moments-raw.bin', 'cell-moments-averaged.txt', 'cell-moments-averaged.bin'))


def compare(directory, manifest_path, grid=48):
    root=Path(directory).absolute()
    manifest=json.loads(Path(manifest_path).read_text())
    baseline=manifest['baseline_exports']
    if len(baseline)!=len(EXPORTS) or {x['name'] for x in baseline}!=EXPORTS:
        raise ValueError('Expected all eight unique prospective baseline exports')
    # Validate the source identities as well as candidate output equality.
    for item in baseline:
        source=Path(item['path'])
        if (source.name!=item['name'] or source.stat().st_size!=item['bytes']
                or digest(source)!=item['sha256']):
            raise ValueError('Changed frozen baseline: '+item['name'])
    checked=verify(root,manifest_path,guard_seconds=manifest['guard_seconds'],grid=grid)
    comparisons=[]
    for item in baseline:
        candidate=root/item['name']
        actual=digest(candidate)
        same=candidate.stat().st_size==item['bytes'] and actual==item['sha256']
        if not same:
            raise ValueError('Response export differs: '+item['name'])
        comparisons.append(dict(name=item['name'],expected_sha256=item['sha256'],
            actual_sha256=actual,bitwise_equal=True))
    checked.update(comparison=comparisons,all_eight_exports_bitwise_equal=True,
        equivalence_scope=__doc__.strip())
    return checked


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('manifest_path',type=Path)
    parser.add_argument('--grid',type=int,choices=(48,64),default=48)
    print(json.dumps(compare(**vars(parser.parse_args())),indent=2,allow_nan=False))
