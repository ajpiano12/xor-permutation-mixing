# The sharp three-round rate for inverse triples

Let $N=2^n\ge4$ and let $I$ be the field inverse on $\mathbb F_N$, with $I(0)=0$. For **every** ordered triple $X$ of distinct field elements, the total variation distance $d_X$ after three independently keyed rounds of this same permutation satisfies

$$
\frac7N-\frac{12}{N^2}-\frac{64}{(N-1)(N-2)}
\ \le\ d_X\ \le\ \frac7N-\frac{12}{N^2}.
$$

In particular $Nd_X\to7$ uniformly over starting triples. At eight bits, $Nd_X$ ranges from about $6.779$ to $6.856$. The simpler upper certificate also applies to permutations that differ from the inverse on $h$ entries, with an additional $6h/N$ in TV. The sharp leading coefficient here concerns the exact inverse. [Three-round certificate and perturbation proof](TRIPLE_ROUNDS.md)

## Count the generic shapes

Drop the final deterministic inversion, which preserves distance to uniform. The remaining permutation is $T_c I T_b I T_a$, where $T_a(x)=x+a$ and $a,b,c$ are independent uniform field elements. The last translation gives a uniform first coordinate conditional on the *shape*, the two differences from that coordinate. Therefore $d_X$ equals the TV distance on $S=(N-1)(N-2)$ shapes, sampled with $K=N^2$ equally likely key pairs $(a,b)$.

For $b\ne0$, write $u=1/b$, $v=a+u$, and $t=c+u$. Direct substitution gives the field permutation

$$
x\longmapsto
\begin{cases}
t+u, & x=v,\\
t, & x=v+u,\\
t+u^2/(x+v), & x\notin\{v,v+u\}.
\end{cases}
$$

The free output translation $t$ disappears from the shape. Call $(v,u)$ generic for $X$ when both exceptional inputs miss $X$. There are $G=(N-3)(N-4)$ such key pairs. They produce $G$ distinct shapes. Indeed, any specified pair of ordered triples of distinct projective points determines a unique fractional linear interpolant. Two identical shapes differ only by an output translation, which preserves both the pole $v$ and the nonzero coefficient $u^2$. Squaring is bijective in this field. Each generic shape has probability at least $1/K$, which is below the uniform mass $1/S$. Thus the overlap with uniform is at least $G/K$, giving $d_X\le 1-G/K$.

## At most 43 more shapes are occupied

For distinct finite inputs $x_0,x_1,x_2$ and distinct finite outputs $y_0,y_1,y_2$, put

$$s_{ij}=(y_i+y_j)/(x_i+x_j).$$

