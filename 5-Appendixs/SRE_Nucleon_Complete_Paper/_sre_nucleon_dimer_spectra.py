# -*- coding: utf-8 -*-
"""两体拼接的谱学细算 + 目标量表达式搜索。
不写论文，只做数值探查。
"""
import sys, itertools
import numpy as np
import networkx as nx
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

M_P = 938.27208816
M_N = 939.56542052
M_E = 0.51099895000
DM = M_N - M_P
ALPHA = 1.0 / 137.035999084
B_D = 2.224566


def sec(t):
    print("\n" + "=" * 74 + "\n" + t + "\n" + "=" * 74)


def Y3(pref=""):
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge(pref + "c%d" % i, pref + "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge(pref + "L0%d" % j, pref + "L1%d" % j)
        G.add_edge(pref + "L1%d" % j, pref + "L2%d" % j)
        G.add_edge(pref + "L2%d" % j, pref + "L0%d" % j)
    return G


P = Y3()
N = nx.relabel_nodes(P.copy(), {v: "n_" + v for v in P.nodes()})
N.remove_edge("n_L02", "n_L22")


def spectrum(G):
    """单连通图：返回降序特征值数组"""
    return np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))


def mult(ev, tol=1e-9):
    out = []
    for v in ev:
        if out and abs(out[-1][0] - v) < tol:
            out[-1][1] += 1
        else:
            out.append([float(v), 1])
    return [(round(v, 9), m) for v, m in out]


def topo(G):
    V, E = G.number_of_nodes(), G.number_of_edges()
    c = nx.number_connected_components(G)
    return V, E, E - V + c, sum(nx.triangles(G).values()) // 3


def amalgam(P, N, pairs):
    m = {}
    for pv, nv in pairs:
        m[nv] = pv
    H = nx.Graph()
    for u, v in P.edges():
        H.add_edge(u, v)
    for u, v in N.edges():
        uu, vv = m.get(u, u), m.get(v, v)
        if uu != vv:
            H.add_edge(uu, vv)
    return H


sec("[1] 闭态与开态（环边休眠）的完整谱对照")
evP = spectrum(P)
print("  P 闭态 V=12 E=18 谱（值, 重数）：")
print("   ", mult(evP))
print("  最大特征值 rho = %.15f" % evP[-1])
print("  精确 rho 闭式 (7+sqrt13)/2 = %.15f" % ((7 + 13 ** 0.5) / 2))
# 开态单独作为连通图
evN = spectrum(N)
print("  N 开态 V=12 E=17 谱（值, 重数）：")
print("   ", mult(evN))
print("  最大特征值 rho = %.15f" % evN[-1])
print()
print("  谱差异（逐模对照，各自降序）：")
for i, (a, b) in enumerate(zip(evP[::-1], evN[::-1])):
    flag = "" if abs(a - b) < 1e-9 else "   <-- 不同"
    print("    k=%2d  闭 %.9f   开 %.9f   差 %+.9f%s" % (i, a, b, b - a, flag))

sec("[2] 变体 A（缺口两端贴环边）高精度")
A = amalgam(P, N, [("L00", "n_L02"), ("L10", "n_L22")])
evA = spectrum(A)
print("  V,E,b1,T =", topo(A))
print("  谱：", mult(evA))
print("  lam2 = %.15f" % evA[1])
print("  rho  = %.15f" % evA[-1])
print("  Pi1  = %.15f" % (evA[1] / evA[-1]))

sec("[3] 变体 D（开放路径三点贴环）高精度")
D = amalgam(P, N, [("L00", "n_L02"), ("L10", "n_L12"), ("L20", "n_L22")])
evD = spectrum(D)
print("  V,E,b1,T =", topo(D))
print("  谱：", mult(evD))
print("  lam2 = %.15f   (2-sqrt3 = %.15f)" % (evD[1], 2 - 3 ** 0.5))
print("  rho  = %.15f" % evD[-1])
print("  Pi1  = %.15f" % (evD[1] / evD[-1]))

sec("[4] 目标量")
T_DM = DM / M_P
T_BD = B_D / M_P
T_R = B_D / DM
T_A = B_D / (ALPHA * M_P)
DLAM = 1.0 - 0.527166091
DRHO_A = evA[-1] - evP[-1]
print("  dm_np/m_p        = %.15e" % T_DM)
print("  B_d/m_p          = %.15e" % T_BD)
print("  B_d/dm_np        = %.12f" % T_R)
print("  B_d/(alpha*m_p)  = %.12f" % T_A)
print("  1 - lam2(辐条开) = %.15f" % DLAM)
print("  rho(A) - rho(P)  = %.15f" % DRHO_A)
print("  [rho(A)-rho(P)]/rho(P) = %.12f" % (DRHO_A / evP[-1]))
print("  rho(A)/rho(P)    = %.12f" % (evA[-1] / evP[-1]))

sec("[5] 关键比值检验")
cands = {
    "drho / (dm_np/m_p)": DRHO_A / T_DM,
    "dlam2 / (dm_np/m_p)": DLAM / T_DM,
    "beta1^3 = 343": 343.0,
    "drho*rho": DRHO_A * evP[-1],
    "(rho(A)-rho(P))*Pi1": DRHO_A * (1 / evP[-1]),
    "1 - lam2(A)": 1 - evA[1],
    "1 - lam2(D)": 1 - evD[1],
    "lam2(A)": evA[1],
    "lam2(D)": evD[1],
}
for k, v in cands.items():
    print("  %-28s = %.12f" % (k, v))

sec("[6] sympy 简单表达式搜索")
try:
    from sympy import nsimplify, sqrt as S, pi as PI, Rational, GoldenRatio, E as SE
    consts = [S(3), S(13), S(5), PI, GoldenRatio, SE, Rational(1, 2)]
    targets = {
        "dm_np/m_p": T_DM,
        "B_d/m_p": T_BD,
        "B_d/dm_np": T_R,
        "B_d/(alpha m_p)": T_A,
        "drho_A": DRHO_A,
        "drho/rho": DRHO_A / evP[-1],
        "rho(A)/rho(P)": evA[-1] / evP[-1],
        "1-lam2(A)": 1 - evA[1],
        "dlam2_spoke": DLAM,
    }
    for k, v in targets.items():
        r = nsimplify(v, consts, rational=True, tolerance=1e-6)
        print("  %-18s = %.12f  ->  %s" % (k, v, r))
except Exception as e:
    print("  sympy 不可用：", e)

sec("[7] 单位口径反查：若 B_d = k * dm_np，k 必须是什么")
print("  k = B_d/dm_np = %.9f" % T_R)
print("  连分数收敛：")
from fractions import Fraction
fr = Fraction(T_R).limit_denominator(200)
print("    T_R ~ %s = %.9f  (dev %.4f%%)" % (fr, float(fr), 100 * abs(float(fr) - T_R) / T_R))
for den in range(1, 220):
    f = Fraction(T_R).limit_denominator(den)
    d = abs(float(f) - T_R) / T_R
    if d < 2e-3:
        print("    %-8s = %.9f   dev %.5f%%" % (f, float(f), 100 * d))
print("\n[done]")
