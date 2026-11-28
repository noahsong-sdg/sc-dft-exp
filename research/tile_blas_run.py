"""Source-build two BLAS tile probes in one guarded fresh root; no material solve."""
import json
import os
from pathlib import Path
import subprocess
import sys

from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require
from tile_blas_analysis import analyze

RESEARCH=Path(__file__).resolve().parent
SYSTEM_VERSION=Path('/System/Library/CoreServices/SystemVersion.plist')
OTOOL=Path('/usr/bin/otool')


def stage(baseline_manifest,baseline_result,framework_stub,destination):
    mp,rp,stub,root=map(lambda p:Path(p).absolute(),(baseline_manifest,baseline_result,framework_stub,destination))
    if root.exists():raise ValueError('Fresh tile root required')
    prior=json.loads(mp.read_text());check_pins(prior);owner=Path(prior['cwd'])
    if mp.read_bytes()!=(owner/'run-manifest.json').read_bytes():raise ValueError('Different consumed baseline build')
    compiler=Path(prior['compiler']);archive=Path(prior['link_archives'][-1])
    entries={x['path']:x for x in prior['files']}
    for path in (mp,rp,owner/'run-manifest.json',owner/'results/build/receipt.json',compiler,compiler.resolve(),
                 archive,stub,stub.resolve(),SYSTEM_VERSION,OTOOL,Path(__file__).resolve(),
                 RESEARCH/'tile_blas_probe.f90',RESEARCH/'tile_blas_analysis.py',RESEARCH/'macos_native_guard_v2.py',
                 Path(sys.executable),Path(sys.executable).resolve()):
        item=identity(path)
        if str(path) in entries and entries[str(path)]!=item:raise ValueError('Conflicting tile source input')
        entries[str(path)]=item
    m=dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],files=list(entries.values()),
           baseline_manifest=str(mp),baseline_result=str(rp),compiler=str(compiler),reference_archive=str(archive),
           framework_stub=str(stub),system_version=str(SYSTEM_VERSION),guard_seconds=90,launch_normal_seconds=120,
           group_rss_cap_bytes=3221225472,guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__)
    root.mkdir(parents=True);(root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def validate(m):
    pins=check_pins(m);mp=Path(m['baseline_manifest']);rp=Path(m['baseline_result'])
    require(pins,(mp,rp,Path(__file__).resolve(),RESEARCH/'tile_blas_probe.f90',RESEARCH/'tile_blas_analysis.py',
                  Path(m['compiler']),Path(m['reference_archive']),Path(m['framework_stub']),Path(m['system_version']),OTOOL))
    parent=json.loads(mp.read_text());owner=Path(parent['cwd']);receipt_path=owner/'results/build/receipt.json'
    require(pins,(owner/'run-manifest.json',receipt_path))
    if any(pins.get(x['path'])!=x for x in parent['files']):raise ValueError('Incomplete tile baseline closure')
    result=json.loads(rp.read_text());receipt=json.loads(receipt_path.read_text())
    if (mp.read_bytes()!=(owner/'run-manifest.json').read_bytes() or result.get('status')!='PASS'
            or result.get('inputs_unchanged') is not True or result.get('historical_custom_objects_used') is not False
            or result.get('manifest_sha256')!=digest(mp) or result.get('receipt')!=receipt
            or receipt['status']!='PASS' or receipt['exit']!=0 or receipt['error'] is not None
            or receipt['command']!=parent['command'] or receipt['cwd']!=parent['cwd']
            or receipt['guard_source_sha256']!=parent['guard_source_sha256']
            or receipt['continuous_deadline_s']!=parent['guard_seconds'] or not 0<receipt['wall_s']<parent['guard_seconds']
            or m['compiler']!=parent['compiler'] or m['reference_archive']!=parent['link_archives'][-1]):
        raise ValueError('Unaccepted reference BLAS source build')
    return pins


def run(root):
    root=Path(root).absolute();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if (Path.cwd()!=root or m['cwd']!=str(root) or sys.platform!='darwin'
            or m['command']!=[sys.executable,str(Path(__file__).resolve())]):raise ValueError('Different tile owner/platform/command')
    names=['tile-readback.json','build-plan.json','library-bindings.txt']
    for prefix in ('reference','accelerate'):
        names += [f'probe-{prefix}.x',*(f'{prefix}-{suffix}' for suffix in ('summary.txt','controls.bin','samples.bin'))]
    if any((root/name).exists() for name in names):raise ValueError('Fresh tile outputs required')
    validate(m);commands=[];answers=[];bindings=[]
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
    for prefix,link in (('reference',[m['reference_archive']]),('accelerate',[m['framework_stub']])):
        command=[m['compiler'],'-O2','-ffp-contract=off','-fcheck=all','-ffree-line-length-none',
                 str(RESEARCH/'tile_blas_probe.f90'),*link,'-o',f'probe-{prefix}.x']
        commands.append(command);subprocess.run(command,cwd=root,check=True,env=env)
        bindings.append(subprocess.check_output([str(OTOOL),'-L',str(root/f'probe-{prefix}.x')],text=True))
        subprocess.run([str(root/f'probe-{prefix}.x'),prefix,'benchmark'],cwd=root,check=True,env=env)
        answers.append(analyze(root,prefix))
    (root/'build-plan.json').write_text(json.dumps(commands,indent=2)+'\n')
    (root/'library-bindings.txt').write_text('\n'.join(bindings))
    check_pins(m)
    if mp.read_bytes()!=before:raise ValueError('Changed tile manifest')
    result=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),build_commands=commands,
                libraries=answers,requested_environment={k:env[k] for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS')},
                outputs={name:identity(root/name) for name in names if name!='tile-readback.json'},
                conditioned_gap_error_bounded=False,physical_response_verified=False,scope=__doc__)
    (root/'tile-readback.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result),flush=True);return result


if __name__=='__main__':run(Path.cwd())
