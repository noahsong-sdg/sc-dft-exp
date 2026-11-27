"""Read the explicit five-float saved gap schema; do not invent curvature.

Owning historical writer: xi, delta, Z, dk, dxq, kindx, bindx. This schema
contains no temperature, momentum vector, curvature or convergence certificate.
"""
import argparse
import json
import math
from pathlib import Path
from compare_legacy_gap import digest


def counts(path):
    with Path(path).open() as source:header=source.readline().split()
    if len(header)!=3 or header[0]!='#':raise ValueError('Expected two saved-gap counts')
    values=list(map(int,header[1:]))
    if min(values)<=0:raise ValueError('Positive saved-gap counts required')
    return values


def records(path,dimensions):
    with Path(path).open() as source:
        if source.readline().split()!=['#',*map(str,dimensions)]:
            raise ValueError('Saved-gap counts differ')
        for grid,count in enumerate(dimensions):
            for state in range(count):
                line=source.readline()
                while line and not line.strip():line=source.readline()
                fields=line.split()
                if len(fields)!=7:raise ValueError('Expected five floats and two indices; no schema guessing')
                values=list(map(float,fields[:5]));indices=list(map(int,fields[5:]))
                if not all(map(math.isfinite,values)):raise ValueError('Nonfinite saved gap')
                if min(indices)<=0 or values[3]<0:raise ValueError('Invalid saved index or assigned weight')
                yield grid,state,values,indices
        if source.read().strip():raise ValueError('Trailing saved-gap data')


def summarize(path,emin=1e-7):
    dimensions=counts(path);selected=[[],[]];weights=[[],[]]
    for grid,state,values,indices in records(path,dimensions):
        xi,gap,z,weight,shift=values
        if abs(xi)<emin:
            selected[grid].append(abs(gap)*weight)
            weights[grid].append(weight)
    rows=[]
    for grid in range(2):
        total=math.fsum(weights[grid])
        if total<=0:raise ValueError('No positive Fermi-window weight')
        rows.append(dict(states=dimensions[grid],fermi_window_states=len(weights[grid]),
                         mean_absolute_gap_mev=13605.693122994*math.fsum(selected[grid])/total))
    return dict(sha256=digest(path),emin_ry=emin,grids=rows,
                scope='Five-float archive schema and gap scalar fingerprint only; provenance not inferred')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('path',type=Path)
    print(json.dumps(summarize(parser.parse_args().path),indent=2,allow_nan=False))
