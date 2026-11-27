import json
from pathlib import Path
import tempfile
import unittest

from fetch_public_response_inputs import digest
from qualified_band_artifact import check


class QualifiedBandReuseTest(unittest.TestCase):
    def test_prior_evidence_reuse_preserves_history_and_rejects_changed_artifacts(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();parent=root/'parent.json'
            # Historical code hash is retained as evidence, not rewritten to today's source.
            parent.write_text(json.dumps(dict(files=[dict(path='/historical/stager.py',sha256='old-code')])) )
            paths=[root/'scratch/pwscf.a2Fsave',root/'scratch/pwscf.save/data-file-schema.xml',root/'reference.json']
            for path in paths:
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text('qualified artifact')
            receipt=root/'results/serialize/receipt.json';receipt.parent.mkdir(parents=True)
            terminal=dict(status='PASS',error=None,exit=0,cwd=str(root),continuous_deadline_s=120)
            receipt.write_text(json.dumps(terminal));paths += [receipt,parent]
            metadata=dict(grid=[48]*3,shared_point_and_serialization_targets_met=True,
                all_parent_coordinates_energies_weights_preserved=True,separate_native_serialization=True,
                energy_offset_fitted=False,minimum_common_reference_points=100,
                acceptance_max_eigenvalue_difference_ry=1e-6,shared_reference_points=145,
                max_shared_eigenvalue_difference_ry=4e-8,terminal_receipt=terminal,
                sha256={str(p):digest(p) for p in paths})
            result=root/'qualification.json';result.write_text(json.dumps(metadata));expected=digest(result)
            checked=check(root,parent,result,expected)
            self.assertTrue(checked['qualification_reused'])
            self.assertEqual(checked['sha256'][str(result)],expected)
            with self.assertRaisesRegex(ValueError,'Changed published'):
                check(root,parent,result,'0'*64)
            paths[0].write_text('changed serialized data')
            with self.assertRaisesRegex(ValueError,'Changed qualified artifact'):
                check(root,parent,result,expected)
            paths[0].write_text('qualified artifact')
            metadata['shared_reference_points']=99;result.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,'Expected qualified48'):
                check(root,parent,result,digest(result))
            metadata['shared_reference_points']=145
            metadata['sha256'].pop(str(receipt));result.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,'Missing qualified'):
                check(root,parent,result,digest(result))


if __name__=='__main__':
    unittest.main()
