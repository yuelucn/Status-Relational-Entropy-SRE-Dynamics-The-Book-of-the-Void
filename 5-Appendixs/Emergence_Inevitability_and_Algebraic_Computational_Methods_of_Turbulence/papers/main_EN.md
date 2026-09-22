# Emergence Inevitability and Algebraic Computational Methods of Turbulence Based on Discrete Microscopic Causal Statistics and Multidimensional Manifold Reconstruction

**Version: 2.0 (revised)**
Numerical baseline: `sre_core.py` · Dataset: `phase_data_v2.json` · Interactive check: `sim/console_EN.html`

This document is the English counterpart of `main_CN.md` v2. Section numbering, theorem
labels (Theorem 3 / 6 / 7) and every numerical claim are kept in one-to-one
correspondence with the Chinese version. Where the two disagree, the Chinese
version governs.

---

## 0. Revision notes

| ID | Defect in v1 | Treatment here |
| :--- | :--- | :--- |
| **R1** | §2.2 defined $P_{\text{active}}=1/(1+e^{-\Delta S})$ yet asserted $P_{\text{active}}\to0$ as $\Lambda\to\infty$. The formula gives the opposite limit. | Replaced by $P_{\text{active}}=1/(1+e^{\Psi})$ with $\Psi\equiv\beta\Lambda\mathbf{D}-\alpha\operatorname{Tr}(A^TA)$. See §3.2 |
| **R2** | $\beta\Lambda\mathbf{D}$ was labelled the *destabilising* term, but $\Lambda\propto1/Re$ so large $\Lambda$ means laminar. | Relabelled: $\beta\Lambda\mathbf{D}$ is the smoothing (ordering) term; $\alpha\operatorname{Tr}(A^TA)$ is the generation (destabilising) term |
| **R3** | No split of $M$ into symmetric and antisymmetric parts. The reference implementation even forced $M_{vm,v_f}=-M_{v_f,v_m}$, making $M$ globally antisymmetric — incompatible with "$A$ is the antisymmetric *part* of $M$", and an antisymmetric matrix is rejected by MDS as a precomputed dissimilarity | Strict bipartition: $\mathbf{S}=(M+M^T)/2$ carries the metric and all geometry; $\mathbf{A}=(M-M^T)/2$ carries chirality. See §2.2 |
| **R4** | §5 claimed the constraint $M_{n+1}[1{:}n,1{:}n]\equiv M_n$ had been "completely abolished"; it was in fact present throughout | Clarified as a **defining component** of the Operator 1 structural equation, not an external patch. See §4.1 |
| **R5** | The endogenous spectral-radius parameter $\lambda(n)$ of Theorem 7 displaced the exogenous $\Lambda$, leaving "$\Lambda$ controls the transition" with no counterpart in code | $\Lambda$ and $\lambda(n)$ are explicitly separated; two modes are defined and compared. See §4.3 and §6.3 |
| **R6** | A "unique critical point $\Lambda_c$" was claimed | Measured as a smooth crossover spanning ~1.5 decades; downgraded to a **transition band** with a stated width. See §6.2 |
| **R7** | A "1D rigid axis" emerging at high Reynolds number was claimed | Sensitive to the metric-reconstruction criterion (two MDS criteria give opposite trends); not a robust result. See §6.5 |
| **R8** | "Strict collapse onto Kolmogorov $k^{-5/3}$" was claimed | The measured 1D proxy slope is ≈ −1.85 and drifts further from −5/3 as $N$ grows. Restricted to a proxy indicator. See §6.6 |
| **R9** | The choice of metric-reconstruction criterion was not reported | New §6.1 with a controlled comparison |

---

## 1. Introduction and physical image

The classical Navier-Stokes equations formulate fluids as absolutely continuous
media. When explaining the mechanism of turbulence, microscopic thermal motion and
energy fluctuations are amplified by the non-linear advection term, which within the
continuum readily triggers singularities (blow-up) and divergence. This has long
been a bottleneck for classical continuum mechanics.

