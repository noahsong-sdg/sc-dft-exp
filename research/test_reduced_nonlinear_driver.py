import math
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

from reduced_nonlinear_analysis import analyze


class ReducedNonlinearDriverTest(unittest.TestCase):
    def test_file_bound_nonsymmetric_solution_and_stale_inputs(self):
        compiler = shutil.which('gfortran')
        self.assertIsNotNone(compiler)
        research = Path(__file__).parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'stubs.f90').write_text('module kinds\n use iso_fortran_env,only:dp=>real64\n'
                'end module\nmodule constants\n use kinds\n'
                'real(dp),parameter::RYTOEV=13.605693122994_dp\nend module\n')
            subprocess.run([compiler,'-O2','-fcheck=all','-ffree-line-length-none','stubs.f90',
                            str(research/'reduced_nonlinear_core.f90'),
                            str(research/'reduced_nonlinear_driver.f90'),'-llapack','-lblas','-o','test'],
                           cwd=root,check=True)
            basis, prepare, mode = [root/n for n in ('basis','prepare','mode')]
            for p in (basis,prepare,mode):
                p.mkdir()
            meta = 'tc-basis-v1\n2 2\n1000\n'+'a'*64+'\n2 10 10 2 1 1\n'
            for p in (basis,mode):
                (p/'basis.meta').write_text(meta)
            payload = struct.pack('<8d',1,0,0,1,.8,.3,.5,.8)
            (basis/'basis.bin').write_bytes(payload)
            eigenvalue = .8+math.sqrt(.15)
            v = [1/math.sqrt(1.6), math.sqrt(.6)/math.sqrt(1.6)]
            (mode/'selected.meta').write_text(f'1 2\n{eigenvalue:.17g} 0\n')
            (mode/'selected.bin').write_bytes(struct.pack('<4d',*v,0,0))
            (prepare/'native-init.meta').write_text(
                'native-init-v1; arrays are native binary64/int32, Fortran order\n'
                '1 1 1 2 1 1 1\n1 1e-7 1e-8 1 1 1 1\nT\n')
            reals = [-1,1,.5,.5]+[0]*4+[.001,.001]+[0]*4
            (prepare/'native-init.bin').write_bytes(struct.pack('<14d4i',*reals,1,1,1,1))
            control = f'{basis}\n{prepare}\n{mode}\n'+'a'*64+'\n1000 20\n'
            (root/'reduced-control.in').write_text(control)
            subprocess.run([str(root/'test')],cwd=root,check=True,capture_output=True)
            d = struct.unpack('<2d',(root/'reduced-gap.bin').read_bytes())
            occupations = [2/1000*(1-math.exp(-1000*x))/(1+math.exp(-1000*x)) for x in d]
            r = [.8*occupations[0]+.5*occupations[1]-d[0],
                 .3*occupations[0]+.8*occupations[1]-d[1]]
            self.assertLess(max(map(abs,r)),2e-13)
            self.assertGreater(min(d),1e-4)
            self.assertFalse(analyze(root,prepare)['full_native_residual_verified'])
            saved_gap=(root/'reduced-gap.bin').read_bytes()
            for bad in (saved_gap[:-1], struct.pack('<2d',math.nan,d[1])):
                (root/'reduced-gap.bin').write_bytes(bad)
                with self.assertRaises(ValueError):
                    analyze(root,prepare)
            (root/'reduced-gap.bin').write_bytes(saved_gap)
            stale = root/'stale';stale.mkdir()
            (stale/'reduced-control.in').write_text(control)
            (basis/'basis.bin').write_bytes(payload[:-1])
            result = subprocess.run([str(root/'test')],cwd=stale,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Stale reduced basis payload',result.stderr)
            (basis/'basis.bin').write_bytes(payload)
            (basis/'basis.meta').write_text(meta.replace('a'*64,'b'*64))
            result = subprocess.run([str(root/'test')],cwd=stale,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('Stale reduced basis context',result.stderr)


if __name__ == '__main__':
    unittest.main()
