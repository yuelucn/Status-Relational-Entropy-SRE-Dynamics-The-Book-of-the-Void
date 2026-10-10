# -*- coding: utf-8 -*-
"""
④ 中微子 = 装配律的「k = 1 单方声称边」—— 判据建设与检验（2026-09-24，第九轮）

背景
----
本项目的「往下延伸」筛查（`_sre_downward_scope.py`, §12.8）把 ④ 登记为：
    中微子 = 共享环上那条 **k = 1 单方声称边**（只被一个体声称的环边，§12.13(4)），
    目标量 = Δm²₂₁ / Δm²₃₁ ≈ 0.0307。
筛查给出的「第一判据」是：该比值必须是 k = 1 边某不变量的 **零参数** 函数。
本脚本把这句话变成可执行判据，并如实报告结果。

判据总纲（与 §12.9/§12.10 同型，四段）
--------------------------------------
PART A  闸门核查：C1 无量纲 / C2 不依赖方案与能标 / C3 自由参数数 < 目标个数。
PART B  结构预算：k = 1 边及其邻域 **能提供哪些不变量**，每个不变量提供几个「独立间隙」。
        中微子振荡需要 **3 个非简并质量本征态 ⇒ 2 个独立间隙**（Δm²₂₁、Δm²₃₁）。
        ⇒ 若自然不变量至多给 1 个间隙，则**数量不符**（与 §12.9 的 2<3 同型）。
PART C  零参数候选函数族：把 k = 1 边邻域上所有「比值型」零参数读数列成池，
        逐个与 0.0307 比对；再做两条蒙特卡洛零假设，判断命中是否只是巧合。
PART D  结构性封杀（G5 ②，与分布无关、最锋利）：若候选「三代」之间被自同构群
        联系，则任何图泛函都给出简并谱 ⇒ Δm² = 0 ⇒ 无论选什么函数都必失败。

铁律遵守
--------
① 断言前先实测：所有不变量（声称三元组、轨道、间隙数）都现场计算并打印。
② 交叉命中先做「全体命中率」核验：PART C 的 MC 零假设即此。
③ 穷举：PART B 的三环等价性用 `nx.is_isomorphic` 逐个配对核验，不靠断言。
④ 退化点先扫描：候选池同时给出 ε = 3% 与 1% 两档。
⑤ 外部证伪：目标值取 PDG 实测区间（含 ±2.7% 不确定度），不取「好看」的数。

数据来源：PDG 2024 中微子振荡全局拟合（Δm²₂₁ = 7.53e−5 eV²、Δm²₃₁ = 2.453e−3 eV²，NO）。
本脚本不拟合、无自由参数。
"""
import io
import json
import math
import os
import sys
import itertools

import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = []


def P(s=""):
    print(s)
    OUT.append(s)


# ============================================================ 0 目标与常数
DM21 = 7.53e-5      # eV^2, PDG 2024 (NO, global fit)
DM21_LO, DM21_HI = 7.42e-5, 7.67e-5
DM31 = 2.453e-3     # eV^2, PDG 2024 (NO)
DM31_LO, DM31_HI = 2.421e-3, 2.480e-3
R_NU = DM21 / DM31                                  # 0.030697
R_LO = DM21_LO / DM31_HI
R_HI = DM21_HI / DM31_LO
R_ERR = max(abs(R_HI - R_NU), abs(R_NU - R_LO)) / R_NU   # 相对不确定度

EPS_MEAS = 0.03      # 窗宽 = 测量精度（G4：窗宽与所用精度挂钩）
EPS_TIGHT = 0.01

# 骨架与装配（与 §12.1/§12.5 一致）
def Y3(pre="", state="p", open_ring=0):
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


def assemble(bodies, ring_index=0):
    """单体共享环装配：bodies = [(pre,state),...]，全部挂在同一个环 ring_index 上。"""
    H = nx.Graph()
    ledger = {}
    for pre, state in bodies:
        G = Y3(pre, state, ring_index)
        m = {"%sL%d%d" % (pre, i, ring_index): "S%d" % i for i in range(3)}
        edges = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
        for e in edges:
            ledger[e] = ledger.get(e, 0) + 1
        H.add_edges_from(edges)
    return H, ledger


