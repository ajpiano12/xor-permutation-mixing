# /// script
# requires-python = ">=3.10"
# dependencies = ["sympy==1.14.0"]
# ///
"""Determine the largest tuple order that mixes from a permutation truth table."""

import argparse
import json
from math import factorial, isqrt

from sympy.combinatorics import Permutation, PermutationGroup

from classify_mixing import add_table_arguments, read_table_arguments, validated_table


def giant_witness(p):
    """Find a long prime cycle in one of the first sixteen actual round permutations."""
    size = len(p)
    for key in range(min(size, 16)):
        seen = bytearray(size)
        for x in range(size):
            if seen[x]:
                continue
            length = 0
            y = x
            while not seen[y]:
                seen[y] = 1
                y = p[y ^ key]
                length += 1
            if size // 2 < length < size - 2:
                if all(length % d for d in range(2, isqrt(length) + 1)):
                    return {"key": key, "cycle_start": x, "prime_length": length}
    return None


def group_profile(permutation):
    """Return maximum mixing order, with a group-order formula for large alternating groups."""
    p = validated_table(permutation)
    size = len(p)
    bits = size.bit_length() - 1
    witness = giant_witness(p) if size >= 8 else None
    if witness:
        # The transitive ambient group contains A_N by Jordan. Its normal
        # closure of translations is exactly A_N by parity and simplicity.
        order = factorial(size) // 2 if size < 1024 else f"{size}!/2"
        return {"bits": bits, "degree": size, "mixes_through": size - 2,
                "closure_order": order, "closure_is_alternating": True, "cycle_witness": witness}
    step = Permutation(list(p))
    layer = [Permutation([x ^ (1 << i) for x in range(size)]) for i in range(bits)]
    closure = PermutationGroup(layer)
    # Every layer consists of the basis translations conjugated by one more
    # power of P. Once it adds nothing, conjugation preserves the whole group.
    while True:
        layer = [g ^ step for g in layer]
        additions = [g for g in layer if not closure.contains(g)]
        if not additions:
            break
        closure = PermutationGroup(closure.generators + additions)

    order = int(closure.order())
    # The first k base points have one orbit on ordered k-tuples exactly
    # while their successive orbit sizes attain N, N-1, ... .
    max_t = 0
    for orbit in closure.basic_orbits:
        if len(orbit) != size - max_t:
            break
        max_t += 1
    if max_t == size - 1:
        # One remaining unused point is uniquely determined.
        max_t = size
    alternating = bits >= 2 and max_t == size - 2
    if alternating and size >= 1024:
        order = f"{size}!/2"
    elif order.bit_length() > 12000:
        # Keep an exact, compact expression even on Python builds with decimal digit limits.
        order = " * ".join(str(len(orbit)) for orbit in closure.basic_orbits)
    return {"bits": bits, "degree": size, "mixes_through": max_t,
            "closure_order": order, "closure_is_alternating": alternating}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_table_arguments(parser)
    args = parser.parse_args()
    try:
        result = group_profile(read_table_arguments(parser, args))
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
