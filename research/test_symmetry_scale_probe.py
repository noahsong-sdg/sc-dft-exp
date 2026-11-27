import unittest

from symmetry_scale_probe import run


class SymmetryScaleTest(unittest.TestCase):
    def test_nonzero_direction_is_scale_invariant_and_zero_is_distinct(self):
        result = run()['results']
        released = result['released']
        self.assertEqual([row['retained_symmetries'] for row in released], [1, 1, 2, 2, 2, 2])
        self.assertLess(max(released[2]['first_moment_squared_retention']), 1e-25)
        for row in result['relative'][:-1]:
            self.assertEqual(row['retained_symmetries'], 1)
            for retention in row['first_moment_squared_retention']:
                self.assertAlmostEqual(retention, 1., places=13)
        zero = result['relative'][-1]
        self.assertEqual(zero['q_fractional'], 0.)
        self.assertEqual(zero['retained_symmetries'], 2)
        self.assertLess(max(zero['first_moment_squared_retention']), 1e-25)


if __name__ == '__main__':
    unittest.main()
