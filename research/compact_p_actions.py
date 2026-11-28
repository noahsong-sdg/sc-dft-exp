"""Independent fsum control: P(Dv)=Q^T D(ADv); caller must bind native parents."""
import math
from pathlib import Path
import sys

from stream_inverse_action import column


def compare(qpath,ppath,d,v,adv,rank):
    n=len(d);qpath,ppath=Path(qpath),Path(ppath)
    if (sys.byteorder!='little' or n<1 or not 1<=rank<=64 or len(v)!=n or len(adv)!=n
            or any(not math.isfinite(x) for field in (d,v,adv) for x in field)):
        raise ValueError('Invalid P action context')
    if any(path.stat().st_size!=8*n*rank for path in (qpath,ppath)):raise ValueError('Stale P action matrix shape')
    dv=[a*b for a,b in zip(d,v)];dadv=[a*b for a,b in zip(d,adv)]
    if not all(math.isfinite(x) for field in (dv,dadv) for x in field):raise ValueError('Nonfinite P action input product')
    lhs=[[] for _ in range(rank)];scales=[[] for _ in range(rank)]
    # P is rank-by-active column-major. Sum short aligned column chunks once,
    # retaining only chunk sums instead of transposing or loading the full P.
    with ppath.open('rb') as stream:
        for first in range(0,n,1024):
            width=min(1024,n-first);values=column(stream,width*rank)
            if not all(map(math.isfinite,values)):raise ValueError('Nonfinite P action matrix')
            for r in range(rank):
                terms=[values[j*rank+r]*dv[first+j] for j in range(width)]
                if not all(map(math.isfinite,terms)):raise ValueError('Nonfinite P action product')
                lhs[r].append(math.fsum(terms));scales[r].append(math.fsum(map(abs,terms)))
        if stream.read(1):raise ValueError('Trailing P action matrix')
    left=list(map(math.fsum,lhs));right=[];bounds=[]
    with qpath.open('rb') as stream:
        for r in range(rank):
            q=column(stream,n)
            if not all(map(math.isfinite,q)):raise ValueError('Nonfinite Q action matrix')
            terms=[a*b for a,b in zip(q,dadv)]
            if not all(map(math.isfinite,terms)):raise ValueError('Nonfinite Q action product')
            right.append(math.fsum(terms))
            bounds.append(1e-28+1e-10*(math.fsum(scales[r])+math.fsum(map(abs,terms))))
        if stream.read(1):raise ValueError('Trailing Q action matrix')
    errors=[abs(a-b) for a,b in zip(left,right)]
    if any(not math.isfinite(b) or not math.isfinite(e) or e>b for e,b in zip(errors,bounds)):
        raise ValueError('Independent full P saved-action mismatch')
    return dict(controls=rank,left_P_Dv=left,right_QT_D_ADv=right,absolute_errors=errors,bounds=bounds,
                max_absolute_error=max(errors),max_error_over_bound=max(e/b for e,b in zip(errors,bounds)),
                full_space_norm_measured=False,conditioned_gap_error_bounded=False,physical_response_verified=False)
