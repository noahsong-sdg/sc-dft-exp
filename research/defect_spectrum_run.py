"""Guarded fresh build and retained-row diagnosis; no kernel construction or inverse adoption."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from compact_defect_material import analyze as parent_analyze
from defect_spectrum_readback import check
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require

RESEARCH=Path(__file__).resolve().parent
OUTPUTS=('spectrum.x','spectrum-build-command.json','row-errors.bin','row-gram.bin','row-eigenvectors.bin',
         'sensitivity-directions.bin','basis-overlap.bin','basis-gram.bin','direction-gram.bin','row-spectrum.txt','row-baselines.bin')


def stage(parent_manifest,parent_result,destination):
    mp,rp=map(lambda x:Path(x).absolute(),(parent_manifest,parent_result));root=Path(destination).absolute()
    if root.exists():raise ValueError('Fresh row spectrum root required')
    parent=json.loads(mp.read_text());recorded=json.loads(rp.read_text());replayed=parent_analyze(mp)
    if any(recorded.get(k)!=v for k,v in replayed.items()):raise ValueError('Different accepted defect parent')
    pins=check_pins(parent);defect=Path(parent['cwd']);compact=Path((defect/'compact-defect-control.in').read_text().splitlines()[1])
    p=json.loads(Path(parent['p_manifest']).read_text());qual=json.loads(Path(p['predecessor_manifest']).read_text())
    selected=json.loads(Path(qual['selected_manifest']).read_text());tiles=Path(selected['cwd'])
    bm=json.loads(Path(parent['build_manifest']).read_text());sdk=Path(bm['defect_blas']);compiler=Path(shutil.which('gfortran')).absolute()
    require(pins,(compact/name for name in ('compact-q.bin','compact-u.bin','compact-state.bin','compact-state.meta')))
    require(pins,(tiles/f'compact-kernel-{i}.bin' for i in (1,2)))
    for name,item in recorded['outputs'].items():
        if identity(defect/name)!=item:raise ValueError('Changed retained defect output')
        pins[item['path']]=item
    for path in (mp,rp,defect/'run-manifest.json',defect/'results/material/receipt.json',defect/'campaign_launch_watch.json',
                 Path(__file__).resolve(),RESEARCH/'defect_row_spectrum.f90',RESEARCH/'defect_spectrum_readback.py',
                 RESEARCH/'macos_native_guard_v2.py',sdk,compiler,compiler.resolve(),Path(sys.executable),Path(sys.executable).resolve()):
        item=identity(path)
        if item['path'] in pins and pins[item['path']]!=item:raise ValueError('Conflicting row spectrum input')
        pins[item['path']]=item
    left,right,_,rank=parent['counts'];counts=[left,right,rank]
    root.mkdir(parents=True);control=root/'spectrum-control.in'
    control.write_text('retained-defect-row-spectrum-v1\n'+str(compact)+'\n'+str(defect)+'\n'+str(tiles)+'\n'+f'{left} {right} {rank} 64\n')
    pins[str(control)]=identity(control)
    m=dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],files=list(pins.values()),
           parent_manifest=str(mp),parent_result=str(rp),compact=str(compact),defect=str(defect),tiles=str(tiles),counts=counts,
           compiler=str(compiler),sdk=str(sdk),guard_seconds=90,launch_normal_seconds=120,group_rss_cap_bytes=3221225472,
           guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__,
           acceptance='Independent row/Gram/eigenpair/action/overlap checks; retained64row sample only, no new basis or full norm')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def run(root):
    root=Path(root).absolute();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if Path.cwd()!=root or m['cwd']!=str(root) or m['command']!=[sys.executable,str(Path(__file__).resolve())]:raise ValueError('Different spectrum owner')
    if any((root/name).exists() for name in (*OUTPUTS,'spectrum-readback.json')):raise ValueError('Fresh spectrum outputs required')
    pins=check_pins(m);require(pins,(Path(__file__).resolve(),RESEARCH/'defect_row_spectrum.f90',RESEARCH/'defect_spectrum_readback.py',Path(m['compiler']),Path(m['sdk'])))
    expected='retained-defect-row-spectrum-v1\n'+m['compact']+'\n'+m['defect']+'\n'+m['tiles']+'\n'+' '.join(map(str,(*m['counts'],64)))+'\n'
    if (root/'spectrum-control.in').read_text()!=expected:raise ValueError('Different retained spectrum control')
    command=[m['compiler'],'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',str(RESEARCH/'defect_row_spectrum.f90'),m['sdk'],'-o',str(root/'spectrum.x')]
    (root/'spectrum-build-command.json').write_text(json.dumps(command)+'\n')
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    built=subprocess.run(command,cwd=root,env=env,check=True,capture_output=True,text=True)
    print(built.stdout,end='');print(built.stderr,end='',file=sys.stderr)
    done=subprocess.run([str(root/'spectrum.x')],cwd=root,env=env,check=True,capture_output=True,text=True)
    print(done.stdout,end='');print(done.stderr,end='',file=sys.stderr)
    if done.stdout.count('RETAINED_ROW_SPECTRUM_COMPLETE; no new kernels or adopted directions')!=1:raise ValueError('Incomplete spectrum console')
    checked=check(root,m['compact'],m['defect'],m['tiles'],m['counts']);check_pins(m)
    if mp.read_bytes()!=before:raise ValueError('Changed spectrum manifest')
    result=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),**checked,
                blas_thread_environment={k:env[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},
                outputs={name:identity(root/name) for name in OUTPUTS})
    (root/'spectrum-readback.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':run(Path.cwd())
