from decimal import Decimal
import unittest

from gauss_decimal_reference import reference


class DecimalGaussTest(unittest.TestCase):
    def test_independent_polynomial_exactness_and_symmetry(self):
        result = reference()
        nodes = list(map(Decimal, result['nodes_decimal']))
        weights = list(map(Decimal, result['weights_decimal']))
        self.assertEqual(len(nodes), 100)
        self.assertTrue(all(-1 < x < 1 for x in nodes))
        self.assertTrue(all(w > 0 for w in weights))
        self.assertTrue(all(a < b for a, b in zip(nodes, nodes[1:])))
        self.assertLess(Decimal(result['max_absolute_moment_error_through_degree199']), Decimal('1e-60'))
        self.assertLess(max(abs(a+b) for a, b in zip(nodes, reversed(nodes))), Decimal('1e-60'))
        self.assertLess(max(abs(a-b) for a, b in zip(weights, reversed(weights))), Decimal('1e-60'))
        self.assertFalse(result['production_grid_replacement'])
