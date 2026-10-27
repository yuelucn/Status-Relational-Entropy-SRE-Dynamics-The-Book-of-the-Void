# Operator 20: Activation / Bridge Operator $\mathcal{K}_{\text{act}}$
## Rigorous Mathematical Specification (v0.3)

**Version**: 0.3 (October 2026 · SRE Operator System No. 20, first entry into the project formal documentation sequence)
**Reference Implementation**: `sre_activation_operator.py` (public entry `operator_20_activation_index`; dual versions v0/v1; supports explicit orientation $\varsigma_e$; contains `self_test` 19/19 PASS)
**Companion Verification Program**: `verify_operator_20.py` (independent strict verification, V1–V14, **41/41 PASS**; depends only on numpy; V11 cross-check against Operator 19 requires networkx, auto-SKIPs when missing)
**Freeze Contract**: `activation_keys(res)` must always return exactly **7 keys** (`act_kappa`, `act_rho_path`, `act_nu_path`, `act_mu`, `act_rho_tot`, `act_nu_tot`, `act_gamma_star`); no future implementation may change this key count — downstream fingerprint/report pipelines consume 7 keys.
**Upstream Dependencies**: Operator 1/4 ($A_s$ bond graph), Operator 11/12 (electronic degrees of freedom and cycle count), Operator 13 ($\mathcal{E}_{\text{mom}}$ moment encoding), Operator 14 ($\mathcal{R}_{\text{hodge}}$ homological routing), Operator 15 ($\mathcal{N}_{\text{endo}}$ quasi-Newton inversion), Operator 16 ($\mathcal{C}_{\text{hankel}}$ feasibility clamp), Operator 17 ($\mathcal{A}_{\text{sol}}$ branch audit), Operator 19 ($\mathbb{Z}_2$ sign channel)
**Numbering Note**: Numbered **20** following No. 19; pairwise verified against the 18 existing operators plus No. 19 in `SRE-math_C.md` with no overlap (boundaries in §9).

> **v0.2 five structural revisions relative to v0.1**
> 1. **D1 introduces external boundary graph** $B=(V_B,E_B)$ and interface edges $E_I\subseteq V\times V_B$ — correcting v0.1's $C\subseteq V$ (catalyst cannot be a skeleton subset, otherwise no new cycles can be created).
> 2. **D1 introduces adsorption waypoint** $w_{\text{ads}}$ — correcting v0.1's endpoint-only setup which made $\varrho$ independent of catalyst.
> 3. **New vertex channel** $\delta_v$ (hydrogen coverage) — H still does not create nodes, but coverage change becomes an independent channel; C–H steps are no longer invisible.
> 4. **$\rho$ renamed $\varrho$** — to avoid conflict with Spearman correlation coefficient $\rho_S$.
> 5. **A20 changed to Pareto axiom**; new **T20.3 (endpoint invariance)**, upgrading "interface edges cannot change endpoint homology class" from a defect to a theorem.

> **v0.3 three corrections relative to v0.2 (all discovered during implementation and verification)**
> 1. **D7 / §2.3 definition of $\gamma$ was self-contradictory and rewritten.** v0.2 took "largest connected component", which by definition is connected ⇒ $\lambda_2>0$ ⇒ the P20.5 equivalence is always true, V7 is never observable. v0.3 changes it to **union of components containing active sites** $X$ (definition in D7).
> 2. **D2 missing orientation specification.** Bond-order changes are **undirected** data, while $C^1$ coordinates carry orientation; v0.2 did not specify how the two are assigned, causing $\varrho$ to depend on vertex labeling (measured: 6-ring uniform $+0.5$ gives $2/3$ vs $1/3$). v0.3 formalises $\delta$ as a **directed cochain along a reference orientation**, and adds optional explicit orientation $\varsigma_e$ (**already wired into the implementation**); labeling dependency is now a declared boundary R11.
> 3. **T20.4 statement was false and corrected.** v0.2 wrote "$\nu(\delta_v+c\mathbf1)=\nu(\delta_v)$", but $\nu$'s denominator is $\|\delta_v\|$ and translation changes the denominator. The correct invariances are: **invariant under global translation of all waypoint coverages** ($\delta_v$ depends only on differences) and **invariant under nonzero scaling of $\delta_v$**.

> **Status Declaration**: T20.1–T20.4, P20.5, P20.6 have complete proofs; **H20.1 (central hypothesis) and C20.7 (volcano conjecture) are explicitly marked unproven** — they must be tested by V12/V6 before being promoted.

---

## Abstract

In the current SRE system, a "reaction" is **not an object**: Operator 19 handles the $\mathbb{Z}_2$ sign channel of static graphs, Operators 13–18 handle spectral equations, and neither can answer "why catalysts are needed".

Operator 20 formalises reactions as **piecewise paths** and gives three mutually independent channels:

| Channel | Mathematical Quantity | Encodes | Algebraic Belonging | Catalyst Can Affect? |
|---|---|---|---|---|
| **Edge topological frustration** $\varrho$ | $\lVert \delta_{e,\text{harm}}\rVert /\lVert \delta_e\rVert$ | The non-eliminable portion of bond-order rearrangement around cycles | $H^1(G;\mathbb{R})$ | **Only path value** $\varrho_{\text{path}}$ (see T20.3) |
| **Vertex contrast** $\nu$ | $\lVert \delta_v^{\perp}\rVert /\lVert \delta_v\rVert$ | **Redistribution** of hydrogen coverage across sites | $C^0(G;\mathbb{R})$ | Yes (through waypoints) |
| **Rigidity bottleneck** $\kappa$ | $\int dt/(\gamma+\varepsilon)$ | Spectral-gap collapse along the path | Endogenous spectral-gap ratio $\gamma=\lambda_2/\alpha_n$ | Yes (through interface edges) |

