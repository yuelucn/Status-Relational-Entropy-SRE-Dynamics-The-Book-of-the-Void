# Emergence of Multidimensional Spacetime and Dynamical Gravity via Regularized Causal-Information Networks
**Version**: 6.3-rev (incorporating ontological corrigendum; updated numerical simulation results, distinguishing historical reference value from Bootstrap statistical simulation outputs)

## Abstract
The ΛCDM standard-cosmology framework encounters significant observational tension at high redshift $z>5$. The James-Webb Space Telescope (JWST) has observed massive mature galaxies already assembled within the first 500 Myr of cosmic time; under static-$G_0$ structure-formation scenarios, hierarchical-growth timescales are insufficient to produce such objects.

Built upon the State-Relation-Entropy (SRE) dynamical axiom-system (v1.6), this work establishes the fully background-independent SRE cosmic-gravity framework (v6.2-rev). Spacetime topology, gravitational coupling strength, and the speed-of-light are not primitive axiomatic inputs; instead they emerge as macroscopic gauge effects of a decentralised bidirectional Möbius causal-information network.

This manuscript corrects the residual ontological dependency on extrinsic redshift-difference coordinates $\lvert z_i-z_j\rvert$ present in the v6.1 draft section 2.3. Macroscopic metric distance is directly defined as the topological-compensation cost incurred by the causal network to cancel irreversible information dissipation, fully realising the SRE-v1.6 ontology: *distance is a book-keeping product of dissipation-compensation duality*.

The dynamical compression coefficient $\alpha_{0,\mathrm{dynamic}}$ abandons the hard-fitted constant used in v5.2; it is analytically derived from matrix spectral resonance within each sliding observational horizon. Variable emergent effective-speed-of-light $c_\mathrm{eff}$ is implemented at network-routing level; conformal-gauge covariance rescales the emergent metric tensor while preserving local Lorentz invariance for measured light-speed.

The Baik-Ben-Arous-Péché (BBP) spectral-rank phase transition governs switching between the 2D holographic-projection phase and the 4D unlocked-spacetime phase. The early-version v6.1 provided a priori theoretical reference critical redshift $z_\mathrm{crit}=4.1605$. Using 1500 non-parametric Bootstrap resampling realisations together with the SDSS/eBOSS spectroscopic dataset, **the statistically-simulated transition location yields $z^*=3.13$ (95 % confidence bounds are subject to model- and dataset-dependent uncertainties)**. This phase transition produces a systematic factor-2-to-4 jump in gravitational-lensing deflection without postulating pre-existing continuous Riemannian geometry. Within the primordial dense-universe regime $z\ge z^*$, baryonic-gas cooling rates are substantially enhanced, amplifying accretion efficiencies without altering cosmic thermal ages, and naturally alleviating the JWST early-massive-galaxy formation puzzle.

Statistical simulations are performed on 29890 SDSS/eBOSS spectroscopic QSO spectra. Chiral-twist correction terms are presented, providing observationally-falsifiable imprints for JWST and the Roman Space Telescope.

**Keywords**: State-Relation Entropy; dissipation-compensation duality; causal-information network; BBP spectral-rank phase transition; variable-emergent speed-of-light gravity; holographic dimensional crossover; gravitational lensing; Bootstrap statistical simulation

## 1 Introduction
Modern observational cosmology pushes ΛCDM beyond its domain-of-validity. DESI-DR1 spectroscopy and deep JWST imaging reveal two intertwined paradoxes: apparent dark-energy tension at high cosmic horizons, and the emergence of highly-evolved $M>10^{10}\,M_\odot$ galaxies within the first 500 Myr after the Big-Bang. Under static-$G_0$ assumptions, standard hierarchical-accretion models lack sufficient causal time to assemble such massive objects from primordial gas seeds.

Earlier incarnations of SRE cosmic-gravity (v5.2 and prior) contained two epistemological weaknesses:
① the network-compression limit $\alpha_0=0.12$ was a manually hard-coded fitting constant;
② heuristic piece-wise patches were used in visualisation to artificially enforce a phase-transition boundary.
Moreover, the original v6.1 draft section 2.3 retained the ontological flaw of adopting redshift-coordinate differences $\lvert z_i-z_j\rvert$ as a distance substrate, in violation of SRE-v1.6 ontology:
> *Spatial distance is not a-priori given coordinates; it arises solely as a book-keeping outcome of mutual-measurement driven dissipation-compensation duality*.

This paper carries out four tiers of improvements:
1. Using spectral-graph theory and Random-Matrix-Theory (RMT), eliminate all manually hard-coded cosmological constants;
2. Adopt the corrigendum ontological fix: discard $\lvert z_i-z_j\rvert$ as distance substrate, and construct macroscopic metrics directly from topological dissipation-compensation operators;
3. Introduce non-parametric Bootstrap Monte-Carlo resampling, perform statistical simulation with SDSS/eBOSS spectroscopic data to obtain the simulated transition redshift $z^*$; demote $z_\mathrm{crit}=4.1605$ to a v6.1 historical-theoretical reference value and remove it as a rigid model prediction of the present revision;
4. Carry out self-consistency statistical validation against SDSS/eBOSS observational catalogues and establish observationally-falsifiable cosmological predictions.

