# -*- coding: utf-8 -*-
"""
三体/四体拼接：三方共有的显式构造、结构不变量、共享账本、定价过定检验。只做计算。
"""
import sys, itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

M_P, M_N = 938.27208816, 939.56542052
DM = M_N - M_P                       # 1.293332 MeV
BEXP = {"d": 2.224566, "t": 8.4820, "He3": 7.7181, "He4": 28.2957}


def Y3(pre, state="p"):
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("%sL%d%d" % (pre, a, j), "%sL%d%d" % (pre, b, j))
    if state == "n":
        G.remove_edge("%sL00" % pre, "%sL10" % pre)
    return G


def build(bodies, coin):
    """bodies=[(pre,state)]；coin={pre:(j,...)} 指定该体哪些环参与重合区"""
    H = nx.Graph()
    ledger = {}
    for pre, state in bodies:
        G = Y3(pre, state)
        m = {}
        for j in coin.get(pre, ()):
            for i in range(3):
                m["%sL%d%d" % (pre, i, j)] = "S%d_%d" % (j, i)
        E = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
        for e in E:
            ledger[e] = ledger.get(e, 0) + 1
        H.add_edges_from(E)
    return H, ledger


def inv(G):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    return dict(V=G.number_of_nodes(), E=G.number_of_edges(),
                T=sum(nx.triangles(G).values()) // 3,
                b1=G.number_of_edges() - G.number_of_nodes() + 1,
                rho=float(ev[-1]), lam2=float(ev[1]),
                naut=sum(1 for _ in itertools.islice(
                    GraphMatcher(G, G).isomorphisms_iter(), 200000)))


def nice(x, tol=1e-9):
    """搜索 (p+q*sqrt(m))/r 的简洁闭式"""
    for m in (2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21):
        for r in range(1, 13):
            for p in range(-40, 41):
                for q in range(-40, 41):
                    if q == 0:
                        continue
                    if abs((p + q * m ** 0.5) / r - x) < tol:
                        return "( %d %+d*sqrt(%d) ) / %d" % (p, q, m, r)
    return None


def report(name, G, ledger, ref=None):
    i = inv(G)
    print("=" * 74)
    print("%s   V=%d E=%d T=%d beta1=%d |Aut|=%d" %
          (name, i["V"], i["E"], i["T"], i["b1"], i["naut"]))
    print("   rho=%.9f  lam2=%.9f" % (i["rho"], i["lam2"]))
    print("   rho 闭式: %s" % (nice(i["rho"]) or "无(简洁)"))
    print("   lam2 闭式: %s" % (nice(i["lam2"]) or "无(简洁)"))
    if ref:
        print("   与 %s 同构? %s" % (ref[0], nx.is_isomorphic(G, ref[1])))
    cen = {}
    for e, k in ledger.items():
        cen[k] = cen.get(k, 0) + 1
    print("   共享账本 k 分布 (k=声称该边的核子数): %s" %
          ", ".join("k=%d:%d条" % (k, w) for k, w in sorted(cen.items())))
    S = [e for e in ledger if str(e[0]).startswith("S")]
    print("   重合区边 (%d 条):" % len(S))
    for e in sorted(S, key=str):
        print("      %-16s k=%d" % (str(e), ledger[e]))
    return i, ledger


# ---------------- 构形 ----------------
print("### 三方共有：全部三体的环 0 重合成一个共享环")
H3a, L3a = build([("a", "n"), ("b", "n"), ("c", "p")], {"a": (0,), "b": (0,), "c": (0,)})
report("3H(a)  n,n,p  三方共环0", H3a, L3a)

He3a, M3a = build([("a", "p"), ("b", "p"), ("c", "n")], {"a": (0,), "b": (0,), "c": (0,)})
report("3He(a) p,p,n  三方共环0", He3a, M3a, ref=("3H(a)", H3a))

print()
print("### 对照：链式（两次独立两方共有，环位不同）")
H3b, L3b = build([("a", "n"), ("b", "p"), ("c", "n")],
                 {"a": (0,), "b": (0, 1), "c": (1,)})
report("3H(b) 链式 n-p | p-n", H3b, L3b, ref=("3H(a)", H3a))

He3b, M3b = build([("a", "n"), ("b", "p"), ("c", "p")],
                  {"a": (0,), "b": (0, 1), "c": (1,)})
report("3He(b) 链式 n-p | p-p", He3b, M3b, ref=("3H(a)", H3a))

print()
print("### 四体：2p+2n 四方共环0")
He4, M4 = build([("a", "p"), ("b", "p"), ("c", "n"), ("d", "n")],
                {"a": (0,), "b": (0,), "c": (0,), "d": (0,)})
report("4He  p,p,n,n  四方共环0", He4, M4)