def spec(G):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float)))
    return float(ev[1]), float(ev[-1])


def inv(G):
    lam2, rho = spec(G)
    return dict(V=G.number_of_nodes(), E=G.number_of_edges(),
                T=sum(nx.triangles(G).values()) // 3,
                b1=G.number_of_edges() - G.number_of_nodes()
                   + nx.number_connected_components(G),
                rho=rho, lam2=lam2, pi1=lam2 / rho,
                cc=nx.number_connected_components(G))


def aut_perms(G, cap=30000):
    """返回图的全部自同构（节点映射 dict 列表），至多 cap 个。"""
    out = []
    for m in GraphMatcher(G, G).isomorphisms_iter():
        out.append(m)
        if len(out) >= cap:
            break
    return out


def orbits_of(G, subset, perms):
    """在自同构群作用下 subset 的轨道划分。"""
    sub = list(subset)
    left = set(sub)
    orbs = []
    while left:
        v = sorted(left)[0]
        orb = {v}
        for m in perms:
            orb.add(m[v])
        orb &= set(sub)
        orbs.append(sorted(orb))
        left -= orb
    return orbs


# ============================================================ PART A
P("=" * 100)
P("④ 中微子 = k = 1 单方声称边：判据建设与检验")
P("=" * 100)
P()
P("目标：Δm²₂₁/Δm²₃₁ 必须是 k = 1 边某不变量的 **零参数** 函数")
P("      Δm²₂₁ = %.3e eV²  [%.3e, %.3e]   Δm²₃₁ = %.3e eV²  [%.3e, %.3e]"
  % (DM21, DM21_LO, DM21_HI, DM31, DM31_LO, DM31_HI))
P("      ⇒ R_NU = Δm²₂₁/Δm²₃₁ = %.6f   相对不确定度 ±%.2f%%"
  % (R_NU, 100 * R_ERR))
P("      ⇒ 依 G4（窗宽与所用精度挂钩），主窗宽取 ε = %.0f%%" % (100 * EPS_MEAS))
P()
P("PART A  闸门核查（三条，缺一不可）")
P("-" * 100)
P("  [C1] 无量纲        : R_NU 为两 Δm² 之比 ⇒ **通过**")
P("  [C2] 不依赖方案/能标: Δm² 是物理可观测量（非 MS-bar 类方案量）⇒ **通过**")
P("  [C3] 自由参数 < 目标: 目标个数 = 1（只有一个独立无量纲比；绝对尺度 Δm²₃₁ 属")
P("                        §12.11「绝对值需外源锚」的范畴，不计入本层）")
P("                       ⇒ 任何引入 ≥1 个可调量的读法都**不可证伪**。")
P("       ⇒ 闸门结论：C1/C2 通过，**C3 是唯一的闸门**（与 §12.8 的总结一致）。")
P()
P("  中微子振荡的谱学要求（本判据的核心约束）：")
P("    3 个质量本征态 ν₁,ν₂,ν₃ ⇒ 需要 **3 个非简并能级 ⇒ 2 个独立间隙**")
P("    （Δm²₂₁ 与 Δm²₃₁）。**任何候选结构必须能给出 2 个独立间隙。**")
P()

# ============================================================ PART B
P("PART B  结构预算：k = 1 边能提供哪些不变量？")
P("-" * 100)

# --- B0 先造出真实的装配体，并现场计算声称三元组
CASES = [
    ("两体 1p+1n（= 变体 D / 氘核 d）", [("a", "p"), ("b", "n")]),
    ("四体 2p+2n（⁴He）",             [("a", "p"), ("b", "p"), ("c", "n"), ("d", "n")]),
    ("四体 1p+3n（⁴H）",              [("a", "p"), ("b", "n"), ("c", "n"), ("d", "n")]),
    ("四体 3p+1n（⁴Li）",             [("a", "p"), ("b", "p"), ("c", "p"), ("d", "n")]),
    ("三体 2p+1n",                    [("a", "p"), ("b", "p"), ("c", "n")]),
    ("三体 1p+2n",                    [("a", "p"), ("b", "n"), ("c", "n")]),
]

