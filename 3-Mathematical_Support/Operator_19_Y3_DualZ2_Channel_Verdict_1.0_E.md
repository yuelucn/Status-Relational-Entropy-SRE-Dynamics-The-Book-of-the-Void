# Dual ℤ₂-Channel Verdict on the Nucleon Skeleton Y₃: Landing the Cut-Space Criterion on the Project's Own Object, the Relation to the Möbius Ladder Family, and a Readable Certificate for the Pfaffian Obstruction

> **Abstract**　The core carrier of this project is the nucleon skeleton $Y_3=Y_3\rtimes\triangle_3$ (closed state $V=12,E=18,\beta_1=7,|\mathrm{Aut}|=36$). Rounds 101–103 established, respectively, the unbiased linear system for Pfaffian orientation classes, the label-independent $\mathbb Z_2$ invariant $\mathrm{rank}_\mathrm{hol}$, and a necessary-and-sufficient criterion for the latter (the cut-space intersection-dimension identity). These three results were never placed side by side on $Y_3$ itself, so the project's central claim — that the charge sign is carried by $H^1$ holonomy rather than by a Pfaffian orientation — still lacked direct measurement on its own object; moreover, "the closed state has no Pfaffian orientation" existed only as the bare fact "the system is infeasible", which a reader cannot check; and the true relation between $Y_3$ and the Möbius ladder family $M_{2n}$ had never been adjudicated.
>
> This report closes all three gaps. **First**, three independent implementations recompute $\mathrm{rank}_\mathrm{hol}$ on $Q_3$, $Y_3^\mathrm{cl}$ and $Y_3^\mathrm{op}$, giving $0/1/2$ — in exact agreement with Operator 19 v1.1 — and in zero mismatch with the cut-space identity. **Second**, a **readable certificate** is given for the absence of a Pfaffian orientation on $Y_3^\mathrm{cl}$: its six perfect-matching equations form a minimal unsatisfiable row subset, and removing any single row restores solvability, i.e. the obstruction is one equation away from being satisfiable. The structural reason is identified: $Y_3^\mathrm{cl}$ contains 42 nice even cycles, whereas $Y_3^\mathrm{op}$ — obtained by deleting one ring edge — contains none, and the Pfaffian channel opens accordingly ($\dim=13$, $|\mathcal O_\mathrm{Pf}|=2^{13}$). **Third**, the relation between $Y_3$ and $M_{2n}$ is adjudicated: complete backtracking enumeration proves zero coverings and zero quotients of $Y_3^\mathrm{cl}$ onto any $n\ge3$ ladder, while $Y_3^\mathrm{cl}$ is exactly a **three-fold regular covering** of $K_4\cong M_4$ (deck group of order 3, quotient $\cong K_4$) — which both explains why $Y_3^\mathrm{cl}$ has three triangles and pins down, to a verifiable precision, the long-open question of whether the two families are related.
>
> All 45 in-repository copies of the $Y_3$ constructor were put through an isomorphism health check (16 independently checkable copies all isomorphic; the 5 that could not be executed in isolation are recorded individually with their cause — signature or same-file dependency; zero non-isomorphic ones). Zero mismatch across four readings on 22 samples; all five falsification gates pass. **Two new portable rules** result (G70 the isomorphism-consistency law, G71 the minimal-conflict-certificate law).

**Keywords**: nucleon skeleton; $\mathbb Z_2$ sign channel; cut space; Pfaffian orientation class; nice even cycle; graph covering; Möbius ladder

---

## 1　Origin: three unsettled questions

The two main lines of this project — "charge emergence" and "mass origin" — share one carrier: the nucleon skeleton $Y_3=Y_3\rtimes\triangle_3$. Its closed state (proton) and open state (neutron) are joined by deleting a single ring edge. The previous three rounds each touched it without landing on it.

**Question one (the claim lacks direct measurement).** the initial Operator 19 release proved that on the Möbius ladder family "a Pfaffian orientation class exists $\iff$ the graph is non-bipartite", and established $\mathcal O_\mathrm{Pf}(M_{2n})\neq\emptyset\iff n$ even $\iff$ non-bipartite; Operator 19 v1.1 introduced the label-independent $\mathbb Z_2$ invariant $\mathrm{rank}_\mathrm{hol}$ and measured $Q_3=0$, $Y_3^\mathrm{cl}=1$, $Y_3^\mathrm{op}=2$; Operator 19 v1.2 gave a necessary-and-sufficient criterion for $\mathrm{rank}_\mathrm{hol}$ (the cut-space intersection-dimension identity T9) and corrected three statements in the Operator 19 text. What was always missing at the seam: **the "Pfaffian channel" and the "$H^1$ holonomy channel" were never adjudicated side by side on $Y_3$ itself**. The evidence chain for the central claim — "the charge sign is carried by $H^1$ holonomy, not by a Pfaffian orientation" — was therefore "on the ladder family it holds, and extrapolating to the skeleton fails", an indirect argument. This report measures precisely that.

**Question two (a negative verdict that cannot be checked).** the initial Operator 19 release's verdict was "the closed state $Y_3^\mathrm{cl}$ admits no Pfaffian orientation", technically "the unbiased linear system is infeasible". This statement is **correct but uncheckable**: from "the system is infeasible" the reader cannot see which row carries the contradiction, nor how close the system is to being feasible. Operator 19 v1.1 recorded it more pointedly as "within one skeleton family, a single edge deletion flips the Pfaffian existence — a sharp falsifiable anchor" — yet gave no structural reason for the flip.

**Question three (the relation was never adjudicated).** An open question carried over from Operator 19 v1.1 asks for a measurement of the relation between $Y_3$ and the Möbius ladder $M_{2n}$, and for "the honest form of the bridge". What existed was one assertion from the initial Operator 19 release — "$Y_3^\mathrm{cl}$ and $M_{12}$ differ in triangle count, hence are not isomorphic" — which excludes isomorphism only, and leaves weaker relations (covering, quotient, double cover) open.

