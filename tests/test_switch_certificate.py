import itertools
import unittest
from collections import Counter
from fractions import Fraction

from inverse_triples import field_inverse_table
from research.spectral_certificate import block_bound, certify, irreducible, round_image, sufficient_rounds


class SwitchCertificateTests(unittest.TestCase):
    def test_compact_and_table_certificates(self):
        p112 = (1 << 112) | 0x39
        p120 = (1 << 120) | 0x1b
        for t, b, p, expected in ((3, 16, p112, [17, 33, 65]), (4, 16, p112, [33, 49, 81]),
                                  (8, 8, p120, [65, 97, 193]),
                                  (3, 22, (1 << 106) | 0x63, [25, 37, 61]),
                                  (8, 7, (1 << 121) | 0x123, [77, 115, 191])):
            result = certify(128, b, t, p, [32, 64, 128])
            self.assertEqual(list(result["sufficient_cipher_rounds"].values()), expected)
        self.assertFalse(irreducible(0b10101, 4))  # (x²+x+1)²
        inv = field_inverse_table(8, 0b1011)
        p = [round_image(i, inv, 3, 1) for i in range(16)]
        self.assertEqual(certify(4, 1, 3, 0b1011, [64], p)["mismatches"], 0)
        p[2], p[5] = p[5], p[2]
        self.assertEqual(certify(4, 1, 3, 0b1011, [64], p)["mismatches"], 2)
        with self.assertRaisesRegex(ValueError, "irreducible"):
            certify(4, 1, 3, 0b1001, [64])
        delta = block_bound(127, 13, 4)
        rounds = sufficient_rounds(127, 13, delta, 127)
        self.assertIsNotNone(rounds)
        blocks = (rounds - 1) // 20
        self.assertLessEqual((2 * delta)**blocks / 2, Fraction(1, 2**127))
        self.assertGreater((2 * delta)**(blocks - 1) / 2, Fraction(1, 2**127))

    def test_final_mask_lifts_the_difference_law_exactly(self):
        p = (3, 1, 5, 6, 0, 2, 7, 4)
        size = len(p)
        difference_states = (size - 1) * (size - 2)

        def tv_from_uniform(counts, states):
            total = sum(counts.values())
            return 1 - sum(min(Fraction(count, total), Fraction(1, states))
                           for count in counts.values())

        for left, right in itertools.permutations(range(1, size), 2):
            quotient, full = Counter(), Counter()
            for first_key in range(size):
                a, b, c = (p[first_key ^ x] for x in (0, left, right))
                quotient[b ^ a, c ^ a] += 1
                for last_key in range(size):
                    full[tuple(p[last_key ^ x] for x in (a, b, c))] += 1
            self.assertEqual(tv_from_uniform(quotient, difference_states),
                             tv_from_uniform(full, size * difference_states))

    def test_joint_character_bounds_for_inverse_projection(self):
        # Exhaust all differences and nonzero masks for two 2-bit outputs over GF(64).
        size = 64
        inv = field_inverse_table(size, 0b1000011)
        maximum = 0
        for difference in range(1, size):
            for a, b in itertools.product(range(1, 4), repeat=2):
                negative = sum((((a & inv[u]).bit_count() + (b & inv[u ^ difference]).bit_count()) % 2)
                               for u in range(size))
                maximum = max(maximum, abs(size - 2 * negative))
        self.assertGreater(maximum, 0)
        self.assertLessEqual(maximum, 2 * 8 + 3)

    def test_first_ideal_sweep_pair_bound(self):
        # Include both a disjoint sweep and overlapping windows, and every ordered difference.
        for n, b in ((6, 2), (7, 3)):
            size, alphabet = 1 << n, 1 << b
            length = (n + b - 1) // b
            factor = alphabet if n % b == 0 else alphabet**2
            for initial in range(1, size):
                paths = Counter({initial: 1})
                for step in range(length):
                    shift = b * step % n
                    offsets = [((v << shift) | (v >> (n - shift))) & (size - 1) for v in range(alphabet)]
                    mask = offsets[-1]
                    updated = Counter()
                    for old, count in paths.items():
                        if old & ~mask:
                            for off in offsets:
                                updated[old ^ off] += count
                        else:
                            updated[old] += alphabet * count
                    paths = updated
                self.assertLessEqual(size * max(paths.values()), factor * alphabet**length)
                self.assertNotIn(0, paths)

    def test_translated_switch_factorization(self):
        size, bits, block = 16, 4, 1
        inv = field_inverse_table(8, 0b1011)
        p = [round_image(i, inv, bits - block, block) for i in range(size)]
        p[1], p[5] = p[5], p[1]  # Check even an unstructured perturbation.
        def rotation(x):
            return (x >> 1) | (x & 1) << (bits - 1)
        def inverse_rotation(x):
            return ((x << 1) % size) | (x >> (bits - 1))
        for keys in itertools.product(range(size), repeat=3):
            state, translated = (1, 2, 7), (1, 2, 7)
            prior = 0
            for key in keys:
                c = key ^ prior
                state = tuple(p[key ^ x] for x in state)
                translated = tuple(rotation(c ^ inverse_rotation(p[c ^ x])) for x in translated)
                prior = rotation(c)
                self.assertEqual(state, tuple(prior ^ x for x in translated))


if __name__ == "__main__":
    unittest.main()
