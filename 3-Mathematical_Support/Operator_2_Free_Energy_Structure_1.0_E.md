# The Free-Energy Generative Structure of Operator 2 in Status–Relational Entropy Dynamics: The Heat-Bath Identity, the Geometric-Mean Law, and Four Verifiable Uses

Version: 1.0  

[Resource & Availability Statement] This framework is built on Status–Relational Entropy (SRE) dynamics. All theoretical materials are archived in the Zenodo open data repository. **This document suite includes the systems paper, application development, scientific hypotheses, the complete algebraic derivations of Operators 1–20, and the simulation code, all fully open source.**

> The author's GitHub repository is accessible at:
>
> https://github.com/yuelucn/Status-Relational-Entropy-SRE-Dynamics-The-Book-of-the-Void
>
> A Tencent intelligent document space (with AI-assisted search) is accessible at (available on both PC and WeChat mobile):
>
> https://docs.qq.com/space/DUkRjYUtNWFdyV253
>
> According to the Status–Relational Entropy (SRE) principle, the foundations of classical physics derive from information statistics.


**Abstract.** Status–Relational Entropy (SRE) dynamics reinterprets evolution in terms of "dissipation–compensation", yet throughout it possesses no generating functional: there is neither a phase space nor a Hamiltonian. This paper shows that what is missing is not a symbol $H$, but the **mechanism that converts already-existing objects into one and the same scalar**, and that this mechanism is in fact already written inside Operator 2. Rewriting the pruning probability of Operator 2 by one step yields

$$p=\sigma(-F),\qquad F=\ln\frac{\mathfrak{B}}{\Lambda D}$$

that is: **Operator 2 is itself a heat bath at temperature 1 (Glauber dynamics), and $F$ is the free-energy difference of this single flip.** Three testable consequences follow: the coherence length is controlled by the "geometric-mean barrier" rather than the arithmetic mean; the scaling exponent is not a constant but a local quantity that varies with depth; and replacing the arithmetic mean by the geometric mean incurs a bias that can be computed exactly (the Jensen gap). We performed a strict test on about $1.1\times10^6$ channel decisions: the identity residual is $2.2\times10^{-16}$, and the standardized residual is $0.96\sim1.07$ (if the formula is correct, this number should be exactly 1), showing that the geometric-mean law is an exact law rather than a fit.

More importantly, this set of formulas **works**. This paper presents four uses that have already been run successfully on real simulations: fitting only 3 parameters on even depths predicts the pruning rate at odd depths, reducing the error from 0.122 to 0.0090 ($R^2=0.995$); inverting the dissipation coefficient $\Lambda$ from observed data with an error of 2.0%, whereas the naive procedure that ignores the barrier errs by 80%; predicting the critical $\Lambda^*$ at which "the first layer is exactly half pruned", which is off by 33% in one shot and drops to 1.5% after two-step fixed-point iteration; and scoring channels by $F$ for selection, where keeping only 10% of channels recovers 40%–59% of the truly surviving channels, an enrichment of 4.0–5.9 fold. A negative result is also given: SRE cannot possess a Hamiltonian, and the three obstacles are mutually independent.

**Keywords**: free energy; Glauber heat bath; geometric mean; Jensen inequality; coherence length; scaling exponent; inverse problem; channel selection

---

## 1 Introduction

### 1.1 A gap between name and substance

SRE contains a quantity called $\mathcal H_{\mathrm{local}}$ whose name is "Hamiltonian", but which is in fact only a piecewise-linear function of the configuration, used to compute a weight and never generating any equation of motion. Elsewhere in the text there are three further "energy/action" objects — the local weight, the Dirichlet energy, and the symplectic structure — none of which can be converted into another. Consequently the theory speaks of "variational closure, energy conservation, least action", while structurally there is no functional that can be varied.

### 1.2 What this paper does

This paper does not supply an $H$; it argues instead that **SRE's true identity is free-energy-type dissipative dynamics, that its generative structure is hidden in the probability rule of Operator 2, and that nobody has ever solved it out.** Specifically it does three things:

1. rewrite the probability of Operator 2 into heat-bath form and give the closed form of $F$ (Theorem 1);
2. derive from $F$ the correct forms of the coherence length and the scaling exponent, with analytic expressions for the two corrections (Theorems 2 and 3);
3. prove that SRE cannot have a Hamiltonian and state clearly what the obstacles are (Proposition 5);
4. give four uses that are **already running, with reproducible numbers** (Section 6).

### 1.3 For undergraduates reading this for the first time

There is no need to understand the glossary in Section 2 first. The suggested reading order is: read 3.1 to see what the two operators do, then read Theorem 1 (it is one line of algebra), then jump to Section 6 to see what these formulas can do, and finally come back to the proofs. Every technical term at its first occurrence is explained in the body by a **boldfaced "one sentence"**; the glossary is only for later lookup.

---

## 2 Glossary

### 2.1 Probability and statistics

