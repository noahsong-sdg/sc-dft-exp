import array
import contextlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

import resolved_sensitivity_prepare as owner
from inverse_material_run import identity


def put(path,values):
    with path.open('wb') as stream:array.array('d',values).tofile(stream)


class ResolvedSensitivityPrepareTest(unittest.TestCase):
    def fixture(self,root):
        spectrum=root/'spectrum';compact=root/'compact';previous=root/'previous';run=root/'run'
        for p in (spectrum,compact,previous,run):p.mkdir()
        n=128;eig=[0.]*60+[1.,4.,9.,16.]
        (spectrum/'row-spectrum.txt').write_text('retained-row-spectrum-v1; diagnostic, NOT an inverse or certificate\n64 64 1 64 3\n'+'\n'.join(map(str,eig))+'\n')
        put(spectrum/'row-eigenvectors.bin',[float(i==j) for j in range(64) for i in range(64)])
        put(spectrum/'row-errors.bin',[float(j+1) if j<4 and i==60+j else 0. for j in range(n) for i in range(64)])
        put(compact/'compact-q.bin',[float(i==4) for i in range(n)])
        put(compact/'compact-state.bin',[0.]*(4*n)+[2.]*n)
        put(previous/'trial-inputs.bin',[float(i==j) for j in (3,2,1) for i in range(n)])
        m=dict(cwd=str(run),command=[sys.executable,str(Path(owner.__file__).resolve())],compact=str(compact),spectrum=str(spectrum),previous=str(previous),counts=[64,64,1],files=[identity(p) for directory in (spectrum,compact,previous) for p in directory.iterdir()])
        (run/'run-manifest.json').write_text(json.dumps(m));return m,run

    def test_fixed_threshold_exact_omitted_mode_and_bitwise_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            m,run=self.fixture(Path(directory).resolve())
            with contextlib.chdir(run):result=owner.run(run)
            self.assertEqual(result['omitted_eigenvalues'],[1.]);self.assertEqual(result['new_columns'],1)
            self.assertEqual(result['reconstructed_action_max_error'],0.)
            self.assertTrue(result['original_trial_prefix_bitwise_equal']);self.assertTrue(result['training_only'])
            self.assertFalse(result['A_actions_available']);self.assertEqual(result['records'][0]['reconstruction_relative_error'],0.)
            data=array.array('d');data.frombytes((run/'trial-inputs.bin').read_bytes());self.assertEqual(data[-128:],array.array('d',[1.]+[0.]*127))
            with contextlib.chdir(run),self.assertRaises(ValueError):owner.run(run)

    def test_owner_stale_spectrum_payload_and_changed_input_pin(self):
        for fault in ('owner','pin','spectrum','payload','rank'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory() as directory:
                m,run=self.fixture(Path(directory).resolve());spectrum=Path(m['spectrum'])
                if fault=='owner':
                    with self.assertRaises(ValueError):owner.run(run)
                elif fault=='pin':
                    (Path(m['compact'])/'compact-q.bin').write_bytes(b'changed')
                    with contextlib.chdir(run),self.assertRaises(ValueError):owner.run(run)
                else:
                    if fault=='spectrum':(spectrum/'row-spectrum.txt').write_text('stale')
                    if fault=='payload':put(spectrum/'row-errors.bin',[0.]*8192)
                    if fault=='rank':
                        p=spectrum/'row-spectrum.txt';p.write_text(p.read_text().replace('64 64 1 64 3','64 64 62 64 3'))
                    with self.assertRaises(ValueError):owner.omitted_directions(spectrum,128)
                self.assertFalse((run/'resolved-readback.json').exists())
