import unittest
from fractions import Fraction
from math import factorial

from four_bit_obstructions import find_obstruction, obstruction_counts
from mixing import chain_period, transition_counts


class ObstructionTests(unittest.TestCase):
    def test_classification_and_witnesses_against_difference_graph(self):
        # Multiplication by x and x³ in GF(16) modulo x⁴+x+1.
        mul_x = tuple((x << 1) ^ (0b10011 if x & 8 else 0) for x in range(16))
        mul_x3 = tuple(mul_x[mul_x[mul_x[x]]] for x in range(16))
        fixtures = [
            (tuple(range(16)), "hyperplane", None),
            ((0, 1, 4, 5, 8, 9, 12, 13, 6, 7, 2, 3, 14, 15, 11, 10), "line", None),
            ((3, 9, 14, 7, 4, 10, 13, 0, 6, 11, 8, 2, 1, 15, 12, 5), "plane", None),
            (mul_x3, "affine_order_5", None),
            (mul_x, "affine_order_15", 15),
            ((9, 11, 2, 4, 13, 10, 8, 7, 14, 15, 3, 12, 0, 1, 5, 6), None, 1),
        ]
        for p, family, period in fixtures:
            with self.subTest(family=family):
                # A nonzero output translation must preserve the same witness.
                witness = find_obstruction(p)
                self.assertEqual(witness, find_obstruction(tuple(x ^ 13 for x in p)))
                self.assertEqual(witness[0] if witness else None, family)
                self.assertEqual(chain_period(transition_counts(p)), period)
                if witness and witness[1]:
                    w = witness[1]
                    self.assertTrue(all(p[x] ^ p[x ^ a] in w for x in range(16) for a in w))

    def test_disjoint_counts_against_graph_enumeration(self):
        self.assertEqual(Fraction(sum(obstruction_counts().values()), factorial(16)),
                         Fraction(421, 180180))
