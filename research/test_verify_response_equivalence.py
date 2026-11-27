import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fetch_public_response_inputs import digest
from verify_response_equivalence import EXPORTS, compare


class ExactResponseExportsTest(unittest.TestCase):
    def test_all_exports_required_and_both_baseline_and_candidate_are_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();baseline=root/'baseline';baseline.mkdir()
            run=root/'run';run.mkdir();entries=[]
            for name in sorted(EXPORTS):
                source=baseline/name;source.write_text(name)
                (run/name).write_bytes(source.read_bytes())
                entries.append(dict(name=name,path=str(source),bytes=source.stat().st_size,sha256=digest(source)))
            manifest=root/'manifest.json'
            def write(rows):
                manifest.write_text(json.dumps(dict(guard_seconds=900,baseline_exports=rows)))
            write(entries)
            with patch('verify_response_equivalence.verify',return_value=dict(physical_response_verified=False)) as check:
                result=compare(run,manifest)
                self.assertTrue(result['all_eight_exports_bitwise_equal'])
                self.assertEqual(len(result['comparison']),8)
                check.assert_called_once_with(run,manifest,guard_seconds=900,grid=48)
                write(entries[:-1])
                with self.assertRaisesRegex(ValueError,'eight unique'):
                    compare(run,manifest)
                write(entries[:-1]+[entries[0]])
                with self.assertRaisesRegex(ValueError,'eight unique'):
                    compare(run,manifest)
                write(entries)
                changed=run/entries[0]['name'];changed.write_text('changed candidate')
                with self.assertRaisesRegex(ValueError,'export differs'):
                    compare(run,manifest)
                changed.write_bytes(Path(entries[0]['path']).read_bytes())
                Path(entries[-1]['path']).write_text('changed baseline')
                with self.assertRaisesRegex(ValueError,'Changed frozen baseline'):
                    compare(run,manifest)


if __name__=='__main__':
    unittest.main()