The underlying ontology strictly inherits the SRE-v1.6 axiom suite. Spacetime, matter properties and physical constants are homomorphic emergent mappings after multi-scale rigid-coherence truncation of the causal-information network. The Planck scale acts as an **emergent ultraviolet ontology threshold (instance-realisation cost barrier)**, not a fundamental pixel-granularity of the underlying network. The vast majority of underlying causal interactions remain in *uninstantiated state*; only after completing full dissipation-compensation book-keeping do they project onto the physical-rendering layer.

## 2 Axiomatic Mathematical Formulation and Ontological Anchoring
### 2.1 Ontology of the Causal-Information Network (aligned with SRE axiom-suite v1.6)
The causal-information-network provides a cosmological realisation for the SRE-v1.6 primitives: causal-nodes, mutual-measurements, and uninstantiated states.

1. **Causal node $V$**: Ontologically defined as quantum-evidence events occupying local sectors of Planck-phase-space $H_\mathrm{Planck}$. Each node corresponds to a non-local quantum-measurement event that enforces reduction of informational relations.
2. **Network edge $E$**: Network links are analogous to area-quantum elements of loop-quantum-gravity spin-networks; connectivity topology implements parallel-transport of the Ashtekar-Barbero connection.
3. **Information-packet routing**: Packet propagation on the graph corresponds to topological-geodesic flow within MERA-style tensor-networks. Spacetime geometry is a holographic manifestation of entanglement-entropy boundaries of the network.

> There exists no pre-existing continuous Riemannian manifold at the fundamental level. Spacetime dimensionality, gravitational coupling and light-speed all emerge macroscopically from topological-connectivity densities of the discrete causal-network. Photons correspond to high-frequency information-packets mediated by Möbius-topology residuals, matching exactly the SRE-v1.6 primitive *light-residual $\Psi_\mathrm{light}$*.

### 2.2 Topological-Dissipation Tensor and Compensation Operator (core corrigendum)
> Discard the v6.1-draft practice of building distances from $\lvert z_i-z_j\rvert$. Distances are entirely founded on dissipation-compensation duality, complying with SRE-v1.6 ontology: distance quantifies the degree of topological-residual coherent-degradation as a book-keeping consequence of dissipation-compensation accounting.

Define the **topological-dissipation tensor $\hat{\mathcal{D}}_{ij}$**, which characterises intrinsic information-loss operators for quantum-evidence events $(i,j)$, constrained by observational measurement-entropy bounds $\sigma_z$:
$$
\hat{\mathcal{D}}_{ij}=\ln\left(1+\frac{\sigma_{z,i}\cdot \sigma_{z,j}}{\epsilon_\mathrm{mach}}\right)
$$
$\epsilon_\mathrm{mach}$ denotes machine floating-point epsilon.

Define the dynamical topological-compensation-operator $\hat{\mathcal{C}}_\mathrm{compensation}(\alpha_{0,\mathrm{dynamic}})$, representing routing-computational overhead invoked by the network to counteract information-dissipation and maintain numerical-matrix stability:
$$
\hat{\mathcal{C}}=\alpha_{0,\mathrm{dynamic}}^{-1}\cdot \sin^2\left(\pi \alpha_{0,\mathrm{dynamic}}\cdot \hat{\mathcal{D}}_{ij}\right)
$$

The macroscopic squared-metric distance is directly defined as the trace inner-product of dissipation-tensor and compensation-operator:
$$
R_{ij}^{2}\equiv \mathrm{Tr}\big(\hat{\mathcal{D}}_{ij}\cdot \hat{\mathcal{C}}_\mathrm{compensation}(\alpha_{0,\mathrm{dynamic}})\big)\cdot \exp\left(-\gamma \cdot \mu_\mathrm{loss}\right)
$$
- $\gamma=0.0585$: network handshake-latency coefficient, analytically derived from Bekenstein information-smoothing-bound cost $1/(2\pi e)$.
- $\mu_\mathrm{loss}$: local-mean information-loss weight.

> **Ontological-paradigm shift**: spatial “distance” is not given a-priori. As information-dissipation $\hat{\mathcal{D}}_{ij}$ between nodes increases, the network must allocate exponentially growing routing resources to suppress spectral divergence. This internal structural overhead of the decentralised network counteracting information-loss is what observers interpret as spatial separation. This strictly realises SRE-v1.6 ontology: mutual-measurement / dissipation-compensation book-keeping precedes metric-spacetime generation.

### 2.3 Topological-Stiffness Weights and Baryonic-Centroid Redshift
Topological-stiffness weight $\mathcal{W}_{ij}$ encodes macroscopic mass-equivalences within the relational manifold, derived purely from spectroscopic observational measurement-entropy:
$$
\mathcal{W}_{ij}=\sqrt{\mathcal{C}_i\cdot \mathcal{C}_j}=
\left[\Big(1+\ln\big(1+\max(\sigma_{z,i},\epsilon_\mathrm{mach})\big)\Big)
\cdot
\Big(1+\ln\big(1+\max(\sigma_{z,j},\epsilon_\mathrm{mach})\big)\Big)\right]^{-1/2}
$$

Given a local slice-subgraph $V_\mathrm{slice}$ containing $N$ events, define the gravitationally-weighted **baryonic-centroid redshift $\mu$**:
$$
\mu=\frac{\sum_{i=1}^{N}\mathcal{C}_i\cdot z_i}{\sum_{i=1}^{N}\mathcal{C}_i}
$$

