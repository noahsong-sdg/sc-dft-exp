"""Independent readback of an enlarged fresh Ritz basis and full-image residuals."""
from array import array
import argparse
import json
import math
from pathlib import Path

from fetch_public_response_inputs import digest
from initial_basis_analysis import binary,relative_residual


def read_reduced(root,columns):
    reduced = binary(Path(root)/'reduced.bin',2*columns*columns+2*columns)
    square = columns*columns
    return (reduced[:square],reduced[square:square+columns],
        reduced[square+columns:square+2*columns],reduced[square+2*columns:])


def inspect(root):
    root = Path(root).absolute()
    proof = json.loads((root/'basis-enrichment-result.json').read_text())
    if proof['status'] != 'PASS' or proof['full_images_native_checked'] is not True:
        raise ValueError('Complete native-checked images required')
    for name,value in proof['full_output_sha256'].items():
        if digest(root/name) != value:raise ValueError('Changed certified basis output')
    meta = (root/'basis.meta').read_text().splitlines()
    if len(meta) != 5 or meta[0] != 'tc-basis-v1' :
        raise ValueError('Stale initial basis metadata')
    size,columns = map(int,meta[1].split())
    if size != 135880 or columns not in (32,48,64):raise ValueError('Invalid enlarged basis dimensions')
    block = size*columns
    values = binary(root/'basis.bin',2*block)
    q = [values[i*size:(i+1)*size] for i in range(columns)]
    aq = [values[block+i*size:block+(i+1)*size] for i in range(columns)]
    for data in q+aq:
        if any(data[66867:67940]):raise ValueError('Nonzero initial basis padding')
    h,wr,wi,vr = read_reduced(root,columns)
    gram_error = 0.;projection_error = 0.
    for j in range(columns):
        for i in range(columns):
            gram = math.fsum(a*b for a,b in zip(q[i],q[j]))
            gram_error = max(gram_error,abs(gram-int(i==j)))
            projected = math.fsum(a*b for a,b in zip(q[i],aq[j]))
            difference = abs(projected-h[i+j*columns])
            projection_error = max(projection_error,difference)
            if difference > 2e-12*max(1.,abs(projected)):
                raise ValueError('Initial basis projection mismatch')
    if gram_error > 1e-10:raise ValueError('Initial basis Gram matrix failed')
    lines = (root/'ritz.meta').read_text().splitlines()
    if len(lines) != columns+1:raise ValueError('Incomplete Ritz spectrum')
    modes = []
    for j,line in enumerate(lines[1:]):
        fields = list(map(float,line.split()))
        if fields[:3] != [j+1,wr[j],wi[j]]:raise ValueError('Ritz spectrum differs from binary')
        if wi[j] != 0:continue
        if len(fields) != 8 or not all(map(math.isfinite,fields)):
            raise ValueError('Invalid real Ritz mode')
        coefficients = vr[j*columns:(j+1)*columns]
        relative = relative_residual(q,aq,coefficients,wr[j])
        if abs(relative-fields[3]) > 5e-12:
            raise ValueError('Independent full-image Ritz residual mismatch')
        modes.append(dict(index=j+1,eigenvalue=wr[j],relative_residual=relative,native_channel=int(fields[4])))
    selected = list(map(int,(root/'selected.meta').read_text().splitlines()[0].split()))
    if len(selected) != 2 or selected[1] != columns or not 0 <= selected[0] <= columns:
        raise ValueError('Invalid selected initial mode')
    return dict(status='PASS',basis_sha256=digest(root/'basis.bin'),reduced_sha256=digest(root/'reduced.bin'),
        analysis_source_sha256=digest(Path(__file__)),gram_error=gram_error,projection_error=projection_error,
        real_modes=modes,selected_index=selected[0],basis_columns=columns,gap_converged=False,physical_response_verified=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    print(json.dumps(inspect(p.parse_args().root),indent=2))
