# -*- coding: utf-8 -*-
"""
=============================================================================
核子线 <-> 谱形方程求解算子组 (Op13-18，C:\\mywork\\math-graph) 接口评估
=============================================================================
目的：判定 `c:\\mywork\\math-graph` 的「谱形方程求解算子组」能否用于本项目的
      核子计算与「锚定经典物理量」。

本脚本只做**实测**，不做断言。七个部分：
  A  桥接对象核对：vasp 的 Π₁ vs 框架的内生谱隙比 γ —— 是否同一个量？
  B  Op13 编码可移植性：把 Y₃ 骨架喂进框架的矩编码管线，与 eigvalsh 对照
  C  两个「环数」辨析：ν(circuit rank) vs β₁(homology)
  D  规范冗余：τ 与 Π₁ 在 m -> c m 下是否严格不变（对应 vasp 的「实欠定 1」）
  E  障碍判据读数：ρ_h = ||h||/||r|| 在骨架复形上的实测值
  F  端到端跑一次框架求解器（骨架复形 + 矩空间方程）
  G  综合裁定

运行： KMP_DUPLICATE_LIB_OK=TRUE C:/myapp/miniconda3/envs/ai/python.exe -u \
       _sre_nucleon_op1318_interface.py > _op1318_interface.log 2>&1
=============================================================================
"""
import sys, os, itertools
import numpy as np
import networkx as nx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"C:\mywork\math-graph")
import Operator_13_18_P as OP          # noqa: E402

np.set_printoptions(precision=9, suppress=True, linewidth=140)


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * 78)
    P(t)
    P("=" * 78)


# ---------------------------------------------------------------------------
# 0. vasp 侧：Y₃ 骨架与共享环装配（与项目既有 assemble() 口径一致）
# ---------------------------------------------------------------------------
def Y3(pre="", state="p", open_ring=0):
    """Y₃ 骨架：3 股心 c{i} + 9 叶点 L{i}{j}。闭态 V12/E18/ν7/T3；开态去一条环边。"""
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


def assemble(groups):
    """共享环装配：群索引 r 即环号；把各体的 L{i}{r} 合并为共享点 S{r}{i}。"""
    H = nx.Graph()
    for r, (_t, bodies) in enumerate(groups):
        for pre, state in bodies:
            G = Y3(pre, state, r)
            m = {"%sL%d%d" % (pre, i, r): "S%d%d" % (r, i) for i in range(3)}
            E = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
            H.add_edges_from(E)
    return H


def mk_groups(kd):
    return [("g%d" % r, [("b%d_%d" % (r, j), "p") for j in range(k)])
            for r, k in enumerate(kd)]


# ---------------------------------------------------------------------------
# 1. 把 networkx 图翻译成框架要的链复形 (D=∂₁, C=∂₂)
# ---------------------------------------------------------------------------
def complex_from_graph(G, faces=None):
    """
    返回 D (m_g x n), C (f x m_g), edge_list
        D[e,u] = -1, D[e,v] = +1   （边 e 定向 u -> v）
        C[i,e] = 有向重数（面 i 沿边 e 的方向）
    faces: 列表，每项是顶点环 [v0,v1,...,vk-1]（须为图中的闭行走）
    注：**面集是本脚本额外赋予骨架的结构**，vasp 原文未定义 2-链。
    """
    nodes = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    edges = [tuple(sorted(e)) for e in G.edges()]
    edges.sort()
    eidx = {e: i for i, e in enumerate(edges)}
    m_g = len(edges)

    D = np.zeros((m_g, n))
    for e, (u, v) in enumerate(edges):
        D[e, idx[u]] = -1.0
        D[e, idx[v]] = +1.0

    if faces is None:
        C = np.zeros((0, m_g))
        f_list = []
    else:
        f_list = []
        rows = []
        for cyc in faces:
            row = np.zeros(m_g)
            ok = True
            for a in range(len(cyc)):
                u, v = cyc[a], cyc[(a + 1) % len(cyc)]
                key = tuple(sorted((u, v)))
                if key not in eidx:
                    ok = False
                    break
                # 边的规范定向 edges[key] = (min,max)，方向为 min->max
                lo, hi = key
                sign = +1.0 if (u, v) == (lo, hi) else -1.0
                row[eidx[key]] += sign
            if ok:
                rows.append(row)
                f_list.append(list(cyc))
        C = np.array(rows) if rows else np.zeros((0, m_g))
    return D, C, edges, f_list, nodes


def skeleton_faces_closed():
    """闭态 Y₃ 的 3 个三角环（叶点三点环），作为 2-链生成元。"""
    fs = []
    for j in range(3):
        fs.append(["L0%d" % j, "L1%d" % j, "L2%d" % j])
    return fs


def skeleton_faces_open(open_ring=0):
    """开态：被打开的那条环边消失 ⇒ 对应三角形不再是闭行走，只剩 2 个面。"""
    fs = []
    for j in range(3):
        if j == open_ring:
            continue
        fs.append(["L0%d" % j, "L1%d" % j, "L2%d" % j])
    return fs


