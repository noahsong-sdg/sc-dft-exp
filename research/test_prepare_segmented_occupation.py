import array
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from compare_legacy_gap import digest
from prepare_segmented_occupation import prepare


class PrepareSegmentedOccupationTests(unittest.TestCase):
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
            (reduced/'reduced-result.txt').write_text('fixture summary; readback independently patched\n')
            inputs = [basis/'basis.meta', basis/'basis.bin', geometry/'native-init.meta', geometry/'native-init.bin',
                      reduced/'reduced-control.in', reduced/'reduced-gap.bin', reduced/'reduced-result.txt']
            manifest = root/'basis-manifest.json'
            manifest.write_text(json.dumps(dict(cwd=str(full), files=[dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in inputs])))
            full_manifest = manifest
            checked = dict(full_readback=dict(beta=100.), stationary_residual_targets_met=False)
            candidate = dict(dimensions=[3, 3, 3, 2, 1], beta=100.)
            certificate = dict(complete_left_row_coverage=True, full_candidate=checked,
                               terminal_guard_pass=True, inputs_unchanged=True, manifest_sha256=digest(manifest),
                               receipt={}, checkpoint=dict(sha256={}), microscopic_split_qualified=False)
            full_result = root/'certified.json'; full_result.write_text(json.dumps(certificate))
            with patch('prepare_segmented_occupation.certify', return_value=certificate), patch('prepare_segmented_occupation.reduced_readback', return_value=candidate):
                report = prepare(full, full_manifest, full_result, reduced, root/'output')
                self.assertEqual(report['new_rank'], 2)
                data = array.array('d'); data.frombytes((root/'output/basis.bin').read_bytes())
                self.assertEqual(list(data[:6]), [1., 0., 0., 0., 0., 0.])
                for q, aq in zip(data[6:12], data[18:24]):
                    self.assertAlmostEqual(aq, 2*q, places=13)
                self.assertFalse(report['full_candidate_targets_met'])
                # Partial, stale published and unpinned reduced-control contexts
                # cannot reuse a passing arithmetic fixture as provenance.
                certificate['complete_left_row_coverage'] = False
                with self.assertRaisesRegex(ValueError, 'Complete owning'):
                    prepare(full, full_manifest, full_result, reduced, root/'partial')
                self.assertFalse((root/'partial').exists())
                certificate['complete_left_row_coverage'] = True
                old = full_result.read_text()
                recorded = json.loads(old); recorded['full_candidate']['stationary_residual_targets_met'] = True
                full_result.write_text(json.dumps(recorded))
                with self.assertRaisesRegex(ValueError, 'recorded certification'):
                    prepare(full, full_manifest, full_result, reduced, root/'stale-record')
                self.assertFalse((root/'stale-record').exists()); full_result.write_text(old)
                raw = json.loads(manifest.read_text())
                altered = dict(raw, cwd=str(root/'other'))
                manifest.write_text(json.dumps(altered))
                with self.assertRaisesRegex(ValueError, 'Complete owning'):
                    prepare(full, full_manifest, full_result, reduced, root/'wrong-root')
                self.assertFalse((root/'wrong-root').exists()); manifest.write_text(json.dumps(raw))
                altered = dict(raw, files=[x for x in raw['files'] if x['path'] != str(reduced/'reduced-control.in')])
                manifest.write_text(json.dumps(altered))
                with self.assertRaisesRegex(ValueError, 'Changed declared'):
                    prepare(full, full_manifest, full_result, reduced, root/'unpinned')
                self.assertFalse((root/'unpinned').exists()); manifest.write_text(json.dumps(raw))
                # A changed persisted basis must fail before creating output.
                (basis/'basis.bin').write_bytes(b'stale')
                with self.assertRaisesRegex(ValueError, 'Changed declared'):
                    prepare(full, full_manifest, full_result, reduced, root/'rejected')
                self.assertFalse((root/'rejected').exists())

    def test_failed_chain_certification_has_no_fallback_or_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch('prepare_segmented_occupation.certify', side_effect=ValueError('invalid chain')):
                with self.assertRaisesRegex(ValueError, 'invalid chain'):
                    prepare(root/'full', root/'manifest', root/'result', root/'reduced', root/'output')
            self.assertFalse((root/'output').exists())


if __name__ == '__main__':
    unittest.main()
