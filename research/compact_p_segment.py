"""Resume the qualified material64-row P checkpoint through the actual final row."""
import json
import math
from pathlib import Path
import re
import shutil

from compact_p_material import analyze as qualify_analyze,parents
from compact_p_readback import checkpoint,integers,timings
from compact_tile_material import COPIED
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require

RESEARCH=Path(__file__).resolve().parent


def predecessor(manifest,result):
    mp,rp=map(lambda x:Path(x).absolute(),(manifest,result));m=json.loads(mp.read_text());recorded=json.loads(rp.read_text())
    replayed=qualify_analyze(mp)
    if (any(recorded.get(k)!=v for k,v in replayed.items()) or set(recorded)-set(replayed)-{'postread_wall_s','postread_maxrss_bytes'}
            or any(not math.isfinite(recorded[k]) or recorded[k]<=0 for k in ('postread_wall_s','postread_maxrss_bytes') if k in recorded)
            or replayed.get('material_restart_qualified') is not True or replayed['continuous_checkpoint']['completed_left_rows']!=64):
        raise ValueError('Unaccepted material P restart predecessor')
    sm,selected,prep,pr,bm,fp,counts,_=parents(*(m[k] for k in ('selected_manifest','selected_result','build_manifest','build_result','registration')))
    root=Path(m['cwd']);pins=check_pins(m)
    for path in (mp,rp,root/'run-manifest.json',root/'results/material/receipt.json',root/'results/material/console.log',root/'campaign_launch_watch.json'):
        pins[str(path)]=identity(path)
    for name,item in recorded['outputs'].items():
        if identity(root/name)!=item:raise ValueError('Changed P predecessor output')
        if item['path'] in pins and pins[item['path']]!=item:raise ValueError('Conflicting P predecessor output')
        pins[item['path']]=item
    for name in ('compact_p_segment.py','compact_p_readback.py','macos_native_guard_v2.py'):
        path=RESEARCH/name;pins[str(path)]=identity(path)
    return m,replayed,prep,pr,fp,counts,pins


def controls(root,prior,prep,pr,fp,counts):
    meta=(Path(prep['cwd'])/'compact-state.meta').read_text().splitlines()
    return {'seed-control.in':str(root)+'\n'+pr['operator_sha256']+'\n',
            'compact-P-control.in':'ordered-compact-P-pass-v1\n'+prep['cwd']+'\n'+str(pr['rank'])+'\n'+'\n'.join(meta[3:])+'\n'+fp+'\n'+prior['cwd']+'\n64 '+str(counts[0])+'\nsegment\n'}


def stage(predecessor_manifest,predecessor_result,destination):
    root=Path(destination).absolute()
    if root.exists():raise ValueError('Fresh full P segment directory required')
    prior,recorded,prep,pr,fp,counts,pins=predecessor(predecessor_manifest,predecessor_result)
    if counts[0]<=64:raise ValueError('No remaining P rows')
    source=Path(prior['cwd']);root.mkdir(parents=True)
    for name in (*COPIED,'compact-P-native.x'):shutil.copy2(source/name,root/name)
    for name,text in controls(root,prior,prep,pr,fp,counts).items():(root/name).write_text(text)
    for name in (*COPIED,'compact-P-native.x','seed-control.in','compact-P-control.in'):pins[str(root/name)]=identity(root/name)
    m=dict(cwd=str(root),command=[str(root/'compact-P-native.x'),'-in',str(root/'native.in')],files=list(pins.values()),
           predecessor_manifest=str(Path(predecessor_manifest).absolute()),predecessor_result=str(Path(predecessor_result).absolute()),
           fingerprint=fp,counts=counts,completed_before=64,stop_at=counts[0],guard_seconds=900,launch_normal_seconds=120,
           group_rss_cap_bytes=3221225472,guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__,
           acceptance='Contiguous full P coverage, exact qualified predecessor, finite checkpoint; no norm or response acceptance')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def progress(path,left,initial_cpu,final_cpu):
    if not 0<Path(path).stat().st_size<=16384:raise ValueError('Invalid P segment progress size')
    lines=Path(path).read_text().splitlines()
    expected=[min(first+31,left) for first in range(65,left+1,32) if (first-1)%1024==0 or min(first+31,left)==left]
    if len(lines)!=len(expected):raise ValueError('Incomplete P segment progress')
    previous=initial_cpu
    for line,last in zip(lines,expected):
        fields=line.split()
        if len(fields)!=4 or integers(' '.join(fields[:2]),2)!=[last,left]:raise ValueError('Different P segment progress coverage')
        cpu=timings(' '.join(fields[2:]),2)
        if any(a>b for a,b in zip(previous,cpu)):raise ValueError('Decreasing P segment CPU')
        previous=cpu
    if previous!=final_cpu:raise ValueError('Different P final progress CPU')
    return len(lines)