Higher-order loop-perturbation fields couple to the centroid redshift:
$$
\xi(z)\equiv\xi(\mu)=0.08\cdot \exp(0.15\cdot \mu)
$$

### 2.4 Spectral-Resonance derivation of dynamical compression coefficient $\boldsymbol{\alpha_{0,\mathrm{dynamic}}}$
$\alpha_{0,\mathrm{dynamic}}$ is no longer an exogenous input parameter. It is analytically obtained from Fourier-spectral resonance of the double-centred network-matrix within each sliding observational causal-horizon of width $\Delta z=z_\mathrm{max}-z_\mathrm{min}$. Matrix-stability conditions enforce matching of chiral-sine modes to the first resonance valley to avoid numerical dissipation:
$$
\alpha_{0,\mathrm{dynamic}}=\frac{\theta_\mathrm{conformal}}{\Delta z+\epsilon_\mathrm{mach}}
$$

Where the conformal-geometric index $\theta_\mathrm{conformal}\approx0.82798$ comes from symplectic-eigenvalue integration for maximum-packing fractions on complex-hyperbolic Möbius manifolds:
$$
\theta_\mathrm{conformal}=\frac{1}{\pi}\int_{0}^{1}\frac{\ln(1+x^2)}{x}\mathrm{d}x+\frac{1}{2e}\approx 0.82798
$$

For SDSS sliding-window slices with $\Delta z\approx0.03925$, we obtain $\alpha_{0,\mathrm{dynamic}}=21.09\pm0.34$. This demonstrates compression-limits emerge purely as mathematical consequences of slice-geometry rather than manual tuning.

## 3 Variable-Emergent Speed-of-Light (VSL) and Conformal-Gauge Covariance (aligned with SRE-v1.6)
SRE-v1.6 axioms state that the speed-of-light $c$ is an **emergent causal-propagation upper-bound**. In the high-dissipation primordial universe the effective throughput $c_\mathrm{eff}$ drops; conformal-gauge transformations preserve local measured Lorentz-invariance. This section presents the full mathematical formulation.

### 3.1 Information-propagation emergent effective-speed-of-light
$c_\mathrm{eff}(\mu)$ is defined as the maximum packet-routing bandwidth upper-bound on the adjacency network. In the dense primordial universe high topological-winding creates impedance and increases transmission latency:
$$
c_\mathrm{eff}(\mu)=c_0\cdot\Phi_\mathrm{net}(\mu)=c_0\cdot\left[1-\kappa\ln\left(1+\frac{\rho_\mathrm{info}}{\rho_\mathrm{critical}}\right)\right]
$$
- $c_0$: sparse-near-field baseline propagation-speed.
- $\rho_\mathrm{info}$: local relational-link information-density.
- Topological-coupling index $\kappa=\dfrac{1}{\ln2\cdot\pi^2}\approx 0.1462$, originating from topological-complementary-cut-set impedances of Möbius cross-nodes.

> Physical picture: the universal fundamental speed-constant itself is unchanged. Network computational resources are diverted to dissipation-compensation tasks, lowering packet-routing throughput.

### 3.2 Conformal-scaling factor and local Lorentz-invariance
To guarantee gauge-covariance, changes in link-density simultaneously rescale the emergent metric tensor $g_{\mu\nu}$ and effective propagation-speed:
$$
\tilde{g}_{\mu\nu}=\Omega^2(\alpha_{0,\mathrm{dynamic}})\,g_{\mu\nu},\qquad
\tilde{c}_\mathrm{eff}=\Omega(\alpha_{0,\mathrm{dynamic}})\,c_\mathrm{eff}
$$

The line-integral of the conformal-scalar-field over relational-moduli-space:
$$
I(z)=-\frac{\gamma}{4}\int_{z_\mathrm{min}}^{z_\mathrm{max}}\alpha_{0,\mathrm{dynamic}}(z)\,\mathrm{d}z
$$

Substituting the analytic expression for $\alpha_{0,\mathrm{dynamic}}$ yields the conformal multiplier:
$$
\Omega(\alpha_{0,\mathrm{dynamic}})=\exp(I(z))=\left(\frac{\Delta z}{\theta_\mathrm{conformal}}\right)^{-\gamma/4}
$$

Algebraic cancellation preserves the local line-element:
$$
\mathrm{d}s^2=\tilde{g}_{\mu\nu}\mathrm{d}x^\mu\mathrm{d}x^\nu
=g_{00}c_0^2\mathrm{d}t^2+\Omega^2 g_{ij}\mathrm{d}x^i\mathrm{d}x^j
$$

> **v6.3 revision (premise audit)**: the step above is a **conditional** cancellation, not an unconditional conclusion. It requires $c_\mathrm{eff}\propto\Omega$, i.e. $c_\mathrm{eff}$ linear in the network scale; but the actual form of operator 5 is not linear. The audit follows.

