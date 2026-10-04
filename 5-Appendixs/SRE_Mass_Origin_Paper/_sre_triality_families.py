# -*- coding: utf-8 -*-
"""
_sre_triality_families.py —— 「三档结构」的数学归宿：Z3 / 三力性（triality）
（第三十轮，2026-09-28）

承接第二十九轮报告 §8.3 留下的开放方向：
  「不要再用二值数据硬破三点对称；去找一个**已含三档**的强制结构，
    把同调类当作**约束**而不是**解**。」

本脚本的论断（逐条给判据 + 实测 + 作用域）：
  PART A  Z2 → Z3 是「对偶（duality）→ 三力性（triality）」的标准升格（第 2/第 3 单位根）；
          同调阶梯 |H^1(G;Z_n)| = n^{beta_1}（n 元覆盖的个数）
  PART B  SRE 骨架**本身**携带 Z3：闭态 |Aut| = 36 含 8 个三阶元；
          且存在显式 phi: 环号 j -> j+1（保边、阶 3）=> 三环构成一个 Z3-挠子（自由 + 传递）
  PART C  开态把 Z3 破为 Z2（|Aut| = 4；三环轨道 1 -> 2）
          => 「闭 -> 开」= 「Z3 -> Z2」；质子->中子 = 三力性 -> 对偶性
  PART D  三档**不必**来自二值边标号（上一轮判负处）：
          它来自**一个复序参量 A 的 Z3 轨道**——三点天然互异、且是规范的
  PART E  Koide 定理：Q = 1/3 + (2/3)eta^2 **与相位 delta 无关**；
          Q = 2/3 <=> eta^2 = 1/2 <=> |A| = 1/sqrt2（C-S 区间中点 / 45 度）
  PART F  裁决 + 诚实边界

用法：
  C:/myapp/miniconda3/envs/ai/python.exe -u _sre_triality_families.py > _sre_triality_families.log 2>&1
"""
import json
import math
import itertools
import cmath
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

OUT = {}
W = cmath.exp(2j * math.pi / 3.0)          # omega = 第 3 单位根


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * 90)
    P(t)
    P("=" * 90)


# ==================================================================================
# 0  最小 SRE 装配（复制自 _sre_weight_homology.py，避免 import 顶层会执行的脚本）
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


def beta1(G):
    return G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)


def perm_order(m, nodes):
    o = 1
    for v in nodes:
        x, c = v, 0
        while True:
            x = m[x]
            c += 1
            if x == v:
                break
        o = o * c // math.gcd(o, c)
    return o


def ring_orbits(G, autos):
    """三环 {L0j,L1j,L2j} 在 Aut 下的轨道结构（返回轨道列表 + 每环的像环号集合）。"""
    rings = [frozenset(("L0%d" % j, "L1%d" % j, "L2%d" % j)) for j in range(3)]
    ring_index = {r: j for j, r in enumerate(rings)}
    # 每个自同构诱导环集上的置换
    perms = []
    for m in autos:
        img = {}
        for j, r in enumerate(rings):
            r2 = frozenset(m[x] for x in r)
            img[j] = ring_index.get(r2, None)
        if all(v is not None for v in img.values()):
            perms.append(tuple(img[j] for j in range(3)))
    # 轨道
    seen, orbits = set(), []
    for j in range(3):
        if j in seen:
            continue
        orb = {j}
        for p in perms:
            orb.add(p[j])
        seen |= orb
        orbits.append(sorted(orb))
    return orbits, sorted(set(perms))


# ==================================================================================
# PART A —— Z2 -> Z3：对偶 -> 三力性；同调阶梯
# ==================================================================================
head("PART A  Z2 -> Z3：「对偶（duality）-> 三力性（triality）」的标准升格")

