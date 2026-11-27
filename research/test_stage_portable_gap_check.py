import json
from pathlib import Path
import tempfile
import unittest
from fetch_public_response_inputs import digest
from stage_portable_gap_check import stage


class PortableCheckStagingTest(unittest.TestCase):
    def test_stale_build_dependency_or_existing_destination_cannot_launch(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);build=root/'build';build.mkdir();receipt=build/'results/build/receipt.json';receipt.parent.mkdir(parents=True)
            lib=build/'liblapack.a';lib.write_text('original library')
            manifest=dict(cwd=str(build),command=['builder'],files=[dict(path=str(lib),bytes=lib.stat().st_size,sha256=digest(lib))])
            (build/'run-manifest.json').write_text(json.dumps(manifest))
            (build/'qualification-result.json').write_text(json.dumps(dict(full_gap_driver_linked=True,checks=902)))
            receipt.write_text(json.dumps(dict(status='PASS',exit=0,error=None,command=['builder'],cwd=str(build))))
            lib.write_text('changed library')
            with self.assertRaisesRegex(ValueError,'Changed declared'):
                stage(build,root/'inputs',root/'reference.json',root/'new')
            self.assertFalse((root/'new').exists())
            (root/'existing').mkdir();sentinel=root/'existing/preserved';sentinel.write_text('do not replace')
            with self.assertRaisesRegex(ValueError,'Fresh replacement'):
                stage(build,root/'inputs',root/'reference.json',root/'existing')
            self.assertEqual(sentinel.read_text(),'do not replace')
            terminal=json.loads(receipt.read_text());terminal['status']='FAIL';receipt.write_text(json.dumps(terminal))
            with self.assertRaisesRegex(ValueError,'not accepted'):
                stage(build,root/'inputs',root/'reference.json',root/'failed')
            self.assertFalse((root/'failed').exists())


if __name__=='__main__':unittest.main()
