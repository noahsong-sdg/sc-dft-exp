"""Bound symmetry-averaging effects on a candidate's resolved-support response."""
import argparse
import array
from collections import Counter, defaultdict
import json
import math
import re
from pathlib import Path
import sys

from cell_moment_cache import FIELDS, read_pair
from compare_legacy_gap import digest, native_arrays
from gap_symmetry_audit import mapped_cell, read_rotations
from linear_response import sech2, stiffness
from moment_analysis import analyze as moment_controls
from reduced_nonlinear_analysis import analyze as reduced_readback
from response_assignment_analysis import analyze as assignment_readback, read_assignment


def cell_orbits(size, rotations, side):
    """Require actual native maps to be uniform, closed orbit averaging."""
    mappings = {}
    for cell in range(1, size**3+1):
        targets = Counter(mapped_cell(cell, side, size, r) for r in rotations)
        if None in targets or len(set(targets.values())) != 1:
            raise ValueError('Nonuniform or noncommensurate cell averaging')
        mappings[cell] = tuple(sorted(targets))
    for cell, orbit in mappings.items():
        if any(mappings[target] != orbit for target in orbit) or cell not in orbit:
            raise ValueError('Cell averaging does not form closed orbits')
    return sorted(set(mappings.values()))


def coefficients(xi, gap, beta):
    energy = math.hypot(xi, gap)
    if energy == 0 or not all(map(math.isfinite, (xi, gap, beta))) or beta <= 0:
        raise ValueError('Invalid candidate thermal context')
    return (beta*(sech2(.5*beta*xi)-sech2(.5*beta*energy)),
            4*(math.tanh(.5*beta*xi)-xi/energy*math.tanh(.5*beta*energy)))


def contract(dims, physical, raw, averaged, thermal, orbits):
    """Replay all cached averages; contract only a closed, declared support."""
    nx, first, last, cells, _ = dims
    bands = last-first+1
    denominator = physical[1]*physical[0]**2
    if denominator == 0 or not math.isfinite(denominator):
        raise ValueError('Invalid response normalization range')
    errors = {f: 0. for f in FIELDS}
    scales = {f: max(map(abs, raw[f])) for f in FIELDS}
    cases = []
    for side in (0, 1):
        terms = defaultdict(list)
        retained = 0
        for orbit in orbits[side]:
            for band in range(bands):
                for ix in range(nx):
                    indices = [ix+nx*(band+bands*(cell-1+cells*side)) for cell in orbit]
                    expected_fields = {}
                    for field in FIELDS:
                        expected = math.fsum(raw[field][i] for i in indices)/len(indices)
                        expected_fields[field] = expected
                        errors[field] = max(errors[field], max(abs(averaged[field][i]-expected) for i in indices))
                    selected = [i in thermal for i in indices]
                    if any(selected) and not all(selected):
                        raise ValueError('Resolved support is not closed under cell averaging')
                    if not any(selected):
                        continue
                    retained += len(indices)
                    ts, hs = zip(*(thermal[i] for i in indices))
                    tmin, tmax, hmin, hmax = min(ts), max(ts), min(hs), max(hs)
                    w = raw['dx0'][ix]/denominator
                    for i, t, h in zip(indices, ts, hs):
                        dos = averaged['dos'][i]
                        if dos <= 1e-12:
                            raise ValueError('Nonretained state in resolved response support')
                        raw_term = w*(t*raw['second'][i]+h*raw['curvature'][i])
                        terms['raw_second'].append(raw_term)
                        terms['averaged_second'].append(w*(t*averaged['second'][i]+h*averaged['curvature'][i]))
                        terms['averaged_mean_squared'].append(w*(t*averaged['first'][i]**2/dos+h*averaged['curvature'][i]))
                        terms['coefficient_range_bound'].append(abs(w)*(
                            abs(raw['second'][i])*max(abs(t-tmin), abs(tmax-t))
                            + abs(raw['curvature'][i])*max(abs(h-hmin), abs(hmax-h))))
                        terms['raw_absolute_term_sum'].append(abs(raw_term))
                        # Cache replay differs from ideal averaging in floating arithmetic.
                        terms['observed_replay_allowance'].append(abs(w)*(
                            abs(t)*abs(averaged['second'][i]-expected_fields['second'])
                            + abs(h)*abs(averaged['curvature'][i]-expected_fields['curvature'])))
                        terms['roundoff_scale'].append(abs(w)*(
                            abs(t)*(abs(raw['second'][i])+abs(averaged['second'][i]))
                            + abs(h)*(abs(raw['curvature'][i])+abs(averaged['curvature'][i]))))
        row = {name: math.fsum(values) for name, values in terms.items()}
        if not retained:
            raise ValueError('Empty resolved response support')
        row['floating_roundoff_allowance'] = 64*sys.float_info.epsilon*row['roundoff_scale']
        row['averaging_absolute_bound'] = (row['coefficient_range_bound']
            + row['observed_replay_allowance'] + row['floating_roundoff_allowance'])
        row['retained_resolved_states'] = retained
        row['averaging_difference'] = row['averaged_second']-row['raw_second']
        scale = abs(row['raw_second'])
        row['averaging_bound_over_raw_response'] = row['averaging_absolute_bound']/scale if scale else None
        row['raw_cancellation_ratio'] = row['raw_absolute_term_sum']/scale if scale else None
        cases.append(row)
    if any(errors[f] > 1e-12*scales[f] for f in FIELDS):
        raise ValueError('Cached moment averaging fails native orbit replay')
    if any(abs(row['averaging_difference']) > row['averaging_absolute_bound'] for row in cases):
        raise ValueError('Observed averaging change exceeds computed bound')
    return dict(grids=cases, averaging_replay_max_absolute_errors=errors,
                averaging_replay_reference_scales=scales, averaging_replay_relative_tolerance=1e-12)



