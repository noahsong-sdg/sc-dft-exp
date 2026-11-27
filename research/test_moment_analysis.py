from pathlib import Path
import tempfile
import unittest
from moment_analysis import analyze


OUTPUT='''# velocity-moment-diagnostic-v1; imposed constant gap; NOT a material prediction
100 6 7 32768 512
.0001 122
10 .1 1
0 0 0
2 .5 .6 .9 .9 1 1 1
4 .4 .5 .8 .8 1 1 1
8 .3 .4 .7 .7 1 1 1
'''


class MomentAnalysisTests(unittest.TestCase):
    def read(self,text):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'moments.txt';path.write_text(text)
            return analyze(path)

    def test_reports_closure_difference_without_equating_active_and_all_support(self):
        result=self.read(OUTPUT)
        self.assertEqual(result['negative_fine_weights'],10)
        self.assertEqual(result['cases'][0]['mean_squared_active'],[.5,.6])
        self.assertEqual(result['cases'][0]['second_moment_active'],[.9,.9])
        self.assertEqual(result['cases'][0]['direct_reference_max_absolute_error'],0.)

    def test_control_or_conservation_failures_reject_result(self):
        for text in (OUTPUT.replace('0 0 0\n','0 .001 0\n'),
                     OUTPUT.replace('1 1 1\n','1 1 2\n'),
                     OUTPUT.replace('.0001 122','nan 122')):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):self.read(text)

    def test_old_preparation_schema_and_truncation_rejected(self):
        for text in ('# preparation-only-v1\n',OUTPUT.rsplit('\n',2)[0]+'\n'):
            with self.assertRaises(ValueError):self.read(text)


if __name__=='__main__':unittest.main()
