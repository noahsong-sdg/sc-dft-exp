"""Replay a documented archived gap using separately reconstructed curvature.

Geometry must match before transfer. This freezes the released gap; it does not
re-solve the corrected gap equation or infer a zero-Q penetration depth.
"""
import argparse
import array
import hashlib
import json
import math
from pathlib import Path
import re
import resource
import sys
import time
from urllib.request import urlopen

from archived_finite_q_gap import records
from compare_finite_q_geometry import compare
from full_current_probe import URL,SHA256,STUB,compile_run,robust_correction


def run(preparation,gap):
    began=time.perf_counter()
    preparation=Path(preparation).resolve();gap=Path(gap).resolve()
    geometry=compare(preparation,gap)
    for row in geometry['grids']:
        if row['index_mismatches'] or max(row[name] for name in
                ('max_xi_absolute_difference','max_weight_absolute_difference','max_shift_absolute_difference'))>1e-12:
            raise ValueError('Archived geometry does not match reconstruction to the declared 1e-12 boundary')
    qvec=[geometry['tpiba']*math.fsum(geometry['reciprocal_basis_fortran_order'][r+3*c]*
                geometry['momentum_fractional'][c] for c in range(3)) for r in range(3)]
    q=math.hypot(*qvec)
    if q<=0:raise ValueError('Finite-Q replay requires nonzero physical momentum')
    dimensions=[row['states'] for row in geometry['grids']]
    terms=[array.array('d'),array.array('d')];zero_xi=[0,0]
    with preparation.open() as source:
        for _ in range(5):source.readline()
        for grid,state,values,indices in records(gap,dimensions):
            curvature=float(source.readline().split()[4])
            xi,delta,z,weight,shift=values;energy=math.hypot(xi,delta)
            zero_xi[grid]+=xi==0
            def thermal(e):
                plus=math.tanh(.5*geometry['beta']*(e+abs(shift)))
                minus=math.tanh(.5*geometry['beta']*(e-abs(shift)))
                return .5*(plus+minus),.5*(plus-minus)
            ed,de=thermal(energy);xd,dx=thermal(abs(xi))
            paired=0. if energy==0 else xi/energy*ed
            terms[grid].append(weight*(2*abs(shift)*(dx-de)+
                               4*curvature*(math.copysign(xd,xi)-paired)))
    direct=[math.fsum(values)/(geometry['volume']*q) for values in terms]
    with urlopen(URL,timeout=45) as response:data=response.read(1_000_001)
    if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Pinned current differs')
    routine=re.search(r'(?ims)^SUBROUTINE supercurrent\(\).*?^END SUBROUTINE supercurrent',data.decode()).group()
    routine=routine.replace('2e15.5','2es25.16')
    modules=STUB.split('program probe')[0].replace(
        'real(dp) :: xi(2,2),delta(2,2),dxq(2,2),dk(2,2),d2xq(2,2),q_fflo(3),beta',
        'real(dp),allocatable :: xi(:,:),delta(:,:),dxq(:,:),dk(:,:),d2xq(:,:)\n real(dp) :: q_fflo(3),beta')
    p_literal=str(preparation).replace("'","''");g_literal=str(gap).replace("'","''")
    driver=modules+f'''
program probe
 use kinds
 use cell_base
 use sctk_val
 implicit none
 integer :: u,v,i,g,n,owner,k,b,ki,bi,saved(2)
 real(dp) :: x,d,z,w,shift
 character(200) :: header
 open(newunit=u,file='{p_literal}',status='old')
 open(newunit=v,file='{g_literal}',status='old')
 read(u,'(a)')header
 read(u,*)ngap
 read(u,*)beta,omega,tpiba
 read(u,*)q_fflo
 read(u,*)bg
 read(v,'(a)')header
 read(header(3:),*)saved
 if(any(saved/=ngap))error stop 'Archive dimensions changed'
 n=maxval(ngap)
 allocate(xi(n,2),delta(n,2),dk(n,2),dxq(n,2),d2xq(n,2))
 do g=1,2
 do i=1,ngap(g)
 read(u,*)xi(i,g),delta(i,g),dk(i,g),dxq(i,g),d2xq(i,g),owner,k,b
 read(v,*)x,d,z,w,shift,ki,bi
 if(owner/=g.or.k/=ki.or.b/=bi)error stop 'Archive ordering changed'
 xi(i,g)=x;delta(i,g)=d;dk(i,g)=w;dxq(i,g)=shift
 end do
 end do
 close(u);close(v)
 call supercurrent()
 delta=0
 call supercurrent()
end program
'''
    builds={}
    for label,code,flags,threads in (
            ('released',routine,('-O0',),1),
            ('candidate_serial',robust_correction(routine),('-O0',),1),
            ('candidate_openmp',robust_correction(routine),('-O3','-fopenmp'),4)):
        output=compile_run(code,driver,flags,threads)
        if len(output)!=2:raise AssertionError('Missing archived/normal current output')
        values=[list(map(float,row)) for row in output]
        if not all(map(math.isfinite,values[0])):raise AssertionError('Nonfinite archived-gap replay')
        normal_finite=all(map(math.isfinite,values[1]))
        if (not normal_finite and label!='released') or (normal_finite and max(map(abs,values[1]))>1e-12):
            raise AssertionError('Normal-state cancellation failed')
        builds[label]=dict(current=values[0],normal_control=[v if math.isfinite(v) else None for v in values[1]],
                           normal_control_finite=normal_finite,
                           flags=[*flags,'-std=f2008','-fcheck=all'],threads=threads)
    published=[1.0308e-6,1.1274e-6]
    reproduction=max(abs(a-b) for a,b in zip(builds['released']['current'],published))
    if reproduction>5.1e-11:raise AssertionError('Released current not reproduced at printed precision')
    for label in ('candidate_serial','candidate_openmp'):
        if max(abs(a-b) for a,b in zip(builds[label]['current'],direct))>1e-12:
            raise AssertionError('Corrected replay differs from direct occupations')
    scale=1 if sys.platform=='darwin' else 1024
    return dict(geometry=geometry,qnorm=q,source_sha256=SHA256,
                driver_sha256=hashlib.sha256(driver.encode()).hexdigest(),
                direct=direct,published_current=published,reproduction_absolute_error=reproduction,
                exact_zero_xi_states=zero_xi,
                builds=builds,wall_s=time.perf_counter()-began,
                python_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*scale,
                max_child_rss_bytes_including_compiler=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*scale,
                scope='Documented converged finite-Q gap frozen; curvature reconstructed; no corrected gap solve or zero-Q prediction')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('preparation',type=Path);parser.add_argument('gap',type=Path)
    args=parser.parse_args();print(json.dumps(run(args.preparation,args.gap),indent=2,allow_nan=False))
