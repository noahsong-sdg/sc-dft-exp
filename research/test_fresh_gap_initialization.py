import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fresh_gap_initialization as init
from fetch_public_response_inputs import PREFIX, digest


class FreshInitializationTest(unittest.TestCase):
    def test_stale_inputs_or_wrong_bundle_reject_before_creating_root(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); build = root/'build'; build.mkdir()
            inputs = root/'inputs'; inputs.mkdir()
            sources = root/'public_response_sources.json'; sources.write_text('{}')
            (build/'build-result.json').write_text(json.dumps(dict(source_manifest_sha256=digest(sources))))
            data = inputs/'pwscf.a2Fsave'; data.write_text('original bands')
            (root/'public_response_inputs.json').write_text(json.dumps(dict(files={
                'pwscf.a2Fsave': dict(url=PREFIX+'pwscf.a2Fsave', bytes=data.stat().st_size, sha256=digest(data))})))
            native = root/'native.in'; native.write_text("outdir='/different/'")
            with patch.object(init, 'RESEARCH', root):
                with self.assertRaisesRegex(ValueError, 'directory differs'):
                    init.stage(build, inputs, native, root/'new')
                data.write_text('changed bands')
                with self.assertRaisesRegex(ValueError, 'Changed microscopic'):
                    init.stage(build, inputs, native, root/'new')
                self.assertFalse((root/'new').exists())
            sentinel = root/'keep'; sentinel.write_text('preserved')
            with self.assertRaisesRegex(ValueError, 'Fresh'):
                init.stage(build, inputs, native, root)
            self.assertEqual(sentinel.read_text(), 'preserved')