| Term | One-sentence explanation | Where used in this paper |
|---|---|---|
| probability $p$ | the confidence that an event occurs, ranging from 0 to 1 | pruning probability |
| odds | $p/(1-p)$, turning "0 to 1" into "0 to infinity" | logit |
| logit | the logarithm of the odds, $\ln\frac{p}{1-p}$. Its advantage is that it **turns multiplication into addition**, so that slope and intercept become meaningful | Theorem 3 |
| sigmoid $\sigma$ | $\sigma(z)=\frac{1}{1+e^{-z}}$, compressing any real number back into 0 to 1; it is the inverse of the logit | Theorem 1 |
| expectation $\mathbb{E}$ | weighted average (the weights are probabilities) | throughout |
| variance / standard deviation | the mean squared fluctuation / the typical size of a fluctuation | Theorem 2 |
| skewness / third cumulant | whether the distribution is left–right asymmetric | correction term of Theorem 2 |
| logarithm $\ln$ | turns "multiplication" into "addition"; $\ln(ab)=\ln a+\ln b$ | definition of $F$ |
| arithmetic mean | ordinary sum divided by the count | control |
| geometric mean | take logarithms, average, then transform back, $\exp(\mathbb{E}\ln x)$. It is **more robust to extreme values** | Theorem 2 |
| Jensen inequality | for a nonlinear function, "average then compute" $\ne$ "compute then average". For convex functions the former is larger, for concave functions smaller | Proposition 4 |
| normal distribution | the bell curve, fully determined by mean and variance | proof of Theorem 2 |
| binomial distribution | the distribution of the number of successes when a biased coin is tossed $n$ times | noise of the verification |
| standard error (SE) | the sampling fluctuation of an estimator; for a proportion it is $\sqrt{p(1-p)/n}$ | verification criterion |
| residual / standardized residual | observation minus prediction / residual divided by the fluctuation it should have. **If the model is right, the standardized residual should be "the noise itself", with RMS $\approx1$** | core of Section 5 |
| $R^2$ (coefficient of determination) | how much better the model is than "guess with the mean alone"; 1 means perfect | A1 |
| Gauss–Hermite quadrature | a numerical method that turns "a continuous integral" into "a small weighted sum" | Appendix A |
| probit approximation | approximating the sigmoid by the normal distribution function, error about 1% | Appendix A comparison |
| AUC | the probability that, given one positive and one negative sample at random, the scorer ranks the positive first. 0.5 is guessing, 1 is perfect ordering | A4 |
| precision / recall | of what was selected, how much is correct / of what is correct, how much was selected | A4 |
| lift | precision divided by the "pick at random" baseline, measuring how many times better than guessing | A4 |
| hold-out | fit on one half of the data and test on the other, to prevent self-deception | A1, A2 |

### 2.2 Physics

| Term | One-sentence explanation | Where used in this paper |
|---|---|---|
| free energy | a measure of "how much work the system wants to do", $F=E-TS$: energy wants to decrease, entropy wants to increase, and the temperature $T$ decides whose voice is louder | Theorem 1 |
| Boltzmann weight | $e^{-E/T}$; the lower the energy, the larger the weight | the phase-transition argument of the original text |
| heat bath / Glauber dynamics | the system sits in a constant-temperature environment and accepts a flip with probability $\sigma(-\Delta F/T)$. **No Newtonian equation needs to be written** | Theorem 1 |
| phase space | the space spanned jointly by "position + momentum"; the minimal stage of classical mechanics | Proposition 5 |
| conjugate momentum | the quantity paired with position (for example velocity times mass) | Proposition 5 |
| Hamiltonian $H$ | a function on phase space that **generates** time evolution: $\dot q=\partial H/\partial p$, $\dot p=-\partial H/\partial q$ | Proposition 5 |
| Lagrangian / action | the "cost" accumulated along a path; an extremal action is the principle of least action | Proposition 5 |
| Poisson bracket / symplectic structure | the algebraic skeleton of Hamiltonian evolution, which must be **antisymmetric** | Proposition 5 |
| canonical transformation | a coordinate transformation preserving the symplectic structure. **Hamiltonian evolution is always a canonical transformation**, hence must be invertible | Proposition 5(ii) |
| generating function | the "potential" describing a canonical transformation. Conversely: **an irreversible transformation has no generating function, and hence no $H$** | Proposition 5(ii) |
| Noether's theorem | each continuous symmetry corresponds to a conserved quantity; time-translation symmetry corresponds to energy conservation | Proposition 5(iii) |
| generator / semigroup | when evolution can be written $e^{tA}$, $A$ is the generator. If it is definable only for $t\ge0$, it is a semigroup (irreversible) | Proposition 5(i) |
| eigenvalue / eigenmode | those modes whose shape evolution does not change, only being scaled by $e^{\lambda t}$ | Proposition 5(i) |
| coherence length $\xi$ | beyond this scale, two places are essentially "mutually incoherent" | Theorem 2 |
| scaling exponent / power law | the $n$ in $y\propto x^n$; on log axes it is the slope | Theorem 3 |
| GENERIC | the framework that writes "reversible energy flow" and "irreversible entropy production" side by side in one equation | corollary of Proposition 5 |

### 2.3 Graphs and algorithms

