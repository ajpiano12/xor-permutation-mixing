# One fixed permutation for three, four and more inputs at small error

On 128 bits, a single explicit permutation sends **every ordered quadruple** within $2^{-128}$ of uniform after **129 cipher rounds**. The same permutation gives **81 rounds for triples**. A second choice gives **225 rounds for eight inputs**. Each uses one public table or circuit throughout and independent uniform XOR keys, as in Problem 4. These numbers are sufficient upper bounds.

| Bits $n$ | Updated bits $b$ | Tuple order $t$ | Rounds for $2^{-32}$ | Rounds for $2^{-64}$ | Rounds for $2^{-128}$ |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 64 | 8 | 3 | 65 | 113 | 209 |
| 128 | 16 | 3 | 33 | 49 | 81 |
| 128 | 16 | 4 | 33 | 65 | 129 |
| 128 | 8 | 8 | 65 | 129 | 225 |
| 256 | 32 | 4 | 17 | 33 | 65 |

For all sufficiently large $n$ and every target $2\le t\le n/2-1$, choosing the block width for that target gives **$O(t(1+\log(1/\epsilon)/n))$ rounds**. In particular, at error $2^{-n}$ the bound is $O(t)$, matching the key-count lower bound up to a constant. Each public permutation is fixed throughout its run. Its bound for $t$ also applies to all smaller orders by projection.

## Construction and verification

Take $1\le b\le n/2$, write $B=2^b$, $N=2^n$, and $Q=2^{n-b}$. Split an input into its low $b$ bits $v$ and the other bits $z$. Interpret $z$ in a specified polynomial basis of $\mathbb F_Q$. Put $I(0)=0$ and $I(z)=1/z$ elsewhere. Let $f(z)$ be the low $b$ coordinates of $I(z)$. Define $E(v,z)=(v\oplus f(z),z)$ and let $R$ rotate the entire word right by $b$ positions, moving the low block to the high end. Use the fixed public permutation $P_0=R E$. The invertible update $E$ is an unbalanced Feistel step. Any surjective binary linear projection in place of the low $b$ coordinates gives the same bound.

The verifier accepts this compact description and checks irreducibility of the field modulus in polynomial time in $n$. A generic supplied circuit still needs a witness that it implements this formula. For a table, the verifier compares every entry to $P_0$ and automatically includes the number $h$ of disagreements. The table check costs $O(N\,\mathrm{poly}(n))$. The first command verifies both large and small thresholds on the specified compact 128-bit example, whose irreducible modulus is $X^{112}+X^5+X^4+X^3+1$. Pass a table with `--file` to verify a concrete list instead. [Verifier](spectral_certificate.py)

```sh
uv run --locked python -m research.spectral_certificate --bits 128 --block-bits 16 --order 4 --modulus 0x10000000000000000000000000039 --error-bits 32 64 128
uv run --locked python -m research.spectral_certificate --bits 128 --block-bits 8 --order 8 --modulus 0x100000000000000000000000000001b
```

## Finite bound

Write $d=\lceil n/b\rceil$, $s=\min(t,Q)$, and take $C=B$ when $b$ divides $n$ and $C=B^2$ otherwise. Set

$$
\beta=\frac{2(s-1)\sqrt Q+s+1}{Q},\qquad
\eta=\tfrac12\sqrt{B^s-1}\,\beta,\qquad
\delta=\min\left(1,\frac{d\binom t2 C(B-1)}{N}+2d(\eta+th/N)\right).
$$

If $P$ differs from $P_0$ on $h$ inputs and $\delta<1/2$, then at $1+2dj$ cipher rounds the worst-start TV satisfies

$$d_t(1+2dj)\le\delta(2\delta)^{j-1},\qquad j\ge1.$$

The first block already gives $d_t(1+2d)\le\delta$ regardless of its size. The program rounds each square root upward to the next integer for rational arithmetic and returns the first block count meeting the requested threshold with these upper bounds.

## Independent translated updates from the original keys

Write the actual permutation as $P=R E'$, with $E'=E$ for the unmodified construction. Denote XOR by $T_a$. Starting at $F_0=G_0=\mathrm{id}$ and $A_0=0$, set $C_i=K_i\oplus A_{i-1}$, $A_i=R C_i$ and

$$G_i=R T_{C_i} E' T_{C_i}G_{i-1}.$$

Then $F_i=T_{A_i}G_i$ by induction. The masks $C_i$ are independent uniform, since each original $K_i$ is fresh given the past. The original $r$-round cipher is $F_r=P T_{C_r}G_{r-1}$, with its last mask independent of $G_{r-1}$. Applying this final random bijection preserves uniform and contracts TV. It suffices to study the homogeneous walk $G$ over $r-1$ layers.

With $E'=E$, conjugation translates the control $z$ by one uniform $u\in\mathbb F_Q$. The updated low block now receives $f(z+u)$, with the same $u$ across the tuple. For general $E'$, the probability of encountering one of the $h$ exceptional inputs among the $t$ translated points is at most $th/N$ per layer from any current state.

## Replacing the translated update by independent offsets

