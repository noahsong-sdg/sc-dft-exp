"""Stage a48cubed response diagnostic with explicitly derived band data."""
import argparse
import json
from pathlib import Path
import shutil

from fetch_public_response_inputs import digest
from public_band_grid_analysis import analyze as check_bands
from stage_public_response import RESEARCH, stage as stage_original
from verify_band_serialization import verify as check_serialization


def stage(build, inputs, bands, band_manifest, destination,
          manifest_path=RESEARCH/'public_response_inputs.json', serialization_manifest=None):
    build,inputs,bands,root=[Path(p).absolute() for p in (build,inputs,bands,destination)]
    band_manifest=Path(band_manifest).absolute()
    built=json.loads((build/'build-result.json').read_text())
    if built.get('point_capacity',40000)<48**3:
        raise ValueError('Response build cannot store48cubed')
    if serialization_manifest is None:
        checked=check_bands(bands,band_manifest)
    else:
        serialization_manifest=Path(serialization_manifest).absolute()
        serialized=json.loads(serialization_manifest.read_text())
        if serialized['source_band_manifest']!=str(band_manifest):
            raise ValueError('Serialization belongs to a different parent band protocol')
        checked=check_serialization(bands,serialization_manifest)
    if not checked['shared_point_and_serialization_targets_met']:
        raise ValueError('Generated band-grid validation failed')
    derived=bands/'scratch/pwscf.a2Fsave'
    expected=checked['sha256'][str(derived)]
    if digest(derived)!=expected:
        raise ValueError('Generated bands changed after readback')
    derived_bytes=derived.stat().st_size
    # Original staging checks every public file before creating this destination.
    result=stage_original(build,inputs,root,manifest_path)
    catalog=json.loads(Path(manifest_path).read_text())['files']
    bundle=root/'inputs';bundle.mkdir()
    for name,item in catalog.items():
        source=derived if name=='pwscf.a2Fsave' else inputs/name
        target=bundle/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)
        result['files'].append(dict(path=str(target),bytes=derived_bytes if source==derived else item['bytes'],
                                   sha256=expected if source==derived else item['sha256']))
    template=(RESEARCH/'public_response_native.in.template').read_text()
    (root/'native.in').write_text(template.replace('@PUBLIC_INPUT_DIRECTORY@',str(bundle).replace("'","''")))
    for item in result['files']:
        if item['path']==str(root/'native.in'):
            item.update(bytes=(root/'native.in').stat().st_size,sha256=digest(root/'native.in'))
    result['files'].append(dict(path=str(derived),bytes=derived_bytes,sha256=expected))
    result['files'].append(dict(path=str(band_manifest),bytes=band_manifest.stat().st_size,
                               sha256=checked['sha256'][str(band_manifest)]))
    for path in (Path(__file__),RESEARCH/'public_band_grid_analysis.py',
                 RESEARCH/'public_band_pilot_analysis.py',RESEARCH/'stage_public_response.py'):
        result['files'].append(dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path)))
    if serialization_manifest is not None:
        for path in (serialization_manifest,bands/'results/serialize/receipt.json'):
            result['files'].append(dict(path=str(path),bytes=path.stat().st_size,
                                       sha256=checked['sha256'][str(path)]))
        path=RESEARCH/'verify_band_serialization.py'
        result['files'].append(dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path)))
    result.update(grid=[48]*3,response_cell_grid=8,guard_seconds=240,
                  derived_inputs={'pwscf.a2Fsave':dict(source=str(derived),sha256=expected,
                    original_public_sha256=catalog['pwscf.a2Fsave']['sha256'],
                    provenance='Generated fixed-density48cubed bands, not an author-hosted original')},
                  band_validation=checked,
                  scope=__doc__.strip()+' Imposed gap; unchanged density/phonons/cell grid. Not physical response accuracy.')
    (root/'run-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('build','inputs','bands','band_manifest','destination'):
        parser.add_argument(name,type=Path)
    parser.add_argument('--serialization-manifest',type=Path,help='Explicit separately verified QE serialization protocol')
    print(json.dumps(stage(**vars(parser.parse_args())),indent=2))
