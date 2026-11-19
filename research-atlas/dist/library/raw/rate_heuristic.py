"""Estimate, certify, or measure worst-start pairwise mixing times for a supplied table."""
import argparse
from collections import defaultdict
from fractions import Fraction
import json
from math import ceil, log2
from pathlib import Path
from random import Random
from statistics import median

import numpy as np

from classify_mixing import add_table_arguments, read_table_arguments, validated_table
from fast_mixing import walsh
from mixing import chain_period, transition_counts

ERROR_BITS = (32, 64, 128)
PROBE_STEPS = 12
SUMMARY = Path(__file__).resolve().parents[1] / "results" / "rate_heuristic.json"


def parity_score(p):
    histogram = [0] * len(p)
    for x, image in enumerate(p):
        histogram[x ^ image] += 1
    return max(abs(value) for value in walsh(histogram)[1:])


def parity_lower_rounds(size, score, exponent):
    """Necessary round count from a single diagonal entry in the Walsh representation."""
    states = size - 1
    probability = Fraction(score, size) ** 2
    threshold = Fraction(1, states) + Fraction(2 * states, size << exponent)
    if probability == 1:
        return None
    if threshold >= 1:
        return 1
    low, high = 0, 1
    while probability ** high > threshold:
        low, high = high, 2 * high
    while high - low > 1:
        mid = (high + low) // 2
        if probability ** mid > threshold:
            low = mid
        else:
            high = mid
    return high + 1


def arnoldi_factor(counts):
    """Largest Ritz modulus on mean-zero vectors, using at most 12 matrix-vector products."""
    states = len(counts)
    kernel = np.asarray(counts, dtype=float) / (states + 1)
    dimension = min(PROBE_STEPS, states - 1)
    basis = np.zeros((states, dimension + 1))
    projected = np.zeros((dimension + 1, dimension))
    rng = np.random.default_rng(109)
    initial = rng.standard_normal(states)
    initial -= initial.mean()
    basis[:, 0] = initial / np.linalg.norm(initial)
    for j in range(dimension):
        columns = basis[:, :j + 1]
        work = kernel @ columns[:, j]
        work -= work.mean()
        # A second pass keeps nearly dependent directions orthogonal on small tables.
        for _ in range(2):
            coefficients = columns.T @ work
            projected[:j + 1, j] += coefficients
            work -= columns @ coefficients
        residual = np.linalg.norm(work)
        if residual < 1e-13:
            dimension = j + 1
            break
        projected[j + 1, j] = residual
        basis[:, j + 1] = work / residual
    return float(np.abs(np.linalg.eigvals(projected[:dimension, :dimension])).max())


def norm_numerator(centered):
    return int(np.abs(centered).sum(axis=1).max())


def exact_rounds(counts, error_bits):
    """Exact integer threshold crossings on an already classified mixing table."""
    states = len(counts)
    keys = (states + 1) // 2
    paths = np.asarray(counts, dtype=object) // 2
    stride = 8
    powers = [np.eye(states, dtype=int).astype(object)]
    for _ in range(stride):
        powers.append(powers[-1] @ paths)
    centered = states * powers[0] - 1
    steps, denominator, result = 0, 2 * states, {}
    deviation = norm_numerator(centered)
    for target in sorted(set(error_bits)):
        while (deviation << target) > denominator:
            previous = centered
            centered = centered @ powers[stride]
            steps += stride
            denominator *= keys ** stride
            deviation = norm_numerator(centered)
        if not steps:
            result[target] = 1
            continue
        # The previous block may contain several crossings. Start at its first step.
        low, high = 0, stride
        start_denominator = denominator // keys ** stride
        while high - low > 1:
            offset = (low + high) // 2
            at_offset = norm_numerator(previous @ powers[offset])
            if (at_offset << target) <= start_denominator * keys ** offset:
                high = offset
            else:
                low = offset
        result[target] = 1 + steps - stride + high
    return result