Core conclusions:

| No. | Proposition | Meaning | Status |
|---|---|---|---|
| **T20.1** | $\delta_e$ is exact $\iff$ all cycles $\mathrm{Hol}_\mathbb{R}=0$ $\iff\delta_{e,\text{harm}}=0$ | $\varrho$ is well-defined | **Proven** |
| **T20.2** | $\gamma\in(0,1]$, $\kappa\ge\frac{1}{1+\varepsilon}$, invariant under global scaling | $\kappa$ is dimensionless and comparable across systems | **Proven** |
| **T20.3** | Interface edges **cannot** change endpoint homology class: $\varrho_{\text{tot}}$ is independent of catalyst | Only $\varrho_{\text{path}}$ can be used for catalyst ranking | **Proven (new in this section)** |
| **T20.4** | $\delta_v=\mu\mathbf1+\delta_v^{\perp}$ orthogonal decomposition; $\nu$ invariant under **global translation of all coverages** and under nonzero scaling of $\delta_v$ | Norm-gauge invariance of vertex channel | **Proven (v0.3 corrected)** |
| **P20.5** | $g(t^\ast)=0\iff$ zero-weight edges contain a cut on $X$ (where $X$ = union of components containing active sites) | Operational criterion for transition states | **Proven (v0.3 restated)** |
| **P20.6** | Adding edges makes $\lambda_2,\alpha_n$ both non-decreasing, so $\gamma$ is **not monotone** | Forbids "adding edges always lowers $\kappa$" | **Proven** |
| **H20.1** | $(\kappa,\varrho_{\text{path}},\nu_{\text{path}})$ rank-correlate with DFT barrier $\lvert \rho_S\rvert \ge0.7$ | **Operator 20's reason for existing** | **Unproven** |
| **C20.7** | $\kappa(w_I)$ is U-shaped over interface weights | SRE-version of Sabatier volcano curve | **Unproven (conjecture)** |

---

## 1 Problem Statement

### 1.1 The Gap

SRE's graph ontology only has "configurations", not "reactions". Consequently:

1. Cannot formulate a catalyst's role (no counterpiece to "lowering the barrier");
2. Cannot formulate transition states (no energy);
3. Cannot rank same-topology metals (Operator 19 is identical at every site for Pt/Pd/Rh/Ni/Cu).

### 1.2 Task of This Document

Introduce four objects — **reaction paths**, **external catalyst boundary**, **adsorption waypoints**, and **vertex channel for hydrogen coverage** — to define Operator 20:

- **Input**: heavy-atom skeleton $G$, path waypoints $\{(w_j,n_j)\}$, external boundary graph $B$, interface edges $E_I$ with weights $w_I$;
- **Output**: $\mathcal{K}_{\text{act}}=(\kappa,\varrho_{\text{path}},\nu_{\text{path}},\mu;\ \text{diagnostics})$, all dimensionless except $\mu$ (which is hydrogen change per site);
- **Properties**: T20.1–T20.4, P20.5–P20.6, plus **falsification protocols** for H20.1/C20.7.

### 1.3 Applicable Scope (Hard Boundaries)

- Only reactions where **heavy-atom skeleton is conserved**: hydrogenation/dehydrogenation, bond-order rearrangement, isomerisation, aromatisation;
- **H does not create nodes**; encoded as vertex coverage $n_H\in\mathbb{Z}_{\ge0}^{V}$; C–H bond energy is not in the model, only coverage change enters the vertex channel;
- **C–C cleavage / skeleton rearrangement** changes $V$, outside v0.3;
- Only **single elementary steps** or two-step "adsorption + reaction" paths; the 9 H₂ molecules of DBT require 9 invocations.

---

## 2 Mathematical Preliminaries

### 2.1 Cochain Complex and Hodge Decomposition

For skeleton $G=(V,E)$ with $\lvert V\rvert =n$, $\lvert E\rvert =m$. SRE has no 2-cells, so

$$C^0\xrightarrow{\ \delta_0\ }C^1\xrightarrow{\ \delta_1=0\ }C^2=0,\qquad H^1(G;\mathbb{R})=C^1/\,\mathrm{im}\,\delta_0 .$$

Take the **standard Euclidean inner product** (default; weighted inner product see §10 R3), giving orthogonal decomposition

$$C^1=\underbrace{\mathrm{im}\,\delta_0}_{\text{exact (gradient)}}\ \oplus\ \underbrace{\mathcal{H}^1}_{\text{harmonic}},\qquad \dim\mathcal{H}^1=\beta_1(G)=E-V+c .$$

**Note**: With no 2-cells the curl component is zero; if upstream graphs are filled complexes (containing 2-cells), the three-component decomposition must be used — this specification does not cover that case (§10 R4).

### 2.2 Edge Orientation (added in v0.2)

For each undirected edge $e=\{i,j\}$ ($i<j$), fix the reference orientation $i\to j$. A cycle $\gamma$ traversing in the same direction as the reference takes $+$, opposite takes $-$:

$$\varepsilon_{e,\gamma}=\begin{cases}+1,& \gamma\ \text{traverses along}\ i\to j\\-1,& \text{reversed}\end{cases},\qquad \mathrm{Hol}_\mathbb{R}(\delta,\gamma)=\sum_{e\in\gamma}\varepsilon_{e,\gamma}\,\delta_e .$$

**Specification Clause (added in v0.3, mandatory to read)** $\varepsilon_{e,\gamma}$ is the sign of **cycle traversal** relative to the reference orientation — a different matter from the §2.2 reference orientation itself. The reference orientation is fixed by an **assignment convention**:

