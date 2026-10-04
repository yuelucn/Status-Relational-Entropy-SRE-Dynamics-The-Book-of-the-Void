# Mass Origin in the State–Relational–Entropy Framework

## A Circulant-Operator Formulation on the Three-Ring ℤ₃ Torsor

**Version: 1.0 (Treatise Format)**
**Date: 2026-09-28**

---

## Abstract

**Background and problem.** Within the State–Relational–Entropy (SRE) framework, mass is treated as a **projected reading** of relational structure rather than an ontological input, and therefore in principle it should not be a number given in advance. However, the question "since mass is an emergent quantity, what exactly is its precise mathematical object?" had not previously been answered head-on. This paper answers that question and places the answer in a recomputable, falsifiable form.

**Method.** This paper takes the SRE nucleon skeleton $Y_3\ltimes\triangle_3$ ($V=12$, $E=18$, $\beta_1=7$, $|\mathrm{Aut}|=36$) as its only structural input. It first proves that the three shared rings of this skeleton form a **ℤ₃-torsor** under the automorphism group — there is a cyclic order but no absolute origin; then, taking "respecting that structure" as the constraint, it derives the unique admissible form of the mass operator and sets out its spectrum, invariants and external comparisons.

**Results.** The paper gives four mutually independent, verifiable propositions: (1) **the object proposition** — a mass operator that respects the three-ring structure must commute with the cyclic shift $S$, and "commuting with $S$" holds if and only if it is a **circulant matrix**; hence $A=c_0\mathbb{1}+c_1S+\bar c_1S^{2}$, and ℤ₃-equivariance compresses 9 matrix entries into 3; (2) **the shape proposition (with one correction)** — the spectrum of a Hermitian circulant is a set of 120° samples of one cosine, $\lambda_j=c_0+2|c_1|\cos(\theta+2\pi j/3)$, but **this form holds trivially for any three generations** (three points, three unknowns, always solvable), so the "cosine shape" is a **free reparameterisation** rather than a constraint; (3) **the opening proposition** — writing the amplitude multiset as an ordered triple is equivalent to choosing an origin for the DFT characters, and the three choices give **exactly the same invariants**, so "opening" is a ℤ₃ **gauge degree of freedom** rather than information; (4) **the invariant proposition** — the invariant moduli space is **two-dimensional**, $(\eta,\ \delta\bmod 2\pi/3)$, and the Koide combination $Q=\tfrac13+\tfrac23\eta^{2}$ probes only the single direction $\eta$. Measurement on the charged leptons gives $\eta^{2}=1/2$ to within $3.3\times10^{-6}$.

**Boundary and conclusion.** The paper also states two limitations that must be made explicit: **the cosine shape is free** (so the entire content of Koide collapses to **a single number** $\eta=1/\sqrt2$); and **absolute mass (the scale $c_0$) does not lie inside SRE**, while **only renormalization-group-invariant dimensionless combinations qualify as candidate targets**. The overall conclusion is registered as **case 15 of the discrete-closure law (G12)**: "three" and the functional form are given (discrete side, closed), while the value of $\eta$ and the scale are not (continuous side, requiring external input). All numerical verification in this paper **holds only within the SRE model**, and comparisons with charged-lepton masses are always stated as "structural consistency" rather than "numerical prediction".

**Keywords**: State–Relational–Entropy (SRE); mass origin; circulant matrix; ℤ₃-torsor; triality; Koide relation; gauge degree of freedom; renormalization-group invariant; discrete-closure law.

---

## 1. Introduction

### 1.1 Statement of the problem

This paper answers the following proposition (raised 2026-09-28):

> **Original proposition.** The mass described by SRE is an evolutionary logic that is **unopened and cyclic**. What, then, is its precise mathematical description and expression?

This proposition combines three independently decidable sub-problems:

| No. | Sub-problem | Corresponding section |
|---|---|---|
| **P1** | What **mathematical object** should mass be expressed as? | §4 (Theorem 2) |
| **P2** | What precisely does "**cyclic**" mean here? | §4.4 (Proposition 3) |
| **P3** | Which operation does "**unopened**" omit? | §6 (Propositions 5, 6) |

### 1.2 Existing characterisations and their predicament

In the prior work of this project, three conclusions relating to mass already exist, but all of them remain at the level of **ratios** and do not touch the **object** itself:

| Clue | Conclusion | Source |
|---|---|---|
| Graph functional | The three rings lie in one orbit ⇒ any graph functional gives the three rings **the same value** ⇒ $Q$ collapses to the Cauchy–Schwarz lower bound $\tfrac13$ | Rounds 29, 30 [10][14] |
| Ledger | The information that the three generations have **unequal** masses can only be carried by **explicit bookkeeping**; graph functionals are **structurally blind** to it | Rounds 30, 31 [11] |
| Koide relation | $Q=\tfrac13+\tfrac23\eta^{2}$, independent of phase; $Q=\tfrac23\iff\eta^{2}=\tfrac12$ | Round 30 [10], ref. [1] |

These three clues point together to an object that is **not yet named**: it is **not** three mass numbers, and **not** an invariant of any graph functional, but an **operator carrying the cyclic relation between the three generations**. The task of this paper is to name and characterise that object precisely.

The most naive scheme is to regard "the three-generation masses" as an **ordered triple** $(m_0,m_1,m_2)$. This paper shows that the scheme is inaccurate at two levels:

1. **Ontological level**: there is no origin for "which generation" inside the SRE structure. The three rings are indistinguishable under $\mathrm{Aut}$ (§3.1), and imposing labels introduces an **artificial origin**;
2. **Covariance level**: the output of SRE should **not depend** on artificial labels (objectivity / covariance).

The correct object should **carry a cyclic structure of its own and presuppose no origin** — and this is exactly how a **circulant matrix** is defined: it is characterised by "commuting with the cyclic shift", it does not itself single out an origin; an origin is introduced only at the moment of **reading** (spectral decomposition), and the manner of introduction is a gauge degree of freedom.

### 1.3 Contributions of this paper

Relative to the existing material, this paper gives four substantive items:

1. **It establishes "three rings = ℤ₃-torsor" as a structural theorem** (Theorem 1), with an explicit witness and character decomposition (Propositions 1, 2);
2. **It makes the mass operator unique** (Theorem 2): "respecting the structure" directly forces a circulant matrix, with centraliser dimension exactly $n=3$;
3. **One correction** (Theorem 3): it proves that "three points lie on one cosine" is a **free reparameterisation valid for any three generations**, and thereby narrows the content to be explained by Koide from "the shape" **down to a single number** $\eta=1/\sqrt2$;
4. **One screening rule** (Theorem 5): only renormalization-group-invariant dimensionless combinations qualify as candidate targets, which clarifies the scope of the negative verdict on the quark side.

### 1.4 Structure of this paper

Section 2 gives the skeleton definition, notation and adjudication discipline, and builds intuition through an **analogy guide**; Section 3 proves the ℤ₃-torsor structure of the three rings (first pillar); Section 4 proves the unique form of the mass operator (second pillar); Sections 5, 6 and 7 respectively treat the spectrum and the "free cosine", the boundary between "unopened" and "opened", and the invariant moduli space; Section 8 compares with charged-lepton data; Section 9 discusses the boundary on the quark side; Section 10 locates the single gap and gives falsification criteria; Sections 11 and 12 are discussion and conclusion. Appendix A is the recomputation list, Appendix B the honesty boundary, Appendix C the **analogy index**, Appendix D the references.

**Notation convention**: numbers followed by "**(proven, within-model)**" can all be recomputed in one command by the script in Appendix A; those marked "**(to be proven)**" are structural hypotheses proposed here but not yet delivered; those marked "**(negative verdict)**" are propositions already falsified or explicitly delimited as non-computable.

---

## 2. Preliminaries

### 2.1 The basic stance of SRE and the skeleton definition

SRE regards a physical object as a stable emergent state of a **binary self-organising network** in relational space, rather than a point particle placed in space in advance. Within this framework, "the foundations of classical physics originate from information statistics": geometry, charge, current, mass and the like are all treated as **projected readings** of relational structure rather than ontological inputs. This paper uses only one concrete product of that stance: **the nucleon skeleton and its open/closed two states**.

**Definition 1 (nucleon skeleton $Y_3\ltimes\triangle_3$).** The skeleton is formed by **three** Y-shaped coherent cores closed into a **triangle**. Its vertex set and edge set are

$$\mathcal{V}=\{c_0,c_1,c_2\}\cup\{L_{ij}:\ i,j\in\{0,1,2\}\},\qquad |\mathcal{V}|=12,$$

where $c_i$ is the **hub** of the $i$-th strand and $L_{ij}$ is the **ring leaf** at position $j$ of strand $i$. The edges fall into two classes:

- **strand edges** (hub–leaf): $c_i\!-\!L_{ij}$, 3 per strand, 9 in total;
- **ring edges** (leaf–leaf): ring $j$ is the triangle $\{L_{0j},L_{1j},L_{2j}\}$, 3 per ring, 9 in total.

Hence $E=18$, $\beta_1=E-V+1=7$, $|\mathrm{Aut}|=36$ (proven, within-model); the spectral readings are $\rho=5.302775638$, $\lambda_2=1$, $\Pi_1=\lambda_2/\rho=0.188580485$.

**Definition 2 (open/closed two states).** The **closed state** is the graph above, corresponding to the SRE proton state; the **open state** means removing one ring edge from the skeleton (here we fix the removal of $(L_{0r},L_{1r})$, $r=0$), so that $E=17$, $\beta_1=6$, corresponding to the neutron state.

