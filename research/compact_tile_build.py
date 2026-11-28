"""Source-build the compact native tile variant; no material kernels executed."""
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require
from portable_full_step_build import stage as parent_stage

RESEARCH=Path(__file__).resolve().parent
SDK=Path('/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/System/Library/Frameworks/Accelerate.framework/Accelerate.tbd')
SOURCES=('compact_defect_io.f90','streamed_defect_core.f90','compact_native_tile_probe.f90')


def stage(parent,destination,sdk=SDK):
    sdk=Path(sdk).absolute();identity(sdk)
    m=parent_stage(parent,destination);root=Path(m['cwd']);entries={x['path']:x for x in m['files']}
    for path in (Path(__file__).resolve(),*(RESEARCH/x for x in SOURCES),RESEARCH/'portable_gap/compact_tile_link.mk',
                 sdk,Path(sys.executable),Path(sys.executable).resolve()):
        item=identity(path)
        if item['path'] in entries and entries[item['path']]!=item:raise ValueError('Conflicting compact build source')
        entries[item['path']]=item
    m.update(command=[sys.executable,str(Path(__file__).resolve())],files=list(entries.values()),
             guard_seconds=60,defect_blas=str(sdk),scope=__doc__,
             acceptance='Fresh source link, exact dry-run plan/console and902cache controls; no material or norm acceptance')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def plan_check(plan,pins,sdk):
    compiles=[];links=[]
    for line in plan.splitlines():
        tokens=shlex.split(line)
        if '-c' in tokens:
            source=Path(tokens[tokens.index('-c')+1]);require(pins,(source,));compiles.append(str(source))
            target=tokens[tokens.index('-o')+1]
            if Path(target).name!=target or not target.endswith('.o'):raise ValueError('Nonlocal compact build object')
        elif '-o' in tokens:
            target=tokens[tokens.index('-o')+1];links.append(tokens)
            if target not in ('full-gap-check.x','cache-qualification.x'):raise ValueError('Unexpected compact build executable')
            for item in tokens:
                if item.endswith('.a'):require(pins,(Path(item),))
        else:raise ValueError('Unexpected compact build plan command')
    if len(links)!=2 or len(compiles)!=len(set(compiles)) or not {str(RESEARCH/x) for x in SOURCES}<=set(compiles):
        raise ValueError('Incomplete or duplicate compact source build plan')
    native=[x for x in links if x[x.index('-o')+1]=='full-gap-check.x']
    if len(native)!=1 or native[0].count(sdk)!=1:raise ValueError('Missing explicit compact BLAS link')
    first_archive=next(i for i,x in enumerate(native[0]) if x.endswith('.a'))
    if native[0].index(sdk)>first_archive:raise ValueError('Compact BLAS follows static reference archive')
    return len(compiles)


def run(root):
    root=Path(root).absolute();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if Path.cwd()!=root or m['cwd']!=str(root) or m['command']!=[sys.executable,str(Path(__file__).resolve())]:
        raise ValueError('Different compact build owner or command')
    if any(root.glob('*.o')) or any(root.glob('*.mod')) or any(root.glob('*.x')) or any((root/x).exists() for x in ('build-plan.txt','compact-build-result.json')):
        raise ValueError('Fresh compact build outputs required')
    pins=check_pins(m);sdk=m['defect_blas']
    require(pins,(Path(__file__).resolve(),*(RESEARCH/x for x in SOURCES),RESEARCH/'portable_gap/compact_tile_link.mk',Path(sdk)))
    command=['/usr/bin/make','-f',str(RESEARCH/'portable_gap/compact_tile_link.mk'),
             'RESEARCH='+str(RESEARCH),'QE_ROOT='+str(Path(m['public_build'])/'qe'),'DEFECT_BLAS='+sdk,'full-link']
    plan=subprocess.check_output([command[0],'-n',*command[1:]],cwd=root,text=True)
    count=plan_check(plan,pins,sdk);(root/'build-plan.txt').write_text(plan)
    built=subprocess.run(command,cwd=root,text=True,capture_output=True,check=True)
    print(built.stdout,end='',flush=True);print(built.stderr,end='',file=sys.stderr,flush=True)
    if built.stdout!=plan:raise ValueError('Compact build console differs from source plan')
    identity(root/'full-gap-check.x');identity(root/'cache-qualification.x')
    cache=subprocess.check_output([str(root/'cache-qualification.x')],cwd=root,text=True)
    if not re.fullmatch(r'\s*CACHE_QUALIFICATION_PASS checks=902\s*',cache):raise ValueError('Incomplete compact cache controls')
    check_pins(m)
    if before!=mp.read_bytes():raise ValueError('Changed compact build manifest')
    result=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),
                fresh_compile_count=count,build_plan_matches_console=True,cache_checks=902,cache_all_bitwise_equal=True,
                explicit_blas=identity(sdk),historical_custom_objects_used=False,material_runtime_qualified=False,
                outputs={p.name:identity(p) for p in sorted(root.iterdir()) if p.suffix in ('.o','.mod','.x') or p.name=='build-plan.txt'})
    (root/'compact-build-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True);return result


if __name__=='__main__':run(Path.cwd())
