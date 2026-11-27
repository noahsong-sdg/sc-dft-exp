import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from public_band_pilot_analysis import compare, analyze, verify_postrun_inputs
from fetch_public_response_inputs import digest
from stage_public_band_pilot import render
from test_stage_public_band_pilot import fixture


class PublicBandReadbackTest(unittest.TestCase):
    def test_only_consumed_xml_can_be_rewritten_after_launch(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();save=root/'scratch/pwscf.save';save.mkdir(parents=True)
            xml=save/'data-file-schema.xml';xml.write_text('initial XML')
            charge=save/'charge-density.dat';charge.write_text('density')
            files=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in (xml,charge)]
            files[0]['rewritten_by_native']=True
            xml.write_text('native output XML')
            verify_postrun_inputs(dict(files=files),root)
            charge.write_text('changed')
            with self.assertRaisesRegex(ValueError,'Changed declared'):
                verify_postrun_inputs(dict(files=files),root)
            files[1]['rewritten_by_native']=True
            with self.assertRaisesRegex(ValueError,'Unexpected mutable'):
                verify_postrun_inputs(dict(files=files),root)

    def test_all_points_all_bands_and_no_fitted_energy_shift(self):
        xml=fixture(); _,reference=render(xml)
        self.assertEqual(compare(reference,xml),[0.]*8)
        root=ET.fromstring(xml)
        for state in root.findall('output/band_structure/ks_energies'):
            node=state.find('eigenvalues')
            node.text=' '.join(str(float(x)+.01) for x in node.text.split())
        shifted=compare(reference,ET.tostring(root,encoding='unicode'))
        self.assertTrue(all(abs(x-.02)<1e-14 for x in shifted))
        root.find('output/band_structure/ks_energies/k_point').text='0 0 .1'
        with self.assertRaisesRegex(ValueError,'layout'):
            compare(reference,ET.tostring(root,encoding='unicode'))
        with self.assertRaisesRegex(ValueError,'eight'):
            compare(reference[:-1],xml)

    def test_terminal_receipt_and_unchanged_original_are_required(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve(); (root/'scratch/pwscf.save').mkdir(parents=True)
            xml=fixture(); _,reference=render(xml)
            (root/'scratch/pwscf.save/data-file-schema.xml').write_text(xml)
            (root/'reference.json').write_text(json.dumps(reference))
            original=root/'original-density.dat';original.write_bytes(b'unchanged density')
            manifest=root/'manifest.json'
            manifest.write_text(json.dumps(dict(cwd=str(root),points=8,
                acceptance_max_eigenvalue_difference_ry=1e-6,command=['declared-pw.x'],
                files=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p))
                       for p in (root/'reference.json',original)])))
            with self.assertRaisesRegex(ValueError,'receipt required'):
                analyze(root,manifest)
            (root/'receipt.json').write_text(json.dumps(dict(command=['declared-pw.x'],cwd=str(root),
                status='PASS',exit=0,continuous_deadline_s=180)))
            self.assertTrue(analyze(root,manifest)['replay_targets_met'])
            original.write_bytes(b'changed density')
            with self.assertRaisesRegex(ValueError,'Changed declared'):
                analyze(root,manifest)


if __name__=='__main__':
    unittest.main()