The full derivation of the skeleton (how integer-ness of the vertex number, the spectral ratio and triple symmetry jointly screen out the unique survivor) is given in §7–§8 of the project's nucleon paper [12] and is not repeated here. All that is needed here are **two properties**:

1. the three rings form **a single orbit** under $\mathrm{Aut}$ (closed state) — the three rings are **mutually indistinguishable**;
2. there exists in $\mathrm{Aut}$ an **edge-preserving automorphism of order 3**.

Together these are equivalent to: **the three rings are a ℤ₃-torsor**. This is the **only** structural input of the whole paper.

### 2.2 Notation

**Table 1.** Table of symbols used throughout.

| Symbol | Meaning |
|---|---|
| SRE | State–Relational–Entropy, the parent framework of this paper |
| $Y_3\ltimes\triangle_3$ | the nucleon skeleton (Definition 1) |
| $L_{ij}$ | the ring leaf at position $j$ of strand $i$ |
| ring $j$ | the triangle $\{L_{0j},L_{1j},L_{2j}\}$; there are three (**the three rings**) |
| $S$ | the **cyclic shift** on the three rings, $S^{3}=\mathbb{1}$ |
| $A$ | the **mass operator** (the central object of this paper) |
| $\varphi$ | the explicit order-3 automorphism $L_{ij}\mapsto L_{i,\,j+1}$ (§3.2) |
| $\mathrm{Aut}$ | the automorphism group of the skeleton |
| $\mathrm{Circ}(n)$ | the space of $n$-th order circulant matrices, $\dim=n$ |
| $\omega$ | the cube root of unity $e^{2\pi i/3}$ |
| $\eta,\ \delta$ | the **amplitude ratio** and **phase** of the non-trivial component of the circulant operator: $c_1=|c_1|e^{i\theta}$, $\eta=|c_1|/c_0$ |
| $Q$ | the **Koide combination** $Q=\dfrac{\sum m}{(\sum\sqrt m)^{2}}$ |
| $\rho,\ \lambda_2,\ \Pi_1$ | spectral radius, second-smallest Laplacian eigenvalue, closure degree $\Pi_1=\lambda_2/\rho$ |
| D1／D2／D3 | adjudication discipline: small-denominator rationals listed separately／angles may not serve as anchors／the main statistics use only irrational readings × clean targets |

### 2.3 Analogy guide: three-phase alternating current

Before entering the formal argument, we set up a **system that can be checked in daily life**, in order to fix the intuition behind all the wording that follows. The system chosen is **symmetric three-phase alternating current** — which is not an analogical resemblance to the ℤ₃ structure of this paper, but a **real instance of the same algebra**.

**Analogy 1 (three-phase alternating current).** Let the three phase voltages be

$$u_A(t)=U\cos\omega t,\qquad u_B(t)=U\cos\!\Big(\omega t-\frac{2\pi}{3}\Big),\qquad u_C(t)=U\cos\!\Big(\omega t+\frac{2\pi}{3}\Big).$$

In phasor representation, introducing the operator $a=e^{2\pi i/3}$, the three phase phasors are exactly $U,\ Ua,\ Ua^{2}$. This operator satisfies two identities:

$$a^{3}=1,\qquad 1+a+a^{2}=0 .$$

Comparing with the notation of this paper, $a=\omega$, and $1+a+a^{2}=0$ corresponds exactly to the $\sum_k\cos(\delta+\tfrac{2\pi k}{3})=0$ used in §5.1. The three-phase system serves three demonstrative purposes for this paper:

1. **Cyclic but with no origin.** The phase sequence $A\to B\to C$ is cyclic: rename A as B and B as C, and **every physical quantity is unchanged**. That is, "which phase is called the first" **has no physical meaning** (= the **gauge degree of freedom** of this paper), whereas "the three phases differ by $120^\circ$" **does** have physical meaning (= the **torsor structure** of this paper).
2. **Decomposition is DFT.** The method of symmetrical components (Fortescue) uses $a$ to decompose any three-phase signal into **positive-, negative- and zero-sequence** parts. Mathematically this decomposition is exactly the **third-order discrete Fourier transform**; its consequence is that every permutation-invariant, scale-invariant property of a three-phase system **can only** be determined by the amplitudes of these three components.
3. **The cost of "opening" is zero.** Since "which is the first phase" is a convention, **writing the three phases as an ordered triple** **adds no information whatsoever** — and this is precisely the proposition proved in §6 of this paper (opening = gauge, not information).

**Example 1 (cosine reparameterisation of three numbers, toy example).** Take the data $u=(1,\ 1.2,\ 0.7)$. Form the transform $z=\sum_k u_k\omega^{-k}$; measurement gives $|z|=0.435890$, $\arg z=-1.455835$ rad, so that

$$\bar u=\tfrac13\textstyle\sum_k u_k=0.966667,\qquad |c_1|=\tfrac{|z|}{3}=0.145297,\qquad \theta=-\arg z=1.455835\ \mathrm{rad}.$$

Substituting back into $u_k=\bar u+2|c_1|\cos\!\big(\theta+\tfrac{2\pi k}{3}\big)$ gives the multiset $\{1.000000,\ 1.200000,\ 0.700000\}$, consistent with the input (proven, within-model). Two points must be noted here first: (i) **any three numbers can be reparameterised in this way**, a triviality formally proved in Theorem 3; (ii) the **order** of the inverse output depends on the choice of origin (here the reconstructed order is $(1,\ 0.7,\ 1.2)$, different from the input arrangement), while **the multiset is unaffected** — and this is the simplest instance of the "opening = gauge" argument of §6.

### 2.4 Methodological discipline: the discrete-closure law (G12)

All results of this paper can be located by a methodological discipline already established in the project:

> **Discrete-closure law (G12).** Every link "discrete structure ⇒ discrete target" is **closed** within SRE; each crossing of "discrete → continuous" **must pay one external input**.

The role of this law is **division of labour**: for any result, it must be possible to say which half is given by SRE (the discrete side) and which half must be paid in externally (the continuous side). Section 11.4 will locate all conclusions accordingly.

---

## 3. First pillar: the three rings = a ℤ₃-torsor

### 3.1 Orbit structure of the automorphisms

Fully enumerating the automorphisms of the closed-state and open-state skeletons respectively gives

**Table 2.** Skeleton invariants and three-ring orbit structure for the two states (proven, within-model).

| State | $V$ | $E$ | $\beta_1$ | $|\mathrm{Aut}|$ | order-3 elements | order-2 elements | three-ring orbits |
|---|---|---|---|---|---|---|---|
| closed (proton) | 12 | 18 | 7 | **36** | **8** | 15 | **1 orbit: $\{0,1,2\}$** |
| open (neutron) | 12 | 17 | 6 | **4** | **0** | 3 | **2 orbits: $\{0\}\mid\{1,2\}$** |

In the closed state, the permutation induced by $\mathrm{Aut}$ on the three rings is **all six** (i.e. $S_3$); in the open state only two remain.

Columns 4, 6 and 7 of **Table 2** are the source of every structural argument in this paper and must be checked one by one: for the closed state $|\mathrm{Aut}|=36=2^{2}\cdot3^{2}$, of which the **order-3 elements number 8** (Sylow-3 subgroup $\cong\mathbb{Z}_3\times\mathbb{Z}_3$); for the open state $|\mathrm{Aut}|$ falls to 4 and the **order-3 elements vanish**. The number of three-ring orbits changes from 1 to 2, the most vivid trace left by "closed → open" at the structural level.

### 3.2 Explicit witness

**Proposition 1 (explicit order-3 automorphism).** The map

$$\varphi:\ L_{ij}\mapsto L_{i,\,(j+1)\bmod 3},\qquad c_i\mapsto c_i$$

is an **edge-preserving** automorphism of the skeleton, and $\mathrm{ord}(\varphi)=3$.

*Proof.* It suffices to verify each item. (i) **Vertex-preserving**: $\varphi$ is a bijection on $\mathcal V$. (ii) **Strand-edge preserving**: $c_i\!-\!L_{ij}\mapsto c_i\!-\!L_{i,j+1}$, still within the strand-edge set. (iii) **Ring-edge preserving**: the triangle $\{L_{0j},L_{1j},L_{2j}\}$ of ring $j$ is sent to $\{L_{0,j+1},L_{1,j+1},L_{2,j+1}\}$, i.e. ring $j+1$, still a triangle. (iv) **Order 3**: $\varphi^{3}(L_{ij})=L_{i,j+3}=L_{ij}$, while $\varphi\ne\mathrm{id}$. $\square$

The measured result is: edge-preserving = true, $\mathrm{ord}(\varphi)=3$ (proven, within-model). This is a genuine order-3 automorphism, and it acts **freely and transitively** on the three rings (sending ring $j$ to ring $j+1$).

### 3.3 The structural theorem

> **Theorem 1 (ℤ₃-torsor structure of the three rings).** The three rings of the closed-state skeleton form a **ℤ₃-torsor**: there is a **cyclic order** among them, but **no absolute origin**; their only degree of freedom is an **overall phase shift**.

*Proof.* Denote the three rings by the 3-element set $R=\{R_0,R_1,R_2\}$. By Proposition 1, $\langle\varphi\rangle\cong\mathbb{Z}_3$ acts on $R$; since $\varphi(R_j)=R_{j+1}$, the action is **transitive** (orbit $=R$). And since $|R|=3=|\langle\varphi\rangle|$, the stabiliser is trivial, so the action is **free**. A set acted on **freely and transitively** by a group $G$ is by definition a $G$-torsor: it carries the structure of a **principal homogeneous space** for $G$ — any two points are related by a unique $g\in G$, but **there is no base point fixed by the group action**. Taking $G=\mathbb{Z}_3$ gives the claim. $\square$

