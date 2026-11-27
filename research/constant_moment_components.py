"""Separate two computed constant-gap response terms on all cached support.

These are diagnostics within the shared native approximation, not separately
validated physical paramagnetic/diamagnetic observables or an error bound.
"""
import argparse
import json
import math
from pathlib import Path

from anisotropic_moment_analysis import coefficients
from cell_moment_cache import read_pair
from fetch_public_response_inputs import digest
from moment_analysis import analyze as native_controls


def components(dims, physical, raw, beta, gap):
    nx,first,last,cells,sides=dims
    count=nx*(last-first+1)*cells
    thermal,curvature=zip(*(coefficients(x,gap,beta) for x in raw['xi0']))
    weights=[x/(physical[1]*physical[0]**2) for x in raw['dx0']]
    result=[]
    for side in range(sides):
        indices=range(side*count,(side+1)*count)
        v=math.fsum(weights[i%nx]*thermal[i%nx]*raw['second'][i] for i in indices)
        h=math.fsum(weights[i%nx]*curvature[i%nx]*raw['curvature'][i] for i in indices)
        result.append(dict(thermal_velocity_squared=v,curvature_term=h,total=v+h))
    return result


def analyze(directory):
    root=Path(directory);controls=native_controls(root/'velocity-moments.txt')
    dims,physical,raw,_=read_pair(root)
    if (dims[:3]!=controls['dimensions'][:3] or dims[3]!=controls['dimensions'][4]
            or dims[4]!=2 or not math.isclose(physical[0],controls['qnorm'],rel_tol=1e-14)
            or not math.isclose(physical[1],controls['volume'],rel_tol=1e-14)):
        raise ValueError('Moment cache and native diagnostic contexts differ')
    cases=[]
    for control in controls['cases']:
        temperature=control['temperature_kelvin']
        rows=components(dims,physical,raw,157887.51240203338/temperature,1.5/13605.693122994)
        for row in rows:
            error=abs(row['total']-control['fine_grid_reference'])
            if error>1e-12+1e-9*abs(control['fine_grid_reference']):
                raise ValueError('Component sum does not reproduce native fine quadrature')
            row['native_fine_reference_difference']=error
        cases.append(dict(temperature_kelvin=temperature,imposed_gap_mev=1.5,grids=rows))
    paths=[root/'velocity-moments.txt']+[root/f'cell-moments-{phase}.{suffix}'
        for phase in ('raw','averaged') for suffix in ('txt','bin')]
    return dict(cases=cases,dimensions=dims,physical=physical,support_filter_applied=False,
                units='Same atomic-unit diagnostic normalization as native fine_grid_reference',
                sha256={str(p):digest(p) for p in paths},scope=__doc__.strip())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('directory',type=Path)
    print(json.dumps(analyze(**vars(parser.parse_args())),indent=2,allow_nan=False))
