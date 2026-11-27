"""Measure upstream quadrature differences; never accept or repair a gap state."""
import argparse
import json
import math
from pathlib import Path
import struct

from fetch_public_response_inputs import digest

RESEARCH = Path(__file__).resolve().parent


def stage(build, inputs, reference, destination):
    build, inputs, reference, root = map(lambda p: Path(p).absolute(),
        (build, inputs, reference, destination))
    if root.exists():
        raise ValueError('Fresh quadrature diagnostic directory required')
    qe = build/'qe'
    bands = inputs/'pwscf.a2Fsave'
    elph = inputs/'_ph0/pwscf.q_1/pwscf.elph1'
    meta = reference/'native-init.meta'
    counts = list(map(int, meta.read_text().splitlines()[1].split()))
    if len(counts) != 7 or counts[3] != 100:
        raise ValueError('Expected retained 100-node context')
    files = [Path(__file__), RESEARCH/'portable_gap/grid_probe.f90',
        RESEARCH/'portable_gap/grid_probe.mk', RESEARCH/'public_response_probe.mk',
        RESEARCH/'macos_native_guard.py', build/'build-result.json', qe/'make.inc',
        bands, elph, meta, reference/'native-init.bin']
    files += sorted(build.rglob('*.a')) + sorted(qe.rglob('*.mod'))
    entries = [dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p)) for p in files]
    command = ['/usr/bin/make', '-f', str(RESEARCH/'portable_gap/grid_probe.mk'),
        'RESEARCH='+str(RESEARCH), 'QE_ROOT='+str(qe), 'BANDS='+str(bands),
        'REFERENCE='+str(meta), 'ELPH='+str(elph), 'qualify-grid']
    manifest = dict(cwd=str(root), command=command, files=entries,
        guard_seconds=120, launch_normal_seconds=120, reference=str(reference),
        acceptance='Measure arrays, finite values and reference differences only; no state acceptance',
        forecast='One small source compile/link and 100-node quadrature; below 120s/3GiB')
    root.mkdir(parents=True)
    (root/'run-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest


def compare(payload, reference):
    if len(payload) != 4800 or len(reference) < 1600:
        raise ValueError('Stale quadrature binary shape')
    actual = struct.unpack('<600d', payload)
    expected = struct.unpack('<200d', reference[:1600])
    if not all(math.isfinite(x) for x in (*actual, *expected)):
        raise ValueError('Nonfinite quadrature data')
    result = {}
    for section, offset in [('xi0', 0), ('dx0', 100)]:
        differences = []
        for i in range(100):
            a, b = actual[200+offset+i], expected[offset+i]
            if struct.pack('<d', a) != struct.pack('<d', b):
                differences.append(dict(index=i+1, actual=a.hex(), reference=b.hex(),
                    absolute_difference=abs(a-b),
                    difference_in_reference_ulps=abs(a-b)/math.ulp(b)))
        result[section] = differences
    return dict(sections=result, transformed_grid_bitwise_equal=not any(result.values()),
        gap_state_accepted=False, scope=__doc__)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('build', 'inputs', 'reference', 'destination'):
        p.add_argument(name, type=Path)
    print(json.dumps(stage(**vars(p.parse_args())), indent=2))