Theorem 1 is the structural foundation of the entire paper. It gives the precise source of the shape of "three generations": **the three generations carry a ℤ₃ cyclic order, but no absolute origin** — the origin is precisely the overall phase shift, corresponding to the phase $\delta$ in the Koide parameterisation below.

**Analogy 2 (a three-strand braid and a clock face).** In a braid woven from three strands, any strand may be named "the first", while the **interlacing relation** of the braid is unchanged; an object with "a cyclic order but no identifiable first strand" is a torsor. Another everyday instance is the **directions on a clock face**: the phrase "the three o'clock direction" is meaningful only after agreeing where "twelve o'clock" is — elements of a torsor are likewise such that one can speak of "how far apart" but not of "where".

### 3.4 Character decomposition under ℤ₃

Let $\varphi$ have character equal to the number of fixed points $\chi(\varphi)$ on some real permutation representation space. For $G=\mathbb{Z}_3$ (generator $\varphi$), the regular decomposition of the representation is $1+\omega+\omega^{2}$, hence

$$\mathrm{mult}(\text{trivial})=\tfrac13\big(\dim+2\chi\big),\qquad \mathrm{mult}(\omega)=\mathrm{mult}(\omega^{2})=\tfrac13\big(\dim-\chi\big).$$

$\varphi$ fixes the three hubs $c_i$ and fixes no ring leaf, so for the vertex space $\chi=3$; no edge is fixed by $\varphi$, so for the edge space $\chi=0$. Measurement gives

**Table 3.** Character decomposition of ℤ₃ on the vertex and edge spaces (proven, within-model).

| Space | $\dim$ | $\chi(\varphi)$ | decomposition | trivial weight | non-trivial weight |
|---|---|---|---|---|---|
| vertex | 12 | 3 | $6\cdot1+3\omega+3\omega^{2}$ | $6/12=\mathbf{1/2}$ | $\mathbf{1/2}$ |
| edge | 18 | 0 | $6\cdot1+6\omega+6\omega^{2}$ | $6/18=\mathbf{1/3}$ | $\mathbf{2/3}$ |

**Proposition 2 (structural reading of the character decomposition).** The weights above can be read off directly from the construction of the skeleton.

*Proof.* The skeleton = 3 strands × (1 hub + 3 ring leaves). The hubs are fixed by $\varphi$, so each hub contributes one copy of the trivial representation; the ring leaves are cycled by $\varphi$, so the three ring leaves of each strand contribute one copy of the regular representation $1+\omega+\omega^{2}$. Hence per strand the trivial multiplicity is $1+1=2$ and the non-trivial multiplicity is $1+1=2$, so the **vertex space splits $1/2\mid1/2$**. Edge side: the strand edges $c_i\!-\!L_{ij}$ are sent to $c_i\!-\!L_{i,j+1}$ and the ring edges to the corresponding edges of the next ring, so **all edges are moved away by $\varphi$** ($\chi=0$); hence the edge representation is 6 copies of the regular representation, with trivial weight $1/3$ and non-trivial weight $2/3$. $\square$

**Note 1 (registration discipline).** The values $1/2$, $1/3$, $2/3$ in Table 3 are all **small-denominator rationals** (the D1 trap) and **have no discriminating power** on their own. Their possible meaning is registered in the candidate chain of §11.2; this paper **does not upgrade them to conclusions**.

---

## 4. Second pillar: the unique form of the mass operator

The conclusions of this chapter were first given in the form of a working note [13]; this paper reorganises them into treatise form, supplies the complete proof, and corrects one over-claim in them (see Theorem 3).

### 4.1 The main theorem

> **Theorem 2 (circulant criterion).** Let $S$ be the $n$-th order cyclic shift matrix. Then an $n\times n$ matrix $A$ commutes with $S$ ($AS=SA$) **if and only if** $A$ is a circulant matrix, i.e. $A$ is completely determined by its first row:
> $$A=c_0\mathbb{1}+c_1S+c_2S^{2}+\cdots+c_{n-1}S^{n-1}.$$

*Proof.* Write $S$ for the permutation matrix sending the basis vector $e_j$ to $e_{j+1}$ (indices mod $n$). If $A$ is circulant, then $A=\sum_kc_kS^{k}$, which obviously commutes with $S$. Conversely, suppose $AS=SA$. Take the first row of $A$ to be $(a_0,a_1,\dots,a_{n-1})$; comparing column by column from $AS=SA$ gives $a_{ij}=a_{0,\,j-i\bmod n}$, i.e. row $i$ of $A$ is the first row cyclically shifted right $i$ times, hence $A=\sum_k a_{0,k}S^{k}$. $\square$

**Numerical verification ($n=3$).** Writing the constraint $AS-SA=0$ as a homogeneous linear system in $\mathrm{vec}(A)$,

$$\big(S^{\mathsf T}\!\otimes I-I\otimes S\big)\,\mathrm{vec}(A)=0,$$

measurement gives **rank 6** for this coefficient matrix in the 9-dimensional space, so the solution space has dimension $=9-6=\mathbf{3}=n$; taking a basis of the null space and reshaping it into matrices, **all of them are circulant** (the check is true) (proven, within-model).

The substance of Theorem 2 is a quantification of **constraining power**: $\mathbb{Z}_3$-equivariance compresses the $n^{2}=9$ matrix entries down to $n=3$. This is the **entire** constraining power carried by the word "cyclic" in SRE — no more, no less.

### 4.2 Necessity of the mass operator

By §3.3 the three rings are a ℤ₃-torsor. A mass operator that **respects that structure** (does not conflict with the cyclic shift) is by definition one that "commutes with $S$"; by Theorem 2 it **can only** be a circulant matrix. Taking the Hermitian form (whose necessity is shown in §5.2):

> **Corollary 1 (object proposition).** The unique admissible form of the mass operator is
> $$A=c_0\mathbb{1}+c_1S+\bar c_1S^{2},\qquad c_0\in\mathbb{R}.$$

This is not a language that has been picked, but a result **forced by the structure**. At this point sub-problems **P1 (object)** and **P2 (cyclic)** both have precise names.

**Example 2 (a concrete mass operator).** Take $c_0=1$, $c_1=0.3\,e^{i\cdot40^\circ}$; then

$$A=\begin{pmatrix}1 & 0.3e^{i40^\circ} & 0.3e^{-i40^\circ}\\[2pt] 0.3e^{-i40^\circ} & 1 & 0.3e^{i40^\circ}\\[2pt] 0.3e^{i40^\circ} & 0.3e^{-i40^\circ} & 1\end{pmatrix}.$$

The matrix is **determined by only two real numbers** ($c_0$ and $|c_1|$, plus the phase $\theta$), whereas a $3\times3$ matrix has 9 entries in general. Its measured eigenvalues are

$$(0.436184,\ 1.104189,\ 1.459627)\quad(\text{ascending}),$$

matching term by term the analytic form of Proposition 4, $\lambda_j=1+0.6\cos(40^\circ+120^\circ j)$ (proven, within-model). This $3\times3$ matrix is the **smallest writable instance** of the "mass" asserted in this paper.

### 4.3 Why "evolution" is cyclic (a group) rather than one-way (a semigroup)

The word "evolution" easily suggests a time arrow, so its precise meaning must be made clear.

**Table 4.** One-way evolution versus cyclic evolution.

| | one-way evolution (semigroup $\mathbb{N}$) | cyclic evolution (group $\mathbb{Z}_3$) |
|---|---|---|
| starting point | yes ($t=0$) | **no** |
| reversible | no | **yes** ($S^{-1}=S^{2}$) |
| closed | no | **yes** ($S^{3}=\mathbb{1}$) |
| carrier | a directed interval | **a cyclic group action on a torsor** |

**Proposition 3 (answer to P2).** The so-called "cyclic evolutionary logic" is mathematically the use of a **group (ℤ₃) rather than a semigroup** to characterise the index space.

*Proof.* The defining element of a semigroup is "there exists an irreversible starting point", whereas the defining element of the group $\mathbb{Z}_3$ is "$S^{3}=\mathbb{1}$, $S^{-1}=S^{2}$, and no element is fixed by the action". By Theorem 1, the three rings are exactly a $\mathbb{Z}_3$-torsor, so their index space possesses only the second set of properties. $\square$

This conclusion also explains the "**absence** of opening": once an origin is introduced or an ordered labelling taken, the cycle degenerates into a **linear sequence with a starting point** — and that is precisely "opening" (§6).

**Analogy 3 (a wheel versus an hourglass).** The typical image of semigroup evolution is an **hourglass**: the sand flows in one direction only, start and end are asymmetric, and it is irreversible. The typical image of group evolution is a **wheel with three equal divisions on its rim but no mark for "twelve o'clock"**: every rotation can be turned back, three rotations return to the start, and **no division on the dial is special**. The mass discussed in this paper belongs to the latter.

---

## 5. The spectrum and the "free cosine"

### 5.1 Spectral form

**Proposition 4 (spectrum of a Hermitian circulant).** Let $A=c_0\mathbb{1}+c_1S+\bar c_1S^{2}$ with $c_0\in\mathbb R$, $c_1=|c_1|e^{i\theta}$. Then the eigenvalues of $A$ are

