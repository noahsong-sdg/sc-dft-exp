"""Exercise the real BLAS wrapper against independent rectangular explicit sums."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class NonlinearTileApplyTest(unittest.TestCase):
    def test_both_sides_batches_partial_tile_and_padding(self):
        compiler = shutil.which('gfortran')
        self.assertIsNotNone(compiler, 'gfortran is required')
        source = '''program test
 use iso_fortran_env, only: real64
 use nonlinear_tile_apply
 implicit none
 real(real64):: kernels(7,5,2),weights(9,2,4),result(9,2,4),expected(9,2,4)
 integer::i,j,g,k,first,last
 do g=1,2
 do i=1,5
 do j=1,7
 kernels(j,i,g)=real(100*g+10*i+j,real64)/37
 end do
 end do
 end do
 weights=-999
 do k=1,4
 do g=1,2
 do i=1,merge(5,7,g==1)
 weights(i,g,k)=real(k-2*i+3*g,real64)/13
 end do
 end do
 end do
 result=0;expected=0
 do k=1,4
 do i=1,5
 do j=1,7
 expected(i,1,k)=expected(i,1,k)+kernels(j,i,1)*weights(j,2,k)
 expected(j,2,k)=expected(j,2,k)+kernels(j,i,2)*weights(i,1,k)
 end do
 end do
 end do
 do first=1,5,2
 last=min(first+1,5)
 call apply_tile(kernels(:,first:last,:),first,5,7,weights,result)
 end do
 if(maxval(abs(result-expected))>1.e-12_real64)error stop 'Batched orientation/padding mismatch'
end program
'''
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'test.f90').write_text(source)
            module = Path(__file__).with_name('nonlinear_tile_apply.f90')
            subprocess.run([compiler, '-O2', '-fcheck=all', str(module), 'test.f90',
                            '-lblas', '-o', 'test'], cwd=root, check=True, capture_output=True)
            subprocess.run([str(root / 'test')], cwd=root, check=True, capture_output=True)


if __name__ == '__main__':
    unittest.main()
