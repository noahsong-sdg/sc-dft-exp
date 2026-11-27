"""Stage the actual897-point32cubed public dense-band replay, not refinement."""
import argparse
import json
import math
from pathlib import Path

from fetch_public_response_inputs import digest, validate
from stage_public_band_pilot import RESEARCH, numbers, render, stage as stage_pilot


def dense_reference(text):
    lines=text.splitlines()
    if len(lines)<5 or list(map(int,lines[0].split()))!=[26,897]:
        raise ValueError('Expected pinned26band/897point dense input')
    energy,k,weight=[numbers(line) for line in lines[1:4]]
    grid=list(map(int,lines[4].split()))
    if (len(energy)!=26*897 or len(k)!=3*897 or len(weight)!=897 or grid!=[32]*3
            or min(weight)<0 or not math.isclose(math.fsum(weight),2.,rel_tol=0,abs_tol=1e-12)):
        raise ValueError('Invalid dense layout, grid or weights')
    # read_a2fsave reads these arrays directly in internal Ry units.
    return [dict(k_tpiba=k[3*i:3*i+3],eigenvalues_ry=energy[26*i:26*i+26]) for i in range(897)]


def stage(executable,inputs,destination,manifest_path=RESEARCH/'public_response_inputs.json'):
    inputs=Path(inputs).absolute();root=Path(destination).absolute()
    manifest=json.loads(Path(manifest_path).read_text());name='pwscf.a2Fsave'
    item=manifest['files'][name];source=inputs/validate(name,item)
    if source.stat().st_size!=item['bytes'] or digest(source)!=item['sha256']:
        raise ValueError('Changed declared dense-band input')
    reference=dense_reference(source.read_text())
    pilot,_=render((inputs/'pwscf.save/data-file-schema.xml').read_text())
    marker='K_POINTS tpiba\n8\n'
    if pilot.count(marker)!=1:
        raise ValueError('Changed pilot point-card boundary')
    native=pilot.split(marker)[0]+'K_POINTS tpiba\n897\n'+'\n'.join(
        ' '.join(format(x,'.17g') for x in row['k_tpiba'])+' 1' for row in reference)+'\n'
    result=stage_pilot(executable,inputs,root,manifest_path)
    (root/'native.in').write_text(native)
    (root/'reference.json').write_text(json.dumps(reference,indent=2)+'\n')
    for entry in result['files']:
        path=Path(entry['path'])
        if path in (root/'native.in',root/'reference.json'):
            entry.update(bytes=path.stat().st_size,sha256=digest(path))
    # Never adopt a changed original after its catalog check and reference read.
    result['files'].append(dict(path=str(source.absolute()),bytes=item['bytes'],sha256=item['sha256']))
    path=Path(__file__)
    result['files'].append(dict(path=str(path.absolute()),bytes=path.stat().st_size,sha256=digest(path)))
    result.update(points=897,guard_seconds=600,
                  scope='Complete32cubed saved-density band reproduction at author897coordinates. No new density, grid refinement, phonon or gap solve.')
    (root/'run-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('executable','inputs','destination'):
        parser.add_argument(name,type=Path)
    print(json.dumps(stage(**vars(parser.parse_args())),indent=2))
