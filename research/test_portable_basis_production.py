from pathlib import Path
import unittest

from portable_basis_production import interval


class ProductionTraversalTest(unittest.TestCase):
    def test_production_contraction_is_identical_to_qualified_source(self):
        root = Path(__file__).parent/'portable_gap'
        def contraction(name):
            text = (root/name).read_text()
            return text[text.index('  subroutine accumulate('):]
        self.assertEqual(contraction('basis_sweep_driver.f90'),contraction('basis_production_driver.f90'))

    def test_contiguous_tile_boundaries_and_registered_chunk_sizes(self):
        for first,last,previous in ((1,16384,None),(16385,32768,'prior'),(32769,49152,'prior'),(49153,66867,'prior')):
            interval(first,last,previous)
        for first,last,previous in ((1,16384,'prior'),(16385,32768,None),(2,64,'prior'),(1,33,None),(1,32768,None),(49153,66868,'prior')):
            with self.subTest(first=first,last=last), self.assertRaises(ValueError):
                interval(first,last,previous)
