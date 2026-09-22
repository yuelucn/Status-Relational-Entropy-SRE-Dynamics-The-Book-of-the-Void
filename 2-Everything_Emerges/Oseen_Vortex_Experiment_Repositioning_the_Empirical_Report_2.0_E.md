# Oseen Vortex Initial-Value Experiment: Repositioning the Empirical Report (v2)

> This document was originally an empirical report titled *"Empirical Verification of
> Oseen Vortex Manifold Emergence and Topological Locking under the SRE-MDS Discrete
> Dynamics Paradigm"*. After unified cross-checking against `main_EN.md` v2, two
> central interpretations in the original report were found to be **overclaims**,
> inconsistent with the measurements of `sre_core.py`. This version retains the
> complete original experimental setup and observed data, corrects only the
> interpretations, and states explicitly where this experiment actually sits in the
> chain of evidence.

---

## 0. Summary of Corrections

| Original statement | Problem | Handling in this version |
| :--- | :--- | :--- |
| "The order parameter $\Phi(N)\equiv 1.0000$ is pinned at the ceiling … completing the most absolute closed-loop proof of the Oseen vortex pseudo-spectral bound conjecture" | $\Phi$ is defined as "surviving channels / current dimension". Being identically 1 means **zero pruning** — a trivial result at the chosen parameters, not a proof of noise immunity | Downgraded to "an indicator of the zero-dissipation limit"; the correct experimental design for testing noise immunity is given |
| "`Residual MSE = 8.93\times10^{-1}$` strictly represents the intrinsic non-Euclidean geometric curvature (topological curl)" | This residual is an **embedding error**: the pairwise dissimilarity cannot be represented faithfully in three-dimensional Euclidean space. No quantitative relation between it and "curvature" has been established | The value is retained, the curvature interpretation is deleted, and an alternative test route is given |
| "The outer yellow-green emergent shell … forms a perfect centripetal topological wrapping" | It relies on visual reading of a "rigid central axis", a phenomenon sensitive to the metric-reconstruction method (see `main_EN.md` §6.5) | No longer stated as a conclusion |
| The experimental parameter $\Lambda=0.05$ was called "extremely high Reynolds number" | Per the phase diagram of `main_EN.md` §6.2, $\Lambda=0.05$ lies at the **upper edge of the transition region**, with structure density about 0.44 — not an extreme Reynolds number | Corrected to "transition region" |

---

## 1. Experimental Setup (retained, unmodified)

* For the first 30 steps (`CORE_SIZE = 30`), inject a two-point correlation coupling
  square matrix conforming to the Lamb–Oseen vortex Gaussian distribution and an
  asymmetric unidirectional rotational velocity field;
* then hand over to the self-organising network to grow freely to $N=100$, with
  $\Lambda = 0.05$;
* reconstruct the correlation matrix into three-dimensional manifold coordinates by MDS.

```python
M_core = generate_oseen_vortex_initial_matrix(core_size=30)
for n in range(core_size, steps):
    ratio = (lam * d_matrix) / (np.abs(M @ M) + 1)
    activate_matrix = rand_matrix >= (1.0 - 1.0 / (1.0 + ratio))
distance_matrix = np.sqrt(np.clip(2.0 - 2.0 * (M_main / 1.0), 0, None))
coordinates_3d = MDS(n_components=3, dissimilarity='precomputed').fit_transform(distance_matrix)
```

Under the calibration of `main_EN.md` v2, the present $\Lambda=0.05$ falls at the
**upper edge of the transition region**: the Mode A phase diagram gives a structure
density of 0.4483 at $\Lambda=3.16\times10^{-2}$ and 0.3809 at $\Lambda=10^{-1}$, so
this working point has a structure density around 0.44 and a spectral slope around
−1.83. It is neither "laminar" nor "extremely turbulent".

---

## 2. Observation I: the correct reading of $\Phi(N)\equiv 1.0000$

**Original observation**: the order parameter stays pinned at 1.0000 as the steps
advance, with no fluctuation at all.

**Corrected reading**: in the implementation $\Phi$ is defined as

$$\Phi(n) = \frac{\text{number of surviving channels at this step}}{n}$$

The denominator $n$ is the current number of historical nodes, and the numerator is at
most $n$. Hence $\Phi\equiv 1$ is equivalent to **all frontier channels surviving at
every step**, i.e. $p_{\text{prune}}\approx 0$: the system sits in the
**zero-dissipation limit**.

