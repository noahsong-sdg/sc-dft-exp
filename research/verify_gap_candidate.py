"""Certify declared stationary residual targets, never physical response accuracy."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from full_nonlinear_analysis import analyze as full_readback


def verify(directory, manifest_path):
    root = Path(directory)
    manifest = json.loads(Path(manifest_path).read_text())
    exe_entries = [x for x in manifest['files'] if Path(x['path']).name == 'verify-gap-seed.x']
    if len(exe_entries) != 1:
        raise ValueError('Missing unique prospective executable identity')
    exe = exe_entries[0]
    declared_root = Path(exe['path']).parent
    for item in manifest['files']:
        if Path(item['path']).parent == declared_root:
            payload = root/Path(item['path']).name
            if payload.stat().st_size != item['bytes'] or hashlib.sha256(payload.read_bytes()).hexdigest() != item['sha256']:
                raise ValueError('Changed declared native input: '+payload.name)
    receipt = json.loads((root/'results/moment/receipt.json').read_text())
    if receipt.get('status') != 'PASS' or receipt.get('exit') != 0 or receipt.get('error') is not None:
        raise ValueError('Native execution did not pass its guard')
    wall = receipt['wall_s']
    if not math.isfinite(wall) or wall < 0 or receipt['command'][0] != exe['path'] or receipt['cwd'] != str(declared_root):
        raise ValueError('Stale native execution receipt')
    full = full_readback(root)
    meta = (root/'gap-seed.meta').read_text().splitlines()
    if len(meta) != 5 or meta[0] != 'gap-seed-v1; binary64 Fortran order':
        raise ValueError('Stale gap seed metadata')
    dims = list(map(int,meta[1].split()))
    if len(dims) != 6 or min(dims) < 1 or dims[:3] != full['dimensions'][:3] or float(meta[2]) != full['beta']:
        raise ValueError('Incompatible persisted seed context')
    seed = (root/'gap-seed.bin').read_bytes()
    if hashlib.sha256(seed).hexdigest() != manifest['candidate_sha256'] or len(seed) != 16*dims[2]:
        raise ValueError('Changed declared candidate')
    with (root/'full-map.bin').open('rb') as source:
        if source.read(len(seed)) != seed:
            raise ValueError('Native evaluation used a different gap')
        residual_payload = source.read(len(seed))
    gap = struct.unpack('<'+'d'*(2*dims[2]),seed)
    residual = struct.unpack('<'+'d'*(2*dims[2]),residual_payload)
    gap2 = math.fsum(x*x for x in gap)
    if gap2 <= 0:
        raise ValueError('Zero candidate cannot certify the declared nonzero branch')
    ratio = math.sqrt(math.fsum(x*x for x in residual)/gap2)
    infinity = max(side['max_absolute_residual_ry'] for side in full['sides'])
    return dict(full_readback=full,terminal_guard_pass=True,input_gap_bitwise_preserved=True,
                wall_s=wall,peak_individual_rss_bytes=receipt['max_individual_descendant_rss_bytes'],
                residual_infinity_ry=infinity,rms_residual_over_gap=ratio,
                thresholds=dict(residual_infinity_ry=1e-10,rms_residual_over_gap=1e-5),
                stationary_residual_targets_met=infinity <= 1e-10 and ratio <= 1e-5,
                conditioned_gap_error_bounded=False,physical_response_verified=False,
                manifest_sha256=hashlib.sha256(Path(manifest_path).read_bytes()).hexdigest(),
                scope=__doc__.strip())


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('manifest',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.directory,args.manifest),indent=2,allow_nan=False))
