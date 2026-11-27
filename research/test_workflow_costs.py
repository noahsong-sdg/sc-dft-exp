import unittest
from workflow_costs import duration


class ClockTests(unittest.TestCase):
    def test_multiunit_and_spaced_clock(self):
        self.assertEqual(duration("1d12h28m"), 131280.)
        self.assertAlmostEqual(duration("12m12.02s"), 732.02)
        self.assertEqual(duration(" 1h 2m 3.5s "), 3723.5)

    def test_unknown_clock_rejected(self):
        with self.assertRaises(ValueError):
            duration("not reported")