P("A0  文献定式（外部事实，非本脚本计算）：")
P("    · 三力性论文（McRae 2025, arXiv:2502.14016）原话：")
P("      「triality 可以看作**基乘以第 3 单位根**，正如 duality 常是**基乘以第 2 单位根**。」")
P("    · 于是：")
P("        duality  = Z2 = 单位根 {+1,-1}          -> 二值（自旋 1/2 / 双覆盖 / 电荷正负）")
P("        triality = Z3 = 单位根 {1, w, w^2}       -> 三值（**三代**）")
P("    · 三代模型普遍用 Z3：")
P("        DVFT（Thorwe 2026）：三分量真空场的天然 Z3 -> 相位 120 度 -> **循环矩阵** -> Koide")
P("        Rousselle 2026 (arXiv:2608.19277)：U(3)_F -> U(1)_F^3，等价于破缺到 **Z(SU(3)) = Z3**")
P("        Ma 2006 (hep-ph/0612022)：四个 Z3 生成元 -> Sigma(81) 群")
P("        Koide 本人 1981：sqrt(m_k) ~ 1 + sqrt(2) cos(delta + 2*pi*k/3) —— **2*pi*k/3 就是 Z3**")
P("    · ⇒ 「三档」的数学名字是 **Z3 = 三力性**，不是「Z2 的第三个取值」。")
P()

P("A1  同调阶梯（本脚本计算）：覆盖的个数 = |H^1(G;Z_n)| = n^{beta_1}")
ga = {"C3 共享环": nx.cycle_graph(3),
      "K4": nx.complete_graph(4),
      "Q3 = 立方体": nx.hypercube_graph(3),
      "Y3 闭态骨架": Y3(),
      "Y3 开态骨架": Y3(state="n")}
P("    %-16s %5s %5s %6s %14s %14s" % ("图", "V", "E", "beta_1", "|H1(Z2)|=2^b1", "|H1(Z3)|=3^b1"))
tabA = {}
for nm, G in ga.items():
    b1 = beta1(G)
    tabA[nm] = {"V": G.number_of_nodes(), "E": G.number_of_edges(), "beta1": b1,
                "H1Z2": 2 ** b1, "H1Z3": 3 ** b1}
    P("    %-16s %5d %5d %6d %14d %14d" % (nm, G.number_of_nodes(), G.number_of_edges(),
                                          b1, 2 ** b1, 3 ** b1))
P()
P("    ⇒ Z_n 覆盖的个数是 n^{beta_1}。Z2 档 = 双覆盖（项目已有：Mobius 4pi 双覆盖 / Z2 holonomy）；")
P("      Z3 档 = **三覆盖**（= 三力性）。阶梯不是「多加一个值」，而是**换系数群**。")
OUT["A"] = tabA


# ==================================================================================
# PART B —— SRE 骨架本身携带 Z3
# ==================================================================================
head("PART B  SRE 骨架**本身**携带 Z3（三环 = 一个 Z3-挠子）")

tabB = {}
for st, label in (("p", "闭态（质子）"), ("n", "开态（中子）")):
    G = Y3(state=st)
    nodes = list(G.nodes())
    autos = list(GraphMatcher(G, G).isomorphisms_iter())
    ords = [perm_order(m, nodes) for m in autos]
    n3 = sum(1 for o in ords if o == 3)
    n2 = sum(1 for o in ords if o == 2)
    orbits, perms = ring_orbits(G, autos)
    tabB[st] = {"V": G.number_of_nodes(), "E": G.number_of_edges(), "Aut": len(autos),
                "order3_elements": n3, "order2_elements": n2,
                "ring_orbits": orbits, "ring_perms": perms}
    P()
    P("B  %s   V=%d E=%d   |Aut|=%d" % (label, G.number_of_nodes(), G.number_of_edges(), len(autos)))
    P("    阶 3 自同构个数 = %d ；阶 2 自同构个数 = %d" % (n3, n2))
    P("    三环在 Aut 下的轨道： %s" % orbits)
    P("    环集上诱导的置换（去重）： %s" % perms)
    if st == "p":
        phi = lambda nm: nm if nm.startswith("c") else ("L%s%d" % (nm[1], (int(nm[2]) + 1) % 3))
        ok_edge = all(G.has_edge(phi(u), phi(v)) for u, v in G.edges())
        ok_ord3 = all(phi(phi(phi(x))) == x for x in G.nodes())
        P("    显式验证 phi: L(i,j) -> L(i,j+1)，c_i -> c_i： 保边 = %s ；阶 = 3 = %s" % (ok_edge, ok_ord3))
        tabB["phi_ok_edge"] = bool(ok_edge)
        tabB["phi_ok_order3"] = bool(ok_ord3)