$$\lambda_j=c_0+c_1\omega^{j}+\bar c_1\omega^{-j}=c_0+2|c_1|\cos\!\Big(\theta+\frac{2\pi j}{3}\Big),\qquad j=0,1,2.$$

*Proof.* The eigenvectors of $S$ are the discrete Fourier basis $v_j=(1,\omega^{j},\omega^{2j})^{\mathsf T}/\sqrt3$, with eigenvalues $\omega^{j}$ ($j=0,1,2$). Any polynomial in $S$ shares these eigenvectors, so $A v_j=\big(c_0+c_1\omega^{j}+\bar c_1\omega^{-j}\big)v_j$. Using $\omega^{-j}=\overline{\omega^{j}}$, we get $c_1\omega^{j}+\bar c_1\omega^{-j}=2\,\mathrm{Re}\big(c_1\omega^{j}\big)=2|c_1|\cos(\theta+2\pi j/3)$. $\square$

Numerical verification (6 random parameter sets against the analytic form): all Hermitian checks true, maximum error $1.1\times10^{-15}$ (proven, within-model).

The intuitive reading of **Proposition 4** is: **the three eigenvalues lie on the 120° samples of one and the same cosine**.

### 5.2 Real-symmetric versus complex phase: why a phase is necessary

**Proposition 5 (real-symmetric degeneracy).** If $A$ is a real-symmetric circulant (i.e. $\theta=0$), its spectrum **always has two values**:

$$\big(c_0+2|c_1|,\ \ c_0-|c_1|,\ \ c_0-|c_1|\big).$$

*Proof.* At $\theta=0$, $\lambda_0=c_0+2|c_1|$, while $\lambda_1=c_0+2|c_1|\cos(2\pi/3)=c_0-|c_1|$ and $\lambda_2$ is the same (since $\cos(4\pi/3)=\cos(2\pi/3)$). $\square$

Measured comparison: the real-symmetric choice $c_0=1,|c_1|=0.3$ gives the spectrum $(0.7,\,0.7,\,1.6)$, a **2+1** split; the complex phase $\theta=1$ gives the spectrum $(0.400668,\ 1.27515,\ 1.324181)$, a **1+1+1** split (proven, within-model).

> Proposition 5 directly answers "why a phase is needed": **the spectrum of a real-symmetric circulant degenerates structurally and cannot carry three distinct generations; for the three generations to be distinct the operator must be Hermitian rather than real-symmetric** (thereby giving the Hermitian form of Corollary 1 its necessity).

**Note 2 (registration, not conclusion).** Proposition 5 and the "closed-state ℤ₃ ／ open-state ℤ₂" of Table 2 echo each other at the level of operators: the open state has only two values (a $\mathbb{Z}_2$-type degeneracy), the closed state generally three (the full $\mathbb{Z}_3$). This paper has **not proved** that the two are the same mechanism (see Appendix B item 4) and merely registers the observation.

### 5.3 A correction that must be stated: the cosine shape is "free"

**Theorem 3 (triviality of the shape).** The trigonometric form $\lambda_k=c_0+2|c_1|\cos(\theta+\tfrac{2\pi k}{3})$ has a solution for **any** three real numbers $\lambda_0,\lambda_1,\lambda_2$; that is, the form **contains no constraint whatsoever**.

*Proof.* Given the data $\lambda_k$, form

$$\sum_k\lambda_k=3c_0,\qquad z:=\sum_k\lambda_k\,\omega^{k}=3|c_1|e^{-i\theta},$$

i.e. $c_0=\overline{\lambda}$, $|c_1|=|z|/3$, $\theta=-\arg z$. The three unknowns ($c_0,|c_1|,\theta$) exactly match the three data, so generically the solution is unique and is given explicitly by the formulas above. $\square$

Measurement: taking 8 random sets of **arbitrary** three numbers, solving by the formulas above and substituting back to reconstruct, the maximum error is of order $10^{-15}$ (the companion script of this paper gives $5.11\times10^{-15}$, a preceding script $2.22\times10^{-15}$, the same order of magnitude) (proven, within-model).

> **Correction (direct consequence of Theorem 3).** "Three points lie on one cosine" is **not** a constraint delivered by cyclicity, but the **standard reparameterisation of three numbers**. Hence saying "ℤ₃ gives the shape of Koide" is an **over-claim**. The **content** of Koide is not the shape but the number
> $$\eta=\frac{|c_1|}{c_0}=\frac{1}{\sqrt{2}}\qquad(\text{measured }0.707104444\ \text{vs}\ 0.707106781,\ \text{deviation}\ -2.34\times10^{-6}).$$

Thus the true contribution of ℤ₃ collapses to two items: **(a) why there are exactly 3 positions** (the torsor has size 3, not 2 or 4); **(b) why $\delta$ is gauge** (a torsor has no origin ⇒ the phase can only be taken mod $2\pi/3$). **The shape is trivial; "$\eta=1/\sqrt2$" is the number that genuinely awaits explanation** — and it belongs to the **continuous side** of G12.

**Analogy 4 (a prism and dispersion).** The mass operator may be compared to a composite light beam made by mixing three pure colours in fixed proportions: without spectral decomposition you see only its **overall hue and brightness** (= permutation-invariant, scale-invariant quantities); performing the DFT is like **passing the beam through a prism**, and the three eigenvalues are the intensities of the three emerging beams. What Theorem 3 says is: **any set of three intensities corresponds to some composite beam** — the dispersing step contains no information, it merely restates the same thing in another language.

**Note 3 (D1 discipline).** $\eta=1/\sqrt2$ is irrational (consistent with adjudication discipline D3); but $\eta^{2}=1/2$ together with the $1/3$, $2/3$ in $Q$ are still small-denominator rationals, so the numerical agreement **does not count as independent evidence**. The gain of this section is **structural**: separating the "trivial shape" from the "real content".

---

## 6. "Unopened" and "opened": the boundary between gauge and information

### 6.1 Opening = choosing the DFT origin

**Proposition 6 (gauge-independence of opening).** Writing the **multiset** of amplitudes $\{\lambda_0,\lambda_1,\lambda_2\}$ as an **ordered triple** is equivalent to choosing an **origin** for the characters $\omega^{k}$; there are 3 choices of origin, and the three choices give **exactly the same** permutation invariants.

*Proof.* Let $(u_0,u_1,u_2)$ be one representative; the others are given by the cyclic shift $u^{(s)}_k=u_{k-s}$. For any function $F$ depending only on the multiset (e.g. the Koide combination $Q$ and the $R$ of §7.1), multiset invariance gives $F(u^{(s)})=F(u)$ immediately. $\square$

Measurement: taking $\eta=1/\sqrt2$, $\delta=2/9$, the three representatives give

**Table 5.** Invariants under the three choices of DFT origin (proven, within-model).

| representative (cyclic shift) | $Q$ | $R=(\lambda^{2}_{\max}-\lambda^{2}_{\min})/\sum\lambda^{2}$ |
|---|---|---|
| shift 0 | 0.666666666667 | 0.943349649589 |
| shift 1 | 0.666666666667 ($|\Delta Q|=2.2\times10^{-16}$) | 0.943349649589 |
| shift 2 | 0.666666666667 ($|\Delta Q|=0$) | 0.943349649589 |

⇒ **the three choices give three representatives of one and the same equivariance class.** Hence "opening" changes no SRE observable; it only decides "which generation is called the first" — **this is gauge (redundancy), not information**.

### 6.2 The two levels of "opening" must not be conflated

**Table 6.** Strict distinction between the two kinds of "opening".

| Level | Operation | Consequence |
|---|---|---|
| **(i) gauge level** | choosing an origin = ℤ₃ labelling | invariants **unchanged** (redundancy) — this is the level the original proposition refers to |
| **(ii) physical level** | closed → open (cutting one ring edge) | $|\mathrm{Aut}|$ falls from 36 to 4, order-3 elements from 8 to 0: a **real** breaking ℤ₃→ℤ₂ that **changes** the accessible invariants |

**Analogy 5 (transposition of a score).** The **interval structure** of a melody is unchanged by an overall transposition — after transposition it is still "the same piece". Choosing an origin for the DFT characters is like **fixing the tonic**: it decides "which generation is the tonic" without changing the internal structure of the piece; whereas the physical-level "opening" of §6.2 (cutting a ring) is different, being like **rewriting the score itself** — the structure of the piece really changes.

### 6.3 "Not opened" is not a defect but covariance

Combining §§6.1–6.2, we can answer **P3**:

> **Proposition 7 (answer to P3).** "Not opened" = **no eigenbasis (DFT origin) chosen**, and the SRE native output stops at the **multiset** level.

This contains two things of entirely different nature that were previously often conflated; this paper separates them completely:

- **Gauge undetermined** (the ℤ₃ choice of $\delta$) ⇒ the SRE output **does not depend on artificial labels**. This is an **advantage** (objectivity / covariance), **not a deficiency**;
- **Scale ungiven** ($c_0$) ⇒ this is the **real information gap**, and lies **outside SRE** (§9 has settled: absolute mass is not its responsibility).

---

## 7. Invariants and the moduli space

### 7.1 The output of "unopened" = the equivariance class

Take the parameterisation $\lambda_k=1+2\eta\cos(\delta+\tfrac{2\pi k}{3})$ ($c_0$ already normalised; the scale is an external input). The following two quantities are invariant under **permutation** and under **overall scale**, and their measured behaviour is as follows.

**Table 7.** The invariant $Q$ is immune to the phase $\delta$ (sweeping $\delta$ over a full turn).

