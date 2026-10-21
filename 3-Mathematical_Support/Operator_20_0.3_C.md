# 算子 20：活化 / 桥接算子 $\mathcal{K}_{\text{act}}$
## 严格数学规范（v0.3）

**版本**：0.3（2026 年 10 月 · SRE 算子体系第 20 号，首次进入本项目正式文档序列）
**参考实现**：`sre_activation_operator.py`（公共入口 `operator_20_activation_index`；v0/v1 双版；支持 $\varsigma_e$ 显式定向；含 `self_test` 19/19 PASS）
**配套验证程序**：`verify_operator_20.py`（独立严格验证，V1–V14，**41/41 PASS**；仅依赖 numpy，V11 的算子 19 交叉检验需 networkx，缺失时自动 SKIP）
**冻结契约**：`activation_keys(res)` 必须恒定返回 **7 键**（`act_kappa`、`act_rho_path`、`act_nu_path`、`act_mu`、`act_rho_tot`、`act_nu_tot`、`act_gamma_star`），禁止后续实现改动此键数——下游指纹/报告管线按 7 键消费。
**前置依赖**：算子 1/4（$A_s$ 键图）、算子 11/12（电子自由度与环计数）、算子 13（$\mathcal{E}_{\text{mom}}$ 矩编码）、算子 14（$\mathcal{R}_{\text{hodge}}$ 同调路由）、算子 15（$\mathcal{N}_{\text{endo}}$ 拟牛顿反演）、算子 16（$\mathcal{C}_{\text{hankel}}$ 可行性钳制）、算子 17（$\mathcal{A}_{\text{sol}}$ 分支审计）、算子 19（$\mathbb{Z}_2$ 符号通道）
**编号说明**：接续 19 号编号为 **20**；与 `SRE-math_C.md` 既有 18 算子及 19 号无重合（边界见 §9）。

> **v0.2 相对 v0.1 的五项结构性修订**
> 1. **D1 引入外部边界图** $B=(V_B,E_B)$ 与界面边 $E_I\subseteq V\times V_B$——修正 v0.1 的 $C\subseteq V$（催化剂不能是骨架子集，否则造不出新环）。
> 2. **D1 引入吸附态 waypoint** $w_{\text{ads}}$——修正 v0.1 只有端点、导致 $\varrho$ 与催化剂无关的缺陷。
> 3. **新增顶点通道** $\delta_v$（氢覆盖）——H 仍不建节点，但覆盖变化成为独立通道，C–H 步骤不再不可见。
> 4. **$\rho$ 改名 $\varrho$**——避免与 Spearman 相关系数 $\rho_S$ 冲突。
> 5. **A20 改为 Pareto 公理**；新增 **T20.3（端点不变性）**，把“界面边不能改变端点同调类”从缺陷升格为定理。

> **v0.3 相对 v0.2 的三项修正（全部由实现期与验证期发现）**
> 1. **D7 / §2.3 的 $\gamma$ 定义自相矛盾，已重写。** v0.2 取"最大连通分量"，该分量按定义连通 ⇒ $\lambda_2>0$ ⇒ P20.5 的等价式恒真、V7 永不可观测。v0.3 改为**含活性位的分量之并** $X$（定义见 D7）。
> 2. **D2 补定向规范。** 键级变化是**无定向**数据，而 $C^1$ 坐标带定向；v0.2 未规定两者之间的赋值，导致 $\varrho$ 依赖顶点标号（实测 6 环均匀 $+0.5$：$2/3$ 与 $1/3$）。v0.3 把 $\delta$ 明确为**沿参考定向的定向上链**，并新增可选显式定向 $\varsigma_e$（**已接入实现**）；标号依赖作为边界 R11 显式声明。
> 3. **T20.4 原陈述为假，已修正。** v0.2 写"$\nu(\delta_v+c\mathbf1)=\nu(\delta_v)$"，但 $\nu$ 的分母是 $\|\delta_v\|$，平移会改变分母。正确不变性是：**对全部 waypoint 覆盖整体平移不变**（$\delta_v$ 只依赖差值）与**对 $\delta_v$ 的非零缩放不变**。

> **状态声明**：T20.1–T20.4、P20.5、P20.6 已给出完整证明；**H20.1（中心假设）与 C20.7（火山猜想）明确标注为未证**，须由 V12/V6 检验后才可升级。

---

## 摘要

SRE 现有体系里，「反应」**不是对象**：算子 19 处理静态图的 $\mathbb{Z}_2$ 符号通道，算子 13–18 处理谱形方程，二者都无法回答"为什么需要催化剂"。

算子 20 把反应建为**分段路径**，给出三个相互独立的通道：

| 通道 | 数学量 | 编码什么 | 代数归属 | 催化剂可影响？ |
|---|---|---|---|---|
| **边拓扑挫折** $\varrho$ | $\|\delta_{e,\text{harm}}\|/\|\delta_e\|$ | 键级重排中绕环不可消的部分 | $H^1(G;\mathbb{R})$ | **仅路径值** $\varrho_{\text{path}}$（见 T20.3） |
| **顶点对比度** $\nu$ | $\|\delta_v^{\perp}\|/\|\delta_v\|$ | 氢覆盖在各位点间的**再分配** | $C^0(G;\mathbb{R})$ | 是（经 waypoint） |
| **刚度瓶颈** $\kappa$ | $\int dt/(\gamma+\varepsilon)$ | 沿路径的谱隙塌缩 | 内生谱隙比 $\gamma=\lambda_2/\alpha_n$ | 是（经界面边） |

