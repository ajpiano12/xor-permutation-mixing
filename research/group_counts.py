"""Exact arithmetic for the coset probabilities and five-bit pairwise bounds."""

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
from math import comb, factorial, prod


def gaussian(n, k):
    """Number of k-spaces in the n-dimensional binary vector space."""
    return prod(2**n - 2**i for i in range(k)) // prod(2**k - 2**i for i in range(k))


def cell_permutations(n, codimension):
    cells = 2**codimension
    return factorial(2 ** (n - codimension)) ** cells


def parity_union_count(n):
    # Möbius coefficient of a d-space in the full lattice of masks.
    return sum(
        (-1) ** (d + 1) * 2 ** (d * (d - 1) // 2) * gaussian(n, d)
        * 2**d * cell_permutations(n, d)
        for d in range(1, n + 1)
    )


def quotient_coefficients(degree):
    coeffs = [0]
    for k in range(1, degree + 1):
        earlier = sum(gaussian(k, d) * coeffs[d] * cell_permutations(k, d)
                      for d in range(1, k))
        coeffs.append(factorial(2**k) - earlier)
    return coeffs


def five_bit_bounds():
    n, size = 5, 32
    gl = prod(size - 2**i for i in range(n))
    singer = size * gl * ((size - 2) // n) // (size - 1)
    low = parity_union_count(n) + singer
    remaining = sum(gaussian(n, d) * factorial(2**d) * cell_permutations(n, d)
                    for d in (2, 3, 4))
    return Fraction(low, factorial(size)), Fraction(low + remaining, factorial(size))


def simple_counts(bits):
    """Count normalized nonlinear-simple and linear-simple maps by dimension."""
    coeffs = quotient_coefficients(bits)
    # A(z) = 1 - sum a[d] z^d. R(z) = -z A'(z)/A(z).
    a, r = [Fraction(0)], [Fraction(0)]
    irreducibles, counts = [0], [(0, 0)]
    for d in range(1, bits + 1):
        size = 2**d
        gl = prod(size - 2**i for i in range(d))
        a.append(Fraction(coeffs[d], size * gl))
        r.append(d * a[d] + sum(a[i] * r[d - i] for i in range(1, d)))
        nonlinear = (r[d] - 1) * gl / d
        assert nonlinear.denominator == 1
        smaller = sum(i * irreducibles[i] for i in range(1, d) if d % i == 0)
        irreducibles.append((size - smaller) // d)
        linear = 1 if d == 1 else gl * irreducibles[d] // (size - 1)
        counts.append((int(nonlinear), linear))
    return counts


def scientific(fraction):
    with localcontext() as context:
        context.prec = 40
        return f"{Decimal(fraction.numerator) / Decimal(fraction.denominator):.17E}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, default=5, help="last dimension for exact block-system counts")
    bits = parser.parse_args().bits
    if bits < 1:
        parser.error("bits must be positive")
    print("Quotient coefficients c1 through c4:", quotient_coefficients(4)[1:])
    for n in (3, 4, 5, 6, 7):
        npoints = 2**n
        parity = Fraction(parity_union_count(n), factorial(npoints))
        leading = Fraction(2 * (npoints - 1), comb(npoints, npoints // 2))
        print(f"n={n}  exact parity-union probability {scientific(parity)}  "
              f"leading expression {scientific(leading)}")
    lower, upper = five_bit_bounds()
    print(f"Five-bit pairwise failure interval [{scientific(lower)}, {scientific(upper)}]")
    assert parity_union_count(3) == 7232
    assert parity_union_count(4) == 48_678_419_456
    assert quotient_coefficients(3) == [0, 2, 0, 32_256]
    for d, (nonlinear, linear) in enumerate(simple_counts(bits)[1:], 1):
        size = 2**d
        total = factorial(size)
        imprimitive = total - size * (nonlinear + linear)
        # At high dimension the exact integer can exceed Python's decimal-string limit.
        count_text = str(imprimitive) if imprimitive.bit_length() < 12_000 else f"{imprimitive.bit_length()}-bit integer"
        print(f"n={d}  permutations preserving a proper nonzero coset partition: {count_text}"
              f"  probability {scientific(Fraction(imprimitive, total))}")
        if d in (3, 4, 5):
            fail = total - size * nonlinear
            print(f"     pairwise failures {fail} / {total} = {scientific(Fraction(fail, total))}")
            if d == 3:
                assert size * nonlinear == 32_256
            if d == 4:
                assert size * nonlinear == 20_873_902_694_400
            if d == 5:
                assert lower < Fraction(fail, total) < upper
