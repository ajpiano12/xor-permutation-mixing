# How many rounds does the rotating update need?

For the same 128-bit inverse construction with a 16-bit update, **10 rounds are necessary and 36 suffice** for the worst ordered quadruple at total variation (TV) distance $2^{-128}$. The previous two-sweep analysis certified 81 rounds. The upper bound of 36 also holds for every degree-15 control polynomial with the same geometry. All statements assume fresh independent uniform XOR keys shared by the inputs. [Definitions and 10-round lower bound](SPECTRAL_CERTIFICATE.md) · [Polynomial construction](POLYNOMIAL_UPDATE.md)

| Word bits | Updated bits | Control | Inputs | Rounds for $2^{-32}$ | Rounds for $2^{-64}$ | Rounds for $2^{-128}$ |
| ---: | ---: | --- | ---: | ---: | ---: | ---: |
| 128 | 16 | inverse | 3 | 12 | 22 | 34 |
| 128 | 16 | inverse | 4 | 19 | 25 | 36 |
| 128 | 16 | any degree-15 polynomial | 4 | 19 | 25 | 36 |
| 128 | 12 | any degree-15 polynomial | 4 | 15 | 29 | 57 |
| 128 | 8 | inverse | 8 | 39 | 53 | 73 |

The table takes the better of two sufficient bounds below for each threshold. Changing the update width changes the permutation. The verifier returns both bounds separately. [Underlying calculations](sweep_bounds.py) · [Verifier](spectral_certificate.py)

```sh
uv run --locked python -m research.spectral_certificate --bits 128 --block-bits 16 --order 4 --modulus 0x10000000000000000000000000039 --sweep-analysis
```

## What a single update can retain

Write $N=2^n$, $B=2^b$, $Q=N/B$, $d=\lceil n/b\rceil$ and $p=\binom t2$. In a rotating frame each layer updates one window of $b$ bits. A sweep of $d$ windows covers the word. An ideal layer chooses a fresh independent uniform offset for each distinct control (the other $n-b$ bits). The actual layer applies $f(z+u)$ to each control $z$ with one common uniform $u$. Let $\beta$ bound every nontrivial parity of *relative* offsets on at most $s=\min(t,Q)$ distinct controls. For the inverse one can use $[2(s-1)\sqrt Q+s+1]/Q$. For a degree-15 control polynomial at $t\le4$ one can use $12/\sqrt Q$. Write $\beta_2$ for the corresponding pair bound. The public cipher after $r$ rounds has exactly the TV distance of its relative differences after $r-1$ such layers. [Character estimates and final-mask identity](SPECTRAL_CERTIFICATE.md) · [Degree-15 bound](POLYNOMIAL_UPDATE.md)

## A short warmup before one sweep

Track a pair in an ideal layer. If both controls agree, its nonzero window difference stays fixed. Otherwise the written difference is uniform among $B$ possibilities. Thus, conditional on any history, a write is zero with probability at most $1/B$. To collide on the next control, the pair must agree on each of the previous $m$ written windows, provided those windows and the new window are mutually disjoint. Their successive writes must all have been zero, an event of probability at most $B^{-m}$. This reasoning applies up to $m=c=\lfloor n/b\rfloor-1$ even when the last window of a sweep overlaps the first.

Use $k$ warmup layers and then one full sweep. During the final $d$ layers, couple the ideal process to a process that always uses independent offsets for each label. The latter process ends with independent uniform words. The coupling agrees until two labels share a control. The ideal process is distinct-valued, so conditioning the independent target on distinctness decreases TV. A union bound gives
$$ e_k=p\sum_{j=0}^{d-1}B^{-\min(k+j,c)}. $$

At every history, relative writes in the real layer have chi-squared divergence at most $v=(B^{s-1}-1)\beta^2$ from the ideal writes, by Parseval. Thus the second moment of their likelihood ratio is at most $1+v$. Multiplying the successive likelihood ratios and conditioning step by step gives a path second moment at most $(1+v)^{d+k}$. TV of the endpoint is at most half the square root of the resulting chi-squared divergence. If a supplied permutation table differs from the specified construction at $h$ entries, successive coupling contributes at most $(d+k)th/N$. Therefore a block of $d+k$ difference layers has worst row TV at most
$$ \delta_k=e_k+\tfrac12\sqrt{(1+v)^{d+k}-1}+(d+k)th/N. $$

A kernel with worst row TV $\delta_k$ from stationarity contracts signed zero-mass measures in TV by at most $2\delta_k$. A sequence of blocks yields TV at most $\tfrac12\prod_i(2\delta_{k_i})$. The program compares products for different warmup lengths by dynamic programming with upward rounding. At 128 bits, 16-bit updates and four inputs, five ten-layer blocks plus the final full mask give **51 rounds** for either control family. The next argument exploits more information about which starting tuples retain a difference.

## A sweep as an operator

Assume $b$ divides $n$ and use the specified permutation ($h=0$). Every coordinate is then written exactly once per sweep. Work on full ordered distinct tuples with uniform law $U$. In the real translated layers, add an independent uniform *common* $b$-bit offset to the updated window. This leaves the one-step transition on differences unchanged. Earlier common shifts only translate the input to the next uniform mask. Each lifted layer is a mixture of bijections on the entire word, so $U$ is stationary. Upper bounds on its full-tuple TV give upper bounds on difference TV by projection.

