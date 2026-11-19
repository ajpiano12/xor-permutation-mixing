# Problem 4 at small statistical distance

Page 5 of the project brief fixes **one public permutation** $P$ and draws a fresh uniform $n$-bit XOR key for each round. The target is the largest total variation distance over **all ordered distinct input tuples**. It asks for a simple condition on a given $P$ and an explicit round count, first for pairs and then, if possible, for three or more inputs. It welcomes restricted families. The brief sets no numerical error threshold. Our main finite benchmark is $2^{-128}$, with $2^{-32}$ and $2^{-64}$ as intermediate measurements. We also study $\epsilon=2^{-n}$ as the width grows.

## Which ideas answer the question?

| Direction | What we can check | What it gives at $2^{-128}$ |
| --- | --- | --- |
| One repeated block update and rotation | From block width and an irreducible field polynomial, verify a compact construction without enumerating its table. On a supplied table, count deviations and include them in the bound. | The same 128-bit permutation certifies 65 full rounds on triples and 81 on quadruples. [Construction and proof](SPECTRAL_CERTIFICATE.md) |
| Rotate after a polynomial block update | A 12-bit update works with any degree-15 control polynomial over the specified field. | On 128 bits, 89 rounds suffice for every quadruple. The monomial uses two field multiplications and three squarings per update. [Proof and prior work](POLYNOMIAL_UPDATE.md) |
| Low-degree field powers for pairs | From $n,d$ alone, bound the rate for a specified power permutation. A table comparison also certifies perturbed powers. | On 128 bits $x^7$ takes at most five rounds, even after up to $2^{62}$ changes. Field inversion takes exactly four. [Character bound and exact verifier](POWER_CERTIFICATE.md) |
| Field powers at higher order | Check the exponent to decide eventual mixing for all orders. At small widths, group symmetries reduce the exact worst-start calculation. | Cubing at five bits needs 66 rounds on triples and 67 on quadruples. At three bits it needs 129 and 258. A useful large-width rate for cubing on quadruples remains open. [Classification and measurements](STRUCTURED_SMALL_ERROR.md) |
| All three-bit tables | Enumerate the 20 symmetry classes with exact integer path counts, retaining their full labeled multiplicities. | Two equally large families that tie at $1/4$ on triples need 88 and 129 rounds. A signed orientation statistic explains why the latter retains information longer. [Census and explanation](SMALL_ERROR_DATA.md) |

The **block update and rotation** is the strongest candidate for a paper. For sufficiently large $n$ and $2\le t\le n/2-1$, choose the block width for the largest tuple order of interest. The same public permutation then gives $O(t(1+\log_2(1/\epsilon)/n))$ rounds. In particular $O(t)$ rounds suffice at $\epsilon=2^{-n}$, where counting key sequences already requires at least $t$ rounds. The construction uses an inverse on part of the state. The published lower bound for the repeated inverse on the *entire* state concerns a different permutation. [Proof, finite constants and prior work](SPECTRAL_CERTIFICATE.md) · [Jain et al.](https://eprint.iacr.org/2024/1795)

For the 16-bit inverse update we can now bracket the true four-input mixing time between 10 and 81 rounds. Analyzing two consecutive translated updates together could narrow that interval. The polynomial proof offers a second direction. Its sufficient condition can be read from the leading degree alone. Using more of the formula may certify cheaper updates. Cubing the whole word at odd widths gives an independent benchmark for these approaches. [Ranked research directions and closest papers](LITERATURE_REVIEW.md#outstanding-work)

## Why exact independence fails, and a precision-dependent lower bound

Write $N=2^n$. With $r$ finite rounds, each ordered output pair has probability an integer multiple of $1/N^r$. Under a uniform random permutation its probability is $1/[N(N-1)]$. For $n\ge2$ the odd factor $N-1>1$ cannot divide a power of two, so exact pairwise independence is impossible for every $P$.

There is also a quantitative obstruction. One pairwise difference step samples the $N/2$ unordered pairs $\{x,x+a\}$ uniformly, because the two endpoints have the same output difference. After $r$ full cipher rounds the pair TV equals difference TV after $r-1$ steps. Thus this difference law has counts with denominator $D=(N/2)^{r-1}$ on $m=N-1$ states. Write $j=D\bmod m$. Giving each state either $\lfloor D/m\rfloor$ or $\lceil D/m\rceil$ counts minimizes distance to uniform: moving one count from an overfilled state to an underfilled one cannot increase the sum of absolute deviations. The minimum is $j(m-j)/(mD)$. Here $1\le j<m$, so every table has TV at least $(1-1/m)/D$. In particular $\epsilon=2^{-\lambda}$ with integer $\lambda\ge1$ requires

$$ r\ge 1+\left\lceil\frac{\lambda}{n-1}\right\rceil. $$

This gives at least 65 rounds on three bits and 20 on eight bits at $2^{-128}$, before considering the structure of $P$. At every higher tuple order the pair marginal gives the same necessary condition. The counting proof is elementary. The stronger construction-specific upper and lower bounds above distinguish what actually happens.

## Where publication priority stands

The published record covers shifted inverse sums with the precise constant used here, translated powers observed through a trace bit, and the use of degree 15 in a keyed Feistel round. The remaining priority question concerns the worst-start bounds obtained by reusing each specified formula with fresh independent XOR keys. The literature review records the assumptions of the closest theorems. [Source-by-source comparison](LITERATURE_REVIEW.md#prior-work-on-the-explicit-four-input-constructions) · [Niederreiter and Winterhof](https://matwbn.icm.edu.pl/ksiazki/aa/aa93/aa9346.pdf) · [Makhul and Winterhof](https://link.springer.com/article/10.1007/s40993-022-00335-8) · [MiMC](https://eprint.iacr.org/2016/492)
