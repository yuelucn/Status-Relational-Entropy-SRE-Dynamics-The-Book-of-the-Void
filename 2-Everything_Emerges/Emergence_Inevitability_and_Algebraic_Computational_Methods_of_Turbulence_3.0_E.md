# The Necessity of Turbulence Emergence and an Algebraic Computational Method Based on Discrete Microscopic Causal Statistics and Multidimensional Manifold Reconstruction

Version: 3.0 (Revised)


Numerical benchmark: `sre_core.py`　Dataset: `phase_data_v2.json`　Interactive verification: `sim/sre_phase_console.html`

> **v3 Note**: This version further corrects v2 based on a program-correctness gate (`reproduce_ns62.py` reproduces the §6.2 phase diagram to $\Delta\le10^{-4}$) and two prior verifications (`verify_paper_claims.py`). Wherever this version conflicts with v2, this version prevails.

---

## 0. Revision Notes

This version makes the following corrections relative to v1. Wherever it conflicts with v1, this version prevails; the basis for each correction is given.

| No. | Problem in v1 | Handling in this version |
| :--- | :--- | :--- |
| **R1** | §2.2 defines $P_{\text{active}}=\frac{1}{1+e^{-\Delta S}}$, yet the text states that $P_{\text{active}}\to 0$ as $\Lambda\to\infty$. The two directly contradict each other: this expression gives $P_{\text{active}}\to 1$ as $\Lambda\to\infty$ | Changed to $P_{\text{active}}=\frac{1}{1+e^{\Psi}}$. See §3.2 (where the expression for $\Psi$ is further corrected by R10 of v3) |
| **R2** | $\beta\Lambda\mathbf{D}$ is labeled the "destabilizing term." But $\Lambda\propto 1/Re$, and large $\Lambda$ corresponds to low-Reynolds-number laminar flow, so this term is in fact the ordering term | Corrected labeling: $\beta\Lambda\mathbf{D}$ is the smoothing (ordering) term, $\alpha\operatorname{Tr}(A^TA)$ is the generating (destabilizing) term |
| **R3** | The symmetric and antisymmetric parts of $M$ are not distinguished; the reference implementation `N-S.py` even enforces $M_{vm,v_f}=-M_{v_f,v_m}$, making $M$ wholly antisymmetric, which conflicts with "$A$ is the antisymmetric part of $M$," and an antisymmetric matrix cannot serve as the precomputed metric for MDS | Strict bisection: $\mathbf{S}=(M+M^T)/2$ carries the metric and geometry, $\mathbf{A}=(M-M^T)/2$ carries the chirality. See §2.2 |
| **R4** | §5 claims to have "thoroughly abolished" constraints such as $M_{n+1}[1{:}n,1{:}n]\equiv M_n$, but this constraint is always present in the reference implementation | Clarified: this constraint is a **definitional component** of Operator 1's structural equation, not external hard-coding; v1's statement is untrue. See §4.1 |
| **R5** | Theorem 7 uses an endogenous $\lambda(n)$ built from the spectral radius to replace the exogenous $\Lambda$, leaving "$\Lambda$ controls the phase transition" with no counterpart in the code | $\Lambda$ and $\lambda(n)$ are explicitly separated, and two modes are provided for comparison. See §4.3 and §6.3 |
| **R6** | Claims a "unique critical point $\Lambda_c$" | Measured to be a smooth transition spanning about 1.5 orders of magnitude; downgraded to a **transition region** with a measured width. See §6.2 |
| **R7** | Claims that a "one-dimensional rigid central axis" emerges at high Reynolds number | This conclusion is sensitive to the metric reconstruction method (two MDS criteria give opposite trends) and does not constitute a robust conclusion. See §6.5 |
| **R8** | Claims the energy spectrum "strictly converges to Kolmogorov $k^{-5/3}$" | The measured one-dimensional surrogate spectral slope is about $-1.85$ and, as $N$ increases, further deviates from $-5/3$. It has been restricted to a surrogate indicator. See §6.6 (where "deviation with $N$" is corrected by R12 of v3 to large-$N$ saturation) |
| **R9** | Does not report the choice and uncertainty of the metric reconstruction method | Added §6.1, a methodological note and a comparison experiment |

**New corrections in v3 (R10–R12)**

