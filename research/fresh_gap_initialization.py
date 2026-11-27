"""Stage fresh Mac Q0 geometry; no retained Z, basis or gap state is consumed."""
import argparse
import json
from pathlib import Path
import shutil

from fetch_public_response_inputs import digest, validate

RESEARCH = Path(__file__).resolve().parent


def stage(build, inputs, native_input, destination):
    build, inputs, native_input, root = map(lambda p: Path(p).absolute(),
        (build, inputs, native_input, destination))
    if root.exists():
        raise ValueError('Fresh initialization directory required')
    if json.loads((build/'build-result.json').read_text())['source_manifest_sha256'] != digest(RESEARCH/'public_response_sources.json'):
        raise ValueError('Different public source build')
    files = []
    catalog = RESEARCH/'public_response_inputs.json'
    for name, item in json.loads(catalog.read_text())['files'].items():
        p = inputs/validate(name, item)
        if p.stat().st_size != item['bytes'] or digest(p) != item['sha256']:
            raise ValueError('Changed microscopic input: '+name)
        files.append(p)
    # The input points to this exact bundle; no undeclared restart directory.
    text = native_input.read_text()
    if text.count("outdir='"+str(inputs)+"/'") != 1:
        raise ValueError('Native input directory differs from declared bundle')
    qe = build/'qe'
    files += [native_input, catalog, Path(__file__), RESEARCH/'public_response_sources.json',
        RESEARCH/'portable_gap/fresh_gap_initialization.f90',
        RESEARCH/'portable_gap/fresh_gap_initialization.mk',
        RESEARCH/'portable_gap/native_state_io.f90', RESEARCH/'public_response_probe.mk',
        RESEARCH/'macos_native_guard.py', build/'build-result.json', qe/'make.inc']
    files += sorted(build.rglob('*.a')) + sorted(qe.rglob('*.mod'))
    entries = [dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in files]
    command = ['/usr/bin/make', '-f', str(RESEARCH/'portable_gap/fresh_gap_initialization.mk'),
        'RESEARCH='+str(RESEARCH), 'QE_ROOT='+str(qe),
        'NATIVE_INPUT='+str(root/'native.in'), 'qualify-initialization']
    root.mkdir(parents=True)
    shutil.copy2(native_input, root/'native.in')
    entries.append(dict(path=str(root/'native.in'), bytes=native_input.stat().st_size, sha256=digest(native_input)))
    manifest = dict(cwd=str(root), command=command, files=entries, guard_seconds=180,
        launch_normal_seconds=120, retained_state_used=False,
        acceptance='Genuine upstream Q0 initialization and exact native schema roundtrip; no solved gap or Z',
        forecast='Below180s/3GiB; prior full initialization plus Coulomb read61s, Coulomb not needed here')
    (root/'run-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('build', 'inputs', 'native_input', 'destination'):
        p.add_argument(name, type=Path)
    print(json.dumps(stage(**vars(p.parse_args())), indent=2))
