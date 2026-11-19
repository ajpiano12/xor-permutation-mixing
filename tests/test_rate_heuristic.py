from fractions import Fraction
from random import Random
import unittest

from mixing import analyze, transition_counts
try:
    from research.rate_heuristic import arnoldi_factor, block_certificate, exact_rounds, parity_lower_rounds, parity_score
except ModuleNotFoundError as error:
    if error.name != "numpy":
        raise
    raise unittest.SkipTest("Install the four-bit extra for the pair-rate tests.") from error


class RateHeuristicTests(unittest.TestCase):
    def test_exact_crossings_and_certified_remainders(self):
        errors = [3, 4, 5, 16, 32, 64, 128]
        p = [2, 5, 7, 1, 0, 4, 6, 3]
        counts = transition_counts(p)
        reference = analyze(counts, tuple(Fraction(1, 1 << e) for e in errors))
        self.assertEqual(reference.status, "mixing")
        measured = exact_rounds(counts, errors)
        whole, partial = block_certificate(counts, errors)
        self.assertEqual(tuple(measured[e] for e in errors), reference.pair_rounds)
        for e in errors:
            self.assertLessEqual(measured[e], partial[e])
            self.assertLessEqual(partial[e], whole[e])
        self.assertTrue(any(partial[e] < whole[e] for e in errors))

    def test_parity_scores_and_necessary_rounds(self):
        rng = Random(254)
        for _ in range(16):
            p = list(range(16))
            rng.shuffle(p)
            score = parity_score(p)
            brute = max(abs(sum((-1) ** (((x ^ image) & mask).bit_count() % 2)
                                for x, image in enumerate(p))) for mask in range(1, 16))
            self.assertEqual(score, brute)
            counts = transition_counts(p)
            reference = analyze(counts, (Fraction(1, 16), Fraction(1, 4096)))
            if reference.status == "mixing":
                for exponent, truth in zip((4, 12), reference.pair_rounds):
                    self.assertLessEqual(parity_lower_rounds(16, score, exponent), truth)
        self.assertEqual(parity_score(range(16)), 16)
        self.assertIsNone(parity_lower_rounds(16, 16, 32))

    def test_full_krylov_space_on_three_bit_inverse(self):
        p = (0, 1, 5, 6, 7, 2, 3, 4)
        self.assertAlmostEqual(arnoldi_factor(transition_counts(p)), 1 / (8 ** 0.5))
