"""Compare analytic slope with complete pinned native finite-Q currents."""
import hashlib
import json
import re
from urllib.request import urlopen
from full_current_probe import URL, SHA256, STUB, compile_run, stable_correction
from linear_response import stiffness,released_bias


def run():
    with urlopen(URL,timeout=45) as response:
        data=response.read(1_000_001)
    if hashlib.sha256(data).hexdigest()!=SHA256:
        raise ValueError('Current source differs')
    routine=re.search(r'(?ims)^SUBROUTINE supercurrent\(\).*?^END SUBROUTINE supercurrent',data.decode()).group()
    if routine.count('2e15.5')!=1:
        raise ValueError('Diagnostic format changed')
    routine=routine.replace('2e15.5','2es25.16')
    points=[.03,.01,.003,.001,.0003,.0001]
    cases=[(q,gamma) for gamma in (0.,3.) for q in points]
    driver=[STUB.split('program probe')[0],'program probe','use kinds','use cell_base',
            'use sctk_val','implicit none','bg(1,1)=1; bg(2,2)=1; bg(3,3)=1']
    for q,gamma in cases:
        driver.extend([
            'q_fflo=[%s_dp,0._dp,0._dp]' % q,
            'xi(1,:)=.4_dp; xi(2,:)=-.4_dp; beta=2',
            'delta=%s_dp; dxq=%s_dp; d2xq=%s_dp' % (1+gamma*q*q,.7*q,.3*q*q),
            'dk(1,:)=1; dk(2,:)=.25_dp','call supercurrent()'])
    driver.append('end program')
    released=compile_run(routine,'\n'.join(driver))
    candidate=compile_run(stable_correction(routine),'\n'.join(driver))
    if len(released)!=len(cases) or len(candidate)!=len(cases):
        raise AssertionError('Incomplete native slope output')
    states=[(.4,1.,1.,.7,.3),(-.4,1.,.25,.7,.3)]
    exact=stiffness(states,2.)
    bias=released_bias(states,2.)
    rows=[]
    for (q,gamma),old,new in zip(cases,released,candidate):
        ratios=[float(value)/q for value in new]
        if abs(ratios[0]-ratios[1])>1e-12:
            raise AssertionError('Synthetic identical grids differ')
        rows.append(dict(q=q,gap_quadratic_coefficient=gamma,
                         released_slope=float(old[0])/q,candidate_slope=ratios[0],
                         candidate_error=abs(ratios[0]-exact)))
    for gamma in (0.,3.):
        selected=[r for r in rows if r['gap_quadratic_coefficient']==gamma]
        if selected[-1]['candidate_error']>5e-8:
            raise AssertionError('Analytic slope limit not reached')
        # A factor ten smaller Q should reduce the smooth finite-Q error ~100x.
        if not 80 < selected[1]['candidate_error']/selected[3]['candidate_error'] < 120:
            raise AssertionError('Expected quadratic approach absent')
        if abs(selected[-1]['released_slope']-(exact+bias))>5e-8:
            raise AssertionError('Predicted released slope bias absent')
    return dict(source_sha256=SHA256,analytic_slope=exact,released_limit_bias=bias,
                cases=rows,scope='Synthetic complete current, serial, Q-even gap controls; no material prediction')


if __name__=='__main__':
    print(json.dumps(run(),indent=2,allow_nan=False))
