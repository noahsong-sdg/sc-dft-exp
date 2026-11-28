"""Declared-step owning-root residual verifier; original targets unchanged."""
import argparse
import array
import json
import math
from pathlib import Path

from fetch_public_response_inputs import digest
from full_map_segment_analysis import binary
from full_step_summary_analysis import analyze as full_readback


def verify(directory, manifest_path):
    root = Path(directory).absolute()
    manifest = json.loads(Path(manifest_path).read_text())
    command = manifest.get('command')
    expected = str(root/'verify-gap-seed.x')
    if manifest.get('cwd') != str(root) or not command or command[0] != expected:
        raise ValueError('Missing owning root/command executable identity')
    exe_entries = [x for x in manifest['files'] if x['path'] == expected]
    if len(exe_entries) != 1:
        raise ValueError('Missing unique owning executable identity')
    exe = exe_entries[0]
    declared_root = root
    for item in manifest['files']:
        if Path(item['path']).parent == declared_root:
            payload = root/Path(item['path']).name
            if payload.stat().st_size != item['bytes'] or digest(payload) != item['sha256']:
                raise ValueError('Changed declared native input: '+payload.name)
    receipt = json.loads((root/'results/moment/receipt.json').read_text())
    if receipt.get('status') != 'PASS' or receipt.get('exit') != 0 or receipt.get('error') is not None:
        raise ValueError('Native execution did not pass its guard')
    wall = receipt['wall_s']
    if not math.isfinite(wall) or wall < 0 or receipt['command'] != command or receipt['cwd'] != str(declared_root):
        raise ValueError('Stale native execution receipt')
    full = full_readback(root)
    meta = (root/'gap-seed.meta').read_text().splitlines()
    if len(meta) != 5 or meta[0] != 'gap-seed-v1; binary64 Fortran order':
        raise ValueError('Stale gap seed metadata')
    dims = list(map(int,meta[1].split()))
    if len(dims) != 6 or min(dims) < 1 or dims[:3] != full['dimensions'][:3] or float(meta[2]) != full['beta']:
        raise ValueError('Incompatible persisted seed context')
    gap = binary(root/'gap-seed.bin',2*dims[2])
    if digest(root/'gap-seed.bin') != manifest['candidate_sha256']:
        raise ValueError('Changed declared candidate')
    with (root/'full-map.bin').open('rb') as source:
        if source.read(8*len(gap)) != gap.tobytes():
            raise ValueError('Native evaluation used a different gap')
        residual=array.array('d');residual.fromfile(source,len(gap))
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
                manifest_sha256=digest(Path(manifest_path)),
                scope=__doc__.strip())


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('manifest',type=Path)
    args=parser.parse_args()
    print(json.dumps(verify(args.directory,args.manifest),indent=2,allow_nan=False))
