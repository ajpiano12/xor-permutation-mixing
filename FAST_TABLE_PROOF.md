# A nearly linear randomized filter for pairwise mixing

Let `P` be a table of $N=2^n$ images, with $n\ge1$, and fix an error budget
$0<\varepsilon<1$. There is an algorithm with the following guarantees for
**each fixed input table**, over the algorithm's independent random choices.

- Every table reported as **mixing** really mixes.
- A mixing table is reported as mixing with probability at least $1-\varepsilon$.
- The worst-case cost is $O(N n^4\log(Nn/\varepsilon))$ word operations and
  $O(N)$ working words. The Python implementation batches the probability
  checks using $O(n+\log(1/\varepsilon))$-bit integers. Repeating them with
  single-bit weights gives the same time bound with $O(n)$-bit transform
  arithmetic, as shown below.

One can interpret the other answer as *unresolved*, use it as a one-sided
Monte Carlo prediction of nonmixing, or run the deterministic classifier on
the unresolved inputs for an exact decision. In the last mode the worst-case
fallback still takes quadratic time. The guarantee addresses classification
and places no bound on the mixing time.

## What suffices to certify mixing

An ordered pair of table inputs $(x,y)$ gives a directed edge

$$a=x\oplus y \ \longrightarrow\ b=P(x)\oplus P(y).$$

