# Strict Mathematical Specification of the Spectral-Shape Equation-Solving Operator Set (Operators 13–18): Homological Solvability Theorems and the Endogenous Inversion Pipeline

**Version**: 1.3 (September 2026 · SRE Version 18.0 Extension Layer)
**Reference implementation**: `Operator_13_18_P.py` (built-in checks V1–V18, 19/19 passing)
**Stress-test suite**: `bench_random_equations.py` (10 problem types × 5 random instances = **50 equations** + 6 verification items independent of the pipeline, **50/50 passing**; problem-set document `bench_out/problem_set.md`)
**Prerequisites**: Operators 1–12 (`structure.md` v18.0, `Operator_10_C.md`, `Operator_11_C.md`, `Operator_12_C.md`)

> **The three extensions of v1.1 over v1.0** (corresponding to the engineering constraints specified by the user):
> 1. **Coupled multiple spectral shapes** (§5, §6.4): Operator 14 is generalized to a multi-shard block Jacobian, with cross-shard coupling terms and a shard-to-global embedding map;
> 2. **Non-polynomial kernels** (§4.4): Operator 13 gains an endogenous adaptive truncation order $K_f$ based on Chebyshev coefficient decay, including Bernstein-ellipse convergence-rate prediction and singularity avoidance;
> 3. **Homological solutions** (§3, §9): the definition of a solution is relaxed from "exact solution $r=0$" to "homological solution $h=0$", and a new Operator 18 (homological solution realizer) together with canonical-representative selection are added.

> **The three corrections of v1.2 over v1.1** (from what the "10 random equations" stress test exposed empirically):
> 1. **The $K_f$ criterion of Operator 13.4 changed from "single term" to "tail sum"** (§13.4) — the original criterion truncates too early when the coefficients decay geometrically; the $\ln$ kernel yields $K_f=1$ while the tail still exceeds $\gamma$;
> 2. **Zero-mode stripping is upgraded from "exclusive to singular kernels" to "mandatory whenever kernel expansion is used"** (§13.5) — for the Stieltjes kernel the analytic ellipse semi-axis is $a_{\max}=1.142 < |\xi_0|=1.536$, so the series **diverges** at the zero mode, and the higher the order the more the error explodes ($8.1\!\times\!10^{-1}\to5.0\!\times\!10^{5}$ as $K{:}2\to32$);
> 3. **For multiple shards one must freeze $\alpha_n$ and $\lambda_2$ simultaneously** (§13.6), and it was clarified that "locked-shell rescaling" may be applied only to the initial value and **not to an already-obtained solution** — a frozen scale explicitly destroys the rescaling gauge redundancy.

> **The three corrections of v1.3 over v1.2** (from what the "10 problem types × 5 groups = 50 random equations" stress test exposed empirically):
> 1. **`OBSTRUCTION` is a structural false-positive branch** (§17.1) — because the identity $r = F\nabla F$ makes $\rho_h=\|h\|/\|r\|\approx0.95$ a constant, the criterion band for "exact part converged, harmonic part not converged" is as wide as $1/\gamma \approx 4.3$ times, so any $F$ falling inside it is **misjudged as a topological obstruction** and handed to Operator 9, which changes $\beta_1$. It is now required that "the update direction is exhausted (`step_dead`)" before an obstruction may be declared;
> 2. **The $\eta_N$ normalization deleted the trust region together with $1/(1+q)$** (§15.2, §15.4) — a Newton step for strongly nonlinear instances overshoots ($\|\Delta M\|\approx0.23$), $\Psi$ rises instead, and the monotonicity red line fails. An **endogenous backtracking line search** (Phase 3.5b) is now added as a safeguard;
> 3. **`SOLVED` must not look only at "first crossing of $\varepsilon$"** (§17.2) — otherwise the V-B independent-residual verification degenerates into a **tautology** with a threshold equal to the termination threshold. The added requirement is the "exhausted" condition (or `step_dead`).

---

## Abstract

This paper addresses the inverse problem **"several unknown spectral shapes form an equation; find its solution"**, and provides, within the SRE binary self-organizing-network dimension-free graph-operator system, a complete solving methodology together with the supporting operators (13–18).

The core conclusion is a **structural discovery**: the $k$-th spectral moment of a graph is algebraically exactly the normalized weight sum of $k$-step closed walks on the graph; and a closed walk is a **cycle** ($\ker\partial_1$) in the 1-chain space, whose span after modding out face boundaries $\mathrm{im}\,\partial_2$ is precisely the **first homology group $H_1$**. Hence:

> **The residual of a spectral-shape equation is intrinsically a first cohomology class $[r] \in H^1$; solving the equation is equivalent to annihilating that cohomology class on $H^1$.**

Consequently the solving process needs no new dynamics invented — it is rigorously reduced to a **discrete Hodge three-component routing** on the existing boundary operators $D_{\text{global}}=\partial_1$, $C_{\text{global}}=\partial_2$:

| Residual component | Algebraic home | Elimination mechanism | Reused operator |
|---|---|---|---|
| Gradient component $D_{\text{global}}\phi$ | $\mathrm{im}(\partial_1)$ | Vertex-potential $\Phi$ re-solve | Operator 6 ($\Phi=(D^TD)^\dagger D^TE$) |
| Curl component $C_{\text{global}}^T\psi$ | $\mathrm{im}(\partial_2^T)$ | Circulation $B$-field leapfrog cancellation | Operator 7 ($\mathcal{O}_{\text{lock}}$) |
| Harmonic component $h$ | $\mathcal{H}_1 = \ker(\partial_1^T)\cap\ker(\partial_2)$ | **Cannot be eliminated by field iteration** | Operator 9 (Betti stitching, changes topology) |

From this we obtain the **topological criterion for solvability** (Theorem S3): the equation is solvable on the given graph topology if and only if the harmonic component $h \equiv 0$; when $h \neq 0$ the residual is "closed but not exact", in which case no iteration can converge, and Operator 9's Betti stitching must change $\beta_1$ before solvability is even possible. This criterion provides the solver with an **existence certificate free of external parameters**.

**The key semantic upgrade of v1.1 — a solution is a homology class**: the user specified that "the restored graph structure may be a homological mapping rather than an exact solution". This fits the framework naturally: the exact part of the residual ($D\phi + C^T\psi$) can be absorbed by the absorption mechanisms of Operators 6/7 and **does not constitute a genuine obstruction**; the only genuine obstruction is the harmonic part. Therefore the definition of a solution can be relaxed to

$$\textbf{Exact solution: } r = 0 \qquad \subsetneq \qquad \textbf{Homological solution: } h = 0 \;(\text{i.e. } [r] = 0 \in H^1)$$

that is, **only the residual being exact is required, not the residual being zero** (Definition 3.1). Homological solutions form an affine equivalence class $M^\star + \mathrm{im}(\partial_1)\oplus\mathrm{im}(\partial_2^T)$, whose canonical representative is the one minimizing the Dirichlet energy within the homology class (Operator 18); this yields an explicit semantics for solution uniqueness: **uniqueness holds only in the sense of homology classes** (Theorem S5).

> **⚠ Correction to the intuition "relaxing the criterion ⇒ faster convergence" (v1.1 empirical)**
> Relaxing the termination criterion from $\|r\|\to 0$ to $\|h\|\to 0$ **does not necessarily reduce the iteration count**. Since $\rho_h \equiv \|h\|/\|r\| = \|\Pi_{\mathcal{H}_1}\nabla F\|/\|\nabla F\|$ is independent of $F$ (empirically approximately the constant $0.947$ on a $\beta_1=1$ complex), the harmonic channel cannot be compressed independently and can only vanish together with $\|r\|$; when $\rho_h > \gamma$ the two-level criteria coincide at the convergence point (empirically V15 shows no bifurcation point).
> **The true benefit of homological solutions is semantic, not accelerative**: it relaxes the acceptable solution set from $\{r=0\}$ to $\{h=0\}$, so that when the equation admits **no exact solution at all** because it is topologically obstructed, one can still deliver a graph structure correct in the homological sense. See §17.1 for details.

---

## 1. Canonical Formalization of the Problem

### 1.1 What is a "spectral shape"

In the SRE framework there are no external coordinates and no continuous metric, so a "spectral shape" must be defined as a **purely algebraic quantity**:

**Definition 1.1 (spectral shape)**: Let the reduced Laplacian of a locally autonomous shard $\Omega_\nu$ be $L_{\Omega_\nu} \in \mathbb{R}^{N_K \times N_K}$ (positive semi-definite, with $\ker$ dimension $=$ the local component of $\beta_0$). Its **spectral shape** $\sigma_\nu$ is defined as the normalized spectral measure of that operator:

$$\sigma_\nu(\lambda) \equiv \frac{1}{N_{K_\nu}}\sum_{i=1}^{N_{K_\nu}} \delta\left(\lambda - \lambda_i\left(L_{\Omega_\nu}\right)\right)$$

After compression by the endogenous normalization $\alpha_n$ (spectral radius) of Operator 6, the spectral support is clamped into the **dimensionless interval** $[0, 1]$:

$$\hat{L}_{\Omega_\nu} \equiv \frac{L_{\Omega_\nu}}{\alpha_n}, \qquad \mathrm{supp}(\sigma_\nu) \subseteq [0,1]$$

**Note**: Operator 10 has already proved that $\lambda_2(n) > 0$ always holds, so the effective lower bound of the spectral support is the endogenous spectral gap ratio $\gamma \equiv \lambda_2/\alpha_n \in (0,1]$. **This dimensionless ratio is the only natural scale unit of this solving system**; every threshold, step size, and convergence criterion throughout is generated endogenously from $\gamma$, with no external constant whatsoever (in accordance with Postulate 3).

### 1.2 What is a "spectral-shape equation"

**Definition 1.2 (spectral-shape equation)**: Let there be $p$ unknown spectral shapes $\sigma_1,\dots,\sigma_p$; the equation $\mathcal{F}$ is an algebraic–analytic functional on spectral moments:

$$\boxed{\;\mathcal{F}\left(\sigma_1, \dots, \sigma_p\right) \equiv \sum_{j=1}^{J} a_j \prod_{\nu=1}^{p} \left( \int_{0}^{1} f_{j\nu}(\lambda)\, d\sigma_\nu(\lambda) \right)^{e_{j\nu}} = 0\;}$$

where $a_j \in \mathbb{R}$, $e_{j\nu} \in \mathbb{N}$, and $f_{j\nu}$ are analytic kernels. The solving goal: find the spectral-shape tuple $\{\sigma_\nu^\star\}$ such that $\mathcal{F} = 0$, and **realize it as a concrete spin-adjacency structure $M_\Omega^\star$** under the SRE semantics (since in this system only the graph is real, and a spectral shape is merely its projection).

### 1.3 The key dimension reduction: spectral shape → moment vector

Expanding the kernel functions $f_{j\nu}(\lambda) = \sum_{k} c_{j\nu k} T_k(\lambda)$ in the Chebyshev basis $\{T_k\}_{k=0}^{K}$ gives

$$\int f_{j\nu}\, d\sigma_\nu = \sum_{k=0}^{K} c_{j\nu k}\, \tau_k^{(\nu)}, \qquad \tau_k^{(\nu)} \equiv \int_0^1 T_k(\lambda)\, d\sigma_\nu(\lambda)$$

and the equation becomes a **multivariate equation in moment space** $\mathcal{F}(\boldsymbol{\tau}^{(1)},\dots,\boldsymbol{\tau}^{(p)}) = 0$. The unknown is reduced from the infinite-dimensional function $\sigma$ to the finite-dimensional vector $\boldsymbol{\tau} \in \mathbb{R}^{p(K+1)}$, and $\tau_k$ admits a purely combinatorial, purely local computational route (Theorem 13.1), with no eigendecomposition throughout.

### 1.4 Three-level complexity classification of equation kernels (v1.1)

According to how $\mathcal{F}$ acts on the spectral shapes, the equations are divided into three levels, each requiring additional machinery:

| Level | Form | Handling mechanism | Specification location |
|---|---|---|---|
| **L1 single spectral shape · polynomial kernel** | $\mathcal{F} = \sum_j a_j \prod_k (\tau_k)^{e_{jk}}$ | The Operators 13–17 baseline suffices | §3–§8 |
| **L2 multiple spectral shapes · coupled kernel** | $\mathcal{F}$ contains cross-shard products $\tau_k^{(\mu)}\tau_l^{(\nu)}$ | Block Jacobian + shard embedding map + splicing consistency | **§6.4** |
| **L3 non-polynomial kernel** | contains $\ln$, rational (Stieltjes-type), exponential, etc. | Chebyshev coefficient expansion + endogenous adaptive truncation $K_f$ | **§4.4** |

**Their combination** (L2 ∩ L3, i.e. coupled multiple spectral shapes with a non-polynomial kernel) is the complete domain of applicability of specification v1.1. The key limitation is the singularity-avoidance criterion of §4.4: the convergence rate of a non-polynomial kernel is **determined solely by the endogenous spectral gap ratio $\gamma = \lambda_2/\alpha_n$** — as $\gamma \to 0$ (the graph approaching disconnection) the required expansion order of a $\ln$-type kernel diverges, and Operator 16's feasibility warning must catch it.

---

## 2. Core Mathematical Foundation: Three Foundational Theorems

### Theorem S1 (Endogenous equivalence theorem of spectral moments and closed walks)

The $k$-th Chebyshev spectral moment equals the normalized weight sum of $k$-step closed walks on the graph, and can be obtained deterministically within $\mathcal{O}(N_K M_K K)$ by a three-term recurrence, **without any eigenvalue decomposition**.

**Proof**: Let $Y_\nu \equiv 2\hat{L}_{\Omega_\nu} - I$, whose spectral support is $\subseteq [-1,1]$. By the spectral theorem,

$$\tau_k^{(\nu)} = \frac{1}{N_K}\mathrm{tr}\left(T_k(Y_\nu)\right) = \frac{1}{N_K}\sum_{v \in \Omega_\nu} \left\langle e_v,\; T_k(Y_\nu)\, e_v \right\rangle$$

Expand $T_k(Y) = \sum_{r=0}^{k} \beta_{kr} Y^r$; then $(Y^r)_{vv} = \sum_{v_1,\dots,v_{r-1}} Y_{v v_1}Y_{v_1 v_2}\cdots Y_{v_{r-1} v}$ is exactly the **weight sum of all closed walks of length $r$ starting from $v$**. Hence $\tau_k$ is a linear combination of closed walks of length $\le k$. Moreover $T_k(Y)e_v$ is generated order by order through the Chebyshev three-term recurrence

$$u_0 = e_v,\quad u_1 = Y e_v,\quad u_{k+1} = 2Y u_k - u_{k-1}$$

and each order needs only one **local sparse matrix–vector product** (the number of nonzeros of $Y$ is $= \mathcal{O}(M_K)$). No matrix factorization is involved throughout, satisfying Postulate 1 (spectral-flow shard splicing and reuse; a globally synchronized decomposition is forbidden). $\blacksquare$

### Theorem S2 (First-homology attribution theorem of spectral moments)