| Term | One-sentence explanation | Where used in this paper |
|---|---|---|
| graph Laplacian $\mathbf L_G=\mathbf D-\mathbf A$ | the standard "diffusion" operator on a graph; it is symmetric, hence can only decay, not oscillate | Proposition 5(i) |
| surjective / injective | every target has a preimage / distinct inputs map to distinct outputs. Not being surjective means "losing information", i.e. not invertible | Proposition 5(ii) |
| read-only inheritance | rows and columns already written are never revised | Operator 1 |
| classifier scoring | give every sample a score, sort by score, take the first few | A4 |
| fixed-point iteration | repeatedly applying $x\leftarrow g(x)$ to approach the solution of $x=g(x)$ | A3 |

---

## 3 Notation and objects

### 3.1 Configurations and the two operators

A **configuration** is an $n\times n$ relational matrix $M$ with entries $+1$ or $-1$: $+1$ means "identity element / no relation", $-1$ means "chirality present / interference present". Binary and zero-forbidden.

**Operator 1 (expansion)**: at step $n$ a new $n$-th row and $n$-th column are added, and for each old column $v_m<n$ a value is decided in turn; once written it propagates forward only and is never revised (read-only inheritance).

**Operator 2 (pruning)**: for a channel $c$, first compute a "two-step-walk interference quantity"

$$\tilde{\mathcal E}_c=\underbrace{\sum_{k}\big[M_{k,v_m}\ne1\big]\big[M_{v,k}\ne1\big]M_{v,k}M_{k,v_m}}_{\text{interference}}+\underbrace{2M_{v,v_m}}_{\text{self}}$$

The first term is the interference term of the two-step walk: **only intermediate nodes whose both endpoints are non-identity are counted**; the second term is the self term.

Then define the **barrier** $\mathfrak{B}_c=\lvert\tilde{\mathcal E}_c\rvert+e^{\operatorname{sgn}\tilde{\mathcal E}_c}>0$ and the **depth** $D_c=n-v_m-1$ (the more recently a channel is added, the shallower it is; the newest channel has $D=0$), and finally

$$p_c=1-\frac{1}{1+\Lambda D_c/\mathfrak{B}_c} \qquad (1)$$

toss a coin to decide whether to prune. $\Lambda$ is the exogenous dissipation coefficient (written $\Gamma$ in the original text). This paper uses $\Lambda$ so as not to be confused with the inverse temperature $\beta$.

> **Notation note**: a channel with $D=0$ is never pruned by (1) ($p=0$); all formulas below assume $D\ge1$ by default.

### 3.2 Why the double mask is mandatory

$\tilde{\mathcal E}$ accumulates only intermediate nodes **non-identity at both ends**. If the second layer $[M_{v,k}\ne1]$ is omitted, the $+1$ "empty slots" are counted as genuine interference, producing impossible channels with $\mathfrak{B}=1$ and inflating the Jensen gap from 0.95 to a spurious 0.70. An early version of this paper fell into this trap; it should be written into the formal definition of the operator.

---

## 4 Main results

### 4.1 Theorem 1 (heat-bath identity)

> **In one sentence: the rule of Operator 2 is not an arbitrary design; it is exactly a standard heat bath.**

Let

$$F_c=\ln\frac{\mathfrak{B}_c}{\Lambda D_c} \qquad (2)$$

Then (1) and the following are **identical**:

$$p_c=\sigma(-F_c)=\frac{1}{1+e^{F_c}} \qquad (3)$$

**Proof.** From $\Lambda D_c/\mathfrak{B}_c=e^{-F_c}$ we have $\dfrac{1}{1+\Lambda D_c/\mathfrak{B}_c}=\dfrac{1}{1+e^{-F_c}}=\sigma(-F_c)$, and then $1-\sigma(-F_c)=\dfrac{e^{-F_c}}{1+e^{-F_c}}=\dfrac{1}{1+e^{F_c}}=\sigma(-F_c)$. Q.E.D.

**How to read (3)**: when $F>0$, $\sigma(-F)<1/2$, tending not to prune; when $F<0$, tending to prune. $F$ is exactly "the difference of free energy before and after this flip" — $\ln\mathfrak{B}$ is the resistance, $\ln(\Lambda D)$ the driving force, and their difference is the net driving force. This is the heat-bath rule $\sigma(-\Delta F/T)$ specialized to $T=1$ with $\Delta F=\ln(\Lambda D)-\ln\mathfrak{B}$.

**Corollary 1.1** The dynamical class of Operator 2 is the Glauber heat bath, and $F$ is the scalar mother-object of this system.

**Corollary 1.2 (the three layers and the transition no longer need external calibration)** $F>0$, $F\approx0$, $F<0$ are exactly the three-layer structure; the coexistence surface $F=0$ is $\Lambda_c=\mathfrak{B}/D$ — the transition point, formerly treated as a "calibration anchor", is now the zero set of $F$.

### 4.2 Theorem 2 (geometric-mean law)

> **In one sentence: what controls the coherence length is the geometric mean of the barrier, not the arithmetic mean.**

Fix the depth $D$, and write $u=\ln\mathfrak{B}$, $\mu_D=\mathbb{E}[u\mid D]$, $s_D^2=\operatorname{Var}(u\mid D)$. The expected pruning rate of the depth profile is

