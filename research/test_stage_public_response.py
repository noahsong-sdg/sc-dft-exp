import json
from pathlib import Path
import tempfile
import unittest

from fetch_public_response_inputs import PREFIX, digest
from stage_public_response import stage


class StagePublicResponseTest(unittest.TestCase):
    def test_checked_new_run_and_stale_input_or_build_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            build = root/'build'; (build/'probe').mkdir(parents=True)
            exe = build/'probe/velocity-moment-probe.x'; exe.write_bytes(b'fixture')
            (build/'build-result.json').write_text(json.dumps(dict(executable=str(exe), executable_sha256=digest(exe))))
            inputs = root/"input's"; inputs.mkdir()
            data = inputs/'pwscf.a2Fsave'; data.write_bytes(b'public')
            manifest = root/'manifest.json'
            manifest.write_text(json.dumps(dict(files={'pwscf.a2Fsave':dict(url=PREFIX+'pwscf.a2Fsave',
                bytes=data.stat().st_size, sha256=digest(data))})))
            run = root/'run'
            result = stage(build, inputs, run, manifest)
            self.assertEqual(result['command'][0], str(run/exe.name))
            self.assertIn("input''s/", (run/'native.in').read_text())
            self.assertFalse((run/'matdyn0').exists())
            self.assertEqual((run/exe.name).read_bytes(), exe.read_bytes())
            data.write_bytes(b'stale')
            with self.assertRaisesRegex(ValueError, 'public input'):
                stage(build, inputs, root/'stale-run', manifest)
            self.assertFalse((root/'stale-run').exists())
            exe.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'executable'):
                stage(build, inputs, root/'stale-build-run', manifest)
            self.assertFalse((root/'stale-build-run').exists())


if __name__ == '__main__':
    unittest.main()
