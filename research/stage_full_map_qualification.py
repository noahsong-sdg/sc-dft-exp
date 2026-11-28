"""Stage one actual-input64-versus32+32 checkpoint test; no automatic launch."""
import argparse
import json
from pathlib import Path
import shutil

from fetch_public_response_inputs import digest
from full_map_segment_analysis import seed_context
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def stage(seed_manifest, build_manifest, destination):
    seed_manifest, build_manifest, root = map(lambda p: Path(p).absolute(),
                                             (seed_manifest, build_manifest, destination))
    if root.exists():
        raise ValueError('Fresh full-map qualification directory required')
    seed, build = (json.loads(path.read_text()) for path in (seed_manifest, build_manifest))
    source, built = Path(seed['cwd']), Path(build['cwd'])
    for manifest, directory in ((seed, source), (build, built)):
        if manifest != json.loads((directory/'run-manifest.json').read_text()):
            raise ValueError('Different public/consumed parent manifest')
        verify_postrun_inputs(manifest, directory)
    receipt_path = built/'results/build/receipt.json'
    receipt = json.loads(receipt_path.read_text())
    qualification_path = built/'qualification-result.json'
    qualified = json.loads(qualification_path.read_text())
    executable = built/'full-gap-check.x'
    if (receipt.get('status') != 'PASS' or receipt.get('exit') != 0 or receipt.get('error') is not None
            or receipt['command'] != build['command'] or receipt['cwd'] != str(built)
            or receipt['guard_source_sha256'] != build['guard_source_sha256']
            or qualified.get('checks') != 902 or qualified.get('all_checks_bitwise_equal') is not True
            or qualified.get('full_gap_driver_linked') is not True
            or qualified.get('historical_objects_used') is not False
            or digest(executable) != qualified['full_gap_executable_sha256']):
        raise ValueError('Qualified source-only checkpoint build required')
    dims, _, operator, _ = seed_context(source)
    if dims[0] < 64 or digest(source/'gap-seed.bin') != seed['candidate_sha256'] or operator != seed['operator_context_sha256']:
        raise ValueError('Different full-map seed/operator identity')
    recipe = dict(schema='ordered-full-map-evaluation-v1', candidate_sha256=seed['candidate_sha256'],
                  executable_sha256=qualified['full_gap_executable_sha256'], operator_context_sha256=operator,
                  seed_manifest=dict(path=str(seed_manifest), sha256=digest(seed_manifest)),
                  build_manifest=dict(path=str(build_manifest), sha256=digest(build_manifest)),
                  build_qualification=dict(path=str(qualification_path), sha256=digest(qualification_path)))
    entries = {}
    for manifest in (seed, build):
        for item in manifest['files']:
            if item['path'] in entries and entries[item['path']] != item:
                raise ValueError('Conflicting ancestor input identity')
            entries[item['path']] = item
    for path in (seed_manifest, build_manifest, qualification_path, receipt_path, executable,
                 Path(__file__), RESEARCH/'full_map_segment_analysis.py', RESEARCH/'compare_legacy_gap.py',
                 RESEARCH/'public_band_pilot_analysis.py', RESEARCH/'fetch_public_response_inputs.py',
                 RESEARCH/'macos_native_guard_v2.py'):
        entries[str(path)] = dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
    root.mkdir(parents=True); (root/'split').mkdir()
    for name in ('gap-seed.meta', 'gap-seed.bin', 'map-control.in', 'native.in'):
        shutil.copy2(source/name, root/name)
    shutil.copy2(executable, root/'verify-gap-seed.x')
    (root/'seed-control.in').write_text(str(root)+'\n'+operator+'\n')
    (root/'evaluation-context.json').write_text(json.dumps(recipe, sort_keys=True, separators=(',', ':'))+'\n')
    identity = digest(root/'evaluation-context.json')
    (root/'full-map-segment.in').write_text('ordered-full-map-control-v1\n'+identity+'\n-\n0 64\nqualify\n')
    for name in ('gap-seed.meta', 'gap-seed.bin', 'map-control.in', 'native.in', 'verify-gap-seed.x',
                 'seed-control.in', 'evaluation-context.json', 'full-map-segment.in'):
        path = root/name
        entries[str(path)] = dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
    manifest = dict(cwd=str(root), command=[str(root/'verify-gap-seed.x'), '-in', str(root/'native.in')],
                    files=list(entries.values()), candidate_sha256=seed['candidate_sha256'],
                    operator_context_sha256=operator, evaluation_context_sha256=identity,
                    completed_rows=0, last_row=64, previous_directory='-', mode='qualify',
                    guard_seconds=180, launch_normal_seconds=120, group_rss_cap_bytes=3221225472,
                    guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'), scope=__doc__,
                    acceptance='All four images continuous64 vs persisted32+32 bitwise; exact source state and independent occupations; no full residual')
    (root/'run-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('seed_manifest', 'build_manifest', 'destination'):
        parser.add_argument(name, type=Path)
    print(json.dumps(stage(**vars(parser.parse_args())), indent=2))
