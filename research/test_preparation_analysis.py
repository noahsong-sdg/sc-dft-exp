from pathlib import Path
import tempfile
import unittest
from preparation_analysis import analyze


STATE='''# preparation-only-v1; initial gap is NOT self-consistent
1 1
2 1 2
0.1 0 0
1 0 0 0 1 0 0 0 1
.4 1 1 .14 .012 1 3 2
-.4 1 .25 .14 .012 2 4 2
'''


class PreparationAnalysisTests(unittest.TestCase):
    def run_state(self,text):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'state.txt';path.write_text(text)
            return analyze(path)

    def test_serialized_q_scaling_and_separate_grid_estimates(self):
        result=self.run_state(STATE)
        self.assertAlmostEqual(result['qnorm'],.2)
        self.assertEqual([g['nonzero_curvature_states'] for g in result['grids']],[1,1])
        self.assertIn('NOT',result['scope'])

    def test_corrupt_or_production_state_is_rejected(self):
        for text in (STATE.replace('preparation-only-v1','scgap'),
                     STATE.replace('.4 1 1','nan 1 1'),
                     STATE.replace('1 3 2','2 3 2'),
                     STATE.rsplit('\n',2)[0]+'\n',STATE+'extra\n'):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):self.run_state(text)


if __name__=='__main__':unittest.main()
