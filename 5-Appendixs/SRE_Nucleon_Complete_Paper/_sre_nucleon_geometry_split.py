# -*- coding: utf-8 -*-
"""
A = 4 的区分能否落在"空间结构"（MDS 涌现几何）里？

背景（论文口径）：
  §12.11(1) 结构层不可行 —— ⁴He/⁴H/⁴Li 按共享环规则构造后互为**同构**，
             任何图泛函（ρ、λ₂、T、β₁、|Aut|、全谱）在三者上取同值。
  §12.12(2) λ 不可由 SRE 导出 —— 其中第一条排除理由是：
             "常数惩罚会同时落在已定标的 ⁴He 上，使四条定标方程不再被 ψ(1..4) 满足
              —— 定标自身被破坏"。
             该理由作用于**惩罚项**，不作用于**图量本身**。

待检验命题：
  A = 4 的区分不在图的不变量里，而在图的**几何像**里 —— 三者图同构，
  但 MDS 反演出的形状不同。

为什么这不是 §12.12 已经排除的那类输入：
  · 不是图不变量（不取同构类上的常数） -> 不破坏 ⁴He 定标；
  · 不是 (A, #p) 的**加性**函数        -> 绕过 §12.11(2) 的恒等式。
  它是"图泛函的几何像"：输入是图派生的距离矩阵 D，输出是形状。

方法（复用 _sre_mds_inversion.py 的管线，不重写 MDS）：
  1. 用论文的共享环规则构造 ⁴He(2p2n)、⁴H(1p3n)、⁴Li(3p1n) 三个产物图
     （复用 _sre_nucleon_interference.py 的构造逻辑，见下 validate_graphs()）。
  2. 由**账本**给边赋权重：共享环上第 i 条边的声称数 k_i ∈ {#p, A, A}。
     三个权重方案（都只用到账本，不含坐标）：
       方案 T（拓扑）  : w = 1                （纯拓扑，无账本信息）
       方案 K（声称赞本）: w = 1/k            （声称数越多 -> 关系越近）
       方案 L（对数）  : w = 1/log2(1+k)      （弱化压缩）
  3. Floyd 求关系距离 D（只沿边，不喂任何坐标）-> 古典 MDS 反演 -> 形状 X。
  4. 判据：
     (a) 三个同构图在方案 T 下是否给出相同形状？（应为是 —— 同构图同 D）
     (b) 在方案 K/L 下是否给出**不同**形状？（若是，区分即有几何承载）
     (c) 形状差异是否**可靠**（对顶点重标号不变）？用随机重标号 N=200 次检验
         形状距离分布，与 ⁴He 自身重标号的基线对照。
  5. 另报：三者的 D 矩阵是否不同（D 已带账本信息，这一步是必要条件），
     以及各自"共享环三点"的形状几何（这三点是 §12.5 的最低模零振幅点）。

诚实边界：
  · 若方案 T 下三者形状即不同 -> 说明构造有误（同构图必有同 D），须先查 bug。
  · 若方案 K/L 下形状不同，但随机重标号后差异不显著 -> 判为"不构成可靠区分"。
  · MDS 是**有损同态**（见 SRE_MDS_Inversion_Real_Graph.md §3）：
    形状差异存在不等于该差异在现实中可观测。
"""

import sys, json, math, random
from collections import Counter
import numpy as np
import networkx as nx

HERE = r"C:\mywork\vasp"
sys.path.insert(0, HERE)
from _p3_p1a_final_scaffolds import mds_coords_from_dmat

random.seed(20260923)
np.random.seed(20260923)

# ══════════════════════════════════════════════════════════════════════
# (0) 核子骨架与共享环构造 —— 与论文 §12.5 / §12.13 口径一致
# ══════════════════════════════════════════════════════════════════════
def Y3(pre, state="p", open_ring=0):
    """单体骨架 Y₃⋉△₃：3 个股心 c{i} + 9 个叶点 L{i}{j}（i=股号, j=环号）。
    state='n' 时删除环边 (L0r, L1r)。"""
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


