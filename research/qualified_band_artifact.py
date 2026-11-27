"""Reuse a published serialization qualification without rerunning its old code.

An explicit result hash anchors prior evidence. Historical manifests remain
immutable; changed historical staging code is not a consumed runtime input of
the new response. Every recorded artifact must still match that qualification.
"""
import hashlib
import json
from pathlib import Path

from fetch_public_response_inputs import digest


def check(directory, band_manifest, result_path, expected_result_sha256):
    root,band_manifest,result_path=[Path(p).absolute() for p in (directory,band_manifest,result_path)]
    payload=result_path.read_bytes()
    if hashlib.sha256(payload).hexdigest()!=expected_result_sha256:
        raise ValueError('Changed published band qualification')
    result=json.loads(payload)
    if (result.get('grid')!=[48]*3
            or result.get('shared_point_and_serialization_targets_met') is not True
            or result.get('all_parent_coordinates_energies_weights_preserved') is not True
            or result.get('separate_native_serialization') is not True
            or result.get('energy_offset_fitted') is not False
            or result.get('minimum_common_reference_points')!=100
            or result.get('acceptance_max_eigenvalue_difference_ry')!=1e-6
            or result.get('shared_reference_points',0)<100
            or not 0<=result.get('max_shared_eigenvalue_difference_ry',float('inf'))<=1e-6):
        raise ValueError('Expected qualified48-grid serialization evidence')
    hashes=result['sha256']
    required=[root/'scratch/pwscf.a2Fsave',root/'scratch/pwscf.save/data-file-schema.xml',
        root/'reference.json',root/'results/serialize/receipt.json',band_manifest]
    if any(str(p) not in hashes for p in required):
        raise ValueError('Missing qualified artifact provenance')
    for path,expected in hashes.items():
        if digest(Path(path))!=expected:
            raise ValueError('Changed qualified artifact: '+path)
    receipt=json.loads((root/'results/serialize/receipt.json').read_text())
    if (receipt!=result['terminal_receipt'] or receipt.get('status')!='PASS'
            or receipt.get('error') is not None or receipt.get('exit')!=0
            or receipt.get('cwd')!=str(root) or receipt.get('continuous_deadline_s')!=120):
        raise ValueError('Changed qualified serialization receipt')
    return dict(result,sha256={**hashes,str(result_path):expected_result_sha256},
        qualification_reused=True,qualification_scope=__doc__.strip())
