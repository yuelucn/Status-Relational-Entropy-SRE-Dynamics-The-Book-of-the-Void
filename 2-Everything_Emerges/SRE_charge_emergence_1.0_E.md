# Emergence of Positive and Negative Electric Charge in the SRE Framework: Magnitude, Sign, and Numerical Verification


Version: 1.0


> **Companion scripts**: `_sigma_deg_independence.py`, `_se_assignment_test.py` (both reuse the official skeleton `y3()` from §8 of *A Complete Characterization of the Nucleon in the SRE Framework*).

**Cited articles from *The Book of the Void***: https://zenodo.org/records/23137136
- *State-Relation Entropy (SRE) Dynamics: User Manual and Theoretical Background*
- *A Unified Theory of the Electronic Logical Structure and Physical Properties Based on an Instantiable Minimal Topological Scale*
- *A Fundamental Reconstruction of Classical Electrodynamics Based on Discrete Graph Topology and Bidirectional Causality*
- *A Rigorous Reconstruction of Maxwell's Field Equations Based on Pure Dimensionless Graph Cohomology and Global Evolution Steps*
- *The SRE Dynamical Topological Paradigm for Composite Elementary Particles and the Emergence of Relational Space*
- *A Complete Characterization of the Electron in the SRE Framework*
- *The Origin of Mass in the SRE System: A Cyclic Operator Formulation on the Three-Ring ℤ₃ Torsor*
- *The Positioning of Light and Electromagnetic Waves in the SRE System*
- *A Complete Characterization of the Nucleon in the SRE Framework* v2.1

---

## Abstract

SRE dynamics expresses electric charge as "the counting of topological knots" (*…Fundamental Reconstruction of Classical Electrodynamics*). Counting is naturally non-negative and yields only the **magnitude**, not the **sign**. This paper closes that gap and rigorously gives:

$$Q(K)=\sigma(K)\cdot\deg(K)\cdot e,\qquad \deg(K)=\beta_1(K)\bmod 2,\qquad \sigma(K)\in H^1(G;\mathbb{Z}_2).$$

Namely: **charge magnitude = the parity of the number of independent loops**; **charge sign = the ℤ₂ winding phase (holonomy)**. Thereby we obtain in closed form the electron $Q=-e$, the positron $Q=+e$, the proton $Q=+e$, the neutron $Q=0$, and the antiproton $Q=-e$, and we explain "the proton and the electron have the same charge magnitude while their masses differ by about a factor of 1836" (charge–mass decoupling). Two numerical tests confirm: **the sign channel and the magnitude channel are mutually independent** (§10.1); **the electron is forced by skeletal symmetry into the trivial holonomy class, while the proton falls into the non-trivial class** (§10.2), so that the opposite signs of the electron and the proton acquire a structural origin.

**Keywords:** State-Relation Entropy (SRE); electric charge emergence; topological knot; charge magnitude; charge sign; ℤ₂ holonomy (winding phase); Betti-number parity; Möbius closed loop; charge conjugation; charge–mass decoupling; graph homology; gauge convention.

---

## 1. Problem Statement and the Gap

### 1.1 Existing Formulation in the Original Works

- **Charge = counting of topological knots**: *A Fundamental Reconstruction of Classical Electrodynamics Based on Discrete Graph Topology and Bidirectional Causality* expresses the charge $Q$ as the count of specific nonlinear topological knots (node sets) in a graph, where electric current is the refresh frequency of knots crossing topological cut-sets.
- **Elementary charge $e\equiv1$**: *A Rigorous Reconstruction of Maxwell's Field Equations Based on Pure Dimensionless Graph Cohomology and Global Evolution Steps* formalizes $e$ as the unitary discrete increment $\Delta N=1$ of an isolated 0-chain under a single global evolution step $\Delta S=1$.
- **The electron's unit charge = outward topological bias**: *A Unified Theory of the Electronic Logical Structure and Physical Properties Based on an Instantiable Minimal Topological Scale* models the electron as a self-consistent Möbius closed loop, whose unit charge is the constant topological logical bias that this closed loop exerts outward.

