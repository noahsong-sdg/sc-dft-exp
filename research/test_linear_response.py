import math
import unittest
from linear_response import stiffness,released_bias,sech2


class LinearResponseTests(unittest.TestCase):
    def test_normal_state_cancels(self):
        states=[(.4,0.,1.,.7,.3),(-.2,0.,.3,-.2,-.1)]
        self.assertEqual(stiffness(states,20.),0.)
        self.assertEqual(released_bias(states,20.),0.)

    def test_symmetric_states_cancel_gap_dependent_reference_bias(self):
        states=[(.4,1.,1.,.7,.3),(-.4,1.,1.,-.7,.3)]
        self.assertEqual(released_bias(states,2.),0.)

    def test_thermal_tail_does_not_use_one_minus_saturated_tanh(self):
        self.assertEqual(math.tanh(30.),1.)
        self.assertGreater(sech2(30.),0.)
        self.assertAlmostEqual(sech2(0.),1.)

    def test_zero_quasiparticle_energy_is_outside_stated_derivation(self):
        with self.assertRaises(ValueError):
            stiffness([(0.,0.,1.,1.,1.)],2.)


if __name__=='__main__':
    unittest.main()
