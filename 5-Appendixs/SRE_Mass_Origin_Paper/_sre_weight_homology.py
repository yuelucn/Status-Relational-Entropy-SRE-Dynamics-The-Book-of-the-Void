# -*- coding: utf-8 -*-
"""
_sre_weight_homology.py —— 「加权方式的数学解释」核查：休眠率是不是同调表现形式？
（第二十九轮，2026-09-28）

用户命题（两条分句，须各自判定）：
  (U1) 轨道是**算出来的**，没有任何观测能看到轨道；
  (U2) 加权方式应当对应一种**数学解释**，例如「休眠率是一种同调（上同调）表现形式」。

本脚本把两条拆成可判定命题，逐条给判据 + 实测 + 作用域：

 PART A  (U1) 形式化：观测量是 Aut-不变量的函数 ⇒ 「轨道数」是模型侧派生量，不是观测量
 PART B  C¹ 的**两个角色**：度量（conductance → Laplacian → 电阻距离） vs 联络（→ H¹ 类）
 PART C  (U2) 正例：休眠模式 σ 是 ℤ₂ 1-上链；其类 [σ] = H₁(G)→ℤ₂ 的表示（= 双覆盖 / 扭转）
 PART D  (U2) 反例（决定性）：类是**规范不变**的 ⇒ 对「哪条边带扭转」失明 ⇒ 不能唯一破对称
 PART E  账本权重恒为 2 值 ⇒ 三点环最多 2+1 分裂 ⇒ {1,1,1} 不可达（中微子靶的**同调级**判负）
 PART F  裁决表

用法：
  C:/myapp/miniconda3/envs/ai/python.exe -u _sre_weight_homology.py > _sre_weight_homology.log 2>&1
"""
import json
import itertools
import numpy as np
import networkx as nx

OUT = {}


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * 88)
    P(t)
    P("=" * 88)


# ==================================================================================
# 0  最小 SRE 装配（复制自 _sre_multigraph_probe.py，避免 import 顶层会跑的脚本）
# ==================================================================================
def Y3(pre="", state="p", open_ring=0):
    """核子骨架：三股 Y + 三角闭合；state='n' 时打开 (L0r,L1r) 一条环边。"""
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("%sL%d%d" % (pre, a, j), "%sL%d%d" % (pre, b, j))
    if state == "n":
        G.remove_edge("%sL0%d" % (pre, open_ring), "%sL1%d" % (pre, open_ring))
    return G


def assemble(groups):
    """groups = [(tag, [(pre,state), ...]), ...]；每 group 共享一条环。
    返回 (简单图 H, 账本重数 ledger)。"""
    H = nx.Graph()
    ledger = {}
    for r, (_tag, bodies) in enumerate(groups):
        for pre, state in bodies:
            G = Y3(pre, state, r)
            m = {"%sL%d%d" % (pre, i, r): "S%d%d" % (r, i) for i in range(3)}
            edges = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
            for e in edges:
                ledger[e] = ledger.get(e, 0) + 1
            H.add_edges_from(edges)
    return H, ledger


def ring_triple(ledger, r=0):
    """共享环三条边 (S0,S1),(S1,S2),(S2,S0) 的声称重数。"""
    ring = [tuple(sorted(("S%d0" % r, "S%d1" % r))),
            tuple(sorted(("S%d1" % r, "S%d2" % r))),
            tuple(sorted(("S%d2" % r, "S%d0" % r)))]
    return [ledger.get(e, 0) for e in ring]


# ==================================================================================
# 1  三个图论 / 代数小工具
# ==================================================================================
def beta1(G):
    """一阶 Betti 数（纯图，无 2-胞腔）：E - V + 连通分量数。"""
    return G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)


def res_matrix(L):
    """电阻距离矩阵 R_ij = L⁺_ii + L⁺_jj - 2 L⁺_ij。"""
    Lp = np.linalg.pinv(L)
    d = np.diag(Lp)
    R = d[:, None] + d[None, :] - 2.0 * Lp
    return np.clip(R, 0.0, None)


