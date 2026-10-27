# 算子 19：ℤ₂ holonomy / σ 电荷符号通道算子
## 严格数学规范、可解性推理依据与验证协议

**作者**：岳路
**版本**：1.0（2026 年 10 月 · SRE 算子体系第 19 号）
**参考实现**：`sre_z2_holonomy_bridge.py`（公共入口 `operator_19_z2_charge_channel`）
**配套验证程序**：`verify_operator_19.py`（独立严格验证，V1–V12，零外部依赖 numpy/networkx）
**前置依赖**：算子 1/4（SRE 平滑邻接 $A_s$ 的键图支撑）、算子 11（自旋极性诊断量 $s_i,\sigma_{ij}$）、算子 12（一阶贝蒂数 $\beta_1$ 环计数）
**上游论文**：《SRE 体系下正负电荷的涌现：量值、符号与数值确证》（下称"电荷涌现论文"）
**下游集成**：`sre_cluster_substitute_screen.py`（`z2_*` 字段接入化合物筛选流水线）
**编号说明**：算子在既有 18 号之后接续编号为 **19**；已逐条核验与 `SRE-math_C.md` 全部 18 个算子**无重合**（边界见 §9）。

---

## 摘要

SRE 动力学把电荷表述为「拓扑纽结的计数」。计数天然非负，只给出电荷的**量值**，无法给出**符号**。电荷涌现论文补全该缺口，提出电荷泛函

$$Q(K)=\sigma(K)\cdot\deg(K)\cdot e,\qquad \deg(K)=\beta_1(K)\bmod 2,\qquad \sigma(K)\in H^1(G;\mathbb{Z}_2).$$

其中「符号通道」$\sigma$ 被声明为一条 **$\mathbb{Z}_2$ 卷绕相位（holonomy）** 上同调类，但该论文以一个**独立数值脚本**（`_se_assignment_test.py`）在少数骨架与分子上做了抽样验证，**并未给出该算子的独立、可复用、可证明的实现规范**。本文把 $\sigma$ 通道**单独**实现为 **算子 19**，并给出三项此前缺失的内容：

1. **严格的推理依据**（§2–§5）：在分子键图的 **1-维链复形** 上，把「边极性 $\to$ 环 holonomy $\to$ 上同调类」的链路严格化，证明算子输出的良定义性，并给出**全部定理与证明**（T0–T8）。
2. **对应的论文**（本文）：给出算子的公理定位、与上游电子算子的桥接语义、与既有算子的边界，以及在官方骨架与分子层上的忠实复现。
3. **严格验证程序**（`verify_operator_19.py`）：把每条定理映射为可复现断言（V1–V12），运行全部通过即实证本规范。

核心结论（全部在 1-维复形上严格成立，不依赖任何外部参数）：

