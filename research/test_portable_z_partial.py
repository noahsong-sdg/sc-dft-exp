import json
from pathlib import Path
import tempfile
import unittest

from portable_z_partial import stage


class ZPartialStagingTest(unittest.TestCase):
    def test_failed_parent_or_existing_destination_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); parent = root/'parent'; parent.mkdir()
            (parent/'run-manifest.json').write_text('{}')
            receipt = parent/'results/zbuild/receipt.json'; receipt.parent.mkdir(parents=True)
            receipt.write_text(json.dumps(dict(status='FAIL',exit=1,error='failure')))
            with self.assertRaisesRegex(ValueError, 'Unaccepted parent'):
                stage(root, parent, root, root, root/'new')
            self.assertFalse((root/'new').exists())
            sentinel = root/'keep'; sentinel.write_text('preserved')
            with self.assertRaisesRegex(ValueError, 'Fresh'):
                stage(root, parent, root, root, root)
            self.assertEqual(sentinel.read_text(), 'preserved')
