"""Certify candidate-bound correction-step segments and actual restart equality."""
import json
import math
from pathlib import Path

from correction_direction_artifact import certify as certify_direction
from fetch_public_response_inputs import digest
from full_map_segment_analysis import seed_context
from inverse_material_run import identity
from public_band_pilot_analysis import verify_postrun_inputs
from step_checkpoint_analysis import checkpoint, declared


def analyze(directory, manifest_path):
    root = Path(directory).absolute(); manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    if manifest['cwd'] != str(root) or manifest != json.loads((root/'run-manifest.json').read_text()):
        raise ValueError('Different public/consumed segment manifest')
    verify_postrun_inputs(manifest, root)
    receipt = json.loads((root/'results/moment/receipt.json').read_text())
    if (receipt.get('status') != 'PASS' or receipt.get('exit') != 0 or receipt.get('error') is not None
            or receipt['command'] != manifest['command'] or receipt['cwd'] != str(root)
            or receipt['guard_source_sha256'] != manifest['guard_source_sha256']
            or receipt['continuous_deadline_s'] != manifest['guard_seconds']):
        raise ValueError('No matching terminal segment PASS receipt')
    if (not math.isfinite(receipt['wall_s']) or not 0 <= receipt['wall_s'] < manifest['guard_seconds']
            or not 0 <= receipt['max_individual_descendant_rss_bytes'] <= 3221225472
            or not 0 <= receipt['sampled_peak_group_rss_bytes'] <= 3221225472):
        raise ValueError('Invalid segment resource receipt')
    context = manifest['evaluation_context_sha256']
    recipe_file = root/'evaluation-context.json'
    recipe = json.loads(recipe_file.read_text())
    if (digest(recipe_file) != context or recipe['schema'] != 'declared-step-full-map-evaluation-v1'
            or recipe['candidate_sha256'] != manifest['candidate_sha256']
            or recipe['operator_context_sha256'] != manifest['operator_context_sha256']
            or recipe['executable_sha256'] != digest(root/'verify-gap-seed.x')):
        raise ValueError('Different declared evaluation identity')
    pins = {item['path']: item for item in manifest['files']}
    for key in ('seed_manifest', 'build_manifest', 'build_qualification', 'direction_manifest', 'direction_result'):
        ancestor = recipe[key]
        if (digest(Path(ancestor['path'])) != ancestor['sha256']
                or pins.get(ancestor['path']) != identity(ancestor['path'])):
            raise ValueError('Changed evaluation ancestor')
        for item in json.loads(Path(ancestor['path']).read_text()).get('files', []):
            if pins.get(item['path']) != item:
                raise ValueError('Incomplete evaluation ancestor input closure')
    preparation = certify_direction(recipe['direction_manifest']['path'],recipe['direction_result']['path'])
    direction_root = Path(preparation['root'])
    if (preparation['recipe']['candidate_sha256'] != manifest['candidate_sha256']
            or preparation['recipe']['operator_context_sha256'] != manifest['operator_context_sha256']):
        raise ValueError('Different prepared correction context')
    for name in ('direction-state.meta','direction-state.bin','full-map-step.in','direction-recipe.json'):
        if digest(root/name) != digest(direction_root/name):
            raise ValueError('Different prepared correction payload')
    control = (root/'full-map-segment.in').read_text().splitlines()
    expected = ['ordered-full-map-control-v1', context, manifest['previous_directory'],
                f"{manifest['completed_rows']} {manifest['last_row']}", manifest['mode']]
    if control != expected:
        raise ValueError('Changed segment control')
    dims, beta, operator, fields = seed_context(root)
    if digest(root/'gap-seed.bin') != manifest['candidate_sha256'] or operator != manifest['operator_context_sha256']:
        raise ValueError('Changed segment candidate/operator')
    if ((root/'map-control.in').read_text().strip() != (root/'gap-seed.meta').read_text().splitlines()[3]
            or (root/'seed-control.in').read_text().splitlines() != [str(root), operator]):
        raise ValueError('Different native geometry/seed control')
    completed, last = manifest['completed_rows'], manifest['last_row']
    if (manifest['mode'] not in ('qualify', 'segment') or not 0 <= completed < last <= dims[0]
            or completed % 32 or (last != dims[0] and last % 32)):
        raise ValueError('Invalid declared ordered segment range')
    declared_state = declared(root,dims[:3],beta,operator,fields)
    direction,step = declared_state['direction'],declared_state['step']
    main = checkpoint(root, dims[:3], beta, context, manifest['last_row'], fields, direction, step)
    split = None
    if manifest['mode'] == 'qualify':
        if manifest['completed_rows'] != 0 or manifest['last_row'] != 64 or manifest['previous_directory'] != '-':
            raise ValueError('Different split qualification range')
        console = (root/'results/moment/console.log').read_text().splitlines()
        if console.count('FULL_MAP_SPLIT_BITWISE_PASS') != 1:
            raise ValueError('Missing native continuous-versus-restarted equality assertion')
        split = checkpoint(root/'split', dims[:3], beta, context, 32, fields, direction, step)
        if main['sha256']['full-map-checkpoint-state.bin'] != split['sha256']['full-map-checkpoint-state.bin']:
            raise ValueError('Split checkpoint state changed')
        if (main['tile_sum_max_absolute_difference'] < split['tile_sum_max_absolute_difference']
                or main['cumulative_kernel_cpu_s'] < split['cumulative_kernel_cpu_s']):
            raise ValueError('Split diagnostics were not carried forward')
    if manifest['mode'] == 'qualify' or manifest['last_row'] < dims[0]:
        if (root/'full-map.bin').exists() or (root/'full-map.txt').exists():
            raise ValueError('Partial segment unexpectedly emits full-map output')
    return dict(terminal_guard_pass=True, inputs_unchanged=True, verified_input_count=len(manifest['files']),
                checkpoint=main, split_checkpoint=split, receipt=receipt,
                direction_preparation=preparation, declared_state_sha256=declared_state['sha256'],
                microscopic_split_qualified=split is not None, full_native_residual_verified=False,
                physical_response_verified=False, manifest_sha256=digest(manifest_path), scope=__doc__)
