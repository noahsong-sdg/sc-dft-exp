import unittest
from full_rhs_probe import corrected


class RHSPatchBoundaryTests(unittest.TestCase):
    def test_earlier_zero_temperature_else_is_not_selected(self):
        cold = ('        IF(cold_boundary) THEN\n'
                '          chi(igap,ii) = 1.0_dp\n'
                '        ELSE\n          chi(igap,ii) = 0.0_dp\n'
                '        END IF\n')
        start = '        IF(1.0_dp - tanhd * tanhe < 1.0e-10_dp) THEN'
        regular = ('\n        ELSE\n          chi(igap,ii) = regular_expression\n'
                   '        END IF\n')
        result=corrected(cold+start+'\n          obsolete_shortcut\n'+regular)
        self.assertTrue(result.startswith(cold))
        self.assertTrue(result.endswith(regular))
        self.assertNotIn('obsolete_shortcut',result)
        self.assertIn('TANH(0.5_dp*beta*',result)

    def test_changed_saturation_boundary_is_rejected(self):
        with self.assertRaises(ValueError):
            corrected('changed upstream routine')


if __name__ == '__main__':
    unittest.main()