$$\boxed{\ \text{Reference orientation of edge }e=\{i,j\}=i\to j\ (i<j)\ \text{ (by vertex numbering)}\ }$$

Therefore, **$\delta\in C^1(G;\mathbb{R})$ is a directed cochain "along the reference orientation"**: $\delta_e$ is the increment in the $i\to j$ direction, not an undirected scalar.

**Resulting labeling dependency (important, see §10 R11)** Bond orders (and their changes) are **undirected** chemical data, while $C^1$ coordinates carry orientation; mapping undirected data into directed coordinates requires one assignment, and different assignments give different Hodge decompositions. **Therefore $\varrho$ depends on vertex labeling**: the same physical reaction (6-ring uniform bond-order $+0.5$, i.e. benzene aromatisation) gives $\varrho=2/3$ under labeling $[0,1,2,3,4,5]$ and $\varrho=1/3$ after swapping $1\leftrightarrow2$ (measured in V3).

**Optional explicit orientation $\varsigma_e$ (added input in v0.3)** If the user wants to read the chemical intuition (e.g. to have "uniform bond-order increase around a ring" read as a pure cycle channel), they may additionally provide $\varsigma_e\in\{+1,-1\}$; the specification automatically replaces $\delta_e$ with $\varsigma_e\delta_e$ before decomposition. **Default $\varsigma_e\equiv+1$** (i.e. bit-wise identical to v0.2). $\varsigma$ is a different symbol from $\varepsilon_{e,\gamma}$ and from the D7 regular $\varepsilon$.

**Implementation Status (wired in v0.3)** `build_reaction(..., orient=ς)` accepts a scalar, length-$\lvert E\rvert$ vector, or `{(i,j):±1}` dictionary; non-$\pm1$ values raise error; $\varsigma_e$ **only acts on the edge channel** ($\varrho$), **does not affect** $\kappa$ (uses $W$, no orientation) or $\nu,\mu$ (vertex channel, no orientation). Public helper `orient_from_cycle(n, edges, cycle)`: takes $\varsigma_e=\varepsilon_{e,\gamma}$, turning the chemical intuition of "entire ring synchronously increasing/decreasing bond order" into a specification orientation.

Measured (6-ring uniform $+0.5$, i.e. benzene aromatisation, with both default and natural-cycle traversal):

| $\varsigma_e$ | $\varrho_{\text{tot}}$ | Reading |
|---|---|---|
| $\equiv+1$ (default, $i<j$ reference orientation) | $2/3$ | Mixed (contains gradient component) |
| $[+1,+1,+1,+1,+1,-1]$ (natural-cycle traversal) | $1$ | Pure cycle channel (chemical intuition) |
| $-\varsigma$ (globally flipped) | Same as $\varsigma$ | Both $\delta$ and gradient component flip sign |

V3 assertions: default reproduces $2/3$, natural-cycle orientation gives $1$, global flip unchanged, does not affect $\kappa$, dictionary form and vector form equivalent, invalid values rejected, and **T20.3 still holds under arbitrary $\varsigma_e$**.

### 2.3 Spectral Shape and Endogenous Spectral-Gap Ratio

Weighted adjacency $W\ge0$, $L(W)=\mathrm{diag}(W\mathbf1)-W$. Spectral shape is encoded by Chebyshev moments $\boldsymbol\tau(W)=(\tau_0,\dots,\tau_K)$ (Operator 13). Define

$$\boxed{\ \gamma(W)=\frac{\lambda_2(L(W))}{\alpha_n(L(W))}\in(0,1]\ }$$

$\alpha_n=\lambda_n$ is the spectral radius. The **domain of computation** of $\gamma$ is defined by D7 (rewritten in v0.3: union of components containing active sites $X$, not "largest connected component").

---

## 3 Definitions

### D1 (Reaction, rewritten in v0.2)

$$\mathcal{R}=\Big(G,\ \{(w_j,n_j)\}_{j=0}^{m},\ B,\ E_I,\ w_I\Big).$$

- $G=(V,E)$: heavy-atom skeleton, $E=E_R\cup E_P$ (bond-forming/breaking represented by zero weight);
- $w_j\in[0,3]^{E}$: bond orders at waypoint $j$ ($w_0=w_R$, $w_m=w_P$); upper bound 3 = triple bond;
- $n_j\in\mathbb{Z}_{\ge0}^{V}$: hydrogen coverage at waypoint $j$;
- $B=(V_B,E_B)$: **external** catalyst boundary graph ($V_B\cap V=\varnothing$);
- $E_I\subseteq V\times V_B$: interface edges; $w_I\in\mathbb{R}_{\ge0}^{E_I}$;
- $\bar E=E\cup E_B\cup E_I$.

**Two types of path**:
- **Direct path**: $m=1$, $(w_R,n_R)\to(w_P,n_P)$;
- **Catalytic path**: $m=2$, $(w_R,n_R)\to(w_{\text{ads}},n_{\text{ads}})\to(w_P,n_P)$.

### D2 (Piecewise Displacement)

For segment $j$ ($t\in[t_{j-1},t_j]$):
$$\delta_e^{(j)}=w_j-w_{j-1}\in C^1(G;\mathbb{R}),\qquad \delta_{v}^{(j)}=n_j-n_{j-1}\in C^0(G;\mathbb{R}).$$

**Endpoint displacement** (path-independent):
$$\delta_{e,\text{tot}}=w_P-w_R,\qquad \delta_{v,\text{tot}}=n_P-n_R .$$

**Convention**: $\delta_e$ takes nonzero values only on $G$; interface edges **do not enter** $\delta_e$ (interface edges affect only $\kappa$, see D7). This differs from v0.1's writing $w_C$ on $E_C$, fixing semantic inconsistency (v0.1's P0-4).

