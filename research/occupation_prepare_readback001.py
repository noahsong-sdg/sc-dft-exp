"""Independent streaming readback of the first fresh occupation enrichment."""
import array
import json
import math
from pathlib import Path

from compare_legacy_gap import native_arrays
from fetch_public_response_inputs import digest
from full_map_segments import certify

ROOT = Path(__file__).resolve().parent


def column(source, index, n):
    source.seek(8*n*index)
    values = array.array('d'); values.fromfile(source, n)
    if not all(map(math.isfinite, values)):
        raise ValueError('Nonfinite basis column')
    return values


def main():
    protocol = ROOT/'portable_occupation_prepare001_manifest.json'
    manifest = json.loads(protocol.read_text()); root = Path(manifest['cwd'])
    if json.loads((root/'run-manifest.json').read_text()) != manifest:
        raise ValueError('Changed consumed preparation manifest')
    for item in manifest['files']:
        path = Path(item['path'])
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('Changed preparation input: '+str(path))
    receipt = json.loads((root/'results/occupation/receipt.json').read_text())
    if (receipt['status'] != 'PASS' or receipt['exit'] != 0 or receipt['error'] is not None
            or receipt['command'] != manifest['command'] or receipt['cwd'] != str(root)
            or receipt['guard_source_sha256'] != manifest['guard_source_sha256']
            or receipt['continuous_deadline_s'] != manifest['guard_seconds']
            or not 0 <= receipt['wall_s'] < manifest['guard_seconds']
            or max(receipt['max_individual_descendant_rss_bytes'], receipt['sampled_peak_group_rss_bytes']) > 3*1024**3):
        raise ValueError('Invalid preparation terminal receipt')
    report_path = root/'basis/enrichment.json'; report = json.loads(report_path.read_text())
    checked = certify(manifest['full_manifest'])
    if (not checked['complete_left_row_coverage'] or report['full_segmented_certificate'] != checked
            or report['full_evaluation'] != checked['full_candidate']
            or report['full_result_sha256'] != digest(Path(manifest['full_result']))):
        raise ValueError('Changed full evaluation binding')
    for path, expected in (report['inputs_sha256'] | report['outputs_sha256']).items():
        if digest(Path(path)) != expected:
            raise ValueError('Changed enrichment input/output')
    reduced = Path(manifest['reduced_directory'])
    control = (reduced/'reduced-control.in').read_text().splitlines()
    old, geometry = map(Path, control[:2]); new = root/'basis'
    meta = (old/'basis.meta').read_text().splitlines(); n, rank = map(int, meta[1].split())
    expected = list(meta); expected[1] = f'{n} {rank+1}'
    if ((new/'basis.meta').read_text().splitlines() != expected
            or (old/'basis.bin').stat().st_size != 16*n*rank
            or (new/'basis.bin').stat().st_size != 16*n*(rank+1)):
        raise ValueError('Changed inherited basis dimensions/context')
    counts, state = native_arrays(geometry); beta = float(meta[2])
    full = Path(json.loads(Path(manifest['full_manifest']).read_text())['cwd'])
    with (full/'full-map.bin').open('rb') as source:
        gap, residual = column(source, 0, n), column(source, 1, n)
    occupation = []
    def thermal(energy):
        t = math.expm1(-beta*energy)
        return -t/(2+t)
    for x, d in zip(state['xi'], gap):
        e = math.hypot(x, d)
        denominator = thermal(abs(x))/abs(x) if x else beta/2
        occupation.append(d/e*thermal(e)/denominator if e else 0.)
    with (old/'basis.bin').open('rb') as before, (new/'basis.bin').open('rb') as after:
        q, u = column(after, rank, n), column(after, 2*rank+1, n)
        alpha = math.fsum(a*b for a, b in zip(q, occupation))
        reconstructed = array.array('d', (alpha*x for x in u)); overlap = 0.
        for j in range(rank):
            oq, ou = column(before, j, n), column(before, rank+j, n)
            if oq.tobytes() != column(after, j, n).tobytes() or ou.tobytes() != column(after, rank+1+j, n).tobytes():
                raise ValueError('Inherited basis/action column changed')
            overlap = max(overlap, abs(math.fsum(a*b for a, b in zip(q, oq))))
            coefficient = math.fsum(a*b for a, b in zip(oq, occupation))
            for i, x in enumerate(ou): reconstructed[i] += coefficient*x
    norm = math.sqrt(math.fsum(x*x for x in q))
    if overlap > 1e-10 or abs(norm-1) > 1e-10:
        raise ValueError('New direction fails orthonormality')
    for side, active in enumerate(counts[:2]):
        padding = slice(side*counts[2]+active, (side+1)*counts[2])
        if any(q[padding]) or any(u[padding]): raise ValueError('Nonzero enriched padding')
    measured = [d+r for d, r in zip(gap, residual)]
    error = max(abs(a-b) for a, b in zip(measured, reconstructed))
    bound = 2e-18+2e-12*max(map(abs, measured))
    if error > bound: raise ValueError('Occupation/action reconstruction failed')
    return dict(terminal_guard_pass=True, inputs_unchanged=True, verified_input_count=len(manifest['files']),
                inherited_columns_bitwise_preserved=True, new_direction_norm=norm, maximum_old_basis_overlap=overlap,
                exponential_occupation_image_reconstruction_error=error, reconstruction_bound=bound,
                old_rank=rank, new_rank=rank+1, receipt=receipt,
                manifest_sha256=digest(protocol), enrichment_report_sha256=digest(report_path),
                outputs_sha256=report['outputs_sha256'], full_candidate_targets_met=False,
                conditioned_gap_error_bounded=False, physical_response_verified=False,
                scope=__doc__)


if __name__ == '__main__':
    print(json.dumps(main(), indent=2, allow_nan=False))