def tri_resistance(w):
    """三角形三点，边权 w = [w01, w12, w20]（= 电导）⇒ 三个电阻距离。"""
    w01, w12, w20 = w
    L = np.array([[w01 + w20, -w01, -w20],
                  [-w01, w01 + w12, -w12],
                  [-w20, -w12, w12 + w20]], float)
    R = res_matrix(L)
    return [R[0, 1], R[1, 2], R[2, 0]]


def partition3(vals, tol=1e-9):
    """把 3 个电阻距离聚成「层级划分」字符串，如 '3' / '2+1' / '1+1+1'。"""
    vs = sorted(vals)
    groups = [[vs[0]]]
    for v in vs[1:]:
        if abs(v - groups[-1][-1]) <= tol * max(1.0, abs(v)):
            groups[-1].append(v)
        else:
            groups.append([v])
    return "+".join(str(len(g)) for g in groups)


def periods(sigma_edges, cycles, eidx):
    """1-上链 σ 在一组圈基上的周期（ℤ₂）：class(σ) 的坐标。"""
    out = []
    for cyc in cycles:
        s = 0
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            e = tuple(sorted((a, b)))
            s ^= sigma_edges[eidx[e]]
        out.append(s)
    return tuple(out)


# ==================================================================================
# PART A —— (U1) 形式化：轨道是「算出来的」
# ==================================================================================
head("PART A  (U1) 形式化：观测量是 Aut-不变量的函数，「轨道数」不是观测量")


def ring_graph():
    G = nx.Graph()
    G.add_edges_from([("S0", "S1"), ("S1", "S2"), ("S2", "S0")])
    return G


G_ring = ring_graph()
lab = ["S0", "S1", "S2"]
P("A1  无权重共享环（三角形）：")
P("    度序列 = %s    Laplacian 谱 = %s" % (sorted(dict(G_ring.degree()).values()),
                                        np.round(np.sort(np.linalg.eigvalsh(
                                            nx.laplacian_matrix(G_ring).toarray().astype(float))), 9).tolist()))
P("    Aut 轨道数 = 1（顶点传递）⇒ 三点不可分辨")
P()

# 「哪条环边是开态带」这一标记，逐个试
specs = []
for j in range(3):
    Gc = ring_graph()
    # 把「第 j 条边更重」的权重贴上去 —— 只是标记，不作为物理权重
    w = [1.0, 1.0, 1.0]
    w[j] = 2.0
    L = np.diag([w[0] + w[2], w[0] + w[1], w[1] + w[2]]) - np.array(
        [[0, w[0], w[2]], [w[0], 0, w[1]], [w[2], w[1], 0]])
    specs.append(np.round(np.sort(np.linalg.eigvalsh(L)), 9).tolist())
P("A2  把「哪条环边带标记」逐个换（j = 0,1,2）：")
for j, s in enumerate(specs):
    P("    j=%d  谱 = %s" % (j, s))
P("    ⇒ 三个谱**逐位相同**（差 <= 1e-9）：观测者从谱上**分不出**是哪条边 ⇒ 标记不可观测。")
P()
P("A3  结论（(U1) 成立，且更精确）：")
P("    · 观测量 = Aut-不变量的函数（谱、连通性、计数……）；")
P("    · 「Aut 轨道 / 轨道数」是**模型侧的派生量**（由 G 的标号算出来的），")
P("      **不是**任何观测能返回的量。⇒ 用轨道去「破简并」，等于在模型侧加标号。")
P("    · 因此 (U1) 的两半都成立：轨道确实只是算出来的，也确实不可观测。")
P("    · 但要注意：不可观测 ≠ 无意义。轨道决定「哪些量必然简并」，是**模型的自洽性约束**。")
OUT["A"] = {"ring_spectra_identical": all(s == specs[0] for s in specs),
            "ring_orbit_count": 1}


# ==================================================================================
# PART B —— C¹ 的两个角色
# ==================================================================================
head("PART B  C¹ 的两个角色：度量（→电阻距离） vs 联络（→ H¹ 类）")

