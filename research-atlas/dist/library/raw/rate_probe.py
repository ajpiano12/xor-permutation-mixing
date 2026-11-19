"""Audit two-step reuse identities and measure worst-start total variation."""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import permutations
from math import factorial
from statistics import median

import numpy as np


def transition_counts(p):
    """One row per nonzero XOR difference, counting all base points."""
    n = len(p)
    x = np.arange(n)
    a = x[1:, None]
    outcomes = p[x] ^ p[a ^ x]
    codes = (a - 1) * n + outcomes
    return np.bincount(codes.ravel(), minlength=(n - 1) * n).reshape(n - 1, n)[:, 1:]


def verify_small(n):
    # Translating outputs leaves the difference table unchanged.
    m = n - 1
    count = factorial(m)
    sum_squares = np.zeros((m, m), dtype=np.int64)
    sum_energy = 0
    apn_tables = Counter()
    for tail in permutations(range(1, n)):
        t = transition_counts(np.array((0, *tail)))
        sum_squares += t @ t
        sum_energy += np.sum(t * t)
        if n == 8 and t.max() == 2:
            apn_tables[t.tobytes()] += n
    # E[T²] = U + 2/[N(N-3)] (I-U), removing all denominators.
    eye = np.eye(m, dtype=np.int64)
    assert np.all(sum_squares * m * n * (n - 3) ==
                  count * n**2 * (n * (n - 3) + 2 * (m * eye - 1)))
    # E[||T-U||_F²] = 2(N-2)² / [N(N-3)].
    assert (sum_energy - count * n**2) * n * (n - 3) == count * n**2 * 2 * (n - 2)**2
    if n == 8:
        assert Counter(apn_tables.values()) == {64: 168}


def distances(p):
    n = len(p)
    m = n - 1
    counts = transition_counts(p)
    distances_one = np.abs(m * counts - n).sum(axis=1) / (2 * m * n)
    # A binary64 sum of these integer products is exact while N² <= 2^53.
    two = counts.astype(np.float64)
    two = two @ two
    distances_two = np.abs(m * two - n**2).sum(axis=1) / (2 * m * n**2)
    return float(distances_one.max()), float(distances_two.max()), bool(np.all(two > 0))


def verify_inverses():
    """Check the trace formula for the inverse against direct difference counts."""
    for bits, modulus in enumerate((0x7, 0xB, 0x13, 0x25, 0x43, 0x83, 0x11B), 2):
        n = 1 << bits

        def multiply(a, b):
            product = 0
            while b:
                if b & 1:
                    product ^= a
                b >>= 1
                a <<= 1
                if a & n:
                    a ^= modulus
            return product

        field = np.array([[multiply(x, y) for y in range(n)] for x in range(n)])
        inverse = np.concatenate(([0], np.argmax(field[1:] == 1, axis=1)))
        assert np.all(field[np.arange(1, n), inverse[1:]] == 1)
        trace = np.zeros(n, dtype=int)
        power = np.arange(n)
        for _ in range(bits):
            trace ^= power
            power = field[power, power]
        assert np.all((trace == 0) | (trace == 1))
        character = 1 - 2 * trace
        ratios = field[inverse[1:], 1:]
        predicted = (n + (n + 4) * (ratios == 1)
                     + 2 * character[ratios] + 2 * character[inverse[ratios]])
        t = transition_counts(inverse)
        assert np.array_equal(t @ t, predicted)
        k = sum(int(s) for s in character[np.arange(1, n) ^ inverse[1:]])
        both_zero = (n - 3 + k) // 4 - int(bits % 2 == 0)
        exact = (Fraction(2 * n + 4 + 4 * (-1)**bits, n**2) - Fraction(1, n-1)
                 + both_zero * (Fraction(n + 4, n**2) - Fraction(1, n-1)))
        direct = Fraction(int(np.max(np.abs((n-1) * predicted - n**2).sum(axis=1))),
                          2 * (n-1) * n**2)
        assert direct == exact
        print(f"Inverse with {bits} bits: d2 = {exact}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20261118)
    parser.add_argument("--samples", type=int, default=100)
    parser.add_argument("--bits", type=int, nargs="+", default=[4, 5, 6, 7, 8, 9])
    args = parser.parse_args()
    if args.samples < 1 or any(n < 2 or n > 13 for n in args.bits):
        parser.error("use positive sample size and block sizes 2 through 13 for dense matrices")
    for n in (4, 8):
        verify_small(n)
    print("Exact mean and one-step energy verified for N=4 and N=8.")
    verify_inverses()
    rng = np.random.default_rng(args.seed)
    print("bits | median d1 | median d2 | d2 <= 1/4 | T^2 positive")
    for bits in args.bits:
        rows = [distances(rng.permutation(1 << bits)) for _ in range(args.samples)]
        d1, d2, positive = zip(*rows)
        print(f"{bits} | {median(d1):.5f} | {median(d2):.5f} | "
              f"{sum(d <= 0.25 for d in d2)}/{args.samples} | "
              f"{sum(positive)}/{args.samples}")


if __name__ == "__main__":
    main()
