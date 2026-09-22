# -*- coding: utf-8 -*-
"""
共享环分析：变体 A（缺口被一条环边补齐 => 新建混合环）与 变体 D（开态三点与
一条完整环三点完全重合 => 环被两体共有）的结构与谱学对照。

只做计算，不改论文。
"""
import sys, json, itertools, math
import numpy as np
import networkx as nx
import sympy as sp
from networkx.algorithms.isomorphism import GraphMatcher
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
X = sp.Symbol("x")

M_P = 938.27208816
M_N = 939.56542052
DM = (M_N - M_P) / M_P                 # 1.37850e-3
B_D = 2.224566                         # MeV
DM_MEV = M_N - M_P                     # 1.293332 MeV


# ---------------------------------------------------------------- 构造
def Y3(pre=""):
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        G.add_edge("%sL0%d" % (pre, j), "%sL1%d" % (pre, j))
        G.add_edge("%sL1%d" % (pre, j), "%sL2%d" % (pre, j))
        G.add_edge("%sL2%d" % (pre, j), "%sL0%d" % (pre, j))
    return G


def openN(pre=""):
    """中子开态：环 j=0 上的一条环边休眠（L00-L10 消失，环变成 3 点开路）"""
    G = Y3(pre)
    G.remove_edge("%sL00" % pre, "%sL10" % pre)
    return G


def amalgam(P, N, pairs):
    rep = {nn: pn for pn, nn in pairs}
    f = lambda x: rep.get(x, x)
    H = nx.Graph()
    for G in (P, N):
        for u, v in G.edges():
            H.add_edge(f(u), f(v))
    return H


def mapped(P, N, pairs):
    """返回 (p 的边集, n 映射后的边集, 双边集)"""
    rep = {nn: pn for pn, nn in pairs}
    f = lambda x: rep.get(x, x)
    EP = {tuple(sorted((f(u), f(v)))) for u, v in P.edges()}
    EN = {tuple(sorted((f(u), f(v)))) for u, v in N.edges()}
    return EP, EN, EP & EN


P = Y3("p_")
N = openN("n_")
EDGE_CLOSE = ("p_L00", "p_L10")          # 质子侧被借用的那条环边

A = amalgam(P, N, [("p_L00", "n_L00"), ("p_L10", "n_L10")])
D = amalgam(P, N, [("p_L00", "n_L00"), ("p_L10", "n_L10"), ("p_L20", "n_L20")])


# ---------------------------------------------------------------- 谱工具
def lap_exact(G):
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
    return M


def closed_forms(G, name):
    """精确特征多项式 -> 因式分解 -> 根（能解出闭式的给出闭式）"""
    M = lap_exact(G)
    ch = sp.factor(M.charpoly(X).as_expr())
    print("  [%s] 特征多项式（因式化）:" % name)
    for f, m in sp.factor_list(ch)[1]:
        print("      (%s)^%d" % (sp.nsimplify(f), m))
    print("  [%s] 根:" % name)
    for f, m in sp.factor_list(ch)[1]:
        rts = sp.roots(sp.Poly(f, X), X) if sp.degree(f, X) <= 4 else {}
        if rts:
            for r, rm in rts.items():
                print("      %-46s 重数 %d" % (sp.nsimplify(sp.simplify(r)), m * rm))
        else:
            num = np.roots([float(c) for c in sp.Poly(f, X).all_coeffs()])
            print("      deg=%d 无根式解，数值: %s" % (sp.degree(f, X), np.round(np.sort(num), 9)))
    return ch