核心结论：

| 编号 | 命题 | 意义 | 状态 |
|---|---|---|---|
| **T20.1** | $\delta_e$ 恰当 $\iff$ 全环 $\mathrm{Hol}_\mathbb{R}=0$ $\iff\delta_{e,\text{harm}}=0$ | $\varrho$ 良定义 | **已证** |
| **T20.2** | $\gamma\in(0,1]$，$\kappa\ge\frac{1}{1+\varepsilon}$，对全局缩放不变 | $\kappa$ 无量纲、可跨体系比较 | **已证** |
| **T20.3** | 界面边**不能**改变端点同调类：$\varrho_{\text{tot}}$ 与催化剂无关 | 只有 $\varrho_{\text{path}}$ 可用于催化剂排序 | **已证（本节新增）** |
| **T20.4** | $\delta_v=\mu\mathbf1+\delta_v^{\perp}$ 正交分解；$\nu$ 对**覆盖整体平移**与非零缩放不变 | 顶点通道的规范不变性 | **已证**（v0.3 修正） |
| **P20.5** | $g(t^\ast)=0\iff$ 零权边含 $X$ 上的割（$X$=含活性位的分量之并） | 过渡态的操作性判据 | **已证**（v0.3 重述） |
| **P20.6** | 加边使 $\lambda_2,\alpha_n$ 同时不减，$\gamma$ **不单调** | 禁止"加边必降 $\kappa$" | **已证** |
| **H20.1** | $(\kappa,\varrho_{\text{path}},\nu_{\text{path}})$ 与 DFT 势垒秩相关 $|\rho_S|\ge0.7$ | **算子 20 的存在理由** | **未证** |
| **C20.7** | $\kappa(w_I)$ 对界面权重呈 U 形 | SRE 版 Sabatier 火山曲线 | **未证（猜想）** |

---

## 1 问题陈述

### 1.1 缺口

SRE 的图本体论只有"构型"，没有"反应"。由此：

1. 无法表述催化剂的作用（无"降低势垒"的对应物）；
2. 无法表述过渡态（无能量）；
3. 无法排序同拓扑金属（算子 19 对 Pt/Pd/Rh/Ni/Cu 逐位相同）。

### 1.2 本文任务

引入四个对象——**反应路径**、**外部催化剂边界**、**吸附态 waypoint**、**氢覆盖顶点通道**——定义算子 20：

- **输入**：重原子骨架 $G$、路径 waypoints $\{(w_j,n_j)\}$、外部边界图 $B$、界面边 $E_I$ 及权重 $w_I$；
- **输出**：$\mathcal{K}_{\text{act}}=(\kappa,\varrho_{\text{path}},\nu_{\text{path}},\mu;\ \text{诊断量})$，全部无量纲（$\mu$ 除外，它是每站点氢数变化）；
- **性质**：T20.1–T20.4、P20.5–P20.6，以及 H20.1/C20.7 的**可证伪协议**。

### 1.3 适用范围（硬边界）

- 仅**重原子骨架守恒**的反应：加氢/脱氢、键级重排、异构化、芳构化；
- **H 不建节点**，编码为顶点覆盖 $n_H\in\mathbb{Z}_{\ge0}^{V}$；C–H 的**键能**不在模型内，只有覆盖变化进入顶点通道；
- **C–C 断裂/骨架重排**改变 $V$，超出 v0.2；
- 仅**单个基元步**或"吸附 + 反应"两段路径；DBT 的 9 个 H₂ 是 9 次调用。

---

## 2 数学预备

### 2.1 上链复形与 Hodge 分解

对骨架 $G=(V,E)$，$|V|=n$，$|E|=m$。SRE 无 2-胞腔，故

$$C^0\xrightarrow{\ \delta_0\ }C^1\xrightarrow{\ \delta_1=0\ }C^2=0,\qquad H^1(G;\mathbb{R})=C^1/\,\mathrm{im}\,\delta_0 .$$

取**标准欧氏内积**（默认口径；加权内积见 §10 R3），有正交分解

$$C^1=\underbrace{\mathrm{im}\,\delta_0}_{\text{恰当（梯度）}}\ \oplus\ \underbrace{\mathcal{H}^1}_{\text{调和}},\qquad \dim\mathcal{H}^1=\beta_1(G)=E-V+c .$$

**注**：因无 2-胞腔，旋度分量为零；若上游图为填面复形（含 2-胞腔），必须改用三分量分解，本规范不覆盖该情形（§10 R4）。

### 2.2 边定向（v0.2 新增）

对每条无向边 $e=\{i,j\}$（$i<j$）固定参考定向 $i\to j$。环 $\gamma$ 的遍历方向与参考定向一致时取 $+$，相反取 $-$：

$$\varepsilon_{e,\gamma}=\begin{cases}+1,& \gamma\ \text{沿}\ i\to j\\-1,&\ \text{反向}\end{cases},\qquad \mathrm{Hol}_\mathbb{R}(\delta,\gamma)=\sum_{e\in\gamma}\varepsilon_{e,\gamma}\,\delta_e .$$

**规范条款（v0.3 新增，必读）**　$\varepsilon_{e,\gamma}$ 是**环遍历**相对参考定向的符号，与 §2.2 的参考定向是两件事。参考定向本身由**赋值约定**给出，规范固定为：

$$\boxed{\ \text{边 }e=\{i,j\}\text{ 的参考定向 }=i\to j\ (i<j)\ \text{（按顶点编号）}\ }$$

