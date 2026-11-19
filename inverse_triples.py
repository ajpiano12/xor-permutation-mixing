"""Certify a finite triple-mixing bound by comparison with a binary field inverse."""
import argparse
from fractions import Fraction
import json

from classify_mixing import add_table_arguments, read_table_arguments, validated_table


def field_inverse_table(size, modulus):
    """Invert polynomials by the extended Euclidean algorithm over GF(2)."""
    if size < 2 or size & (size - 1) or modulus.bit_length() != size.bit_length() or modulus <= 0:
        raise ValueError("supply a positive binary modulus of degree equal to the bit length of the inputs")
    result = [0]
    for x in range(1, size):
        u, v = x, modulus
        c, d = 1, 0
        while u != 1:
            if not u:
                raise ValueError("the binary modulus is reducible")
            shift = u.bit_length() - v.bit_length()
            if shift < 0:
                u, v = v, u
                c, d = d, c
                shift = -shift
            u ^= v << shift
            c ^= d << shift
        while c >= size:
            c ^= modulus << (c.bit_length() - modulus.bit_length())
        result.append(c)
    return result


def triple_certificate(p, modulus):
    p = validated_table(p)
    if len(p) < 4:
        raise ValueError("at least three distinct inputs are required")
    field_inverse = field_inverse_table(len(p), modulus)
    mismatches = sum(a != b for a, b in zip(p, field_inverse))
    bound = min(Fraction(1), Fraction(7 + 6 * mismatches, len(p)))
    return mismatches, bound


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_table_arguments(parser)
    parser.add_argument("--modulus", required=True, type=lambda s: int(s, 0),
                        help="binary field modulus, e.g. 0x25 for X^5 + X^2 + 1")
    parser.add_argument("--epsilon", type=Fraction, default=Fraction(1, 1 << 128), help="target TV (default 2^-128)")
    args = parser.parse_args()
    if not 0 < args.epsilon < 1:
        parser.error("epsilon must lie strictly between zero and one")
    try:
        p = read_table_arguments(parser, args)
        mismatches, delta = triple_certificate(p, args.modulus)
    except ValueError as exc:
        parser.error(str(exc))
    rounds = 3
    error = delta
    if delta < Fraction(1, 2):
        while error > args.epsilon:
            error *= 2 * delta
            rounds += 3
    print(json.dumps({"mismatches": mismatches, "three_round_tv_upper_bound": str(delta),
                      "epsilon": str(args.epsilon),
                      "sufficient_cipher_rounds": rounds if error <= args.epsilon else None}))


if __name__ == "__main__":
    main()