def shared_ring(bodies, r=0):
    """k 体共享环拼接：把各体的环 r 三顶点合并为 S0,S1,S2。
    返回 (合并图 H, 账本 ledger{e: 声称数}, 顶点映射 m)。
    注意：r 必须传给 Y3 —— 否则出现"打开环 0 却合并环 r"的错图。"""
    H = nx.Graph()
    ledger = {}
    m = {}
    for pre, state in bodies:
        G = Y3(pre, state, r)
        mm = {}
        for i in range(3):
            mm["%sL%d%d" % (pre, i, r)] = "S%d" % i
        m[pre] = mm
        edges = {tuple(sorted((mm.get(u, u), mm.get(v, v)))) for u, v in G.edges()}
        for e in edges:
            ledger[e] = ledger.get(e, 0) + 1
        H.add_edges_from(edges)
    return H, ledger, m


BODIES = {
    "4He": [("p1", "p"), ("p2", "p"), ("n1", "n"), ("n2", "n")],
    "4H":  [("p1", "p"), ("n1", "n"), ("n2", "n"), ("n3", "n")],
    "4Li": [("p1", "p"), ("p2", "p"), ("p3", "p"), ("n1", "n")],
}

GRAPH = {}
LEDGER = {}
for name, bodies in BODIES.items():
    H, led, _ = shared_ring(bodies, r=0)
    GRAPH[name] = H
    LEDGER[name] = led

print("=" * 84)
print("(1) 前提复核：三个 A=4 产物图是否互为同构（§12.11(1)）")
print("=" * 84)
inv = {}
for name, H in GRAPH.items():
    rho = max(nx.laplacian_spectrum(H))
    l2 = sorted(nx.laplacian_spectrum(H))[1] if H.number_of_nodes() > 1 else 0.0
    inv[name] = dict(V=H.number_of_nodes(), E=H.number_of_edges(),
                     T=sum(nx.triangles(H).values()) // 3,
                     beta1=H.number_of_edges() - H.number_of_nodes() + nx.number_connected_components(H),
                     aut=len(list(nx.algorithms.isomorphism.GraphMatcher(H, H).isomorphisms_iter())),
                     rho=round(rho, 9), lam2=round(l2, 9))
    print("  %-4s V=%d E=%d T=%d beta1=%d |Aut|=%-4d rho=%.9f lam2=%.9f"
          % (name, inv[name]["V"], inv[name]["E"], inv[name]["T"],
             inv[name]["beta1"], inv[name]["aut"], inv[name]["rho"], inv[name]["lam2"]))

pairs = [("4He", "4H"), ("4He", "4Li"), ("4H", "4Li")]
print("\n  同构判定：")
for a, b in pairs:
    gm = nx.algorithms.isomorphism.GraphMatcher(GRAPH[a], GRAPH[b])
    print("    %-4s ~ %-4s : %s" % (a, b, gm.is_isomorphic()))

print("\n  账本剖面（共享环三边的声称数）：")
PROFILE = {}
for name in BODIES:
    sd = [LEDGER[name][tuple(sorted(("S%d" % i, "S%d" % j)))]
          for i, j in ((0, 1), (1, 2), (2, 0))]
    PROFILE[name] = sorted(sd, reverse=True)
    print("    %-4s -> %s" % (name, tuple(sd)))

# ══════════════════════════════════════════════════════════════════════
# (2) 三套边权方案（全部只依赖账本，不含任何坐标）
# ══════════════════════════════════════════════════════════════════════
SCHEMES = {
    "T_topology": lambda k: 1.0,                       # 纯拓扑：不含账本
    "K_ledger":   lambda k: 1.0 / k,                   # 声称数越多 -> 关系越近
    "L_log":      lambda k: 1.0 / math.log2(1.0 + k),  # 对数弱化
}


def floyd_from_graph(H, ledger, wfun):
    """只沿图边求最短路径（不喂坐标）。边权 = wfun(声称数)。"""
    nodes = sorted(H.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    D = np.full((n, n), 1e9)
    np.fill_diagonal(D, 0.0)
    for u, v in H.edges():
        e = tuple(sorted((u, v)))
        w = wfun(ledger.get(e, 1))
        D[idx[u], idx[v]] = D[idx[v], idx[u]] = w
    for kk in range(n):
        D = np.minimum(D, D[:, kk, None] + D[None, kk, :])
    return D, nodes


def shape_signature(H, ledger, wfun, ndim=3):
    """MDS 反演 -> 形状。返回 (D, X, 形状不变量)。"""
    D, nodes = floyd_from_graph(H, ledger, wfun)
    X = mds_coords_from_dmat(D, ndim=ndim)
    # 形状相似度用的"形状指纹"：顶点两两距离分布的百分位（对刚体/平移不变）
    pd = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1))
    iu = np.triu_indices(len(nodes), 1)
    pct = np.percentile(pd[iu], [10, 25, 50, 75, 90])
    return D, X, pct