| No. | Problem in v2 | Handling and basis in this version |
| :--- | :--- | :--- |
| **R10** | §3.2 defines $\Psi\equiv\beta\Lambda\mathbf{D}-\alpha\operatorname{Tr}(A^TA)$, **linear** in $\Lambda$. But Theorem 6 of §4.2 and the reference implementation give $P_{\text{active}}=1/(1+\Gamma\mathcal{D}_s/\mathfrak{B})$, which is **logarithmic** in $\Gamma(\Lambda)$ ($\Psi=\ln\Gamma+\ln\mathcal{D}_s-\ln\mathfrak{B}$). The two cannot both hold; moreover $\beta\Lambda\mathbf{D}$ is a matrix while $\alpha\operatorname{Tr}(A^TA)$ is a scalar, a type mismatch | §3.2 rewritten into the self-consistent main-equation form. **Basis**: Theorem 6 of §4.2 agrees term-by-term with `sre_core.py`, and is verified to $\le1.1\%$ error against the measured $C$ via `verify_dissipation.py`. See §3.2 |
| **R11** | §6.4 merely states that "the transition region is not converged and cannot be extrapolated," without giving the convergence mechanism | Added the analytic mechanism of finite-size convergence: the universal curve $C(z)=1-\ln(1+z)/z$, $z\propto\lambda n/E$, derived from the combined_C dissipation main equation, gives $\beta_\infty=0$ ($\ln z/z$ slow decay). **Basis**: `beta_dissipation_theory.py` (13 points, $R^2(\log z)=0.997$), `verify_dissipation.py` ($\beta_{\text{theo}}=0.420$ vs $\beta_{\text{meas}}=0.460$). See §6.4 |
| **R12** | §6.6 claims the spectral slope "becomes further steeper as $N$ increases" (inferred from $N=40\to100$: $-1.767\to-1.932$) | At large $N$ this trend **no longer exists**: at $\Lambda=10^{-3}$ the slope first steepens and then **saturates** ($N=800/1600/3200$ give $-1.79/-1.80/-1.78$); at $\Lambda=10^{-2}$ it **flattens** ($N=800\to6400$: $-1.63\to-1.38$). The "steepening" is a small-$N$ finite-size artifact. See §6.6 |

---

## 1. Introduction and Physical Picture

The traditional Navier–Stokes equations treat a fluid as an absolutely continuous medium. When explaining the origin of turbulence, microscopic thermal motion and energy fluctuations are amplified by the nonlinear convective term, which in continuous mathematics readily leads to singularity (blow-up) and divergence difficulties—a long-standing bottleneck of classical continuum mechanics.

This paper proposes a discrete dynamical paradigm: rather than treating a fluid as pressure and velocity fields over continuous space, we reconstruct it as an **information-statistical network of causal correlations among a large number of discrete microscopic states**.

* **Space and time are not a priori**: spatial geometry is not a pre-existing stage; the substrate is a discrete, dimensionless network of causal correlations.
* **The macroscopic emerges spontaneously**: geometric form is the macroscopic result emerging from the algebraic evolutionary correlation distances among microscopic states.

The goal of this paper is to give an axiomatic formulation of this paradigm, to show that it degenerates to the N–S equations in the continuum limit, and to **test each of its quantitative assertions with reproducible numerical experiments**. All numerical values in Section 6 are produced by `sre_core.py` and can be reproduced on a standard scientific computing stack.

---

## 2. Basic Objects and Dimensional System

### 2.1 Dimensional Basis

Let the fundamental dimensions be spanned by three independent bases: the elementary causal clock step $[\tau]$, the ground-state topological geometric distance $[\ell]$, and the minimal quantum of information action $[H]$.

* **State matrix $M\in\mathbb{R}^{n\times n}$**: the microscopic causal correlation matrix, with binary entries $M_{ij}\in\{-1,+1\}$, **generally non-symmetric**.
* **Intrinsic relaxation time $\tau_0$** and **external macroscopic characteristic time $T$**, both of dimension $[\tau]$. Define the dimensionless dissipation coefficient

$$\Lambda \equiv \frac{\tau_0}{T} \propto \frac{1}{Re}$$

### 2.2 Strict Symmetric / Antisymmetric Bisection (Correction R3)

This is a structural correction of this version relative to v1. The two algebraic components of $M$ play entirely different physical roles:

$$\mathbf{S} \equiv \frac{M + M^T}{2}, \qquad \mathbf{A} \equiv \frac{M - M^T}{2}$$

* **$\mathbf{S}$—the topological metric part.** It is symmetric and can serve as the precomputed dissimilarity source for multidimensional scaling (MDS). All geometric reconstruction (manifold coordinates, anisotropy) acts only on $\mathbf{S}$.
* **$\mathbf{A}$—the local spin operator.** The antisymmetric shear component; its inner-product quadratic form $\operatorname{Tr}(A^TA)=\sum_{i,j}A_{ij}^2$ corresponds to the flux of local vortex action in the microscopic non-equilibrium state.

The relation between the two is exclusive and complete: $M$ non-symmetric $\iff$ $\mathbf{A}\neq 0$ $\iff$ the system carries chirality.

> **Note**: The reference implementation of v1 enforces $M_{vm,v_f}=-M_{v_f,v_m}$, making $M$ wholly antisymmetric. In that case $\mathbf{A}\equiv M$ and $\mathbf{S}\equiv 0$, so the statement "A is the antisymmetric part of M" degenerates into an identity, and $\mathbf{S}=0$ means the metric vanishes entirely—which contradicts the theoretical intent. This version retains the general non-symmetric structure of $M$. Measurement ($N=60$, $\Lambda=10^{-2}$) gives an antisymmetric energy fraction $\operatorname{Tr}(A^TA)/\operatorname{Tr}(M^TM)=0.947$, i.e., the overwhelming majority of the correlation energy is indeed carried by the chiral part, but $\mathbf{S}$ is non-degenerate and the metric still exists.

