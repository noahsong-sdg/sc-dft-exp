"""Extract pinned current geometry for a fully shifted-grid compatibility test.

Generated GPL source stays in the ignored build directory. The retained native
QE build represents a fully shifted grid by logical true; current SCTK uses
three integer shift flags. This test fixes those flags to [1,1,1] explicitly.
"""
import argparse
import hashlib
from pathlib import Path
import re
from urllib.request import urlopen

REVISION='4bc883e5dfd8a2b38f47f2cb6efba26b773d5b33'
SHA256='2cc0458b5c98016567919d8d0c6d60cc2438f5a4e07c5e1ed43f8021e2305d80'
URL=f'https://raw.githubusercontent.com/mitsuaki1987/sctk/{REVISION}/src/sctk_ini_delta.f90'


def extract(data,unshifted=False):
    if hashlib.sha256(data).hexdigest()!=SHA256:raise ValueError('Current geometry source differs')
    source=data.decode();routines=[]
    for name in ('compute_dosk','symm_dosk'):
        matches=re.findall(r'(?ims)^SUBROUTINE '+name+r'\(.*?^END SUBROUTINE '+name+r'\s*$',source)
        if len(matches)!=1:raise ValueError('Owning geometry routine missing or ambiguous')
        routine,count=re.subn(r'(?im)^  USE elph_tetra_mod, ONLY : lshift_q\n','',matches[0])
        if count!=1:raise ValueError('Expected shift-array import changed')
        routines.append(routine)
    derivative_import='  USE sctk_ini_delta, ONLY : calc_d_xi_q\n'
    if unshifted:
        derivative=re.search(r'(?ims)^SUBROUTINE calc_d_xi_q\(.*?^END SUBROUTINE calc_d_xi_q\s*$',source).group()
        assignment='et(ibnd, ik) = et0(ibnd, ik) + qCq'
        if derivative.count(assignment)!=1:raise ValueError('Expected band-shift assignment changed')
        derivative=derivative.replace(assignment,'et(ibnd, ik) = et0(ibnd, ik)')
        routines.insert(0,derivative)
        derivative_import=''
    notice=source.split('MODULE sctk_ini_delta')[0]
    mode='unshifted-band linear-response diagnostic' if unshifted else 'finite-Q geometry compatibility diagnostic'
    return notice+f'! {mode}; fully shifted grid only; not a full current SCTK build.\n'+'''MODULE sctk_current_moment_geometry
'''+derivative_import+'''
  IMPLICIT NONE
  INTEGER,PARAMETER :: lshift_q(3)=[1,1,1]
CONTAINS
'''+ '\n'.join(routines)+'\nEND MODULE sctk_current_moment_geometry\n'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('destination',type=Path)
    parser.add_argument('--unshifted-bands',action='store_true',help='Keep immutable Q=0 band energies for the linear-response quadrature')
    args=parser.parse_args()
    with urlopen(URL,timeout=45) as response:data=response.read(300001)
    result=extract(data,args.unshifted_bands)
    with args.destination.open('x') as output:output.write(result)
    print(hashlib.sha256(result.encode()).hexdigest())
