from pathlib import Path
import tempfile
import unittest
from compare_finite_q_geometry import compare

PREP='''# preparation-only-v1; initial gap is NOT self-consistent
1 1
2 1 1
.1 0 0
1 0 0 0 1 0 0 0 1
-.4 .01 .5 -.001 .002 1 1 2
.3 .01 .4 .002 .003 2 3 4
'''
GAP='# 1 1\n-.4 -.02 .2 .5 -.001 1 2\n.3 .02 .1 .4 .002 3 4\n'


class FiniteQGeometryTests(unittest.TestCase):
    def run_case(self,prep=PREP,gap=GAP):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'prep').write_text(prep);(root/'gap').write_text(gap)
            return compare(root/'prep',root/'gap')

    def test_geometry_is_compared_without_substituting_initial_gap(self):
        result=self.run_case()
        for row in result['grids']:
            self.assertEqual(row['index_mismatches'],0)
            self.assertEqual(row['max_shift_absolute_difference'],0)
            self.assertEqual(row['max_weight_absolute_difference'],0)

    def test_different_indices_are_reported(self):
        result=self.run_case(gap=GAP.replace('1 2\n','9 2\n'))
        self.assertEqual(result['grids'][0]['index_mismatches'],1)

    def test_stale_gap_and_incomplete_geometry_are_rejected(self):
        with self.assertRaises(ValueError):self.run_case(gap=GAP.replace(' -.001',''))
        with self.assertRaises(ValueError):self.run_case(prep=PREP.rsplit('\n',2)[0]+'\n')


if __name__=='__main__':unittest.main()
