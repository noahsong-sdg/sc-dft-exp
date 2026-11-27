"""Check mode continuity across a complete certified basis extension."""
import argparse
import json
from pathlib import Path

from enlarged_basis_analysis import read_reduced
from fetch_public_response_inputs import digest
from portable_basis_enrichment import parent
from restart_mode_analysis import overlap,advancement


def check_prefix(previous,current,size,old_columns,new_columns):
    """Q and AQ have different offsets after extension; compare actual bytes."""
    count=8*size*old_columns
    if (not 0<old_columns<new_columns or previous.stat().st_size!=2*count
            or current.stat().st_size!=16*size*new_columns):
        raise ValueError('Stale extended basis shape')
    with previous.open('rb') as before,current.open('rb') as after:
        for side in range(2):
            before.seek(side*count);after.seek(side*8*size*new_columns)
            remaining=count
            while remaining:
                take=min(remaining,1024*1024)
                if before.read(take)!=after.read(take):
                    raise ValueError('Changed retained Q/AQ bytes')
                remaining-=take


def qualified(root,analysis):
    m,saved,_=parent(root)
    proof=json.loads((root/'basis-enrichment-result.json').read_text())
    if not proof['full_images_native_checked'] or saved['completed']!=66867:
        raise ValueError('Complete certified images required')
    for name,value in proof['full_output_sha256'].items():
        if digest(root/name)!=value:raise ValueError('Changed certified basis output')
    checked=json.loads(analysis.read_text());columns=checked['basis_columns']
    if (checked['status']!='PASS' or checked['basis_sha256']!=digest(root/'basis.bin')
            or checked['reduced_sha256']!=digest(root/'reduced.bin')
            or checked['analysis_source_sha256']!=digest(Path(__file__).parent/'enlarged_basis_analysis.py')):
        raise ValueError('Stale independent basis analysis')
    meta=(root/'basis.meta').read_text().splitlines()
    if (len(meta)!=5 or meta[0]!='tc-basis-v1' or meta[1].split()!=['135880',str(columns)]
            or meta[3]!=m['operator_context_sha256'] or float(meta[2])!=saved['beta']):
        raise ValueError('Inconsistent basis operator metadata')
    return m,checked,meta


def inspect(previous,current,previous_analysis,current_analysis):
    previous,current,previous_analysis,current_analysis=(Path(p).absolute() for p in
        (previous,current,previous_analysis,current_analysis))
    pm,old,pmeta=qualified(previous,previous_analysis)
    cm,new,cmeta=qualified(current,current_analysis)
    before,after=old['basis_columns'],new['basis_columns']
    if (cm['basis_source']!=str(previous) or cm['old_columns']!=before or after!=before+16
            or cmeta[2:]!=pmeta[2:]):raise ValueError('Changed extension operator/context')
    check_prefix(previous/'basis.bin',current/'basis.bin',135880,before,after)
    index=old['selected_index']-1
    if index<0:raise ValueError('Previous conventional mode required for tracking')
    _,_,old_wi,old_vr=read_reduced(previous,before)
    if old_wi[index]!=0:raise ValueError('Real previous target required')
    target=old_vr[index*before:(index+1)*before]
    reference=[x for x in old['real_modes'] if x['index']==index+1]
    if len(reference)!=1:raise ValueError('Missing previous independent residual')
    _,wr,wi,vr=read_reduced(current,after)
    candidates=[]
    for mode in new['real_modes']:
        j=mode['index']-1
        if wi[j]!=0 or wr[j]!=mode['eigenvalue']:raise ValueError('Changed mode spectrum')
        candidates.append({**mode,'normalized_overlap':overlap(target,vr[j*after:(j+1)*after])})
    tracked=max(candidates,key=lambda x:x['normalized_overlap'])
    fields=list(map(float,(current/'ritz.meta').read_text().splitlines()[tracked['index']].split()))
    same_sign=fields[5]*fields[6]>0
    reduction,advance=advancement(reference[0]['relative_residual'],tracked,same_sign)
    paths=[previous_analysis,current_analysis,previous/'basis.bin',current/'basis.bin',
        previous/'reduced.bin',current/'reduced.bin',Path(__file__),Path(__file__).parent/'restart_mode_analysis.py']
    return dict(status='PASS',previous_columns=before,current_columns=after,
        previous_mode=reference[0],tracked_mode=tracked,same_sign_fermi_averages=same_sign,
        residual_reduction=reduction,admit_next_extension=advance and after<64,
        criterion='Same mode overlap>=0.99, residual reduction>=2, same-sign averages, lambda>1;64-vector cap.',
        sha256={str(p):digest(p) for p in paths},gap_seed_qualified=False,physical_response_verified=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('previous','current','previous_analysis','current_analysis'):p.add_argument(name,type=Path)
    print(json.dumps(inspect(**vars(p.parse_args())),indent=2))
