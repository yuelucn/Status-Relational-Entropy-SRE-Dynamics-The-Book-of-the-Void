# How Does Time "Grow" Itself?
## ——A Plain-Language Account Based on the Status–Relational–Entropy (SRE) Framework

**Emergence of Time in the Status–Relational–Entropy Framework — A Plain-Language Version**

Version: 1.0 (plain-language rewrite)
Original technical version dated: 2026-10-04

> **Note**: This article is a **plain-language rewrite** of *The Emergence of Time in the SRE Framework*, aimed at readers with a general university science-and-engineering background (a little calculus and probability is enough). The technical version keeps all formulas, numbers, and reproducible scripts; this version replaces most of its project-internal jargon with everyday language and analogies, while preserving every core conclusion and every data table.

### Resources and Reproducibility
This framework is built on an information-dynamics model called "Status–Relational–Entropy (SRE)". All theoretical material and simulation code are archived openly on Zenodo; the scripts used in this article are listed at the end and can be re-run with one command.

---

## Abstract (in plain words)

When we normally say "time," we are secretly mixing up three different meanings. This article uses a model called SRE to make the business of "time" clear: in this model, the world is a digital network that keeps rewriting itself; rather than asking "what time is it now," it is better to ask "how much did this network change at each step." Add up that "amount of change," and you get a kind of **emergent time**.

We prove seven things:

1. The world's rate of change slowly "saturates" toward nearly 100% — the older the world, the more nearly every step changes something.
2. How far it still is from saturation follows a clear curve: the gap ≈ c·(ln n)/√n. And this curve can be predicted, **without any fitting**, directly from two even simpler laws, with an error under 2%.
3. As a result, time *looks* uniform — this is a **consequence**, not an assumption.
4. But the interior of the network is not uniform: newborn cells barely move, old cells move at almost every step, so every little cell has its own "clock."
5. No matter whether you speed the model up or slow it down (parameter λ spanning 15×), the final "time constant" stays the same; but the moment you change the "shape" of the rule (squaring the denominator), it jumps to another value.
6. The model contains two kinds of clocks that are both legitimate, yet their speed ratio keeps widening forever and never lines up — **time is not a built-in property of the world; it is a product of the choice of what you use to keep time.**
7. The most crucial point: the current state carries *zero bits* of information about which path it "took in the past." In other words, time cannot be *read out* from the present state; it can only be *accumulated* step by step — and that is exactly what "time emerges" means.

**Honest boundary**: We have only solved the "shape" of time (its form), not "how many seconds one step equals" (its scale). Every comparison in this article to real physical time is only a **structural analogy**, not a numerical prediction.

---

## 1. Time Is Not Discovered — It Is "Chosen"

### 1.1 Three things that are all called "time"

Everywhere time is actually used, the same thing is really happening: **first pick a process you believe runs steadily, then use its accumulated amount to label events.** Newton's approach was to assume an external standard clock by default; relativity admits that each reading needs a conversion rule. This article puts that "clock-picking" action out in the open:

> **The nature of time is not discovered; it is selected.** Only after selection does the rest become computable.

In the SRE model, the word "time" had previously mixed up three different meanings, which must be separated first, or the discussion is meaningless:

| Symbol | Name | How obtained | Meaning |
|---|---|---|---|
| t_ext | External counting time | Stand outside the network and count "how many steps" n have passed | Pure step count |
| τ_mem | Memory intrinsic time | Calibrate the clock by "how far memory can reach," ≈ 2.005·√n | Time by memory depth |
| T_em | Emergent time | Calibrate the clock by "how much the world changed," ≈ n | Time by accumulated change |

The three are not equal to one another. The point of this article is to prove: T_em / n approaches 1, but **is strictly not equal to 1 at any finite number of steps** — that is, we are not defending "n is time," but computing "from when does n start to look like time, and to what degree."

### 1.2 What this article does

It turns "time emerges" from a slogan into a specific law that is **both computable and falsifiable by experiment**, and answers: under what conditions does the time read this way behave uniformly?

---

## 2. What This "World Model" Looks Like

SRE's evolving body is a symmetric digital network (a matrix) whose entries take only +1 or −1. It starts from the smallest 1×1 grid; at each step it grows one row and one column, eventually becoming n×n.

What happens at each step? For every little cell (i,j) in the grid:

