from collections import Counter
from fractions import Fraction
from itertools import permutations, product
from math import comb, prod
import unittest

from research.sweep_bounds import bias_bound, mixed_warmup_rounds, sqrt_upper, sweep_analysis


class SweepBoundsTests(unittest.TestCase):
    def test_numerical_certificates(self):
        for control in ("inverse", "power15", "polynomial15"):
            result = sweep_analysis(128, 16, 4, [32, 64, 128], 0, control)
            self.assertEqual([v["sweep_norm"]["rounds"] for v in result.values()], [19, 25, 36])
            self.assertEqual(result["2^-128"]["sweep_norm"], {"rounds": 36, "warmup": 3, "additional_sweeps": 3})
            self.assertEqual(result["2^-128"]["short_blocks"], 51)
        result = sweep_analysis(128, 12, 4, [128], 0, "power15")
        self.assertEqual(result["2^-128"], {"short_blocks": 57, "sweep_norm": None})
        self.assertIsNone(sweep_analysis(128, 16, 4, [32], 2, "inverse")["2^-32"]["sweep_norm"])

    def test_mixed_products_and_outward_rounding(self):
        choices = {3: Fraction(1, 8), 5: Fraction(1, 64)}
        self.assertEqual(mixed_warmup_rounds(choices, [1, 7, 10]), {1: 4, 7: 6, 10: 9})
        for x in [Fraction(0), Fraction(1, 2**319), Fraction(2**300, 3), Fraction(17, 101)]:
            self.assertGreaterEqual(sqrt_upper(x)**2, x)
        self.assertGreaterEqual(bias_bound(8, 1, 3, "inverse") * 128 - 4, 0)

    def test_pair_collision_all_starts_with_overlapping_windows(self):
        for bits, width in [(4, 2), (5, 2), (7, 2)]:
            size, alphabet = 1 << bits, 1 << width
            cap = bits // width - 1
            for initial in range(1, size):
                weights = Counter({initial: 1})
                for j in range(2 * ((bits + width - 1) // width)):
                    start = width * j % bits
                    offsets = [((v << start) | (v >> (bits - start))) & (size - 1)
                               for v in range(alphabet)]
                    hit = sum(count for diff, count in weights.items() if not diff & ~offsets[-1])
                    self.assertLessEqual(hit * alphabet**min(j, cap), sum(weights.values()))
                    after = Counter()
                    for diff, count in weights.items():
                        if not diff & ~offsets[-1]:
                            after[diff] += alphabet * count
                        else:
                            for offset in offsets:
                                after[diff ^ offset] += count
                    weights = after

    def test_unique_ideal_paths_all_distinct_triples(self):
        # All 336 ordered starts on 3 bits. Track paths, integer masses and deficits.
        size, order, bits = 8, 3, 3
        row_chi_sum = Fraction(0)
        targets = prod(size-i for i in range(order))
        denom = (1 << order)**bits
        for start in permutations(range(size), order):
            paths = [(start, 1, 0)]
            for j in range(bits):
                step = []
                for state, numerator, loss in paths:
                    controls = [x & ~(1 << j) for x in state]
                    group = list(dict.fromkeys(controls))
                    increment = order - len(group)
                    for writes in product((0, 1), repeat=len(group)):
                        offsets = dict(zip(group, writes))
                        after = tuple(x ^ (offsets[z] << j) for x, z in zip(state, controls))
                        step.append((after, numerator << increment, loss + increment))
                paths = step
            self.assertEqual(len(paths), len({x[0] for x in paths}))
            self.assertEqual(sum(mass for _, mass, _ in paths), denom)
            self.assertTrue(all(mass == (1 << loss) and loss <= 2 for _, mass, loss in paths))
            row_chi_sum += Fraction(targets * sum(mass**2 for _, mass, _ in paths), denom**2) - 1
        edge = Fraction(bits, size - order + 1)
        forest_bound = sum(comb(3, v) * edge**v * 2**comb(v+1, 2) for v in range(1, order))
        self.assertLessEqual(row_chi_sum / targets, forest_bound)