P()
P("B1  判据与结论：")
P("    · 闭态骨架的 Aut 含 8 个三阶元（Sylow-3 = Z3 x Z3）⇒ 其中**存在**一个自由、传递地")
P("      置换三环的 Z3（实测：三环在 Aut 下**只有 1 条轨道**，大小为 3）。")
P("    · 一个集合被一个群**自由且传递**地作用 = 该集合是一个 **G-挠子（torsor）**。")
P("      ⇒ **三环构成一个 Z3-挠子**：它们可以（且只能）被**无原点地**用 Z3 标签——")
P("         即「换个整体相移」是唯一的自由度。")
P("    · ⚠ 这正是第二十九轮判负的来源，也**正是**三代的形状：三代之间有一个 Z3 循环序，")
P("      但**没有绝对原点**（原点 = 相移 = Koide 的 delta）。")
OUT["B"] = tabB


# ==================================================================================
# PART B2 —— Z3 特征分解：顶点表示给 1/2|1/2，边表示给 1/3|2/3
# ==================================================================================
head("PART B2  Z3 特征分解：顶点表示给 1/2|1/2，边表示给 1/3|2/3")

G = Y3()
phi = lambda nm: nm if nm.startswith("c") else ("L%s%d" % (nm[1], (int(nm[2]) + 1) % 3))
nodes = list(G.nodes())
edges = [tuple(sorted(e)) for e in G.edges()]
fix_v = sum(1 for v in nodes if phi(v) == v)
fix_e = sum(1 for e in edges if tuple(sorted((phi(e[0]), phi(e[1])))) == e)


def char_mult(dim, fix):
    """置换表示 (dim, chi(phi)=fix) 在 Z3 下的重数：triv=(dim+2fix)/3，(w,w2)=(dim-fix)/3。"""
    return (dim + 2 * fix) // 3, (dim - fix) // 3


mtv, mwv = char_mult(len(nodes), fix_v)
mte, mwe = char_mult(len(edges), fix_e)
P("B2  取 phi: 环号 j -> j+1（PART B 已证其保边、阶 3）。置换表示 chi(phi) = 不动点数：")
P("    顶点： V=%-3d 不动点数 chi(phi)=%-3d ⇒ 表示 = %d*1 + %d*w + %d*w^2"
  % (len(nodes), fix_v, mtv, mwv, mwv))
P("          ⇒ 平凡权重 = %d/%d = %.6f ； 非平凡权重 = %.6f"
  % (mtv, len(nodes), mtv / len(nodes), 1 - mtv / len(nodes)))
P("    边  ： E=%-3d 不动点数 chi(phi)=%-3d ⇒ 表示 = %d*1 + %d*w + %d*w^2"
  % (len(edges), fix_e, mte, mwe, mwe))
P("          ⇒ 平凡权重 = %d/%d = %.6f ； 非平凡权重 = %.6f"
  % (mte, len(edges), mte / len(edges), 1 - mte / len(edges)))
