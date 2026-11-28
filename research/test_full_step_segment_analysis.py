"""Native checkpoint arithmetic plus declared evaluation/provenance boundaries."""
import array
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from fetch_public_response_inputs import digest
from full_step_segment_analysis import analyze
from inverse_material_run import identity
import test_full_map_segment_analysis as old_fixture
import test_full_step_probe as step_fixture


class FullStepSegmentAnalysisTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        old_fixture.FullMapSegmentAnalysisTests.setUpClass()
        cls.addClassCleanup(old_fixture.FullMapSegmentAnalysisTests.tearDownClass)
        cls.fixture=old_fixture.FullMapSegmentAnalysisTests.fixture
        step_fixture.FullStepProbeTest.setUpClass.__func__(cls)

    def prepare(self,base):
        root,path=old_fixture.FullMapSegmentAnalysisTests.prepare(self,base)
        for directory in (root,root/'split'):
            for name in ('full-map-progress.txt','linear-image-checkpoint.meta','linear-image-checkpoint.bin',
                         'full-map-checkpoint.meta','full-map-checkpoint-state.bin'):
                (directory/name).unlink(missing_ok=True)
        shutil.copy2(self.executables['declared'],root/'verify-gap-seed.x')
        gap=array.array('d');gap.frombytes((root/'gap-seed.bin').read_bytes())
        direction=array.array('d',[-.5 if x else 0. for x in gap]);direction[0]=1.
        (root/'direction-state.bin').write_bytes(gap.tobytes()+direction.tobytes())
        (root/'direction-state.meta').write_text('declared-full-map-direction-v1\n67 71 71\n1000\n'+'c'*64+'\n')
        (root/'full-map-step.in').write_text('declared-full-map-step-v1\n5.502435566805578e-10\n')
        (root/'direction-recipe.json').write_text('{"synthetic": true}\n')
        prepared=base/'prepared';prepared.mkdir()
        for name in ('direction-state.meta','direction-state.bin','full-map-step.in','direction-recipe.json'):
            shutil.copy2(root/name,prepared/name)
        preparation=dict(root=str(prepared),recipe=dict(candidate_sha256=digest(root/'gap-seed.bin'),operator_context_sha256='c'*64))
        recipe=json.loads((root/'evaluation-context.json').read_text())
        for key in ('direction_manifest','direction_result'):
            p=base/(key+'.json');p.write_text('{"files": []}\n');recipe[key]=dict(path=str(p),sha256=digest(p))
        recipe.update(schema='declared-step-full-map-evaluation-v1',executable_sha256=digest(root/'verify-gap-seed.x'))
        (root/'evaluation-context.json').write_text(json.dumps(recipe))
        context=digest(root/'evaluation-context.json')
        (root/'full-map-segment.in').write_text('ordered-full-map-control-v1\n'+context+'\n-\n0 64\nqualify\n')
        run=subprocess.run([str(root/'verify-gap-seed.x')],cwd=root,capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        (root/'results/moment/console.log').write_text(run.stdout)
        m=json.loads(path.read_text());m['evaluation_context_sha256']=context
        paths=[Path(x['path']) for x in m['files']]+[base/(key+'.json') for key in ('direction_manifest','direction_result')]
        paths += [root/name for name in ('direction-state.meta','direction-state.bin','full-map-step.in','direction-recipe.json')]
        m['files']=[identity(p) for p in paths]
        self.record(root,path,m)
        return root,path,preparation

    def record(self,root,path,m):
        path.write_text(json.dumps(m));(root/'run-manifest.json').write_bytes(path.read_bytes())

    def test_native_split_and_bound_preparation(self):
        with tempfile.TemporaryDirectory() as directory:
            root,path,preparation=self.prepare(Path(directory))
            with patch('full_step_segment_analysis.certify_direction',return_value=preparation):
                result=analyze(root,path)
            self.assertTrue(result['microscopic_split_qualified'])
            self.assertEqual(result['checkpoint']['step_ry'],5.502435566805578e-10)
            self.assertFalse(result['full_native_residual_verified'])
            self.assertFalse(result['physical_response_verified'])

    def test_stale_evaluation_and_rehashed_payload_reject(self):
        for mutation in ('schema','direction','step','preparation','ancestor_pin','checkpoint','marker','receipt'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                root,path,preparation=self.prepare(Path(directory));m=json.loads(path.read_text())
                if mutation in ('direction','step'):
                    p=root/('direction-state.bin' if mutation=='direction' else 'full-map-step.in')
                    p.write_bytes(p.read_bytes()+b'changed')
                    m['files']=[identity(x['path']) for x in m['files']];self.record(root,path,m)
                elif mutation=='preparation':preparation['recipe']['candidate_sha256']='d'*64
                elif mutation=='schema':
                    p=root/'evaluation-context.json';r=json.loads(p.read_text());r['schema']='ordered-full-map-evaluation-v1'
                    p.write_text(json.dumps(r));m['evaluation_context_sha256']=digest(p)
                    m['files']=[identity(x['path']) for x in m['files']];self.record(root,path,m)
                elif mutation=='ancestor_pin':
                    m['files']=[x for x in m['files'] if x['path']!=str(Path(directory)/'direction_result.json')]
                    self.record(root,path,m)
                elif mutation=='checkpoint':
                    p=root/'full-map-checkpoint.meta';p.write_text(p.read_text().replace('declared-step','old'))
                elif mutation=='marker':(root/'results/moment/console.log').write_text('')
                else:
                    p=root/'results/moment/receipt.json';r=json.loads(p.read_text());r['command']=['different'];p.write_text(json.dumps(r))
                with patch('full_step_segment_analysis.certify_direction',return_value=preparation):
                    with self.assertRaises(ValueError):analyze(root,path)

    def test_stage_strict_build_preparation_and_fresh_output(self):
        from stage_full_step_qualification import stage, RESEARCH
        for mutation in ('none','guard','deadline','peak','builder','candidate','closure'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as directory:
                base=Path(directory);source,seed,preparation=self.prepare(base)
                prepared=Path(preparation['root']);dm=base/'prep-public.json';dr=base/'prep-result-public.json'
                ancestor=dict(cwd=str(prepared),files=[])
                if mutation=='closure':ancestor['files']=[dict(identity(source/'native.in'),sha256='d'*64)]
                dm.write_text(json.dumps(ancestor));dr.write_text('{}')
                (prepared/'run-manifest.json').write_bytes(dm.read_bytes())
                (prepared/'direction-preparation-result.json').write_text('{}')
                (prepared/'results/direction').mkdir(parents=True)
                (prepared/'results/direction/receipt.json').write_text('{}')
                build=base/'build';(build/'results/build').mkdir(parents=True)
                exe=build/'full-gap-check.x';shutil.copy2(source/'verify-gap-seed.x',exe)
                command=['python',str(RESEARCH/'portable_full_step_build.py'),'run',str(build)]
                if mutation=='builder':command[1]='old-builder'
                b=dict(cwd=str(build),command=command,guard_source_sha256='b'*64,guard_seconds=120,
                       group_rss_cap_bytes=3221225472,files=[identity(RESEARCH/name) for name in
                       ('portable_full_step_build.py','full_step_checkpoint.f90','full_nonlinear_step_probe.f90','portable_gap/full_step_link.mk')])
                bp=base/'build-public.json';bp.write_text(json.dumps(b));(build/'run-manifest.json').write_bytes(bp.read_bytes())
                q=dict(checks=902,all_checks_bitwise_equal=True,full_gap_driver_linked=True,
                       historical_objects_used=False,full_gap_executable_sha256=digest(exe))
                (build/'qualification-result.json').write_text(json.dumps(q))
                r=dict(status='PASS',exit=0,error=None,command=command,cwd=str(build),guard_source_sha256='b'*64,
                       continuous_deadline_s=120,wall_s=1,max_individual_descendant_rss_bytes=1024,sampled_peak_group_rss_bytes=2048)
                if mutation=='guard':r['guard_source_sha256']='d'*64
                if mutation=='deadline':r['continuous_deadline_s']=121
                if mutation=='peak':r['sampled_peak_group_rss_bytes']=3221225473
                if mutation=='candidate':preparation['recipe']['candidate_sha256']='d'*64
                (build/'results/build/receipt.json').write_text(json.dumps(r))
                destination=base/'staged'
                with patch('stage_full_step_qualification.certify_direction',return_value=preparation):
                    if mutation!='none':
                        with self.assertRaises(ValueError):stage(seed,bp,dm,dr,destination)
                        self.assertFalse(destination.exists())
                    else:
                        m=stage(seed,bp,dm,dr,destination)
                        self.assertEqual(m['evaluation_context_sha256'],digest(destination/'evaluation-context.json'))
                        self.assertEqual((destination/'direction-state.bin').read_bytes(),(prepared/'direction-state.bin').read_bytes())
                        with self.assertRaisesRegex(ValueError,'Fresh'):stage(seed,bp,dm,dr,destination)
