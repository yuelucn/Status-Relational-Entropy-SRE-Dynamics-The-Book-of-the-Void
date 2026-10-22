# 算子 19：ℤ₂ holonomy / σ 电荷符号通道算子
## 严格数学规范、可解性推理依据、双 ℤ₂ 通道判决与验证协议

**版本**：1.2（2026 年 10 月 · SRE 算子体系第 19 号；v1.1 增补极性注入与跨实现验证，v1.2 增补割空间充要判据、Pfaffian / $H^1$ 双通道并置判决与梯族编号口径对照）
**参考实现**：功能式桥接 `sre_z2_holonomy_bridge.py`（入口 `operator_19_z2_charge_channel`）；类式发布套件 `sre_charge_channel.py`（`SREChargeChannelSuite.execute_operator_19_z2_charge_channel`；三份镜像 SHA-256 一致）——双实现互证无歧义
**配套验证程序**：三份独立程序共同实证本规范
  - `verify_operator_19.py`（V1–V12，骨架忠实 / 定理逐项 / 冻结契约，45 断言）
  - `verify_operator_19_mobius.py`（M1–M9，Möbius 型图专项，57 断言）
  - `verify_operator_19_cross.py`（X1–X10，跨实现一致性 + 守卫边界，29 断言）
**前置依赖**：算子 1/4（SRE 平滑邻接 $A_s$ 的键图支撑）、算子 11（自旋极性诊断量 $s_i,\sigma_{ij}$）、算子 12（一阶贝蒂数 $\beta_1$ 环计数）
**上游论文**：《SRE 体系下正负电荷的涌现：量值、符号与数值确证》（下称"电荷涌现论文"）
**下游集成**：`sre_cluster_substitute_screen.py`（`z2_*` 字段接入化合物筛选流水线）
**编号说明**：算子在既有 18 号之后接续编号为 **19**；已逐条核验与 `SRE-math_C.md` 全部 18 个算子**无重合**（边界见 §9）。
**外部判决报告（v1.2 引用）**：《核子骨架 $Y_3$ 的双 $\mathbb{Z}_2$ 通道判决：割空间充要判据在项目自身对象上的落地、与莫比乌斯梯族的关系及 Pfaffian 障碍的可读证书》（第 104 轮，下称"$Y_3$ 判决报告"）。本版 T9、T10、T11、§6.2、§6.3 的实测数值与证书均源于该报告；其中割空间恒等式已在本项目内独立复核（§8.4）。

---

## 摘要

SRE 动力学把电荷表述为「拓扑纽结的计数」。计数天然非负，只给出电荷的**量值**，无法给出**符号**。电荷涌现论文补全该缺口，提出电荷泛函

$$Q(K)=\sigma(K)\cdot\deg(K)\cdot e,\qquad \deg(K)=\beta_1(K)\bmod 2,\qquad \sigma(K)\in H^1(G;\mathbb{Z}_2).$$

其中「符号通道」$\sigma$ 被声明为一条 **$\mathbb{Z}_2$ 卷绕相位（holonomy）** 上同调类，但该论文以一个**独立数值脚本**（`_se_assignment_test.py`）在少数骨架与分子上做了抽样验证，**并未给出该算子的独立、可复用、可证明的实现规范**。本文把 $\sigma$ 通道**单独**实现为 **算子 19**，并给出三项此前缺失的内容：

1. **严格的推理依据**（§2–§5）：在分子键图的 **1-维链复形** 上，把「边极性 $\to$ 环 holonomy $\to$ 上同调类」的链路严格化，证明算子输出的良定义性，并给出**全部定理与证明**（T0–T11）。
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
| **T9** | $\operatorname{rank}_{\rm hol}=n_{\rm orb}-\dim\big(W(G)\cap\operatorname{Cut}(G)\big)$ | **平凡性的充要判据**（T2 的维数深化） |
| **T10** | $Y_3^{\rm cl}$ 的 Pfaffian 无解有**极小不可解证书**（6 行全用即矛盾，差 1 行） | 判负可核查 |
| **T11** | 梯族 $\operatorname{rank}_{\rm hol}=0\iff k=3$（$K_{3,3}$） | 奇环**不是**通道开闭的判据 |

**v1.2 新增（全部经 $Y_3$ 判决报告门 A–F 与本项目内复核）**：

1. **T9（割空间恒等式）**　把 T2 的「存在非平凡类」判据深化为**维数恒等式**：可达（Aut-不变）类数恰为 $2^{\operatorname{rank}_{\rm hol}}$；三个官方骨架读数为 $Q_3=0$、$Y_3^{\rm cl}=1$、$Y_3^{\rm op}=2$（§6 表 6.2）。
2. **§6.2 双 $\mathbb{Z}_2$ 通道并置判决**　在同一个 $Y_3^{\rm cl}$ 上，$H^1$ 通道**打开**（1 比特）而 **Pfaffian 通道一个定向都不存在**，并给出可读证书（6 行极小不可解）与机制（42 条 nice even cycle 在开态归零）。
3. **§6.3 覆盖判决与编号口径**　$Y_3^{\rm cl}$ 与 $M_{2n}(n\ge3)$ **零覆盖、零商**，但恰是 $K_4\cong M_4$ 的**三折正规覆盖**；并建立书内 $M_k$ 与论文 $M_{2n}$ 的因子 2 对照表（表 6.5）。
4. **对 v1.1 的纠正**　v1.1 §10 第 3 条「非平凡可达**仅当**含奇环且轨道数 $\ge2$」**已被证伪**：梯族 $k\ge5$ 奇为二分图（无奇环）却仍有 $\operatorname{rank}_{\rm hol}\ge1$；正确判据是 T9 的 $W\not\subseteq\operatorname{Cut}$。相应地，§6.1 原句「真正决定翻转的是奇环存在性」亦已修正。

**关键词**：$\mathbb{Z}_2$ 上同调；holonomy；余边界；割空间；边轨道；Aut-不变赋值；电荷符号通道；Pfaffian 定向；一阶贝蒂数

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

