"""Analytic Q->0 limit in the audited current routine's conventions.

States are (xi, gap, weight, a, b), where dxq=a*Q and d2xq=b*Q**2,
and Q is the physical momentum norm used by the routine's denominator.
No experimental-unit conversion or self-consistent gap computation is supplied.
"""
import math


def sech2(value):
    tail=math.exp(-2*abs(value))
    return 4*tail/(1+tail)**2


def stiffness(states,beta,volume=1.):
    terms=[]
    for xi,gap,weight,a,b in states:
        energy=math.hypot(xi,gap)
        if energy==0:
            raise ValueError('This derivation requires nonzero quasiparticle energy')
        tx=math.tanh(.5*beta*abs(xi))
        te=math.tanh(.5*beta*energy)
        paramagnetic=beta*a*a*(sech2(.5*beta*xi)-sech2(.5*beta*energy))
        curvature=4*b*(math.copysign(tx,xi)-xi/energy*te)
        terms.append(weight*(paramagnetic+curvature))
    return math.fsum(terms)/volume


def released_bias(states,beta,volume=1.):
    return math.fsum(4*weight*b*math.copysign(1.,xi)*
                     (math.tanh(.5*beta*math.hypot(xi,gap))-
                      math.tanh(.5*beta*abs(xi)))
                     for xi,gap,weight,a,b in states)/volume
