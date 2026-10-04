# -*- coding: utf-8 -*-
"""
_sre_mass_origin_paper_check.py
《SRE 体系下的质量起源》—— 论文全部关键读数的**一键复算**脚本。

本脚本不引入新结论，只把论文引用的每一处数值重新算一遍，使其可被独立复核。
覆盖三份前序脚本的要点：
  _sre_triality_families.py   （第 30 轮：Z3 / 三力性 / 挠子）
  _sre_quark_mass_probe.py    （第 31 轮：夸克 / RG 不变靶）
  _sre_cyclic_mass_formalism.py （第 32 轮：循环算子）

运行（需 numpy + networkx）：
  C:/myapp/miniconda3/envs/ai/python.exe -u _sre_mass_origin_paper_check.py > _sre_mass_origin_paper_check.log 2>&1
"""
import json
import math
import cmath
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

OUT = {}
W = cmath.exp(2j * math.pi / 3.0)


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * 92)
    P(t)
    P("=" * 92)


# ==================================================================================
# 骨架与群工具
# ==================================================================================
def Y3(pre="", state="p", open_ring=0):
    """核子骨架：三股 Y + 三角闭合；state='n' 时打开 (L0r,L1r) 一条环边。"""
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


def beta1(G):
    return G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)


def all_autos(G):
    """全枚举自同构（12 顶点，成本可接受），返回 {node->node} 字典列表。"""
    gm = GraphMatcher(G, G)
    return [dict(m.items()) for m in gm.isomorphisms_iter()]


def perm_order(m, nodes):
    o = 1
    for v in nodes:
        x, c = v, 0
        while True:
            x = m[x]
            c += 1
            if x == v:
                break
        o = o * c // math.gcd(o, c)
    return o


def ring_orbits(G, autos):
    """三环 {L0j,L1j,L2j} 在 Aut 下的轨道（返回轨道列表 + 环集置换集合）。"""
    rings = [frozenset(("L0%d" % j, "L1%d" % j, "L2%d" % j)) for j in range(3)]
    ring_index = {r: j for j, r in enumerate(rings)}
    perms = []
    for m in autos:
        img = {}
        for j, r in enumerate(rings):
            r2 = frozenset(m[x] for x in r)
            img[j] = ring_index.get(r2, None)
        if all(v is not None for v in img.values()):
            perms.append(tuple(img[j] for j in range(3)))
    seen, orbits = set(), []
    for j in range(3):
        if j in seen:
            continue
        orb = {k for p in perms for k in [p[j]]}
        # 闭包
        changed = True
        while changed:
            changed = False
            for p in perms:
                for k in list(orb):
                    if p[k] not in orb:
                        orb.add(p[k]); changed = True
        seen |= orb
        orbits.append(sorted(orb))
    return orbits, sorted(set(perms))


# ==================================================================================
# 线性代数工具
# ==================================================================================
def shift_matrix(n=3):
    S = np.zeros((n, n))
    for k in range(n):
        S[(k + 1) % n, k] = 1.0
    return S


def is_circulant(A, tol=1e-9):
    n = A.shape[0]
    c = A[0, :]
    for i in range(n):
        for j in range(n):
            if abs(A[i, j] - c[(j - i) % n]) > tol:
                return False
    return True


def amps(eta, delta, c0=1.0):
    return [c0 + 2.0 * eta * math.cos(delta + 2.0 * math.pi * k / 3.0) for k in range(3)]


def Qof(a):
    return sum(x * x for x in a) / (sum(a) ** 2)


def invs(a):
    m = [x * x for x in a]
    e1 = sum(m)
    return Qof(a), (max(m) - min(m)) / e1


