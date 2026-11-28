import math
import unittest
from sensitivity_enrichment import trial_inputs,dot


class SensitivityEnrichmentTest(unittest.TestCase):
    def test_derivative_mapping_reorthogonalization_and_reconstruction(self):
        q=[[1.,0.,0.,0.]];d=[2.,3.,5.,7.]
        v=[[0.,1.,1.,0.],[0.,0.,1.,1.]]
        extra,records=trial_inputs(q,d,v)
        # A bare v would point equally along axes3/4; D*v must point5:7.
        self.assertAlmostEqual(extra[0][2]/extra[0][3],5/7)
        self.assertLess(abs(dot(extra[0],extra[1])),1e-14)
        self.assertTrue(all(r['reconstruction_relative_error']<1e-14 for r in records))
        self.assertEqual(v,[[0.,1.,1.,0.],[0.,0.,1.,1.]])

    def test_rejects_exhausted_span_nonfinite_and_stale_shape(self):
        for d,v in (([1.,1.],[[1.,0.]]),([0.,0.],[[0.,1.]]),([1.,1.],[[0.,math.nan]]),([1.,1.],[[0.]])):
            with self.subTest(d=d,v=v),self.assertRaises(ValueError):trial_inputs([[1.,0.]],d,v)

    def test_owner_rejects_wrong_cwd_stale_output_and_changed_pin(self):
        import contextlib
        import json
        from pathlib import Path
        import sys
        import tempfile
        import sensitivity_enrichment as owner
        from inverse_material_run import identity
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();pin=root/'input';pin.write_text('original')
            m=dict(cwd=str(root),command=[sys.executable,str(Path(owner.__file__).resolve())],files=[identity(pin)])
            (root/'run-manifest.json').write_text(json.dumps(m))
            with self.assertRaises(ValueError):owner.run(root)
            with contextlib.chdir(root):
                path=root/'trial-inputs.bin';path.write_text('stale')
                with self.assertRaises(ValueError):owner.run(root)
                path.unlink();pin.write_text('changed')
                with self.assertRaises(ValueError):owner.run(root)
