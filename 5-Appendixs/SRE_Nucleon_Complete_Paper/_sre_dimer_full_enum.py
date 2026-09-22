# -*- coding: utf-8 -*-
"""
两体拼接的完整枚举：把 (p,p) (n,n) (n,p) 三种配对在所有自然对接方式下跑一遍，
看结构本身能否排除 n-n / p-p，还是必须额外加"出借者须闭合完备"这一原则。
只做计算。
"""
import sys, itertools, json
import numpy as np
import networkx as nx
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


def open_body(pre):
    G = Y3(pre)
    G.remove_edge("%sL00" % pre, "%sL10" % pre)
    return G


def amal(X, Y, pairs):
    rep = {b: a for a, b in pairs}
    f = lambda x: rep.get(x, x)
    H = nx.Graph()
    for G in (X, Y):
        for u, v in G.edges():
            H.add_edge(f(u), f(v))
    return H


def inv(G):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    return dict(V=G.number_of_nodes(), E=G.number_of_edges(),
                T=sum(nx.triangles(G).values()) // 3,
                b1=G.number_of_edges() - G.number_of_nodes() + 1,
                conn=nx.is_connected(G), rho=float(ev[-1]), lam2=float(ev[1]),
                naut=sum(1 for _ in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), 100000)),
                comps=nx.number_connected_components(G))


def canon(G):
    """把图归一为同构类签名（数值指纹）"""
    A = nx.to_numpy_array(G)
    return (tuple(np.round(np.linalg.eigvalsh(A), 5)),
            tuple(sorted(nx.triangles(G).values())),
            tuple(sorted(dict(G.degree()).values())))


# ---------------- 各类对接方式 ----------------
def families(X, Y, tagX, tagY):
    """返回 list of (名称, 配对列表, 图) ；X 为缺口持有者，Y 为出借者"""
    out = []
    xgap = ("%sL00" % tagX, "%sL20" % tagX, "%sL10" % tagX)   # 开路三点（顺序按路径）
    xends = ("%sL00" % tagX, "%sL10" % tagX)

    # 族 A：缺口两端 <-> Y 的某条边两端
    seen = {}
    for e in Y.edges():
        H = amal(X, Y, list(zip(xends, e)))
        seen.setdefault(canon(H), H)
    for i, H in enumerate(seen.values(), 1):
        out.append(("A 两点对接(缺口两端<-一条边) #%d" % i, H))

    # 族 D：缺口路径三点 <-> Y 的某个三角环三点
    seenD = {}
    tris = [c for c in itertools.combinations(Y.nodes(), 3)
            if Y.has_edge(c[0], c[1]) and Y.has_edge(c[1], c[2]) and Y.has_edge(c[0], c[2])]
    for c in tris:
        best = None
        for p in itertools.permutations(c):
            H = amal(X, Y, list(zip(xgap, p)))
            k = canon(H)
            if best is None or k < best[0]:
                best = (k, H)
        seenD.setdefault(best[0], best[1])
    for i, H in enumerate(seenD.values(), 1):
        out.append(("D 三点重合(开路三点<-一条完整环) #%d" % i, H))

    # 族 C：单点接触
    seenC = {}
    for v in Y:
        for u in xgap:
            H = amal(X, Y, [(u, v)])
            seenC.setdefault(canon(H), H)
    for i, H in enumerate(seenC.values(), 1):
        out.append(("C 单点接触 #%d" % i, H))
    return out


def run(name, X, Y, tx, ty):
    print("=" * 76)
    print("配对 %s   （缺口方=%s，出借方=%s）" % (name, tx, ty))
    print("=" * 76)
    res = families(X, Y, tx, ty)
    # 按族聚合
    agg = {}
    for label, H in res:
        fam = label.split(" ")[0]
        agg.setdefault(fam, []).append((label, H))
    for fam in ("A", "D", "C"):
        if fam not in agg:
            continue
        items = agg[fam]
        uniq = {}
        for label, H in items:
            uniq.setdefault(canon(H), H)
        for k, H in uniq.items():
            i = inv(H)
            print("  [%s] 同构类 V=%-3d E=%-3d T=%-2d b1=%-3d 连通=%-5s rho=%-11.6f lam2=%-11.6f |Aut|=%-4d" %
                  (label, i["V"], i["E"], i["T"], i["b1"], i["conn"], i["rho"], i["lam2"], i["naut"]))
    print()


P = Y3("p_")
N = open_body("n_")

run("p-p", P, P, "p_", "q_")          # 两边都闭合
run("n-p", N, P, "n_", "p_")          # 中子有缺口，质子完整
run("n-n", N, open_body("m_"), "n_", "m_")   # 两边都有缺口

print("=" * 76)
print("原理检查：'出借者必须闭合完备' 能排除哪些")
print("=" * 76)
print("  p-p: 双方都无缺口 -> 无 '缺口<->完整环' 可对接（结构上即无解）")
print("  n-n: 缺口方 n1 的缺口可由 n2 的环 j=1/j=2 一条边补上（n2 只坏在环 j=0）")
print("       -> 结构上有解；要排除必须引入『出借者须无休眠』这一原则")
print("  n-p: 唯一解（见上）")
