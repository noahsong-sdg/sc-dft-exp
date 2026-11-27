"""Read a reduced candidate; a separate full native residual is mandatory."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


def analyze(directory, prepare_directory):
    root, prepare = Path(directory), Path(prepare_directory)
    summary, binary = root/'reduced-result.txt', root/'reduced-gap.bin'
    lines = summary.read_text().splitlines()
    if len(lines) != 4 or lines[0] != '# reduced-nonlinear-v1; candidate; FULL native residual required':
        raise ValueError('Incomplete or stale reduced result')
    dims = list(map(int,lines[1].split()))
    if len(dims) != 5 or min(dims) < 1 or dims[2] != max(dims[:2]) or not 1 <= dims[4] <= 64:
        raise ValueError('Invalid reduced dimensions')
    controls = list(map(float,lines[2].split()))
    if len(controls) != 7 or not all(map(math.isfinite,controls)) or min(controls) < 0:
        raise ValueError('Invalid reduced controls')
    beta, amplitude, iterations, residual, orth, mode_error, rytoev = controls
    if beta <= 0 or amplitude <= 0 or not iterations.is_integer() or not 1 <= iterations <= 40 or residual > 1e-13 or orth > 1e-10 or not 13 < rytoev < 14:
        raise ValueError('Reduced numerical gate failed')
    fields = list(map(float,lines[3].split()))
    if len(fields) != 4 or not all(map(math.isfinite,fields)) or min(fields[:2]) <= .001 or min(fields[2:]) <= 0:
        raise ValueError('No declared positive nonzero reduced candidate')
    maximum, nx = dims[2:4]
    if binary.stat().st_size != 16*maximum:
        raise ValueError('Stale reduced gap payload')
    gap = struct.unpack('<'+'d'*(2*maximum),binary.read_bytes())
    if not all(map(math.isfinite,gap)):
        raise ValueError('Nonfinite reduced gap')
    metadata = prepare/'native-init.meta'
    meta = metadata.read_text().splitlines()
    if len(meta) != 4 or meta[0] != 'native-init-v1; arrays are native binary64/int32, Fortran order':
        raise ValueError('Stale reduced geometry metadata')
    counts = list(map(int,meta[1].split()))
    scalars = list(map(float,meta[2].split()))
    if len(counts) != 7 or counts[:4] != dims[:4] or len(scalars) != 7 or not all(map(math.isfinite,scalars)) or scalars[1] <= 0:
        raise ValueError('Incompatible reduced geometry')
    state = prepare/'native-init.bin'
    if state.stat().st_size != 16*nx+96*maximum:
        raise ValueError('Stale reduced geometry payload')
    data = state.read_bytes()
    x = struct.unpack_from('<'+'d'*(2*maximum),data,16*nx)
    dk = struct.unpack_from('<'+'d'*(2*maximum),data,16*nx+32*maximum)
    if not all(map(math.isfinite,(*x,*dk))):
        raise ValueError('Nonfinite reduced geometry')
    averages, minima = [], []
    for g,count in enumerate(dims[:2]):
        start = g*maximum
        if any(v != 0 for v in gap[start+count:start+maximum]):
            raise ValueError('Nonzero reduced gap padding')
        fermi = [start+i for i in range(count) if abs(x[start+i]) < scalars[1]]
        denominator = math.fsum(dk[i] for i in fermi)
        positive = [gap[i] for i in fermi if dk[i] > 0]
        if denominator <= 0 or not positive:
            raise ValueError('Invalid reduced Fermi support')
        averages.append(math.fsum(gap[i]*dk[i] for i in fermi)/denominator*1000*rytoev)
        minima.append(min(positive)*1000*rytoev)
    expected = [*averages,max(map(abs,gap)),min(minima)]
    if any(not math.isclose(a,b,rel_tol=2e-13,abs_tol=1e-18) for a,b in zip(fields,expected)):
        raise ValueError('Reduced gap summary/binary disagreement')
    return dict(dimensions=dims,beta=beta,initial_amplitude_mev=amplitude,iterations=int(iterations),
                coefficient_residual=residual,orthogonality_error=orth,mode_projection_error=mode_error,
                fermi_averages_mev=averages,min_positive_weight_fermi_gap_mev=min(minima),
                max_absolute_gap_ry=expected[2],rytoev=rytoev,full_native_residual_verified=False,
                sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (summary,binary,metadata,state)},
                scope=__doc__.strip())


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('prepare_directory',type=Path)
    args=parser.parse_args()
    print(json.dumps(analyze(args.directory,args.prepare_directory),indent=2,allow_nan=False))
