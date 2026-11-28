"""Exact-rational signed controls and bounded-shape throughput; not a material bound."""
import array
from fractions import Fraction as F
import math
from pathlib import Path
import sys

ACTIVE=134807
OFF_DIAGONAL=9085887960
RANK=51


def pattern(i,j,which):
    if which==1:return ((17*i+13*j)%31-15)/16+(-1)**(i+j)*(i+j)*2.**-40
    return ((11*i+7*j)%29-14)/16+(-1)**(i+j)*(i+2*j)*2.**-43


def binary(path,count):
    if sys.byteorder!='little' or Path(path).stat().st_size!=8*count:raise ValueError('Stale tile binary shape or byte order')
    values=array.array('d')
    with Path(path).open('rb') as stream:values.fromfile(stream,count)
    if not all(map(math.isfinite,values)):raise ValueError('Nonfinite tile output')
    return values


def dot_check(actual,a,b):
    # Exact represented input/output values. Conventional 2k elementary-rounding
    # allowance; a tested arithmetic model, not proof about an opaque library.
    terms=[F(x)*F(y) for x,y in zip(a,b)];k=len(terms)
    gamma=F(2*k,2**53-2*k)
    error=abs(F(actual)-sum(terms));bound=gamma*sum(map(abs,terms))
    if error>bound:raise ValueError('Exact rational tile product differs')
    return float(error),float(bound)


def controls(path):
    data=binary(path,286);offset=0;errors=[];bounds=[]
    for kind in ('P','U'):
        m,n,r=7,5,9;inner=m if kind=='P' else r;rows=r if kind=='P' else m
        a=data[offset:offset+m*r];offset+=m*r
        b=data[offset:offset+inner*n];offset+=inner*n
        c=data[offset:offset+rows*n];offset+=rows*n
        if (any(a[j*m+i]!=pattern(i+1,j+1,1) for j in range(r) for i in range(m))
                or any(b[j*inner+i]!=pattern(i+1,j+1,2) for j in range(n) for i in range(inner))):
            raise ValueError('Changed signed tile inputs')
        for j in range(n):
            for i in range(rows):
                left=a[i*m:(i+1)*m] if kind=='P' else [a[k*m+i] for k in range(r)]
                error,bound=dot_check(c[j*rows+i],left,b[j*inner:(j+1)*inner]);errors.append(error);bounds.append(bound)
    return dict(entries_checked=len(errors),max_absolute_error=max(errors),max_absolute_bound=max(bounds))


def analyze(root,prefix,mode='benchmark'):
    if prefix not in ('reference','accelerate') or mode not in ('fixture','benchmark'):raise ValueError('Unsupported tile analysis mode')
    root=Path(root);lines=(root/f'{prefix}-summary.txt').read_text().splitlines()
    shapes=[(9,11,3,128)] if mode=='fixture' else [(256,384,51,32),(512,768,51,32),(1024,1024,51,32)]
    if lines[0]!=f'tile-blas-probe-v1 {mode}' or len(lines)!=1+2*len(shapes):raise ValueError('Stale tile summary')
    samples=binary(root/f'{prefix}-samples.bin',18*len(shapes));timings=[];errors=[]
    for index,line in enumerate(lines[1:]):
        fields=line.split();kind=('P','U')[index%2];case=index//2;m,n,r,reps=shapes[case]
        if len(fields)!=8 or fields[0]!=kind or list(map(int,fields[1:6]))!=[case+1,m,n,r,reps]:raise ValueError('Different tile dimensions')
        wall,cpu=map(float,fields[6:])
        if not (math.isfinite(wall) and math.isfinite(cpu) and wall>0 and cpu>=0):raise ValueError('Invalid tile timing')
        rows=r if kind=='P' else m;inner=m if kind=='P' else r
        for jj,j in enumerate((1,(n+1)//2,n)):
            for ii,i in enumerate((1,(rows+1)//2,rows)):
                left=[pattern(k,i,1) if kind=='P' else pattern(i,k,1) for k in range(1,inner+1)]
                right=[pattern(k,j,2) for k in range(1,inner+1)]
                error,bound=dot_check(samples[9*index+3*jj+ii],left,right);errors.append(error)
        flops=2*m*n*r*reps
        timings.append(dict(kind=kind,case=case+1,tile_rows=m,tile_columns=n,rank=r,repetitions=reps,
                            wall_s=wall,process_cpu_s=cpu,requested_threads=1,flops=flops,gflops_per_s=flops/wall/1e9))
    projections=[]
    if mode=='benchmark':
        for p,u in zip(timings[::2],timings[1::2]):
            first=2*RANK*OFF_DIAGONAL/(p['gflops_per_s']*1e9)
            second=2*RANK*ACTIVE**2/(u['gflops_per_s']*1e9)
            projections.append(dict(case=p['case'],first_pass_contraction_s=first,second_pass_contraction_s=second,
                                    contraction_only_s=first+second))
    return dict(prefix=prefix,signed_controls=controls(root/f'{prefix}-controls.bin'),timings=timings,
                benchmark_samples_checked=len(samples),sample_max_absolute_error=max(errors),
                projections=projections,scope=__doc__,conditioned_gap_error_bounded=False,physical_response_verified=False)
