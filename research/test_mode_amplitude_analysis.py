import math
from pathlib import Path
import struct
import tempfile
import unittest

from mode_amplitude_analysis import AMPLITUDES, analyze


class ModeAmplitudeAnalysisTest(unittest.TestCase):
    def test_readback_and_corrupt_or_stale_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            v = [1/math.sqrt(3), 0, 1/math.sqrt(3), 1/math.sqrt(3)]
            eigenvalue = 1.00186
            linear = [eigenvalue*x for x in v]
            bound = 2e-13+2e-12*max(map(abs,linear))
            lines = ['# mode-amplitudes-v1; projected candidates; NOT solved gaps',
                     '1 2 2 8', f'1000 {eigenvalue} 0 {bound:.17g} 0 1']
            values = v + linear
            for a in AMPLITUDES:
                scale = a*1e-5
                image = [scale*eigenvalue/(1+a*a)*x for x in v]
                residual = [x-scale*y for x,y in zip(image,v)]
                projection = math.fsum(x*y for x,y in zip(v,residual))/math.fsum(x*x for x in v)
                metrics = [a, scale, projection, max(map(abs,residual)),
                           math.sqrt(math.fsum(x*x for x in residual)/3), residual[0], residual[2]]
                lines.append(' '.join(f'{x:.17g}' for x in metrics))
                values += image
            text = '\n'.join(lines)+'\n'
            payload = struct.pack('<36d', *values)
            (root/'mode-amplitudes.txt').write_text(text)
            (root/'mode-amplitudes.bin').write_bytes(payload)
            result = analyze(root)
            self.assertEqual(result['projected_sign_change_intervals_mev'], [[.025,.05]])
            for bad in (payload[:-1], struct.pack('<36d', math.nan, *values[1:]),
                        struct.pack('<36d', values[0], 1, *values[2:])):
                (root/'mode-amplitudes.bin').write_bytes(bad)
                with self.assertRaises(ValueError):
                    analyze(root)
            (root/'mode-amplitudes.bin').write_bytes(payload)
            changed = lines.copy()
            fields = changed[3].split(); fields[0] = '0.026'; changed[3] = ' '.join(fields)
            for bad in (text.replace('amplitudes-v1','amplitudes-v0'), text+'extra\n',
                        '\n'.join(changed)+'\n'):
                (root/'mode-amplitudes.txt').write_text(bad)
                with self.assertRaises(ValueError):
                    analyze(root)


if __name__ == '__main__':
    unittest.main()
