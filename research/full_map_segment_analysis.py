"""Certify ordered partial images and exact state binding, not a physical response."""
import argparse
import array
import json
import math
from pathlib import Path
import sys

from compare_legacy_gap import native_arrays
from fetch_public_response_inputs import digest
from public_band_pilot_analysis import verify_postrun_inputs


def binary(path, count):
    path = Path(path)
    if sys.byteorder != 'little' or path.stat().st_size != 8*count:
        raise ValueError('Stale checkpoint binary shape or unsupported byte order')
    values = array.array('d')
    with path.open('rb') as source:
        values.fromfile(source, count)
    if not all(map(math.isfinite, values)):
        raise ValueError('Nonfinite checkpoint data')
    return values


def seed_context(root):
    meta = (root/'gap-seed.meta').read_text().splitlines()
    if len(meta) != 5 or meta[0] != 'gap-seed-v1; binary64 Fortran order':
        raise ValueError('Stale segment seed metadata')
    dims = list(map(int, meta[1].split())); beta = float(meta[2])
    if len(dims) != 6 or min(dims) < 1 or dims[2] != max(dims[:2]) or not math.isfinite(beta) or beta <= 0:
        raise ValueError('Invalid segment seed dimensions/temperature')
    geometry = Path(meta[3]); counts, state = native_arrays(geometry)
    # native-init reports nx, cell/band/fine-grid counts; it does not report nmf/ne.
    if counts[:4] != dims[:4]:
        raise ValueError('Segment seed/geometry dimensions differ')
    gap = binary(root/'gap-seed.bin', 2*dims[2])
    zmeta = (geometry/'full-z.meta').read_text().splitlines()
    if (len(zmeta) != 4 or zmeta[0] != 'native-Z-v1; binary64 Fortran order'
            or list(map(int, zmeta[1].split())) != [*dims[:4], 1]
            or float(zmeta[2].split()[0]) != beta or zmeta[3].strip() != 'F'):
        raise ValueError('Segment Z context differs')
    z = binary(geometry/'full-z.bin', len(gap))
    if any(1+x <= 0 for x in z):
        raise ValueError('Invalid segment Z denominator')
    return dims, beta, meta[4], (gap, state['xi'], state['dk'], z)


def checkpoint(root, counts, beta, context, completed, source_fields):
    lines = (root/'linear-image-checkpoint.meta').read_text().splitlines()
    if (len(lines) != 4 or lines[0] != 'ordered-linear-image-checkpoint-v1; unnormalized partial sums'
            or lines[1] != context or list(map(int, lines[2].split())) != [*counts, 4, completed]
            or float(lines[3]) != beta):
        raise ValueError('Stale ordered image metadata')
    meta = (root/'full-map-checkpoint.meta').read_text().splitlines()
    if len(meta) != 2 or meta[0] != 'ordered-full-map-checkpoint-v1; exact active state binding':
        raise ValueError('Stale full-map state schema')
    controls = list(map(float, meta[1].split()))
    if len(controls) != 3 or not all(map(math.isfinite, controls)) or controls[0] != 1e-8 or min(controls[1:]) < 0:
        raise ValueError('Invalid full-map checkpoint diagnostics')
    maximum = counts[2]; n = 2*maximum
    images = binary(root/'linear-image-checkpoint.bin', 4*n)
    state = binary(root/'full-map-checkpoint-state.bin', 8*n)
    for side, active in enumerate(counts[:2]):
        start = side*maximum
        for k in range(8):
            values = state[k*n+start:k*n+start+maximum]
            if any(values[active:]):
                raise ValueError('Nonzero checkpoint state padding')
            if k < 4 and values[:active].tobytes() != source_fields[k][start:start+active].tobytes():
                raise ValueError('Checkpoint state differs from declared source')
        for k in range(4):
            begin = completed if side == 0 else active
            if any(images[k*n+start+begin:k*n+start+maximum]):
                raise ValueError('Nonzero uncomputed checkpoint image rows')
    worst = 0.
    for side, active in enumerate(counts[:2]):
        for i in range(side*maximum, side*maximum+active):
            d, x, w, _ = (field[i] for field in source_fields)
            direction = (1 if side == 0 else -1)/math.sqrt(1+(x/.01)**2)
            def thermal(e):
                q = math.exp(-beta*e)
                return (1-q)/(1+q), 4*q/(1+q)**2
            def occupation(delta, initial=False):
                e = math.sqrt(x*x+delta*delta) if initial else math.hypot(x, delta)
                return w*delta/2/e*thermal(e)[0] if e else 0.
            e = math.hypot(x, d); t, sech = thermal(e)
            derivative = w*beta/4 if e == 0 else w/2*((x/e)**2*t/e+beta/2*(d/e)**2*sech)
            expected = [occupation(d, True), occupation(d+1e-8*direction),
                        occupation(d-1e-8*direction), derivative*direction]
            for k, value in enumerate(expected):
                worst = max(worst, abs(state[(k+4)*n+i]-value))
    if worst > 1e-14:
        raise ValueError('Independent occupation/derivative weights differ')
    sum_bound = 2e-13+2e-12*max(map(abs, images))
    if controls[1] > sum_bound:
        raise ValueError('Partial-image explicit-sum discrepancy exceeds control bound')
    names = ('linear-image-checkpoint.meta', 'linear-image-checkpoint.bin',
             'full-map-checkpoint.meta', 'full-map-checkpoint-state.bin')
    return dict(completed_rows=completed, dimensions=counts, beta=beta, step_ry=controls[0],
                tile_sum_max_absolute_difference=controls[1], cumulative_kernel_cpu_s=controls[2],
                partial_image_explicit_sum_bound=sum_bound,
                independent_weights_max_absolute_difference=worst, independent_weights_bound=1e-14,
                state_bitwise_matches_source=True, sha256={name: digest(root/name) for name in names})