### 1.2 Three Gaps

1. **Counting (non-negative) cannot carry a sign** — the original works give only the magnitude.
2. **Composite polarity-synthesis rules are missing** — one must give the charge generation for the proton and the neutron.
3. **The sign reference is not anchored** — "which orientation counts as positive" is undefined.

This paper uses only the SRE's own constructions (binary polarity, $\mathbb{F}_2$ group isomorphism, Möbius double cover, cut-set counting, μ-homology) as building materials, closing these gaps in sequence.

---

## 2. Preparatory Theory

### 2.1 Binary Self-Organizing Network

The underlying ontology is a strictly binary network: the instantaneous state is described by a real symmetric configuration matrix $\mathbf{M}_n$, whose entries are restricted to the spin-polarity set $\{+1,-1\}$; there exists no intermediate state with value 0 (Axiom I of *A Complete Characterization of the Electron in the SRE Framework*).

### 2.2 Polarity Multiplication Group and Isomorphism with $\mathbb{F}_2$

**Lemma 2.1 (Polarity–Boolean Isomorphism)** The map $\varphi:\{+1,-1\}\to\mathbb{F}_2$, $\varphi(S)\equiv\frac{1-S}{2}$ ($-1\mapsto1,\ +1\mapsto0$), is a group isomorphism $(\{+1,-1\},\cdot)\cong(\mathbb{F}_2,\oplus)$.

**Proof** See Appendix A. $\square$

**Corollary 2.2** "Multiplying polarities" and "adding modulo 2" are in strict one-to-one correspondence — the algebraic cornerstone for composing and merging polarities later on.

### 2.3 Möbius Closed Loop and holonomy

An electron-type closed loop possesses a Möbius double-layer phase structure: it requires completing $2N$ mutual measurements at the $\ell_{\min}$ scale before it returns to the initial state; $N$ times alone is insufficient (*A Unified Theory of the Electronic Logical Structure and Physical Properties Based on an Instantiable Minimal Topological Scale* §II). Its **overall holonomy is $-1$** (orientation reversal). This holonomy is a **topological invariant**: it depends only on the overall winding manner of the closed loop and is rigidly invariant under any internal deformation.

### 2.4 Graph Chain Complex, Cut-Set, and Homology

On the dimension-free state-relation graph: the chain complex $C_0,C_1,C_2$ and the boundary operator $\partial$; a **cut-set** $\Sigma$ is a set of 1-chains that separates the graph; charge, per *…Fundamental Reconstruction of Classical Electrodynamics*, is precisely "the count of knots crossing the cut-set."

---

## 3. Basic Definitions

**D1 (Closed-loop knot $K$)** A self-consistent Möbius topological closed loop, internally containing $\beta_1(K)$ independent causal cycles.

**D2 (Internal path count $N$, mass channel)** $N(K)\approx$ the cumulative number of closed-loop steps, with $m(K)\propto N(K)\cdot\ell_{\min}$ (*A Unified Theory of the Electronic Logical Structure and Physical Properties Based on an Instantiable Minimal Topological Scale* §III.1).

**D3 (Edge polarity)** The polarity of each edge $e$ is $s_e\equiv\operatorname{sign}\mathbf{M}_{ij}\in\{+1,-1\}$.

**D4 (Boundary holonomy $\sigma$, sign channel)**
$$\sigma(K)\equiv\prod_{e\in\partial K}s_e\in\{+1,-1\},$$
i.e., the product of the polarities of all edges on the closed loop (*A Complete Characterization of the Electron in the SRE Framework* §1.2, "ℤ₂ winding phase").

