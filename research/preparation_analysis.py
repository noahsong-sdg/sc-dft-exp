"""Validate preparation-only output; report diagnostic slopes, not predictions."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from linear_response import stiffness, released_bias


def numbers(line, count, kind=float):
    fields=line.split()
    if len(fields)!=count:
        raise ValueError('Unexpected preparation record length')
    values=list(map(kind,fields))
    if not all(map(math.isfinite,values)):
        raise ValueError('Nonfinite preparation value')
    return values


def analyze(path):
    path=Path(path)
    with path.open() as source:
        if source.readline().strip()!='# preparation-only-v1; initial gap is NOT self-consistent':
            raise ValueError('Not the preparation-only schema')
        counts=numbers(source.readline(),2,int)
        beta,volume,tpiba=numbers(source.readline(),3)
        momentum=numbers(source.readline(),3)
        bg=numbers(source.readline(),9)
        if min(counts)<=0 or min(beta,volume,tpiba)<=0:
            raise ValueError('Invalid preparation dimensions or physical scale')
        # Serialized Fortran matrix order: row index varies fastest.
        vector=[tpiba*math.fsum(bg[row+3*col]*momentum[col] for col in range(3))
                for row in range(3)]
        q=math.hypot(*vector)
        if q==0:
            raise ValueError('Nonzero preparation momentum needed for contractions')
        grids=[]
        for grid,count in enumerate(counts,1):
            states=[]
            indices=[]
            for _ in range(count):
                fields=source.readline().split()
                if len(fields)!=8:
                    raise ValueError('Expected five floats and three integer indices')
                xi,gap,weight,dxq,d2xq=numbers(' '.join(fields[:5]),5)
                owner,k,band=numbers(' '.join(fields[5:]),3,int)
                if owner!=grid or min(k,band)<=0 or weight<0:
                    raise ValueError('Invalid grid, state index or integration weight')
                states.append((xi,gap,weight,dxq/q,d2xq/q**2))
                indices.append((k,band))
            grids.append(dict(states=count,nonzero_velocity_states=sum(s[3]!=0 for s in states),
                              nonzero_curvature_states=sum(s[4]!=0 for s in states),
                              weight_sum=math.fsum(s[2] for s in states),
                              initial_gap_slope=stiffness(states,beta,volume),
                              released_reference_slope_bias=released_bias(states,beta,volume),
                              distinct_band_k_pairs=len(set(indices))))
        if source.read().strip():
            raise ValueError('Trailing preparation state data')
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),beta=beta,
                volume=volume,tpiba=tpiba,qnorm=q,grids=grids,
                scope='Initial-gap diagnostic at prepared finite-Q geometry; NOT a self-consistent or Q=0 material prediction')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state',type=Path)
    args=parser.parse_args()
    print(json.dumps(analyze(args.state),indent=2,allow_nan=False))
