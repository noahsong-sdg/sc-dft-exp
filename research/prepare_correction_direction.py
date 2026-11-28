"""Bind a normalized compressed correction to the exact accepted candidate."""
import array
from contextlib import chdir
import json
import hashlib
import math
from pathlib import Path
import sys

from fetch_public_response_inputs import digest
from inverse_material_run import check_pins, identity, require, validate as validate_inverse
from low_rank_inverse_analysis import analyze as inverse_arithmetic, values

RESEARCH = Path(__file__).resolve().parent
OUTPUTS = ('direction-state.meta','direction-state.bin','full-map-step.in',
           'direction-recipe.json','direction-preparation-result.json')


def certify_inverse(manifest_path, result_path):
    manifest_path, result_path = map(Path,(manifest_path,result_path))
    m = json.loads(manifest_path.read_text()); root = Path(m['cwd'])
    if manifest_path.read_bytes() != (root/'run-manifest.json').read_bytes():
        raise ValueError('Different consumed inverse manifest')
    with chdir(root):
        checked_manifest = validate_inverse(root)
    if checked_manifest != m:
        raise ValueError('Different validated inverse manifest')
    receipt = json.loads((root/'results/inverse/receipt.json').read_text())
    result = json.loads(result_path.read_text())
    raw = json.loads((root/'inverse-readback.json').read_text())
    if (receipt.get('status') != 'PASS' or receipt.get('exit') != 0 or receipt.get('error') is not None
            or receipt['command'] != m['command'] or receipt['cwd'] != str(root)
            or receipt['guard_source_sha256'] != m['guard_source_sha256']
            or receipt['continuous_deadline_s'] != m['guard_seconds']
            or not math.isfinite(receipt['wall_s']) or not 0 < receipt['wall_s'] < m['guard_seconds']
            or any(not 0 <= receipt[k] <= m['group_rss_cap_bytes'] for k in
                   ('max_individual_descendant_rss_bytes','sampled_peak_group_rss_bytes'))
            or result.get('terminal_guard_pass') is not True or result.get('inputs_unchanged') is not True
            or result['receipt'] != receipt or result['manifest_sha256'] != digest(manifest_path)
            or result['readback_sha256'] != digest(root/'inverse-readback.json')
            or raw.get('terminal_guard_pass') is not False or raw.get('inputs_unchanged') is not True):
        raise ValueError('Unqualified inverse direction source')
    for name,sha in result['outputs_sha256'].items():
        if digest(root/name) != sha:
            raise ValueError('Changed inverse direction source output')
    for key,value in raw.items():
        if key not in ('terminal_guard_pass','scope') and result.get(key) != value:
            raise ValueError('Changed recorded inverse readback')
    arithmetic = inverse_arithmetic(root)
    for key,value in arithmetic.items():
        if key != 'scope' and (result.get(key) != value or raw.get(key) != value):
            raise ValueError('Independent inverse replay differs')
    if arithmetic['full_source_residual_targets_met'] is not True:
        raise ValueError('Unaccepted inverse source residual')
    return m,arithmetic


def write_direction(root, candidate, correction, counts, beta, operator):
    root = Path(root)
    if len(counts) != 3:
        raise ValueError('Invalid correction direction dimensions')
    n = 2*counts[2]
    if (min(counts) <= 0 or counts[2] != max(counts[:2])
            or len(candidate) != n or len(correction) != n
            or not math.isfinite(beta) or beta <= 0 or len(operator) != 64
            or any(c not in '0123456789abcdef' for c in operator)
            or not all(math.isfinite(x) for a in (candidate,correction) for x in a)):
        raise ValueError('Invalid correction direction context/state')
    scale = max(map(abs,correction))
    if scale <= 0 or not math.isfinite(2*scale):
        raise ValueError('Invalid correction direction scale')
    for side,count in enumerate(counts[:2]):
        sl = slice(side*counts[2]+count,(side+1)*counts[2])
        if any(candidate[sl]) or any(correction[sl]):
            raise ValueError('Nonzero correction direction padding')
    if any((root/name).exists() for name in OUTPUTS):
        raise ValueError('Fresh correction direction outputs required')
    direction = array.array('d',(x/scale for x in correction))
    error = max(abs(scale*v-c) for v,c in zip(direction,correction))
    (root/'direction-state.meta').write_text('declared-full-map-direction-v1\n'
        +' '.join(map(str,counts))+f'\n{beta:.17g}\n{operator}\n')
    with (root/'direction-state.bin').open('wb') as target:
        array.array('d',candidate).tofile(target);direction.tofile(target)
    (root/'full-map-step.in').write_text(f'declared-full-map-step-v1\n{scale:.17g}\n')
    return dict(step_ry=scale,direction_infinity=max(map(abs,direction)),
                rescaled_correction_max_absolute_difference_ry=error,
                rescaled_correction_relative_difference=error/scale,
                candidate_sha256=hashlib.sha256(array.array('d',candidate).tobytes()).hexdigest(),
                sha256={name:digest(root/name) for name in OUTPUTS[:3]})


