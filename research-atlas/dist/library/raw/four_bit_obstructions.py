"""Four-bit nonmixing families. The counting argument is in FOUR_BIT_COUNT.md."""

from functools import cache
from itertools import combinations
from math import factorial, prod


@cache
def proper_subspaces():
    """All 65 proper nonzero subspaces, in the order used for disjoint counting."""
    hyperplanes = [
        frozenset(x for x in range(16) if (x & mask).bit_count() % 2 == 0)
        for mask in range(1, 16)
    ]
    lines = [frozenset((0, x)) for x in range(1, 16)]
    planes = {tuple(sorted((0, a, b, a ^ b))) for a, b in combinations(range(1, 16), 2)}
    return tuple(hyperplanes + lines + [frozenset(w) for w in sorted(planes)])


def find_obstruction(permutation):
    """Return (family, invariant subspace) or (affine order family, None), or None if mixing."""
    if sorted(permutation) != list(range(16)):
        raise ValueError("expected a permutation of 0 through 15")
    p = tuple(value ^ permutation[0] for value in permutation)
    for w in proper_subspaces():
        # For the coset containing 0 the condition reduces to p(W) = W.
        if any(p[a] not in w for a in w):
            continue
        if all(p[x] ^ p[x ^ a] in w for x in range(16) for a in w):
            family = {8: "hyperplane", 2: "line", 4: "plane"}[len(w)]
            return family, tuple(sorted(w))
    if all(p[x ^ bit] == p[x] ^ p[bit] for bit in (1, 2, 4, 8) for x in range(16)):
        # With no nontrivial invariant subspace, all nonzero orbits have
        # length 5 or all have length 15.
        state = p[1]
        order = 1
        while state != 1:
            state = p[state]
            order += 1
        return f"affine_order_{order}", None
    return None


def subspace_count(n, k):
    """Number of k-dimensional binary subspaces (count ordered bases twice)."""
    return prod(2**n - 2**i for i in range(k)) // prod(2**k - 2**i for i in range(k))


def hyperplane_preservers(n):
    """Count permutations preserving at least one parity partition, allowing a swap."""
    exact = {}
    for k in range(n, 0, -1):
        cells = 2**k
        per_subspace = cells * factorial(2**(n - k))**cells
        incidences = subspace_count(n, k) * per_subspace
        exact[k] = incidences - sum(subspace_count(j, k) * count for j, count in exact.items())
    return sum(exact.values())


def obstruction_counts():
    """Disjoint labeled counts, in decreasing priority as in find_obstruction."""
    # A fixed line leaves a three-bit quotient permutation fixing zero.
    quotient_choices = factorial(7) - hyperplane_preservers(3) // 8
    fiber_flips = 2**7 - 8
    lines = 16 * 15 * quotient_choices * fiber_flips

    # For a fixed plane choose an order-3 quotient map, three free offsets,
    # and four binary GL(2) maps with no common fixed direction.
    fiber_linear_choices = 6**4 - 3 * 2**4 + 2
    per_plane = 2 * 4**3 * fiber_linear_choices
    gl4 = prod(16 - 2**i for i in range(4))
    gl2_over_four = (16 - 1) * (16 - 4)
    counted_five_times = gl4 // gl2_over_four
    planes = 16 * (35 * per_plane - 4 * counted_five_times)

    # One irreducible quartic of order 5 and two of order 15. The
    # invertible maps commuting with a given irreducible matrix number 15.
    per_quartic = 16 * gl4 // 15
    return {
        "hyperplane": hyperplane_preservers(4),
        "line": lines,
        "plane": planes,
        "affine_order_5": per_quartic,
        "affine_order_15": 2 * per_quartic,
    }