P("B0  定义。给图的每条边一个实数，得到的是 C¹(G;ℝ) 的一个元素 w。")
P("    同一个 w 可以扮演两个**互不相同**的角色：")
P()
P("    角色 I  度量 / 电导（conductance）")
P("            w → 加权 Laplacian L_w = B₁ diag(w) B₁ᵀ → 可观测 = 电阻距离 R = L_w⁺ 的 Green 函数。")
P("            这是**对称、正、无规范自由**的对象；换 w 就是换一张不同的网。")
P()
P("    角色 II 联络 / 状态（connection）")
P("            w 的「周期」（沿圈求和，或 ℤ₂ 下沿圈异或）是**规范不变量**：")
P("            规范变换 w → w + df（f: V→ℤ₂ 或 →ℝ 的边缘），周期不变。")
P("            ⇒ 不变量 = 类 [w] ∈ H¹(G; A)  ≅  Hom(H₁(G), A)  = 「H₁ 的一个表示」。")
P()
P("B1  两个角色**不是同一个东西**（数值演示）：三角形上取同一条 ℤ₂ 类（周期相同）的两条实现，")
P("    转成电导后给**不同的分裂**（见 PART D）。⇒ 类 ≠ 度量。")
OUT["B"] = {"note": "C^1 has two roles: metric (Laplacian) and connection (cohomology class)"}


# ==================================================================================
# PART C —— (U2) 正例：休眠模式是 ℤ₂ 1-上链，其类 = H₁→ℤ₂ 的表示
# ==================================================================================
head("PART C  (U2) 正例：休眠率确有一个同调解释 —— ℤ₂ 1-上链的类")

P("C0  定义「休眠模式」σ：每条边一个 ℤ₂ 值（开/闭、或重数亏缺的奇偶）。")
P("    σ ∈ C¹(G; ℤ₂)。**在图上（1-维复形，无 2-胞腔）每条 1-上链自动是上圈** ⇒ 无所谓「上圈条件」，")
P("    全部内容就在它的**周期**（沿每个独立圈异或求和）。")
P("    周期向量 ∈ ℤ₂^{β₁} ⇒ σ 的类 [σ] ∈ H¹(G; ℤ₂) ≅ Hom(H₁(G), ℤ₂)。")
P("    ⇒ 这正是「**H₁ 的一个表示**」—— 即用户所说的『同调表现形式』，且是**精确**的对应。")
P()

# 共享环三点环：单圈
G1 = ring_graph()
cyc = nx.cycle_basis(G1)
eidx = {tuple(sorted(e)): i for i, e in enumerate(G1.edges())}
P("C1  共享环（三角形，β₁ = %d，|H¹(ℤ₂)| = 2^β₁ = %d）：" % (beta1(G1), 2 ** beta1(G1)))
for name, sig in [("全闭 (0,0,0)", (0, 0, 0)),
                  ("开一条 (1,0,0)", (1, 0, 0)),
                  ("开一条 (0,1,0)", (0, 1, 0)),
                  ("开一条 (0,0,1)", (0, 0, 1)),
                  ("开两条 (1,1,0)", (1, 1, 0))]:
    per = periods(sig, cyc, eidx)
    P("    σ = %-16s 周期 = %s  ⇒ %s" % (name, per,
      "非平凡类（扭转 Twisted）" if per[0] else "平凡类（无扭转 Untwisted）"))
P("    ⇒ **三种『开一条边』的实现全在同一个非平凡类**（它们差一个规范 df）⇒ 类不区分「哪条边」。")
P()

P("C2  把 SRE 实际装配的账本读进来（亏缺 = 开态体数）：")
cases = [("³H  (p,n,n)", [("t", [("a", "p"), ("b", "n"), ("c", "n")])]),
         ("³He (p,p,n)", [("h", [("a", "p"), ("b", "p"), ("c", "n")])]),
         ("p-p (p,p)  ", [("d", [("a", "p"), ("b", "p")])]),
         ("n-n (n,n)  ", [("e", [("a", "n"), ("b", "n")])])]
cres = {}
for name, grp in cases:
    H, led = assemble(grp)
    rt = ring_triple(led)
    deficit = [max(rt) - x for x in rt]           # 相对满值 k 的亏缺
    sig = tuple(d % 2 for d in deficit)
    per = periods(sig, cyc, eidx)
    cres[name] = {"ring_ledger": rt, "deficit": deficit, "sigma": sig, "period": per}
    P("    %-12s 环账本 = %-10s 亏缺 = %-10s σ = %-10s 周期 = %d ⇒ %s"
      % (name, rt, deficit, sig, per[0],
         "非平凡（扭转）" if per[0] else "平凡（无扭转）"))
