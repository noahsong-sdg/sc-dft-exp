"""Read selected nonlinear-map diagnostics; no full-map/convergence inference."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def analyze(path):
    path = Path(path)
    lines = path.read_text().splitlines()
    if len(lines) != 6 or lines[0] != '# selected-nonlinear-map-v1; imposed seed; NOT a converged gap':
        raise ValueError('Expected complete selected-map diagnostic schema')
    dims = list(map(int, lines[1].split()))
    if len(dims) != 6 or min(dims) < 1 or dims[0] < 8 or dims[2] != max(dims[:2]):
        raise ValueError('Invalid selected-map dimensions')
    beta, zero_text, weight_error = lines[2].split()
    beta, zeros, weight_error = float(beta), int(zero_text), float(weight_error)
    if not all(map(math.isfinite, (beta, weight_error))) or beta <= 0 or not 0 <= weight_error <= 1e-14:
        raise ValueError('Invalid thermal reference check')
    if not 0 < zeros <= sum(dims[:2]):
        raise ValueError('Missing actual zero-energy product control')
    rows = []
    for line, expected_first in zip(lines[3:], (1, max(1, dims[0] // 2), dims[0] - 7)):
        fields = line.split()
        if len(fields) != 6:
            raise ValueError('Incomplete selected tile')
        first, last = map(int, fields[:2])
        values = list(map(float, fields[2:]))
        if first != expected_first or last != min(first + 7, dims[0]):
            raise ValueError('Selected tile positions changed')
        if not all(map(math.isfinite, values)) or min(values) < 0:
            raise ValueError('Invalid selected tile metrics')
        rows.append(dict(first=first, last=last, build_cpu_s=values[0],
                         explicit_sum_blas_max_absolute_difference=values[1],
                         sampled_uncached_coefficient_max_absolute_difference=values[2],
                         selected_residual_max_absolute_value=values[3]))
    return dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), dimensions=dims,
                beta=beta, exact_zero_energy_products=zeros,
                exponential_reference_max_absolute_difference=weight_error, tiles=rows,
                scope='Selected nonlinear Q0 map rows with imposed seed; native receipt needed for execution acceptance; no converged gap')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', type=Path)
    print(json.dumps(analyze(parser.parse_args().path), indent=2, allow_nan=False))
