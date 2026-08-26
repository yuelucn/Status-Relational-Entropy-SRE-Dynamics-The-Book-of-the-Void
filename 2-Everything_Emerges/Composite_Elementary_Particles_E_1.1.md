# A SRE‑Dynamics Inspired Topological Paradigm for Composite Elementary Particles and Relational Space Emergence
**Author**: Yue Lu
**Version**: v1.1‑rev

> **Resource & Availability Statement**: This framework is built upon Status‑Relational Entropy (SRE) Dynamics. The complete suite of theoretical materials is archived in the Zenodo open‑data repository.
> **The full package includes system manuscripts, application developments, scientific hypotheses, complete algebraic derivations for operators 1‑6, and simulation source code, all open‑source**. Operators 7, 8, 9, 10 belong to subsequent closed‑source commercial core modules and are not included in this document suite.
>
> A Tencent Smart‑Document workspace supporting AI‑assisted review is available for both PC and mobile access.
>
> As of 2026‑08‑14, the author no longer maintains or updates the Google Gemini Notebook SRE documentation suite due to Google Terms‑of‑Service constraints; this link serves purely as historical archive and shall not be used for formal citation:
>
> - Gemini Notebook (historical archive, no longer updated):
<https://notebooklm.google.com/notebook/ef52bf5a‑f6d0‑4a2a‑aed4‑b25d6520ab2c>
> - Tencent Smart‑Document workspace:
<https://docs.qq.com/space/DUkRjYUtNWFdyV253>
>
> According to the SRE principle, physical foundations originate from information statistics.
> Reference baseline: SRE‑v1.6 Axiom Suite (https://doi.org/10.5281/zenodo.22077475)
> Historical references: earlier SRE archive DOIs retained for traceability.

> Remark: This is a qualitative‑semi‑analytical topological hypothesis. Large‑scale multi‑degree‑of‑freedom numerical simulation and quantitative benchmarking against lattice‑QCD are left for future follow‑up research.
> Ontological narrative note: The underlying physical driving force comes from the dissipation‑compensation duality dynamics of SRE. The cross‑spectral Hermitian matrix, coherence coefficient, condition number and related quantities are **statistical characterisation tools describing underlying dynamical behaviour, not ontological primitive operators generating physical effects**. The original v1.0 manuscript contained causal inversion in narrative; this revised v1.1‑rev version corrects the ontological causal hierarchy while keeping all mathematical formulas unchanged.

## Abstract
Within the conceptual framework of Status‑Relational‑Entropy (SRE) Dynamics, this paper presents a qualitative‑probabilistic formulation for the topological configuration and emergent geometry of composite elementary particles. Traditional physical paradigms rely heavily on fine‑tuned continuous variables and empirical constants to explain rest‑mass amplification and strong‑interaction effects in composite structures. This work strips away all a‑priori assumptions of absolute time, space and energy; space is de‑indexed and reformulated as a macroscopic geometric manifestation of status‑relational entropy and phase coherence among distinct causal chains.

The underlying physical process is driven by **dissipation‑compensation duality dynamics** of bidirectional Möbius causal loops. Coupled evolution of two internal causal‑loops modifies mutual‑information and phase‑coherence between them. The 2×2 local cross‑spectral Hermitian operator is a characterisation tool obtained by statistical smoothing over dynamical output time‑series, capturing spectral‑evolution features of the system. When the cross‑coherence coefficient (at the representational level) asymptotically approaches unity, it corresponds to underlying dynamical saturation of phase coherence. The dimensionless eigenvalue‑spacing of the ensemble spontaneously undergoes a distribution transition from the Wigner Surmise toward a continuous Poisson process. Within the full‑rank expanded spectral regime, three‑in‑one co‑emergent phenomena appear at the macroscopic rendering‑layer: relational distance collapses toward zero due to maximised mutual information; the matrix condition‑number hits numerical truncation thresholds, characterising an abrupt logical‑pressure gradient rendered macroscopically as the strong‑interaction force; instantaneous residual resonance triggers non‑linear combinatorial explosion of secondary causal‑feedback paths.

Free‑parameter tuning and pre‑existing background geometry are not required. This paradigm achieves self‑consistent mathematical unification of composite‑particle physics and relational metric space. Spectral‑matrix constructions serve purely as statistical‑analytical representations; the first‑principle physical origin resides in dissipation‑compensation duality evolution of the causal‑information network.

> <sup>†</sup>Note: In early manuscripts this fundamental resolution parameter was denoted Minimum Observational Step $\ell_{\mathrm{min}}$. Within the SRE‑v1.6 axiom suite it is standardised as the **global evolution step $\boldsymbol{\Delta S}$**, representing the fundamental discrete state‑refresh cycle of the causal network.

**Keywords**: Status‑Relational Entropy; internal causal loops; composite elementary particles; relational space; dissipation‑compensation duality; cross‑spectral Hermitian operator; coherence saturation; gluon‑sea‑like mass amplification; strong interaction; Wigner‑Poisson spectral‑ensemble transition

## 1 Foundational Axioms: Single‑Parameter System and Non‑Background‑Dependent Relational Space
### 1.1 Single‑Parameter System and Local Counting of Time
The SRE architecture discards all macroscopic physical postulates. The rendered universe is derived from one single fundamental parameter — the **global evolution step $\boldsymbol{\Delta S}$**<sup>†</sup> — which defines the absolute resolution threshold for causal operations. Within this logical framework:

- Time is strictly defined as local sequential counting of internal state‑transitions within isolated causal chains, establishing a non‑global intrinsic time axis.
- Rest‑mass is neither an intrinsic material substance nor external computational overhead. It corresponds to topological depth and cumulative path‑counts of internal causal‑loops inside a node. When the global sorting protocol samples or attempts to displace a local node, it must fully traverse and process all internal feedback‑paths contained within that node. This intrinsic structural complexity of the discrete graph manifests as inertial mass at the emergent layer.

> <sup>†</sup>Note: In early manuscripts this fundamental resolution parameter was denoted Minimum Observational Step $\ell_{\mathrm{min}}$. Within the SRE‑v1.6 axiom suite it is standardised as the **global evolution step $\boldsymbol{\Delta S}$**, representing the fundamental discrete state‑refresh cycle of the causal network.

### 1.2 Relational‑Distance Space as a Probabilistic Emergent Outcome
This framework strictly rejects any absolute background grid or pre‑defined spatial coordinate indices (**non‑background‑dependent; no pre‑existing spacetime manifold**). Space is a purely derived construct: macroscopic geometric rendering of status‑relational entropy among decoupled causal chains.

The observed “relational distance” between two causal nodes at the macroscopic layer represents discrete information impedance and sequential step‑delay required for step‑size cross‑correction between nodes at the underlying protocol layer.

### 1.3 Local Cross‑Spectral Operator and Information‑Geometric Mapping
> Ontological remark: $X_{0}(t)$ and $X_{1}(t)$ are discrete complex time‑series samples output by underlying dissipation‑compensation duality dynamics. The 2×2 local complex cross‑spectral Hermitian matrix $\boldsymbol{M}$ below is a **statistical characterisation matrix** obtained by local statistical smoothing over dynamical outputs. It describes system‑evolution features and is not an ontological primitive operator generating physical phenomena.

Let $X_{0}(t)$ and $X_{1}(t)$ denote discrete complex response streams output by dynamical evolution of two underlying internal causal‑loops. Within the generalised spectral domain, local statistical smoothing over an iterative window yields the 2×2 local complex cross‑spectral Hermitian operator $\boldsymbol{M}$:

\[
M=\begin{pmatrix}
E\left[\left|X_{0}\right|^{2}\right] & E\left[X_{0} X_{1}^{*}\right] \\
E\left[X_{1} X_{0}^{*}\right] & E\left[\left|X_{1}\right|^{2}\right]
\end{pmatrix}
\]

The modulus of the non‑linear cross‑coherence term $\rho=|E[X_{0} X_{1}^{*}]| \in[0,1]$ serves as a characterisation quantity directly quantifying logical correlation density between two causal chains. Emergent macroscopic distance $D$ is not propagated from an external background; it is derived strictly from Shannon mutual‑information encoded within the local Hermitian‑matrix representation. Define shared status‑relational entropy between two loops as $I=-\ln (1-\rho^{2})$. Emergent geometric distance is inversely proportional to this shared logical density:

\[
D \propto \frac{1}{I}=\frac{1}{-\ln \left(1-\rho^{2}\right)}
\]

- When $\rho \to 0$, mutual‑information vanishes ($I\to0$), emergent distance $D\to\infty$. The two causal chains behave as fully decoupled, independent, infinitely separated particles.
- When underlying dissipation‑compensation duality dynamics drive causal‑loops toward phase‑coherence saturation — represented at the characterisation level by $\rho\to1$ — mutual‑information saturates toward $I\to\infty$ and forces emergent distance $D\to0$. Two causal‑loops spatially overlap completely. Physical “approach” or “contact” of particles is an emergent manifestation of relational‑metric‑space collapse following underlying causal‑network phase‑coherence saturation; $\rho$ is merely a spectral indicator for this physical process.

Using single‑pass first‑order closed‑form algebra, raw eigenvalue spacing $\Delta\lambda$ and local condition number $\kappa$ are extracted; both quantities are spectral characterisers of underlying dynamical behaviour:

\[
\Delta \lambda=\sqrt{\mathrm{Tr}(M)^{2}-4 \det(M)}
\]

\[
\kappa=\frac{\mathrm{Tr}(M)+\Delta \lambda}{\max \big(\mathrm{Tr}(M)-\Delta \lambda,\ \varepsilon\big)}
\]

> $\varepsilon=10^{-7}$<sup>\*</sup>
>
> <sup>\*</sup>Note: $\varepsilon=10^{-7}$ is purely a numerical regularisation cutoff for matrix‑computation pipelines. **It is not a fundamental physical constant of the underlying causal‑information network.**

## 2 Core Paradigm: Three‑in‑One Emergent Jump and Composite‑Particle Birth
> Ontological remark: Numerical change in $\rho$ does **not** drive underlying physics. Instead: **underlying bidirectional Möbius causal‑loops are driven toward phase‑coherence saturation by dissipation‑compensation duality dynamics**. This physical dynamical process manifests spectrally as $\rho\to1$, which in turn causes full‑rank expansion $\det(M)>0$ of the local cross‑spectral matrix $\boldsymbol{M}$, triggering radical redistribution inside the probabilistic feature‑space.

### 2.1 Spectral Transition from Wigner to Poisson Ensemble
Once a full‑rank coupled physical state is established by underlying dynamics, at the representational generalised spectral‑ensemble level, the dimensionless ensemble‑spacing metric $s=\frac{\Delta\lambda}{E[\Delta\lambda]}$ spontaneously transitions from isolated Wigner‑Surmise statistics to a continuous Poisson‑process: $P(s)=e^{-s}$ (valid for global sequentially‑sorted generalised spectral‑ensembles).

Under Poisson‑clustering ($P(s)\to1$ as $s\to0$), microscopic eigenvalue‑spacing compresses densely toward the centre. Algebraically the denominator term $\big(\mathrm{Tr}(M)-\Delta\lambda\big)$ is forced toward the numerical cutoff limit $\varepsilon=10^{-7}$. This phenomenon is the spectral representational signature of underlying causal‑network dynamics.

### 2.2 Three‑in‑One Co‑Emergence of Space, Force and Mass
Defining space as a relational emergent construct implies composite‑particle formation is an algebraic necessity of underlying causal‑network evolution. Under dissipation‑compensation‑driven phase‑coherence saturation (represented by $\rho\to1$), three inter‑connected phenomena spontaneously appear at the macroscopic layer:

1. **Relational spatial overlap ($D \to 0$)**: Underlying dissipation‑compensation dynamics produce cross‑coherence saturation and maximised mutual‑information. Macro‑geometric distance collapses toward zero at the representational level; two independent loops merge into a single local composite node possessing internal topology.
2. **Emergence of interaction force ($\kappa \to \infty$)**: Underlying causal information‑streams mutually modify and “chase” each other’s discrete step‑sizes, generating intense logical‑pressure gradients. This dynamical effect manifests spectrally as eigenvalue‑spectrum compression and multi‑order logarithmic spike of condition‑number $\kappa$, rendered macroscopically as the strong‑interaction force. No mechanical force constants are manually introduced.
3. **Rest‑mass amplification: combinatorial explosion of secondary causal‑feedback paths**: In isolation, a single causal‑loop processes only its intrinsic $2N$ steps. Within the underlying full‑rank‑coupled physical phase‑space, maintaining zero‑residual global‑protocol consensus across the unified node causes steps from loop $X_0$ to continuously trigger and cross‑correct states of $X_1$. This triggers combinatorial explosion of intertwined secondary causal‑feedback paths at the discrete‑graph layer.

Total cumulative loop‑steps and path‑depth of the composite entity transitions from linear summation toward high‑order graph‑ensemble mapping, exhibiting qualitative scaling bifurcation:

\[
\mathrm{Total\ Causal\ Paths} =\int_{0}^{\infty} \kappa(s) \cdot f(\text{Secondary Feedback Path Generations}) \cdot e^{-s} \,\mathrm{d}s
\]

> Note: This equation evaluates topological scaling‑bifurcation using spectral‑representational quantities; it is not a numerically‑fitted expression. Driven by condition‑number‑spike high‑frequency step‑correction near the cutoff boundary, the discrete causal‑graph undergoes structural phase‑transition with exponential complexity growth. It provides a self‑consistent, non‑fitted mathematical account for step‑wise non‑linear rest‑mass amplification observed upon sub‑loop binding.

## 3 Geometric Pruning of Internal Loops via Instantaneous Path Alignment
Static phase‑rotations of the complex Hermitian matrix $\boldsymbol{M}$ leave time‑averaged eigenvalues invariant; this is merely a mathematical property at the representational level. True system dynamics originate from evolution of underlying bidirectional causal‑loops. Instantaneous state‑trajectories within discrete statistical‑smoothing windows are strictly governed by phase‑locking‑alignment mechanisms intrinsic to the dual‑loop ontology. The macroscopic concept of parallel / anti‑parallel spin can thereby be fully decomposed into purely discrete graph‑path mechanisms:

1. **Anti‑phase alignment (opposite‑spin mode)**: Under discrete beats, Möbius residuals of the dual loops point in opposing directions within the complex plane. Underlying dynamics produce high‑frequency algebraic cancellation of instantaneous residuals prior to window‑smoothing, suppressing physical divergence and preventing representational‑matrix condition‑number from reaching critical divergence. Secondary‑feedback‑path generation remains stable and bounded, explaining why certain two‑loop configurations yield low‑order mass profiles.
2. **In‑phase alignment (parallel‑spin mode)**: Möbius residuals align symmetrically, triggering constructive phase‑resonance at the physical level. Severe full‑rank deformation of underlying loops occurs, forcing protocol‑layer high‑intensity local‑pruning functions $(1.0-\alpha e^{-s})$ at every beat to maintain topological closure. This triggers structural combinatorial explosion of secondary causal paths, manifesting as higher‑mass structural configurations.

## Discussion
The composite‑particle‑generation picture advanced in this paper constitutes a **qualitative‑semi‑analytical topological hypothesis via structural homomorphic analogy**. Homomorphic analogy means the model preserves core structural relations of underlying causal‑network coupling‑evolution, yet partial microscopic details may be lost when mapping onto real QCD hadron systems.

### Model Scope and Boundaries
1. **Achievable goals (mechanism level)**
Built upon SRE underlying dissipation‑compensation‑duality dynamics, this model delivers a conceptually self‑consistent mechanistic explanation: when two internal causal‑loops approach phase‑coherence saturation, combinatorial explosion of secondary causal‑feedback‑paths produces non‑linear amplification of rest‑mass. This topological picture addresses the physical mechanism: *why mass increases significantly upon binding*. It also delivers a unified ontological account for the co‑emergence of relational‑space collapse, strong‑interaction emergence, and spin phase‑alignment phenomena.

2. **Current limitations (quantitative level)**
> ⚠️ At present this model **cannot derive real‑world gluon‑sea mass‑amplification factors, absolute hadron‑mass values, nor precise baryon‑spectral mass‑splitting quantitative results**.
- The total‑causal‑paths integral shown above
\[
\mathrm{Total\ Causal\ Paths} =\int_{0}^{\infty} \kappa(s) \cdot f(\text{Secondary Feedback Path Generations}) \cdot e^{-s} \,\mathrm{d}s
\]
is a **qualitative formal expression characterising topological scaling bifurcation**, not a complete quantitative formula ready for direct GeV‑scale numerical evaluation.
- The 2×2 simplified cross‑spectral Hermitian operator represents a two‑loop toy‑model only. Real hadron‑systems are complex networks with huge numbers of coupled degrees‑of‑freedom; this model performs degree‑of‑freedom reduction. The homomorphic mapping preserves structural evolutionary logic, yet a complete quantitative conversion bridge between SRE topological quantities and QCD / lattice‑QCD observables has not yet been established.
- Neither $\kappa(s)$ nor the secondary‑feedback‑path‑generation function $f(\cdot)$ have been fully analytically determined from SRE‑v1.6 axioms. Calibration constants required for matching against experimental / lattice‑QCD datasets are absent. Therefore mass‑amplification factors for real‑world protons, neutrons and other hadrons cannot be output presently.

Further constrained by SRE axiom architecture: the framework prescribes only the global evolution‑step $\Delta S$ as minimal causal‑operation resolution limit, **but does not pre‑assign a fixed, precise underlying microscopic topological‑connectivity structure. Local sub‑graph connectivity configurations themselves are emergent outcomes of dissipation‑compensation‑duality dynamics and are not a‑priori axiomatic inputs.**

From this we obtain a robust qualitative mechanistic inference: when two sets of internal causal‑loops reach phase‑coherence saturation, combinatorial explosion of secondary causal‑feedback‑paths inevitably produces non‑linear mass‑surge for composite systems.

Nevertheless, the final total number of secondary feedback‑paths generated depends sensitively upon real‑time local topological‑details evolved by dynamics. Given there exists no pre‑specified fixed microscopic topology, the minimal‑resolution scale $\Delta S$ alone is insufficient to uniquely constrain path‑proliferation magnitude. Consequently purely from axioms alone, deterministic analytical derivation of unique mass‑amplification‑factors or absolute hadron‑masses is impossible.

This contrasts with lattice‑QCD: its numerical calculations rest upon pre‑defined fixed discrete lattices plus SU(3) gauge‑degree‑of‑freedom bases. Within the SRE picture topological connectivity itself is dynamical output rather than computational input. Progress toward quantitative outputs requires large‑scale network‑simulations allowing spontaneous emergence of local topology, followed by statistical extraction of observables; such work lies outside scope of this qualitative‑semi‑analytical mechanistic paper.

### Comparison with Quantum Chromodynamics (QCD / Lattice‑QCD)
It is instructive to compare against established quantum‑chromodynamics: the SU(3) gauge Lagrangian of QCD serves as its underlying axiom, yet no closed‑form analytical solution exists for the low‑energy confinement regime. Pure algebraic derivation yielding gluon‑sea mass‑amplification factors is unavailable numerically. Present‑day numerical hadron‑masses and gluon‑contribution fractions are outputs from large‑scale non‑perturbative lattice‑QCD simulations; these are **outputs of first‑principle numerical simulation rather than closed‑form analytical derivations**.

This SRE model operates at an ontological level more fundamental than QCD degrees‑of‑freedom. The 2‑loop toy‑model here delivers a qualitative‑semi‑analytical homomorphic picture revealing the mechanism: coupling‑phase‑coherence‑saturation triggers secondary‑feedback‑path‑explosion giving non‑linear rest‑mass amplification. The total‑causal‑paths integral is only a formal expression characterising topological scaling bifurcation. Secondary‑feedback‑generation $f(\cdot)$ and condition‑number function $\kappa(s)$ are not fully solved analytically from SRE‑v1.6 axioms. Therefore real‑world gluon‑sea mass‑amplification factors cannot be output at present. To achieve quantitative results in future requires large‑multi‑degree‑of‑freedom network‑simulation plus construction of complete quantitative‑mapping bridges between SRE topological quantities and QCD observables.

### Future direction: AI‑assisted inverse inference from sampled datasets
Even though pure forward analytical derivation of deterministic mass‑amplification factors cannot be achieved solely from SRE axioms, one post‑processing computational pathway remains open for future investigation: inverse‑problem identification via large‑sample datasets combined with machine‑learning / AI‑driven regression.

From inverse‑problem perspective: SRE‑v1.6 axioms define dynamical evolution rules (dissipation‑compensation duality, minimal resolution given by global evolution‑step $\Delta S$). However local topological‑connectivity is dynamical output instead of pre‑defined input, leaving degrees‑of‑freedom not uniquely locked by axioms alone.

If a large‑multi‑degree‑of‑freedom forward SRE causal‑network simulator is constructed in future, large batches of coupled‑loop system simulation‑samples can be generated, pairing underlying topological‑statistical‑features against emergent macroscopic observables. Real‑world observational samples from lattice‑QCD or experimental hadron‑spectra may also be incorporated. Based on this sample library, Bayesian inference, sparse‑system‑identification or physics‑informed‑machine‑learning can perform inverse inference: constraining secondary‑feedback‑generation function $f(\cdot)$ and condition‑number function $\kappa(s)$ from macroscopic observables, establishing effective mappings between topological statistics and hadronic observables.

Important distinction: this paradigm **is not equivalent to pure axiomatic first‑principle analytical derivation**. Axioms supply dynamical rules, yet sample datasets play an essential role constraining degenerate solution‑space. This inverse‑problem intrinsically carries risks of solution‑degeneracy: distinct underlying topological‑configurations may yield similar macroscopic observables. Strong SRE ontological priors must be embedded to shrink degenerate solution‑space. Prediction performance also strongly depends upon completeness of sample‑configuration‑coverage; extrapolation toward unseen novel configurations carries failure‑risk.

In summary: AI‑sample‑driven inverse identification represents a promising future computational pathway; it is outside scope of this manuscript. This paper only elaborates the qualitative‑semi‑analytical mechanism that phase‑coherence‑saturation yields non‑linear mass‑surge.

### Follow‑up research roadmap
To move beyond homomorphic‑analogy‑only mechanism description three follow‑up tasks are required:
1. Extend the 2‑loop toy‑model toward large‑multi‑degree‑of‑freedom causal‑network simulation, escaping two‑body simplifying assumptions.
2. Build complete mapping rules converting SRE topological quantities (path‑counts, condition‑numbers, feedback‑path proliferation) into QCD observables (energy‑momentum‑tensor, hadron rest‑masses).
3. Calibrate against public lattice‑QCD datasets to determine concrete functional forms for $f(\cdot)$ and other unknown functions, enabling predictions for real‑world mass‑amplification‑factors and hadron‑spectra.

Until completion of above tasks, all results within this paper shall be strictly confined to **qualitative‑semi‑analytical ontological‑mechanism discussion; no numerical predictions for hadron‑masses are made**.

## Conclusions
As pointed‑out within the Discussion section, the present paradigm is a qualitative‑semi‑analytical topological picture via structural homomorphic analogy. It can reveal internal mechanisms for composite‑particle formation but cannot output quantitative physical values such as real‑world gluon‑sea mass‑amplification‑factors.

This formulation advances SRE Dynamics toward a fully non‑background, loop‑intrinsic paradigm. The structural validity of composite elementary particles is no longer an isolated question of material composition. Instead it emerges as a unified probabilistic outcome: driven by dissipation‑compensation‑duality of underlying bidirectional Möbius causal‑networks reaching phase‑coherence‑saturation, giving co‑occurrence of relational‑space collapse, interaction‑force manifestation and secondary‑loop‑path proliferation.

Cross‑spectral matrices, condition‑numbers and coherence‑coefficients are merely statistical‑characterisation and analytical tools for describing this evolutionary process. **Fundamental physical properties of composite particles are rigid inevitable outcomes of dissipation‑compensation‑duality dynamics of the underlying causal‑information‑network; they are not produced by matrix‑operators themselves.** This mathematical model frees itself from empirical physical constraints and fixed spacetime backgrounds.

> Supplementary remark: This manuscript delivers qualitative‑semi‑analytical topological insight for gluon‑sea‑like mass‑amplification inside composite‑particles. Full quantitative numerical validation against hadron‑spectra is reserved for follow‑up research.

## References
1. SRE‑Dynamics Axiom Suite v1.6, Zenodo archive.
2. SRE early‑archive series DOIs for traceability.
3. Lattice QCD: research on gluon‑sea mass‑generation inside hadrons.
