import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import compact_tile_build as build
from inverse_material_run import identity
import test_portable_full_step_build as parent_fixture


class CompactTileBuildTest(unittest.TestCase):
    def staged(self,base):
        base=base.resolve()
        _,parent=parent_fixture.PortableFullStepBuildTests().parent(base)
        sdk=base/'Accelerate.tbd';sdk.write_bytes(b'explicit fixture SDK stub')
        m=build.stage(parent,base/'new',sdk);root=Path(m['cwd'])
        archive=base/'reference.a';archive.write_bytes(b'fixture reference')
        m['files'].append(identity(archive));(root/'run-manifest.json').write_text(json.dumps(m))
        lines=[f'gfortran -c {build.RESEARCH/name} -o {Path(name).stem}.o' for name in build.SOURCES]
        lines.extend([f'gfortran -o full-gap-check.x compact_native_tile_probe.o {sdk} {archive}',f'gfortran -o cache-qualification.x {archive}'])
        return root,m,'\n'.join(lines)+'\n'

    def test_source_sdk_owner_and_freshness_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            root,m,plan=self.staged(Path(directory));pins={x['path']:x for x in m['files']}
            self.assertEqual(build.plan_check(plan,pins,m['defect_blas']),3)
            self.assertEqual(m['guard_seconds'],60)
            self.assertEqual(m['command'][1],str(Path(build.__file__).resolve()))
            for source in build.SOURCES:self.assertIn(str(build.RESEARCH/source),pins)
            self.assertIn(m['defect_blas'],pins)
            with self.assertRaises(ValueError):build.run(root)
            with contextlib.chdir(root):
                (root/'stale.o').write_bytes(b'preexisting object')
                with self.assertRaises(ValueError):build.run(root)

    def test_plan_rejects_omitted_duplicate_foreign_and_late_sdk(self):
        with tempfile.TemporaryDirectory() as directory:
            root,m,plan=self.staged(Path(directory));pins={x['path']:x for x in m['files']}
            archive=str(root.parent/'reference.a');sdk=m['defect_blas']
            for changed in (plan.replace(plan.splitlines()[0]+'\n',''),plan+plan.splitlines()[0]+'\n',
                            plan.replace('compact_defect_io.o','/foreign.o'),plan.replace(sdk+' '+archive,archive+' '+sdk),
                            plan.replace(sdk+' ',''),plan+'echo hidden command\n',plan.replace(archive,'/unbound.a')):
                with self.subTest(plan=changed),self.assertRaises((ValueError,OSError)):build.plan_check(changed,pins,sdk)

    def test_run_console_cache_and_final_pins(self):
        for fault in ('none','console','cache','pins'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                root,m,plan=self.staged(Path(directory))
                def make(*args,**kwargs):
                    for name in ('full-gap-check.x','cache-qualification.x'):(root/name).write_bytes(name.encode())
                    if fault=='pins':Path(m['defect_blas']).write_bytes(b'changed')
                    return SimpleNamespace(stdout=plan+('extra\n' if fault=='console' else ''),stderr='')
                def output(command,**kwargs):
                    return plan if '-n' in command else ('CACHE_QUALIFICATION_PASS checks=901\n' if fault=='cache' else 'CACHE_QUALIFICATION_PASS checks=902\n')
                with contextlib.chdir(root),patch.object(build.subprocess,'check_output',side_effect=output),patch.object(build.subprocess,'run',side_effect=make),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                    if fault=='none':
                        result=build.run(root);self.assertFalse(result['terminal_guard_pass']);self.assertEqual(result['cache_checks'],902)
                        self.assertIn('full-gap-check.x',result['outputs'])
                    else:
                        with self.assertRaises(ValueError):build.run(root)
                        self.assertFalse((root/'compact-build-result.json').exists())
