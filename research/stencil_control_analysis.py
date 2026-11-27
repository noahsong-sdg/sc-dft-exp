"""Read a prospectively registered same-band64 stencil control; no accuracy bound."""
import argparse
import hashlib
import json
from pathlib import Path

from cell_moment_cache import read_pair
from third_grid_comparison import native_cases


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(plan_path, second_path, fourth_path, plan_sha256):
    plan_path,second_path,fourth_path=map(Path,(plan_path,second_path,fourth_path))
    if digest(plan_path)!=plan_sha256:
        raise ValueError('Changed prospective stencil plan')
    plan=json.loads(plan_path.read_text())
    base=plan_path.resolve().parent.parent
    for name,expected in plan['sha256'].items():
        if digest(base/name)!=expected:
            raise ValueError('Changed prospective source: '+name)
    if plan['sha256']['research/public_indexed_fourth_response64_result.json']!=digest(fourth_path):
        raise ValueError('Fourth-order result differs from prospective baseline')
    second,fourth=[json.loads(p.read_text()) for p in (second_path,fourth_path)]
    controls=[native_cases(r,64) for r in (second,fourth)]
    caches=[];paths=[plan_path,second_path,fourth_path,Path(__file__)]
    for result in (second,fourth):
        for name,expected in result['components']['sha256'].items():
            if digest(name)!=expected:
                raise ValueError('Changed qualified cache: '+name)
            paths.append(Path(name))
        caches.append(read_pair(result['terminal_receipt']['cwd']))
    if caches[0][:2]!=caches[1][:2]:
        raise ValueError('Changed same-band response context')
    for phase in (2,3):
        for name in ('xi0','dx0','dos','curvature'):
            if caches[0][phase][name]!=caches[1][phase][name]:
                raise ValueError('Changed stencil-independent cache field: '+name)
    old=json.loads((base/'research/grid_stencil_comparison.json').read_text())['cases']
    rows=[]
    for baseline,a,b in zip(old,*controls):
        t=a['temperature_kelvin'];delta=b['fine_grid_reference']-a['fine_grid_reference']
        previous=baseline['fourth48']-baseline['second48']
        predicted=plan['conditional_predictions'][str(t)]
        if predicted!=.5625*previous or predicted==0:
            raise ValueError('Changed conditional h2 prediction')
        rows.append(dict(temperature_kelvin=t,second64=a['fine_grid_reference'],fourth64=b['fine_grid_reference'],
            stencil_difference64=delta,stencil_difference48=previous,
            difference_ratio64_over48=delta/previous,conditional_prediction64=predicted,
            conditional_prediction_relative_discrepancy=delta/predicted-1,
            fourth_vs_second64_fraction=delta/a['fine_grid_reference']))
    return dict(cases=rows,dos_curvature_and_energy_axes_bitwise_equal=True,
        continuum_error_bounded=False,physical_response_verified=False,
        sha256={str(p):digest(p) for p in paths},scope=__doc__.strip())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('plan_path','second_path','fourth_path'):
        parser.add_argument(name,type=Path)
    parser.add_argument('--plan-sha256',required=True)
    print(json.dumps(compare(**vars(parser.parse_args())),indent=2,allow_nan=False))
