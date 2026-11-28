"""Own selected64-row joint A/P material pilot; no augmented inverse adoption."""
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys

from compact_tile_material import accepted,COPIED
from enrichment_action_readback import controls
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require

RESEARCH=Path(__file__).resolve().parent
OUTPUTS=('enrichment-actions.bin','enrichment-p.bin','enrichment-kernel-left.bin','enrichment-kernel-right.bin',
         'enrichment-action.meta','enrichment-progress.txt')


def stage(preparation,preparation_result,build,build_result,destination):
    root=Path(destination).resolve()
    if root.exists():raise ValueError('Fresh enrichment material owner required')
    prep,pr,pins=accepted(preparation,preparation_result,'prepare','trial-readback.json')
    bm,br,bp=accepted(build,build_result,'build','compact-build-result.json')
    if (pr['extra_columns']!=3 or pr['A_actions_available'] is not False or pr['inverse_adopted'] is not False
            or br['fresh_compile_count']!=19 or br['cache_checks']!=902 or br['cache_all_bitwise_equal'] is not True
            or br['build_plan_matches_console'] is not True or br['historical_custom_objects_used'] is not False):raise ValueError('Unqualified enrichment parents')
    for path,item in bp.items():
        if path in pins and pins[path]!=item:raise ValueError('Conflicting enrichment input closure')
        pins[path]=item
    old=RESEARCH/'compact_defect_material001_manifest.json';require(pins,(old,));source=Path(json.loads(old.read_text())['cwd'])
    require(pins,(source/name for name in COPIED))
    compact=Path(prep['compact']);counts=prep['counts'];meta=(compact/'compact-state.meta').read_text().splitlines()
    if len(meta)!=6 or list(map(int,meta[1].split()))!=[*counts[:2],max(counts[:2]),counts[2]]:raise ValueError('Different enrichment compact geometry')
    root.mkdir(parents=True)
    for name in COPIED:shutil.copy2(source/name,root/name)
    shutil.copy2(Path(bm['cwd'])/'full-gap-check.x',root/'enrichment-native.x')
    control='enrichment-action-pass-v1\n'+str(compact)+'\n'+str(counts[2])+'\n'+'\n'.join(meta[3:])+'\n'+prep['cwd']+'\n64\n'
    (root/'enrichment-action-control.in').write_text(control);(root/'seed-control.in').write_text(str(root)+'\n'+meta[3]+'\n')
    for p in (Path(__file__).resolve(),RESEARCH/'enrichment_action_readback.py',RESEARCH/'macos_native_guard_v2.py',
              Path(sys.executable),Path(sys.executable).resolve(),*(root/name for name in (*COPIED,'enrichment-native.x','seed-control.in','enrichment-action-control.in'))):
        item=identity(p);pins[item['path']]=item
    m=dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],files=list(pins.values()),
           compact=str(compact),trials=prep['cwd'],counts=counts,stop=64,guard_seconds=90,launch_normal_seconds=120,
           group_rss_cap_bytes=3221225472,guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__)
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def run(root):
    root=Path(root).resolve();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if Path.cwd()!=root or m['cwd']!=str(root) or m['command']!=[sys.executable,str(Path(__file__).resolve())] or m['stop']!=64:raise ValueError('Different selected enrichment owner')
    if any((root/name).exists() for name in (*OUTPUTS,'enrichment-readback.json')):raise ValueError('Fresh enrichment outputs required')
    pins=check_pins(m);require(pins,(root/name for name in (*COPIED,'enrichment-native.x','seed-control.in','enrichment-action-control.in')))
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    done=subprocess.run([str(root/'enrichment-native.x'),'-in',str(root/'native.in')],cwd=root,env=env,check=True,capture_output=True,text=True)
    print(done.stdout,end='');print(done.stderr,end='',file=sys.stderr)
    if (len(re.findall(r'ENRICHMENT_ACTION_PASS_COMPLETE rows=\s*64\s+left=\s*'+str(m['counts'][0])+r'\b',done.stdout))!=1
            or done.stdout.count('INCOMPLETE A/P; no inverse qualification')!=1):raise ValueError('Different enrichment console coverage')
    checked=controls(root,m['compact'],m['trials'],m['counts'][:2],m['counts'][2],64);check_pins(m)
    if mp.read_bytes()!=before:raise ValueError('Changed enrichment owner manifest')
    out=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),**checked,
             outputs={name:identity(root/name) for name in OUTPUTS})
    (root/'enrichment-readback.json').write_text(json.dumps(out,indent=2)+'\n');return out


if __name__=='__main__':run(Path.cwd())
