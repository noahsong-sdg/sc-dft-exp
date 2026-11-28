"""Own selected defect rows before deciding whether a full second sweep is worthwhile."""
import json
import math
from pathlib import Path
import shutil

from compact_defect_readback import controls
from compact_p_readback import integers,records,timings
from compact_p_segment import analyze as p_analyze
from compact_tile_material import accepted,COPIED
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require

RESEARCH=Path(__file__).resolve().parent


def parents(p_manifest,p_result,action_result,build_manifest,build_result):
    mp,rp,ap,bmp,brp=map(lambda x:Path(x).absolute(),(p_manifest,p_result,action_result,build_manifest,build_result))
    m=json.loads(mp.read_text());recorded=json.loads(rp.read_text());checked=p_analyze(mp)
    if any(recorded.get(k)!=v for k,v in checked.items()) or checked.get('complete_P') is not True:raise ValueError('Unaccepted full P defect parent')
    pins=check_pins(m);action=json.loads(ap.read_text())
    if (action.get('accepted_complete_P_manifest_sha256')!=digest(mp) or action.get('accepted_complete_P_result_sha256')!=digest(rp)
            or action.get('complete_P') is not True or action.get('inputs_unchanged') is not True
            or action.get('independent_full_P_action_controls_passed') is not True or action.get('controls')!=m['counts'][3]):
        raise ValueError('Unaccepted P saved-image controls')
    for path,item in action['bindings'].items():
        if identity(Path(path))!=item:raise ValueError('Changed saved-image action binding')
    for path in (mp,rp,Path(m['cwd'])/'compact-p.bin',RESEARCH/'compact_p_action_readback.py',RESEARCH/'compact_p_actions.py'):
        if action['bindings'].get(str(path))!=identity(path):raise ValueError('Missing P action binding')
    fields=[action.get(k,[]) for k in ('left_P_Dv','right_QT_D_ADv','absolute_errors','bounds')]
    if any(len(x)!=m['counts'][3] for x in fields):raise ValueError('Incomplete P action controls')
    for a,b,e,bound in zip(*fields):
        if not all(map(math.isfinite,(a,b,e,bound))) or e!=abs(a-b) or not 0<=e<=bound:raise ValueError('Invalid P action control')
    if action['max_absolute_error']!=max(fields[2]) or action['max_error_over_bound']!=max(e/b for e,b in zip(fields[2],fields[3])):
        raise ValueError('Different P action summary')
    bm,br,bp=accepted(bmp,brp,'build','compact-build-result.json')
    if (br.get('fresh_compile_count')!=19 or br.get('build_plan_matches_console') is not True or br.get('cache_checks')!=902
            or br.get('cache_all_bitwise_equal') is not True or br.get('historical_custom_objects_used') is not False
            or br.get('material_runtime_qualified') is not False):raise ValueError('Unqualified defect native build')
    for path,item in bp.items():
        if path in pins and pins[path]!=item:raise ValueError('Conflicting defect closure')
        pins[path]=item
    root=Path(m['cwd']);qual=json.loads(Path(m['predecessor_manifest']).read_text());selected=json.loads(Path(qual['selected_manifest']).read_text())
    prep=json.loads(Path(selected['preparation_manifest']).read_text());compact=Path(prep['cwd']);counts=m['counts']
    if min(counts[:2])<64:raise ValueError('Selected defect needs two native tiles')
    for path in (mp,rp,ap,root/'run-manifest.json',root/'results/material/receipt.json',root/'results/material/console.log',root/'campaign_launch_watch.json',
                 *(root/name for name in recorded['outputs']),*(Path(p) for p in action['bindings']),
                 RESEARCH/'compact_defect_material.py',RESEARCH/'compact_defect_readback.py',RESEARCH/'macos_native_guard_v2.py'):
        item=identity(path)
        if item['path'] in pins and pins[item['path']]!=item:raise ValueError('Conflicting defect parent identity')
        pins[item['path']]=item
    require(pins,(compact/name for name in ('compact-state.meta','compact-state.bin','compact-q.bin','compact-u.bin','compact-w.bin')))
    return m,prep,bm,pins


def control(root,p,prep):
    meta=(Path(prep['cwd'])/'compact-state.meta').read_text().splitlines()
    return {'seed-control.in':str(root)+'\n'+meta[3]+'\n',
            'compact-defect-control.in':'compact-full-defect-v1\n'+prep['cwd']+'\n'+str(p['counts'][3])+'\n'+'\n'.join(meta[3:])+'\n'+p['fingerprint']+'\n'+p['cwd']+'\n64 64\n'}


