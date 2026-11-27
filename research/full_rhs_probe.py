"""Full pinned RHS fixture: real BLAS, serial MPI/clock stubs, synthetic inputs."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.request import urlopen
from rhs_thermal_probe import URL, SHA256, extract

STUBS = """
module kinds
 use iso_fortran_env, only: dp=>real64
end module
module io_global
 use iso_fortran_env, only: stdout=>output_unit
end module
module mp_world
 integer :: world_comm=0
end module
module mp
 use kinds
contains
 subroutine mp_sum(array,comm)
 real(dp), intent(inout) :: array(:,:)
 integer :: comm
 end subroutine
end module
module constants
 use kinds
 real(dp), parameter :: RYTOEV=13.605693122994_dp
end module
module sctk_val
 use kinds
 integer, parameter :: ngapmax=3
 integer :: ngap(2)=[2,3]
 real(dp) :: beta=100, xic=-1, dk(3,2), effint(3,3,2), xi(3,2), Z(3,2), dxq(3,2)
 logical :: zero_kelvin=.false.
end module
subroutine divide(comm,n,first,last)
 integer :: comm,n,first,last
 first=1; last=n
end subroutine
subroutine start_clock(name)
 character(*) :: name
end subroutine
subroutine stop_clock(name)
 character(*) :: name
end subroutine
program probe
 use kinds
 use sctk_val
 implicit none
 real(dp) :: delta(3,2), res(3,2)
 integer :: grid, state
 interface
 subroutine gapeq_rhs(delta,res)
 use sctk_val, only: ngapmax
 use kinds
 real(dp), intent(in) :: delta(ngapmax,2)
 real(dp), intent(out) :: res(ngapmax,2)
 end subroutine
 end interface
 xi(:,1)=[0._dp,.4_dp,0._dp]; xi(:,2)=[0._dp,-.3_dp,1._dp]
 delta=2; delta(3,1)=0
 dxq=2; dk(:,1)=[1._dp,.7_dp,0._dp]; dk(:,2)=[.8_dp,.6_dp,.4_dp]
 Z(:,1)=[.2_dp,.4_dp,0._dp]; Z(:,2)=[.1_dp,.3_dp,.5_dp]
 effint=0
 effint(:,1,1)=[-2._dp,.3_dp,.4_dp]
 effint(:,2,1)=[.2_dp,-1._dp,.7_dp]
 effint(:,1,2)=[-1.5_dp,.1_dp,.2_dp]
 effint(:,2,2)=[.4_dp,-.8_dp,.3_dp]
 call gapeq_rhs(delta,res)
 do grid=1,2
 do state=1,ngap(grid)
 write(*,'(es25.16)') res(state,grid)
 end do
 end do