The linear space spanned by the spectral moments, after modding out face boundaries, is **isomorphic to the dual of the first homology group $H_1$**; its dimension is the first Betti number $\beta_1$.

**Proof**: By Theorem S1, the spectral moments are generated by closed walks. A closed walk $w = \sum_e n_e e$ satisfies in–out conservation at every vertex, i.e. $\partial_1 w = 0$, so $w \in \ker\partial_1$ (a **cycle**). By the exactness constraint of the chain complex $\partial_1\partial_2 = 0$, one has $\mathrm{im}\,\partial_2 \subseteq \ker\partial_1$. The space of closed walks, after modding out the boundaries generated by 2-chains (faces), is precisely

$$H_1 \equiv \ker\partial_1 \big/ \mathrm{im}\,\partial_2, \qquad \dim H_1 = \beta_1$$

and Operator 12 has already proved $n_{\text{loops}} = \beta_1$ (Theorem 12.4). Hence the spectral-moment functional naturally takes values in $H_1^* \cong H^1$. $\blacksquare$

**Corollary S2.1**: The sensitivity vector of the spectral moments with respect to the edge weights (defined in Operator 14) must lie in the 1-chain space $C_1 \cong \mathbb{R}^{m_g}$, so the **residual can be injected losslessly into Operator 7's $E/B$-field leapfrog**, with no additional spatial embedding.

### Terminology convention (important: strict distinction between the two "cycle counts")

This specification strictly distinguishes the following two quantities that are often conflated; they coincide only in the special case ($\partial_2$ spanning the full cycle space):

| Symbol | Name | Definition | Semantics |
|---|---|---|---|
| $\nu$ | cycle-space dimension / circuit rank | $\nu \equiv \dim\ker\partial_1 = m_g - n + \beta_0$ | the number of independent **closed-walk** basis elements. This is the $n_{\text{loops}}$ of Operator 12 |
| $\beta_1$ | first Betti number / homology dimension | $\beta_1 \equiv \dim\mathcal{H}_1 = \nu - \mathrm{rank}(\partial_2)$ | the number of topologically "true holes" remaining after subtracting **face boundaries** |

**Key**: $\nu$ measures "how many independent closed loops can be drawn", while $\beta_1$ measures "how many loops **cannot** be filled by 2-chains (faces)". $\beta_1 = 0$ means all cycles can be filled by faces (e.g. spherical topology), in which case **there is no topological obstruction** (the $h$-space of Theorem S3 is zero and the equation is always solvable).

When, for a planar graph, one takes all bounded faces of its planar embedding as 2-chain generators, then $\mathrm{rank}(\partial_2) = \nu$, so $\beta_1 = 0$; if the face set is incomplete (e.g. taking only triangles and omitting the large cycles), then $\beta_1 > 0$, and the **residual $\beta_1$ is precisely the degrees of freedom by which the equation may be unsolvable**. This distinction is the numerical basis by which Operator 17 decides "topological obstruction".

---

## 2-bis. Definition and Structure of Homological Solutions (v1.1 core)

### Definition 3.1 (exact solution vs. homological solution)

Let the residual 1-chain of equation $\mathcal{F}$ on graph $M$ be $r(M)$, with Hodge decomposition $r = D\phi + h + C^T\psi$. Two levels of solution are defined:

$$\textbf{Exact solution } \mathcal{S}_{\text{exact}} \equiv \{ M : r(M) = 0 \} \qquad\text{(all three components zero, } m_g \text{ constraints in total)}$$

$$\boxed{\;\textbf{Homological solution } \mathcal{S}_{\text{hom}} \equiv \{ M : h(M) = 0 \} \;=\; \{ M : [r(M)] = 0 \in H^1 \} \;}\qquad\text{(only } \beta_1 \text{ constraints)}$$

**Physical semantics**: the exact part of the residual $D\phi + C^T\psi$ can be absorbed by the absorption mechanisms of Operator 6 (potential re-solve) and Operator 7 (circulation cancellation), and **does not constitute a genuine obstruction**; the only genuine obstruction is the harmonic part. Hence "residual exact" already suffices to call it a solution — this is exactly the rigorous formalization of the user's stipulation that "the graph structure may be a homological mapping rather than an exact solution".

Obviously $\mathcal{S}_{\text{exact}} \subseteq \mathcal{S}_{\text{hom}}$, and the inclusion is proper when $\beta_1 > 0$.

### Definition 3.2 (homological equivalence and homological distance)

