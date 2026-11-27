import math
import unittest

from linear_response import stiffness as curvature_form
from uniform_gap_reference import stiffness as velocity_form


class UniformGapReferenceTest(unittest.TestCase):
    def test_periodic_band_integration_by_parts_at_finite_temperature(self):
        # Smooth periodic dispersion: no boundary term and analytic derivatives.
        n=4096;gap=.2
        curvature=[];velocity=[]
        for i in range(n):
            k=2*math.pi*(i+.5)/n
            xi=math.cos(k)-.3;v=-math.sin(k);c=-math.cos(k)
            curvature.append((xi,gap,1/n,v/2,c/8))
            velocity.append((xi,1/n,v))
        for beta in (2.,8.,40.):
            with self.subTest(beta=beta):
                self.assertAlmostEqual(curvature_form(curvature,beta),velocity_form(velocity,gap,beta),delta=2e-13)

    def test_zero_gap_and_small_energy_limit(self):
        self.assertEqual(velocity_form([(0.,1.,2.),(1.,1.,3.)],0.,4.),0.)
        # At xi=0, beta*gap ->0: kernel -> beta^3*gap^2/24.
        gap=1e-9;beta=4.
        actual=velocity_form([(0.,1.,2.)],gap,beta)
        expected=4*beta**3*gap**2/24
        self.assertAlmostEqual(actual/expected,1.,delta=1e-14)
