import unittest

from nonlinear_weight_probe import coefficients, run


class NonlinearWeightTest(unittest.TestCase):
    def test_jacobian_matches_high_precision_direct_differences(self):
        self.assertEqual(len(run()['cases']), 125)

    def test_zero_energy_derivative_is_not_zero(self):
        self.assertEqual(coefficients(0., 0., 100., .8), (0., 20.))


if __name__ == '__main__':
    unittest.main()
