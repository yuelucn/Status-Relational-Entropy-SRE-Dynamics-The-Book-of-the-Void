# Operator 19: ℤ₂ Holonomy / σ Charge-Sign Channel Operator
## Rigorous Mathematical Specification, Solvability Rationale, Dual ℤ₂ Channel Verdict, and Verification Protocol

**Version**: 1.2 (October 2026 · SRE Operator System No. 19; v1.1 added polarity injection and cross-implementation verification; v1.2 adds the cut-space necessary-and-sufficient criterion, the side-by-side Pfaffian / $H^1$ dual-channel verdict, and the ladder-family numbering convention)
**Reference Implementations**: Functional bridge `sre_z2_holonomy_bridge.py` (entry `operator_19_z2_charge_channel`); class-style release suite `sre_charge_channel.py` (`SREChargeChannelSuite.execute_operator_19_z2_charge_channel`; three mirrors share identical SHA-256) — dual implementations prove no ambiguity in the specification
**Companion Verification Programs**: Three independent programs collectively validate this specification
  - `verify_operator_19.py` (V1–V12, skeleton fidelity / theorem-by-theorem / freeze contract, 45 assertions)
  - `verify_operator_19_mobius.py` (M1–M9, Möbius-family experiments, 57 assertions)
  - `verify_operator_19_cross.py` (X1–X10, cross-implementation parity + guard boundaries, 29 assertions)
**Upstream Dependencies**: Operator 1/4 (SRE smoothed adjacency $A_s$ bond-graph support), Operator 11 (spin-polarity diagnostics $s_i,\sigma_{ij}$), Operator 12 (first Betti number $\beta_1$ cycle counting)
**Upstream Paper**: *"Emergence of Positive and Negative Charge in the SRE System: Magnitude, Sign, and Numerical Validation"* (the "charge-emergence paper" hereinafter)
**Downstream Integration**: `sre_cluster_substitute_screen.py` (`z2_*` fields piped into compound screening pipeline)
**Numbering Note**: This operator is numbered **19** after the existing 18; pairwise verification confirms **no overlap** with all 18 operators in `SRE-math_C.md` (boundary details in §9).
**External Verdict Report (cited by v1.2)**: *"Dual $\mathbb{Z}_2$ Channel Verdict on the Nucleon Skeleton $Y_3$: Landing the Cut-Space Necessary-and-Sufficient Criterion on the Project's Own Objects, Its Relation to the Möbius Ladder Family, and a Readable Certificate of the Pfaffian Obstruction"* (round 104, the "$Y_3$ verdict report" hereinafter). All measured values and certificates in T9, T10, T11, §6.2 and §6.3 of this version originate from that report; the cut-space identities have additionally been independently re-checked inside this project (§8.4).

---

## Abstract

SRE dynamics renders charge as "the counting of topological knots". Counting is non-negative by nature and therefore supplies only the **magnitude** of charge, not its **sign**. The charge-emergence paper closes this gap by proposing the charge functional

$$Q(K)=\sigma(K)\cdot\deg(K)\cdot e,\qquad \deg(K)=\beta_1(K)\bmod 2,\qquad \sigma(K)\in H^1(G;\mathbb{Z}_2).$$

where the "sign channel" $\sigma$ is declared as a $\mathbb{Z}_2$ holonomy cohomology class—but that paper used a standalone numerical script (`_se_assignment_test.py`) to spot-check a handful of skeletons and molecules, **without providing an independent, reusable, provable implementation specification** for this operator. This document grounds the $\sigma$ channel **separately** as **Operator 19** and delivers three previously missing pieces:

1. **Rigorous rationale** (§2–§5): On the **1-dimensional chain complex** of molecular bond graphs, the "edge polarity → cycle holonomy → cohomology class" pipeline is formalised, the well-definedness of the operator output is proven, and **all theorems with proofs** are given (T0–T11).
2. **Accompanying paper** (this document): The operator's axiomatic positioning, bridging semantics with upstream electronic operators, boundaries with existing operators, and faithful reproduction on official skeletons and molecular layers.
3. **Rigorous verification programs** (`verify_operator_19.py`): Each theorem is mapped to a reproducible assertion (V1–V12); passing all assertions empirically establishes this specification.

Core conclusions (all rigorous on 1-complexes, independent of any external parameter):

