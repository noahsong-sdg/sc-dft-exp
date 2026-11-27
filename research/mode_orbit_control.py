"""Compare a freshly validated linear mode and its image on native cell orbits."""
import argparse
import array
import json
from pathlib import Path

from compare_legacy_gap import digest, native_arrays
from gap_symmetry_audit import audit_values
from mode_amplitude_analysis import analyze
from prepare_critical_mode_enrichment import declared_inputs


def audit(amplitude_directory, amplitude_manifest, amplitude_result, geometry_manifest, symmetry_file):
    root = Path(amplitude_directory).absolute()
    am = json.loads(Path(amplitude_manifest).read_text())
    gm = json.loads(Path(geometry_manifest).read_text())
    runtime = [Path(e['path']) for e in am['files'] if Path(e['path']).parent == root]
    declared_inputs(am, runtime)
    receipt_path = root/'results/moment/receipt.json'
    receipt = json.loads(receipt_path.read_text())
    if (receipt != am['receipt'] or receipt.get('status') != 'PASS' or receipt.get('exit') != 0
            or receipt.get('error') is not None or receipt['cwd'] != str(root)
            or receipt['command'][0] != str(root/'mode-amplitude-probe.x')
            or any(root/name not in runtime for name in
                   ('mode-amplitude-probe.x', 'mode-control.in', 'map-control.in'))):
        raise ValueError('Stale linear-mode execution receipt')
    checked = analyze(root)
    if checked['sha256'] != json.loads(Path(amplitude_result).read_text())['sha256']:
        raise ValueError('Changed published linear-mode output')
    control = (root/'mode-control.in').read_text().splitlines()
    frame = (root/'map-control.in').read_text().splitlines()
    if len(control) != 2 or len(frame) != 1:
        raise ValueError('Stale linear-mode frame control')
    prepare = Path(frame[0])
    native_files = [prepare/'native-init.meta', prepare/'native-init.bin']
    declared_inputs(gm, native_files)
    mode_meta_path = Path(control[0])/'basis.meta'
    declared_inputs(am, [mode_meta_path])
    meta = mode_meta_path.read_text().splitlines()
    counts, _ = native_arrays(prepare)
    if (len(meta) != 5 or meta[0] != 'tc-basis-v1' or len(control[1]) != 64
            or gm['context'] != control[1] or meta[3] != control[1]
            or gm['beta'] != checked['beta'] or float(meta[2]) != checked['beta']
            or int(meta[1].split()[0]) != 2*counts[2] or counts[:3] != checked['dimensions'][:3]):
        raise ValueError('Incompatible linear-mode geometry context')
    scales = [row['mode_scale_ry'] for row in checked['rows'] if row['mean_gap_amplitude_mev'] == .15]
    if len(scales) != 1:
        raise ValueError('Missing registered mode amplitude')
    reports = {}
    with (root/'mode-amplitudes.bin').open('rb') as source:
        for role in ('mode_scaled_to_015mev', 'fresh_linear_image_same_scale'):
            values = array.array('d'); values.fromfile(source, 2*counts[2])
            reports[role] = audit_values([scales[0]*value for value in values], prepare, symmetry_file)
    inputs = [Path(p) for p in (amplitude_manifest, amplitude_result, geometry_manifest, symmetry_file)]
    inputs.extend([*runtime, *native_files, mode_meta_path, receipt_path,
                   root/'mode-amplitudes.txt', root/'mode-amplitudes.bin'])
    return dict(reports=reports, measured_mode_readback=checked,
                context=control[1], beta=checked['beta'], scope=__doc__,
                sha256={str(p): digest(p) for p in inputs}, physical_response_verified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('amplitude_directory', 'amplitude_manifest', 'amplitude_result',
                 'geometry_manifest', 'symmetry_file'):
        parser.add_argument(name, type=Path)
    print(json.dumps(audit(**vars(parser.parse_args())), indent=2, allow_nan=False))
