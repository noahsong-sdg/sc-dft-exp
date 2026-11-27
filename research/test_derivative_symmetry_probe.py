import unittest
from derivative_symmetry_probe import evaluate


class DerivativeSymmetryTests(unittest.TestCase):
    def test_cubic_analytic_band_distinguishes_stencil_error(self):
        result=evaluate(8)
        self.assertLess(abs(result['analytic_relative_direction_difference']),1e-12)
        second=abs(result['second_order_relative_direction_difference'])
        fourth=abs(result['fourth_order_relative_direction_difference'])
        self.assertGreater(second,1e-4)
        self.assertLess(fourth,second/3)


if __name__=='__main__':unittest.main()
