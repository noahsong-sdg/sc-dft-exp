import json
import math
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from compare_legacy_gap import digest
from prepare_critical_mode_enrichment import prepare


class PrepareCriticalModeEnrichmentTests(unittest.TestCase):
    def test_measured_image_preservation_and_stale_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            basis, full, mode = [root/name for name in ('basis', 'full', 'mode')]
            for path in (basis, full, mode):
                path.mkdir()
            context = 'a'*64
            meta = f'tc-basis-v1\n4 1\n100\n{context}\n100 10 10 2 2 2\n'
            for path in (basis/'basis.meta', mode/'basis.meta'):
                path.write_text(meta)
            (basis/'basis.bin').write_bytes(struct.pack('<8d', 1, 0, 0, 0, 2, 0, 0, 0))
            (mode/'selected.meta').write_text('fixture')
            (mode/'selected.bin').write_bytes(b'fixture')
            (full/'mode-control.in').write_text(str(mode)+'\n'+context+'\n')
            (full/'mode-amplitude-probe.x').write_bytes(b'fixture executable identity')
            (full/'mode-amplitudes.txt').write_text('fixture readback')
            r = math.sqrt(.5)
            # Known nonsymmetric action on the measured direction.
            (full/'mode-amplitudes.bin').write_bytes(struct.pack('<8d', r, r, 0, 0, 5*r, 3*r, 0, 0))
            def manifest(paths):
                return dict(files=[dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in paths])
            bm = root/'basis-manifest.json'; bm.write_text(json.dumps(manifest([basis/'basis.meta', basis/'basis.bin'])))
            receipt = dict(status='PASS', exit=0, error=None, cwd=str(full), command=[str(full/'mode-amplitude-probe.x')])
            (full/'results/moment').mkdir(parents=True)
            receipt_path = full/'results/moment/receipt.json'; receipt_path.write_text(json.dumps(receipt))
            am = root/'amplitude-manifest.json'
            data = manifest([full/'mode-control.in', full/'mode-amplitude-probe.x', mode/'basis.meta', mode/'selected.meta', mode/'selected.bin'])
            data['receipt'] = receipt; am.write_text(json.dumps(data))
            checked = dict(dimensions=[2, 2, 2, 8], beta=100, sha256={p.name:digest(p) for p in (full/'mode-amplitudes.txt', full/'mode-amplitudes.bin')})
            result = root/'amplitude-result.json'; result.write_text(json.dumps(checked))
            with patch('prepare_critical_mode_enrichment.analyze', return_value=checked):
                report = prepare(basis, bm, full, am, result, root/'output')
                self.assertEqual(report['new_rank'], 2)
                self.assertLess(report['mode_projection_defect_norm'], 1e-14)
                self.assertLess(report['mode_action_defect_norm'], 1e-14)
                # New q=e2 and A q=(3,3,0,0), without assuming symmetry.
                values = struct.unpack('<16d', (root/'output/basis.bin').read_bytes())
                self.assertAlmostEqual(values[12], 3.)
                self.assertAlmostEqual(values[13], 3.)
                receipt_path.write_text(json.dumps(dict(receipt, status='FAIL')))
                with self.assertRaisesRegex(ValueError, 'Stale measured-mode'):
                    prepare(basis, bm, full, am, result, root/'rejected')
                self.assertFalse((root/'rejected').exists())


if __name__ == '__main__':
    unittest.main()