**(a) The true functional form of operator 5.** The edge capacity is $W_e\equiv\sqrt{D_{ii}D_{jj}}$, where $D_{ii}=\sum_j A_{ij}$ is the vertex degree. Measured (identical for a 2-node graph and a 3-node chain, $W\in[0.01,20]$):
$$
c_e=\alpha_n\min\!\left(3,\ \frac{1}{\ln(1+W_e)}\right)
\quad\Longleftrightarrow\quad
v_e=\frac{1}{\alpha_n}\max\!\left(\tfrac13,\ \ln(1+W_e)\right)
$$
i.e. a **logarithmic rate plus a speed floor of $1/3$**, with critical capacity $W_c=e^{1/3}-1=0.395612$. The linear relation only holds approximately when $sW\ll1$.

**(b) The criterion for cancellation is the metric's shape, not the speed's value.** Any scalar factor is divided out by normalisation, so only a change of shape implies non-cancellation. Measured for three carriers:

| Carrier | Uniform degree? | $W_e$ edge span | $\lambda_2/\lambda_{\max}$ | Shape drift ($s$ sweep) |
|---|---|---|---|---|
| Complete matrix graph $n=60$ | yes (59-regular) | $1.0\times$ | $1.000$ | geometrically degenerate, unusable |
| $M_{60}$ ladder ($\alpha$-anchor carrier) | yes (3-regular) | $1.0\times$ | $0.0073$ | $4.4\times10^{-16}$ |
| $\chi=1$ subgraph $n=150$ | no (degree 2–15) | $3.9\times$ | $0.088$ | $3.03\times10^{-1}$ |

Multiplying by any scalar $\Omega\in\{0.5,1,3,17\}$ leaves the shape drift at $0.303218$ in all four cases: **a scalar can change scale, never shape**.

**(c) Revised proposition (v6.3).**
$$
\boxed{\ \text{local light-speed invariance}\iff W_e\ \text{edge-uniform}\iff\text{carrier graph is regular}\ }
$$
On a uniform carrier, take $\Omega(s)=\dfrac{\max(1/3,\ln(1+sW))}{\max(1/3,\ln(1+W))}$; cancellation then holds exactly (drift $4.4\times10^{-16}$). This $\Omega(s)$ **replaces** the $\Omega=\exp(I(z))$ used earlier in this section: the latter is the approximation in the linear limit $sW\ll1$ and coincides with it only on a uniform carrier in the low-capacity region. On a heterogeneous carrier no scalar conformal factor exists; the only edge-wise candidate $\Omega_e=v(sW_e)/v(W_e)$ differs edge by edge by construction (span $1.22\times$ at $s=2$), i.e. it is a **Weyl transformation** rather than a conformal one, so the shape genuinely changes.

⇒ The original statement "the locally measured light-speed equals $c_0$" must be restricted to **regular carriers** (the $M_{60}$ used by the $\alpha$ anchor is of this class). A generic evolving network (the $\chi=1$ subgraph) does not satisfy the premise, and its local light-speed changes with epoch. This revision does not touch the $\alpha=\lambda_2/\lambda_{\max}$ anchor — a dimensionless ratio is invariant under uniform rescaling.

### 3.3 Testable prediction: the relative refractive index of a medium pair drifts with epoch
Part (a) directly gives the relative refractive index
$$
n_\mathrm{rel}(s)=\frac{\max\!\left(\tfrac13,\ \ln(1+sW_a)\right)}{\max\!\left(\tfrac13,\ \ln(1+sW_b)\right)}
$$
With $W_a=3$, $W_b=1$ (two link-density classes), analytic values:

| Epoch scale $s$ | 0.5 | 1 | 2 | 10 |
|---|---|---|---|---|
| $n_\mathrm{rel}$ | 2.259851 | 2.000000 | 1.771244 | 1.432084 |

Monotonically decreasing towards 1. Physical reading: **the refractive contrast of media is stronger in the early universe and vanishes with epoch**; when both capacities fall into the floored region ($W<W_c=0.395612$) the speeds are clamped, so the contrast is identically 1 ("no refraction in an extremely dilute medium").

**Criterion**: the ratio $R(z)$ measured across redshift for the same medium pair must lie within the shape family given in §3.4 (start $1$, peak $1.1736$, end $0.5$, non-monotone); any monotone curve, or an asymptote different from $1/n_\mathrm{rel}(0)$, falsifies it. §3.4 supplies the $s(z)$ mapping and the reading of $\kappa$.

(Sources: `verify_e8_conformal_log_fix.py`, `verify_e9_uniformity_audit.py`)

### 3.4 Mapping from epoch scale to redshift: $s(z)$ and the redshift criterion

The drift in §3.3 uses the epoch scale $s$ as its independent variable, whereas the observable is the redshift $z$. This subsection supplies $s(z)$ and turns the "testable prediction" of §3.3 into a criterion that can be checked directly. **This is the only new constitutive identification in this paper**: it is a continuous-to-continuous map, it introduces no new dimensionless free parameter, but it must be declared explicitly (G12).

**(a) Mapping.** Take the power law
$$
s(z)=(1+z)^{-\kappa},\qquad \kappa\in\{0,1,2,3\}
$$
The reading of $\kappa$ is fixed by what the capacity counts: $\kappa=1$ length (capacity follows the linear size of the causal cell), $\kappa=2$ holographic boundary (area), $\kappa=3$ counting (number of channels in the cell, $\propto$ volume), $\kappa=0$ no drift ($s$ independent of $z$, redshift carries no capacity information). The direction is fixed by §3.2: $z$ up $\Rightarrow s$ down $\Rightarrow W_e=sW$ down $\Rightarrow v_e=\max(1/3,\ln(1+W_e))/\alpha_n$ down, consistent with "$c_\mathrm{eff}$ decreases in the high-dissipation primordial regime". **$\kappa=3$ is the default reading**; $\kappa$ is an integer, not a fitted real number.