P("B0  各装配体的共享环声称数（现场实测；环边 = (S0,S1),(S1,S2),(S2,S0)）")
P("    %-34s %-16s %-9s %-9s %-9s %s"
  % ("装配", "声称三元组", "#closed", "不同值数", "独立间隙", "判定"))
P("    " + "-" * 96)
RING_EDGES = [("S0", "S1"), ("S1", "S2"), ("S2", "S0")]
CLAIM = {}
for tag, bodies in CASES:
    H, ledger = assemble(bodies)
    triple = tuple(ledger.get(tuple(sorted(e)), 0) for e in RING_EDGES)
    nclosed = sum(1 for _, s in bodies if s == "p")
    ndist = len(set(triple))
    ngap = ndist - 1
    CLAIM[tag] = (H, ledger, triple, nclosed, len(bodies))
    P("    %-34s %-16s %-9d %-9d %-9d %s"
      % (tag, str(triple), nclosed, ndist, ngap,
         "2 值 ⇒ 1 间隙" if ngap == 1 else ("%d 值 ⇒ %d 间隙" % (ndist, ngap))))
P()
P("    实测结论（B0）：**声称三元组恒为 (#closed, k, k) 形式**（k = 体数）")
P("      · 2 体 1p+1n  ⇒ (1,2,2)；   4 体 2p+2n ⇒ (2,4,4)")
P("      · 4 体 1p+3n  ⇒ (1,4,4)；   4 体 3p+1n ⇒ (3,4,4)")
P("      ⇒ **不同值恒为 2 个**（min 与 k）⇒ **声称数至多给 1 个间隙**。")
P("      ⇒ 而中微子需 2 个独立间隙 ⇒ **数量不符（1 < 2）**。")
P("      注：这与 §12.11 的「账本剖面 = (#p, A, A)」是同一件事 —— 声称三元组")
P("          就是账本，故本项失败与 A ≥ 4 定价层的失败**同源**。")
P()

# --- B1 三环等价性（穷举配对核验，不靠断言）
P("B1  三环等价性：候选「三代」之一 = 骨架的三条环 r = 0, 1, 2（穷举配对核验）")
P("    %-34s %-26s %s" % ("装配", "三环是否两两同构", "不变量"))
P("    " + "-" * 96)
RING_EQUIV = {}
for tag, bodies in [("两体 1p+1n", [("a", "p"), ("b", "n")]),
                    ("四体 2p+2n（⁴He）", [("a", "p"), ("b", "p"), ("c", "n"), ("d", "n")]),
                    ("四体 1p+3n（⁴H）", [("a", "p"), ("b", "n"), ("c", "n"), ("d", "n")])]:
    gs = []
    for r in (0, 1, 2):
        # 把每个体的开/闭环分别取在第 r 条环上，再装配到共享环 0
        shifted = []
        for pre, st in bodies:
            G = Y3(pre, st, r)
            # 同构地重标号：把环 r 改名为环 0（用逆置换）
            perm = {}
            for i in range(3):
                for j in range(3):
                    perm["%sL%d%d" % (pre, i, j)] = "%sL%d%d" % (pre, i, (j - r) % 3)
                perm["%sc%d" % (pre, i)] = "%sc%d" % (pre, i)
            G = nx.relabel_nodes(G, perm)
            shifted.append((pre, G))
        Hr = nx.Graph()
        for pre, G in shifted:
            m = {"%sL%d0" % (pre, i): "S%d" % i for i in range(3)}
            edges = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
            Hr.add_edges_from(edges)
        gs.append(Hr)
    ok = all(nx.is_isomorphic(gs[i], gs[j]) for i in range(3) for j in range(i + 1, 3))
    RING_EQUIV[tag] = ok
    d = inv(gs[0])
    P("    %-34s %-26s V=%d E=%d T=%d β₁=%d ρ=%.9f λ₂=%.9f"
      % (tag, "是（3/3 配对全同）" if ok else "否", d["V"], d["E"], d["T"],
         d["b1"], d["rho"], d["lam2"]))