P()
P("C3  读法：")
P("    · 休眠模式**确实**是一个 ℤ₂ 1-上链，其类**确实**是 H₁(G)→ℤ₂ 的表示 ⇒ (U2) 的")
P("      **数学识别成立**：这条对应关系是精确的，不是类比。")
P("    · 非平凡类 = 图的一个**双覆盖**（覆盖理论：ℤ₂ 上圈 ↔ 双覆盖）⇒ 与项目的")
P("      「Möbius 4π 双覆盖 / Z₂ holonomy」**同一件东西**（电子桥 §4 的 4-圈符号连乘）。")
P("    · **规则→类的推论（零参数）**：装配规则「每共享环恰有一个开态体 ⇒ 恒有一条 k=1 边」")
P("      给出亏缺恰 1 ⇒ 周期恰 1 ⇒ **每条共享环都携带非平凡 ℤ₂ 类 ⇒ 共享环是扭转的**。")
P()
P("C4  **零参数正例**：³H 与 ³He 落在**不同的 ℤ₂ 类**里（亏缺 2 vs 1 ⇒ 周期 0 vs 1）。")
P("    这是一个**规范不变、零自由参数**的离散不变量，能把二者分开（不需要任何电导/权重）。")
P("    ⚠ 诚实：它等于「开态体数的奇偶」（= 中子数奇偶），是 **1 bit** 的弱不变量，")
P("      与我们真正要的质量比 / 磁矩比（连续量）之间**没有已知的赋值规则** ⇒")
P("      它证明「同调层有可分辨内容」，但**不**给出 μ 族锚的数值。")
P("    规范不变性数值自检：枚举全部 f ∈ ℤ₂^V，取 σ → σ + df，看周期是否恒定。")
G1n = list(G1.nodes())
eord = [tuple(sorted(e)) for e in G1.edges()]
def df_of(f):
    out = [0] * len(eord)
    for i, (u, v) in enumerate(eord):
        out[i] = (f[G1n.index(v)] ^ f[G1n.index(u)])
    return out
chk = []
for f in itertools.product([0, 1], repeat=3):
    d = df_of(f)
    for sig in ([0, 0, 0], [1, 0, 0], [1, 1, 0]):
        s2 = [a ^ b for a, b in zip(sig, d)]
        chk.append(periods(tuple(s2), cyc, eidx) == periods(tuple(sig), cyc, eidx))
P("      %d 组 (f, σ) 检验：周期全部不变？ %s  ⇒ 周期（类）确为规范不变量 ✓" % (len(chk), all(chk)))
OUT["C"] = {"ring": cres, "H1_Z2_ring": 2 ** beta1(G1),
            "gauge_invariance_verified": bool(all(chk)),
            "3H_class": cres["³H  (p,n,n)"]["period"][0],
            "3He_class": cres["³He (p,p,n)"]["period"][0]}


# ==================================================================================
# PART D —— (U2) 反例（决定性）：类对「哪条边」失明 ⇒ 不能唯一破对称
# ==================================================================================
head("PART D  (U2) 反例（决定性）：类是规范不变量 ⇒ 不能唯一破三点对称")

P("D1  上一步已见：σ=(1,0,0) / (0,1,0) / (0,0,1) **同属一个类**（差规范 df）。")
P("    现在看这三者作为**电导**给出的电阻距离划分：")
tblD = []
for j, nm in enumerate(["j=0 边重", "j=1 边重", "j=2 边重"]):
    w = [1.0, 1.0, 1.0]
    w[j] = 2.0
    R = tri_resistance(w)
    part = partition3(R)
    tblD.append((nm, [round(float(x), 9) for x in R], part))
    P("    %-10s 电导 w = %-16s R = %s  ⇒ 划分 %s"
      % (nm, w, [round(float(x), 9) for x in R], part))