**Question four (implementation consistency never health-checked).** While preparing this report, it was found that the $Y_3$ constructor appears in the repository in **45** places, merging into **21** distinct implementation bodies. The project had never verified that they all yield the same graph. The iron law G63 (shared-engine law) requires "the same implementation" before a strong cross-certification is available; here even "the same implementation" was not established.

---

## 2　Preliminaries: the three skeletons and the two channels

### 2.1　The canonical construction

**Definition 2.1 (closed nucleon skeleton $Y_3$).** Take the vertex set $\{c_0,c_1,c_2\}\cup\{L_{ij}:i,j\in\{0,1,2\}\}$ (12 vertices). The edge set is
$$E\bigl(Y_3^\mathrm{cl}\bigr)=\bigl\{\{c_i,L_{ij}\}:i,j\in\{0,1,2\}\bigr\}\;\cup\;\bigl\{\{L_{0j},L_{1j}\},\{L_{1j},L_{2j}\},\{L_{2j},L_{0j}\}:j\in\{0,1,2\}\bigr\}.$$
Semantically: three centres $c_i$, each joined to three "legs" $L_{ij}$; the legs are grouped by $j$ into three groups, each group $(L_{0j},L_{1j},L_{2j})$ forming a triangle. Hence the closed state contains three triangles.

**Definition 2.2 (open state $Y_3$).** Obtained from $Y_3^\mathrm{cl}$ by deleting one triangle edge; denote it $Y_3^\mathrm{op}$.

**Proposition 2.3 (basic quantities).** $Y_3^\mathrm{cl}$: $V=12$, $E=18$, 3-regular, $\beta_1=7$, $|\mathrm{Aut}|=36$, 2 edge orbits (9 edges each), non-planar, non-bipartite. $Y_3^\mathrm{op}$: $V=12$, $E=17$, $\beta_1=6$, $|\mathrm{Aut}|=4$, 7 edge orbits (sizes $1,2,2,2,2,4,4$), non-planar, non-bipartite.

> **Note 2.4 (a fact about implementation scatter).** The repository contains 45 bodies of $y_3$ / $y_{3,\mathrm{closed}}$ / $y_{3,\mathrm{open}}$, merging into 21 distinct implementation bodies (by function name × body md5). All measurement in this report uses the canonical adjacency of Definition 2.1.

### 2.2　The two ℤ₂ channels

**Definition 2.5 (the $H^1$ holonomy channel).** Let $G$ be connected. $\mathrm{Aut}(G)$ acts on the edge set; the orbits are **edge orbits**, and $\dim W(G)=n_\mathrm{orb}$. Assign a sign $s_e\in\{\pm1\}$ to each edge (constant on each orbit, hence an element of $W(G)$), and define $\sigma(\gamma)=\prod_{e\in\gamma}s_e$ for a cycle $\gamma$; $\sigma$ takes values in $H^1(G;\mathbb F_2)$. Operator 19 v1.1 defined the invariant
$$\mathrm{rank}_\mathrm{hol}(G):=\dim_{\mathbb F_2}\operatorname{im}\Phi_G,\qquad \Phi_G:W(G)\longrightarrow H^1(G;\mathbb F_2).$$

**Theorem 2.6 (Operator 19 v1.2 main theorem, the cut-space identity).** Write $\operatorname{Cut}(G)=\{d(S):S\subseteq V\}$, where $d(S)$ is the set of edges with exactly one endpoint in $S$ (the cut space, i.e. the coboundary space $\operatorname{im}\partial^{\mathsf T}$). Then
$$\boxed{\ \mathrm{rank}_\mathrm{hol}(G)=n_\mathrm{orb}-\dim\bigl(W(G)\cap\operatorname{Cut}(G)\bigr)\ }$$
and $\mathrm{rank}_\mathrm{hol}(G)=0\iff W(G)\subseteq\operatorname{Cut}(G)$ (a necessary-and-sufficient criterion for triviality: every Aut-invariant assignment is some cut).

> **Note 2.7 (cut space vs cycle space — do not confuse).** A basis of $\operatorname{Cut}(G)$ consists of the **stars** $d(\{v\})$ (all edges incident to $v$). If one mistakenly takes "the edge set of the tree path from $v$ to the root", one obtains the tree of the tree-cotree decomposition, which belongs to the **cycle space**; this caused 566/996 mismatches in measurement. Gate B below deliberately uses that substitution as a **falsification** check (see §7.2).

**Definition 2.8 (Pfaffian orientation class).** Let $G$ have perfect matchings $\mathcal{M}$. An edge orientation $t:E(G)\to\{\pm1\}$ is a **Pfaffian orientation** if for every $M\in\mathcal{M}$,
$$\prod_{e\in M}t_e=(-1)^{\mathrm{cr}(M)},\qquad \mathrm{cr}(M)=\text{crossing number of }M \bmod 2 .$$
the initial Operator 19 release proved this equivalent to the solvability of an **unbiased linear system** (no orientation presupposed):
$$\sum_{e\in M}t_e=\mathrm{cr}(M)\quad(\bmod\ 2),\qquad\text{for every }M\in\mathcal{M}.$$
Write the solution set $\mathcal O_\mathrm{Pf}(G)$. When $\#\mathcal{M}=0$ the Pfaffian vanishes identically, the criterion passes trivially, and it **cannot serve as a discovery**.

**Definition 2.9 (nice even cycle).** An even cycle $C$ is a nice even cycle if each of its edges belongs to exactly **two** perfect matchings of $G$.

### 2.3　The relation between the two channels: a structural fact

the initial Operator 19 release obtained, on $Y_3$, the fact that the closed state has **no solution** in the Pfaffian channel but **does** in the $H^1$ channel. This report upgrades that fact to a checkable verdict and supplies a mechanism.

---

## 3　Verdict one: the $H^1$ channel on the three skeletons

### 3.1　Three independent implementations

**Method 3.1 (three implementations).** On $Q_3$, $Y_3^\mathrm{cl}$ and $Y_3^\mathrm{op}$, compute $\mathrm{rank}_\mathrm{hol}$ along three **mutually independent** routes:

