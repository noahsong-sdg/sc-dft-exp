import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fetch_public_response_inputs import digest
from portable_basis_enrichment import accepted_basis


class EnrichmentAdmissionTest(unittest.TestCase):
    def test_contraction_matches_qualified_production(self):
        root = Path(__file__).parent/'portable_gap'
        texts = [(root/name).read_text().split('  subroutine accumulate(',1)[1]
            for name in ('basis_enrichment_driver.f90','basis_production_driver.f90')]
        self.assertEqual(*texts)

    def test_certified_vectors_context_and_exhausted_basis(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            names = ('native-linear.meta','basis.meta','basis.bin','ritz.meta','reduced.bin',
                'selected.meta','next.meta','next-vectors.bin')
            for name in names:(root/name).write_text('fixture')
            meta = root/'basis.meta'
            original = 'tc-basis-v1\n135880 16\n19613.355577892344\n'+'a'*64+'\n100 10 10 2 66867 67940\n'
            meta.write_text(original);(root/'next.meta').write_text('16\n')
            vectors = root/'next-vectors.bin';vectors.write_bytes(bytes(8*135880*16))
            def proof():
                (root/'basis-production-result.json').write_text(json.dumps(dict(
                    full_images_native_checked=True,full_output_sha256={name:digest(root/name) for name in names})))
            proof()
            parent = ({'context_sha256':'a'*64},{'completed':66867},[])
            with patch('portable_basis_enrichment.certified_parent',return_value=parent):
                self.assertEqual(accepted_basis(root)[2:],('a'*64,16))
                vectors.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'Changed certified'):accepted_basis(root)
                vectors.write_bytes(bytes(8*135880*16))
                for altered in (original.replace('135880 16','135880 64'),original.replace('a'*64,'b'*64)):
                    meta.write_text(altered);proof()
                    with self.assertRaisesRegex(ValueError,'Stale or exhausted'):accepted_basis(root)
