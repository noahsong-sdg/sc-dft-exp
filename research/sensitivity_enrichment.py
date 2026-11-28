"""Prepare derivative-weighted trial inputs; no A actions or inverse adoption."""
import array
import json
import math
from pathlib import Path
import sys

from compact_tile_material import accepted
from defect_spectrum_readback import matrix
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity

RESEARCH=Path(__file__).resolve().parent


def dot(a,b):return math.fsum(x*y for x,y in zip(a,b))


def trial_inputs(q,d,v):
    n=len(d)
    if not q or not v or any(len(col)!=n for col in (*q,*v)) or not all(math.isfinite(x) for col in (*q,*v,d) for x in col):
        raise ValueError('Invalid enrichment geometry or values')
    extra=[];records=[]
    for direction in reversed(v):  # Largest retained singular direction first.
        target=array.array('d',(x*y for x,y in zip(d,direction)));norm=math.sqrt(dot(target,target))
        if norm==0:raise ValueError('Zero derivative-weighted sensitivity input')
        overlap=[dot(col,target)/norm for col in q]
        residual=array.array('d',target)
        for _ in range(2):
            for col in (*q,*extra):
                coefficient=dot(col,residual)
                for i,x in enumerate(col):residual[i]-=coefficient*x
        remaining=math.sqrt(dot(residual,residual))
        if remaining<=1e-8*norm:raise ValueError('Sensitivity input already in trial span')
        residual=array.array('d',(x/remaining for x in residual))
        err=max(abs(dot(col,residual)) for col in (*q,*extra))
        if err>1e-9 or abs(dot(residual,residual)-1)>1e-12:raise ValueError('Trial input orthogonalization failed')
        extra.append(residual)
        # Independently check target reconstruction by all accepted trial columns.
        basis=(*q,*extra);coefficients=[dot(col,target) for col in basis]
        error=math.sqrt(math.fsum((target[i]-math.fsum(c*col[i] for c,col in zip(coefficients,basis)))**2 for i in range(n)))/norm
        if error>1e-9:raise ValueError('Mapped sensitivity not captured by trial span')
        records.append(dict(mapped_norm=norm,old_basis_projection_squared_fraction=dot(overlap,overlap),
                            residual_fraction=remaining/norm,trial_orthogonality_error=err,reconstruction_relative_error=error))
    return extra,records


def stage(manifest,result,destination):
    m,r,pins=accepted(manifest,result,'analysis','spectrum-readback.json');root=Path(destination).resolve()
    if root.exists():raise ValueError('Fresh sensitivity preparation required')
    if r['rows']!=64 or r['kept_directions']!=3 or r['adopted_directions'] is not False:raise ValueError('Different sensitivity parent')
    for p in (Path(__file__).resolve(),RESEARCH/'macos_native_guard_v2.py',Path(sys.executable),Path(sys.executable).resolve()):
        item=identity(p);pins[item['path']]=item
    root.mkdir(parents=True)
    out=dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],files=list(pins.values()),
             compact=m['compact'],spectrum=m['cwd'],counts=m['counts'],guard_seconds=90,group_rss_cap_bytes=3221225472,
             launch_normal_seconds=120,guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__)
    (root/'run-manifest.json').write_text(json.dumps(out,indent=2)+'\n');return out


def run(root):
    root=Path(root).resolve();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if Path.cwd()!=root or m['command']!=[sys.executable,str(Path(__file__).resolve())] or m['cwd']!=str(root):raise ValueError('Different trial owner')
    if any((root/name).exists() for name in ('trial-inputs.bin','trial-readback.json')):raise ValueError('Stale trial outputs')
    check_pins(m);left,right,rank=m['counts'];n=left+right
    compact=Path(m['compact']);q=matrix(compact/'compact-q.bin',n,rank)
    with (compact/'compact-state.bin').open('rb') as stream:
        stream.seek(8*n*4);d=array.array('d');d.fromfile(stream,n)
    v=matrix(Path(m['spectrum'])/'sensitivity-directions.bin',n,3)
    extra,records=trial_inputs(q,d,v)
    with (root/'trial-inputs.bin').open('xb') as stream:
        for col in extra:col.tofile(stream)
    check_pins(m)
    if mp.read_bytes()!=before:raise ValueError('Changed trial manifest')
    out=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),records=records,
             order='largest singular value first; twice reorthogonalized D*v',extra_columns=len(extra),
             A_actions_available=False,inverse_adopted=False,physical_response_verified=False,
             outputs={'trial-inputs.bin':identity(root/'trial-inputs.bin')})
    (root/'trial-readback.json').write_text(json.dumps(out,indent=2)+'\n');return out


if __name__=='__main__':run(Path.cwd())
