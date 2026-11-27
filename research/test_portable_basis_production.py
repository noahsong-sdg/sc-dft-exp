from pathlib import Path
import unittest

from portable_basis_production import interval


class ProductionTraversalTest(unittest.TestCase):
    def test_production_contraction_is_identical_to_qualified_source(self):
        root = Path(__file__).parent/'portable_gap'
        def contraction(name):
            text = (root/name).read_text()
            return text[text.index('  subroutine accumulate('):]
        self.assertEqual(contraction('basis_sweep_driver.f90'),contraction('basis_production_driver.f90'))

    def test_contiguous_tile_boundaries_and_registered_chunk_sizes(self):
        for first,last,previous in ((1,16384,None),(16385,32768,'prior'),(32769,49152,'prior'),(49153,66867,'prior')):
            interval(first,last,previous)
        for first,last,previous in ((1,16384,'prior'),(16385,32768,None),(2,64,'prior'),(1,33,None),(1,32768,None),(49153,66868,'prior')):
            with self.subTest(first=first,last=last), self.assertRaises(ValueError):
                interval(first,last,previous)


class ProductionParentTest(unittest.TestCase):
    def test_certified_parent_rejects_changed_payload_and_inherited_input(self):
        from array import array
        import json
        import tempfile
        from fetch_public_response_inputs import digest
        from portable_basis_production import certified_parent
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);(root/'results/basissplit').mkdir(parents=True)
            (root/'linear-image-checkpoint.meta').write_text(
                'ordered-linear-image-checkpoint-v1; unnormalized partial sums\n'+'a'*64+'\n4 5 5 2 2\n12.34\n')
            binary = root/'linear-image-checkpoint.bin'
            original = array('d',[0.]*20).tobytes();binary.write_bytes(original)
            (root/'basis-sweep.x').write_text('fixture')
            (root/'results/basissplit/receipt.json').write_text('{}')
            source = root/'input.dat';source.write_text('original')
            (root/'run-manifest.json').write_text(json.dumps(dict(context_sha256='a'*64,files=[
                dict(path=str(source),bytes=source.stat().st_size,sha256=digest(source))])))
            paths = {'manifest_sha256':'run-manifest.json','receipt_sha256':'results/basissplit/receipt.json',
                'checkpoint_sha256':'linear-image-checkpoint.bin','metadata_sha256':'linear-image-checkpoint.meta',
                'executable_sha256':'basis-sweep.x'}
            result = {key:digest(root/name) for key,name in paths.items()}
            result.update(status='PASS',split_qualification_passed=True,
                checkpoint=dict(context='a'*64,counts=[4,5,5,2],completed=2,beta=12.34))
            (root/'basis-split-result.json').write_text(json.dumps(result))
            self.assertEqual(certified_parent(root,True)[1]['completed'],2)
            binary.write_bytes(original[:-8])
            with self.assertRaisesRegex(ValueError,'Changed certified'):
                certified_parent(root,True)
            binary.write_bytes(original);source.write_text('modified')
            with self.assertRaisesRegex(ValueError,'Changed declared'):
                certified_parent(root,True)


class ProductionBuildOrderTest(unittest.TestCase):
    def test_driver_build_waits_for_imported_modules(self):
        import shutil
        import subprocess
        import tempfile
        # Exercise the actual make rule with isolated prerequisite fixtures.
        make = shutil.which('make')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);sources = root/'portable_gap';sources.mkdir()
            (sources/'basis_compile.mk').write_text('MPIF90 = echo compile\nFF =\n')
            (sources/'basis_production_driver.f90').touch()
            (sources/'linear_image_checkpoint.f90').touch()
            for name in ('block_linear_operator.o','native_state_io.o','saved_coulomb.o'):
                (root/name).touch()
            (root/'prerequisites.mk').write_text('tc_native_oracle.o tc_subspace.o:\n\t@echo module-$@\n')
            actual = Path(__file__).resolve().parent/'portable_gap/basis_production.mk'
            result = subprocess.run([make,'-n','-f',str(actual),'-f',str(root/'prerequisites.mk'),
                'RESEARCH='+str(root),'basis_production_driver.o'],cwd=root,text=True,capture_output=True,check=True)
            lines = result.stdout.splitlines()
            driver = next(i for i,line in enumerate(lines) if 'basis_production_driver.f90' in line)
            for module in ('tc_native_oracle.o','tc_subspace.o'):
                self.assertLess(next(i for i,line in enumerate(lines) if 'module-'+module in line),driver)