def stats(G, name):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    T = sum(nx.triangles(G).values()) // 3
    deg = dict(G.degree())
    n4 = sum(1 for v in deg if deg[v] == 4)
    n2 = sum(1 for v in deg if deg[v] == 2)
    # 自同构
    naut = sum(1 for _ in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), 200000))
    # 轨道
    seen, groups = [], []
    orb = {}
    for m in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), 200000):
        for v in G:
            orb.setdefault(v, set()).add(m[v])
    for v in G:
        g = frozenset(orb[v])
        if g not in seen:
            seen.append(g)
            groups.append(sorted(map(str, g)))
    # 边轨道
    eo = {}
    for m in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), 200000):
        for e in G.edges():
            eo.setdefault(tuple(sorted(e)), set()).add(tuple(sorted((m[e[0]], m[e[1]]))))
    eclasses = []
    done = set()
    for e in G.edges():
        k = tuple(sorted(e))
        if k in done:
            continue
        cl = {tuple(sorted(x)) for x in eo[k]} | {k}
        # 传递闭包
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
        eclasses.append(sorted(cl))
    print("### %s" % name)
    print("    V=%d  E=%d  T=%d  beta1=%d  连通=%s" %
          (G.number_of_nodes(), G.number_of_edges(), T,
           G.number_of_edges() - G.number_of_nodes() + 1, nx.is_connected(G)))
    print("    度序列:", sorted(deg.values(), reverse=True), " 度4顶点=%d 度2顶点=%d" % (n4, n2))
    print("    |Aut|=%d   顶点轨道=%d %s" % (naut, len(groups), [len(g) for g in groups]))
    print("    边轨道=%d  各轨大小=%s" % (len(eclasses), [len(c) for c in eclasses]))
    print("    rho=%.12f   lambda2=%.12f   Pi1=%.12f  trace=%.1f" %
          (ev[-1], ev[1], ev[1] / ev[-1], ev.sum()))
    print("    谱:", np.round(ev, 9))
    return ev


# ---------------------------------------------------------------- 主
print("=" * 78)
print("0. 单核子基准")
print("=" * 78)
eP = stats(P, "质子（闭态）")
eN = stats(N, "中子（开态，一条环边休眠）")
print("    rho 差 = %.3e   lambda2 差 = %.3e  （rho/lambda2 均为过渡不变量）" %
      (abs(eP[-1] - eN[-1]), abs(eP[1] - eN[1])))

print()
print("=" * 78)
print("1. 变体 A 与 变体 D 的结构/谱对照")
print("=" * 78)
eA = stats(A, "变体 A（两点对接：缺口两端 <- 一条环边两端）")
print()
eD = stats(D, "变体 D（三点重合：开态开路 <- 一条完整环）")

print()
print("--- 双属（两体同时拥有）的边 ---")
for tag, H in (("A", A), ("D", D)):
    EP, EN, both = mapped(P, N, [("p_L00", "n_L00"), ("p_L10", "n_L10")] if tag == "A" else
                          [("p_L00", "n_L00"), ("p_L10", "n_L10"), ("p_L20", "n_L20")])
    print("  %s: |E_p|=%d |E_n|=%d 双属边 %d 条 -> %s" %
          (tag, len(EP), len(EN), len(both), sorted(map(str, both))))

print()
print("=" * 78)
print("2. 变体 D 的精确谱")
print("=" * 78)
closed_forms(D, "D")
print()
closed_forms(A, "A")

print()
print("=" * 78)
print("3. 变体 D 的整数性稀有度（同度序列随机图）")
print("=" * 78)
dsq = sorted(dict(D.degree()).values(), reverse=True)
rng = np.random.default_rng(7)
n6 = 0
NTRY = 3000
best = []
for _ in range(NTRY):
    H = nx.Graph(nx.configuration_model(dsq, seed=int(rng.integers(1 << 31))))
    H.remove_edges_from(nx.selfloop_edges(H))
    if not nx.is_connected(H):
        continue
    ev = np.linalg.eigvalsh(nx.laplacian_matrix(H).toarray())
    if abs(ev[-1] - 6.0) < 1e-6:
        n6 += 1
    best.append(ev[-1])
best = np.array(best)
print("  同度序列随机图样本 = %d" % len(best))
print("  rho 分布: min=%.6f  中位=%.6f  max=%.6f" %
      (best.min(), np.median(best), best.max()))
print("  rho 恰为整数 6（1e-6 内）的样本数 = %d  → 稀有度 %.2e" %
      (n6, n6 / max(1, len(best))))
print("  落在 [5.99,6.01] 的比例 = %.4f" % float(np.mean(np.abs(best - 6) < 0.01)))

print()
print("=" * 78)
print("4. 能量记账：B_d 与各候选标度")
print("=" * 78)
print("  实测: B_d = %.6f MeV,  Delta m_np = %.6f MeV,  B_d/Dm = %.6f" %
      (B_D, DM_MEV, B_D / DM_MEV))
print("  单核子标定: Delta m_np/m_p = %.9f = alpha*Pi1  (Pi1 = lambda2/rho)" % DM)
print()
rows = []
for tag, H in (("A", A), ("D", D)):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(H).toarray()))
    T = sum(nx.triangles(H).values()) // 3
    V, E = H.number_of_nodes(), H.number_of_edges()
    b1 = E - V + 1
    rows.append((tag, V, E, T, b1, ev[-1], ev[1], ev[1] / ev[-1]))