**Orientation (added in v0.3)**: $w_j,n_j$ are **undirected** chemical quantities; $\delta_e\in C^1$ is a **directed cochain**. Assignment per §2.2 specification clause: fixed $i<j$ reference orientation, or explicit $\varsigma_e$ given by user. Consequently $\varrho$ depends on vertex labeling (boundary R11), and **labeling convention must be declared in every report**.

### D3 ($\mathbb{R}$-Valued Holonomy)

Per §2.2 orientation convention:
$$\mathrm{Hol}_\mathbb{R}(\delta_e,\gamma)=\sum_{e\in\gamma}\varepsilon_{e,\gamma}\,\delta_{e}.$$

### D4 (Edge Channel $\varrho$)

Decompose $\delta_e=\delta_{e,\text{grad}}+\delta_{e,\text{harm}}$ on $G$ (where $\delta_e$ is the directed cochain from §2.2), define

$$\varrho_{\text{tot}}=\frac{\|\delta_{e,\text{tot,harm}}\|}{\|\delta_{e,\text{tot}}\|}\in[0,1],\qquad
\varrho_{\text{path}}=\sum_{j=1}^{m}\ell_j\,\frac{\|\delta_{e,\text{harm}}^{(j)}\|}{\|\delta_{e}^{(j)}\|},$$

where $\ell_j=t_j-t_{j-1}$ is segment length, $\sum\ell_j=1$; if a segment has $\|\delta_e^{(j)}\|=0$, that segment contributes $0$. Convention: $\|\delta_{e,\text{tot}}\|=0$ gives $\varrho_{\text{tot}}=0$.

**Semantics**: $\varrho_{\text{tot}}$ is the topological frustration of the **reaction** (endpoint-determined); $\varrho_{\text{path}}$ is the topological frustration of the **mechanism** (path-determined).

### D5 (Vertex Channel $\mu,\nu$, added in v0.2)

Orthogonal decomposition of $\delta_v\in C^0(G;\mathbb{R})$
$$\delta_v=\mu\mathbf1+\delta_v^{\perp},\qquad \mu=\frac1n\sum_i\delta_{v,i},\qquad \mathbf1^\top\delta_v^{\perp}=0 .$$
Define
$$\nu_{\text{tot}}=\frac{\|\delta_{v,\text{tot}}^{\perp}\|}{\|\delta_{v,\text{tot}}\|}\in[0,1],\qquad
\nu_{\text{path}}=\sum_{j=1}^{m}\ell_j\,\frac{\|\delta_{v}^{(j),\perp}\|}{\|\delta_{v}^{(j)}\|},$$
with $\|\delta_v\|=0$ giving the corresponding quantity $0$.

**Semantics**:
- $\mu$ = net hydrogen change per site (with sign; DBT dehydrogenation is negative);
- $\nu$ = contrast of hydrogen coverage (proportion of redistribution across sites), insensitive to "how many H overall", only to "how H is distributed".

### D6 (Spectral-Shape Path and Constraint Inversion)

Linear path in moment space for each segment
$$\boldsymbol\tau(t)=(1-s)\boldsymbol\tau(w_{j-1})+s\,\boldsymbol\tau(w_j),\qquad s\in[0,1],$$
solve sequentially by $s$ (warm start + step-size constraint):
$$w(t)=\arg\min_{w\in[0,3]^E}\ \|\boldsymbol\tau(w)-\boldsymbol\tau(t)\|^2+\lambda\|w-w_0(t)\|^2,\qquad \|w(s)-w(s-\Delta s)\|\le s_{\max}.$$

**Note** (P1-3): Linear interpolation of moments is always feasible on the **measure level** (convexity of spectral measures), but **graph realisation** is not necessarily feasible; the latter is judged by Operator 16's Hankel clamp and Operator 17's branch audit.

### D7 (Rigidity Bottleneck $\kappa$, computation domain rewritten in v0.3)

**Computation domain $X$ (v0.3 core correction)** v0.2 took "largest connected component containing active sites", which is self-contradictory: by definition that component is connected ⇒ $\lambda_2>0$ ⇒ P20.5's equivalence is always true and $\gamma\to0$ is never observable. v0.3 changes it to **union of components containing active sites**:

$$\boxed{\ X=V\ \cup\ \big\{b\in V_B\ :\ \exists\,(a,b)\in E_I,\ w_I(a,b)>0\big\}\ }$$

i.e.: **all skeleton vertices count as active**, plus "boundary vertices connected to the skeleton by positive-weight interface edges". Isolated boundary vertices are automatically excluded; when $w_I=0$, $X=V$. Define $L|_X$ as the Laplacian of the weighted graph $W|_X$ induced on $X$ by

$$W|_X:\quad \text{skeleton edges take }w(t),\quad \text{boundary edges take }w_B,\quad \text{interface edges take }w_I .$$

Then

$$g(t)\equiv\frac{\lambda_2\big(L\lvert _X(w(t))\big)}{\lambda_n\big(L\rvert _X(w(t))\big)},\qquad \gamma_\ast=\min_{t}g(t),\qquad \boxed{\ \kappa=\sum_{j=1}^{m}\int_{t_{j-1}}^{t_j}\frac{dt}{g(t)+\varepsilon}\ }\quad(\varepsilon>0).$$

**Conventions**: $\lvert X\rvert \le1$ gives $g=1$; when $g(t)=0$ (the induced graph on $X$ is disconnected) that point contributes $1/\varepsilon$ to the integral (numerically truncated).