**D5 (Magnitude $\deg$, parity channel)**
$$\deg(K)\equiv\big(E-V+c\big)\bmod 2=\beta_1(K)\bmod 2,\qquad \beta_1=E-V+c.$$
Namely, **the parity of the number of independent loops (the first Betti number)**.

---

## 4. Axioms

**A1 (Charge functional)**
$$\boxed{\ Q(K)=\sigma(K)\cdot\deg(K)\cdot e\ },\qquad Q\in\mathbb{Z}e.$$

**A2 (Composite boundary recomputation law)** When $n$ knots merge into a composite knot $K_{\mathrm{comp}}$ due to phase-coherence saturation ($\rho\to1,\ D\to0$; *The SRE Dynamical Topological Paradigm for Composite Elementary Particles and the Emergence of Relational Space* §2), its charge is recomputed from the **new boundary**: $\sigma_{\mathrm{comp}}=\prod_i\sigma_i$ (by Lemma 2.1, i.e., $\mathbb{F}_2$ addition modulo 2), $\deg_{\mathrm{comp}}=\beta_1(K_{\mathrm{comp}})\bmod2$.

**A3 (Additivity under separation)** For mutually independent knots: $Q_{\mathrm{tot}}=\sum_i Q(K_i)$. This is the precondition for macroscopic electric neutrality.

**A0 (Sign reference anchor)** Prescribe that **the holonomy class to which the electron belongs** is "negative" (a gauge convention; see §8).

---

## 5. Magnitude Channel: $\deg=\beta_1\bmod 2$

### 5.1 Official Skeleton Inputs

- **Electron ontology $Q_3$**: $(V,E,\beta_1)=(8,12,5)$ (*A Complete Characterization of the Electron in the SRE Framework* §6).
- **Nucleon skeleton $Y_3\ltimes\triangle_3$** (*A Complete Characterization of the Nucleon in the SRE Framework* §8): closed state (proton) $(12,18,7)$, open state (neutron, with one loop-edge removed) $(12,17,6)$.
- **Many-body assembly law** (same work, §12): $V=9k+3,\ E=15k+3,\ \beta_1=6k+1$.

### 5.2 Closed Form

$$\boxed{\ \deg(K)\equiv\beta_1(K)\bmod 2\ }$$

### 5.3 Mechanism: the "Pairing Criterion" for Independent Loops

A knot is "neutralizable" if and only if its independent loops can be **paired and closed so as to cancel**, and pairing requires $\beta_1$ to be even. When $\beta_1$ is odd there is exactly one independent loop that **cannot be paired**, which bears the net winding number → net charge $\pm e$. This is consistent with two statements in the original works: "charge = cut-set counting" (what is counted is the loops that cannot be symmetrically cancelled); "polarity cancellation → neutral" (the precondition for pairwise cancellation is that loops can be paired).

Taking the parity (rather than $\beta_1$ itself) is necessary: a single charged knot always has $|Q|=e$ (a proton is not $7e$); the magnitude information of $\beta_1$ enters the **mass/internal-path** channel. This is the manifestation of **charge–mass decoupling** at the level of graph invariants.

### 5.4 Composite: Sum over Bodies

The many-body scaffold $\beta_1=6k+1$ is always odd and **cannot** be subjected to this criterion (otherwise it would misjudge "every composite is charged"). The composite charge is summed over **bodies** according to **A3**: each closed-state (proton) body contributes $\pm e$, each open-state (neutron) body contributes $0$ — consistent with "nuclear charge $Z$ = number of protons."

---

## 6. Sign Channel: $\sigma=$ ℤ₂ holonomy

### 6.1 Carrier: the ℤ₂ Winding Phase Native to the Theory

*A Complete Characterization of the Electron in the SRE Framework* §1.2 defines the "ℤ₂ winding phase": the product of the edge polarities along a closed loop equals $\pm1$; taking $-1$ means that one flip is experienced in going around once. Generalized to an arbitrary closed chain $\gamma$: $\sigma(\gamma)=\prod_{e\in\gamma}s_e$.