The unique projective interpolant is affine precisely when $s_{01}=s_{02}$. Otherwise it has the form $t'+u'^2/(x+v')$, with $u'\ne0$. Its pole $v'$ misses all three inputs since their outputs are finite. The interpolant represents a generic shape unless $x_i=v'+u'$ for some $i$. Dividing the pairwise output differences gives

$$
s_{ij}=\frac{u'^2}{(x_i+v')(x_j+v')},\qquad
D_i:=\frac{s_{ij}s_{ik}}{s_{jk}}=\frac{u'^2}{(x_i+v')^2}
\quad (\{i,j,k\}=\{0,1,2\}).
$$

Thus a shape outside the generic set must satisfy at least one of four tests, namely $s_{01}=s_{02}$ or one of $D_0,D_1,D_2$ equals $1$.

If exactly one exceptional point hits $X$, reorder and translate inputs so that $X=(0,A,B)$, with $0$ the exceptional input and $0,A,B$ distinct. This sends $v$ to its translated value and preserves $u$. Take $t=0$. In both cases below $u\notin\{0,A,B\}$, by the single-hit condition.

| Exceptional input | Output triple | $s_{01}$ | $s_{02}$ | $s_{12}$ |
|---|---|---|---|---|
| $v=0$ | $(u,u^2/A,u^2/B)$ | $u(u+A)/A^2$ | $u(u+B)/B^2$ | $u^2/(AB)$ |
| $v+u=0$ | $(0,u^2/(A+u),u^2/(B+u))$ | $u^2/[A(A+u)]$ | $u^2/[B(B+u)]$ | $u^2/[(A+u)(B+u)]$ |

In the first row, equating the first two slopes gives a linear equation in $u$ after cancellation, with nonzero leading coefficient because $A\ne B$. Also $D_0=(u+A)(u+B)/(AB)$, so $D_0=1$ has at most one nonzero solution. For $D_1=1$ the equation is $B u^2(u+A)=A^3(u+B)$, a nonzero cubic. Exchanging $A,B$ gives the corresponding cubic for $D_2$. These four tests cover at most $1+1+3+3=8$ exceptional parameter values.

In the second row, equality of slopes gives $u=A+B$, while $D_0=1$ gives $u^2=AB$. The equation $D_1=1$ is $B u^2=A(A+u)^2$, or $(A+B)u^2=A^3$. Exchanging $A,B$ gives $D_2=1$. Each equation has at most one root, so this row contributes at most four more.

There are three choices of the single exceptional input, at most six ordered choices for two hits $(v,v+u)$ within $X$, and a single shape from $b=0$ because then $I I$ cancels and the finite map is a translation. Altogether at most $3(8+4)+6+1=43$ shapes outside the generic set can receive positive mass.

## Bound the overlap from above

The $K-G$ nongeneric key pairs can increase the overlap on the original $G$ shapes by at most $(K-G)(1/S-1/K)$. Each of those shapes starts with at least $1/K$ mass, and one hit from another key pair suffices for this upper bound on its additional contribution. The at most 43 other occupied shapes contribute at most $43/S$. Since $K-G=7N-12$ and $K-S=3N-2$, the overlap is at most $G/K+64/S$. Subtracting from one proves the stated lower bound.

The same argument gives an exact algorithm for one starting triple using $O(N)$ field operations and $O(N)$ storage. Generate only the $7N-12$ nongeneric key pairs, recording each output shape and its multiplicity $m$. Start with overlap $G/K$. For each recorded shape use the four tests above to decide whether it is generic. If it is, add $\min\{(1+m)/K,1/S\}-1/K$. Otherwise add $\min\{m/K,1/S\}$. Subtract the resulting overlap from one. Equal shapes can be grouped by hashing in expected linear time or by sorting in $O(N\log N)$ comparisons. The numerical check below instead enumerates all key pairs as an independent verification.

## Finite checks

Scaling inputs by a nonzero field element scales inverses by its reciprocal, and the independent translations can be scaled accordingly. Thus translating the first input to zero and scaling the second to one leaves just $N-2$ triples $(0,1,r)$ to check. These are exact worst-start distances for the inverse.

| Bits | Worst three-round TV | $N$ times worst TV |
|---:|---:|---:|
| 5 | $3347/19840$ | 5.3984 |
| 6 | $827515/7999488$ | 6.6205 |
| 7 | $482701/9363456$ | 6.5986 |
| 8 | $14210611/530595840$ | 6.8563 |

From the repository root, the following calculation enumerates both difference steps and checks the bounds for every starting class from two through eight bits.

```sh
uv run --locked --extra four-bit python - <<'PY'
from fractions import Fraction
import numpy as np
from inverse_triples import field_inverse_table

for bits, modulus in [(2, 7), (3, 11), (4, 19), (5, 37),
                      (6, 67), (7, 131), (8, 283)]:
    size = 1 << bits
    table = np.asarray(field_inverse_table(size, modulus))
    x = np.arange(size)
    difference = table[:, None] ^ table[x[:, None] ^ x]
    states = (size - 1) * (size - 2)
    generic = (size - 3) * (size - 4)
    upper = 1 - Fraction(generic, size**2)
    distances = []
    for r in range(2, size):
        first = difference[:, difference[:, 1]]
        second = difference[:, difference[:, r]]
        labels = (size * first + second).ravel()
        counts = np.bincount(labels, minlength=size**2)
        overlap = int(np.minimum(counts * states, size**2).sum())
        distance = 1 - Fraction(overlap, states * size**2)
        assert upper - Fraction(64, states) <= distance <= upper
        assert generic <= np.count_nonzero(counts) <= generic + 43
        distances.append(distance)
    print(bits, min(distances), max(distances))
PY
```

**Attribution.** The projective interpolation and the representation of compositions of patched inversions by fractional linear maps with exceptional inputs are established. The uniform sharp marginal coefficient and the bound on additional occupied shapes are project derivations. Publication priority for these specific statements remains unverified. [Aksoy et al., *On the Carlitz rank of permutation polynomials*](https://doi.org/10.1016/j.ffa.2009.02.006) · [Ding, *Connecting two types of representations of a permutation*](https://arxiv.org/abs/2103.09064) · [Jain et al., *How Fast Does the Inverse Walk Approximate a Random Permutation?*](https://eprint.iacr.org/2024/1795)
