"""Certify slow pairwise mixing near affine maps and bound the one-transposition family."""
import argparse
from collections import Counter
from fractions import Fraction
import json

from classify_mixing import add_table_arguments, read_table_arguments, validated_table


def rounded_power(base, exponent, precision, *, upper):
    """Enclose a nonnegative rational power on a binary grid by repeated squaring."""
    scale = 1 << precision
    rounding = scale - 1 if upper else 0
    value = (base.numerator * scale + (base.denominator - 1 if upper else 0)) // base.denominator
    result = scale
    while exponent:
        if exponent & 1:
            result = (result * value + rounding) // scale
        exponent >>= 1
        value = (value * value + rounding) // scale
    return Fraction(result, scale)


def crossing_bound(base, threshold, precision, *, upper):
    """Return a sufficient or necessary integer exponent for base**k <= threshold."""
    if threshold >= 1:
        return 0
    lo, hi = 0, 1
    while rounded_power(base, hi, precision, upper=upper) > threshold:
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if rounded_power(base, mid, precision, upper=upper) > threshold:
            lo = mid
        else:
            hi = mid
    # For a lower bound, the last lower enclosure above threshold certifies hi−1 fails.
    return hi


def close_affine(permutation):
    """Recover the unique affine map if its table differs on fewer than N/4 inputs."""
    p = validated_table(permutation)
    size = len(p)
    if size < 4:
        raise ValueError("at least two input bits are required")
    columns = []
    for i in range(size.bit_length() - 1):
        step = 1 << i
        # Each unordered pair has the same derivative in both orientations.
        counts = Counter(p[x] ^ p[x | step] for x in range(size) if not x & step)
        column, count = counts.most_common(1)[0]
        if 4 * count <= size:
            return None
        columns.append(column)
    values = [0] * size
    for x in range(1, size):
        bit = x & -x
        values[x] = values[x ^ bit] ^ columns[bit.bit_length() - 1]
    offset, count = Counter(image ^ linear for image, linear in zip(p, values)).most_common(1)[0]
    h = size - count
    return (columns, offset, h) if 4 * h < size else None


def table_bounds(permutation, error_bits):
    if error_bits < 1:
        raise ValueError("error bits must be positive")
    fit = close_affine(permutation)
    if fit is None:
        return {"status": "no affine approximation within the strict N/4 radius"}
    columns, offset, h = fit
    size = 1 << len(columns)
    answer = {"columns": columns, "offset": offset, "mismatches": h, "bits": len(columns)}
    if h == 0:
        return {**answer, "status": "affine; pair distances never converge"}
    base = Fraction(size - 4*h, size)
    precision = len(columns) + 2 * error_bits + 32
    k = crossing_bound(base, Fraction(2, 1 << error_bits), precision, upper=False)
    return {**answer, "status": "necessary rounds certified", "epsilon_bits": error_bits,
            "necessary_cipher_rounds": 1 + k}


def family_bounds(bits, error_bits, order=2):
    """Applicable to a linear cycle on nonzero points with two table entries swapped."""
    if bits < 4 or error_bits < 1 or not 2 <= order <= 1 << bits:
        raise ValueError("family requires at least four bits, positive error bits and a valid tuple order")
    size = 1 << bits
    m = size - 1
    p = Fraction(4, size)
    precision = bits + 2 * error_bits + 32
    target = Fraction(1, 1 << error_bits)
    base = 1 - 2*p
    necessary = crossing_bound(base, 4 * target**2, precision, upper=False)
    answer = {"bits": bits, "order": order, "epsilon_bits": error_bits,
              "necessary_cipher_rounds": 1 + necessary}
    if order > 2:
        # Compare one uniformly sampled matching edge to independent label moves.
        q = Fraction(2, size)
        one_epoch_error = order * (order - 1) * q * (1 + 3*m*q)
        one_label = rounded_power(1 - 2*q, size // 2, precision, upper=True)
        pairs = order * (order - 1) // 2
        best_epochs = None
        if order*q <= 1:
            for batch in range(1, bits + 1):
                comparison = 2*batch*one_epoch_error
                if comparison >= 1:
                    break
                factor = pairs * rounded_power(one_label, 2*batch, precision, upper=True) + comparison
                if factor < 1:
                    epochs = batch * crossing_bound(factor, target, precision, upper=True)
                    if best_epochs is None or epochs < best_epochs:
                        best_epochs = epochs
        return {**answer, "sufficient_epochs": best_epochs,
                "sufficient_cipher_rounds": None if best_epochs is None else 1 + m*best_epochs}
    alpha = rounded_power(base, size // 2, precision, upper=True)
    single = m*p*rounded_power(1 - p, m - 1, precision, upper=False)
    contraction = min(1 - single, alpha + 2*p*(1 + m*p))
    epochs = crossing_bound(contraction, target * m / (m - 1), precision, upper=True)
    return {**answer, "sufficient_cipher_rounds": 1 + m*epochs, "sufficient_epochs": epochs,
            "epoch_contraction_upper": str(contraction)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    table = sub.add_parser("table", help="search a supplied table for a certified slow affine approximation")
    add_table_arguments(table)
    family = sub.add_parser("family", help="bounds for a linear full cycle with two entries swapped")
    family.add_argument("--bits", type=int, required=True)
    family.add_argument("--order", type=int, default=2, help="number of distinct inputs to track")
    for cmd in (table, family):
        cmd.add_argument("--error-bits", type=int, default=128, help="target total variation is 2^(-error-bits)")
    args = parser.parse_args()
    try:
        if args.command == "table":
            result = table_bounds(read_table_arguments(parser, args), args.error_bits)
        else:
            result = family_bounds(args.bits, args.error_bits, args.order)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