### 6.2 Group Structure

After mapping through $\varphi$ to $\mathbb{Z}_2$ values, $\sigma(\gamma)$ becomes a linear functional on $\gamma$; the collection of all such forms
$$H^1(G;\mathbb{Z}_2)=\operatorname{Hom}\big(H_1(G;\mathbb{Z}_2),\mathbb{Z}_2\big),\qquad |H^1|=2^{\beta_1}.$$
This agrees with the "homology ladder" $|H^1(G;\mathbb{Z}_n)|=n^{\beta_1}$ of *The Positioning of Light and Electromagnetic Waves in the SRE System* (with $n=2$).

### 6.3 Why Charge Falls on the ℤ₂ Rung

*The Positioning of Light and Electromagnetic Waves in the SRE System* **Theorem 2**: **light/electromagnetism take the ℤ₂ rung, mass takes the ℤ₃ rung** (two adjacent levels of the same homology ladder), and $\delta_A$ is "the emergent coupling strength of the ℤ₂ holonomy channel." Charge is the source of electromagnetic coupling, hence **the sign of charge naturally belongs to the ℤ₂ rung** — $\sigma$ lands on a channel already named by the theory.

---

## 7. Charge Conjugation $\mathcal{C}$ = holonomy Reversal

**Definition** $\mathcal{C}:\sigma\mapsto-\sigma$ (the unique non-trivial automorphism of $\{+1,-1\}$).

**Proposition 7.1** $\mathcal{C}$ sends $\sigma\to-\sigma$, whereas $\deg=\beta_1\bmod2$ is unchanged.

**Proof** $\{+1,-1\}$ is a group of order two; its unique non-trivial automorphism is negation, which sends every holonomy class to its opposite class; $\deg$ depends only on the graph, not on the edge assignment. $\square$

**Physical reading**: **charge conjugation = holonomy reversal**: $e^-\leftrightarrow e^+,\ p\leftrightarrow\bar p$.

---

## 8. Sign Anchor A0: Convention and Physical Content

### 8.1 Absolute Naming Is a Gauge Convention

Physics (including classical electromagnetism) determines only the **relative sign** (like signs repel / opposite signs attract); labeling some object as positive or negative is a gauge choice. The theory supplies the ℤ₂ quantum number; the absolute naming needs an anchor:

> **A0 (Convention)** Prescribe that **the holonomy class to which the electron belongs** is "negative."

### 8.2 Physical Content (Not Convention) — Already Numerically Confirmed in §10.2

| Relation | Theoretical content | Observation |
|---|---|---|
| electron vs positron | $\sigma$ opposite ($\mathcal{C}$) | opposite signs |
| proton vs antiproton | $\sigma$ opposite ($\mathcal{C}$) | opposite signs |
| electron vs proton | **holonomy classes opposite** (§10.2) | opposite signs |
| charged vs neutral | $\deg$ 1 vs 0 ($\beta_1$ odd vs even) | present / absent |

**The structural origin of "electron and proton have opposite signs" (already numerically confirmed)**:

- **The electron $Q_3$ is forced into the trivial class**: the cube is **edge-transitive** (its 12 edges lie in the same orbit under $\lvert\mathrm{Aut}\rvert=48$) ⇒ a symmetric-respecting $s_e$ assignment must be uniform; and because the cube is **bipartite** (all loop lengths even) ⇒ every loop's holonomy $=(+1)^{\text{even}}=+1$ ⇒ trivial class, and the non-trivial class is **unreachable**.
- **The proton $Y_3\ltimes\triangle_3$ admits the non-trivial class**: it contains a **triangle** (non-bipartite) plus **two edge orbits** (loop-edge / spoke, 9 each) ⇒ taking $s(\text{loop-edge})=-1$ yields on the triangle a holonomy $=(-1)^3=-1$ ⇒ the non-trivial class is reachable.

