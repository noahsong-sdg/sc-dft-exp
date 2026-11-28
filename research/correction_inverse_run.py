"""Own streamed inverse diagnostics on the complete correction-sized sweep."""
import array
import json
import math
from pathlib import Path
import sys

from correction_image_readback import corrected_states
from fetch_public_response_inputs import digest
from full_map_segment_analysis import binary, seed_context
from full_step_segments import certify
from inverse_material_run import check_pins, identity, require
from step_checkpoint_analysis import declared
from stream_inverse_action import apply

RESEARCH=Path(__file__).resolve().parent
OUTPUTS=('inverse-actions.bin','inverse-action-readback.json')


def block(path,start,count):
    values=array.array('d')
    with Path(path).open('rb') as stream:stream.seek(8*start);values.fromfile(stream,count)
    if not all(map(math.isfinite,values)):raise ValueError('Nonfinite inverse source block')
    return values


def stage(full_manifest,full_result,destination):
    full_manifest,full_result,root=map(lambda p:Path(p).absolute(),(full_manifest,full_result,destination))
    if root.exists():raise ValueError('Fresh correction inverse directory required')
    source=json.loads(full_manifest.read_text());prior=Path(source['cwd']);check_pins(source)
    if full_manifest.read_bytes()!=(prior/'run-manifest.json').read_bytes():
        raise ValueError('Different consumed correction sweep')
    entries={x['path']:x for x in source['files']}
    paths=(full_manifest,full_result,prior/'run-manifest.json',prior/'results/moment/receipt.json',
           *(prior/name for name in ('full-map.bin','full-map.txt','linear-image-checkpoint.meta',
              'linear-image-checkpoint.bin','full-map-checkpoint.meta','full-map-checkpoint-state.bin')),
           Path(__file__).resolve(),RESEARCH/'stream_inverse_action.py',RESEARCH/'full_step_segments.py',
           RESEARCH/'correction_image_readback.py',RESEARCH/'macos_native_guard_v2.py',
           Path(sys.executable),Path(sys.executable).resolve())
    for path in paths:
        item=identity(path)
        if str(path) in entries and entries[str(path)]!=item:raise ValueError('Conflicting correction inverse input')
        entries[str(path)]=item
    m=dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],files=list(entries.values()),
           full_manifest=str(full_manifest),full_result=str(full_result),guard_seconds=90,launch_normal_seconds=120,
           group_rss_cap_bytes=3221225472,guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__)
    root.mkdir(parents=True);(root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    return m


def validate(root,m):
    pins=check_pins(m);mp=Path(m['full_manifest']);rp=Path(m['full_result'])
    require(pins,(mp,rp,Path(__file__).resolve(),RESEARCH/'stream_inverse_action.py'))
    parent=json.loads(mp.read_text());prior=Path(parent['cwd'])
    if any(pins.get(x['path'])!=x for x in parent['files']):raise ValueError('Incomplete correction sweep closure')
    require(pins,(prior/'run-manifest.json',prior/'results/moment/receipt.json',
                  *(prior/name for name in ('full-map.bin','full-map.txt','linear-image-checkpoint.meta',
                    'linear-image-checkpoint.bin','full-map-checkpoint.meta','full-map-checkpoint-state.bin'))))
    checked=certify(mp);recorded=json.loads(rp.read_text())
    if any(recorded.get(key)!=value for key,value in checked.items()):raise ValueError('Changed recorded full correction sweep')
    if checked.get('complete_left_row_coverage') is not True or checked.get('full_native_residual_verified') is not True:
        raise ValueError('Complete accepted base residual required')
    recipe=checked['direction_preparation']['recipe'];im=Path(recipe['inverse_manifest']['path'])
    ir=Path(recipe['inverse_result']['path']);require(pins,(im,ir))
    inverse=Path(json.loads(im.read_text())['cwd']);control=(inverse/'inverse-control.in').read_text().splitlines()
    require(pins,(inverse/'inverse-control.in',inverse/'inverse-result.bin',Path(control[1])/'basis.bin'))
    source=json.loads(ir.read_text());n,rank,left,right,maximum=source['dimensions']
    dims,beta,operator,fields=seed_context(prior)
    if ([left,right,maximum]!=dims[:3] or n!=2*maximum or source['beta']!=beta
            or control[4]!=operator or recipe['candidate_sha256']!=digest(prior/'gap-seed.bin')):
        raise ValueError('Different frozen inverse/correction state')
    binding=declared(prior,dims[:3],beta,operator,fields)
    images=binary(prior/'linear-image-checkpoint.bin',4*n)
    states=corrected_states(images,fields[0],binding['direction'],fields[3],dims[:3],binding['step'])
    for label,summary in zip(('base','plus','minus'),states['summaries']):
        if summary!=checked['correction_readback'][label]:raise ValueError('Changed corrected residual reconstruction')
    return inverse,Path(control[1])/'basis.bin',n,rank,binding,states


def run(root):
    root=Path(root).absolute();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if m['cwd']!=str(root) or Path.cwd()!=root or sys.byteorder!='little':raise ValueError('Different correction inverse owner')
    if m['command']!=[sys.executable,str(Path(__file__).resolve())]:raise ValueError('Different correction inverse command')
    if any((root/name).exists() for name in OUTPUTS):raise ValueError('Fresh correction inverse outputs required')
    inverse,basis,n,rank,binding,states=validate(root,m)
    payload=inverse/'inverse-result.bin'
    if payload.stat().st_size!=8*(3*n+rank*rank+rank):raise ValueError('Stale original inverse payload')
    diagonal=block(payload,0,n);small=block(payload,3*n,rank*rank)
    answer=apply(basis,diagonal,small,[array.array('d',(-x for x in states['jacobian'])),states['residuals'][1],states['residuals'][0]])
    direction=binding['direction'];actions=answer.pop('answers')
    original=block(payload,n,n)
    native_error=max(abs(a-b) for a,b in zip(actions[2],original))
    native_bound=1e-30+1e-10*max(abs(x) for values in (actions[2],original) for x in values)
    if native_error>native_bound:raise ValueError('Streamed baseline differs from original native correction')
    with (root/'inverse-actions.bin').open('xb') as stream:
        for values in actions:values.tofile(stream)
    check_pins(m)
    if mp.read_bytes()!=before:raise ValueError('Changed correction inverse manifest')
    result=dict(answer,inputs_unchanged=True,terminal_guard_pass=False,manifest_sha256=digest(mp),
        correction_direction_inverse_defect_ratio=max(abs(a-v) for a,v in zip(actions[0],direction))/max(map(abs,direction)),
        frozen_inverse_plus_residual_infinity_ry=max(map(abs,actions[1])),
        frozen_inverse_plus_residual_over_original_correction=max(map(abs,actions[1]))/binding['step'],
        original_native_correction_max_difference_ry=native_error,original_native_correction_bound_ry=native_bound,
        outputs_sha256={'inverse-actions.bin':digest(root/'inverse-actions.bin')},
        scope='Frozen base-point B on J(base)*v and R(base+c); finite diagnostics, no full-space error bound or new-point inverse.')
    (root/'inverse-action-readback.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result),flush=True);return result


if __name__=='__main__':run(Path.cwd())
