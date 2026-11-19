# Predicting and certifying the pairwise round count

For a supplied table, twelve short matrix-vector products usually sufficed to rank four- and five-bit permutations by their exact pairwise mixing time. At TV $2^{-128}$, the mean absolute prediction error was **0.56 rounds on four bits** and **1.38 rounds on five bits**. These are measurements on held-out uniform permutations. A second calculation gives a rigorous upper bound for the individual table. Both counts include the final keyed round. [Program](rate_heuristic.py) · [Benchmark data and prediction bins](../results/rate_heuristic.json)

## What was tested

For each width we shuffled 128 uniform tables to calibrate the predictors and drew 256 more from an independent seeded stream to evaluate them. Every sampled table mixed. The exact answer is the first round at which the worst input pair reaches the given TV threshold. We computed the integer path counts for all input differences, including checks of the first crossing inside each eight-step interval. All fitting used only calibration tables. The seeds, fitted constants, and counts in each prediction bin are in the benchmark file.

| Bits | TV threshold | Exact rounds, min / median / max | Mean error, baseline | Mean error, parity | Mean error, Arnoldi | Rank correlation, Arnoldi |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 4 | $2^{-32}$ | 20 / 26 / 48 | 4.36 | 2.43 | 0.37 | 0.989 |
| 4 | $2^{-64}$ | 38 / 50 / 94 | 8.92 | 4.86 | 0.42 | 0.996 |
| 4 | $2^{-128}$ | 74 / 97.5 / 186 | 18.10 | 9.86 | 0.56 | 0.997 |
| 5 | $2^{-32}$ | 17 / 19 / 28 | 0.91 | 0.85 | 0.45 | 0.842 |
| 5 | $2^{-64}$ | 32 / 36 / 55 | 1.99 | 1.89 | 0.66 | 0.909 |
| 5 | $2^{-128}$ | 61 / 70 / 108 | 4.13 | 3.87 | 1.38 | 0.907 |

Mean error in the table means mean **absolute** error, measured in full cipher rounds. The baseline always predicts the median calibration time for that width and threshold. The parity predictor uses the calibration median among tables with the nearest observed best parity agreement. Rank correlation is Spearman's coefficient with tied ranks averaged. At the strictest threshold the spectral estimate was within two rounds on 248 of 256 four-bit tables and 216 of 256 five-bit tables. Its largest errors were 21 and 11 rounds respectively.

## Estimating speed from the slowest mode

Let $N=2^n$, $m=N-1$, and $T$ be the $m$-state pairwise difference matrix. Start with one fixed-seed mean-zero vector and repeatedly apply $T$. Arnoldi iteration orthogonalizes the resulting vectors. The largest eigenvalue modulus $\hat\rho$ of the resulting small matrix estimates the slowest decay factor. As $\hat\rho$ approaches one, an extra round removes less of the remaining bias. With a fitted amplitude $A$, the estimated full round count is

$$1+\left\lceil\frac{\lambda+\log_2 A}{-\log_2\hat\rho}\right\rceil \qquad (\epsilon=2^{-\lambda}).$$

The fitted $\log_2 A$ is the median of $(r-1.5)(-\log_2\hat\rho)-\lambda$ over the three thresholds and all calibration tables of that width. The half-round offset centers the integer crossing interval. The implementation uses at most 12 steps and two passes of orthogonalization. Constructing and storing $T$ takes $O(N^2)$ time and space. For a fixed step budget the additional arithmetic also costs $O(N^2)$. The method is an empirical ranking tool for pairs. Its measured accuracy concerns random tables at the two tested widths. [Arnoldi's original method](https://doi.org/10.1090/qam/42792)

The largest four-bit error gives a reproducible example. The predictor returned **129** rounds for the table below. Exact counts gave **150**, and the short-block certificate gave **157**. The twelve-dimensional projection reported a factor of 0.4985 while the full numerical eigenspectrum gives 0.5511.

```sh
uv run --locked --extra four-bit python -m research.rate_heuristic table 3 1 0 10 4 14 5 15 13 7 6 9 2 8 12 11 --error-bits 128 --certificate --exact
uv run --locked --extra four-bit python -m research.rate_heuristic benchmark
```

## A finite-round upper bound for an individual table

Write $d(k)$ for the worst-row TV of $T^k$ from uniform. The program computes $d(0),\ldots,d(12)$ exactly. It also computes $\beta$, the largest TV distance between two rows of $T^{12}$. Any signed difference between two probability laws can be written as its TV norm times the difference of two probability laws on disjoint supports. Applying $T^{12}$ to these latter laws gives two convex mixtures of rows. Their distance is at most $\beta$. Since uniform is stationary, iteration gives

$$d(12q+a)\le \beta^q d(a), \qquad 0\le a\le12.$$

The first $1+12q+a$ full rounds certified by this inequality give a sufficient count on the supplied permutation. When $\beta=1$ and the short profile still exceeds the threshold, this test returns no bound. All probabilities and threshold comparisons use integers or exact rational arithmetic. Forming twelve dense matrix powers and comparing all row pairs costs $O(N^3)$ arithmetic operations for fixed block length. At TV $2^{-128}$ the certificate covered all 512 held-out tables. Its mean excess over the exact answer was 8.61 rounds on four bits and 6.09 on five bits. The largest excesses were 20 and 11 rounds. The Dobrushin contraction coefficient is classical. [Seneta, *Coefficients of ergodicity*](https://doi.org/10.2307/1426855)

## A parity check that avoids the difference matrix

Compute the histogram of $x\oplus P(x)$ and take its Walsh–Hadamard transform. Its largest absolute nonconstant coefficient $s$ corresponds to a parity bit that $P$ preserves, up to a possible complement, on $(N+s)/2$ of its inputs. This costs $O(N\log N)$ arithmetic and $O(N)$ space for a table. The empirical parity-only ranking was useful on four bits and substantially weaker on five bits. Running the program in **parity** mode also returns a proven lower round bound.

To see the lower bound, adjoin the fixed zero difference to $T$, and denote the enlarged matrix by $\widetilde T$. Let $W$ be the orthogonal Walsh matrix. The established differential–linear transform gives $S=W\widetilde T W$, a matrix of squared normalized Walsh coefficients of $P$. It has nonnegative entries and a nonzero-mask diagonal entry $p=(s/N)^2$. At this entry $S^k_{vv}\ge p^k$ by staying on $v$ throughout. The target kernel fixes zero and makes each nonzero row uniform on all $m$ nonzero states. Its Walsh transform has diagonal entry $1/m$ at $v$. Expanding the Walsh transform of the kernel deviation shows each nonzero difference row contributes at most $2d(k)/N$ in absolute value. The zero row contributes zero. Therefore

$$d(k)\ge \frac{N}{2m}\max\{0,p^k-1/m\}.$$

In particular $s=N$ certifies failure to mix for $n\ge2$. Otherwise the code returns one plus the first $k$ at which this lower bound allows the requested distance. The inequality is a direct project corollary of the published transform. [Walsh identity and antecedents](RATES_AND_LITERATURE.md#literature-and-provenance)

```sh
uv run --locked --extra four-bit python -m research.rate_heuristic parity 3 1 0 10 4 14 5 15 13 7 6 9 2 8 12 11 --error-bits 128
```
