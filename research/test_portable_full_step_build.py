import json
from pathlib import Path
import tempfile
import unittest

from fetch_public_response_inputs import digest
from portable_full_step_build import stage


class PortableFullStepBuildTests(unittest.TestCase):
    def parent(self, root):
        prior = root/'parent'; (prior/'results/build').mkdir(parents=True)
        exe = prior/'full-gap-check.x'; exe.write_bytes(b'qualified source-built parent')
        command = ['python', 'source-build']
        (prior/'qualification-result.json').write_text(json.dumps(dict(
            checks=902, all_checks_bitwise_equal=True, full_gap_driver_linked=True,
            full_gap_executable_sha256=digest(exe))))
        receipt = prior/'results/build/receipt.json'
        receipt.write_text(json.dumps(dict(status='PASS', exit=0, error=None, command=command, cwd=str(prior),
                                          guard_source_sha256='a'*64, continuous_deadline_s=120, wall_s=1,
                                          max_individual_descendant_rss_bytes=1024, sampled_peak_group_rss_bytes=2048)))
        manifest = root/'parent.json'
        manifest.write_text(json.dumps(dict(cwd=str(prior), command=command, public_build=str(root/'public'),
                                            guard_source_sha256='a'*64, guard_seconds=120, group_rss_cap_bytes=3221225472,
                                            files=[dict(path=str(exe), bytes=exe.stat().st_size, sha256=digest(exe))])))
        (prior/'run-manifest.json').write_bytes(manifest.read_bytes())
        return prior, manifest

    def test_new_source_and_guard_are_bound_without_rewriting_parent(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); prior, manifest = self.parent(root)
            before = manifest.read_bytes()
            staged = stage(manifest, root/'new')
            self.assertEqual(manifest.read_bytes(), before)
            names = {Path(item['path']).name for item in staged['files']}
            self.assertTrue({'full_nonlinear_step_probe.f90', 'declared_full_direction.f90', 'full_step_checkpoint.f90',
                             'linear_image_checkpoint.f90', 'full_step_link.mk',
                             'macos_native_guard_v2.py'} <= names)
            self.assertEqual(staged['guard_seconds'], 120)
            self.assertFalse(staged['historical_objects_used'])

    def test_stale_parent_executable_receipt_and_unqualified_result_create_no_output(self):
        for mutation in ('same_size_bytes', 'receipt', 'qualification', 'guard', 'deadline', 'consumed'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as folder:
                root = Path(folder); prior, manifest = self.parent(root)
                if mutation == 'same_size_bytes':
                    exe = prior/'full-gap-check.x'; exe.write_bytes(b'x'*exe.stat().st_size)
                if mutation == 'receipt':
                    receipt = prior/'results/build/receipt.json'; data = json.loads(receipt.read_text())
                    data['cwd'] = str(root/'wrong'); receipt.write_text(json.dumps(data))
                if mutation in ('guard', 'deadline'):
                    receipt = prior/'results/build/receipt.json'; data = json.loads(receipt.read_text())
                    data['guard_source_sha256' if mutation=='guard' else 'continuous_deadline_s'] = 'b'*64 if mutation=='guard' else 121
                    receipt.write_text(json.dumps(data))
                if mutation == 'consumed':
                    (prior/'run-manifest.json').write_text('{}')
                if mutation == 'qualification':
                    proof = prior/'qualification-result.json'; data = json.loads(proof.read_text())
                    data['checks'] = 901; proof.write_text(json.dumps(data))
                with self.assertRaises(ValueError): stage(manifest, root/'new')
                self.assertFalse((root/'new').exists())


if __name__ == '__main__':
    unittest.main()
