"""Read back a declared32/48/64cubed imposed-gap response, without claiming convergence."""
import argparse
import json
from pathlib import Path

from cell_moment_cache import read_pair
from constant_moment_components import analyze as components
from fetch_public_response_inputs import digest
from moment_analysis import analyze as native_controls
from public_band_pilot_analysis import verify_postrun_inputs


def verify(directory, manifest_path, guard_seconds=240,grid=48):
    root=Path(directory).absolute();manifest_path=Path(manifest_path).absolute()
    manifest=json.loads(manifest_path.read_text())
    deadlines={32:(120,),48:(240,900),64:(900,)}
    if (grid not in deadlines or guard_seconds not in deadlines.get(grid,())
            or manifest['cwd']!=str(root) or manifest['grid']!=[grid]*3
            or manifest['response_cell_grid']!=8 or manifest['guard_seconds']!=guard_seconds):
        raise ValueError('Changed declared refined-response protocol')
    if json.loads((root/'run-manifest.json').read_text())!=manifest:
        raise ValueError('Public and consumed manifests differ')
    verify_postrun_inputs(manifest,root)
    receipt_path=root/'results/response/receipt.json'
    receipt=json.loads(receipt_path.read_text())
    if (receipt.get('status')!='PASS' or receipt.get('error') is not None
            or receipt.get('exit')!=0 or receipt['command']!=manifest['command']
            or receipt['cwd']!=str(root) or receipt['continuous_deadline_s']!=guard_seconds):
        raise ValueError('Refined-response execution did not pass')
    controls=native_controls(root/'velocity-moments.txt')
    dims,physical,_,_=read_pair(root)
    if (controls['dimensions']!=[100,6,7,grid**3,8**3]
            or dims!=[100,6,7,8**3,2]
            or physical[2:]!=[1e-12,0.,0.]):
        raise ValueError('Changed native response grid or imposed momentum')
    terms=components(root)
    paths=[manifest_path,receipt_path,root/'velocity-moments.txt']
    return dict(terminal_receipt=receipt,native_controls=controls,
        cache_dimensions=dims,cache_physical=physical,components=terms,
        all_declared_inputs_unchanged=True,diagnostic_readback_pass=True,
        physical_response_verified=False,
        sha256={str(p):digest(p) for p in paths},
        scope=__doc__.strip()+' Numerical conservation is not physical response accuracy.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path);parser.add_argument('manifest_path',type=Path)
    parser.add_argument('--guard-seconds',type=int,default=240,choices=(120,240,900),
                        help='Explicit prospective protocol deadline; no automatic retry')
    parser.add_argument('--grid',type=int,choices=(32,48,64),default=48)
    print(json.dumps(verify(**vars(parser.parse_args())),indent=2,allow_nan=False))