Let $I_j$ and $M_j$ denote the ideal and lifted real kernels for one window. Fix the controls of the tuple and all within-control differences. If there are $l$ distinct controls, the remaining degrees of freedom are one anchor window value per control, forming the additive group of $l$ blocks. The real update is convolution on this group. The ideal update averages uniformly. Fourier characters are an orthonormal eigenbasis for the difference of these two kernels. Characters sensitive to a common offset have zero mean in both processes. For the remaining nonconstant characters the real expectation is at most $\beta$ in absolute value. Hence $\lVert M_j-I_j\rVert_{2\to2}\le\beta$ on each fiber and on their disjoint union with uniform measure. Telescoping the product over one sweep costs at most $d\beta$, because all kernels are contractions in $L^2(U)$.

Let $K$ be one complete ideal sweep and $J$ projection to uniform. A starting tuple $x$ and ending tuple $y$ specify all the intermediate states: at every step, read the processed prefix from $y$ and the remaining suffix from $x$. For a compatible path let $l_j$ be the number of distinct controls at step $j$, and put $D=\sum_{j=1}^d(t-l_j)$. Its ideal transition probability is $B^{-dt+D}$. Thus $K(x,y)/U(y)\le B^D$ since $(N)_t\le N^t$.

Make a graph on the $t$ labels, joining pairs that collide on some control during this sweep. Two labels in the same control group have distinct window values. They retain this nonzero difference, so they can collide at most once in a sweep of disjoint windows. Each group of $m$ labels accounts for $m-1$ units of $D$ and $\binom m2$ pair collisions. Hence $D$ is at most the graph's number of edges. A graph of rank $v$ (number of vertices minus number of connected components) has at most $\binom{v+1}2$ edges.

Draw $X$ from $U$, independently of all the random switch tables. Fix the switch tables for the sweep. To realize any prescribed set of $v$ forest edges with specified collision times, expose the starting labels along the forest from its roots. When adding a child, its parent position at the specified time fixes the required control. The maps from starting words to words at that time are bijective. The child's starting word is uniform among at least $N-t+1$ unused words, and at most $B-1$ of them can match its parent's control. Union over at most $\binom pv$ forests and $d^v$ time choices. Since a rank-$v$ graph contains such a forest,
$$
S=\sum_{v=1}^{t-1}\binom pv
\left(\frac{d(B-1)}{N-t+1}\right)^v B^{\binom{v+1}{2}}
\quad\text{bounds}\quad \mathbb E[B^D-1].
$$
The squared Hilbert–Schmidt norm of $K-J$ is $\mathbb E[K(X,Y)/U(Y)]-1$ for $X\sim U,\ Y\sim K(X,\cdot)$. Therefore $\lVert K-J\rVert_{2\to2}\le\sqrt S$. The lifted real sweep contracts mean-zero $L^2(U)$ by at most $\sigma=\sqrt S+d\beta$. The adjoint has the same norm, which is the direction required for evolving densities.

## From a fixed starting tuple

For one actual lifted sweep, a compatible path has density relative to $U$ at most $A B^D$ with $A=[1+(B^{t-1}-1)\beta]^d$. To see this, Fourier inversion on the $l_j-1$ relative offsets bounds the probability of any particular relative write by $[1+(B^{l_j-1}-1)\beta]/B^{l_j-1}$. The extra common offset supplies the independent uniform absolute anchor. Multiplying over the unique path gives the claim.

There is a useful deterministic bound on $D$. Choose one of the $t$ labels uniformly and follow its written prefix. The increase in prefix entropy at step $j$ is the entropy of the new window conditioned on the old prefix. Conditioning further on the control (old prefix and unwritten suffix) can only decrease that entropy. Within a control class of size $m$, all $m$ new window values are distinct, giving $\log_2 m$ bits. Since $m\log_2 m\ge2(m-1)$ for integer $m\ge1$, the total increase that step is at least $2(t-l_j)/t$. The final prefix has entropy $\log_2 t$. Thus $D\le E=\lfloor t\log_2(t)/2\rfloor$. If only the first window collides then $D\le t-1$.

For real writes the chance that a particular pair writes zero, conditional on any past, is at most $a=1/B+(1-1/B)\beta_2$ by single-window Fourier inversion. A forced pair has probability zero of writing zero. After $k$ warmup layers the first window of the full sweep has some control collision with probability at most $p_0=\min(1,p a^k)$, for $0\le k\le d-1$. The chance of a later collision in that sweep is at most $p_1=\min(1,p\sum_{j=1}^{d-1} a^{\min(k+j,d-1)})$. Conditioning on the state at the end of the warmup, the chi-squared divergence plus one of the sweep's output equals the expected transition density relative to $U$. Convexity of divergence permits averaging that estimate over the warmup. Classifying paths by the first or a later collision gives
$$
H=A\min\{B^E,1+(B^{t-1}-1)p_0+(B^E-1)p_1\}-1
$$
as an upper bound on chi-squared divergence after the first $k+d$ layers. After another $m$ sweeps, TV is at most $\tfrac12\sqrt H\,\sigma^m$, at $1+k+d+md$ cipher rounds.

For the 128-bit inverse with $b=16,t=4$, the stationary contraction satisfies $\sigma<2.53\times10^{-14}$. With $k=3$, three further sweeps give TV below $2^{-134}$. The degree-15 bound gives TV below $2^{-134}$ with the same schedule. These are sufficient guarantees for every initial quadruple. They do not determine its exact mixing time.

Morris, Rogaway and Stegers analyze ordered inputs under the independent-switch Thorp shuffle. Gelman and Ta-Shma prove a bound for unordered sets under the Beneš switching network. The local character estimates used here also have published sources. The warmup estimate, forest count and application of the sweep norm to these explicit permutations are project derivations. Publication priority for their combination remains unverified. [Thorp shuffle](https://www.cs.ucdavis.edu/~rogaway/papers/thorp.pdf) · [Beneš network](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.FSTTCS.2014.327) · [Construction and prior work](SPECTRAL_CERTIFICATE.md) · [Literature review](LITERATURE_REVIEW.md)