P()
P("B2' 结构解释（为何恰好是这两个比值）：")
P("    · 骨架 = 3 个股 x (1 个股心 c_i + 3 个环叶 L{i}{0,1,2})。")
P("      股心被 phi **固定**（进平凡表示）；3 个环叶被 phi **循环**（= 正则表示 reg = 1+w+w^2）。")
P("      ⇒ 每股权重：平凡 = 1 + 1 = 2；非平凡 = 1 + 1 = 2 ⇒ **顶点等分 1/2 | 1/2**。")
P("    · 边：所有边都被 phi 移走（无不动边，chi=0）⇒ 边表示 = **6 份正则表示**")
P("      ⇒ 平凡 1/3、非平凡 2/3 ⇒ **边给 1/3 | 2/3**。")
P()
P("B2'' 登记（**候选，非结论**，须过 D1）：")
P("    · 顶点表示给 **1/2 | 1/2**（等分）；边表示给 **1/3 | 2/3**。")
P("    · 与 Koide 形式的**数字对应**（仅登记，机制未给）：")
P("        Q = 1/3 + (2/3)*eta^2  的 (1/3, 2/3)  <-  **边**表示的 Z3 特征权重")
P("        eta^2 = 1/2                        <-  **顶点**表示的平凡权重（等分）")
P("    · ⇒ 若两者同源，则 Q = 1/3 + (2/3)*(1/2) = 2/3 **自动**成立。")
P("    · ⚠ 1/3、2/3、1/2 全是**小分母有理数** ⇒ 单独看**无判别力**（D1 陷阱）。")
P("      登记为候选的**唯一理由**是三者**恰好拼成** Q=2/3 这一完整链条；")
P("      升级为结论**必须**另找机制（把「边表示/顶点表示」接到「m_k/序参量」上）。")
OUT["B2"] = {"vertex": {"dim": len(nodes), "chi": fix_v, "mult_triv": mtv, "mult_non": mwv,
                        "w_triv": mtv / len(nodes), "w_non": 1 - mtv / len(nodes)},
             "edge": {"dim": len(edges), "chi": fix_e, "mult_triv": mte, "mult_non": mwe,
                      "w_triv": mte / len(edges), "w_non": 1 - mte / len(edges)},
             "candidate_chain": "Q = 1/3 + (2/3)*eta^2 with (1/3,2/3) from edge rep and eta^2=1/2 from vertex rep => Q=2/3"}


# ==================================================================================
# PART C —— 开态把 Z3 破为 Z2：闭->开 = Z3->Z2
# ==================================================================================
head("PART C  开态把 Z3 破为 Z2：闭 -> 开 = Z3 -> Z2")

P("C0  上一步实测：")
P("      闭态 |Aut| = %d，含阶 3 元 %d 个，三环轨道 1 条（{0,1,2}）"
  % (tabB["p"]["Aut"], tabB["p"]["order3_elements"]))
P("      开态 |Aut| = %d，含阶 3 元 %d 个，三环轨道 %s"
  % (tabB["n"]["Aut"], tabB["n"]["order3_elements"], tabB["n"]["ring_orbits"]))
P()
P("C1  读法（本轮的**结构级发现**）：")
P("    · 闭态（质子态）三环**完全等价**（Z3 对称）⇒ 图层对「哪一环」简并；")
P("    · 开态（中子态，断一条环边）Z3 **被破为 Z2**（|Aut| 由 36 落到 4；阶 3 元归零）")
P("      ⇒ 三环裂为 **2 条轨道**：{开环} | {另两环}。")
P("    · ⇒ **「闭 -> 开」这个 SRE 的基本二态，恰好就是「Z3 -> Z2」**：")
P("         闭态 = 三力性（triality, 三环等价）")
P("         开态 = 对偶性（duality,  两环等价 + 一环特异）")
P("    · 与文献**同构**：Koide 结构 = 「有 Z3（三代）+ 有 1/2（等分）」；SRE 基本二态同时给出")
P("      这两半：Z3 来自闭态骨架，2 分结构来自开态的 Z2。")
P()
P("    ⚠ 诚实边界：这里只证「SRE 基本二态 = Z3->Z2 破缺」是**结构事实**；")
P("      它**还没有**把 Z3 接到质量值上（赋值规则仍未给出，见 PART E/F）。")
OUT["C"] = {"closed_Aut": tabB["p"]["Aut"], "open_Aut": tabB["n"]["Aut"],
            "closed_ring_orbits": tabB["p"]["ring_orbits"],
            "open_ring_orbits": tabB["n"]["ring_orbits"],
            "note": "closed skeleton carries Z3; opening it breaks Z3 -> Z2"}


