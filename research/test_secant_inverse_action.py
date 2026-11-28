"""Independent exact dense secant equation, held-out failure, and finite limits."""
from fractions import Fraction as F
import math
import unittest

from secant_inverse_action import action,factors


class SecantInverseActionTest(unittest.TestCase):
    def test_exact_nonsymmetric_dense_oracle_and_other_rhs(self):
        b=[[F(1),F(1,3),F(0)],[F(0),F(4,5),F(-1,7)],[F(1,6),F(0),F(3,2)]]
        j=[[F(2),F(1,4),F(0)],[F(-1,3),F(1),F(1,5)],[F(0),F(1,7),F(4,3)]]
        v=[F(1),F(-1,2),F(1,4)]
        def mv(m,x):return [sum(a*c for a,c in zip(row,x)) for row in m]
        z=mv(j,v);bz=mv(b,z);u=[a-c for a,c in zip(v,bz)]
        w=[a/sum(c*c for c in z) for a in z]
        updated=[[b[i][k]+u[i]*w[k] for k in range(3)] for i in range(3)]
        self.assertEqual(mv(updated,z),v)
        actual=factors(*[[float(x) for x in block] for block in (v,z,bz)])
        for rhs in (z,[F(1,5),F(-2,7),F(4,9)]):
            expected=mv(updated,rhs)
            result=action(*actual,list(map(float,rhs)),list(map(float,mv(b,rhs))))
            self.assertLess(max(abs(a-float(c)) for a,c in zip(result,expected)),2e-15)
        # Any other exact solution differs by rows perpendicular to z.
        perpendicular=[z[1],-z[0],F(0)]
        alternative=[[u[i]*w[k]+(i+1)*perpendicular[k] for k in range(3)] for i in range(3)]
        minimum=sum(x*x for row in [[a*c for c in w] for a in u] for x in row)
        other=sum(x*x for row in alternative for x in row)
        self.assertGreater(other,minimum)

    def test_training_fit_can_worsen_held_out_direction(self):
        # J=[[1,0],[1,1]], B=I. Training e1 improves; held-out e2 gets worse.
        u,w=factors([1.,0.],[1.,1.],[1.,1.])
        self.assertEqual(list(action(u,w,[1.,1.],[1.,1.])),[1.,0.])
        heldout=action(u,w,[0.,1.],[0.,1.])
        self.assertEqual(list(heldout),[0.,.5])
        self.assertGreater(max(abs(a-b) for a,b in zip(heldout,[0.,1.])),0.)

    def test_scaling_shape_nonfinite_and_zero_boundaries(self):
        for scale in (1e-150,1e150):
            u,w=factors([1.,-.5],[scale,2*scale],[.25,.125])
            got=action(u,w,[scale,2*scale],[.25,.125])
            self.assertLess(max(abs(a-b) for a,b in zip(got,[1.,-.5])),1e-15)
        for args in (([],[],[]),([1.],[0.],[0.]),([1.],[1.,2.],[0.]),([math.nan],[1.],[0.]),([1.],[1e-320],[0.])):
            with self.assertRaises(ValueError):factors(*args)
        for args in (([1.],[1.],[1.,2.],[0.]),([1.],[math.inf],[1.],[0.]),([1e308],[1.],[2.],[0.])):
            with self.assertRaises(ValueError):action(*args)
