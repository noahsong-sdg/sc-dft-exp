"""Stage strictly contiguous, context-pinned finite-temperature Z batches."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import struct

from fetch_public_response_inputs import digest, validate
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def checkpoint(root):
    root = Path(root)
    lines = (root/'z-checkpoint.meta').read_text().splitlines()
    if len(lines) != 4 or lines[0] != 'ordered-Z-checkpoint-v1; partial sums, not full Z':
        raise ValueError('Stale Z checkpoint schema')
    if not re.fullmatch('[0-9a-f]{64}', lines[1]):
        raise ValueError('Invalid Z checkpoint context')
    fields = list(map(int, lines[2].split()))
    if len(fields) != 4:
        raise ValueError('Invalid Z checkpoint dimensions')
    left, right, size, completed = fields
    beta = float(lines[3])
    if min(left,right) < 1 or size != max(left,right) or not 1 <= completed <= left:
        raise ValueError('Invalid Z checkpoint row range')
    payload = (root/'z-checkpoint.bin').read_bytes()
    if len(payload) != 16*size:
        raise ValueError('Stale Z checkpoint binary shape')
    values = struct.unpack('<'+str(2*size)+'d', payload)
    if not math.isfinite(beta) or beta <= 0 or not all(map(math.isfinite,values)):
        raise ValueError('Nonfinite Z checkpoint data')
    if any(values[completed:size]) or any(values[size+right:]):
        raise ValueError('Nonzero uncomputed Z checkpoint rows')
    return dict(context=lines[1],counts=[left,right,size],completed=completed,beta=beta)


def certify(root):
    """Read back a terminal batch and bind its output identities for the next batch."""
    root = Path(root).absolute()
    protocol = root/'run-manifest.json'; receipt = root/'results/zsweep/receipt.json'
    m = json.loads(protocol.read_text()); r = json.loads(receipt.read_text())
    if ((r.get('status'),r.get('exit'),r.get('error'),r.get('command'),r.get('cwd'),r.get('continuous_deadline_s'))
            != ('PASS',0,None,m['command'],str(root),m['guard_seconds'])
            or not math.isfinite(r['wall_s']) or not 0 <= r['wall_s'] < m['guard_seconds']
            or r['guard_source_sha256'] != digest(RESEARCH/'macos_native_guard.py')):
        raise ValueError('Unaccepted terminal Z sweep receipt')
    verify_postrun_inputs(m,root)
    saved = checkpoint(root)
    if (saved['context'] != m['context_sha256'] or saved['completed'] != m['rows'][1]
            or saved['counts'] != [66867,67940,67940]
            or saved['beta'] != json.loads((RESEARCH/'portable_z_partial_result.json').read_text())['beta']):
        raise ValueError('Z checkpoint differs from registered sweep')
    log = (root/'results/zsweep/console.log').read_text()
    if (log.count('Z_SWEEP_CHECKPOINT_PASS') != 1
            or log.count('Z_SWEEP_SPLIT_BITWISE_PASS') != int(m['qualification'])):
        raise ValueError('Incomplete Z sweep output')
    result = dict(status='PASS',checkpoint=saved,manifest_sha256=digest(protocol),receipt_sha256=digest(receipt),
        checkpoint_sha256=digest(root/'z-checkpoint.bin'),metadata_sha256=digest(root/'z-checkpoint.meta'),
        executable_sha256=digest(root/'z-sweep.x'),receipt=r,
        split_qualification_passed=m['qualification'],full_Z_qualified=False,physical_response_verified=False)
    (root/'z-sweep-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def stage(build, initialization, partial, inputs, destination, first, last, previous=None, qualification=False):
    build, initialization, partial, inputs, root = map(lambda p: Path(p).absolute(),
        (build, initialization, partial, inputs, destination))
    if root.exists():
        raise ValueError('Fresh Z sweep directory required')
    if not 1 <= first <= last <= 66867 or last-first+1 > 33434:
        raise ValueError('Invalid bounded Z sweep interval')
    if qualification:
        if (first,last,previous) != (1,16,None):
            raise ValueError('Qualification requires rows1:16 without predecessor')
    elif previous is None:
        raise ValueError('Qualified predecessor required')
    parents = []
    for parent,label,token in [(initialization,'init','FRESH_GAP_INITIALIZATION_ROUNDTRIP_PASS'),
            (partial,'zpartial','Z_PARTIAL_DIRECT_CACHED_PASS')]:
        protocol = parent/'run-manifest.json'; receipt = parent/'results'/label/'receipt.json'
        m = json.loads(protocol.read_text()); r = json.loads(receipt.read_text())
        if (r.get('status'),r.get('exit'),r.get('error'),r.get('command'),r.get('cwd')) != ('PASS',0,None,m['command'],str(parent)):
            raise ValueError('Unaccepted Z preparation parent')
        log = parent/'results'/label/'console.log'
        if log.read_text().count(token) != 1:
            raise ValueError('Incomplete Z preparation parent')
        verify_postrun_inputs(m,parent)
        parents += [protocol,receipt,log]
    accepted = RESEARCH/'fresh_gap_initialization_result.json'
    state = json.loads(accepted.read_text())
    if (state['retained_state_consumed'] or not state['exact_own_array_roundtrip']
            or digest(initialization/'native-init.bin') != state['state_sha256']
            or digest(initialization/'native-init.meta') != state['metadata_sha256']):
        raise ValueError('Changed fresh initialization state')
    partial_proof = RESEARCH/'portable_z_partial_result.json'
    comparison = json.loads(partial_proof.read_text())
    if not comparison['partial_arrays_bitwise_equal'] or digest(partial/'z-partial.bin') != comparison['binary_sha256']:
        raise ValueError('Changed direct/cached Z qualification')
    common = [initialization/'native-init.meta',initialization/'native-init.bin',initialization/'native.in']
    for catalog in [RESEARCH/'public_response_inputs.json',RESEARCH/'public_gap_coulomb_inputs.json']:
        common.append(catalog)
        for name,item in json.loads(catalog.read_text())['files'].items():
            p = inputs/validate(name,item)
            if p.stat().st_size != item['bytes'] or digest(p) != item['sha256']:
                raise ValueError('Changed microscopic input: '+name)
            common.append(p)
    native = initialization/'native.in'
    if native.read_text().count("outdir='"+str(inputs)+"/'") != 1:
        raise ValueError('Different microscopic input directory')
    common += [Path(__file__),RESEARCH/'macos_native_guard.py',RESEARCH/'public_response_probe.mk',
        build/'build-result.json',build/'qe/make.inc']
    common += [RESEARCH/'portable_gap'/n for n in ('z_sweep_driver.f90','z_checkpoint.f90',
        'z_sweep.mk','z_partial.mk','z_build.mk','prefix_operator.f90','zsf_workspace.f90',
        'native_rotation.f90','slab_operator.f90','native_state_io.f90','native_coefficients.f90',
        'hash_stream.c','hash_pipe.c')]
    common += sorted(build.rglob('*.a'))+sorted((build/'qe').rglob('*.mod'))
    identities = [dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in common]
    context = hashlib.sha256(json.dumps(identities,sort_keys=True).encode()).hexdigest()
    if previous is not None:
        previous = Path(previous).absolute()
        proof = previous/'z-sweep-result.json'
        qualified = json.loads(proof.read_text())
        pm = json.loads((previous/'run-manifest.json').read_text())
        r = json.loads((previous/'results/zsweep/receipt.json').read_text())
        if (qualified['status'] != 'PASS'
                or qualified['manifest_sha256'] != digest(previous/'run-manifest.json')
                or qualified['receipt_sha256'] != digest(previous/'results/zsweep/receipt.json')
                or qualified['checkpoint_sha256'] != digest(previous/'z-checkpoint.bin')
                or qualified['metadata_sha256'] != digest(previous/'z-checkpoint.meta')):
            raise ValueError('Changed certified Z checkpoint')
        if (r.get('status'),r.get('exit'),r.get('error'),r.get('command'),r.get('cwd')) != ('PASS',0,None,pm['command'],str(previous)):
            raise ValueError('Unaccepted Z checkpoint predecessor')
        verify_postrun_inputs(pm,previous)
        saved = checkpoint(previous)
        if (pm['context_sha256'] != context or saved['context'] != context
                or saved['counts'] != [66867,67940,67940] or saved['beta'] != comparison['beta']
                or saved['completed'] != pm['rows'][1] or first != saved['completed']+1
                or not pm['qualified_chain']):
            raise ValueError('Stale or noncontiguous Z checkpoint')
        log = previous/'results/zsweep/console.log'
        if log.read_text().count('Z_SWEEP_CHECKPOINT_PASS') != 1:
            raise ValueError('Incomplete Z checkpoint predecessor')
        parents += [proof,previous/'run-manifest.json',previous/'results/zsweep/receipt.json',log,
            previous/'z-checkpoint.meta',previous/'z-checkpoint.bin']
    root.mkdir(parents=True)
    if qualification:
        (root/'split').mkdir()
    shutil.copy2(native,root/'native.in')
    control = root/'z-sweep-control.in'
    control.write_text('fresh-Z-sweep-control-v1\n'+str(initialization)+'\n'+context+'\n'
        +str(first)+' '+str(last)+'\n'+(str(previous) if previous is not None else '-')+'\n'
        +('qualify' if qualification else 'sweep')+'\n')
    extras = parents+[accepted,partial_proof,root/'native.in',control]
    identities += [dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in extras]
    command = ['/usr/bin/make','-f',str(RESEARCH/'portable_gap/z_sweep.mk'),
        'RESEARCH='+str(RESEARCH),'QE_ROOT='+str(build/'qe'),
        'NATIVE_INPUT='+str(root/'native.in'),'qualify-sweep']
    manifest = dict(cwd=str(root),command=command,files=identities,context_sha256=context,
        rows=[first,last],qualification=qualification,qualified_chain=True,
        predecessor=None if previous is None else str(previous),temperature_kelvin=8.05,
        guard_seconds=240 if qualification else 2400,launch_normal_seconds=120,
        acceptance='Strict fresh state/context, contiguous serial accumulation; split16 vs8+8 bitwise in qualification; full-Z output only at completed66867; full-sum sample oracles separate',
        forecast='Qualification below240s/3GiB; production <=33434rows below2400s/3GiB based on current partial timings; forecast is not a bound')
    (root/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('build','initialization','partial','inputs','destination'):
        p.add_argument(name,type=Path)
    p.add_argument('--first',type=int,required=True);p.add_argument('--last',type=int,required=True)
    p.add_argument('--previous',type=Path);p.add_argument('--qualification',action='store_true')
    print(json.dumps(stage(**vars(p.parse_args())),indent=2))
