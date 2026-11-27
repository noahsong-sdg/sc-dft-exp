import math
import unittest

from occupation_enrichment import dot, enrich


class OccupationEnrichmentTests(unittest.TestCase):
    def test_nonsymmetric_exact_operator_and_reorthogonalization(self):
        a = [[2., 3., -1., .2], [-4., 1., 2., .5], [1., -2., 3., 4.], [2., 0., -1., 1.]]
        apply = lambda x: [dot(row, x) for row in a]
        r = math.sqrt(.5)
        q = [[r, r, 0., 0.], [0., 0., r, r]]
        u = list(map(apply, q))
        f = [.7, -.3, .2, .9]
        new, image, report = enrich(q, u, f, apply(f))
        for actual, expected in zip(image, apply(new)):
            self.assertAlmostEqual(actual, expected, places=13)
        self.assertLess(report['new_direction_old_basis_overlap'], 1e-14)
        self.assertAlmostEqual(dot(new, new), 1., places=14)
        self.assertFalse(report['inherited_operator_consistency_verified'])

    def test_unresolved_direction_and_invalid_basis_are_rejected(self):
        for f in ([1., 0., 0.], [1., 1e-16, 0.]):
            with self.assertRaisesRegex(ValueError, 'unresolved'):
                enrich([[1., 0., 0.]], [[2., 0., 0.]], f, [2., 0., 0.])
        with self.assertRaisesRegex(ValueError, 'orthonormal'):
            enrich([[2., 0., 0.]], [[2., 0., 0.]], [1., 1., 0.], [2., 1., 0.])
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            enrich([[1., 0., 0.]], [[2., 0., 0.]], [1., math.nan, 0.], [2., 1., 0.])


if __name__ == '__main__':
    unittest.main()
