"""Build/check fixed-row enriched inverse diagnostic from accepted saved inputs."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from compact_tile_material import accepted
from resolved_action_readback import controls
from resolved_inverse_readback import check
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require

RESEARCH=Path(__file__).resolve().parent
OUTPUTS=('inverse.x','inverse-build-command.json','enriched-m.bin','enriched-w.bin','enriched-c.bin','enriched-rows.bin',
         'baseline-rows.bin','enriched-norms.bin','enriched-qgram.bin','enriched-singular.bin')


def stage(manifest,result,destination):
    full,recorded,pins=accepted(manifest,result,'material','resolved-action-readback.json');root=Path(destination).resolve()
    if root.exists():raise ValueError('Fresh enriched inverse owner required')
    replay=controls(full['cwd'],full['compact'],full['trials'],full['counts'][:2],full['counts'][2],full['stop'])
    if any(recorded.get(k)!=v for k,v in replay.items()) or recorded['complete_A_and_P'] is not True:raise ValueError('Incomplete enriched inverse action parent')
    oldmp=RESEARCH/'compact_defect_material001_manifest.json';require(pins,(oldmp,));old=json.loads(oldmp.read_text())
    pmp=Path(old['p_manifest']);require(pins,(pmp,));p=json.loads(pmp.read_text())
    oldc=Path(old['cwd']);previous=Path(p['cwd']);compact=Path(full['compact']);trials=Path(full['trials'])
    if old['counts'][:2]+[old['counts'][3]]!=full['counts']:raise ValueError('Different old/new inverse context')
    require(pins,(oldc/'compact-c.bin',oldc/'compact-defect-rows.bin',previous/'compact-p.bin'))
    compiler=Path(shutil.which('gfortran')).absolute()
    sdk=Path('/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks/Accelerate.framework/Accelerate.tbd')
    for path in (Path(__file__).resolve(),RESEARCH/'resolved_inverse_rows.f90',RESEARCH/'resolved_inverse_readback.py',
                 RESEARCH/'macos_native_guard_v2.py',compiler,compiler.resolve(),sdk,Path(sys.executable),Path(sys.executable).resolve()):
        item=identity(path)
        if item['path'] in pins and pins[item['path']]!=item:raise ValueError('Conflicting enriched inverse input')
        pins[item['path']]=item
    root.mkdir(parents=True)
    control='resolved-inverse-rows-v1\n'+'\n'.join(map(str,(compact,trials,Path(full['cwd']),previous,oldc)))+'\n'+' '.join(map(str,full['counts']))+'\n'
    (root/'enriched-inverse-control.in').write_text(control);pins[str(root/'enriched-inverse-control.in')]=identity(root/'enriched-inverse-control.in')
    m=dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],files=list(pins.values()),
           compact=str(compact),trials=str(trials),full=full['cwd'],previous=str(previous),oldc=str(oldc),counts=full['counts'],
           compiler=str(compiler),sdk=str(sdk),guard_seconds=240,launch_normal_seconds=120,group_rss_cap_bytes=3221225472,
           guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__)
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def run(root):
    root=Path(root).resolve();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if Path.cwd()!=root or m['cwd']!=str(root) or m['command']!=[sys.executable,str(Path(__file__).resolve())]:raise ValueError('Different enriched inverse owner')
    if any((root/name).exists() for name in (*OUTPUTS,'inverse-readback.json')):raise ValueError('Fresh enriched inverse outputs required')
    pins=check_pins(m);require(pins,(root/'enriched-inverse-control.in',RESEARCH/'resolved_inverse_rows.f90',RESEARCH/'resolved_inverse_readback.py',Path(m['compiler']),Path(m['sdk'])))
    expected='resolved-inverse-rows-v1\n'+'\n'.join(m[k] for k in ('compact','trials','full','previous','oldc'))+'\n'+' '.join(map(str,m['counts']))+'\n'
    if (root/'enriched-inverse-control.in').read_text()!=expected:raise ValueError('Different enriched inverse control')
    command=[m['compiler'],'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',str(RESEARCH/'resolved_inverse_rows.f90'),m['sdk'],'-o',str(root/'inverse.x')]
    (root/'inverse-build-command.json').write_text(json.dumps(command)+'\n')
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    for command in (command,[str(root/'inverse.x')]):
        done=subprocess.run(command,cwd=root,env=env,check=True,capture_output=True,text=True)
        print(done.stdout,end='');print(done.stderr,end='',file=sys.stderr)
    if done.stdout.count('ENRICHED_INVERSE_ROWS_COMPLETE; DIAGNOSTIC ONLY, no adopted inverse')!=1:raise ValueError('Incomplete enriched inverse console')
    checked=check(root,*(m[k] for k in ('compact','trials','full','previous','oldc','counts')));check_pins(m)
    if mp.read_bytes()!=before:raise ValueError('Changed enriched inverse manifest')
    out=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),**checked,
             outputs={name:identity(root/name) for name in OUTPUTS})
    (root/'inverse-readback.json').write_text(json.dumps(out,indent=2)+'\n');return out


if __name__=='__main__':run(Path.cwd())
