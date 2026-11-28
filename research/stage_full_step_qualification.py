"""Stage a correction-bound actual-input64-versus32+32 test; no launch."""
import argparse
import json
import math
from pathlib import Path
import shutil

from correction_direction_artifact import certify as certify_direction
from fetch_public_response_inputs import digest
from inverse_material_run import identity, require
from full_map_segment_analysis import seed_context
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def stage(seed_manifest, build_manifest, direction_manifest, direction_result, destination):
    seed_manifest, build_manifest, root = map(lambda p: Path(p).absolute(),
                                             (seed_manifest, build_manifest, destination))
    if root.exists():
        raise ValueError('Fresh full-map qualification directory required')
    direction_manifest,direction_result = map(lambda p:Path(p).absolute(),(direction_manifest,direction_result))
    preparation=certify_direction(direction_manifest,direction_result)
    direction_root=Path(preparation['root'])
    direction_source=json.loads(direction_manifest.read_text())
    seed, build = (json.loads(path.read_text()) for path in (seed_manifest, build_manifest))
    source, built = Path(seed['cwd']), Path(build['cwd'])
    for manifest, directory in ((seed, source), (build, built)):
        if manifest != json.loads((directory/'run-manifest.json').read_text()):
            raise ValueError('Different public/consumed parent manifest')
        verify_postrun_inputs(manifest, directory)
    require({x['path']:x for x in build['files']},
            (RESEARCH/'portable_full_step_build.py',RESEARCH/'full_step_checkpoint.f90',
             RESEARCH/'full_nonlinear_step_probe.f90',RESEARCH/'portable_gap/full_step_link.mk'))
    if (len(build['command'])!=4 or build['command'][1:]!=
            [str(RESEARCH/'portable_full_step_build.py'),'run',str(built)]):
        raise ValueError('Different declared-step source builder')
    receipt_path = built/'results/build/receipt.json'
    receipt = json.loads(receipt_path.read_text())
    qualification_path = built/'qualification-result.json'
    qualified = json.loads(qualification_path.read_text())
    executable = built/'full-gap-check.x'
    if (receipt.get('status') != 'PASS' or receipt.get('exit') != 0 or receipt.get('error') is not None
            or receipt['command'] != build['command'] or receipt['cwd'] != str(built)
            or receipt['guard_source_sha256'] != build['guard_source_sha256']
            or receipt['continuous_deadline_s']!=build['guard_seconds']
            or not math.isfinite(receipt['wall_s']) or not 0<receipt['wall_s']<build['guard_seconds']
            or any(not 0<=receipt[k]<=build['group_rss_cap_bytes'] for k in
                   ('max_individual_descendant_rss_bytes','sampled_peak_group_rss_bytes'))
            or qualified.get('checks') != 902 or qualified.get('all_checks_bitwise_equal') is not True
            or qualified.get('full_gap_driver_linked') is not True
            or qualified.get('historical_objects_used') is not False
            or digest(executable) != qualified['full_gap_executable_sha256']):
        raise ValueError('Qualified source-only checkpoint build required')
    dims, _, operator, _ = seed_context(source)
    if dims[0] < 64 or digest(source/'gap-seed.bin') != seed['candidate_sha256'] or operator != seed['operator_context_sha256']:
        raise ValueError('Different full-map seed/operator identity')
    if (preparation['recipe']['candidate_sha256']!=seed['candidate_sha256']
            or preparation['recipe']['operator_context_sha256']!=operator):
        raise ValueError('Different prepared correction/seed context')
    recipe = dict(schema='declared-step-full-map-evaluation-v1', candidate_sha256=seed['candidate_sha256'],
                  executable_sha256=qualified['full_gap_executable_sha256'], operator_context_sha256=operator,
                  seed_manifest=dict(path=str(seed_manifest), sha256=digest(seed_manifest)),
                  build_manifest=dict(path=str(build_manifest), sha256=digest(build_manifest)),
                  build_qualification=dict(path=str(qualification_path), sha256=digest(qualification_path)),
                  direction_manifest=dict(path=str(direction_manifest),sha256=digest(direction_manifest)),
                  direction_result=dict(path=str(direction_result),sha256=digest(direction_result)))
    entries = {}
    for manifest in (seed, build, direction_source):
        for item in manifest['files']:
            if item['path'] in entries and entries[item['path']] != item:
                raise ValueError('Conflicting ancestor input identity')
            entries[item['path']] = item
    for path in (seed_manifest, build_manifest, qualification_path, receipt_path, executable,
                 direction_manifest,direction_result,
                 *(direction_root/name for name in ('direction-state.meta','direction-state.bin','full-map-step.in',
                                                    'direction-recipe.json','direction-preparation-result.json')),
                 direction_root/'run-manifest.json',direction_root/'results/direction/receipt.json',
                 Path(__file__), RESEARCH/'full_map_segment_analysis.py', RESEARCH/'full_step_segment_analysis.py',
                 RESEARCH/'correction_direction_artifact.py',RESEARCH/'step_checkpoint_analysis.py',
                 RESEARCH/'compare_legacy_gap.py',
                 RESEARCH/'public_band_pilot_analysis.py', RESEARCH/'fetch_public_response_inputs.py',
                 RESEARCH/'macos_native_guard_v2.py'):
        item=identity(path)
        if str(path) in entries and entries[str(path)]!=item:
            raise ValueError('Conflicting evaluation input identity')
        entries[str(path)] = item
    root.mkdir(parents=True); (root/'split').mkdir()
    for name in ('gap-seed.meta', 'gap-seed.bin', 'map-control.in', 'native.in'):
        shutil.copy2(source/name, root/name)
    for name in ('direction-state.meta','direction-state.bin','full-map-step.in','direction-recipe.json'):
        shutil.copy2(direction_root/name,root/name)
    shutil.copy2(executable, root/'verify-gap-seed.x')
    (root/'seed-control.in').write_text(str(root)+'\n'+operator+'\n')
    (root/'evaluation-context.json').write_text(json.dumps(recipe, sort_keys=True, separators=(',', ':'))+'\n')
    evaluation_identity = digest(root/'evaluation-context.json')
    (root/'full-map-segment.in').write_text('ordered-full-map-control-v1\n'+evaluation_identity+'\n-\n0 64\nqualify\n')
    for name in ('gap-seed.meta', 'gap-seed.bin', 'map-control.in', 'native.in', 'verify-gap-seed.x',
                 'seed-control.in', 'evaluation-context.json', 'full-map-segment.in',
                 'direction-state.meta','direction-state.bin','full-map-step.in','direction-recipe.json'):
        path = root/name
        entries[str(path)] = dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
    manifest = dict(cwd=str(root), command=[str(root/'verify-gap-seed.x'), '-in', str(root/'native.in')],
                    files=list(entries.values()), candidate_sha256=seed['candidate_sha256'],
                    operator_context_sha256=operator, evaluation_context_sha256=evaluation_identity,
                    completed_rows=0, last_row=64, previous_directory='-', mode='qualify',
                    guard_seconds=180, launch_normal_seconds=120, group_rss_cap_bytes=3221225472,
                    guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'), scope=__doc__,
                    acceptance='All four images continuous64 vs persisted32+32 bitwise; exact source state and independent occupations; no full residual')
    (root/'run-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('seed_manifest', 'build_manifest', 'direction_manifest', 'direction_result', 'destination'):
        parser.add_argument(name, type=Path)
    print(json.dumps(stage(**vars(parser.parse_args())), indent=2))