- **输入**：算子 1/4 输出的 SRE 平滑邻接 $A_s$（键图支撑为 $A_s>0$）；可选极性口径四选一（D3）——缺省 `polarity="topo"`，或显式 `edge_polarity` / 轨道 `orbit_signs` / 自旋 `chi`；可选元素标号（分子着色，保色 Aut）；可选守卫参数 `aut_cap`（缺省 100 000）与 `aut_max_v`（缺省 22，超限仅跳过可达性）。
- **输出**：图不变量 $\{V,E,c,\beta_1,\deg,\text{bipartite},\text{has\_odd\_cycle}\}$、$\sigma$ 类 $\{\sigma\text{-vector},\sigma\text{-class},\text{trivial}\}$、Aut-不变可达性、以及模型内部电荷档 $Q_{\text{model}}=\sigma\cdot\deg$；
- **性质**：T0–T11（§5）。其中 T9 给出符号通道的比特数（割空间充要判据），T10/T11 与 §6.2/§6.3 给出双 $\mathbb{Z}_2$ 通道并置判决与梯族编号口径（v1.2 新增；后者不改变输入输出与冻结契约）。

---

## 2 数学预备

### 2.1 图作为 1-维链复形

设键图 $G=(V,E)$，$|V|=n$，$|E|=m$。SRE 体系**只在 1-维复形（图）上运行**——不存在 2-胞腔（面），故

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

**D3（四种边极性口径 / 注入优先级）**　
算子 19 支持四种**互斥**的边极性来源，按优先级排序：

1. **explicit 显式注入**（`polarity="explicit"` + `edge_polarity=spec`）：外部字典 `{(i,j):±1}` 或长度 $E$ 的序列，必须覆盖全部边且取值仅 $\pm1$。最灵活的调试/实验口径。
2. **orbit 轨道注入**（`polarity="orbit"` + `orbit_signs=[±1,\dots]`）：每条边轨道整体取同一符号，**构造上即 Aut-不变**（对接电荷涌现 §13.2 的明示假设）。长度必须等于边轨道数，且要求 $V\le\text{aut\_max\_v}$。
3. **spin 自旋口径**（`polarity="spin"` + `chi=\chi`）：$s_e=s_i\cdot s_j$，$s_i=\operatorname{sign}(\chi_i-\bar\chi)$。由 T1 其 holonomy **恒平凡**，故该口径可用来演示"顶点势型无法产生非平凡符号通道"。
4. **topo 字面口径**（`polarity="topo"`，缺省）：协同边一律 $s_e=+1$（电荷涌现论文 A1 的字面声明）。

同时提供多注入口径（如 `edge_polarity` 与 `orbit_signs` 同给）或非法取值会抛出 `ValueError`，两类实现共享同一校验契约（见 §8.3 / X8）。

**D4（环 holonomy）**　对环 $\gamma$(顶点序列 $v_0v_1\cdots v_{L-1}v_0$)：$\sigma(\gamma)\equiv\prod_{k}s_{(v_k,v_{k+1})}$，等价地 $\sigma(\gamma)=\big(\sum_{e\in\gamma}z_e\big)\bmod 2$。

**D5（基本环基）**　取 $G$ 的生成森林（BFS parent），每条非树边 $(u,v)$ 配以树上路径 $u\leadsto v$ 构成基本环 $\gamma_i$，$i=1,\dots,\beta_1$。$\{\gamma_i\}$ 是 $H_1$ 的一组基。

**D6（$\sigma$ 类 / 平凡性）**　$[s]=s+\delta C^0\in H^1$。称 $[s]$ **平凡**（$[s]=0$）当且仅当 $s\in\delta C^0$（即存在顶点势 $t\in\{\pm1\}^V$ 使 $s_e=t_it_j$），等价于**基本环基上全体 $\sigma(\gamma_i)=+1$**。$\sigma_{\text{canonical}}\equiv+1$(平凡)$/-1$(非平凡)。

**D7（量值通道 $\deg$）**　$\deg(K)\equiv\beta_1(K)\bmod 2$。（不依赖 $s$。）

**D8（模型内部电荷档 $Q_{\text{model}}$）**　$Q_{\text{model}}\equiv\sigma_{\text{canonical}}\cdot\deg\in\{-1,0,+1\}$（$e$ 归一为 1）。

**D9（Aut-不变赋值）**　设自同构群 $\operatorname{Aut}(G)$（分子场景为**保元素**自同构，见 T7）作用于 $E$，把 $E$ 分成边轨道 $\{O_1,\dots,O_k\}$。称 $s$ 为 **Aut-不变**，若 $s$ 在每条轨道上取常值。

**D10（通道类型）**　
- **electron-like（强制平凡）**：Aut-不变赋值下**所有** $s$ 都平凡；
- **nucleon-like（允许非平凡）**：$\exists$ Aut-不变 $s$ 非平凡。

**D11（Aut-不变赋值空间 $W(G)$，v1.2 新增）**　设边轨道为 $O_1,\dots,O_k$，
$$W(G)\equiv\operatorname{span}_{\mathbb{F}_2}\{\mathbf 1_{O_1},\dots,\mathbf 1_{O_k}\}\subseteq C^1(G;\mathbb{F}_2),\qquad \dim W(G)=n_{\rm orb}=k .$$
$W(G)$ 是"全体 Aut-不变赋值"构成的子空间。**对照**：不加 Aut 约束时赋值空间为整个 $C^1$（维 $m$），此时非平凡类是常态（维 $\beta_1$，见 §10 第 2 条）。

**D12（割空间 $\operatorname{Cut}(G)$，v1.2 新增）**　
$$\operatorname{Cut}(G)\equiv\{d(S):S\subseteq V\}=\operatorname{im}\delta_0=\delta C^0\subseteq C^1(G;\mathbb{F}_2),\qquad \dim\operatorname{Cut}(G)=n-c ,$$
其中 $d(S)$ 为恰有一个端点在 $S$ 中的边集。**基取星集** $d(\{v\})$（与 $v$ 关联的全部边）。**陷阱提示**：若误把基取为"生成树上 $v\to$ 根的路径边集"，得到的是 **循环空间**（tree-cotree 分解中的 tree），不是割空间——$Y_3$ 判决报告实测该替换在 996 例中造成 566 例失配（见 §8.4 门 B′）。

