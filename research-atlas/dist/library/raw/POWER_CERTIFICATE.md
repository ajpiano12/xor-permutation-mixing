# Small-error pairwise bounds for field powers

On 128 bits the fixed permutation $P(x)=x^7$ over $\mathbb F_{2^{128}}$ brings **every ordered pair within $2^{-128}$ of uniform in at most five cipher rounds**. This bound even tolerates changing up to $2^{62}$ entries, provided the new table is a permutation. For the patched inverse on the same width, **exactly four rounds** are necessary and sufficient at this threshold. Both conclusions use fresh independent shared XOR keys and the same public permutation each round.

| Public permutation | Bits | Type of result | Rounds at $2^{-32}$ | At $2^{-64}$ | At $2^{-128}$ |
| --- | ---: | --- | ---: | ---: | ---: |
| $x^7$, up to $2^{62}$ changed entries | 128 | Sufficient | 3 | 4 | 5 |
| Patched inverse | 128 | Sufficient, last column exact | 3 | 3 | 4 |
| $x^7$ | 8 | Exact | 15 | 28 | 56 |
| Patched inverse | 8 | Exact | 10 | 19 | 35 |

The eight-bit rows illustrate why block width matters when setting an absolute error target. The computations at that width iterate exact integer counts. The large-width bounds come from the formula for $P$ and require no enumeration. The verifier also accepts an explicit table and checks its distance from the specified power in the supplied polynomial basis. [Verifier and exact calculator](../power_mixing.py)

```sh
uv run --locked power_mixing.py bound --bits 128 --power 7 --security 32 64 128
uv run --locked power_mixing.py exact --modulus 0x11b --power 7 --security 32 64 128
uv run --locked power_mixing.py verify --modulus 0x11b --power 7 --file permutation.txt
```

## A single derivative row gives the complete pair walk

Let $N=2^n$, $m=N-1$, and let $P(0)=0$, $P(x)=x^d$ on the multiplicative group, with $\gcd(d,m)=1$. For a uniform field element $U$ define $Z=P(U+1)+P(U)$. If a pair has difference $a\ne0$, its next difference has the law of $a^d Z$. This follows by writing the uniform first argument as $aU$. The fresh $Z$ is independent of past differences. From start $a$, after $s$ difference steps the result is distributed as

$$ a^{d^s} \prod_{j=0}^{s-1} Z_j^{d^j}, $$

with $Z_j$ independent copies. All starts have the same distance to uniform. Taking logs in the cyclic group gives an affine random walk. For its nontrivial multiplicative characters $\chi$ write $w(\chi)=\mathbb E\chi(Z)$. If $T$ is the difference kernel on nonzero states, then $T\chi=w(\chi)\chi^d$. Since the character indices are permuted by $d$, the operator norm on the mean-zero subspace is exactly $\rho=\max_{\chi\ne1}|w(\chi)|$. Parseval also gives exact chi-squared distance $\sum_{\chi\ne1}\prod_{j=0}^{s-1}|w(\chi^{d^j})|^2$. Thus the full cipher satisfies

$$d_2(1+s)\le\tfrac12\sqrt{N-2}\,\rho^s.$$

