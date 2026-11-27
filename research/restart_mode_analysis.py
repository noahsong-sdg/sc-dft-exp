"""Track a declared restart target; advancement is not scientific seed acceptance."""
import argparse
import json
import math
from pathlib import Path

from enlarged_basis_analysis import read_reduced
from initial_basis_analysis import binary
from occupation_enrichment import dot
from portable_basis_enrichment import parent
from portable_basis_restart import accepted_restart
from fetch_public_response_inputs import digest


def overlap(target,coefficients):
    if len(coefficients)<len(target) or not all(map(math.isfinite,(*target,*coefficients))):
        raise ValueError('Invalid mode overlap dimensions/values')
    norms=math.sqrt(dot(target,target)*dot(coefficients,coefficients))
    if norms==0:raise ValueError('Zero mode in overlap')
    return abs(dot(target,coefficients[:len(target)]))/norms


def advancement(reference,tracked,same_sign):
    residual=tracked['relative_residual']
    if not math.isfinite(residual) or residual<0 or not math.isfinite(reference) or reference<=0:
        raise ValueError('Invalid tracked residual')
    reduction=reference/residual if residual else None
    advance=(tracked['normalized_overlap']>=.99 and residual<=reference/2 and same_sign
        and tracked['eigenvalue']>1)
    return reduction,advance


def inspect(restart,basis,analysis):
    restart,basis,analysis=(Path(p).absolute() for p in (restart,basis,analysis))
    r=accepted_restart(restart);m,saved,_=parent(basis)
    proof=json.loads((basis/'basis-enrichment-result.json').read_text())
    if (not proof['full_images_native_checked'] or saved['completed']!=66867
            or m['basis_source']!=str(restart) or m['old_columns']!=16
            or m['operator_context_sha256']!=r['operator_context_sha256']):
        raise ValueError('Incompatible restarted operator application')
    for name,value in proof['full_output_sha256'].items():
        if digest(basis/name)!=value:raise ValueError('Changed restarted basis output')
    checked=json.loads(analysis.read_text())
    if (checked['status']!='PASS' or checked['basis_columns']!=32
            or checked['basis_sha256']!=digest(basis/'basis.bin')
            or checked['reduced_sha256']!=digest(basis/'reduced.bin')
            or checked['analysis_source_sha256']!=digest(Path(__file__).parent/'enlarged_basis_analysis.py')):
        raise ValueError('Stale restarted independent analysis')
    retained=binary(restart/'basis.bin',2*135880*16)
    current=binary(basis/'basis.bin',2*135880*32)
    for offset,new_offset in ((0,0),(135880*16,135880*32)):
        if retained[offset:offset+135880*16]!=current[new_offset:new_offset+135880*16]:
            raise ValueError('Restart basis/image prefix changed')
    old=Path(r['parent']);_,old_wr,_,old_vr=read_reduced(old,64)
    index=r['target_index']-1
    coefficients=binary(restart/'retained-coefficients.bin',64*16)
    target=[dot(coefficients[j*64:(j+1)*64],old_vr[index*64:(index+1)*64]) for j in range(16)]
    _,wr,wi,vr=read_reduced(basis,32)
    candidates=[]
    for mode in checked['real_modes']:
        j=mode['index']-1
        if wi[j]!=0 or wr[j]!=mode['eigenvalue']:raise ValueError('Changed tracked Ritz spectrum')
        candidates.append({**mode,'normalized_overlap':overlap(target,vr[j*32:(j+1)*32])})
    tracked=max(candidates,key=lambda x:x['normalized_overlap'])
    line=(basis/'ritz.meta').read_text().splitlines()[tracked['index']]
    fields=list(map(float,line.split()))
    same_sign=fields[5]*fields[6]>0
    reduction,advance=advancement(r['target_relative_residual'],tracked,same_sign)
    return dict(status='PASS',restart_sha256=digest(restart/'restart-result.json'),
        basis_sha256=digest(basis/'basis.bin'),analysis_sha256=digest(analysis),
        analysis_source_sha256=digest(Path(__file__)),parent_target_eigenvalue=old_wr[index],
        parent_target_relative_residual=r['target_relative_residual'],tracked_mode=tracked,
        same_sign_fermi_averages=same_sign,residual_reduction=reduction,advance_to48=advance,
        criterion='Overlap>=0.99, residual reduction>=2, same-sign Fermi averages, lambda>1; independent native/image checks required.',
        gap_seed_qualified=False,physical_response_verified=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('restart','basis','analysis'):p.add_argument(name,type=Path)
    print(json.dumps(inspect(**vars(p.parse_args())),indent=2))
