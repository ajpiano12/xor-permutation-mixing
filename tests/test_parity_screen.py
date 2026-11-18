import unittest
from itertools import permutations
from random import Random

from parity_screen import parity_query_budget, screen_parity


def span(basis):
    result = {0}
    for mask in basis:
        result |= {value ^ mask for value in result}
    return result


class ParityTests(unittest.TestCase):
    def test_exhaustive_against_direct_parity_checks(self):
        rng = Random(179)
        tables = list(permutations(range(4)))
        for size in (8, 16, 32):
            tables.extend(rng.sample(range(size), size) for _ in range(20))
        for p in tables:
            with self.subTest(p=p):
                size = len(p)
                result = screen_parity(size.bit_length() - 1, p.__getitem__)
                expected = {
                    m for m in range(size)
                    if all(((x ^ p[x] ^ p[0]) & m).bit_count() % 2 == 0 for x in range(size))
                }
                self.assertEqual(span(result.mask_basis), expected)
                self.assertEqual(2**len(result.mask_basis), len(expected))
                self.assertEqual(result.status, "no_witness" if expected == {0} else "nonmixing")
                self.assertLessEqual(result.evaluations, size)

    def test_budgeted_candidate_on_a_mixing_permutation(self):
        p = [0, 1, 5, 6, 7, 2, 3, 4]
        queries = []

        def evaluate(x):
            queries.append(x)
            return p[x]

        sample = screen_parity(3, evaluate, budget=2, rng=Random(3))
        self.assertEqual(sample.status, "candidate")
        self.assertTrue(sample.mask_basis)
        self.assertEqual(sample.evaluations, len(queries))
        self.assertEqual(len(queries), 2)
        self.assertEqual(screen_parity(3, evaluate, budget=8).status, "no_witness")

    def test_exact_masks_survive_sampling_on_a_compact_input(self):
        bits = 128
        flip = 42
        # Add the low two bits modulo four; higher bits retain their parities.
        def evaluate(x):
            return ((x & ~3) | ((x + 1) % 4)) ^ flip

        sample = screen_parity(bits, evaluate, budget=80, rng=Random(8))
        self.assertEqual(sample.status, "candidate")
        self.assertEqual(len(sample.mask_basis), bits - 1)
        self.assertTrue(all(mask & 2 == 0 for mask in sample.mask_basis))
        self.assertEqual(sample.evaluations, 80)

    def test_sampled_rows_can_conclusively_rule_out_parity(self):
        # Rotation through the seven nonzero differences remains periodic.
        p = (0, 2, 4, 6, 3, 1, 7, 5)
        result = screen_parity(3, p.__getitem__, budget=7, rng=Random(42))
        self.assertEqual(result.status, "no_witness")
        self.assertLessEqual(result.evaluations, 7)

    def test_one_bit_and_invalid_inputs(self):
        self.assertEqual(screen_parity(1, lambda x: x).status, "no_witness")
        for bits, budget in ((0, 1), (5, 0)):
            with self.assertRaises(ValueError):
                screen_parity(bits, lambda x: x, budget=budget)
        with self.assertRaises(ValueError):
            screen_parity(3, lambda x: 8)
        for args in ((0, 0.1, 0.1), (8, 0, 0.01), (8, 0.1, 1)):
            with self.assertRaises(ValueError):
                parity_query_budget(*args)
        self.assertEqual(parity_query_budget(3, 0.1, 0.01), 8)
        self.assertEqual(parity_query_budget(128, 0.01, 0.01), 9334)
