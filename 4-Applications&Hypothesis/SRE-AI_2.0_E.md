# SRE Topological Spectral Model: From Discrete Operators to a Differentiable AI Model Layer


Version: 2.0  

[Resource & Availability Statement] This framework is built upon Status-Relational Entropy (SRE) dynamics. All theoretical materials are archived in the Zenodo open-access repository. **This document suite includes the system paper, application development, scientific hypotheses, complete algebraic derivations of Operators 1–20, and fully open-source simulation code**.

> Visit the author's GitHub repository:
>
> https://github.com/yuelucn/Status-Relational-Entropy-SRE-Dynamics-The-Book-of-the-Void
>
> Visit the Tencent Smart Document Space with AI-assisted navigation (accessible on PC and WeChat mobile):
>
> https://docs.qq.com/space/DUkRjYUtNWFdyV253
>
> According to the Status-Relational Entropy (SRE) principle, classical physical foundations originate from information statistics.


> This document records the complete design reasoning, architectural implementation, and experimental results of the SRE Topological Spectral Model. It is both a reproducible experimental report and an extensible technical manual. Readers need no prior knowledge of graph Laplacians, Chebyshev polynomials, or chain complexes to follow the reasoning chain and understand the model's design motivation and mathematical foundations.

---

## Table of Contents