def block_certificate(counts, error_bits):
    """Return whole-block and remainder bounds from the exact 12-step row separation."""
    states = len(counts)
    keys = (states + 1) // 2
    counts_half = np.asarray(counts, dtype=object) // 2
    block = np.eye(states, dtype=int).astype(object)
    distances = [Fraction(states - 1, states)]
    for step in range(1, PROBE_STEPS + 1):
        block = block @ counts_half
        mass = keys ** step
        distances.append(Fraction(norm_numerator(states * block - mass), 2 * states * mass))
    denominator = keys ** PROBE_STEPS
    distance = distances[-1]
    separation = max(norm_numerator(block[i + 1:] - row) for i, row in enumerate(block[:-1]))
    coefficient = Fraction(separation, 2 * denominator)
    whole, partial = {}, {}
    for exponent in error_bits:
        target = Fraction(1, 1 << exponent)
        if distance <= target:
            blocks = 0
        elif coefficient == 1:
            partial[exponent] = whole[exponent] = None
            continue
        else:
            low, high = 0, 1
            while distance * coefficient ** high > target:
                low, high = high, 2 * high
            while high - low > 1:
                mid = (low + high) // 2
                if distance * coefficient ** mid <= target:
                    high = mid
                else:
                    low = mid
            blocks = high
        contraction = coefficient ** blocks
        tail = next(i for i, value in enumerate(distances) if contraction * value <= target)
        whole[exponent] = 1 + (blocks + 1) * PROBE_STEPS
        partial[exponent] = 1 + blocks * PROBE_STEPS + tail
    return whole, partial


def observe(p, exponents):
    counts = transition_counts(p)
    if chain_period(counts) != 1:
        return None
    whole, partial = block_certificate(counts, exponents)
    return {"factor": arnoldi_factor(counts), "parity": parity_score(p),
            "rounds": exact_rounds(counts, exponents), "upper": whole, "partial_upper": partial}


def sample(size, draws, seed):
    rng = Random(seed)
    observations = []
    for _ in range(draws):
        table = list(range(size))
        rng.shuffle(table)
        row = observe(table, ERROR_BITS)
        if row is not None:
            observations.append(row)
    return observations


def fit(rows):
    if not rows:
        raise ValueError("calibration requires at least one mixing table")
    offsets = []
    parity_groups = defaultdict(list)
    for row in rows:
        scale = -log2(row["factor"])
        for e, rounds in row["rounds"].items():
            offsets.append((rounds - 1.5) * scale - e)
        parity_groups[row["parity"]].append(row["rounds"])
    return {"log2_amplitude": float(median(offsets)), "baseline": {
                str(e): round(median(row["rounds"][e] for row in rows)) for e in ERROR_BITS},
            "parity_medians": {str(score): {str(e): round(median(row[e] for row in grouped))
                                            for e in ERROR_BITS}
                               for score, grouped in sorted(parity_groups.items())}}


def predict(factor, exponent, log_amplitude=0):
    if not 0 < factor < 1:
        return None
    return max(1, 1 + ceil((exponent + log_amplitude) / -log2(factor)))


def ranks(values):
    ordered = sorted(range(len(values)), key=values.__getitem__)
    result = np.empty(len(values))
    start = 0
    while start < len(ordered):
        stop = start + 1
        while stop < len(ordered) and values[ordered[stop]] == values[ordered[start]]:
            stop += 1
        result[ordered[start:stop]] = (start + stop - 1) / 2
        start = stop
    return result