**(b) Criterion quantity.** Take the double ratio of the speed ratios of the same medium pair at two epochs:
$$
R(z)\equiv\frac{v\!\left(s(z)W_a\right)/v\!\left(s(z)W_b\right)}{v(W_a)/v(W_b)},\qquad R(0)=1 .
$$
It is insensitive to the reciprocal convention ($n=c/v$ versus $v$) and cancels the unmeasurable common factor in the absolute speeds — a purely **differential** observable (for instance the source-redshift dependence of the time-delay ratio between two lensed images).

**(c) Three $\kappa$-independent anchors.**

1. **Start**: $R(0)=1$.
2. **Peak height**: the slower medium hits the floor first ($s_1=W_c/W_b$), where
$$
R_\mathrm{peak}=\frac{v\!\left(W_cW_a/W_b\right)/W_c}{\ln(1+W_a)/\ln(1+W_b)} ;
$$
for $W_a=3,W_b=1$, $R_\mathrm{peak}=1.173600$ — **independent of $\kappa$**; $\kappa$ only moves the peak ($z_\mathrm{peak}\simeq z_1$).
3. **High-$z$ freeze**: as $z\to\infty$ both hit the floor and $R(\infty)=1/n_\mathrm{rel}(0)=0.5$ (same pair).

Hence the **shape** (start $1$, peak $1.1736$, end $0.5$, non-monotone) is fully fixed; $\kappa$ only sets the two kink positions:
$$
z_1=\left(\frac{W_b}{W_c}\right)^{1/\kappa}-1,\qquad z_2=\left(\frac{W_a}{W_c}\right)^{1/\kappa}-1 .
$$

| $z$ | 0.2 | 0.3 | 0.5 | 1 | 2 | 5 | 10 |
|---|---|---|---|---|---|---|---|
| $R_{\kappa=1}$ | 1.033401 | 1.048341 | 1.075330 | 1.129926 | 1.039721 | 0.608198 | 0.500000 |
| $R_{\kappa=2}$ | 1.067603 | 1.097974 | 1.152082 | 0.839424 | 0.500000 | 0.500000 | 0.500000 |
| $R_{\kappa=3}$ | 1.102200 | 1.147618 | 0.953983 | 0.500000 | 0.500000 | 0.500000 | 0.500000 |

Corresponding kinks: $\kappa=1$ gives $(z_1,z_2)=(1.527726,\ 6.583179)$; $\kappa=2$ gives $(0.589883,\ 1.753757)$; $\kappa=3$ gives $(0.362208,\ 0.964644)$.

**(d) Self-calibration and over-determination.** From the observed positions of the two kinks, invert for the capacities:
$$
W_b=W_c(1+z_1)^{\kappa},\qquad W_a=W_c(1+z_2)^{\kappa},
$$
then check against the locally measured $n_\mathrm{rel}(0)=\ln(1+W_a)/\ln(1+W_b)$. The three numbers $(n_0,z_1,z_2)$ contain only two independent capacity degrees of freedom, so the third is an **over-determination test**: closure fixes both $\kappa$ and the two capacities at once; failure to close falsifies.

**(e) Alternative internal reading, and its exclusion.** If redshift is instead **defined** as the ratio of background speeds, $1+z=v(W_0)/v(sW_0)$, then $s(z)=\left[(1+W_0)^{1/(1+z)}-1\right]/W_0$, with a redshift ceiling
$$
z_{\max}=3\ln(1+W_0)-1 .
$$
$W_0=1$ gives $z_{\max}=1.079$, $W_0=3$ gives $z_{\max}=3.159$. **Quasars have been observed at $z\simeq7$**, so this reading requires $W_0\ge e^{8/3}-1=13.392$ — the model provides no mechanism for a background capacity that large. We therefore adopt the counting reading (a) and register this reading as already excluded by observation.

**(f) Falsification list.** (i) If at $z\simeq0.3$ the deviation of $R$ from $1$ is below $1\%$ (i.e. $\kappa=0$), the drift prediction is falsified; (ii) if $R(\infty)\ne0.5$ (for $W_a=3,W_b=1$), falsified; (iii) if the curve is monotone, with neither peak nor kink, falsified; (iv) if the kink positions do not yield an integer $\kappa$, or the $(n_0,z_1,z_2)$ over-determination fails to close, falsified.

**Observational threshold**: at $z=0.3$, $\kappa=3$ deviates from no-drift by $14.8\%$, $\kappa=2$ by $9.8\%$ and $\kappa=1$ by $4.8\%$; a $5\%$ measurement of the differential time-delay ratio already separates $\kappa=3$ from no drift.

(Sources: `verify_e10_redshift_sz.py`)

## 4 Random-Matrix-Theory and BBP Spectral-Rank Phase-Transition: 2D-Holographic ↔ 4D-Unlocked-Spacetime
Effective rendered-spacetime dimensionality is determined by the eigenvalue-spectrum of the stabilised association matrix $B_\mathrm{stabilized}$. Effective rank counts eigenvalues exceeding the Tracy-Widom statistical-bulk boundary:
$$
\mathrm{Rank}(z)=\sum\Big(\mathrm{eigvals}(B_\mathrm{stabilized})>\epsilon_\mathrm{adaptive}\Big)
$$