---

## 3. Axiomatic Derivation of the Criterion Operator

### 3.1 Maximum-Entropy Master Equation

Suppose the probability of a microscopic degree of freedom transferring from a "coherent ordered state" to a "disordered decoherent state" is governed by the entropy change. According to non-equilibrium Boltzmann–Shannon statistics, the probability that a microscopic degree of freedom is activated by disordered fluctuations follows a logistic distribution.

Define the **discriminant** $\Psi$ (smoothing term minus generating term): its exact form is given by the self-consistent expression of §3.2, $\Psi=\ln\Gamma+\ln\mathcal{D}_s-\ln\mathfrak{B}$. The physical meaning of its two terms is (correction R2, v3 correction R10):

1. **Smoothing (ordering) term**: borne by $\ln\Gamma$; large $\Gamma$ ($\propto\Lambda$) means fast local relaxation, so topological differences are erased as soon as they are generated.
2. **Generating (destabilizing) term**: borne by $-\ln\mathfrak{B}$; the higher the local spin coherence barrier $\mathfrak{B}$, the stronger the ability to regenerate topological differences.

> **v3 correction (R10)**: v2 wrote $\Psi\equiv\beta\Lambda\mathbf{D}-\alpha\operatorname{Tr}(A^TA)$, which is linear in $\Lambda$ and has a matrix/scalar type mismatch; this version changes it to the logarithmic form consistent with §4.2/the reference implementation. The qualitative physical picture (the smoothing term grows with $\Lambda$, the generating term grows with chirality) is unchanged.

### 3.2 Activation Probability and Sign Convention (Correction R1, v3 Correction R10)

$$P_{\text{active}} = \frac{1}{1 + e^{\Psi}}$$

> **v3 correction (R10)**: v2 wrote the discriminant as $\Psi\equiv\beta\Lambda\mathbf{D}-\alpha\operatorname{Tr}(A^TA)$, linear in $\Lambda$. This expression is inconsistent with Theorem 6 of §4.2 and with the reference implementation (the latter is logarithmic in $\Gamma$), so this version gives a self-consistent form.

**The self-consistent discriminant.** Solving the §4.2 master equation for the survival probability $P_{\text{active}}=1-p_{\text{prune}}$:

$$P_{\text{active}} = \frac{1}{1 + \Gamma\cdot\dfrac{\mathcal{D}_s}{\mathfrak{B}}}, \qquad\text{i.e.}\qquad \Psi = \ln\Gamma + \ln\mathcal{D}_s - \ln\mathfrak{B}$$

where $\mathcal{D}_s$ is the causal topological depth, $\mathfrak{B}=\mathcal{E}_{\text{local}}+\exp(\operatorname{sgn}\tilde{\mathcal{E}}_{\text{local}})$ is the barrier (§4.2), and $\Gamma$ is the pruning gain. $\Psi$ is **logarithmic in $\Gamma$**, not linear in $\Lambda$—this is the form consistent with §4.2/the reference implementation.

Limiting behavior (consistent with the physical picture):

* $\Gamma\to+\infty$ (extreme low Reynolds number, large $\Lambda$): $\Psi\to+\infty$, $P_{\text{active}}\to 0$, entering the deterministic laminar phase.
* $\Gamma\to 0$ (extreme high Reynolds number): $\Psi\to-\infty$, $P_{\text{active}}\to 1$, disordered fluctuations fully activated.

> **Note**: In v2, $\beta\Lambda\mathbf{D}$ is a matrix while $\alpha\operatorname{Tr}(A^TA)$ is a scalar, and subtracting the two is a type mismatch; moreover, $\Psi$ being linear in $\Lambda$ contradicts the code's $\ln$ dependence. This version adopts the logarithmic form, §4.2 corresponds term-by-term to `sre_core.py`, and it is verified against the measured $C$ (`verify_dissipation.py`, error $\le1.1\%$).

### 3.3 Critical Condition (Correction R6)

From $\Psi(\Lambda)=0$ (i.e., $\Gamma\mathcal{D}_s/\mathfrak{B}=1$) we obtain the formal critical condition

$$\Gamma_c = \frac{\mathfrak{B}}{\mathcal{D}_s}$$

In mode A, $\Gamma=\Lambda$, so $\Lambda_c=\mathfrak{B}/\mathcal{D}_s$; in mode B, $\Gamma=\Lambda\lambda(n)$, and the critical $\Lambda$ is rescaled accordingly (see §6.3).