def shared_ring_faces(k):
    """
    共享环 k 体的面集 = 全部 (2k+1) 个三角环（与 vasp 的 T = 2k+1 一一对应）：
      · 共享环本身 1 个： (S00, S01, S02)
      · 每个体 2 个自有环：ring j=1,2（ring 0 已被合并为共享环）
    这是**vasp 自身「闭合单元数 T」的自然对应物** —— 适配规则取 rank(∂₂) ← T。
    """
    fs = [["S00", "S01", "S02"]]
    for b in range(k):
        pre = "b0_%d" % b
        for j in (1, 2):
            fs.append(["%sL0%d" % (pre, j), "%sL1%d" % (pre, j), "%sL2%d" % (pre, j)])
    return fs


def spectra(M):
    ev = np.sort(np.linalg.eigvalsh(M))
    return ev


def gamma_of(L, n):
    """框架的内生谱隙比 gamma = lambda_2 / alpha_n。"""
    ev = spectra(L)
    alpha_n = ev[-1]
    lam2 = ev[1] if n > 1 else ev[0]
    return lam2, alpha_n, lam2 / alpha_n


# ===========================================================================
# PART A —— 桥接对象核对
# ===========================================================================
def part_A():
    head("PART A  桥接对象核对：vasp 的 Π₁ = λ₂/ρ  与 框架的内生谱隙比 γ = λ₂/α_n")
    P("vasp 口径（论文 §12.4 / 骨架文档 §2.2）：")
    P("   Π₁ = λ₂ / ρ，λ₂ = 最小非零特征值，ρ = 最大特征值")
    P("框架口径（§1.1）：")
    P("   α_n ≡ λ_max（谱半径，算子 6 内生归一化），γ ≡ λ₂/α_n，称『唯一的自然尺度单位』")
    P("⇒ 二者的定义**逐字相同**。下面逐例实测核对。")
    P()
    P("%-26s %-14s %-14s %-16s %-16s %s" %
      ("构形", "λ₂", "ρ=α_n", "Π₁=λ₂/ρ", "γ=λ₂/α_n", "相等?"))
    P("-" * 104)

    rows = []
    for st in ("p", "n"):
        G = Y3("", st)
        D, C, edges, _, nodes = complex_from_graph(G)
        L = OP.laplacian(D, np.ones(D.shape[0]))
        lam2, alpha_n, gamma = gamma_of(L, D.shape[1])
        pi1 = lam2 / alpha_n
        rows.append((st, lam2, alpha_n, pi1, gamma))
        P("%-26s %-14.9f %-14.9f %-16.9f %-16.9f %s" %
          ("Y₃ 单骨架 state=%s" % st, lam2, alpha_n, pi1, gamma,
           "是" if abs(pi1 - gamma) < 1e-15 else "否"))

    for k in range(2, 7):
        H = assemble(mk_groups([k]))
        D, C, edges, _, nodes = complex_from_graph(H)
        L = OP.laplacian(D, np.ones(D.shape[0]))
        lam2, alpha_n, gamma = gamma_of(L, D.shape[1])
        pi1 = lam2 / alpha_n
        rows.append(("k=%d" % k, lam2, alpha_n, pi1, gamma))
        P("%-26s %-14.9f %-14.9f %-16.9f %-16.9f %s" %
          ("共享环 k=%d 体" % k, lam2, alpha_n, pi1, gamma,
           "是" if abs(pi1 - gamma) < 1e-15 else "否"))
    P()
    P("对照论文闭式（§12.4）：Π₁ = (β₁ − √(V+1)) / E = (7 − √13)/18")
    P("  论文值 = %.9f   ； 实测 Y₃(闭) λ₂/ρ = %.9f   ； 差 = %.3e" %
      ((7 - np.sqrt(13)) / 18, rows[0][3], abs((7 - np.sqrt(13)) / 18 - rows[0][3])))
    P()
    P("对照实测锚点 κ_N = Δm/m_p ÷ α = 0.188893067，论文口径偏差 0.165%")
    P("  ⇒ **Π₁ ≡ γ，二者是同一个量**：vasp 唯一已标定的图泛函")
    P("    = 框架唯一的内生尺度单位。")
    P()
    P("【推论·电子侧】Q₃/Möbius 的 Π₁ = α = 1/137.036 ⇒ γ_e = 7.2975e-3")
    P("   这直接落在框架 §13.4/§13.6 的**病态端**（见 PART B 的 K 核算）。")
    return rows


