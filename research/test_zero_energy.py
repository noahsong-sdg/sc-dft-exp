import unittest
from full_current_probe import zero_energy_correction


class ZeroEnergyCorrectionTests(unittest.TestCase):
    def test_exact_product_and_boundary_only(self):
        source='''      j_q(ii) = j_q(ii) + dk(igap, ii) * ( &
      & xi(igap, ii)/e_qp*e_d )
'''
        patched=zero_energy_correction(source)
        self.assertIn('IF(e_qp == 0.0_dp) THEN\n        e_d = 0.0_dp',patched)
        self.assertIn('ELSE\n        e_d = xi(igap, ii)/e_qp*e_d',patched)
        self.assertTrue(patched.endswith('& e_d )\n'))

    def test_changed_or_already_patched_source_is_rejected(self):
        for source in ('different source','xi(igap, ii)/e_qp*e_d'):
            with self.assertRaises(ValueError):zero_energy_correction(source)


if __name__=='__main__':unittest.main()
