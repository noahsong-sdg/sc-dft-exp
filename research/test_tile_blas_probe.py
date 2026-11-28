"""Compile actual BLAS calls, exact signed products, stale and transpose boundaries."""
import array
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys
import unittest

from tile_blas_analysis import analyze,dot_check


class TileBlasProbeTest(unittest.TestCase):
    def fixture(self,root):
        compiler=shutil.which('gfortran');self.assertIsNotNone(compiler)
        source=Path(__file__).with_name('tile_blas_probe.f90')
        subprocess.run([compiler,'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',str(source),'-lblas','-o','probe.x'],cwd=root,check=True,capture_output=True)
        return subprocess.run([str(root/'probe.x'),'reference','fixture'],cwd=root,check=True,capture_output=True)

    def test_native_transpose_layout_exact_control_and_fresh_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root);result=analyze(root,'reference','fixture')
            self.assertEqual(result['signed_controls']['entries_checked'],80)
            self.assertEqual(result['benchmark_samples_checked'],18)
            self.assertFalse(result['conditioned_gap_error_bounded'])
            self.assertFalse(result['physical_response_verified'])
            self.assertEqual(len(result['timings']),2)
            self.assertTrue(all(x['repetitions']==128 and x['wall_s']>0 for x in result['timings']))
            for k in range(8):
                cwd=root/str(k);cwd.mkdir()
                subprocess.run([str(root/'probe.x'),'reference','fixture'],cwd=cwd,check=True,capture_output=True)
                analyze(cwd,'reference','fixture')
            again=subprocess.run([str(root/'probe.x'),'reference','fixture'],cwd=root,capture_output=True)
            self.assertNotEqual(again.returncode,0)
            invalid=subprocess.run([str(root/'probe.x'),'other','fixture'],cwd=root,capture_output=True)
            self.assertNotEqual(invalid.returncode,0)

    def test_stale_shape_summary_nonfinite_and_transposed_product_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.fixture(root)
            paths=[root/f'reference-{name}' for name in ('summary.txt','controls.bin','samples.bin')]
            saved=[path.read_bytes() for path in paths]
            for mutation in ('summary','shape','nonfinite','control','sample'):
                with self.subTest(mutation=mutation):
                    for path,content in zip(paths,saved):path.write_bytes(content)
                    if mutation=='summary':paths[0].write_text(paths[0].read_text().replace('fixture','benchmark'))
                    if mutation=='shape':paths[2].write_bytes(saved[2][:-8])
                    if mutation in ('nonfinite','control','sample'):
                        path=paths[2] if mutation=='sample' else paths[1];values=array.array('d');values.frombytes(path.read_bytes())
                        values[0]=float('nan') if mutation=='nonfinite' else values[0]+.1
                        path.write_bytes(values.tobytes())
                    with self.assertRaises(ValueError):analyze(root,'reference','fixture')
            with self.assertRaises(ValueError):dot_check(0.,[1.,-2.],[3.,4.])

    @unittest.skipUnless(sys.platform=='darwin','Mac system framework binding')
    def test_actual_framework_stub_link_and_signed_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);sdk=subprocess.check_output(['xcrun','--show-sdk-path'],text=True).strip()
            stub=Path(sdk)/'System/Library/Frameworks/Accelerate.framework/Accelerate.tbd'
            subprocess.run([shutil.which('gfortran'),'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',
                            str(Path(__file__).with_name('tile_blas_probe.f90')),str(stub),'-o','probe.x'],cwd=root,check=True,capture_output=True)
            subprocess.run([str(root/'probe.x'),'accelerate','fixture'],cwd=root,check=True,capture_output=True)
            result=analyze(root,'accelerate','fixture')
            self.assertEqual(result['signed_controls']['entries_checked'],80)
            bindings=subprocess.check_output(['otool','-L',str(root/'probe.x')],text=True)
            self.assertIn('Accelerate.framework',bindings)