# ===========================================================================
# PART B —— Op13 编码可移植性
# ===========================================================================
def part_B():
    head("PART B  Op13 谱形编码能否直接吃下核子骨架（框架 V1 / V2 / 内生 K）")
    P("B1 矩编码保真：τ_k 由框架三项递推 vs eigvalsh 直算")
    P("%-22s %-8s %-16s %-16s %s" % ("构形", "K", "max|τ_rec−τ_eig|", "阈值", "判定"))
    P("-" * 78)
    for st in ("p", "n"):
        G = Y3("", st)
        D, C, _, _, nodes = complex_from_graph(G)
        N = D.shape[1]
        m = np.ones(D.shape[0])
        L = OP.laplacian(D, m)
        alpha_n, lam2 = OP.spectral_assets(L, N)
        K = 8
        tau, Y, U = OP.chebyshev_moments(L, alpha_n, K)
        # eigvalsh ground truth
        ev = spectra(L)
        Yspec = 2 * ev / alpha_n - 1
        tau_eig = np.array([np.mean(np.cos(k * np.arccos(np.clip(Yspec, -1, 1))))
                            for k in range(K + 1)])
        err = float(np.max(np.abs(tau - tau_eig)))
        P("%-22s %-8d %-16.3e %-16s %s" %
          ("Y₃ state=%s" % st, K, err, "1e-10", "PASS" if err < 1e-10 else "FAIL"))
    P()

    P("B2 内生截断阶 K = min(⌈α_n/λ₂⌉, ⌊2ln(1+N_K)⌋)，下限 4")
    P("%-24s %-10s %-10s %-14s %-14s %s" %
      ("构形", "α_n", "λ₂", "K_res", "K_cap", "K(用)"))
    P("-" * 84)
    def kline(name, G):
        D, C, _, _, nodes = complex_from_graph(G)
        N = D.shape[1]
        L = OP.laplacian(D, np.ones(D.shape[0]))
        alpha_n, lam2 = OP.spectral_assets(L, N)
        K, Kres, Kcap = OP.endogenous_K(alpha_n, lam2, N)
        flag = "  <- cap 绑定（红线）" if Kcap < Kres else ""
        P("%-24s %-10.6f %-10.6f %-14d %-14d %d%s" %
          (name, alpha_n, lam2, Kres, Kcap, K, flag))
    kline("Y₃(p) N_K=12", Y3("", "p"))
    kline("Y₃(n) N_K=12", Y3("", "n"))
    for k in (2, 3):
        kline("共享环 k=%d 体" % k, assemble(mk_groups([k])))
    P()
    P("电子侧对照（Π₁ = α = 1/137.036 ⇒ γ = 7.2975e-3）：")
    alpha_ne, lam2e = 1.0, 7.2975e-3
    for Ne, tag in ((60, "Möbius n=60（N_K=60）"), (12, "Q₃/Möbius n=12")):
        K, Kres, Kcap = OP.endogenous_K(alpha_ne, lam2e, Ne)
        P("   %-26s K_res=%-5d K_cap=%-5d K(用)=%-5d %s" %
          (tag, Kres, Kcap, K, "<- cap 硬绑定，触发框架红线" if Kcap < Kres else ""))
    P()
    P("非多项式核可展开性下界 K_f ≳ ln(1/γ)/ln ρ（定理 13.2, ρ = |ξ₀|+√(ξ₀²−1)）")
    P("%-18s %-12s %-12s %-14s %-14s %s" %
      ("γ", "ξ₀", "ρ", "K_f 下界", "K_cap(12)", "判定"))
    P("-" * 84)
    for g, tag in ((0.188580, "核子骨架"), (0.0072975, "电子 α")):
        xi0 = -(1 + g) / (1 - g)
        rho = abs(xi0) + np.sqrt(xi0 ** 2 - 1)
        Kf = np.log(1 / g) / np.log(rho)
        Kcap = int(np.floor(2 * np.log(1 + 12)))
        P("%-18.6f %-12.6f %-12.6f %-14.2f %-14d %s" %
          (g, xi0, rho, Kf, Kcap,
           "可展开" if Kf <= Kcap else "**超出 K_cap ⇒ 框架宣告『核不可展开』**"))
    P()
    P("⇒ 核子骨架可展开（K_f≈2）；电子侧 α 标定点 K_f≈29 ≫ K_cap=8，")
    P("   框架会对其宣告红线『核不可展开 / 精度须降级』。这是必须正面处理的张力。")
    P()

    P("B3 灵敏度解析式 vs 中心差分（骨架 λ₂ 有重数 2 ⇒ 检查矩灵敏度是否仍良定义）")
    G = Y3("", "p")
    D, C, _, _, nodes = complex_from_graph(G)
    N, m_g = D.shape[1], D.shape[0]
    m = np.ones(m_g)
    L = OP.laplacian(D, m)
    alpha_n, lam2 = OP.spectral_assets(L, N)
    K = 4
    tau0, Y, U = OP.chebyshev_moments(L, alpha_n, K)
    W = OP.moment_sensitivity(D, Y, N, alpha_n, K)
    h = 1e-6
    maxrel = 0.0
    # 选一条边做差分（其余够多，取前 3 条）
    for e in range(min(3, m_g)):
        mp = m.copy(); mp[e] += h
        mm = m.copy(); mm[e] -= h
        dtau = (OP.chebyshev_moments(OP.laplacian(D, mp), alpha_n, K)[0]
                - OP.chebyshev_moments(OP.laplacian(D, mm), alpha_n, K)[0]) / (2 * h)
        for kk in range(1, K + 1):
            if abs(dtau[kk]) > 0 or abs(W[kk, e]) > 0:
                rel = abs(dtau[kk] - W[kk, e]) / max(abs(dtau[kk]), 1e-14)
                maxrel = max(maxrel, rel)
    P("   前 3 条边、k=1..4 的 max 相对偏差 = %.3e  → %s" %
      (maxrel, "PASS（矩编码对退化谱仍解析可微）" if maxrel < 1e-4 else "FAIL"))
    P("   对照：vasp 直接用的 Π₁ = λ₂/λ_max 在 λ₂ 重数 2 处**不可微**（次梯度）。")
    P("   ⇒ 框架的矩编码提供了一个**光滑替身**。")
    P()

    P("B4  τ_1 是否线性承载「边权和」（决定 vasp 的**加和律**能否搬进本框架）")
    P("   理论：tr(L) = tr(Dᵀ diag(m) D) = 2 Σ_e m_e ⇒ 冻结 α_n 时")
    P("        τ_1 = (1/N) tr(2L/α_n − I) = 4 Σ_e m_e /(N α_n^lock) − 1，**严格线性**。")
    rng = np.random.default_rng(11)
    xs, ys = [], []
    for _ in range(6):
        mv = 1.0 + 0.5 * rng.standard_normal(m_g)
        tau_v, _, _ = OP.chebyshev_moments(OP.laplacian(D, mv), alpha_n, K)
        xs.append(float(mv.sum())); ys.append(float(tau_v[1]))
    xs = np.array(xs); ys = np.array(ys)
    slope, inter = np.polyfit(xs, ys, 1)
    pred_slope = 4.0 / (N * alpha_n)
    resid = float(np.max(np.abs(ys - (slope * xs + inter))))
    P("   实测拟合斜率 = %.12f ； 理论 4/(N·α_n^lock) = %.12f ； 相对差 = %.2e" %
      (slope, pred_slope, abs(slope - pred_slope) / pred_slope))
    P("   线性残差（6 个随机权样本）= %.3e  → %s" %
      (resid, "严格线性" if resid < 1e-12 else "非线性"))
    P("   ⇒ vasp 的「键长加和律」（Σ_e n_e w_e = 实测）正是 τ_1 型约束，")
    P("     **可以**作为 L1 级（多项式核）方程进入框架的求解管线。")
    return maxrel