Since $\partial\Psi/\partial\Gamma=1/\Gamma>0$, $\Psi$ is strictly monotonically increasing in $\Gamma$, so $\Psi=0$ has at most one solution. **The intermediate value theorem guarantees that this solution exists, but existence does not imply a sharp phase transition**: the measurements of §6.2 show that the macroscopic order parameter evolves smoothly near the transition region, spanning about 1.5 orders of magnitude rather than jumping at a point. Hence this paper calls $\Lambda_c$ the **center of the transition region** and does not claim it to be a critical point in the thermodynamic sense.

---

## 4. Operator System

The system evolution is composed of a cascade of three operators: $M(t+\tau) = \mathcal{O}_3\circ\mathcal{O}_2\circ\mathcal{O}_1\,[M(t)]$.

### 4.1 Operator 1: Boundary Expansion $\mathcal{G}_{n\to n+1}$ (Clarification R4)

For any realized matrix $M_n$, the expansion operator maps to a block matrix by a single-step increment:

$$M_{n+1} = \mathcal{G}_{n\to n+1}(M_n) = \begin{pmatrix} M_n & \mathbf{x}_{n+1} \\ \mathbf{x}_{n+1}^T & y_{n+1} \end{pmatrix}, \qquad M_{n+1}[1{:}n,1{:}n] \equiv M_n$$

> **Clarification**: v1 §5 claimed that this framework "thoroughly abolished" constraints such as $M_{n+1}[1{:}n,1{:}n]\equiv M_n$. That statement is untrue—this constraint has always been present in the reference implementation, and **it should not be abolished**: it is a definitional component of Operator 1's structural equation, prescribing the algebraic property that the historical sub-block is read-only. Without this constraint, $\mathcal{G}_{n\to n+1}$ would degenerate into an arbitrary rewriting operator, and "causal inheritance" would be meaningless. This paper retains the constraint and makes explicit its axiomatic status: **once realized, history cannot be retroactively modified**. The claim in v1 of "no artificial hard-coding" should be understood as "no empirical fitting coefficients, no phenomenological drag corrections," not as "no structural constraints."

**Theorem 3 (Diagonal Invariance Theorem)**: On the binary domain $\Phi(x)\in\{-1,1\}$,

$$\Phi\big((M_{n+1}^2)_{n+1,n+1}\big) = \sum_{m=1}^{n}\Phi(x_{n+1,m})^2 + \Phi(y_{n+1})^2 = n + 1$$

That is, the diagonal path count of a newly injected node is independent of its specific assignment and is always $n+1$.

### 4.2 Operator 2: Maximum-Entropy Pruning $\mathcal{M}_\chi\circ\mathcal{E}_{\text{local}}$

The local multi-loop interference polynomial between a frontier node $v_f$ and a historical node $v_m$ (a 2-step graph walk):

$$\tilde{\mathcal{E}}_{\text{local}}(v_f,v_m) = \sum_{v_k\in\mathcal{N}(v_f)\cap\mathcal{N}(v_m)} M(v_f,v_k)M(v_k,v_m) + 2M(v_f,v_m)$$

Taking the absolute value and the sign: $\mathcal{E}_{\text{local}}=|\tilde{\mathcal{E}}_{\text{local}}|$, and the barrier $\mathfrak{B} = \mathcal{E}_{\text{local}} + \exp(\operatorname{sgn}\tilde{\mathcal{E}}_{\text{local}})$. Define the **dimensionless causal topological depth** $\mathcal{D}_s(v_f,v_m)=(n+1)-\sigma(v_m)$.

**Theorem 6 (Maximum-Entropy Pruning Master Equation)**:

$$p_{\text{prune}}(v_f,v_m) = 1 - \frac{1}{1 + \Gamma\cdot\dfrac{\mathcal{D}_s}{\mathfrak{B}}}$$

where $\Gamma$ is the **pruning gain** (see §4.3). When pruning occurs ($\chi=0$), **Paradigm B (elimination–conduction)** is executed:

$$M_{n+1}(i,j) \leftarrow \chi\cdot M_{n+1}(i,j) + (1-\chi)\cdot 1$$

That is, the channel spin is forced to the multiplicative identity $+1$, thereby eliminating the channel's phase contribution from the product feedback loop without disconnecting the graph connectivity. Surviving channels ($\chi=1$) instead inject an antisymmetric chiral shear.

### 4.3 Gain $\Gamma$: Exogenous $\Lambda$ and Endogenous $\lambda(n)$ (Correction R5)

To eliminate the cyclic dependence among operators, Theorem 7 of v1 constructed an adaptive tracking parameter from the spectral radius of the previously realized subgraph:

$$\lambda(n) = \frac{1}{\beta}\cdot\frac{\ln\!\big(1+\rho(\mathbf{A}_{n-1})\big)}{n+1}$$

By the Perron–Frobenius theorem, the spectral radius of a real matrix is the unique algebraic invariant that always exists, so $\lambda(n)$ has a unique real analytic solution at each step. However, v1 used $\lambda(n)$ to **completely replace** $\Lambda$, causing the macroscopic dissipation authority to disappear from the evolution equation, so that "$\Lambda$ controls the phase transition" had no counterpart in the code.