print("\n" + "=" * 84)
print("(2) 方案 T（纯拓扑）下三者形状比较 —— 对照组")
print("=" * 84)
for name in BODIES:
    D, X, pct = shape_signature(GRAPH[name], LEDGER[name], SCHEMES["T_topology"])
    print("  %-4s  shape_percentiles = %s" % (name, np.round(pct, 6)))

Ds = {}
for name in BODIES:
    Ds[name] = shape_signature(GRAPH[name], LEDGER[name], SCHEMES["T_topology"])[0]
print("\n  D 矩阵逐元素最大差：")
for a, b in pairs:
    print("    %-4s vs %-4s : %.3e" % (a, b, np.abs(Ds[a] - Ds[b]).max()))

# ══════════════════════════════════════════════════════════════════════
# (3) 核心检验：账本加权的 D 是否把三者分开
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 84)
print("(3) 核心检验：账本加权后 D 是否不同、形状是否不同")
print("=" * 84)

SUM = {}
for sname, wfun in SCHEMES.items():
    print("\n  ── 方案 %s ──" % sname)
    dd = {}
    pp = {}
    xx = {}
    for name in BODIES:
        D, X, pct = shape_signature(GRAPH[name], LEDGER[name], wfun)
        dd[name] = D
        pp[name] = pct
        xx[name] = X
    # D 差异
    print("     D 矩阵最大逐元素差（三对）：")
    dmax = max(np.abs(dd[a] - dd[b]).max() for a, b in pairs)
    for a, b in pairs:
        print("       %-4s vs %-4s : %.6e" % (a, b, np.abs(dd[a] - dd[b]).max()))
    # 形状差异（距离分位数向量）
    print("     形状分位数向量：")
    for name in BODIES:
        print("       %-4s %s" % (name, np.round(pp[name], 6)))
    smax = max(np.abs(pp[a] - pp[b]).max() for a, b in pairs)
    print("     形状指纹最大差 = %.6e" % smax)
    SUM[sname] = dict(dmax=float(dmax), smax=float(smax),
                      pct={n: [float(x) for x in pp[n]] for n in BODIES},
                      X={n: xx[n].tolist() for n in BODIES})

# ══════════════════════════════════════════════════════════════════════
# (4) 可靠性检验：顶点重标号不变性
#    同构图在同 D 下必给同形状；但 D 由**带标签的**账本决定，
#    须确认差异不是重标号假象。
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 84)
print("(4) 可靠性检验：随机重标号下的形状稳定性（N=200）")
print("=" * 84)


def relabeled_shape(H, ledger, wfun, seed):
    """对图做随机顶点重标号（保持账本随边同移），再算形状指纹。
    重标号应**不改变**形状指纹（MDS 对顶点顺序：仅当 D 不变时；此处 D 随标签变，
    故我们考察的是"三者在**固定规范标签**下的可比性"是否稳健）。"""
    rng = random.Random(seed)
    nodes = sorted(H.nodes())
    perm = nodes[:]
    rng.shuffle(perm)
    mp = dict(zip(nodes, perm))
    H2 = nx.relabel_nodes(H, mp)
    led2 = {}
    for e, k in ledger.items():
        led2[tuple(sorted((mp[e[0]], mp[e[1]])))] = k
    D, X, pct = shape_signature(H2, led2, wfun)
    return pct


