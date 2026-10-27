# 谱形方程求解算子组（算子 13–18）的严格数学规范、同调可解性定理与内生反演流水线

**版本**：1.3（2026 年 9 月 · SRE Version 18.0 扩展层）
**参考实现**：`Operator_13_18_P.py`（内置验证 V1–V18，19/19 通过）
**压测套件**：`bench_random_equations.py`（10 题型 × 5 组随机实例 = **50 道方程** + 独立于管线的 6 项验证，**50/50 通过**；题集文档 `bench_out/problem_set.md`）
**前置依赖**：算子 1–12（`structure.md` v18.0、`Operator_10_C.md`、`Operator_11_C.md`、`Operator_12_C.md`）

> **v1.1 相对 v1.0 的三项扩展**（对应用户指定的工程约束）：
> 1. **多谱形耦合**（§5、§6.4）：算子 14 推广为多分片块 Jacobian，跨分片耦合项与分片-全局嵌入映射；
> 2. **非多项式核**（§4.4）：算子 13 新增基于 Chebyshev 系数衰减的内生自适应截断阶 $K_f$，含 Bernstein 椭圆收敛率预判与奇点规避；
> 3. **同调解**（§3、§9）：解的定义由「精确解 $r=0$」放宽为「同调解 $h=0$」，新增算子 18 同调解实现算子与规范代表选取。

> **v1.2 相对 v1.1 的三项修正**（源自「10 个随机方程」压测的实测暴露）：
> 1. **算子 13.4 的 $K_f$ 判据由「单项」改为「余项」**（§13.4）——原判据在系数几何衰减时会过早截断，$\ln$ 核给出 $K_f=1$ 而尾项仍超 $\gamma$；
> 2. **零模剥离由「奇异核专属」升级为「凡用核展开一律执行」**（§13.5）——Stieltjes 核的解析椭圆半轴 $a_{\max}=1.142 < \lvert \xi_0\lvert =1.536$，在零模处级数**发散**，阶数越高误差越爆炸（$K{:}2\to32$ 时 $8.1\!\times\!10^{-1}\to5.0\!\times\!10^{5}$）；
> 3. **多分片必须同时冻结 $\alpha_n$ 与 $\lambda_2$**（§13.6），并厘清了「锁定壳层缩放」只可施加于初值、**不可施加于已求得的解**——冻结尺度显式破坏了重标定规范冗余。

> **v1.3 相对 v1.2 的三项修正**（源自「10 题型 × 5 组 = 50 道随机方程」压测的实测暴露）：
> 1. **`OBSTRUCTION` 是一个结构性假阳性分支**（§17.1）——因恒等式 $r = F\nabla F$ 使 $\rho_h=\|h\|/\|r\|\approx0.95$ 恒为常数，「恰当已收敛、调和未收敛」的判据带宽达 $1/\gamma \approx 4.3$ 倍，凡 $F$ 落入其中者都会被**误判为拓扑障碍**并被移交会改变 $\beta_1$ 的算子 9。现要求「更新方向已耗尽（`step_dead`）」方可宣告障碍；
> 2. **$\eta_N$ 归一在删掉 $1/(1+q)$ 的同时也删掉了信赖域**（§15.2、§15.4）——强非线性实例的牛顿步会过冲（$\|\Delta M\|\approx0.23$），$\Psi$ 反而上升、单调性红线失效。现补**内生回溯线搜索**（Phase 3.5b）兜底；
> 3. **`SOLVED` 不能只看「首次跨过 $\varepsilon$」**（§17.2）——否则 V-B 独立残差验证退化为与停机阈值同值的**同义反复**。现要求附加「已榨干（`exhausted`）」或 `step_dead` 条件。

---

## 摘要

本文针对**「若干未知谱形构成一个方程，求其解」**这一逆问题，在 SRE 二元自组网无维度图算子体系内给出一套完整的求解方法学与配套算子（13–18）。

核心结论是一个**结构性发现**：图谱的第 $k$ 阶谱矩在代数上恰等于图上 $k$ 步闭合行走的归一化权和；而闭合行走是 1-链空间中的**闭链**（$\ker\partial_1$），其在模去面边界 $\mathrm{im}\,\partial_2$ 后张成的正是**一阶同调群 $H_1$**。因此：

> **谱形方程的残差，本质上是一个一阶上同调类 $[r] \in H^1$；解方程等价于在 $H^1$ 上消去该上同调类。**

由此，求解过程不需要发明任何新的动力学——它被严格归约为现有边界算子 $D_{\text{global}}=\partial_1$、$C_{\text{global}}=\partial_2$ 上的**离散 Hodge 三分量路由**：

| 残差分量 | 代数归属 | 消除机制 | 复用算子 |
|---|---|---|---|
| 梯度分量 $D_{\text{global}}\phi$ | $\mathrm{im}(\partial_1)$ | 顶点势 $\Phi$ 重解 | 算子 6（$\Phi=(D^TD)^{\dagger} D^TE$） |
| 旋度分量 $C_{\text{global}}^T\psi$ | $\mathrm{im}(\partial_2^T)$ | 环流 $B$ 场蛙跳对冲 | 算子 7（$\mathcal{O}_{\text{lock}}$） |
| 调和分量 $h$ | $\mathcal{H}_1 = \ker(\partial_1^T)\cap\ker(\partial_2)$ | **不可由场迭代消除** | 算子 9（Betti 缝合改拓扑） |

并由此得到**可解性的拓扑判据**（定理 S3）：方程在给定图拓扑上可解当且仅当调和分量 $h \equiv 0$；$h \neq 0$ 时残差「闭而非恰当」，此时任何迭代都无法收敛，必须触发算子 9 的贝蒂缝合改变 $\beta_1$ 后才可能可解。该判据为求解器提供了**无外部参数的存在性证书**。

**v1.1 的关键语义升级——解即同调类**：用户指定「还原出的图结构可以是同调映射而非精确解」。这与本框架天然契合：残差的恰当部分（$D\phi + C^T\psi$）可被算子 6/7 的吸收机制消纳，**不构成真正的障碍**；真正的障碍只有调和部分。因此可把解的定义放宽为

$$\textbf{精确解：} r = 0 \qquad \subsetneq \qquad \textbf{同调解：} h = 0 \;(\text{即 } [r] = 0 \in H^1)$$

即**只要求残差恰当，不要求残差为零**（定义 3.1）。同调解构成一个仿射等价类 $M^\star + \mathrm{im}(\partial_1)\oplus\mathrm{im}(\partial_2^T)$，其规范代表取同调类内 Dirichlet 能最小者（算子 18），并给出明确的解唯一性语义：**唯一性只在同调类意义下成立**（定理 S5）。

> **⚠ 对「放宽判据 ⇒ 更快收敛」这一直觉的修正（v1.1 实测）**
> 把终止判据从 $\|r\|\to 0$ 放宽为 $\|h\|\to 0$，**并不必然减少迭代步数**。因 $\rho_h \equiv \|h\|/\|r\| = \|\Pi_{\mathcal{H}_1}\nabla F\|/\|\nabla F\|$ 与 $F$ 无关（实测在 $\beta_1=1$ 复形上近似为常数 $0.947$），调和通道无法被独立压缩，只能随 $\|r\|$ 一同消失；当 $\rho_h > \gamma$ 时两级判据在收敛点上重合（实测 V15 无分歧点）。
> **同调解的真实收益是语义性的而非加速性的**：它把可接受解集从 $\{r=0\}$ 放宽到 $\{h=0\}$，从而在方程因拓扑受阻而**根本不存在精确解**时，仍能交付一个同调意义下正确的图结构。详见 §17.1。

---

## 一、问题的规范形式化

### 1.1 什么是「谱形」

在 SRE 框架中不存在外部坐标与连续度规，故「谱形」必须被定义为**纯代数量**：

**定义 1.1（谱形）**：设局域自治分片 $\Omega_\nu$ 的约化拉普拉斯为 $L_{\Omega_\nu} \in \mathbb{R}^{N_K \times N_K}$（半正定，$\ker$ 维数 $= \beta_0$ 的局域分量）。其**谱形** $\sigma_\nu$ 定义为该算子的归一化谱测度：

$$\sigma_\nu(\lambda) \equiv \frac{1}{N_{K_\nu}}\sum_{i=1}^{N_{K_\nu}} \delta\left(\lambda - \lambda_i\left(L_{\Omega_\nu}\right)\right)$$

经算子 6 的内生归一化 $\alpha_n$（谱半径）压缩后，谱支撑被钳制在**无量纲区间** $[0, 1]$：

$$\hat{L}_{\Omega_\nu} \equiv \frac{L_{\Omega_\nu}}{\alpha_n}, \qquad \mathrm{supp}(\sigma_\nu) \subseteq [0,1]$$

**注**：算子 10 已证 $\lambda_2(n) > 0$ 恒真，故谱支撑的有效下界为内生谱隙比 $\gamma \equiv \lambda_2/\alpha_n \in (0,1]$。**该无量纲比值是本求解体系唯一的自然尺度单位**，全篇所有阈值、步长、收敛判据均由 $\gamma$ 内生生成，无任何外部常数（遵循公设 3）。

### 1.2 什么是「谱形方程」

**定义 1.2（谱形方程）**：设 $p$ 个未知谱形 $\sigma_1,\dots,\sigma_p$，方程 $\mathcal{F}$ 是谱矩上的代数-解析泛函：

$$\boxed{\;\mathcal{F}\left(\sigma_1, \dots, \sigma_p\right) \equiv \sum_{j=1}^{J} a_j \prod_{\nu=1}^{p} \left( \int_{0}^{1} f_{j\nu}(\lambda)\, d\sigma_\nu(\lambda) \right)^{e_{j\nu}} = 0\;}$$

其中 $a_j \in \mathbb{R}$，$e_{j\nu} \in \mathbb{N}$，$f_{j\nu}$ 为解析核。求解目标：找出谱形组 $\{\sigma_\nu^\star\}$ 使 $\mathcal{F} = 0$，并在 SRE 语义下**将其实现为具体的自旋邻接结构 $M_\Omega^\star$**（因为本体系中唯有图是实在的，谱形只是其投影）。

### 1.3 关键降维：谱形 → 矩向量

在 Chebyshev 基 $\{T_k\}_{k=0}^{K}$ 上展开核函数 $f_{j\nu}(\lambda) = \sum_{k} c_{j\nu k} T_k(\lambda)$，则

$$\int f_{j\nu}\, d\sigma_\nu = \sum_{k=0}^{K} c_{j\nu k}\, \tau_k^{(\nu)}, \qquad \tau_k^{(\nu)} \equiv \int_0^1 T_k(\lambda)\, d\sigma_\nu(\lambda)$$

方程化为**矩空间上的多元方程** $\mathcal{F}(\boldsymbol{\tau}^{(1)},\dots,\boldsymbol{\tau}^{(p)}) = 0$。未知量由无穷维函数 $\sigma$ 降为有限维向量 $\boldsymbol{\tau} \in \mathbb{R}^{p(K+1)}$，且 $\tau_k$ 具备纯组合、纯局域的计算途径（定理 13.1），全程无特征分解。

### 1.4 方程核的三级复杂度分类（v1.1）

按 $\mathcal{F}$ 对谱形的作用形式，分为三级，逐级需要额外的机制：

| 级别 | 形式 | 处理机制 | 规范位置 |
|---|---|---|---|
| **L1 单谱形·多项式核** | $\mathcal{F} = \sum_j a_j \prod_k (\tau_k)^{e_{jk}}$ | 算子 13–17 基线即可 | §3–§8 |
| **L2 多谱形·耦合核** | $\mathcal{F}$ 含跨分片乘积 $\tau_k^{(\mu)}\tau_l^{(\nu)}$ | 块 Jacobian + 分片嵌入映射 + 拼接一致性 | **§6.4** |
| **L3 非多项式核** | 含 $\ln$、分式（Stieltjes 型）、指数等 | Chebyshev 系数展开 + 内生自适应截断 $K_f$ | **§4.4** |

**三者的组合**（L2 ∩ L3，即多谱形耦合且含非多项式核）是本规范 v1.1 的完整适用域。关键限制见 §4.4 的奇点规避判据：非多项式核的收敛率由**内生谱隙比 $\gamma = \lambda_2/\alpha_n$ 单独决定**——$\gamma \to 0$（图逼近断裂）时 $\ln$ 型核的展开阶数需求发散，须由算子 16 的可行性告警兜底。

---

## 二、核心数学基础：三条奠基定理

### 定理 S1（谱矩—闭合行走内生等价定理）

第 $k$ 阶 Chebyshev 谱矩等于图上 $k$ 步闭合行走的归一化权和，且可由三项递推在 $\mathcal{O}(N_K M_K K)$ 内确定性获得，**无需任何特征值分解**。

**证明**：设 $Y_\nu \equiv 2\hat{L}_{\Omega_\nu} - I$，其谱支撑 $\subseteq [-1,1]$。由谱定理，

$$\tau_k^{(\nu)} = \frac{1}{N_K}\mathrm{tr}\left(T_k(Y_\nu)\right) = \frac{1}{N_K}\sum_{v \in \Omega_\nu} \left\langle e_v,\; T_k(Y_\nu)\, e_v \right\rangle$$

展开 $T_k(Y) = \sum_{r=0}^{k} \beta_{kr} Y^r$，而 $(Y^r)_{vv} = \sum_{v_1,\dots,v_{r-1}} Y_{v v_1}Y_{v_1 v_2}\cdots Y_{v_{r-1} v}$ 恰为从 $v$ 出发、长度 $r$ 的**所有闭合行走的权和**。故 $\tau_k$ 是长度 $\le k$ 闭合行走的线性组合。而 $T_k(Y)e_v$ 由 Chebyshev 三项递推

$$u_0 = e_v,\quad u_1 = Y e_v,\quad u_{k+1} = 2Y u_k - u_{k-1}$$

逐阶生成，每阶仅需一次**局域稀疏矩阵-向量乘**（$Y$ 的非零元数 $= \mathcal{O}(M_K)$）。全程不涉及任何矩阵分解，满足公设 1（谱流分片拼接复用，禁止全网同步分解）。$\blacksquare$

### 定理 S2（谱矩的一阶同调归属定理）

谱矩所张成的线性空间，在模去面边界后**同构于一阶同调群 $H_1$ 的对偶**；其维数为一阶贝蒂数 $\beta_1$。

