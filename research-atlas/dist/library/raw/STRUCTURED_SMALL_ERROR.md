# Which field powers mix at small error?

Take a fixed field permutation $P(x)=x^d$ on $N=2^n$ points, with $P(0)=0$. Assume $n\ge3$ and $\gcd(d,N-1)=1$. Reduce $d$ to $1,\ldots,N-2$. There is a complete answer for eventual mixing. **If $d$ is a power of two, even pairs fail to mix. Every other exponent mixes every ordered tuple size through $N-2$.** This includes cubing in every odd dimension at least three. The decision uses just the exponent. It follows from a published finite-group classification by Stafford. [Stafford, *Groups of Permutation Polynomials over Finite Fields*, 1998](https://doi.org/10.1006/ffta.1998.0224)

There is also a finite sufficient round count. For every nonlinear permuting exponent, every $2\le t\le N-2$ and every integer $\lambda\ge1$,
$$r=2N^{2t+4}(\lambda+nt)$$
full cipher rounds guarantee worst-start TV at most $2^{-\lambda}$. This is a coarse bound intended to certify the whole class. Its growth in $N$ leaves substantial room for improvement. Even the inverse power can require order $N$ rounds at fixed error on quadruples. The exact finite-width measurements below give much smaller round counts for cubing. [Inverse-walk lower bound](https://eprint.iacr.org/2024/1795)

## Exact small-error times for cubing

Every entry is the first full cipher round at the stated threshold, maximizing TV over all ordered distinct inputs. The arithmetic and symmetry reduction are exact.

| Bits | Tuple size | Starting classes checked | $2^{-16}$ | $2^{-32}$ | $2^{-64}$ | $2^{-128}$ |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 3 | 1 | 17 | 33 | 65 | 129 |
| 5 | 3 | 1 | 10 | 17 | 34 | 66 |
| 7 | 3 | 3 | 8 | 12 | 23 | 44 |
| 3 | 4 | 2 | 34 | 66 | 130 | 258 |
| 5 | 4 | 8 | 11 | 18 | 34 | 67 |

At five bits, quadruples take just one more round than triples at the $2^{-128}$ threshold. At three bits they take twice as many. Neither observation establishes the rate at larger widths. LTV study cubing and pairwise independence. The table here records the realized rate for triples and quadruples of one fixed cubing permutation with fresh binary XOR keys. [Liu, Tessaro and Vaikuntanathan](https://eprint.iacr.org/2021/507)

The verifier can evaluate exact short blocks and use those blocks to certify smaller errors. For example, at five bits, just eight measured shape steps certify 89 full rounds for quadruples at $2^{-128}$. Extending the exact computation to 66 shape steps gives the minimal 67 rounds. With the pure field-power description the second command instead evaluates the conservative all-width formula without materializing a field table. [Verifier](structured_probe.py)

```sh
uv run --locked --extra four-bit python -m research.structured_probe --modulus 0x25 --exponent 3 --order 4 --steps 66
uv run --locked python -m research.structured_probe --bits 128 --exponent 7 --order 4 --security-bits 128
```

The other table moduli, in the polynomial basis, are $X^3+X+1$ (`0xb`) and $X^7+X+1$ (`0x83`). To reproduce a column, take one fewer shape steps than its largest claimed full round at the selected bit width and tuple order. Supply `--file table.txt` with `--modulus` to check a decimal truth table against the given power in its polynomial basis. The comparison costs $O(N\,\mathrm{poly}(n,\log d))$ on top of measuring the reference blocks. If the table has $h$ disagreements, the same keys couple one shape update except when one of the $t$ translated inputs lands in those entries. Each translated input is uniform. Thus a measured $s$-step reference distance $\delta_s$ gives a worst distance at most $\min(1,\delta_s+sth/N)$ on the actual table. The program amplifies this bound per block. For example, on seven bits any transposition of two outputs of cubing ($h=2$) still certifies ordered triples at $2^{-128}$ in **256 rounds**, using reference blocks through eight shape steps. [Field-table generator](../power_mixing.py)

## Why the exponent decides all tuple orders

Write $T$ for the XOR translations, $S_c(x)=cx$ for field scalar multiplication, and $H=\langle P^j T P^{-j}: j\in\mathbb Z\rangle$. The group $H$ controls the independent keyed rounds. It is normalized by $P$ and contains $T$. It is also normalized by every $S_c$, because $P S_c P^{-1}=S_{c^d}$ and scalars normalize $T$. For example, conjugating $P^jTP^{-j}$ by $S_c$ yields the very same subgroup, by moving the scalar through $P^j$. Consequently $H$ is normal in $G=\langle P,T,S_c:c\ne0\rangle$.

Stafford proves that this larger group contains $A_N$ whenever $d$ is a permuting exponent other than a Frobenius power. All nonidentity binary translations are even for $n\ge2$ (each is a product of $N/2$ transpositions), so $1\ne H\le A_N$. Simplicity of $A_N$ gives $H=A_N$. The alternating group acts transitively on every ordered distinct $t$-tuple for $t\le N-2$, proving the positive criterion by the tuple-orbit theorem. At $t=N-1,N$, the tuple reveals the permutation's sign and every fixed round count has a deterministic sign. If $d$ is a power of two, $P$ is binary linear and every pair difference evolves deterministically. [Orbit theorem](../LARGER_BITS.md#an-exact-criterion-for-every-bit-length)

## A dimension-explicit bound at any error

Let $k$ be the multiplicative order of $d$ modulo $N-1$. Then $P^k$ is the identity and $k\le N-1$. In a block of $k$ rounds, move all deterministic copies of $P$ to one end of the product. The remaining independent factors are uniform elements of the $k$ groups $P^jTP^{-j}$, each used once in fixed order. On functions on the $M=(N)_t$ ordered distinct tuples, averaging over such a subgroup is an orthogonal projection $E_i$ in counting-measure $\ell^2$. Every subgroup orbit is a clique of size $N$ because no nonidentity conjugate translation fixes a point.

The union of the clique graphs is connected by $H$-transitivity. For mean-zero $f$,
$$\sum_i\|(I-E_i)f\|_2^2 \ \ge\ \frac{\|f\|_2^2}{NM^2}.$$
Indeed the energy of one projection is $1/N$ times the sum of squared differences across all unordered edges of its disjoint cliques. Choose a spanning tree in the union. The squared difference between any two vertices is at most $M$ times the sum of squared edge differences on the tree, by Cauchy–Schwarz along their path. Summing over pairs and using $\sum_{u,v}|f(u)-f(v)|^2=2M\|f\|_2^2$ gives the displayed bound.

Apply the projections in the block order starting with $f_0=f$, and set $w_i=\|f_{i-1}-f_i\|_2$ with $f_i=E_i f_{i-1}$. Pythagoras gives $\sum_iw_i^2=\|f\|_2^2-\|f_k\|_2^2$. Since $I-E_i$ is a contraction, $\|(I-E_i)f\|_2\le\sum_{j\le i}w_j$. Summing the squared inequalities bounds the left side of the energy inequality by $k^2\sum_iw_i^2$. Hence each block contracts the mean-zero norm by at most $\sqrt{1-1/(NM^2k^2)}$.

After $j$ blocks the TV from a fixed starting tuple is thus at most $\sqrt{M-1}\exp(-j/(2NM^2k^2))/2$. The prefactor follows from Cauchy–Schwarz applied to the initial point mass relative to uniform. TV cannot increase at later rounds since each keyed layer preserves uniform. Using $k\le N$, $M\le N^t$ and $\log N=n\log2$ proves the advertised round count. Its logarithmic dependence on the desired inverse error follows from contraction.

## How the finite-width certificate works

Represent a start by $(0,1,z_2,\dots,z_{t-1})$. Translating the inputs only changes the first key. Multiplying every input by $c\ne0$ multiplies outputs after $r$ rounds by $c^{d^r}$ in law, by rescaling the independent keys at each step. Frobenius squaring commutes with $P$ and maps uniform keys to uniform keys. Finally permuting the tuple positions preserves TV. These symmetries yield the small number of starting classes in the table. The procedure enumerates normalized sets and explicitly covers each class under these operations. It retains every ordered output shape in the transition calculation.

With the first coordinate used as anchor, a shape is a list of $t-1$ distinct nonzero differences. Its transition independently chooses $u$ uniform and applies $a\mapsto P(u+a)+P(u)$ to every entry. Each such map is a bijection. The TV after $s$ shape steps equals the full tuple TV after $s+1$ cipher rounds because a final uniform XOR distributes each shape uniformly in its fiber, and the final fixed bijection preserves TV. [General shape reduction](HIGHER_CENSUS.md)

Let $m=(N-1)_{t-1}$. Store the exact signed integers $m\,c_s(y)-N^s$, where $c_s(y)$ is the number of key paths ending at $y$. A step sums the stored integers over all predecessors. Divide the sum of their absolute values by $2mN^s$ to get TV. The verifier switches to arbitrary-precision arithmetic before overflow. A computed maximum $\delta_s$ bounds the TV distance between any two rows by $2\delta_s$. If $2\delta_s<1$, repeated blocks of $s$ shape steps certify
$$d_t(1+js)\le\delta_s(2\delta_s)^{j-1}.$$
The program labels extrapolations as upper bounds and fully evaluated threshold crossings as exact. This calculation is exponential in the bit width and is intended for the small cases in the table.

## A route to sharper cube bounds

For triples, the field-power symmetry also reduces the operator itself. Write the shape as $(a,az)$ with $a\ne0$ and $z\notin\{0,1\}$. At a uniform normalized anchor $u$, put $h(u)=(u+1)^d+u^d$ and $z'=[(u+z)^d+u^d]/h(u)$. The new shape has scale $a^dh(u)$ and ratio $z'$. For any multiplicative character $\chi$, applying the one-step operator to $\chi(a)g(z)$ gives $\chi(a)^d(B_\chi g)(z)$, where
$$ (B_\chi g)(z)=N^{-1}\sum_u \chi(h(u))g(z'). $$
Thus long products can be studied on matrices of size $N-2$ along the character cycles $\chi\mapsto\chi^d$. The pairwise case has scalar character factors. A uniform bound for these triple products for cubing could explain the much smaller round counts in the table. The exponent classification alone does not give that rate.

**Attribution.** The affine-plus-power group classification is Stafford's published result. The XOR-only conclusion follows by normality, and the quantitative all-width bound follows from elementary projection and path inequalities. The higher-order threshold measurements here are project computations. Publication priority for the round estimates remains unverified.
