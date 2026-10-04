# Emergence of Time in the State–Relational–Entropy Framework

## A Saturation Law for the Rate of Change, Universality, and the Incompatibility of Two Internal Clocks

**Version: 1.0**
**Date: 2026-10-04**
**Short abstract: `SRE_时间涌现_摘要.md` (English first, Chinese after)**

---

## Abstract

**Background and problem.** Within the State–Relational Entropy (SRE) framework the word "time" currently carries three distinct objects under one name, so any discussion of whether time is uniform must begin with a clarification of definition. This paper starts from a concrete observation: every update in the evolution loop occurs with a *per-step probability*, and this family of probabilities is what an external observer perceives as "change in the world". If that is so, time is not an externally imposed parameter but a derived quantity obtained *after an internal process has been designated as the clock*. The task of this paper is to turn that sentence into something computable and falsifiable.

**Method.** No new free real number is introduced. $\lambda$ and the step-count scale follow existing registrations, and the evolution loop is unaltered; what is new is one definition and a set of verdicts. The defining quantity is

$$
\Omega(n)\;=\;\big\langle\,a_{ij}(n)\,\big\rangle_{\text{all }n^{2}\text{ entries}},
\qquad
a_{ij}=\frac{\rho_{ij}}{1+\rho_{ij}},\qquad
\rho_{ij}=\frac{\lambda\,d_{ij}}{|M^{2}|_{ij}+1},
$$

read as "the time worth of step $n$ = the expected amount of change in the world at that step", together with $T_{\rm em}(n)=\sum_{k<n}\Omega(k)$, the **emergent time**. Every conclusion is synthesized from two **pre-existing zero-parameter laws** (the age-distribution law and the iid $|S_n|$ spectral law of round 77) and then compared against measurement.

**Results.** Seven verdicts. (1) **Saturation**: $\Omega$ rises monotonically toward $1$; at $999$ steps the remaining gap is still $0.1540$, and the self-consistency check holds to $2.2\times10^{-16}$. (2) **Saturation law**: $1-\Omega=c\ln n/\sqrt n$ with $c=0.694157$ and a maximum relative residual of $1.589\%$, whereas a pure power law $n^{-1/2}$ gives $26.43\%$ — the logarithm is the fingerprint of the harmonic tail. The same law is predicted **with zero free parameters** by combining the age law with the spectral law, agreeing with measurement to $0.28\%$–$1.65\%$. (3) **Asymptotic uniformity**: the relative step-to-step non-uniformity $\eta$ falls from $4.23\times10^{-3}$ ($n=50$) to $6.10\times10^{-5}$ ($n=980$), and its ratio to the prediction *differentiated from the saturation law* stays inside $[0.873,1.407]$. (4) **Internal non-uniformity**: the rewriting rate of a single element rises monotonically with its own age; at $n=999$ it runs from $0.058931$ (newborn) to $0.957750$ (oldest), so the clock of an individual member is not uniform. (5) **Universality**: sweeping $\lambda$ from $0.2$ to $3.0$ (a factor of $15$) does not move the limit of $\Omega$, only the speed of approach. (6) **Phase transition**: squaring the denominator of the update rule (a single symbol) moves the limit from $1.0000$ to about $0.390$; at $1099$ steps the gap between the two groups has reached $0.4629$ and is still widening. (7) **The price**: calibrating with the memory horizon gives $\tau_{\rm mem}\propto\sqrt n$, calibrating with the amount of change gives $T_{\rm em}\propto n$, and their ratio diverges with $n$ (a factor of $6.89$ and still growing), so **no rescaling can make both clocks uniform simultaneously**.

**Boundaries and conclusions.** Three limitations must be stated. First, the emergent time has **shape but no scale**: $T_{\rm em}\to n$ states that the emergent time is asymptotically equivalent to the external step count, while "how many seconds one step is" remains external input; this paper does not solve the scale problem. Second, at attainable sizes "time is constant" holds only to about $22\%$ ($T_{\rm em}/n=0.7776$ at $n=999$), and convergence is as slow as $\ln n/\sqrt n$. Third, two **guesses formed before measurement** have been refuted by measurement ($c\propto\lambda^{-1}$ gives $-0.577$; "the variant kernel runs away into freezing, $\Omega'\to0$" settles instead at a fixed point near $0.39$), and both are registered honestly as open items rather than used as evidence. One further separation must be preserved: **there is structure, there is no memory** — the joint distribution of the state matrix rejects full independence (row-sum variance is $1.94$–$2.03$ times the iid value, KS $p<10^{-4}$), yet two different prefixes become indistinguishable after continued evolution (exact permutation $p\ge0.3841$, none significant after Holm correction). It is precisely this that gives content to the claim that time must be *emergent* rather than *read off*: the present state carries zero bits about its own past. All numerical verification holds **only inside the SRE model**; any comparison with physical time is stated as a structural analogy and **not** as a numerical prediction.

**Keywords**: State–Relational Entropy (SRE); emergence of time; saturation law; rewriting rate; age law; memory horizon; incompatibility of two clocks; separation of structure and memory; exact permutation test; discrete closure law.

---

## 1. Introduction

### 1.1 Statement of the problem

"What is time" resists treatment because it disguises a **decision about which reading to take** as an **ontological query**. Every actual use of time does the same thing: choose a process believed to run steadily and mark events by its accumulated amount. The Newtonian move is to assume an *externally supplied* standard process; the relativistic move is to concede that every reading requires a *conversion rule*; this paper puts the act of selection itself on the table: **the character of time is not discovered, it is chosen**, and only what remains after that choice is computable.

To speak about this inside SRE one must first grant a fact already confirmed repeatedly: this dynamical machine carries no marking of "what moment it is now". It has no seconds, no frame rate, no list of external clocks. What it has is a step-by-step update loop and one probability assigned at each step. An observer outside sees the machine changing, and it is this change that is read as time. This paper writes that sentence as a formula and asks: **under what conditions does the time read out this way appear uniform?**

