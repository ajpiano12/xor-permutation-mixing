# Pairwise mixing of small key-alternating ciphers

These experiments study problem 4 for pairs of distinct inputs. They use the
same public permutation P in every round and a fresh uniform XOR key shared by
the pair. We count mixing and nonmixing permutations exactly for three and four
bits. We measure convergence rates exhaustively at three bits and by sampling
at four bits.

Explore the [Difference Atlas research map](research-atlas/dist/index.html) for
the questions, proofs, experiment data, and attribution notes. Run
`uv run research-atlas/serve.py` to monitor the working tree locally.

## Decide whether one permutation mixes

Given a truth table in the order P(0), P(1), …, [the classifier](classify_mixing.py)
decides pairwise mixing exactly for any positive bit length. It accepts decimal
or `0x` integers separated by spaces, commas or newlines, and infers the bit
length from the number of images.

```sh
uv run --locked classify_mixing.py 0 1 5 6 7 2 3 4
uv run --locked classify_mixing.py --witness 0 2 4 6 3 1 7 5
uv run --locked classify_mixing.py --file permutation.txt
```

The first example mixes. The second gives a connected chain of period seven,
and its witness lists the seven classes in cyclic order. On disconnected inputs,
`--witness` gives a nonempty proper set of differences closed under every key.
Use `--file -` to read standard input. The Python function `classify(images)`
returns the same decision and witnesses.

For $N=2^n$ table entries, the deterministic worst-case bounds are $O(N^2)$ time
and $O(N)$ words of memory. Affine permutations take $O(N)$ time. The proof also
explains when the search can stop early. [Decision theorem](LARGER_BITS.md#deciding-pairwise-mixing-from-a-truth-table)

For a succinct Boolean permutation circuit, an exact decision is NP-hard.
For black-box access, $N-1$ queries are necessary in the deterministic worst
case for $n\ge3$. [Proofs for circuit and oracle inputs](CIRCUIT_INPUT.md)

## Faster decisions for a single table

The randomized filter takes the same inputs as the exact classifier.

```sh
uv run --locked fast_mixing.py --error-bits 32 --file permutation.txt
uv run --locked fast_mixing.py --exact --file permutation.txt
```

**Every `mixing` result is exact.** All nonmixers return `unresolved` in filter
mode. For each fixed mixing permutation, the probability of `unresolved` is
at most $2^{-32}$ with the first command, over the filter's fresh random choices.
The filter first tests the transitions induced by just three sampled first
inputs. When they leave the answer open, Walsh–Hadamard transforms search
many differences simultaneously for edges that join components or break a
proposed period. With $N=2^n$ entries and error budget $\varepsilon$, the
worst-case cost is $O(N n^4\log(Nn/\varepsilon))$ word operations and $O(N)$
words. The proof gives the word width and constants. `--exact` checks
unresolved tables for an invariant parity and uses the deterministic
classifier if needed, with quadratic worst-case time for fixed error budget.
[Algorithm and proof](FAST_TABLE_PROOF.md) · [Python implementation](fast_mixing.py)

In a seeded check, the filter certified all 32,256 mixers in the three-bit
census and all 9,974 mixers in the four-bit sample. The 8,064 and 26
nonmixers, respectively, returned `unresolved`.

The deterministic classifier also has a native multicore implementation.
Build it with a C compiler that supports OpenMP. It accepts up to 32-bit table
entries and can print a closed set or cyclic classes on failure.

```sh
cc -O3 -std=c11 -fopenmp parallel_mixing.c -o /tmp/parallel_mixing
/tmp/parallel_mixing -j 8 --witness --file permutation.txt
```

Workers scan different rows of the same breadth-first-search level and merge
their successor bitsets. All those rows start at the same depth, so merging
preserves the period computation. The worst-case row work is still quadratic.
With $T$ workers the scratch bitsets take $T\lceil N/64\rceil$ 64-bit words
in addition to the table, depths and queue. The timings below include file
parsing and are medians of five runs on an Intel Core i9-13900H. The
15-bit table shuffles each high-bit half independently. The 18-bit table is
one uniformly shuffled permutation. [Native implementation](parallel_mixing.c)

| Fixed input | 1 thread | 2 threads | 4 threads | 8 threads |
| --- | ---: | ---: | ---: | ---: |
| 15-bit disconnected | 2.292 s | 1.156 s | 0.587 s | 0.363 s |
| 18-bit mixing | 0.088 s | 0.073 s | 0.062 s | 0.114 s |

## When the table is too large

The parity screen accepts a callable that maps an integer block to an integer
block. Fix the key if the callable implements a keyed block cipher. The
budget helper and screen can be used directly from Python.

```python
from parity_screen import parity_query_budget, screen_parity

# encrypt_block(x) evaluates the same fixed 128-bit permutation on every call.
budget = parity_query_budget(128, delta=0.01, epsilon=0.01)
result = screen_parity(128, encrypt_block, budget=budget)
```

A nonzero mask in an exhaustive result certifies disconnection. With a query
budget, `candidate` returns the basis of masks consistent with the samples.
`no_witness` proves that this particular family of obstructions is absent.
The 128-bit example takes at most 9,334 evaluations. With probability at least
99%, every surviving parity equation holds on more than 99% of all inputs.
A circuit proof can verify whether a surviving equation holds everywhere.
The exhaustive screen caught 7,232 of the 8,064 three-bit nonmixers and 25 of
the 26 nonmixers in the four-bit sample. [Parity screen](parity_screen.py) ·
[Guarantee and circuit verification](CIRCUIT_INPUT.md#screening-for-invariant-parities)

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
