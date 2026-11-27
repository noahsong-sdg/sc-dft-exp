import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch as mock_patch

from build_indexed_mesh_response import build, fourth_geometry
from fetch_public_response_inputs import digest
from mesh_equivalence_patch import patch


class IndexedMeshParentTest(unittest.TestCase):
    def test_explicit_fourth_geometry_rejects_wrong_order_capacity_and_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve();(root/'probe').mkdir()
            source=root/'probe/current_geometry.f90';source.write_text('fourth geometry')
            exe=root/'probe/velocity-moment-probe.x';exe.write_text('fourth executable')
            metadata=dict(velocity_stencil_order=4,curvature_stencil_unchanged=True,
                point_capacity=300000,executable=str(exe),executable_sha256=digest(exe),
                generated_geometry_sha256=digest(source))
            path=root/'build-result.json';path.write_text(json.dumps(metadata))
            self.assertEqual(fourth_geometry(root,300000),(source,path,exe))
            with self.assertRaisesRegex(ValueError,'fourth-order'):
                fourth_geometry(root,110592)
            metadata['velocity_stencil_order']=2;path.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError,'fourth-order'):
                fourth_geometry(root,300000)
            metadata['velocity_stencil_order']=4;path.write_text(json.dumps(metadata))
            parent=root/'valid-parent';(parent/'probe').mkdir(parents=True)
            parent_exe=parent/'probe/velocity-moment-probe.x';parent_exe.write_text('parent')
            (parent/'build-result.json').write_text(json.dumps(dict(point_capacity=300000,
                executable=str(parent_exe),executable_sha256=digest(parent_exe))))
            qe=parent/'qe';(qe/'PW/src').mkdir(parents=True)
            (qe/'PW/src/tetra.f90').write_text('pinned upstream fixture')
            (qe/'make.inc').write_text('make fixture')
            (parent/'fixture.a').write_text('library')
            (parent/'fixture.mod').write_text('module')
            def compile_fixture(command,cwd,**kwargs):
                (cwd/'velocity-moment-probe.x').write_text('combined executable')
            with mock_patch('build_indexed_mesh_response.patch',return_value='indexed fixture'), mock_patch(
                    'build_indexed_mesh_response.subprocess.run',side_effect=compile_fixture):
                built=build(parent,root/'combined',fourth_geometry_build=root)
            self.assertEqual(built['velocity_stencil_order'],4)
            self.assertTrue(built['indexed_mesh_lookup'])
            self.assertFalse(built['numerical_response_qualified'])
            self.assertEqual((root/'combined/probe/current_geometry.f90').read_bytes(),source.read_bytes())
            self.assertEqual(built['generated_geometry_sha256'],digest(source))
            self.assertIn(str(path),[item['path'] for item in built['link_inputs']])
            source.write_text('changed')
            with self.assertRaisesRegex(ValueError,'fourth-order'):
                fourth_geometry(root,300000)
            parent=root/'parent';(parent/'probe').mkdir(parents=True)
            parent_exe=parent/'probe/velocity-moment-probe.x';parent_exe.write_text('parent')
            (parent/'build-result.json').write_text(json.dumps(dict(point_capacity=300000,
                executable=str(parent_exe),executable_sha256=digest(parent_exe))))
            with self.assertRaisesRegex(ValueError,'fourth-order'):
                build(parent,root/'rejected',fourth_geometry_build=root)
            self.assertFalse((root/'rejected').exists())

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
