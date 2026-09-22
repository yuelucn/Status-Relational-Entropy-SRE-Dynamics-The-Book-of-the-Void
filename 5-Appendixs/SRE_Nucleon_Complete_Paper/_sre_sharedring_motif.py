# -*- coding: utf-8 -*-
"""n-n 的 D 型拼接是否与 n-p 的 D 型共享同一"算术刚性"；以及 p-p 的 D 型是否退化回单质子。"""
import sys, itertools
import numpy as np
import networkx as nx
import sympy as sp
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
X = sp.Symbol("x")


def Y3(pre):
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        G.add_edge("%sL0%d" % (pre, j), "%sL1%d" % (pre, j))
        G.add_edge("%sL1%d" % (pre, j), "%sL2%d" % (pre, j))
        G.add_edge("%sL2%d" % (pre, j), "%sL0%d" % (pre, j))
    return G


def open_body(pre):
    G = Y3(pre)
    G.remove_edge("%sL00" % pre, "%sL10" % pre)
    return G


def amal(Xg, Yg, pairs):
    rep = {b: a for a, b in pairs}
    f = lambda x: rep.get(x, x)
    H = nx.Graph()
    for G in (Xg, Yg):
        for u, v in G.edges():
            H.add_edge(f(u), f(v))
    return H


def facspec(G, name):
    nodes = sorted(G.nodes(), key=str)
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    M = sp.zeros(n, n)
    for u, v in G.edges():
        i, j = idx[u], idx[v]
        M[i, i] += 1
        M[j, j] += 1
        M[i, j] -= 1
        M[j, i] -= 1
    ch = sp.factor(M.charpoly(X).as_expr())
    fl = sp.factor_list(ch)[1]
    degs = sorted(sp.degree(f, X) for f, m in fl)
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    print("--- %s : V=%d E=%d T=%d b1=%d |Aut|=%d" %
          (name, G.number_of_nodes(), G.number_of_edges(),
           sum(nx.triangles(G).values()) // 3,
           G.number_of_edges() - G.number_of_nodes() + 1,
           sum(1 for _ in itertools.islice(
               nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter(), 100000))))
    print("    不可约因子次数:", degs, "  (全<=2 表示只含整数与二次无理)")
    for f, m in fl:
        if sp.degree(f, X) <= 2:
            rts = sp.roots(sp.Poly(f, X), X)
            print("      (%s)^%d  -> %s" % (sp.nsimplify(f), m,
                  [str(sp.nsimplify(sp.simplify(r))) + "×%d" % (m * rm) for r, rm in rts.items()]))
        else:
            print("      (%s)^%d  -> 三次/更高，无简洁闭式" % (sp.nsimplify(f), m))
    print("    特征值:", np.round(ev, 6))
    print()


P = Y3("p_")
N1 = open_body("n_")
N2 = open_body("m_")
Q = Y3("q_")

# n-n 的 D 型（对应环 j=0 对 j=0）
NN = amal(N1, N2, [("n_L00", "m_L00"), ("n_L10", "m_L10"), ("n_L20", "m_L20")])
# n-p 的 D 型
NP = amal(N1, P, [("n_L00", "p_L00"), ("n_L10", "p_L10"), ("n_L20", "p_L20")])
# p-p 的 D 型（对应环 j=0 对 j=0）
PP = amal(P, Q, [("p_L00", "q_L00"), ("p_L10", "q_L10"), ("p_L20", "q_L20")])

facspec(NP, "n-p  D 型")
facspec(NN, "n-n  D 型")
facspec(PP, "p-p  D 型（是否退化回单质子 Y3⋉△3）")

print("p-p D 型 与 单质子 同构?", nx.is_isomorphic(PP, P))
print("n-n D 型 与 n-p D 型 同构?", nx.is_isomorphic(NN, NP))
print()

# 环归属对照：共享环上每条边的"共有重数"
for tag, (A_, B_, pairs) in {"n-p": (N1, P, [("n_L00", "p_L00"), ("n_L10", "p_L10"), ("n_L20", "p_L20")]),
                             "n-n": (N1, N2, [("n_L00", "m_L00"), ("n_L10", "m_L10"), ("n_L20", "m_L20")])}.items():
    rep = {b: a for a, b in pairs}
    f = lambda x: rep.get(x, x)
    EA = {tuple(sorted((f(u), f(v)))) for u, v in A_.edges()}
    EB = {tuple(sorted((f(u), f(v)))) for u, v in B_.edges()}
    both = EA & EB
    print("%s: 共享环三点=%s  双属边=%d 条 %s  该环三条边归属=%s" % (
        tag, sorted(rep.keys())[:1] and sorted({f(k) for k in rep}),
        len(both), sorted(map(str, both)),
        [("共" if tuple(sorted((u, v))) in both else "单") for u, v in
         itertools.combinations(sorted({f(k) for k in rep}), 2)]))
