"""Append a measured conventional mode/image to the same-context retained basis."""
import argparse
import array
import json
import math
from pathlib import Path
import sys

from compare_legacy_gap import digest
from mode_amplitude_analysis import analyze
from occupation_enrichment import combine, dot, enrich


def declared_inputs(manifest, paths):
    for path in paths:
        entries = [e for e in manifest['files'] if e['path'] == str(path)]
        if len(entries) != 1 or path.stat().st_size != entries[0]['bytes'] or digest(path) != entries[0]['sha256']:
            raise ValueError('Changed declared mode-enrichment input: '+str(path))


def prepare(basis_directory, basis_manifest, amplitude_directory, amplitude_manifest, amplitude_result, output):
    basis, full, output = (Path(p).absolute() for p in (basis_directory, amplitude_directory, output))
    if sys.byteorder != 'little':
        raise ValueError('Retained mode enrichment requires little-endian binary64')
    bm = json.loads(Path(basis_manifest).read_text())
    am = json.loads(Path(amplitude_manifest).read_text())
    basis_files = [basis/'basis.meta', basis/'basis.bin']
    runtime = [Path(e['path']) for e in am['files'] if Path(e['path']).parent == full]
    declared_inputs(bm, basis_files)
    declared_inputs(am, runtime)
    receipt = json.loads((full/'results/moment/receipt.json').read_text())
    if (receipt != am['receipt'] or receipt.get('status') != 'PASS' or receipt.get('exit') != 0
            or receipt.get('error') is not None or receipt['cwd'] != str(full)
            or receipt['command'][0] != str(full/'mode-amplitude-probe.x')
            or full/'mode-amplitude-probe.x' not in runtime or full/'mode-control.in' not in runtime):
        raise ValueError('Stale measured-mode execution receipt')
    checked = analyze(full)
    recorded = json.loads(Path(amplitude_result).read_text())
    if checked['sha256'] != recorded['sha256']:
        raise ValueError('Changed declared amplitude output')
    control = (full/'mode-control.in').read_text().splitlines()
    if len(control) != 2:
        raise ValueError('Stale measured-mode control')
    mode_dir = Path(control[0])
    mode_files = [mode_dir/'basis.meta', mode_dir/'selected.meta', mode_dir/'selected.bin']
    declared_inputs(am, mode_files)
    meta = (basis/'basis.meta').read_text().splitlines()
    mode_meta = mode_files[0].read_text().splitlines()
    if len(meta) != 5 or len(mode_meta) != 5 or meta[0] != 'tc-basis-v1' or mode_meta[0] != meta[0]:
        raise ValueError('Stale critical-mode basis schema')
    n, rank = map(int, meta[1].split())
    if (n != 2*checked['dimensions'][2] or not 1 <= rank < 64
            or int(mode_meta[1].split()[0]) != n
            or float(meta[2]) != checked['beta'] or float(mode_meta[2]) != checked['beta']
            or meta[3] != control[1] or mode_meta[3] != control[1]
            or len(control[1]) != 64 or meta[4].split() != mode_meta[4].split()
            or (basis/'basis.bin').stat().st_size != 16*n*rank):
        raise ValueError('Incompatible critical-mode operator context')
    columns = []
    with (basis/'basis.bin').open('rb') as source:
        for _ in range(2*rank):
            column = array.array('d'); column.fromfile(source, n); columns.append(column)
    with (full/'mode-amplitudes.bin').open('rb') as source:
        mode = array.array('d'); mode.fromfile(source, n)
        image = array.array('d'); image.fromfile(source, n)
    q, u = columns[:rank], columns[rank:]
    direction, action, report = enrich(q, u, mode, image)
    q_new, u_new = [*q, direction], [*u, action]
    for side, count in enumerate(checked['dimensions'][:2]):
        padding = slice(side*n//2+count, (side+1)*n//2)
        if any(x for column in (*q_new, *u_new) for x in column[padding]):
            raise ValueError('Nonzero critical-mode basis padding')
    p = [dot(column, mode) for column in q_new]
    projection_error = [a-b for a, b in zip(mode, combine(q_new, p))]
    action_error = [a-b for a, b in zip(image, combine(u_new, p))]
    report.update(old_rank=rank, new_rank=rank+1, beta=checked['beta'], context=control[1],
                  mode_projection_defect_norm=math.sqrt(dot(projection_error, projection_error)),
                  mode_action_defect_norm=math.sqrt(dot(action_error, action_error)),
                  mode_action_max_error=max(map(abs, action_error)),
                  scope=__doc__, full_nonlinear_candidate_verified=False,
                  inputs_sha256={str(p): digest(p) for p in (*basis_files, *runtime, *mode_files,
                      full/'mode-amplitudes.txt', full/'mode-amplitudes.bin',
                      Path(basis_manifest), Path(amplitude_manifest), Path(amplitude_result))})
    output.mkdir()
    meta[1] = f'{n} {rank+1}'
    (output/'basis.meta').write_text('\n'.join(meta)+'\n')
    with (output/'basis.bin').open('wb') as destination:
        for column in (*q_new, *u_new):
            array.array('d', column).tofile(destination)
    report['outputs_sha256'] = {str(p): digest(p) for p in (output/'basis.meta', output/'basis.bin')}
    (output/'enrichment.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('basis_directory', 'basis_manifest', 'amplitude_directory', 'amplitude_manifest', 'amplitude_result', 'output'):
        parser.add_argument(name, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(**vars(args)), indent=2, allow_nan=False))
