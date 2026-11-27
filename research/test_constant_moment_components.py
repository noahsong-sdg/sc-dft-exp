import math
import unittest

from constant_moment_components import components


class ConstantComponentsTest(unittest.TestCase):
    def test_signed_and_zero_dos_support_is_not_discarded_from_either_term(self):
        dims=[2,6,6,1,2];physical=[2.,3.,1.,0.,0.]
        raw=dict(xi0=[-1.,1.],dx0=[.25,.75],dos=[-1.,0.,-1.,0.],
                 second=[3.,-2.,5.,7.],curvature=[11.,13.,17.,19.])
        rows=components(dims,physical,raw,2.,1.)
        thermal=2*(1/math.cosh(1)**2-1/math.cosh(math.sqrt(2))**2)
        curvature=4*(math.tanh(1)-math.tanh(math.sqrt(2))/math.sqrt(2))
        for row,v,h in zip(rows,(-.75,6.5),(7.,10.)):
            self.assertAlmostEqual(row['thermal_velocity_squared'],thermal*v/12,places=15)
            self.assertAlmostEqual(row['curvature_term'],curvature*h/12,places=15)
            self.assertAlmostEqual(row['total'],(thermal*v+curvature*h)/12,places=15)
        self.assertLess(rows[0]['thermal_velocity_squared'],0)


if __name__=='__main__':
    unittest.main()
