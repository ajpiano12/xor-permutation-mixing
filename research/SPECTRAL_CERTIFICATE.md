# One fixed permutation for three, four and more inputs at small error

On 128 bits, one explicit permutation sends **every ordered quadruple** within $2^{-128}$ of uniform after **81 cipher rounds**. The same permutation gives **65 rounds for triples**. Its worst-start quadruple mixing time at this threshold is at least **10 rounds**. Changing the update width gives **61 rounds for triples** or **191 rounds for eight inputs**. Each construction uses one fixed public permutation and independent uniform XOR keys, as in Problem 4.

| Bits $n$ | Updated bits $b$ | Tuple order $t$ | Rounds for $2^{-32}$ | Rounds for $2^{-64}$ | Rounds for $2^{-128}$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 64 | 8 | 3 | 49 | 81 | 161 |
| 128 | 16 | 3 | 17 | 33 | 65 |
| 128 | 22 | 3 | 25 | 37 | 61 |
| 128 | 16 | 4 | 33 | 49 | 81 |
| 128 | 8 | 8 | 65 | 97 | 193 |
| 128 | 7 | 8 | 77 | 115 | 191 |
| 256 | 32 | 4 | 17 | 33 | 49 |

The table lists sufficient round counts for the inverse update. At $n=128$ and error $2^{-128}$, checking the finite bound below for every width $1\le b\le64$ gives the smallest certified counts at $b=22,16,7$ for $t=3,4,8$ respectively. A width change also changes the public permutation. A polynomial update gives another compact construction for triples and quadruples. [Polynomial update](POLYNOMIAL_UPDATE.md)

For all sufficiently large $n$ and every target $2\le t\le n/2-1$, choosing the block width for that target gives **$O(t(1+\log(1/\epsilon)/n))$ rounds**. In particular, at error $2^{-n}$ the bound is $O(t)$, matching the key-count lower bound up to a constant. Each public permutation is fixed throughout its run. Its bound for $t$ also applies to all smaller orders by projection.

## Construction and verification

Take $1\le b\le n/2$, write $B=2^b$, $N=2^n$, and $Q=2^{n-b}$. Split an input into its low $b$ bits $v$ and the other bits $z$. Interpret $z$ in a specified polynomial basis of $\mathbb F_Q$. Put $I(0)=0$ and $I(z)=1/z$ elsewhere. Let $f(z)$ be the low $b$ coordinates of $I(z)$. Define $E(v,z)=(v\oplus f(z),z)$ and let $R$ rotate the entire word right by $b$ positions, moving the low block to the high end. Use the fixed public permutation $P_0=R E$. The invertible update $E$ is an unbalanced Feistel step. Any surjective binary linear projection in place of the low $b$ coordinates gives the same bound.

The verifier accepts this compact description and checks irreducibility of the field modulus in polynomial time in $n$. A generic supplied circuit still needs a witness that it implements this formula. For a table, the verifier compares every entry to $P_0$ and automatically includes the number $h$ of disagreements. The table check costs $O(N\,\mathrm{poly}(n))$. The first command verifies both large and small thresholds on the specified compact 128-bit example, whose irreducible modulus is $X^{112}+X^5+X^4+X^3+1$. Pass a table with `--file` to verify a concrete list instead. [Verifier](spectral_certificate.py)

```sh
uv run --locked python -m research.spectral_certificate --bits 128 --block-bits 16 --order 4 --modulus 0x10000000000000000000000000039 --error-bits 32 64 128
uv run --locked python -m research.spectral_certificate --bits 128 --block-bits 22 --order 3 --modulus 0x400000000000000000000000063
uv run --locked python -m research.spectral_certificate --bits 128 --block-bits 8 --order 8 --modulus 0x100000000000000000000000000001b
uv run --locked python -m research.spectral_certificate --bits 128 --block-bits 7 --order 8 --modulus 0x2000000000000000000000000000123
```

## Finite bound

Write $d=\lceil n/b\rceil$, $s=\min(t,Q)$, and take $C=B$ when $b$ divides $n$ and $C=B^2$ otherwise. Set

$$
\beta=\frac{2(s-1)\sqrt Q+s+1}{Q},\qquad
\eta=\tfrac12\sqrt{B^{s-1}-1}\,\beta,\qquad
\delta=\min\left(1,\frac{d\binom t2 C(B-1)}{N}+2d(\eta+th/N)\right).
$$

If $P$ differs from $P_0$ on $h$ inputs and $\delta<1/2$, then at $1+2dj$ cipher rounds the worst-start TV satisfies

$$d_t(1+2dj)\le\delta(2\delta)^{j-1},\qquad j\ge1.$$

The first block already gives $d_t(1+2d)\le\delta$ regardless of its size. The program rounds each square root upward to the next integer for rational arithmetic and returns the first block count meeting the requested threshold with these upper bounds.

## Independent translated updates from the original keys

Write the actual permutation as $P=R E'$, with $E'=E$ for the unmodified construction. Denote XOR by $T_a$. Starting at $F_0=G_0=\mathrm{id}$ and $A_0=0$, set $C_i=K_i\oplus A_{i-1}$, $A_i=R C_i$ and

