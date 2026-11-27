"""Relink the pinned QE tetrahedron module with an indexed mesh lookup.

Only tetrahedron lookup and reverse coverage change. An explicitly selected
fourth-order geometry build can be composed without modifying its source.
Generated GPL source remains ignored.
Reuses source-built libraries; no cold-start or numerical qualification claim.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import time

from fetch_public_response_inputs import digest
from mesh_equivalence_patch import patch

RESEARCH=Path(__file__).resolve().parent


def fourth_geometry(directory, capacity):
    directory=Path(directory).absolute()
    metadata=directory/'build-result.json'
    result=json.loads(metadata.read_text())
    source=directory/'probe/current_geometry.f90'
    executable=directory/'probe/velocity-moment-probe.x'
    if (result.get('velocity_stencil_order')!=4
            or result.get('curvature_stencil_unchanged') is not True
            or result.get('point_capacity')!=capacity
            or result.get('executable')!=str(executable)
            or digest(executable)!=result.get('executable_sha256')
            or digest(source)!=result.get('generated_geometry_sha256')):
        raise ValueError('Missing or changed explicit fourth-order geometry build')
    return source,metadata,executable


def build(parent,destination,fourth_geometry_build=None):
    parent,root=[Path(p).absolute() for p in (parent,destination)]
    original=json.loads((parent/'build-result.json').read_text())
    if (original.get('point_capacity',40000)<48**3
            or Path(original['executable'])!=parent/'probe/velocity-moment-probe.x'
            or digest(Path(original['executable']))!=original['executable_sha256']):
        raise ValueError('Missing or changed capacity-qualified parent')
    geometry=parent/'probe/current_geometry.f90'
    geometry_inputs=[]
    if fourth_geometry_build is not None:
        geometry,*geometry_inputs=fourth_geometry(fourth_geometry_build,original['point_capacity'])
    qe=parent/'qe';source=qe/'PW/src/tetra.f90'
    candidate=patch(source.read_text())
    paths=[source,geometry,*geometry_inputs,parent/'build-result.json',qe/'make.inc',
        Path(__file__),RESEARCH/'mesh_equivalence.f90',RESEARCH/'mesh_equivalence_patch.py',
        RESEARCH/'indexed_mesh_probe.mk',RESEARCH/'public_response_probe.mk',
        RESEARCH/'velocity_moment_probe.f90',RESEARCH/'response_assignment_dump.f90']
    paths+=sorted(parent.rglob('*.a'))+sorted(parent.rglob('*.mod'))
    if not any(p.suffix=='.a' for p in paths) or not any(p.suffix=='.mod' for p in paths):
        raise ValueError('Missing compiled link inputs')
    identities=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in paths]
    root.mkdir(parents=True);probe=root/'probe';probe.mkdir()
    (probe/'indexed_tetra.f90').write_text(candidate)
    shutil.copy2(geometry,probe/'current_geometry.f90')
    command=['make','-f',str(RESEARCH/'indexed_mesh_probe.mk'),'QE_ROOT='+str(qe),'velocity-moment-probe.x']
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
        link_inputs_unchanged=True,indexed_tetra_sha256=digest(probe/'indexed_tetra.f90'),
        generated_geometry_sha256=digest(probe/'current_geometry.f90'),
        build_log_sha256=digest(root/'build.log'),indexed_mesh_lookup=True,
        velocity_stencil_order=4 if fourth_geometry_build is not None else 2,
        curvature_stencil_unchanged=True,numerical_response_qualified=False,scope=__doc__.strip())
    (root/'build-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parent',type=Path);parser.add_argument('destination',type=Path)
    parser.add_argument('--fourth-geometry-build',type=Path,help='Explicit hash-checked fourth-order geometry; requires new native response qualification')
    print(json.dumps(build(**vars(parser.parse_args())),indent=2))
