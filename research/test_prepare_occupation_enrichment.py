import array
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from compare_legacy_gap import digest
from prepare_occupation_enrichment import prepare


class PrepareOccupationEnrichmentTests(unittest.TestCase):
    def test_file_bound_image_and_changed_persisted_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            full, reduced, basis, geometry = [root/name for name in ('full', 'reduced', 'basis', 'geometry')]
            for path in (full, reduced, basis, geometry):
                path.mkdir()
            context = 'a'*64
            (basis/'basis.meta').write_text(f'tc-basis-v1\n6 1\n100\n{context}\n2 10 10 2 3 3\n')
            (basis/'basis.bin').write_bytes(struct.pack('<12d', 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0))
            (geometry/'native-init.meta').write_text('native-init-v1; arrays are native binary64/int32, Fortran order\n3 3 3 2 512 26 3\n0 1 1 1 1 1 1\nT\n')
            x = [0., .1, .2, .3, .4, .5]
            gap = [.1, .2, .3, .4, .5, .6]
            values = [-1., 1., 1., 1., *x, *([0.]*6), *([1.]*6), *([0.]*12)]
            (geometry/'native-init.bin').write_bytes(struct.pack('<34d12i', *values, *([1]*12)))
            seed = struct.pack('<6d', *gap)
            (full/'gap-seed.bin').write_bytes(seed)
            (reduced/'reduced-gap.bin').write_bytes(seed)
            (full/'gap-seed.meta').write_text(f'gap-seed-v1; binary64 Fortran order\n3 3 3 2 10 50\n100\n{geometry}\n{context}\n')
            (reduced/'reduced-control.in').write_text(f'{basis}\n{geometry}\n/mode\n{context}\n100 .15\n')
            # Independent exponential-occupation ratio, with exact A0=2I.
            import math
            f = []
            for xi, delta in zip(x, gap):
                e = math.hypot(xi, delta)
                tanh = lambda z: (1-math.exp(-2*z))/(1+math.exp(-2*z))
                denominator = tanh(50*abs(xi))/abs(xi) if xi else 50
                f.append(delta/e*tanh(50*e)/denominator)
            (full/'full-map.bin').write_bytes(seed+struct.pack('<6d', *(2*v-d for v, d in zip(f, gap))))
            inputs = [basis/'basis.meta', basis/'basis.bin', geometry/'native-init.meta', geometry/'native-init.bin']
            manifest = root/'basis-manifest.json'
            manifest.write_text(json.dumps(dict(files=[dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in inputs])))
            full_manifest = root/'full-manifest.json'; full_manifest.write_text('{}')
            checked = dict(full_readback=dict(beta=100.), stationary_residual_targets_met=False)
            candidate = dict(dimensions=[3, 3, 3, 2, 1], beta=100.)
            with patch('prepare_occupation_enrichment.verify', return_value=checked), patch('prepare_occupation_enrichment.reduced_readback', return_value=candidate):
                report = prepare(full, full_manifest, reduced, manifest, root/'output')
                self.assertEqual(report['new_rank'], 2)
                data = array.array('d'); data.frombytes((root/'output/basis.bin').read_bytes())
                self.assertEqual(list(data[:6]), [1., 0., 0., 0., 0., 0.])
                for q, aq in zip(data[6:12], data[18:24]):
                    self.assertAlmostEqual(aq, 2*q, places=13)
                # A changed persisted basis must fail before creating output.
                (basis/'basis.bin').write_bytes(b'stale')
                with self.assertRaisesRegex(ValueError, 'Changed declared'):
                    prepare(full, full_manifest, reduced, manifest, root/'rejected')
                self.assertFalse((root/'rejected').exists())


if __name__ == '__main__':
    unittest.main()