**This restores observability in P20.5**: $w_I=0$ and skeleton containing a zero-weight cut ⇒ $g=0$ ⇒ $\kappa\sim1/\varepsilon$; catalyst reconnects both sides of the cut via interface edges ⇒ $\lambda_2>0$ ⇒ $\kappa$ finite. **This is precisely A20's mechanism** (V7/V9 measured: $\kappa$ 26.76 → 6.66).

### D8 (Output and Partial Order)

$$\boxed{\ \mathcal{K}_{\text{act}}(\mathcal{R})=\Big(\kappa,\ \varrho_{\text{path}},\ \nu_{\text{path}},\ \mu;\ \underbrace{\varrho_{\text{tot}},\nu_{\text{tot}},\gamma_\ast,\text{feasible}}_{\text{diagnostics}}\Big)\ }$$

**Pareto partial order**: for two candidates $A,B$ for the same reaction,
$$A\preceq B\iff \kappa_A\le\kappa_B,\ \varrho_{\text{path},A}\le\varrho_{\text{path},B},\ \nu_{\text{path},A}\le\nu_{\text{path},B},$$
with at least one strict inequality. **No scalarisation defined** — weights are external input if needed.

**Control protocol**: direct reference and catalytic candidate use the **same** $\bar E$; direct reference takes $w_I=0$ (zero-weight edges do not change Laplacian), catalytic candidate takes $w_I>0$ and optionally inserts $w_{\text{ads}}$. This makes $\kappa$ comparable.

---

## 4 Positioning Axioms

**A20 (Bridge Axiom, Pareto version)** A catalyst works by **simultaneously improving all three channels along the path under fixed stoichiometry**:

$$\boxed{\ C\ \text{effective}\iff \mathcal{K}_{\text{act}}(C)\preceq \mathcal{K}_{\text{act}}(\text{direct reference}),\quad \mu\ \text{fixed}\ }$$

It is **not** "reduce $\varrho$ to 0" — by T20.3, interface edges cannot change endpoint $\varrho_{\text{tot}}$; what is possible is changing the **path** (via $w_{\text{ads}}$) and lowering $\kappa$.

**H20.2 (Orthogonality Hypothesis, former A20′)** Three channels encode independent barriers; any one being zero does not imply the others are zero. Verified numerically by V4.

---

## 5 Theorems and Proofs

### T20.1 (Exactness Criterion)

Let $G$ be connected, $\delta\in C^1(G;\mathbb{R})$. The following are equivalent:

**(i)** $\delta$ is exact ($\exists\varphi\in C^0$, $\delta_e=\varphi_i-\varphi_j$);
**(ii)** $\mathrm{Hol}_\mathbb{R}(\delta,\gamma)=0$ for all cycles $\gamma$;
**(iii)** $\delta_{\text{harm}}=0$ (i.e. $\varrho=0$).

**Proof**
(i)⇒(ii): $\mathrm{Hol}=\sum_{e\in\gamma}\varepsilon_{e,\gamma}(\varphi_i-\varphi_j)$; each edge is cancelled exactly once in the closed traversal, so sum is $0$.
(ii)⇒(i): Take base point $v_0$, let $\varphi_v=\sum_{e\in P(v_0\to v)}\varepsilon_{e,P}\delta_e$. If $P,P'$ are two paths $v_0\to v$, then $P\cup P'^{-1}$ is a closed chain; when not simple it can be decomposed into a sum of simple cycles, each summing to $0$ by (ii), so $\varphi_v$ is path-independent, thus $\delta_e=\varphi_i-\varphi_j$.
(i)⇔(iii): By the orthogonal decomposition in §2.1. $\square$

**Corollary 20.1.1** $\varrho$ is independent of cycle-basis choice ($\delta_{\text{harm}}$ is the orthogonal projection onto $\mathcal{H}^1$).

### T20.2 (Bounds of $\kappa$ and Scaling Invariance)

For connected $G$ and any $W\ge0$: $\lambda_2\le\lambda_n=\alpha_n$, so $g\in(0,1]$,

$$\kappa\ge\frac{1}{1+\varepsilon},$$

and $L(cW)=cL(W)$ ⇒ $\gamma(cW)=\gamma(W)$, so $\kappa$ is invariant under **global** weight scaling.

**Proof** $\lambda_2\le\lambda_n$ is obvious; connectedness gives $\lambda_2>0$; scaling cancels. $\square$

**Note**: scaling invariance requires both $w$ **and** $w_I$ to scale together; scaling only the interface weights changes $\kappa$ (this is exactly the quantity C20.7 scans).

### T20.3 (Endpoint Invariance, added in v0.2)

Let $\bar E=E\cup E_B\cup E_I$. For arbitrary $E_I$ and $w_I$, the endpoint displacement $\delta_{e,\text{tot}}$ on $E$ is unchanged, and

$$\varrho_{\text{tot}}(\bar E)=\varrho_{\text{tot}}(G).$$

**Proof** The inclusion map $\iota:C^1(G)\to C^1(\bar E)$ extends the 1-cochain on $E$ by $0$ on $E_I$; dually, $H_1(G)\hookrightarrow H_1(\bar E)$ is injective. For any $\gamma\subset G$,
$$\langle[\delta_{\text{tot}}],[\gamma]\rangle_{\bar E}=\sum_{e\in\gamma}\varepsilon_{e,\gamma}\delta_{e,\text{tot}}=\langle[\delta_{\text{tot}}|_G],[\gamma]\rangle_G$$
independent of $E_I$. So $\delta_{\text{tot}}$'s image on $H_1(G)$ is unchanged, and $\varrho_{\text{tot}}$ is unchanged. $\square$

