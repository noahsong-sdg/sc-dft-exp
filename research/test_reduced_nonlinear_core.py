"""Actual reduced Newton solve checked against independent nonlinear equations."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class ReducedNonlinearCoreTest(unittest.TestCase):
    def test_nonsymmetric_exact_rank_and_zero_energy_derivative(self):
        source = '''program test
 use iso_fortran_env,only:dp=>real64
 use reduced_nonlinear_core
 implicit none
 real(dp)::q(2,2),u(2,2),x(2),c(2),d(2),r,beta,reference(2)
 real(dp)::v(2),derivative(2),plus(2),minus(2),unused(2),h
 integer::iterations,info
 q=0;q(1,1)=1;q(2,2)=1
 u=reshape([.8_dp,.3_dp,.5_dp,.8_dp],[2,2]);x=0;beta=1000;c=.002_dp
 call solve_reduced(q,u,x,beta,c,d,iterations,r,info)
 if(info/=0.or.r>1.e-13_dp.or.minval(d)<1.e-4_dp)error stop 'Nonzero reduced root failed'
 ! Independent exponential occupations, with a fully represented nonsymmetric A.
 reference=matmul(u,2/beta*(1-exp(-beta*d))/(1+exp(-beta*d)))-d
 if(maxval(abs(reference))>2.e-13_dp)error stop 'Independent full nonlinear residual mismatch'
 x=[0._dp,.001_dp];d=[0._dp,-.0003_dp];h=1.e-9_dp
 call occupation_ratio(x,d,beta,v,derivative)
 if(v(1)/=0.or.derivative(1)/=1)error stop 'Zero boundary ratio mismatch'
 call occupation_ratio(x,d+h,beta,plus,unused)
 call occupation_ratio(x,d-h,beta,minus,unused)
 if(maxval(abs((plus-minus)/(2*h)-derivative))>1.e-8_dp)error stop 'Ratio derivative mismatch'
 ! Above transition, the normal root is valid for this core; branch selection is external.
 u=0;u(1,1)=.8_dp;u(2,2)=.7_dp;c=.002_dp;x=0
 call solve_reduced(q,u,x,beta,c,d,iterations,r,info)
 if(info/=0.or.maxval(abs(d))>1.e-12_dp)error stop 'Normal root failed'
end program
'''
        compiler = shutil.which('gfortran')
        self.assertIsNotNone(compiler)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'test.f90').write_text(source)
            subprocess.run([compiler,'-O2','-fcheck=all',
                            str(Path(__file__).with_name('reduced_nonlinear_core.f90')),
                            'test.f90','-llapack','-lblas','-o','test'],cwd=root,check=True)
            subprocess.run([str(root/'test')],cwd=root,check=True,capture_output=True)


if __name__ == '__main__':
    unittest.main()
