# Four rounds are typically necessary for triples at TV 1/4

Draw one uniform permutation $P$ on $q=2^n$ bit strings and apply the same $P$ after a fresh uniform XOR key in every round. **At every fixed total variation threshold $0<\epsilon<1/3$, the worst-start ordered-triple mixing time is exactly four rounds with probability tending to one.** For $1/2<\epsilon<1$ it is exactly three. The behavior between these two ranges, including the endpoints, remains open. These conclusions combine a computer-assisted calculation after three rounds with the four-round upper bound. Published priority for the random-table result remains unverified. [Four-round proof](TRIPLE_MOMENT.md)

## Two keys leave empty cells

A triple up to translation has a shape given by its two differences from one designated point. There are $m=(q-1)(q-2)$ shapes. Write $D_s(P)$ for the distance to uniform after two shape steps starting from shape $s$. This equals the distance on actual ordered triples after three cipher rounds. The final uniform key spreads the first point uniformly within its shape, and the final application of $P$ preserves total variation. [Reduction to shapes](HIGHER_CENSUS.md)

For fixed $P,s$ there are $L=q^2$ equally probable ordered two-key paths. Independently choose a uniform target shape $Y$ and let $Z$ count the paths ending there. Write $M_s(P)$ for the fraction of missing shapes, so $\Pr(Z=0\mid P,s)=M_s(P)$. The integer counts constrain TV. When $q\ge8$, $1<L/m<2$. A missing target contributes $1/m$ to the total deficit from uniform. A target hit exactly once contributes $1/m-1/L$. Every other target contributes zero to the deficit. Consequently

$$0\le D_s(P)-M_s(P)\le 1-m/L=O(1/q).$$

Write $(z)_j=z(z-1)\cdots(z-j+1)$. We will prove that, for $j=1,2,3$,

$$\mathbb E_{P,Y}[(Z)_j]=1+O(1/q).$$

The alternating truncations of inclusion–exclusion (Bonferroni inequalities) give

$$1-Z+\binom Z2-\binom Z3\ \le\ \mathbf1_{Z=0}\ \le\ 1-Z+\binom Z2.$$

Taking expectations gives $1/3-O(1/q)\le\mathbb E D_s(P)\le1/2+O(1/q)$. This controls TV directly through the missing mass without an assumption of independent paths.

## Computing the factorial moments

Choose $j$ independent uniform key pairs and run their paths from one starting triple. Let $E_j$ be the event that the key pairs are pairwise distinct and their endpoints have the same shape. Summing over the $L^j$ ordered choices of key pairs gives

$$\mathbb E_{P,Y}[(Z)_j]=\frac{q^{2j}}{m}\Pr(E_j).$$

The factor $1/m$ is the chance that the independent target equals the common endpoint. For $j=1$, this already gives $q^2/m$. For $j=2,3$, the following finite enumeration gives

$$\Pr(E_j)=q^{-2(j-1)}(1+O(1/q)).$$

Represent the starting triple as $(0,a,b)$ for two fixed independent binary vectors. Any other triple reduces to this one by translation and a linear change of coordinates. Conjugating a uniform $P$ preserves its law. Evaluate all six calls to $P$ on each path, retaining the input addresses and replies shared across all paths. Each address is a key XOR either an initial point or a previous reply.

Consider one exact pattern of equal addresses with $k$ distinct addresses. Give their outputs $k$ variables. Past addresses coincide precisely as prescribed and the $k$ outputs must be distinct. Add the two vector equations per further path that equate its endpoint differences to the first path's. For every pair of paths, require at least one of its two keys to differ. Given an assignment satisfying these conditions, a uniform table realizes the assigned outputs with probability $1/(q)_k$. The keys contribute $q^{-2j}$, even when their later query addresses depend on earlier replies. The exact contribution of the pattern is the number of admissible assignments divided by $q^{2j}(q)_k$.

Let $e$ be the rank of the vector equations in the $2j+k$ variables. In a consistent pattern their solution space has $q^{2j+k-e}$ points. A nonzero linear combination of $a,b$ cannot be forced to zero. Any required inequality between addresses or outputs either holds identically, is impossible, or rules out just a $1/q$ fraction. Identical key pairs require **both** component equalities. If both are forced, discard the pattern. Otherwise the forbidden joint event is empty or lies inside a proper affine subspace of relative size at most $1/q$. There are finitely many restrictions, so a consistent pattern has weight $q^{-e}(1+O(1/q))$ as $q$ grows.

The checker searches the exact patterns as follows.

1. Encode each key, reply, and the constants $a,b$ by distinct bits. Keep the full binary linear span of all imposed equations. It contains at most 16 expressions for $j\le3$ through the required rank $2(j-1)$. An address equality is forced precisely when its XOR belongs to the span.
2. A forced repeated address reuses its unique value. Otherwise branch on a hit to each distinct earlier address and one fresh address. The fresh branch records all inequalities that distinguish its input and output from earlier ones. These cases are exhaustive and disjoint.
3. Add the two endpoint equations of each subsequent path as soon as the corresponding replies are available. After extending the equation span, reject a contradictory constant, a violated inequality, or a forced identical key pair. Further equations and fresh variables cannot lower the existing rank.
4. Count terminal paths through rank $2(j-1)$. All higher-rank terminal paths combined contribute $O(q^{-2(j-1)-1})$ because the number of equality patterns of at most 18 calls is a fixed constant.

| Distinct two-key paths | Surviving rank | Distinct addresses | Surviving patterns |
|---:|---:|---:|---:|
| 2 | 2 | 12 | 1 |
| 3 | 4 | 18 | 1 |

At each order the unique surviving pattern has distinct addresses throughout. This proves the probability estimate and all three factorial moment identities. An independent computation allowing repeated key pairs gives limiting ordinary moments $1,2,5$, agreeing with the factorial moments. The standard-library certificate reproduces the table. [Enumeration code](triple_lower.py)

    uv run --locked research/triple_lower.py

## From one start to every start

Transposing two images of $P$ changes a one-step shape row in TV by at most $6/q$. Only keys bringing one of the three points to one of the exchanged inputs can affect the row. A coupling over two steps therefore bounds the change of $D_s(P)$ by $12/q$. Expose the uniform permutation one image at a time. Completions for two possible images can be paired by one transposition. Azuma's inequality bounds the two-sided tail at distance $t$ from the mean by $2\exp(-qt^2/288)$. A union bound over the $m$ starting shapes now gives, simultaneously for all $s$,

$$\frac13-O_K\!\left(\sqrt{\frac{\log q}{q}}\right)
\le D_s(P)\le
\frac12+O_K\!\left(\sqrt{\frac{\log q}{q}}\right)$$

with probability $1-O_K(q^{-K})$ for every fixed $K>0$. After two full cipher rounds a starting triple has at most $q$ shapes in the corresponding one-step distribution, so its TV is at least $1-q/m$. After four full rounds the worst-start distance tends to zero with high probability. These facts give the stated threshold times. At any fixed threshold strictly inside either range, the same concentration estimates with constant $t$ give an exponentially small exceptional probability. [Four-round concentration](TRIPLE_MOMENT.md)