end program
"""


def corrected(routine):
    start_text = '        IF(1.0_dp - tanhd * tanhe < 1.0e-10_dp) THEN'
    end_text = '\n        ELSE\n          chi(igap,ii) = '
    if routine.count(start_text) != 1:
        raise ValueError('RHS saturation boundary changed')
    start = routine.index(start_text)+len(start_text)
    if routine[start:].count(end_text) != 1:
        raise ValueError('Finite-temperature RHS branch changed')
    end = routine.index(end_text,start)
    energy='SQRT(xi(igap,ii)**2 + delta(igap,ii)**2)'
    value = ('\n          chi(igap,ii) = 0.5_dp * ( &\n'
             '          TANH(0.5_dp*beta*(%s + ABS(dxq(igap,ii)))) + &\n'
             '          TANH(0.5_dp*beta*(%s - ABS(dxq(igap,ii)))))\n') % (energy,energy)
    return routine[:start]+value+routine[end:]


def expected():
    x=((0.,.4),(0.,-.3,1.))
    weights=((1.,.7),(.8,.6,.4))
    z=((.2,.4),(.1,.3,.5))
    matrices=(((-2.,.2),(.3,-1.),(.4,.7)),
              ((-1.5,.4),(.1,-.8),(.2,.3)))
    chi=[]
    for values,dk in zip(x,weights):
        terms=[]
        for xi,weight in zip(values,dk):
            energy=math.hypot(xi,2.)
            thermal=.5*(math.tanh(50*(energy+2))+math.tanh(50*(energy-2)))
            terms.append(weight*thermal/energy)
        chi.append(terms)
    first=[-math.fsum(matrices[0][j][i]*chi[1][j] for j in range(3))/(1+z[0][i])-2
           for i in range(2)]
    second=[-math.fsum(matrices[1][j][i]*chi[0][i] for i in range(2))/(1+z[1][j])-2
            for j in range(3)]
    return first+second


def zero_energy_correction(routine):
    """Apply the finite-temperature zero limit of delta/E times occupation."""
    original='''    chi(1:ngap(ii),ii) = 0.5_dp * dk(1:ngap(ii),ii) * delta(1:ngap(ii),ii) * chi(1:ngap(ii),ii) &
    &                  / SQRT(xi(1:ngap(ii),ii)**2 + delta(1:ngap(ii),ii)**2)'''
    replacement='''    DO igap = 1, ngap(ii)
      IF(.NOT. zero_kelvin .AND. xi(igap,ii) == 0.0_dp .AND. delta(igap,ii) == 0.0_dp) THEN
        chi(igap,ii) = 0.0_dp
      ELSE
        chi(igap,ii) = 0.5_dp * dk(igap,ii) * delta(igap,ii) * chi(igap,ii) &
        &             / SQRT(xi(igap,ii)**2 + delta(igap,ii)**2)
      END IF
    END DO'''
    if routine.count(original)!=1:
        raise ValueError('Expected RHS quasiparticle product changed')
    return routine.replace(original,replacement)


def robust_correction(routine):
    return zero_energy_correction(corrected(routine))


def run(blas):
    if not Path(blas).is_file():
        raise ValueError('Pass an existing compatible BLAS static library')
    with urlopen(URL,timeout=45) as response:
        data=response.read(1_000_001)
    extract(data)  # Reject any source outside the frozen hash before extraction.
    routine=re.search(r'(?ims)^SUBROUTINE gapeq_rhs\(delta,res\).*?^END SUBROUTINE gapeq_rhs',
                      data.decode()).group()
    result={}
    compiler=subprocess.check_output(['gfortran','--version'],text=True).splitlines()[0]
    for label,source,flags,threads in (
        ('released',routine,('-O0',),1),
        ('candidate_serial',corrected(routine),('-O0',),1),
        ('candidate_openmp',corrected(routine),('-O3','-fopenmp'),4)):
        with tempfile.TemporaryDirectory(prefix='sctk-full-rhs-') as folder:
            root=Path(folder)
            fixture=STUBS+'\n'+source
            (root/'probe.f90').write_text(fixture)
            subprocess.run(['gfortran',*flags,'-ffree-line-length-none','-fcheck=all',
                            str(root/'probe.f90'),str(Path(blas).resolve()),'-o',str(root/'probe')],
                           cwd=root,check=True,capture_output=True,text=True)
            output=subprocess.check_output([str(root/'probe')],text=True,
                                           env=dict(os.environ,OMP_NUM_THREADS=str(threads)))
            values=[float(line) for line in output.splitlines()]
        if len(values)!=5 or not all(map(math.isfinite,values)):
            raise AssertionError('Incomplete or nonfinite RHS output')
        result[label]=dict(values=values,max_absolute_error=max(abs(a-b) for a,b in zip(values,expected())),
                           flags=[*flags,'-ffree-line-length-none','-fcheck=all'],threads=threads,
                           fixture_sha256=hashlib.sha256(fixture.encode()).hexdigest())
    if result['released']['max_absolute_error']<.1:
        raise AssertionError('Expected assembled residual discrepancy absent')
    if any(result[key]['max_absolute_error']>1e-10 for key in ('candidate_serial','candidate_openmp')):
        raise AssertionError('Candidate assembled RHS disagrees')
    return dict(source_sha256=SHA256,compiler=compiler,
                blas_sha256=hashlib.sha256(Path(blas).read_bytes()).hexdigest(),
                direct=expected(),builds=result,
                scope='Complete RHS, synthetic interactions, xic=-1, serial MPI stubs; no gap solve')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blas',required=True)
    print(json.dumps(run(parser.parse_args().blas),indent=2,allow_nan=False))
