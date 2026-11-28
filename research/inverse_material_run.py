"""Own a fresh inverse diagnostic; arithmetic is not a full-space certificate."""
import json
from pathlib import Path
import subprocess
import time

from fetch_public_response_inputs import digest
from full_map_segments import certify, recorded_result
from low_rank_inverse_analysis import analyze

OUTPUTS = ('inverse-result.txt', 'inverse-result.bin', 'inverse-readback.json')


def identity(path):
    path = Path(path)
    return dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))


def check_pins(manifest):
    pins = {}
    for item in manifest['files']:
        if item['path'] in pins or identity(item['path']) != item:
            raise ValueError('Duplicate or changed inverse input')
        pins[item['path']] = item
    return pins


def require(pins, paths):
    for path in paths:
        if pins.get(str(path)) != identity(path):
            raise ValueError('Missing inverse provenance binding')


def parent(pins, path):
    path = Path(path)
    require(pins, (path,))
    manifest = json.loads(path.read_text())
    for item in manifest['files']:
        if pins.get(item['path']) != item:
            raise ValueError('Incomplete inverse parent closure')
    return manifest


def validate(root):
    manifest_path = root/'run-manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest['cwd'] != str(root) or Path.cwd() != root:
        raise ValueError('Different inverse owner directory')
    pins = check_pins(manifest)
    require(pins, (Path(__file__).resolve(), root/'inverse-control.in', root/'inverse-actions.x'))
    build_path = Path(manifest['build_manifest']); full_path = Path(manifest['full_manifest'])
    build = parent(pins, build_path); full = parent(pins, full_path)
    build_root, full_root = Path(build['cwd']), Path(full['cwd'])
    build_result_path = Path(manifest['build_result']); full_result_path = Path(manifest['full_result'])
    require(pins, (build_result_path, full_result_path, build_root/'run-manifest.json',
                   build_root/'results/build/receipt.json', build_root/'build-plan.txt',
                   *(build_root/name for name in json.loads(build_result_path.read_text())['outputs']),
                   full_root/'run-manifest.json', full_root/'results/moment/receipt.json',
                   *(full_root/name for name in ('full-map.txt', 'full-map.bin', 'gap-seed.meta', 'gap-seed.bin'))))
    if build_path.read_bytes() != (build_root/'run-manifest.json').read_bytes():
        raise ValueError('Different consumed inverse build manifest')
    result = json.loads(build_result_path.read_text())
    receipt = json.loads((build_root/'results/build/receipt.json').read_text())
    if (result.get('status') != 'PASS' or result.get('inputs_unchanged') is not True
            or result.get('build_plan_matches_console') is not True
            or result.get('historical_custom_objects_used') is not False
            or result['manifest_sha256'] != digest(build_path) or result['receipt'] != receipt
            or receipt['status'] != 'PASS' or receipt['exit'] != 0 or receipt['error'] is not None
            or receipt['command'] != build['command'] or receipt['cwd'] != build['cwd']
            or receipt['guard_source_sha256'] != build['guard_source_sha256']
            or receipt['continuous_deadline_s'] != build['guard_seconds']
            or not 0 < receipt['wall_s'] < build['guard_seconds']
            or result['executable_sha256'] != digest(root/'inverse-actions.x')):
        raise ValueError('Unqualified inverse executable')
    for name, sha in result['outputs'].items():
        if digest(build_root/name) != sha:
            raise ValueError('Changed inverse build output')
    checked = certify(full_path)
    recorded_result(full_result_path, checked)
    recorded = json.loads(full_result_path.read_text())
    if (checked.get('complete_left_row_coverage') is not True
            or checked.get('full_native_residual_verified') is not True
            or recorded.get('full_candidate') != checked['full_candidate']):
        raise ValueError('Unaccepted inverse full candidate')
    reduced = Path(manifest['reduced_directory'])
    require(pins, (reduced/'reduced-control.in', reduced/'reduced-gap.bin'))
    control = (root/'inverse-control.in').read_text().splitlines()
    reduced_control = (reduced/'reduced-control.in').read_text().splitlines()
    if (len(control) != 7 or control[0] != 'low-rank-inverse-control-v1'
            or len(reduced_control) != 5 or control[1:3] != reduced_control[:2]
            or control[3] != str(full_root) or control[4] != reduced_control[3]
            or float(control[5]) != float(reduced_control[4].split()[0])
            or digest(reduced/'reduced-gap.bin') != digest(full_root/'gap-seed.bin')):
        raise ValueError('Different inverse reduced candidate or context')
    basis_meta = Path(control[1])/'basis.meta'
    require(pins, (basis_meta, Path(control[1])/'basis.bin'))
    if control[6] != basis_meta.read_text().splitlines()[4]:
        raise ValueError('Different inverse basis configuration')
    return manifest


def run(root):
    root = Path(root).absolute()
    if any((root/name).exists() for name in OUTPUTS):
        raise ValueError('Inverse diagnostic requires fresh outputs')
    manifest_bytes = (root/'run-manifest.json').read_bytes()
    started = time.monotonic()
    print('Validating inverse source lineage', flush=True)
    manifest = validate(root)
    validated = time.monotonic()
    print('Running source-built inverse actions', flush=True)
    subprocess.run([str(root/'inverse-actions.x')], cwd=root, check=True)
    native_done = time.monotonic()
    print('Reading every inverse matrix entry and both actions', flush=True)
    result = analyze(root)
    check_pins(manifest)
    if (root/'run-manifest.json').read_bytes() != manifest_bytes:
        raise ValueError('Changed inverse owner manifest')
    result.update(inputs_unchanged=True, manifest_sha256=digest(root/'run-manifest.json'),
                  validation_s=validated-started, native_s=native_done-validated,
                  readback_s=time.monotonic()-native_done,
                  terminal_guard_pass=False,
                  scope='Arithmetic and lineage readback; owning terminal guard still required. No full-space gap or physical response bound.')
    (root/'inverse-readback.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Inverse arithmetic readback complete; terminal guard pending', flush=True)
    return result


if __name__ == '__main__':
    run(Path.cwd())