- It has an **age d**: how many steps have passed since it was last modified.
- There is a corresponding **activity E** (a measure of the current "busyness" of the whole network, roughly proportional to √n).
- From these we compute a **rewrite probability a**: `a = (λ·d)/(E+1) divided by (1 + itself)`. The older it is and the busier the network, the more likely it is to be rewritten.
- Throw a random number once: if the random number is larger than a, the cell is **permanently reset to +1** (its history is erased once, and cannot be recovered); otherwise it keeps its old value.

Intuition: this is a machine whose "memory ages." Old cells are easily overwritten; new cells are temporarily safe.

To keep things clear, we unify two names (the model source code once mistakenly called the retention rate the "dormancy rate"; here we correct it to match the actual numbers):

- **Retention rate r**: the probability that this cell "preserves its history" at this step.
- **Rewrite rate a**: the probability that this cell "gets changed" at this step (a and r are complementary, a + r = 1).

**The "world change" that the observer reads is exactly a.** This article uses a to keep time.

---

## 3. Emergent Time: Keeping Time by "How Much the World Changed"

Let Ω(n) be, at step n, the **average fraction of cells in the whole network that got rewritten**. Then adding up Ω at every step gives the **emergent time** T_em:

> **How much "time" step n is worth = the expected amount of change that happened in the world at that step; emergent time = the accumulation of those amounts of change.**

This definition compresses the operationalist view of time — "use some process to count change" — into a quantity that can be computed directly, and needs no external units (it does not depend on "seconds").

---

## 4. Conclusion 1: The Rate of Change "Saturates" (Theorem 1)

**Theorem 1**: No matter how fast or slow you set the model (parameter λ > 0), Ω(n) rises monotonically and eventually tends toward 1 (that is, 100% of cells change at every step).

**Intuition**: As the world ages, most cells are "ancient," with large age d, so the rewrite probability a approaches 1. The saturation value 1 does not depend on any specific parameter — just as no matter how hard you push, an object's speed limit does not depend on how hard you push.

Measured (λ=0.8):

| n | 1 | 10 | 50 | 100 | 200 | 400 | 600 | 800 | 999 |
|---|---|---|---|---|---|---|---|---|---|
| Ω (rate of change) | 0.286 | 0.402 | 0.625 | 0.684 | 0.743 | 0.793 | 0.818 | 0.834 | 0.846 |
| 1−Ω (gap) | 0.714 | 0.598 | 0.375 | 0.316 | 0.257 | 0.207 | 0.182 | 0.166 | 0.154 |

Note: even at 999 steps, the gap is still 0.154 — saturation is remarkably slow. The next section explains what shape this gap takes.

---

## 5. Conclusion 2: The Saturation Law — Why the Gap Is ln n / √n (Theorem 2)

**Theorem 2**: There exists a parameter-dependent constant c such that

> **Gap 1 − Ω(n) ≈ c · (ln n) / √n**

**Why does ln appear?** Split the grid into layers by age: the young layer (age smaller than the memory depth) is almost entirely preserved, occupying roughly 2·(memory depth)/n of the total; the old layer decays as "memory depth / age," and summing 1/age from 1 to n gives ln n. Multiplying the two gives (ln n)/√n. So ln n is not a decorative afterthought — it is the fingerprint of a "harmonic tail."

**Shape judgment** (fit for n≥100, reporting the maximum relative error):

| Candidate curve | Fit constant c | Max relative error |
|---|---|---|
| Pure power law n^(−1/2) | 3.99 | **26.4%** (clearly fails) |
| **ln n / √n** | **0.694** | **1.59%** (the only one that passes) |
| n^(−0.4) | 2.25 | 12.9% |
| (ln n)² / √n | 0.116 | 22.3% |

The pure power law is explicitly eliminated; ln n / √n is the only qualified candidate.

**The prettiest result — the zero-parameter prediction**: The model already contains two simple laws (① the age distribution is fixed as 2(n−d)+1; ② the fluctuation amplitude of activity ≈ √(2n/π)). Plugging these two directly into the calculation of Ω, **with no fitted constants at all**, yields:

| n | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | 999 |
|---|---|---|---|---|---|---|---|---|---|---|
| Measured 1−Ω | 0.3157 | 0.2572 | 0.2268 | 0.2072 | 0.1930 | 0.1823 | 0.1730 | 0.1657 | 0.1594 | 0.1540 |
| Predicted 1−Ω | 0.3105 | 0.2544 | 0.2251 | 0.2060 | 0.1920 | 0.1811 | 0.1724 | 0.1650 | 0.1588 | 0.1536 |
| Relative deviation | 1.65% | 1.10% | 0.72% | 0.58% | 0.51% | 0.62% | 0.40% | 0.42% | 0.37% | 0.28% |

The deviation drops all the way to 0.28%–1.65%. **This is the strongest quantitative result in the whole article**: a non-trivial dynamical law, fully explained down to the sub-percent level by two more fundamental laws, with not a single parameter tuned along the way.

---

## 6. Conclusion 3: Why Time Looks Uniform (Theorem 3)

Define the "relative step non-uniformity" η: how much the rate of change differs between adjacent steps, divided by the current rate of change. Time is uniform if and only if η → 0.

**Theorem 3**: Directly differentiating the saturation law (not a separate fit) gives

> **η(n) ∝ (ln n) / n^(3/2) → 0**

That is, as the number of steps grows, the difference in "amount changed" between one step and the next becomes smaller and smaller — time tends toward uniformity. This conclusion is a **computed consequence**, and it even gives the specific number for "how non-uniform it is."

Measured (η uses a ±10-step smoothed difference quotient):

| n | 50 | 100 | 200 | 400 | 600 | 800 | 980 |
|---|---|---|---|---|---|---|---|
| η measured | 4.23×10⁻³ | 1.40×10⁻³ | 5.47×10⁻⁴ | 2.38×10⁻⁴ | 1.11×10⁻⁴ | 8.88×10⁻⁵ | 6.10×10⁻⁵ |
| η predicted | 3.00×10⁻³ | 1.32×10⁻³ | 5.45×10⁻⁴ | 2.18×10⁻⁴ | 1.27×10⁻⁴ | 8.61×10⁻⁵ | 6.54×10⁻⁵ |
| Ratio | 1.41 | 1.06 | 1.00 | 1.09 | 0.87 | 1.03 | 0.93 |

η has dropped by a factor of 69, and the measured-to-predicted ratio stays within 0.87–1.41 throughout. **This is the theorem-form, in this article, of the everyday statement "human perception of time is constant"**: it is not assumed, it is derived.

**Corollary**: Emergent time T_em ≈ n − O(√n·ln n). The measured T_em/n at n=100, 400, 999 is 0.573, 0.708, 0.778 respectively. In other words: only **after you explicitly choose "keep time by how much the world changes"** does the step count n asymptotically equal time, and the error is a "sublinear tail" too large to ignore. **Do not treat the step count as time unconditionally.**

---

## 7. Conclusion 4: But the Inside Is Not Uniform (Theorem 4)

A trend toward uniformity overall does not mean every place inside moves at the same speed. Fix the current step n and scan the cells' age d:

| n | newborn a(d=1) | a(d=n/8) | a(d=n/4) | a(d=n/2) | a(d=3n/4) |
|---|---|---|---|---|---|
| 100 | 0.140 | 0.596 | 0.729 | 0.825 | 0.887 |
| 400 | 0.083 | 0.728 | 0.828 | 0.912 | 0.929 |
| 999 | 0.059 | 0.805 | 0.885 | 0.941 | 0.958 |

**Theorem 4**: At the same instant, a cell's rewrite rate rises monotonically with its own age — newborn cells are nearly still (a under 0.06), old cells are rewritten at almost every step (a over 0.95). So **there is no single local flow speed inside the network**: every cell has its own clock.

**Why does the whole still tend toward uniformity?** Because the mass weight of the age distribution depends only on the ratio "age / total steps," which is **self-similar** when you zoom in (the shape stays the same under scale change). The various age layers rise and fall along the same curve, and the weighted average happens to compress the n-dependence down to ln n/√n. In other words: **uniformity is an averaging effect brought by self-similarity, not a property of every location** — just like a pot of boiling water has a uniform temperature overall, yet every water molecule is jittering around.

---

## 8. Conclusions 5 and 6: What Is Constant, What Is Not

The author's benchmark is the famous line about the speed of light: "as long as no phase transition occurs, it is a constant." Hidden in that line is an ambiguity that must be split apart.

