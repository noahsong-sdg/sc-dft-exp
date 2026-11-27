import unittest
from full_current_probe import correction


class PatchBoundaryTests(unittest.TestCase):
    def test_changes_only_normal_branch(self):
        condition = "IF(xi(igap,ii)**2 + delta(igap,ii)**2 > dxq(igap,ii)**2) THEN"
        normal = "IF(1.0_dp - tanhd * tanhx < 1.0e-10_dp) THEN"
        source = condition + "\n" + normal + "\n" + condition + "\nx_d = tanhe * factor"
        result = correction(source)
        self.assertEqual(result.split(normal)[0], condition + "\n")
        self.assertIn("IF(xi(igap,ii)**2 > dxq(igap,ii)**2) THEN", result)
        self.assertIn("x_d = tanhx * factor", result)

    def test_rejects_changed_source(self):
        with self.assertRaises(ValueError):
            correction("unrecognized source")
