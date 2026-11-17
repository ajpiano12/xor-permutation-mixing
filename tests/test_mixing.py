import unittest
from collections import Counter
from fractions import Fraction
from itertools import permutations

from mixing import analyze, transition_counts


NONLINEAR = (0, 1, 2, 4, 5, 6, 7, 3)


def pair_distances(permutation, last_round):
    """Directly evolve all ordered input pairs, keeping integer key-sequence counts."""
    pairs = list(permutations(range(8), 2))
    distributions = [Counter([pair]) for pair in pairs]
    distances = []
    for round_number in range(last_round + 1):
        key_count = 8**round_number
        deviation = max(
            sum(abs(len(pairs) * counts[pair] - key_count) for pair in pairs)
            for counts in distributions
        )
        distances.append(Fraction(deviation, 2 * len(pairs) * key_count))
        if round_number < last_round:
            next_distributions = []
            for counts in distributions:
                new_counts = Counter()
                for (x, y), count in counts.items():
                    for key in range(8):
                        new_counts[permutation[x ^ key], permutation[y ^ key]] += count
                next_distributions.append(new_counts)
            distributions = next_distributions
    return distances


class MixingTests(unittest.TestCase):
    def test_transition_counts_use_eight_keys(self):
        matrix = transition_counts(NONLINEAR)
        self.assertEqual(tuple(matrix[0]), (2, 0, 2, 2, 0, 2, 0))
        self.assertEqual([sum(row) for row in matrix], [8] * 7)
        self.assertEqual([sum(column) for column in zip(*matrix)], [8] * 7)

    def test_field_inverse_two_round_counts(self):
        # Multiplicative inversion in GF(2)[x]/(x^3 + x + 1), with 0 fixed.
        matrix = transition_counts((0, 1, 5, 6, 7, 2, 3, 4))
        for i, row in enumerate(matrix):
            for j, column in enumerate(zip(*matrix)):
                count = sum(a * b for a, b in zip(row, column))
                self.assertEqual(count, 16 if i == j else 8, (i, j))

    def test_disconnected_identity_and_connected_seven_cycle(self):
        thresholds = (Fraction(1, 4), Fraction(1, 2))
        for permutation, status, period in [
            (tuple(range(8)), "disconnected", None),
            ((0, 2, 4, 6, 3, 1, 7, 5), "periodic", 7),
        ]:
            with self.subTest(permutation=permutation):
                result = analyze(transition_counts(permutation), thresholds)
                self.assertEqual(result.status, status)
                self.assertEqual(result.period, period)
                self.assertEqual(result.difference_rounds, (None, None))
                self.assertEqual(result.pair_rounds, (None, None))

    def test_pair_times_against_full_cipher(self):
        boundary = Fraction(3, 7)
        thresholds = (Fraction(3, 28), Fraction(1, 2), boundary - Fraction(1, 2**80), boundary)
        distances = pair_distances(NONLINEAR, 4)
        self.assertEqual(distances[3], boundary)
        expected = tuple(
            next(r for r, distance in enumerate(distances) if distance <= threshold)
            for threshold in thresholds
        )
        self.assertEqual(expected, (4, 3, 4, 3))

        result = analyze(transition_counts(NONLINEAR), thresholds)
        self.assertEqual(result.status, "mixing")
        self.assertEqual(result.period, 1)
        self.assertEqual(result.pair_rounds, expected)
        self.assertEqual(result.difference_rounds, tuple(r - 1 for r in expected))