### 1.2 Definition clearing: three objects sharing one name

Synonyms must be cleared before any work begins — this project has paid several times already for words that carry two meanings (two $\delta$, two $\Pi_1$, two kinds of "opening", two kinds of "light", two kinds of "13.40 orders", two instances of $m$, and the inverted `dorm` of round 77). "Time" is the third case, and it has three members at once:

| Symbol | Name | Definition | How obtained |
|---|---|---|---|
| $t_{\rm ext}$ | external counting time | $n$ (evolution steps) | counting steps from **outside** the network |
| $\tau_{\rm mem}$ | memory intrinsic time | $\displaystyle\int^{n}\frac{dk}{H(k)}\propto\sqrt n$ (round 77, §8) | calibrating with the **memory horizon** $H$ |
| $T_{\rm em}$ | emergent time | $\displaystyle\sum_{k<n}\Omega(k)$ (this paper) | calibrating with the **amount of change** $\Omega$ |

None of the three equals or injects into another, and round 77 explicitly forbids taking $n$ as time **unconditionally**. This paper does not circumvent that discipline: §4 shows that $T_{\rm em}/n\to1$ holds **asymptotically but fails strictly at finite $n$**, and gives the exact order of the deviation, $O(\sqrt n\ln n)$. That is, this paper does not argue that "$n$ really is time after all"; it computes *when $n$ starts to behave like time, and how well*.

### 1.3 Contributions

1. Turning "time emerges" from a slogan into a **computable and falsifiable saturation law** (Theorem 2), with its zero-parameter origin exhibited.
2. Proving that the uniformity of time is not an assumption but a **corollary** (Theorem 3), together with its rate of convergence.
3. Splitting "constant as long as there is no phase transition" into two separate claims, **uniformity** and **time constant**, and adjudicating each (Theorems 5 and 6).
4. Producing a counter-intuitive price: internal time is **not unique** (Theorem 7); two internal clocks cannot coexist.
5. Completing the pre-registered 77→78 exit: separating "structure" from "memory" at the **joint** level (§8), and showing why this is exactly the reason time must emerge.

### 1.4 Structure

§2 preliminaries; §3 definition of emergent time and the saturation law; §4 asymptotic uniformity; §5 non-uniformity inside the network; §6 universality and phase transition; §7 incompatibility of two clocks; §8 separation of structure and memory; §9 falsifiable predictions; §10 discussion; §11 conclusion.

---

## 2. Preliminaries

### 2.1 The SRE evolution loop

The evolving body is a symmetric $\pm1$ matrix $M$ starting from $M_{1}=[[1]]$. At step $n$ (before appending row $n$, so $M$ is $n\times n$):

$$
E=|M^{2}|,\qquad
d_{ij}=n-\max(i,j),\qquad
\rho_{ij}=\frac{\lambda\,d_{ij}}{E_{ij}+1},
$$

$$
r_{ij}\;=\;\frac{1}{1+\rho_{ij}},\qquad
a_{ij}\;=\;1-r_{ij}\;=\;\frac{\rho_{ij}}{1+\rho_{ij}},
$$

$$
\mathrm{act}_{ij}=\big[\,\mathrm{rand}_{ij}\ge a_{ij}\,\big],\qquad
\text{act true means the historical value survives; otherwise the entry is permanently reset to }1 .
$$

Here $d_{ij}$ is the **age** of entry $(i,j)$. Since the early block is inherited literally (`new_M[:n,:n] = M`), a reset is permanent freezing — history is destroyed at most once, irreversibly.

### 2.2 Symbolic discipline: the name is inverted

The source variable `dorm` equals $r_{ij}=(1+\rho)^{-1}$ numerically, while `activate = rand >= p_matrix` gives $P(\text{history survives})=1-p_{\rm matrix}=r_{ij}$. Thus `dorm`, nominally "dormancy", is actually the **history-retention rate** — registered in round 77. This paper always speaks by the numbers and adopts the following symbols:

| Symbol | Source counterpart | Meaning |
|---|---|---|
| $r_{ij}$ | `dorm` | **retention rate** (probability that history continues) |
| $a_{ij}$ | `p_matrix` | **rewriting rate** (probability of being interrupted at this step) |
| $\Omega(n)$ | — | $\langle a_{ij}\rangle$, the **amount of change in the world** |

What the originating proposition calls "the dormancy/activation rates being observed as change in the world" reads in this notation as follows: **the "change" an observer reads off is $a$, complementary to the retention rate $r$; this complementary pair is precisely what we calibrate clocks with.**

### 2.3 Two pre-existing zero-parameter laws

**Proposition 1 (age-distribution law, round 77).**

$$
\#\{(i,j):d_{ij}=d\}=2(n-d)+1,\qquad d=1,\dots ,n,\qquad \textstyle\sum_{d}=n^{2}.
$$

Measured item-by-item error is identically $0$. The law **contains no dynamics**: whether the evolution is run, which seed, which $\lambda$, none of it matters. Corollaries: the median age ratio $d_{\rm med}/n\to1-1/\sqrt2=0.292893$; the mean $\bar d=(n+1)(2n+1)/(6n)\to n/3$.

**Proposition 2 (spectral law E5, round 77).**

$$
\big\langle |E_{ij}|^{2}\big\rangle_{\rm off}=n,\qquad
\big\langle |E_{ij}|\big\rangle_{\rm off}=\mathbb E|S_{n}|\;\approx\;\sqrt{2n/\pi},
$$

i.e. the off-diagonal activity field sits at the maximum-entropy (iid symmetric Rademacher) position; both exact moments deviate by less than $0.5\%$ for $n\ge400$.

Every quantitative result in this paper is synthesized from **these two laws** — that is where its zero-parameter character comes from.

### 2.4 Methodological discipline

Four standing rules are carried forward:

- **G6**: any new regularity must first be tested against external samples; every extrapolation beyond the model is explicitly labelled an analogy in §10.
- **G12 (discrete closure law)**: every crossing from "discrete" to "continuous" must be paid for by external input. This paper registers as its 16th instance.
- **G13**: three criteria for admissibility of a test (external-sample property / non-degeneracy / dependence on window width). In particular, if a statistic takes the same constant value in both populations it has no discriminating power and must be reported as "indistinguishable", **not** as "agreeing" (Appendix B invokes this to handle the quantiles).
- **Structural statements are not shields**: "finite-size effect" may explain a discrepancy, but a discrepancy of **order-of-magnitude** size must be acknowledged as containing something real (used in §6.2).

---

## 3. Emergent time

### 3.1 Definition

**Definition 3.1 (emergent time).**

$$
\boxed{\ \Omega(n)\;=\;\frac{1}{n^{2}}\sum_{i,j}a_{ij}(n),\qquad
T_{\rm em}(n)\;=\;\sum_{k=1}^{n-1}\Omega(k)\ }
$$

That is: the time worth of step $n$ equals the expected amount of change occurring in the world at that step, and the emergent time is its accumulation. The definition compresses the operationalist view of time (counting change with some process) into a directly computable quantity that requires no external unit.

### 3.2 Theorem 1: saturation

**Theorem 1 (saturation).** For every $\lambda>0$, $\Omega(n)$ rises monotonically to the limit $1$:

$$
\lim_{n\to\infty}\Omega(n)=1 .
$$

**Proof.** By Proposition 1 the typical age satisfies $d\sim c\,n$; by Proposition 2, $E\sim\sqrt{2n/\pi}$. Hence $\rho=\lambda d/(E+1)\sim\lambda c\,n^{1/2}\to\infty$ on almost all entries, so $a=\rho/(1+\rho)\to1$. $\square$

**Measurement** ($\lambda=0.8$, seed $1111$):

| $n$ | 1 | 10 | 50 | 100 | 200 | 400 | 600 | 800 | 999 |
|---|---|---|---|---|---|---|---|---|---|
| $\Omega$ | 0.285714 | 0.402329 | 0.624903 | 0.684338 | 0.742764 | 0.792840 | 0.817723 | 0.834268 | 0.846003 |
| $1-\Omega$ | 0.714286 | 0.597671 | 0.375097 | 0.315662 | 0.257236 | 0.207160 | 0.182277 | 0.165732 | 0.153997 |

Since the step-by-step $\Omega$ is a realized random quantity, monotonicity is judged on **block means** (blocks of $50$ steps): $0.701790,\,0.729869,\dots ,0.844839$, strictly non-decreasing across $18$ blocks. The self-consistency check (age-profile weighted vs. direct mean) differs by $2.2\times10^{-16}$.

Note that the gap is still $0.154$ at $999$ steps — saturation is remarkably slow, which is the subject of §4.

### 3.3 Theorem 2: the saturation law

**Theorem 2 (saturation law).** There is a $c=c(\lambda)$ with

$$
1-\Omega(n)\;=\;c(\lambda)\,\frac{\ln n}{\sqrt n}\,(1+o(1)).
$$

**Where the logarithm comes from.** Take the memory horizon $H=(E+1)/\lambda\propto\sqrt n$ (round 77, §8). The young shell with $d\lesssim H$ retains almost everything; its mass fraction is $\approx2H/n$. The old shell decays as $H/d$, and $\sum_{d}1/d$ supplies the logarithm. Their product gives $(\ln n)/\sqrt n$. The logarithm is therefore not fitted decoration; it is **the fingerprint of the harmonic tail**.

**Shape adjudication** (fitting $1-\Omega=c\,f(n)$ over $n\ge100$, maximum relative residual reported):

| $f(n)$ | $c$ | max relative residual |
|---|---|---|
| $n^{-1/2}$ | 3.990929 | 26.430% |
| $\ln n/\sqrt n$ | **0.694157** | **1.589%** |
| $n^{-0.4}$ | 2.248210 | 12.879% |
| $(\ln n)^{2}/\sqrt n$ | 0.116210 | 22.315% |

Pure power laws are decisively rejected; $\ln n/\sqrt n$ is the only admissible form, with residual $1.589\%$.

**Zero-parameter numerical prediction.** Using the age weights of Proposition 1 and the exact $|S_n|$ distribution of Proposition 2,

$$
\langle r\rangle_{\rm pred}
=\frac{1}{n^{2}}\sum_{d=1}^{n}\bigl(2(n-d)+1\bigr)\,
\mathbb E_{|S_{n}|}\!\left[\frac{K+1}{K+1+\lambda d}\right],
$$

**containing no fitted constant whatsoever**:

| $n$ | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 999 |
|---|---|---|---|---|---|---|---|---|---|---|
| measured $1-\Omega$ | 0.315662 | 0.257236 | 0.226762 | 0.207160 | 0.192979 | 0.182277 | 0.173042 | 0.165732 | 0.159378 | 0.153997 |
| zero-parameter prediction | 0.310462 | 0.254402 | 0.225136 | 0.205964 | 0.191990 | 0.181140 | 0.172357 | 0.165032 | 0.158786 | 0.153561 |
| relative deviation | 1.65% | 1.10% | 0.72% | 0.58% | 0.51% | 0.62% | 0.40% | 0.42% | 0.37% | 0.28% |

The deviation decreases monotonically to $0.28\%$–$1.65\%$. **This is the strongest quantitative result of the paper**: a non-trivial dynamical law is explained by two pre-existing zero-parameter laws down to the sub-percent level.

---

## 4. Theorem 3: asymptotic uniformity of the emergent time

**Definition 4.1 (relative step-to-step non-uniformity).**

$$
\eta(n)\;=\;\frac{|\Omega(n+1)-\Omega(n)|}{\Omega(n)} .
$$