def check_constant_controls(dims, physical, averaged, controls):
    """Bind cached moments to all three independently accumulated native rows."""
    nx, first, last, cells, _ = dims
    if (controls['dimensions'][:3] != [nx, first, last]
            or controls['dimensions'][4] != cells
            or [controls['qnorm'], controls['volume']] != physical[:2]):
        raise ValueError('Cached/native constant-control context differs')
    stride = nx*(last-first+1)*cells
    denominator = physical[1]*physical[0]**2
    errors = []
    for row in controls['cases']:
        beta = 157887.51240203338/row['temperature_kelvin']
        thermal = [coefficients(x, 1.5/13605.693122994, beta) for x in averaged['xi0']]
        for side in (0, 1):
            totals = defaultdict(list)
            for i in range(side*stride, (side+1)*stride):
                t, h = thermal[i % nx]
                w = averaged['dx0'][i % nx]/denominator
                second = w*(t*averaged['second'][i]+h*averaged['curvature'][i])
                totals['second_moment_all'].append(second)
                if averaged['dos'][i] > 1e-12:
                    totals['second_moment_active'].append(second)
                    totals['mean_squared_active'].append(w*(
                        t*averaged['first'][i]**2/averaged['dos'][i]+h*averaged['curvature'][i]))
            for name, values in totals.items():
                expected = row[name][side]
                error = abs(math.fsum(values)-expected)
                if error > 1e-12+1e-9*abs(expected):
                    raise ValueError('Cache differs from native constant-gap control')
                errors.append(error)
    return max(errors)


