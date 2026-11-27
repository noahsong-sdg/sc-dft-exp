"""Independent intraband uniform-gap response control in code slope units.

Hiorth et al., arXiv:2603.10955v1 Eq.4 supplies the conventional kernel.
The factor1/2 here converts that kernel to the existing pair-momentum slope
convention; see UNIFORM_GAP_REFERENCE.md. No geometric or vertex term supplied.
"""
import math


def stiffness(states,gap,beta,volume=1.0):
    """Integrate (xi, weight, directional band derivative) for one constant gap."""
    if not all(map(math.isfinite,(gap,beta,volume))) or gap < 0 or beta <= 0 or volume <= 0:
        raise ValueError('Finite nonnegative gap and positive beta/volume required')
    terms=[]
    for xi,weight,velocity in states:
        if not all(map(math.isfinite,(xi,weight,velocity))):
            raise ValueError('Nonfinite uniform-gap state')
        energy=math.hypot(xi,gap)
        x=.5*beta*energy
        if x < 1e-3:
            # Expansion of (tanh(x)-x*sech(x)^2)/x^3 at the origin.
            kernel=beta**3*gap**2/16*(2/3-8/15*x*x+34/105*x**4)
        else:
            tail=math.exp(-2*x)
            kernel=.5*(gap/energy)**2/energy*(math.tanh(x)-4*x*tail/(1+tail)**2)
        terms.append(weight*velocity**2*kernel)
    return math.fsum(terms)/volume