It measures whether consecutive steps are equivalent. Time is uniform if and only if $\eta\to0$.

**Theorem 3 (asymptotic uniformity).**

$$
\eta(n)\;=\;\frac{c\,(\tfrac12\ln n-1)}{n^{3/2}\,\Omega(n)}\,(1+o(1))
\;\propto\;\frac{\ln n}{n^{3/2}}\;\longrightarrow\;0 .
$$

**Proof.** From Theorem 2, $\Omega=1-c\ln n\cdot n^{-1/2}$; differentiating termwise gives $d\Omega/dn=c(\tfrac12\ln n-1)n^{-3/2}$. Dividing by $\Omega\to1$ yields the claim. $\square$

The point is that this follows **by differentiating the saturation law**, not by a second fit; $c$ was already fixed in Theorem 2, so the prediction here has zero free parameters.

**Measurement** ($\eta$ from a $\pm10$ smoothed difference quotient, suppressing the realization noise of $\Omega$):

| $n$ | 50 | 100 | 200 | 400 | 600 | 800 | 980 |
|---|---|---|---|---|---|---|---|
| $\eta$ measured | $4.227\!\times\!10^{-3}$ | $1.395\!\times\!10^{-3}$ | $5.469\!\times\!10^{-4}$ | $2.378\!\times\!10^{-4}$ | $1.108\!\times\!10^{-4}$ | $8.878\!\times\!10^{-5}$ | $6.102\!\times\!10^{-5}$ |
| $\eta$ predicted | $3.004\!\times\!10^{-3}$ | $1.321\!\times\!10^{-3}$ | $5.449\!\times\!10^{-4}$ | $2.184\!\times\!10^{-4}$ | $1.270\!\times\!10^{-4}$ | $8.613\!\times\!10^{-5}$ | $6.542\!\times\!10^{-5}$ |
| ratio | 1.407 | 1.055 | 1.004 | 1.089 | 0.873 | 1.031 | 0.933 |

$\eta$ falls by a factor of $69.3$, and the ratio stays inside $[0.873,1.407]$ throughout. **This is the form in which "the time perceived by humans is constant" becomes a theorem here**: it is not assumed, it is computed — down to the number expressing *how non-uniform it still is*.

**Corollary 4.2 (emergent time vs. step count).**

$$
T_{\rm em}(n)\;=\;n-O(\sqrt n\,\ln n).
$$

Measured $T_{\rm em}/n=0.5734,\,0.7077,\,0.7776$ at $n=100,400,999$. This corollary is the strict version of the round-77 discipline: **do not take $n$ as time unconditionally**; only after designating "calibrate with the amount of change" does $n$ become time asymptotically, and even then with a sublinear error term too large to ignore.

---

## 5. Theorem 4: differential ageing inside the network

Uniformity of the aggregate does not mean uniformity everywhere inside. Fixing the current step $n$ and scanning the age $d$ of entries:

| $n$ | $a(d=1)$ | $a(d=n/8)$ | $a(d=n/4)$ | $a(d=n/2)$ | $a(d=3n/4)$ | half-life age $H_{\rm eff}$ | $H_{\rm eff}/\sqrt n$ |
|---|---|---|---|---|---|---|---|
| 100 | 0.139768 | 0.596166 | 0.729099 | 0.824956 | 0.886612 | 9 | 0.9000 |
| 400 | 0.083088 | 0.728347 | 0.827560 | 0.912367 | 0.929344 | 17 | 0.8500 |
| 999 | 0.058931 | 0.804968 | 0.884809 | 0.940564 | 0.957750 | 23 | 0.7277 |

(The last sample in each row, $d=n$, is a single entry, the diagonal corner, where $E_{ii}=n$ holds exactly and the rewriting rate is pinned at $\lambda n/(n+1+\lambda n)\approx0.444$; it does not follow the trend of its shell and counts as an **atypical singleton** under G13, so it is excluded from the trend.)

**Theorem 4 (differential ageing).** At a single instant, the expected rewriting rate of an entry rises monotonically with its own age: newborn entries are nearly static ($a\lesssim0.06$), old entries are nearly rewritten at every step ($a\gtrsim0.95$). Hence **there is no unique local rate of time inside the network**.

**Why the aggregate still becomes uniform.** By Proposition 1 the mass weights $2(n-d)+1$ depend only on $d/n$, i.e. the age profile is **self-similar** under stretching by $n$. All shells move along one and the same curve, and the weighting happens to compress the residual $n$-dependence down to $\ln n/\sqrt n$. In other words: **uniformity is an averaging effect brought by self-similarity, not a property of any one place.**

---

## 6. What stays constant and what does not

The originating proposal benchmarks against the speed of light: "constant as long as there is no phase transition". That sentence hides an ambiguity that must be opened up.

### 6.1 Theorem 5: the value of $\lambda$ does not move the limit

**Definition 6.1.** Call

$$
\Omega_{\infty}\;=\;\lim_{n\to\infty}\Omega(n)
$$

the **time constant** of this dynamics: how much internal time one step is worth.

**Theorem 5 (numerical universality).** The value of $\lambda$ does not change $\Omega_{\infty}$; it changes only the **speed** of approach, $c(\lambda)$.

**Measurement** ($\lambda\in\{0.2,\dots ,3.0\}$, a $15$-fold span):

| $\lambda$ | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 | 1.5 | 2.0 | 3.0 |
|---|---|---|---|---|---|---|---|---|
| $\Omega(199)$ | 0.502787 | 0.627409 | 0.698311 | 0.741054 | 0.771403 | 0.822181 | 0.852601 | 0.885878 |
| $\Omega(399)$ | 0.574492 | 0.694596 | 0.753735 | 0.792215 | 0.817939 | 0.859558 | 0.883932 | 0.913126 |
| $\Omega(799)$ | 0.640836 | 0.749044 | 0.801660 | 0.833995 | 0.856051 | 0.890282 | 0.910422 | 0.933125 |
| $c(\lambda)$ | 1.3896 | 1.0121 | 0.8148 | 0.6928 | 0.6071 | 0.4694 | 0.3881 | 0.2946 |