$$f(D)=\mathbb{E}\big[\sigma\big(\ln(\Lambda D)-u\big)\mid D\big] \qquad (4)$$

**Conclusion**: the half-value point $\xi$ (satisfying $f(\xi)=\tfrac12$) obeys

$$\ln(\Lambda\xi)=\mu_\xi+O\big(\kappa_{3,\xi}s_\xi^3\big),\qquad \xi=\frac{\mathfrak{B}_{\mathrm{geo}}(\xi)}{\Lambda},\quad \mathfrak{B}_{\mathrm{geo}}=e^{\mu} \qquad (5)$$

**Proof.** Let $g(m)=\mathbb{E}[\sigma(m-u)]$. Since $\sigma$ is strictly monotone, $g$ is strictly monotone and the half-value point is unique. Expand $u$ about $\mu$ to third order:

$$g(\mu+\delta)=\sigma(\delta)+\frac{s^2}{2}\sigma''(\delta)-\frac{\kappa_3s^3}{6}\sigma'''(\delta)+O(s^4)$$

Substituting $\sigma(0)=\tfrac12$, $\sigma''(0)=0$, $\sigma'''(0)=-\tfrac18$ gives $g=\tfrac12+\tfrac{\delta}{4}+\tfrac{\kappa_3s^3}{48}+O(s^4)$. Setting $g=\tfrac12$ yields $\delta=-\kappa_3s^3/12$. Q.E.D.

**Order of magnitude**: measured $s\le0.17$, $\lvert\kappa_3\rvert\le4.7$, so the correction is $\le2\times10^{-3}$ in log units and negligible. This is why "the geometric mean" is almost exact in this ensemble.

**Note 1 (why a global mean cannot be used)**: replacing $\mu$ by a global mean $\bar\mu$ introduces a drift of $\mu$ along depth. Measured, $\xi\Lambda$ varies between $4.75$ and $5.77$ (21%), so "$\xi\propto1/\Lambda$ with a global geometric-mean proportionality constant" holds only to 20% accuracy.

### 4.3 Theorem 3 (local scaling exponent)

> **In one sentence: the scaling exponent is not a constant; it varies with depth, and fluctuations contribute less than 1% correction.**

$$n(D)=\Big(1-\frac{\mathrm{d}\mu_D}{\mathrm{d}\ln D}\Big)\cdot\frac{1}{\sqrt{1+\alpha s_D^2}},\qquad \alpha=0.4028 \qquad (6)$$

**Proof.** From (4), $\mathrm{logit}\,f=\mathrm{logit}\,g(m)$ with $m=\ln(\Lambda D)$. Differentiating totally with respect to $\ln D$: the explicit part of $m$ contributes 1, the implicit part of $\mu_D$ contributes $-\mathrm{d}\mu_D/\mathrm{d}\ln D$, and the whole is multiplied by the slope of $G(m)\equiv\mathrm{logit}\,\mathbb{E}[\sigma(m-u)]$ at $m=\mu$. That slope is independently calibrated by Gauss–Hermite quadrature as $A(s)=1/\sqrt{1+\alpha s^2}$ (Appendix A). Q.E.D.

**Note 2 (the chord slope is not the exponent)**: in practice $\mathrm{logit}f$ is regressed linearly against $\ln D$ over the whole range, and the resulting "exponent" is really the weighted average of $n(D)$ within that range, further superposed with the nonlinearity of $\mu_D$. It changes with $\Lambda$ (measured $1.023\sim1.116$) and should not be reported as a universal constant.

### 4.4 Proposition 4 (Jensen gap)

$$\lambda_J\equiv\frac{\mathfrak{B}_{\mathrm{geo}}}{\mathfrak{B}_{\mathrm{arith}}}=\exp\big(\mathbb{E}[\ln\mathfrak{B}]-\ln\mathbb{E}[\mathfrak{B}]\big)\le1 \qquad (7)$$

> **In one sentence: it quantifies exactly the error of "using the arithmetic mean instead of the geometric mean".**

Measured $\lambda_J=0.946\sim0.999$ ($\Lambda:0.2\to2.0$), i.e. an error of 0.1%–5.4%.

### 4.5 Proposition 5 (no Hamiltonian is possible)

> **In one sentence: this is not "not yet found", but three independent structural obstacles.**

**(i) The generator is of the wrong type.** The original text explicitly fixes the generator of the refresh dynamics as the graph Laplacian $\mathbf L_G=\mathbf D-\mathbf A$. It is symmetric positive semidefinite and generates a **semigroup** $e^{-\mathbf L_Gs}$, whose eigenvalues are decay rates; a Hamiltonian is antisymmetric and generates a **group** $e^{-iHt}$, whose eigenvalues are frequencies. Different categories.

**(ii) Irreversible, hence no generating function.** Hamiltonian evolution is a canonical transformation and must be invertible and preserve phase volume. The read-only inheritance of Operator 1 makes the map non-surjective, and Operator 2 is an elimination; their composition is irreversible, and an irreversible transformation has no generating function, so no $H(q,p)$ can be written.

