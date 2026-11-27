import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fetch_public_response_inputs import PREFIX, digest
from stage_refined_response import stage
from stage_public_response import stage as stage_original


class RefinedResponseStagingTest(unittest.TestCase):
    def test_derived_identity_is_explicit_and_never_adopts_a_later_change(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();build=root/'build';(build/'probe').mkdir(parents=True)
            exe=build/'probe/velocity-moment-probe.x';exe.write_bytes(b'fixture')
            built=build/'build-result.json'
            built.write_text(json.dumps(dict(executable=str(exe),executable_sha256=digest(exe),point_capacity=300000)))
            inputs=root/'public';inputs.mkdir();catalog={}
            for name in ('pwscf.a2Fsave','pwscf.elph1'):
                p=inputs/name;p.write_text('original '+name)
                catalog[name]=dict(url=PREFIX+name,bytes=p.stat().st_size,sha256=digest(p))
            manifest=root/'catalog.json';manifest.write_text(json.dumps(dict(files=catalog)))
            bands=root/'bands';(bands/'scratch').mkdir(parents=True)
            derived=bands/'scratch/pwscf.a2Fsave';derived.write_text('generated48 bands')
            band_manifest=bands/'manifest.json';band_manifest.write_text('band protocol')
            checked=dict(shared_point_and_serialization_targets_met=True,
                sha256={str(derived):digest(derived),str(band_manifest):digest(band_manifest)})
            with patch('stage_refined_response.check_bands',return_value=dict(shared_point_and_serialization_targets_met=False)):
                with self.assertRaisesRegex(ValueError,'validation failed'):
                    stage(build,inputs,bands,band_manifest,root/'failed',manifest)
            self.assertFalse((root/'failed').exists())
            def changed_after_check(*args):
                result=stage_original(*args)
                derived.write_text('changed generated bands')
                return result
            with patch('stage_refined_response.check_bands',return_value=checked), patch(
                    'stage_refined_response.stage_original',side_effect=changed_after_check):
                result=stage(build,inputs,bands,band_manifest,root/'run',manifest)
            self.assertIn(str(root/'run/inputs')+'/',(root/'run/native.in').read_text())
            self.assertEqual(digest(inputs/'pwscf.a2Fsave'),catalog['pwscf.a2Fsave']['sha256'])
            identity=result['derived_inputs']['pwscf.a2Fsave']
            self.assertEqual(identity['sha256'],checked['sha256'][str(derived)])
            self.assertNotIn('url',identity)
            for path in (derived,root/'run/inputs/pwscf.a2Fsave'):
                entry=next(x for x in result['files'] if x['path']==str(path))
                self.assertEqual(entry['sha256'],checked['sha256'][str(derived)])
                self.assertNotEqual(entry['sha256'],digest(path))
            with patch('stage_refined_response.check_bands',return_value=checked):
                with self.assertRaisesRegex(ValueError,'changed after readback'):
                    stage(build,inputs,bands,band_manifest,root/'stale',manifest)
            self.assertFalse((root/'stale').exists())


if __name__=='__main__':
    unittest.main()