$\Omega$ is monotone increasing in $\lambda$ (at fixed $n$) and monotone increasing in $n$ (at fixed $\lambda$); both hold, hence all $\lambda$ approach **the same target**.

**Why it looks like this.** $\Omega_{\infty}=1$ is a **saturation value**, and saturation values carry no coupling strength: however large or small $\lambda$ is, $\rho\sim\lambda n^{1/2}\to\infty$ still holds, and the ceiling of $a=\rho/(1+\rho)$ is $1$. This is the same structure as "the bound $|v|\le c$ does not depend on the specific strength of the interaction".

**Open item (registered honestly).** For the approach-speed constant $c(\lambda)$, a naive asymptotic argument gives $c\propto\lambda^{-1}$ (the gap is proportional to the memory horizon, hence to $1/\lambda$). **Measurement rejects this guess**: the slope of $\ln c$ against $\ln\lambda$ is $-0.5549$ (window $100$–$399$), $-0.5914$ ($200$–$799$) and $-0.5769$ ($100$–$799$). The direction agrees with a correction term $\propto\ln\lambda/\ln n$ (the slope drifts weakly toward $-1$ as the window is pushed outward), but $1/\ln n$ decays too slowly for finite windows to reach $-1$. **This item is registered as open and forbidden as evidence.**

### 6.2 Theorem 6: the form of the rule moves the limit

**Controlled variant.** Only the denominator is changed to $(E+1)^{2}$; nothing else is altered (same $\lambda=0.8$):

$$
\rho'_{ij}=\frac{\lambda\,d_{ij}}{(E_{ij}+1)^{2}} .
$$

| $n$ | control $\Omega$ | variant $\Omega'$ | gap |
|---|---|---|---|
| 100 | 0.684338 | 0.344778 | 0.339559 |
| 200 | 0.742764 | 0.363154 | 0.379610 |
| 400 | 0.792840 | 0.375944 | 0.416896 |
| 600 | 0.817723 | 0.381696 | 0.436027 |
| 800 | 0.834268 | 0.385128 | 0.449140 |
| 1000 | 0.846201 | 0.386770 | 0.459431 |
| 1099 | 0.850685 | 0.387804 | 0.462881 |

The gap widens monotonically to $0.4629$ and is still widening, hence **the two groups cannot share a limit**. Meanwhile $\langle E\rangle$ in the variant group is nearly identical to the control ($27.4251$ vs. $27.4397$), showing that the $E$-field is still governed by Proposition 2 and that no runaway has occurred; the system has simply landed on **another fixed point**.

**Theorem 6 (phase transition).** The **form** of the update rule determines the time constant $\Omega_{\infty}$; the **value** of the coupling parameter $\lambda$ does not change it.

