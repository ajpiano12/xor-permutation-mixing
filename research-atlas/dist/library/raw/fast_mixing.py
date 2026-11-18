"""One-sided, near-linear randomized screen for pairwise mixing of a permutation table."""

import argparse
import json
from math import gcd
from secrets import SystemRandom

from classify_mixing import add_table_arguments, classify, classify_support, read_table_arguments, validated_table
from parity_screen import screen_parity


class DifferenceForest:
    """Join actual edges a -> b, keeping height[b] - height[a] = 1 on tree edges."""

    def __init__(self, size):
        self.parent = list(range(size))
        self.size = [1] * size
        self.offset = [0] * size  # height relative to parent
        self.components = size - 1  # difference zero is excluded
        self.period_multiple = size - 1  # cyclic classes have equal size

    def locate(self, a):
        parent = self.parent[a]
        if parent != a:
            root, above = self.locate(parent)  # union by size bounds depth by log2(N)
            self.offset[a] += above
            self.parent[a] = root
        return self.parent[a], self.offset[a]

    def edge(self, a, b):
        left, ha = self.locate(a)
        right, hb = self.locate(b)
        discrepancy = ha + 1 - hb
        if left == right:
            if self.period_multiple != 1:
                self.period_multiple = gcd(self.period_multiple, discrepancy)
            return
        if self.size[left] < self.size[right]:
            left, right = right, left
            discrepancy = -discrepancy
        self.parent[right] = left
        self.offset[right] = discrepancy
        self.size[left] += self.size[right]
        self.components -= 1

    def anchor(self, p, x):
        for y, py in enumerate(p):
            if y != x:
                self.edge(x ^ y, p[x] ^ py)


def walsh(values):
    """Unnormalized Walsh-Hadamard transform in integer arithmetic."""
    result = list(values)
    stride = 1
    while stride < len(result):
        for start in range(0, len(result), 2 * stride):
            for i in range(start, start + stride):
                left, right = result[i], result[i + stride]
                result[i], result[i + stride] = left + right, left - right
        stride *= 2
    return result


