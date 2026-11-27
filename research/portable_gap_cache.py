"""Fresh custom-cache build and original-function qualification; not a full gap solve."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

from fetch_public_response_inputs import digest
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH=Path(__file__).resolve().parent


def stage(public_build, destination, operator_compile=False, full_link=False):
    operator_compile=operator_compile or full_link
    build,root=map(lambda p:Path(p).absolute(),(public_build,destination))
    qe=build/'qe'
    if root.exists():
        raise ValueError('Fresh custom build directory required')
    parent=build/'build-result.json'
    if json.loads(parent.read_text())['source_manifest_sha256']!=digest(RESEARCH/'public_response_sources.json'):
        raise ValueError('Different public source qualification')
    sources=[RESEARCH/'portable_gap'/n for n in ('cached_kel.f90','cached_phonon.f90','cache_qualification.f90')]
    provenance=[RESEARCH/'portable_gap/source_provenance.json']
    if operator_compile:
        provenance.append(RESEARCH/'portable_gap/operator_source_provenance.json')
    if full_link:
        provenance.append(RESEARCH/'portable_gap/io_source_provenance.json')
    recorded={}
    for proof in provenance:
        recorded.update(json.loads(proof.read_text()))
    sources+= [RESEARCH/'portable_gap'/n for n in recorded if RESEARCH/'portable_gap'/n not in sources]
    for name,item in recorded.items():
        if digest(RESEARCH/'portable_gap'/name)!=item['sha256']:
            raise ValueError('Changed migrated source: '+name)
    # All available public-tree interfaces/libraries are pinned; no historical
    # object or module directory is passed to make or the compiler.
    inputs=sources+[RESEARCH/'portable_gap/cache_qualification.mk',
        RESEARCH/'portable_gap/source_provenance.json',RESEARCH/'public_response_probe.mk',
        RESEARCH/'public_response_sources.json',RESEARCH/'portable_gap_cache.py',
        RESEARCH/'macos_native_guard.py',parent,qe/'make.inc']+provenance
    if operator_compile:
        inputs.append(RESEARCH/'portable_gap/operator_compile.mk')
    if full_link:
        inputs += [RESEARCH/'portable_gap/full_link.mk'] + [RESEARCH/n for n in
            ('nonlinear_tile_apply.f90','full_nonlinear_probe.f90','gap_seed_io.f90','nonlinear_map_probe.f90')]
    inputs+=sorted(build.rglob('*.a'))+sorted(qe.rglob('*.mod'))
    root.mkdir(parents=True)
    command=[sys.executable,str(RESEARCH/'portable_gap_cache.py'),'run',str(root)]
    manifest=dict(cwd=str(root),command=command,guard_seconds=120,public_build=str(build),
        files=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in inputs],
        scope=__doc__,historical_objects_used=False,launch_normal_seconds=120,operator_compile=operator_compile,full_link=full_link,
        acceptance='Build from migrated source, then bitwise original-function checks across context changes and cache collisions')
    (root/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def run(root):
    root=Path(root).absolute();manifest=json.loads((root/'run-manifest.json').read_text())
    verify_postrun_inputs(manifest,root)
    operator=manifest['operator_compile']
    full=manifest['full_link']
    makefile='full_link.mk' if full else ('operator_compile.mk' if operator else 'cache_qualification.mk')
    target='full-link' if full else ('operator-compile' if operator else 'cache-qualification.x')
    command=['/usr/bin/make','-f',str(RESEARCH/'portable_gap'/makefile),
        'RESEARCH='+str(RESEARCH),'QE_ROOT='+str(Path(manifest['public_build'])/'qe'),target]
    subprocess.run(command,cwd=root,check=True)
    completed=subprocess.run([str(root/'cache-qualification.x')],cwd=root,text=True,capture_output=True,check=True)
    print(completed.stdout,flush=True)
    matched=re.fullmatch(r'\s*CACHE_QUALIFICATION_PASS checks=(\d+)\s*',completed.stdout)
    if not matched or int(matched[1])!=902:
        raise ValueError('Incomplete native cache qualification')
    verify_postrun_inputs(manifest,root)
    result=dict(checks=int(matched[1]),all_checks_bitwise_equal=True,historical_objects_used=False,
        executable_sha256=digest(root/'cache-qualification.x'),public_build=manifest['public_build'],
        operator_sources_compiled=operator,operator_runtime_qualified=False,
        full_gap_driver_linked=full,full_gap_runtime_qualified=False,scope=__doc__)
    if full:
        result['full_gap_executable_sha256']=digest(root/'full-gap-check.x')
    (root/'qualification-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('stage');p.add_argument('public_build',type=Path);p.add_argument('destination',type=Path)
    p.add_argument('--operator-compile',action='store_true',help='Compile migrated operator interfaces; not runtime qualification')
    p.add_argument('--full-link',action='store_true',help='Build full strict gap-check driver; does not execute it')
    p=sub.add_parser('run');p.add_argument('root',type=Path)
    args=vars(parser.parse_args());action=args.pop('action')
    print(json.dumps((stage if action=='stage' else run)(**args),indent=2))
