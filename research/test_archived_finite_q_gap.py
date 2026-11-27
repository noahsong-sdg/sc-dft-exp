from pathlib import Path
import tempfile
import unittest
from archived_finite_q_gap import records


class ArchivedFiniteQGapTests(unittest.TestCase):
    def parse(self,text):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'gap';path.write_text(text)
            return list(records(path,[1,1]))

    def test_finite_q_velocity_and_order_are_preserved(self):
        values=self.parse('# 1 1\n\n-.4 -.01 .2 .5 -.001 1 2\n.3 .02 .1 .4 .002 3 4\n')
        self.assertEqual(values[0],(0,0,[-.4,-.01,.2,.5,-.001],[1,2]))
        self.assertEqual(values[1][0],1)

    def test_stale_missing_or_extra_fields_are_rejected(self):
        for first in ('-.4 .01 .2 .5 1 2','-.4 .01 .2 .5 .001 .002 1 2',''):
            with self.subTest(first=first),self.assertRaises(ValueError):
                self.parse('# 1 1\n'+first+'\n.3 .02 .1 .4 .002 3 4\n')

    def test_nonfinite_and_trailing_data_are_rejected(self):
        for text in ('# 1 1\nnan .01 .2 .5 .001 1 2\n.3 .02 .1 .4 .002 3 4\n',
                     '# 1 1\n-.4 .01 .2 .5 .001 1 2\n.3 .02 .1 .4 .002 3 4\nextra\n'):
            with self.assertRaises(ValueError):self.parse(text)


if __name__=='__main__':unittest.main()