**(iii) No phase space.** Configurations take values in $\{\pm1\}$ with no conjugate momentum; time is only the accumulated bookkeeping of dissipation–compensation, with no time-translation symmetry, so Noether's theorem yields no conserved energy.

**Corollary 5.1** SRE belongs at most to a free-energy gradient flow / generalized GENERIC:

$$\partial_s m=\kappa_A\mathbf J\nabla\mathcal E+\kappa_L\mathbf L_G\nabla\mathcal S$$

but neither of the two degeneracy conditions of strict GENERIC holds ($\mathbf J\nabla\mathcal S\ne0$, $\mathbf L_G\nabla\mathcal E\ne0$), so $F=\mathcal E-T\mathcal S$ is in general not monotone. This is consistent with (5)(6): **free energy is a "potential", not an "energy".**

---

## 5 Strict numerical verification

### 5.1 Protocol

$N=600$ steps, 6 random seeds, 6 values of $\Lambda$, with about $1.08\times10^6$ channel decisions merged per value. Binning by depth (at least 300 samples per bin), keeping only the transition band with $f\in(0.05,0.95)$. All tests are performed in **logit space** and standardized with the delta-method standard error $\mathrm{SE}=1/\sqrt{nf(1-f)}$.

| ID | Test | Criterion |
|---|---|---|
| K1 | identity (3) | $\max\lvert p-\sigma(-F)\rvert<10^{-12}$ |
| K2 | barrier positivity | $\mathfrak{B}>0$ |
| K3 | geometric-mean law (5) | standardized residual ${\mathrm{RMS}}(z)\in[0.75,1.25]$ |
| K4 | intersection equation | $\lvert\ln(\Lambda\xi)-\mu(\xi)\rvert<0.08$ |
| K5 | local exponent (6) | chord slope differs from $1-\Delta\mu/\Delta\ln D$ by $<0.03$ |

**K3 is the core**: if (5) is right, the residual should be exactly the binomial sampling noise, ${\mathrm{RMS}}(z)\approx1$; if the geometric-mean law is wrong, this number will be far larger than 1. Using "the distribution of the predicted residual" rather than "tuning parameters to fit the curve" is the key distinction of the verification in this paper.

### 5.2 Results

| $\Lambda$ | bins | ${\mathrm{RMS}}(z)$ | $\ln(\Lambda\xi)-\mu(\xi)$ | $\xi$ | geometric error | arithmetic error | chord slope (measured) | chord slope (predicted) | $\lambda_J$ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.20 | 479 | 1.000 | $+0.019$ | 25.90 | 1.90% | 1.92% | 1.116 | 1.137 | 0.946 |
| 0.34 | 285 | 1.066 | $-0.008$ | 13.97 | 0.84% | 1.44% | 1.069 | 1.086 | 0.977 |
| 0.50 | 193 | 1.034 | $-0.040$ | 10.59 | 4.10% | 7.06% | 1.046 | 1.065 | 0.988 |
| 0.80 | 115 | 1.064 | $+0.001$ | 7.21 | 0.06% | 1.71% | 1.038 | 1.044 | 0.995 |
| 1.20 | 79 | 0.960 | $+0.019$ | 4.45 | 1.88% | 0.72% | 1.026 | 1.033 | 0.997 |
| 2.00 | 47 | 1.005 | $+0.024$ | 2.56 | 2.36% | 1.80% | 1.023 | 1.023 | 0.999 |

K1–K5 all pass (script exit code 0, output `SUCCESS`).

### 5.3 Three readings

1. **${\mathrm{RMS}}(z)\approx1$ is evidence that "the formula is right", not that "the fit is good".** We tuned no parameter to match the curve; instead we first computed how large the residual should be, then checked whether it is exactly the noise.
2. **The chord slope being systematically greater than 1 is physics, not error.** $\mathrm{d}\mu/\mathrm{d}\ln D<0$ makes $n(D)>1$; as $\Lambda$ increases the barrier contrast collapses, so the chord slope decreases monotonically from 1.116 to 1.023.
3. **Geometric and arithmetic means are indistinguishable in this ensemble** ($\lambda_J\ge0.946$, maximum difference 5.4%, the same order as the interpolation error). Hence the evidence for (5) comes from K4, not from a comparison of "which mean is more accurate". To genuinely distinguish the two, an ensemble with larger $\mathfrak{B}$ dispersion must be constructed.

---

## 6 What it is good for: four scenarios already running

> All numbers in this section come from `verify_applications.py`, which shares the same simulator as Section 5; the evaluation data were never fed back into the fit.

### 6.1 A1: predicting the pruning rate without tossing the coin

**Question**: given an already grown matrix, can the pruning rate at some depth be predicted **without waiting for the actual pruning outcome**? In engineering terms this is "can one measure the structure only, not the outcome". The answer is yes — because $\mathfrak{B}$ is computed from the matrix before the coin is tossed, and $F$ depends only on $\mathfrak{B}$ and $D$.

**Procedure**: at $\Lambda=0.8$, $N=600$, fit 3 parameters using only the **even depths** (155 of them)