**Significance (critical)**: **Catalysts cannot change the topological frustration of the reaction endpoints**; they can only change the **path** (by inserting $w_{\text{ads}}$) and the **rigidity** (interface edges). This turns v0.1's "axiom unsatisfiable" into a clear division of labour.

### T20.4 (Vertex Decomposition and Gauge Invariance, corrected statement in v0.3)

$\delta_v=\mu\mathbf1+\delta_v^{\perp}$ is an orthogonal decomposition ($\mathbf1^\top\delta_v^\perp=0$), and $\nu$ satisfies two **correct** invariances:

**(a) Invariant under global translation of all waypoint coverages** If $n_j\mapsto n_j+c\mathbf1$ (with $c$ independent of $j$, i.e. every waypoint at every site adds the same $c$), all $\delta_v^{(j)}$, $\mu$, and $\nu$ are unchanged;
**(b) Invariant under nonzero scaling of $\delta_v$** $\nu(c\,\delta_v)=\nu(\delta_v)$ ($c\neq0$).

**Proof** (a) Translation gives $\delta_v^{(j)}=(n_j+c\mathbf1)-(n_{j-1}+c\mathbf1)=\delta_v^{(j)}$, unchanged term by term. $\square$
(b) $\delta_v=\mu\mathbf1+\delta_v^\perp$ ⇒ $c\delta_v=(c\mu)\mathbf1+c\delta_v^\perp$ ($\mathbf1^\top(c\delta_v^\perp)=c\cdot0=0$, still orthogonal decomposition), so
$$\nu(c\delta_v)=\frac{\|c\delta_v^\perp\|}{\|c\delta_v\|}=\frac{\lvert c\rvert \,\|\delta_v^\perp\|}{\lvert c\rvert \,\|\delta_v\|}=\nu(\delta_v).\ \square$$

> **False statement from v0.2 deleted** v0.2 wrote "for any $c\in\mathbb{R}$, $\nu(\delta_v+c\mathbf1)=\nu(\delta_v)$". This is **false**: $\nu$'s denominator is $\|\delta_v\|$, translation changes numerator (which is unchanged) and denominator (which increases when $c\neq0$), so $\nu$ generally decreases. Numerical counterexample in V13. **This is a substantive v0.2 error**: the orthogonal decomposition itself is correct, but the invariance it implies was incorrectly written on $\delta_v$ (it should be on $n_j$, i.e. (a)).

### P20.5 (Transition-State Criterion, restated in v0.3)

On domain $X$ (union of components containing active sites, per D7),
$$g(t^\ast)=0\iff\lambda_2\big(L|_X(w(t^\ast))\big)=0\iff \text{the zero-weight edge set contains a cut of the induced graph on } X.$$

**Proof** $\lambda_2=0\iff L|_X$ is disconnected (degenerate zero modes) $\iff$ there exists a cut with all-zero weights. Taking $X$ as "skeleton vertices $\cup$ boundary vertices connected by positive-weight interface edges" already excludes two kinds of trivial zero modes: (i) isolated vertices caused by removed H — H does not create nodes, no zero mode; (ii) isolated boundary vertices not connected by positive interface edges — excluded from $X$. $\square$

**Significance**: transition state = spectral degeneracy point of the weighted skeleton; $\kappa$ measures how close the path comes to degeneracy; a catalyst's role is to **route the path around the degeneracy point** (provide a detour). **This was unobservable in v0.2** ("largest connected component" is by definition connected ⇒ always has $\lambda_2>0$ ⇒ right-hand side always false); after rewriting the computation domain in v0.3 this criterion is finally testable (V7).

### P20.6 ($\gamma$ is Not Monotone)

Adding edges $W'=W+\Delta W$ ($\Delta W\ge0$) gives $L'\succeq L$; Weyl's theorem gives component-wise non-decreasing eigenvalues, so $\lambda_2$ and $\alpha_n$ both increase, and $\gamma'=\lambda_2'/\alpha_n'$ has **no fixed size relation** to $\gamma$.

**Proof** $\Delta L=w(e_i-e_j)(e_i-e_j)^{\top}\succeq0$; Weyl monotonicity; ratio is indefinite. $\square$

### C20.7 (Volcano Conjecture, **unproven**)

Under fixed chemical environment, varying only $w_I$, $\kappa(w_I)$ is U-shaped: $w_I\to0$ gives no bridging (high); intermediate $w_I^\ast$ gives minimum; when $w_I$ is too large, interface rigidity dominates (rebounds).

**Status**: Conjecture, tested by V6; if monotone or non-unimodal it is falsified, not affecting T20.1–T20.4.

### H20.1 (Central Hypothesis, **unproven**)

$(\kappa,\varrho_{\text{path}},\nu_{\text{path}})$ rank-correlate with DFT barrier $\Delta^\ddagger$ with $\lvert \rho_S\rvert \ge0.7$, and the sign is consistent within similar reaction families. **If $\lvert \rho_S\rvert <0.5$ or sign flips, Operator 20 is downgraded to a structural descriptor.**

---

## 6 Algorithm Design

### 6.1 v0 (Low-Cost, First Validate H20.1)

```
Input R=(G, waypoints, B, E_I, w_I)
1. For each segment j:
     δe ← w_j − w_{j−1}           (on E)
     δv ← n_j − n_{j−1}           (on V)
     Hodge(δe) on G → δe_harm ;  ϱ_j ← ‖δe_harm‖/‖δe‖
     δv = μ_j 1 + δv⊥ ;          ν_j ← ‖δv⊥‖/‖δv‖
2. ϱ_path ← Σ ℓ_j ϱ_j ;  ν_path ← Σ ℓ_j ν_j ;  μ ← mean(n_P − n_R)
3. for t in linspace per segment:
     w(t) ← (1−s)w_{j−1} + s w_j     (on E; interface edges remain w_I)
     L(t) ← L|_X(w(t)) ;  g(t) ← λ2/λn  (X = union of active-site components, D7)
4. γ* ← min g ;  κ ← Σ_j trapz(1/(g+ε), segment)
Output (κ, ϱ_path, ν_path, μ; ϱ_tot, ν_tot, γ*, feasible)
```

