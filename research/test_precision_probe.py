import unittest
from precision_probe import oracle, run, stable_normal


class PrecisionTests(unittest.TestCase):
    def test_equal_energy_half_occupation(self):
        self.assertEqual(oracle(1.,1.,1e6), .5)
        self.assertEqual(stable_normal(1.,1.,1e6), .5)

    def test_held_out_grid(self):
        result = run()
        self.assertEqual(result["cases"], 120)
        self.assertEqual(result["failures_above_1e_7"], 0)