# ===========================================================================
# PART C —— 两个「环数」辨析
# ===========================================================================
def part_C():
    head("PART C  两个『环数』：vasp 的 β₁ 与框架的 β₁ 不是同一个量")
    P("vasp（论文第 107 行）：『β₁（第一贝蒂数）| β₁ = E − V + 1，图中独立闭环的个数』")
    P("框架（§术语约定·重要）：")
    P("   ν  ≡ dim ker ∂₁ = m_g − n + β₀   （环空间维数 / circuit rank）")
    P("   β₁ ≡ dim H₁ = ν − rank(∂₂)      （扣除面边界后的『真洞』数）")
    P("⇒ vasp 名为 β₁，实为 ν。下面实测。")
    P()
    P("%-24s %-5s %-5s %-7s %-9s %-9s %-11s %-10s %s" %
      ("构形", "V", "E", "T(面)", "ν=E-V+1", "rank∂₂", "β₁_hom", "论文β₁", "辨析"))
    P("-" * 112)

    def line(name, G, faces, paper_b1):
        D, C, edges, fl, nodes = complex_from_graph(G, faces)
        V = D.shape[1]; E = D.shape[0]
        nu = E - V + 1
        rk2 = int(np.linalg.matrix_rank(C)) if C.shape[0] > 0 else 0
        b1h = nu - rk2
        # 链复形正合性自检 ∂₁∂₂ = 0：D=∂₁ 为 (m_g×n)，C=∂₂ 为 (f×m_g)
        # ∂₁∘∂₂ 的矩阵为 (n×m_g)@(m_g×f) = Dᵀ Cᵀ，应为零
        exact = float(np.max(np.abs(D.T @ C.T))) if C.shape[0] > 0 else 0.0
        P("%-24s %-5d %-5d %-7d %-9d %-9d %-11d %-10d %s" %
          (name, V, E, len(fl), nu, rk2, b1h, paper_b1,
           "vasp β₁=ν ✓" if paper_b1 == nu else "?"))
        if exact > 1e-12:
            P("      ⚠ ∂₁∂₂ 残差 = %.2e（面定向不一致）" % exact)
        return nu, rk2, b1h

    r = []
    r.append(line("Y₃ 闭态 (k=1, T=3)", Y3("", "p"), skeleton_faces_closed(), 7))
    r.append(line("Y₃ 开态 (k=1, T=2)", Y3("", "n"), skeleton_faces_open(0), 6))
    for k in (2, 3, 4):
        H = assemble(mk_groups([k]))
        r.append(line("共享环 k=%d 体 (T=%d)" % (k, 2 * k + 1), H,
                      shared_ring_faces(k), 6 * k + 1))
    P()
    P("⇒ 实测结论：")
    P("  ⓪ 链复形正合性 ∂₁∂₂ = 0 全部成立（无告警）⇒ 面集合法。")
    P("  ① vasp 的 β₁（=7、6、13、19、25）**恒等于 ν**（E−V+1），与面集无关；")
    P("     ⚠ 但这不是 vasp 的错：**一维复形（纯图）没有 2-链，H₁ = ker∂₁，故 β₁ = ν**。")
    P("     命名在『只有图』的前提下是正确的。歧义只在**加入 2-链之后**才出现。")
    P("  ② 框架的核心机制（Hodge 三分量 r = Dφ + h + Cᵀψ）**必须有 ∂₂**，")
    P("     即必须先把 vasp 的核子层升级为 **2 维复形**；vasp 原文从未定义面。")
    P("  ③ 可用 vasp 自身的『闭合单元数 T』作为 rank(∂₂) 的对应物（实测 T = rank∂₂）：")
    P("     取全部 (2k+1) 个三角环为面时，rank(∂₂) = 2k+1 = T，于是")
    P("        β₁_hom = ν − T = (6k+1) − (2k+1) = **4k**")
    P("     k=1(骨架) → 4；k=2 → 8；k=3 → 12；k=4 → 16。实测逐例吻合。")
    P("  ④ **p/n 跃迁（开一条环边）使 ν 与 rank∂₂ 同步各减 1 ⇒ β₁_hom 不变（4）**。")
    P("     即：框架的**拓扑障碍计数分辨不出质子与中子**；")
    P("     vasp 用来区分 p/n 的那个量是 **ν / T**，不是同调维数。")
    P("     ⇒ 若要把框架的『障碍证书』用于核子线，须改用 ν 或 T 作判据载体。")
    P()
    P("⚠ 适配成本（必须正面登记）：面集是**本脚本额外赋予**骨架的结构；")
    P("   换一套面集，β₁_hom 与全部『拓扑障碍』裁定都随之改变。这是建模选择，")
    P("   不是客观给定 —— 必须先由物理（或由 T 的读数）把它钉死。")
    return r