Two graphs $M, M'$ are called **homologically equivalent** ($M \sim M'$) if the difference of their residuals is an exact chain:
$$M \sim M' \iff r(M) - r(M') \in \mathrm{im}(\partial_1) \oplus \mathrm{im}(\partial_2^T) \iff h(M) = h(M')$$

On the equivalence classes we define the **homological distance** (a pseudo-metric, identically zero within a class):

$$\boxed{\; d_{\text{hom}}(M, M') \equiv \big\| h(M) - h(M') \big\|_2 \;}$$

$d_{\text{hom}}$ measures the **true difference in the topological sense** between two graph realizations — it automatically ignores every exact difference absorbable by the field, and compares only the "holes that cannot be eliminated". This is the correct metric for judging whether two candidate realizations are "essentially the same".

### Theorem S4 (dimension of the homological-solution set: $m_g - \beta_1$)

Linearizing at a solution $M^\star \in \mathcal{S}_{\text{hom}}$, the tangent space of the homological-solution set contains $\mathcal{H}_1^{\perp} = \mathrm{im}(\partial_1)\oplus\mathrm{im}(\partial_2^T)$, hence

$$\dim \mathcal{S}_{\text{hom}} \;=\; m_g - \beta_1, \qquad \dim \mathcal{S}_{\text{exact}} \;=\; 0 \;(\text{isolated point})$$

**Proof**: The constraint $h(M) = 0$ consists of $\beta_1$ independent scalar equations (since $h \in \mathcal{H}_1$, $\dim = \beta_1$), acting on the $m_g$-dimensional edge-weight space, so the solution set has dimension $m_g - \beta_1$. The tangent directions are guaranteed by Theorem 15.3: $\Delta M \perp \mathcal{H}_1$, i.e. moving along the Newton direction does not change $h$ to first order. $\blacksquare$

**Corollary S4.1 (solving difficulty is monotonically determined by $\beta_1$)**: the larger $\beta_1$ is → the more harmonic constraints → the smaller the homological-solution set → the harder to solve; when $\beta_1 = 0$ the number of constraints is zero.

### Theorem S5 (uniqueness semantics of homological solutions)

The solution of the equation is **unique in the sense of homology classes**: any two homological solutions $M_1^\star, M_2^\star \in \mathcal{S}_{\text{hom}}$ must be homologically equivalent ($d_{\text{hom}} = 0$), but in general $M_1^\star \neq M_2^\star$ (they may differ by an exact edge-weight perturbation).

### ⚠ Degeneracy warning: homological solutions lose discriminating power when $\beta_1 = 0$

When $\beta_1 = 0$ (e.g. a closed complex), $\mathcal{H}_1 = \{0\}$, so $h \equiv 0$ **holds for any graph** — the homological-solution set degenerates to the whole edge-weight space $\mathcal{S}_{\text{hom}} = \mathbb{R}^{m_g}$, and the criterion $|h| = 0$ carries no information.

In this case one must invoke the **canonical-representative** criterion to select a unique realization (Operator 18): take the one minimizing the Dirichlet energy within the homology class. This also explains why canonical-representative selection in Operator 18 is not an option but a necessary component of v1.1.

**Engineering guideline**: before solving, compute $\beta_1$. If $\beta_1 = 0$, solve directly with the exact-solution criterion $\|r\| \le \epsilon_{\text{endo}}$ and skip the homological-solution flow; if $\beta_1 > 0$, one may then enable the homological-solution criterion $\|h\| \le \epsilon_{\text{endo}}$ to save iterations.

### Theorem S3 (Hodge three-component decomposition of the residual and the solvability criterion) ★core

Given any 1-chain residual $r \in C_1(\mathbb{R}^{m_g})$, there exists a **unique orthogonal decomposition**

$$\boxed{\; r = D_{\text{global}}\,\phi \;+\; h \;+\; C_{\text{global}}^T\,\psi \;}$$

where ($D = \partial_1: C_0\!\to\!C_1$ is $m_g\times n$, $C = \partial_2: C_1\!\to\!C_2$ is $f\times m_g$)
- $D\phi \in \mathrm{im}(\partial_1) \subseteq C_1$: the **gradient component**, with $\phi \in \mathbb{R}^{n}$ the vertex potential difference;
- $C^T\psi \in \mathrm{im}(\partial_2^T) \subseteq C_1$: the **curl component**, with $\psi \in \mathbb{R}^{f}$ the circulation density;
- $h \in \mathcal{H}_1 \equiv \ker(\partial_1^T) \cap \ker(\partial_2) \subseteq C_1$: the **harmonic component**, satisfying $D^T h = 0$ and $C h = 0$.

and the projection operators are completely endogenous (using only the boundary operators, with no external metric):

$$\phi \equiv \underbrace{(D^T D)^{\dagger}}_{\displaystyle L_0^{\dagger}\;(\text{0-order Laplacian pseudo-inverse})} D^T r \;\in\; \mathbb{R}^{n}, \qquad \psi \equiv (C C^T)^{\dagger} C\, r \;\in\; \mathbb{R}^{f}, \qquad h \equiv r - D\phi - C^T\psi$$

**Note**: the solving formula for $\phi$ is **strictly isomorphic** to Operator 6's potential-closure formula $\Phi_{s-1} = (D^TD)^\dagger(D^T E_{s-1})$ (merely replacing the edge flow $E$ by the residual $r$), so all of Operator 6's $\mathcal{O}(1)$ local facilities can be reused directly, with zero new solver.

**Solvability criterion**: the equation is solvable on the given graph topology $\iff h \equiv 0$.

**Proof**:
*(i) Existence and uniqueness*: the graph Hodge decomposition theorem guarantees that $C_1 = \mathrm{im}(\partial_1) \oplus \mathcal{H}_1 \oplus \mathrm{im}(\partial_2^T)$ is an orthogonal direct-sum decomposition (where $\mathcal{H}_1 \cong H_1$ is the harmonic representative of the homology group), so the decomposition is unique, and

$$\|r\|_2^2 = \|D\phi\|_2^2 + \|h\|_2^2 + \|C^T\psi\|_2^2$$

*(ii) Projection formulas*: $D\phi$ is the orthogonal projection of $r$ onto $\mathrm{im}\,\partial_1$, whose normal equation is $D^T(D\phi) = D^T r \Rightarrow (D^TD)\phi = D^T r$, hence $\phi = (D^TD)^\dagger D^T r$; likewise $C^T\psi$ is the projection of $r$ onto $\mathrm{im}\,\partial_2^T$, with $\psi = (CC^T)^\dagger C r$. The former is the 0-order Laplacian pseudo-inverse (of the same origin as Operator 6's potential solve), the latter the 2-order Laplacian pseudo-inverse; an $\mathcal{O}(1)$ local solving route has been established for both.

*(iii) Solvability*: the update direction of the solving iteration (Operator 15) must belong to $\mathrm{im}(\partial_1) \oplus \mathrm{im}(\partial_2^T) = \mathcal{H}_1^{\perp}$ (see Theorem 15.3). Hence if $h \neq 0$, the harmonic component of the residual falls into the kernel of the update operator, and **no number of field iterations can make it decrease**; then $r$ is a "closed but not exact" cohomology class, constituting a **topological obstruction**. Only changing the graph's topology ($\Delta\beta_1 \neq 0$, Operator 9's Betti stitching) can change the dimension of $\mathcal{H}_1$ and thereby open a new exact direction for the residual. $\blacksquare$

**Corollary S3.1 (obstruction certificate)**: when the iteration stalls with $\|h\|$ not decreasing, the harmonic component $h$ itself is the **algebraic certificate** that the equation is unsolvable — it precisely indicates "how many independent loops the equation demands that the current manifold cannot provide".

---

## 3. Operator Specifications

### Operator 13: $\mathcal{E}_{\text{mom}}$, the Spectral-Shape Chebyshev Moment Encoder
**(Spectral-Shape Chebyshev Moment Encoder)**

| Item | Specification |
|---|---|
| Topological space | $\mathcal{H}_{\text{sym}}(N_K) \to \mathbb{R}^{K+1}$ |
| Input | Local shard reduced Laplacian $L_{\Omega_\nu}$; global spectral assets $(\alpha_n,\lambda_2)$ (output of Operator 6) |
| Output | Normalized Chebyshev moment vector $\boldsymbol{\tau}^{(\nu)} = (\tau_0,\dots,\tau_K)^{T}$; sensitivity vector set $\{\mathbf{w}_k^{(\nu)}\}$ |
| Timing position | Tail of Phase 1 (immediately after Operator 6, reusing its Lanczos subspace, with zero extra spectral decomposition) |

#### 13.1 Endogenous normalization and moment recurrence

$$\hat{L}_{\Omega_\nu} \equiv \frac{L_{\Omega_\nu}}{\alpha_n}, \qquad Y_\nu \equiv 2\hat{L}_{\Omega_\nu} - I \quad \left(\mathrm{spec}(Y_\nu) \subseteq [-1,1]\right)$$

$$\tau_k^{(\nu)} \equiv \frac{1}{N_{K_\nu}} \mathrm{tr}\left( T_k(Y_\nu) \right) = \frac{1}{N_{K_\nu}} \sum_{v\in\Omega_\nu} \left\langle e_v,\; u_k^{(v)} \right\rangle, \quad u_{k+1}^{(v)} = 2Y_\nu u_k^{(v)} - u_{k-1}^{(v)}$$

#### 13.2 Endogenous truncation order $K$ (no external parameters)

$$K_\nu \equiv \min\left( \left\lceil \frac{\alpha_n}{\lambda_2} \right\rceil,\; K_{\text{cap}} \right), \qquad K_{\text{cap}} \equiv \left\lfloor 2\ln\left(1 + N_{K_\nu}\right) \right\rfloor$$

**Basis**: the Chebyshev truncation error for a Lipschitz spectral density is $\mathcal{O}(K^{-1})$; requiring the truncation error not to exceed the endogenous minimum resolvable scale $\lambda_2/\alpha_n$ demands $K \gtrsim \alpha_n/\lambda_2$. $K_{\text{cap}}$ prevents the moment order from exceeding the logarithm of the shard's degrees of freedom (overfitting protection); the accuracy loss when it is exceeded is caught by Operator 16.

#### 13.3 Edge-space sensitivity vectors (closed form, reusing boundary-operator column vectors)

From $\partial L/\partial M_e = d_e d_e^T$ ($d_e$ being the transpose of the $e$-th row of $D_{\text{global}}$) and $T_k' = k\,U_{k-1}$ (Chebyshev of the second kind), one obtains the **fully analytic sensitivity**:

$$\boxed{\; w_{k,e}^{(\nu)} \equiv \frac{\partial \tau_k^{(\nu)}}{\partial M_e} = \frac{2k}{N_{K_\nu}\,\alpha_n}\; d_e^{T}\, U_{k-1}(Y_\nu)\, d_e \; \quad (k \ge 1), \qquad w_{0,e}^{(\nu)} \equiv 0 \;}$$

**Derivation**: from $L = D^T\mathrm{diag}(M)D$ one gets $\partial L/\partial M_e = d_e d_e^T$ ($d_e \equiv$ the transpose of the $e$-th row of the boundary operator), and $\partial Y/\partial M_e = \frac{2}{\alpha_n}d_e d_e^T$, hence
$$\frac{\partial \tau_k}{\partial M_e} = \frac{1}{N_K}\mathrm{tr}\!\left(T_k'(Y)\cdot \tfrac{2}{\alpha_n} d_e d_e^T\right) = \frac{2}{N_K\alpha_n} d_e^T T_k'(Y) d_e = \frac{2k}{N_K\alpha_n} d_e^T U_{k-1}(Y) d_e$$
(using the identity $T_k' = k\,U_{k-1}$; at $k=0$, $\tau_0 \equiv 1$, so the sensitivity is identically zero.)

$U_{k-1}$ is likewise generated synchronously by the three-term recurrence, with zero extra matrix factorization. **This formula is strictly isomorphic to Operator 10's effective impedance tensor $\mathbf{Z}_{\text{eff}} = (e_u-e_v)^T L^{+}(e_u-e_v)$** — both are quadratic forms of boundary-operator column vectors over matrix functions, so all of Operator 10's localization accelerations and Sherman-Morrison incremental-update facilities can be reused.

#### Theorem 13.1 (two-way distinguishability of moments and spectral shape)
If $K \ge \alpha_n/\lambda_2$, then the moment vector uniquely determines the spectral shape at the same scale, and the reconstruction error satisfies
$$\left\| \rho_\nu - \rho_{\nu,K} \right\|_{\infty} \le C \cdot \frac{\lambda_2}{\alpha_n}$$
**Corollary**: the resolution limit of the moment representation is exactly the endogenous spectral gap ratio; there is no finer distinguishable degree of freedom — this is consistent with the system's stance of "no external metric".

#### 13.4 Handling of non-polynomial kernels (v1.1 addition · L3-level equations)

When the equation contains a non-polynomial kernel $f$ ($\ln$, rational/Stieltjes-type, exponential, etc.), **one does not integrate $f$ numerically directly**; instead one expands it in the Chebyshev basis, thereby linearizing the nonlinear action completely into a moment inner product.

**Unified variables**: the spectral variable $\hat\lambda = \lambda/\alpha_n \in [\gamma, 1]$ relates to the recurrence variable $y \in [-1,1]$ by $\hat\lambda = (y+1)/2$. Letting $g(y) \equiv f\!\left(\frac{y+1}{2}\right)$, one has

$$\int_0^1 f(\hat\lambda)\, d\sigma \;=\; \int_{-1}^{1} g(y)\, d\sigma_Y \;=\; \sum_{k=0}^{K_f} c_k\,\tau_k \;=\; \mathbf{c}^{T}\boldsymbol{\tau}$$

**Chebyshev coefficients (Chebyshev-Gauss quadrature, deterministic)**:
$$c_k \equiv \frac{2}{N_c}\sum_{j=0}^{N_c-1} g\!\left(\cos\theta_j\right)\cos\left(k\theta_j\right), \qquad \theta_j \equiv \frac{(2j+1)\pi}{2N_c}$$
exact for polynomials of $\deg < N_c$; for general functions it converges at the Bernstein ellipse rate.

**Endogenous adaptive truncation order $K_f$** (replacing the fixed $K$ of the polynomial-kernel case):

> **v1.2 correction (empirical from the 10-equation random stress test, bench E06/E08)**. The original criterion took
> $K_f = \max\{k : |c_k| > \gamma\max|c|\}$, which measures whether a **single term** has become small. This is logically wrong: the Chebyshev coefficients decay geometrically, and **a single term becoming small is far from meaning the approximation is good enough**. Empirically the $\ln$ kernel gives $K_f = 1$, while $\mathrm{tail}(1)$ still accounts for $21\%$ of the peak $> \gamma$, with a truncation error reaching $3.25\times10^{-2}$.

What really determines accuracy is the **sum** of the discarded terms. Since $|T_k(s)| \le 1$ on $[-1,1]$,
$$\Big| g(s) - \sum_{k\le K} c_k T_k(s)\Big| \;\le\; \sum_{k>K}|c_k| \;\equiv\; \mathrm{tail}(K)$$
so $\mathrm{tail}(K)$ is the **strict upper bound** on the approximation error, and is exactly the quantity that should be compared with the endogenous tolerance:

$$\boxed{\; K_f \;\equiv\; \min\Big\{ K \;:\; \mathrm{tail}(K) \;\le\; \gamma\cdot\max_k|c_k| \Big\}, \qquad \mathrm{tail}(K) = \sum_{k>K}|c_k| \;}$$

The threshold is still $\gamma\cdot\max|c|$ — the sole endogenous scale, with no external parameters. **This criterion automatically adapts to the smoothness of the kernel**: smooth kernels give a small $K_f$, kernels with strong singularities give a large $K_f$.

**Note that this guarantees $\gamma$-level accuracy, not machine accuracy.** To reach the $10^{-6}$ level, $K$ must be as deep as $\mathcal{O}\!\left(1/\ln\rho\right)\approx 16$–$24$ — this is an explicitly stated cost, not a defect (see the bench report for the empirical $K$-sweep).

**Theorem 13.2 (the convergence rate of non-polynomial kernels is determined solely by the spectral gap ratio)**
For a kernel with a logarithmic branch point at $\hat\lambda = 0$ (typically $\ln\hat\lambda$), the location of its singularity in the $y$ variable and the Bernstein parameter are
$$\xi_0 = -\frac{1+\gamma}{1-\gamma}, \qquad \rho \equiv |\xi_0| + \sqrt{\xi_0^2 - 1}$$
The Chebyshev coefficients decay asymptotically as $|c_k| = \mathcal{O}\!\left(k^{-1}\rho^{-k}\right)$, so the lower bound on the required order is
$$K_f \;\gtrsim\; \frac{\ln(1/\gamma)}{\ln \rho}, \qquad \lim_{\gamma \to 0}\rho = 1 \;\Rightarrow\; K_f \to \infty$$

**Corollary**: **the spectral gap ratio $\gamma$ is simultaneously a measure of "the graph's connectivity margin" and of "the expandability of a non-polynomial kernel"**. The closer the graph is to disconnection ($\gamma \to 0$), the more the required expansion order of a $\ln$-type kernel diverges — this is the method's fundamental limitation on ill-conditioned graphs, and it cannot be circumvented by adding computing power.

**Singularity-avoidance criterion**: let the kernel's singularity be $\hat\lambda_s$, and define its endogenous distance to the spectral support $d_s \equiv \mathrm{dist}(\hat\lambda_s, [\gamma, 1])$.
- If $d_s > \gamma$: the expansion is safe, and $K_f$ is determined by the coefficient criterion;
- If $d_s \le \gamma$: **critical**; a $\ln$-type kernel is always in this case (the distance from the singularity 0 to the support $[\gamma,1]$ is exactly $\gamma$); here one must rely on the adaptive $K_f$ criterion, and Operator 16 must flag the warning "kernel expansion accuracy limited by the spectral gap".
- Handling: prefer raising $\lambda_2$ via Operator 9 (topological stitching to increase connectivity) so as to lift $\gamma$, rather than increasing $K_f$ and brute-forcing.

**Special status of the Stieltjes-type kernel**: the response of the kernel $\frac{1}{\hat\lambda - z}$ ($z \in \mathbb{C}\setminus\mathbb{R}$) is exactly the spectral Stieltjes transform $m(z) = \sum_k c_k(z)\tau_k$. It is simultaneously the standard gateway to **spectral-density inversion**:
$$\rho(\hat\lambda) = \frac{1}{\pi}\,\mathrm{Im}\, m(\hat\lambda + i\varepsilon), \qquad \varepsilon_{\text{endo}} \equiv \gamma$$
(the imaginary offset must be given endogenously by the spectral gap ratio; an external small quantity is forbidden.) This provides a direct route for Operator 18's "moments → spectral density" reconstruction.

#### 13.5 Zero-mode stripping (v1.2 correction · **strip whenever kernel expansion is used**, not exclusive to singular kernels)

##### Why it is not "$\ln$-only"

v1.1 wrote stripping as a prerequisite exclusive to singular kernels ($\ln$, $1/\hat\lambda$); **this is incomplete**. E08 (Stieltjes kernel) of the 10-equation random stress test exposed the true discriminating condition:

The trivial zero mode in the shifted variable is always located at
$$\xi_0 \;=\; -\frac{1+\gamma}{1-\gamma}, \qquad \rho(\xi_0) \;=\; |\xi_0| + \sqrt{\xi_0^2-1}$$
It is **always outside $[-1,1]$**, and $T_k(\xi_0)$ grows exponentially as $\rho(\xi_0)^k$. Meanwhile the Chebyshev series of the kernel $g$ converges only inside its own Bernstein ellipse, whose real semi-axis is
$$a_{\max} \;=\; \frac{\rho_{\max} + \rho_{\max}^{-1}}{2}$$
where $\rho_{\max}$ is determined by the singularity of $g$ nearest to the spectral support. **As soon as $a_{\max} < |\xi_0|$, the series diverges at $\xi_0$**, and the high-order terms, amplified by the zero mode, explode — the higher the order, the worse.

Empirical Stieltjes kernel $z = 0.5 + i\gamma$ ($\gamma = 0.2113$):

| Quantity | Value |
|---|---|
| singularity $\;s_{\text{pole}}$ | $-0.267949 + 0.535899\,i$ |
| $\rho_{\max}$ | $1.693185$ |
| $a_{\max} = (\rho+\rho^{-1})/2$ | $1.141894$ |
| $\lvert\xi_0\rvert$ | $1.535899$ |
| **Verdict** | $a_{\max} = 1.142 < 1.536 = \lvert\xi_0\rvert$ → **divergence** |

As $K$ increases from 2 to 32, the kernel-fidelity error goes $8.1\times10^{-1} \to 5.0\times10^{5}$ — **explosion rather than convergence**. After stripping it falls back to $2.02\times10^{-2}$.

> **Rule (v1.2)**: whenever a Chebyshev kernel expansion is used, always strip the zero mode. Reason: the location of $\lambda = 0$ is universally known, stripping needs no eigendecomposition, and after stripping the reduced spectrum lies strictly in $[\gamma, 1]\to s\in[-1,1]$, so the series necessarily converges. For entire functions (e.g. $\exp$) stripping is harmless; for branch/pole-type kernels stripping is **mandatory**.

##### Stripping formula

When there are multiple connected components there is an $n_0$-fold zero mode ($n_0$ is obtained purely combinatorially by union-find, using no spectral decomposition), generalized to

$$\boxed{\; \tau_k^{\text{red}} \;=\; \frac{N\,\tau_k \;-\; n_0\,T_k(\xi_0)}{N - n_0} \;}$$

($T_k(\xi_0)$ is obtained by the scalar three-term recurrence $T_{k+1} = 2\xi_0 T_k - T_{k-1}$.) The kernel integral then becomes $\frac{1}{N-n_0}\sum_{\lambda_i \ne 0} f(\hat\lambda_i) = \sum_k c_k \tau_k^{\text{red}}$.

**Corresponding correction of the sensitivity**: stripping is a linear operation, so $\partial\tau_k^{\text{red}}/\partial M_e = \frac{N}{N-n_0}\,\partial\tau_k/\partial M_e$; composed with the shift coordinate $\alpha_n^{\text{eff}} = \alpha_n(1-\gamma)$, this gives
$$w^{\text{red}}_{k,e} \;=\; \frac{N}{N-n_0}\cdot\frac{2k}{N\,\alpha_n(1-\gamma)}\,d_e^{T}U_{k-1}(\tilde Y)d_e$$

> This operation is consistent with the stance of Operator 6 that "the zero mode is a gauge redundancy rather than a physical degree of freedom": the zero mode carries only the counting information of connected components and does not participate in the spectral shape.

#### 13.6 Endogenous scale locking and field-refresh period (v1.1 addition · key consistency constraint)

The spectral moments $\tau_k$ are normalized by the endogenous scale $\alpha_n(M)$, while $\alpha_n$ itself is a function of $M$. The sensitivity of Operator 13.3 **$W_k$ does not differentiate with respect to $\alpha_n$ under Operator 6's convention** ($\alpha_n$ is a hard constant within a field-refresh period). This yields a **consistency constraint that must be obeyed**:

> **$\alpha_n$ and $\lambda_2$ must remain locked for several iteration steps. If refreshed at every step, the definition of $F$ jumps between steps and the Newton prediction $\Delta F = -F$ fails.**

Empirical comparison: at the same step size, refreshing step by step makes $F$ **jump up** on the very first step ($7.163\times10^{-2}\to7.192\times10^{-2}$), destroying the monotonicity of $\Psi$; switching to locking gives convergence in 2 steps with strict monotonicity ($7.163\times10^{-2}\to2.715\times10^{-3}$).

**Endogenous refresh criterion** (no external period parameter):
$$\text{refresh} \iff \frac{\|L(M) - L_{\text{ref}}\|_F}{\alpha_n} \;>\; \gamma$$
i.e. refresh when the relative drift of the Laplacian exceeds the spectral gap ratio — this is of the same origin as the trust region of Theorem 15.1, $\|\Delta L\|_F \le \lambda_2/2$: once the drift has accumulated past $\gamma$, the linearization is no longer trustworthy.

**For multiple shards one must** simultaneously **freeze $\lambda_2$** (v1.2 supplement, empirical from bench E09/E10). The kernel coordinate of §13.5,
$$\tilde Y \;=\; \frac{Y - \gamma I}{1-\gamma}, \qquad \gamma = \frac{\lambda_2}{\alpha_n}$$
depends on $\alpha_n$ **and** $\lambda_2$ at the same time. If one freezes only $\alpha_n$ and lets $\lambda_2$ be recomputed at every step, "inside the solver" and "the external evaluation" end up in **two different shift coordinate systems**. The empirical moment cross-deviation reaches the $2\times10^{-2}$ level (E09: $1.955\times10^{-2}$; E10: $4.567\times10^{-2}$), which in turn worsens the independent residual to $3.47\times10^{-1}$ / $1.405\times10^{0}$; freezing $\lambda_2$ as well brings it back down to $7.24\times10^{-3}$ / $1.13\times10^{-2}$.

**Locked-shell rescaling** (a prerequisite for comparing multiple realizations): when comparing two candidate graphs under the **same** set of locked scales, one must first perform
$$M \;\mapsto\; cM, \qquad c \equiv \frac{\alpha_n^{\text{lock}}}{\alpha_n(M)}$$
otherwise the spectrum of $Y = 2L/\alpha_n^{\text{lock}} - I$ escapes $[-1,1]$, the Chebyshev recurrence is amplified, and the two candidates are simply not under the same normalization — the comparison is meaningless.

> **Boundary of applicability (v1.2 clarification, important)**: shell rescaling **may be applied only to "the initial value/candidate graph before injection into the solve"**, and **must never be applied to an already-obtained solution $M^\star$**.
>
> Reason: $L(M) = D^{T}\!\operatorname{diag}(M)D$ is positively homogeneous of degree one in $M$; if **every point** is normalized by its own $\alpha_n$, then rescaling leaves $\hat\lambda$ unchanged and $\tau$ and $F$ strictly unchanged — this is intrinsically a one-dimensional **gauge redundancy**. But this system must freeze $\alpha_n$, and then $Y = 2L/\alpha_n^{\text{lock}} - I$ turns the **absolute scale** of $M$ into a physical quantity: the rescaling factor $c$ makes $Y \mapsto cY + (c-1)I$, which is **affine rather than the identity**, and $\tau_k \sim Y^{k}$ changes accordingly.
>
> Empirical (bench E01): after multiplying back the $\alpha_n$ drift of the solution $M^\star$ ($4.35\times10^{-3}$) for gauge fixing, the independent residual worsens from $1.85\times10^{-2}$ to $1.19\times10^{0}$ (two orders of magnitude).
>
> **Conclusion: a frozen scale explicitly destroys the rescaling gauge redundancy; it is the symmetry this method actively gives up in exchange for the smoothness of $F$.** Therefore the residual $\alpha_n$ drift after convergence can only be accepted in Operator 16 as a second-order effect (see below).

**Quantitative acceptance criterion for the drift**: write $\varepsilon \equiv \bigl|\alpha_n(M^\star)/\alpha_n^{\text{lock}} - 1\bigr|$. When the top of the support crosses from $1$ to $1+\varepsilon$, the Hausdorff infeasibility of the moment sequence appears only at **second order** (to first order it merely shifts the support boundary), so one should have
$$\bigl|\lambda_{\min}(H)\bigr| \;=\; \mathcal{O}(\varepsilon^{2})$$
Empirical E01: $\varepsilon^{2}=1.89\times10^{-5}$ vs $|\lambda_{\min}| = 1.00\times10^{-5}$ (ratio $0.53$); E09: $\varepsilon^{2}=5.59\times10^{-5}$ vs $8.43\times10^{-5}$ (ratio $1.51$). Operator 16's admission criterion is graded accordingly:

| Case | Verdict |
|---|---|
| $\lambda_{\min}(H) \ge 0$ | **pass** |
| $\lambda_{\min}(H) < 0$ but $\|\lambda_{\min}\| \le 10\,\varepsilon^{2}$ and $\varepsilon < \gamma$ | **pass (*)** — every violation is explained by the freezing artifact |
| $\lambda_{\min}(H) < 0$ and $\|\lambda_{\min}\| > 10\,\varepsilon^{2}$ | **fail** — genuinely infeasible moments, must be clamped by Op16 |

#### Complexity and red lines
$\mathcal{O}(N_K \cdot M_K \cdot K)$ (polynomial kernel) or $\mathcal{O}(N_c^2 + N_K M_K K_f)$ (non-polynomial kernel, with the coefficient quadrature precomputed once). Since Operator 10 has proved $N_K \le K_0 = \mathcal{O}(1)$, the whole is at the **local constant order**.
**Hard red line**: when $K_{\text{cap}}$ takes effect (ill-conditioned graph, $\kappa_\Omega \gg K_{\text{cap}}$) the accuracy claim must be downgraded, and Operator 16 must output a feasibility warning; silently downgrading accuracy is forbidden. For non-polynomial kernels one must additionally verify $K_f \le K_{\text{cap}}$, otherwise declare "kernel not expandable".

---

### Operator 14: $\mathcal{R}_{\text{hodge}}$, the Equation-Residual Homological Router
**(Equation Residual Homological Router)**

| Item | Specification |
|---|---|
| Topological space | $\mathbb{R}^{p(K+1)} \to C_1(\mathbb{R}^{m_g}) \to \mathrm{im}(\partial_1) \oplus \mathcal{H}_1 \oplus \mathrm{im}(\partial_2^T)$ |
| Input | Moment vector set $\{\boldsymbol{\tau}^{(\nu)}\}$, equation $\mathcal{F}$, boundary operators $D_{\text{global}}, C_{\text{global}}$ |
| Output | Three residual components $(\phi, \psi, h)$ and their norms; injection instructions |
| Timing position | Tail of Phase 3 (executed jointly with Operator 7's half-step $B_{s+1/2}$ update) |

#### 14.1 Moment-space residual and dimension lifting ($\mu_{\text{resid}}$ micro-operator)

$$g \equiv \mathcal{F}\left(\boldsymbol{\tau}^{(1)},\dots,\boldsymbol{\tau}^{(p)}\right) \in \mathbb{R}^{q}$$

Jacobian $J \in \mathbb{R}^{q \times p(K+1)}$, $J_{j,(\nu,k)} \equiv \partial \mathcal{F}_j / \partial \tau_k^{(\nu)}$ (analytically available, since $\mathcal{F}$ is polynomial in the moments).

**Residual dimension lifting**: push the scalar residual back into the 1-chain space along the sensitivity directions:

$$r \equiv \sum_{\nu} \sum_{k=0}^{K} \left( J^{T} g \right)_{(\nu,k)} \cdot \mathbf{w}_k^{(\nu)} \;\in\; \mathbb{R}^{m_g}$$

i.e. $\nabla_M \mathcal{F} = \sum_{\nu,k} J_{(\nu,k)}\,\mathbf{w}_k^{(\nu)}$, combined with the scalar residual $g$. **This vector naturally belongs to the edge space**, and by Corollary S2.1 it can enter the Hodge decomposition directly.

#### 14.2 Three-component projection

$$\phi \equiv (D^T D)^{\dagger} D^T r \in \mathbb{R}^{n},\qquad \psi \equiv (C C^T)^{\dagger} C\, r \in \mathbb{R}^{f},\qquad h \equiv r - D\phi - C^T\psi$$

#### 14.3 Component routing (reusing existing operators, zero new dynamics)

**Gradient channel** (vertex potential $\Phi$, Operator 6 reuse): the gradient component of the residual requires a vertex-potential correction $\phi$, injected directly in the 0-chain space:
$$\Phi_{s-1} \;\leftarrow\; \Phi_{s-1} \;-\; \eta_{\text{inj}}^{(\phi)} \cdot \phi, \qquad \eta_{\text{inj}}^{(\phi)} \equiv \frac{\lambda_2}{\lambda_2 + \|D\phi\|_2}$$
(equivalently, Operator 6's right-hand side is rewritten as $(D^TD)^\dagger D^T\!\left(E_{s-1} - \eta\,r\right)$; the two are equivalent by the projection idempotency $D(D^TD)^\dagger D^T = P_{\mathrm{im}D}$.)

**Curl channel** (circulation $B$, Operator 7 reuse): $\psi \in \mathbb{R}^f$ is itself a face-space element, injected directly:
$$B_{s+1/2} \;\leftarrow\; B_{s+1/2} \;-\; \eta_{\text{inj}}^{(\psi)} \cdot \psi, \qquad \eta_{\text{inj}}^{(\psi)} \equiv \frac{\lambda_2}{\lambda_2 + \|C^T\psi\|_2} \in (0,1]$$
The injected amount feeds back naturally to the edge flow $E$ in the next half-step through Operator 7's $C^T B$ term, closing the loop.

The endogenous injection coefficients $\eta_{\text{inj}}^{(\cdot)}$ guarantee that the injection does not overshoot (the denominator self-adaptively absorbs the magnitude), with no external relaxation factor.

$$\textbf{Harmonic} \to \text{suspended, handed to Operator 17 for adjudication}$$

#### Theorem 14.1 (conservation of the dual pairing on a closed manifold)
Under the premise that the **zero-flux-escape condition** $C_{\text{global}}E_{\text{global}} \equiv 0$ already guaranteed by Operator 7 holds, the Poincaré dual-pairing variation caused by the above curl injection is identically zero:
$$\Delta\left( E_s^T \, C_{\text{global}}^T \, B_{s+1/2} \right) \;=\; -\eta_{\text{inj}}^{(\psi)}\left\langle C_{\text{global}} E_s,\; \psi \right\rangle \;=\; 0$$
**Proof**: $C E_s = 0 \Rightarrow E_s \in \ker\partial_2 = \left(\mathrm{im}\,\partial_2^T\right)^\perp$, so $E_s \perp C^T\psi$ holds for any $\psi$, and the pairing variation is zero. $\blacksquare$

**Corollary 14.1 (constructive guarantee of closed flow)**: by the exactness of the chain complex $\partial_2\partial_1 = 0$, any gradient field $E = D_{\text{global}}\varphi$ automatically satisfies $CE = (CD)\varphi = 0$, so the edge flow generated by Operator 6's output potential field falls naturally within the domain of this theorem, **with no extra projection needed**.

**Counterexample warning**: if $E$ contains a nonzero curl component ($CE \neq 0$, i.e. the manifold is not closed), the injection produces a pairing variation of $\mathcal{O}(\eta\|CE\|\|\psi\|)$; in that case the closure must first be completed within Operator 7 before the solving injection is performed — this is the **hard timing reason** why Phase 3.5 must come after Phase 3.

#### 14.4 Coupled multiple spectral shapes (v1.1 addition · L2-level equations)

Suppose the equation couples the spectral shapes of $p$ shards. Each shard $\Omega_\nu$ has its own local edge space $\mathbb{R}^{M_{K_\nu}}$ and local sensitivity $\mathbf{w}_k^{(\nu)}$, but the residual must be synthesized in the **global edge space** $C_1 \cong \mathbb{R}^{m_g}$ before a Hodge decomposition can be performed.

**Shard embedding map $\Xi_\nu$** (isomorphic to the block splicing of Operator 3's $D_{\text{global}}$):
$$\Xi_\nu \in \{0,1\}^{m_g \times M_{K_\nu}}, \qquad \Xi_\nu(e_{\text{global}}, e_{\text{local}}) = 1 \iff e_{\text{local}} \in \text{the } e_{\text{global}}\text{-th global edge of } \Omega_\nu$$
i.e. a 0-1 selection matrix (column-orthogonal, $\Xi_\nu^T\Xi_\nu = I$). Local vectors are lifted to the global space via $\tilde{\mathbf{w}}_k^{(\nu)} \equiv \Xi_\nu \mathbf{w}_k^{(\nu)}$.

**Block Jacobian and residual synthesis**:
$$J \in \mathbb{R}^{q \times p(K+1)}, \quad J_{j,(\nu,k)} \equiv \frac{\partial \mathcal{F}_j}{\partial \tau_k^{(\nu)}}$$
$$\boxed{\; r \;=\; \sum_{\nu=1}^{p} \Xi_\nu \left( \sum_{k=0}^{K} \left(J^{T} g\right)_{(\nu,k)} \, \mathbf{w}_k^{(\nu)} \right) \;\in\; \mathbb{R}^{m_g} \;}$$

**Coupling terms need no special machinery**: if $\mathcal{F}$ contains a cross-shard product $\tau_k^{(\mu)}\tau_l^{(\nu)}$, then by the product rule
$$\frac{\partial \mathcal{F}}{\partial \tau_k^{(\mu)}} = \tau_l^{(\nu)}\cdot(\cdots)$$
this factor falls automatically into the $(\mu,k)$ block of the block Jacobian. **The coupling is carried entirely by the block structure of the Jacobian**, and the downstream machinery of Operators 15/16/17 is unchanged word for word.

**Splicing consistency constraint (a rigid requirement specific to multiple shards)**:
all shards must be normalized by the **same global $\alpha_n$** (Operator 13.1), while $\alpha_n, \lambda_2$ are updated monotonically by Operator 6's splicing kernel as
$$\alpha_n \leftarrow \max\left(\alpha_{n-1},\ \alpha_{\Omega_k}\|P_{\Omega_k,\text{edge}}\|_2^2\right), \qquad \lambda_2(n) \leftarrow \min\left(\lambda_2(n-1),\ \lambda_{2,\Omega_k}\right)$$
Since $\max$/$\min$ are both monotone operations, **the change of the spectral gap ratio $\gamma = \lambda_2/\alpha_n$ within the solving inner loop is bounded and non-oscillatory**, so $K_f$ (Theorem 13.2) remains stable during the iteration. This is the **structural precondition** for coupled multiple spectral shapes to converge.

**Theorem 14.2 (the endogenous trust region automatically absorbs the coupling amplification)**
After multi-shard synthesis $\|\mathbf{g}_M\|_2$ grows with $p$ (contributions of the shards add up), but the trust-region denominator $1 + \tilde{\mathbf{g}}^TA^\dagger\tilde{\mathbf{g}}$ of Operator 15 grows quadratically while the numerator grows only linearly, so the step size is automatically compressed as $\mathcal{O}(1/p)$. **Conclusion: increasing the number of coupled shards requires no step-size re-tuning**.

#### Complexity and red lines
$\mathcal{O}\!\left(\sum_\nu M_{K_\nu}K + m_g + f\right) = \mathcal{O}(p\,M_K K)$ (multiple shards).
**Hard red line**: the injection **must never** touch the diagonal entries of $M_\Omega$ (Postulate 2); curl cancellation may only be performed in the edge/cycle space. The only legal route for diagonal correction is Operator 8's $\mu_{\text{trace}}$. With multiple shards one must also verify that all shards use the **same** $\alpha_n$; per-shard normalization is forbidden (it would make the moment scales inconsistent and render the product terms on both sides of the coupled equation meaningless).

---

### Operator 15: $\mathcal{N}_{\text{endo}}$, the Endogenous Quasi-Newton Spectral Inverter
**(Endogenous Quasi-Newton Spectral Inverter)**

| Item | Specification |
|---|---|
| Topological space | $C_1(\mathbb{R}^{m_g}) \to C_1(\mathbb{R}^{m_g})$ (edge-weight increment space) |
| Input | Edge-space gradient $\mathbf{g}_M \equiv r$, harmonic component $h$, weighted Hodge Laplacian $A$ |
| Output | Edge-weight increment $\Delta M$ (the graph realization update of the spectral shape) |
| Timing position | **Phase 3.5 (new solving inner loop, step $\kappa$)** |

#### 15.1 Endogenous Hessian surrogate (weighted Hodge Laplacian)

$$\boxed{\; \mathcal{H}_{\text{endo}} \equiv \mathbf{g}_M \mathbf{g}_M^T \;+\; \underbrace{\lambda_2\, D D^T \;+\; \frac{\lambda_2^2}{\alpha_n}\, C^T C}_{\displaystyle A\;(\text{weighted Hodge Laplacian } L_1)} \;}$$

Semantics of the three terms:
1. **rank-one Gauss-Newton term**: captures the local curvature of the equation;
2. **$\lambda_2 DD^T$ (gradient regularization)**: the step size is clamped by the spectral gap along connected directions, preventing overshoot across a cut set;
3. **$\frac{\lambda_2^2}{\alpha_n}C^TC$ (curl regularization)**: the step must not destroy the existing cycle structure (the algebraic guarantee of $\Delta\beta_1 = 0$).

#### 15.2 Sherman-Morrison closed-form inversion ★ (v1.1 correction: Newton normalization)

Since $\mathcal{H} = A + \mathbf{g}\mathbf{g}^T$, its Moore-Penrose pseudo-inverse has an exact closed form:

$$\mathcal{H}^{\dagger}\mathbf{g} = A^{\dagger}\mathbf{g} - \frac{A^{\dagger}\mathbf{g}\,\left(\mathbf{g}^T A^{\dagger}\mathbf{g}\right)}{1 + \mathbf{g}^T A^{\dagger}\mathbf{g}} = \frac{A^{\dagger}\mathbf{g}}{1 + \mathbf{g}^T A^{\dagger}\mathbf{g}}$$

where $A^\dagger(\cdot)$ is solved by the **conjugate gradient method** ($A$ is sparse symmetric positive semi-definite), and the iteration first removes the harmonic component to guarantee $x \perp \ker A$. Here $\ker A = \ker(D^T)\cap\ker(C) = \mathcal{H}_1$, so $\dim\ker A = \beta_1$ — **the iteration's component along every homological direction is identically zero**, which is precisely the algebraic root of "the harmonic residual cannot be eliminated by iteration" in Theorem S3.

In what follows the effective gradient after removing the harmonic component is denoted $\tilde{\mathbf{g}} \equiv \mathbf{g}_M - h$ ($\tilde{\mathbf{g}} \perp \mathcal{H}_1$), and $q \equiv \tilde{\mathbf{g}}^T A^\dagger \tilde{\mathbf{g}}$.

> **⚠ Defect of the v1.0 form (empirically exposed, corrected in v1.1)**
>
> v1.0 directly took $\Delta M = -\dfrac{A^\dagger\tilde{\mathbf{g}}}{1+q}$. The **per-step relative descent rate of this formula is $\nabla F^T A^\dagger \nabla F =:\varkappa$**, and $\varkappa$ depends on the writing magnitude of the equation residual $F$:
> under the rescaling $F \to sF$, one has $q \to s^4 q$, $\tilde{\mathbf{g}} \to s^2\tilde{\mathbf{g}}$, so $\Delta M \to -\dfrac{s^2 A^\dagger\tilde{\mathbf{g}}}{1+s^4 q}$ — **the trajectory changes with the artificial scaling of the equation**. Empirically $\varkappa \approx 5.7\times10^{-3}$, i.e. about ~175 steps are needed to accomplish the work of one Newton step; and if the equation is rewritten as $100F$, the trajectory immediately differs. This violates the system's very foundation of "dimension-free, no external parameters" (Postulate 3).

**The corrected update step** (Theorem 15.1'):

$$\boxed{\; \Delta M \;\equiv\; -\,\eta_N\, A^{\dagger}\tilde{\mathbf{g}}, \qquad \eta_N \equiv \frac{F^2}{q} = \frac{F^2}{\tilde{\mathbf{g}}^T A^\dagger \tilde{\mathbf{g}}} \;}$$

**Scale-invariance proof**: when $F\to sF$, one has $\tilde{\mathbf{g}} = F\nabla\tilde{F} \to s^2\tilde{\mathbf{g}}$, $q \to s^4 q$, $F^2\to s^2F^2$, hence
$\Delta M \to -\dfrac{s^2F^2}{s^4 q}s^2 A^\dagger\tilde{\mathbf{g}} = \Delta M$, **strictly invariant**. $\blacksquare$

**Newton completeness**: after linearization, $\Delta F = \nabla F^T\Delta M = \dfrac{\tilde{\mathbf{g}}^T}{F}\left(-\eta_N A^\dagger\tilde{\mathbf{g}}\right) = -\dfrac{\eta_N q}{F} = -F$, i.e. **zeroed in one step** (the v1.0 form can only descend by the fraction $\varkappa$).

#### Theorem 15.1 (Endogenous trust-region theorem) ★v1.1
After adopting the Newton normalization $\eta_N$, the step size requires an additional **endogenous trust region**, otherwise it overshoots in the nonlinear region. Take:

$$\|\Delta L\|_F \;=\; \big\|D^T\mathrm{diag}(\Delta M)\,D\big\|_F \;\le\; \frac{\lambda_2}{2}$$

i.e. **the step must not cross half the spectral gap**. This is a direct corollary of Postulate 3: the spectral gap ratio $\gamma = \lambda_2/\alpha_n$ is the only dimensionless endogenous scale; if a single step crosses $\lambda_2/2$, then $\gamma$ itself (along with $K$, $\varepsilon_{\text{endo}}$, and the thresholds) self-destructs. Equivalently: $\|\Delta Y\| \lesssim \gamma$, i.e. the drift of $Y$ does not exceed $\gamma$ times the spectral support — which is precisely the necessary and sufficient scale for the linearization to remain valid. If exceeded, scale back proportionally by $\dfrac{\lambda_2/2}{\|\Delta L\|_F}$.

Hence the step size of this system is **not given by any external parameter**: $\eta_N$ is given endogenously by the equation residual, and the trust-region radius is given endogenously by $\lambda_2$.

> **⚠ v1.3 correction (exposed by the 50-equation stress test): the trust region must actually be put into effect, and this must be done in the form of a backtracking line search.**
> When v1.1 replaced $1/(1+q)$ by $\eta_N$, **it deleted the trust-region factor as well** — the formula $\Delta M=-\eta_N A^\dagger\tilde g$ above does not contain the $\lambda_2/2$ proportional scaling. Empirically, for a strongly nonlinear instance (bench B2-E02, $\sum a_k\tau_k^2=c$) the Newton step is $\|\Delta M\|\approx0.23$, while $\Psi=F^2/2$ instead rises ($-6.85\!\times\!10^{-3}\to-7.56\!\times\!10^{-3}$), convergence degenerates into a slow oscillation with ratio $\approx0.85$, and the monotonicity red lines (V5/V6) fail.
> **Correction**: insert an **endogenous backtracking line search in Phase 3.5b** (§15.4) between Operator 15 and Operator 16, with "$\Psi$ strictly decreases" as the sole acceptance criterion, floating-point resolution as the termination floor, and a bisection back-off factor of $1/2$. It contains no externally tunable parameter (the criterion is a comparison of the endogenous quantity $\Psi$ with its own historical value), in accordance with Postulate 3.

#### Theorem 15.2 (monotone decrease of the Dirichlet energy)
The first-order Dirichlet-energy variation along $\Delta M$ is
$$\Delta \mathcal{E}_D \;=\; \tilde{\mathbf{g}}^T \Delta M \;+\; \mathcal{O}(\|\Delta M\|^2) \;=\; -\,\eta_N\,q \;=\; -F^2 \;\le\; 0$$
with equality if and only if $F = 0$. That is, each inversion step necessarily makes the whole-graph Dirichlet energy non-increasing (and exactly $-F^2$ within the Newton region), of the same origin and isomorphic to Operator 8's red line "$\Delta\mathcal{E}_{D,\text{trace}} \le 0$ strictly monotone convergence".

#### Theorem 15.3 (orthogonality constraint on the update direction)
$\Delta M \in \mathrm{im}(\partial_1) \oplus \mathrm{im}(\partial_2^T) = \mathcal{H}_1^{\perp}$, i.e. the update always lies in the orthogonal complement of the harmonic space.
**Proof**: $\Delta M \propto A^\dagger(\mathbf{g}-h)$, and the range of $A^\dagger$ is $(\ker A)^\perp = \mathcal{H}_1^\perp$. $\blacksquare$

#### 15.3 Endogenous momentum acceleration (optional)

$$\beta_{\text{mom}} \equiv 1 - \frac{\lambda_2}{\alpha_n} \;\in\; [0,1)$$
the better the conditioning (the larger the spectral gap ratio), the stronger the momentum — driven entirely by the endogenous spectral assets, with no external hyperparameter.

**⚠ Empirical warning (v1.0)**: the trust region of Theorem 15.1 guarantees only **single-step** boundedness, not monotonicity after momentum accumulation. Empirically, at $\beta_{\text{mom}} = 0.798$ the residual oscillates and crosses zero, and the monotonicity of $\Psi$ fails (see §7, V6 comparison). **Hence momentum is off by default**; if enabled, one must add the backtracking arbitration "retreat whenever the energy rises", and that backtracking criterion itself must still be endogenous (e.g. taking the previous value of $\mathcal{E}_D$ as reference). This is a **known limitation** explicitly stated in specification v1.0.

#### 15.4 Endogenous backtracking line search (v1.3 addition · Phase 3.5b)

Since $\eta_N$ no longer carries a trust region (§15.2 ⚠), single-step overshoot must be caught by **backtracking**. Define the objective functional
$$\Psi(M) \;\equiv\; \tfrac12\,F(M)^2 \;\ge\; 0,$$
and at step $\kappa$ perform a bisection backtracking along the Newton direction $\Delta M$, taking

$$\boxed{\; t_\kappa \;\equiv\; \max\Big\{\, t = 2^{-j},\ j = 0,1,2,\dots \;:\; \Psi\!\left(\max\!\big(m + t\,\Delta M,\; m_{\min}\big)\right) < \Psi(m) \,\Big\} \;}$$

- **Acceptance criterion**: $\Psi$ strictly decreases. Since $\Psi$ is already the residual squared, its absolute decrease suffices; **there is no need to introduce an Armijo constant** (any Armijo parameter would be an external quantity);
- **Termination floor**: $t_\kappa \le 10^{-14}$ or $\|t_\kappa\,\Delta M\| \le 10^{-12} m_{\min}$, at which point `step_dead = True` is set and handed to Operator 17 for adjudication (§17.1/§17.2);
- **Recomputation**: $F(m+t\Delta M)$ reuses the **exactly identical** encoding pipeline of Operator 13 (the same $\alpha_n,\lambda_2,K$), so it is **of the same origin and comparable** with the inner-loop residual, introducing no additional approximation;
- **Relation to the trust region**: $t_\kappa < 1$ is equivalent to one adaptive trust-region retraction, and fits the true curvature better than the fixed $\lambda_2/2$ radius — it is the **executable stand-in** for Theorem 15.1.

**Empirical (bench B2-E02, 14 steps of strictly monotone convergence)**: $t_\kappa = 0.5$ ($\kappa=3,4,5$), $t_\kappa = 0.25$ ($\kappa=12$), and $t_\kappa = 1$ otherwise; after backtracking takes effect the trajectory is strictly monotone, and the V-B independent residual drops from $7.30\!\times\!10^{-1}$ to $1.29\!\times\!10^{-1}$ ($<$ threshold $\gamma = 0.1761$).

> **On "does a line search violate the no-external-parameters principle"**: no, it does not. The backtracking criterion (decrease of $\Psi$) and the quantity compared against ($\Psi$'s own historical value) are both endogenous; the bisection factor $1/2$ is a discretization choice rather than a tunable hyperparameter; and the floor $10^{-14}$ is the floating-point resolution. This is the same paradigm as Operator 16's "bisect along the feasible-cone line to take the largest feasible step", viewed as two projections of one paradigm.

#### Complexity and red lines
$\mathcal{O}(M_K \cdot n_{\text{cg}})$, with $n_{\text{cg}}$ endogenously bounded by the condition number of $A$ ($\kappa(A) \le \kappa_\Omega^2$).
**Hard red line**: when $A$ is singular ($\beta_1 > 0$) the use of direct inversion or dense factorization is **forbidden**; one must first remove the $h$ component before entering CG, otherwise the iteration drifts along the null space and causes numerical escape.

---

### Operator 16: $\mathcal{C}_{\text{hankel}}$, the Spectral-Feasibility Hankel Clamp
**(Spectral Feasibility Hankel Clamp)**

| Item | Specification |
|---|---|
| Topological space | $\mathbb{R}^{K+1} \to \mathcal{K}_{\text{feas}}$ (feasible moment cone) |
| Input | Moment vector recomputed after the update $\boldsymbol{\tau}^{(+)}$ (in power-moment form $\mu_k$) |
| Output | Feasible moments $\tilde{\boldsymbol{\tau}}$; feasibility warning flag |
| Timing position | Phase 3.5 inner loop, immediately after Operator 15 |

#### 16.1 Feasibility criterion (Hausdorff moment problem)

The sequence $\{\mu_k\}_{k=0}^{2K'}$ are the moments of some non-negative measure supported on $[-1,1]$ **if and only if** two Hankel matrices are simultaneously positive semi-definite:

$$H^{(0)}_{ij} \equiv \mu_{i+j} \succeq 0, \qquad H^{(1)}_{ij} \equiv \mu_{i+j} - \mu_{i+j+2} \succeq 0$$

(the second corresponds to $(1-\lambda^2)d\sigma \ge 0$. The Chebyshev moments $\tau_k$ and the power moments $\mu_k$ are mutually inverse through the lower-triangular transformation given by the power expansion of $T_k$, and can be converted locally.)

#### 16.2 Two-stage clamping valve (strictly isomorphic to Operator 10)

$$\mathcal{C}_{\text{hankel}}(\boldsymbol{\mu}) \equiv \begin{cases} \Pi_{\mathcal{K}}\left(\boldsymbol{\mu}\right), & \text{if } \lambda_{\min}\left(H\right) < -\theta_{\text{endo}} \quad \text{(hard interception · spectral projection back to the feasible cone)} \\[6pt] \boldsymbol{\mu} \;+\; \delta_{\text{soft}}\cdot\Pi_{\text{supp}}, & \text{otherwise} \quad \text{(soft contraction · endogenous spectral-support clamping)} \end{cases}$$

- **Endogenous threshold** $\theta_{\text{endo}} \equiv \dfrac{\lambda_2}{\alpha_n}$ (the tolerance is of the same order as the endogenous minimum resolvable scale)
- **Hard interception** $\Pi_{\mathcal{K}}$ (**the canonical main formula · trust-domain rollback**): along the line "previous feasible moments $\boldsymbol{\mu}_{\text{ref}}$ → new moments $\boldsymbol{\mu}$", take the largest feasible step
  $$\Pi_{\mathcal{K}}(\boldsymbol{\mu}) \equiv \boldsymbol{\mu}_{\text{ref}} + t^{\star}\left(\boldsymbol{\mu} - \boldsymbol{\mu}_{\text{ref}}\right), \qquad t^{\star} \equiv \max\left\{ t \in [0,1] \;:\; H^{(0)}, H^{(1)}\big(\boldsymbol{\mu}_{\text{ref}} + t\,\Delta\boldsymbol{\mu}\big) \succeq -\theta_{\text{endo}} I \right\}$$
  Since the feasible set is convex and $\boldsymbol{\mu}_{\text{ref}}$ is an interior point of it, $t^{\star}$ necessarily exists and can be found exactly by bisection. **This is the counterpart of the endogenous trust region in moment space** — the step size is adjudicated by feasibility itself.
- **Soft contraction** $\Pi_{\text{supp}}$: clamp the moment support back to the endogenous interval $[\gamma, 1]$, $\gamma = \lambda_2/\alpha_n$, realized by shift-rescaling (rescaling with respect to $\frac{\lambda-\gamma}{1-\gamma}$)
- **Alternative (spectral projection, fallback only)**: apply the spectral projection $\lambda_{\min}\to\max(\lambda_{\min},0)$ to the Hankel matrices, then recover the moments by anti-diagonal averaging. **Empirically this path converges slowly under alternating projection** (after 8 alternating steps there remains an $\mathcal{O}(10^{-2})$ negative eigenvalue), so it is not adopted as the main formula

#### Theorem 16.1 (feasibility preservation)
After $\mathcal{C}_{\text{hankel}}$, the moment sequence necessarily corresponds to some non-negative measure supported on $[\gamma, 1]$, i.e. **a true spectral shape (in the moment sense) necessarily exists**; moreover $\Pi_{\mathcal{K}}$ is the nearest-point projection onto the feasible cone in the Euclidean norm, so $\|\tilde{\boldsymbol{\mu}} - \boldsymbol{\mu}\|_2$ is minimized.

#### Theorem 16.2 (compatibility with trace sovereignty)
The clamping acts only on the moment-space representation and **does not modify any diagonal entry of $M_\Omega$**, so $\mathrm{Tr}(M_\Omega) \equiv 0$ and local trace sovereignty (Postulate 2) are not violated. The moment deviation introduced by the clamping is **not absorbed locally**; instead it **flows back into Operator 14 as a new residual** and re-enters the routing — guaranteeing closed-loop self-consistency and forbidding the silent discarding of infeasible components.

#### Complexity and red lines
$\mathcal{O}(K^3)$, since $K \le K_{\text{cap}} = \mathcal{O}(\ln N_K)$ and $N_K = \mathcal{O}(1)$, so the whole is at the **constant order**.
**Hard red line**: when $K_{\text{cap}}$ truncates, the Hankel criterion is only a **necessary condition** (high-order moments are missing); in this case Operator 16 must output the "feasibility undetermined" warning flag and must not claim verification.

---

### Operator 17: $\mathcal{A}_{\text{sol}}$, the Solution-Branch Betti Audit and Termination Arbiter
**(Solution-Branch Betti Audit & Termination Arbiter)**

| Item | Specification |
|---|---|
| Input | Three-component norm sequence, $\beta_0,\beta_1$, adaptive spectral window $\tau(s)$ (Operator 9) |
| Output | Verdict: continue / trigger topological stitching / declare solved / output obstruction certificate |
| Timing position | Phase 4 (same layer as Operators 8 and 9, but before them) |

#### 17.1 Two-level endogenous convergence criteria (v1.1 · relative, dimensionless)

Taking the first-step residual $\|r_0\|_2$ as the endogenous reference scale, define a unified relative tolerance $\epsilon_{\text{endo}} \equiv \dfrac{\lambda_2}{\alpha_n}\,\|r_0\|_2$. The solution mode is chosen according to the user's needs:

| Mode | Enabling condition | Criterion | Monitored degrees of freedom |
|---|---|---|---|
| **Exact solution** | $\beta_1 = 0$, or the user explicitly requires it | $\|D\phi\|, \|C^T\psi\| \le \epsilon_{\text{endo}}$ and $\|h\| \le \epsilon_{\text{endo}}$ | $m_g$ |
| **Homological solution** (default) | $\beta_1 > 0$ | **only** $\|h\|_2 \le \epsilon_{\text{endo}}$ | $\beta_1$ |

**In the homological-solution mode no requirement is placed on the gradient/curl components** — they are absorbed naturally by Operators 6/7 in subsequent pulses (Definition 3.1). This brings two benefits:
1. **the monitored dimension drops from $m_g$ to $\beta_1$**, greatly reducing the degrees of freedom tracked by the convergence decision;
2. upon reaching a homological solution one may immediately proceed to Operator 18 to realize the graph structure, **without waiting for the exact components to fully dissolve**.

**Properties**: generated entirely from the endogenous spectral assets and the first-step residual, **dimensionless and with no external tolerance parameter**, and automatically adapting to the overall magnitude of the equation.

**⚠ Empirical qualification (v1.1): when the homological-solution criterion really terminates early**

Since $r(M) = F(M)\,\nabla F(M)$ and $h(M) = F(M)\,\Pi_{\mathcal{H}_1}\nabla F(M)$, the ratio of the two,
$$\rho_h(M) \;\equiv\; \frac{\|h(M)\|}{\|r(M)\|} \;=\; \frac{\|\Pi_{\mathcal{H}_1}\nabla F\|}{\|\nabla F\|}$$
is **independent of $F(M)$**. Empirically, on a test complex with $\beta_1 = 1$, $\rho_h$ is stable at $\approx 0.945$ for almost all initial values (min $0.9446$ / max $0.9503$ / mean $0.9473$), i.e. **the harmonic fraction of the residual is approximately a constant that does not change with the iteration**.

Corollaries (important):
1. the harmonic channel **cannot be compressed independently**, and can only vanish together with $\|r\|\to 0$;
2. therefore when $\rho_h > \gamma$ the homological-solution criterion **coincides** with the exact-solution criterion at the convergence point, and the two-level criteria produce no bifurcation point (empirically V15 "no bifurcation point");
3. the necessary and sufficient condition for the homological-solution criterion to truly terminate early is $\rho_h(M_0) \le \gamma$ — i.e. the initial value's harmonic fraction is itself below the endogenous minimum resolvable scale;
4. if $\rho_h$ is identically $\mathcal{O}(1)$ (e.g. $0.945$ here), then $\|h\| \le \epsilon_{\text{endo}}$ can only be attained by an overall decrease of $\|r\|$, and **in this case there is no homological solution "earlier than the exact solution"** — the full iteration must be run; if the iteration stalls at $\|h\| > \epsilon_{\text{endo}}$ while the gradient/curl have already met the criterion, then OBSTRUCTION is declared and it is handed to Operator 9 for Betti stitching.

> This conclusion clarifies the true benefit boundary of "homological solutions": their value is **not faster convergence, but relaxing the "acceptable solution" from $\{r=0\}$ to $\{h=0\}$**, so that when the equation is intrinsically not exactly solvable (topologically obstructed) one can still deliver a graph structure correct in the homological sense.

> **⚠ v1.3 correction (exposed by the 50-equation stress test): `OBSTRUCTION` is a structural false-positive branch.**
> From the identity $r = F\nabla F$, $\rho_h = \|h\|/\|r\|$ is independent of $F$ (empirically $\approx 0.95$ above). Hence "$\|h\| \le \epsilon_{\text{endo}}$" is equivalent to "$\|r\| \le \epsilon_{\text{endo}}/\rho_h$", while "the exact part has converged" corresponds to "$\|r\| \le \epsilon_{\text{endo}}$". The criterion band between the two criteria is
> $$\frac{\epsilon_{\text{endo}}}{\rho_h} \;<\; \|r\| \;\le\; \frac{\epsilon_{\text{endo}}}{\rho_h}\cdot\frac{1}{\gamma} \qquad (\text{here} \approx 4.3\,\epsilon_{\text{endo}}),$$
> **as wide as $1/\gamma$ times**. Any $F$ falling into this band simultaneously satisfies "exact part converged, harmonic part not converged", and is thereby **misjudged as a topological obstruction** — yet the problems inside this band are in fact well-posed and solvable.
> **Consequence**: a well-posed problem is handed to **Operator 9, which changes $\beta_1$**, directly violating the red line "$\Delta\beta_1 \equiv 0$ hard lock" of §17.3 (empirically bench B2-E02).
> **Correction**: declaring `OBSTRUCTION` must **additionally require the condition "the update direction is exhausted"** — i.e. the $t_\kappa$ of §15.4 hitting the floor (`step_dead`), or $\|\Delta M\|\to0$. Only when the residual cannot move even in a direction is it admitted to be a genuine topological obstruction; otherwise it is invariably judged `CONTINUE` (continue iterating) or `STALLED` (numerical stall, no topological change triggered).
> **Verification**: after suppressing this false positive, only 2 of the 50 equations still fell into the "tautology" channel (see the `exhausted` condition of §17.2); with that closed, **all 50/50 are SOLVED**.

#### 17.2 Verdict routing table (v1.3 revision)

Let `below` denote "all three channels meet the criterion", `exhausted` denote "the residual decrease has been wrung dry", `step_dead` denote "the update direction is exhausted (the §15.4 line search hit the floor)", `pert` denote "the exact components ($D\phi,C^T\psi$) meet the criterion", and `harm` denote "the harmonic component meets the criterion".

| Condition | Verdict | Action |
|---|---|---|
| `below` **and** (`exhausted` **or** `step_dead`) | **SOLVED** | Hand to Operator 18; output $M_\Omega^\star$ and $\sigma^\star$ (both exact solutions and homological solutions go this way; when the residual is exact it is registered for absorption by Operators 6/7) |
| not `below`, and the update direction is not exhausted | **CONTINUE** | $\kappa \leftarrow \kappa+1$, return to Operator 15 |
| `step_dead`, and `pert` and $\lnot$`harm` (**only** the harmonic part remains) | **OBSTRUCTION** | Hand to Operator 9 to perform Betti stitching (changes $\beta_1$), restart the inner loop |
| `step_dead`, and not "only the harmonic part remains" | **STALLED** (numerical stall) | Report a numerical warning, **do not trigger a topological change** (protecting the $\Delta\beta_1\equiv0$ red line) |
| $\|h\|$ still does not decrease after $\tau(s)$ stitching steps | **UNSOLVABLE** | Output the obstruction certificate $h$, terminate and warn |

**The `exhausted` (wrung-dry) condition (v1.3 addition)**:
$$|F_\kappa| \;\ge\; (1-\gamma)\,|F_{\kappa-1}|,$$
i.e. the residual decrease of the previous step is below the relative fraction $\gamma$ — the information carried by the Newton direction has been wrung dry. It stands alongside "$\|r\|\le\epsilon_{\text{endo}}$" and together they constitute the criterion of `SOLVED`.

> **Why this condition must be added**: the V-B independent-residual verification and the termination criterion **take the same threshold $\epsilon_{\text{endo}}$**. If one terminates merely on "first crossing $\epsilon_{\text{endo}}$", then any instance that happens to fall on either side of the threshold within the $1/\gamma$ band (empirically B4-E02 $=0.1726$, B5-E02 $=0.1787$ vs $\gamma = 0.1761$) will be judged "solved", but the independently recomputed residual is still above the threshold and V-B FAILs — **the verification degenerates into a tautology**. After adding `exhausted`, the V-B of 49 empirical equations falls to $10^{-14}\sim10^{-9}$, and B2-E02's V-B drops from $7.30\!\times\!10^{-1}$ to $1.29\!\times\!10^{-1}$.

**The `step_dead` (direction-exhausted) condition (v1.3 addition)**: see the line-search floor of §15.4. It is a necessary condition for `OBSTRUCTION` (§17.1 ⚠), and also one of the sufficient conditions for `SOLVED` (near the threshold, being unable to move in any direction counts as converged).

**Verdict priority**: Operator 17 must execute before Operators 8/9 (first in Phase 4), because its verdict determines whether Operator 9's stitching is needed — if the conservative clamping were done first, it might flatten the topological information awaiting stitching in advance.

#### 17.3 Multi-branch solution audit

The multiple fixed points of the equation correspond to multiple basins of attraction of the residual manifold, with the number of branches counted by $\beta_0$. Throughout the inner loop **$\Delta\beta_1 \equiv 0$ is hard-locked** (unless Operator 9 actively stitches), preventing the iteration from spuriously proliferating/merging solution branches (reusing Operator 9's unique-ordering arbitration chain $\mu_{\text{trace}} \to \text{blocking gate} \to \mathcal{O}_{\text{stitch\_dual}}$).

#### 17.4 Handover to Operator 18

Once solved (whether exact or homological), the result is invariably handed to **Operator 18 $\mathcal{R}_{\text{homo}}$** to complete the graph-structure realization. Operator 17 is responsible only for the verdict, not for the realization.

---

### Operator 18: $\mathcal{R}_{\text{homo}}$, the Homological Solution Realizer (v1.1 addition)
**(Homological Solution Realizer)**

| Item | Specification |
|---|---|
| Topological space | $\mathcal{S}_{\text{hom}} \subset \mathbb{R}^{m_g} \;\to\; M_\Omega^\star$ (spin-adjacency structure) |
| Input | The graph $M$ judged "solved", the three residual components, the moment vector $\boldsymbol{\tau}$, the Fiedler vector $v_2$ |
| Output | Canonical homological representative $M^\star_{\text{canon}}$; spectral shape $\sigma^\star$; homological-distance certificate |
| Timing position | Last in Phase 4 (executed once after Operator 17 judges "solved") |

#### 18.1 The five realization steps

1. **Homology-class confirmation**: verify $\|h\| \le \epsilon_{\text{endo}}$. If it does not hold, flow back to Operator 9; if it holds, record the current homology class $[M]$.
2. **Registration of the exact residual** (do not discard!): register the remaining exact residual $D\phi + C^T\psi$ as an **amount to be absorbed** by Operators 6/7, to be consumed in a subsequent unified pulse. The registered amount itself constitutes the error budget of the solution.
3. **Canonical-representative selection**: within the homology class take the one minimizing the Dirichlet energy as the output:
   $$M^\star_{\text{canon}} \;\equiv\; \arg\min_{M' \in [M]} \mathcal{E}_D(M')$$
   Practical implementation: perform energy descent along the $\mathcal{H}_1^{\perp}$ direction (i.e. the update direction of Operator 15) until $\Delta\mathcal{E}_D \approx 0$; Theorem 15.3 guarantees that this direction does not leave the homology class.
4. **Spectral-shape reconstruction** ($\mu_{\text{realize}}$ micro-operator): invert the spectral density from the moment vector. Prefer Stieltjes inversion (§13.4):
   $$\rho^\star(\hat\lambda) = \frac{1}{\pi}\,\mathrm{Im}\!\left[ \sum_k c_k(\hat\lambda + i\gamma)\,\tau_k \right], \qquad \text{imaginary offset endogenously } \varepsilon_{\text{endo}} = \gamma$$
   In the degenerate case (or when $K_f$ is insufficient), switch to the direct Chebyshev expansion $\rho^\star \approx \sum_k \tau_k T_k$ and apply a non-negativity clamp.
5. **Sign and spin assignment**: use Operator 3's Fiedler sign gate to assign the spin sign inversely, $\Gamma(k,j) = \mathrm{sgn}(v_2(j))$, then invert the edge weights via Operator 5, $W_e = \exp(\alpha_n/c_e) - 1$, and substitute into Operator 4's degree relation for verification.

#### Theorem 18.1 (local well-definedness of the canonical representative)

Linearizing in a neighborhood of the homological solution $M^\star$, one has $A \succ 0$ along $\mathcal{H}_1^{\perp}$ ($A$ being Operator 15's weighted Hodge Laplacian, whose kernel is exactly $\mathcal{H}_1$), so $\mathcal{E}_D$ is strictly convex on $\mathcal{H}_1^{\perp}$ ⟹ $\arg\min\mathcal{E}_D$ **exists locally and is unique**.

**Note**: global uniqueness does not hold — different homology classes ($h \neq 0$) are not comparable; this is precisely the meaning of Theorem S5, "uniqueness holds only in the sense of homology classes".

#### 18.2 Output certificates

Operator 18 must output the following three items together with the solution, as a credibility statement about the solution:

| Certificate item | Definition | Semantics |
|---|---|---|
| Homological residual $\|h\|_2$ | the norm of the harmonic projection of the residual | $=0$ ⟹ the homological solution holds |
| Homological distance $d_{\text{hom}}(M^\star, M_{\text{init}})$ | $\|h(M^\star) - h(M_{\text{init}})\|_2$ | how far it has moved from the initial value (in the topological sense) |
| Exact-residual budget $\|D\phi + C^T\psi\|_2$ | the amount to be absorbed by Operators 6/7 | the residual error of the exact solution |

#### Complexity and red lines
$\mathcal{O}(M_K \cdot n_{\text{cg}} + N_K^2)$, executed only once.
**Hard red lines**:
- the reconstructed spectral density must be non-negative, else it is re-clamped by Operator 16 (outputting a negative spectral density is forbidden);
- when $\beta_1 = 0$ the homological-solution set degenerates to the whole space (degeneracy warning, §2-bis), in which case **the canonical-representative criterion (minimum Dirichlet energy) is the sole basis for selection**, and step 3 must not be omitted.

---

## 4. Extended Pipeline Timing (embedded into the Version 18.0 four-phase pulse)

A new **Phase 3.5: spectral-shape equation solving inner loop (Solve Inner Loop, step $\kappa$)** is added, located after Phase 3 field closure and before Phase 4 conservation. The solving inner loop **does not change the advancement of the structural pulse $s$**; it merely performs sub-step iterations inside a unified pulse, so all network Actors still advance in strict lockstep.

| Phase | Executed operators | Input | Attributes |
|---|---|---|---|
| **Phase 1** | Op4 → Op6 → **Op13** | $M_\Omega(s)$, $(\alpha_n,\lambda_2)$ | Op13 reuses Op6's Lanczos subspace, **zero extra spectral decomposition**; outputs the moment vector and sensitivity set |
| **Phase 2** | Op5 → Op2 → Op3 | unchanged | unchanged |
| **Phase 3** | Op7 → $\mu_{\text{betti}}$ → **Op14** | closed manifold + equation $\mathcal{F}$ | Op14 executes jointly with the half-step $B_{s+1/2}$; three-component residual routing, conservative pairing (Theorem 14.1) |
| **Phase 3.5** (new) | **Op15 → line search (3.5b) → Op16 → criterion** | $\mathbf{g}_M, h, A$ | Endogenous quasi-Newton single-line closed form; **backtracking line-search sub-step** (§15.4); Hankel feasibility clamping; $\kappa \leftarrow \kappa+1$ |
| **Phase 4** | **Op17** → Op8 → Op9 → compensation → **Op18** | three-component norms, $\beta_0,\beta_1,\tau(s)$ | Op17's verdict takes priority: obstruction → Op9 stitching; solved (exact/homological) → **Op18 realization**; then Op8/Op9 conservation |

**Multi-shard timing supplement**: the Op13 of $p$ shards may be executed **in parallel** in Phase 1 (each shard is independent, with no synchronization dependency), but they must use the **same $\alpha_n$** (§14.4); residual synthesis (Op14) is performed centrally in Phase 3, since the Hodge decomposition must be completed in one shot over the global edge space and shards may not project separately and then add (the sum of shard projections $\neq$ the global projection, unless the shards' edge sets are orthogonal).

**Nesting relation of the solving pulses**: the outer unified pulse $s$ advances the evolution of the graph structure, while the inner solving pulse $\kappa$ converges the equation under the same structure. If $\kappa$ exceeds the endogenous spectral window $\tau(s)$ and still has not converged, it is handed to Op17 for adjudication (continue / stitch / declare unsolvable).

---

## 5. Computational-Complexity Invariants Comparison Table

| Operator | Core operations | Complexity | Notes |
|---|---|---|---|
| Op13 $\mathcal{E}_{\text{mom}}$ | Chebyshev three-term recurrence + boundary-column quadratic forms | $\mathcal{O}(N_K M_K K)$ | both $N_K, K$ endogenously clamped by the local horizon, effectively $\mathcal{O}(1)$; no eigendecomposition |
| Op14 $\mathcal{R}_{\text{hodge}}$ | sensitivity synthesis + two pseudo-inverse projections | $\mathcal{O}(M_K K + M_K + f)$ | the pseudo-inverses reuse Op6/Op10's $\mathcal{O}(1)$ facilities |
| Op15 $\mathcal{N}_{\text{endo}}$ | Sherman-Morrison closed form + one CG | $\mathcal{O}(M_K n_{\text{cg}})$ | single-line closed form, no dense factorization; $n_{\text{cg}}$ endogenously bounded by $\kappa(A)$ |
| Op16 $\mathcal{C}_{\text{hankel}}$ | $K\times K$ Hankel spectral projection | $\mathcal{O}(K^3)$ | $K = \mathcal{O}(\ln N_K)$, constant order |
| Op17 $\mathcal{A}_{\text{sol}}$ | verdict (the homological-solution mode monitors only $\beta_1$ degrees of freedom) | $\mathcal{O}(M_K + f)$ | reuses Op9's arbitration chain |
| Op18 $\mathcal{R}_{\text{homo}}$ | canonical-representative selection + Stieltjes spectral reconstruction + Fiedler sign assignment | $\mathcal{O}(M_K n_{\text{cg}} + N_K^2)$ | executed once only upon declaring a solution |

**Overall multi-shard overhead**: $\mathcal{O}\!\left(p\,M_K K\right)$ ($p$ being the number of coupled shards); parallelizable within Phase 1, serial from Phase 3 onward.

**Global property**: the extension layer introduces no $\mathcal{O}(n^3)$ or globally synchronized decomposition operation; all operators are at the local constant order in the thermodynamic limit, consistent with Version 18.0's complexity red line.

---

## 6. Methodology Summary: the Six-Step Solving Method

For "an equation formed by unknown spectral shapes", the standard solving flow is:

1. **Encoding** (Op13): encode each unknown spectral shape $\sigma_\nu$ as a Chebyshev moment vector $\boldsymbol{\tau}^{(\nu)}$. For polynomial kernels use $K = \lceil\alpha_n/\lambda_2\rceil$; **for non-polynomial kernels use the tail-sum criterion $K_f$** ($\sum_{k>K}|c_k| \le \gamma\max|c|$, §13.4 v1.2); **whenever kernel expansion is used, the zero mode must be stripped first** (§13.5) — *turn functions into finite vectors*.
2. **Algebraization** (Definition 1.2): turn the equation $\mathcal{F}(\sigma)=0$ into an equation in moment space. **Coupled multiple spectral shapes** manifest as a block Jacobian $J \in \mathbb{R}^{q\times p(K+1)}$, with coupling terms falling automatically into the block structure via the product rule — *turn functional equations into algebraic equations*.
3. **Routing** (Op14): the residual is synthesized via the shard embeddings $\Xi_\nu$ and the sensitivity vectors into a global 1-chain, and a Hodge three-component decomposition is performed — *turn the residual into topological components*.
4. **Inversion** (Op15 → 3.5b → 16): the endogenous quasi-Newton single-line closed form updates the edge weights, **the backtracking line search (§15.4) contracts the step to guarantee $\Psi$ strictly decreases**, and the Hankel clamp guarantees the spectral feasibility of the solution — *iterate to convergence in graph space*.
5. **Verdict** (Op17): **the default homological-solution criterion $\|h\| \le \epsilon_{\text{endo}}$**, plus the `exhausted` (wrung-dry) or `step_dead` (direction-exhausted) conditions (§17.2 v1.3); only when **the direction is exhausted and only the harmonic part remains** is a topological obstruction declared and the result handed to Operator 9 for stitching; otherwise the verdict is "continue" or "numerical stall" — *deliver a solution or prove it does not exist*.
6. **Realization** (Op18): within the homology class take the canonical representative minimizing the Dirichlet energy, reconstruct the spectral density by Stieltjes inversion, and assign spins via the Fiedler sign gate — *output the graph structure + three credibility certificates*.

**The three "no's" of this methodology**:
- **No whole-network eigendecomposition** (Postulate 1; closed walks + three-term recurrence throughout)
- **No external parameters introduced** (Postulate 3; all thresholds are generated endogenously from $\lambda_2/\alpha_n$)
- **No touching of shard diagonal entries** (Postulate 2; curl cancellation is performed only in the edge/cycle space)

**Semantics of the solution (v1.1)**: the default output is a **homological solution** ($h = 0$, i.e. the residual is exact) rather than an exact solution ($r = 0$). The difference between the two is measured by $\|D\phi + C^T\psi\|$, written into the certificate as the "exact-residual budget" and handed to Operators 6/7 for absorption in subsequent pulses. Uniqueness **holds only in the sense of homology classes** (Theorem S5).

---

## 7. v1.0 Verification Protocol

| # | Verification item | Expectation | Basis |
|---|---|---|---|
| V1 | Moment-encoding correctness: $\tau_k$ computed by recurrence vs. `eigvalsh` direct computation | relative error $< 10^{-10}$ | Theorem S1 |
| V2 | Sensitivity closed form vs. central differences | relative error $< 10^{-6}$ | Eq. 13.3 |
| V3 | Hodge orthogonality: $\langle D\phi, C^T\psi\rangle = \langle D\phi, h\rangle = \langle C^T\psi, h\rangle = 0$ | $\approx 0$ | Theorem S3 |
| V4 | Harmonic criterion: $D^T h = 0$ and $C h = 0$; $\dim\mathcal{H}_1 = \beta_1 = \nu - \mathrm{rank}(\partial_2)$, $\nu = m_g-n+\beta_0$ | holds (numerical rank) | Theorem S3 + terminology convention |
| V5 | Monotone decrease of the residual for a solvable equation (e.g. $\tau_2 - c = 0$) | $\|r_{\kappa+1}\| \le \|r_{\kappa}\|$ | Theorem 15.2 |
| V6 | Dirichlet energy non-increasing | $\Delta\mathcal{E}_D \le 0$ | Theorem 15.2 |
| V7 | Update-direction orthogonality: $\Delta M \perp \mathcal{H}_1$ | $\langle \Delta M, h\rangle \approx 0$ | Theorem 15.3 |
| V8 | Both matrices positive semi-definite after Hankel clamping | $\lambda_{\min}(H^{(0)}), \lambda_{\min}(H^{(1)}) \ge -\epsilon$ | Theorem 16.1 |
| V9 | Topological-obstruction test case: requiring a nonzero harmonic residual on a $\beta_1 = 0$ graph | Op17 correctly warns and $\|h\|$ does not decrease | Theorem S3 |
| V10 | Closed-flow conservation: taking $E = D\varphi$ (automatically satisfying $CE=0$), after injecting $\psi$, $\Delta(E^T C^T B)$ | $= 0$ | Theorem 14.1 |
| V11 | Counterexample comparison: taking a non-closed flow with $CE \neq 0$ and injecting likewise | $\Delta \neq 0$, confirming the timing necessity | Corollary 14.1 note |

### v1.1 new verification items (coupled multiple spectral shapes / non-polynomial kernels / homological solutions)

| # | Verification item | Expectation | Basis |
|---|---|---|---|
| **V12** | Coupled multiple spectral shapes: two-shard equation $\tau_2^{(1)}\tau_2^{(2)} - c = 0$, block Jacobian + shard embedding $\Xi_\nu$ | residual decreases monotonically and a solution is adjudicated | §14.4 |
| **V7b** | Equation scale invariance: $\Delta M$ must be invariant under $F\to sF$ ($s=1,10,100$) | new form relative offset $<10^{-8}$; the v1.0 old form deviates significantly (scale-dependent) | Theorem 15.1' |
| **V13** | Non-polynomial kernel $\ln\hat\lambda$: Chebyshev coefficient sum $\mathbf{c}^T\boldsymbol{\tau}^{\text{red}}$ vs. reduced spectral integral (zero-mode stripping first) | empirical error $\le$ Bernstein tail bound $\sum_{j>K_f}\|c_j\|$, and $\le \gamma\|\text{exact}\|$ | §13.4 / §13.5 |
| **V14** | Bernstein ellipse rate: empirical $\ln$-kernel coefficient decay rate vs. $\rho = \frac{1+\gamma}{1-\gamma}+\sqrt{\left(\frac{1+\gamma}{1-\gamma}\right)^2-1}$ | empirical decay rate of the same order as the theoretical $\rho$ | Theorem 13.2 |
| **V15** | Homological solution vs. exact solution: the same equation on a $\beta_1>0$ complex under the two criteria | homological-solution step count $\le$ exact-solution step count, and $\|h\|$ meets the criterion | Definition 3.1 |
| **V16** | Homological distance: two different realizations $M_1^\star\neq M_2^\star$ that are homologically equivalent (must share the same set of locked scales + locked-shell rescaling, and both be judged SOLVED) | $d_{\text{hom}}\le\epsilon_{\text{endo}}$ while $\|M_1^\star - M_2^\star\| \gg 0$ | Definition 3.2 / Theorem S5 / §13.6 |
| **V17** | Degeneracy warning: on a $\beta_1 = 0$ complex, $\|h\| \equiv 0$ holds for any graph | the homological-solution criterion fails, and the canonical-representative criterion must be used | §2-bis |
| **V18** | Canonical representative: unique within a homological equivalence class by minimum Dirichlet energy | outputs a unique representative + three certificates | Operator 18 / Theorem 18.1 |

### v1.0 empirical results (n=12 ring + chord-edge complex, m_g=24)

The actual run output of the reference implementation `Operator_13_18_P.py` (upgraded from v1.0's `Operator_13_17_P.py`) (12/12 passing, including V7b):

| # | Verification item | Empirical | Conclusion |
|---|---|---|---|
| V1 | Moment-encoding recurrence vs. direct eigendecomposition | $1.86\times10^{-15}$ | PASS |
| V2 | Sensitivity closed form vs. central differences | $3.57\times10^{-10}$ | PASS |
| V3 | Hodge orthogonality + Pythagorean identity | $2.82\times10^{-15}$ | PASS |
| V4 | Harmonic criterion $\lVert D^{Th}\rVert,\lVert Ch\rVert$ | $1.10\times10^{-14}$ | PASS |
| V5 | Monotone decrease of the residual for a solvable equation | $F:\ 7.16\!\times\!10^{-2}\to3.83\!\times\!10^{-3}$ (4 steps) | PASS |
| V6 | Objective functional $\Psi$ non-increasing | $2.57\!\times\!10^{-3}\to7.32\!\times\!10^{-6}$ | PASS |
| V7 | $\langle\Delta M,h\rangle$ | $4.42\times10^{-16}$ | PASS |
| V8 | Feasibility recovery after Hankel clamping | $-3.73\!\times\!10^{-1}\to-1.0\!\times\!10^{-9}$ ($t^\star=0.099$) | PASS |
| V9 | Inversion driven by harmonic residual | $\lVert\Delta M\rVert = 0$ (completely uneliminable) | PASS |
| V10 | Closed flow $E=D\varphi$ pairing conservation | $6.29\times10^{-17}$ | PASS |
| V11 | Non-closed-flow counterexample | $-4.12\times10^{-1}$ (significantly nonzero) | PASS |

**The two complexes compared** (this is the key to V9 holding):

| Complex | Face count $f$ | $\mathrm{rank}(\partial_2)$ | $\nu$ | $\beta_1$ | Equation solvability |
|---|---|---|---|---|---|
| Closed complex (adding the chord-edge cycle as the 13th face) | 13 | 13 | 13 | **0** | residual entirely in gradient + curl, converges in 4 steps |
| Holed complex (only 12 triangles) | 12 | 12 | 13 | **1** | the harmonic component cannot be eliminated, requiring Operator 9 stitching |

**Two engineering points exposed empirically** (already written into the implementation):
1. **Endogenous momentum overshoots**: at $\beta_{\text{mom}}=0.798$ the residual oscillates (V6 monotonicity fails), so it is off by default; if enabled it must be paired with backtracking (this corroborates that the trust region of Theorem 15.1 guarantees only single-step boundedness, not monotonicity after momentum accumulation).
2. **Hankel clamping should take the "rollback" path rather than "alternating projection"**: after 8 single-step alternating projections there still remains a negative eigenvalue of $-6.7\times10^{-2}$; switching to the bisection rollback along the line "previous feasible moments → new moments" (the largest feasible step on the convex set), it recovers to $-10^{-9}$ in one step. The former does not converge; the latter guarantees the output is feasible.

### v1.1 empirical results (same complex family, reference implementation `Operator_13_18_P.py`, 12/12 + 7/7 all passing)

**The v1.0 items are comprehensively sped up after switching to the Newton normalization** ($n=12$ closed complex, $\alpha_n=7.229$, $\lambda_2=1.456$, $\gamma=0.2014$, $K=5$):

| # | Verification item | v1.0 empirical | v1.1 empirical | Conclusion |
|---|---|---|---|---|
| V5 | Monotone decrease of the residual for a solvable equation | $7.16\!\times\!10^{-2}\to3.83\!\times\!10^{-3}$ (4 steps, **non-monotone**) | $7.16\!\times\!10^{-2}\to2.71\!\times\!10^{-3}$ (**2 steps, strictly monotone**) | PASS |
| V6 | Objective functional $\Psi$ non-increasing | $2.57\!\times\!10^{-3}\to7.32\!\times\!10^{-6}$ | $2.57\!\times\!10^{-3}\to3.68\!\times\!10^{-6}$ (monotonicity restored) | PASS |
| V7b | Equation scale invariance $F\to sF$ | — | new form $\|\Delta M\|$ identically $4.881435483\times10^{-2}$ ($s=1,10,100$, relative offset $8.4\times10^{-15}$); old form $3.31\times10^{-1}\to3.57\times10^{-3}\to3.57\times10^{-5}$ (spanning 4 orders of magnitude) | PASS (old form FAIL) |

**v1.1 new items, empirically**:

| # | Verification item | Empirical | Conclusion |
|---|---|---|---|
| V12 | Coupled multiple spectral shapes $\tau_2^{(1)}\tau_2^{(2)}-c=0$ ($p=2$) | $F:\ -2.290\!\times\!10^{-3}\to+1.039\!\times\!10^{-4}$ (2 steps, monotone) | PASS |
| V13 | $\ln\hat\lambda$ expansion (with zero-mode stripping) | $\xi_0=-1.5045$, $\rho=2.6286$; error vs. order $1.50\!\times\!10^{-2}(K{=}1)\to1.61\!\times\!10^{-2}(K{=}2)\to4.39\!\times\!10^{-3}\to1.61\!\times\!10^{-4}\to5.71\!\times\!10^{-5}(K{=}5)\to2.40\!\times\!10^{-7}(K{=}8)\to7.82\!\times\!10^{-10}(K{=}16)$; the v1.2 tail-sum criterion gives $K_f=2$, empirical error $1.61\!\times\!10^{-2}\le$ tail bound $5.19\!\times\!10^{-2}$ and $\le$ endogenous tolerance $\gamma\|\text{exact}\|=9.81\!\times\!10^{-2}$ | PASS |
| V14 | Bernstein ellipse rate | empirical $\rho_{\text{fit}}=3.129$ vs. theoretical $\rho=2.629$, ratio $1.19$ | PASS |
| V15 | Two-level criteria ($\beta_1=1$) | homological solution 2 steps / exact solution 2 steps, **no bifurcation point** (due to $\rho_h\approx0.947>\gamma$, see §17.1 qualification) | PASS |
| V16 | Homological distance | $\|M_a^\star-M_b^\star\|=7.53\!\times\!10^{-1}$, $d_{\text{hom}}=3.42\!\times\!10^{-3}\le\epsilon_{\text{endo}}$; $\rho_h$ scan mean $0.9473$ | PASS |
| V17 | $\beta_1=0$ degeneracy warning | $\|h\|$ of 5 random residuals $\in[6.5,14.9]\times10^{-15}$, homological-solution set = whole space | CONFIRMED |
| V18 | Canonical representative (minimum Dirichlet energy) | $E_a=3.05\times10^{-9}$ wins, outputs three certificates | PASS |

**The four points exposed empirically by v1.1** (all written back into the specification body):
1. **Newton normalization replaces $1/(1+q)$** (§15.2) — $1/(1+q)$ lacks equation scale invariance, and the convergence rate depends on the writing magnitude of $F$, empirically 175 times slower.
2. **The endogenous scale must be locked** (§13.6) — the sensitivity does not differentiate with respect to $\alpha_n$, so refreshing $\alpha_n$ step by step makes $F$ jump and destroys the monotonicity of $\Psi$; switching to "refresh triggered by drift $>\gamma$" gives strictly monotone convergence in 2 steps.
3. **Singular kernels must be zero-mode-stripped first** (§13.5) — the singularity of $\ln$ in the shifted variable is exactly the Bernstein singularity $\xi_0$, and the zero mode falls just outside the support; subtracting its moment contribution suffices, with no eigendecomposition.
4. **The benefit boundary of the homological-solution criterion** (§17.1) — $\rho_h=\|h\|/\|r\|$ is independent of $F$ and empirically approximately the constant $0.947$, so the harmonic channel cannot be compressed independently; the value of homological solutions is to **relax the acceptable solution set** $\{r=0\}\to\{h=0\}$, not to accelerate convergence.

### v1.2: the "10 random equations" stress test (`bench_random_equations.py`, 10/10 passing)

Equation family: E01 $\tau_3$ / E02 $\sum a_k\tau_k^2$ (single spectral shape); E03 two-shard multiplication / E04 weighted linear mixture / E05 three-shard cross coupling; E06 $\ln$ / E07 $\sqrt{\ }$ / E08 Stieltjes (non-polynomial kernels); E09 polynomial $\parallel\exp$ / E10 multiplication $+\ln$ (cross-shard mixed kernels). The target constants are endogenously constructed by the intermediate-value theorem $c=(1-u)G(m_a)+uG(m_b)$, $u\sim U(0.15,0.85)$ — guaranteeing randomness and well-posedness.

**Verification independent of the pipeline**: `F(τ)` uses the Op13 three-term recurrence, while **verification uses the exact `eigvalsh` spectrum** (SRE forbids eigendecomposition inside the operators, so `eigh` can only exist as a terminal ground-truth benchmark). Six items:

| Item | Content | Empirical range |
|---|---|---|
| V-A | moment cross $\max\|\tau_{\text{pipe}}-\tau_{\text{eig}}\|$ | $5.3\!\times\!10^{-16}\sim2.1\!\times\!10^{-15}$ |
| V-B | independent residual $\|G_{\text{eig}}(M^\star)-c\|/\|G(m_a)-c\|$ (threshold $\gamma$) | $4.9\!\times\!10^{-3}\sim1.7\!\times\!10^{-1}$ |
| V-C | kernel fidelity: expansion vs. exact spectral integral (threshold $\gamma$) | $1.1\!\times\!10^{-3}\sim1.4\!\times\!10^{-1}$ |
| V-D | legality: positive edge weights, $\lambda_2>0$, Hankel feasible | E01/E09 are second-tier verdicts (see the §13.6 table) |
| V-E | $\Psi=F^2/2$ non-increasing | 10/10 |
| V-F | Operator 18's three certificates | 10/10 |

**The three points thereby exposed and corrected** (see §13.4/§13.5/§13.6 for details): the $K_f$ criterion changed from single term to tail sum; zero-mode stripping upgraded from exclusive-to-singular-kernels to a general requirement; for multiple shards $\alpha_n$ and $\lambda_2$ must be frozen simultaneously. Incidentally clarified: a frozen scale **explicitly destroys** the rescaling gauge redundancy, so the shell rescaling of §13.6 cannot be applied to an already-obtained solution.

**The accuracy cost of non-polynomial kernels is explicitly priced** (E09's $K$-sweep): $K{=}2{:}1.1\!\times\!10^{-3}$, $K{=}4{:}1.2\!\times\!10^{-5}$, $K{=}6{:}2.7\!\times\!10^{-8}$, $K{=}8{:}3.4\!\times\!10^{-11}$. Reaching the $\gamma$ level requires $K\ge2$, and the $10^{-6}$ level requires $K\ge6$.

### v1.3: the "10 problem types × 5 groups = 50 equations" stress test (`bench_random_equations.py`, 50/50 passing)

The 10 random equations of v1.2 are generalized to **10 problem types × 5 random instances = 50**: the types E01–E10 are unchanged, and each group uses an independent seed block (`SEED_BASE = 20260924`, `case_seed(b,i) = SEED_BASE + b*1000 + i`; $b=0$ degenerates to v1.2's historical seeds, guaranteeing reproducibility). The target constants are still endogenously constructed by the intermediate-value theorem $c=(1-u)G(m_a)+uG(m_b)$, $u\sim U(0.15,0.85)$. The entire solving process, trajectories, and the six verifications are archived in `bench_out/problem_set.md` (the problem set: 50 problem statements + solutions) and `bench_out/report.md`.

| Item | Empirical |
|---|---|
| Overall verdict | **50 / 50 SOLVED** |
| Total steps | 286 steps (mean $5.72$ steps/equation) |
| V-A moment cross $\max\|\tau_{\text{pipe}}-\tau_{\text{eig}}\|$ | $\le 1.29\times10^{-14}$ (machine precision) |
| V-B independent residual $\|G_{\text{eig}}(M^\star)-c\|/\|G(m_a)-c\|$ (threshold $\gamma$) | 49 equations $<10^{-9}$; B2-E02 $=1.29\times10^{-1}$ |
| V-D legality | 50/50 |
| V-E monotonicity of $\Psi$ non-increasing | 50/50 |
| V-F Operator 18's three certificates | 50/50 |
| Total time | $\approx 0.9$–$1.1$ s |

**Step-count distribution by problem type** (5 instances per group): E01 $[5,6,5,5,5]$; E02 $[5,14,4,7,7]$; E03 all $6$; E04 $[8,5,7,6,7]$; E05 $[6,6,5,6,6]$; E06 $[5,5,5,6,5]$; E07 $[5,5,5,4,5]$; E08 $[5,5,6,6,5]$; E09 all $5$; E10 $[5,6,6,6,6]$.

**The three points thereby exposed and corrected** (see §15.4/§17.1/§17.2 for details, corresponding to 5.1–5.3 of Chapter 5 of the problem set):
1. **`OBSTRUCTION` false positive** — the criterion band width is $1/\gamma$, and well-posed problems were misrouted to Operator 9; now `step_dead` is required before declaring an obstruction.
2. **Missing trust region** — the $\eta_N$ normalization deleted the trust region, so strongly nonlinear instances overshoot and $\Psi$ rises; now an endogenous backtracking line search is added in Phase 3.5b.
3. **`SOLVED` tautology** — looking only at "first crossing of $\epsilon$" makes V-B and the termination quantity share a threshold; now the `exhausted` condition is additionally required.

**Correction confirmation**: after the three corrections the main-implementation regression remains **19/19** (V1–V18 + additional items); B2-E02 changes from "a slow oscillation with ratio $\approx0.85$" to **14 steps of strictly monotone convergence**, its V-B drops from $7.30\times10^{-1}$ to $1.29\times10^{-1}$ ($<\gamma = 0.1761$), and the trajectory's $t_\kappa=0.5$ ($\kappa=3,4,5$) and $t_\kappa=0.25$ ($\kappa=12$) confirm the line search is at work.

---

## 8. Interface Declaration with the Existing Operator System

| This layer's operator | Existing operators depended on | Dependency content |
|---|---|---|
| Op13 | Op6, Op10 | $(\alpha_n,\lambda_2)$ spectral assets; $\mathcal{O}(1)$ pseudo-inverse facilities; $N_K \le K_0$ horizon clamping |
| Op14 | Op6, Op7, Op10 | potential re-solve $\Phi$; $B$-field leapfrog; $(DD^T)^\dagger$ local solving |
| Op15 | Op7, Op10 | boundary operators $D,C$; Sherman-Morrison incremental recurrence; Dirichlet-energy monotonicity red line |
| Op16 | Op4, Op9 | endogenous spectral support $[\gamma,1]$; adaptive spectral window $\tau(s)$ (for warning counting) |
| Op17 | Op8, Op9 | $\mu_{\text{trace}}$ arbitration chain; Betti stitching; $\mathcal{S}_{\text{stable}}$ termination criterion |
| Op18 | Op3, Op4, Op5, Op15 | Fiedler sign gate; $c_e$ inversion of $W_e$; degree-relation verification; energy-descent direction on $\mathcal{H}_1^\perp$ |

**Reverse contributions**: this layer adds three capabilities to the existing system —
1. **a local, decomposition-free computational route for spectral moments** (Theorem S1), which can be reused by Op12's Möbius phase detection to replace its explicit matrix power of $\mathrm{tr}(M^k)$;
2. **the weighted Hodge Laplacian $A$ and the endogenous trust region** (Theorem 15.1), providing Op7's field iteration with a step-size mechanism that is adaptive without external parameters;
3. **"closed but not exact" as a first-class criterion** (Theorem S3 + Definition 3.1): it introduces into the whole system a general criterion for judging "whether a constraint can be absorbed by the field dynamics" — any residual falling in $\mathrm{im}\partial_1\oplus\mathrm{im}\partial_2^T$ can safely be handed to Op6/Op7 for absorption, while only the harmonic component must resort to a topological change. This criterion is not limited to solving equations and can be used to judge the satisfiability of any SRE constraint.

---

**References**: SRE Dynamics: The Book of the Void; SRE Fine-Structure-Constant Derivation; SRE Electron Topology (Zenodo); `structure.md` v18.0; `Operator_10_C.md`; `Operator_11_C.md`; `Operator_12_C.md`