# ==================================================================================
head("PART 1  定理：与循环移位交换 ⇔ 循环矩阵（论文 §5）")
n = 3
I = np.eye(n)
S = shift_matrix(n)
L = np.kron(S.T, I) - np.kron(I, S)
sv = np.linalg.svd(L, compute_uv=False)
rank = int(np.sum(sv > 1e-9))
dim_c = n * n - rank
U, s_, Vt = np.linalg.svd(L)
null_basis = Vt[rank:, :]
allcirc = all(is_circulant(null_basis[i].reshape(n, n)) for i in range(null_basis.shape[0]))
P("1.1  vec(AS-SA)=0 系数矩阵秩 = %d / %d  ⇒ 中心化子维数 = %d（应 = n = %d）：%s"
  % (rank, n * n, dim_c, n, "是" if dim_c == n else "否"))
P("1.2  零空间基 reshape 后**全为循环矩阵**：%s" % allcirc)
P("      ⇒ Z3-等变性把 9 个矩阵元素压到 3 个。")
OUT["P1"] = {"rank": rank, "dim_centralizer": dim_c, "null_basis_all_circulant": bool(allcirc)}

# ==================================================================================
head("PART 2  Hermitian 循环矩阵的谱：2+1 vs 1+1+1（论文 §6）")
rng = np.random.default_rng(7)
tabB, max_err = [], 0.0
for _ in range(6):
    c0 = rng.uniform(0.5, 2.0)
    m1 = rng.uniform(0.0, 0.45 * c0)
    th = rng.uniform(0.0, 2.0 * math.pi)
    c1 = m1 * cmath.exp(1j * th)
    M = c0 * I + c1 * S + np.conj(c1) * (S @ S)
    herm = bool(np.allclose(M, M.conj().T))
    ev = np.sort(np.linalg.eigvalsh(M))
    frm = np.sort([c0 + 2.0 * m1 * math.cos(th + 2.0 * math.pi * j / 3.0) for j in range(3)])
    e = float(np.max(np.abs(ev - frm)))
    max_err = max(max_err, e)
    tabB.append({"c0": c0, "abs_c1": m1, "theta": th, "hermitian": herm, "max_err": e})
P("2.1  随机 6 组对照「谱 vs 解析 c0+2|c1|cos(θ+2πj/3)」：Hermitian 全 True，最大误差 = %.2e" % max_err)
for tag, m1, th in (("实对称 θ=0", 0.30, 0.0), ("复相位 θ=1", 0.30, 1.0)):
    c1 = m1 * cmath.exp(1j * th)
    M = 1.0 * I + c1 * S + np.conj(c1) * (S @ S)
    ev = np.sort(np.real(np.linalg.eigvalsh(M)))
    uniq = len(set(np.round(ev, 9).tolist()))
    part = {1: "3", 2: "2+1", 3: "1+1+1"}[uniq]
    P("2.2  %-10s λ = %-32s 取值数=%d ⇒ 划分 %s"
      % (tag, np.array2string(ev, precision=6), uniq, part))
P("      ⇒ 实对称循环恒为 2+1；要三代互异必须带复相位（Hermitian）。")
OUT["P2"] = {"max_err": max_err, "checks": tabB}

# ==================================================================================
head("PART 3  形状是**免费**的：任意三数皆可写成该余弦（论文 §6.3）")
rng2 = np.random.default_rng(11)
maxerr_arb = 0.0
for _ in range(8):
    a = list(rng2.uniform(-2.0, 5.0, 3))
    c0x = sum(a) / 3.0
    zx = sum(a[k] * (W ** k) for k in range(3))
    c1a = abs(zx) / 3.0
    thx = (-cmath.phase(zx)) % (2.0 * math.pi)
    rec = [c0x + 2.0 * c1a * math.cos(thx + 2.0 * math.pi * k / 3.0) for k in range(3)]
    maxerr_arb = max(maxerr_arb, float(max(abs(rec[k] - a[k]) for k in range(3))))
P("3.1  随机 8 组**任意三数** → 反解 → 重构，最大误差 = %.2e" % maxerr_arb)
P("      ⇒ 「三点共一条余弦」不是约束，是免费重参数化；Koide 的内容是 η 的**值**。")
OUT["P3"] = {"arbitrary_triple_reconstruction_max_err": maxerr_arb}

