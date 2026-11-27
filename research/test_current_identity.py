import unittest
from current_identity import corrected_normal, direct_normal, released_normal


class CurrentIdentityTests(unittest.TestCase):
    def test_corrected_regular_branch_matches_direct_identity(self):
        for x in (.01, .4, 1., 3.):
            for d in (.02, .2, 2.):
                # Avoid cancellation in the addition formula here; the
                # saturated regime is covered by the direct-expression test.
                for beta in (.1, 1., 2.):
                    self.assertAlmostEqual(corrected_normal(x,d,beta),
                                           direct_normal(x,d,beta), places=9)

    def test_released_regular_branch_depends_on_gap(self):
        expected = direct_normal(.4,.2,2.)
        self.assertAlmostEqual(released_normal(.4,.2,0.,2.), expected)
        self.assertGreater(abs(released_normal(.4,.2,1.,2.)-expected), .1)

    def test_released_saturation_branch_uses_superconducting_energy(self):
        # x<d but sqrt(x*x+gap*gap)>d. Normal reference tends to zero.
        self.assertAlmostEqual(direct_normal(1.,2.,100.), 0.)
        self.assertGreater(released_normal(1.,2.,2.,100.), .99)


if __name__ == "__main__":
    unittest.main()
