# All tuple orders on three bits

Exactly 32,256 of the 40,320 three-bit permutations mix ordered triples. These are exactly the pairwise mixers. Raising the order to four leaves 26,880 permutations. All of those mix through order six. A single keyed round already gives a uniform output on one input.

| Order | Mixing permutations | Disconnected | Connected and periodic | Full cipher rounds at TV ≤ 1/4 among mixers |
| ---: | ---: | ---: | ---: | --- |
| 2 | 32,256 | 7,680 | 384 | 3, 4, 5 |
| 3 | 32,256 | 8,064 | 0 | 4, 5, 6 |
| 4 | 26,880 | 13,440 | 0 | 5, 6, 7 |
| 5 | 26,880 | 13,440 | 0 | 5, 7 |
| 6 | 26,880 | 13,440 | 0 | 6, 8 |
| 7 or 8 | 0 | 24,192 | 16,128 | — |

“Disconnected” and “periodic” describe the support chain on **ordered differences**. Threshold times maximize over every ordered distinct starting tuple, draw fresh independent XOR keys, and reuse the same public permutation each round. The data give exact hitting times for six thresholds from 1/4 to 1/128. [Full census](../results/higher_three_bit.csv)

## Where the extra 5,376 failures come from

Take the table $(0,1,3,4,2,6,7,5)$. Triples mix. Four points can lie in an affine plane or outside one, after an appropriate relabeling of the eight points. Both the translations and this permutation preserve the resulting collection of fourteen planes. Starting on a plane therefore excludes every quadruple outside that collection for all time. Three distinct binary points are always affinely independent, so this obstruction first appears at four. The census verifies triple mixing separately.

Relabeling the ordinary plane system by every permutation produces 30 distinct systems. Eight of them are invariant under the original translations. Every one of the 5,376 triple mixers that fail on quadruples preserves exactly one of these eight systems. This is one symmetry class of labeled tables. Group transitivity gives a dimension-independent explanation for the plateau from four through six and an explicit family showing how pairs and triples can separate in larger dimension. [Group proofs and examples](ALGORITHMIC_PRIOR_ART.md)

Every translation of eight points is even. After $r$ rounds the composite permutation has sign $\operatorname{sign}(P)^r$. Observing seven images determines the eighth and hence detects the sign. Uniform permutations give each sign probability one half. This explains the impossibility at seven and eight.

## How to reproduce the census

Write a tuple relative to its first point as $(a_1,\ldots,a_{t-1})$. At each difference step choose $x$ uniformly and apply the same map $a\mapsto P(x)\oplus P(x\oplus a)$ to every entry. This is a permutation on nonzero differences and therefore on these shapes. A cipher round starts by making the first point uniform independently of the incoming shape. Its final public permutation is a bijection. Consequently TV after $r$ cipher rounds equals shape TV after $r-1$ difference rounds, also for triples and above.

Adding any constant to the output of $P$ cancels in each difference. Translating the input permutes the possible $x$. Simultaneous linear changes of coordinates just relabel every shape. The program groups tables by these symmetries, counts the exact multiplicity of each of 20 representatives, and checks the sum is $8!$. Reordering the tuple and translating its starting points preserve its distance. This reduces the number of starts required for the worst-case calculation. Each step sums exact integer path counts over eight predecessors. A graph-period computation detects failures before the threshold loop. The last image at order eight is forced, so the order-seven calculation gives that row too. [Census program](../higher_census.py)

```sh
uv run --locked --extra four-bit higher_census.py
```

O’Connor’s 1995 census already identified all 10,752 three-bit APN permutations as ergodic. Checking the explicit difference tables of the 20 representatives shows these are exactly the 10,752 tables attaining TV 1/4 after three full cipher rounds. Each has worst TV 3/28 then, while every other table has TV at least 3/7. The full status breakdown, higher-order threshold measurements, and match to the eight plane systems are project computations. [O’Connor, §2.2](https://link.springer.com/content/pdf/10.1007%2F3-540-49264-X_2.pdf) The affine and alternating group actions underlying the obstructions are classical. Published priority for the exact census has not been established.
