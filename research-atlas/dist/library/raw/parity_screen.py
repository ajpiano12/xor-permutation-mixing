"""Screen a permutation oracle for a parity preserved up to a constant."""

from collections.abc import Callable
from dataclasses import dataclass
from math import ceil, log
from operator import index
from random import Random, SystemRandom
from typing import Literal


@dataclass(frozen=True)
class ParityResult:
    status: Literal["nonmixing", "candidate", "no_witness"]
    mask_basis: tuple[int, ...]
    evaluations: int


def parity_query_budget(bits: int, delta: float, epsilon: float) -> int:
    """Calls sufficient to reject all delta-far masks with error at most epsilon.

    A delta-far mask disagrees with its proposed parity identity on at least
    a delta fraction of inputs. The returned budget includes the call to P(0)
    and is capped at the cost of an exhaustive search.
    """
    if bits < 1 or not 0 < delta <= 1 or not 0 < epsilon < 1:
        raise ValueError("require bits >= 1, 0 < delta <= 1, and 0 < epsilon < 1")
    size = 1 << bits
    draws = (bits * log(2) - log(epsilon)) / delta
    return size if draws >= size - 1 else 1 + ceil(draws)


def screen_parity(
    bits: int,
    evaluate: Callable[[int], int],
    *,
    budget: int | None = None,
    rng: Random | None = None,
) -> ParityResult:
    """Find masks m with m·P(x) = m·x XOR m·P(0), assuming P is a permutation.

    Pass table.__getitem__ for an explicit table or a callable for a circuit.
    An unlimited budget (default) or a budget >= 2**bits is exhaustive. Smaller
    budgets include the anchor P(0) and sample nonzero inputs with replacement.
    'nonmixing' certifies the returned masks exactly. 'candidate' means they
    passed the sampled inputs. 'no_witness' rules out this obstruction family.
    The mask basis represents all surviving masks by their binary span.
    """
    if bits < 1 or (budget is not None and budget < 1):
        raise ValueError("bits and any supplied evaluation budget must be positive")
    if bits == 1:
        # There is only one nonzero difference, so no proper nonempty closed set.
        return ParityResult("no_witness", (), 0)
    size = 1 << bits
    exhaustive = budget is None or budget >= size
    if exhaustive:
        inputs = range(1, size)
    else:
        generator = rng if rng is not None else SystemRandom()
        inputs = (generator.randrange(1, size) for _ in range(budget - 1))

    def image(x: int) -> int:
        value = index(evaluate(x))
        if not 0 <= value < size:
            raise ValueError("permutation output is outside the given bit width")
        return value

    anchor = image(0)
    evaluations = 1
    rows = [0] * bits
    rank = 0
    for x in inputs:
        row = x ^ image(x) ^ anchor
        evaluations += 1
        while row:
            pivot = row.bit_length() - 1
            if rows[pivot] == 0:
                rows[pivot] = row
                rank += 1
                break
            row ^= rows[pivot]
        if rank == bits:
            return ParityResult("no_witness", (), evaluations)

    # Solve the triangular equations in order from low to high pivot bits.
    mask_basis = []
    for free_bit, pivot_row in enumerate(rows):
        if pivot_row:
            continue
        mask = 1 << free_bit
        for bit, row in enumerate(rows):
            if (row & mask).bit_count() % 2:
                mask |= 1 << bit
        mask_basis.append(mask)
    return ParityResult("nonmixing" if exhaustive else "candidate", tuple(mask_basis), evaluations)
