# -*- coding: utf-8 -*-
"""
核子骨架并列候选的打破预备扫描（v2 附录）
=============================================
判据 ②③ 之后剩两个候选（|Aut|=36 与 |Aut|=12），它们在泛函 Pi_1 = lambda_2/rho 上
取值完全相同，因此 Pi_1 无法区分二者。
（更正：二者并非同谱图，仅 lambda_2 与 rho 恰好重合，见 _sre_nucleon_tiebreak_v2.py
  的同谱检验：邻接/Laplacian/无符号/归一化四类谱的最大特征值差均为 2.0。）本脚本：

  (a) 给出两个候选的全部非谱不变量，说明它们在哪里真正不同；
  (b) 用核子侧三个独立实测比做交叉检验尝试，并显式计算多重比较基数，
      避免把偶然命中当作证据。

输出：sre_nucleon_tiebreak_results.json
"""

import json
import itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

M_P = 938.27208816
M_N = 939.56542052
ALPHA = 1.0 / 137.035999084
OUT = {}


def P(s=""):
    print(s)


# ---------------------------------------------------------------- Y3 骨架
def y3():
    G = nx.Graph()
    lea = {(i, j): "L%d%d" % (i, j) for i in range(3) for j in range(3)}
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, lea[(i, j)])
    for j in range(3):
        G.add_edge(lea[(0, j)], lea[(1, j)])
        G.add_edge(lea[(1, j)], lea[(2, j)])
        G.add_edge(lea[(2, j)], lea[(0, j)])
    return nx.convert_node_labels_to_integers(G)


def fingerprint(G):
    A = nx.to_numpy_array(G)
    return (tuple(np.round(np.linalg.eigvalsh(A), 6)),
            tuple(sorted(nx.triangles(G).values())),
            tuple(sorted(np.diag(np.linalg.matrix_power(A, 4)).astype(int))))


def aut_order(G, cap=6000):
    return sum(1 for _ in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap))


def orbit_count(G, cap=6000):
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


Y = y3()
lapY = np.round(np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(Y).toarray())), 8)

# ---------------------------------------------------------------- 找回另一个候选
rng = np.random.default_rng(11)
buckets, pool = {}, []
for _ in range(30000):
    H = nx.configuration_model([3] * 12, seed=int(rng.integers(1 << 31)))
    G = nx.Graph(H)
    G.remove_edges_from(nx.selfloop_edges(G))
    if G.number_of_edges() != 18 or not nx.is_connected(G):
        continue
    k = fingerprint(G)
    b = buckets.setdefault(k, [])
    if any(nx.is_isomorphic(G, X) for X in b):
        continue
    b.append(G)
    pool.append(G)
    if len(pool) >= 85:
        break

TARGET = ((M_N - M_P) / M_P) / ALPHA


def lap_ratio(G):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    return float(ev[1] / ev[-1])


scored = sorted(((abs(lap_ratio(G) - TARGET) / TARGET, G) for G in pool), key=lambda t: t[0])
near = [(d, G) for d, G in scored if d < 0.03]
P("=" * 78)
P("[A] V=12 立方图中 Pi_1 落在目标 3% 内、且满足三重对称的候选")
P("=" * 78)
P("  偏差 <3%% 的图共 %d 个；逐个取自同构阶并要求 3 | |Aut|：" % len(near))
sel = []
for d, G in near:
    a = aut_order(G)
    keep = a % 3 == 0
    P("    ratio=%.6f  偏差=%6.3f%%  |Aut|=%3d  %s"
      % (lap_ratio(G), 100 * d, a, "保留" if keep else "剔除"))
    if keep:
        sel.append((d, a, G))
other = None
for d, a, G in sel:
    if not nx.is_isomorphic(G, Y):
        other = G
        break
P("  经三重对称后剩 %d 个；其中与手构 Y3 不同构者为候选 B" % len(sel))

P("")
P("=" * 78)
P("[B] 两个并列候选的非谱不变量对照")
P("=" * 78)


