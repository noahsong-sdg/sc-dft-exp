import contextlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import compact_p_build as build
from inverse_material_run import identity
import test_portable_full_step_build as parent_fixture


class CompactPBuildTest(unittest.TestCase):
    def fixture(self,base):
        base=base.resolve();_,parent=parent_fixture.PortableFullStepBuildTests().parent(base)
        sdk=base/'Accelerate.tbd';sdk.write_bytes(b'explicit SDK fixture')
        m=build.stage(parent,base/'new',sdk);root=Path(m['cwd'])
        archive=base/'reference.a';archive.write_bytes(b'reference fixture')
        m['files'].append(identity(archive));(root/'run-manifest.json').write_text(json.dumps(m))
        lines=[f'gfortran -c {build.RESEARCH/name} -o {Path(name).stem}.o' for name in build.SOURCES]
        lines.extend([f'gfortran -o full-gap-check.x compact_p_native_pass.o {sdk} {archive}',f'gfortran -o cache-qualification.x {archive}'])
        return root,m,'\n'.join(lines)+'\n'

    def test_exact_new_source_plan_and_missing_checkpoint_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root,m,plan=self.fixture(Path(directory));pins={x['path']:x for x in m['files']}
            self.assertEqual(build.plan_check(plan,pins,m['defect_blas']),4)
            self.assertIn(str(build.RESEARCH/'compact_p_checkpoint.f90'),pins)
            self.assertIn(str(build.RESEARCH/'compact_p_native_pass.f90'),pins)
            self.assertEqual(m['command'][1],str(Path(build.__file__).resolve()))
            bad='\n'.join(x for x in plan.splitlines() if ' -c ' not in x or 'compact_p_checkpoint.f90' not in x)+'\n'
            with self.assertRaises(ValueError):build.plan_check(bad,pins,m['defect_blas'])
            with self.assertRaises(ValueError):build.plan_check(plan+plan.splitlines()[0]+'\n',pins,m['defect_blas'])

    def test_owner_freshness_console_cache_and_changed_pin_boundaries(self):
        for fault in ('none','owner','stale','console','cache','pin'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                root,m,plan=self.fixture(Path(directory))
                def make(*args,**kwargs):
                    for name in ('full-gap-check.x','cache-qualification.x'):(root/name).write_bytes(name.encode())
                    if fault=='pin':Path(m['defect_blas']).write_bytes(b'changed')
                    return SimpleNamespace(stdout=plan+('extra\n' if fault=='console' else ''),stderr='')
                def output(command,**kwargs):
                    return plan if '-n' in command else ('CACHE_QUALIFICATION_PASS checks=901\n' if fault=='cache' else 'CACHE_QUALIFICATION_PASS checks=902\n')
                if fault=='owner':
                    with self.assertRaises(ValueError):build.run(root)
                    continue
                if fault=='stale':(root/'stale.o').write_bytes(b'persisted old object')
                with contextlib.chdir(root),patch.object(build.subprocess,'check_output',side_effect=output),patch.object(build.subprocess,'run',side_effect=make),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
                    if fault=='none':self.assertFalse(build.run(root)['terminal_guard_pass'])
                    else:
                        with self.assertRaises(ValueError):build.run(root)
                        self.assertFalse((root/'compact-build-result.json').exists())
