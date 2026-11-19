# A degree-15 update for four-input mixing

On 128 bits, a fixed public permutation built from the field map $z\mapsto z^{15}$ takes **every ordered quadruple** within total variation $2^{-128}$ of uniform after **89 rounds** with a 12-bit update. A 16-bit update gives **97 rounds**. Both are sufficient bounds for independent uniform XOR keys. Changing the update width changes the public permutation.

| Update width $b$ | Irreducible control-field modulus | Rounds for $2^{-32}$ | Rounds for $2^{-64}$ | Rounds for $2^{-128}$ |
| ---: | --- | ---: | ---: | ---: |
| 12 | $X^{116}+X^4+X^2+X+1$ | 23 | 45 | 89 |
| 16 | $X^{112}+X^5+X^4+X^3+1$ | 33 | 49 | 97 |

Both commands certify 89 rounds for four inputs at $2^{-128}$. The first uses $z^{15}$. The second uses $2z^{15}+3z^2+1$, where integers encode field elements in the specified polynomial basis. Supply the 16 coefficients from constant to leading. Add `--file` with a permutation table to count entries that differ from the specified construction and adjust the bound. [Verifier](spectral_certificate.py)

```sh
uv run --locked python -m research.spectral_certificate --bits 128 --block-bits 12 --order 4 --modulus 0x100000000000000000000000000017 --control power15 --error-bits 128
uv run --locked python -m research.spectral_certificate --bits 128 --block-bits 12 --order 4 --modulus 0x100000000000000000000000000017 --control polynomial15 --coefficients 1 0 3 0 0 0 0 0 0 0 0 0 0 0 0 2 --error-bits 128
```

## The public permutation

Write the low $b$ bits as $v$ and identify the other $n-b$ bits with $z$ in the polynomial basis of $\mathbb F_Q$, where $Q=2^{n-b}$ and $1\le b\le n/2$. Take the low $b$ coordinates for the binary linear projection $L$, or choose any surjective binary linear projection onto $b$ bits. XOR $L(z^{15})$ into $v$, then rotate the whole word right by $b$ bits. The update is its own inverse before rotation. To evaluate the power, compute $w=z^2z$ and then $w^4w$. This takes two field multiplications and three squarings.

## Why every set of four inputs satisfies the bound

In a layer translated by a fresh uniform mask, each distinct control $a_i$ gets the offset $L((u+a_i)^{15})$ for one common uniform $u\in\mathbb F_Q$. Simultaneous XOR by a common offset preserves all tuple differences. For $k$ distinct controls we can therefore subtract the first offset from each of the other $k-1$. Under the comparison layer that assigns independent uniform offsets to each control, these $k-1$ differences are independent and uniform. With only one distinct control the difference update is deterministic in both models. [Key translation and the difference walk](SPECTRAL_CERTIFICATE.md)

Consider any nonzero Fourier character of the $k-1$ relative offsets, with $2\le k\le4$. By the trace pairing, its value is $(-1)^{\operatorname{Tr}(H(u))}$, where

$$
H(X)=\sum_{i=1}^{j} c_i(X+a_i)^{15},\qquad 2\le j\le k,\qquad \sum_{i=1}^{j}c_i=0.
$$

Here the $a_i$ are the distinct controls carrying nonzero field masks $c_i$. The masks sum to zero because each relative offset uses the reference control once. Surjectivity of $L$ makes its dual injective, so a nonzero relative character has a nonzero field mask.

All binomial coefficients of exponent 15 are odd, since $15=1+2+4+8$. For $0\le h<j$, the coefficient of $X^{15-2h}$ in $H$ is therefore $\sum_i c_i(a_i^2)^h$. The Vandermonde matrix on the distinct $a_i^2$ is invertible. These $j$ coefficients cannot all vanish. The coefficient of $X^{15}$ does vanish since $\sum_i c_i=0$, so at least one of the coefficients in degrees 13, 11 or 9 survives.

The field trace satisfies $\operatorname{Tr}(eX^{2m})=\operatorname{Tr}(\sqrt e\,X^m)$ at every field element. Successively reduce every even power in $H$ by this identity. All resulting terms have degree at most seven when they come from an even power of $H$, so the surviving high odd coefficient persists. The reduced polynomial has odd degree between 9 and 13. The additive Weil bound gives