The vertices of interest are the $N-1$ nonzero differences. Pairs with $x=y$
give the auxiliary edge $0\to0$ and can be ignored. The chain is an average
of permutations, so weak connectivity implies strong connectivity, and
the uniform law on differences is stationary. To certify mixing, we can
exhibit a spanning tree of real edges with directions retained, then prove
that the full graph has period one. One bit is immediate because its graph
has just one vertex. [Difference-chain proof](LARGER_BITS.md#deciding-pairwise-mixing-from-a-truth-table)

First, the implementation samples up to three inputs $x$ and searches just
the edges supplied by those inputs. Each fixed $x$ permutes the differences.
If the sampled support is already connected and aperiodic, all its connecting
paths and cycles are still present in the full graph, which therefore mixes.
Otherwise its edges seed the forest. This initial test costs $O(N)$ time.

## Finding a crossing edge for many components at once

Signed sums for recovering crossing edges also appear in graph sketching.
Here the two ends of each edge are XOR differences, which lets the table
produce all the signed sums through convolutions. [Ahn, Guha and McGregor,
*Analyzing Graph Structure via Linear Measurements*](https://people.cs.umass.edu/~mcgregor/papers/12-dynamic.pdf)

Maintain a forest. A *crossing pair* for a tree component $S$ is a pair
$(x,y)$ whose edge has exactly one endpoint in $S$. Given two subsets $X,Y$
of the table inputs, consider all ordered pairs in the rectangle $X\times Y$.
For each component $S$, compute three signed sums over these pairs, using
the weights $w(x,y)=1,x,y$ respectively. The summand is

$$w(x,y)\bigl(\mathbf1_S(x\oplus y)-\mathbf1_S(P(x)\oplus P(y))\bigr).$$

Pairs internal or external to $S$ cancel individually. If precisely one pair
crosses the cut, the three results are $s,sx,sy$ for a sign $s\in\{-1,1\}$.
Whenever the first value is $\pm1$, recover the candidate $x,y$ by division.
Check that both are in range and use the table to check that their edge crosses
the cut. A collision of several pairs can also suggest a candidate, but this
last check ensures that only genuine crossing edges enter the forest.

The three signed sums are computable for *all components together* in
$O(Nn)$ time. For an XOR convolution write

$$(A*B)(a)=\sum_x A(x)B(x\oplus a).$$

With $A=\mathbf1_X$ and $B=\mathbf1_Y$, one convolution counts all pairs in
the rectangle by input difference. Replacing each input array $U$ by
$U\circ P^{-1}$ gives the counts by output difference. Subtract these two
arrays and aggregate their entries by component. For the endpoint moments,
repeat after multiplying the relevant input array by its input index, before
reordering. A fast Walsh–Hadamard transform computes each convolution in
$O(Nn)$ additions, subtractions and multiplications. Indeed each Walsh
character $\chi_u(x)=(-1)^{u\cdot x}$ satisfies
$\chi_u(x\oplus y)=\chi_u(x)\chi_u(y)$, so the transform of a convolution
is the coordinatewise product of the transforms. Applying the same transform
again and dividing by $N$ recovers the convolution. Each of the $n$ bit
positions contributes one stage of $N/2$ independent sum-and-difference
operations. The integer intermediates for these cut sums are polynomially
bounded in $N$, so $O(n)$-bit words suffice.

## Why the sampled rectangles find even a rare edge

A pass tries inclusion probabilities $2^{-i},2^{-j}$ for $0\le i,j\le n$.
At level $i$, include each first input independently in $X$ with probability
$2^{-i}$. Keep this $X$ while trying all second-input levels $j$. For each
$j$, sample $Y$ independently of $X$, including each second input with
probability $2^{-j}$. The rectangles can be processed one at a time.

Fix a component with at least one crossing pair. Let $k$ be the number of
first inputs $x$ that occur in such a pair. Some level gives a probability
$p$ in $[1/(2k),1/k]$. Exactly one of these $k$ inputs is selected with
probability $kp(1-p)^{k-1}\ge1/4$. Indeed this expression increases up
to $p=1/k$, and at $p=1/(2k)$ Bernoulli's inequality gives the bound.
Conditioned on the unique selected first input, apply the same argument
to its number of crossing second inputs. The appropriate second level
selects exactly one of them with probability at least $1/4$. Thus one pass
discovers a genuine crossing edge for this component with probability at
least $1/16$, regardless of how sparse the cut is.

Freeze the component labels at the start of each phase. Run independent
passes to find one outgoing undirected edge per component that has one.
Merge along these edges, retaining the directed witnesses when joining
distinct components. On a connected graph, a phase finding an edge for
every component at least halves the component count when it exceeds one.
After at most $n$ such phases the forest spans the full graph. In a
disconnected graph the same argument applies inside each true component.
It is enough to stop a phase as soon as its component count has halved.
It is also safe to return unresolved if a phase exhausts its budget before
the count halves. An implementation can warm-start with any verified edges.
Each success is still backed by actual directed edges. A premature stop can
send a mixer to the unresolved set.

There are at most $Nn$ cut tests over the phases. Conditional on all previous
phases, the chance to miss a specified nonempty cut in $r$ fresh passes is
at most $(15/16)^r$. A union bound applies even though earlier phases and
their edges determine the later cuts.

## Certifying the period without enumerating the remaining edges

Take the spanning tree and assign integer heights $h$. Give its root height
zero, add one when traversing a tree edge in its recorded direction, and
subtract one in the other direction. For any directed graph edge $a\to b$
put $z(a,b)=h(a)+1-h(b)$. The period $d$ is exactly the gcd of the $|z(a,b)|$.
To see this, the signed expressions sum to the length around every directed
cycle. Conversely, directed distances from the root are well defined modulo
$d$ because two directed paths to a vertex can be closed with the same return
path. Every edge advances this residue by one. The tree heights obey these
same congruences, so $d$ divides every $z(a,b)$.

Each of the $d$ cyclic classes has equal stationary mass because every step
passes its mass to the next class. The stationary law is uniform, so $d$
divides $N-1$. Initialize $g=N-1$. Each time a real edge has $g\nmid z(a,b)$,
replace $g$ by $\gcd(g,|z(a,b)|)$. The true period still divides $g$.
Reaching $g=1$ on a connected graph certifies mixing. Every strict update
at least halves $g$. A disjoint-set forest that tracks relative heights can
maintain this gcd while edges are inserted. Joining two components adds a
constant to the heights in one tree, preserving all previous within-tree
discrepancies. An edge within a tree supplies a discrepancy immediately.

For $g>1$, define $A(a)=(h(a)+1)\bmod g$ and $B(b)=h(b)\bmod g$ on the
nonzero differences. Set $A(0)=B(0)=0$. A random probe independently draws
a fair bit $r(y)$ for each table input and computes all fingerprints

$$E(x)=\sum_y r(y)\bigl(A(x\oplus y)-B(P(x)\oplus P(y))\bigr).$$

These are again two XOR convolutions, the second using $r\circ P^{-1}$ and
then evaluating the result at $P(x)$. If $E(x)\ne0$, scan that row to find
an actual violated congruence and update $g$. If any edge violates the
congruence, select one such $(x,y)$ for the proof. Conditional on all other
bits, at most one value of $r(y)$ can make $E(x)$ zero because its coefficient
is nonzero. Thus a probe detects some violation with probability at least
$1/2$. More generally, drawing each coordinate independently and uniformly
from $\{0,\ldots,2^b-1\}$ gives miss probability at most $2^{-b}$.
If the candidate is valid, every probe is identically zero.

The same fingerprint accelerates connectivity. For a proposed partition,
take $A(a)=B(a)$ equal to the integer label of its component and set
$A(0)=B(0)=0$. A nonzero row exposes a real edge between two components.
One can add every directed edge at the exposed first input $x$ by scanning
the $N$ second inputs. If all fingerprints vanish while more than one
component remains, returning unresolved costs at most $2^{-b}$ in
false-exclusion probability on a connected graph. The cyclic-color
probe likewise permits adding a whole exposed row.

## Algorithm and error budget

```text
start with isolated differences and add verified edges at sampled first inputs
for up to n phases, while multiple components remain:
    optionally try a partition fingerprint, adding a whole row if it exposes one
    use independent rectangle passes with frozen component labels as needed
    after the first full pass, optionally probe the current partition again
    merge verified crossing edges until the count at label-freeze time has halved
    if the phase exhausts its budget first, return unresolved
if the forest does not span all differences, return unresolved
take g from the forest, initialized to N - 1 and updated with witnessed edges
while g exceeds one:
    test the cyclic colors for g with an independent fingerprint
    if no violation was found, return unresolved
    add the exposed row, updating g from its real edges
return certified mixing
```

For an error target $\varepsilon=2^{-e}$, a conservative pass limit per
phase is $r=16(e+n+\lceil\log_2(n+1)\rceil+2)$. Since
$(15/16)^r\le \exp(-r/16)\le 2^{-r/16}$, the $Nn$ cut tests together
cost at most $\varepsilon/4$ in false-exclusion probability. For each
partition or cyclic-color fingerprint take $b=e+\lceil\log_2(3n+4)\rceil+1$.
There are at most $2n$ phase partition checks and at most $n+1$ period
checks. With fresh coordinates at each check their combined miss bound
is at most $\varepsilon/2$, including room for preliminary checks. Thus
the chance that a mixing input is unresolved is at most $\varepsilon$.
The implementation uses integer bit lengths, which can round these limits
up by one at powers of two. Scanning sparse rectangles with at most $N$
pairs recovers every edge in that rectangle within $O(Nn)$ time including
disjoint-set updates.
Any smaller work budget still preserves the guarantee that every reported
mixer is genuine, with the false-exclusion bound adjusted to that budget.

There are at most $n$ phases of $(n+1)^2$ rectangles per pass, each costing
$O(Nn)$ word operations. Batched fingerprints use $O(n+e)$-bit integers.
Equivalently one can take $b$ independent fair-bit probes per check to
retain the $O(n)$-bit arithmetic bound. Even with these repeated probes the
period stage costs only $O(Nn^2\log(Nn/\varepsilon))$ word operations.
Streaming transforms and retaining only a forest and component labels
uses $O(N)$ words. The polynomial in $n=\log_2 N$ and the constants matter
for small tables. Verified sparse edges can finish the decision before the
first expensive rectangle pass. The bounds use independent random bits.
