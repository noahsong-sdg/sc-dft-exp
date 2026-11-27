"""Stage a source-built full gap check on the unchanged retained8.05K problem.

This qualifies a native dependency replacement, not portable microscopic setup
or physical response. All retained data remain explicit, read-only dependencies.
"""
import argparse
import json
from pathlib import Path
import shutil

from fetch_public_response_inputs import digest,validate
from public_band_pilot_analysis import verify_postrun_inputs
from verify_gap_candidate import verify

RESEARCH=Path(__file__).resolve().parent


def stage(build, inputs, reference_manifest, destination):
    build,inputs,reference_manifest,root=map(lambda p:Path(p).absolute(),(build,inputs,reference_manifest,destination))
    if root.exists():
        raise ValueError('Fresh replacement qualification directory required')
    built=json.loads((build/'qualification-result.json').read_text())
    protocol=json.loads((build/'run-manifest.json').read_text())
    receipt=json.loads((build/'results/build/receipt.json').read_text())
    if (built.get('full_gap_driver_linked') is not True or built.get('checks')!=902
            or receipt.get('status')!='PASS' or receipt.get('exit')!=0 or receipt.get('error') is not None
            or receipt['command']!=protocol['command'] or receipt['cwd']!=str(build)):
        raise ValueError('Source-only full driver build is not accepted')
    verify_postrun_inputs(protocol,build)
    exe=build/'full-gap-check.x'
    if digest(exe)!=built['full_gap_executable_sha256']:
        raise ValueError('Changed source-built executable')
    old=json.loads(reference_manifest.read_text());parent=Path(old['cwd'])
    verify_postrun_inputs(old,parent)
    qualified=verify(parent,reference_manifest)
    if not qualified['stationary_residual_targets_met']:
        raise ValueError('Unaccepted retained candidate')
    point=Path((parent/'map-control.in').read_text().strip())
    seed_control=(parent/'seed-control.in').read_text().splitlines()
    catalogs=[RESEARCH/'public_response_inputs.json',RESEARCH/'public_gap_coulomb_inputs.json']
    files={}
    for catalog in catalogs:
        for name,item in json.loads(catalog.read_text())['files'].items():
            if name in files:
                raise ValueError('Duplicate microscopic input')
            source=inputs/validate(name,item)
            if source.stat().st_size!=item['bytes'] or digest(source)!=item['sha256']:
                raise ValueError('Changed microscopic input: '+name)
            files[name]=item
    if len(files)!=57 or sum(n.startswith('pwscf.vel') for n in files)!=26:
        raise ValueError('Incomplete declared Nb interaction/input bundle')
    native=(parent/'native.in').read_text();marker="outdir='"+str(inputs)+"/'"
    if native.count(marker)!=1 or len(seed_control)!=2:
        raise ValueError('Different retained input/seed protocol')
    external=[reference_manifest,*catalogs,build/'run-manifest.json',build/'qualification-result.json',
        build/'results/build/receipt.json',exe,Path(__file__),RESEARCH/'macos_native_guard.py',
        RESEARCH/'verify_gap_candidate.py',RESEARCH/'full_nonlinear_analysis.py']
    external += [point/n for n in ('native-init.meta','native-init.bin','full-z.meta','full-z.bin')]
    entries=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in external]
    copied={name:dict(bytes=(parent/name).stat().st_size,sha256=digest(parent/name))
        for name in ('gap-seed.meta','map-control.in')}
    root.mkdir(parents=True)
    for name,item in files.items():
        source=inputs/name;target=root/'inputs'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        entries += [dict(path=str(p),bytes=item['bytes'],sha256=item['sha256']) for p in (source,target)]
    target=root/'verify-gap-seed.x';shutil.copy2(exe,target)
    for name in ('gap-seed.meta','gap-seed.bin','map-control.in'):
        shutil.copy2(parent/name,root/name)
    (root/'seed-control.in').write_text(str(root)+'\n'+seed_control[1]+'\n')
    (root/'native.in').write_text(native.replace(marker,"outdir='"+str(root/'inputs').replace("'","''")+"/'"))
    entries.append(dict(path=str(target),bytes=target.stat().st_size,sha256=built['full_gap_executable_sha256']))
    for name,item in copied.items():entries.append(dict(path=str(root/name),**item))
    for p in (root/'seed-control.in',root/'native.in'):
        entries.append(dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)))
    # Preserve the original candidate identity; never adopt copy-time changes.
    entries.append(dict(path=str(root/'gap-seed.bin'),bytes=(parent/'gap-seed.bin').stat().st_size,sha256=old['candidate_sha256']))
    result=dict(cwd=str(root),command=[str(target),'-in',str(root/'native.in')],files=entries,
        candidate_sha256=old['candidate_sha256'],guard_seconds=900,launch_normal_seconds=120,
        rss_cap_bytes=3221225472,retained_inputs_used=True,historical_objects_used=False,
        original_full_map_sha256=digest(parent/'full-map.bin'),
        scope=__doc__,acceptance='Strict bitwise initialization/seed/Z context, unchanged stationary targets, full-map comparison to original; not conditioned error or physical prediction',
        forecast='About680s/1GB from prior native action; bound900s/3GiB; original new-campaign4h pilot')
    (root/'run-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('build','inputs','reference_manifest','destination'):p.add_argument(name,type=Path)
    print(json.dumps(stage(**vars(p.parse_args())),indent=2))
