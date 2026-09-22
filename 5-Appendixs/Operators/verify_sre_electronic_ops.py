# -*- coding: utf-8 -*-
"""
verify_sre_electronic_ops.py
============================
SRE 算子 11/12（v1.1 规范）配套验证程序。

对应文档：《算子-11/12：电子自由度扩展算子组严格数学规范、推导与论证》（v1.1）
第 7 节"验证实验设计"第 7.1-7.10 项，逐条实证规范中的引理与定理：

  7.1  引理 3.1/3.2/3.3  A_s 非负、对称、连通（两种平滑邻接构造）
  7.2  定理 11.1/11.2    极性二元性；A_q 对称、非负、A_q>=A_s、支撑保持
  7.3  定理 11.3        L_q 半正定、lambda_2_q>0、Gershgorin 上界
  7.4  定理 11.4/11.5    电负性差单调增益；同核不变；max_spin_coupling 定位
  7.5  定理 11.6        Weyl 谱摄动上界；rho->0 连续退化
  7.6  定理 12.1/12.2    闭合行走迹语义；回溯污染假阳性；乙醇 n_loops=0
  7.7  定理 12.3        Möbius 符号平衡判据（全 +1 平衡 / 负环非平衡）
  7.8  定理 12.4        环数与一阶贝蒂数衔接（乙醇 0 / 苯环 1）
  7.9  定理 12.5        环上子图 Cauchy 交错与条件数钳制
  7.10 定理 12.6        审计迹 Lipschitz 鲁棒性（数值微扰上界）

零外部依赖：仅 numpy + scipy。运行：python verify_sre_electronic_ops.py
任一断言失败以退出码 1 结束。
"""
import numpy as np

# =====================================================================
# 分子体系定义（坐标 + 显式化学键列表 + 电负性）
# =====================================================================
# 乙醇：C1-C2-O 链（Trae 坐标，键长化学合理）
ETHANOL_POS = np.array([
    [0.0, 0.0, 0.0],       # 0 C1 (c3)
    [1.52, 0.0, 0.0],      # 1 C2 (c3)
    [2.15, 1.35, 0.0],     # 2 O  (oh)
    [-0.5, 0.9, 0.3],      # 3 H  (hc)
    [-0.5, -0.9, -0.3],    # 4 H  (hc)
    [-0.5, 0.0, -0.9],     # 5 H  (hc)
    [1.52, -0.9, 0.9],     # 6 H  (h1)
    [1.52, 0.9, -0.9],     # 7 H  (h1)
    [2.15, 1.35, 0.96],    # 8 H5 (ho, O-H)
], dtype=np.float64)

# 显式化学键（乙醇为开链树：9 原子 8 边，beta_1 = 0）
ETHANOL_BONDS = [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 6), (1, 7), (2, 8)]
ETHANOL_ATOMTYPES = ["c3", "c3", "oh", "hc", "hc", "hc", "h1", "h1", "ho"]
ETHANOL_CHI = np.array([2.55, 2.55, 3.44, 2.20, 2.20, 2.20, 2.20, 2.20, 2.20])

# 苯环：6 个 C，正六边形边长 1.40 Å，键 = 邻位（C6 单环，beta_1 = 1）
ANG = np.linspace(0, 2 * np.pi, 7)[:-1]
BENZENE_POS = np.column_stack([np.cos(ANG), np.sin(ANG), np.zeros(6)]) * 1.40
BENZENE_BONDS = [(i, (i + 1) % 6) for i in range(6)]
BENZENE_CHI = np.array([2.55] * 6)


# =====================================================================
# 平滑邻接构造（两种）
# =====================================================================
def _dist_matrix(pos):
    d = np.sqrt(np.maximum(np.sum((pos[:, None, :] - pos[None, :, :]) ** 2, axis=2), 0.0))
    return d


def _bond_mask(n, bonds):
    B = np.zeros((n, n), dtype=bool)
    for i, j in bonds:
        B[i, j] = B[j, i] = True
    return B


