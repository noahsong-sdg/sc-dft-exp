import math
import unittest
from free_electron_response_probe import reference
from response_units import penetration_depth_nm,BOHR,ELECTRON_CHARGE,MU0


class FreeElectronNormalizationTests(unittest.TestCase):
    def test_rydberg_slope_matches_two_spin_particle_density(self):
        result=reference()
        self.assertLess(abs(result['relative_density_error']),1e-8)
        self.assertGreater(result['total_particle_density'],.03)

    def test_si_conversion_matches_independent_london_density_relation(self):
        density=.04
        electron_mass=9.1093837015e-31
        london=1e9*math.sqrt(electron_mass/(MU0*(density/BOHR**3)*ELECTRON_CHARGE**2))
        self.assertLess(abs(penetration_depth_nm(density)/london-1),1e-10)

    def test_nonpositive_or_nonfinite_stiffness_has_no_real_length(self):
        for value in (0,-1,math.nan,math.inf):
            with self.assertRaises(ValueError):penetration_depth_nm(value)


if __name__=='__main__':unittest.main()