$$\mu(D)=a+b\ln D+c(\ln D)^2$$

(measured $a=1.7461$, $b=-0.0315$, $c=-0.0001$), then predict $f(D)=\sigma(\ln(0.8D)-\mu(D))$ at the **odd depths** (153 of them, which took no part in the fit).

**Results**:

| Metric | Value |
|---|---|
| prediction RMSE (probability space) | **0.0090** |
| baseline (always guess the training-set mean pruning rate) RMSE | 0.1224 |
| explanatory power relative to baseline $R^2$ | **0.9946** |

The prediction error is only 1/14 of the baseline. **Use**: three numbers can replace the empirical statistics of more than three hundred depth bins; conversely, if the measured curve departs from this 3-parameter curve and the residual exceeds the sampling noise, the system contains heterogeneity beyond the structure — which is itself a ready-made anomaly-detection idea (control chart: alarm when the residual $z$ exceeds 3).

### 6.2 A2: inverting the dissipation coefficient from observations

**Question**: if $\Lambda$ is unknown (it is often supplied by the external environment and cannot be measured), can it be recovered from "the curve of pruning rate versus depth"?

**Procedure**: take the logit of (3) and rearrange:

$$\ln\Lambda=\mathrm{logit}\,f(D)-\ln D+\mu_D \qquad (8)$$

Every quantity on the right is measurable ($f$ from outcome counts, $\mu_D$ from the barrier), so averaging over several depths gives the estimator $\hat\Lambda=\exp\langle\cdot\rangle$.

**Results** (true $\Lambda=0.8$):

| Estimator | Value | Relative error |
|---|---|---|
| corrected estimate $\hat\Lambda=\exp\langle\mathrm{logit}f-\ln D+\mu_D\rangle$ | 0.7839 | **2.01%** |
| naive estimate $\hat\Lambda_0=\exp\langle\mathrm{logit}f-\ln D\rangle$ (assuming $\mathfrak{B}=1$) | 0.1596 | 80.06% |

The naive method is low by a factor of 5.01, because it drops the barrier ($\langle\ln\mathfrak{B}\rangle\approx1.59$, $e^{1.59}\approx4.9$). **Use**: $\Lambda$ is a physical parameter that can be inverted, rather than a constant that can only be specified externally — this gives SRE, for the first time, a channel for "determining parameters from data". It also shows that the $\mathfrak{B}$ term **cannot be omitted**: omitting it means a factor-5 bias.

### 6.3 A3: extrapolating to a new parameter (including one failure)

**Question**: can the critical $\Lambda^*$ at which "the first layer ($D=1$) is exactly half pruned" be predicted without a parameter sweep?

**One-shot prediction**: at $\Lambda=0.8$ we measure $\mu_1=1.9097$. Setting $f(1)=\tfrac12$ in (5) gives $\Lambda^*=e^{\mu_1}=6.751$.

**Test**: actually running $\Lambda=6.751$ gives $f(1)=0.5635$ — a deviation of **0.0635** from 0.5. Compared with the fixed-point solution $\Lambda^*=5.081$, $\Lambda$ was overestimated by **33%**.

**Why it fails**: $\mu_1$ itself varies with $\Lambda$. When $\Lambda$ is large the matrix is pruned emptier, and the barrier distribution changes with it, so $\mathfrak{B}$ is not an exogenous constant and a one-shot substitution must be biased.

**Correction**: treat (5) as a **self-consistent equation** $\Lambda=e^{\mu_1(\Lambda)}$ and perform fixed-point iteration:

| Iteration | $\Lambda$ | $\mu_1$ | measured $f(1)$ | next $\Lambda$ |
|---:|---:|---:|---:|---:|
| 0 | 6.751 | 1.6078 | 0.5635 | 4.992 |
| 1 | 4.992 | 1.6256 | 0.4849 | 5.081 |
| converged | **5.081** | — | **0.4849** | deviation 0.0151 |

Two steps compress the deviation of $f(1)$ from 0.0635 to **0.0151** (a 4.2-fold improvement). **Use**: this gives an operational method — **whenever predicting a parameter coupled to its own state, one must solve the self-consistent equation, never substitute once**. This lesson is more valuable than the prediction itself.

### 6.4 A4: scoring channels with $F$ for selection

**Question**: if only the "skeleton" of the matrix is to be kept, which channels should be kept? $F$ is exactly the ranking score (the smaller $p$, the more it should be kept).

**Procedure**: sort by increasing $p$, keep only the first 10%, and record the "survival purity" (the fraction of kept channels that truly survive), the "survival recall" (the fraction of truly surviving channels that are recovered) and the enrichment factor.

**Results**:

| $\Lambda$ | pruning base rate | AUC | discard-side purity (lift) | keep 10%: survival purity (lift) | survival recall |
|---:|---:|---:|---:|---:|---:|
| 0.34 | 84.7% | 0.808 | 0.971 (1.15×) | 0.617 (**4.03×**) | 0.403 |
| 0.80 | 92.2% | 0.825 | 0.988 (1.07×) | 0.393 (**5.03×**) | 0.503 |
| 2.00 | 96.2% | 0.847 | 0.995 (1.04×) | 0.227 (**5.90×**) | 0.590 |