Namely: **electron in the trivial class (assigned negative) ↔ proton in the non-trivial class (assigned positive)**, uniquely determined by the skeleton automorphism structure.

---

## 9. Full Table (after anchoring A0)

| Particle | skeleton | $\beta_1$ | $\deg$ | holonomy class $\sigma$ | $Q$ |
|---|---|---|---|---|---|
| electron $e^-$ | $Q_3$ (edge-transitive + bipartite) | 5 | 1 | **trivial class** (A0 anchors −) | $-e$ |
| positron $e^+$ | $Q_3$, after $\mathcal{C}$ | 5 | 1 | non-trivial class (+) | $+e$ |
| proton $p$ | $Y_3\ltimes\triangle_3$ closed state | 7 | 1 | **non-trivial class** (+) | $+e$ |
| neutron $n$ | $Y_3\ltimes\triangle_3$ open state | 6 | 0 | (magnitude 0, sign meaningless) | $0$ |
| antiproton $\bar p$ | closed state, after $\mathcal{C}$ | 7 | 1 | trivial class (−) | $-e$ |

**Consistency**: $\mathcal{C}$ flips $\sigma$ row by row while keeping $\deg$ fixed ⇒ all particle/antiparticle pairs hold.

---

## 10. Numerical Verification

### 10.1 $\sigma$ and $\deg$ Are Mutually Independent (`_sigma_deg_independence.py`)

| object | V | E | $\beta_1$ (three algorithms agree) | $\deg$ | $\lvert H^1\rvert=2^{\beta_1}$ | $\sigma$ reachable |
|---|---|---|---|---|---|---|
| electron $Q_3$ | 8 | 12 | 5 | 1 | 32 | $\{+1,-1\}$ |
| proton closed state | 12 | 18 | 7 | 1 | 128 | $\{+1,-1\}$ |
| neutron open state | 12 | 17 | 6 | 0 | 64 | $\{+1,-1\}$ |

$\beta_1$ is cross-checked by three algorithms — $E-V+c$, real correlation rank, and $\mathbb{Z}_2$ correlation rank — all in agreement. **Verdict [SUCCESS]**: $(\deg,\sigma)$ spans a $1\times2^{\beta_1}$ product space — the magnitude channel is **1 bit**, the sign channel is **$\beta_1$ bit**, and they are independent; **there is no lock-in of the form $\sigma=(-1)^{\beta_1}$**.

### 10.2 The Holonomy Classes of Electron and Proton Are Opposite (`_se_assignment_test.py`)

Enumerate the edge-polarity assignments $s_e$ that **respect the automorphism group**, and find their $H^1(G;\mathbb{Z}_2)$ class:

| skeleton | $\lvert\mathrm{Aut}\rvert$ | edge orbits | bipartite | symmetric class: trivial | symmetric class: non-trivial |
|---|---|---|---|---|---|
| electron $Q_3$ | 48 | 1 (12 edges, same orbit) | True | reachable | **unreachable (forced trivial)** |
| proton closed state | 36 | 2 (9+9) | False | reachable | **reachable** |
| neutron open state | 4 | 7 | False | reachable | reachable |

**Verdict [SUCCESS]**: electron trivial class, proton non-trivial class — **opposite (OPPOSITE)**. Note: without the symmetry constraint both graphs contain non-trivial classes (electron $31/32$, proton $127/128$) — the difference comes from **symmetry admissibility**, not from $H^1$ capacity. **This upgrades F2 from a "structural side-by-side reading" to a "numerical confirmation."**

---

## 11. Conservation, Neutrality, $\delta_A$

