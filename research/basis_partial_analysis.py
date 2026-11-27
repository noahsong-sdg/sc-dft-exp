"""Certify the bounded actual-input fresh-basis qualification and its forecast."""
import argparse
from array import array
import json
import math
from pathlib import Path

from fetch_public_response_inputs import digest
from public_band_pilot_analysis import verify_postrun_inputs

RESEARCH = Path(__file__).resolve().parent


def read_payload(path, rows, columns):
    """Read vectors followed by images, each (rows, 2, columns) binary64."""
    values = array('d')
    expected_bytes = 2 * rows * 2 * columns * 8
    if values.itemsize != 8 or path.stat().st_size != expected_bytes:
        raise ValueError('Stale partial basis binary shape')
    with path.open('rb') as stream:
        values.fromfile(stream, expected_bytes // 8)
    if not all(map(math.isfinite, values)):
        raise ValueError('Nonfinite partial basis data')
    return values


def certify(root):
    root=Path(root).absolute()
    m=json.loads((root/'run-manifest.json').read_text())
    receipt=root/'results/basispartial/receipt.json';r=json.loads(receipt.read_text())
    if ((r.get('status'),r.get('exit'),r.get('error'),r.get('command'),r.get('cwd'),r.get('continuous_deadline_s'))
            != ('PASS',0,None,m['command'],str(root),420)
            or not math.isfinite(r['wall_s']) or not 0 <= r['wall_s'] < 420
            or r['guard_source_sha256'] != digest(RESEARCH/'macos_native_guard.py')):
        raise ValueError('Unaccepted partial basis receipt')
    verify_postrun_inputs(m,root)
    log=(root/'results/basispartial/console.log').read_text()
    if log.count('BASIS_PARTIAL_UNCACHED_CONTROL_PASS') != 1:
        raise ValueError('Missing partial basis acceptance')
    lines=(root/'basis-partial.meta').read_text().splitlines()
    if (len(lines)!=3 or lines[0]!='fresh-basis-partial-v1; four64row blocks; not full images or solved gap'
            or list(map(int,lines[1].split())) != [66867,67940,67940,16,29]):
        raise ValueError('Stale partial basis metadata')
    numbers=list(map(float,lines[2].split()))
    if (len(numbers)!=7 or not all(map(math.isfinite,numbers))
            or numbers[0] != json.loads((RESEARCH/'portable_z_partial_result.json').read_text())['beta']
            or not 0 <= numbers[1] <= numbers[2] or min(numbers[3:]) <= 0):
        raise ValueError('Invalid partial basis controls')
    payload=root/'basis-partial.bin'
    values=read_payload(payload,67940,16)
    # Validate both vector and image padding without duplicating the full operator.
    vector_size=2*67940;block_size=16*vector_size
    for part in (0,block_size):
        for column in range(16):
            offset=part+column*vector_size
            if any(values[offset+66867:offset+67940]):
                raise ValueError('Nonzero partial basis padding')
    gram_error=0.
    for i in range(16):
        for j in range(i+1):
            value=math.fsum(values[i*vector_size+k]*values[j*vector_size+k] for k in range(vector_size))
            gram_error=max(gram_error,abs(value-int(i==j)))
    if gram_error > 1e-10:
        raise ValueError('Fresh trial Gram matrix failed')
    timings=numbers[3:]
    result=dict(status='PASS',manifest_sha256=digest(root/'run-manifest.json'),receipt_sha256=digest(receipt),
        binary_sha256=digest(payload),metadata_sha256=digest(root/'basis-partial.meta'),
        executable_sha256=digest(root/'basis-partial.x'),analysis_source_sha256=digest(Path(__file__)),
        receipt=r,beta=numbers[0],uncached_error=numbers[1],uncached_bound=numbers[2],
        trial_gram_error=gram_error,block_wall_s=timings,
        row_only_full_sweep_forecast_s=dict(mean=sum(timings)/256*66867,
            sampled_min=min(timings)/64*66867,sampled_max=max(timings)/64*66867),
        partial_images_only=True,physical_response_verified=False,
        forecast_limitation='Row extrapolation from four64-row blocks, not a runtime bound or isolated workflow benchmark')
    (root/'basis-partial-result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    print(json.dumps(certify(p.parse_args().root),indent=2))
