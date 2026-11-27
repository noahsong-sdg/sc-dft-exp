"""Exercise the real amplitude module with an analytic rank-one kernel."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from mode_amplitude_analysis import analyze


class ModeAmplitudeProbeTest(unittest.TestCase):
    def test_fresh_mode_and_nonlinear_amplitudes_and_stale_context(self):
        stubs = '''module kinds
 use iso_fortran_env,only:dp=>real64
end module
module constants
 use kinds
 real(dp),parameter::RYTOEV=13.605693122994_dp
end module
module sctk_val
 use kinds
 integer::ngap(2)=[35,37],ngapmax=37,nx=100,nmf=10,nci=10,scdft_kernel=2
 real(dp)::beta=1000,emin=1.e-7_dp,xi(37,2)=0,dk(37,2)=0,Z(37,2)=0
end module
module slab_operator
contains
 subroutine clear_slab()
 end subroutine
end module
module tiled_operator
 use kinds
contains
 subroutine build_tile(first,last,block,width)
 integer,intent(in)::first,last,width
 real(dp),intent(out)::block(37,first:last,2)
 block(:,:,1)=-1.1_dp/(37*.25_dp)
 block(:,:,2)=-1.1_dp/(35*.25_dp)
 end subroutine
end module
'''
        main = '''program test
 use kinds
 use constants
 use sctk_val
 use mode_amplitude_probe
 implicit none
 real(dp)::v(37,2),r(37,2),numbers(7),a,s,p,mx,rms,f(2),expected,d,e,t
 integer::u,k,g
 character(256)::header
 dk(1:35,1)=.001_dp;dk(:,2)=.001_dp
 v=0;v(1:35,1)=1/sqrt(72._dp);v(:,2)=1/sqrt(72._dp);r=0
 open(newunit=u,file='selected.bin',access='stream',form='unformatted',status='new')
 write(u)v,r
 close(u)
 call run_mode_amplitudes()
 open(newunit=u,file='mode-amplitudes.txt',status='old')
 read(u,'(a)')header
 read(u,*)g,k
 read(u,*)numbers(1:6)
 do k=1,7
 read(u,*)a,s,p,mx,rms,f
 d=a/(1000*RYTOEV);e=beta*d/2;t=tanh(e)/e
 expected=d*(1.1_dp*t-1)
 if(abs(p-expected*sqrt(72._dp))>1.e-15_dp)error stop 'Projected amplitude oracle mismatch'
 if(abs(mx-abs(expected))>1.e-15_dp.or.abs(rms-abs(expected))>1.e-15_dp) &
 error stop 'Full amplitude residual oracle mismatch'
 if(any(abs(f-expected)>1.e-15_dp))error stop 'Fermi residual oracle mismatch'
 end do
 close(u)
end program
'''
        compiler = shutil.which('gfortran')
        self.assertIsNotNone(compiler)
        research = Path(__file__).parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'stubs.f90').write_text(stubs)
            (root/'main.f90').write_text(main)
            (root/'mode-control.in').write_text('.\n'+'a'*64+'\n')
            basis = 'tc-basis-v1\n74 1\n1000\n'+'a'*64+'\n100 10 10 2 35 37\n'
            (root/'basis.meta').write_text(basis)
            (root/'selected.meta').write_text('1 1\n1.1 0\n')
            subprocess.run([compiler, '-O2', '-fcheck=all', 'stubs.f90',
                            str(research/'nonlinear_tile_apply.f90'),
                            str(research/'mode_amplitude_probe.f90'), 'main.f90',
                            '-lblas', '-o', 'test'], cwd=root, check=True)
            subprocess.run([str(root/'test')], cwd=root, check=True, capture_output=True)
            self.assertEqual(len(analyze(root)['rows']), 7)
            # Run again in a fresh directory: stale context must fail before application.
            stale = root/'stale'; stale.mkdir()
            for name in ('mode-control.in','selected.meta'):
                shutil.copy2(root/name, stale/name)
            (stale/'basis.meta').write_text(basis.replace('a'*64, 'b'*64))
            result = subprocess.run([str(root/'test')], cwd=stale, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Stale declared mode operator context', result.stderr)


if __name__ == '__main__':
    unittest.main()
