"""Verify the declared fixed-density band replay, without fitting energy offsets."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from fetch_public_response_inputs import digest
from stage_public_band_pilot import numbers


def verify_postrun_inputs(manifest, root):
    """Originals stay fixed; only the consumed XML becomes a native output."""
    for item in manifest['files']:
        path = Path(item['path'])
        if item.get('rewritten_by_native') is True:
            if path != root/'scratch/pwscf.save/data-file-schema.xml':
                raise ValueError('Unexpected mutable band input')
            continue
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('Changed declared band-pilot input: '+str(path))


def compare(reference, xml, expected_points=8):
    states = ET.fromstring(xml).findall('output/band_structure/ks_energies')
    if len(reference) != expected_points or len(states) != expected_points:
        count='eight' if expected_points==8 else str(expected_points)
        raise ValueError('Band replay must contain exactly '+count+' points')
    differences = []
    for row, state in zip(reference, states):
        k = numbers(state.findtext('k_point'))
        energy = numbers(state.findtext('eigenvalues'))
        expected = row['eigenvalues_ry']
        if (len(k) != 3 or len(energy) != 26 or len(expected) != 26
                or max(abs(a-b) for a,b in zip(k,row['k_tpiba'])) > 1e-12):
            raise ValueError('Band replay point or band layout differs')
        differences.append(max(abs(2*a-b) for a,b in zip(energy,expected)))
    return differences


def analyze(directory, manifest_path, expected_points=8, guard_seconds=180):
    root = Path(directory).absolute()
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    if (manifest['cwd'] != str(root) or manifest['points'] != expected_points
            or manifest['acceptance_max_eigenvalue_difference_ry'] != 1e-6):
        raise ValueError('Changed declared band-pilot context')
    verify_postrun_inputs(manifest, root)
    receipts = []
    for path in root.rglob('receipt.json'):
        receipt = json.loads(path.read_text())
        if receipt.get('command') == manifest['command'] and receipt.get('cwd') == str(root):
            receipts.append((path, receipt))
    if len(receipts) != 1:
        raise ValueError('Exactly one matching terminal band-pilot receipt required')
    receipt_path, receipt = receipts[0]
    if receipt['status'] != 'PASS' or receipt['exit'] != 0 or receipt['continuous_deadline_s'] != guard_seconds:
        raise ValueError('Band-pilot guard did not pass the declared protocol')
    output = root/'scratch/pwscf.save/data-file-schema.xml'
    reference = json.loads((root/'reference.json').read_text())
    differences = compare(reference, output.read_text(), expected_points)
    return dict(max_eigenvalue_difference_ry=max(differences), point_max_differences_ry=differences,
                acceptance_max_eigenvalue_difference_ry=1e-6, replay_targets_met=max(differences)<=1e-6,
                energy_offset_fitted=False, original_inputs_unchanged=True, terminal_receipt=receipt,
                sha256={str(path):digest(path) for path in (manifest_path,receipt_path,output,root/'reference.json')},
                scope=__doc__.strip()+' Not density, cutoff or k-grid convergence; not physical response accuracy.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('manifest_path', type=Path)
    print(json.dumps(analyze(**vars(parser.parse_args())), indent=2, allow_nan=False))