# ==================================================================================
# PART D —— 三档来自「一个复序参量的 Z3 轨道」，不是来自二值边标号
# ==================================================================================
head("PART D  三档的来源：一个复序参量的 Z3 轨道（对比：二值边标号做不到）")

P("D0  回顾上一轮判负（第二十九轮 PART E）：")
P("    在**一个三角形的三条边**上贴二值标号（Z2 或两档重数）⇒ 可达划分只有 {3, 2+1}，")
P("    **{1+1+1} 结构性不可达**。⇒ 想从「一条环的三条边」拿三档：不可能。")
P()

P("D1  正确的对象不是「一条环的三条边」，而是「**三环的 Z3 轨道**」：")
P("    取一个**复序参量** A = eta * exp(i*delta)（2 个实参数），定义三个实数")
P("        x_k = 1 + 2*eta*cos(delta + 2*pi*k/3) ,  k = 0,1,2")
P("    （= 「同一个 A 在 Z3 挠子的三个位置上的读数」，即 A 的 Z3 **轨道**。）")
P("    判据：对一般 (eta, delta)，三点**互异**（1+1+1）；退化只在测度零处发生。")
P()
P("    实测（若干 (eta, delta)）：")
P("    %-22s %-34s %-10s" % ("(eta, delta)", "x_k", "划分"))
tabD = []
for eta, delta in [(0.0, 0.0), (1 / math.sqrt(2), 2 / 9), (1 / math.sqrt(2), 0.0),
                   (0.5, 1.0), (0.9, 2.5)]:
    xs = [1 + 2 * eta * math.cos(delta + 2 * math.pi * k / 3) for k in range(3)]
    xs_r = [round(x, 6) for x in xs]
    # 划分
    vs = sorted(xs)
    g = [[vs[0]]]
    for v in vs[1:]:
        if abs(v - g[-1][-1]) <= 1e-9 * max(1.0, abs(v)):
            g[-1].append(v)
        else:
            g.append([v])
    part = "+".join(str(len(c)) for c in g)
    tabD.append((eta, delta, xs_r, part))
    P("    %-22s %-34s %-10s" % ("(%.4f, %.4f)" % (eta, delta), xs_r, part))
P()
P("    ⇒ eta != 0 且 delta 不在特殊值时，三点互异 ⇒ **1+1+1 天然可达**。")
P("    ⇒ 三档**不需要**新增第三个「档」；它来自 **Z3 这个群本身**（三点 = 群的三个位置）。")
P("      上一轮判负的作用域因此得以精确化：")
P("        「在**一条环的三条边**上用二值标号」不可达；")
P("        但「在**三环的 Z3 挠子**上用 Z3 作用」是**天然三档**的。")
OUT["D"] = {"examples": [{"eta": e, "delta": d, "x": x, "partition": p} for e, d, x, p in tabD]}


# ==================================================================================
# PART E —— Koide 定理：Q 只依赖 |A|；Q=2/3 <=> eta^2=1/2
# ==================================================================================
head("PART E  Koide 定理：Q = 1/3 + (2/3)*eta^2 **与相位无关**；Q=2/3 <=> eta^2 = 1/2")

P("E0  解析（可手算验证）：x_k = 1 + 2*eta*cos(delta + 2*pi*k/3)。")
P("    因 sum_k cos(delta+2*pi*k/3) = 0、 sum_k cos^2(...) = 3/2：")
P("        sum_k x_k   = 3")
P("        sum_k x_k^2 = 3 + 4*eta^2*(3/2) = 3 + 6*eta^2")
P("    Koide 组合 Q = (sum m)/( sum sqrt(m) )^2  取 m_k ~ x_k^2  ==>")
P("        Q = (sum x_k^2)/(sum x_k)^2 = (3+6*eta^2)/9 = 1/3 + (2/3)*eta^2")
P("    ⇒ **Q 只依赖 eta = |A|，完全不依赖相位 delta**（这是 Z3 不变量的直接后果）。")
P("    ⇒ Q = 2/3  <=>  (2/3)*eta^2 = 1/3  <=>  eta^2 = 1/2  <=>  |A| = 1/sqrt(2)。")
P()
P("E1  等价链（同一个约束的五种语言）：")
P("        Q = 2/3  <=>  eta^2 = 1/2  <=>  |A| = 1/sqrt(2)  <=>  与 (1,1,1) 夹角 = 45 度")
P("                 <=>  Q 落在 Cauchy-Schwarz 区间 [1/3, 1] 的**正中点**")
P()
P("E2  实测（真实带电轻子质量，PDG）：")


