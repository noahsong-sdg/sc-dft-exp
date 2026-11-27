import unittest
from state_format import parse_current_record


class StateFormatTests(unittest.TestCase):
    def test_current_state_preserves_curvature(self):
        values, indices = parse_current_record("1D-2 2e-3 1 .008 .01 -.2 1 4")
        self.assertEqual(values[-1], -.2)
        self.assertEqual(indices, (1, 4))

    def test_archived_legacy_state_is_rejected(self):
        archived = "-4.68774234432135 -2.64197278292306e-5 .036517307749784 .008 0 1 1"
        with self.assertRaisesRegex(ValueError, "lacks d2xq"):
            parse_current_record(archived)

    def test_nonfinite_state_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Nonfinite"):
            parse_current_record("0 0 1 .008 0 nan 1 1")