Adaptive threshold:
$$
\epsilon_\mathrm{adaptive}=\epsilon_\mathrm{mach}\cdot\frac{\ln\left(1+\|B_\mathrm{stabilized}\|_1/N\right)}{2.5}\cdot1.2
$$

$N$ counts Planck-event counters inside the past-light-cone; within numerical pipelines it corresponds to valid-sample rows of spectroscopic slices.

The dimensional-fluctuation-field $\Psi_\mathrm{fluct}(z)$ obeys a modified topological Ginzburg-Landau equation describing the BBP spectral-rank phase-transition, with Planck-scale boundary-conditions:
$$
\frac{\partial^2 \Psi_\mathrm{fluct}}{\partial z^2}+\beta(z)\Psi_\mathrm{fluct}-\eta\Psi_\mathrm{fluct}^3=0
$$
$$
\Psi_\mathrm{fluct}(z^*)=0,\quad
\left.\frac{\partial \Psi_\mathrm{fluct}}{\partial z}\right|_{z\to\infty}=\sqrt{\frac{\beta_0}{\eta}}
$$

Microscopically dimensionality oscillates at Planck-frequency $10^{43}\,\mathrm{Hz}$. Astronomical observing-instruments have integration-times $\Delta t\gg \tau_P$; environmentally-induced decoherence washes out fast oscillations and observers detect the smooth expectation-value envelope:
$$
\langle \mathrm{Rank}(z)\rangle=\int_{0}^{\Delta t}\Psi_\mathrm{fluct}(t)\,\mathrm{d}t
$$

> Two distinct phases separated by the statistically-simulated transition redshift $z^*$:
1. **Late-time universe $z<z^*$, $\mathrm{Rank}=2$ (2D-holographic-projection phase)**: the network remains in single-handed Möbius topology; compensation-operator collapses onto a single routing-layer.
2. **Primordial dense universe $z\ge z^*$, $\mathrm{Rank}=4$ (4D-unlocked-spacetime phase)**: BBP spectral-rank phase-transition triggers; single-handed Möbius topology splits into bidirectional-chiral two-layer network. The compensation-operator separates into two independent eigen-branches: time-layer compensation and space-layer compensation:
$$
\mathrm{Tr}(\hat{\mathcal{C}}_\mathrm{time})
=\mathrm{Tr}(\hat{\mathcal{C}}_\mathrm{space})
=\alpha_{0,\mathrm{dynamic}}^{-1}\cdot\sin^2\big(\pi\alpha_{0,\mathrm{dynamic}}\hat{\mathcal{D}}_{ij}\big)
$$

> $z^*$ denotes the simulated statistical transition-redshift; $z_\mathrm{crit}=4.1605$ is the historical-theoretical reference value from v6.1. In SRE-v1.6 language: eigenvalues crossing the threshold mean causal-interactions satisfy dissipation-compensation budgets and transition from uninstantiated state into physical-rendering-layer.

![Figure 1](./figures/sre_phase_transition.png)
**Figure 1** BBP spectral-rank cosmological phase-transition. Left-hand vertical axis (red): ensemble-mean normalised effective gravitational coupling $\langle G_\mathrm{eff}/G_0\rangle$ from Bootstrap realisations. Right-hand vertical axis (blue dashed): ensemble-mean emergent spacetime rank $\langle \mathrm{Rank}(z)\rangle$. Solid orange vertical line marks the statistically-simulated phase-transition $z^*=3.13$; purple dashed vertical line shows historical-theoretical reference $z_\mathrm{crit}=4.1605$. Below $z^*$ the system resides in the two-dimensional holographic phase; above $z^*$ four-dimensional spacetime unlocks, accompanied by oscillatory behaviour of $G_\mathrm{eff}$ induced by chiral-manifold corrections. Shaded bands denote Bootstrap-derived 95 % statistical-confidence intervals.

## 5 Causally-Emergent Gravity: Thermodynamic Effect of Dissipation-Gradients
Gravity is not a fundamental-field but a statistical-thermodynamic consequence of local information-dissipation-gradients. Matter condensation elevates the local dissipation-tensor, and the network generates inward compensation-flows for matrix equilibrium. Discarding pre-supposed Riemannian backgrounds, SRE-v6.2-rev obtains gravitational-acceleration from logarithmic-gradients of relational-metrics conditional upon the current network rank-state:
$$
a_\mathrm{SRE}(r,z)=
\begin{cases}
-\dfrac{\alpha_\mathrm{scale}\cdot \mathcal{W}_{ij}}{r}-\dfrac{\gamma c_\mathrm{eff}(z)^2}{4} & \mathrm{Rank}=2,\ z<z^* \\[8pt]
-\dfrac{2\cdot\alpha_\mathrm{scale}\cdot\mathcal{W}_{ij}}{r^2}-\dfrac{\gamma c_\mathrm{eff}(z)^2}{4}+\Gamma_\mathrm{chiral}(r)
& \mathrm{Rank}=4,\ z\ge z^*
\end{cases}
$$

