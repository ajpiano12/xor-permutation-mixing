"""Certify small-error tuple mixing for a rotating unbalanced Feistel permutation."""
import argparse
from fractions import Fraction
import json
from math import comb, isqrt

from classify_mixing import add_table_arguments, read_table_arguments, validated_table
from inverse_triples import field_inverse_table
from power_mixing import multiply


CONTROLS = ("inverse", "power15", "polynomial15")


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
    """XOR a projected control-table entry into the low block and rotate to the top."""
    block_mask = (1 << block_bits) - 1
    control = value >> block_bits
    return ((value ^ inverse[control]) & block_mask) << control_bits | control


def ceil_sqrt(x):
    return 1 + isqrt(x - 1)


def power15(value, modulus):
    """Compute x^15 as (x^3)^4 * x^3 in the control field."""
    cube = multiply(multiply(value, value, modulus), value, modulus)
    sixth = multiply(cube, cube, modulus)
    return multiply(multiply(sixth, sixth, modulus), cube, modulus)


def polynomial_value(value, coefficients, modulus):
    """Evaluate coefficients in ascending degree order over the binary field."""
    result = coefficients[-1]
    for coefficient in reversed(coefficients[:-1]):
        result = multiply(result, value, modulus) ^ coefficient
    return result


def block_bound(bits, block_bits, order, mismatches=0, *, control="inverse"):
    """Rational, outward-rounded upper bound for tuple differences after two sweeps."""
    if not 1 <= block_bits <= bits // 2:
        raise ValueError("block width must be between 1 and half the bit length")
    size = 1 << bits
    if not 2 <= order <= size or not 0 <= mismatches <= size:
        raise ValueError("order must be between 2 and the table size, and h must be a valid count")
    if control not in CONTROLS:
        raise ValueError(f"control must be one of {', '.join(CONTROLS)}")
    if control != "inverse" and order > 4:
        raise ValueError("the degree-15 certificate covers tuple orders 2 through 4")
    blocks = (bits + block_bits - 1) // block_bits
    alphabet = 1 << block_bits
    field_size = size // alphabet
    queries = min(order, field_size)
    relative_bits = block_bits * (queries - 1)
    if relative_bits >= 2 * field_size.bit_length():
        # The outward-rounded character bound already gives the trivial estimate in this regime.
        return Fraction(1)
    root = ceil_sqrt(field_size)
    if control != "inverse":
        # The weighted translates have zero coefficient sum and reduced odd degree <= 13.
        bias = Fraction(12 * root, field_size)
    else:
        bias = Fraction(2 * (queries - 1) * root + queries + 1, field_size)
    # Common block offsets cancel from all tuple differences.
    layer_error = ceil_sqrt((1 << relative_bits) - 1) * bias / 2
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


def certify(bits, block_bits, order, modulus, error_bits, permutation=None, *,
            control="inverse", coefficients=None):
    if not 1 <= block_bits <= bits // 2:
        raise ValueError("block width must be between 1 and half the bit length")
    control_bits = bits - block_bits
    field_size = 1 << control_bits
    if not irreducible(modulus, control_bits):
        raise ValueError(f"expected an irreducible binary polynomial of degree {control_bits}")
    if control == "polynomial15":
        if coefficients is None or len(coefficients) != 16:
            raise ValueError("polynomial15 needs exactly 16 coefficients in constant-to-leading order")
        if any(not isinstance(c, int) or not 0 <= c < field_size for c in coefficients):
            raise ValueError(f"each coefficient must be a control-field integer from 0 to {field_size - 1}")
        if coefficients[-1] == 0:
            raise ValueError("the degree-15 leading coefficient must be nonzero")
    elif coefficients is not None:
        raise ValueError("specify coefficients only for the polynomial15 control")
    delta = block_bound(bits, block_bits, order, control=control)
    mismatches = 0
    if permutation is not None:
        p = validated_table(permutation)
        if len(p) != 1 << bits:
            raise ValueError("table length does not match the specified bit length")
        if control == "power15":
            values = [power15(z, modulus) for z in range(field_size)]
        elif control == "polynomial15":
            values = [polynomial_value(z, coefficients, modulus) for z in range(field_size)]
        else:
            values = field_inverse_table(field_size, modulus)
        mismatches = sum(y != round_image(i, values, control_bits, block_bits) for i, y in enumerate(p))
        delta = block_bound(bits, block_bits, order, mismatches, control=control)
    result = {"input": "specified compact construction" if permutation is None else "supplied truth table",
              "bits": bits, "block_bits": block_bits, "order": order, "control": control, "field_modulus": hex(modulus),
              "mismatches": mismatches, "two_sweep_tv_bound": str(delta),
              "sufficient_cipher_rounds": {f"2^-{k}": sufficient_rounds(bits, block_bits, delta, k)
                                          for k in error_bits}}
    if coefficients is not None:
        result["coefficients"] = list(coefficients)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, required=True)
    parser.add_argument("--block-bits", type=int, required=True)
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--control", choices=CONTROLS, default="inverse",
                        help="control-field update (degree-15 updates are certified up to four inputs)")
    parser.add_argument("--coefficients", type=lambda s: int(s, 0), nargs=16, metavar="C",
                        help="16 field elements, from the constant to the leading coefficient, for polynomial15")
    parser.add_argument("--modulus", type=lambda s: int(s, 0), required=True)
    parser.add_argument("--error-bits", nargs="+", type=int, default=[32, 64, 128])
    parser.add_argument("--sweep-analysis", action="store_true",
                        help="also calculate short warmup and disjoint-window sweep bounds")
    add_table_arguments(parser)
    args = parser.parse_args()
    try:
        p = read_table_arguments(parser, args) if args.images or args.file is not None else None
        result = certify(args.bits, args.block_bits, args.order, args.modulus, args.error_bits, p,
                         control=args.control, coefficients=args.coefficients)
        if args.sweep_analysis:
            from research.sweep_bounds import sweep_analysis
            result["improved_sweep_bounds"] = sweep_analysis(
                args.bits, args.block_bits, args.order, args.error_bits, result["mismatches"], args.control)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