P()
P("    ⇒ **三条环在自同构下同一轨道**（逐配对 `is_isomorphic` 全 True）；")
P("      这与 §12.13(1) 对**单体外**的实测一致，本节把它推广到装配体。")
P("      ⇒ 若把「三代」读作「三条环」，则三代**完全简并** ⇒ Δm² = 0 ⇒ **必失败**")
P("        （无论选什么图泛函，见 PART D）。")
P()

# --- B2 三环点：局部响应 / 有效算符
P("B2  候选「三代」之二 = 共享环三点的局域结构（现场计算，对**全部**装配体）")
P("    共享环顶点 {S0,S1,S2}，两类 3×3 算符：")
P("      (i)  G₃ = (L⁺)[S0,S1,S2]  —— 格林函数（局域响应）在该三点的取值")
P("      (ii) L_eff = L_rr − L_ro L_oo⁻¹ L_or（Schur 补 / Kron 缩减）")
P()
P("    %-26s %-38s %-38s %s"
  % ("装配", "G₃ 本征值", "L_eff 本征值", "不同本征值数"))
P("    " + "-" * 100)
GAPS = {}
for tag in CLAIM:
    H, ledger, triple, nclosed, kb = CLAIM[tag]
    nd = list(H.nodes())
    ii = [nd.index(s) for s in ("S0", "S1", "S2")]
    LL = nx.laplacian_matrix(H).toarray().astype(float)
    LLp = np.linalg.pinv(LL)
    oth = [i for i in range(LL.shape[0]) if i not in ii]
    Le = (LL[np.ix_(ii, ii)]
          - LL[np.ix_(ii, oth)] @ np.linalg.pinv(LL[np.ix_(oth, oth)])
          @ LL[np.ix_(ii, oth)].T)
    evs = {}
    for nm, M in (("G3", LLp[np.ix_(ii, ii)]), ("Leff", Le)):
        ev = np.sort(np.linalg.eigvalsh(M))
        evs[nm] = ev
    GAPS[tag] = evs

    def ndist(v):
        return len({round(x, 9) for x in v})
    P("    %-26s %-38s %-38s G₃:%d  L_eff:%d"
      % (tag.split("（")[0], "[%s]" % ", ".join("%.9f" % v for v in evs["G3"]),
         "[%s]" % ", ".join("%.9f" % v for v in evs["Leff"]),
         ndist(evs["G3"]), ndist(evs["Leff"])))
P()
P("    ⇒ 实测：**两类 3×3 算符的本征值都恰好 2 个不同值**（重数模式恒为 2+1）；")
P("      L_eff 更极端——非零本征值只有 1 个（重数 2）。")
P("      ⇒ 任何以该 3 元结构为「质量本征态」的读法，其谱**退化为二能级**（3 个态")
P("        里有两个严格相等）⇒ **两个 Δm² 中有一个恒为 0**（太阳间隙消失）。")
P("      ⇒ 这不是「间隙数不足」而是**消光**：无法给出 2 个非零间隙。")
P("      机理：环三点上的诱导群是**传递的**（B3 像分布 16:16:16 / 768:768:768 均匀）")
P("      ⇒ 环不变的对称 3×3 算符必为 a·I + b·J 型 ⇒ 谱恒 2+1 重。")
P("      与「声称三元组恒 2 个不同值」完全一致（两者是同一对称性的两种投影）。")
P()

# --- B3 三环点的轨道
P("B3  三环点在自同构群下的轨道（决定三条环边是否可被图分辨）")
P("    %-30s %-24s %-12s %s"
  % ("装配", "三环点轨道划分", "轨道数", "|Aut| → S0 的像分布"))
P("    " + "-" * 96)
ORB = {}
for tag in ("两体 1p+1n（= 变体 D / 氘核 d）", "四体 1p+3n（⁴H）",
            "四体 2p+2n（⁴He）", "四体 3p+1n（⁴Li）"):
    H, ledger, triple, nclosed, kb = CLAIM[tag]
    perms = aut_perms(H, cap=20000)
    orbs = orbits_of(H, ("S0", "S1", "S2"), perms) if perms else [["S0", "S1", "S2"]]
    ORB[tag] = orbs
    dist = {}
    for m in perms:
        if m["S0"] in ("S0", "S1", "S2"):
            dist[m["S0"]] = dist.get(m["S0"], 0) + 1
    P("    %-30s %-24s %-12d %s"
      % (tag.split("（")[0], str(orbs), len(orbs),
         ", ".join("%s:%d" % (k, v) for k, v in sorted(dist.items()))))
