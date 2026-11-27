"""Complete pinned RHS regression at the finite-temperature E=0 boundary."""
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

from full_rhs_probe import STUBS, corrected, zero_energy_correction, expected
from rhs_thermal_probe import URL,SHA256,extract


def evaluate(source,driver,blas,flags,threads):
    with tempfile.TemporaryDirectory(prefix='sctk-rhs-zero-') as folder:
        root=Path(folder); fixture=driver+'\n'+source
        (root/'probe.f90').write_text(fixture)
        subprocess.run(['gfortran',*flags,'-ffree-line-length-none','-fcheck=all',
                        str(root/'probe.f90'),str(blas),'-o',str(root/'probe')],
                       cwd=root,check=True,capture_output=True,text=True)
        output=subprocess.check_output([str(root/'probe')],text=True,
                    env=dict(os.environ,OMP_NUM_THREADS=str(threads)))
    return [float(line) for line in output.splitlines()]


def run(blas):
    blas=Path(blas).resolve()
    with urlopen(URL,timeout=45) as response:data=response.read(1_000_001)
    extract(data)
    routine=re.search(r'(?ims)^SUBROUTINE gapeq_rhs\(delta,res\).*?^END SUBROUTINE gapeq_rhs',data.decode()).group()
    thermal=corrected(routine); candidate=zero_energy_correction(thermal)
    # Preserve the nontrivial BLAS matrices, Z factors, and unequal grid sizes.
    driver=STUBS.replace('delta=2; delta(3,1)=0','delta=0; beta=2')
    driver=driver.replace(' call gapeq_rhs(delta,res)', ''' do boundary=1,3
 xi=real(boundary-2,dp)*1.e-12_dp
 do shift=0,2
 dxq=real(shift,dp)*.2_dp
 call gapeq_rhs(delta,res)''')
    driver=driver.replace(' integer :: grid, state',' integer :: grid, state, boundary, shift')
    driver=driver.replace('end program',' end do\n end do\nend program')
    old=evaluate(thermal,driver,blas,('-O0',),1)
    if len(old)!=45 or sum(not math.isfinite(x) for x in old)!=15:
        raise AssertionError('Expected three singular five-state residuals absent')
    builds=[]
    for flags,threads in ((('-O0',),1),(('-O3','-fopenmp'),4)):
        values=evaluate(candidate,driver,blas,flags,threads)
        control=evaluate(candidate,STUBS,blas,flags,threads)
        if len(values)!=45 or any(not math.isfinite(x) or x!=0 for x in values):
            raise AssertionError('Finite-temperature normal RHS is not zero')
        error=max(abs(a-b) for a,b in zip(control,expected()))
        if len(control)!=5 or error>1e-10:
            raise AssertionError('Nonzero-gap control changed')
        builds.append(dict(flags=flags,threads=threads,normal_residual_max=0,
                           nonzero_gap_control_error=error))
    return dict(source_sha256=SHA256,blas_sha256=hashlib.sha256(blas.read_bytes()).hexdigest(),
                compiler=subprocess.check_output(['gfortran','--version'],text=True).splitlines()[0],
                fixture_sha256=hashlib.sha256((driver+'\n'+candidate).encode()).hexdigest(),
                previous_nonfinite_residuals=15,normal_cases_per_build=9,
                builds=builds,scope='Complete RHS, finite temperature, synthetic interactions, xic=-1; zero-T unchanged')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--blas',required=True)
    print(json.dumps(run(parser.parse_args().blas),indent=2,allow_nan=False))