$$G_i=R T_{C_i} E' T_{C_i}G_{i-1}.$$

Then $F_i=T_{A_i}G_i$ by induction. The masks $C_i$ are independent uniform, since each original $K_i$ is fresh given the past. The original $r$-round cipher is $F_r=P T_{C_r}G_{r-1}$, with its last mask independent of $G_{r-1}$.

For a tuple $x$, write $D(x)=(x_2\oplus x_1,\ldots,x_t\oplus x_1)$. Given $D(x)$, the fresh mask makes $T_{C_r}x$ uniform over all $N$ choices of its first point. A uniform ordered distinct tuple has the same conditional law. Summing the absolute differences over each of these equally sized sets shows that the full TV distance of $F_r$ is **exactly** the TV distance of $D(G_{r-1})$ from uniform on ordered distinct nonzero differences. The final fixed bijection $P$ preserves TV.

These differences form a Markov chain. In one layer, shifting the initial tuple by $a$ and changing $C$ to $C\oplus a$ shifts the entire output by $Ra$. The mask is uniform, so the next difference law depends only on the starting differences. This argument works for any $E'$. The ideal layer below has the same property because translating the controls only permutes the indices of its independent offsets.

With $E'=E$, conjugation translates the control $z$ by one uniform $u\in\mathbb F_Q$. The updated low block now receives $f(z+u)$, with the same $u$ across the tuple. For general $E'$, the probability of encountering one of the $h$ exceptional inputs among the $t$ translated points is at most $th/N$ per layer from any current state.

## Replacing the translated update by independent offsets

In the ideal layer each control gets an independent uniform $b$-bit offset. Suppose the tuple uses $k\le s$ distinct controls $a_1,\ldots,a_k$. The next tuple differences depend only on the $k-1$ offsets relative to the first, $f(a_i+u)\oplus f(a_1+u)$ for $2\le i\le k$. A common offset shifts every updated point by the same amount. In the ideal layer these $k-1$ relative offsets are independent uniform, including when several points use the same control. For $k=1$ both relative laws are deterministic.

