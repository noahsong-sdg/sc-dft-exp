"""Check fresh ownership, immutable closure and post-execution verification."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import inverse_material_run as runner


class InverseMaterialRunTest(unittest.TestCase):
    def test_pin_and_parent_closure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root/'source'; source.write_text('original')
            item = runner.identity(source)
            parent = root/'parent.json'; parent.write_text(json.dumps(dict(files=[item])))
            manifest = dict(files=[item, runner.identity(parent)])
            pins = runner.check_pins(manifest)
            self.assertEqual(runner.parent(pins, parent)['files'], [item])
            with self.assertRaisesRegex(ValueError, 'Incomplete'):
                runner.parent({str(parent): runner.identity(parent)}, parent)
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                runner.check_pins(dict(files=[item, item]))
            source.write_text('stale')
            with self.assertRaisesRegex(ValueError, 'changed'):
                runner.check_pins(manifest)

    def test_fresh_output_and_post_native_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); manifest = root/'run-manifest.json'; manifest.write_text('{}')
            for name in runner.OUTPUTS:
                (root/name).write_text('stale')
                with self.assertRaisesRegex(ValueError, 'fresh'):
                    runner.run(root)
                (root/name).unlink()
            with patch.object(runner, 'validate', return_value={'files': []}), \
                    patch.object(runner.subprocess, 'run') as native, \
                    patch.object(runner, 'analyze', return_value={'physical_response_verified': False}), \
                    patch.object(runner, 'check_pins', side_effect=ValueError('changed input')):
                with self.assertRaisesRegex(ValueError, 'changed input'):
                    runner.run(root)
                native.assert_called_once_with([str(root/'inverse-actions.x')], cwd=root, check=True)
                self.assertFalse((root/'inverse-readback.json').exists())

    def test_terminal_claim_withheld_and_native_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root/'run-manifest.json').write_text('{}')
            with patch.object(runner, 'validate', return_value={'files': []}), \
                    patch.object(runner.subprocess, 'run'), \
                    patch.object(runner, 'analyze', return_value={'physical_response_verified': False}), \
                    patch.object(runner, 'check_pins'):
                result = runner.run(root)
                self.assertFalse(result['terminal_guard_pass'])
                self.assertFalse(result['physical_response_verified'])
                self.assertEqual(result, json.loads((root/'inverse-readback.json').read_text()))
            (root/'inverse-readback.json').unlink()
            with patch.object(runner, 'validate', return_value={'files': []}), \
                    patch.object(runner.subprocess, 'run', side_effect=RuntimeError('native failed')), \
                    patch.object(runner, 'analyze') as analyze:
                with self.assertRaisesRegex(RuntimeError, 'native failed'):
                    runner.run(root)
                analyze.assert_not_called()
                self.assertFalse((root/'inverse-readback.json').exists())
