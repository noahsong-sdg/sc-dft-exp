"""Stage the first measured application after a certified offline Ritz restart."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from portable_basis_enrichment import parent,RESEARCH
from portable_basis_production import interval
from portable_basis_restart import accepted_restart,identities


def stage(basis,destination,first,last,previous=None):
    interval(first,last,previous)
    basis,root=(Path(p).absolute() for p in (basis,destination))
    if root.exists():raise ValueError('Fresh restarted sweep directory required')
    r=accepted_restart(basis)
    entries={x['path']:x for x in r['files']+r['outputs']}
    paths=[basis/'restart-result.json',Path(__file__),RESEARCH/'portable_basis_restart.py',
        RESEARCH/'portable_gap/basis_enrichment.mk',RESEARCH/'portable_gap/basis_enrichment_driver.f90']
    entries.update({x['path']:x for x in identities(paths)})
    context=hashlib.sha256(json.dumps(list(entries.values()),sort_keys=True).encode()).hexdigest()
    if previous is not None:
        previous=Path(previous).absolute();pm,saved,paths=parent(previous)
        if (pm['context_sha256']!=context or saved['completed']+1!=first
                or pm['basis_source']!=str(basis)):
            raise ValueError('Stale or noncontiguous restarted predecessor')
        entries.update({x['path']:x for x in identities(paths)})
    root.mkdir();shutil.copy2(basis/'native.in',root/'native.in')
    control=root/'basis-enrichment-control.in'
    control.write_text('fresh-basis-enrichment-control-v1\n'+r['geometry']+'\n'+r['z_directory']+'\n'
        +str(basis/'next-vectors.bin')+'\n'+context+'\n'+f'{first} {last}\n'
        +(str(previous) if previous else '-')+'\n'+r['operator_context_sha256']+'\n'+str(basis)+'\n')
    entries.update({x['path']:x for x in identities([control,root/'native.in'])})
    command=r['parent_manifest']['command'].copy()
    command[-2]='NATIVE_INPUT='+str(root/'native.in')
    m=dict(cwd=str(root),command=command,files=list(entries.values()),context_sha256=context,
        operator_context_sha256=r['operator_context_sha256'],basis_source=str(basis),old_columns=16,
        restart_source=str(basis/'restart-result.json'),rows=[first,last],
        predecessor=str(previous) if previous else None,temperature_kelvin=8.05,trial_columns=16,
        tile_width=32,guard_seconds=600,launch_normal_seconds=120,
        acceptance='Same native operator, retained16 plus fresh measured16 images; final uncached oracle and Ritz; no relaxation of seed/gap gates.',
        forecast='250–300s per segment, not a bound;600s/3GiB/quiet120. Unchanged qualified contraction.')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    return m


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('basis','destination'):p.add_argument(name,type=Path)
    p.add_argument('--first',type=int,required=True);p.add_argument('--last',type=int,required=True)
    p.add_argument('--previous',type=Path)
    print(json.dumps(stage(**vars(p.parse_args())),indent=2))
