import unittest
from collections import Counter
from fractions import Fraction
from itertools import permutations, product
from math import perm

from research.structured_probe import distances, round_certificate, universal_rounds

try:
    import numpy
except ImportError:
    numpy = None


class PowerCriterionTests(unittest.TestCase):
    def test_measured_block_perturbation(self):
        curve = [Fraction(1), Fraction(1, 8)]
        self.assertEqual(round_certificate(curve, Fraction(1, 8)), (2, True))
        self.assertEqual(round_certificate(curve, Fraction(1, 8), Fraction(1, 8)), (3, False))
        self.assertEqual(round_certificate(curve, Fraction(1, 8), Fraction(1, 2)), (None, False))

    def test_frobenius_and_parity_boundaries(self):
        self.assertIsNone(universal_rounds(5, 32 + 1, 3, 64))  # 33 == 2 mod 31
        self.assertIsNone(universal_rounds(3, 3, 7, 128))
        self.assertEqual(universal_rounds(3, 3, 1, 128), 1)
        self.assertEqual(universal_rounds(3, 3, 6, 32), 2 * 8 ** 16 * (32 + 18))
        with self.assertRaises(ValueError):
            universal_rounds(4, 3, 3, 128)


@unittest.skipIf(numpy is None, "requires the four-bit extra")
class PowerMeasurementsTests(unittest.TestCase):
    def test_all_starts_and_true_cipher_rounds(self):
        p = (0, 1, 3, 4, 5, 6, 7, 2)
        for order in (3, 4):
            classes, curve = distances(0xb, 3, order, 2)
            self.assertEqual(classes, 1 if order == 3 else 2)
            total = perm(8, order)
            worst = Fraction()
            # Input translation is absorbed in K1. Enumerate every remaining
            # ordered start and three actual keys independently of the shape code.
            for tail in permutations(range(1, 8), order - 1):
                outputs = Counter()
                for k, l, m in product(range(8), repeat=3):
                    outputs[tuple(p[m ^ p[l ^ p[k ^ v]]] for v in (0, *tail))] += 1
                missing = total - len(outputs)
                deviation = 512 * missing + sum(abs(total * c - 512) for c in outputs.values())
                worst = max(worst, Fraction(deviation, 2 * total * 512))
            self.assertEqual(curve[2], worst)

    def test_arbitrary_precision_hitting_time(self):
        _, curve = distances(0xb, 3, 3, 129)
        self.assertEqual(round_certificate(curve, Fraction(1, 1 << 128)), (129, True))
        short, exact = round_certificate(curve[:7], Fraction(1, 1 << 128))
        self.assertFalse(exact)
        self.assertGreaterEqual(short, 129)
