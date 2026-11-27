"""Stage measured fresh-basis work only after certified uncached full-Z checks."""
import argparse
import json
from pathlib import Path
import shutil

from fetch_public_response_inputs import digest
from portable_z_oracle import completed_sweep
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def accepted_oracle(root):
    root = Path(root).absolute()
    manifest = root/'run-manifest.json';receipt = root/'results/zoracle/receipt.json'
    result = json.loads((root/'z-oracle-result.json').read_text())
    m = json.loads(manifest.read_text());r = json.loads(receipt.read_text())
    paths = {'manifest_sha256':manifest,'receipt_sha256':receipt,
        'samples_sha256':root/'z-oracle-samples.bin','sample_metadata_sha256':root/'z-samples.meta',
        'executable_sha256':root/'z-oracle.x'}
    if (result['status'] != 'PASS' or result['six_full_sums_bitwise_equal'] is not True
            or any(result[key] != digest(p) for key,p in paths.items())):
        raise ValueError('Changed or unqualified Z oracle')
    if ((r.get('status'),r.get('exit'),r.get('error'),r.get('command'),r.get('cwd'))
            != ('PASS',0,None,m['command'],str(root))):
        raise ValueError('Unaccepted Z oracle receipt')
    verify_postrun_inputs(m,root)
    control = (root/'z-oracle-control.in').read_text().splitlines()
    if len(control) != 2:
        raise ValueError('Stale Z oracle control')
    geometry,completed = map(Path,control)
    completed_sweep(completed)
    if (digest(completed/'full-z.bin') != result['full_Z_sha256']
            or digest(completed/'full-z.meta') != result['full_Z_metadata_sha256']
            or (root/'results/zoracle/console.log').read_text().count('Z_SIX_UNCACHED_FULL_SUMS_BITWISE_PASS') != 1):
        raise ValueError('Changed qualified full Z')
    return m,geometry,completed


def stage(oracle,build,destination):
    oracle,build,root = map(lambda p: Path(p).absolute(),(oracle,build,destination))
    if root.exists():
        raise ValueError('Fresh basis measurement directory required')
    m,geometry,completed = accepted_oracle(oracle)
    identities = {item['path']:item for item in m['files']}
    for p in (geometry/'native-init.bin',geometry/'native-init.meta',build/'qe/make.inc'):
        if str(p) not in identities or identities[str(p)]['sha256'] != digest(p):
            raise ValueError('Different fresh geometry or build')
    files = [oracle/n for n in ('run-manifest.json','z-oracle-result.json','results/zoracle/receipt.json',
        'results/zoracle/console.log','z-oracle-control.in','z-oracle-samples.bin','z-samples.meta','z-oracle.x')]
    files += [Path(__file__),RESEARCH/'portable_z_oracle.py',RESEARCH/'portable_z_sweep.py',
        RESEARCH/'public_band_pilot_analysis.py',RESEARCH/'fetch_public_response_inputs.py']
    files += [RESEARCH/'portable_gap'/name for name in ('basis_partial_driver.f90','basis_partial.mk',
        'basis_compile.mk','block_linear_operator.f90','tc_subspace.f90','basis_source_provenance.json',
        'full_link.mk','operator_compile.mk','cache_qualification.mk','cached_kel.f90','cached_phonon.f90',
        'tiled_operator.f90','tc_native_oracle.f90','streamed_coulomb.f90','saved_coulomb.f90')]
    for p in files:
        identities[str(p)] = dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p))
    root.mkdir(parents=True)
    shutil.copy2(geometry/'native.in',root/'native.in')
    (root/'basis-partial-control.in').write_text(str(geometry)+'\n'+str(completed)+'\n')
    for p in (root/'native.in',root/'basis-partial-control.in'):
        identities[str(p)] = dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p))
    command = ['/usr/bin/make','-f',str(RESEARCH/'portable_gap/basis_partial.mk'),
        'RESEARCH='+str(RESEARCH),'QE_ROOT='+str(build/'qe'),
        'NATIVE_INPUT='+str(root/'native.in'),'qualify-basis-partial']
    manifest = dict(cwd=str(root),command=command,files=list(identities.values()),guard_seconds=420,
        launch_normal_seconds=120,temperature_kelvin=8.05,trial_columns=16,seed=29,
        left_blocks=[[1,64],[16717,16780],[33434,33497],[66804,66867]],
        acceptance='Strict fresh geometry, independently sampled full Z, finite16-column partial images, selected complete left and block-right sums match uncached native pairs under frozen2e-13+2e-12*reference bound; not full basis or gap',
        forecast='Below420s/3GiB including cold pairing-only setup, four64-row blocks and uncached controls; scheduling estimate, not a bound; measure before full application forecast')
    (root/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('oracle','build','destination'):
        p.add_argument(name,type=Path)
    print(json.dumps(stage(**vars(p.parse_args())),indent=2))