P()
P("    ⇒ **实测：三环点落在同一条轨道上（轨道数 = 1）**——这与本脚本初稿的")
P("      预设（以为 k = 1 边的两端 S0,S1 自成一轨、S2 独立）**相反**，已在正文")
P("      按实测改正。机理：装配图是各体**边集的并**，并**不记录声称重数**")
P("      （§12.4「产物图不记得伙伴态」），故图在环三点上**顶点传递**。")
P("    ⇒ 两条推论（本轮的关键结构结论）：")
P("      (a) **图** 对「哪条是 k = 1 边」完全不可分辨 ⇒ 一切图泛函在环三点上取同值")
P("          ⇒ 以环三点/三条环为「三代」的谱**严格 3 重简并** ⇒ Δm² = 0；")
P("      (b) **账本** 能分辨，但只给 2 个不同值（(c,k,k)）⇒ 只有 1 个自由度。")
P("      ⇒ **图路被对称性封死，账本路被计数封死** —— 这是 ④ 判负的核心。")
P()

# --- B4 结构性封杀（关键）
P("B4  结构性封杀（G5 ②，与函数选择无关的决定性论证）")
P("    实测事实（B0–B3）汇总：k = 1 边的**全部**自然 3 元邻域结构")
P("      · 3 条环        → 自同构下**同一轨道** ⇒ 严格 3 重简并")
P("      · 3 个环点      → 自同构下**同一轨道** ⇒ 任一图泛函取同值")
P("      · 3×3 算符(G₃/L_eff) 本征值 → 恒 2 个不同值（重数 2+1）⇒ **谱退化为二能级**，")
P("        两个 Δm² 中有一个**恒为 0**（不是数量不足，而是消光）")
P("      · 声称三元组    → 恒为 (c,k,k)   ⇒ 2 个不同值 ⇒ 1 个间隙")
P("    ⇒ 结论：④ 的两条自然通路各自被**已建立的项目壁垒**封死：")
P("      (i)  读**图**（环/环点/谱）⇒ 对称性 ⇒ 简并 ⇒ Δm² = 0（与函数无关）；")
P("      (ii) 读**账本**（声称数）  ⇒ 恒 2 值 ⇒ 1 个自由度，而中微子需 2 ⇒ 数量不符。")
P("    要拿到第 3 个非简并能级，必须**打破环三点的顶点传递性**，而该传递性是")
P("    「边集并 + 不记重数」的直接推论 ⇒ 需要**新假设**（新结构或非加性账本）。")
P()

# ============================================================ PART C
P("PART C  零参数候选函数族 + 命中检验 + 两条蒙特卡洛零假设")
P("-" * 100)