**D13（holonomy 秩与可达类数，v1.2 新增）**　定义 $\mathbb{F}_2$-线性映射
$$\Phi_G:W(G)\longrightarrow H^1(G;\mathbb{F}_2),\qquad z\longmapsto[s(z)],\qquad \operatorname{rank}_{\rm hol}(G)\equiv\dim_{\mathbb{F}_2}\operatorname{im}\Phi_G .$$
**含义**：$\operatorname{rank}_{\rm hol}$ 是"符号通道的比特数"，Aut-不变可达类数 $=2^{\operatorname{rank}_{\rm hol}}$；$\operatorname{rank}_{\rm hol}=0\iff$ 一切 Aut-不变赋值平凡（即 D10 的 electron-like，此处给出精确化）。

**D14（Pfaffian 定向类，v1.2 新增——仅作 §6.2 的对照通道）**　设 $G$ 的完美匹配集为 $\mathcal M$。边定向 $t:E\to\{\pm1\}$ 称 **Pfaffian 定向**，若对每个 $M\in\mathcal M$ 有 $\prod_{e\in M}t_e=(-1)^{\mathrm{cr}(M)}$，$\mathrm{cr}(M)$ 为匹配交叉数 $\bmod\,2$。等价于**无偏线性系统** $\sum_{e\in M}t_e=\mathrm{cr}(M)\ (\bmod 2)$ 的可解性，解集记 $\mathcal O_{\rm Pf}(G)$。$\#\mathcal M=0$ 时判据恒通过，**不可作发现**。

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

**T2.2（秩形式：$\operatorname{rank}(M)=\operatorname{rank}_{\rm hol}$，v1.2 新增）**

**陈述**　$\operatorname{rank}_{\mathbb{F}_2}(M)=k-\dim\big(W(G)\cap\operatorname{Cut}(G)\big)=\operatorname{rank}_{\rm hol}(G)$。

**证明**　$M$ 的零空间为 $\ker M=\{z:Mz=0\}=\{z:\sigma(\gamma_i)=0\ \forall i\}$。由 T3（环基无关性），"在基本环基上全为零"$\iff$"在一切环上全为零"$\iff[s(z)]=0$；又由 T4，$[s(z)]=0\iff s(z)\in\delta C^0=\operatorname{Cut}$。故 $\ker M=W(G)\cap\operatorname{Cut}(G)$。秩-零化度定理给出 $\operatorname{rank}M=k-\dim\ker M=k-\dim(W\cap\operatorname{Cut})$，再由 T9 等于 $\operatorname{rank}_{\rm hol}$。$\blacksquare$

**T2.3（判据的地位：必要性的误写，v1.2 修正）**　T2 的 $M\neq0$ 是**存在性**判据（等价于 $\operatorname{rank}_{\rm hol}\ge1$），**不给维数**（维数由 T9/T2.2 给出）。v1.1 §10 第 3 条把"含奇环 + 轨道数 $\ge2$"写成**必要条件**，**已被证伪**：梯族（书内编号）$k\ge5$ 奇为**二分图**（无奇环）、双轨道，却仍有 $\operatorname{rank}_{\rm hol}\ge1$（§6.3 T11）；而 $k=3$（$K_{3,3}$）为二分 + 单轨道，$\operatorname{rank}_{\rm hol}=0$。**奇环既非充分也非必要**，唯一充要判据是 T9 的 $W(G)\not\subseteq\operatorname{Cut}(G)$。

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

**证明**　单轨道 $\Rightarrow s$ 为常数 $z$（$\mathbb{F}_2$）。二分 $\Rightarrow$ 所有环 $\gamma$ 长度 $|\gamma|$ 为偶。故 $\sigma(\gamma)=z^{|\gamma|}=(z)^{even}=+1$，平凡。$\blacksquare$

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

### T9（割空间恒等式 / 平凡性的充要判据，v1.2 新增）

**陈述**　设 $G$ 连通（$c=1$；一般 $c$ 情形逐分量套用），$n_{\rm orb}=\dim W(G)$，则

$$\boxed{\ \operatorname{rank}_{\rm hol}(G)=n_{\rm orb}-\dim_{\mathbb{F}_2}\big(W(G)\cap\operatorname{Cut}(G)\big)\ }\qquad\text{且}\qquad \boxed{\ \operatorname{rank}_{\rm hol}(G)=0\iff W(G)\subseteq\operatorname{Cut}(G)\ }$$

即：**符号通道平凡 $\iff$ 每个 Aut-不变赋值都是某个割**。

**证明**　由 D13，$\Phi_G:W(G)\to H^1$ 是 $\mathbb{F}_2$-线性映射。其核
$$\ker\Phi_G=\{s\in W(G):[s]=0\in H^1\}=\{s\in W(G):s\in\delta C^0\}=W(G)\cap\operatorname{Cut}(G),$$
第一个等号是核的定义，第二个等号由 $H^1=C^1/\delta C^0$（§2.1）与 T4（类由 $[s]$ 唯一决定），第三个等号由 D12（$\operatorname{Cut}=\delta C^0$）。按秩-零化度定理，
$$\operatorname{rank}_{\rm hol}=\dim\operatorname{im}\Phi_G=\dim W(G)-\dim\ker\Phi_G=n_{\rm orb}-\dim(W\cap\operatorname{Cut}).$$
再由 $\operatorname{rank}_{\rm hol}=0\iff\operatorname{im}\Phi_G=0\iff\ker\Phi_G=W(G)\iff W(G)\subseteq\operatorname{Cut}(G)$ 得第二个等价式。$\blacksquare$

**推论 T9.1（与 T2 的衔接）**　$\operatorname{rank}_{\rm hol}\ge1\iff W(G)\not\subseteq\operatorname{Cut}(G)\iff M\neq0$（T2 的存在性判据）。T2 只回答"有没有非平凡类"，T9 回答"有几个比特"。

**推论 T9.2（两条相互独立的计算路线）**　路线 A：T2 的矩阵秩 $\operatorname{rank}_{\mathbb{F}_2}M$（$\mathcal{O}(\beta_1 k)$）；路线 B：割空间交维数 $\dim W+\dim\operatorname{Cut}-\operatorname{rank}(W\cup\operatorname{Cut})$，$\operatorname{Cut}$ 基取**星集**（D12）。$Y_3$ 判决报告在 22 个样本上（梯族、柱族、经典图、随机 3-正则图）实测两路线与"$H^1$ 类枚举""子集枚举"四路零失配。

