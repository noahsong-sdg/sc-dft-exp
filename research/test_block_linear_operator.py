"""Exercise the actual linear block routine on a tiny known asymmetric kernel."""
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


STUBS = '''module kinds
use iso_fortran_env,only:dp=>real64
end module
module mp_world
integer::nproc=1
end module
module sctk_val
use kinds
integer,parameter::ngapmax=3
integer::ngap(2)=[3,2]
real(dp)::beta=2,xi(3,2),dk(3,2),Z(3,2),dxq(3,2)=0,xic=-1
logical::zero_kelvin=.false.
end module
module slab_operator
contains
subroutine clear_slab()
end subroutine
end module
module tiled_operator
use kinds
use sctk_val,only:ngap
contains
subroutine build_tile(first,last,block,slab_width)
integer,intent(in)::first,last,slab_width
real(dp),intent(out)::block(ngap(2),first:last,2)
integer::i,j
do i=first,last
 do j=1,ngap(2)
  block(j,i,1)=i+2*j
  block(j,i,2)=3*i-j
 end do
end do
end subroutine
end module
subroutine dgemv(trans,m,n,alpha,a,lda,x,incx,beta,y,incy)
use kinds
character,intent(in)::trans
integer,intent(in)::m,n,lda,incx,incy
real(dp),intent(in)::alpha,beta,a(lda,*),x(*)
real(dp),intent(inout)::y(*)
integer::i,j
if(trans=='T')then
 do j=1,n
  y(j)=beta*y(j)+alpha*sum(a(1:m,j)*x(1:m))
 end do
else
 do i=1,m
  y(i)=beta*y(i)+alpha*sum(a(i,1:n)*x(1:n))
 end do
end if
end subroutine
'''
PROGRAM = '''program fixture
use kinds
use sctk_val
use block_linear_operator
implicit none
real(dp)::vectors(3,2,1),images(3,2,1)
character(20)::mode
call get_command_argument(1,mode)
xi=reshape([0._dp,1._dp,2._dp,0._dp,1._dp,0._dp],[3,2])
dk=reshape([1._dp,2._dp,3._dp,4._dp,5._dp,0._dp],[3,2])
Z=reshape([.1_dp,.2_dp,.3_dp,.4_dp,.5_dp,0._dp],[3,2])
vectors(:,:,1)=reshape([1._dp,2._dp,3._dp,4._dp,5._dp,0._dp],[3,2])
if(mode=='padding')vectors(3,2,1)=1
call apply_linear_block(vectors,images,1,2,1)
print '(6es26.17e3)',images
end program
'''


class BlockLinearOperatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler=shutil.which('gfortran')
        if compiler is None:
            raise RuntimeError('Linear block verification requires gfortran')
        cls.workspace=tempfile.TemporaryDirectory();cls.root=Path(cls.workspace.name)
        (cls.root/'stubs.f90').write_text(STUBS)
        (cls.root/'fixture.f90').write_text(PROGRAM)
        source=Path(__file__).parent/'portable_gap/block_linear_operator.f90'
        subprocess.run([compiler,'-O0','-fcheck=all','-ffree-line-length-none','stubs.f90',
            str(source),'fixture.f90','-o','fixture'],cwd=cls.root,check=True,capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def test_zero_energy_limit_both_orientations_and_renormalization(self):
        result=subprocess.run(['./fixture'],cwd=self.root,check=True,capture_output=True,text=True)
        actual=list(map(float,result.stdout.split()))
        # Independent scalar evaluation; the zero-energy weight is beta*dk/4.
        left=[.5,math.tanh(1)*2,3*math.tanh(2)/4*3]
        right=[2*4,2.5*math.tanh(1)*5]
        expected=[-sum((i+2*j)*right[j-1] for j in (1,2))/(1+.1*i) for i in (1,2,3)]
        expected += [-sum((3*i-j)*left[i-1] for i in (1,2,3))/(1+[.4,.5][j-1]) for j in (1,2)]
        expected += [0.0]
        for a,e in zip(actual,expected):
            self.assertAlmostEqual(a,e,delta=1e-12)
        self.assertEqual(len(actual),6)

    def test_nonzero_padding_rejected(self):
        result=subprocess.run(['./fixture','padding'],cwd=self.root,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Nonzero trial block padding',result.stderr)
