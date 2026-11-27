"""Independent scalar checks of the normal-reference thermal factor.

This is an algebra probe, not a replacement native current implementation.
Arguments x,d are nonnegative energy magnitudes; beta is inverse temperature.
"""
import math


def direct_normal(x, d, beta):
    return .5 * (math.tanh(.5*beta*(x+d)) + math.tanh(.5*beta*(x-d)))


def released_normal(x, d, gap, beta):
    a = math.tanh(.5*beta*d)
    b = math.tanh(.5*beta*x)
    e = math.tanh(.5*beta*math.hypot(x, gap))
    if 1-a*b < 1e-10:
        if x*x+gap*gap > d*d:
            return b*(1+a)/(1+a*b)
        return 0.
    return e*(1+a)/(1+a*b)*(1-a)/(1-a*b)


def corrected_normal(x, d, beta):
    a = math.tanh(.5*beta*d)
    b = math.tanh(.5*beta*x)
    if 1-a*b < 1e-10:
        # The release's limiting shortcut has a separate boundary issue.
        # Direct tanh evaluation is well conditioned for this scalar check.
        return direct_normal(x, d, beta)
    return b*(1+a)/(1+a*b)*(1-a)/(1-a*b)
