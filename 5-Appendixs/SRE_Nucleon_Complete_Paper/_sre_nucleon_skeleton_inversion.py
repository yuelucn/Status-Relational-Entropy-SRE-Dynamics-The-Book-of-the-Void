# -*- coding: utf-8 -*-
"""
SRE 核子骨架反演 v2 —— 可复算脚本
=====================================
主题：以中子 β 衰变为拓扑线索，用实测无量纲比值反演核子的图投影骨架。

方法学（与电子推衍一致）：
    SRE 只能推算物理值之间的"比值"关系，不能给出绝对量。
    因此做法是：把实测比值当作"图泛函的值"，反解图的拓扑参数。

三步筛选（判据先于数值，避免事后拟合）：
    判据 ①  整数性：beta_1 * (m_n-m_p)/m_p  对标流质量占比实测值 —— 定顶点数 V
    判据 ②  谱比：lambda_2/rho 落在目标值 3% 以内 —— 定拓扑（在 V=12 的立方图族内）
    判据 ③  三重对称：3 | |Aut(G)| —— 定解（三股骨架的结构要求）

依赖：numpy, networkx（闭源算子不参与，本脚本为开源层纯复算）
运行：python -u _sre_nucleon_skeleton_inversion.py
输出：sre_nucleon_skeleton_inversion_results.json
"""

import json
import itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

# ---------------------------------------------------------------- 常数
M_E = 0.51099895000       # 电子质量 MeV (CODATA 2018)
M_P = 938.27208816        # 质子质量 MeV (CODATA 2018)
M_N = 939.56542052        # 中子质量 MeV (CODATA 2018)
ALPHA = 1.0 / 137.035999084          # 精细结构常数
M_U, M_D = 2.16, 4.67     # u/d 流夸克质量 MeV (PDG, MS-bar 2 GeV)，仅作无量纲实测比借用

DM_RATIO = (M_N - M_P) / M_P          # (m_n - m_p)/m_p
TARGET = DM_RATIO / ALPHA             # 目标 kappa = 该比值除以 alpha
QUARK_SUM = (2 * M_U + M_D) / M_P     # (2m_u + m_d)/m_p

OUT = {}
LOG = []


def P(s=""):
    LOG.append(s)
    print(s)


# ---------------------------------------------------------------- 工具
def lap_ratio(G):
    """图泛函 Pi_1 = lambda_2 / rho （归一化 Laplacian 谱隙比，此处用组合 Laplacian）"""
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    return float(ev[1] / ev[-1])


def fingerprint(G):
    """结构指纹：邻接谱 + 三角形分布 + 4-闭 walks。用于同构去重的快速分桶。"""
    A = nx.to_numpy_array(G)
    return (tuple(np.round(np.linalg.eigvalsh(A), 6)),
            tuple(sorted(nx.triangles(G).values())),
            tuple(sorted(np.diag(np.linalg.matrix_power(A, 4)).astype(int))))


def aut_order(G, cap=6000):
    n = 0
    for _ in GraphMatcher(G, G).isomorphisms_iter():
        n += 1
        if n >= cap:
            break
    return n