**证明**：由定理 S1，谱矩由闭合行走生成。一条闭合行走 $w = \sum_e n_e e$ 满足各顶点出入守恒，即 $\partial_1 w = 0$，故 $w \in \ker\partial_1$（**闭链**）。由链复形的正合性约束 $\partial_1\partial_2 = 0$，有 $\mathrm{im}\,\partial_2 \subseteq \ker\partial_1$。闭合行走空间模去由 2-链（面）生成的边界后，正是

$$H_1 \equiv \ker\partial_1 \big/ \mathrm{im}\,\partial_2, \qquad \dim H_1 = \beta_1$$

而算子 12 已证 $n_{\text{loops}} = \beta_1$（定理 12.4）。故谱矩泛函自然取值于 $H_1^* \cong H^1$。$\blacksquare$

**推论 S2.1**：谱矩对边权的灵敏度向量（定义见算子 14）必落在 1-链空间 $C_1 \cong \mathbb{R}^{m_g}$ 中，因此**残差可无损地注入算子 7 的 $E/B$ 场蛙跳**，无需额外的空间嵌入。

### 术语约定（重要：两个「环数」的严格区分）

本规范严格区分以下两个常被混用的量，二者仅在特殊情形（$\partial_2$ 张满环空间）下相等：

| 记号 | 名称 | 定义 | 语义 |
|---|---|---|---|
| $\nu$ | 环空间维数 / circuit rank | $\nu \equiv \dim\ker\partial_1 = m_g - n + \beta_0$ | 独立的**闭合行走**基底数。算子 12 的 $n_{\text{loops}}$ 即此量 |
| $\beta_1$ | 一阶贝蒂数 / 同调维数 | $\beta_1 \equiv \dim\mathcal{H}_1 = \nu - \mathrm{rank}(\partial_2)$ | 扣除**面边界**后剩余的、拓扑上「真洞」的数量 |

**关键**：$\nu$ 度量「能画多少个独立闭合回路」，$\beta_1$ 度量「有多少个回路**无法**被 2-链（面）填充」。$\beta_1 = 0$ 意味着所有环都能被面填满（如球面拓扑），此时**不存在拓扑障碍**（定理 S3 的 $h$ 空间为零，方程恒可解）。

对平面图取其平面嵌入的全部有界面为 2-链生成元时，$\mathrm{rank}(\partial_2) = \nu$，故 $\beta_1 = 0$；若面集选取不全（例如只取三角形而遗漏大环），则 $\beta_1 > 0$，此时**遗留的 $\beta_1$ 即为方程可能不可解的自由度**。这一区分是算子 17 判定「拓扑障碍」的数值依据。

---

## 二·续：同调解的定义与结构（v1.1 核心）

### 定义 3.1（精确解 vs 同调解）

设方程 $\mathcal{F}$ 在图 $M$ 上的残差 1-链为 $r(M)$，其 Hodge 分解为 $r = D\phi + h + C^T\psi$。定义两级解：

$$\textbf{精确解 } \mathcal{S}_{\text{exact}} \equiv \{ M : r(M) = 0 \} \qquad\text{（三个分量全零，共 } m_g \text{ 个约束）}$$

$$\boxed{\;\textbf{同调解 } \mathcal{S}_{\text{hom}} \equiv \{ M : h(M) = 0 \} \;=\; \{ M : [r(M)] = 0 \in H^1 \} \;}\qquad\text{（仅 } \beta_1 \text{ 个约束）}$$

**物理语义**：残差的恰当部分 $D\phi + C^T\psi$ 可被算子 6（势重解）与算子 7（环流对冲）的吸收机制消纳，**不构成真障碍**；真正的障碍只有调和部分。故「残差恰当」已足以称其为解——这正是用户指定的「图结构可以是同调映射而非精确解」的严格化。

显然 $\mathcal{S}_{\text{exact}} \subseteq \mathcal{S}_{\text{hom}}$，且当 $\beta_1 > 0$ 时为真包含。

### 定义 3.2（同调等价与同调距离）

