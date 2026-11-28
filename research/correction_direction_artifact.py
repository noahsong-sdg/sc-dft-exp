"""Verify immutable preparation evidence and exact correction normalization."""
import array
import json
import math
import sys
from pathlib import Path

from fetch_public_response_inputs import digest
from inverse_material_run import check_pins, identity, require
from low_rank_inverse_analysis import values

OUTPUTS = ('direction-state.meta','direction-state.bin','full-map-step.in',
           'direction-recipe.json','direction-preparation-result.json')


def certify(manifest_path, result_path):
    manifest_path,result_path = map(Path,(manifest_path,result_path))
    m=json.loads(manifest_path.read_text());root=Path(m['cwd'])
    if manifest_path.read_bytes() != (root/'run-manifest.json').read_bytes():
        raise ValueError('Different consumed correction preparation')
    pins=check_pins(m)
    helper=Path(__file__).with_name('prepare_correction_direction.py').resolve()
    require(pins,(helper,Path(m['inverse_manifest']),Path(m['inverse_result'])))
    if len(m['command']) != 2 or m['command'][1] != str(helper):
        raise ValueError('Different correction preparation producer')
    r=json.loads((root/'results/direction/receipt.json').read_text())
    raw=json.loads((root/'direction-preparation-result.json').read_text())
    result=json.loads(result_path.read_text());recipe=json.loads((root/'direction-recipe.json').read_text())
    if (r.get('status')!='PASS' or r.get('exit')!=0 or r.get('error') is not None
            or r['command']!=m['command'] or r['cwd']!=str(root)
            or r['guard_source_sha256']!=m['guard_source_sha256']
            or r['continuous_deadline_s']!=m['guard_seconds']
            or not math.isfinite(r['wall_s']) or not 0<r['wall_s']<m['guard_seconds']
            or any(not 0<=r[k]<=m['group_rss_cap_bytes'] for k in
                   ('max_individual_descendant_rss_bytes','sampled_peak_group_rss_bytes'))
            or result.get('terminal_guard_pass') is not True or result.get('inputs_unchanged') is not True
            or result['receipt']!=r or result['manifest_sha256']!=digest(manifest_path)
            or result['readback_sha256']!=digest(root/'direction-preparation-result.json')
            or raw.get('terminal_guard_pass') is not False or raw.get('inputs_unchanged') is not True
            or raw['recipe']!=recipe or raw['recipe_sha256']!=digest(root/'direction-recipe.json')):
        raise ValueError('Unqualified correction preparation receipt/result')
    for key,value in raw.items():
        if key not in ('terminal_guard_pass','scope') and result.get(key)!=value:
            raise ValueError('Changed recorded correction preparation')
    if set(result['output_files'])!=set(OUTPUTS):
        raise ValueError('Incomplete correction preparation outputs')
    for name in OUTPUTS:
        if result['output_files'][name]!=identity(root/name):
            raise ValueError('Changed correction preparation output')
    parent=json.loads(Path(m['inverse_manifest']).read_text());prior=Path(parent['cwd'])
    if any(pins.get(x['path'])!=x for x in parent['files']):
        raise ValueError('Incomplete inverse preparation closure')
    for key in ('inverse_manifest','inverse_result'):
        if recipe[key]!=dict(path=m[key],sha256=digest(Path(m[key]))):
            raise ValueError('Different correction preparation ancestor')
    inverse=json.loads(Path(m['inverse_result']).read_text());n,rank,left,right,maximum=inverse['dimensions']
    require(pins,(prior/'inverse-result.bin',prior/'inverse-control.in'))
    control=(prior/'inverse-control.in').read_text().splitlines();full=Path(control[3])
    require(pins,(full/'gap-seed.bin',full/'gap-seed.meta'))
    payload=prior/'inverse-result.bin'
    if sys.byteorder!='little' or payload.stat().st_size!=8*(3*n+rank*rank+rank):
        raise ValueError('Stale correction source binary shape/byte order')
    original=array.array('d')
    with payload.open('rb') as stream:
        stream.seek(8*n);original.fromfile(stream,n)
    if not all(map(math.isfinite,original)):
        raise ValueError('Nonfinite correction source')
    candidate=values(full/'gap-seed.bin',n);state=values(root/'direction-state.bin',2*n)
    scale=max(map(abs,original))
    if not math.isfinite(scale) or scale<=0:
        raise ValueError('Invalid artifact correction scale')
    expected=array.array('d',(x/scale for x in original));error=max(abs(scale*v-c) for v,c in zip(expected,original))
    if (recipe['schema']!='compressed-correction-direction-v1'
            or recipe['counts']!=[left,right,maximum] or n!=2*maximum
            or recipe['beta']!=inverse['beta'] or recipe['operator_context_sha256']!=control[4]
            or recipe['step_ry']!=scale or scale!=inverse['correction_infinity_ry']
            or recipe['candidate_sha256']!=digest(full/'gap-seed.bin')
            or recipe['source_correction_sha256']!=digest(prior/'inverse-result.bin')
            or state[:n].tobytes()!=candidate.tobytes() or state[n:].tobytes()!=expected.tobytes()
            or recipe['direction_infinity']!=max(map(abs,expected)) or max(map(abs,expected))!=1
            or recipe['rescaled_correction_max_absolute_difference_ry']!=error
            or recipe['rescaled_correction_relative_difference']!=error/scale):
        raise ValueError('Different correction normalization/candidate recipe')
    meta=['declared-full-map-direction-v1',f'{left} {right} {maximum}',f"{inverse['beta']:.17g}",control[4]]
    if ((root/'direction-state.meta').read_text().splitlines()!=meta
            or (root/'full-map-step.in').read_text().splitlines()!=['declared-full-map-step-v1',f'{scale:.17g}']):
        raise ValueError('Different direction artifact metadata/step')
    for name in OUTPUTS[:3]:
        if recipe['sha256'].get(name)!=digest(root/name):raise ValueError('Changed recipe payload hash')
    for side,count in enumerate((left,right)):
        sl=slice(side*maximum+count,(side+1)*maximum)
        if any(candidate[sl]) or any(expected[sl]):raise ValueError('Nonzero artifact padding')
    return dict(root=str(root),recipe=recipe,receipt=r,manifest_sha256=digest(manifest_path),
                result_sha256=digest(result_path),terminal_guard_pass=True,inputs_unchanged=True,
                conditioned_gap_error_bounded=False,physical_response_verified=False)
