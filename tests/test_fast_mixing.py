import unittest
from collections import defaultdict
from itertools import permutations
from random import Random
from unittest.mock import Mock, patch

import fast_mixing
from classify_mixing import classify
from fast_mixing import DifferenceForest, rectangle_edges, screen, violating_anchor


def real_edges(p, xs, ys):
    return [(x ^ y, p[x] ^ p[y]) for x in xs for y in ys if x != y]


class FastMixingTests(unittest.TestCase):
    def test_signed_tree_heights_and_cycle_gcd(self):
        forest = DifferenceForest(16)
        # The first component is smaller than the second at their merge.
        for a, b in ((1, 2), (3, 4), (4, 5), (1, 3), (6, 5), (7, 2)):
            forest.edge(a, b)
        root, origin = forest.locate(1)
        for vertex, expected in enumerate((0, 1, 1, 2, 3, 2, 0), start=1):
            component, height = forest.locate(vertex)
            self.assertEqual(component, root)
            self.assertEqual(height - origin, expected)
        self.assertEqual(forest.components, 9)
        self.assertEqual(forest.period_multiple, 15)
        forest.edge(5, 2)
        self.assertEqual(forest.period_multiple, 3)
        forest.edge(2, 1)
        self.assertEqual(forest.period_multiple, 1)

    def test_dense_rectangle_recovers_unique_crossings(self):
        rng = Random(84)
        instances = [
            ([4, 3, 5, 6, 7, 2, 1, 0], [0, 1, 2, 3, 2, 1, 1, 2], [4, 5, 6], [7, 4, 5])
        ]
        for _ in range(40):
            size = 16
            p = rng.sample(range(size), size)
            labels = [0] + [rng.randrange(1, 5) for _ in range(1, size)]
            instances.append((p, labels, rng.sample(range(size), 5), rng.sample(range(size), 5)))
        for p, labels, xs, ys in instances:
            self.assertGreater(len(xs) * len(ys), len(p))
            cuts = defaultdict(list)
            for a, b in real_edges(p, xs, ys):
                if labels[a] != labels[b]:
                    cuts[labels[a]].append((a, b))
                    cuts[labels[b]].append((a, b))
            unique = {edges[0] for edges in cuts.values() if len(edges) == 1}
            if len(p) == 8:
                # One isolated pair has a positive signed sum, the other negative.
                self.assertEqual(unique, {(3, 7), (2, 6)})
            recorded = Mock()
            rectangle_edges(p, labels, xs, ys, recorded)
            found = {call.args for call in recorded.edge.call_args_list}
            self.assertLessEqual(unique, found)
            # Collisions may suggest a genuine crossing outside the rectangle.
            all_edges = set(real_edges(p, range(len(p)), range(len(p))))
            self.assertLessEqual(found, all_edges)
            self.assertTrue(all(labels[a] != labels[b] for a, b in found))

    def test_valid_and_invalid_partitions_and_cyclic_colors(self):
        rotate = tuple(((x << 1) & 7) | (x >> 2) for x in range(8))
        partition = [x.bit_count() for x in range(8)]
        singer = (0, 2, 4, 6, 3, 1, 7, 5)
        heights = [0] * 8
        a = 1
        for h in range(7):
            heights[a] = h
            a = singer[a]
        advanced = [0] + [(h + 1) % 7 for h in heights[1:]]
        for p, source, target in ((rotate, partition, partition), (singer, advanced, heights)):
            for corrupt in (False, True):
                candidate = target.copy()
                if corrupt:
                    candidate[3] += 1
                bad_rows = {
                    x for x in range(len(p))
                    if any(source[x ^ y] != candidate[p[x] ^ py] for y, py in enumerate(p))
                }
                self.assertEqual(bool(bad_rows), corrupt)
                for seed in (3, 11, 71):
                    witness = violating_anchor(p, source, candidate, 32, Random(seed))
                    if corrupt:
                        self.assertIn(witness, bad_rows)
                    else:
                        self.assertIsNone(witness)

    def test_sparse_change_needs_more_than_the_sampled_anchors(self):
        bits = 5
        size = 1 << bits
        # Rotate the bits after swapping the final two inputs.
        swapped = [x if x < size - 2 else x ^ 1 for x in range(size)]
        p = [((x << 1) % size) | (x >> (bits - 1)) for x in swapped]
        seed = 1
        forest = DifferenceForest(size)
        for x in Random(seed).sample(range(size), 3):
            forest.anchor(p, x)
        self.assertGreater(forest.components, 1)
        self.assertEqual(classify(p).status, "mixing")
        with patch.object(fast_mixing, "violating_anchor", wraps=violating_anchor) as probes:
            self.assertEqual(screen(p, 16, rng=Random(seed)), "mixing")
            self.assertGreaterEqual(probes.call_count, 1)

    def test_screen_on_structured_and_random_permutations(self):
        cube = (0, 1, 3, 4, 5, 6, 7, 2)
        block_swap = tuple((cube[x & 7] << 3) | cube[x >> 3] for x in range(64))
        singer = (0, 2, 4, 6, 3, 1, 7, 5)
        tables = [*permutations(range(2)), *permutations(range(4)), block_swap, singer]
        table_rng = Random(18)
        for size in (8, 16, 32):
            tables.extend(table_rng.sample(range(size), size) for _ in range(20))
        for p in tables:
            expected = "mixing" if classify(p).status == "mixing" else "unresolved"
            for seed in (23, 316):
                with self.subTest(p=p, seed=seed):
                    self.assertEqual(screen(p, 32, rng=Random(seed)), expected)

    def test_invalid_input(self):
        for p in ((), (1, 1), (1, 2)):
            with self.assertRaises(ValueError):
                screen(p)
        for e in (0, -1, 0.5):
            with self.assertRaises(ValueError):
                screen((0, 1), e)
