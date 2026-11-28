from pathlib import Path
import struct
import tempfile
import unittest

from compact_p_readback import HEADER,checkpoint,qualification
from fetch_public_response_inputs import digest


class CompactPReadbackTest(unittest.TestCase):
    def write(self,root,completed,cpu=(1.,2.)):
        root.mkdir(exist_ok=True)
        (root/'compact-p.meta').write_text(f'{HEADER}\n65 67 3\n{completed}\n'+ 'a'*64+'\n'+' '.join(map(str,cpu))+'\n')
        values=[float(i+1) if i<completed*3 or i>=65*3 else 0. for i in range(132*3)]
        (root/'compact-p.bin').write_bytes(struct.pack('<396d',*values))

    def test_qualification_and_finite_visited_corruption(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.write(root,64);self.write(root/'split',32,(.5,1.))
            (root/'compact-P-qualification.txt').write_text('compact-P-split-qualification-v1; all P bits equal\n'+'a'*64+'\n65 67 3 64\n1 2 1.5 3\n')
            sha=digest(root/'compact-p.bin')
            self.assertTrue(qualification(root,[65,67],3,'a'*64,sha)['accepted_partial_P_bitwise_equal'])
            with (root/'compact-p.bin').open('r+b') as stream:stream.write(struct.pack('<d',9.))
            # Finite visited entries need the accepted content hash, not shape/context alone.
            checkpoint(root,[65,67],3,64,'a'*64)
            with self.assertRaisesRegex(ValueError,'Different accepted'):qualification(root,[65,67],3,'a'*64,sha)

    def test_stale_persisted_metadata_and_binary_invariants(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.write(root,64);meta=root/'compact-p.meta';original=meta.read_text()
            for old,new in ((HEADER,'old-schema'),('65 67 3','65 66 3'),('\n64\n','\n32\n'),('a'*64,'b'*64),('1.0 2.0','1 /'),('1.0 2.0','1e999 2')):
                meta.write_text(original.replace(old,new))
                with self.assertRaises(ValueError):checkpoint(root,[65,67],3,64,'a'*64)
            meta.write_text(original+'extra\n')
            with self.assertRaises(ValueError):checkpoint(root,[65,67],3,64,'a'*64)
            for index,value in ((0,float('nan')),(64*3,1.)):
                self.write(root,64)
                with (root/'compact-p.bin').open('r+b') as stream:stream.seek(8*index);stream.write(struct.pack('<d',value))
                with self.assertRaises(ValueError):checkpoint(root,[65,67],3,64,'a'*64)
            self.write(root,64);(root/'compact-p.bin').write_bytes(b'stale')
            with self.assertRaises(ValueError):checkpoint(root,[65,67],3,64,'a'*64)

    def test_initial_and_final_short_tile(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);self.write(root,65)
            self.assertEqual(checkpoint(root,[65,67],3,65,'a'*64)['completed_left_rows'],65)
            self.write(root,0,(0.,0.))
            with self.assertRaises(ValueError):checkpoint(root,[65,67],3,0,'a'*64)
            (root/'compact-p.bin').write_bytes(bytes(396*8))
            checkpoint(root,[65,67],3,0,'a'*64)
