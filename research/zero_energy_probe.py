"""Full pinned current regression for the E=0 normal-state boundary."""
import hashlib
import json
import math
import re
from urllib.request import urlopen
from full_current_probe import URL,SHA256,STUB,compile_run,stable_correction,robust_correction


def run():
    with urlopen(URL,timeout=45) as response:data=response.read(1_000_001)
    if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Source differs')
    routine=re.search(r'(?ims)^SUBROUTINE supercurrent\(\).*?^END SUBROUTINE supercurrent',data.decode()).group()
    routine=routine.replace('2e15.5','2es25.16')
    driver=STUB.split('program probe')[0]+'''
program probe
 use kinds
 use cell_base
 use sctk_val
 implicit none
 integer :: i,j
 real(dp) :: values(3)=[0._dp,1.e-12_dp,-1.e-12_dp]
 bg(1,1)=1; bg(2,2)=1; bg(3,3)=1
 q_fflo=[1._dp,0._dp,0._dp]
 do i=1,3
   xi=values(i);delta=0;dk=1;d2xq=.3_dp
   do j=1,3
     dxq=real(j-1,dp)*.2_dp;beta=2
     call supercurrent()
   end do
 end do
end program
'''
    old=compile_run(stable_correction(routine),driver)
    results=[]
    for flags,threads in [(('-O0',),1),(('-O3','-fopenmp'),4)]:
        new=compile_run(robust_correction(routine),driver,flags,threads)
        if len(new)!=9:raise AssertionError('Missing boundary cases')
        error=max(abs(float(value)) for row in new for value in row)
        if not all(math.isfinite(float(value)) for row in new for value in row) or error>1e-14:
            raise AssertionError('Normal-state cancellation failed')
        results.append(dict(flags=flags,threads=threads,max_normal_current=error))
    if not all(not math.isfinite(float(v)) for row in old[:3] for v in row):
        raise AssertionError('Expected original boundary failure absent')
    return dict(source_sha256=SHA256,previous_candidate_nonfinite_cases=3,
                cases_per_build=9,builds=results,
                scope='Full routine E=0 and two-sided approach, normal-state controls')


if __name__=='__main__':print(json.dumps(run(),indent=2,allow_nan=False))