- **I1 (the $M$-matrix route).** Replicates T2 of the Operator 19 chapter: rows of $M$ are cycle-basis elements, columns are edge orbits, and $M[c][o]$ is the number of edges of $c$ lying in orbit $o$, mod 2. Then $\mathrm{rank}_\mathrm{hol}=\operatorname{rank}_{\mathbb F_2}M$.
- **I2 (cut-space intersection route).** Take the orbit characteristic vectors as a basis of $W$ and the stars as a basis of $\operatorname{Cut}$; from $\dim(W\cap\operatorname{Cut})=\dim W+\dim\operatorname{Cut}-\operatorname{rank}(W\cup\operatorname{Cut})$ obtain $\mathrm{rank}_\mathrm{hol}$.
- **I3 (subset-enumeration route).** Enumerate all $2^{|V|}$ subsets $S$ and take **all distinct values** of $d(S)$ as a generating set for $\operatorname{Cut}$ (a construction *not* cohomologous with I2's "star basis"), then intersect with $W$.

**Theorem 3.2.** On $Q_3$, $Y_3^\mathrm{cl}$ and $Y_3^\mathrm{op}$, the readings of I1, I2, I3 and the identity of Theorem 2.6 agree **exactly**:
$$\mathrm{rank}_\mathrm{hol}(Q_3)=0,\qquad \mathrm{rank}_\mathrm{hol}\bigl(Y_3^\mathrm{cl}\bigr)=1,\qquad \mathrm{rank}_\mathrm{hol}\bigl(Y_3^\mathrm{op}\bigr)=2 .$$
The per-item values of $|W|$, $\dim\operatorname{Cut}$ and $\dim(W\cap\operatorname{Cut})$ are given in Table 3.1, and the four readings show zero mismatch on 22 samples (ladder family, prism family, control graphs, random 3-regular graphs).

**Table 3.1　Four readings on the three skeletons**

| Skeleton | $V$ | $E$ | $\beta_1$ | $|\mathrm{Aut}|$ | $n_\mathrm{orb}$ | $\dim\operatorname{Cut}$ | $\dim(W\cap\operatorname{Cut})$ | $\mathrm{rank}_\mathrm{hol}$ (I1/I2/I3/T9) |
|---|---|---|---|---|---|---|---|---|
| $Q_3$ (electron) | 8 | 12 | 5 | 48 | 1 | 7 | 1 | **0** / 0 / 0 / 0 |
| $Y_3^\mathrm{cl}$ (proton) | 12 | 18 | 7 | 36 | 2 | 11 | 1 | **1** / 1 / 1 / 1 |
| $Y_3^\mathrm{op}$ (neutron) | 12 | 17 | 6 | 4 | 7 | 11 | 5 | **2** / 2 / 2 / 2 |

### 3.2　What the three readings mean

**Corollary 3.3 (the electron's sign is locked by topology).** $\mathrm{rank}_\mathrm{hol}(Q_3)=0$, i.e. $W(Q_3)\subseteq\operatorname{Cut}(Q_3)$: the unique Aut-invariant assignment (all-ones, since $Q_3$ is edge-transitive) is exactly a cut of the bipartite graph, so the sign has **no** topological degree of freedom. This agrees with Operator 19 v1.1's $\lambda(Q_3)=\mathrm{True}$ and supplies its mechanism: the sign is not "locked by accident" but "the single candidate assignment happens to lie in the cut space".

**Corollary 3.4 (the proton has exactly one bit of sign freedom).** For $Y_3^\mathrm{cl}$, $n_\mathrm{orb}=2$ while $\dim(W\cap\operatorname{Cut})=1$, so $\mathrm{rank}_\mathrm{hol}=1$: exactly two reachable holonomy classes (the trivial class and a nontrivial class $v$). In Operator 19 v1.1 this appeared only as "$\mathrm{sym\_n\_classes}=2$"; this report gives its **structural source**: of the two edge orbits, exactly one has its assignment inside the cut space and the other does not.

**Corollary 3.5 (the neutron has two bits).** $Y_3^\mathrm{op}$ has 7 edge orbits, so $n_\mathrm{orb}=7$; the intersection dimension is 5, hence $\mathrm{rank}_\mathrm{hol}=2$.

**Corollary 3.6 (independent agreement with Operator 19 v1.1).** The three readings $0/1/2$ agree **exactly** with Operator 19 v1.1's holonomy class counts ($\mathrm{sym\_n\_classes}=1/2/4$), although the two paths use different implementations (the former works in the linear algebra of the Aut-invariant assignment space, the latter counts $H^1$ classes). By G63 this is a **strong cross-certification** of Operator 19 v1.1.

---

## 4　Verdict two: the Pfaffian channel reading and a readable certificate

### 4.1　The reading

**Table 4.1　The dual-channel verdict (central result)**

| Skeleton | $n_\mathrm{orb}$ | $\mathrm{rank}_\mathrm{hol}$ ($H^1$ channel) | $\#\mathcal M$ | $\|\mathcal O_\mathrm{Pf}\|$ | $\dim\mathcal O_\mathrm{Pf}$ | Pfaffian channel | nice even cycles |
|---|---|---|---|---|---|---|---|
| $Q_3$ | 1 | 0 | 9 | 128 | 6 | **solvable** | 0 |
| $Y_3^\mathrm{cl}$ | 2 | 1 | 6 | **0** | — | **infeasible** | **42** |
| $Y_3^\mathrm{op}$ | 7 | 2 | 4 | 16384 | 13 | **solvable** | **0** |

**Proposition 4.2 (channel separation).** On the closed nucleon skeleton the $H^1$ holonomy channel is **open** ($\mathrm{rank}_\mathrm{hol}=1$) while the Pfaffian channel is **closed** ($\mathcal O_\mathrm{Pf}=\emptyset$). Hence the project's central claim — that the charge sign is carried by $H^1$ holonomy — receives, **for the first time, direct side-by-side measurement on the project's own object**, rather than the indirect argument "it holds on the ladder family and extrapolates to the skeleton".

### 4.2　A readable certificate: the minimal unsatisfiable row subset

**Definition 4.3 (minimal conflict certificate).** For the unbiased linear system of Definition 2.8, a subset $R'$ of the row set $R$ is a **minimal unsatisfiable row subset** (minimal unsatisfiable subset) if $R'$ is infeasible while every proper subset $R''\subsetneq R'$ is feasible.

**Theorem 4.4 (the certificate for $Y_3^\mathrm{cl}$).** The unbiased system of $Y_3^\mathrm{cl}$ has 6 rows (6 perfect matchings) $\times\,18$ columns (18 edges), and **all 6 rows** form a minimal unsatisfiable row subset; removing any single row leaves a **feasible** 5-row system. That is: $Y_3^\mathrm{cl}$ is **one equation away** from admitting a Pfaffian orientation.

> **Note 4.5 (checkability).** The six rows and their right-hand sides (the $\mathrm{cr}$ values) are listed one by one in the experimental output (Table 7.2 in §7.3); the "one row away" fact was confirmed by **exhausting all row subsets**, not heuristically.

**Proposition 4.6 (structural reason: the nice even cycles vanish).** $Y_3^\mathrm{cl}$ contains **42** nice even cycles (length distribution: 9 of length 6, 9 of length 8, 18 of length 10, 6 of length 12); $Y_3^\mathrm{op}$ contains **0**. The existence of nice even cycles forces the "sign consistency around the cycle" conditions of a Pfaffian orientation into mutual conflict; deleting one ring edge empties that obstruction set, and the Pfaffian channel opens accordingly ($\dim=13$, $\|\mathcal O_\mathrm{Pf}\|=2^{13}=16384$, with the particular solution independently re-checked: $\mathrm{Pf}=+4=\#\mathcal M$).

> **Note 4.7 (the nice obstruction is an indicator, not a criterion).** In the classifier sense (false positives and false negatives must both be reported, per G69), taking "has a nice even cycle" as an **indicator** of "no Pfaffian orientation" yields TP=4, FP=2, FN=3, TN=13 on the 22 samples. False positive: $M_8$ (Wagner graph, nice=1 yet solvable, $|\mathcal O_\mathrm{Pf}|=256$). False negatives: $M_{10}$, $M_{14}$ (bipartite, nice=0 yet infeasible) and one random 3-regular graph ($\mathrm{rank}_\mathrm{hol}=3$, nice=0, infeasible). Hence a nice even cycle can only serve as an **obstruction indicator, never as a criterion**; the truth is always supplied by the unbiased system. This evaluation also locates the false negatives: they lie mainly in the **bipartite** quadrant (in a bipartite graph the all-ones assignment lies in the cut space, so no nice obstruction arises, yet the system may still be infeasible).

---

## 5　Verdict three: the relation between $Y_3$ and the Möbius ladder family

### 5.1　Complete enumeration of coverings

**Method 5.1 (covering enumeration).** A **covering** $G\to H$ is a map $t:V(G)\to V(H)$ satisfying (i) homomorphism, $uv\in E(G)\Rightarrow t(u)\sim t(v)\in E(H)$; and (ii) **local bijectivity**: for every $v$, $\{t(w):w\in N_G(v)\}=N_H(t(v))$. The enumeration is by backtracking: fix $t$ pointwise in BFS order, pruning only by necessary conditions (adjacency to already-fixed images, distinctness from the images of already-fixed neighbours, and the local-bijectivity condition at vertices whose neighbourhood is fully fixed). The enumeration is **complete**.

**Proposition 5.2 (covering and isomorphism exclusion).**

1. $Y_3^\mathrm{cl}$ is **not isomorphic** to any $M_{2n}$ ($n\ge3$): the adjacency spectra differ (e.g. $Y_3^\mathrm{cl}$: $[-2.303,-2.303,-1,-1,-1,-1,-1,1.303,1.303,2,2,3]$; $M_{12}$: $[-2.732,-2.732,-1,-1,-1,0,0,0.732,0.732,2,2,3]$), and the triangle counts differ (3 vs 0).
2. There are **zero** coverings $Y_3^\mathrm{cl}\to M_{2n}$ for $n\ge3$ (complete backtracking over $\{M_4,M_6,M_8,M_{10},M_{12},M_{14}\}$, all giving 0).
3. There is **no** regular covering whose quotient makes $Y_3^\mathrm{cl}$ isomorphic to any ladder (a quotient is a special case of a covering, so zero coverings implies zero quotients).
4. **But**: $Y_3^\mathrm{cl}$ is a **$k=3$ regular covering** of $K_4$ (the unique covering; deck group of order 3; quotient $\cong K_4$; each of the six $K_4$ edges is lifted three times).

> **Note 5.3 ($K_4$ *is* $M_4$).** The edge set of $M_4=\mathrm{Cay}(\mathbb Z_4,\{1,2\})$ is exactly $K_4$ ($V=4$, $E=6$, 4 triangles); the two are isomorphic. Hence the $K_4$ of Proposition 5.2(4) **is the degenerate small member** of the ladder family. The strict statement is therefore: $Y_3$ *does* stand in a covering/quotient relation to the ladder family, but the base graph is $M_4$ ($n=2$), and it is unrelated to any genuine ladder with $n\ge3$.

**Theorem 5.4 (the structural origin of $Y_3$).** $Y_3^\mathrm{cl}$ is a three-fold covering of the complete graph $K_4$, and this covering is **regular** (deck group of order 3). Its fibres are four groups of three points each; every $K_4$ edge is lifted three times. $Y_3^\mathrm{cl}$ has exactly three triangles — consistent with "the four triangles of $K_4$ are spread over three fibres".

### 5.2　The honest form of the verdict

**Proposition 5.5 (a direct answer to an open question carried over from Operator 19 v1.1).** $Y_3$ and the Möbius ladder family $M_{2n}$ ($n\ge3$) stand in **no** covering, quotient or double-cover relation: not isomorphic, zero coverings, zero quotients. $Y_3$ does possess a covering structure, but its base graph is $K_4\cong M_4$, the **smallest degenerate point** of the ladder family, not any genuine ladder. The "threefold" character of $Y_3$ (3 centres, 3 leg groups, 3 triangles, $|\mathrm{Aut}|=36=3!\times3!$, 2 edge orbits of 9 edges) acquires a unified explanation in the covering view: **$Y_3$ is a three-fold complete graph**.

**Corollary 5.6 (why the the initial Operator 19 release theorem does not extrapolate).** the initial Operator 19 release's theorem "$\mathcal O_\mathrm{Pf}(M_{2n})\neq\emptyset\iff n$ even $\iff$ non-bipartite" holds within the ladder family. $Y_3^\mathrm{cl}$ is non-bipartite yet admits **no** Pfaffian orientation, so "non-bipartite $\Rightarrow$ an orientation class exists" is **not a universal proposition**. This report supplies its structural reason (Corollary 5.6): $Y_3^\mathrm{cl}$ lies outside the ladder family (§5.1) and carries 42 nice even cycles (§4.2), whereas even-$n$ ladders carry none.

### 5.3　Cross-reference index conventions (added in the second half of this report)

**Problem.** All the verdicts above are written as "$M_{2n}$", but the **Operator 19 chapter** (and the preamble of its initial release) denotes the same family by $M_k$, and the two subscripts are **not** defined identically. Without settling the conventions first, a statement such as "$Y_3$ is not isomorphic to $M_{12}$" points at the wrong graph once it is cited across documents.

**Definition 5.7 (the two conventions).**

- **Operator-19 convention**: $M_k=$ the even cycle $C_{2k}$ plus a diametric chord, with $V=2k$ vertices;
- **Paper convention**: $M_{2n}=\mathrm{Cay}(\mathbb Z_{2n},\{1,n\})$, with $V=2n$ vertices.

**Proposition 5.8 (index correspondence).** $\text{Operator-19 }M_k\cong\text{this-report }M_{2k}$: for the same family the two indexings **differ by a factor of 2**. Verified case by case on 11 examples ($k=2,\dots,12$), all isomorphic, 0 mismatches. The three error-prone anchors are

| Graph | Operator-19 index | Paper index | $V$ |
|---|---|---|---|
| $K_4$ | $M_2$ | $M_4$ | 4 |
| $K_{3,3}$ | $M_3$ | $M_6$ | 6 |
| Wagner graph ($M_8$) | $M_4$ | $M_8$ | 8 |

**Corollary 5.9 (restating §5.1).** The set $\{M_4,M_6,M_8,M_{10},M_{12},M_{14}\}$ in **paper** indexing corresponds to $\{M_2,M_3,M_4,M_5,M_6,M_7\}$ in **Operator-19** indexing; note that $M_2\cong K_4$ there. Hence the "zero coverings" claim of §5.1(2) refers to the **same set of objects** under both conventions, but the $n=2$ member must be excluded by definition to obtain "genuine ladders".

**Proposition 5.10 (whole-family readings under Operator-19 conventions for the whole family, $k=2,\dots,24$).** Four-way readings ($n_\mathrm{orb}$ / $\mathrm{rank}_\mathrm{hol}$ / bipartiteness / triangle count) on all 23 members in **Operator-19** indexing give the exact laws:

1. $n_\mathrm{orb}=1\iff k\in\{2,3\}$, and 2 otherwise;
2. $k$ even $\iff$ non-bipartite; $k$ odd $\iff$ bipartite;
3. $\mathrm{rank}_\mathrm{hol}=0\iff k=3$, and $\ge1$ otherwise; $k=3$ is the family's **only** "bipartite + single-orbit" member.

**Theorem 5.11 (necessary and sufficient condition for the ladder family to open the symbolic channel).** Within the ladder family, $\mathrm{rank}_\mathrm{hol}=0$ (the $H^1$ channel is trivial) **if and only if** $k=3$ in Operator-19 indexing, i.e. $n=3$ in paper indexing. Hence **the ladder family opens the symbolic channel if and only if $k\neq3$**. Remark: for odd $k\ge5$ the channel is still open, but the mechanism is **not** an odd cycle (the graph is bipartite there) — it is "bipartite + two orbits". This is why the initial Operator 19 release, treating "has an odd cycle" as a sufficient condition, missed an entire class.

> **Note 5.12 ($k=3$ is the only member needing separate treatment).** $k=3$ (Operator-19) $=K_{3,3}=$ paper $M_6$ is the family's unique member that is simultaneously bipartite, single-orbit and $H^1$-trivial; it is also the $K_{3,3}$ of §5.1 that carries 15 nice even cycles, all unsatisfiable. The family's behaviour therefore splits into **three** classes indexed by $k$ — $k=3$ / $k$ even / odd $k\ge5$ — rather than the intuitive two.

---

## 6　Five new portable rules

**Rule G70 (the isomorphism-consistency law).** Whenever a single skeletal object exists in the repository as **several implementation copies**, one must **first prove they yield the same graph** (isomorphic) before making any claim that rests on it; the number of copies is itself a risk signal. Measured this report: 45 function bodies, 21 implementation bodies, 16 independently checkable copies all isomorphic, 5 that cannot be executed in isolation (due to a parameterised signature or a same-file dependency) recorded individually with their cause, and 0 non-isomorphic. **Corollary**: before isomorphism is proven, "the multiple copies agree" cannot be used as an assumption.

**Rule G71 (the minimal-conflict-certificate law).** When "some linear system is infeasible" is reported merely as a **fact**, the reader can neither check it nor judge how close it is. Two things must be added: (i) a **minimal unsatisfiable row subset**, independently re-checked (extract that subset and re-solve: still infeasible; remove any one row: becomes feasible); and (ii) the **satisfiable fraction** (here: $Y_3^\mathrm{cl}$ is one row short of a contradiction). This report thereby upgrades the initial Operator 19 release's "the closed state has no solution" from a fact to a checkable certificate.

**Rule G72 (the audit-criterion law).** The **criterion** of an audit script must itself be falsifiable; otherwise an all-green report carries no information. Two requirements: (i) a **negative control** — inject known-wrong expected values and require the checker to report MISS (this report: injecting 3 wrong values yields exactly 5 MISSes; injecting 3 cell-level corruptions yields 3 alarms); (ii) the criterion must **locate by structure** — parse tables and read column positions rather than relying on fragile string needles. Measured this report: the needle-based criterion raised 9 false alarms on a perfectly correct document, so without this fix a correct paper would have been judged wrong. **Companion rule**: an enumerating implementation that exceeds its capability boundary ($|V|>16$) must be marked `n/a` rather than **counted as a mismatch** — otherwise "cannot compute" is misread as "disagrees".

**Rule G73 (the index-convention correspondence law).** **The same family may differ by a factor in its subscript across documents** (here: Operator-19 $M_k$ is the even cycle $C_{2k}$ plus a diametric chord with $V=2k$; paper $M_{2n}$ is $\mathrm{Cay}(\mathbb Z_{2n},\{1,n\})$ with $V=2n$; the two differ by a factor of 2) ⇒ **an index-convention correspondence table must be built before any cross-document citation**. The three error-prone anchors: $K_4$ = Operator-19 $M_2$ = paper $M_4$; $K_{3,3}$ = $M_3$ = $M_6$; Wagner graph = $M_4$ = $M_8$. **Corollary**: any statement of the form "$X$ is not isomorphic to $M_{12}$" is **not decidable** unless the indexing system is stated — it may denote two different graphs.

**Rule G74 (the covering-enumeration law).** A graph covering $G\to H$ is defined by **homomorphism plus local bijectivity** $\{t(w):w\in N_G(v)\}=N_H(t(v))$; neither condition may be dropped (demanding only a homomorphism admits the trivial map and folds). The enumeration must be **complete**: this report uses pure CSP backtracking with pruning by **homomorphism-necessary conditions only** (adjacent to the images of already-placed neighbours, distinct from them), and it is validated by the positive control $Q_3\to K_4$ (the $k=2$ double covering) — stronger pruning would miss that case, so "completeness" is an attribute that must be verified separately, not a default. **Two corollaries**: (i) a **quotient is a special case of a covering**, so "zero coverings" **implies** "zero quotients", not conversely; (ii) a **normal covering $\iff$ a non-trivial deck group** (deck transformations = automorphisms preserving the covering map).

> **Note 6.1 (relation to existing rules).** G71 belongs to the same family as G67 (falsification gates must be injectable) and G68 (tampering must delete every occurrence) — all under "a verdict must be checkable"; G72 **strengthens** G67: not only must the gate be injectable, the **criterion itself** must be injectable. It complements G62 (a counterexample in a finite field suffices to establish incrementality): G62 says that one counterexample in a finite field settles incrementality, G71 says that a negative verdict must come with its minimal conflict size. Gate F below is constructed per G67/G68/G72. G73 and G74 belong to the family of G29 (first ask whether the obstruction is discreteness, cardinality, or labelling): G73 shows that a **labelling**-level convention issue can masquerade as a mathematical-level counterexample.

---

## 7　Verification protocol

### 7.1　Implementation inventory

| No. | Script | Role |
|---|---|---|
| E1 | `5-Appendixs/Operators/Y3_Verdict/_dir7_y3_skeleton_verdict.py` | Main experiment: Parts A–F (all verdicts of this report) |
| E2 | `5-Appendixs/Operators/Y3_Verdict/_probe_y3_impls.py` | Probe: implementation distribution and API localisation (conclusions folded into E1) |
| E3 | `5-Appendixs/Operators/Y3_Verdict/_probe_y3_facts.py` | Probe: preliminary measurement of nice cycles, bridges, spectra |
| existing | `5-Appendixs/Operators/Y3_Verdict/_pfcore.py`, `5-Appendixs/Operators/Y3_Verdict/_gf2.py` | the initial Operator 19 release Pfaffian engine (unbiased system + dual-implementation cross-check) |
| existing | `5-Appendixs/Operators/Y3_Verdict/_bridge101_nucleon.py` | the initial Operator 19 release bridge ($Y_3$ construction and holonomy mechanism) |

### 7.2　Gate table

| Gate | Content | Result |
|---|---|---|
| A | All in-repository $Y_3$ implementations isomorphic to the canonical adjacency (those checkable) | **PASS** (16/16 isomorphic, 0 non-isomorphic) |
| A′ | Falsification: $Y_3^\mathrm{cl}\not\cong Q_3$ and $Y_3^\mathrm{cl}\cong Y_3^\mathrm{cl}$ | **PASS** |
| B | I1/I2/I3 + Theorem 2.6 in zero mismatch on the three skeletons | **PASS** |
| B′ | Falsification: replacing the definition of $\operatorname{Cut}$ by "tree path edge sets" must change the reading ($1\to2$) | **PASS** |
| B″ | Positive control: $W$ degenerating to the zero space forces $\mathrm{rank}_\mathrm{hol}=0$ | **PASS** |
| E | Three implementations + identity in zero mismatch on 22 samples | **PASS** |
| F1 | Injecting known-bad data (breaking one edge of $Y_3^\mathrm{cl}$) must be reported as non-isomorphic | **PASS** |
| F2 | Positive control $Y_3^\mathrm{op}$ (true value: solvable) judged solvable + known-bad $Y_3^\mathrm{cl}$ judged infeasible | **PASS** |
| F3 | Validity of the minimal conflict certificate: the subset alone re-solves infeasible, and removing any row makes it feasible | **PASS** |
| F4 | Tampering with the T9 reading must raise an alarm | **PASS** |
| F5 | Positive control: the classical double covering $Q_3\to K_4$ must be enumerated ($k=2$, fibres $2,2,2,2$) | **PASS** |

### 7.3　Certificate details

**Table 7.1　The unbiased system of $Y_3^\mathrm{cl}$ (6 rows × 18 columns)**

| Row | Perfect matching $M$ | $\mathrm{cr}(M)$ |
|---|---|---|
| 1 | $\{(0,1),(2,6),(3,11),(4,7),(5,9),(8,10)\}$ | 1 |
| 2 | $\{(0,1),(2,10),(3,7),(4,6),(5,9),(8,11)\}$ | 0 |
| 3 | $\{(0,2),(1,5),(3,11),(4,7),(6,10),(8,9)\}$ | 0 |
| 4 | $\{(0,2),(1,9),(3,7),(4,5),(6,10),(8,11)\}$ | 1 |
| 5 | $\{(0,3),(1,5),(2,10),(4,6),(7,11),(8,9)\}$ | 1 |
| 6 | $\{(0,3),(1,9),(2,6),(4,5),(7,11),(8,10)\}$ | 0 |

All six rows together are infeasible; removing any one row leaves a feasible 5-row system (maximal satisfiable row count $=5/6$).

**Table 7.2　nice even cycle counts (length distribution)**

| Graph | Total | len 4 | len 6 | len 8 | len 10 | len 12 | Pfaffian |
|---|---|---|---|---|---|---|---|
| $Y_3^\mathrm{cl}$ | 42 | 0 | 9 | 9 | 18 | 6 | infeasible |
| $Y_3^\mathrm{op}$ | 0 | 0 | 0 | 0 | 0 | 0 | solvable ($\dim=13$) |
| $M_8$ | 1 | 0 | 0 | 1 | 0 | 0 | solvable |
| $M_{12}$ | 0 | 0 | 0 | 0 | 0 | 0 | solvable |
| Petersen | 25 | 0 | 10 | 15 | 0 | 0 | infeasible |
| $K_{3,3}$ | 15 | 9 | 6 | 0 | 0 | 0 | infeasible |

### 7.4　External-sample falsification

The 22 samples cover the ladder family $M_4$–$M_{16}$, the prism family $\mathrm{prism}_3$–$\mathrm{prism}_6$, classical graphs ($Q_3$, $K_3$, $K_4$, Heawood, Petersen) and four random 3-regular graphs (fixed seed). The four readings show zero mismatch on all 22 samples; the out-of-family distribution of the two channels' behaviour is fully recorded (Table 4.1, Note 4.7). **No** new type beyond "$H^1$ open but Pfaffian closed" was found; $Q_3$ is the only sample of type "$H^1$ closed, Pfaffian open" shared with $K_{3,3}$, $M_6$, $M_{10}$, $M_{14}$, Heawood, $\mathrm{prism}_4$ and $\mathrm{prism}_6$.

---

## 8　Conclusions

### 8.1　Table of the three verdicts

| Verdict | Statement | Basis |
|---|---|---|
| One | $\mathrm{rank}_\mathrm{hol}$ on $Q_3/Y_3^\mathrm{cl}/Y_3^\mathrm{op}$ equals $0/1/2$, with zero mismatch across four readings | Theorem 3.2, Table 3.1, Gates B/B′/B″ |
| Two | The absence of a Pfaffian orientation on $Y_3^\mathrm{cl}$ carries a **readable certificate** (6-row minimal unsatisfiable set, one row short); the structural reason is 42 nice even cycles, and $Y_3^\mathrm{op}$'s vanishing of that count reopens the channel | Theorem 4.4, Proposition 4.6, Note 4.7 |
| Three | $Y_3$ stands in no covering/quotient/double-cover relation with $M_{2n}(n\ge3)$; $Y_3$ is a three-fold regular covering of $K_4$ | Proposition 5.2, Theorem 5.4, Proposition 5.5 |

### 8.2　What this says about the project's own results

This report upgrades "the charge sign is carried by $H^1(G;\mathbb Z_2)$ holonomy rather than by a Pfaffian orientation" from an **indirect argument** (holds on the ladder family, fails on extrapolation to the skeleton) to a **side-by-side measurement on the project's own object** (Proposition 4.2): on the very same graph $Y_3^\mathrm{cl}$, the $H^1$ channel yields exactly two reachable classes (one bit of freedom) while the Pfaffian channel admits no orientation at all — with a checkable certificate (§4.2) and a structural mechanism (the nice even cycle count drops from 42 to 0). Simultaneously, Operator 19 v1.1's qualitative observation that "one edge deletion flips the Pfaffian existence within a single skeleton family" is located to a **specific mechanism**: deleting a ring edge empties the nice-even-cycle obstruction set.

The scope of the initial Operator 19 release's theorem is likewise tightened, with a structural reason (Corollary 5.6): "non-bipartite $\Rightarrow$ a Pfaffian orientation class exists" holds only inside the ladder family; $Y_3$ supplies an out-of-family counterexample, and the counterexample works because $Y_3$ is a different family and carries nice obstructions.

### 8.3　Relation to the Operator 19 chapter

Operator 19 v1.2 already adjudicated three statements in its own text and prepared five patches. The present report does **not** overturn those verdicts; rather, it provides **positive evidence drawn from this project's own objects** for the item "the §6.1 skeleton table": that table lists skeletons such as $Y_3$ as "multi-orbit + non-bipartite", and v1.2 falsified the way its reasoning was written ("$T_2\ M\neq0$" as a necessary condition); this report measures $\mathrm{rank}_\mathrm{hol}(Y_3^\mathrm{cl})=1\neq0$ and $\dim(W\cap\operatorname{Cut})=1$, confirming on the **project's own object** that the channel is indeed open — thereby supporting the table row while rejecting the form of its justification.

At the same time, the five new rules (G70–G74) are **methodological increments** that have now been folded into Operator 19 §10 boundary clauses: G70 adds "multiple implementations of one object must first be proven isomorphic"; G71 adds "a negative verdict must carry a minimal conflict certificate"; G72 adds "the audit criterion itself must be falsifiable"; G74 adds "the covering definition includes local bijectivity, and completeness of the enumeration must be verified separately".

**A dedicated remark on index conventions (G73).** Operator 19 §6.1 skeleton table and the family notation in §6.2 use $M_k$, whereas this report uses $M_{2n}$. The two **differ by a factor of 2** (both have $V=2k$/$2n$ vertices, but the subscripts mean different things). When citing this report's statement "$k=3$ is the only $H^1$-trivial member", note that this $k=3$ is $M_6\cong K_{3,3}$ in this report's indexing, **not** $M_3$. The index-convention correspondence table is Proposition 5.8, and the whole-family readings under Operator 19 conventions are Proposition 5.10.

**A third boundary concerning criteria.** When this report was first written it measured that searches of the Operator 19 text for `Pfaffian`, `rank_hol` and "closed/open flip" returned **0 hits each** — i.e. the results of this report, v1.1 and v1.2 had at that time not yet entered the text. This release has merged T9–T11, §6.2 and §6.3 into Operator 19 and corrected v1.1's odd-cycle criterion statement, so this boundary is closed as of this release.

### 8.4　Honest boundaries

1. **Completeness of the covering enumeration rests on the implementation**: the completeness of Method 5.1 is guaranteed by "pruning only by necessary conditions" and is checked by the positive control $Q_3\to K_4$ ($k=2$); but no third-party independent implementation cross-check was performed.
2. **$|\mathrm{Aut}|$ was not classified group-theoretically**: the group structure of $|\mathrm{Aut}(Y_3^\mathrm{cl})|=36$ (conjecturally $S_3\times S_3$) is unproved; the isomorphism type of the order-3 deck group is undetermined.
3. **No universal proof of the causal link between nice even cycles and infeasibility**: Proposition 4.6 gives the empirical correspondence in the direction "the nice count vanishes $\Rightarrow$ the channel opens", together with a full indicator evaluation (TP/FP/FN/TN all reported); the sufficiency of "has a nice cycle $\Rightarrow$ infeasible" is **not** proven (there is a false positive, $M_8$).
4. **No physical interpretation was advanced**: this report adjudicates at the graph-theoretic level only and does **not** match the covering structure ($Y_3$ as a three-fold $K_4$) against the physical quantities of mass and charge; that line is left for a later merging with the molecular layer (the $\kappa,\varrho,\nu$ channels of Operator 20).
5. **Sample size**: 22 external samples is small for the distribution of out-of-family behaviour; this report only **reports** that distribution and asserts nothing universal from it.
6. **Choice of deleted edge for $Y_3^\mathrm{op}$**: this report follows the initial Operator 19 release's canonical choice (the first triangle edge). Given the high $S_3\times S_3$ symmetry of the three leg groups in $Y_3^\mathrm{cl}$, the choice is **probably** immaterial, but its independence from the choice of edge is **not proven**.

---

## References

[1] WorkBuddy. *SRE Operator 19: the $\mathbb Z_2$ holonomy charge-sign channel — a rigorous mathematical specification and paper*. Part 3, "Operator 19", of this book (v1.2).
[2] WorkBuddy. *SRE non-planar canonical orientation classes: the Möbius ladder*. Earlier work in this project (the initial Operator 19 release).
[3] WorkBuddy. *A triviality criterion for the $\mathbb Z_2$ channel: cut-space intersection dimension, parity counterexamples on the Möbius ladder, and three verdicts on the Operator 19 text*. In this project (Chinese/English mirror, Operator 19 v1.2).
[4] Kasteleyn, C. A. D. *The number of perfect matchings of the 3-regular planar graphs*. J. Combin. Theory 3 (1967) 269–271.
[5] Lovász, L. T.; Plummer, M. D. *A survey of the theory of Pfaffian orientations*. J. Combin. Theory B 40 (1986) 227–252.
[6] Thomas, R. *Graphs with every cycle even*. Discrete Math. 61 (1986) 1–12.
[7] Biggs, N. *Algebraic Graph Theory and Its Applications*. Cambridge UP, 1993 (coverings and deck transformations).
[8] Godsil, R.; Royle, G. *Algebraic Graph Theory*. Springer, 2001 (graph coverings, double coverings).
[9] Kasteleyn, C. A. D. *The number of perfect matchings of the 3-regular planar graphs*; the Pfaffian expansion condition for Kasteleyn orientations.
[10] Diestel, R. *Graph Theory*. 5th ed. Springer, 2017 (cycle space, cut space, tree-cotree decomposition).
[11] WorkBuddy. *The last-subshell-state criterion: mechanism tracing and a new hold-out set*. Earlier work in this project (predecessor of Operator 19 v1.1).

---

## Appendix A　Reproduction

```
C:\myapp\miniconda3\envs\ai\python.exe 5-Appendixs\Operators\Y3_Verdict\_dir7_y3_skeleton_verdict.py
```
Output: `5-Appendixs/Operators/Y3_Verdict/_dir7_y3_skeleton_verdict.json` (containing all numerical values of Parts A–F). Runtime is about 2 minutes (the covering backtracking of Part D and the minimal-subset exhaustion of Part C account for most of it).

> **A boundary on Part A (implementation census)**: Part A recursively scans every `.py` under `SRE_Y3_ROOT` (default: the directory containing the script) and counts the copies and isomorphism status of the `y3_closed` / `y3_open` / `y3` family. The shipped JSON records the readings on the **full project source tree** (21 implementations, 45 copies); run inside the appendix directory alone, only 4 are reachable and the `partA` readings shrink accordingly. **Parts B–F and every conclusion of this chapter are independent of that scan** — the chapter has been re-run in the appendix directory: Parts B–F match the shipped JSON key by key, and gates D, E, F all PASS. To reproduce 21/45, set `SRE_Y3_ROOT=<project source root>` before running.

The index-convention correspondence of §5.3 and the whole-family readings under Operator-19 conventions are produced by a second script:

```
C:\myapp\miniconda3\envs\ai\python.exe 5-Appendixs\Operators\Y3_Verdict\_dir7b_book_index_convention.py
```

Output: `5-Appendixs/Operators/Y3_Verdict/_dir7b_book_index_convention.json` (Part 1: 11 convention-correspondence cases; Part 2: four-way readings of the whole Operator-19-indexed family $M_k$, $k=2,\dots,24$; Part 3: correspondence checks and reverse-validity tests).
