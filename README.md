# Three-bit key-alternating cipher mixing times

This experiment enumerates all 40,320 permutations of three-bit strings for the
pairwise case (`t = 2`) of problem 4. Each round applies the same public
permutation as `x → P(x XOR K)`, using a fresh uniform three-bit key shared by
both inputs. The measurement is the first round at which **every** ordered pair
of distinct inputs is within total variation distance ε of uniform on the 56
ordered pairs of distinct outputs.

## Run

```sh
uv run --locked mixing.py
uv run --locked python -m unittest discover -s tests -v
```

The included results use ε = 1/4, 1/8, 1/16, 1/32, 1/64 and 1/128. To try
other thresholds and keep these results, choose a different output directory.

```sh
uv run --locked mixing.py --epsilons 1/4 0.1 1/1000 --output-dir results-custom
```

The program uses Python 3.10 or newer and the standard library. It accepts
fractions and decimals in the range 0 < ε ≤ 1/2. At those thresholds a
reducible or periodic seven-state chain always has a starting state whose
distance exceeds ε. Threshold comparisons use exact fractions.

## Results

Of the 40,320 permutations, **32,256 (80%) mix**, 7,680 have disconnected
difference graphs, and 384 have connected graphs of period seven. For example,
the identity fixes every difference. The permutation with images
`0 2 4 6 3 1 7 5` cycles deterministically through all seven differences.

| ε | Fastest pair mixing (rounds) | Slowest finite pair mixing (rounds) |
|---:|---:|---:|
| 1/4 | 3 | 5 |
| 1/8 | 3 | 6 |
| 1/16 | 4 | 7 |
| 1/32 | 5 | 8 |
| 1/64 | 5 | 9 |
| 1/128 | 6 | 10 |

- [permutations.csv](results/permutations.csv) contains one row per permutation
  per threshold. The eight numbers in `permutation` give P(0) through P(7).
- [summary.csv](results/summary.csv) groups these rows by threshold, graph
  status, period and mixing time. To plot a histogram at a given ε, filter to
  `status == "mixing"`, use `pair_rounds` as the horizontal axis, and use
  `permutations` as the count. At ε = 1/4 the counts for rounds 3, 4 and 5 are
  10,752, 16,128 and 5,376.

Both files give a numeric `epsilon` for plotting and an `epsilon_exact` fraction
for reproducing the cutoff. Empty round counts indicate failure to converge to
uniform from every start. The period is given for connected chains.

## Calculation

For nonzero XOR differences a and b, the transition probability is

```text
T[a,b] = #{u in {0,…,7} : P(u) XOR P(u XOR a) = b} / 8.
```

Every row sums to one. Every column does too, since each of the eight ordered
output pairs of difference b has exactly one ordered preimage under P. Thus
uniform on the seven differences is stationary. The program checks connectivity
and period before computing powers. For a mixing chain it propagates integer
key-sequence counts and finds the least r satisfying

```text
max_a (1/2) sum_b |T^r[a,b] − 1/7| ≤ ε.
```

This is `difference_rounds`. To see why `pair_rounds` is exactly one more,
condition on difference b just before the next key. The common XOR makes the
ordered pair uniform on the eight pairs of that difference. These seven sets
are disjoint and equally sized, so the pair's distance from uniform equals the
preceding difference distance. The final application of P to both coordinates
preserves that distance. The zero-round pair distance is 55/56.

The exhaustive loop computes one matrix for every P with P(0) = 0. XORing
any constant into all eight outputs cancels in the difference formula. Writing
all eight translations of each of the 7! representatives covers every labeled
permutation exactly once per threshold.

## The inverse permutation as a benchmark

Liu, Tessaro and Vaikuntanathan analyze the patched field inverse (zero maps
to zero) in Appendix A. Their two-round theorem assumes an even bit length
and includes a final XOR key. Section 4 allows different public permutations
across rounds. The experiment here fixes one P throughout and measures the
odd-bit case directly. [Liu, Tessaro and Vaikuntanathan, full paper](https://eprint.iacr.org/2021/507.pdf)

In the polynomial basis of GF(8) modulo x³ + x + 1, the inverse has images
`0 1 5 6 7 2 3 4`. Its one-step distance is 3/7. In two difference rounds
the probability of returning to the starting difference is 1/4 and the
probability of each other difference is 1/8. Thus T² = (1/8)I + (7/8)U,
where every row of U is uniform. Every two more rounds divide the distance by
eight. This gives an independent check on the sweep and explains why the
inverse needs just **3, 3, 4, 5, 5 and 6 cipher rounds** at the six thresholds.
It attains the minimum at each.

Jain, Liu, Mizgerd, Pelecanos, Tessaro and Vaikuntanathan show that the
inverse walk requires Ω(q log(1/ε)) rounds for approximate **four-wise**
independence in their asymptotic regime, where q is the field size. This
distinction matters when extending the experiment beyond pairs. [Jain et al., *How Fast Does the Inverse Walk Approximate a Random Permutation?*](https://eprint.iacr.org/2024/1795)
