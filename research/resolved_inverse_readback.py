"""Independent small matrix, inverse, coefficient and complete-row diagnostics."""
import math
from pathlib import Path

from defect_spectrum_readback import matrix
from compact_tile_readback import finite_file
from stream_inverse_action import column


def check(root,compact,trials,full,previous,oldc,counts):
    root,compact,trials,full,previous,oldc=map(Path,(root,compact,trials,full,previous,oldc))
    left,right,oldr=counts;n=left+right;r=oldr+9
    state=matrix(compact/'compact-state.bin',n,5);d=state[4]
    u=matrix(compact/'compact-u.bin',n,oldr)+matrix(full/'enrichment-actions.bin',n,9)
    m=matrix(root/'enriched-m.bin',r,r);w=matrix(root/'enriched-w.bin',r,r)
    mg=matrix(root/'enriched-qgram.bin',r,r)
    if max(abs(mg[j][i]-float(i==j)) for i in range(r) for j in range(r))>1e-8:raise ValueError('Nonorthonormal enriched basis')
    max_m_error=0.;max_m_ratio=0.
    for path,number,offset in ((compact/'compact-q.bin',oldr,0),(trials/'trial-inputs.bin',9,oldr)):
        finite_file(path,n*number)
        with path.open('rb') as stream:
            for local in range(number):
                q=column(stream,n);qd=[x*y for x,y in zip(q,d)];i=offset+local
                for j in range(r):
                    terms=[a*b for a,b in zip(qd,u[j])];expected=float(i==j)-math.fsum(terms)
                    error=abs(m[j][i]-expected);bound=1e-28+1e-10*(float(i==j)+math.fsum(map(abs,terms)))
                    if not math.isfinite(error) or error>bound:raise ValueError('Independent enriched M mismatch')
                    max_m_error=max(max_m_error,error);max_m_ratio=max(max_m_ratio,error/bound)
    inverse_error=max(abs(math.fsum(a[k][i]*b[j][k] for k in range(r))-float(i==j)) for a,b in ((m,w),(w,m)) for i in range(r) for j in range(r))
    if inverse_error>1e-9:raise ValueError('Independent two-sided inverse mismatch')
    singular=matrix(root/'enriched-singular.bin',r,1)[0]
    if list(singular)!=sorted(singular,reverse=True) or singular[-1]<=0:raise ValueError('Invalid enriched singular values')
    frob=math.fsum(x*x for col in m for x in col)
    if abs(math.fsum(x*x for x in singular)-frob)>1e-9*max(1.,frob):raise ValueError('Enriched singular Frobenius mismatch')
    sample=sorted({0,31,left-1,left,left+(right-1)//2,n-1});cerror=0.
    paths=(previous/'compact-p.bin',full/'enrichment-p.bin',compact/'compact-q.bin',trials/'trial-inputs.bin',root/'enriched-c.bin')
    finite_file(paths[0],oldr*n);finite_file(paths[1],9*n);finite_file(paths[4],r*n)
    with paths[0].open('rb') as op,paths[1].open('rb') as ep,paths[2].open('rb') as oq,paths[3].open('rb') as eq,paths[4].open('rb') as cp:
        for j in sample:
            op.seek(8*oldr*j);ep.seek(72*j);p=list(column(op,oldr))+list(column(ep,9));q=[]
            for stream,number in ((oq,oldr),(eq,9)):
                for k in range(number):stream.seek(8*(n*k+j));q.extend(column(stream,1))
            cp.seek(8*r*j);native=column(cp,r)
            for i in range(r):
                terms=[w[k][i]*(p[k]-q[k]) for k in range(r)];error=abs(native[i]-math.fsum(terms));bound=1e-28+1e-10*math.fsum(map(abs,terms))
                if not math.isfinite(error) or error>bound:raise ValueError('Independent enriched C mismatch')
                cerror=max(cerror,error)
    indices=[0,31,63,min(66,left)-1,(left+3)//4-1,3*left//4-1,left+1,left+right//4-1,left+3*right//4-1]
    us=[[col[i] for col in u] for i in indices];del u
    kl=matrix(full/'enrichment-kernel-left.bin',right,6);kr=matrix(full/'enrichment-kernel-right.bin',left,3)
    beta=float((compact/'compact-state.meta').read_text().splitlines()[2]);weights=[]
    for x,dk in zip(state[1],state[2]):weights.append(dk/2*(beta/2 if x==0 else math.tanh(beta*abs(x)/2)/abs(x)))
    normsets=[];row_error=0.
    for filename,cpath,rank in (('baseline-rows.bin',oldc/'compact-c.bin',oldr),('enriched-rows.bin',root/'enriched-c.bin',r)):
        finite_file(root/filename,9*n);finite_file(cpath,rank*n);parts=[[] for _ in indices]
        with (root/filename).open('rb') as stream,cpath.open('rb') as cs:
            for first in range(0,n,1024):
                width=min(1024,n-first);values=column(stream,9*width);cv=column(cs,rank*width)
                for i,row in enumerate(indices):
                    parts[i].append(math.fsum(abs(x) for x in values[i::9]))
                    for local in range(width):
                        j=first+local;terms=[a*b for a,b in zip(us[i][:rank],cv[rank*local:rank*(local+1)])]
                        av=0.
                        if i<6 and j>=left:av=-kl[i][j-left]*weights[j]/(1+state[3][row])
                        if i>=6 and j<left:av=-kr[i-6][j]*weights[j]/(1+state[3][row])
                        expected=(math.fsum(terms)+av)*d[j];error=abs(values[9*local+i]-expected)
                        bound=1e-28+1e-10*(math.fsum(map(abs,terms))+abs(av))*abs(d[j])
                        if not math.isfinite(error) or error>bound:raise ValueError('Independent enriched row mismatch')
                        row_error=max(row_error,error)
        normsets.append(list(map(math.fsum,parts)))
    native_norms=matrix(root/'enriched-norms.bin',9,2)
    if any(abs(a-b)>1e-28+1e-10*max(abs(a),abs(b)) for arow,brow in zip(native_norms,normsets) for a,b in zip(arow,brow)):raise ValueError('Enriched row norm mismatch')
    with (oldc/'compact-defect-rows.bin').open('rb') as stream:accepted=column(stream,64)
    if any(abs(normsets[0][i]-accepted[j])>1e-10*max(normsets[0][i],accepted[j]) for i,j in enumerate((0,31,63))):raise ValueError('Original training rows changed')
    return dict(indices_one_based=[i+1 for i in indices],training_positions=[0,1,2],heldout_positions=list(range(3,9)),
                old_row_norms=normsets[0],enriched_row_norms=normsets[1],sampled_contraction_gate_pass=max(normsets[1])<1,
                small_matrix_max_error=max_m_error,small_matrix_max_error_over_bound=max_m_ratio,inverse_two_sided_max_error=inverse_error,
                singular_values=list(singular),small_matrix_singular_ratio=singular[0]/singular[-1],coefficient_max_error=cerror,
                row_element_max_error=row_error,inverse_adopted=False,full_space_norm_measured=False,outward_certified=False,physical_response_verified=False)
