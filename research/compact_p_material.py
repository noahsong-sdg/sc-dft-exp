"""Own a bounded material64-row continuous versus32+32 P restart qualification."""
import json
import math
from pathlib import Path
import shutil

from compact_p_context import fingerprint
from compact_p_readback import qualification
from compact_tile_material import accepted,COPIED
from compact_tile_readback import analyze as selected_analyze
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require

RESEARCH=Path(__file__).resolve().parent


def parents(selected_manifest,selected_result,build_manifest,build_result,registration):
    smp,srp,bmp,brp,rp=map(lambda x:Path(x).absolute(),(selected_manifest,selected_result,build_manifest,build_result,registration))
    sm=json.loads(smp.read_text());selected=json.loads(srp.read_text())
    replayed=selected_analyze(smp)
    if (any(selected.get(k)!=v for k,v in replayed.items())
            or set(selected)-set(replayed)-{'postread_maxrss_bytes','postread_wall_s'}
            or any(not math.isfinite(selected[k]) or selected[k]<=0 for k in ('postread_maxrss_bytes','postread_wall_s') if k in selected)):
        raise ValueError('Different accepted selected material result')
    prep,pr,pp=accepted(sm['preparation_manifest'],sm['preparation_result'],'prepare','compact-preparation-result.json')
    bm,br,bp=accepted(bmp,brp,'build','compact-build-result.json')
    if (br.get('fresh_compile_count')!=19 or br.get('build_plan_matches_console') is not True
            or br.get('cache_checks')!=902 or br.get('cache_all_bitwise_equal') is not True
            or br.get('historical_custom_objects_used') is not False or br.get('material_runtime_qualified') is not False):
        raise ValueError('Unqualified ordered P build')
    pins=check_pins(sm)
    def add(item):
        if item['path'] in pins and pins[item['path']]!=item:raise ValueError('Conflicting P material closure')
        pins[item['path']]=item
    for closure in (pp,bp):
        for item in closure.values():add(item)
    selected_root=Path(sm['cwd'])
    for path in (smp,srp,selected_root/'run-manifest.json',selected_root/'results/material/receipt.json',
                 selected_root/'results/material/console.log',selected_root/'campaign_launch_watch.json',rp):add(identity(path))
    for name,item in selected['outputs'].items():
        if identity(selected_root/name)!=item:raise ValueError('Changed accepted selected P output')
        add(item)
    compact=Path(prep['cwd']);source=Path(sm['native_source_directory']);exe=Path(bm['cwd'])/'full-gap-check.x';sdk=Path(bm['defect_blas'])
    meta=(source/'gap-seed.meta').read_text().splitlines();dims=list(map(int,meta[1].split()))
    if len(meta)!=5 or meta[0]!='gap-seed-v1; binary64 Fortran order' or len(dims)!=6:raise ValueError('Stale native P seed context')
    counts=[*dims[:3],pr['rank']]
    if (dims[0]<64 or float(meta[2])!=pr['beta'] or meta[4]!=pr['operator_sha256']
            or digest(source/'gap-seed.bin')!=pr['padded_candidate_sha256']):raise ValueError('Different native P seed')
    bindings=dict(Q=compact/'compact-q.bin',state=compact/'compact-state.bin',executable=exe,blas=sdk,native_seed_metadata=source/'gap-seed.meta')
    require(pins,bindings.values());require(pins,(source/name for name in COPIED))
    fp,dependencies=fingerprint(counts,dims[3:],pr['beta'],pr['operator_sha256'],pr['padded_candidate_sha256'],
                                bindings['Q'],bindings['state'],exe,sdk)
    reg=json.loads(rp.read_text())
    if (reg.get('schema')!='compact-P-context-registration-v1' or reg.get('fingerprint')!=fp or reg.get('dependencies')!=dependencies
            or reg.get('context_producer')!=identity(RESEARCH/'compact_p_context.py')
            or reg.get('accepted_preparation')!=identity(Path(sm['preparation_result'])) or reg.get('accepted_build')!=identity(brp)
            or reg.get('file_bindings')!={k:identity(v) for k,v in bindings.items()}
            or any(reg.get(k) is not False for k in ('material_restart_qualified','complete_P','full_space_norm_measured'))):
        raise ValueError('Stale registered P dependency context')
    for name in ('compact_p_material.py','compact_p_context.py','compact_p_readback.py','macos_native_guard_v2.py'):add(identity(RESEARCH/name))
    return sm,selected,prep,pr,bm,fp,counts,pins


def controls(root,sm,prep,pr,fp):
    meta=(Path(prep['cwd'])/'compact-state.meta').read_text().splitlines()
    return {'seed-control.in':str(root)+'\n'+pr['operator_sha256']+'\n',
            'compact-P-control.in':'ordered-compact-P-pass-v1\n'+prep['cwd']+'\n'+str(pr['rank'])+'\n'+'\n'.join(meta[3:])+'\n'+fp+'\n-\n0 64\nqualify\n'}