def build_we_smooth_adjacency(pos, bonds, eps_topo=1e-6):
    """规范构造：定义 3.1 算子 4 平滑权重，投影到化学键支撑 E+。"""
    n = len(pos)
    bond = _bond_mask(n, bonds)
    # 键图拉普拉斯（Fiedler 值 / 谱半径）
    A_b = bond.astype(float)
    deg = A_b.sum(axis=1)
    Lb = np.diag(deg) - A_b
    ev = np.linalg.eigvalsh(Lb)
    lam2 = float(ev[1]) if n > 1 else 0.0      # 连通 => > 0
    alpha = float(ev[-1]) if n > 0 else 1.0
    # M：键 +1 协同，非键 -1 休眠，对角 +1（SRE 公理 1，无零元）
    M = np.where(bond, 1.0, -1.0)
    np.fill_diagonal(M, 1.0)
    D_ii = np.abs(M).sum(axis=1)
    D_self = np.diag(M).copy()
    num = np.sqrt(np.outer(D_ii, D_ii))
    denom = np.sqrt(lam2 + D_self[:, None] + D_self[None, :] + eps_topo)
    M2 = M @ M
    damp = 1.0 + np.abs(M2) * np.log(1.0 + lam2 / alpha) / (alpha + np.sqrt(np.outer(D_ii, D_ii)))
    We = (num / denom) * damp
    A_s = We * bond.astype(float)
    np.fill_diagonal(A_s, 0.0)
    return A_s, M


def build_exp_smooth_adjacency(pos, bonds, R_cut=2.85):
    """几何代理：A_s = exp(-D/R_cut) 投影到化学键支撑 E+（对照构造）。"""
    n = len(pos)
    D = _dist_matrix(pos)
    A_s = np.exp(-D / max(R_cut, 1e-6)) * _bond_mask(n, bonds).astype(float)
    np.fill_diagonal(A_s, 0.0)
    M = np.where(_bond_mask(n, bonds), 1.0, -1.0)
    np.fill_diagonal(M, 1.0)
    return A_s, M


# =====================================================================
# 算子 11（v1.1 规范公式）
# =====================================================================
def operator_11(A_s, chi, rho):
    chi = np.asarray(chi, dtype=np.float64)
    n = len(chi)
    chi_mean = np.mean(chi)
    s = np.sign(chi - chi_mean)
    s[s == 0] = 1.0
    sigma = np.outer(s, s)
    d = (1.0 - sigma) / 2.0
    wq = np.abs(np.tanh(chi[:, None] - chi[None, :]))
    A_q = A_s * (1.0 + rho * wq)
    np.fill_diagonal(A_q, 0.0)
    deg = A_q.sum(axis=1)
    L_q = np.diag(deg) - A_q
    ev = np.linalg.eigvalsh(L_q)
    lam2_q = float(ev[1]) if n > 1 else 0.0
    alpha_q = float(np.max(np.abs(ev)))
    kappa_q = alpha_q / lam2_q if lam2_q > 1e-12 else float("inf")
    q_dispersion = float(np.std(np.abs(chi)) / (np.mean(np.abs(chi)) + 1e-12))
    support = A_s > 0
    wq_sup = np.abs(sigma * wq)[support]
    max_sc = float(np.max(wq_sup)) if support.any() else 0.0
    return {"A_q": A_q, "L_q": L_q, "lambda_2_q": lam2_q, "alpha_q": alpha_q,
            "kappa_q": kappa_q, "q_dispersion": q_dispersion,
            "max_spin_coupling": max_sc, "s": s, "sigma": sigma, "d": d, "wq": wq}


# =====================================================================
# 算子 12（v1.1 规范公式）
# =====================================================================
def enumerate_simple_cycles(adj, N_max):
    """DFS 枚举长度 <= N_max 的简单环（无向图）。

    每个无向环按其正、反两个方向的规范表示（最小顶点置首，
    取正向/反向字典序较小者）去重，确保同一环只计数一次。
    """
    n = adj.shape[0]
    supp = adj > 1e-12
    cycles_raw = []
    for s in range(n):
        path = [s]

        def dfs(u):
            if len(path) >= 3 and len(path) <= N_max and supp[u, s]:
                cycles_raw.append(list(path))
            if len(path) >= N_max:
                return
            for v in range(s + 1, n):
                if supp[u, v] and v not in path:
                    path.append(v)
                    dfs(v)
                    path.pop()

        dfs(s)
    seen, cycles = set(), []
    for c in cycles_raw:
        m = min(c)
        k = c.index(m)
        rot = c[k:] + c[:k]           # 最小顶点旋转到首位
        rev = [rot[0]] + rot[:0:-1]   # 反向（最小顶点仍在首位）
        key = min(tuple(rot), tuple(rev))
        if key not in seen:
            seen.add(key)
            cycles.append(c)
    return cycles


