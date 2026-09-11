# Long-lived mammals constrain indels, not substitutions, in the stop-proximal 3′ UTR of cell-cycle genes

**Status:** working manuscript, assembled from the result series in `docs/results/`. Every number
below is reproduced by a script in `scripts/` and stored in a machine-readable artifact next to the
corresponding `RESULT.md`.

---

## Abstract

Large, long-lived mammals should accumulate more cancers than they do — Peto's paradox — and one
family of explanations posits tighter control of the cell-cycle program. We first tested this at the
coding level, screening protein-language-model divergence at protein–protein interfaces across two
predicted pathways, two designs and three built-in controls. Nothing survived multiple-testing
correction, and a five-way rigor battery localised the negative to the metric itself rather than to
the design: embedding distance at coding interfaces does not detect lineage-specific selection.

Moving the unit of analysis to non-coding regulatory sequence produced a positive. Across 57 mammals
on a dated phylogeny, the 3′ UTRs of cell-cycle and tumour-suppressor genes are more conserved in
long-lived species: CDK4 (p = 4 × 10⁻⁵) and CDC20 (p = 0.003) survive FDR, 20 of 25 module genes
conserve directionally (sign test p = 0.004), and the effect is independent of body mass.

We then asked what the signal is made of. It is not canonical miRNA target sites, not AU-rich
elements, and not predicted RNA secondary structure. The reason all three failed is that the
proximal signal is not a substitution signal at all. Separating alignment gaps from mismatches on
identical alignments shows the localisation is carried by **indels**: proximal indel rate p = 0.0003
against substitution p = 0.15. Long-lived mammals carry fewer insertions and deletions in the
stop-proximal 3′ UTR, so the constraint is on UTR architecture rather than on which bases occupy it.

Two external controls bound the claim. Intronic windows from the same genes are flat
(slope −0.004, 95 % CI [−0.022, +0.014]) and their interval excludes the 3′ UTR slope, ruling out a
genome-wide mutation-rate explanation. Twenty-four housekeeping genes are flat (p = 0.92) while the
within-species contrast between modules is significant (p = 0.005), so the effect is specific to the
cell-cycle module rather than a general property of long-lived mammals' 3′ UTRs.

---

## 1. Introduction

Body mass and lifespan both correlate with the number of cell divisions an organism sustains, and
therefore with the number of opportunities for oncogenic mutation. That large, long-lived mammals do
not show correspondingly elevated cancer incidence is Peto's paradox, and it implies lineage-specific
mechanisms of tumour suppression. Candidate mechanisms have been found at the level of gene copy
number (elephant *TP53*) and of specific molecules (naked mole-rat high-molecular-mass hyaluronan),
but a systematic, comparative search for the molecular level at which such control is encoded has
been harder to specify.

This work is organised as two acts, and the first is negative. We report it in full because it is
what motivated the second: knowing precisely *where* a method fails is what tells you where to look
next.

## 2. Act 1 — a bounded negative at the coding interface

### 2.1 Hypothesis and design

The convergent–divergent model proposes two routes to exceptional longevity with distinct molecular
signatures: extremely long-lived small mammals (mole-rats, bats) intensifying selection on cellular
maintenance and DNA repair, and big-bodied long-lived mammals (whales, elephant, rhino) intensifying
selection on cell-cycle and tumour-suppressor control. Both predict elevated protein–protein
interface divergence in the relevant group. We tested the first with a SIRT6-centred DNA-repair
panel, the second with a cell-cycle panel, and used an AMPK energy-sensing panel as the model's own
negative-control pathway. Twenty-two species plus a human anchor.

Per-residue ESM-C embeddings were used to compute an enrichment ratio — mean interface L2 delta over
mean non-interface delta, ortholog against human — with interfaces defined by 8 Å inter-chain
contacts. Group contrasts used Mann–Whitney U with Benjamini–Hochberg FDR across interfaces, plus
three controls: a 1000-permutation shuffled mask, a NEGATOME universal-partner specificity control,
and a cross-lineage convergence requirement.

### 2.2 Results

No lane produced an FDR-surviving signal: 0/26 for SIRT6, 0/30 for AMPK, 0/25–29 across the
stratified designs, and 0/28 for the cell-cycle panel. The cell-cycle panel is the informative
failure — its interfaces are *more* conserved than the rest of the protein (mean enrichment 0.90),
below both the shuffled (1.00) and NEGATOME (1.22) baselines, so the predicted direction is not
merely absent but inverted.

