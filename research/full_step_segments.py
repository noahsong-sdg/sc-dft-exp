"""Stage and certify correction-step coverage and saved plus/minus residuals."""
import argparse
import json
from pathlib import Path
import shutil

from fetch_public_response_inputs import digest
from full_map_segment_analysis import binary, seed_context
from full_step_segment_analysis import analyze
from full_map_segments import normalization_readback
from correction_image_readback import corrected_states
from step_checkpoint_analysis import declared
from verify_gap_candidate_step import verify

RESEARCH = Path(__file__).resolve().parent
OUTPUTS = ('linear-image-checkpoint.meta', 'linear-image-checkpoint.bin',
           'full-map-checkpoint.meta', 'full-map-checkpoint-state.bin')


def certify(manifest_path):
    return _certify(Path(manifest_path).absolute(), {}, set())


def recorded_result(path, checked):
    recorded = json.loads(Path(path).read_text())
    if (recorded.get('terminal_guard_pass') is not True or recorded.get('inputs_unchanged') is not True
            or recorded.get('manifest_sha256') != checked['manifest_sha256']
            or recorded.get('receipt') != checked['receipt']
            or recorded.get('checkpoint', {}).get('sha256') != checked['checkpoint']['sha256']
            or recorded.get('microscopic_split_qualified') != checked['microscopic_split_qualified']):
        raise ValueError('Predecessor differs from its recorded certification')


def _certify(manifest_path, cache, visiting):
    key = str(manifest_path)
    if key in visiting:
        raise ValueError('Cyclic full-map predecessor chain')
    if key in cache:
        return cache[key]
    visiting.add(key)
    manifest = json.loads(manifest_path.read_text()); root = Path(manifest['cwd'])
    checked = analyze(root, manifest_path)
    checked.update(lineage_depth=0, lineage_native_wall_s=checked['receipt']['wall_s'],
                   qualification_manifest=key, qualification_manifest_sha256=digest(manifest_path))
    if manifest['mode'] == 'segment':
        previous_path = Path(manifest['previous_manifest']).absolute()
        previous_manifest = json.loads(previous_path.read_text())
        previous_root = Path(previous_manifest['cwd'])
        previous = _certify(previous_path, cache, visiting)
        recorded_result(manifest['previous_result'], previous)
        if (manifest['previous_directory'] != str(previous_root)
                or manifest['completed_rows'] != previous['checkpoint']['completed_rows']
                or manifest['evaluation_context_sha256'] != previous_manifest['evaluation_context_sha256']
                or manifest['qualification_manifest'] != previous['qualification_manifest']
                or manifest['qualification_manifest_sha256'] != previous['qualification_manifest_sha256']
                or checked['checkpoint']['sha256']['full-map-checkpoint-state.bin']
                != previous['checkpoint']['sha256']['full-map-checkpoint-state.bin']):
            raise ValueError('Noncontiguous or changed full-map predecessor')
        pins = {item['path']: item for item in manifest['files']}
        for item in previous_manifest['files']:
            if pins.get(item['path']) != item:
                raise ValueError('Incomplete predecessor input closure')
        for path in (previous_path, Path(manifest['previous_result']), previous_root/'run-manifest.json', previous_root/'results/moment/receipt.json',
                     *(previous_root/name for name in OUTPUTS)):
            if pins.get(str(path)) != dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path)):
                raise ValueError('Missing immutable predecessor output binding')
        for field in ('tile_sum_max_absolute_difference', 'cumulative_kernel_cpu_s'):
            if checked['checkpoint'][field] < previous['checkpoint'][field]:
                raise ValueError('Restart diagnostics decreased')
        checked.update(lineage_depth=previous['lineage_depth']+1,
                       lineage_native_wall_s=previous['lineage_native_wall_s']+checked['receipt']['wall_s'],
                       qualification_manifest=previous['qualification_manifest'],
                       qualification_manifest_sha256=previous['qualification_manifest_sha256'])
    elif not checked['microscopic_split_qualified']:
        raise ValueError('Unqualified full-map chain origin')
    completed = checked['checkpoint']['completed_rows']
    full_count = checked['checkpoint']['dimensions'][0]
    checked['complete_left_row_coverage'] = manifest['mode'] == 'segment' and completed == full_count
    if checked['complete_left_row_coverage']:
        checked['full_candidate'] = verify(root, manifest_path)
        checked['normalization_readback'] = normalization_readback(root)
        checked['correction_readback'] = correction_readback(root)
        checked['full_native_residual_verified'] = checked['full_candidate']['stationary_residual_targets_met']
    visiting.remove(key); cache[key] = checked
    return checked