def Q_of(m):
    s = sum(math.sqrt(x) for x in m)
    return sum(m) / (s * s)


cases = [("m_tau = 1776.86（归档口径）", [0.51099895069, 105.6583755, 1776.86]),
         ("m_tau = 1776.93（2026 PDG 中心）", [0.51099895069, 105.6583755, 1776.93])]
P("    %-30s %-16s %-14s %-14s %-12s" % ("输入", "Q", "eta^2=(3Q-1)/2", "偏差 vs 2/3", "45度角"))
tabE = []
for nm, m in cases:
    Q = Q_of(m)
    eta2 = (3 * Q - 1) / 2
    ang = math.degrees(math.acos(min(1.0, math.sqrt(1 / (3 * Q)))))
    dev = Q - 2 / 3
    tabE.append({"case": nm, "Q": Q, "eta2": eta2, "dev_from_2_3": dev, "angle_deg": ang})
    P("    %-30s %-16.9f %-14.9f %-14.3e %-12.4f" % (nm, Q, eta2, dev, ang))
P()
P("    ⇒ eta^2 = 1/2 在真实数据上成立到 %.2e（m_tau=1776.93 口径）。" % abs(tabE[1]["eta2"] - 0.5))
P()
P("E3  相位 delta 的测量（旁证，**须过 D1 纪律**）：")
P("    由 u_k = (sqrt(m_k)/a0 - 1)/sqrt(2) = cos(delta + 2*pi*k/3)，")
P("    取 DFT： z = sum_k u_k * w^{-k} = (3/2) e^{i*delta}  ⇒ delta = arg(z)（模 2*pi/3）。")
me, mmu, mtau = 0.51099895069, 105.6583755, 1776.93
tabE_phase = []
for tag, mvec in (("升序 (e,mu,tau)", [me, mmu, mtau]),
                  ("降序 (tau,mu,e)", [mtau, mmu, me])):
    A = [math.sqrt(x) for x in mvec]
    a0 = sum(A) / 3.0
    u = [(v / a0 - 1) / math.sqrt(2) for v in A]
    z = sum(u[k] * (W ** (-k)) for k in range(3))
    d = cmath.phase(z) % (2 * math.pi / 3)
    tabE_phase.append({"order": tag, "delta_mod_2pi_over_3": d,
                       "two_ninths": 2 / 9, "dev": d - 2 / 9})
    P("    %-16s delta (mod 2pi/3) = %.9f rad   2/9 = %.9f   偏差 = %+.3e (相对 %+.5f%%)"
      % (tag, d, 2 / 9, d - 2 / 9, 100 * (d - 2 / 9) / (2 / 9)))
P("    ⚠ D1 纪律：2/9 是**小分母有理数**，与 delta 的吻合**不得**当独立证据（会踩 D1 陷阱）。")
P("      本轮只登记为**旁证**；且须注意 delta 本身是**规范量**（整体相移 = 三代置换）。")
OUT["E"] = {"cases": tabE, "phase": tabE_phase,
            "theorem": "Q = 1/3 + (2/3) eta^2, independent of delta; Q=2/3 <=> eta^2=1/2"}


# ==================================================================================
# PART F —— 裁决 + 诚实边界
# ==================================================================================
head("PART F  裁决与诚实边界")