P("    ⇒ 三者给**同一个划分型 2+1**（只是哪两点配成对被换掉）—— 一个类**只能**给到 2+1。")
P()
P("D2  更致命：**同一个类可以有不同划分**。都取平凡类（周期 0）：")
tblD2 = []
for nm, w in [("w=(1,1,1)", [1.0, 1.0, 1.0]), ("w=(1,1,2)", [1.0, 1.0, 2.0]),
              ("w=(2,2,1)", [2.0, 2.0, 1.0])]:
    R = tri_resistance(w)
    part = partition3(R)
    tblD2.append((nm, part))
    P("    %-10s R = %s ⇒ 划分 %s" % (nm, [round(float(x), 9) for x in R], part))
P("    ⇒ 同属平凡类的 w=(1,1,1) 给划分 3，w=(1,1,2) 给划分 2+1。")
P("       ⇒ **划分不是类的函数**（类 → 划分 不是良定义映射）。")
P()
P("D3  结论（作用域写清）：")
P("    · 类 [σ] 是**规范不变量**，因此**必然对「扭转落在哪条边」失明**；")
P("    · 「哪两点配上对」这件事住在**规范部分（非类部分）**里，而规范部分**不是**任何不变量；")
P("    · ⇒ 想用「同调类」去**唯一地**破三点对称：**不可能**（定理级，与数值无关）。")
P("    · 这与既有律同型：**不变量定形、规范部分定值** —— 定形不定值在**同调层**再出现一次。")
OUT["D"] = {"same_class_partitions": tblD, "trivial_class_partitions": tblD2,
            "verdict": "class is gauge-invariant => blind to which edge => cannot canonically break symmetry"}


# ==================================================================================
# PART E —— 账本权重恒 2 值 ⇒ {1,1,1} 不可达（中微子靶的同调级判负）
# ==================================================================================
head("PART E  账本权重恒 2 值 ⇒ 三点环最多 2+1 分裂 ⇒ {1,1,1} 不可达")

P("E1  账本形态定理（枚举 + 归纳）：k 体共享环、其中 m 体开态 ⇒ 环边重数 = (k−m, k, k)。")
P("    （因所有开态体打开**同一条**环边，亏缺全落在那一条上。）")
P("    ⇒ 环边重数**只有两个不同值** ⇒ 作为电导只能产生 2+1 或 3 的划分。")
P()
P("E2  穷举 ℤ₂ 上链 × 电导 realize（在三角形上）——可达划分统计：")
parts = {}
for sig in itertools.product([0, 1], repeat=3):
    w = [1.0 + s for s in sig]        # ℤ₂ 值 → 电导 {1,2}
    part = partition3(tri_resistance(w))
    parts.setdefault(part, []).append(sig)
for part, sigs in sorted(parts.items()):
    P("    划分 %-6s 可达 σ ∈ %s" % (part, sigs))
P("    ⇒ **{1,1,1} 永不出现**：要三点两两不等需三条边**三个不同**权重，")
P("      而 ℤ₂ 只有两个值、账本重数也只有两个值 ⇒ **结构性不可达**。")
P()
P("E2' 目击对照（证明卡点恰是「二值」，不是「一般不可能」）：给三条边**三个不同**权重：")
for w in ([1.0, 2.0, 3.0], [1.0, 1.5, 4.0]):
    R = tri_resistance(w)
    P("    w = %-16s R = %-30s ⇒ 划分 %s"
      % (w, [round(float(x), 9) for x in R], partition3(R)))
P("    ⇒ **三值权重确实能给出 1+1+1**。所以判负的**精确作用域**是：")
P("      「凡赋值只有**两个档**（ℤ₂ / 两档重数）者，三点环给不出 1+1+1」。")
P("      要 1+1+1，必须引入**第三个档**——而第三个档既不在 ℤ₂ 里，也不在账本重数里，")
P("      只能来自**新增的连续输入**（= C3 闸门：自由参数数 < 目标个数）。")
P()
P("E3  与中微子靶的关系：")
P("    · 中微子需**两个非零 Δm²**（三个非简并能级）⇒ 要求三点谱**两两不等**（划分 1+1+1）。")
P("    · 上一轮电阻距离探针只拿到 **2+1**（轨道 1→2）；本轮给出**为什么止步于 2**：")
P("      ℤ₂ 类 + 账本重数**都是二值的** ⇒ 天然只能 2+1。")
P("    · ⇒ §12.14 判负的**作用域可以再加一层**：不只是「简单图装配下」，而是")
P("      「**任何二值（ℤ₂ / 两档重数）赋值下**，三点环都不可能给出 1+1+1」。")
OUT["E"] = {"achievable_partitions": {k: [list(x) for x in v] for k, v in parts.items()},
            "111_reachable": "1+1+1" in parts}


