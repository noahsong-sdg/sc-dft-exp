import math
import unittest

from restart_mode_analysis import overlap,advancement


class RestartModeOverlapTest(unittest.TestCase):
    def test_target_prefix_and_new_orthogonal_directions(self):
        target=[1/math.sqrt(2),1/math.sqrt(2)]
        self.assertAlmostEqual(overlap(target,[3.,3.,0.]),1.)
        self.assertAlmostEqual(overlap(target,[-3.,-3.,0.]),1.)
        self.assertAlmostEqual(overlap(target,[0.,0.,1.]),0.)
        self.assertAlmostEqual(overlap(target,[1.,1.,2.]),1/math.sqrt(3))

    def test_invalid_overlap(self):
        for target,mode in (([1.,0.],[1.]),([0.],[1.]),([1.],[math.nan])):
            with self.assertRaises(ValueError):overlap(target,mode)

    def test_continuation_requires_same_mode_and_measured_improvement(self):
        mode=dict(relative_residual=.001,normalized_overlap=.999,eigenvalue=1.002)
        self.assertEqual(advancement(.002,mode,True),(2.,True))
        self.assertFalse(advancement(.0019,mode,True)[1])
        self.assertFalse(advancement(.002,mode,False)[1])
        self.assertFalse(advancement(.002,{**mode,'normalized_overlap':.98},True)[1])
        self.assertFalse(advancement(.002,{**mode,'eigenvalue':1.},True)[1])
        self.assertEqual(advancement(.002,{**mode,'relative_residual':0.},True),(None,True))
