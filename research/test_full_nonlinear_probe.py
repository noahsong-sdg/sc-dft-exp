"""Run the full owning map/derivative routine on a rectangular independent oracle."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class FullNonlinearProbeTest(unittest.TestCase):
    def test_full_batched_residual_and_jacobian_with_zero_and_padding(self):
        source = '''module kinds
 use iso_fortran_env,only:dp=>real64
end module
module sctk_val
 use kinds
 integer::ngap(2)=[35,37],ngapmax=40
 real(dp)::delta(40,2),xi(40,2),dk(40,2),beta=1000, Z(40,2)
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
 integer::i,j,g
 do g=1,2
 do i=first,last
 do j=1,37
 block(j,i,g)=real(100*g+3*i-2*j,dp)/97
 end do
 end do
 end do
 end subroutine
end module
'''
        main = '''program test
 use kinds
 use sctk_val
 use full_nonlinear_probe
 implicit none
 real(dp)::chi(40,2),expected(40,2),saved(40,2),res(40,2),v(40,2),jac(40,2)
 real(dp)::energy,thermal,pair
 integer::i,j,g,u
 delta=0;xi=0;dk=0;Z=0;chi=0;expected=0
 do g=1,2
 do i=1,ngap(g)
 xi(i,g)=real(i-17,dp)*.001_dp
 delta(i,g)=.0001_dp
 if(i==17)delta(i,g)=0
 dk(i,g)=real(i-5,dp)/1000
 Z(i,g)=.5_dp+real(i,dp)/100
 energy=hypot(xi(i,g),delta(i,g))
 if(energy>0)then
 thermal=(1-exp(-beta*energy))/(1+exp(-beta*energy))
 chi(i,g)=dk(i,g)*delta(i,g)/2/energy*thermal
 end if
 end do
 end do
 do i=1,ngap(1)
 do j=1,ngap(2)
 expected(i,1)=expected(i,1)+real(100+3*i-2*j,dp)/97*chi(j,2)
 expected(j,2)=expected(j,2)+real(200+3*i-2*j,dp)/97*chi(i,1)
 end do
 end do
 do g=1,2
 expected(:,g)=-expected(:,g)/(1+Z(:,g))-delta(:,g)
 end do
 call run_full_map(chi)
 open(newunit=u,file='full-map.bin',access='stream',form='unformatted',status='old')
 read(u)saved,res,v,jac
 close(u)
 if(maxval(abs(saved-delta))>0)error stop 'Seed changed'
 if(maxval(abs(res-expected))>1.e-15_dp)error stop 'Full residual oracle mismatch'
 if(any(res(38:40,:)/=0).or.any(jac(38:40,:)/=0))error stop 'Padding changed'
end program
'''
        compiler = shutil.which('gfortran')
        self.assertIsNotNone(compiler, 'gfortran is required')
        research = Path(__file__).parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'stubs.f90').write_text(source)
            (root / 'main.f90').write_text(main)
            subprocess.run([compiler, '-O2', '-fcheck=all', 'stubs.f90',
                            str(research / 'nonlinear_tile_apply.f90'),
                            str(research / 'full_nonlinear_probe.f90'), 'main.f90',
                            '-lblas', '-o', 'test'], cwd=root, check=True, capture_output=True)
            subprocess.run([str(root / 'test')], cwd=root, check=True, capture_output=True)
            lines = (root / 'full-map.txt').read_text().splitlines()
            self.assertEqual(len(lines), 5)
            self.assertIn('NOT a converged gap', lines[0])


if __name__ == '__main__':
    unittest.main()
