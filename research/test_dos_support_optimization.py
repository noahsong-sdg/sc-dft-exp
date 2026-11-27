"""Check the source boundary and compiled ratio/branch output preservation.

These synthetic formulas test the relocation, not the full SCTK weight routine.
The native material eight-export comparison is a separate acceptance gate.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from dos_support_optimization import BRANCHES, RATIOS, patch


class DosSupportOptimizationTest(unittest.TestCase):
    def test_compiled_boundary_and_degenerate_energy_outputs_are_bitwise_equal(self):
        compiler=shutil.which('gfortran');self.assertIsNotNone(compiler)
        source='''SUBROUTINE calc_dosk(dosd)
 use iso_fortran_env, only: dp=>real64
 implicit none
 integer,parameter::nx=13
 real(dp),intent(out)::dosd(nx,6)
 real(dp)::e(4),a(4,4),xi0(nx),value
 integer::ii,ix,k
 xi0=[-3._dp,-2._dp,-1._dp,-.5_dp,-1.e-15_dp,0._dp,1.e-15_dp,.5_dp,1._dp,1.5_dp,2._dp,2.5_dp,3._dp]
 do k=1,6
 select case(k)
 case(1);e=[-2._dp,-1._dp,1._dp,2._dp]
 case(2);e=[-2._dp,-1._dp,-1._dp,2._dp]
 case(3);e=[-2._dp,-2._dp,1._dp,2._dp]
 case(4);e=[-2._dp,-1._dp,2._dp,2._dp]
 case(5);e=0
 case(6);e=[-1._dp,-1._dp+1.e-14_dp,1._dp,2._dp]
 end select
 do ix=1,nx
'''+RATIOS+BRANCHES[0]+''' value=a(2,1)*a(3,1)*a(4,1)/(xi0(ix)-e(1))
'''+BRANCHES[1]+''' value=(a(2,3)*a(3,1)+a(3,2)*a(2,4))/(e(4)-e(1))
'''+BRANCHES[2]+''' value=a(1,4)*a(2,4)*a(3,4)/(e(4)-xi0(ix))
 else
 value=0
 end if
 dosd(ix,k)=value
 end do
 end do
END SUBROUTINE calc_dosk
program test
 use iso_fortran_env, only: real64
 implicit none
 real(real64)::weights(13,6)
 call calc_dosk(weights)
 open(10,file='weights.bin',access='stream',form='unformatted',status='replace')
 write(10)weights
 close(10)
end program
'''
        candidate=patch(source)
        self.assertEqual(candidate.count(RATIOS),3)
        for stale in (source.replace('e(2)) THEN','e(2)) THEN_CHANGED'),candidate,
                      source.replace('a(ii,1:4) =','a(ii,1:4) = 2*')):
            with self.assertRaises(ValueError):
                patch(stale)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);outputs=[]
            for name,text in [('original',source),('candidate',candidate)]:
                path=root/(name+'.f90');path.write_text(text)
                subprocess.run([compiler,'-O2','-ffp-contract=off','-fcheck=all',
                    '-ffree-line-length-none',str(path),'-o',name],cwd=root,check=True,capture_output=True)
                subprocess.run([str(root/name)],cwd=root,check=True,capture_output=True)
                outputs.append((root/'weights.bin').read_bytes())
            self.assertEqual(outputs[0],outputs[1])


if __name__=='__main__':
    unittest.main()
