"""Complete native current on prepared Nb geometry with imposed constant gaps.

This is a numerical-impact diagnostic, not a self-consistent material prediction.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.request import urlopen
from full_current_probe import URL,SHA256,STUB,compile_run,stable_correction
from preparation_analysis import analyze


def run(path):
    path=Path(path).resolve()
    validation=analyze(path)
    with urlopen(URL,timeout=45) as response:data=response.read(1_000_001)
    if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Source differs')
    routine=re.search(r'(?ims)^SUBROUTINE supercurrent\(\).*?^END SUBROUTINE supercurrent',data.decode()).group()
    if routine.count('2e15.5')!=1:raise ValueError('Output format differs')
    routine=routine.replace('2e15.5','2es25.16')
    modules=STUB.split('program probe')[0].replace(
        'real(dp) :: xi(2,2),delta(2,2),dxq(2,2),dk(2,2),d2xq(2,2),q_fflo(3),beta',
        'real(dp),allocatable :: xi(:,:),delta(:,:),dxq(:,:),dk(:,:),d2xq(:,:)\n real(dp) :: q_fflo(3),beta')
    # Data path is a Fortran literal, not shell text.
    literal=str(path).replace("'","''")
    driver=modules+f"""
program probe
 use kinds
 use cell_base
 use sctk_val
 implicit none
 integer :: unit,i,g,owner,k,b,n,t
 real(dp) :: gap
 character(200) :: header
 open(newunit=unit,file='{literal}',status='old')
 read(unit,'(a)') header
 read(unit,*) ngap
 read(unit,*) beta,omega,tpiba
 read(unit,*) q_fflo
 read(unit,*) bg
 n=maxval(ngap)
 allocate(xi(n,2),delta(n,2),dk(n,2),dxq(n,2),d2xq(n,2))
 do g=1,2
   do i=1,ngap(g)
     read(unit,*) xi(i,g),delta(i,g),dk(i,g),dxq(i,g),d2xq(i,g),owner,k,b
   end do
 end do
 close(unit)
 do t=1,3
   beta=157887.51240203338_dp/real(2**t,dp)
   delta=0
   call supercurrent()
   delta=1.5_dp/13605.693122994_dp
   call supercurrent()
 end do
end program
"""
    old=compile_run(routine,driver)
    new=compile_run(stable_correction(routine),driver)
    with path.open() as source:
        for _ in range(5):source.readline()
        states=[[],[]]
        for g,count in enumerate([r['states'] for r in validation['grids']]):
            for _ in range(count):states[g].append(list(map(float,source.readline().split()[:5])))
    rows=[]
    for temperature in (2,4,8):
        beta=157887.51240203338/temperature
        for gap_mev in (0,1.5):
            gap=gap_mev/13605.693122994
            references=[]
            for grid in states:
                terms=[]
                for xi,_,weight,shift,curvature in grid:
                    energy=math.hypot(xi,gap)
                    def factors(e):
                        plus=math.tanh(.5*beta*(e+abs(shift)))
                        minus=math.tanh(.5*beta*(e-abs(shift)))
                        return .5*(plus+minus),.5*(plus-minus)
                    ed,de=factors(energy);xd,dx=factors(abs(xi))
                    # At E=0 both xi and gap vanish; xi/E times the odd-in-E
                    # occupation sum has the continuous value zero.
                    paired=0. if energy==0 else xi/energy*ed
                    terms.append(weight*(2*abs(shift)*(dx-de)+4*curvature*
                                          (math.copysign(xd,xi)-paired)))
                references.append(math.fsum(terms)/(validation['volume']*validation['qnorm']))
            index=len(rows);original=list(map(float,old[index]));candidate=list(map(float,new[index]))
            finite=all(map(math.isfinite,candidate))
            if gap_mev and (not finite or max(abs(a-b) for a,b in zip(candidate,references))>1e-10):
                raise AssertionError('Native candidate disagrees with direct occupations')
            if gap_mev==0 and finite and max(map(abs,candidate))>1e-12:
                raise AssertionError('Normal-state current does not cancel')
            rows.append(dict(temperature_kelvin=temperature,imposed_gap_mev=gap_mev,
                             released=[x if math.isfinite(x) else None for x in original],
                             candidate=[x if math.isfinite(x) else None for x in candidate],
                             native_candidate_finite=finite,direct_reference=references,
                             released_minus_reference=[a-b if math.isfinite(a) else None
                                                       for a,b in zip(original,references)]))
    return dict(preparation=validation,source_sha256=SHA256,cases=rows,
                scope='Frozen finite-Q material geometry, imposed constant gaps; no self-consistency or experimental accuracy claim')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('state',type=Path)
    args=parser.parse_args();print(json.dumps(run(args.state),indent=2,allow_nan=False))
