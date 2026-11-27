import json
from pathlib import Path
import tempfile
import unittest

from build_indexed_mesh_response import build
from fetch_public_response_inputs import digest
from mesh_equivalence_patch import patch


class IndexedMeshParentTest(unittest.TestCase):
    def test_stale_parent_and_source_fail_before_output_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();parent=root/'parent';(parent/'probe').mkdir(parents=True)
            exe=parent/'probe/velocity-moment-probe.x';exe.write_bytes(b'original')
            result=parent/'build-result.json'
            metadata=dict(executable=str(exe),executable_sha256=digest(exe))
            result.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,'capacity-qualified'):
                build(parent,root/'legacy')
            self.assertFalse((root/'legacy').exists())
            metadata['point_capacity']=300000;result.write_text(json.dumps(metadata))
            exe.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'capacity-qualified'):
                build(parent,root/'stale')
            self.assertFalse((root/'stale').exists())
            exe.write_bytes(b'original')
            source=parent/'qe/PW/src/tetra.f90';source.parent.mkdir(parents=True)
            source.write_text('changed upstream routine')
            with self.assertRaisesRegex(ValueError,'pinned QE tetra source'):
                build(parent,root/'changed-source')
            self.assertFalse((root/'changed-source').exists())
            with self.assertRaisesRegex(ValueError,'pinned QE tetra source'):
                patch('SUBROUTINE opt_tetra_init changed')


if __name__=='__main__':
    unittest.main()
