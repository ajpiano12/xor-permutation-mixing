# How an almost affine permutation can mix slowly

On 128 bits, multiplying by a fixed primitive field element after swapping the inputs 0 and 1 yields a permutation that **eventually mixes every pair**. At worst-start total variation $2^{-128}$, its required number of full rounds is between $7.48\times 10^{39}$ and $7.83\times 10^{39}$. A table with very similar outputs to an affine map admits a general, one-sided certificate of slow mixing. The certificate uses $O(n2^n)$ word operations and $O(2^n)$ words, without building the difference matrix. [Implementation](round_bounds.py)

## A screen for supplied tables

Let $N=2^n\ge4$, $m=N-1$ and $T$ be the row-stochastic matrix on nonzero XOR differences. Its columns also sum to one. For uniform input differences and uniform base points, both an input pair and its image under a permutation are uniform ordered distinct pairs. Write $J$ for the $m\times m$ uniform matrix. The worst pair TV after $1+k$ full rounds is $d(k)=\|T^k-J\|_\infty/2$, where the norm is the largest absolute row sum. A final common uniform XOR chooses the first point uniformly inside each difference class, and the final public permutation preserves distance. Every higher-order worst TV is at least the pair TV by projection.

Suppose $P$ disagrees with an affine bijection $A(x)=Lx+c$ on $h<N/4$ inputs. For any input difference $a$, the two points avoid all disagreements except with probability at most $2h/N$. Thus $T(a,La)\ge 1-2h/N$. Let $\Pi$ be the permutation matrix for $a\mapsto La$. When $h>0$ we can write $T=(1-2h/N)\Pi+(2h/N)S$ for a doubly stochastic matrix $S$. Jensen's inequality gives $\|Sv\|_2\le\|v\|_2$. The reverse triangle inequality gives $\|Tv\|_2\ge (1-4h/N)\|v\|_2$. Hence even the smallest modulus of an eigenvalue of $T$ on the mean-zero subspace is at least $1-4h/N$. The spectral radius of $T^k-J$ is a lower bound for its infinity norm, proving

$$d(k)\ge \tfrac12(1-4h/N)^k.$$

If $h=0$, the differences evolve deterministically and $d(k)=1-1/m$ forever. To find a close affine map, take the most frequent value of $P(x)\oplus P(x+e_i)$ for each standard basis vector $e_i$. The inequality above makes $Le_i$ the unique majority if a map within the strict radius exists. Reconstruct $L$, take the most frequent $P(x)\oplus Lx$ as the offset, and count disagreements exactly. A map within this radius automatically has full rank since an image of size at most $N/2$ can match a permutation on at most $N/2$ inputs. If the test finds nothing, some other mechanism can still cause slow mixing.

## An explicitly mixing family with sharp growth in the required rounds

Take an invertible binary linear map $L$ that cycles through all nonzero field elements, fix $s\ne0$, and use $P=L\circ(0\ s)$, where $(0\ s)$ swaps just two inputs. For each $a\ne s$, the two-point derivative equals $L(a+s)$ with probability $p=4/N$ and equals $La$ otherwise. Exactly four base points $0,s,a,a+s$ give the exceptional transition. For $a=s$ the derivative is always $Ls$. Here and below $n\ge4$.

The deterministic edges $a\mapsto La$ connect all differences. There is a self-loop at $a=(I+L)^{-1}Ls$: $I+L$ is invertible since $L$ fixes no nonzero point, and this $a$ is different from both $0$ and $s$. Thus the pair walk is irreducible and aperiodic.

**Lower bound.** Before applying $L$, the difference step acts as $(1-p)I+p\Sigma_s$. The permutation $\Sigma_s$ XORs by $s$ except that it fixes $s$ on the nonzero state space. Its transpositions number $(N-2)/2$, so $|\det T|=(1-2p)^{(N-2)/2}$. Removing the stationary direction leaves $N-2$ eigenvalues with that product in modulus. At least one has modulus $\sqrt{1-2p}$ or larger. Therefore

$$ d(k)\ge\tfrac12(1-2p)^{k/2}. $$

