"""Independent selected material contractions; no complete P or norm certificate."""
import array
from collections import Counter
import json
import math
from pathlib import Path

from compact_tile_material import accepted
from fetch_public_response_inputs import digest
from inverse_material_run import check_pins,identity,require
from stream_inverse_action import column


def finite_file(path,count,zero_from=None,zero_to=None):
    if path.stat().st_size!=8*count:raise ValueError('Stale selected tile binary shape')
    with path.open('rb') as stream:
        for at in range(0,count,65536):
            values=column(stream,min(65536,count-at))
            if not all(map(math.isfinite,values)):raise ValueError('Nonfinite selected tile output')
            if zero_from is not None:
                lo=max(at,zero_from);hi=min(at+len(values),zero_to)
                if lo<hi and any(values[lo-at:hi-at]):raise ValueError('Unvisited partial P column changed')


def controls(root,compact_root,left,right,rank,beta):
    root,compact_root=Path(root),Path(compact_root);n=left+right
    if left<64 or right<1 or not 1<=rank<=64 or not math.isfinite(beta) or beta<=0:raise ValueError('Invalid selected tile context')
    for name,count in (('compact-state.bin',5*n),('compact-q.bin',n*rank)):
        if (compact_root/name).stat().st_size!=8*count:raise ValueError('Stale selected compact state')
    with (compact_root/'compact-state.bin').open('rb') as f:state=[column(f,n) for _ in range(5)]
    if not all(math.isfinite(x) for values in state for x in values) or any(1+x<=0 for x in state[3]):raise ValueError('Invalid selected compact fields')
    weights=array.array('d',(dk/2*(beta/2 if x==0 else math.tanh(beta*abs(x)/2)/abs(x)) for x,dk in zip(state[1],state[2])))
    rs=sorted({0,(rank-1)//2,rank-1});js=sorted({0,(right-1)//2,right-1})
    k2={};k1={j:[] for j in js}
    for tile in (1,2):
        path=root/f'compact-kernel-{tile}.bin';finite_file(path,64*right)
        with path.open('rb') as f:
            for j in js:
                for k in range(32):
                    f.seek(8*(k*right+j));k1[j].append(column(f,1)[0])
            for k in (0,31):
                f.seek(8*((32+k)*right));k2[32*(tile-1)+k]=column(f,right)
    ppath=root/'compact-partial-p.bin';finite_file(ppath,n*rank,64*rank,left*rank)
    errors=[];bounds=[]
    with (compact_root/'compact-q.bin').open('rb') as qfile,ppath.open('rb') as pfile:
        for r in rs:
            qfile.seek(8*r*n);q=column(qfile,n);qd=[a*b for a,b in zip(q,state[4])]
            for j,kernel in k2.items():
                terms=[qd[left+i]*(-value*weights[j]/(1+state[3][left+i])) for i,value in enumerate(kernel)]
                pfile.seek(8*(j*rank+r));actual=column(pfile,1)[0]
                error=abs(actual-math.fsum(terms));bound=1e-28+1e-10*math.fsum(map(abs,terms))
                if not math.isfinite(bound) or error>bound:raise ValueError('Independent selected left P mismatch')
                errors.append(error);bounds.append(bound)
            for j,kernel in k1.items():
                terms=[qd[i]*(-value*weights[left+j]/(1+state[3][i])) for i,value in enumerate(kernel)]
                pfile.seek(8*((left+j)*rank+r));actual=column(pfile,1)[0]
                error=abs(actual-math.fsum(terms));bound=1e-28+1e-10*math.fsum(map(abs,terms))
                if not math.isfinite(bound) or error>bound:raise ValueError('Independent selected right P mismatch')
                errors.append(error);bounds.append(bound)
    return dict(independent_controls=len(errors),max_absolute_error=max(errors),max_error_over_bound=max(e/b for e,b in zip(errors,bounds)),
                selected_rank_indices=[r+1 for r in rs],selected_right_indices=[j+1 for j in js],all_partial_P_and_kernel_values_finite=True,
                unvisited_left_columns_zero=True)


def analyze(manifest):
    mp=Path(manifest).absolute();m=json.loads(mp.read_text());root=Path(m['cwd']);pins=check_pins(m)
    if mp.read_bytes()!=(root/'run-manifest.json').read_bytes():raise ValueError('Different selected tile consumed manifest')
    prep,pr,pp=accepted(m['preparation_manifest'],m['preparation_result'],'prepare','compact-preparation-result.json')
    _,_,bp=accepted(m['build_manifest'],m['build_result'],'build','compact-build-result.json')
    if any(pins.get(path)!=item for parent in (pp,bp) for path,item in parent.items()):raise ValueError('Incomplete selected parent closure')
    require(pins,(Path(__file__).resolve(),Path(prep['cwd'])/'compact-q.bin',Path(prep['cwd'])/'compact-state.bin'))
    receipt=json.loads((root/'results/material/receipt.json').read_text())
    if (receipt['status']!='PASS' or receipt['exit']!=0 or receipt['error'] is not None
            or receipt['command']!=m['command'] or receipt['cwd']!=m['cwd']
            or receipt['guard_source_sha256']!=m['guard_source_sha256'] or receipt['continuous_deadline_s']!=m['guard_seconds']
            or not 0<receipt['wall_s']<m['guard_seconds']
            or any(not 0<=receipt[k]<=m['group_rss_cap_bytes'] for k in ('max_individual_descendant_rss_bytes','sampled_peak_group_rss_bytes'))
            or json.loads((root/'campaign_launch_watch.json').read_text())['phase']!='completed'):
        raise ValueError('Unaccepted selected material receipt')
    console=(root/'results/material/console.log').read_text()
    if console.count('COMPACT_NATIVE_TILES_PASS rows=64; DIAGNOSTIC ONLY, incomplete P')!=1:raise ValueError('Incomplete selected native result')
    lines=(root/'compact-tile-checks.txt').read_text().splitlines()
    if lines[0]!='selected-compact-native-tiles-v1; partial P only; NOT a norm':raise ValueError('Stale selected native controls')
    derivative_error=float(lines[1]);cpu={'kernel_cpu_s':[],'contraction_cpu_s':[]};native=[]
    if not math.isfinite(derivative_error) or derivative_error<0:raise ValueError('Invalid native D control')
    for line in lines[2:]:
        fields=line.split()
        if len(fields)==3 and fields[1] in cpu:
            value=float(fields[2])
            if int(fields[0])!=len(cpu[fields[1]])+1 or not math.isfinite(value) or value<0:raise ValueError('Invalid selected timing')
            cpu[fields[1]].append(value)
        elif len(fields)==6 and fields[0] in ('left','right'):
            values=list(map(float,fields[3:]))
            if not all(map(math.isfinite,values)) or values[2]<0 or abs(values[0]-values[1])>values[2]:raise ValueError('Invalid native P control')
            native.append((fields[0],int(fields[1]),int(fields[2])))
        else:raise ValueError('Malformed selected native control')
    rank=pr['rank'];counts=list(map(int,(Path(prep['cwd'])/'compact-state.meta').read_text().splitlines()[1].split()))
    rr=[1,(rank+1)//2,rank];jj=[1,(counts[1]+1)//2,counts[1]]
    expected=[('left',r,j) for r in rr for j in (1,32,33,64)]+[('right',r,j) for _ in range(2) for r in rr for j in jj]
    if Counter(native)!=Counter(expected) or any(len(v)!=2 for v in cpu.values()):raise ValueError('Incomplete selected native controls')
    counts=list(map(int,(Path(prep['cwd'])/'compact-state.meta').read_text().splitlines()[1].split()))
    checked=controls(root,prep['cwd'],*counts[:2],pr['rank'],pr['beta']);check_pins(m)
    outputs={name:identity(root/name) for name in ('compact-tile-checks.txt','compact-partial-p.bin','compact-kernel-1.bin','compact-kernel-2.bin')}
    return dict(terminal_guard_pass=True,inputs_unchanged=True,manifest_sha256=digest(mp),verified_input_count=len(pins),receipt=receipt,
                native_controls=30,native_derivative_max_absolute_difference=derivative_error,**cpu,**checked,outputs=outputs,
                complete_P=False,full_space_norm_measured=False,conditioned_gap_error_bounded=False,physical_response_verified=False)
