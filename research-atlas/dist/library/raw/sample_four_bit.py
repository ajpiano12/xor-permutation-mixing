"""Sample uniform four-bit permutations and measure pairwise convergence."""

import argparse
import csv
import json
import random
from collections import Counter
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from statistics import NormalDist
from tempfile import TemporaryDirectory

import numpy as np

from mixing import DEFAULT_THRESHOLDS, MixingResult, analyze, transition_counts


@dataclass(frozen=True)
class SampleResult(MixingResult):
    rate: float | None = None
    best_bit_agreement: int = 0


def best_bit_agreement(permutation):
    """Max number of inputs where a nonzero linear bit is preserved, up to complement."""
    changes = [x ^ y for x, y in enumerate(permutation)]
    best = 0
    for mask in range(1, 16):
        flips = sum((mask & change).bit_count() % 2 for change in changes)
        best = max(best, flips, 16 - flips)
    return best


def analyze_permutation(permutation, profile_rounds):
    if len(permutation) != 16 or profile_rounds < 0:
        raise ValueError("expected a four-bit permutation and a nonnegative profile length")
    counts = transition_counts(permutation)
    result = analyze(counts, DEFAULT_THRESHOLDS, profile_rounds)
    rate = None
    if result.status == "mixing":
        # T-U acts as T on deviations from uniform and kills the constant mode.
        centered = np.asarray(counts) / 16 - 1 / 15
        rate = float(np.max(np.abs(np.linalg.eigvals(centered))))
    return SampleResult(result.status, result.period, result.difference_rounds, result.distances,
                        rate, best_bit_agreement(permutation))


def wilson_interval(successes, total):
    z = NormalDist().inv_cdf(0.975)
    p = successes / total
    z2 = z * z
    center = (p + z2 / (2 * total)) / (1 + z2 / total)
    width = z * sqrt(p * (1 - p) / total + z2 / (4 * total**2)) / (1 + z2 / total)
    return [max(0.0, center - width), min(1.0, center + width)]


def summarize(seed, total, profile_rounds, counts_by_agreement, mixing):
    rates = [row.rate for row in mixing]
    quantiles = [0, 0.05, 0.25, 0.5, 0.75, 0.95, 1]
    statuses = ("mixing", "disconnected", "periodic")
    bit_summary = {}
    for score, counts in sorted(counts_by_agreement.items()):
        group = [row.rate for row in mixing if row.best_bit_agreement == score]
        bit_summary[score] = {
            "status_counts": dict(counts),
            "median_mixing_rate": float(np.median(group)) if group else None,
        }
    return {
        "seed": seed,
        "draws": total,
        "profile_rounds": profile_rounds,
        "status_counts": {s: sum(counts[s] for counts in counts_by_agreement.values()) for s in statuses},
        "by_best_linear_bit_agreement": bit_summary,
        "mixing_fraction": len(mixing) / total,
        "mixing_fraction_wilson_95": wilson_interval(len(mixing), total),
        "distinct_exact_profiles_through_round": {
            r: len({row.distances[:r + 1] for row in mixing}) for r in range(profile_rounds + 1)
        },
        "asymptotic_rate_quantiles": (
            dict(zip(quantiles, map(float, np.quantile(rates, quantiles)))) if mixing else {}
        ),
        "cipher_round_counts": {
            str(e): dict(sorted(Counter(row.difference_rounds[i] + 1 for row in mixing).items()))
            for i, e in enumerate(DEFAULT_THRESHOLDS)
        },
    }


def plot_sample(mixing, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.1), constrained_layout=True)
    if mixing:
        profiles = np.array([row.distances for row in mixing], dtype=float)
        rounds = np.arange(profiles.shape[1])
        low, lower, median, upper, high = np.quantile(profiles, [0.05, 0.25, 0.5, 0.75, 0.95], axis=0)
        axes[0].fill_between(rounds, low, high, color="#c6e5e1", label="5th–95th percentiles")
        axes[0].fill_between(rounds, lower, upper, color="#78bcb3", label="25th–75th percentiles")
        axes[0].plot(rounds, median, "o-", color="#125c52", ms=4, label="Median")
        axes[0].set_yscale("log")
        axes[0].legend(frameon=False, fontsize=9)
        rates = np.array([row.rate for row in mixing])
        bins = np.arange(int(rates.min() * 100), int(rates.max() * 100) + 2) / 100
        near_bit = np.array([row.best_bit_agreement >= 14 for row in mixing])
        axes[1].hist([rates[~near_bit], rates[near_bit]], bins=bins, stacked=True,
                     color=["#3566a1", "#cb7731"], edgecolor="white", linewidth=0.45,
                     label=["At most 12 of 16", "14 of 16"])
        axes[1].legend(title="Best linear bit agreement", frameon=False, fontsize=9)
    else:
        for ax in axes:
            ax.text(0.5, 0.5, "No mixing draws", ha="center", va="center", transform=ax.transAxes)
    axes[0].set(xlabel="Difference rounds", ylabel="Worst-case total variation distance",
                title="Distance to uniform")
    axes[1].set(xlabel="Asymptotic factor per round (smaller is faster)", ylabel="Permutations",
                title="Distribution of convergence rates")
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(f"Four-bit pairwise mixing  ·  {len(mixing):,} mixing draws")
    fig.savefig(path, dpi=170)
    plt.close(fig)


def run_sample(total, seed, profile_rounds, output_dir):
    if total <= 0 or profile_rounds < 0:
        raise ValueError("draw count must be positive and profile length nonnegative")
    rng = random.Random(seed)
    counts_by_agreement = {}
    mixing = []
    output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output_dir) as tmp:
        folder = Path(tmp)
        with (folder / "samples.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow([
                "draw", "permutation", "status", "period", "rate", "best_bit_agreement",
                *(f"diff_rounds_{e.numerator}_{e.denominator}" for e in DEFAULT_THRESHOLDS),
                *(f"tv_{r}" for r in range(profile_rounds + 1)),
            ])
            for draw in range(1, total + 1):
                permutation = list(range(16))
                rng.shuffle(permutation)
                result = analyze_permutation(permutation, profile_rounds)
                counts_by_agreement.setdefault(result.best_bit_agreement, Counter())[result.status] += 1
                if result.status == "mixing":
                    mixing.append(result)
                writer.writerow([
                    draw, " ".join(map(str, permutation)), result.status, result.period, result.rate,
                    result.best_bit_agreement,
                    *result.difference_rounds, *(result.distances or [None] * (profile_rounds + 1)),
                ])
        summary = summarize(seed, total, profile_rounds, counts_by_agreement, mixing)
        (folder / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        plot_sample(mixing, folder / "convergence.png")
        for name in ("samples.csv", "summary.json", "convergence.png"):
            (folder / name).replace(output_dir / name)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20261118)
    parser.add_argument("--profile-rounds", type=int, default=8)
    parser.add_argument("--output-dir", type=Path, default=Path("results/four_bit"))
    args = parser.parse_args()
    if args.samples < 1 or args.profile_rounds < 0:
        parser.error("--samples must be positive and --profile-rounds must be nonnegative")
    summary = run_sample(args.samples, args.seed, args.profile_rounds, args.output_dir)
    print(f"{summary['status_counts']} across {args.samples:,} draws with seed {args.seed}")
    print(f"Results written to {args.output_dir}")


if __name__ == "__main__":
    main()