由此，**$\delta\in C^1(G;\mathbb{R})$ 是"沿参考定向"的定向上链**：$\delta_e$ 是沿 $i\to j$ 方向的增量，而非无向标量。

**由此产生的标号依赖（重要，见 §10 R11）**　键级（与键级变化）在化学上是**无定向**数据，而 $C^1$ 的坐标带定向；把无定向数据放进带定向坐标需要一次赋值，而不同赋值给出不同的 Hodge 分解。**因此 $\varrho$ 依赖顶点标号**：同一物理反应（6 环上键级均匀 $+0.5$，即"苯芳构化"）在标号 $[0,1,2,3,4,5]$ 下 $\varrho=2/3$，在交换 $1\leftrightarrow2$ 的标号下 $\varrho=1/3$（V3 实测）。

**可选显式定向 $\varsigma_e$（v0.3 新增输入）**　若使用者希望按化学直觉读（例如希望"环上均匀升键级"被算作纯环通道），可额外提供 $\varsigma_e\in\{+1,-1\}$，规范自动把 $\delta_e$ 换成 $\varsigma_e\delta_e$ 后再分解。**默认 $\varsigma_e\equiv+1$**（即与 v0.2 逐位一致）。$\varsigma$ 与 $\varepsilon_{e,\gamma}$、与 D7 的正则 $\varepsilon$ 均为不同记号。

**实现状态（v0.3 已接入）**　`build_reaction(..., orient=ς)` 接受标量 / 长度 $|E|$ 的向量 / $\{(i,j):\pm1\}$ 字典，取值非 $\pm1$ 时报错；`ς_e` **只作用于边通道**（$\varrho$），**不影响** $\kappa$（用 $W$，无定向）与 $\nu,\mu$（顶点通道，无定向）。附带公共辅助 `orient_from_cycle(n, edges, cycle)`：取 $\varsigma_e=\varepsilon_{e,\gamma}$，把"整环同步加/减键级"这一化学直觉转成规范定向。

实测（6 环均匀 $+0.5$，即苯芳构化，$\varsigma$ 默认与自然环遍历两种）：

| $\varsigma_e$ | $\varrho_{\text{tot}}$ | 读法 |
|---|---|---|
| $\equiv+1$（默认，$i<j$ 参考定向） | $2/3$ | 混合（含梯度成分） |
| $[+1,+1,+1,+1,+1,-1]$（自然环遍历） | $1$ | 纯环通道（化学直觉） |
| $-\varsigma$（全局取反） | 与 $\varsigma$ 相同 | $\delta$ 与梯度分量同时反号 |

V3 断言：默认复现 $2/3$、自然环定向给 $1$、全局取反不变、$\kappa$ 不受影响、字典形式与向量形式等价、非法值被拒、且 **T20.3 在任意 $\varsigma_e$ 下仍成立**。

### 2.3 谱形与内生谱隙比

加权邻接 $W\ge0$，$L(W)=\mathrm{diag}(W\mathbf1)-W$。谱形以 Chebyshev 矩 $\boldsymbol\tau(W)=(\tau_0,\dots,\tau_K)$ 编码（算子 13）。定义

$$\boxed{\ \gamma(W)=\frac{\lambda_2(L(W))}{\alpha_n(L(W))}\in(0,1]\ }$$

$\alpha_n=\lambda_n$ 为谱半径。$\gamma$ 的**计算域**由 D7 定义（v0.3 已重写：含活性位的分量之并 $X$，不是"最大连通分量"）。

---

## 3 定义

### D1（反应，v0.2 重写）

$$\mathcal{R}=\Big(G,\ \{(w_j,n_j)\}_{j=0}^{m},\ B,\ E_I,\ w_I\Big).$$

- $G=(V,E)$：重原子骨架，$E=E_R\cup E_P$（成键/断键用 0 权重表示）；
- $w_j\in[0,3]^{E}$：第 $j$ 个 waypoint 的键级（$w_0=w_R$，$w_m=w_P$）；上界 3 = 三键；
- $n_j\in\mathbb{Z}_{\ge0}^{V}$：第 $j$ 个 waypoint 的氢覆盖；
- $B=(V_B,E_B)$：**外部**催化剂边界图（$V_B\cap V=\varnothing$）；
- $E_I\subseteq V\times V_B$：界面边；$w_I\in\mathbb{R}_{\ge0}^{E_I}$；
- $\bar E=E\cup E_B\cup E_I$。

**两种路径**：
- **直接路径**：$m=1$，$(w_R,n_R)\to(w_P,n_P)$；
- **催化路径**：$m=2$，$(w_R,n_R)\to(w_{\text{ads}},n_{\text{ads}})\to(w_P,n_P)$。

### D2（分段位移）

对第 $j$ 段（$t\in[t_{j-1},t_j]$）：
$$\delta_e^{(j)}=w_j-w_{j-1}\in C^1(G;\mathbb{R}),\qquad \delta_{v}^{(j)}=n_j-n_{j-1}\in C^0(G;\mathbb{R}).$$

**端点位移**（与路径无关）：
$$\delta_{e,\text{tot}}=w_P-w_R,\qquad \delta_{v,\text{tot}}=n_P-n_R .$$

**约定**：$\delta_e$ 只在 $G$ 上取非零；界面边**不进入** $\delta_e$（界面边只影响 $\kappa$，见 D7）。这与 v0.1 在 $E_C$ 上取 $w_C$ 的写法不同，修正了语义不一致（v0.1 的 P0-4）。

