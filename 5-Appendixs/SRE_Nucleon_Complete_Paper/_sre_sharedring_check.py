# -*- coding: utf-8 -*-
"""复核：变体 D 的借用边权重是否真的不影响谱；并顺带取 D 轨道归属。"""
import sys, itertools, numpy as np, networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


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


P = Y3("p_")
N = Y3("n_")
N.remove_edge("n_L00", "n_L10")


def amal(pairs):
    rep = {nn: pn for pn, nn in pairs}
    f = lambda x: rep.get(x, x)
    H = nx.Graph()
    for G in (P, N):
        for u, v in G.edges():
            H.add_edge(f(u), f(v))
    return H


D = amal([("p_L00", "n_L00"), ("p_L10", "n_L10"), ("p_L20", "n_L20")])
A = amal([("p_L00", "n_L00"), ("p_L10", "n_L10")])

print("D 有边 (p_L00,p_L10)?", D.has_edge("p_L00", "p_L10"))
print("度(p_L00,p_L10,p_L20) =", D.degree("p_L00"), D.degree("p_L10"), D.degree("p_L20"))
print()

print("--- 手搓加权 Laplacian：只改 (p_L00,p_L10) 权重 ---")
for t in (1.0, 0.9, 0.5, 0.1, 0.0):
    nodes = list(D.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    Adj = np.zeros((n, n))
    for u, v in D.edges():
        w = t if {u, v} == {"p_L00", "p_L10"} else 1.0
        i, j = idx[u], idx[v]
        Adj[i, j] = w
        Adj[j, i] = w
    Lm = np.diag(Adj.sum(1)) - Adj
    ev = np.sort(np.linalg.eigvalsh(Lm))
    print("  t=%.1f  迹=%7.3f  lam2=%.9f  lam3=%.9f  rho=%.9f" %
          (t, np.trace(Lm), ev[1], ev[2], ev[-1]))

print()
print("--- 对照：变体 A 改它那条被借用的边 (p_L00,p_L10) ---")
for t in (1.0, 0.9, 0.5, 0.1, 0.0):
    nodes = list(A.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    Adj = np.zeros((n, n))
    for u, v in A.edges():
        w = t if {u, v} == {"p_L00", "p_L10"} else 1.0
        i, j = idx[u], idx[v]
        Adj[i, j] = w
        Adj[j, i] = w
    Lm = np.diag(Adj.sum(1)) - Adj
    ev = np.sort(np.linalg.eigvalsh(Lm))
    print("  t=%.1f  迹=%7.3f  lam2=%.9f  lam3=%.9f  rho=%.9f" %
          (t, np.trace(Lm), ev[1], ev[2], ev[-1]))

print()
print("--- D 的顶点轨道归属 ---")
orb = {}
for m in itertools.islice(GraphMatcher(D, D).isomorphisms_iter(), 200000):
    for v in D:
        orb.setdefault(v, set()).add(m[v])
seen, groups = [], []
for v in D:
    g = frozenset(orb[v])
    if g not in seen:
        seen.append(g)
        groups.append(sorted(map(str, g)))
for i, g in enumerate(groups, 1):
    print("  轨道%d (大小 %d): %s" % (i, len(g), g))

print()
print("--- D 的边轨道归属 ---")
eo = {}
for m in itertools.islice(GraphMatcher(D, D).isomorphisms_iter(), 200000):
    for e in D.edges():
        eo.setdefault(tuple(sorted(e)), set()).add(tuple(sorted((m[e[0]], m[e[1]]))))
done, classes = set(), []
for e in D.edges():
    k = tuple(sorted(e))
    if k in done:
        continue
    cl = {k}
    changed = True
    while changed:
        changed = False
        for e2 in list(cl):
            for x in eo.get(e2, set()):
                if tuple(sorted(x)) not in cl:
                    cl.add(tuple(sorted(x)))
                    changed = True
    for x in cl:
        done.add(x)
    classes.append(sorted(cl))
EP, EN, both = None, None, None
rep = {"n_L00": "p_L00", "n_L10": "p_L10", "n_L20": "p_L20"}
f = lambda x: rep.get(x, x)
EP = {tuple(sorted((f(u), f(v)))) for u, v in P.edges()}
EN = {tuple(sorted((f(u), f(v)))) for u, v in N.edges()}
both = EP & EN
for i, c in enumerate(classes, 1):
    tag = ["共" if e in both else ("p_单" if e in EP else "n_单") for e in c]
    print("  边轨%d (大小 %d): 例 %s  归属=%s" % (i, len(c), str(c[0]), set(tag)))
