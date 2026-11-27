"""Certify actual-input ordered linear-image restart qualification."""
from array import array
import argparse
import json
import math
from pathlib import Path
import re

from fetch_public_response_inputs import digest
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def checkpoint(root):
    root = Path(root)
    lines = (root/'linear-image-checkpoint.meta').read_text().splitlines()
    if len(lines) != 4 or lines[0] != 'ordered-linear-image-checkpoint-v1; unnormalized partial sums':
        raise ValueError('Stale linear image checkpoint schema')
    if not re.fullmatch('[0-9a-f]{64}',lines[1]):
        raise ValueError('Invalid linear image checkpoint context')
    fields = list(map(int,lines[2].split()))
    if len(fields) != 5:
        raise ValueError('Invalid linear image checkpoint dimensions')
    left,right,size,columns,completed = fields
    if min(left,right) < 1 or size != max(left,right) or not 1 <= columns <= 64 or not 1 <= completed <= left:
        raise ValueError('Invalid linear image checkpoint row range')
    beta = float(lines[3]);values = array('d')
    path = root/'linear-image-checkpoint.bin'
    if values.itemsize != 8 or path.stat().st_size != 8*size*2*columns:
        raise ValueError('Stale linear image checkpoint binary shape')
    with path.open('rb') as stream:
        values.fromfile(stream,2*size*columns)
    if not math.isfinite(beta) or beta <= 0 or not all(map(math.isfinite,values)):
        raise ValueError('Nonfinite linear image checkpoint data')
    for column in range(columns):
        offset = column*2*size
        if any(values[offset+completed:offset+size]) or any(values[offset+size+right:offset+2*size]):
            raise ValueError('Nonzero uncomputed linear image checkpoint rows')
    return dict(context=lines[1],counts=fields[:4],completed=completed,beta=beta)


def certify(root):
    root = Path(root).absolute()
    protocol = root/'run-manifest.json';receipt = root/'results/basissplit/receipt.json'
    m = json.loads(protocol.read_text());r = json.loads(receipt.read_text())
    if ((r.get('status'),r.get('exit'),r.get('error'),r.get('command'),r.get('cwd'),r.get('continuous_deadline_s'))
            != ('PASS',0,None,m['command'],str(root),420)
            or not math.isfinite(r['wall_s']) or not 0 <= r['wall_s'] < 420
            or r['guard_source_sha256'] != digest(RESEARCH/'macos_native_guard.py')):
        raise ValueError('Unaccepted basis split receipt')
    verify_postrun_inputs(m,root)
    saved = checkpoint(root);split = checkpoint(root/'split')
    expected_beta = json.loads((RESEARCH/'portable_z_partial_result.json').read_text())['beta']
    for data,rows in ((saved,64),(split,32)):
        if data != dict(context=m['context_sha256'],counts=[66867,67940,67940,16],completed=rows,beta=expected_beta):
            raise ValueError('Stale actual-input basis checkpoint')
    log = (root/'results/basissplit/console.log').read_text()
    for marker in ('BASIS_SWEEP_SPLIT_BITWISE_PASS','BASIS_SWEEP_CHECKPOINT_PASS'):
        if log.count(marker) != 1:
            raise ValueError('Incomplete basis split qualification')
    result = dict(status='PASS',checkpoint=saved,split_checkpoint=split,
        split_qualification_passed=True,full_images=False,physical_response_verified=False,receipt=r,
        manifest_sha256=digest(protocol),receipt_sha256=digest(receipt),
        checkpoint_sha256=digest(root/'linear-image-checkpoint.bin'),
        metadata_sha256=digest(root/'linear-image-checkpoint.meta'),
        executable_sha256=digest(root/'basis-sweep.x'),analysis_source_sha256=digest(Path(__file__)))
    (root/'basis-split-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path)
    print(json.dumps(certify(parser.parse_args().root),indent=2))
