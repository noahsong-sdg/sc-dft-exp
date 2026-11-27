"""Check the finite-T Q0 nonlinear occupation Jacobian with Decimal differences.

This qualifies a scalar formula for a proposed native map, not a gap solver.
"""
from decimal import Decimal, localcontext
import json
import math


def coefficients(xi, delta, beta, weight):
    energy = math.hypot(xi, delta)
    if energy == 0:
        return 0., weight * beta / 4
    thermal = math.tanh(beta * energy / 2)
    tail = math.exp(-beta * energy)
    sech2 = 4 * tail / (1 + tail)**2
    occupation = weight / 2 * delta / energy * thermal
    derivative = weight / 2 * ((xi / energy)**2 / energy * thermal
                               + beta / 2 * (delta / energy)**2 * sech2)
    return occupation, derivative


def reference(xi, delta, beta, weight):
    """Differentiate the exponential occupation directly in 80-digit arithmetic."""
    with localcontext() as context:
        context.prec = 80
        x, d, b, w = map(lambda value: Decimal(str(value)), (xi, delta, beta, weight))
        step = Decimal('1e-24')

        def chi(value):
            energy = (x*x + value*value).sqrt()
            if energy == 0:
                return Decimal(0)
            tail = (-b*energy).exp()
            return w/2 * value/energy * (1-tail)/(1+tail)

        return float(chi(d)), float((chi(d+step)-chi(d-step))/(2*step))


def run():
    rows = []
    for beta in (.1, 1., 100., 19613.355577892344, 1e6):
        for xi in (0., 1e-12, 1e-7, .001, .4):
            for delta in (-.01, -1e-6, 0., 1e-6, .01):
                actual = coefficients(xi, delta, beta, .7)
                expected = reference(xi, delta, beta, .7)
                errors = [abs(a-b) for a, b in zip(actual, expected)]
                if any(error > 1e-16 + 2e-12*abs(value) for error, value in zip(errors, expected)):
                    raise AssertionError((beta, xi, delta, actual, expected))
                rows.append(dict(beta=beta, xi=xi, delta=delta, weight=.7,
                                 occupation=actual[0], derivative=actual[1],
                                 reference=expected, absolute_errors=errors))
    return dict(cases=rows, decimal_precision=80, difference_step='1e-24',
                acceptance='absolute1e-16 + relative2e-12 per scalar',
                scope='Q0 finite-T scalar nonlinear weight and Jacobian; no native map or converged gap')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, allow_nan=False))
