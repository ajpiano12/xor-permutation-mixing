"""Decide pairwise mixing for a permutation of n-bit strings given by its images."""

import argparse
import json
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from math import gcd
from operator import index
from pathlib import Path


@dataclass(frozen=True)
class Decision:
    status: str
    period: int | None
    closed_set: tuple[int, ...] = ()
    cyclic_classes: tuple[tuple[int, ...], ...] = ()


def classify_support(states: int, successors: Callable[[int], Iterable[int]]) -> Decision:
    """Decide a balanced finite chain on 1,...,states, streaming its directed edges."""
    depth = [-1] * (states + 1)
    depth[1] = 0
    discovered = [1]
    period = 0
    # The list is a BFS queue; new discoveries are appended in traversal order.
    for a in discovered:
        next_depth = depth[a] + 1
        for b in successors(a):
            if depth[b] == -1:
                depth[b] = next_depth
                discovered.append(b)
            elif period != 1:
                period = gcd(period, next_depth - depth[b])
            if period == 1 and len(discovered) == states:
                return Decision("mixing", 1)

    if len(discovered) < states:
        # All outgoing edges of this proper reachable set have been checked.
        return Decision("disconnected", None, tuple(discovered))
    classes = [[] for _ in range(period)]
    for a in range(1, states + 1):
        classes[depth[a] % period].append(a)
    return Decision("periodic", period, cyclic_classes=tuple(map(tuple, classes)))


def validated_table(permutation: Iterable[int]) -> tuple[int, ...]:
    """Materialize and validate a truth table on a positive number of bits."""
    try:
        p = tuple(map(index, permutation))
    except TypeError as exc:
        raise ValueError("permutation images must be integers") from exc
    size = len(p)
    if size < 2 or size & (size - 1):
        raise ValueError("table length must be a power of two, at least 2")
    seen = bytearray(size)
    for value in p:
        if not 0 <= value < size or seen[value]:
            raise ValueError(f"expected each of the integers 0 through {size - 1} exactly once")
        seen[value] = 1
    return p


def classify(permutation: Iterable[int]) -> Decision:
    """Exact decision in O(N²) word operations and O(N) words for N table entries."""
    p = validated_table(permutation)
    size = len(p)

    # Clearing a set bit gives an induction test for linearity of P(x) XOR P(0).
    def agrees_with_basis(x):
        bit = x & -x
        return p[x] ^ p[x ^ bit] == p[bit] ^ p[0]

    if all(agrees_with_basis(x) for x in range(1, size)):
        return classify_support(size - 1, lambda a: (p[a] ^ p[0],))

    def successors(a):
        for x in range(size):
            y = x ^ a
            if x < y:
                yield p[x] ^ p[y]

    return classify_support(size - 1, successors)


def add_table_arguments(parser):
    parser.add_argument("images", nargs="*", help="P(0), P(1), ... as decimal or 0x-prefixed integers")
    parser.add_argument("--file", metavar="PATH", help="read the image list from a file, or - for stdin")


def read_table_arguments(parser, args):
    if bool(args.images) == (args.file is not None):
        parser.error("supply the images on the command line or use --file")
    try:
        if args.file is None:
            raw = " ".join(args.images)
        elif args.file == "-":
            raw = sys.stdin.read()
        else:
            raw = Path(args.file).read_text(encoding="utf-8")
        tokens = raw.replace(",", " ").split()
        return [int(token, 16 if token.lower().startswith("0x") else 10) for token in tokens]
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_table_arguments(parser)
    parser.add_argument("--witness", action="store_true", help="include a closed set or the cyclic classes on failure")
    args = parser.parse_args()
    p = read_table_arguments(parser, args)
    try:
        decision = classify(p)
    except ValueError as exc:
        parser.error(str(exc))
    output = {"bits": len(p).bit_length() - 1, "mixes": decision.status == "mixing",
              "status": decision.status, "period": decision.period}
    if args.witness and decision.closed_set:
        output["closed_set"] = decision.closed_set
    if args.witness and decision.cyclic_classes:
        output["cyclic_classes"] = decision.cyclic_classes
    print(json.dumps(output))


if __name__ == "__main__":
    main()
