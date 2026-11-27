"""Read and verify matched-quadrature velocity-moment diagnostic output."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def analyze(path):
    path=Path(path)
    lines=path.read_text().splitlines()
    if len(lines)!=8 or lines[0]!='# velocity-moment-diagnostic-v1; imposed constant gap; NOT a material prediction':
        raise ValueError('Unexpected moment diagnostic schema')
    dims=list(map(int,lines[1].split()))
    if len(dims)!=5 or min(dims)<=0 or dims[1]>dims[2]:raise ValueError('Invalid dimensions')
    q,volume=map(float,lines[2].split())
    signs=list(map(float,lines[3].split()));errors=list(map(float,lines[4].split()))
    if len(signs)!=3 or len(errors)!=3:raise ValueError('Missing diagnostic checks')
    if not all(map(math.isfinite,[q,volume,*signs,*errors])) or min(q,volume)<=0:
        raise ValueError('Invalid physical scales or nonfinite checks')
    if min(errors)<0 or signs[0]!=int(signs[0]) or min(signs)<0 or signs[1]>signs[2]:
        raise ValueError('Invalid error or signed-weight audit')
    if max(errors)>1e-12:raise ValueError('Original native first-moment path not reproduced')
    rows=[]
    for temperature,line in zip((2,4,8),lines[5:]):
        values=list(map(float,line.split()))
        if len(values)!=8 or values[0]!=temperature or not all(map(math.isfinite,values)):
            raise ValueError('Invalid thermal moment row')
        _,first0,first1,second0,second1,all0,all1,fine=values
        conservation=max(abs(all0-fine),abs(all1-fine))
        if conservation>1e-12+1e-9*abs(fine):
            raise ValueError('Second moment fails direct fine-grid conservation')
        rows.append(dict(temperature_kelvin=temperature,imposed_gap_mev=1.5,
                         mean_squared_active=[first0,first1],
                         second_moment_active=[second0,second1],
                         second_moment_all=[all0,all1],fine_grid_reference=fine,
                         direct_reference_max_absolute_error=conservation))
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),dimensions=dims,
                qnorm=q,volume=volume,native_control_max_absolute_errors=errors,
                negative_fine_weights=int(signs[0]),negative_fine_weight_absolute_sum=signs[1],
                fine_weight_absolute_sum=signs[2],cases=rows,
                scope='Matched-energy constant-gap closure diagnostic; not a converged material response')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('path',type=Path)
    args=parser.parse_args();print(json.dumps(analyze(args.path),indent=2,allow_nan=False))