Here $d_2(r)$ is worst-start **pair** TV after $r$ full rounds. The last uniform key randomizes the first coordinate of the pair and the last fixed permutation preserves TV. [Pair-to-difference reduction](../README.md#calculation) · [Power-function differential spectra](https://users.ics.aalto.fi/blondeau/PDF/WCC2013.pdf) · [Affine random walks on cyclic groups](https://doi.org/10.4213/sm9811e)

## A checkable condition from low signed degree

For a positive odd exponent $e>1$ let $F_e(x)=(x+1)^e+x^e$. It has degree $e-1$ and exactly $e-1$ simple roots over the algebraic closure. Indeed $x=0,1$ are excluded, and $(x+1)/x$ gives a bijection from the roots to the nonidentity $e$th roots of unity, all distinct in characteristic two. Hence for any nontrivial character of order $k$ this polynomial cannot be a constant multiple of a $k$th power. The multiplicative Weil bound gives $|w(\chi)|\le(e-2)/\sqrt N$. The noise of the actual permutation has no zero values. [Weil bound, Theorem 3.7](https://people.cs.uchicago.edu/~laci/papers/span1.pdf)

For the negative odd exponent $-e$, with zero patched to zero, use $F_e(x)/(x(x+1))^e$ away from $0,1$, taking $F_1=1$. Inside a character of order $k$, replace the denominator by multiplication by $(x(x+1))^{k-(e\bmod k)}$. Since $e$ is coprime to $m$, both introduced roots have multiplicity coprime to $k$. They are disjoint from the numerator roots. There are $e+1$ distinct roots, including when $e=1$. The character bound is $e\sqrt N$ for the unnormalized sum, and restoring the two patched inputs costs at most two more. Thus $\rho\le e/\sqrt N+2/N$.

Multiplying the exponent by a power of two amounts to an additive Frobenius change of output coordinates. Replacing $P$ by its inverse transposes $T$ by exchanging input and output pairs in the difference counts. Both operations preserve the norm. The verifier takes the best signed degree among these equivalent representations.

If a supplied permutation differs from the certified power in at most $h$ table entries, its one-step difference row changes in TV by at most $2h/N$. Either of the two translated inputs must hit a changed entry for a discrepancy. The inverse tables also differ in exactly $h$ entries, so the same inequality holds for columns. The maximal absolute row sum and column sum of the **difference of the kernels** are both at most $4h/N$. Their geometric mean bounds the Euclidean operator norm. The new table therefore satisfies the same round guarantee with $\rho+4h/N$ whenever this is below one. This applies to a supplied valid table even when its altered values destroy the power symmetry.

For $N=2^{128}$, $7$ is coprime to $N-1$, and $h\le 2^{62}$ gives $\rho+4h/N\le6/2^{64}$. Four difference steps give worst-case TV less than $2^{-128}$, hence five cipher rounds suffice. In compact mode the program checks the exponent condition with integer arithmetic. An externally supplied bound on $h$ is an assumption in this mode. The table mode verifies $h$ by enumeration.

## Exactly four inverse rounds at error $1/N$

Take even $n\ge6$. In the patched-inverse two-step formula the probability to return to a starting difference is $(2N+8)/N^2$. Its excess above $1/(N-1)$ already exceeds $1/N$. Thus three cipher rounds miss the target. Three difference steps, or four cipher rounds, give

$$d_2(4)\le \frac{\sqrt{1-2/N}}{2N}(1+2/\sqrt N)^3\le 1/N,$$

since $N\ge64$. This proves minimality, including the 128-bit row. The inverse is a published benchmark; the calculation builds on the case analysis in the paper named in the assignment. [Two-step formula](RATES_AND_LITERATURE.md#the-patched-inverse-has-an-exact-two-step-distance) · [Liu, Tessaro and Vaikuntanathan, Appendix A](https://eprint.iacr.org/2021/507.pdf)

## Exact and fallback calculations

The exact program forms one histogram in discrete-log coordinates, giving one vote per unordered pair $\{x,x+1\}$. To advance a row it permutes its indices by $d$ and cyclically convolves with the histogram. After $s$ steps the common denominator is $(N/2)^s$. With integer counts $c_j$ and denominator $D$, the test for TV $\le2^{-k}$ is $2^k\sum_j|m c_j-D|\le2mD$. Packing the coefficients into nonoverlapping base-$256$ digit groups reduces each cyclic convolution to one integer multiplication and a wraparound addition. Only $O(N)$ counts are stored. Their bit length grows with the number of rounds.

The support of $Z$ contains $1$. Its discrete logs generate the entire cyclic group precisely when their gcd with $m$ is one. Otherwise the walk from $1$ stays in a proper subgroup. When the gcd is one, every nontrivial character sees at least two different phases and hence has $|w(\chi)|<1$. This decides convergence without a dense matrix. For nonlinear permutation powers the full-group case also follows from Lenstra’s character-preserver theorem: if a quotient by a proper noise subgroup existed, $P$ would induce exponentiation by $d$ on the quotient of every nonzero difference, forcing a semilinear affine map. Here $P(0)=0,P(1)=1$, so it would be Frobenius. Stafford’s group theorem gives an independent route covering higher orders. [Lenstra, Theorem 3](https://www.math.leidenuniv.nl/~lenstrahw/PUBLICATIONS/1990a/art.pdf) · [Stafford, 1998](https://doi.org/10.1006/ffta.1998.0224)

This yields a coarse guarantee even if the Weil estimate exceeds one. Two distinct phases each have mass at least $2/N$. Removing this mass from each and applying the triangle inequality gives $|w(\chi)|\le1-(4/N)(1-\cos(\pi/m))\le1-8/(Nm^2)$. The last step uses $\sin v\ge2v/\pi$ on $[0,\pi/2]$. The compact calculator uses this fallback for unmodified nonlinear powers. For Frobenius powers, every derivative is deterministic and pairs fail to mix for $n\ge2$.

**Attribution.** The homogeneity of power derivatives, Fourier analysis of affine cyclic walks, character estimates, and the semilinear/group classifications are published. The pairwise formulas and round certificates here are applications of those results to one repeated public permutation. The exact finite measurements are project computations. Publication priority for the quantitative specialization and perturbation guarantee remains unverified.