In the ideal layer each control $z$ gets an independent uniform $b$-bit offset. A tuple addresses at most $s$ distinct controls. For any $k\le s$ distinct controls, Fourier inversion, Parseval and Cauchy–Schwarz give TV at most $\sqrt{B^k-1}\,\beta/2$ if the bias of every nonzero joint binary parity of its $k$ offsets is at most $\beta$. This is a standard small-bias estimate. [Naor and Naor](https://doi.org/10.1137/0222053)

Here is why the needed bias holds for the inverse projection. By nondegeneracy of the field trace pairing, any nontrivial parity uses a nonempty set of $j\le k$ distinct controls $a_i$ and nonzero coefficients $c_i\in\mathbb F_Q$. Off these controls the parity is the absolute trace of
$$g(u)=\sum_{i=1}^{j}\frac{c_i}{u+a_i}.$$
Each pole is simple with nonzero residue, which also ensures the Artin–Schreier curve $y^2+y=g(u)$ is geometrically irreducible. Its smooth projective model has genus $j-1$. Each finite pole contributes one rational point, and infinity contributes two since $g(\infty)=0$. Consequently its point count equals $Q+2+\sum_{u\notin\{a_i\}}(-1)^{\operatorname{Tr}(g(u))}$. Hasse–Weil bounds its distance from $Q+1$ by $2(j-1)\sqrt Q$. Including the $j$ patched summands changes the sum by at most $j$, giving the claimed $\beta$. This uses classical arithmetic of Artin–Schreier curves. [Bucur, David, Feigon and Lalín, §2](https://mypage.concordia.ca/mathstat/cdavid/PAPERS/BDFL-TAMS-final.pdf)

## Two sweeps of the ideal updates

Remove the deterministic rotations by tracking coordinates in a rotating frame. A sweep consists of $d$ updates of successive $b$-bit windows. They cover all the coordinates. If $b$ divides $n$ they are disjoint. Otherwise only the first and last overlap, in $db-n$ coordinates.

Track two distinct points. When their controls differ, their two ideal offsets are independent. The difference on the updated window is therefore freshly uniform. When the controls agree, the existing nonzero difference lies entirely within that window and stays fixed. Call this update forced. Among the first $d-1$ disjoint windows, at most one update can be forced, since it leaves a nonzero difference in an already processed window. In the disjoint case this holds across all $d$ windows. There are at most two forced updates in the overlapping case.

Fix a candidate final difference. In the disjoint case it determines every written window. Its probability after the sweep is at most $B^{-(d-1)}=B/N$. In the overlapping case there are at most $2^{db-n}$ possible first writes on the bits that are subsequently overwritten. Every possible history has probability at most $B^{-(d-2)}$. Consequently every nonzero difference has probability at most $C/N$ after one sweep. Each subsequent ideal difference kernel is doubly stochastic. On a nonzero fixed control difference it replaces the window uniformly, and on control difference zero it fixes the nonzero window. Thus the same pointwise upper bound applies throughout the second sweep.

At a given second-sweep step the probability that some two tracked points share a control is at most $\binom t2(B-1)C/N$, since a colliding difference is one of the $B-1$ nonzero differences supported in that window. Couple these ideal updates to a process that uses fresh independent offsets *for each point*, even when two controls match. They can agree throughout the second sweep unless a control collision occurs. The independent process ends in $t$ independent uniform points, since all coordinates are refreshed by independent uniform window bits. This gives the first term of $\delta$ by a union bound. The ideal process always ends in distinct points. For any law supported there, conditioning the independent uniform target on distinctness can only decrease its TV from that law: conditioning increases the target mass at every possible observed point and decreases the total positive excess.

Comparing actual and ideal layers for $2d$ steps costs at most $2d(\eta+th/N)$ by successive couplings. Thus every row of the $2d$-step actual kernel is within $\delta$ of uniform. The largest TV distance between two rows is at most $2\delta$. Decomposing a signed measure into positive and negative parts gives that contraction factor for each subsequent block. Uniform is stationary, proving the bound.

## Scaling and prior work

For $2\le t\le n/2-1$, take $b=\lfloor n/(2(t+1))\rfloor$ and $h=0$. Since the floor of a real number at least one is at least half that number, $d\le4(t+1)+1$. The bias contribution is $O(t^2 2^{-(n-b(t+1))/2})=O(t^2 2^{-n/4})$, and the ideal term is $O(t^3 2^{3b-n})=O(t^3 2^{-n/2})$. Thus $2\delta\le2^{-n/5}$ for all sufficiently large $n$, uniformly over the stated orders. Taking $j=\max(1,\lceil5\log_2(1/\epsilon)/n\rceil)$ proves the round bound. Conversely $r$ independent $n$-bit keys can reach at most $N^r$ target tuples. TV at most $\epsilon$ requires $N^r\ge(1-\epsilon)(N)_t$, where $(N)_t=N(N-1)\cdots(N-t+1)$. At $\epsilon=2^{-n}$ this gives $r\ge t$ for these orders and sufficiently large $n$. A different tradeoff uses $b=1$ to allow $t\le(1-\gamma)n$ for fixed $0<\gamma<1$, still obtaining exponentially small block error up to polynomial factors.

Morris, Rogaway and Stegers study precisely the independent-switch one-bit model under the name *Thorp shuffle*, giving a stronger ideal bound after $2n-1$ steps. Hoang and Rogaway treat wider unbalanced Feistel networks in their independent random-function model. Kaplan, Naor and Reingold construct almost $t$-wise permutations via derandomization and discuss Feistel networks with richer function families. The local Fourier estimate, character-sum bound and TV amplification are established tools. The particular repeated public inverse-projection construction, its translation reduction, and the stated quantitative guarantee are project derivations whose publication priority is unverified. [Morris–Rogaway–Stegers, Theorem 1](https://www.cs.ucdavis.edu/~rogaway/papers/thorp.pdf) · [Hoang–Rogaway, unbalanced Feistel](https://www.cs.ucdavis.edu/~rogaway/papers/feistel.pdf) · [Kaplan–Naor–Reingold](https://www.wisdom.weizmann.ac.il/~naor/PAPERS/kwise.pdf)
