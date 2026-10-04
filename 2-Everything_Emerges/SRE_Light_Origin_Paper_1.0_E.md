# Positioning of Light and Electromagnetic Waves in the SRE Framework

## The Involutive ℤ₂ Sector, the Cohomological Ladder, and "One Emission as One Closed→Open Transition"

**Version: 1.0 (Treatise Format)**
**Date: 2026-09-28**

---

## Abstract

**Background and problem.** In prior work, SRE has identified "mass" as a ℤ₃-equivariant circulant operator, and connected it with the **ℤ₃-torsor** structure of the three-ring skeleton. A natural follow-up question then arises: **what is the SRE description of "light and electromagnetic waves", what is its relation to mass, and can it cover at once the radiation of chemical origin and of nuclear origin?** This paper answers these three questions head-on.

**Method.** This paper places the project's existing light-side stipulations (the residuality axiom, the Möbius double-cover parameterisation, the involution $P=S^{n/2}$ on the weighted Möbius ladder, the $\mathbb{Z}_2$ holonomy coupling $\delta_A$) and the ℤ₃ structure on the mass side (the three-ring torsor, the circulant operator) under one framework for comparison: the **cohomological ladder** $\lvert H^{1}(G;\mathbb{Z}_n)\rvert=n^{\beta_1}$. The whole paper needs only one structural input — **the involution $P=S^{n/2}$ on the weighted Möbius ladder $M_n$** — and everything else is recomputable linear algebra and group theory.

**Results.** The paper gives four mutually independent, verifiable propositions: (1) **the gear proposition** — light and mass are **two gears of the same machine**: light runs on the coefficient group $\mathbb{Z}_2$ (duality), mass on $\mathbb{Z}_3$ (triality), and the two are adjacent rungs of the same cohomological ladder; the root of the difference is a **group-theoretic prohibition** $\lvert\mathbb{Z}_2\rvert=2<3$ (the light gear structurally cannot hold three generations). (2) **the carrier proposition** — the light carrier is the **odd eigenspace of an involution**, with $P^{2}=I$, membership in the automorphism group, commutation with the Laplacian, zero trace, and spectrum exactly $\{\pm1\}$; it is **completely determined by the single integer $n$, with zero continuous free parameters**, so **there is no place to put a source**. (3) **the source proposition** — the spectrum of the weighted Möbius ladder splits into a **"sector-blind term + odd-sector constant term"** $\mu_k=2c(1-\cos\frac{2\pi k}{n})+2w\cdot\mathbb{1}[k\ \text{odd}]$, in which only the $w$ channel simultaneously satisfies "**acts only on the odd sector**" and "**shifts every mode uniformly**"; measurement over $\delta\in[10^{-3},5\times10^{-1}]$ shows that the $n/2$ modes of the odd sector are shifted by **strictly the same amount** (range $\sim10^{-15}$), that the even sector is **always motionless**, and that the spectral shape is **preserved mode by mode** (residual $8.9\times10^{-16}$); hence **the source can inject only one scalar on the light side**. (4) **the transition proposition** — "one emission = one **closed → open** transition": the **ledger difference** of the transition carries the energy ($E$, $\beta_1$ each $-1$), the **spectral invariants** of the transition carry the light carrier ($\rho$, the sector structure $P$), and the two are **orthogonal**; therefore a chemical source (transition at the electronic-molecular level) and a nuclear source (transition at the nuclear level) **share the same carrier**, their only difference being the level at which the ledger is recorded.

**Boundary and conclusion.** The paper also states four limitations: the light-side readings **come from the project's existing axioms, and this paper only puts them into recomputable form without adding any light-side physical content**; equating the "open state" with "light" is a **structural conjecture**, and the paper claims only a **consistency of direction**; $\mathbb{Z}_3$ is the **smallest** coefficient group able to carry three gears but **not the unique** one ($\mathbb{Z}_4$ works as well); the numerical equality $\mathrm{rank}(P_E)=7$ vs. $\beta_1=7$ **is a pure coincidence and must not be used as mutual evidence**. The overall conclusion is registered as **case 18 of the discrete-closure law (G12)**: it gives "why the gears are two and three", "why the source is a single scalar" and "why energy and carrier are orthogonal" (discrete side, closed), but **not** the energy scale of light (continuous side, requiring external input). All numerical verification in this paper **holds only within the SRE model**.

**Keywords**: State–Relational–Entropy (SRE); light; electromagnetic waves; Möbius double cover; involution; $\mathbb{Z}_2$ holonomy; duality; triality; cohomological ladder; gauge degree of freedom; discrete-closure law.

---

## 1. Introduction

### 1.1 Statement of the problem

This paper answers the following proposition (raised 2026-09-28):

> **Original proposition.** Through the chain "triality ℤ₃ → mass = circulant operator → light and mass = the same mechanism with a different coefficient group", can one and the same SRE description cover at once **light/electromagnetic waves produced by chemical energy** and **light/electromagnetic waves produced by nuclei**? And — is the SRE description of light itself **exactly consistent** with "mass = an unopened circulant operator"?

The proposition overlays three independently decidable sub-problems:

**Table 1.** Three sub-problems and their treatment in this paper.

| No. | Sub-problem | Corresponding section |
|---|---|---|
| **P1** | What is the **carrier** of light in SRE? | §3 (Definition 1, Propositions 1, 2) |
| **P2** | **What is the relation** between light and mass? | §4 (Theorem 2, Propositions 3, 4) |
| **P3** | Can a chemical light source and a nuclear light source **share the same carrier**? | §7, §8 (Theorem 4, Proposition 8) |

### 1.2 Existing characterisations and their predicament

In the prior work of this project, four conclusions relating to "light" already exist, but their **attributions are scattered** — they fall respectively on the axiom level, the spectral level, the coupling level and the numerical level:

**Table 2.** Existing light-side conclusions of the project (existing wording, not paraphrase).

| Clue | Conclusion | Source |
|---|---|---|
| **Residuality axiom** | Light is the **mutually non-annihilating topological residue** at the causal intersection of jointly executed chains: $\Psi_{\text{light}}=\ker(\partial_{\text{mutual}})$ | Electron paper §3.1 [1] |
| **Möbius double cover** | The residual manifold is parameterised by two intrinsic degrees of freedom $(\phi,w)$; when $\phi\to\phi+2\pi$, $w\to-w$, and only $\Delta\phi=4\pi$ closes | Electron topology §2 [2] |
| **Sector attribution** | On the weighted Möbius ladder the involution $P=S^{n/2}$ satisfies $P^{2}=I$, $Pv_k=(-1)^{k}v_k$; **$k$ even = electron sector, $k$ odd = photon sector** | Fork A §2.4/§3.5 [3] |
| **Coupling strength $\delta_A$** | $\delta_A=w^{*}-1$ is the **emergent coupling strength** of the $\mathbb{Z}_2$ holonomy channel, with the character of a **metric parameter** | Electron topology §3 [2] |

These four clues point together to an object that is **not yet uniformly named**, and each exposes a predicament:

1. The **axiom level** gives light's **ontological identity** (residue), but not its **carrier operator**;
2. The **spectral level** gives the carrier operator $P=S^{n/2}$, but not **why it is the one**, nor what its relation to the mass operator is;
3. The **coupling level** gives that $\delta_A$ is "the continuous coupling of the ℤ₂ gear", but it **cannot be measured independently** (an $\alpha^{*}$ input is required);
4. The **numerical level** gives the topological reproduction of $\alpha=\Pi_1(M_{60})$, but covers only **one** constant.

The task of this paper is to **gather these four clues into one framework** and to answer P1–P3. The key step is the methodological discipline of §2.4: **every crossing from "discrete" to "continuous" must be paid for with an external input**. Accordingly the light side splits into a **discrete gear** (given by $\mathbb{Z}_2$) and **continuous quantities** (coupling strength, energy scale, to be paid externally) — and the past predicament is precisely the result of mixing the two halves together.

### 1.3 Contributions of this paper

Relative to the existing material, this paper gives four substantive items:

1. **It establishes the "gear" as a structural proposition** (§4, Theorem 2): light and mass are not two mechanisms but adjacent rungs of one cohomological ladder $\lvert H^{1}(G;\mathbb{Z}_n)\rvert=n^{\beta_1}$; "changing gear = changing the coefficient group", and the hard reason is a group-theoretic prohibition $\lvert\mathbb{Z}_2\rvert=2<3$.
2. **It makes the light carrier a recomputable reading** (§3, Proposition 2): the eleven properties of the involution $P$ and the parameter count of zero continuous free parameters are all computed at once; on this basis it gives the structural ground for "**there is no place to put a source on the light side**".
3. **It proves that "the source injects only one scalar" as the unique channel screened out by two conditions** (§7, Theorem 4): starting from the two-term splitting of the spectrum, it proves that only the $w$ channel satisfies both "acts only on the odd sector" and "shifts uniformly"; and it gives a **counterexample control** (the circumferential channel $c$ fails both).
4. **It establishes "energy lives in the ledger, the carrier lives in the spectrum" as the transition proposition** (§8, Theorem 5), and on this basis explains that a chemical light source and a nuclear light source **share the same carrier** (answering P3).