This version explicitly distinguishes the two and defines two modes for comparison:

| Mode | Pruning gain $\Gamma$ | Meaning |
| :--- | :--- | :--- |
| **A (exogenous)** | $\Gamma = \Lambda$ | $\Lambda$ directly serves as the phase-transition control quantity |
| **B (adaptive)** | $\Gamma = \Lambda\cdot\lambda(n)$ | Superimposes the state-adaptive correction of Theorem 7 on top of $\Lambda$ |

Both $\lambda(n)$ and $\Lambda$ are dimensionless, so their product does not break dimensional consistency. §6.3 gives a measured comparison of the two modes.

### 4.4 Operator 3: Five-Node Parity Breaking and Logical Emergence

To break the parity degeneracy of the pure spin-product space, a 5-node inhomogeneous array with a fixed inversion anchor is introduced ($n:5\to6$):

$$\mathbf{M}_5 = \begin{pmatrix} 1 & 1 & -1 & 1 & 1 \\ 1 & 1 & -1 & 1 & 1 \\ -1 & -1 & -1 & 1 & 1 \\ 1 & 1 & 1 & 1 & 1 \\ 1 & 1 & 1 & 1 & 1 \end{pmatrix}$$

Nodes 1 and 2 are the input ports $A,B$; node 3 is the rigid inversion anchor (its self-loop and cross-edges are hard-coded to $-1$); nodes 4 and 5 are a $+1$ inert boundary subgraph. Taking the activation mask $\boldsymbol{\chi}=[1,1,1,0,0]^T$, the macro-spin field is

$$Y_{\text{spin}} = \operatorname{sgn}\!\left(\tfrac12(S_{1,6}+S_{2,6}) - S_{3,6}\right), \qquad \operatorname{sgn}(0)\to+1$$

The four input combinations are mapped through the projection $f(S)=(1-S)/2$ to $\{1,1,1,0\}$, matching the truth table of a standard **NAND** gate, thereby providing a proof of the Turing completeness of this algebraic system. The topological differences generated by this operator are permanently locked, forming a rigid core that resists Paradigm B smoothing.

---

## 5. Continuum Limit and Compatibility with the N–S Equations

Let $\tau\to0,\ \ell\to0$ and map $M_{ij}$ to a multi-point correlation function $M(\mathbf{x},\mathbf{y},t)$ on a continuous manifold, defining the macroscopic density and velocity fields as first-order matrix moments:

$$\rho(\mathbf{x},t)=\int M\,d\mathbf{y}, \qquad \rho\mathbf{u}(\mathbf{x},t)=\int\frac{\mathbf{x}-\mathbf{y}}{\tau}M\,d\mathbf{y}$$

When $\Lambda\to\infty$ and the microscopic fluctuations tend to zero, the transition probability degenerates to Dirac $\delta$ evolution, and the algebraic free evolution can be written as a continuous master equation:

$$\frac{\partial M}{\partial t} + \nabla_{\mathbf{x}}\cdot\left(\frac{\mathbf{x}-\mathbf{y}}{\tau}M\right) = \mathcal{C}[M]$$

Performing a Chapman–Enskog expansion in $\epsilon=\ell/L$ (the algebraic equivalent of the Knudsen number), $M=M^{(0)}+\epsilon M^{(1)}+\mathcal{O}(\epsilon^2)$:

1. **The first moment** gives the continuity equation $\partial_t\rho+\nabla\cdot(\rho\mathbf{u})=0$;
2. **The second moment**, under momentum conservation of the collision operator $\int(\mathbf{x}-\mathbf{y})\mathcal{C}[M]d\mathbf{y}=0$, gives rise to the convective term, and the second-order correction $M^{(1)}$ contributes a viscous stress tensor under symmetry breaking. With $\Lambda\equiv\tau_0/T$, the kinematic viscosity is formally written as $\nu=\zeta\,\ell^2\Lambda$.

Hence

$$\rho\left(\frac{\partial\mathbf{u}}{\partial t}+(\mathbf{u}\cdot\nabla)\mathbf{u}\right) = -\nabla p + \rho\,\zeta\ell^2\Lambda\,\nabla^2\mathbf{u}$$

that is, the standard N–S equations.

> **Qualification**: $\zeta$ is a network geometric constant to be determined; this paper neither derives its value from first principles nor performs a direct numerical simulation comparison. Therefore this section establishes a **structural compatibility** (the discrete algebraic master equation possesses the N–S moment structure in the continuum limit), not a proof of quantitative equivalence. $\nu=\zeta\ell^2\Lambda$ should be regarded as a formal correspondence from dimensional analysis, whose coefficient must be fixed by subsequent calibration.

---

## 6. Numerical Evidence

All numerical values are produced by `sre_core.py` with parameters: $N=60$, 5 random seeds (0–4), dataset `phase_data_v2.json`.