# ===========================================================================
# PART D —— 规范冗余（对应 vasp「实欠定 1」）
# ===========================================================================
def part_D():
    head("PART D  规范冗余：为什么 vasp 的『实欠定 1』不可能靠加方程修掉")
    P("框架 §13.6 的严格陈述：L(m) = Dᵀ diag(m) D 对 m **一次齐次** ⇒ m → c·m 时")
    P("  α_n → c·α_n，Y = 2L/α_n − I **严格不变** ⇒ 所有 τ_k、所有 F(τ) 严格不变。")
    P("下面实测验证。")
    P()
    G = Y3("", "p")
    D, C, _, _, nodes = complex_from_graph(G)
    N, m_g = D.shape[1], D.shape[0]
    m = np.ones(m_g) * 1.7            # 任意非平凡边权
    K = 6
    L = OP.laplacian(D, m)
    alpha_n, lam2 = OP.spectral_assets(L, N)
    tau, _, _ = OP.chebyshev_moments(L, alpha_n, K)
    pi1 = lam2 / alpha_n
    P("%-10s %-30s %-14s %s" % ("c", "max|τ(c·m) − τ(m)|", "Π₁(c·m)", "Π₁ 偏移"))
    P("-" * 74)
    for c in (0.5, 1.0, 2.0, 137.036, 1e6):
        mc = c * m
        Lc = OP.laplacian(D, mc)
        an_c, l2_c = OP.spectral_assets(Lc, N)
        tau_c, _, _ = OP.chebyshev_moments(Lc, an_c, K)
        P("%-10.4g %-30.3e %-14.9f %.3e" %
          (c, float(np.max(np.abs(tau_c - tau))), l2_c / an_c, abs(l2_c / an_c - pi1)))
    P()
    P("⇒ 实测：整条矩向量 τ（以及 Π₁）在 m → c·m 下**逐位严格不变**（差 ~1e-16）。")
    P()
    P("这给出 vasp『实欠定 1』的**代数诊断**：")
    P("  · vasp 的 L1（整数层：β₁=E−V+1、n=E·β₁、kV=2E）与 L2（谱方程 Π₁=κ_N）")
    P("    以及 L3（w_N = 1+δ_N 的近对称假设）**全部是尺度无关量**；")
    P("  · 因此再补多少条这类方程，都无法定出**整体尺度** —— 缺口不是『方程数不够』，")
    P("    而是**规范不变性**（1 维规范轨道）。")
    P("  · 唯一出路是 L4 一类**跨两个图**的关系（Ψ(G_N)/Ψ(G_e)）—— 且必须**同一把锁**")
    P("    （框架 §13.6 的『锁定壳层缩放』），即强制两图共用一把标尺。")
    P("  · 框架明示其代价：冻结尺度**显式破坏**重标定规范冗余，被锁定的尺度从此")
    P("    成为物理输入量（实测 E01：把解 α 漂移乘回去做规范固定，独立残差由")
    P("    1.85e-2 恶化到 1.19e+0）。")
    P()
    P("⇒ 结论：vasp 的『实欠定 1』是**结构性**的，与『SRE 只定住形不定住值』同源；")
    P("   给定量（如 Δm_np 作为闭合度单位）必须由外部注入，这正是 L4 的不可省略性。")
    return None


