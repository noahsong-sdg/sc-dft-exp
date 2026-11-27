import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from stencil_control_analysis import compare, digest


class StencilControlTest(unittest.TestCase):
    def test_conditional_prediction_and_stale_or_changed_context(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);research=root/'research';research.mkdir()
            old=research/'grid_stencil_comparison.json'
            old.write_text(json.dumps(dict(cases=[dict(fourth48=1.1,second48=1.) for _ in range(3)])))
            def result(value):
                return dict(diagnostic_readback_pass=True,all_declared_inputs_unchanged=True,
                    terminal_receipt=dict(cwd=folder,status='PASS',error=None,exit=0,continuous_deadline_s=900),
                    native_controls=dict(dimensions=[100,6,7,64**3,512],cases=[dict(
                        temperature_kelvin=t,imposed_gap_mev=1.5,fine_grid_reference=value) for t in (2,4,8)]),
                    components=dict(sha256={str(old):digest(old)}))
            second=research/'second.json';fourth=research/'public_indexed_fourth_response64_result.json'
            second.write_text(json.dumps(result(1.)));fourth.write_text(json.dumps(result(1.05625)))
            plan=research/'plan.json'
            plan.write_text(json.dumps(dict(sha256={str(p.relative_to(root)):digest(p) for p in (old,fourth)},
                conditional_predictions={str(t):.5625*(1.1-1.) for t in (2,4,8)})))
            expected=digest(plan)
            fields={name:[1.,2.] for name in ('xi0','dx0','dos','curvature')}
            cache=([100,6,7,512,2],[1e-12,100.,1e-12,0.,0.],fields,copy.deepcopy(fields))
            with patch('stencil_control_analysis.read_pair',side_effect=[cache,cache]):
                checked=compare(plan,second,fourth,expected)
            self.assertAlmostEqual(checked['cases'][0]['difference_ratio64_over48'],.5625)
            self.assertAlmostEqual(checked['cases'][0]['conditional_prediction_relative_discrepancy'],0.)
            self.assertFalse(checked['continuum_error_bounded'])
            for field in ('xi0','dx0','dos','curvature'):
                changed=copy.deepcopy(cache);changed[2][field][0]=99.
                with self.subTest(field=field),patch('stencil_control_analysis.read_pair',side_effect=[cache,changed]):
                    with self.assertRaisesRegex(ValueError,'stencil-independent'):
                        compare(plan,second,fourth,expected)
            changed=copy.deepcopy(cache);changed[1][1]=101.
            with patch('stencil_control_analysis.read_pair',side_effect=[cache,changed]):
                with self.assertRaisesRegex(ValueError,'context'):
                    compare(plan,second,fourth,expected)
            second.write_text(json.dumps(result(2.)))
            bad=result(2.);bad['native_controls']['cases'][0]['imposed_gap_mev']=1.6
            second.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError,'temperature controls'):
                compare(plan,second,fourth,expected)
            old.write_text('changed baseline')
            with self.assertRaisesRegex(ValueError,'prospective source'):
                compare(plan,second,fourth,expected)
            plan.write_text('changed plan')
            with self.assertRaisesRegex(ValueError,'prospective stencil plan'):
                compare(plan,second,fourth,expected)


if __name__=='__main__':
    unittest.main()