One interface (Ku80's contact surface for the vaccinia C10 antagonist) recurred at nominal
significance and never survived FDR. Testing it with an orthogonal selection metric — Nei–Gojobori
dN/dS — returned the same verdict, 0/42 residues surviving FDR, and showed the interface's 1.83×
elevation over the whole protein falls to 1.56× (p = 0.12) against a solvent-exposure-matched
background. Two independent metrics converging on the same sub-FDR call tightens the negative rather
than opening a lead.

### 2.3 The negative is not a design artifact

Five ways the null could have been manufactured were each tested and excluded:

| Assumption that could hide a signal | Check | Result |
|---|---|---|
| Binary groups, species non-independence | continuous PGLS, Brownian VCV | lifespan p = 0.96 |
| Single panel, low power | all-lane PGLS, 52 interfaces pooled | lifespan p = 0.73 |
| Wrong direction (constraint, not divergence) | long-lived vs reference | binomial p = 0.21, Wilcoxon p = 0.36 |
| Interface mean masks adaptive sites | site-level PGLS with FDR | 0 / 5 618 residues |
| Residue classes pooled | class-stratified FDR | 0 in any class |

Phylogenetic correction *reduced* the one apparent hint rather than revealing one — the direction
expected when relatedness was inflating an effect.

### 2.4 Where the negative localises

The failure is at the metric's molecular level, not in the design or the statistics. L2 divergence
of protein-language-model embeddings at coding interfaces is not a detector of lineage-specific
selection, and a single ortholog's coding sequence integrates selection across all tissues, making
cell-type-specific proliferation biology invisible by construction. Coding-interface divergence
cannot capture regulatory change, gene dosage, isoform usage or expression — which is where the
project's only positive leads already pointed.

That is an actionable negative: change the level.

## 3. Act 2 — a regulatory signal and its anatomy

### 3.1 First signal, and a power question

Moving to UTR sequence divergence (Jukes–Cantor distance of pairwise alignments to human) produced a
3′ UTR conservation trend at n = 22 (pooled p = 0.022) with no counterpart in the 5′ UTR. Rather
than treat a borderline result as either a finding or a null, we calibrated: the detection floor at
n = 22 was |r| ≈ 0.57, and the observed effect was |r| = 0.55. The trend was real in size but sitting
exactly at the power boundary — a prescription to enlarge the panel, not to reinterpret the data.

### 3.2 Extended panel

Enlarging to 59 mammals (57 placed on a dated TimeTree phylogeny, max lifespan 3.8–122 yr, body mass
7.5 g–100 t) and replacing the hand-built tree with real branch lengths, the edge signal crossed FDR.
CDK4 reached p = 4 × 10⁻⁵ and CDC20 p = 0.003; 13 of 15 genes conserved directionally (sign test
p = 0.007); the pooled 3′ UTR effect was p = 0.022 (|r| = 0.55) while body mass carried none
(p = 0.87). Leave-one-species-out jackknives gave worst-case p = 1 × 10⁻⁴ (CDK4) and p = 0.013
(CDC20). The 5′ UTR was a clean null throughout (0/15, pooled p = 0.60).

Notably, the apparent lead at n = 22 had been *HAS2* (p = 0.007); with tripled data it fell to
p = 0.29 while cell-cycle genes rose. The small-panel lead was sampling noise.

### 3.3 A module, not two genes

Expanding the cell-cycle set from 9 to 25 genes did not add individual FDR hits but revealed a
pathway-level property: **20 of 25 genes conserve** their 3′ UTR in long-lived species (sign test
p = 0.004), pooled p = 0.016 (r = −0.51), mass p = 0.94. The two FDR survivors are the tips of a
module-wide pattern.

### 3.4 Localisation and the first three failed hypotheses

Binning each 3′ UTR into eight relative segments localised the signal to the **proximal ~38 %**, next
to the stop codon (p = 0.0005, 0.0008, 0.013 in the three proximal bins), fading monotonically
distally (p > 0.09).

Three hypotheses about what occupies that region were then tested and each failed:

- **Canonical miRNA target sites.** Scoring every position as inside a 7mer-m8 site of a broadly
  conserved family, inside an ATTTA AU-rich core, or neither, all three classes conserved with
  similar slopes (−0.034 to −0.044) and the background class was the most significant (p = 0.035 vs
  0.14 for miRNA sites, 0.093 for AREs). No element type carried the signal.
- **RNA secondary structure.** Folding the human proximal 3′ UTR (ViennaRNA, local fold with
  `max_bp_span = 150`) and comparing divergence at paired versus unpaired positions, the primary
  within-sequence contrast was flat: p = 0.14, slope −0.006. The method is demonstrably able to see
  structure — real pairing masks beat length-matched shuffled masks across 1 376 species–gene pairs
  (Wilcoxon p = 4.7 × 10⁻⁴) — so this is a genuine null rather than an insensitive assay. Under a
  *global* fold the compensatory-substitution rate reached p = 0.071, a hint that vanishes (p = 0.37)
  under local folding: it was an artifact of unreliable long-range pairs.
- **Language-model embeddings.** Re-tested at n = 57 with a 3′UTR-pretrained model (3UTRBERT) over
  the proximal window, embedding distance to human never added anything beyond the alignment. In
  twelve grid cells the partial p of embedding given Jukes–Cantor distance was never significant
  (0.26–0.88), while the reverse stayed at 0.041–0.14; correlation with JC distance was 0.66–0.85.
  Both FDR survivors were missed (CDK4 0.53, CDC20 0.49). Embedding distance is not blind — it is
  redundant, a compressed and noisier restatement of sequence identity whose loss falls on exactly
  the genes that carry the signal.

### 3.5 The decomposition: indels, not substitutions

All three failed hypotheses are claims about *which bases are present*, tested with
substitution-based metrics. The published positional score, however, counted an alignment gap
exactly like a mismatch. Separating the two on identical alignments resolves the series:

| relative bin | combined (published) | substitution only | indel only |
|---|---|---|---|
| 0.00–0.12 | **0.0005** | 0.061 | **0.0022** |
| 0.12–0.25 | **0.0008** | 0.39 | **0.0014** |
| 0.25–0.38 | **0.013** | 0.14 | **0.015** |
| 0.38–0.50 | 0.080 | **0.0045** | 0.17 |
| 0.50–0.62 | 0.12 | **0.0086** | 0.23 |
| 0.88–1.00 | 0.29 | 0.054 | 0.42 |

The combined column reproduces the published positional map exactly, validating the
reimplementation; the decomposition then shows the indel column carries the proximal concentration
and the substitution column does not. Over the proximal window as a whole: combined p = 0.0002,
**indel p = 0.0003**, **substitution p = 0.15**.

The effect is robust. Entering each species' UTR-length mismatch to human as a covariate — the
mechanical driver of gaps — leaves p = 0.0009, and length mismatch is itself uncorrelated with
lifespan (r = −0.029). Worst-case leave-one-gene-out jackknife p = 0.0042; worst-case
leave-one-clade-out p = 0.0021 (dropping all rodents). In absolute coordinates the constraint spans
roughly the first 400 nt from the stop codon (p = 0.005, 0.012, 0.001, 0.015) and fades beyond
(400–800 nt p = 0.090; 800–3 000 nt p = 0.30).

An internal check favours biology over annotation artifact: the proximal 3′ UTR boundary is anchored
by the stop codon and is the best-annotated part of the transcript, the distal poly-A boundary the
worst. Gap rates follow that ordering (0.21 proximal vs 0.49 distal), so the signal sits where the
data are cleanest — the opposite of what an annotation artifact produces.

### 3.6 Control I — is it a slower mutation clock?

Long-lived mammals have longer generation times and lower per-year mutation rates, so they might
accumulate indels more slowly everywhere. We tested this against intronic windows from the same
genes, run through identical machinery. The windows behave as neutral reference sequence should: for
ATM, GC content 0.384 in the intron against 0.559 in the 3′ UTR, and the intron is more divergent on
both metrics (substitutions 0.220 vs 0.209; indels 0.306 vs 0.116).

| region and metric | slope | 95 % CI | p |
|---|---|---|---|
| 3′ UTR proximal, indel | **−0.0331** | [−0.0642, −0.0020] | **0.038** |
| intron, indel | **−0.0040** | **[−0.0218, +0.0138]** | 0.65 |
| 3′ UTR proximal, substitution | −0.0044 | [−0.0150, +0.0062] | 0.41 |
| intron, substitution | −0.0088 | [−0.0189, +0.0013] | 0.087 |

The intron result is a genuine null rather than a power failure: its confidence interval **excludes**
the 3′ UTR slope, and the effect is 8.3× smaller. Adjusting the 3′ UTR test for each species'
intronic indel rate leaves it standing (p = 0.044). The rate effect that does exist sits in
substitutions in neutral sequence — exactly the shape of a mild generation-time effect, visible in
introns and absent from the constrained window.

### 3.7 Control II — is it about the cell cycle at all?

The Peto framing had never been tested directly. Twenty-four housekeeping genes in three blocks
(ribosomal proteins, core glycolysis, cytoskeleton/TCA enzymes) were run as a control set:

| gene set | slope | 95 % CI | p |
|---|---|---|---|
| cell-cycle (25 genes) | **−0.0465** | [−0.0709, −0.0221] | **0.0003** |
| control (24 genes) | **−0.0016** | **[−0.0316, +0.0285]** | **0.92** |
| within-species contrast | **−0.0449** | [−0.0756, −0.0142] | **0.0049** |

All three control blocks are independently flat (p = 0.42, 0.81, 0.62), one with a positive point
estimate; the control interval excludes the cell-cycle slope; the effects differ by a factor of 29.
Nor is the null caused by lack of variation — control genes carry *more* proximal indels on average
(0.352 vs 0.216), so there was more room to detect a deficit, not less.

We explicitly do **not** claim the mirror image the substitution metric suggests (cell-cycle p = 0.15,
controls p = 0.005). The substitution contrast between modules is not significant (p = 0.16) and the
intervals overlap heavily, so there is no basis for separating those slopes. Module specificity
belongs to the indel component alone.

## 4. Discussion

The concrete claim is **stabilizing selection on the architecture of the stop-proximal 3′ UTR in the
cell-cycle and tumour-suppressor module of long-lived mammals**. What is conserved is length and
spacing, not base identity — which is why three consecutive sequence-composition hypotheses came up
empty, and why the failure of all three is explanatory rather than merely disappointing.

Three methodological findings stand somewhat apart from the biology and may be of wider use.

**Embedding distance is redundant, not blind.** The earlier conclusion that language-model embeddings
cannot detect lineage-specific selection was too strong: re-tested at adequate sample size and in the
right window, a genome-generic DNA model reaches nominal significance. But no model in the grid added
information beyond the pairwise alignment it correlates with at r ≈ 0.7–0.85. Anyone proposing an
embedding-derived evolutionary metric should report its partial association given ordinary sequence
distance; without that control, a positive result is uninterpretable.

**Gap conventions are not cosmetic.** A per-position divergence score that counts an indel as a
substitution merges two classes of mutation with different biology. The published localisation of
this signal was correct but was attributed to the wrong class for that reason alone.

**Silent data-integrity failures.** NCBI gene resolution reproducibly returned a genomic record
instead of an mRNA for one gene–species pair, yielding a 144 Mb "3′ UTR". Because analyses truncate
long inputs, the first 3 000 nt of a chromosome would have entered the statistics as a UTR without
anything crashing. A plausibility guard now drops such records by name; across 3 231 records it drops
exactly two.

### 4.1 Limitations

All divergence is measured by human-anchored pairwise alignment, so indel calls are alignment calls
under one gap-penalty regime, and the reference is itself a long-lived species. Mammalian 3′ UTR
annotation is prediction-based for most non-model species. The intron control runs on the 11 genes
whose genomic span permits a mid-gene window, a subset biased toward long genes, and "intronic" there
is probabilistic rather than annotated. Indel *rate* is measured, not the length spectrum or the
insertion/deletion polarity, which would require outgroup polarisation. The control modules were
chosen a priori, but "no established link to lifespan" is a judgement about a literature. Finally,
this is a comparative correlation across species, not a demonstrated mechanism in any one of them.

### 4.2 What would move it

The most concrete mechanistic hypothesis is transposable-element insertion: Alu and L1 elements are
the dominant source of indels in mammalian 3′ UTRs, and a deficit of retroelement insertion in the
proximal 3′ UTR of cell-cycle genes would connect this result to the existing literature on
retrotransposon suppression in long-lived species. That test carries its own confound — Alu elements
are primate-specific, so human-anchored gaps partly track phylogenetic distance from the anchor —
which the existing intron control and leave-one-clade-out jackknife address only in part. Alternative
polyadenylation site usage is the second candidate, since a shift in proximal poly-A site position is
itself an indel.

## 5. Data and code availability

All analyses are scripted and regenerable. Each result directory under `docs/results/` contains a
`RESULT.md`, machine-readable JSON outputs and the figure. The extended-panel result pins its exact
inputs — tree, traits and UTR sequences — under `docs/results/2026-08-05-extended-panel/inputs/` for
bit-level reproducibility. Sequence data come from NCBI, lifespan and body-mass traits from AnAge,
and the dated phylogeny from TimeTree. Intermediates under `data/` are gitignored and regenerable.
