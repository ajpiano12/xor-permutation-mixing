"""Exact pairwise mixing times for every fixed three-bit permutation."""

import argparse
import csv
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
from operator import mul
from pathlib import Path
from tempfile import TemporaryDirectory

from classify_mixing import classify_support


SIZE = 8
DEFAULT_THRESHOLDS = tuple(Fraction(1, 2**k) for k in range(2, 8))
Matrix = tuple[tuple[int, ...], ...]


def transition_counts(permutation: tuple[int, ...]) -> Matrix:
    """Entry [a-1][b-1] counts keys giving output difference b from a."""
    size = len(permutation)
    if size < 4 or size & (size - 1) or sorted(permutation) != list(range(size)):
        raise ValueError("expected a permutation of a power-of-two domain of size at least four")
    rows = []
    for a in range(1, size):
        counts = [0] * (size - 1)
        for u in range(size):
            b = permutation[u] ^ permutation[u ^ a]
            counts[b - 1] += 1
        rows.append(tuple(counts))
    return tuple(rows)


def chain_period(matrix: Matrix) -> int | None:
    """Return the period, or None if the difference graph is disconnected."""
    def successors(a):
        return (b for b, count in enumerate(matrix[a - 1], start=1) if count)

    return classify_support(len(matrix), successors).period


@dataclass(frozen=True)
class MixingResult:
    status: str
    period: int | None
    difference_rounds: tuple[int | None, ...]
    distances: tuple[Fraction, ...] = ()

    @property
    def pair_rounds(self) -> tuple[int | None, ...]:
        return tuple(None if r is None else r + 1 for r in self.difference_rounds)


def difference_distances(matrix: Matrix):
    """Yield exact worst-start TV at rounds 0, 1, ... using integer counts."""
    states = len(matrix)
    keys = states + 1
    yield Fraction(states - 1, states)
    power = matrix
    columns = tuple(zip(*matrix))
    key_sequences = keys
    while True:
        deviation = max(
            sum(abs(states * count - key_sequences) for count in row)
            for row in power
        )
        yield Fraction(deviation, 2 * states * key_sequences)
        power = tuple(
            tuple(sum(map(mul, row, column)) for column in columns)
            for row in power
        )
        key_sequences *= keys


def analyze(matrix: Matrix, thresholds: tuple[Fraction, ...], profile_rounds: int = -1) -> MixingResult:
    """Find threshold crossing times and optionally retain TV through profile_rounds."""
    if not thresholds or any(e <= 0 or 2 * e > 1 for e in thresholds):
        raise ValueError("supply total variation thresholds in (0, 1/2]")
    period = chain_period(matrix)
    if period != 1:
        status = "disconnected" if period is None else "periodic"
        return MixingResult(status, period, (None,) * len(thresholds))

    remaining = sorted(set(thresholds))  # easiest threshold at the end
    first_round = {}
    distances = []
    for rounds, worst_tv in enumerate(difference_distances(matrix)):
        if rounds <= profile_rounds:
            distances.append(worst_tv)
        while remaining and worst_tv <= remaining[-1]:
            first_round[remaining.pop()] = rounds
        if not remaining and rounds >= profile_rounds:
            break
    return MixingResult("mixing", period, tuple(first_round[e] for e in thresholds), tuple(distances))


def census(thresholds: tuple[Fraction, ...], output_dir: Path) -> Counter:
    """Write per-permutation measurements and counts grouped for plotting."""
    output_dir.mkdir(parents=True, exist_ok=True)
    common_fields = ["epsilon", "epsilon_exact", "status", "period", "difference_rounds", "pair_rounds"]
    histogram = Counter()
    # Finish both CSVs before replacing any previous run.
    with TemporaryDirectory(dir=output_dir) as tmp:
        details = Path(tmp) / "permutations.csv"
        summary = Path(tmp) / "summary.csv"
        with details.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["permutation", *common_fields])
            for tail in permutations(range(1, SIZE)):
                representative = (0, *tail)
                result = analyze(transition_counts(representative), thresholds)
                measurements = []
                for e, dr, pr in zip(thresholds, result.difference_rounds, result.pair_rounds):
                    measurements.append((float(e), str(e), result.status, result.period, dr, pr))
                    histogram[e, result.status, result.period, dr, pr] += SIZE
                # An output XOR cancels in every difference. Each permutation
                # has exactly one such representative, obtained by XORing P(0).
                for offset in range(SIZE):
                    label = " ".join(str(value ^ offset) for value in representative)
                    writer.writerows((label, *row) for row in measurements)

        with summary.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow([*common_fields, "permutations"])
            for (e, status, period, dr, pr), count in sorted(histogram.items(), reverse=True):
                writer.writerow([float(e), str(e), status, period, dr, pr, count])

        for path in (details, summary):
            path.replace(output_dir / path.name)
    return histogram


def parse_epsilon(value: str) -> Fraction:
    try:
        e = Fraction(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise argparse.ArgumentTypeError("use a fraction or decimal") from exc
    if not 0 < e <= Fraction(1, 2):
        raise argparse.ArgumentTypeError("epsilon must be in (0, 1/2]")
    return e


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--epsilons", type=parse_epsilon, nargs="+", default=DEFAULT_THRESHOLDS,
        help="TV thresholds as fractions or decimals (default: 1/4 down to 1/128 by halves)",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path("results"),
        help="directory for permutations.csv and summary.csv (default: results)",
    )
    args = parser.parse_args()
    thresholds = tuple(dict.fromkeys(args.epsilons))
    histogram = census(thresholds, args.output_dir)
    counts = Counter()
    for (e, status, *_), count in histogram.items():
        if e == thresholds[0]:
            counts[status] += count
    print(f"{counts.total():,} permutations, {len(thresholds)} thresholds")
    for status, count in sorted(counts.items()):
        print(f"  {status:14} {count:6,}")
    print(f"Results written to {args.output_dir}")


if __name__ == "__main__":
    main()