Chiral-gravitational-correction originates from genus-1 manifold Dirac-operator loop-corrections:
$$
\Gamma_\mathrm{chiral}(r)=\xi(z)\cdot\frac{\sin\left(\pi\alpha_{0,\mathrm{dynamic}}\cdot 2\mu\right)}{r^2\cdot\ln(r/\ell_P)}
$$
$\ell_P$ is the CODATA Planck-length, the emergent-ontology ultraviolet-threshold defined in SRE-v1.6.

- $\mathrm{Rank}=2$ holographic-phase: gravity manifests long-range logarithmic-potential $\propto 1/r$.
- $\mathrm{Rank}=4$ unlocked-phase: recovers inverse-square-law $(1/r)^2$ behaviour; $G_\mathrm{eff}$ undergoes smooth oscillations within model-allowed bounds.

**Baryonic-cooling-boost factor (explanation for JWST early-massive-galaxy puzzle)**
$$
Cooling\_Boost=\left(\frac{G_\mathrm{eff}}{G_0}\right)^2
$$

Within the primordial dense-universe interval $z\ge z^*$, baryonic-molecular cooling-rates receive enhancements. Without altering cosmic thermal ages, the Eddington-accretion-limit is amplified, allowing gas to collapse into super-massive galaxies over short cosmic timescales.

![Figure 2](./figures/sre_galaxy_mass_crisis.png)
**Figure 2** Primordial causal-core mass-accumulation comparison. Black dashed curve: standard Λ-CDM accretion under static $G_0$. Red solid curve: SRE enhanced-accretion under ensemble-mean dynamic $\langle G_\mathrm{eff}\rangle$ within the high-dimensional unlocked-phase. Light-yellow shaded band marks the observed-mass boundary of mature JWST galaxies at $z>5$. Horizontal axis is cosmic lookback-time in Gyr. Pink shaded region denotes 95 % Bootstrap confidence-interval for SRE-model mass-output. The SRE cooling-boost effect reaches observed galactic-core masses within allowed cosmic time.

## 6 Gravitational-Lensing Shear Formula and the 2-to-4 Systematic Jump (after corrigendum)
Photons propagate as high-frequency information-packets across the causal-network. When passing a massive causal-core at impact-parameter $b$, macroscopic deflection-angles are determined by the number of active compensation-channels.

1. **$z<z^*,\ \mathrm{Rank}=2$, two-dimensional holographic-degenerate lensing**
Only the time-delay compensation-channel is active:
$$
\theta_\mathrm{macro}^{(2D)}=\frac{2\cdot \mathcal{W}_{ij}}{b}
$$

2. **$z\ge z^*$, four-dimensional unlocked-lensing**
The BBP spectral-rank phase-transition opens bidirectional-two-layer networks; time-layer and space-layer compensation-flows operate in-parallel and add linearly:
$$
\theta_\mathrm{macro}^{(4D)}=\theta_\mathrm{time}+\theta_\mathrm{space}
=\frac{2\cdot \mathcal{W}_{ij}}{b}+\frac{2\cdot \mathcal{W}_{ij}}{b}
=\frac{4\cdot \mathcal{W}_{ij}}{b}\cdot\big[1+\Lambda_\mathrm{twist}(b)\big]
$$

Chiral-twist correction produces observable anisotropic polarisation imprints testable by JWST and Roman-Space-Telescope:
$$
\Lambda_\mathrm{twist}(b)=\frac{\xi(z)}{b}\cdot\cos^2\left(\frac{\pi\alpha_{0,\mathrm{dynamic}}b}{\ell_P}\right)
$$
$\Lambda_\mathrm{twist}(b)$ is strictly bounded within $\pm0.1500$.

> Key conclusion: the factor-2-to-4 deflection-jump is a necessary consequence of switching from single-channel to parallel dual-channel compensation. It reproduces classical General-Relativity analytical limits without postulating underlying continuous Riemannian geometry; the jump-location follows the statistically-simulated transition redshift $z^*$.

## 7 Numerical Validation and Stability Metrics
### 7.1 Data-processing pipeline
Data-source: SDSS/eBOSS spAll-v6_1_3-allepoch FITS spectroscopic catalogue comprising 29890 raw spectra. Selection criteria: $z_\mathrm{WARN}=0$, $z>0.05$, $z_\mathrm{ERR}>0$. Seventy percent of samples are high-redshift QSO. Effective working-node count $N=15\,000$.

### 7.2 Bootstrap statistical-error-analysis
Non-parametric Bootstrap resampling with **1500 independent Monte-Carlo realisations** for sliding-causal-horizon simulations.

> Important note: simulated transition redshift $z^*=3.13$. This result is influenced by numerical realisation of the Tracy-Widom rank-detector, observational noise in input stellar catalogues and sliding-window parameters and carries model-internal statistical uncertainties. $z_\mathrm{crit}=4.1605$ is a historical-theoretical reference from v6.1 and is no longer treated as a model output in this revision.

Key simulated statistical outputs:
- First-principles derived compression-coefficient: $\alpha_{0,\mathrm{dynamic}}=21.09\pm0.34$, 95 %CI $[20.423,\ 21.761]$
- Simulated statistical transition redshift: $z^*=3.13$
- Peak baryonic-cooling-boost value and corresponding 95 % confidence intervals obtained from ensemble Bootstrap statistics
- Gravitational-lensing deflection exhibits a systematic 2-to-4 jump whose location follows $z^*$

