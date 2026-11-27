from pathlib import Path
import struct
import tempfile
import unittest

from full_nonlinear_analysis import analyze


class FullNonlinearAnalysisTest(unittest.TestCase):
    def test_complete_readback_and_stale_or_nonfinite_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            text = ('# full-nonlinear-map-v1; imposed seed; NOT a converged gap\n'
                    '1 2 2 4\n1000 1e-8 1 0 1e-9 4.01e-6\n1 1 1 2\n2 1 1 2\n')
            # Four matrices in Fortran order: seed,residual,direction,Jacobian.
            values = [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 2, 0, 2, 2]
            payload = struct.pack('<16d', *values)
            (root/'full-map.txt').write_text(text)
            (root/'full-map.bin').write_bytes(payload)
            self.assertEqual(analyze(root)['sides'][0]['rms_residual_ry'], 1)
            for bad in (payload[:-1], struct.pack('<16d', float('nan'), *values[1:]),
                        struct.pack('<16d', 1, 1, *values[2:])):
                (root/'full-map.bin').write_bytes(bad)
                with self.assertRaises(ValueError):
                    analyze(root)
            (root/'full-map.bin').write_bytes(payload)
            for bad in (text.replace('map-v1', 'map-v0'), text + 'trailing\n',
                        text.replace('1 1 1 2', '1 3 1 2'), text.replace('4.01e-6', '1'),
                        text.replace('1e-8 1 0', '1e-8 1 1')):
                (root/'full-map.txt').write_text(bad)
                with self.assertRaises(ValueError):
                    analyze(root)


if __name__ == '__main__':
    unittest.main()
