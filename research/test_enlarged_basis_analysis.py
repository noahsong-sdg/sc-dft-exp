from array import array
from pathlib import Path
import tempfile
import unittest

from enlarged_basis_analysis import read_reduced
from initial_basis_analysis import relative_residual


class EnlargedBasisLayoutTest(unittest.TestCase):
    def test_native_column_major_projected_matrix_and_eigenvectors(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            # Fortran writes H, real eigenvalues, imaginary parts, right vectors.
            values=[2.,0.,1.,3., 2.,3., 0.,0., 1.,0.,1.,1.]
            (root/'reduced.bin').write_bytes(array('d',values).tobytes())
            h,wr,wi,vr=read_reduced(root,2)
            self.assertEqual(list(h),[2.,0.,1.,3.])
            self.assertEqual(list(wi),[0.,0.])
            self.assertEqual(relative_residual([[1.,0.],[0.,1.]],
                [h[:2],h[2:]],vr[2:],wr[1]),0.)
            with self.assertRaisesRegex(ValueError,'shape'):read_reduced(root,3)
