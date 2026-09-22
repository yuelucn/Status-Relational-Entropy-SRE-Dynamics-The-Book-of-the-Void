# -*- coding: utf-8 -*-
"""最低非平凡模的体数无关性：k=2..6 共享环构形的 lam2 与特征向量支集。只做计算。"""
import sys
import numpy as np
import networkx as nx
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TARGET = 2 - 3 ** 0.5


def build(k, nopen):
    """k 个体共享环 0；其中前 nopen 个是开态（休眠环0的一条边）"""
    H = nx.Graph()
    for b in range(k):
        pre = "b%d_" % b
        for i in range(3):
            for j in range(3):
                u = "%sc%d" % (pre, i)
                v = "%sL%d%d" % (pre, i, j)
                H.add_edge(u, v)
        for j in range(3):
            for a, c in ((0, 1), (1, 2), (2, 0)):
                H.add_edge("%sL%d%d" % (pre, a, j), "%sL%d%d" % (pre, c, j))
        if b < nopen:
            H.remove_edge("%sL00" % pre, "%sL10" % pre)
    m = {}
    for b in range(k):
        pre = "b%d_" % b
        for i in range(3):
            m["%sL%d0" % (pre, i)] = "S0_%d" % i
    return nx.relabel_nodes(H, m, copy=True)


print("=== 最低非平凡模 lam2 随体数 k 的变化 ===")
print("  %-6s %-14s %-14s %-10s %-14s" % ("k", "lam2", "2-sqrt3", "相对差", "rho"))
res = {}
for k in range(2, 7):
    G = build(k, 1)
    L = nx.laplacian_matrix(G).toarray().astype(float)
    ev, vec = np.linalg.eigh(L)
    lam2 = ev[1]
    res[k] = (G, ev, vec, lam2)
    print("  %-6d %-14.12f %-14.12f %-10.2e %-14.9f" %
          (k, lam2, TARGET, abs(lam2 - TARGET), ev[-1]))

print()
print("=== lam2 特征向量的支集（谁的振幅非零）===")
for k in (2, 3, 4):
    G, ev, vec, lam2 = res[k]
    v = vec[:, 1]
    nz = {n: abs(v[i]) for i, n in enumerate(G.nodes()) if abs(v[i]) > 1e-8}
    typ = {}
    for n, a in nz.items():
        if str(n).startswith("S0_"):
            t = "共享环顶点"
        elif str(n)[-3:] == "L00" or str(n)[-3:] == "L10" or str(n)[-3:] == "L20":
            t = "环0叶点(已并入共享环)"
        elif "_L" in str(n) and str(n)[-1] == "0":
            t = "环0叶点"
        elif str(n)[-1] in "12":
            t = "环1/2叶点(未参与重合)"
        else:
            t = "股心"
        typ[t] = typ.get(t, 0) + 1
    print("  k=%d  lam2=%.12f  支集节点数=%d / %d" % (k, lam2, len(nz), G.number_of_nodes()))
    for t, c in sorted(typ.items()):
        print("       %-26s %d" % (t, c))
    # 环1/2 的叶点与股心是否完全无振幅
    off = [n for n in G.nodes() if abs(v[list(G.nodes()).index(n)]) <= 1e-8]
    print("       零振幅（完全不动）节点数 = %d" % len(off))

print()
print("=== 对照：k=3 但三体全部同步（3 个都开态）是否改变 lam2 ===")
for nopen in (0, 1, 2, 3):
    G = build(3, nopen)
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float)))
    print("  nopen=%d  V=%d E=%d lam2=%.12f  rho=%.9f  与 2-sqrt3 差 %.2e" %
          (nopen, G.number_of_nodes(), G.number_of_edges(), ev[1], ev[-1],
           abs(ev[1] - TARGET)))