| $\eta$ | range of $Q$ over $\delta$ | $Q$ | analytic value $\tfrac13+\tfrac23\eta^{2}$ |
|---|---|---|---|
| 0.30 | $3.3\times10^{-16}$ | 0.393333333 | 0.393333333 |
| 0.50 | $6.1\times10^{-16}$ | 0.500000000 | 0.500000000 |
| $1/\sqrt2$ | $1.2\times10^{-15}$ | 0.666666667 | 0.666666667 |
| 0.80 | $1.6\times10^{-15}$ | 0.760000000 | 0.760000000 |

**Table 8.** The invariant $R$ depends on $\delta$ (with $\eta=1/\sqrt2$ fixed).

| $\delta$ | $Q$ | $R$ |
|---|---|---|
| 0.0 | 0.666666667 | 0.957106781 |
| 0.4 | 0.666666667 | 0.880903092 |
| 0.8 | 0.666666667 | 0.633929534 |
| 1.2 | 0.666666667 | 0.566017302 |

### 7.2 Correction: the moduli space is two-dimensional

> **Proposition 8 (dimension of the invariant moduli space).** The invariant moduli space is
> $$\big(\eta,\ \delta\!\!\mod\tfrac{2\pi}{3}\big),$$
> that is, **two-dimensional**.

*Proof.* By §7.1, $Q$ depends only on $\eta$ and not on $\delta$ (the order of magnitude $\sim10^{-15}$ of the range in Table 7 confirms strict independence); while Table 8 shows that $R$ varies monotonically with $\delta$ at fixed $\eta$, so $\delta\!\!\bmod 2\pi/3$ is a second invariant **independent** of $\eta$. The sum of the two parameters is the dimension of the moduli space. $\square$

> **Correction.** A previous reading of "SRE has only one invariant, $Q$" is an **over-simplification**. The correct statement is: $Q$ **probes only the one direction $\eta$** (because it is immune to $\delta$, and the triple permutation of $\delta$ is precisely the source of permutation invariance); $\delta\!\!\bmod\tfrac{2\pi}{3}$ is a second independent direction.

### 7.3 A typology of invariance

**Table 9.** The invariance of various quantities and the layer they live in.

| Quantity | Immune to | Layer |
|---|---|---|
| $\rho$ (spectral radius) | **cutting a ring** (range over 18 cuts $\sim10^{-15}$) | spectral layer |
| $\Pi_1=\lambda_2/\rho$ | graph isomorphism ($\mathrm{Aut}$) | spectral layer |
| $Q$ (Koide) | **ℤ₃ origin** (triple permutation of $\delta$) | torsor / map layer |
| $\eta^{2}$ | ℤ₃ origin | torsor layer |
| **absolute mass $c_0$** | — (immune to no structure) | **outside SRE** |

The reading of **Table 9** is: **the quantities SRE can give internally all have "immunity to some structure" as their content**; and **the one quantity immune to no structure** (absolute mass $c_0$) is precisely the one **not belonging to SRE**. This table corresponds item by item to the gap of §10.

**Analogy 6 (an altitude datum and relative height).** The sentence "this mountain is 1000 m high" presupposes agreeing where "sea level" is; changing the datum from sea level to some valley floor changes every absolute height, while **the ratio of the relative heights of two mountains is unchanged**. The quantities SRE can give internally ($\Pi_1$, $Q$, $\eta$) are **relative quantities** (datum-independent); the absolute mass $c_0$ is an **absolute altitude** — it must first have an external datum to be meaningful. This is also the intuitive root of the "$\alpha$ has an anchor, mass has none" discussion of §11.3: the fine-structure constant is a **ratio** (datum-independent), whereas the absolute scale of mass is not.

---

## 8. The Koide relation and the charged leptons

### 8.1 Analytic derivation

**Theorem 4 (Koide relation).** Let $\lambda_k=c_0+2|c_1|\cos(\delta+\tfrac{2\pi k}{3})$ and $m_k\propto\lambda_k^{2}$. Then

$$Q=\frac{\sum_k m_k}{\big(\sum_k\sqrt{m_k}\big)^{2}}=\frac13+\frac23\eta^{2},\qquad \eta=\frac{|c_1|}{c_0}.$$

*Proof.* From $\sum_k\cos(\delta+\tfrac{2\pi k}{3})=0$ and $\sum_k\cos^{2}(\delta+\tfrac{2\pi k}{3})=\tfrac32$ we directly get

$$\sum_k\lambda_k=3c_0,\qquad \sum_k\lambda_k^{2}=3c_0^{2}+6|c_1|^{2}.$$

Substituting into the definition of $Q$ (note $\sqrt{m_k}\propto\lambda_k$, so the denominator $=\big(\sum\lambda_k\big)^{2}$):

$$Q=\frac{\sum_k\lambda_k^{2}}{\big(\sum_k\lambda_k\big)^{2}}=\frac{3c_0^{2}+6|c_1|^{2}}{9c_0^{2}}=\frac13+\frac23\Big(\frac{|c_1|}{c_0}\Big)^{2}. \square$$

The point of **Theorem 4** is: $Q$ **depends only on $\eta=|c_1|/c_0$ and not at all on the phase $\delta$**. This is a direct consequence of the ℤ₃ invariance property — by Proposition 8, $Q$ probes only the $\eta$ direction in the moduli space. In particular,

$$Q=\tfrac23\iff\eta^{2}=\tfrac12\iff\frac{|c_1|}{c_0}=\frac{1}{2\sqrt2}.$$

**Note 4 (one piece of empirical content).** "Taking $m_k\propto\lambda_k^{2}$ (i.e. $a=\sqrt m$ rather than $m$)" is the **empirical content of Koide**, equivalent to the testable structural hypothesis that "**the square root of the mass operator** is ℤ₃-equivariant". This paper **has not proved** it (see Appendix B item 2).

### 8.2 The equivalence chain: five ways of writing one constraint

$$Q=\tfrac23\ \Longleftrightarrow\ \eta^{2}=\tfrac12\ \Longleftrightarrow\ |A|=\tfrac{1}{\sqrt2}\ \Longleftrightarrow\ \text{angle with }(1,1,1)=45^\circ\ \Longleftrightarrow\ Q\ \text{at the midpoint of the C–S interval}\ [\tfrac13,1].$$

**Note 5.** The five items of this chain are **five languages for the same constraint**, **not five independent pieces of evidence**. They must not be listed side by side as mutually corroborating evidence.

**Analogy 7 (forty-five degrees is the "midpoint deviation").** Denote by $\phi$ the angle between the vector $(\sqrt{m_0},\sqrt{m_1},\sqrt{m_2})$ and the equal-mass direction $(1,1,1)$. $\phi=0^\circ$ corresponds to three equal generations ($Q$ takes the C–S lower bound $\tfrac13$, the spectrum degenerates), $\phi=90^\circ$ to the largest possible deviation ($Q$ takes the upper bound $1$); and $45^\circ$ is exactly the **midpoint** of this interval. The Koide relation can therefore be read as: **the square-root mass vector of the three generations stops exactly midway between "equal mass" and "maximal deviation"**. This is the two sides of one coin with the "real-symmetric degeneracy ⟺ complete equal mass" of §5.2 Proposition 5.

### 8.3 Comparison with charged-lepton data

Taking the PDG charged-lepton masses $m_e=0.51099895069$ MeV, $m_\mu=105.6583755$ MeV, $m_\tau\in\{1776.86,\ 1776.93\}$ MeV [9]:

**Table 10.** Recomputing the Koide combination for the charged leptons (proven, within-model).

| Input | $Q$ | $\eta^{2}=(3Q-1)/2$ | deviation vs $\tfrac23$ | angle with $(1,1,1)$ |
|---|---|---|---|---|
| $m_\tau=1776.86$ MeV (archive convention) | 0.666660511 | 0.499990767 | $-6.155\times10^{-6}$ | $44.9997^\circ$ |
| $m_\tau=1776.93$ MeV | 0.666664463 | **0.499996695** | $-2.203\times10^{-6}$ | $44.9999^\circ$ |

⇒ $\eta^{2}=\tfrac12$ holds on the real data to within $3.30\times10^{-6}$; the inverse solution gives $\eta=0.707104444$ against $1/\sqrt2=0.707106781$, a deviation of $-2.34\times10^{-6}$.

**Example 3 (a complete recomputation).** Take $m_\tau=1776.93$ MeV. Then

$$\sum_k m_k=1883.099374,\qquad \sum_k\sqrt{m_k}=0.7148419+10.2790260+42.1536475=53.147515435,$$

$$Q=\frac{\sum_k m_k}{\big(\sum_k\sqrt{m_k}\big)^{2}}=\frac{1883.099374}{2824.658397}=\mathbf{0.666664463}.$$

The inverse solution gives $\eta^{2}=(3Q-1)/2=0.499996695$, differing from $\tfrac12$ by $3.3\times10^{-6}$ (proven, within-model).

### 8.4 The phase (supporting evidence)

From $u_k=\dfrac{\sqrt{m_k}/a_0-1}{\sqrt2}=\cos(\delta+\tfrac{2\pi k}{3})$ and the DFT $z=\sum_k u_k\omega^{-k}=\tfrac32 e^{i\delta}$, the phase can be solved for. Measurement:

**Table 11.** Sensitivity of the phase solution to the "labelling convention".

| Labelling convention | $\delta\ (\mathrm{mod}\ 2\pi/3)$ | reference value $2/9$ | deviation |
|---|---|---|---|
| ascending $(e,\mu,\tau)$ | **0.222224762** | 0.222222222 | $+2.54\times10^{-6}$ |
| descending $(\tau,\mu,e)$ | 1.872170340 | 0.222222222 | $+1.65$ (wrong convention) |