### 1.4 Structure of this paper

Section 2 gives the existing stipulations, notation, an **analogy guide** and the methodological discipline; Section 3 proves that the light carrier is the involutive ℤ₂ gear (first pillar); Section 4 proves that light and mass form adjacent rungs of the cohomological ladder (second pillar); Section 5 reviews the three-ring ℤ₃-torsor and the structural change "closed → open" (third pillar); Section 6 argues that "unopened" is one and the same kind of statement on both sides; Section 7 treats the **source** side and gives channel uniqueness; Section 8 discusses masslessness and the unification of chemical and nuclear sources; Section 9 connects this paper item by item with the existing SRE light-side documents; Section 10 is discussion and the screening of homonyms; Section 11 is the conclusion. Appendix A is the recomputation list, Appendix B the honesty boundary, Appendix C the analogy index, Appendix D the references.

**Notation convention**: numbers followed by "**(proven, within-model)**" can all be recomputed in one command by the script in Appendix A; those marked "**(to be proven)**" are structural hypotheses proposed here but not yet delivered; those marked "**(negative verdict)**" are propositions already falsified or explicitly delimited as non-computable.

---

## 2. Preliminaries

### 2.1 Existing SRE stipulations about light

**(a) Residuality (Axiom I).** The original wording of electron paper §3.1 [1] is:

> "Light is not an independent material substance. Given a boundary node A evolving to logical-depth step $t$, and a node B evolving to step $t'$, light is embodied as the **mutually non-annihilating topological residue** at the causal intersection of the jointly executed chains:
> $$\Psi_{\text{light}}(\phi,w)\equiv\ker\!\left(\partial_{\text{mutual}}(A_t,B_{t'})\right)."$$

**(b) The Möbius double cover (Axiom II).** The same residual manifold is governed by **two intrinsic degrees of freedom**:

$$\mathbf{X}(\phi,w)=\Big(\big(1+w\cos\tfrac{\phi}{2}\big)\cos\phi,\ \ \big(1+w\cos\tfrac{\phi}{2}\big)\sin\phi,\ \ w\sin\tfrac{\phi}{2}\Big),$$

and when $\phi\to\phi+2\pi$ the transverse vector **flips intrinsically**, $w\to-w$; one must traverse $\Delta\phi=4\pi$ to close (axiom A2 of §2.2, §2.3, and the "4π closure" theorem [2]).

**(c) Involution and sectors (Fork A §2.4/§3.5).** Discretising this 4π-periodic structure into $n$ equally spaced nodes ($n$ even) yields the **weighted Möbius ladder** $M_n$: circumferential edges $(i,i\pm1)$ with weight $c$ (within-sheet refresh), and cross-sheet identification edges $(i,i+n/2)$ with weight $w$ (the Möbius twist channel). On it the **involution**

$$P=S^{n/2},\qquad P^{2}=I,\qquad Pv_k=(-1)^{k}v_k .$$

Its eigenspaces give the **sector split**: $k$ even = electron sector (soft mode), $k$ odd = **photon sector** [3].

**(d) Coupling strength $\delta_A$ (electron topology §3).** $\delta_A\equiv w^{*}-1$ is "the emergent coupling strength of the $\mathbb{Z}_2$ holonomy channel", with the character of a **metric parameter** (persistent-homology test: "$\delta_A$ does not change the barcode"; Morse test: "$\delta_A$ has no Morse counterpart"). Its **parameter-independent spectral fingerprint** is [2][3]

$$\mu_k(1+\delta_A)-\mu_k(1)=\begin{cases}2\delta_A & k\ \text{odd (photon sector)}\\ 0 & k\ \text{even (electron sector)}\end{cases}$$

**(e) Discrete electromagnetic realisation.** `code/Maxwell.py` is a **gauge-covariantly closed** engine on a discrete cell complex: incidence matrix $D$ ($12\times8$), ring-edge matrix $C$ ($5\times12$), projector $P_E=D(D^{\mathsf T}D)^{-1}D^{\mathsf T}$; $E\in\Omega^{1}$ lives on edges, $B\in\Omega^{2}$ on rings, with three discretisations: Faraday / Ampère / Gauss.

The entire work of this paper is to unify (a)–(e) under the discipline of §2.4 and to answer P1–P3.

### 2.2 Notation

**Table 3.** Table of symbols used throughout.

| Symbol | Meaning |
|---|---|
| SRE | State–Relational–Entropy, the parent framework of this paper |
| $M_n$ | weighted Möbius ladder ($n$ even; $V=n$, $E=3n/2$, $\beta_1=n/2+1$) |
| $c,\ w$ | circumferential edge weight (within-sheet refresh) and cross-sheet identification weight (Möbius twist channel) |
| $P=S^{n/2}$ | the **involution** on $M_n$ (light carrier) |
| $k$ | Fourier mode index; $k$ even = electron sector, $k$ odd = photon sector |
| $\mu_k$ | Laplacian spectrum of the weighted Möbius ladder |
| $\mathbb{Z}_n$ | coefficient group (gear): $n=2$ light gear, $n=3$ mass gear |
| $\lvert H^{1}(G;\mathbb{Z}_n)\rvert=n^{\beta_1}$ | **cohomological ladder**: the number of $n$-fold covers |
| $\delta_A$ | **coupling strength** of the $\mathbb{Z}_2$ holonomy channel (metric parameter) |
| $\delta_B$ | the **phase** on the mass side (ℤ₃ gauge degree of freedom) — **not synonymous** with $\delta_A$ |
| $Y_3\ltimes\triangle_3$ | nucleon skeleton (mass-side carrier; §5) |
| $\rho,\ \lambda_2$ | largest / second-smallest Laplacian eigenvalue |
| $Q$ | Koide combination $Q=\dfrac{\sum m}{(\sum\sqrt m)^{2}}=\tfrac13+\tfrac23\eta^{2}$ |
| G12/D1/D2/D3 | discrete-closure law / small-denominator rationals listed separately / angles may not serve as anchors / main statistics only on irrational readings × clean targets |

### 2.3 Analogy guide: the Möbius strip and the switch

Before entering the formal arguments, let us build three **everyday-testable reference systems**, in order to fix the intuition behind all later wording.

**Analogy 1 (the Möbius strip).** Take a paper strip, give one end a half twist and glue it to the other end. Walk once along the **centre line** of the surface back to the starting point — put differently, after "one lap" you are on the **antipodal sheet**; only a second lap truly returns you to the original sheet. This is the $\mathbb{Z}_2$ double cover: **closure requires two laps ($4\pi$), not one ($2\pi$)**. The carrier operator $P=S^{n/2}$ of this paper is exactly the discrete version of this "sheet-flipping" operation, and its eigenvalues $\pm1$ label respectively "stay on this sheet" and "flip to the antipodal sheet".

**Analogy 2 (three-phase and single-phase electricity).** The phasor operator $a=e^{2\pi i/3}$ of three-phase AC satisfies $a^{3}=1$, and its three eigenvalues form $\mathbb{Z}_3$; the operator of a single-phase / two-valued system is $-1$, satisfying $(-1)^{2}=1$, and its two eigenvalues form $\mathbb{Z}_2$. **The central proposition of this paper (Theorem 2) is that light uses the latter and mass the former** — the two systems are not two machines but one machine in different gears.

**Analogy 3 (a switch has only two states).** A switch with only "on/off" can express **at most two** distinct states, however it is thrown. If three things are required to be **pairwise distinct**, the switch structurally cannot do it — not "no method has been found yet", but **the state space is too small**. The capacity criterion of this paper (Theorem 2) is exactly the group-theoretic version of this plain fact: $\lvert\mathbb{Z}_2\rvert=2<3$.

### 2.4 Methodological discipline: the discrete-closure law (G12)

All results of this paper can be located by one methodological discipline already existing in the project:

> **The discrete-closure law (G12).** Every link of the form "discrete structure ⇒ discrete target" **closes** within SRE; every crossing from "discrete" to "continuous" **must be paid for with an external input**.

The role of this law is a **division of labour**: for any result one must be able to tell which half is given by SRE (the discrete side) and which half must be paid in externally (the continuous side). It is the **main axis** along which this paper answers P1–P3 — because the four light-side clues of Table 2 are scattered precisely for want of this distinction.

**Remark 1 (previous instances of G12).** The law has accumulated seventeen instances in earlier work of the project (projection vs. distance, weighted homology, triality, RG invariance of quark targets, the "shape for free" of the circulant operator, light ↔ mass as a change of coefficient group, and others). The conclusion of this paper is registered as the **18th instance** (§10.4).

---

## 3. First pillar: light = the involutive $\mathbb{Z}_2$ gear

### 3.1 The carrier operator

**Definition 1 (weighted Möbius ladder).** Let $n$ be even. The vertex set of $M_n$ is $\{0,1,\dots,n-1\}$, and the edges fall into two classes:

- **circumferential edges**: $(i,i+1\bmod n)$, weight $c$, $n$ of them (within-sheet refresh);
- **identification edges**: $(i,i+n/2)$, weight $w$, $n/2$ of them (Möbius twist channel).

Hence $V=n$, $E=3n/2$, $\beta_1=E-V+1=n/2+1$.

**Definition 2 (light carrier).** Define the involution

$$P:\ i\mapsto i+n/2\ (\bmod n).$$

By [3], $P$ is an automorphism of $M_n$, commutes with the cyclic shift, and **commutes with the graph Laplacian $L$**. The spectrum of $L$ splits by the eigenvalue of $P$ into **two sectors**: the branch of eigenvalue $+1$ is the **electron sector**, that of $-1$ the **photon sector**.

### 3.2 The two-term splitting of the spectrum

**Proposition 1 (sector decomposition of the spectrum).** The Laplacian spectrum of $M_n$ (circumferential weight $c$, identification weight $w$) is

$$\mu_k=2c\Big(1-\cos\frac{2\pi k}{n}\Big)+2w\cdot\mathbb{1}[k\ \text{odd}],\qquad k=0,1,\dots,n-1 .$$

*Proof.* The Fourier modes $v_k[i]=e^{2\pi i ki/n}$ diagonalise simultaneously the circumferential part and $P$: the circumferential part gives $2c(1-\cos\frac{2\pi k}{n})$ (independent of the $\pm$ orientation), and $P$ gives $(-1)^{k}$. The degree is $2c+w$, so the Laplacian acts as

$$L v_k=\big[(2c+w)-2c\cos\tfrac{2\pi k}{n}-w(-1)^{k}\big]v_k=2c\Big(1-\cos\tfrac{2\pi k}{n}\Big)+w\big(1-(-1)^{k}\big)\,v_k .$$

And $1-(-1)^{k}=2\mathbb{1}[k\ \text{odd}]$. $\square$

**Remark 2.** This is equivalent to the project's existing closed form $\mu_k=(2+w)-2\cos\frac{2\pi k}{n}-w(-1)^{k}$ ([3] §3.4) at $c=1$; Proposition 1 merely separates $c$ explicitly so that **channels** can be compared in §7.

**Numerical check of Proposition 1** (Appendix A, PART 1a): for $n=6,8,10,20,30,60$, the maximum deviation between the closed form and direct diagonalisation is $\le6.2\times10^{-15}$; $\mu_0=0$ holds identically; the two branches have $n/2$ modes each (for $n=60$, $|$even$|=|$odd$|=30$) (proven, within-model).

Proposition 1 immediately yields **two structural facts**, which will serve in §7 as the two criteria screening the "source channel":

**Table 4.** Range and shape of the two channels (proven, within-model).

| Channel | Range | Per-mode displacement | Shape |
|---|---|---|---|
| $c$ (circumferential weight) | **both sectors treated alike** | $\propto\big(1-\cos\frac{2\pi k}{n}\big)$ | **non-uniform** |
| $w$ (identification weight / holonomy) | **odd sector only** | identically $=2w$ | **a pure constant shift, no shape** |

### 3.3 Topological protection of the soft mode

**Theorem 1 (topological protection of the soft mode, existing [3] §3.5).** For all $w$,

$$\lambda_2(w)=2-2\cos\frac{4\pi}{n}\qquad(\text{independent of }w),\qquad \lambda_{\max}(w)=2+2w+2\cos\frac{2\pi}{n}\ (w>1-\cos\tfrac{2\pi}{n}).$$

*Proof.* By Proposition 1, for $k$ even $2w\cdot\mathbb{1}[k\ \text{odd}]=0$, so $\mu_k$ is independent of $w$; for $k$ odd $\mu_k$ contains $+2w$. The second-smallest non-zero mode comes from $k=2$ (even), so $\lambda_2=2c(1-\cos\frac{4\pi}{n})$ is independent of $w$; the largest mode comes from an odd mode with $k$ near $n/2$, giving $2+2w+2\cos\frac{2\pi}{n}$. $\square$

**Physical reading.** The electron modes are **purely topological** (completely insensitive to the strength of the twist channel); the Möbius twist channel only renormalises the **speed-of-light modes**. The numerator of $\alpha$ is topological while the denominator contains dynamics — this is the spectral ground for the project's reading of $\alpha$ as $v/c$ [3].

**Measurement** (Appendix A, PART 1b–1c): for $w\in\{0.05,\dots,10\}$, $\lambda_2$ is identically $0.043704798532$, spread $4.3\times10^{-15}$ (proven, within-model).

### 3.4 The carrier has zero parameters: no place to put a source

**Proposition 2 (parameter count of the light carrier).** $P$ is completely determined by **one integer $n$**, and contains **no continuous free parameter**; its eleven structural properties are as follows.

**Table 5.** Eleven tests of $P=S^{n/2}$ ($n=60$) (proven, within-model).

| Test | Result |
|---|---|
| $P^{2}=I$ | true |
| $P\ne I$ | true |
| $P\in\mathrm{Aut}$ ($PAP^{\mathsf T}=A$) | true |
| $[P,L]=0$ (simultaneously diagonalisable) | true |
| $\mathrm{spec}(P)=\{+1,-1\}$ | true |
| $\mathrm{tr}(P)=0$ (the two branches have equal weight) | true |
| $P_{+},\ P_{-}$ idempotent | true |
| $P_{+}P_{-}=0$ (orthogonal) | true |
| $P_{+}+P_{-}=I$ | true |
| $\mathrm{rank}(P_{+})=\mathrm{rank}(P_{-})=n/2$ | true |

*Proof.* Each item is verified directly from the definition of $P$ together with $PAP^{\mathsf T}=A$ and $PL=LP$; idempotence and orthogonality follow from the spectral projections $P_\pm=\frac12(I\pm P)$ built from $P^{2}=I$. $\square$

**Table 6.** Comparison of carrier parameter counts.

| Carrier | Input determining it | Continuous free parameters |
|---|---|---|
| light: symmetry carrier $P$ | **one integer $n$** | **0** |
| light: spectral scales $(c,w)$ | — | 2, but only $w$ is "light-exclusive" |
| mass: operator $A$ | $\mathrm{Re}\,c_0,\ \mathrm{Re}\,c_1,\ \mathrm{Im}\,c_1$ | 3 (invariants 2: $c_0$ and $\lvert c_1\rvert$) |

> **Table 6 is the hardest item in the answer this section seeks: in the symmetry carrier there is no place to put a source.** Compare the mass side — the degrees of freedom $(c_0,\lvert c_1\rvert)$ of the operator $A$ are the landing point of the "ledger" (§8). This is the **common source** of "the source is invisible" in §7 and "energy lives in the ledger" in §8.

**Analogy 4 (a volume knob).** An amplifier with only one knob, "volume", leaves the **shape of the frequency response** unchanged however it is turned; only the **overall loudness** changes. The light source can act only through the single knob $w$ — what it changes is the amplitude, not the shape. Section 7 turns this intuition into a criterion.

---

## 4. Second pillar: the cohomological ladder — light and mass are adjacent rungs

### 4.1 The cohomological ladder

**Proposition 3 (counting $n$-fold covers).** Let $G$ be a finite connected graph with first Betti number $\beta_1$. Then the number of $\mathbb{Z}_n$ principal covers of $G$ is

$$\bigl|H^{1}(G;\mathbb{Z}_n)\bigr|=n^{\beta_1}.$$

*Proof.* $H^{1}(G;\mathbb{Z}_n)\cong\mathrm{Hom}\big(\pi_1(G),\mathbb{Z}_n\big)$, and the free part of $\pi_1(G)$ has rank $\beta_1$, hence $\lvert\mathrm{Hom}(\mathbb{Z}^{\beta_1},\mathbb{Z}_n)\rvert=n^{\beta_1}$. $\square$

**Table 7.** The cohomological ladder (Appendix A, PART 4a; $\beta_1$ measured).

| Graph | $V$ | $E$ | $\beta_1$ | $\lvert H^{1}(\mathbb{Z}_2)\rvert=2^{\beta_1}$ | $\lvert H^{1}(\mathbb{Z}_3)\rvert=3^{\beta_1}$ |
|---|---|---|---|---|---|
| $C_3$ (triangle) | 3 | 3 | 1 | 2 | 3 |
| $K_4$ | 4 | 6 | 3 | 8 | 27 |
| $Q_3$ (cube) | 8 | 12 | 5 | 32 | 243 |
| $M_6$ | 6 | 9 | 4 | 16 | 81 |
| $Y_3$ closed (nucleon skeleton) | 12 | 18 | 7 | 128 | **2,187** |
| $Y_3$ open (one ring edge removed) | 12 | 17 | 6 | 64 | **729** |
| $M_{60}$ ($\alpha$ anchor carrier) | 60 | 90 | 31 | 2,147,483,648 | 617,673,396,283,947 |

**The reading of Table 7 is the central sentence of this paper: this ladder has only one free parameter — the $n$ of the coefficient group.** Light and mass are not two mechanisms but **adjacent rungs of one and the same ladder**: light takes the $n=2$ column, mass the $n=3$ column. The readings of the $n=3$ column agree item by item with the project's triality report [4], with consistent conventions.

### 4.2 The capacity criterion: why the light gear cannot hold three generations

**Theorem 2 (capacity criterion).** Attach a $\mathbb{Z}_N$ label to each of the three edges of a triangle. Then:

- $\mathbb{Z}_2$: the reachable partition patterns are only $\{3\}$ and $\{2{+}1\}$, **$(1,1,1)$ is unreachable**, and the maximum number of pairwise distinct labels $=2$;
- $\mathbb{Z}_3$: the reachable patterns include $(1,1,1)$, and the maximum number of pairwise distinct labels $=3$;
- $\mathbb{Z}_4$: likewise includes $(1,1,1)$, and the maximum number of pairwise distinct labels $=3$.

*Proof.* The labels of the three edges in $\mathbb{Z}_N$ are $(a,b,c)$, and the partition pattern is the partition of their multiplicities. Under $\mathbb{Z}_2$, $a,b,c\in\{0,1\}$, so the three fall into at most 2 distinct values and the partition can only be $(3)$ or $(2,1)$; under $\mathbb{Z}_3$, taking $(a,b,c)=(0,1,2)$ gives $(1,1,1)$. $\square$

**Measurement** (Appendix A, PART 4b): the reachable patterns for $\mathbb{Z}_2$ $=\{(3),(2,1)\}$; both $\mathbb{Z}_3$ and $\mathbb{Z}_4$ include $(1,1,1)$ (proven, within-model).

**Corollary 1.** Since $\lvert\mathbb{Z}_2\rvert=2<3$, **the light gear structurally cannot carry three generations**. This is the **hard reason** for "changing the coefficient group", and the **group-theoretic root** of the project's negative verdict in round 29 ("under two-valued labelling a triangle gives at most $2{+}1$, and $\{1,1,1\}$ is never reachable") [5].

**Analogy 5 (a two-compartment drawer cannot hold three things).** Theorem 2 says: a drawer with only two compartments cannot, however it is arranged, hold something that requires "three pairwise distinct items". This is not a question of "arrangement technique" but of **too few compartments** — irrespective of **what the third item is**. The restriction is purely combinatorial, and therefore has nothing to do with physical questions such as "whether light is a wave".

### 4.3 A limitation that must be stated clearly: $\mathbb{Z}_3$ is "smallest", not "unique"

**The literature says $\mathbb{Z}_4$ also gives three pairwise distinct labels** (third column of Theorem 2). Hence:

> **Remark 3.** "$\lvert\mathbb{Z}_n\rvert\ge3$" is only a **necessary condition**; the status of $\mathbb{Z}_3$ is that of the **smallest** (the first gear that is just big enough), **not the unique** one. The **uniqueness** of $\mathbb{Z}_3$ requires a separate reason — what the project's triality report [4] gives is "the three rings form a single orbit under $\mathrm{Aut}$, of size exactly 3 ⇒ there exists a group of order exactly 3 acting freely and transitively on them (a $G$-torsor)". But this uses "the number of juxtaposed positions $=3$", and "why the number of positions is 3" remains undecided. **Circular argument is not allowed.**

This paper does **not** claim that $\mathbb{Z}_3$ is unique. It uses only half of it — the **necessary condition**: $\mathbb{Z}_2$ is **not enough**.

### 4.4 The same parent group

**Proposition 4 (common parent group).** $\mathbb{Z}_2\subset U(1)$, $\mathbb{Z}_3\subset U(1)$, and $U(1)$ is precisely the electromagnetic gauge group. Hence:

- **light = the order-2 subgroup of $U(1)$** (phase taking $\{0,\pi\}$, i.e. the 2nd root of unity);
- **mass = the order-3 subgroup of $U(1)$** (phase taking $\{0,\frac{2\pi}{3},\frac{4\pi}{3}\}$, i.e. the 3rd root of unity).

*Literature basis.* The original wording of McRae 2025 [6] is "**triality may be seen as multiplication of the basis by a third root of unity, just as duality is often multiplication by a second root of unity**" — that is, **duality = $\mathbb{Z}_2$, triality = $\mathbb{Z}_3$**.

**Remark 4.** By G12 (§2.4): the **continuous phase** of $U(1)$ (coupling strength, continuous angles) belongs on both sides to the **continuous side** and requires external input. This paper treats only the **discrete gears** on both sides.

---

## 5. Third pillar: the three-ring $\mathbb{Z}_3$-torsor and "closed → open"

This section reviews the mass-side structure, to provide the basis for the comparisons in §6 and §8; the full proof is in the project's mass-origin paper [7].

### 5.1 The torsor structure (cited)

**Theorem 3 (the $\mathbb{Z}_3$-torsor structure of the three rings, [4][7]).** The three rings of the closed-state nucleon skeleton $Y_3\ltimes\triangle_3$ ($V=12$, $E=18$, $\beta_1=7$, $\lvert\mathrm{Aut}\rvert=36$) form a $\mathbb{Z}_3$-torsor: there is a **cyclic order**, but **no absolute origin**; the only degree of freedom is an **overall phase shift**.

Its explicit witness is the order-3 automorphism $\varphi:\ L_{ij}\mapsto L_{i,(j+1)\bmod 3}$. **Measurement** (Appendix A, PART 5b): edge-preserving = true, $\mathrm{ord}(\varphi)=3$ = true, $\varphi\ne\mathrm{id}$ = true (proven, within-model).

### 5.2 The order-element spectrum: closed → open = $\mathbb{Z}_3\to\mathbb{Z}_2$

**Proposition 5 (the structural change from closed to open).** The order-element spectra of the automorphism groups of the closed state and the open state (one ring edge removed) are as follows.

**Table 8.** Automorphisms and order-element spectra of the two states (Appendix A, PART 5a; proven, within-model).

| State | $\lvert\mathrm{Aut}\rvert$ | order 1 | order 2 | order 3 | order 6 | orbits on the three rings |
|---|---|---|---|---|---|---|
| **closed** ($E{=}18$, $\beta_1{=}7$) | **36** | 1 | **15** | **8** | 12 | **1** |
| **open** (one ring edge removed, $E{=}17$, $\beta_1{=}6$) | **4** | 1 | **3** | **0** | 0 | **2** $\{0\}\mid\{1,2\}$ |

**Reading.**

> **Closed state (unopened): $\mathbb{Z}_3$ is alive (8 elements of order 3) ⇒ triality ⇒ mass / three generations.**
> **Open state (opened): $\mathbb{Z}_3$ vanishes, only $\mathbb{Z}_2$ remains ⇒ duality ⇒ light.**

And the project's residuality axiom (§2.1a) states plainly that "light is … a **mutually non-annihilating topological residue**" — **light falls precisely on the "opened / unclosed" side**. The two **agree in direction**.

**Remark 5 (this is a structural conjecture, not a proven equivalence).** Equating the "open state" with "light" is a **structural conjecture** of this paper; the paper claims only **consistency of direction** (see Appendix B, item 3).

### 5.3 The character decomposition of $\mathbb{Z}_3$

**Table 9.** The character decomposition of $\mathbb{Z}_3$ on the vertex space and the edge space (Appendix A, PART 5c; proven, within-model).

| Space | $\dim$ | $\chi(\varphi)$ | Decomposition | Trivial weight | Non-trivial weight |
|---|---|---|---|---|---|
| vertices | 12 | 3 | $6\cdot1+3\omega+3\omega^{2}$ | $6/12=\mathbf{1/2}$ | $6/12=\mathbf{1/2}$ |
| edges | 18 | 0 | $6\cdot1+6\omega+6\omega^{2}$ | $6/18=\mathbf{1/3}$ | $12/18=\mathbf{2/3}$ |

**Remark 6 (registration discipline).** The $1/2$, $1/3$, $2/3$ in Table 9 are all **small-denominator rationals** (the D1 trap) and are **without discriminating power** on their own. Their role on the mass side is registered in the candidate chain of [7] §11.2; this paper cites them only as a **comparison** and does not upgrade them.

---

## 6. "Unopened" is the same kind of statement on both sides

The wording put forward by the user in round 32 is "**an evolutionary logic that is unopened and cyclic**". This sentence lands precisely on the light, mass and electromagnetic sides alike, and **lands at the same point**.

### 6.1 The mass side

**Proposition 6 (the "unopened" on the mass side, [7] Proposition 6).** Writing the **multiset** of amplitudes as an **ordered triple** is equivalent to choosing an **origin** for the DFT characters; there are 3 choices of origin, and the three choices give **exactly the same** permutation invariants.

**Measurement** (Appendix A, PART 7a): with $\eta=1/\sqrt{2}$, $\delta_B=2/9$, the three choices of origin give $Q=0.666666666667$, $\lvert\Delta Q\rvert\le2.2\times10^{-16}$ (proven, within-model).

### 6.2 The light side

**Proposition 7 (the "unopened" on the light side).** By the double-cover parameterisation of $M_n$, $\phi$ and $\phi+2\pi$ **are not the same point but the same point on the antipodal sheet** ($w\to-w$); only traversing $4\pi$ returns to the original sheet.

**Measurement** (Appendix A, PART 7b):

$$\bigl|\mathbf{X}(\phi{+}2\pi,w)-\mathbf{X}(\phi,-w)\bigr|=0,\qquad \bigl|\mathbf{X}(\phi{+}4\pi,w)-\mathbf{X}(\phi,w)\bigr|=1.1\times10^{-15}\ (\text{proven, within-model}).$$

### 6.3 The three sides are one and the same kind of statement

**Table 10.** The exact meaning of "unopened" on the three sides (proven, within-model).

| Side | Exact meaning of "unopened" | What is identified away |
|---|---|---|
| **mass** | no origin-bearing DFT ⇒ the origin of $\mathbb{Z}_3$ is unobservable, giving only the equivariance class | the **origin label** of $\mathbb{Z}_3$ |
| **light** | $\phi$ and $\phi+2\pi$ are the same point on the antipodal sheet, giving only $4\pi$ closure | the **antipodal sheet** of $\mathbb{Z}_2$ |
| **electromagnetic wave** | gauge invariance: $A\to A+d\lambda$ leaves observables unchanged ($P_E$ idempotent) | the **gauge function** of $U(1)$ |

> **All three = "do not fix an origin in advance, output only gauge invariants".** The difference lies only in **what is identified away**. This explains why the wording "unopened" can cover all three at once — it is not a metaphor but **one and the same kind of gauge structure**.

**Remark 7 (two senses of "opening" must not be conflated).** "Opening" has two layers, which must be strictly distinguished:

**Table 11.** Two senses of "opening".

| Layer | Operation | Consequence |
|---|---|---|
| **(i) gauge layer** | choose an origin = label | invariants **unchanged** (redundancy) — this is the layer meant in this section |
| **(ii) physical layer** | closed → open (cut one ring edge) | $\lvert\mathrm{Aut}\rvert$ drops from 36 to 4 and the order-3 elements from 8 to zero: a **real** breaking $\mathbb{Z}_3\to\mathbb{Z}_2$ (§5.2, §7) |

---

## 7. The source is invisible: one emission = one closed → open transition

### 7.1 The source injects only one scalar

This section answers the remainder of P1 and the first half of P3: **can the source of light be seen?**

**Theorem 4 (channel uniqueness).** Within the **family of linear perturbations preserving the $P$ symmetry**, only the $w$ channel (identification weight / holonomy) simultaneously satisfies:

- (i) it acts **only on the odd sector**;
- (ii) it applies **the same displacement** $2\delta$ to every mode of the odd sector.

*Proof.* By Proposition 1, $\mu_k=2c(1-\cos\frac{2\pi k}{n})+2w\mathbb{1}[k\ \text{odd}]$. A perturbation $\delta c$ of $c$ gives $\Delta\mu_k=2\delta c(1-\cos\frac{2\pi k}{n})$, which appears **in both sectors at once** (violating i) and is non-uniform in $k$ (violating ii). A perturbation $\delta w$ of $w$ gives $\Delta\mu_k=2\delta w\,\mathbb{1}[k\ \text{odd}]$: only in the odd sector (satisfying i), and $\Delta\mu_k/2\delta w\equiv1$ (satisfying ii). The supports of the two on $\{v_k\}$ determine their action spaces, so within the linear family preserving $P$ the channel is **unique**. $\square$

**Measurement** (Appendix A, PART 3a): $w:1\to1+\delta$, $\delta\in\{10^{-3},10^{-2},10^{-1},5\times10^{-1}\}$:

**Table 12.** Uniformity test of the $w$ channel (proven, within-model).

| $\delta$ | range of $\Delta\mu$ in the odd sector | range of $\Delta\mu/2\delta$ | range of $\Delta\mu$ in the even sector |
|---|---|---|---|
| $10^{-3}$ | $1.8\times10^{-15}$ | $1.000000000\sim1.000000000$ | $0$ |
| $10^{-2}$ | $8.9\times10^{-16}$ | $1.000000000\sim1.000000000$ | $0$ |
| $10^{-1}$ | $1.8\times10^{-15}$ | $1.000000000\sim1.000000000$ | $0$ |
| $5\times10^{-1}$ | $8.9\times10^{-16}$ | $1.000000000\sim1.000000000$ | $0$ |

**Corollary 2 (the spectral shape is unchanged).** Under the $w$ channel the **spectral shape of the photon sector is preserved mode by mode**, with only an overall shift by $2\delta$.

**Measurement** (Appendix A, PART 3b): after subtracting the shift and comparing with the baseline, the residual is $8.9\times10^{-16}$ (proven, within-model).

> **On the light side the source is invisible; one can hear its sound (amplitude) but cannot see its shape.**

### 7.2 Counterexample control

**Table 13.** Counterexample: the circumferential channel $c=1+u$ (Appendix A, PART 3c; proven, within-model).

| $u$ | range of displacement in the odd sector | range of displacement in the even sector | odd sector only? |
|---|---|---|---|
| $10^{-2}$ | $3.98\times10^{-2}$ | $4.00\times10^{-2}$ | **no** (both sectors move) |
| $10^{-1}$ | $3.98\times10^{-1}$ | $4.00\times10^{-1}$ | **no** |

⇒ both criteria **fail**. So "the light-exclusive channel = $w$" is **screened out**, not chosen at will.

**Back to Analogy 4.** $w$ is exactly that "volume knob": it **raises the whole frequency-response curve** (a shift) without touching its shape; whereas $c$ is more like "adjusting the timbre" — it **changes the shape of the curve**, and hence is no longer "the same carrier at a different strength".

### 7.3 Energy lives in the ledger, the carrier lives in the spectrum

**Theorem 5 (orthogonality of ledger and spectrum).** On the nucleon skeleton $Y_3$, "closed → open" (cutting one ring edge) **changes only ledger quantities** ($E$, $\beta_1$, the number of rings) and **does not change spectral quantities** ($\rho$, $\lambda_2$ and the sector structure).

*Proof (measurement + structural explanation).* See **Table 14**: the ledger quantities $E$ and $\beta_1$ each change by $-1$, while the changes in $\rho$ and $\lambda_2$ are zero to machine precision. The structural reason is that $\rho$ and $\lambda_2$ are **automorphism invariants** (points in the same orbit take the same value), whereas "which edge is cut" is **explicit bookkeeping** — by the project's dichotomy of "graph functional vs. ledger" [7] §9.1, invariants are **blind** to points in the same orbit, so the cut-edge information can only be carried by the ledger. $\square$

**Table 14.** Signature vector of the $Y_3$ skeleton closed ↔ open (Appendix A, PART 6a; proven, within-model).

| Quantity | closed | open | difference | Class |
|---|---|---|---|---|
| $V$ | 12 | 12 | $+0$ | **ledger** |
| $E$ | 18 | 17 | $-1$ | **ledger** |
| $\beta_1$ | 7 | 6 | $-1$ | **ledger** |
| $\rho$ | 5.302775637732 | 5.302775637732 | $-4.4\times10^{-15}$ | **spectral (unmoved)** |
| $\lambda_2$ | 1.000000000000 | 1.000000000000 | $1.3\times10^{-15}$ | **spectral (unmoved)** |

**Corollary 3 (division of labour between source and carrier).** **Energy** (how much is released) lives in the **ledger**; the **light carrier** lives in the **spectral invariants**; the two are **orthogonal**. ⇒ **The source changes only the ledger, not the carrier.**

**Table 15.** Spectral quantities when each of the 18 edges is cut in turn (Appendix A, PART 6b; proven, within-model).

| Edge class | count | range of $\rho$ | value of $\lambda_2$ (range within the class) |
|---|---|---|---|
| ring edges (L–L) | 9 | $2.7\times10^{-15}$ | $1.000000000$ ($2.3\times10^{-15}$) |
| strand edges (c–L) | 9 | $3.6\times10^{-15}$ | $0.527166091$ ($2.2\times10^{-15}$) |

**Remark 8 (a refinement, not a refutation).** The project's nucleon paper §4 records that "in the open state, cutting one ring edge ⇒ $\rho$, $\lambda_2$ unchanged". Table 15 **refines** this to: $\rho$ is a **globally strict invariant** (18/18 edges, range $\sim10^{-15}$); whereas $\lambda_2$ is an **orbit-level invariant** — it stays constant only **within one $\mathrm{Aut}$-orbit** (the ring-edge orbit gives $1.0$, the strand-edge orbit $0.527$), and does **not** depend on which particular edge was cut. The original statement is **correct** in the context "cutting a ring edge"; generalised to "immune to whichever edge is cut" it **does not hold**.

**Analogy 6 (the ledger and the scale).** Picture a warehouse: the **stock ledger** records every movement of goods in and out (ledger quantities), while the **calibration of the weighing platform** (the spectrum) records the manner of weighing and does not change its calibration because one crate is missing. Table 14 of this paper separates the two — the source (one crate missing) moves the **ledger**, the carrier (the calibration) does not. **Chemical energy** and **nuclear energy** can be described by one and the same language precisely because their difference is recorded only in the ledger, while the way the calibration is read is the same.

---

## 8. Masslessness and the unification of chemical and nuclear light

### 8.1 The light carrier has no additive scale

**Proposition 8 (the light carrier has no additive scale).** The spectrum of the light carrier $P$ is identically $\{+1,-1\}$ ($\lvert\mathrm{eig}\rvert\equiv1$), the spectral mean is $\mathrm{tr}(P)/n=0$, and $\mu_0=0$ holds identically; whereas the spectral mean of the mass carrier $A=c_0\mathbb{1}+c_1S+\bar c_1S^{2}$ **equals the free parameter $c_0$**.

**Table 16.** Spectral means of the two carriers (Appendix A, PART 8; proven, within-model).

| Carrier | Spectrum | Spectral mean | Additive scale |
|---|---|---|---|
| light: $P$ | identically $\{+1,-1\}$, $\lvert\mathrm{eig}\rvert\equiv1$ | $\mathbf{0}$ | **none** ($\mu_0=0$ holds identically) |
| mass: $A$ | $c_0+2\lvert c_1\rvert\cos(\theta+\frac{2\pi k}{3})$ | $\equiv\mathbf{c_0}$ | **present** ($c_0$ is a free parameter) |

*Measurement* (Appendix A, PART 8b): for $c_0\in\{0,0.5,1,2\}$ the spectral mean of the mass carrier is exactly $0,0.5,1,2$; the light carrier has mean identically $0$ for every $n$ (proven, within-model).

By G12 (§2.4): $c_0$ is that dimension which **must be input externally**. This is the answer to predicament (4) of §1.2, and is **three phrasings of the same conclusion** — with the project's existing corollary "a pure transition has no mass ⇒ the photon is unique" and with "the absolute scale $c_0\in$ outside SRE" (**not three independent pieces of evidence**, see Remark 9).

**Remark 9 (prohibition of double counting).** The following three point to **one and the same place** and **must not be listed as mutually corroborating evidence**:

1. this section: the light carrier has no additive scale while the mass carrier does ⇒ $c_0$ is the dimension that "must be input externally";
2. the project's `_sre_boson_transition.py`: "$\rho$ is a transition invariant ⇒ a pure transition has no mass ⇒ the photon is unique";
3. the project's mass-origin paper §10: the absolute scale $c_0\in$ outside SRE (SRE gives only ratios) [7].

> **Mass needs a scale that SRE cannot supply; light does not.** This is the **formal location** of "the photon is massless" in SRE. It must be stressed that "the photon is massless" has a different source in the Standard Model (gauge invariance plus only two transverse degrees of freedom); the statement here carries only the one layer "**no $\mathbb{Z}_3$ ⇒ no such unopened cycle**", and the two **must not be conflated**.

### 8.2 Chemical light and nuclear light: the same carrier

**Table 17.** Comparison of the two sources on the SRE carrier (Appendix A, PART 2, 3, 6; proven, within-model).

| Aspect | Chemical energy / atomic emission | Nuclear emission ($\gamma$) | Attribution on the SRE side |
|---|---|---|---|
| carrier | odd sector $P$ | odd sector $P$ | **the same** ($P$ determined by $n$ alone) |
| sector structure | $n/2$ even + $n/2$ odd | the same | **the same** |
| spectral shape | independent of the source | independent of the source | **the same** (Corollary 2) |
| coupling quantity | one scalar $w$ | one scalar $w$ | **of the same type**, differing only in magnitude |
| transition occurs at | L1/L2 (electronic–molecular level) | L3 (nuclear level) | **different** |
| order of magnitude of released energy | $\sim$1–10 eV | $\sim$0.1–10 MeV | **external ledger** (Remark 10) |

**⇒ Answer to P3: yes.** Chemical light and nuclear light **share the same carrier** on the SRE side, and this is not a new assumption but a **direct corollary** of "there is no place to put a source on the light side" (§3.4) and "ledger and spectrum are orthogonal" (§7.3).

**Analogy 7 (a battery and a generator).** The same light bulb can be connected to a **battery** (chemical energy) or to a **generator** (mechanical energy) — the bulb (the carrier) is exactly the same, and what changes is the **power source**. If someone asks "is a bulb lit by a battery the same kind of bulb as one lit by a generator", the answer is obviously "the same bulb, a different source". Table 17 of this paper says exactly this: **the carrier is the same, the source differs**.

### 8.3 The difference lies in the ledger

**Remark 10 (prohibition of appropriating a homonymous term).** The project's existing "span of 13.40 orders of magnitude across three layers" (L1 $-2.30$/L2 $-0.09$/L3 $+11.10$) is the span of the **sensitivity of decay rates to the environment**, **not** a span of photon energies. The two are different physical quantities and **must not be cross-cited**.

**Remark 11 (annotation of external magnitudes).** The eV/MeV in Table 17 are **external reference magnitudes** (neither measured here nor an SRE output): the ratio is $\sim10^{5\text{–}6}$. **This is the ledger magnitude of the source; there is no corresponding reading on the SRE side** — the same gap as $c_0$ in §8.1.

---

## 9. Connection with existing SRE light-side documents

This section connects this paper item by item with the four existing clues (Table 2), in order to confirm that this paper **adds no light-side physical content** and only performs **structuring and making-recomputable**.

### 9.1 The residuality axiom and the "open state"

The project's residuality axiom (§2.1a) says that light is a "mutually non-annihilating **topological residue**". The structural fact of §5.2 of this paper is: the closed state has $\lvert\mathrm{Aut}\rvert=36$ and contains 8 elements of order 3; the open state has $\lvert\mathrm{Aut}\rvert=4$ and **zero order-3 elements**.

> **"Residue" = the part of the structure that has not been closed away.** What is supported by $\mathbb{Z}_3$ in the closed state and **vanishes** in the open state is exactly the "triality" part; what remains is $\mathbb{Z}_2$. Hence "light is a residue" and "light is on the $\mathbb{Z}_2$ gear" **agree in direction**.

**Remark 12.** This is only **consistency of direction**, and does not constitute a proof that "open state = light" (see Appendix B, item 3).

### 9.2 Formal separation of the two $\delta$'s

The comparison of this paper touches **two** homonymous symbols, which must be pinned down item by item:

**Table 18.** Separation of the two $\delta$'s.

| | $\delta_A$ (electron topology §3 [2]) | $\delta_B$ (mass side [7]) |
|---|---|---|
| definition | $\delta_A=w^{*}-1$, the **coupling strength** of the $\mathbb{Z}_2$ holonomy channel $=4.347\times10^{-5}$ | the **phase** (relative DFT origin), mod $2\pi/3$ |
| character | **metric parameter** (continuous, not a topological invariant) | **gauge** (redundancy) |
| consequence | raises the photon sector only, $+2\delta_A$ per mode (Table 12) | zero effect on invariants (Proposition 6) |
| independent measurement | **in principle** falsifiable, currently infeasible (an $\alpha^{*}$ input is required) | unobservable quantity |

**One is a metric, the other a gauge. They are not interchangeable.** This paper writes $\delta_A$/$\delta_B$ throughout.

**Remark 13 (an operational warning).** The **fingerprints** of Table 12 and Proposition 6 are **completely identical** (both are "raise the odd sector only, by an equal amount per mode"), and the difference lies only in **semantics**: $\delta_A$ is a metric **fixed** by an external input, $\delta_B$ a gauge **freely choosable**. This is exactly why the phenomenon "raising the odd sector" is by itself **insufficient** to distinguish the two — one must state together whether it changes observables.

### 9.3 The $\alpha$ anchor and the Möbius ladder

The project already has a relation of the "constant ↔ single invariant" type on $\alpha$ and $M_{60}$ [2][3]:

$$\Pi_1(M_n)=\frac{4\sin^{2}(2\pi/n)}{2+2w+2\cos(2\pi/n)}\Big|_{w=1},\qquad \Pi_1(M_{60})=7.297458502\times10^{-3},$$

with a relative deviation of $1.45\times10^{-5}$ from the CODATA value $1/137.035999084=7.297352569\times10^{-3}$; solving $\Pi_1(M_n)=1/\alpha$ gives $n^{*}=60.000436$ (**Appendix A, PART 9, proven, within-model**).

**Table 19.** $\alpha$ anchor readings (Appendix A, PART 9).

| Quantity | Value |
|---|---|
| $\lambda_2(M_{60})$ | $0.043704798532$ |
| $\rho(M_{60})=\lambda_{\max}$ | $5.989043790737$ |
| $\Pi_1(M_{60})=\lambda_2/\rho$ | $7.297458502\times10^{-3}$ |
| CODATA $1/\alpha$ | $137.035999084$ |
| relative deviation | $1.452\times10^{-5}$ |
| $n^{*}$ | $60.000436$ |

This paper needs only this one item: **the light-side carrier $M_n$ and the mass-side carrier $Y_3$ are two members of one family** — both appear in the cohomological ladder of Table 7.

### 9.4 The discrete Maxwell engine

**Table 20.** Structural readings of `code/Maxwell.py` (Appendix A, PART 10; proven, within-model).

| Quantity | Value |
|---|---|
| incidence matrix $D$ | $12\times8$, $\mathrm{rank}(D)=7=V-1$ |
| $\beta_1=E-\mathrm{rank}(D)$ | $12-7=\mathbf{5}$ |
| ring-edge matrix $C$ | $5\times12$, $\mathrm{rank}(C)=5$ |
| projector $P_E$ | idempotent ✓, symmetric ✓, $\mathrm{rank}=7$ |
| engine actually running (Gauss residual) | $\max\lvert\text{residual}\rvert=2.842\times10^{-14}$ |

**The mathematical content of "gauge-covariant closure" = the projector $P_E$ is idempotent ⇒ field evolution is locked inside the chain space (the gauge orbit).** This is **of the same type** as the "invariant projection" on the mass side (cf. the third row of Table 10): **both rely on an idempotent projection to restrict the result to the physical subspace** — on the light side projecting onto the chain space and erasing the gauge component, on the mass side projecting onto the $S$-equivariance class and erasing the choice of origin.

**Remark 14 (D1 warning).** $\mathrm{rank}(P_E)=7$ is the **dimension of the image space of 0-forms**, while $\beta_1=7$ is the **dimension of the 1-homology** — the same number with different meanings, and **mutual evidence is forbidden**. Likewise, $\mathrm{rank}(C)=5$ and $\beta_1=5$ being numerically equal is also a coincidence (noted in Appendix A, PART 10).

---

## 10. Discussion

### 10.1 Screening of homonyms (an old pitfall of this project)

This paper touches **four groups** of homonyms, pinned down item by item:

**Table 21.** Four groups of homonyms.

| Group | A | B |
|---|---|---|
| **$\delta$** | $\delta_A$ = $\mathbb{Z}_2$ holonomy **coupling strength** (metric) | $\delta_B$ = **phase** (gauge) |
| **$\Pi_1$** | spectral projection $\lambda_2/\rho$ (Möbius closed form) | skeleton closure degree ($Y_3=0.188580485$) |
| **"opening"** | choosing an origin = gauge (invariants unchanged) | closed → open cut = real breaking $\mathbb{Z}_3\to\mathbb{Z}_2$ |
| **"light"** | the residuality axiom ($\mathbb{Z}_2$ gear, discrete) | the discrete Maxwell engine ($U(1)$ continuous gauge) |

There is also the **same number, different meaning** case: $\mathrm{rank}(P_E)=7$ vs. $\beta_1=7$ (Remark 14). All of the above **may under no circumstances be used as mutual evidence**.

### 10.2 Relation to external work

**Table 22.** Forms in which light/electromagnetic structures appear in the literature.

| Work | Related structure |
|---|---|
| McRae 2025 [6] | "triality = multiplication by a third root of unity, just as duality = multiplication by a second root of unity" — the **direct literature basis** for the gear proposition of this paper |
| Berry phase and the AB effect | both are $U(1)$ continuous phases; the $\delta_A$ of this paper is a **continuous coupling** on the discrete $\mathbb{Z}_2$ gear, and is **of a different class** (distinguished in the project's T1-H4) |
| the $\mathbb{Z}_2$ invariant of topological insulators | the edge-state coupling is $U(1)$ rather than $\mathbb{Z}_2$; the $\delta_A$ of this paper **has no Standard-Model counterpart** [2] |

**The difference from them lies in the landing point**: the works above take $\mathbb{Z}_2$/$\mathbb{Z}_3$ as their **starting point**; in this paper the gear is **read out** from the **automorphisms and spectrum** of the SRE skeleton (the involution $P$ and the three-ring torsor). That is, what this paper provides is a structural source for "**why these coefficient groups appear**".

### 10.3 Candidates and registration

**Remark 15 (candidates, not upgraded).** Two items are **registered as candidates** and **must not** be promoted to conclusions:

1. **physical comparison**: "2 photon polarisations ↔ 2 of $\mathbb{Z}_2$" and "three generations ↔ 3 of $\mathbb{Z}_3$" are **structurally parallel** (a capacity comparison of discrete gears), **not a quantum-number correspondence**, and **must not be used as mutual evidence**;
2. **"the photon is massless" ↔ there is no $\mathbb{Z}_3$ torsor on the light side**: a **weak candidate**, whose Standard-Model source is different (Remark 9).

### 10.4 The discrete-closure-law perspective

The conclusion of this paper is located as **case 18 of G12**:

- **discrete side (closed)**: why the gears are two and three (involution / torsor); why the source is a single scalar (channel uniqueness, Theorem 4); why energy and carrier are orthogonal (Theorem 5); why "unopened" is gauge (Propositions 6, 7);
- **continuous side (input required)**: the energy scale of light (eV/MeV order), the absolute value of the coupling strength $\delta_A$, the $U(1)$ continuous phase.

It is of the same type as the previous instances: **discrete structure fixes the shape, continuous quantities must be paid externally**. An empirical corroboration still holds: **those that pass the tests are all dimensionless ratios, those with a negative verdict are all quantities seeking dimensionalisation.**

---

## 11. Conclusion

This paper gives the following rulings on "the positioning of light and electromagnetic waves in SRE":

1. **Gear layer**: light and mass are **two gears of the same machine** — light runs on $\mathbb{Z}_2$ (duality), mass on $\mathbb{Z}_3$ (triality), and the two are **adjacent rungs** of one **cohomological ladder** $\lvert H^{1}(G;\mathbb{Z}_n)\rvert=n^{\beta_1}$ (Proposition 3, Table 7). "Changing gear = changing the coefficient group", and the hard reason is the **group-theoretic prohibition** $\lvert\mathbb{Z}_2\rvert=2<3$ (Theorem 2, Corollary 1).
2. **Carrier layer**: the light carrier = **the odd eigenspace of the involution $P=S^{n/2}$** (Definition 2); it is completely determined by the single integer $n$, with **zero continuous free parameters** (Proposition 2, Table 6). **In the symmetry carrier there is no place to put a source.**
3. **Source layer**: the spectrum splits into a "**sector-blind term + odd-sector constant term**" (Proposition 1); within the linear family preserving $P$, **only the $w$ channel** satisfies both "odd sector only" and "uniform shift" (Theorem 4) — measurement shows the $n/2$ odd-sector modes are shifted by strictly the same amount, the even sector is always motionless, and the **spectral shape is preserved mode by mode** (Corollary 2, Table 12). ⇒ **The source is invisible; one can hear its sound only.**
4. **Transition layer**: "**one emission = one closed → open transition**" (Theorem 5): the **ledger difference** carries the energy, the **spectral invariants** carry the carrier, and the two are **orthogonal** (Table 14). ⇒ A chemical light source and a nuclear light source **share the same carrier**, their only difference being the level at which the ledger is recorded (Table 17).
5. **Masslessness layer**: the light carrier has no additive scale (spectral mean $\equiv0$); the spectral mean of the mass carrier is $\equiv c_0$ (a free parameter) (Proposition 8, Table 16). This explains the **formal location** of "the photon is massless" in SRE, and is three phrasings of the same conclusion as "a pure transition has no mass ⇒ the photon is unique" and "$c_0\in$ outside SRE" (Remark 9).
6. **Gap layer**: **the energy scale of light** (eV/MeV order) and **the absolute value of the coupling strength $\delta_A$** must be input externally — of the same type as the $\eta$ and $c_0$ gaps on the mass side (payment on the continuous side).

**Overall statement of the conclusion.** **Light = the involutive invariant of the $\mathbb{Z}_2$ gear**; its carrier is borne by the odd sector of the involution $P$; "unopened" = outputting only gauge invariants; "source" = able to inject only one scalar. What SRE can give: **the gear, the carrier, channel uniqueness, the orthogonality of ledger and spectrum**; what it cannot give: **the energy scale of light and the absolute value of the coupling strength**. And **the reason chemical light and nuclear light can be described by one and the same language is not that they "happen to be similar", but that the source cannot enter the carrier.**

---

## Appendix A　Recomputation list

**Recompute all readings in one command** (requires numpy + networkx):

```
python.exe -u _sre_light_origin_paper_check.py \
    > _sre_light_origin_paper_check.log 2>&1      # all readings of the main text (PART 1-11)
```

**Table A1.** Correspondence between the readings of this paper and the recomputation script.

| Location in this paper | Script PART | Key output |
|---|---|---|
| Proposition 1, Table 4 (§3.2) | PART 1a | max deviation closed form vs. numerical $\le6.2\times10^{-15}$; $\mu_0=0$ |
| Theorem 1 (§3.3) | PART 1b–1c | $\lambda_2=0.043704798532$; spread over the $w$ scan $4.3\times10^{-15}$ |
| Proposition 2, Tables 5–6 (§3.4) | PART 2 | all eleven tests true |
| Theorem 4, Table 12 (§7.1) | PART 3a–3b | odd-sector shift range $\le1.8\times10^{-15}$; $\Delta\mu/2\delta\equiv1$; shape residual $8.9\times10^{-16}$ |
| Table 13 (§7.2) | PART 3c | counterexample: the $c$ channel moves both sectors ($3.98\times10^{-2}$/$4.00\times10^{-2}$) |
| Proposition 3, Table 7 (§4.1) | PART 4a | cohomological ladder (including $M_{60}$: $\beta_1=31$) |
| Theorem 2 (§4.2) | PART 4b | $\mathbb{Z}_2$ patterns $\{(3),(2,1)\}$; $\mathbb{Z}_3$ contains $(1,1,1)$ |
| Theorem 3, Proposition 5, Table 8 (§5) | PART 5a–5b | closed $36/1/15/8/12/1$ orbits; open $4/1/3/0/0/2$ orbits; $\varphi$ edge-preserving of order 3 |
| Table 9 (§5.3) | PART 5c | vertices $1/2\mid1/2$; edges $1/3\mid2/3$ |
| Theorem 5, Tables 14–15 (§7.3) | PART 6a–6b | $E:18\to17$, $\beta_1:7\to6$; $\rho$, $\lambda_2$ range $\sim10^{-15}$; $\lambda_2$ ring edges $1.0$/strand edges $0.527166091$ |
| Propositions 6–7, Table 10 (§6) | PART 7a–7b | $\lvert\Delta Q\rvert\le2.2\times10^{-16}$; $\lvert\mathbf{X}(\phi{+}4\pi)-\mathbf{X}(\phi)\rvert=1.1\times10^{-15}$ |
| Proposition 8, Table 16 (§8.1) | PART 8a–8b | light carrier mean $\equiv0$; mass carrier mean $\equiv c_0$ |
| Table 19 (§9.3) | PART 9 | $\Pi_1(M_{60})=7.297458502\times10^{-3}$; deviation $1.452\times10^{-5}$; $n^{*}=60.000436$ |
| Table 20 (§9.4) | PART 10 | $D$ $12\times8$/$\mathrm{rank}\,7$; $\beta_1=5$; $P_E$ idempotent of rank 7; Gauss residual $2.8\times10^{-14}$ |
| §4.3, §10 comparison | PART 11 | Koide $Q=0.666664463$, $\eta^{2}=0.499996695$ |

**Table A2.** Preceding scripts (independent sources for the conclusions of this paper; all archived in `code/`).

| Script | Round | Content |
|---|---|---|
| `_sre_weight_homology.py` | round 29 | weighted homology / dormancy rate (prerequisite of the $\mathbb{Z}_2$-gear negative verdict) |
| `_sre_triality_families.py` | round 30 | $\mathbb{Z}_3$ / triality / torsor / Koide |
| `_sre_light_mass_correspondence.py` | round 35 | light ↔ mass change of coefficient group, cohomological ladder, capacity criterion |
| `_sre_light_source_universality.py` | round 36 | chemical and nuclear light on one carrier, source invisibility |

---

## Appendix B　Honesty boundary

1. Everything in this paper is a self-consistent statement **internal to the SRE model / at the level of linear algebra and group theory**, and **does not** claim numerical predictions about real physics. The comparison with experimental orders of magnitude (eV/MeV) serves only to illustrate that "the difference lies in the ledger".
2. **All light-side readings come from the project's existing axioms** (residuality axiom, Möbius double cover, Fork A involution, $\delta_A$, Maxwell engine); this paper **only puts them into recomputable form and adds no light-side physical content**.
3. **Equating the "open state" with "light" is a structural conjecture.** This paper claims only that §5.2 and the residuality axiom **agree in direction**, and **does not** claim equivalence.
4. **The capacity criterion of §4.2 gives only a necessary condition.** $\mathbb{Z}_3$ is the **smallest** coefficient group able to carry three gears, **not the unique** one ($\mathbb{Z}_4$ works as well). The uniqueness of $\mathbb{Z}_3$ requires a separate reason, and **must not** be argued circularly from "the number of positions = 3".
5. **The numerical equality $\mathrm{rank}(P_E)=7$ vs. $\beta_1=7$ is a pure coincidence** (quantities of different dimensions); likewise $\mathrm{rank}(C)=5$ vs. $\beta_1=5$. Mutual evidence is forbidden under the D1 warning.
6. **$\delta_A$ and $\delta_B$ have the same name but different meanings** (Table 18); this paper has separated them, but historical documents have not all been revised accordingly.
7. **The "channel uniqueness" of Theorem 4 is confined to the family of linear perturbations preserving the $P$ symmetry.** Non-linear or symmetry-breaking sources lie outside this paper (see the gap layer in §11).
8. **The continuous phase of $U(1)$ (coupling strength, continuous angles) belongs on both sides to the "continuous side" and requires external input**; this paper does not touch it.
9. **Table 15 is a refinement of an existing conclusion (not a refutation).** The original statement is correct in its restricted context; this paper does not alter existing documents, only registers.
10. The conclusion = **case 18 of G12**.

---

## Appendix C　Analogy index

**Table C1.** Index of analogies and illustrations.

| No. | Name | Location | What it illustrates |
|---|---|---|---|
| Analogy 1 | the Möbius strip | §2.3 | $\mathbb{Z}_2$ double cover: two laps to return to the original sheet ($4\pi$ closure) |
| Analogy 2 | three-phase and single-phase electricity | §2.3 | $\mathbb{Z}_3$ (phasor $a$) vs. $\mathbb{Z}_2$ ($-1$): changing gear = changing the coefficient group |
| Analogy 3 | a switch has only two states | §2.3 | capacity: two states cannot hold three distinct values |
| Analogy 4 | an amplifier with only a volume knob | §3.4, §7.2 | the source changes amplitude only, not shape (channel uniqueness) |
| Analogy 5 | a two-compartment drawer cannot hold three things | §4.2 | the capacity criterion is a **counting** problem, not a physical one |
| Analogy 6 | the ledger and the scale | §7.3 | ledger quantities (energy) vs. carrier quantities (spectrum), mutually orthogonal |
| Analogy 7 | a battery and a generator | §8.2 | a chemical source and a nuclear source share one carrier; only the source is swapped |
| Analogy 8 | a prism and dispersion | §6.1 | DFT = dispersion; choice of origin = gauge |
| Analogy 9 | an altitude datum and relative height | §8.1 | relative quantities (ratios) vs. absolute quantities (requiring an external datum) |

**Usage note.** To explain this paper to a non-specialist, the recommended route is: **Analogy 1** (the Möbius strip) → **Analogy 2** (three-phase electricity) → **Analogy 3** (the switch) → **Analogy 4** (the volume knob) → **Analogy 7** (the battery and the generator). These five steps convey the skeleton of the whole paper without using any additional terminology.

---

## Appendix D　References

[1] This project, *A Complete Characterisation of the Electron in the SRE Framework* (electron complete paper) §3: the residuality axiom (Axiom I) and the closed-form parameter map (Axiom II).

[2] This project, *The Intrinsic Topological Structure of the Electron in the SRE Framework* (electron topology, 2026-09-16): the Möbius double cover, $4\pi$ closure, $\delta=$ the emergent coupling strength of the $\mathbb{Z}_2$ holonomy channel, and six topological tool tests (K1–K6).

[3] This project, *Fork A Axiomatic Derivation: the Double-Cover Four-State Complex and the Fine-Structure Constant*: closed-form spectrum of the weighted Möbius ladder (§3.4), topological protection of the soft mode (§3.5), the modulus no-go and the A5 bare coupling (§7), the parameter-independent signature of $\delta$ (§7.4).

[4] This project, *SRE Triality / Three-Gear Structure Report* (round 30, 2026-09-28): the $\mathbb{Z}_3$-torsor, the order-3 automorphism $\varphi$, the character decomposition, and the first measurement of closed → open $=\mathbb{Z}_3\to\mathbb{Z}_2$.

[5] This project, *SRE Weighted Homology / Dormancy Rate Report* (round 29, 2026-09-28): weighted homology of the $\mathbb{Z}_2$ gear, and the negative verdict "under two-valued labelling a triangle gives at most $\{3,2{+}1\}$".

[6] R. McRae, *Triality as multiplication by a third root of unity* (the root-of-unity characterisation of triality and duality), arXiv:2502.14016 (2025).

[7] This project, *Mass Origin in the SRE Framework: a Circulant-Operator Formulation on the Three-Ring ℤ₃ Torsor* (mass-origin paper, v2.0, 2026-09-28): the circulant operator, the torsor, the invariant moduli space, the Koide relation and the assignment-rule gap.

[8] This project, *Topological Derivation of the Fine-Structure Constant in the SRE Framework*: Möbius topological modelling (§3), the spectral-gap formula and the topological meaning of $n=60$ (§4), the final positioning of $\delta$ (§10).

[9] Particle Data Group, *Review of Particle Physics* (tables of charged-lepton and quark masses).

> **Citation discipline.** When using the references, the "$\approx$" in the original text must be copied verbatim and must not be transcribed as "equals".