This paper proposes a discrete dynamical paradigm. Rather than treating a fluid as
pressure and velocity fields over a continuous space, we reconstruct it as a
statistical information network governed by causal correlations among a large
number of discrete microscopic states.

* **Space-time is non-prior**: geometry is not a pre-existing stage; the bedrock is
  a discrete, dimensionless causal network.
* **Spontaneous macroscopic emergence**: geometry is a macroscopic consequence of
  the algebraic evolution of correlative distances among microscopic states.

The aim is an axiomatic statement of the paradigm, a proof that it degenerates to
the N-S equations in the continuum limit, and — critically — **reproducible
numerical tests of every quantitative claim**. All numbers in §6 are produced by
`sre_core.py`.

---

## 2. Basic objects and dimensional system

### 2.1 Dimensional basis

Three independent bases span the dimensional system: the elementary causal clock
step $[\tau]$, the ground-state topological distance $[\ell]$, and the elementary
information action $[H]$.

* **State matrix $M\in\mathbb{R}^{n\times n}$**: binary causal correlation matrix,
  $M_{ij}\in\{-1,+1\}$, **generally non-symmetric**.
* **Intrinsic relaxation time $\tau_0$** and **macroscopic characteristic time
  $T$**, both of dimension $[\tau]$. The dimensionless dissipation coefficient is

$$\Lambda \equiv \frac{\tau_0}{T} \propto \frac{1}{Re}$$

### 2.2 Strict symmetric / antisymmetric bipartition (fixes R3)

$$\mathbf{S} \equiv \frac{M + M^T}{2}, \qquad \mathbf{A} \equiv \frac{M - M^T}{2}$$

* **$\mathbf{S}$ — topological metric part.** Symmetric; it is the sole legitimate
  input to multidimensional scaling. All geometric reconstruction (manifold
  coordinates, anisotropy) acts on $\mathbf{S}$ only.
* **$\mathbf{A}$ — local spin operator.** The antisymmetric shear component; its
  quadratic form $\operatorname{Tr}(A^TA)=\sum_{i,j}A_{ij}^2$ is the local vortex
  action flux out of equilibrium.

The relation is exclusive and exhaustive: $M$ non-symmetric $\iff$ $\mathbf{A}\neq0$
$\iff$ the system carries chirality.

> The v1 implementation forced $M_{vm,v_f}=-M_{v_f,v_m}$, making $M$ globally
> antisymmetric. Then $\mathbf{A}\equiv M$ and $\mathbf{S}\equiv0$: the phrase
> "$A$ is the antisymmetric part of $M$" degenerates to an identity, and
> $\mathbf{S}=0$ means the metric vanishes altogether. The present version keeps
> $M$ generally non-symmetric. Measured at $N=60$, $\Lambda=10^{-2}$, the
> antisymmetric share $\operatorname{Tr}(A^TA)/\operatorname{Tr}(M^TM)=0.947$:
> most correlation energy is indeed carried by the chiral part, yet $\mathbf{S}$
> remains non-degenerate.

---

## 3. Axiomatic derivation of the criterion operator

### 3.1 Maximum-entropy master equation

Define the **discriminant** (smoothing minus generation):

$$\Psi \equiv \beta\Lambda\mathbf{D} - \alpha\operatorname{Tr}(A^TA)$$

with dimensionless constants $\alpha,\beta$ and normalised topological distance
matrix $\mathbf{D}$ (fixes R2):

1. **$\beta\Lambda\mathbf{D}$ — ordering (smoothing) term.** Large $\Lambda$ means
   fast local relaxation: differences are erased as soon as they appear.
2. **$\alpha\operatorname{Tr}(A^TA)$ — destabilising (generation) term.** Higher
   local spin coherence means a stronger capacity to regenerate differences.

### 3.2 Activation probability and sign convention (fixes R1)

$$\boxed{P_{\text{active}} = \frac{1}{1 + e^{\Psi}} = \frac{1}{1 + \exp\!\big(\beta\Lambda\mathbf{D} - \alpha\operatorname{Tr}(A^TA)\big)}}$$

Limiting behaviour is now consistent with the physics:

