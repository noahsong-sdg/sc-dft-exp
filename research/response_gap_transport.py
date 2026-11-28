"""Conditional gap-to-stiffness sensitivity; not a gap or rounding certificate."""
import math


def infinity_gap_lipschitz(states, beta, volume=1.):
    """Bound |S(d+e)-S(d)| by result*||e||_inf for fixed finite-T states.

    States follow linear_response.stiffness: (xi, gap, weight, a, b).
    The real-arithmetic bound allows signed weights and arbitrary real gaps.
    It covers only gap changes, with fixed xi/weight/a/b/beta/volume.
    """
    if not math.isfinite(beta) or beta <= 0 or not math.isfinite(volume) or volume <= 0:
        raise ValueError('Positive finite beta and volume required')
    terms = []
    for state in states:
        if len(state) != 5 or not all(map(math.isfinite, state)):
            raise ValueError('Five finite state values required')
        _, _, weight, a, b = state
        terms.append(abs(weight)*(2/(3*math.sqrt(3))*beta*beta*a*a+beta*abs(b)))
    result = math.fsum(terms)/volume
    if not math.isfinite(result):
        raise ValueError('Sensitivity bound exceeds finite arithmetic range')
    return result
