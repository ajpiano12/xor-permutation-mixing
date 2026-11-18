import unittest
from collections import Counter
from fractions import Fraction
from math import sqrt

from mixing import DEFAULT_THRESHOLDS

try:
    from sample_four_bit import analyze_permutation
except ModuleNotFoundError as exc:
    if exc.name not in {"numpy", "matplotlib"}:
        raise
    raise unittest.SkipTest("Install the four-bit extra to run the sampler tests.") from exc


# Patched inversion in GF(2)[x]/(x^4 + x + 1).
INVERSE = (0, 1, 9, 14, 13, 11, 7, 6, 15, 2, 12, 5, 10, 4, 3, 8)


def direct_difference_distances(permutation, last_round):
    """Follow both cipher outputs with shared keys, starting at (0, a)."""
    pairs = [{(0, a): 1} for a in range(1, 16)]
    distances = []
    for r in range(last_round + 1):
        key_count = 16**r
        worst = 0
        for counts in pairs:
            differences = Counter()
            for (x, y), count in counts.items():
                differences[x ^ y] += count
            deviation = sum(abs(15 * differences[b] - key_count) for b in range(1, 16))
            worst = max(worst, deviation)
        distances.append(Fraction(worst, 30 * key_count))
        if r < last_round:
            next_pairs = []
            for counts in pairs:
                new_counts = Counter()
                for (x, y), count in counts.items():
                    for key in range(16):
                        new_counts[permutation[x ^ key], permutation[y ^ key]] += count
                next_pairs.append(new_counts)
            pairs = next_pairs
    return tuple(distances)


class FourBitTests(unittest.TestCase):
    def test_disconnected_identity_and_connected_fifteen_cycle(self):
        # Multiplication by x in the field above cycles through all 15 differences.
        multiply_by_x = tuple((a << 1) ^ (0b10011 if a & 8 else 0) for a in range(16))
        for p, status, period in [
            (tuple(range(16)), "disconnected", None),
            (multiply_by_x, "periodic", 15),
        ]:
            with self.subTest(status=status):
                result = analyze_permutation(p, profile_rounds=3)
                self.assertEqual((result.status, result.period), (status, period))
                self.assertEqual(result.distances, ())
                self.assertEqual(result.difference_rounds, (None,) * len(DEFAULT_THRESHOLDS))
                self.assertIsNone(result.rate)

    def test_inverse_profile_against_full_cipher(self):
        result = analyze_permutation(INVERSE, profile_rounds=7)
        expected = direct_difference_distances(INVERSE, 7)
        self.assertEqual((result.status, result.period), ("mixing", 1))
        self.assertTrue(all(isinstance(d, Fraction) for d in result.distances))
        self.assertEqual(result.distances, expected)
        hits = tuple(next(r for r, d in enumerate(expected) if d <= e) for e in DEFAULT_THRESHOLDS)
        self.assertEqual(result.difference_rounds, hits)
        self.assertAlmostEqual(result.rate, 3 / 8)

    def test_slow_nonlinear_chain(self):
        # (b0, b1, b2, b3) -> (b1, b2, b3, b0 XOR (b1 AND b2)).
        feedback = (0, 8, 1, 9, 2, 10, 11, 3, 4, 12, 5, 13, 6, 14, 15, 7)
        result = analyze_permutation(feedback, profile_rounds=3)
        self.assertEqual(result.distances, (Fraction(14, 15),) * 3 + (Fraction(13, 15),))
        # First crossings from direct integer counts of cipher output pairs.
        self.assertEqual(result.difference_rounds, (8, 10, 14, 17, 20, 24))
        # The characteristic polynomial of twice the transition matrix is
        # x^10 (x - 2) (x^2 + 2) (x^2 + x - 1). Its dominant nontrivial root is negative.
        self.assertAlmostEqual(result.rate, (1 + sqrt(5)) / 4)
