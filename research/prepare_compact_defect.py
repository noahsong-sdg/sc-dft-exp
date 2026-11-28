"""Prepare a compact fixed-inverse state from accepted full native actions."""
import array
import json
import math
from pathlib import Path
import sys

from compact_defect_state import FILES,actions,compact,write
from correction_inverse_run import block,validate as full_context
from fetch_public_response_inputs import digest
from full_map_segment_analysis import binary,seed_context
from inverse_material_run import check_pins,identity,require

RESEARCH=Path(__file__).resolve().parent
OUTPUTS=(*FILES,'compact-recipe.json','compact-preparation-result.json')


def stage(manifest,result,destination):
    mp,rp,root=map(lambda p:Path(p).absolute(),(manifest,result,destination))
    if root.exists():raise ValueError('Fresh compact preparation directory required')
    parent=json.loads(mp.read_text());prior=Path(parent['cwd']);check_pins(parent)
    if mp.read_bytes()!=(prior/'run-manifest.json').read_bytes():raise ValueError('Different consumed inverse action source')
    entries={x['path']:x for x in parent['files']}
    for path in (mp,rp,prior/'run-manifest.json',prior/'results/inverse/receipt.json',prior/'inverse-action-readback.json',
                 prior/'inverse-actions.bin',Path(__file__).resolve(),RESEARCH/'compact_defect_state.py',
                 RESEARCH/'compact_defect_io.f90',RESEARCH/'macos_native_guard_v2.py',Path(sys.executable),Path(sys.executable).resolve()):
        item=identity(path)
        if str(path) in entries and entries[str(path)]!=item:raise ValueError('Conflicting compact preparation input')
        entries[str(path)]=item
    m=dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],files=list(entries.values()),
           source_manifest=str(mp),source_result=str(rp),guard_seconds=90,launch_normal_seconds=120,
           group_rss_cap_bytes=3221225472,guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__)
    root.mkdir(parents=True);(root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def inputs(m):
    pins=check_pins(m);mp=Path(m['source_manifest']);rp=Path(m['source_result'])
    require(pins,(mp,rp,Path(__file__).resolve(),RESEARCH/'compact_defect_state.py',RESEARCH/'compact_defect_io.f90'))
    parent=json.loads(mp.read_text());prior=Path(parent['cwd'])
    if any(pins.get(x['path'])!=x for x in parent['files']):raise ValueError('Incomplete compact preparation closure')
    require(pins,(prior/'run-manifest.json',prior/'results/inverse/receipt.json',prior/'inverse-action-readback.json',prior/'inverse-actions.bin'))
    receipt=json.loads((prior/'results/inverse/receipt.json').read_text());raw=json.loads((prior/'inverse-action-readback.json').read_text());recorded=json.loads(rp.read_text())
    if (mp.read_bytes()!=(prior/'run-manifest.json').read_bytes() or receipt['status']!='PASS' or receipt['exit']!=0 or receipt['error'] is not None
            or receipt['command']!=parent['command'] or receipt['cwd']!=parent['cwd']
            or receipt['guard_source_sha256']!=parent['guard_source_sha256'] or receipt['continuous_deadline_s']!=parent['guard_seconds']
            or not 0<receipt['wall_s']<parent['guard_seconds']
            or any(not 0<=receipt[k]<=parent['group_rss_cap_bytes'] for k in ('max_individual_descendant_rss_bytes','sampled_peak_group_rss_bytes'))
            or recorded.get('terminal_guard_pass') is not True
            or recorded.get('receipt')!=receipt or raw.get('terminal_guard_pass') is not False or raw.get('inputs_unchanged') is not True
            or raw.get('manifest_sha256')!=digest(mp) or recorded.get('readback_sha256')!=digest(prior/'inverse-action-readback.json')
            or any(recorded.get(k)!=v for k,v in raw.items() if k!='terminal_guard_pass')
            or raw.get('outputs_sha256')!={'inverse-actions.bin':digest(prior/'inverse-actions.bin')}):
        raise ValueError('Unaccepted compact preparation source')
    errors=raw['independent_action_max_errors'];bounds=raw['independent_action_bounds']
    if len(errors)!=3 or len(bounds)!=3 or any(not (math.isfinite(e) and math.isfinite(b) and 0<=e<=b) for e,b in zip(errors,bounds)):
        raise ValueError('Unaccepted compact source actions')
    inverse,basis,n,rank,binding,states=full_context(prior,parent)
    full=Path(json.loads(Path(parent['full_manifest']).read_text())['cwd']);dims,beta,operator,fields=seed_context(full)
    if n!=2*dims[2]:raise ValueError('Different compact source dimensions')
    payload=inverse/'inverse-result.bin';require(pins,(payload,basis))
    if payload.stat().st_size!=8*(3*n+rank*rank+rank):raise ValueError('Stale compact inverse source')
    original=block(payload,n,n);expected=binary(prior/'inverse-actions.bin',3*n)
    native_error=max(abs(a-b) for a,b in zip(original,expected[2*n:]))
    bound=1e-30+1e-10*max(abs(x) for values in (original,expected[2*n:]) for x in values)
    if native_error>bound:raise ValueError('Compact source differs from native correction')
    diagonal=block(payload,0,n);small=block(payload,3*n,rank*rank)
    rhss=[array.array('d',(-x for x in states['jacobian'])),states['residuals'][1],states['residuals'][0]]
    return basis,[*fields,diagonal],small,dims[:3],rank,beta,operator,rhss,expected


def run(root):
    root=Path(root).absolute();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if m['cwd']!=str(root) or Path.cwd()!=root or m['command']!=[sys.executable,str(Path(__file__).resolve())]:
        raise ValueError('Different compact preparation owner or command')
    if any((root/name).exists() for name in OUTPUTS):raise ValueError('Fresh compact preparation outputs required')
    basis,vectors,small,counts,rank,beta,operator,rhss,expected=inputs(m)
    result=write(root,basis,vectors,small,counts,rank,beta,operator,digest(Path(m['source_manifest'])))
    packed=[compact(rhs,counts,True) for rhs in rhss];chosen=actions(root,sum(counts[:2]),rank,packed)
    n=2*counts[2];errors=[];bounds=[]
    for k,answer in enumerate(chosen):
        reference=compact(expected[k*n:(k+1)*n],counts,True)
        error=max(abs(a-b) for a,b in zip(answer,reference));bound=1e-30+1e-10*max(abs(x) for block in (answer,reference) for x in block)
        if error>bound:raise ValueError('Chosen compact W differs from accepted inverse action')
        errors.append(error);bounds.append(bound)
    recipe=dict(schema='compact-defect-preparation-v1',source_manifest=identity(m['source_manifest']),source_result=identity(m['source_result']),
                source_basis=identity(basis),vector_order=['gap','xi','dk','Z','D'],basis_order='all active left, then all active right; columns in Fortran order',
                chosen_W='Columns solve the stored nonsymmetric M against unit vectors; fixed binary64 W, not an exact inverse assumption.',
                calibration_max_errors=errors,calibration_bounds=bounds,**result)
    (root/'compact-recipe.json').write_text(json.dumps(recipe,indent=2,allow_nan=False)+'\n')
    check_pins(m)
    if before!=mp.read_bytes():raise ValueError('Changed compact preparation manifest')
    result.update(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),recipe=recipe,
                  outputs={name:identity(root/name) for name in OUTPUTS if name!='compact-preparation-result.json'})
    (root/'compact-preparation-result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result),flush=True);return result


if __name__=='__main__':run(Path.cwd())
