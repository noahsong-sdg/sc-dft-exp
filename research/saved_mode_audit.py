"""Audit a saved native Ritz candidate against its exact initialization layout.

This is serialized-data qualification, not a fresh operator application.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


def audit(mode_directory, prepare_directory):
    mode, prepare = Path(mode_directory), Path(prepare_directory)
    paths = [mode/'selected.meta', mode/'selected.bin', mode/'basis.meta',
             prepare/'native-init.meta', prepare/'native-init.bin']
    selected = paths[0].read_text().splitlines()
    if len(selected) != 2:
        raise ValueError('Unsupported selected candidate metadata')
    index, columns = map(int, selected[0].split())
    eigenvalue, reported_error = map(float, selected[1].split())
    if not 1 <= index <= columns or eigenvalue <= 0 or reported_error < 0 or not all(map(math.isfinite, (eigenvalue, reported_error))):
        raise ValueError('Invalid selected eigenpair')
    init = paths[3].read_text().splitlines()
    if len(init) != 4 or init[0] != 'native-init-v1; arrays are native binary64/int32, Fortran order':
        raise ValueError('Unsupported initialization schema')
    counts = list(map(int, init[1].split()))
    if len(counts) != 7 or min(counts) < 1 or counts[2] != max(counts[:2]):
        raise ValueError('Invalid initialization dimensions')
    left, right, maximum, nx = counts[:4]
    scalars = list(map(float, init[2].split()))
    if len(scalars) != 7 or not all(map(math.isfinite, scalars)) or scalars[1] <= 0 or init[3].strip() not in ('T', 'F'):
        raise ValueError('Invalid initialization scalars')
    basis = paths[2].read_text().splitlines()
    if len(basis) != 5 or basis[0] != 'tc-basis-v1':
        raise ValueError('Unsupported Ritz basis schema')
    n, basis_columns = map(int, basis[1].split())
    beta = float(basis[2])
    context = basis[3]
    config = list(map(int, basis[4].split()))
    if (n != 2*maximum or basis_columns != columns or not math.isfinite(beta) or beta <= 0
            or len(context) != 64 or any(c not in '0123456789abcdef' for c in context)
            or len(config) != 6 or config[0] != nx or config[-2:] != counts[:2]):
        raise ValueError('Stale candidate basis context')
    if paths[1].stat().st_size != 16*n or paths[4].stat().st_size != 16*nx+96*maximum:
        raise ValueError('Stale candidate or initialization binary size')
    values = struct.unpack('<'+'d'*(2*n), paths[1].read_bytes())
    vector, residual = values[:n], values[n:]
    state = paths[4].read_bytes()
    xi = struct.unpack_from('<'+'d'*n, state, 16*nx)
    dk = struct.unpack_from('<'+'d'*n, state, 16*nx+16*n)
    if not all(map(math.isfinite, (*values, *xi, *dk))):
        raise ValueError('Nonfinite candidate data')
    norm = math.sqrt(math.fsum(x*x for x in vector))
    residual_norm = math.sqrt(math.fsum(x*x for x in residual))
    image_norm = math.sqrt(math.fsum((eigenvalue*x+r)**2 for x,r in zip(vector, residual)))
    if norm == 0:
        raise ValueError('Zero candidate vector')
    relative = residual_norm/max(image_norm, eigenvalue*norm)
    if not math.isclose(relative, reported_error, rel_tol=2e-8, abs_tol=1e-15):
        raise ValueError('Saved eigenpair residual disagrees with metadata')
    sides = []
    for g, count in enumerate((left, right)):
        start = g*maximum
        if any(x != 0 for block in (vector, residual, xi, dk) for x in block[start+count:start+maximum]):
            raise ValueError('Nonzero candidate/state padding')
        fermi = [start+i for i in range(count) if abs(xi[start+i]) < scalars[1]]
        denominator = math.fsum(dk[i] for i in fermi)
        if denominator <= 0:
            raise ValueError('Invalid Fermi normalization')
        average = math.fsum(vector[i]*dk[i] for i in fermi)/denominator
        sides.append(dict(side=g+1, fermi_average=average, fermi_count=len(fermi)))
    return dict(eigenvalue=eigenvalue, relative_saved_residual=relative, vector_norm=norm,
                beta=beta, context=context, configuration=config, sides=sides,
                same_sign_fermi_averages=sides[0]['fermi_average']*sides[1]['fermi_average']>0,
                sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                scope=__doc__.strip())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode_directory', type=Path)
    parser.add_argument('prepare_directory', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.mode_directory, args.prepare_directory), indent=2, allow_nan=False))