**Upper bound.** Undo the cumulative $L$ after each transition. Over a sweep of $m=N-1$ steps the scheduled XOR directions $s_j=L^{-j}s$, $0\le j<m$, exhaust the nonzero vectors. At each step an independent coin of probability $p$ decides whether to use the scheduled direction. Suppress any resulting move to zero. After a sweep the frame agrees with the original coordinates.

First allow moves to zero as well. Starting at $a$, the endpoint is $a$ plus the sum of all selected directions. Each nontrivial binary character sees exactly $N/2$ negative directions, so its expected sign is $\alpha=(1-2p)^{N/2}$. Fourier inversion on the full binary space gives endpoint law $\alpha\delta_a+(1-\alpha)U_N$.

Couple the actual and unrestricted processes with the same coins. Their first disagreement requires a successful coin when the unrestricted pre-step state equals the currently scheduled direction. Along each sample path that equality can occur at most once between successive successful coins, because the unrestricted state stays constant and the directions are distinct. The expected number of opportunities is at most $1+mp$. Whether an opportunity arises is determined before its coin, so the probability of any disagreement is at most $p(1+mp)$. The maximum TV between two unrestricted endpoint laws is $\alpha$. The triangle inequality now bounds the maximal TV between two actual rows by $\alpha+2p(1+mp)$.

A second bound works at every width. For any unequal nonzero states $a,b$, selecting just the direction $a+b$ reaches $b$ without touching zero. Staying at $a$ requires no successes, an event at least as probable. Thus every entry of $T^m$ is at least $p(1-p)^{m-1}$. Subtracting this common mass across the $m$ states gives the second contraction factor below. Applying the best factor repeatedly gives

$$d(jm)\le(1-1/m)\gamma_N^j,\qquad
\gamma_N=\min\{\alpha+2p(1+mp),\;1-mp(1-p)^{m-1}\}.$$

The contraction step uses the usual coupling bound for a Markov kernel whose rows are pairwise within a specified TV distance. As $N$ grows, $\gamma_N=e^{-4}+O(1/N)$, while $(1-2p)^{m/2}$ in the lower bound also tends to $e^{-4}$. For $\lambda\to\infty$ and $n\to\infty$, solving both inequalities gives the same leading term for the worst pair mixing time at TV $2^{-\lambda}$,

$$\tau_2(2^{-\lambda})\sim \frac{\ln 2}{4}\,2^n\lambda.$$

Rounding the upper bound up to a full sweep costs at most $N-1$ steps. This yields $\Theta(2^n)$ at each fixed threshold below $1/2$, and taking $\lambda=n$ gives the sharp leading asymptotic at the small-error benchmark.

## The same leading term holds at every fixed tuple order

