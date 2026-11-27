import hashlib
import io
import os
import re
import shutil
import subprocess
from pathlib import Path
import tarfile
import tempfile
import unittest

from build_public_response import archive_file, patch_build_rules, unpack, build_environment, export_required_tetra_interfaces, export_required_elph_interface, enlarge_point_capacity


class PublicResponseBuildTests(unittest.TestCase):
    def test_consistent_point_storage_module_rebuild_supports_48cubed(self):
        source = ('module parameters\nimplicit none\n'
                  '  INTEGER, PARAMETER :: npk = 40000\n'
                  'integer, parameter :: ntypx=10\nend module\n')
        candidate = enlarge_point_capacity(source, 300000)
        self.assertEqual(candidate.replace('300000', '40000'), source)
        for stale in (candidate, source+source):
            with self.assertRaisesRegex(ValueError, 'declaration changed'):
                enlarge_point_capacity(stale, 300000)
        for invalid in (40000, 32768, 300000., True):
            with self.assertRaisesRegex(ValueError, 'integer above40000'):
                enlarge_point_capacity(source, invalid)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); module = root/'parameters.f90'; client = root/'client.f90'
            client.write_text('program client\nuse parameters\n'
                              'real(8)::xk(3,npk)\ninteger::n\nn=48**3\n'
                              'xk(:,n)=1\nif(any(xk(:,n)/=1)) stop 2\nend program\n')
            command = ['gfortran', '-fcheck=bounds', str(module), str(client), '-o', str(root/'test')]
            module.write_text(source)
            subprocess.run(command, cwd=root, check=True, capture_output=True)
            failed = subprocess.run([str(root/'test')], capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('Fortran runtime error', failed.stderr)
            self.assertIn('110592', failed.stderr)
            self.assertIn('40000', failed.stderr)
            module.write_text(candidate)
            subprocess.run(command, cwd=root, check=True, capture_output=True)
            subprocess.run([str(root/'test')], check=True)

    def test_pinned_archive_cache_rejects_stale_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root/'qe.tar.gz'; path.write_bytes(b'known')
            item = dict(url='https://example.invalid/unused', bytes=5,
                        sha256=hashlib.sha256(b'known').hexdigest())
            self.assertEqual(archive_file('qe', item, root), path)
            path.write_bytes(b'stale')
            with self.assertRaisesRegex(ValueError, 'preserved'):
                archive_file('qe', item, root)
            self.assertEqual(path.read_bytes(), b'stale')

    def test_archive_build_patch_preserves_arithmetic_and_unrelated_recipes(self):
        with tempfile.TemporaryDirectory() as folder:
            qe = Path(folder)
            (qe/'install').mkdir(); (qe/'SCTK/src').mkdir(parents=True)
            (qe/'PHonon/PH').mkdir(parents=True)
            (qe/'PHonon/PH/elph_tetra_mod.f90').write_text(
                '  &      elph_tetra_lambda, elph_tetra_gamma\ncontains\nelph body\n')
            (qe/'LR_Modules').mkdir()
            (qe/'LR_Modules/dfpt_tetra_mod.f90').write_text(
                '            dfpt_tetra_main, dfpt_tetra_linit\ncontains\nscientific body\n')
            utils = qe/'install/install_utils'
            utils.write_text('before\ndefine update_submodule\n old git step\nendef\nafter\n')
            make = qe/'SCTK/src/Makefile'
            make.write_text('objects\nhash:\n old hash step\n\nsctk.x : objects\n link\n')
            (qe/'SCTK/src/sctk_write_hash').write_text('commit = HASH\n')
            kernel = qe/'SCTK/src/kernel.f90'; kernel.write_text('scientific computation\n')
            before = kernel.read_bytes()
            change = patch_build_rules(qe, {'sctk': {'commit': 'a'*40}})
            self.assertIn('SC_DFT_SOURCE_PIN', utils.read_text())
            self.assertTrue(utils.read_text().startswith('before\n'))
            self.assertTrue(utils.read_text().endswith('after\n'))
            self.assertIn('sctk.x : objects\n link', make.read_text())
            self.assertEqual(kernel.read_bytes(), before)
            self.assertTrue((qe/'LR_Modules/dfpt_tetra_mod.f90').read_text().endswith(
                'contains\nscientific body\n'))
            self.assertEqual((qe/'SCTK/src/sctk_write_hash.f90').read_text(), 'commit = '+'a'*40+'\n')
            self.assertIn('- old git step', change)

    def test_required_private_tetra_interfaces_compile_after_export_only_patch(self):
        names = ['dfpt_tetra_lindhard_'+suffix for suffix in
                 ('1234', '1231', '1233', '1221', '1222', '1211')]
        source = ('module dfpt_tetra_mod\nimplicit none\nprivate\n'
                  'public :: dfpt_tetra_beta, dfpt_tetra_ttheta, dfpt_tetra_delta, &\n'
                  '            dfpt_tetra_main, dfpt_tetra_linit\n'
                  'integer :: dfpt_tetra_beta,dfpt_tetra_ttheta,dfpt_tetra_delta,dfpt_tetra_main,dfpt_tetra_linit\n'
                  'contains\n'+''.join('integer function '+name+'()\n'+name+'=7\nend function\n'
                                        for name in names)+'end module\n')
        patched = export_required_tetra_interfaces(source)
        self.assertEqual(source.split('contains')[1], patched.split('contains')[1])
        with self.assertRaisesRegex(ValueError, 'interface changed'):
            export_required_tetra_interfaces(patched)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            client = root/'client.f90'
            client.write_text('program client\nuse dfpt_tetra_mod,only:'+names[0]+
                              '\nif ('+names[0]+'()/=7) stop 1\nend program\n')
            module = root/'module.f90'
            module.write_text(source)
            failed = subprocess.run(['gfortran', str(module), str(client), '-o', str(root/'old')],
                                    cwd=root, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('not found in module', failed.stderr)
            module.write_text(patched)
            subprocess.run(['gfortran', str(module), str(client), '-o', str(root/'fixed')],
                           cwd=root, check=True, capture_output=True)
            subprocess.run([str(root/'fixed')], check=True)

    def test_private_elph_helper_is_exported_without_changing_its_body(self):
        source = ('module elph_tetra_mod\nimplicit none\nprivate\n'
                  'public :: &\n  &      elph_tetra_lambda, elph_tetra_gamma\n'
                  'integer :: elph_tetra_lambda,elph_tetra_gamma\ncontains\n'
                  'subroutine elph_tetra_delta1(i)\ninteger,intent(out)::i\ni=9\nend subroutine\nend module\n')
        patched = export_required_elph_interface(source)
        self.assertEqual(source.split('contains')[1], patched.split('contains')[1])
        with self.assertRaisesRegex(ValueError, 'interface changed'):
            export_required_elph_interface(patched)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); module = root/'module.f90'; client = root/'client.f90'
            client.write_text('program client\nuse elph_tetra_mod,only:elph_tetra_delta1\n'
                              'integer::i\ncall elph_tetra_delta1(i)\nif(i/=9) stop 1\nend program\n')
            module.write_text(source)
            failed = subprocess.run(['gfortran', str(module), str(client), '-o', str(root/'old')],
                                    cwd=root, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('not found in module', failed.stderr)
            module.write_text(patched)
            subprocess.run(['gfortran', str(module), str(client), '-o', str(root/'fixed')],
                           cwd=root, check=True, capture_output=True)
            subprocess.run([str(root/'fixed')], check=True)

    def test_policy_environment_reaches_actual_nested_cmake_project(self):
        cmake = shutil.which('cmake')
        self.assertIsNotNone(cmake)
        version = subprocess.run([cmake, '--version'], capture_output=True, text=True, check=True).stdout
        major = int(re.search(r'version (\d+)', version).group(1))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); (root/'inner').mkdir()
            (root/'CMakeLists.txt').write_text(
                'cmake_minimum_required(VERSION 3.5)\nproject(Outer C)\n'
                'try_compile(OK "${CMAKE_BINARY_DIR}/nested" "${CMAKE_SOURCE_DIR}/inner" Inner target)\n'
                'if(NOT OK)\nmessage(FATAL_ERROR "nested probe failed")\nendif()\n')
            (root/'inner/CMakeLists.txt').write_text(
                'cmake_minimum_required(VERSION 3.2)\nproject(Inner C)\nadd_executable(target main.c)\n')
            (root/'inner/main.c').write_text('int main(void){return 0;}\n')
            command = [cmake, '-S', str(root), '-DCMAKE_POLICY_VERSION_MINIMUM=3.5']
            if major >= 4:
                env = {k:v for k,v in os.environ.items() if k != 'CMAKE_POLICY_VERSION_MINIMUM'}
                failed = subprocess.run(command+['-B', str(root/'old')], env=env, capture_output=True, text=True)
                self.assertNotEqual(failed.returncode, 0)
                self.assertIn('Compatibility with CMake < 3.5', failed.stdout+failed.stderr)
            passed = subprocess.run(command+['-B', str(root/'fixed')], env=build_environment(), capture_output=True, text=True)
            self.assertEqual(passed.returncode, 0, passed.stdout+passed.stderr)

    @unittest.skipUnless(hasattr(tarfile, 'data_filter'), 'Safe archive extraction requires Python>=3.12')
    def test_fresh_extract_and_nonempty_placeholder_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            archive = root/'source.tar.gz'
            with tarfile.open(archive, 'w:gz') as output:
                entry = tarfile.TarInfo('source/file.f90'); entry.size = 4
                output.addfile(entry, io.BytesIO(b'code'))
            unpack(archive, root/'fresh')
            self.assertEqual((root/'fresh/file.f90').read_bytes(), b'code')
            with self.assertRaises(OSError):
                unpack(archive, root/'fresh')
            self.assertEqual((root/'fresh/file.f90').read_bytes(), b'code')


if __name__ == '__main__':
    unittest.main()
