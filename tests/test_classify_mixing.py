import unittest
from itertools import permutations
from random import Random

from classify_mixing import classify


def successors(permutation):
    """Enumerate every one-round outcome for each starting difference."""
    return {
        a: {permutation[x] ^ permutation[x ^ a] for x in range(len(permutation))}
        for a in range(1, len(permutation))
    }


def classify_by_reachable_sets(graph):
    """Track which states can be reached from 1 in exactly r rounds."""
    seen = {}
    visited = set()
    current = frozenset({1})
    while current not in seen:
        seen[current] = len(seen)
        visited.update(current)
        current = frozenset(v for u in current for v in graph[u])
    if len(visited) < len(graph):
        return "disconnected", None
    # Eventually the reachable sets cycle through the full periodic classes.
    period = len(seen) - seen[current]
    return ("mixing" if period == 1 else "periodic"), period


class ClassificationTests(unittest.TestCase):
    def check_table(self, permutation, expected):
        graph = successors(permutation)
        result = classify(permutation)
        self.assertEqual((result.status, result.period), expected)
        if result.status == "disconnected":
            closed = set(result.closed_set)
            self.assertTrue(closed)
            self.assertLess(closed, set(graph))
            for a in closed:
                self.assertLessEqual(graph[a], closed)
        elif result.status == "periodic":
            classes = result.cyclic_classes
            self.assertEqual(len(classes), result.period)
            self.assertCountEqual((a for group in classes for a in group), graph.keys())
            for i, group in enumerate(classes):
                self.assertTrue(group)
                following = set(classes[(i + 1) % result.period])
                for a in group:
                    self.assertLessEqual(graph[a], following)
        return result

    def test_one_bit_and_identity(self):
        for p in permutations(range(2)):
            self.check_table(p, ("mixing", 1))
        self.check_table(tuple(range(16)), ("disconnected", None))

    def test_periodic_affine_permutation_with_output_translation(self):
        # Multiplication by t in GF(2)[t]/(t^4 + t + 1), followed by XOR 7.
        p = tuple(((x << 1) ^ (0b10011 if x & 8 else 0)) ^ 7 for x in range(16))
        self.check_table(p, ("periodic", 15))

    def test_aperiodic_without_any_self_loop(self):
        p = (0, 9, 6, 8, 14, 11, 7, 1, 4, 12, 5, 2, 15, 10, 3, 13)
        self.assertTrue(all(a not in row for a, row in successors(p).items()))
        self.check_table(p, ("mixing", 1))

    def test_six_bit_block_swap(self):
        # Cube in GF(8) using the basis defined by t^3 + t + 1.
        cube = (0, 1, 3, 4, 5, 6, 7, 2)
        p = tuple((cube[x & 7] << 3) | cube[x >> 3] for x in range(64))
        result = self.check_table(p, ("disconnected", None))
        self.assertIn(len(result.closed_set), (14, 49))

    def test_against_exact_reachable_sets(self):
        rng = Random(20261118)
        tables = list(permutations(range(4)))
        for size in (8, 16, 32):
            tables.extend(tuple(rng.sample(range(size), size)) for _ in range(30))
        for p in tables:
            with self.subTest(permutation=p):
                self.check_table(p, classify_by_reachable_sets(successors(p)))

    def test_invalid_tables(self):
        for p in ((), (0,), (0, 1, 2), (1, 1), (-1, 0), (0, 2), (0, 1.5)):
            with self.subTest(permutation=p):
                with self.assertRaises((ValueError, TypeError)):
                    classify(p)