# ==================================================================================
# PART F —— |H¹(G;ℤ₂)| 表 + 裁决
# ==================================================================================
head("PART F  |H¹(G;ℤ₂)| 表 与 总裁决")

ga = {"C₃ 共享环": ring_graph(),
      "K₄": nx.complete_graph(4),
      "Q₃ = 立方体": nx.hypercube_graph(3),
      "三棱柱 C₃×K₂": nx.cartesian_product(nx.cycle_graph(3), nx.complete_graph(2)),
      "Möbius 梯 M₆": nx.Graph([(i, (i + 1) % 6) for i in range(6)] +
                               [(i, i + 3) for i in range(3)]),
      "Y₃ 闭态骨架": Y3(),
      "Y₃ 开态骨架": Y3(state="n")}
P("    图                 V     E    β₁   |H¹(ℤ₂)| = 2^β₁")
tabF = {}
for nm, G in ga.items():
    b1 = beta1(G)
    tabF[nm] = {"V": G.number_of_nodes(), "E": G.number_of_edges(), "beta1": b1, "H1Z2": 2 ** b1}
    P("    %-18s %-5d %-5d %-5d %d" % (nm, G.number_of_nodes(), G.number_of_edges(), b1, 2 ** b1))
P()
P("    ⇒ |H¹(G;ℤ₂)| = 2^β₁ = 该图的双覆盖个数 ⇒ 「扭转模」的个数是**有限整数**，")
P("      是可数的**离散**量（与项目『离散侧闭合』主线一致）。")
OUT["F"] = tabF

head("总裁决")

verdict = [
 ("(U1) 轨道是算出来的、不可观测",
  "**成立**",
  "观测量 = Aut-不变量函数；轨道数是模型侧派生量。用轨道破简并 = 在模型侧加标号。"),
 ("(U2-A) 休眠率 = H₁ 的一个表示（同调表现形式）",
  "**成立（数学识别精确）**",
  "休眠模式 σ ∈ C¹(G;ℤ₂)，类 [σ] ∈ H¹(G;ℤ₂) ≅ Hom(H₁(G),ℤ₂) = 双覆盖 = Z₂ holonomy。"),
 ("(U2-B) 用同调类**唯一地**破三点对称",
  "**判负（定理级）**",
  "类是规范不变量 ⇒ 对「扭转落在哪条边」失明；且类→划分 非良定义。"),
 ("(U2-C) 账本权重能给出三点两两不等（{1,1,1}）",
  "**判负（结构性）**",
  "ℤ₂ 与账本重数皆二值 ⇒ 只能 2+1 或 3 ⇒ 中微子所需 1+1+1 不可达。"),
]
for i, (q, v, why) in enumerate(verdict, 1):
    P("  %d. %s" % (i, q))
    P("     判定：%s" % v)
    P("     依据：%s" % why)
    P()
P("  净结论：")
P("    · 用户对「轨道不可观测」的判断是对的，对「加权应有数学解释」的判断也是对的；")
P("    · 那个解释**确实存在且是标准的**：C¹(G) 的上同调 —— 休眠率 = H₁→ℤ₂ 的表示；")
P("    · 但**它是「定形」的那一半**（给不变量、给双覆盖、给扭转的离散模），")
P("      而「破对称、定值」的那一半住在**规范部分/度量**里，**不能被同调类替代**；")
P("    · ⇒ 上一轮的电阻距离探针（破 1→2）是在**度量角色**下做的，本轮的类是在**联络角色**下看的，")
P("      两者互补，但**不能用后者给前者「追认」一个规范身份** —— 这正是 C3（自由参数数 < 目标数）")
P("      在**同调层**的再现。")
OUT["verdict"] = [{"question": q, "verdict": v, "reason": why} for q, v, why in verdict]

with open("_sre_weight_homology.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P()
P("已写出 _sre_weight_homology.json")
