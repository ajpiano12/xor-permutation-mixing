"""Certified round bounds for the rotating update, using short warmups and sweep norms."""
from fractions import Fraction
from math import comb, isqrt


def sqrt_upper(x):
    """An outward-rounded rational square root with at least 64 significant bits."""
    if x == 0:
        return Fraction(0)
    precision = max(0, 65 + (x.denominator.bit_length() - x.numerator.bit_length()) // 2)
    numerator = x.numerator << (2 * precision)
    root = isqrt(numerator // x.denominator)
    return Fraction(root + (root * root * x.denominator < numerator), 1 << precision)


def bias_bound(bits, width, order, control):
    q = 1 << (bits - width)
    field_root = sqrt_upper(Fraction(q))
    if control == "inverse":
        return min(1, (2 * (order - 1) * field_root + order + 1) / q)
    return min(1, 12 * field_root / q)


def collision_sum(a, warmup, count, cap):
    """Pair-collision upper bounds across consecutive writes after a warmup."""
    return sum(a ** min(warmup + j, cap) for j in range(count))


def warmup_blocks(bits, width, order, beta, mismatches):
    """Map block lengths to upper bounds on twice their worst row TV."""
    size, alphabet = 1 << bits, 1 << width
    d = (bits + width - 1) // width
    cap = bits // width - 1
    q = size // alphabet
    parity_bits = width * (min(q, order) - 1)
    # Every available beta is >= 1/sqrt(q). In this case even one layer is trivial.
    if parity_bits > 2 * (bits - width):
        return {}
    chi_sq = ((1 << parity_bits) - 1) * beta**2
    if chi_sq >= 1:
        return {}
    choices = {}
    for warmup in range(1, cap + 1):
        length = warmup + d
        ideal = comb(order, 2) * collision_sum(Fraction(1, alphabet), warmup, d, cap)
        real = sqrt_upper((1 + chi_sq) ** length - 1) / 2
        delta = ideal + real + Fraction(length * order * mismatches, size)
        if 2 * delta < 1:
            choices[length] = 2 * delta
    return choices


def required_repeats(factor, target):
    """Least k>=0 with factor^k<=target for 0<factor<1 and target>0."""
    if target >= 1:
        return 0
    low, high = 0, 1
    while factor**high > target:
        low, high = high, high * 2
    while high - low > 1:
        mid = (low + high) // 2
        if factor**mid <= target:
            high = mid
        else:
            low = mid
    return high


def mixed_warmup_rounds(choices, error_bits):
    """Minimize the total length among products of the certified blocks."""
    if not choices:
        return {}
    # Using a fixed number of fractional bits keeps the dynamic program small,
    # and rounding every product up preserves the certificate.
    precision = max(error_bits) + 64
    scale = 1 << precision
    best = [scale]
    result = {}
    pending = sorted(set(error_bits))
    while pending:
        budget = len(best)
        value = best[-1]
        for length, factor in choices.items():
            if length <= budget:
                product = best[budget-length] * factor.numerator
                rounded = (product + factor.denominator - 1) // factor.denominator
                value = min(value, rounded)
        best.append(value)
        while pending and budget >= min(choices) and value <= (1 << (precision + 1 - pending[0])):
            result[pending.pop(0)] = budget + 1
        # Upward rounding may stall when all factors are extremely close to one.
        # Use exact constant-block powers as a fallback for those parameters.
        if budget >= max(choices) and best[-1] == best[-max(choices)] and pending:
            for e in pending:
                target = Fraction(2, 1 << e)
                result[e] = 1 + min(l * max(1, required_repeats(c, target))
                                    for l, c in choices.items())
            break
    return result


def sweep_norm(bits, width, order, beta):
    """Bound the stationary Euclidean operator norm on mean-zero functions."""
    size, alphabet = 1 << bits, 1 << width
    d = bits // width
    pairs = comb(order, 2)
    # The rank-(order-1) term alone would already be >=1.
    if width * pairs >= bits * (order - 1):
        return Fraction(1)
    edge = Fraction(d * (alphabet - 1), size - order + 1)
    ideal_squared = Fraction(0)
    for rank in range(1, order):
        ideal_squared += comb(pairs, rank) * edge**rank * alphabet**comb(rank + 1, 2)
        if ideal_squared >= 1:
            return Fraction(1)
    return min(1, sqrt_upper(ideal_squared) + d * beta)


def spectral_rounds(bits, width, order, beta, beta2, error_bits):
    if bits % width:
        return {}
    sigma = sweep_norm(bits, width, order, beta)
    if sigma >= 1:
        return {}
    alphabet, d = 1 << width, bits // width
    pairs = comb(order, 2)
    # D <= floor((t/2) log2(t)). Compute that integer without floating point.
    deficits = (order**order).bit_length() - 1
    deficits //= 2
    a = Fraction(1, alphabet) + (1 - Fraction(1, alphabet)) * beta2
    A = (1 + (alphabet ** (order - 1) - 1) * beta) ** d
    best = {}
    for warmup in range(d):
        first = min(1, pairs * a**warmup)
        later = min(1, pairs * collision_sum(a, warmup + 1, d - 1, d - 1))
        moment = min(alphabet**deficits,
                     1 + (alphabet ** (order - 1) - 1) * first + (alphabet ** deficits - 1) * later)
        initial_chi_sq = A * moment - 1
        for e in error_bits:
            count = required_repeats(sigma**2, Fraction(4, 1 << (2 * e)) / initial_chi_sq)
            rounds = 1 + warmup + d + count * d
            if e not in best or rounds < best[e]["rounds"]:
                best[e] = {"rounds": rounds, "warmup": warmup, "additional_sweeps": count}
    return best


def sweep_analysis(bits, width, order, error_bits, mismatches, control):
    """Input is validated by the public compact/table verifier."""
    beta = bias_bound(bits, width, min(order, 1 << (bits - width)), control)
    choices = warmup_blocks(bits, width, order, beta, mismatches)
    mixed = mixed_warmup_rounds(choices, error_bits)
    spectral = {}
    if mismatches == 0:
        spectral = spectral_rounds(bits, width, order, beta, bias_bound(bits, width, 2, control), error_bits)
    return {f"2^-{e}": {"short_blocks": mixed.get(e), "sweep_norm": spectral.get(e)}
            for e in error_bits}