- **Charge conservation**: $\sigma\in H^1(G;\mathbb{Z}_2)$ is additive as a $\mathbb{Z}_2$ functional under subgraph assembly; together with A3, the total charge is conserved.
- **Macroscopic electric neutrality**: the angular-element negative-feedback rule drives $\sum\sigma_i\deg_i\to0$ (the distribution of positive/negative holonomy classes is symmetrized).
- **Interface with $\delta_A$**: the $\delta_A=w^*-1=4.347\times10^{-5}$ of §2 of *The Positioning of Light and Electromagnetic Waves in the SRE System* is the **continuous coupling strength** of the ℤ₂ holonomy channel; the $\sigma$ of this paper is the **discrete rung** ($\pm1$) of that channel. Division of labor: **the discrete rung provides the sign and the quantization, the continuous coupling provides the coupling strength.**

---

## 12. Falsifiability Criteria

- **F1 ($\mathcal{C}$ theorem)** Particle and antiparticle have opposite $\sigma$ and identical $\deg$ ⇒ strictly opposite charge signs and equal magnitude. If an antiparticle pair of equal magnitude but not opposite sign is found, this is falsified.
- **F2 (opposite sign between different species) — confirmed in §10.2** The electron and the proton fall into opposite holonomy classes. If, within a larger skeleton family, a skeletal structure forces the two into the same class (same sign), this is falsified.
- **F3 (channel independence) — confirmed in §10.1** The capacity $2^{\beta_1}$ of the $\sigma$ channel is independent of the 1 bit of $\deg$. If $\sigma$ is found to be uniquely determined by $\beta_1$, this is falsified.
- **F4 (neutral = even $\beta_1$)** Neutral ⇔ $\beta_1$ even. If a case with even $\beta_1$ yet charged (or vice versa) is found, and it cannot be decomposed into co-located multiple knots, this is falsified.

---

## 13. Honest Boundaries

1. **Absolute sign is a convention.** What this paper closes is "the carrier and the relative structure of the sign," not the absolute naming (which is physically undeducible and of the same origin as the charge-conjugation convention).
2. **The "opposite class" relies on an explicit assumption.** The conclusion of §10.2 relies on "the physical $s_e$ assignment respects the skeleton automorphism group $\mathrm{Aut}$"; without this assumption, both graphs admit non-trivial classes, and the sign assignment falls back to physical input. This assumption is a discussable modeling choice.
3. **No fractional charge is produced.** This model gives integer $Q\in\mathbb{Z}e$ and cannot reproduce the quark's $\pm2/3,\pm1/3$. This is an ontology-difference hypothesis: SRE views fractional charge as "the averaged reading when three strands share one and the same closed loop" (*A Complete Characterization of the Nucleon in the SRE Framework* §4.2, conjecture Q2, not yet independently tested).
4. **Divergence from the nucleon paper v1.5 — CLOSED by §14.** That paper's §6 defines the open/closed two states as isospin structure **independent of charge**; this paper connects $\deg=\beta_1\bmod2$ to the charge magnitude (reading A). As proven in §14 (Proposition 6.1), the two Z₂'s are the *same* Z₂: open/closed ≡ one fewer independent loop ≡ parity flip ≡ charged/neutral. The isospin Z₂ is thus reinterpreted as the charge-magnitude Z₂; no conflict remains.
5. **Extracting the closed form has reached the mechanism level; quantitative benchmarking is left for later.** This is consistent with the quantitative lacuna left by *The SRE Dynamical Topological Paradigm for Composite Elementary Particles and the Emergence of Relational Space*.

---

## 14. Topological Derivation of the Nucleon Charges (Magnitude and Sign)

§9 gives the nucleon charge table by assertion and numerical check; this section supplies the **topological derivation** on the official nucleon skeleton $Y_3\rtimes\triangle_3$ (nucleon paper v1.5) using the functional $Q=\sigma\cdot\deg\cdot e$ established above. The full treatment — all measured invariants, the multi-body extension, and the honesty boundaries — is the companion document *Topological Derivation of the Nucleon Charges from the Charge-Emergence Functional* (`SRE_Nucleon_Charge_Derivation_E.md`).

### 14.1 Skeleton inputs

