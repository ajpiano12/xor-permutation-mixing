"""Count mixing, disconnected and periodic permutations using difference color partitions.

An integer bit mask represents a set of nonzero XOR differences. A tuple of
such masks partitions those differences. Its cells are colors on pairs of
points: the color of {x,y} is the cell containing x ^ y. We fix P(0)=0
throughout and multiply by the domain size at the end.
"""
import argparse
from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
from math import factorial

import numpy as np

from four_bit_obstructions import obstruction_counts


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def labels(partition, size):
    colors = [0] * size
    for block in partition:
        first = next(members(block))
        for point in members(block):
            colors[point] = first
    return colors


def pack(colors):
    return sum(color << (4 * i) for i, color in enumerate(colors[1:]))


def linear_maps(bits):
    """Enumerate ordered bases and the linear maps that use them as images."""
    size = 1 << bits

    def extend(images):
        if len(images) == size:
            yield images
        else:
            for image in range(1, size):
                if image not in images:
                    yield from extend(images + [image ^ x for x in images])

    return np.array(list(extend([0])), dtype=np.uint16)


def split_cells(partition, stabilizer):
    """All one-cell splits up to a linear change preserving the partition."""
    seen = set()
    for block in partition:
        keep = tuple(other for other in partition if other != block)
        positions = list(members(block))
        if len(positions) < 2:
            continue
        images = 1 << stabilizer[:, positions]
        full_images = np.bitwise_or.reduce(images, axis=1)
        subset = (block - 1) & block
        while subset:
            if subset not in seen:
                columns = [i for i, j in enumerate(positions) if subset >> j & 1]
                half = np.bitwise_or.reduce(images[:, columns], axis=1)
                seen.update(half.tolist())
                seen.update((half ^ full_images).tolist())
                yield (*keep, subset, block ^ subset)
            subset = (subset - 1) & block


class ColorGraph:
    def __init__(self, partition, size):
        self.size = size
        self.color = labels(partition, size)
        # For a target vertex y and a source color c, neighbors[y][c]
        # contains exactly its target neighbors of color c.
        self.neighbors = [[0] * size for _ in range(size)]
        for x in range(size):
            for y in range(size):
                self.neighbors[x][self.color[x ^ y]] |= 1 << y

    def find_map(self, perm, domains, i, y):
        """Try i -> y, using the most constrained remaining vertex first."""
        perm[i] = y
        candidates = {}
        for j, allowed in domains.items():
            if j == i:
                continue
            reduced = allowed & self.neighbors[y][self.color[i ^ j]]
            if not reduced:
                return False
            candidates[j] = reduced
        if not candidates:
            return True
        j = min(candidates, key=lambda p: candidates[p].bit_count())
        return any(self.find_map(perm, candidates, j, k) for k in members(candidates[j]))

    def stabilizer(self):
        """Return the normalized color-preserving group order and its point orbits."""
        size = self.size
        components = Components(size)
        order = 1
        domains = dict.fromkeys(range(1, size), (1 << size) - 1)
        # At stage i, only maps fixing 0,...,i-1 remain. One map for each
        # possible image of i gives coset representatives for the next
        # stabilizer. Together the representatives generate the whole group.
        for i in range(size):
            if i:
                orbit = 1
                for y in members(domains[i]):
                    if y == i:
                        continue
                    perm = list(range(size))
                    if self.find_map(perm, domains, i, y):
                        orbit += 1
                        for j in domains:
                            components.join(j, perm[j])
                order *= orbit
                del domains[i]
            for j in domains:
                domains[j] &= self.neighbors[i][self.color[i ^ j]]
        return order, components.partition()


class Components:
    """Disjoint sets on differences, with zero omitted from the output."""

    def __init__(self, size):
        self.group = list(range(size))

    def root(self, i):
        while self.group[i] != i:
            i = self.group[i]
        return i

    def join(self, i, j):
        self.group[self.root(i)] = self.root(j)

    def partition(self):
        blocks = {}
        for i in range(1, len(self.group)):
            root = self.root(i)
            blocks[root] = blocks.get(root, 0) | (1 << i)
        return tuple(sorted(blocks.values()))


