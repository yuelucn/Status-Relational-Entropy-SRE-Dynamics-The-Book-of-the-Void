# Theory of Hierarchical Dissipative Self-Organizing Binary Network Dynamics

**Author:** Yue Lu
**Version: 1.1** (MDS methodological caveats and appendix added based on v1.0; all original axioms, equations and theorems preserved; v1.0 archived for historical traceability)

> 
> **Resource-Availability Statement**
> This framework is built upon Status-Relational Entropy (SRE) Dynamics. All theoretical materials are archived in the Zenodo open-access repository. **This manuscript suite, including system papers, application developments, scientific hypotheses, full algebraic derivations for operators 1-6 and simulation code, is fully open-source**. Operators 7, 8, 9, 10 are subsequent closed-source commercial core modules and are not part of this manuscript suite.
>
>You may also access the Tencent intelligent-document space supporting AI-assisted reading, available on both PC and WeChat mobile clients.
>
>As of 2026-08-14, constrained by Google’s terms-of-service, the author no longer maintains or updates the SRE document library hosted in Google Gemini Notebook. The link below serves only as a historical archive and must not be used as a formal citation source:
>- Google Gemini Notebook (historical archive, no further updates):
[https://notebooklm.google.com/notebook/ef52bf5a-f6d0-4a2a-aed4-b25d6520ab2c](https://notebooklm.google.com/notebook/ef52bf5a%E2%80%91f6d0%E2%80%914a2a%E2%80%91aed4%E2%80%91b25d6520ab2c)
>- Tencent Intelligent Document Space:
[https://docs.qq.com/space/DUkRjYUtNWFdyV253](https://docs.qq.com/space/DUkRjYUtNWFdyV253)
>
>According to Status-Relational Entropy (SRE) principles, fundamental classical physics originates from information statistics.

### Framework Positioning Statement

The theory of hierarchical dissipative self-organizing binary-network dynamics presented herein constitutes **the underlying discrete network foundation for the self-emergent cosmic picture within the Status-Relational Entropy (SRE) Dynamics framework**.

This theory provides a computable set of discrete evolutionary axioms. Starting from simple binary spins and asynchronous activate-dormancy mechanisms, spacetime, gravitation, the speed of light and other physical quantities are not pre-implanted. A topologically coherent kernel emerges spontaneously through finite-size scaling phase transitions.

This underlying network undergoes two successive layers of abstract generalization:

1. Ontological refinement via the SRE v1.6 axiom suite, which defines general ontological concepts including causal nodes, pending-for-instantiation states, dissipation-compensation duality, reciprocal measurement, and multi-scale homomorphic mapping.
2. Further mathematical upgrade incorporating spectral-graph theory, the Baik-Ben Arous-Péché (BBP) spectral phase transition, and conformal-gauge transformations, yielding the SRE v6.0 cosmological framework. Metric geometry, variable-speed-of-light effects, gravitational dynamics, and gravitational-lensing step-jump observational predictions are derived within this higher-level framework.

Note that the present paper treats only the axioms, evolutionary equations, and scaling theorems of the underlying binary network. Cosmological-scale derivations and observational-data validation are the scope of the subsequent SRE v6.0 main paper and are not developed here.

## I. Foundational Physical Axioms of the System

### 1. Strict Binary Constraint

The state of the system after the $n$-th pulse evolution is characterised by a real-symmetric square matrix $M_{n}\in\mathbb{R}^{n\times n}$. The entire evolutionary process contains no continuous-function truncation and no dissipative zero state. Matrix elements are strictly restricted to the binary-spin set:
$$
\forall\ S_{ij}\in{+1,-1},\quad S_{ij}=S_{ji}
$$
The initial evolutionary baseline is a first-order non-zero single-point seed source:
$$
M_{1}= [1]
$$

### 2. Asynchronous Binary Activation (Microscopic Point-by-Point Asynchronous-Activation Uncertainty)

The system adopts an asynchronous-update mechanism on a discrete topology. At each dimensional outward expansion $n\to n+1$, every historical lattice point $(i,j)$ of the old matrix determines its activation state in the current evolutionary step via an endogenous binary stochastic decision gate:

- Dormant state $\chi_{(i,j)}=0$: the lattice point does not participate in the current step; information conduction is truncated. Algebraically, it contributes as multiplication by unity in the continued-product operation.
- Active state $\chi_{(i,j)}=1$: the lattice point is normally activated, bringing its original $\pm1$ spin value into the evolution.

### 3. Dynamic Geodesic Field (Global Dynamic Geodesic-Depth Rheology)

Topological relations of the system are defined entirely by algebraic topological adjacency among nodes. The cumulative topological step length from any historical lattice point $(i,j)$ to the current evolutionary frontier grows synchronously as system order expands, manifesting as global dynamic redshift rheology:
$$
d_{n}(i,j)=n-\max(i,j)
$$

## II. Endogenous Dynamical Definition of Probability $p$

The dormancy probability $p_{ij}^{(n)}$ for lattice point $(i,j)$ at step $n$ is determined endogenously by the local frustration tension at that location together with global scale factors.

### 1. Local Frustration Energy

The coherent-tension inner product for lattice point $(i,j)$ on the matrix intersection manifold is defined:
$$
E_{\mathrm{local}}(i,j)=\left|\sum_{k=1}^{n}S_{ik}\cdot S_{kj}\right|
$$
Smaller absolute values indicate stronger cancellation of positive-negative polarities, corresponding to higher local geometric frustration; such links tend to degenerate into dormant edge states.

### 2. Adaptive Energy-Level Mapping Equation

Combined with cumulative topological step-length $d_{n}(i,j)$, the lattice-point dormancy probability is rigorously defined:
$$
p_{ij}^{(n)}=\mathrm{Pr}\big(\chi_{(i,j)}=0\big)=1-\frac{1}{1+\lambda\cdot \dfrac{n-\max(i,j)}{E_{\mathrm{local}}(i,j)+1}}
$$
where $\lambda\in\mathbb{R}^+$ denotes the endogenous coupling constant of the system.

**Physical corollaries of this definition:**

- Microscopic newborn layer: $n-\max(i,j)\to0$. Newborn nodes have step-length approaching the evolutionary frontier, giving $p_{ij}^{(n)}\to0$. Microscopic newborn units tend to deterministic activation updates, guaranteeing local-manifold geometric rigidity.
- Macroscopic ancient layer: $n-\max(i,j)\gg0$. As evolution proceeds, cumulative topological step-lengths for ancient nodes increase monotonically, and dormancy probability rises spontaneously. Large-scale domains enter dormancy; long-range coherence is diluted by spontaneous system-internal dissipation.

## III. Core Evolutionary Equation and Global Adaptive Negative-Feedback Damping

When the system undergoes dimensional expansion triggered by the $(n+1)$-th pulse, each matrix element $S_{i,n+1}$ on the new boundary propagates following a point-wise nonlinear continued-product feedback equation:
$$
S_{i,n+1}=\prod_{j=1}^{n}\Big[\chi_{(i,j)}\cdot S_{ij}+\big(1-\chi_{(i,j)}\big)\Big],\quad i=1,2,\dots,n
$$
The bottom-rightmost diagonal matrix element acts as an endogenous energy-balance regulating valve for the system. It carries no stochastic gate and strictly enforces global algebraic adaptive negative-feedback damping, stabilising the global net-spin pool at each evolutionary step:
$$
S_{n+1,n+1}=
\begin{cases}
-1,& \displaystyle\sum_{x=1}^{n}\sum_{y=1}^{n}S_{xy}\ge 0 \\[6pt]
+1,& \displaystyle\sum_{x=1}^{n}\sum_{y=1}^{n}S_{xy}<0
\end{cases}
$$

## IV. Macroscopic Dynamical Emergence and Finite-Size-Scaling Asymptotic-Convergence Theorems

Emergence of system spatial dimension is not an instantaneous observation at some discrete step count (e.g., $N=250$). Instead it represents asymptotic phase-transition behaviour under the thermodynamic limit via finite-size scaling.

### Theorem 1: Statistical Condensation of Local Stable Manifolds and Order-Parameter Convergence

To exclude pseudo-emergence caused by finite-size effects, we take microscopic-core surviving units (the first $k$ sub-matrix rows/columns, with $k=\lfloor 0.2N\rfloor$) and define the topological-coherence order parameter:
$$
\Phi(N)=1-\frac{\mathrm{Var}\big(\mathrm{Tr}(M_{k})\big)}{k^2}
$$
Numerical and analytical derivations show that as total pulse steps go to infinity $N\to\infty$, even though macroscopic boundaries exhibit large uncertainties from asynchronous activation, the order-parameter for the ancient core region obeys strict asymptotic boundedness:
$$
\lim_{N\to\infty}\Phi(N)=\Phi_0>0
$$
This non-zero constant $\Phi_0$ rigorously demonstrates that condensation of the system’s local stable manifold is not an accidental finite-step fluctuation. It is a statistically asymptotically stable core established by feedback suppression from the high-dimensional renormalisation pool.
This asymptotic-convergence behaviour is directly observable in numerical simulations; see the $\Phi(N)$ convergence plots in the middle column of Figure 1.

### Theorem 2: Coherence-Length Decay and Hierarchical Fragmentation under Scaling Cascades

Spatial dimension and geometric curvature within the lattice obey a progressive-dissipation rule: “each outward layer brings one degree of coherence weakening”. Define the two-point sign-correlation decay function against topological step-size $x$:
$$
G(x)=\langle S_i\cdot S_{i+x}\rangle \propto e^{-x/\xi}
$$
where $\xi$ denotes the effective coherent correlation length.

During finite-size-scaling cascades, rheology of coherence length with total system size $N$ satisfies:
$$
\lim_{N\to\infty}\frac{\xi(N)}{N}=0
$$
This limit rigorously proves that three structural regimes arising from spontaneous system phase transition are macroscopically distinguishable:

1. **Microscopic core layer** ($x\le\xi$): dormancy probability $p\approx0$, the system maintains very high topological coherence and rigidity. Observed via Multidimensional Scaling (MDS), high-dimensional eigenvalues collapse toward zero, and positive-definite three-dimensional manifolds together with local curvature emerge spontaneously within this layer.
2. **Mesoscopic intermediate layer** ($\xi<x\sim2\xi$): crossing the correlation-length scale triggers avalanche-like cascade amplification within continued-product causal chains. Manifold resilience against stochastic-dormancy perturbations decays exponentially; geometrically rigid lattice structures undergo nonlinear bending and bifurcation.
3. **Macroscopic thermal-dissipation layer** ($x\gg\xi$): long-range coherence is fully diluted and decoupled by abundant dormant points. Original system structure disintegrates and returns to an isotropic chaotic state.

Simulation results are shown in Figure 1; the MDS three-dimensional manifold on the right-hand side visualises this three-layer hierarchical structure.

![Figure 1](./figures/3_runs_complete_comparison.png)
**Figure 1. Unified verification simulation for hierarchical-dissipation dynamics. Three independent random seeds (1111, 2222, 3333), evolution steps $(N=300)$, coupling parameter $\lambda=0.8$.**
Left column: matrix heatmaps of the network. Middle column: evolution curves for topological-coherence order-parameter $\Phi(N)$; red dashed lines mark asymptotic limit $\Phi_0$. Right column: emergent three-dimensional manifold obtained via MDS embedding. Simulations verify the asymptotic-convergence behaviour of Theorem 1 and visualise the three-layer hierarchical structure predicted by Theorem 2: high-coherence microscopic core, mesoscopic intermediate zone, and macroscopic dissipative outer layer.

## V. Theoretical Conclusion

This paper establishes a finite-size-scaling asymptotic evolutionary model for non-equilibrium binary-network self-organised phase transitions.

The theory demonstrates that matter (damping of $\pm1$ spins under polar frustration), space (dynamic distance defined via topological geodesics), gravitation (relative path contraction-convergence and spatial evaporative-dissipation arising from local dormancy), and three-dimensional space itself require no hard-coded presupposition at the underlying level.

Taking microscopic point-wise binary activate-dormancy uncertainty as its underlying engine and global algebraic continued-multiplication as causal bonds, the system can spontaneously condense self-organised spacetime on finite-size-scaling phase-transition lines without invoking external continuous probability waves, as system size approaches the thermodynamic limit. The microscopic core yields geometrically positive-definite stable structure, while outward hierarchical expansion is accompanied by progressive dissipation. This asymptotic phase-transition structure, transitioning from non-integer dimensions toward integer three-dimensionality, constitutes the intrinsic macroscopic-thermodynamic limiting phase of this discrete computational model.

> 
> **Methodological Supplementary Remark (added in v1.1)**
> Multidimensional Scaling (MDS) serves only as an offline post-processing numerical prototype. MDS reads static snapshots of the binary network and embeds pairwise topological relations into three-dimensional Euclidean space. Spatial distances within this embedded manifold are emergent representations of node relational-profile similarity; **Euclidean geometric distance does not pre-exist within the underlying binary-network ontology**. This static-snapshot embedding is conceptually distinct from the event-driven, incremental-instantiation mechanism characterising the full SRE-Dynamics physical-rendering-layer. Embedding artefacts appear in strongly-dissipative outer regimes beyond the coherence length $\xi$, where the validity of low-dimensional geometric descriptions degrades.

---

## Appendix A Conceptual Distinctions and Applicable Boundaries for MDS Numerical Embedding (added in v1.1)

### A.1 Conceptual Distinction between MDS Simulation Prototype and the SRE Physical-Rendering-Layer

Within the accompanying simulation script `sim_P.py`, Multidimensional Scaling (MDS) operates as **snapshot-oriented offline post-processing**: after full network evolution to a specified step count, the complete final-state matrix is taken, and pairwise topological relations for all nodes are projected in a single pass onto three-dimensional Euclidean coordinates.

This numerical workflow possesses two key features:

1. It is not incremental-difference rendering: only complete snapshots of all node-topology relations are input; only differential changes per evolutionary step are not rendered.
2. It performs homomorphic dimensional reduction rather than isomorphic copying: the underlying object is high-dimensional discrete binary topology possessing no Euclidean coordinates. MDS executes many-to-one coarse-graining and information compression. Numerous microscopic degrees-of-freedom including underlying spin signs, activate-dormancy stochastic gates, and local frustration are not fully preserved within three-dimensional output.

By contrast, the **physical-rendering-layer** defined in the SRE v1.6 ontological framework is an event-driven incremental-instantiation system:
The underlying causal network undergoes continuous asynchronous-link fluctuations. The vast majority of transient perturbations fail instantiation-cost thresholds and remain in the pending-for-instantiation state without projection onto spacetime. **Only causal relations completing one full round of reciprocal measurement together with dissipation-compensation settlement update distance- and time-bookkeeping records within the rendering layer.**

> 
> MDS simulation: static characterisation of an already-evolved system, answering what three-dimensional manifold would arise via homomorphic projection given statistically stable topology.
> SRE physical-rendering-layer: real-time incremental instantiation triggered by reciprocal-measurement events; the ontological mechanism corresponding to real-world physical cosmology. The two must not be treated as directly equivalent.

### A.2 Intuitive Rules and Failure Conditions for MDS Manifold Distances

Geometric distances output by MDS embedding follow this statistical tendency:

> 
> If two nodes exhibit highly similar patterns of causal association (relational-profiles) with all remaining network nodes, their Euclidean distances within the three-dimensional embedded manifold tend to be small.

This property corresponds to SRE ontological intuition: macroscopic spatial distance characterises the degree of coherence degradation between events. More similar relational-profiles imply lower mutual information dissipation, smaller topological-compensation cost, and correspondingly smaller macroscopic metric distance.

This rule-of-thumb has strict applicability boundaries:

- **Microscopic core region ($x\le\xi$, high order-parameter $\Phi(N)$)**: high network topological coherence yields good MDS dimensional-reduction fidelity; the relational-profile versus manifold-distance correspondence holds.
- **Mesoscopic / macroscopic strong-dissipation regimes ($x>\xi$)**: abundant stochastic link dormancy creates highly disordered topology; no low-dimensional geometry can perfectly represent all high-dimensional relations. MDS produces minimal-loss approximate fits and embedding artefacts may occur: nodes with substantially different underlying relational-profiles may lie accidentally close geometrically, while minor topological differences may be artificially amplified during dimensional compression. Under these conditions low-dimensional geometric descriptions degrade, and the relational-profile / manifold-distance correspondence becomes unreliable.

### A.3 Correspondence with the Full SRE System

Phenomena within the binary-network simulation can be mapped in parallel to SRE ontological concepts, though direct identification is not permitted:

1. Link dormancy $\chi_{ij}=0$ ⇔ irreversible information dissipation (microscopic origin of the topological-dissipation tensor $\hat{\mathcal{D}}_{ij}$ in cosmological papers).
2. MDS dimensional-reduction embedding ⇔ numerical demonstration prototype for multi-scale homomorphic mapping.
3. Core / meso-scale / outer-layer tripartite division ⇔ multi-scale rigid coherence-truncation boundary filtering mechanism.
4. Finite-size-scaling phase transition ⇔ underlying discrete prototype for the BBP spectral phase transition ($z_{\mathrm{crit}}=4.1605$, 2D-holographic ↔ 4D-spacetime switching).

> 
> Note: the binary network itself contains no built-in spacetime, gravitational constant, or speed of light. All such physical quantities are macroscopic statistical effects emerging inside the rendering-layer after homomorphic-mapping filtering.

> 
> In summary, this binary network constitutes the discrete computational substrate for SRE’s self-emergent cosmic picture. Full cosmological physical predictions require ontological abstraction plus spectral-matrix mathematical upgrades; refer to the accompanying SRE v6.0 paper.

### A.4 Version-Change Notes

> 
> v1.1 update record:
> 
> 
> 1. Added brief MDS methodological warning at the end of Chapter 5 Theoretical Conclusion.
> 2. Added Appendix A giving full conceptual distinction between the MDS numerical prototype and the SRE physical-rendering-layer, together with applicable-boundary discussion.
> 3. The v1.0 manuscript is fully preserved in the Zenodo archive for historical traceability and is not overwritten.
