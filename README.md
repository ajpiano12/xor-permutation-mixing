# Pairwise mixing of small key-alternating ciphers

These experiments study problem 4 for pairs of distinct inputs. They use the
same public permutation P in every round and a fresh uniform XOR key shared by
the pair. We count mixing and nonmixing permutations exactly for three and four
bits. We measure convergence rates exhaustively at three bits and by sampling
at four bits.

## Exact four-bit count

Exactly **20,873,902,694,400 of the 16! permutations mix**, a fraction of
**179,759/180,180 (99.766345%)**. There are 48,887,150,592 disconnected cases
and 43,008 connected periodic cases, all with period 15.

A four-bit permutation fails to mix precisely when it is affine or maps the
cosets of some proper nonzero binary subspace to cosets of that same subspace.
A disconnected or periodic chain can therefore be recognized directly from the
16 images. The [counting argument](FOUR_BIT_COUNT.md) explains why the test is
exhaustive, how to avoid double counting, and why the fraction changes so much
between three and four bits.

The [larger-dimension proof](LARGER_BITS.md) extends this characterization to
five bits, constructs a six-bit counterexample, and gives a group-theoretic
mixing criterion valid at every bit length.

```sh
uv run --locked --extra four-bit exact_four_bit.py
uv run --locked --extra four-bit exact_four_bit.py --bits 3
```

## Four-bit sample

```sh
uv run --locked --extra four-bit sample_four_bit.py
uv run --locked python verify_rate_bins.py --scale 100000
uv run --locked --extra four-bit python -m unittest discover -s tests -v
```

The default run shuffles a fresh list of the 16 images for each of 10,000 draws
with replacement, using seed 20261118. Change `--samples`, `--seed`,
`--profile-rounds`, and `--output-dir` to run another experiment. Each
permutation acts on 15 nonzero differences. Graph reachability and period give
an exact classification independently of how long the distance curve is recorded.

**9,974 permutations mixed (99.74%), 26 were disconnected, and zero connected
periodic cases appeared in this sample.** The 95% Wilson interval for the
mixing fraction is 99.62% to 99.82%. At ε = 1/4 the counts for 3, 4, 5, 6 and 7
cipher rounds were 2,582, 7,300, 83, 7 and 2. The exhaustive three-bit fraction
was 80%. [Wilson's interval](https://www.jstor.org/stable/2276774)

Among mixing draws there were **9,957 distinct exact distance curves through
round 8**. The sample already had 6,978 different curves through round 3 and
9,924 through round 4. These counts compare the entire sequence of distances
from round 0 up to the indicated round.

For each mixing permutation, let T be its difference transition matrix, U the
uniform-row matrix, and d(r) its worst-start total variation distance. The CSV
reports the numerical spectral radius of T − U. This is the asymptotic factor
lim d(r)^(1/r), since 2d(r) is the maximum absolute row sum of (T − U)^r
for r ≥ 1. The median factor was 0.387 and the middle 90% ran from 0.319 to
0.539. The independent `verify_rate_bins.py` audit certifies **at least 7,798
distinct asymptotic factors** by finding witnesses in disjoint intervals of
width 0.00001. Floating-point eigenvalues select candidate intervals. Integer
characteristic polynomials and exact tests of the moduli of their roots certify
membership, including roots on interval boundaries.

A secondary concentration of slower rates appears near 0.53. For each nonzero
four-bit mask h, compare the parity bit h·x with h·P(x), allowing the latter
to be complemented. The best agreement over all masks was 14 of 16 inputs for
1,334 mixing permutations. Their median factor was 0.530, compared with 0.378
for the remaining 8,640. Perfect agreement on all 16 inputs preserves the
partition into the two parity classes and forces disconnection. It occurred in
25 of the 26 disconnected draws.

There is a reason for the location of that second peak. With agreement on 14
inputs, the two exceptions u and v lie on opposite sides of the parity split,
since the input and output bits are balanced. For difference u XOR v the bit of
the difference always survives a round. For every other nonzero difference a,
exactly four choices of x put just one of x and x XOR a among the exceptions.
Thus its bit flips with probability 1/4. Starting uniformly in each parity
class gives the one-step matrix `[[3/4, 1/4], [7/32, 25/32]]` (even, odd).
Its second eigenvalue is **17/32 = 0.53125**. This explains the scale of the
peak. The exceptional difference and the other odd differences have different
flip probabilities, so a single permutation's long-run rate still depends on
how probability moves within the classes.

- [Sample measurements](results/four_bit/samples.csv) give P(0) through P(15),
  status, period, numerical rate, best bit agreement, the first difference round
  at each threshold, and exact worst-start TV fractions at rounds 0 through 8.
  The cipher requires one additional round at these thresholds. Nonmixing draws
  have empty rate, time, and distance fields.
- [Summary](results/four_bit/summary.json) includes the sampling parameters,
  confidence interval, profile counts, rate quantiles and cipher-round counts
  for six thresholds from 1/4 to 1/128.
- [Convergence plot](results/four_bit/convergence.png) shows the spread of the
  exact distances over the mixing sample and a histogram of its asymptotic rates.

## Three-bit census

This experiment enumerates all 40,320 permutations of three-bit strings for the
pairwise case (`t = 2`) of problem 4. Each round applies the same public
permutation as `x → P(x XOR K)`, using a fresh uniform three-bit key shared by
both inputs. The measurement is the first round at which **every** ordered pair
of distinct inputs is within total variation distance ε of uniform on the 56
ordered pairs of distinct outputs.

### Run

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

### Results

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

### Calculation

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

### The inverse permutation as a benchmark

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