**How to read**: in this system the vast majority of channels are pruned anyway (base rate 85%–96%), so "discard-side purity 0.99" is almost the same as guessing (lift only 1.04–1.15×), and **this is not the selling point**. The real selling point is the retained side: keeping only 10% of channels recovers 40%–59% of the truly surviving channels, an enrichment of 4.0–5.9 fold; and the "cleaner" the system ($\Lambda$ larger), the stronger the enrichment.

**Use**: this is a quantitative scheme for "skeleton extraction" — compress by 90% and keep about half of the true structure. The larger $\Lambda$, the more economical the scheme.

### 6.5 Summary

| Scenario | Input | Output | Measured accuracy | Corresponding formula |
|---|---|---|---|---|
| A1 prediction | barrier + 3 parameters | pruning rate at any depth | RMSE 0.0090 ($R^2=0.995$) | (3)(5) |
| A2 inversion | pruning counts + barrier | $\Lambda$ | error 2.01% | (8) |
| A3 extrapolation | local measurement at $\Lambda=0.8$ | critical $\Lambda^*$ | 27% off in one shot, 1.5% after iteration | (5) self-consistent |
| A4 selection | full matrix | 10% skeleton | recall 0.40–0.59, enrichment 4–5.9× | (3) |

All four are **predictive** uses (they use data that took no part in the fit), not descriptive uses (restating what has already been seen in different words).

---

## 7 Relation to existing texts

**Correction to Theorem 5 of the original text.** The original text argues the three phases using "probability follows $\exp(-\beta\mathcal H_{\mathrm{local}})$". But $\mathcal H_{\mathrm{local}}$ is **piecewise linear** in $\tilde{\mathcal E}$, whereas the driving quantity of (1) is the **logarithm** $\ln\mathfrak{B}$; no single $\beta$ can make the two equal. The correct causal direction is the reverse: $\mathfrak{B}$ (and hence $F$) is the mother object, and $\mathcal H_{\mathrm{local}}$ is only the hard $T\to0$ limit and a monotone surrogate. The three phases in this picture are the constant offsets $e^{-1},1,e$ of $F$ — **those two $\pm1$ are "thermal units", not Euler's constant**.

**Correction to Theorem 2 of the original text.** The three layers are the trichotomy of $\operatorname{sgn}F_c$; but the transition layer degenerates into a single section in mean-field depth coordinates (measured transition-band fraction $\approx0$). A mesoscopic layer with width must rely on fluctuations of $\mathfrak{B}$ or on multiscale heterogeneity.

**Relation to Operator 7.** The symplectic matrix $\mathbf J$ is a legitimate discrete realization on the dual space and may serve as a candidate for the antisymmetric block $\mathbf L$ in GENERIC; but it serves the solver, not the ontology.

---

## 8 Discussion

### 8.1 How the scaling law should be written

Do not write "$\xi\propto1/\Lambda$ with proportionality constant $\langle\mathfrak{B}\rangle$". The correct statements are two:

**Local form**

$$\xi(D)=\frac{\mathfrak{B}_{\mathrm{geo}}(D)}{\Lambda}$$

**Exponent form**

$$n(D)=1-\frac{\mathrm{d}\ln\mathfrak{B}_{\mathrm{geo}}}{\mathrm{d}\ln D}$$

The global form holds approximately only when $\mathfrak{B}_{\mathrm{geo}}$ varies slowly (measured drift 21%).

### 8.2 Why the fluctuation correction is sub-percent

Measured $s^2\le0.028$, hence $A(s)\ge0.994$. The dominant effect is the drift of $\mu_D$, not the fluctuation. This is directly related to the support of $\mathfrak{B}$ being pinned to $[4.718,\infty)$ with mass concentrated on few values.

### 8.3 Limitations

1. **$\lambda_J$ is not resolvable**: geometric and arithmetic means differ by less than 5.4% in this ensemble, the same order as the interpolation error. Resolving them requires a variant with larger $\mathfrak{B}$ dispersion.
2. **Temperature is pinned at 1**: if an adjustable $T$ were introduced, (3) would become $\sigma(-F/T)$, and both $\xi$ and $n$ would shift with $T$, allowing a stricter collapse test.
3. **Sensitive to implementation details**: both layers of the mask are indispensable (§3.2).
4. **$\mathfrak{B}$ is not an exogenous constant**: A3 has shown that it varies with $\Lambda$, so any "one-shot substitution" extrapolation is unreliable.
5. **The mechanism of read-only inheritance is not elaborated**: this paper uses only the statistics of $D$ and $\mathfrak{B}$.

### 8.4 Falsifiable predictions

1. At any $\Lambda$, the intersection satisfies $\lvert\ln(\Lambda\xi)-\mu(\xi)\rvert<0.05$.
2. $n(D)$ approaches 1 monotonically with $\Lambda$, and $n(D)-1$ has the same sign as $\mathrm{d}\mu/\mathrm{d}\ln D$.
3. $\lambda_J(\Lambda)\to1$ as $\Lambda$ increases.
4. In a variant with amplified $\mathfrak{B}$ dispersion, the intersection must follow the geometric mean, in which case $\lambda_J$ is measurable and $<1$.

