"""Stage48cubed fixed-density XML bands; serialize a2Fsave in a separate action."""
import argparse
import json
from pathlib import Path

from fetch_public_response_inputs import digest, validate
from stage_public_band_pilot import RESEARCH, stage as stage_pilot
from stage_public_dense_bands import dense_reference


def stage(build, inputs, destination, manifest_path=RESEARCH/'public_response_inputs.json'):
    build,inputs,root=[Path(p).absolute() for p in (build,inputs,destination)]
    built=json.loads((build/'build-result.json').read_text())
    if built.get('point_capacity',40000)<48**3:
        raise ValueError('Consistent response build must support the full48cubed grid')
    catalog=json.loads(Path(manifest_path).read_text())
    name='pwscf.a2Fsave';item=catalog['files'][name];original=inputs/validate(name,item)
    if original.stat().st_size!=item['bytes'] or digest(original)!=item['sha256']:
        raise ValueError('Changed original dense-band reference')
    reference=dense_reference(original.read_text())
    result=stage_pilot(build/'qe/bin/pw.x',inputs,root,manifest_path)
    native=(root/'native.in').read_text()
    marker='K_POINTS tpiba\n8\n'
    if native.count(marker)!=1 or native.count("occupations='fixed',")!=1:
        raise ValueError('Changed qualified band input boundaries')
    native=native.split(marker)[0]+'K_POINTS automatic\n48 48 48 0 0 0\n'
    (root/'native.in').write_text(native)
    (root/'reference.json').write_text(json.dumps(reference,indent=2)+'\n')
    for entry in result['files']:
        path=Path(entry['path'])
        if path in (root/'native.in',root/'reference.json'):
            entry.update(bytes=path.stat().st_size,sha256=digest(path))
    # Preserve catalog identity even if the original changes after its check.
    result['files'].append(dict(path=str(original),bytes=item['bytes'],sha256=item['sha256']))
    for path in (build/'build-result.json',Path(__file__),RESEARCH/'stage_public_dense_bands.py'):
        result['files'].append(dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path)))
    result.pop('points')
    result.update(grid=[48]*3,guard_seconds=1200,minimum_common_reference_points=100,
                  scope=__doc__.strip()+' Derivative-grid experiment; physical response qualification remains separate.')
    (root/'run-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('build','inputs','destination'):
        parser.add_argument(name,type=Path)
    print(json.dumps(stage(**vars(parser.parse_args())),indent=2))
