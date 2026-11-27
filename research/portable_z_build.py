"""Stage source-only Z cache qualification and slab interface compilation."""
import argparse
import json
from pathlib import Path

from fetch_public_response_inputs import digest

RESEARCH = Path(__file__).resolve().parent


def stage(build, destination):
    build, root = map(lambda p: Path(p).absolute(), (build, destination))
    if root.exists():
        raise ValueError('Fresh Z build directory required')
    parent = build/'build-result.json'
    if json.loads(parent.read_text())['source_manifest_sha256'] != digest(RESEARCH/'public_response_sources.json'):
        raise ValueError('Different public source build')
    proof = RESEARCH/'portable_gap/z_source_provenance.json'
    for name, item in json.loads(proof.read_text()).items():
        if digest(RESEARCH/'portable_gap'/name) != item['sha256']:
            raise ValueError('Changed migrated Z source: '+name)
    qe = build/'qe'
    files = [RESEARCH/'portable_gap'/n for n in ('zsf_workspace.f90','slab_z.f90',
        'z_qualification.f90','native_rotation.f90','slab_operator.f90','z_build.mk')]
    files += [proof, parent, qe/'make.inc', Path(__file__),
        RESEARCH/'public_response_sources.json', RESEARCH/'public_response_probe.mk',
        RESEARCH/'macos_native_guard.py']
    files += sorted(build.rglob('*.a')) + sorted(qe.rglob('*.mod'))
    entries = [dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in files]
    command = ['/usr/bin/make', '-f', str(RESEARCH/'portable_gap/z_build.mk'),
        'RESEARCH='+str(RESEARCH), 'QE_ROOT='+str(qe), 'qualify-z']
    manifest = dict(cwd=str(root), command=command, files=entries,
        guard_seconds=120, launch_normal_seconds=120, historical_objects_used=False,
        acceptance='1200 bitwise direct upstream Zsf checks, context changes and forced collisions; slab compilation only',
        forecast='Small source compile/link plus1200scalarchecks; below120s/3GiB; no full Z')
    root.mkdir(parents=True)
    (root/'run-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('build', type=Path); p.add_argument('destination', type=Path)
    print(json.dumps(stage(**vars(p.parse_args())), indent=2))