Complexity $O(m\cdot n^3)$ (dense eigendecomposition) or $O(m\cdot \lvert E\lvert \cdot \text{iter})$ (Lanczos).

### 6.2 v1 (Full)

Moment-space interpolation + constraint inversion (D6) + Operator 16/17 feasibility and branch audit. An order of magnitude more expensive, but the path is the canonical representative in spectral-shape space.

### 6.3 Parameters

| Parameter | Meaning | Default | Notes |
|---|---|---|---|
| $K$ | Sample points per segment | 32 | — |
| $\varepsilon$ | Regularisation for $\kappa$ | $10^{-3}$ | **Must report $\kappa$ ordering stability across $\{10^{-1},10^{-2},10^{-3}\}$** (P1-5) |
| $\lambda$ | D6 anchor regularisation | $10^{-2}$ | — |
| $s_{\max}$ | Step-size upper bound | $0.1$ | Guarantees path continuity |
| $w_I$ | Interface weight | **external input** | See §10 R1 |

---

## 7 Complexity

| Version | Main Cost | Order of Magnitude (n≈21 skeleton) |
|---|---|---|
| v0 | Per-segment $K$ extreme eigenvalues | Seconds |
| v1 | Per-segment $K$ inversions × Operator 15 iterations | Minutes |
| Hodge | Sparse least-squares $O(m)$ | Negligible |

---

## 8 Verification Protocol (V1–V14)

| No. | Assertion | Correspondence |
|---|---|---|
| V1 | Oriented $\mathrm{Hol}_\mathbb{R}$ matches hand calculation (including reverse traversal) | D3/§2.2 |
| V2 | T20.1 three-way equivalence holds over $10^3$ random graphs | T20.1 |
| V3 | $\varrho$ independent of spanning-tree / cycle-basis choice; explicitly measure vertex-label dependency of $\varrho$; **$\varsigma_e$ orientation clause** (default $2/3$, natural cycle orientation $1$, global flip unchanged, does not affect $\kappa$, illegal values rejected, T20.3 still holds) | Corollary 20.1.1 + §2.2 + R11 |
| V4 | Three-channel rank correlation $\lvert \rho_S\rvert <0.7$ (orthogonality) | H20.2 |
| V5 | $\kappa$ invariant under global scaling; **not** invariant under scaling only $w_I$ | T20.2 |
| V6 | C20.7 volcano shape (scan $w_I$, judge unimodal/monotone) | C20.7 |
| V7 | Construct zero-weight cut, verify $\gamma\to0$, $\kappa$ monotonically diverges as $\varepsilon$ decreases ($\kappa\sim1/\varepsilon$) | P20.5 |
| V8 | Add-edge counterexamples: $\gamma$ increases and decreases at least one case each | P20.6 |
| V9 | $w_I=0$ catalytic path degenerates to direct-path $\kappa$ | D8 control protocol |
| V10 | v0 vs v1 ranking consistent (Spearman $\ge0.8$) | §6 |
| V11 | Bipartite + single-orbit skeleton; interface grafting still cannot open Operator 19's sign channel | §9 |
| V12 | **DFT benchmark**: 5–8 elementary steps, report $\rho_S$ and ablation | H20.1 |
| V13 | Vertex channel: $\mu=(1/n)\sum\delta_v$, $\delta_v^\perp\perp\mathbf1$, $\nu$ invariant under global translation of coverage and nonzero scaling; pure uniform loading gives $\nu=0$; three analytic examples attached | T20.4/D5 |
| V14 | Endpoint invariance: $\varrho_{\text{tot}}$ unchanged under arbitrary $E_I/w_I$ | T20.3 |

V1–V11, V13–V14 are internal consistency (executable immediately); **V12 is the only external verification deciding H20.1**.

---

## 9 Boundaries with Existing Operators

| Operator | Object | Relation to 20 |
|---|---|---|
| 1/4 | $A_s$ bond graph | **Upstream**: provides $G$ |
| 11 | Spin polarity | Different object: vertex-potential polarities are always trivial (19-T1) |
| 12 | Cycle count, Möbius | Reuses $\beta_1=\dim\mathcal{H}^1$ |
| **13** | Spectral-shape moment $\mathcal{E}_{\text{mom}}$ | **Subroutine**: $\boldsymbol\tau(W)$ (D6) |
| **14** | Equation residual Hodge routing | ⚠ **Nearest neighbour**: 14 decomposes **equation residual** $r$; 20 decomposes **reaction displacement** $\delta$; mechanism is reused, object and output differ |
| **15** | Quasi-Newton spectral inversion | **Subroutine**: D6 |
| **16** | Hankel clamp | **Subroutine**: `feasible` |
| **17** | Solution branch audit | **Subroutine**: branch adjudication |
| **18** | Homology solution implementation | **Analogy**: D6's anchor $w_0$ plays a gauge-fixing role |
| 9/7 | Betti stitching / cohomology locking | Different: acts on equation solvability |
| **19** | $\mathbb{Z}_2$ sign channel | **Orthogonal complement**: 19 is sign ($\mathbb{Z}_2$); 20 is magnitude ($\mathbb{R}$) + vertex + rigidity |

