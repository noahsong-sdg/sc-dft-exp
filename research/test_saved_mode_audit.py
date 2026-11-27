import math
from pathlib import Path
import struct
import tempfile
import unittest

from saved_mode_audit import audit


class SavedModeAuditTest(unittest.TestCase):
    def test_saved_residual_and_fermi_readback_with_stale_rejections(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            mode, prepare = root/'mode', root/'prepare'
            mode.mkdir(); prepare.mkdir()
            vector = [1/math.sqrt(6), 0, 1/math.sqrt(6), 2/math.sqrt(6)]
            residual = [1e-10*x for x in vector]
            relative = 1e-10/(1.1+1e-10)
            meta = f'1 1\n1.1 {relative:.17g}\n'
            (mode/'selected.meta').write_text(meta)
            basis = 'tc-basis-v1\n4 1\n1000\n'+'a'*64+'\n2 10 10 2 1 2\n'
            (mode/'basis.meta').write_text(basis)
            payload = struct.pack('<8d', *vector, *residual)
            (mode/'selected.bin').write_bytes(payload)
            (prepare/'native-init.meta').write_text(
                'native-init-v1; arrays are native binary64/int32, Fortran order\n'
                '1 2 2 2 1 1 1\n1 1e-4 1e-5 1 1 1 1\nT\n')
            reals = [-1, 1, .5, .5] + [0, 0, 0, .001] + [0]*4 + [1, 0, 1, 1] + [0]*8
            state = struct.pack('<24d8i', *reals, *([0]*8))
            (prepare/'native-init.bin').write_bytes(state)
            result = audit(mode, prepare)
            self.assertTrue(result['same_sign_fermi_averages'])
            self.assertAlmostEqual(result['vector_norm'], 1)
            for bad in (payload[:-1], struct.pack('<8d', math.nan, *vector[1:], *residual),
                        struct.pack('<8d', vector[0], 1, *vector[2:], *residual)):
                (mode/'selected.bin').write_bytes(bad)
                with self.assertRaises(ValueError):
                    audit(mode, prepare)
            (mode/'selected.bin').write_bytes(payload)
            for bad in (meta+'extra\n', meta.replace('1.1 ', 'nan '), meta.replace(f'{relative:.17g}', '.1')):
                (mode/'selected.meta').write_text(bad)
                with self.assertRaises(ValueError):
                    audit(mode, prepare)
            (mode/'selected.meta').write_text(meta)
            (mode/'basis.meta').write_text(basis.replace('4 1', '6 1'))
            with self.assertRaises(ValueError):
                audit(mode, prepare)


if __name__ == '__main__':
    unittest.main()