def stage(selected_manifest,selected_result,build_manifest,build_result,registration,destination):
    root=Path(destination).absolute()
    if root.exists():raise ValueError('Fresh P material directory required')
    sm,selected,prep,pr,bm,fp,counts,pins=parents(selected_manifest,selected_result,build_manifest,build_result,registration)
    root.mkdir(parents=True);(root/'split').mkdir()
    for name in COPIED:shutil.copy2(Path(sm['native_source_directory'])/name,root/name)
    shutil.copy2(Path(bm['cwd'])/'full-gap-check.x',root/'compact-P-native.x')
    for name,text in controls(root,sm,prep,pr,fp).items():(root/name).write_text(text)
    for name in (*COPIED,'compact-P-native.x','seed-control.in','compact-P-control.in'):pins[str(root/name)]=identity(root/name)
    m=dict(cwd=str(root),command=[str(root/'compact-P-native.x'),'-in',str(root/'native.in')],files=list(pins.values()),
           selected_manifest=str(Path(selected_manifest).absolute()),selected_result=str(Path(selected_result).absolute()),
           build_manifest=str(Path(build_manifest).absolute()),build_result=str(Path(build_result).absolute()),registration=str(Path(registration).absolute()),
           fingerprint=fp,counts=counts,guard_seconds=90,launch_normal_seconds=120,group_rss_cap_bytes=3221225472,
           guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__,
           acceptance='Continuous64 equals accepted selected material P; checkpoint32+32 bitwise replay; no full P or norm')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def analyze(manifest):
    mp=Path(manifest).absolute();m=json.loads(mp.read_text());root=Path(m['cwd']);pins=check_pins(m)
    sm,selected,prep,pr,bm,fp,counts,parentpins=parents(*(m[k] for k in ('selected_manifest','selected_result','build_manifest','build_result','registration')))
    if any(pins.get(k)!=v for k,v in parentpins.items()):raise ValueError('Incomplete P material closure')
    if (mp.read_bytes()!=(root/'run-manifest.json').read_bytes() or m['fingerprint']!=fp or m['counts']!=counts
            or m['command']!=[str(root/'compact-P-native.x'),'-in',str(root/'native.in')]
            or m['guard_source_sha256']!=digest(RESEARCH/'macos_native_guard_v2.py')
            or m['guard_seconds']!=90 or m['launch_normal_seconds']!=120 or m['group_rss_cap_bytes']!=3221225472):raise ValueError('Different P material owner')
    for name,text in controls(root,sm,prep,pr,fp).items():
        if (root/name).read_text()!=text:raise ValueError('Different P native control')
    for name in COPIED:
        if digest(root/name)!=digest(Path(sm['native_source_directory'])/name):raise ValueError('Different P native input')
    if digest(root/'compact-P-native.x')!=digest(Path(bm['cwd'])/'full-gap-check.x'):raise ValueError('Different P native executable')
    require(pins,(root/name for name in (*COPIED,'compact-P-native.x','seed-control.in','compact-P-control.in')))
    receipt=json.loads((root/'results/material/receipt.json').read_text())
    if (receipt['status']!='PASS' or receipt['exit']!=0 or receipt['error'] is not None or receipt['command']!=m['command'] or receipt['cwd']!=m['cwd']
            or receipt['guard_source_sha256']!=m['guard_source_sha256'] or receipt['continuous_deadline_s']!=90
            or not math.isfinite(receipt['wall_s']) or not 0<receipt['wall_s']<90
            or any(not 0<=receipt[k]<=3221225472 for k in ('max_individual_descendant_rss_bytes','sampled_peak_group_rss_bytes'))
            or json.loads((root/'campaign_launch_watch.json').read_text())['phase']!='completed'):raise ValueError('Unaccepted P material receipt')
    console=(root/'results/material/console.log').read_text()
    if console.count('COMPACT_P_PASS_COMPLETE')!=1 or 'INCOMPLETE P; no coefficient or norm acceptance' not in console:raise ValueError('Incomplete P qualification console')
    checked=qualification(root,counts[:2],pr['rank'],fp,selected['outputs']['compact-partial-p.bin']['sha256'])
    outputs={name:identity(root/name) for name in ('compact-p.meta','compact-p.bin','split/compact-p.meta','split/compact-p.bin','compact-P-qualification.txt','compact-P-progress.txt')}
    check_pins(m)
    return dict(terminal_guard_pass=True,inputs_unchanged=True,manifest_sha256=digest(mp),verified_input_count=len(pins),receipt=receipt,
                fingerprint=fp,material_restart_qualified=True,**checked,outputs=outputs,conditioned_gap_error_bounded=False,physical_response_verified=False)
