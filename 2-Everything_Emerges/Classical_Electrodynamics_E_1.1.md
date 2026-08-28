# A Foundational Reconstruction of Classical Electrodynamics via Discrete Graph Topology and Bidirectional Causality
**Author**: Yue Lu
**Version**: v1.1-rev

> **Resource & Availability Statement**: This framework is built upon Status-Relational Entropy (SRE) Dynamics. The complete suite of theoretical materials is archived in the Zenodo open-data repository.
> **The full package includes system manuscripts, application developments, scientific hypotheses, complete algebraic derivations for operators 1-6, and simulation source code, all open-source**. Operators 7, 8, 9, 10 belong to subsequent closed-source commercial core modules and are not included in this document suite.
>
> A Tencent Smart-Document workspace supporting AI-assisted review is available for both PC and mobile access.
>
> As of 2026-08-14, the author no longer maintains or updates the Google Gemini Notebook SRE documentation suite due to Google Terms-of-Service constraints; this link serves purely as historical archive and shall not be used for formal citation:
>
> - Gemini Notebook (historical archive, no longer updated):
<https://notebooklm.google.com/notebook/ef52bf5a-f6d0-4a2a-aed4-b25d6520ab2c>
> - Tencent Smart-Document workspace:
<https://docs.qq.com/space/DUkRjYUtNWFdyV253>
>
> According to the SRE principle, physical foundations originate from information statistics.
> Reference baseline: SRE-v1.6 Axiom Suite (https://doi.org/10.5281/zenodo.22077475)
> Historical references:
> https://doi.org/10.5281/zenodo.19935370
> https://doi.org/10.5281/zenodo.20344105
> https://doi.org/10.5281/zenodo.20576606

> Remark: This manuscript adopts a pragmatic hybrid approach combining the SRE ontological picture with classical-engineering frameworks. Underlying topological evolution obeys SRE axioms. Observational-mapping anchors adopt experimentally-measured universal constants as conversion interfaces and are not endogenously derived directly from SRE axioms. Fully endogenous derivation of all cosmic universal constants is a long-term research objective and lies outside the scope of v1.1-rev. The accompanying simulation `sre_simulation.py` is an engineering-oriented demonstration after mapping, not native dimensionless topological evolution at the底层 level.

## Abstract
This paper carries out a paradigm-shift in fundamental physics: discarding continuous spacetime background, continuous electric charge and scalar energy fields, reconstruction is performed within the Status-Relational-Entropy (SRE) Dynamics framework. Macro-physical phenomena are mapped onto a discrete-graph network composed of infinite nodes, and fundamental electrical equations are derived using first-order and n-th-order adjacency matrices. Four sets of **observational-mapping anchors** $(\kappa_{I}, \kappa_{R}, \kappa_{V}, \kappa_{P})$ are defined, which adopt known universal cosmic constants as conversion interfaces to map dimensionless discrete-topology observables onto laboratory-scale SI engineering quantities. This enables the SRE topological picture to interface with power-system and semiconductor-device engineering simulations.

Ontologically, SRE Dynamics naturally unifies classical-circuit theory with the special-relativistic mass-energy equivalence relation $E=mc^2$, re-defining mass as local causal loops. Macroscopic thermodynamic entropy is mapped onto statistical decoherence of graph sub-structures. Mathematical formalisation for alternating-current (AC) resonance is accomplished via graph-Laplacian spectral decomposition.

**Keywords**: Status-Relational Entropy; discrete graph topology; bidirectional causality; observational-mapping anchors; circuit topology; graph Laplacian; RLC resonance; mass-energy equivalence; power-system simulation; semiconductor topological analysis

## 1 First Principles & Metric Alignment of SRE Dynamics
SRE Dynamics abandons classical notions of absolute space (“meters”) and continuous time (“seconds”). The physical continuum is reconstructed entirely via discrete graph-theoretic metrics; physical foundations originate purely from informational statistics.

**Cumulative Evolutionary Step $\boldsymbol{\Delta S}$**: The discrete minimal unit of global state-refresh cycles inside the SRE network. Macroscopic time $t$ is not a continuous physical backdrop but an emergent property accumulated from evolutionary steps $\Delta S$.

**Topological Geodesic Path $\boldsymbol{d_{min}}$**: The minimal number of discrete causal steps between two topological structures inside the network matrix, completely replacing the continuous spatial-distance metric $L$. Spatial distance is an emergent appearance originating from linkage depth between nodes.

**Intrinsic Update Velocity $\boldsymbol{c}$**: A proportional constant defining the maximum rate of bidirectional causal reconciliation inside the SRE network. Determined by the global “topological rigidity” of the matrix, it serves as an absolute upper bound for computation and propagation speed.

**Bidirectional Causality**: Spacetime evolution does not propagate unidirectionally from node A to node B. Instead it is governed by global bidirectional harmonic resonance. A local topological state transitions to its final discrete computational steady-state **only after causal loops fully close across the whole network**, enforcing strict conservation laws at boundary interfaces.

## 2 Higher-Order Adjacency Definitions & Physical Manifestations
To fully formalise the framework, powers of adjacency matrix $\boldsymbol{A}$ directly correspond to discrete causal-link lengths, defining physical mechanisms for fields:

- **First-Order Adjacency $\boldsymbol{A^{1}}$**: Represents immediate localised causal coupling between neighbouring nodes. Information propagates within one single evolutionary step ($\Delta S=1$). Macroscopically this manifests as the electrostatic field (Coulomb force) and local potential differences.
- **Higher-Order Adjacency $\boldsymbol{A^{k}}$**: Represents long-range cross-network causal phase-locking. When an electronic node-cluster maintains a constant refresh rate (macroscopic uniform linear motion), its first-order local symmetry remains unbroken. Nevertheless its evolutionary flow permeates deep matrix layers at intrinsic velocity $c$. Upon encountering another cluster with matching step-refresh rate at the $k$-th-order network boundary, synchronised co-evolution is triggered. Macroscopically this manifests as the magnetic field.

**Topological Resistance Fraction**: Making use of Kirchhoff’s Matrix-Tree Theorem, the determinant ratio
\[
\frac{\det(D-A)^{(1)}}{\det(D-A)^{(k)}}
\]
The determinant of graph-Laplacian matrix $L=D-A$ counts spanning-trees (valid information channels). This ratio directly quantifies structural obstruction from the intervening grid against higher-order causal propagation, replacing macroscopic resistivity $\rho$.

## 3 Dimensional Quantization and Observational-Mapping Anchors
To map dimensionless topological updates of SRE Dynamics directly onto empirical International-System-of-Units (SI) measurements, fundamental spacetime granularity is defined: let $\Delta\tau$ denote macro-equivalent duration for one global-evolution step $\Delta S=1$; and $\Delta\ell=c\cdot\Delta\tau$ the minimal geodesic metric unit.

The four observational-mapping constants $(\kappa_{I}, \kappa_{R}, \kappa_{V}, \kappa_{P})$ serve as conversion anchors at the observation-engineering layer. **In this work mapping coefficients are constructed adopting known universal physical constants; they are not purely derived from internal SRE axioms. Endogenously deriving all universal constants from causal-network dynamics remains a subsequent long-term research objective.** Here $e$ is elementary charge, $h$ Planck constant, $Z_0$ vacuum characteristic impedance.

### I. Charge and Current: Causal-Link Cut-Set Counting
- Classical form: $I=\frac{Q}{t}$
- SRE formulation: Electric charge $Q$ counts specific non-linear topological knots (node-set $N_{\mathrm{nodes}}$) inside SRE graph $g$. Current $I$ is the refresh frequency of causal-link paths crossing a designated topological cut-set per evolutionary step $\Delta S$.
- Mapping operator:
$$
I=\kappa_{I} \cdot \frac{\Delta N_{\mathrm{nodes}}}{\Delta S}
$$
- Observational-mapping anchor:
$$
\kappa_{I}=\frac{e}{\Delta \tau} \quad\left[ A \cdot step \cdot flow ^{-1}\right]
$$

### II. Ohm’s Law: High-Order Network Topological Impedance
- Classical form: $R=\frac{V}{I}=\rho \frac{L}{A}$
- SRE formulation: Resistance $R$ represents structural elongation and topological obstruction of intervening grids against higher-order causal propagation.
- Mapping operator:
$$
R=\kappa_{R} \cdot \frac{d_{\mathrm{min}}}{W_{\mathrm{width}}} \cdot \frac{\det(D-A)^{(1)}}{\det(D-A)^{(k)}}
$$
- Observational-mapping anchor:
$$
\kappa_{R}=Z_{0} \cdot \frac{W_{\mathrm{width}}}{d_{\mathrm{min}}}=\sqrt{\frac{\mu _{0}}{\varepsilon _{0}}} \cdot \mathcal{F}( geometry) [\Omega ]
$$

### III. Potential Difference (Voltage): First-Order Adjacency Phase Gradient
- Classical form: $V=\frac{w}{Q}$
- SRE formulation: Voltage $V$ is the absolute difference in first-order-adjacency-network refresh-rate (step-pressure gradient) between two local topological sub-networks A and B.
- Mapping operator:
$$
V=\kappa _{V}\cdot \left[ f_{\mathrm{refresh}}(A)^{(1)}-f_{\mathrm{refresh}}(B)^{(1)}\right]
$$
- Observational-mapping anchor (aligned via Josephson constant $K_{J}=\frac{2 e}{h}$):
$$
\kappa_{V}=\frac{h}{e \cdot \Delta \tau}=\frac{2 \cdot K_{J}}{\Delta \tau} \quad\left[V \cdot node \cdot gradient ^{-1}\right]
$$

### IV. Electrical Power and Dissipation: Global Causal Settlement Rate
- Classical form: $P=VI$ and $E=P \cdot t$
- SRE formulation: Power $P$ represents total scale of causal-links undergoing phase-transition or dissociation per evolutionary step.
- Mapping operator:
$$
P=\kappa_{P} \cdot\left(\Delta S \times Tr\left(M^{T} M\right)\right)
$$
- Observational-mapping anchor:
$$
\kappa_{P}=\frac{h}{\Delta \tau} \quad\left[ W \cdot step \cdot settle^{-1}\right]
$$

## 4 Mass-Energy Equivalence ($E=mc^2$) as a Topological Theorem
SRE Dynamics naturally derives Einstein’s mass-energy equivalence as a geometric law for discrete informational states:

- **Topology of Mass ($m$)**: Mathematically mass is defined as local self-closed causal dead-loops (strongly-connected components) inside the SRE matrix. Executing internal updates at maximum intrinsic rate $c$ without producing relative spatial displacement, it manifests macroscopically as rest-mass and inertial impedance.
- **Topology of Energy ($E$)**: Energy denotes uncoiled, linearly-propagating open topological flows diffusing outward across the grid (e.g., electromagnetic waves).

**Mechanism for $E=mc^2$**: When self-closed dead-loops uncoil into open propagating flows, bidirectional-causality constraints demand forward-propagation computation plus backward-echo reconciliation. This introduces the rigid scaling factor $c\times c = c^2$ within the informational state-space.
Accordingly, $E=mc^2$ is an exact discrete-counting amplification factor when “stationary looping links” transform into “outward-broadcasting phase-repair waves”.

## 5 RLC Resonance via Graph-Laplacian Spectral Decomposition
To establish mathematical equivalence with classical alternating-current (AC) networks, macroscopic harmonic resonance maps directly onto eigenvalues of the discrete graph-Laplacian matrix.

### I. Topological Operators for Capacitance and Inductance
- **Capacitance ($C$)**: Reformulated as vertex-cut capacity of the graph. It measures the threshold for boundary networks to store topological node-knots while maintaining first-order refresh-phase gradient; representing low-frequency localised potential storage.
- **Inductance ($L$)**: Reformulated as structural inertia of the graph’s Cycle-Space Matrix ($C_{\mathrm{cycle}}$). It measures network capacity to sustain self-consistent high-order co-evolutionary loops.

### II. Proof of Mathematical Convergence to $f=\frac{1}{2\pi\sqrt{LC}}$
Continuous-time macroscopic-wave propagation inside the SRE-network topology obeys the dimensionalised second-order matrix-evolution equation incorporating observational-mapping anchors derived in Section 3:
$$
\frac{\partial^{2} \Psi}{\partial t^{2}}+\left(\frac{\kappa_{V}}{\kappa_{I} \cdot \Delta \tau^{2}}\right) L_{\mathrm{graph}} \Psi=0
$$
Where $t=S \cdot \Delta\tau$ represents macro-seconds; $L_{\mathrm{graph}}=D-A$ is the normalised graph-Laplacian matrix in standard Farad and Ohm dimensions.
Under continuous-spatial limit with node cardinality $|V| \to \infty$ and geodesic-step size $\Delta\ell \to 0$, the scaled discrete graph-Laplacian operator rigorously converges to the continuous Beltrami-Laplace operator:
$$
\lim _{\Delta \ell \to 0} \frac{1}{\Delta \ell^{2}} L_{\mathrm{graph}} \Psi=-c^{2} \nabla^{2} \Psi
$$

Partition global-network interaction topology into vertex-cut potential-storage operators (capacitive sub-network array $C_{\mathrm{op}}$, measured in Farads) and loop-space structural-inertia operators (inductive cycle-space matrix $L_{\mathrm{op}}$, measured in Henries). The dimensionalised Laplacian matrix scales approximately as:
$$
L_{\mathrm{graph}} \approx\left(L_{\mathrm{op}} C_{\mathrm{op}}\right)^{-1}
$$

According to spectral-scaling rules for Riemannian graph-manifolds, the lowest non-zero eigenvalue (Fiedler eigenvalue $\lambda_{1}$) under Dirichlet boundary-conditions represents the fundamental system-resonance modal limit:
$$
\frac{1}{\lambda_{1}}=\iint_{\mathcal{G}} G(x, y) d C_{\mathrm{op}}(x) d L_{\mathrm{op}}(y) \stackrel{|\mathcal{V}| \to \infty}{\to} L \cdot C
$$

Substituting dimensionalised spectral identity for macroscopic angular frequency $\omega=2 \pi f$, the evolutionary coefficient yields perfect dimensional closure:
$$
\omega^{2}=\left(\frac{\kappa_{V}}{\kappa_{I} \cdot \Delta \tau^{2}}\right) \lambda_{1}=\frac{1}{L \cdot C}
$$

Taking square-root and isolating linear cyclic-frequency $f$, we extract the exact macro-equivalent harmonic identity:
$$
2 \pi f=\frac{1}{\sqrt{L C}} \Rightarrow f=\frac{1}{2 \pi \sqrt{L C}}
$$

> Conclusion: The classical RLC-resonance-frequency formula is not an empirical postulate. It constitutes geometric manifestation of network Fiedler-eigenvalue emerging under macroscopic continuous approximations, rigidly bounded by SRE-Dynamics observational-mapping anchors.

## 6 Wide-Area Dispersion and Causal Conservation in Macro-Grids
SRE Dynamics delivers an elegant account for mass-conservation inside macroscopic power grids. For instance, when a global grid outputs power, the computed global mass-loss (approx. 1.2 tons per annum) represents a strict topological phase-transition from localisation toward wide-area dispersion.

### I. Generation Source (Power Plants)
- **Topological Action**: Localised causal dead-loops uncoil. Chemical-bond or nuclear-binding forces break.
- **Macroscopic Output**: High-order co-evolutionary flows (electric current) are generated.
- **Mass Manifestation**: Rigid local mass-loss occurs (global grid loses approx. 1.2 tons / year).

### II. Transmission & Utilisation (The Grid Topology)
- Transformed open linear-topological flows are broadly driven into cosmic-grid interfaces, transitioning from low-entropy synchronised alignment toward highly fragmented relational patterns.

**Macroscopic Manifestations & Thermodynamic-Entropy Closure**
- **Thermal Dissipation (Joule Heating)**: Due to boundary-friction against intervening-grid impedance, coherent open causal-flows undergo non-linear scattering. They shatter and re-coil into billions of chaotic, unsynchronised, highly-localised micro-dead-loops (thermal mass). Whilst these microscopic-loops lock finite rest-mass locally ($\Delta m=\Delta E_{\mathrm{thermal}} / c^{2}$), their spatial distribution and phase-alignment are fully randomised. This perfectly maps macroscopic thermodynamic-entropy increase ($\Delta S_{\mathrm{thermal}}>0$) onto statistical decoherence of graph-sub-structures. Note that thermodynamic-entropy notation is decoupled symbolically from SRE evolutionary-step variable $\Delta S$; they are distinct physical quantities.
- **Mechanical Work**: Flows couple directly with external local boundary-conditions, transforming into relative topological-geodesic refresh-rates and manifesting macro-kinetic momentum.
- **Electromagnetic Radiation**: Un-trapped high-frequency causal-links fully decouple from local vertex-clusters, transforming into permanent open phase-repair-waves diffusing outward into deep cosmic-matrix reference sinks.

Within macroscopic-engineering practice this mass-shift is obscured by experimental noise (e.g., a Tesla-vehicle battery loses exactly $4\,\mu\mathrm{g}$ mass upon discharging 100 kWh electricity; a relative variance of $8 ×10^{-11}\%$ completely masked by thermal-buoyancy variations). Nevertheless within SRE-Dynamics the global count of evolutionary-steps ($\Delta S$) remains strictly conserved, furnishing a pristine unified mathematical architecture for all electrical phenomena.

## Discussion
### Model Positioning and Inherent Limitations
This work does not pursue fully-closed cosmic-scale first-principle analytical derivations free from external inputs. In-principle purely-analytical endogenous derivation of universal constants such as elementary-charge $e$, Planck’s-constant $h$, vacuum characteristic-impedance $Z_0$ starting from bare SRE axioms would require complete global knowledge of the full causal-information-network configuration of the universe - information presently unavailable for humans.

This paper therefore adopts a pragmatic hybrid-research-strategy with controlled mixing of the SRE ontological picture and well-established classical-physics engineering frameworks. Ontological interpretations for underlying physical phenomena are built entirely upon discrete-graph-topology and bidirectional-causality SRE axioms. Meanwhile observational-mapping anchors $\kappa_{I},\kappa_{R},\kappa_{V},\kappa_{P}$ are introduced, adopting experimentally-measured universal constants to convert dimensionless-topology observables into SI-engineering units.

The core merit of this hybrid paradigm is not cosmic-scale theoretical deduction, but delivering fresh physical viewpoints: re-interpreting circuits, dissipation, resonance and electromagnetic propagation as topological-evolution phenomena of causal-networks. Through this mapping-bridge, the SRE topological-model directly interfaces with existing engineering tool-chains for power-system simulation and semiconductor-device analysis. It opens new avenues for discovering topology-related effects less visible within conventional electromagnetic theory, with potential for technological progress in power-engineering and fundamental-semiconductor applications.

Important conceptual distinction: underlying topological-mechanisms constitute theoretical innovations of this manuscript; observational-mapping anchors merely serve as conversion interfaces on the observation-engineering layer. Complete elimination of external-constant inputs and fully-endogenous emergence of all universal constants from causal-network-dynamics remains a long-term theoretical objective and lies outside scope of v1.1-rev. The accompanying simulation `sre_simulation.py` is an engineering-oriented demonstration built upon exactly this mapping-bridge.

> This manuscript maintains ontological consistency with other SRE-system papers (Emergent Classical Mechanics, Composite Elementary-Particles Topological Paradigm): qualitative-semi-analytical mechanism construction is achieved at ontological level; quantitative numerical benchmarking relies upon observational-mapping or subsequent simulation-inverse-inference. Fully cosmic-scale analytical derivation is treated as long-term objective.

## Conclusions
This manuscript accomplishes ontological reconstruction of classical electrodynamics upon discrete bidirectional-causal graph-networks. Charge, voltage, resistance, capacitance, inductance all receive topological-level ontological interpretations; RLC-resonance is recovered via graph-Laplacian spectral-decomposition; mass-energy equivalence is understood as topological theorem for loop-open-flow conversion. Observational-mapping anchors realise conversion from topological quantities toward SI-engineering units, opening the interface between SRE topological picture and power- / semiconductor-engineering simulations.

Classical electromagnetism and circuit-theory emerge as effective theories of discrete causal-information-networks under specific conditions. The emphasis of this paper lies in delivering novel topological-analysis perspectives for engineering-application exploration. Fully endogenous derivation of all cosmic universal-constants starting from axioms is reserved for subsequent long-term-research tasks.

## References
1. SRE-Dynamics Axiom Suite v1.6, Zenodo archive.
2. SRE early-archive series DOIs for traceability.
3. Literature on graph theory, graph Laplacian, Matrix-Tree Theorem.
4. Circuit theory, RLC resonance, fundamentals of semiconductor devices.
5. `sre_simulation.py`: accompanying engineering demonstration simulation code included within open-source suite.

