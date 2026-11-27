import unittest
from response_analysis import analyze, parse_curve, slope


class ResponseTests(unittest.TestCase):
    def test_author_script_and_plot_conversion(self):
        # Archived xi.dat: ll=1844.38; fflo.gp plots 0.1*0.529177249*ll.
        rows = [(0., 3.9293, 0., 0.),
                (.0033468, 3.92925, .0025, 7.7802e-7),
                (.0066936, 3.9274, .005, 1.19955e-6),
                (.01004, 3.90265, .0075, 1.25867e-6),
                (.013387, 3.79835, .01, 1.03262e-6)]
        actual = analyze(rows)["author_single_point_lambda_nm"]
        self.assertAlmostEqual(actual, 0.1 * 0.529177249 * 1844.38, places=3)
        self.assertLess(abs(actual - 97.), 1.)

    def test_linear_current_has_window_invariant_stiffness(self):
        rows = [(float(q), 2., float(q), 3.*q) for q in range(6)]
        self.assertEqual(slope(rows[1:]), 3.)
        for window in analyze(rows)["windows"]:
            self.assertAlmostEqual(window["lambda_ratio"], 1.)

    def test_cubic_current_changes_finite_window(self):
        rows = [(q, 2., q, 3*q-q**3) for q in (0., .1, .2, .3, .4)]
        result = analyze(rows)
        self.assertGreater(result["windows"][-1]["lambda_ratio"], 1.)

    def test_rejects_nonfinite_and_duplicate_momentum(self):
        for text in ("0 1 0 0\n1 1 1 nan\n2 1 2 1\n3 1 3 1",
                     "0 1 0 0\n1 1 1 1\n1 1 2 1\n3 1 3 1"):
            with self.assertRaises(ValueError):
                parse_curve(text)


if __name__ == "__main__":
    unittest.main()
