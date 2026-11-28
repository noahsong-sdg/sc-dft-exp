"""Independent coefficient samples and six streamed defect row sums; not a certificate."""
import math
from pathlib import Path

from compact_p_readback import integers,records,timings
from compact_tile_readback import finite_file
from stream_inverse_action import column


def controls(root,compact,checkpoint,counts,rank,stops):
    root,compact,checkpoint=map(Path,(root,compact,checkpoint));left,right=counts;n=left+right
    if (min(counts)<3 or not 1<=rank<=64 or len(stops)!=2 or any(not 3<=s<=c or s!=c and s%32 for s,c in zip(stops,counts))):
        raise ValueError('Invalid defect readback coverage')
    meta=records(root/'compact-defect.meta',7)
    if (meta[0]!='compact-defect-diagnostic-v1; ordinary binary64; NOT outward certified'
            or integers(meta[1],3)!=[*counts,rank] or integers(meta[2],2)!=list(stops)):
        raise ValueError('Different defect readback geometry')
    li=[1,(stops[0]+1)//2,stops[0]];ri=[1,(right+1)//2,right]
    if integers(meta[4],3)!=li or integers(meta[5],3)!=ri:raise ValueError('Different defect sample rows')
    info=timings(meta[6],6);beta=float((compact/'compact-state.meta').read_text().splitlines()[2])
    if not math.isfinite(beta) or beta<=0:raise ValueError('Invalid defect beta')
    finite_file(compact/'compact-state.bin',5*n)
    with (compact/'compact-state.bin').open('rb') as stream:state=[column(stream,n) for _ in range(5)]
    weights=[dk/2*(beta/2 if x==0 else math.tanh(beta*abs(x)/2)/abs(x)) for x,dk in zip(state[1],state[2])]
    if any(1+z<=0 for z in state[3]) or not all(map(math.isfinite,weights)):raise ValueError('Invalid defect linear weights')
    finite_file(root/'compact-defect-rows.bin',n,stops[0],left)
    with (root/'compact-defect-rows.bin').open('rb') as stream:rows=column(stream,n)
    if any(x<0 for x in rows) or max(rows)!=info[1]:raise ValueError('Different defect maximum')
    selected=[x-1 for x in li]+[left+x-1 for x in ri];urows=[[] for _ in selected]
    if (compact/'compact-u.bin').stat().st_size!=8*n*rank:raise ValueError('Stale defect U shape')
    with (compact/'compact-u.bin').open('rb') as stream:
        for _ in range(rank):
            values=column(stream,n)
            if not all(map(math.isfinite,values)):raise ValueError('Nonfinite defect U')
            for target,i in zip(urows,selected):target.append(values[i])
    finite_file(root/'defect-kernel-left.bin',3*right);finite_file(root/'defect-kernel-right.bin',3*stops[0])
    with (root/'defect-kernel-left.bin').open('rb') as stream:lk=[column(stream,right) for _ in range(3)]
    with (root/'defect-kernel-right.bin').open('rb') as stream:rk=[column(stream,stops[0]) for _ in range(3)]
    if (root/'compact-c.bin').stat().st_size!=8*n*rank:raise ValueError('Stale defect coefficient shape')
    partials=[[] for _ in selected];scales=[[] for _ in selected]
    with (root/'compact-c.bin').open('rb') as stream:
        for first in range(0,n,1024):
            width=min(1024,n-first);values=column(stream,width*rank)
            if not all(map(math.isfinite,values)):raise ValueError('Nonfinite defect coefficients')
            for sample,(i,ur) in enumerate(zip(selected,urows)):
                terms=[];magnitudes=[]
                for local in range(width):
                    j=first+local
                    if sample>=3 and not (j<stops[0] or left<=j<left+stops[1]):continue
                    products=[ur[k]*values[local*rank+k] for k in range(rank)];uc=math.fsum(products);a=0.
                    if sample<3 and j>=left:a=-lk[sample][j-left]*weights[j]/(1+state[3][i])
                    if sample>=3 and j<left:a=-rk[sample-3][j]*weights[j]/(1+state[3][i])
                    terms.append(abs((uc+a)*state[4][j]));magnitudes.append((math.fsum(map(abs,products))+abs(a))*abs(state[4][j]))
                partials[sample].append(math.fsum(terms));scales[sample].append(math.fsum(magnitudes))
    expected=list(map(math.fsum,partials));bounds=[1e-28+1e-10*math.fsum(x) for x in scales]
    errors=[abs(rows[i]-value) for i,value in zip(selected,expected)]
    if any(not math.isfinite(b) or not math.isfinite(e) or e>b for e,b in zip(errors,bounds)):raise ValueError('Independent defect row mismatch')
    # C=W(P-Q^T) is checked separately at six columns, every rank component.
    for path,size in ((compact/'compact-q.bin',8*n*rank),(compact/'compact-w.bin',8*rank*rank),(checkpoint/'compact-p.bin',8*n*rank)):
        if path.stat().st_size!=size:raise ValueError('Stale defect coefficient dependency shape')
    with (compact/'compact-w.bin').open('rb') as stream:small=column(stream,rank*rank)
    cerrors=[];cbounds=[]
    with (compact/'compact-q.bin').open('rb') as q,(checkpoint/'compact-p.bin').open('rb') as p,(root/'compact-c.bin').open('rb') as c:
        for j in selected:
            p.seek(8*j*rank);pv=column(p,rank);c.seek(8*j*rank);cv=column(c,rank);difference=[]
            for k in range(rank):q.seek(8*(k*n+j));difference.append(pv[k]-column(q,1)[0])
            for i in range(rank):
                terms=[small[i+k*rank]*difference[k] for k in range(rank)];value=math.fsum(terms)
                error=abs(cv[i]-value);bound=1e-28+1e-10*math.fsum(map(abs,terms))
                if not math.isfinite(error) or not math.isfinite(bound) or error>bound:raise ValueError('Independent defect coefficient mismatch')
                cerrors.append(error);cbounds.append(bound)
    return dict(complete_coverage=list(stops)==list(counts),diagnostic_max_row_sum=max(rows),native_derivative_max_difference=info[0],cpu_s=info[2:],
                independent_rows=[i+1 for i in selected],independent_row_sums=expected,row_absolute_errors=errors,row_bounds=bounds,
                independent_coefficient_controls=len(cerrors),coefficient_max_error=max(cerrors),coefficient_max_error_over_bound=max(e/b for e,b in zip(cerrors,cbounds)),
                row_max_error_over_bound=max(e/b for e,b in zip(errors,bounds)),
                independent_sample_rows_above_one=[i+1 for i,x,b in zip(selected,expected,bounds) if x>1+b],outward_certified=False,
                conditioned_gap_error_bounded=False,physical_response_verified=False)
