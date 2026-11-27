"""Relink a support-only DOS candidate against an unchanged fresh public build.

Reuses compiled libraries; not a cold-start build or a qualified improvement.
Generated modified upstream GPL source stays under the ignored build root.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from dos_support_optimization import patch
from fetch_public_response_inputs import digest

RESEARCH=Path(__file__).resolve().parent


def build(parent,destination):
    parent,root=[Path(p).absolute() for p in (parent,destination)]
    original=json.loads((parent/'build-result.json').read_text())
    if (original.get('point_capacity',40000)<48**3
            or Path(original['executable'])!=parent/'probe/velocity-moment-probe.x'
            or digest(Path(original['executable']))!=original['executable_sha256']):
        raise ValueError('Missing or changed capacity-qualified parent')
    qe=parent/'qe';source=qe/'SCTK/src/sctk_tetra.f90'
    candidate=patch(source.read_text())
    paths=[source,parent/'probe/current_geometry.f90',parent/'build-result.json',qe/'make.inc',
        Path(__file__),RESEARCH/'dos_support_optimization.py',RESEARCH/'dos_support_probe.mk',
        RESEARCH/'public_response_probe.mk',RESEARCH/'velocity_moment_probe.f90',
        RESEARCH/'response_assignment_dump.f90']
    paths+=sorted(parent.rglob('*.a'))+sorted(parent.rglob('*.mod'))
    if not any(p.suffix=='.a' for p in paths) or not any(p.suffix=='.mod' for p in paths):
        raise ValueError('Missing compiled link inputs')
    identities=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in paths]
    root.mkdir(parents=True);probe=root/'probe';probe.mkdir()
    (probe/'optimized_tetra.f90').write_text(candidate)
    shutil.copy2(parent/'probe/current_geometry.f90',probe/'current_geometry.f90')
    command=['make','-f',str(RESEARCH/'dos_support_probe.mk'),'QE_ROOT='+str(qe),'velocity-moment-probe.x']
    started=time.monotonic()
    with (root/'build.log').open('x') as log:
        subprocess.run(command,cwd=probe,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    for item in identities:
        path=Path(item['path'])
        if path.stat().st_size!=item['bytes'] or digest(path)!=item['sha256']:
            raise ValueError('Changed link input: '+str(path))
    exe=probe/'velocity-moment-probe.x'
    result=dict(executable=str(exe),executable_sha256=digest(exe),point_capacity=original['point_capacity'],
        wall_s=time.monotonic()-started,command=command,cwd=str(probe),link_inputs=identities,
        link_inputs_unchanged=True,optimized_tetra_sha256=digest(probe/'optimized_tetra.f90'),
        generated_geometry_sha256=digest(probe/'current_geometry.f90'),
        build_log_sha256=digest(root/'build.log'),dos_support_only=True,
        numerical_response_qualified=False,scope=__doc__.strip())
    (root/'build-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parent',type=Path);parser.add_argument('destination',type=Path)
    print(json.dumps(build(**vars(parser.parse_args())),indent=2))