---

## 9 Conclusion

SRE does not need an externally supplied Hamiltonian; it needs to solve its own probability rule into a free energy. In Operator 2 this step is an **identity rather than an assumption**: $p=\sigma(-F)$, $F=\ln(\mathfrak{B}/\Lambda D)$. The geometric-mean law and the local exponent law derived from it behave as exact laws on million-scale samples (the standardized residual is exactly the noise), and yield two corrections that must be written into the theory.

In terms of use, this set of formulas can already: predict the pruning rate at any depth with 3 parameters ($R^2=0.995$); invert $\Lambda$ from observations (error 2%, naive method 80%); predict the critical parameter (requires solving a self-consistent equation, two iterations converging to 1.5%); and compress the matrix to 10% while retaining about half of the true skeleton (enrichment 4–5.9×). Meanwhile Proposition 5 explains why no Hamiltonian will appear along this route. Positioning SRE as **free-energy-type dissipative dynamics** is more accurate than claiming "everything unifies in a Hamiltonian", and is also easier to falsify.

---

## Appendix A Independent calibration of the logistic–normal integral

For $u\sim\mathcal N(0,1)$, $v=m+su$, compute $\mathbb{E}[\sigma(v)]$ with 80-point Gauss–Hermite quadrature, then regress $\mathrm{logit}\,\mathbb{E}[\sigma]$ on $m$ within $f\in(0.05,0.95)$:

| $s$ | 0.00 | 0.20 | 0.40 | 0.60 | 0.80 | 1.00 | 1.20 | 1.40 | 1.60 |
|---|---|---|---|---|---|---|---|---|---|
| $A(s)$ | 1.000 | 0.992 | 0.970 | 0.936 | 0.893 | 0.845 | 0.796 | 0.747 | 0.701 |

Fitting $A(s)=1/\sqrt{1+\alpha s^2}$ gives $\alpha=0.4028$, with maximum deviation $3.2\times10^{-3}$. The probit approximation gives $1/1.702^2=0.3452$ (17% off); the numerically calibrated value is authoritative. **This calibration uses no simulation data**, so the test of (6) is a cross-validation of two independent computational routes.

## Appendix B Reproduction

```powershell
cd 5-Appendixs/Operators/Operator_2_Free_Energy_Structure   # chapter program directory (archived with the book)
python verify_free_energy_strict.py   # Section 5: K1–K5
python verify_applications.py         # Section 6: A1–A4
```

Both scripts print item-by-item KPIs and exit with code 0 when normal.

## Appendix C Symbols

| Symbol | Meaning |
|---|---|
| $M$ | relational matrix, entries $\in\{\pm1\}$, $+1$ is the identity element |
| $\tilde{\mathcal E}$ | two-step-walk interference quantity (double mask) |
| $\mathfrak{B}$ | barrier $\lvert\tilde{\mathcal E}\rvert+e^{\operatorname{sgn}\tilde{\mathcal E}}>0$ |
| $D$ | channel depth $n-v_m-1$ |
| $\Lambda$ | exogenous dissipation coefficient ($\Gamma$ in the original text) |
| $F$ | free-energy difference $\ln(\mathfrak{B}/\Lambda D)$ |
| $\mu_D,s_D^2$ | depth-conditional mean and variance of $\ln\mathfrak{B}$ |
| $\xi$ | coherence length (intersection depth of $f=\tfrac12$) |
| $\mathfrak{B}_{\mathrm{geo}}$ | geometric mean $e^{\mu}$ |
| $\lambda_J$ | Jensen gap |
| $n(D)$ | local scaling exponent |
| $\alpha$ | logistic–normal convolution coefficient, $0.4028$ |

## Appendix D Implementation notes for the applications

- **A1**: fitting on even depths and testing on odd depths is "alternating hold-out", harder to fake than one-sided extrapolation; using a quadratic polynomial for $\mu(D)$ is an empirical choice, not a theoretical requirement.
- **A2**: the estimator is very sensitive to the error of $\mu_D$ ($\ln\Lambda$ adds $\mu$ directly), so the two-layer mask of the barrier definition must first be confirmed correct (§3.2).
- **A3**: whether the fixed-point iteration converges depends on $\lvert\mathrm{d}\mu/\mathrm{d}\Lambda\rvert$; in this example two steps converge, but in general one should try the iteration before drawing conclusions.
- **A4**: base rate and lift must be reported together. Looking at precision alone is fooled by a high base rate (here the discard-side lift is only 1.04–1.15×).

## References (internal)

[1] `combined_C.md`, the pruning rule and pseudocode of Operator 2.
[2] ibid., the combinatorial Laplacian as generator, eigenmodes as relaxation modes.
[3] ibid., Theorem 5 (three phases) and Theorem 2 (three-layer structure).
[4] ibid., the symplectic structure $\mathbf J$ of Operator 7.
[5] ibid., two assertions corrected by this paper: that the conservation property is "complete", and that $\det\mathbf M=1$ implies energy conservation; §7.0 and the introduction show that neither holds.
