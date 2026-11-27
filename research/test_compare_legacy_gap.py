from pathlib import Path
import tempfile
import unittest
from compare_legacy_gap import records


class LegacyGapRecordTests(unittest.TestCase):
    def parse(self,text):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'gap'
            path.write_text(text)
            return list(records(path,[1,1]))

    def test_explicit_old_schema_and_grid_boundary(self):
        rows=self.parse('# 1 1\n\n-.4 .01 .2 .5 1 2\n.3 .02 .1 .4 3 4\n')
        self.assertEqual([(g,s,indices) for g,s,_,indices in rows],[(0,0,[1,2]),(1,0,[3,4])])

    def test_newer_schema_cannot_shift_integer_columns(self):
        with self.assertRaises(ValueError):
            self.parse('# 1 1\n-.4 .01 .2 .5 .001 1 2\n.3 .02 .1 .4 3 4\n')

    def test_missing_and_trailing_records_are_rejected(self):
        for text in ('# 1 1\n-.4 .01 .2 .5 1 2\n',
                     '# 1 1\n-.4 .01 .2 .5 1 2\n.3 .02 .1 .4 3 4\nextra\n'):
            with self.subTest(text=text),self.assertRaises(ValueError):
                self.parse(text)

    def test_nonfinite_record_is_rejected(self):
        with self.assertRaises(ValueError):
            self.parse('# 1 1\nnan .01 .2 .5 1 2\n.3 .02 .1 .4 3 4\n')


if __name__=='__main__':
    unittest.main()
