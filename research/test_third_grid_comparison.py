import copy
import json
from pathlib import Path
import tempfile
import unittest

from fetch_public_response_inputs import digest
from third_grid_comparison import compare


class ThirdGridComparisonTest(unittest.TestCase):
    def test_contraction_reversal_and_incompatible_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'baseline.json';source.write_text('registered source')
            rows=[dict(temperature_kelvin=t,fourth32=1.,fourth48=1.1,conditional64={'2':1.135,'4':1.117}) for t in (2,4,8)]
            plan=root/'plan.json';plan.write_text(json.dumps(dict(cases=rows,input_sha256={source.name:digest(source)})))
            expected_plan=digest(plan)
            def result(grid,value):
                return dict(diagnostic_readback_pass=True,all_declared_inputs_unchanged=True,
                    all_eight_exports_bitwise_equal=True,cache_physical=[1e-12,100.,1e-12,0.,0.],
                    terminal_receipt=dict(status='PASS',exit=0,error=None,continuous_deadline_s=900),
                    native_controls=dict(dimensions=[100,6,7,grid**3,512],cases=[
                        dict(temperature_kelvin=t,imposed_gap_mev=1.5,fine_grid_reference=value) for t in (2,4,8)]))
            old=result(48,1.1);new=result(64,1.12)
            a=root/'48.json';b=root/'64.json'
            def write():
                a.write_text(json.dumps(old));b.write_text(json.dumps(new))
            write();checked=compare(plan,a,b,expected_plan)
            self.assertTrue(checked['contracts_at_all_temperatures'])
            self.assertTrue(checked['same_direction_at_all_temperatures'])
            self.assertFalse(checked['continuum_error_bounded'])
            new=result(64,1.09);write();checked=compare(plan,a,b,expected_plan)
            self.assertTrue(checked['contracts_at_all_temperatures'])
            self.assertFalse(checked['same_direction_at_all_temperatures'])
            new=result(64,1.3);write()
            self.assertFalse(compare(plan,a,b,expected_plan)['contracts_at_all_temperatures'])
            good_new=result(64,1.12);good_old=copy.deepcopy(old)
            for mutate in ('unqualified','context','temperature','grid','baseline','guard'):
                new=copy.deepcopy(good_new);old=copy.deepcopy(good_old)
                if mutate=='unqualified':old['all_eight_exports_bitwise_equal']=False
                if mutate=='context':new['cache_physical'][1]=101.
                if mutate=='temperature':new['native_controls']['cases'][0]['temperature_kelvin']=3
                if mutate=='grid':new['native_controls']['dimensions'][3]=48**3
                if mutate=='baseline':old['native_controls']['cases'][0]['fine_grid_reference']=1.100001
                if mutate=='guard':new['terminal_receipt']['status']='FAIL'
                write()
                with self.subTest(mutate=mutate),self.assertRaises(ValueError):
                    compare(plan,a,b,expected_plan)
            saved_plan=plan.read_bytes();plan.write_text('changed hypothesis')
            with self.assertRaisesRegex(ValueError,'Changed registered hypothesis'):
                compare(plan,a,b,expected_plan)
            plan.write_bytes(saved_plan)
            source.write_text('changed prior source')
            with self.assertRaisesRegex(ValueError,'Changed prospective'):
                compare(plan,a,b,expected_plan)


if __name__=='__main__':
    unittest.main()
