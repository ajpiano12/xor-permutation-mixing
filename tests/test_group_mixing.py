"""Cross-check the stabilizer-chain classifier against direct walks on ordered tuples."""

from collections import deque
from itertools import permutations
from math import gcd, perm
from random import Random
import unittest

try:
    from group_mixing import group_profile
except ModuleNotFoundError as exc:
    if exc.name != "sympy":
        raise
    group_profile = None


def direct_tuple_mixes(p, t):
    initial = tuple(range(t))
    depth = {initial: 0}
    queue = deque([initial])
    period = 0
    while queue:
        state = queue.popleft()
        next_depth = depth[state] + 1
        for key in range(len(p)):
            image = tuple(p[x ^ key] for x in state)
            if image not in depth:
                depth[image] = next_depth
                queue.append(image)
            period = gcd(period, next_depth - depth[image])
    return len(depth) == perm(len(p), t) and period == 1


@unittest.skipIf(group_profile is None, "install the optional SymPy dependency to run group checks")
class GroupMixingTests(unittest.TestCase):
    def test_direct_ordered_walks(self):
        rng = Random(49710)
        tables = [*permutations(range(2)), *permutations(range(4))]
        tables.extend(rng.sample(range(8), 8) for _ in range(12))
        for p in tables:
            max_t = group_profile(p)["mixes_through"]
            for t in range(1, min(len(p), 4) + 1):
                self.assertEqual(t <= max_t, direct_tuple_mixes(p, t), (p, t))

    def test_hidden_affine_and_cycle_certificate(self):
        p = (0, 2, 4, 7, 8, 10, 15, 12, 1, 3, 5, 6, 9, 11, 14, 13)
        result = group_profile(p)
        self.assertEqual((result["mixes_through"], result["closure_order"]), (3, 322560))

        cycle = list(range(1, 11)) + [0] + list(range(11, 16))
        result = group_profile(cycle)
        self.assertEqual(result["cycle_witness"]["prime_length"], 11)
        self.assertEqual(result["mixes_through"], 14)

    def test_hidden_field_lines(self):
        # GF(4) in the basis 1,s, with s*s = s+1.
        def hidden(x):
            a, b = (x >> 2) & 3, x >> 4
            sa = (a << 1) ^ (7 if a & 2 else 0)
            product = (a if b & 1 else 0) ^ (sa if b & 2 else 0)
            return x ^ product

        p = []
        for x in range(64):
            y = hidden(x)
            rotated = ((y << 2) & 63) | (y >> 4)
            p.append(hidden(rotated))
        result = group_profile(p)
        self.assertEqual((result["mixes_through"], result["closure_order"]), (2, 3870720))