* $\Lambda\to+\infty$ (very low $Re$): $\Psi\to+\infty$, $P_{\text{active}}\to0$ —
  deterministic laminar phase.
* $\Lambda\to0$ (very high $Re$): $\Psi\to-\alpha\operatorname{Tr}(A^TA)\le0$, so
  $P_{\text{active}}\ge\tfrac12$, approaching $1$ when the chiral level is
  significant — fluctuations are fully activated.

> v1 wrote $P_{\text{active}}=1/(1+e^{-\Delta S})$ while asserting
> $P_{\text{active}}\to0$ as $\Lambda\to\infty$; these cannot both hold. The sign
> in the exponent is corrected here. The critical condition $\Psi=0$ yields the
> same $\Lambda_c$ expression as v1, so v1's qualitative conclusions survive.

### 3.3 Critical condition (fixes R6)

$$\Lambda_c = \frac{\alpha\operatorname{Tr}(A^TA)}{\beta\mathbf{D}}$$

Since $\partial\Psi/\partial\Lambda=\beta\mathbf{D}>0$, $\Psi$ is strictly
increasing in $\Lambda$ and $\Psi=0$ has at most one root. **Existence of the root
does not imply a sharp transition**: §6.2 shows the macroscopic order parameter
evolves smoothly across roughly 1.5 decades. $\Lambda_c$ is therefore called the
**centre of the transition band**, not a thermodynamic critical point.

---

## 4. Operator system

Cascade: $M(t+\tau)=\mathcal{O}_3\circ\mathcal{O}_2\circ\mathcal{O}_1\,[M(t)]$.

### 4.1 Operator 1 — boundary expansion $\mathcal{G}_{n\to n+1}$ (clarifies R4)

$$M_{n+1} = \mathcal{G}_{n\to n+1}(M_n) = \begin{pmatrix} M_n & \mathbf{x}_{n+1} \\ \mathbf{x}_{n+1}^T & y_{n+1} \end{pmatrix}, \qquad M_{n+1}[1{:}n,1{:}n] \equiv M_n$$

> **Clarification.** v1 §5 claimed this constraint had been "completely abolished".
> It was present throughout, and **it should not be abolished**: it is a defining
> component of the Operator 1 structural equation, encoding read-only history.
> Without it, $\mathcal{G}_{n\to n+1}$ degenerates into an arbitrary rewriting
> operator and causal inheritance is undefined. Its axiomatic status is retained
> here: **history, once realised, cannot be retroactively modified**. The v1 claim
> of "no artificial hardcoding" should be read as "no empirical fitting
> coefficients and no phenomenological drag corrections", not "no structural
> constraints".

**Theorem 3 (diagonal invariant).** On the binary domain $\Phi(x)\in\{-1,1\}$,

$$\Phi\big((M_{n+1}^2)_{n+1,n+1}\big) = \sum_{m=1}^{n}\Phi(x_{n+1,m})^2 + \Phi(y_{n+1})^2 = n + 1$$

### 4.2 Operator 2 — maximum-entropy pruning $\mathcal{M}_\chi\circ\mathcal{E}_{\text{local}}$

Local multi-circuit interference polynomial (2-step walk) between frontier node
$v_f$ and historical node $v_m$:

$$\tilde{\mathcal{E}}_{\text{local}}(v_f,v_m) = \sum_{v_k\in\mathcal{N}(v_f)\cap\mathcal{N}(v_m)} M(v_f,v_k)M(v_k,v_m) + 2M(v_f,v_m)$$

with $\mathcal{E}_{\text{local}}=|\tilde{\mathcal{E}}_{\text{local}}|$, barrier
$\mathfrak{B}=\mathcal{E}_{\text{local}}+\exp(\operatorname{sgn}\tilde{\mathcal{E}}_{\text{local}})$,
and dimensionless causal depth $\mathcal{D}_s=(n+1)-\sigma(v_m)$.

**Theorem 6 (pruning master equation).**

$$p_{\text{prune}}(v_f,v_m) = 1 - \frac{1}{1 + \Gamma\cdot\dfrac{\mathcal{D}_s}{\mathfrak{B}}}$$

