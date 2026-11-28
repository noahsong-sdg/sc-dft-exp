"""Fresh stage/owning source-build boundaries; native arithmetic tested separately."""
from contextlib import chdir
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import tile_blas_run as runner
from inverse_material_run import identity
from fetch_public_response_inputs import digest


def write(path,value):path.write_text(json.dumps(value));return path


class TileBlasRunTest(unittest.TestCase):
    def fixture(self,base):
        base=base.resolve();prior=base/'prior';(prior/'results/build').mkdir(parents=True)
        source=base/'source';source.write_text('frozen');archive=base/'libblas.a';archive.write_text('reference')
        stub=base/'Accelerate.tbd';stub.write_text('framework');system=base/'SystemVersion.plist';system.write_text('version')
        tool=base/'otool';tool.write_text('tool')
        self.addCleanup(patch.stopall)
        patch.object(runner,'SYSTEM_VERSION',system).start();patch.object(runner,'OTOOL',tool).start()
        parent=dict(cwd=str(prior),files=[identity(source),identity(archive)],compiler=sys.executable,
                    link_archives=[str(archive)],command=['baseline'],guard_seconds=120,guard_source_sha256='guard')
        mp=write(base/'baseline.json',parent);(prior/'run-manifest.json').write_bytes(mp.read_bytes())
        receipt=dict(status='PASS',exit=0,error=None,command=['baseline'],cwd=str(prior),continuous_deadline_s=120,
                     wall_s=1.,guard_source_sha256='guard')
        write(prior/'results/build/receipt.json',receipt)
        rp=write(base/'result.json',dict(status='PASS',inputs_unchanged=True,historical_custom_objects_used=False,
                                      manifest_sha256=digest(mp),receipt=receipt))
        root=base/'run';m=runner.stage(mp,rp,stub,root)
        return root,m,source

    def test_fresh_stage_closure_and_failed_source_build(self):
        for mutation in ('none','stale','receipt','closure','library'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                root,m,source=self.fixture(Path(directory))
                if mutation=='stale':source.write_text('changed')
                if mutation=='receipt':
                    rp=Path(m['baseline_result']);result=json.loads(rp.read_text());result['receipt']['status']='FAIL';write(rp,result)
                    m['files']=[identity(x['path']) for x in m['files']]
                if mutation=='closure':m['files']=[x for x in m['files'] if x['path']!=str(source)]
                if mutation=='library':m['reference_archive']=str(source)
                if mutation=='none':self.assertTrue(runner.validate(m))
                else:
                    with self.assertRaises(ValueError):runner.validate(m)
                with self.assertRaisesRegex(ValueError,'Fresh'):runner.stage(m['baseline_manifest'],m['baseline_result'],m['framework_stub'],root)

    def test_owned_build_commands_and_withheld_terminal(self):
        with tempfile.TemporaryDirectory() as directory:
            root,m,_=self.fixture(Path(directory))
            def command(argv,**kwargs):
                if '-o' in argv:(root/argv[-1]).write_text('fresh executable')
                else:
                    for suffix in ('summary.txt','controls.bin','samples.bin'):(root/f'{argv[1]}-{suffix}').write_text('fixture')
            with chdir(root),patch.object(sys,'platform','darwin'),patch.object(runner.subprocess,'run',side_effect=command), \
                 patch.object(runner.subprocess,'check_output',return_value='linked framework'),patch.object(runner,'analyze',return_value={'scope':'fixture'}):
                result=runner.run(root)
                self.assertFalse(result['terminal_guard_pass']);self.assertFalse(result['conditioned_gap_error_bounded'])
                self.assertIn(m['reference_archive'],result['build_commands'][0])
                self.assertEqual(result['build_commands'][1][-3],m['framework_stub'])
                with self.assertRaisesRegex(ValueError,'Fresh'):runner.run(root)

    def test_changed_command_and_final_source_rejected(self):
        for mutation in ('command','final'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                root,m,source=self.fixture(Path(directory))
                if mutation=='command':m['command']=['other'];write(root/'run-manifest.json',m)
                def command(argv,**kwargs):
                    if '-o' in argv:(root/argv[-1]).write_text('fresh')
                    else:
                        for suffix in ('summary.txt','controls.bin','samples.bin'):(root/f'{argv[1]}-{suffix}').write_text('fixture')
                    source.write_text('changed')
                with chdir(root),patch.object(sys,'platform','darwin'),patch.object(runner.subprocess,'run',side_effect=command), \
                     patch.object(runner.subprocess,'check_output',return_value='linked'),patch.object(runner,'analyze',return_value={}):
                    with self.assertRaises(ValueError):runner.run(root)
                self.assertFalse((root/'tile-readback.json').exists())