# ==================================================================================
head("PART 4  不变量模空间 (η, δ mod 2π/3)：Q 对 δ 免疫（论文 §8）")
tabC1 = []
for eta in (0.30, 0.50, 1.0 / math.sqrt(2), 0.80):
    qs = [Qof(amps(eta, d)) for d in np.linspace(0.0, 2.0 * math.pi, 361)]
    tabC1.append({"eta": eta, "Q_range": max(qs) - min(qs), "Q": qs[0],
                  "analytic": 1.0 / 3.0 + 2.0 * eta * eta / 3.0})
    P("4.1  η=%.6f  Q 极差=%.2e  Q=%.9f  解析=%.9f"
      % (eta, max(qs) - min(qs), qs[0], 1.0 / 3.0 + 2.0 * eta * eta / 3.0))
tabC2 = []
for delta in (0.0, 0.4, 0.8, 1.2):
    Q, R = invs(amps(1.0 / math.sqrt(2), delta))
    tabC2.append({"delta": delta, "Q": Q, "R": R})
    P("4.2  η=1/√2 δ=%.3f  Q=%.9f  R=%.9f  ⇒ R 依赖 δ（第二个不变量）" % (delta, Q, R))
a0 = amps(1.0 / math.sqrt(2), 2.0 / 9.0)
Q0, R0 = invs(a0)
tabD = [{"shift": 0, "Q": Q0, "R": R0}]
for r in (1, 2):
    ar = a0[r:] + a0[:r]
    Q1, R1 = invs(ar)
    tabD.append({"shift": r, "Q": Q1, "R": R1, "dQ": abs(Q1 - Q0), "dR": abs(R1 - R0)})
P("4.3  三个代表元（循环移位）不变量比较：")
for row in tabD:
    P("      shift=%d  Q=%.12f  R=%.12f%s"
      % (row["shift"], row["Q"], row["R"], "" if row["shift"] == 0 else "  (|dQ|=%.1e)" % row["dQ"]))
P("      ⇒ 3 个代表元不变量完全相同 ⇒ 「打开（选原点）」是 Z3 规范，不改变可观测量。")
OUT["P4"] = {"Q_delta_independent": tabC1, "R_delta_dependent": tabC2,
             "representatives": tabD, "moduli_dim": 2}

# ==================================================================================
head("PART 5  Koide 与真实带电轻子（论文 §9）")
tabE = []
for nm, m in (("m_tau=1776.86（归档）", [0.51099895069, 105.6583755, 1776.86]),
              ("m_tau=1776.93（2026 PDG）", [0.51099895069, 105.6583755, 1776.93])):
    aa = [math.sqrt(x) for x in m]
    Q = Qof(aa)
    eta2 = (3.0 * Q - 1.0) / 2.0
    ang = math.degrees(math.acos(min(1.0, 1.0 / math.sqrt(3.0 * Q))))
    tabE.append({"case": nm, "Q": Q, "eta2": eta2, "dev_vs_2over3": Q - 2.0 / 3.0, "angle_deg": ang})
    P("5.1  %-26s Q=%.9f  η²=%.9f  偏差(2/3)=%+.3e  夹角=%.4f°" % (nm, Q, eta2, Q - 2.0 / 3.0, ang))
aa = [math.sqrt(x) for x in (0.51099895069, 105.6583755, 1776.93)]
zx = sum(aa[k] * (W ** k) for k in range(3))
c0x = sum(aa) / 3.0
eta_meas = (abs(zx) / 3.0) / c0x
P("5.2  反解 η = |c1|/c0 = %.9f   1/√2 = %.9f   偏差 = %+.3e"
  % (eta_meas, 1.0 / math.sqrt(2.0), eta_meas - 1.0 / math.sqrt(2.0)))
P("      ⇒ Q = 1/3 + (2/3)η²，**与相位 δ 无关**；Q=2/3 ⟺ η²=1/2 ⟺ 45°。")
OUT["P5"] = {"cases": tabE, "eta_measured": eta_meas, "eta_target": 1.0 / math.sqrt(2.0)}

