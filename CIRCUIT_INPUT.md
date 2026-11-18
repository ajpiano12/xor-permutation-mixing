# The cost of deciding whether a permutation mixes

Suppose an input circuit computes a permutation $P$ of $n$-bit strings.
Deciding whether its XOR-difference chain converges to uniform from every
nonzero starting difference is **NP-hard**, even when an inverse circuit is
also supplied. With an explicit table, the graph can be built in
$O(2^{2n})$ table lookups, polynomial in the table length. A circuit
can describe the same table much more compactly.

## Reduction from satisfiability

Given a Boolean formula $F$ on $m$ variables, use $n=m+3$ bits
$x=(x_0,x_1,x_2,y)$, where $y$ has $m$ bits. Let $R$ rotate the $n$
coordinates one place to the left. Define $f(x)=1$ exactly when
$x_1=x_2=0$ and $F(y)=1$. Let $e_0$ be the first unit vector and set

$$
H(x)=x\oplus f(x)e_0,\qquad P(x)=R(H(x)).
$$

The function $f$ ignores $x_0$, so $H$ is its own inverse.
Both $P$ and $P^{-1}=H\circ R^{-1}$ have circuit size $O(|F|+n)$.
If $F$ is unsatisfiable, $P=R$. Every difference then rotates
deterministically, preserving its Hamming weight. The chain is disconnected.

Suppose $F$ is satisfiable. The difference graph contains an edge
$a\to b$ whenever some $x$ satisfies $P(x)\oplus P(x\oplus a)=b$.
Two kinds of edges suffice.

1. **Rotation.** For every $a\ne0$, some $x$ has
   $f(x)=f(x\oplus a)=0$. The support of $f$ and its translate each cover
   at most a quarter of the domain. This gives the edge $a\to Ra$.
2. **Flip followed by rotation.** When $a_1=1$, take $x$ with
   $x_1=x_2=0$ and $y$ a satisfying assignment. Then $f(x)=1$ and
   $f(x\oplus a)=0$, giving $a\to R(a\oplus e_0)$.

Follow the second edge with $n-1$ rotation edges. This gives a path
that toggles bit 0 whenever bit 1 is set. Rotating before and after this
path lets any set bit toggle its predecessor, with indices taken cyclically.
Starting at a set bit of any nonzero difference, walk backwards around the
cycle and turn each zero encountered into a one. Thus every state can reach
the all-ones state. Each toggle leaves its controlling bit set, so each path
of toggles can be undone. The graph is strongly connected. Rotation fixes the
all-ones state, giving a self-loop and hence period one.

The chain is doubly stochastic because $P$ permutes ordered pairs of
distinct inputs. Strong connectivity and period one therefore give convergence
to uniform. We have a polynomial-time many-one reduction taking satisfiable
formulas exactly to mixing permutations. [Cook's satisfiability theorem](https://doi.org/10.1145/800157.805047)

## Exact query bound for a black-box permutation

For $n\ge3$, a deterministic exact tester needs **$2^n-1$ evaluations**
in the worst case. Set $q=2^n$. Over the field of order $q$, multiplication
by a generator of the multiplicative group gives a linear map $L$ that cycles all $q-1$ nonzero
differences. Its chain is periodic. Swapping any two outputs of $L$ makes it
mix, as follows.

Write the modified permutation as $P=\tau\circ L$, where the transposition
$\tau$ exchanges two points differing by $\delta\ne0$. For an input
difference $a$, the two points before $\tau$ differ by $La$. At most four
choices of the first point touch either swapped point, so every edge
$a\to La$ survives. When $La\ne\delta$, choosing the first point to be
a swapped point changes the difference by $\delta$. The graph therefore
also contains $a\to La\oplus\delta$. The map $I+L$ is invertible because
$L$ fixes no nonzero point. Taking $a=(I+L)^{-1}\delta$ gives a self-loop
from this second edge, since $a\ne0$ and $La\ne\delta$. The surviving
cycle and this self-loop prove mixing.

On the oracle $L$, any two unqueried inputs could still have their outputs
swapped. An exact tester must query all but one input, and the permutation
promise then determines the last output. Bounded-error randomized testers
also require $\Omega(q)$ queries. Couple the oracle $L$ to a copy with a
uniformly random pair swapped. Until a query hits that pair the two
transcripts coincide, and the probability of a hit in $k$ queries is at
most $2k/q$.

In particular, a two-answer tester with worst-case error $\varepsilon<1/2$
must have $2k/q\ge1-2\varepsilon$. The two inputs need to produce different
answers with probability at least $1-2\varepsilon$. This bound holds even
if the queries are evaluated in parallel. It concerns point evaluations.
A known circuit exposes additional structure to a proof.

## Screening for invariant parities

Large permutations are often supplied as an algorithm, Boolean circuit or
callable that computes one image at a time. For example, fixing an AES key
specifies a permutation on 128-bit blocks, compactly represented by its round
transformations and key schedule. A public unkeyed design such as the
320-bit Ascon permutation is also specified by layers of operations on words.
In the pairwise experiment the chosen permutation is fixed across rounds,
while the experiment supplies fresh common XOR keys. [NIST AES standard](https://csrc.nist.gov/pubs/fips/197/final) · [Ascon designers' permutation specification](https://ascon.isec.tugraz.at/specification.html)

For $n\ge2$, seek a nonzero mask $m$ such that

$$m\cdot P(x)=m\cdot x\ \oplus\ m\cdot P(0)\quad\text{for all }x,$$

where the dot product is binary parity. Such a mask preserves the parity
of every difference through every round. The nonzero differences with
$m\cdot a=0$ form a nonempty proper closed set, proving disconnection.
Define $v(x)=P(x)\oplus x\oplus P(0)$. The allowed masks form the
orthogonal complement of the span of the $v(x)$. Binary elimination therefore
finds **all** invariant hyperplanes in one table scan using $O(nN)$
word operations in total and $O(n)$ words for the basis (each $n$ bits).
Full rank rules out every such mask immediately. The six-bit block-swap
example shows that other obstructions can remain. [Implementation](parity_screen.py) ·
[Six-bit counterexample](LARGER_BITS.md#a-six-bit-counterexample)

On a callable, use the same elimination on $k$ independent uniform
nonzero inputs and the anchor $P(0)$. For a mask whose equation fails on
at least a $\delta$ fraction of *all* inputs, the chance of passing is at
most $(1-\delta)^k$. Zero always satisfies the equation, so sampling
nonzero inputs only improves the bound. A union bound over all nonzero
masks gives at most $(2^n-1)e^{-k\delta}$ for **any** such mask to survive.
Thus $k\ge(n\ln2+\ln(1/\varepsilon))/\delta$ suffices, and genuine invariant
masks survive every sample. A surviving candidate can have rare exceptions.
This error bound concerns the parity identity. The general black-box lower
bound above applies to deciding mixing itself.

Given a circuit and a candidate $m$, ask a Boolean satisfiability solver
whether there exists an $x$ with $m\cdot v(x)=1$. A satisfying assignment
discards the candidate and an unsatisfiability proof certifies nonmixing.
One can similarly verify a proposed proper subspace $W$ with basis $w_i$.
Search for $x,i$ with $P(x)\oplus P(x\oplus w_i)\notin W$.
If the formula is unsatisfiable, telescoping the basis shifts proves closure
for every $w\in W$. Solver runtime depends on the circuit. The Python
screen implements the elimination and sampling steps.
