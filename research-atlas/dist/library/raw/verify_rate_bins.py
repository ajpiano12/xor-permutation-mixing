"""Certify a lower bound on the number of distinct four-bit mixing rates.

For the 15 nonzero differences, let B = 8Q, where Q is the transition
matrix. Each unordered input pair with a given difference contributes one
integer count. The rows of B sum to 8. Removing one factor (x - 8) from
its characteristic polynomial leaves the eigenvalues on the quotient by
constant functions. For an ergodic chain their largest modulus is 8*rho,
where rho is the asymptotic exponential rate of worst-start TV distance.
Twice that distance is the maximum absolute row sum of (Q - U)**k for
k >= 1 and U the uniform-row matrix, so the spectral radius formula applies.

For rational r > 0, rho < r exactly when f(8*r*z) has all roots strictly
inside the unit disk. The real-coefficient Schur recursion tests this with
integer arithmetic. For descending coefficients and leading and constant
terms a and b, strict stability requires |b| < |a|. Under this condition,
p is strictly stable iff (a*p - b*z**deg(p)*p(1/z))/z is strictly stable.
Indeed the reversed polynomial has the same modulus as p on the circle.
A boundary zero persists in the reduction. Otherwise Rouché's theorem
shows that the numerator and p have the same number of interior zeros,
and dividing by z removes one. A boundary zero therefore fails the test.

Two such decisions certify a half-open interval [k/s, (k+1)/s). Distinct
occupied intervals require distinct rates. The CSV rate only proposes a
bin. Skipping further candidates for an already certified bin preserves
the lower bound, even if a proposed bin was inaccurate.
"""

import argparse
import csv
from fractions import Fraction
from itertools import islice
from math import gcd
from pathlib import Path


def nonstationary_polynomial(permutation):
    """Return descending integer coefficients of det(xI - B)/(x - 8)."""
    if sorted(permutation) != list(range(16)):
        raise ValueError(f"Invalid four-bit permutation {permutation}")
    counts = [[0] * 15 for _ in range(15)]
    for x in range(16):
        for y in range(x):
            counts[(x ^ y) - 1][(permutation[x] ^ permutation[y]) - 1] += 1

    # Newton identities recover each coefficient from traces of powers.
    columns = list(zip(*counts))
    power = counts
    traces = [0]
    coeffs = [1]
    for k in range(1, 16):
        traces.append(sum(power[i][i] for i in range(15)))
        numerator = -sum(coeffs[j] * traces[k - j] for j in range(k))
        coeff, remainder = divmod(numerator, k)
        assert remainder == 0
        coeffs.append(coeff)
        if k < 15:
            power = [
                [sum(a * b for a, b in zip(row, col)) for col in columns]
                for row in power
            ]

    quotient = [1]
    for coeff in coeffs[1:]:
        quotient.append(coeff + 8 * quotient[-1])
    remainder = quotient.pop()
    assert remainder == 0
    return quotient


def roots_inside_radius(coeffs, numerator, denominator):
    """Test max |root| < numerator/denominator, including boundary cases."""
    if numerator <= 0:
        return False
    common = gcd(numerator, denominator)
    numerator //= common
    denominator //= common
    degree = len(coeffs) - 1
    c = [v * numerator**(degree - i) * denominator**i for i, v in enumerate(coeffs)]
    while len(c) > 1:
        lead, tail = c[0], c[-1]
        if abs(tail) >= abs(lead):
            return False
        if tail == 0:
            c.pop()
        else:
            c = [lead * x - tail * y for x, y in zip(c[:-1], reversed(c[1:]))]
            common = gcd(*c)
            c = [v // common for v in c]
    return True


def certified_bin(coeffs, guess, scale):
    def below(boundary):
        return roots_inside_radius(coeffs, 8 * boundary, scale)

    if not below(guess) and below(guess + 1):
        return guess
    # Recover from a rounded or inaccurate estimate by monotone bisection.
    low, high = 0, scale
    if not below(high):
        raise ValueError("A row marked mixing has a nonstationary rate >= 1")
    while high - low > 1:
        mid = (low + high) // 2
        if below(mid):
            high = mid
        else:
            low = mid
    return low


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("samples", type=Path, nargs="?",
                        default=Path("results/four_bit/samples.csv"))
    parser.add_argument("--limit", type=int, help="maximum number of mixing rows to read")
    parser.add_argument("--scale", type=int, default=1000, help="bins per unit (default 1000)")
    args = parser.parse_args()
    if args.scale < 1 or (args.limit is not None and args.limit < 1):
        parser.error("--scale and --limit must be positive")

    occupied = set()
    audited = 0
    seen = 0
    with args.samples.open(newline="") as stream:
        mixing_rows = (row for row in csv.DictReader(stream) if row["status"] == "mixing")
        for row in islice(mixing_rows, args.limit):
            seen += 1
            rate = Fraction(row["rate"])
            guess = min(args.scale - 1, max(0, int(rate * args.scale)))
            if guess in occupied:
                continue
            permutation = [int(item) for item in row["permutation"].split()]
            occupied.add(certified_bin(nonstationary_polynomial(permutation), guess, args.scale))
            audited += 1
    print(f"Read {seen} mixing rows and certified {audited} witnesses.")
    print(f"At least {len(occupied)} distinct asymptotic rates (bin width 1/{args.scale}).")


if __name__ == "__main__":
    main()