where $\Gamma$ is the **pruning gain** (§4.3). Under pruning ($\chi=0$) the
Elimination-Conduction mechanism (Paradigm B) applies:

$$M_{n+1}(i,j) \leftarrow \chi\cdot M_{n+1}(i,j) + (1-\chi)\cdot 1$$

forcing the spin to the multiplicative identity $+1$, which erases the channel's
phase contribution from the product feedback loop without severing graph
connectivity. Surviving channels ($\chi=1$) receive an antisymmetric chiral shear.

### 4.3 The gain $\Gamma$: exogenous $\Lambda$ vs endogenous $\lambda(n)$ (fixes R5)

Theorem 7 removed the circular dependency between operators via the spectral radius
of the previously realised sub-graph:

$$\lambda(n) = \frac{1}{\beta}\cdot\frac{\ln\!\big(1+\rho(\mathbf{A}_{n-1})\big)}{n+1}$$

By Perron-Frobenius the spectral radius is a unique algebraic invariant, so
$\lambda(n)$ has a unique real analytic value at each frontier expansion. However,
v1 let $\lambda(n)$ **fully replace** $\Lambda$, expelling the macroscopic
dissipation authority from the evolution equation.

Here the two are explicitly separated:

| Mode | Gain $\Gamma$ | Meaning |
| :--- | :--- | :--- |
| **A (exogenous)** | $\Gamma = \Lambda$ | $\Lambda$ acts directly as the transition control |
| **B (adaptive)** | $\Gamma = \Lambda\cdot\lambda(n)$ | Theorem 7 adaptive correction on top of $\Lambda$ |

Both factors are dimensionless, so dimensional consistency is preserved. §6.3
compares the two empirically.

### 4.4 Operator 3 — pentagonal parity breaking and logical emergence

To break the parity degeneracy of the pure spin-product space, a 5-node
non-homogeneous array with a fixed inversion anchor is introduced ($n:5\to6$):

$$\mathbf{M}_5 = \begin{pmatrix} 1 & 1 & -1 & 1 & 1 \\ 1 & 1 & -1 & 1 & 1 \\ -1 & -1 & -1 & 1 & 1 \\ 1 & 1 & 1 & 1 & 1 \\ 1 & 1 & 1 & 1 & 1 \end{pmatrix}$$

Nodes 1 and 2 are inputs $A,B$; node 3 is the rigid inversion anchor (self-loop and
cross edges hard-coded to $-1$); nodes 4 and 5 are inert $+1$ boundary subgraphs.
With activation mask $\boldsymbol{\chi}=[1,1,1,0,0]^T$,

$$Y_{\text{spin}} = \operatorname{sgn}\!\left(\tfrac12(S_{1,6}+S_{2,6}) - S_{3,6}\right), \qquad \operatorname{sgn}(0)\to+1$$

The four input combinations map through $f(S)=(1-S)/2$ to $\{1,1,1,0\}$ — a standard
**NAND** gate — completing the Turing-completeness argument. The topological
difference it creates is permanently locked and resists erasure by Paradigm B.

---

## 5. Continuum limit and compatibility with N-S

Let $\tau\to0$, $\ell\to0$, mapping $M_{ij}$ to a multi-point correlation function
$M(\mathbf{x},\mathbf{y},t)$ and defining macroscopic moments:

$$\rho(\mathbf{x},t)=\int M\,d\mathbf{y}, \qquad \rho\mathbf{u}(\mathbf{x},t)=\int\frac{\mathbf{x}-\mathbf{y}}{\tau}M\,d\mathbf{y}$$

As $\Lambda\to\infty$ with vanishing fluctuations, the transition probability
degenerates to a Dirac $\delta$ evolution and the algebraic operator becomes a
continuous master equation:

$$\frac{\partial M}{\partial t} + \nabla_{\mathbf{x}}\cdot\left(\frac{\mathbf{x}-\mathbf{y}}{\tau}M\right) = \mathcal{C}[M]$$

