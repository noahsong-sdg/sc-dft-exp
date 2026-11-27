import json
from pathlib import Path
import tempfile
import unittest
from regenerated32_analysis import compare,digest


class RegenerationAnalysisTest(unittest.TestCase):
    def test_same_grid_shift_and_changed_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            plan=root/'plan.json';plan.write_text(json.dumps(dict(original_third_grid_hypothesis_unchanged=True)))
            physical=[1e-12,100.,1e-12,0.,0.]
            fourth=root/'public_indexed_fourth_response64_result.json'
            fourth.write_text(json.dumps(dict(cache_physical=physical)))
            series=root/'series.json';series.write_text(json.dumps(dict(
                cases=[dict(temperature_kelvin=t,fourth32=1.,fourth48=1.1,fourth64=1.05) for t in (2,4,8)],
                sha256={str(fourth):digest(fourth)})))
            result=dict(terminal_receipt=dict(status='PASS',exit=0,error=None,continuous_deadline_s=120),
                diagnostic_readback_pass=True,all_declared_inputs_unchanged=True,cache_physical=physical[:],
                native_controls=dict(dimensions=[100,6,7,32**3,512],cases=[dict(
                    temperature_kelvin=t,imposed_gap_mev=1.5,fine_grid_reference=1.001) for t in (2,4,8)]))
            control=root/'control.json'
            def write():control.write_text(json.dumps(result))
            write();expected=digest(plan);checked=compare(plan,series,control,expected)
            self.assertAlmostEqual(checked['cases'][0]['regeneration_fraction'],.001)
            self.assertAlmostEqual(checked['cases'][0]['regeneration_shift_over_original32to48'],.01)
            self.assertFalse(checked['continuum_error_bounded'])
            result['cache_physical'][1]=101.;write()
            with self.assertRaisesRegex(ValueError,'volume'):
                compare(plan,series,control,expected)
            result['cache_physical']=physical[:];result['terminal_receipt']['continuous_deadline_s']=900;write()
            with self.assertRaisesRegex(ValueError,'qualified automatic32'):
                compare(plan,series,control,expected)
            fourth.write_text('changed source')
            with self.assertRaisesRegex(ValueError,'series source'):
                compare(plan,series,control,expected)
            plan.write_text('changed plan')
            with self.assertRaisesRegex(ValueError,'prospective regeneration plan'):
                compare(plan,series,control,expected)


if __name__=='__main__':
    unittest.main()
