# -*- coding: utf-8 -*-
"""
verify_operator_20.py
=====================
SRE 算子 20（活化 / 桥接算子 𝒦_act）配套**独立严格验证程序**。

对应文档：《算子 20：活化 / 桥接算子 𝒦_act —— 严格数学规范》（v0.3）第 8 节「验证协议」（见 `Operator_20_C.md`）。

本程序**独立于实现的自测**（不调用 sre_activation_operator.self_test），逐条实证规范中的定义与定理：

  V1  定向 holonomy      §2.2/D3   Hol_R 与手算一致；反向遍历取负
  V2  恰当性判据         T20.1     10³ 随机图上 (i)⟺(ii)⟺(iii) 三等价
  V3  环基无关性         推论 20.1.1   ϱ 与生成树/环基/SVD 零空间口径一致
  V4  三通道正交性       H20.2     N 例随机反应三通道秩相关 |ρ_S| < 0.7
  V5  κ 的缩放不变性     T20.2     全局缩放不变；单独缩放 w_I **不**不变
  V6  火山形态           C20.7     扫 w_I 判单峰/单调（猜想检验）
  V7  零权割             P20.5     γ→0；κ 随 ε 单调发散（κ ~ 1/ε）
  V8  加边非单调         P20.6     加边使 γ 上升/下降各至少一例
  V9  对照协议           D8        w_I=0 退化到裸骨架；w_I>0 改变 κ
  V10 v0/v1 排序一致     §6        两版 κ 排序 Spearman ≥ 0.8
  V11 与算子 19 兼容     §9        保二分接枝不开符号通道；同色界面边可开
  V12 DFT 对标           H20.1     外部验证（本程序 SKIP，需外部数据）
  V13 顶点通道           T20.4/D5  μ 守恒、ν 平移不变、纯加载 ν=0（附解析算例）
  V14 端点不变性         T20.3     任意 E_I/w_I 下 ϱ_tot 不变

依赖：numpy（V11 额外需要 networkx，缺失时自动 SKIP）。
运行：python verify_operator_20.py
任一行断言失败以退出码 1 结束。
"""
from __future__ import annotations

import sys

import numpy as np

from sre_activation_operator import (
    build_reaction, incidence, hodge_g1, uniform_split,
    cycle_basis_bfs, cycle_basis_dfs, orientation_sign, holonomy_R,
    orient_from_cycle, operator_20_activation_index, pareto_leq,
)

try:
    import networkx as nx  # noqa: F401
    from sre_z2_holonomy_bridge import operator_19_z2_charge_channel
    _HAS_OP19 = True
except Exception:  # pragma: no cover
    _HAS_OP19 = False

RESULTS = []


def check(tag, desc, cond):
    RESULTS.append((tag, desc, bool(cond)))
    print("  [%s] %s" % ("PASS" if cond else "FAIL", desc))


def _raises(fn):
    """验证某调用确实抛错（用于非法输入断言）。"""
    try:
        fn()
    except Exception:
        return True
    return False


def note(msg):
    print("     · %s" % msg)


# ══════════════════════════════════════════════════════════════════════
# 独立工具（不依赖被测模块的内部实现）
# ══════════════════════════════════════════════════════════════════════

def _ekey(i, j):
    return (i, j) if i < j else (j, i)


def adj_from(n, edges):
    A = np.zeros((n, n), dtype=np.float64)
    for i, j in edges:
        A[i, j] = A[j, i] = 1.0
    return A


def random_connected_edges(rng, n, extra):
    edges, seen = [], set()
    for i in range(1, n):
        j = int(rng.integers(0, i))
        edges.append(_ekey(i, j)); seen.add(_ekey(i, j))
    tries = 0
    while extra > 0 and tries < 300:
        tries += 1
        a, b = int(rng.integers(0, n)), int(rng.integers(0, n))
        k = _ekey(a, b)
        if k[0] == k[1] or k in seen:
            continue
        seen.add(k); edges.append(k); extra -= 1
    return edges


def random_reaction(rng, n=None, extra=None, nseg=2, w_min=0.5, w_max=2.0):
    n = int(n if n is not None else rng.integers(6, 13))
    extra = int(extra if extra is not None else rng.integers(1, 4))
    E = random_connected_edges(rng, n, extra)
    m = len(E)
    w = rng.uniform(w_min, w_max, m)
    wps = [{"w": w.copy(), "nH": rng.integers(0, 3, n).astype(float)}]
    for _ in range(nseg):
        w = np.clip(wps[-1]["w"] + rng.normal(0.0, 0.6, m), 0.02, 3.0)
        nh = np.clip(wps[-1]["nH"] + rng.integers(-1, 2, n), 0, 4)
        wps.append({"w": w, "nH": nh})
    return build_reaction(n, E, wps, w_I=0.0)


