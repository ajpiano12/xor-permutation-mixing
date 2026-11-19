"""Measure exact fixed-start triple distances for a seeded sample of fixed tables."""
import argparse
import csv
from fractions import Fraction
from pathlib import Path
from random import Random

import numpy as np


def triple_distances(p, steps=3):
    size = len(p)
    if steps < 0 or size ** steps * size ** 2 * 2 > np.iinfo(np.int64).max:
        raise ValueError("The exact integer TV numerator must fit in 64 bits")
    x = np.arange(size)
    table = np.array(p)
    inverse = np.argsort(table)
    predecessors = [inverse[table[k] ^ x] ^ k for k in range(size)]
    states = (size - 1) * (size - 2)
    valid = (x[:, None] != x) & (x[:, None] != 0) & (x != 0)
    counts = np.zeros((size, size), dtype=np.int64)
    counts[1, 2] = 1
    distances = []
    for step in range(1, steps + 1):
        new = np.zeros_like(counts)
        for index in predecessors:
            new += counts[np.ix_(index, index)]
        counts = new
        keys = size ** step
        assert counts.sum() == keys
        numerator = int(np.abs(states * counts[valid] - keys).sum())
        distances.append(Fraction(numerator, 2 * states * keys))
    return distances


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", nargs="+", type=int, default=[4, 5, 6, 7])
    parser.add_argument("--draws", type=int, default=32)
    parser.add_argument("--seed", type=int, default=20261118)
    parser.add_argument("--output", type=Path, default=Path("results/triple_probe.csv"))
    args = parser.parse_args()
    if any(n < 2 or n > 12 for n in args.bits) or args.draws < 1:
        parser.error("choose 2 to 12 bits and a positive sample size")
    with args.output.open("w", newline="") as f:
        out = csv.writer(f, lineterminator="\n")
        out.writerow(["bits", "draw", "seed", "input_tuple", "cipher_rounds", "tv_exact"])
        for n in args.bits:
            rng = Random((args.seed << 8) | n)
            for draw in range(1, args.draws + 1):
                p = list(range(1 << n))
                rng.shuffle(p)
                for r, tv in enumerate(triple_distances(p), 2):
                    out.writerow([n, draw, args.seed, "0 1 2", r, str(tv)])


if __name__ == "__main__":
    main()
