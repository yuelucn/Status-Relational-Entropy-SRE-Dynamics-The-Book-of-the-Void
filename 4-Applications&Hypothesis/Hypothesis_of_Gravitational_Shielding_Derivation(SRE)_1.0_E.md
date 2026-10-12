# Hypothesis of Gravitational Shielding Derivation (SRE)



Version: 1.0  


- Basis: the following articles in the manuscript collection `The Book of the Void` of *Status-Relational Entropy (SRE) Dynamics* (https://doi.org/10.5281/zenodo.23275050) (all references in this document are given as **article name + section**, and no longer by line number)
- Terminology convention: uniformly expressed as **"gravitational shielding"**—shielding naturally produces anti-gravity/weightlessness, rather than "flipping the sign of gravity / introducing negative mass".
- Status: This document only performs derivation, order-of-magnitude criteria, and phenomenological interpretation.

---

## Literature Correspondence Table (Articles and Sections Cited in This Document)

This document cites the following seven articles in the manuscript collection ``The Book of the Void``. In the main text, sources are uniformly marked in the form 《short name》§section; the table below gives the correspondence between short names and full titles, so that readers can cross-check under any typesetting (including PDF).

| Short name | Full article title (manuscript-collection title) | Sections used in this document |
|---|---|---|
| **《Multidimensional Spacetime and Dynamical Gravity》** | 《Emergence of Multidimensional Spacetime and Dynamical Gravity via Regularized Causal Information Networks》 (Chinese title: 正则化因果信息网络下多维时空与动态变光速引力) | §2.2 Topological dissipation tensor and compensation operator; §2.3 Topological stiffness weights and baryonic center-of-mass redshift; §2.4 Spectral resonance deriving the dynamic compression coefficient; §5 Causal emergent gravity: a thermodynamic effect as a dissipation gradient |
| **《Composite Elementary Particles》** | 《Composite Elementary Particles and the SRE-Dynamics Topological Paradigm of Relational-Space Emergence》 (Chinese title: 复合基本粒子与关系空间涌现的SRE动力学拓扑范式) | §1.3 Local cross-spectral operator and information-geometry mapping; §II Core paradigm: the three-in-one emergence jump and composite-particle generation; §Discussion · Model capability boundary |
| **《Reconstruction of Classical Electrodynamics》** | 《A Basic Reconstruction of Classical Electrodynamics Based on Discrete Graph Topology and Bidirectional Causality》 (Chinese title: 基于离散图拓扑与双向因果性对经典电动力学的基础重构) | §4 Mass–energy equivalence $E=mc^2$ as a topological theorem |
| **《Necessity of Turbulence Emergence》** | 《The Necessity of Turbulence Emergence and an Algebraic Computation Method Based on Discrete Microscopic Causal Statistics and Multidimensional Manifold Reconstruction》 (Chinese title: 基于离散微观因果统计与多维流形重构的湍流涌现必然性及代数计算方法) | §4.1 Operator 1: boundary expansion; §4.2 Operator 2: maximum-entropy pruning; §4.3 Gain $\Gamma$: exogenous $\Lambda$ and endogenous $\lambda(n)$ |
| **《Logical-Depth Anchoring and Safety Shielding》** | 《On the Order-of-Magnitude Anchoring of the Logical Depth N and the Safety Shielding of Observation Protocols》 (Chinese title: 关于逻辑深度 N 的量级锚定与观测协议的安全性屏蔽) | Section 3 Core safety adjudication: the physical-level "read-only" restriction |
| **《Complete Characterization of the Nucleon》** | 《A Complete Characterization of the Nucleon in the SRE Framework: Open–Closed Two-State Skeleton Inversion, Quark Conjecture, and a Unified Formulation Validated by Nuclear Reactions》 (Chinese title: SRE 框架下核子的完整刻画：开闭二态骨架反演、夸克推测与核反应验证的统一表述) | §2.1 Binary self-organizing network and the sim_p generator |
| **《Graph-Operator Pipeline Whitepaper》** | 《Overall Framework Whitepaper of the General Graph-Operator Pipeline for Status-Relational Entropy (SRE) Dynamics (Academic Revision)》 (Chinese title: 状态‑关系熵（SRE）动力学通用图算子流水线总体框架白皮书（学术修订版）) | §1.2 Operator 1: local graph-expansion operator; §3.1 Operator 5: endogenous-variable delay-calibration operator; §4.2 Morphological-morphism projection principle of macroscopic observables; §5.1 Operator 10: preemptive homological random-pruning operator; §5.3 Operator 8: local lock-free algebraic-valve equalization operator |

**Reading convention**: "Part I" appearing in the main text refers to the first part of this document (Gravitational Shielding Derivation); "Part II" refers to the second part (Reverse Interpretation of the Podkletnov Result). Cross-part citations are written as "Part I §n" or "Part II §n".

---

## Part I　Gravitational Shielding Derivation

## 0 Summary of Conclusions

1. In SRE, gravity is not a fundamental field but a **thermodynamic aftereffect of local information-dissipation gradients** (*Multidimensional Spacetime and Dynamical Gravity* §5). Therefore "gravitational shielding" = **suppressing the network correlations capable of generating that dissipation gradient**, rather than canceling a fundamental force.
2. The dependence of the gravitational acceleration $a_\mathrm{SRE}$ on the network state can be decomposed into **three shieldable quantities**:
   - Main amplitude $\alpha_\mathrm{scale}\cdot\mathcal{W}_{ij}$ (suppressible, the only substantive channel)
   - Chiral phase term $\Gamma_\mathrm{chiral}$ (the only sign-reversible term, capable of providing net repulsion)
   - Uniform term $-\gamma c_\mathrm{eff}^2/4$ (a global term, not locally shieldable)
3. The main channel yields an **exact, dimensionless shielding factor** (Part I §3):
   $$\Xi\equiv\frac{\mathcal{W}_{ij}^{\text{shielded}}}{\mathcal{W}_{ij}^{\text{vacuum}}}=\frac{1+\ln(1+\sigma_z^{\text{vacuum}})}{1+\ln(1+\sigma_z^{\text{shielded}})}<1$$
   The cost is that the **local measurement entropy must be amplified logarithmically**: $\Xi=0.5$ requires $\sigma_z$ to increase by about 180 times, and $\Xi=0.1$ by about $9\times10^3$ times. $\mathcal{W}\to0$ (complete weightlessness) corresponds to $\sigma_z\to\infty$, and is **unreachable**.
4. The compensation operator $\hat{\mathcal{C}}$ is **non-monotonic/oscillatory** with respect to the dissipation $\hat{\mathcal{D}}$ (period $1/\alpha_0$, the first maximum at $\hat{\mathcal{D}}_0^{*}=1/(2\alpha_0)$; the derivative proof is given in Part I §5). However, under realistic parameters $\hat{\mathcal{D}}\sim 18\text{–}27 \gg 1/\alpha_0$, it falls into the strong-oscillation regime, where its envelope mean is pinned at $\langle\hat{\mathcal{C}}\rangle=1/(2\alpha_0)$, and it is **not a clean local knob** (an honest conclusion).
5. The only engineerable actuation mechanism is **Op2 maximum-entropy pruning** (*Necessity of Turbulence Emergence* §4.2): set the channel spin to the multiplicative identity $+1$, thereby eliminating that channel's phase contribution **without breaking graph connectivity**. Because the interior of a mass closed loop is "non-addressable/non-writable" (read-only barrier, *Logical-Depth Anchoring and Safety Shielding* Section 3), **shielding can only be a boundary operation**—operating on the dissipation–compensation channel between the shielded region and the external network, rather than rewriting the internal closed loop.
6. The chiral term $\Gamma_\mathrm{chiral}$ can reverse sign to produce **net repulsion**, and its phase condition is strictly obtainable (Part I §4); but whether it can dominate depends on the not-yet-calibrated dimensionless $\alpha_\mathrm{scale}$: only when $\alpha_\mathrm{scale}\lesssim8\times10^{-4}$ is the chiral repulsion of the same order as the Newtonian term. **Thus the door to "true anti-gravity" is ajar, and its hinge is the experimental anchoring of $\alpha_\mathrm{scale}$.**

---

## 1 Starting Point: Gravity as a Thermodynamic Aftereffect of Dissipation Gradients

The theoretical body (*Multidimensional Spacetime and Dynamical Gravity* §5, verbatim):

$$
a_\mathrm{SRE}(r,z)=
\begin{cases}
-\dfrac{\alpha_\mathrm{scale}\cdot \mathcal{W}_{ij}}{r}-\dfrac{\gamma c_\mathrm{eff}(z)^2}{4} & \mathrm{Rank}=2,\ z<z^* \\[10pt]
-\dfrac{2\,\alpha_\mathrm{scale}\cdot\mathcal{W}_{ij}}{r^{2}}-\dfrac{\gamma c_\mathrm{eff}(z)^2}{4}+\Gamma_\mathrm{chiral}(r)
& \mathrm{Rank}=4,\ z\ge z^*
\end{cases}
$$

$$
\Gamma_\mathrm{chiral}(r)=\xi(z)\cdot\frac{\sin\!\big(\pi\alpha_{0,\mathrm{dynamic}}\cdot 2\mu\big)}{r^{2}\cdot\ln(r/\ell_P)}
$$

Supporting definitions (*Multidimensional Spacetime and Dynamical Gravity* §2.2–§2.4, verbatim):

$$
\hat{\mathcal{D}}_{ij}=\ln\!\Big(1+\frac{\sigma_{z,i}\cdot\sigma_{z,j}}{\epsilon_\mathrm{mach}}\Big),\qquad
\hat{\mathcal{C}}=\alpha_{0,\mathrm{dynamic}}^{-1}\cdot\sin^{2}\!\big(\pi\alpha_{0,\mathrm{dynamic}}\hat{\mathcal{D}}_{ij}\big)
$$

$$
R_{ij}^{2}\equiv \mathrm{Tr}\big(\hat{\mathcal{D}}_{ij}\cdot\hat{\mathcal{C}}\big)\cdot\exp(-\gamma\,\mu_\mathrm{loss})
$$

$$
\mathcal{W}_{ij}=\sqrt{\mathcal{C}_i\,\mathcal{C}_j}
=\Big[\big(1+\ln(1+\sigma_{z,i})\big)\big(1+\ln(1+\sigma_{z,j})\big)\Big]^{-1/2}
$$

$$
\mu=\frac{\sum_i \mathcal{C}_i z_i}{\sum_i \mathcal{C}_i},\qquad
\xi(z)\equiv\xi(\mu)=0.08\,e^{0.15\mu}
$$

$$
\alpha_{0,\mathrm{dynamic}}=\frac{\theta_\mathrm{conformal}}{\Delta z+\epsilon_\mathrm{mach}},\qquad
\theta_\mathrm{conformal}\approx0.82798,\qquad \gamma=0.0585=\frac{1}{2\pi e}
$$

Ontological key point (*Multidimensional Spacetime and Dynamical Gravity* §5): "Gravity is not a fundamental field; it is a statistical thermodynamic aftereffect brought about by local information-dissipation gradients."—This statement directly provides the **physical entry point** for shielding: to shield gravity is essentially to suppress the **local dissipation tensor and its gradient**, which is determined by the measurement entropy $\sigma_z$ and its spatial distribution.

---

## 2 Structural Decomposition of Gravity: Three Shieldable Quantities

Writing $a_\mathrm{SRE}$ as a "source × kernel" decomposition, and extracting the independently adjustable factors within the kernel:

| Quantity | Expression | Dependence on network state | Shieldable? | Role |
|---|---|---|---|---|
| Main amplitude | $\alpha_\mathrm{scale}\cdot\mathcal{W}_{ij}$ | $\mathcal{W}_{ij}=f(\sigma_{z,i},\sigma_{z,j})$ | ✅ Suppressible | The only substantive channel |
| Chiral term | $\Gamma_\mathrm{chiral}=\xi(z)\sin(\cdot)/(r^2\ln(r/\ell_P))$ | Phase $\propto\alpha_0\mu$ | ✅ Sign-reversible | The only source of net repulsion |
| Uniform term | $-\gamma c_\mathrm{eff}^2/4$ | Global $c_\mathrm{eff}(z)$ | ❌ Not local | Background/expansion term |

**Key observation**: $\mathcal{W}_{ij}$ is a **strictly decreasing** function of $\sigma_z$ (*Multidimensional Spacetime and Dynamical Gravity* §2.3); while the dissipation $\hat{\mathcal{D}}_{ij}$ is a **strictly increasing** function of $\sigma_z$ (*Multidimensional Spacetime and Dynamical Gravity* §2.2). Hence the single action of **injecting local measurement entropy** simultaneously:
- (i) directly lowers $\mathcal{W}_{ij}$ → lowers the amplitude of $a_\mathrm{SRE}$;
- (ii) raises $\hat{\mathcal{D}}_{ij}$ → shifts the operating point of the compensation operator (Part I §5).

The two channels share the same origin, so "gravitational shielding" has a unified operational definition in this theory: **raise the local measurement entropy $\sigma_z$ of the target region (making its information more "blurred" and more decohered), and cut off its dissipation–compensation channel to the outside.**

---

## 3 Main Channel: $\mathcal{W}_{ij}$ Entropy Collapse (Exact, Quantifiable)

### 3.1 Shielding Factor

Let the endpoint vacuum measurement entropy be $\sigma_z$, and after shielding be $\sigma_z'$. From the definition of $\mathcal{W}_{ij}$:

$$
\boxed{\;\Xi\equiv\frac{\mathcal{W}(\sigma_z')}{\mathcal{W}(\sigma_z)}=\frac{1+\ln(1+\sigma_z)}{1+\ln(1+\sigma_z')}\;}
$$

Since both branches of $a_\mathrm{SRE}$ are proportional to $\mathcal{W}_{ij}$, **the relative gravity-weakening amount is exactly $1-\Xi$**, independent of $\alpha_\mathrm{scale}$, $r$, and $z$—determined purely by the local measurement entropy. This is the cleanest result of this derivation.

### 3.2 Inverse Design Equation

Given a target shielding factor $\Xi$, the required local measurement entropy:

$$
\boxed{\;\sigma_z'=\exp\!\left(\frac{1+\ln(1+\sigma_z)}{\Xi}-1\right)-1\;}
$$

### 3.3 Order-of-Magnitude Table (taking $\sigma_z=0.01$, $1+\ln(1.01)=1.00995$)

| Target $\Xi$ | Gravity weakening | Required $\sigma_z'$ | Amplification relative to vacuum |
|---|---|---|---|
| 0.99 | 1% | 0.0204 | ×2.0 |
| 0.98 | 2% | 0.0310 | ×3.1 |
| 0.90 | 10% | 0.1300 | ×13 |
| 0.50 | 50% | 1.773 | ×177 |
| 0.10 | 90% | $8.95\times10^3$ | $9.0\times10^5$ |

**Conclusion**: Weight reduction is "logarithmic-scale investment for linear-scale weight reduction"; $\Xi\to0$ requires $\sigma_z\to\infty$. **Within the main channel, complete weightlessness is unreachable; only asymptotic weight reduction is possible.** This falls in the same order-of-magnitude window as the "weight-reduction ceiling of about 2%" (Podkletnov scale) in the early conjecture.

---

## 4 Phase Channel: $\Gamma_\mathrm{chiral}$, the Only Sign-Reversible Term

### 4.1 Strict Condition for Sign Reversal (Net Repulsion)

$\Gamma_\mathrm{chiral}$ carries its sign through $\sin(\pi\alpha_0\cdot2\mu)$ (*Multidimensional Spacetime and Dynamical Gravity* §5). Taking $\sin=-1$ (maximum outward contribution):

$$
\pi\alpha_0\cdot 2\mu = -\frac{\pi}{2}+2\pi n
\;\Longrightarrow\;
\boxed{\;\mu^{*}=\frac{4n-1}{4\,\alpha_{0,\mathrm{dynamic}}}\;}
$$

Then $\Gamma_\mathrm{chiral}^{\max\to-}=-\dfrac{\xi(z)}{r^2\ln(r/\ell_P)}$, producing a **net subtraction** from the attractive term. $\mu$ is the baryonic center-of-mass redshift ($\mu=\sum\mathcal{C}_iz_i/\sum\mathcal{C}_i$; definition in *Multidimensional Spacetime and Dynamical Gravity* §2.3), set by the weighted redshift of the local subgraph $V_\mathrm{slice}$—**thus the phase is tunable** (by changing the redshift composition of the observed subgraph).

### 4.2 Order-of-Magnitude Criterion (Deciding Whether "Anti-Gravity" Is Feasible)

The ratio of the chiral term to the main attractive term (Rank=4):

$$
\mathcal{R}\equiv\frac{|\Gamma_\mathrm{chiral}|}{2\alpha_\mathrm{scale}\mathcal{W}_{ij}/r^2}
=\frac{\xi(z)\,\big|\sin(\cdot)\big|}{2\,\alpha_\mathrm{scale}\,\mathcal{W}_{ij}\,\ln(r/\ell_P)}
\;\xrightarrow[\ \sin=\pm1\ ]{}\;
\frac{\xi(z)}{2\,\alpha_\mathrm{scale}\,\mathcal{W}_{ij}\,\ln(r/\ell_P)}
$$

Substituting $\xi\approx0.108$ ($\mu\approx2$), $\mathcal{W}\approx1$, $\ln(r/\ell_P)\approx80$ ($r\sim1\,\mathrm{m}$):

$$
\mathcal{R}\approx\frac{6.8\times10^{-4}}{\alpha_\mathrm{scale}}
$$

**Interpretation**:
- If $\alpha_\mathrm{scale}\sim1$: $\mathcal{R}\sim10^{-3}$, the chiral term is a perturbation (phenomenologically manifesting as a small-amplitude oscillation of $G_\mathrm{eff}$; see the discussion of smooth $G_\mathrm{eff}$ oscillation in *Multidimensional Spacetime and Dynamical Gravity* §5), **insufficient to produce anti-gravity by itself**.
- If $\alpha_\mathrm{scale}\lesssim8\times10^{-4}$: $\mathcal{R}\gtrsim1$, the chiral repulsion is of the same order as the Newtonian term or even dominant → **net repulsion (anti-gravity) holds**.

Since $\alpha_\mathrm{scale}$ is a dimensionless free coupling in the theory, whose physical anchoring is deferred to experiment (see Part I §9), **"whether anti-gravity is reachable" is here precisely reduced to an experimentally decidable number**: the order of magnitude of $\alpha_\mathrm{scale}$.

### 4.3 Design Equation for Complete Cancellation

Requiring $a_\mathrm{SRE}=0$ at some radius $r$ (ignoring the uniform term):

$$
\xi^{*}=\frac{2\,\alpha_\mathrm{scale}\,\mathcal{W}_{ij}\,\ln(r/\ell_P)}{\big|\sin(\cdot)\big|}
\;\xrightarrow[\ \sin=1\ ]{}\;
2\,\alpha_\mathrm{scale}\,\mathcal{W}_{ij}\,\ln(r/\ell_P)
$$

Then, from $\xi=0.08e^{0.15\mu}$ (*Multidimensional Spacetime and Dynamical Gravity* §2.3), invert to find the required center-of-mass redshift:

$$
\boxed{\;\mu_\mathrm{cancel}=\frac{20}{3}\,\ln\!\Big(\frac{\xi^{*}}{0.08}\Big)\;}
$$

---

## 5 Geometric Criterion: Compensation-Operator Peak $\hat{\mathcal{D}}_0^{*}=\dfrac{1}{2\alpha_0}$

Differentiating $\hat{\mathcal{C}}(\hat{\mathcal{D}})=\alpha_0^{-1}\sin^2(\pi\alpha_0\hat{\mathcal{D}})$ (definition in *Multidimensional Spacetime and Dynamical Gravity* §2.2):

$$
\frac{d\hat{\mathcal{C}}}{d\hat{\mathcal{D}}}=\alpha_0^{-1}\cdot 2\sin(\pi\alpha_0\hat{\mathcal{D}})\cos(\pi\alpha_0\hat{\mathcal{D}})\cdot\pi\alpha_0
=\pi\,\sin\!\big(2\pi\alpha_0\hat{\mathcal{D}}\big)
$$

- Extremum condition $\sin(2\pi\alpha_0\hat{\mathcal{D}})=0\Rightarrow \hat{\mathcal{D}}=\dfrac{n}{2\alpha_0}$, $n\in\mathbb{Z}$;
- The first **maximum** (strongest compensation) is at $\hat{\mathcal{D}}_0^{*}=\dfrac{1}{2\alpha_0}$, with maximum value $\hat{\mathcal{C}}_{\max}=1/\alpha_0$;
- The zeros are at $\hat{\mathcal{D}}=\dfrac{n}{\alpha_0}$ (compensation collapses to zero).

Numerically (SDSS window): $\Delta z\approx0.03925$, $\alpha_0=\theta/\Delta z=21.094$ (*Multidimensional Spacetime and Dynamical Gravity* §2.4), hence

$$
\hat{\mathcal{D}}_0^{*}=\frac{1}{2\alpha_0}=\frac{\Delta z}{2\theta}=\frac{0.03925}{2\times0.82798}=0.02370
$$

**Meaning**: The compensation operator is the "routing compute" that the network schedules to offset dissipation, and it is **non-monotonic**. If the local operating point can be placed at a zero of $\hat{\mathcal{C}}$ ($\hat{\mathcal{D}}=n/\alpha_0$), then the compensation in that region collapses → $R^2$ collapses → the gravity generated by the dissipation gradient is locally zeroed ("resonant zero-point shielding").

**Honest order-of-magnitude limitation**: Under realistic parameters $\epsilon_\mathrm{mach}\sim2\times10^{-16}$, $\sigma_z\sim10^{-2}$, so

$$
\hat{\mathcal{D}}=\ln\!\Big(1+\frac{\sigma_z^2}{\epsilon_\mathrm{mach}}\Big)\approx 2\ln\sigma_z+36.0\approx 26.8
$$

and $1/\alpha_0\approx0.0474$, so $\hat{\mathcal{D}}$ is already in the **strong-oscillation regime** (about $565$ oscillation periods). The region-averaged compensation is then pinned at the envelope mean:

$$
\langle\hat{\mathcal{C}}\rangle=\alpha_0^{-1}\langle\sin^2\rangle=\frac{1}{2\alpha_0}=0.02370
$$

which **exactly equals** the value of $\hat{\mathcal{D}}_0^{*}$. To "lock" onto a particular zero, one would need to control $\ln\sigma_z$ to $10^{-8}$-level precision—**practically uncontrollable**. Hence this channel of Part I §5 is **mathematically valid but engineering-fragile**: it explains why intrinsic oscillations and a discrete spectrum exist at the geometric scale, but it does not constitute a clean shielding knob.

---

## 6 Actuation Mechanism: Op2 Maximum-Entropy Pruning and "Boundary-ness"

### 6.1 Mechanism (*Necessity of Turbulence Emergence* §4.2–§4.3, verbatim)

Pruning probability (maximum-entropy pruning master equation):

$$
p_\text{prune}(v_f,v_m)=1-\frac{1}{1+\Gamma\cdot\dfrac{\mathcal{D}_s}{\mathfrak{B}}}
$$

When pruning occurs ($\chi=0$), **Paradigm B (eliminate–conduct)** is executed:

$$
M_{n+1}(i,j)\leftarrow \chi\cdot M_{n+1}(i,j)+(1-\chi)\cdot 1
$$

"That is, the channel spin is forcibly set to the multiplicative identity $+1$, thereby eliminating that channel's phase contribution from the product feedback loop without disconnecting graph connectivity. Surviving channels ($\chi=1$) are injected with an antisymmetric chiral shear." (*Necessity of Turbulence Emergence* §4.2)

The pruning gain $\Gamma$ has two modes (*Necessity of Turbulence Emergence* §4.3):

| Mode | Pruning gain | Meaning |
|---|---|---|
| A (exogenous) | $\Gamma=\Lambda$ | $\Lambda$ directly serves as the phase-transition control quantity |
| B (adaptive) | $\Gamma=\Lambda\cdot\lambda(n)$ | Superimposed with state-adaptive correction |

### 6.2 Why This Is the Physical Actuation Channel for Shielding

- After the channel spin is set to $+1$ (multiplicative identity), that edge's contribution to the **product feedback loop** is eliminated, but **connectivity is preserved**—precisely the property required by "shield without destroying": cutting phase contribution ≠ cutting topology.
- Raising the local pruning gain $\Gamma$ (i.e., raising the local $\Lambda$) → raises $p_\text{prune}$ → more edges go dormant → the local multi-loop structure is weakened → the local ability to maintain a low $\sigma_z$ (coherent measurement) decreases → $\sigma_z$ rises → by Part I §3, $\Xi<1$, so **gravity is locally weakened**.
- Therefore **$\Lambda$ (or the local $\Gamma$) is precisely the control knob for "gravitational shielding"**.

### 6.3 Boundary Operation, Not Internal Rewriting (Key Clarification)

"Shielding" has two distinct meanings in this document (a trap, do not conflate):
1. **Observational shielding / read-only barrier**: the internal topology of a mass closed loop is "non-addressable, non-writable"; the outside can only manipulate the rendering layer as a whole (electromagnetic, scattering). → **We cannot directly "dismantle" the mass closed loop of a target object** (that is exactly the source of the infeasibility of topological decoupling; *Logical-Depth Anchoring and Safety Shielding* Section 3).
2. **Phase-contribution shielding / gating**: Op2 sets the edge's spin to the multiplicative identity, eliminating its phase contribution to the feedback loop while **not breaking global connectivity**. → This is an **accessible** operation.

Combining the two gives the correct picture: **gravitational shielding is a boundary operation**—it does not rewrite the object's interior (non-addressable), but performs gating (Op2) **on the dissipation–compensation channel between the object and the external network**, so that the region's dissipation gradient as measured externally is suppressed. By analogy: it is not "turning off the inside of the light bulb", but "inserting a controllable scattering layer between the light bulb and the observer".

---

## 7 Three Intensity Tiers and Hard Boundaries

### 7.1 Three Tiers

| Tier | Mechanism | Reachability | Order of magnitude |
|---|---|---|---|
| **A Weight reduction** | Local injection of $\sigma_z$ (Part I §3 main channel) | Self-consistent, engineerable | $\Xi\sim0.98$ (about 2%), rising logarithmically with injection |
| **B Shielded weightlessness** | Boundary Op2 gating + suppression of the local dissipation gradient; or (fragilely) locking a compensation zero | Theoretical boundary | $\Xi\ll1$, but requires continuous power input to counter self-repair |
| **C Topological decoupling** | Directly release the mass closed loop ($m\equiv$ closed loop; *Reconstruction of Classical Electrodynamics* §4) | Hypothesis-level | Blocked by the read-only barrier, **no known stable mechanism** |

### 7.2 Hard Boundaries (Why This Is Not a Perpetual-Motion Machine)

1. **The uniform term is unshieldable**: $-\gamma c_\mathrm{eff}^2/4$ is a global term that local operations cannot eliminate; any "local weightlessness" is superimposed on this background.
2. **The compensation operator is self-repair**: $\hat{\mathcal{C}}$ is the self-patching mechanism by which the network counters dissipation and maintains numerical stability (*Multidimensional Spacetime and Dynamical Gravity* §2.2). The $\sigma_z$ you inject will be continuously "flattened" by the network, so shielding requires **continuous energy input**; there is no steady-state weightlessness with zero input.
3. **Order of magnitude of the chiral term**: unless $\alpha_\mathrm{scale}\lesssim8\times10^{-4}$, $\Gamma_\mathrm{chiral}$ is only a $10^{-3}$-level perturbation and cannot produce anti-gravity by itself (Part I §4).
4. **Topological decoupling destroys the definition of mass**: locally releasing a closed loop locally cancels the very concept of "mass"; the current formalization cannot guarantee the stability and recoverability of the decoupled region.

---

## 8 Design Equations and Falsifiable Predictions

**Summary of design equations**

$$
\Xi=\frac{1+\ln(1+\sigma_z)}{1+\ln(1+\sigma_z')}
\qquad
\sigma_z'=\exp\!\Big(\tfrac{1+\ln(1+\sigma_z)}{\Xi}-1\Big)-1
$$

$$
\hat{\mathcal{D}}_0^{*}=\frac{1}{2\alpha_{0,\mathrm{dynamic}}}=\frac{\Delta z}{2\theta_\mathrm{conformal}}
\qquad
\mu^{*}=\frac{4n-1}{4\alpha_{0,\mathrm{dynamic}}}
\qquad
\mu_\mathrm{cancel}=\frac{20}{3}\ln\!\Big(\frac{\xi^{*}}{0.08}\Big)
$$

**Falsifiable predictions**

1. **Shielding amount is independent of the absolute gravitational constant**: under a fixed increment of $\sigma_z$, the gravity-weakening ratio $1-\Xi$ should be independent of the test mass and position (universality). Any "material-dependent" additional shielding would require introducing a mechanism beyond $\mathcal{W}_{ij}$.
2. **Logarithmic law**: the weight-reduction effect saturates with injected entropy in a $1/(1+\ln)$ form—the marginal benefit of increasing injection diminishes (distinguishable from a "linear response" prediction).
3. **Phase reversal**: in the Rank=4 region ($z\ge z^*$), when the local center-of-mass redshift is tuned to $\mu^{*}$, a sign flip/zero of $G_\mathrm{eff}$ should appear (corresponding to the smooth $G_\mathrm{eff}$ oscillation described in *Multidimensional Spacetime and Dynamical Gravity* §5).
4. **$\alpha_\mathrm{scale}$ criterion**: if experiments measure $\alpha_\mathrm{scale}\gtrsim10^{-3}$, then "net anti-gravity" is falsified within SRE (only weight reduction is possible); if $\alpha_\mathrm{scale}\ll10^{-3}$, then chiral repulsion is the dominant channel.

---

## 9 Relation to the Uncalibrated $\alpha_\mathrm{scale}$

$\alpha_\mathrm{scale}$ "appears" throughout the text but is never "calibrated" (see the localization conclusion from the previous round); moreover, according to the SRE axioms, **before anchoring, all quantities are dimensionless numbers**. This brings one advantage and one cost:

- **Advantage**: The shielding factor $\Xi$ of the Part I §3 main channel is independent of $\alpha_\mathrm{scale}$, so the "weight-reduction ratio" is a testable prediction that can be **given prior to anchoring**.
- **Cost**: "whether chirality can dominate" in Part I §4, and "whether net anti-gravity is truly possible", **depend uniquely on the order of magnitude of $\alpha_\mathrm{scale}$**—which must be fixed only after future experiments (Newtonian-limit calibration).

Therefore this derivation compresses "anti-gravity" from a slogan into a definite experimentally-decidable numerical criterion: **the order of magnitude of $\alpha_\mathrm{scale}$**.

---

## 10 Open Questions (To-Do)

1. An explicit mapping between $\Lambda$ (the local pruning gain) and macroscopic observables ($\sigma_z$ injection rate, shielding power).
2. The **construction and reachability** of Op2 local gating: how the Op1 frontier (node injection) delivers the control signal to the target boundary while being constrained by the read-only barrier. → **Completed; see Part I §11**.
3. Chiral-phase tunability: the specific observables and operating window for setting $\mu^{*}$ by changing the subgraph redshift composition.
4. The **stability and dissipation cost** of the shielded region: the lower bound on continuous power required to counter the self-repair of $\hat{\mathcal{C}}$.

---

## 11 Op2 Local Gating Construction and Op1 Reachability (Execution Plan)

### 11.1 Three Reachability Constraints (Primary Sources)

| # | Constraint | Content | Source |
|---|---|---|---|
| 1 | **Read-only inheritance** | $M_{n+1}[1{:}n,1{:}n]\equiv M_n$: once realized, the historical sub-block cannot be retroactively modified (with axiomatic status) | *Necessity of Turbulence Emergence* §4.1 Operator 1 |
| 2 | **Frontier-size upper bound** | $M_K\le K_0\ll n$: each step acts on only $O(1)$ frontier channels, decoupled from the network-wide size | *Graph-Operator Pipeline Whitepaper* §5.3 Operator 8 |
| 3 | **Read-only/causal barrier** | The deep interior topology of the target closed loop is non-addressable and non-writable; $\ell_\min$ is the lower bound of addressable scale at the rendering layer | *Logical-Depth Anchoring and Safety Shielding* Section 3 |

> Key distinction (*Logical-Depth Anchoring and Safety Shielding* Section 3): the barrier **does not prevent ordinary physical manipulation of the entire topological closed loop at the rendering layer** (electromagnetic fields, scattering); it only forbids **penetrating the closed loop to rewrite its deep interior topology**.

**Corollary 11.1 (Reachability Theorem)**: Op2 gating **cannot act on the interior closed loop of the target object**; it can only act on the **boundary channel** between "the target region ↔ the external network"; moreover, by constraint 1, **existing old edges cannot be rewritten**—the control signal must be fed in via the Op1 **newly added frontier nodes**. ⇒ Shielding is a **boundary-layer, incremental** operation.

### 11.2 Four-Step Construction of Local Gating (Aligned with the Operator Pipeline)

Goal: on the boundary shell $\Omega_\partial$ surrounding the target region, set **redundant** dissipation–compensation channels to dormant ($\chi=0$, spin → $+1$), while preserving cut-set connectivity.

**Step 1 Op1 access** (Operator 1 boundary expansion $\mathcal{G}_{n\to n+1}$, *Necessity of Turbulence Emergence* §4.1):

$$
M_{n+1}=\begin{pmatrix}M_n & \mathbf{x}_{n+1}\\ \mathbf{x}_{n+1}^T & y_{n+1}\end{pmatrix},\qquad M_{n+1}[1{:}n,1{:}n]\equiv M_n
$$

Push a ring of frontier nodes $\mathcal{V}_\partial$ into the perimeter of the target region (new rows/columns; history is read-only). **What is addressable is only these newly added boundary nodes, not the object's interior**—this is precisely the only legitimate interface that bypasses the barrier.

**Step 2 Op2 gating** (Operator 2 maximum-entropy pruning, *Necessity of Turbulence Emergence* §4.2):

$$
p_\text{prune}=1-\frac{1}{1+\Gamma_\partial\cdot \mathcal{D}_s/\mathfrak{B}}
\;\xrightarrow[\ \Gamma_\partial\,\mathcal{D}_s/\mathfrak{B}\gg1\ ]{}\;1,
\qquad
M(i,j)\leftarrow \chi\,M(i,j)+(1-\chi)\cdot 1
$$

On $\Omega_\partial$, raise the local pruning gain to $\Gamma_\partial$, and roll the gate $\chi$ edge by edge; boundary edges with $\chi=0$ → $+1$ (**conducting but forming no loop**; *Complete Characterization of the Nucleon* §2.1).

**Step 3 Safety exemption** (Operator 10, *Graph-Operator Pipeline Whitepaper* §5.1): for the **bridge edges** on $\Omega_\partial$, enforce $\boldsymbol{\chi}_{e_\text{bridge}}\equiv1$, preserving

$$
\lambda_2(n+1)\ \ge\ \lambda_2(n)>0
$$

⇒ The graph does not tear, and global connectivity is preserved.

**Step 4 Effective-impedance screening** (also belonging to the effective topological-impedance criterion of Operator 10, *Graph-Operator Pipeline Whitepaper* §5.1): use $\mathbf{L}_n^{+}$ to compute the effective topological impedance of candidate edges

$$
\mathbf{Z}_\text{eff}(u,v_f)=(\mathbf{e}_u-\mathbf{e}_{v_f})^T\,\mathbf{L}_n^{+}\,(\mathbf{e}_u-\mathbf{e}_{v_f})
$$

**Only low-impedance (non-bridge) edges are allowed to go dormant.** This gives the **geometric criterion** for gating: shielding only consumes "redundant channels" and does not touch "unique channels".

### 11.3 Quantitative Reachability Bound (Upper Limit of Shieldable Fraction)

Let the boundary shell $\Omega_\partial$ have $|V_\partial|$ nodes and $|E_\partial|$ edges. Operator 10 requires retaining a spanning tree ($|V_\partial|-1$ edges), so the **number of dormable edges** is

$$
N_\text{gate}\ \le\ |E_\partial|-(|V_\partial|-1)
$$

**Upper limit of the shieldable channel fraction**

$$
\boxed{\ \frac{N_\text{gate}}{|E_\partial|}\ \le\ 1-\frac{|V_\partial|-1}{|E_\partial|}\ =\ 1-\frac{2}{\langle k\rangle}\ }
$$

($\langle k\rangle$ is the boundary average degree.) Example: $\langle k\rangle=4$ ⇒ at most **50%** of boundary channels can be shielded per operation; $\langle k\rangle=6$ ⇒ upper limit 67%.

**Meaning (falsifiable)**: The upper limit of shielding capability is determined by the **boundary topological redundancy**, not by energy alone; low-connectivity (near-bridge) boundaries are **structurally unshieldable**.

### 11.4 Control-Signal Path and Diffusion Cost

The transfer chain of the control quantity $\Gamma_\partial$ (Mode A: $\Gamma=\Lambda$; Mode B: $\Gamma=\Lambda\lambda(n)$, *Necessity of Turbulence Emergence* §4.3):

$$
\Lambda_\text{local}\ \xrightarrow[\ \text{Op1}\ ]{}\ \mathcal{V}_{n+1}\ (\text{frontier-variable injection})\ \xrightarrow[\ \text{Op2}\ ]{}\ \Gamma\ \text{acts on candidate frontier edges}\ \xrightarrow[\ \text{Op6/10}\ ]{}\ \Omega_\partial\ \text{executes gating}
$$

Key costs (from constraints 1+2):

- **Each step affects only $M_K\le K_0$ channels** ⇒ gating the entire shell requires $N_\text{steps}\ge M_\partial/K_0$ ⇒ shielding is **established diffusively and gradually**, with a time cost $\propto$ boundary area/perimeter, and **cannot be instantaneous**.
- Each step of frontier expansion "injects new random differences and expands outward" (*Complete Characterization of the Nucleon* §2.1)—the advance itself raises the local $\sigma_z$. **Two-sidedness**: on the positive side, it directly contributes to the Part I §3 main channel ($\Xi<1$); on the negative side, the injected differences are **uncontrollable random quantities**, making the shielding band fluctuate randomly frontier by frontier.
- Because of read-only inheritance (constraint 1), shielding is **non-rollbackable**—to undo shielding, a new frontier must be built; old edges cannot be reverted.

### 11.5 Why Tier C (Topological Decoupling) Is Thoroughly Blocked

Tier C requires **dismantling an already-realized mass closed loop** ($m\equiv$ closed loop; *Reconstruction of Classical Electrodynamics* §4). But: the read-only barrier makes the deep interior topology non-addressable and non-writable (*Logical-Depth Anchoring and Safety Shielding* Section 3); and read-only inheritance $M_{n+1}[1{:}n,1{:}n]\equiv M_n$ does not permit rewriting existing edges (*Necessity of Turbulence Emergence* §4.1).

**Double blocking** ⇒ within the theory there **exists no accessible operation** capable of dismantling an already-realized closed loop. Hence Tier C is not "hypothesis-level" but **mechanically excluded**. The only exception is the rendering-layer holistic manipulation permitted by *Logical-Depth Anchoring and Safety Shielding* Section 3 (electromagnetic/scattering)—that is the **transport/interaction** of mass, not the elimination of mass.

### 11.6 Summary (Grading of Executable Claims)

| Claim | Status | Basis |
|---|---|---|
| Boundary shell can be gated by Op2 | **Constructible** | Part I §11.2 four steps |
| Shieldable fraction $\le 1-2/\langle k\rangle$ | **Structural theorem** | Part I §11.3 |
| Shielding is gradual, non-instantaneous, non-rollbackable, and requires continuous power | **Constraint corollary** | Part I §11.4 + Part I §7 |
| Interior closed loop can be dismantled (true anti-gravity/topological decoupling) | **Mechanically excluded** | Part I §11.5 |

---

## Part II　Reverse Interpretation of the Podkletnov Result and the Difficulty of Reproduction

**Premise (assuming the result holds)**: an object above a rotating YBCO superconducting disk loses about 2% of its weight (Podkletnov & Nieminen 1992); a double-layer disk produces a stronger effect; a later "impulse gravity generator" gives a directed force.
**Task**: not to question the experiment, but to explain **why it holds** within the SRE framework, and to give discriminable predictions—as well as why others find it hard to reproduce.

---

## Part II-1 Pivot: Two Opposite Effects of Coherent Saturation

"Phase-coherent saturation ($\rho\to1$)" has **two oppositely-signed** consequences in SRE; conflating them necessarily yields the wrong sign:

| | Mechanism | Consequence |
|---|---|---|
| **Interior effect** | Closed-loop merging, combinatorial explosion of secondary feedback paths | Relational space collapses $D\to0$, **mass rises nonlinearly** (*Composite Elementary Particles* §Discussion · Model capability boundary) |
| **Boundary effect** | Relative phases are pinned flat ⇒ the local **dissipation gradient is flattened** | The gravity source (= dissipation gradient, *Multidimensional Spacetime and Dynamical Gravity* §5) is suppressed ⇒ **weight reduction** |

**Weight reduction comes from the boundary effect, not the interior effect.** This distinction is the pivot of the entire explanation chain.

## Part II-2 Mechanism Chain (Five Steps)

1. **Superconductor = phase-rigid plate**: Cooper pairs drive the in-disk network into macroscopic phase locking ($\rho\to1$; *Composite Elementary Particles* §1.3 and §II), pinning the channel relative phases to the same value.
2. **Equivalent to Op2 dormancy**: phase locking makes the disk↔outside boundary channels behave equivalently to dormant edges $M(i,j)\leftarrow+1$—"**conducting but forming no loop**" (*Complete Characterization of the Nucleon* §2.1; mechanism definition in *Necessity of Turbulence Emergence* §4.2). The disk becomes a **gating layer** that only conducts and does not generate multi-loop feedback.
3. **Dissipation gradient is short-circuited**: on the boundary shell $\Omega_\partial$, execute the four steps of Part I §11 (Op1 access → Op2 gating → Operator 10 preserving $\lambda_2>0$ → effective-impedance screening consuming only low-$Z_\text{eff}$ redundant edges), reducing the local stiffness $\mathcal{W}_{ij}$ of the test mass.
4. **Rotation = chiral bias**: surviving channels are injected with an antisymmetric chiral shear (*Necessity of Turbulence Emergence* §4.2), pushing the phase $\pi\alpha_0\!\cdot\!2\mu$ away from zero, so that $\Gamma_\mathrm{chiral}$ acquires an **outward** component ⇒ a small anti-gravity term is superimposed, and a **directionality** along the rotation axis is given.
5. **Layer compounding**: each disk layer is a boundary shell, $\Xi_\text{tot}=\prod_k\Xi_k$ ⇒ the stronger double-layer effect is a **product law**.

## Part II-3 Quantitative Self-Consistency

$$\Xi=\frac{1+\ln(1+\sigma_z)}{1+\ln(1+\sigma_z')}$$

$2\%$ weight reduction $\Rightarrow \Xi=0.98 \Rightarrow$ $\sigma_z$ need only be ×3. This belongs to **Tier A weight reduction** (Part I §7), matching the order of magnitude of the "weight-reduction ceiling of about 2%"—**this is precisely why the effect is small**.

## Part II-4 Why Only About 2% (Hard Boundaries)

- Upper limit of the shieldable fraction $1-2/\langle k\rangle$ (capped by boundary redundancy; Part I §11.3);
- Limited coherence budget (the phase difference the disk can rearrange is finite);
- Must continuously counter the self-repair of $\hat{\mathcal{C}}$ ⇒ **it disappears upon stopping rotation/heating** (consistent with the experiment's requirement of "low temperature + rotation").

## Part II-5 Discriminable Predictions (If the Result Holds, SRE Requires These to Co-occur)

1. **Tc discontinuity**: the effect vanishes **abruptly** as the temperature crosses the superconducting critical temperature (coherent saturation is a phase transition, not a gradual change).
2. **Chirality**: the effect depends on the **direction** of rotation (sign reversal), and is monotonic with rotation speed.
3. **Product law**: multiple layers superimpose as $\prod\Xi_k$, **not** linear addition.
4. **Material independence**: the weight-reduction ratio of the shielded object is independent of its own composition/density ($\Xi$ depends only on $\sigma_z$).
5. **Counterintuitive**: during shielding, the **superconducting disk itself** should have its inertial mass **slightly increased** (the mass surge from interior closed-loop merging; *Composite Elementary Particles* §Discussion · Model capability boundary), while the object above the disk becomes lighter—this is the discriminant that separates the two opposite effects.
6. **Geometry**: weight reduction occurs only **above the disk** and varies with the rotation-axis orientation (boundary gating + chiral directionality).

## Part II-6 Bounds and Extensions

- Belongs to **gravitational shielding (Tier A/B)**, not Tier C topological decoupling (the latter is **doubly excluded** by the read-only barrier + read-only inheritance; Part I §11.5).
- The "impulse gravity generator" = the **$\Gamma_\mathrm{chiral}$ traveling wave** emitted by a coherent chiral source (a directed phase pulse of an open loop), isomorphic to the SRE picture "closed→open = luminescence/radiation" (*Reconstruction of Classical Electrodynamics* §4).
- The same mechanism as Section I of the early conjecture, "superconductivity isomorphism: back-reaction of causal developmental probability"; here it lands on the concrete operators $\mathcal{W}_{ij}$ and Op2.

## Part II-7 Why Others Find It Hard to Reproduce (Same SRE Framework)

| # | Irreproducibility mechanism | SRE basis | What reproduction must control |
|---|---|---|---|
| 1 | Boundary redundancy is an **exogenous local quantity**, differing across samples ⇒ different $\Xi$ | $\Xi$ depends on $\sigma_z$ (Part I §3); shieldable fraction $\le1-2/\langle k\rangle$ (Part I §11.3) | Single-phase single crystal, specified crystallographic orientation/twin structure |
| 2 | Coherent saturation is a **phase-transition criticality**; off the critical point it fails avalanche-like | $\rho\to1$ saturation (*Composite Elementary Particles* §1.3, §II) | Strict temperature control, pushing $\langle\rho\rangle$ to the critical neighborhood |
| 3 | **Path dependence** (read-only inheritance ⇒ hysteresis, non-ergodicity) | Op1 read-only inheritance (*Necessity of Turbulence Emergence* §4.1) | Reproduce the **cooling/rotation time-sequence protocol**, not just the final-state parameters |
| 4 | Frontier expansion **carries its own random-difference injection**; the small effect is buried by noise | The sim_p generator injects random differences at each step (*Complete Characterization of the Nucleon* §2.1) | Sufficient averaging / per-frontier locking |
| 5 | $\hat{\mathcal{C}}$ **self-repairs**; requires continuous power + the correct sampling time window | Part I §7 hard boundaries | Steady-state power + correct duty cycle |
| 6 | **The chiral phase is signed and exogenous**; if unmatched, the directional part vanishes or reverses | $\Gamma_\mathrm{chiral}\propto\sin(\pi\alpha_0 2\mu)$ (*Multidimensional Spacetime and Dynamical Gravity* §5) | Phase matching (rotation-axis orientation / subgraph window) |
| 7 | The order of magnitude is only 2%, and **boundary effects are easily mechanically short-circuited** | 2% ≈ buoyancy/thermal drift; boundary gating (Part I §11) | Decoupled support + differential measurement |

**Falsifiability boundary (against excuse-making)**: if some experiment **simultaneously** satisfies the above 7 conditions (especially $\langle\rho\rangle$ in the critical neighborhood, phase matching, and consistent historical protocol) and still measures no effect, then **Tier A weight reduction is falsified**—"hard to reproduce" ends here and can no longer serve as an explanation.

---

## Appendix A Symbol Table

| Symbol | Meaning | Source (article · section) |
|---|---|---|
| $a_\mathrm{SRE}$ | SRE gravitational acceleration, in two branches Rank=2/4 | *Multidimensional Spacetime and Dynamical Gravity* §5 |
| $\alpha_\mathrm{scale}$ | Dimensionless gravitational coupling (uncalibrated, pending experimental anchoring) | *Multidimensional Spacetime and Dynamical Gravity* §5 |
| $\mathcal{W}_{ij}$ | Topological stiffness weight (macroscopic mass equivalent), a decreasing function of $\sigma_z$ | *Multidimensional Spacetime and Dynamical Gravity* §2.3 |
| $\hat{\mathcal{D}}_{ij}$ | Topological dissipation tensor | *Multidimensional Spacetime and Dynamical Gravity* §2.2 |
| $\hat{\mathcal{C}}$ | Dynamic topological compensation operator (non-monotonic/oscillatory) | *Multidimensional Spacetime and Dynamical Gravity* §2.2 |
| $R_{ij}^2$ | Squared macroscopic metric distance | *Multidimensional Spacetime and Dynamical Gravity* §2.2 |
| $\gamma$ | Handshake-latency coefficient $=1/(2\pi e)=0.0585$ | *Multidimensional Spacetime and Dynamical Gravity* §2.2 |
| $\xi(z)$ | Higher-order loop correction $=0.08e^{0.15\mu}$ | *Multidimensional Spacetime and Dynamical Gravity* §2.3 |
| $\Gamma_\mathrm{chiral}$ | Chiral correction (the only sign-reversible term) | *Multidimensional Spacetime and Dynamical Gravity* §5 |
| $\mu$ | Baryonic center-of-mass redshift | *Multidimensional Spacetime and Dynamical Gravity* §2.3 |
| $\alpha_{0,\mathrm{dynamic}}$ | Dynamic compression coefficient $=\theta/\Delta z$ | *Multidimensional Spacetime and Dynamical Gravity* §2.4 |
| $\theta_\mathrm{conformal}$ | Conformal geometric exponent $\approx0.82798$ | *Multidimensional Spacetime and Dynamical Gravity* §2.4 |
| $\Lambda,\Gamma$ | Pruning gain / phase-transition control quantity (shielding knob) | *Necessity of Turbulence Emergence* §4.3 |
| $\ell_P$ | Planck length (emergent UV boundary) | *Multidimensional Spacetime and Dynamical Gravity* §5 |

## Appendix B Comparison with the Early Conjecture

| Early conjecture (Theoretical Synopsis Based on Status) | Corresponding item in this design | Verdict |
|---|---|---|
| Eliminating local observation probability → local $G$ drift | Raising local $\sigma_z$ → $\mathcal{W}_{ij}\downarrow$ (Part I §3) | Isomorphic, now quantified ($\Xi$) |
| Back-reaction of causal developmental probability (superconductivity isomorphism) | Network self-repair $\hat{\mathcal{C}}$ + Op2 gating | Corresponding, belongs to Tier B |
| Weight-reduction ceiling of about 2% (Podkletnov level) | $\Xi\approx0.98$ requires $\sigma_z$ ×3 | Order of magnitude consistent |
| Ramanujan theta + Bernoulli nested fitting | Not incorporated into this design (belongs to the fitting layer) | To-do |

---

**Basis (article · section correspondence)**: gravity source = dissipation gradient → *Multidimensional Spacetime and Dynamical Gravity* §5; $\mathcal{W}_{ij}$ → *Multidimensional Spacetime and Dynamical Gravity* §2.3; dissipation tensor and compensation operator → *Multidimensional Spacetime and Dynamical Gravity* §2.2; coherent saturation → *Composite Elementary Particles* §1.3, §II, §Discussion · Model capability boundary; Op2 dormancy mechanism → *Necessity of Turbulence Emergence* §4.2, and see *Complete Characterization of the Nucleon* §2.1; Op1 read-only inheritance → *Necessity of Turbulence Emergence* §4.1; frontier random-difference injection → *Complete Characterization of the Nucleon* §2.1; mass–energy equivalence / closed–open → *Reconstruction of Classical Electrodynamics* §4; read-only barrier → *Logical-Depth Anchoring and Safety Shielding* Section 3; permeability → *Graph-Operator Pipeline Whitepaper* §3.1 Operator 5; frontier-size upper bound and safety exemption/impedance criterion → *Graph-Operator Pipeline Whitepaper* §5.1 Operator 10, §5.3 Operator 8.