from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class MeshEquivalenceTest(unittest.TestCase):
    def test_indexed_map_matches_independent_brute_force(self):
        compiler=shutil.which('gfortran');self.assertIsNotNone(compiler)
        research=Path(__file__).parent.resolve()
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            subprocess.run([compiler,'-O2','-ffp-contract=off','-fcheck=all',
                str(research/'mesh_equivalence.f90'),str(research/'mesh_equivalence_fixture.f90'),
                '-o','fixture'],cwd=root,check=True,capture_output=True)
            result=subprocess.run([str(root/'fixture')],cwd=root,check=True,
                                  capture_output=True,text=True,timeout=30)
            self.assertIn('1920  uniform-mesh cases match brute force',result.stdout)
            for context,message in [('ambiguous','Ambiguous uniform-mesh tolerance'),
                    ('nonfinite','Nonfinite reciprocal point'),
                    ('range','Reciprocal index exceeds integer range')]:
                failed=subprocess.run([str(root/'fixture'),context],cwd=root,
                    capture_output=True,text=True,timeout=5)
                self.assertNotEqual(failed.returncode,0)
                self.assertIn(message,failed.stderr)


if __name__=='__main__':
    unittest.main()
