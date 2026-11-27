import json
from pathlib import Path
import tempfile
import unittest

from public_band_grid_analysis import read_dense, shared_comparison, analyze
from fetch_public_response_inputs import digest


class BandGridReadbackTest(unittest.TestCase):
    def test_complete_readback_checks_last_common_band_stale_input_and_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();save=root/'scratch/pwscf.save';save.mkdir(parents=True)
            reference=[dict(k_tpiba=[i/1000.,0.,0.],eigenvalues_ry=[float(j) for j in range(26)]) for i in range(100)]
            (root/'reference.json').write_text(json.dumps(reference))
            original=root/'original';original.write_text('known')
            manifest=root/'manifest.json'
            command=[str(root/'pw.x'),'-in',str(root/'native.in')]
            manifest.write_text(json.dumps(dict(cwd=str(root),grid=[48]*3,
                acceptance_max_eigenvalue_difference_ry=1e-6,minimum_common_reference_points=100,
                command=command,files=[dict(path=str(original),bytes=original.stat().st_size,sha256=digest(original))])))
            receipt=root/'results/bands/receipt.json';receipt.parent.mkdir(parents=True)
            receipt.write_text(json.dumps(dict(status='PASS',error=None,exit=0,command=command,cwd=str(root),continuous_deadline_s=1200)))
            def outputs(last_shift):
                rows=[dict(k_tpiba=row['k_tpiba'],eigenvalues_ry=row['eigenvalues_ry'][:]) for row in reference]
                rows[-1]['eigenvalues_ry'][-1]+=last_shift
                (root/'scratch/pwscf.a2Fsave').write_text('26 100\n'+
                    ' '.join(str(x) for row in rows for x in row['eigenvalues_ry'])+'\n'+
                    ' '.join(str(x) for row in rows for x in row['k_tpiba'])+'\n'+
                    ' '.join(['.02']*100)+'\n48 48 48\n')
                xml=('<root><output><band_structure>'+''.join(
                    '<ks_energies><k_point>'+' '.join(map(str,row['k_tpiba']))+'</k_point><eigenvalues>'+
                    ' '.join(str(x/2) for x in row['eigenvalues_ry'])+'</eigenvalues></ks_energies>' for row in rows)+
                    '</band_structure></output></root>')
                (save/'data-file-schema.xml').write_text(xml)
            outputs(0)
            self.assertTrue(analyze(root,manifest)['shared_point_and_serialization_targets_met'])
            outputs(.01)
            self.assertFalse(analyze(root,manifest)['shared_point_and_serialization_targets_met'])
            original.write_text('stale')
            with self.assertRaisesRegex(ValueError,'Changed declared band-pilot input'):
                analyze(root,manifest)
            original.write_text('known')
            data=json.loads(receipt.read_text());data['cwd']='/stale';receipt.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'guard did not pass'):
                analyze(root,manifest)

    def test_ry_layout_last_band_and_grid_are_checked(self):
        text='26 2\n'+' '.join(str(i/10) for i in range(52))+'\n0 0 0 .1 .2 .3\n1 1\n48 48 48\n'
        rows=read_dense(text,48)
        self.assertEqual(rows[-1]['eigenvalues_ry'][-1],5.1)
        self.assertEqual(rows[-1]['k_tpiba'],[.1,.2,.3])
        for invalid in (text.replace('48 48 48','32 32 32'),text.replace('\n1 1\n','\n1 2\n')):
            with self.assertRaises(ValueError):
                read_dense(invalid,48)
        with self.assertRaisesRegex(ValueError,'Nonfinite'):
            read_dense(text.replace('0.0 0.1','nan 0.1'),48)

    def test_shared_absolute_energies_are_not_offset_fitted(self):
        old=[dict(k_tpiba=[0.,0.,0.],eigenvalues_ry=[float(i) for i in range(26)])]
        new=[dict(k_tpiba=[0.,0.,0.],eigenvalues_ry=[i+.02 for i in range(26)]),
             dict(k_tpiba=[.1,0.,0.],eigenvalues_ry=[float(i) for i in range(26)])]
        count,error=shared_comparison(old,new)
        self.assertEqual(count,1);self.assertAlmostEqual(error,.02)
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            shared_comparison(old,old+old)
        with self.assertRaisesRegex(ValueError,'No unchanged'):
            shared_comparison(old,new[1:])


if __name__=='__main__':
    unittest.main()
