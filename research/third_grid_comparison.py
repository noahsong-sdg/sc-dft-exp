"""Compare a held-out64-grid diagnostic to the registered32/48 continuation.

Observed contraction is not a continuum-error bound or physical validation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


def native_cases(result, grid):
    receipt=result['terminal_receipt']
    if (result.get('diagnostic_readback_pass') is not True
            or result.get('all_declared_inputs_unchanged') is not True
            or receipt.get('status')!='PASS' or receipt.get('exit')!=0
            or receipt.get('error') is not None or receipt.get('continuous_deadline_s')!=900
            or result['native_controls']['dimensions']!=[100,6,7,grid**3,512]):
        raise ValueError('Expected qualified native grid/context readback')
    cases=result['native_controls']['cases']
    if ([row['temperature_kelvin'] for row in cases]!=[2,4,8]
            or any(row['imposed_gap_mev']!=1.5 or not math.isfinite(row['fine_grid_reference']) for row in cases)):
        raise ValueError('Changed fixed-gap temperature controls')
    return cases


def compare(plan_path, matched48_path, refined64_path, plan_sha256):
    plan_path,matched48_path,refined64_path=map(Path,(plan_path,matched48_path,refined64_path))
    payload=plan_path.read_bytes()
    if hashlib.sha256(payload).hexdigest()!=plan_sha256:
        raise ValueError('Changed registered hypothesis')
    plan=json.loads(payload)
    for name,expected in plan['input_sha256'].items():
        if hashlib.sha256((plan_path.parent/name).read_bytes()).hexdigest()!=expected:
            raise ValueError('Changed prospective comparison source: '+name)
    matched=json.loads(matched48_path.read_text());refined=json.loads(refined64_path.read_text())
    if matched.get('all_eight_exports_bitwise_equal') is not True:
        raise ValueError('Combined48 probe has not passed exact-export qualification')
    previous=native_cases(matched,48);current=native_cases(refined,64)
    if matched['cache_physical']!=refined['cache_physical']:
        raise ValueError('Changed volume or imposed momentum')
    if [row['temperature_kelvin'] for row in plan['cases']]!=[2,4,8]:
        raise ValueError('Changed registered temperatures')
    rows=[]
    for frozen,old,new in zip(plan['cases'],previous,current):
        x,y,z=frozen['fourth32'],frozen['fourth48'],new['fine_grid_reference']
        if old['fine_grid_reference']!=y:
            raise ValueError('Combined48 probe differs from registered baseline')
        before=y/x-1;after=z/y-1
        rows.append(dict(temperature_kelvin=frozen['temperature_kelvin'],fourth32=x,fourth48=y,fourth64=z,
            previous_grid_fraction=before,held_out_grid_fraction=after,
            observed_change_contracts=abs(after)<abs(before),
            continued_direction=(y-x)*(z-y)>0,
            conditional64=frozen['conditional64'],
            conditional_model_discrepancy_over48={p:(z-prediction)/y for p,prediction in frozen['conditional64'].items()}))
    paths=[plan_path,matched48_path,refined64_path,Path(__file__)]
    return dict(cases=rows,contracts_at_all_temperatures=all(r['observed_change_contracts'] for r in rows),
        same_direction_at_all_temperatures=all(r['continued_direction'] for r in rows),
        continuum_error_bounded=False,physical_response_verified=False,
        sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},scope=__doc__.strip())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('plan_path','matched48_path','refined64_path'):
        parser.add_argument(name,type=Path)
    parser.add_argument('--plan-sha256',required=True,help='Previously published hypothesis identity')
    print(json.dumps(compare(**vars(parser.parse_args())),indent=2,allow_nan=False))