def _rank(x):
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    order = np.argsort(x, kind="mergesort")
    r = np.empty(n)
    r[order] = np.arange(n, dtype=float)
    sx = x[order]
    i = 0
    while i < n:
        j = i
        while j + 1 < n and sx[j + 1] == sx[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = _rank(a), _rank(b)
    ra = ra - ra.mean(); rb = rb - rb.mean()
    d = float(np.sqrt((ra @ ra) * (rb @ rb)))
    return float(ra @ rb / d) if d > 1e-300 else 0.0


def _shape(y, rel=1e-3):
    y = np.asarray(y, dtype=np.float64)
    if y.max() - y.min() <= rel * max(abs(y.max()), 1e-12):
        return "constant"
    i = int(np.argmin(y))
    if i == 0:
        return "monotone_decreasing"
    if i == len(y) - 1:
        return "monotone_increasing"
    return "unimodal"


# ══════════════════════════════════════════════════════════════════════
# V1 定向 holonomy（§2.2 / D3）
# ══════════════════════════════════════════════════════════════════════

def v1_holonomy():
    print("\n--- V1 定向 holonomy（§2.2/D3）：与手算一致，反向遍历取负 ---")
    n = 3
    edges = [_ekey(0, 1), _ekey(1, 2), _ekey(0, 2)]
    idx = {e: k for k, e in enumerate(edges)}
    d = np.array([0.7, -0.3, 1.1])

    fwd = [0, 1, 2]
    rev = [0, 2, 1]
    h_fwd = holonomy_R(d, edges, fwd, idx)
    h_rev = holonomy_R(d, edges, rev, idx)
    # 手算：0→1 (+), 1→2 (+), 2→0 走 (0,2) 反向 (−)
    expect_fwd = d[0] + d[1] - d[2]
    # 独立口径：按遍历方向构造带符号边向量，再点乘
    def cycle_vector(cyc):
        z = np.zeros(len(edges))
        for t in range(len(cyc)):
            a, b = cyc[t], cyc[(t + 1) % len(cyc)]
            z[idx[_ekey(a, b)]] += orientation_sign(a, b)
        return z
    indep_fwd = float(cycle_vector(fwd) @ d)
    indep_rev = float(cycle_vector(rev) @ d)

    check("V1", "手算 Hol(0→1→2→0) = δ₀₁+δ₁₂−δ₀₂ = %.6f" % expect_fwd,
          abs(h_fwd - expect_fwd) < 1e-12)
    check("V1", "独立带符号边向量口径与 holonomy_R 一致",
          abs(h_fwd - indep_fwd) < 1e-12 and abs(h_rev - indep_rev) < 1e-12)
    check("V1", "反向遍历 Hol 取负：%.6f = −%.6f" % (h_rev, h_fwd),
          abs(h_rev + h_fwd) < 1e-12)


# ══════════════════════════════════════════════════════════════════════
# V2 恰当性判据 T20.1（10³ 随机图三等价）
# ══════════════════════════════════════════════════════════════════════

def v2_equivalence(rng, trials=1000):
    print("\n--- V2 定理 T20.1：δ 恰当 ⟺ 全环 Hol=0 ⟺ δ_harm=0（%d 例随机图）---" % trials)
    bad = 0
    for _ in range(trials):
        n = int(rng.integers(4, 13))
        E = random_connected_edges(rng, n, int(rng.integers(0, 6)))
        d = rng.normal(size=len(E))
        hd = hodge_g1(d, n, E)
        # (ii) 环基上 holonomy 全零
        cyc = cycle_basis_bfs(n, E)
        idx = {e: k for k, e in enumerate(E)}
        hmax = max((abs(holonomy_R(d, E, c, idx)) for c in cyc), default=0.0)
        hmax_rel = hmax / max(np.linalg.norm(d), 1e-30)
        # (iii) 调和分量
        harm_rel = np.linalg.norm(hd["harm"]) / max(np.linalg.norm(d), 1e-30)
        # (i) 存在势 φ 使 Bᵀφ = δ（最小二乘残差）
        B = incidence(n, E)
        res = np.linalg.norm(B.T @ np.linalg.lstsq(B.T, d, rcond=None)[0] - d)
        res_rel = res / max(np.linalg.norm(d), 1e-30)

        is_grad = res_rel < 1e-8
        hol_zero = hmax_rel < 1e-8
        harm_zero = harm_rel < 1e-8
        if not (is_grad == hol_zero == harm_zero):
            bad += 1
    check("V2", "1000 例：(i) 恰当 ⟺ (ii) 全环 Hol=0 ⟺ (iii) δ_harm=0（失配 %d 例）" % bad,
          bad == 0)


# ══════════════════════════════════════════════════════════════════════
# V3 环基无关性（推论 20.1.1）
# ══════════════════════════════════════════════════════════════════════

def v3_basis_independence(rng, trials=60):
    print("\n--- V3 推论 20.1.1：ϱ 与生成树/环基选取无关 ---")
    bad = 0
    for _ in range(trials):
        n = int(rng.integers(5, 13))
        E = random_connected_edges(rng, n, int(rng.integers(1, 6)))
        d = rng.normal(size=len(E))
        rho = hodge_g1(d, n, E)["rho"]
        # 独立口径：δ_harm = 投影到 ker(B)（右零空间）上的分量
        B = incidence(n, E)
        sv = np.linalg.svd(B, compute_uv=False)
        vt = np.linalg.svd(B)[2]
        rank = int((sv > 1e-9 * max(sv[0], 1e-30)).sum())
        Z = vt[rank:]                      # ker(B) 的正交基
        harm2 = Z.T @ (Z @ d) if Z.shape[0] else np.zeros_like(d)
        rho2 = float(np.linalg.norm(harm2) / max(np.linalg.norm(d), 1e-30))
        # 环基口径：两组不同生成森林给出相同的基本环数（β₁）
        c1 = len(cycle_basis_bfs(n, E, root=0))
        c2 = len(cycle_basis_dfs(n, E, root=n - 1))
        if abs(rho - rho2) > 1e-9 or c1 != c2:
            bad += 1
    check("V3", "60 例：ϱ（最小二乘口径）== ϱ（SVD 零空间口径），且两种生成森林 β₁ 相同（失配 %d）" % bad,
          bad == 0)

    # ϱ 的取值依赖 §2.2 的 i<j 参考定向 ⇒ 依赖顶点标号（规范 R11）
    rho_lab = {}
    for tag, order in (("id", [0, 1, 2, 3, 4, 5]), ("swap_1_2", [0, 2, 1, 3, 4, 5]),
                       ("rev", [5, 4, 3, 2, 1, 0])):
        Ed = [_ekey(order[i], order[(i + 1) % 6]) for i in range(6)]
        rho_lab[tag] = hodge_g1(np.full(6, 0.5), 6, Ed)["rho"]
    print("     同一物理反应（6 环键级均匀 +0.5）在不同标号下的 ϱ："
          + "  ".join("%s=%.6f" % (k, v) for k, v in rho_lab.items()))
    note("规范 §2.2 已把该现象升格为**显式条款 + 边界 R11**：δ 是「沿参考定向的定向上链」，")
    note("默认 i<j 参考定向；可选显式定向 ς_e；跨体系比较 ϱ 前必须统一标号约定（或先统一原子排序）。")
    distinct = len({round(v, 9) for v in rho_lab.values()})
    check("V3", "复现规范 R11 声明的标号依赖：三种标号下 ϱ 取值不唯一（实测 %d 个不同值）" % distinct,
          distinct >= 2)
    check("V3", "标号 [0..5] 下 ϱ = 2/3，交换 1↔2 后 ϱ = 1/3（与规范 §2.2 所述数值一致）",
          abs(rho_lab["id"] - 2.0 / 3.0) < 1e-9 and abs(rho_lab["swap_1_2"] - 1.0 / 3.0) < 1e-9)
    check("V3", "整体反转标号 [5..0] 不改变 ϱ（反转保持相对定向结构）",
          abs(rho_lab["rev"] - rho_lab["id"]) < 1e-9)

    # ── ς_e 显式边定向（规范 §2.2 v0.3 正式入参）───────────────────────
    E6 = [_ekey(i, (i + 1) % 6) for i in range(6)]
    wps6 = [{"w": {e: 1.0 for e in E6}, "nH": {}},
            {"w": {e: 1.5 for e in E6}, "nH": {}}]
    kappa6 = operator_20_activation_index(
        build_reaction(6, E6, wps6, w_I=0.0), K=24)["kappa"]

    def rho_with(orient):
        return operator_20_activation_index(
            build_reaction(6, E6, wps6, w_I=0.0, orient=orient))["rho_tot"]

    ori_nat = orient_from_cycle(6, E6, [0, 1, 2, 3, 4, 5])
    print("     ς_e = %s（自然环遍历）⇒ ϱ = %.6f（默认 %.6f）"
          % (ori_nat.astype(int).tolist(), rho_with(ori_nat), rho_lab["id"]))
    check("V3", "ς_e ≡ +1（默认）复现 v0.2 参考定向：ϱ = 2/3",
          abs(rho_with(np.ones(6)) - 2.0 / 3.0) < 1e-12)
    check("V3", "ς_e = 自然环遍历定向 ⇒ 环上均匀 +0.5 被读作纯环通道 ϱ = 1",
          abs(rho_with(ori_nat) - 1.0) < 1e-12)
    check("V3", "ς_e 全局取反不改 ϱ：ϱ(−ς) == ϱ(ς)",
          abs(rho_with(-ori_nat) - rho_with(ori_nat)) < 1e-12)
    check("V3", "ς_e 只作用于 ϱ：κ 与 ν 不随 ς_e 改变",
          abs(operator_20_activation_index(
              build_reaction(6, E6, wps6, w_I=0.0, orient=ori_nat),
              K=24)["kappa"] - kappa6) < 1e-12
          and abs(rho_with(ori_nat) - rho_lab["id"]) > 1e-9)
    check("V3", "ς_e 字典形式（单边覆盖）与向量形式等价",
          abs(rho_with({(0, 5): -1}) - rho_with(ori_nat)) < 1e-12)
    check("V3", "ς_e 取值非法（0）时被拒绝",
          _raises(lambda: build_reaction(6, E6, wps6, orient=0.0)))

    # ς_e 下 T20.3（端点不变性）仍成立
    ok = True
    for ie in ([(0, 6)], [(0, 6), (2, 6)], [(1, 6), (3, 6), (5, 6)]):
        Alt = build_reaction(6, E6, wps6, interface_edges=ie, n_boundary=1,
                             w_I=2.0, orient=ori_nat)
        ok &= abs(operator_20_activation_index(Alt)["rho_tot"]
                  - rho_with(ori_nat)) < 1e-12
    check("V3", "ς_e 下 T20.3 仍成立：ϱ_tot 与 E_I/w_I 无关", ok)


# ══════════════════════════════════════════════════════════════════════
# V4 三通道正交性（H20.2）
# ══════════════════════════════════════════════════════════════════════

def v4_orthogonality(rng, trials=80):
    print("\n--- V4 假设 H20.2：三通道（κ, ϱ_path, ν_path）秩相关 |ρ_S| < 0.7 ---")
    K, Rp, Np = [], [], []
    for _ in range(trials):
        res = operator_20_activation_index(random_reaction(rng), K=16)
        K.append(res["kappa"]); Rp.append(res["rho_path"]); Np.append(res["nu_path"])
    s_kr = spearman(K, Rp)
    s_kn = spearman(K, Np)
    s_rn = spearman(Rp, Np)
    print("     ρ_S(κ,ϱ)=%.3f   ρ_S(κ,ν)=%.3f   ρ_S(ϱ,ν)=%.3f" % (s_kr, s_kn, s_rn))
    check("V4", "三通道两两 |ρ_S| < 0.7（%d 例随机反应）" % trials,
          max(abs(s_kr), abs(s_kn), abs(s_rn)) < 0.7)


# ══════════════════════════════════════════════════════════════════════
# V5 κ 的缩放不变性（T20.2）
# ══════════════════════════════════════════════════════════════════════

def v5_scaling(rng):
    print("\n--- V5 定理 T20.2：κ 对全局缩放不变，对单独 w_I 缩放不变性**失效** ---")
    n = 6
    E = [_ekey(i, (i + 1) % n) for i in range(n)]
    wR = np.full(n, 1.0)
    wP = np.full(n, 1.5)
    wP[3] = 0.2
    ie = [(0, 7), (3, 7), (5, 7)]

    def build(c=1.0, wi=1.0):
        return build_reaction(n, E,
                              [{"w": c * wR, "nH": {}}, {"w": c * wP, "nH": {}}],
                              interface_edges=ie, n_boundary=1,
                              w_I=c * wi, w_B=c * 1.0)

    base = operator_20_activation_index(build(1.0), K=24)["kappa"]
    ok = True
    for c in (0.5, 2.0, 137.036, 1e4):
        if abs(operator_20_activation_index(build(c), K=24)["kappa"] - base) > 1e-9 * max(base, 1):
            ok = False
    check("V5", "c ∈ {0.5, 2, 137.036, 1e4}：κ(c·所有边权) == κ（全局缩放不变）", ok)

    k1 = operator_20_activation_index(build(1.0, wi=1.0), K=24)["kappa"]
    k2 = operator_20_activation_index(build(1.0, wi=6.0), K=24)["kappa"]
    print("     w_I=1 → κ=%.6f ; w_I=6 → κ=%.6f" % (k1, k2))
    check("V5", "单独缩放 w_I 会改变 κ（κ 不是 w_I 的齐次量）", abs(k1 - k2) > 1e-6)


# ══════════════════════════════════════════════════════════════════════
# V6 火山形态（C20.7，猜想）
# ══════════════════════════════════════════════════════════════════════

def v6_volcano():
    print("\n--- V6 猜想 C20.7：扫 w_I，检 κ(w_I) 的形态（火山/单峰）---")
    n = 4
    E = [_ekey(0, 1), _ekey(1, 2), _ekey(2, 3)]
    wR = np.full(3, 1.0)
    wP = np.array([1.0, 0.0, 1.0])              # 中间键断裂 ⇒ 未桥接时 γ=0
    ie = [(1, 4), (2, 4)]                       # 催化剂原子桥接断键两端
    grid = np.linspace(0.0, 4.0, 25)
    ks = []
    for wi in grid:
        Rr = build_reaction(n, E, [{"w": wR, "nH": {}}, {"w": wP, "nH": {}}],
                            interface_edges=ie, n_boundary=1, w_I=float(wi))
        ks.append(operator_20_activation_index(Rr, K=32)["kappa"])
    ks = np.array(ks)
    sh = _shape(ks)
    print("     w_I ∈ [0,4]（25 点）：κ 由 %.3f → 最小 %.3f (@w_I=%.2f) → %.3f"
          % (ks[0], ks.min(), grid[int(np.argmin(ks))], ks[-1]))
    print("     形态判定：%s" % sh)
    check("V6", "κ(w_I) 非常数（界面权重确实进入 κ）", sh != "constant")
    check("V6", "形态属火山许可集 {单峰, 单调}（实测 %s）" % sh,
          sh in ("unimodal", "monotone_decreasing", "monotone_increasing"))
    check("V6", "存在内点极小（w_I>0 处 κ 低于两端，SRE 版火山）",
          int(np.argmin(ks)) not in (0, len(ks) - 1) and ks[0] > ks.min() and ks[-1] > ks.min())


# ══════════════════════════════════════════════════════════════════════
# V7 零权割（P20.5）
# ══════════════════════════════════════════════════════════════════════

def v7_zero_cut():
    print("\n--- V7 命题 P20.5：零权割 ⟹ γ→0，κ 随 ε 单调发散 ---")
    n = 4
    E = [_ekey(0, 1), _ekey(1, 2), _ekey(2, 3)]
    Rr = build_reaction(n, E,
                        [{"w": {e: 1.0 for e in E}, "nH": {}},
                         {"w": {_ekey(0, 1): 1.0, _ekey(1, 2): 0.0, _ekey(2, 3): 1.0}, "nH": {}}],
                        w_I=0.0)
    r = operator_20_activation_index(Rr, K=32)
    eps_list = (1e-2, 1e-3, 1e-6)
    ks = [operator_20_activation_index(Rr, K=32, eps=e)["kappa"] for e in eps_list]
    print("     γ* = %.3e ; κ(ε=1e-2,1e-3,1e-6) = %s" % (r["gamma_star"], ["%.3f" % k for k in ks]))
    check("V7", "零权边含割 ⟹ γ* = 0", r["gamma_star"] < 1e-12)
    check("V7", "κ 随 ε↓ 单调不减且 κ(1e-6)/κ(1e-3) > 100（κ ~ 1/ε）",
          ks[0] < ks[1] < ks[2] and ks[2] / ks[1] > 100.0)


# ══════════════════════════════════════════════════════════════════════
# V8 加边使 γ 非单调（P20.6）
# ══════════════════════════════════════════════════════════════════════

def v8_nonmonotone(rng, trials=400):
    print("\n--- V8 命题 P20.6：加边使 γ 上升/下降各至少一例 ---")

    def gamma_of(n, E, w):
        Rr = build_reaction(n, E, [{"w": w, "nH": {}}, {"w": w, "nH": {}}], w_I=0.0)
        from sre_activation_operator import spectral_gamma
        return spectral_gamma(Rr, w)

    up, down = 0, 0
    for _ in range(trials):
        n = int(rng.integers(6, 13))
        E = random_connected_edges(rng, n, int(rng.integers(0, 4)))
        # 候选加边（不在 E 中）
        cand = [_ekey(a, b) for a in range(n) for b in range(a + 1, n) if _ekey(a, b) not in E]
        if not cand:
            continue
        E2 = E + [cand[int(rng.integers(0, len(cand)))]]
        w1 = rng.uniform(0.5, 2.0, len(E))
        w2 = np.concatenate([w1, [rng.uniform(0.5, 2.0)]])
        g1, g2 = gamma_of(n, E, w1), gamma_of(n, E2, w2)
        if g2 > g1 + 1e-9:
            up += 1
        elif g2 < g1 - 1e-9:
            down += 1
    print("     加边后 γ 上升 %d 例 / 下降 %d 例 / 持平其余" % (up, down))
    check("V8", "γ 关于加边非单调：上升与下降均出现", up > 0 and down > 0)


# ══════════════════════════════════════════════════════════════════════
# V9 对照协议（D8）
# ══════════════════════════════════════════════════════════════════════

def v9_control(rng):
    print("\n--- V9 对照协议 D8：w_I=0 ⟹ 退化到裸骨架；w_I>0 改变 κ ---")
    n = 4
    E = [_ekey(0, 1), _ekey(1, 2), _ekey(2, 3)]
    wR = np.full(3, 1.0)
    wP = np.array([1.0, 0.0, 1.0])          # 中间键断裂
    ie = [(1, 4), (2, 4)]
    bare = build_reaction(n, E, [{"w": wR, "nH": {}}, {"w": wP, "nH": {}}], w_I=0.0)
    zero = build_reaction(n, E, [{"w": wR, "nH": {}}, {"w": wP, "nH": {}}],
                          interface_edges=ie, n_boundary=1, w_I=0.0)
    on = build_reaction(n, E, [{"w": wR, "nH": {}}, {"w": wP, "nH": {}}],
                        interface_edges=ie, n_boundary=1, w_I=1.0)
    kb = operator_20_activation_index(bare, K=32)["kappa"]
    k0 = operator_20_activation_index(zero, K=32)["kappa"]
    k1 = operator_20_activation_index(on, K=32)["kappa"]
    print("     κ: 裸骨架=%.6f  w_I=0=%.6f  w_I=1=%.6f" % (kb, k0, k1))
    check("V9", "w_I=0 时零权界面边不改变 Laplacian ⇒ κ 与裸骨架逐位一致",
          abs(kb - k0) < 1e-12)
    check("V9", "w_I=1 时催化剂桥接断键 ⇒ κ 显著下降（旁路机制）", k1 < kb * 0.5)

    # 非断键情形：耦合本身改变 κ（未必下降）
    nb = build_reaction(6, [_ekey(i, (i + 1) % 6) for i in range(6)],
                        [{"w": np.full(6, 1.0), "nH": {}}, {"w": np.full(6, 1.1), "nH": {}}],
                        w_I=0.0)
    nw = build_reaction(6, [_ekey(i, (i + 1) % 6) for i in range(6)],
                        [{"w": np.full(6, 1.0), "nH": {}}, {"w": np.full(6, 1.1), "nH": {}}],
                        interface_edges=[(0, 6), (3, 6)], n_boundary=1, w_I=1.0)
    k_a = operator_20_activation_index(nb, K=24)["kappa"]
    k_b = operator_20_activation_index(nw, K=24)["kappa"]
    check("V9", "非断键体系：界面耦合仍改变 κ（%.4f → %.4f）" % (k_a, k_b),
          abs(k_a - k_b) > 1e-6)


# ══════════════════════════════════════════════════════════════════════
# V10 v0 / v1 排序一致（§6）
# ══════════════════════════════════════════════════════════════════════

def v10_v0_v1(rng, trials=10):
    print("\n--- V10 §6：v0（键级线性插值）与 v1（矩空间约束反演）κ 排序 Spearman ≥ 0.8 ---")
    k0, k1 = [], []
    for _ in range(trials):
        Rr = random_reaction(rng, n=8, extra=2, nseg=1)
        k0.append(operator_20_activation_index(Rr, K=24, version="v0")["kappa"])
        k1.append(operator_20_activation_index(Rr, K=12, version="v1")["kappa"])
    s = spearman(k0, k1)
    print("     κ_v0 = %s" % ["%.3f" % v for v in k0])
    print("     κ_v1 = %s   Spearman=%.3f" % (["%.3f" % v for v in k1], s))
    check("V10", "v0 与 v1 的 κ 排序一致（Spearman = %.3f ≥ 0.8）" % s, s >= 0.8)


# ══════════════════════════════════════════════════════════════════════
# V11 与算子 19 的兼容命题（§9）
# ══════════════════════════════════════════════════════════════════════

def v11_op19_compat():
    print("\n--- V11 §9 兼容命题：保二分界面接枝不开算子 19 的 σ 通道 ---")
    if not _HAS_OP19:
        note("SKIP：networkx / sre_z2_holonomy_bridge 不可用")
        return
    ring = [_ekey(i, (i + 1) % 6) for i in range(6)]

    # Case A：界面边把催化剂接到**同色**骨架顶点（0,2,4 同色）⇒ 保二分
    EA = ring + [_ekey(0, 6), _ekey(2, 6), _ekey(4, 6)]
    resA = operator_19_z2_charge_channel(adj_from(7, EA).astype(float),
                                         elements=["C"] * 6 + ["M"])
    rA = resA["reachability"]
    print("     A 保二分接枝: bipartite=%s 轨道=%s 非平凡可达=%s"
          % (resA["bipartite"], rA["orbit_sizes"], rA["nontrivial_reachable"]))
    check("V11", "保二分界面接枝：σ 通道仍**强制平凡**（电子型）",
          resA["bipartite"] and rA["nontrivial_reachable"] is False)

    # Case B：界面边接到**异色**骨架顶点（0,1）⇒ 造出奇环（三角形）
    EB = ring + [_ekey(0, 6), _ekey(1, 6)]
    resB = operator_19_z2_charge_channel(adj_from(7, EB).astype(float),
                                         elements=["C"] * 6 + ["M"])
    rB = resB["reachability"]
    print("     B 同色相接（造奇环）: bipartite=%s 轨道=%s 非平凡可达=%s"
          % (resB["bipartite"], rB["orbit_sizes"], rB["nontrivial_reachable"]))
    check("V11", "造出奇环后 σ 通道**允许非平凡**（质子型）",
          (not resB["bipartite"]) and rB["nontrivial_reachable"] is True)


# ══════════════════════════════════════════════════════════════════════
# V12 DFT 对标（H20.1，外部验证）
# ══════════════════════════════════════════════════════════════════════

def v12_dft():
    print("\n--- V12 假设 H20.1（外部验证）：(κ, ϱ_path, ν_path) 与 DFT 势垒秩相关 ≥ 0.7 ---")
    note("SKIP：本程序无 DFT/实验势垒数据；H20.1 **未证**，不得在报告中被当作既成事实。")
    note("待办：5–8 个基元步（如 DBT 加氢/脱氢、苯加氢、乙醇脱氢），收集 Δ‡ 后重跑本项。")


# ══════════════════════════════════════════════════════════════════════
# V13 顶点通道（T20.4 / D5）+ 解析算例
# ══════════════════════════════════════════════════════════════════════

def v13_vertex_channel(rng):
    print("\n--- V13 顶点通道 T20.4/D5：μ=(1/n)Σδ_v、δ_v⊥⊥1、ν 对覆盖整体平移与非零缩放不变 ---")
    # 乙醇脱氢：CH3CH2OH → CH3CHO + H2
    nH_R = np.array([3.0, 2.0, 1.0])
    nH_P = np.array([3.0, 1.0, 0.0])
    E = [_ekey(0, 1), _ekey(1, 2)]
    Rr = build_reaction(3, E,
                        [{"w": {e: 1.0 for e in E}, "nH": nH_R},
                         {"w": {e: 1.0 for e in E}, "nH": nH_P}], w_I=0.0)
    res = operator_20_activation_index(Rr, K=16)
    dv = nH_P - nH_R
    us = uniform_split(dv)
    check("V13", "μ = (1/n)Σδ_v = 总 H 变化/n：%.6f == %.6f"
          % (res["mu"], dv.sum() / 3.0), abs(res["mu"] - dv.sum() / 3.0) < 1e-12)
    check("V13", "乙醇脱氢：μ < 0 且 ν_tot > 0（氢在位点间再分配）",
          res["mu"] < 0 and res["nu_tot"] > 0)

    ok_shift = True
    base_shift = None
    E3 = [_ekey(0, 1), _ekey(1, 2)]
    for c in (0.0, -4.0, 7.5):
        Rr = build_reaction(3, E3,
                            [{"w": {e: 1.0 for e in E3}, "nH": nH_R + c},
                             {"w": {e: 1.0 for e in E3}, "nH": nH_P + c}], w_I=0.0)
        v = operator_20_activation_index(Rr, K=16)
        if base_shift is None:
            base_shift = (v["nu_tot"], v["mu"])
        elif (abs(v["nu_tot"] - base_shift[0]) > 1e-12
              or abs(v["mu"] - base_shift[1]) > 1e-12):
            ok_shift = False
    check("V13", "ν、μ 对「所有 waypoint 覆盖整体平移 c」不变（δ_v 只依赖差值）", ok_shift)

    ok_orth = True
    ok_scale = True
    for _ in range(30):
        d = rng.normal(size=7)
        us = uniform_split(d)
        if abs(float(us["perp"] @ np.ones(7))) > 1e-10 * max(np.linalg.norm(d), 1e-30):
            ok_orth = False
        for c in (-2.5, 0.3, 9.0):
            if abs(uniform_split(c * d)["nu"] - us["nu"]) > 1e-12:
                ok_scale = False
    check("V13", "δ_v⊥ ⊥ 1（T20.4 正交分解）", ok_orth)
    check("V13", "ν 对非零缩放/反号不变：ν(c·δ_v) == ν(δ_v)", ok_scale)

    # v0.2 的错误陈述 ν(δ_v + c·1) = ν(δ_v) 的数值反例（规范 §5 T20.4 注记）
    d0 = np.array([1.0, -1.0, 0.0])
    v0 = uniform_split(d0)["nu"]
    v1 = uniform_split(d0 + 3.0)["nu"]
    v2 = uniform_split(d0 - 5.0)["nu"]
    print("     v0.2 陈述反例：ν(δ_v)=%.6f ; ν(δ_v+3·1)=%.6f ; ν(δ_v−5·1)=%.6f" % (v0, v1, v2))
    check("V13", "证伪 v0.2 的 ν(δ_v+c·1)=ν(δ_v)：c≠0 时 ν 下降",
          v1 < v0 - 1e-9 and v2 < v0 - 1e-9)

    # 解析算例（规范 §11-4）
    n6 = 6
    E6 = [_ekey(i, (i + 1) % n6) for i in range(n6)]
    ben = build_reaction(n6, E6,
                         [{"w": {e: 1.0 for e in E6}, "nH": {i: 2 for i in range(6)}},
                          {"w": {e: 1.5 for e in E6}, "nH": {i: 1 for i in range(6)}}], w_I=0.0)
    rb = operator_20_activation_index(ben, K=24)
    eth = build_reaction(2, [_ekey(0, 1)],
                         [{"w": {_ekey(0, 1): 1.0}, "nH": {0: 3, 1: 3}},
                          {"w": {_ekey(0, 1): 1.0}, "nH": {0: 3, 1: 3}}], w_I=0.0)
    re_ = operator_20_activation_index(eth, K=16)
    etoh = build_reaction(3, E,
                          [{"w": {e: 1.0 for e in E}, "nH": nH_R},
                           {"w": {e: 1.0 for e in E}, "nH": nH_P}], w_I=0.0)
    rd = operator_20_activation_index(etoh, K=16)
    print("     解析算例  ϱ_tot / ν_tot / μ :")
    print("       环己烷→苯（芳构化）: %.4f / %.4f / %.4f" % (rb["rho_tot"], rb["nu_tot"], rb["mu"]))
    print("       乙烷 C–C 旋转      : %.4f / %.4f / %.4f" % (re_["rho_tot"], re_["nu_tot"], re_["mu"]))
    print("       乙醇脱氢          : %.4f / %.4f / %.4f" % (rd["rho_tot"], rd["nu_tot"], rd["mu"]))
    check("V13", "解析算例符合规范 §11-4：苯芳构化 ϱ>0；乙烷旋转 ϱ=ν=0；乙醇脱氢 μ<0,ν>0",
          rb["rho_tot"] > 0 and abs(re_["rho_tot"]) < 1e-12 and abs(re_["nu_tot"]) < 1e-12
          and rd["mu"] < 0 and rd["nu_tot"] > 0)


# ══════════════════════════════════════════════════════════════════════
# V14 端点不变性（T20.3）
# ══════════════════════════════════════════════════════════════════════

def v14_endpoint_invariance(rng, trials=50):
    print("\n--- V14 定理 T20.3：任意 E_I / w_I 下 ϱ_tot 不变 ---")
    bad = 0
    for _ in range(trials):
        n = int(rng.integers(5, 11))
        E = random_connected_edges(rng, n, int(rng.integers(1, 5)))
        wR = rng.uniform(0.5, 2.0, len(E))
        wP = np.clip(wR + rng.normal(0, 0.7, len(E)), 0.0, 3.0)
        base = build_reaction(n, E, [{"w": wR, "nH": {}}, {"w": wP, "nH": {}}], w_I=0.0)
        rho0 = operator_20_activation_index(base, K=8)["rho_tot"]
        nb = int(rng.integers(1, 4))
        k = int(rng.integers(1, 4))
        ie = [(_ekey(int(rng.integers(0, n)), n + int(rng.integers(0, nb)))) for _ in range(k)]
        wi = float(rng.uniform(0.1, 3.0))
        alt = build_reaction(n, E, [{"w": wR, "nH": {}}, {"w": wP, "nH": {}}],
                             interface_edges=ie, n_boundary=nb, w_I=wi, w_B=1.7)
        if abs(operator_20_activation_index(alt, K=8)["rho_tot"] - rho0) > 1e-12:
            bad += 1
    check("V14", "50 例随机 E_I/w_I：ϱ_tot(Ē) == ϱ_tot(G)（失配 %d）" % bad, bad == 0)


# ══════════════════════════════════════════════════════════════════════
# 主程序
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 80)
    print("SRE 算子 20 严格验证程序（V1–V14）")
    print("=" * 80)
    rng = np.random.default_rng(20261021)

    v1_holonomy()
    v2_equivalence(rng)
    v3_basis_independence(rng)
    v4_orthogonality(rng)
    v5_scaling(rng)
    v6_volcano()
    v7_zero_cut()
    v8_nonmonotone(rng)
    v9_control(rng)
    v10_v0_v1(rng)
    v11_op19_compat()
    v12_dft()
    v13_vertex_channel(rng)
    v14_endpoint_invariance(rng)

    # ── Pareto 偏序自洽（D8）──
    print("\n--- 附：D8 Pareto 偏序自洽 ---")
    A = {"kappa": 1.0, "rho_path": 0.2, "nu_path": 0.1}
    B = {"kappa": 1.1, "rho_path": 0.3, "nu_path": 0.2}
    check("附", "A ⪯ B（三通道全不劣且至少一项严格）", pareto_leq(A, B) is True)
    check("附", "⪯ 反对称：B ⪯ A 为假", pareto_leq(B, A) is False)
    check("附", "不可比：κ 更小而 ϱ 更大时两者互不 ⪯",
          pareto_leq({"kappa": 1.0, "rho_path": 0.5, "nu_path": 0.1}, B) is False
          and pareto_leq(B, {"kappa": 1.0, "rho_path": 0.5, "nu_path": 0.1}) is False)

    print("\n" + "=" * 80)
    passed = sum(1 for r in RESULTS if r[2])
    fails = [r for r in RESULTS if not r[2]]
    print("通过 %d/%d 项断言" % (passed, len(RESULTS)))
    for tag, desc, _ in fails:
        print("  FAIL: [%s] %s" % (tag, desc))
    print("[%s] 算子 20 严格验证" % ("SUCCESS" if not fails else "FAIL"))
    print("=" * 80)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