Every nonzero binary parity on the relative offsets is a nonzero parity on the original $k$ offsets. Its masks on $a_2,\ldots,a_k$ are the given masks and its mask on $a_1$ is their XOR. If each such parity has bias at most $\beta$, Parseval and Cauchy–Schwarz give TV from uniform at most $\sqrt{B^{k-1}-1}\,\beta/2$. Passing from relative offsets to tuple differences contracts TV. This saves a factor of approximately $\sqrt B$ in the layer error compared with counting all $k$ offsets. [Naor and Naor](https://doi.org/10.1137/0222053)

Niederreiter and Winterhof's Theorem 1 gives the required translated-inverse character bound, including the constant and the zero convention. Their observation immediately after the proof allows arbitrary distinct shifts in the complete sum. To see its application here, nondegeneracy of the field trace pairing expresses any nontrivial parity using a nonempty set of $j\le k$ distinct controls $a_i$ and nonzero coefficients $c_i\in\mathbb F_Q$. Off those controls the parity is the absolute trace of the following rational function. [Niederreiter and Winterhof, Acta Arithmetica 93 (2000), pp. 391–392](https://matwbn.icm.edu.pl/ksiazki/aa/aa93/aa9346.pdf)
$$g(u)=\sum_{i=1}^{j}\frac{c_i}{u+a_i}.$$
Each pole is simple with nonzero residue, which also ensures the Artin–Schreier curve $y^2+y=g(u)$ is geometrically irreducible. Its smooth projective model has genus $j-1$. Each finite pole contributes one rational point, and infinity contributes two since $g(\infty)=0$. Consequently its point count equals $Q+2+\sum_{u\notin\{a_i\}}(-1)^{\operatorname{Tr}(g(u))}$. Hasse–Weil bounds its distance from $Q+1$ by $2(j-1)\sqrt Q$. Including the $j$ patched summands changes the sum by at most $j$, giving the claimed $\beta$. This uses classical arithmetic of Artin–Schreier curves. [Bucur, David, Feigon and Lalín, §2](https://mypage.concordia.ca/mathstat/cdavid/PAPERS/BDFL-TAMS-final.pdf)

## Two sweeps of the ideal updates

Remove the deterministic rotations by tracking coordinates in a rotating frame. A sweep consists of $d$ updates of successive $b$-bit windows. They cover all the coordinates. If $b$ divides $n$ they are disjoint. Otherwise only the first and last overlap, in $db-n$ coordinates.

Track two distinct points. When their controls differ, their two ideal offsets are independent. The difference on the updated window is therefore freshly uniform. When the controls agree, the existing nonzero difference lies entirely within that window and stays fixed. Call this update forced. Among the first $d-1$ disjoint windows, at most one update can be forced, since it leaves a nonzero difference in an already processed window. In the disjoint case this holds across all $d$ windows. There are at most two forced updates in the overlapping case.

Fix a candidate final difference. In the disjoint case it determines every written window. Its probability after the sweep is at most $B^{-(d-1)}=B/N$. In the overlapping case there are at most $2^{db-n}$ possible first writes on the bits that are subsequently overwritten. Every possible history has probability at most $B^{-(d-2)}$. Consequently every nonzero difference has probability at most $C/N$ after one sweep. Each subsequent ideal difference kernel is doubly stochastic. On a nonzero fixed control difference it replaces the window uniformly, and on control difference zero it fixes the nonzero window. Thus the same pointwise upper bound applies throughout the second sweep.

At a given second-sweep step the probability that some two tracked points share a control is at most $\binom t2(B-1)C/N$, since a colliding difference is one of the $B-1$ nonzero differences supported in that window. Couple these ideal updates to a process that uses fresh independent offsets *for each point*, even when two controls match. They can agree throughout the second sweep unless a control collision occurs. The independent process ends in $t$ independent uniform points, since all coordinates are refreshed by independent uniform window bits. This gives the first term of $\delta$ by a union bound. The ideal process always ends in distinct points. For any law supported there, conditioning the independent uniform target on distinctness can only decrease its TV from that law: conditioning increases the target mass at every possible observed point and decreases the total positive excess.

The ideal sweep bound also holds after projecting to differences. Comparing the actual and ideal difference chains for $2d$ steps costs at most $2d(\eta+th/N)$ by successive couplings. Thus every row of the actual $2d$-step difference kernel is within $\delta$ of uniform on differences. The largest TV distance between two rows is at most $2\delta$. Decomposing a signed measure into positive and negative parts gives that contraction factor for each subsequent block. Uniform on differences is stationary since each full-tuple layer is a mixture of permutations, and every difference tuple has $N$ preimages. The exact final-mask identity now gives the claimed full-tuple bound.

## A finite lower bound for this construction

When $t\le B$, start with $t$ distinct low blocks and a common control. The first layer gives every point the same offset, so the first difference state is deterministic. Each later layer has at most $B^{t-1}$ possible patterns of relative offsets. After $r\ge2$ cipher rounds the support of the difference law before the final mask therefore has size at most $B^{(t-1)(r-2)}$. The uniform target has $(N-1)(N-2)\cdots(N-t+1)$ difference states. Its mass outside that support gives a lower bound on TV.

For $n=128$, $b=16$, $t=4$ and $r=9$, the support contains at most $2^{336}$ of the $(2^{128}-1)(2^{128}-2)(2^{128}-3)$ states. The resulting distance is greater than $2^{-128}$, so at least 10 rounds are necessary in the worst case. The sufficient bound of 81 leaves room to improve the analysis. In its two-sweep estimate, the relative-offset comparison contributes approximately $1.12\times10^{-8}$ and the ideal control-collision term contributes $6.06\times10^{-28}$.

## Scaling and prior work

For $2\le t\le n/2-1$, take $b=\lfloor n/(2(t+1))\rfloor$ and $h=0$. Since the floor of a real number at least one is at least half that number, $d\le4(t+1)+1$. The bias contribution is $O(t^2 2^{-(n-b(t+1))/2})=O(t^2 2^{-n/4})$, and the ideal term is $O(t^3 2^{3b-n})=O(t^3 2^{-n/2})$. Thus $2\delta\le2^{-n/5}$ for all sufficiently large $n$, uniformly over the stated orders. Taking $j=\max(1,\lceil5\log_2(1/\epsilon)/n\rceil)$ proves the round bound. Conversely $r$ independent $n$-bit keys can reach at most $N^r$ target tuples. TV at most $\epsilon$ requires $N^r\ge(1-\epsilon)(N)_t$, where $(N)_t=N(N-1)\cdots(N-t+1)$. At $\epsilon=2^{-n}$ this gives $r\ge t$ for these orders and sufficiently large $n$. A different tradeoff uses $b=1$ to allow $t\le(1-\gamma)n$ for fixed $0<\gamma<1$, still obtaining exponentially small block error up to polynomial factors.

Morris, Rogaway and Stegers study precisely the independent-switch one-bit model under the name *Thorp shuffle*, giving a stronger ideal bound after $2n-1$ steps. Hoang and Rogaway treat wider unbalanced Feistel networks in their independent random-function model. Kaplan, Naor and Reingold construct almost $t$-wise permutations via derandomization and discuss Feistel networks with richer function families. The local Fourier estimate, character-sum bound and TV amplification are established tools. The particular repeated public inverse-projection construction, its translation reduction, and the stated quantitative guarantee are project derivations whose publication priority is unverified. [Morris–Rogaway–Stegers, Theorem 1](https://www.cs.ucdavis.edu/~rogaway/papers/thorp.pdf) · [Hoang–Rogaway, unbalanced Feistel](https://www.cs.ucdavis.edu/~rogaway/papers/feistel.pdf) · [Kaplan–Naor–Reingold](https://www.wisdom.weizmann.ac.il/~naor/PAPERS/kwise.pdf)
