import array
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import test_streamed_defect_core as dense_fixture


class CompactPCheckpointTest(unittest.TestCase):
    def compile(self,base):
        research=Path(__file__).resolve().parent
        subprocess.run([shutil.which('gfortran'),'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',
                        *(str(research/name) for name in ('streamed_defect_core.f90','compact_p_checkpoint.f90','compact_p_checkpoint_fixture.f90')),
                        '-lblas','-o','fixture.x'],cwd=base,check=True,capture_output=True)

    def run_fixture(self,base,root,mode):
        return subprocess.run([str(base/'fixture.x'),mode],cwd=root,capture_output=True,text=True)

    def test_ordered_restart_final_partial_tile_and_dense_P(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);self.compile(base);root=base/'run';(root/'complete').mkdir(parents=True)
            done=self.run_fixture(base,root,'normal');self.assertEqual(done.returncode,0,done.stderr)
            self.assertEqual((root/'echo.bin').read_bytes(),(root/'complete/compact-p.bin').read_bytes())
            self.assertEqual((root/'echo.bin').read_bytes(),(root/'continuous.bin').read_bytes())
            with (root/'echo.bin').open('rb') as f:actual=array.array('d');actual.fromfile(f,222)
            for a,b in zip(actual,dense_fixture.oracle()[:222]):self.assertLessEqual(abs(a-b),1e-13*(1+abs(b)))
            self.assertEqual((root/'compact-p.meta').read_text().splitlines()[2].strip(),'32')
            self.assertEqual((root/'complete/compact-p.meta').read_text().splitlines()[2].strip(),'35')
            done=self.run_fixture(base,root,'write');self.assertNotEqual(done.returncode,0)

    def test_writer_domain_boundaries(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);self.compile(base)
            for mode in ('write-unvisited','write-nonfinite','write-split','write-negative-time'):
                with self.subTest(mode=mode):
                    root=base/mode;root.mkdir();done=self.run_fixture(base,root,mode)
                    self.assertNotEqual(done.returncode,0);self.assertFalse((root/'compact-p.meta').exists())
                    self.assertFalse((root/'compact-p.bin').exists())

    def test_stale_persisted_context_shape_coverage_and_values(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);self.compile(base);good=base/'good';good.mkdir()
            done=self.run_fixture(base,good,'write');self.assertEqual(done.returncode,0,done.stderr)
            for fault in ('identity','coverage','schema','dimensions','extra','slash','null','trailing','long','shape','nan','unvisited','time'):
                with self.subTest(fault=fault):
                    root=base/fault;root.mkdir()
                    for name in ('compact-p.meta','compact-p.bin'):shutil.copy2(good/name,root/name)
                    meta=root/'compact-p.meta';lines=meta.read_text().splitlines()
                    if fault=='schema':lines[0]='old-P-format'
                    if fault=='dimensions':lines[1]='35 38 3'
                    if fault=='extra':lines[1]+=' extra'
                    if fault=='slash':lines[1]='35 39 /'
                    if fault=='null':lines[1]='3*'
                    if fault=='trailing':lines.append('extra')
                    if fault=='long':lines[3]+=' '*256+'extra'
                    if fault=='time':lines[4]='NaN .125'
                    meta.write_text('\n'.join(lines)+'\n')
                    if fault=='shape':(root/'compact-p.bin').write_bytes(b'stale')
                    if fault in ('nan','unvisited'):
                        with (root/'compact-p.bin').open('r+b') as f:
                            f.seek(8*(32*3 if fault=='unvisited' else 0));array.array('d',[float('nan') if fault=='nan' else 1.]).tofile(f)
                    done=self.run_fixture(base,root,fault if fault in ('identity','coverage') else 'read')
                    self.assertNotEqual(done.returncode,0);self.assertFalse((root/'echo.bin').exists())