**定向（v0.3 补）**：$w_j,n_j$ 是**无定向**的化学量；$\delta_e\in C^1$ 是**定向上链**。赋值按 §2.2 的规范条款：固定 $i<j$ 参考定向，或由使用者显式给出 $\varsigma_e$。由此 $\varrho$ 依赖顶点标号（边界 R11），**必须在报告中声明标号约定**。

### D3（$\mathbb{R}$ 值 holonomy）

按 §2.2 的定向约定：
$$\mathrm{Hol}_\mathbb{R}(\delta_e,\gamma)=\sum_{e\in\gamma}\varepsilon_{e,\gamma}\,\delta_{e}.$$

### D4（边通道 $\varrho$）

在 $G$ 上分解 $\delta_e=\delta_{e,\text{grad}}+\delta_{e,\text{harm}}$（$\delta_e$ 为 §2.2 的定向上链），定义

$$\varrho_{\text{tot}}=\frac{\|\delta_{e,\text{tot,harm}}\|}{\|\delta_{e,\text{tot}}\|}\in[0,1],\qquad
\varrho_{\text{path}}=\sum_{j=1}^{m}\ell_j\,\frac{\|\delta_{e,\text{harm}}^{(j)}\|}{\|\delta_{e}^{(j)}\|},$$

其中 $\ell_j=t_j-t_{j-1}$ 为段长，$\sum\ell_j=1$；若某段 $\|\delta_e^{(j)}\|=0$，该段贡献记为 $0$。约定 $\|\delta_{e,\text{tot}}\|=0$ 时 $\varrho_{\text{tot}}=0$。

**语义**：$\varrho_{\text{tot}}$ 是**反应**的拓扑挫折（端点决定）；$\varrho_{\text{path}}$ 是**机理**的拓扑挫折（路径决定）。

### D5（顶点通道 $\mu,\nu$，v0.2 新增）

对 $\delta_v\in C^0(G;\mathbb{R})$ 作正交分解
$$\delta_v=\mu\mathbf1+\delta_v^{\perp},\qquad \mu=\frac1n\sum_i\delta_{v,i},\qquad \mathbf1^\top\delta_v^{\perp}=0 .$$
定义
$$\nu_{\text{tot}}=\frac{\|\delta_{v,\text{tot}}^{\perp}\|}{\|\delta_{v,\text{tot}}\|}\in[0,1],\qquad
\nu_{\text{path}}=\sum_{j=1}^{m}\ell_j\,\frac{\|\delta_{v}^{(j),\perp}\|}{\|\delta_{v}^{(j)}\|},$$
若 $\|\delta_v\|=0$ 则相应量为 $0$。

**语义**：
- $\mu$ = 每站点**净**氢数变化（带符号；DBT 脱氢为负）；
- $\nu$ = 氢覆盖的**对比度**（位点间再分配的比例），对"整体加多少个 H"不敏感，只对"H 怎么分布"敏感。

### D6（谱形路径与约束反演）

对每段在矩空间取线性路径
$$\boldsymbol\tau(t)=(1-s)\boldsymbol\tau(w_{j-1})+s\,\boldsymbol\tau(w_j),\qquad s\in[0,1],$$
按 $s$ 顺序求解（warm start + 步长约束）：
$$w(t)=\arg\min_{w\in[0,3]^E}\ \|\boldsymbol\tau(w)-\boldsymbol\tau(t)\|^2+\lambda\|w-w_0(t)\|^2,\qquad \|w(s)-w(s-\Delta s)\|\le s_{\max}.$$

**注**（P1-3）：矩的线性插值在**测度层**恒可行（谱测度的凸性），但**图实现**未必可行；后者由算子 16 的 Hankel 钳制与算子 17 的分支审计判定。

### D7（刚度瓶颈 $\kappa$，v0.3 重写计算域）

**计算域 $X$（v0.3 核心修正）**　v0.2 取"含活性位的**最大连通分量**"，这是自相矛盾的：该分量按定义连通 ⇒ $\lambda_2>0$ ⇒ P20.5 的等价式恒真、$\gamma\to0$ 永不可观测。v0.3 改为**含活性位的分量之并**：

$$\boxed{\ X=V\ \cup\ \big\{b\in V_B\ :\ \exists\,(a,b)\in E_I,\ w_I(a,b)>0\big\}\ }$$

即：**骨架顶点全部视为活性位**，再加上"经正权界面边与骨架相连"的边界顶点。孤立边界顶点自动排除；当 $w_I=0$ 时 $X=V$。定义 $L|_X$ 为 $X$ 上由下式诱导的加权图 $W|_X$ 的拉普拉斯：

$$W|_X:\quad \text{骨架边取 }w(t),\quad \text{边界边取 }w_B,\quad \text{界面边取 }w_I .$$

于是

$$g(t)\equiv\frac{\lambda_2\big(L|_X(w(t))\big)}{\lambda_n\big(L|_X(w(t))\big)},\qquad \gamma_\ast=\min_{t}g(t),\qquad \boxed{\ \kappa=\sum_{j=1}^{m}\int_{t_{j-1}}^{t_j}\frac{dt}{g(t)+\varepsilon}\ }\quad(\varepsilon>0).$$

**约定**：$|X|\le1$ 时约定 $g=1$；当 $g(t)=0$（$X$ 上诱导图不连通）时该点对积分贡献按 $1/\varepsilon$ 计（数值上截断）。