Undo the linear rotation and the common XOR after each round. The rule for moving **points**, including three or more at once, is particularly simple. In each scheduled direction $s_j$, choose one edge uniformly from the perfect matching $\{\{x,x+s_j\}\}$ and swap its endpoints. This follows by conjugating $(0\ s)$ by a uniform translation. The masks stay independent across rounds, and the final independent mask converts the difference law to the full tuple law with the usual extra round. [Derivation of the moving coordinates](SPECTRAL_CERTIFICATE.md#independent-translated-updates-from-the-original-keys)

Fix $t\ge2$, put $q=2/N$ and suppose $tq\le1$. In a comparison walk each of the $t$ labels independently takes direction $s_j$ with probability $q$. If their occupied edges are all distinct, the actual indicators select any particular label with probability $q$ and select none otherwise. Their TV from the independent indicators is at most $tq[1-(1-q)^{t-1}]\le t(t-1)q^2$, since only the singleton probabilities are larger in the actual law. If $r$ pairs of labels occupy the same edge, their indicators instead move together with probability $q$. Replacing the two separate singleton events by one joint event and one no-move event costs $2q$ per such pair in TV.

During a sweep, each particular pair can occupy the scheduled edge at most once between moves of either label, since the pre-step difference stays fixed and every direction occurs once. Its expected number of such opportunities is at most $1+2mq$. Couple the walks until their first disagreement and sum the conditional bounds over the actual path. From every starting tuple the probability of disagreement in a sweep is at most

$$D=m t(t-1)q^2+2q\binom{t}{2}(1+2mq)=t(t-1)q(1+3mq).$$

Over $J$ sweeps the comparison cost is at most $JD$. For the independent walk, each label retains its initial value with probability $u=(1-2q)^{NJ/2}$ and otherwise takes a uniformly random value on the full space. The labels use independent randomness. Whenever at most one label is retained, the $t-1$ relative XOR differences are jointly uniform on the unrestricted difference space: even an anchored label leaves a free uniform coordinate for each difference. This common part is the same for every initial tuple. Consequently the maximal TV between two independent-walk difference rows is at most $\binom{t}{2}u^2$. The actual kernel on differences among distinct labels therefore contracts TV in $J$ sweeps by at most

$$\binom{t}{2}(1-4/N)^{NJ}+2JD.$$

At fixed $t,J$, this tends to $\binom{t}{2}e^{-4J}$ as $N$ grows. Choose a fixed $J$ large enough to give contraction. Repeated blocks yield a limsup for $\tau_t(2^{-\lambda})/(N\lambda)$ of at most $J\ln 2/(4J-\ln\binom{t}{2})$ as $n,\lambda\to\infty$. Letting $J$ grow and using the pair marginal lower bound proves the leading term $(\ln2/4)N\lambda$ for every **fixed** $t$. For the concrete 128-bit permutation, four-input mixing at TV $2^{-128}$ requires more than $7.48\times10^{39}$ rounds and takes fewer than $8.17\times10^{39}$ rounds. This compares directly with fast four-input constructions at the same width and error.

## Finite checks

These are full cipher rounds for **pairs** at TV $2^{-128}$. The upper column uses only the proof above. At four and five bits, direct integer iteration independently gives the exact crossing. For the four-, five- and 128-bit examples take $L$ to be multiplication by $X$ in the polynomial basis with moduli $X^4+X+1$, $X^5+X^2+1$ and $X^{128}+X^7+X^2+X+1$ respectively, and $s=1$. In each case $X$ has multiplicative order $2^n-1$. The bounds apply to every choice of primitive multiplier and nonzero $s$.

| Bits | Necessary rounds | Exact, when computed | Sufficient rounds |
| ---: | ---: | ---: | ---: |
| 4 | 255 | 266 | 19,231 |
| 5 | 613 | 626 | 37,604 |
| 8 | 5,547 | | 13,006 |
| 16 | 1,442,192 | | 1,507,306 |
| 128 | $>7.48\times 10^{39}$ | | $<7.83\times 10^{39}$ |

The verifier evaluates powers with outward-rounded binary fixed-point arithmetic. The first command uses only $n$ and $\lambda$ for this family. The second evaluates the higher-order bound. The third takes an arbitrary input table and returns a necessary round count if it finds an affine witness.

```sh
uv run --locked python -m research.round_bounds family --bits 128 --error-bits 128
uv run --locked python -m research.round_bounds family --bits 128 --order 4 --error-bits 128
uv run --locked python -m research.round_bounds table --error-bits 128 2 0 4 6 8 10 12 14 3 1 7 5 11 9 15 13
```

**Prior work.** Recovering a nearly linear function from its pairwise derivatives is a classical self-correction idea. Fourier analysis of a linear shift register with additive noise has established precedents. The present calculation uses rare moves of probability $4/N$ and suppresses transitions to zero as dictated by the permutation derivative. The affine screen, finite bounds and leading constant for this family are project derivations. Their publication priority is unverified. [Blum, Luby and Rubinfeld, self-correction](https://www.sciencedirect.com/science/article/pii/002200009390044W) · [Levin and Tankala, randomized shift-register walk](https://arxiv.org/abs/2109.05387) · [Liu, Tessaro and Vaikuntanathan, pair difference walk](https://eprint.iacr.org/2021/507)

Jain et al. already prove an exponential-in-width four-input obstruction for repeated whole-field inversion. The construction here is a different explicitly specified permutation whose pair and higher-order slowdown can be quantified. [Jain et al., inverse walk](https://eprint.iacr.org/2024/1795)
