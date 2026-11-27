"""Compare exported response assignment with a gap's initialized native layout."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

from compare_legacy_gap import native_arrays


def analyze(directory, prepare_directory):
    root, prepare = Path(directory), Path(prepare_directory)
    summary, binary = root/'response-assignment.txt', root/'response-assignment.bin'
    lines = summary.read_text().splitlines()
    if len(lines) != 3 or lines[0] != '# response-assignment-v1; native geometry only; NOT a gap transfer':
        raise ValueError('Stale response assignment schema')
    dims = list(map(int, lines[1].split()))
    physical = list(map(float, lines[2].split()))
    if (len(dims) != 7 or min(dims) < 1 or dims[2] != max(dims[:2]) or dims[5] > dims[6]
            or len(physical) != 2 or not all(map(math.isfinite, physical)) or min(physical) <= 0):
        raise ValueError('Invalid response assignment metadata')
    maximum, nx = dims[2:4]
    if binary.stat().st_size != 16*nx+80*maximum:
        raise ValueError('Stale response assignment payload')
    data = binary.read_bytes()
    reals = struct.unpack_from('<'+'d'*(2*nx+8*maximum), data)
    indices = struct.unpack_from('<'+'i'*(4*maximum), data, 16*nx+64*maximum)
    if not all(map(math.isfinite, reals)):
        raise ValueError('Nonfinite response assignment')
    arrays = dict(xi0=reals[:nx], dx0=reals[nx:2*nx])
    for j, name in enumerate(('xi', 'dk', 'dxq', 'd2xq')):
        arrays[name] = reals[2*nx+2*j*maximum:2*nx+2*(j+1)*maximum]
    arrays['kindx'], arrays['bindx'] = indices[:2*maximum], indices[2*maximum:]
    for side, count in enumerate(dims[:2]):
        start = side*maximum
        for name in ('xi', 'dk', 'dxq', 'd2xq', 'kindx', 'bindx'):
            if any(arrays[name][start+count:start+maximum]):
                raise ValueError('Nonzero response assignment padding')
        if (any(not 1 <= i <= dims[4] for i in arrays['kindx'][start:start+count])
                or any(not dims[5] <= i <= dims[6] for i in arrays['bindx'][start:start+count])):
            raise ValueError('Invalid response assignment indices')
    counts, native = native_arrays(prepare)
    shape_matches = dims[:5] == counts[:5]
    differences = {}
    if shape_matches:
        for name in ('xi0', 'dx0', 'xi', 'dk'):
            pairs = list(zip(arrays[name], native[name]))
            differences[name] = dict(
                max_absolute_difference=max(abs(a-b) for a, b in pairs),
                entries_beyond_64eps_relative=sum(abs(a-b) > 64*sys.float_info.epsilon*max(abs(a), abs(b)) for a, b in pairs))
        for name in ('kindx', 'bindx'):
            differences[name] = dict(mismatches=sum(a != b for a, b in zip(arrays[name], native[name])))
    compatible = shape_matches and all(
        row.get('entries_beyond_64eps_relative', row.get('mismatches', 0)) == 0 for row in differences.values())
    return dict(dimensions=dims, native_counts=counts, shape_matches=shape_matches,
                mapping_compatible=compatible, differences=differences,
                qnorm=physical[0], volume=physical[1], tolerance='64eps elementwise relative; zeros exact; indices exact',
                gap_transfer_verified=False, physical_response_verified=False,
                sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                        (summary, binary, prepare/'native-init.meta', prepare/'native-init.bin')}, scope=__doc__)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('prepare_directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze(args.directory, args.prepare_directory), indent=2, allow_nan=False))