verdict = [
    ("「三档」的数学名字是什么？",
     "**Z3 = 三力性（triality）**",
     "对偶 = 第 2 单位根（Z2）；三力性 = 第 3 单位根（Z3）。文献（McRae）原话；三代模型普遍用 Z3。"),
    ("Z3 在 SRE 里有原生归宿吗？",
     "**有（结构级）**",
     "闭态骨架 |Aut|=36 含 8 个三阶元；显式 phi: 环号 j->j+1（保边、阶 3）⇒ 三环 = Z3-挠子。"),
    ("上一轮的 {1,1,1} 不可达被判负，矛盾吗？",
     "**不矛盾，作用域不同**",
     "判负限於「**一条环的三条边 + 二值标号**」；三档的正确载体是「**三环的 Z3 轨道**」，天然三值。"),
    ("Z3 能给出 Koide 吗？",
     "**给出形状（定理级），不给值**",
     "Q = 1/3 + (2/3)eta^2 **与相位无关**；Q=2/3 <=> eta^2=1/2。eta 的值仍须输入（= G12 连续侧）。"),
    ("SRE 基本二态与 Z3/Z2 的关系？",
     "**闭->开 = Z3->Z2（结构级发现）**",
     "闭态 |Aut|=36（Z3 完整）；开态 |Aut|=4（阶 3 元归零，三环裂为 2 轨道）⇒ 开态只剩 Z2。"),
]
for i, (q, v, why) in enumerate(verdict, 1):
    P("  %d. %s" % (i, q))
    P("     判定：%s" % v)
    P("     依据：%s" % why)
    P()
P("总裁决（一句话）：")
P("    「三档结构」有一个精确的数学归宿 —— **Z3 / 三力性**，它是项目已有 Z2（对偶 / Mobius 双覆盖）")
P("    的**同族升格**（第 2 单位根 -> 第 3 单位根）；SRE 骨架**本身**就携带这个 Z3（三环 = Z3-挠子），")
P("    而「闭 -> 开」这一基本二态**恰好**是 Z3 -> Z2 的破缺。⇒ 三代 = 三环的 Z3 轨道；")
P("    三代的质量模式 = 一个复序参量在 Z3 上的轨道；Koide 的 Q=2/3 <=> |A| = 1/sqrt2（等分点）。")
P()
P("诚实边界（不可省）：")
P("   1. 本报告全部为 **SRE 模型内部 / 图论与群论层面**的自洽陈述，不声称对现实物理的数值预言。")
P("   2. 「Z3 是三代的结构」是**数学识别 + 文献共识**；SRE 视角下**新增的**是「骨架自带 Z3」与")
P("      「闭->开 = Z3->Z2」两条**结构事实**，不是新的数值预言。")
P("   3. **识别 ≠ 赋值**：Z3 给出「三代」的形状与 Koide 的函数形式，但**不给** eta 的值；")
P("      eta^2 = 1/2 的**来源**仍未给出（候选：Z2 等分；须另证，见下一步）。")
P("   4. 相位 delta ≈ 2/9 属**小分母有理数**（D1 陷阱），只作旁证；且 delta 是规范量。")
P("   5. PART B2'' 的「边表示 1/3|2/3 + 顶点表示 1/2 => Q=2/3」链条**是候选不是结论**：")
P("      三个比值全是小分母有理数（D1 陷阱），单独无判别力；登记的唯一理由是三者恰好拼成")
P("      Q=1/3+(2/3)(1/2)=2/3。升级为结论必须**另找机制**（把「边/顶点表示」接到「m_k/序参量」上），")
P("      否则与「整数 ≈ 整数」同型，不予采信。")
P("   6. PART A 的 |H^1(G;Z3)| = 3^beta_1 只说明「Z3 覆盖/三力性在图上**存在**」；")
P("      它**不**自动等于「物理上有三代」——「三代」仍须机制（Z3 挠子 + 序参量）。")
OUT["verdict"] = [{"q": q, "verdict": v, "why": why} for q, v, why in verdict]

with open("_sre_triality_families.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P()
P("已写出 _sre_triality_families.json")