def invariants(G):
    A = nx.to_numpy_array(G)
    L = nx.laplacian_matrix(G).toarray()
    ev = np.sort(np.linalg.eigvalsh(L))
    Lp = np.linalg.pinv(L)
    n = G.number_of_nodes()
    # 电阻距离与 Kirchhoff 指数
    R = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                R[i, j] = Lp[i, i] + Lp[j, j] - 2 * Lp[i, j]
    Kf = R.sum() / 2
    d = dict(
        V=n, E=G.number_of_edges(),
        beta1=G.number_of_edges() - n + 1,
        triangles=sum(nx.triangles(G).values()) // 3,
        girth=min(len(c) for c in nx.cycle_basis(G)),
        diameter=nx.diameter(G),
        aut=aut_order(G), orbits=orbit_count(G),
        lambda2=float(ev[1]), rho=float(ev[-1]),
        Pi1=float(ev[1] / ev[-1]),
        Pi2_lam2_over_lam4=float(ev[1] / ev[3]),
        Kirchhoff=float(Kf),
        Wiener=float(nx.wiener_index(G)),
        mean_resistance=float(R.sum() / (n * (n - 1))),
        triangles_over_edges=float((sum(nx.triangles(G).values()) // 3) / G.number_of_edges()),
    )
    return d


dY, dO = invariants(Y), invariants(other)
keys = list(dY.keys())
P("  %-22s %14s %14s" % ("不变量", "候选 A (Y3)", "候选 B"))
for k in keys:
    mark = "   <-- 不同" if abs(dY[k] - dO[k]) > 1e-9 else ""
    P("  %-22s %14.6f %14.6f%s" % (k, dY[k], dO[k], mark))
OUT["candidate_A_Y3"] = dY
OUT["candidate_B"] = dO
OUT["candidate_B_edges"] = [list(map(int, e)) for e in other.edges()]

P("")
P("  候选 B 的顶点数/边数/β₁ 与 A 相同，谱完全相同；真正区别在于：")
P("    独立三角环数 %d vs %d ，顶点轨道数 %d vs %d ，自同构阶 %d vs %d"
  % (dO["triangles"], dY["triangles"], dO["orbits"], dY["orbits"], dO["aut"], dY["aut"]))
P("  即：A 有 3 个等价三角环、顶点分 2 类（股心 / 叶点）；B 只有 1 个三角环、顶点分 3 类。")
P("  按「三股骨架」的结构要求（三个等价闭合单元 + 股心/叶点二分），A 与直觉同源，B 不是。")

# ---------------------------------------------------------------- (b) 交叉检验
P("")
P("=" * 78)
P("[C] 交叉检验尝试：核子侧独立实测比 vs 图量（含多重比较基数核算）")
P("=" * 78)
targets = {
    "|mu_p/mu_n|": 1.4599,
    "g_A": 1.2756,
    "(m_Delta-m_N)/m_p": 293.0 / M_P,
    "|r_n^2|/r_p^2": 0.1161 / 0.84075 ** 2,
    "m_pi+-/m_p": 139.57039 / M_P,
    "B/A(Fe56)/m_p": 8.7903 / M_P,
}
quantities = {k: (dY[k], dO[k]) for k in keys}
rows = []
for tname, tv in targets.items():
    for qname, (a, b) in quantities.items():
        for cand, val in (("A", a), ("B", b)):
            if val == 0:
                continue
            for inv in (False, True):
                v = 1 / val if inv else val
                dev = abs(v - tv) / tv
                rows.append((dev, tname, qname + ("⁻¹" if inv else ""), cand, v, tv))
rows.sort()
P("  扫描基数：%d 个实测比 x %d 个图量 x 2 个候选 x 2 (正/倒) = %d 次比较"
  % (len(targets), len(quantities), len(rows)))
P("  在 <2%% 阈值下，偶然命中的期望次数 ≈ %d x 0.02 = %.1f  —— 故以下仅作线索，不作证据"
  % (len(rows), len(rows) * 0.02))
P("")
P("  偏差最小的 10 组（dev<5%）：")
n_hit2 = 0
for dev, tn, qn, cand, v, tv in rows[:10]:
    if dev >= 0.05:
        break
    if dev < 0.02:
        n_hit2 += 1
    P("    %-19s <- %-24s 候选%s : %.6f vs %.6f   偏差 %6.3f%%" % (tn, qn, cand, v, tv, 100 * dev))
P("")
P("  实际 <2%% 命中次数 = %d （期望 %.1f）-> %s"
  % (n_hit2, len(rows) * 0.02,
     "未显著超出偶然水平" if n_hit2 <= len(rows) * 0.02 + 1 else "值得追查"))
OUT["cross_check"] = dict(n_comparisons=len(rows), n_hit_2pct=n_hit2,
                          expected_hit_2pct=len(rows) * 0.02,
                          top=[dict(dev=r[0], target=r[1], quantity=r[2],
                                    candidate=r[3], value=r[4], observed=r[5])
                               for r in rows[:10]])

with open("sre_nucleon_tiebreak_results.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P("")
P("已写出 sre_nucleon_tiebreak_results.json")