def correction_readback(root):
    dims,beta,operator,fields=seed_context(root);n=2*dims[2]
    binding=declared(root,dims[:3],beta,operator,fields)
    with (root/'full-map.bin').open('rb') as stream:
        stream.seek(16*n)
        if stream.read(8*n)!=binding['direction'].tobytes():
            raise ValueError('Final native direction differs from declared correction')
    images=binary(root/'linear-image-checkpoint.bin',4*n)
    readback=corrected_states(images,fields[0],binding['direction'],fields[3],dims[:3],binding['step'])
    return dict(base=readback['summaries'][0],plus=readback['summaries'][1],minus=readback['summaries'][2],
                independent_fd_error=readback['independent_fd_error'],independent_fd_bound=readback['independent_fd_bound'],
                step_ry=binding['step'],sha256=dict(binding['sha256'],
                    images=digest(root/'linear-image-checkpoint.bin')),
                conditioned_gap_error_bounded=False,physical_response_verified=False)


def stage(previous_manifest, previous_result, destination, last_row, guard_seconds=480):
    previous_path, root = map(lambda p: Path(p).absolute(), (previous_manifest, destination))
    if root.exists():
        raise ValueError('Fresh full-map segment directory required')
    accepted = certify(previous_path)
    previous_result = Path(previous_result).absolute()
    recorded_result(previous_result, accepted)
    previous = json.loads(previous_path.read_text()); source = Path(previous['cwd'])
    completed = accepted['checkpoint']['completed_rows']; full_count = accepted['checkpoint']['dimensions'][0]
    if (not completed < last_row <= full_count or completed % 32
            or (last_row != full_count and last_row % 32) or not 0 < guard_seconds <= 480):
        raise ValueError('Invalid bounded ordered segment admission')
    entries = {item['path']: item for item in previous['files']}
    for path in (previous_path, previous_result, source/'run-manifest.json', source/'results/moment/receipt.json',
                 *(source/name for name in OUTPUTS), Path(__file__), RESEARCH/'verify_gap_candidate_step.py',RESEARCH/'full_step_summary_analysis.py',
                 RESEARCH/'correction_image_readback.py',RESEARCH/'step_checkpoint_analysis.py'):
        entries[str(path)] = dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
    root.mkdir(parents=True)
    copied = ('gap-seed.meta', 'gap-seed.bin', 'map-control.in', 'native.in',
              'verify-gap-seed.x', 'evaluation-context.json', 'direction-state.meta', 'direction-state.bin',
              'full-map-step.in','direction-recipe.json')
    for name in copied:
        shutil.copy2(source/name, root/name)
    (root/'seed-control.in').write_text(str(root)+'\n'+previous['operator_context_sha256']+'\n')
    (root/'full-map-segment.in').write_text('ordered-full-map-control-v1\n'
        +previous['evaluation_context_sha256']+'\n'+str(source)+f'\n{completed} {last_row}\nsegment\n')
    for name in (*copied, 'seed-control.in', 'full-map-segment.in'):
        path = root/name
        entries[str(path)] = dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
    manifest = dict(previous, cwd=str(root), command=[str(root/'verify-gap-seed.x'), '-in', str(root/'native.in')],
                    files=list(entries.values()), previous_manifest=str(previous_path), previous_directory=str(source),
                    previous_result=str(previous_result),
                    completed_rows=completed, last_row=last_row, mode='segment', guard_seconds=guard_seconds,
                    qualification_manifest=accepted['qualification_manifest'],
                    qualification_manifest_sha256=accepted['qualification_manifest_sha256'],
                    scope=__doc__, acceptance='Certified contiguous predecessor/state, unchanged arithmetic and final gates; no partial residual acceptance')
    (root/'run-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('stage'); p.add_argument('previous_manifest', type=Path)
    p.add_argument('previous_result', type=Path)
    p.add_argument('destination', type=Path); p.add_argument('last_row', type=int)
    p.add_argument('--guard-seconds', type=int, default=480)
    p = sub.add_parser('certify'); p.add_argument('manifest_path', type=Path)
    args = vars(parser.parse_args()); action = args.pop('action')
    print(json.dumps((stage if action == 'stage' else certify)(**args), indent=2, allow_nan=False))
