import json
from pathlib import Path
import tempfile
import unittest

from fetch_public_response_inputs import digest
from portable_full_checkpoint_build import stage


class PortableFullCheckpointBuildTests(unittest.TestCase):
    def parent(self, root):
        prior = root/'parent'; (prior/'results/build').mkdir(parents=True)
        exe = prior/'full-gap-check.x'; exe.write_bytes(b'qualified source-built parent')
        command = ['python', 'source-build']
        (prior/'qualification-result.json').write_text(json.dumps(dict(
            checks=902, all_checks_bitwise_equal=True, full_gap_driver_linked=True,
            full_gap_executable_sha256=digest(exe))))
        receipt = prior/'results/build/receipt.json'
        receipt.write_text(json.dumps(dict(status='PASS', exit=0, error=None, command=command, cwd=str(prior))))
        manifest = root/'parent.json'
        manifest.write_text(json.dumps(dict(cwd=str(prior), command=command, public_build=str(root/'public'),
                                            files=[dict(path=str(exe), bytes=exe.stat().st_size, sha256=digest(exe))])))
        return prior, manifest

    def test_new_source_and_guard_are_bound_without_rewriting_parent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); prior, manifest = self.parent(root)
            before = manifest.read_bytes()
            staged = stage(manifest, root/'new')
            self.assertEqual(manifest.read_bytes(), before)
            names = {Path(item['path']).name for item in staged['files']}
            self.assertTrue({'full_nonlinear_checkpoint_probe.f90', 'full_map_checkpoint.f90',
                             'linear_image_checkpoint.f90', 'full_checkpoint_link.mk',
                             'macos_native_guard_v2.py'} <= names)
            self.assertEqual(staged['guard_seconds'], 120)
            self.assertFalse(staged['historical_objects_used'])

    def test_stale_parent_executable_receipt_and_unqualified_result_create_no_output(self):
        for mutation in ('same_size_bytes', 'receipt', 'qualification'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); prior, manifest = self.parent(root)
                if mutation == 'same_size_bytes':
                    exe = prior/'full-gap-check.x'; exe.write_bytes(b'x'*exe.stat().st_size)
                if mutation == 'receipt':
                    receipt = prior/'results/build/receipt.json'; data = json.loads(receipt.read_text())
                    data['cwd'] = str(root/'wrong'); receipt.write_text(json.dumps(data))
                if mutation == 'qualification':
                    proof = prior/'qualification-result.json'; data = json.loads(proof.read_text())
                    data['checks'] = 901; proof.write_text(json.dumps(data))
                with self.assertRaises(ValueError): stage(manifest, root/'new')
                self.assertFalse((root/'new').exists())


if __name__ == '__main__':
    unittest.main()
