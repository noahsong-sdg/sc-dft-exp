"""Read opt-in native moment caches; no gap transfer or physical qualification."""
import array
import math
from pathlib import Path
import sys

HEADER = '# response-cell-moments-v1; fixed geometry diagnostic; NOT a physical prediction'
FIELDS = ('dos', 'first', 'second', 'curvature')


def read_cache(directory, phase):
    if phase not in ('raw', 'averaged'):
        raise ValueError('Unknown moment cache phase')
    root = Path(directory)
    summary, binary = [root / f'cell-moments-{phase}.{suffix}' for suffix in ('txt', 'bin')]
    lines = summary.read_text().splitlines()
    if len(lines) != 4 or lines[0] != HEADER or lines[1] != phase:
        raise ValueError('Stale moment cache schema or phase')
    dims = list(map(int, lines[2].split()))
    physical = list(map(float, lines[3].split()))
    if (len(dims) != 5 or min(dims) < 1 or dims[1] > dims[2] or dims[4] != 2
            or len(physical) != 5 or not all(map(math.isfinite, physical))
            or min(physical[:2]) <= 0 or not any(physical[2:])):
        raise ValueError('Invalid moment cache metadata')
    if sys.byteorder != 'little' or array.array('d').itemsize != 8:
        raise ValueError('Moment cache requires little-endian binary64')
    nx, first, last, cells, sides = dims
    length = nx * (last-first+1) * cells * sides
    if binary.stat().st_size != 8*(2*nx+4*length):
        raise ValueError('Stale moment cache payload')
    arrays = {}
    with binary.open('rb') as source:
        for name, count in [('xi0', nx), ('dx0', nx)] + [(f, length) for f in FIELDS]:
            values = array.array('d')
            values.fromfile(source, count)
            if not all(map(math.isfinite, values)):
                raise ValueError('Nonfinite moment cache payload')
            arrays[name] = values
    return dims, physical, arrays


def read_pair(directory):
    raw_dims, raw_physical, raw = read_cache(directory, 'raw')
    dims, physical, averaged = read_cache(directory, 'averaged')
    if (dims != raw_dims or physical != raw_physical or raw['xi0'] != averaged['xi0']
            or raw['dx0'] != averaged['dx0']):
        raise ValueError('Incompatible moment cache phases')
    return dims, physical, raw, averaged
