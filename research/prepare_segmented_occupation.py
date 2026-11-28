"""Prepare occupation enrichment only from a certified complete segmented map."""
import argparse
import array
import json
import math
from pathlib import Path
import sys

from compare_legacy_gap import digest, native_arrays
from occupation_enrichment import enrich
from reduced_nonlinear_analysis import analyze as reduced_readback
from full_map_segments import certify, recorded_result


def prepare(full_directory, full_manifest, full_result, reduced_directory, output):
    full, reduced, output = map(Path, (full_directory, reduced_directory, output))
    if sys.byteorder != 'little':
        raise ValueError('Retained basis requires little-endian binary64')
    certificate = certify(full_manifest)
    if (not certificate['complete_left_row_coverage']
            or json.loads(Path(full_manifest).read_text())['cwd'] != str(full.absolute())):
        raise ValueError('Complete owning segmented evaluation required')
    recorded_result(full_result, certificate)
    if json.loads(Path(full_result).read_text()).get('full_candidate') != certificate['full_candidate']:
        raise ValueError('Full candidate differs from its recorded certification')
    checked = certificate['full_candidate']
    basis_manifest = full_manifest
    control = (reduced/'reduced-control.in').read_text().splitlines()
    if len(control) != 5:
        raise ValueError('Stale reduced control')
    basis, geometry = map(Path, control[:2])
    expected_context = control[3]
    beta = float(control[4].split()[0])
    manifest = json.loads(Path(basis_manifest).read_text())
    inputs = [basis/'basis.meta', basis/'basis.bin', geometry/'native-init.meta', geometry/'native-init.bin',
              reduced/'reduced-control.in', reduced/'reduced-gap.bin', reduced/'reduced-result.txt']
    for path in inputs:
        entries = [entry for entry in manifest['files'] if entry['path'] == str(path)]
        if len(entries) != 1 or path.stat().st_size != entries[0]['bytes'] or digest(path) != entries[0]['sha256']:
            raise ValueError('Changed declared enrichment input: '+str(path))
    candidate = reduced_readback(reduced, geometry)
    if digest(reduced/'reduced-gap.bin') != digest(full/'gap-seed.bin'):
        raise ValueError('Full evaluation does not belong to the reduced candidate')
    seed = (full/'gap-seed.meta').read_text().splitlines()
    meta = (basis/'basis.meta').read_text().splitlines()
    if len(meta) != 5 or meta[0] != 'tc-basis-v1':
        raise ValueError('Unsupported retained basis schema')
    n, rank = map(int, meta[1].split())
    counts, state = native_arrays(geometry)
    config = list(map(int, meta[4].split()))
    seed_dims = list(map(int, seed[1].split()))
    if (not 1 <= rank < 64 or n != 2*counts[2] or rank != candidate['dimensions'][4]
            or float(meta[2]) != beta or beta != checked['full_readback']['beta']
            or beta != candidate['beta'] or meta[3] != expected_context
            or seed[3] != str(geometry) or seed[4] != expected_context
            or config != [seed_dims[3], seed_dims[4], 10, 2, *counts[:2]]):
        # The native verification experiment fixes nx/nmf/ne; require its exact
        # retained operator configuration, rather than infer cache compatibility.
        raise ValueError('Incompatible enrichment operator context')
    if (basis/'basis.bin').stat().st_size != 16*n*rank:
        raise ValueError('Stale retained basis payload')
    with (basis/'basis.bin').open('rb') as source:
        columns = []
        for _ in range(2*rank):
            column = array.array('d')
            column.fromfile(source, n)
            columns.append(column)
    gap = array.array('d')
    with (full/'full-map.bin').open('rb') as source:
        gap.fromfile(source, n)
        residual = array.array('d'); residual.fromfile(source, n)
    occupation = []
    for x, delta in zip(state['xi'], gap):
        energy = math.hypot(x, delta)
        denominator = math.tanh(beta*abs(x)/2)/abs(x) if x != 0 else beta/2
        occupation.append(delta/energy*math.tanh(beta*energy/2)/denominator if energy != 0 else 0.)
    image = [d+r for d, r in zip(gap, residual)]
    direction, action, report = enrich(columns[:rank], columns[rank:], occupation, image)
    for side, count in enumerate(counts[:2]):
        padding = slice(side*counts[2]+count, (side+1)*counts[2])
        if any(direction[padding]) or any(action[padding]):
            raise ValueError('Nonzero enriched padding')
    # No output directory is created until all source and numerical gates pass.
    output.mkdir()
    meta[1] = f'{n} {rank+1}'
    (output/'basis.meta').write_text('\n'.join(meta)+'\n')
    with (output/'basis.bin').open('wb') as destination:
        for column in (*columns[:rank], direction, *columns[rank:], action):
            array.array('d', column).tofile(destination)
    report.update(old_rank=rank, new_rank=rank+1, beta=beta, context=expected_context,
                  full_candidate_targets_met=checked['stationary_residual_targets_met'],
                  full_evaluation=checked, full_segmented_certificate=certificate,
                  full_result_sha256=digest(full_result),
                  inputs_sha256={str(path): digest(path) for path in (*inputs,
                      reduced/'reduced-control.in', reduced/'reduced-gap.bin',
                      Path(full_manifest), Path(basis_manifest))},
                  outputs_sha256={str(path): digest(path) for path in (output/'basis.meta', output/'basis.bin')},
                  scope=__doc__)
    (output/'enrichment.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('full_directory', 'full_manifest', 'full_result', 'reduced_directory', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(**vars(args)), indent=2, allow_nan=False))
