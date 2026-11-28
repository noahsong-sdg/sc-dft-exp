"""Arithmetic readback only; terminal/provenance required; no full-space bound."""
import argparse
import array
import json
import math
from pathlib import Path
import sys

from compare_legacy_gap import native_arrays
from fetch_public_response_inputs import digest
from full_nonlinear_analysis import analyze as full_readback


def values(path, count):
    if Path(path).stat().st_size != 8*count:
        raise ValueError('Stale inverse binary size')
    result = array.array('d')
    with Path(path).open('rb') as source:
        result.fromfile(source, count)
    if not all(map(math.isfinite, result)):
        raise ValueError('Nonfinite inverse binary')
    return result


def analyze(directory):
    if sys.byteorder != 'little':
        raise ValueError('Native inverse payload requires little-endian binary64')
    root = Path(directory)
    control = (root/'inverse-control.in').read_text().splitlines()
    if len(control) != 7 or control[0] != 'low-rank-inverse-control-v1':
        raise ValueError('Unsupported inverse control')
    basis, geometry, full = map(Path, control[1:4]); context = control[4]
    beta = float(control[5]); config = list(map(int, control[6].split()))
    meta = (basis/'basis.meta').read_text().splitlines()
    seed = (full/'gap-seed.meta').read_text().splitlines()
    if len(meta) != 5 or meta[0] != 'tc-basis-v1' or len(seed) != 5 or seed[0] != 'gap-seed-v1; binary64 Fortran order':
        raise ValueError('Unsupported inverse source metadata')
    n, rank = map(int, meta[1].split()); counts, native = native_arrays(geometry)
    seed_dims = list(map(int, seed[1].split()))
    if (not math.isfinite(beta) or beta <= 0 or len(context) != 64
            or any(c not in '0123456789abcdef' for c in context)
            or not 1 <= rank <= min(n, 64) or n != 2*counts[2]
            or float(meta[2]) != beta or meta[3] != context
            or list(map(int, meta[4].split())) != config or len(config) != 6
            or len(seed_dims) != 6 or min(seed_dims) <= 0 or seed_dims[:4] != counts[:4]
            or config != [counts[3], seed_dims[4], config[2], 2, *counts[:2]]
            or float(seed[2]) != beta or seed[3] != str(geometry) or seed[4] != context):
        raise ValueError('Different inverse source context')
    checked = full_readback(full)
    if checked['beta'] != beta or checked['dimensions'] != [*counts[:3], 4]:
        raise ValueError('Different inverse full-map state')
    source = values(full/'full-map.bin', 4*n)
    gap, residual, direction, native_jv = [source[k*n:(k+1)*n] for k in range(4)]
    if gap.tobytes() != (full/'gap-seed.bin').read_bytes():
        raise ValueError('Different inverse candidate')
    ratios = []
    for g, count in enumerate(counts[:2]):
        indices = range(g*counts[2], g*counts[2]+count)
        gap_norm = math.sqrt(math.fsum(gap[i]**2 for i in indices))
        if gap_norm == 0:
            raise ValueError('Zero inverse source gap')
        ratios.append(math.sqrt(math.fsum(residual[i]**2 for i in indices))/gap_norm)
    ratio = max(ratios)
    if max(map(abs, residual)) > 1e-10 or ratio > 1e-5 or max(map(abs, direction)) == 0:
        raise ValueError('Inverse source residual gate failed')
    lines = (root/'inverse-result.txt').read_text().splitlines()
    if len(lines) != 4 or lines[0] != '# low-rank-inverse-v1; DIAGNOSTIC; NO full-space bound':
        raise ValueError('Unsupported inverse summary')
    if list(map(int, lines[1].split())) != [n, rank, *counts[:3]]:
        raise ValueError('Different inverse result dimensions')
    controls, reported = [list(map(float, line.split())) for line in lines[2:]]
    if (len(controls) != 5 or len(reported) != 4 or not all(map(math.isfinite, controls+reported))
            or min(controls+reported) < 0 or controls[0] != beta or controls[1] > 1e-10 or controls[4] <= 0):
        raise ValueError('Invalid inverse summary values')
    data = values(root/'inverse-result.bin', 3*n+rank*rank+rank)
    diagonal, correction, probe = [data[k*n:(k+1)*n] for k in range(3)]
    small = data[3*n:3*n+rank*rank]; singular = data[3*n+rank*rank:]
    expected_d = []
    for x, delta in zip(native['xi'], gap):
        energy = math.hypot(x, delta); tail = math.exp(-beta*energy)
        tx = math.expm1(-beta*abs(x)); te = math.expm1(-beta*energy)
        denominator = -tx/(2+tx)/abs(x) if x else beta/2
        expected_d.append(((x/energy)**2*(-te/(2+te))/energy
                           +beta/2*(delta/energy)**2*4*tail/(1+tail)**2)/denominator if energy else 1.)
    for side, count in enumerate(counts[:2]):
        padding = slice(side*counts[2]+count, (side+1)*counts[2])
        expected_d[padding] = [0.]*(counts[2]-count)
        if any(v != 0 for vector in (diagonal, correction, probe) for v in vector[padding]):
            raise ValueError('Nonzero inverse output padding')
    derivative_error = max(abs(a-b) for a, b in zip(diagonal, expected_d))
    if derivative_error > 3e-13:
        raise ValueError('Independent occupation derivative differs')
    if (basis/'basis.bin').stat().st_size != 16*n*rank:
        raise ValueError('Stale inverse basis size')
    columns = []
    with (basis/'basis.bin').open('rb') as stream:
        for _ in range(2*rank):
            col = array.array('d'); col.fromfile(stream, n)
            if not all(map(math.isfinite, col)):
                raise ValueError('Nonfinite inverse basis')
            columns.append(col)
    q, u = columns[:rank], columns[rank:]
    for side, count in enumerate(counts[:2]):
        if any(v != 0 for col in columns for v in col[side*counts[2]+count:(side+1)*counts[2]]):
            raise ValueError('Nonzero inverse basis padding')
    matrix_error = 0.
    for j in range(rank):
        for i in range(rank):
            expected = float(i == j)-math.fsum(q[i][k]*diagonal[k]*u[j][k] for k in range(n))
            error = abs(small[j*rank+i]-expected); matrix_error = max(matrix_error, error)
            if error > 2e-13+2e-12*abs(expected):
                raise ValueError('Independent small matrix differs')
    if (min(singular) <= 0 or not math.isfinite(singular[0]/singular[-1])
            or list(singular) != sorted(singular, reverse=True)
            or not math.isclose(controls[3], singular[0], rel_tol=2e-13)
            or not math.isclose(controls[4], singular[-1], rel_tol=2e-13)
            or not math.isclose(math.fsum(x*x for x in small), math.fsum(x*x for x in singular), rel_tol=2e-12, abs_tol=1e-25)):
        raise ValueError('Inconsistent small singular values')
    action_errors, action_bounds = [], []
    for vector, rhs in ((correction, residual), ([a+b for a, b in zip(probe, direction)], [-x for x in native_jv])):
        coefficients = [math.fsum(col[i]*diagonal[i]*vector[i] for i in range(n)) for col in q]
        image = [math.fsum(u[k][i]*coefficients[k] for k in range(rank)) for i in range(n)]
        error = max(abs(a-b-c) for a, b, c in zip(vector, image, rhs)); action_errors.append(error)
        scale = max(abs(v) for block in (vector, image, rhs) for v in block)
        action_bounds.append(1e-30+1e-10*scale)
        if error > action_bounds[-1]:
            raise ValueError('Independent inverse action differs')
    if controls[2] > max(action_bounds):
        raise ValueError('Driver inverse residual exceeds algebraic tolerance')
    expected = [max(map(abs, residual)), max(map(abs, correction)),
                max(map(abs, correction))/max(map(abs, gap)), max(map(abs, probe))/max(map(abs, direction))]
    if any(not math.isclose(a, b, rel_tol=2e-13, abs_tol=1e-25) for a, b in zip(reported, expected)):
        raise ValueError('Inverse summary/binary disagreement')
    inputs = [root/'inverse-control.in', basis/'basis.meta', basis/'basis.bin', geometry/'native-init.meta',
              geometry/'native-init.bin', *(full/name for name in ('gap-seed.meta', 'gap-seed.bin', 'full-map.txt', 'full-map.bin'))]
    return dict(dimensions=[n, rank, *counts[:3]], beta=beta, residual_infinity_ry=expected[0],
                correction_infinity_ry=expected[1], correction_over_gap_infinity=expected[2],
                native_probe_defect_ratio=expected[3], small_matrix_condition_ratio=singular[0]/singular[-1],
                small_singular_values=list(singular), independent_derivative_max_error=derivative_error,
                independent_matrix_max_error=matrix_error, independent_action_max_errors=action_errors,
                driver_model_inverse_residual=controls[2], full_source_residual_targets_met=True,
                conditioned_gap_error_bounded=False, physical_response_verified=False,
                inputs_sha256={str(p): digest(p) for p in inputs},
                outputs_sha256={name: digest(root/name) for name in ('inverse-result.txt', 'inverse-result.bin')}, scope=__doc__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    print(json.dumps(analyze(parser.parse_args().directory), indent=2, allow_nan=False))
