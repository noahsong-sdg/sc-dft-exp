import json
from pathlib import Path
import tempfile
import unittest

from fetch_public_response_inputs import digest
from portable_basis_split import RESEARCH, accepted_trials


class FreshTrialsAdmissionTest(unittest.TestCase):
    def test_certified_trials_and_changed_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'results/basispartial').mkdir(parents=True)
            names = {'receipt_sha256':'results/basispartial/receipt.json',
                'binary_sha256':'basis-partial.bin','metadata_sha256':'basis-partial.meta',
                'executable_sha256':'basis-partial.x'}
            for name in names.values():
                (root/name).write_text('fixture')
            source = root/'input.dat';source.write_text('original')
            (root/'run-manifest.json').write_text(json.dumps({'files':[
                dict(path=str(source),bytes=source.stat().st_size,sha256=digest(source))]}))
            names['manifest_sha256'] = 'run-manifest.json'
            result = {key:digest(root/name) for key,name in names.items()}
            result.update(status='PASS',analysis_source_sha256=digest(RESEARCH/'basis_partial_analysis.py'))
            (root/'basis-partial-result.json').write_text(json.dumps(result))
            self.assertTrue(accepted_trials(root))
            payload = root/'basis-partial.bin';payload.write_text('changed')
            with self.assertRaisesRegex(ValueError, 'fresh trials'):
                accepted_trials(root)
            payload.write_text('fixture');source.write_text('modified')
            with self.assertRaisesRegex(ValueError, 'Changed declared'):
                accepted_trials(root)
