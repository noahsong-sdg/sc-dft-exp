"""Compare a fresh binary64 grid with the grid prefix of a native saved state.

Explicit native-init-v1 little-endian binary64/int32 layout; never rewrites data.
"""
import argparse
import json
import math
from pathlib import Path
import struct

from compare_legacy_gap import digest


def compare(fresh, metadata, state):
    fresh, metadata, state = map(Path, (fresh, metadata, state))
    lines = metadata.read_text().splitlines()
    if len(lines) != 4 or lines[0] != 'native-init-v1; arrays are native binary64/int32, Fortran order':
        raise ValueError('Unsupported saved initialization metadata')
    counts = list(map(int, lines[1].split()))
    if len(counts) != 7 or min(counts) < 1 or counts[2] != max(counts[:2]):
        raise ValueError('Invalid saved initialization dimensions')
    nx, maximum = counts[3], counts[2]
    scalars = list(map(float, lines[2].split()))
    if len(scalars) != 7 or not all(map(math.isfinite, scalars)) or lines[3].strip() not in ('T', 'F'):
        raise ValueError('Invalid initialization scalar metadata')
    if fresh.stat().st_size != 16*nx or state.stat().st_size != 16*nx+96*maximum:
        raise ValueError('Stale grid or saved-state binary shape')
    actual = struct.unpack('<' + 'd'*(2*nx), fresh.read_bytes())
    with state.open('rb') as source:
        saved = struct.unpack('<' + 'd'*(2*nx), source.read(16*nx))
    if not all(map(math.isfinite, (*actual, *saved))) or min(actual[nx:]) <= 0 or min(saved[nx:]) <= 0:
        raise ValueError('Invalid finite positive-weight quadrature')
    sections = {}
    for name, offset in (('xi0', 0), ('dx0', nx)):
        differences = []
        for i in range(nx):
            a, b = actual[offset+i], saved[offset+i]
            if a.hex() != b.hex():
                differences.append(dict(index=i+1, fresh_hex=a.hex(), saved_hex=b.hex(),
                                        absolute_difference=abs(a-b),
                                        ulps_at_saved_value=abs(a-b)/math.ulp(b)))
        sections[name] = differences
    return dict(fresh_sha256=digest(fresh), saved_state_sha256=digest(state),
                metadata_sha256=digest(metadata), nx=nx, differences=sections,
                scope='Grid prefix comparison only; no state/Z acceptance, no tolerance change')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('fresh', type=Path)
    parser.add_argument('metadata', type=Path)
    parser.add_argument('state', type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(args.fresh, args.metadata, args.state), indent=2, allow_nan=False))
