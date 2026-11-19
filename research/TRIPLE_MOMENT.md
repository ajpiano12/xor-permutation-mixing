# Four cipher rounds suffice for random fixed-permutation triples

Let $q=2^n$. Choose a uniform permutation $P$ of the $q$ field elements once and use it in every round, with a fresh common uniform XOR key. With probability at least $1-O_K(q^{-K})$ over $P$, **every ordered triple of distinct inputs is within $O_K(\sqrt{\log q/q})$ of the uniform ordered triple after four cipher rounds**, for each fixed $K>0$. At any fixed positive error threshold the probability of failing this upper bound on the round count is exponentially small for large $q$. This is a computer-assisted project proof. The finite case enumeration uses only integer XOR, Gaussian elimination and two loops over previous queries.

At TV threshold $1/4$, the typical mixing time is **exactly four cipher rounds**. A complementary calculation puts every start's three-round distance between $1/3-o(1)$ and $1/2+o(1)$ with probability tending to one. The precise limiting constant remains open. [Three-round occupancy bounds](TRIPLE_LOWER.md)

## A collision of two paths measures the error

An ordered triple up to common translation has a unique shape $(a,b)$, the pair of differences from its first coordinate. There are $m=(q-1)(q-2)$ shapes since $a,b$ are distinct and nonzero. Write $Q$ for the shape transition induced by an independent uniform translation followed by $P$. Uniform on shapes is stationary because each shape has $q$ representatives and $P$ bijects the triples. As for pairs, the final uniform translation distributes a triple uniformly in its shape and the final bijection preserves TV. Consequently the four-cipher-round TV is the three-shape-step TV. Any starting shape may be taken to $(a,b)$ for two fixed independent binary vectors by a change of linear coordinates that preserves the uniform law of $P$.

For a fixed start let $p(P)$ be the row of $Q^3$. Run two trajectories of three shape steps using the same $P$ and independent keys. Conditional on the table the probability their final shapes agree is $\sum_s p_s(P)^2$. The finite enumeration below proves the unconditional collision probability is

$$
\mathbb E_P\sum_s p_s(P)^2=q^{-2}+O(q^{-3}).
$$

Subtract $1/m=q^{-2}+O(q^{-3})$ and use Cauchy–Schwarz to obtain

$$
\mathbb E_P\,\mathrm{TV}(p(P),u)
\le \tfrac12\sqrt{m\,\mathbb E_P\sum_s (p_s(P)-1/m)^2}
=O(q^{-1/2}).
$$