A Chapman-Enskog expansion in $\epsilon=\ell/L$,
$M=M^{(0)}+\epsilon M^{(1)}+\mathcal{O}(\epsilon^2)$, gives:

1. **First moment** — continuity equation $\partial_t\rho+\nabla\cdot(\rho\mathbf{u})=0$;
2. **Second moment** — momentum conservation
   $\int(\mathbf{x}-\mathbf{y})\mathcal{C}[M]d\mathbf{y}=0$ yields the advection
   term, while $M^{(1)}$ contributes the viscous stress tensor under symmetry
   breaking. Since $\Lambda\equiv\tau_0/T$, the kinematic viscosity is formally
   $\nu=\zeta\,\ell^2\Lambda$.

Hence

$$\rho\left(\frac{\partial\mathbf{u}}{\partial t}+(\mathbf{u}\cdot\nabla)\mathbf{u}\right) = -\nabla p + \rho\,\zeta\ell^2\Lambda\,\nabla^2\mathbf{u}$$

which is the standard Navier-Stokes equation.

> **Caveat.** $\zeta$ is an undetermined network geometric constant; it is not
> derived from first principles here, nor calibrated against direct numerical
> simulation. This section establishes **structural compatibility** (the discrete
> master equation carries the N-S moment structure), not quantitative equivalence.
> $\nu=\zeta\ell^2\Lambda$ is a dimensional-analysis correspondence pending
> calibration.

---

## 6. Empirical verification

All numbers from `sre_core.py`: $N=60$, five seeds (0–4), dataset
`phase_data_v2.json`.

### 6.1 Method: choice of metric-reconstruction criterion (new, R9)

Dissimilarities are taken from the symmetric part:
$d_{ij}=\sqrt{\max(0,\,2-2S_{ij})}$. Two criteria exist for recovering 3D
coordinates. This work adopts **classical MDS (Torgerson)**: eigendecomposition of
the double-centred Gram matrix $\mathbf{B}=-\tfrac12\mathbf{J}\mathbf{D}^{(2)}\mathbf{J}$,
retaining the top three eigenvectors.

Rationale: it is a closed-form solution — deterministic, reproducible, and free of
local minima. That matters here, since avoiding local minima is precisely what this
paradigm claims over gradient-based approaches.

The two criteria nevertheless give **opposite** anisotropy trends ($N=60$, seed 0):

| $\Lambda$ | classical MDS (strain) | SMACOF (stress, converged) |
| ---: | ---: | ---: |
| $10^{-3}$ | 0.3720 | 0.3338 |
| $10^{-2}$ | 0.3635 | 0.3365 |
| $10^{-1}$ | 0.3686 | 0.3573 |
| $1$ | 0.3422 | 0.3682 |
| $10$ | 0.3546 | 0.4634 |

SMACOF stress is stable after `max_iter=1000` (653.79, no further descent), so the
discrepancy is **not** under-convergence — it is a different objective function.
This methodological uncertainty bears directly on §6.5.

### 6.2 Mode A — phase diagram under exogenous $\Lambda$ (fixes R6)

| $\Lambda$ | $Re\propto1/\Lambda$ | structure density | sd | anisotropy | slope | sd |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| $10^{-4}$ | $10^{4}$ | 0.4915 | 0.0001 | 0.4308 | −1.851 | 0.055 |
| $10^{-3}$ | $10^{3}$ | 0.4901 | 0.0004 | 0.3753 | −1.847 | 0.151 |
| $10^{-2}$ | $10^{2}$ | 0.4764 | 0.0016 | 0.3587 | −1.824 | 0.326 |
| $10^{-1}$ | $10$ | 0.3809 | 0.0023 | 0.3515 | −1.566 | 0.250 |
| $3.16\times10^{-1}$ | $3.16$ | 0.2622 | 0.0026 | 0.3510 | −0.556 | 0.935 |
| $1$ | $1$ | 0.1435 | 0.0046 | 0.3501 | +0.207 | 1.414 |
| $3.16$ | $0.32$ | 0.0647 | 0.0026 | 0.3618 | +0.124 | 0.762 |
| $10$ | $0.1$ | 0.0254 | 0.0024 | 0.3600 | +0.264 | 1.080 |
| $10^{2}$ | $10^{-2}$ | 0.0026 | 0.0004 | 0.3715 | +0.442 | 0.095 |