**由此 P20.5 恢复可观测性**：$w_I=0$ 且骨架含零权割 ⇒ $g=0$ ⇒ $\kappa\sim1/\varepsilon$；催化剂经界面边把割的两侧重新桥接 ⇒ $\lambda_2>0$ ⇒ $\kappa$ 有限。**这正是 A20 的机制**（V7/V9 实测：$\kappa$ 26.76 → 6.66）。

### D8（输出与偏序）

$$\boxed{\ \mathcal{K}_{\text{act}}(\mathcal{R})=\Big(\kappa,\ \varrho_{\text{path}},\ \nu_{\text{path}},\ \mu;\ \underbrace{\varrho_{\text{tot}},\nu_{\text{tot}},\gamma_\ast,\text{feasible}}_{\text{诊断量}}\Big)\ }$$

**Pareto 偏序**：对同一反应的两个候选 $A,B$，
$$A\preceq B\iff \kappa_A\le\kappa_B,\ \varrho_{\text{path},A}\le\varrho_{\text{path},B},\ \nu_{\text{path},A}\le\nu_{\text{path},B},$$
且至少一项严格。**不定义标量化**——权重若需要，属外部输入。

**对照协议**：直接参考与催化候选使用**同一** $\bar E$；直接参考取 $w_I=0$（零权边不改变 Laplacian），催化候选取 $w_I>0$，并可选插入 $w_{\text{ads}}$。这样 $\kappa$ 可比。

---

## 4 定位公理

**A20（桥接公理，Pareto 版）**　催化剂的作用是**在固定化学计量下，沿路径同时改善三个通道**：

$$\boxed{\ C\ \text{有效}\iff \mathcal{K}_{\text{act}}(C)\preceq \mathcal{K}_{\text{act}}(\text{直接参考}),\quad \mu\ \text{固定}\ }$$

它**不是**"把 $\varrho$ 降为 0"——由 T20.3，端点的 $\varrho_{\text{tot}}$ 不可能被界面边改变；可行的是改变**路径**（经 $w_{\text{ads}}$）与降低 $\kappa$。

**H20.2（正交性假设，原 A20′）**　三通道编码独立障碍；任一为零不蕴含其余为零。由 V4 数值检验。

---

## 5 定理与证明

### T20.1（恰当性判据）

设 $G$ 连通，$\delta\in C^1(G;\mathbb{R})$。下列等价：

**(i)** $\delta$ 恰当（$\exists\varphi\in C^0$，$\delta_e=\varphi_i-\varphi_j$）；
**(ii)** 对所有环 $\gamma$，$\mathrm{Hol}_\mathbb{R}(\delta,\gamma)=0$；
**(iii)** $\delta_{\text{harm}}=0$（即 $\varrho=0$）。

**证明**
(i)⇒(ii)：$\mathrm{Hol}=\sum_{e\in\gamma}\varepsilon_{e,\gamma}(\varphi_i-\varphi_j)$，每条边在闭合遍历中恰好被抵消一次，故为 $0$。
(ii)⇒(i)：取基点 $v_0$，令 $\varphi_v=\sum_{e\in P(v_0\to v)}\varepsilon_{e,P}\delta_e$。若 $P,P'$ 是两条 $v_0\to v$ 路径，则 $P\cup P'^{-1}$ 是闭链；非简单时可分解为简单环之和，由 (ii) 其和为 $0$，故 $\varphi_v$ 与路径无关，于是 $\delta_e=\varphi_i-\varphi_j$。
(i)⇔(iii)：由 §2.1 的正交分解。$\square$

**推论 20.1.1**　$\varrho$ 与环基选取无关（$\delta_{\text{harm}}$ 是 $\mathcal{H}^1$ 上的正交投影）。

### T20.2（$\kappa$ 的界与缩放不变性）

对连通 $G$ 与任意 $W\ge0$：$\lambda_2\le\lambda_n=\alpha_n$，故 $g\in(0,1]$，

$$\kappa\ge\frac{1}{1+\varepsilon},$$

且 $L(cW)=cL(W)$ ⇒ $\gamma(cW)=\gamma(W)$，故 $\kappa$ 对**全局**权重缩放不变。

**证明**　$\lambda_2\le\lambda_n$ 显然；连通性给 $\lambda_2>0$；缩放相消。$\square$

**注意**：缩放不变性要求 $w$ 与 $w_I$ **同时**缩放；单独缩放界面权重会改变 $\kappa$（这正是 C20.7 要扫的量）。

### T20.3（端点不变性，v0.2 新增）

设 $\bar E=E\cup E_B\cup E_I$。对任意 $E_I$ 与 $w_I$，端点位移 $\delta_{e,\text{tot}}$ 在 $E$ 上不变，且

$$\varrho_{\text{tot}}(\bar E)=\varrho_{\text{tot}}(G).$$

**证明**　包含映射 $\iota:C^1(G)\to C^1(\bar E)$ 把 $E$ 上的 1-上链延拓为 $E_I$ 上取 0；对偶地 $H_1(G)\hookrightarrow H_1(\bar E)$ 是单射。对任意 $\gamma\subset G$，
$$\langle[\delta_{\text{tot}}],[\gamma]\rangle_{\bar E}=\sum_{e\in\gamma}\varepsilon_{e,\gamma}\delta_{e,\text{tot}}=\langle[\delta_{\text{tot}}|_G],[\gamma]\rangle_G$$
与 $E_I$ 无关。故 $\delta_{\text{tot}}$ 在 $H_1(G)$ 上的像不变，$\varrho_{\text{tot}}$ 不变。$\square$

