"""Own complete ordered joint A/P pass after accepted pilot; no inverse adoption."""
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys

from compact_tile_material import accepted,COPIED
from enrichment_action_material import stage as selected_stage
from enrichment_action_readback import controls
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require

RESEARCH=Path(__file__).resolve().parent
OUTPUTS=('enrichment-actions.bin','enrichment-p.bin','enrichment-kernel-left.bin','enrichment-kernel-right.bin',
         'enrichment-action.meta','enrichment-progress.txt')


def stage(pilot_manifest,pilot_result,preparation,preparation_result,build,build_result,destination):
    pilot,recorded,pp=accepted(pilot_manifest,pilot_result,'material','enrichment-readback.json')
    replay=controls(pilot['cwd'],pilot['compact'],pilot['trials'],pilot['counts'][:2],pilot['counts'][2],64)
    if any(recorded.get(k)!=v for k,v in replay.items()) or recorded['complete_A_and_P'] is not False:
        raise ValueError('Unqualified selected enrichment pilot')
    m=selected_stage(preparation,preparation_result,build,build_result,destination);root=Path(m['cwd'])
    if any(m[k]!=pilot[k] for k in ('compact','trials','counts')) or digest(root/'enrichment-native.x')!=digest(Path(pilot['cwd'])/'enrichment-native.x'):
        raise ValueError('Different full enrichment context')
    control=root/'enrichment-action-control.in';lines=control.read_text().splitlines()
    if lines[-1]!='64':raise ValueError('Different selected predecessor control')
    lines[-1]=str(m['counts'][0]);control.write_text('\n'.join(lines)+'\n')
    pins={item['path']:item for item in m['files']}
    for path,item in pp.items():
        if path in pins and pins[path]!=item:raise ValueError('Conflicting full enrichment closure')
        pins[path]=item
    for p in (control,Path(__file__).resolve()):
        item=identity(p);pins[item['path']]=item
    m.update(command=[sys.executable,str(Path(__file__).resolve())],files=list(pins.values()),
             stop=m['counts'][0],guard_seconds=900,scope=__doc__,pilot_manifest=str(Path(pilot_manifest).resolve()),
             pilot_result=str(Path(pilot_result).resolve()))
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def run(root):
    root=Path(root).resolve();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if Path.cwd()!=root or m['cwd']!=str(root) or m['command']!=[sys.executable,str(Path(__file__).resolve())] or m['stop']!=m['counts'][0] or m['guard_seconds']!=900:raise ValueError('Different selected enrichment owner')
    if any((root/name).exists() for name in (*OUTPUTS,'enrichment-readback.json')):raise ValueError('Fresh enrichment outputs required')
    pins=check_pins(m);require(pins,(root/name for name in (*COPIED,'enrichment-native.x','seed-control.in','enrichment-action-control.in')))
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    done=subprocess.run([str(root/'enrichment-native.x'),'-in',str(root/'native.in')],cwd=root,env=env,check=True,capture_output=True,text=True)
    print(done.stdout,end='');print(done.stderr,end='',file=sys.stderr)
    if (len(re.findall(r'ENRICHMENT_ACTION_PASS_COMPLETE rows=\s*'+str(m['stop'])+r'\s+left=\s*'+str(m['counts'][0])+r'\b',done.stdout))!=1
            or 'INCOMPLETE A/P' in done.stdout):raise ValueError('Different enrichment console coverage')
    checked=controls(root,m['compact'],m['trials'],m['counts'][:2],m['counts'][2],m['stop']);check_pins(m)
    if mp.read_bytes()!=before:raise ValueError('Changed enrichment owner manifest')
    out=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),**checked,
             outputs={name:identity(root/name) for name in OUTPUTS})
    (root/'enrichment-readback.json').write_text(json.dumps(out,indent=2)+'\n');return out


if __name__=='__main__':run(Path.cwd())