**推论 T9.3（官方骨架读数）**　

| 骨架 | $n_{\rm orb}$ | $\dim\operatorname{Cut}$ | $\dim(W\cap\operatorname{Cut})$ | $\operatorname{rank}_{\rm hol}$ |
|---|---|---|---|---|
| $Q_3$ | 1 | 7 | 1 | **0** |
| $Y_3^{\rm cl}$ | 2 | 11 | 1 | **1** |
| $Y_3^{\rm op}$ | 7 | 11 | 5 | **2** |

与 T2 的判据一致（$Q_3$：$M=0$；$Y_3^{\rm cl}$：$M\neq0$），并与电荷涌现论文 §10.2 的通道类型一致；其中 $Q_3$ 的平凡性获得**机制解释**：其唯一 Aut-不变赋值（全 1，因边传递）恰落在割空间内。

**注（标号无关性）**　$\operatorname{rank}_{\rm hol}$ 是整数，且只依赖 $G$ 的轨道结构与割空间，**不依赖**环基选取（T3）、不依赖顶点标号（与 §6 的 $\sigma$ 类同）；这与 $\varrho$ 类量（算子 20，见其规范 §2.2）恰相反——后者对顶点标号敏感。故 $\operatorname{rank}_{\rm hol}$ 可作跨骨架的**可比较不变量**。

---

## 6 与上游电荷涌现论文的对接（官方骨架忠实复现）

算子 19 以 `skel_electron_q3 / skel_y3_closed / skel_y3_open` 忠实复现电荷涌现论文 §10.2 三类骨架，作为规范的**锚点自测**：

**表 6.1　三类骨架锚点读数**

| 骨架 | $V$ | $E$ | $\beta_1$ | $\deg$ | $\lvert\operatorname{Aut}\rvert$ | 边轨道 | 二分 | 非平凡可达 | 通道类型 |
|---|---|---|---|---|---|---|---|---|---|
| 电子 $e^-$ ($Q_3$) | 8 | 12 | 5 | 1 | 48 | 1 | 是 | **否** | electron-like |
| 质子 $p$（闭态） | 12 | 18 | 7 | 1 | 36 | 2 | 否 | **是** | nucleon-like |
| 中子 $n$（开态） | 12 | 17 | 6 | 0 | 4 | 7 | 否 | **是** | nucleon-like |

**表 6.2　割空间读数（T9；与 $Y_3$ 判决报告表 3.1 逐项一致，本项目内复核见 §8.4）**

| 骨架 | $n_{\rm orb}$ | $\dim\operatorname{Cut}$ | $\dim(W\cap\operatorname{Cut})$ | $\operatorname{rank}_{\rm hol}$ | 可达类数 $2^{\rm rank}$ |
|---|---|---|---|---|---|
| $Q_3$（电子） | 1 | 7 | 1 | **0** | 1 |
| $Y_3^{\rm cl}$（质子） | 2 | 11 | 1 | **1** | 2 |
| $Y_3^{\rm op}$（中子） | 7 | 11 | 5 | **2** | 4 |

结论（v1.2 强化）：**电子被骨架对称性强制到平凡 holonomy 类**——不是"碰巧"，而是唯一候选赋值（$Q_3$ 边传递 $\Rightarrow$ 全 1）恰落在割空间内（$\dim(W\cap\operatorname{Cut})=n_{\rm orb}=1\Rightarrow\operatorname{rank}_{\rm hol}=0$）；**质子恰有 1 比特符号自由度**（两条边轨道中恰有一条的赋值落在割空间内，故 $H^1$ 通道打开、恰 2 个可达类）；**中子有 2 比特**（7 轨道、交维数 5）。与 A0 一起给出电子/质子异号的结构来源。中子的 $\deg=0$，无论 $\sigma$ 如何 $Q_{\text{model}}=0$——**量值通道单独使中子中性**。

### 6.1 Möbius 型图实证（M1–M9，57/57 通过）

`verify_operator_19_mobius.py` 以显式构造的 Möbius 族，把「非平凡 $\sigma$」从定理变成可复现的数值实验——并给出非平凡类的**显式证书**（holonomy $-1$、非余边界、双重覆盖复原）。

**构造族**：

- **Möbius 梯 $M_k$** $=$ 偶环 $C_{2k}$ + 对径弦 $(i, i+k)$；$V=2k, E=3k, \beta_1=k+1$。$M_3$ 退化为 $K_{3,3}$，$M_4$ 即 Wagner 图 $V_8$（射影平面最小三角剖分的 1-骨架）。**编号口径（v1.2）**：本节一律用**书内编号** $M_k$（$V=2k$）；$Y_3$ 判决报告用**论文编号** $M_{2n}=\mathrm{Cay}(\mathbb{Z}_{2n},\{1,n\})$（$V=2n$），二者差因子 2，对照见 §6.3 表 6.5。
- **圆柱梯 $\Pi_k$** 对照：双 $k$-环 + $k$ 竖档；与 $M_k$ 同 $V$ 同 $E$，仅"扭"不同。
- **加扭偶环**：偶环 $C_{2k}$ 上把相邻两顶点标为异色，构成扭缺陷。

**核心数值结论**（M1–M3）：

| 族 | $\beta_1$ | 通道类型 | 结构来源 |
|---|---|---|---|
| $M_3 = K_{3,3}$ | 4 | **electron-like** | 二分 + 单边轨道，T6 强制平凡 |
| $M_k, k\ge 4$ | $k+1$ | **nucleon-like** | 多轨道，$M\neq0$（T2）。**v1.2 细分**：$k$ **偶**为非二分（含奇环）；$k$ **奇**为**二分**——此时通道打开靠"二分 + 双轨道"（$\operatorname{rank}_{\rm hol}\ge1$），与奇环无关（P19.4 / T11） |
| $\Pi_k$（偶 $k$） | $k+1$ | **electron-like** | 二分（含偶柱面）+ 单边轨道（偶数阶） |
| $\Pi_k$（奇 $k$） | $k+1$ | **nucleon-like** | 含三角面（奇环），**非二分**。**v1.2 修正**：v1.1 由此推出"真正决定翻转的是奇环存在性"，**该推理不成立**——梯族 $k\ge5$ 奇为二分图（无奇环）却有 $\operatorname{rank}_{\rm hol}\ge1$（§6.3 T11）。唯一判据是 $W\not\subseteq\operatorname{Cut}$（T9）；本族内翻转与奇环同步只是**族内巧合** |