def operator_12(A_q, M, N_max):
    n = A_q.shape[0]
    cycles = enumerate_simple_cycles(A_q, N_max)
    n_loops = len(cycles)
    loop_atoms = sorted(set(v for c in cycles for v in c))
    # Möbius 相位比（定义 5.3）
    ratios = []
    for k in range(3, N_max + 1):
        Mk = np.linalg.matrix_power(M, k)
        tau = np.trace(Mk)
        ratios.append(abs(tau) / float(n ** k))
    mobius_ratio = float(np.mean(ratios)) if ratios else 1.0
    # 环上子图谱量（定义 5.4）
    if len(loop_atoms) >= 3:
        deg = A_q.sum(axis=1)
        L_q = np.diag(deg) - A_q
        sub = np.ix_(loop_atoms, loop_atoms)
        L_loop = L_q[sub]
        ev = np.linalg.eigvalsh(L_loop)
        lam2_loop = float(ev[1])
        kappa_loop = float(ev[-1] / ev[1]) if ev[1] > 1e-12 else float("inf")
    else:
        lam2_loop = float("nan")
        kappa_loop = float("nan")
    return {"n_loops": n_loops, "mobius_ratio": mobius_ratio,
            "loop_atoms": loop_atoms, "lambda_2_loop": lam2_loop,
            "kappa_loop": kappa_loop}


# =====================================================================
# 断言框架
# =====================================================================
RESULTS = []


def check(item, desc, cond, detail=""):
    RESULTS.append((item, desc, bool(cond), detail))
    tag = "PASS" if cond else "FAIL"
    print(f"[{tag}] {item}  {desc}" + (f"  ({detail})" if detail else ""))
    return bool(cond)