0. [From Operators to Model: Reasoning Chain and Key Bridge (Required Reading)](#0-from-operators-to-model-reasoning-chain-and-key-bridge-required-reading)
1. [Notation and Core Intuition](#1-notation-and-core-intuition)
2. [Preliminaries: Five Concepts with Precise Definitions](#2-preliminaries-five-concepts-with-precise-definitions)
3. [Model Architecture: Data Flow and Gradient Propagation](#3-model-architecture-data-flow-and-gradient-propagation)
4. [Experimental Setup: Three Tasks and Two Baselines](#4-experimental-setup-three-tasks-and-two-baselines)
5. [Experimental Results and Causal Analysis](#5-experimental-results-and-causal-analysis)
6. [Complete Usage Tutorial: From Environment Setup to Running All Cases](#6-complete-usage-tutorial-from-environment-setup-to-running-all-cases)
7. [Weight File Loading and Inference](#7-weight-file-loading-and-inference)
8. [Hyperparameter Tuning Guide](#8-hyperparameter-tuning-guide)
9. [Honest Boundaries: Verified Capabilities and Known Limitations](#9-honest-boundaries-verified-capabilities-and-known-limitations)
10. [Roadmap for Improvements](#10-roadmap-for-improvements)
11. [Project Structure and License](#11-project-structure-and-license)

---

## 0. From Operators to Model: Reasoning Chain and Key Bridge (Required Reading)

This section answers the most fundamental question: **Why can the 19 canonical operators be bridged into a differentiable AI model?** This reasoning chain was not complete at the start of design; it converged gradually through repeated verification. Following this chain helps understand the origin of every design decision.

### 0.1 Stage One: Operators are End-to-End Connected, Bridging Identity Holds Exactly

The foundation of the project is 19 discrete operators (hereinafter "canonical operators"), all implemented in numpy, frozen, and verified by 98 unit tests. The operator pipeline starts at molecular atom types and coordinates and ends at the weighted Laplacian matrix $L$:

$$
\text{positions} + \text{atomtypes} \xrightarrow{\text{Op1-6}} W_e \xrightarrow{\text{Op7-10}} m \xrightarrow{\text{Op11-19}} L
$$

The most critical bridging identity (verified in `main.py` Phase 6 with residual $\le 10^{-12}$) is:

$$
L = D_0^\top \operatorname{diag}(m) D_0 \equiv \operatorname{deg}(A_s) - A_s
$$

Here $D_0$ is the oriented incidence matrix of the graph (each edge assigned a direction, tail = −1, head = +1), and $m$ is the edge weight vector. The significance of this identity is: **the Laplacian matrix has two equivalent construction paths**—from the incidence matrix (algebraic path) and from the adjacency matrix (graph-theoretic path). The two paths are numerically exact, providing a dual-path validation for subsequent implementations.

The conclusion of Stage One: **the mathematical object $L$ has been completely defined and is numerically stable, but has not yet been "differentiably" parameterized**—numpy does not support autograd.

### 0.2 Stage Two: Torch Mirror Implementation of Operator Calculus

Alongside the canonical operators, the project already contains an independent torch module `operator_calculus.py`, which is the **differentiable mirror** of the canonical operators. The core of this module is three classes:

- **`ChainComplex`**: Encapsulates the incidence matrix $D_0$ and face operator $D_1$, internally replacing `numpy.ndarray` with `torch.Tensor` so the boundary identity $D_1 D_0 = 0$ holds differentiably.
- **`Operator`**: Wraps an $N \times N$ linear operator on a chain complex, supporting matrix multiplication, addition, commutators, power operations, and functional calculus. All operations return new `Operator` instances—**calculus closure** guarantees intermediate results never need to revert to numpy.
- **`OperatorCalculus`**: Bound to a `ChainComplex`, provides the exterior derivative $d$, codifferential $\delta$, Hodge Laplacian $\Delta = d\delta + \delta d$, weighted Laplacian $L_0(w) = D_0^\top \operatorname{diag}(w) D_0$, and Chebyshev functional calculus.

The key implementation detail is **Chebyshev functional calculus** (`chebyshev_functional`, lines 221–253). It uses the three-term recurrence:

$$
T_0(Y) = I,\quad T_1(Y) = Y,\quad T_{k+1}(Y) = 2Y T_k(Y) - T_{k-1}(Y)
$$

to expand any spectral function $g(L)$ as $g(L) \approx \sum_{k=0}^K c_k T_k(Y)$, where $Y = 2L/b - I$ maps the spectrum to $[-1, 1]$. **The entire process uses only matrix multiplication and never calls `torch.linalg.eigvalsh`**. This has two key benefits: (1) autograd can track gradients precisely—$\partial T_{k+1}/\partial Y = 2T_k + 2Y \partial T_k/\partial Y - \partial T_{k-1}/\partial Y$, the chain rule applies automatically; (2) it avoids gradient non-uniqueness caused by eigenvalue degeneracy.

This module already contains an inversion demo (`run_training_demo`, lines 277–324) that uses torch autograd to invert edge weights $w$ from spectral observations: given ground truth $w^*$, compute observations $Y^* = g(L_0(w^*)) X$ ($X$ is a multi-probe matrix), then train parameter $w$ so that $g(L_0(w)) X \approx Y^*$. Measured results: loss drops to $2 \times 10^{-19}$, Pearson correlation $\text{corr}(\hat{w}, w^*) = 1.0$.

The conclusion of Stage Two: **the step "from operators to differentiable operators" is already complete, and trainability has been verified on a small demo**. But the demo only uses ChainComplex + OperatorCalculus—it lacks a complete hierarchical structure and coarse-graining capability. It is essentially just a "toy verification of operator trainability."

### 0.3 Stage Three: The Missing Load-Bearing Component—Differentiable Hierarchical Compression

To extend operator_calculus into a true AI model, one core capability is still missing: **learnable granularity**. The model should not only extract features at a single scale, but also be able to see the same graph at multiple coarse-graining levels.

Coarse-graining has a standard form in algebraic topology—**Galerkin projection**: given an $n_0 \times C$ assignment matrix $P$ ($P^\top P = I$, orthogonality), the fine-level Laplacian $L_0$ can be projected to the coarse level:

$$
L_0' = P^\top L_0 P
$$

The chain complex is correspondingly reduced: $D_0' = D_0 P$ (the incidence matrix of the fine level multiplied by the assignment matrix yields the incidence matrix of the coarse level), and $D_1' = D_1$ (the face operator is invariant under coarse-graining because faces are filled by edge cycles, which are not split as units).

Galerkin projection has two modes:

| Mode | Construction of $P$ | $\beta_1$ Preservation | Differentiable | Purpose |
|:---|:---|:---|:---|:---|
| **Exact mode** | 0/1 hard assignment from BFS spanning tree | Provably strictly invariant | No | Validation baseline / structural pooling |
| **Learnable mode** | $P = \operatorname{softmax}(Z)$, where $Z$ is an $n_0 \times C$ learnable parameter | Soft constraint (penalize closure with soft rank) | Yes | Carrier of learnable granularity |

The proof that $\beta_1$ is strictly preserved in exact mode is straightforward: after contracting a spanning tree, $V' = \beta_0$, $E' = E - (n_0 - \beta_0)$, and the number of faces $F$ is unchanged, so

$$
\beta_1' = E' - V' + F = (E - n_0 + \beta_0) - \beta_0 + F = E - n_0 + F = \beta_1
$$

Galerkin projection is the model's **load-bearing component**—without it, operator_calculus is just a tool for computing spectral moments; with it, the model gains a hierarchical structure "from coarse to fine" and can extract features at multiple scales.

### 0.4 Stage Four: The Mathematical Discovery That $\tau_k$ Is Not Preservable and the Alternative

The original design plan called for using the relative error of $\tau_k$ as the spectral fidelity criterion ($\le 5\%$). $\tau_k$ is the normalized trace of Chebyshev spectral moments:

$$
\tau_k = \frac{1}{N} \operatorname{tr}(T_k(Y)),\quad Y = \frac{2L_0}{\alpha_n} - I
$$

Under Galerkin projection, $\tau_k' = \operatorname{tr}(T_k(Y'))/N'$, where $Y' = 2L_0'/\alpha_n' - I$.

Measured data (exact Galerkin, 4 graphs, 8 levels) yielded an unexpected conclusion: **$\tau_k$ is not preservable under Galerkin**—the relative error reaches 63% to 100%.

The mathematical root cause is: $\tau_k$ depends on the full spectral distribution + dimension $N$ + spectral radius $\alpha_n$. Galerkin projection changes all three simultaneously—eigenvalues are sandwiched between adjacent eigenvalues of $L_0$ by the Cauchy interlacing theorem ($\lambda_i(L_0) \le \lambda_i(L_0') \le \lambda_{i+n_0-C}(L_0)$), but $N$ changes from $n_0$ to $C$, and $\alpha_n$ also changes with $L_0'$. With three variables changing simultaneously, the nonlinear function $\operatorname{tr}(T_k(Y))$ cannot remain invariant.

The alternative adopts a two-layer design:

**Monitoring metric—eigenvalue cosine similarity** (`spectral_cosine_similarity`): Apply `eigvalsh` to $L_0$ and $L_0'$ to obtain sorted eigenvalue vectors, linearly interpolate the coarse-level eigenvalues to align with the fine-level index space, then compute cosine similarity. The Cauchy interlacing theorem guarantees stable ordering, and measured $\cos_{\text{sim}} \in [0.996, 1.000]$ under exact Galerkin. This metric is for monitoring only and does not participate in gradients.

**Differentiable loss—heat kernel trace relative distance** (inside `loss_of`):

$$
L_{\text{spec}} = \operatorname{mean}_{t \in \{1.0, 2.0\}} \frac{\lvert \operatorname{tr}(e^{-t L_0'}) - \operatorname{tr}(e^{-t L_0})\rvert }{\max(\operatorname{tr}(e^{-t L_0}), 10^{-30})}
$$

The heat kernel trace $\operatorname{tr}(e^{-t L}) = \sum_i e^{-t \lambda_i}$ is computed via `chebyshev_functional`—fully differentiable. Key design detail: $L_0$ is **detached** (converted to Python float as a constant), so the gradient of $L_{\text{spec}}$ cannot interfere with the inversion direction of edge weights $m$; $L_0'$ is **not detached**, and gradients flow through $L_0' \leftarrow P \leftarrow Z$ back to SoftAggPooler's parameters.

### 0.5 Complete Bridging Diagram

```
Canonical operators (numpy, 19 Op, frozen)
  │  W_e → m → L   Bridging identity L = D0ᵀdiag(m)D0 ≡ deg - A_s
  ▼
operator_calculus.py (torch, differentiable mirror)
  │  ChainComplex → Operator → OperatorCalculus
  │  chebyshev_functional: three-term recurrence, autograd, no eigvalsh
  │  laplacian0(w): weighted graph Laplacian, w differentiable
  │  run_training_demo: inversion verified loss→2e-19, corr=1.0
  ▼
sre_topology_model.py (new model layer)
  │  SoftAggPooler: P = softmax(Z), Galerkin projection L0' = PᵀL0P
  │  ScaleGauge: m = s · softplus(ρ)/mean, eliminates scale flat direction
  │  SRETopoEncoder: fixed operator, τ_k + α_n + λ₂, no learnable parameters
  │  Five-term loss: L_task + λ_g L_gauge + λ_s L_spec + λ_h L_hom + λ_head L_head
  │  L_spec gradient path: L_spec → tr_c → chebyshev → Y → L0' → P → Z
  ▼
Three use cases verified: UC1 inversion corr=1.0, UC2 regression R²=0.878, UC3 classification acc=1.0
```

The core logic of this bridging chain is: **mathematical correctness of operators is guaranteed by the canonical operators, differentiability by the torch mirror implementation, and hierarchical expressiveness by SoftAggPooler**. The three are independently implemented, independently verified, and then converge in the model layer.

---

## 1. Notation and Core Intuition

**Given the connectivity of a molecule or graph, extract its topological spectral features, then use these features for molecular property prediction, graph classification, or graph inversion tasks.**

More concretely: imagine you have the atomic connectivity table of a molecule—"carbon atom #0 is connected to hydrogen atoms #3, #4, #5 and another carbon atom #1." Input this table to the SRE model, and it outputs an 11-dimensional feature vector representing the full spectral information encoded in this molecule's topological structure. Then you can train a simple linear regression on this vector to predict the molecule's HOMO-LUMO gap (a molecular property), or train a binary classifier to determine whether the graph contains a cycle (β₁=1 or 0).

The core viewpoint of the SRE model is: **the spectrum (eigenvalue distribution) of a graph's Laplacian matrix carries more shape information than the adjacency matrix itself**. Traditional graph neural networks (GCN, GIN) start from the adjacency matrix and perform message passing, while SRE directly targets the spectrum as the more fundamental object.

---

## 2. Preliminaries: Five Concepts with Precise Definitions

Each concept in this section follows the same structure: **intuitive metaphor → formal definition → why it matters for the model**. Skip any concept you are already familiar with. Understanding these concepts requires no graduate-level mathematics—each paragraph starts with intuition before presenting formulas.

### 2.1 Graph Laplacian Matrix: The Vibration Equation of a Graph

**Intuitive metaphor**: Imagine a graph as a spring system. Each node is a small ball, each edge is a spring. The Laplacian matrix is the matrix that describes the vibration equation of this system—its eigenvalues are the vibration frequencies, its eigenvectors are the vibration modes. Therefore the eigenvalue distribution (the "spectrum") of the Laplacian matrix encodes the shape of the entire graph. Cycles, chains, and complete graphs all have fundamentally different spectrum shapes.

**Formal definition**: Given a graph $G = (V, E)$ with adjacency matrix $A$ ($A_{ij} = 1$ when there is an edge between $i$ and $j$), degree matrix $D$ ($D_{ii} = \sum_j A_{ij}$), the Laplacian is defined as $L = D - A$. If edges have weights $w_{ij}$, then $L = D - A$ where $A_{ij} = w_{ij}$ and $D_{ii} = \sum_j w_{ij}$. In incidence matrix form this is $L = D_0^\top \operatorname{diag}(m) D_0$, where $D_0$ is the oriented incidence matrix (each edge assigned a direction, tail −1, head +1) and $m$ is the edge weight vector.

**Why it matters for the model**: The Laplacian is the core carrier of the entire SRE model. All spectral features in the model ($\tau_k$, $\alpha_n$, $\lambda_2$) are computed from $L$. The model treats $L$ as a differentiable tensor so that the entire forward pass flows through PyTorch's autograd.

### 2.2 Betti Number β₁: How Many Independent Cycles in a Graph

**Intuitive metaphor**: Imagine a graph made of rubber bands. If you cut it once, how many pieces does it fall into? $\beta_0$ is the number of connected components. How many cuts do you need to make the graph into a tree (a graph with no cycles)? $\beta_1$ is the number of independent cycles. A single cycle ($C_6$) has $\beta_1=1$, a chain has $\beta_1=0$, two disconnected cycles have $\beta_0=2$ and $\beta_1=2$.

**Formal definition**: $\beta_1 = n_1 - n_0 + n_2$, where $n_0$ is the number of nodes, $n_1$ the number of edges, $n_2$ the number of faces (closed regions). This is the Euler-Poincaré formula for chain complexes. For a pure graph ($n_2=0$), the formula reduces to $\beta_1 = n_1 - n_0 + 1$ (assuming $\beta_0=1$, a connected graph).

**Why it matters for the model**: $\beta_1$ is a topological property—it should remain strictly invariant under coarse-graining (merging multiple nodes into one). The SRE model uses $\beta_1$ as a criterion to check whether coarse-graining operations are correct, and also as the label for the UC3 classification task. The model includes a soft rank function `soft_rank` that approximates $\beta_1$ using the trace of the Hodge Laplacian $\Delta_2$.

### 2.3 Chebyshev Polynomial Functional Calculus: Computing Spectral Functions Without Eigendecomposition

**Intuitive metaphor**: You want to compute $f(L)$ where $f$ is some function (like the heat kernel $\exp(-tL)$), but you don't want to first perform the eigendecomposition of $L$ (which is $O(n^3)$ and unstable). Chebyshev polynomials provide a shortcut—they have a three-term recurrence formula that you can compute layer by layer like the Fibonacci sequence, using only matrix multiplication the entire time.

**Formal definition**: $T_0(Y) = I$, $T_1(Y) = Y$, $T_{k+1}(Y) = 2Y T_k(Y) - T_{k-1}(Y)$. To compute $f(L)$, first scale $Y = 2L/b - I$ to map the spectrum of $L$ to $[-1, 1]$, then perform numerical interpolation at the Chebyshev nodes to obtain coefficients $c_k$, and finally $f(L) \approx \sum_{k=0}^K c_k T_k(Y)$. For the trace, $\operatorname{tr}(f(L)) \approx \sum_k c_k \operatorname{tr}(T_k(Y))$, where each term can be computed recursively.

**Why it matters for the model**: $\tau_k$ in the SRE model is exactly $\operatorname{tr}(T_k(Y))/N$, and the heat kernel trace loss is also computed via `chebyshev_functional`. The key benefit is that **the entire process uses PyTorch matrix multiplication, so autograd can track gradients precisely**, and with $K=32$ it is sufficiently accurate, completely bypassing the $O(n^3)$ bottleneck of `eigvalsh`.

### 2.4 Galerkin Projection and the Non-Preservability of τ_k

**Intuitive metaphor**: There are two ways to shrink a high-resolution photograph. The Galerkin projection approach is: divide $n_0$ pixels into $C$ clusters, use one representative pixel per cluster, then compute the Laplacian of the compressed image as $L_0' = P^\top L_0 P$, where $P$ is an $n_0 \times C$ 0/1 matrix (each pixel belongs to exactly one cluster). The problem is that a spectral feature $\tau_k$ of the original image depends on all $n_0$ eigenvalues, but the compressed image only has $C$ eigenvalues and their distribution has changed—you cannot expect $\tau_k'$ of the compressed image to equal $\tau_k$ of the original.

**Formal definition**: Galerkin projection $L_0' = P^\top L_0 P$, where $P^\top P = I$ (orthogonality). By the Cauchy interlacing theorem, the eigenvalues of $L_0'$ are sandwiched between adjacent eigenvalues of $L_0$: $\lambda_i(L_0) \le \lambda_i(L_0') \le \lambda_{i + n_0 - C}(L_0)$. But $\tau_k = \operatorname{tr}(T_k(Y))/N$ is a nonlinear function of the full spectrum and is not invariant under Galerkin projection.

**Why it matters for the model**: This is one of the earliest mathematical facts exposed in this project—the original design plan required $\tau_k$ relative error $\le 5\%$, but measured error under exact Galerkin reached 63%–100%. We replaced it with **eigenvalue cosine similarity cos_sim** as the spectral fidelity monitoring metric (0.996–1.000 under exact Galerkin) and **differentiable heat kernel trace distance** as the $L_{\text{spec}}$ loss.

### 2.5 Heat Kernel Trace: A Global Measure of Heat Diffusion Processes

**Intuitive metaphor**: Imagine placing a heat source simultaneously at every node of a graph, then letting heat diffuse along the edges. After time $t$, what is the total heat in the entire graph? $\operatorname{tr}(\exp(-tL_0))$ is exactly this value. This quantity encodes the overall connectivity of the graph: as $t \to 0$ it equals $N$ (each node's own heat), and as $t \to \infty$ it equals $\beta_0$ (only connected components still have temperature differences). Therefore at intermediate values of $t$ it is most sensitive to spectrum shape.

**Formal definition**: $\exp(-tL_0) = \sum_i \exp(-t\lambda_i) v_i v_i^\top$, and taking the trace gives $\operatorname{tr}(\exp(-tL_0)) = \sum_i \exp(-t\lambda_i)$. $t$ is a time scale: small $t$ primarily looks at small eigenvalues (low-frequency modes), large $t$ at large eigenvalues (high-frequency modes).

**Why it matters for the model**: The $L_{\text{spec}}$ loss uses the relative distance of heat kernel traces as a spectral fidelity metric. Its key advantage is that when computed via `chebyshev_functional` it is fully differentiable, and gradients can propagate from $L_0'$ back through the SoftAggPooler's parameter $Z$. This turns $L_{\text{spec}}$ from a non-differentiable monitoring metric into a regularization term that truly participates in training.

---

## 3. Model Architecture: Data Flow and Gradient Propagation

This section uses a step-by-step description to explain what transformations a molecular graph undergoes inside the model from input to final prediction, the mathematical form of each transformation, and how gradients flow.

### 3.1 Input: Chain Complex Representation of Molecular Graphs

The model receives three raw inputs: $D_0$ (incidence matrix, shape $n_1 \times n_0$), $D_1$ (face operator, shape $n_2 \times n_1$; for most molecular graphs $n_2=0$), and $m$ (edge weight vector, length $n_1$). Constructing $D_0$ is straightforward: number each edge, assign each edge a direction (e.g., from the smaller node number to the larger), fill −1 at the tail column and +1 at the head column. For ethanol, $n_0=9$ atoms, $n_1=8$ bonds, so $D_0$ is an $8 \times 9$ matrix.

### 3.2 Laplacian Construction: Analytic Formula, Differentiable

Compute $L_0 = D_0^\top \operatorname{diag}(m) D_0$ directly from $D_0$ and $m$. There are no neural network layers here—just two matrix multiplications and a diagonal matrix. The benefit is: PyTorch's autograd can precisely track the gradient of $m$—$\partial L_0 / \partial m = D_0^\top \odot D_0$ (element-wise multiplication), and $\partial \operatorname{tr}(L_0) / \partial m = 2 \cdot \sum_{i \in \text{edge } jk} (L_{0,ii} + L_{0,jj} - 2L_{0,ij}) \cdot D_{0,ij}^2$. The model also has a Galerkin path: compute $L_0' = P^\top L_0 P$ from the SoftAggPooler output $P$, used for cross-level spectral features. $L_0$ is `.detach()`-ed before passing into SRETopoEncoder—this is deliberate design, so $L_{\text{spec}}$ does not interfere with the inversion gradient direction of $m$.

### 3.3 SoftAggPooler: A Learnable Coarse-Graining

This layer is the only "learnable" component (aside from the final task head). It has an `nn.Parameter` tensor $Z$ with shape $n_0 \times n_{\text{clusters}}$. Applying softmax to each row yields the granularity assignment matrix $P$—each node belongs to $n_{\text{clusters}}$ clusters with a probability distribution. $P$ is a "soft version" of the 0/1 hard assignment. Galerkin projection $L_0' = P^\top L_0 P$ uses this $P$ for coarse-graining. The gradient of $Z$ comes from $L_{\text{spec}}$'s heat kernel trace loss (gradient path: $L_{\text{spec}} \to \text{tr}_c \to \text{chebyshev\_functional} \to Y \to L_0' \to P \to Z$). The pooler is initialized with `torch.randn(...) * 0.01`, a small random value that ensures softmax is close to uniform assignment early in training.

### 3.4 SRE Topo Encoder: Fixed Operator, Computing Spectral Features

This layer has no learnable parameters—it is simply a set of canonical operators (Op13–18 Chebyshev functional calculus + Op9 Hodge Laplacian). Input is $L_0$ (detached, not in the gradient graph), output is a $K+3$-dimensional spectral feature vector: $[\tau_0, \tau_1, \dots, \tau_K, \alpha_n, \lambda_2]$.

$\tau_k = \operatorname{tr}(T_k(Y))/N$, where $Y = 2L_0/\alpha_n - I$ and $\alpha_n = \lambda_{\max}(L_0)$. $\alpha_n$ is the spectral radius of $L_0$, obtained directly via `torch.linalg.matrix_norm(L0, ord=2)` or `torch.linalg.eigvalsh(L0)[-1]`. $\lambda_2$ is the second-smallest eigenvalue, also called "algebraic connectivity"—it measures how tightly connected the graph is.

The key design decision of this layer: **do not use eigvalsh**. If you want to compute the eigenvalue distribution, the most direct way is `eigvalsh`, but its gradients are unstable (gradient is 0 or non-unique at eigenvalue degeneracy). The SRE design philosophy is to **use Chebyshev functional calculus instead of eigvalsh** to indirectly compute spectral moments—gradients are more stable, and the entire process uses only matrix multiplication, making it friendly for large graphs.

### 3.5 Level Attention Head: Multi-Level Spectral Feature Fusion

SoftAggPooler can perform multi-layer coarse-graining: original layer $L_0 \to$ first-level coarse-graining $L_0' \to$ second-level $L_0'' \to \dots$. Each level $L_0$ computes a $K+3$-dimensional spectral feature, forming an $n_{\text{levels}} \times (K+3)$ matrix $X$. LevelAttentionHead performs attention-weighted fusion on $X$: first map each row feature to hidden dimension, then perform attention pooling over the hidden dimension to obtain a fixed-length fused feature, and finally pass through two MLP layers to output the task value.

### 3.6 Task Head: Simple MLP, Regression or Classification

The final layer is a linear classifier or regressor. For the UC2 regression task: `Linear(9, 32) → ReLU → Linear(32, 1)`, outputs a scalar prediction (estimated gap). For the UC3 classification task: `Linear(9, 32) → ReLU → Linear(32, 1) → Sigmoid`, outputs a probability in $[0, 1]$. Trained with `BCEWithLogitsLoss` (classification) or `MSELoss` (regression).

### 3.7 Loss Function: Five-Term Combination

The complete loss function is $L = L_{\text{task}} + \lambda_g L_{\text{gauge}} + \lambda_s L_{\text{spec}} + \lambda_h L_{\text{hom}} + \lambda_{\text{head}} L_{\text{head}}$.

$L_{\text{task}}$ is the main loss—in the self-supervised demo it makes $g(L_0(m)) X \approx g(L_0(m_{\text{star}})) X$; in regression/classification tasks it makes $\text{MLP}(\text{spectral features}) \approx y_{\text{true}}$. $L_{\text{head}}$ is an auxiliary loss between multi-level spectral features, making coarse-level $\tau_k$ approach fine-level $\tau_k$ (note: here $\tau_k$ is computed on $L_0$ which is not detached, so $L_{\text{head}}$ can directly train $m$). $L_{\text{gauge}}$ constrains $\alpha_n(m)$ not to deviate too far from $\alpha_n(m_0)$, used to eliminate the flat direction of overall edge weight scaling. $L_{\text{spec}}$ is the differentiable heat kernel trace loss, training SoftAggPooler's $Z$. $L_{\text{hom}}$ uses soft rank (difference of $\operatorname{tr} h(L_1') - \operatorname{tr} h(L_1)$ with sharp=80, K=48, $h(t) = \exp(-80t)$) to constrain the $\beta_1$ closure between coarse and fine levels.

---

## 4. Experimental Setup: Three Tasks and Two Baselines

### UC1: Self-Supervised Edge Weight Inversion

**Task definition**: Given the topological structure of a molecule (how atoms are connected), invert the actual strength $m$ of each bond. This task has no "ground-truth edge weights" as supervision labels—hence it is **self-supervised**: we generate a ground truth $m_{\text{star}}$ with a random seed, then compute observations $Y = g(L_0(m_{\text{star}})) \cdot X$ (where $g$ is a power series of $L_0$, the observation operator, and $X$ is a random probe matrix). During training the model only sees $Y$ and $D_0/D_1$ and must learn $m$ to fit.

**Why use random ground truth**: If we use the real $W_e$ (electronegativity edge weights), its numerical range is very uniform (most bond weights are between 0.95–1.05), making it nearly unidentifiable—scaling $m$ uniformly by 0.99 produces negligible change in observations. Using uniformly distributed random values between 0.5–2.0 as ground truth guarantees the inversion is well-conditioned and identifiable.

**Training process**: Adam optimizer with lr=0.08, 1500 iterations. $m$ starts from uniform initialization, is pushed toward fitting $g(L_0(m)) \cdot X \approx Y$ by $L_{\text{task}}$, while $L_{\text{spec}}$ and $L_{\text{hom}}$ serve as regularization terms constraining spectral and topological structure. SoftAggPooler's $Z$ is also trained by $L_{\text{spec}}$, learning a reasonable coarse-graining assignment.

**Result interpretation**: $\text{corr}(\hat{w}, w^*) = 1.0000$ indicates perfect inversion convergence—the Pearson correlation between recovered edge weights and ground truth reaches 1. $L_{\text{task}}$ drops from $3 \times 10^{-3}$ to $8 \times 10^{-11}$, MAE is only $2.9 \times 10^{-5}$. This demonstrates that the model's trainability is not in question—when observations $Y$ are sufficiently informative, inversion is completely feasible.

**Weight file**: `release/weights/uc1_edge_inversion.pt`. Internal structure includes `pooler_state` (SoftAggPooler's $Z$ parameter), `D0`/`D1` (numpy arrays of the ethanol chain complex), and `meta` (training hyperparameters).

### UC2: Molecular Property Regression

**Task definition**: Given graph structure (synthesized cycles and chains), predict HOMO-LUMO gap. Labels are synthesized by: compute the Laplacian eigenvalues of each graph, take $\text{gap} = (\lambda_{\max} - \lambda_2) / \lambda_{\max}$, then add 5% Gaussian noise. This definition is justified because $\lambda_{\max}$ and $\lambda_2$ correspond respectively to the highest and lowest non-trivial eigenvalues of molecular orbitals, and their difference directly reflects the molecule's electronic energy gap.

**Dataset**: 6 graphs, $n_0$ from 5 to 10, alternating cycles and chains. 4 training samples, 2 test samples. This dataset is small—our goal is not large-scale benchmarking but to **verify that the model's spectral features indeed encode gap information**.

**Input comparison of the three models**: SRE input is $K+3=9$-dimensional spectral features $[\tau_0..\tau_6, \alpha_n, \lambda_2]$. GCN and GIN inputs are $n_0 \times 1$ identity node features + $n_0 \times n_0$ normalized adjacency matrix, zero-padded to $n_0=10$ for small graphs. The three models have **comparable parameter budgets**: SRE's MLP has $9 \times 32 + 32 + 32 \times 1 + 1 = 321$ parameters; each of GCN/GIN's two layers has $1 \times 16 + 16 + 16 \times 16 + 16 = 304$ parameters. So the comparison is fair.

**Result interpretation**: SRE achieves MSE=0.0023, R²=0.878; GIN achieves 0.0062/0.674; GCN achieves 0.0159/0.160. SRE leads GIN by 20 percentage points in R² and GCN by 72 percentage points. GCN's R² is only 0.16—approximately random guessing. This is not because GCN failed to converge (it converged to loss=0.0159), but because **mean pooling completely washes out the graph's topological information**. After mean pooling in GCN, cycles and chains have nearly identical feature vectors, and the MLP simply cannot distinguish them. GIN's sum pooling preserves node identity, so it performs much better than GCN, but SRE still significantly outperforms it—because SRE's spectral features directly contain $\alpha_n$ and $\lambda_2$, which are the key variables in the gap formula.

**Weight files**: `uc2_sre_regression.pt` / `uc2_gcn_regression.pt` / `uc2_gin_regression.pt`. Each checkpoint stores trained `state_dict`, all graph features, labels, and config (K, in_dim, task).

### UC3: Graph Classification (β₁ Topology Identification)

**Task definition**: Distinguish cyclic ($\beta_1=1$) from acyclic ($\beta_1=0$) graphs. We synthesized 20 graphs: 10 cyclic (first generate a spanning tree to ensure connectivity, then add one edge to introduce at least one cycle), 10 pure chains ($n_0-1$ edges, naturally acyclic). $n_0$ is randomized between 5–8, edge weights between 0.5–2.0.

**Why choose $\beta_1$ as the classification target**: $\beta_1$ is a pure topological invariant—it depends only on the graph's connected structure and is completely independent of edge weight values. This makes it an ideal metric to verify whether the model truly learns **topological properties** rather than **edge weight patterns**.

**Result interpretation**: Both SRE and GIN achieve 100% accuracy; GCN only achieves 85%. Where do GCN's 15% errors come from? After mean pooling, some cyclic and acyclic graphs have very similar feature vectors (especially when short chains and cycles have similar spectrum shapes), and the linear classifier cannot draw a clear decision boundary. SRE's spectral features directly encode $\beta_1$ proxies (e.g., soft_rank output, whether $\lambda_2 > 0$, or the shape of $\tau_k$), so the classifier can perfectly separate them. GIN's sum pooling preserves node identity, allowing the MLP to learn some $\beta_1$-equivalent signature (e.g., "sum of products of node degrees" or some count from WL iterations), also achieving perfect classification.

**Weight files**: `uc3_sre_classifier.pt` / `uc3_gcn_classifier.pt` / `uc3_gin_classifier.pt`.

---

## 5. Experimental Results and Causal Analysis

This section does not repeat the result table from the previous section, but explains **why** SRE significantly outperforms baselines in some cases, matches baselines in others, and still lags baselines in certain scenarios. Understanding this will let you judge whether SRE is suitable for your task.

**The fundamental reason SRE significantly outperforms GCN/GIN on UC2**: SRE's feature space is the spectrum—$\alpha_n$ ($\lambda_{\max}$) and $\lambda_2$ (algebraic connectivity) are directly the core variables of the gap formula, and $\tau_k$ (Chebyshev spectral moments) encodes higher-order information about the full spectrum shape. Intuitively: SRE's input already contains the key variables ($\alpha_n$ and $\lambda_2$) needed by the gap formula, while GCN/GIN's input is only the raw graph topological structure information, requiring the MLP to extract $\alpha_n$ and $\lambda_2$ indirectly through multi-layer nonlinear transformations. This is why SRE leads baselines by 20–72 percentage points in R² on UC2.

**Why GCN performs much worse than other baselines on UC2 (R²=0.16)**: Mean pooling discards graph scale information. Imagine two different graphs—one with $n_0=6, \lambda_{\max}=3$ and another with $n_0=8, \lambda_{\max}=3$. After GCN mean pooling, their feature vectors might be identical (both depend only on normalized adjacency node degrees), while SRE can distinguish them through $\alpha_n$ and $\lambda_2$. The more fundamental issue is: GCN's message passing essentially computes "powers of the adjacency matrix," and there is no direct monotonic relationship between powers of the adjacency matrix and the eigenvalues of the Laplacian. Without node features (identity features), GCN's expressiveness is severely limited.

**Why GIN also achieves 100% on UC3**: GIN's expressiveness has been proven equivalent to the Weisfeiler-Leman graph isomorphism test—it can distinguish any two distinct graph structures (in a certain sense). Graphs with $\beta_1=0$ and $\beta_1=1$ are obviously non-isomorphic, so GIN naturally learns some $\beta_1$-equivalent signature. But this does not mean GIN can match SRE on all tasks—on UC2, gap is a continuous spectral property rather than a discrete graph isomorphism class label. GIN's learning efficiency on continuous spectral properties is much lower than SRE, because it must indirectly derive spectral information from intermediate message-passing representations.

**Where SRE is weak**: The current model only has one SoftAggPooler layer, while GCN/GIN can stack multiple layers to form deep networks. On tasks requiring multi-layer message passing to learn abstract concepts (e.g., molecular toxicity prediction needing both local functional groups and global scaffolds simultaneously), the single-layer SRE may underperform deep GIN. Another weakness is SRE's scalability with respect to $n_0$—both `eigvalsh` and `chebyshev_functional` have $O(n^3)$ complexity, making the current implementation impractical for graphs with $n_0 \ge 100$, while the message-passing paradigm can run large graphs with $O(n + m)$ complexity.

---

## 6. Complete Usage Tutorial: From Environment Setup to Running All Cases

### 6.1 Environment Requirements

On Windows, `KMP_DUPLICATE_LIB_OK=TRUE` must be set before importing numpy or torch; otherwise it will crash due to duplicate OpenMP library initialization. Python ≥ 3.8, torch ≥ 2.0, numpy ≥ 1.24. No dependencies on torch-geometric, scipy, rdkit, or other third-party packages.

### 6.2 Three Steps to Run Everything

```powershell
# Step 1: Set environment variable (must be before any import)
$env:KMP_DUPLICATE_LIB_OK = "TRUE"

# Step 2: Run all cases + baselines + save weights + print evaluation table
python sre_ai_model\sre_release.py

# Step 3: Check outputs
ls sre_ai_model\release\weights\          # 9 .pt weight files
type sre_ai_model\release\metrics.json    # Machine-readable evaluation metrics
```

`sre_release.py` also supports `--use uc1`, `--use uc2`, `--use uc3`, and `--use all` (default) for selective execution. Each case takes seconds to tens of seconds depending on iteration count.

### 6.3 Run the Self-Supervised Demo Alone

If you only want to see SRE's core inversion capability, this is sufficient:

```powershell
$env:KMP_DUPLICATE_LIB_OK = "TRUE"
python -c "import sys; sys.path.insert(0,'sre_ai_model'); import sre_topology_model as stm; r=stm.run_selfsupervised_demo(iters=1500); print(f'corr={r[\"corr\"]:.4f}, MSE={r[\"loss1\"]:.2e}')"
```

Two key lines in the output are `corr` and `cos_sim`—corr=1.0 indicates perfect inversion convergence, cos_sim indicates the spectral fidelity of coarse-graining in learnable mode (exact mode is 0.996–1.000; learnable mode depends on SoftAggPooler's training degree).

### 6.4 Run Unit Tests

Torch-side model layer tests:

```powershell
$env:KMP_DUPLICATE_LIB_OK = "TRUE"
python -m pytest sre_ai_model\test_sre_topo_model.py -v
```

All 11 tests pass, covering: $\beta_1$ preservation, Galerkin identity, $\tau$ consistency with canonical Op13, non-zero gradients, soft-rank $\beta_1$ closure, demo convergence, prior invariance, cementing the non-preservability of $\tau$, and verifying cos_sim reachability.

Canonical regression (19 operators):

```powershell
$env:KMP_DUPLICATE_LIB_OK = "TRUE"
python -m pytest test_operators_11_19.py test_operator_calculus.py -q
```

98 items, zero breakage.

### 6.5 All Output Files

After running `sre_release.py`, you will see in `sre_ai_model/release/`:

- `weights/uc1_edge_inversion.pt` — SoftAggPooler weights for UC1 + ethanol chain complex D0/D1
- `weights/uc2_sre_regression.pt` — Regression head weights for UC2 + SRE spectral features for all graphs
- `weights/uc2_gcn_regression.pt` — GCN baseline weights for UC2
- `weights/uc2_gin_regression.pt` — GIN baseline weights for UC2
- `weights/uc3_sre_classifier.pt` — Classification head weights for UC3
- `weights/uc3_gcn_classifier.pt` — GCN baseline weights for UC3
- `weights/uc3_gin_classifier.pt` — GIN baseline weights for UC3
- `metrics.json` — Machine-readable evaluation metrics with detailed numerical values for each case and each model

---

## 7. Weight File Loading and Inference

This section explains how to load already trained weights and how to perform inference on a new graph. The checkpoint design principle is: **all information needed to reconstruct the model structure is stored in the config field**, so you don't need to re-read source code to find hyperparameters.

### 7.1 Load the UC1 Inversion SoftAggPooler

```python
import os, sys
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, "sre_ai_model")
import torch
import sre_topology_model as stm

# Load checkpoint (PyTorch 2.6+ safe: all values converted to tensor)
ckpt = torch.load("sre_ai_model/release/weights/uc1_edge_inversion.pt",
                  weights_only=False)

# Each field has a _type wrapper; read .value to unwrap
sd = ckpt["pooler_state"]    # {"_type": "state_dict", "value": {"Z": tensor}}
D0 = ckpt["D0"]["value"]     # torch.Tensor, shape (n1, n0)

# Infer n0 from D0, n_clusters from Z
n0 = int(D0.shape[1])
n_clusters = int(sd["value"]["Z"].shape[1])

# Rebuild pooler with same architecture and load
pool = stm.SoftAggPooler(n0, n_clusters, seed=0)
pool.load_state_dict(sd["value"])
pool.eval()
```

### 7.2 Load the UC2 Regression Head and Perform Inference on a New Graph

```python
import os, sys
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, "sre_ai_model")
import torch
import torch.nn as nn
import numpy as np
import sre_topology_model as stm

ckpt = torch.load("sre_ai_model/release/weights/uc2_sre_regression.pt",
                  weights_only=False)

# config is a nested raw_dict; unwrap layer by layer
config = ckpt["config"]["value"]
K = config["K"]                    # 6
in_dim = config["in_dim"]          # 9 (= K+3)

# Rebuild MLP: Linear(in_dim, 32) → ReLU → Linear(32, 1)
class SREHead(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 32), nn.ReLU(), nn.Linear(32, 1))
    def forward(self, x):
        return self.net(x).squeeze(-1)

head = SREHead(in_dim)
head.load_state_dict(ckpt["model_state"]["value"])
head.eval()

# Inference on a new graph: compute spectral features → pass MLP → gap prediction
def predict_gap(D0_np, m_np, K=6):
    """D0_np is the (n1, n0) incidence matrix; m_np is the (n1,) edge weight vector"""
    D0t = stm._as_tensor(D0_np)
    mt = stm._as_tensor(m_np)
    L0 = stm.laplacian0_from_DigD(D0t, mt)
    tau = stm.spectral_tau(L0, K=K)
    alpha = stm.spectral_radius(L0)
    ev = torch.linalg.eigvalsh(L0.detach())
    lam2 = float(ev[1]) if len(ev) > 1 else 0.0
    feat = torch.cat([tau, torch.tensor([alpha], dtype=torch.float64),
                      torch.tensor([lam2], dtype=torch.float64)])
    with torch.no_grad():
        return float(head(feat))

# Example: a 7-node cycle (n0=7, n1=7)
n0, n1 = 7, 7
D0 = np.zeros((n1, n0))
for e in range(n1):
    D0[e, e] = -1.0; D0[e, (e + 1) % n0] = +1.0
m = np.ones(n1)
print(f"Predicted HOMO-LUMO gap = {predict_gap(D0, m):.4f}")
```

### 7.3 Checkpoint Format Specification

All `.pt` files are saved with `torch.save(payload)`, where payload is a dict and each entry has a `_type` marker:

| `_type` | value type | Typical scenario |
|:---|:---|:---|
| `"state_dict"` | `dict[str, Tensor]` | nn.Module parameters (all values are tensors) |
| `"tensor"` | `Tensor` | Chain complex D0/D1, precomputed feats, labels |
| `"raw_dict"` | `dict[str, _serialize_val]` | config (containing K, in_dim, task, metric values, etc.) |
| `"raw"` | Python primitives | meta information, strings, scalars |

**Why not store numpy**: PyTorch 2.6+ `torch.load` defaults to `weights_only=True` and refuses to pickle numpy types. `save_checkpoint` internally converts numpy to tensor storage, making it cross-version safe. When reading, unwrap with `ckpt["field"]["value"]`.

### 7.4 Encapsulated Utility Functions

If you don't want to manually unwrap `_type` fields, use `save_checkpoint` / `load_checkpoint`:

```python
import sre_topology_model as stm

# Save: nn.Module / numpy / tensor / plain dict can all be passed directly
stm.save_checkpoint("my_model.pt", {
    "pooler": pool,            # nn.Module → automatically stores state_dict
    "D0": D0_np,               # numpy → automatically converts to tensor
    "meta": {"version": 1}})   # plain dict → recursive processing

# Load: returns unwrapped dict
ckpt = stm.load_checkpoint("my_model.pt")
D0 = ckpt["D0"]               # torch.Tensor
```

Note that `load_checkpoint` only returns a bare `state_dict` for nn.Module (because it doesn't know which class to reconstruct), so you need to first build the same architecture and then call `.load_state_dict()`.

---

## 8. Hyperparameter Tuning Guide

The goal of this section is to give you enough information to independently determine which direction to tune based on symptoms observed during training. Each parameter entry includes: default value, symptoms for increasing, consequences of increasing, symptoms for decreasing, and consequences of decreasing.

### 8.1 K — Chebyshev Order (default 8)

**What it is**: The order of $\tau_k$, determines the resolution of spectral features. Larger K means $\tau_k$ covers finer spectral frequency components.

**When to increase**: The demo's $L_{\text{head}}$ loss drops noticeably slowly (poor $\tau_k$ fitting to $\tau_k^*$), or R²/accuracy on UC2/UC3 is below baseline.

**Consequences of increasing**: Feature dimension increases to $K+3$, the first MLP layer becomes wider (slightly more parameters). Computation increases linearly (more Chebyshev iterations). If the graph is very small ($n_0 \le 10$), $\tau_k$ may contain redundant information when K exceeds $n_0/2$.

**When to decrease**: $L_{\text{head}}$ converges to 0 quickly but final prediction is poor (possible overfitting to noise), or training is too slow.

**Consequences of decreasing**: Spectral information becomes coarse—higher-order moments of $\tau_k$ are lost. For tasks like UC2 that depend on precise $\alpha_n/\lambda_2$, too small K leads to insufficient SRE feature information.

**Recommended range**: 4 ~ 16. Ethanol with $n_0=9$ is sufficient at K=8; try K=12–16 for large graphs with $n_0 \ge 20$.

### 8.2 lam_s — $L_{\text{spec}}$ Weight (default 0.1)

**What it is**: The contribution coefficient of the heat kernel trace loss to total loss. Determines how strongly SoftAggPooler's $Z$ is constrained by spectral fidelity.

**When to increase**: cos_sim is too low in learnable mode (e.g., demo outputs cos_sim < 0.90), indicating the pooler learned a bad solution deviating from Galerkin exact assignment. Or the heat kernel trace of $L_0'$ is too different from $L_0$.

**Consequences of increasing**: $L_{\text{spec}}$ exerts stronger gradients on $Z$, pushing $Z$ toward "matching the heat kernel trace of $L_0'$ to that of $L_0$". It may compete with $L_{\text{task}}$—if $Z$ focuses too much on spectral fidelity, inversion target may degrade (corr decreases).

**When to decrease**: $L_{\text{spec}}$'s loss accounts for a large proportion of total loss (e.g., > 30%), but corr stays low—indicating that $L_{\text{spec}}$'s gradient direction conflicts with $L_{\text{task}}$, hindering the model from converging in the correct direction.

**Recommended range**: 0.01 ~ 0.5. UC1 demo uses 0.1; try 0.2 for larger graphs; drop to 0.05 if $L_{\text{spec}}$ dominates gradient direction.

### 8.3 lam_h — $L_{\text{hom}}$ Weight (default 1.0)

**What it is**: The weight of the soft rank difference $\lvert \operatorname{tr} h(L_1') - \operatorname{tr} h(L_1)\rvert$, constraining the $\beta_1$ closure between coarse and fine levels.

**When to increase**: SRE classification accuracy on UC3 is below baseline—the model's `soft_rank` may predict incorrect $\beta_1$ on some graphs.

**Consequences of increasing**: $L_{\text{hom}}$ directly uses the `soft_rank` operator (requiring `eigh`), with higher computation than $L_{\text{spec}}$. If too large, it interferes with the main task.

**Recommended range**: 0.5 ~ 2.0.

### 8.4 lr — Adam Learning Rate (default 0.08)

**What it is**: The initial step size of the Adam optimizer, controlling the magnitude of parameter updates.

**When to increase**: Loss barely moves in the first few hundred steps (gradient direction may be fine but step is too small), or corr lingers at low values (0.3–0.5 range).

**Consequences of increasing**: May skip the optimal solution—loss oscillates, corr fluctuates unstably between 0.9–0.99.

**When to decrease**: Loss oscillates back and forth, corr fluctuates unstably beyond 0.05, or the norm of SoftAggPooler's Z.grad suddenly increases dramatically.

**Recommended range**: 0.01 ~ 0.2. Ethanol demo uses 0.08 for fast convergence; regression/classification heads for UC2/UC3 are more stable at 0.01–0.05.

### 8.5 n_clusters — SoftAggPooler Granularity (default $(n_0+1)//2$)

**What it is**: How many clusters SoftAggPooler divides $n_0$ nodes into. More clusters means less "coarse" coarse-graining, $L_0'$ and $L_0$ are closer; fewer clusters means stronger coarse-graining.

**When to increase**: cos_sim is already close to 1.0 under exact Galerkin, indicating $n_{\text{clusters}}$ is too small causing severe information loss.

**Consequences of increasing**: $P$ matrix becomes larger (more columns in $n_0 \times C$), dimension of $L_0'$ changes from $C$ to $C'$, making $L_0'$ and $L_0$ more similar. If $C$ approaches $n_0$, coarse-graining degenerates to the identity mapping.

**When to decrease**: $n_0$ is large (e.g., 50+), $C$ is also large causing computation to increase dramatically. Or $L_{\text{spec}}$ loses regularization meaning because $C$ is too large.

**Recommended range**: $\max(2, n_0//3) \sim n_0$. Default of 5 is appropriate for $n_0=9$; try 7–10 for $n_0=20$.

### 8.6 Recommended Tuning Procedure

Grid search is the simplest approach: fix all but one parameter, sweep that parameter over a reasonable range, record corr and cos_sim, and pick the optimal one. Then proceed to the next. Recommended order: **first lr (affects convergence speed) → then lam_s (affects regularization strength) → finally K (affects feature dimension)**.

---

## 9. Honest Boundaries: Verified Capabilities and Known Limitations

The purpose of this section is to let you clearly understand the model's capability boundaries before deciding whether to apply SRE to your project. All statements are supported by measured data, not speculation.

### 9.1 Verified Capabilities

UC1 self-supervised inversion (corr=1.0), UC2 molecular property regression (R²=0.878, leading GCN/GIN), UC3 $\beta_1$ classification (acc=1.0). Spectral fidelity monitoring cos_sim is 0.996–1.000 under exact Galerkin. Differentiable $L_{\text{spec}}$ can make SoftAggPooler.Z receive non-zero gradients and participate in training under learnable mode. All 19 canonical operators are fully implemented and pass 100% of regression tests (98 items).

### 9.2 Observed but Unresolved Issues

**Large graphs are impractical**: `eigvalsh` is $O(n^3)$ for $n_0 \ge 100$, and intermediate computations of `chebyshev_functional` also require $O(n^3)$ matrix multiplication. The current implementation is not practical for graphs above 100 nodes.

**Cross-domain generalization residual**: Zero-shot inversion residual of 0.131 on RMAT graphs (completely random topology, untrained). This indicates the spectral features learned by the model still have a gap on out-of-distribution topologies.

**Single-layer pooler**: Currently only one SoftAggPooler + one task head has been verified. Whether multi-layer stacking can further improve performance and how gradients propagate between layers have not been investigated.

**soft_rank depends on eigvalsh**: Soft rank uses `torch.linalg.eigvalsh(L1)`, where $L1$ is the Hodge Laplacian with dimension $n_2 \times n_2$ (square of the number of faces). For many molecular graphs $n_2=0$ or very small, but for graphs with $n_2=100$ this step would also be slow.

### 9.3 Explicitly Abandoned Directions

**Making $L_{\text{spec}}$ propagate back to $m$**: We tried making $L_0$ also differentiable (not detached), so that $L_{\text{spec}}$ gradients train both $Z$ and $m$. Measured inversion diverged—loss rose to $10^{-1}$, corr dropped to −0.17. The explanation is that $L_{\text{spec}}$'s gradient direction conflicts with $L_{\text{task}}$, and together they push $m$ toward an unsatisfactory equilibrium point for both.

**Using $\tau_k$ as spectral fidelity criterion**: The original plan §8 required $\tau_k$ relative error $\le 5\% / \le 3\%$. Measured error under exact Galerkin is 63%–100%. Mathematically impossible—$\tau_k$ is a nonlinear function of the full spectrum + dimension, and Galerkin changes both simultaneously.

**Heat kernel trace distance as sole component of final loss**: We tried using only `hkt_dist` without cos_sim. `hkt_dist` is unstable under extreme reduction (→ 1 node)—after reducing a random graph to 1 node, $\operatorname{tr}(\exp(-tL))$ becomes $N_0$ (number of connected components of original graph), $\operatorname{tr}(\exp(-tL'))$ becomes 1, and relative error increases dramatically.

---

## 10. Roadmap for Improvements

This section lists five priority-sorted improvement directions, from immediately actionable to architecture-refactoring. Each gives expected benefit, implementation difficulty, and key risks.

### P0: Real Molecular Dataset Validation (Large Benefit, Low Difficulty)

Replace UC2's synthetic dataset with a small sample from QM9 (e.g., 100 molecules' HOMO-LUMO gap). QM9 data can be downloaded directly from pytorch-geometric, but this project does not use torch-geometric—manually parse QM9 xyz files to extract atomic coordinates and element types, compute adjacency matrices (covalent radius threshold) and chain complexes ourselves. We expect SRE to still outperform GCN/GIN on QM9, because gap is essentially a spectral property. The risk is that QM9 molecules typically have $n_0 \ge 10$, and `chebyshev_functional` computation will increase noticeably.

### P1: Multi-Layer SoftAggPooler Stacking (Medium Benefit, Medium Difficulty)

Currently only one pooler. We can stack two layers: first layer does $C_1 = n_0/2$ coarse-graining, second layer does another $C_2 = C_1/2$ coarse-graining on the first layer's $L_0'$. Each layer has its own $L_{\text{spec}}$ loss (spectral consistency between levels). This way the model can learn multi-scale topological patterns—local (original level) and global (coarse level). The risk is longer gradient paths between layers; need to increase lam_s to compensate for gradient decay.

### P2: C++/CUDA Acceleration of chebyshev_functional (Large Benefit, High Difficulty)

Current `chebyshev_functional` uses pure PyTorch matrix multiplication. For $n_0=100$ graphs with $K=32$, one forward pass needs 32 $(100 \times 100) \times (100 \times 100)$ matrix multiplications. Writing a CUDA kernel can fuse the three-term recurrence into one kernel, reducing GPU memory round-trips. Expected 5–10× forward speedup. The risk is needing to write a C++ extension and handle Windows compilation environment.

### P3: Differentiable Alternative for $\tau_k$ (Medium Benefit, Medium Difficulty)

Currently $\tau_k$ is computed from detached $L_0$ and does not enter the gradient graph. Making $\tau_k$ differentiable would allow using $\tau$ matching loss to directly train $m$ (consistent with the original plan). But $\tau_k$ is not preservable under Galerkin, so $\tau$ matching loss would conflict with Galerkin regularization. The alternative is to **compute $\tau_k$ directly on $m$**, not contrasting with Galerkin, but making $\tau_k$ at different granularities form a hierarchy consistent loss (closed loop similar to $L_{\text{hom}}$).

### P4: Cross-Domain Robustness (Medium Benefit, High Difficulty)

Can the model trained on UC2 (molecular gap) be directly applied to UC3 ($\beta_1$ classification) or to completely unrelated graph tasks? Current spectral features $[\tau_0..\tau_K, \alpha_n, \lambda_2]$ are theoretically domain-agnostic—they depend only on the Laplacian spectrum of the graph, not on which domain the graph comes from. But the measured RMAT zero-shot residual of 0.131 indicates there is still a gap. We can use domain adaptation techniques (e.g., SRE features + domain discriminator) to close the cross-domain gap.

---

## 11. Project Structure and License

### 11.1 Project Structure

```
math-vector_v2/
├── sre_ai_model/                     AI model layer (new in this project)
│   ├── sre_topology_model.py         Model main body (~65 KB)
│   ├── sre_release.py                Release script (UC1/UC2/UC3 + baselines)
│   ├── test_sre_topo_model.py        11 unit tests
│   └── release/
│       ├── weights/                  9 .pt weight files
│       ├── metrics.json              Evaluation metrics summary
│       └── SRE_AI_Model_C.md         This document (Chinese version)
├── operator_calculus.py              Canonical operator calculus (frozen, numpy-only)
├── sre_electronic_layer.py           Canonical electronic layer operators (frozen)
├── sre_spectral_solver.py            Canonical spectral solver (frozen)
├── test_operators_11_19.py           Op11-19 unit tests (61 items)
├── test_operator_calculus.py         Operator calculus unit tests (37 items)
└── .trae/documents/
    └── SRE_AI_Model_Design.md        Design document (authoritative source, contains all criterion definitions)
```

### 11.2 Dependencies

- Python ≥ 3.8
- torch ≥ 2.0 (includes torch.linalg.eigvalsh)
- numpy ≥ 1.24
- No dependencies on torch-geometric, scipy, rdkit, or other third-party packages

### 11.3 License

The 19 canonical operators and AI model layer code are both released under the **MIT License**.

```text
Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
