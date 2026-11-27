import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fetch_public_response_inputs import digest
from verify_refined_response import verify


class RefinedResponseReadbackTest(unittest.TestCase):
    def test_changed_consumed_data_and_wrong_grid_do_not_qualify(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();data=root/'bands';data.write_text('original')
            manifest=dict(cwd=str(root),grid=[48]*3,response_cell_grid=8,
                guard_seconds=240,command=['probe'],files=[dict(path=str(data),bytes=8,sha256=digest(data))])
            path=root/'run-manifest.json';path.write_text(json.dumps(manifest))
            receipt=root/'results/response/receipt.json';receipt.parent.mkdir(parents=True)
            receipt.write_text(json.dumps(dict(status='PASS',error=None,exit=0,
                command=['probe'],cwd=str(root),continuous_deadline_s=240)))
            controls=dict(dimensions=[100,6,7,48**3,512])
            physical=[1.,2.,1e-12,0.,0.]
            with patch('verify_refined_response.native_controls',return_value=controls), patch(
                    'verify_refined_response.read_pair',return_value=([100,6,7,512,2],physical,{},{})), patch(
                    'verify_refined_response.components',return_value={}), patch(
                    'verify_refined_response.digest',return_value='hash'):
                # Keep actual input hashing active inside the guard verifier.
                (root/'velocity-moments.txt').touch()
                self.assertTrue(verify(root,path)['diagnostic_readback_pass'])
                manifest['guard_seconds']=900;path.write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError,'declared refined-response'):
                    verify(root,path)
                with self.assertRaisesRegex(ValueError,'execution did not pass'):
                    verify(root,path,guard_seconds=900)
                terminal=json.loads(receipt.read_text());terminal['continuous_deadline_s']=900
                receipt.write_text(json.dumps(terminal))
                self.assertTrue(verify(root,path,guard_seconds=900)['diagnostic_readback_pass'])
                manifest['guard_seconds']=240;path.write_text(json.dumps(manifest))
                terminal['continuous_deadline_s']=240;receipt.write_text(json.dumps(terminal))
                controls['dimensions'][3]=32**3
                with self.assertRaisesRegex(ValueError,'native response grid'):
                    verify(root,path)
                data.write_text('changed!')
                with self.assertRaisesRegex(ValueError,'Changed staged input'):
                    verify(root,path)


if __name__=='__main__':
    unittest.main()
