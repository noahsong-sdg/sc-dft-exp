"""Compile the scalar upstream reproduction independently of Python algebra."""
import pathlib
import shutil
import subprocess
import tempfile
import unittest


class NativeProbeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("gfortran"), "gfortran required")
    def test_compiled_counterexamples(self):
        source = pathlib.Path(__file__).with_name("current_probe.f90")
        with tempfile.TemporaryDirectory(prefix="scdft-current-") as folder:
            executable = str(pathlib.Path(folder) / "probe")
            subprocess.run(["gfortran", "-std=f2008", "-Wall", "-Wextra",
                            "-fcheck=all", "-O0", str(source), "-o", executable],
                           check=True, capture_output=True, text=True)
            result = subprocess.run([executable], check=True, capture_output=True,
                                    text=True)
            rows = [list(map(float, line.split())) for line in result.stdout.splitlines()]
            self.assertEqual(len(rows), 3)
            self.assertLess(rows[0][3], 1e-14)
            self.assertGreater(rows[1][3], .1)
            self.assertGreater(rows[2][3], .99)


if __name__ == "__main__":
    unittest.main()