def analyze(directory, candidate, prepare, manifest_path):
    root, candidate, prepare = map(Path, (directory, candidate, prepare))
    manifest = json.loads(Path(manifest_path).read_text())
    for entry in manifest['files']:
        path = Path(entry['path'])
        if path.stat().st_size != entry['bytes'] or digest(path) != entry['sha256']:
            raise ValueError('Changed prospective cache input: '+str(path))
    executables = [Path(e['path']) for e in manifest['files'] if Path(e['path']).name == 'velocity-moment-probe.x']
    if executables != [root.absolute()/'velocity-moment-probe.x']:
        raise ValueError('Prospective cache executable belongs to another directory')
    receipt = json.loads((root/'results/moment/receipt.json').read_text())
    if (receipt.get('status') != 'PASS' or receipt.get('exit') != 0 or receipt.get('error') is not None
            or receipt['cwd'] != str(root.absolute())
            or receipt['command'] != [str(root.absolute()/'velocity-moment-probe.x'), '-in', str(root.absolute()/'native.in')]):
        raise ValueError('Missing or stale terminal cache receipt')
    controls = moment_controls(root/'velocity-moments.txt')
    mapping = assignment_readback(root, prepare)
    if not mapping['mapping_compatible']:
        raise ValueError('Candidate/response assignment is incompatible')
    checked = reduced_readback(candidate, prepare)
    dims, physical, raw, averaged = read_pair(root)
    constant_error = check_constant_controls(dims, physical, averaged, controls)
    size, rotations = read_rotations(root/'response-symmetry.txt')
    log = root/'results/moment/console.log'
    selected = list(map(int, re.findall(r'Number of symmetries conserving q_FFLO\s*:\s*(\d+)', log.read_text())))
    if not selected or any(count != len(rotations) for count in selected):
        raise ValueError('Native cache did not use the exported full rotation group')
    counts, state = native_arrays(prepare)
    nx, first, last, cells, _ = dims
    bands = last-first+1
    if (cells != size**3 or nx != counts[3] or cells != counts[4]
            or physical[:2] != [mapping['qnorm'], mapping['volume']]
            or first < mapping['dimensions'][5] or last > mapping['dimensions'][6]
            or list(raw['xi0']) != list(state['xi0'])):
        raise ValueError('Incompatible cache/candidate geometry')
    orbits = [cell_orbits(size, rotations, side) for side in (0, 1)]
    gap = array.array('d')
    gap.frombytes((candidate/'reduced-gap.bin').read_bytes())
    groups = defaultdict(list)
    for side, count in enumerate(counts[:2]):
        start = side*counts[2]
        for i in range(start, start+count):
            groups[side, state['kindx'][i], state['bindx'][i]].append(i)
    thermal = {}
    omitted = [0, 0]
    single_states = [[], []]
    _, _, assigned, _, _ = read_assignment(root)
    tolerance = 64*sys.float_info.epsilon
    for (side, cell, band), indices in groups.items():
        offset = nx*((band-first)+bands*(cell-1+cells*side)) if first <= band <= last else None
        labels = ([ix for ix in range(nx) if averaged['dos'][offset+ix] > 1e-12]
                  if offset is not None else [])
        # store_d3k resolves a cell/band only when at least TWO nodes survive.
        if len(labels) < 2:
            if len(indices) != 1:
                raise ValueError('Native single-state branch count differs')
            i = indices[0]
            omitted[side] += 1
            single_states[side].append((assigned['xi'][i], gap[i], assigned['dk'][i],
                assigned['dxq'][i]/physical[0], assigned['d2xq'][i]/physical[0]**2))
            continue
        by_energy = {state['xi'][i]: i for i in indices}
        if len(by_energy) != len(indices) or set(by_energy) != {raw['xi0'][ix] for ix in labels}:
            raise ValueError('Resolved candidate energy labels differ from cache support')
        for ix in labels:
            i = by_energy[raw['xi0'][ix]]
            weight = averaged['dos'][offset+ix]*raw['dx0'][ix]
            if abs(weight-state['dk'][i]) > tolerance*max(abs(weight), abs(state['dk'][i])):
                raise ValueError('Resolved candidate quadrature weight differs from cache')
            thermal[offset+ix] = coefficients(state['xi'][i], gap[i], checked['beta'])
    expected_support = sum(count for offset in range(0, len(averaged['dos']), nx)
        if (count := sum(d > 1e-12 for d in averaged['dos'][offset:offset+nx])) >= 2)
    if len(thermal) != expected_support:
        raise ValueError('Candidate does not cover all retained cache support')
    result = contract(dims, physical, raw, averaged, thermal, orbits)
    for side, row in enumerate(result['grids']):
        single = stiffness(single_states[side], checked['beta'], physical[1])
        row['unchanged_single_state_branch_response'] = single
        row['combined_raw_second'] = row['raw_second']+single
        row['combined_averaged_second'] = row['averaged_second']+single
        row['combined_averaged_mean_squared'] = row['averaged_mean_squared']+single
        denominator = abs(row['combined_raw_second'])
        row['averaging_bound_over_combined_response'] = row['averaging_absolute_bound']/denominator if denominator else None
    paths = [root/f'cell-moments-{phase}.{suffix}' for phase in ('raw', 'averaged') for suffix in ('txt', 'bin')]
    paths += [Path(manifest_path), root/'results/moment/receipt.json', log, root/'response-symmetry.txt', root/'velocity-moments.txt', candidate/'reduced-gap.bin']
    result.update(scope=__doc__, dimensions=dims, qnorm=physical[0], volume=physical[1],
                  beta=checked['beta'], omitted_native_states=omitted,
                  cached_constant_control_max_absolute_error=constant_error,
                  constant_gap_native_controls=controls, assignment=mapping,
                  reduced_readback=checked, sha256={str(p): digest(p) for p in paths},
                  bound_scope='Change of moments on native resolved support; native single-state contribution held identical in combined totals; discarded DOS support not reconstructed',
                  terminal_receipt=receipt,
                  bound_is_formal_interval_certificate=False,
                  roundoff_scope='Triangle bound on computed coefficients with measured cache replay error and 64eps contraction allowance; not interval-certified transcendental functions',
                  gap_modified=False, conditioned_gap_error_bounded=False, physical_response_verified=False)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('directory', 'candidate', 'prepare', 'manifest_path'):
        parser.add_argument(name, type=Path)
    print(json.dumps(analyze(**vars(parser.parse_args())), indent=2, allow_nan=False))