**意义（关键）**：**催化剂不能改变反应端点的拓扑挫折**；它只能改变**路径**（插入 $w_{\text{ads}}$）与**刚度**（界面边）。这把 v0.1 的"公理不可满足"转成了清晰的分工。

### T20.4（顶点分解与规范不变性，v0.3 修正陈述）

$\delta_v=\mu\mathbf1+\delta_v^{\perp}$ 是正交分解（$\mathbf1^\top\delta_v^\perp=0$），且 $\nu$ 满足两条**正确**的不变性：

**(a) 对全部 waypoint 覆盖整体平移不变**　若 $n_j\mapsto n_j+c\mathbf1$（$c$ 与 $j$ 无关，即每个 waypoint 的所有位点同加 $c$），则所有 $\delta_v^{(j)}$ 与 $\mu,\nu$ 均不变；
**(b) 对 $\delta_v$ 的非零缩放不变**　$\nu(c\,\delta_v)=\nu(\delta_v)$（$c\neq0$）。

**证明**　(a) 平移使 $\delta_v^{(j)}=(n_j+c\mathbf1)-(n_{j-1}+c\mathbf1)=\delta_v^{(j)}$，逐项不变。$\square$
(b) $\delta_v=\mu\mathbf1+\delta_v^\perp$ ⇒ $c\delta_v=(c\mu)\mathbf1+c\delta_v^\perp$（$\mathbf1^\top(c\delta_v^\perp)=c\cdot0=0$，仍是正交分解），故
$$\nu(c\delta_v)=\frac{\|c\delta_v^\perp\|}{\|c\delta_v\|}=\frac{|c|\,\|\delta_v^\perp\|}{|c|\,\|\delta_v\|}=\nu(\delta_v).\ \square$$

> **v0.2 的错误陈述已删除**　v0.2 写"对任意 $c\in\mathbb{R}$，$\nu(\delta_v+c\mathbf1)=\nu(\delta_v)$"。该式**为假**：$\nu$ 的分母是 $\|\delta_v\|$，平移同时改变分子（不变）与分母（$c\neq0$ 时增大），故 $\nu$ 一般下降。数值反例见 V13。**这是 v0.2 的一处实质性错误**：正交分解本身正确，但由此推出的不变性被错误地写在 $\delta_v$ 上（应写在 $n_j$ 上，即 (a)）。

### P20.5（过渡态判据，v0.3 重述）

在 D7 的计算域 $X$（含活性位的分量之并）上，
$$g(t^\ast)=0\iff\lambda_2\big(L|_X(w(t^\ast))\big)=0\iff \text{零权边集包含 } X\ \text{上诱导图的一个割}.$$

**证明**　$\lambda_2=0\iff L|_X$ 不连通（重根零模）$\iff$ 存在全零权的割。取 $X$ 为"骨架顶点 ∪ 正权界面边所连边界顶点"，已排除两类平凡零模：(i) 被移除的 H 造成孤立顶点——H 不建节点，不产生零模；(ii) 无正权界面连边的孤立边界顶点——不计入 $X$。$\square$

**意义**：过渡态 = 加权骨架的谱退化点；$\kappa$ 度量路径靠近退化点的程度；催化剂的作用是**让路径绕开退化点**（提供旁路）。**v0.2 在此处不可观测**（"最大连通分量"按定义连通 ⇒ 恒有 $\lambda_2>0$ ⇒ 右端恒假），v0.3 重写计算域后该判据才真正可检验（V7）。

### P20.6（$\gamma$ 不单调）

加边 $W'=W+\Delta W$（$\Delta W\ge0$）使 $L'\succeq L$，Weyl 定理给逐序特征值不减，故 $\lambda_2,\alpha_n$ 同时不减，$\gamma'=\lambda_2'/\alpha_n'$ 与 $\gamma$ **无固定大小关系**。

**证明**　$\Delta L=w(e_i-e_j)(e_i-e_j)^\top\succeq0$；Weyl 单调；比值不定。$\square$

### C20.7（火山猜想，**未证**）

固定化学环境、仅变 $w_I$，$\kappa(w_I)$ 呈 U 形：$w_I\to0$ 无桥接（高）；中间 $w_I^\ast$ 最小；$w_I$ 过大时界面刚性主导（回升）。

**状态**：猜想，由 V6 检验；若单调或非单峰则证伪，不影响 T20.1–T20.4。

### H20.1（中心假设，**未证**）

$(\kappa,\varrho_{\text{path}},\nu_{\text{path}})$ 与 DFT 势垒 $\Delta^\ddagger$ 的秩相关 $|\rho_S|\ge0.7$，且符号在同类反应族内一致。**若 $|\rho_S|<0.5$ 或符号翻转，算子 20 降级为结构描述符。**

---

## 6 算法设计

### 6.1 v0（低成本，先验证 H20.1）

```
输入 R=(G, waypoints, B, E_I, w_I)
1. 对每段 j:
     δe ← w_j − w_{j−1}           (E 上)
     δv ← n_j − n_{j−1}           (V 上)
     Hodge(δe) on G → δe_harm ;  ϱ_j ← ‖δe_harm‖/‖δe‖
     δv = μ_j 1 + δv⊥ ;          ν_j ← ‖δv⊥‖/‖δv‖
2. ϱ_path ← Σ ℓ_j ϱ_j ;  ν_path ← Σ ℓ_j ν_j ;  μ ← mean(n_P − n_R)
3. for t in 每段 linspace:
     w(t) ← (1−s)w_{j−1} + s w_j     (E 上；界面边恒为 w_I)
     L(t) ← L|_X(w(t)) ;  g(t) ← λ2/λn  (X = 含活性位的分量之并, D7)
4. γ* ← min g ;  κ ← Σ_j trapz(1/(g+ε), 段)
输出 (κ, ϱ_path, ν_path, μ; ϱ_tot, ν_tot, γ*, feasible)
```

