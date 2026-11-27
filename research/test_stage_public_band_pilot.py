import json
from pathlib import Path
import tempfile
import unittest

from fetch_public_response_inputs import PREFIX, digest
from stage_public_band_pilot import NAMES, render, stage


def fixture():
    points = ''.join('<k_point>0 0 '+str(i/16)+'</k_point>' for i in range(8))
    states = ''.join('<ks_energies><k_point>0 0 '+str(i/16)+'</k_point><eigenvalues>'+
                     ' '.join(str(j/10) for j in range(26))+'</eigenvalues></ks_energies>' for i in range(8))
    return ('<root><input><atomic_structure nat="1" alat="5.4"><cell>'+
            ''.join('<'+name+'>'+vector+'</'+name+'>' for name,vector in
                    zip(('a1','a2','a3'),('-3 3 3','3 -3 3','3 3 -3')))+
            '</cell><atomic_positions><atom>0 0 0</atom></atomic_positions></atomic_structure>'
            '<atomic_species><species><pseudo_file>'+NAMES[-1]+'</pseudo_file></species></atomic_species>'
            '<bands><nbnd>26</nbnd></bands><dft><functional>PBE</functional></dft>'
            '<spin><lsda>false</lsda><noncolin>false</noncolin><spinorbit>false</spinorbit></spin>'
            '<basis><ecutwfc>20</ecutwfc><ecutrho>160</ecutrho></basis>'
            '<k_points_IBZ>'+points+'</k_points_IBZ></input><output><basis_set>'
            '<fft_grid nr1="32" nr2="32" nr3="32"/><fft_smooth nr1="24" nr2="24" nr3="24"/>'
            '</basis_set><band_structure>'+states+'</band_structure></output></root>')


class StageBandPilotTest(unittest.TestCase):
    def test_hartree_to_ry_and_point_units_are_explicit_without_energy_fit(self):
        native, reference = render(fixture())
        self.assertIn('ecutwfc=40, ecutrho=320', native)
        self.assertIn('celldm(1)=5.4', native)
        self.assertIn('K_POINTS tpiba\n8\n', native)
        self.assertEqual(reference[3]['k_tpiba'], [0.,0.,3/16])
        self.assertEqual(reference[3]['eigenvalues_ry'][25], 5.)
        with self.assertRaisesRegex(ValueError, 'cutoffs'):
            render(fixture().replace('<ecutwfc>20', '<ecutwfc>40'))
        with self.assertRaisesRegex(ValueError, 'Nonfinite'):
            render(fixture().replace('<eigenvalues>0.0', '<eigenvalues>nan', 1))

    def test_stage_preserves_public_files_and_rejects_stale_input_before_mkdir(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve(); inputs=root/'public'; save=inputs/'pwscf.save'; save.mkdir(parents=True)
            files={}
            for name in NAMES:
                p=save/name; p.write_text(fixture() if name.endswith('.xml') else 'fixture')
                key='pwscf.save/'+name
                files[key]=dict(url=PREFIX+key,bytes=p.stat().st_size,sha256=digest(p))
            manifest=root/'manifest.json'; manifest.write_text(json.dumps(dict(files=files)))
            exe=root/'source.x';exe.write_bytes(b'checked executable')
            result=stage(exe,inputs,root/'run',manifest)
            self.assertEqual(result['points'],8)
            self.assertEqual(result['command'][0],str(root/'run/pw.x'))
            for name in NAMES:
                self.assertEqual(digest(save/name),files['pwscf.save/'+name]['sha256'])
                self.assertEqual((root/'run/scratch/pwscf.save'/name).read_bytes(),(save/name).read_bytes())
            (save/'charge-density.dat').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'Changed declared band input'):
                stage(exe,inputs,root/'stale',manifest)
            self.assertFalse((root/'stale').exists())


if __name__=='__main__':
    unittest.main()
