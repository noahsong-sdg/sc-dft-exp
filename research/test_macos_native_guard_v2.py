"""Streaming verification preserves immutable manifests and rejection boundaries."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

if sys.platform == 'darwin':
    import macos_native_guard_v2 as guard


@unittest.skipUnless(sys.platform == 'darwin', 'macOS process/resource integration')
class StreamingGuardTest(unittest.TestCase):
    def test_streams_large_input_and_rejects_stale_bytes_or_shape(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();data=root/'native.bin'
            payload=b'bounded SHA256 fixture\0'*100000
            data.write_bytes(payload)
            manifest=root/'run-manifest.json'
            manifest.write_text(json.dumps(dict(cwd=str(root),command=['native.x'],
                files=[dict(path=str(data),bytes=len(payload),sha256=hashlib.sha256(payload).hexdigest())])))
            original=Path.read_bytes
            def reject_whole_input(path):
                if path==data:raise AssertionError('Manifest input was allocated whole')
                return original(path)
            with patch.object(Path,'read_bytes',reject_whole_input):
                guard.verify_manifest(root,['native.x'])
                data.write_bytes(b'changed'+payload[7:])
                with self.assertRaisesRegex(ValueError,'Changed staged input'):
                    guard.verify_manifest(root,['native.x'])
                data.write_bytes(payload[:-1])
                with self.assertRaisesRegex(ValueError,'Changed staged input'):
                    guard.verify_manifest(root,['native.x'])
                data.unlink()
                with self.assertRaises(FileNotFoundError):guard.verify_manifest(root,['native.x'])

    def test_resource_policy_is_identical_to_frozen_guard(self):
        def policy(path):
            tree=ast.parse(path.read_text())
            return [ast.dump(node,include_attributes=False) for node in tree.body
                if not (isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant)
                        and isinstance(node.value.value,str))
                and not (isinstance(node,ast.FunctionDef) and node.name=='verify_manifest')]
        root=Path(__file__).parent
        self.assertEqual(policy(root/'macos_native_guard.py'),policy(root/'macos_native_guard_v2.py'))

    def test_existing_guard_contract_on_versioned_implementation(self):
        # Reuse the existing real-child, deadline, launch ownership and stale-input
        # checks against the new module without changing the frozen old module.
        import test_macos_native_guard as tests
        with patch.object(tests,'guard',guard):
            suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.MacGuardTest)
            result=unittest.TestResult();suite.run(result)
        self.assertEqual(result.testsRun,4)
        self.assertEqual(result.errors,[])
        self.assertEqual(result.failures,[])


if __name__=='__main__':unittest.main()
