from fractions import Fraction
from math import prod
from unittest import TestCase

from mixing import analyze, transition_counts
from power_mixing import multiply
from research.round_bounds import close_affine, family_bounds, rounded_power, table_bounds
from research.spectral_certificate import irreducible


class RoundBoundsTests(TestCase):
    def test_detect_and_recover_affine_approximation(self):
        linear = [multiply(x, 2, 0x13) ^ 11 for x in range(16)]
        self.assertEqual(close_affine(linear), ([2, 4, 8, 3], 11, 0))
        linear[0], linear[1] = linear[1], linear[0]
        self.assertEqual(close_affine(linear), ([2, 4, 8, 3], 11, 2))
        self.assertEqual(table_bounds(linear, 128)["necessary_cipher_rounds"], 128)
        linear[2], linear[3] = linear[3], linear[2]
        self.assertIsNone(close_affine(linear))

    def test_rotating_swap_kernel_and_finite_bracket(self):
        size, modulus = 16, 0x13
        parent = [multiply(x, 2, modulus) for x in range(size)]
        table = parent.copy()
        table[0], table[1] = table[1], table[0]
        counts = transition_counts(tuple(table))
        for a in range(1, size):
            row = [0] * (size - 1)
            row[parent[a] - 1] = size - 4
            row[parent[a if a == 1 else a ^ 1] - 1] += 4
            self.assertEqual(counts[a - 1], tuple(row))
        exact, = analyze(counts, (Fraction(1, 1 << 128),)).pair_rounds
        bounds = family_bounds(4, 128)
        self.assertEqual(exact, 266)
        self.assertLessEqual(bounds["necessary_cipher_rounds"], exact)
        self.assertLessEqual(exact, bounds["sufficient_cipher_rounds"])

    def test_outward_rounding(self):
        base = Fraction(13, 15)
        for k in (0, 1, 3, 23, 150):
            self.assertLessEqual(rounded_power(base, k, 15, upper=False), base**k)
            self.assertGreaterEqual(rounded_power(base, k, 15, upper=True), base**k)

    def test_independent_retention_and_higher_order_bounds(self):
        # A uniform XOR for each independently refreshed label erases any sole anchor.
        from itertools import product
        from collections import Counter
        for anchored in range(3):
            starts = [0, 1, 2]
            outputs = [range(4) if i != anchored else [x] for i, x in enumerate(starts)]
            shapes = Counter((b ^ a, c ^ a) for a, b, c in product(*outputs))
            self.assertEqual(len(shapes), 16)
            self.assertEqual(set(shapes.values()), {1})
        result = family_bounds(128, 128, 4)
        self.assertEqual(result["sufficient_epochs"], 24)
        self.assertIsNone(family_bounds(4, 128, 4)["sufficient_cipher_rounds"])

    def test_concrete_128bit_linear_cycle(self):
        modulus = (1 << 128) | 0x87
        factors = (3, 5, 17, 257, 641, 65537, 274177, 6700417, 67280421310721)
        m = (1 << 128) - 1
        self.assertTrue(irreducible(modulus, 128))
        self.assertEqual(prod(factors), m)
        def x_power(k):
            value, base = 1, 2
            while k:
                if k & 1:
                    value = multiply(value, base, modulus)
                base = multiply(base, base, modulus)
                k >>= 1
            return value
        self.assertEqual(x_power(m), 1)
        for q in factors:
            self.assertNotEqual(x_power(m // q), 1)
        self.assertEqual(family_bounds(128, 128)["sufficient_epochs"], 23)