Transposing two images of $P$ affects at most six of the $q$ possible translations in any one-step row. Each image can occur in each of the three input positions for only one translation. Thus every such row changes by at most $6/q$ in TV. Telescoping $Q^3-(Q')^3$ and using that stochastic kernels contract TV gives $18/q$ for three steps. Exposing the values of the uniform table one at a time, coupling completions by a transposition, gives martingale increments bounded by $18/q$. Azuma's inequality and a union bound over all $m$ starts yield

$$
\Pr\!\left[\max_s \mathrm{TV}(e_sQ^3,u)>C/\sqrt q+t\right]
\le 2m\exp(-qt^2/648)
$$

for all sufficiently large $q$ and an absolute constant $C$. Taking $t$ of order $\sqrt{\log q/q}$ proves the theorem. At fixed error use constant $t$. When the maximal TV is below $1/2$, distances between rows are bounded away from one and $Q^3$ strictly contracts TV, giving convergence for every starting triple.

## Exact finite enumeration of the leading terms

There are six independent keys, one for each of two paths at each of three times. Starting the paths at $(0,a,b)$, each path queries $P$ at three distinct addresses per time. List the first path's queries in chronological order and then the second path's. The two paths share the table and use independent keys, so this order preserves their joint law. A query address is its previous reply XOR its new round key. For the first time use $0,a,b$ in place of previous replies.

Partition the 18 calls by address equality. Give each distinct address a formal output variable. A repeated address must receive its previous reply, and different addresses must receive distinct replies. For a fixed pattern with $k$ distinct calls its six keys and $k$ assigned outputs must satisfy finitely many XOR equalities and inequations over $\mathbb F_2^n$. Add the two equations asserting final shape equality. The total mass of this pattern is exactly

$$
\frac{\#\{\text{assignments of the six keys and }k\text{ outputs satisfying all constraints}\}}
     {q^6(q)_k},
\qquad (q)_k=q(q-1)\cdots(q-k+1).
$$

For every assignment in the numerator the probability of its keys is $q^{-6}$. The assigned distinct input-output pairs have probability $1/(q)_k$ for a uniform permutation. Reuse across times is part of this count.

Let $e$ be the rank of the independent equality constraints on the $6+k$ variables. Treat $a,b$ as independent fixed vectors. A constraint that forces $a$, $b$ or $a+b$ to zero is inconsistent. So is an inequation forced to zero. Otherwise, the equalities leave exactly $q^{6+k-e}$ choices. Any remaining inequation either always holds or excludes exactly a $1/q$ fraction. There are finitely many, so their removal leaves $q^{6+k-e}(1+O(1/q))$ choices as $q\to\infty$. Each consistent pattern therefore contributes $q^{-e}(1+O(1/q))$. All constants here are absolute since the list length is fixed at 18.

The following search visits all consistent terminal patterns with $e\le2$.

1. Keep a list of the distinct addresses and assigned replies, a row-echelon basis of the imposed equalities, and all required nonzero expressions. Expressions are XOR bitmasks for the six keys, symbolic replies and the two constants.
2. If an existing address is forced equal to the next query, reuse its reply. Otherwise branch separately on equality to each previous address, imposing that equality. Reject contradictions and any branch of rank above two.
3. In the remaining branch the new address differs from all old ones. Introduce a fresh output variable and record the inequalities enforcing distinct addresses and distinct replies. These branches are exhaustive and disjoint.
4. Impose each endpoint equality as soon as its two differences have been exposed. Reject inconsistent inequations and tally by final equality rank and number of distinct addresses.

Each circuit here has finitely many possible partitions (at most the 18th Bell number). Equality rank can never decrease when a branch is extended, since a fresh reply is a new independent variable and does not alter existing equations. As a result the total contribution from all discarded consistent terminal patterns of rank at least three is $O(q^{-3})$. The calculation does not require enumerating those discarded patterns or approximating their number.

The standalone certificate in this repository reproduces the following complete counts through rank two.

    uv run --locked research/triple_moment.py

| Shape steps | Rank | Distinct calls | Number of patterns |
|---:|---:|---:|---:|
| 1 | 1 | 3 | 1 |
| 1 | 2 | 4 | 3 |
| 1 | 2 | 6 | 1 |
| 2 | 2 | 6 | 1 |
| 2 | 2 | 12 | 1 |
| **3** | **2** | **18** | **1** |

After three shape steps exactly one pattern survives. All 18 calls are at distinct addresses and the two final shape equations are independent. Its mass is $q^{-2}(1+O(q^{-1}))$. Together with the discarded terms this gives the required collision estimate.

## Independent checks of the collision counts

There is a direct finite-field check at one shape step. Compare the keys of the two paths. If they agree, the collision probability is one. If they differ by $a,b,$ or $a+b$, two of the three points are interchanged between paths. The two endpoint shapes coincide exactly when the four distinct output points sum to zero, with probability $1/(q-3)$. For any other key difference the two input triples are disjoint. Given the first image triple there are $q-4$ translations disjoint from it, among $(q-3)(q-4)(q-5)$ possible second outputs. Thus for $q\ge8$ the unconditional collision probability after one shape step is

$$
\frac1q+\frac{3}{q(q-3)}+\frac{q-4}{q(q-3)(q-5)}.
$$

This agrees with the three rows of the enumeration at one step and equals $7/30$ at $q=8$. The certificate independently verifies $7/30$ by enumerating all $8!$ permutations with output-translation symmetry.

After **two** shape steps two paths have total collision probability $2q^{-2}+O(q^{-3})$. With three paths and the same two steps the program also checks through rank four. It finds one rank-four pattern with six distinct table addresses, three with twelve and one with eighteen. All lower ranks are absent. The resulting collision probability is $5q^{-4}+O(q^{-5})$.

For a uniform independent target shape let $Z$ count the two-key paths reaching it. Summing over independent paths with repetitions allowed and dividing by the $m$ target shapes gives $\mathbb EZ^j=(q^{2j}/m)\Pr[\text{all }j\text{ paths agree in shape}]$. Thus the first three ordinary moments tend to $1,2,5$. In particular the first three falling-factorial moments tend to $1,1,1$. This independently checks the calculation in the companion proof, whose program directly counts paths with pairwise distinct key tuples. [Three-round occupancy bounds and threshold theorem](TRIPLE_LOWER.md)