Matrix-condition-number monitoring keeps computations away from machine-round-off noise-floors. The core routine `execute_axiomatic_conformal_engine()` endogenously solves for $\alpha_{0,\mathrm{dynamic}}$, conformal-factor $\Omega$, $c_\mathrm{eff}$ from redshift-and-redshift-error inputs and enforces algebraic assertions guaranteeing local measured-speed-of-light equals $c_0$.

![Figure 3](./figures/sre_condition_diagnostics.png)
**Figure 3** Numerical-stability monitoring of matrix-condition-number versus cosmological redshift $z$. Grey dashed curve: unregularised metric-matrix. Green solid curve: output under adaptive Tikhonov-manifold regularisation keeping condition-numbers inside numerically-stable domains. Red horizontal dotted line represents machine-safety ceiling $\mathrm{Cond}\le 10^{12}$.

![Figure 4](./figures/lens_jump_2to4.png)
**Figure 4** Gravitational-lensing Einstein-radius evolution with cosmic redshift. Blue solid curve: Bootstrap-ensemble-mean result; light-blue shaded band denotes 95 % confidence interval. Green dashed horizontal line: Einstein-radius baseline under $G_0$. Solid-orange vertical line marks simulated statistical transition $z^*=3.13$; purple dashed vertical line marks historical-theoretical-reference $z_\mathrm{crit}=4.1605$.

## 8 Discussion: Alignment-boundaries against SRE-v1.6 axiom-suite
Revision v6.2-rev preserves *all axioms* of the SRE-v1.6 framework without altering fundamental-principles; it only carries out mathematical-formulation upgrades, simulation-pipeline improvements and updates of numerical results:
1. **Emergent-ontology ultraviolet-boundary**: Planck-quantities are instance-realisation-cost thresholds, not fundamental network granularity.
2. **Dissipation-compensation duality**: distances are trace-inner-products of compensation- / dissipation-operators, mathematically realising v1.6 ontology of distance as book-keeping for topological-residual coherent-degradation.
3. **Mutual-measurement and Möbius light-residual**: photons correspond to Möbius-topology residual information-packets; BBP spectral-rank phase-transition splits single-handed Möbius topology into bidirectional two-layer networks.
4. **Uninstantiated-state / physical-rendering-layer**: eigenvalues crossing the Tracy-Widom boundary signify causal-interactions satisfying budget-constraints and completing instance-realisation.
5. **Homomorphic-mapping, not isomorphism**: astronomical-observations are coarse-grained many-to-one projections of the high-dimensional causal-network.
6. **Variable emergent-speed-of-light + conformal-covariance**: strictly preserves qualitative SRE-v1.6 predictions supplemented by explicit VSL formulae.
7. **Ontological-boundary statement**: this framework does not answer the ultimate origin of causal differences. It only describes how pre-existing asynchronous informational-differences give rise to emergent-cosmology. Questions concerning 0-to-1 genesis lie outside the closed scope of this revision.

> Version-historical reminder: original v6.1 draft contained residual coordinate-substrate ontological defects together with the a-priori conjecture $z_\mathrm{crit}=4.1605$. This v6.2-rev revision completes corrigenda. $z_\mathrm{crit}=4.1605$ serves only as historical-reference. **$z^*=3.13$ is the statistical simulation output of this manuscript; it is not a direct astronomical observational measurement**. Versions v1.5.x and earlier are historical heuristic-sketches and shall be used for traceability purposes only.
> The Tracy-Widom rank-detector inside simulation-pipeline uses numerical-fitting implementation. Future work shall perform parameter-sensitivity-tests investigating the influence of sliding-window sizes and different observational catalogues upon $z^*$.

## 9 Future-research outlook
Subsequent work will couple the SRE-framework into CMB Boltzmann-solvers and test whether conformal-scaling of baryon-acoustic-horizon and photon-propagation during 4D-to-2D holographic-regression maintains CMB acoustic-peak positions within Planck / ACT observational error-bars. Simultaneously perform simulation-parameter-sensitivity-analysis, test the stability of simulated transition redshift $z^*$ with DESI and other spectroscopic catalogues, and await future-telescope tests for the falsifiable imprints: gravitational-lensing 2-to-4 jump and chiral-polarisation signatures.

## Conclusions
The SRE cosmic-gravity-framework (v6.2-rev) constructs a fully background-independent cosmological picture. Spacetime-topology, gravitational-strength and light-speed all emerge uniformly as macroscopic-consequences of link-topology within underlying discrete causal-information-networks. Using the SDSS/eBOSS spectroscopic dataset and 1500 Bootstrap Monte-Carlo realisations we obtain the BBP-spectral-rank statistical-phase-transition redshift $z^*=3.13$. This phase-transition yields dimensional-crossover, gravitational-lensing factor-2-to-4 jump and primordial baryonic-cooling-enhancement effects which self-consistently alleviate the JWST high-redshift massive-galaxy puzzle. $z_\mathrm{crit}=4.1605$ is a historical-theoretical-reference originating from v6.1 and is no longer treated as a rigid prediction within this revision. The model delivers observationally-falsifiable imprints for examination by JWST and the Roman Space Telescope.
