"""Offline same-operator Ritz retention; this produces no qualified gap seed."""
from array import array
import argparse
import json
import math
from pathlib import Path
import shutil

from enlarged_basis_analysis import read_reduced
from initial_basis_analysis import binary,relative_residual
from occupation_enrichment import dot
from portable_basis_enrichment import parent,RESEARCH
from fetch_public_response_inputs import digest
from public_band_pilot_analysis import verify_postrun_inputs


def retained_coefficients(wr,wi,vr,keep,target):
    """Keep whole real/complex DGEEV blocks, ordered by eigenvalue magnitude."""
    size=len(wr)
    if not 0 < keep < size or len(wi)!=size or len(vr)!=size*size:
        raise ValueError('Invalid restart dimensions')
    if not all(math.isfinite(x) for x in (*wr,*wi,*vr)):
        raise ValueError('Nonfinite restart spectrum')
    if not 0 <= target < size or wi[target]!=0 or wr[target]<=1:
        raise ValueError('Declared real near-one target required')
    groups=[];j=0
    while j<size:
        if wi[j]==0:
            group=[j]
        else:
            if wi[j]<=0 or j+1>=size or wr[j+1]!=wr[j] or wi[j+1]!=-wi[j]:
                raise ValueError('Invalid DGEEV conjugate pair')
            group=[j,j+1]
        groups.append(group);j+=len(group)
    chosen=[]
    for group in sorted(groups,key=lambda g:-math.hypot(wr[g[0]],wi[g[0]])):
        if len(chosen)+len(group)>keep:
            raise ValueError('Retention boundary splits a conjugate pair')
        chosen.extend(group)
        if len(chosen)==keep:break
    if target not in chosen:raise ValueError('Target would be discarded')
    columns=[];minimum=math.inf
    for index in chosen:
        c=list(vr[index*size:(index+1)*size]);original=math.sqrt(dot(c,c))
        for _ in range(2):
            for previous in columns:
                overlap=dot(previous,c)
                c=[a-overlap*b for a,b in zip(c,previous)]
        norm=math.sqrt(dot(c,c))
        if original==0 or norm<=1e-8*original:
            raise ValueError('Ill-conditioned retained Ritz span')
        minimum=min(minimum,norm/original)
        columns.append([x/norm for x in c])
    original=list(vr[target*size:(target+1)*size])
    weights=[dot(c,original) for c in columns]
    defect=[x-math.fsum(c[i]*w for c,w in zip(columns,weights)) for i,x in enumerate(original)]
    error=math.sqrt(dot(defect,defect))/math.sqrt(dot(original,original))
    if error>1e-12:raise ValueError('Restart lost its declared target')
    return columns,dict(indices=[i+1 for i in chosen],target_index=target+1,
        target_coefficient_defect=error,minimum_relative_orthogonalization_norm=minimum)


def transform(columns,coefficients):
    """Apply identical coefficients to Q and A Q; never re-evaluate a kernel."""
    return [array('d',(math.fsum(c[i]*w for c,w in zip(columns,weights))
        for i in range(len(columns[0])))) for weights in coefficients]


def identities(paths):
    return [dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in dict.fromkeys(paths)]


def check_identities(entries):
    for item in entries:
        path=Path(item['path'])
        if path.stat().st_size!=item['bytes'] or digest(path)!=item['sha256']:
            raise ValueError('Changed restart evidence: '+str(path))