print("  %-4s %-4s %-4s %-4s %-5s %-12s %-12s %-10s" %
      ("变体", "V", "E", "T", "b1", "rho", "lambda2", "Pi1"))
for r in rows:
    print("  %-4s %-4d %-4d %-4d %-5d %-12.6f %-12.6f %-10.6f" % r)
print()
print("  若“一个闭合单元 = Delta m_np”:")
for tag, H in (("A", A), ("D", D)):
    T = sum(nx.triangles(H).values()) // 3
    pred = (T - 5) * DM_MEV      # 5 = 纯环总数(3质子+2中子)
    print("    %s: 新增闭合单元 = %d  -> B_d^pred = %.6f MeV  (偏差 %+.1f%%)" %
          (tag, T - 5, pred, 100 * (pred - B_D) / B_D))
print("    参照: 若按 b1 增量, A: %d  D: %d" %
      ((A.number_of_edges() - A.number_of_nodes() + 1) - 13,
       (D.number_of_edges() - D.number_of_nodes() + 1) - 13))
print()
cands = {
    "B_d/Dm 实测": B_D / DM_MEV,
    "V/b1 (D)": 21 / 13,
    "V/b1 (A)": 22 / 14,
    "E/b1 (D)": 33 / 13,
    "T+? ...": None,
    "(T)/b1 (D)": 5 / 13,
    "(E-V)/b1 (D)": 12 / 13,
}
for k, v in cands.items():
    if v is None:
        continue
    print("    %-16s = %.6f   偏差 %+8.3f%%" % (k, v, 100 * (v - B_D / DM_MEV) / (B_D / DM_MEV)))
print()
print("  其它可能标度对照（只列，不作证据）:")
extra = {
    "(rho_D/2 - 1)*2": (6.0 / 2 - 1) * 2,
    "rho_D/rho_P": 6.0 / eP[-1],
    "rho_D/rho_P^? ": 6.0 / (eP[-1] ** 2),
    "b1_D/b1_P": 13 / 7,
    "b1_D/b1_N": 13 / 6,
    "T_D/T_P": 5 / 3,
    "E_D/E_P": 33 / 18,
    "V_D/V_P": 21 / 12,
    "sqrt(3)": math.sqrt(3),
}
for k, v in extra.items():
    print("    %-16s = %.6f   偏差 %+8.3f%%" % (k, v, 100 * (v - B_D / DM_MEV) / (B_D / DM_MEV)))

print()
print("=" * 78)
print("5. 变体 D 的休眠边连续化（权重 1 -> t）：谱怎么走")
print("=" * 78)
# D 中那条“借用”的边就是 p_L00-p_L10；把它与 n 的休眠边并成一个权重 t 的边
# 即：闭态 D 的 6 个环去掉最弱一环，或连续扫描 n 侧休眠边
W = D.copy()
e_borrow = ("p_L00", "p_L10")
for t in (1.0, 0.9, 0.7, 0.5, 0.3, 0.1, 0.0):
    H = D.copy()
    H[e_borrow[0]][e_borrow[1]]["weight"] = t
    L = nx.laplacian_matrix(H, weight="weight").toarray().astype(float)
    ev = np.sort(np.linalg.eigvalsh(L))
    print("  t=%.2f  lambda2=%.9f  lambda3=%.9f  split=%.9f  rho=%.9f" %
          (t, ev[1], ev[2], ev[2] - ev[1], ev[-1]))

print()
print("=" * 78)
print("6. 变体 D 图谱（节点角色）")
print("=" * 78)
deg = dict(D.degree())
print("  度4:", sorted([v for v in deg if deg[v] == 4]))
print("  度2:", sorted([v for v in deg if deg[v] == 2]))
print("  度3:", len([v for v in deg if deg[v] == 3]))
tri = []
for a, b, c in itertools.combinations(D.nodes(), 3):
    if D.has_edge(a, b) and D.has_edge(b, c) and D.has_edge(a, c):
        tri.append(sorted(map(str, (a, b, c))))
print("  三角环 (%d 个):" % len(tri))
for t in tri:
    # 标注每条边的归属
    EP, EN, both = mapped(P, N, [("p_L00", "n_L00"), ("p_L10", "n_L10"), ("p_L20", "n_L20")])
    own = []
    for u, v in itertools.combinations(t, 2):
        k = (u, v) if (u, v) in both or (v, u) in both else None
        kk = tuple(sorted((u, v)))
        own.append("共" if kk in both else "单")
    print("     %s  边归属[%s]" % (t, "/".join(own)))
