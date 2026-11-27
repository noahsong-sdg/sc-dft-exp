import hashlib
import io
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from fetch_public_response_inputs import PREFIX, fetch_one, validate


class Response(io.BytesIO):
    status = 200
    headers = {}

    def geturl(self):
        return PREFIX+'pwscf.a2Fsave'


class PublicInputFetchTests(unittest.TestCase):
    def item(self, payload=b'public'):
        return dict(url=PREFIX+'pwscf.a2Fsave', bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())

    def test_download_then_verify_existing_and_preserve_stale_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            with patch('fetch_public_response_inputs.urlopen', return_value=Response(b'public')):
                result = fetch_one(root, 'pwscf.a2Fsave', self.item(), time.monotonic()+30)
            self.assertEqual(result['status'], 'downloaded')
            with patch('fetch_public_response_inputs.urlopen') as opener:
                self.assertEqual(fetch_one(root, 'pwscf.a2Fsave', self.item(), time.monotonic()+30)['status'], 'verified_existing')
                opener.assert_not_called()
            path = root/'pwscf.a2Fsave'; path.write_bytes(b'stale')
            with self.assertRaisesRegex(ValueError, 'preserved'):
                fetch_one(root, 'pwscf.a2Fsave', self.item(), time.monotonic()+30)
            self.assertEqual(path.read_bytes(), b'stale')

    def test_corrupt_truncated_or_oversize_download_never_promoted(self):
        for payload in (b'wrong!', b'pub', b'public-extra'):
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as folder:
                root = Path(folder).resolve()
                with patch('fetch_public_response_inputs.urlopen', return_value=Response(payload)):
                    with self.assertRaises(ValueError):
                        fetch_one(root, 'pwscf.a2Fsave', self.item(), time.monotonic()+30)
                self.assertFalse((root/'pwscf.a2Fsave').exists())

    def test_invalid_identity_symlink_and_deadline_rejected(self):
        for name in ('../outside', '/outside', 'a/../outside'):
            with self.assertRaises(ValueError):
                validate(name, {**self.item(), 'url': PREFIX+name})
        with self.assertRaises(ValueError):
            validate('pwscf.a2Fsave', {**self.item(), 'url': 'https://example.com/file'})
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            with self.assertRaises(TimeoutError):
                fetch_one(root, 'pwscf.a2Fsave', self.item(), time.monotonic()-1)
            (root/'pwscf.a2Fsave').symlink_to(root/'outside')
            with self.assertRaisesRegex(ValueError, 'Symlink'):
                fetch_one(root, 'pwscf.a2Fsave', self.item(), time.monotonic()+30)


if __name__ == '__main__':
    unittest.main()