复杂度 $O(m\cdot n^3)$（稠密特征分解）或 $O(m\cdot |E|\cdot \text{iter})$（Lanczos）。

### 6.2 v1（完整）

矩空间插值 + 约束反演（D6）+ 算子 16/17 的可行性与分支审计。代价高一个量级，但路径是谱形空间的规范代表。

### 6.3 参数

| 参数 | 含义 | 默认 | 备注 |
|---|---|---|---|
| $K$ | 每段采样点 | 32 | — |
| $\varepsilon$ | $\kappa$ 正则 | $10^{-3}$ | **必须报告 $\kappa$ 在 $\{10^{-1},10^{-2},10^{-3}\}$ 下的排序稳定性**（P1-5） |
| $\lambda$ | D6 锚正则 | $10^{-2}$ | — |
| $s_{\max}$ | 步长上界 | $0.1$ | 保证路径连续 |
| $w_I$ | 界面权重 | **外部输入** | 见 §10 R1 |

---

## 7 复杂度

| 版本 | 主要开销 | 量级（n≈21 骨架） |
|---|---|---|
| v0 | 每段 $K$ 次极端特征值 | 秒级 |
| v1 | 每段 $K$ 次反演 × 算子 15 迭代 | 分钟级 |
| Hodge | 稀疏最小二乘 $O(m)$ | 可忽略 |

---

## 8 验证协议（V1–V14）

| 编号 | 断言 | 对应 |
|---|---|---|
| V1 | 带定向的 $\mathrm{Hol}_\mathbb{R}$ 与手算一致（含反向遍历） | D3/§2.2 |
| V2 | T20.1 三等价式在 $10^3$ 随机图上成立 | T20.1 |
| V3 | $\varrho$ 与生成树/环基选取无关；显式测出 $\varrho$ 的顶点标号依赖；**$\varsigma_e$ 定向条款**（默认 $2/3$、自然环定向 $1$、全局取反不变、不影响 $\kappa$、非法值被拒、T20.3 仍成立） | 推论 20.1.1 + §2.2 + R11 |
| V4 | 三通道秩相关 $|\rho_S|<0.7$（正交性） | H20.2 |
| V5 | $\kappa$ 对全局缩放不变；对单独 $w_I$ 缩放**不**不变 | T20.2 |
| V6 | C20.7 火山形态（扫 $w_I$，判单峰/单调） | C20.7 |
| V7 | 构造零权割，验证 $\gamma\to0$、$\kappa\sim1/\varepsilon$ | P20.5 |
| V8 | 加边反例：$\gamma$ 上升/下降各一例 | P20.6 |
| V9 | $w_I=0$ 时催化路径退化为直接路径的 $\kappa$ | D8 对照协议 |
| V10 | v0 与 v1 排序一致（Spearman $\ge0.8$） | §6 |
| V11 | 二分+单轨道骨架，界面接枝仍不能开算子 19 的符号通道 | §9 |
| V12 | **DFT 对标**：5–8 基元步，报告 $\rho_S$ 与消融 | H20.1 |
| V13 | 顶点通道：$\mu=(1/n)\sum\delta_v$、$\delta_v^\perp\perp\mathbf1$、$\nu$ 对覆盖整体平移与非零缩放不变、纯均匀加载 $\nu=0$；附三个解析算例 | T20.4/D5 |
| V14 | 端点不变性：任意 $E_I$ 下 $\varrho_{\text{tot}}$ 不变 | T20.3 |

V1–V11、V13–V14 为内部一致性（可立即执行）；**V12 是唯一决定 H20.1 的外部验证**。

---

## 9 与既有算子的边界

| 算子 | 对象 | 与 20 的关系 |
|---|---|---|
| 1/4 | $A_s$ 键图 | **上游**：提供 $G$ |
| 11 | 自旋极性 | 不同对象：顶点势型极性恒平凡（19-T1） |
| 12 | 环计数、Möbius | 复用 $\beta_1=\dim\mathcal{H}^1$ |
| **13** | 谱形矩 $\mathcal{E}_{\text{mom}}$ | **子程序**：$\boldsymbol\tau(W)$（D6） |
| **14** | 方程残差 Hodge 路由 | ⚠ **最近邻**：14 分解**方程残差** $r$，20 分解**反应位移** $\delta$；机制复用、对象与输出不同 |
| **15** | 拟牛顿谱形反演 | **子程序**：D6 |
| **16** | Hankel 钳制 | **子程序**：`feasible` |
| **17** | 解分支审计 | **子程序**：分支裁定 |
| **18** | 同调解实现 | **类比**：D6 的锚 $w_0$ 起规范固定作用 |
| 9/7 | Betti 缝合/上同调锁定 | 不同：作用于方程可解性 |
| **19** | $\mathbb{Z}_2$ 符号通道 | **正交互补**：19 符号（$\mathbb{Z}_2$）、20 量值（$\mathbb{R}$）+ 顶点 + 刚度 |

**与 19 的兼容命题（待严格证明）**　若 $G$ 二分且只有 1 条边轨道，任何**保二分**的界面接枝都不能使 19 的 $\sigma$ 非平凡；催化剂须以"同色顶点相连"的界面边造出奇环，才能同时打开符号通道（依据 19-T6）。

