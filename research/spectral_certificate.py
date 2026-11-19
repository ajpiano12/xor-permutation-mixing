"""Certify small-error tuple mixing for an inverse-based unbalanced Feistel permutation."""
import argparse
from fractions import Fraction
import json
from math import comb, isqrt

from classify_mixing import add_table_arguments, read_table_arguments, validated_table
from inverse_triples import field_inverse_table


def polynomial_remainder(a, b):
    while a and a.bit_length() >= b.bit_length():
        a ^= b << (a.bit_length() - b.bit_length())
    return a


def irreducible(modulus, degree):
    """Every reducible binary polynomial has an irreducible factor of degree <= degree/2."""
    if degree < 1 or modulus <= 0 or modulus.bit_length() != degree + 1:
        return False
    x_power = 2
    for _ in range(1, degree // 2 + 1):
        square = sum(1 << (2 * i) for i in range(x_power.bit_length()) if x_power & (1 << i))
        x_power = polynomial_remainder(square, modulus)
        a, b = modulus, x_power ^ 2
        while b:
            a, b = b, polynomial_remainder(a, b)
        if a != 1:
            return False
    return True


def round_image(value, inverse, control_bits, block_bits):
    """XOR the projected inverse into the low block, then rotate that block to the top."""
    block_mask = (1 << block_bits) - 1
    control = value >> block_bits
    return ((value ^ inverse[control]) & block_mask) << control_bits | control


def ceil_sqrt(x):
    return 1 + isqrt(x - 1)


def block_bound(bits, block_bits, order, mismatches=0):
    """Rational, outward-rounded upper bound after two sweeps in translated coordinates."""
    if not 1 <= block_bits <= bits // 2:
        raise ValueError("block width must be between 1 and half the bit length")
    size = 1 << bits
    if not 2 <= order <= size or not 0 <= mismatches <= size:
        raise ValueError("order must be between 2 and the table size, and h must be a valid count")
    blocks = (bits + block_bits - 1) // block_bits
    alphabet = 1 << block_bits
    field_size = size // alphabet
    queries = min(order, field_size)
    if block_bits * queries >= 2 * field_size.bit_length():
        # The outward-rounded character bound already gives the trivial estimate in this regime.
        return Fraction(1)
    bias = Fraction(2 * (queries - 1) * ceil_sqrt(field_size) + queries + 1, field_size)
    layer_error = ceil_sqrt(alphabet**queries - 1) * bias / 2
    pointwise_factor = alphabet if bits % block_bits == 0 else alphabet**2
    ideal_error = Fraction(blocks * comb(order, 2) * pointwise_factor * (alphabet - 1), size)
    perturbation = Fraction(order * mismatches, size)
    return min(Fraction(1), ideal_error + 2 * blocks * (layer_error + perturbation))


def sufficient_rounds(bits, block_bits, delta, error_bits):
    if error_bits <= 0:
        raise ValueError("error bits must be positive")
    target = Fraction(1, 1 << error_bits)
    length = 2 * ((bits + block_bits - 1) // block_bits)
    if delta <= target:
        return 1 + length
    if 2 * delta >= 1:
        return None
    # Binary search gives the first certified block count without floating point.
    def reaches(blocks):
        return (2 * delta) ** blocks <= 2 * target
    low, high = 1, 2
    while not reaches(high):
        low, high = high, 2 * high
    while high - low > 1:
        middle = (high + low) // 2
        if reaches(middle):
            high = middle
        else:
            low = middle
    return 1 + length * high


def certify(bits, block_bits, order, modulus, error_bits, permutation=None):
    if not 1 <= block_bits <= bits // 2:
        raise ValueError("block width must be between 1 and half the bit length")
    control_bits = bits - block_bits
    if not irreducible(modulus, control_bits):
        raise ValueError(f"expected an irreducible binary polynomial of degree {control_bits}")
    mismatches = 0
    if permutation is not None:
        p = validated_table(permutation)
        if len(p) != 1 << bits:
            raise ValueError("table length does not match the specified bit length")
        inverse = field_inverse_table(1 << control_bits, modulus)
        mismatches = sum(y != round_image(i, inverse, control_bits, block_bits) for i, y in enumerate(p))
    delta = block_bound(bits, block_bits, order, mismatches)
    return {"input": "specified compact construction" if permutation is None else "supplied truth table",
            "bits": bits, "block_bits": block_bits, "order": order, "field_modulus": hex(modulus),
            "mismatches": mismatches, "two_sweep_tv_bound": str(delta),
            "sufficient_cipher_rounds": {f"2^-{k}": sufficient_rounds(bits, block_bits, delta, k)
                                        for k in error_bits}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, required=True)
    parser.add_argument("--block-bits", type=int, required=True)
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--modulus", type=lambda s: int(s, 0), required=True)
    parser.add_argument("--error-bits", nargs="+", type=int, default=[32, 64, 128])
    add_table_arguments(parser)
    args = parser.parse_args()
    try:
        p = read_table_arguments(parser, args) if args.images or args.file is not None else None
        result = certify(args.bits, args.block_bits, args.order, args.modulus, args.error_bits, p)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
