"""Stage owning QE XML-to-a2F serialization after a completed fixed-density run."""
import argparse
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from fetch_public_response_inputs import digest
from public_band_pilot_analysis import verify_postrun_inputs
from stage_public_band_pilot import NAMES


def stage(executable, bands, band_manifest, destination,grid=48):
    if grid not in (48,64):
        raise ValueError('Only declared48/64cubed serialization protocols are supported')
    exe,bands,band_manifest,root=[Path(p).absolute() for p in (executable,bands,band_manifest,destination)]
    upstream=json.loads(band_manifest.read_text())
    if upstream['cwd']!=str(bands) or upstream['grid']!=[grid]*3:
        raise ValueError(f'Expected declared{grid}cubed band parent')
    verify_postrun_inputs(upstream,bands)
    receipt_path=bands/'results/bands/receipt.json';receipt=json.loads(receipt_path.read_text())
    if (receipt.get('status')!='PASS' or receipt.get('error') is not None or receipt.get('exit')!=0
            or receipt['command']!=upstream['command'] or receipt['cwd']!=str(bands)
            or receipt['continuous_deadline_s']!=(1200 if grid==48 else 1800)):
        raise ValueError('Parent band execution did not pass')
    xml=bands/'scratch/pwscf.save/data-file-schema.xml'
    points=len(ET.fromstring(xml.read_text()).findall('output/band_structure/ks_energies'))
    if points<100:
        raise ValueError('Incomplete parent band XML')
    sources=[bands/'scratch/pwscf.save'/name for name in NAMES]+[bands/'reference.json']
    identities={p:dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sources}
    executable_hash=digest(exe)
    root.mkdir(parents=True);save=root/'scratch/pwscf.save';save.mkdir(parents=True)
    files=[]
    for source in sources:
        target=root/'reference.json' if source.name=='reference.json' else save/source.name
        shutil.copy2(source,target)
        for path in (source,target):
            files.append(dict(path=str(path),**identities[source]))
    target=root/'a2f-serialize.x';shutil.copy2(exe,target)
    (root/'native.in').write_text("&control prefix='pwscf', outdir='./scratch/', calculation='scdft', restart_mode='from_scratch' /\n")
    for path in (target,root/'native.in',band_manifest,receipt_path,Path(__file__)):
        files.append(dict(path=str(path),bytes=path.stat().st_size,sha256=digest(path)))
    if digest(target)!=executable_hash:
        raise ValueError('Serialization executable changed during staging')
    result=dict(command=[str(target),'-in',str(root/'native.in')],cwd=str(root),files=files,
                grid=[grid]*3,expected_points=points,minimum_common_reference_points=100,
                acceptance_max_eigenvalue_difference_ry=1e-6,guard_seconds=120,
                source_band_directory=str(bands),source_band_manifest=str(band_manifest),
                original_band_receipt=receipt,source_xml_sha256=identities[xml]['sha256'],
                scope=__doc__.strip()+' New serialization action, not a repeat diagonalization or a passing original a2Fsave output protocol.')
    (root/'run-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('executable','bands','band_manifest','destination'):
        parser.add_argument(name,type=Path)
    parser.add_argument('--grid',type=int,choices=(48,64),default=48)
    print(json.dumps(stage(**vars(parser.parse_args())),indent=2))