---

## 10 诚实边界与风险

下列条目在正文中以 **R1–R11** 引用。

1. **$w_I$ 是唯一自由输入，且无法内生。** $\Delta\chi$ 代理会预测 Ni 强于 Pt，与 DBT 实测相反。因此**算子 20 只能做"固定金属下的结构排序"，不能做"金属种类排序"**；后者须 DFT/实验标定 $w_I$。这也是算子 19 排不出 Pt/Pd 的根因。
2. **不是最小能量路径。** 矩空间线性插值只是规范代表；$\kappa$ 是指标，不是势垒上界。
3. **Hodge 内积口径**：默认标准欧氏内积（无参数）。若改用边权内积，$\varrho$ 会变；必须固定口径并在报告中声明。
4. **2-胞腔情形不覆盖**：若上游图为填面复形，旋度分量非零，§2.1 的二分解失效。
5. **$\kappa$ 的 $\varepsilon$ 敏感性**：零隙点附近 $\kappa\sim1/\varepsilon$；必须报告三档 $\varepsilon$ 的排序稳定性。
6. **H 的键能不在模型内**：顶点通道只编码覆盖的净量与对比度，不含 C–H 键解离能。
7. **0 K、无熵、无覆盖度竞争、无溶剂**：300 °C 的熵效应与竞争吸附不在体系内。
8. **$t$ 不是时间**，$\kappa$ 不是速率；$t$ 只是同伦参数。
9. **单基元步**：DBT 的 9 个 H₂ 是 9 次调用，不是一次。
10. **H20.1 未证**：算子 20 目前只有内部自洽性，没有任何实证支持。
11. **（R11）$\varrho$ 依赖顶点标号。** 键级变化是**无定向**数据，而 $C^1$ 的坐标带定向（§2.2 规范条款）；把无定向数据赋成定向上链需要一次人为约定，不同约定给出不同的 Hodge 分解。实测：6 环上键级均匀 $+0.5$（苯芳构化）在标号 $[0..5]$ 下 $\varrho=2/3$，交换 $1\leftrightarrow2$ 后 $\varrho=1/3$（V3）。**后果与要求**：(i) $\varrho$ 的**绝对值**不具跨文献可比性，只有**同一标号约定下的相对排序**有意义；(ii) 每份报告必须声明所用的标号约定（默认 $i<j$ 参考定向，或显式 $\varsigma_e$）；(iii) 跨体系比较 $\varrho$ 前必须先统一标号（例如用规范化的原子排序）。这是算子 20 目前**未解决**的理论缺口——根治需要从反应数据本身诱导定向，属 v1.0 待办。

---

## 11 待办清单

**已完成**

1. ~~实现 `sre_activation_operator.py`（v0 优先，含顶点通道）~~ **[完成]** 含 v0/v1 双版；
2. ~~实现 `verify_operator_20.py`（V1–V11、V13–V14）~~ **[完成]** 30/30 PASS；
3. ~~解析算例：苯芳构化（$\varrho>0$）、乙烷 C–C 单键旋转（$\varrho=0$）、乙醇脱氢（$\mu<0,\nu>0$）~~ **[完成]** 全部符合。

**v0.3 已完成的三项规范修正 + 一项入参接入**（全部由实现期/验证期发现，非实现缺陷）

4. ~~D7 / §2.3 的 $\gamma$ 计算域自相矛盾~~ **[已修]** 改为 D7 的 $X$（含活性位的分量之并）；P20.5 随之重述并恢复可观测性（V7/V9 实测）。
5. ~~D2 缺定向规范、$\varrho$ 依赖顶点标号~~ **[已修]** §2.2 新增规范条款（固定 $i<j$ 参考定向、$\delta$ 为定向上链、可选显式 $\varsigma_e$）；标号依赖不再隐藏，升格为边界 **R11**。
6. ~~T20.4 陈述为假~~ **[已修]** 原式 $\nu(\delta_v+c\mathbf1)=\nu(\delta_v)$ 为假；已改为正确形式（覆盖整体平移 + 非零缩放不变），并保留数值反例于 V13。
7. ~~实现 `sre_activation_operator.py` 的 $\varsigma_e$ 显式定向入参~~ **[已完成]** `build_reaction(..., orient=ς)` + 公共辅助 `orient_from_cycle(...)`；V3 断言 41/41 PASS，自测 19/19 PASS。

**待做**

8. **补 §9 兼容命题的严格证明**（V11 已给出二分/奇环两向的数值证据；缺的是证明）。
9. DBT 实例：C21 骨架 + 18 H 覆盖变化，跑 v0，输出 $(\kappa,\varrho,\nu,\mu)$。
10. **V12 DFT 对标**：5–8 个基元步，检验 H20.1——唯一决定算子存在理由的外部验证。
11. **v1.0 理论缺口（R11 的根治）**：从反应数据自身诱导边定向，使 $\varrho$ 脱离人为标号约定。在此之前，$\varrho$ 只可用于**同一标号约定下**的相对排序；$\varsigma_e$ 提供了手工修正手段，但不是自动解。

---

*v0.3。所有"已证"结论在无 2-胞腔的 1-维复形上成立；所有"未证"结论（H20.1、C20.7）已显式标注，不得在实现与报告中当作既成事实引用。v0.3 的三项修正中，第 3 项（T20.4）是 v0.2 的实质性数学错误，第 1 项（D7）是定义层自相矛盾，两者均已在验证程序中有对应断言。*