- **Proton** = **closed** $Y_3\rtimes\triangle_3$: $(V,E,\beta_1)=(12,18,7)$, non-bipartite, 2 edge orbits (9 ring + 9 spokes).
- **Neutron** = **open** $Y_3\rtimes\triangle_3$: one ring edge removed, $(12,17,6)$, still connected, 7 edge orbits.
- (Electron $Q_3$: $(8,12,5)$, bipartite, 1 edge orbit — from §9.)

### 14.2 Magnitude from $\beta_1$ parity

**Proposition.** $\deg=\beta_1\bmod 2$ is fixed solely by open/closed connectivity:
$$\deg(p)=7\bmod 2=1,\qquad \deg(n)=6\bmod 2=0.$$
The neutron has one fewer independent loop than the proton ⇒ parity flips ⇒ neutral. This is exactly the magnitude-side counterpart of nucleon-paper §6.3's "the $10^{-3}$ breaking comes from a missing loop".

### 14.3 Sign from holonomy class

- **Electron forced trivial** (§10.2): $Q_3$ is edge-transitive ($|\mathrm{Aut}|=48$) and bipartite ⇒ every Aut-respecting polarity assignment gives holonomy $+1$ ⇒ only the trivial class is reachable (measured: 1 class).
- **Proton allows non-trivial** (§10.2): the closed state contains a triangle (odd cycle) and has 2 edge orbits ⇒ choosing the ring-edge orbit $s=-1$ makes the triangle holonomy $-1$ ⇒ the non-trivial class is reachable (measured: 2 classes).
- With A0 (electron's class = "negative"), the electron/proton structural opposition fixes proton sign $=+$, electron sign $=-$ (§8.2).

### 14.4 Charge table and charge conjugation

| Particle | $\beta_1$ | $\deg$ | $\sigma$ | $Q$ |
|---|---|---|---|---|
| proton $p$ | 7 | 1 | non-trivial $(+)$ | $+e$ |
| neutron $n$ | 6 | 0 | moot | $0$ |
| antiproton $\bar p$ | 7 | 1 | trivial $(-)$ | $-e$ |

$\mathcal C:\sigma\mapsto-\sigma$ flips particle/antiparticle pairs; the neutron ($\deg=0$) is $\mathcal C$-invariant.

### 14.5 Closing the §13 divergence: isospin Z₂ ≡ charge-magnitude Z₂

Nucleon paper v1.5 §6 marks open/closed as an isospin Z₂ "independent of charge"; §13 (item 4) here attached $\deg=\beta_1\bmod 2$ to charge magnitude. **Ruling (Proposition 6.1):** they are the same Z₂ — open/closed ≡ one fewer loop ≡ parity flip ≡ charged/neutral. The isospin Z₂ is thus reinterpreted as the charge-magnitude Z₂; the mass breaking ($10^{-3}$) lives in the dynamical layer, not the topological charge layer. No conflict; the §13 divergence is closed.

### 14.6 Multi-body: A3 body-sum gives nuclear charge $Z\cdot e$

The multi-body scaffold $V=9k+3,\ E=15k+3,\ \beta_1=6k+1$ is **always odd** ($k\ge1$), so the single-knot criterion "neutral ⇔ $\beta_1$ even" cannot be applied to the whole scaffold. By A3, sum over nucleon **bodies**:
$$Q_{\rm nucleus}=\sum_{\text{proton bodies}}(+e)+\sum_{\text{neutron bodies}}(0)=Z\cdot e,$$
with $Z$ = number of proton bodies. Neutron bodies ($\deg=0$) contribute nothing — exactly "neutrons are uncharged". A re-computable script verification is provided in `SRE-charge-emergence/_nucleon_multibody_charge.py`.

---

## Appendix A: Complete Proof of the $\mathbb{F}_2$ Isomorphism

Let $S\in\{+1,-1\}$, $B=\varphi(S)=(1-S)/2$.

1. Bijection: $-1\mapsto1$, $+1\mapsto0$.
2. Homomorphism: $\varphi(S_1S_2)=\dfrac{1-S_1S_2}{2}$, and
$$\varphi(S_1)\oplus\varphi(S_2)=\frac{1-S_1}{2}+\frac{1-S_2}{2}-2\cdot\frac{1-S_1}{2}\cdot\frac{1-S_2}{2}=\frac{1-S_1S_2}{2}.$$
3. Inverse map: $\varphi^{-1}(B)=1-2B$. Hence $\varphi$ is a group isomorphism. $\square$

## Appendix B: Notation Table

| symbol | meaning | channel |
|---|---|---|
| $K$ | closed-loop knot | — |
| $\beta_1=E-V+c$ | first Betti number (number of independent loops) | magnitude |
| $\deg=\beta_1\bmod2$ | charge magnitude (0/1) | magnitude (1 bit) |
| $s_e=\operatorname{sign}\mathbf{M}_{ij}$ | edge polarity $\pm1$ | sign |
| $\sigma=\prod_{e\in\partial K}s_e$ | boundary holonomy $\in\{\pm1\}$ | sign ($H^1$, $\beta_1$ bit) |
| $Q=\sigma\cdot\deg\cdot e$ | charge functional | boundary (ℤ₂ × parity) |
| $\mathcal{C}:\sigma\mapsto-\sigma$ | charge conjugation | — |
| $N$ | internal path count | mass $m\propto N\ell_{\min}$ |

## Appendix C: Mapping Table to the Chapters of *The Book of the Void*

| point of this draft | corresponding chapter (article name + section) |
|---|---|
| charge = cut-set counting | *A Fundamental Reconstruction of Classical Electrodynamics Based on Discrete Graph Topology and Bidirectional Causality* |
| elementary charge $e\equiv1$ | *A Rigorous Reconstruction of Maxwell's Field Equations Based on Pure Dimensionless Graph Cohomology and Global Evolution Steps* |
| electron unit charge = outward topological bias; Möbius 2N | *A Unified Theory of the Electronic Logical Structure and Physical Properties Based on an Instantiable Minimal Topological Scale* §II, §III |
| ℤ₂ winding phase; $Q_3$ ontology; Axiom I (binary constraint) | *A Complete Characterization of the Electron in the SRE Framework* §1.2, §6 |
| three-strand Y skeleton; open/closed two states; assembly law; $N_c=3$=number of strands | *A Complete Characterization of the Nucleon in the SRE Framework* v2.1 §6, §8, §12, §4.2 |
| light/electromagnetism take ℤ₂, mass takes ℤ₃; homology ladder; δ_A | *The Positioning of Light and Electromagnetic Waves in the SRE System* Theorem 2, §2 |
| three-ring ℤ₃ torsor (cyclic structure of the three generations) | *The Origin of Mass in the SRE System: A Cyclic Operator Formulation on the Three-Ring ℤ₃ Torsor* |
| double closed-loop composite particle (mass amplification) | *The SRE Dynamical Topological Paradigm for Composite Elementary Particles and the Emergence of Relational Space* §2 |

---

**One-sentence conclusion**:
$$\sigma\in H^1(G;\mathbb{Z}_2),\quad \deg=\beta_1\bmod 2,\quad Q=\sigma\cdot\deg\cdot e.$$
In the SRE framework, **positive and negative charges are the synthesis of two independent invariants on the boundary of one and the same topological knot — the ℤ₂ holonomy gives the sign, and the parity of $\beta_1$ gives the magnitude**; the electron is forced by skeletal symmetry into the trivial class, the proton falls into the non-trivial class (opposite), charged versus neutral is decided by the parity of $\beta_1$, and particle/antiparticle reverse sign through $\mathcal{C}$. Two numerical tests confirm that the sign and the magnitude are independent, and that the electron and proton classes are opposite.