def analyze(manifest):
    mp=Path(manifest).absolute();m=json.loads(mp.read_text());root=Path(m['cwd']);pins=check_pins(m)
    prior,recorded,prep,pr,fp,counts,parentpins=predecessor(m['predecessor_manifest'],m['predecessor_result'])
    if any(pins.get(k)!=v for k,v in parentpins.items()):raise ValueError('Incomplete full P closure')
    if (mp.read_bytes()!=(root/'run-manifest.json').read_bytes() or m['fingerprint']!=fp or m['counts']!=counts
            or m['command']!=[str(root/'compact-P-native.x'),'-in',str(root/'native.in')] or m['completed_before']!=64 or m['stop_at']!=counts[0]
            or m['guard_source_sha256']!=digest(RESEARCH/'macos_native_guard_v2.py') or m['guard_seconds']!=900
            or m['launch_normal_seconds']!=120 or m['group_rss_cap_bytes']!=3221225472):raise ValueError('Different full P owner')
    for name,text in controls(root,prior,prep,pr,fp,counts).items():
        if (root/name).read_text()!=text:raise ValueError('Different full P control')
    for name in (*COPIED,'compact-P-native.x'):
        if digest(root/name)!=digest(Path(prior['cwd'])/name):raise ValueError('Different full P native input')
    require(pins,(root/name for name in (*COPIED,'compact-P-native.x','seed-control.in','compact-P-control.in')))
    receipt=json.loads((root/'results/material/receipt.json').read_text())
    if (receipt['status']!='PASS' or receipt['exit']!=0 or receipt['error'] is not None or receipt['command']!=m['command'] or receipt['cwd']!=m['cwd']
            or receipt['guard_source_sha256']!=m['guard_source_sha256'] or receipt['continuous_deadline_s']!=900
            or not math.isfinite(receipt['wall_s']) or not 0<receipt['wall_s']<900
            or any(not 0<=receipt[k]<=3221225472 for k in ('max_individual_descendant_rss_bytes','sampled_peak_group_rss_bytes'))
            or json.loads((root/'campaign_launch_watch.json').read_text())['phase']!='completed'):raise ValueError('Unaccepted full P receipt')
    console=(root/'results/material/console.log').read_text()
    marker=rf'COMPACT_P_PASS_COMPLETE rows=\s*{counts[0]}\s+left=\s*{counts[0]}\s+mode=segment'
    if len(re.findall(marker,console))!=1 or console.count('COMPACT_P_PASS_COMPLETE')!=1 or 'INCOMPLETE P;' in console:raise ValueError('Incomplete full P console')
    checked=checkpoint(root,counts[:2],pr['rank'],counts[0],fp)
    with (root/'compact-p.bin').open('rb') as new,(Path(prior['cwd'])/'compact-p.bin').open('rb') as old:
        if new.read(8*64*pr['rank'])!=old.read(8*64*pr['rank']):raise ValueError('Changed completed left P columns')
    samples=progress(root/'compact-P-progress.txt',counts[0],recorded['continuous_checkpoint']['cpu_s'],checked['cpu_s'])
    outputs={name:identity(root/name) for name in ('compact-p.meta','compact-p.bin','compact-P-progress.txt')};check_pins(m)
    return dict(terminal_guard_pass=True,inputs_unchanged=True,manifest_sha256=digest(mp),verified_input_count=len(pins),receipt=receipt,
                fingerprint=fp,checkpoint=checked,progress_records=samples,completed_left_prefix_bitwise_equal=True,outputs=outputs,
                complete_P=True,independent_full_P_action_controls_passed=False,full_space_norm_measured=False,conditioned_gap_error_bounded=False,physical_response_verified=False)