Structure density falls monotonically from 0.4915 to 0.0026 in a smooth sigmoid.
Defining the band by structure density decreasing from 0.40 to 0.08:

$$\Lambda \in [\,8\times10^{-2},\ 2.5\,], \qquad Re\propto1/\Lambda \in [\,0.4,\ 12\,]$$

**The band spans about 1.5 decades.** Seed-to-seed sd stays $\le0.005$ throughout,
so the smoothness is intrinsic rather than noise.

> The framework does **not** support a sharp critical point. What can be robustly
> claimed is a monotone, reproducible structure-dissipation crossover roughly 1.5
> decades wide. For $\Lambda>10^{2}$ structure density drops below $10^{-2}$, the
> distance matrix becomes nearly null and MDS loses meaning (omitted).

### 6.3 Mode B — consequences of engaging Theorem 7 (fixes R5)

| $\Lambda$ | structure density | slope |
| ---: | ---: | ---: |
| $10^{-2}$ | 0.4914 | −1.854 |
| $1$ | 0.4673 | −1.842 |
| $3.16$ | 0.4186 | −1.672 |
| $10$ | 0.1676 | −0.484 |
| $10^{2}$ | 0.0269 | +0.136 |

The same crossover now occurs at $\Lambda\approx3\sim30$, about **two decades** later
than in mode A.

Cause: $\lambda(n)$ decays from 0.315 to 0.010 over $n$ (at $N=60$), averaging
$\sim10^{-2}$, systematically shrinking the effective gain. The decay also means the
**effective pruning strength decreases with evolution time** — an intrinsic
temporal non-stationarity (strong pruning early, weak later).

> Engaging Theorem 7 preserves the qualitative structure (monotone crossover and
> slope plateau both survive) but (i) rescales the effective magnitude of $\Lambda$
> and (ii) introduces decay-type temporal non-stationarity. Both are the price of
> decoupling the circular dependency; v1 did not mention them.

### 6.4 Finite-size check

| $N$ | $\Lambda=10^{-3}$ | $\Lambda=10^{-1}$ | $\Lambda=1$ |
| ---: | ---: | ---: | ---: |
| 40 | 0.4870 | 0.4020 | 0.1759 |
| 60 | 0.4901 | 0.3809 | 0.1435 |
| 80 | 0.4922 | 0.3608 | 0.1212 |
| 100 | 0.4927 | 0.3452 | 0.1062 |

* **High-$Re$ side ($\Lambda=10^{-3}$) has converged**: 0.487 → 0.493 from
  $N=40$ to $100$, a change under 1.5%.
* **Transition band ($\Lambda=10^{-1},1$) has not**: density keeps falling (at
  $\Lambda=1$, 0.176 → 0.106, a 40% drop).

> The **quantitative position of the band is $N$-dependent** and must not be
> extrapolated to $N\to\infty$. Only the qualitative claim — a monotone crossover
> exists — is robust.

### 6.5 On the "1D rigid axis" (fixes R7)

v1 claimed that at high Reynolds number the MDS reconstruction spontaneously
exhibits a "highly connected rigid centreline" (red core) wrapped by a dissipative
shell. The present tests do not support this strong claim:

* Under classical MDS, anisotropy $\lambda_1/\sum\lambda$ stays within
  **0.34–0.43** for $\Lambda\in[10^{-4},10]$; the variation is of the same order as
  the seed-to-seed sd (up to 0.08 at the extremes), with no drift towards 1. Since
  $1/3$ is perfect isotropy, the measured values sit only marginally above the
  isotropic baseline.
* Anisotropy rises above 0.86 only in the **degenerate, over-damped regime**
  ($\Lambda\ge10^{2}$, structure density $<10^{-2}$), where the network is almost
  entirely $+1$, the MDS input is near-singular, and the number carries no physical
  meaning.
