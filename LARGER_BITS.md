# How far does the four-bit mixing criterion extend?

For pairwise mixing, the four-bit criterion also holds at **five bits**.
**Six bits is the first counterexample** for bit lengths of at least two.
There are counterexamples at arbitrarily large bit lengths.

## Five bits

Write $V=\mathbb F_2^5$, let $T$ be the group of all XOR translations, and let
$G=\langle T,P\rangle$. Two observations connect the difference walk to the action of $G$.

1. **The difference graph is connected exactly when $G$ is 2-transitive.**
   Here 2-transitivity means that any ordered pair of distinct points can be
   carried to any other. The round maps $P\tau$, for $\tau\in T$, generate $G$
   because one of them is $P$ and multiplying by $P^{-1}$ recovers every translation.
   On a finite set any inverse is a positive power. Translations move freely
   between pairs of a given difference. Taking differences of the pair
   orbits therefore gives exactly the components of the difference walk.
2. **$G$ is primitive exactly when $P$ preserves no coset partition of a proper
   nonzero binary subspace.** Primitive means there is no nontrivial partition
   of the points which the group permutes. In any invariant partition let $W$
   be the part containing zero. For $w\in W$, the translate $w+W$ meets $W$
   at $w$, so it must equal $W$. Thus $W$ is a subspace and all the parts are
   its cosets. Conversely, if $P$ permutes the cosets of $W$, every generator
   of $G$ preserves that partition.

The dimension-specific input is the classification of primitive groups of degree
32. There are seven up to permutation isomorphism, and each is at least
2-transitive. Consequently a five-bit difference chain is **disconnected if and
only if** its permutation preserves a nontrivial subspace coset partition. [GAP PrimGrp coverage](https://gap-packages.github.io/primgrp/doc/chap1_mj.html) · [Degree-32 records](https://github.com/gap-packages/primgrp/blob/v4.0.3/data/gps1.g#L798-L846)

For a connected difference chain of period $h$, each cyclic class has the same
stationary mass. Uniform is stationary, so the classes have equal size and
$h$ divides 31. A nontrivial period is therefore 31, making every class a
singleton. Every difference $a$ then has a deterministic successor. In symbols,

$$P(x+a)+P(x)=P(a)+P(0)\qquad\text{for every }x,a.$$

This makes $x\mapsto P(x)+P(0)$ additive, hence binary linear. Conversely,
every affine map $P(x)=Ax+c$ evolves differences deterministically as $a\mapsto Aa$.
This proves the five-bit criterion, including periodicity.

## A six-bit counterexample

Write six bits as two field elements in $E=\mathbb F_8$. Take $S(x)=x^3$ and

$$P(x,y)=(S(y),S(x)).$$

Since $\gcd(3,7)=1$, $S$ is a permutation. For $a\ne0$ its derivative is

$$D_aS(x)=(x+a)^3+x^3=a^3(1+t+t^2),\qquad t=x/a.$$

The binary linear map $t\mapsto t+t^2$ has kernel $\{0,1\}$. Hence the
derivative takes four distinct values, all nonzero by injectivity of $S$.
In particular $P$ is nonaffine, and those four values span $E$ because a proper
binary subspace of $E$ contains at most three nonzero vectors.

**Failure of mixing.** A difference $(a,b)$ becomes
$(D_bS(y),D_aS(x))$, with $x,y$ ranging independently over $E$. Each output
coordinate is nonzero exactly when the corresponding input difference was
nonzero, with the coordinates exchanged. The number of nonzero coordinates is
conserved. The 14 differences with one active coordinate can never reach the
49 with two.

**Absence of a preserved coset partition.** Suppose the cosets of a nonzero
binary subspace $W$ were preserved. Then $P(v+w)+P(v)\in W$ for all $w\in W$
and all $v$. Pick a nonzero $(a,b)\in W$. If $a\ne0$, fix $y$ and vary $x$.
Adding two outputs with different second coordinates gives $(0,c)\in W$ with
$c\ne0$. If only $b\ne0$, exchange the roles of the coordinates. From
$(0,c)$ the possible successors $(D_cS(y),0)$ span the first coordinate axis.
Starting from any nonzero vector on that axis gives the entire second axis
in the same way. Thus $W=E^2$.

For any $k\ge2$, cube each of $k$ three-bit blocks and cyclically rotate
the blocks. The number of nonzero difference blocks is
conserved, and the single-axis argument propagates around the entire cycle.
More generally, any odd block length $b\ge3$ works over $\mathbb F_{2^b}$.
The cube is bijective because $3$ is coprime to $2^b-1$, and each nonzero
derivative takes $2^{b-1}$ nonzero values, enough to span the block.

## An exact criterion for every bit length

Let $m$ be the order of $P$. Form the group

$$H=\langle P^j T P^{-j}:0\le j<m\rangle.$$

Then **the pairwise difference chain mixes if and only if $H$ is
2-transitive**. More generally, for $2\le t\le |V|$, the cipher converges
to uniform on ordered distinct $t$-tuples from every starting tuple if and
only if $H$ is $t$-transitive.

To prove this, group rounds into blocks of $m$. Move every occurrence of $P$
to the right in the product of the $m$ round maps. The remaining factors are
conjugates of translations, and $P^m$ is the identity. Conversely, setting
all keys to zero realizes the identity, and allowing just one key to vary
realizes any translation in any one of the conjugate groups. Thus the block
transitions generate exactly $H$ and include a self-loop. They mix uniformly
on each $H$-orbit because the transitions average permutations. Convergence
from every start to the uniform law on all distinct $t$-tuples is therefore
equivalent to having a single orbit. Uniform is stationary for each individual
round, so convergence along the block endpoints also gives convergence at every
round. For pairs, $T\subseteq H$ ensures that the orbits are unions of whole
difference fibers, giving the same criterion for the difference chain.
