"""Measure exact worst-input round counts for pairs and triples at small TV thresholds.

Run from the repository root with uv run --locked --extra four-bit -m research.small_error_census.
"""
import argparse
import csv
from itertools import combinations, islice, permutations
from pathlib import Path

import numpy as np

from higher_census import measure, normalized_starts, representatives
from inverse_triples import field_inverse_table


PRECISION_BITS = (16, 32, 64, 128)


def tables(sample_file, draws):
    for p, weight in representatives():
        yield "three-bit census", p, weight
    # Use x^4 + x + 1 to represent GF(16).
    yield "four-bit inverse", tuple(field_inverse_table(16, 0x13)), 1
    with sample_file.open(newline="") as stream:
        for row in islice(csv.DictReader(stream), draws):
            p = tuple(map(int, row["permutation"].split()))
            yield f"four-bit draw {row['draw']}", p, 1


def census(sample_file, draws):
    spaces = {}
    for family, p, weight in tables(sample_file, draws):
        n = len(p).bit_length() - 1
        precisions = (n, *PRECISION_BITS)
        for order in (2, 3):
            space = len(p), order
            if space not in spaces:
                shapes = [bytes(s) for s in permutations(range(1, len(p)), order - 1)]
                ids = {s: i for i, s in enumerate(shapes)}
                starts = normalized_starts(order, ids, domain_size=len(p))
                spaces[space] = shapes, ids, starts
            status, period, hits = measure(
                p, *spaces[space], denominators=tuple(1 << k for k in precisions)
            )
            yield [n, order, family, " ".join(map(str, p)), weight, status, period,
                   *(hits or [""] * len(precisions))]


def verify_three_bit_structure():
    """Check the orientation obstruction and the fast family's annihilating polynomial."""
    pairs = list(permutations(range(1, 8), 2))
    pair_id = {pair: i for i, pair in enumerate(pairs)}
    planes = sorted({tuple(sorted((a, b, a ^ b))) for a, b in pairs})
    plane_id = {plane: i for i, plane in enumerate(planes)}
    fast = (0, 1, 2, 4, 5, 6, 7, 3)
    apn_total = 0
    for p, weight in representatives():
        diff = [[p[x] ^ p[x ^ a] for a in range(8)] for x in range(8)]
        apn = all(len({row[a] for row in diff}) == 4 for a in range(1, 8))
        if not apn and p != fast:
            continue
        signed = np.zeros((7, 7), dtype=np.int64)
        for i, (a, b, _) in enumerate(planes):
            for row in diff:
                image = (row[a], row[b], row[a] ^ row[b])
                inversions = sum(x > y for x, y in combinations(image, 2))
                j = plane_id[tuple(sorted(image))]
                signed[i, j] += (-1) ** inversions
        if apn:
            if not np.array_equal(signed @ signed.T, 16 * np.eye(7, dtype=np.int64)):
                raise AssertionError(f"orientation identity failed at {p}")
            apn_total += weight
        if p == fast:
            if np.any(signed @ signed):
                raise AssertionError("signed kernel must vanish at step two")
            matrix = np.zeros((42, 42), dtype=np.int64)
            for i, (a, b) in enumerate(pairs):
                for row in diff:
                    matrix[i, pair_id[row[a], row[b]]] += 1
            identity = np.eye(42, dtype=np.int64)
            projection = matrix @ matrix @ (matrix - 8 * identity) @ (matrix + identity)
            if not np.any(projection) or np.any(projection @ (matrix @ matrix - 8 * identity)):
                raise AssertionError("fast family's matrix identity failed")
    if apn_total != 10752:
        raise AssertionError("three-bit APN count did not match")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=Path, default=Path("results/four_bit/samples.csv"))
    parser.add_argument("--draws", type=int, default=8, help="use the first draws from the recorded sample")
    parser.add_argument("--output", type=Path, default=Path("results/small_error_times.csv"))
    args = parser.parse_args()
    if args.draws < 0:
        parser.error("draw count must be nonnegative")
    verify_three_bit_structure()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["bits", "t", "family", "representative", "permutations", "status", "period",
                         "rounds_at_2^-n", *(f"rounds_at_2^-{k}" for k in PRECISION_BITS)])
        writer.writerows(census(args.samples, args.draws))


if __name__ == "__main__":
    main()