This is a trivial result, not a proof of "noise-immune locking" — for a simple reason:
if the pruning probability is already zero, then there is no event of "noise being
resisted" to observe at all. In the zero-dissipation limit $\Phi\equiv1$ holds **by
construction**, regardless of whether the initial value is an Oseen vortex; with any
other initial value, even a purely random one, the same $\Phi\equiv1$ is obtained as
long as $p_{\text{prune}}\approx0$.

**To actually test noise immunity, the experiment should be designed thus**: fix the
initial value, sweep over $\Lambda$, observe the decay curve of $\Phi(\Lambda)$, and
compare the Oseen-vortex initial value against a chirality-free random initial value.
Per `main_EN.md` §6.2, $\Phi$ (here, the structure density) decays smoothly from 0.49
as $\Lambda$ grows, and it is the **shape** of that decay curve which carries the real
information. The original experiment sampled a single point of the curve.

> Conclusion: this observation cannot support a "closed-loop proof of the Oseen vortex
> pseudo-spectral bound conjecture". At most it shows that at this particular working
> point, $\Lambda=0.05$, pruning has not yet been activated.

---

## 3. Observation II: the correct reading of the residual $8.93\times10^{-1}$

**Original observation**: the MDS reconstruction residual is $0.893$.

**Corrected reading**: whether classical MDS or iterative SMACOF is used, this
residual is an **embedding error** — it measures "the degree to which the pairwise
dissimilarity matrix cannot be represented in three-dimensional Euclidean space".

No quantitative relation between it and "intrinsic non-Euclidean geometric curvature"
has been established. For such an interpretation to hold, one would need to:

1. first estimate the **intrinsic dimension** of the data (e.g. by maximum-likelihood
   estimation or the two-point correlation dimension), confirming that the true
   dimension exceeds 3;
2. then measure the "curl" independently with embedding-independent topological
   quantities (persistent-homology Betti numbers, discrete curvature);
3. finally establish the correspondence between the two.

Until then, $0.893$ should be reported only as "the three-dimensional embedding cannot
fully represent this pairwise metric", and the three-dimensional embedding itself is a
visualisation choice, not a physical dimension. Part of this value may also stem from
non-convergence of the MDS iteration (see the methodological comparison in
`main_EN.md` §6.1).

---

## 4. Where This Experiment Actually Sits in the Chain of Evidence

After the corrections, what this experiment can and cannot support is as follows.

**Can support**:

* an Oseen-vortex-type initial value can be injected into the discrete operator chain
  and retains its chiral character in subsequent evolution;
* at the working point $\Lambda=0.05$ the system maintains a chiral channel density of
  about 0.44, and the chiral field exhibits power-law scaling (slope about −1.83),
  consistent with `main_EN.md` §6.6.

**Cannot support**:

* any form of proof of the pseudo-spectral bound conjecture (this requires a parameter
  sweep, not a single point);
* topological noise-immune locking (this requires a controlled comparison: chiral
  initial value vs chirality-free initial value);
* intrinsic non-Euclidean curvature (this requires intrinsic dimension and independent
  topological quantities);
* emergence of a rigid central axis (sensitive to the metric-reconstruction method,
  see `main_EN.md` §6.5).

---

## 5. Recommended Additional Experiments

To bring this report up to publishable empirical strength, the following should be
carried out in order:

1. **$\Lambda$ sweep**: with the same Oseen-vortex initial value, sweep
   $\Lambda\in[10^{-4},10^{2}]$ (17 logarithmically spaced points, $\geq 5$ seeds) and
   report the structure density and spectral slope curves. `sre_core.py` can be reused
   directly.
2. **Initial-value control**: Oseen-vortex initial value vs chirality-free Gaussian
   initial value vs uniform random initial value; compare, at the same $\Lambda$, the
   evolution of structure density and of the topological charge
   $\mathcal{Q}=\operatorname{Tr}(A\mathbf{D})$.
3. **Intrinsic dimension estimation**: estimate the manifold intrinsic dimension with
   the two-point correlation dimension or MLE, decide whether the three-dimensional
   embedding is genuinely under-representing, and only then discuss "curvature".
4. **Embedding-independence test**: compute $\beta_0,\beta_1$ with persistent homology
   to test whether the "core–shell" structure exists independently of the MDS
   criterion.

---

## 6. Appendix: Relation to the Main Paper

This document no longer serves as the carrier of an independent empirical conclusion.
It is repositioned as **an initial-value specification and supplementary experimental
record for `main_EN.md` v2**. All quantitative assertions are subject to the
reproduction results of `sre_core.py`. The "paradigm comparison" table of the original
Section 1 has been merged into `main_EN.md` §1 and is not repeated here.
