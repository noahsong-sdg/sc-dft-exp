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
            serialized=bands/'serialization-manifest.json'
            serialized.write_text(json.dumps(dict(source_band_manifest=str(band_manifest))))
            receipt=bands/'results/serialize/receipt.json';receipt.parent.mkdir(parents=True);receipt.write_text('{}')
            checked['sha256'].update({str(serialized):digest(serialized),str(receipt):digest(receipt)})
            with patch('stage_refined_response.check_serialization',return_value=checked), patch(
                    'stage_refined_response.check_bands',side_effect=AssertionError('Wrong validation route')):
                result=stage(build,inputs,bands,band_manifest,root/'serialized-run',manifest,serialization_manifest=serialized)
            self.assertEqual(result['derived_inputs']['pwscf.a2Fsave']['sha256'],digest(derived))
            with patch('stage_refined_response.check_serialization',return_value=checked) as checker:
                result64=stage(build,inputs,bands,band_manifest,root/'serialized64',manifest,
                    serialization_manifest=serialized,grid=64)
                self.assertEqual(result64['grid'],[64]*3)
                self.assertEqual(result64['guard_seconds'],900)
                checker.assert_called_once_with(bands,serialized,grid=64)
            with patch('stage_refined_response.check_serialization',return_value=checked) as checker:
                result32=stage(build,inputs,bands,band_manifest,root/'serialized32',manifest,
                    serialization_manifest=serialized,grid=32)
                self.assertEqual(result32['grid'],[32]*3)
                self.assertEqual(result32['guard_seconds'],120)
                checker.assert_called_once_with(bands,serialized,grid=32)
            with self.assertRaisesRegex(ValueError,'serialization'):
                stage(build,inputs,bands,band_manifest,root/'unqualified32',manifest,grid=32)
            self.assertFalse((root/'unqualified32').exists())
            with self.assertRaisesRegex(ValueError,'serialization'):
                stage(build,inputs,bands,band_manifest,root/'unqualified64',manifest,grid=64)
            self.assertFalse((root/'unqualified64').exists())
            qualification=root/'qualified-result.json';qualification.write_text('{}')
            qualification_hash=digest(qualification)
            qualified=dict(checked,qualification_reused=True,
                sha256={**checked['sha256'],str(qualification):qualification_hash})
            with patch('stage_refined_response.check_qualified',return_value=qualified) as checker, patch(
                    'stage_refined_response.check_bands',side_effect=AssertionError('Must use explicit prior qualification')):
                reused=stage(build,inputs,bands,band_manifest,root/'reused',manifest,
                    qualified_band_result=qualification,qualified_band_result_sha256=qualification_hash)
            checker.assert_called_once_with(bands,band_manifest,qualification,qualification_hash)
            self.assertTrue(reused['band_validation']['qualification_reused'])
            proof=next(item for item in reused['files'] if item['path']==str(qualification))
            self.assertEqual(proof['sha256'],qualification_hash)
            for extra in (dict(qualified_band_result=qualification),
                    dict(qualified_band_result_sha256=qualification_hash),
                    dict(qualified_band_result=qualification,qualified_band_result_sha256=qualification_hash,
                         serialization_manifest=serialized)):
                with self.assertRaisesRegex(ValueError,'result/hash pair'):
                    stage(build,inputs,bands,band_manifest,root/'bad-reuse',manifest,**extra)
                self.assertFalse((root/'bad-reuse').exists())
            serialized.write_text(json.dumps(dict(source_band_manifest='/stale/parent.json')))
            with self.assertRaisesRegex(ValueError,'different parent'):
                stage(build,inputs,bands,band_manifest,root/'wrong-parent',manifest,serialization_manifest=serialized)
            self.assertFalse((root/'wrong-parent').exists())
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
