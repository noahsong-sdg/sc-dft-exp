"""Apply the unchanged operator to certified enrichment vectors in bounded batches."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil

from basis_split_analysis import checkpoint
from fetch_public_response_inputs import digest
from portable_basis_production import certified_parent,interval
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def accepted_basis(root):
    root = Path(root).absolute()
    enriched = (root/'basis-enrichment-result.json').exists()
    if enriched:
        m,saved,files = parent(root)
        proof = json.loads((root/'basis-enrichment-result.json').read_text())
    else:
        m,saved,files = certified_parent(root,False)
        proof = json.loads((root/'basis-production-result.json').read_text())
    if proof['full_images_native_checked'] is not True or saved['completed'] != 66867:
        raise ValueError('Complete qualified basis required')
    required = ('native-linear.meta','basis.meta','basis.bin','ritz.meta','reduced.bin',
        'selected.meta','next.meta','next-vectors.bin')
    if any(name not in proof['full_output_sha256'] for name in required):
        raise ValueError('Incomplete basis certificate')
    for name,value in proof['full_output_sha256'].items():
        if digest(root/name) != value:raise ValueError('Changed certified basis output')
        files.append(root/name)
    lines = (root/'basis.meta').read_text().splitlines()
    if len(lines) != 5 or lines[0] != 'tc-basis-v1':raise ValueError('Stale basis schema')
    size,columns = map(int,lines[1].split())
    operator_context = m.get('operator_context_sha256',m['context_sha256'])
    if (size != 135880 or columns not in (16,32,48) or lines[3] != operator_context
            or list(map(int,lines[4].split())) != [100,10,10,2,66867,67940]
            or (root/'next.meta').read_text().split() != ['16']
            or (root/'next-vectors.bin').stat().st_size != 8*135880*16):
        raise ValueError('Stale or exhausted basis enrichment')
    return m,files,operator_context,columns


def parent(root):
    root = Path(root).absolute();proof = root/'basis-enrichment-result.json'
    result = json.loads(proof.read_text());m = json.loads((root/'run-manifest.json').read_text())
    paths = {'manifest_sha256':root/'run-manifest.json','receipt_sha256':root/'results/basisenrichment/receipt.json',
        'checkpoint_sha256':root/'linear-image-checkpoint.bin','metadata_sha256':root/'linear-image-checkpoint.meta',
        'executable_sha256':root/'basis-enrichment.x'}
    if result['status'] != 'PASS' or any(result[key] != digest(path) for key,path in paths.items()):
        raise ValueError('Changed certified enrichment parent')
    verify_postrun_inputs(m,root);saved = checkpoint(root)
    if saved != result['checkpoint'] or saved['context'] != m['context_sha256']:
        raise ValueError('Stale enrichment checkpoint context')
    return m,saved,list(paths.values())+[proof]


def stage(basis,destination,first,last,previous=None):
    interval(first,last,previous)
    basis,root = map(lambda p:Path(p).absolute(),(basis,destination))
    if root.exists():raise ValueError('Fresh enrichment directory required')
    bm,evidence,operator_context,old_columns = accepted_basis(basis)
    identities = {item['path']:item for item in bm['files']}
    files = evidence+[Path(__file__),RESEARCH/'portable_basis_production.py',
        RESEARCH/'portable_gap/basis_enrichment.mk',RESEARCH/'portable_gap/basis_enrichment_driver.f90']
    for path in files:
        identities[str(path)] = dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path))
    # Batch identity changes with vectors/old basis; the physical operator identity does not.
    context = hashlib.sha256(json.dumps(list(identities.values()),sort_keys=True).encode()).hexdigest()
    if previous is not None:
        previous = Path(previous).absolute();pm,saved,paths = parent(previous)
        if pm['context_sha256'] != context or saved['completed']+1 != first or pm['basis_source'] != str(basis):
            raise ValueError('Stale or noncontiguous enrichment predecessor')
        for path in paths:
            identities[str(path)] = dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path))
    control_name = 'basis-enrichment-control.in' if 'operator_context_sha256' in bm else 'basis-production-control.in'
    control = (basis/control_name).read_text().splitlines()
    root.mkdir(parents=True);shutil.copy2(basis/'native.in',root/'native.in')
    path = root/'basis-enrichment-control.in'
    path.write_text('fresh-basis-enrichment-control-v1\n'+'\n'.join(control[1:3])+'\n'
        +str(basis/'next-vectors.bin')+'\n'+context+'\n'+str(first)+' '+str(last)+'\n'
        +(str(previous) if previous else '-')+'\n'+operator_context+'\n'+str(basis)+'\n')
    for path in (path,root/'native.in'):
        identities[str(path)] = dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path))
    command = bm['command'].copy();command[2] = str(RESEARCH/'portable_gap/basis_enrichment.mk')
    command[-2] = 'NATIVE_INPUT='+str(root/'native.in');command[-1] = 'enrich-basis'
    m = dict(cwd=str(root),command=command,files=list(identities.values()),context_sha256=context,
        operator_context_sha256=operator_context,basis_source=str(basis),old_columns=old_columns,
        rows=[first,last],predecessor=str(previous) if previous else None,temperature_kelvin=8.05,
        trial_columns=16,tile_width=32,guard_seconds=600,launch_normal_seconds=120,
        acceptance='Certified next16vectors, unchanged physical operator; contiguous32-row tiles and bitwise checkpoint roundtrip; final uncached oracle before append/Ritz; not a converged gap or response.',
        forecast='250–300s per <=17715rows including setup; previous full16-vector sweep segments187–206s. Final oracle/Ritz additional, estimate not bound.600s/3GiB/quiet120.')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    return m


def certify(root):
    root = Path(root).absolute();protocol = root/'run-manifest.json';receipt = root/'results/basisenrichment/receipt.json'
    m = json.loads(protocol.read_text());r = json.loads(receipt.read_text());saved = checkpoint(root)
    if ((r.get('status'),r.get('exit'),r.get('error'),r.get('command'),r.get('cwd'),r.get('continuous_deadline_s'))
            != ('PASS',0,None,m['command'],str(root),m['guard_seconds'])
            or not math.isfinite(r['wall_s']) or not 0 <= r['wall_s'] < m['guard_seconds']
            or r['guard_source_sha256'] != digest(RESEARCH/'macos_native_guard.py')):
        raise ValueError('Unaccepted enrichment receipt')
    verify_postrun_inputs(m,root)
    beta = json.loads((RESEARCH/'portable_z_partial_result.json').read_text())['beta']
    if saved != dict(context=m['context_sha256'],counts=[66867,67940,67940,16],completed=m['rows'][1],beta=beta):
        raise ValueError('Stale enrichment output')
    full = saved['completed'] == 66867;log = (root/'results/basisenrichment/console.log').read_text()
    for marker,count in [('CHECKPOINT',1),('UNCACHED_ORACLE',int(full)),('RITZ',int(full))]:
        if log.count('BASIS_ENRICHMENT_'+marker+'_PASS') != count:raise ValueError('Incomplete enrichment output')
    outputs = {}
    if full:
        lines = (root/'native-linear.meta').read_text().splitlines()
        if len(lines) != 7:raise ValueError('Incomplete enrichment oracle')
        rows = [list(map(float,line.split())) for line in lines[1:]]
        if any(len(row) != 6 or not all(map(math.isfinite,row)) for row in rows):
            raise ValueError('Invalid enrichment oracle')
        bound = 2e-13+2e-12*max(abs(row[2]) for row in rows)
        if any(row[4] != abs(row[2]-row[3]) or not 0 <= row[4] <= row[5] or row[5] != bound for row in rows):
            raise ValueError('Enrichment oracle mismatch')
        meta = (root/'basis.meta').read_text().splitlines()
        if (len(meta) != 5 or meta[0] != 'tc-basis-v1'
                or list(map(int,meta[1].split())) != [135880,m['old_columns']+16]
                or float(meta[2]) != beta or meta[3] != m['operator_context_sha256']):
            raise ValueError('Stale enlarged basis')
        for name in ('native-linear.meta','basis.meta','basis.bin','ritz.meta','reduced.bin','selected.meta','next.meta','next-vectors.bin'):
            outputs[name] = digest(root/name)
        for name in ('selected.bin','selected-coefficients.bin'):
            if (root/name).exists():outputs[name] = digest(root/name)
    result = dict(status='PASS',checkpoint=saved,manifest_sha256=digest(protocol),receipt_sha256=digest(receipt),
        checkpoint_sha256=digest(root/'linear-image-checkpoint.bin'),metadata_sha256=digest(root/'linear-image-checkpoint.meta'),
        executable_sha256=digest(root/'basis-enrichment.x'),receipt=r,full_images_native_checked=full,
        full_output_sha256=outputs,physical_response_verified=False)
    (root/'basis-enrichment-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('basis',type=Path);p.add_argument('destination',type=Path)
    p.add_argument('--first',type=int,required=True);p.add_argument('--last',type=int,required=True);p.add_argument('--previous',type=Path)
    print(json.dumps(stage(**vars(p.parse_args())),indent=2))