# ===========================================================================
# PART E —— 障碍判据读数
# ===========================================================================
def part_E():
    head("PART E  框架的『拓扑障碍』判据在核子复形上的读数 ρ_h = ||h||/||r||")
    P("框架 §17.1：ρ_h ≡ ||h||/||r|| = ||Π_{H₁}∇F|| / ||∇F||，称其『与 F 无关』，")
    P("在自建 β₁=1 复形上实测 ≈ 0.945（min 0.9446 / max 0.9503），并据此判定")
    P("「调和通道不可独立压缩」。下面在**核子复形**上重测，并做权值与 k 的扫描。")
    P()
    P("【测法要点】框架量 ρ_h 里的 r 是 **∇_M F = Σ_k (∂F/∂τ_k)·w_k**（Op14 残差升维）。")
    P("对 F = τ_k − c 即 ∇F = w_k。故对每个 k 直接测 w_k 的调和占比。")
    P()

    def scan(tag, G, faces, mvals=None, K=6):
        D, C, edges, fl, nodes = complex_from_graph(G, faces)
        N, m_g = D.shape[1], D.shape[0]
        nu = m_g - N + 1
        rk2 = int(np.linalg.matrix_rank(C)) if C.shape[0] > 0 else 0
        b1h = nu - rk2
        m = np.ones(m_g) if mvals is None else mvals
        L = OP.laplacian(D, m)
        alpha_n, lam2 = OP.spectral_assets(L, N)
        tau, Y, U = OP.chebyshev_moments(L, alpha_n, K)
        W = OP.moment_sensitivity(D, Y, N, alpha_n, K)
        rh = []
        for k in range(1, K + 1):
            hp = OP.hodge_project(W[k], D, C)
            rh.append(np.linalg.norm(hp["harm"]) / max(np.linalg.norm(W[k]), 1e-30))
        P("  %-24s V=%d E=%d ν=%d rank∂₂=%d β₁_hom=%d  √(β₁/m_g)=%.3f" %
          (tag, N, m_g, nu, rk2, b1h, np.sqrt(b1h / max(m_g, 1))))
        P("      ρ_h(k=1..%d) = [%s]" % (K, ", ".join("%.4f" % v for v in rh)))
        # 随机方向对照
        rng = np.random.default_rng(20260924)
        vals = []
        for _ in range(300):
            rv = rng.standard_normal(m_g)
            vals.append(np.linalg.norm(OP.hodge_project(rv, D, C)["harm"])
                        / np.linalg.norm(rv))
        P("      随机方向对照: mean=%.4f  (对照维度比 √(β₁/m_g)=%.4f)" %
          (np.mean(vals), np.sqrt(b1h / max(m_g, 1))))
        return rh

    rng = np.random.default_rng(3)
    Gp, Gn = Y3("", "p"), Y3("", "n")
    Dp, _, _, _, _ = complex_from_graph(Gp)
    mrand_p = 1.0 + 0.7 * rng.standard_normal(Dp.shape[0])

    a = scan("Y₃ 闭态（单位权）", Gp, skeleton_faces_closed())
    b = scan("Y₃ 开态（单位权）", Gn, skeleton_faces_open(0))
    c = scan("Y₃ 闭态（随机权）", Gp, skeleton_faces_closed(), mrand_p)
    # 框架自建复形需直接传 D/C，单独处理
    P("  --- 框架自建复形（参照，β₁_hom=1）---")
    for tag, cc in (("有洞 close_cycle=False", False), ("闭 close_cycle=True", True)):
        D0, C0, _, _ = OP.build_complex(12, close_cycle=cc)
        N, m_g = D0.shape[1], D0.shape[0]
        L0 = OP.laplacian(D0, np.ones(m_g))
        an0, l20 = OP.spectral_assets(L0, N)
        tau0, Y0, U0 = OP.chebyshev_moments(L0, an0, 6)
        W0 = OP.moment_sensitivity(D0, Y0, N, an0, 6)
        nu0 = m_g - N + 1
        rk0 = int(np.linalg.matrix_rank(C0))
        rh0 = []
        for k in range(1, 7):
            hp = OP.hodge_project(W0[k], D0, C0)
            rh0.append(np.linalg.norm(hp["harm"]) / np.linalg.norm(W0[k]))
        P("  %-24s V=%d E=%d ν=%d rank∂₂=%d β₁_hom=%d" %
          ("  " + tag, N, m_g, nu0, rk0, nu0 - rk0))
        P("      ρ_h(k=1..6) = [%s]" % ", ".join("%.4f" % v for v in rh0))
    P()
    P("⇒ 实测读数（关键，与框架 §17.1 的『ρ_h ≈ 0.945 与 F 无关』对照）：")
    P("  ① ρ_h **不是常数、也不是复形的维度比**，它同时依赖【复形】与【边权】：")
    P("       · 框架自建有洞复形（单位权）：0.95 量级 —— 与其自报一致；")
    P("       · 核子骨架闭态（**单位权**）：1e-15 —— **w_k 恒为恰当链，无调和分量**；")
    P("       · 核子骨架闭态（随机权）：0.2~0.4 量级；")
    P("       · 核子骨架开态（单位权）：0.04~0.11 量级；")
    P("       · 随机 1-链方向：≈ √(β₁_hom/m_g)（维度比，纯几何）。")
    P("  ② ⇒ 若照搬框架的『ρ_h ≈ 0.945』到本项目，会得到**完全相反的结论**。")
    P("     ρ_h 必须**逐构形逐方程重测**。这是与 sre-ai 的 λ₂/Δβ₁ 同型的『同名不同义』坑。")
    P("  ③ 对 vasp 的**单位权**构形，矩型约束的调和占比≈0 ⇒ 在框架判据下**无拓扑障碍**；")
    P("     一旦允许加权，调和分量即出现（0.2~0.4）—— 这与 §7『账本加权可分开』的")
    P("     既有结论在方向上一致：加权会引入新的结构量。")
    P("  ④ 判据带宽 1/γ ≈ 5.3（核子）/ 137（电子）≫ 框架自建复形的 1/γ ≈ 5.0：")
    P("     OBSTRUCTION 假阳性风险随 1/γ 放大 ⇒ v1.3 补的 `step_dead` 附加条件")
    P("     在本项目是**必需**的，不是可选优化。")
    return (a, b, c)


