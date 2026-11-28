from decimal import Decimal, localcontext
import math
import unittest

from response_gap_transport import infinity_gap_lipschitz


def independent_stiffness(states, beta, volume):
    # Decimal exp formulation, independent of the production tanh/sech code.
    with localcontext() as ctx:
        ctx.prec = 70
        beta, volume = Decimal(str(beta)), Decimal(str(volume))
        total = Decimal(0)
        for state in states:
            x, d, w, a, b = map(lambda v: Decimal(str(v)), state)
            e = (x*x+d*d).sqrt()
            def thermal(z):
                q = (-beta*abs(z)).exp()
                return (1-q)/(1+q), 4*q/(1+q)**2
            tx, sx = thermal(x)
            te, se = thermal(e)
            signed_tx = tx if x >= 0 else -tx
            # The zero-energy continuous extension is zero.
            curvature = 0 if not e else 4*b*(signed_tx-x/e*te)
            total += w*(beta*a*a*(sx-se)+curvature)
        return total/volume


class ResponseGapTransportTests(unittest.TestCase):
    def test_finite_balls_against_independent_high_precision_observable(self):
        cases = 0
        for beta in (.5, 4., 40., 20000.):
            for x in (0., 1e-12, .0001, -.2, 2.):
                for d in (0., 1e-10, .00001, .3):
                    for radius in (1e-12, .000003, .2):
                        states = [(x, d, -.7, .3, -.4), (-x, -d, 1.2, -.2, .1)]
                        changed = [(x, d-radius, -.7, .3, -.4), (-x, -d+radius/3, 1.2, -.2, .1)]
                        difference = abs(independent_stiffness(changed, beta, 2.3)
                                         - independent_stiffness(states, beta, 2.3))
                        bound = infinity_gap_lipschitz(states, beta, 2.3)*radius
                        self.assertLessEqual(difference, Decimal(str(bound))*(1+Decimal('1e-14')))
                        cases += 1
        self.assertEqual(cases, 240)

    def test_bound_controls_inf_norm_with_signed_weights(self):
        states = [(.2, .1, -2., .3, -.4), (-.4, .2, 1., -.1, .2)]
        bound = infinity_gap_lipschitz(states, 4.)
        self.assertGreater(bound, 0.)
        self.assertAlmostEqual(infinity_gap_lipschitz(states, 4., 3.), bound/3)
        self.assertEqual(infinity_gap_lipschitz([], 4.), 0.)

    def test_reject_nonfinite_and_invalid_domain(self):
        for beta, volume in ((0., 1.), (-1., 1.), (math.inf, 1.), (1., 0.), (1., math.nan)):
            with self.assertRaises(ValueError):
                infinity_gap_lipschitz([], beta, volume)
        for state in ((0., 0., 1., math.nan, 0.), (0., 1., 1., 1.)):
            with self.assertRaises(ValueError):
                infinity_gap_lipschitz([state], 2.)


if __name__ == '__main__':
    unittest.main()
