"""Verify48cubed band serialization and unchanged energies at shared points.

Shared-point agreement is not independent accuracy at new points or convergence
of a superconducting response. No energy-offset fit is permitted.
"""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

from fetch_public_response_inputs import digest
from stage_public_band_pilot import numbers
from public_band_pilot_analysis import verify_postrun_inputs


def read_dense(text, grid):
    lines=text.splitlines()
    bands,points=map(int,lines[0].split())
    if bands!=26 or points<1 or list(map(int,lines[4].split()))!=[grid]*3:
        raise ValueError('Changed generated dense-band layout or grid')
    energies,k,weights=[numbers(line) for line in lines[1:4]]
    if (len(energies)!=26*points or len(k)!=3*points or len(weights)!=points
            or min(weights)<0 or not math.isclose(math.fsum(weights),2.,abs_tol=1e-12,rel_tol=0)):
        raise ValueError('Invalid generated dense-band payload or weights')
    return [dict(k_tpiba=k[3*i:3*i+3],eigenvalues_ry=energies[26*i:26*i+26]) for i in range(points)]


def shared_comparison(reference, generated):
    def key(row):
        return tuple(round(x,10) for x in row['k_tpiba'])
    def indexed(rows):
        lookup={key(row):row for row in rows}
        if len(lookup)!=len(rows):
            raise ValueError('Duplicate shared-point coordinates')
        return lookup
    old,new=indexed(reference),indexed(generated)
    common=old.keys()&new.keys()
    if not common:
        raise ValueError('No unchanged shared reference points')
    return len(common),max(abs(a-b) for k in common for a,b in
                           zip(old[k]['eigenvalues_ry'],new[k]['eigenvalues_ry']))


def analyze(directory, manifest_path):
    root=Path(directory).absolute();manifest_path=Path(manifest_path)
    manifest=json.loads(manifest_path.read_text())
    if (manifest['cwd']!=str(root) or manifest['grid']!=[48]*3
            or manifest['acceptance_max_eigenvalue_difference_ry']!=1e-6
            or manifest['minimum_common_reference_points']!=100):
        raise ValueError('Changed declared48cubed band protocol')
    verify_postrun_inputs(manifest, root)
    receipt_path=root/'results/bands/receipt.json'
    receipt=json.loads(receipt_path.read_text())
    if (receipt.get('status')!='PASS' or receipt.get('error') is not None or receipt.get('exit')!=0
            or receipt['command']!=manifest['command'] or receipt['cwd']!=str(root)
            or receipt['continuous_deadline_s']!=1200):
        raise ValueError('Band-grid native guard did not pass declared protocol')
    dense=root/'scratch/pwscf.a2Fsave'
    rows=read_dense(dense.read_text(),48)
    output=root/'scratch/pwscf.save/data-file-schema.xml'
    states=ET.fromstring(output.read_text()).findall('output/band_structure/ks_energies')
    if len(states)!=len(rows):
        raise ValueError('XML and generated dense-band point counts differ')
    for row,state in zip(rows,states):
        k=numbers(state.findtext('k_point'));energy=numbers(state.findtext('eigenvalues'))
        if (len(k)!=3 or len(energy)!=26 or max(abs(a-b) for a,b in zip(k,row['k_tpiba']))>1e-12
                or max(abs(2*a-b) for a,b in zip(energy,row['eigenvalues_ry']))>1e-12):
            raise ValueError('XML and Ry dense-band serialization differ')
    count,error=shared_comparison(json.loads((root/'reference.json').read_text()),rows)
    passed=count>=100 and error<=1e-6
    return dict(grid=[48]*3,generated_irreducible_points=len(rows),
                shared_reference_points=count,max_shared_eigenvalue_difference_ry=error,
                minimum_common_reference_points=100,acceptance_max_eigenvalue_difference_ry=1e-6,
                shared_point_and_serialization_targets_met=passed,energy_offset_fitted=False,
                new_points_independently_validated=False,original_inputs_unchanged=True,
                terminal_receipt=receipt,sha256={str(p):digest(p) for p in
                    (manifest_path,receipt_path,dense,output,root/'reference.json')},scope=__doc__.strip())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path);parser.add_argument('manifest_path',type=Path)
    print(json.dumps(analyze(**vars(parser.parse_args())),indent=2,allow_nan=False))