def evaluate(rows, model):
    results = {}
    for e in ERROR_BITS:
        truth = [r["rounds"][e] for r in rows]
        parity_predictions = []
        for r in rows:
            category = min(model["parity_medians"], key=lambda key: abs(int(key) - r["parity"]))
            parity_predictions.append(model["parity_medians"][category][str(e)])
        predictions = {"constant": [model["baseline"][str(e)]] * len(rows), "parity": parity_predictions,
                       "arnoldi": [predict(r["factor"], e, model["log2_amplitude"]) for r in rows],
                       "certified": [r["upper"][e] for r in rows],
                       "certified_with_remainder": [r["partial_upper"][e] for r in rows]}
        metrics = {}
        for name, estimates in predictions.items():
            pairs = [(a, b) for a, b in zip(truth, estimates) if b is not None]
            errors = [abs(a - b) for a, b in pairs]
            if not pairs:
                metrics[name] = {"covered": 0}
                continue
            x, y = zip(*pairs)
            rank = None if len(set(y)) < 2 or len(set(x)) < 2 else float(np.corrcoef(ranks(x), ranks(y))[0, 1])
            metrics[name] = {"covered": len(errors), "mae": float(np.mean(errors)), "spearman": rank,
                             "within_two_rounds": sum(d <= 2 for d in errors), "max_abs_error": max(errors),
                             "underestimates": sum(a > b for a, b in pairs)}
        # Per-bin min and max show the spread that a median alone would hide.
        bins = defaultdict(list)
        for actual, estimated in zip(truth, predictions["arnoldi"]):
            if estimated is not None:
                bins[estimated // 10 * 10].append((estimated, actual))
        by_prediction = []
        for lower, values in sorted(bins.items()):
            estimated, actual = zip(*values)
            by_prediction.append({"lower": lower, "n": len(actual), "median_prediction": median(estimated),
                                  "actual_min": min(actual), "actual_q25": float(np.quantile(actual, 0.25)),
                                  "actual_median": median(actual), "actual_q75": float(np.quantile(actual, 0.75)),
                                  "actual_max": max(actual)})
        results[str(e)] = {"actual_min_median_max": [min(truth), median(truth), max(truth)],
                           "metrics": metrics, "prediction_bins": by_prediction}
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    bench = subs.add_parser("benchmark", help="fit on one sample and score an independent sample")
    bench.add_argument("--train", type=int, default=128)
    bench.add_argument("--holdout", type=int, default=256)
    bench.add_argument("--output", type=Path, default=SUMMARY)
    analyze = subs.add_parser("table", help="estimate rounds for a table")
    add_table_arguments(analyze)
    analyze.add_argument("--error-bits", type=int, nargs="+", default=ERROR_BITS)
    analyze.add_argument("--model", type=Path, default=SUMMARY)
    analyze.add_argument("--exact", action="store_true", help="also find every exact threshold crossing")
    analyze.add_argument("--certificate", action="store_true", help="also certify sufficient round counts")
    parity = subs.add_parser("parity", help="use one fast Walsh transform, without building the difference matrix")
    add_table_arguments(parity)
    parity.add_argument("--error-bits", type=int, nargs="+", default=ERROR_BITS)
    parity.add_argument("--model", type=Path, default=SUMMARY)
    args = parser.parse_args()
    if args.command == "benchmark":
        if min(args.train, args.holdout) < 1:
            parser.error("draw counts must be positive")
        results = {}
        for bits in [4, 5]:
            train_seed, holdout_seed = 2026111900 + 2 * bits, 2026111901 + 2 * bits
            train, holdout = sample(1 << bits, args.train, train_seed), sample(1 << bits, args.holdout, holdout_seed)
            if not holdout:
                parser.error("holdout contains no mixing tables")
            model = fit(train)
            results[str(bits)] = {"train_seed": train_seed, "holdout_seed": holdout_seed,
                                  "train_draws": args.train, "holdout_draws": args.holdout,
                                  "train_mixing": len(train), "holdout_mixing": len(holdout),
                                  "model": model, "holdout": evaluate(holdout, model)}
        args.output.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")
        return
    if min(args.error_bits) < 1:
        parser.error("error bits must be positive")
    try:
        p = validated_table(read_table_arguments(parser, args))
        if len(p) < 4:
            raise ValueError("supply a permutation on at least two bits")
        if args.command == "parity":
            score = parity_score(p)
            result = {"parity_agreement_up_to_complement": (len(p) + score) // 2, "table_size": len(p),
                      "nonmixing_certified": score == len(p)}
            if score < len(p):
                result["necessary_cipher_rounds"] = {e: parity_lower_rounds(len(p), score, e)
                                                    for e in args.error_bits}
                model = json.loads(args.model.read_text()).get(str(len(p).bit_length() - 1), {}).get("model")
                if model:
                    category = min(model["parity_medians"], key=lambda key: abs(int(key) - score))
                    result["estimated_rounds_if_mixing"] = {
                        e: model["parity_medians"][category][str(e)] for e in args.error_bits if e in ERROR_BITS}
            print(json.dumps(result, indent=2))
            return
        counts = transition_counts(p)
    except ValueError as error:
        parser.error(str(error))
    period = chain_period(counts)
    result = {"status": "mixing" if period == 1 else ("disconnected" if period is None else "periodic")}
    if period == 1:
        model = json.loads(args.model.read_text()).get(str(len(p).bit_length() - 1), {}).get("model", {})
        factor = arnoldi_factor(counts)
        amplitude = model.get("log2_amplitude", 0)
        result.update({"arnoldi_factor": factor, "calibrated": bool(model), "estimated_cipher_rounds":
                       {e: predict(factor, e, amplitude) for e in args.error_bits}})
        if args.exact:
            result["exact_cipher_rounds"] = exact_rounds(counts, args.error_bits)
        if args.certificate:
            _, result["sufficient_cipher_rounds"] = block_certificate(counts, args.error_bits)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