### 8.1 The time constant does not depend on the "speed" parameter (Theorem 5)

Define the "time constant" Ω_∞ = the Ω at the limit; it represents "how much internal time one step amounts to."

**Theorem 5**: The value of the parameter λ (which controls the overall speed of rewriting) does not change Ω_∞; it only changes the **approach speed**.

Measured (λ swept from 0.2 to 3.0, a 15× span):

| λ | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 | 1.5 | 2.0 | 3.0 |
|---|---|---|---|---|---|---|---|---|
| Ω(199) | 0.503 | 0.627 | 0.698 | 0.741 | 0.771 | 0.822 | 0.853 | 0.886 |
| Ω(399) | 0.574 | 0.695 | 0.754 | 0.792 | 0.818 | 0.860 | 0.884 | 0.913 |
| Ω(799) | 0.641 | 0.749 | 0.802 | 0.834 | 0.856 | 0.890 | 0.910 | 0.933 |

Ω rises monotonically with both λ and n ⇒ all λ are approaching the **same target 1**.

**Why?** Ω_∞=1 is a saturation value. A saturation value carries no coupling strength: no matter how large or small λ is, the upper bound of the rewrite probability is 1. This has the same structure as "the speed-of-light limit does not depend on how the light source moves."

> **Honest note**: Regarding the approach speed c(λ), we originally guessed c ∝ 1/λ, but measurement overturned this guess (the slope is about −0.577, and because the window is too short it never reaches −1). This item is recorded as an open problem and is not treated as a conclusion.

### 8.2 But the time constant depends on the "shape of the rule" (Theorem 6, phase transition)

Just square the denominator of the update rule (same λ=0.8), changing nothing else:

| n | Control Ω | Variant Ω′ | Difference |
|---|---|---|---|
| 100 | 0.684 | 0.345 | 0.340 |
| 200 | 0.743 | 0.363 | 0.380 |
| 400 | 0.793 | 0.376 | 0.417 |
| 800 | 0.834 | 0.385 | 0.449 |
| 1099 | 0.851 | 0.388 | 0.463 |

The difference widens monotonically to 0.463 and is still growing ⇒ the two groups **cannot share the same limit**. Meanwhile, the variant group's activity E is almost identical to the control (27.43 vs 27.44), showing nothing ran out of control; it simply landed on **another fixed point** (the value the system finally settles on) Ω_∞≈0.39.

**Theorem 6 (phase transition)**: The **shape** of the update rule determines the time constant; the numerical value of the **parameter λ** that controls speed cannot change it.

> **Verdict**: "constant as long as no phase transition" is translated, in this article, into an executable criterion —
> - **Uniformity** (existence of the limit) holds under all tested parameters and both rules ⇒ robust;
> - the **time constant** (the numerical limit) is a function of the rule's **shape** ⇒ change the shape and you change it. Sweeping λ 15× could not move it; squaring one denominator symbol moved it.

**A guess that was overturned (written truthfully)**: We had thought the variant core would make the system "freeze out of control" (the less it changes → the more the network skews → the larger the denominator → the less it changes → Ω′→0). Wrong. Measurement shows activity is pinned at √(2n/π) by the basic law, the positive feedback never builds up, and the system stops at 0.39 instead of 0. This shows a "phase transition" changes the **numerical value** of the time constant, not "turning time off" — a world with Ω_∞=0.39 still has uniform time, only the internal duration per step is shortened by about 60%.

### 8.3 The boundary of the speed-of-light analogy

