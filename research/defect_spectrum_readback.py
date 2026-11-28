"""Check retained64-row Gram/sensitivity diagnostics; no adopted basis or norm bound."""
import math
from pathlib import Path

from compact_p_readback import integers
from compact_tile_readback import finite_file
from stream_inverse_action import column


def matrix(path,rows,cols):
    finite_file(path,rows*cols)
    with Path(path).open('rb') as stream:return [column(stream,rows) for _ in range(cols)]


def check(root,compact,defect,tiles,counts):
    root,compact,defect,tiles=map(Path,(root,compact,defect,tiles));left,right,rank=counts;n=left+right;m=64
    lines=(root/'row-spectrum.txt').read_text().splitlines()
    if len(lines)!=66 or lines[0]!='retained-row-spectrum-v1; diagnostic, NOT an inverse or certificate':raise ValueError('Stale spectrum metadata')
    dims=integers(lines[1],5);kept=dims[-1]
    if dims[:4]!=[left,right,rank,m] or not 1<=kept<=3:raise ValueError('Different spectrum geometry')
    eig=list(map(float,lines[2:]));gram=matrix(root/'row-gram.bin',m,m);lv=matrix(root/'row-eigenvectors.bin',m,m)
    if not all(map(math.isfinite,eig)) or eig!=sorted(eig) or eig[-1]<=0 or eig[0]<-1e-10*eig[-1]:raise ValueError('Invalid Gram spectrum')
    if kept!=min(3,sum(x>1e-10*eig[-1] for x in eig)):raise ValueError('Different resolved spectrum rank')
    eigen_error=max(abs(math.fsum(gram[j][i]*lv[k][j] for j in range(m))-eig[k]*lv[k][i]) for k in range(m) for i in range(m))
    eigen_scale=max(1.,max(abs(x) for col in gram for x in col))
    orth_error=max(abs(math.fsum(a*b for a,b in zip(lv[i],lv[j]))-float(i==j)) for i in range(m) for j in range(m))
    if eigen_error>1e-9*eigen_scale or orth_error>1e-9:raise ValueError('Independent Gram eigenpair mismatch')
    v=matrix(root/'sensitivity-directions.bin',n,kept);qv=matrix(root/'basis-overlap.bin',rank,kept)
    qgram=matrix(root/'basis-gram.bin',rank,rank);vg=matrix(root/'direction-gram.bin',kept,kept)
    qerror=max(abs(qgram[j][i]-float(i==j)) for i in range(rank) for j in range(rank))
    verror=max(abs(math.fsum(a*b for a,b in zip(v[i],v[j]))-float(i==j)) for i in range(kept) for j in range(kept))
    if qerror>1e-8 or verror>1e-5 or any(abs(vg[j][i]-math.fsum(a*b for a,b in zip(v[i],v[j])))>1e-9 for i in range(kept) for j in range(kept)):
        raise ValueError('Nonorthonormal diagnostic basis/directions')
    samples=sorted({0,(rank-1)//2,rank-1});overlap_error=0.
    with (compact/'compact-q.bin').open('rb') as stream:
        for r in samples:
            stream.seek(8*n*r);q=column(stream,n)
            for k in range(kept):
                terms=[a*b for a,b in zip(q,v[k])];error=abs(math.fsum(terms)-qv[k][r]);bound=1e-28+1e-10*math.fsum(map(abs,terms))
                if not math.isfinite(error) or error>bound:raise ValueError('Independent basis overlap mismatch')
                overlap_error=max(overlap_error,error)
    pairs=((0,0),(0,31),(0,63),(31,31),(31,63),(63,63));gp=[[] for _ in pairs];rowparts=[[] for _ in range(m)]
    imageparts=[[[] for _ in range(m)] for _ in range(kept)]
    finite_file(root/'row-errors.bin',m*n)
    with (root/'row-errors.bin').open('rb') as stream:
        for first in range(0,n,1024):
            width=min(1024,n-first);values=column(stream,m*width)
            for i in range(m):
                row=values[i::m];rowparts[i].append(math.fsum(map(abs,row)))
                for k in range(kept):imageparts[k][i].append(math.fsum(a*b for a,b in zip(row,v[k][first:first+width])))
            for part,(a,b) in zip(gp,pairs):part.append(math.fsum(values[j*m+a]*values[j*m+b] for j in range(width)))
    gram_error=max(abs(math.fsum(part)-gram[b][a]) for part,(a,b) in zip(gp,pairs))
    if gram_error>1e-9*eigen_scale:raise ValueError('Independent row Gram mismatch')
    rows=list(map(math.fsum,rowparts))
    with (defect/'compact-defect-rows.bin').open('rb') as stream:old=column(stream,m)
    if any(abs(a-b)>1e-28+1e-10*max(abs(a),abs(b)) for a,b in zip(rows,old)):raise ValueError('Retained row norm changed')
    ev_error=0.
    for k in range(kept):
        sigma=math.sqrt(eig[m-kept+k])
        for i in range(m):
            error=abs(math.fsum(imageparts[k][i])-sigma*lv[m-kept+k][i]);ev_error=max(ev_error,error)
            if error>1e-8*max(1.,sigma):raise ValueError('Independent sensitivity action mismatch')
    finite_file(compact/'compact-state.bin',5*n)
    with (compact/'compact-state.bin').open('rb') as stream:state=[column(stream,n) for _ in range(5)]
    beta=float((compact/'compact-state.meta').read_text().splitlines()[2]);wr=[]
    for j in range(left,n):
        x=state[1][j];wr.append(state[2][j]/2*(beta/2 if x==0 else math.tanh(beta*abs(x)/2)/abs(x))*state[4][j])
    baselines=[]
    for tile in (1,2):
        with (tiles/f'compact-kernel-{tile}.bin').open('rb') as stream:
            for local in range(32):
                kernel=column(stream,right);i=32*(tile-1)+local
                baselines.append(math.fsum(abs(a*b/(1+state[3][i])) for a,b in zip(kernel,wr)))
    native_baseline=matrix(root/'row-baselines.bin',m,1)[0]
    if any(abs(a-b)>1e-28+1e-10*max(abs(a),abs(b)) for a,b in zip(baselines,native_baseline)):raise ValueError('Independent A-only baseline mismatch')
    trace=math.fsum(gram[i][i] for i in range(m));spectrum_trace=math.fsum(eig)
    if trace<=0 or abs(trace-spectrum_trace)>1e-9*trace:raise ValueError('Gram trace mismatch')
    return dict(rows=64,inputs=n,kept_directions=kept,raw_eigenvalues=eig,
                retained_energy_fractions={str(k):math.fsum(eig[-k:])/trace for k in (1,3,13)},
                direction_eigenvalues=eig[-kept:],basis_projection_squared_norms=[math.fsum(x*x for x in col) for col in qv],
                basis_orthogonality_error=qerror,direction_orthogonality_error=verror,gram_eigenpair_max_error=eigen_error,
                gram_fsum_max_error=gram_error,sensitivity_action_max_error=ev_error,basis_overlap_fsum_max_error=overlap_error,
                max_row_norm=max(rows),max_A_only_row_norm=max(baselines),row_norms=rows,A_only_row_norms=baselines,
                adopted_directions=False,full_space_norm_measured=False,outward_certified=False,physical_response_verified=False)
