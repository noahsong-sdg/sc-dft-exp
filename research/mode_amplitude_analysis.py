"""Validate full residual readback along a saved mode; no solved-gap inference."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

AMPLITUDES = [.025, .05, .1, .15, .2, .3, .5]


def analyze(directory):
    root = Path(directory)
    summary, binary = root/'mode-amplitudes.txt', root/'mode-amplitudes.bin'
    lines = summary.read_text().splitlines()
    if len(lines) != 10 or lines[0] != '# mode-amplitudes-v1; projected candidates; NOT solved gaps':
        raise ValueError('Incomplete or stale amplitude summary')
    dims = list(map(int, lines[1].split()))
    if len(dims) != 4 or min(dims) < 1 or dims[2] != max(dims[:2]) or dims[3] != 8:
        raise ValueError('Invalid amplitude dimensions')
    control = list(map(float, lines[2].split()))
    if len(control) != 6 or not all(map(math.isfinite, control)) or min(control) < 0:
        raise ValueError('Invalid amplitude controls')
    beta, eigenvalue, error, bound, relative, cpu = control
    if beta <= 0 or eigenvalue <= 1 or error > bound or relative > 1e-9:
        raise ValueError('Fresh mode comparison failed')
    maximum = dims[2]
    if binary.stat().st_size != 144*maximum:
        raise ValueError('Stale amplitude binary size')
    data = struct.unpack('<'+'d'*(18*maximum), binary.read_bytes())
    if not all(map(math.isfinite, data)):
        raise ValueError('Nonfinite amplitude payload')
    for matrix in range(9):
        for g, count in enumerate(dims[:2]):
            start = (2*matrix+g)*maximum
            if any(x != 0 for x in data[start+count:start+maximum]):
                raise ValueError('Nonzero amplitude padding')
    n = 2*maximum
    mode, linear = data[:n], data[n:2*n]
    norm2 = math.fsum(x*x for x in mode)
    if abs(norm2-1) > 2e-10:
        raise ValueError('Changed mode normalization')
    expected_relative = math.sqrt(math.fsum((a-eigenvalue*v)**2 for a,v in zip(linear,mode)))/max(
        math.sqrt(math.fsum(x*x for x in linear)), eigenvalue*math.sqrt(norm2))
    expected_bound = 2e-13+2e-12*max(map(abs, linear))
    if not math.isclose(bound, expected_bound, rel_tol=2e-13, abs_tol=1e-18) or not math.isclose(
            relative, expected_relative, rel_tol=2e-8, abs_tol=1e-15):
        raise ValueError('Changed fresh-mode readback')
    rows = []
    for k, amplitude in enumerate(AMPLITUDES):
        fields = list(map(float, lines[k+3].split()))
        if len(fields) != 7 or not all(map(math.isfinite, fields)) or fields[0] != amplitude or fields[1] <= 0:
            raise ValueError('Invalid amplitude record')
        scale = fields[1]
        image = data[(k+2)*n:(k+3)*n]
        residual = [a-scale*v for a,v in zip(image, mode)]
        expected = (math.fsum(v*r for v,r in zip(mode,residual))/norm2,
                    max(map(abs, residual)), math.sqrt(math.fsum(r*r for r in residual)/sum(dims[:2])))
        if any(not math.isclose(a,b,rel_tol=2e-11,abs_tol=1e-17) for a,b in zip(fields[2:5],expected)):
            raise ValueError('Amplitude residual summary disagrees with binary')
        rows.append(dict(mean_gap_amplitude_mev=amplitude, mode_scale_ry=scale,
                         projected_residual_ry=expected[0], max_absolute_residual_ry=expected[1],
                         rms_residual_ry=expected[2], fermi_residuals_ry=fields[5:]))
    brackets = [[a['mean_gap_amplitude_mev'], b['mean_gap_amplitude_mev']] for a,b in zip(rows,rows[1:])
                if a['projected_residual_ry']*b['projected_residual_ry'] < 0]
    return dict(dimensions=dims,beta=beta,eigenvalue=eigenvalue,fresh_relative_residual=relative,
                fresh_action_max_error=error,kernel_cpu_s=cpu,rows=rows,
                projected_sign_change_intervals_mev=brackets,
                sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (summary,binary)},
                scope=__doc__.strip())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    print(json.dumps(analyze(parser.parse_args().directory),indent=2,allow_nan=False))