| 编号 | 定理 | 意义 |
|---|---|---|
| **T0** | 1-复形上 $\sigma$ 是 $H_1$ 上的 $\mathbb{F}_2$-线性泛函 | 良定义，可比较 |
| **T1** | 顶点势型极性 $s_e=t_it_j$ 的 holonomy **恒平凡** | **电荷符号不能由局部自旋重标定造出** |
| **T2** | Aut-不变赋值的非平凡可达性 $=$ $\mathbb{Z}_2$ 线性判据（$\exists$ 环 $i$、轨道 $o$，使 $m_{i,o}=1$）| 无需 $2^{\#\text{轨道}}$ 枚举 |
| **T3** | 平凡性判别**与环基选取无关** | 结果唯一 |
| **T4** | 乘以**余边界**（顶点势）不改变任何环 holonomy | $[s]\in H^1$ 是规范不变量 |
| **T5** | 符号通道 $\sigma$ 与量值通道 $\deg$ **正交独立** | 两通道分别编码 |
| **T6** | 二分图 + 单边轨道 $\Rightarrow$ **强制平凡**（电子型）| 电子 $Q_3$ 的结构来源 |
| **T7** | 分子层 Aut **必须保元素着色**，否则可达性判据失真（可致判据翻转）| 元素着色的必要性 |
| **T8** | 复合体 $\sigma_{\text{comp}}=\prod_i\sigma_i$，$Q$ 按新边界重算 | 对接 A2/A3 |

**关键词**：$\mathbb{Z}_2$ 上同调；holonomy；余边界；顶点势；边轨道；Aut-不变赋值；电荷符号通道；一阶贝蒂数

---

## 1 问题陈述

### 1.1 缺口

电荷涌现论文（§3–§4）给出：

- **量值通道** $\deg(K)=\beta_1(K)\bmod 2$（§5）；
- **符号通道** $\sigma(K)=\prod_{e\in\partial K}s_e\in\{+1,-1\}$（定义 D4），并声明 $\sigma\in H^1(G;\mathbb{Z}_2)$；
- **电荷泛函** $Q(K)=\sigma(K)\cdot\deg(K)\cdot e$（公理 A1）。

但该论文的符号通道**只在少量离散骨架上被抽样核验**，缺少：

1. **良定义性的严格论证**——$\prod_{e\in\partial K}s_e$ 是否真的只依赖 $K$ 的同调类（而非代表）；
2. **可复用实现**——如何把 $\sigma$ 落到任意分子键图上，并与电子算子共享同一张图；
3. **可达性的严格判据**——在何种条件下非平凡类可达（"电子/质子异号"的结构来源）。

### 1.2 本文任务

把 $\sigma$ 通道**单独**建基为算子 19：

- **输入**：算子 1/4 输出的 SRE 平滑邻接 $A_s$（键图支撑为 $A_s>0$）、电负性 $\chi$（自旋口径）、元素标号（分子着色）；
- **输出**：图不变量 $\{V,E,c,\beta_1,\deg,\text{bipartite},\text{has\_odd\_cycle}\}$、$\sigma$ 类 $\{\sigma\text{-vector},\sigma\text{-class},\text{trivial}\}$、Aut-不变可达性、以及模型内部电荷档 $Q_{\text{model}}=\sigma\cdot\deg$；
- **性质**：T0–T8（§5）。

---

## 2 数学预备

### 2.1 图作为 1-维链复形

设键图 $G=(V,E)$，$\lvert V\rvert =n$，$\lvert E\rvert =m$。SRE 体系**只在 1-维复形（图）上运行**——不存在 2-胞腔（面），故

$$Z_1=\ker\partial_1,\qquad B_1=\mathrm{im}\,\partial_2=0,\qquad H_1(G;\mathbb{F}_2)=Z_1/B_1=Z_1,\qquad \dim H_1=\beta_1=E-V+c,$$

其中 $c$ 为连通分支数。**关键**：因为没有 2-胞腔，$B_1=0$，$H_1$ 即为环空间本身（"环数 = 同调维数"，与算子 12 的 $n_{\text{loops}}=\beta_1$ 一致）。

对偶地，上链复形 $C^0\xrightarrow{\delta}C^1\xrightarrow{\delta}C^2$，因 $C^2=0$（无 2-胞腔），有 $Z^1=C^1$，$B^1=\delta C^0$，故

$$H^1(G;\mathbb{F}_2)=C^1/\,\delta C^0.$$

$\delta C^0$ 即**余边界**（顶点势型 1-上链）。配对 $H^1\times H_1\to\mathbb{F}_2$ 由 $\langle [s],[\gamma]\rangle=\sum_{e\in\gamma}z_e$ 给出。

### 2.2 极性—布尔同构

**引理 2.1（极性—布尔同构）**　映射 $\varphi:\{+1,-1\}\to\mathbb{F}_2$，$\varphi(S)\equiv\frac{1-S}{2}$（$-1\mapsto1,\ +1\mapsto0$），是群同构 $(\{+1,-1\},\cdot)\cong(\mathbb{F}_2,\oplus)$。

**证明**　双射显然。核验同态性：$\varphi(S_1S_2)=1$ 当且仅当恰有一个 $S_k=-1$，与 $\varphi(S_1)\oplus\varphi(S_2)$ 一致；四个输入组合逐一核验成立。$\square$

故「极性相乘」与「模 2 相加」严格一一对应，本文后续在 $\mathbb{F}_2$ 中运算（记 $z_e\equiv\varphi(s_e)$）。

### 2.3 SRE 公理 1 的二元性

SRE 公理 1（无零元）保证每条边只能取 $s_e\in\{+1,-1\}$，即 $z_e\in\mathbb{F}_2$ 无"缺省/未定义"态。**这是算子 19 能定义在边的全空间 $C^1$ 上的前提**（不依赖边的"存在与否"）。

---

## 3 定义

**D1（键图 $G$）**　由 $A_s$ 的支撑给出：$G=(V,E)$，$E=\{(i,j):A_s{}_{ij}>0,\,i<j\}$。（对应 SRE 公理 1 的协同边 $E^+$。）

**D2（边极性 1-上链 $s$）**　$s:E\to\{+1,-1\}$，$z_e\equiv\varphi(s_e)\in\mathbb{F}_2$；$s\in C^1(G;\mathbb{F}_2)$。

**D3（字面口径 / 顶点势口径）**　
- **字面口径**（电荷涌现论文 A1）：协同边一律 $s_e=+1$（拓扑全正）；
- **自旋口径**（算子 11 诊断量）：$s_e=s_i\cdot s_j$，$s_i=\operatorname{sign}(\chi_i-\bar\chi)$。

**D4（环 holonomy）**　对环 $\gamma$(顶点序列 $v_0v_1\cdots v_{L-1}v_0$)：$\sigma(\gamma)\equiv\prod_{k}s_{(v_k,v_{k+1})}$，等价地 $\sigma(\gamma)=\big(\sum_{e\in\gamma}z_e\big)\bmod 2$。

**D5（基本环基）**　取 $G$ 的生成森林（BFS parent），每条非树边 $(u,v)$ 配以树上路径 $u\leadsto v$ 构成基本环 $\gamma_i$，$i=1,\dots,\beta_1$。$\{\gamma_i\}$ 是 $H_1$ 的一组基。

**D6（$\sigma$ 类 / 平凡性）**　$[s]=s+\delta C^0\in H^1$。称 $[s]$ **平凡**（$[s]=0$）当且仅当 $s\in\delta C^0$（即存在顶点势 $t\in\{\pm1\}^V$ 使 $s_e=t_it_j$），等价于**基本环基上全体 $\sigma(\gamma_i)=+1$**。$\sigma_{\text{canonical}}\equiv+1$(平凡)$/-1$(非平凡)。

**D7（量值通道 $\deg$）**　$\deg(K)\equiv\beta_1(K)\bmod 2$。（不依赖 $s$。）

**D8（模型内部电荷档 $Q_{\text{model}}$）**　$Q_{\text{model}}\equiv\sigma_{\text{canonical}}\cdot\deg\in\{-1,0,+1\}$（$e$ 归一为 1）。

**D9（Aut-不变赋值）**　设自同构群 $\operatorname{Aut}(G)$（分子场景为**保元素**自同构，见 T7）作用于 $E$，把 $E$ 分成边轨道 $\{O_1,\dots,O_k\}$。称 $s$ 为 **Aut-不变**，若 $s$ 在每条轨道上取常值。

**D10（通道类型）**　
- **electron-like（强制平凡）**：Aut-不变赋值下**所有** $s$ 都平凡；
- **nucleon-like（允许非平凡）**：$\exists$ Aut-不变 $s$ 非平凡。

---

## 4 公理（承接电荷涌现论文）

**A1（电荷泛函）**　$Q=\sigma\cdot\deg\cdot e$，$\sigma\in H^1(G;\mathbb{F}_2)$。
**A2（复合重算）**　复合纽结 $K_{\text{comp}}$ 的 $\sigma_{\text{comp}}=\prod_i\sigma_i$（$\mathbb{F}_2$ 加法），$\deg_{\text{comp}}=\beta_1(K_{\text{comp}})\bmod2$。
**A3（分离可加）**　独立纽结 $Q_{\text{tot}}=\sum_i Q(K_i)$。
**A0（符号基准）**　规定电子所在 holonomy 类为"负"（规范约定）。

**算子 19 的口径声明**：算子 19 实现 $\sigma$ 通道与 $\deg$ 通道，输出 $Q_{\text{model}}$ 作为**模型内部电荷档**；A0 的"负"基准由 $\sigma_{\text{canonical}}=-1$ 承载。

---

## 5 核心定理与证明

> 以下定理均在**图（1-维复形）**上陈述，$c$ 为连通分支数，$\beta_1=E-V+c$。

### T0（良定义性：$\sigma$ 是 $H_1$ 上的 $\mathbb{F}_2$-线性泛函）

**陈述**　在无 2-胞腔的图上，$B_1=0$，故 $H_1=Z_1$；映射 $\sigma:Z_1\to\mathbb{F}_2$，$\gamma\mapsto\sum_{e\in\gamma}z_e$ 是线性泛函，只依赖 $\gamma$ 的链本身。

**证明**　$\partial_2=0\Rightarrow B_1=0\Rightarrow H_1=Z_1$，环即同调类，故 $\sigma$ 无"代表歧义"问题。线性性：设 $\gamma_1,\gamma_2\in Z_1$，$\sigma(\gamma_1+\gamma_2)=\sum_{e\in\gamma_1\triangle\gamma_2}z_e=\sigma(\gamma_1)+\sigma(\gamma_2)\ (\mathrm{mod}\,2)$，因公共边在对称差中出现两次、模 2 抵消。$\blacksquare$

**注**　这是算子 19 相对通用图论更简洁的一处：分子键图没有填充环的"面"，因此电荷涌现论文中"$\sigma\in H^1$"的声明在图层面**自动成立**，无需额外的 2-胞腔结构。

### T1（顶点势平凡定理）

**陈述**　设 $s_e=t_i\cdot t_j$（$t\in\{\pm1\}^V$，即 $s=\delta$-型顶点势），则对**任意**闭链 $\gamma$ 有 $\sigma(\gamma)=+1$；即 $[s]=0$。

**证明**　
$$\sigma(\gamma)=\prod_{(i,j)\in\gamma}s_i s_j=\prod_{v\in\gamma}t_v^{\,\deg_\gamma(v)},$$
其中 $\deg_\gamma(v)$ 为 $v$ 在闭链 $\gamma$ 中被关联的边数（入+出）。闭链满足各顶点出入守恒，$\deg_\gamma(v)$ 为**偶数**，故 $t_v^{\deg_\gamma(v)}=+1$，连乘得 $\sigma(\gamma)=+1$。$\blacksquare$

**推论 T1.1（电荷符号不可由局部自旋重标定涌现）**　算子 11 的自旋极性 $s_e=s_i s_j$ **正是**顶点势型；由 T1 其 holonomy 恒平凡。因此：

> **电荷的符号通道 $\sigma$ 必须来自真正的非余边界上链 $[s]\neq0\in H^1$，不能由顶点的局部自旋重标定造出。**

这解释了为什么「单纯给顶点赋自旋符号」不足以产生净电荷符号——它落在 $H^1$ 的平凡类里。

### T2（Aut-不变可达性的 $\mathbb{Z}_2$ 线性判据）

**陈述**　设 $\operatorname{Aut}(G)$ 的边轨道为 $O_1,\dots,O_k$，Aut-不变赋值在轨道 $o$ 上取值 $z_o\in\mathbb{F}_2$。定义

$$m_{i,o}\equiv\#\{e\in O_o\cap\gamma_i\}\bmod2\in\mathbb{F}_2,\qquad M=(m_{i,o})\in\mathbb{F}_2^{\beta_1\times k}.$$

则 $\sigma(\gamma_i)=\bigoplus_{o}m_{i,o}z_o$，且

$$\boxed{\ \text{非平凡类可达}\iff \exists\,i,o:\ m_{i,o}=1\iff M\neq 0\ }$$

**证明**　由 T0 的线性性，$\sigma(\gamma_i)=\sum_{e\in\gamma_i}z_e=\sum_o z_o\cdot\#(O_o\cap\gamma_i)=\bigoplus_o m_{i,o}z_o$，即 $M$ 给出的线性映射 $T:\mathbb{F}_2^k\to\mathbb{F}_2^{\beta_1}$，$z\mapsto Mz$。
- （$\Leftarrow$）若 $\exists m_{i,o}=1$，取 $z=e_o$（仅 $z_o=1$），则 $\sigma(\gamma_i)=m_{i,o}=1\neq0$，非平凡可达（平凡类 $z=0$ 恒可达）。
- （$\Rightarrow$）若 $M=0$，则 $\forall z$，$Mz=0$，全部环 holonomy 恒为 $+1$，无任何非平凡类可达。
故可达性等价于 $M\neq0$，即只需在 $M$ 中**找到任一非零元**，复杂度 $\mathcal{O}(\beta_1\cdot k)$，**不做** $2^k$ 字典序枚举。$\blacksquare$

**推论 T2.1**　平凡类**恒可达**（取全零赋值 $s_e\equiv+1$）。非平凡类可达**当且仅当**存在某条边轨道在某个基本环上出现奇数次。

### T3（环基选取无关性）

**陈述**　$\sigma$ 的平凡性判别（$[s]=0$）与基本环基 $\{\gamma_i\}$ 的选取无关。

**证明**　任取两组基本环基 $\{\gamma_i\},\{\gamma'_j\}$，它们都是 $H_1=Z_1$ 的基，故 $\gamma'_j=\sum_i a_{ji}\gamma_i$（$a_{ji}\in\mathbb{F}_2$）。由 T0 线性性 $\sigma(\gamma'_j)=\bigoplus_i a_{ji}\sigma(\gamma_i)$。因此「在一组基上全为 0」等价于「在另一组基上全为 0」，平凡性判别唯一。$\blacksquare$

### T4（余边界规范不变性 / 上同调类是规范不变量）

**陈述**　设 $s'=s\cdot\delta t$（即 $s'_e=s_e\,t_it_j$，$t\in\{\pm1\}^V$）。则 $\forall\gamma:\sigma'(\gamma)=\sigma(\gamma)$；故 $\sigma$ 只依赖 $[s]\in H^1$。

**证明**　$\sigma'(\gamma)=\big(\prod_{e\in\gamma}s_e\big)\cdot\big(\prod_{e\in\gamma}t_it_j\big)=\sigma(\gamma)\cdot1$，末因子由 T1 恒为 $+1$。$\blacksquare$

**推论 T4.1**　$H^1=C^1/\delta C^0$ 的商结构正对应"$\sigma$ 对顶点势重标定免疫"；规范自由度为 $\delta C^0$（顶点势）。

### T5（双通道正交独立）

**陈述**　$\deg=\beta_1\bmod2$ 只由 $(V,E,c)$ 决定，不依赖 $s$；$\sigma$ 只由 $[s]$ 决定，不依赖 $(V,E,c)$ 的具体数值（只依赖图的**轨道结构**与 $[s]$）。二者自变量不相交，故独立取值。

**证明**　$\deg$ 是图拓扑函数（$\beta_1=E-V+c$）；$\sigma$ 是上同调类函数。取不同的 $s,s'$ 可保持 $\deg$ 不变而改变 $\sigma$，取不同的图（$\deg$ 变化）可保持 $\sigma$ 结构不变。故 $Q=\sigma\cdot\deg$ 的确由两个独立通道相乘得到。$\blacksquare$

### T6（偶环强制平凡：电子型的结构来源）

**陈述**　若 $G$ **二分**（无奇环）且**只有 1 条边轨道**，则一切 Aut-不变赋值都平凡（electron-like）。

**证明**　单轨道 $\Rightarrow s$ 为常数 $z$（$\mathbb{F}_2$）。二分 $\Rightarrow$ 所有环 $\gamma$ 长度 $\lvert \gamma\rvert$ 为偶。故 $\sigma(\gamma)=z^{\lvert \gamma\rvert }=(z)^{even}=+1$，平凡。$\blacksquare$

**对照**（与电荷涌现论文 §10.2 一致）：
- 电子 $Q_3$（立方体图）：二分、单边轨道 $\Rightarrow$ **强制平凡**（$[s]=0$）；
- 质子 $Y_3\ltimes\triangle_3$（闭态）：**非二分**（含奇环）、2 条边轨道 $\Rightarrow$ 允许非平凡。

### T7（元素着色必要性）

**陈述**　分子场景的自同构**必须保元素标号**（保色 Aut）。用不保色 Aut 会合并本应区分的边轨道，使可达性判据失真，**可致判据翻转**。

**证明（反例）**　取 4-环 $v_0v_1v_2v_3v_0$，元素为 $[O,C,C,O]$（$v_0{=}O,v_1{=}C,v_2{=}C,v_3{=}O$），边 $e_1{=}(0,1),e_2{=}(1,2),e_3{=}(2,3),e_4{=}(3,0)$。
- **保色 Aut**：交换 $v_0\leftrightarrow v_3$、$v_1\leftrightarrow v_2$ 保持元素。轨道：$O_1=\{e_1,e_3\}$、$O_2=\{e_2\}$、$O_3=\{e_4\}$（3 条轨道）。唯一环 $\gamma$ 上：$m_{\gamma,O_1}=2\equiv0$，$m_{\gamma,O_2}=1$，$m_{\gamma,O_3}=1$，故 $M\neq0$ $\Rightarrow$ **非平凡可达**。
- **不保色 Aut**：$D_4$ 在 4 条边上**传递**（1 条轨道）。环 $\gamma$ 长 4 偶，$\sigma=z^{4}=+1$ $\Rightarrow$ **强制平凡**。

两口径给出**相反的通道判据**，故元素着色是分子层分析的必要条件。$\blacksquare$

**实现要求**　`automorphisms(adj, colors=elements)` 必须以 `node_match`（按元素标号）限制自同构；`elements=None` 时退化为不保色，仅可用于抽象图实验。

### T8（复合与可加：对接 A2/A3）

**陈述**　对由 $n$ 个纽结相干合并的复合体 $K_{\text{comp}}$：$\sigma_{\text{comp}}=\prod_i\sigma_i$（$\mathbb{F}_2$ 加法），$\deg_{\text{comp}}=\beta_1(K_{\text{comp}})\bmod2$，$Q_{\text{comp}}=\sigma_{\text{comp}}\deg_{\text{comp}}$。

**证明**　复合体重算新边界（A2），边界为各 $\partial K_i$ 之对称差；由 T0 线性性 $\sigma$ 沿对称差相加 $\Rightarrow$ 极性相乘（引理 2.1）。$\deg$ 按新 $(V,E,c)$ 重算。分离可加（A3）由 $Q$ 对独立成分求和给出。$\blacksquare$

---

## 6 与上游电荷涌现论文的对接（官方骨架忠实复现）

算子 19 以 `skel_electron_q3 / skel_y3_closed / skel_y3_open` 忠实复现电荷涌现论文 §10.2 三类骨架，作为规范的**锚点自测**：

| 骨架 | $V$ | $E$ | $\beta_1$ | $\deg$ | $\lvert\operatorname{Aut}\rvert$ | 边轨道 | 二分 | 非平凡可达 | 通道类型 |
|---|---|---|---|---|---|---|---|---|---|
| 电子 $e^-$ ($Q_3$) | 8 | 12 | 5 | 1 | 48 | 1 | 是 | **否** | electron-like |
| 质子 $p$（闭态） | 12 | 18 | 7 | 1 | 36 | 2 | 否 | **是** | nucleon-like |
| 中子 $n$（开态） | 12 | 17 | 6 | 0 | 4 | 7 | 否 | **是** | nucleon-like |

结论：**电子被骨架对称性强制到平凡 holonomy 类，质子落在非平凡类**，与 A0 一起给出电子/质子异号的结构来源。中子的 $\deg=0$，无论 $\sigma$ 如何 $Q_{\text{model}}=0$——**量值通道单独使中子中性**。

---

## 7 算法与复杂度

| 步骤 | 输入 | 输出 | 复杂度 |
|---|---|---|---|
| 1 键图 | $A_s$ | 布尔邻接 $\mathrm{adj}$ | $\mathcal{O}(n^2)$ |
| 2 图不变量 | $\mathrm{adj}$ | $V,E,c,\beta_1,\deg,\text{bipartite}$ | $\mathcal{O}(n^2)$ |
| 3 基本环基 | $\mathrm{adj}$ | $\{\gamma_i\}_{i\le\beta_1}$ | $\mathcal{O}(n^2+E\cdot L)$ |
| 4 环 holonomy | $\{\gamma_i\},s$ | $\sigma$-vector、trivial | $\mathcal{O}(\sum_i\lvert \gamma_i\rvert )$ |
| 5 自同构（可选） | $\mathrm{adj},\text{colors}$ | $E$ 的轨道 | 受 `aut_cap`/`aut_max_v` 守卫（缺省 $V\le22$，否则跳过） |
| 6 可达性（可选） | $\{\gamma_i\},\{\text{轨道}\}$ | $M$、非平凡可达、见证 | $\mathcal{O}(\beta_1\cdot k)$ |

**总复杂度**：$\mathcal{O}(n^2 + \beta_1\cdot\bar L)$（不含自同构枚举）；自同构枚举为瓶颈，故设守卫 `aut_max_v=22`，超限仅跳过可达性而**不影响** $\sigma$ 类判别与 $Q_{\text{model}}$。

---

## 8 验证协议（Verification Protocol）

配套验证程序 `verify_operator_19.py` 逐条实现下列断言；运行全部通过即实证本规范全部定理。

### 8.1 验证程序 ↔ 定理映射表

| 验证项 | 对应定理 | 体系 | 断言 |
|---|---|---|---|
| **V1** 骨架忠实性 | §6 / 电荷涌现 §10.2 | $Q_3,Y_3$闭,$Y_3$开 | $V,E,\beta_1,\deg,\lvert\operatorname{Aut}\rvert$,边轨道,二分,非平凡可达逐项一致 |
| **V2** 顶点势平凡 | T1, T1.1 | 40 例随机图 + $Q_3$ | 自旋极性 $s_e=s_is_j$ 的 holonomy 全为 $+1$ |
| **V3** 可达性判据 | T2, T2.1 | 30 例随机小图 | 线性判据 $=$ $2^{k}$ 暴力枚举；平凡类恒可达 |
| **V4** 环基无关性 | T3 | 随机图（两种生成森林根） | 平凡性判别与 $\sigma_{\text{canonical}}$ 一致 |
| **V5** 余边界规范不变 | T4, T4.1 | 随机图 + 随机顶点势 | $\sigma'(\gamma)=\sigma(\gamma)$ 对所有环成立 |
| **V6** $\deg$ 通道 | D7, T5 | 骨架 + 随机图 | $\deg=\beta_1\bmod2$ |
| **V7** 电荷泛函一致 | D8, T5 | 骨架 + 分子 | $Q_{\text{model}}=\sigma_{\text{canonical}}\cdot\deg$ 且 $\in\{-1,0,1\}$ |
| **V8** 元素着色必要性 | T7 | 反例 4-环 $[O,C,C,O]$ | 保色判据"非平凡"、不保色判据"平凡"（判据翻转） |
| **V9** 端到端入口 | §1.2, §6 | 乙醇（树）、苯（偶环）、环戊烷（奇环） | 树/偶环 $\to$ electron-like；奇环+多轨道 $\to$ nucleon-like |
| **V10** 幂等与冻结契约 | D5, §6 | 指纹键 + `attach` 守卫 | `charge_channel_keys` 两次调用逐键相等；已含 `z2_deg` 的指纹再 attach 不重复计入 |
| **V11** 图不变量自洽 | §7 | 骨架 + 随机图 | $\beta_1=E-V+c$；`has_odd_cycle` 与 bipartite 互补 |
| **V12** 分子层判据 | T6, T7 | 6 个分子键图 | 偶环族 electron-like；奇环族 nucleon-like |

### 8.2 运行

```
python verify_operator_19.py
```
零外部依赖（仅 numpy + networkx，networkx 仅用于自同构枚举）；任一行断言失败以退出码 1 结束。

---

## 9 与既有算子（1–18）的边界（不重合声明）

算子 19 已逐条对照 `SRE-math_C.md` 全部 18 个算子，**无重合**：

| 邻近算子 | 其职责 | 与算子 19 的边界 |
|---|---|---|
| **算子 12**（拓扑闭合环审计） | 输出 $n_{\text{loops}}=\beta_1$、Möbius 相位比 $t_{2k}/(2t_k)$（**谱启发式**） | 12 给**环的计数**（量值）；19 给**边极性上链的上同调类** $\sigma$（符号）。12 的 mobius_ratio **没有环、没有边极性、也没有类**，**不是**严格 $\mathbb{Z}_2$ holonomy；19 才是其严格化 |
| **算子 14**（方程残差 Hodge 路由） | 把残差 1-链分解为 $\mathrm{im}\,\partial_1\oplus\mathcal{H}_1\oplus\mathrm{im}\,\partial_2^{T}$ | 14 在 **1-链空间** $C_1$ 上做正交分解；19 在 **1-上链空间** $C^1$ 上取上同调类。二者互为 Hodge 对偶：14 的梯度分量 $\mathrm{im}\,\partial_1$ 的对偶正是 T1 的**余边界**平凡类 |
| **算子 7**（$B_{co}$ 环流对冲） | 动力学：环流 $B$ 场蛙跳对冲 | 7 是**动力学**（循环流更新）；19 是**静态不变量**（给定 $s$ 的分类） |
| **算子 9 / 17**（贝蒂审计 / 终止裁定） | 改变或审计**拓扑** $\beta_1$ | 9/17 改变或审计量值通道；19 在**固定拓扑**上给符号通道 |
| **算子 18**（同调解实现） | step 5 用 Fiedler 符号门赋自旋 $\Gamma(k,j)=\operatorname{sgn}(v_2(j))$ | 18 的自旋赋型属**顶点势型**，由 **T1** 其 holonomy 恒平凡；19 证明"18 的赋型无法产生非平凡符号通道"，构成握手边界 |
| **算子 11**（自旋-电荷邻接） | 输出诊断量 $s_i,\sigma_{ij},d_{ij}$ | 11 的 $\sigma_{ij}=s_is_j$ **恰是** T1 的平凡类样例；19 把它定位为"不可造符号" |

**层级定位**：开源底座层（1–6）、开源核心层（7–10）、电子自由度扩展层（11–12）、谱形方程求解层（13–18）之后的**第五层——电荷符号 / $\mathbb{Z}_2$ holonomy 通道层（19）**。

---

## 10 诚实边界与适用域

1. **模型内部构造，非物理断言**。本规范全部结论为 SRE 模型**内部自洽构造**；$Q_{\text{model}}$ 是**模型内部电荷档**（$\in\{-1,0,+1\}$），不构成对现实分子/粒子电荷数值的物理断言。
2. **Aut-不变是明示假设**。可达性结论（T2、T6）依赖电荷涌现论文 §13.2 的**明示假设**"边极性在自同构下不变"。**不加此假设**时，任何含环的图都容许非平凡类（1 bit 自由度，维数 $=\beta_1$），可达性分析退化为平凡事实。
3. **非平凡可达的必要条件**。仅当图含**奇环**且边轨道数 $\ge2$（更准确：$M\neq0$）时，非平凡类才可达——这是"偶数环族被偶长强制平凡"（T6）的直接后果。
4. **分子层需元素着色**。分子键图的 Aut 必须以元素标号着色（T7），否则 C 与 H 等异元素可能被混同，轨道结构失真。
5. **规模守卫**。自同构枚举设 `aut_max_v=22` 守卫；超大图仅跳过可达性分析，$\sigma$ 类判别与 $Q_{\text{model}}$ 仍有效。
6. **$A_s$ 语义**。19 复用算子 1/4 输出的 $A_s$，其键图支撑 $A_s>0$ 的语义由上游保证（SRE 公理 1 的协同边 $E^+$）；若上游 $A_s$ 含数值噪声，请以 `bond_graph_from_As(eps)` 的 $\epsilon$ 判定。

---

## 11 结论

算子 19 把电荷涌现论文的 $\sigma$ **符号通道**单独实现、单独建基：

- **良定义**（T0）：1-复形上 $\sigma$ 是 $H_1$ 上的 $\mathbb{F}_2$-线性泛函，无代表歧义；
- **符号的不可伪造性**（T1/T1.1）：顶点势型极性（含算子 11 自旋极性、算子 18 符号赋型）holonomy 恒平凡——电荷符号不能由局部自旋重标定造出；
- **可达性的封闭判据**（T2/T2.1）：非平凡可达 $\iff M\neq0$，$\mathcal{O}(\beta_1 k)$，无需 $2^k$ 枚举；
- **规范不变性**（T3/T4）：平凡性判别与环基无关，$\sigma$ 对顶点势重标定免疫，只依赖 $[s]\in H^1$；
- **双通道分离**（T5）：符号 $\sigma$ 与量值 $\deg$ 正交，$Q=\sigma\deg$；
- **电子型/核子型的结构来源**（T6）：偶环 + 单轨道强制平凡（电子），奇环 + 多轨道允许非平凡（质子）；
- **分子层的必要形成分**（T7）：元素着色 Aut，否则判据翻转。

并与上游电子算子共享同一张图（$A_s$），输出 `z2_*` 标量键接入化合物筛选流水线，实现原子/电子级的高速符号通道计算。

---

## 附录 A：符号与记号

| 记号 | 含义 |
|---|---|
| $G=(V,E)$ | 键图（1-维链复形），$V$ 顶点、$E$ 边 |
| $c$ | 连通分支数 |
| $\beta_1=E-V+c$ | 一阶贝蒂数 $=\dim H_1$ |
| $s_e\in\{+1,-1\}$ | 边极性（1-上链） |
| $z_e=\varphi(s_e)\in\mathbb{F}_2$ | 极性布尔化 |
| $\sigma(\gamma)=\prod_{e\in\gamma}s_e$ | 环 holonomy |
| $[s]\in H^1(G;\mathbb{F}_2)$ | $\sigma$ 的上同调类 |
| $\delta C^0$ | 余边界（顶点势型上链） |
| $O_o$ | Aut 作用下的边轨道 |
| $m_{i,o}$ | 轨道 $o$ 在基本环 $i$ 上的边数 mod 2 |
| $M=(m_{i,o})$ | 可达性矩阵，非平凡可达 $\iff M\neq0$ |
| $\deg=\beta_1\bmod2$ | 量值通道 |
| $Q_{\text{model}}=\sigma_{\text{canonical}}\cdot\deg$ | 模型内部电荷档 |