def stage(p_manifest,p_result,action_result,build_manifest,build_result,destination):
    root=Path(destination).absolute()
    if root.exists():raise ValueError('Fresh defect material directory required')
    p,prep,bm,pins=parents(p_manifest,p_result,action_result,build_manifest,build_result);source=Path(p['cwd'])
    root.mkdir(parents=True)
    for name in COPIED:shutil.copy2(source/name,root/name)
    shutil.copy2(Path(bm['cwd'])/'full-gap-check.x',root/'compact-defect-native.x')
    for name,text in control(root,p,prep).items():(root/name).write_text(text)
    for name in (*COPIED,'compact-defect-native.x','seed-control.in','compact-defect-control.in'):pins[str(root/name)]=identity(root/name)
    m=dict(cwd=str(root),command=[str(root/'compact-defect-native.x'),'-in',str(root/'native.in')],files=list(pins.values()),
           p_manifest=str(Path(p_manifest).absolute()),p_result=str(Path(p_result).absolute()),action_result=str(Path(action_result).absolute()),
           build_manifest=str(Path(build_manifest).absolute()),build_result=str(Path(build_result).absolute()),
           counts=p['counts'],fingerprint=p['fingerprint'],stops=[64,64],guard_seconds=90,launch_normal_seconds=120,
           group_rss_cap_bytes=3221225472,guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__,
           acceptance='Six independent partial/full row samples and all-rank C samples; NOT full-space norm or outward certificate')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def analyze(manifest):
    mp=Path(manifest).absolute();m=json.loads(mp.read_text());root=Path(m['cwd']);pins=check_pins(m)
    p,prep,bm,pp=parents(*(m[k] for k in ('p_manifest','p_result','action_result','build_manifest','build_result')))
    if any(pins.get(k)!=v for k,v in pp.items()):raise ValueError('Incomplete defect parent closure')
    if (mp.read_bytes()!=(root/'run-manifest.json').read_bytes() or m['counts']!=p['counts'] or m['fingerprint']!=p['fingerprint'] or m['stops']!=[64,64]
            or m['command']!=[str(root/'compact-defect-native.x'),'-in',str(root/'native.in')]
            or m['guard_seconds']!=90 or m['launch_normal_seconds']!=120 or m['group_rss_cap_bytes']!=3221225472
            or m['guard_source_sha256']!=digest(RESEARCH/'macos_native_guard_v2.py')):raise ValueError('Different selected defect owner')
    for name,text in control(root,p,prep).items():
        if (root/name).read_text()!=text:raise ValueError('Different defect native control')
    for name in COPIED:
        if digest(root/name)!=digest(Path(p['cwd'])/name):raise ValueError('Different defect native input')
    if digest(root/'compact-defect-native.x')!=digest(Path(bm['cwd'])/'full-gap-check.x'):raise ValueError('Different defect executable')
    require(pins,(root/name for name in (*COPIED,'compact-defect-native.x','seed-control.in','compact-defect-control.in')))
    receipt=json.loads((root/'results/material/receipt.json').read_text())
    if (receipt['status']!='PASS' or receipt['exit']!=0 or receipt['error'] is not None or receipt['command']!=m['command'] or receipt['cwd']!=m['cwd']
            or receipt['guard_source_sha256']!=m['guard_source_sha256'] or receipt['continuous_deadline_s']!=90
            or not math.isfinite(receipt['wall_s']) or not 0<receipt['wall_s']<90
            or any(not 0<=receipt[k]<=3221225472 for k in ('max_individual_descendant_rss_bytes','sampled_peak_group_rss_bytes'))
            or json.loads((root/'campaign_launch_watch.json').read_text())['phase']!='completed'):raise ValueError('Unaccepted defect receipt')
    console=(root/'results/material/console.log').read_text()
    if console.count('COMPACT_DEFECT_PARTIAL; NOT a full-space norm')!=1 or 'COMPACT_DEFECT_COMPLETE;' in console:raise ValueError('Different defect coverage marker')
    checked=controls(root,prep['cwd'],p['cwd'],m['counts'][:2],m['counts'][3],[64,64])
    if (root/'compact-defect.meta').read_text().splitlines()[3]!=m['fingerprint']:raise ValueError('Different defect fingerprint')
    progress=records(root/'compact-defect-progress.txt',4);previous=[0.]*4
    for line,(phase,last) in zip(progress,((1,32),(1,64),(2,32),(2,64))):
        fields=line.split()
        if len(fields)!=7 or integers(' '.join(fields[:3]),3)!=[phase,last,64]:raise ValueError('Different defect progress coverage')
        cpu=timings(' '.join(fields[3:]),4)
        if any(a>b for a,b in zip(previous,cpu)):raise ValueError('Decreasing defect CPU')
        previous=cpu
    if previous!=checked['cpu_s']:raise ValueError('Different final defect CPU')
    outputs={name:identity(root/name) for name in ('compact-c.bin','compact-defect-rows.bin','defect-kernel-left.bin','defect-kernel-right.bin','compact-defect.meta','compact-defect-progress.txt')}
    check_pins(m)
    return dict(terminal_guard_pass=True,inputs_unchanged=True,manifest_sha256=digest(mp),verified_input_count=len(pins),receipt=receipt,
                **checked,outputs=outputs,full_space_norm_measured=False)
