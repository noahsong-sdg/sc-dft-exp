"""Bounded-memory application of the frozen low-rank inverse; diagnostic only."""
import array
import math
from pathlib import Path


def solve_small(matrix, rhs):
    rank=len(rhs)
    if (not 1<=rank<=64 or len(matrix)!=rank*rank
            or not all(math.isfinite(x) for block in (matrix,rhs) for x in block)):
        raise ValueError('Invalid small inverse system')
    rows=[[matrix[j*rank+i] for j in range(rank)]+[rhs[i]] for i in range(rank)]
    for k in range(rank):
        pivot=max(range(k,rank),key=lambda i:abs(rows[i][k]))
        if rows[pivot][k]==0:raise ValueError('Singular small inverse system')
        rows[k],rows[pivot]=rows[pivot],rows[k]
        for i in range(k+1,rank):
            factor=rows[i][k]/rows[k][k];rows[i][k]=0.
            for j in range(k+1,rank+1):rows[i][j]-=factor*rows[k][j]
        if any(not math.isfinite(x) for row in rows[k:] for x in row):
            raise ValueError('Nonfinite small inverse elimination')
    solution=[0.]*rank
    for k in range(rank-1,-1,-1):
        solution[k]=(rows[k][-1]-math.fsum(rows[k][j]*solution[j] for j in range(k+1,rank)))/rows[k][k]
    if not all(map(math.isfinite,solution)):raise ValueError('Nonfinite small inverse solution')
    return solution


def column(stream,n):
    result=array.array('d');result.fromfile(stream,n)
    if not all(map(math.isfinite,result)):raise ValueError('Nonfinite inverse basis column')
    return result


def apply(basis, diagonal, small, rhss):
    """Apply B=(I-U Q^T D)^-1 using stored M=I-Q^T D U.

    Stream Q/U twice and check (I-U Q^T D)answer=rhs independently.
    The residual is an algebraic control, not a forward-error/full-space bound.
    """
    n=len(diagonal);rank=math.isqrt(len(small));basis=Path(basis)
    if (n<1 or rank*rank!=len(small) or not 1<=rank<=64 or not rhss
            or any(len(rhs)!=n for rhs in rhss) or basis.stat().st_size!=16*n*rank
            or not all(math.isfinite(x) for block in (diagonal,small,*rhss) for x in block)):
        raise ValueError('Invalid frozen inverse action inputs')
    weighted=[array.array('d',(d*x for d,x in zip(diagonal,rhs))) for rhs in rhss]
    if any(not math.isfinite(x) for block in weighted for x in block):
        raise ValueError('Nonfinite weighted inverse right-hand side')
    coefficients=[[] for _ in rhss]
    with basis.open('rb') as stream:
        for _ in range(rank):
            q=column(stream,n)
            for out,weighted_rhs in zip(coefficients,weighted):out.append(math.fsum(a*b for a,b in zip(q,weighted_rhs)))
        coefficients=[solve_small(small,rhs) for rhs in coefficients]
        answers=[array.array('d',rhs) for rhs in rhss]
        for k in range(rank):
            u=column(stream,n)
            for answer,coef in zip(answers,coefficients):
                for i,value in enumerate(u):answer[i]+=value*coef[k]
    if any(not math.isfinite(x) for block in answers for x in block):
        raise ValueError('Nonfinite frozen inverse action')
    weighted=[array.array('d',(d*x for d,x in zip(diagonal,answer))) for answer in answers]
    if any(not math.isfinite(x) for block in weighted for x in block):
        raise ValueError('Nonfinite weighted inverse answer')
    overlaps=[[] for _ in rhss]
    residuals=[array.array('d',(a-b for a,b in zip(answer,rhs))) for answer,rhs in zip(answers,rhss)]
    with basis.open('rb') as stream:
        for _ in range(rank):
            q=column(stream,n)
            for out,weighted_answer in zip(overlaps,weighted):out.append(math.fsum(a*b for a,b in zip(q,weighted_answer)))
        for k in range(rank):
            u=column(stream,n)
            for residual,coef in zip(residuals,overlaps):
                for i,value in enumerate(u):residual[i]-=value*coef[k]
    errors=[];bounds=[]
    for answer,rhs,residual in zip(answers,rhss,residuals):
        if not all(map(math.isfinite,residual)):raise ValueError('Nonfinite inverse action residual')
        scale=max(abs(x) for block in (answer,rhs) for x in block)
        bound=1e-30+1e-10*scale;error=max(map(abs,residual))
        if error>bound:raise ValueError('Independent streamed inverse action differs')
        errors.append(error);bounds.append(bound)
    return dict(answers=answers,independent_action_max_errors=errors,independent_action_bounds=bounds,
                conditioned_gap_error_bounded=False,physical_response_verified=False)
