"""Own a saved-data secant diagnostic, including the pre-existing separate probe."""
import array
import json
import math
from pathlib import Path
import sys

from correction_inverse_run import block,validate as full_context
from fetch_public_response_inputs import digest
from full_map_segment_analysis import binary
from inverse_material_run import check_pins,identity,require
from secant_inverse_action import action,factors

RESEARCH=Path(__file__).resolve().parent
OUTPUTS=('secant-actions.bin','secant-readback.json')


def stage(manifest,result,destination):
    mp,rp,root=map(lambda p:Path(p).absolute(),(manifest,result,destination))
    if root.exists():raise ValueError('Fresh secant directory required')
    parent=json.loads(mp.read_text());prior=Path(parent['cwd']);check_pins(parent)
    if mp.read_bytes()!=(prior/'run-manifest.json').read_bytes():raise ValueError('Different consumed inverse diagnostic')
    entries={x['path']:x for x in parent['files']}
    for path in (mp,rp,prior/'run-manifest.json',prior/'results/inverse/receipt.json',
                 prior/'inverse-actions.bin',prior/'inverse-action-readback.json',
                 Path(__file__).resolve(),RESEARCH/'secant_inverse_action.py',
                 RESEARCH/'macos_native_guard_v2.py',Path(sys.executable),Path(sys.executable).resolve()):
        item=identity(path)
        if str(path) in entries and entries[str(path)]!=item:raise ValueError('Conflicting secant input')
        entries[str(path)]=item
    m=dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],files=list(entries.values()),
           diagnostic_manifest=str(mp),diagnostic_result=str(rp),guard_seconds=60,launch_normal_seconds=120,
           group_rss_cap_bytes=3221225472,guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__)
    root.mkdir(parents=True);(root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def accepted(m):
    pins=check_pins(m);mp=Path(m['diagnostic_manifest']);rp=Path(m['diagnostic_result'])
    require(pins,(mp,rp,Path(__file__).resolve(),RESEARCH/'secant_inverse_action.py'))
    parent=json.loads(mp.read_text());prior=Path(parent['cwd'])
    if any(pins.get(x['path'])!=x for x in parent['files']):raise ValueError('Incomplete inverse diagnostic closure')
    paths=[prior/name for name in ('run-manifest.json','results/inverse/receipt.json','inverse-actions.bin','inverse-action-readback.json')]
    require(pins,paths)
    if mp.read_bytes()!=paths[0].read_bytes():raise ValueError('Changed consumed inverse diagnostic')
    receipt=json.loads(paths[1].read_text());raw=json.loads(paths[3].read_text());result=json.loads(rp.read_text())
    if (receipt['status']!='PASS' or receipt['exit']!=0 or receipt['error'] is not None
            or receipt['command']!=parent['command'] or receipt['cwd']!=parent['cwd']
            or receipt['guard_source_sha256']!=parent['guard_source_sha256']
            or receipt['continuous_deadline_s']!=parent['guard_seconds']
            or not 0<receipt['wall_s']<parent['guard_seconds']
            or not 0<receipt['max_individual_descendant_rss_bytes']<=parent['group_rss_cap_bytes']
            or not 0<=receipt['sampled_peak_group_rss_bytes']<=parent['group_rss_cap_bytes']
            or result.get('receipt')!=receipt or result.get('terminal_guard_pass') is not True
            or raw.get('terminal_guard_pass') is not False or raw.get('inputs_unchanged') is not True
            or raw.get('manifest_sha256')!=digest(mp) or result.get('readback_sha256')!=digest(paths[3])
            or raw.get('outputs_sha256')!={'inverse-actions.bin':digest(paths[2])}
            or any(result.get(k)!=v for k,v in raw.items() if k!='terminal_guard_pass')):
        raise ValueError('Unaccepted source inverse diagnostic')
    errors=raw['independent_action_max_errors'];bounds=raw['independent_action_bounds']
    if len(errors)!=3 or len(bounds)!=3 or any(not (math.isfinite(e) and math.isfinite(b) and 0<=e<=b) for e,b in zip(errors,bounds)):
        raise ValueError('Unaccepted inverse equation controls')
    inverse,basis,n,rank,binding,states=full_context(prior,parent)
    actions=binary(paths[2],3*n)
    old_full=Path((inverse/'inverse-control.in').read_text().splitlines()[3])
    require(pins,(old_full/'full-map.bin',inverse/'inverse-result.bin'))
    old=binary(old_full/'full-map.bin',4*n)
    if old[n:2*n]!=states['residuals'][0]:raise ValueError('Different separate-probe base residual')
    v=binding['direction'];original=block(inverse/'inverse-result.bin',n,n)
    expected=dict(correction_direction_inverse_defect_ratio=max(abs(a-b) for a,b in zip(actions[:n],v))/max(map(abs,v)),
                  frozen_inverse_plus_residual_infinity_ry=max(map(abs,actions[n:2*n])),
                  frozen_inverse_plus_residual_over_original_correction=max(map(abs,actions[n:2*n]))/binding['step'],
                  original_native_correction_max_difference_ry=max(abs(a-b) for a,b in zip(actions[2*n:],original)))
    if (any(raw[k]!=value for k,value in expected.items())
            or not math.isfinite(raw['original_native_correction_bound_ry'])
            or not 0<=expected['original_native_correction_max_difference_ry']<=raw['original_native_correction_bound_ry']):
        raise ValueError('Changed inverse diagnostic metric')
    # Original saved probe block is B*J*vold-vold, not B*J*vold.
    old_direction=old[2*n:3*n];old_j=array.array('d',(-x for x in old[3*n:]))
    old_defect=block(inverse/'inverse-result.bin',2*n,n)
    old_action=array.array('d',(a+b for a,b in zip(old_direction,old_defect)))
    return n,binding,states,actions,old_direction,old_j,old_action


def run(root):
    root=Path(root).absolute();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if m['cwd']!=str(root) or Path.cwd()!=root or m['command']!=[sys.executable,str(Path(__file__).resolve())]:
        raise ValueError('Different secant owner or command')
    if any((root/name).exists() for name in OUTPUTS):raise ValueError('Fresh secant outputs required')
    n,binding,states,base,old_v,old_j,old_bj=accepted(m)
    v=binding['direction'];jv=array.array('d',(-x for x in states['jacobian']))
    u,w=factors(v,jv,base[:n])
    rhss=(jv,old_j,states['residuals'][0],states['residuals'][1])
    prior=(base[:n],old_bj,base[2*n:],base[n:2*n])
    updated=[action(u,w,rhs,b) for rhs,b in zip(rhss,prior)]
    norm=lambda x:max(map(abs,x))
    defect=lambda a,b:norm([x-y for x,y in zip(a,b)])/norm(b)
    metrics=dict(training_defect_before=defect(prior[0],v),training_defect_after=defect(updated[0],v),
                 separate_probe_defect_before=defect(prior[1],old_v),separate_probe_defect_after=defect(updated[1],old_v),
                 base_correction_before_ry=norm(prior[2]),base_correction_after_ry=norm(updated[2]),
                 plus_correction_before_ry=norm(prior[3]),plus_correction_after_ry=norm(updated[3]))
    if metrics['training_defect_after']>1e-12:raise ValueError('Secant training equation differs')
    with (root/'secant-actions.bin').open('xb') as stream:
        for values in (u,w,*updated):values.tofile(stream)
    check_pins(m)
    if before!=mp.read_bytes():raise ValueError('Changed secant manifest')
    result=dict(metrics,inputs_unchanged=True,terminal_guard_pass=False,manifest_sha256=digest(mp),
                outputs_sha256={'secant-actions.bin':digest(root/'secant-actions.bin')},
                conditioned_gap_error_bounded=False,physical_response_verified=False,
                scope='One fitted secant direction and one pre-existing separate probe; no full-space bound or updated nonlinear sweep.')
    (root/'secant-readback.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result),flush=True);return result


if __name__=='__main__':run(Path.cwd())