# ==================================================================================
head("PART 6  Z3 在骨架上有原生归宿：挠子（论文 §4）")
for st, name in (("p", "闭态(质子)"), ("n", "开态(中子)")):
    G = Y3(state=st)
    autos = all_autos(G)
    nodes = list(G.nodes())
    o3 = sum(1 for m in autos if perm_order(m, nodes) == 3)
    o2 = sum(1 for m in autos if perm_order(m, nodes) == 2)
    orbits, perms = ring_orbits(G, autos)
    P("6.1  %-10s V=%d E=%d β1=%d |Aut|=%d  阶3元=%d  阶2元=%d  三环轨道数=%d %s"
      % (name, G.number_of_nodes(), G.number_of_edges(), beta1(G), len(autos), o3, o2, len(orbits), orbits))
    P("      环集上的诱导置换 = %s" % perms)
    OUT["P6_" + st] = {"V": G.number_of_nodes(), "E": G.number_of_edges(), "beta1": beta1(G),
                       "n_aut": len(autos), "n_order3": o3, "n_order2": o2,
                       "ring_orbits": orbits, "perms": [list(p) for p in perms]}
Gc = Y3(state="p")
phi = {v: (v if v.startswith("c") else "L%s%d" % (v[1], (int(v[2]) + 1) % 3)) for v in Gc.nodes()}
ok_edge = all(Gc.has_edge(phi[u], phi[v]) for u, v in Gc.edges())
ok3 = all(phi[phi[phi[x]]] == x for x in Gc.nodes())
P("6.2  见证 φ: L_ij ↦ L_i,(j+1)  —— 保边=%s，阶3=%s" % (ok_edge, ok3))
P("      ⇒ 三环被一个阶 3 自同构自由、传递作用 ⇒ 三环 = Z3-挠子（无原点）。")
OUT["P6_phi"] = {"edge_preserving": bool(ok_edge), "order3": bool(ok3)}

# ==================================================================================
head("PART 7  Z3 特征分解：顶点 1/2|1/2，边 1/3|2/3（论文 §4.3）")
for nm, dim, fix in (("顶点", 12, 3), ("边", 18, 0)):
    triv = (dim + 2 * fix) // 3
    nontr = (dim - fix) // 3
    P("7.1  %-4s dim=%2d  χ(φ)=%d  ⇒  %d·1 + %d·ω + %d·ω²   平凡 %d/%d = %.4f  非平凡 %.4f"
      % (nm, dim, fix, triv, nontr, nontr, triv, dim, triv / dim, (dim - triv) / dim))
    OUT["P7_" + nm] = {"dim": dim, "chi": fix, "trivial": triv, "nontrivial": nontr,
                       "trivial_weight": triv / dim}
P("      ⚠ D1 警戒：1/2、1/3、2/3 全是小分母有理数 ⇒ 不作独立证据（见论文 §12.2）。")

# ==================================================================================
head("PART 8  夸克侧：Q 对同乘因子严格不变（论文 §10）")
mlight = [2.16e-3, 4.67e-3, 93.4e-3]          # u,d,s @2 GeV（量级演示）
q0 = Qof([math.sqrt(x) for x in mlight])
res = []
for c in (1e-3, 1e-1, 1.0, 1e3, 1e6):
    res.append(abs(Qof([math.sqrt(c * x) for x in mlight]) - q0))
P("8.1  Q(c·m) 残差（c=1e-3..1e6，u/d/s）：最大 = %.2e  ⇒ Q 是尺度不变量" % max(res))
P("      推论：γ_m 味无关 ⇒ u,d,s 同乘一因子跑动 ⇒ Q_light 是 RG 不变量（标准结论）。")
P("      对照：绝对值 / 同标度比 / 含 m_p·Λ_QCD 的组合 ⇒ 一律出局（闸门 C2）。")
OUT["P8"] = {"Q_scale_invariance_max_residual": max(res), "Q_light_demo": q0}

# ==================================================================================
with open("_sre_mass_origin_paper_check.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P()
P("已写出 _sre_mass_origin_paper_check.json")
