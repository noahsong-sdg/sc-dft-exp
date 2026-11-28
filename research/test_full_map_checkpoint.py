"""Execute persisted full-map segments against the frozen owning routine."""
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest


STUBS = '''module kinds
use iso_fortran_env,only:dp=>real64
end module
module sctk_val
use kinds
integer::ngap(2)=[67,71],ngapmax=71
real(dp)::delta(71,2),xi(71,2),dk(71,2),beta=1000,Z(71,2)
end module
module slab_operator
contains
subroutine clear_slab()
end subroutine
end module
module cached_kel
contains
subroutine reset_kel_cache()
end subroutine
end module
module cached_phonon
contains
subroutine reset_phonon_cache()
end subroutine
end module
module tiled_operator
use kinds
contains
subroutine build_tile(first,last,block,width)
integer,intent(in)::first,last,width
real(dp),intent(out)::block(71,first:last,2)
integer::i,j,g
do g=1,2
do i=first,last
do j=1,71
 block(j,i,g)=real(100*g+3*i-2*j,dp)/97
end do
end do
end do
end subroutine
end module
'''

MAIN = '''program fixture
use kinds
use sctk_val
use full_nonlinear_probe
implicit none
real(dp)::chi(71,2),energy
integer::i,g
character(20)::change
call get_command_argument(1,change)
delta=0;xi=0;dk=0;Z=0;chi=0
do g=1,2
do i=1,ngap(g)
 xi(i,g)=real(i-17,dp)*.001_dp
 delta(i,g)=.0001_dp
 if(i==17)delta(i,g)=0
 dk(i,g)=real(i-5,dp)/1000
 Z(i,g)=.5_dp+real(i,dp)/100
 energy=hypot(xi(i,g),delta(i,g))
 if(energy>0)chi(i,g)=dk(i,g)*delta(i,g)/2/energy*tanh(beta*energy/2)
end do
end do
if(change=='gap')delta(1,1)=delta(1,1)*1.1_dp
if(change=='xi')xi(1,1)=xi(1,1)*1.1_dp
if(change=='dk')dk(1,1)=dk(1,1)*1.1_dp
if(change=='Z')Z(1,1)=Z(1,1)*1.1_dp
if(change=='weights')chi(1,1)=chi(1,1)*1.1_dp
if(change=='temperature')beta=999
call run_full_map(chi)
print *,'FIXTURE_PASS'
end program
'''


class FullMapCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('gfortran')
        if not compiler:
            raise RuntimeError('Full-map checkpoint regression requires gfortran')
        cls.workspace = tempfile.TemporaryDirectory()
        cls.build = Path(cls.workspace.name)
        research = Path(__file__).parent
        cls.executables = {}
        for variant in ('original', 'checkpoint'):
            root = cls.build/variant
            root.mkdir()
            (root/'stubs.f90').write_text(STUBS)
            (root/'main.f90').write_text(MAIN)
            sources = [root/'stubs.f90', research/'nonlinear_tile_apply.f90']
            if variant == 'checkpoint':
                sources += [research/'portable_gap/linear_image_checkpoint.f90',
                            research/'full_map_checkpoint.f90', research/'full_nonlinear_checkpoint_probe.f90']
            else:
                sources += [research/'full_nonlinear_probe.f90']
            exe = root/'fixture.x'
            subprocess.run([compiler, '-O2', '-ffp-contract=off', '-fcheck=all',
                            '-ffree-line-length-none', *map(str, sources), str(root/'main.f90'),
                            '-lblas', '-o', str(exe)], cwd=root, check=True, capture_output=True)
            cls.executables[variant] = exe

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def control(self, root, previous='-', completed=0, stop=67, context='a'*64, mode='segment'):
        root.mkdir(exist_ok=True)
        (root/'full-map-segment.in').write_text(
            f'ordered-full-map-control-v1\n{context}\n{previous}\n{completed} {stop}\n{mode}\n')

    def run_fixture(self, root, variant='checkpoint', change=''):
        return subprocess.run([str(self.executables[variant]), change], cwd=root,
                              text=True, capture_output=True)

    def require_pass(self, root, variant='checkpoint'):
        run = self.run_fixture(root, variant)
        self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
        return run

    def test_restart_final_output_matches_original_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            original = root/'original'; original.mkdir()
            self.require_pass(original, 'original')
            continuous = root/'continuous'; self.control(continuous)
            self.require_pass(continuous)
            first = root/'first'; self.control(first, stop=32)
            self.require_pass(first)
            self.assertFalse((first/'full-map.bin').exists())
            second = root/'second'; self.control(second, first, 32, 64)
            self.require_pass(second)
            final = root/'final'; self.control(final, second, 64, 67)
            self.require_pass(final)
            expected = (original/'full-map.bin').read_bytes()
            self.assertEqual((continuous/'full-map.bin').read_bytes(), expected)
            self.assertEqual((final/'full-map.bin').read_bytes(), expected)
            # Only kernel CPU time may differ in the summary.
            reference = (original/'full-map.txt').read_text().splitlines()
            for directory in (continuous, final):
                actual = (directory/'full-map.txt').read_text().splitlines()
                self.assertEqual(actual[:2]+actual[3:], reference[:2]+reference[3:])
                controls, wanted = actual[2].split(), reference[2].split()
                self.assertEqual(controls[:2]+controls[3:], wanted[:2]+wanted[3:])

    def test_internal_actual_path_split_qualification(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.control(root, stop=64, mode='qualify')
            (root/'split').mkdir()
            result = self.require_pass(root)
            self.assertIn('FULL_MAP_SPLIT_BITWISE_PASS', result.stdout)
            self.assertFalse((root/'full-map.bin').exists())

    def test_changed_active_state_is_rejected_before_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            first = root/'first'; self.control(first, stop=32)
            self.require_pass(first)
            for change in ('gap', 'xi', 'dk', 'Z', 'weights', 'temperature'):
                with self.subTest(change=change):
                    target = root/change; self.control(target, first, 32, 67)
                    self.assertNotEqual(self.run_fixture(target, change=change).returncode, 0)
                    self.assertFalse((target/'full-map.bin').exists())

    def test_reject_stale_persisted_state_and_noncontiguous_controls(self):
        mutations = ('context', 'rows', 'boundary', 'schema', 'state_size', 'state_bits',
                     'image_size', 'nan', 'step', 'error', 'cpu', 'trailing', 'control_trailing')
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                first = root/'first'; self.control(first, stop=32)
                self.require_pass(first)
                target = root/'next'; self.control(target, first, 32, 67)
                meta = first/'full-map-checkpoint.meta'
                lines = meta.read_text().splitlines()
                state = first/'full-map-checkpoint-state.bin'
                image = first/'linear-image-checkpoint.bin'
                if mutation == 'context': self.control(target, first, 32, 67, context='b'*64)
                if mutation == 'rows': self.control(target, first, 0, 67)
                if mutation == 'boundary': self.control(target, first, 32, 33)
                if mutation == 'schema': lines[0] = 'old-state-v0'
                if mutation == 'state_size': state.write_bytes(state.read_bytes()[:-1])
                if mutation == 'state_bits':
                    payload = bytearray(state.read_bytes()); payload[0] ^= 1; state.write_bytes(payload)
                if mutation == 'image_size': image.write_bytes(image.read_bytes()[:-1])
                if mutation == 'nan':
                    payload = bytearray(image.read_bytes()); struct.pack_into('<d', payload, 0, float('nan'))
                    image.write_bytes(payload)
                if mutation in ('step', 'error', 'cpu'):
                    values = lines[1].split()
                    values[{'step': 0, 'error': 1, 'cpu': 2}[mutation]] = '-1'
                    lines[1] = ' '.join(values)
                if mutation == 'trailing': lines.append('unexpected')
                if mutation == 'control_trailing':
                    with (target/'full-map-segment.in').open('a') as out: out.write('unexpected\n')
                meta.write_text('\n'.join(lines)+'\n')
                result = self.run_fixture(target)
                self.assertNotEqual(result.returncode, 0, result.stdout+result.stderr)
                self.assertFalse((target/'full-map.bin').exists())


if __name__ == '__main__':
    unittest.main()
