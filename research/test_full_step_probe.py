"""Real native variable-step/restart controls and independent plus-image residual."""
import array
import math
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

from correction_image_readback import corrected_states
from full_step_summary_analysis import analyze as step_summary
from full_nonlinear_analysis import analyze as fixed_summary
from test_full_map_checkpoint import STUBS, MAIN
import test_declared_full_direction as direction_fixture


class FullStepProbeTest(unittest.TestCase):
    run_native = direction_fixture.DeclaredFullDirectionTest.run_native

    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('gfortran')
        if not compiler:raise AssertionError('Native step compiler required')
        cls.build = tempfile.TemporaryDirectory();cls.addClassCleanup(cls.build.cleanup)
        root = Path(cls.build.name); research = Path(__file__).resolve().parent
        (root/'stubs.f90').write_text(STUBS);(root/'main.f90').write_text(MAIN)
        sources = [root/'stubs.f90',research/'nonlinear_tile_apply.f90',
                   research/'portable_gap/linear_image_checkpoint.f90',research/'full_step_checkpoint.f90',
                   research/'declared_full_direction.f90',research/'full_nonlinear_step_probe.f90',root/'main.f90']
        exe = root/'fixture.x'
        subprocess.run([compiler,'-O2','-ffp-contract=off','-ffree-line-length-none','-fcheck=all',
                        *map(str,sources),'-lblas','-o',str(exe)],cwd=root,check=True,capture_output=True)
        cls.executables = {'declared':exe}

    def stage(self,root,step=5.502435566805578e-10,stop=67,previous='-',completed=0):
        direction_fixture.DeclaredFullDirectionTest.stage(self,root,stop,previous,completed)
        (root/'full-map-step.in').write_text(f'declared-full-map-step-v1\n{step:.17g}\n')

    def test_corrected_residuals_match_dense_nonlinear_evaluation(self):
        step = 5.502435566805578e-10
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);self.stage(root,step)
            run = self.run_native(root);self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            summary = step_summary(root)
            self.assertEqual(summary['finite_difference_step_ry'],step)
            with self.assertRaises(ValueError):fixed_summary(root)
            control=root/'full-map-step.in';original=control.read_text()
            control.write_text('declared-full-map-step-v1\n6e-10\n')
            with self.assertRaises(ValueError):step_summary(root)
            control.write_text(original)
            images = array.array('d');images.frombytes((root/'linear-image-checkpoint.bin').read_bytes())
            state = struct.unpack('<284d',(root/'direction-state.bin').read_bytes())
            gap,direction = state[:142],state[142:]
            z = [0.]*142
            for side,count in enumerate((67,71)):
                for j in range(count):z[side*71+j]=.5+(j+1)/100
            result = corrected_states(images,gap,direction,z,[67,71,71],step)
            self.assertFalse(result['conditioned_gap_error_bounded'])
            for k,point in enumerate((gap,result['plus_gap'],result['minus_gap'])):
                weights = [0.]*142
                for side,count in enumerate((67,71)):
                    for j in range(count):
                        i=side*71+j;x=(j+1-17)*.001;w=(j+1-5)/1000;e=math.hypot(x,point[i])
                        q=math.exp(-1000*e)
                        weights[i]=w*point[i]/2/e*(1-q)/(1+q) if e else 0.
                for side,count in enumerate((67,71)):
                    for j in range(count):
                        i=side*71+j
                        if side==0:
                            image=math.fsum((100+3*(j+1)-2*(t+1))/97*weights[71+t] for t in range(71))
                        else:
                            image=math.fsum((200+3*(t+1)-2*(j+1))/97*weights[t] for t in range(67))
                        expected=-image/(1+z[i])-point[i]
                        self.assertAlmostEqual(result['residuals'][k][i],expected,delta=2e-16+2e-12*abs(expected))
            meta=(root/'full-map-checkpoint.meta').read_text().splitlines()
            self.assertTrue(meta[0].startswith('declared-step-full-map-checkpoint-v1'))
            self.assertEqual(float(meta[1].split()[0]),step)
            for badstep in (0.,-1.,float('nan'),float('inf')):
                with self.assertRaises(ValueError):corrected_states(images,gap,direction,z,[67,71,71],badstep)
            corrupt=array.array('d',images);corrupt[142]+=1e-5
            with self.assertRaisesRegex(ValueError,'finite difference'):
                corrected_states(corrupt,gap,direction,z,[67,71,71],step)

    def test_restart_step_and_schema_are_immutable(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);first=root/'first';self.stage(first,stop=32)
            self.assertEqual(self.run_native(first).returncode,0)
            final=root/'final';self.stage(final,previous=first,completed=32)
            run=self.run_native(final);self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            continuous=root/'continuous';self.stage(continuous)
            self.assertEqual(self.run_native(continuous).returncode,0)
            self.assertEqual((final/'full-map.bin').read_bytes(),(continuous/'full-map.bin').read_bytes())
            self.assertEqual((final/'linear-image-checkpoint.bin').read_bytes(),(continuous/'linear-image-checkpoint.bin').read_bytes())
            changed=root/'changed';self.stage(changed,step=6e-10,previous=first,completed=32)
            self.assertNotEqual(self.run_native(changed).returncode,0)
            meta=first/'full-map-checkpoint.meta'
            meta.write_text(meta.read_text().replace('declared-step-full-map-checkpoint-v1','ordered-full-map-checkpoint-v1'))
            stale=root/'stale';self.stage(stale,previous=first,completed=32)
            self.assertNotEqual(self.run_native(stale).returncode,0)

    def test_bad_native_steps_reject_before_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            for index,text in enumerate(('declared-full-map-step-v1\n0\n','declared-full-map-step-v1\nnan\n',
                                         'declared-full-map-step-v1\n-1\n','declared-full-map-step-v1\ninf\n','old\n1e-8\n',
                                         'declared-full-map-step-v1\n1e-8\nextra\n')):
                root=Path(directory)/str(index);self.stage(root);(root/'full-map-step.in').write_text(text)
                self.assertNotEqual(self.run_native(root).returncode,0)
                self.assertFalse((root/'linear-image-checkpoint.bin').exists())

    def test_invalid_readback_shape_padding_and_overflow(self):
        for images,gap,direction,z,counts,step in (
                ([0.]*7,[1.,1.],[1.,1.],[0.,0.],[1,1,1],1e-8),
                ([0.]*8,[1.,1.],[1.,1.],[-1.,0.],[1,1,1],1e-8),
                ([-1e200]*6+[-1.,-1.],[1.,1.],[1.,1.],[0.,0.],[1,1,1],1e-8)):
            with self.assertRaises(ValueError):corrected_states(images,gap,direction,z,counts,step)
        images=[0.]*16;images[1]=.1
        with self.assertRaisesRegex(ValueError,'padding'):
            corrected_states(images,[1.,0.,1.,1.],[1.,0.,1.,1.],[0.]*4,[1,2,2],1e-8)