def orbit_count(G, cap=6000):
    """自同构群作用在顶点集上的轨道数（结构"角色种类"数）"""
    maps = list(itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap))
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    parent = list(range(len(nodes)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for m in maps:
        for v, w in m.items():
            a, b = find(idx[v]), find(idx[w])
            if a != b:
                parent[a] = b
    return len({find(i) for i in range(len(nodes))})


def girth(G):
    try:
        return min(len(c) for c in nx.cycle_basis(G))
    except Exception:
        return 0


def describe(G):
    return dict(
        V=G.number_of_nodes(), E=G.number_of_edges(),
        beta1=G.number_of_edges() - G.number_of_nodes() + 1,
        girth=girth(G), triangles=sum(nx.triangles(G).values()) // 3,
        bipartite=nx.is_bipartite(G), diameter=nx.diameter(G),
        aut=aut_order(G), orbits=orbit_count(G),
        lambda2_over_rho=lap_ratio(G),
    )


# ================================================================ [0] 电子标定
P("=" * 78)
P("[0] 电子侧唯一已标定投影 Pi_1 = lambda_2 / rho 的复算（Mobius 阶梯族 M_n）")
P("=" * 78)


def mobius_spec(n, w):
    """Mobius 阶梯 M_n：环 C_n + 直径弦（弦权 w）"""
    A = np.zeros((n, n))
    h = n // 2
    for i in range(n):
        A[i, (i + 1) % n] = 1.0
        A[(i + 1) % n, i] = 1.0
    for i in range(h):
        A[i, i + h] = w
        A[i + h, i] = w
    L = np.diag(A.sum(1)) - A
    return np.sort(np.linalg.eigvalsh(L))


ev60 = mobius_spec(60, 1.0)
r60 = ev60[1] / ev60[-1]
# 解析闭式： lambda2 = 4 sin^2(2pi/n), rho = 2 + 2w + 2 cos(2pi/n)
x = 2 * np.pi / 60
closed = (2 * np.sin(x) ** 2) / (1 + 1.0 + np.cos(x))


def w_solve(n, target):
    xx = 2 * np.pi / n
    return 2 * np.sin(xx) ** 2 / target - 1 - np.cos(xx)


w_star = w_solve(60, ALPHA)
P("  n=60, w=1    : Pi_1 = %.9e  (解析闭式 %.9e, 相对差 %.1e)" %
  (r60, closed, abs(r60 - closed) / closed))
P("  alpha        :        %.9e  ; 与 w=1 处相对差 %.2e" % (ALPHA, abs(r60 - ALPHA) / ALPHA))
P("  解 Pi_1 = alpha 得 w* = 1 + %.4e   (论文报告 delta = 4.347e-5)" % (w_star - 1.0))
OUT["electron_calibration"] = dict(
    n=60, Pi1_at_w1=float(r60), alpha=float(ALPHA),
    rel_dev_at_w1=float(abs(r60 - ALPHA) / ALPHA),
    w_star=float(w_star), delta=float(w_star - 1.0))

# ================================================================ [1] 目标值
P("")
P("=" * 78)
P("[1] 核子侧目标值与三条判据的输入")
P("=" * 78)
P("  (m_n - m_p)/m_p             = %.9e" % DM_RATIO)
P("  目标 kappa = 上述 / alpha    = %.9f" % TARGET)
P("  (2m_u + m_d)/m_p (借用实测比) = %.6e  [%.4f%%]" % (QUARK_SUM, QUARK_SUM * 100))
OUT["targets"] = dict(dm_over_mp=float(DM_RATIO), kappa=float(TARGET),
                      quark_sum_over_mp=float(QUARK_SUM))

# ================================================================ [2] 判据 ①
P("")
P("[2] 判据 ① 整数性定 V：立方图 beta_1 = V/2 + 1，检验 beta_1 * (m_n-m_p)/m_p")
P("     V   beta1   beta1*dm/m [%]   vs 实测 0.9578%   相对偏差 [%]")
crit1 = []
for V in [8, 10, 12, 14, 16, 18]:
    b1 = V // 2 + 1
    val = b1 * DM_RATIO
    dev = 100 * (val - QUARK_SUM) / QUARK_SUM
    crit1.append(dict(V=V, beta1=b1, pct=val * 100, dev_pct=dev))
    star = "  <== 唯一选中" if abs(dev) < 2 else ""
    P("    %3d   %3d    %10.4f            %+8.2f%s" % (V, b1, val * 100, dev, star))
OUT["criterion_1"] = crit1

V_STAR, B1_STAR = 12, 7

# ================================================================ [3] 判据 ②
P("")
P("=" * 78)
P("[3] 判据 ② 谱比定拓扑：枚举 V=%d 的立方连通图（该阶不同构总数 85）" % V_STAR)
P("=" * 78)

rng = np.random.default_rng(11)
buckets, pool = {}, []
for _ in range(30000):
    H = nx.configuration_model([3] * V_STAR, seed=int(rng.integers(1 << 31)))
    G = nx.Graph(H)
    G.remove_edges_from(nx.selfloop_edges(G))
    if G.number_of_edges() != 3 * V_STAR // 2 or not nx.is_connected(G):
        continue
    k = fingerprint(G)
    b = buckets.setdefault(k, [])
    if any(nx.is_isomorphic(G, X) for X in b):
        continue
    b.append(G)
    pool.append(G)
    if len(pool) >= 85:
        break
P("  采样并同构去重得 %d 个不同构立方连通图" % len(pool))

ratios = np.array([lap_ratio(G) for G in pool])
devs = np.abs(ratios - TARGET) / TARGET
P("  谱比分布: min=%.4f  p25=%.4f  中位=%.4f  p75=%.4f  max=%.4f"
  % (ratios.min(), *np.percentile(ratios, [25, 50, 75]), ratios.max()))

for tol in [0.00165, 0.005, 0.01, 0.02, 0.03, 0.05]:
    P("    相对偏差 <%5.2f%% : %3d / %d   (命中率 %.4f)"
      % (tol * 100, (devs < tol).sum(), len(ratios), (devs < tol).mean()))
OUT["criterion_2_pool"] = dict(n_graphs=len(pool), ratio_min=float(ratios.min()),
                               ratio_median=float(np.median(ratios)), ratio_max=float(ratios.max()))
OUT["criterion_2_hit_rate"] = {str(t): float((devs < t).mean()) for t in
                               [0.00165, 0.005, 0.01, 0.02, 0.03, 0.05]}

# ================================================================ [4] 三股骨架
P("")
P("=" * 78)
P("[4] 结构直觉先定的候选：三股 Y 三角闭合骨架 Y3<)D3")
P("=" * 78)


def y3_closed(remove_edge=None):
    """三股 Y（3 中心 x 3 叶）的三角闭合体；remove_edge 用于构造开态（中子候选）"""
    G = nx.Graph()
    lea = {(i, j): "L%d%d" % (i, j) for i in range(3) for j in range(3)}
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, lea[(i, j)])
    for j in range(3):
        G.add_edge(lea[(0, j)], lea[(1, j)])
        G.add_edge(lea[(1, j)], lea[(2, j)])
        G.add_edge(lea[(2, j)], lea[(0, j)])
    if remove_edge is not None:
        G.remove_edge(*remove_edge)
    return nx.convert_node_labels_to_integers(G)


YC = y3_closed()
YN = y3_closed(remove_edge=("L22", "L02"))
d_c, d_n = describe(YC), describe(YN)
P("  闭合态(p 候选): " + json.dumps(d_c, ensure_ascii=False))
P("  开  态(n 候选): " + json.dumps(d_n, ensure_ascii=False))
P("  闭合态谱比 %.6f 与目标 %.6f 的相对偏差 = %.3f%%"
  % (d_c["lambda2_over_rho"], TARGET, 100 * abs(d_c["lambda2_over_rho"] - TARGET) / TARGET))
P("  关键观察：开/闭两态谱比相同 -> Pi_1 分辨不出 p 与 n；"
  "开合应由 beta_1（环数）读取：beta_1(p) - beta_1(n) = %d"
  % (d_c["beta1"] - d_n["beta1"]))
OUT["y3_closed"] = d_c
OUT["y3_open"] = d_n
OUT["y3_closed_dev_pct"] = float(100 * abs(d_c["lambda2_over_rho"] - TARGET) / TARGET)

# ================================================================ [5] 判据 ③
P("")
P("=" * 78)
P("[5] 判据 ③ 三重对称定解：三股骨架要求 3 | |Aut(G)|")
P("=" * 78)
cands = []
order = np.argsort(devs)
for i in order:
    if devs[i] < 0.03:
        G = pool[i]
        d = describe(G)
        d["dev_pct"] = float(100 * devs[i])
        d["triple_symmetric"] = (d["aut"] % 3 == 0)
        cands.append((d, G))
P("  偏差 <3%% 的候选共 %d 个：" % len(cands))
for d, G in cands:
    tag = "  <<< 三重对称（保留）" if d["aut"] % 3 == 0 else ""
    P("    ratio=%.6f  偏差=%6.3f%%  |Aut|=%3d  轨道=%d  围长=%d  三角=%d  直径=%d%s"
      % (d["lambda2_over_rho"], d["dev_pct"], d["aut"], d["orbits"],
         d["girth"], d["triangles"], d["diameter"], tag))
survivors = [(d, G) for d, G in cands if d["aut"] % 3 == 0]
P("")
P("  经判据 ③ 后剩余 %d 个候选" % len(survivors))

# 与手构 Y3 的同一性核验
for d, G in survivors:
    iso_YC = nx.is_isomorphic(G, YC)
    if iso_YC:
        P("    -> |Aut|=%d 的候选与手构三股 Y 三角闭合骨架同构（结构直觉先定、数值后验）"
          % d["aut"])
OUT["criterion_3"] = dict(n_after_crit2=len(cands), n_after_crit3=len(survivors),
                          survivors=[d for d, _ in survivors])

# 稀有度估计
p_crit23 = len(survivors) / len(pool)
p_joint = p_crit23 / 5.0     # V 档 5 选 1
P("")
P("  稀有度：判据 ②③ 联合命中率 = %d/%d = %.4f ；再乘 V 档 1/5 -> p ~ %.2e"
  % (len(survivors), len(pool), p_crit23, p_joint))
OUT["rarity"] = dict(p_crit23=float(p_crit23), p_joint=float(p_joint))

# ================================================================ [6] 结构体检
P("")
P("=" * 78)
P("[6] 结构体检：候选骨架能否摘出电子本体 Q3")
P("=" * 78)
Q3 = nx.hypercube_graph(3)
hits = 0
for S in itertools.combinations(YC.nodes(), 8):
    H = YC.subgraph(S)
    if H.number_of_edges() == 12 and all(dd == 3 for _, dd in H.degree()):
        hits += 1
isoQ = any(nx.is_isomorphic(YC.subgraph(S), Q3)
           for S in itertools.combinations(YC.nodes(), 8)
           if YC.subgraph(S).number_of_edges() == 12
           and all(dd == 3 for _, dd in YC.subgraph(S).degree()))
P("  含 3-正则 8 点子图: %d 个；其中与 Q3 同构: %s" % (hits, isoQ))
P("  -> beta 衰变只能取「种子沉降」的弱读法，不能取「从中掏出电子」的强读法")
OUT["q3_check"] = dict(cubic8_subgraphs=hits, contains_Q3=bool(isoQ))

# ================================================================ 输出
with open("sre_nucleon_skeleton_inversion_results.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P("")
P("已写出 sre_nucleon_skeleton_inversion_results.json")
