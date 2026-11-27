"""Actual seed loader: explicit vector reuse and persisted-context rejection."""
from pathlib import Path
import math
import shutil
import struct
import subprocess
import tempfile
import unittest


class GapSeedIOTest(unittest.TestCase):
    def test_explicit_vector_and_stale_or_invalid_seed(self):
        compiler=shutil.which('gfortran')
        self.assertIsNotNone(compiler)
        source='''module kinds
 use iso_fortran_env,only:dp=>real64
end module
module sctk_val
 use kinds
 integer::ngap(2)=[1,2],ngapmax=2,nx=100,nmf=10,ne=50
 real(dp)::beta=19613.355577892344_dp,xi(2,2)=0,dk(2,2),emin=1.e-7_dp
end module
program test
 use kinds
 use sctk_val
 use gap_seed_io
 real(dp)::gap(2,2)
 integer::u
 dk=1;dk(2,1)=0
 call load_gap_seed('/retained/prepare',gap)
 open(newunit=u,file='readback.bin',access='stream',form='unformatted',status='replace')
 write(u)gap
 close(u)
end program
'''
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'test.f90').write_text(source.split('program test')[0])
            (root/'main.f90').write_text('program test'+source.split('program test')[1])
            subprocess.run([compiler,'-O2','-fcheck=all','test.f90',
                            str(Path(__file__).with_name('gap_seed_io.f90')),'main.f90','-o','test'],
                           cwd=root,check=True)
            context='a'*64
            (root/'seed-control.in').write_text('.\n'+context+'\n')
            metadata=('gap-seed-v1; binary64 Fortran order\n1 2 2 100 10 50\n'
                      '19613.355577892344\n/retained/prepare\n'+context+'\n')
            values=[1e-5,0,1.1e-5,1.2e-5]
            payload=struct.pack('<4d',*values)
            (root/'gap-seed.meta').write_text(metadata)
            (root/'gap-seed.bin').write_bytes(payload)
            subprocess.run([str(root/'test')],cwd=root,check=True,capture_output=True)
            self.assertEqual((root/'readback.bin').read_bytes(),payload)
            for bad in (metadata.replace('seed-v1','seed-v0'),metadata.replace('100 10','99 10'),
                        metadata.replace('19613.355577892344','19612'),metadata.replace('/retained/','/other/'),
                        metadata.replace(context,'b'*64),metadata+'trailing\n'):
                (root/'gap-seed.meta').write_text(bad)
                result=subprocess.run([str(root/'test')],cwd=root,capture_output=True)
                self.assertNotEqual(result.returncode,0)
            (root/'gap-seed.meta').write_text(metadata)
            for bad in (payload[:-1],struct.pack('<4d',math.nan,*values[1:]),
                        struct.pack('<4d',values[0],1,*values[2:]),
                        struct.pack('<4d',0,*values[1:]),struct.pack('<4d',-1e-5,*values[1:])):
                (root/'gap-seed.bin').write_bytes(bad)
                result=subprocess.run([str(root/'test')],cwd=root,capture_output=True)
                self.assertNotEqual(result.returncode,0)


if __name__=='__main__':
    unittest.main()
