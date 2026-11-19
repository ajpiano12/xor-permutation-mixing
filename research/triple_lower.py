"""Count the collision patterns needed for the three-round triple TV lower bound."""

from collections import Counter
from itertools import combinations


def leading_patterns(copies):
    """Count consistent histories up to rank 2(copies-1) for distinct two-key paths."""
    if copies not in (2, 3):
        raise ValueError("the lower bound uses two or three copies")
    max_span_size = 1 << (2 * (copies - 1))
    keys = [(1 << (2 + 2 * c), 1 << (3 + 2 * c)) for c in range(copies)]
    # A key pair is identical only when both vector equations hold simultaneously.
    equal_paths = [(a ^ c, b ^ d) for (a, b), (c, d) in combinations(keys, 2)]
    totals = Counter()

    def impose(eq, span, forbidden):
        if eq in span:
            return span
        if len(span) == max_span_size:
            return None
        enlarged = span | {x ^ eq for x in span}
        # Low bits 1 and 2 denote two fixed independent binary vectors.
        if enlarged.intersection((1, 2, 3)) or enlarged.intersection(forbidden):
            return None
        if any(left in enlarged and right in enlarged for left, right in equal_paths):
            return None
        return enlarged

    def visit(answers, table, forbidden, span):
        t = len(answers)
        if t:
            c, slot = divmod(t - 1, 6)
            if c and slot in (4, 5):
                # Match this output relative to its triple's anchor to copy zero.
                eq = answers[-1] ^ answers[6 * c + 3] ^ answers[slot] ^ answers[3]
                span = impose(eq, span, forbidden)
                if span is None:
                    return
        if t == 6 * copies:
            totals[len(span).bit_length() - 1, len(table)] += 1
            return

        c, slot = divmod(t, 6)
        r, i = divmod(slot, 3)
        # Process the initial triple in order (2,0,1), anchoring at the third point.
        arg = keys[c][r] ^ ((2, 0, 1)[i] if r == 0 else answers[t - 3])
        for old, value in table:
            if (arg ^ old) in span:
                visit((*answers, value), table, forbidden, span)
                return

        if len(span) < max_span_size:
            for old, value in table:
                candidate = impose(arg ^ old, span, forbidden)
                if candidate is not None:
                    visit((*answers, value), table, forbidden, candidate)

        # A fresh input to a permutation has an output distinct from all old outputs.
        fresh = 1 << (2 + 2 * copies + t)
        inequalities = forbidden.union(arg ^ old for old, _ in table)
        inequalities = inequalities.union(fresh ^ value for _, value in table)
        visit((*answers, fresh), (*table, (arg, fresh)), inequalities, span)

    visit((), (), frozenset(), frozenset({0}))
    return totals


if __name__ == "__main__":
    for copies in (2, 3):
        counts = leading_patterns(copies)
        expected = {(2 * (copies - 1), 6 * copies): 1}
        if counts != expected:
            raise RuntimeError(f"unexpected pattern counts for {copies} copies: {counts}")
        for (rank, inputs), count in counts.items():
            print(f"{copies} copies: rank {rank}, {inputs} distinct inputs, {count} pattern")
