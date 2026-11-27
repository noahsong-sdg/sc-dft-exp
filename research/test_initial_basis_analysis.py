from array import array
from pathlib import Path
import tempfile
import unittest

from initial_basis_analysis import binary,relative_residual


class InitialBasisReadbackTest(unittest.TestCase):
    def test_nonsymmetric_exact_mode_and_known_residual(self):
        # A=[[2,1],[0,3]], Q=identity. [1,1] is its eigenvector at3.
        q=[[1.,0.],[0.,1.]];aq=[[2.,0.],[1.,3.]]
        self.assertEqual(relative_residual(q,aq,[1.,1.],3.),0.)
        self.assertAlmostEqual(relative_residual(q,aq,[1.,0.],3.),1/3)
        self.assertEqual(relative_residual(q,aq,[7.,7.],3.),0.)

    def test_binary_shape_and_nonfinite_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'basis.bin'
            path.write_bytes(array('d',[1.,2.]).tobytes())
            self.assertEqual(list(binary(path,2)),[1.,2.])
            with self.assertRaisesRegex(ValueError,'shape'):binary(path,3)
            path.write_bytes(array('d',[1.,float('inf')]).tobytes())
            with self.assertRaisesRegex(ValueError,'Nonfinite'):binary(path,2)