**Note 6 (D1 discipline).** $2/9$ is a small-denominator rational, and its agreement with $\delta$ **must not** serve as independent evidence; moreover $\delta$ is itself a **gauge quantity** (an overall phase shift = a permutation of the three generations). This paper registers it only as supporting evidence. (Registered together: $2/9=\tfrac23\cdot\tfrac13$ is the product of two SRE structure constants, likewise in the D1 domain, registered only.)

**Table 11** also demonstrates an operational warning: **using the wrong labelling convention (here the descending one) makes the phase deviate by $1.65$ rad** — i.e. the "same $\delta$" is a **completely different** number under a wrong origin. This is the practical manifestation of the "gauge undetermined" of §6.3, and it is also why every test using $\delta$ as a target must first fix the convention.

### 8.5 Strength levels of the theorem

- **Proven (within-model)**: $Q=\tfrac13+\tfrac23\eta^{2}$ is independent of the phase; $Q=\tfrac23\iff\eta^{2}=\tfrac12$.
- **Consistent with data**: $\eta^{2}=\tfrac12$ holds to $3.3\times10^{-6}$ — **structural consistency, not numerical prediction**.
- **Not proven**: why $\eta^{2}$ is exactly $\tfrac12$ (see §10).

---

## 9. Boundary: the quark side and dimensions

### 9.1 The precise meaning of "emergent" in this project

According to the three ontological speculations of SRE (project nucleon paper §4 [12]), quarks are an **emergent statistical phenomenon** rather than an independent ontology: $N_c=3$ is the **number of strands**, "flavour" is a statistical projection of open/closed breaking, and "fractional charge" is an equal-share reading of the three-strand shared loop. Hence "quark mass" **cannot** be an input of SRE and can only be an output. Outputs fall into two classes that must be sharply distinguished:

**Table 12.** Visibility of the two classes of output.

| Output type | Nature | Can it see "which ring"? |
|---|---|---|
| **graph functional** ($\lambda_2,\beta_1,\rho,\Pi_1$) | automorphism invariant | **blind** (points in the same orbit take the same value) |
| **ledger** (explicit bookkeeping of edges) | not an invariant | **yes** |

**Table 12** is the skeleton of all the conclusions: any information of the kind "the three generations have unequal masses" **cannot structurally be given by graph functionals** and can only be carried by the ledger. This law is of the same type as "the product graph does not remember the partner state ⇒ the binding energy can only be carried by the ledger" (project nucleon paper §12 [12]).

### 9.2 The graph level: the degenerate baseline $Q=1/3$

The 9 ring edges of the closed-state skeleton lie in **a single automorphism orbit** (Table 2) ⇒ **any graph functional** gives the three rings **the same value** ⇒ $m_1=m_2=m_3$ ⇒

$$Q=\frac{3m}{(3\sqrt m)^{2}}=\frac13 \qquad(\text{proven, within-model}).$$

This is exactly the **Cauchy–Schwarz lower bound** of the Koide combination (the equal-mass limit).

**Note 7 (the double-identity trap of $1/3$).** The $1/3$ here is the **C–S lower bound** (the equal-mass limit), which is **different in origin** from the SRE $\Pi_1(Q_3)=1/3$ (**closure degree**) and **must not be identified with it**. The numerical coincidence is pure chance, and any reasoning that treats the two as mutually corroborating is void.

### 9.3 The ledger level: the splitting exists, but the rule is not written down

$$Q=\underbrace{\tfrac13}_{\text{graph baseline (degenerate)}}+\underbrace{\tfrac23\eta^{2}}_{\text{ledger splitting}}$$

Inverting $Q$ for $\eta^{2}=(3Q-1)/2$ gives a self-consistency check:

**Table 13.** Inverse solution of $\eta^{2}$ for three classes of objects (proven, within-model).

| Object | $Q$ | $\eta^{2}$ | reference point |
|---|---|---|---|
| charged leptons (pole masses) | 0.666667 | **0.500000** | $\eta^{2}=1/2\Leftrightarrow Q=2/3$ |
| heavy quarks $(c,b,t)$ @own scale | 0.662748 | 0.494122 | deviation $-0.6\%$ |
| light quarks $(u,d,s)$ @2 GeV | 0.567043 | 0.350564 | near $\eta^{2}=1/3\Leftrightarrow Q=5/9$ |

⇒ the splitting **does exist and has the right order of magnitude**, but the numerical origin of $\eta^{2}$ is still the single real gap (§10).

### 9.4 Quarks have one more wall than leptons

Lepton masses are **pole masses** (physical quantities, scheme-independent); the "mass" of a quark is the **MS-bar running mass** (**scheme-dependent + scale-dependent**) — so it **cannot even be settled whether it is the same quantity**. This is exactly the **C2 negative verdict** recorded long ago in the project.

Changing the convention for the same physical problem, $Q$ can move from 0.34 to 0.89 (proven, within-model): PDG MS-bar gives $Q(u,d,s)=0.5670$, $Q(c,b,t)=0.6627$; unified to $M_Z$, $Q(c,b,t)=0.7195$; taking naive **constituent quark masses** gives $Q(u,d,s)=0.3378$. This is not a matter of error bars but of **the quantity itself having no unique definition**.

**Analogy 8 (measuring the same mountain from different datum surfaces).** The situation above is like measuring the same mountain from three datums — sea level, some valley floor, a neighbouring peak — and obtaining three heights that are all "correct" yet mutually unequal. When a quantity **has no unique definition**, any "agreement" that uses it as a target constitutes no evidence — this is the substance of tollgate C2.

### 9.5 A positive result: only RG-invariant dimensionless combinations qualify as targets

**Theorem 5 (invariance of the scale).** The Koide combination is invariant under an overall scale:

$$Q(c\,m_0,\ c\,m_1,\ c\,m_2)=Q(m_0,m_1,m_2)\qquad\forall c>0.$$

*Proof.* The numerator $\sum c\,m_k=c\sum m_k\propto c$; the denominator $\big(\sum\sqrt{c\,m_k}\big)^{2}=\big(\sqrt c\sum\sqrt{m_k}\big)^{2}=c\big(\sum\sqrt{m_k}\big)^{2}\propto c$. The two cancel, and the ratio is independent of $c$. $\square$

Numerical verification ($c=10^{-3}\ldots10^{6}$): residual $\le1.1\times10^{-16}$ (proven, within-model).

**Corollary 2 (screening rule for RG-invariant targets).** The mass anomalous dimension of QCD $\gamma_m$ is **flavour-independent**, so the running of the light quarks $u,d,s$ is **multiplication by a common factor** ⇒ **$Q_{\text{light}}$ is a renormalization-group invariant**.

**Corollary 2** explains a past failure: in the probe $(2m_u+m_d)/m_p$ the denominator is the **external hadronic scale** $m_p$, so going from 2 GeV to 1 GeV changes the value by $+23\%$, and back-solving the number of strands $V$ jumps from 12 to 16 (negative verdict). But $Q_{\text{light}}$ is a **pure quark-mass ratio**, RG-invariant. **The two are not quantities of the same kind**: the earlier negative verdict was correct, but it **does not implicate** $Q_{\text{light}}$.

> **Screening rule.** Only **renormalization-group-invariant dimensionless combinations** qualify as candidate targets. Absolute values, same-scale ratios, and combinations containing a hadronic scale ($m_p$, $\Lambda_{\mathrm{QCD}}$) are all excluded.

### 9.6 A caveat that must be retained: "light quarks ≈ 5/9" is only an interval-level agreement

Taking the PDG asymmetric errors and enumerating the 8 corners: the centre of $Q_{\text{light}}$ is $0.567043$, the interval $[0.545962,\ 0.586139]$, and $5/9=0.555556$ **lies inside the interval**, but the central value deviates by $+2.07\%$ (proven, within-model). This differs from the lepton one (deviation $3.3\times10^{-6}$) by **three orders of magnitude**. Hence "≈ $5/9$" can only serve as a **loose target**, not a precision hit.

Literature side: Rodejohann and Zhang once put "heavy quarks $Q\approx2/3$" into a preprint and **deleted it themselves at publication** [8]; and for "heavy quarks" the deviation degrades from $0.6\%$ to $7.9\%$ after the scale is moved — a full order of magnitude.

---

## 10. The single real gap: the assignment rule

### 10.1 Balance sheet of this paper

**Table 14.** State of attainment at each level.

| Level | Content | Status |
|---|---|---|
| object | mass = the circulant operator on the three-ring torsor $c_0\mathbb{1}+c_1S+\bar c_1S^{2}$ | **named, form unique (Theorem 2)** |
| number of positions | exactly 3 (the torsor has size 3) | **proven (structural)** |
| gauge | $\delta$ is a ℤ₃ gauge (no origin) | **proven (structural)** |
| functional form | $Q=\tfrac13+\tfrac23\eta^{2}$, independent of $\delta$ | **proven (within-model)** |
| the value of $\eta$ | why $\eta^{2}=\tfrac12$ | **not proven — the single real gap** |
| scale | $c_0$ (absolute mass / energy scale) | **outside SRE (must be paid in externally)** |

### 10.2 Precise statement of the gap

The gap is an **assignment rule** — a rule connecting "the **representation** of ℤ₃ (edge $\tfrac13\mid\tfrac23$, vertex $\tfrac12\mid\tfrac12$, Table 3)" to "$m_k$ / the order parameter $A$". That is to say:

> SRE already gives **everything on the discrete side** (why there are 3 positions, why $\delta$ is gauge, the functional form), but does not give the step "**representation weight → real measured value**". This step is what G12 calls the **continuous-side payment**.

### 10.3 Three hard criteria

Any work claiming to have written down the assignment rule must **simultaneously** satisfy:

1. **it must produce exactly 3 generations** (not 2 or 4);
2. **it must give $\eta^{2}=\tfrac12$ and explain its origin** — $\tfrac12$ **must not** be taken as an input;
3. **it must give zero-parameter predictions for the three quark generations and the three neutrino generations** (light quarks $\approx5/9$, heavy quarks $\approx2/3$ already have measurements (Table 13) ⇒ it can be **immediately falsified out of sample**).

> The statement of criterion 2 is one substantive narrowing of this paper: since Theorem 3 proves that "the cosine shape holds trivially for any three generations", **in future it is no longer necessary to explain "why the shape is a cosine"; it is only necessary to explain "why $\eta=1/\sqrt2$" — this one number**.

---

## 11. Discussion

### 11.1 Relation to external work

The ℤ₃ structure identified in this paper is not isolated in the literature.

**Table 15.** The form in which ℤ₃ / three generations appears in each work.

| Work | In what form ℤ₃ / three generations appears |
|---|---|
| Koide 1981 [1] | $\sqrt{m_k}\propto1+\sqrt2\cos(\delta+\tfrac{2\pi k}{3})$ — that $\tfrac{2\pi k}{3}$ **is ℤ₃** |
| McRae 2025 [2] | "triality may be viewed as multiplication of a basis by a third root of unity, just as duality is often multiplication by a second root of unity" — **duality = ℤ₂, triality = ℤ₃** |
| Thorwe 2026 (DVFT) [3] | the natural ℤ₃ of a three-component vacuum field ⇒ phase $120^\circ$ ⇒ **circulant mass matrix** ⇒ Koide |
| Rousselle 2026 [4] | $U(3)_F\to U(1)_F^{3}$, equivalent to "crystallising" the vacuum to $Z(SU(3))=\mathbb{Z}_3$ |
| Ma 2006 [5] | four ℤ₃ generators → the group $\Sigma(81)$ |
| Sumino 2009 [6] | $U(3)\times O(3)$ family gauge symmetry; a $45^\circ$ geometric reading |
| Libanov–Troitsky 2000 [7] | three generations from a **topological defect with topological number 3** (index theorem: number of zero modes = topological number) |

This paper differs from them in **where it lands**: the works above generally take ℤ₃ / circulant matrices as a **starting point** from which to construct mass matrices, whereas the ℤ₃ of this paper is **read off from the automorphism group of the SRE skeleton** (three rings = ℤ₃-torsor). That is to say, this paper provides a **structural source for "why a circulant mass matrix should appear"**, rather than yet another construction of a circulant mass matrix.

### 11.2 Candidate chain registered (D1 caution, not upgraded)

$$Q=\tfrac13+\tfrac23\eta^{2}\ \ \text{(Theorem 4)},\qquad (\tfrac13,\tfrac23)\leftarrow\text{the }\mathbb{Z}_3\text{ weights of the edge representation},\qquad \eta^{2}=\tfrac12\leftarrow\text{the trivial weight of the vertex representation (Table 3)}.$$

If the three are **of the same origin**, then $Q=\tfrac13+\tfrac23\cdot\tfrac12=\tfrac23$ holds **automatically**.

**But this paper explicitly does not accept the chain**, for the reason: $1/3$, $2/3$, $1/2$ are **all small-denominator rationals** (the D1 trap) and **have no discriminating power** on their own. The **only** reason for registering them as a candidate is that the three pieces happen to join into the complete chain $Q=2/3$; **to upgrade it to a conclusion, a mechanism must be found elsewhere**, connecting "the edge representation / vertex representation" to "$m_k$ / the order parameter $A$" (i.e. the assignment rule of §10). Otherwise it is of the same type as "integer ≈ integer" and is not accepted.

The role of **Table 3** must therefore be precisely delimited: it is **the registration of one link of a candidate chain**, not one of the conclusions of this paper.

### 11.3 Contrast with the "anchor" system

In the project's earlier anchor work, the only quantity satisfying a "constant ↔ single invariant" type of relation is the **fine-structure constant**:

$$\alpha=\Pi_1(M_{60})=7.2974585\times10^{-3}\qquad(\text{relative deviation }1.45\times10^{-5}\text{ from the CODATA value }7.2973526\times10^{-3}),$$

solving $\Pi_1(M_n)=\alpha$ gives $n^{*}=60.000436$ (proven, within-model). Here $M_{60}$ is the 60-vertex Möbius ladder, whose closed form is

$$\Pi_1(M_n)=\frac{4\sin^{2}(2\pi/n)}{2+2w+2\cos(2\pi/n)}\Big|_{w=1}.$$

**Mass has no such anchor** — and the reason is exactly the typology of Table 9: $\alpha$ is a **dimensionless ratio** (SRE can give it internally), whereas the **absolute scale $c_0$ of mass is immune to no structure** (outside SRE).

**Analogy 9 (why a clock can be an anchor but "a pile of lengths" cannot).** A pendulum clock can serve as a time standard because its pendulum length and period are **locked together into a ratio** — once locked, the external "second" is brought into physics through that ratio. This is the mechanism of an "anchor": **connecting an external constant to an internal structural invariant**. The mass discussed in this paper lacks exactly such a lock: $c_0$ is a **free scale**, constrained by no internal ratio, so it can only be **specified directly** from outside and cannot be **derived** internally. This also explains why the gap of §10 is "the absence of a rule" rather than "an inaccurate number".

(Registered together, one candidate **H4**: SRE has the exact ratio $\tfrac23=T(\text{open})/T(\text{closed})$ (independent of $V$), numerically equal to the Koide $Q=2/3$. It is likewise in the D1 domain, registered only, not cross-corroborated.)

### 11.4 The discrete-closure-law perspective

The location of this round is **case 15 of G12**:

- **discrete side (closed)**: cyclicity ⇒ the structure is a **circulant matrix**; the number of positions = 3 (torsor size); $\delta$ is gauge;
- **continuous side (requires input)**: the **value** of $\eta$ (the origin of $1/\sqrt2$) and the scale $c_0$.

It is of the same type as the existing cases: **discrete structure fixes the shape, continuous quantities must be paid in externally**. One empirical aside: **everything that passes the tests is a dimensionless ratio; everything judged negative is a value for which dimensions are sought.**

---

## 12. Conclusion

This paper gives the following adjudication of the precise mathematical expression of "mass" in SRE:

1. **Object level**: mass is not three numbers but the **ℤ₃-equivariant operator on the three-ring ℤ₃-torsor = a circulant matrix** $A=c_0\mathbb{1}+c_1S+\bar c_1S^{2}$ (Corollary 1). It is **forced** by the skeleton structure (Theorem 1, Theorem 2) rather than an imposed language; the centraliser dimension is exactly $n=3$.
2. **"Cyclic" level**: = using the **group** ℤ₃ (rather than a semigroup) to characterise the index space (Proposition 3); $9$ matrix entries are compressed to $3$. For the three generations to be distinct, the operator **must carry a complex phase** (Proposition 5).
3. **"Unopened" level**: = not performing an origin-bearing spectral decomposition ⇒ the native output is an **equivariance class (multiset)**; the invariant moduli space is **two-dimensional** $(\eta,\ \delta\bmod\tfrac{2\pi}{3})$ (Proposition 8), and $Q$ occupies only the $\eta$ direction. **"Opening" = choosing the DFT origin, which is a ℤ₃ gauge (redundancy) and changes no observable** (Proposition 6).
4. **Content level**: **"three points lie on one cosine" is free** (Theorem 3, holds for any three generations); **the entire content of Koide is that number** $\eta=1/\sqrt2$ (measured $\eta^{2}$ deviates by $3.3\times10^{-6}$, Table 10).
5. **Boundary level**: **absolute mass (the scale $c_0$) is not inside SRE**; **only RG-invariant dimensionless combinations qualify as candidate targets** (Corollary 2).
6. **Gap level**: the **assignment rule** — connecting the representation weights of ℤ₃ to $m_k$ / the order parameter $A$. The three hard criteria are in §10.3.

**Overall statement of the conclusion.** Mass = an invariant of "the cyclic structure on ℤ₃"; its carrier is a circulant matrix; "unopened" = outputting only the equivariance class; "opened" = choosing an origin (gauge, not information). What SRE can give: the **position** of $(\eta,\delta)$; what it cannot give: the **value** of $\eta$ and the scale $c_0$.

---

## Appendix A　Recomputation list

**One-command recomputation of all readings** (requires numpy + networkx):

```
C:/myapp/miniconda3/envs/ai/python.exe -u _sre_mass_origin_paper_check.py \
    > _sre_mass_origin_paper_check.log 2>&1      # main body (PART 1-8)
C:/myapp/miniconda3/envs/ai/python.exe -u _sre_paper_v2_check.py \
    > _sre_paper_v2_check.log 2>&1               # v2.0 additions (Examples 1-3, alpha anchor, recheck of Tables 2 and 3)
```

The two scripts are mutually independent implementations and share the project's existing closed form `mobius_pi1` (see `code/_sre_anchor_registry.py`).

**Table A1.** Correspondence between the readings of this paper and the recomputation scripts.

