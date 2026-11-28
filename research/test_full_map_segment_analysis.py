import array
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from fetch_public_response_inputs import digest
from full_map_segment_analysis import analyze, binary
from stage_full_map_qualification import stage
import test_full_map_checkpoint as native


class FullMapSegmentAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        native.FullMapCheckpointTests.setUpClass()
        cls.fixture = native.FullMapCheckpointTests()

    @classmethod
    def tearDownClass(cls):
        native.FullMapCheckpointTests.tearDownClass()

    def prepare(self, root):
        initial = root/'initial'
        self.fixture.control(initial, stop=32)
        self.fixture.require_pass(initial)
        fields = binary(initial/'full-map-checkpoint-state.bin', 8*142)
        source = [fields[k*142:(k+1)*142] for k in range(4)]
        geometry = root/'geometry'; geometry.mkdir()
        (geometry/'native-init.meta').write_text(
            'native-init-v1; arrays are native binary64/int32, Fortran order\n67 71 71 3 512 26 32768\n')
        with (geometry/'native-init.bin').open('wb') as out:
            array.array('d', [0.]*6).tofile(out)
            for values in (source[1], source[0], source[2], [0.]*142, [0.]*142):
                array.array('d', values).tofile(out)
            array.array('i', [1]*284).tofile(out)
        (geometry/'full-z.meta').write_text('native-Z-v1; binary64 Fortran order\n67 71 71 3 1\n1000 0 0 0 0 0 0 0\n F\n')
        with (geometry/'full-z.bin').open('wb') as out: source[3].tofile(out)
        probe = root/'probe'; probe.mkdir(); (probe/'split').mkdir()
        with (probe/'gap-seed.bin').open('wb') as out: source[0].tofile(out)
        (probe/'gap-seed.meta').write_text(
            f'gap-seed-v1; binary64 Fortran order\n67 71 71 3 10 50\n1000\n{geometry}\n'+64*'c'+'\n')
        (probe/'map-control.in').write_text(str(geometry)+'\n')
        (probe/'seed-control.in').write_text(str(probe)+'\n'+64*'c'+'\n')
        (probe/'native.in').write_text('fixture\n')
        shutil.copy2(self.fixture.executables['checkpoint'], probe/'verify-gap-seed.x')
        ancestors = {}
        for key in ('seed_manifest', 'build_manifest', 'build_qualification'):
            path = root/(key+'.json'); path.write_text('{"files": []}\n')
            ancestors[key] = dict(path=str(path), sha256=digest(path))
        recipe = dict(schema='ordered-full-map-evaluation-v1', candidate_sha256=digest(probe/'gap-seed.bin'),
                      executable_sha256=digest(probe/'verify-gap-seed.x'), operator_context_sha256='c'*64, **ancestors)
        (probe/'evaluation-context.json').write_text(json.dumps(recipe, sort_keys=True)+'\n')
        identity = digest(probe/'evaluation-context.json')
        self.fixture.control(probe, stop=64, context=identity, mode='qualify')
        command = [str(probe/'verify-gap-seed.x'), '-in', str(probe/'native.in')]
        run = subprocess.run(command, cwd=probe, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        results = probe/'results/moment'; results.mkdir(parents=True)
        (results/'console.log').write_text(run.stdout)
        guard = 'b'*64
        receipt = dict(status='PASS', exit=0, error=None, command=command, cwd=str(probe),
                       guard_source_sha256=guard, continuous_deadline_s=180, wall_s=.01,
                       max_individual_descendant_rss_bytes=100000, sampled_peak_group_rss_bytes=100000)
        (results/'receipt.json').write_text(json.dumps(receipt))
        inputs = list(geometry.iterdir())+[Path(item['path']) for item in ancestors.values()]
        inputs += [probe/name for name in ('gap-seed.bin','gap-seed.meta','map-control.in','seed-control.in',
                                           'native.in','verify-gap-seed.x','evaluation-context.json','full-map-segment.in')]
        manifest = dict(cwd=str(probe), command=command, files=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in inputs],
                        candidate_sha256=recipe['candidate_sha256'], operator_context_sha256='c'*64,
                        evaluation_context_sha256=identity, previous_directory='-', completed_rows=0, last_row=64,
                        mode='qualify', guard_seconds=180, guard_source_sha256=guard)
        path = root/'public-manifest.json'
        path.write_text(json.dumps(manifest)); (probe/'run-manifest.json').write_text(json.dumps(manifest))
        return probe, path

    def test_native_split_images_and_independent_weight_readback(self):
        with tempfile.TemporaryDirectory() as folder:
            root, manifest = self.prepare(Path(folder))
            checked = analyze(root, manifest)
            self.assertTrue(checked['microscopic_split_qualified'])
            self.assertTrue(checked['checkpoint']['state_bitwise_matches_source'])
            self.assertLess(checked['checkpoint']['independent_weights_max_absolute_difference'], 1e-14)
            self.assertFalse(checked['full_native_residual_verified'])

    def test_stale_output_state_receipt_and_manifest_are_rejected(self):
        mutations = ('image', 'state', 'weight', 'old_schema', 'diagnostics_extra', 'large_sum_error', 'marker', 'receipt',
                     'manifest', 'partial_full', 'input_bytes', 'future_row')
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as folder:
                root, manifest = self.prepare(Path(folder))
                if mutation == 'image':
                    path = root/'linear-image-checkpoint.bin'; path.write_bytes(path.read_bytes()[:-1])
                if mutation in ('state', 'weight', 'future_row'):
                    name = 'linear-image-checkpoint.bin' if mutation == 'future_row' else 'full-map-checkpoint-state.bin'
                    path = root/name; values = array.array('d'); values.frombytes(path.read_bytes())
                    values[{'state': 0, 'weight': 4*142, 'future_row': 64}[mutation]] += .01
                    path.write_bytes(values.tobytes())
                if mutation in ('old_schema', 'diagnostics_extra', 'large_sum_error'):
                    path = root/'full-map-checkpoint.meta'; lines = path.read_text().splitlines()
                    if mutation == 'old_schema': lines[0] = 'pre-migration-state-v0'
                    elif mutation == 'diagnostics_extra': lines[1] += ' 17'
                    else:
                        fields = lines[1].split(); fields[1] = '1'; lines[1] = ' '.join(fields)
                    path.write_text('\n'.join(lines)+'\n')
                if mutation == 'marker': (root/'results/moment/console.log').write_text('')
                if mutation == 'receipt':
                    path = root/'results/moment/receipt.json'; data = json.loads(path.read_text())
                    data['command'] = ['other']; path.write_text(json.dumps(data))
                if mutation == 'manifest':
                    data = json.loads(manifest.read_text()); data['last_row'] = 32; manifest.write_text(json.dumps(data))
                if mutation == 'partial_full': (root/'full-map.bin').write_bytes(b'partial')
                if mutation == 'input_bytes': (root/'native.in').write_text('changed\n')
                with self.assertRaises(ValueError): analyze(root, manifest)

    def test_staging_binds_source_parents_and_rejects_stale_build_before_writing(self):
        for stale in (False, True):
            with self.subTest(stale=stale), tempfile.TemporaryDirectory() as folder:
                base = Path(folder); seed, seed_manifest = self.prepare(base)
                build = base/'build'; (build/'results/build').mkdir(parents=True)
                exe = build/'full-gap-check.x'; shutil.copy2(seed/'verify-gap-seed.x', exe)
                command = ['python', 'source-only-build']
                parent = dict(cwd=str(build), command=command, guard_source_sha256='b'*64,
                              files=[dict(path=str(exe), bytes=exe.stat().st_size, sha256=digest(exe))])
                build_manifest = base/'build-public.json'; build_manifest.write_text(json.dumps(parent))
                (build/'run-manifest.json').write_text(json.dumps(parent))
                (build/'qualification-result.json').write_text(json.dumps(dict(
                    checks=902, all_checks_bitwise_equal=True, historical_objects_used=False,
                    full_gap_driver_linked=True, full_gap_executable_sha256=digest(exe))))
                (build/'results/build/receipt.json').write_text(json.dumps(dict(status='PASS', exit=0, error=None,
                    command=['different'] if stale else command, cwd=str(build), guard_source_sha256='b'*64)))
                destination = base/'staged'
                if stale:
                    with self.assertRaises(ValueError): stage(seed_manifest, build_manifest, destination)
                    self.assertFalse(destination.exists())
                else:
                    staged = stage(seed_manifest, build_manifest, destination)
                    self.assertEqual(staged['evaluation_context_sha256'], digest(destination/'evaluation-context.json'))
                    self.assertEqual(staged['candidate_sha256'], digest(seed/'gap-seed.bin'))
                    self.assertEqual(staged['mode'], 'qualify')


if __name__ == '__main__':
    unittest.main()