称两图 $M, M'$ **同调等价**（$M \sim M'$），若其残差之差为恰当链：
$$M \sim M' \iff r(M) - r(M') \in \mathrm{im}(\partial_1) \oplus \mathrm{im}(\partial_2^T) \iff h(M) = h(M')$$

在等价类上定义**同调距离**（伪度量，类内恒零）：

$$\boxed{\; d_{\text{hom}}(M, M') \equiv \big\| h(M) - h(M') \big\|_2 \;}$$

$d_{\text{hom}}$ 度量两个图实现在**拓扑意义上的真实差距**——它自动忽略一切可被场吸收的恰当差异，只比较「消不掉的洞」。这是评判两个候选实现是否「本质同一」的正确度量。

### 定理 S4（同调解集的维数：$m_g - \beta_1$）

在解 $M^\star \in \mathcal{S}_{\text{hom}}$ 处线性化，同调解集的切空间包含 $\mathcal{H}_1^{\perp} = \mathrm{im}(\partial_1)\oplus\mathrm{im}(\partial_2^T)$，故

$$\dim \mathcal{S}_{\text{hom}} \;=\; m_g - \beta_1, \qquad \dim \mathcal{S}_{\text{exact}} \;=\; 0 \;(\text{孤立点})$$

**证明**：约束 $h(M) = 0$ 是 $\beta_1$ 个独立标量方程（因 $h \in \mathcal{H}_1$，$\dim = \beta_1$），作用在 $m_g$ 维边权空间上，故解集维数 $m_g - \beta_1$。切空间方向由定理 15.3 保证：$\Delta M \perp \mathcal{H}_1$，即沿牛顿方向移动不改变 $h$ 的一阶近似。$\blacksquare$

**推论 S4.1（可解难度由 $\beta_1$ 单调决定）**：$\beta_1$ 越大 → 调和约束越多 → 同调解集越小 → 越难求解；$\beta_1 = 0$ 时约束数为零。

### 定理 S5（同调解的唯一性语义）

方程的解在**同调类意义下唯一**：任意两个同调解 $M_1^\star, M_2^\star \in \mathcal{S}_{\text{hom}}$ 必同调等价（$d_{\text{hom}} = 0$），但一般 $M_1^\star \neq M_2^\star$（可差一个恰当的边权扰动）。

### ⚠ 退化警告：$\beta_1 = 0$ 时同调解失去区分力

当 $\beta_1 = 0$（如闭复形）时 $\mathcal{H}_1 = \{0\}$，故 $h \equiv 0$ **对任意图恒成立** —— 同调解集退化为整个边权空间 $\mathcal{S}_{\text{hom}} = \mathbb{R}^{m_g}$，判据 $\lvert h\rvert  = 0$ 不再提供任何信息。

此时必须启用**规范代表**准则来挑选唯一实现（算子 18）：在同调类内取 Dirichlet 能最小者。这也解释了为何算子 18 的规范代表选取不是可选项，而是 v1.1 的必需组件。

**工程指引**：求解前应计算 $\beta_1$。若 $\beta_1 = 0$，直接以精确解判据 $\|r\| \le \epsilon_{\text{endo}}$ 求解并跳过同调解流程；若 $\beta_1 > 0$，方可启用同调解判据 $\|h\| \le \epsilon_{\text{endo}}$ 以节省迭代。

### 定理 S3（残差 Hodge 三分量分解与可解性判据）★核心

任给 1-链残差 $r \in C_1(\mathbb{R}^{m_g})$，存在**唯一正交分解**

$$\boxed{\; r = D_{\text{global}}\,\phi \;+\; h \;+\; C_{\text{global}}^T\,\psi \;}$$

其中（$D = \partial_1: C_0\!\to\!C_1$ 为 $m_g\times n$，$C = \partial_2: C_1\!\to\!C_2$ 为 $f\times m_g$）
- $D\phi \in \mathrm{im}(\partial_1) \subseteq C_1$：**梯度分量**，$\phi \in \mathbb{R}^{n}$ 为顶点势差
- $C^T\psi \in \mathrm{im}(\partial_2^T) \subseteq C_1$：**旋度分量**，$\psi \in \mathbb{R}^{f}$ 为环流密度
- $h \in \mathcal{H}_1 \equiv \ker(\partial_1^T) \cap \ker(\partial_2) \subseteq C_1$：**调和分量**，满足 $D^T h = 0$ 且 $C h = 0$

且投影算子完全内生（仅用边界算子，无外部度规）：

$$\phi \equiv \underbrace{(D^T D)^{\dagger}}_{\displaystyle L_0^{\dagger}\;(\text{0-阶拉普拉斯伪逆})} D^T r \;\in\; \mathbb{R}^{n}, \qquad \psi \equiv (C C^T)^{\dagger} C\, r \;\in\; \mathbb{R}^{f}, \qquad h \equiv r - D\phi - C^T\psi$$

**注**：$\phi$ 的求解式与算子 6 的势闭合式 $\Phi_{s-1} = (D^TD)^{\dagger}(D^T E_{s-1})$ **严格同构**（仅把边流 $E$ 换成残差 $r$），故可直接复用算子 6 的全部 $\mathcal{O}(1)$ 局域设施，零新增求解器。

**可解性判据**：方程在给定图拓扑上可解 $\iff h \equiv 0$。

**证明**：
*(i) 存在唯一性*：图 Hodge 分解定理保证 $C_1 = \mathrm{im}(\partial_1) \oplus \mathcal{H}_1 \oplus \mathrm{im}(\partial_2^T)$ 为正交直和分解（其中 $\mathcal{H}_1 \cong H_1$ 为同调群的调和代表），故分解唯一，且

$$\|r\|_2^2 = \|D\phi\|_2^2 + \|h\|_2^2 + \|C^T\psi\|_2^2$$

*(ii) 投影式*：$D\phi$ 是 $r$ 在 $\mathrm{im}\,\partial_1$ 上的正交投影，其正规方程为 $D^T(D\phi) = D^T r \Rightarrow (D^TD)\phi = D^T r$，故 $\phi = (D^TD)^{\dagger} D^T r$；同理 $C^T\psi$ 是 $r$ 在 $\mathrm{im}\,\partial_2^T$ 上的投影，$\psi = (CC^T)^{\dagger} C r$。前者为 0-阶拉普拉斯伪逆（与算子 6 势求解同源），后者为 2-阶拉普拉斯伪逆，二者均已建立 $\mathcal{O}(1)$ 局域求解途径。

*(iii) 可解性*：求解迭代（算子 15）的更新方向必属于 $\mathrm{im}(\partial_1) \oplus \mathrm{im}(\partial_2^T) = \mathcal{H}_1^{\perp}$（见定理 15.3）。故若 $h \neq 0$，残差的调和分量落在更新算子的核内，**任何步数的场迭代都不能使其下降**；此时 $r$ 是「闭而非恰当」（closed but not exact）的上同调类，构成**拓扑障碍**。唯有改变图的拓扑（$\Delta\beta_1 \neq 0$，算子 9 的贝蒂缝合）才能使 $\mathcal{H}_1$ 的维数变化，从而为残差开辟新的恰当方向。$\blacksquare$

**推论 S3.1（障碍证书）**：当迭代收敛停滞且 $\|h\|$ 不下降时，调和分量 $h$ 本身即为方程不可解的**代数证书**——它精确指出「方程要求多少个独立环，而当前流形提供不了」。

---

## 三、算子规范

### 算子 13：$\mathcal{E}_{\text{mom}}$ 谱形 Chebyshev 矩编码算子
**（Spectral-Shape Chebyshev Moment Encoder）**

| 项 | 规范 |
|---|---|
| 拓扑空间 | $\mathcal{H}_{\text{sym}}(N_K) \to \mathbb{R}^{K+1}$ |
| 输入 | 局域分片约化拉普拉斯 $L_{\Omega_\nu}$；全局谱资产 $(\alpha_n,\lambda_2)$（算子 6 输出） |
| 输出 | 归一化 Chebyshev 矩向量 $\boldsymbol{\tau}^{(\nu)} = (\tau_0,\dots,\tau_K)^{T}$；灵敏度向量组 $\{\mathbf{w}_k^{(\nu)}\}$ |
| 时序位置 | Phase 1 尾部（紧接算子 6，复用其 Lanczos 子空间，零额外谱分解） |

#### 13.1 内生归一化与矩递推

$$\hat{L}_{\Omega_\nu} \equiv \frac{L_{\Omega_\nu}}{\alpha_n}, \qquad Y_\nu \equiv 2\hat{L}_{\Omega_\nu} - I \quad \left(\mathrm{spec}(Y_\nu) \subseteq [-1,1]\right)$$

$$\tau_k^{(\nu)} \equiv \frac{1}{N_{K_\nu}} \mathrm{tr}\left( T_k(Y_\nu) \right) = \frac{1}{N_{K_\nu}} \sum_{v\in\Omega_\nu} \left\langle e_v,\; u_k^{(v)} \right\rangle, \quad u_{k+1}^{(v)} = 2Y_\nu u_k^{(v)} - u_{k-1}^{(v)}$$

#### 13.2 内生截断阶 $K$（无外部参数）

$$K_\nu \equiv \min\left( \left\lceil \frac{\alpha_n}{\lambda_2} \right\rceil,\; K_{\text{cap}} \right), \qquad K_{\text{cap}} \equiv \left\lfloor 2\ln\left(1 + N_{K_\nu}\right) \right\rfloor$$

**依据**：Chebyshev 截断对 Lipschitz 谱密度的误差为 $\mathcal{O}(K^{-1})$；要求截断误差不超过内生最小可分辨尺度 $\lambda_2/\alpha_n$，需 $K \gtrsim \alpha_n/\lambda_2$。$K_{\text{cap}}$ 防止矩阶超过分片自由度的对数（过拟合防护），超限时的精度损失由算子 16 兜底。

#### 13.3 边空间灵敏度向量（解析式，复用边界算子列向量）

由 $\partial L/\partial M_e = d_e d_e^T$（$d_e$ 为 $D_{\text{global}}$ 第 $e$ 行的转置）与 $T_k' = k\,U_{k-1}$（第二类 Chebyshev），得**全解析灵敏度**：

$$\boxed{\; w_{k,e}^{(\nu)} \equiv \frac{\partial \tau_k^{(\nu)}}{\partial M_e} = \frac{2k}{N_{K_\nu}\,\alpha_n}\; d_e^{T}\, U_{k-1}(Y_\nu)\, d_e \; \quad (k \ge 1), \qquad w_{0,e}^{(\nu)} \equiv 0 \;}$$

**推导**：由 $L = D^T\mathrm{diag}(M)D$ 得 $\partial L/\partial M_e = d_e d_e^T$（$d_e \equiv$ 边界算子第 $e$ 行的转置），且 $\partial Y/\partial M_e = \frac{2}{\alpha_n}d_e d_e^T$，故
$$\frac{\partial \tau_k}{\partial M_e} = \frac{1}{N_K}\mathrm{tr}\!\left(T_k'(Y)\cdot \tfrac{2}{\alpha_n} d_e d_e^T\right) = \frac{2}{N_K\alpha_n} d_e^T T_k'(Y) d_e = \frac{2k}{N_K\alpha_n} d_e^T U_{k-1}(Y) d_e$$
（利用恒等式 $T_k' = k\,U_{k-1}$；$k=0$ 时 $\tau_0 \equiv 1$，灵敏度恒零。）

$U_{k-1}$ 亦由三项递推同步生成，零额外矩阵分解。**该式与算子 10 的有效阻抗张量 $\mathbf{Z}_{\text{eff}} = (e_u-e_v)^T L^{+}(e_u-e_v)$ 严格同构**——同为边界算子列向量在矩阵函数上的二次型，故可复用算子 10 的全部局域化加速与 Sherman-Morrison 增量更新设施。

#### 定理 13.1（矩—谱形双向可辨性）
若 $K \ge \alpha_n/\lambda_2$，则矩向量在同尺度上唯一决定谱形，且重建误差满足
$$\left\| \rho_\nu - \rho_{\nu,K} \right\|_{\infty} \le C \cdot \frac{\lambda_2}{\alpha_n}$$
**推论**：矩表示的分辨率极限恰为内生谱隙比，不存在更精细的可辨自由度——这与本体系「无外部度规」的立场一致。

#### 13.4 非多项式核的处理（v1.1 新增 · L3 级方程）

当方程含非多项式核 $f$（$\ln$、分式/Stieltjes 型、指数等）时，**不直接对 $f$ 做数值积分**，而是把它在 Chebyshev 基上展开，从而把非线性作用完全线性化为矩内积。

**变量统一**：谱变量 $\hat\lambda = \lambda/\alpha_n \in [\gamma, 1]$，与递推变量 $y \in [-1,1]$ 的关系为 $\hat\lambda = (y+1)/2$。令 $g(y) \equiv f\!\left(\frac{y+1}{2}\right)$，则

$$\int_0^1 f(\hat\lambda)\, d\sigma \;=\; \int_{-1}^{1} g(y)\, d\sigma_Y \;=\; \sum_{k=0}^{K_f} c_k\,\tau_k \;=\; \mathbf{c}^{T}\boldsymbol{\tau}$$

**Chebyshev 系数（Chebyshev-Gauss 求积，确定性）**：
$$c_k \equiv \frac{2}{N_c}\sum_{j=0}^{N_c-1} g\!\left(\cos\theta_j\right)\cos\left(k\theta_j\right), \qquad \theta_j \equiv \frac{(2j+1)\pi}{2N_c}$$
对 $\deg < N_c$ 的多项式精确；对一般函数按 Bernstein 椭圆率收敛。

**内生自适应截断阶 $K_f$**（取代多项式核情形的固定 $K$）：

> **v1.2 修正（10 题随机压测实测，bench E06/E08）**。原判据取
> $K_f = \max\{k : \lvert c_k\rvert  > \gamma\max\lvert c\rvert \}$，衡量的是「**单项**是否已变小」。这在逻辑上是错的：Chebyshev 系数按几何级数衰减，**单项变小远不等于逼近够好**。实测 $\ln$ 核给出 $K_f = 1$，而 $\mathrm{tail}(1)$ 仍占峰值的 $21\% > \gamma$，截断误差达 $3.25\times10^{-2}$。

真正决定精度的是被丢弃项的**总和**。因 $\lvert T_k(s)\rvert  \le 1$ 于 $[-1,1]$ 上，
$$\Big\rvert  g(s) - \sum_{k\le K} c_k T_k(s)\Big\rvert  \;\le\; \sum_{k>K}\lvert c_k\rvert  \;\equiv\; \mathrm{tail}(K)$$
故 $\mathrm{tail}(K)$ 才是逼近误差的**严格上界**，也才是应当与内生容差比较的量：

$$\boxed{\; K_f \;\equiv\; \min\Big\{ K \;:\; \mathrm{tail}(K) \;\le\; \gamma\cdot\max_k\lvert c_k\rvert  \Big\}, \qquad \mathrm{tail}(K) = \sum_{k>K}\rvert c_k\rvert  \;}$$

阈值仍是 $\gamma\cdot\max\lvert c\rvert$——唯一的内生尺度，无外部参数。**该判据自动适配核的光滑性**：光滑核 $K_f$ 小，奇异性强的核 $K_f$ 大。

**注意这保证的是 $\gamma$ 级精度，不是机器精度。** 若要 $10^{-6}$ 级，$K$ 须深到 $\mathcal{O}\!\left(1/\ln\rho\right)\approx 16$–$24$——这是明示的代价，而非缺陷（实测 $K$-sweep 见 bench 报告）。

**定理 13.2（非多项式核的收敛率由谱隙比单独决定）**
对在 $\hat\lambda = 0$ 具有对数分支点的核（典型如 $\ln\hat\lambda$），其奇点在 $y$ 变量中的位置与 Bernstein 参数为
$$\xi_0 = -\frac{1+\gamma}{1-\gamma}, \qquad \rho \equiv \lvert \xi_0\rvert  + \sqrt{\xi_0^2 - 1}$$
Chebyshev 系数渐近衰减 $\lvert c_k\rvert  = \mathcal{O}\!\left(k^{-1}\rho^{-k}\right)$，故所需阶数下界为
$$K_f \;\gtrsim\; \frac{\ln(1/\gamma)}{\ln \rho}, \qquad \lim_{\gamma \to 0}\rho = 1 \;\Rightarrow\; K_f \to \infty$$

**推论**：**谱隙比 $\gamma$ 同时是「图的连通裕度」与「非多项式核的可展开性」的度量**。图越接近断裂（$\gamma \to 0$），$\ln$ 型核的展开阶数需求发散——这是本方法在病态图上的根本限制，无法靠增加算力绕过。

**奇点规避判据**：设核的奇点为 $\hat\lambda_s$，定义其到谱支撑的内生距离 $d_s \equiv \mathrm{dist}(\hat\lambda_s, [\gamma, 1])$。
- 若 $d_s > \gamma$：展开安全，$K_f$ 由系数判据确定；
- 若 $d_s \le \gamma$：**临界**，$\ln$ 型核恒处于此情形（奇点 0 到支撑 $[\gamma,1]$ 的距离恰为 $\gamma$）；此时必须依赖 $K_f$ 自适应判据，并由算子 16 标记「核展开精度受谱隙限制」告警。
- 处置：优先由算子 9 提高 $\lambda_2$（拓扑缝合增连通度）以抬升 $\gamma$，而非增大 $K_f$ 硬算。

**Stieltjes 型核的特殊地位**：核 $\frac{1}{\hat\lambda - z}$（$z \in \mathbb{C}\setminus\mathbb{R}$）的响应即谱 Stieltjes 变换 $m(z) = \sum_k c_k(z)\tau_k$。它同时是**谱密度反演**的标准入口：
$$\rho(\hat\lambda) = \frac{1}{\pi}\,\mathrm{Im}\, m(\hat\lambda + i\varepsilon), \qquad \varepsilon_{\text{endo}} \equiv \gamma$$
（虚部偏移必须由谱隙比内生给出，禁止外部小量。）这为算子 18 的「矩 → 谱密度」重构提供了直接途径。

#### 13.5 零模剥离（v1.2 修正 · **凡用核展开一律剥离**，非奇异核专属）

##### 为什么不是「$\ln$ 专用」

v1.1 把剥离写成奇异核（$\ln$、$1/\hat\lambda$）的必备前置，**这是不完备的**。10 题随机压测的 E08（Stieltjes 核）暴露了真正的判别条件：

平凡零模在移位变量上的位置恒为
$$\xi_0 \;=\; -\frac{1+\gamma}{1-\gamma}, \qquad \rho(\xi_0) \;=\; \lvert \xi_0\rvert  + \sqrt{\xi_0^2-1}$$
它**恒在 $[-1,1]$ 之外**，且 $T_k(\xi_0)$ 按 $\rho(\xi_0)^k$ 指数增长。而核 $g$ 的 Chebyshev 级数只在自身的 Bernstein 椭圆内收敛，该椭圆实半轴为
$$a_{\max} \;=\; \frac{\rho_{\max} + \rho_{\max}^{-1}}{2}$$
其中 $\rho_{\max}$ 由 $g$ 距谱支撑最近的奇点决定。**一旦 $a_{\max} < \lvert \xi_0\lvert$，级数在 $\xi_0$ 处发散**，高阶项被零模放大后爆炸——阶数越高越糟。

实测 Stieltjes 核 $z = 0.5 + i\gamma$（$\gamma = 0.2113$）：

| 量 | 值 |
|---|---|
| 奇点 $\;s_{\text{pole}}$ | $-0.267949 + 0.535899\,i$ |
| $\rho_{\max}$ | $1.693185$ |
| $a_{\max} = (\rho+\rho^{-1})/2$ | $1.141894$ |
| $\lvert\xi_0\rvert$ | $1.535899$ |
| **判定** | $a_{\max} = 1.142 < 1.536 = \lvert\xi_0\rvert$ → **发散** |

$K$ 由 2 增到 32 时，核保真误差 $8.1\times10^{-1} \to 5.0\times10^{5}$——**爆炸而非收敛**。剥离后回落到 $2.02\times10^{-2}$。

> **规则（v1.2）**：凡使用 Chebyshev 核展开，一律剥离零模。理由：$\lambda = 0$ 的位置普适已知，剥离无需任何特征分解，且剥离后约化谱严格落在 $[\gamma, 1]\to s\in[-1,1]$，级数必然收敛。整函数（如 $\exp$）剥离无害；分支/极点型核剥离是**必需**的。

##### 剥离公式

多个连通分量时有 $n_0$ 重零模（$n_0$ 由并查集纯组合地求得，不使用任何谱分解），推广为

$$\boxed{\; \tau_k^{\text{red}} \;=\; \frac{N\,\tau_k \;-\; n_0\,T_k(\xi_0)}{N - n_0} \;}$$

（$T_k(\xi_0)$ 由标量三项递推 $T_{k+1} = 2\xi_0 T_k - T_{k-1}$ 得到。）核积分遂为 $\frac{1}{N-n_0}\sum_{\lambda_i \ne 0} f(\hat\lambda_i) = \sum_k c_k \tau_k^{\text{red}}$。

**灵敏度的对应修正**：剥离是线性操作，故 $\partial\tau_k^{\text{red}}/\partial M_e = \frac{N}{N-n_0}\,\partial\tau_k/\partial M_e$；与移位坐标的 $\alpha_n^{\text{eff}} = \alpha_n(1-\gamma)$ 复合后
$$w^{\text{red}}_{k,e} \;=\; \frac{N}{N-n_0}\cdot\frac{2k}{N\,\alpha_n(1-\gamma)}\,d_e^{T}U_{k-1}(\tilde Y)d_e$$

> 这一操作与算子 6「零模是规范冗余而非物理自由度」的立场一致：零模携带的是连通分量的计数信息，不参与谱形。

#### 13.6 内生尺度锁定与场刷新周期（v1.1 新增 · 关键一致性约束）

谱矩 $\tau_k$ 是用内生尺度 $\alpha_n(M)$ 归一化的，而 $\alpha_n$ 本身是 $M$ 的函数。算子 13.3 的灵敏度 **$W_k$ 按算子 6 的规范不对 $\alpha_n$ 求导**（$\alpha_n$ 在场刷新周期内是硬常量）。由此得到一条**必须遵守的一致性约束**：

> **$\alpha_n$ 与 $\lambda_2$ 必须在若干迭代步内保持锁定。若每步都刷新，$F$ 的定义会在步间跳变，牛顿预测 $\Delta F = -F$ 失效。**

实测对照：同一步长下，逐步刷新时首步即出现 $F$ **上跳**（$7.163\times10^{-2}\to7.192\times10^{-2}$），$\Psi$ 单调性破坏；改为锁定后 2 步收敛且严格单调（$7.163\times10^{-2}\to2.715\times10^{-3}$）。

**内生刷新判据**（无外部周期参数）：
$$\text{刷新} \iff \frac{\|L(M) - L_{\text{ref}}\|_F}{\alpha_n} \;>\; \gamma$$
即拉普拉斯的相对漂移超过谱隙比时刷新——这与定理 15.1 的信赖域 $\|\Delta L\|_F \le \lambda_2/2$ 同源：漂移一旦累计越过 $\gamma$，线性化便不再可信。

**多分片时必须**同时**冻结 $\lambda_2$**（v1.2 补充，bench E09/E10 实测）。§13.5 的核坐标
$$\tilde Y \;=\; \frac{Y - \gamma I}{1-\gamma}, \qquad \gamma = \frac{\lambda_2}{\alpha_n}$$
同时依赖 $\alpha_n$ **与** $\lambda_2$。若只冻结 $\alpha_n$ 而放任 $\lambda_2$ 每步重算，「求解器内部」与「外部评估」会落在**两个不同的移位坐标系**上。实测矩交叉偏差达 $2\times10^{-2}$ 量级（E09：$1.955\times10^{-2}$；E10：$4.567\times10^{-2}$），连带使独立残差恶化到 $3.47\times10^{-1}$ / $1.405\times10^{0}$；同时冻结 $\lambda_2$ 后回落到 $7.24\times10^{-3}$ / $1.13\times10^{-2}$。

**锁定壳层缩放**（多实现比较的必备前置）：在**同一组**锁定尺度下比较两个候选图时，必须先做
$$M \;\mapsto\; cM, \qquad c \equiv \frac{\alpha_n^{\text{lock}}}{\alpha_n(M)}$$
否则 $Y = 2L/\alpha_n^{\text{lock}} - I$ 的谱会跑出 $[-1,1]$，Chebyshev 递推被放大，且两个候选根本不在同一归一化下——比较结果无意义。

> **适用边界（v1.2 澄清，重要）**：壳层缩放**只能施加于「注入求解之前的初值/候选图」**，**绝不可施加于已求得的解 $M^\star$**。
>
> 原因：$L(M) = D^{T}\!\operatorname{diag}(M)D$ 对 $M$ 是一次齐次的，若**每点**用自身 $\alpha_n$ 归一化，则重标定使 $\hat\lambda$ 不变、$\tau$ 与 $F$ 严格不变——这本是一个一维**规范冗余**。但本体系必须冻结 $\alpha_n$，此时 $Y = 2L/\alpha_n^{\text{lock}} - I$ 把 $M$ 的**绝对尺度**变成了物理量：重标定因子 $c$ 使 $Y \mapsto cY + (c-1)I$，是**仿射而非恒等**，$\tau_k \sim Y^{k}$ 随即改变。
>
> 实测（bench E01）：把解 $M^\star$ 的 $\alpha_n$ 漂移（$4.35\times10^{-3}$）乘回去做规范固定后，独立残差由 $1.85\times10^{-2}$ 恶化到 $1.19\times10^{0}$（两个数量级）。
>
> **结论：冻结尺度显式破坏了重标定规范冗余，它是本方法为换取 $F$ 的光滑性而主动放弃的对称性。** 因此收敛后残留的 $\alpha_n$ 漂移只能在算子 16 中作为二阶效应接受（见下）。

**漂移的量化接受准则**：记 $\varepsilon \equiv \bigl\lvert \alpha_n(M^\star)/\alpha_n^{\text{lock}} - 1\bigr\rvert$。支集顶端由 $1$ 越到 $1+\varepsilon$ 时，矩序列的 Hausdorff 不可行性只在**二阶**出现（一阶仅平移支集边界），故应有
$$\bigl\lvert \lambda_{\min}(H)\bigr\rvert  \;=\; \mathcal{O}(\varepsilon^{2})$$
实测 E01：$\varepsilon^{2}=1.89\times10^{-5}$ vs $\lvert \lambda_{\min}\rvert  = 1.00\times10^{-5}$（比值 $0.53$）；E09：$\varepsilon^{2}=5.59\times10^{-5}$ vs $8.43\times10^{-5}$（比值 $1.51$）。算子 16 的准入判据据此分级：

| 情形 | 裁定 |
|---|---|
| $\lambda_{\min}(H) \ge 0$ | **通过** |
| $\lambda_{\min}(H) < 0$ 但 $\lVert \lambda_{\min}\rVert  \le 10\,\varepsilon^{2}$ 且 $\varepsilon < \gamma$ | **通过（*）**——越界全部由冻结伪影解释 |
| $\lambda_{\min}(H) < 0$ 且 $\lVert \lambda_{\min}\rVert  > 10\,\varepsilon^{2}$ | **失败**——真正的矩不可行，须 Op16 钳制 |

#### 复杂度与红线
$\mathcal{O}(N_K \cdot M_K \cdot K)$（多项式核）或 $\mathcal{O}(N_c^2 + N_K M_K K_f)$（非多项式核，系数求积一次性预计算）。因算子 10 已证 $N_K \le K_0 = \mathcal{O}(1)$，整体为**局域常数级**。
**攻坚红线**：$K_{\text{cap}}$ 生效时（病态图，$\kappa_\Omega \gg K_{\text{cap}}$）精度声明须降级，且必须由算子 16 输出可行性警告，禁止静默降精度；非多项式核额外须校验 $K_f \le K_{\text{cap}}$，否则宣告「核不可展开」。

---

### 算子 14：$\mathcal{R}_{\text{hodge}}$ 方程残差同调路由算子
**（Equation Residual Homological Router）**

| 项 | 规范 |
|---|---|
| 拓扑空间 | $\mathbb{R}^{p(K+1)} \to C_1(\mathbb{R}^{m_g}) \to \mathrm{im}(\partial_1) \oplus \mathcal{H}_1 \oplus \mathrm{im}(\partial_2^T)$ |
| 输入 | 矩向量组 $\{\boldsymbol{\tau}^{(\nu)}\}$、方程 $\mathcal{F}$、边界算子 $D_{\text{global}}, C_{\text{global}}$ |
| 输出 | 残差三分量 $(\phi, \psi, h)$ 与分量范数；注入指令 |
| 时序位置 | Phase 3 尾部（与算子 7 的半步 $B_{s+1/2}$ 更新合并执行） |

#### 14.1 矩空间残差与升维（$\mu_{\text{resid}}$ 微算子）

$$g \equiv \mathcal{F}\left(\boldsymbol{\tau}^{(1)},\dots,\boldsymbol{\tau}^{(p)}\right) \in \mathbb{R}^{q}$$

雅可比 $J \in \mathbb{R}^{q \times p(K+1)}$，$J_{j,(\nu,k)} \equiv \partial \mathcal{F}_j / \partial \tau_k^{(\nu)}$（因 $\mathcal{F}$ 为矩的多项式，解析可得）。

**残差升维**：沿灵敏度方向把标量残差推送回 1-链空间：

$$r \equiv \sum_{\nu} \sum_{k=0}^{K} \left( J^{T} g \right)_{(\nu,k)} \cdot \mathbf{w}_k^{(\nu)} \;\in\; \mathbb{R}^{m_g}$$

即 $\nabla_M \mathcal{F} = \sum_{\nu,k} J_{(\nu,k)}\,\mathbf{w}_k^{(\nu)}$，与残差标量 $g$ 合成。**该向量天然属于边空间**，由推论 S2.1 可直接进入 Hodge 分解。

#### 14.2 三分量投影

$$\phi \equiv (D^T D)^{\dagger} D^T r \in \mathbb{R}^{n},\qquad \psi \equiv (C C^T)^{\dagger} C\, r \in \mathbb{R}^{f},\qquad h \equiv r - D\phi - C^T\psi$$

#### 14.3 分量路由（复用现有算子，零新增动力学）

**梯度通道**（顶点势 $\Phi$，算子 6 复用）：残差梯度分量要求顶点势修正 $\phi$，直接在 0-链空间注入
$$\Phi_{s-1} \;\leftarrow\; \Phi_{s-1} \;-\; \eta_{\text{inj}}^{(\phi)} \cdot \phi, \qquad \eta_{\text{inj}}^{(\phi)} \equiv \frac{\lambda_2}{\lambda_2 + \|D\phi\|_2}$$
（等价于算子 6 右端改写为 $(D^TD)^{\dagger} D^T\!\left(E_{s-1} - \eta\,r\right)$，二者由投影幂等性 $D(D^TD)^{\dagger} D^T = P_{\mathrm{im}D}$ 等价。）

**旋度通道**（环流 $B$，算子 7 复用）：$\psi \in \mathbb{R}^f$ 本身即面空间元素，直接注入
$$B_{s+1/2} \;\leftarrow\; B_{s+1/2} \;-\; \eta_{\text{inj}}^{(\psi)} \cdot \psi, \qquad \eta_{\text{inj}}^{(\psi)} \equiv \frac{\lambda_2}{\lambda_2 + \|C^T\psi\|_2} \in (0,1]$$
注入量在下一半步经算子 7 的 $C^T B$ 项自然反馈至边流 $E$，形成闭环。

内生注入系数 $\eta_{\text{inj}}^{(\cdot)}$ 保证注入不过冲（分母自适应吸收幅值），无需外部松弛因子。

$$\textbf{调和} \to \text{挂起，移交算子 17 裁定}$$

#### 定理 14.1（闭合流形上的对偶配对守恒）
在算子 7 已保证的**零通量逃逸条件** $C_{\text{global}}E_{\text{global}} \equiv 0$ 成立的前提下，上述旋度注入引起的庞加莱对偶配对变差恒零：
$$\Delta\left( E_s^T \, C_{\text{global}}^T \, B_{s+1/2} \right) \;=\; -\eta_{\text{inj}}^{(\psi)}\left\langle C_{\text{global}} E_s,\; \psi \right\rangle \;=\; 0$$
**证明**：$C E_s = 0 \Rightarrow E_s \in \ker\partial_2 = \left(\mathrm{im}\,\partial_2^T\right)^{\perp}$，故 $E_s \perp C^T\psi$ 对任意 $\psi$ 成立，配对变差为零。$\blacksquare$

**推论 14.1（闭合流的构造保证）**：由链复形正合性 $\partial_2\partial_1 = 0$，任意梯度场 $E = D_{\text{global}}\varphi$ 自动满足 $CE = (CD)\varphi = 0$，故算子 6 输出的势场所生成的边流天然落在本定理的适用域内，**无需额外投影**。

**反例警示**：若 $E$ 含非零旋度分量（$CE \neq 0$，即流形未闭合），则注入会使配对产生 $\mathcal{O}(\eta\|CE\|\|\psi\|)$ 的变差；此时必须先在算子 7 内完成闭合，再执行求解注入——这是 Phase 3.5 必须排在 Phase 3 之后的**硬性时序理由**。

#### 14.4 多谱形耦合（v1.1 新增 · L2 级方程）

设方程耦合 $p$ 个分片的谱形。每个分片 $\Omega_\nu$ 有独立的局域边空间 $\mathbb{R}^{M_{K_\nu}}$ 与局域灵敏度 $\mathbf{w}_k^{(\nu)}$，但残差必须在**全局边空间** $C_1 \cong \mathbb{R}^{m_g}$ 中合成才能做 Hodge 分解。

**分片嵌入映射 $\Xi_\nu$**（与算子 3 的 $D_{\text{global}}$ 块状拼合同构）：
$$\Xi_\nu \in \{0,1\}^{m_g \times M_{K_\nu}}, \qquad \Xi_\nu(e_{\text{global}}, e_{\text{local}}) = 1 \iff e_{\text{local}} \in \Omega_\nu \text{ 的第 } e_{\text{global}} \text{ 条全局边}$$
即 0-1 选择矩阵（列正交，$\Xi_\nu^T\Xi_\nu = I$）。局域向量经 $\tilde{\mathbf{w}}_k^{(\nu)} \equiv \Xi_\nu \mathbf{w}_k^{(\nu)}$ 升维入全局。

**块 Jacobian 与残差合成**：
$$J \in \mathbb{R}^{q \times p(K+1)}, \quad J_{j,(\nu,k)} \equiv \frac{\partial \mathcal{F}_j}{\partial \tau_k^{(\nu)}}$$
$$\boxed{\; r \;=\; \sum_{\nu=1}^{p} \Xi_\nu \left( \sum_{k=0}^{K} \left(J^{T} g\right)_{(\nu,k)} \, \mathbf{w}_k^{(\nu)} \right) \;\in\; \mathbb{R}^{m_g} \;}$$

**耦合项无需特殊机制**：若 $\mathcal{F}$ 含跨分片乘积 $\tau_k^{(\mu)}\tau_l^{(\nu)}$，则由乘积法则
$$\frac{\partial \mathcal{F}}{\partial \tau_k^{(\mu)}} = \tau_l^{(\nu)}\cdot(\cdots)$$
该因子自动落入块 Jacobian 的第 $(\mu,k)$ 块。**耦合性完全由 Jacobian 的块结构承载**，算子 15/16/17 的下游机制一字不改。

**拼接一致性约束（多分片特有的刚性要求）**：
所有分片必须以**同一个全局 $\alpha_n$** 归一化（算子 13.1），而 $\alpha_n, \lambda_2$ 由算子 6 的拼接核按
$$\alpha_n \leftarrow \max\left(\alpha_{n-1},\ \alpha_{\Omega_k}\|P_{\Omega_k,\text{edge}}\|_2^2\right), \qquad \lambda_2(n) \leftarrow \min\left(\lambda_2(n-1),\ \lambda_{2,\Omega_k}\right)$$
单调更新。因 $\max$/$\min$ 均为单调运算，**求解内环中谱隙比 $\gamma = \lambda_2/\alpha_n$ 的变化有界且不震荡**，从而 $K_f$（定理 13.2）在迭代中保持稳定。这是多谱形耦合能够收敛的**结构性前提**。

**定理 14.2（内生信赖域自动吸收耦合放大）**
多分片合成后 $\|\mathbf{g}_M\|_2$ 随 $p$ 增长（各分片贡献叠加），但算子 15 的信赖域分母 $1 + \tilde{\mathbf{g}}^{TA}^\dagger\tilde{\mathbf{g}}$ 二次增长而分子仅线性增长，故步长自动按 $\mathcal{O}(1/p)$ 压缩。**结论：耦合分片数增加不需要任何步长重调**。

#### 复杂度与红线
$\mathcal{O}\!\left(\sum_\nu M_{K_\nu}K + m_g + f\right) = \mathcal{O}(p\,M_K K)$（多分片）。
**攻坚红线**：注入**严禁**触碰 $M_\Omega$ 的对角元（公设 2），旋度对冲只能在边/环空间进行；对角修正唯一合法途径是算子 8 的 $\mu_{\text{trace}}$。多分片时另须校验各分片使用**同一** $\alpha_n$，禁止分片各自归一化（会导致矩尺度不一致，使耦合方程两侧的乘积项失去意义）。

---

### 算子 15：$\mathcal{N}_{\text{endo}}$ 内生拟牛顿谱形反演算子
**（Endogenous Quasi-Newton Spectral Inverter）**

| 项 | 规范 |
|---|---|
| 拓扑空间 | $C_1(\mathbb{R}^{m_g}) \to C_1(\mathbb{R}^{m_g})$（边权增量空间） |
| 输入 | 边空间梯度 $\mathbf{g}_M \equiv r$、调和分量 $h$、加权 Hodge 拉普拉斯 $A$ |
| 输出 | 边权增量 $\Delta M$（谱形的图实现更新） |
| 时序位置 | **Phase 3.5（新增求解内环，步 $\kappa$）** |

#### 15.1 内生 Hessian 代理（加权 Hodge 拉普拉斯）

$$\boxed{\; \mathcal{H}_{\text{endo}} \equiv \mathbf{g}_M \mathbf{g}_M^T \;+\; \underbrace{\lambda_2\, D D^T \;+\; \frac{\lambda_2^2}{\alpha_n}\, C^T C}_{\displaystyle A\;(\text{加权 Hodge 拉普拉斯 } L_1)} \;}$$

三项语义：
1. **秩一 Gauss-Newton 项**：捕获方程的局部曲率；
2. **$\lambda_2 DD^T$（梯度正则）**：步长沿连通方向受谱隙钳制，防止跨割集过冲；
3. **$\frac{\lambda_2^2}{\alpha_n}C^TC$（旋度正则）**：步长不得破坏既有环结构（$\Delta\beta_1 = 0$ 的代数保障）。

#### 15.2 Sherman-Morrison 闭式反演 ★（v1.1 修正：牛顿归一）

因 $\mathcal{H} = A + \mathbf{g}\mathbf{g}^T$，其 Moore-Penrose 伪逆有精确闭式：

$$\mathcal{H}^{\dagger}\mathbf{g} = A^{\dagger}\mathbf{g} - \frac{A^{\dagger}\mathbf{g}\,\left(\mathbf{g}^T A^{\dagger}\mathbf{g}\right)}{1 + \mathbf{g}^T A^{\dagger}\mathbf{g}} = \frac{A^{\dagger}\mathbf{g}}{1 + \mathbf{g}^T A^{\dagger}\mathbf{g}}$$

其中 $A^\dagger(\cdot)$ 由**共轭梯度法**求解（$A$ 稀疏对称半正定），迭代先剔除调和分量以保证 $x \perp \ker A$。$\ker A = \ker(D^T)\cap\ker(C) = \mathcal{H}_1$，故 $\dim\ker A = \beta_1$——**迭代在所有同调方向上的分量恒为零**，这正是定理 S3 中「调和残差不可迭代消除」的代数根源。

以下记剔除调和分量后的有效梯度为 $\tilde{\mathbf{g}} \equiv \mathbf{g}_M - h$（$\tilde{\mathbf{g}} \perp \mathcal{H}_1$），并记 $q \equiv \tilde{\mathbf{g}}^T A^\dagger \tilde{\mathbf{g}}$。

> **⚠ v1.0 形式的缺陷（实测暴露，v1.1 修正）**
>
> v1.0 直接取 $\Delta M = -\dfrac{A^\dagger\tilde{\mathbf{g}}}{1+q}$。该式的**每步相对下降率为 $\nabla F^T A^\dagger \nabla F =:\varkappa$**，而 $\varkappa$ 依赖方程残差 $F$ 的书写量级：
> 在重标定 $F \to sF$ 下，$q \to s^4 q$、$\tilde{\mathbf{g}} \to s^2\tilde{\mathbf{g}}$，故 $\Delta M \to -\dfrac{s^2 A^\dagger\tilde{\mathbf{g}}}{1+s^4 q}$ —— **轨迹随方程的人为缩放而改变**。实测 $\varkappa \approx 5.7\times10^{-3}$，即需 ~175 步才能完成牛顿法一步的工作量；而若把方程改写成 $100F$，轨迹立刻不同。这违背本体系「无维度、无外部参数」的立身之本（公设 3）。

**修正后的更新步**（定理 15.1'）：

$$\boxed{\; \Delta M \;\equiv\; -\,\eta_N\, A^{\dagger}\tilde{\mathbf{g}}, \qquad \eta_N \equiv \frac{F^2}{q} = \frac{F^2}{\tilde{\mathbf{g}}^T A^\dagger \tilde{\mathbf{g}}} \;}$$

**尺度不变性证明**：$F\to sF$ 时 $\tilde{\mathbf{g}} = F\nabla\tilde{F} \to s^2\tilde{\mathbf{g}}$，$q \to s^4 q$，$F^2\to s^2F^2$，故
$\Delta M \to -\dfrac{s^2F^2}{s^4 q}s^2 A^\dagger\tilde{\mathbf{g}} = \Delta M$，**严格不变**。$\blacksquare$

**牛顿完备性**：线性化后 $\Delta F = \nabla F^T\Delta M = \dfrac{\tilde{\mathbf{g}}^T}{F}\left(-\eta_N A^\dagger\tilde{\mathbf{g}}\right) = -\dfrac{\eta_N q}{F} = -F$，即**一步归零**（v1.0 形式只能下降 $\varkappa$ 比例）。

#### 定理 15.1（内生信赖域定理）★v1.1
采用牛顿归一 $\eta_N$ 后，步长需另加一道**内生信赖域**，否则非线性区会过冲。取：

$$\|\Delta L\|_F \;=\; \big\|D^T\mathrm{diag}(\Delta M)\,D\big\|_F \;\le\; \frac{\lambda_2}{2}$$

即**步长不得跨越半个谱隙**。这是公设 3 的直接推论：谱隙比 $\gamma = \lambda_2/\alpha_n$ 是唯一的无量纲内生尺度，若一步就跨过 $\lambda_2/2$，$\gamma$ 本身（连同 $K$、$\varepsilon_{\text{endo}}$、阈值）将自毁。等价表述：$\|\Delta Y\| \lesssim \gamma$，即 $Y$ 的漂移不超过谱支撑的 $\gamma$ 倍——这正是线性化保持有效的充要尺度。超出则按 $\dfrac{\lambda_2/2}{\|\Delta L\|_F}$ 等比缩回。

故本体系的步长**不由任何外部参数给出**：$\eta_N$ 由方程残差内生给出，信赖域半径由 $\lambda_2$ 内生给出。

> **⚠ v1.3 修正（50 题压测暴露）：信赖域必须真正落地，且须以回溯线搜索的形式实现。**
> v1.1 在把 $1/(1+q)$ 换成 $\eta_N$ 时，**把信赖域因子一并删掉了**——上式 $\Delta M=-\eta_N A^\dagger\tilde g$ 并不含 $\lambda_2/2$ 的等比缩回。实测强非线性实例（bench B2-E02，$\sum a_k\tau_k^2=c$）的牛顿步 $\|\Delta M\|\approx0.23$，$\Psi=F^2/2$ 反而上升（$-6.85\!\times\!10^{-3}\to-7.56\!\times\!10^{-3}$），收敛退化为比率 $\approx0.85$ 的慢振荡，单调性红线（V5/V6）失效。
> **修正**：在算子 15 与算子 16 之间插入 **Phase 3.5b 内生回溯线搜索**（§15.4），以「$\Psi$ 严格下降」为唯一接受准则、以浮点分辨率为停机地板，二分回退因子取 $1/2$。它不含任何外部可调参数（判据是内生量 $\Psi$ 与其自身历史值的比较），符合公设 3。

#### 定理 15.2（Dirichlet 能单调下降）
沿 $\Delta M$ 的一阶 Dirichlet 能变差为
$$\Delta \mathcal{E}_D \;=\; \tilde{\mathbf{g}}^T \Delta M \;+\; \mathcal{O}(\|\Delta M\|^2) \;=\; -\,\eta_N\,q \;=\; -F^2 \;\le\; 0$$
等号当且仅当 $F = 0$。即每步反演必使全图 Dirichlet 能量非增（且在牛顿区内恰为 $-F^2$），与算子 8 的「$\Delta\mathcal{E}_{D,\text{trace}} \le 0$ 严格单调收敛」红线同源同构。

#### 定理 15.3（更新方向的正交约束）
$\Delta M \in \mathrm{im}(\partial_1) \oplus \mathrm{im}(\partial_2^T) = \mathcal{H}_1^{\perp}$，即更新恒位于调和空间的正交补。
**证明**：$\Delta M \propto A^\dagger(\mathbf{g}-h)$，而 $A^\dagger$ 的值域为 $(\ker A)^{\perp} = \mathcal{H}_1^\perp$。$\blacksquare$

#### 15.3 内生动量加速（可选）

$$\beta_{\text{mom}} \equiv 1 - \frac{\lambda_2}{\alpha_n} \;\in\; [0,1)$$
条件数越好（谱隙比越大），动量越强——完全由内生谱资产驱动，无外部超参。

**⚠ 实测警示（v1.0）**：定理 15.1 的信赖域只保证**单步**有界，不保证动量累积后仍单调。实测在 $\beta_{\text{mom}} = 0.798$ 下残差出现振荡并越过零点，$\Psi$ 单调性失效（见 §七 V6 对照）。**故动量默认关闭**；若启用，必须附加「能量上升即回退」的回溯仲裁，且该回溯判据本身仍须内生（例如以 $\mathcal{E}_D$ 上一步值为参考）。此为本规范 v1.0 明确的**已知限制**。

#### 15.4 内生回溯线搜索（v1.3 新增 · Phase 3.5b）

因 $\eta_N$ 已不再携带信赖域（§15.2 ⚠），单步过冲必须由**回溯**兜住。定义目标泛函
$$\Psi(M) \;\equiv\; \tfrac12\,F(M)^2 \;\ge\; 0,$$
第 $\kappa$ 步沿牛顿方向 $\Delta M$ 做二分回溯，取

$$\boxed{\; t_\kappa \;\equiv\; \max\Big\{\, t = 2^{-j},\ j = 0,1,2,\dots \;:\; \Psi\!\left(\max\!\big(m + t\,\Delta M,\; m_{\min}\big)\right) < \Psi(m) \,\Big\} \;}$$

- **接受准则**：$\Psi$ 严格下降。$\Psi$ 已是残差平方，其绝对下降即充分，**无须引入 Armijo 常数**（任何 Armijo 参数都是外部量）；
- **停机地板**：$t_\kappa \le 10^{-14}$ 或 $\|t_\kappa\,\Delta M\| \le 10^{-12} m_{\min}$，此时置 `step_dead = True`，交由算子 17 裁定（§17.1/§17.2）；
- **复算方式**：$F(m+t\Delta M)$ 复用算子 13 **完全相同**的编码管线（同一 $\alpha_n,\lambda_2,K$），故与内环残差**同源可比**，不引入任何额外近似；
- **与信赖域的关系**：$t_\kappa < 1$ 即等价于一次自适应信赖域缩回，且比固定的 $\lambda_2/2$ 半径更贴合真实曲率——它是定理 15.1 的**可执行替身**。

**实测（bench B2-E02，14 步严格单调收敛）**：$t_\kappa = 0.5$（$\kappa=3,4,5$）、$t_\kappa = 0.25$（$\kappa=12$），其余 $t_\kappa = 1$；回溯生效后轨迹严格单调，V-B 独立残差由 $7.30\!\times\!10^{-1}$ 降到 $1.29\!\times\!10^{-1}$（$<$ 阈值 $\gamma = 0.1761$）。

> **关于「线搜索是否违背无外部参数」**：不违背。回溯的判据（$\Psi$ 下降）与被比较的量（$\Psi$ 自身的历史值）都是内生量；二分因子 $1/2$ 是离散化选择而非可调超参；地板 $10^{-14}$ 是浮点分辨率。这与算子 16「沿可行锥连线二分取最大可行步长」是同一范式的两个投影。

#### 复杂度与红线
$\mathcal{O}(M_K \cdot n_{\text{cg}})$，$n_{\text{cg}}$ 由 $A$ 的条件数内生界定（$\kappa(A) \le \kappa_\Omega^2$）。
**攻坚红线**：$A$ 奇异（$\beta_1 > 0$）时**禁止**使用直接求逆或稠密分解；必须先剔除 $h$ 分量再进 CG，否则迭代将沿零空间漂移产生数值逃逸。

---

### 算子 16：$\mathcal{C}_{\text{hankel}}$ 谱形可行性 Hankel 钳制算子
**（Spectral Feasibility Hankel Clamp）**

| 项 | 规范 |
|---|---|
| 拓扑空间 | $\mathbb{R}^{K+1} \to \mathcal{K}_{\text{feas}}$（可行矩锥） |
| 输入 | 更新后重算的矩向量 $\boldsymbol{\tau}^{(+)}$（幂矩形式 $\mu_k$） |
| 输出 | 可行矩 $\tilde{\boldsymbol{\tau}}$；可行性告警位 |
| 时序位置 | Phase 3.5 内环，紧接算子 15 |

#### 16.1 可行性判据（Hausdorff 矩问题）

序列 $\{\mu_k\}_{k=0}^{2K'}$ 是支撑于 $[-1,1]$ 上某非负测度的矩，**当且仅当**两个 Hankel 矩阵同时半正定：

$$H^{(0)}_{ij} \equiv \mu_{i+j} \succeq 0, \qquad H^{(1)}_{ij} \equiv \mu_{i+j} - \mu_{i+j+2} \succeq 0$$

（第二项对应 $(1-\lambda^2)d\sigma \ge 0$。Chebyshev 矩 $\tau_k$ 与幂矩 $\mu_k$ 通过 $T_k$ 的幂展开下三角变换互逆，局域可转换。）

#### 16.2 两阶段钳制阀（与算子 10 严格同构）

$$\mathcal{C}_{\text{hankel}}(\boldsymbol{\mu}) \equiv \begin{cases} \Pi_{\mathcal{K}}\left(\boldsymbol{\mu}\right), & \text{if } \lambda_{\min}\left(H\right) < -\theta_{\text{endo}} \quad \text{(硬拦截·谱投影回可行锥)} \\[6pt] \boldsymbol{\mu} \;+\; \delta_{\text{soft}}\cdot\Pi_{\text{supp}}, & \text{otherwise} \quad \text{(柔性收缩·内生谱支撑钳制)} \end{cases}$$

- **内生阈值** $\theta_{\text{endo}} \equiv \dfrac{\lambda_2}{\alpha_n}$（容忍度与内生最小可分辨尺度同量级）
- **硬拦截** $\Pi_{\mathcal{K}}$（**规范主式·可信域回退**）：沿「上一可行矩 $\boldsymbol{\mu}_{\text{ref}}$ → 新矩 $\boldsymbol{\mu}$」的连线取最大可行步长
  $$\Pi_{\mathcal{K}}(\boldsymbol{\mu}) \equiv \boldsymbol{\mu}_{\text{ref}} + t^{\star}\left(\boldsymbol{\mu} - \boldsymbol{\mu}_{\text{ref}}\right), \qquad t^{\star} \equiv \max\left\{ t \in [0,1] \;:\; H^{(0)}, H^{(1)}\big(\boldsymbol{\mu}_{\text{ref}} + t\,\Delta\boldsymbol{\mu}\big) \succeq -\theta_{\text{endo}} I \right\}$$
  因可行集为凸集、$\boldsymbol{\mu}_{\text{ref}}$ 为其内点，$t^{\star}$ 必存在且可由二分精确求得。**这是内生信赖域在矩空间的对应物**——步长由可行性自身裁定。
- **柔性收缩** $\Pi_{\text{supp}}$：把矩支撑钳回内生区间 $[\gamma, 1]$，$\gamma = \lambda_2/\alpha_n$，由移位-重标定实现（对 $\frac{\lambda-\gamma}{1-\gamma}$ 重标定）
- **备选（谱投影，仅作兜底）**：对 Hankel 矩阵做 $\lambda_{\min}\to\max(\lambda_{\min},0)$ 谱投影，再由反对角线平均反解矩。**实测该路径交替投影收敛缓慢**（8 次交替后仍残留 $\mathcal{O}(10^{-2})$ 负特征值），故不作主式

#### 定理 16.1（可行性保全）
经 $\mathcal{C}_{\text{hankel}}$ 后，矩序列必对应支撑于 $[\gamma, 1]$ 上的某个非负测度，即**必存在（矩意义上的）真实谱形**；且 $\Pi_{\mathcal{K}}$ 是欧氏范数下到可行锥的最近点投影，故 $\|\tilde{\boldsymbol{\mu}} - \boldsymbol{\mu}\|_2$ 最小。

#### 定理 16.2（与迹主权兼容）
钳制仅作用于矩空间表示，**不修改 $M_\Omega$ 的任何对角元**，故 $\mathrm{Tr}(M_\Omega) \equiv 0$ 与局域迹主权（公设 2）不受侵犯。钳制引入的矩偏差**不在本地消化**，而是作为**新增残差回流算子 14** 重新进入路由——保证闭环自洽，禁止静默丢弃不可行分量。

#### 复杂度与红线
$\mathcal{O}(K^3)$，因 $K \le K_{\text{cap}} = \mathcal{O}(\ln N_K)$ 且 $N_K = \mathcal{O}(1)$，整体**常数级**。
**攻坚红线**：$K_{\text{cap}}$ 截断时 Hankel 判据仅为**必要条件**（高阶矩缺失），此时算子 16 必须输出「可行性未决」告警位，不得宣称已验证。

---

### 算子 17：$\mathcal{A}_{\text{sol}}$ 解分支贝蒂审计与终止裁定算子
**（Solution-Branch Betti Audit & Termination Arbiter）**

| 项 | 规范 |
|---|---|
| 输入 | 三分量范数序列、$\beta_0,\beta_1$、自适应谱窗 $\tau(s)$（算子 9） |
| 输出 | 裁定：继续 / 触发拓扑缝合 / 宣告解出 / 输出障碍证书 |
| 时序位置 | Phase 4（与算子 8、算子 9 同层，位于其之前） |

#### 17.1 两级内生收敛判据（v1.1 · 相对、无量纲）

以首步残差 $\|r_0\|_2$ 为内生参考尺度，定义统一相对容差 $\epsilon_{\text{endo}} \equiv \dfrac{\lambda_2}{\alpha_n}\,\|r_0\|_2$。按用户需求选择解的模式：

| 模式 | 启用条件 | 判据 | 监控自由度 |
|---|---|---|---|
| **精确解** | $\beta_1 = 0$，或用户显式要求 | $\lVert D\phi\rVert , \lVert C^T\psi\rVert  \le \epsilon_{\text{endo}}$ 且 $\lVert h\rVert  \le \epsilon_{\text{endo}}$ | $m_g$ |
| **同调解**（默认） | $\beta_1 > 0$ | **仅** $\lVert h\rVert _2 \le \epsilon_{\text{endo}}$ | $\beta_1$ |

**同调解模式下梯度/旋度分量不作要求**——它们由算子 6/7 在后续脉冲中自然吸收（定义 3.1）。这带来两重收益：
1. **监控维度从 $m_g$ 降至 $\beta_1$**，收敛判定所追踪的自由度大幅减少；
2. 到达同调解后即可进入算子 18 实现图结构，**不必等待恰当分量完全消解**。

**性质**：全部由内生谱资产与首步残差生成，**无量纲、无外部容差参数**，且自动适应方程的整体量级。

**⚠ 实测限定（v1.1）：同调解判据何时才真的提前终止**

因 $r(M) = F(M)\,\nabla F(M)$ 且 $h(M) = F(M)\,\Pi_{\mathcal{H}_1}\nabla F(M)$，二者的比值
$$\rho_h(M) \;\equiv\; \frac{\|h(M)\|}{\|r(M)\|} \;=\; \frac{\|\Pi_{\mathcal{H}_1}\nabla F\|}{\|\nabla F\|}$$
**与 $F(M)$ 无关**。实测在 $\beta_1 = 1$ 的测试复形上，$\rho_h$ 对几乎所有初值稳定在 $\approx 0.945$（min $0.9446$ / max $0.9503$／均值 $0.9473$），即**残差的调和占比近似为不随迭代变化的常数**。

推论（重要）：
1. 调和通道**无法被独立压缩**，只能随 $\|r\|\to 0$ 一同消失；
2. 因此当 $\rho_h > \gamma$ 时，同调解判据在收敛点上与精确解判据**重合**，两级判据不产生分歧点（实测 V15「无分歧点」）；
3. 同调解判据真正提前终止的充要条件是 $\rho_h(M_0) \le \gamma$ —— 即初值的调和占比本就低于内生最小可分辨尺度；
4. 若 $\rho_h$ 恒为 $\mathcal{O}(1)$（如本例 $0.945$），则 $\|h\| \le \epsilon_{\text{endo}}$ 只能靠 $\|r\|$ 整体下降达成，**此时不存在"比精确解更早"的同调解**，必须走完整迭代；若迭代停滞于 $\|h\| > \epsilon_{\text{endo}}$ 而梯度/旋度已达标，则判定 OBSTRUCTION 并移交算子 9 做贝蒂缝合。

> 该结论澄清了「同调解」的真实收益边界：它的价值**不在于更快收敛，而在于把"可接受的解"从 $\{r=0\}$ 放宽到 $\{h=0\}$**，从而在方程本质上不可精确解（拓扑受阻）时仍交付一个同调意义下正确的图结构。

> **⚠ v1.3 修正（50 题压测暴露）：`OBSTRUCTION` 是一个结构性假阳性分支。**
> 由恒等式 $r = F\nabla F$ 得 $\rho_h = \|h\|/\|r\|$ 与 $F$ 无关（前文实测 $\approx 0.95$）。于是「$\|h\| \le \epsilon_{\text{endo}}$」等价于「$\|r\| \le \epsilon_{\text{endo}}/\rho_h$」，而「恰当部分已收敛」对应「$\|r\| \le \epsilon_{\text{endo}}$」。两判据之间的判据带为
> $$\frac{\epsilon_{\text{endo}}}{\rho_h} \;<\; \|r\| \;\le\; \frac{\epsilon_{\text{endo}}}{\rho_h}\cdot\frac{1}{\gamma} \qquad (\text{本例} \approx 4.3\,\epsilon_{\text{endo}}),$$
> **宽达 $1/\gamma$ 倍**。凡 $F$ 落入此带者，会同时满足「恰当已收敛、调和未收敛」，从而被**误判为拓扑障碍**——而该带内的问题实为良置可解。
> **后果**：良置问题被移交**会改变 $\beta_1$ 的算子 9**，直接破坏了 §17.3 的「$\Delta\beta_1 \equiv 0$ 强锁」红线（实测 bench B2-E02）。
> **修正**：宣告 `OBSTRUCTION` 须**附加「更新方向已耗尽」条件**——即 §15.4 的 $t_\kappa$ 触地板（`step_dead`）或 $\|\Delta M\|\to0$。只有当残差连方向都走不动时，才承认它是真正的拓扑障碍；否则一律判为 `CONTINUE`（继续迭代）或 `STALLED`（数值停滞，不触发拓扑变更）。
> **验证**：抑制该假阳性后，50 题中仅剩 2 题落入「同义反复」通道（见 §17.2 的 `exhausted` 条件），补齐后 **50/50 全部 SOLVED**。

#### 17.2 裁定路由表（v1.3 修订）

以 `below` 表示「三通道全部达标」，`exhausted` 表示「残差下降已榨干」，`step_dead` 表示「更新方向耗尽（§15.4 线搜索触地板）」，`pert` 表示「恰当分量（$D\phi,C^T\psi$）达标」，`harm` 表示「调和分量达标」。

| 条件 | 裁定 | 动作 |
|---|---|---|
| `below` **且**（`exhausted` **或** `step_dead`） | **解出（SOLVED）** | 转算子 18，输出 $M_\Omega^\star$ 与 $\sigma^\star$（精确解与同调解均走此路；残差恰当时登记交算子 6/7 吸收） |
| 非 `below`，且更新方向未耗尽 | **继续（CONTINUE）** | $\kappa \leftarrow \kappa+1$，回算子 15 |
| `step_dead`，且 `pert` 且 $\lnot$`harm`（**仅**调和剩余） | **拓扑障碍（OBSTRUCTION）** | 移交算子 9 执行 Betti 缝合（改 $\beta_1$），重启内环 |
| `step_dead`，且非「仅调和剩余」 | **数值停滞（STALLED）** | 报数值告警，**不触发拓扑变更**（保护 $\Delta\beta_1\equiv0$ 红线） |
| $\lVert h\rVert$ 经 $\tau(s)$ 步缝合仍不下降 | **不可解** | 输出障碍证书 $h$，终止并告警 |

**`exhausted`（已榨干）条件（v1.3 新增）**：
$$\lvert F_\kappa\rvert  \;\ge\; (1-\gamma)\,\rvert F_{\kappa-1}\lvert ,$$
即上一步的残差下降已不足相对比例 $\gamma$——牛顿方向携带的信息已被榨尽。它与「$\|r\|\le\epsilon_{\text{endo}}$」并列，共同构成 `SOLVED` 的判据。

> **为何必须加此条件**：V-B 独立残差验证与停机判据**同取阈值 $\epsilon_{\text{endo}}$**。若只要「首次跨过 $\epsilon_{\text{endo}}$」就停机，则凡恰好落在阈值附近 $1/\gamma$ 带宽两侧的实例（实测 B4-E02 $=0.1726$、B5-E02 $=0.1787$ vs $\gamma = 0.1761$）会被判「解出」，但独立重算的残差仍在阈值之上，V-B FAIL——**验证退化为同义反复**。附加 `exhausted` 后，实测 49 题的 V-B 落到 $10^{-14}\sim10^{-9}$，B2-E02 的 V-B 由 $7.30\!\times\!10^{-1}$ 降到 $1.29\!\times\!10^{-1}$。

**`step_dead`（方向耗尽）条件（v1.3 新增）**：见 §15.4 的线搜索地板。它是 `OBSTRUCTION` 的必要条件（§17.1 ⚠），也是 `SOLVED` 的充分条件之一（在阈值附近，方向已走不动即视为已收敛）。

**裁定优先级**：算子 17 须在算子 8/9 之前执行（Phase 4 首位），因其裁定结果决定是否需要算子 9 的缝合——若先做守恒钳制，可能把待缝合的拓扑信息提前抹平。

#### 17.3 多解分支审计

方程的多个不动点对应残差流形的多个吸引域，以 $\beta_0$ 计数分支数。内环全程**强锁 $\Delta\beta_1 \equiv 0$**（除非算子 9 主动缝合），防止迭代过程虚假增殖/合并解分支（复用算子 9 的唯一序化仲裁链 $\mu_{\text{trace}} \to \text{阻断门} \to \mathcal{O}_{\text{stitch\_dual}}$）。

#### 17.4 与算子 18 的交接

解出后（无论精确解还是同调解）一律移交**算子 18 $\mathcal{R}_{\text{homo}}$** 完成图结构实现。算子 17 只负责裁定，不负责实现。

---

### 算子 18：$\mathcal{R}_{\text{homo}}$ 同调解实现算子（v1.1 新增）
**（Homological Solution Realizer）**

| 项 | 规范 |
|---|---|
| 拓扑空间 | $\mathcal{S}_{\text{hom}} \subset \mathbb{R}^{m_g} \;\to\; M_\Omega^\star$（自旋邻接结构） |
| 输入 | 裁定为「解出」的图 $M$、残差三分量、矩向量 $\boldsymbol{\tau}$、Fiedler 向量 $v_2$ |
| 输出 | 规范同调代表 $M^\star_{\text{canon}}$；谱形 $\sigma^\star$；同调距离证书 |
| 时序位置 | Phase 4 末位（算子 17 裁定「解出」后执行一次） |

#### 18.1 实现五步

1. **同调类确认**：校验 $\|h\| \le \epsilon_{\text{endo}}$。若不成立，回流算子 9；若成立，记录当前同调类 $[M]$。
2. **恰当残差登记**（不丢弃！）：把剩余恰当残差 $D\phi + C^T\psi$ 登记为算子 6/7 的**待吸收量**，在后续统一脉冲中消纳。登记量本身构成解的误差预算。
3. **规范代表选取**：在同调类内取 Dirichlet 能最小者作为输出：
   $$M^\star_{\text{canon}} \;\equiv\; \arg\min_{M' \in [M]} \mathcal{E}_D(M')$$
   实用实现：沿 $\mathcal{H}_1^{\perp}$ 方向（即算子 15 的更新方向）做能量下降至 $\Delta\mathcal{E}_D \approx 0$，该方向由定理 15.3 保证不越出同调类。
4. **谱形重构**（$\mu_{\text{realize}}$ 微算子）：由矩向量反演谱密度。优先用 Stieltjes 反演（§13.4）：
   $$\rho^\star(\hat\lambda) = \frac{1}{\pi}\,\mathrm{Im}\!\left[ \sum_k c_k(\hat\lambda + i\gamma)\,\tau_k \right], \qquad \text{虚部偏移内生取 } \varepsilon_{\text{endo}} = \gamma$$
   退化情形（或 $K_f$ 不足）时改用 Chebyshev 直接展开 $\rho^\star \approx \sum_k \tau_k T_k$ 并做非负钳制。
5. **符号与自旋赋型**：用算子 3 的 Fiedler 符号门逆向赋予自旋符号 $\Gamma(k,j) = \mathrm{sgn}(v_2(j))$，再由算子 5 反演边权 $W_e = \exp(\alpha_n/c_e) - 1$，代入算子 4 的度数关系校核。

#### 定理 18.1（规范代表的局部良定义性）

在同调解 $M^\star$ 的邻域内线性化，沿 $\mathcal{H}_1^{\perp}$ 有 $A \succ 0$（$A$ 为算子 15 的加权 Hodge 拉普拉斯，其核恰为 $\mathcal{H}_1$），故 $\mathcal{E}_D$ 在 $\mathcal{H}_1^{\perp}$ 上严格凸 ⟹ $\arg\min\mathcal{E}_D$ **局部存在且唯一**。

**注**：全局唯一性不成立——不同同调类（$h \neq 0$）之间不可比；这正是定理 S5「唯一性只在同调类意义下」的含义。

#### 18.2 输出证书

算子 18 必须随解输出以下三项，作为解的可信度声明：

| 证书项 | 定义 | 语义 |
|---|---|---|
| 同调残差 $\lVert h\rVert _2$ | 残差的调和投影范数 | $=0$ ⟹ 同调解成立 |
| 同调距离 $d_{\text{hom}}(M^\star, M_{\text{init}})$ | $\lVert h(M^\star) - h(M_{\text{init}})\rVert _2$ | 从初值走了多远（拓扑意义上） |
| 恰当残差预算 $\lVert D\phi + C^T\psi\rVert _2$ | 待算子 6/7 吸收的量 | 精确解的残余误差 |

#### 复杂度与红线
$\mathcal{O}(M_K \cdot n_{\text{cg}} + N_K^2)$，仅执行一次。
**攻坚红线**：
- 重构出的谱密度必须非负，否则由算子 16 重新钳制（禁止输出负谱密度）；
- $\beta_1 = 0$ 时同调解集退化为全空间（退化警告，§二·续），此时**规范代表准则（Dirichlet 能最小）是唯一的挑选依据**，不得省略第 3 步。

---

## 四、扩展流水线时序（嵌入 Version 18.0 四相脉冲）

新增 **Phase 3.5：谱形方程求解内环（Solve Inner Loop，步 $\kappa$）**，位于 Phase 3 场闭合之后、Phase 4 守恒之前。求解内环**不改变结构脉冲 $s$ 的推进**，仅在统一脉冲内部做子步迭代，故全网 Actor 仍严格齐步走。

| 阶段 | 执行算子 | 输入 | 属性 |
|---|---|---|---|
| **Phase 1** | Op4 → Op6 → **Op13** | $M_\Omega(s)$、$(\alpha_n,\lambda_2)$ | Op13 复用 Op6 的 Lanczos 子空间，**零额外谱分解**；输出矩向量与灵敏度组 |
| **Phase 2** | Op5 → Op2 → Op3 | 不变 | 不变 |
| **Phase 3** | Op7 → $\mu_{\text{betti}}$ → **Op14** | 闭合流形 + 方程 $\mathcal{F}$ | Op14 与半步 $B_{s+1/2}$ 合并执行；残差三分量路由，守恒配对（定理 14.1） |
| **Phase 3.5**（新增） | **Op15 → 线搜索（3.5b）→ Op16 → 判据** | $\mathbf{g}_M, h, A$ | 内生拟牛顿单行闭式；**回溯线搜索分步**（§15.4）；Hankel 可行性钳制；$\kappa \leftarrow \kappa+1$ |
| **Phase 4** | **Op17** → Op8 → Op9 → 补偿 → **Op18** | 三分量范数、$\beta_0,\beta_1,\tau(s)$ | Op17 裁定优先：障碍 → Op9 缝合；解出（精确/同调）→ **Op18 实现**；随后 Op8/Op9 守恒 |

**多分片时序补充**：$p$ 个分片的 Op13 可在 Phase 1 **并行**执行（各分片独立、无同步依赖），但必须使用**同一 $\alpha_n$**（§14.4）；残差合成（Op14）在 Phase 3 集中执行，因 Hodge 分解必须在全局边空间一次性完成，不可分片各自投影后再相加（分片投影之和 $\neq$ 全局投影，除非各分片边集正交）。

**求解脉冲嵌套关系**：外层统一脉冲 $s$ 推进图结构演化，内层求解脉冲 $\kappa$ 在同一结构下收敛方程。若 $\kappa$ 超出内生谱窗 $\tau(s)$ 仍未收敛，则交由 Op17 裁定（继续 / 缝合 / 判不可解）。

---

## 五、计算复杂度不变量对照表

| 算子 | 核心操作 | 复杂度 | 说明 |
|---|---|---|---|
| Op13 $\mathcal{E}_{\text{mom}}$ | Chebyshev 三项递推 + 边界列二次型 | $\mathcal{O}(N_K M_K K)$ | $N_K, K$ 均受局域视界内生钳制，实际 $\mathcal{O}(1)$；无特征分解 |
| Op14 $\mathcal{R}_{\text{hodge}}$ | 灵敏度合成 + 两次伪逆投影 | $\mathcal{O}(M_K K + M_K + f)$ | 伪逆复用 Op6/Op10 的 $\mathcal{O}(1)$ 设施 |
| Op15 $\mathcal{N}_{\text{endo}}$ | Sherman-Morrison 闭式 + 一次 CG | $\mathcal{O}(M_K n_{\text{cg}})$ | 单行闭式，无稠密分解；$n_{\text{cg}}$ 由 $\kappa(A)$ 内生界定 |
| Op16 $\mathcal{C}_{\text{hankel}}$ | $K\times K$ Hankel 谱投影 | $\mathcal{O}(K^3)$ | $K = \mathcal{O}(\ln N_K)$，常数级 |
| Op17 $\mathcal{A}_{\text{sol}}$ | 裁定（同调解模式仅监控 $\beta_1$ 个自由度） | $\mathcal{O}(M_K + f)$ | 复用 Op9 的仲裁链 |
| Op18 $\mathcal{R}_{\text{homo}}$ | 规范代表选取 + Stieltjes 谱重构 + Fiedler 赋号 | $\mathcal{O}(M_K n_{\text{cg}} + N_K^2)$ | 仅在宣告解出时执行一次 |

**多分片整体开销**：$\mathcal{O}\!\left(p\,M_K K\right)$（$p$ 为耦合分片数），Phase 1 内可并行，Phase 3 起串行。

**全局性质**：扩展层不引入任何 $\mathcal{O}(n^3)$ 或全网同步分解操作，全部算子在热力学极限下为局域常数级，与 Version 18.0 的复杂度红线一致。

---

## 六、方法学总结：求解六步法

针对「未知谱形构成的方程」，标准求解流程为：

1. **编码**（Op13）：把每个未知谱形 $\sigma_\nu$ 编码为 Chebyshev 矩向量 $\boldsymbol{\tau}^{(\nu)}$。多项式核用 $K = \lceil\alpha_n/\lambda_2\rceil$；**非多项式核用余项判据 $K_f$**（$\sum_{k>K}\lvert c_k\rvert  \le \gamma\max\rvert c\lvert$，§13.4 v1.2）；**凡用核展开必先剥离零模**（§13.5）—— *化函数为有限向量*。
2. **代数化**（定义 1.2）：方程 $\mathcal{F}(\sigma)=0$ 化为矩空间方程。**多谱形耦合**体现为块 Jacobian $J \in \mathbb{R}^{q\times p(K+1)}$，耦合项由乘积法则自动落入块结构 —— *化泛函方程为代数方程*。
3. **路由**（Op14）：残差经分片嵌入 $\Xi_\nu$ 与灵敏度向量合成至全局 1-链，做 Hodge 三分量分解 —— *化残差为拓扑分量*。
4. **反演**（Op15 → 3.5b → 16）：内生拟牛顿单行闭式更新边权，**回溯线搜索（§15.4）二次缩步保证 $\Psi$ 严格下降**，Hankel 钳制保证解的谱形可行性 —— *在图空间上迭代收敛*。
5. **裁定**（Op17）：**默认同调解判据 $\|h\| \le \epsilon_{\text{endo}}$**，并附加 `exhausted`（已榨干）或 `step_dead`（方向耗尽）条件（§17.2 v1.3）；仅当**方向已耗尽且仅调和剩余**时才宣告拓扑障碍、移交算子 9 缝合，否则判「继续」或「数值停滞」—— *给出解或证明其不存在*。
6. **实现**（Op18）：在同调类内取 Dirichlet 能最小的规范代表，Stieltjes 反演重构谱密度，Fiedler 符号门赋自旋 —— *输出图结构 + 三项可信度证书*。

**本方法学的三个「不」**：
- **不做全网特征分解**（公设 1，全程闭合行走 + 三项递推）
- **不引入外部参数**（公设 3，一切阈值由 $\lambda_2/\alpha_n$ 内生生成）
- **不碰分片对角元**（公设 2，旋度对冲仅在边/环空间进行）

**解的语义（v1.1）**：默认输出**同调解**（$h = 0$，即残差恰当）而非精确解（$r = 0$）。两者的差由 $\|D\phi + C^T\psi\|$ 度量，作为「恰当残差预算」写入证书，交由算子 6/7 在后续脉冲中吸收。唯一性**只在同调类意义下成立**（定理 S5）。

---

## 七、v1.0 验证协议

| # | 验证项 | 预期 | 依据 |
|---|---|---|---|
| V1 | 矩编码正确性：$\tau_k$ 由递推算得 vs `eigvalsh` 直算 | 相对误差 $< 10^{-10}$ | 定理 S1 |
| V2 | 灵敏度解析式 vs 中心差分 | 相对误差 $< 10^{-6}$ | 13.3 式 |
| V3 | Hodge 正交性：$\langle D\phi, C^T\psi\rangle = \langle D\phi, h\rangle = \langle C^T\psi, h\rangle = 0$ | $\approx 0$ | 定理 S3 |
| V4 | 调和判据：$D^T h = 0$ 且 $C h = 0$；$\dim\mathcal{H}_1 = \beta_1 = \nu - \mathrm{rank}(\partial_2)$，$\nu = m_g-n+\beta_0$ | 成立（数值秩） | 定理 S3 + 术语约定 |
| V5 | 可解方程（如 $\tau_2 - c = 0$）残差单调下降 | $\lVert r_{\kappa+1}\rVert  \le \lVert r_{\kappa}\rVert$ | 定理 15.2 |
| V6 | Dirichlet 能单调非增 | $\Delta\mathcal{E}_D \le 0$ | 定理 15.2 |
| V7 | 更新方向正交性：$\Delta M \perp \mathcal{H}_1$ | $\langle \Delta M, h\rangle \approx 0$ | 定理 15.3 |
| V8 | Hankel 钳制后两矩阵半正定 | $\lambda_{\min}(H^{(0)}), \lambda_{\min}(H^{(1)}) \ge -\epsilon$ | 定理 16.1 |
| V9 | 拓扑障碍用例：$\beta_1 = 0$ 图上要求非零同调残差 | Op17 正确告警且 $\lVert h\rVert$ 不下降 | 定理 S3 |
| V10 | 闭合流守恒：取 $E = D\varphi$（自动满足 $CE=0$），注入 $\psi$ 后 $\Delta(E^T C^T B)$ | $= 0$ | 定理 14.1 |
| V11 | 反例对照：取 $CE \neq 0$ 的非闭合流，同样注入 | $\Delta \neq 0$，验证时序必要性 | 推论 14.1 注 |

### v1.1 新增验证项（多谱形耦合 / 非多项式核 / 同调解）

| # | 验证项 | 预期 | 依据 |
|---|---|---|---|
| **V12** | 多谱形耦合：两分片方程 $\tau_2^{(1)}\tau_2^{(2)} - c = 0$，块 Jacobian + 分片嵌入 $\Xi_\nu$ | 残差单调下降并裁定解出 | §14.4 |
| **V7b** | 方程尺度不变性：$F\to sF$（$s=1,10,100$）时 $\Delta M$ 必须不变 | 新式相对偏移 $<10^{-8}$；v1.0 旧式显著偏移（尺度依赖） | 定理 15.1' |
| **V13** | 非多项式核 $\ln\hat\lambda$：Chebyshev 系数和 $\mathbf{c}^T\boldsymbol{\tau}^{\text{red}}$ vs 约化谱积分（须先零模剥离） | 实测误差 $\le$ Bernstein 尾界 $\sum_{j>K_f}\lVert c_j\rVert$，且 $\le \gamma\lVert \text{exact}\rVert$ | §13.4 / §13.5 |
| **V14** | Bernstein 椭圆率：实测 $\ln$ 核系数衰减率 vs $\rho = \frac{1+\gamma}{1-\gamma}+\sqrt{\left(\frac{1+\gamma}{1-\gamma}\right)^2-1}$ | 实测衰减率与理论 $\rho$ 同量级 | 定理 13.2 |
| **V15** | 同调解 vs 精确解：同一方程在 $\beta_1>0$ 复形上分别用两种判据 | 同调解步数 $\le$ 精确解步数，且 $\lVert h\rVert$ 达标 | 定义 3.1 |
| **V16** | 同调距离：两个不同实现 $M_1^\star\neq M_2^\star$ 但同调等价（须共用同一组锁定尺度 + 锁定壳层缩放，且两者均判定 SOLVED） | $d_{\text{hom}}\le\epsilon_{\text{endo}}$ 而 $\lVert M_1^\star - M_2^\star\rVert  \gg 0$ | 定义 3.2 / 定理 S5 / §13.6 |
| **V17** | 退化警告：$\beta_1 = 0$ 复形上 $\lVert h\rVert  \equiv 0$ 对任意图恒成立 | 同调解判据失效，须走规范代表准则 | §二·续 |
| **V18** | 规范代表：同调等价类内按 Dirichlet 能最小唯一化 | 输出唯一代表 + 三项证书 | 算子 18 / 定理 18.1 |

### v1.0 实测结果（n=12 环形+弦边复形，m_g=24）

参考实现 `Operator_13_18_P.py`（由 v1.0 的 `Operator_13_17_P.py` 升级而来）的实跑输出（12/12 通过，含 V7b）：

| # | 验证项 | 实测 | 结论 |
|---|---|---|---|
| V1 | 矩编码递推 vs 特征分解直算 | $1.86\times10^{-15}$ | PASS |
| V2 | 灵敏度解析式 vs 中心差分 | $3.57\times10^{-10}$ | PASS |
| V3 | Hodge 正交性 + 勾股等式 | $2.82\times10^{-15}$ | PASS |
| V4 | 调和判据 $\lVert D^{Th}\rVert,\lVert Ch\rVert$ | $1.10\times10^{-14}$ | PASS |
| V5 | 可解方程残差单调下降 | $F:\ 7.16\!\times\!10^{-2}\to3.83\!\times\!10^{-3}$（4 步） | PASS |
| V6 | 目标泛函 $\Psi$ 单调非增 | $2.57\!\times\!10^{-3}\to7.32\!\times\!10^{-6}$ | PASS |
| V7 | $\langle\Delta M,h\rangle$ | $4.42\times10^{-16}$ | PASS |
| V8 | Hankel 钳制可行性恢复 | $-3.73\!\times\!10^{-1}\to-1.0\!\times\!10^{-9}$（$t^\star=0.099$） | PASS |
| V9 | 调和残差驱动反演 | $\lVert\Delta M\rVert = 0$（完全无法消除） | PASS |
| V10 | 闭合流 $E=D\varphi$ 配对守恒 | $6.29\times10^{-17}$ | PASS |
| V11 | 非闭合流反例 | $-4.12\times10^{-1}$（显著非零） | PASS |

**两组复形对照**（这是 V9 能够成立的关键）：

| 复形 | 面数 $f$ | $\mathrm{rank}(\partial_2)$ | $\nu$ | $\beta_1$ | 方程可解性 |
|---|---|---|---|---|---|
| 闭复形（加弦边闭链为第 13 面） | 13 | 13 | 13 | **0** | 残差全在梯度+旋度，4 步收敛 |
| 有洞复形（仅 12 个三角形） | 12 | 12 | 13 | **1** | 调和分量不可消除，需算子 9 缝合 |

**实测暴露的两个工程要点**（已写入实现）：
1. **内生动量会过冲**：$\beta_{\text{mom}}=0.798$ 时残差出现振荡（V6 单调性失败），故默认关闭；若启用必须配合回溯（这印证了定理 15.1 的信赖域只保证单步有界，不保证动量累积后仍单调）。
2. **Hankel 钳制应走「回退」而非「交替投影」**：单步交替投影 8 次后仍残留 $-6.7\times10^{-2}$ 的负特征值；改用沿「上一步可行矩 → 新矩」连线的二分回退（凸集上的最大可行步长）后，一步即恢复到 $-10^{-9}$。前者不收敛，后者保证输出可行。

### v1.1 实测结果（同一复形族，参考实现 `Operator_13_18_P.py`，12/12 + 7/7 全通过）

**v1.0 项在改用牛顿归一后全面提速**（$n=12$ 闭复形，$\alpha_n=7.229$，$\lambda_2=1.456$，$\gamma=0.2014$，$K=5$）：

| # | 验证项 | v1.0 实测 | v1.1 实测 | 结论 |
|---|---|---|---|---|
| V5 | 可解方程残差单调下降 | $7.16\!\times\!10^{-2}\to3.83\!\times\!10^{-3}$（4 步，**非单调**） | $7.16\!\times\!10^{-2}\to2.71\!\times\!10^{-3}$（**2 步，严格单调**） | PASS |
| V6 | 目标泛函 $\Psi$ 非增 | $2.57\!\times\!10^{-3}\to7.32\!\times\!10^{-6}$ | $2.57\!\times\!10^{-3}\to3.68\!\times\!10^{-6}$（单调性恢复） | PASS |
| V7b | 方程尺度不变性 $F\to sF$ | — | 新式 $\lVert \Delta M\rVert$ 恒为 $4.881435483\times10^{-2}$（$s=1,10,100$，相对偏移 $8.4\times10^{-15}$）；旧式 $3.31\times10^{-1}\to3.57\times10^{-3}\to3.57\times10^{-5}$（跨 4 个数量级） | PASS（旧式 FAIL） |

**v1.1 新增项实测**：

| # | 验证项 | 实测 | 结论 |
|---|---|---|---|
| V12 | 多谱形耦合 $\tau_2^{(1)}\tau_2^{(2)}-c=0$（$p=2$） | $F:\ -2.290\!\times\!10^{-3}\to+1.039\!\times\!10^{-4}$（2 步，单调） | PASS |
| V13 | $\ln\hat\lambda$ 展开（含零模剥离） | $\xi_0=-1.5045$，$\rho=2.6286$；误差随阶数 $1.50\!\times\!10^{-2}(K{=}1)$ → $1.61\!\times\!10^{-2}(K{=}2)$ → $4.39\!\times\!10^{-3}$ → $1.61\!\times\!10^{-4}$ → $5.71\!\times\!10^{-5}(K{=}5)$ → $2.40\!\times\!10^{-7}(K{=}8)$ → $7.82\!\times\!10^{-10}(K{=}16)$；v1.2 余项判据给出 $K_f=2$，实测误差 $1.61\!\times\!10^{-2}\le$ 尾界 $5.19\!\times\!10^{-2}$ 且 $\le$ 内生容差 $\gamma\lVert \text{exact}\rVert =9.81\!\times\!10^{-2}$ | PASS |
| V14 | Bernstein 椭圆率 | 实测 $\rho_{\text{fit}}=3.129$ vs 理论 $\rho=2.629$，比值 $1.19$ | PASS |
| V15 | 两级判据（$\beta_1=1$） | 同调解 2 步 / 精确解 2 步，**无分歧点**（$\rho_h\approx0.947>\gamma$ 所致，见 §17.1 限定） | PASS |
| V16 | 同调距离 | $\lVert M_a^\star-M_b^\star\rVert =7.53\!\times\!10^{-1}$，$d_{\text{hom}}=3.42\!\times\!10^{-3}\le\epsilon_{\text{endo}}$；$\rho_h$ 扫描均值 $0.9473$ | PASS |
| V17 | $\beta_1=0$ 退化警告 | 5 个随机残差的 $\lVert h\rVert \in[6.5,14.9]\times10^{-15}$，同调解集 = 全空间 | CONFIRMED |
| V18 | 规范代表（Dirichlet 能最小） | $E_a=3.05\times10^{-9}$ 胜出，输出三项证书 | PASS |

**v1.1 实测暴露的四个要点**（均已回写进规范正文）：
1. **牛顿归一取代 $1/(1+q)$**（§15.2）——$1/(1+q)$ 不具方程尺度不变性，收敛速度取决于 $F$ 的书写量级，实测慢 175 倍。
2. **内生尺度必须锁定**（§13.6）——灵敏度不对 $\alpha_n$ 求导，故 $\alpha_n$ 逐步刷新会使 $F$ 跳变、$\Psi$ 单调性破坏；改用「漂移 $>\gamma$ 触发刷新」后 2 步严格单调收敛。
3. **奇异核须先剥离零模**（§13.5）——$\ln$ 的奇点在移位变量上恰为 Bernstein 奇点 $\xi_0$，零模正落在支撑外，减掉其矩贡献即可，无需特征分解。
4. **同调解判据的收益边界**（§17.1）——$\rho_h=\|h\|/\|r\|$ 与 $F$ 无关且实测近似为常数 $0.947$，故调和通道不可独立压缩；同调解的价值是**放宽可接受解集** $\{r=0\}\to\{h=0\}$，而非加快收敛。

### v1.2：「10 个随机方程」压测（`bench_random_equations.py`，10/10 通过）

方程族：E01 $\tau_3$／E02 $\sum a_k\tau_k^2$（单谱形）；E03 双分片乘法／E04 加权线性混合／E05 三谱形交叉耦合；E06 $\ln$／E07 $\sqrt{\ }$／E08 Stieltjes（非多项式核）；E09 多项式 $\parallel\exp$／E10 乘法 $+\ln$（跨分片混合核）。目标常数由介值定理内生构造 $c=(1-u)G(m_a)+uG(m_b)$，$u\sim U(0.15,0.85)$——保证随机且良置。

**验证独立于管线**：`F(τ)` 走 Op13 三项递推，**验证走 `eigvalsh` 精确谱**（SRE 禁止算子内部做特征分解，故 eigh 只能作为终端 ground truth 基准存在）。六项：

| 项 | 内容 | 实测范围 |
|---|---|---|
| V-A | 矩交叉 $\max\lVert \tau_{\text{pipe}}-\tau_{\text{eig}}\rVert$ | $5.3\!\times\!10^{-16}\sim2.1\!\times\!10^{-15}$ |
| V-B | 独立残差 $\lVert G_{\text{eig}}(M^\star)-c\rVert /\lVert G(m_a)-c\rVert$（阈值 $\gamma$） | $4.9\!\times\!10^{-3}\sim1.7\!\times\!10^{-1}$ |
| V-C | 核保真：展开 vs 精确谱积分（阈值 $\gamma$） | $1.1\!\times\!10^{-3}\sim1.4\!\times\!10^{-1}$ |
| V-D | 合法性：正边权、$\lambda_2>0$、Hankel 可行 | E01/E09 为二级裁定（见 §13.6 表） |
| V-E | $\Psi=F^2/2$ 单调非增 | 10/10 |
| V-F | 算子 18 三项证书 | 10/10 |

**由此暴露并修正的三处**（详见 §13.4／§13.5／§13.6）：$K_f$ 判据由单项改余项；零模剥离由奇异核专属升级为通用要求；多分片须同时冻结 $\alpha_n$ 与 $\lambda_2$。附带厘清：冻结尺度**显式破坏**了重标定规范冗余，故 §13.6 的壳层缩放不可施加于已求得的解。

**非多项式核的精度代价已明码标价**（E09 的 $K$-sweep）：$K{=}2{:}1.1\!\times\!10^{-3}$，$K{=}4{:}1.2\!\times\!10^{-5}$，$K{=}6{:}2.7\!\times\!10^{-8}$，$K{=}8{:}3.4\!\times\!10^{-11}$。达到 $\gamma$ 级需 $K\ge2$，达到 $10^{-6}$ 级需 $K\ge6$。

### v1.3：「10 题型 × 5 组 = 50 道方程」压测（`bench_random_equations.py`，50/50 通过）

把 v1.2 的 10 道随机方程推广为 **10 种题型 × 5 组随机实例 = 50 道**：题型 E01–E10 不变，每组用独立种子区块（`SEED_BASE = 20260924`，`case_seed(b,i) = SEED_BASE + b*1000 + i`；$b=0$ 退化为 v1.2 的历史种子，保证可复现）。目标常数仍由介值定理内生构造 $c=(1-u)G(m_a)+uG(m_b)$，$u\sim U(0.15,0.85)$。全部解方程过程、轨迹与六项验证留档于 `bench_out/problem_set.md`（题集，50 题题面+解答）与 `bench_out/report.md`。

| 项 | 实测 |
|---|---|
| 总判定 | **50 / 50 SOLVED** |
| 总步数 | 286 步（均值 $5.72$ 步/题） |
| V-A 矩交叉 $\max\lVert \tau_{\text{pipe}}-\tau_{\text{eig}}\rVert$ | $\le 1.29\times10^{-14}$（机器精度） |
| V-B 独立残差 $\lVert G_{\text{eig}}(M^\star)-c\rVert /\lVert G(m_a)-c\rVert$（阈值 $\gamma$） | 49 题 $<10^{-9}$；B2-E02 $=1.29\times10^{-1}$ |
| V-D 合法性 | 50/50 |
| V-E 单调性 $\Psi$ 非增 | 50/50 |
| V-F 算子 18 三项证书 | 50/50 |
| 总耗时 | $\approx 0.9$–$1.1$ s |

**题型步数分布**（每组 5 个实例）：E01 $[5,6,5,5,5]$；E02 $[5,14,4,7,7]$；E03 全 $6$；E04 $[8,5,7,6,7]$；E05 $[6,6,5,6,6]$；E06 $[5,5,5,6,5]$；E07 $[5,5,5,4,5]$；E08 $[5,5,6,6,5]$；E09 全 $5$；E10 $[5,6,6,6,6]$。

**由此暴露并修正的三处**（详见 §15.4／§17.1／§17.2，对应题集第五章 5.1–5.3）：
1. **`OBSTRUCTION` 假阳性**——判据带宽 $1/\gamma$，良置问题被误移交算子 9；现要求 `step_dead` 才宣告障碍。
2. **信赖域缺失**——$\eta_N$ 归一删掉信赖域，强非线性实例过冲、$\Psi$ 上升；现补 Phase 3.5b 内生回溯线搜索。
3. **`SOLVED` 同义反复**——只看「首次跨过 $\epsilon$」会使 V-B 与停机量同阈值；现要求附加 `exhausted` 条件。

**修正确认**：三处修正后主实现回归仍 **19/19**（V1–V18 + 附加项）；B2-E02 由「比率 $\approx0.85$ 的慢振荡」变为 **14 步严格单调收敛**，V-B 由 $7.30\times10^{-1}$ 降到 $1.29\times10^{-1}$（$<\gamma = 0.1761$），轨迹中 $t_\kappa=0.5$（$\kappa=3,4,5$）、$t_\kappa=0.25$（$\kappa=12$）确证线搜索在起作用。

---

## 八、与现有算子体系的接口声明

| 本层算子 | 依赖的既有算子 | 依赖内容 |
|---|---|---|
| Op13 | Op6、Op10 | $(\alpha_n,\lambda_2)$ 谱资产；$\mathcal{O}(1)$ 伪逆设施；$N_K \le K_0$ 视界钳制 |
| Op14 | Op6、Op7、Op10 | 势重解 $\Phi$；$B$ 场蛙跳；$(DD^T)^{\dagger}$ 局域求解 |
| Op15 | Op7、Op10 | 边界算子 $D,C$；Sherman-Morrison 增量递推；Dirichlet 能单调红线 |
| Op16 | Op4、Op9 | 内生谱支撑 $[\gamma,1]$；自适应谱窗 $\tau(s)$（用于告警计数） |
| Op17 | Op8、Op9 | $\mu_{\text{trace}}$ 仲裁链；Betti 缝合；$\mathcal{S}_{\text{stable}}$ 终止判据 |
| Op18 | Op3、Op4、Op5、Op15 | Fiedler 符号门；$c_e$ 反演 $W_e$；度数关系校核；$\mathcal{H}_1^\perp$ 上的能量下降方向 |

**反向贡献**：本层为既有体系新增三项能力——
1. **谱矩的局域无分解计算途径**（定理 S1），可被 Op12 的 Möbius 相位检测复用，替代其 $\mathrm{tr}(M^k)$ 的显式矩阵幂；
2. **加权 Hodge 拉普拉斯 $A$ 与内生信赖域**（定理 15.1），为 Op7 的场迭代提供无外部参数的自适应步长机制；
3. **「闭而非恰当」作为一等公民判据**（定理 S3 + 定义 3.1）：为整个体系引入了一个判别「某约束是否可被场动力学吸收」的通用准则——凡残差落在 $\mathrm{im}\partial_1\oplus\mathrm{im}\partial_2^T$ 者均可安全交由 Op6/Op7 吸收，唯独调和分量必须诉诸拓扑变更。该准则不限于解方程，可用于判别任意 SRE 约束的可满足性。

---

**参考文献**：SRE Dynamics: The Book of the Void；SRE Fine-Structure-Constant Derivation；SRE Electron Topology (Zenodo)；`structure.md` v18.0；`Operator_10_C.md`；`Operator_11_C.md`；`Operator_12_C.md`
