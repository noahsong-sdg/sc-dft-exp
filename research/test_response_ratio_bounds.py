from decimal import Decimal, localcontext
from fractions import Fraction
import math
import unittest

from response_ratio_bounds import stiffness_ratio_interval


class ResponseRatioBoundsTests(unittest.TestCase):
    def test_independent_high_precision_interior_and_corners(self):
        # Decimal arithmetic uses exact binary64 inputs, independent of Fraction.
        with localcontext() as ctx:
            ctx.prec = 100
            for n in (-1.7, 0., 2.3):
                for d in (-3.1, .7):
                    for ne in (0., .003, 2.):
                        for de in (0., .02, .3):
                            low, high = stiffness_ratio_interval(n, ne, d, de)
                            nd, ed, dd, ded = map(Decimal.from_float, (n, ne, d, de))
                            for a in (-1, -.3, 0, .4, 1):
                                for b in (-1, -.2, 0, .6, 1):
                                    value = (nd+Decimal.from_float(float(a))*ed)/(dd+Decimal.from_float(float(b))*ded)
                                    self.assertLessEqual(Decimal.from_float(low), value)
                                    self.assertGreaterEqual(Decimal.from_float(high), value)

    def test_outward_rounding_and_subnormal_results(self):
        for numerator, denominator in ((1., 3.), (-1., 3.), (math.ulp(0.), 2.), (-math.ulp(0.), 2.)):
            low, high = stiffness_ratio_interval(numerator, 0., denominator, 0.)
            exact = Fraction.from_float(numerator)/Fraction.from_float(denominator)
            self.assertLessEqual(Fraction.from_float(low), exact)
            self.assertGreaterEqual(Fraction.from_float(high), exact)
            self.assertLessEqual(high-low, max(math.ulp(low), math.ulp(high)))
        self.assertEqual(stiffness_ratio_interval(2., 0., 4., 0.), (.5, .5))
        self.assertEqual(stiffness_ratio_interval(0., 0., -2., .1), (0., 0.))

    def test_reject_unbounded_or_invalid_intervals(self):
        for values in ((1., 0., 0., 0.), (1., 0., 1., 1.), (1., 0., -.1, .2),
                       (1., -1., 2., 0.), (1., 0., 2., -1.), (math.nan, 0., 2., 0.),
                       (1., 0., math.inf, 0.), (1., math.inf, 2., 0.),
                       (1e308, 0., math.ulp(0.), 0.)):
            with self.subTest(values=values), self.assertRaises(ValueError):
                stiffness_ratio_interval(*values)


if __name__ == '__main__':
    unittest.main()
