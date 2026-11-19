"""Certify pairwise TV for finite-field powers, or compute exact hitting times."""
import argparse
from fractions import Fraction
import json
from math import gcd, isqrt

from classify_mixing import add_table_arguments, read_table_arguments, validated_table
from inverse_triples import field_inverse_table


def multiply(a, b, modulus):
    value = 0
    size = 1 << (modulus.bit_length() - 1)
    while b:
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
        if a & size:
            a ^= modulus
    return value


def field_cycle(modulus):
    """Powers of a generator and discrete logs in the supplied polynomial basis."""
    if modulus < 2:
        raise ValueError("supply a binary irreducible polynomial of positive degree")
    size = 1 << (modulus.bit_length() - 1)
    field_inverse_table(size, modulus)  # checks irreducibility
    order = size - 1
    remaining = order
    primes = []
    for p in range(2, isqrt(order) + 1):
        if remaining % p == 0:
            primes.append(p)
            while remaining % p == 0:
                remaining //= p
    if remaining > 1:
        primes.append(remaining)

    def power(base, k):
        result = 1
        while k:
            if k & 1:
                result = multiply(result, base, modulus)
            base = multiply(base, base, modulus)
            k >>= 1
        return result

    generator = next(g for g in range(1, size) if all(power(g, order // p) != 1 for p in primes))
    powers, logs = [], [0] * size
    x = 1
    for j in range(order):
        powers.append(x)
        logs[x] = j
        x = multiply(x, generator, modulus)
    return powers, logs


def field_powers(modulus, exponent):
    powers, logs = field_cycle(modulus)
    m = len(powers)
    if gcd(exponent, m) != 1:
        raise ValueError("exponent must be coprime to the multiplicative group order")
    return [0] + [powers[(exponent * j) % m] for j in logs[1:]]


def algebraic_bound(bits, power, changes, security):
    """Bound with integer arithmetic only. Input descriptions need no truth table."""
    if bits < 1 or security < 1:
        raise ValueError("bits and security must be positive")
    size = 1 << bits
    m = size - 1
    if not 0 <= changes <= size or gcd(power, m) != 1:
        raise ValueError("choose a power coprime to 2^n−1 and 0 <= changes <= 2^n")
    if size == 2:
        return {"sufficient_cipher_rounds": 1}
    # Frobenius twists permute the characters isometrically. Inversion of the
    # permutation transposes its difference kernel and preserves its operator norm.
    upper_root = isqrt(size - 1) + 1
    candidates = []
    for d in {power % m, pow(power, -1, m)}:
        for _ in range(bits):
            for negative, degree in [(False, d), (True, m - d)]:
                if degree % 2 == 0 or (not negative and degree == 1):
                    continue
                a = degree if negative else degree - 2
                b = 4 * changes + (2 if negative else 0)
                squared = Fraction(a*a*size + 2*a*b*upper_root + b*b, size*size)
                candidates.append((squared, -degree if negative else degree, "character sum"))
            d = (2 * d) % m
    residue = power % m
    if changes == 0 and residue.bit_count() != 1:
        # The Lenstra/Stafford criterion rules out a proper multiplicative noise subgroup.
        # Every character sees two unequal phases, each with mass at least 2/N.
        gap = Fraction(8, size * m * m)
        candidates.append(((1 - gap)**2, residue, "subgroup bound"))
    if not candidates:
        return {"sufficient_cipher_rounds": None}
    rho2, degree, method = min(candidates)
    answer = {"method": method, "equivalent_signed_degree": degree, "squared_norm_upper": str(rho2),
              "sufficient_cipher_rounds": None}
    if rho2 >= 1:
        return answer
    target_bits = max(0, 2 * security + (size - 3).bit_length() - 2)
    # Guarantee (rho²)^steps <= 2^(-target_bits), including very small gaps.
    gain = (rho2.denominator // rho2.numerator).bit_length() - 1
    if gain:
        high = (target_bits + gain - 1) // gain
        low = 0
        while low < high:
            mid = (low + high) // 2
            if ((size - 2) * pow(rho2.numerator, mid) << (2 * security)) <= 4 * pow(rho2.denominator, mid):
                high = mid
            else:
                low = mid + 1
        steps = low
    else:
        gap = rho2.denominator - rho2.numerator
        block = (rho2.numerator + gap - 1) // gap
        steps = block * target_bits
    answer["sufficient_cipher_rounds"] = steps + 1
    return answer


def cyclic_convolution(left, right):
    """Multiply nonnegative integer vectors in Z[z]/(z^m-1) by digit packing."""
    m = len(left)
    width = max(1, ((sum(left) * sum(right)).bit_length() + 7) // 8)
    def packed(v):
        return int.from_bytes(b"".join(x.to_bytes(width, "little") for x in v), "little")
    digits = (packed(left) * packed(right)).to_bytes(width * (2 * m - 1), "little")
    result = [0] * m
    for i in range(2 * m - 1):
        result[i % m] += int.from_bytes(digits[i*width:(i+1)*width], "little")
    return result


def exact_times(modulus, power, security_bits):
    if not security_bits or min(security_bits) < 1:
        raise ValueError("security exponents must be positive")
    powers, logs = field_cycle(modulus)
    m = len(powers)
    if gcd(power, m) != 1:
        raise ValueError("power does not define a permutation")
    p = [0] + [powers[(power * j) % m] for j in logs[1:]]
    noise = [0] * m
    for x in range(0, m + 1, 2):  # unordered {x,x xor 1}, with one vote per pair
        noise[logs[p[x] ^ p[x ^ 1]]] += 1
    subgroup_index = m
    for i, count in enumerate(noise):
        if count:
            subgroup_index = gcd(subgroup_index, i)  # log(1)=0 belongs to support
    if subgroup_index > 1:
        return {"mixes": False, "subgroup_index": subgroup_index, "rounds": {}}
    drift = [(power * j) % m for j in range(m)]
    counts = [1] + [0] * (m - 1)
    denominator = 1
    rounds = {}
    pending = sorted(set(security_bits))
    steps = 0
    while True:
        deviation = sum(abs(m * c - denominator) for c in counts)
        while pending and (deviation << pending[0]) <= 2 * m * denominator:
            rounds[pending.pop(0)] = steps + 1
        if not pending:
            return {"mixes": True, "subgroup_index": 1, "rounds": rounds}
        shifted = [0] * m
        for i, image in enumerate(drift):
            shifted[image] = counts[i]
        counts = cyclic_convolution(shifted, noise)
        denominator *= (m + 1) // 2
        steps += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    bound = sub.add_parser("bound", help="algebraic round guarantee from a compact power description")
    bound.add_argument("--bits", type=int, required=True)
    bound.add_argument("--changes", type=int, default=0, help="known upper bound on altered entries")
    verify = sub.add_parser("verify", help="check a supplied table against a power in a given basis")
    add_table_arguments(verify)
    exact = sub.add_parser("exact", help="minimal rounds from one derivative row, for modest field sizes")
    for cmd in (exact, verify):
        cmd.add_argument("--modulus", required=True, type=lambda s: int(s, 0))
    for cmd in (bound, verify, exact):
        cmd.add_argument("--power", type=int, required=True, help="zero is fixed, including for negative exponents")
        cmd.add_argument("--security", nargs="+", type=int, default=[32, 64, 128], help="target TV is 2^(-k)")
    args = parser.parse_args()
    try:
        if args.mode == "exact":
            result = exact_times(args.modulus, args.power, args.security)
        else:
            if args.mode == "verify":
                table = validated_table(read_table_arguments(parser, args))
                bits = len(table).bit_length() - 1
                if args.modulus <= 0 or args.modulus.bit_length() != bits + 1:
                    raise ValueError("modulus degree and table width must agree")
                expected = field_powers(args.modulus, args.power)
                changes = sum(x != y for x, y in zip(table, expected))
            else:
                bits, changes = args.bits, args.changes
            result = {"bits": bits, "power": args.power, "changes": changes,
                      "bounds": {k: algebraic_bound(bits, args.power, changes, k) for k in args.security}}
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
