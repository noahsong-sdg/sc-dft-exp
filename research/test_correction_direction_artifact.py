"""Synthetic evidence controls; these fixtures are not material calculations."""
import array
import json
from pathlib import Path
import tempfile
import unittest

import correction_direction_artifact as artifact
from fetch_public_response_inputs import digest
from inverse_material_run import identity
from prepare_correction_direction import write_direction


def save(path, value):
    path.write_text(json.dumps(value, allow_nan=False))


class CorrectionDirectionArtifactTest(unittest.TestCase):
    def fixture(self, directory):
        base=Path(directory).resolve();root=base/'preparation';prior=base/'inverse';full=base/'full'
        (root/'results/direction').mkdir(parents=True);prior.mkdir();full.mkdir()
        gap=array.array('d',[.001,.002,0,.003,.004,.005])
        correction=array.array('d',[-1e-10,2e-10,0,3e-10,-4e-10,1e-10])
        (full/'gap-seed.bin').write_bytes(gap.tobytes());(full/'gap-seed.meta').write_text('synthetic source metadata')
        data=array.array('d',[0.]*6)+correction+array.array('d',[0.]*8)
        (prior/'inverse-result.bin').write_bytes(data.tobytes())
        (prior/'inverse-control.in').write_text('\n'.join(['low-rank-inverse-control-v1','basis','geometry',str(full),'a'*64,'1000','config'])+'\n')
        inverse_manifest=base/'inverse-manifest.json';inverse_result=base/'inverse-result.json'
        inherited=[identity(p) for p in (prior/'inverse-result.bin',prior/'inverse-control.in',full/'gap-seed.bin',full/'gap-seed.meta')]
        save(inverse_manifest,dict(cwd=str(prior),files=inherited))
        save(inverse_result,dict(dimensions=[6,1,2,3,3],beta=1000,correction_infinity_ry=4e-10))
        helper=Path(artifact.__file__).with_name('prepare_correction_direction.py').resolve()
        recipe=write_direction(root,gap,correction,[2,3,3],1000,'a'*64)
        recipe.update(schema='compressed-correction-direction-v1',counts=[2,3,3],beta=1000,operator_context_sha256='a'*64,inverse_manifest=dict(path=str(inverse_manifest),sha256=digest(inverse_manifest)),
                      inverse_result=dict(path=str(inverse_result),sha256=digest(inverse_result)),
                      source_correction_sha256=digest(prior/'inverse-result.bin'))
        save(root/'direction-recipe.json',recipe)
        manifest=dict(cwd=str(root),command=['python',str(helper)],files=inherited+[identity(p) for p in (helper,inverse_manifest,inverse_result)],
                      inverse_manifest=str(inverse_manifest),inverse_result=str(inverse_result),
                      guard_source_sha256='b'*64,guard_seconds=90,group_rss_cap_bytes=3221225472)
        path=base/'manifest.json';save(path,manifest);(root/'run-manifest.json').write_bytes(path.read_bytes())
        receipt=dict(status='PASS',exit=0,error=None,command=manifest['command'],cwd=str(root),
                     guard_source_sha256='b'*64,continuous_deadline_s=90,wall_s=1,
                     max_individual_descendant_rss_bytes=1024,sampled_peak_group_rss_bytes=2048)
        save(root/'results/direction/receipt.json',receipt)
        result=base/'result.json';self.record(root,path,result,receipt)
        return root,path,result

    def record(self,root,path,result,receipt=None):
        if receipt is None:receipt=json.loads((root/'results/direction/receipt.json').read_text())
        raw=dict(terminal_guard_pass=False,inputs_unchanged=True,recipe=json.loads((root/'direction-recipe.json').read_text()),
                 recipe_sha256=digest(root/'direction-recipe.json'),scope='synthetic')
        save(root/'direction-preparation-result.json',raw)
        save(result,dict(raw,terminal_guard_pass=True,receipt=receipt,manifest_sha256=digest(path),
                         readback_sha256=digest(root/'direction-preparation-result.json'),
                         output_files={name:identity(root/name) for name in artifact.OUTPUTS}))

    def test_exact_payload_without_replaying_inverse(self):
        with tempfile.TemporaryDirectory() as directory:
            root,path,result=self.fixture(directory)
            checked=artifact.certify(path,result)
            self.assertTrue(checked['terminal_guard_pass'])
            self.assertEqual(checked['recipe']['step_ry'],4e-10)
            self.assertFalse(checked['conditioned_gap_error_bounded'])
            self.assertFalse(checked['physical_response_verified'])

    def test_stale_evidence_and_rehashed_numeric_changes_reject(self):
        for change in ('consumed','receipt','deadline','terminal','closure','output','direction','candidate','step','roundoff','metadata','source'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as directory:
                root,path,result=self.fixture(directory)
                if change=='consumed':(root/'run-manifest.json').write_text('{}')
                elif change in ('receipt','deadline'):
                    p=root/'results/direction/receipt.json';r=json.loads(p.read_text())
                    r['guard_source_sha256' if change=='receipt' else 'continuous_deadline_s']='c'*64 if change=='receipt' else 91
                    save(p,r);self.record(root,path,result)
                elif change=='terminal':
                    r=json.loads(result.read_text());r['terminal_guard_pass']=False;save(result,r)
                elif change=='closure':
                    m=json.loads(path.read_text());m['files'].pop(0);save(path,m)
                    (root/'run-manifest.json').write_bytes(path.read_bytes());self.record(root,path,result)
                elif change=='output':(root/'direction-state.bin').write_bytes(b'stale')
                elif change=='source':
                    m=json.loads(path.read_text());p=Path(m['files'][0]['path']);p.write_bytes(b'stale source')
                else:
                    recipe=json.loads((root/'direction-recipe.json').read_text())
                    if change in ('direction','candidate'):
                        p=root/'direction-state.bin';state=array.array('d');state.frombytes(p.read_bytes())
                        state[6 if change=='direction' else 0]*=.5;p.write_bytes(state.tobytes())
                        recipe['sha256'][p.name]=digest(p)
                    elif change=='step':
                        p=root/'full-map-step.in';p.write_text('declared-full-map-step-v1\n8e-10\n')
                        recipe['step_ry']=8e-10;recipe['sha256'][p.name]=digest(p)
                    elif change=='metadata':
                        p=root/'direction-state.meta';p.write_text(p.read_text().replace('1000','1001'))
                        recipe['sha256'][p.name]=digest(p)
                    else:recipe['rescaled_correction_max_absolute_difference_ry']=1.
                    save(root/'direction-recipe.json',recipe);self.record(root,path,result)
                with self.assertRaises(ValueError):artifact.certify(path,result)