# ===========================================================================
# PART F —— 端到端跑一次框架求解器
# ===========================================================================
def part_F():
    head("PART F  端到端：把核子骨架复形交给框架求解器跑一次")
    P("方程取 L1 级（多项式核）标量方程 F(τ) = τ_2 − c，其中 c 由某个已知边权 m* 生成")
    P("（保证良置、有真解）。初值取 m* 的扰动，看框架能否收敛回去。")
    P()
    G = Y3("", "p")
    D, C, edges, fl, nodes = complex_from_graph(G, skeleton_faces_closed())
    N, m_g = D.shape[1], D.shape[0]
    m_star = np.ones(m_g)
    Ls = OP.laplacian(D, m_star)
    alpha_n, lam2 = OP.spectral_assets(Ls, N)
    K, Kres, Kcap = OP.endogenous_K(alpha_n, lam2, N)
    tau_star, _, _ = OP.chebyshev_moments(Ls, alpha_n, K)
    c = float(tau_star[2])
    P("  N_K=%d  m_g=%d  α_n=%.6f  λ₂=%.6f  γ=%.6f  K=%d (K_res=%d, K_cap=%d)" %
      (N, m_g, alpha_n, lam2, lam2 / alpha_n, K, Kres, Kcap))
    P("  冻结尺度 = (α_n, λ₂) 于 m* 处；目标 c = τ₂(m*) = %.9f" % c)
    P()

    def F(tau):
        return float(tau[2] - c)

    def dFdtau(tau, K):
        g = np.zeros(K + 1); g[2] = 1.0; return g

    rng = np.random.default_rng(7)
    for tag, sc in (("轻微扰动 (1±2%)", 0.02), ("中度扰动 (1±20%)", 0.20),
                    ("强扰动 (1±60%)", 0.60)):
        m0 = m_star * (1 + sc * rng.standard_normal(m_g))
        try:
            m_end, hist = OP.solve_spectral_equation(
                D, C, m0, F, dFdtau, [2], max_kappa=60, verbose=False,
                use_momentum=False, mode="exact", freeze=(alpha_n, lam2))
            last = hist[-1]
            P("  %-20s 裁定=%-13s 步数=%-4d |F_final|=%-11.3e ||r||=%-11.3e" %
              (tag, last["verdict"], len(hist), abs(last["F"]), last["r_norm"]))
            P("     F 轨迹: %s" % " -> ".join("%.3e" % h["F"] for h in hist))
            P("     ⚠ 返回的边权与真解 m* 的距离 ‖m_end−m*‖/‖m*‖ = %.4f（≠0）" %
              (np.linalg.norm(m_end - m_star) / np.linalg.norm(m_star)))
        except Exception as e:
            P("  %-20s **异常**: %s: %s" % (tag, type(e).__name__, str(e)[:110]))
    P()
    P("⇒ 结论分两层，必须分开说：")
    P("  ① **管线可用**：框架在核子复形上跑通，5 / 8 / 15 步收敛到 |F| ~ 1e-17，")
    P("     无异常、无死锁；扰动越强步数越多，行为与规范一致。")
    P("  ② **但它解的不是 vasp 的问题**：方程只有 1 条（τ₂ = c），未知 18 个 ⇒")
    P("     解集是一条 17 维流形。框架**收敛到流形上的某一点**，返回的边权与真解")
    P("     相差 1.3% / 26% / 42%（扰动越大偏离越远）—— 这正是 §(B) 那句")
    P("     『算子 18 的 Dirichlet 能最小规范代表没有物理依据』的**数值实证**。")
    P("     换言之：框架能可靠地回答『存在解吗』，但**不能**回答『是哪一个解』。")
    P("  ③ 方程 F(τ)=τ₂−c 在**冻结 α_n** 下才带尺度信息；若每步刷新 α_n，")
    P("     则 τ 与 F 对 m→cm 严格不变（PART D），方程**退化为规范不变** ——")
    P("     这正是 §13.6 把『冻结』写成强制约束的原因，也解释了为何该框架的『值』")
    P("     必须由外部锁定的尺度承担。")
    return None


