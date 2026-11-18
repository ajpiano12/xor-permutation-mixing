import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import tempfile
import unittest

from classify_mixing import classify


class ParallelMixingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("cc")
        if not compiler:
            raise unittest.SkipTest("a C compiler with OpenMP is required")
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.binary = Path(cls.temp.name) / "parallel_mixing"
        # A missing OpenMP toolchain is optional. Compilation errors in the
        # classifier itself should still fail on systems with OpenMP.
        probe = subprocess.run(
            [compiler, "-x", "c", "-fopenmp", "-", "-o", str(cls.binary)],
            input="#include <omp.h>\nint main(void) { return omp_get_num_threads() == 0; }",
            capture_output=True, text=True,
        )
        if probe.returncode:
            raise unittest.SkipTest("OpenMP toolchain is unavailable")
        source = Path(__file__).resolve().parents[1] / "parallel_mixing.c"
        subprocess.run([compiler, "-std=c11", "-O2", "-fopenmp", str(source), "-o", str(cls.binary)],
                       check=True)

    def run_native(self, *args, stdin=None):
        return subprocess.run([str(self.binary), *args], input=stdin, capture_output=True,
                              text=True, env={**os.environ, "OMP_DYNAMIC": "FALSE"})

    def compare(self, p, threads):
        wanted = classify(p)
        completed = self.run_native("-j", str(threads), "--witness", "--file", "-",
                                    stdin=", ".join(map(str, p)))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        actual = json.loads(completed.stdout)
        self.assertEqual((actual["bits"], actual["status"], actual["period"], actual["mixes"]),
                         (len(p).bit_length() - 1, wanted.status, wanted.period, wanted.status == "mixing"))
        if wanted.closed_set:
            self.assertEqual(set(actual["closed_set"]), set(wanted.closed_set))
        if wanted.cyclic_classes:
            self.assertEqual(actual["cyclic_classes"], list(map(list, wanted.cyclic_classes)))

    def test_native_agreement(self):
        rng = random.Random(12833)
        tables = [[1, 0], [0, 2, 4, 6, 3, 1, 7, 5]]
        for n in (4, 8, 16, 64, 256):
            tables += [rng.sample(range(n), n) for _ in range(4)]
            # Preserve the high-bit halves, so the root component can be large.
            tables.append(rng.sample(range(n // 2), n // 2) + rng.sample(range(n // 2, n), n // 2))
        for threads in (1, 4):
            for p in tables:
                with self.subTest(threads=threads, permutation=p):
                    self.compare(p, threads)

    def test_file_and_table_validation(self):
        path = Path(self.temp.name) / "table.txt"
        path.write_text("0x00, 01\n0x02 3\n")
        self.assertEqual(json.loads(self.run_native("--file", str(path)).stdout)["status"], "disconnected")
        for args in (("0", "0"), ("0x1", "0", "2"), ("0", "2"), ("-j", "0", "0", "1")):
            self.assertNotEqual(self.run_native(*args).returncode, 0)