$$
\Omega_{\infty}=1.0000\ \ (\rho=\lambda d/(E+1))\qquad
\rightsquigarrow\qquad
\Omega_{\infty}\approx0.390\ \ (\rho'=\lambda d/(E+1)^{2})
$$

(the latter interval $[0.388,0.391]$ comes from the last point $0.387804$ plus a geometric remainder bound $\le0.0027$).

**Verdict.** "Constant as long as there is no phase transition" translates here into an **executable criterion**:

- **Uniformity** (existence of $\Omega_{\infty}$) holds for every tested $\lambda$ and under both rules ⇒ it is robust and can emerge in many independent ways;
- **The time constant** (the value of $\Omega_{\infty}$) is a function of the rule's **form** ⇒ changing the form changes it. Sweeping $\lambda$ by a factor of $15$ does not budge it; squaring one denominator does.

### 6.3 A guess that was refuted (discipline requires it be written down)

Before running anything, the expectation was that the variant kernel would **run away into freezing** (less rewriting ⇒ $M$ biased toward $+1$ ⇒ larger $E$ ⇒ larger squared denominator ⇒ even less rewriting ⇒ $\Omega'\to0$). **This guess was wrong.** Measurement shows the $E$-field pinned at $\sqrt{2n/\pi}$ by Proposition 2 (which also explains why $\langle E\rangle$ is nearly identical in both groups); no positive feedback is established, and the system settles at $\Omega'\approx0.39$ rather than $0$.

The refutation has value of its own: it shows that a phase transition changes the **value** of the time constant rather than "switching time off". A world with $\Omega_{\infty}=0.39$ still has a uniform time; each step is merely worth about sixty per cent less internal duration.

### 6.4 The exact scope of the light-speed analogy

The analogy must have stated limits, otherwise it becomes a universal pass.

**Where it holds.** Both quantities are **saturation or ceiling values**, hence insensitive to base-level coupling parameters (here $\lambda$; there the state of motion of the source); both are **structural constants** (here the form of the update rule; there the metric structure of spacetime), and changing the structure changes the constant.

**Where it fails (three items, not to be extrapolated).** First, $\Omega_{\infty}$ here is **dimensionless** (a fraction of entries rewritten per step), whereas $c$ **carries dimensions** and requires a unit system; they are not the same kind of number. Second, the other side of the analogy — the *scale* of time (seconds) — is **still absent** here ($T_{\rm em}\to n$ settles the shape only). Third, the invariance of $c$ rests on the experimental basis of Lorentz invariance, whereas $\Omega_{\infty}$ here has been verified only in two controlled comparisons inside a model. **Nothing in this paper may be used to assert any numerical conclusion about the physical speed of light.**

---

## 7. Theorem 7: two clocks cannot coexist (time is not unique)

Round 77 calibrated with the memory horizon and obtained $\tau_{\rm mem}(n)=2\lambda\sqrt{\pi/2}\,\sqrt n=2.005303\sqrt n$, with the verdict "this clock decelerates continuously". This paper calibrates with the amount of change and obtains $T_{\rm em}\propto n$. Both are readings taken **inside** the network.

| $n$ | 50 | 100 | 200 | 400 | 600 | 800 | 999 |
|---|---|---|---|---|---|---|---|
| $\tau_{\rm mem}$ | 14.1796 | 20.0530 | 28.3593 | 40.1061 | 49.1197 | 56.7185 | 63.3815 |
| $T_{\rm em}$ | 25.2648 | 58.0257 | 129.6670 | 283.8656 | 445.1452 | 610.4507 | 777.6977 |
| $T_{\rm em}/\tau_{\rm mem}$ | 1.7818 | 2.8936 | 4.5723 | 7.0779 | 9.0625 | 10.7628 | 12.2701 |
| $T_{\rm em}/n$ | 0.505296 | 0.580257 | 0.648335 | 0.709664 | 0.741909 | 0.763063 | 0.778476 |

**Theorem 7 (incompatibility).** The ratio $T_{\rm em}/\tau_{\rm mem}$ diverges with $n$ (a measured factor of $6.89$ and still growing). Therefore no rescaling exists under which both intrinsic clocks are uniform simultaneously; "time" is not a property the system carries, but a derived quantity obtained **after a clock process has been chosen**.

**Both tend to uniformity, but at different rates:**

| $n$ | 100 | 400 | 980 |
|---|---|---|---|
| $\eta(T_{\rm em})$ | $1.395\times10^{-3}$ | $2.378\times10^{-4}$ | $6.102\times10^{-5}$ |
| $\eta(\tau_{\rm mem})=1/(2n+2)$ | $4.963\times10^{-3}$ | $1.248\times10^{-3}$ | $5.098\times10^{-4}$ |
| ratio | 0.28 | 0.19 | 0.12 |

$\eta(T_{\rm em})\propto\ln n/n^{3/2}$ while $\eta(\tau_{\rm mem})\propto1/n$: **calibrating with the amount of change pushes non-uniformity one order further down.** This is where the sentence of §1.1 finally lands: uniform time is observed because observers implicitly use the reading "how much happened in the world", not the memory-horizon reading.

---

## 8. Where the past is: separating structure from memory

### 8.1 There is structure (full independence is rejected)

Taking the joint null hypothesis to be "entries are iid" is the **wrong null** — the update rule itself (symmetry, columnwise products, permanent freezing on reset) manufactures correlations even in the total absence of historical memory. Two questions are therefore adjudicated separately.

**T5a (structure).** Each real history is compared with a **completely iid symmetric $\pm1$ random matrix**. Two scales ($n=150$, $n=300$), $K=8$ histories, $R=40$ surrogates:

| statistic | $n=150$ real | $n=150$ iid | gap$/\sigma$ | $n=300$ real | $n=300$ iid | gap$/\sigma$ |
|---|---|---|---|---|---|---|
| $\langle|E|\rangle_{\rm off}$ | $9.8442\pm0.1274$ | $9.7549\pm0.1045$ | 0.70 | $13.8493\pm0.0767$ | $13.7983\pm0.0681$ | 0.66 |
| fraction of $+1$ | $0.5020\pm0.0059$ | $0.5016\pm0.0039$ | 0.07 | $0.5013\pm0.0025$ | $0.5007\pm0.0019$ | 0.27 |
| spectral radius$/\sqrt n$ | $1.9881\pm0.0419$ | $1.9606\pm0.0373$ | 0.66 | $2.0027\pm0.0186$ | $1.9798\pm0.0208$ | 1.23 |
| **row-sum variance$/n$** | $\mathbf{1.9446\pm0.1060}$ | $\mathbf{1.0170\pm0.1200}$ | **8.75** | $\mathbf{2.0302\pm0.0740}$ | $\mathbf{1.0019\pm0.0957}$ | **13.89** |

The **marginal** layer of the $E$-field (mean, $\sigma$, sign fraction, spectral radius) agrees with iid, consistent with Proposition 2; but the **row-sum variance** is $1.94$–$2.03$ times the iid value at both scales, with KS $p<10^{-4}$ ⇒ **full independence is rejected**: entries within a row are co-ordinated, so the joint is not the product of the marginals.

### 8.2 There is no memory (prefixes are indistinguishable)

**Experimental design.** Take two prefixes with **nothing in common** (different seeds, each run to step $150$; the two differ in $48.50\%$ of entries). From each prefix run $G=8$ continuations with mutually different random streams up to step $300$, giving $2G=16$ terminal states. $H_{0}$: these $16$ states are exchangeable. **Exact permutation test** (enumerating all $C(16,8)=12870$ splits):

| statistic | group A | group B | $|\text{difference}|/\sigma_{\rm pooled}$ | permutation $p$ |
|---|---|---|---|---|
| $\langle|E|\rangle_{\rm off}$ | $13.8645\pm0.0731$ | $13.8676\pm0.0517$ | 0.050 | 0.9223 |
| $\sigma(|E|)$ | $10.5091\pm0.0692$ | $10.5015\pm0.0370$ | 0.141 | 0.8222 |
| row-sum variance$/n$ | $1.9720\pm0.0971$ | $1.9734\pm0.0871$ | 0.015 | 0.9775 |
| fraction of $+1$ | $0.5009\pm0.0017$ | $0.5018\pm0.0021$ | 0.453 | 0.3841 |
| spectral radius$/\sqrt n$ | $1.9931\pm0.0304$ | $2.0047\pm0.0348$ | 0.361 | 0.4920 |

None significant after Holm–Bonferroni correction.

**T5b (no trace).** Two entirely different first halves become **indistinguishable** after the second half.

The limitation must be stated: the test is carried out on $5$ scalar statistics and is **not** a general proof about mutual information. What it establishes is that on these $5$ readings a shared prefix leaves no detectable trace.

### 8.3 Why time must be emergent

Putting §8.1 and §8.2 together yields the single most important sentence of this paper:

> **The present state carries zero bits about its own past, so there is no time marker inside "now" that could be read off; time can only be accumulated, never read — and that is the precise meaning of "time emerges".**

This continues the same thread as the $\le1$ bit of round 74, the $=0$ bit of round 76 and the exact $0$ bit on the diagonal of round 77, and upgrades it to the **joint distribution of the entire state matrix**: having structure does not imply having memory, and both can hold at once; it is precisely "no memory" that prevents time from being recovered from the state. Round 76 reached the same conclusion from the **target side** (the vibrational-period axis runs entirely through the mass $\mu$; the graph side contributes $0$), and round 77 from the **dynamics side** (intrinsic time has shape but no scale); this paper arrives at it a third time from the **joint-distribution side**. Three independent paths converge on one place — and that convergence itself carries information.

---

## 9. Falsifiable predictions and checklist

Each item below can be used to reject this paper directly with the same script:

| # | prediction | criterion | current measurement |
|---|---|---|---|
| P1 | $1-\Omega$ must contain $\ln n$ | pure power law significantly worse than $\ln n/\sqrt n$ | $26.43\%$ vs $1.59\%$ |
| P2 | the zero-parameter synthesis holds | prediction within $2\%$ of measurement | $0.28\%$–$1.65\%$ |
| P3 | $\eta\to0$ with ratio near $1$ | $\eta/\eta_{\rm pred}\in[0.5,2]$ | $[0.873,1.407]$ |
| P4 | $\Omega_{\infty}$ independent of $\lambda$ | $\Omega$ monotone in $\lambda$ and in $n$ | holds ($8$ values of $\lambda$) |
| P5 | changing rule form moves the limit | gap monotone and $>0.30$ | $0.4629$ |
| P6 | joint has structure | row-sum variance gap $>3\sigma$ and KS $p<0.01$ | $8.75\sigma$ / $13.89\sigma$, $p<10^{-4}$ |
| P7 | joint has no memory | nothing significant after Holm | $\min p=0.3841$ |
| P8 | two clocks cannot coexist | ratio diverges monotonically with $n$ | $1.78\to12.27$ |

**The easiest to overturn is P2**: should the age-law × spectral-law synthesis fail to explain things to better than a percent under another $\lambda$ or another update rule, the whole "zero-parameter" claim collapses.

---

## 10. Discussion

### 10.1 Relation to neighbouring concepts

The thesis of this paper passes alongside several familiar discussions in the philosophy of time, but borrows **no** quantitative result from any of them:

- **Relationalism / timeless ordering** (Barbour-style "time does not exist"): this paper agrees that "time is not in the state" but rejects the inference to non-existence; it supplies instead a **computable substitute** $T_{\rm em}$ whose uniformity is a corollary, not an assumption.
- **Thermal time hypothesis** (Connes–Rovelli style: time supplied by the modular flow of a state): $\Omega$ here is likewise a time specified by "how the state changes", but this paper **measures its saturation law and the convergence order of its non-uniformity**, which thermal-time constructions usually do not provide.
- **Page–Wootters style** (taking a subsystem as clock): Theorem 7 is a **limitation** on that idea — choosing a different subsystem may yield an incompatible clock whose ratio diverges.

All are registered as **structural analogies only** and are not used as evidence under G6.

### 10.2 Accounts against the preceding rounds of this project

| round | conclusion | relation to this paper |
|---|---|---|
| 76 | vibrational-period axis: graph side $0$ bit, $\mu$-only $0.07\%$; there are steps but no seconds | this paper inherits "the scale must still be supplied externally" |
| 77 | $\tau_{\rm mem}\propto\sqrt n$; exact $0$ bit on the diagonal; $\varepsilon$ demoted to a window function | this paper takes $\tau_{\rm mem}$ as the second clock, from which the non-coexistence follows |
| this paper | $T_{\rm em}\propto n$; saturation law; universality / phase transition; structure vs memory | completes the pre-registered 77→78 exit |

**Still unsolved**: the scale. $T_{\rm em}\to n$ shows only that the emergent time is asymptotically equivalent to the step count; "how many seconds is one step" remains external input. The gap identified in rounds 76 and 77 is not narrowed here.

### 10.3 Guiding analogy

One sentence for the non-specialist: **time is uniform not because the universe carries a standard clock that happens to run steadily, but because the quantity "how much the world changed" saturates on its own; once saturated, counting change with it yields uniform time. We measure a constant because the underlying rule has not undergone a phase transition — exactly as the speed of light is constant because spacetime structure has not undergone one.**

### 10.4 View from the discrete closure law (G12, instance 16)

- **Given (discrete side, closed)**: the distribution of $d$, the $n^{2}$ weights, the distribution of $|S_{n}|$, the symmetry ⇒ hence the shape $\ln n/\sqrt n$ and the form of $T_{\rm em}$.
- **Not given (continuous side, external input required)**: the physical unit corresponding to $\Omega_{\infty}$ (seconds), and why one *ought* to calibrate with $\Omega$ rather than $\tau_{\rm mem}$ — the latter is a choice on the observer's side, which the dynamics cannot answer.

---

## 11. Conclusion

All seven verdicts pass:

| label | verdict | result |
|---|---|---|
| T1 | definition of emergent time and saturation | pass (self-consistency $2.2\times10^{-16}$) |
| T2 | saturation law $\ln n/\sqrt n$ + zero-parameter prediction | pass (residual $1.589\%$, deviation $\le1.65\%$) |
| T3 | relative step non-uniformity $\to0$ | pass ($\eta/\eta_{\rm pred}\in[0.873,1.407]$) |
| T4 | single-member clock accelerates with its own age | pass |
| T5a / T5b | structure / no memory | pass ($8.75\sigma$–$13.89\sigma$; $\min p=0.3841$) |
| T6a / T6b | $\lambda$ does not move the limit / rule form does | pass (gap $0.4629$) |
| T7 | two clocks cannot coexist | pass (ratio grows by $6.89$ and diverges) |

Together with three open items ($c\propto\lambda^{-1}$ rejected; $T_{\rm em}/n$ reaches only $0.7776$ at attainable sizes; the scale remains unsolved) and two guesses formed before measurement that were refuted, the balance sheet of this paper is clear:

**(Established)** Time is not an external parameter; it is a quantity accumulated **as part of** an internal process. Its uniformity is not an assumption but a corollary of a saturation law, and that saturation law is explained in full by two pre-existing zero-parameter laws down to the sub-percent level.

**(Adjudicated)** "Constant as long as there is no phase transition" splits into two: uniformity holds under every tested parameter and rule (robust), while the time constant moves only when the *form* of the update rule changes — which is the strict location of the phase transition.

**(Price paid)** Time is not unique: two equally legitimate internal readings give incompatible times whose ratio diverges, and the clock of every single member inside the network is non-uniform. Using "how much the world changed" as the clock is a choice, not a discovery.

**(Still missing)** The scale. This paper settles the shape and does not settle "how many seconds is one step" — which is the same gap registered in rounds 76 and 77 ($L_{4}$, the assignment rule), projected onto the problem of timekeeping.

**(And explained)** Why time must be emergent rather than read off: the present state carries zero bits about which history it walked.

---

## Appendix A　Recomputation checklist

| item | script | key quantities |
|---|---|---|
| saturation law and all verdicts | `code/_time_emergence.py` (PART 0–8) | $\Omega(n)$, $c$, $\eta$, $T_{\rm em}$ |
| supplementary probe ($\Omega$ first used as target) | `code/_probe_time78.py` | initial shape judgement for $1-\Omega$ |
| T6 follow-up | `code/_probe_time78b.py` | two windows for $c(\lambda)$; long-run trend of the variant kernel |
| reference implementation of the loop | `code/sim_p.py` | the single authoritative version of the update rule |
| archived results | `code/_time_emergence.json` | intermediate data for all verdicts |

Recompute: `python code/_time_emergence.py` (about $2$ minutes, EXIT=0).

---

## Appendix B　Honest boundaries

1. **One guess that preceded measurement**: $c\propto\lambda^{-1}$ is rejected (measured slope $-0.577$). Every statement involving $c(\lambda)$ is a registration, **not a conclusion**.
2. **A second such guess**: "the variant kernel runs away into freezing, $\Omega'\to0$" is refuted; it settles at a fixed point near $0.39$. The original guess is preserved in §6.3.
3. **Limited attainable precision**: at $n=999$, $T_{\rm em}/n=0.7776$, i.e. "time is constant" holds to only about $22\%$ at attainable sizes. Any reading that equates the results here with "physical time is strictly uniform" is a misreading.
4. **Statistics with no discriminating power**: the $50\%$ and $90\%$ quantiles of the $E$-field take identical values in both populations ($8$ and $20$; $12$ and $28$), giving gap$/\sigma=\infty$ with KS $p=1.0000$. Under G13 such statistics must be reported as "indistinguishable" and **must not** be counted as agreement. They are excluded from the tables above.
5. **Limit of reach of T5b**: the permutation test is performed on $5$ scalar statistics only and is not a general proof about mutual information. A stronger version would require vector-valued or spectral two-sample tests.
6. **$\lambda=0.8$ and $\sqrt{2/\pi}=0.797885$ differ by $0.265\%$**: registered in round 77 as a conjecture awaiting test. Since $\lambda$ currently has no independent calibration, this paper does **not** use that proximity as an argument (G6; "too accurate" = the fingerprint of circularity).
7. **$\varepsilon=0.183246$ remains a window function** (the verdict of round 77 §7 is not altered here): the $\Omega$ used in this paper is defined step by step and involves no window.
8. **The scale is absent**: stated a third time — $T_{\rm em}$ has shape, not seconds.

---

## Appendix C　Analogy index

| analogy | purpose | failure point |
|---|---|---|
| speed of light $c$ | why a saturation value is insensitive to coupling strength | $c$ carries dimensions and requires a unit system; $\Omega_{\infty}$ here is dimensionless and derives no physical dimension; the two cannot be inferred from each other |
| several people each counting by their own heartbeat | why clocks belonging to different processes cannot coexist | — |
| harmonic tail | where $\ln n$ comes from | only an integral approximation; the constant still has to be fixed numerically |

---

## Appendix D　References

1. This project: *The dormancy/activation clock: zero-parameter laws, zero-bit branches and intrinsic time* (round 77) — Proposition 1 (age law), Proposition 2 (diagonal closed form), E5 (spectral law), source of $\tau_{\rm mem}$.
2. This project: *The vibrational-period axis: definition of time and the isotope criterion* (round 76) — the topological definition of frequency $\Delta\lambda=|\lambda_{1}-\lambda_{2}|$, and the verdict "steps but no seconds".
3. This project: *Applied layer, ninth run: the general form of Proposition U* (round 74) — methodological source of the information bound $\le1$ bit.
4. This project: *Applied layer, tenth run: ascending to $L_{3}$* (round 75) — source of the discipline "range verdicts precede fitting verdicts".
5. `code/sim_p.py` — the single authoritative implementation of the evolution loop.
6. J. B. Barbour, *The End of Time* — conceptual neighbour (analogy only; no quantitative result borrowed).
7. A. Connes and C. Rovelli, *Von Neumann algebra automorphisms and time-thermodynamics relation in generally covariant quantum theories*, Class. Quantum Grav. **11** (1994) 2899 — prototype of the thermal-time hypothesis (analogy only).
8. D. N. Page and W. K. Wootters, *Evolution without evolution*, Phys. Rev. D **27** (1983) 2885 — prototype of taking a subsystem as clock; Theorem 7 here is a limitation on it.
