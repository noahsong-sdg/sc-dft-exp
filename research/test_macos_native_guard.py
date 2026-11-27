import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

if sys.platform == 'darwin':
    import macos_native_guard as guard


@unittest.skipUnless(sys.platform == 'darwin', 'macOS process/resource integration')
class MacGuardTest(unittest.TestCase):
    def test_cli_uses_declared_cwd_and_rejects_existing_owner(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve()
            data=root/'native.in';data.write_bytes(b'declared input')
            (root/'run-manifest.json').write_text(json.dumps(dict(cwd=str(root),
                command=['declared-pw.x','-in','native.in'],files=[dict(path=str(data),
                bytes=data.stat().st_size,sha256=hashlib.sha256(data.read_bytes()).hexdigest())])))
            with patch.object(guard,'wait_normal'), patch.object(guard,'run',return_value={'status':'PASS'}) as run:
                result=guard.main(['bands','180',str(root),'declared-pw.x','-in','native.in'])
                self.assertEqual(result['status'],'PASS')
                self.assertEqual(guard.ROOT,root)
                self.assertEqual(run.call_args.args[:4],('bands',['declared-pw.x','-in','native.in'],root,180.))
                self.assertEqual(json.loads((root/'campaign_launch_watch.json').read_text())['phase'],'completed')
                with self.assertRaises(FileExistsError):
                    guard.main(['bands','180',str(root),'declared-pw.x','-in','native.in'])

    def test_stale_or_changed_command_is_rejected_before_owner_exists(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();data=root/'native.in';data.write_bytes(b'stale')
            (root/'run-manifest.json').write_text(json.dumps(dict(cwd=str(root),command=['pw.x'],
                files=[dict(path=str(data),bytes=5,sha256='a'*64)])))
            with self.assertRaisesRegex(ValueError,'Changed staged'):
                guard.main(['bands','180',str(root),'pw.x'])
            self.assertFalse((root/'campaign_launch_watch.json').exists())
            with self.assertRaisesRegex(ValueError,'Command/cwd'):
                guard.main(['bands','180',str(root),'different.x'])

    def test_normal_window_resets_and_has_a_deadline(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            times=iter([0,0,0,60,60,90,90,150,150,270,270])
            with patch.object(guard.time,'monotonic',side_effect=lambda:next(times)), \
                 patch.object(guard,'pressure',side_effect=['1','1','2','1','1']), \
                 patch.object(guard.time,'sleep'):
                guard.wait_normal(root)
            self.assertEqual(json.loads((root/'campaign_launch_watch.json').read_text())['normal_seconds'],120.)
            with patch.object(guard.time,'monotonic',side_effect=[0,1201]):
                with self.assertRaisesRegex(RuntimeError,'launch window'):
                    guard.wait_normal(root)

    def test_real_child_success_failure_and_timeout_receipts(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); old=guard.ROOT; guard.ROOT=root
            try:
                with patch.object(guard,'pressure',return_value='1'):
                    result=guard.run('success',[sys.executable,'-c','print("guard-fixture")'],root,5)
                    self.assertEqual(result['status'],'PASS')
                    self.assertEqual(result['exit'],0)
                    with self.assertRaisesRegex(RuntimeError,'exit 7'):
                        guard.run('failure',[sys.executable,'-c','raise SystemExit(7)'],root,5)
                    with self.assertRaisesRegex(RuntimeError,'deadline'):
                        guard.run('timeout',[sys.executable,'-c','import time;time.sleep(30)'],root,.25)
                self.assertEqual(json.loads((root/'results/failure/receipt.json').read_text())['exit'],7)
                self.assertEqual(json.loads((root/'results/timeout/receipt.json').read_text())['status'],'FAIL')
            finally:
                guard.ROOT=old


if __name__=='__main__':
    unittest.main()