def analyze(directory, manifest_path):
    root = Path(directory).absolute(); manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    if manifest['cwd'] != str(root) or manifest != json.loads((root/'run-manifest.json').read_text()):
        raise ValueError('Different public/consumed segment manifest')
    verify_postrun_inputs(manifest, root)
    receipt = json.loads((root/'results/moment/receipt.json').read_text())
    if (receipt.get('status') != 'PASS' or receipt.get('exit') != 0 or receipt.get('error') is not None
            or receipt['command'] != manifest['command'] or receipt['cwd'] != str(root)
            or receipt['guard_source_sha256'] != manifest['guard_source_sha256']
            or receipt['continuous_deadline_s'] != manifest['guard_seconds']):
        raise ValueError('No matching terminal segment PASS receipt')
    if (not math.isfinite(receipt['wall_s']) or not 0 <= receipt['wall_s'] < manifest['guard_seconds']
            or not 0 <= receipt['max_individual_descendant_rss_bytes'] <= 3221225472
            or not 0 <= receipt['sampled_peak_group_rss_bytes'] <= 3221225472):
        raise ValueError('Invalid segment resource receipt')
    context = manifest['evaluation_context_sha256']
    recipe_file = root/'evaluation-context.json'
    recipe = json.loads(recipe_file.read_text())
    if (digest(recipe_file) != context or recipe['schema'] != 'ordered-full-map-evaluation-v1'
            or recipe['candidate_sha256'] != manifest['candidate_sha256']
            or recipe['operator_context_sha256'] != manifest['operator_context_sha256']
            or recipe['executable_sha256'] != digest(root/'verify-gap-seed.x')):
        raise ValueError('Different declared evaluation identity')
    pins = {item['path']: item for item in manifest['files']}
    for key in ('seed_manifest', 'build_manifest', 'build_qualification'):
        ancestor = recipe[key]
        if digest(Path(ancestor['path'])) != ancestor['sha256']:
            raise ValueError('Changed evaluation ancestor')
        for item in json.loads(Path(ancestor['path']).read_text()).get('files', []):
            if pins.get(item['path']) != item:
                raise ValueError('Incomplete evaluation ancestor input closure')
    control = (root/'full-map-segment.in').read_text().splitlines()
    expected = ['ordered-full-map-control-v1', context, manifest['previous_directory'],
                f"{manifest['completed_rows']} {manifest['last_row']}", manifest['mode']]
    if control != expected:
        raise ValueError('Changed segment control')
    dims, beta, operator, fields = seed_context(root)
    if digest(root/'gap-seed.bin') != manifest['candidate_sha256'] or operator != manifest['operator_context_sha256']:
        raise ValueError('Changed segment candidate/operator')
    if ((root/'map-control.in').read_text().strip() != (root/'gap-seed.meta').read_text().splitlines()[3]
            or (root/'seed-control.in').read_text().splitlines() != [str(root), operator]):
        raise ValueError('Different native geometry/seed control')
    completed, last = manifest['completed_rows'], manifest['last_row']
    if (manifest['mode'] not in ('qualify', 'segment') or not 0 <= completed < last <= dims[0]
            or completed % 32 or (last != dims[0] and last % 32)):
        raise ValueError('Invalid declared ordered segment range')
    main = checkpoint(root, dims[:3], beta, context, manifest['last_row'], fields)
    split = None
    if manifest['mode'] == 'qualify':
        if manifest['completed_rows'] != 0 or manifest['last_row'] != 64 or manifest['previous_directory'] != '-':
            raise ValueError('Different split qualification range')
        console = (root/'results/moment/console.log').read_text().splitlines()
        if console.count('FULL_MAP_SPLIT_BITWISE_PASS') != 1:
            raise ValueError('Missing native continuous-versus-restarted equality assertion')
        split = checkpoint(root/'split', dims[:3], beta, context, 32, fields)
        if main['sha256']['full-map-checkpoint-state.bin'] != split['sha256']['full-map-checkpoint-state.bin']:
            raise ValueError('Split checkpoint state changed')
        if (main['tile_sum_max_absolute_difference'] < split['tile_sum_max_absolute_difference']
                or main['cumulative_kernel_cpu_s'] < split['cumulative_kernel_cpu_s']):
            raise ValueError('Split diagnostics were not carried forward')
    if manifest['mode'] == 'qualify' or manifest['last_row'] < dims[0]:
        if (root/'full-map.bin').exists() or (root/'full-map.txt').exists():
            raise ValueError('Partial segment unexpectedly emits full-map output')
    return dict(terminal_guard_pass=True, inputs_unchanged=True, verified_input_count=len(manifest['files']),
                checkpoint=main, split_checkpoint=split, receipt=receipt,
                microscopic_split_qualified=split is not None, full_native_residual_verified=False,
                physical_response_verified=False, manifest_sha256=digest(manifest_path), scope=__doc__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path); parser.add_argument('manifest_path', type=Path)
    print(json.dumps(analyze(**vars(parser.parse_args())), indent=2, allow_nan=False))
