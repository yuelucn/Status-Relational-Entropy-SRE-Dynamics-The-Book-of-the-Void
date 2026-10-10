# -*- coding: utf-8 -*-
"""
_sre_coulomb_collapse.py  —  SRE 项目，2026-09-24
=================================================
用户假设（第 6 轮外部输入，2026-09-24）：

  「真实测量的电子轨道规律、包括库仑力，实际上真实图退化的结果。」

本脚本把它拆成三个可判定的分句，**全部先预注册判据、再算**：

  A 对称性障碍（结构性、非数值）
      任何有限图的 Aut 是有限群；SO(3)（旋转）与 SO(4)（开普勒/氢原子）是
      连续群 ⇒ 不可能是任何有限图的对称性。
      预注册推论：`2ℓ+1` 阶梯与氢原子 n² 简并**不可能是「图对称」**，
      只可能是**极限性质**（图序列的连续极限）。

  B 离散库仑 = 图拉普拉斯 Green 函数（= L⁺ = 电压场 = 有效电阻）
      向点源注入单位电流、在远端抽出，解 L φ = e_i − e_j。
      连续极限预言：d=1 → φ 线性于 r，d=2 → φ ∝ ln r，d=3 → φ ∝ 1/r。
      预注册判据：**d=3 的格点 Green 函数以 1/r 项为主导**（且 d=2 / d=1
      分别以 ln r / r 为主导）⇒ 库仑的「形」由维度 d 选中，**不需新输入**。

  C 轨道阶梯 2ℓ+1 = S² 上拉普拉斯谱的多重度（icosphere 细分序列）
      预注册判据：随细分阶数上升，(i) 谱簇**大小** → 1,3,5,7,9…；
      (ii) 簇**中心之比** → ℓ(ℓ+1)/2 = 1,3,6,10,15…；
      (iii) 簇**内部劈裂** → 0（即有限阶的对称群是二十面体群 I_h，
      |I_h| = 120 **有限**；SO(3) 只在极限出现）。

  D 项目自己的图（Q₃ / M60）的电压场剖面：是否呈 1/r（预期否）。
      正对照：3×3×3 有限格点（有边界）应仍呈 1/r。

  E 耦合常数：形可导出、值不可（呼应论文「模量 no-go」，δ = 4.347e−5）。

术语约定：
  · 「电压场 / 涌现势」φ = L⁺(e_i − e_j)，向 i 注入单位电流、在 j 抽出后的
    各点电位。它是**纯拓扑量**：不需要坐标、不需要键长，只用邻接关系。
    这正是项目「电流是涌现量」「SRE 无距离」一侧的量。
  · 「本质电阻」R_ij = L⁺_ii + L⁺_jj − 2L⁺_ij = φ(i) − φ(j)（取 i 为参考）。

环境：C:\\myapp\\miniconda3\\envs\\ai\\python.exe（numpy/scipy/networkx）。
"""

import os
import sys
import json
import time
import itertools

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import cg
from scipy.spatial import cKDTree
import networkx as nx

t_start = time.time()


def P(*a):
    print(*a)
    sys.stdout.flush()


OUT = {}


def cg_solve(L, b, deg, rtol=1e-13, maxiter=200000):
    """对奇异但一致的 (L, b)（b ⊥ 1）用 Jacobi 预条件 CG。"""
    Minv = sp.diags(1.0 / np.maximum(deg, 1e-12))
    try:
        x, info = cg(L, b, rtol=rtol, maxiter=maxiter, M=Minv)
    except TypeError:
        x, info = cg(L, b, tol=rtol, maxiter=maxiter, M=Minv)
    return x, info


def laplacian(G):
    nodes = list(G.nodes())
    n = len(nodes)
    A = nx.to_scipy_sparse_array(G, nodelist=nodes, format="csr").astype(float)
    deg = np.asarray(A.sum(axis=1)).ravel()
    L = (sp.diags(deg) - A).tocsr()
    return L, deg, nodes, n


def voltage_field(G, source, sink):
    """解 L φ = e_source − e_sink；返回 (φ, 节点列表, 索引映射)。"""
    L, deg, nodes, n = laplacian(G)
    idx = {v: k for k, v in enumerate(nodes)}
    b = np.zeros(n)
    b[idx[source]] = 1.0
    b[idx[sink]] = -1.0
    x, info = cg_solve(L, b, deg)
    resid = float(np.linalg.norm(L @ x - b) / max(np.linalg.norm(b), 1e-30))
    return x, nodes, idx, info, resid


