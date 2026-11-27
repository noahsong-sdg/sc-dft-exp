import json
from pathlib import Path
import tempfile
import unittest

from finite_window_controls import analyze, interpolated_peak, odd_cubic, run
from response_analysis import TEMPERATURES
from fetch_public_response_inputs import digest


class FiniteWindowControlsTest(unittest.TestCase):
    def test_odd_cubic_recovers_known_limit_at_small_momentum(self):
        rows=[(q,2.,q,3*q-7*q**3) for q in (1e-5,2e-5,3e-5,4e-5)]
        fitted=odd_cubic(rows)
        self.assertAlmostEqual(fitted['slope'],3.,places=12)
        self.assertAlmostEqual(fitted['cubic_coefficient'],-7.,places=4)
        with self.assertRaises(ValueError):
            odd_cubic([rows[0],rows[0]])

    def test_linear_limit_and_point_removal(self):
        rows=[(q,2.,q,3*q) for q in (0.,.1,.2,.3,.4,.5)]
        checked=analyze(rows)
        for row in checked['leave_one_out_first_four']+checked['odd_cubic_fits']:
            self.assertAlmostEqual(row['lambda_ratio_to_first'],1.,places=12)
        self.assertFalse(checked['empirical_parity_test_available'])
        self.assertFalse(checked['separate_current_estimates_available'])
        perturbed=list(rows);perturbed[1]=(.1,2.,.1,.6)
        self.assertNotEqual(analyze(perturbed)['leave_one_out_first_four'][0]['slope_ratio_to_first'],1.)

    def test_irregular_peak_interpolation_and_endpoint_rejection(self):
        rows=[(q,2.,q,4-(q-.35)**2) for q in (0.,.2,.4,.8,1.)]
        peak=interpolated_peak(rows)
        self.assertTrue(peak['qualified'])
        self.assertAlmostEqual(peak['q_angstrom_inverse'],.35)
        self.assertAlmostEqual(peak['current_reported_au'],4.)
        self.assertFalse(interpolated_peak([(q,2.,q,q) for q in (0.,1.,2.)])['qualified'])

    def test_released_input_hash_is_required(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);save=root/'Si2V6-186003';save.mkdir();files=[]
            for temperature in TEMPERATURES:
                path=save/f'fflo_{temperature}.0.dat'
                path.write_text(''.join(f'{q} 2 {q} {3*q}\n' for q in (0.,.1,.2,.3,.4)))
                files.append(dict(path=str(path.relative_to(root)),bytes=path.stat().st_size,sha256=digest(path)))
            script=root/'fflo_j.sh';script.write_text('processing fixture')
            files.append(dict(path='fflo_j.sh',bytes=script.stat().st_size,sha256=digest(script)))
            manifest=root/'manifest.json';manifest.write_text(json.dumps(dict(files=files)))
            self.assertEqual(len(run(root,manifest)['temperatures_k']),7)
            path.write_text('changed legacy curve')
            with self.assertRaisesRegex(ValueError,'Changed released'):
                run(root,manifest)


if __name__=='__main__':
    unittest.main()