Where the analogy holds: both are "saturation values / upper-bound values," both are insensitive to specific coupling values; both are "structural constants" (here the rule's shape, there the space-time metric) — change the structure and you change the constant.

Where the analogy fails (cannot be extrapolated):
1. The Ω_∞ here is a **dimensionless ratio**, whereas the speed of light c **has dimensions** and needs a unit system; they are not the same kind of number.
2. The other side of the analogy, "the scale of time (seconds)," is **still absent** in this article (T_em → n only solved the shape).
3. The constancy of light speed has experimental backing; the Ω_∞ here is verified only on two groups of comparisons inside the model. **Do not use this article's results to assert any numerical conclusion about the physical speed of light.**

---

## 9. Conclusion 7: Time Is Not Unique — Two Clocks Cannot Coexist (Theorem 7)

Earlier, calibrating by "memory depth" gave τ_mem ≈ 2.005·√n (this is a continuously decelerating clock); this article, calibrating by "world change," gives T_em ≈ n. Both are *internal* readings of the network.

| n | 50 | 100 | 200 | 400 | 600 | 800 | 999 |
|---|---|---|---|---|---|---|---|
| τ_mem (memory clock) | 14.2 | 20.1 | 28.4 | 40.1 | 49.1 | 56.7 | 63.4 |
| T_em (change clock) | 25.3 | 58.0 | 129.7 | 283.9 | 445.1 | 610.5 | 777.7 |
| T_em / τ_mem | 1.78 | 2.89 | 4.57 | 7.08 | 9.06 | 10.76 | 12.27 |

**Theorem 7**: The ratio T_em / τ_mem diverges with n (measured growth of 6.89× and still going). Therefore **there is no rescaling that can make both intrinsic clocks uniform at once**.

Intuition: This is like two people each counting by their own heartbeat — as long as their heart rates differ, they will never agree on "how much time passed." The conclusion: **"time" is not a built-in property of the system; it is a derived quantity that appears after you choose a clock-calibration process.**

Supplement: both are tending toward uniformity, but at different rates. Calibrating by "world change" compresses non-uniformity to a lower order — this exactly explains why we observe uniform time: because the observer defaults to the reading "how much happened in the world," not the memory-depth route.

---

## 10. Where Did the Past Go: Structure, but No Memory

This is the most important section of the whole article.

### 10.1 There is structure (rejecting "completely random")

Treating "the world is purely random" as a null hypothesis is **wrong** — because the update rule itself (symmetry, per-column product, reset means freeze) creates correlations even with no historical memory at all. So the verdict must be done in two steps.

Measured: compare the real history against "purely random symmetric ±1 matrices," doing statistics at two scales, n=150 and n=300. Most indicators (mean, positive/negative sign ratio, spectral radius — a quantity measuring the network's scale) fall on the random line; **only the "row-sum variance" is about 1.94–2.03× the random value at both scales, with statistical significance (KS test, a test for whether two datasets share a distribution) p < 10⁻⁴**. This shows: cells within the same row are coordinated, and the joint distribution is not the product of the marginals — **the world has structure**.

### 10.2 But there is no memory (prefix indistinguishable)

Experiment: take two histories with **nothing in common** (different random seeds, run to step 150, with 48.5% of cells differing), then continue each for another 150 steps, obtaining 16 final states. Question: can these 16 final states still tell which prefix they came from?

Using an exact permutation test (enumerating all 12870 groupings): across 5 scalar statistics, the smallest p-value for the difference between the two groups is still 0.384 (and remains non-significant after multiple-testing correction). That is: **the two different first-half histories become indistinguishable after the second half** — no detectable trace is left behind.

> Limitation: this test is completed only on 5 statistics, not a global proof of "mutual information." But it is enough to show: on these 5 readings, sharing the same past leaves no trace.

### 10.3 Why time must be "emergent"

Combining the two points above gives the single most important sentence of the whole article:

> **The current state carries zero bits of information about its own past; therefore the "now" contains no readable time marker. Time can only be accumulated, not read — and that is the exact meaning of "time emerges."**

Put another way: if you only look at the world's present appearance, you cannot read out "how long it has lived" or "which path it took." Time is not a clockface engraved on the state; it is something you accumulate by counting, step by step, "how much it changed."

---

## 11. Eight Falsifiable Predictions

Each of the following can be used, with the same script, to directly overturn this article:

| # | Prediction | Criterion | Current measurement |
|---|---|---|---|
| P1 | Gap must contain ln n | Pure power law error significantly worse than ln n/√n | 26.4% vs 1.59% |
| P2 | Zero-parameter synthesis holds | Prediction vs measurement difference < 2% | 0.28%–1.65% |
| P3 | η→0 and ratio≈1 | η/η_predicted ∈ [0.5, 2] | [0.87, 1.41] |
| P4 | Ω_∞ independent of λ | Ω monotonic in both λ and n | holds (8 λ values) |
| P5 | Change rule shape moves the limit | Difference monotonic and > 0.30 | 0.463 |
| P6 | Joint has structure | Row-sum variance gap > 3σ and p<0.01 | 8.75σ / 13.89σ, p<10⁻⁴ |
| P7 | Joint no memory | Non-significant after correction | smallest p=0.384 |
| P8 | Two clocks cannot coexist | Ratio monotonically diverges with n | 1.78 → 12.27 |

**The easiest to topple is P2**: the moment you switch to another λ or another rule and the synthesis of those two basic laws no longer explains down to the percent level, the entire "zero-parameter" claim collapses.

---

## 12. Discussion: Neighborhoods of Historical Views of Time

This article's claims pass alongside several well-known discussions in the philosophy of time, but **do not** cite their quantitative results — only structural analogies:
- **Relationism / "time does not exist" (Barbour-style)**: This article agrees that "time is not in the state," but disagrees with concluding "it does not exist" — this article offers a computable substitute, and its uniformity is a consequence, not an assumption.
- **Thermal-time hypothesis (Connes–Rovelli style)**: The Ω here is also a time given by "how the state changes," but this article measures its saturation law and the convergence order of its non-uniformity — content the thermal-time construction usually does not write down.
- **Page–Wootters style (using a subsystem as a clock)**: Theorem 7 here is a **limitation** on it — switching to another subsystem may yield an incompatible clock, and the ratio will diverge.

---

## 13. Conclusion

All seven verdicts pass:

| Number | Verdict | Result |
|---|---|---|
| T1 | Emergent-time definition and saturation | Pass (self-consistent 2.2×10⁻¹⁶) |
| T2 | Saturation law ln n/√n + zero-parameter prediction | Pass (residual 1.59%, prediction deviation ≤1.65%) |
| T3 | Relative step non-uniformity → 0 | Pass (η/η_predicted ∈ [0.87,1.41]) |
| T4 | Single-member clock accelerates with its own age | Pass |
| T5a/T5b | Has structure / no memory | Pass (8.75σ–13.89σ; smallest p=0.384) |
| T6a/T6b | λ does not move the limit / rule shape moves the limit | Pass (difference 0.463) |
| T7 | Two clocks cannot coexist | Pass (ratio grows 6.89× and diverges) |

**Established**: Time is not an external parameter, but an accumulated quantity nested inside internal processes. Its uniformity is not an assumption but a consequence of the saturation law; and that saturation law can be fully explained down to the sub-percent level by two more fundamental laws.

**Judged**: "constant as long as no phase transition" splits into two sentences — uniformity holds under all tested parameters and rules (robust), while the time constant only moves when the update-rule shape is changed (and that is the strict location of a phase transition).

**The price paid**: Time is not unique. Two equally legitimate internal readings give incompatible times (the ratio diverges), and no member's clock inside the network runs uniformly. Calibrating by "how much the world changed" is a choice, not a discovery.

**Still missing**: Scale. This article solved the shape, not "how many seconds one step is" — this is the same thing as the only genuine gap registered in the project's early research (the assignment rule), projected onto the time-keeping problem.

**Also explained**: why time must be emergent rather than read — the current state carries zero bits about which history it traversed.

---

## 14. Honesty Statement (Boundaries for the Reader)

1. All numbers in this article are produced inside the SRE model (λ=0.8, seed=1111, except the multi-history contrast experiments), and the scripts and logs are archived with the article for one-command reproduction.
2. **Any comparison to real physical time is only a structural analogy, not a numerical prediction.**
3. Content labeled "analogy," "guess," or "open item" in the text must not be quoted as a conclusion.
4. **Reachable precision is limited**: at n=999, T_em/n=0.778, meaning "time is constant" has only about 22% precision at reachable scales. Equating this article's results directly with "physical time is strictly uniform" is a misreading.
5. **Scale is absent**: T_em has only a shape, no seconds.

---

## Appendix: Reproducibility Checklist (technical, kept for verification)

| Item | Script | Key quantity |
|---|---|---|
| Saturation law and all verdicts | `code/_time_emergence.py` (PART 0–8) | Ω(n), c, η, T_em |
| Supplementary probes | `code/_probe_time78.py` | initial judgment of 1−Ω shape |
| T6 investigation | `code/_probe_time78b.py` | c(λ), variant-core long-range trend |
| Evolution loop baseline | `code/sim_p.py` | authoritative update rule |
| Result dump | `code/_time_emergence.json` | all intermediate data |

Reproduce: `python code/_time_emergence.py` (about 2 minutes, EXIT=0).
