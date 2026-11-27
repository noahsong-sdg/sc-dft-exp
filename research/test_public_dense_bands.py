import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from public_band_pilot_analysis import compare
from stage_public_dense_bands import dense_reference, stage
from stage_public_band_pilot import stage as stage_pilot, NAMES
from fetch_public_response_inputs import PREFIX, digest
from test_stage_public_band_pilot import fixture


class DenseBandReplayTest(unittest.TestCase):
    def test_fortran_layout_and_ry_units_are_not_reinterpreted(self):
        energy=[str(i/1000) for i in range(26*897)]
        k=[str(i/10000) for i in range(3*897)]
        weights=['0']*896+['2']
        text='\n'.join(('26 897',' '.join(energy),' '.join(k),' '.join(weights),'32 32 32','ignored native trailing symmetry metadata'))
        rows=dense_reference(text)
        self.assertEqual(len(rows),897)
        self.assertEqual(rows[1]['k_tpiba'],[.0003,.0004,.0005])
        self.assertEqual(rows[1]['eigenvalues_ry'][:2],[.026,.027])
        with self.assertRaisesRegex(ValueError,'grid'):
            dense_reference(text.replace('32 32 32','48 48 48'))
        with self.assertRaisesRegex(ValueError,'Nonfinite'):
            dense_reference(text.replace('0.0 0.001','nan 0.001',1))

    def test_staging_preserves_catalog_hashes_if_original_changes_after_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();inputs=root/'inputs';save=inputs/'pwscf.save';save.mkdir(parents=True)
            files={}
            for name in NAMES:
                path=save/name;path.write_text(fixture() if name.endswith('.xml') else 'known')
                key='pwscf.save/'+name
                files[key]=dict(url=PREFIX+key,bytes=path.stat().st_size,sha256=digest(path))
            dense=inputs/'pwscf.a2Fsave'
            dense.write_text('26 897\n'+' '.join(['0']*(26*897))+'\n'+
                ' '.join(['0']*(3*897))+'\n'+' '.join(['0']*896+['2'])+'\n32 32 32\n')
            files['pwscf.a2Fsave']=dict(url=PREFIX+'pwscf.a2Fsave',bytes=dense.stat().st_size,sha256=digest(dense))
            manifest=root/'catalog.json';manifest.write_text(json.dumps(dict(files=files)))
            exe=root/'pw.x';exe.write_bytes(b'executable fixture')
            def changed_after_check(*args):
                result=stage_pilot(*args)
                (save/'charge-density.dat').write_bytes(b'changed')
                dense.write_bytes(b'changed dense reference')
                return result
            with patch('stage_public_dense_bands.stage_pilot',side_effect=changed_after_check):
                result=stage(exe,inputs,root/'run',manifest)
            self.assertEqual(result['points'],897)
            self.assertIn('K_POINTS tpiba\n897\n',(root/'run/native.in').read_text())
            entries=[item for item in result['files'] if item['path']==str(save/'charge-density.dat')]
            self.assertEqual(entries[0]['sha256'],files['pwscf.save/charge-density.dat']['sha256'])
            self.assertNotEqual(entries[0]['sha256'],digest(save/'charge-density.dat'))
            entry=next(item for item in result['files'] if item['path']==str(dense))
            self.assertEqual(entry['sha256'],files['pwscf.a2Fsave']['sha256'])
            self.assertNotEqual(entry['sha256'],digest(dense))

    def test_dense_readback_checks_last_band_of_last_point_without_offset_fit(self):
        reference=[dict(k_tpiba=[0.,0.,0.],eigenvalues_ry=[float(j) for j in range(26)]) for _ in range(897)]
        states=''.join('<ks_energies><k_point>0 0 0</k_point><eigenvalues>'+
            ' '.join(str(j/2) for j in range(26))+'</eigenvalues></ks_energies>' for _ in range(897))
        xml='<root><output><band_structure>'+states+'</band_structure></output></root>'
        self.assertEqual(max(compare(reference,xml,expected_points=897)),0.)
        reference[-1]['eigenvalues_ry'][-1]+=.02
        differences=compare(reference,xml,expected_points=897)
        self.assertEqual(max(differences[:-1]),0.)
        self.assertAlmostEqual(differences[-1],.02)

    def test_pilot_protocol_stays_eight_and_dense_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'897'):
            compare([],fixture(),expected_points=897)
        with self.assertRaisesRegex(ValueError,'eight'):
            compare([],fixture())


if __name__=='__main__':
    unittest.main()
