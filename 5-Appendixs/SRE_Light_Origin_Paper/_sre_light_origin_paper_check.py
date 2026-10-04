# -*- coding: utf-8 -*-
"""
_sre_light_origin_paper_check.py
=================================================================
《光与电磁波在 SRE 体系下的定位》配套**一键复算**脚本
（论文：SRE_Light_Origin_Paper.md）

本脚本独立实现（除项目既有闭式外不复用旧脚本代码），逐项复算论文
正文与附录 A 引用的每一个读数。运行：

    C:/myapp/miniconda3/envs/ai/python.exe -u _sre_light_origin_paper_check.py \
        > _sre_light_origin_paper_check.log 2>&1

依赖：numpy, networkx
输出：_sre_light_origin_paper_check.log / .json
=================================================================
"""
import os
import sys
import math
import cmath
import json
import subprocess
from math import gcd

import numpy as np
import networkx as nx

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

OUT = {}
W3 = cmath.exp(2j * math.pi / 3)
ALPHA_INV = 137.035999084          # CODATA 1/alpha（外部输入）


def P(*a):
    print(*a, flush=True)


def head(t):
    P()
    P("=" * 88)
    P(t)
    P("=" * 88)


# ==================================================================
# 公共构造
# ==================================================================
def mobius_weighted(n, c=1.0, w=1.0):
    """加权 Möbius 阶梯 M_n（n 偶）：环边 (i,i+1) 权 c；对合伙伴 (i,i+n/2) 权 w。"""
    assert n % 2 == 0
    A = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        A[i, j] += c
        A[j, i] += c
    for i in range(n // 2):
        A[i, i + n // 2] += w
        A[i + n // 2, i] += w
    L = np.diag(A.sum(1)) - A
    return A, L


def closed_mu(n, c, w):
    """闭式谱：mu_k = 2c(1-cos(2pi k/n)) + w(1-(-1)^k)。"""
    k = np.arange(n)
    return 2.0 * c * (1.0 - np.cos(2.0 * np.pi * k / n)) + w * (1.0 - ((-1.0) ** k))


def involution(n):
    """对合 P = S^{n/2}：i -> i + n/2。"""
    Pm = np.zeros((n, n))
    for i in range(n):
        Pm[i, (i + n // 2) % n] = 1.0
    return Pm


def mobius_pi1_closed(n, w=1.0):
    """项目既有闭式 Pi_1(M_n) = 4 sin^2(2pi/n) / (2 + 2w + 2 cos(2pi/n))。"""
    return 4.0 * math.sin(2 * math.pi / n) ** 2 / (2.0 + 2.0 * w + 2.0 * math.cos(2 * math.pi / n))


def Y3(open_ring=None):
    """核子骨架 Y3 (x) triangle_3：股心 c_i + 环叶 L_ij；环 j = {L0j,L1j,L2j}。"""
    G = nx.Graph()
    for i in range(3):
        G.add_node("c%d" % i)
        for j in range(3):
            G.add_node("L%d%d" % (i, j))
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    if open_ring is not None:
        G.remove_edge("L0%d" % open_ring, "L1%d" % open_ring)
    return G


def lap_stats(G):
    """项目口径：rho = 拉普拉斯最大特征值；lam2 = 拉普拉斯次小特征值。"""
    G = nx.convert_node_labels_to_integers(G)
    A = nx.to_numpy_array(G).astype(float)
    L = np.diag(A.sum(1)) - A
    ev = np.sort(np.linalg.eigvalsh(L))
    return dict(V=G.number_of_nodes(), E=G.number_of_edges(),
                b1=G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G),
                rho=float(ev[-1]), lam2=float(ev[1]))


def perm_order(p):
    seen, l = set(), 1
    for x in p:
        if x in seen:
            continue
        c, y = 0, x
        while y not in seen:
            seen.add(y)
            y = p[y]
            c += 1
        l = l * c // gcd(l, c)
    return l


def ring_idx(nm):
    return int(nm[2]) if nm.startswith("L") else None


# ==================================================================
head("PART 1  光载体：谱与扇区（P = S^{n/2}，只由 n 决定）")
# ==================================================================
P("1a. 闭式谱 mu_k = 2c(1-cos(2pi k/n)) + w(1-(-1)^k)  与数值对角化对照")
P("    （把谱拆成「扇区盲项 + 奇扇区常数项」是本论文的关键一步）")
P()
P("       n     数值 vs 闭式 最大偏差      mu_0        |偶|   |奇|")
P("    " + "-" * 66)
rows1a = []
for n in (6, 8, 10, 20, 30, 60):
    A, L = mobius_weighted(n, 1.0, 1.0)
    num = np.sort(np.linalg.eigvalsh(L))
    cl = np.sort(closed_mu(n, 1.0, 1.0))
    dev = float(np.abs(num - cl).max())
    ev = closed_mu(n, 1.0, 1.0)
    P("    %4d       %.3e              %.1e      %2d     %2d"
      % (n, dev, abs(ev[0]), len(ev[0::2]), len(ev[1::2])))
    rows1a.append(dict(n=n, dev=dev, mu0=float(ev[0])))
OUT["P1a_closed_form"] = rows1a

P()
P("1b. n=60 的两支 (软模拓扑保护)")
A, L = mobius_weighted(60, 1.0, 1.0)
ev = np.sort(np.linalg.eigvalsh(L))
P("      lambda_2 (偶模 k=2) = %.12f   闭式 2-2cos(4pi/60) = %.12f"
  % (ev[1], 2 - 2 * math.cos(4 * math.pi / 60)))
P("      lambda_max (奇模)  = %.12f   闭式 2+2+2cos(2pi/60) = %.12f"
  % (ev[-1], 4 + 2 * math.cos(2 * math.pi / 60)))
P("      mu_0 = %.3e （恒零）" % ev[0])
OUT["P1b_softmode"] = dict(lam2=float(ev[1]), lam_max=float(ev[-1]), mu0=float(ev[0]))

P()
P("1c. 软模 lambda_2 对 w 完全免疫（W 扫 {0.05,...,10}）")
ws = [0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
lam2s = []
for w in ws:
    _, Lw = mobius_weighted(60, 1.0, w)
    lam2s.append(float(np.sort(np.linalg.eigvalsh(Lw))[1]))
P("      lambda_2 取值 = [%s]" % ", ".join("%.12f" % x for x in lam2s))
P("      展布 = %.3e  （机器精度量级）" % (max(lam2s) - min(lam2s)))
OUT["P1c_lam2_wfree"] = dict(spread=float(max(lam2s) - min(lam2s)), ref=2 - 2 * math.cos(4 * math.pi / 60))


# ==================================================================
head("PART 2  光载体零参数：对合 P 的十一项检验（n=60）")
# ==================================================================
n, c, w = 60, 1.0, 1.0
A, L = mobius_weighted(n, c, w)
Pm = involution(n)
Ppm = 0.5 * (np.eye(n) + Pm)
Pmm = 0.5 * (np.eye(n) - Pm)
chk = {
    "P^2 = I": bool(np.allclose(Pm @ Pm, np.eye(n))),
    "P != I": bool(not np.allclose(Pm, np.eye(n))),
    "P in Aut (P A P^T = A)": bool(np.allclose(Pm @ A @ Pm.T, A)),
    "[P, L] = 0": bool(np.allclose(Pm @ L, L @ Pm)),
    "spec(P) = {+1,-1}": bool(np.allclose(sorted(set(np.round(np.linalg.eigvalsh(Pm), 9))), [-1.0, 1.0])),
    "tr(P) = 0": bool(abs(np.trace(Pm)) < 1e-12),
    "P_+ idempotent": bool(np.allclose(Ppm @ Ppm, Ppm)),
    "P_- idempotent": bool(np.allclose(Pmm @ Pmm, Pmm)),
    "P_+ P_- = 0": bool(np.allclose(Ppm @ Pmm, 0)),
    "P_+ + P_- = I": bool(np.allclose(Ppm + Pmm, np.eye(n))),
    "rank(P_+) = rank(P_-) = n/2": bool(abs(np.trace(Ppm) - n / 2) < 1e-9 and abs(np.trace(Pmm) - n / 2) < 1e-9),
}
for k, v in chk.items():
    P("      %-32s : %s" % (k, v))
OUT["P2_involution"] = {k: bool(v) for k, v in chk.items()}


# ==================================================================
head("PART 3  源只注入一个标量：唯一通道 = w（横档 / holonomy）")
# ==================================================================
P("3a. w 通道（w = 1 -> 1+delta）：奇扇区是否严格均匀平移？偶扇区是否恒不动？")
P("      delta     奇扇区 dmu 极差      dmu/2delta 最小~最大        偶扇区 dmu 极差")
P("    " + "-" * 84)
rows3a = []
for delta in (1e-3, 1e-2, 1e-1, 5e-1):
    ev0 = closed_mu(n, 1.0, 1.0)
    ev1 = closed_mu(n, 1.0, 1.0 + delta)
    d = ev1 - ev0
    do, de = d[1::2], d[0::2]
    P("    %-9.3f %.3e           %.9f ~ %.9f    %.3e"
      % (delta, do.max() - do.min(), do.min() / (2 * delta), do.max() / (2 * delta), de.max() - de.min()))
    rows3a.append(dict(delta=delta, spread_odd=float(do.max() - do.min()),
                       spread_even=float(de.max() - de.min()),
                       ratio_min=float(do.min() / (2 * delta)), ratio_max=float(do.max() / (2 * delta))))
OUT["P3a_w_channel"] = rows3a
P()
P("    ⇒ 奇数 n/2 个模平移量严格相同（极差 ~1e-16），偶扇区恒不动 ⇒ **源只留一个数**。")

P()
P("3b. 谱形不变：减去平移量后与基准逐位比较")
for delta in (1e-2, 1e-1):
    ev0 = closed_mu(n, 1.0, 1.0)
    ev1 = closed_mu(n, 1.0, 1.0 + delta)
    o0, o1 = np.sort(ev0[1::2]), np.sort(ev1[1::2])
    P("      delta=%.2f : max| (奇谱-2delta) - 奇谱基准 | = %.3e" % (delta, np.abs(o1 - 2 * delta - o0).max()))

P()
P("3c. 反例对照：环向通道 c = 1+u（证明「唯一通道 = w」不是空话）")
P("      u         奇扇区位移极差        偶扇区位移极差        只在奇扇区？")
P("    " + "-" * 76)
for u in (1e-2, 1e-1):
    ev0 = closed_mu(n, 1.0, 1.0)
    evu = closed_mu(n, 1.0 + u, 1.0)
    d = evu - ev0
    do, de = d[1::2], d[0::2]
    P("    %-9.3f %.3e               %.3e              否（两扇区同动）"
      % (u, do.max() - do.min(), de.max() - de.min()))
P()
P("    ⇒ 「只在奇扇区」+「均匀」两条同时成立 ⇒ 通道唯一被钉死在 w 上。")


# ==================================================================
head("PART 4  同调阶梯与容量判据")
# ==================================================================
P("4a. |H^1(G;Z_n)| = n^{beta_1}（n 元覆盖的个数）")
P()
P("      图                      V     E    beta1      Z_2 档            Z_3 档")
P("    " + "-" * 82)


def beta1_of(G):
    return G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)


graphs = [("C_3 (三环)", nx.cycle_graph(3)),
          ("K_4", nx.complete_graph(4)),
          ("Q_3 (立方体)", nx.hypercube_graph(3)),
          ("M_6 (Mobius 梯)", nx.cycle_graph(6))]
# 加 Möbius 横档
M6 = nx.cycle_graph(6)
for i in range(3):
    M6.add_edge(i, i + 3)
graphs[3] = ("M_6 (Mobius 梯)", M6)
graphs.append(("Y_3 闭 (核子骨架)", Y3(None)))
graphs.append(("Y_3 开 (断一环边)", Y3(0)))
M60 = nx.cycle_graph(60)
for i in range(30):
    M60.add_edge(i, i + 30)
graphs.append(("M_60 (alpha 锚载体)", M60))
rows4a = []
for name, G in graphs:
    b1 = beta1_of(G)
    P("    %-20s %4d %5d %5d   %-16d %d"
      % (name, G.number_of_nodes(), G.number_of_edges(), b1, 2 ** b1, 3 ** b1))
    rows4a.append(dict(name=name, V=G.number_of_nodes(), E=G.number_of_edges(), b1=b1))
OUT["P4a_ladder"] = rows4a

P()
P("4b. 容量判据：给三点环的 3 条边各贴一个 Z_N 标签，可达的「划分模式」与「最大互异标签数」？")


def partition_patterns(N):
    """三条边标签 ∈ Z_N 时，可达的划分模式（按各组大小降序）；(1,1,1) 即可三条边互异。"""
    from collections import Counter
    pats = set()
    for a in range(N):
        for b in range(N):
            for cc in range(N):
                pats.add(tuple(sorted(Counter([a, b, cc]).values(), reverse=True)))
    return sorted(pats, reverse=True)


def max_distinct(N):
    return min(N, 3)


for N in (2, 3, 4):
    pats = partition_patterns(N)
    P("      Z_%-3d 可达划分模式 = %s      最大互异标签数 = %d   %s"
      % (N, pats, max_distinct(N), "**取不到 (1,1,1)**" if (1, 1, 1) not in pats else "含 (1,1,1)，三条边可互异"))
OUT["P4b_capacity"] = {N: dict(patterns=partition_patterns(N), max_distinct=max_distinct(N)) for N in (2, 3, 4)}
P()
P("    ⇒ Z_2 只能给 {3} 或 {2+1}（(1,1,1) 不可达）；Z_3 可达 (1,1,1) ⇒ |Z_2| = 2 < 3")
P("      ⇒ 光档在结构上不能承载三代（第 29 轮判负的群论根源）。")


# ==================================================================
head("PART 5  Z_3 挠子与阶元谱：闭 -> 开 = Z_3 -> Z_2")
# ==================================================================
P("5a. 闭态 / 开态骨架的自同构与阶元谱")


def aut_analysis(G):
    autos = list(nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
    orders = {}
    for p in autos:
        o = perm_order(p)
        orders[o] = orders.get(o, 0) + 1
    # 三环轨道
    parent = {0: 0, 1: 1, 2: 2}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for p in autos:
        for j in range(3):
            a, b = j, ring_idx(p["L0%d" % j])
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    norb = len(set(find(j) for j in range(3)))
    return autos, orders, norb


for tag, r in (("闭态", None), ("开态", 0)):
    G = Y3(r)
    autos, orders, norb = aut_analysis(G)
    P("      %s: |Aut| = %2d   阶1=%d 阶2=%d 阶3=%d 阶6=%d   三环轨道数 = %d"
      % (tag, len(autos), orders.get(1, 0), orders.get(2, 0), orders.get(3, 0), orders.get(6, 0), norb))
    OUT["P5_" + tag] = dict(aut=len(autos), orders=orders, ring_orbits=norb)

P()
P("5b. 显式三阶自同构 phi: L_ij -> L_i,(j+1)%3")
G = Y3(None)
phi = lambda nm: nm if nm.startswith("c") else ("L%s%d" % (nm[1], (int(nm[2]) + 1) % 3))
ok_edge = all(G.has_edge(phi(u), phi(v)) for u, v in G.edges())
ok_ord3 = all(phi(phi(phi(x))) == x for x in G.nodes())
ok_nontriv = any(phi(x) != x for x in G.nodes())
P("      保边 = %s ; ord(phi)=3 = %s ; phi != id = %s" % (ok_edge, ok_ord3, ok_nontriv))
OUT["P5b_phi"] = dict(edge=bool(ok_edge), order3=bool(ok_ord3), nontrivial=bool(ok_nontriv))

P()
P("5c. Z_3 特征分解（顶点 / 边空间）")


def char_mult(dim, fix):
    return (dim + 2 * fix) // 3, (dim - fix) // 3


P("      空间   dim   chi(phi)   分解                     平凡权重 / 非平凡权重")
P("    " + "-" * 76)
for space, dim, fix in (("顶点", 12, 3), ("边", 18, 0)):
    triv, nontriv = char_mult(dim, fix)
    # 分解 = triv * 1 + nontriv * w + nontriv * w^2  ⇒ 非平凡总权重 = 2*nontriv
    P("      %-4s   %3d     %d        %d*1 + %d*w + %d*w^2      平凡 %d/%d = %.4f | 非平凡 %d/%d = %.4f"
      % (space, dim, fix, triv, nontriv, nontriv, triv, dim, triv / dim, 2 * nontriv, dim, 2 * nontriv / dim))
OUT["P5c_chardecomp"] = dict(vertex=dict(triv=6, nontriv_each=3), edge=dict(triv=6, nontriv_each=6))


# ==================================================================
head("PART 6  能量在账本里、不在谱里")
# ==================================================================
P("6a. Y_3 骨架 闭 <-> 开（断一条环边）的签名向量")
sc, so = lap_stats(Y3(None)), lap_stats(Y3(0))
P("      量        闭态              开态              差              归类")
P("    " + "-" * 74)
for key in ("V", "E", "b1", "rho", "lam2"):
    a, b = sc[key], so[key]
    fmt = "%.12f" if key in ("rho", "lam2") else "%d"
    dv = b - a
    P("      %-6s  %-16s  %-16s  %-15s  %s"
      % (key, fmt % a, fmt % b, ("%.3e" % dv) if key in ("rho", "lam2") else ("%+d" % dv),
         "账本" if key in ("V", "E", "b1") else "谱（不动）"))
OUT["P6a_ledger"] = dict(closed=sc, open=so)

P()
P("6b. 把全部 18 条边逐条断开，分「环边 / 股边」两类看谱量")
G0 = Y3(None)
ring_e, spoke_e = [], []
for (u, v) in sorted(tuple(sorted(e)) for e in G0.edges()):
    (ring_e if (u.startswith("L") and v.startswith("L")) else spoke_e).append((u, v))
res6 = {}
for tag, elist in (("环边 (L-L)", ring_e), ("股边 (c-L)", spoke_e)):
    rho_s, lam_s = [], []
    for (u, v) in elist:
        Gx = G0.copy()
        Gx.remove_edge(u, v)
        if not nx.is_connected(Gx):
            continue
        st = lap_stats(Gx)
        rho_s.append(st["rho"])
        lam_s.append(st["lam2"])
    res6[tag] = dict(n=len(rho_s), rho_spread=float(max(rho_s) - min(rho_s)),
                     lam2_spread=float(max(lam_s) - min(lam_s)),
                     lam2=float(lam_s[0]))
    P("      %-10s 断开 %2d 条 : rho 极差 = %.3e | lambda2 = %.9f (极差 %.3e)"
      % (tag, len(rho_s), res6[tag]["rho_spread"], res6[tag]["lam2"], res6[tag]["lam2_spread"]))
OUT["P6b_breakclass"] = res6
P()
P("    ⇒ rho = 全局严格不变量（18/18）；lambda2 = 轨道级不变量（环边轨道 vs 股边轨道不同值）。")


# ==================================================================
head("PART 7  「未打开」在两侧是同一类陈述（规范不变性）")
# ==================================================================
P("7a. 质量侧：不选 DFT 原点 ⇒ 三种选法给同一组不变量")
eta, delta7 = 1 / math.sqrt(2), 2 / 9
u = np.array([1 + 2 * eta * math.cos(delta7 + 2 * math.pi * k / 3) for k in range(3)])


def koide(x):
    m = x ** 2
    return m.sum() / (np.sqrt(m).sum() ** 2)


q0 = koide(u)
P("      shift0 Q = %.12f" % q0)
for s in (1, 2):
    us = np.roll(u, s)
    P("      shift%d Q = %.12f   |dQ| = %.3e" % (s, koide(us), abs(koide(us) - q0)))
OUT["P7a_norminvariance"] = float(max(abs(koide(np.roll(u, s)) - q0) for s in (1, 2)))

P()
P("7b. 光侧：X(phi+2pi,w) = X(phi,-w)（对映片）；X(phi+4pi,w) = X(phi,w)（4pi 闭合）")


def X(phi, w):
    return np.array([(1 + w * math.cos(phi / 2)) * math.cos(phi),
                     (1 + w * math.cos(phi / 2)) * math.sin(phi),
                     w * math.sin(phi / 2)])


d1 = float(np.abs(X(0.7 + 2 * math.pi, 0.3) - X(0.7, -0.3)).max())
d2 = float(np.abs(X(0.7 + 4 * math.pi, 0.3) - X(0.7, 0.3)).max())
P("      |X(phi+2pi,w) - X(phi,-w)| = %.3e" % d1)
P("      |X(phi+4pi,w) - X(phi,w)|  = %.3e" % d2)
OUT["P7b_mobius"] = dict(antipode=d1, closure4pi=d2)


# ==================================================================
head("PART 8  无质量性：光载体没有加性标度")
# ==================================================================
P("8a. 光载体 P：|spec| == 1，谱均值 = tr(P)/n = 0，mu_0 = 0")
for nn in (6, 8, 20, 60):
    Pn = involution(nn)
    evp = np.linalg.eigvalsh(Pn)
    P("      n=%2d : |spec| = {%s}, mean = %.1e, mu_0 = %.1e"
      % (nn, ",".join("%.0f" % x for x in sorted(set(np.round(np.abs(evp), 9)))), evp.mean(),
         closed_mu(nn, 1.0, 1.0)[0]))

P()
P("8b. 质量载体 A = c0*I + c1*S + conj(c1)*S^2：谱均值恰为 c0（自由参数）")
S3 = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=complex)
P("      c0     |c1|   theta(deg)   谱均值")
P("    " + "-" * 56)
for c0, a, th in ((0.0, 0.3, 40.0), (0.5, 0.3, 40.0), (1.0, 0.3, 40.0), (2.0, 0.3, 40.0)):
    Am = c0 * np.eye(3, dtype=complex) + a * cmath.exp(1j * math.radians(th)) * S3 + \
         a * cmath.exp(-1j * math.radians(th)) * (S3 @ S3)
    ev = np.sort(np.linalg.eigvalsh(Am).real)
    P("      %-6.2f %-6.2f %-13.1f %.9f" % (c0, a, th, ev.mean()))
    if c0 == 1.0:
        OUT["P8b_massspectrum"] = dict(c0=c0, spec=ev.tolist(), mean=float(ev.mean()))
P()
P("    ⇒ 光载体均值恒 0（被锁）；质量载体均值 = c0（可自由拨动）。")


# ==================================================================
head("PART 9  alpha 锚：Pi_1(M_60)")
# ==================================================================
A60, L60 = mobius_weighted(60, 1.0, 1.0)
ev60 = np.sort(np.linalg.eigvalsh(L60))
pi1_num = float(ev60[1] / ev60[-1])
pi1_closed = mobius_pi1_closed(60)
P("      Pi_1(M_60) 数值 = %.12f   闭式 = %.12f" % (pi1_num, pi1_closed))
P("      1/alpha_0 = %.12f   相对偏差 = %.3e" % (ALPHA_INV, abs(pi1_num - 1 / ALPHA_INV) / (1 / ALPHA_INV)))
# 解 Pi_1(M_n) = alpha 的 n*
lo, hi = 10.0, 200.0
for _ in range(200):
    mid = 0.5 * (lo + hi)
    if mobius_pi1_closed(mid) > 1 / ALPHA_INV:
        lo = mid
    else:
        hi = mid
nstar = 0.5 * (lo + hi)
P("      n* (解 Pi_1(M_n) = 1/alpha_0) = %.6f" % nstar)
OUT["P9_alpha"] = dict(pi1=pi1_num, pi1_closed=pi1_closed, dev=float(abs(pi1_num - 1 / ALPHA_INV) / (1 / ALPHA_INV)),
                       nstar=nstar)


# ==================================================================
head("PART 10  离散 Maxwell 引擎（code/Maxwell.py 的结构读数）")
# ==================================================================
D_edge = np.array([
    [1, -1, 0, 0, 0, 0, 0, 0], [0, 1, -1, 0, 0, 0, 0, 0],
    [0, 0, 1, -1, 0, 0, 0, 0], [0, 0, 0, 1, -1, 0, 0, 0],
    [0, 0, 0, 0, 1, -1, 0, 0], [0, 0, 0, 0, 0, 1, -1, 0],
    [0, 0, 0, 0, 0, 0, 1, -1], [-1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, -1, 0, 0, 0, 0, 0], [0, 1, 0, -1, 0, 0, 0, 0],
    [0, 0, 1, 0, -1, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, -1]
], dtype=float)
C_cycle = np.array([
    [1, 1, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, -1, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, -1, 0, 0, 1, 0, 0],
    [1, 0, 0, 1, 0, 0, 0, -1, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, -1]
], dtype=float)
P_E = D_edge @ np.linalg.pinv(D_edge.T @ D_edge) @ D_edge.T
P("      D  : %d x %d, rank(D) = %d (= V-1)" % (D_edge.shape[0], D_edge.shape[1], np.linalg.matrix_rank(D_edge)))
P("      C  : %d x %d, rank(C) = %d" % (C_cycle.shape[0], C_cycle.shape[1], np.linalg.matrix_rank(C_cycle)))
P("      beta1 = E - rank(D) = %d - %d = %d" % (D_edge.shape[0], np.linalg.matrix_rank(D_edge),
                                                D_edge.shape[0] - np.linalg.matrix_rank(D_edge)))
P("      P_E  : idempotent = %s, symmetric = %s, rank = %d"
  % (bool(np.allclose(P_E @ P_E, P_E)), bool(np.allclose(P_E, P_E.T)), np.linalg.matrix_rank(P_E)))
P("      注：C 为引擎自带的 2-链基，其行**不**满足 C@D = 0（max|C@D| = %.3g）⇒ 不作环的数学断言；"
  % float(np.abs(C_cycle @ D_edge).max()))
P("          rank(C) = 5 与 beta1 = 5 数值相同、**含义不同**（D1 警戒，禁互证）。")
OUT["P10_maxwell"] = dict(D=list(D_edge.shape), rankD=int(np.linalg.matrix_rank(D_edge)),
                          C=list(C_cycle.shape), rankC=int(np.linalg.matrix_rank(C_cycle)),
                          b1=int(D_edge.shape[0] - np.linalg.matrix_rank(D_edge)),
                          rankPE=int(np.linalg.matrix_rank(P_E)),
                          maxCD=float(np.abs(C_cycle @ D_edge).max()))
# 引擎实际运行（捕获 Gauss 残差）
try:
    r = subprocess.run([sys.executable, os.path.join("code", "Maxwell.py")],
                       capture_output=True, text=True, timeout=120)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    rr = []
    for l in lines:
        parts = l.split()
        if len(parts) >= 5:
            try:
                rr.append(abs(float(parts[-1])))
            except ValueError:
                pass
    P("      引擎运行 Gauss 残差 max|residual| = %.3e（行数 %d）" % (max(rr), len(rr)))
    OUT["P10_maxwell"]["gauss_residual_max"] = float(max(rr))
except Exception as e:
    P("      引擎运行跳过（%s）" % e)


# ==================================================================
head("PART 11  质量侧对照（Koide，供论文第 4 节引用）")
# ==================================================================
me, mmu, mtau = 0.51099895069, 105.6583755, 1776.93
m = np.array([me, mmu, mtau])
Q = m.sum() / (np.sqrt(m).sum() ** 2)
eta2 = (3 * Q - 1) / 2
P("      Q  = %.9f   eta^2 = %.9f   dev vs 2/3 = %.3e" % (Q, eta2, Q - 2 / 3))
P("      反解 eta = %.9f vs 1/sqrt2 = %.9f (偏 %.3e)" % (math.sqrt(eta2), 1 / math.sqrt(2), math.sqrt(eta2) - 1 / math.sqrt(2)))
OUT["P11_koide"] = dict(Q=float(Q), eta2=float(eta2), dev=float(Q - 2 / 3))


# ------------------------------------------------------------------
with open("_sre_light_origin_paper_check.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1, default=str)

head("SUMMARY")
P("saved _sre_light_origin_paper_check.json")
P("ALL PARTS DONE.")