@dataclass
class PartitionClass:
    blocks: tuple
    group_order: int
    stabilizer: np.ndarray
    copies: int
    exact: int = 0


def closed_partitions(bits):
    """Generate and index all orbit partitions up to a linear change of basis.

    Closing a partition means replacing its colors by the point orbits of
    the group fixing 0 and preserving each color. This refines the partition
    and leaves its automorphism group unchanged. To reach a chosen closed
    refinement, split a cell along the target cells and close. Its group is
    still contained in the split graph's group, so closing cannot overshoot.
    Repeating reaches every closed partition starting from the single cell.
    """
    size = 1 << bits
    linear = linear_maps(bits)
    classes = []
    labeled = {}
    shifts = np.arange(size - 1, dtype=np.uint64) * 4

    def register(partition, order):
        raw_key = pack(labels(partition, size))
        if raw_key in labeled:
            return
        transformed = np.zeros_like(linear)
        rows = np.arange(len(linear))[:, None]
        for block in partition:
            points = linear[:, list(members(block))]
            transformed[rows, points] = points.min(axis=1, keepdims=True)
        keys = np.bitwise_or.reduce(transformed[:, 1:].astype(np.uint64) << shifts, axis=1)
        stabilizer = linear[keys == raw_key]
        copies = len(linear) // len(stabilizer)
        index = len(classes)
        labeled.update(dict.fromkeys(np.unique(keys).tolist(), index))
        classes.append(PartitionClass(partition, order, stabilizer, copies))

    full = (1 << size) - 2
    register((full,), factorial(size - 1))
    # register appends newly discovered refinements to the traversal.
    for rep in classes:
        for split in split_cells(rep.blocks, rep.stabilizer):
            if pack(labels(split, size)) not in labeled:
                order, closed = ColorGraph(split, size).stabilizer()
                register(closed, order)
    return classes, labeled, linear


def disconnected_count(classes, labeled, size):
    """Invert |H(pi)| = sum of exact component counts for refinements of pi.

    A permutation belongs to H(pi) iff each difference transition stays in
    its cell. Each chain component partition is closed. Indeed a path on
    differences lifts to compositions of point translations and P (and
    inverses for a reversed edge). These maps preserve component colors.
    A final translation places the first endpoint back at 0.
    """
    decoded = [
        ([0] + [(key >> (4 * i)) & 15 for i in range(size - 1)], classes[index])
        for key, index in labeled.items()
    ]
    total = 0
    for rep in sorted(classes, key=lambda rep: len(rep.blocks), reverse=True):
        color = labels(rep.blocks, size)
        finer = sum(
            other.exact for names, other in decoded
            if len(other.blocks) > len(rep.blocks)
            and all(color[x] == color[names[x]] for x in range(1, size))
        )
        rep.exact = rep.group_order - finer
        assert rep.exact >= 0
        if len(rep.blocks) > 1:
            total += rep.exact * rep.copies
    return total


def obstruction_counts_from_components(classes, linear, bits):
    """Count disjoint obstruction families directly from exact component partitions."""
    size = 1 << bits
    subspaces = {}
    for dimension in range(1, bits):
        # All subspaces of a given dimension are linear images of one span.
        masks = np.bitwise_or.reduce(1 << linear[:, 1:(1 << dimension)], axis=1)
        subspaces[dimension] = np.unique(masks).tolist()

    priority = [bits - 1, *range(1, bits - 1)]
    counts = {dimension: 0 for dimension in priority}
    affine = 0
    for rep in classes:
        if len(rep.blocks) == 1 or rep.exact == 0:
            continue
        copies = rep.copies * rep.exact * size
        for dimension in priority:
            # The cosets form an invariant partition exactly when the nonzero
            # elements of the subspace are a union of whole component cells.
            if any(all((cell & mask) in (0, cell) for cell in rep.blocks)
                   for mask in subspaces[dimension]):
                counts[dimension] += copies
                break
        else:
            colors = np.array(labels(rep.blocks, size))
            fixes_colors = (colors[rep.stabilizer] == colors).all(axis=1)
            assert np.count_nonzero(fixes_colors) == rep.group_order
            # Every such P fixing zero is linear. With no invariant proper
            # subspace its minimal polynomial is irreducible, and each cell
            # has size equal to the order of its linear part.
            assert bits == 4 and sorted(b.bit_count() for b in rep.blocks) == [5, 5, 5]
            affine += copies
    return counts, affine


