import csv
import unittest
from collections import Counter
from fractions import Fraction
from itertools import permutations
from math import factorial, perm
from pathlib import Path

from inverse_triples import field_inverse_table, triple_certificate
from quadratic_mixing import has_certificate, sufficient_rounds

try:
    import numpy as np
    from higher_census import DENOMINATORS, measure, normalized_starts, representatives
    from research.triple_probe import triple_distances
except ModuleNotFoundError as exc:
    if exc.name != "numpy":
        raise
    np = None


class CertificateTests(unittest.TestCase):
    def test_binary_field_and_triple_certificate(self):
        self.assertEqual(field_inverse_table(8, 0b1011), [0, 1, 5, 6, 7, 2, 3, 4])
        for modulus in (0b1001, 0b1010, 0b1100):
            with self.subTest(modulus=modulus), self.assertRaisesRegex(ValueError, "reducible"):
                field_inverse_table(8, modulus)
        with self.assertRaises(ValueError):
            field_inverse_table(16, 0b1011)
        p = field_inverse_table(32, 0x25)
        self.assertEqual(triple_certificate(p, 0x25), (0, Fraction(7, 32)))
        p[0], p[1] = p[1], p[0]
        self.assertEqual(triple_certificate(p, 0x25), (2, Fraction(19, 32)))
        p[2:5] = p[3:5] + p[2:3]
        self.assertEqual(triple_certificate(p, 0x25), (5, Fraction(1)))

    def test_apn_gram_and_sufficient_rounds(self):
        # Cubing in GF(8), with an output translation to exercise normalization.
        p = [x ^ 6 for x in (0, 1, 3, 4, 5, 6, 7, 2)]
        self.assertTrue(has_certificate(p))
        self.assertFalse(has_certificate(tuple(range(8))))
        # The patched inverse on five bits is APN, but has degree four.
        self.assertFalse(has_certificate(field_inverse_table(32, 0x25)))
        rows = [Counter(p[x] ^ p[x ^ a] for x in range(8)) for a in range(1, 8)]
        for i, row in enumerate(rows):
            for j, other in enumerate(rows):
                self.assertEqual(sum(row[b] * other[b] for b in range(1, 8)),
                                 16 if i == j else 8)
        for epsilon in (Fraction(1, 4), Fraction(1, 128), Fraction(1, 10**20)):
            r = sufficient_rounds(32, epsilon)
            self.assertLessEqual(Fraction(30, 32 ** (r - 1)), 4 * epsilon ** 2)
            self.assertGreater(Fraction(30, 32 ** (r - 2)), 4 * epsilon ** 2)

    def test_high_order_census_parity_and_multiplicities(self):
        path = Path(__file__).resolve().parents[1] / "results" / "higher_three_bit.csv"
        with path.open(newline="") as fh:
            rows = list(csv.DictReader(fh))
        totals = Counter()
        periodic = Counter()
        for row in rows:
            order, weight = int(row["t"]), int(row["permutations"])
            totals[order] += weight
            if order in (7, 8):
                self.assertIn(row["status"], {"disconnected", "periodic"})
                if row["status"] == "periodic":
                    self.assertEqual(row["period"], "2")
                    p = tuple(map(int, row["representative"].split()))
                    inversions = sum(x > y for i, x in enumerate(p) for y in p[i + 1:])
                    self.assertEqual(inversions % 2, 1)
                    periodic[order] += weight
        self.assertEqual(totals, {order: factorial(8) for order in range(2, 9)})
        self.assertEqual(periodic, {7: 16128, 8: 16128})


@unittest.skipIf(np is None, "Install the four-bit extra for the exact tuple rate checks.")
class TupleRateTests(unittest.TestCase):
    def test_three_bit_apn_count_by_orbits(self):
        reps = list(representatives())
        self.assertEqual(sum(weight for _, weight in reps), factorial(8))
        self.assertEqual(sum(weight for p, weight in reps if has_certificate(p)), 10752)

    def test_ordered_triples_against_full_round_maps(self):
        p = (0, 1, 2, 4, 5, 6, 7, 3)
        tuples = list(permutations(range(8), 3))
        ids = {t: i for i, t in enumerate(tuples)}
        images = [[ids[tuple(p[x ^ k] for x in t)] for t in tuples] for k in range(8)]
        # Row i starts at the ith true ordered triple and evolves by each keyed bijection.
        counts = np.eye(perm(8, 3), dtype=np.int64)
        hits = []
        fixed = []
        states = len(tuples)
        for r in range(1, 14):
            updated = np.zeros_like(counts)
            for image in images:
                updated[:, image] += counts
            counts = updated
            keys = 8 ** r
            deviation = np.abs(states * counts - keys).sum(axis=1)
            if 2 <= r <= 4:
                fixed.append(Fraction(int(deviation[ids[0, 1, 2]]), 2 * states * keys))
            distance = Fraction(int(deviation.max()), 2 * states * keys)
            while len(hits) < len(DENOMINATORS) and distance <= Fraction(1, DENOMINATORS[len(hits)]):
                hits.append(r)
            if len(hits) == len(DENOMINATORS) and r >= 4:
                break
        self.assertEqual(triple_distances(p), fixed)
        self.assertEqual(len(hits), len(DENOMINATORS))
        shapes = [bytes(s) for s in permutations(range(1, 8), 2)]
        shape_ids = {s: i for i, s in enumerate(shapes)}
        starts = normalized_starts(3, shape_ids)
        self.assertEqual(measure(p, shapes, shape_ids, starts), ("mixing", 1, tuple(hits)))