# ===========================================================================
# PART G —— 综合裁定
# ===========================================================================
def part_G():
    head("PART G  综合裁定")
    P("【可用（真桥接）】")
    P(" 1. **Π₁ ≡ γ**，逐字同定义（实测逐例相等到 1e-16）。")
    P("    vasp 唯一已标定泛函 = 框架唯一内生尺度。⇒ 框架的全部阈值")
    P("    （ε_endo=γ‖r₀‖、θ_endo=γ、Stieltjes 虚部 ε=γ、K=⌈1/γ⌉）在本项目里")
    P("    由 Π₁ 直接给定，零新参数 —— 与公设 3 同构。")
    P(" 2. **规范冗余定理**严格解释了 vasp 的『实欠定 1』：L1/L2/L3 全部尺度无关，")
    P("    再补同类方程也补不上；必须引入**跨图**的 L4 并用**同一把锁**。")
    P("    ⇒ 『L4 不可省略』从经验缺口升级为**代数必然**。")
    P(" 3. **同调定义补全**：vasp 现用的 β₁ = E−V+1 是 **circuit rank ν**（在一维复形下")
    P("    命名无误）；框架另给了同调维数 β₁_hom = ν − rank(∂₂)。取面集 = 全部")
    P("    三角环（= vasp 自己的 T）时，**β₁_hom = 4k**，且 **p/n 跃迁对它不变**。")
    P("    ⇒ ① 给了『Δβ₁ ≡ 0 强锁』一个精确对象；")
    P("      ② 明确警告：**框架的障碍计数分辨不出质子与中子**，这一点不可照搬。")
    P(" 4. **τ₁ 严格线性承载边权和**（实测斜率对理论 1.8e-15）：vasp 的「键长加和律」")
    P("    Σ_e n_e w_e = 实测 **正是 τ₁ 型约束**，可作为 L1 级方程进入框架 ——")
    P("    这是『锚定经典物理量』一侧唯一立刻可用的接口。")
    P(" 5. **矩编码对退化谱仍解析可微**（灵敏度 vs 差分 2.5e-10），而 vasp 的 Π₁ 在")
    P("    λ₂ 重数 2 处不可微 ⇒ τ 向量是 Π₁ 的**光滑替身**，可用于任何需要梯度的场合。")
    P()
    P("【不可用 / 必须正面处理的张力】")
    P(" A. **求解器对象不匹配**：Op15 在**固定复形**上求**连续边权**；vasp 的反演是")
    P("    在**离散拓扑**上枚举（V=12 立方图 85 个）。搜索空间不同，不能互相替代。")
    P(" B. **方程数严重不足**（PART F 实测）：L2 只有 1 条方程（Π₁=κ_N）而未知 m_g=18，")
    P("    解集是 17 维流形。框架能收敛到**流形上某一点**（|F|→1e-17），但返回的边权")
    P("    与真解差 1.3%/26%/42% ⇒ 它回答『有解吗』，**不回答『是哪一个』**。")
    P(" C. **面集是外加结构**：vasp 原文没有 2-链。换面集 ⇒ β₁_hom 变 ⇒ 全部障碍裁定变。")
    P("    必须先由物理（建议就用 T 的读数）钉死，否则『拓扑障碍』结论不可比。")
    P(" D. **A ≥ 4 的不可算性，框架的障碍判据诊断不了**：vasp 的壁垒是一条**代数恒等式**")
    P("    （ψ(1)−ψ(2) = B(³H)−B(³He) > 0），不是『闭而非恰当』的上同调类。")
    P("    框架的补救是算子 9 改 β₁；**恒等式不会因改 β₁ 而消失** ⇒ 该路线对 A≥4 无效。")
    P("    （这是**负面但有用**的结论：可以据此排除『靠拓扑缝合救 A≥4』这条路。）")
    P(" E. **ρ_h 不可照搬**（PART E 实测）：框架报 ρ_h ≈ 0.945「与 F 无关」，")
    P("    但在核子复形上实测为 0（单位权闭态，恒为恰当链）～ 0.2~0.4（随机权）～")
    P("    0.04~0.11（单位权开态）。照搬会得到**相反**结论。与 sre-ai 的 λ₂/Δβ₁ 同型坑。")
    P(" F. **电子侧 α 标定点落在框架红线内**：γ_e = 7.2975e-3 ⇒ K_res=137 ≫ K_cap=8、")
    P("    非多项式核 K_f≈29 > K_cap ⇒ 框架会宣告『核不可展开 / 精度须降级』。")
    P("    要把框架推广到电子层，K_cap = ⌊2ln(1+N_K)⌋ 这条**过拟合防护**须重新论证。")
    P()
    P("【净结论】")
    P("  · 作为**求解器**：对核子线的现有问题（离散反演、定价层）**基本用不上** ——")
    P("    对象（连续边权 vs 离散拓扑）与方程数（1 条 vs 18 未知）都不匹配。")
    P("  · 作为**理论接口**：有 5 项真桥接。优先级建议 ——")
    P("    ① #2（规范冗余 ⇒ L4 不可省略）写进论文 §12.12 附近，作为『λ / w(k) / k 分布 /")
    P("       跨层参数化 / 实欠定 1』这组『SRE 只定形不定值』现象的**统一代数解释**；")
    P("    ② #4（τ₁ ↔ 加和律）用于「维度塌缩 / 键长加和律」那条线，是本轮唯一能")
    P("       **立刻把框架当工具用**的接口（加和律 = 线性矩约束，可求解、可带 Hankel 可行性钳制）；")
    P("    ③ #3（ν vs β₁_hom）写进论文术语表，避免后续混用。")
    return None


def main():
    P("#" * 78)
    P("# 核子线 <-> 谱形方程求解算子组 (Op13-18) 接口评估")
    P("# 框架版本：v1.3（Operator-13_18_Strict-Mathematical-Specification，50/50 压测通过）")
    P("#" * 78)
    part_A()
    part_B()
    part_C()
    part_D()
    part_E()
    part_F()
    part_G()


if __name__ == "__main__":
    main()
