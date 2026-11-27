"""Stage six uncached full-sum checks against a certified completed Z sweep."""
import argparse
import json
from pathlib import Path
import shutil

from fetch_public_response_inputs import digest
from portable_z_sweep import checkpoint
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def completed_sweep(root):
    root = Path(root).absolute()
    manifest = root/'run-manifest.json'
    receipt = root/'results/zsweep/receipt.json'
    result = json.loads((root/'z-sweep-result.json').read_text())
    m = json.loads(manifest.read_text()); r = json.loads(receipt.read_text())
    identities = {'manifest_sha256': manifest, 'receipt_sha256': receipt,
        'checkpoint_sha256': root/'z-checkpoint.bin',
        'metadata_sha256': root/'z-checkpoint.meta', 'executable_sha256': root/'z-sweep.x'}
    if result['status'] != 'PASS' or any(result[key] != digest(p) for key,p in identities.items()):
        raise ValueError('Changed certified completed sweep')
    if ((r.get('status'),r.get('exit'),r.get('error'),r.get('command'),r.get('cwd'))
            != ('PASS',0,None,m['command'],str(root))):
        raise ValueError('Unaccepted completed sweep receipt')
    verify_postrun_inputs(m,root)
    saved = checkpoint(root)
    if (saved != result['checkpoint'] or saved['completed'] != 66867
            or saved['counts'] != [66867,67940,67940]
            or saved['context'] != m['context_sha256'] or m['rows'][1] != 66867
            or not m['qualified_chain'] or m['qualification']):
        raise ValueError('Incomplete or mismatched full Z sweep')
    log = (root/'results/zsweep/console.log').read_text()
    if log.count('Z_SWEEP_CHECKPOINT_PASS') != 1 or log.count('CHECKED_FULL_Z_FS ') != 1:
        raise ValueError('Missing completed Z output')
    if digest(root/'full-z.bin') != result['checkpoint_sha256']:
        raise ValueError('Full Z differs from certified ordered sums')
    lines = (root/'full-z.meta').read_text().splitlines()
    if (len(lines) != 4 or lines[0] != 'native-Z-v1; binary64 Fortran order'
            or list(map(int,lines[1].split())) != [66867,67940,67940,100,1]
            or float(lines[2].split()[0]) != saved['beta'] or lines[3].strip() != 'F'):
        raise ValueError('Stale full Z metadata')
    return m


def stage(completed, initialization, build, destination):
    completed, initialization, build, root = map(lambda p: Path(p).absolute(),
        (completed,initialization,build,destination))
    if root.exists():
        raise ValueError('Fresh Z oracle directory required')
    m = completed_sweep(completed)
    identities = {item['path']: item for item in m['files']}
    extras = [completed/n for n in ('run-manifest.json','z-sweep-result.json',
        'results/zsweep/receipt.json','results/zsweep/console.log','z-checkpoint.meta',
        'z-checkpoint.bin','z-sweep.x','full-z.meta','full-z.bin')]
    extras += [Path(__file__),RESEARCH/'portable_z_sweep.py']
    extras += [RESEARCH/'portable_gap'/n for n in ('native_oracle_z.f90',
        'z_oracle_source_provenance.json','z_sample_oracle.f90','z_sample_oracle.mk')]
    for p in extras:
        identities[str(p)] = dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p))
    # The native verifier must use the same accepted geometry and library context.
    for p in (initialization/'native-init.bin',initialization/'native-init.meta',build/'qe/make.inc'):
        if str(p) not in identities or identities[str(p)]['sha256'] != digest(p):
            raise ValueError('Different geometry or build context')
    root.mkdir(parents=True)
    shutil.copy2(initialization/'native.in',root/'native.in')
    (root/'z-oracle-control.in').write_text(str(initialization)+'\n'+str(completed)+'\n')
    for p in (root/'native.in',root/'z-oracle-control.in'):
        identities[str(p)] = dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p))
    command = ['/usr/bin/make','-f',str(RESEARCH/'portable_gap/z_sample_oracle.mk'),
        'RESEARCH='+str(RESEARCH),'QE_ROOT='+str(build/'qe'),
        'NATIVE_INPUT='+str(root/'native.in'),'qualify-oracle']
    manifest = dict(cwd=str(root),command=command,files=list(identities.values()),
        guard_seconds=420,launch_normal_seconds=120,temperature_kelvin=8.05,
        acceptance='Six uncached full sums bitwise equal to completed Z: first, last, first positive-weight Fermi state on each grid; strict geometry/full-Z metadata/Fermi-average readback',
        forecast='404421 pairs plus cold initialization and up to512 slab groups; below420s/3GiB scheduling estimate, not a runtime bound')
    (root/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('completed','initialization','build','destination'):
        p.add_argument(name,type=Path)
    print(json.dumps(stage(**vars(p.parse_args())),indent=2))
