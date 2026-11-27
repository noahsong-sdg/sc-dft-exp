"""Audit scalar-gap invariance on native cell orbits; not a response certificate."""
import argparse
import array
from collections import Counter
import json
import math
from pathlib import Path
import sys

from compare_legacy_gap import digest, native_arrays
from reduced_nonlinear_analysis import analyze as reduced_readback

HEADER = '# response-cell-rotations-v1; integer native matrices in Fortran order'


def read_rotations(path):
    lines = Path(path).read_text().splitlines()
    if not lines or lines[0] != HEADER:
        raise ValueError('Stale cell rotation schema')
    fields = list(map(int, lines[1].split())) if len(lines) > 1 else []
    if (len(fields) != 7 or not 1 <= fields[0] <= 192 or min(fields[1:4]) < 1
            or len(set(fields[1:4])) != 1 or fields[4:] != [1, 1, 1]
            or len(lines) != fields[0]+2):
        raise ValueError('Expected cubic cells and fully shifted second grid')
    rotations = []
    for line in lines[2:]:
        flat = list(map(int, line.split()))
        if len(flat) != 9:
            raise ValueError('Incomplete native rotation')
        m = tuple(tuple(flat[a+3*b] for b in range(3)) for a in range(3))
        determinant = sum(m[0][i]*(m[1][(i+1)%3]*m[2][(i+2)%3]
                          - m[1][(i+2)%3]*m[2][(i+1)%3]) for i in range(3))
        if abs(determinant) != 1 or m in rotations:
            raise ValueError('Invalid or duplicate native rotation')
        rotations.append(m)
    if ((1, 0, 0), (0, 1, 0), (0, 0, 1)) not in rotations:
        raise ValueError('Native rotations lack identity')
    return fields[1], rotations


def mapped_cell(cell, side, size, rotation):
    """Exact integer version of native symm_dosk's shifted-cell mapping."""
    k = cell-1
    indices = [k//(size*size), k//size % size, k % size]
    doubled = [2*i+side for i in indices]
    shifted = [sum(a*b for a, b in zip(row, doubled))-side for row in rotation]
    if any(i % 2 for i in shifted):
        return None  # Native path also skips operations off this cell grid.
    i, j, k = [(value//2) % size for value in shifted]
    return 1+k+size*j+size*size*i


def audit_records(records, size, rotations):
    """Records: (side, cell, band, energy-label) -> (xi, weight, scalar gap)."""
    if not records:
        raise ValueError('Empty scalar-gap orbit audit')
    for key, values in records.items():
        if (len(key) != 4 or key[0] not in (0, 1) or not 1 <= key[1] <= size**3
                or key[2] < 1 or len(values) != 3 or not all(map(math.isfinite, values))):
            raise ValueError('Invalid scalar-gap orbit record')
    scale = max(abs(values[2]) for values in records.values())
    if scale == 0:
        raise ValueError('Nonzero candidate required')
    comparisons = missing = skipped = geometry_failures = 0
    energy_error = weight_error = gap_error = 0.
    tolerance = 64*sys.float_info.epsilon
    for (side, cell, band, label), values in records.items():
        for rotation in rotations:
            target = mapped_cell(cell, side, size, rotation)
            if target is None:
                skipped += 1
                continue
            other = records.get((side, target, band, label))
            if other is None:
                missing += 1
                continue
            comparisons += 1
            differences = [abs(a-b) for a, b in zip(values, other)]
            energy_error = max(energy_error, differences[0])
            weight_error = max(weight_error, differences[1])
            gap_error = max(gap_error, differences[2])
            geometry_failures += any(differences[i] > tolerance*max(abs(values[i]), abs(other[i]))
                                     for i in (0, 1))
    geometry_ok = missing == 0 and geometry_failures == 0
    return dict(states=len(records), rotations=len(rotations), mapped_comparisons=comparisons,
                missing_orbit_records=missing, noncommensurate_operations_skipped=skipped,
                geometry_comparisons_beyond_64eps=geometry_failures,
                max_energy_difference_ry=energy_error, max_weight_difference=weight_error,
                max_gap_difference_ry=gap_error, max_gap_difference_over_global_max=gap_error/scale,
                geometry_orbits_compatible=geometry_ok,
                gap_symmetry_test_passed=geometry_ok and gap_error/scale <= 1e-10,
                gap_relative_tolerance=1e-10, physical_response_verified=False)


def audit_values(gap, prepare, symmetry_file):
    """Audit supplied gap-shaped values in Ry on the declared native geometry."""
    prepare, symmetry_file = map(Path, (prepare, symmetry_file))
    size, rotations = read_rotations(symmetry_file)
    counts, state = native_arrays(prepare)
    if size**3 != counts[4]:
        raise ValueError('Cell rotations belong to a different geometry')
    if len(gap) != 2*counts[2] or not all(map(math.isfinite, gap)):
        raise ValueError('Invalid gap-shaped orbit vector')
    nodes = {x: i for i, x in enumerate(state['xi0'])}
    records = {}
    for side, count in enumerate(counts[:2]):
        start = side*counts[2]
        if any(gap[start+count:start+counts[2]]):
            raise ValueError('Nonzero gap-shaped orbit padding')
        groups = Counter((state['kindx'][i], state['bindx'][i]) for i in range(start, start+count))
        for i in range(start, start+count):
            cell, band = state['kindx'][i], state['bindx'][i]
            label = nodes.get(state['xi'][i]) if groups[cell, band] > 1 else -1
            if label is None:
                raise ValueError('Resolved native state is not an exact energy node')
            key = side, cell, band, label
            if key in records:
                raise ValueError('Duplicate native orbit key')
            records[key] = state['xi'][i], state['dk'][i], gap[i]
    result = audit_records(records, size, rotations)
    result.update(scope=audit_values.__doc__,
                  sha256={str(p): digest(p) for p in (symmetry_file, prepare/'native-init.meta',
                      prepare/'native-init.bin')})
    return result


def analyze(candidate, prepare, symmetry_file):
    candidate = Path(candidate)
    checked = reduced_readback(candidate, prepare)
    gap = array.array('d')
    gap.frombytes((candidate/'reduced-gap.bin').read_bytes())
    result = audit_values(gap, prepare, symmetry_file)
    result.update(reduced_readback=checked, scope=__doc__)
    result['sha256'][str(candidate/'reduced-gap.bin')] = digest(candidate/'reduced-gap.bin')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('candidate', 'prepare', 'symmetry_file'):
        parser.add_argument(name, type=Path)
    print(json.dumps(analyze(**vars(parser.parse_args())), indent=2, allow_nan=False))
