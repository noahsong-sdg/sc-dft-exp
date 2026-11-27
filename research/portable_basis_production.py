"""Stage contiguous, context-pinned fresh16-vector linear-image batches."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil

from basis_split_analysis import checkpoint
from fetch_public_response_inputs import digest
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def interval(first,last,previous):
    if (not 1 <= first <= last <= 66867 or last-first+1 > 17715
            or (first-1)%32 or (last != 66867 and last%32)
            or (first == 1) != (previous is None)):
        raise ValueError('Invalid bounded image interval or predecessor')


def certified_parent(root,qualification):
    root = Path(root).absolute()
    name,label,exe = ('basis-split','basissplit','basis-sweep') if qualification else ('basis-production','basisproduction','basis-production')
    proof = root/(name+'-result.json')
    result = json.loads(proof.read_text());m = json.loads((root/'run-manifest.json').read_text())
    paths = {'manifest_sha256':root/'run-manifest.json','receipt_sha256':root/'results'/label/'receipt.json',
        'checkpoint_sha256':root/'linear-image-checkpoint.bin','metadata_sha256':root/'linear-image-checkpoint.meta',
        'executable_sha256':root/(exe+'.x')}
    if result['status'] != 'PASS' or any(result[key] != digest(path) for key,path in paths.items()):
        raise ValueError('Changed certified image parent')
    if qualification and result['split_qualification_passed'] is not True:
        raise ValueError('Unqualified image restart')
    verify_postrun_inputs(m,root)
    saved = checkpoint(root)
    if saved != result['checkpoint'] or saved['context'] != m['context_sha256']:
        raise ValueError('Stale image parent context')
    return m,saved,list(paths.values())+[proof]


def stage(qualification,destination,first,last,previous=None):
    interval(first,last,previous)
    qualification,root = map(lambda p:Path(p).absolute(),(qualification,destination))
    if root.exists():raise ValueError('Fresh image production directory required')
    qm,_,evidence = certified_parent(qualification,True)
    # Checkpoint rows cannot be imported across the new production source context.
    identities = {item['path']:item for item in qm['files'] if not Path(item['path']).is_relative_to(qualification)}
    files = [Path(__file__),RESEARCH/'basis_split_analysis.py',RESEARCH/'portable_gap/basis_production.mk',
        RESEARCH/'portable_gap/basis_production_driver.f90']+evidence
    for path in files:
        identities[str(path)] = dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path))
    context = hashlib.sha256(json.dumps(list(identities.values()),sort_keys=True).encode()).hexdigest()
    if previous is not None:
        previous = Path(previous).absolute()
        pm,saved,paths = certified_parent(previous,False)
        if pm['context_sha256'] != context or saved['completed']+1 != first or not pm['qualified_chain']:
            raise ValueError('Stale or noncontiguous image predecessor')
        for path in paths:
            identities[str(path)] = dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path))
    control = (qualification/'basis-sweep-control.in').read_text().splitlines()
    root.mkdir(parents=True)
    shutil.copy2(qualification/'native.in',root/'native.in')
    path = root/'basis-production-control.in'
    path.write_text('fresh-basis-production-control-v1\n'+'\n'.join(control[1:4])+'\n'+context+'\n'
        +str(first)+' '+str(last)+'\n'+(str(previous) if previous else '-')+'\n')
    for path in (path,root/'native.in'):
        identities[str(path)] = dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path))
    command = qm['command'].copy();command[2] = str(RESEARCH/'portable_gap/basis_production.mk')
    command[-2] = 'NATIVE_INPUT='+str(root/'native.in');command[-1] = 'produce-basis'
    m = dict(cwd=str(root),command=command,files=list(identities.values()),context_sha256=context,
        rows=[first,last],qualified_chain=True,predecessor=str(previous) if previous else None,
        temperature_kelvin=8.05,trial_columns=16,tile_width=32,guard_seconds=600,launch_normal_seconds=120,
        acceptance='Contiguous32-row tiles; bitwise serialization; unnormalized partial images until66867; then frozen uncached native oracle before Ritz. Not a gap or response result.',
        forecast='250–300s including cold setup per <=17715-row segment, based on0.705s/64rows; final oracle/Ritz additional. Forecast not bound;600s/3GiB guard.')
    (root/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    return m


def certify(root):
    root = Path(root).absolute();protocol = root/'run-manifest.json';receipt = root/'results/basisproduction/receipt.json'
    m = json.loads(protocol.read_text());r = json.loads(receipt.read_text());saved = checkpoint(root)
    if ((r.get('status'),r.get('exit'),r.get('error'),r.get('command'),r.get('cwd'),r.get('continuous_deadline_s'))
            != ('PASS',0,None,m['command'],str(root),m['guard_seconds'])
            or not math.isfinite(r['wall_s']) or not 0 <= r['wall_s'] < m['guard_seconds']
            or r['guard_source_sha256'] != digest(RESEARCH/'macos_native_guard.py')):
        raise ValueError('Unaccepted image production receipt')
    verify_postrun_inputs(m,root)
    beta = json.loads((RESEARCH/'portable_z_partial_result.json').read_text())['beta']
    if saved != dict(context=m['context_sha256'],counts=[66867,67940,67940,16],completed=m['rows'][1],beta=beta):
        raise ValueError('Stale production checkpoint')
    log = (root/'results/basisproduction/console.log').read_text();full = saved['completed'] == 66867
    for token,count in [('BASIS_PRODUCTION_CHECKPOINT_PASS',1),('BASIS_PRODUCTION_UNCACHED_ORACLE_PASS',int(full)),('BASIS_PRODUCTION_RITZ_PASS',int(full))]:
        if log.count(token) != count:raise ValueError('Incomplete image production output')
    outputs = {}
    if full:
        lines = (root/'native-linear.meta').read_text().splitlines()
        if len(lines) != 7 or lines[0] != 'native-linear-v1; side index native saved abs-difference frozen-bound':
            raise ValueError('Incomplete native image oracle')
        rows = [list(map(float,line.split())) for line in lines[1:]]
        bound = 2e-13+2e-12*max(abs(row[2]) for row in rows)
        if (any(len(row) != 6 or not all(map(math.isfinite,row)) for row in rows)
                or any(row[4] != abs(row[2]-row[3]) or not 0 <= row[4] <= row[5] or row[5] != bound for row in rows)):
            raise ValueError('Invalid native image oracle controls')
        meta = (root/'basis.meta').read_text().splitlines()
        if len(meta) != 5 or meta[0] != 'tc-basis-v1' or list(map(int,meta[1].split())) != [135880,16] or float(meta[2]) != beta or meta[3] != m['context_sha256']:
            raise ValueError('Stale initial Ritz basis')
        for name in ('native-linear.meta','basis.meta','basis.bin','ritz.meta','reduced.bin','selected.meta','next.meta','next-vectors.bin'):
            outputs[name] = digest(root/name)
        for name in ('selected.bin','selected-coefficients.bin'):
            if (root/name).exists():outputs[name] = digest(root/name)
    result = dict(status='PASS',checkpoint=saved,manifest_sha256=digest(protocol),receipt_sha256=digest(receipt),
        checkpoint_sha256=digest(root/'linear-image-checkpoint.bin'),metadata_sha256=digest(root/'linear-image-checkpoint.meta'),
        executable_sha256=digest(root/'basis-production.x'),receipt=r,full_images_native_checked=full,
        physical_response_verified=False,full_output_sha256=outputs)
    (root/'basis-production-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('qualification',type=Path);p.add_argument('destination',type=Path)
    p.add_argument('--first',type=int,required=True);p.add_argument('--last',type=int,required=True);p.add_argument('--previous',type=Path)
    print(json.dumps(stage(**vars(p.parse_args())),indent=2))