**非平凡 $\sigma$ 的显式证书**（M4）：$M_4$ 上存在见证边轨道，令其取 $-1$、其余取 $+1$ 得 Aut-不变极性 $s_{\text{witness}}$，满足
1. $\sigma(\gamma) = -1$（基本环上有一奇环 holonomy $-1$）；
2. 独立余边界求解器（与实现无关）返回 False，确认 $s_{\text{witness}}$ **非余边界**；
3. Op19 注入口径直出 $\sigma_{\text{class}}=$ nontrivially、Q\_model $=-1$。

**双重覆盖复原**（M5）：$\sigma(\gamma^{2}) = \sigma(\gamma)^2 = +1$——绕 Möbius 梯两次回到平凡类（2π 变号 / 4π 复原），是 Möbius 带拓扑的直接数值体现。

**顶点势口径的恒平凡性**（M6）：自旋极性 $s_e=s_i s_j$ 在 $M_k$ 上的 holonomy **全为 $+1$**，再次实证 T1。

**独立交叉校验**（M7）：DFS 独立环基、$2^{\#\text{轨道}}$ 暴力枚举、独立余边界求解器三口径与 Op19 输出一致。

**电子骨架 $Q_3$ 的强制平凡**（M8）：二分 + 单边轨道，无论注入何种 Aut-不变极性，Op19 恒输出 electron-like。

**极性注入 API 回归**（M9）：orbit / explicit 双口径、Aut-不变诊断、非法输入校验，与 §8.3 / X2/X3/X8 等价。

### 6.2 双 $\mathbb{Z}_2$ 通道并置判决：$H^1$ holonomy 与 Pfaffian 定向（v1.2 新增）

算子 19 的 $\sigma$ 通道是 $H^1(G;\mathbb{Z}_2)$ 上的 holonomy 类。图论中另有一条同样取 $\mathbb{Z}_2$ 的"符号"通道——**Pfaffian 定向类**（D14）。二者是否同源，此前只在梯族上间接论证；本节在**项目自身的核子骨架**上并置判决。

**表 6.3　两通道并置读数（$Y_3$ 判决报告 §4.1）**

| 骨架 | $n_{\rm orb}$ | $\operatorname{rank}_{\rm hol}$（$H^1$ 通道） | $\#\mathcal M$ | $\lvert\mathcal O_{\rm Pf}\rvert$ | $\dim\mathcal O_{\rm Pf}$ | Pfaffian 通道 | nice even cycle |
|---|---|---|---|---|---|---|---|
| $Q_3$（电子） | 1 | 0 | 9 | 128 | 6 | **有解** | 0 |
| $Y_3^{\rm cl}$（质子） | 2 | 1 | 6 | **0** | — | **无解** | **42** |
| $Y_3^{\rm op}$（中子） | 7 | 2 | 4 | 16384 | 13 | **有解** | **0** |

**命题 P19.1（通道分离判决）**　在核子骨架闭态上，$H^1$ holonomy 通道**打开**（$\operatorname{rank}_{\rm hol}=1$，恰 2 个可达类），而 Pfaffian 通道**关闭**（$\mathcal O_{\rm Pf}=\emptyset$）。故"电荷符号由 $H^1$ holonomy 承载、而非 Pfaffian 定向承载"这一项目核心主张，在项目自身骨架上获得**直接并置实测**，不再只是"梯族上成立、骨架上外推失败"的间接论证。

**定理 T10（极小不可解行子集证书）**　$Y_3^{\rm cl}$ 的无偏系统为 $6$ 行（6 个完美匹配）$\times\,18$ 列（18 条边）；其**全部 6 行**构成极小不可解行子集：去掉任意一行，余下 5 行**可解**（可满足的最大行数 $=5/6$）。即 $Y_3^{\rm cl}$ 与"有 Pfaffian 定向"之间**只差一行**。

**证明**　由判据 D14，逐行列出 6 个完美匹配与右端 $\mathrm{cr}$ 值（表 6.4），对全部 $2^6$ 个行子集穷举：仅全集不可解，其余 63 个真子集均可解；故全集是极小不可解行子集。$\blacksquare$

**表 6.4　$Y_3^{\rm cl}$ 的无偏系统（6 行 × 18 列，右端为 $\mathrm{cr}(M)$）**

| 行 | 完美匹配 $M$ | $\mathrm{cr}(M)$ |
|---|---|---|
| 1 | $\{(0,1),(2,6),(3,11),(4,7),(5,9),(8,10)\}$ | 1 |
| 2 | $\{(0,1),(2,10),(3,7),(4,6),(5,9),(8,11)\}$ | 0 |
| 3 | $\{(0,2),(1,5),(3,11),(4,7),(6,10),(8,9)\}$ | 0 |
| 4 | $\{(0,2),(1,9),(3,7),(4,5),(6,10),(8,11)\}$ | 1 |
| 5 | $\{(0,3),(1,5),(2,10),(4,6),(7,11),(8,9)\}$ | 1 |
| 6 | $\{(0,3),(1,9),(2,6),(4,5),(7,11),(8,10)\}$ | 0 |

"差一行"由**穷举全部行子集**确认，非启发式。

**命题 P19.2（结构性机制：nice even cycle 归零）**　$Y_3^{\rm cl}$ 含 **42** 条 nice even cycle（长 6 共 9、长 8 共 9、长 10 共 18、长 12 共 6）；删去一条环边得到的 $Y_3^{\rm op}$ 该数为 **0**，Pfaffian 通道随之打开（$\dim=13$、$\lvert\mathcal O_{\rm Pf}\rvert=2^{13}$，特解独立复核 $\mathrm{Pf}=+4=\#\mathcal M$）。故"闭/开一念之差导致存在性翻转"这一 v1.1 的定性观察，现有了**具体机制**。

> **边界一（指示器不是判据）**　nice even cycle 只是**障碍指示器**：在 22 个样本上作分类器得 TP=4、FP=2、FN=3、TN=13（假阳性如 Wagner 图 $M_8$：nice=1 但有解；假阴性多为二分图）。真值始终由无偏系统给出。
> **边界二（契约不变）**　Pfaffian 是**邻接的图论通道，不属于算子 19 的输出**：实现不引入任何新键，`charge_channel_keys` 仍恒 **10 键**（§8.3），冻结契约不因本节改动。

### 6.3 $Y_3$ 与 Möbius 梯族的关系判决与编号口径（v1.2 新增）

**命题 P19.3（覆盖 / 商判决）**　$Y_3^{\rm cl}$ 与任何 $M_{2n}$（$n\ge3$）**不同构**（邻接谱与三角形数均不同）、**零覆盖**（完备回溯枚举 $M_4$–$M_{14}$ 全为 0）、**零商**（商是覆盖的特例，零覆盖蕴含零商）。**但** $Y_3^{\rm cl}$ 是 $K_4$ 的 **$k=3$ 正规覆盖**（唯一覆盖；deck 群 3 阶；商 $\cong K_4$；四条 $K_4$ 边各被提升 3 次）。$Y_3$ 的"三"（3 中心、3 组腿、3 个三角形、$\lvert\operatorname{Aut}\rvert=36=3!\times3!$、2 条边轨道各 9 条）由此获得统一解释：**$Y_3$ 是三折的完全图**。

**表 6.5　编号口径对照（差因子 2；跨文献引用前必查）**

| 图 | 书内编号 $M_k$（偶环 $C_{2k}$ + 对径弦，$V=2k$） | 论文编号 $M_{2n}=\mathrm{Cay}(\mathbb{Z}_{2n},\{1,n\})$，$V=2n$ |
|---|---|---|
| $K_4$ | $M_2$ | $M_4$ |
| $K_{3,3}$ | $M_3$ | $M_6$ |
| Wagner 图 | $M_4$ | $M_8$ |

**命题 P19.4（书内口径全族读数，$k=2,\dots,24$）**　$n_{\rm orb}=1\iff k\in\{2,3\}$；$k$ 偶 $\iff$ 非二分，$k$ 奇 $\iff$ 二分；$\operatorname{rank}_{\rm hol}=0\iff k=3$。

**定理 T11（梯族打开符号通道的充要条件）**　梯族中 $\operatorname{rank}_{\rm hol}=0$ **当且仅当** $k=3$（即 $K_{3,3}$，全族唯一"二分 + 单轨道"成员）。故 $k\neq3$ 的梯族一律打开符号通道；当 $k\ge5$ 为奇时图为**二分**（无奇环）而通道仍打开，机制是"二分 + 双轨道"。

**证明**　$k=3$ 时单轨道 + 二分，由 T6 强制平凡；$k=2$ 为 $K_4$：单轨道但含三角形，$\operatorname{rank}_{\rm hol}\ge1$。$k\ge4$ 时 $n_{\rm orb}=2$；若 $k$ 偶则含奇环，若 $k$ 奇则二分——两种情形下两条轨道中至少一条不落在割空间内（$k$ 奇时全 1 赋值落在割空间、另一条不落），故 $\dim(W\cap\operatorname{Cut})\le1<n_{\rm orb}=2$，由 T9 得 $\operatorname{rank}_{\rm hol}\ge1$。$\blacksquare$

**推论 T11.1（对 T6 与 §6.1 的修正）**　T6 的"二分 + 单轨道 $\Rightarrow$ 强制平凡"是**充分**条件，其**逆不真**（反例：$k\ge5$ 奇的梯族，二分 + 双轨道、通道打开）。因此 §6.1 原句"真正决定翻转的是奇环存在性"**不成立**，同时收紧 v1.1 §10 第 3 条把"奇环 + 多轨道"写作必要条件的写法：唯一充要判据是 T9 的 $W(G)\not\subseteq\operatorname{Cut}(G)$。

---

## 7 算法与复杂度

| 步骤 | 输入 | 输出 | 复杂度 |
|---|---|---|---|
| 0 极性选取 | `polarity` + 注入参数（D3） | 边极性 $s_e$ | 取决于口径（explicit/orbit/topo $O(E)$；spin $O(n)$ + $O(E)$） |
| 1 键图 | $A_s$ | 布尔邻接 $\mathrm{adj}$ | $\mathcal{O}(n^2)$ |
| 2 图不变量 | $\mathrm{adj}$ | $V,E,c,\beta_1,\deg,\text{bipartite}$ | $\mathcal{O}(n^2)$ |
| 3 基本环基 | $\mathrm{adj}$ | $\{\gamma_i\}_{i\le\beta_1}$ | $\mathcal{O}(n^2+E\cdot L)$ |
| 4 环 holonomy | $\{\gamma_i\},s$ | $\sigma$-vector、trivial | $\mathcal{O}(\sum_i|\gamma_i|)$ |
| 5 自同构（可选） | $\mathrm{adj},\text{colors}$ | $E$ 的轨道 | 受 `aut_cap`/`aut_max_v` 守卫（缺省 $V\le22$，否则跳过） |
| 6 可达性（可选） | $\{\gamma_i\},\{\text{轨道}\}$ | $M$、非平凡可达、见证 | $\mathcal{O}(\beta_1\cdot k)$ |

**总复杂度**：$\mathcal{O}(n^2 + \beta_1\cdot\bar L)$（不含自同构枚举）；自同构枚举为瓶颈，故设守卫 `aut_max_v=22`，超限仅跳过可达性而**不影响** $\sigma$ 类判别与 $Q_{\text{model}}$。

极性选取的校验契约（两类实现共享）：多注入口径同时给出抛 `ValueError`；`orbit_signs` 长度 ≠ 轨道数抛 `ValueError`；`edge_polarity` 缺边或含非法取值（非 $\pm1$）抛 `ValueError`；`polarity="spin"` 缺 `chi` 抛 `ValueError`。详见 §8.3 / X8。

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

三份验证程序各自独立运行，任一行断言失败以退出码 1 结束：

```
python verify_operator_19.py          # V1–V12，45 断言（严格定理逐项）
python verify_operator_19_mobius.py   # M1–M9，57 断言（Möbius 型图专项）
python verify_operator_19_cross.py    # X1–X10，29 断言（跨实现一致性 + 守卫边界）
```

零外部依赖（仅 numpy + networkx，networkx 仅用于自同构枚举）。

### 8.3 跨实现一致性结果（X1–X10，29/29 通过）

算子 19 存在两套独立维护的平行实现，二者共享本规范但代码库分离：

| 实现 | 入口 | 镜像 |
|---|---|---|
| 功能式桥接 | `operator_19_z2_charge_channel` | 单一 `sre_z2_holonomy_bridge.py` |
| 类式发布套件 | `SREChargeChannelSuite.execute_operator_19_z2_charge_channel` | 三份 SHA-256 一致（`release/`、`math-vector_v2/`、`dist/windows/`） |

`verify_operator_19_cross.py` 以同一输入对拍两实现的全部可观测量（$V,E,c,\beta_1,\deg,\sigma$-vector, $\sigma$-class, $\sigma_{\text{canonical}}, Q_{\text{model}}$, channel\_type, reachability 全字段），覆盖：

- **X1** topo 口径 32 张图（Möbius $M_3$–$M_8$、圆柱 $\Pi_3$–$\Pi_8$、$Q_3$、$Y_3$ 闭/开、$K_{2,2,2}$、16 张随机连通图）
- **X2** explicit 三口径（全 $+1$ / 首边翻转 / 逐边随机 $\pm1$）
- **X3** orbit 四口径（all+1 / all−1 / flip-first / flip-witness）
- **X4** spin 口径（含 `spin_net_sign`）
- **X5** 冻结契约：`charge_channel_keys` 恒 10 键且两实现逐键等值；跳过时键数不变、内部字段以 `None` 占位
- **X6** $V>\text{aut\_max\_v}$ 守卫（含自定义 `aut\_max\_v=10` 触发）：两实现一致跳过可达性、skip 原因一致、$\sigma$ 类仍有效
- **X7** 非连通图（双三角）：$c=2,\beta_1=E-V+c$ 两实现一致
- **X8** 8 类非法输入（极性口径非法、多注入冲突、长度不符、缺边、取值非 $\pm1$、spin 缺 chi、orbit 于 $V>\text{aut\_max\_v}$）：两实现抛同型 `ValueError`
- **X9** 元素着色对轨道与可达性的影响：两实现一致
- **X10** 顶点重标号不变性：$\sigma$ 类 / channel\_type / 不变量在随机置换下不变，且重标号后仍两实现一致

全部 29 项断言通过，证明本规范在两独立代码库上的**行为收敛**——不存在「规范文字可被多歧义解读」的空间。

> **冻结契约（D5，不得违反）**：`charge_channel_keys(res)` 必须恒定返回 **10 键**；两实现已被证实遵守，禁止后续实现改动此键数。

### 8.4 外部判决报告的复核（v1.2 新增，门 A–F）

$Y_3$ 判决报告的全部结论按六个门逐项复核；本项目内**不修改任何实现、不新增任何键**，只以独立脚本调用既有桥接函数重算可观测量：

| 门 | 复核内容 | 判定 |
|---|---|---|
| **A** 对象忠实性 | $Y_3^{\rm cl}$ / $Y_3^{\rm op}$ 的 $V,E,\beta_1,\deg,\lvert\operatorname{Aut}\rvert$、边轨道数、二分性 | 与 §6 表 6.1 逐项一致 |
| **B** 割空间恒等式 | 三骨架的 $n_{\rm orb},\dim\operatorname{Cut},\dim(W\cap\operatorname{Cut}),\operatorname{rank}_{\rm hol}$ 四列读数；$\operatorname{rank}_{\rm hol}$ 与 T2 判据 $M\neq0$ 的相容性 | $Q_3=0$、$Y_3^{\rm cl}=1$、$Y_3^{\rm op}=2$，**在本项目内独立复现** |
| **B′** 基选取陷阱 | 割空间基取星集 $d(\{v\})$ vs 误取"生成树路径边集"（后者实为循环空间） | 星集口径复现全部读数；误取口径在报告 996 例中 566 例失配，确认 D12 的陷阱提示必要 |
| **C** 四路零失配 | 矩阵秩（T2）/ 割空间交维数（T9）/ $H^1$ 类枚举 / 子集枚举 四条独立路线 | 22 个样本零失配，T9.2 成立 |
| **D** Pfaffian 证书 | 无偏系统可解性与极小不可解行子集（T10）、特解 $\mathrm{Pf}$ 交叉校验、nice even cycle 计数与分类器指标 | 逐项一致（表 6.3、6.4）；指示器假阳性/假阴性边界如 §6.2 所述，不改变判据 |
| **E** 覆盖判决与口径 | $Y_3^{\rm cl}$ 对 $M_{2n}$ 的同构/覆盖/商判定；$Y_3^{\rm cl}\to K_4$ 三折覆盖；书内 $M_k$ 与论文 $M_{2n}$ 对照 | 一致（P19.3、表 6.5） |
| **F** 编号与结论修订 | 报告对 v1.1 的两处纠正（§6.1 奇环判据、§10 第 3 条必要条件）是否已被本文吸收 | 已吸收（T2.3、T11.1、§10） |

**复核方法说明**：本项目的复核脚本**不落盘为独立验证程序**——它复用 `sre_z2_holonomy_bridge.py` 的 `edge_list / automorphisms / edge_orbits` 与骨架构造器，只在外部追加割空间维数计算；因此 V1–V12 / M1–M9 / X1–X10 的计数不变（45 / 57 / 29）。若后续需把 T9 纳入常规回归，应作为 **V13** 新增，并同步更新三处计数与冻结契约表述。

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

**层级定位**：开源底座层（1–6）、同调缝合核心层（7–10）、电子自由度扩展层（11–12）、谱形方程求解层（13–18）之后的**第五层——电荷符号 / $\mathbb{Z}_2$ holonomy 通道层（19）**。

---

## 10 诚实边界与适用域

1. **模型内部构造，非物理断言**。本规范全部结论为 SRE 模型**内部自洽构造**；$Q_{\text{model}}$ 是**模型内部电荷档**（$\in\{-1,0,+1\}$），不构成对现实分子/粒子电荷数值的物理断言。
2. **Aut-不变是明示假设**。可达性结论（T2、T6）依赖电荷涌现论文 §13.2 的**明示假设**"边极性在自同构下不变"。**不加此假设**时，任何含环的图都容许非平凡类（1 bit 自由度，维数 $=\beta_1$），可达性分析退化为平凡事实。
3. **非平凡可达的充要条件是割空间判据，不是奇环判据（v1.2 修正）**。v1.1 曾把"含**奇环**且边轨道数 $\ge2$"写作必要条件，**该写法已被证伪**：梯族 $k\ge5$ 奇为二分图（无奇环）而 $\operatorname{rank}_{\rm hol}\ge1$（T11）。正确表述是 T9：$W(G)\not\subseteq\operatorname{Cut}(G)$，等价于 T2 的 $M\neq0$。**二分性、奇环存在性、轨道数均非充要**；它们只在特定族内与结论同步。
4. **分子层需元素着色**。分子键图的 Aut 必须以元素标号着色（T7），否则 C 与 H 等异元素可能被混同，轨道结构失真。
5. **规模守卫**。自同构枚举设 `aut_max_v=22` 守卫；超大图仅跳过可达性分析，$\sigma$ 类判别与 $Q_{\text{model}}$ 仍有效。
6. **$A_s$ 语义**。19 复用算子 1/4 输出的 $A_s$，其键图支撑 $A_s>0$ 的语义由上游保证（SRE 公理 1 的协同边 $E^+$）；若上游 $A_s$ 含数值噪声，请以 `bond_graph_from_As(eps)` 的 $\epsilon$ 判定。
7. **割空间基必须取星集（v1.2）**。$\operatorname{Cut}$ 的基取 $d(\{v\})$；若误取"生成树上 $v\to$ 根的路径边集"，得到的是**循环空间**而非割空间，$\operatorname{rank}_{\rm hol}$ 将系统性失真（报告 996 例中 566 例失配，§8.4 门 B′）。
8. **Pfaffian 是外部对照通道，不是算子 19 的输出（v1.2）**。§6.2 的 Pfaffian 读数不进入计算结果、不新增键；`charge_channel_keys` 仍恒 **10 键**。Pfaffian 逻辑需另设入口，禁止挂到算子 19 的返回值上。
9. **nice even cycle 只是指示器（v1.2）**。其在 22 样本分类器上 TP=4 / FP=2 / FN=3 / TN=13，**不可**用作判据；真值必须由无偏线性系统给出（D14）。
10. **编号口径必须标注（v1.2）**。书内 $M_k$（$V=2k$）与论文 $M_{2n}$（$V=2n$）差因子 2；任何跨文献引用梯族编号处必须同时写出两套编号（表 6.5），否则 $K_{3,3}=M_3=M_6$ 之类的对照会错位一格。
11. **$\operatorname{rank}_{\rm hol}$ 的跨骨架可比性有前提（v1.2）**。它只依赖轨道结构与割空间，故与标号无关（优于 $\varrho$ 类量）；但**只在相同 Aut 约束下可比**——放宽 Aut 约束后空间变为整个 $C^1$，维数变为 $\beta_1$，与 $n_{\rm orb}$ 口径不可混用。

---

## 11 结论

算子 19 把电荷涌现论文的 $\sigma$ **符号通道**单独实现、单独建基：

- **良定义**（T0）：1-复形上 $\sigma$ 是 $H_1$ 上的 $\mathbb{F}_2$-线性泛函，无代表歧义；
- **符号的不可伪造性**（T1/T1.1）：顶点势型极性（含算子 11 自旋极性、算子 18 符号赋型）holonomy 恒平凡——电荷符号不能由局部自旋重标定造出；
- **可达性的封闭判据**（T2/T2.1/T2.2）：非平凡可达 $\iff M\neq0$，$\mathcal{O}(\beta_1 k)$，无需 $2^k$ 枚举；
- **平凡性的充要判据与比特计数**（T9/T9.2，v1.2）：$\operatorname{rank}_{\rm hol}=n_{\rm orb}-\dim(W\cap\operatorname{Cut})$，可达类数 $=2^{\operatorname{rank}_{\rm hol}}$；两独立计算路线在 22 样本零失配；
- **双 $\mathbb{Z}_2$ 通道的并置判决**（§6.2，v1.2）：在 $Y_3^{\rm cl}$ 上 $H^1$ 通道打开（1 比特）而 Pfaffian 通道无解（极小不可解证书：6 行全用才矛盾），符号归属由实测而非推断确定；
- **覆盖关系与编号口径**（§6.3，v1.2）：$Y_3^{\rm cl}$ 与梯族零覆盖、零商，但为 $K_4$ 的三折正规覆盖；书内 $M_k$ 与论文 $M_{2n}$ 的因子 2 对照已建表；
- **规范不变性**（T3/T4）：平凡性判别与环基无关，$\sigma$ 对顶点势重标定免疫，只依赖 $[s]\in H^1$；
- **双通道分离**（T5）：符号 $\sigma$ 与量值 $\deg$ 正交，$Q=\sigma\deg$；
- **电子型/核子型的结构来源**（T6/T11.1）：偶环 + 单轨道强制平凡（电子）——但**逆不真**，$k\ge5$ 奇梯族为二分却打开通道；判据收敛到 T9；
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
| $W(G)=\operatorname{span}\{\mathbf 1_{O_o}\}$ | Aut-不变赋值子空间，$\dim=n_{\rm orb}$（v1.2） |
| $\operatorname{Cut}(G)=d(S)$ | 割空间 $=\operatorname{im}\delta_0$，$\dim=n-c$；基取星集 $d(\{v\})$（v1.2） |
| $\operatorname{rank}_{\rm hol}=\dim\operatorname{im}\Phi_G$ | 符号通道比特数，可达类数 $=2^{\operatorname{rank}_{\rm hol}}$（v1.2） |
| $\mathcal O_{\rm Pf}$ | Pfaffian 定向解集（外部对照通道，不属算子 19 输出）（v1.2） |
| $\deg=\beta_1\bmod2$ | 量值通道 |
| $Q_{\text{model}}=\sigma_{\text{canonical}}\cdot\deg$ | 模型内部电荷档 |
