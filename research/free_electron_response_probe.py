"""Normalize the audited current using a spin-degenerate free-electron gas.

Energy is k**2 in Rydberg units; the radial quadrature is per spin. At the
chosen low temperature the Galilean stiffness equals total particle density.
This controls the scalar projection convention, not a material functional.
"""
import hashlib
import json
import math
import re
import subprocess
from urllib.request import urlopen

from full_current_probe import URL,SHA256,compile_run,robust_correction
from linear_response import stiffness

N=12000
KMAX=4.
BETA=1000.
GAP=.1


def reference(n=N):
    step=KMAX/n
    states=[];density=[]
    for i in range(n):
        k=(i+.5)*step;xi=k*k-1;energy=math.hypot(xi,GAP)
        weight=step*k*k/(2*math.pi**2)
        states.append((xi,GAP,weight,k/math.sqrt(3),.25))
        # Both spin occupations, not a derivative of the response expression.
        density.append(weight*(1-xi/energy*math.tanh(.5*BETA*energy)))
    total=math.fsum(density)
    slope=stiffness(states,BETA)
    return dict(radial_points=n,cutoff=KMAX,beta=BETA,gap=GAP,
                total_particle_density=total,analytic_code_slope=slope,
                relative_density_error=slope/total-1)


def run():
    with urlopen(URL,timeout=45) as response:data=response.read(1_000_001)
    if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Pinned current differs')
    routine=re.search(r'(?ims)^SUBROUTINE supercurrent\(\).*?^END SUBROUTINE supercurrent',data.decode()).group()
    routine=robust_correction(routine).replace('2e15.5','2es25.16')
    driver=f'''
module kinds
 use iso_fortran_env, only: dp=>real64
end module
module io_global
 use iso_fortran_env, only: stdout=>output_unit
end module
module cell_base
 use kinds
 real(dp) :: omega=1, bg(3,3)=0, tpiba=1
end module
module sctk_val
 use kinds
 integer, parameter :: nk={N}
 real(dp) :: xi(nk,2),delta(nk,2),dxq(nk,2),dk(nk,2),d2xq(nk,2),q_fflo(3),beta
 integer :: ngap(2)=nk
end module
program probe
 use kinds
 use cell_base
 use sctk_val
 implicit none
 integer :: i,j
 real(dp) :: k,q,step,pi
 pi=acos(-1._dp);step={KMAX}_dp/nk; beta={BETA}_dp
 bg(1,1)=1;bg(2,2)=1;bg(3,3)=1
 do j=1,3
 q=10._dp**(-j-2);q_fflo=[q,0._dp,0._dp]
 do i=1,nk
 k=(i-.5_dp)*step
 xi(i,:)=k*k-1
 delta(i,:)={GAP}_dp
 dk(i,:)=step*k*k/(2*pi*pi)
 dxq(i,:)=k*q/sqrt(3._dp)
 d2xq(i,:)=q*q/4
 end do
 call supercurrent()
 end do
end program
'''
    ref=reference();cases=[]
    for flags,threads in ((('-O0',),1),(('-O3','-fopenmp'),4)):
        outputs=compile_run(routine,driver,flags,threads)
        if len(outputs)!=3:raise AssertionError('Missing momentum controls')
        errors=[]
        for i,pair in enumerate(outputs,1):
            q=10**(-i-2)
            values=[float(value)/q for value in pair]
            error=max(abs(value/ref['total_particle_density']-1) for value in values)
            if not all(map(math.isfinite,values)):raise AssertionError('Nonfinite free-gas response')
            errors.append(error)
        if errors[-1]>1e-7 or abs(ref['relative_density_error'])>1e-8:
            raise AssertionError('Free-gas density/stiffness normalization failed')
        cases.append(dict(flags=[*flags,'-std=f2008','-fcheck=all'],threads=threads,momenta=[1e-3,1e-4,1e-5],
                          relative_density_errors=errors))
    return dict(source_sha256=SHA256,fixture_sha256=hashlib.sha256((driver+routine).encode()).hexdigest(),
                compiler=subprocess.check_output(['gfortran','--version'],text=True).splitlines()[0],
                reference=ref,builds=cases,
                scope='Low-T free gas, single-spin weights and implicit two-spin current; not a niobium prediction')


if __name__=='__main__':print(json.dumps(run(),indent=2,allow_nan=False))
