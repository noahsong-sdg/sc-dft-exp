import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fetch_public_response_inputs import digest
import portable_gap_cache as build


class PortableGapStageTest(unittest.TestCase):
    def test_source_only_manifest_and_stale_source_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);research=root/'research';research.mkdir();public=root/'public';qe=public/'qe';qe.mkdir(parents=True)
            (research/'portable_gap').mkdir()
            names=['portable_gap/cached_kel.f90','portable_gap/cached_phonon.f90',
                'portable_gap/cache_qualification.f90','portable_gap/cache_qualification.mk',
                'public_response_probe.mk','public_response_sources.json','portable_gap_cache.py','macos_native_guard.py']
            for name in names:(research/name).write_text('fixture '+name)
            records={name:dict(sha256=digest(research/'portable_gap'/name)) for name in ('cached_kel.f90','cached_phonon.f90')}
            (research/'portable_gap/source_provenance.json').write_text(json.dumps(records))
            (qe/'make.inc').write_text('qualified configuration')
            (qe/'core.a').write_text('public library');(qe/'kinds.mod').write_text('public interface')
            parent=public/'build-result.json';parent.write_text(json.dumps(dict(source_manifest_sha256=digest(research/'public_response_sources.json'))))
            with patch.object(build,'RESEARCH',research):
                result=build.stage(public,root/'run')
                paths={p['path'] for p in result['files']}
                self.assertIn(str(qe/'core.a'),paths);self.assertIn(str(qe/'kinds.mod'),paths)
                self.assertFalse(result['historical_objects_used'])
                with self.assertRaisesRegex(ValueError,'Fresh custom'):
                    build.stage(public,root/'run')
                source=research/'portable_gap/tiled_operator.f90';source.write_text('operator source')
                proof=research/'portable_gap/operator_source_provenance.json'
                proof.write_text(json.dumps({source.name:dict(sha256=digest(source))}))
                makefile=research/'portable_gap/operator_compile.mk';makefile.write_text('operator target')
                operator=build.stage(public,root/'operator',operator_compile=True)
                self.assertTrue(operator['operator_compile'])
                self.assertIn(str(source),{item['path'] for item in operator['files']})
                source.write_text('changed operator')
                with self.assertRaisesRegex(ValueError,'Changed migrated'):
                    build.stage(public,root/'changed-operator',operator_compile=True)
                self.assertFalse((root/'changed-operator').exists())
                (research/'portable_gap/cached_kel.f90').write_text('modified arithmetic')
                with self.assertRaisesRegex(ValueError,'Changed migrated'):
                    build.stage(public,root/'changed')
                self.assertFalse((root/'changed').exists())
                parent.write_text(json.dumps(dict(source_manifest_sha256='stale')))
                with self.assertRaisesRegex(ValueError,'Different public source'):
                    build.stage(public,root/'bad-parent')
                self.assertFalse((root/'bad-parent').exists())


if __name__=='__main__':unittest.main()