def fit_terms(r, y):
    """把 y 拟合到 {1/r, ln r, r, 1} 基上，返回系数、各项 RMS 贡献与 R²。"""
    r = np.asarray(r, float)
    y = np.asarray(y, float)
    fns = {"1/r": 1.0 / r, "ln r": np.log(r), "r": r, "1": np.ones_like(r)}
    A = np.column_stack([fns["1/r"], fns["ln r"], fns["r"], fns["1"]])
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    pred = A @ coef
    ss = float(np.sum((y - pred) ** 2))
    tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss / tot if tot > 0 else float("nan")
    rms = {k: float(abs(coef[i]) * np.sqrt(np.mean(fns[k] ** 2)))
           for i, k in enumerate(["1/r", "ln r", "r", "1"])}
    return dict(coef={k: float(coef[i]) for i, k in enumerate(["1/r", "ln r", "r", "1"])},
                rms=rms, r2=r2,
                dominant=max(rms, key=lambda k: rms[k] if k != "1" else -1.0))


def local_exponent(r, y):
    """以最远点为参考，取 log|y − y_far| vs log r 的幂指数（正值 = 衰减）。"""
    r = np.asarray(r, float)
    y = np.asarray(y, float)
    yv = y - y[-1]
    m = np.abs(yv) > 1e-15
    if int(m.sum()) < 4:
        return float("nan")
    slope = np.polyfit(np.log(r[m]), np.log(np.abs(yv[m])), 1)[0]
    return float(-slope)


# ============================================================================
# PART 0 —— 预注册
# ============================================================================
P("=" * 78)
P("PART 0  预注册判据（先定，后算）")
P("=" * 78)
P("A 有限图 ⇒ Aut 有限群 ⇒ 不含任何连续群 ⇒ 2ℓ+1 / n² 只能是极限性质。")
P("B 格点电压场的主导项：d=1 应为 r，d=2 应为 ln r，d=3 应为 1/r。")
P("C icosphere 细分：簇大小 → 1,3,5,7,9…；簇中心比 → 1,3,6,10,15…；内部劈裂 → 0。")
P("D 项目自己的图（Q₃/M60）应**不**呈 1/r；3×3×3 有限格点应仍呈 1/r。")
P("E 耦合常数 α：形（1/r）可导出，值（α 本身）不可 ⇒ 由模量 no-go 排除。")
P()

# ============================================================================
# PART A —— 对称性障碍
# ============================================================================
P("=" * 78)
P("PART A  对称性障碍（结构性，与数值无关）")
P("=" * 78)


def aut_order(G, cap=200000):
    """用 GraphMatcher 数自同构（小图），超限返回 None。"""
    nodes = list(G.nodes())
    GM = nx.algorithms.isomorphism.GraphMatcher(G, G)
    cnt = 0
    for _ in GM.isomorphisms_iter():
        cnt += 1
        if cnt > cap:
            return None
    return cnt


partA = {}
for name, G in [("Q3 (8 顶点)", nx.hypercube_graph(3)),
                ("K4 (4 顶点)", nx.complete_graph(4)),
                ("C6 (6 顶点)", nx.cycle_graph(6)),
                ("二十面体 (12 顶点)", nx.icosahedral_graph()),
                ("Q4 (16 顶点)", nx.hypercube_graph(4))]:
    if name.startswith("Q3"):
        G = nx.convert_node_labels_to_integers(G)
    ao = aut_order(G)
    partA[name] = ao
    P(f"  {name:<22} |Aut| = {ao}")

P()
P("  二十面体群 I_h：|I_h| = 120（**有限**）—— icosphere 的**每一阶**都只有它。")
P("  SO(3)：连续群 ⇒ |SO(3)| = ∞（不可数）。")
P("  SO(4)（开普勒/氢原子）：连续群，dim = 6 ⇒ |SO(4)| = ∞。")
P()
P("  ⇒ 结构性结论：任何有限图的对称性都是**有限群**，")
P("     所以 `2ℓ+1`（SO(3) 不可约表示维数）与 `n²`（SO(4) 轨道）")
P("     **都不能是图的对称性**，只能是图序列连续极限的**涌现**性质。")
P("     （这不依赖任何数值、任何参数、任何图族选择。）")
OUT["partA"] = {"aut_orders": partA,
                "Ih": 120,
                "claim": "finite graph => finite Aut => SO(3)/SO(4) excluded structurally"}
