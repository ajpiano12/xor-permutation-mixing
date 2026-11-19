# Exact pair and triple mixing at small error

At TV at most $2^{-128}$, the fastest three-bit tables for pairs take **87 cipher rounds**. The fastest three-bit tables for triples take **88 rounds**, and constitute a different family. The 10,752 almost perfect nonlinear (APN) permutations attain the pair minimum. Each needs **129 rounds** for triples. Another 10,752 permutations reach the triple target in 88 rounds. Both families reached the old triple threshold of $1/4$ in four rounds, so that threshold concealed a 41-round difference at higher precision.

All distances here maximize over every ordered distinct starting tuple for the fixed public permutation. Each cipher round draws a fresh independent XOR key shared by the inputs. The thresholds $2^{-16},2^{-32},2^{-64},2^{-128}$ compare different error budgets on the same table. We also report $2^{-n}$ in the data to give a target that scales with bit length. [Exact measurements](../results/small_error_times.csv)

## Exhaustive results on three bits

Each cell gives the exact first full cipher round at or below the indicated threshold. The grouped rows cover all 32,256 mixing tables at each order. The other 8,064 tables at each order fail to mix. The CSV gives their support status and the rows for the 20 original symmetry classes.

| Tuple order | Number of tables | $2^{-16}$ | $2^{-32}$ | $2^{-64}$ | $2^{-128}$ |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pair | 10,752 | 12 | 23 | 44 | 87 |
| Pair | 10,752 | 13 | 24 | 45 | 88 |
| Pair | 5,376 | 18 | 34 | 66 | 130 |
| Pair | 5,376 | 19 | 35 | 67 | 131 |
| Triple | 10,752 | 14 | 24 | 46 | 88 |
| Triple | 10,752 | 17 | 33 | 65 | 129 |
| Triple | 5,376 | 19 | 35 | 67 | 131 |
| Triple | 5,376 | 20 | 36 | 68 | 132 |

## An obstruction visible to ordered triples

A triple determines two distinct nonzero binary differences $a,b$ and a plane whose three nonzero elements are $a,b,a+b$. There are seven planes at three bits. Each plane admits six ordered bases. Use the ascending ordering of its three nonzero elements as a reference. The sign of an ordered basis is the parity of the ordering $(a,b,a+b)$ relative to the reference.

Define a seven-by-seven matrix $S$. Start from the reference basis of plane $i$, take one difference step, and set $S_{ij}$ equal to the probability of landing in plane $j$ with positive sign minus that of landing there with negative sign. Reordering the three inputs commutes with the random keyed map, including when the reordering changes the base point used for the differences. This reordering acts as the same permutation, up to a fixed identification, on the three nonzero differences, so a transposition reverses their sign. The vector of signed probabilities after $s$ steps from any basis of plane $i$ is therefore the $i$th row of $S^s$, up to the starting sign. Uniform has zero signed probability in each plane.

For **every three-bit APN permutation**, direct integer multiplication gives

$$ (8S)(8S)^\mathsf{T}=16I. $$

The verification uses four representatives, covering all 10,752 APN permutations. A translation of the input or output preserves the shape kernel, and conjugating by a linear map relabels the planes and their orientation signs. This preserves the matrix identity. Thus $2S$ is orthogonal and the signed-probability vector after $s$ steps has Euclidean norm $2^{-s}$. Its sum of absolute entries is at least that large. This sum is bounded above by twice the TV distance, by grouping the positive- and negative-sign states within each plane. Since full-round TV at $r$ equals shape TV at $s=r-1$, **every starting triple** of every three-bit APN permutation satisfies

$$ d(r)\ge 2^{-r}\qquad(r\ge1). $$

This explains why improving the target from $2^{-64}$ to $2^{-128}$ costs this family another 64 rounds. The pair result uses a different observable, the derivative hyperplane, and its decay factor is $1/\sqrt 8$ per step. [Pairwise certificate](QUADRATIC_CERTIFICATE.md)

## Why the faster triple family gains ground

Consider the representative $(0,1,2,4,5,6,7,3)$ of the other 10,752-table family. Its signed matrix satisfies $S^2=0$. Its full triple-shape matrix $Q$ is an average of eight permutation matrices on the 42 ordered shapes. Set $B=8Q$. The verifier constructs this matrix from the representative and checks the following exact identities.

$$ H=B^2(B-8I)(B+I)\ne 0,\qquad H(B^2-8I)=0. $$

Consequently the only possible eigenvalues of $B$ are $0,8,-1,\sqrt8,-\sqrt8$. At least one of the last two occurs since $H\ne0$. The nonzero roots of the annihilating polynomial are simple, so their Jordan blocks have size one. The support check confirms irreducibility and aperiodicity, and the stationary projection is uniform. The spectral radius on the zero-sum space of $Q$ is therefore exactly $1/\sqrt8$. Writing $U$ for the uniform matrix, twice the worst-start shape TV equals the induced row-sum norm $\lVert Q^s-U\rVert_\infty$. The eigenspace decomposition bounds this norm above by a constant times $8^{-s/2}$ for $s\ge2$, and its spectral radius gives the matching lower bound. Thus this family's triple distance gains asymptotically 1.5 bits of precision per round. The two small matrix checks explain the observed separation independently of extrapolating the four measured cutoffs. [Integer verification](small_error_census.py)

## Four bits as a check on transfer

On four bits, the patched inverse uses the polynomial basis modulo $X^4+X+1$. The eight random tables below are the **first eight** from the previously recorded, seeded four-bit sample. Each range reports the minimum and maximum of eight exact worst-start hitting times.

| Table or sample | Order | $2^{-16}$ | $2^{-32}$ | $2^{-64}$ | $2^{-128}$ |
| --- | --- | ---: | ---: | ---: | ---: |
| Field inverse | Pair | 13 | 24 | 47 | 92 |
| Field inverse | Triple | 14 | 26 | 49 | 95 |
| First eight sampled tables | Pair | 12–20 | 22–37 | 41–70 | 80–138 |
| First eight sampled tables | Triple | 12–20 | 22–37 | 42–70 | 81–138 |

This small comparison checks how pair and triple rates behave within the same tables. Estimating a four-bit population distribution would require a larger sample.

## Exact arithmetic and attribution

The program uses the existing enumeration up to input and output translations and binary linear conjugacy. For each representative and order $t$, one state records the $t-1$ ordered differences from a base input. For worst-start TV, translations and input reorderings allow one start per translation class of unordered input sets. At difference step $s$ let $c_y$ count paths to shape $y$, let $m$ be the number of shapes and let $K=N^s$ with $N=2^n$. The program compares $2^k\sum_y|mc_y-K|$ with $2mK$ using integers, switching from 64-bit to arbitrary precision before overflow. This determines exactly when error crosses $2^{-k}$. An independent regression check reproduces the three-bit inverse pair results from its closed-form distances. [Higher-order census method](HIGHER_CENSUS.md)

Run the following command from the repository root.

```sh
uv run --locked --extra four-bit -m research.small_error_census
```

O’Connor reported the 10,752 three-bit APN permutations and studied pairwise differential convergence. The small-error census, the signed orientation identities for triples and the finite matrix verification above are project computations. Publication priority for these specific results remains unverified. [O’Connor, EUROCRYPT 1995](https://doi.org/10.1007/3-540-49264-X_2)
