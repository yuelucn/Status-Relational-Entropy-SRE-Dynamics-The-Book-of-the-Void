# -*- coding: utf-8 -*-
"""
检验：账本->边权映射 w(k) 的选择是否**任意**？

若 A=4 的几何区分只在**某一个特定** w(k) 下成立，那是拟合；
若在一族自然的、单调递减的 w(k) 下**普遍**成立，才是结构性的。

方案 T : w = 1              (无账本信息，对照组)
方案 K : w = 1/k            (幂律 p=1)      -> ⁴He 与 ⁴H 退化为同一形状
方案 L : w = 1/log2(1+k)    -> 三对全分开
本脚本扫描一般幂律/对数族：
    w_p(k) = k^(-p)          p ∈ {0, 0.1, ..., 2.0}
    w_a(k) = 1/log2(1+k)^a   a ∈ {0.5, 1, 2, 4}
并报告：⁴He vs ⁴H 形状指纹差随参数的变化（"区分是否稳健"）。
"""
import sys, math, json
import numpy as np
import networkx as nx

HERE = r"C:\mywork\vasp"
sys.path.insert(0, HERE)
from _p3_p1a_final_scaffolds import mds_coords_from_dmat


def Y3(pre, state="p", open_ring=0):
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
    H = nx.Graph(); ledger = {}
    for pre, state in bodies:
        G = Y3(pre, state, r)
        mm = {"%sL%d%d" % (pre, i, r): "S%d" % i for i in range(3)}
        edges = {tuple(sorted((mm.get(u, u), mm.get(v, v)))) for u, v in G.edges()}
        for e in edges:
            ledger[e] = ledger.get(e, 0) + 1
        H.add_edges_from(edges)
    return H, ledger


B4 = {"4He": [("p1", "p"), ("p2", "p"), ("n1", "n"), ("n2", "n")],
      "4H":  [("p1", "p"), ("n1", "n"), ("n2", "n"), ("n3", "n")],
      "4Li": [("p1", "p"), ("p2", "p"), ("p3", "p"), ("n1", "n")]}
GRAPH, LED = {}, {}
for n, b in B4.items():
    GRAPH[n], LED[n] = shared_ring(b, r=0)


def shape(H, led, wfun, ndim=3):
    nodes = sorted(H.nodes()); idx = {v: i for i, v in enumerate(nodes)}
    N = len(nodes)
    D = np.full((N, N), 1e9); np.fill_diagonal(D, 0.0)
    for u, v in H.edges():
        w = wfun(led.get(tuple(sorted((u, v))), 1))
        D[idx[u], idx[v]] = D[idx[v], idx[u]] = w
    for k in range(N):
        D = np.minimum(D, D[:, k, None] + D[None, k, :])
    X = mds_coords_from_dmat(D, ndim=ndim)
    pd = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1))
    iu = np.triu_indices(N, 1)
    return np.percentile(pd[iu], [10, 25, 50, 75, 90]), D


def fp_diff(wfun):
    P = {n: shape(GRAPH[n], LED[n], wfun)[0] for n in B4}
    Ds = {n: shape(GRAPH[n], LED[n], wfun)[1] for n in B4}
    return (max(abs(a - b) for a, b in zip(P["4He"], P["4H"])),
            max(abs(a - b) for a, b in zip(P["4He"], P["4Li"])),
            max(abs(a - b) for a, b in zip(P["4H"], P["4Li"])),
            np.abs(Ds["4He"] - Ds["4H"]).max())


print("=" * 88)
print("账本->边权映射 w(k) 的稳健性扫描：A=4 几何区分是否只是某个 w 的巧合？")
print("=" * 88)
print("\n%-26s %14s %14s %14s %14s" % ("w(k)", "Δ(4He,4H)", "Δ(4He,4Li)", "Δ(4H,4Li)", "ΔD(4He,4H)"))
print("-" * 88)

rows = []
print("\n── 幂律族 w = k^(-p) ──")
for p in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0]:
    d1, d2, d3, dd = fp_diff(lambda k, p=p: k ** (-p))
    tag = "w=1（纯拓扑）" if p == 0 else "p=%.1f" % p
    print("%-26s %14.6e %14.6e %14.6e %14.6e" % (tag, d1, d2, d3, dd))
    rows.append((tag, d1, d2, d3, dd))

print("\n── 对数族 w = 1/log2(1+k)^a ──")
for a in [0.5, 1.0, 2.0, 4.0]:
    d1, d2, d3, dd = fp_diff(lambda k, a=a: 1.0 / math.log2(1.0 + k) ** a)
    tag = "log a=%.1f" % a
    print("%-26s %14.6e %14.6e %14.6e %14.6e" % (tag, d1, d2, d3, dd))
    rows.append((tag, d1, d2, d3, dd))

print("\n── 其它自然形式 ──")
for tag, fn in [("w=1-k/4（线性差值）", lambda k: max(1.0 - k / 4.0, 1e-6)),
                ("w=1/sqrt(k)", lambda k: k ** -0.5),
                ("w=(1-1/k) 保序", lambda k: 1.0 - 1.0 / k),
                ("w=1/(1+ln k)", lambda k: 1.0 / (1.0 + math.log(k)))]:
    d1, d2, d3, dd = fp_diff(fn)
    print("%-26s %14.6e %14.6e %14.6e %14.6e" % (tag, d1, d2, d3, dd))
    rows.append((tag, d1, d2, d3, dd))

print("\n" + "=" * 88)
print("统计")
print("=" * 88)
nz = [r for r in rows if r[1] > 1e-6]
zr = [r for r in rows if r[1] <= 1e-6]
print("  共测 %d 种 w(k) 形式" % len(rows))
print("  ⁴He~⁴H **已分开** 者 %d 种：%s" % (len(nz), ", ".join(r[0] for r in nz)))
print("  ⁴He~⁴H **未分开** 者 %d 种：%s" % (len(zr), ", ".join(r[0] for r in zr)))
print("\n  判读：")
if len(nz) == 0:
    print("    · 无任何 w 分开 ⁴He~⁴H -> 几何路线不成立")
elif len(zr) == 0:
    print("    · 全部 w 都分开 -> 区分对 w 的形式不敏感，属结构性")
else:
    print("    · 区分**依赖 w 的具体形式**（%d/%d 分开）" % (len(nz), len(rows)))
    print("    · 须指明：这仍是**选择**，不是导出 -> 与 §12.12 中 λ 的地位同类")

with open(r"C:\mywork\vasp\sre_nucleon_geometry_wscan.json", "w", encoding="utf-8") as f:
    json.dump([{"w": r[0], "d_He_H": r[1], "d_He_Li": r[2], "d_H_Li": r[3], "dD": r[4]}
               for r in rows], f, indent=2, ensure_ascii=False)
print("\n[OK] -> sre_nucleon_geometry_wscan.json")
print("done")
