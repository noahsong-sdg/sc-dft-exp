"""Build a fourth-order-velocity probe against a qualified fresh QE tree.

This relinks reused source-built libraries; it is not another cold-start build.
Curvature and every other response expression remain unchanged.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time
from urllib.request import urlopen

from build_public_response import digest
from current_moment_geometry import URL, extract

RESEARCH=Path(__file__).resolve().parent


def build(parent, destination):
    parent,root=[Path(p).absolute() for p in (parent,destination)]
    original=json.loads((parent/'build-result.json').read_text())
    if (original.get('point_capacity',40000)<48**3
            or Path(original['executable'])!=parent/'probe/velocity-moment-probe.x'
            or digest(Path(original['executable']))!=original['executable_sha256']):
        raise ValueError('Missing or changed capacity-qualified parent build')
    make=shutil.which('make')
    if make is None:
        raise RuntimeError('make is unavailable')
    qe=parent/'qe'
    paths=[parent/'build-result.json',qe/'make.inc',RESEARCH/'public_response_probe.mk',
           RESEARCH/'velocity_moment_probe.f90',RESEARCH/'response_assignment_dump.f90',
           RESEARCH/'current_moment_geometry.py',Path(__file__)]
    paths+=sorted(parent.rglob('*.a'))+sorted(parent.rglob('*.mod'))
    if not any(p.suffix=='.a' for p in paths) or not any(p.suffix=='.mod' for p in paths):
        raise ValueError('Parent compiled libraries/modules are unavailable')
    identities=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in paths]
    root.mkdir(parents=True)
    probe=root/'probe';probe.mkdir()
    started=time.monotonic()
    with urlopen(URL,timeout=45) as response:
        source=response.read(300001)
    generated=probe/'current_geometry.f90'
    generated.write_text(extract(source,unshifted=True,fourth_order=True))
    command=[make,'-f',str(RESEARCH/'public_response_probe.mk'),'QE_ROOT='+str(qe),'velocity-moment-probe.x']
    with (root/'build.log').open('x') as log:
        subprocess.run(command,cwd=probe,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
    for item in identities:
        p=Path(item['path'])
        if p.stat().st_size!=item['bytes'] or digest(p)!=item['sha256']:
            raise ValueError('Link input changed during probe build: '+str(p))
    exe=probe/'velocity-moment-probe.x'
    result=dict(executable=str(exe),executable_sha256=digest(exe),point_capacity=original['point_capacity'],
                wall_s=time.monotonic()-started,command=command,cwd=str(probe),
                generated_geometry_sha256=digest(generated),build_log_sha256=digest(root/'build.log'),
                link_inputs=identities,link_inputs_unchanged=True,velocity_stencil_order=4,
                curvature_stencil_unchanged=True,numerical_response_qualified=False,
                scope=__doc__.strip())
    (root/'build-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parent',type=Path);parser.add_argument('destination',type=Path)
    print(json.dumps(build(**vars(parser.parse_args())),indent=2))