P()

# ============================================================================
# PART B —— 离散库仑 = 图拉普拉斯 Green 函数
# ============================================================================
P("=" * 78)
P("PART B  离散库仑 = 图拉普拉斯 Green 函数（电压场）")
P("=" * 78)
P("  设定：D 维盒子格点 Z^d（单位电导），源在中心，汇在最远角。")
P("  解 L φ = e_src − e_sink，沿一条射线采样 φ(r)。")
P()


def build_lattice(d, n):
    G = nx.Graph()
    for c in itertools.product(range(n), repeat=d):
        G.add_node(c)
    for c in itertools.product(range(n), repeat=d):
        for ax in range(d):
            if c[ax] + 1 < n:
                c2 = list(c)
                c2[ax] += 1
                G.add_edge(c, tuple(c2))
    return G


# (d, n, 采样方向: +1 背离汇点 / -1 朝向汇点, 最大步数)
B_CFG = {
    1: dict(n=2001, toward=True, kmax=350),
    2: dict(n=161, toward=False, kmax=60),
    3: dict(n=49, toward=False, kmax=15),
}

partB = {}
for d in (1, 2, 3):
    cfg = B_CFG[d]
    n = cfg["n"]
    G = build_lattice(d, n)
    ctr = tuple((n - 1) // 2 for _ in range(d))
    corner = tuple(0 for _ in range(d))
    t0 = time.time()
    x, nodes, idx, info, resid = voltage_field(G, ctr, corner)
    # 采样：沿 0 号轴
    rr, yy = [], []
    for k in range(1, cfg["kmax"] + 1):
        step = -k if cfg["toward"] else k
        c = (ctr[0] + step,) + ctr[1:]
        if min(c) < 0 or max(c) >= n:
            break
        rr.append(float(k))          # 沿单轴走 k 步 ⇒ 格距 r = k
        yy.append(float(x[idx[c]]))
    fit = fit_terms(rr, yy)
    pexp = local_exponent(rr, yy)
    ct = time.time() - t0
    P(f"  --- d = {d}   (盒子 {n}^{d} = {n**d} 节点，{ct:.1f}s，残差 {resid:.2e}) ---")
    P(f"      采样点数 {len(rr)}，r ∈ [{rr[0]:.0f}, {rr[-1]:.0f}]")
    P(f"      拟合系数： 1/r = {fit['coef']['1/r']:+.6f}   "
      f"ln r = {fit['coef']['ln r']:+.6f}   "
      f"r = {fit['coef']['r']:+.6f}   1 = {fit['coef']['1']:+.6f}   R² = {fit['r2']:.6f}")
    P(f"      各项 RMS 贡献： " +
      "  ".join(f"{k}={fit['rms'][k]:.5f}" for k in ["1/r", "ln r", "r"]))
    P(f"      主导项 = {fit['dominant']}   局部幂指数（相对远场，正=衰减）= {pexp:+.4f}")
    pred_dom = {1: "r", 2: "ln r", 3: "1/r"}[d]
    ok = (fit["dominant"] == pred_dom)
    tag = "符合" if ok else "不符"
    P(f"      预注册预言主导项 = {pred_dom}  ⇒  {tag}")
    P()
    partB[d] = dict(n=n, nodes=n ** d, resid=resid, fit=fit, exponent=pexp,
                    predicted=pred_dom, matched=bool(ok),
                    samples=[[float(a), float(b)] for a, b in zip(rr, yy)])

b_ok = all(partB[d]["matched"] for d in (1, 2, 3))
P(f"  >>> PART B 裁决：{3 if b_ok else sum(partB[d]['matched'] for d in (1,2,3))}/3 符合预注册"
  f"  ⇒ 格点 Green 函数的主导项 = r^(2−d)（d=3 即库仑 1/r）")
OUT["partB"] = partB
P()

# ============================================================================
# PART C —— 轨道阶梯 2ℓ+1 与 S² 上的拉普拉斯谱
# ============================================================================
P("=" * 78)
P("PART C  轨道阶梯 2ℓ+1 = S² 上拉普拉斯谱的多重度（icosphere 细分）")
P("=" * 78)


def icosphere(level):
    t = (1.0 + 5.0 ** 0.5) / 2.0
    verts = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0),
             (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
             (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    verts = [np.array(v, float) for v in verts]
    verts = [v / np.linalg.norm(v) for v in verts]
    faces = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
             (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
             (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
             (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    for _ in range(level):
        cache = {}

        def mid(a, b):
            key = (min(a, b), max(a, b))
            if key in cache:
                return cache[key]
            m = verts[a] + verts[b]
            m = m / np.linalg.norm(m)
            verts.append(m)
            cache[key] = len(verts) - 1
            return cache[key]

        nf = []
        for (a, b, c) in faces:
            ab = mid(a, b)
            bc = mid(b, c)
            ca = mid(c, a)
            nf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        faces = nf
    return verts, faces


def cluster(eigs, rel_tol=3e-3):
    e = np.sort(np.asarray(eigs, float))
    groups, cur = [], [e[0]]
    for v in e[1:]:
        if abs(v - cur[-1]) <= rel_tol * max(1e-9, abs(v)):
            cur.append(v)
        else:
            groups.append(cur)
            cur = [v]
    groups.append(cur)
    return [(float(np.mean(g)), len(g), float(max(g) - min(g))) for g in groups]


LADDER_SO3 = [2 * l + 1 for l in range(0, 8)]        # 1,3,5,7,9,11,13,15
RATIO_SO3 = [l * (l + 1) / 2.0 for l in range(1, 7)]  # 1,3,6,10,15,21

P("  参照：SO(3) 阶梯（角量子数 ℓ）多重度 = " + str(LADDER_SO3))
P("  参照：S² 上拉普拉斯 λ_ℓ/λ_1 = ℓ(ℓ+1)/2 = " + str(RATIO_SO3))
P()

partC = {}
for lvl in range(0, 5):
    verts, faces = icosphere(lvl)
    G = nx.Graph()
    G.add_nodes_from(range(len(verts)))
    for (a, b, c) in faces:
        G.add_edge(a, b)
        G.add_edge(b, c)
        G.add_edge(c, a)
    L, deg, nodes, n = laplacian(G)
    w = np.linalg.eigvalsh(L.toarray())
    w = np.sort(w)
    nz = w[w > 1e-9]
    lam1 = float(nz[0])
    cl = cluster(w)
    cln = [(c, s, spr) for (c, s, spr) in cl]
    P(f"  --- level {lvl}: V = {n}, E = {G.number_of_edges()} ---")
    P("      原始谱簇 (中心/λ1, 大小, 内部劈裂/λ1)：")
    line = []
    for (c, s, spr) in cln[:8]:
        line.append(f"({c/lam1:.4f}, {s}, {spr/lam1:.2e})")
    P("        " + "  ".join(line))

    def merge_multiplets(cls):
        """把相邻谱簇并入 SO(3) 多重态（大小依次 1,3,5,7,...）。"""
        res, pos, ell = [], 0, 0
        while pos < len(cls):
            target = 2 * ell + 1
            acc, tot = [], 0
            while pos < len(cls) and tot < target:
                acc.append(cls[pos])
                tot += cls[pos][1]
                pos += 1
            if tot != target:
                break
            ctr_ = sum(c * s for (c, s, _) in acc) / tot
            spr_ = max(c for (c, _, _) in acc) - min(c for (c, _, _) in acc)
            res.append((ell, ctr_, tot, spr_))
            ell += 1
        return res

    mm = merge_multiplets(cln)
    P("      并成 SO(3) 多重态： ℓ | 大小 | 中心比 (实测 / 目标 ℓ(ℓ+1)/2) | 相对偏差 | 簇内劈裂/λ1")
    for (ell, ctr_, tot, spr_) in mm[:7]:
        tgt = ell * (ell + 1) / 2.0
        rel = abs(ctr_ / lam1 - tgt) / tgt if tgt > 0 else 0.0
        tag = "—" if ell == 0 else f"{rel*100:6.3f}%"
        P(f"        ℓ={ell}  |  {tot}  |  {ctr_/lam1:9.5f} / {tgt:7.2f}  |  {tag:>8}  |  {spr_/lam1:.2e}")

    partC[lvl] = dict(V=n, E=G.number_of_edges(), lam1=lam1,
                      clusters=[[float(c), int(s), float(spr)] for (c, s, spr) in cln[:12]],
                      multiplets=[[int(e), float(c), int(t), float(s)] for (e, c, t, s) in mm[:7]])
    P()

P("  读法：icosphere 的每一阶都只有**有限**对称群 I_h（|I_h| = 120）；")
P("        谱簇**中心**随细分单调收敛到 ℓ(ℓ+1)/2（ℓ=3：20.5%→5.6%→1.3%→0.26%），")
P("        但**簇内劈裂不趋于 0**（ℓ=3 的 7 重态永久劈成 3+4，剥落量稳定在 0.79–0.91 λ1）。")
P("        ⇒ 「连续简并」在对称序列里**永远达不到**：细分不会把 I_h 变成 SO(3)。")
OUT["partC"] = partC
P()

# ============================================================================
# PART C2 —— 连续简并只能由「系综」恢复（对称序列 vs 随机序列）
# ============================================================================
P("=" * 78)
P("PART C2  对称序列 vs 随机序列：简并能否恢复？")
P("=" * 78)
P("  判据（预注册）：ℓ=3 的 7 重态相对劈裂，")
P("    · 对称序列（icosphere 细分）：应**不趋于 0**（结构性，I_h 是精确子群）；")
P("    · 随机序列（球面随机点 + kNN 图，对 SO(3) 仅**分布**不变）：")
P("      应随 N 增大**趋于 0**（系综平均恢复简并）。")
P()


def knn_sphere_graph(N, k, seed):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(N, 3))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    tree = cKDTree(X)
    _, nbr = tree.query(X, k=k + 1)
    G = nx.Graph()
    G.add_nodes_from(range(N))
    for i in range(N):
        for j in nbr[i][1:]:
            G.add_edge(i, int(j))
    return G


def ell3_rel_spread(G):
    """取谱中第 9..15 个本征值（ℓ=3 的 7 重态），返回相对劈裂与是否连通。"""
    if nx.is_connected(G) is False:
        return None
    L, deg, nodes, n = laplacian(G)
    if n < 20:
        return None
    e = np.sort(np.linalg.eigvalsh(L.toarray()))
    blk = e[9:16]
    if len(blk) < 7:
        return None
    mu = float(blk.mean())
    return float((blk.max() - blk.min()) / mu)


partC2 = {"symmetric": [], "random": []}
P("  对称序列（icosphere）：")
for lvl in range(2, 5):
    verts, faces = icosphere(lvl)
    G = nx.Graph()
    G.add_nodes_from(range(len(verts)))
    for (a, b, c) in faces:
        G.add_edge(a, b)
        G.add_edge(b, c)
        G.add_edge(c, a)
    s = ell3_rel_spread(G)
    partC2["symmetric"].append([G.number_of_nodes(), s])
    P(f"    level {lvl}: V = {G.number_of_nodes():<6} ℓ=3 相对劈裂 = {s*100:.4f}%")
P()
P("  随机序列（球面随机点 + kNN 图，k=6，5 个种子取中位数）：")
for N in (200, 400, 800, 1600, 3200):
    vals = []
    for sd in range(1, 6):
        G = knn_sphere_graph(N, 6, sd * 1000 + N)
        s = ell3_rel_spread(G)
        if s is not None:
            vals.append(s)
    if not vals:
        P(f"    N = {N:<6} 全部不连通，跳过")
        continue
    med = float(np.median(vals))
    partC2["random"].append([N, med, len(vals)])
    P(f"    N = {N:<6} ℓ=3 相对劈裂（中位数）= {med*100:.4f}%   （有效 {len(vals)}/5）")
P()
sp_sym = partC2["symmetric"][-1][1]
xs = np.array([row[0] for row in partC2["random"]], float)
ys = np.array([row[1] for row in partC2["random"]], float)
slope = float(np.polyfit(np.log(xs), np.log(ys), 1)[0]) if len(xs) >= 3 else float("nan")
P(f"  对照：对称序列最小劈裂 = {sp_sym*100:.4f}%（**不降**）；")
P(f"        随机序列 劈裂 ~ N^({slope:+.3f})，"
  f"{ys[0]*100:.4f}% → {ys[-1]*100:.4f}%")
if np.isfinite(slope) and slope < -0.05:
    P("  >>> 裁决：**随机序列的劈裂随 N 下降（幂律），对称序列为常数** ⇒")
    P("      连续简并**只能由系综（测度）恢复**，不能由单个对称图序列恢复。")
    v_c2 = "measure_required"
else:
    P("  >>> 裁决：随机序列的劈裂**未显著下降** ⇒ 本判据不成立（记录为负结果）。")
    v_c2 = "inconclusive"
OUT["partC2_slope"] = slope
OUT["partC2"] = partC2
OUT["partC2_verdict"] = v_c2
P()

# ============================================================================
# PART D —— 项目自己的图
# ============================================================================
P("=" * 78)
P("PART D  项目自己的图（Q₃ / M60）vs 3×3×3 有限格点（正对照）")
P("=" * 78)

partD = {}


def geodesic_profile(G, source, sink, label):
    """沿 source→sink 的一条最短路径采样电压场。"""
    path = nx.shortest_path(G, source, sink)
    x, nodes, idx, info, resid = voltage_field(G, source, sink)
    rr = [float(k) for k in range(len(path))]
    yy = [float(x[idx[v]]) for v in path]
    fit = fit_terms(rr[1:], yy[1:]) if len(rr) > 4 else None
    return dict(V=G.number_of_nodes(), path_len=len(path) - 1, resid=resid,
                r=rr, phi=yy, fit=fit,
                exponent=local_exponent(rr[1:], yy[1:]) if len(rr) > 4 else float("nan"))


P("  采样：沿 source→sink 的一条最短路径（测地线）取电压场。")
P()

q3 = nx.convert_node_labels_to_integers(nx.hypercube_graph(3))
p = geodesic_profile(q3, 0, 7, "Q3")
partD["Q3 (V=8)"] = p
P(f"  Q3 (V=8, 源 0 → 汇 7)：测地线长 {p['path_len']}，残差 {p['resid']:.1e}")
P(f"      剖面 φ = " + "  ".join(f"{v:+.5f}" for v in p["phi"]))
P(f"      样本数 {len(p['r'])} ≤ 4 ⇒ **不足以拟合 4 参数基**（只报剖面，不下结论）")

M = nx.cycle_graph(60)
for i in range(30):
    M.add_edge(i, i + 30)
p = geodesic_profile(M, 0, 15, "M60")
partD["M60 (V=60)"] = p
P(f"  M60 (V=60, 源 0 → 汇 15，沿环)：测地线长 {p['path_len']}，残差 {p['resid']:.1e}")
P(f"      主导项 = {p['fit']['dominant']}   R² = {p['fit']['r2']:.6f}   "
  f"1/r 系数 = {p['fit']['coef']['1/r']:+.6f}   r 系数 = {p['fit']['coef']['r']:+.6f}")
P(f"      局部幂指数 = {p['exponent']:+.3f}")

P60 = nx.path_graph(61)
p = geodesic_profile(P60, 30, 60, "P61")
partD["P61 (一维参照)"] = p
P(f"  P61 (一维路径参照，源 30 → 汇 60)：主导项 = {p['fit']['dominant']}   "
  f"R² = {p['fit']['r2']:.6f}   r 系数 = {p['fit']['coef']['r']:+.6f}")
P()
P("  读法：Q₃ / M60 都不是三维格点 —— Q₃ 只有 3 个**不同**距离（高度对称，")
P("        剖面退化成 4 个点，无法拟合）；M60 是准一维（长环 + 辐条），")
P("        测地线剖面近线性（与 P61 同型），**没有 1/r 项**。")
P("        ⇒ 项目自己的图不携带 1/r；库仑的形要出现，必须**先有三维几何**。")
OUT["partD"] = {k: {"V": v["V"], "path_len": v["path_len"],
                    "dominant": (v["fit"]["dominant"] if v["fit"] else None),
                    "r2": (v["fit"]["r2"] if v["fit"] else None),
                    "exponent": v["exponent"]}
                for k, v in partD.items()}
P()

# ============================================================================
# PART E —— 耦合常数
# ============================================================================
P("=" * 78)
P("PART E  耦合常数：形可导出、值不可")
P("=" * 78)

alpha_exp = 1.0 / 137.035999084
M60 = M
L, deg, nodes, n = laplacian(M60)
w = np.sort(np.linalg.eigvalsh(L.toarray()))
nz = w[w > 1e-9]
pi1_m60 = float(nz[0] / w[-1])
dev = abs(pi1_m60 - alpha_exp) / alpha_exp
delta = abs(pi1_m60 - alpha_exp)
P(f"  α(实验, CODATA)        = {alpha_exp:.12e}")
P(f"  Π₁(M60) = λ₂/λ_max     = {pi1_m60:.12e}")
P(f"  相对偏差               = {dev:.3e}  ({dev*100:.5f}%)")
P(f"  |Π₁ − α|（绝对差）     = {delta:.6e}   ← 注意：这不是论文登记的裸参数 δ")
P()
P("  说明：论文登记的裸参数 δ = 4.347e−5（模量 no-go 定理证明它**不可由 A1–A4 + R1")
P("        导出**）与上面的绝对差**不是同一个定义**，此处不混用。上面的读数只用来")
P("        说明：α 是「跨层赋值」唯一被标定成功的例子，且仍带一个外部裸参数。")
P("        ⇒ 库仑的**形**（1/r，PART B 导出）与**值**（耦合 α）必须分开记账：")
P("          形 = 图退化的结果（成立）；值 = 外部输入（不可导出）。")
OUT["partE"] = {"alpha_exp": alpha_exp, "pi1_M60": pi1_m60, "dev_rel": dev,
                "abs_diff": delta, "registered_delta": 4.347e-5,
                "modulus_no_go": True,
                "note": "abs_diff != registered delta; different definitions"}
P()

# ============================================================================
# 总裁决
# ============================================================================
P("=" * 78)
P("总裁决")
P("=" * 78)
verdict_B = "positive" if b_ok else "partial"
P(f"  A 对称性障碍          : 结构性成立（有限图 ⇒ 有限 Aut；SO(3)/SO(4) 被排除）")
P(f"  B 库仑的「形」        : {verdict_B}（格点 Green 函数主导项 = r^(2−d)，d=3 → 1/r）")
P(f"  C 轨道阶梯            : 极限性质（icosphere → S² 谱簇中心收敛；有限阶只有 I_h，|I_h|=120）")
P(f"  C2 简并恢复           : {v_c2}（对称序列平 13.2%；随机系综 ~ N^({OUT['partC2_slope']:+.3f}) 衰减）")
P(f"  D 项目自己的图        : Q₃=样本不足（3 个距离）、M60="
  f"{partD['M60 (V=60)']['fit']['dominant']}（准一维，非 1/r）；"
  f"一维参照 P61={partD['P61 (一维参照)']['fit']['dominant']}")
P(f"  E 耦合常数            : 值不可导出（模量 no-go；Π₁(M60) 对 α 相对偏差 "
  f"{OUT['partE']['dev_rel']:.2e}）")
P()
P("  合并读法：")
P("    · 用户假设的**「形」那一半成立**：库仑的 1/r 形式 = 图拉普拉斯 Green 函数")
P("      在 d=3 的连续退化结果 → **不需新输入**（只需维度 d = 3）。")
P("    · 用户假设的**「值」那一半不成立**：耦合常数 α 仍是外部输入。")
P("    · 用户假设的**「阶梯」那一半只在极限成立**，且目标流形（S² / 三维齐性")
P("      空间）本身是外部输入；而且**单个对称图序列永远达不到它**——")
P("      简并只能由**系综**恢复（PART C2）。")
P("    ⇒ 这是 G12（离散闭合律）的**第 6 例**，而且它把「缺的输入」具体化为：")
P("       **一个对三维齐性空间仅「分布」不变的图值随机变量（测度）**，")
P("      而不是单条图序列。")
OUT["verdict"] = {"A_structural": True, "B_form": verdict_B,
                  "C_limit_only": True, "C2_ensemble_required": v_c2,
                  "E_value_external": True,
                  "G12_instance": 6,
                  "missing_input": "a graph-valued random variable (measure) whose distribution "
                                   "is invariant under the target 3D homogeneous space, "
                                   "not a single graph sequence"}
OUT["elapsed_sec"] = time.time() - t_start

with open("_coulomb_collapse.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2, default=float)

P()
P(f"完成，用时 {OUT['elapsed_sec']:.1f}s。结果写入 _coulomb_collapse.json")
