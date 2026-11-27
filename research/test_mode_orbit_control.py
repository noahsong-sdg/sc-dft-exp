import json
import math
from pathlib import Path
import struct
import tempfile
import unittest

from compare_legacy_gap import digest
from gap_symmetry_audit import HEADER
from mode_amplitude_analysis import AMPLITUDES, analyze
from mode_orbit_control import audit


class ModeOrbitControlTest(unittest.TestCase):
    def test_actual_amplitude_schema_and_stale_context_or_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); prepare = root/'prepare'; prepare.mkdir()
            mode = root/'mode'; mode.mkdir(); context = 'a'*64
            (mode/'basis.meta').write_text('tc-basis-v1\n4 1\n1000\n'+context+'\n2 10 10 2 1 2\n')
            (prepare/'native-init.meta').write_text(
                'native-init-v1; arrays are native binary64/int32, Fortran order\n'
                '1 2 2 2 1 2 1\n0 1e-7 1 1 1 1 1\nT\n')
            values = [-1, 1, .5, .5]+[.1, 0, .1, .1]+[0]*4+[.5, 0, .5, .5]+[0]*8
            (prepare/'native-init.bin').write_bytes(struct.pack('<24d8i', *values, 1, 0, 1, 1, 1, 0, 1, 2))
            (root/'mode-amplitude-probe.x').write_bytes(b'fixture')
            (root/'map-control.in').write_text(str(prepare)+'\n')
            (root/'mode-control.in').write_text(str(mode)+'\n'+context+'\n')
            v = [1/math.sqrt(3), 0, 1/math.sqrt(3), 1/math.sqrt(3)]
            eigenvalue = 1.00186; linear = [eigenvalue*x for x in v]
            bound = 2e-13+2e-12*max(linear)
            lines = ['# mode-amplitudes-v1; projected candidates; NOT solved gaps',
                     '1 2 2 8', f'1000 {eigenvalue} 0 {bound:.17g} 0 1']
            payload = v+linear
            for amplitude in AMPLITUDES:
                scale = amplitude*1e-5
                image = [scale*eigenvalue/(1+amplitude**2)*x for x in v]
                residual = [a-scale*b for a, b in zip(image, v)]
                fields = [amplitude, scale, math.fsum(a*b for a,b in zip(v,residual))/math.fsum(x*x for x in v),
                          max(map(abs,residual)), math.sqrt(math.fsum(x*x for x in residual)/3), residual[0], residual[2]]
                lines.append(' '.join(f'{x:.17g}' for x in fields)); payload.extend(image)
            (root/'mode-amplitudes.txt').write_text('\n'.join(lines)+'\n')
            (root/'mode-amplitudes.bin').write_bytes(struct.pack('<36d', *payload))
            receipt = dict(status='PASS', exit=0, error=None, cwd=str(root), command=[str(root/'mode-amplitude-probe.x')])
            result_dir = root/'results/moment'; result_dir.mkdir(parents=True)
            receipt_path = result_dir/'receipt.json'; receipt_path.write_text(json.dumps(receipt))
            def entries(paths):
                return [dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in paths]
            am = root/'am.json'; gm = root/'gm.json'; recorded = root/'recorded.json'
            am.write_text(json.dumps(dict(receipt=receipt, files=entries([root/'mode-amplitude-probe.x',
                root/'map-control.in', root/'mode-control.in', mode/'basis.meta']))))
            geometry = dict(context=context, beta=1000, files=entries([prepare/'native-init.meta', prepare/'native-init.bin']))
            gm.write_text(json.dumps(geometry)); recorded.write_text(json.dumps(analyze(root)))
            symmetry = root/'symmetry.txt'
            symmetry.write_text(HEADER+'\n2 1 1 1 1 1 1\n1 0 0 0 1 0 0 0 1\n-1 0 0 0 -1 0 0 0 -1\n')
            result = audit(root, am, recorded, gm, symmetry)
            self.assertEqual(len(result['reports']), 2)
            self.assertTrue(all(row['gap_symmetry_test_passed'] for row in result['reports'].values()))
            gm.write_text(json.dumps({**geometry, 'context': 'b'*64}))
            with self.assertRaisesRegex(ValueError, 'geometry context'):
                audit(root, am, recorded, gm, symmetry)
            gm.write_text(json.dumps(geometry)); receipt_path.write_text(json.dumps({**receipt, 'status': 'FAIL'}))
            with self.assertRaisesRegex(ValueError, 'execution receipt'):
                audit(root, am, recorded, gm, symmetry)


if __name__ == '__main__':
    unittest.main()
