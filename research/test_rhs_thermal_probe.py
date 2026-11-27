import unittest
from rhs_thermal_probe import extract, reference


class RHSThermalTests(unittest.TestCase):
    def test_finite_temperature_boundary_is_half_occupied(self):
        self.assertEqual(reference(0., 2., 2., 100.), .5)
        self.assertEqual(reference(0., .0002, .0002, 1.e6), .5)

    def test_unverified_source_is_rejected(self):
        with self.assertRaises(ValueError):
            extract(b"changed upstream")


if __name__ == "__main__":
    unittest.main()
