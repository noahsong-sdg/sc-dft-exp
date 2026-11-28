"""Independent declared-step checkpoint arithmetic; owning provenance separate."""
import math
from pathlib import Path

from fetch_public_response_inputs import digest
from full_map_segment_analysis import binary


def declared(root, counts, beta, operator, source_fields):
    root = Path(root)
    meta = (root/'direction-state.meta').read_text().splitlines()
    if (len(meta) != 4 or meta[0] != 'declared-full-map-direction-v1'
            or list(map(int,meta[1].split())) != list(counts)
            or float(meta[2]) != beta or meta[3] != operator):
        raise ValueError('Stale declared checkpoint direction metadata')
    n = 2*counts[2]
    state = binary(root/'direction-state.bin',2*n)
    if state[:n].tobytes() != source_fields[0].tobytes():
        raise ValueError('Declared direction candidate differs bitwise')
    direction = state[n:]
    if max(map(abs,direction)) != 1:
        raise ValueError('Declared direction requires unit infinity norm')
    for side,count in enumerate(counts[:2]):
        if any(direction[side*counts[2]+count:(side+1)*counts[2]]):
            raise ValueError('Nonzero declared direction padding')
    control = (root/'full-map-step.in').read_text().splitlines()
    if len(control) != 2 or control[0] != 'declared-full-map-step-v1':
        raise ValueError('Stale declared checkpoint step')
    step = float(control[1])
    if not math.isfinite(step) or not 0 < step or not math.isfinite(2*step):
        raise ValueError('Invalid declared checkpoint step')
    return dict(direction=direction,step=step,
                sha256={name:digest(root/name) for name in
                        ('direction-state.meta','direction-state.bin','full-map-step.in')})


def checkpoint(root, counts, beta, context, completed, source_fields, direction, step):
    n = 2*counts[2]
    if (len(source_fields) != 4 or any(len(x) != n for x in source_fields) or len(direction) != n
            or not math.isfinite(step) or step <= 0 or not all(map(math.isfinite,direction))
            or max(map(abs,direction)) != 1):
        raise ValueError('Invalid declared checkpoint state shape/step')
    lines = (root/'linear-image-checkpoint.meta').read_text().splitlines()
    if (len(lines) != 4 or lines[0] != 'ordered-linear-image-checkpoint-v1; unnormalized partial sums'
            or lines[1] != context or list(map(int, lines[2].split())) != [*counts, 4, completed]
            or float(lines[3]) != beta):
        raise ValueError('Stale ordered image metadata')
    meta = (root/'full-map-checkpoint.meta').read_text().splitlines()
    if len(meta) != 2 or meta[0] != 'declared-step-full-map-checkpoint-v1; exact active state binding':
        raise ValueError('Stale full-map state schema')
    controls = list(map(float, meta[1].split()))
    if len(controls) != 3 or not all(map(math.isfinite, controls)) or controls[0] != step or min(controls[1:]) < 0:
        raise ValueError('Invalid full-map checkpoint diagnostics')
    maximum = counts[2]; n = 2*maximum
    images = binary(root/'linear-image-checkpoint.bin', 4*n)
    state = binary(root/'full-map-checkpoint-state.bin', 8*n)
    for side, active in enumerate(counts[:2]):
        start = side*maximum
        if any(direction[start+active:start+maximum]):
            raise ValueError('Nonzero checkpoint direction padding')
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
            v = direction[i]
            def thermal(e):
                q = math.exp(-beta*e)
                return (1-q)/(1+q), 4*q/(1+q)**2
            def occupation(delta, initial=False):
                e = math.sqrt(x*x+delta*delta) if initial else math.hypot(x, delta)
                return w*delta/2/e*thermal(e)[0] if e else 0.
            e = math.hypot(x, d); t, sech = thermal(e)
            derivative = w*beta/4 if e == 0 else w/2*((x/e)**2*t/e+beta/2*(d/e)**2*sech)
            expected = [occupation(d, True), occupation(d+step*v),
                        occupation(d-step*v), derivative*v]
            if not all(map(math.isfinite,expected)):
                raise ValueError('Nonfinite independent occupation/derivative')
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

