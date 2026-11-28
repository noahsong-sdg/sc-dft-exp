"""Training-only completion of original resolved sensitivity span; no new kernels."""
import array
import json
import math
from pathlib import Path
import sys

from compact_tile_material import accepted
from compact_tile_readback import finite_file
from defect_spectrum_readback import matrix
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity
from sensitivity_enrichment import trial_inputs,dot
from stream_inverse_action import column

RESEARCH=Path(__file__).resolve().parent


def omitted_directions(spectrum,n):
    spectrum=Path(spectrum);lines=(spectrum/'row-spectrum.txt').read_text().splitlines()
    if len(lines)!=66 or lines[0]!='retained-row-spectrum-v1; diagnostic, NOT an inverse or certificate':raise ValueError('Stale resolved spectrum')
    dims=list(map(int,lines[1].split()));eig=list(map(float,lines[2:]))
    if len(dims)!=5 or sum(dims[:2])!=n or dims[3:]!=[64,3] or not all(map(math.isfinite,eig)) or eig!=sorted(eig) or eig[-1]<=0:raise ValueError('Different resolved spectrum')
    selected=[i for i,x in enumerate(eig) if x>1e-10*eig[-1]][:-3]
    if not selected or len(selected)+3+dims[2]>64:raise ValueError('Resolved completion unavailable within rank64')
    lv=matrix(spectrum/'row-eigenvectors.bin',64,64);finite_file(spectrum/'row-errors.bin',64*n)
    vectors=[array.array('d') for _ in selected]
    with (spectrum/'row-errors.bin').open('rb') as stream:
        for _ in range(n):
            row=column(stream,64)
            for v,index in zip(vectors,selected):v.append(dot(row,lv[index])/math.sqrt(eig[index]))
    gram_error=max(abs(dot(a,b)-float(i==j)) for i,a in enumerate(vectors) for j,b in enumerate(vectors))
    # The fixed eigenvalue threshold allows Gram roundoff amplification at tiny modes.
    if not math.isfinite(gram_error) or gram_error>1e-4:raise ValueError('Unresolved reconstructed sensitivity directions')
    parts=[[[] for _ in range(64)] for _ in vectors]
    with (spectrum/'row-errors.bin').open('rb') as stream:
        for first in range(0,n,1024):
            width=min(1024,n-first);data=column(stream,64*width)
            for k,v in enumerate(vectors):
                for i in range(64):parts[k][i].append(math.fsum(a*b for a,b in zip(data[i::64],v[first:first+width])))
    action_error=0.
    for k,index in enumerate(selected):
        sigma=math.sqrt(eig[index]);bound=256*sys.float_info.epsilon*eig[-1]/sigma
        for i in range(64):
            error=abs(math.fsum(parts[k][i])-sigma*lv[index][i]);action_error=max(action_error,error)
            if not math.isfinite(error) or error>bound:raise ValueError('Reconstructed sensitivity action mismatch')
    return vectors,dict(omitted_eigenvalues=[eig[i] for i in selected],relative_eigenvalue_threshold=1e-10,
                        reconstructed_gram_error=gram_error,reconstructed_action_max_error=action_error)


def stage(spectrum_manifest,spectrum_result,preparation_manifest,preparation_result,destination):
    sm,sr,pins=accepted(spectrum_manifest,spectrum_result,'analysis','spectrum-readback.json')
    pm,pr,pp=accepted(preparation_manifest,preparation_result,'prepare','trial-readback.json');root=Path(destination).resolve()
    if root.exists():raise ValueError('Fresh resolved preparation required')
    if pm['spectrum']!=sm['cwd'] or pm['counts']!=sm['counts'] or pr['extra_columns']!=3:raise ValueError('Different original training parents')
    for path,item in pp.items():
        if path in pins and pins[path]!=item:raise ValueError('Conflicting resolved preparation parents')
        pins[path]=item
    for path in (Path(__file__).resolve(),RESEARCH/'sensitivity_enrichment.py',RESEARCH/'macos_native_guard_v2.py',Path(sys.executable),Path(sys.executable).resolve()):
        item=identity(path);pins[item['path']]=item
    root.mkdir(parents=True)
    m=dict(cwd=str(root),command=[sys.executable,str(Path(__file__).resolve())],files=list(pins.values()),
           compact=pm['compact'],spectrum=sm['cwd'],previous=pm['cwd'],counts=pm['counts'],guard_seconds=120,
           launch_normal_seconds=120,group_rss_cap_bytes=3221225472,guard_source_sha256=digest(RESEARCH/'macos_native_guard_v2.py'),scope=__doc__)
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');return m


def run(root):
    root=Path(root).resolve();mp=root/'run-manifest.json';before=mp.read_bytes();m=json.loads(before)
    if Path.cwd()!=root or m['cwd']!=str(root) or m['command']!=[sys.executable,str(Path(__file__).resolve())]:raise ValueError('Different resolved preparation owner')
    if any((root/name).exists() for name in ('trial-inputs.bin','resolved-readback.json')):raise ValueError('Stale resolved outputs')
    check_pins(m);left,right,rank=m['counts'];n=left+right
    vectors,checked=omitted_directions(m['spectrum'],n)
    q=matrix(Path(m['compact'])/'compact-q.bin',n,rank);old=matrix(Path(m['previous'])/'trial-inputs.bin',n,3)
    with (Path(m['compact'])/'compact-state.bin').open('rb') as stream:stream.seek(32*n);d=column(stream,n)
    extra,records=trial_inputs(q+old,d,vectors)
    target=root/'trial-inputs.bin'
    with target.open('xb') as stream:
        for col in old+extra:col.tofile(stream)
    with target.open('rb') as stream, (Path(m['previous'])/'trial-inputs.bin').open('rb') as prior:
        for _ in range(3):
            if stream.read(8*n)!=prior.read(8*n):raise ValueError('Original trial prefix changed')
    check_pins(m)
    if mp.read_bytes()!=before:raise ValueError('Changed resolved preparation manifest')
    out=dict(terminal_guard_pass=False,inputs_unchanged=True,manifest_sha256=digest(mp),**checked,records=records,
             original_trial_prefix_bitwise_equal=True,new_columns=len(extra),total_trial_columns=3+len(extra),
             training_only=True,A_actions_available=False,inverse_adopted=False,physical_response_verified=False,
             outputs={'trial-inputs.bin':identity(target)})
    (root/'resolved-readback.json').write_text(json.dumps(out,indent=2)+'\n');return out


if __name__=='__main__':run(Path.cwd())