### 6.1 Method: Choice of Metric Reconstruction Criterion (New R9)

The manifold geometry starts from the symmetric part $\mathbf{S}$, taking the dissimilarity $d_{ij}=\sqrt{\max(0,\,2-2S_{ij})}$. There are two common criteria for recovering three-dimensional coordinates from $d_{ij}$, and this work mainly uses **classical MDS (Torgerson)**: eigendecomposition of the double-centered Gram matrix $\mathbf{B}=-\tfrac12\mathbf{J}\mathbf{D}^{(2)}\mathbf{J}$, taking the first three eigenvectors.

Reason for the choice: it is a closed-form solution that is **deterministic, reproducible, and free of local-minimum problems**—this is especially critical for the present framework, because "avoiding iterative entrapment in local minima" is one of the paradigm's claims relative to gradient-based methods.

However, it must be reported that the two criteria give **opposite** anisotropy trends (comparison experiment, $N=60$, seed 0):

| $\Lambda$ | Classical MDS (strain criterion) | SMACOF (stress criterion, converged) |
| ---: | ---: | ---: |
| $10^{-3}$ | 0.3720 | 0.3338 |
| $10^{-2}$ | 0.3635 | 0.3365 |
| $10^{-1}$ | 0.3686 | 0.3573 |
| $1$ | 0.3422 | 0.3682 |
| $10$ | 0.3546 | 0.4634 |

SMACOF's stress has stabilized after `max_iter=1000` (653.79 no longer decreasing), so the difference is **not** insufficient convergence but a difference in objective function. This methodological uncertainty directly affects the conclusions of §6.5.

### 6.2 Mode A: Phase Diagram for Exogenous $\Lambda$ (Correction R6)

| $\Lambda$ | $Re\propto1/\Lambda$ | Structural density | sd | Anisotropy | Spectral slope | sd |
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

The structural density (the fraction of surviving chiral channels) decreases monotonically from 0.4915 to 0.0026, in a smooth S-shaped form. Defining the transition region as the structural density falling from 0.40 to 0.08 gives

$$\Lambda \in [\,8\times10^{-2},\ 2.5\,], \qquad \text{i.e.} \quad Re\propto1/\Lambda \in [\,0.4,\ 12\,]$$

**The transition width is about 1.5 orders of magnitude.** The inter-seed standard deviation is $\le 0.005$ throughout, so the smoothness is not due to noise but is an intrinsic property of the system.

> Conclusion: This framework does **not** support the strong claim of a "sharp critical point." What can be robustly asserted is: there exists a monotonic, reproducible structural–dissipation transition region of width about 1.5 orders of magnitude. For $\Lambda>10^2$, the structural density is $<10^{-2}$, the manifold degenerates to a near-zero distance matrix, and MDS values lose meaning (omitted from the table).

### 6.3 Mode B: Consequences of Switching On Theorem 7 (Correction R5)

| $\Lambda$ | Structural density | Spectral slope |
| ---: | ---: | ---: |
| $10^{-2}$ | 0.4914 | −1.854 |
| $1$ | 0.4673 | −1.842 |
| $3.16$ | 0.4186 | −1.672 |
| $10$ | 0.1676 | −0.484 |
| $10^{2}$ | 0.0269 | +0.136 |

Compared with mode A: the same transition occurs at $\Lambda\approx3\sim30$, about **2 orders of magnitude** later than in mode A.

Reason: $\lambda(n)$ decays from 0.315 to 0.010 as $n$ goes to $N=60$, with an average magnitude of about $10^{-2}$, systematically shrinking the effective gain. At the same time, the decay of $\lambda(n)$ means that the **effective pruning strength decreases with evolution time**, i.e., the system has an intrinsic temporal non-stationarity—strong pruning early, weak pruning late.

> Conclusion: Switching on Theorem 7 does not change the qualitative structure of the transition (monotonic transition and spectral slope plateau are both retained), but (i) it rescales the effective magnitude of $\Lambda$ and (ii) it introduces a temporal non-stationarity that decays with $n$. These two are the price paid for decoupling the cyclic dependence, which v1 did not mention.

### 6.4 Finite-Size Test

| $N$ | $\Lambda=10^{-3}$ | $\Lambda=10^{-1}$ | $\Lambda=1$ |
| ---: | ---: | ---: | ---: |
| 40 | 0.4870 | 0.4020 | 0.1759 |
| 60 | 0.4901 | 0.3809 | 0.1435 |
| 80 | 0.4922 | 0.3608 | 0.1212 |
| 100 | 0.4927 | 0.3452 | 0.1062 |

* **The high-Reynolds-number side ($\Lambda=10^{-3}$) is converged**: from $N=40\to100$ the structural density changes only from 0.487 to 0.493, a change of $<1.5\%$.
* **The transition region ($\Lambda=10^{-1},1$) is not converged**: the structural density continues to decrease with $N$ (at $\Lambda=1$, from 0.176 to 0.106, a 40% drop).

