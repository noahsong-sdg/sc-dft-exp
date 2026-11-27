import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fetch_public_response_inputs import PREFIX, digest
from stage_public_band_grid import stage
from stage_public_band_pilot import NAMES, stage as stage_pilot
from test_stage_public_band_pilot import fixture


class PublicBandGridTest(unittest.TestCase):
    def test_fixed_density_grid_changes_only_declared_controls_and_rejects_stale_reference(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();inputs=root/'inputs';save=inputs/'pwscf.save';save.mkdir(parents=True)
            files={}
            for name in NAMES:
                path=save/name;path.write_text(fixture() if name.endswith('.xml') else 'known')
                key='pwscf.save/'+name
                files[key]=dict(url=PREFIX+key,bytes=path.stat().st_size,sha256=digest(path))
            dense=inputs/'pwscf.a2Fsave'
            dense.write_text('26 897\n'+' '.join(['0']*(26*897))+'\n'+
                ' '.join(['0']*(3*897))+'\n'+' '.join(['0']*896+['2'])+'\n32 32 32\n')
            files['pwscf.a2Fsave']=dict(url=PREFIX+'pwscf.a2Fsave',bytes=dense.stat().st_size,sha256=digest(dense))
            catalog=root/'catalog.json';catalog.write_text(json.dumps(dict(files=files)))
            build=root/'build';(build/'qe/bin').mkdir(parents=True)
            (build/'qe/bin/pw.x').write_bytes(b'executable fixture')
            result=build/'build-result.json';result.write_text('{}')
            with self.assertRaisesRegex(ValueError,'full48cubed'):
                stage(build,inputs,root/'insufficient',catalog)
            self.assertFalse((root/'insufficient').exists())
            result.write_text(json.dumps(dict(point_capacity=300000)))
            def changed_after_check(*args):
                staged=stage_pilot(*args)
                dense.write_bytes(b'changed')
                return staged
            with patch('stage_public_band_grid.stage_pilot',side_effect=changed_after_check):
                staged=stage(build,inputs,root/'run',catalog)
            native=(root/'run/native.in').read_text()
            self.assertIn('K_POINTS automatic\n48 48 48 0 0 0',native)
            self.assertIn("occupations='fixed',",native)
            self.assertNotIn('la2F',native)
            self.assertIn("startingpot='file'",native)
            self.assertIn('ecutwfc=40, ecutrho=320',native)
            self.assertNotIn('K_POINTS tpiba',native)
            entry=next(x for x in staged['files'] if x['path']==str(dense))
            self.assertEqual(entry['sha256'],files['pwscf.a2Fsave']['sha256'])
            self.assertNotEqual(entry['sha256'],digest(dense))
            with self.assertRaisesRegex(ValueError,'Changed original'):
                stage(build,inputs,root/'stale',catalog)
            self.assertFalse((root/'stale').exists())


if __name__=='__main__':
    unittest.main()