def stage(inverse_manifest, inverse_result, destination):
    inverse_manifest,inverse_result,root = map(lambda p:Path(p).absolute(),
                                              (inverse_manifest,inverse_result,destination))
    if root.exists():
        raise ValueError('Fresh correction preparation directory required')
    source = json.loads(inverse_manifest.read_text()); prior = Path(source['cwd'])
    check_pins(source)
    if inverse_manifest.read_bytes() != (prior/'run-manifest.json').read_bytes():
        raise ValueError('Different consumed inverse source')
    entries = {x['path']:x for x in source['files']}
    paths = (inverse_manifest,inverse_result,prior/'run-manifest.json',prior/'results/inverse/receipt.json',
             prior/'inverse-readback.json',prior/'inverse-result.txt',prior/'inverse-result.bin',
             Path(__file__).resolve(),RESEARCH/'inverse_material_run.py',RESEARCH/'low_rank_inverse_analysis.py',
             RESEARCH/'macos_native_guard_v2.py',Path(sys.executable),Path(sys.executable).resolve())
    for path in paths:
        item = identity(path)
        if str(path) in entries and entries[str(path)] != item:
            raise ValueError('Conflicting correction preparation input')
        entries[str(path)] = item
    manifest = dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],
                    files=list(entries.values()),inverse_manifest=str(inverse_manifest),inverse_result=str(inverse_result),
                    guard_seconds=90,launch_normal_seconds=120,group_rss_cap_bytes=3221225472,
                    guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),
                    scope='Prepare exact accepted candidate/normalized correction/step; no microscopic action or new gap acceptance.')
    root.mkdir(parents=True)
    (root/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def run(root):
    root = Path(root).absolute(); manifest_path = root/'run-manifest.json'
    before = manifest_path.read_bytes(); m = json.loads(before)
    if m['cwd'] != str(root) or Path.cwd() != root or sys.byteorder != 'little':
        raise ValueError('Different correction preparation owner/byte order')
    if any((root/name).exists() for name in OUTPUTS):
        raise ValueError('Fresh correction preparation outputs required')
    pins = check_pins(m)
    for path in (Path(m['inverse_manifest']),Path(m['inverse_result']),Path(__file__).resolve()):
        if pins.get(str(path)) != identity(path):
            raise ValueError('Missing correction preparation source binding')
    parent = json.loads(Path(m['inverse_manifest']).read_text())
    prior = Path(parent['cwd'])
    require(pins,(prior/'run-manifest.json',prior/'results/inverse/receipt.json',
                  prior/'inverse-readback.json',prior/'inverse-result.txt',prior/'inverse-result.bin'))
    if any(pins.get(x['path']) != x for x in parent['files']):
        raise ValueError('Incomplete inverse preparation closure')
    print('Recertifying inverse source and exhaustive arithmetic',flush=True)
    inverse,arithmetic = certify_inverse(m['inverse_manifest'],m['inverse_result'])
    source = Path(inverse['cwd']); control = (source/'inverse-control.in').read_text().splitlines()
    n,rank,left,right,maximum = arithmetic['dimensions']; counts = [left,right,maximum]
    payload = values(source/'inverse-result.bin',3*n+rank*rank+rank)
    candidate = values(Path(control[3])/'gap-seed.bin',n)
    data = write_direction(root,candidate,payload[n:2*n],counts,arithmetic['beta'],control[4])
    if data['step_ry'] != arithmetic['correction_infinity_ry']:
        raise ValueError('Correction scale differs from inverse readback')
    recipe = dict(schema='compressed-correction-direction-v1',**data,
                  inverse_manifest=dict(path=m['inverse_manifest'],sha256=digest(Path(m['inverse_manifest']))),
                  inverse_result=dict(path=m['inverse_result'],sha256=digest(Path(m['inverse_result']))),
                  operator_context_sha256=control[4],beta=arithmetic['beta'],counts=counts,
                  source_correction_sha256=digest(source/'inverse-result.bin'))
    (root/'direction-recipe.json').write_text(json.dumps(recipe,sort_keys=True,separators=(',',':'))+'\n')
    check_pins(m)
    if before != manifest_path.read_bytes():raise ValueError('Changed correction preparation manifest')
    result = dict(inputs_unchanged=True,terminal_guard_pass=False,manifest_sha256=digest(manifest_path),
                  recipe=recipe,recipe_sha256=digest(root/'direction-recipe.json'),
                  conditioned_gap_error_bounded=False,physical_response_verified=False,
                  scope='Direction preparation arithmetic complete; owning terminal guard required.')
    (root/'direction-preparation-result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)
    return result


if __name__ == '__main__':
    run(Path.cwd())