> Therefore: the **quantitative location of the transition region is $N$-dependent** and cannot be extrapolated to $N\to\infty$. What can be robustly asserted is only the qualitative conclusion that "a monotonic transition exists."

#### 6.4.1 Analytic Explanation of the Convergence Mechanism (New in v3, R11)

v2 merely stated "not converged"; this version adds its analytic origin. From the master equation in §II of combined_C, *A Hierarchical Dissipation Self-Organization Theory of Binary Network Dynamics*,

$$p_{\text{prune}}(d,\mathcal{E}) = 1 - \frac{1}{1+\Gamma\,\dfrac{d}{\mathcal{E}+1}}, \qquad d=n-\max(i,j)$$

performing a continuum approximation integral over depth $d\in[0,n]$, the survival probability $\langle 1-p_{\text{prune}}\rangle$ becomes the **universal curve**

$$C(z) = 1 - \frac{\ln(1+z)}{z}, \qquad z \equiv \frac{\Gamma\,n}{\mathcal{E}+1}$$

The power-law exponent $\beta\equiv-\dfrac{d\ln C}{d\ln Re}$ satisfies, as $z\to\infty$, $\beta(z)\approx\dfrac{\ln z-1}{z}\to 0$. **That is, in the thermodynamic limit there is no finite asymptotic value, $\beta_\infty=0$**, and the decay is $\ln z/z$, **slower than any power law** (hence neither the $1/N$ nor the $1/N^2$ extrapolations hold).

**Numerical verification** (`beta_dissipation_theory.py`, `verify_dissipation.py`):

* Inverting $z$ from the measured $C(\lambda,N)$ under a consistent protocol gives $z\propto\lambda^{1.40}N^{0.97}$, with $R^2(\log z)=0.997$ over 13 data points;
* Substituting the actual barrier of the final $M$ into the master equation, $C_{\text{theo}}$ and $C_{\text{meas}}$ differ by $\le1.1\%$ for $\Gamma\in[10^{-2},10^{-1}]$, with $\beta_{\text{theo}}=0.420$ vs $\beta_{\text{meas}}=0.460$;
* The measured doubling ratio $[800\to1600]/[1600\to3200]=1.135$ agrees with the theoretical prediction $1.131$—whereas the $1/N$ model predicts $2.0$ and is refuted by the measurement.

