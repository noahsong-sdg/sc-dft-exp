import math
import unittest

from anisotropic_velocity_reference import stiffness
from linear_response import stiffness as curvature_form
from uniform_gap_reference import stiffness as uniform_form


class AnisotropicVelocityReferenceTest(unittest.TestCase):
    def test_periodic_variable_gap_matches_curvature_form(self):
        curvature=[];velocity=[];omitted=[]
        n=4096
        for i in range(n):
            k=2*math.pi*(i+.5)/n
            xi=math.cos(k)+.13*math.cos(2*k)-.3
            v=-math.sin(k)-.26*math.sin(2*k)
            c=-math.cos(k)-.52*math.cos(2*k)
            gap=.2+.09*math.cos(k)+.04*math.sin(2*k)
            gradient=-.09*math.sin(k)+.08*math.cos(2*k)
            curvature.append((xi,gap,1/n,v/2,c/8))
            velocity.append((xi,gap,1/n,v,gradient))
            omitted.append((xi,gap,1/n,v,0.))
        for beta in (2.,8.,40.):
            with self.subTest(beta=beta):
                expected=curvature_form(curvature,beta)
                self.assertAlmostEqual(stiffness(velocity,beta),expected,delta=2e-13)
                # This fixture must detect accidentally dropping the new term.
                self.assertGreater(abs(stiffness(omitted,beta)-expected),1e-5)

    def test_constant_gap_reduces_to_existing_reference(self):
        states=[(-.3,.2,1.,.7,0.),(.8,.2,.4,-.2,0.)]
        uniform=[(xi,w,v) for xi,g,w,v,d in states]
        for beta in (1e-4,4.,400.):
            self.assertAlmostEqual(stiffness(states,beta,2.),
                uniform_form(uniform,.2,beta,2.),delta=1e-15)

    def test_real_gap_sign_and_nodal_limit(self):
        state=(.3,.2,.7,-.8,.1)
        xi,g,w,v,d=state
        self.assertEqual(stiffness([state],4.),stiffness([(xi,-g,w,v,-d)],4.))
        self.assertEqual(stiffness([(0.,0.,1.,2.,.3)],4.),0.)
        tiny=stiffness([(0.,1e-9,1.,2.,0.)],4.)
        self.assertAlmostEqual(tiny/(4*4**3*1e-18/24),1.,delta=1e-14)

    def test_rejects_nonfinite_state_and_invalid_context(self):
        for beta,volume in ((0.,1.),(1.,0.),(math.nan,1.)):
            with self.assertRaises(ValueError):stiffness([],beta,volume)
        with self.assertRaises(ValueError):
            stiffness([(.1,.2,1.,1.,math.nan)],4.)