| No. | Theorem | Meaning |
|---|---|---|
| **T0** | On a 1-complex, $\sigma$ is an $\mathbb{F}_2$-linear functional on $H_1$ | Well-defined, comparable |
| **T1** | Vertex-potential polarities $s_e=t_it_j$ have **always trivial** holonomy | **Charge sign cannot be manufactured by local spin relabeling** |
| **T2** | Nontrivial reachability under Aut-invariant assignments $=$ $\mathbb{Z}_2$ linear criterion ($\exists$ cycle $i$, orbit $o$ with $m_{i,o}=1$) | No $2^{\#\text{orbit}}$ enumeration needed |
| **T3** | Triviality criterion **independent of cycle-basis choice** | Unique result |
| **T4** | Multiplying by a **coboundary** (vertex potential) changes no cycle holonomy | $[s]\in H^1$ is a gauge invariant |
| **T5** | Sign channel $\sigma$ and magnitude channel $\deg$ are **orthogonally independent** | Two channels encode separately |
| **T6** | Bipartite graph + single edge orbit $\Rightarrow$ **forced triviality** (electron-like) | Structural origin of electron $Q_3$ |
| **T7** | Molecular-layer Aut **must preserve element coloring**; otherwise reachability criterion is distorted (can flip) | Necessity of element coloring |
| **T8** | Composite body $\sigma_{\text{comp}}=\prod_i\sigma_i$, $Q$ recomputed at new boundary | Hooks A2/A3 |
| **T9** | $\operatorname{rank}_\mathrm{hol}=n_\mathrm{orb}-\dim\big(W(G)\cap\operatorname{Cut}(G)\big)$ | **Necessary-and-sufficient criterion for triviality** (dimension refinement of T2) |
| **T10** | The Pfaffian unsolvability of $Y_3^\mathrm{cl}$ has a **minimal unsatisfiable certificate** (all 6 rows needed for contradiction, one row short) | Negative verdict is machine-checkable |
| **T11** | Ladder family: $\operatorname{rank}_\mathrm{hol}=0\iff k=3$ ($K_{3,3}$) | Odd cycles are **not** the criterion for channel opening |

**v1.2 Additions (all gated by the $Y_3$ verdict report A–F and re-checked inside this project)**:

1. **T9 (cut-space identity)**　Deepens T2's "does a nontrivial class exist" criterion into a **dimension identity**: the number of reachable (Aut-invariant) classes is exactly $2^{\operatorname{rank}_\mathrm{hol}}$; the three official skeletons read $Q_3=0$, $Y_3^\mathrm{cl}=1$, $Y_3^\mathrm{op}=2$ (§6, Table 6.2).
2. **§6.2 Side-by-side dual $\mathbb{Z}_2$ channel verdict**　On the very same $Y_3^\mathrm{cl}$ the $H^1$ channel is **open** (1 bit) while the **Pfaffian channel admits not a single orientation**, with a readable certificate (6-row minimal unsatisfiable subset) and a mechanism (42 nice even cycles vanish in the open state).
3. **§6.3 Covering verdict and numbering convention**　$Y_3^\mathrm{cl}$ has **zero coverings and zero quotients** over $M_{2n}(n\ge3)$, yet is exactly a **3-fold regular cover of $K_4\cong M_4$**; a factor-2 correspondence table between the in-book $M_k$ and the paper's $M_{2n}$ is established (Table 6.5).
4. **Correction to v1.1**　The v1.1 §10 item 3 statement "nontrivial reachability **only if** the graph contains an odd cycle and has $\ge2$ orbits" is **falsified**: odd-$k\ge5$ ladders are bipartite (no odd cycle) and still have $\operatorname{rank}_\mathrm{hol}\ge1$; the correct criterion is $W\not\subseteq\operatorname{Cut}$ (T9). Correspondingly, the §6.1 sentence "what actually determines the flip is the existence of odd cycles" is corrected as well.

**Keywords**: $\mathbb{Z}_2$ cohomology; holonomy; coboundary; cut space; edge orbit; Aut-invariant assignment; charge-sign channel; Pfaffian orientation; first Betti number

---

## 1 Problem Statement

### 1.1 The Gap

The charge-emergence paper (§3–§4) gives:

- **Magnitude channel** $\deg(K)=\beta_1(K)\bmod 2$ (§5);
- **Sign channel** $\sigma(K)=\prod_{e\in\partial K}s_e\in\{+1,-1\}$ (Definition D4), and declares $\sigma\in H^1(G;\mathbb{Z}_2)$;
- **Charge functional** $Q(K)=\sigma(K)\cdot\deg(K)\cdot e$ (Axiom A1).

But the sign channel in that paper was **only spot-checked on a handful of discrete skeletons**, lacking:

1. **Rigorous well-definedness argument**—does $\prod_{e\in\partial K}s_e$ truly depend only on the homology class of $K$ (not its representative)?
2. **Reusable implementation**—how to project $\sigma$ onto arbitrary molecular bond graphs while sharing the same graph with the electronic operators?
3. **Rigorous reachability criterion**—under what conditions are nontrivial classes reachable (the structural origin of "electron/proton sign differences")?

### 1.2 Task of This Document

Ground the $\sigma$ channel **separately** as Operator 19:

- **Input**: SRE smoothed adjacency $A_s$ from Operators 1/4 (bond-graph support $A_s>0$); optional polarity gauge chosen from four mutually exclusive options (D3) — default `polarity="topo"`, or explicit `edge_polarity` / orbit `orbit_signs` / spin `chi`; optional element labels (molecular coloring, color-preserving Aut); optional guard parameters `aut_cap` (default 100,000) and `aut_max_v` (default 22, skips reachability only when exceeded).
- **Output**: Graph invariants $\{V,E,c,\beta_1,\deg,\text{bipartite},\text{has\_odd\_cycle}\}$, $\sigma$-class $\{\sigma\text{-vector},\sigma\text{-class},\text{trivial}\}$, Aut-invariant reachability, and in-model charge tier $Q_{\text{model}}=\sigma\cdot\deg$;
- **Properties**: T0–T11 (§5). T9 supplies the bit count of the sign channel (cut-space necessary-and-sufficient criterion); T10/T11 together with §6.2/§6.3 supply the dual $\mathbb{Z}_2$ channel verdict and the ladder-family numbering convention (added in v1.2; the latter changes neither the input/output nor the freeze contract).

---

## 2 Mathematical Preliminaries

### 2.1 Graph as a 1-Dimensional Chain Complex

Let the bond graph be $G=(V,E)$ with $\lvert V\rvert =n$ and $\lvert E\rvert =m$. The SRE system operates **exclusively on 1-dimensional complexes (graphs)** — there are no 2-cells (faces), so

$$Z_1=\ker\partial_1,\qquad B_1=\mathrm{im}\,\partial_2=0,\qquad H_1(G;\mathbb{F}_2)=Z_1/B_1=Z_1,\qquad \dim H_1=\beta_1=E-V+c,$$

where $c$ is the number of connected components. **Key**: because there are no 2-cells, $B_1=0$ and $H_1$ is the cycle space itself ("cycle count = homology dimension", consistent with Operator 12's $n_{\text{loops}}=\beta_1$).

Dually, the cochain complex $C^0\xrightarrow{\delta}C^1\xrightarrow{\delta}C^2$ has $C^2=0$ (no 2-cells), so $Z^1=C^1$ and $B^1=\delta C^0$, hence

$$H^1(G;\mathbb{F}_2)=C^1/\,\delta C^0.$$

$\delta C^0$ is the **coboundary** (vertex-potential 1-cochain). The pairing $H^1\times H_1\to\mathbb{F}_2$ is given by $\langle [s],[\gamma]\rangle=\sum_{e\in\gamma}z_e$.

### 2.2 Polarity–Boolean Isomorphism

**Lemma 2.1 (Polarity–Boolean Isomorphism)**　The map $\varphi:\{+1,-1\}\to\mathbb{F}_2$, $\varphi(S)\equiv\frac{1-S}{2}$ ($-1\mapsto1,\ +1\mapsto0$), is a group isomorphism $(\{+1,-1\},\cdot)\cong(\mathbb{F}_2,\oplus)$.

**Proof**　Bijectivity is obvious. Verify homomorphism: $\varphi(S_1S_2)=1$ iff exactly one $S_k=-1$, which matches $\varphi(S_1)\oplus\varphi(S_2)$; all four input combinations hold one-by-one. $\square$

Thus "multiplying polarities" and "adding mod 2" are in strict one-to-one correspondence; subsequent operations use $\mathbb{F}_2$ (denoting $z_e\equiv\varphi(s_e)$).

### 2.3 Duality of SRE Axiom 1

SRE Axiom 1 (no zero elements) guarantees each edge takes only $s_e\in\{+1,-1\}$, i.e. $z_e\in\mathbb{F}_2$ with no "undefined/missing" state. **This is the precondition for Operator 19 to be defined on the full edge space $C^1$** (independent of whether an edge "exists").

---

## 3 Definitions

**D1 (Bond Graph $G$)**　Given by the support of $A_s$: $G=(V,E)$, $E=\{(i,j):A_s{}_{ij}>0,\,i<j\}$. (Corresponds to SRE Axiom 1's cooperative edge set $E^+$.)

**D2 (Edge-Polarity 1-Cochain $s$)**　$s:E\to\{+1,-1\}$, $z_e\equiv\varphi(s_e)\in\mathbb{F}_2$; $s\in C^1(G;\mathbb{F}_2)$.

**D3 (Four Edge-Polarity Gauges / Injection Priority)**

Operator 19 supports four **mutually exclusive** sources of edge polarity, ordered by priority:

1. **explicit injection** (`polarity="explicit"` + `edge_polarity=spec`): external dictionary `{(i,j):±1}` or length-$E$ sequence; must cover every edge and take values only $\pm1$. The most flexible debugging/experimentation gauge.
2. **orbit injection** (`polarity="orbit"` + `orbit_signs=[±1,\dots]`): each edge orbit takes the same sign by construction, **inherently Aut-invariant** (connects to the explicit assumption in charge-emergence §13.2). Length must equal the number of edge orbits and requires $V\le\text{aut\_max\_v}$.
3. **spin gauge** (`polarity="spin"` + `chi=\chi`): $s_e=s_i\cdot s_j$, $s_i=\operatorname{sign}(\chi_i-\bar\chi)$. By T1 its holonomy is **always trivial**, so this gauge demonstrates that "vertex-potential type cannot produce nontrivial sign channels".
4. **topo literal gauge** (`polarity="topo"`, default): cooperative edges all take $s_e=+1$ (the literal declaration in charge-emergence A1).

Providing multiple injection gauges simultaneously (e.g. both `edge_polarity` and `orbit_signs`) or invalid values raises `ValueError`; both implementations share this validation contract (see §8.3 / X8).

**D4 (Cycle Holonomy)**　For cycle $\gamma$ (vertex sequence $v_0v_1\cdots v_{L-1}v_0$): $\sigma(\gamma)\equiv\prod_{k}s_{(v_k,v_{k+1})}$, equivalently $\sigma(\gamma)=\big(\sum_{e\in\gamma}z_e\big)\bmod 2$.

**D5 (Fundamental Cycle Basis)**　Take a spanning forest of $G$ (BFS parent); each non-tree edge $(u,v)$ paired with the tree path $u\leadsto v$ forms a fundamental cycle $\gamma_i$, $i=1,\dots,\beta_1$. $\{\gamma_i\}$ is a basis of $H_1$.

**D6 ($\sigma$-Class / Triviality)**　$[s]=s+\delta C^0\in H^1$. Call $[s]$ **trivial** ($[s]=0$) iff $s\in\delta C^0$ (i.e. there exists a vertex potential $t\in\{\pm1\}^V$ with $s_e=t_it_j$), equivalently **all** $\sigma(\gamma_i)=+1$ on the fundamental cycle basis. $\sigma_{\text{canonical}}\equiv+1$ (trivial) $/-1$ (nontrivial).

**D7 (Magnitude Channel $\deg$)**　$\deg(K)\equiv\beta_1(K)\bmod 2$. (Independent of $s$.)

**D8 (In-Model Charge Tier $Q_{\text{model}}$)**　$Q_{\text{model}}\equiv\sigma_{\text{canonical}}\cdot\deg\in\{-1,0,+1\}$ (with $e$ normalised to 1).

**D9 (Aut-Invariant Assignment)**　Let the automorphism group $\operatorname{Aut}(G)$ (in the molecular context, **color-preserving** automorphisms; see T7) act on $E$, partitioning $E$ into edge orbits $\{O_1,\dots,O_k\}$. Call $s$ **Aut-invariant** if $s$ is constant on each orbit.

**D10 (Channel Type)**
- **electron-like (forced trivial)**: under Aut-invariant assignments, **every** $s$ is trivial;
- **nucleon-like (nontrivial allowed)**: $\exists$ Aut-invariant $s$ that is nontrivial.

**D11 (Aut-Invariant Assignment Space $W(G)$, new in v1.2)**　Let the edge orbits be $O_1,\dots,O_k$,
$$W(G)\equiv\operatorname{span}_{\mathbb{F}_2}\{\mathbf 1_{O_1},\dots,\mathbf 1_{O_k}\}\subseteq C^1(G;\mathbb{F}_2),\qquad \dim W(G)=n_\mathrm{orb}=k .$$
$W(G)$ is the subspace of "all Aut-invariant assignments". **Contrast**: without the Aut constraint the assignment space is the whole $C^1$ (dimension $m$), and nontrivial classes are then the norm (dimension $\beta_1$, see §10 item 2).

**D12 (Cut Space $\operatorname{Cut}(G)$, new in v1.2)**
$$\operatorname{Cut}(G)\equiv\{d(S):S\subseteq V\}=\operatorname{im}\delta_0=\delta C^0\subseteq C^1(G;\mathbb{F}_2),\qquad \dim\operatorname{Cut}(G)=n-c ,$$
where $d(S)$ is the set of edges with exactly one endpoint in $S$. **Use the star-set basis** $d(\{v\})$ (all edges incident to $v$). **Pitfall warning**: if the basis is mistakenly taken as "the tree-path edge set from $v$ to the root", the resulting space is the **cycle space** (the tree half of the tree–cotree decomposition), not the cut space—the $Y_3$ verdict report measured 566 mismatches out of 996 cases under this substitution (see §8.4, gate B′).

**D13 (Holonomy Rank and Number of Reachable Classes, new in v1.2)**　Define the $\mathbb{F}_2$-linear map
$$\Phi_G:W(G)\longrightarrow H^1(G;\mathbb{F}_2),\qquad z\longmapsto[s(z)],\qquad \operatorname{rank}_\mathrm{hol}(G)\equiv\dim_{\mathbb{F}_2}\operatorname{im}\Phi_G .$$
**Meaning**: $\operatorname{rank}_\mathrm{hol}$ is the "number of bits of the sign channel"; the number of Aut-invariant reachable classes is $2^{\operatorname{rank}_\mathrm{hol}}$; $\operatorname{rank}_\mathrm{hol}=0\iff$ every Aut-invariant assignment is trivial (i.e. the electron-like case of D10, made precise here).

**D14 (Pfaffian Orientation Class, new in v1.2 — control channel for §6.2 only)**　Let $\mathcal M$ be the set of perfect matchings of $G$. An edge orientation $t:E\to\{\pm1\}$ is a **Pfaffian orientation** if for every $M\in\mathcal M$, $\prod_{e\in M}t_e=(-1)^{\mathrm{cr}(M)}$, where $\mathrm{cr}(M)$ is the number of crossing pairs in the matching mod 2. This is equivalent to the solvability of the **unbalanced linear system** $\sum_{e\in M}t_e=\mathrm{cr}(M)\ (\bmod 2)$; its solution set is denoted $\mathcal O_\mathrm{Pf}(G)$. When $\#\mathcal M=0$ the criterion passes vacuously and **cannot be used as a discovery**.

---

## 4 Axioms (Inherited from the Charge-Emergence Paper)

**A1 (Charge Functional)**　$Q=\sigma\cdot\deg\cdot e$, $\sigma\in H^1(G;\mathbb{F}_2)$.
**A2 (Composite Recomputation)**　For a composite knot $K_{\text{comp}}$, $\sigma_{\text{comp}}=\prod_i\sigma_i$ (in $\mathbb{F}_2$ addition), $\deg_{\text{comp}}=\beta_1(K_{\text{comp}})\bmod2$.
**A3 (Additive Separation)**　Independent knots satisfy $Q_{\text{tot}}=\sum_i Q(K_i)$.
**A0 (Sign Reference)**　Convention: the holonomy class containing the electron is "negative" (gauge convention).

**Operator 19 Gauge Statement**: Operator 19 implements the $\sigma$ channel and the $\deg$ channel, outputting $Q_{\text{model}}$ as the **in-model charge tier**; the "negative" reference in A0 is carried by $\sigma_{\text{canonical}}=-1$.

---

## 5 Core Theorems and Proofs

> All theorems below are stated on **graphs (1-complexes)**, with $c$ the number of connected components and $\beta_1=E-V+c$.

### T0 (Well-Definedness: $\sigma$ is an $\mathbb{F}_2$-Linear Functional on $H_1$)

**Statement**　On a graph without 2-cells, $B_1=0$ so $H_1=Z_1$; the map $\sigma:Z_1\to\mathbb{F}_2$, $\gamma\mapsto\sum_{e\in\gamma}z_e$, is a linear functional depending only on the cycle chain itself.

**Proof**　$\partial_2=0\Rightarrow B_1=0\Rightarrow H_1=Z_1$; a cycle is a homology class, so $\sigma$ has no "representative ambiguity". Linearity: for $\gamma_1,\gamma_2\in Z_1$, $\sigma(\gamma_1+\gamma_2)=\sum_{e\in\gamma_1\triangle\gamma_2}z_e=\sigma(\gamma_1)+\sigma(\gamma_2)\ (\mathrm{mod}\,2)$, because common edges appear twice in the symmetric difference and cancel mod 2. $\blacksquare$

**Note**　This is one place where Operator 19 is simpler than general graph theory: molecular bond graphs have no faces filling cycles, so the declaration "$\sigma\in H^1$" from the charge-emergence paper holds **automatically** at the graph level, with no extra 2-cell structure required.

### T1 (Vertex-Potential Triviality Theorem)

**Statement**　If $s_e=t_i\cdot t_j$ ($t\in\{\pm1\}^V$, i.e. $s$ is a $\delta$-type vertex potential), then for **every** closed chain $\gamma$ we have $\sigma(\gamma)=+1$; that is, $[s]=0$.

**Proof**　
$$\sigma(\gamma)=\prod_{(i,j)\in\gamma}s_i s_j=\prod_{v\in\gamma}t_v^{\,\deg_\gamma(v)},$$
where $\deg_\gamma(v)$ is the number of edges incident to $v$ in the closed chain $\gamma$. A closed chain satisfies the conservation of incoming and outgoing degrees at each vertex, so $\deg_\gamma(v)$ is **even**, hence $t_v^{\deg_\gamma(v)}=+1$; the product yields $\sigma(\gamma)=+1$. $\blacksquare$

**Corollary T1.1 (Charge Sign Cannot Emerge from Local Spin Relabeling)**　The spin polarities of Operator 11, $s_e=s_i s_j$, are **precisely** of vertex-potential type; by T1 their holonomy is always trivial. Therefore:

> **The charge-sign channel $\sigma$ must come from a genuinely non-coboundary cochain $[s]\neq0\in H^1$ — it cannot be manufactured by local vertex-spin relabeling.**

This explains why "naively assigning vertex-spin signs" cannot produce a net charge sign — it lands in the trivial class of $H^1$.

### T2 (Aut-Invariant Reachability Linear Criterion over $\mathbb{Z}_2$)

**Statement**　Let the Aut edge orbits be $O_1,\dots,O_k$ and let Aut-invariant assignments take values $z_o\in\mathbb{F}_2$ on orbit $o$. Define

$$m_{i,o}\equiv\#\{e\in O_o\cap\gamma_i\}\bmod2\in\mathbb{F}_2,\qquad M=(m_{i,o})\in\mathbb{F}_2^{\beta_1\times k}.$$

Then $\sigma(\gamma_i)=\bigoplus_{o}m_{i,o}z_o$, and

$$\boxed{\ \text{Nontrivial class reachable}\iff \exists\,i,o:\ m_{i,o}=1\iff M\neq 0\ }$$

**Proof**　By the linearity of T0, $\sigma(\gamma_i)=\sum_{e\in\gamma_i}z_e=\sum_o z_o\cdot\#(O_o\cap\gamma_i)=\bigoplus_o m_{i,o}z_o$ — so $M$ gives a linear map $T:\mathbb{F}_2^k\to\mathbb{F}_2^{\beta_1}$, $z\mapsto Mz$.
- ($\Leftarrow$) If $\exists m_{i,o}=1$, take $z=e_o$ (only $z_o=1$); then $\sigma(\gamma_i)=m_{i,o}=1\neq0$ and nontrivial reachability is achieved (the trivial class $z=0$ is always reachable).
- ($\Rightarrow$) If $M=0$, then $\forall z$, $Mz=0$, so every cycle holonomy is always $+1$ and no nontrivial class is reachable.

Thus reachability is equivalent to $M\neq0$ — we need only find any nonzero entry in $M$ with complexity $\mathcal{O}(\beta_1\cdot k)$, **no $2^k$ exhaustive enumeration**. $\blacksquare$

**Corollary T2.1**　The trivial class is **always reachable** (take the zero assignment $s_e\equiv+1$). A nontrivial class is reachable **if and only if** some edge orbit appears an odd number of times in some fundamental cycle.

**T2.2 (Rank Form: $\operatorname{rank}(M)=\operatorname{rank}_\mathrm{hol}$, new in v1.2)**

**Statement**　$\operatorname{rank}_{\mathbb{F}_2}(M)=k-\dim\big(W(G)\cap\operatorname{Cut}(G)\big)=\operatorname{rank}_\mathrm{hol}(G)$.

**Proof**　The null space of $M$ is $\ker M=\{z:Mz=0\}=\{z:\sigma(\gamma_i)=0\ \forall i\}$. By T3 (cycle-basis independence), "vanishing on the fundamental cycle basis" $\iff$ "vanishing on every cycle" $\iff[s(z)]=0$; and by T4, $[s(z)]=0\iff s(z)\in\delta C^0=\operatorname{Cut}$. Hence $\ker M=W(G)\cap\operatorname{Cut}(G)$. The rank–nullity theorem gives $\operatorname{rank}M=k-\dim\ker M=k-\dim(W\cap\operatorname{Cut})$, which equals $\operatorname{rank}_\mathrm{hol}$ by T9. $\blacksquare$

**T2.3 (Status of the Criterion: the Misstated Necessity, corrected in v1.2)**　The $M\neq0$ criterion of T2 is an **existence** criterion (equivalent to $\operatorname{rank}_\mathrm{hol}\ge1$); it **does not give the dimension** (the dimension comes from T9/T2.2). The v1.1 §10 item 3 wrote "contains an odd cycle + orbit count $\ge2$" as a **necessary condition**, which **has been falsified**: the (in-book) ladder family with odd $k\ge5$ is **bipartite** (no odd cycle) with two orbits, yet still has $\operatorname{rank}_\mathrm{hol}\ge1$ (§6.3, T11); while $k=3$ ($K_{3,3}$) is bipartite with a single orbit and has $\operatorname{rank}_\mathrm{hol}=0$. **Odd cycles are neither sufficient nor necessary**; the only necessary-and-sufficient criterion is $W(G)\not\subseteq\operatorname{Cut}(G)$ (T9).

### T3 (Cycle-Basis Independence)

**Statement**　The triviality criterion for $\sigma$ ($[s]=0$) is independent of the choice of fundamental cycle basis $\{\gamma_i\}$.

**Proof**　Take any two fundamental cycle bases $\{\gamma_i\},\{\gamma'_j\}$; both are bases of $H_1=Z_1$, so $\gamma'_j=\sum_i a_{ji}\gamma_i$ ($a_{ji}\in\mathbb{F}_2$). By T0 linearity $\sigma(\gamma'_j)=\bigoplus_i a_{ji}\sigma(\gamma_i)$. Therefore "all zero on one basis" is equivalent to "all zero on the other basis", so the triviality criterion is unique. $\blacksquare$

### T4 (Coboundary Gauge Invariance / Cohomology Class is a Gauge Invariant)

**Statement**　Let $s'=s\cdot\delta t$ (i.e. $s'_e=s_e\,t_it_j$, $t\in\{\pm1\}^V$). Then $\forall\gamma:\sigma'(\gamma)=\sigma(\gamma)$; hence $\sigma$ depends only on $[s]\in H^1$.

**Proof**　$\sigma'(\gamma)=\big(\prod_{e\in\gamma}s_e\big)\cdot\big(\prod_{e\in\gamma}t_it_j\big)=\sigma(\gamma)\cdot1$, where the last factor is always $+1$ by T1. $\blacksquare$

**Corollary T4.1**　The quotient structure $H^1=C^1/\delta C^0$ precisely matches "$\sigma$ is immune to vertex-potential relabeling"; the gauge freedom is $\delta C^0$ (vertex potentials).

### T5 (Two-Channel Orthogonal Independence)

**Statement**　$\deg=\beta_1\bmod2$ is determined solely by $(V,E,c)$, independent of $s$; $\sigma$ depends solely on $[s]$, not on the specific values of $(V,E,c)$ (only on the graph's **orbit structure** and $[s]$). Their independent variables are disjoint, so they take values independently.

**Proof**　$\deg$ is a topological function of the graph ($\beta_1=E-V+c$); $\sigma$ is a function of the cohomology class. Taking different $s,s'$ preserves $\deg$ while changing $\sigma$; taking different graphs (changing $\deg$) preserves the $\sigma$ structure. So $Q=\sigma\cdot\deg$ is indeed the product of two independent channels. $\blacksquare$

### T6 (Even-Cycle Forced Triviality: Structural Origin of Electron Type)

**Statement**　If $G$ is **bipartite** (no odd cycles) and has exactly **one edge orbit**, then every Aut-invariant assignment is trivial (electron-like).

**Proof**　A single orbit $\Rightarrow s$ is a constant $z$ (in $\mathbb{F}_2$). Bipartite $\Rightarrow$ every cycle $\gamma$ has even length $\lvert \gamma\rvert$. Hence $\sigma(\gamma)=z^{\lvert \gamma\rvert }=(z)^{\text{even}}=+1$, trivial. $\blacksquare$

**Reference** (consistent with charge-emergence paper §10.2):
- Electron $Q_3$ (cube graph): bipartite, single edge orbit $\Rightarrow$ **forced trivial** ($[s]=0$);
- Proton $Y_3\ltimes\triangle_3$ (closed state): **non-bipartite** (contains odd cycles), two edge orbits $\Rightarrow$ nontrivial allowed.

### T7 (Element-Coloring Necessity)

**Statement**　In molecular contexts, automorphisms **must preserve element labels** (color-preserving Aut). Using non-color-preserving Aut merges edge orbits that should remain distinct, distorting the reachability criterion and **potentially flipping it**.

**Proof (Counterexample)**　Take a 4-cycle $v_0v_1v_2v_3v_0$ with elements $[O,C,C,O]$ ($v_0{=}O, v_1{=}C, v_2{=}C, v_3{=}O$) and edges $e_1{=}(0,1),e_2{=}(1,2),e_3{=}(2,3),e_4{=}(3,0)$.
- **Color-preserving Aut**: swap $v_0\leftrightarrow v_3$ and $v_1\leftrightarrow v_2$ preserve elements. Orbits: $O_1=\{e_1,e_3\}, O_2=\{e_2\}, O_3=\{e_4\}$ (3 orbits). On the unique cycle $\gamma$: $m_{\gamma,O_1}=2\equiv0, m_{\gamma,O_2}=1, m_{\gamma,O_3}=1$, so $M\neq0$ $\Rightarrow$ **nontrivial reachable**.
- **Non-color-preserving Aut**: $D_4$ acts **transitively** on all 4 edges (1 orbit). Cycle $\gamma$ has length 4, even, $\sigma=z^{4}=+1$ $\Rightarrow$ **forced trivial**.

The two gauges give **opposite channel criteria**, so element coloring is a necessary condition for molecular-layer analysis. $\blacksquare$

**Implementation Requirement**　`automorphisms(adj, colors=elements)` must restrict automorphisms by `node_match` (by element label); `elements=None` falls back to non-color-preserving, suitable only for abstract-graph experiments.

### T8 (Composition and Additivity: Hooks A2/A3)

**Statement**　For a composite body $K_{\text{comp}}$ formed by coherently merging $n$ knots: $\sigma_{\text{comp}}=\prod_i\sigma_i$ (in $\mathbb{F}_2$ addition), $\deg_{\text{comp}}=\beta_1(K_{\text{comp}})\bmod2$, $Q_{\text{comp}}=\sigma_{\text{comp}}\deg_{\text{comp}}$.

**Proof**　The composite recomputes new boundaries (A2), with boundary equal to the symmetric difference of each $\partial K_i$; by T0 linearity, $\sigma$ sums over the symmetric difference $\Rightarrow$ polarities multiply (Lemma 2.1). $\deg$ is recomputed from the new $(V,E,c)$. Additive separation (A3) follows from $Q$ summing over independent components. $\blacksquare$

### T9 (Cut-Space Identity / Necessary-and-Sufficient Criterion for Triviality, new in v1.2)

**Statement**　Let $G$ be connected ($c=1$; the general $c$ case is applied component-wise), $n_\mathrm{orb}=\dim W(G)$. Then

$$\boxed{\ \operatorname{rank}_\mathrm{hol}(G)=n_\mathrm{orb}-\dim_{\mathbb{F}_2}\big(W(G)\cap\operatorname{Cut}(G)\big)\ }\qquad\text{and}\qquad \boxed{\ \operatorname{rank}_\mathrm{hol}(G)=0\iff W(G)\subseteq\operatorname{Cut}(G)\ }$$

That is: **the sign channel is trivial $\iff$ every Aut-invariant assignment is some cut**.

**Proof**　By D13, $\Phi_G:W(G)\to H^1$ is $\mathbb{F}_2$-linear. Its kernel is
$$\ker\Phi_G=\{s\in W(G):[s]=0\in H^1\}=\{s\in W(G):s\in\delta C^0\}=W(G)\cap\operatorname{Cut}(G),$$
where the first equality is the definition of the kernel, the second follows from $H^1=C^1/\delta C^0$ (§2.1) together with T4 (the class is uniquely determined by $[s]$), and the third from D12 ($\operatorname{Cut}=\delta C^0$). By the rank–nullity theorem,
$$\operatorname{rank}_\mathrm{hol}=\dim\operatorname{im}\Phi_G=\dim W(G)-\dim\ker\Phi_G=n_\mathrm{orb}-\dim(W\cap\operatorname{Cut}).$$
Then $\operatorname{rank}_\mathrm{hol}=0\iff\operatorname{im}\Phi_G=0\iff\ker\Phi_G=W(G)\iff W(G)\subseteq\operatorname{Cut}(G)$ gives the second equivalence. $\blacksquare$

**Corollary T9.1 (Connection to T2)**　$\operatorname{rank}_\mathrm{hol}\ge1\iff W(G)\not\subseteq\operatorname{Cut}(G)\iff M\neq0$ (the existence criterion of T2). T2 only answers "is there a nontrivial class"; T9 answers "how many bits".

**Corollary T9.2 (Two Mutually Independent Computational Routes)**　Route A: the matrix rank $\operatorname{rank}_{\mathbb{F}_2}M$ of T2 ($\mathcal{O}(\beta_1 k)$); Route B: the cut-space intersection dimension $\dim W+\dim\operatorname{Cut}-\operatorname{rank}(W\cup\operatorname{Cut})$ with the **star-set** basis of $\operatorname{Cut}$ (D12). The $Y_3$ verdict report measured these two routes plus "$H^1$ class enumeration" and "subset enumeration" on 22 samples (ladder family, prism family, classical graphs, random 3-regular graphs) with **zero mismatch across all four routes**.

**Corollary T9.3 (Official Skeleton Readings)**

| Skeleton | $n_\mathrm{orb}$ | $\dim\operatorname{Cut}$ | $\dim(W\cap\operatorname{Cut})$ | $\operatorname{rank}_\mathrm{hol}$ |
|---|---|---|---|---|
| $Q_3$ | 1 | 7 | 1 | **0** |
| $Y_3^\mathrm{cl}$ | 2 | 11 | 1 | **1** |
| $Y_3^\mathrm{op}$ | 7 | 11 | 5 | **2** |

This agrees with the T2 criterion ($Q_3$: $M=0$; $Y_3^\mathrm{cl}$: $M\neq0$) and with the channel types in charge-emergence paper §10.2; moreover the triviality of $Q_3$ now receives a **mechanistic explanation**: its only Aut-invariant assignment (all ones, since the graph is edge-transitive) happens to lie inside the cut space.

**Note (Label Independence)**　$\operatorname{rank}_\mathrm{hol}$ is an integer depending only on the orbit structure and the cut space of $G$; it is **independent** of the choice of cycle basis (T3) and of vertex labeling (matching the $\sigma$ class of §6). This is exactly opposite to $\varrho$-type quantities (Operator 20, see its specification §2.2), which are label-sensitive. Hence $\operatorname{rank}_\mathrm{hol}$ is a **comparable invariant** across skeletons.

---

## 6 Bond with the Upstream Charge-Emergence Paper (Faithful Reproduction on Official Skeletons)

Operator 19 faithfully reproduces the three skeletons from charge-emergence paper §10.2 using `skel_electron_q3 / skel_y3_closed / skel_y3_open`, serving as the **anchor self-test** of the specification:

**Table 6.1　Anchor readings of the three skeletons**

| Skeleton | $V$ | $E$ | $\beta_1$ | $\deg$ | $\lvert\operatorname{Aut}\rvert$ | Edge Orbits | Bipartite | Nontrivial Reachable | Channel Type |
|---|---|---|---|---|---|---|---|---|---|
| Electron $e^-$ ($Q_3$) | 8 | 12 | 5 | 1 | 48 | 1 | Yes | **No** | electron-like |
| Proton $p$ (closed) | 12 | 18 | 7 | 1 | 36 | 2 | No | **Yes** | nucleon-like |
| Neutron $n$ (open) | 12 | 17 | 6 | 0 | 4 | 7 | No | **Yes** | nucleon-like |

**Table 6.2　Cut-space readings (T9; item-by-item identical to Table 3.1 of the $Y_3$ verdict report, re-checked inside this project in §8.4)**

| Skeleton | $n_\mathrm{orb}$ | $\dim\operatorname{Cut}$ | $\dim(W\cap\operatorname{Cut})$ | $\operatorname{rank}_\mathrm{hol}$ | Reachable classes $2^\mathrm{rank}$ |
|---|---|---|---|---|---|
| $Q_3$ (electron) | 1 | 7 | 1 | **0** | 1 |
| $Y_3^\mathrm{cl}$ (proton) | 2 | 11 | 1 | **1** | 2 |
| $Y_3^\mathrm{op}$ (neutron) | 7 | 11 | 5 | **2** | 4 |

Conclusion (strengthened in v1.2): **The electron is forced into a trivial holonomy class by skeleton symmetry**—not "by coincidence", but because the only candidate assignment ($Q_3$ is edge-transitive $\Rightarrow$ all ones) happens to lie inside the cut space ($\dim(W\cap\operatorname{Cut})=n_\mathrm{orb}=1\Rightarrow\operatorname{rank}_\mathrm{hol}=0$); **the proton has exactly 1 bit of sign freedom** (of its two edge orbits exactly one assignment lies in the cut space, so the $H^1$ channel is open with exactly 2 reachable classes); **the neutron has 2 bits** (7 orbits, intersection dimension 5). Together with A0 this gives the structural origin of the electron/proton sign difference. The neutron has $\deg=0$, so $Q_{\text{model}}=0$ regardless of $\sigma$—**the magnitude channel alone makes the neutron neutral**.

### 6.1 Möbius-Family Experiments (M1–M9, 57/57 passed)

`verify_operator_19_mobius.py` uses explicitly constructed Möbius families to turn "nontrivial $\sigma$" from a theorem into a reproducible numerical experiment — providing **explicit certificates** for nontrivial classes (holonomy $-1$, non-coboundary, double-cover restoration).

**Construction Families**:

- **Möbius ladder $M_k$** $=$ even cycle $C_{2k}$ + antipodal chords $(i, i+k)$; $V=2k, E=3k, \beta_1=k+1$. $M_3$ degenerates to $K_{3,3}$; $M_4$ is the Wagner graph $V_8$ (the 1-skeleton of the smallest triangulation of the real projective plane). **Numbering convention (v1.2)**: this section uses the **in-book numbering** $M_k$ ($V=2k$) throughout; the $Y_3$ verdict report uses the **paper numbering** $M_{2n}=\mathrm{Cay}(\mathbb{Z}_{2n},\{1,n\})$ ($V=2n$). The two differ by a factor of 2; see Table 6.5 in §6.3.
- **Prism ladder $\Pi_k$** (control): two $k$-cycles + $k$ rungs; same $V$ and $E$ as $M_k$, differing only by the "twist".
- **Twisted even cycle**: on $C_{2k}$, mark two adjacent vertices with different colors to form a twist defect.

**Core Numerical Findings** (M1–M3):

| Family | $\beta_1$ | Channel Type | Structural Origin |
|---|---|---|---|
| $M_3 = K_{3,3}$ | 4 | **electron-like** | Bipartite + single orbit, forced trivial by T6 |
| $M_k, k\ge 4$ | $k+1$ | **nucleon-like** | Multiple orbits, $M\neq0$ (T2). **v1.2 refinement**: even $k$ is non-bipartite (contains odd cycles); odd $k$ is **bipartite**—here the channel opens via "bipartite + two orbits" ($\operatorname{rank}_\mathrm{hol}\ge1$), independently of odd cycles (P19.4 / T11) |
| $\Pi_k$ (even $k$) | $k+1$ | **electron-like** | Bipartite (contains even prism) + single orbit (even order) |
| $\Pi_k$ (odd $k$) | $k+1$ | **nucleon-like** | Contains triangular faces (odd cycles), **non-bipartite**. **v1.2 correction**: v1.1 inferred from this that "what actually determines the flip is the existence of odd cycles"—**that inference fails**: odd-$k\ge5$ ladders are bipartite (no odd cycle) yet have $\operatorname{rank}_\mathrm{hol}\ge1$ (§6.3, T11). The sole criterion is $W\not\subseteq\operatorname{Cut}$ (T9); the within-family co-occurrence of the flip with odd cycles is a **family-local coincidence** |

**Explicit Certificate of Nontrivial $\sigma$** (M4): On $M_4$, there exists a witness edge orbit that, when assigned $-1$ (all others $+1$), gives an Aut-invariant polarity $s_{\text{witness}}$ satisfying
1. $\sigma(\gamma) = -1$ (one odd cycle on the fundamental basis has holonomy $-1$);
2. An independent coboundary solver (unrelated to the implementation) returns False, confirming $s_{\text{witness}}$ is **not a coboundary**;
3. The Op19 injection gauge directly outputs $\sigma_{\text{class}}=$ nontrivially, with $Q_{\text{model}}=-1$.

**Double-Cover Restoration** (M5): $\sigma(\gamma^{2}) = \sigma(\gamma)^2 = +1$ — traversing the Möbius ladder twice returns to the trivial class (sign changes at $2\pi$, restores at $4\pi$), a direct numerical manifestation of Möbius-band topology.

**Vertex-Potential Gauge Always Trivial** (M6): Spin polarities $s_e=s_i s_j$ have holonomy **all $+1$** on $M_k$, reaffirming T1.

**Independent Cross-Check** (M7): Three independent gauges — DFS-independent cycle basis, $2^{\#\text{orbit}}$ exhaustive enumeration, independent coboundary solver — all agree with Op19 output.

**Forced Triviality of Electron Skeleton $Q_3$** (M8): Bipartite + single orbit; regardless of which Aut-invariant polarity is injected, Op19 always outputs electron-like.

**Polarity Injection API Regression** (M9): orbit / explicit dual gauges, Aut-invariance diagnostics, invalid-input validation — equivalent to §8.3 / X2/X3/X8.

### 6.2 Side-by-Side Dual $\mathbb{Z}_2$ Channel Verdict: $H^1$ Holonomy vs. Pfaffian Orientation (new in v1.2)

The $\sigma$ channel of Operator 19 is a holonomy class in $H^1(G;\mathbb{Z}_2)$. Graph theory contains another equally $\mathbb{Z}_2$-valued "sign" channel—the **Pfaffian orientation class** (D14). Whether the two share a common origin had previously been argued only indirectly on the ladder family; this section renders a side-by-side verdict on the **project's own nucleon skeletons**.

**Table 6.3　Side-by-side readings of the two channels ($Y_3$ verdict report §4.1)**

| Skeleton | $n_\mathrm{orb}$ | $\operatorname{rank}_\mathrm{hol}$ ($H^1$ channel) | $\#\mathcal M$ | $\lvert\mathcal O_\mathrm{Pf}\rvert$ | $\dim\mathcal O_\mathrm{Pf}$ | Pfaffian channel | nice even cycles |
|---|---|---|---|---|---|---|---|
| $Q_3$ (electron) | 1 | 0 | 9 | 128 | 6 | **solvable** | 0 |
| $Y_3^\mathrm{cl}$ (proton) | 2 | 1 | 6 | **0** | — | **unsolvable** | **42** |
| $Y_3^\mathrm{op}$ (neutron) | 7 | 2 | 4 | 16384 | 13 | **solvable** | **0** |

**Proposition P19.1 (Channel-Separation Verdict)**　On the closed nucleon skeleton the $H^1$ holonomy channel is **open** ($\operatorname{rank}_\mathrm{hol}=1$, exactly 2 reachable classes), while the Pfaffian channel is **closed** ($\mathcal O_\mathrm{Pf}=\emptyset$). Hence the project's core claim—that the charge sign is carried by $H^1$ holonomy rather than by Pfaffian orientation—obtains **direct side-by-side measurement on the project's own skeleton**, no longer resting only on the indirect argument "holds on the ladder family, fails to extrapolate to the skeleton".

**Theorem T10 (Minimal Unsatisfiable Row-Subset Certificate)**　The unbalanced system of $Y_3^\mathrm{cl}$ has $6$ rows (6 perfect matchings) $\times\,18$ columns (18 edges); its **full set of 6 rows** is a minimal unsatisfiable row subset: removing any single row leaves the remaining 5 rows **solvable** (maximum satisfiable row count $=5/6$). That is, $Y_3^\mathrm{cl}$ is **exactly one row away** from admitting a Pfaffian orientation.

**Proof**　By criterion D14, list the 6 perfect matchings row by row together with the right-hand sides $\mathrm{cr}$ (Table 6.4), and exhaust all $2^6$ row subsets: only the full set is unsatisfiable, while all 63 proper subsets are satisfiable; hence the full set is a minimal unsatisfiable row subset. $\blacksquare$

**Table 6.4　The unbalanced system of $Y_3^\mathrm{cl}$ (6 rows × 18 columns; right-hand sides are $\mathrm{cr}(M)$)**

| Row | Perfect matching $M$ | $\mathrm{cr}(M)$ |
|---|---|---|
| 1 | $\{(0,1),(2,6),(3,11),(4,7),(5,9),(8,10)\}$ | 1 |
| 2 | $\{(0,1),(2,10),(3,7),(4,6),(5,9),(8,11)\}$ | 0 |
| 3 | $\{(0,2),(1,5),(3,11),(4,7),(6,10),(8,9)\}$ | 0 |
| 4 | $\{(0,2),(1,9),(3,7),(4,5),(6,10),(8,11)\}$ | 1 |
| 5 | $\{(0,3),(1,5),(2,10),(4,6),(7,11),(8,9)\}$ | 1 |
| 6 | $\{(0,3),(1,9),(2,6),(4,5),(7,11),(8,10)\}$ | 0 |

"One row short" is confirmed by **exhausting all row subsets**, not heuristically.

**Proposition P19.2 (Structural Mechanism: nice even cycles vanish)**　$Y_3^\mathrm{cl}$ contains **42** nice even cycles (9 of length 6, 9 of length 8, 18 of length 10, 6 of length 12); the open state $Y_3^\mathrm{op}$, obtained by deleting one rim edge, has **0**, and the Pfaffian channel opens accordingly ($\dim=13$, $\lvert\mathcal O_\mathrm{Pf}\rvert=2^{13}$, with the particular solution independently cross-checked at $\mathrm{Pf}=+4=\#\mathcal M$). Thus the v1.1 qualitative observation—"a single closed/open decision flips existence"—now has a **concrete mechanism**.

> **Boundary 1 (an indicator is not a criterion)**　nice even cycles are only an **obstruction indicator**: used as a classifier on 22 samples it scores TP=4, FP=2, FN=3, TN=13 (false positives such as the Wagner graph $M_8$: nice=1 yet solvable; false negatives are mostly bipartite graphs). Ground truth always comes from the unbalanced system.
> **Boundary 2 (contract unchanged)**　Pfaffian orientation is an **adjacent graph-theoretic channel, not part of Operator 19's output**: the implementation introduces no new keys, `charge_channel_keys` still returns exactly **10 keys** (§8.3), and the freeze contract is untouched by this section.

### 6.3 Relation of $Y_3$ to the Möbius Ladder Family and the Numbering Convention (new in v1.2)

**Proposition P19.3 (Covering / Quotient Verdict)**　$Y_3^\mathrm{cl}$ is **non-isomorphic** to every $M_{2n}$ ($n\ge3$) (adjacency spectra and triangle counts both differ), admits **zero coverings** (complete backtracking enumeration over $M_4$–$M_{14}$ returns 0) and **zero quotients** (a quotient is a special case of a covering, so zero coverings implies zero quotients). **However**, $Y_3^\mathrm{cl}$ is a **$k=3$ regular cover of $K_4$** (unique covering; deck group of order 3; quotient $\cong K_4$; each of the four $K_4$ edges lifts 3 times). The "three-ness" of $Y_3$ (3 centers, 3 leg groups, 3 triangles, $\lvert\operatorname{Aut}\rvert=36=3!\times3!$, 2 edge orbits of 9 edges each) thereby receives a unified explanation: **$Y_3$ is a 3-fold complete graph**.

**Table 6.5　Numbering convention (factor 2; always check before cross-referencing)**

| Graph | In-book $M_k$ (even cycle $C_{2k}$ + antipodal chords, $V=2k$) | Paper $M_{2n}=\mathrm{Cay}(\mathbb{Z}_{2n},\{1,n\})$, $V=2n$ |
|---|---|---|
| $K_4$ | $M_2$ | $M_4$ |
| $K_{3,3}$ | $M_3$ | $M_6$ |
| Wagner graph | $M_4$ | $M_8$ |

**Proposition P19.4 (Full-Family Readings in the In-Book Convention, $k=2,\dots,24$)**　$n_\mathrm{orb}=1\iff k\in\{2,3\}$; even $k\iff$ non-bipartite, odd $k\iff$ bipartite; $\operatorname{rank}_\mathrm{hol}=0\iff k=3$.

**Theorem T11 (Necessary-and-Sufficient Condition for Opening the Sign Channel on the Ladder Family)**　On the ladder family, $\operatorname{rank}_\mathrm{hol}=0$ **if and only if** $k=3$ (i.e. $K_{3,3}$, the family's only "bipartite + single orbit" member). Hence every ladder with $k\neq3$ opens the sign channel; when $k\ge5$ is odd the graph is **bipartite** (no odd cycle) yet the channel is still open, with mechanism "bipartite + two orbits".

**Proof**　For $k=3$, single orbit + bipartite forces triviality by T6. For $k=2$ the graph is $K_4$: single orbit but contains triangles, so $\operatorname{rank}_\mathrm{hol}\ge1$. For $k\ge4$, $n_\mathrm{orb}=2$; if $k$ is even the graph contains odd cycles, if $k$ is odd it is bipartite—in either case at least one of the two orbits does not lie in the cut space (for odd $k$ the all-ones assignment lies in the cut space while the other does not), so $\dim(W\cap\operatorname{Cut})\le1<n_\mathrm{orb}=2$, and T9 yields $\operatorname{rank}_\mathrm{hol}\ge1$. $\blacksquare$

**Corollary T11.1 (Correction to T6 and §6.1)**　T6's "bipartite + single orbit $\Rightarrow$ forced triviality" is a **sufficient** condition whose **converse fails** (counterexample: odd-$k\ge5$ ladders—bipartite with two orbits, channel open). Therefore the §6.1 sentence "what actually determines the flip is the existence of odd cycles" **does not hold**, and the v1.1 §10 item 3 writing "odd cycle + multiple orbits" as a necessary condition is tightened accordingly: the sole necessary-and-sufficient criterion is $W(G)\not\subseteq\operatorname{Cut}(G)$ (T9).

---

## 7 Algorithms and Complexity

| Step | Input | Output | Complexity |
|---|---|---|---|
| 0 Polarity Selection | `polarity` + injection parameters (D3) | Edge polarities $s_e$ | Depends on gauge (explicit/orbit/topo $O(E)$; spin $O(n)$ + $O(E)$) |
| 1 Bond Graph | $A_s$ | Boolean adjacency $\mathrm{adj}$ | $\mathcal{O}(n^2)$ |
| 2 Graph Invariants | $\mathrm{adj}$ | $V,E,c,\beta_1,\deg,\text{bipartite}$ | $\mathcal{O}(n^2)$ |
| 3 Fundamental Cycle Basis | $\mathrm{adj}$ | $\{\gamma_i\}_{i\le\beta_1}$ | $\mathcal{O}(n^2+E\cdot L)$ |
| 4 Cycle Holonomy | $\{\gamma_i\},s$ | $\sigma$-vector, trivial | $\mathcal{O}(\sum_i\lvert \gamma_i\rvert )$ |
| 5 Automorphisms (optional) | $\mathrm{adj},\text{colors}$ | Edge orbits | Guarded by `aut_cap`/`aut_max_v` (default $V\le22$, otherwise skipped) |
| 6 Reachability (optional) | $\{\gamma_i\},\{\text{orbits}\}$ | $M$, nontrivial reachable, witness | $\mathcal{O}(\beta_1\cdot k)$ |

**Overall Complexity**: $\mathcal{O}(n^2 + \beta_1\cdot\bar L)$ (excluding automorphism enumeration); automorphism enumeration is the bottleneck, so the guard `aut_max_v=22` is set — exceeding it skips only reachability and **does not affect** $\sigma$-class discrimination or $Q_{\text{model}}$.

Polarity-selection validation contract (shared by both implementations): providing multiple injection gauges simultaneously raises `ValueError`; `orbit_signs` length $\neq$ number of orbits raises `ValueError`; `edge_polarity` missing edges or containing invalid values (not $\pm1$) raises `ValueError`; `polarity="spin"` missing `chi` raises `ValueError`. See §8.3 / X8.

---

## 8 Verification Protocol

The companion verification programs `verify_operator_19.py`, `verify_operator_19_mobius.py`, and `verify_operator_19_cross.py` each implement the assertions below; all must pass to empirically establish this specification.

### 8.1 Verification Program ↔ Theorem Mapping

| Item | Theorem | Family | Assertion |
|---|---|---|---|
| **V1** Skeleton Fidelity | §6 / charge-emergence §10.2 | $Q_3, Y_3$ closed, $Y_3$ open | $V,E,\beta_1,\deg,\lvert\operatorname{Aut}\rvert$, edge orbits, bipartite, nontrivial reachable — all match exactly |
| **V2** Vertex-Potential Triviality | T1, T1.1 | 40 random graphs + $Q_3$ | Spin polarities $s_e=s_is_j$ have holonomy all $+1$ |
| **V3** Reachability Criterion | T2, T2.1 | 30 random small graphs | Linear criterion $=$ $2^{k}$ exhaustive enumeration; trivial class always reachable |
| **V4** Cycle-Basis Independence | T3 | Random graphs (two spanning-forest roots) | Triviality criterion and $\sigma_{\text{canonical}}$ agree |
| **V5** Coboundary Gauge Invariance | T4, T4.1 | Random graphs + random vertex potentials | $\sigma'(\gamma)=\sigma(\gamma)$ on all cycles |
| **V6** $\deg$ Channel | D7, T5 | Skeletons + random graphs | $\deg=\beta_1\bmod2$ |
| **V7** Charge Functional Consistency | D8, T5 | Skeletons + molecules | $Q_{\text{model}}=\sigma_{\text{canonical}}\cdot\deg$ and $\in\{-1,0,1\}$ |
| **V8** Element-Coloring Necessity | T7 | Counterexample 4-cycle $[O,C,C,O]$ | Color-preserving criterion "nontrivial", non-color-preserving "trivial" (criterion flip) |
| **V9** End-to-End Pipeline | §1.2, §6 | Ethanol (tree), benzene (even cycle), cyclopentane (odd cycle) | Tree / even cycle $\to$ electron-like; odd cycle + multiple orbits $\to$ nucleon-like |
| **V10** Idempotency and Freeze Contract | D5, §6 | Fingerprint keys + `attach` guard | `charge_channel_keys` equal on two calls; fingerprint already containing `z2_deg` does not duplicate on re-attach |
| **V11** Graph Invariant Self-Consistency | §7 | Skeletons + random graphs | $\beta_1=E-V+c$; `has_odd_cycle` and bipartite are complementary |
| **V12** Molecular-Layer Criterion | T6, T7 | 6 molecular bond graphs | Even-cycle family electron-like; odd-cycle family nucleon-like |

### 8.2 Execution

Each verification program runs independently; any failing assertion exits with code 1:

```
python verify_operator_19.py          # V1–V12, 45 assertions (strict theorem-by-theorem)
python verify_operator_19_mobius.py   # M1–M9, 57 assertions (Möbius-family experiments)
python verify_operator_19_cross.py    # X1–X10, 29 assertions (cross-implementation parity + guard boundaries)
```

Zero external dependencies (only numpy + networkx; networkx used exclusively for automorphism enumeration).

### 8.3 Cross-Implementation Parity Results (X1–X10, 29/29 passed)

Operator 19 exists in two independently maintained parallel implementations sharing this specification but living in separate codebases:

| Implementation | Entry | Mirrors |
|---|---|---|
| Functional bridge | `operator_19_z2_charge_channel` | Single `sre_z2_holonomy_bridge.py` |
| Class-style release suite | `SREChargeChannelSuite.execute_operator_19_z2_charge_channel` | Three SHA-256 identical mirrors (`release/`, `math-vector_v2/`, `dist/windows/`) |

`verify_operator_19_cross.py` runs both implementations on the same inputs and compares every observable ($V,E,c,\beta_1,\deg,\sigma$-vector, $\sigma$-class, $\sigma_{\text{canonical}}, Q_{\text{model}}$, channel\_type, all reachability fields), covering:

- **X1** topo gauge on 32 graphs (Möbius $M_3$–$M_8$, prisms $\Pi_3$–$\Pi_8$, $Q_3$, $Y_3$ closed/open, $K_{2,2,2}$, 16 random connected graphs)
- **X2** explicit gauge in three variants (all $+1$ / first edge flipped / per-edge random $\pm1$)
- **X3** orbit gauge in four variants (all+1 / all−1 / flip-first / flip-witness)
- **X4** spin gauge (including `spin_net_sign`)
- **X5** freeze contract: `charge_channel_keys` always returns 10 keys with pairwise equality between both implementations; the key count does not change when reachability is skipped (inner fields set to `None`)
- **X6** $V>\text{aut\_max\_v}$ guard (including custom `aut\_max\_v=10` trigger): both implementations consistently skip reachability with identical skip reason, while $\sigma$-class remains valid
- **X7** disconnected graph (two triangles): both implementations agree on $c=2,\beta_1=E-V+c$
- **X8** 8 classes of invalid input (illegal polarity gauge, multiple gauges conflict, wrong length, missing edge, non-$\pm1$ value, spin missing chi, orbit on $V>\text{aut\_max\_v}$): both implementations raise `ValueError` of the same type
- **X9** effect of element coloring on orbits and reachability: both implementations agree
- **X10** vertex relabeling invariance: $\sigma$-class / channel\_type / invariants are unchanged under random permutations, and both implementations still agree after relabeling

All 29 assertions pass, proving **behavioural convergence** of this specification across two independent codebases — there is no room for "ambiguous interpretation of the specification text".

> **Freeze Contract (D5, must not be violated)**: `charge_channel_keys(res)` must always return exactly **10 keys**; both implementations have been verified to comply, and no future implementation may change this count.

### 8.4 Re-Check of the External Verdict Report (new in v1.2, gates A–F)

Every conclusion of the $Y_3$ verdict report is re-checked gate by gate across six gates; inside this project **no implementation is modified and no key is added**—only an independent script calls the existing bridge functions to recompute the observables:

| Gate | What is re-checked | Verdict |
|---|---|---|
| **A** Object fidelity | $V,E,\beta_1,\deg,\lvert\operatorname{Aut}\rvert$, edge-orbit count and bipartiteness of $Y_3^\mathrm{cl}$ / $Y_3^\mathrm{op}$ | Item-by-item identical to Table 6.1 of §6 |
| **B** Cut-space identity | The four-column readings $n_\mathrm{orb},\dim\operatorname{Cut},\dim(W\cap\operatorname{Cut}),\operatorname{rank}_\mathrm{hol}$ for the three skeletons; compatibility of $\operatorname{rank}_\mathrm{hol}$ with the T2 criterion $M\neq0$ | $Q_3=0$, $Y_3^\mathrm{cl}=1$, $Y_3^\mathrm{op}=2$—**independently reproduced inside this project** |
| **B′** Basis-selection pitfall | Cut-space basis taken as the star set $d(\{v\})$ vs. mistakenly as "spanning-tree path edge sets" (the latter is actually the cycle space) | The star-set convention reproduces all readings; the mistaken convention mismatches 566 of 996 cases in the report, confirming that the D12 pitfall warning is necessary |
| **C** Four-route zero mismatch | Matrix rank (T2) / cut-space intersection dimension (T9) / $H^1$ class enumeration / subset enumeration—four independent routes | Zero mismatch over 22 samples; T9.2 holds |
| **D** Pfaffian certificate | Unsolvability of the unbalanced system and the minimal unsatisfiable row subset (T10), cross-check of the particular solution $\mathrm{Pf}$, nice-even-cycle counts and classifier metrics | Item-by-item identical (Tables 6.3 and 6.4); the indicator's false-positive/false-negative boundaries are as stated in §6.2 and do not affect the criterion |
| **E** Covering verdict and convention | Isomorphism / covering / quotient verdict of $Y_3^\mathrm{cl}$ against $M_{2n}$; the 3-fold cover $Y_3^\mathrm{cl}\to K_4$; the in-book $M_k$ vs. paper $M_{2n}$ correspondence | Consistent (P19.3, Table 6.5) |
| **F** Numbering and conclusion revisions | Whether the report's two corrections to v1.1 (the §6.1 odd-cycle criterion and the §10 item 3 necessary condition) are absorbed in this document | Absorbed (T2.3, T11.1, §10) |

**Note on method**: the re-check script **is not persisted as a standalone verification program**—it reuses `edge_list / automorphisms / edge_orbits` and the skeleton constructors of `sre_z2_holonomy_bridge.py`, appending cut-space dimension computations only outside the library. Hence the counts for V1–V12 / M1–M9 / X1–X10 remain unchanged (45 / 57 / 29). If T9 is later to enter routine regression, it should be added as **V13**, with the three assertion counts and the freeze-contract wording updated together.

---

## 9 Boundaries with Existing Operators (1–18 Non-Overlap Declaration)

Operator 19 has been pairwise verified against all 18 operators in `SRE-math_C.md`, confirming **no overlap**:

| Neighbouring Operator | Its Responsibility | Boundary with Operator 19 |
|---|---|---|
| **Operator 12** (Topological Closure Cycle Audit) | Outputs $n_{\text{loops}}=\beta_1$ and Möbius phase ratio $t_{2k}/(2t_k)$ (**spectral heuristic**) | 12 gives **cycle count** (magnitude); 19 gives the **cohomology class $\sigma$ of edge-polarity cochains** (sign). 12's mobius_ratio has **no cycles, no edge polarities, and no class**, so it is **not** a rigorous $\mathbb{Z}_2$ holonomy; 19 is its rigorous counterpart |
| **Operator 14** (Equation Residual Hodge Routing) | Decomposes residual 1-chains into $\mathrm{im}\,\partial_1\oplus\mathcal{H}_1\oplus\mathrm{im}\,\partial_2^{T}$ | 14 does orthogonal decomposition on the **1-chain space** $C_1$; 19 takes cohomology classes on the **1-cochain space** $C^1$. They are Hodge duals: the gradient component $\mathrm{im}\,\partial_1$ of 14 is exactly dual to T1's **coboundary** trivial class |
| **Operator 7** ($B_{co}$ Circulation Hedging) | Dynamics: circulation $B$-field leapfrog hedging | 7 is **dynamics** (circulation flow update); 19 is a **static invariant** (classification of given $s$) |
| **Operator 9 / 17** (Betti Audit / Termination Verdict) | Change or audit **topology** $\beta_1$ | 9/17 change or audit the magnitude channel; 19 gives the sign channel on **fixed topology** |
| **Operator 18** (Homological Solution Implementation) | Step 5 uses Fiedler sign gate to assign spin $\Gamma(k,j)=\operatorname{sgn}(v_2(j))$ | 18's spin assignment is of **vertex-potential type**, whose holonomy is always trivial by **T1**; 19 proves "18's assignment cannot produce nontrivial sign channels" — forming a handshake boundary |
| **Operator 11** (Spin-Charge Adjacency) | Outputs diagnostics $s_i,\sigma_{ij},d_{ij}$ | 11's $\sigma_{ij}=s_is_j$ is **precisely** the trivial-class example of T1; 19 locates it as "incapable of producing sign" |

**Layer Positioning**: After the Open-Source Foundational Layer (1–6), Homological Stitching Core Layer (7–10), Electronic Degrees-of-Freedom Extension Layer (11–12), and Spectral Equation Solving Layer (13–18), this is the **fifth layer — the Charge Symbol / $\mathbb{Z}_2$ Holonomy Channel Layer (19)**.

---

## 10 Honest Boundaries and Scope

1. **Internal model construction, not a physical assertion**. All conclusions of this specification are **internally self-consistent constructions** of the SRE model; $Q_{\text{model}}$ is the **in-model charge tier** ($\in\{-1,0,+1\}$) and does not constitute a physical assertion about the charge values of real molecules or particles.
2. **Aut-invariance is an explicit assumption**. Reachability conclusions (T2, T6) rely on the **explicit assumption** "edge polarities are invariant under automorphisms" from charge-emergence paper §13.2. **Without this assumption**, any graph containing cycles admits nontrivial classes (1 bit of freedom, dimension $=\beta_1$) and reachability analysis collapses to a trivial fact.
3. **The necessary-and-sufficient condition for nontrivial reachability is the cut-space criterion, not the odd-cycle criterion (corrected in v1.2)**. v1.1 wrote "contains **odd cycles** and has $\ge2$ edge orbits" as a necessary condition; **that formulation has been falsified**: odd-$k\ge5$ ladders are bipartite (no odd cycle) yet have $\operatorname{rank}_\mathrm{hol}\ge1$ (T11). The correct statement is T9: $W(G)\not\subseteq\operatorname{Cut}(G)$, equivalent to $M\neq0$ of T2. **Bipartiteness, odd-cycle existence and orbit count are all non-necessary**; they co-occur with the conclusion only inside specific families.
4. **Molecular layer requires element coloring**. The Aut of molecular bond graphs must respect element labels (T7), otherwise different elements like C and H may be conflated and the orbit structure distorted.
5. **Scale guard**. Automorphism enumeration uses a guard at `aut_max_v=22`; very large graphs skip only reachability analysis, while $\sigma$-class discrimination and $Q_{\text{model}}$ remain valid.
6. **$A_s$ semantics**. Operator 19 reuses the $A_s$ from Operators 1/4, whose bond-graph support $A_s>0$ is guaranteed upstream (cooperative edges $E^+$ of SRE Axiom 1); if the upstream $A_s$ contains numerical noise, judge with `bond_graph_from_As(eps)` using the $\epsilon$ parameter.
7. **The cut-space basis must be the star set (v1.2)**. Take the basis of $\operatorname{Cut}$ as $d(\{v\})$; if it is mistakenly taken as "the tree-path edge set from $v$ to the root", the result is the **cycle space** rather than the cut space, and $\operatorname{rank}_\mathrm{hol}$ is systematically distorted (566 of 996 cases mismatch in the report; §8.4 gate B′).
8. **Pfaffian is an external control channel, not an Operator 19 output (v1.2)**. The Pfaffian readings of §6.2 enter no computation and add no key; `charge_channel_keys` still returns exactly **10 keys**. Pfaffian logic needs its own entry point and must not be attached to Operator 19's return value.
9. **nice even cycles are only an indicator (v1.2)**. On the 22-sample classifier it scores TP=4 / FP=2 / FN=3 / TN=13 and **must not** be used as a criterion; ground truth must come from the unbalanced linear system (D14).
10. **The numbering convention must be stated (v1.2)**. The in-book $M_k$ ($V=2k$) and the paper's $M_{2n}$ ($V=2n$) differ by a factor of 2; every cross-reference to ladder numbering must write both conventions (Table 6.5), otherwise correspondences such as $K_{3,3}=M_3=M_6$ shift by one slot.
11. **Cross-skeleton comparability of $\operatorname{rank}_\mathrm{hol}$ has a precondition (v1.2)**. It depends only on the orbit structure and the cut space, hence is label-independent (superior to $\varrho$-type quantities); but it is **comparable only under the same Aut constraint**—after relaxing the Aut constraint the space becomes all of $C^1$ with dimension $\beta_1$, which cannot be mixed with the $n_\mathrm{orb}$ convention.

---

## 11 Conclusion

Operator 19 grounds the $\sigma$ **sign channel** from the charge-emergence paper as a standalone module:

- **Well-defined** (T0): On 1-complexes, $\sigma$ is an $\mathbb{F}_2$-linear functional on $H_1$, free of representative ambiguity;
- **Nonmanufacturability of sign** (T1/T1.1): Vertex-potential polarities (including Operator 11's spin polarities and Operator 18's sign assignment) always have trivial holonomy — charge sign cannot be manufactured by local spin relabeling;
- **Closed-form reachability criterion** (T2/T2.1/T2.2): Nontrivial reachable $\iff M\neq0$, $\mathcal{O}(\beta_1 k)$, no $2^k$ enumeration;
- **Necessary-and-sufficient criterion and bit counting** (T9/T9.2, v1.2): $\operatorname{rank}_\mathrm{hol}=n_\mathrm{orb}-\dim(W\cap\operatorname{Cut})$, reachable classes $=2^{\operatorname{rank}_\mathrm{hol}}$; two independent computational routes agree with zero mismatch over 22 samples;
- **Side-by-side verdict of the dual $\mathbb{Z}_2$ channels** (§6.2, v1.2): on $Y_3^\mathrm{cl}$ the $H^1$ channel is open (1 bit) while the Pfaffian channel is unsolvable (minimal unsatisfiable certificate: all 6 rows needed for contradiction), so the attribution of the sign is settled by measurement rather than inference;
- **Covering relation and numbering convention** (§6.3, v1.2): $Y_3^\mathrm{cl}$ has zero coverings and zero quotients over the ladder family, yet is a 3-fold regular cover of $K_4$; the factor-2 correspondence between the in-book $M_k$ and the paper's $M_{2n}$ is tabulated;
- **Gauge invariance** (T3/T4): Triviality criterion is independent of cycle basis, $\sigma$ is immune to vertex-potential relabeling, depending only on $[s]\in H^1$;
- **Two-channel separation** (T5): Sign $\sigma$ and magnitude $\deg$ are orthogonal, $Q=\sigma\deg$;
- **Structural origin of electron/nucleon type** (T6/T11.1): Even-cycle + single orbit forces triviality (electron)—but the **converse fails**: odd-$k\ge5$ ladders are bipartite yet open the channel; the criterion converges to T9;
- **Necessary component of molecular layer** (T7): Element-color-preserving Aut; otherwise criterion flips.

While sharing the same graph ($A_s$) with upstream electronic operators, it outputs `z2_*` scalar keys piped into compound screening pipelines, enabling atomic/electronic-level high-speed sign-channel computation.

---

## Appendix A: Symbols and Notation

| Symbol | Meaning |
|---|---|
| $G=(V,E)$ | Bond graph (1-dimensional chain complex), $V$ vertices, $E$ edges |
| $c$ | Number of connected components |
| $\beta_1=E-V+c$ | First Betti number $=\dim H_1$ |
| $s_e\in\{+1,-1\}$ | Edge polarity (1-cochain) |
| $z_e=\varphi(s_e)\in\mathbb{F}_2$ | Booleanised polarity |
| $\sigma(\gamma)=\prod_{e\in\gamma}s_e$ | Cycle holonomy |
| $[s]\in H^1(G;\mathbb{F}_2)$ | Cohomology class of $\sigma$ |
| $\delta C^0$ | Coboundary (vertex-potential cochain) |
| $O_o$ | Edge orbit under Aut |
| $m_{i,o}$ | Number of edges from orbit $o$ in fundamental cycle $i$, mod 2 |
| $M=(m_{i,o})$ | Reachability matrix, nontrivial reachable $\iff M\neq0$ |
| $W(G)=\operatorname{span}\{\mathbf 1_{O_o}\}$ | Aut-invariant assignment subspace, $\dim=n_\mathrm{orb}$ (v1.2) |
| $\operatorname{Cut}(G)=d(S)$ | Cut space $=\operatorname{im}\delta_0$, $\dim=n-c$; basis taken as the star set $d(\{v\})$ (v1.2) |
| $\operatorname{rank}_\mathrm{hol}=\dim\operatorname{im}\Phi_G$ | Sign-channel bit count, reachable classes $=2^{\operatorname{rank}_\mathrm{hol}}$ (v1.2) |
| $\mathcal O_\mathrm{Pf}$ | Pfaffian orientation solution set (external control channel, not an Operator 19 output) (v1.2) |
| $\deg=\beta_1\bmod2$ | Magnitude channel |
| $Q_{\text{model}}=\sigma_{\text{canonical}}\cdot\deg$ | In-model charge tier |
