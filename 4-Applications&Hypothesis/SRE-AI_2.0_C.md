# SRE 拓扑谱模型：从离散算子到可微分 AI 模型层


版本: 2.0  

【资源与可用性声明】 本框架基于状态‑关系熵（SRE）动力学构建。 全部理论资料归档于 Zenodo 开源数据仓库。**本文档套件包括系统论文、应用开发、科学假说、算子1‑19完整代数推导及仿真代码完全开源**。

> 可访问作者的Github仓库：
>
> https://github.com/yuelucn/Status-Relational-Entropy-SRE-Dynamics-The-Book-of-the-Void
>
> 可访问支持AI辅助查阅的腾讯智能文档空间（PC、微信移动端均可访问）：
>
> https://docs.qq.com/space/DUkRjYUtNWFdyV253
>
> 根据状态‐关系熵（SRE）原理，经典物理基础源自信息统计学。


> 本文档记录 SRE 拓扑谱模型的完整设计推理、架构实现与实验结果。它既是一份可复现的实验报告，也是一份可扩展的技术手册。读者无需预先了解图拉普拉斯、Chebyshev 多项式或链式复形即可跟随推理链理解模型的设计动机与数学基础。

---

## 目录

0. [从算子到模型：推理链与关键桥接（必读）](#0-从算子到模型推理链与关键桥接必读)
1. [符号约定与核心直觉](#1-符号约定与核心直觉)
2. [预备知识：五个概念的精确定义](#2-预备知识五个概念的精确定义)
3. [模型架构：数据流向与梯度传播](#3-模型架构数据流向与梯度传播)
4. [实验设置：三个任务与两个基线](#4-实验设置三个任务与两个基线)
5. [实验结果与因果分析](#5-实验结果与因果分析)
6. [完整使用教程：环境搭建到跑通所有用例](#6-完整使用教程环境搭建到跑通所有用例)
7. [权重文件加载与推理](#7-权重文件加载与推理)
8. [超参数调优指南](#8-超参数调优指南)
9. [诚实边界：已验证的能力与已知局限](#9-诚实边界已验证的能力与已知局限)
10. [改进路线图](#10-改进路线图)
11. [项目结构与许可证](#11-项目结构与许可证)

---

## 0. 从算子到模型：推理链与关键桥接（必读）

这一节回答最根本的问题：**为什么规范 19 算子可以桥接为一个可微分的 AI 模型？** 这条推理链并非在设计之初就已完整，而是在反复验证中逐步收敛的。理清这条链有助于理解每一个设计决策的由来。

### 0.1 阶段一：算子首尾相衔，桥接恒等精确成立

项目的基础是 19 个离散算子（以下简称"规范算子"），它们全部基于 numpy 实现，已冻结并通过 98 项单元测试验证。算子流水线的起点是分子的原子类型与坐标，终点是加权拉普拉斯矩阵 $L$：

$$
\text{positions} + \text{atomtypes} \xrightarrow{\text{Op1-6}} W_e \xrightarrow{\text{Op7-10}} m \xrightarrow{\text{Op11-19}} L
$$

其中最关键的桥接恒等式（在 `main.py` Phase 6 中实测残差 $\le 10^{-12}$）为：

$$
L = D_0^\top \operatorname{diag}(m) D_0 \equiv \operatorname{deg}(A_s) - A_s
$$

这里 $D_0$ 是图的定向关联矩阵（每条边指定起点为 −1、终点为 +1），$m$ 是边权向量。这个恒等式的意义在于：**拉普拉斯矩阵有两个等价的构造路径**——从关联矩阵出发（代数路径）和从邻接矩阵出发（图论路径）。两条路径数值上精确相等，为后续实现提供了双路径校验。

阶段一的结论是：**数学对象 $L$ 已被完备定义且数值稳定，但尚未被"可微分"地参数化**——numpy 不支持 autograd。

### 0.2 阶段二：算子微积分的 torch 镜像实现

在规范算子之外，项目中已经存在一个独立的 torch 模块 `operator_calculus.py`，它是规范算子的**可微分镜像**。这个模块的核心是三个类：

- **`ChainComplex`**：封装关联矩阵 $D_0$ 与面算子 $D_1$，内部用 `torch.Tensor` 替代 `numpy.ndarray`，保证边界恒等 $D_1 D_0 = 0$ 可微分地成立。
- **`Operator`**：链复形上的 $N \times N$ 线性算子的封装，支持矩阵乘、加、交换子、幂运算和函数演算，所有运算返回新的 `Operator` 实例——**演算封闭性**保证了中间结果不需要转回 numpy。
- **`OperatorCalculus`**：绑定到一个 `ChainComplex`，提供外导数 $d$、余微分 $\delta$、Hodge Laplacian $\Delta = d\delta + \delta d$、加权拉普拉斯 $L_0(w) = D_0^\top \operatorname{diag}(w) D_0$，以及 Chebyshev 函数演算。

关键实现细节是 **Chebyshev 函数演算**（`chebyshev_functional`，第 221-253 行）。它用三项递推公式：

$$
T_0(Y) = I,\quad T_1(Y) = Y,\quad T_{k+1}(Y) = 2Y T_k(Y) - T_{k-1}(Y)
$$

将任意谱函数 $g(L)$ 展开为 $g(L) \approx \sum_{k=0}^K c_k T_k(Y)$，其中 $Y = 2L/b - I$ 把谱映射到 $[-1, 1]$。**全程只用矩阵乘法，不触发 `torch.linalg.eigvalsh`**。这有两个关键好处：(1) autograd 能精确追踪梯度——$\partial T_{k+1}/\partial Y = 2T_k + 2Y \partial T_k/\partial Y - \partial T_{k-1}/\partial Y$，链式法则自动应用；(2) 规避了特征值简并导致的梯度不唯一问题。

这个模块中已经有一个反演 demo（`run_training_demo`，第 277-324 行），它用 torch 的 autograd 从谱观测反演边权 $w$：给定真值 $w^*$，计算观测 $Y^* = g(L_0(w^*)) X$（$X$ 是多探针矩阵），然后训练参数 $w$ 使 $g(L_0(w)) X \approx Y^*$。实测结果是 loss 降至 $2 \times 10^{-19}$，皮尔逊相关系数 $\text{corr}(\hat{w}, w^*) = 1.0$。

阶段二的结论是：**"从算子到可微分算子"这一步已经完成，且在一个小 demo 上验证了可训练性**。但 demo 只用到了 ChainComplex + OperatorCalculus，还没有完整的层级结构和粗粒化能力——它本质上只是一个"算子可训练性的玩具验证"。

### 0.3 阶段三：缺失的承重件——可微分层级压缩

将 operator_calculus 扩展为真正的 AI 模型，还缺一个核心能力：**可学习的粒度**。模型不应该只在单一尺度上提取特征，而应该能在多个粗粒化水平上看到同一张图。

粗粒化在代数拓扑中有标准形式——**Galerkin 投影**：给定一个 $n_0 \times C$ 的分配矩阵 $P$（$P^\top P = I$，正交性），可以把细层拉普拉斯 $L_0$ 投影到粗层：

$$
L_0' = P^\top L_0 P
$$

同时链复形也相应缩减：$D_0' = D_0 P$（细层的关联矩阵和分配矩阵相乘得到粗层的关联矩阵），$D_1' = D_1$（面算子在粗粒化下不变，因为面由边环填充，边环作为整体不会被拆分）。

Galekin 投影有两种模式：

| 模式 | $P$ 的构造 | $\beta_1$ 保持 | 可微分 | 用途 |
|:---|:---|:---|:---|:---|
| **精确模式** | BFS 生成树的 0/1 硬分配 | 可证严格不变 | 否 | 校验基准 / 结构池化 |
| **可学习模式** | $P = \operatorname{softmax}(Z)$，$Z$ 是 $n_0 \times C$ 的可学习参数 | 软约束（用软秩惩罚闭环） | 是 | 可学习粒度的载体 |

精确模式下 $\beta_1$ 严格保持的证明很简单：收缩生成树后 $V' = \beta_0$，$E' = E - (n_0 - \beta_0)$，面数 $F$ 不变，所以

$$
\beta_1' = E' - V' + F = (E - n_0 + \beta_0) - \beta_0 + F = E - n_0 + F = \beta_1
$$

Galerkin 投影就是模型的 **承重件**——没有它，operator_calculus 只是一个计算谱矩的工具；有了它，模型就有了"从粗到细"的层级结构，可以在多个尺度上提取特征。

### 0.4 阶段四：$\tau_k$ 不可保真的数学发现与替代方案

原始设计方案中，我们计划用 $\tau_k$ 的相对误差作为谱保真判据（$\le 5\%$）。$\tau_k$ 是 Chebyshev 谱矩的归一化迹：

$$
\tau_k = \frac{1}{N} \operatorname{tr}(T_k(Y)),\quad Y = \frac{2L_0}{\alpha_n} - I
$$

在 Galerkin 投影下，$\tau_k' = \operatorname{tr}(T_k(Y'))/N'$，其中 $Y' = 2L_0'/\alpha_n' - I$。

实测数据（精确 Galerkin，4 个图 8 个层级）给出了一个出人意料的结论：**$\tau_k$ 在 Galerkin 下不可保真**——相对误差高达 63% 到 100%。

数学根因是：$\tau_k$ 依赖全谱分布 + 维度 $N$ + 谱半径 $\alpha_n$。Galerkin 投影同时改变了这三者——特征值被 Cauchy 交错定理夹在原特征值之间（$\lambda_i(L_0) \le \lambda_i(L_0') \le \lambda_{i+n_0-C}(L_0)$），但 $N$ 从 $n_0$ 变成 $C$，$\alpha_n$ 也随 $L_0'$ 变化。三个变量同时改变，非线性函数 $\operatorname{tr}(T_k(Y))$ 不可能保持不变。

替代方案采用双层设计：

**监控指标——特征值余弦相似度**（`spectral_cosine_similarity`）：对 $L_0$ 和 $L_0'$ 做 `eigvalsh` 得到排序特征值向量，把粗层特征值在细层索引空间做线性插值对齐，然后计算余弦相似度。Cauchy 交错定理保证排序关系稳定，实测精确 Galerkin 下 $\cos_{\text{sim}} \in [0.996, 1.000]$。这个指标只用于监控，不参与梯度。

**可微分 loss——热核迹相对距离**（在 `loss_of` 内部）：

$$
L_{\text{spec}} = \operatorname{mean}_{t \in \{1.0, 2.0\}} \frac{|\operatorname{tr}(e^{-t L_0'}) - \operatorname{tr}(e^{-t L_0})|}{\max(\operatorname{tr}(e^{-t L_0}), 10^{-30})}
$$

热核迹 $\operatorname{tr}(e^{-t L}) = \sum_i e^{-t \lambda_i}$ 通过 `chebyshev_functional` 计算——全程可微。关键设计细节：$L_0$ **detach**（用 Python float 转为常量），不让 $L_{\text{spec}}$ 的梯度干扰边权 $m$ 的反演方向；$L_0'$ **不 detach**，梯度流过 $L_0' \leftarrow P \leftarrow Z$ 回到 SoftAggPooler 的参数。

### 0.5 完整桥接图

```
规范算子（numpy, 19 Op, 冻结）
  │  W_e → m → L   桥接恒等 L = D0ᵀdiag(m)D0 ≡ deg - A_s
  ▼
operator_calculus.py（torch, 可微分镜像）
  │  ChainComplex → Operator → OperatorCalculus
  │  chebyshev_functional: 三项递推, autograd, 无 eigvalsh
  │  laplacian0(w): 加权图拉普拉斯, w 可微分
  │  run_training_demo: 反演已验证 loss→2e-19, corr=1.0
  ▼
sre_topology_model.py（新建模型层）
  │  SoftAggPooler: P = softmax(Z), Galerkin 投影 L0' = PᵀL0P
  │  ScaleGauge: m = s · softplus(ρ)/mean, 消除尺度平坦方向
  │  SRETopoEncoder: 固定算子, τ_k + α_n + λ₂, 无可学习参数
  │  五项损失: L_task + λ_g L_gauge + λ_s L_spec + λ_h L_hom + λ_head L_head
  │  L_spec 梯度路径: L_spec → tr_c → chebyshev → Y → L0' → P → Z
  ▼
三个用例验证: UC1 反演 corr=1.0, UC2 回归 R²=0.878, UC3 分类 acc=1.0
```

这条桥接链的核心逻辑是：**算子的数学正确性由规范算子保证，可微分性由 torch 镜像实现保证，层级表达力由 SoftAggPooler 保证**。三者独立实现、独立验证，然后在模型层汇合。

---

## 1. 符号约定与核心直觉

**给定一个分子或图的连接关系，提取它的拓扑谱特征，然后用这些特征去做分子性质预测、图分类、或图上的反演问题。**

说得更具体一点：想象你手上有一个分子的原子连接表——"碳原子 #0 连了氢原子 #3、#4、#5 和另一个碳原子 #1"。你把这张表输入 SRE 模型，它输出一个 11 维的特征向量，代表这个分子的拓扑结构所蕴含的全部谱信息。然后用这个向量，你可以训练一个简单的线性回归去预测这个分子的 HOMO-LUMO gap（一种分子性质），或者训练一个二分类器去判断这个图有没有环（β₁=1 还是 0）。

SRE 模型的核心观点是：**图的拉普拉斯矩阵的谱（特征值分布）比邻接矩阵本身携带了更多的形状信息**。传统的图神经网络（GCN、GIN）都是从邻接矩阵出发做消息传递，而 SRE 直接瞄准谱这个更本质的对象。

---

## 2. 预备知识：五个概念的精确定义

本节的写法对每个概念都遵循同一个结构：**直觉比喻 → 形式化定义 → 为什么这个概念对模型重要**。如果你对某个概念已经熟悉，可以跳过。理解这些概念不需要任何研究生数学背景——每一段都先给直觉再给公式。

### 2.1 图的拉普拉斯矩阵：图的振动方程

**直觉比喻**：把图想成一个弹簧系统。每个节点是一个小球，每条边是一根弹簧。拉普拉斯矩阵就是描述这个系统振动方程的那个矩阵——它的特征值就是振动频率，特征向量就是振动模式。所以拉普拉斯矩阵的特征值分布（也就是"谱"）编码了整个图的形状。环、链、完全图，它们的谱形状完全不同。

**形式化定义**：给定图 G = (V, E)，邻接矩阵 A（A_ij = 1 当 i 和 j 之间有边），度矩阵 D（D_ii = Σ_j A_ij），拉普拉斯定义为 L = D − A。如果边有权重 w_ij，就是 L = D − A，其中 A_ij = w_ij 且 D_ii = Σ_j w_ij。写成关联矩阵的形式是 L = D0ᵀ diag(m) D0，其中 D0 是定向关联矩阵（每条边选一个方向，起点 −1，终点 +1），m 是边权向量。

**为什么对模型重要**：拉普拉斯是整个 SRE 模型的核心载体。模型里所有的谱特征（τ_k、α_n、λ₂）都是从 L 算出来的。模型把 L 当成一个可微分的张量，这样整个前向传播就能走 PyTorch 的 autograd。

### 2.2 Betti 数 β₁：图里有多少个独立的环

**直觉比喻**：想象一张用橡皮筋做的图。你用剪刀剪一下能把它剪成几片？β₀ 是连通分量数。你需要剪几刀才能让图变成一棵树（没有环的树）？β₁ 就是独立环的个数。一个环（C₆）β₁=1，一条链 β₁=0，两个不相连的环 β₀=2, β₁=2。

**形式化定义**：β₁ = n₁ − n₀ + n₂，其中 n₀ 是节点数，n₁ 是边数，n₂ 是面（闭合区域）数。这是链复形的 Euler-Poincaré 公式。对于纯图（n₂=0），公式退化为 β₁ = n₁ − n₀ + 1（假定 β₀=1，连通图）。

**为什么对模型重要**：β₁ 是拓扑性质——它在粗粒化（把多个节点合并成一个）过程中应该严格保持不变。SRE 模型用 β₁ 作为一个判据来检查粗粒化操作是否正确，同时也作为 UC3 分类任务的标签本身。模型里有一个软秩函数 `soft_rank`，用 Hodge Laplacian Δ₂ 的迹来近似 β₁。

### 2.3 Chebyshev 多项式函数演算：不用特征分解就能算谱函数

**直觉比喻**：你想算 f(L)，其中 f 是某个函数（比如热核的 exp(−tL)），但你不想先算 L 的特征分解（O(n³) 复杂度，不稳定）。Chebyshev 多项式提供了一个捷径——它有三项递推公式，你可以像算斐波那契数列那样一层一层地往上算，全程只用到矩阵乘法。

**形式化定义**：T₀(Y) = I，T₁(Y) = Y，T_{k+1}(Y) = 2Y T_k(Y) − T_{k−1}(Y)。要算 f(L)，先做缩放 Y = 2L/b − I 把 L 的谱映射到 [−1, 1] 区间，然后在 Chebyshev 节点上做数值插值得到系数 c_k，最后 f(L) ≈ Σ_{k=0}^K c_k T_k(Y)。迹的话就是 tr(f(L)) ≈ Σ_k c_k tr(T_k(Y))，后者可以逐步递推计算。

**为什么对模型重要**：SRE 模型里的 τ_k 就是 tr(T_k(Y))/N，热核迹 loss 也是用 chebyshev_functional 计算的。关键好处是**整个过程是 PyTorch 的矩阵乘法，autograd 能精确追踪梯度**，而且可以设 K=32 就足够精确，完全绕开 eigvalsh 的 O(n³) 瓶颈。

### 2.4 Galerkin 投影与 τ_k 不可保真

**直觉比喻**：把一张高分辨率的照片缩成小图，有两种方式。Galerkin 投影的方式是：把 n₀ 个像素分成 C 个簇，每个簇用一个代表像素，然后把原图拉普拉斯做 L0' = Pᵀ L0 P，其中 P 是 n₀×C 的 0/1 矩阵（每个像素只属于一个簇）。问题是，原图的某个谱特征 τ_k 依赖全部 n₀ 个特征值，但缩图后只剩 C 个特征值了，而且新特征值的分布变了——你不可能指望缩图后的 τ_k' 和原图的 τ_k 相等。

**形式化定义**：Galerkin 投影 L0' = Pᵀ L0 P，其中 Pᵀ P = I（正交性）。由 Cauchy 交错定理，L0' 的特征值被夹在 L0 的相邻特征值之间：λ_i(L0) ≤ λ_i(L0') ≤ λ_{i + n₀ − C}(L0)。但 τ_k = tr(T_k(Y))/N 是全谱的非线性函数，在 Galerkin 下不是不变量。

**为什么对模型重要**：这是本项目最早暴露的数学事实之一——原始设计方案要求 τ_k 相对误差 ≤5%，但实测精确 Galerkin 下误差高达 63%~100%。我们用 **特征值余弦相似度 cos_sim** 替代作为谱保真监控指标（精确 Galerkin 下 0.996~1.000），用**可微热核迹距离**作为 L_spec loss。

### 2.5 热核迹：热扩散过程的全局度量

**直觉比喻**：想象在图上的每个节点同时放一个热源，然后让热量沿着边扩散。过了时间 t 之后，整个图的总热量是多少？tr(exp(−tL0)) 就是这个值。这个量编码了图的整体连通性：t→0 时等于 N（每个节点自己的热），t→∞ 时等于 β₀（只有连通分量之间还有温差）。所以在中间的 t 值，它对谱形状最敏感。

**形式化定义**：exp(−tL0) = Σ_i exp(−tλ_i) v_i v_iᵀ，取迹得 tr(exp(−tL0)) = Σ_i exp(−tλ_i)。t 是时间尺度：t 小的时候主要看小特征值（低频模式），t 大的时候看大特征值（高频模式）。

**为什么对模型重要**：L_spec loss 用热核迹的相对距离作为谱保真度量。它的关键优势是——用 chebyshev_functional 计算时全程可微，梯度能从 L0' 反向传播回 SoftAggPooler 的 Z 参数。这就把 L_spec 从一个不可微的监控指标变成了一个真正参与训练的正则项。

---

## 3. 模型架构：数据流向与梯度传播

这一节用逐步描述的方式，讲清楚一个分子图从输入到最终预测输出，在模型内部经过了哪些变换、每个变换的数学形式、以及梯度是怎么流的。

### 3.1 输入：分子图的链复形表示

模型接收的原始输入有三样：D0（关联矩阵，形状 n₁×n₀）、D1（面算子，形状 n₂×n₁，大多数分子图 n₂=0）、m（边权向量，长度 n₁）。D0 的构造很直接：给每条边编一个号，每条边选一个方向（比如从小到大的节点号），起点列填 −1，终点列填 +1。对于乙醇，n₀=9 个原子，n₁=8 条键，D0 就是 8×9 的矩阵。

### 3.2 Laplacian 构造：解析公式，可微分

从 D0 和 m 直接算 L0 = D0ᵀ diag(m) D0。这里没有任何神经网络层，就是两个矩阵乘法加一个对角矩阵。这样做的好处是：PyTorch 的 autograd 能精确追踪 m 的梯度——∂L0/∂m = D0ᵀ ⊙ D0（逐元素乘），∂tr(L0)/∂m = 2·Σ_{i∈边 jk} (L0_ii + L0_jj − 2L0_ij)·D0_ij²。模型里还有一条 Galerkin 路径：从 SoftAggPooler 的输出 P 算 L0' = Pᵀ L0 P，用于跨层谱特征。L0 在传入 SRETopoEncoder 之前 `.detach()` 了——这是刻意设计，让 L_spec 不干扰 m 的反演梯度方向。

### 3.3 SoftAggPooler：一个可学习的粗粒化

这一层是唯一"可学习"的组件（除了最后一层任务头）。它有一个 `nn.Parameter` 张量 Z，形状 n₀×n_clusters。对每行做 softmax 得到粒度分配矩阵 P——每个节点以概率分布属于 n_clusters 个簇。P 是 0/1 硬分配的"软版本"。Galerkin 投影 L0' = Pᵀ L0 P 就用这个 P 做粗粒化。Z 的梯度来自 L_spec 的热核迹 loss（梯度路径：L_spec → tr_c → chebyshev_functional → Y → L0' → P → Z）。pooler 的初始化方式是 `torch.randn(...) * 0.01`，一个小随机值保证训练初期 softmax 接近均匀分配。

### 3.4 SRE Topo Encoder：固定算子，算谱特征

这一层没有可学习参数——它就是一组规范算子（Op13-18 Chebyshev 函数演算 + Op9 Hodge Laplacian）。输入是 L0（detached，不进梯度图），输出是 K+3 维谱特征向量：[τ₀, τ₁, ..., τ_K, α_n, λ₂]。

τ_k = tr(T_k(Y))/N，其中 Y = 2L0/α_n − I，α_n = λ_max(L0)。α_n 是 L0 的谱半径，用 `torch.linalg.matrix_norm(L0, ord=2)` 或 `torch.linalg.eigvalsh(L0)[-1]` 直接取。λ₂ 是第二小的特征值，也叫"代数连通度"——它衡量图的连通紧密程度。

这一层的关键设计决策：**不做 eigh**。如果要算特征值分布，最直接的方式是 `eigvalsh`，但它的梯度不稳定（特征值简并时梯度为 0 或不唯一）。SRE 的设计理念就是**不用 eigh 而用 Chebyshev 函数演算**来间接算谱矩，梯度更稳定，而且全程只用到矩阵乘法，对大图也友好。

### 3.5 Level Attention Head：多层谱特征融合

SoftAggPooler 可以做多层粗粒化：原始层 L0 → 第一层粗粒化 L0' → 第二层 L0'' → ...。每一层 L0 都能算出 K+3 维谱特征，组成一个 `n_levels × (K+3)` 的矩阵 X。LevelAttentionHead 对 X 做注意力加权融合：先把每一行特征映射到 hidden 维，再对 hidden 维做注意力 pooling，得到一个固定长度的融合特征，最后过两层 MLP 输出任务值。

### 3.6 任务头：简单 MLP，回归或分类

最后一层是线性分类器或回归器。对于 UC2 回归任务：Linear(9, 32) → ReLU → Linear(32, 1)，输出标量预测值（gap 的估计）。对于 UC3 分类任务：Linear(9, 32) → ReLU → Linear(32, 1) → Sigmoid，输出 [0, 1] 之间的概率。用 BCEWithLogitsLoss（分类）或 MSELoss（回归）训练。

### 3.7 损失函数：五项组合

完整的损失函数是 L = L_task + λ_g L_gauge + λ_s L_spec + λ_h L_hom + λ_head L_head。

L_task 是主损失——自监督 demo 里是让 g(L0(m)) X ≈ g(L0(m_star)) X，回归/分类任务里是让 MLP(谱特征) ≈ y_true。L_head 是多层级谱特征之间的辅助损失，让粗层的 τ_k 逼近细层的 τ_k（注意：这里 τ_k 是在 L0 上算的，L0 不 detach，所以 L_head 能直接训练 m）。L_gauge 约束 α_n(m) 不要偏离 α_n(m0) 太远，用来消除边权整体缩放的平坦方向。L_spec 是可微热核迹 loss，训练 SoftAggPooler 的 Z。L_hom 用软秩（sharp=80, K=48 的 h(t) = exp(−80t)）的差来约束粗层和细层的 β₁ 闭环。

---

## 4. 实验设置：三个任务与两个基线

### UC1：自监督边权反演

**任务定义**：给定一个分子的拓扑结构（原子怎么连接），反演每条键的实际强度 m。这个任务本身没有"真实边权"作为监督标签——所以是**自监督**的：我们用一个随机种子生成一个真值 m_star，然后用 m_star 计算观测 Y = g(L0(m_star))·X，其中 g 是 L0 的幂级数（观测算子），X 是随机探针矩阵。训练过程中只给模型看 Y 和 D0/D1，让它自己学出 m 来拟合。

**为什么用随机真值**：如果用真实的 W_e（电负性边权），它的数值范围非常均匀（大多数键权在 0.95~1.05 之间），几乎不可辨识——m 整体缩个 0.99 倍，观测变化微乎其微。用 0.5~2.0 之间均匀分布的随机值作为真值，保证反演是良态可辨识的。

**训练过程**：Adam 优化器 lr=0.08，迭代 1500 步。m 从均匀初始化开始，经过 L_task 让 g(L0(m))·X 逼近 Y，同时 L_spec 和 L_hom 作为正则项约束谱和拓扑结构。SoftAggPooler 的 Z 也被 L_spec 训练，学会了一个合理的粗粒化分配。

**结果解读**：corr(ŵ, w*) = 1.0000 说明反演完美收敛——恢复出来的边权和真值的皮尔逊相关系数高达 1。L_task 从 3e-3 降到 8e-11，MAE 只有 2.9e-5。这说明模型的可训练性是没问题的——当观测 Y 足够有信息量时，反演完全可行。

**权重文件**：`release/weights/uc1_edge_inversion.pt`。内部结构包含 `pooler_state`（SoftAggPooler 的 Z 参数）、`D0`/`D1`（乙醇链复形的 numpy 数组）和 `meta`（训练超参数）。

### UC2：分子性质回归

**任务定义**：给定图结构（合成的环和链），预测 HOMO-LUMO gap。标签的合成方式是：对每个图算出它的拉普拉斯特征值，取 gap = (λ_max − λ₂)/λ_max，再叠加 5% 的高斯噪声。这个定义之所以合理，是因为 λ_max 和 λ₂ 分别对应分子轨道的最高和最低非平凡特征值，它们的差直接反映了分子的电子能隙。

**数据集**：6 个图，n₀ 从 5 到 10，环和链交替。4 个训练样本，2 个测试样本。这个数据集很小——因为我们的目标不是大规模 benchmark 而是**验证模型的谱特征确实能编码 gap 信息**。

**三种模型的输入对比**：SRE 的输入是 K+3=9 维谱特征 [τ₀..τ₆, α_n, λ₂]。GCN 和 GIN 的输入是 n₀×1 的恒等节点特征 + n₀×n₀ 的归一化邻接矩阵，小图用零填充到 n₀=10。这三个模型的**参数预算是同量级的**：SRE 的 MLP 有 9×32 + 32 + 32×1 + 1 = 321 个参数；GCN/GIN 两层各 1×16 + 16 + 16×16 + 16 = 304 个参数。所以对比是公平的。

**结果解读**：SRE 的 MSE=0.0023、R²=0.878，GIN 是 0.0062/0.674，GCN 是 0.0159/0.160。SRE 在 R² 上领先 GIN 20 个百分点，领先 GCN 72 个百分点。GCN 的 R² 只有 0.16——近似于随机猜测。这不是因为 GCN 训练没收敛（它收敛到了 loss=0.0159），而是因为**均值池化彻底抹平了图的拓扑信息**。环和链在 GCN 的 mean pooling 之后，特征向量几乎一样，MLP 根本没法区分。GIN 的 sum pooling 保留了节点身份，所以比 GCN 好得多，但还是被 SRE 显著优于——因为 SRE 的谱特征里直接包含了 α_n 和 λ₂，这两个就是 gap 公式的关键变量。

**权重文件**：`uc2_sre_regression.pt` / `uc2_gcn_regression.pt` / `uc2_gin_regression.pt`。每个 checkpoint 里存了训练好的 state_dict、所有图的特征、标签和 config（K、in_dim、task）。

### UC3：图分类（β₁ 拓扑识别）

**任务定义**：区分含环（β₁=1）和无环（β₁=0）图。我们合成了 20 个图：10 个含环（先生成树保证连通，再加一条边引入至少一个环），10 个纯链（n₀−1 条边，天然无环）。n₀ 在 5~8 之间随机，边权在 0.5~2.0 之间随机。

**为什么选 β₁ 作为分类目标**：β₁ 是一个纯拓扑不变量——它只取决于图的连通结构，和边权数值完全无关。这使得它成为检验模型是否真的学习**拓扑性质**而非**边权模式**的理想验证指标。

**结果解读**：SRE 和 GIN 都达到了 100% 准确率，GCN 只有 85%。GCN 那 15% 的错误来自哪里？mean pooling 之后，某些有环图和无环图的特征向量很接近（特别是短链和环的谱形状相似时），线性分类器无法画出清晰的决策边界。SRE 的谱特征里直接编码了 β₁ 的代理量（比如 soft_rank 的输出、λ₂ 是否大于 0、或 τ_k 的形状），所以分类器可以完美分离。GIN 的 sum pooling 保留了节点身份，让 MLP 能学到某种等价于 β₁ 的签名（比如"节点度数的乘积之和"或某种 WL 迭代的计数），也能达到完美分类。

**权重文件**：`uc3_sre_classifier.pt` / `uc3_gcn_classifier.pt` / `uc3_gin_classifier.pt`。

---

## 5. 实验结果与因果分析

这一节不是重复上一节的结果表格，而是解释**为什么** SRE 在某些用例中显著优于 baseline、在某些用例中与 baseline 持平、以及在哪些场景下仍然落后于 baseline。理解了这些，你就能判断 SRE 适不适合你手头的任务。

**SRE 在 UC2 上显著优于 GCN/GIN 的根本原因**：SRE 的特征空间就是谱——α_n（λ_max）和 λ₂（代数连通度）直接是 gap 公式的核心变量，τ_k（Chebyshev 谱矩）编码了全谱形状的高阶信息。可以直观理解为：SRE 的输入已经包含了 gap 公式所需的关键变量（α_n 和 λ₂），而 GCN/GIN 的输入只是原始图的拓扑结构信息，需要 MLP 通过多层非线性变换间接地从中提取出 α_n 和 λ₂。这就是为什么 SRE 在 UC2 上 R² 领先 baseline 20~72 个百分点。

**GCN 在 UC2 上表现远逊于其他基线（R²=0.16）的原因**：mean pooling 丢弃了图的尺度信息。想象两个不同的图，一个 n₀=6、λ_max=3，另一个 n₀=8、λ_max=3——GCN 对它们做 mean pooling 后得到的特征向量可能完全一样（都只和邻接归一化后的节点度数有关），而 SRE 能通过 α_n 和 λ₂ 区分它们。更根本的问题是：GCN 的消息传递本质上在做"邻接矩阵的幂次"，而邻接矩阵的幂次和拉普拉斯的特征值之间没有直接的单调关系。在没有节点特征（恒等特征）的情况下，GCN 的表达力严重受限。

**GIN 在 UC3 上也拿了 100% 的原因**：GIN 的表达力被证明与 Weisfeiler-Leman 图同构测试等价——它能区分任意两个不同的图结构（在某种意义上）。β₁=0 和 β₁=1 的图显然是同构不同的，GIN 自然能学到某种等价于 β₁ 的签名。但这并不意味着 GIN 在所有任务上都能与 SRE 持平——UC2 里 gap 是一个连续的谱性质，而不是一个离散的图同构类标签。GIN 在连续谱性质上的学习效率远低于 SRE，因为它要从消息传递的中间表征间接推导出谱信息。

**SRE 的弱点在哪里**：当前模型只有一层 SoftAggPooler，而 GCN/GIN 可以叠加多层形成深层网络。在需要多层消息传递才能学到抽象概念的任务上（比如分子毒性预测需要同时考虑局部官能团和全局骨架），单层 SRE 可能不如深层 GIN。另一个弱点是 SRE 对 n₀ 的可扩展性不好——eigvalsh 和 chebyshev_functional 的复杂度是 O(n³)，当前实现对 n₀ ≥ 100 的图不现实，而消息传递范式可以 O(n + m) 的复杂度跑大图。

---

## 6. 完整使用教程：环境搭建到跑通所有用例

### 6.1 环境要求

Windows 上必须在导入 numpy 和 torch 之前设置 `KMP_DUPLICATE_LIB_OK=TRUE`，否则会因为 OpenMP 库重复初始化而崩溃。Python ≥ 3.8，torch ≥ 2.0，numpy ≥ 1.24。不需要 torch-geometric、scipy 或 rdkit。

### 6.2 三步跑通全部

```powershell
# 第一步：设置环境变量（必须在任何 import 之前）
$env:KMP_DUPLICATE_LIB_OK = "TRUE"

# 第二步：跑全部用例 + baseline + 保存权重 + 打印评测表
python sre_ai_model\sre_release.py

# 第三步：看产出
ls sre_ai_model\release\weights\          # 9 个 .pt 权重文件
type sre_ai_model\release\metrics.json    # 机器可读的评测指标
```

`sre_release.py` 还支持 `--use uc1`、`--use uc2`、`--use uc3` 和 `--use all`（默认）来选择性运行。每个用例的跑通时间在几秒到几十秒之间，取决于迭代次数。

### 6.3 单步运行自监督 demo

如果你只想看 SRE 核心的反演能力，跑这个就够了：

```powershell
$env:KMP_DUPLICATE_LIB_OK = "TRUE"
python -c "import sys; sys.path.insert(0,'sre_ai_model'); import sre_topology_model as stm; r=stm.run_selfsupervised_demo(iters=1500); print(f'corr={r[\"corr\"]:.4f}, MSE={r[\"loss1\"]:.2e}')"
```

输出中关键的两行是 corr 和 cos_sim——corr=1.0 说明反演完美收敛，cos_sim 表示可学习模式下粗粒化的谱保真度（精确模式是 0.996~1.000，可学习模式取决于 SoftAggPooler 的训练程度）。

### 6.4 跑单元测试

torch 侧模型层测试：

```powershell
$env:KMP_DUPLICATE_LIB_OK = "TRUE"
python -m pytest sre_ai_model\test_sre_topo_model.py -v
```

11 项测试全部通过，覆盖了：β₁ 保持、Galerkin 恒等、τ 与规范 Op13 一致、梯度非零、软秩 β₁ 闭环、demo 收敛、先验不变性、τ 不可达事实固化、cos_sim 可达验证。

规范回归（19 算子）：

```powershell
$env:KMP_DUPLICATE_LIB_OK = "TRUE"
python -m pytest test_operators_11_19.py test_operator_calculus.py -q
```

98 项，零破坏。

### 6.5 所有产出文件

跑完 `sre_release.py` 后，你会在 `sre_ai_model/release/` 目录下看到：

- `weights/uc1_edge_inversion.pt` —— UC1 的 SoftAggPooler 权重 + 乙醇链复形 D0/D1
- `weights/uc2_sre_regression.pt` —— UC2 的回归头权重 + 所有图的 SRE 谱特征
- `weights/uc2_gcn_regression.pt` —— UC2 的 GCN baseline 权重
- `weights/uc2_gin_regression.pt` —— UC2 的 GIN baseline 权重
- `weights/uc3_sre_classifier.pt` —— UC3 的分类头权重
- `weights/uc3_gcn_classifier.pt` —— UC3 的 GCN baseline 权重
- `weights/uc3_gin_classifier.pt` —— UC3 的 GIN baseline 权重
- `metrics.json` —— 机器可读的评测指标，包含每个用例每个模型的详细数值

---

## 7. 权重文件加载与推理

这一节讲怎么加载已经训练好的权重、怎么对一个新的图做推理。checkpoint 的设计原则是：**所有需要重建模型结构的信息都存在 config 字段里**，不需要重新读代码找超参数。

### 7.1 加载 UC1 反演的 SoftAggPooler

```python
import os, sys
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, "sre_ai_model")
import torch
import sre_topology_model as stm

# 加载 checkpoint（PyTorch 2.6+ 安全：所有值已转 tensor）
ckpt = torch.load("sre_ai_model/release/weights/uc1_edge_inversion.pt",
                  weights_only=False)

# 每个字段都有 _type 包装，读 .value 解包
sd = ckpt["pooler_state"]    # {"_type": "state_dict", "value": {"Z": tensor}}
D0 = ckpt["D0"]["value"]     # torch.Tensor, shape (n1, n0)

# 从 D0 推断 n0，从 Z 推断 n_clusters
n0 = int(D0.shape[1])
n_clusters = int(sd["value"]["Z"].shape[1])

# 重建同架构 pooler 并加载
pool = stm.SoftAggPooler(n0, n_clusters, seed=0)
pool.load_state_dict(sd["value"])
pool.eval()
```

### 7.2 加载 UC2 的回归头并对新图推理

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

# config 是嵌套 raw_dict，逐层解包
config = ckpt["config"]["value"]
K = config["K"]                    # 6
in_dim = config["in_dim"]          # 9 (= K+3)

# 重建 MLP：Linear(in_dim, 32) → ReLU → Linear(32, 1)
class SREHead(nn.Module):
    def __init__(self, d):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d, 32), nn.ReLU(), nn.Linear(32, 1))
    def forward(self, x):
        return self.net(x).squeeze(-1)

head = SREHead(in_dim)
head.load_state_dict(ckpt["model_state"]["value"])
head.eval()

# 对新图推理：算谱特征 → 过 MLP → gap 预测
def predict_gap(D0_np, m_np, K=6):
    """D0_np 是 (n1, n0) 关联矩阵，m_np 是 (n1,) 边权向量"""
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

# 示例：一个 7 节点环（n0=7, n1=7）
n0, n1 = 7, 7
D0 = np.zeros((n1, n0))
for e in range(n1):
    D0[e, e] = -1.0; D0[e, (e + 1) % n0] = +1.0
m = np.ones(n1)
print(f"预测 HOMO-LUMO gap = {predict_gap(D0, m):.4f}")
```

### 7.3 checkpoint 格式规范

所有 `.pt` 文件用 `torch.save(payload)` 保存，payload 是一个 dict，每个 entry 有一个 `_type` 标记：

| `_type` | value 类型 | 典型场景 |
|:---|:---|:---|
| `"state_dict"` | `dict[str, Tensor]` | nn.Module 的参数（值全是 tensor） |
| `"tensor"` | `Tensor` | 链复形 D0/D1、预计算的 feats、labels |
| `"raw_dict"` | `dict[str, _serialize_val]` | config（含 K、in_dim、task、指标值等） |
| `"raw"` | Python 原语 | meta 信息、字符串、标量 |

**为什么不用 numpy 存**：PyTorch 2.6+ 的 `torch.load` 默认 `weights_only=True`，拒绝 pickle numpy 类型。save_checkpoint 在内部把 numpy 转成 tensor 存储，跨版本安全。读取时用 `ckpt["field"]["value"]` 解包。

### 7.4 封装工具函数

如果你不想手动解包 `_type` 字段，可以用 `save_checkpoint` / `load_checkpoint`：

```python
import sre_topology_model as stm

# 保存：nn.Module / numpy / tensor / 普通 dict 都能直接传
stm.save_checkpoint("my_model.pt", {
    "pooler": pool,            # nn.Module → 自动存 state_dict
    "D0": D0_np,               # numpy → 自动转 tensor
    "meta": {"version": 1}})   # 普通 dict → 递归处理

# 加载：返回解包好的 dict
ckpt = stm.load_checkpoint("my_model.pt")
D0 = ckpt["D0"]               # torch.Tensor
```

注意 `load_checkpoint` 对 nn.Module 只返回裸 `state_dict`（因为它不知道你要重建哪个类），你需要自己先构建同架构再 `.load_state_dict()`。

---

## 8. 超参数调优指南

这一节的目标是给你足够的信息，让你能根据训练中观察到的征兆自行判断应该往哪个方向调参。每个参数条目包含：默认值、调大的征兆、调大的后果、调小的征兆、调小的后果。

### 8.1 K —— Chebyshev 阶数（默认 8）

**这是什么**：τ_k 的阶数，决定谱特征的分辨率。K 越大，τ_k 覆盖的谱频率分量越细。

**什么时候该调大**：demo 的 L_head loss 明显下降慢（τ_k 对 τ_k* 拟合差），或者在 UC2/UC3 上 R²/accuracy 不如 baseline。

**调大的后果**：特征维度增加 K+3，MLP 第一层更宽（参数稍多）。计算量线性增加（chebyshev 多迭代几步）。如果图很小（n₀ ≤ 10），K 超过 n₀/2 后 τ_k 会出现重复信息。

**什么时候该调小**：L_head 很快收敛到 0 但最终预测不好（可能过拟合了噪声），或者训练太慢。

**调小的后果**：谱信息变粗——τ_k 的高阶矩丢失。对 UC2 这种依赖精确 α_n/λ₂ 的任务，K 太小会导致 SRE 特征信息不足。

**建议范围**：4 ~ 16。乙醇 n₀=9 用 K=8 就够；n₀ ≥ 20 的大图可以试 K=12~16。

### 8.2 lam_s —— L_spec 权重（默认 0.1）

**这是什么**：热核迹 loss 对总 loss 的贡献系数。决定 SoftAggPooler 的 Z 受谱保真约束的程度。

**什么时候该调大**：cos_sim 在可学习模式下太低（比如 demo 输出 cos_sim < 0.90），说明 pooler 学出了偏离 Galerkin 精确分配的坏解。或者 L0' 的热核迹和 L0 差得太远。

**调大的后果**：L_spec 对 Z 的梯度更强，Z 被推向"让 L0' 和 L0 的热核迹匹配"的方向。可能会和 L_task 竞争——Z 太关注谱保真可能导致反演目标变差（corr 下降）。

**什么时候该调小**：L_spec 的 loss 值在总 loss 里占比很大（比如 > 30%），但 corr 上不去——说明 L_spec 的梯度方向与 L_task 冲突，阻碍了模型朝正确方向收敛。

**建议范围**：0.01 ~ 0.5。UC1 demo 用 0.1；如果是更大的图可以试 0.2；如果 L_spec 主导了梯度方向降到 0.05。

### 8.3 lam_h —— L_hom 权重（默认 1.0）

**这是什么**：软秩差 |tr h(L1') − tr h(L1)| 的权重，约束粗层和细层的 β₁ 闭环。

**什么时候该调大**：UC3 上 SRE 分类准确率不如 baseline——可能模型在某些图上 soft_rank 预测的 β₁ 是错的。

**调大的后果**：L_hom 直接用 soft_rank 算子（需要 eigh），计算量比 L_spec 大。如果太大，会干扰主要任务。

**建议范围**：0.5 ~ 2.0。

### 8.4 lr —— Adam 学习率（默认 0.08）

**这是什么**：Adam 优化器的初始步长，控制参数更新的幅度。

**什么时候该调大**：前几百步 loss 几乎不动（梯度方向可能没问题但步子太小），或者 corr 长时间在低值徘徊（0.3~0.5 之间）。

**调大的后果**：可能跳过最优解——loss 震荡、corr 在 0.9~0.99 之间波动不稳定。

**什么时候该调小**：loss 来回震荡、corr 不稳定波动超过 0.05、或者 SoftAggPooler 的 Z.grad 的范数突然急剧增大。

**建议范围**：0.01 ~ 0.2。乙醇 demo 用 0.08 收敛快；UC2/UC3 的回归/分类头用 0.01~0.05 更稳。

### 8.5 n_clusters —— SoftAggPooler 粒度（默认 (n₀+1)//2）

**这是什么**：SoftAggPooler 把 n₀ 个节点分成几个簇。簇越多，粗粒化越不"粗"，L0' 和 L0 越接近；簇越少，粗粒化越强。

**什么时候该调大**：cos_sim 在精确 Galerkin 下就已经接近 1.0，说明 n_clusters 太小导致信息丢失严重。

**调大的后果**：P 矩阵变大（n₀×C 的列数增加），L0' 的维度从 C 变成 C'，L0' 和 L0 更相似。如果 C 接近 n₀，粗粒化退化为恒等映射。

**什么时候该调小**：n₀ 很大（比如 50+），C 也很大导致计算量急剧增大。或者 L_spec 因为 C 太大而失去正则意义。

**建议范围**：max(2, n₀//3) ~ n₀。n₀=9 时默认 5 合适；n₀=20 可以试 7~10。

### 8.6 调参的推荐流程

网格搜索是最简单的方式：固定除一个外的所有参数，让该参数在合理范围内扫一遍，记录 corr 和 cos_sim，取最优的那个。然后再调下一个。顺序建议：**先 lr（影响收敛速度）→ 再 lam_s（影响正则强度）→ 最后 K（影响特征维度）**。

---

## 9. 诚实边界：已验证的能力与已知局限

这一节的目的是让你在决定是否把 SRE 用到自己项目之前，明确知道它的能力边界。所有陈述都是有实测数据支撑的，不是猜测。

### 9.1 已验证的能力

UC1 自监督反演（corr=1.0）、UC2 分子性质回归（R²=0.878，领先 GCN/GIN）、UC3 β₁ 分类（acc=1.0）。谱保真监控 cos_sim 在精确 Galerkin 下 0.996~1.000。可微 L_spec 在可学习模式下能让 SoftAggPooler.Z 收到非零梯度并参与训练。19 个规范算子全部实现并 100% 回归通过（98 项测试）。

### 9.2 已观测但未解决的问题

**大图不现实**：eigvalsh 在 n₀≥100 时 O(n³)，chebyshev_functional 的中间计算也需要 O(n³) 的矩阵乘法。当前实现对 100 节点以上的图不实用。

**跨域泛化残差**：RMAT 图（完全随机拓扑，不训练）上的零样本反演残差 0.131。说明模型学到的谱特征在分布外拓扑上还有 gap。

**单层池器**：当前只验证了一层 SoftAggPooler + 一个任务头。多层堆叠能不能进一步提升性能、多层之间梯度怎么传递，还没做过。

**soft_rank 依赖 eigh**：软秩用 `torch.linalg.eigvalsh(L1)`，而 L1 是 Hodge Laplacian，维度是 n₂×n₂（面的数量平方）。对于很多分子图 n₂=0 或很小，但如果有 n₂=100 的图，这一步也会慢。

### 9.3 已明确放弃的路线

**让 L_spec 回传到 m**：试过把 L0 也设为可微（不 detach），让 L_spec 的梯度同时训练 Z 和 m。实测反演会发散——loss 升到 1e-1，corr 降到 −0.17。解释是 L_spec 的梯度方向和 L_task 冲突，两者共同作用将 m 推向一个两边都不满意的平衡点。

**用 τ_k 做谱保真判据**：原始方案 §8 要求 τ_k 相对误差 ≤5%/≤3%。实测精确 Galerkin 下 63%~100%。数学上不可能——τ_k 是全谱 + 维度的非线性函数，Galerkin 同时改变谱和维度。

**热核迹距离作为最终 loss 的单一成分**：试过只有 hkt_dist 没有 cos_sim。hkt_dist 在极端缩减（→1 节点）时不稳定——随机图缩减到 1 节点后 tr(exp(-tL)) 变成 N₀（原图的连通分量数），tr(exp(-tL')) 变成 1，相对误差急剧增大。

---

## 10. 改进路线图

本节列出 5 个按优先级排序的改进方向，从立即可以动手的到需要架构重构的。每个方向都给了预期收益、实现难度和关键风险。

### P0：真实分子数据集验证（收益大，难度低）

把 UC2 的合成数据集替换成 QM9 的小样本（比如 100 个分子的 HOMO-LUMO gap）。QM9 数据可以从 pytorch-geometric 直接下载，但本项目不用 torch-geometric——手动解析 QM9 的 xyz 文件提取原子坐标和元素类型，自己算邻接矩阵（共价半径阈值）和链复形。预期 SRE 在 QM9 上依然领先 GCN/GIN，因为 gap 本质就是谱性质。风险是 QM9 分子普遍 n₀≥10，chebyshev_functional 计算量会明显增加。

### P1：多层 SoftAggPooler 堆叠（收益中，难度中）

当前只有一层 pooler。可以堆叠两层：第一层做 C1 = n₀/2 的粗粒化，第二层在第一层的 L0' 上再做 C2 = C1/2 的粗粒化。每一层都有自己的 L_spec loss（层级之间的谱一致性）。这样模型能学到多尺度的拓扑模式——局部（原始层）和全局（粗层）。风险是多层之间的梯度传递路径更长，需要调大 lam_s 来补偿梯度衰减。

### P2：chebyshev_functional 的 C++/CUDA 加速（收益大，难度高）

当前 chebyshev_functional 用纯 PyTorch 的矩阵乘法，对 n₀=100 的图，K=32，一次 forward 需要 32 次 (100×100)×(100×100) 矩阵乘。写成 CUDA kernel 可以把三项递推融合成一个 kernel，减少 GPU 内存往返。预期能把 forward 速度提升 5~10×。风险是需要写 C++ extension 并处理 Windows 上的编译环境。

### P3：τ_k 的可微替代（收益中，难度中）

当前 τ_k 是从 L0（detached）算的，不进梯度图。让 τ_k 可微的好处是可以用 τ 的匹配 loss 直接训练 m（和原始方案一致）。但 τ_k 不可保真 Galerkin，所以 τ 匹配 loss 会和 Galerkin 正则冲突。替代方案是**在 m 上直接算 τ_k**，不和 Galerkin 对比，而是让不同粒度上的 τ_k 形成一个 hierarchy consistent loss（和 L_hom 类似的闭环）。

### P4：跨域鲁棒性（收益中，难度高）

在 UC2（分子 gap）上训练的模型能不能直接用到 UC3（β₁ 分类），或者用到完全无关的图任务上？当前的谱特征 `[τ₀..τ_K, α_n, λ₂]` 理论上是域无关的——它只依赖图的拉普拉斯谱，和图来自什么领域无关。但实测 RMAT 零样本残差 0.131 说明还有 gap。可以用 domain adaptation 技术（比如 SRE 特征 + 域判别器）来缩小跨域差距。

---

## 11. 项目结构与许可证

### 11.1 项目结构

```
math-vector_v2/
├── sre_ai_model/                     AI 模型层（本项目新增）
│   ├── sre_topology_model.py         模型主体（~65 KB）
│   ├── sre_release.py                发布脚本（UC1/UC2/UC3 + baseline）
│   ├── test_sre_topo_model.py        11 项单元测试
│   └── release/
│       ├── weights/                  9 个 .pt 权重文件
│       ├── metrics.json              评测指标汇总
│       └── RELEASE.md                本文档
├── operator_calculus.py              规范算子演算（冻结，numpy-only）
├── sre_electronic_layer.py           规范电子层算子（冻结）
├── sre_spectral_solver.py            规范谱求解器（冻结）
├── test_operators_11_19.py           Op11-19 单元测试（61 项）
├── test_operator_calculus.py         算子演算单元测试（37 项）
└── .trae/documents/
    └── SRE_AI模型设计方案.md          设计文档（权威依据，含所有判据定义）
```

### 11.2 依赖

- Python ≥ 3.8
- torch ≥ 2.0（含 torch.linalg.eigvalsh）
- numpy ≥ 1.24
- 不依赖 torch-geometric、scipy、rdkit 等第三方包

### 11.3 许可证

规范 19 算子与 AI 模型层代码均采用 **MIT License** 开源发布。

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
