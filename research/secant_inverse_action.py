"""Rank-one inverse update from one saved full Jacobian action; diagnostic only."""
import array
import math


def factors(direction, jacobian_action, inverse_action):
    """Return u,w for Bnew=B+u w^T, with Bnew*Jv=v in exact arithmetic.

    u=v-BJv and w=Jv/||Jv||2^2. This is the minimum Frobenius-norm
    matrix change satisfying that one secant equation, not a global inverse.
    """
    n=len(direction)
    if (not n or any(len(x)!=n for x in (jacobian_action,inverse_action))
            or not all(math.isfinite(x) for block in (direction,jacobian_action,inverse_action) for x in block)):
        raise ValueError('Invalid secant vector shape or values')
    scale=max(map(abs,jacobian_action))
    if scale==0:raise ValueError('Zero secant Jacobian action')
    normalized=array.array('d',(x/scale for x in jacobian_action))
    norm2=math.fsum(x*x for x in normalized)
    u=array.array('d',(v-b for v,b in zip(direction,inverse_action)))
    w=array.array('d',((x/norm2)/scale for x in normalized))
    if not all(math.isfinite(x) for block in (u,w) for x in block):
        raise ValueError('Nonfinite secant factors')
    return u,w


def action(u,w,rhs,base_action):
    n=len(u)
    if (not n or any(len(x)!=n for x in (w,rhs,base_action))
            or not all(math.isfinite(x) for block in (u,w,rhs,base_action) for x in block)):
        raise ValueError('Invalid secant action shape or values')
    coefficient=math.fsum(a*b for a,b in zip(w,rhs))
    result=array.array('d',(b+x*coefficient for x,b in zip(u,base_action)))
    if not math.isfinite(coefficient) or not all(map(math.isfinite,result)):
        raise ValueError('Nonfinite secant action')
    return result
