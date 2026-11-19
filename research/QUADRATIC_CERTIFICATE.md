# A finite round certificate for quadratic permutations

Problem 4 asks for an efficiently checkable condition on one public permutation and a round count for a prescribed error. There is a concrete pairwise answer for **quadratic almost perfect nonlinear (APN) permutations**. Given their $N=2^n$ table entries, one can check the certificate using $O(Nn^2)$ operations on $n$-bit words and $O(N)$ words of memory. For every certified table, the worst ordered-pair TV distance after $r\ge1$ cipher rounds satisfies

$$d(r)\le \tfrac12\sqrt{(N-2)/N^{r-1}}.$$

For example, a certified five-bit table needs at most three cipher rounds at $\epsilon=1/4$. At fixed positive error three rounds suffice for all sufficiently large certified tables. The bound continues to decrease geometrically for smaller thresholds. Failure to qualify leaves the mixing question open for this test. [Certificate implementation](../quadratic_mixing.py)

## A bound for every APN permutation

For any APN permutation every nonzero derivative output occurs twice whenever it occurs. Hence every row and column has exactly $N/2$ nonzero entries, of value $2/N$, among the $N-1$ states. For any $a,b$, the support of row $a$ intersects the support of column $b$. Therefore $(T^2)_{ab}\ge4/N^2$. This proves eventual pairwise mixing for every APN permutation, including any with nonquadratic coordinate functions. Writing $T^2=\alpha U+(1-\alpha)S$ gives a uniform component of mass $\alpha=4(N-1)/N^2$. The remaining kernel $S$ is doubly stochastic, giving worst-start TV at most $(1-\alpha)^j$ after $2j$ difference rounds. O’Connor’s 1995 paper formulates APN ergodicity as an assumption in Proposition 2.1, checks it at three bits, and uses the same intersection principle for the row Gram matrix in §3.1. This positivity argument applies it directly to a row and a column of $T$. [O’Connor, full paper](https://link.springer.com/content/pdf/10.1007%2F3-540-49264-X_2.pdf)

## Why the rank test works

The binary Möbius transform recovers the vector-valued algebraic normal form of $P$. Check that every coefficient of degree greater than two vanishes. Then $D_aP(x)=P(x+a)+P(x)$ is affine for every $a\ne0$. Evaluate its linear part on the $n$ basis vectors. Rank $n-1$ means its image has size $N/2$ and each image has precisely two preimages. Zero is absent since $P$ is a permutation. The image is thus $\{b:m_a\cdot b=1\}$ for a unique nonzero mask $m_a$. This derivative geometry is the established crooked-function property. [Bending and Fon-Der-Flaass](https://doi.org/10.37236/1372)

## Exact chi-squared distance

The difference matrix $T$ is doubly stochastic. Its rows put mass $2/N$ at each point of their respective hyperplanes. Every mask occurs exactly once. Indeed, if $c(m)$ counts occurrences including $c(0)=0$, then $\sum_m c(m)=N-1$ and $\sum_{m:m\cdot b=1}c(m)=N/2$ for every $b\ne0$ by column balance. The Walsh transform of $c$ is $N-1$ at zero and $-1$ elsewhere. Inversion gives $c(m)=1$ for every nonzero mask.

Different rows meet in $N/4$ entries for $n\ge2$. Thus $TT^\mathsf{T}$ has entries $2/N$ on the diagonal and $1/N$ off it. With $U$ the uniform matrix on $N-1$ differences, $(T-U)(T-U)^\mathsf{T}=(I-U)/N$. On zero-sum row vectors, multiplication by $T$ scales the Euclidean norm by exactly $N^{-1/2}$. A point mass initially has chi-squared distance $N-2$ from uniform. After $s$ difference rounds its chi-squared distance is exactly $(N-2)N^{-s}$ for every start. Cauchy–Schwarz gives the TV bound with $s=r-1$. The one-bit case has only one nonzero difference and is already exact.

## Explicit tables

For odd $n$ and $\gcd(k,n)=1$, the Gold power $P(x)=x^{2^k+1}$ on $\mathbb F_{2^n}$ is a permutation. A common divisor of $2^k+1$ and $2^n-1$ divides $2^{\gcd(2k,n)}-1=1$. This power is quadratic over the bits. Setting $x=az$ expresses the derivative as $a^{2^k+1}(1+z^{2^k}+z)$. The kernel of $z\mapsto z^{2^k}+z$ is the two-element field, giving the required rank. Cubing is the case $k=1$. The example below is cubing on three bits using $X^3+X+1$.

```sh
uv run --locked quadratic_mixing.py --epsilon 1/4 0 1 3 4 5 6 7 2
```

**Attribution.** The hyperplane structure and these power functions are published. Liu, Tessaro and Vaikuntanathan analyze cubing and its differential geometry. O’Connor uses the Gram matrix for APN maps and gives the three-bit inverse example explicitly. The Gram calculation above is presented as a corollary of incidence geometry. Priority for this exact formulation and the all-round chi-squared expression remains unverified. [Liu et al., Lemma 3.3](https://eprint.iacr.org/2021/507.pdf) · [O’Connor, EUROCRYPT 1995](https://doi.org/10.1007/3-540-49264-X_2)
