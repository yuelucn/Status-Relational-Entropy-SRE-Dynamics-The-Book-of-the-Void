# Operator 19: ℤ₂ holonomy / σ charge-sign channel operator
## Strict mathematical specification, solvability reasoning basis and verification protocol

**Version**: 1.0 (October 2026 · Operator No. 19 of the SRE operator system)
**Reference implementation**: `sre_z2_holonomy_bridge.py` (public entry `operator_19_z2_charge_channel`)
**Companion verification program**: `verify_operator_19.py` (independent strict verification, V1–V12, zero external dependencies beyond numpy/networkx)
**Prerequisite dependencies**: Operators 1/4 (bond-graph support of the SRE smooth adjacency $A_s$), Operator 11 (spin-polarity diagnostics $s_i,\sigma_{ij}$), Operator 12 (first Betti number $\beta_1$ loop counting)
**Upstream paper**: *Emergence of Positive and Negative Charge under the SRE Framework: Magnitude, Sign and Numerical Confirmation* (hereafter the "charge-emergence paper")
**Downstream integration**: `sre_cluster_substitute_screen.py` (the `z2_*` fields are fed into the compound-screening pipeline)
**Numbering note**: the operator continues the numbering after the existing No. 18 as **19**; it has been checked one by one against all 18 operators of `SRE-math_C.md` and found to have **no overlap** (boundaries in §9).

---

## Abstract

SRE dynamics expresses charge as "the counting of topological knots". Counting is naturally non-negative and yields only the **magnitude** of charge, never the **sign**. The charge-emergence paper fills this gap by proposing the charge functional

$$Q(K)=\sigma(K)\cdot\deg(K)\cdot e,\qquad \deg(K)=\beta_1(K)\bmod 2,\qquad \sigma(K)\in H^1(G;\mathbb{Z}_2).$$

Here the "sign channel" $\sigma$ is declared to be a **$\mathbb{Z}_2$ holonomy** cohomology class, but that paper only performs sampled verification with an **independent numerical script** (`_se_assignment_test.py`) on a few skeletons and molecules, and **does not provide an independent, reusable, provable implementation specification for this operator**. This paper implements the $\sigma$ channel **on its own** as **Operator 19**, and supplies three previously missing contents:

1. **Strict reasoning basis** (§2–§5): on the **1-dimensional chain complex** of the molecular bond graph, the chain "edge polarity $\to$ loop holonomy $\to$ cohomology class" is made rigorous, the well-definedness of the operator output is proved, and **all theorems and proofs** (T0–T8) are given.
2. **The corresponding paper** (this document): it gives the operator's axiomatic positioning, the bridging semantics with the upstream electronic operator, the boundary with the existing operators, and a faithful reproduction on the official skeletons and at the molecular layer.
3. **Strict verification program** (`verify_operator_19.py`): each theorem is mapped to a reproducible assertion (V1–V12); running all of them and passing empirically confirms this specification.

Core conclusions (all of which hold rigorously on the 1-dimensional complex and depend on no external parameters):