**Compatibility proposition with 19 (to be rigorously proven)** If $G$ is bipartite and has exactly 1 edge orbit, any **bipartite-preserving** interface grafting cannot make 19's $\sigma$ nontrivial; catalyst must interface with "same-color vertices" to create odd cycles and simultaneously open the sign channel (per 19-T6).

---

## 10 Honest Boundaries and Risks

Items below are cited in the main text as **R1–R11**.

1. **$w_I$ is the only free input and cannot be generated endogenously.** A proxy like $\Delta\chi$ would predict Ni stronger than Pt, opposite to DBT measurements. Therefore **Operator 20 can only rank structures under fixed metal**, not rank metals themselves; the latter requires DFT/experimentally calibrated $w_I$. This is also why Operator 19 cannot rank Pt/Pd.
2. **Not a minimum-energy path.** Moment-space linear interpolation is only a canonical representative; $\kappa$ is an indicator, not a barrier upper bound.
3. **Hodge inner-product convention**: default standard Euclidean inner product (no parameters). If weighted edge-weight inner product is used, $\varrho$ changes; convention must be fixed and declared in reports.
4. **2-cell case not covered**: if the upstream graph is a filled complex, the curl component is nonzero and the two-way decomposition in §2.1 fails.
5. **$\varepsilon$ sensitivity of $\kappa$**: near the zero-gap point $\kappa\sim1/\varepsilon$; ordering stability across three $\varepsilon$ values must be reported.
6. **H bond energy is not in the model**: vertex channel encodes only net amount and contrast of coverage, not C–H bond dissociation energy.
7. **0 K, no entropy, no coverage competition, no solvent**: entropy effects at 300 °C and competitive adsorption are outside the system.
8. **$t$ is not time**, $\kappa$ is not rate; $t$ is only a homotopy parameter.
9. **Single elementary step**: 9 H₂ for DBT means 9 invocations, not one.
10. **H20.1 unproven**: Operator 20 currently has only internal consistency, no empirical support.
11. **(R11) $\varrho$ depends on vertex labeling.** Bond-order changes are **undirected** data, while $C^1$ coordinates carry orientation (§2.2 specification clause); mapping undirected data into directed coordinates requires an arbitrary assignment, different assignments giving different Hodge decompositions. Measured: 6-ring uniform bond-order $+0.5$ (benzene aromatisation) gives $\varrho=2/3$ under labeling $[0..5]$, and $\varrho=1/3$ after swapping $1\leftrightarrow2$ (V3). **Consequences and requirements**: (i) The **absolute value** of $\varrho$ is not comparable across papers, only **relative ranking under the same labeling convention** is meaningful; (ii) every report must declare the labeling convention used (default $i<j$ reference orientation, or explicit $\varsigma_e$); (iii) before comparing $\varrho$ across systems, labeling must first be unified (e.g. normalised atom ordering). This is Operator 20's **unresolved** theoretical gap — radical orientation must be induced from reaction data itself, which is a v1.0 todo.

---

## 11 Todo List

**Done**

1. ~~Implement `sre_activation_operator.py` (v0 first, including vertex channel)~~ **[Done]** includes v0/v1 dual versions;
2. ~~Implement `verify_operator_20.py` (V1–V11, V13–V14)~~ **[Done]** 30/30 PASS;
3. ~~Analytic examples: benzene aromatisation ($\varrho>0$), ethane C–C rotation ($\varrho=0$), ethanol dehydrogenation ($\mu<0,\nu>0$)~~ **[Done]** all match.

**v0.3 three specification corrections + one input wiring** (all discovered during implementation/verification, not implementation defects)

4. ~~D7 / §2.3 $\gamma$ computation domain self-contradictory~~ **[Fixed]** rewritten as $X$ (union of components containing active sites); P20.5 restated and restored observability (V7/V9 measured).
5. ~~D2 missing orientation specification, $\varrho$ depends on vertex labeling~~ **[Fixed]** §2.2 adds specification clause (fixed $i<j$ reference orientation, $\delta$ as directed cochain, optional explicit $\varsigma_e$); labeling dependency is no longer hidden, upgraded to boundary **R11**.
6. ~~T20.4 statement is false~~ **[Fixed]** original $\nu(\delta_v+c\mathbf1)=\nu(\delta_v)$ is false; corrected to proper form (coverage global translation + nonzero scaling invariance), with numerical counterexample retained in V13.
7. ~~Wire $\varsigma_e$ explicit orientation input into `sre_activation_operator.py`~~ **[Done]** `build_reaction(..., orient=ς)` + public helper `orient_from_cycle(...)`; V3 asserts 41/41 PASS, self_test 19/19 PASS.

**To Do**

8. **Add rigorous proof for §9 compatibility proposition** (V11 has numerical evidence in both bipartite / odd-cycle directions; proof is missing).
9. DBT instance: C21 skeleton + 18 H coverage changes, run v0, output $(\kappa,\varrho,\nu,\mu)$.
10. **V12 DFT benchmark**: 5–8 elementary steps, test H20.1 — the external validation deciding the operator's reason for existing.
11. **v1.0 theoretical gap (R11 root fix)**: induce edge orientation from reaction data itself, freeing $\varrho$ from arbitrary labeling conventions. Until then, $\varrho$ can only be used for **relative ranking under the same labeling convention**; $\varsigma_e$ provides a manual correction knob, but not automatic resolution.

---

*v0.3. All "proven" conclusions hold on 1-dimensional complexes without 2-cells; all "unproven" conclusions (H20.1, C20.7) are explicitly marked and must not be cited as established facts in implementations or reports. Of the three v0.3 corrections, item 3 (T20.4) is a substantive mathematical error from v0.2, item 1 (D7) is a definitional self-contradiction; both have corresponding assertions in the verification program.*
