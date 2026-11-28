"""Scalar saved-row and bilinear controls; not inverse or physical acceptance."""
import math
from pathlib import Path

from compact_p_readback import integers,records,timings
from defect_spectrum_readback import matrix
from stream_inverse_action import column
from compact_tile_readback import finite_file


def controls(root,compact,trials,counts,rank,stop):
    root,compact,trials=map(Path,(root,compact,trials));left,right=counts;n=left+right
    if min(counts)<65 or not 64<=stop<=left or stop!=left and stop%32:raise ValueError('Invalid enrichment coverage')
    meta=records(root/'enrichment-action.meta',8);source=records(compact/'compact-state.meta',6)
    li=[1,32,64,min(66,left),(left+3)//4,3*left//4];ri=[2,right//4,3*right//4]
    if (meta[0]!='enrichment-action-v1; diagnostic only, NOT an adopted inverse'
            or integers(meta[1],5)!=[left,right,rank,9,stop] or meta[2:5]!=source[3:6]
            or integers(meta[5],6)!=li or integers(meta[6],3)!=ri):raise ValueError('Different enrichment metadata')
    stats=timings(meta[7],3)
    if stats[0]>1e-12:raise ValueError('Excessive native derivative mismatch')
    expected=[min(first+31,stop) for first in range(1,stop+1,32) if (first-1)%1024==0 or first+31>=stop]
    progresspath=root/'enrichment-progress.txt'
    if not 0<progresspath.stat().st_size<=65536:raise ValueError('Invalid enrichment progress size')
    progress=progresspath.read_text().splitlines();previous=[0.,0.]
    if len(progress)!=len(expected):raise ValueError('Different enrichment progress count')
    for line,last in zip(progress,expected):
        fields=line.split()
        if len(fields)!=4 or integers(' '.join(fields[:2]),2)!=[last,left]:raise ValueError('Different enrichment progress')
        cpu=timings(' '.join(fields[2:]),2)
        if any(a>b for a,b in zip(previous,cpu)):raise ValueError('Decreasing enrichment CPU')
        previous=cpu
    if previous!=stats[1:]:raise ValueError('Different final enrichment CPU')
    trial=matrix(trials/'trial-inputs.bin',n,9);image=matrix(root/'enrichment-actions.bin',n,9)
    state=matrix(compact/'compact-state.bin',n,5);beta=float(source[2]);w=[]
    if not math.isfinite(beta) or beta<=0 or any(1+x<=0 for x in state[3]):raise ValueError('Invalid enrichment state normalization')
    for x,dk in zip(state[1],state[2]):w.append(dk/2*(beta/2 if x==0 else math.tanh(beta*abs(x)/2)/abs(x)))
    finite_file(root/'enrichment-p.bin',9*n)
    with (root/'enrichment-p.bin').open('rb') as stream:packed=column(stream,9*n)
    p=[packed[k::9] for k in range(9)]
    kl=matrix(root/'enrichment-kernel-left.bin',right,6);kr=matrix(root/'enrichment-kernel-right.bin',left,3)
    if any(any(col[stop:left]) for col in (*image,*p)) or any(any(col[stop:]) for col in kr):raise ValueError('Changed unvisited output')
    errors=[];ratios=[]
    def compare(actual,terms):
        expected=math.fsum(terms);bound=1e-28+1e-10*math.fsum(map(abs,terms));error=abs(actual-expected)
        if not math.isfinite(error) or error>bound:raise ValueError('Independent enrichment action mismatch')
        errors.append(error);ratios.append(error/bound)
    for row,kernel in zip(li,kl):
        if row>stop:
            if any(kernel):raise ValueError('Nonzero unvisited left sample')
            continue
        for k in range(9):compare(image[k][row-1],[-x*w[left+j]*trial[k][left+j]/(1+state[3][row-1]) for j,x in enumerate(kernel)])
    for row,kernel in zip(ri,kr):
        for k in range(9):compare(image[k][left+row-1],[-kernel[j]*w[j]*trial[k][j]/(1+state[3][left+row-1]) for j in range(stop)])
    action_count=len(errors)
    # Two differently contracted native products, independently summed in Python.
    for i in range(9):
        for j in range(9):
            lhs=math.fsum(a*b for a,b in zip(p[i],trial[j]))
            rhs=[trial[i][k]*state[4][k]*image[j][k] for k in range(n)]
            terms=[a*b for a,b in zip(p[i],trial[j])]
            expected=math.fsum(rhs);bound=1e-28+1e-10*(math.fsum(map(abs,terms))+math.fsum(map(abs,rhs)))
            error=abs(lhs-expected)
            if not math.isfinite(error) or error>bound:raise ValueError('Independent enrichment bilinear mismatch')
            errors.append(error);ratios.append(error/bound)
    return dict(completed_left_rows=stop,complete_A_and_P=stop==left,all_values_finite=True,
                unvisited_outputs_zero=True,action_controls=action_count,bilinear_controls=81,
                max_absolute_error=max(errors),max_error_over_bound=max(ratios),native_derivative_max_error=stats[0],
                cpu_s=stats[1:],inverse_adopted=False,physical_response_verified=False)
