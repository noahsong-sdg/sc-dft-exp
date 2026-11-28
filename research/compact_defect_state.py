"""Stream padded Q/U into a source-bound compact diagnostic state; no error bound."""
import array
import hashlib
import math
from pathlib import Path
import sys

from stream_inverse_action import column,solve_small

HEADER='compact-defect-state-v1; little-endian binary64 Fortran order'
FILES=('compact-state.meta','compact-q.bin','compact-u.bin','compact-state.bin','compact-w.bin')


def compact(values,counts,zero_padding):
    if (len(counts)!=3 or min(counts)<=0 or counts[2]!=max(counts[:2])
            or len(values)!=2*counts[2] or not all(map(math.isfinite,values))):
        raise ValueError('Invalid padded defect state')
    maximum=counts[2]
    if zero_padding:
        for side,count in enumerate(counts[:2]):
            if any(values[side*maximum+count:(side+1)*maximum]):
                raise ValueError('Nonzero inactive defect padding')
    out=array.array('d',values[:counts[0]]);out.extend(values[maximum:maximum+counts[1]])
    return out


def inverse(small,rank):
    if not 1<=rank<=64 or len(small)!=rank*rank:raise ValueError('Invalid defect small matrix')
    result=array.array('d')
    for j in range(rank):result.extend(solve_small(small,[float(i==j) for i in range(rank)]))
    errors=[]
    for a,b in ((small,result),(result,small)):
        errors.append(max(abs(math.fsum(a[k*rank+i]*b[j*rank+k] for k in range(rank))-float(i==j))
                          for i in range(rank) for j in range(rank)))
    if not all(math.isfinite(e) and e<=1e-10 for e in errors):raise ValueError('Defect small inverse calibration failed')
    return result,errors


def write(root,basis,vectors,small,counts,rank,beta,operator,source_sha):
    root=Path(root);basis=Path(basis)
    if (sys.byteorder!='little' or len(vectors)!=5 or not math.isfinite(beta) or beta<=0
            or any(len(x)!=64 or any(c not in '0123456789abcdef' for c in x) for x in (operator,source_sha))):
        raise ValueError('Invalid compact defect provenance')
    # gap,xi,dk,Z,D. Only gap/D must be zero on inactive positions.
    packed=[compact(v,counts,k in (0,4)) for k,v in enumerate(vectors)]
    if any(1+x<=0 for x in packed[3]):raise ValueError('Invalid compact Z normalization')
    w,errors=inverse(small,rank);n=2*counts[2]
    if basis.stat().st_size!=16*n*rank:raise ValueError('Stale padded defect basis')
    if any((root/name).exists() for name in FILES):raise ValueError('Fresh compact defect outputs required')
    with basis.open('rb') as stream:
        for name in FILES[1:3]:
            with (root/name).open('xb') as target:
                for _ in range(rank):compact(column(stream,n),counts,True).tofile(target)
    with (root/'compact-state.bin').open('xb') as target:
        for values in packed:values.tofile(target)
    with (root/'compact-w.bin').open('xb') as target:w.tofile(target)
    candidate=hashlib.sha256(array.array('d',vectors[0]).tobytes()).hexdigest()
    (root/'compact-state.meta').write_text(HEADER+'\n'+' '.join(map(str,(*counts,rank)))+f'\n{beta:.17g}\n{operator}\n{candidate}\n{source_sha}\n')
    return dict(active_states=sum(counts[:2]),rank=rank,beta=beta,operator_sha256=operator,
                padded_candidate_sha256=candidate,source_manifest_sha256=source_sha,
                small_inverse_two_sided_max_errors=errors,conditioned_gap_error_bounded=False,physical_response_verified=False)


def actions(root,n,rank,rhss):
    """Calibrate the chosen stored W using compact Q/U/D; no new kernel action."""
    root=Path(root)
    if (not 1<=rank<=64 or n<1 or not rhss or any(len(x)!=n for x in rhss)
            or not all(math.isfinite(v) for x in rhss for v in x)):
        raise ValueError('Invalid compact inverse calibration')
    for name,size in (('compact-q.bin',n*rank),('compact-u.bin',n*rank),('compact-state.bin',5*n),('compact-w.bin',rank*rank)):
        if (root/name).stat().st_size!=8*size:raise ValueError('Stale compact calibration size')
    with (root/'compact-state.bin').open('rb') as stream:stream.seek(32*n);d=column(stream,n)
    with (root/'compact-w.bin').open('rb') as stream:w=column(stream,rank*rank)
    weighted=[array.array('d',(a*b for a,b in zip(d,rhs))) for rhs in rhss]
    if any(not math.isfinite(v) for x in weighted for v in x):raise ValueError('Nonfinite compact weighted RHS')
    coefficients=[[] for _ in rhss]
    with (root/'compact-q.bin').open('rb') as stream:
        for _ in range(rank):
            q=column(stream,n)
            for coef,rhs in zip(coefficients,weighted):coef.append(math.fsum(a*b for a,b in zip(q,rhs)))
    coefficients=[[math.fsum(w[j*rank+i]*coef[j] for j in range(rank)) for i in range(rank)] for coef in coefficients]
    answers=[array.array('d',rhs) for rhs in rhss]
    with (root/'compact-u.bin').open('rb') as stream:
        for k in range(rank):
            u=column(stream,n)
            for answer,coef in zip(answers,coefficients):
                for i,value in enumerate(u):answer[i]+=value*coef[k]
    if any(not math.isfinite(v) for x in answers for v in x):raise ValueError('Nonfinite compact inverse action')
    return answers
