import array
import json
import math
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from fetch_public_response_inputs import digest
from occupation_prepare_readback import analyze


class OccupationPreparationReadbackTests(unittest.TestCase):
    def fixture(self, root, scale=1.):
        full, reduced, old, geometry, run = [root/name for name in ('full','reduced','old','geometry','run')]
        for folder in (full, reduced, old, geometry, run/'basis', run/'results/occupation'):
            folder.mkdir(parents=True)
        context = 'a'*64; x = [0., .1, .2, .3, .4, .5]
        gap = [scale*v for v in (.1,.2,.3,.4,.5,.6)]
        occupation = []
        for xi, d in zip(x, gap):
            e = math.hypot(xi, d)
            denominator = math.tanh(50*abs(xi))/abs(xi) if xi else 50
            occupation.append(d/e*math.tanh(50*e)/denominator)
        norm = math.sqrt(math.fsum(v*v for v in occupation[1:]))
        q = [0., *(v/norm for v in occupation[1:])]; e1 = [1.,0.,0.,0.,0.,0.]
        meta = f'tc-basis-v1\n6 1\n100\n{context}\n2 10 10 2 3 3\n'
        (old/'basis.meta').write_text(meta)
        (old/'basis.bin').write_bytes(struct.pack('<12d', *e1, *(2*v for v in e1)))
        (run/'basis/basis.meta').write_text(meta.replace('6 1','6 2'))
        (run/'basis/basis.bin').write_bytes(struct.pack('<24d', *e1, *q, *(2*v for v in e1), *(2*v for v in q)))
        (geometry/'native-init.meta').write_text('native-init-v1; arrays are native binary64/int32, Fortran order\n3 3 3 2 512 26 3\n0 1 1 1 1 1 1\nT\n')
        values = [-1.,1.,1.,1., *x, *([0.]*6), *([1.]*6), *([0.]*12)]
        (geometry/'native-init.bin').write_bytes(struct.pack('<34d12i', *values, *([1]*12)))
        (reduced/'reduced-control.in').write_text(f'{old}\n{geometry}\n/mode\n{context}\n100 .15\n')
        (full/'full-map.bin').write_bytes(struct.pack('<12d', *gap, *(2*f-d for f,d in zip(occupation,gap))))
        fm = root/'full-manifest.json'; fm.write_text(json.dumps(dict(cwd=str(full))))
        candidate = dict(stationary_residual_targets_met=False, full_readback=dict(beta=100.))
        checked = dict(complete_left_row_coverage=True, full_candidate=candidate)
        fr = root/'full-result.json'; fr.write_text(json.dumps(checked))
        inputs = [old/'basis.meta',old/'basis.bin',geometry/'native-init.meta',geometry/'native-init.bin',
                  reduced/'reduced-control.in',full/'full-map.bin',fm,fr]
        manifest = dict(cwd=str(run), command=['fixture'], files=[dict(path=str(p),bytes=p.stat().st_size,sha256=digest(p)) for p in inputs],
                        guard_seconds=180,guard_source_sha256='b'*64,operator_context_sha256=context,full_manifest=str(fm),full_result=str(fr),reduced_directory=str(reduced))
        mp = root/'preparation.json'; mp.write_text(json.dumps(manifest))
        (run/'run-manifest.json').write_text(json.dumps(manifest))
        receipt = dict(status='PASS',exit=0,error=None,command=['fixture'],cwd=str(run),guard_source_sha256='b'*64,
                       continuous_deadline_s=180,wall_s=.01,max_individual_descendant_rss_bytes=1000,sampled_peak_group_rss_bytes=1000)
        (run/'results/occupation/receipt.json').write_text(json.dumps(receipt))
        report = dict(full_segmented_certificate=checked,full_evaluation=candidate,full_result_sha256=digest(fr),
                      full_candidate_targets_met=False,old_rank=1,new_rank=2,beta=100.,context=context,
                      inputs_sha256={str(p):digest(p) for p in inputs},
                      outputs_sha256={str(p):digest(p) for p in (run/'basis/basis.meta',run/'basis/basis.bin')})
        (run/'basis/enrichment.json').write_text(json.dumps(report))
        return mp, run, checked

    def test_explicit_manifest_for_two_independent_datasets(self):
        with tempfile.TemporaryDirectory() as folder:
            for index, scale in enumerate((1., .7)):
                mp, run, checked = self.fixture(Path(folder)/str(index), scale)
                with patch('occupation_prepare_readback.certify', return_value=checked):
                    result = analyze(mp)
                self.assertTrue(result['inherited_columns_bitwise_preserved'])
                self.assertEqual(result['new_rank'], 2)
                self.assertFalse(result['full_candidate_targets_met'])
                self.assertLess(result['exponential_occupation_image_reconstruction_error'], result['reconstruction_bound'])
                self.assertEqual(result['manifest_sha256'], digest(mp))

    def test_adopted_output_hash_cannot_bypass_independent_controls(self):
        for change in ('inherited', 'direction', 'action', 'context', 'partial', 'rss', 'flag'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as folder:
                mp, run, checked = self.fixture(Path(folder))
                if change in ('inherited','direction','action'):
                    p = run/'basis/basis.bin'; data = array.array('d'); data.frombytes(p.read_bytes())
                    data[{'inherited':0,'direction':6,'action':18}[change]] += .1
                    p.write_bytes(data.tobytes())
                if change == 'context':
                    p = run/'basis/basis.meta'; p.write_text(p.read_text().replace('a'*64,'c'*64))
                report_path = run/'basis/enrichment.json'; report = json.loads(report_path.read_text())
                report['outputs_sha256'] = {p:digest(Path(p)) for p in report['outputs_sha256']}
                if change == 'flag': report['full_candidate_targets_met'] = True
                report_path.write_text(json.dumps(report))
                if change == 'partial': checked['complete_left_row_coverage'] = False
                if change == 'rss':
                    p = run/'results/occupation/receipt.json'; receipt = json.loads(p.read_text())
                    receipt['max_individual_descendant_rss_bytes'] = math.nan; p.write_text(json.dumps(receipt))
                with patch('occupation_prepare_readback.certify', return_value=checked):
                    with self.assertRaises(ValueError): analyze(mp)


if __name__ == '__main__':
    unittest.main()
