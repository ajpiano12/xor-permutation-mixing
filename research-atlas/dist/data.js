window.ATLAS = {
  "branches": [
    {
      "id": "model",
      "title": "Foundations",
      "summary": "Follow two distinct inputs through the same keyed rounds."
    },
    {
      "id": "counts",
      "title": "Small permutations",
      "summary": "Count which permutations mix and measure how quickly they approach uniformity."
    },
    {
      "id": "structure",
      "title": "Higher dimensions",
      "summary": "Find the algebraic structures behind disconnected and periodic walks."
    },
    {
      "id": "algorithms",
      "title": "Algorithms and limits",
      "summary": "Choose a decision procedure for a table, a circuit, or a callable permutation."
    }
  ],
  "topics": [
    {
      "id": "difference-walk",
      "branch": "model",
      "title": "The difference walk",
      "status": "Proved",
      "provenance": "Published",
      "summary": "A shared random XOR key turns the evolution of two inputs into a walk on their nonzero differences.",
      "body": [
        "Fix one public permutation P. Each round applies P(x ⊕ K) with a fresh, independent, uniform key K shared by both inputs. Given the current difference a, the next difference is P(x) ⊕ P(x ⊕ a) for a uniformly random x.",
        "The transition matrix has uniform stationary distribution. A finite walk converges to it from every start exactly when the support graph is connected and aperiodic. For this round convention, one extra cipher round converts a difference-distance bound to the ordered-pair bound."
      ],
      "attribution": "Lai, Massey and Murphy established the Markov-chain treatment of differential propagation under independent round keys. Liu, Tessaro and Vaikuntanathan study almost t-wise independence of key-alternating ciphers. The notebook specializes this framework to a repeated P and keeps track of the final round.",
      "resources": [
        {
          "label": "Difference-chain calculation",
          "href": "library/readme.html#calculation",
          "kind": "Notes"
        },
        {
          "label": "Transition-count implementation",
          "href": "library/mixing.py.html",
          "kind": "Code"
        }
      ],
      "sourceIds": [
        "markov",
        "ltv",
        "period"
      ]
    },
    {
      "id": "inverse-walk",
      "branch": "model",
      "title": "The inverse as a benchmark",
      "status": "Proved",
      "provenance": "Project derivation",
      "summary": "The three-bit field inverse gives a mixing curve that can be checked exactly by hand.",
      "body": [
        "On the eight-element field, fix zero and invert each nonzero element. After two difference rounds, the starting difference has probability 1/4 and each of the six others has probability 1/8.",
        "Every two additional rounds divide the distance to uniform by eight. This benchmark attains the fastest observed pair-mixing time at all six thresholds in the three-bit census."
      ],
      "attribution": "The patched inverse is a published construction. Appendix A of Liu–Tessaro–Vaikuntanathan treats an even bit length and a final XOR key. The eight-element calculation here is a project derivation. Jain et al. study a different target, including four-wise convergence of the inverse walk.",
      "resources": [
        {
          "label": "Calculation over the eight-element field",
          "href": "library/readme.html#the-inverse-permutation-as-a-benchmark",
          "kind": "Proof"
        }
      ],
      "sourceIds": [
        "ltv",
        "inverse"
      ]
    },
    {
      "id": "three-bit-census",
      "branch": "counts",
      "title": "The three-bit census",
      "status": "Measured",
      "provenance": "Project experiment",
      "summary": "Exactly four in five permutations on eight points mix. The other fifth splits into disconnected and periodic walks.",
      "metric": {
        "value": "80%",
        "label": "of three-bit permutations mix"
      },
      "body": [
        "Of the 40,320 possible tables, 32,256 mix, 7,680 have disconnected difference graphs and 384 cycle through seven classes. The last group can reach every difference, but the round number determines the current class.",
        "At total variation distance 1/4, the fastest mixers need three cipher rounds and the slowest need five. The census uses exact integer counts at six cutoffs from 1/4 to 1/128."
      ],
      "attribution": "This is an exhaustive computation from the project. The published difference-chain method explains how to compute each walk. The cited papers do not supply this census, and independent publication priority remains unverified.",
      "resources": [
        {
          "label": "Census and threshold table",
          "href": "library/readme.html#three-bit-census",
          "kind": "Notes"
        },
        {
          "label": "Grouped census results",
          "href": "library/results/summary.csv",
          "kind": "Data"
        },
        {
          "label": "All permutation measurements (CSV, gzip)",
          "href": "library/results/permutations.csv.gz",
          "kind": "Data"
        },
        {
          "label": "Enumeration program",
          "href": "library/mixing.py.html",
          "kind": "Code"
        }
      ],
      "sourceIds": [
        "markov",
        "ltv"
      ]
    },
    {
      "id": "four-bit-count",
      "branch": "counts",
      "title": "Counting four-bit permutations",
      "status": "Proved",
      "provenance": "Project derivation",
      "summary": "A structural count gives an exact fraction even though there are over twenty trillion labeled permutations.",
      "metric": {
        "value": "99.7663%",
        "label": "of four-bit permutations mix"
      },
      "body": [
        "The exact fraction is 179,759/180,180. A four-bit permutation fails if and only if it is affine or permutes the cosets of a proper nonzero binary subspace. Counting overlaps between these families yields 20,873,902,694,400 mixers.",
        "A fixed parity split is preserved with probability 1/35 at three bits and only 1/6,435 at four bits. This accounts for most of the jump in mixing frequency. Independently, the verifier counts graph partitions up to linear changes of basis."
      ],
      "attribution": "The coset-block obstruction is published in Caranti et al. Saarinen exhaustively studies other four-bit S-box properties under input/output equivalences. The disjoint count for repeated-P mixing is a project result whose priority remains unverified.",
      "resources": [
        {
          "label": "Four-bit counting proof",
          "href": "library/four_bit_count.html",
          "kind": "Proof"
        },
        {
          "label": "Exact counting verifier",
          "href": "library/exact_four_bit.py.html",
          "kind": "Code"
        },
        {
          "label": "Structural obstruction test",
          "href": "library/four_bit_obstructions.py.html",
          "kind": "Code"
        }
      ],
      "sourceIds": [
        "blocks",
        "saarinen"
      ]
    },
    {
      "id": "convergence-rates",
      "branch": "counts",
      "title": "Convergence rates",
      "status": "Measured",
      "provenance": "Project experiment",
      "summary": "The four-bit mixing curves show far more variation than the three-bit census.",
      "metric": {
        "value": "9,957",
        "label": "distinct curves through 8 rounds in the sample"
      },
      "body": [
        "A seeded sample of 10,000 four-bit tables contained 9,974 mixers. Of those, 9,957 had distinct sequences of worst-case total variation distances through 8 difference rounds.",
        "For the original 10,000 draws at seed 20261118, an exact-arithmetic audit certified at least 7,798 distinct asymptotic factors. A parity that is almost preserved helps explain a smaller concentration of slower curves. The histogram describes the sampled tables."
      ],
      "attribution": "The seeded sample, measured profiles, and exact rate-separation audit were produced in this project. Spectral analysis of finite Markov chains is established theory.",
      "resources": [
        {
          "label": "Convergence plot",
          "href": "library/results/four_bit/convergence.png",
          "kind": "Figure"
        },
        {
          "label": "Rate measurements and interpretation",
          "href": "library/readme.html#four-bit-sample",
          "kind": "Notes"
        },
        {
          "label": "Sample measurements (CSV, gzip)",
          "href": "library/results/four_bit/samples.csv.gz",
          "kind": "Data"
        },
        {
          "label": "Exact rate audit",
          "href": "library/verify_rate_bins.py.html",
          "kind": "Code"
        }
      ],
      "sourceIds": [
        "markov"
      ]
    },
    {
      "id": "general-count",
      "branch": "counts",
      "title": "The fraction at larger n",
      "status": "Open",
      "provenance": "Open question",
      "summary": "How often does a uniformly chosen permutation mix as the bit length grows?",
      "body": [
        "The three- and four-bit proportions are exact. At five bits the project can recognize every failure structurally, but counting all overlaps among preserved subspaces still requires a separate calculation.",
        "At six bits, failure can also come from structure outside the four-bit list. A general counting formula would need to account for those families and their intersections."
      ],
      "attribution": "This comparison is an open task in the notebook. Results about typical permutations in related multi-round models have different assumptions from an exact count for one repeated P.",
      "resources": [
        {
          "label": "Exact count at four bits",
          "href": "library/four_bit_count.html",
          "kind": "Proof"
        },
        {
          "label": "Known higher-dimensional structure",
          "href": "library/larger_bits.html",
          "kind": "Notes"
        }
      ],
      "sourceIds": [
        "ltv",
        "blocks"
      ]
    },
    {
      "id": "five-bit-criterion",
      "branch": "structure",
      "title": "The five-bit criterion",
      "status": "Proved",
      "provenance": "Corollary",
      "summary": "At five bits the same two structural obstructions still account for every failure.",
      "body": [
        "A preserved coset partition traps differences in a subspace. At degree 32 the primitive-group classification implies that ruling out these partitions forces transitivity on ordered pairs of distinct points.",
        "The remaining possible nontrivial period must divide 31. That forces every difference to have one deterministic successor, so the permutation is affine."
      ],
      "attribution": "The coset-block theorem of Caranti et al., the published primitive-group classification recorded in GAP, and the equal sizes of cyclic classes give this dimension-specific corollary.",
      "resources": [
        {
          "label": "Five-bit proof",
          "href": "library/larger_bits.html#five-bits",
          "kind": "Proof"
        }
      ],
      "sourceIds": [
        "blocks",
        "degree32",
        "period"
      ]
    },
    {
      "id": "six-bit-example",
      "branch": "structure",
      "title": "A six-bit counterexample",
      "status": "Proved",
      "provenance": "Project derivation",
      "summary": "A nonlinear permutation can preserve no proper subspace partition and still fail to mix.",
      "body": [
        "Split six bits into two elements of the eight-element field. Cube both elements and exchange them. An input difference with one nonzero coordinate always has one nonzero coordinate after a round.",
        "Fourteen differences with one active coordinate are separated from the forty-nine with two. The derivative calculation also shows that every invariant binary subspace containing a nonzero difference would have to be the whole space."
      ],
      "attribution": "The conserved block weight is a standard product-action observation. The explicit counterexample and verification that it preserves no proper subspace partition are project derivations. Independent priority remains unverified.",
      "resources": [
        {
          "label": "Construction and proof",
          "href": "library/larger_bits.html#a-six-bit-counterexample",
          "kind": "Proof"
        }
      ],
      "sourceIds": [
        "blocks"
      ]
    },
    {
      "id": "orbit-criterion",
      "branch": "structure",
      "title": "The orbit criterion",
      "status": "Proved",
      "provenance": "Corollary",
      "summary": "For every bit length, the mixing question can be expressed as a transitivity test on a finite permutation group.",
      "body": [
        "Conjugate the XOR translations by every power of P and let H be the group they generate. Pairwise mixing is equivalent to H being transitive on ordered pairs of distinct inputs. The same statement holds on ordered distinct t-tuples.",
        "Group rounds into blocks of length equal to the order of P. Such blocks include the identity and generate H. A block walk converges uniformly on each of its orbits, so one orbit gives the desired uniform law."
      ],
      "attribution": "Hornauer, Stephan and Wernsdorf relate periodicity to fixed-length round groups and give a sufficient transitivity condition. The project’s equivalence for the conjugates of translations follows by applying finite-group walk convergence to this key schedule.",
      "resources": [
        {
          "label": "Orbit and transitivity proof",
          "href": "library/larger_bits.html#an-exact-criterion-for-every-bit-length",
          "kind": "Proof"
        }
      ],
      "sourceIds": [
        "round-groups",
        "ltv",
        "blocks"
      ]
    },
    {
      "id": "higher-tuples",
      "branch": "structure",
      "title": "Beyond pairs of inputs",
      "status": "Open",
      "provenance": "Open question",
      "summary": "Which small permutations mix on triples, and how long does that take?",
      "body": [
        "The orbit criterion already decides the eventual uniformity question in principle for fixed tuple order. Tracking t−1 differences instead of one gives a state space of (N−1)(N−2)⋯(N−t+1) shapes.",
        "An exact census of higher-tuple rates for the small fixed permutations is still open in this project. Published lower bounds for four inputs in the inverse walk give a reason to measure these separately."
      ],
      "attribution": "Higher-order mixing has an established literature. The unfinished work here concerns exhaustive small fixed-permutation measurements in the notebook’s round convention.",
      "resources": [
        {
          "label": "General tuple criterion",
          "href": "library/larger_bits.html#an-exact-criterion-for-every-bit-length",
          "kind": "Proof"
        }
      ],
      "sourceIds": [
        "inverse",
        "ltv"
      ]
    },
    {
      "id": "exact-algorithm",
      "branch": "algorithms",
      "title": "An exact table test",
      "status": "Implemented",
      "provenance": "Corollary",
      "summary": "One graph search returns a decision and a witness for failures.",
      "body": [
        "Starting at difference one, generate outgoing XOR differences directly from the table. A proper reached set certifies disconnection. If the search reaches every state, a greatest common divisor of edge-depth discrepancies gives the period.",
        "With N table entries this takes O(N²) worst-case word operations and O(N) words of memory. A native OpenMP version divides rows at a single search depth among workers."
      ],
      "attribution": "Denardo published the linear-in-edges period algorithm in 1977. The table-specific transition generator, failure output, and multicore implementation are engineering contributions of this project.",
      "resources": [
        {
          "label": "Exact decision proof",
          "href": "library/larger_bits.html#deciding-pairwise-mixing-from-a-truth-table",
          "kind": "Proof"
        },
        {
          "label": "Python classifier",
          "href": "library/classify_mixing.py.html",
          "kind": "Code"
        },
        {
          "label": "Parallel classifier",
          "href": "library/parallel_mixing.c.html",
          "kind": "Code"
        },
        {
          "label": "Timing measurements",
          "href": "library/readme.html#faster-decisions-for-a-single-table",
          "kind": "Notes"
        }
      ],
      "sourceIds": [
        "period",
        "markov"
      ]
    },
    {
      "id": "fast-filter",
      "branch": "algorithms",
      "title": "A one-sided mixing filter",
      "status": "Proved",
      "provenance": "Project derivation",
      "summary": "A randomized table test certifies mixers and bounds the probability of leaving a true mixer unresolved.",
      "body": [
        "Every certified table really mixes. For each fixed mixer, the probability of an unresolved result is at most a chosen ε. The proof recovers genuine edges in batches with XOR convolutions and checks that they connect all differences and force period one.",
        "For N = 2ⁿ table entries the worst-case cost is O(N n⁴ log(Nn/ε)) word operations with linear working storage. An optional deterministic fallback gives an exact answer and can still take quadratic time."
      ],
      "attribution": "Ahn, Guha and McGregor published graph connectivity sketches using linear measurements. This project adapts sketching, random equality checks, and Walsh transforms to implicit XOR-difference edges and the period test. The exact combination is a candidate contribution with unverified priority.",
      "resources": [
        {
          "label": "Filter proof and error budget",
          "href": "library/fast_table_proof.html",
          "kind": "Proof"
        },
        {
          "label": "Randomized classifier",
          "href": "library/fast_mixing.py.html",
          "kind": "Code"
        }
      ],
      "sourceIds": [
        "sketch",
        "period"
      ]
    },
    {
      "id": "compact-inputs",
      "branch": "algorithms",
      "title": "Circuits and black boxes",
      "status": "Proved",
      "provenance": "Project derivation",
      "summary": "The cost changes when the permutation is supplied as a short program or an oracle.",
      "body": [
        "For n ≥ 3, an exact deterministic oracle test needs 2ⁿ−1 queries in the worst case. Changing two table entries can turn a periodic permutation into a mixer. Allowing a fixed classification error below one half still requires a linear number of queries in the table size.",
        "A different construction encodes a Boolean formula into a compact permutation circuit. The circuit mixes precisely when the formula is satisfiable, proving NP-hardness even when an inverse circuit is supplied."
      ],
      "attribution": "The reduction starts from Cook’s published satisfiability theorem. The permutation gadget and the two-entry oracle argument for this decision problem were derived here. Their independent priority remains unverified.",
      "resources": [
        {
          "label": "Circuit reduction and oracle lower bound",
          "href": "library/circuit_input.html",
          "kind": "Proof"
        }
      ],
      "sourceIds": [
        "cook"
      ]
    },
    {
      "id": "parity-screen",
      "branch": "algorithms",
      "title": "Screening for invariant parity",
      "status": "Implemented",
      "provenance": "Corollary",
      "summary": "A single binary parity that survives every round certifies disconnection.",
      "body": [
        "Look for a nonzero mask m such that m · P(x) and m · x differ by the same constant on every x. The parity of every pairwise difference is then conserved. Binary elimination finds every such mask on a full table.",
        "Sampling a callable yields candidate masks. A union bound controls the chance of retaining a mask that fails on a specified fraction of inputs. A candidate becomes a proof after exhaustive checking or a circuit unsatisfiability certificate."
      ],
      "attribution": "This is the hyperplane case of the published coset-block obstruction. The screen implements elementary linear algebra and a sampling bound for this application.",
      "resources": [
        {
          "label": "Parity identity and sample guarantee",
          "href": "library/circuit_input.html#screening-for-invariant-parities",
          "kind": "Proof"
        },
        {
          "label": "Callable implementation",
          "href": "library/parity_screen.py.html",
          "kind": "Code"
        }
      ],
      "sourceIds": [
        "blocks"
      ]
    }
  ],
  "sources": [
    {
      "id": "markov",
      "title": "Markov Ciphers and Differential Cryptanalysis",
      "authors": "Xuejia Lai, James L. Massey and Sean Murphy",
      "year": "1991",
      "url": "https://doi.org/10.1007/3-540-46416-6_2",
      "note": "Introduces the Markov-chain framework for round differences under independent keys."
    },
    {
      "id": "ltv",
      "title": "The t-wise Independence of Substitution-Permutation Networks",
      "authors": "Tianren Liu, Stefano Tessaro and Vinod Vaikuntanathan",
      "year": "2021",
      "url": "https://eprint.iacr.org/2021/507",
      "note": "Published bounds for SPNs and key-alternating ciphers. The paper’s round assumptions and inverse benchmark are recorded in the corresponding notes."
    },
    {
      "id": "inverse",
      "title": "How Fast Does the Inverse Walk Approximate a Random Permutation?",
      "authors": "Vishesh Jain, Tianren Liu, Clayton Mizgerd, Angelos Pelecanos, Stefano Tessaro and Vinod Vaikuntanathan",
      "year": "2026",
      "url": "https://doi.org/10.1007/978-3-032-35412-9_9",
      "note": "Published at CRYPTO 2026 after a 2024 ePrint. Gives inverse-walk convergence bounds and a four-wise lower bound."
    },
    {
      "id": "round-groups",
      "title": "Markov Ciphers and Alternating Groups",
      "authors": "G. Hornauer, W. Stephan and R. Wernsdorf",
      "year": "1993",
      "url": "https://doi.org/10.1007/3-540-48285-7_41",
      "note": "EUROCRYPT ’93, proceedings published in 1994. Section 2 connects periodic difference walks with double transitivity of fixed-length round groups."
    },
    {
      "id": "period",
      "title": "Periods of Connected Networks and Powers of Nonnegative Matrices",
      "authors": "Eric V. Denardo",
      "year": "1977",
      "url": "https://doi.org/10.1287/moor.2.1.20",
      "note": "Computes the period of a connected directed graph in work proportional to its number of edges."
    },
    {
      "id": "blocks",
      "title": "On Some Block Ciphers and Imprimitive Groups",
      "authors": "Andrea Caranti, Francesca Dalla Volta and Massimiliano Sala",
      "year": "2009",
      "url": "https://arxiv.org/pdf/0806.4135#page=4",
      "note": "Fact 2 and Corollary 3.3 give the coset-block description for translation-based round groups. Published in Applicable Algebra in Engineering, Communication and Computing."
    },
    {
      "id": "degree32",
      "title": "Primitive Permutation Groups Library · Degree 32",
      "authors": "The GAP Group, PrimGrp package",
      "year": "v4.0.3",
      "url": "https://github.com/gap-packages/primgrp/blob/v4.0.3/data/gps1.g#L798-L846",
      "note": "The seven degree-32 records supply the classification input used by the five-bit corollary."
    },
    {
      "id": "saarinen",
      "title": "Cryptographic Analysis of All 4 × 4-Bit S-Boxes",
      "authors": "Markku-Juhani O. Saarinen",
      "year": "2011",
      "url": "https://eprint.iacr.org/2011/218",
      "note": "Exhaustive four-bit S-box analysis for differential, linear and other cryptographic properties. Separate input and output equivalences can change the repeated-permutation walk."
    },
    {
      "id": "sketch",
      "title": "Analyzing Graph Structure via Linear Measurements",
      "authors": "Kook Jin Ahn, Sudipto Guha and Andrew McGregor",
      "year": "2012",
      "url": "https://people.cs.umass.edu/~mcgregor/papers/12-dynamic.pdf",
      "note": "Develops linear graph sketches for connectivity and spanning forests. The atlas filter must generate edges from a permutation table and determine period as well."
    },
    {
      "id": "cook",
      "title": "The Complexity of Theorem-Proving Procedures",
      "authors": "Stephen A. Cook",
      "year": "1971",
      "url": "https://doi.org/10.1145/800157.805047",
      "note": "Establishes the foundational satisfiability hardness result used as the starting problem for the project’s circuit reduction."
    }
  ],
  "snapshot": {
    "date": "2026-11-18",
    "revision": "ae516d1dfc"
  }
};
