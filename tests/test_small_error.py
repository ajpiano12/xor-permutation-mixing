"""Check tiny distance cutoffs against a closed-form inverse walk."""
import unittest
from fractions import Fraction
from itertools import permutations

try:
    from higher_census import measure, normalized_starts
    from research.small_error_census import verify_three_bit_structure
except ModuleNotFoundError as exc:
    if exc.name != "numpy":
        raise
    measure = None


@unittest.skipIf(measure is None, "requires NumPy from the four-bit extra")
class SmallErrorTests(unittest.TestCase):
    def test_inverse_pair_thresholds(self):
        p = (0, 1, 5, 6, 7, 2, 3, 4)
        shapes = [bytes(s) for s in permutations(range(1, 8), 1)]
        ids = {s: i for i, s in enumerate(shapes)}
        targets = tuple(1 << k for k in (3, 16, 32, 64, 128))
        result = measure(p, shapes, ids, normalized_starts(2, ids), targets)
        # d_(2j) = (6/7) 8^-j and d_(2j+1) = (3/7) 8^-j at difference steps.
        expected = []
        for target in targets:
            steps = 0
            while Fraction(3 if steps % 2 else 6, 7 * 8 ** (steps // 2)) > Fraction(1, target):
                steps += 1
            expected.append(steps + 1)
        self.assertEqual(result, ("mixing", 1, tuple(expected)))

    def test_signed_orientation_and_fast_family(self):
        verify_three_bit_structure()
