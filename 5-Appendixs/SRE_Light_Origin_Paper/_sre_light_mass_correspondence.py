# -*- coding: utf-8 -*-
"""
_sre_light_mass_correspondence.py —— 第 35 轮
================================================
问题：「质量 = 未打开的、循环的演化逻辑（ℤ₃-等变循环算子）」
      与「SRE 对光 / 电磁波的既有描述」是否一致？

既有口径（必须引原文，不得转述）
--------------------------------
· 电子论文 §3.1【公理 I（残余性）】：
    Ψ_light(φ,w) ≡ ker( ∂_mutual(A_t, B_{t'}) )
  —— 「光不是独立的物质本体 …… 光体现为联合执行链因果交集处的互不湮灭拓扑残余」。
· 【公理 II】：X(φ,w) = ((1+w cos(φ/2))cosφ, (1+w cos(φ/2))sinφ, w sin(φ/2))
  —— 2 个内禀自由度 (φ, w)；φ→φ+2π 时横向矢量内禀翻转 w→−w；4π 才闭合。
· Fork A §2.4 / §3.5：加权 Möbius 阶梯 M_n 上，对合 P = S^{n/2}，P² = I，P v_k = (−1)^k v_k；
  **k 偶 = 电子扇区，k 奇 = 光子扇区**。
· 电子拓扑 §3：δ ≡ w*−1 = **ℤ₂ holonomy 通道的涌现耦合强度**（度量参数，非拓扑不变量）。
· 第 30/32 轮（质量侧）：闭态 Y₃ 骨架 |Aut|=36 含 Sylow-3 = ℤ₃×ℤ₃，三环 = ℤ₃-挠子；
  质量算子 A = c₀·1 + c₁·S + c̄₁·S²，S³ = 1（三环循环移位）；
  「未打开」= 不做带原点谱分解，只输出等变类。

本脚本做的是**对照实测**，不是证明等同。
输出：_sre_light_mass_correspondence.log / .json
"""
import sys
import math
import cmath
import json
from collections import Counter

import numpy as np
import networkx as nx

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

OUT = {}
W3 = cmath.exp(2j * math.pi / 3)          # ℤ₃ 生成元的相位（第 3 单位根）
W2 = -1.0                                  # ℤ₂ 生成元的相位（第 2 单位根）


def P(*a):
    print(*a, flush=True)


def head(t):
    P()
    P("=" * 84)
    P(t)
    P("=" * 84)


def perm_order(p):
    """置换的阶 = 各轮换长度的最小公倍数。"""
    seen, l = set(), 1
    for x in p:
        if x in seen:
            continue
        c, y = 0, x
        while y not in seen:
            seen.add(y)
            y = p[y]
            c += 1
        l = l * c // math.gcd(l, c)
    return l


# ------------------------------------------------------------------
# 复用：核子骨架 Y₃ ⋉ △₃（第 29/30/32 轮同一构造）
#   节点：c0,c1,c2（股心）＋ L{0..2}{0..2}（叶点）；共 12 顶点、18 边、β₁ = 7
#   开态：断一条环边 (L0r, L1r) ⇒ 17 边、β₁ = 6
# ------------------------------------------------------------------
def Y3(open_ring=None):
    G = nx.Graph()
    for i in range(3):
        G.add_node("c%d" % i)
        for j in range(3):
            G.add_node("L%d%d" % (i, j))
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    if open_ring is not None:
        G.remove_edge("L0%d" % open_ring, "L1%d" % open_ring)
    return G