> **Conclusion (replacing v2's "cannot be extrapolated")**: The $N$-dependence of the transition region is not an incidental experimental shortcoming but an **intrinsic property of the dissipation master equation**—the finite-size correction decays extremely slowly as $\ln z/z$, never reaching a finite limit. This explains the saturation of the §6.6 spectral slope at large $N$ (see below).

### 6.5 On the "One-Dimensional Rigid Central Axis" (Correction R7)

v1 claimed that at high Reynolds number the MDS-reconstructed space spontaneously develops a "highly connected rigid central axis" (red core) wrapped in a dissipative shell.

The test results of this version do not support this strong claim:

* Under classical MDS, the anisotropy $\lambda_1/\sum\lambda$ stays within **0.34–0.43** throughout $\Lambda\in[10^{-4},10]$, a fluctuation magnitude of the same order as the inter-seed standard deviation (up to 0.08 at the extremes), with no convergence trend toward 1. Since $1/3$ corresponds to complete isotropy, the measured values are only slightly above the isotropic baseline.
* Only in the **extremely dissipative degenerate region** ($\Lambda\ge10^2$, structural density $<10^{-2}$) does the anisotropy rise above 0.86, but at that point the network is almost entirely $+1$, the MDS input is near-singular, and the value is physically meaningless.
* Iterative SMACOF gives the opposite trend (0.334→0.463 as $\Lambda=10^{-3}\to10$), see §6.1.

> Conclusion: Under the metrics of this paper, the "rigid central axis" should be regarded as an **artifact of the metric reconstruction method**, not a robust physical conclusion. To establish this phenomenon, one would need to re-examine it using intrinsic-dimension estimation, persistent homology, and other topological indicators independent of the embedding criterion. This paper no longer lists it as a core conclusion.

### 6.6 Chiral Field Spectral Slope (Correction R8)

Applying an FFT to the one-dimensional signal of the chiral field $A$ along the causal order, and fitting the mid-section of $\log E$–$\log k$:

* For $\Lambda\lesssim3\times10^{-2}$ ($Re\gtrsim30$), the slope is stable at **−1.82 to −1.85**, with inter-seed standard deviations of 0.04–0.33;
* For $\Lambda\gtrsim3\times10^{-1}$, the slope rapidly rises to positive values and the cascade disappears;
* As $N$ increases, the slope **becomes further steeper**: $N=40,60,80,100$ give −1.767, −1.847, −1.899, −1.932 respectively ($\Lambda=10^{-3}$).

**v3 correction (R12): large-$N$ extrapolation refutes "continued steepening."** Extending $N$ to the $10^3$ range (`verify_paper_claims.py`, seeds[0,1]):

| $N$ | $\Lambda=10^{-3}$ | $\Lambda=10^{-2}$ |
| ---: | ---: | ---: |
| 800 | −1.79 | −1.63 |
| 1600 | −1.80 | −1.67 |
| 3200 | −1.78 | −1.55 |
| 6400 | — | **−1.38** |

It can be seen that: at $\Lambda=10^{-3}$ the slope **saturates** for $N\ge800$ (−1.79/−1.80/−1.78, nearly unchanged) and does not continue to steepen; at $\Lambda=10^{-2}$ the slope instead **flattens** (from −1.63 to −1.38 as $N=800\to6400$). **The "monotonic deviation from −1.667 with $N$" inferred by v2 from $N=40\to100$ is a small-$N$ finite-size artifact**, qualitatively consistent with the $\ln z/z$ slow-decay mechanism of §6.4.1 (high-order statistics tend to a plateau rather than diverging as $N$ grows).

**Implementation-dependence note**: The structural density is a first-order statistic and is highly consistent across different random implementations of the PRNG
(the Python PCG64 and the browser-side mulberry32 differ by $<0.001$ at the same $\Lambda$).
But the spectral slope is a high-order statistic and is sensitive to the specific implementation: at the same $\Lambda$ the means given by the two PRNGs
can differ by as much as 0.5 at high $\Lambda$, while the inter-seed standard deviation itself already exceeds 1.0.

> Conclusion: This framework does spontaneously produce a stable power-law scaling region, which is currently the most robust empirical signal. But it is **not** Kolmogorov $k^{-5/3}$: the measured value is about −1.8, and at large $N$ it **saturates to a plateau rather than continuing to deviate**. Furthermore, this spectrum is a one-dimensional surrogate spectrum along the causal order, not equal to the three-dimensional energy spectrum $E(k)$. Given the implementation dependence, this paper asserts only the qualitative fact that "there exists a stable power-law scaling region whose slope saturates at about −1.8 at large $N$," and **does not claim** that the precise value of the slope is comparable across implementations, nor that it achieves quantitative convergence with K41 theory; the acceptance criterion in `cop.md` of "strict parallel convergence with $k^{-5/3}$" should be revised according to this section.

---

## 7. Conclusion

1. **The origin of turbulence**: it is a **non-equilibrium transition** in which microscopic degrees of freedom are activated over a large area when the causal control force ($\Lambda$) is insufficient relative to the local spin generating capacity; measured as a smooth transition region of width about 1.5 orders of magnitude, not a sharp critical point.
2. **Maintenance of coherent structures**: surviving channels are protected by the historical read-only constraint of Operator 1 and the permanent topological anchors of Operator 3, algebraically constituting an invariant that resists Paradigm B smoothing. This is a structural argument, supported by the monotonic phase diagram of §6.2.
3. **Compatibility with continuum mechanics**: the Chapman–Enskog expansion yields the moment structure of N–S (§5), but this is structural compatibility; $\zeta$ in $\nu=\zeta\ell^2\Lambda$ remains to be calibrated.
4. **Finite-size convergence** (new in v3): the non-extrapolatability of the transition region is not an experimental shortcoming but an intrinsic property of the dissipation master equation—the correction decays extremely slowly as $\ln z/z$, $\beta_\infty=0$, with no finite asymptotic value (§6.4.1).
5. **Robust empirical signal**: on the high-Reynolds-number side there exists a stable chiral-field power-law scaling region whose slope **saturates at about −1.8** at large $N$ (rather than continuing to steepen), and which collapses as $\Lambda$ increases. This is currently the most robust reproducible result of this framework.
6. **Not claimed**: a sharp critical point, a one-dimensional rigid central axis, quantitative convergence with Kolmogorov $k^{-5/3}$, and monotonic divergence of the spectral slope with $N$. All four are downgraded due to methodological uncertainty or measured deviation (R6, R7, R8, R12).

By explicitly separating the exogenous control quantity $\Lambda$ from the endogenous adaptive quantity $\lambda(n)$, strictly bisecting the symmetric and antisymmetric components of $M$, and converging all numerical experiments onto a single reproducible benchmark `sre_core.py`, this method provides a foundation for studying complex fluids from the level of discrete information networks that is **testable rather than merely narratable**.

---

## Appendix: Reproduction

```bash
python sre_core.py            # reference implementation (with all revision annotations)
python export_v2.py           # generates phase_data_v2.json (all §6 data)
python make_tables.py         # exports tables.md
```

**New verification scripts in v3**:

```bash
python reproduce_ns62.py          # program-correctness gate: reproduce §6.2 phase diagram (Δ≤1e-4)
python verify_paper_claims.py     # R12: large-N spectral slope; V1: N=800 protocol conflict
python beta_dissipation_theory.py # §6.4.1: dissipation master equation → universal curve C(z), β∞=0
python verify_dissipation.py      # §6.4.1: master-equation closed-loop verification (C_theo vs C_meas)
```