| Location in this paper | Source | Key output |
|---|---|---|
| Theorem 2 (§4.1) | PART 1 | rank $6/9$, null-space basis all circulant = true |
| Proposition 4 (§5.1) | PART 2 | 6 random sets, maximum error $1.1\times10^{-15}$ |
| Proposition 5 (§5.2) | PART 2 | $(0.7,0.7,1.6)$／$(0.400668,1.27515,1.324181)$ |
| Example 2 (§4.2) | v2 Ex.2 | $(0.436184,\ 1.104189,\ 1.459627)$ |
| Theorem 3 (§5.3) | PART 3／v2 Ex.1 | 8 sets of arbitrary triples, reconstruction error $5.11\times10^{-15}$ |
| Example 1 (§2.3) | v2 Ex.1 | $\bar u=0.966667$, $|c_1|=0.145297$, $\theta=1.455835$ rad |
| Proposition 8 (§7.1) | PART 4 | $Q$ range $\le1.6\times10^{-15}$; $R$ varies with $\delta$ |
| Proposition 6 (§6.1) | PART 4 | $|\Delta Q|\le2.2\times10^{-16}$ |
| Theorem 4, Table 10 (§8) | PART 5 | $Q=0.666664463$, $\eta^{2}=0.499996695$, $44.9999^\circ$ |
| Theorem 1, Table 2 (§3) | PART 6 | closed $36/8/1$; open $4/0/2$; $\varphi$ edge-preserving, order 3 |
| Proposition 2, Table 3 (§3.4) | PART 7 | vertex $1/2$; edge $1/3\mid2/3$ |
| Theorem 5 (§9.5) | PART 8 | $Q(c\,m)$ residual $\le1.1\times10^{-16}$ |
| Example 3, Table 10 (§8.3) | v2 Ex.3 | $\sum m=1883.099374$, $\sum\sqrt m=53.147515$, $Q=0.666664463$ |
| §11.3 alpha anchor | v2 anchor | $\Pi_1(M_{60})=7.2974585\times10^{-3}$; relative deviation $1.45\times10^{-5}$; $n^{*}=60.000436$ |

**Table A2.** Preceding scripts (independent sources of the conclusions of this paper, all archived in `code/`).

| Script | Round | Content |
|---|---|---|
| `_sre_weight_homology.py` | Round 29 | weighted homology / dormancy rate (the $\mathbb{Z}_2$ level) |
| `_sre_triality_families.py` | Round 30 | ℤ₃ / triality / torsor / Koide |
| `_sre_quark_mass_probe.py` | Round 31 | three-step decomposition of quark mass / RG-invariant targets |
| `_sre_cyclic_mass_formalism.py` | Round 32 | formalisation of the circulant operator |

---

## Appendix B　Honesty boundary

1. Everything in this paper is a self-consistent statement **internal to the SRE model / at the level of linear algebra and group theory**, and **no** numerical prediction for real physics is claimed. The comparison with charged-lepton masses in the text is **structural consistency**, not prediction.
2. "Taking $a=\sqrt m$ rather than $m$" is the **empirical content of Koide**, equivalent to "**the square root of the mass operator** is ℤ₃-equivariant" — a **testable structural hypothesis** that this paper **has not proved**.
3. "ℤ₃ is the structure of the three generations" is a **mathematical identification + literature consensus**; what this paper **adds** from the SRE perspective is only two **structural facts**: "the skeleton carries ℤ₃ natively (three rings = ℤ₃-torsor)" and "closed → open = ℤ₃ → ℤ₂". Neither is a new numerical prediction.
4. The echo between "real-symmetric ⇒ 2+1" of §5.2 and "the open state has only two values" is only an **observation**, which is **not proved** to be the same mechanism.
5. **The formalisation of this paper adds no constraint** (Theorem 3): it holds trivially for **any** three generations; its value lies in **language** and **layering**, not in new equations. "The shape is trivial" is a known fact in the literature; this paper makes it explicit within the SRE framework and accordingly corrects the earlier wording.
6. The chain of §11.2, "edge $1/3\mid2/3$ + vertex $1/2$ ⇒ $Q=2/3$", **is a candidate, not a conclusion**: all three ratios are small-denominator rationals (D1) with no discriminating power on their own; an upgrade requires a mechanism found elsewhere.
7. The phase $\delta\approx2/9$ of §8.4 is a small-denominator rational (D1), used only as supporting evidence; and $\delta$ is a **gauge quantity**.
8. Theorem 5 is a **mathematical identity** (for a common multiplicative factor); its applicability to QCD running **relies on** the standard result that $\gamma_m$ is flavour-independent (true at LO and beyond; residual dependence only in threshold matching).
9. The scale $c_0$ (absolute mass) still requires external input — consistent with the existing G12 conclusion.
10. Conclusion = **case 15 of G12**.

---

## Appendix C　Analogy index

A survey of the analogies and illustrations used in this paper (each is developed in full at the corresponding place above).

**Table C1.** Index of analogies and illustrations.

| No. | Name | Location | What it addresses |
|---|---|---|---|
| Analogy 1 | three-phase alternating current | §2.3 | the ℤ₃ operator $a=e^{2\pi i/3}$, phase sequence as gauge, symmetrical components as DFT |
| Analogy 2 | a three-strand braid and a clock face | §3.3 | torsor: a cyclic order with no identifiable first element |
| Analogy 3 | a wheel versus an hourglass | §4.3 | group evolution (reversible, no start) vs semigroup evolution (irreversible, with a start) |
| Analogy 4 | a prism and dispersion | §5.3 | DFT = dispersion; "any three colours correspond to some beam" = the shape is free |
| Analogy 5 | transposition of a score | §6.2 | choosing the DFT origin = choosing the tonic (structure unchanged) |
| Analogy 6 | an altitude datum and relative height | §7.3 | relative quantity (datum-independent) vs absolute quantity (needs an external datum) |
| Analogy 7 | forty-five degrees is the "midpoint deviation" | §8.2 | $\eta^{2}=1/2$ means stopping at the midpoint of equal mass and maximal deviation |
| Analogy 8 | three datum surfaces for one mountain | §9.4 | a quantity with no unique definition ⇒ agreement is no evidence |
| Analogy 9 | a pendulum clock as anchor vs a pile of lengths | §11.3 | anchor = locking an external constant to an internal invariant; $c_0$ lacks such a lock |
| Example 1 | cosine reparameterisation of three numbers | §2.3 | the inverse solution always succeeds; the order depends on the origin, the multiset does not |
| Example 2 | a concrete mass operator | §4.2 | a $3\times3$ matrix determined by only two real numbers |
| Example 3 | a complete recomputation for charged leptons | §8.3 | the full hand computation of $Q=0.666664463$ |

**Usage note.** To explain this paper to a non-specialist, the recommended route is: Analogy 1 (three-phase) → Analogy 2 (braid) → Analogy 4 (prism) → Analogy 6 (altitude) → Example 3 (a concrete number). These five steps convey the skeleton of the whole paper without using any further terminology.

---

## Appendix D　References

[1] Y. Koide, *A Fermion-Boson Composite Model of Quarks and Leptons*, Phys. Lett. B **105**, 121 (1981); and the subsequent series of works on the "Koide relation" $Q=2/3$.

[2] R. McRae, *Triality as multiplication by a third root of unity* (a root-of-unity characterisation of triality and duality), arXiv:2502.14016 (2025).

[3] Thorwe, *Discrete Vacuum Field Theory (DVFT)*: the ℤ₃ phase of a three-component vacuum field ⇒ a circulant mass matrix (2026).

[4] Rousselle, *Family symmetry breaking and the center of SU(3)*, arXiv:2608.19277 (2026).

[5] E. Ma, *$\mathbb{Z}_3$ generators and the group $\Sigma(81)$*, hep-ph/0612022 (2006).

[6] Y. Sumino, *Family gauge symmetry and the 45° lepton mixing*, arXiv:0903.3640 (2009).

[7] M. Libanov, S. Troitsky, *Three generations from topological defects*, hep-ph/0011095 (2000).

[8] W. Rodejohann, H. Zhang, a preprint containing "heavy quarks $Q\approx2/3$" (deleted in the published version); and X.-G. He, A. Zee et al. on the scale sensitivity of the Koide relation, arXiv:1111.0480.

[9] Particle Data Group, *Review of Particle Physics* (tables of charged-lepton and quark masses).

[10] This project, *SRE Triality / Three-Level Structure Report* (Round 30, 2026-09-28): first measurement of the ℤ₃-torsor, the order-3 automorphism $\varphi$, the character decomposition, and the Koide recomputation.

[11] This project, *How to Compute Quark Mass in SRE: A Three-Step Decomposition Report* (Round 31, 2026-09-28): the three-step division graph/ledger/dimensions, the RG-invariant target screening rule.

[12] This project, *Complete Characterization of Nucleons within the SRE Framework* (nucleon complete paper): construction and screening of the skeleton $Y_3\ltimes\triangle_3$ (§7–§8), the ledger-carrying law for binding energy (§12).

[13] This project, *A Formal Expression of SRE Mass: Circulant Operator Report* (Round 32, 2026-09-28): the circulant-matrix theorem, triviality of the shape, the invariant moduli space (the formalisation body of §5–§8).

[14] This project, *SRE Projection vs Distance Fidelity Report* (Round 28) and *SRE Weighted Homology / Dormancy Rate Report* (Round 29): the three-level stratification of distance and the ℤ₂-level weighted homology (the prior basis for this paper's judgement that "a two-valued scheme cannot give three levels").

> **Citation discipline.** When citing references, the "$\approx$" in the original must be copied verbatim and must not be rewritten as "equals".
