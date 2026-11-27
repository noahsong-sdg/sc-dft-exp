from pathlib import Path
import tempfile
import unittest

from nonlinear_map_analysis import analyze


class SelectedMapAnalysisTest(unittest.TestCase):
    SAMPLE = '''# selected-nonlinear-map-v1; imposed seed; NOT a converged gap
32 40 40 100 10 50
19613.355577892344 4 1e-20
1 8 0.1 1e-20 1e-14 0.01
16 23 0.2 1e-20 1e-14 0.02
25 32 0.3 1e-20 1e-14 0.03
'''

    def read(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'selected-map.txt'
            path.write_text(text)
            return analyze(path)

    def test_complete_output(self):
        result = self.read(self.SAMPLE)
        self.assertEqual(result['exact_zero_energy_products'], 4)
        self.assertEqual([row['first'] for row in result['tiles']], [1, 16, 25])

    def test_stale_incomplete_and_nonfinite_outputs_fail(self):
        for text in (self.SAMPLE.replace('v1;', 'v0;'), self.SAMPLE.rsplit('\n', 2)[0],
                     self.SAMPLE.replace('19613.355577892344', 'nan'),
                     self.SAMPLE.replace(' 4 1e-20', ' 0 1e-20'),
                     self.SAMPLE.replace('16 23', '17 24'), self.SAMPLE + 'trailing\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.read(text)


if __name__ == '__main__':
    unittest.main()
