"""Periodic integration-by-parts control for the frozen real-gap scalar current.

This is an algebraic reformulation of linear_response.py after integration,
not a physical vertex prescription. See ANISOTROPIC_VELOCITY_REFERENCE.md.
"""
import math


def stiffness(states,beta,volume=1.):
    """Integrate (xi, gap, weight, band derivative, gap derivative).

    Derivatives share one momentum direction. Equivalence to the curvature
    form requires smooth periodic bands/gaps and a consistent full measure.
    """
    if not all(map(math.isfinite,(beta,volume))) or beta<=0 or volume<=0:
        raise ValueError('Positive finite beta and volume required')
    terms=[]
    for xi,gap,weight,velocity,gradient in states:
        if not all(map(math.isfinite,(xi,gap,weight,velocity,gradient))):
            raise ValueError('Finite real-gap reference state required')
        energy=math.hypot(xi,gap)
        x=.5*beta*energy
        if x<1e-3:
            kernel=beta**3/16*(2/3-8/15*x*x+34/105*x**4)
        else:
            tail=math.exp(-2*x)
            kernel=(math.tanh(x)-4*x*tail/(1+tail)**2)/(2*energy**3)
        terms.append(weight*gap*(velocity*velocity*gap-velocity*xi*gradient)*kernel)
    return math.fsum(terms)/volume
