"""Exhaustively measure fixed three-bit permutations at every tuple order."""
import argparse
import csv
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path

import numpy as np

from classify_mixing import classify_support
from exact_four_bit import linear_maps

SIZE = 8
DENOMINATORS = (4, 8, 16, 32, 64, 128)


def representatives():
    """Normalize output translations, change input origin, and conjugate by GL(3,2)."""
    linear = [tuple(map(int, g)) for g in linear_maps(3)]
    changes = [(g, tuple(g.index(i) for i in range(SIZE))) for g in linear]
    seen = set()
    for tail in permutations(range(1, SIZE)):
        p = (0, *tail)
        if p in seen:
            continue
        orbit = {
            tuple(g[p[x ^ shift] ^ p[shift]] for x in inverse)
            for g, inverse in changes for shift in range(SIZE)
        }
        seen.update(orbit)
        yield p, SIZE * len(orbit)


def normalized_starts(t, ids, domain_size=SIZE):
    """One ordering per translation class of unordered input sets for worst-start TV."""
    starts = set()
    for subset in combinations(range(domain_size), t):
        shifted = min(tuple(sorted(x ^ a for x in subset)) for a in subset)
        starts.add(ids[bytes(shifted[1:])])
    return sorted(starts)


def measure(p, shapes, ids, starts, denominators=DENOMINATORS):
    domain_size = len(p)
    size = len(shapes)
    steps = []
    for x in range(domain_size):
        table = bytes(p[x] ^ p[x ^ a] for a in range(domain_size)) + bytes(256 - domain_size)
        steps.append([ids[s.translate(table)] for s in shapes])
    edges = np.asarray(steps, dtype=np.int32)
    decision = classify_support(size, lambda a: (int(b) + 1 for b in edges[:, a - 1]))
    if decision.status != "mixing":
        return decision.status, decision.period, ()
    # Each column action permutes shapes. Gather predecessors to sum key counts.
    predecessors = np.argsort(edges, axis=1)
    counts = np.zeros((len(starts), size), dtype=np.int64)
    counts[np.arange(len(starts)), starts] = 1
    key_sequences, rounds = 1, 0
    hits = []
    while len(hits) < len(denominators):
        # Row sums of abs(size * counts - key_sequences) are <= 2 * size * key_sequences.
        if counts.dtype != object and 2 * size * key_sequences > np.iinfo(np.int64).max:
            counts = counts.astype(object)
        deviation = int(np.abs(size * counts - key_sequences).sum(axis=1).max())
        while len(hits) < len(denominators) and deviation * denominators[len(hits)] <= 2 * size * key_sequences:
            hits.append(rounds + 1)  # convert difference rounds to full cipher rounds
        if len(hits) == len(denominators):
            break
        if counts.dtype != object and key_sequences * domain_size > np.iinfo(np.int64).max:
            counts = counts.astype(object)
        counts = sum((counts[:, pred] for pred in predecessors), np.zeros_like(counts))
        rounds += 1
        key_sequences *= domain_size
    return decision.status, decision.period, tuple(hits)


def affine_designs():
    """All relabelings of the fourteen affine planes that are translation-invariant."""
    points = range(SIZE)
    planes = [q for q in combinations(points, 4) if q[0] ^ q[1] ^ q[2] ^ q[3] == 0]
    def encode(p, blocks):
        return tuple(sorted(sum(1 << p[x] for x in block) for block in blocks))
    designs = {encode(p, planes) for p in permutations(points)}
    translations = [[x ^ bit for x in points] for bit in (1, 2, 4)]
    compatible = []
    for design in designs:
        blocks = [tuple(x for x in points if mask & (1 << x)) for mask in design]
        if all(encode(t, blocks) == design for t in translations):
            compatible.append((blocks, design))
    return encode, compatible


def census():
    reps = list(representatives())
    if sum(weight for _, weight in reps) != 40320:
        raise RuntimeError("Permutation classes do not total 8!")
    encode, compatible = affine_designs()
    designs = {p: sum(encode(p, b) == d for b, d in compatible) for p, _ in reps}
    rows = []
    for t in range(2, SIZE):
        shapes = [bytes(s) for s in permutations(range(1, SIZE), t - 1)]
        ids = {s: i for i, s in enumerate(shapes)}
        starts = normalized_starts(t, ids)
        for p, weight in reps:
            status, period, rounds = measure(p, shapes, ids, starts)
            row = [t, " ".join(map(str, p)), weight, designs[p], status, period, *(rounds or ("",) * len(DENOMINATORS))]
            rows.append(row)
            if t == SIZE - 1:
                rows.append([SIZE, *row[1:]])  # the last image is determined by the other seven
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("results/higher_three_bit.csv"))
    path = parser.parse_args().output
    rows = census()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["t", "representative", "permutations", "translation_invariant_plane_systems_preserved", "status", "period", *(f"rounds_at_1_{d}" for d in DENOMINATORS)])
        writer.writerows(rows)
    for t in range(2, SIZE + 1):
        total = Counter()
        hist = Counter()
        for order, _, weight, _, status, _, *hits in rows:
            if order == t:
                total[status] += weight
                if status == "mixing":
                    hist[hits[0]] += weight
        print(f"t={t}  {dict(total)}  rounds at TV 1/4 {dict(sorted(hist.items()))}")


if __name__ == "__main__":
    main()