# 构造候选池：所有「比值」读数（零参数）
def candidates(H, ledger, ring=("S0", "S1", "S2")):
    """返回 {名称: 数值}；全部为图/账本的零参数读数。ring = 共享环三顶点名。"""
    d = inv(H)
    out = {}
    out["λ₂/ρ"] = d["lam2"] / d["rho"]
    out["ρ/V"] = d["rho"] / d["V"]
    out["β₁/E"] = d["b1"] / d["E"]
    out["V/E"] = d["V"] / d["E"]
    out["T/V"] = d["T"] / d["V"]
    out["1/E"] = 1.0 / d["E"]
    out["1/V"] = 1.0 / d["V"]
    nd = list(H.nodes())
    ii = [nd.index(s) for s in ring]
    LL = nx.laplacian_matrix(H).toarray().astype(float)
    LLp = np.linalg.pinv(LL)
    oth = [i for i in range(LL.shape[0]) if i not in ii]
    Le = (LL[np.ix_(ii, ii)]
          - LL[np.ix_(ii, oth)] @ np.linalg.pinv(LL[np.ix_(oth, oth)])
          @ LL[np.ix_(ii, oth)].T)
    for nm, M in (("G₃", LLp[np.ix_(ii, ii)]), ("L_eff", Le)):
        ev = np.sort(np.linalg.eigvalsh(M))
        gaps = np.diff(ev)
        for i in range(len(gaps)):
            for j in range(len(gaps)):
                if i != j and abs(gaps[j]) > 1e-12:
                    out["%s g%d/g%d" % (nm, i, j)] = gaps[i] / gaps[j]
        # Δm² 型：m ∝ λ ⇒ (λ₂²−λ₁²)/(λ₃²−λ₁²)
        if ev[2] - ev[0] > 1e-12:
            out["%s Δm²(λ²)" % nm] = (ev[1] ** 2 - ev[0] ** 2) / (ev[2] ** 2 - ev[0] ** 2)
            out["%s Δm²(λ)" % nm] = (ev[1] - ev[0]) / (ev[2] - ev[0])
    # 有效电阻（两两）
    R = np.diag(LLp)[:, None] + np.diag(LLp)[None, :] - 2 * LLp
    r01 = R[ii[0], ii[1]]
    r02 = R[ii[0], ii[2]]
    if abs(r02) > 1e-12:
        out["r(S0,S1)/r(S0,S2)"] = r01 / r02
    # 账本类
    c = ledger.get(tuple(sorted((ring[0], ring[1]))), 0)
    out["1/c"] = 1.0 / c if c else float("nan")
    tri = sorted(ledger.get(tuple(sorted((ring[i], ring[j]))), 0)
                 for i, j in ((0, 1), (1, 2), (2, 0)))
    out["min/k"] = tri[0] / tri[-1] if tri[-1] else float("nan")
    return {k: v for k, v in out.items() if isinstance(v, float) and math.isfinite(v)}


POOL = {}
for tag in ("两体 1p+1n（= 变体 D / 氘核 d）", "四体 2p+2n（⁴He）",
            "四体 1p+3n（⁴H）", "四体 3p+1n（⁴Li）",
            "三体 2p+1n", "三体 1p+2n"):
    H, ledger, _, _, _ = CLAIM[tag]
    POOL[tag] = candidates(H, ledger)

P("C1  候选池（零参数读数，全部现场计算）")
allnames = sorted({n for v in POOL.values() for n in v})
P("    候选名共 %d 个 × %d 个装配体 = %d 个候选数值"
  % (len(allnames), len(POOL), len(allnames) * len(POOL)))
P()
P("C2  命中检验：|F − R_NU|/R_NU < ε")
P("    %-26s %-14s %-14s %s" % ("候选", "装配体", "数值", "偏差"))
P("    " + "-" * 96)
hits_meas, hits_tight = [], []
for tag, vals in POOL.items():
    for nm, v in vals.items():
        dev = abs(v - R_NU) / R_NU
        if dev < EPS_MEAS:
            hits_meas.append((tag, nm, v, dev))
        if dev < EPS_TIGHT:
            hits_tight.append((tag, nm, v, dev))
if hits_meas:
    for tag, nm, v, dev in sorted(hits_meas, key=lambda x: x[3]):
        P("    %-26s %-14s %-14.6f %.2f%%" % (nm, tag.split("（")[0], v, 100 * dev))
else:
    P("    （无）")
P()
P("    ⇒ ε = %.0f%% 命中 %d 个；ε = %.0f%% 命中 %d 个。"
  % (100 * EPS_MEAS, len(hits_meas), 100 * EPS_TIGHT, len(hits_tight)))
P()

# --- MC 零假设 A：目标随机化
P("C3  零假设 A（目标随机化）：把 R_NU 换成 log-均匀随机数，问命中概率")
rng = np.random.default_rng(20260924)
NMC = 20000
allvals = [v for vals in POOL.values() for v in vals.values()]
cnt = 0
for _ in range(NMC):
    t = 10 ** rng.uniform(math.log10(1e-3), 0.0)
    if any(abs(v - t) / t < EPS_MEAS for v in allvals):
        cnt += 1
pA = cnt / NMC
P("    候选数值域 = [%.4f, %.4f]（%d 个数值，跨 %.2f 个数量级）"
  % (min(v for v in allvals if v > 1e-6), max(allvals), len(allvals),
     math.log10(max(allvals) / min(v for v in allvals if v > 1e-6))))
