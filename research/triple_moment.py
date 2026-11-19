"""Enumerate low-codimension collision patterns for keyed triple walks.

A formal XOR expression is a bitmask. Bits zero and one denote the two
linearly independent fixed starting offsets. Further bits denote independent
vector variables, each of which ranges freely over the whole field.
"""

from collections import Counter
from fractions import Fraction
from itertools import permutations
from math import factorial


def remainder(expression, basis):
    for pivot, row in basis:
        if expression & pivot:
            expression ^= row
    return expression


def add_equation(expression, basis):
    """Set the XOR expression to zero, or return None for a contradiction."""
    reduced = remainder(expression, basis)
    if reduced == 0:
        return basis
    if reduced < 4:
        return None  # The two fixed offsets are linearly independent.
    pivot = 1 << (reduced.bit_length() - 1)
    return sorted([*basis, (pivot, reduced)], reverse=True)


def low_rank_patterns(rounds, copies=2):
    """Counts terminal alias patterns by equality rank and distinct calls."""
    outcomes = Counter()
    calls_per_path = 3 * rounds
    output_bit_offset = 2 + copies * rounds
    max_rank = 2 * (copies - 1)

    def visit(replies, history, basis, unequal):
        step = len(replies)
        # Constrain the endpoint shape to equal the first path's as soon as its
        # coordinates are available. This prunes infeasible three-path branches early.
        if step > calls_per_path:
            last_path, within = divmod(step - 1, calls_per_path)
            last_layer, i = divmod(within, 3)
            if last_layer == rounds - 1 and i in (1, 2):
                first_endpoint = calls_per_path - 3
                latest_endpoint = last_path * calls_per_path + first_endpoint
                equation = (replies[first_endpoint] ^ replies[first_endpoint + i]
                            ^ replies[latest_endpoint] ^ replies[latest_endpoint + i])
                basis = add_equation(equation, basis)
                if basis is None or len(basis) > max_rank:
                    return
                if any(remainder(e, basis) == 0 for e in unequal):
                    return
        if step == calls_per_path * copies:
            outcomes[len(basis), len(history)] += 1
            return

        path, within = divmod(step, calls_per_path)
        layer, position = divmod(within, 3)
        key = 1 << (2 + path * rounds + layer)
        previous = (0, 1, 2)[position] if layer == 0 else replies[step - 3]
        address = previous ^ key

        # A forced alias is the only possible case because old addresses are distinct.
        for old, value in history:
            if remainder(address ^ old, basis) == 0:
                visit([*replies, value], history, basis, unequal)
                return

        # A possible alias adds one independent equality. All aliases reuse the old reply.
        if len(basis) < max_rank:
            for old, value in history:
                updated = add_equation(address ^ old, basis)
                if updated is not None and all(remainder(e, updated) != 0 for e in unequal):
                    visit([*replies, value], history, updated, unequal)

        # The remaining case assigns a new reply to an address distinct from every old one.
        value = 1 << (output_bit_offset + step)
        excluded = [address ^ old for old, _ in history]
        excluded.extend(value ^ old_value for _, old_value in history)
        visit([*replies, value], [*history, (address, value)], basis, [*unequal, *excluded])

    visit([], [], [], [])
    return dict(sorted(outcomes.items()))


def one_round_at_eight():
    """Independent finite check over every normalized permutation at q=8."""
    n = 8
    matches = 0
    for tail in permutations(range(1, n)):
        table = (0, *tail)
        histogram = Counter((table[k] ^ table[k ^ 1], table[k] ^ table[k ^ 2])
                            for k in range(n))
        matches += sum(v*v for v in histogram.values())
    measured = Fraction(matches, n**2 * factorial(n-1))
    predicted = (Fraction(1, n) + Fraction(3, n*(n-3))
                 + Fraction(n-4, n*(n-3)*(n-5)))
    assert measured == predicted
    return measured


if __name__ == "__main__":
    print("One-step finite collision probability at q=8:", one_round_at_eight())
    for rounds in range(1, 4):
        patterns = low_rank_patterns(rounds)
        print(f"{rounds} difference step(s), counts by (rank, distinct calls): {patterns}")
        if rounds == 3:
            assert patterns == {(2, 18): 1}
    joint = low_rank_patterns(rounds=2, copies=3)
    assert joint == {(4, 6): 1, (4, 12): 3, (4, 18): 1}
    print("Three two-step paths, counts by (rank, distinct calls):", joint)
