import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import portable_z_build as z
from fetch_public_response_inputs import digest


class ZBuildTest(unittest.TestCase):
    def test_stale_migrated_source_rejects_before_creating_root(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); build = root/'build'; build.mkdir()
            sources = root/'public_response_sources.json'; sources.write_text('{}')
            (build/'build-result.json').write_text(json.dumps(dict(source_manifest_sha256=digest(sources))))
            port = root/'portable_gap'; port.mkdir()
            source = port/'zsf_workspace.f90'; source.write_text('original')
            (port/'z_source_provenance.json').write_text(json.dumps({source.name: dict(sha256=digest(source))}))
            source.write_text('changed')
            with patch.object(z, 'RESEARCH', root):
                with self.assertRaisesRegex(ValueError, 'Changed migrated'):
                    z.stage(build, root/'new')
            self.assertFalse((root/'new').exists())
            sentinel = root/'keep'; sentinel.write_text('preserved')
            with self.assertRaisesRegex(ValueError, 'Fresh'):
                z.stage(build, root)
            self.assertEqual(sentinel.read_text(), 'preserved')
