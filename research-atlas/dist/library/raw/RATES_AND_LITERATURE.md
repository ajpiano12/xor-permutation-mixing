# How rapidly does a random fixed permutation mix pairs?

A uniformly sampled permutation on $n$ bits, fixed for the whole walk, takes **exactly three cipher rounds** to bring every starting pair within total variation $1/4$ of uniform with probability tending to one as $n$ grows. At two cipher rounds the distance tends to $e^{-1/2}\approx0.60653$. The third round averages over enough intermediate differences to make the distance vanish. The finite experiments below show how early this asymptotic behavior appears.

The fixed-threshold result and its finite bounds below are project derivations. The expected fraction of zero entries in a random XOR table is published, and earlier typical-ergodicity arguments make an additional graph-distribution assumption. A priority claim for the three-round theorem would require a further literature check. The final section gives a separate consequence of Liu, Tessaro and Vaikuntanathan's inverse calculation and classical trace counts.

## Model and round count

Write $N=2^n$, $m=N-1$, $V=\mathbb F_2^n$, and take $n\ge 2$. A cipher round applies $x\mapsto P(x+k)$, with a fresh uniform common key $k$ each round. Choose $P$ uniformly once when studying a random table. The following probabilities over keys are evaluated **after** fixing $P$. For nonzero $a,b\in V$ define

$$
T_{ab}=N^{-1}\#\{x:P(x)+P(x+a)=b\},\quad
U_{ab}=1/m,\quad M=T-U,\quad
d_j=\max_a \tfrac12\sum_b |(T^j)_{ab}-1/m|.
$$

$T$ is doubly stochastic. Conditioned on a difference, the final random XOR makes the ordered pair uniform in its fiber of size $N$. Those fibers are disjoint and the last permutation preserves distance to uniform. Thus the worst-start ordered-pair distance at cipher round $r\ge1$ is $d_{r-1}$. In particular the one-round distance is exactly $d_0=1-1/m$.

## The three-round theorem

For every fixed $K>0$, with probability $1-O_K(N^{-K})$ over the uniform table,

$$
d_2=O_K\!\left(\sqrt{\frac{\log N}{N}}\right).
$$

Every row's one-step TV tends to $e^{-1/2}$ simultaneously in probability. Hence for fixed $0<\epsilon<e^{-1/2}$ the worst-start pair mixing time is exactly three cipher rounds with probability tending to one. For $e^{-1/2}<\epsilon<1$ it is exactly two with probability tending to one. The argument leaves the behavior at the boundary $\epsilon=e^{-1/2}$ open. Irreducibility and aperiodicity both hold except on an event of probability $\exp(-\Omega(N))$.

### The matching behind a row

The unordered pairs $\{x,x+a\}$ for a fixed $a$ form a perfect matching on $N$ points. The image of this matching under uniform $P$ is a uniform perfect matching. Write $K_{ab}=NT_{ab}/2$ for its number of shared edges with the fixed $b$-matching. Every cell has the same marginal law. For the falling factorial $(x)_j=x(x-1)\cdots(x-j+1)$ and $j\le N/2$,

$$
\mathbb E(K_{ab})_j
= \frac{(N/2)_j}{(N-1)(N-3)\cdots(N-2j+1)}.
$$

Indeed each ordered list of $j$ distinct edges of the $b$-matching occurs in the image matching with probability the reciprocal of the displayed denominator. Each factor in the ratio is at most one and tends to $1/2$ for fixed $j$. For $j>N/2$ the factorial moment vanishes. Inclusion-exclusion for $\Pr(K_{ab}=0)$ and domination by $\sum_j1/j!$ give $\Pr(K_{ab}=0)\to e^{-1/2}$.

