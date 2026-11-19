"""Certify a pairwise round bound for a quadratic APN permutation table."""
import argparse
from fractions import Fraction
import json

from classify_mixing import add_table_arguments, read_table_arguments, validated_table


def has_certificate(permutation):
    p = validated_table(permutation)
    n = len(p).bit_length() - 1
    coefficients = list(p)
    for bit in (1 << i for i in range(n)):
        for x in range(len(p)):
            if x & bit:
                coefficients[x] ^= coefficients[x ^ bit]
    if any(c and index.bit_count() > 2 for index, c in enumerate(coefficients)):
        return False
    for a in range(1, len(p)):
        pivots = [0] * n
        rank = 0
        origin = p[0] ^ p[a]
        for i in range(n):
            vector = origin ^ p[1 << i] ^ p[(1 << i) ^ a]
            while vector:
                j = vector.bit_length() - 1
                if not pivots[j]:
                    pivots[j] = vector
                    rank += 1
                    break
                vector ^= pivots[j]
        if rank != n - 1:
            return False
    return True


def sufficient_rounds(size, epsilon):
    """Solve (N-2)/N^(r-1) <= 4 epsilon^2 without floating-point rounding."""
    rounds = 1
    left = (size - 2) * epsilon.denominator**2
    right = 4 * epsilon.numerator**2
    while left > right:
        right *= size
        rounds += 1
    return rounds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_table_arguments(parser)
    parser.add_argument("--epsilon", type=Fraction, default=Fraction(1, 4))
    args = parser.parse_args()
    if not 0 < args.epsilon < 1:
        parser.error("epsilon must be between zero and one")
    p = read_table_arguments(parser, args)
    try:
        proved = has_certificate(p)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({"certified": proved, "epsilon": str(args.epsilon),
                      "sufficient_cipher_rounds": sufficient_rounds(len(p), args.epsilon) if proved else None}))


if __name__ == "__main__":
    main()