def convolution_spectrum(left, right):
    """XOR convolution given two Walsh spectra."""
    scaled = walsh(a * b for a, b in zip(left, right))
    return [v // len(scaled) for v in scaled]


def permute_values(values, p):
    out = [0] * len(p)
    for x, px in enumerate(p):
        out[px] = values[x]
    return out


def violating_anchor(p, source, target, confidence_bits, rng):
    """Find x with source[x XOR y] != target[P(x) XOR P(y)] for some y."""
    weights = [rng.getrandbits(confidence_bits) for _ in p]
    left = convolution_spectrum(walsh(source), walsh(weights))
    right = convolution_spectrum(walsh(target), walsh(permute_values(weights, p)))
    return next((x for x, px in enumerate(p) if left[x] != right[px]), None)


def rectangle_edges(p, roots, xs, ys, forest):
    """Recover genuine edges from a sampled rectangle of ordered input pairs."""
    size = len(p)
    if len(xs) * len(ys) <= size:
        for x in xs:
            for y in ys:
                if x != y:
                    forest.edge(x ^ y, p[x] ^ p[y])
        return

    def spectra(points, use_indices):
        values = [0] * size
        for point in points:
            values[point] = point if use_indices else 1
        return walsh(values), walsh(permute_values(values, p))

    def cut_sums(left, right):
        # An internal edge contributes with both signs to the same component.
        outgoing = convolution_spectrum(left[0], right[0])
        incoming = convolution_spectrum(left[1], right[1])
        totals = [0] * size
        for a in range(1, size):
            totals[roots[a]] += outgoing[a] - incoming[a]
        return totals

    left, right = spectra(xs, False), spectra(ys, False)
    counts = cut_sums(left, right)
    candidates = [r for r, count in enumerate(counts) if abs(count) == 1]
    if not candidates:
        return
    x_sums = cut_sums(spectra(xs, True), right)
    y_sums = cut_sums(left, spectra(ys, True))
    for r in candidates:
        x, y = x_sums[r] * counts[r], y_sums[r] * counts[r]
        if 0 <= x < size and 0 <= y < size and x != y:
            a, b = x ^ y, p[x] ^ p[y]
            if roots[a] != roots[b] and r in (roots[a], roots[b]):
                forest.edge(a, b)


def rectangle_pass(p, roots, forest, goal, rng):
    # Keep X fixed across all Y scales, so the useful Y scale can depend on X.
    levels = range(len(p).bit_length())
    for i in levels:
        xs = [x for x in range(len(p)) if rng.getrandbits(i) == 0]
        for j in levels:
            ys = [y for y in range(len(p)) if rng.getrandbits(j) == 0]
            rectangle_edges(p, roots, xs, ys, forest)
            if forest.components <= goal:
                return


def grow_forest(p, forest, n, confidence_bits, error_bits, rng):
    """Try to halve the number of components in each of at most n phases."""
    size = len(p)
    repeats = 16 * (error_bits + n + (n + 1).bit_length() + 2)
    for _ in range(n):
        if forest.components == 1:
            return True
        roots = [forest.locate(a)[0] for a in range(size)]
        x = violating_anchor(p, roots, roots, confidence_bits, rng)
        if x is None:
            return False
        forest.anchor(p, x)
        if forest.components == 1:
            return True
        roots = [forest.locate(a)[0] for a in range(size)]
        goal = forest.components // 2

        # Freeze the component labels while recovering crossing edges.
        for attempt in range(repeats):
            rectangle_pass(p, roots, forest, goal, rng)
            if forest.components <= goal:
                break
            if attempt == 0:
                # The first pass may have finished every true component.
                labels = [forest.locate(a)[0] for a in range(size)]
                anchor = violating_anchor(p, labels, labels, confidence_bits, rng)
                if anchor is None:
                    return False
                forest.anchor(p, anchor)
                if forest.components <= goal:
                    break
        else:
            return False
    return forest.components == 1


def screen(permutation, error_bits=32, *, rng=None):
    """Return 'mixing' or 'unresolved'. A mixing table is missed with probability <= 2^-error_bits."""
    p = validated_table(permutation)
    if not isinstance(error_bits, int) or error_bits < 1:
        raise ValueError("error_bits must be a positive integer")
    if rng is None:
        rng = SystemRandom()
    n = len(p).bit_length() - 1
    anchors = rng.sample(range(len(p)), min(3, len(p)))
    # The sampled columns are permutations, so they too define a balanced chain.
    def sampled_successors(a):
        for x in anchors:
            yield p[x] ^ p[x ^ a]

    if classify_support(len(p) - 1, sampled_successors).status == "mixing":
        return "mixing"
    forest = DifferenceForest(len(p))
    for x in anchors:
        forest.anchor(p, x)

    confidence_bits = error_bits + (3 * n + 4).bit_length() + 1
    if not grow_forest(p, forest, n, confidence_bits, error_bits, rng):
        return "unresolved"
    while forest.period_multiple > 1:
        modulus = forest.period_multiple
        target = [forest.locate(a)[1] % modulus for a in range(len(p))]
        source = [(label + 1) % modulus for label in target]
        source[0] = target[0] = 0
        x = violating_anchor(p, source, target, confidence_bits, rng)
        if x is None:
            return "unresolved"
        forest.anchor(p, x)
    return "mixing"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_table_arguments(parser)
    parser.add_argument("--error-bits", type=int, default=32,
                        help="probability of missing a mixing table is at most 2^-BITS (default 32)")
    parser.add_argument("--exact", action="store_true",
                        help="resolve any inconclusive result with the deterministic classifier")
    args = parser.parse_args()
    p = read_table_arguments(parser, args)
    try:
        status = screen(p, args.error_bits)
        if status == "unresolved" and args.exact:
            parity = screen_parity(len(p).bit_length() - 1, p.__getitem__)
            status = "disconnected" if parity.status == "nonmixing" else classify(p).status
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps({"bits": len(p).bit_length() - 1, "status": status,
                      "mixing_miss_bound": "0" if args.exact else f"2^-{args.error_bits}"}))


if __name__ == "__main__":
    main()
