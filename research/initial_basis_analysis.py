"""Independent binary readback of the initial fresh Ritz basis and residuals."""
from array import array
import argparse
import json
import math
from pathlib import Path

from fetch_public_response_inputs import digest


def binary(path,count):
    values = array('d')
    if values.itemsize != 8 or path.stat().st_size != count*8:
        raise ValueError('Stale initial basis binary shape')
    with path.open('rb') as stream:values.fromfile(stream,count)
    if not all(map(math.isfinite,values)):raise ValueError('Nonfinite initial basis payload')
    return values


def relative_residual(q,aq,coefficients,eigenvalue):
    norms = [[],[],[]]
    for row in range(len(q[0])):
        vector = math.fsum(column[row]*coefficient for column,coefficient in zip(q,coefficients))
        image = math.fsum(column[row]*coefficient for column,coefficient in zip(aq,coefficients))
        norms[0].append(vector*vector);norms[1].append(image*image)
        norms[2].append((image-eigenvalue*vector)**2)
    vector,image,residual = (math.sqrt(math.fsum(values)) for values in norms)
    return residual/max(image,abs(eigenvalue)*vector,1e-300)


def inspect(root):
    root = Path(root).absolute()
    proof = json.loads((root/'basis-production-result.json').read_text())
    if proof['status'] != 'PASS' or proof['full_images_native_checked'] is not True:
        raise ValueError('Complete native-checked images required')
    for name,value in proof['full_output_sha256'].items():
        if digest(root/name) != value:raise ValueError('Changed certified basis output')
    meta = (root/'basis.meta').read_text().splitlines()
    if len(meta) != 5 or meta[0] != 'tc-basis-v1' or list(map(int,meta[1].split())) != [135880,16]:
        raise ValueError('Stale initial basis metadata')
    size,columns = 135880,16;block = size*columns
    values = binary(root/'basis.bin',2*block)
    q = [values[i*size:(i+1)*size] for i in range(columns)]
    aq = [values[block+i*size:block+(i+1)*size] for i in range(columns)]
    for data in q+aq:
        if any(data[66867:67940]):raise ValueError('Nonzero initial basis padding')
    reduced = binary(root/'reduced.bin',2*columns*columns+2*columns)
    h = reduced[:256];wr = reduced[256:272];wi = reduced[272:288];vr = reduced[288:]
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
    if len(selected) != 2 or selected[1] != 16 or not 0 <= selected[0] <= 16:
        raise ValueError('Invalid selected initial mode')
    return dict(status='PASS',basis_sha256=digest(root/'basis.bin'),reduced_sha256=digest(root/'reduced.bin'),
        analysis_source_sha256=digest(Path(__file__)),gram_error=gram_error,projection_error=projection_error,
        real_modes=modes,selected_index=selected[0],gap_converged=False,physical_response_verified=False)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path)
    print(json.dumps(inspect(p.parse_args().root),indent=2))