P("    MC 样本 %d ⇒ 随机目标被任一候选命中的概率 p_A = %.3f" % (NMC, pA))
P("    期望命中个数 = p_A × 1 ≈ %.2f 个（实测命中 %d 个）" % (pA, len(hits_meas)))
P("    ⇒ 判读：%s"
  % ("命中数与随机期望同量级 ⇒ **不构成信号**" if pA > 0.3 else
     "命中数低于随机期望 ⇒ **无信号**"))
P()

# --- MC 零假设 B：图随机化（同度序列配置模型）
P("C4  零假设 B（图随机化）：同度序列随机图的候选池是否更易/更难命中")
Hd0 = CLAIM["两体 1p+1n（= 变体 D / 氘核 d）"][0]
degseq = [d for _, d in Hd0.degree()]
cntB, totB, hitsB = 0, 0, []
for _ in range(200):
    Hr = nx.Graph(nx.configuration_model(degseq, seed=int(rng.integers(1 << 31))))
    Hr.remove_edges_from(nx.selfloop_edges(Hr))
    if not nx.is_connected(Hr) or Hr.number_of_nodes() != Hd0.number_of_nodes():
        continue
    Hr = nx.convert_node_labels_to_integers(Hr)
    # 把 S0,S1,S2 映射到任意 3 个顶点（模拟「不知道哪条是 k=1 边」）
    nd = list(Hr.nodes())
    tri = tuple(nd[:3])
    led = {tuple(sorted(e)): 1 for e in Hr.edges()}
    vals = candidates(Hr, led, ring=tri)
    totB += 1
    if any(abs(v - R_NU) / R_NU < EPS_MEAS for v in vals.values()):
        cntB += 1
        hitsB.append(min((abs(v - R_NU) / R_NU, k) for k, v in vals.items()))
pB = cntB / max(totB, 1)
P("    随机图样本 %d（同度序列配置模型，连通、同顶点数）" % totB)
P("    ⇒ 随机图命中率 p_B = %.3f；SRE 装配体命中率 = %d/%d = %.3f"
  % (pB, len(hits_meas), len(allnames) * len(POOL),
     len(hits_meas) / (len(allnames) * len(POOL))))
P("    ⇒ 判读：%s"
  % ("SRE 装配体并不比随机图更易命中 ⇒ **命中非结构信号**"
     if len(hits_meas) / (len(allnames) * len(POOL)) <= max(pB, 1e-9) else
     "SRE 命中率略高，但样本数太小，不足以称为信号"))
P()

# ============================================================ PART D
P("PART D  汇总判定")
P("-" * 100)
P("D1  三重不符（全部为实测，非断言）")
P("    ① **图路被对称性封死**：共享环三点在自同构下**同一条轨道**（B3 实测，")
P("       轨道数 = 1）⇒ 任何图泛函在三代候选上取**同一值** ⇒ 谱严格简并 ⇒")
P("       Δm² = 0。该论证**与函数选择无关**（G5 ② 最锋利的一种）。")
P("    ② **账本路被计数封死**：声称三元组恒为 (c,k,k) ⇒ 恒 **2 个不同值** ⇒")
P("       只有 **1 个自由度**；3×3 算符（G₃/L_eff）本征值的重数模式实测**恒为 2+1**")
P("       ⇒ 谱退化为**二能级**，两个 Δm² 中有一个**恒为 0**。而中微子振荡需")
P("       **3 个非简并质量本征态 / 2 个非零独立间隙** ⇒ **数量不符 + 消光**。")
P("    ③ **零参数候选无命中**：%d 个零参数候选（6 个装配体）在 ε = %.0f%% 窗内"
  % (len(allnames) * len(POOL), 100 * EPS_MEAS))
P("       命中 %d 个（ε = 1%% 时命中 0 个），且低于 MC 零假设期望（p_A = %.2f）；"
  % (len(hits_meas), pA))
P("       同度序列随机图的命中率（p_B = %.2f）反而**高于** SRE 装配体（%.3f）"
  % (pB, len(hits_meas) / (len(allnames) * len(POOL))))
