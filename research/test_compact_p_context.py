from pathlib import Path
import shutil
import tempfile
import unittest

from compact_p_context import fingerprint


class CompactPContextTest(unittest.TestCase):
    def fixture(self,base):
        names=('q','state','exe','blas')
        for name,size in zip(names,(80,200,32,16)):(base/name).write_bytes(b'0'*size)
        return ([2,3,3,2],[100,10,50],1.25,'a'*64,'b'*64,*(base/name for name in names))

    def test_all_P_inputs_change_identity_but_UW_and_relocation_do_not(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);args=self.fixture(base);original,description=fingerprint(*args)
            self.assertEqual(description['beta_binary64_hex'],1.25.hex())
            for name in ('q','state','exe','blas'):
                path=base/name;before=path.read_bytes();path.write_bytes(b'x'+before[1:])
                self.assertNotEqual(fingerprint(*args)[0],original);path.write_bytes(before)
            (base/'u').write_bytes(b'changed U');(base/'w').write_bytes(b'changed W')
            self.assertEqual(fingerprint(*args)[0],original)
            other=base/'other';other.mkdir()
            for name in ('q','state','exe','blas'):shutil.copy2(base/name,other/name)
            relocated=(*args[:5],*(other/name for name in ('q','state','exe','blas')))
            self.assertEqual(fingerprint(*relocated)[0],original)
            for index,value in ((1,[100,11,50]),(2,1.5),(3,'c'*64),(4,'d'*64)):
                changed=list(args);changed[index]=value;self.assertNotEqual(fingerprint(*changed)[0],original)

    def test_stale_shapes_and_invalid_context_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);args=self.fixture(base)
            for index,value in ((0,[2,3,4,2]),(0,[2,3,3,65]),(1,[100,10,0]),(2,float('nan')),(3,'bad')):
                changed=list(args);changed[index]=value
                with self.assertRaises(ValueError):fingerprint(*changed)
            (base/'q').write_bytes(b'stale')
            with self.assertRaises(ValueError):fingerprint(*args)