Every positive cell of $T$ is at least $2/N>1/m$. Hence the exact one-step TV of a row is its number of missing differences divided by $m$. Its mean is $\Pr(K_{ab}=0)$, the same for every $a$. The expected density of zero cells was determined by O'Connor. [O'Connor, *On the Distribution of Characteristics in Bijective Mappings*](https://doi.org/10.1007/BF00190756)

Transposing two images of $P$ changes at most two unordered edges in any input matching. Each changed edge moves mass $2/N$ within its row. Consequently every row changes by at most $4/N$ in TV or $8/N$ in $\ell^1$. The same bound holds for columns because $T(P^{-1})=T(P)^\top$.

If a real function of a uniform permutation changes by at most $c$ under such transpositions, revealing its images one at a time gives a martingale with increments bounded by $c$. Two possible choices of the next image can be coupled by interchanging those two outputs in the completion. Azuma's inequality gives $\Pr(|f-\mathbb Ef|>t)\le 2\exp[-t^2/(2Nc^2)]$. Applying this with $c=4/N$ and taking a union bound over the $m$ rows proves the simultaneous one-step claim.

### Two-step energy for one table used twice

Directly from the first two factorial moments,

$$
\mathbb E\sum_b T_{ab}^2=\frac{3N-8}{N(N-3)},\qquad
\mathbb E\|M\|_F^2
=\mathbb E\|T\|_F^2-1=\frac{2(N-2)^2}{N(N-3)}.
$$

The fourth moment $\mathbb E K_{ab}^4$ is at most $15$ by expanding into falling factorials with coefficients $1,7,6,1$ in increasing order. Cauchy–Schwarz across the $m^2$ cells gives $\mathbb E\|M\|_F^4\le \mathbb E\|T\|_F^4\le 16(m/N)^4\mathbb E K_{ab}^4\le 240$. These calculations require only the marginal law of each cell.

Let $L$ be an independent uniform invertible linear map on $V$ and $C$ its permutation matrix on the $m$ nonzero differences, oriented so that $T(LP)=T(P)C$. Any ordered pair of distinct nonzero vectors is linearly independent over $\mathbb F_2$. Therefore the linear group acts transitively on those ordered pairs. For any fixed $M$, the average of $CMM^\top C^\top$ has a constant diagonal and a constant off-diagonal. It kills the all-ones vector, and its trace is $\|M\|_F^2$. Thus

$$
\mathbb E_C[CMM^\top C^\top]=\frac{\|M\|_F^2}{m-1}(I-U).
$$

$LP$ is uniformly distributed, so we may calculate the energy of its square and average first over $L$. Orthogonality of $C$ and $M(I-U)=M$ give

$$
\mathbb E_P\|M^2\|_F^2
=\mathbb E_{P,C}\|MCMC\|_F^2
=\mathbb E_{P,C}\operatorname{tr}(MCMM^\top C^\top M^\top)
=\frac{\mathbb E_P\|M\|_F^4}{m-1}.
$$

This averaging preserves the reuse of the same permutation in **both** factors. Conjugating $P$ by $L$ permutes both row and column indices together. By transitivity every row of $M^2$ therefore has the same expected squared Euclidean norm. Applying Cauchy–Schwarz to a row and Jensen's inequality to its mean gives

$$
\mathbb E\,\mathrm{TV}(e_aT^2,u)
\le \tfrac12\sqrt{\mathbb E\|M^2\|_F^2}
\le \sqrt{60/(N-2)},
$$

where $e_a$ is point mass and $u$ is the uniform row. For tables $T,T'$ differing by a transposition of images of $P$, expand $T^2-(T')^2=(T-T')T+T'(T-T')$. Stochastic contraction in the first term and a convex combination of row differences in the second show that each two-step row's TV changes by at most $8/N$. Applying the transposition estimate again,

$$
\Pr\!\left(d_2>\sqrt{60/(N-2)}+t\right)
\le 2m\exp(-Nt^2/128).
$$

Choose $t$ proportional to $\sqrt{\log N/N}$ for the polynomial-tail bound. For large enough $N$ choose $t=1/4$ to obtain $d_2<1/2$ with exponentially small exception probability. On this event the maximum TV between two rows of $T^2$ is at most $2d_2<1$. Decomposing a signed zero-sum row into equal positive and negative masses gives $\mathrm{TV}(pT^2,qT^2)\le 2d_2\,\mathrm{TV}(p,q)$ for all distributions. Uniform is stationary, so every start converges and $d_{2j}\le d_2(2d_2)^{j-1}$ for $j\ge1$. This completes the proof.

## Exact mean of two steps with reuse

For $N\ge4$,

$$
\mathbb E_P[T(P)^2]=U+\frac{2}{N(N-3)}(I-U).
$$

A table reused across rounds has a small excess two-step return probability. Independent tables in the two rounds give exactly $U$ in expectation since $\mathbb E T=U$.

To see the correction from reuse, first conjugate $P$ by $L$. The same diagonal/off-diagonal argument shows that $\mathbb E_P[M^2]$ is a scalar multiple of $I-U$. To identify the scalar, condition on $M$ and again average over the independent output relabeling $C$. Write $r_i$ for the rows of $M$. In the expansion of $\operatorname{tr}(MCMC)$ the terms with equal row indices contribute $\|M\|_F^2/m$ in expectation. For $i\ne j$ the assigned columns are a uniform ordered pair of distinct columns, giving expected summand $-\langle r_i,r_j\rangle/[m(m-1)]$ since each row sums to zero. As the columns sum to zero too, $\sum_{i\ne j}\langle r_i,r_j\rangle=-\|M\|_F^2$. Thus $\mathbb E_C\operatorname{tr}(MCMC)=\|M\|_F^2/(m-1)$. Finally divide by $\operatorname{tr}(I-U)=m-1$ and insert the preceding one-step moment. This calculation accounts for the dependence between factors. The TV of the averaged row is distinct from the expected TV of a realized row.

## Every two-step entry concentrates

The same model gives a uniform relative error bound for individual transition probabilities. For every fixed $K>0$, except with probability $O_K(N^{-K})$,

$$
\max_{a,b}\left|(T^2)_{ab}-\frac1{N-1}\right|
=O_K\!\left(\frac{(\log N)^{3/2}}{N^{3/2}}\right).
$$

In particular $T^2$ is strictly positive with probability tending to one. For a derivation, set $s=\lceil\log N\rceil$. Markov's inequality applied to $(K_{ab})_s$ gives $\Pr(\max K_{ab}\ge s)\le m^2/s!$, smaller than every fixed negative power of $N$ asymptotically. Cap all entries of $T$ at $h=2s/N$ to obtain $B$. Write $F_{ab}=(B^2)_{ab}$. On the complementary event it equals $(T^2)_{ab}$, and both random variables lie in $[0,1]$. Their means differ by at most $m^2/s!$.

Under a transposition each capped row and column changes by at most $8/N$ in $\ell^1$, since coordinatewise capping contracts $\ell^1$ distance. In the dot product defining $F_{ab}$ the row change costs at most $8h/N$, and the column change costs as much. Hence $c=32s/N^2$ works in the transposition estimate. Union bound over $m^2$ cells with $t$ a sufficiently large $K$-dependent multiple of $s\sqrt{\log N}/N^{3/2}$. The exact mean just proved differs from $1/m$ by at most $2/[N(N-3)]$. Combining the three errors proves the bound.

## Fixed-seed numerical check

The rate probe tests the mean matrix and one-step energy by exact integer arithmetic over all tables at $N=4,8$, identifying output translations. It then samples 100 uniform tables at each bit length with seed 20261118. Distances are worst-start distances for each fixed permutation before taking medians across permutations.

| Bits | Median $d_1$ | Median $d_2$ | $d_2\le 1/4$ | Every $T^2$ entry positive |
|---:|---:|---:|---:|---:|
| 4 | 0.73333 | 0.29323 | 22/100 | 7/100 |
| 5 | 0.67742 | 0.19292 | 97/100 | 65/100 |
| 6 | 0.66667 | 0.13063 | 100/100 | 99/100 |
| 7 | 0.66142 | 0.08844 | 100/100 | 100/100 |
| 8 | 0.64706 | 0.05959 | 100/100 | 100/100 |
| 9 | 0.63796 | 0.04032 | 100/100 | 100/100 |

Run from the repository root using the project environment.

    OPENBLAS_NUM_THREADS=1 uv run --locked --extra four-bit research/rate_probe.py

The measured $\sqrt N\,d_2$ medians are about $0.95$ at seven bits and $0.91$ at nine. Whether they approach a positive constant, and whether the worst-start $\sqrt{\log N}$ in the bound can be removed, remain open in this analysis.

## Literature and provenance

- **The Markov model and convergence question.** Lai, Massey and Murphy derive the homogeneous difference chain with independent round keys. O'Connor and Golić, §3 Theorem 5, bound the number of nonzero transitions for a random table. Their Corollary 2 infers typical ergodicity under the explicit additional assumption that the support graph is uniform given its edge count. Their conclusion leaves convergence rates for further work. The proof above works directly with the distribution induced by a permutation, including dependencies between edges. [Lai, Massey and Murphy, EUROCRYPT 1991](https://doi.org/10.1007/3-540-46416-6_2), [O'Connor and Golić, ASIACRYPT 1994, pp. 391, 396](https://link.springer.com/content/pdf/10.1007%2FBFb0000450.pdf)
- **Differentially 2-uniform permutations.** O'Connor's §2.2 explicitly assumes ergodicity in Proposition 2.1 and reports a census of all $8!$ permutations in support of it. All 10,752 three-bit differentially 2-uniform permutations mix. Section 3.1 rigorously proves positivity of the Gram matrix $TT^\top$ by row-support intersection, computes the Gram matrix for a three-bit field example and models general off-diagonal intersections by a binomial law. These are direct predecessors for Gram-based rate proofs. The three-round theorem above concerns an unrestricted uniform permutation and uses its true distribution. The paper also reports seven distinct transition matrices in its census. With differences labeled in their original order, the rate probe counts **168 distinct matrices**, each arising from 64 permutations, so the distinction matters when comparing counts. [O'Connor, EUROCRYPT 1995, pp. 17–21](https://link.springer.com/content/pdf/10.1007%2F3-540-49264-X_2.pdf)
- **Single-round statistics.** O'Connor calculates the exact distribution of XOR-table entries of a uniform permutation. Daemen and Rijmen revisit differential and linear probability distributions, distinguishing random permutations from other distributions over mappings. The zero-probability limit and elementary one-step energy here are consequences of the random-matching count. The dependence of repeated steps enters at $T(P)^2$. [O'Connor, *On the Distribution of Characteristics in Bijective Mappings*](https://doi.org/10.1007/BF00190756), [Daemen and Rijmen, *Probability Distributions of Correlation and Differentials*](https://cs.ru.nl/~joan/papers/JDA_VRI_Stat_2007.pdf)
- **Walsh and difference spectra.** Include the isolated zero difference by taking $\widetilde T=1\oplus T$. If $W_{ux}=N^{-1/2}(-1)^{u\cdot x}$ and $(S_P)_{xy}=\mathbf1_{y=P(x)}$, then $W\widetilde T W=(W S_P W)^{\circ2}$, where the square on the right is entrywise. Expanding the left side gives $N^{-2}\sum_{x,y}(-1)^{u\cdot(x+y)+v\cdot(P(x)+P(y))}$, the square of the corresponding Walsh coefficient. This is the established differential/linear transform. It yields the same spectrum on both sides, including the additional trivial eigenvalue. Canteaut and Roué separately show how affine equivalence can change two-round differential probabilities. [Chabaud and Vaudenay, EUROCRYPT 1994](https://doi.org/10.1007/BFb0053450), [Blondeau, Leander and Nyberg, equation (4)](https://www.iacr.org/archive/fse2014/85400143/85400143.pdf), [Canteaut and Roué, EUROCRYPT 2015](https://www.iacr.org/archive/eurocrypt2015/90560131/90560131.pdf)
- **Statistical security under composition.** Vaudenay's decorrelation framework develops distribution matrices on tuples and bounds for independently keyed composition. Here the realized one-round key ensembles are independent conditional on $P$. Averaging over $P$ reintroduces dependence, as the exact mean of two steps illustrates. Liu, Tessaro and Vaikuntanathan's Section 4.5 allows a different public permutation per round in its existence argument. Their Appendix A.1 does reuse the patched field inverse. [Vaudenay, *Decorrelation*](https://doi.org/10.1007/s00145-003-0220-6), [Liu, Tessaro and Vaikuntanathan, full paper](https://eprint.iacr.org/2021/507.pdf)
- **One public permutation across rounds.** Wu, Yu, Cao and Dong and the subsequent general result of Yu, Wu, Yu, Cao and Dong consider key-alternating ciphers that reuse a public random permutation. Their security game limits oracle queries, including access to that permutation. Here the table may be entirely known when selecting the starting pair and evaluating its output law, and there are fresh independent XOR keys. This distinction matters when comparing quantitative conclusions. [Wu et al., ASIACRYPT 2020](https://eprint.iacr.org/2020/1073), [Yu et al., TCC 2023](https://eprint.iacr.org/2023/1355)
- **From pairs to higher orders.** Jain et al. prove an $\Omega(N\log(1/\epsilon))$ lower bound for approximate four-wise independence in the inverse-walk regime they analyze. Its proximity to pairwise uniformity can coexist with a large obstruction at order four. [Jain et al., *How Fast Does the Inverse Walk Approximate a Random Permutation?*](https://eprint.iacr.org/2024/1795)

## The patched inverse has an exact two-step distance

Let $P(x)=x^{-1}$ on $\mathbb F_N^\times$, $P(0)=0$, and write $\psi(x)=(-1)^{\operatorname{Tr}_{\mathbb F_N/\mathbb F_2}(x)}$. Liu, Tessaro and Vaikuntanathan bound the even-bit distance by $5/N$ for $n\ge4$ and report numerical evidence of a constant at most two. They use two inverse applications with a final XOR key, giving the same TV as our third cipher round. Their cases combined with the classical trace/co-trace count yield an exact formula of either parity and the asymptotic constant $7/4$. These are corollaries of the field calculation and the trace count. [Liu, Tessaro and Vaikuntanathan, Appendix A.1](https://eprint.iacr.org/2021/507.pdf), [Bojilov, Borissov and Borissov, §5.1](https://arxiv.org/abs/1711.08306)

For nonzero $a,b$ the equation $P(x)+P(x+a)=b$ at $x\notin\{0,a\}$ becomes $z^2+z=(ab)^{-1}$ with $z=x/a$. It has two solutions when the absolute trace on the right is zero and none otherwise. The two exceptional inputs each give $b=1/a$. Hence

$$
NT_{ab}=1+\psi((ab)^{-1})+2\mathbf1_{ab=1}.
$$

Multiply by the same kernel and sum over the intermediate nonzero field element $c$. The constant and character terms alone contribute $N-1-2+\sum_{c\ne0}\psi((a^{-1}+b^{-1})/c)$, which is $N-4+N\mathbf1_{a=b}$. The cross terms with one exceptional input contribute $4+2\psi(b/a)+2\psi(a/b)$, and the term with two contributes $4\mathbf1_{a=b}$. For $r=b/a$ this gives

$$
N^2(T^2)_{ab}=N+(N+4)\mathbf1_{r=1}+2\psi(r)+2\psi(1/r).
$$

For even $n$, the diagonal is $2/N+8/N^2$. The printed sum in Case 1 of Liu, Tessaro and Vaikuntanathan's Theorem A.1 substitutes $N-2$ for the $N/2-2$ ordinary nonzero contributions counted in the preceding sentence. Using their count gives the diagonal above and preserves their stated upper bound. [Liu, Tessaro and Vaikuntanathan, p. 43](https://eprint.iacr.org/2021/507.pdf)

The diagonal always exceeds the uniform mass. Off the diagonal, only ratios with both traces zero exceed it. Let $\mathcal K=\sum_{r\ne0}\psi(r+r^{-1})$. The number of nonzero elements with both traces zero is $\sum_{r\ne0}(1+\psi(r))(1+\psi(1/r))/4=(N-3+\mathcal K)/4$. Remove $r=1$ when $n$ is even and denote the resulting count by $A$. Summing the excess mass in a row gives

$$
d_2=\frac{2N+4+4(-1)^n}{N^2}-\frac1{N-1}
+A\left(\frac{N+4}{N^2}-\frac1{N-1}\right).
$$

The binary Kloosterman estimate $|\mathcal K|\le2\sqrt N$ gives $A=N/4+O(\sqrt N)$ and hence $d_2=7/(4N)+O(N^{-3/2})$. One also gets the finite bound **$d_2\le 2/N$ for every $n\ge3$**. Indeed the diagonal excess multiplied by $N$ is at most $1+7/N$, the off-diagonal excess multiplied by $N$ is at most $3/N$ per positive term, and $A\le (N+2\sqrt N)/4$. Thus $Nd_2\le 7/4+7/N+3/(2\sqrt N)<2$ for $N\ge128$. For $n=3,4,5,6$ the exact distances are respectively $3/28,9/80,235/3968,841/32256$. The rate probe verifies the full two-step identity and the resulting distances by independent field arithmetic from two through eight bits. At two bits the exact distance is $2/3$. [Bojilov, Borissov and Borissov](https://arxiv.org/abs/1711.08306), [Conrad, *Kloosterman Sums in Characteristic Two*](https://kconrad.math.uconn.edu/articles/kloosterman.pdf)