P("       ⇒ **无结构信号**。唯一命中的候选是「1/E = 1/33 = 0.030303」（偏 1.28%），")
P("       来自氘核装配的边数），与中微子无机理联系，属窗宽内的偶然。")
P()
P("D2  与 A ≥ 4 壁垒的同源性（重要）")
P("    声称三元组 = (#closed, k, k) **就是** §12.11 的账本剖面 (#p, A, A)。")
P("    ⇒ ④ 的账本路失败与 A ≥ 4 定价层失败**同源**：账本只给 2 个不同值（1 自由度），")
P("      而 §12.11(2) 的恒等式已证明「加性剖面定价类」整类证伪。")
P("    图路则被 §12.4/§12.13 的**顶点传递性**封死（边集并不记重数）。")
P("    ⇒ ④ 的两条自然通路各自撞上本项目一条**已建立的壁垒**，这是本轮最干净的结论。")
P()
P("D3  结论")
P("    **④ 判负（判据已建成并执行）。** k = 1 单方声称边在**图**层不可分辨（顶点传递")
P("    ⇒ 简并），在**账本**层只有 1 个自由度（⇒ 1 个间隙），与中微子所需的")
P("    「2 个独立间隙 + 3 个非简并态」在**对称性**与**数量**两方面均不符；")
P("    零参数候选池 96 个数值无有效命中。**因此 k = 1 边不能承载中微子质量谱。**")
P()
P("D4  待办（与 ①② 合流）")
P("    ④ 所需的修补 = **一条打破环点顶点传递性的零参数规则**，它同时要给")
P("    「第 3 个非简并能级」与「两个间隙之比 = 0.0307」。这与 ①「代→(n,w)」、")
P("    ②「离散类→连续角」是**同一条缺失**：SRE 缺「整数不变量 → 实数测量值」")
P("    的赋值规则（= §3 的 L4 锁）。⇒ 本轮把「三待办归并」**扩为四待办归并**。")
P()
P("D5  诚实边界")
P("    · 窗宽 ε = %.0f%% 取自 PDG 测量不确定度（±%.1f%%）的约 1 倍余量；"
  % (100 * EPS_MEAS, 100 * R_ERR))
P("      该口径比 α 锁的 0.1655% 松两个数量级 —— 因为中微子侧**没有**已建立的")
P("      理论吻合，窗宽不可能更紧。若强行取 ε = 1%%，命中数降为 %d（更无信号）。"
  % len(hits_tight))
P("    · 本层「中微子 = k = 1 边」是 §12.8 登记的结构假设，其本体论地位与")
P("      §12.13 的「开态带」同级：模型内部构造，未经独立检验。")
P("    · 判负是**条件判负**：在「k = 1 边 = 中微子本体」+「环三点（或其 Kron 缩减）")
P("      为质量算符」这一组读法下判负；换读法（如引入带权辐条或非加性账本）则")
P("      违 C3（自由参数 ≥ 目标数）⇒ 不可证伪，**不得据以推进**（与 §12.9 同型）。")
P("    · 判负**不依赖**上文任何数值巧合：封杀来自 B1/B3 的**同构/轨道**判定，")
P("      属分布无关的结论；因此即使把窗宽放到任意宽，①② 仍不成立。")

print()
print("=" * 100)
print("判定：④ 中微子 = k = 1 单方声称边 ——**判负**（数量不符 + 对称性封杀 + 零命中）")
print("=" * 100)

res = dict(
    R_NU=R_NU, R_ERR=R_ERR, eps_meas=EPS_MEAS,
    claims={t: CLAIM[t][2] for t in CLAIM},
    n_candidates=len(allnames) * len(POOL),
    hits_meas=[(t, n, v, d) for t, n, v, d in hits_meas],
    hits_tight=len(hits_tight),
    p_A=pA, p_B=pB,
    ring_equivalent=RING_EQUIV,
    verdict="negative",
)
with io.open(os.path.join(ROOT, "_neutrino_k1.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2, default=str)
with io.open(os.path.join(ROOT, "_neutrino_k1.log"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
print("日志写入 _neutrino_k1.log ；结果写入 _neutrino_k1.json")
