"""Independent lattice checks for the coset-partition counting recurrence."""

import unittest
from fractions import Fraction
from itertools import permutations
from math import factorial

from research.group_counts import five_bit_bounds, quotient_coefficients, simple_counts


def binary_spaces(n):
    """Enumerate all subspaces, retaining one basis each."""
    result = {frozenset({0}): ()}
    for v in range(1, 2**n):
        for space, basis in list(result.items()):
            if v not in space:
                larger = space | frozenset(x ^ v for x in space)
                if larger not in result:
                    result[larger] = basis + (v,)
    return sorted(result.items(), key=lambda pair: len(pair[0]))


def invariant_spaces(table, spaces):
    return [space for space, basis in spaces
            if all(table[x] ^ table[x ^ v] in space for v in basis for x in range(len(table)))]


class GroupCountTests(unittest.TestCase):
    def test_normalized_three_bit_lattices(self):
        spaces = binary_spaces(3)
        total_mu = 0
        linear_mu = 0
        simple_nonlinear = 0
        for images in permutations(range(1, 8)):
            p = (0, *images)
            lattice = invariant_spaces(p, spaces)
            mu = {}
            for w in lattice:
                mu[w] = 1 if len(w) == 1 else -sum(v for u, v in mu.items() if u < w)
            top_mu = mu[lattice[-1]]
            total_mu += top_mu
            if all(p[x ^ y] == p[x] ^ p[y] for x in range(8) for y in range(8)):
                linear_mu += top_mu
            elif len(lattice) == 2:
                simple_nonlinear += 1
        self.assertEqual(-8 * total_mu, quotient_coefficients(3)[3])
        self.assertEqual(linear_mu, 0)
        self.assertEqual(simple_nonlinear, simple_counts(3)[3][0])

    def test_identical_nonlinear_factors_have_no_diagonal_congruence(self):
        # The cube on GF(8) is simple nonlinear. Its product has two proper ideals.
        cube = (0, 1, 3, 4, 5, 6, 7, 2)
        product = tuple((cube[x >> 3] << 3) | cube[x & 7] for x in range(64))
        spaces = binary_spaces(6)
        self.assertEqual(len(spaces), 2825)
        proper = invariant_spaces(product, spaces)[1:-1]
        self.assertEqual(set(proper), {frozenset(range(8)), frozenset(range(0, 64, 8))})

    def test_five_bit_count_inside_independent_bounds(self):
        q5, linear = simple_counts(5)[-1]
        failure = 1 - Fraction(32 * q5, factorial(32))
        self.assertEqual(32 * linear, 61_931_520)
        self.assertEqual(failure, Fraction(3534251519984761663, 34264020623061220992000000))
        lower, upper = five_bit_bounds()
        self.assertLess(lower, failure)
        self.assertLess(failure, upper)
