"""Build the ordered full-map variant; does not run microscopic kernel images."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from fetch_public_response_inputs import digest
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def stage(parent_manifest, destination):
    parent_manifest, root = map(lambda p: Path(p).absolute(), (parent_manifest, destination))
    parent = json.loads(parent_manifest.read_text())
    prior = Path(parent['cwd'])
    verify_postrun_inputs(parent, prior)
    receipt = json.loads((prior/'results/build/receipt.json').read_text())
    result = json.loads((prior/'qualification-result.json').read_text())
    if (receipt.get('status') != 'PASS' or receipt.get('exit') != 0 or receipt.get('error') is not None
            or receipt['command'] != parent['command'] or receipt['cwd'] != str(prior)
            or result.get('checks') != 902 or result.get('all_checks_bitwise_equal') is not True
            or result.get('full_gap_driver_linked') is not True
            or digest(prior/'full-gap-check.x') != result['full_gap_executable_sha256']):
        raise ValueError('Qualified source-only parent build required')
    if root.exists():
        raise ValueError('Fresh checkpoint build directory required')
    entries = {}
    for item in parent['files']:
        if item['path'] in entries and entries[item['path']] != item:
            raise ValueError('Conflicting parent input identity')
        entries[item['path']] = item
    paths = [parent_manifest, prior/'results/build/receipt.json', prior/'qualification-result.json',
             prior/'full-gap-check.x', Path(__file__), RESEARCH/'macos_native_guard_v2.py',
             RESEARCH/'full_map_checkpoint.f90', RESEARCH/'full_nonlinear_checkpoint_probe.f90',
             RESEARCH/'portable_gap/linear_image_checkpoint.f90',
             RESEARCH/'portable_gap/full_checkpoint_link.mk']
    for path in paths:
        entries[str(path)] = dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
    manifest = dict(cwd=str(root), command=[sys.executable, str(Path(__file__).resolve()), 'run', str(root)],
                    public_build=parent['public_build'], files=list(entries.values()),
                    guard_seconds=120, launch_normal_seconds=120, group_rss_cap_bytes=3221225472,
                    guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),
                    historical_objects_used=False, scope=__doc__,
                    acceptance='Source-only variant link and902unchanged bitwise cache controls; no microscopic split or full residual acceptance')
    root.mkdir(parents=True)
    (root/'run-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def run(root):
    root = Path(root).absolute()
    manifest = json.loads((root/'run-manifest.json').read_text())
    verify_postrun_inputs(manifest, root)
    subprocess.run(['/usr/bin/make', '-f', str(RESEARCH/'portable_gap/full_checkpoint_link.mk'),
                    'RESEARCH='+str(RESEARCH), 'QE_ROOT='+str(Path(manifest['public_build'])/'qe'),
                    'full-link'], cwd=root, check=True)
    cache = subprocess.run([str(root/'cache-qualification.x')], cwd=root,
                           text=True, capture_output=True, check=True)
    if not re.fullmatch(r'\s*CACHE_QUALIFICATION_PASS checks=902\s*', cache.stdout):
        raise ValueError('Incomplete unchanged-cache qualification')
    verify_postrun_inputs(manifest, root)
    result = dict(checks=902, all_checks_bitwise_equal=True, historical_objects_used=False,
                  full_gap_driver_linked=True, full_gap_executable_sha256=digest(root/'full-gap-check.x'),
                  microscopic_split_qualified=False, full_gap_runtime_qualified=False, scope=__doc__)
    (root/'qualification-result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(cache.stdout, flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('stage')
    p.add_argument('parent_manifest', type=Path); p.add_argument('destination', type=Path)
    p = sub.add_parser('run'); p.add_argument('root', type=Path)
    args = vars(parser.parse_args()); action = args.pop('action')
    print(json.dumps((stage if action == 'stage' else run)(**args), indent=2))
