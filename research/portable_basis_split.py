"""Admit actual-input linear-image restart qualification from certified fresh trials."""
import argparse
import hashlib
import json
from pathlib import Path

from fetch_public_response_inputs import digest
from portable_basis_partial import stage as stage_partial
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def accepted_trials(root):
    root = Path(root).absolute()
    result = json.loads((root/'basis-partial-result.json').read_text())
    manifest = json.loads((root/'run-manifest.json').read_text())
    paths = {'manifest_sha256':root/'run-manifest.json',
        'receipt_sha256':root/'results/basispartial/receipt.json',
        'binary_sha256':root/'basis-partial.bin','metadata_sha256':root/'basis-partial.meta',
        'executable_sha256':root/'basis-partial.x','analysis_source_sha256':RESEARCH/'basis_partial_analysis.py'}
    if result['status'] != 'PASS' or any(result[key] != digest(path) for key,path in paths.items()):
        raise ValueError('Changed or unqualified fresh trials')
    verify_postrun_inputs(manifest,root)
    return list(paths.values()) + [root/'basis-partial-result.json']


def stage(oracle,build,trials,destination):
    trials,root = map(lambda p:Path(p).absolute(),(trials,destination))
    evidence = accepted_trials(trials)
    m = stage_partial(oracle,build,root)
    # Keep inherited source/input identities; this experiment replaces only control/driver.
    evidence += [Path(__file__),RESEARCH/'portable_basis_partial.py',
        RESEARCH/'portable_gap/basis_sweep_driver.f90',RESEARCH/'portable_gap/basis_sweep.mk',
        RESEARCH/'portable_gap/linear_image_checkpoint.f90']
    identities = {item['path']:item for item in m['files'] if not Path(item['path']).is_relative_to(root)}
    for path in evidence:
        identities[str(path)] = dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path))
    context = hashlib.sha256(json.dumps(list(identities.values()),sort_keys=True).encode()).hexdigest()
    geometry,completed = (root/'basis-partial-control.in').read_text().splitlines()
    (root/'basis-partial-control.in').unlink()
    control = root/'basis-sweep-control.in'
    control.write_text('fresh-basis-split-control-v1\n'+geometry+'\n'+completed+'\n'
        +str(trials/'basis-partial.bin')+'\n'+context+'\n')
    (root/'split').mkdir()
    for path in (control,root/'native.in'):
        identities[str(path)] = dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path))
    m.update(files=list(identities.values()),context_sha256=context,
        command=['/usr/bin/make','-f',str(RESEARCH/'portable_gap/basis_sweep.mk'),
            'RESEARCH='+str(RESEARCH),'QE_ROOT='+str(Path(build).absolute()/'qe'),
            'NATIVE_INPUT='+str(root/'native.in'),'qualify-basis-sweep'],
        rows=[1,64],tile_width=32,qualification=True,
        acceptance='Uninterrupted1:64 vs1:32 + persisted/reloaded33:64 bitwise across all16 unnormalized images, cache/slab reset at restart; strict context and serialization; not full images or gap',
        forecast='Below420s/3GiB including cold setup and two64-row applications, based on53s partial qualification; scheduling estimate, not bound')
    m.pop('left_blocks')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    return m


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('oracle','build','trials','destination'):
        parser.add_argument(name,type=Path)
    print(json.dumps(stage(**vars(parser.parse_args())),indent=2))