for sname in ("K_ledger", "L_log"):
    print("\n  ── 方案 %s ──" % sname)
    for name in BODIES:
        base = np.array(SUM[sname]["pct"][name])
        devs = []
        for s in range(200):
            pct = relabeled_shape(GRAPH[name], LEDGER[name], SCHEMES[sname], s)
            devs.append(np.abs(np.array(pct) - base).max())
        devs = np.array(devs)
        print("     %-4s 重标号后指纹偏离: max=%.6e  median=%.6e"
              % (name, devs.max(), np.median(devs)))
    # 跨体差异 vs 重标号噪声
    cross = np.abs(np.array(SUM[sname]["pct"]["4He"]) - np.array(SUM[sname]["pct"]["4H"])).max()
    print("     跨体形状差（4He vs 4H） = %.6e" % cross)

# ══════════════════════════════════════════════════════════════════════
# (5) 共享环三点的形状（§12.5 最低模零振幅点）
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 84)
print("(5) 共享环三点 S0,S1,S2 的几何（最低激发模的零振幅点）")
print("=" * 84)
for sname in ("T_topology", "K_ledger"):
    print("\n  ── 方案 %s ──" % sname)
    for name in BODIES:
        D, X, pct = shape_signature(GRAPH[name], LEDGER[name], SCHEMES[sname])
        _, nodes = floyd_from_graph(GRAPH[name], LEDGER[name], SCHEMES[sname])
        si = [nodes.index("S%d" % i) for i in range(3)]
        P = X[si]
        a = np.linalg.norm(P[1] - P[0]); b = np.linalg.norm(P[2] - P[0]); c = np.linalg.norm(P[2] - P[1])
        # 三角形面积（2D 投影意义下）
        print("     %-4s S0-S1=%.6f  S0-S2=%.6f  S1-S2=%.6f   比值=%.6f:%.6f:%.6f"
              % (name, a, b, c, a / max(a, b, c), b / max(a, b, c), c / max(a, b, c)))

# ══════════════════════════════════════════════════════════════════════
# (6) 结论
# ══════════════════════════════════════════════════════════════════════
print("\n" + "=" * 84)
print("(6) 结论")
print("=" * 84)
print("  (a) 前提：三个 A=4 产物图互为同构 -> %s"
      % all(nx.algorithms.isomorphism.GraphMatcher(GRAPH[a], GRAPH[b]).is_isomorphic()
            for a, b in pairs))
print("  (b) 纯拓扑方案 T：D 逐元素最大差 = %.3e（应 = 0）" % SUM["T_topology"]["dmax"])
print("      形状指纹最大差 = %.3e（应 = 0）" % SUM["T_topology"]["smax"])
print("  (c) 账本方案 K：D 最大差 = %.6e，形状指纹最大差 = %.6e"
      % (SUM["K_ledger"]["dmax"], SUM["K_ledger"]["smax"]))
print("  (d) 账本方案 L：D 最大差 = %.6e，形状指纹最大差 = %.6e"
      % (SUM["L_log"]["dmax"], SUM["L_log"]["smax"]))
print("\n  判读（须逐对看，不可只看 max）：")
verdict_T = "同值（同构图同 D，符合预期）" if SUM["T_topology"]["dmax"] < 1e-9 else "异常！须查构造"
print("    · 方案 T：%s" % verdict_T)
for s in ("K_ledger", "L_log"):
    per = {}
    for a, b in pairs:
        per[(a, b)] = max(abs(x - y) for x, y in
                          zip(SUM[s]["pct"][a], SUM[s]["pct"][b]))
    print("    · 方案 %s：逐对形状指纹差 ->" % s)
    for a, b in pairs:
        print("        %-4s vs %-4s : %.6e %s"
              % (a, b, per[(a, b)], "分开" if per[(a, b)] > 1e-6 else "**未分开**"))
    # 关键：⁴He-⁴H 是 §12.11(2) 恒等式预言必须为正、实测不束缚的那一对
    crit = per[("4He", "4H")]
    print("      => 判据：⁴He vs ⁴H %s -> 该方案%s承载 A=4 的区分"
          % ("分开" if crit > 1e-6 else "未分开",
             "" if crit > 1e-6 else "**不**"))

with open(r"C:\mywork\vasp\sre_nucleon_geometry_split.json", "w", encoding="utf-8") as f:
    json.dump({"invariants": inv, "profile": {k: list(v) for k, v in PROFILE.items()},
               "summary": SUM}, f, indent=2, ensure_ascii=False)
print("\n[OK] -> sre_nucleon_geometry_split.json")
print("done")
