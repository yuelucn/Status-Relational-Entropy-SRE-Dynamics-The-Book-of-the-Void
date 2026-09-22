# -*- coding: utf-8 -*-
"""逐轨道的开边读数唯一性 + 关键数值的闭式搜索"""
import sys, json, itertools, numpy as np, networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


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


A = y3()
B = nx.convert_node_labels_to_integers(nx.Graph(
    json.load(open("sre_nucleon_tiebreak_results.json", encoding="utf-8"))["candidate_B_edges"]))


def orbits(G, cap=4000):
    edges = [tuple(sorted(e)) for e in G.edges()]
    parent = {e: e for e in edges}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for m in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap):
        for e in edges:
            f = tuple(sorted((m[e[0]], m[e[1]])))
            a, b = find(e), find(f)
            if a != b:
                parent[a] = b
    g = {}
    for e in edges:
        g.setdefault(find(e), []).append(e)
    return list(g.values())


def lam2(G):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    return float(ev[1])


def T(G):
    return sum(nx.triangles(G).values()) // 3


print("=" * 74)
print("逐轨道：打开一条边后的读数")
print("=" * 74)
for tag, G in (("A", A), ("B", B)):
    print("候选 %s  闭态 lam2=%.9f  T=%d  边轨道数=%d" % (tag, lam2(G), T(G), len(orbits(G))))
    for i, o in enumerate(orbits(G), 1):
        e = o[0]
        H = G.copy(); H.remove_edge(*e)
        print("   轨道%d  |E|=%2d  代表边 %-9s  ->  lam2=%.9f   T=%d->%d"
              % (i, len(o), str(e), lam2(H), T(G), T(H)))
    readings = sorted({round(lam2(G.copy()) if False else 0, 9)})
    vals = []
    for e in G.edges():
        H = G.copy(); H.remove_edge(*e)
        vals.append(round(lam2(H), 9))
    uniq = sorted(set(vals))
    lower = sorted({v for v in uniq if v < 0.999999})
    print("   18 次开边所得 lam2 取值：%s  共 %d 种" % (uniq, len(uniq)))
    print("   其中使 lam2 下降的读数：%s  共 %d 种" % (lower, len(lower)))
    # 读数是否只由一个轨道产生
    for v in lower:
        cnt = sum(1 for x in vals if abs(x - v) < 1e-9)
        print("      读数 %.9f 出现 %d 次" % (v, cnt))
    print()

print("=" * 74)
print("关键数值的闭式搜索（对 sqrt13 的有理线性组合、以及低次整系数多项式）")
print("=" * 74)
s13 = 13 ** 0.5
vals = {"lam2_open": 0.527166091, "lam4_open": 1.537402,
        "drop_low": 1 - 0.527166091, "drop_high": 1.697224362 - 1.537402}
for name, x in vals.items():
    hits = []
    for r in range(1, 25):
        for p in range(-40, 41):
            for q in range(-40, 41):
                if abs((p + q * s13) / r - x) < 5e-9:
                    hits.append("( %d %+d*sqrt13 )/%d" % (p, q, r))
    print("  %-11s = %.9f   闭式命中: %s" % (name, x, hits if hits else "无（前 25/±40 搜索内）"))

print()
print("关系核算：")
print("  lam2_open + drop_low  = %.9f  (应 = 1)" % (0.527166091 + (1 - 0.527166091)))
print("  lam4_open + drop_high = %.9f  (应 = 1.697224362)" % (1.537402 + (1.697224362 - 1.537402)))
print("  drop_low / drop_high  = %.9f" % ((1 - 0.527166091) / (1.697224362 - 1.537402)))
print("  lam2_open * rho       = %.9f" % (0.527166091 * 5.302775637732))
print("  lam4_open * rho       = %.9f" % (1.537402 * 5.302775637732))
print("  lam2_open / rho       = %.9f   (kappa = 0.188893067)" % (0.527166091 / 5.302775637732))
print("  drop_low  / rho       = %.9f" % ((1 - 0.527166091) / 5.302775637732))
print("  1 / rho               = %.9f   (kappa = 0.188893067)" % (1 / 5.302775637732))
print("  m_e/m_p/alpha         = %.9f" % (0.51099895 / 938.27208816 / (1 / 137.035999084)))
print("  Q/m_p/alpha           = %.9f" % ((1.29333236 - 0.51099895) / 938.27208816 / (1 / 137.035999084)))
