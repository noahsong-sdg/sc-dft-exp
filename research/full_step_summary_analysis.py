"""Strict readback of a full imposed-seed residual; not a convergence certificate."""
import argparse
import json
import math
import sys
from fetch_public_response_inputs import digest
from pathlib import Path
import array


def analyze(directory):
    root = Path(directory)
    declared = (root/'full-map-step.in').read_text().splitlines()
    if len(declared) != 2 or declared[0] != 'declared-full-map-step-v1':
        raise ValueError('Invalid declared step control')
    declared_step = float(declared[1])
    if not math.isfinite(declared_step) or declared_step <= 0:
        raise ValueError('Invalid declared step value')
    summary, binary = root / 'full-map.txt', root / 'full-map.bin'
    lines = summary.read_text().splitlines()
    if len(lines) != 5 or lines[0] != '# full-nonlinear-map-v1; imposed seed; NOT a converged gap':
        raise ValueError('Incomplete or unsupported full-map summary')
    dims = list(map(int, lines[1].split()))
    if len(dims) != 4 or min(dims) < 1 or dims[2] != max(dims[:2]) or dims[3] != 4:
        raise ValueError('Invalid full-map dimensions/batches')
    controls = list(map(float, lines[2].split()))
    if len(controls) != 6 or not all(map(math.isfinite, controls)) or min(controls) < 0:
        raise ValueError('Invalid full-map controls')
    beta, step, cpu, sum_error, fd_error, fd_bound = controls
    if beta <= 0 or step != declared_step or fd_error > fd_bound:
        raise ValueError('Invalid derivative comparison')
    maximum = dims[2]
    if binary.stat().st_size != 64 * maximum:
        raise ValueError('Stale full-map binary shape')
    if sys.byteorder != 'little':
        raise ValueError('Native summary requires little-endian binary64')
    arrays = array.array('d')
    with binary.open('rb') as source:
        arrays.fromfile(source,8*maximum)
    if not all(map(math.isfinite, arrays)):
        raise ValueError('Nonfinite full-map binary')
    sides = []
    image_scale = 0
    for g, count in enumerate(dims[:2]):
        fields = list(map(float, lines[g + 3].split()))
        if len(fields) != 4 or fields[0] != g + 1 or min(fields[1:]) < 0 or not all(map(math.isfinite, fields)):
            raise ValueError('Invalid side summary')
        blocks = [arrays[(2 * a + g) * maximum:(2 * a + g + 1) * maximum] for a in range(4)]
        if any(value != 0 for block in blocks for value in block[count:]):
            raise ValueError('Nonzero persisted padding')
        residual, jacobian = blocks[1][:count], blocks[3][:count]
        image_scale = max(image_scale, max(abs(a+b) for a,b in zip(residual, blocks[0][:count])))
        expected = (max(map(abs, residual)), math.sqrt(math.fsum(x*x for x in residual)/count),
                    max(map(abs, jacobian)))
        if any(not math.isclose(a, b, rel_tol=2e-13, abs_tol=1e-18) for a, b in zip(fields[1:], expected)):
            raise ValueError('Summary/binary residual disagreement')
        sides.append(dict(side=g+1, max_absolute_residual_ry=expected[0], rms_residual_ry=expected[1],
                          max_absolute_jacobian_action=expected[2]))
    expected_bound = 1e-8 + 2e-6 * max(side['max_absolute_jacobian_action'] for side in sides)
    if not math.isclose(fd_bound, expected_bound, rel_tol=2e-13, abs_tol=1e-18):
        raise ValueError('Changed Jacobian acceptance bound')
    if sum_error > 2e-13 + 2e-12 * image_scale:
        raise ValueError('Tile explicit-sum check failed')
    return dict(dimensions=dims, beta=beta, finite_difference_step_ry=step, kernel_cpu_s=cpu,
                tile_sum_max_absolute_difference=sum_error, jacobian_difference=fd_error,
                jacobian_acceptance_bound=fd_bound, sides=sides,
                sha256={p.name: digest(p) for p in (summary, binary)},
                scope='Full native Q0 residual at imposed seed; terminal receipt required; no gap convergence or physical response validation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    print(json.dumps(analyze(parser.parse_args().directory), indent=2, allow_nan=False))