def prepare(basis,analysis,output,target=3):
    basis,analysis,output=(Path(p).absolute() for p in (basis,analysis,output))
    if output.exists():raise ValueError('Fresh restart directory required')
    m,saved,evidence=parent(basis)
    proof=json.loads((basis/'basis-enrichment-result.json').read_text())
    if not proof['full_images_native_checked'] or saved['completed']!=66867:
        raise ValueError('Complete native-checked parent required')
    for name,value in proof['full_output_sha256'].items():
        if digest(basis/name)!=value:raise ValueError('Changed complete parent output')
        evidence.append(basis/name)
    checked=json.loads(analysis.read_text())
    if (checked['status']!='PASS' or checked['basis_columns']!=64
            or checked['basis_sha256']!=digest(basis/'basis.bin')
            or checked['reduced_sha256']!=digest(basis/'reduced.bin')
            or checked['analysis_source_sha256']!=digest(RESEARCH/'enlarged_basis_analysis.py')
            or checked['gram_error']>1e-10 or checked['projection_error']>2e-12):
        raise ValueError('Stale independent parent analysis')
    meta=(basis/'basis.meta').read_text().splitlines()
    context=m['operator_context_sha256']
    if (len(meta)!=5 or meta[0]!='tc-basis-v1' or meta[1].split()!=['135880','64']
            or meta[3]!=context or meta[4].split()!=['100','10','10','2','66867','67940']
            or float(meta[2])!=saved['beta']):raise ValueError('Stale restart operator context')
    _,wr,wi,vr=read_reduced(basis,64)
    coefficients,report=retained_coefficients(wr,wi,vr,16,target-1)
    values=binary(basis/'basis.bin',2*135880*64)
    q=[values[i*135880:(i+1)*135880] for i in range(64)]
    aq=[values[(64+i)*135880:(65+i)*135880] for i in range(64)]
    newq=transform(q,coefficients);newaq=transform(aq,coefficients)
    target_weights=[dot(c,vr[(target-1)*64:target*64]) for c in coefficients]
    target_residual=relative_residual(newq,newaq,target_weights,wr[target-1])
    reference=[mode for mode in checked['real_modes'] if mode['index']==target]
    if (len(reference)!=1 or not math.isfinite(target_residual)
            or abs(target_residual-reference[0]['relative_residual'])>5e-12):
        raise ValueError('Restart changed the full-image target residual')
    report.update(target_eigenvalue=wr[target-1],target_relative_residual=target_residual,
        parent_target_relative_residual=reference[0]['relative_residual'])
    next_values=binary(basis/'next-vectors.bin',135880*16)
    nextq=[next_values[i*135880:(i+1)*135880] for i in range(16)]
    gram=max(abs(dot(a,b)-int(i==j)) for i,a in enumerate(newq+nextq)
        for j,b in enumerate(newq+nextq))
    if gram>1e-10:raise ValueError('Restart basis/trial orthogonality failed')
    if any(any(c[66867:67940]) for c in newq+newaq+nextq):
        raise ValueError('Nonzero restart padding')
    sources=[Path(__file__),RESEARCH/'enlarged_basis_analysis.py',RESEARCH/'initial_basis_analysis.py',
        RESEARCH/'occupation_enrichment.py',RESEARCH/'portable_basis_enrichment.py',
        RESEARCH/'public_band_pilot_analysis.py',RESEARCH/'fetch_public_response_inputs.py']
    inputs=identities([*map(lambda x:Path(x['path']),m['files']),*evidence,analysis,*sources])
    output.mkdir();meta[1]='135880 16'
    (output/'basis.meta').write_text('\n'.join(meta)+'\n')
    with (output/'basis.bin').open('wb') as stream:
        for column in newq+newaq:column.tofile(stream)
    for name in ('next.meta','next-vectors.bin','native.in'):
        shutil.copy2(basis/name,output/name)
    with (output/'retained-coefficients.bin').open('wb') as stream:
        for column in coefficients:array('d',column).tofile(stream)
    names=('basis.meta','basis.bin','next.meta','next-vectors.bin','native.in','retained-coefficients.bin')
    control=(basis/'basis-enrichment-control.in').read_text().splitlines()
    report.update(status='PASS',schema='portable-ritz-restart-v1',parent=str(basis),
        operator_context_sha256=context,beta=saved['beta'],retained_columns=16,trial_columns=16,
        parent_manifest=m,geometry=control[1],z_directory=control[2],gram_error=gram,
        files=inputs,outputs=identities([output/name for name in names]),
        gap_seed_qualified=False,physical_response_verified=False,
        scope='Linear combinations of measured Q/AQ; same physical operator; no new kernel application.')
    # Read back the serialized columns; certification must refer to the bytes actually consumed.
    if binary(output/'basis.bin',2*135880*16)!=array('d',(x for c in newq+newaq for x in c)):
        raise ValueError('Restart serialization differs')
    check_identities(inputs)
    (output/'restart-result.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def accepted_restart(root):
    root=Path(root).absolute();path=root/'restart-result.json'
    r=json.loads(path.read_text())
    if (r['schema']!='portable-ritz-restart-v1' or r['status']!='PASS'
            or r['retained_columns']!=16 or r['trial_columns']!=16 or r['gram_error']>1e-10
            or r['gap_seed_qualified'] is not False):raise ValueError('Unaccepted restart proof')
    check_identities(r['files']);check_identities(r['outputs'])
    verify_postrun_inputs(r['parent_manifest'],Path(r['parent']))
    meta=(root/'basis.meta').read_text().splitlines()
    if (len(meta)!=5 or meta[1].split()!=['135880','16'] or meta[3]!=r['operator_context_sha256']
            or float(meta[2])!=r['beta'] or (root/'next.meta').read_text().split()!=['16']):
        raise ValueError('Stale restart metadata')
    return r


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('basis','analysis','output'):p.add_argument(name,type=Path)
    p.add_argument('--target',type=int,default=3)
    report=prepare(**vars(p.parse_args()))
    print(json.dumps({k:report[k] for k in ('status','indices','target_index','gram_error','gap_seed_qualified')}))
