"""Stage eight Nb band points from public density; no self-consistent solve.

QE's pinned pw_init_qexsd_input writes cutoffs divided by e2=2. Schema energies
are Hartree; PW input cutoffs are Ry. No energy shift is fitted on readback.
"""
import argparse
import json
import math
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

from fetch_public_response_inputs import digest, validate

RESEARCH = Path(__file__).resolve().parent
NAMES = ('data-file-schema.xml', 'charge-density.dat', 'paw.txt',
         'Nb.pbe-spn-kjpaw_psl.0.3.0.UPF')


def numbers(text):
    values = list(map(float, text.split()))
    if not values or not all(map(math.isfinite, values)):
        raise ValueError('Nonfinite or empty band metadata')
    return values


def render(xml):
    root = ET.fromstring(xml)
    inp, out = root.find('input'), root.find('output')
    structure = inp.find('atomic_structure')
    if (structure.get('nat') != '1' or inp.findtext('atomic_species/species/pseudo_file') != NAMES[-1]
            or inp.findtext('bands/nbnd') != '26' or inp.findtext('dft/functional') != 'PBE'
            or inp.findtext('spin/lsda') != 'false' or inp.findtext('spin/noncolin') != 'false'
            or inp.findtext('spin/spinorbit') != 'false'):
        raise ValueError('Pilot supports the pinned nonmagnetic one-atom Nb context only')
    points = inp.findall('k_points_IBZ/k_point')[:8]
    states = out.findall('band_structure/ks_energies')[:8]
    if len(points) != 8 or len(states) != 8:
        raise ValueError('Eight matching source points required')
    reference = []
    for point, state in zip(points, states):
        k = numbers(point.text); output_k = numbers(state.findtext('k_point'))
        energy = numbers(state.findtext('eigenvalues'))
        if len(k) != 3 or len(output_k) != 3 or len(energy) != 26 or max(abs(a-b) for a,b in zip(k,output_k)) > 1e-12:
            raise ValueError('Source input/output band-point mismatch')
        reference.append(dict(k_tpiba=k, eigenvalues_ry=[2*x for x in energy]))
    cutoff = 2*float(inp.findtext('basis/ecutwfc'))
    density_cutoff = 2*float(inp.findtext('basis/ecutrho'))
    if cutoff != 40 or density_cutoff != 320:
        raise ValueError('Unexpected pinned Nb cutoffs')
    cell = [numbers(structure.findtext('cell/'+name)) for name in ('a1','a2','a3')]
    if any(len(vector) != 3 for vector in cell):
        raise ValueError('Invalid cell')
    atom = numbers(structure.findtext('atomic_positions/atom'))
    if atom != [0.,0.,0.]:
        raise ValueError('Unexpected pinned atom position')
    grid = out.find('basis_set/fft_grid').attrib
    smooth = out.find('basis_set/fft_smooth').attrib
    if [int(grid['nr'+str(i)]) for i in (1,2,3)] != [32]*3 or [int(smooth['nr'+str(i)]) for i in (1,2,3)] != [24]*3:
        raise ValueError('Unexpected pinned FFT grids')
    header = """&control
 calculation='bands', prefix='pwscf', outdir='./scratch/',
 pseudo_dir='./scratch/pwscf.save/', disk_io='nowf', verbosity='high'
/
&system
 ibrav=0, nat=1, ntyp=1, nbnd=26, occupations='fixed',
 ecutwfc=40, ecutrho=320, nr1=32, nr2=32, nr3=32,
 nr1s=24, nr2s=24, nr3s=24
/
&electrons
 startingpot='file', startingwfc='atomic+random',
 diago_thr_init=1e-10, diago_full_acc=.true., electron_maxstep=100
/
ATOMIC_SPECIES
 Nb 92.90638 Nb.pbe-spn-kjpaw_psl.0.3.0.UPF
ATOMIC_POSITIONS bohr
 Nb 0 0 0
CELL_PARAMETERS alat
"""
    alat = float(structure.get('alat'))
    if not math.isfinite(alat) or alat <= 0:
        raise ValueError('Invalid lattice scale')
    text = header + '\n'.join(' '.join(format(x/alat,'.17g') for x in vector) for vector in cell)
    # Explicit alat preserves the author's tpiba convention for noncubic primitives.
    text = text.replace('ibrav=0,', 'ibrav=0, celldm(1)='+structure.get('alat')+',')
    text += '\nK_POINTS tpiba\n8\n'+'\n'.join(' '.join(format(x,'.17g') for x in row['k_tpiba'])+' 1' for row in reference)+'\n'
    return text, reference


def stage(executable, inputs, destination, manifest_path=RESEARCH/'public_response_inputs.json'):
    exe, inputs, root = [Path(p).absolute() for p in (executable, inputs, destination)]
    manifest = json.loads(Path(manifest_path).read_text())
    files = []
    for name in NAMES:
        relative = 'pwscf.save/'+name
        item = manifest['files'][relative]
        path = inputs/validate(relative, item)
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('Changed declared band input: '+name)
        files.append(dict(path=str(path), bytes=item['bytes'], sha256=item['sha256']))
    native, reference = render((inputs/'pwscf.save/data-file-schema.xml').read_text())
    executable_hash = digest(exe)
    root.mkdir(parents=True)
    save = root/'scratch/pwscf.save'; save.mkdir(parents=True)
    for name in NAMES:
        shutil.copy2(inputs/'pwscf.save'/name, save/name)
    target = root/'pw.x'; shutil.copy2(exe, target)
    (root/'native.in').write_text(native)
    (root/'reference.json').write_text(json.dumps(reference, indent=2)+'\n')
    for path in (target, root/'native.in', root/'reference.json', Path(manifest_path), Path(__file__)):
        files.append(dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path)))
    result = dict(files=files, command=[str(target), '-in', str(root/'native.in')], cwd=str(root),
                  environment=dict(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1'),
                  source_executable_sha256=executable_hash, points=8,
                  acceptance_max_eigenvalue_difference_ry=1e-6,
                  guard_seconds=180, scope='Eight-point fixed-density replay and cost pilot; not SCF, full band refinement, phonon preparation or response qualification')
    (root/'run-manifest.json').write_text(json.dumps(result, indent=2)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('executable','inputs','destination'):
        parser.add_argument(name, type=Path)
    print(json.dumps(stage(**vars(parser.parse_args())), indent=2))