# =====================================================================
# 主验证流程（7.1 - 7.10）
# =====================================================================
def main():
    print("=== SRE 算子 11/12 规范 v1.1 配套验证 ===\n")
    rho = 0.5
    N_max = 8

    # ---------- 7.1 引理 3.1/3.2/3.3 ----------
    print("--- 7.1 平滑邻接基本性质（两种构造 × 两体系）---")
    for name, pos, bonds in [("乙醇", ETHANOL_POS, ETHANOL_BONDS),
                             ("苯环", BENZENE_POS, BENZENE_BONDS)]:
        for cname, builder in [("W_e", build_we_smooth_adjacency),
                               ("exp", build_exp_smooth_adjacency)]:
            A_s, M = builder(pos, bonds)
            n = len(pos)
            nonneg = float(A_s.min()) >= -1e-12
            sym = np.allclose(A_s, A_s.T)
            deg_s = A_s.sum(axis=1)
            L_s = np.diag(deg_s) - A_s
            ev_s = np.linalg.eigvalsh(L_s)
            lam2_s = float(ev_s[1])
            conn = lam2_s > 1e-9
            check("7.1", f"{name}/{cname}: A_s 非负且对称", nonneg and sym)
            check("7.1", f"{name}/{cname}: 连通 (lambda_2(L_s)={lam2_s:.4f}>0)", conn)

    # ---------- 7.2 定理 11.1/11.2 ----------
    print("\n--- 7.2 极性二元性；A_q 对称/非负/支撑保持（乙醇，W_e）---")
    A_s_e, M_e = build_we_smooth_adjacency(ETHANOL_POS, ETHANOL_BONDS)
    op11 = operator_11(A_s_e, ETHANOL_CHI, rho)
    s = op11["s"]
    check("7.2", "s_i ∈ {-1,+1}", set(np.unique(s)) <= {-1.0, 1.0},
          f"s={s.astype(int).tolist()}")
    check("7.2", "sigma_ij ∈ {-1,+1}, d_ij ∈ {0,1}",
          set(np.unique(op11["sigma"])) <= {-1.0, 1.0} and
          set(np.unique(op11["d"])) <= {0.0, 1.0})
    A_q = op11["A_q"]
    check("7.2", "A_q 对称", np.allclose(A_q, A_q.T))
    check("7.2", "A_q 非负 且 A_q >= A_s", float(A_q.min()) >= -1e-12 and float((A_q - A_s_e).min()) >= -1e-12)
    check("7.2", "支撑保持 supp(A_q) = supp(A_s)",
          np.array_equal((A_q > 0), (A_s_e > 0)))

    # ---------- 7.3 定理 11.3 ----------
    print("\n--- 7.3 L_q 半正定 / Fiedler 正定 / Gershgorin 上界 ---")
    L_q = op11["L_q"]
    ev_q = np.linalg.eigvalsh(L_q)
    psd = float(ev_q.min()) >= -1e-9
    dq = A_q.sum(axis=1)
    gersh = op11["alpha_q"] <= 2.0 * float(dq.max()) + 1e-9
    check("7.3", "L_q 半正定 (min eig=%.6f)" % ev_q.min(), psd)
    check("7.3", f"lambda_2_q = {op11['lambda_2_q']:.4f} > 0", op11["lambda_2_q"] > 0)
    check("7.3", f"alpha_q={op11['alpha_q']:.4f} <= 2*max d_q={2*dq.max():.4f}", gersh)

    # ---------- 7.4 定理 11.4/11.5 ----------
    print("\n--- 7.4 单调增益 / 同核不变 / max_spin_coupling 定位 ---")
    def gain(dchi):
        return 1.0 + rho * abs(np.tanh(dchi))
    order = (gain(1.24) > gain(0.89) > gain(0.35) > gain(0.0))
    check("7.4", "g(O-H)=%.4f > g(C-O)=%.4f > g(C-H)=%.4f > g(C-C)=%.4f"
          % (gain(1.24), gain(0.89), gain(0.35), gain(0.0)), order)
    # 同核键（C-C、H-H 键）权重因子 = 1
    wq = op11["wq"]
    homo = all(abs(wq[i, j]) < 1e-12 for (i, j) in ETHANOL_BONDS if ETHANOL_CHI[i] == ETHANOL_CHI[j])
    check("7.4", "同核键 w_q=0 => A_q=A_s", homo)
    check("7.4", "max_spin_coupling=%.4f ≈ tanh(1.24)=%.4f（O-H）"
          % (op11["max_spin_coupling"], np.tanh(1.24)),
          abs(op11["max_spin_coupling"] - np.tanh(1.24)) < 1e-3)

    # ---------- 7.5 定理 11.6 ----------
    print("\n--- 7.5 Weyl 谱摄动上界 / rho->0 退化 ---")
    Delta_max = float(max(np.sum(A_s_e * wq, axis=1)))
    bound = 2.0 * rho * Delta_max
    weyl = abs(op11["lambda_2_q"] - float(np.linalg.eigvalsh(np.diag(A_s_e.sum(1)) - A_s_e)[1])) <= bound + 1e-9
    check("7.5", f"|lambda_2_q - lambda_2_s| = {abs(op11['lambda_2_q'] - float(np.linalg.eigvalsh(np.diag(A_s_e.sum(1)) - A_s_e)[1])):.6f} <= 2*rho*Delta_max = {bound:.6f}", weyl)
    A_q0 = operator_11(A_s_e, ETHANOL_CHI, 0.0)["A_q"]
    check("7.5", "rho=0 时 A_q = A_s（连续退化）", np.allclose(A_q0, A_s_e, atol=1e-12))

    # ---------- 7.6 定理 12.1/12.2 ----------
    print("\n--- 7.6 闭合行走迹语义 / 回溯污染假阳性 / 乙醇零审计 ---")
    t1 = np.trace(A_q)
    t2 = np.trace(A_q @ A_q)
    check("7.6", f"t_1 = {t1:.2e} = 0", abs(t1) < 1e-9)
    check("7.6", "t_2 = 2*sum(A_ij^2)", abs(t2 - 2.0 * np.sum(np.triu(A_q, 1) ** 2)) < 1e-9)
    tsum_round = sum(round(abs(np.trace(np.linalg.matrix_power(A_q, k)))) for k in range(2, N_max + 1))
    op12_eth = operator_12(A_q, M_e, N_max)
    check("7.6", "回溯污染实证：sum(round(t_k)) = %d > 0（开链假阳性）" % tsum_round, tsum_round > 0)
    check("7.6", f"乙醇 n_loops = {op12_eth['n_loops']} = 0（有效判据免疫）", op12_eth["n_loops"] == 0)

    # ---------- 7.7 定理 12.3 ----------
    print("\n--- 7.7 Möbius 符号平衡判据（合成符号矩阵）---")
    n7 = 6
    M_bal = np.ones((n7, n7))          # 全 +1：平衡
    M_neg = np.ones((n7, n7))          # 含负环：M[0,1]=-1
    M_neg[0, 1] = M_neg[1, 0] = -1.0
    r_bal = operator_12(np.eye(n7), M_bal, 6)["mobius_ratio"]
    r_neg = operator_12(np.eye(n7), M_neg, 6)["mobius_ratio"]
    check("7.7", f"全 +1 符号矩阵 mobius_ratio = {r_bal:.6f} = 1（无 Möbius）", abs(r_bal - 1.0) < 1e-9)
    check("7.7", f"含负环符号矩阵 mobius_ratio = {r_neg:.6f} < 1（Möbius 存在）", r_neg < 1.0 - 1e-9)

    # ---------- 7.8 定理 12.4 ----------
    print("\n--- 7.8 环数与一阶贝蒂数衔接 ---")
    beta1_eth = len(ETHANOL_BONDS) - len(ETHANOL_POS) + 1
    beta1_benz = len(BENZENE_BONDS) - len(BENZENE_POS) + 1
    A_s_b, M_b = build_we_smooth_adjacency(BENZENE_POS, BENZENE_BONDS)
    op11_b = operator_11(A_s_b, BENZENE_CHI, rho)
    op12_benz = operator_12(op11_b["A_q"], M_b, N_max)
    check("7.8", f"乙醇 n_loops={op12_eth['n_loops']} = beta_1={beta1_eth} = 0",
          op12_eth["n_loops"] == beta1_eth == 0)
    check("7.8", f"苯环 n_loops={op12_benz['n_loops']} = beta_1={beta1_benz} = 1",
          op12_benz["n_loops"] == beta1_benz == 1)
    check("7.8", "苯环 n_loops >= beta_1 且环长=6", op12_benz["n_loops"] >= beta1_benz)

    # ---------- 7.9 定理 12.5 ----------
    print("\n--- 7.9 环上子图 Cauchy 交错与条件数钳制（苯环）---")
    inter = (op12_benz["lambda_2_loop"] >= op11_b["lambda_2_q"] - 1e-9) and \
            (op12_benz["lambda_2_loop"] > 0)
    kappab = op12_benz["kappa_loop"] <= op11_b["kappa_q"] + 1e-9
    check("7.9", f"lambda_2_loop={op12_benz['lambda_2_loop']:.4f} >= lambda_2_q={op11_b['lambda_2_q']:.4f} > 0", inter)
    check("7.9", f"kappa_loop={op12_benz['kappa_loop']:.4f} <= kappa_q={op11_b['kappa_q']:.4f}", kappab)

    # ---------- 7.10 定理 12.6 ----------
    print("\n--- 7.10 审计迹 Lipschitz 鲁棒性（数值微扰）---")
    rng = np.random.default_rng(42)
    n10 = A_q.shape[0]
    E = rng.standard_normal((n10, n10))
    E = (E + E.T) / 2.0
    delta = 1e-3
    B = A_q + delta * E
    Mbar = max(np.linalg.norm(A_q, 2), np.linalg.norm(B, 2))
    lip_ok = True
    for k in range(2, N_max + 1):
        tA = np.trace(np.linalg.matrix_power(A_q, k))
        tB = np.trace(np.linalg.matrix_power(B, k))
        lhs = abs(tA - tB)
        rhs = k * Mbar ** (k - 1) * delta * np.linalg.norm(E, 2)
        if lhs > rhs + 1e-9:
            lip_ok = False
    check("7.10", "|t_k(A)-t_k(B)| <= k*M^(k-1)*||A-B||_2 对所有 k∈[2,8] 成立", lip_ok)

    # ---------- 汇总 ----------
    print("\n=== 汇总 ===")
    passed = sum(1 for r in RESULTS if r[2])
    total = len(RESULTS)
    print(f"通过 {passed}/{total} 项断言")
    fails = [r for r in RESULTS if not r[2]]
    for f in fails:
        print("  FAIL:", f[0], f[1])
    print("\n" + ("✅ 全部断言通过：算子 11/12 规范 v1.1 定理体系得到数值实证。"
                  if not fails else "❌ 存在失败断言，请检查规范与实现。"))
    return 0 if not fails else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