def connected(perm):
    size = len(perm)
    components = Components(size)
    for x in range(1, size):
        for y in range(x):
            components.join(x ^ y, perm[x] ^ perm[y])
    return len(components.partition()) == 1


def cyclic_color_maps(blocks, size):
    color = labels(blocks, size)
    perm = [0] * size

    def visit(x, available):
        if x == size:
            return int(connected(perm))
        count = 0
        for y in members(available):
            if all(color[perm[j] ^ y] == target[color[j ^ x]] for j in range(x)):
                perm[x] = y
                count += visit(x + 1, available ^ (1 << y))
        return count

    count = 0
    for rest in permutations(blocks[1:]):
        cycle = [blocks[0], *rest]
        target = dict(zip((next(members(b)) for b in cycle),
                          (next(members(b)) for b in cycle[1:] + cycle[:1])))
        count += visit(1, (1 << size) - 2)
    return count


def periodic_counts(classes, linear, size):
    """Count irreducible walks by period using their unique cyclic partitions.

    A period divisible by d gives one partition of the differences into d
    equal cells that advance by one on each edge. This partition is closed.
    A path connecting two differences in the same cell has length 0 mod d,
    so its lift by translations and P induces a color-preserving map.
    Conversely an irreducible chain with such a color cycle has period
    divisible by d. The final subtraction recovers exact periods.
    """
    divisors = {}
    for rep in classes:
        blocks = rep.blocks
        d = len(blocks)
        if d <= 1 or any(d * b.bit_count() != size - 1 for b in blocks):
            continue
        if d == size - 1:
            count = 0
            for perm in linear.tolist():
                # All singleton colors are preserved up to relabeling exactly by GL.
                x = perm[1]
                length = 1
                while x != 1:
                    x = perm[x]
                    length += 1
                count += (length == d)
        else:
            count = cyclic_color_maps(blocks, size)
        divisors[d] = divisors.get(d, 0) + count * rep.copies
    for d in sorted(divisors, reverse=True):
        for k in divisors:
            if k < d and d % k == 0:
                divisors[k] -= divisors[d]
    return divisors


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bits", type=int, choices=(3, 4), default=4)
    bits = parser.parse_args().bits
    size = 1 << bits
    classes, labeled, linear = closed_partitions(bits)
    disc = disconnected_count(classes, labeled, size) * size
    periodic = {k: v * size for k, v in periodic_counts(classes, linear, size).items()}
    by_dimension, affine = obstruction_counts_from_components(classes, linear, bits)
    assert disc == sum(by_dimension.values()) + affine
    if bits == 4:
        families = {
            "hyperplane": by_dimension[3], "line": by_dimension[1], "plane": by_dimension[2],
            "affine_order_5": affine, "affine_order_15": periodic[15],
        }
        if families != obstruction_counts() or sum(families.values()) != disc + sum(periodic.values()):
            raise ArithmeticError("Orbit partitions and structural family counts disagree")
    else:
        # An independent direct enumeration of the 8! three-bit permutations
        # supplies these regression values.
        assert disc == 7680 and periodic == {7: 384}

    total = factorial(size)
    mixing = total - disc - sum(periodic.values())
    print(f"{len(classes)} partition classes, {len(labeled)} labeled closed partitions")
    print(f"total {total:,}")
    print(f"disconnected {disc:,}")
    for period, count in sorted(periodic.items()):
        print(f"connected with period {period}: {count:,}")
    nonmixing = total - mixing
    print(f"nonmixing {nonmixing:,}/{total:,} = {Fraction(nonmixing, total)}")
    print(f"mixing {mixing:,}/{total:,} = {Fraction(mixing, total)} ({100 * mixing / total:.10f}%)")
    if bits == 4:
        print("Structural counts agree with the orbit-partition count for every family.")


if __name__ == "__main__":
    main()