$$
\left|\mathbb E_u(-1)^{\operatorname{Tr}(H(u))}\right| \le \frac{12}{\sqrt Q}.
$$

The use of relative offsets saves two in the numerator because the degree-15 term cancels. Applying Parseval and Cauchy–Schwarz to the at most $B^3-1$ nonzero characters, where $B=2^b$, bounds the TV cost of one layer by $\eta=6\sqrt{B^3-1}/\sqrt Q$. [Additive Weil bound, Lemma 1](https://link.springer.com/article/10.1007/s40993-022-00335-8)

Set $N=2^n$, $d=\lceil n/b\rceil$, and $C=B$ when $b$ divides $n$, $C=B^2$ otherwise. The two-sweep proof bounds the distance after $1+2dm$ cipher rounds by $\delta(2\delta)^{m-1}$ for $\delta<1/2$, with

$$
\delta=\frac{6dC(B-1)}{N}+2d\eta .
$$

Rounding $\sqrt{B^3-1}$ upward gives $\delta<1.201\times10^{-10}$ at width 12 and $\delta<2.236\times10^{-8}$ at width 16. Four blocks of 22 layers and six blocks of 16 layers, respectively, suffice at $2^{-128}$. The extra round supplies the final independent common mask. [Two-sweep and contraction proof](SPECTRAL_CERTIFICATE.md)

## Published ingredients and the next question

Makhul and Winterhof's Theorem 1 already covers four arbitrary translates of $X^{15}$ observed through one fixed trace bit. Their proof uses the same binomial and Vandermonde argument. The calculation above allows a different field mask at each control as required by a multi-bit projection, and uses their sum-zero constraint. Gyarmati, Mauduit and Sárközy had earlier used weighted-translate Vandermonde equations for polynomial degree below the characteristic. Niederreiter and Winterhof's Theorem 1 supplies the analogous bound for the inverse map. [Makhul–Winterhof, §§3–4](https://link.springer.com/article/10.1007/s40993-022-00335-8) · [Gyarmati–Mauduit–Sárközy, §3, Lemma 3](https://publi.math.unideb.hu/paper/1674/download/10_5486_PMD_2012_5197.pdf) · [Niederreiter–Winterhof, Theorem 1](https://matwbn.icm.edu.pl/ksiazki/aa/aa93/aa9346.pdf)

Albrecht et al.'s MiMC paper gives a shifted-power Feistel construction in §2 and expressly studies degree 15, its translated binomial expansion, and its multiplication cost in §5.3. The project result here is the quantitative worst-quadruple bound for a projected unbalanced update with one fixed public permutation and independent XOR keys. Publication priority for this combined statement remains unverified. [MiMC, §§2 and 5.3](https://backend.orbit.dtu.dk/ws/portalfiles/portal/128048431/492.pdf)

## A sufficient test for other polynomials

**Every degree-15 polynomial over the control field has the same four-input bound**, with arbitrary lower coefficients. More generally, suppose a supplied polynomial $p(X)=\sum_\ell p_\ell X^\ell$ has odd degree $D>4(t-1)$ and $\binom{D}{2h}$ is odd for every $0\le h<t$. The coefficient of $X^{D-2h}$ in $\sum_i c_i p(X+a_i)$ equals $p_D M_h$ plus a linear combination of earlier moments $M_0,\ldots,M_{h-1}$, where $M_h=\sum_i c_i(a_i^2)^h$. Indeed, an even $\ell$ contributes only even powers of $X$. Each lower odd $\ell$ that contributes uses the even exponent $\ell-(D-2h)<2h$ of $a_i$. The resulting triangular coefficient matrix has nonzero diagonal $p_D$. The Vandermonde argument therefore still forces a nonzero coefficient. All these protected degrees exceed $D/2$, and the leading term cancels for relative masks, giving bias at most $(D-3)/\sqrt Q$.

The test on $D$ uses its binary digits. Every 1-bit of $2h$ must also be a 1-bit of $D$, by Lucas' theorem. One choice guaranteed to work is $D=2^{2+\lceil\log_2 t\rceil}-1$. This test gives a round bound directly from a polynomial description and a specified projection. The remaining question is how to certify cheaper or lower-degree updates outside this condition, where trace reduction can cancel some of the leading moments. [Monomial digit conditions and Vandermonde argument, Makhul–Winterhof](https://link.springer.com/article/10.1007/s40993-022-00335-8)
