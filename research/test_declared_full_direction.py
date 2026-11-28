"""Declared direction: same map arithmetic, stale-state rejection, exact restart."""
import math
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

from test_full_map_checkpoint import STUBS, MAIN


class DeclaredFullDirectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('gfortran')
        if not compiler:
            raise AssertionError('Native direction fixture compiler required')
        cls.build = tempfile.TemporaryDirectory(); cls.addClassCleanup(cls.build.cleanup)
        research = Path(__file__).resolve().parent; cls.executables = {}
        for name in ('fixed', 'declared'):
            root = Path(cls.build.name)/name; root.mkdir()
            (root/'stubs.f90').write_text(STUBS); (root/'main.f90').write_text(MAIN)
            sources = [root/'stubs.f90', research/'nonlinear_tile_apply.f90',
                       research/'portable_gap/linear_image_checkpoint.f90', research/'full_map_checkpoint.f90']
            sources += ([research/'declared_full_direction.f90', research/'full_nonlinear_direction_probe.f90']
                        if name == 'declared' else [research/'full_nonlinear_checkpoint_probe.f90'])
            exe = root/'fixture.x'
            subprocess.run([compiler, '-O2', '-ffp-contract=off', '-ffree-line-length-none', '-fcheck=all',
                            *map(str,sources), str(root/'main.f90'), '-lblas', '-o', str(exe)],
                           cwd=root, check=True, capture_output=True)
            cls.executables[name] = exe

    def stage(self, root, stop=67, previous='-', completed=0):
        root.mkdir(exist_ok=True)
        context = 'a'*64
        (root/'seed-control.in').write_text(str(root)+'\n'+context+'\n')
        (root/'direction-state.meta').write_text(f'declared-full-map-direction-v1\n67 71 71\n1000\n{context}\n')
        (root/'full-map-segment.in').write_text(f'ordered-full-map-control-v1\n{context}\n{previous}\n{completed} {stop}\nsegment\n')
        gap = [0.]*142; direction = [0.]*142
        for g,count in enumerate((67,71)):
            for j in range(count):
                x = (j+1-17)*.001
                gap[g*71+j] = .0001 if j != 16 else 0.
                direction[g*71+j] = (1-2*g)/math.sqrt(1+(x/.01)**2)
        (root/'direction-state.bin').write_bytes(struct.pack('<284d',*gap,*direction))

    def run_native(self, root, variant='declared'):
        return subprocess.run([str(self.executables[variant])], cwd=root, capture_output=True, text=True)

    def test_fixed_direction_equivalence_and_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for name in ('fixed','declared'):
                root = base/name; self.stage(root)
                r = self.run_native(root, name); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            expected = (base/'fixed/full-map.bin').read_bytes()
            self.assertEqual((base/'declared/full-map.bin').read_bytes(), expected)
            first = base/'first'; self.stage(first,32)
            self.assertEqual(self.run_native(first).returncode,0)
            last = base/'last'; self.stage(last,67,first,32)
            r = self.run_native(last); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            self.assertEqual((last/'full-map.bin').read_bytes(),expected)
            changed = base/'changed'; self.stage(changed,67,first,32)
            data = list(struct.unpack('<284d',(changed/'direction-state.bin').read_bytes()))
            data[142] *= .9
            (changed/'direction-state.bin').write_bytes(struct.pack('<284d',*data))
            self.assertNotEqual(self.run_native(changed).returncode,0)
            self.assertFalse((changed/'full-map.bin').exists())

    def test_stale_context_candidate_shape_padding_and_nonfinite(self):
        cases = ('beta','context','counts','trailing','truncated','candidate','signedzero','nan','padding','zero','norm')
        with tempfile.TemporaryDirectory() as directory:
            for case in cases:
                with self.subTest(case=case):
                    root = Path(directory)/case; self.stage(root)
                    meta = root/'direction-state.meta'; text = meta.read_text()
                    if case=='beta':meta.write_text(text.replace('1000\n','999\n'))
                    elif case=='context':meta.write_text(text.replace('a'*64,'b'*64))
                    elif case=='counts':meta.write_text(text.replace('67 71 71','66 71 71'))
                    elif case=='trailing':meta.write_text(text+'extra\n')
                    else:
                        p = root/'direction-state.bin'; data = list(struct.unpack('<284d',p.read_bytes()))
                        if case=='truncated':p.write_bytes(p.read_bytes()[:-8])
                        else:
                            if case=='candidate':data[0] *= 1.1
                            elif case=='signedzero':data[16] = -0.
                            elif case=='nan':data[142] = float('nan')
                            elif case=='padding':data[142+67] = .1
                            elif case=='zero':data[142:] = [0.]*142
                            elif case=='norm':data[142+16] = 2.
                            p.write_bytes(struct.pack('<284d',*data))
                    r = self.run_native(root)
                    self.assertNotEqual(r.returncode,0,r.stdout+r.stderr)
                    self.assertFalse((root/'full-map.bin').exists())

    def test_production_variant_retains_frozen_arithmetic(self):
        research = Path(__file__).resolve().parent
        old = (research/'full_nonlinear_checkpoint_probe.f90').read_text()
        new = (research/'full_nonlinear_direction_probe.f90').read_text()
        new = new.replace('! Declared-direction restart variant; original kernel and accumulation order retained.',
                          '! Ordered restart variant of the frozen full Q0 map/Jacobian diagnostic.')
        new = new.replace('  use declared_full_direction, only: load_declared_direction\n','')
        new = new.replace('    call load_declared_direction(direction)\n','')
        new = new.replace('        ! Direction is the explicit candidate-bound input, including both sides.\n',
                          '        ! Different signed sides prevent a symmetry control hiding index errors.\n'
                          '        direction(i,g)=real(3-2*g,dp)/sqrt(1+(xi(i,g)/0.01_dp)**2)\n')
        self.assertEqual(new,old)

    def test_arbitrary_direction_matches_independent_dense_action(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); self.stage(root)
            p = root/'direction-state.bin'; data = list(struct.unpack('<284d',p.read_bytes()))
            direction = [0.]*142; derivative = [0.]*142
            for side, count in enumerate((67,71)):
                for j in range(count):
                    i = side*71+j; x = (j+1-17)*.001; d = data[i]; w = (j+1-5)/1000
                    direction[i] = (-1 if (j+side)%2 else 1)/(j+1)
                    e = math.hypot(x,d); q = math.exp(-1000*e)
                    t, sech = (1-q)/(1+q), 4*q/(1+q)**2
                    derivative[i] = w*1000/4 if e==0 else w/2*((x/e)**2*t/e+500*(d/e)**2*sech)
            p.write_bytes(struct.pack('<284d',*data[:142],*direction))
            run = self.run_native(root); self.assertEqual(run.returncode,0,run.stdout+run.stderr)
            output = struct.unpack('<568d',(root/'full-map.bin').read_bytes())
            self.assertEqual(list(output[284:426]),direction)
            for side,count in enumerate((67,71)):
                for j in range(count):
                    i = side*71+j
                    if side==0:
                        image = math.fsum((100+3*(j+1)-2*(k+1))/97*derivative[71+k]*direction[71+k]
                                          for k in range(71))
                    else:
                        image = math.fsum((200+3*(k+1)-2*(j+1))/97*derivative[k]*direction[k]
                                          for k in range(67))
                    expected = -image/(1.5+(j+1)/100)-direction[i]
                    self.assertAlmostEqual(output[426+i],expected,delta=2e-12+2e-12*abs(expected))
            self.assertTrue(all(v==0 for v in output[426+67:426+71]))
