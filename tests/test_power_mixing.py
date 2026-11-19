"""Cross-check finite-field character bounds and packed counts with direct integer walks."""
import unittest
from collections import Counter
from fractions import Fraction
from random import Random

from power_mixing import algebraic_bound, cyclic_convolution, exact_times, field_powers


def power_table(bits, modulus, exponent):
    """Build a table independently by carryless multiplication and polynomial remainder."""
    q = 1 << bits
    def product(x, y):
        z = 0
        for j in range(bits):
            if y & (1 << j):
                z ^= x << j
        while z.bit_length() > bits:
            z ^= modulus << (z.bit_length() - modulus.bit_length())
        return z
    values = [0]
    for x in range(1, q):
        value = 1
        power = x
        k = exponent % (q - 1)
        while k:
            if k % 2:
                value = product(value, power)
            k //= 2
            power = product(power, power)
        values.append(value)
    return values


def direct_cutoffs(p, bits_of_precision, starts=None):
    # Use all q keyed transitions per row. The reference makes no use of the
    # field scaling, the multiplicative log table, or the unordered-pair reduction.
    q = len(p)
    m = q - 1
    rows = [Counter((p[x] ^ p[x ^ a]) - 1 for x in range(q)) for a in range(1, q)]
    tracked = list(range(m)) if starts is None else [a - 1 for a in starts]
    counts = [[int(start == j) for j in range(m)] for start in tracked]
    remaining = sorted(set(bits_of_precision))
    hits = {}
    denominator = 1
    cipher_round = 1
    while remaining:
        deviation = max(sum(abs(m * n - denominator) for n in row) for row in counts)
        while remaining and (deviation << remaining[0]) <= 2 * m * denominator:
            hits[remaining.pop(0)] = cipher_round
        if not remaining:
            return hits
        next_counts = []
        for row in counts:
            new = [0] * m
            for a, count in enumerate(row):
                if count:
                    for b, multiplicity in rows[a].items():
                        new[b] += count * multiplicity
            next_counts.append(new)
        counts = next_counts
        denominator *= q
        cipher_round += 1
        if cipher_round > 512:
            raise AssertionError("the selected regression cases should mix rapidly")


class PowerMixingTests(unittest.TestCase):
    def test_exact_convolution_across_byte_carries(self):
        rng = Random(3737)
        for m in (1, 2, 7, 31):
            for width in (0, 7, 8, 9, 130):
                left = [rng.getrandbits(width) for _ in range(m)]
                right = [rng.getrandbits(width) for _ in range(m)]
                expected = [sum(left[i] * right[(k-i) % m] for i in range(m)) for k in range(m)]
                self.assertEqual(cyclic_convolution(left, right), expected)
        self.assertEqual(cyclic_convolution([16], [16]), [256])

    def test_exact_times_against_direct_difference_rows(self):
        targets = [128, 16, 5, 32, 64, 16]
        for n, modulus, d in ((3, 0xB, 3), (4, 0x13, -1), (8, 0x11B, 7)):
            p = power_table(n, modulus, d)
            self.assertEqual(field_powers(modulus, d), p)
            # At eight bits check two independently chosen starts. At small widths
            # compare to the worst row over every possible starting difference.
            starts = (3, 127) if n == 8 else None
            expected = direct_cutoffs(p, targets, starts)
            actual = exact_times(modulus, d, targets)
            self.assertTrue(actual["mixes"])
            self.assertEqual(actual["rounds"], expected)
            for k, r in expected.items():
                bound = algebraic_bound(n, d, 0, k)["sufficient_cipher_rounds"]
                self.assertGreaterEqual(bound, r)

    def test_twists_inverse_and_perturbation(self):
        q = 32
        d = 3
        p = power_table(5, 0x25, d)
        p[0], p[11] = p[11], p[0]
        for k, minimal in direct_cutoffs(p, [16, 64]).items():
            base = algebraic_bound(5, d, 2, k)
            self.assertGreaterEqual(base["sufficient_cipher_rounds"], minimal)
            self.assertLess(Fraction(base["squared_norm_upper"]), 1)
            for e in (d, pow(d, -1, q-1)):
                for i in range(5):
                    self.assertEqual(algebraic_bound(5, e << i, 2, k), base)
        self.assertIsNone(algebraic_bound(5, d, q, 64)["sufficient_cipher_rounds"])

    def test_invalid_powers_nonmixers_and_one_bit(self):
        with self.assertRaises(ValueError):
            exact_times(0x13, 3, [32])
        with self.assertRaises(ValueError):
            exact_times(0x15, 7, [32])
        with self.assertRaises(ValueError):
            exact_times(0x13, -1, [0])
        for exponent in (1, 2, 4, 8):
            self.assertFalse(exact_times(0x13, exponent, [16])["mixes"])
        self.assertEqual(exact_times(3, 1, [128])["rounds"], {128: 1})
