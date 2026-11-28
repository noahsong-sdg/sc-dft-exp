"""Compile the actual inverse and compare with independent full dense systems."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class LowRankInverseTest(unittest.TestCase):
    def compile_run(self, source, arguments=()):
        compiler = shutil.which('gfortran')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'test.f90').write_text(source)
            subprocess.run([compiler, '-O2', '-ffp-contract=off', '-fcheck=all',
                            str(Path(__file__).with_name('low_rank_inverse.f90')),
                            'test.f90', '-llapack', '-lblas', '-o', 'test'],
                           cwd=root, check=True, capture_output=True)
            return subprocess.run([str(root/'test'), *arguments], cwd=root,
                                  capture_output=True, text=True)

    def test_dense_nonsymmetric_inverse_and_residual_sign(self):
        result = self.compile_run('''program test
 use iso_fortran_env,only:dp=>real64
 use low_rank_inverse
 implicit none
 real(dp)::q(3,2),u(3,2),d(3),rhs(3,2),answer(3,2),small(2,2),sv(2),err
 real(dp)::a(3,3),jac(3,3),expected(3,2),direction(3),residual(3),saved_rhs(3,2)
 integer::i,j,info,pivots(3)
 q=0;q(1,1)=1;q(2,2)=1
 u=reshape([.5_dp,.3_dp,.4_dp,.2_dp,.9_dp,.6_dp],[3,2]);d=[.9_dp,.8_dp,.7_dp]
 a=matmul(u,transpose(q));jac=0
 do j=1,3
   jac(:,j)=-a(:,j)*d(j);jac(j,j)=jac(j,j)+1
 end do
 residual=[1.e-8_dp,-2.e-8_dp,3.e-8_dp];direction=[.1_dp,-.3_dp,.8_dp]
 ! Rnative=-H, Jnative*v=-J*v: Newton correction is B*Rnative.
 rhs(:,1)=residual;rhs(:,2)=matmul(jac,direction);saved_rhs=rhs
 call inverse_actions(q,u,d,rhs,answer,small,sv,err,info)
 if(info/=0.or.err>2.e-15_dp.or.minval(sv)<=0)error stop 'Inverse diagnostic failed'
 expected=rhs
 call dgesv(3,2,jac,3,pivots,expected,3,info)
 if(info/=0.or.maxval(abs(answer-expected))>2.e-14_dp)error stop 'Dense inverse disagrees'
 if(maxval(abs(answer(:,2)-direction))>2.e-14_dp)error stop 'Jacobian action sign failed'
 if(maxval(abs(matmul(a,d*answer(:,1))-answer(:,1)+residual))>1.e-20_dp) &
   error stop 'Newton correction residual sign failed'
 if(any(rhs/=saved_rhs))error stop 'Input was modified'
end program
''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unmeasured_complement_and_singular_small_system(self):
        result = self.compile_run('''program test
 use iso_fortran_env,only:dp=>real64
 use low_rank_inverse
 implicit none
 real(dp)::q(3,1),u(3,1),d(3),rhs(3,2),answer(3,2),small(1,1),sv(1),err
 real(dp)::true_jac(3,3),direction(3),epsilon
 integer::info
 q=0;q(1,1)=1;u=.5_dp*q;d=1;epsilon=1.e-12_dp
 true_jac=0;true_jac(1,1)=.5_dp;true_jac(2,2)=epsilon;true_jac(3,3)=1
 direction=[1._dp,0._dp,0._dp];rhs(:,1)=matmul(true_jac,direction)
 rhs(:,2)=[0._dp,1._dp,0._dp]
 call inverse_actions(q,u,d,rhs,answer,small,sv,err,info)
 if(info/=0.or.err>1.e-15_dp)error stop 'Complement fixture failed'
 if(maxval(abs(answer(:,1)-direction))>1.e-15_dp)error stop 'Known direction failed'
 ! A perfect probe and well-conditioned small matrix do NOT bound full J inverse.
 if(abs(sv(1)-.5_dp)>1.e-15_dp.or.answer(2,2)/=1)error stop 'Small diagnostic changed'
 if(1/epsilon<1.e11_dp)error stop 'Missing sensitive complement'
 u=q
 call inverse_actions(q,u,d,rhs,answer,small,sv,err,info)
 if(info==0)error stop 'Singular small system was accepted'
end program
''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_nonfinite_and_shape_errors_fail_before_solve(self):
        source = '''program test
 use iso_fortran_env,only:dp=>real64
 use, intrinsic :: ieee_arithmetic,only:ieee_value,ieee_quiet_nan
 use low_rank_inverse
 implicit none
 real(dp)::q(3,1),u(3,1),d(3),rhs(3,2),answer(3,2),small(1,1),sv(1),err
 integer::info
 character(10)::mode
 call get_command_argument(1,mode)
 q=0;q(1,1)=1;u=.5_dp*q;d=1;rhs=1
 if(mode=='shape')then
   call inverse_actions(q,u,d,rhs,answer(:,1:1),small,sv,err,info)
 else
   d(2)=ieee_value(0._dp,ieee_quiet_nan)
   call inverse_actions(q,u,d,rhs,answer,small,sv,err,info)
 end if
end program
'''
        for mode, message in [('shape', 'Invalid inverse dimensions'),
                              ('nan', 'Nonfinite inverse input')]:
            with self.subTest(mode=mode):
                result = self.compile_run(source, [mode])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)


if __name__ == '__main__':
    unittest.main()