* Iterative SMACOF gives the opposite trend (0.334 → 0.463 from $\Lambda=10^{-3}$
  to $10$); see §6.1.

> Under the metrics used here, the "rigid axis" should be regarded as **an artefact
> of the metric-reconstruction method**, not a robust physical result. Establishing
> it would require embedding-independent topological indicators (intrinsic dimension
> estimation, persistent homology). It is no longer listed as a core result.

### 6.6 Spectral slope of the chiral field (fixes R8)

FFT of the chiral field $A$ along causal order; log-log fit over the mid-range:

* For $\Lambda\lesssim3\times10^{-2}$ ($Re\gtrsim30$) the slope is stable at
  **−1.82 ~ −1.85**, seed sd 0.04–0.33;
* For $\Lambda\gtrsim3\times10^{-1}$ it rises rapidly toward positive values — the
  cascade disappears;
* It **steepens** with $N$: −1.767, −1.847, −1.899, −1.932 at
  $N=40,60,80,100$ ($\Lambda=10^{-3}$).

**Implementation sensitivity.** Structure density is a first-order statistic and is
highly consistent across PRNG implementations (Python's PCG64 versus the browser's
mulberry32 differ by $<0.001$ at the same $\Lambda$). The spectral slope, however, is
a higher-order statistic and is implementation-sensitive: at the same $\Lambda$ the
two PRNGs can differ by up to 0.5 at high $\Lambda$, where the seed-to-seed sd
already exceeds 1.0.

> The framework does generate a stable power-law scaling range — the most robust
> empirical signal found so far. But it is **not** Kolmogorov $k^{-5/3}$: the
> measured value is ≈−1.85 and drifts monotonically away from −1.667 as $N$ grows.
> Moreover this is a 1D proxy spectrum along causal order, not the 3D energy
> spectrum $E(k)$. Taken together with its implementation sensitivity, only the
> qualitative fact — a stable power-law scaling range exists — and its approximate
> high-$Re$ value (−1.85) are claimed; **neither cross-implementation comparability
> of the exact slope nor quantitative collapse onto K41 is claimed.** The acceptance
> criterion in `protocol_EN.md` stating "strict parallel collapse with $k^{-5/3}$" should be
> revised in line with this section.

---

## 7. Conclusions

1. **Turbulence generation** is a non-equilibrium crossover triggered when causal
   control ($\Lambda$) is insufficient relative to local spin generation. Measured
   as a smooth transition band about 1.5 decades wide, not a sharp critical point.
2. **Maintenance of coherent structure**: surviving channels are protected by the
   read-only history constraint of Operator 1 and the permanent topological anchor
   of Operator 3, forming algebraic invariants resistant to Paradigm B erasure.
   This structural argument is supported by the monotone phase diagram of §6.2.
3. **Compatibility with continuum mechanics**: the Chapman-Enskog expansion
   reproduces the N-S moment structure (§5), but only structurally; $\zeta$ in
   $\nu=\zeta\ell^2\Lambda$ remains to be calibrated.
4. **Robust empirical signal**: a stable power-law scaling range of the chiral field
   on the high-$Re$ side (slope ≈ −1.85) that collapses as $\Lambda$ grows. This is
   the strongest reproducible result of the framework.
5. **Not claimed**: a sharp critical point, a 1D rigid axis, or quantitative
   collapse onto Kolmogorov $k^{-5/3}$. All three are downgraded (R6, R7, R8).

By separating the exogenous control $\Lambda$ from the endogenous adaptive
$\lambda(n)$, strictly splitting the symmetric and antisymmetric components of $M$,
and consolidating every numerical experiment into a single reproducible baseline
(`sre_core.py`), this work offers a foundation for studying complex fluids at the
level of discrete information networks that is **testable rather than merely
narratable**.

---

## Appendix: reproduction

```bash
python sre_core.py      # reference implementation (all fix annotations inline)
python export_v2.py     # generates phase_data_v2.json (all data in §6)
python make_tables.py   # exports tables.md
```
