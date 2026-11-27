"""Stage matched direct/cached partial Z sums on fresh Mac geometry at 8.05 K."""
import argparse
import json
from pathlib import Path
import shutil

from fetch_public_response_inputs import digest, validate
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def stage(build, z_build, initialization, inputs, destination):
    build, z_build, initialization, inputs, root = map(lambda p: Path(p).absolute(),
        (build, z_build, initialization, inputs, destination))
    if root.exists():
        raise ValueError('Fresh partial-Z directory required')
    parents = []
    for parent, label, token in [(z_build, 'zbuild', 'Z_QUALIFICATION_PASS checks=1200'),
            (initialization, 'init', 'FRESH_GAP_INITIALIZATION_ROUNDTRIP_PASS')]:
        protocol = parent/'run-manifest.json'; receipt = parent/'results'/label/'receipt.json'
        m = json.loads(protocol.read_text()); r = json.loads(receipt.read_text())
        if (r.get('status') != 'PASS' or r.get('exit') != 0 or r.get('error') is not None
                or r['command'] != m['command'] or r['cwd'] != str(parent)):
            raise ValueError('Unaccepted parent qualification')
        log = parent/'results'/label/'console.log'
        if log.read_text().count(token) != 1:
            raise ValueError('Incomplete parent qualification')
        verify_postrun_inputs(m, parent)
        parents += [protocol, receipt, log]
    accepted = RESEARCH/'fresh_gap_initialization_result.json'
    state = json.loads(accepted.read_text())
    if (state['retained_state_consumed'] or not state['exact_own_array_roundtrip']
            or digest(initialization/'native-init.bin') != state['state_sha256']
            or digest(initialization/'native-init.meta') != state['metadata_sha256']):
        raise ValueError('Changed fresh initialization state')
    files = parents+[accepted, initialization/'native-init.meta', initialization/'native-init.bin']
    for catalog in [RESEARCH/'public_response_inputs.json', RESEARCH/'public_gap_coulomb_inputs.json']:
        files.append(catalog)
        for name, item in json.loads(catalog.read_text())['files'].items():
            p = inputs/validate(name, item)
            if p.stat().st_size != item['bytes'] or digest(p) != item['sha256']:
                raise ValueError('Changed microscopic input: '+name)
            files.append(p)
    native = initialization/'native.in'
    if native.read_text().count("outdir='"+str(inputs)+"/'") != 1:
        raise ValueError('Different microscopic input directory')
    files += [native, Path(__file__), RESEARCH/'macos_native_guard.py',
        RESEARCH/'public_response_probe.mk', build/'build-result.json', build/'qe/make.inc']
    files += [RESEARCH/'portable_gap'/n for n in ('z_partial_driver.f90','prefix_operator.f90',
        'z_partial_source_provenance.json','z_partial.mk','z_build.mk','zsf_workspace.f90',
        'native_rotation.f90','slab_operator.f90','native_state_io.f90','native_coefficients.f90',
        'hash_stream.c','hash_pipe.c')]
    files += sorted(build.rglob('*.a'))+sorted((build/'qe').rglob('*.mod'))
    entries = [dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in files]
    root.mkdir(parents=True)
    shutil.copy2(native, root/'native.in')
    (root/'z-control.in').write_text(str(initialization)+'\n')
    for p in (root/'native.in', root/'z-control.in'):
        entries.append(dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)))
    command = ['/usr/bin/make','-f',str(RESEARCH/'portable_gap/z_partial.mk'),
        'RESEARCH='+str(RESEARCH),'QE_ROOT='+str(build/'qe'),
        'NATIVE_INPUT='+str(root/'native.in'),'qualify-partial']
    manifest = dict(cwd=str(root), command=command, files=entries, guard_seconds=300,
        launch_normal_seconds=120, temperature_kelvin=8.05, left_rows=256,
        acceptance='Four 64-row blocks, all right states; exact fresh geometry; both transformed channels; finite and bitwise equal direct/cached partial arrays; not full Z',
        forecast='Below300s/3GiB including build/input initialization and both arms; full-Z forecast requires these current measurements')
    (root/'run-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('build','z_build','initialization','inputs','destination'):
        p.add_argument(name, type=Path)
    print(json.dumps(stage(**vars(p.parse_args())), indent=2))
