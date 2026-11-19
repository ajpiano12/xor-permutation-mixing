# How many rounds do triples need?

There are two different answers worth pursuing. For the **patched field inverse**, three full cipher rounds put every ordered triple within $7/N$ of uniform, where $N=2^n\ge4$. This gives a checkable sufficient condition for three-wise approximate independence, one of the targets of problem 4. For an **unrestricted uniform table** reused each round, a finite collision calculation proves that four rounds suffice at every fixed positive TV threshold with probability tending to one. A second collision calculation shows three rounds typically leave at least $1/3-o(1)$ TV, making four the exact typical time at $1/4$. [Four-round upper bound](TRIPLE_MOMENT.md) · [Three-round lower bound](TRIPLE_LOWER.md)

## An explicit certificate for triples

Identify bit strings with the polynomial basis of $\mathbb F_N$ for a given irreducible modulus. Let $I(x)=x^{-1}$ for nonzero $x$, with $I(0)=0$. If a given permutation $P$ disagrees with $I$ in $h$ table entries, then its worst-start ordered-triple distance satisfies

$$d(3)\le\delta=\min\{1,(7+6h)/N\}.$$

For example the inverse on five bits has $d(3)\le7/32<1/4$. On eight bits this certificate still gives three-round TV below $1/4$ after arbitrary changes at up to nine entries, provided the new table is a permutation. For $\delta<1/2$ it gives $d(3j)\le\delta(2\delta)^{j-1}$. One simply measures the disagreement in the stated field coordinates. Given another known binary linear change of basis one may first conjugate the table by that map, since shared XOR keys are uniform in either basis. The checker computes field inverses by binary polynomial Euclid and rejects reducible moduli. It requires $O(N\,\mathrm{poly}(n))$ time. [Certificate program](../inverse_triples.py)

### Proof on the projective line

Dropping the final application of $P$ preserves TV to uniform. Three rounds on a tuple are therefore equivalent for this measurement to $T_c P T_b P T_a$, where $T_a(x)=x+a$ and the three keys are independent and uniform. Replace the two inversions by projective inversion $J$, which swaps zero and infinity. The resulting map on $\mathbb P^1(\mathbb F_N)$ has determinant-one matrix

$$ T_c J T_b J T_a=
\begin{pmatrix}1+bc & a+c+abc \\ b & 1+ab\end{pmatrix}.$$

Conditional on $b\ne0$, this is uniform over the determinant-one matrices with nonzero lower-left entry. That entry determines $b$ and the diagonal determines $a,c$. The determinant fixes the last entry. There are $(N-1)N^2$ matrices in this subset, out of $N(N^2-1)$ in the group. Thus a uniform group element lands in the subset with probability $N/(N+1)$ and the keyed product does so with probability $(N-1)/N$. The two distributions share a uniform component of mass $(N-1)/N$, giving TV at most $1/N$.

In characteristic two each projective linear map has a unique determinant-one representative because squaring on the field is bijective. The projective group is sharply three-transitive: a unique fractional linear transformation carries any ordered triple of distinct projective points to any other. A uniform group element sends each such triple to a uniform projective triple.

Run the field and projective processes with the same keys from a finite triple. They agree until, before one of the two inversions, a tracked value equals zero or lies in the $h$ disagreement entries. Up to the first disagreement all values are finite. In the field process, independently of its past, the next fresh translation puts each of the three values uniformly in the field. A union bound costs at most $6(1+h)/N$. Including the group estimate gives the displayed bound to projective uniform. To compare with uniform on *finite* triples, observe that the field process is supported on finite triples and conditioning projective uniform to that set increases each target mass there. Summing positive excesses therefore only decreases the TV upper bound.

The three-round stochastic kernel preserves uniform. If every row is within $\delta$ of uniform, any two rows are within $2\delta$ of each other. Decompose a signed row of total mass zero into its positive and negative parts to get contraction factor at most $2\delta$ per block. Iterating proves the bound for $3j$ rounds. Conversely two rounds have at most $N^2$ key sequences and the number of target triples is $N(N-1)(N-2)$. Their TV is at least $1-N/((N-1)(N-2))$. Thus for the inverse, three rounds are optimal at every fixed error in $(0,1)$ for all sufficiently large $n$.

Jain et al. use a modified Möbius approximation in §4.1, Lemmas 4.3–4.4. The sharp three-transitivity of the projective group is classical. We treat this bound as a corollary of the underlying geometry. The explicit constants and the table-disagreement extension above have unverified publication priority. At order four, the published inverse-walk result gives a much slower rate. A fractional linear map preserves the cross-ratio of four points, illustrating why the argument for triples stops there. [Jain et al., inverse walk](https://eprint.iacr.org/2024/1795)

A separate calculation for the exact inverse gives $d(3)=7/N+O(N^{-2})$ uniformly over starting triples. It counts the triple shapes outside the generic fractional linear maps. [Sharp inverse rate](INVERSE_TRIPLE_RATE.md)

## What a random table does

At each bit length we sampled 32 independent uniform permutations and reused each one. We evaluated exact TV for the fixed starting triple $(0,1,2)$ and summarized over tables. Cipher round counts include the last permutation. Each individual distance is obtained by summing integer key counts on the $(N-1)(N-2)$ ordered shapes. [Raw fractions](../results/triple_probe.csv) · [Experiment](triple_probe.py)

| Bits | Median TV after 3 rounds | Median TV after 4 rounds | Range after 4 rounds |
| ---: | ---: | ---: | ---: |
| 4 | 0.41209 | 0.14045 | 0.09363–0.28798 |
| 5 | 0.38805 | 0.08622 | 0.07104–0.11253 |
| 6 | 0.38045 | 0.05632 | 0.05248–0.06380 |
| 7 | 0.37448 | 0.03724 | 0.03650–0.04012 |

```sh
uv run --locked --extra four-bit research/triple_probe.py
```

After two difference steps there are $N^2$ key sequences for $(N-1)(N-2)$ shapes. Independently allocating that many paths would leave about $e^{-1}$ of the shapes empty. The measurements make this a plausible candidate for the limiting three-round TV. Three factorial moments rigorously place the limiting distance between $1/3$ and $1/2$ up to a vanishing error. Identifying an exact limit remains open. [Moment bounds](TRIPLE_LOWER.md) Paths using overlapping inputs of the same table are dependent. A proof needs to count these collisions or control the resulting occupancy law. The concentration step in the four-round proof shows how to transfer a mean estimate for a fixed start to a bound for all starts.

For the four-round upper bound, track two independent key paths from the same triple using the same public table. The joint experiment makes at most 18 table lookups. Classifying equalities among the addresses and the replies gives a finite count showing that the two final shapes have collision probability $N^{-2}+O(N^{-3})$. A permutation concentration bound controls all starting triples at once. The proof and executable certificate are available separately. [Random triple theorem](TRIPLE_MOMENT.md)
