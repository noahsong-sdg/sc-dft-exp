"""Verify a separate owning-QE serialization action against all parent XML data."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from fetch_public_response_inputs import digest
from public_band_grid_analysis import read_dense, shared_comparison
from public_band_pilot_analysis import verify_postrun_inputs
from stage_public_band_pilot import numbers


def verify(directory, manifest_path):
    root=Path(directory).absolute();manifest_path=Path(manifest_path).absolute()
    manifest=json.loads(manifest_path.read_text())
    if (manifest['cwd']!=str(root) or manifest['grid']!=[48]*3
            or manifest['minimum_common_reference_points']!=100
            or manifest['acceptance_max_eigenvalue_difference_ry']!=1e-6):
        raise ValueError('Changed declared serialization protocol')
    verify_postrun_inputs(manifest,root)
    parent_manifest=Path(manifest['source_band_manifest'])
    parent=json.loads(parent_manifest.read_text())
    parent_receipt=Path(manifest['source_band_directory'])/'results/bands/receipt.json'
    original=json.loads(parent_receipt.read_text())
    if (original!=manifest['original_band_receipt'] or original.get('status')!='PASS'
            or original.get('error') is not None or original.get('exit')!=0
            or original['command']!=parent['command'] or original['cwd']!=parent['cwd']
            or original['continuous_deadline_s']!=1200):
        raise ValueError('Changed parent native band provenance')
    receipt_path=root/'results/serialize/receipt.json';receipt=json.loads(receipt_path.read_text())
    if (receipt.get('status')!='PASS' or receipt.get('error') is not None or receipt.get('exit')!=0
            or receipt['command']!=manifest['command'] or receipt['cwd']!=str(root)
            or receipt['continuous_deadline_s']!=120):
        raise ValueError('Serialization execution did not pass')
    output=root/'scratch/pwscf.a2Fsave';rows=read_dense(output.read_text(),48)
    xml=root/'scratch/pwscf.save/data-file-schema.xml'
    if digest(xml)!=manifest['source_xml_sha256']:
        raise ValueError('Changed parent XML during serialization')
    states=ET.fromstring(xml.read_text()).findall('output/band_structure/ks_energies')
    lines=output.read_text().splitlines();weights=numbers(lines[3])
    if len(states)!=len(rows) or len(rows)!=manifest['expected_points']:
        raise ValueError('Incomplete serialized point count')
    for row,weight,state in zip(rows,weights,states):
        k=numbers(state.findtext('k_point'));energy=numbers(state.findtext('eigenvalues'))
        if (len(k)!=3 or len(energy)!=26 or max(abs(a-b) for a,b in zip(k,row['k_tpiba']))>1e-12
                or max(abs(2*a-b) for a,b in zip(energy,row['eigenvalues_ry']))>1e-12
                or abs(float(state.find('k_point').get('weight'))-weight)>1e-12):
            raise ValueError('Owning writer does not preserve parent XML bands or weights')
    common,error=shared_comparison(json.loads((root/'reference.json').read_text()),rows)
    return dict(grid=[48]*3,generated_irreducible_points=len(rows),shared_reference_points=common,
        max_shared_eigenvalue_difference_ry=error,minimum_common_reference_points=100,
        acceptance_max_eigenvalue_difference_ry=1e-6,
        shared_point_and_serialization_targets_met=common>=100 and error<=1e-6,
        all_parent_coordinates_energies_weights_preserved=True,energy_offset_fitted=False,
        terminal_receipt=receipt,original_band_receipt=manifest['original_band_receipt'],
        original_output_protocol_pass=False,separate_native_serialization=True,
        sha256={str(p):digest(p) for p in (manifest_path,receipt_path,output,xml,root/'reference.json',parent_manifest,parent_receipt)},
        scope=__doc__.strip()+' Not independent new-point accuracy, grid convergence or physical response validation.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path);parser.add_argument('manifest_path',type=Path)
    print(json.dumps(verify(**vars(parser.parse_args())),indent=2,allow_nan=False))
