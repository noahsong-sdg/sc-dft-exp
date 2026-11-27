"""Separate same-grid band regeneration from the registered grid-refinement series."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(plan_path, series_path, regenerated_path, plan_sha256):
    plan_path,series_path,regenerated_path=map(Path,(plan_path,series_path,regenerated_path))
    if digest(plan_path)!=plan_sha256:
        raise ValueError('Changed prospective regeneration plan')
    plan=json.loads(plan_path.read_text())
    if plan.get('original_third_grid_hypothesis_unchanged') is not True:
        raise ValueError('Original grid comparison must be preserved')
    series=json.loads(series_path.read_text());new=json.loads(regenerated_path.read_text())
    base=series_path.resolve().parent.parent
    for name,expected in series['sha256'].items():
        source=Path(name) if Path(name).is_absolute() else base/name
        if digest(source)!=expected:
            raise ValueError('Changed registered series source')
    receipt=new['terminal_receipt']
    if (new.get('diagnostic_readback_pass') is not True or new.get('all_declared_inputs_unchanged') is not True
            or receipt.get('status')!='PASS' or receipt.get('exit')!=0 or receipt.get('error') is not None
            or receipt.get('continuous_deadline_s')!=120
            or new['native_controls']['dimensions']!=[100,6,7,32**3,512]):
        raise ValueError('Expected qualified automatic32 response')
    cases=new['native_controls']['cases']
    if ([c['temperature_kelvin'] for c in cases]!=[2,4,8]
            or [c['temperature_kelvin'] for c in series['cases']]!=[2,4,8]
            or any(c['imposed_gap_mev']!=1.5 or not math.isfinite(c['fine_grid_reference']) for c in cases)):
        raise ValueError('Changed fixed-gap temperature context')
    fourth64_path=next(Path(p) for p in series['sha256'] if Path(p).name=='public_indexed_fourth_response64_result.json')
    if not fourth64_path.is_absolute():
        fourth64_path=base/fourth64_path
    if json.loads(fourth64_path.read_text())['cache_physical']!=new['cache_physical']:
        raise ValueError('Changed volume or imposed momentum')
    rows=[]
    for old,control in zip(series['cases'],cases):
        a,b,c,r=old['fourth32'],old['fourth48'],old['fourth64'],control['fine_grid_reference']
        if a==0 or r==0 or b==a:
            raise ValueError('Undefined regeneration comparison ratio')
        rows.append(dict(temperature_kelvin=control['temperature_kelvin'],released32=a,
            regenerated32=r,fourth48=b,fourth64=c,regeneration_fraction=r/a-1,
            regeneration_shift_over_original32to48=(r-a)/(b-a),
            consistent_generation32to48_fraction=b/r-1,consistent_generation48to64_fraction=c/b-1))
    paths=[plan_path,series_path,regenerated_path,Path(__file__)]
    return dict(cases=rows,original_third_grid_comparison_preserved=True,
        continuum_error_bounded=False,physical_response_verified=False,
        sha256={str(p):digest(p) for p in paths},scope=__doc__.strip())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('plan_path','series_path','regenerated_path'):
        parser.add_argument(name,type=Path)
    parser.add_argument('--plan-sha256',required=True)
    print(json.dumps(compare(**vars(parser.parse_args())),indent=2,allow_nan=False))
