# -*- coding: utf-8 -*-
"""A/B 过渡读数的唯一性稀有度 + 全谱释放分布"""
import sys, json, itertools, numpy as np, networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

M_P, M_N, M_E = 938.27208816, 939.56542052, 0.51099895
ALPHA = 1 / 137.035999084
DM = M_N - M_P
KAPPA = (DM / M_P) / ALPHA


def y3():
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    return nx.convert_node_labels_to_integers(G)


def spec(G):
    return np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))


def lam2(G):
    return float(spec(G)[1])


A = y3()
B = nx.convert_node_labels_to_integers(nx.Graph(
    json.load(open("sre_nucleon_tiebreak_results.json", encoding="utf-8"))["candidate_B_edges"]))


def fingerprint(G):
    A_ = nx.to_numpy_array(G)
    return (tuple(np.round(np.linalg.eigvalsh(A_), 6)),
            tuple(sorted(nx.triangles(G).values())),
            tuple(sorted(np.diag(np.linalg.matrix_power(A_, 4)).astype(int))))


rng = np.random.default_rng(11)
buckets, pool = {}, []
for _ in range(40000):
    H = nx.configuration_model([3] * 12, seed=int(rng.integers(1 << 31)))
    G = nx.Graph(H); G.remove_edges_from(nx.selfloop_edges(G))
    if G.number_of_edges() != 18 or not nx.is_connected(G):
        continue
    k = fingerprint(G); b = buckets.setdefault(k, [])
    if any(nx.is_isomorphic(G, X) for X in b):
        continue
    b.append(G); pool.append(G)
    if len(pool) >= 85:
        break

print("=" * 76)
print("A 打开一条股心通道后的全谱与逐模释放量（总释放 = 2 = 2E 的下降）")
print("=" * 76)
evc = spec(A)
# 找不改变三角环数、且使 lam2 下降的边 = 释放边
rel_edges = []
for e in A.edges():
    H = A.copy(); H.remove_edge(*e)
    if lam2(H) < 0.999999 and (sum(nx.triangles(H).values()) // 3) == 3:
        rel_edges.append(e)
print("  释放边数 = %d（三角环数不变，lam2 下降）" % len(rel_edges))
e0 = rel_edges[0]
evo = spec(A.copy())
H = A.copy(); H.remove_edge(*e0)
evo = spec(H)
print("  闭态谱: " + ", ".join("%.6f" % x for x in evc))
print("  开态谱: " + ", ".join("%.6f" % x for x in evo))
drops = evc - evo
print("  逐模差值（闭−开）: " + ", ".join("%+.6f" % x for x in drops))
print("  差值总和 = %.6f  （应 = 2 × 打开边数 = 2）" % drops.sum())
print("  非零差值: " + ", ".join("%+.6f" % x for x in drops if abs(x) > 1e-9))
nz = sorted([float(x) for x in drops if abs(x) > 1e-9], reverse=True)
if len(nz) >= 1:
    print("  最大单模释放 = %.9f ；占总量 %.4f%%" % (nz[0], 100 * nz[0] / 2))
print("  lam2(开)/rho = %.9f ; 1/rho = %.9f ; kappa = %.9f"
      % (evo[1] / evc[-1], 1 / evc[-1], KAPPA))

print()
print("=" * 76)
print("池内稀有度：释放读数的唯一性与简并保护")
print("=" * 76)


def release_profile(G):
    l0 = lam2(G)
    reads = []
    for e in G.edges():
        H = G.copy(); H.remove_edge(*e)
        r = lam2(H)
        if r < l0 - 1e-9:
            reads.append(round(r, 6))
    T0 = sum(nx.triangles(G).values()) // 3
    nT = 0
    for e in G.edges():
        H = G.copy(); H.remove_edge(*e)
        if lam2(H) < l0 - 1e-9 and (sum(nx.triangles(H).values()) // 3) == T0:
            nT += 1
    ev = spec(G)
    m2 = int(np.sum(np.isclose(ev, ev[1], atol=1e-6)))
    return dict(n_read=len(set(reads)), n_rel=len(reads), n_rel_T_preserving=nT,
                m2=m2, Pi1=float(ev[1] / ev[-1]))


rows = [(release_profile(G), G) for G in pool]
uniq = [(r, G) for r, G in rows if r["n_read"] == 1]
print("  池内 85 图：")
print("    释放读数唯一（n_read=1）的图数 = %d" % len(uniq))
for r, G in uniq:
    print("      m(lam2)=%d  Pi1=%.6f  dev=%6.3f%%  释放边数=%d  其中不破坏闭合单元者=%d"
          % (r["m2"], r["Pi1"], 100 * abs(r["Pi1"] - KAPPA) / KAPPA, r["n_rel"],
             r["n_rel_T_preserving"]))
print()
print("    [Pi1<3%%] AND [n_read=1] 命中数 = %d"
      % len([1 for r, G in uniq if abs(r["Pi1"] - KAPPA) / KAPPA < 0.03]))
print("    [Pi1<3%%] AND [m(lam2)=2] 命中数 = %d"
      % len([1 for r, G in rows if r["m2"] == 2 and abs(r["Pi1"] - KAPPA) / KAPPA < 0.03]))
print("    [Pi1<3%%] AND [m(lam2)=2] AND [n_read=1] 命中数 = %d"
      % len([1 for r, G in rows if r["m2"] == 2 and r["n_read"] == 1
             and abs(r["Pi1"] - KAPPA) / KAPPA < 0.03]))
print()
print("   n_read 分布：")
from collections import Counter
c = Counter(r["n_read"] for r, G in rows)
for k in sorted(c):
    print("      n_read=%d : %d 图" % (k, c[k]))

print()
print("=" * 76)
print("0.527166091 的二次闭式搜索（x 为整数系数二次方程的根）")
print("=" * 76)
x = 0.527166091
hits = []
for a in range(1, 60):
    for b in range(-120, 121):
        for cc in range(-120, 121):
            if abs(a * x * x + b * x + cc) < 1e-7:
                hits.append((a, b, cc, b * b - 4 * a * cc))
for h in hits[:12]:
    a, b, cc, disc = h
    print("    %dx^2 %+dx %+d = 0   判别式 = %d" % (a, b, cc, disc))
if not hits:
    print("    未命中（a<60, |b|,|c|<120）")