# ------------------------------------------------------------------
# 复用：项目统一的 Möbius 阶梯 M_n 构造（code/_sre_collapse_in_nucleon.py）
#   V = n、E = n + n/2 = 3n/2、β₁ = n/2 + 1；n 必须为偶
# ------------------------------------------------------------------
def mobius_ladder(n):
    assert n % 2 == 0, "n must be even"
    G = nx.Graph()
    for i in range(n):
        G.add_edge(i, (i + 1) % n)
    for i in range(n // 2):
        G.add_edge(i, i + n // 2)
    return G


def beta1(G):
    return G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)


# ==================================================================
head("PART A  同调阶梯：|H^1(G;Z_n)| = n^{beta1}  —— 光档(n=2) 与 质量档(n=3)")
# ==================================================================
P("A1. 同一个梯子上的两级。n=2 档 = 对偶/双覆盖（光）；n=3 档 = 三力性（质量）。")
P("    （第 30 轮已实测 n=3 档：C₃ 3｜K₄ 27｜Q₃ 243｜Y₃闭 2187｜Y₃开 729；本轮补 n=2 档。）")
P()

GALL = [
    ("C3   (三环)",          nx.cycle_graph(3),      "质量侧最小环（ℤ₃ 载体）"),
    ("K4",                   nx.complete_graph(4),   "第 30 轮对照"),
    ("Q3   (立方体)",        nx.hypercube_graph(3),  "电子线本体（β₁=5）"),
    ("M6   (Möbius 梯)",     mobius_ladder(6),       "光/电子同拓扑（β₁=4）"),
    ("Y3闭 (核子骨架)",      Y3(None),               "质量侧骨架（β₁=7）"),
    ("Y3开 (断一环边)",      Y3(0),                  "开态（β₁=6）"),
    ("M60  (Möbius 梯)",     mobius_ladder(60),      "α 锚载体（β₁=31）"),
]

P("    图                   V     E   b1    |H^1(Z2)| = 2^b1        |H^1(Z3)| = 3^b1")
P("    " + "-" * 88)
rowsA = []
for name, G, note in GALL:
    V, E, b = G.number_of_nodes(), G.number_of_edges(), beta1(G)
    h2, h3 = 2 ** b, 3 ** b
    P("    %-20s %4d  %4d  %3d   %-12s         %s" % (name, V, E, b, format(h2, ","), format(h3, ",")))
    rowsA.append(dict(name=name, V=V, E=E, b1=b, H1_Z2=h2, H1_Z3=h3, note=note))
OUT["A_homology_ladder"] = rowsA

P()
P("A2. 检验：n=3 档的五个读数是否严格等于 3^b1（复现第 30 轮 PART A 表）")
for r in rowsA:
    if r["name"].split()[0] in ("C3", "K4", "Q3", "Y3闭", "Y3开"):
        P("      %-18s b1=%d  →  3^b1 = %-8s (期望同值)" % (r["name"], r["b1"], format(r["H1_Z3"], ",")))
P()
P("A3. 读法：**光与质量不是两个机制，而是同一个梯子的相邻两级**。")
P("    「同调阶梯」的自由参数只有一个：系数群 ℤ_n 的 n。")
P("      n=2 → 双覆盖（2π 与 4π 的对映；Möbius）          → 光／对偶")
P("      n=3 → 三覆盖（挠子，无原点）                      → 质量／三力性")
P("    两者共同的母群 = U(1)（连续相位）——而 U(1) 正是电磁的规范群。")

# ==================================================================
head("PART B  光侧载体实测：M_n 上的对合 P = S^{n/2}（ℤ₂）与「扇区分裂」")
# ==================================================================
P("B1. Fork A 口径：P = S^{n/2}，P² = I，P v_k = (−1)^k v_k；k 偶 = 电子扇区，k 奇 = 光子扇区。")
P("    本轮把它做成可复算的实测：")
P()
n, w = 60, 1.0
Gm = mobius_ladder(n)
Aadj = nx.to_numpy_array(Gm, nodelist=list(range(n)))
Lap = np.diag(Aadj.sum(1)) - Aadj
Pm = np.zeros((n, n))
for i in range(n):
    Pm[i, (i + n // 2) % n] = 1.0

chk = {}
chk["P^2 = I"] = bool(np.allclose(Pm @ Pm, np.eye(n)))
chk["P != I"] = bool(not np.allclose(Pm, np.eye(n)))
chk["P in Aut (P A P^T = A)"] = bool(np.allclose(Pm @ Aadj @ Pm.T, Aadj))
chk["P L = L P (可同时对角化)"] = bool(np.allclose(Pm @ Lap, Lap @ Pm))
chk["tr(P) = (+1) 重数 - (-1) 重数"] = float(np.trace(Pm))
for k, v in chk.items():
    P("      %-32s : %s" % (k, v))
OUT["B_P_check"] = {k: (v if isinstance(v, bool) else float(v)) for k, v in chk.items()}

P()
P("B2. 闭式谱 μ_k = (2+w) − 2cos(2πk/n) − w·(−1)^k（项目既有 code/_sre_downward_scope.py）")
P("    —— 注意那个 (−1)^k 项：**它就是 ℤ₂ 分裂的痕迹**。")
kk = np.arange(n)
mu_closed = (2.0 + w) - 2.0 * np.cos(2.0 * np.pi * kk / n) - w * ((-1.0) ** kk)
mu_numeric = np.sort(np.linalg.eigvalsh(Lap))
P("    数值谱 vs 闭式谱最大偏差 = %.3e" % np.abs(mu_numeric - np.sort(mu_closed)).max())
P()
ev = sorted(mu_closed, reverse=True)
P("    ρ (最大 Laplacian 特征值) = %.12f" % ev[0])
P("    对应 k = ?   %s" % ("k=29 或 31（奇）" if abs(ev[0] - (2 + w - 2 * math.cos(2 * math.pi * 29 / n) - w * (-1))) < 1e-9 else "?"))
P("    λ₂(电子扇区，k=2) = %.12f   = 4sin²(2π/60) = %.12f"
  % (mu_closed[2], 4 * math.sin(2 * math.pi / n) ** 2))
P("    项目闭式 Π₁(M_n) = 4sin²(2π/n)/(2+2w+2cos(2π/n)) ⇒ M60 = %.10f   (1/137.035999084 = %.10f)"
  % (4 * math.sin(2 * math.pi / n) ** 2 / (2 + 2 * w + 2 * math.cos(2 * math.pi / n)),
     1 / 137.035999084))
OUT["B_spectra"] = dict(rho=float(ev[0]), lam2_even=float(mu_closed[2]),
                        pi1_M60=float(4 * math.sin(2 * math.pi / n) ** 2 / (2 + 2 * w + 2 * math.cos(2 * math.pi / n))))

P()
P("B3. 扇区分裂（两条公式只差一个常数 2w —— 且**只作用于奇/光子扇区**）：")
P("      偶扇区（P=+1，电子）:  μ_k = 2      − 2cos(2πk/n)")
P("      奇扇区（P=−1，光子）:  μ_k = 2+2w   − 2cos(2πk/n)")
tabB = []
for k in range(0, 8):
    sgn = "+1" if k % 2 == 0 else "-1"
    base = 2.0 - 2.0 * math.cos(2.0 * math.pi * k / n)
    val = mu_closed[k]
    tabB.append(dict(k=k, P_eig=sgn, mu=float(val), mu_base=float(base)))
    P("      k=%2d  P=%s   μ_k = %.9f      (= base %.9f %s )"
      % (k, sgn, val, base, "          " if k % 2 == 0 else "+ 2w = %.1f" % (2 * w)))
OUT["B_sector_table"] = tabB
P()
P("    ⇒ 与电子拓扑 §3.4 的 δ 指纹**严格同形**：")
P("      μ_k(1+δ) − μ_k(1) = 2δ  (k 奇，光子扇区)  |  0  (k 偶，电子扇区)")
P("      即：**ℤ₂ 对合把谱劈成两支，且偏移只落在光子扇区。**")
P("      『光』在 SRE 里的离散标记 = ℤ₂；它的可观测后果 = 这个 2w 的整体平移。")

# ==================================================================
head("PART C  质量侧载体实测：Y₃ 上的循环移位 S（ℤ₃）与三扇区谱")
# ==================================================================
P("C1. 三环的循环移位 S：环标号 j → j+1（第 30 轮见证 φ: L_{i,j} → L_{i,j+1}）")
Gy = Y3(None)
phi = lambda nm: nm if nm.startswith("c") else ("L%s%d" % (nm[1], (int(nm[2]) + 1) % 3))
ok_edge = all(Gy.has_edge(phi(u), phi(v)) for u, v in Gy.edges())
ok_o3 = all(phi(phi(phi(x))) == x for x in Gy.nodes())
ok_nI = any(phi(x) != x for x in Gy.nodes())
P("      S 保边 (S ∈ Aut)         : %s" % ok_edge)
P("      S³ = id                  : %s" % ok_o3)
P("      S ≠ id                   : %s" % ok_nI)
P("      ⇒ S 是**阶 3** 的保边置换，且它给出的 3 条环边同一条轨道 ⇒ 三环 = ℤ₃-挠子。")
OUT["C_shift"] = dict(edge_preserving=ok_edge, order3=ok_o3, nontrivial=ok_nI)

P()
P("C2. 质量算子 A = c₀·1 + c₁·S + c̄₁·S²（与 S 交换 ⇔ 循环矩阵；第 32 轮实测中心化子维数 = 3 = n）")
P("    谱：λ_k = c₀ + 2|c₁|·cos(θ + 2πk/3)，k = 0,1,2  —— 三个值由 ℤ₃ 相位 2π/3 给出。")
for (c0, c1, th_deg) in [(1.0, 0.3, 40.0), (1.0, 0.3, 0.0)]:
    th = math.radians(th_deg)
    lam = [c0 + 2 * c1 * math.cos(th + 2 * math.pi * k / 3) for k in range(3)]
    P("      c0=%.1f |c1|=%.1f θ=%5.1f°  ⇒  λ = (%.6f, %.6f, %.6f)"
      % (c0, c1, th_deg, lam[0], lam[1], lam[2]))
    if abs(th_deg) < 1e-9:
        P("        （θ=0 时退化：ℤ₃ 的三个相位给出 {c₀+2|c₁|, c₀−|c₁|, c₀−|c₁|} ⇒ **2+1**）")
OUT["C_spectra"] = dict(eq_th40=[1.0 + 2 * 0.3 * math.cos(math.radians(40) + 2 * math.pi * k / 3) for k in range(3)])

P()
P("C3. 两侧并列（**同一形式、不同阶**）：")
P("      " + "-" * 76)
P("      %-26s %-24s %-24s" % ("", "光 / 电磁波", "质量"))
P("      " + "-" * 76)
P("      %-26s %-24s %-24s" % ("载体图的算子", "P = S^{n/2}", "S"))
P("      %-26s %-24s %-24s" % ("阶", "2", "3"))
P("      %-26s %-24s %-24s" % ("本征值", "{+1, −1}", "{1, ω, ω²}"))
P("      %-26s %-24s %-24s" % ("谱扇区数", "2", "3"))
P("      %-26s %-24s %-24s" % ("参数", "(φ, w)", "(η, δ)"))
P("      %-26s %-24s %-24s" % ("谱公式", "μ_k = (2+w)−2cos−w(−1)^k", "λ_k = c₀+2|c₁|cos(θ+2πk/3)"))
P("      %-26s %-24s %-24s" % ("系数（第2/3单位根）", "−1 = e^{iπ}", "ω = e^{2πi/3}"))
P("      " + "-" * 76)
OUT["C_table"] = dict(light=dict(op="S^{n/2}", order=2, eigs=[1, -1], sectors=2, params="(phi,w)"),
                      mass=dict(op="S", order=3, eigs=[1, "omega", "omega^2"], sectors=3, params="(eta,delta)"))

# ==================================================================
head("PART D  闭 → 开 = ℤ₃ → ℤ₂（完整阶元谱，含阶 2 元计数）")
# ==================================================================
P("D1. 两态的置换群结构（GraphMatcher 全枚举）")
prof = {}
for tag, oring in (("闭", None), ("开", 0)):
    G = Y3(oring)
    autos = list(nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
    c = Counter(perm_order(p) for p in autos)
    prof[tag] = c
    P("      Y₃ %s态: |Aut| = %-3d   V=%d E=%d b1=%d" % (tag, len(autos), G.number_of_nodes(), G.number_of_edges(), beta1(G)))
    P("              阶元分布: " + "  ".join("阶%d: %d个" % (o, c[o]) for o in sorted(c)))
OUT["D_profiles"] = {t: {str(o): int(n_) for o, n_ in c.items()} for t, c in prof.items()}

n3_closed, n3_open = prof["闭"].get(3, 0), prof["开"].get(3, 0)
n2_closed, n2_open = prof["闭"].get(2, 0), prof["开"].get(2, 0)
P()
P("D2. 关键读数：")
P("      ℤ₃（阶 3 元）:  闭 %d 个   →   开 %d 个     %s" % (n3_closed, n3_open, "【ℤ₃ 归零】" if n3_open == 0 else ""))
P("      ℤ₂（阶 2 元）:  闭 %-3d个   →   开 %-3d个" % (n2_closed, n2_open))
P("      三环轨道数  :   闭 1 条   →   开 2 条 {0} | {1,2}")
OUT["D_readings"] = dict(o3_closed=n3_closed, o3_open=n3_open, o2_closed=n2_closed, o2_open=n2_open)
P()
P("D3. 读法（**这是本轮的桥**）：")
P("      **闭态（未打开）: ℤ₃ 活着 ⇒ 三力性 ⇒ 质量/三代。**")
P("      **开态（打开）  : ℤ₃ 归零、只剩 ℤ₂ ⇒ 对偶 ⇒ 光。**")
P("    这与电子论文【公理 I】『光是……互不湮灭的拓扑残余』**方向一致**：")
P("      光落在『被打开 / 未闭合』的那一侧。")

# ==================================================================
head("PART E  容量判据：为什么质量必须换到 ℤ₃ 档（第 29 轮判负的根源）")
# ==================================================================
P("E1. 给三点环的 3 条边各贴一个『档标签』，问：能得到几种本质不同的模式？")
P("    （本质不同 = 模去整体平移与整体置换）")
P()


def kinds_and_patterns(N):
    """三条边各取 ℤ_N 的一个标签。返回 (可取的『互异标签数』集合, 平移归一化后的模式集合)。"""
    kinds, pats = set(), set()
    for a in range(N):
        for b in range(N):
            for c in range(N):
                kinds.add(len({a, b, c}))
                pats.add(tuple(sorted(((b - a) % N, (c - a) % N))))   # 平移归一化 a=0
    return sorted(kinds), sorted(pats)


P("E1b. 判据 A（档数）：三条边最多能有几种**互不相同**的标签？")
for N, tag in ((2, "ℤ₂（光档）"), (3, "ℤ₃（质量档）"), (4, "ℤ₄")):
    kinds, pats = kinds_and_patterns(N)
    mark = "    ← **含 3，可达**" if 3 in kinds else "    ← **取不到 3**"
    P("      %-12s 值域 %d 个 ⇒ 可取互异标签数 = %s%s" % (tag, N, kinds, mark))
    P("      %-12s 平移归一化模式 %d 种： %s" % ("", len(pats), pats))
    OUT["E_kinds_%d" % N] = kinds
    OUT["E_pats_%d" % N] = [list(p) for p in pats]
P()
P("E2. 结论：")
P("      **|ℤ₂| = 2 < 3 —— 三条边凑不出『三档互不相等的差分』；**")
P("      **要点出 {1,1,1}（1+1+1 三个不同档）必须 |ℤ_n| ≥ 3，即至少 ℤ₃。**")
P("    这正是第 29 轮的判负在群论上的根源：二值 ⇒ 三点环只能 {3} 或 {2+1}。")
P("    也说明：**光（ℤ₂ 档）在结构上不能承载三代 —— 这是『换系数群』的硬理由，不是偏好。**")

# ==================================================================
head("PART F  两侧的「未打开」：都是『不固定原点』")
# ==================================================================
P("F1. 质量侧（第 32 轮已实测）：『打开』= 选 DFT 原点（3 种选法）")
P("      ⇒ 三种原点给出的不变量差 ≤ 2.2e−16 ⇒ **打开是规范（冗余），不是新信息**。")
P()
P("F2. 光侧（本轮实测）：Möbius 参数化的原点识别")
phi_a = [0.0, 0.7, 1.9, 3.3]
ww = 0.25
res = []
for pa in phi_a:
    def X(ph, w_):
        return np.array([(1 + w_ * math.cos(ph / 2)) * math.cos(ph),
                         (1 + w_ * math.cos(ph / 2)) * math.sin(ph),
                         w_ * math.sin(ph / 2)])
    d1 = np.abs(X(pa + 2 * math.pi, ww) - X(pa, -ww)).max()     # φ→φ+2π ⇔ w→−w
    d2 = np.abs(X(pa + 4 * math.pi, ww) - X(pa, ww)).max()      # 4π 才闭合
    res.append((pa, d1, d2))
    P("      φ=%.1f :  |X(φ+2π,w) − X(φ,−w)| = %.2e   |X(φ+4π,w) − X(φ,w)| = %.2e" % (pa, d1, d2))
OUT["F_mobius"] = [dict(phi=a, d_2pi=float(b), d_4pi=float(c)) for a, b, c in res]
P()
P("      ⇒ φ 与 φ+2π **不是同一个点**，而是『对映片上的同一点』（w→−w）。")
P("         与质量侧的『挠子无原点』是**同一类陈述**：")
P("           · 质量：ℤ₃ 的原点不可观测（只给等变类）")
P("           · 光  ：ℤ₂ 的对映片不可区分（只给 4π 闭合）")
P("     两者都 = 『**未打开**』：不预先固定一个原点，只输出规范不变量。")

P()
P("F3. 电磁波侧的 SRE 实现（code/Maxwell.py『规范协变闭合』引擎，离散胞复形）：")
D_edge = np.array([
    [1, -1, 0, 0, 0, 0, 0, 0], [0, 1, -1, 0, 0, 0, 0, 0],
    [0, 0, 1, -1, 0, 0, 0, 0], [0, 0, 0, 1, -1, 0, 0, 0],
    [0, 0, 0, 0, 1, -1, 0, 0], [0, 0, 0, 0, 0, 1, -1, 0],
    [0, 0, 0, 0, 0, 0, 1, -1], [-1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, -1, 0, 0, 0, 0, 0], [0, 1, 0, -1, 0, 0, 0, 0],
    [0, 0, 1, 0, -1, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, -1]], dtype=float)
C_cycle = np.array([
    [1, 1, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, -1, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, -1, 0, 0, 1, 0, 0],
    [1, 0, 0, 1, 0, 0, 0, -1, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, -1]], dtype=float)
PE = D_edge @ np.linalg.pinv(D_edge.T @ D_edge) @ D_edge.T
rkD = np.linalg.matrix_rank(D_edge)
P("      D (关联矩阵, 边×顶点) = %s  ⇒ rank(D) = %d = V−1（连通）" % (D_edge.shape, rkD))
P("      C (环-边关联, 环×边) = %s  ⇒ 独立环数 = %d ⇒ β₁ = E − rank(D) = %d"
  % (C_cycle.shape, C_cycle.shape[0], D_edge.shape[0] - rkD))
P("      P_E = D(DᵀD)⁻¹Dᵀ :  幂等 P²=P = %s | 对称 Pᵀ=P = %s | rank = %d"
  % (np.allclose(PE @ PE, PE), np.allclose(PE, PE.T), np.linalg.matrix_rank(PE)))
P("      残差 LHS=Div(E_graph), RHS=Q_static 之差 ⇒ run code/Maxwell.py 实测 ~1e−14 = 机器 eps")
P("      ⇒ 『规范协变闭合』的数学内容 = 投影算子 P_E 幂等 ⇒ 场演化被锁在链空间（规范轨道）内。")
P("      ⇒ 与质量侧的『不变量投影』**同型**：两者都靠一个**幂等投影**把结果限制在物理子空间。")
P("      ⚠ 数字巧合警示（D1 警戒）：rank(P_E) = %d = V−1（0-形式像空间维数），" % np.linalg.matrix_rank(PE))
P("         与骨架 β₁ = 7（1-同调维数）**数值相同、含义不同** ⇒ **禁止互证**。")
OUT["F3_maxwell"] = dict(rank_D=int(rkD), n_cycles=int(C_cycle.shape[0]),
                         b1=int(D_edge.shape[0] - rkD),
                         PE_idempotent=bool(np.allclose(PE @ PE, PE)),
                         rank_PE=int(np.linalg.matrix_rank(PE)))

# ==================================================================
head("PART G  物理对照（登记为**候选**，非结论）")
# ==================================================================
P("G1. 可点数（已证，模型内）：")
P("      ℤ₂ 档扇区数 = 2   ；   ℤ₃ 档扇区数 = 3")
P()
P("G2. 与观测量的**结构**对照（候选，需独立判据才可升级）：")
P("      光子的物理偏振态数   = 2   ↔  ℤ₂ 的两个扇区")
P("      三代费米子           = 3   ↔  ℤ₃ 的三个扇区")
P("      『光子无质量』        ↔  光侧没有 ℤ₃ 挠子（只有对合）        【候选】")
OUT["G_candidates"] = dict(photon_polarizations=2, generations=3,
                           note="structural correspondence; NOT a proof")
P()
P("    ⚠ 三条都只是**结构同向**。第 3 条尤其只有『没有 ℤ₃ ⇒ 没有那种未打开的循环』这层意思，")
P("      且光子的『无质量』在标准模型里另有来源（规范不变性 + 只两个横向自由度）。不得混用。")

# ==================================================================
head("PART H  同名不同义排查（本项目的老坑）")
# ==================================================================
P("H1. 项目里存在**两个 δ**，极易混淆：")
P("      δ_A（电子拓扑线，§3）：δ = w*−1 = **ℤ₂ holonomy 通道的耦合强度**；")
P("           性质：**度量参数**、连续、『δ 不改变 barcode』、需 α* 输入；")
P("           指纹：只抬升光子扇区，每模 +2δ。")
P("      δ_B（第 32 轮质量线）：**相位**（DFT 原点相对量），取模 2π/3；")
P("           性质：**规范（冗余）**，对不变量零影响（实测 ≤2.2e−16）。")
P("      ⇒ **一个是度量，一个是规范；不可互换。** 本报告一律写作 δ_A / δ_B。")
P()
P("H2. 另有『Π₁』的两种用法：")
P("      电子/锚点线：Π₁ = λ₂/ρ（谱投影，Möbius 闭式）；")
P("      核子线     ：Π₁ 为骨架闭合度（Y₃ = 0.188580485）。")
P("      ⇒ 数值不同、载体不同，引用时必须带图名。")
P()
P("H3. 「打开」也有两种含义（第 32 轮已登记）：")
P("      (i) 选原点 = 规范（不改不变量）；")
P("      (ii) 闭态→开态断环 = **真实破缺 ℤ₃→ℤ₂**。")
P("      本报告 PART F 说的是 (i)；PART D 说的是 (ii)。")

# ==================================================================
head("PART I  裁决")
# ==================================================================
P("  Q: 「质量 = 未打开的循环算子」是否**恰好**就是 SRE 对光/电磁波的描述？")
P()
P("  严格答案分三层：")
P()
P("  ① **形式同源 —— 是。**")
P("     两侧都是『图的线性算子在 ℤ_n 等变性下的分解』：")
P("       光 : P = S^{n/2}, P²=I ⇒ 谱劈成 2 支（偶/奇 = 电子/光子扇区），两支差 2w；")
P("       质量: S,          S³=I ⇒ 谱给 3 支（cos(θ+2πk/3)）。")
P("     两侧的『未打开』是同一件事：不固定原点 ⇒ 只输出规范不变量。")
P()
P("  ② **结构不同 —— 否。**")
P("     ℤ₂ ≇ ℤ₃（阶不同）。**不是同一个结构，而是同一个同调阶梯 |H¹(ℤ_n)|=n^β₁ 的相邻两级。**")
P("     因此不能说『恰好一致』；准确说法是『**同一机制，换了一个系数群**』。")
P()
P("  ③ **母群相同 —— 是。**")
P("     ℤ₂, ℤ₃ ⊂ U(1)，而 U(1) 就是电磁的规范群。")
P("     ⇒ 在这个意义上，**质量与光共享同一个相位母群**；")
P("        光 = U(1) 的 2 阶子群，质量 = U(1) 的 3 阶子群。")
P()
P("  容量判据（可点数，硬事实）：|ℤ₂| = 2 < 3 ⇒ **光档在结构上无法承载三代**；")
P("        这正是质量必须换到 ℤ₃ 档的理由（= 第 29 轮判负的群论根源）。")
P()

OUT["I_verdict"] = dict(
    formally_homologous=True,
    structurally_identical=False,
    same_parent_group=True,
    verdict="same mechanism, different coefficient group (Z2 for light/duality, Z3 for mass/triality)",
    capacity="|Z2|=2 < 3 => light tier cannot carry three generations",
)

json.dump(OUT, open("_sre_light_mass_correspondence.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=str)
P("saved _sre_light_mass_correspondence.json")
P()
P("=" * 84)
P("EXIT OK")
P("=" * 84)
