from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest


PROGRAM = '''program fixture
use iso_fortran_env,only:real64,int64
use linear_image_checkpoint
implicit none
real(real64)::values(5,2,2),baseline(5,2,2)
integer::i,j,k
character(20)::mode
call get_command_argument(1,mode)
values=0
if(mode=='write')then
 values(:2,1,1)=[.1_real64,.2_real64];values(:,2,:)=.3_real64
 call write_linear_image_checkpoint('.',repeat('a',64),[4,5,5,2],12.34_real64,2,values)
else if(mode=='read')then
 call read_linear_image_checkpoint('.',repeat('a',64),[4,5,5,2],12.34_real64,2,values)
else if(mode=='split')then
 call accumulate(1,4)
 baseline=values;values=0
 call accumulate(1,2)
 call write_linear_image_checkpoint('.',repeat('a',64),[4,5,5,2],12.34_real64,2,values)
 values=0
 call read_linear_image_checkpoint('.',repeat('a',64),[4,5,5,2],12.34_real64,2,values)
 call accumulate(3,4)
 if(any(transfer(values,[0_int64],20)/=transfer(baseline,[0_int64],20)))error stop 'split mismatch'
end if
print *,'PASS'
contains
subroutine accumulate(first,last)
integer,intent(in)::first,last
do i=first,last
 do k=1,2
 do j=1,5
  values(i,1,k)=values(i,1,k)+real(i*j*k,real64)/7
  values(j,2,k)=values(j,2,k)+real(i*j*k,real64)/13
 end do
 end do
end do
end subroutine
end program
'''


class LinearImageCheckpointTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which('gfortran')
        if not compiler:
            raise RuntimeError('Native checkpoint regression requires gfortran')
        cls.workspace = tempfile.TemporaryDirectory()
        cls.build = Path(cls.workspace.name)
        fixture = cls.build/'fixture.f90'; fixture.write_text(PROGRAM)
        cls.exe = cls.build/'fixture.x'
        source = Path(__file__).parent/'portable_gap/linear_image_checkpoint.f90'
        subprocess.run([compiler,'-O2','-fcheck=all','-ffree-line-length-none',
            str(source),str(fixture),'-o',str(cls.exe)], cwd=cls.build, check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def run_fixture(self, root, mode):
        return subprocess.run([str(self.exe), mode], cwd=root, text=True, capture_output=True)

    def test_split_accumulation_retains_bitwise_serial_order(self):
        with tempfile.TemporaryDirectory() as folder:
            result = self.run_fixture(folder, 'split')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('PASS', result.stdout)

    def test_rejects_stale_context_rows_temperature_schema_and_payload(self):
        for mutation in ('context','rows','temperature','schema','trailing','shape','nan','future_row','columns','padding'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                self.assertEqual(self.run_fixture(root, 'write').returncode, 0)
                self.assertEqual(self.run_fixture(root, 'read').returncode, 0)
                meta = root/'linear-image-checkpoint.meta'; lines = meta.read_text().splitlines()
                binary = root/'linear-image-checkpoint.bin'; payload = bytearray(binary.read_bytes())
                if mutation == 'columns': lines[2] = '4 5 5 1 2'
                if mutation == 'padding': struct.pack_into('<d', payload, 14*8, 1.)
                if mutation == 'context': lines[1] = 'b'*64
                if mutation == 'rows': lines[2] = '4 5 5 2 3'
                if mutation == 'temperature': lines[3] = '100'
                if mutation == 'schema': lines[0] = 'old-checkpoint-v0'
                if mutation == 'trailing': lines.append('unexpected')
                if mutation == 'shape': payload = payload[:-1]
                if mutation == 'nan': struct.pack_into('<d', payload, 0, float('nan'))
                if mutation == 'future_row': struct.pack_into('<d', payload, 16, 1.)
                meta.write_text('\n'.join(lines)+'\n'); binary.write_bytes(payload)
                result = self.run_fixture(root, 'read')
                self.assertNotEqual(result.returncode, 0, mutation)