| No. | Theorem | Meaning |
|---|---|---|
| **T0** | On the 1-complex, $\sigma$ is an $\mathbb{F}_2$-linear functional on $H_1$ | Well-defined, comparable |
| **T1** | The holonomy of a vertex-potential-type polarity $s_e=t_it_j$ is **always trivial** | **The charge sign cannot be produced by local spin relabeling** |
| **T2** | Non-trivial reachability of Aut-invariant assignments $=$ $\mathbb{Z}_2$ linear criterion ($\exists$ loop $i$ and orbit $o$ with $m_{i,o}=1$) | No $2^{\#\text{orbits}}$ enumeration needed |
| **T3** | The triviality test is **independent of the choice of cycle basis** | The result is unique |
| **T4** | Multiplying by a **coboundary** (vertex potential) does not change any loop holonomy | $[s]\in H^1$ is a gauge invariant |
| **T5** | The sign channel $\sigma$ and the magnitude channel $\deg$ are **orthogonally independent** | The two channels are encoded separately |
| **T6** | Bipartite graph + single edge orbit $\Rightarrow$ **forced trivial** (electron-like) | Structural origin of the electron $Q_3$ |
| **T7** | At the molecular layer, Aut **must preserve the element coloring**, otherwise the reachability criterion is distorted (the verdict can flip) | Necessity of element coloring |
| **T8** | For a composite, $\sigma_{\text{comp}}=\prod_i\sigma_i$, and $Q$ is recomputed on the new boundary | Connects to A2/A3 |

**Keywords**: $\mathbb{Z}_2$ cohomology; holonomy; coboundary; vertex potential; edge orbit; Aut-invariant assignment; charge-sign channel; first Betti number

---

## 1 Problem statement

### 1.1 The gap

The charge-emergence paper (§3–§4) gives:

- the **magnitude channel** $\deg(K)=\beta_1(K)\bmod 2$ (§5);
- the **sign channel** $\sigma(K)=\prod_{e\in\partial K}s_e\in\{+1,-1\}$ (Definition D4), and declares $\sigma\in H^1(G;\mathbb{Z}_2)$;
- the **charge functional** $Q(K)=\sigma(K)\cdot\deg(K)\cdot e$ (Axiom A1).

But the sign channel of that paper **is only verified by sampling on a small number of discrete skeletons**, and it lacks:

1. **a strict argument for well-definedness** — whether $\prod_{e\in\partial K}s_e$ really depends only on the homology class of $K$ (and not on the representative);
2. **a reusable implementation** — how to land $\sigma$ on an arbitrary molecular bond graph and share the same graph with the electronic operator;
3. **a strict criterion for reachability** — under what conditions a non-trivial class is reachable (the structural origin of the "opposite sign of electron/proton").

### 1.2 Task of this paper

To establish the $\sigma$ channel **on its own** as Operator 19:

- **Input**: the SRE smooth adjacency $A_s$ output by Operators 1/4 (bond-graph support is $A_s>0$), electronegativity $\chi$ (spin convention), element labels (molecular coloring);
- **Output**: graph invariants $\{V,E,c,\beta_1,\deg,\text{bipartite},\text{has\_odd\_cycle}\}$, the $\sigma$ class $\{\sigma\text{-vector},\sigma\text{-class},\text{trivial}\}$, Aut-invariant reachability, and the model-internal charge grade $Q_{\text{model}}=\sigma\cdot\deg$;
- **Properties**: T0–T8 (§5).

---

## 2 Mathematical preliminaries

### 2.1 The graph as a 1-dimensional chain complex

Let the bond graph be $G=(V,E)$, with $|V|=n$ and $|E|=m$. The SRE system **operates only on a 1-dimensional complex (a graph)** — there are no 2-cells (faces), hence

$$Z_1=\ker\partial_1,\qquad B_1=\mathrm{im}\,\partial_2=0,\qquad H_1(G;\mathbb{F}_2)=Z_1/B_1=Z_1,\qquad \dim H_1=\beta_1=E-V+c,$$

where $c$ is the number of connected components. **Key point**: because there are no 2-cells, $B_1=0$, and $H_1$ is the cycle space itself ("the number of loops = the homology dimension", consistent with $n_{\text{loops}}=\beta_1$ of Operator 12).

Dually, for the cochain complex $C^0\xrightarrow{\delta}C^1\xrightarrow{\delta}C^2$, since $C^2=0$ (no 2-cells), we have $Z^1=C^1$ and $B^1=\delta C^0$, hence

$$H^1(G;\mathbb{F}_2)=C^1/\,\delta C^0.$$

Here $\delta C^0$ is the **coboundary** (vertex-potential-type 1-cochain). The pairing $H^1\times H_1\to\mathbb{F}_2$ is given by $\langle [s],[\gamma]\rangle=\sum_{e\in\gamma}z_e$.

### 2.2 Polarity–Boolean isomorphism

**Lemma 2.1 (polarity–Boolean isomorphism)** The map $\varphi:\{+1,-1\}\to\mathbb{F}_2$, $\varphi(S)\equiv\frac{1-S}{2}$ ($-1\mapsto1,\ +1\mapsto0$), is a group isomorphism $(\{+1,-1\},\cdot)\cong(\mathbb{F}_2,\oplus)$.

**Proof** The bijection is obvious. Check the homomorphism property: $\varphi(S_1S_2)=1$ if and only if exactly one $S_k=-1$, consistent with $\varphi(S_1)\oplus\varphi(S_2)$; the four input combinations are verified one by one. $\square$

Hence "polarity multiplication" and "addition modulo 2" correspond strictly one-to-one, and in the sequel we compute in $\mathbb{F}_2$ (writing $z_e\equiv\varphi(s_e)$).

### 2.3 The binary nature of SRE Axiom 1

SRE Axiom 1 (no zero element) guarantees that every edge can only take $s_e\in\{+1,-1\}$, i.e. $z_e\in\mathbb{F}_2$ has no "default/undefined" state. **This is the premise that lets Operator 19 be defined on the full space $C^1$ of edges** (independent of whether an edge "exists or not").

---

## 3 Definitions

**D1 (bond graph $G$)** Given by the support of $A_s$: $G=(V,E)$, $E=\{(i,j):A_s{}_{ij}>0,\,i<j\}$. (Corresponds to the cooperative edges $E^+$ of SRE Axiom 1.)

**D2 (edge-polarity 1-cochain $s$)** $s:E\to\{+1,-1\}$, $z_e\equiv\varphi(s_e)\in\mathbb{F}_2$; $s\in C^1(G;\mathbb{F}_2)$.

**D3 (literal convention / vertex-potential convention)**
- **Literal convention** (charge-emergence paper A1): every cooperative edge takes $s_e=+1$ (topologically all-positive);
- **Spin convention** (Operator 11 diagnostics): $s_e=s_i\cdot s_j$, $s_i=\operatorname{sign}(\chi_i-\bar\chi)$.

**D4 (loop holonomy)** For a loop $\gamma$ (vertex sequence $v_0v_1\cdots v_{L-1}v_0$): $\sigma(\gamma)\equiv\prod_{k}s_{(v_k,v_{k+1})}$, equivalently $\sigma(\gamma)=\big(\sum_{e\in\gamma}z_e\big)\bmod 2$.

**D5 (fundamental cycle basis)** Take a spanning forest of $G$ (BFS parent), pair each non-tree edge $(u,v)$ with the tree path $u\leadsto v$ to form the fundamental cycle $\gamma_i$, $i=1,\dots,\beta_1$. $\{\gamma_i\}$ is a basis of $H_1$.

**D6 ($\sigma$ class / triviality)** $[s]=s+\delta C^0\in H^1$. Call $[s]$ **trivial** ($[s]=0$) if and only if $s\in\delta C^0$ (i.e. there exists a vertex potential $t\in\{\pm1\}^V$ with $s_e=t_it_j$), equivalently **all $\sigma(\gamma_i)=+1$ on the fundamental cycle basis**. $\sigma_{\text{canonical}}\equiv+1$(trivial)$/-1$(non-trivial).

**D7 (magnitude channel $\deg$)** $\deg(K)\equiv\beta_1(K)\bmod 2$. (Independent of $s$.)

**D8 (model-internal charge grade $Q_{\text{model}}$)** $Q_{\text{model}}\equiv\sigma_{\text{canonical}}\cdot\deg\in\{-1,0,+1\}$ ($e$ normalized to 1).

**D9 (Aut-invariant assignment)** Let the automorphism group $\operatorname{Aut}(G)$ (at the molecular layer, the **element-preserving** automorphisms, see T7) act on $E$, partitioning $E$ into edge orbits $\{O_1,\dots,O_k\}$. Call $s$ **Aut-invariant** if $s$ is constant on each orbit.

**D10 (channel type)**
- **electron-like (forced trivial)**: under Aut-invariant assignments, **all** $s$ are trivial;
- **nucleon-like (non-trivial allowed)**: $\exists$ Aut-invariant $s$ that is non-trivial.

---

## 4 Axioms (inherited from the charge-emergence paper)

**A1 (charge functional)** $Q=\sigma\cdot\deg\cdot e$, $\sigma\in H^1(G;\mathbb{F}_2)$.
**A2 (composite recomputation)** For a composite knot $K_{\text{comp}}$, $\sigma_{\text{comp}}=\prod_i\sigma_i$ ($\mathbb{F}_2$ addition), $\deg_{\text{comp}}=\beta_1(K_{\text{comp}})\bmod2$.
**A3 (separable additivity)** For independent knots, $Q_{\text{tot}}=\sum_i Q(K_i)$.
**A0 (sign datum)** The holonomy class in which the electron lies is stipulated to be "negative" (gauge convention).

**Convention statement of Operator 19**: Operator 19 implements the $\sigma$ channel and the $\deg$ channel and outputs $Q_{\text{model}}$ as the **model-internal charge grade**; the "negative" datum of A0 is carried by $\sigma_{\text{canonical}}=-1$.

---

## 5 Core theorems and proofs

> The following theorems are all stated on the **graph (1-dimensional complex)**, where $c$ is the number of connected components and $\beta_1=E-V+c$.

### T0 (well-definedness: $\sigma$ is an $\mathbb{F}_2$-linear functional on $H_1$)

**Statement** On a graph without 2-cells, $B_1=0$, hence $H_1=Z_1$; the map $\sigma:Z_1\to\mathbb{F}_2$, $\gamma\mapsto\sum_{e\in\gamma}z_e$ is a linear functional and depends only on the chain $\gamma$ itself.

**Proof** $\partial_2=0\Rightarrow B_1=0\Rightarrow H_1=Z_1$, so a loop is a homology class, and $\sigma$ has no "representative ambiguity" problem. Linearity: let $\gamma_1,\gamma_2\in Z_1$; then $\sigma(\gamma_1+\gamma_2)=\sum_{e\in\gamma_1\triangle\gamma_2}z_e=\sigma(\gamma_1)+\sigma(\gamma_2)\ (\mathrm{mod}\,2)$, because a common edge appears twice in the symmetric difference and cancels modulo 2. $\blacksquare$

**Remark** This is a point where Operator 19 is simpler than general graph theory: the molecular bond graph has no "faces" filling the loops, so the statement "$\sigma\in H^1$" in the charge-emergence paper **holds automatically** at the graph level, with no additional 2-cell structure needed.

### T1 (vertex-potential triviality theorem)

**Statement** Let $s_e=t_i\cdot t_j$ ($t\in\{\pm1\}^V$, i.e. $s$ is a $\delta$-type vertex potential); then for **any** closed chain $\gamma$ we have $\sigma(\gamma)=+1$; that is, $[s]=0$.

**Proof**
$$\sigma(\gamma)=\prod_{(i,j)\in\gamma}s_i s_j=\prod_{v\in\gamma}t_v^{\,\deg_\gamma(v)},$$
where $\deg_\gamma(v)$ is the number of edges of the closed chain $\gamma$ incident to $v$ (in + out). A closed chain satisfies in-out conservation at every vertex, so $\deg_\gamma(v)$ is **even**, hence $t_v^{\deg_\gamma(v)}=+1$, and the product gives $\sigma(\gamma)=+1$. $\blacksquare$

**Corollary T1.1 (the charge sign cannot emerge from local spin relabeling)** The spin polarity $s_e=s_i s_j$ of Operator 11 is **exactly** of vertex-potential type; by T1 its holonomy is always trivial. Therefore:

> **The sign channel $\sigma$ of charge must come from a genuine non-coboundary cochain $[s]\neq0\in H^1$, and cannot be produced by relabeling local spins at the vertices.**

This explains why "merely assigning a spin sign to the vertices" is insufficient to produce a net charge sign — it lies in the trivial class of $H^1$.

### T2 (the $\mathbb{Z}_2$ linear criterion for Aut-invariant reachability)

**Statement** Let the edge orbits of $\operatorname{Aut}(G)$ be $O_1,\dots,O_k$, and let an Aut-invariant assignment take the value $z_o\in\mathbb{F}_2$ on orbit $o$. Define

$$m_{i,o}\equiv\#\{e\in O_o\cap\gamma_i\}\bmod2\in\mathbb{F}_2,\qquad M=(m_{i,o})\in\mathbb{F}_2^{\beta_1\times k}.$$

Then $\sigma(\gamma_i)=\bigoplus_{o}m_{i,o}z_o$, and

$$\boxed{\ \text{a non-trivial class is reachable}\iff \exists\,i,o:\ m_{i,o}=1\iff M\neq 0\ }$$

**Proof** By the linearity of T0, $\sigma(\gamma_i)=\sum_{e\in\gamma_i}z_e=\sum_o z_o\cdot\#(O_o\cap\gamma_i)=\bigoplus_o m_{i,o}z_o$, i.e. the linear map $T:\mathbb{F}_2^k\to\mathbb{F}_2^{\beta_1}$ given by $M$, $z\mapsto Mz$.
- ($\Leftarrow$) If $\exists m_{i,o}=1$, take $z=e_o$ (only $z_o=1$); then $\sigma(\gamma_i)=m_{i,o}=1\neq0$, so a non-trivial class is reachable (the trivial class $z=0$ is always reachable).
- ($\Rightarrow$) If $M=0$, then $\forall z$, $Mz=0$, all loop holonomies are always $+1$, and no non-trivial class is reachable.
Hence reachability is equivalent to $M\neq0$, i.e. one only needs to **find any non-zero entry** in $M$, with complexity $\mathcal{O}(\beta_1\cdot k)$, and **without** doing $2^k$ lexicographic enumeration. $\blacksquare$

**Corollary T2.1** The trivial class is **always reachable** (take the all-zero assignment $s_e\equiv+1$). A non-trivial class is reachable **if and only if** some edge orbit occurs an odd number of times on some fundamental cycle.

### T3 (independence from the choice of cycle basis)

**Statement** The triviality test of $\sigma$ ($[s]=0$) is independent of the choice of fundamental cycle basis $\{\gamma_i\}$.

**Proof** Take any two fundamental cycle bases $\{\gamma_i\},\{\gamma'_j\}$; both are bases of $H_1=Z_1$, hence $\gamma'_j=\sum_i a_{ji}\gamma_i$ ($a_{ji}\in\mathbb{F}_2$). By the linearity of T0, $\sigma(\gamma'_j)=\bigoplus_i a_{ji}\sigma(\gamma_i)$. Therefore "all zero on one basis" is equivalent to "all zero on the other basis", and the triviality test is unique. $\blacksquare$

### T4 (coboundary gauge invariance / the cohomology class is a gauge invariant)

**Statement** Let $s'=s\cdot\delta t$ (i.e. $s'_e=s_e\,t_it_j$, $t\in\{\pm1\}^V$). Then $\forall\gamma:\sigma'(\gamma)=\sigma(\gamma)$; hence $\sigma$ depends only on $[s]\in H^1$.

**Proof** $\sigma'(\gamma)=\big(\prod_{e\in\gamma}s_e\big)\cdot\big(\prod_{e\in\gamma}t_it_j\big)=\sigma(\gamma)\cdot1$, the last factor being identically $+1$ by T1. $\blacksquare$

**Corollary T4.1** The quotient structure $H^1=C^1/\delta C^0$ corresponds exactly to "$\sigma$ is immune to vertex-potential relabeling"; the gauge freedom is $\delta C^0$ (vertex potentials).

### T5 (orthogonal independence of the two channels)

**Statement** $\deg=\beta_1\bmod2$ is determined only by $(V,E,c)$ and does not depend on $s$; $\sigma$ is determined only by $[s]$ and does not depend on the specific values of $(V,E,c)$ (only on the **orbit structure** of the graph and on $[s]$). The two have disjoint arguments, hence take values independently.

**Proof** $\deg$ is a graph-topological function ($\beta_1=E-V+c$); $\sigma$ is a function of the cohomology class. Choosing different $s,s'$ can keep $\deg$ fixed while changing $\sigma$, and choosing different graphs (with $\deg$ changing) can keep the $\sigma$ structure fixed. Hence $Q=\sigma\cdot\deg$ is indeed obtained by multiplying two independent channels. $\blacksquare$

### T6 (even loops force triviality: structural origin of the electron-like type)

**Statement** If $G$ is **bipartite** (no odd cycle) and has **only 1 edge orbit**, then every Aut-invariant assignment is trivial (electron-like).

**Proof** A single orbit $\Rightarrow s$ is a constant $z$ ($\mathbb{F}_2$). Bipartite $\Rightarrow$ every loop $\gamma$ has even length $|\gamma|$. Hence $\sigma(\gamma)=z^{|\gamma|}=(z)^{even}=+1$, trivial. $\blacksquare$

**Cross-check** (consistent with §10.2 of the charge-emergence paper):
- The electron $Q_3$ (cube graph): bipartite, single edge orbit $\Rightarrow$ **forced trivial** ($[s]=0$);
- The proton $Y_3\ltimes\triangle_3$ (closed state): **non-bipartite** (contains odd cycles), 2 edge orbits $\Rightarrow$ non-trivial allowed.

### T7 (necessity of element coloring)

**Statement** The automorphisms of the molecular setting **must preserve the element labels** (color-preserving Aut). Using color-non-preserving Aut merges edge orbits that should be distinguished, distorting the reachability criterion and **possibly flipping the verdict**.

**Proof (counterexample)** Take the 4-cycle $v_0v_1v_2v_3v_0$ with elements $[O,C,C,O]$ ($v_0{=}O,v_1{=}C,v_2{=}C,v_3{=}O$) and edges $e_1{=}(0,1),e_2{=}(1,2),e_3{=}(2,3),e_4{=}(3,0)$.
- **Color-preserving Aut**: swapping $v_0\leftrightarrow v_3$ and $v_1\leftrightarrow v_2$ preserves the elements. Orbits: $O_1=\{e_1,e_3\}$, $O_2=\{e_2\}$, $O_3=\{e_4\}$ (3 orbits). On the unique loop $\gamma$: $m_{\gamma,O_1}=2\equiv0$, $m_{\gamma,O_2}=1$, $m_{\gamma,O_3}=1$, so $M\neq0$ $\Rightarrow$ **non-trivial reachable**.
- **Color-non-preserving Aut**: $D_4$ is **transitive** on the 4 edges (1 orbit). The loop $\gamma$ has even length 4, $\sigma=z^{4}=+1$ $\Rightarrow$ **forced trivial**.

The two conventions give **opposite channel verdicts**, so element coloring is a necessary condition for molecular-layer analysis. $\blacksquare$

**Implementation requirement** `automorphisms(adj, colors=elements)` must restrict automorphisms with `node_match` (by element labels); when `elements=None` it degenerates to color-non-preserving and may be used only for abstract-graph experiments.

### T8 (composite and additivity: connecting to A2/A3)

**Statement** For a composite $K_{\text{comp}}$ formed by the coherent merging of $n$ knots: $\sigma_{\text{comp}}=\prod_i\sigma_i$ ($\mathbb{F}_2$ addition), $\deg_{\text{comp}}=\beta_1(K_{\text{comp}})\bmod2$, $Q_{\text{comp}}=\sigma_{\text{comp}}\deg_{\text{comp}}$.

**Proof** The composite recomputes a new boundary (A2); the boundary is the symmetric difference of the individual $\partial K_i$; by the linearity of T0, $\sigma$ adds along the symmetric difference $\Rightarrow$ polarity multiplication (Lemma 2.1). $\deg$ is recomputed on the new $(V,E,c)$. Separable additivity (A3) follows from summing $Q$ over independent components. $\blacksquare$

---

## 6 Connection with the upstream charge-emergence paper (faithful reproduction of the official skeletons)

Operator 19 uses `skel_electron_q3 / skel_y3_closed / skel_y3_open` to faithfully reproduce the three skeleton classes of §10.2 of the charge-emergence paper, as the specification's **anchor self-test**:

| Skeleton | $V$ | $E$ | $\beta_1$ | $\deg$ | $\lvert\operatorname{Aut}\rvert$ | Edge orbits | Bipartite | Non-trivial reachable | Channel type |
|---|---|---|---|---|---|---|---|---|---|
| Electron $e^-$ ($Q_3$) | 8 | 12 | 5 | 1 | 48 | 1 | Yes | **No** | electron-like |
| Proton $p$ (closed state) | 12 | 18 | 7 | 1 | 36 | 2 | No | **Yes** | nucleon-like |
| Neutron $n$ (open state) | 12 | 17 | 6 | 0 | 4 | 7 | No | **Yes** | nucleon-like |

Conclusion: **the electron is forced by the skeleton symmetry into the trivial holonomy class, while the proton lands in the non-trivial class**, which together with A0 gives the structural origin of the opposite signs of electron/proton. The neutron has $\deg=0$, so regardless of $\sigma$ we get $Q_{\text{model}}=0$ — **the magnitude channel alone makes the neutron neutral**.

---

## 7 Algorithm and complexity

| Step | Input | Output | Complexity |
|---|---|---|---|
| 1 Bond graph | $A_s$ | Boolean adjacency $\mathrm{adj}$ | $\mathcal{O}(n^2)$ |
| 2 Graph invariants | $\mathrm{adj}$ | $V,E,c,\beta_1,\deg,\text{bipartite}$ | $\mathcal{O}(n^2)$ |
| 3 Fundamental cycle basis | $\mathrm{adj}$ | $\{\gamma_i\}_{i\le\beta_1}$ | $\mathcal{O}(n^2+E\cdot L)$ |
| 4 Loop holonomy | $\{\gamma_i\},s$ | $\sigma$-vector, trivial | $\mathcal{O}(\sum_i|\gamma_i|)$ |
| 5 Automorphisms (optional) | $\mathrm{adj},\text{colors}$ | Orbits of $E$ | Guarded by `aut_cap`/`aut_max_v` (default $V\le22$, otherwise skipped) |
| 6 Reachability (optional) | $\{\gamma_i\},\{\text{orbits}\}$ | $M$, non-trivial reachable, witness | $\mathcal{O}(\beta_1\cdot k)$ |

**Total complexity**: $\mathcal{O}(n^2 + \beta_1\cdot\bar L)$ (excluding automorphism enumeration); automorphism enumeration is the bottleneck, so a guard `aut_max_v=22` is imposed, beyond which only reachability is skipped and **this does not affect** the $\sigma$ class test or $Q_{\text{model}}$.

---

## 8 Verification protocol

The companion verification program `verify_operator_19.py` implements the following assertions one by one; running all of them and passing empirically confirms all theorems of this specification.

### 8.1 Verification program ↔ theorem mapping table

| Verification item | Corresponding theorem | System | Assertion |
|---|---|---|---|
| **V1** Skeleton faithfulness | §6 / charge emergence §10.2 | $Q_3$, $Y_3$ closed, $Y_3$ open | $V,E,\beta_1,\deg,\lvert\operatorname{Aut}\rvert$, edge orbits, bipartite, non-trivial reachable all agree item by item |
| **V2** Vertex-potential triviality | T1, T1.1 | 40 random graphs + $Q_3$ | The holonomy of the spin polarity $s_e=s_is_j$ is always $+1$ |
| **V3** Reachability criterion | T2, T2.1 | 30 random small graphs | Linear criterion $=$ $2^{k}$ brute-force enumeration; the trivial class is always reachable |
| **V4** Cycle-basis independence | T3 | Random graphs (two spanning-forest roots) | The triviality test agrees with $\sigma_{\text{canonical}}$ |
| **V5** Coboundary gauge invariance | T4, T4.1 | Random graphs + random vertex potentials | $\sigma'(\gamma)=\sigma(\gamma)$ holds for all loops |
| **V6** $\deg$ channel | D7, T5 | Skeletons + random graphs | $\deg=\beta_1\bmod2$ |
| **V7** Charge-functional consistency | D8, T5 | Skeletons + molecules | $Q_{\text{model}}=\sigma_{\text{canonical}}\cdot\deg$ and $\in\{-1,0,1\}$ |
| **V8** Necessity of element coloring | T7 | Counterexample 4-cycle $[O,C,C,O]$ | Color-preserving verdict "non-trivial", color-non-preserving verdict "trivial" (verdict flip) |
| **V9** End-to-end entry | §1.2, §6 | Ethanol (tree), benzene (even ring), cyclopentane (odd ring) | Tree/even ring $\to$ electron-like; odd ring + multiple orbits $\to$ nucleon-like |
| **V10** Idempotence and freezing contract | D5, §6 | Fingerprint key + `attach` guard | `charge_channel_keys` agrees key by key over two calls; a fingerprint already containing `z2_deg` is not counted again on re-attach |
| **V11** Graph-invariant self-consistency | §7 | Skeletons + random graphs | $\beta_1=E-V+c$; `has_odd_cycle` is complementary to bipartite |
| **V12** Molecular-layer criterion | T6, T7 | 6 molecular bond graphs | The even-ring family is electron-like; the odd-ring family is nucleon-like |

### 8.2 Running

```
python verify_operator_19.py
```

Zero external dependencies (only numpy + networkx, with networkx used only for automorphism enumeration); any failing assertion ends with exit code 1.

---

## 9 Boundary with the existing operators (1–18) (non-overlap statement)

Operator 19 has been checked one by one against all 18 operators of `SRE-math_C.md` and has **no overlap**:

| Neighboring operator | Its duty | Boundary with Operator 19 |
|---|---|---|
| **Operator 12** (topological closed-loop audit) | Outputs $n_{\text{loops}}=\beta_1$ and the Möbius phase ratio $t_{2k}/(2t_k)$ (a **spectral heuristic**) | 12 gives the **counting of loops** (magnitude); 19 gives the **cohomology class of the edge-polarity cochain** $\sigma$ (sign). The mobius_ratio of 12 has **no loops, no edge polarity, and no class**, and is **not** a strict $\mathbb{Z}_2$ holonomy; 19 is its rigorous form |
| **Operator 14** (equation-residual Hodge routing) | Decomposes the residual 1-chain into $\mathrm{im}\,\partial_1\oplus\mathcal{H}_1\oplus\mathrm{im}\,\partial_2^{T}$ | 14 performs an orthogonal decomposition on the **1-chain space** $C_1$; 19 takes a cohomology class on the **1-cochain space** $C^1$. The two are Hodge-dual to each other: the dual of the gradient component $\mathrm{im}\,\partial_1$ of 14 is precisely the **coboundary** trivial class of T1 |
| **Operator 7** ($B_{co}$ loop-current hedging) | Dynamics: leapfrog hedging of the loop-current $B$ field | 7 is **dynamics** (loop-current update); 19 is a **static invariant** (classification for a given $s$) |
| **Operators 9 / 17** (Betti audit / termination verdict) | Change or audit the **topology** $\beta_1$ | 9/17 change or audit the magnitude channel; 19 gives the sign channel on a **fixed topology** |
| **Operator 18** (homological realization) | Step 5 assigns spins via the Fiedler sign gate $\Gamma(k,j)=\operatorname{sgn}(v_2(j))$ | The spin assignment of 18 is of **vertex-potential type**, and by **T1** its holonomy is always trivial; 19 proves that "the assignment of 18 cannot produce a non-trivial sign channel", forming the handshake boundary |
| **Operator 11** (spin-charge adjacency) | Outputs the diagnostics $s_i,\sigma_{ij},d_{ij}$ | The $\sigma_{ij}=s_is_j$ of 11 is **exactly** a trivial-class example of T1; 19 positions it as "incapable of producing a sign" |

**Layer positioning**: after the open-source foundational layer (1–6), the open-source core layer (7–10), the electronic-degrees-of-freedom extension layer (11–12), and the spectral-equation-solving layer (13–18), it forms the **fifth layer — the charge-sign / $\mathbb{Z}_2$ holonomy channel layer (19)**.

---

## 10 Honest boundaries and domain of applicability

1. **Model-internal construction, not a physical assertion**. All conclusions of this specification are **internally self-consistent constructions** of the SRE model; $Q_{\text{model}}$ is a **model-internal charge grade** ($\in\{-1,0,+1\}$) and does not constitute a physical assertion about the actual charge values of real molecules/particles.
2. **Aut-invariance is an explicit assumption**. The reachability conclusions (T2, T6) rely on the **explicit assumption** of §13.2 of the charge-emergence paper that "the edge polarity is invariant under automorphisms". **Without this assumption**, any graph containing loops admits non-trivial classes (1 bit of freedom, dimension $=\beta_1$), and the reachability analysis degenerates into a trivial fact.
3. **Necessary condition for non-trivial reachability**. Only when the graph contains an **odd cycle** and the number of edge orbits is $\ge2$ (more precisely: $M\neq0$) is a non-trivial class reachable — a direct consequence of "even-cycle families are forced trivial by even length" (T6).
4. **The molecular layer requires element coloring**. The Aut of the molecular bond graph must be colored by element labels (T7), otherwise different elements such as C and H may be conflated and the orbit structure distorted.
5. **Scale guard**. Automorphism enumeration imposes the guard `aut_max_v=22`; for oversized graphs only the reachability analysis is skipped, while the $\sigma$ class test and $Q_{\text{model}}$ remain valid.
6. **Semantics of $A_s$**. 19 reuses the $A_s$ output by Operators 1/4, whose bond-graph support $A_s>0$ has semantics guaranteed upstream (the cooperative edges $E^+$ of SRE Axiom 1); if the upstream $A_s$ contains numerical noise, use the $\epsilon$ test of `bond_graph_from_As(eps)`.

---

## 11 Conclusion

Operator 19 implements and establishes the $\sigma$ **sign channel** of the charge-emergence paper on its own:

- **Well-defined** (T0): on the 1-complex, $\sigma$ is an $\mathbb{F}_2$-linear functional on $H_1$, with no representative ambiguity;
- **Non-forgeability of the sign** (T1/T1.1): vertex-potential-type polarities (including the spin polarity of Operator 11 and the sign assignment of Operator 18) always have trivial holonomy — the charge sign cannot be produced by local spin relabeling;
- **Closed criterion for reachability** (T2/T2.1): non-trivial reachable $\iff M\neq0$, $\mathcal{O}(\beta_1 k)$, no $2^k$ enumeration;
- **Gauge invariance** (T3/T4): the triviality test is independent of the cycle basis, and $\sigma$ is immune to vertex-potential relabeling, depending only on $[s]\in H^1$;
- **Two-channel separation** (T5): the sign $\sigma$ and the magnitude $\deg$ are orthogonal, $Q=\sigma\deg$;
- **Structural origin of the electron-like/nucleon-like types** (T6): even loops + a single orbit force triviality (electron), while odd loops + multiple orbits allow non-triviality (proton);
- **Necessary component of the molecular layer** (T7): element-colored Aut, otherwise the verdict flips.

And it shares the same graph ($A_s$) with the upstream electronic operator, outputting `z2_*` scalar keys that feed the compound-screening pipeline, realizing high-speed sign-channel computation at the atomic/electronic level.

---

## Appendix A: Symbols and notation

| Symbol | Meaning |
|---|---|
| $G=(V,E)$ | Bond graph (1-dimensional chain complex), with $V$ vertices and $E$ edges |
| $c$ | Number of connected components |
| $\beta_1=E-V+c$ | First Betti number $=\dim H_1$ |
| $s_e\in\{+1,-1\}$ | Edge polarity (1-cochain) |
| $z_e=\varphi(s_e)\in\mathbb{F}_2$ | Booleannization of polarity |
| $\sigma(\gamma)=\prod_{e\in\gamma}s_e$ | Loop holonomy |
| $[s]\in H^1(G;\mathbb{F}_2)$ | Cohomology class of $\sigma$ |
| $\delta C^0$ | Coboundary (vertex-potential-type cochain) |
| $O_o$ | Edge orbit under the Aut action |
| $m_{i,o}$ | Number of edges of orbit $o$ on fundamental cycle $i$ mod 2 |
| $M=(m_{i,o})$ | Reachability matrix, non-trivial reachable $\iff M\neq0$ |
| $\deg=\beta_1\bmod2$ | Magnitude channel |
| $Q_{\text{model}}=\sigma_{\text{canonical}}\cdot\deg$ | Model-internal charge grade |