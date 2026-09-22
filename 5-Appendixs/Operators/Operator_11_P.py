"""
SRE Electronic Degrees-of-Freedom Extension — Pure Graph Computation (v1.1)
============================================================================

Operator 11 (Spin-Charge Adjacency): 在 SRE 平滑邻接矩阵 A_s 上叠加电负性差
强度 |tanh(chi_i - chi_j)|，将电子自由度编码为图的边权重增益。

Operator 12 (Topological Closed-Loop Audit): 通过简单环枚举 + SRE 符号矩阵
相位审计，检测 "N 尺度拓扑闭合环 + Möbius 双层相位" 模式。

依赖：仅 numpy（内置 Pauling 电负性表 + 共价半径表）。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v1.1 相对 Trae 原版（sre_electronic_ops.py）的修正（对应《算子-11/12
严格数学规范》v1.1 的 D1-D5）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

D1 自旋耦合符号学矛盾（已修正）:
    原版:  A_q = A_s * (1 + rho * s_i * s_j * |tanh(dchi)|)
          异极性键 (s_i*s_j=-1, 如 O-H) 被衰减 (乙醇 O-H 倍率 0.577)。
    规范:  A_q = A_s * (1 + rho * |tanh(dchi)|)
          异核键一律增益 (乙醇 O-H 1.423, C-O 1.356, C-H 1.168)。

D2 自旋极性均值依赖（已解耦）:
    原版: s_i = sign(chi_i - chi_mean) 直接调制权重方向；乙醇中 O 因高于
          均值被判 +1（给电子），极性方向随分子组成漂移，不可移植。
    规范: 权重调制只用 w_q = |tanh(dchi)|（键内电负性差，与均值无关）；
          s_i / sigma_ij / d_ij 降级为诊断标量，仅用于 max_spin_coupling。

D3 回溯污染 / 谱假阳性（已修正）:
    原版: 用 trace(A^k) 闭合行走 + R(k) 比判环，乙醇(开链)出现
          spectral_resonance=0.0557>0, resonance_length=6 假阳性，
          苯环 loop_lambda_2=NaN。
    规范: n_loops 由简单环枚举（DFS，无回溯、方向去重）直接计数，
          乙醇 = 0，苯环 = 1；mobius_ratio 在 SRE 符号矩阵 M 上以
          |tr(M^k)| / n^k 定义（定理 12.3 符号平衡判据）。

D4 平滑邻接构造（已修正）:
    原版: A_smooth = exp(-D/2.85)，乙醇 72 条非零边全连通，稠密是
          谱假阳性的根源之一。
    规范: A_s = W_e ⊙ P+（定义 3.1 算子 4 平滑权重，投影到化学键支撑
          E+），键由共价半径和 × 1.25 判定；不使用 k-NN，不使用
          全连通距离核。

D5 指纹与条件数（已修正）:
    原版: 指纹返回 9 键（含 closed_loop_strength/spectral_resonance/
          resonance_length），cond_norm_q = cond(A_q+epsI) 与注释公式
          不符。
    规范: 指纹返回 7 键（方案要求）：lambda_2_q, kappa_q, alpha_q,
          n_loops, mobius_ratio, q_dispersion, max_spin_coupling；
          kappa_q = alpha_q / lambda_2_q（定义 4.5）。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
数学推导与物理意义
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╔═══════════════════════════════════════════════════════════════════╗
║  前置：SRE 现有算子链（Operator 1-6, 9-10）                       ║
╚═══════════════════════════════════════════════════════════════════╝

SRE 公理 1（严格二元约束）:
  系统瞬时态由实对称网络配置矩阵 M_n 描述，元素 ∈ {+1, -1}。
  无连续平滑截断，不存在耗散态 0。初始宇宙条件: M_1 = (1)。

SRE 图拉普拉斯（Operator 6, Rayleigh-Ritz 投影）:
  L_G = V_global^T · L_sparse · V_global
  λ₂(n) ≈ λ₂(K_RR)    (代数连通性，Fiedler 值)
  α_n ≈ λ_max(K_RR)   (谱半径)

SRE 边权重 W_e（Operator 4）:
  W_e(i,j) = √(D^out_ii · D^in_jj) / √(λ₂ + D^self_ii + D^self_jj + ε_topo)
             · (1 + |M²_Ω,ij| · ln(1 + λ₂/α_n) / (α_n + √(D^out·D^in)))

SRE 信息传播速率（Operator 5）:
  c_e = min(α_n / (ln(1 + W_e) + δ_flt), c_max)

SRE 态射原理:
  T_morphic: ⟨M_spin, λ₂(n), B_co⟩ ↔ ⟨质量粒子, 引力度量, 内生光速⟩
  其中"量化电荷"(quantised charge)作为粒子涌现属性之一被提及。

SRE 电子拓扑描述:
  电子 = N 尺度 l_min 构成的自洽拓扑闭合环 [A₁,...,A_N]
  - 拓扑闭合: A_N → A₁ 回溯因果，形成自洽闭环
  - Möbius 相位: 需 2N 次互测触发才恢复初始对称态 → 自旋 1/2
  - 电荷: 闭合环每轮互测对因果链施加固定拓扑偏置
  - 质量: 闭环拓扑处理开销 m ∝ N · l_min
  - N ≈ 10²³（Compton 波长 / l_min）

╔═══════════════════════════════════════════════════════════════════╗
║  算子在 SRE 10 算子框架中的位置                                    ║
╚═══════════════════════════════════════════════════════════════════╝

  现有链: Op1 → Op2 → Op3 → Op6 → Op4 → Op5 → Op9 → Op10
                                    ↑
  扩展后: Op1 → Op2 → Op3 → Op6 → Op11 → Op4 → Op12 → Op5 → Op9 → Op10
                                    ↑      ↑      ↑
                                    新输入  改输入  新审计

  - Op 11 在 Op 6 之后、Op 4 之前：Op 11 需要 λ₂, α_n（Op 6 输出）
    来构建 A_q，而 A_q 替代 A_smooth 作为 Op 4 的输入。
  - Op 12 在 Op 4 之后、Op 5 之前：Op 12 审计 A_q（Op 11 输出）
    的闭合环模式，结果用于调制 Op 5 的 c_e（信息传播速率）。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
用法
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 独立演示（坐标 + 原子类型 → A_s(W_e 构造) → M → 算子 11/12）
    A_s  = build_sre_smooth_adjacency(pos, atomtypes=atomtypes)
    M    = sre_sign_matrix(A_s)
    op11 = operator_11_spin_charge_adjacency(A_s, chis, rho=0.5)
    op12 = operator_12_closed_loop_audit(op11["A_q"], M, N_max=8)

    # 流水线接口（A_s 由上游算子 1/4 输出，M 由 A_s 支撑反推）
    fp = compute_electronic_fingerprint(pos, A_s_from_pipeline, chis)

自测: python Operator_11_P.py
"""

import numpy as np

# ─── Pauling Electronegativity Table ──────────────────────────────────
PAULING_ELECTRONEGATIVITY = {
    "H": 2.20,  "He": 0.00,
    "Li": 0.98, "Be": 1.57, "B": 2.04,  "C": 2.55,  "N": 3.04,  "O": 3.44,  "F": 3.98,  "Ne": 0.00,
    "Na": 0.93, "Mg": 1.31, "Al": 1.61, "Si": 1.90, "P": 2.19,  "S": 2.58,  "Cl": 3.16, "Ar": 0.00,
    "K": 0.82,  "Ca": 1.00, "Sc": 1.36, "Ti": 1.54, "V": 1.63,  "Cr": 1.66, "Mn": 1.55,
    "Fe": 1.83, "Co": 1.88, "Ni": 1.91, "Cu": 1.90, "Zn": 1.65, "Ga": 1.81, "Ge": 2.01,
    "As": 2.18, "Se": 2.55, "Br": 2.96, "Kr": 3.00,
    "Rb": 0.82, "Sr": 0.95, "I": 2.66, "Xe": 2.60,
    "Cs": 0.79, "Ba": 0.89,
}

# 共价半径表（Å），用于化学键判定：d < (r_i + r_j) * 1.25
COVALENT_RADIUS = {
    "H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57,
    "Cl": 1.02, "S": 1.05, "P": 1.07, "Br": 1.20, "I": 1.39,
    "Na": 1.66, "Mg": 1.41, "Si": 1.11, "B": 0.84, "Li": 1.28,
    "K": 2.03, "Ca": 1.76, "Fe": 1.32, "Zn": 1.22, "Cu": 1.32,
}
_BOND_FACTOR = 1.25

# GAFF2 atomtype → element mapping
GAFF2_TO_ELEMENT = {
    "c3": "C", "c2": "C", "c1": "C", "ca": "C", "cc": "C", "cd": "C",
    "ce": "C", "cf": "C", "cg": "C", "ch": "C", "ci": "C", "cj": "C",
    "cp": "C", "cq": "C", "cv": "C", "cw": "C", "cx": "C", "cy": "C",
    "cz": "C", "c": "C",
    "n3": "N", "n2": "N", "n1": "N", "na": "N", "nb": "N", "nc": "N",
    "nd": "N", "ne": "N", "nf": "N", "ng": "N", "nh": "N", "ni": "N",
    "nj": "N", "nk": "N", "nl": "N", "nm": "N", "nn": "N", "no": "N",
    "nv": "N", "n": "N",
    "o": "O", "oh": "O", "os": "O", "o2": "O", "op": "O",
    "s": "S", "s2": "S", "sh": "S", "ss": "S", "sx": "S", "sy": "S",
    "s4": "S", "s6": "S",
    "p2": "P", "p3": "P", "p4": "P", "p5": "P", "px": "P", "pb": "P",
    "h1": "H", "h2": "H", "h3": "H", "h4": "H", "h5": "H",
    "hc": "H", "hn": "H", "ho": "H", "hp": "H", "hs": "H", "hw": "H",
    "hx": "H", "hy": "H",
    "f": "F", "cl": "Cl", "br": "Br", "i": "I",
    "mg": "Mg", "ca_ion": "Ca", "zn": "Zn", "fe": "Fe",
    "OW_spc": "O", "HW_spc": "H", "OW": "O", "HW": "H",
    "NA": "Na", "K_ion": "K", "CL": "Cl", "NA_ion": "Na",
}


def gaff2_to_element(atomtype: str) -> str:
    """Map GAFF2/GROMACS atomtype to element symbol."""
    at = str(atomtype).strip()
    if at in GAFF2_TO_ELEMENT:
        return GAFF2_TO_ELEMENT[at]
    first = at[0].upper()
    if first in PAULING_ELECTRONEGATIVITY:
        return first
    return "C"


def get_electronegativity(element: str) -> float:
    """Get Pauling electronegativity for an element."""
    return PAULING_ELECTRONEGATIVITY.get(element, 2.0)


def electronegativities_from_atomtypes(atomtypes: list) -> np.ndarray:
    """Convert GAFF2 atomtype strings to electronegativity values (v1.1)."""
    chis = []
    for at in atomtypes:
        element = gaff2_to_element(at)
        chis.append(get_electronegativity(element))
    return np.array(chis, dtype=np.float64)


def elements_from_atomtypes(atomtypes: list) -> list:
    """Convert GAFF2 atomtype strings to element symbols (v1.1)."""
    return [gaff2_to_element(at) for at in atomtypes]


# ─── 化学键判定（共价半径法；不使用 k-NN）───────────────────────────────

def infer_bonds(positions_xyz: np.ndarray, elements: list = None,
                factor: float = _BOND_FACTOR) -> list:
    """
    由坐标 + 元素符号判定化学键：d_ij < (r_i + r_j) * factor。
    无元素信息时退化为距离阈值 1.85 Å（并打印警告）。

    ⚠️ 启发式局限：仅凭坐标无法消除近距非键接触的歧义（例如
    合成坐标中 O···H 距离 1.19 Å 可能落入 O-H 键判定阈值）。
    生产环境应以拓扑文件（.itp/.prmtop）的键定义或算子 1 输出的
    M 为准；本函数仅在无拓扑信息时作为便利兜底。
    """
    X = np.asarray(positions_xyz, dtype=np.float64)
    n = len(X)
    D2 = np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2)
    D = np.sqrt(np.maximum(D2, 0.0))
    if elements is None:
        print("[warn] infer_bonds: no elements given; using 1.85 A distance cutoff.")
        cutoff = np.full((n, n), 1.85)
    else:
        radii = np.array([COVALENT_RADIUS.get(el, 0.76) for el in elements])
        cutoff = (radii[:, None] + radii[None, :]) * factor
    bonds = []
    for i in range(n):
        for j in range(i + 1, n):
            if D[i, j] < cutoff[i, j]:
                bonds.append((i, j))
    return bonds


# ─── SRE 平滑邻接（定义 3.1 算子 4 平滑权重，投影到化学键支撑 E+）──────

def build_sre_smooth_adjacency(positions_xyz: np.ndarray,
                               atomtypes: list = None,
                               bonds: list = None,
                               eps_topo: float = 1e-6) -> np.ndarray:
    """
    SRE 平滑邻接 A_s（v1.1）。

    A_s = W_e ⊙ P+（定义 3.1 / 3.2）：
      - P+ 为化学键支撑投影（E+ = M 的 +1 协同边，由 infer_bonds 判定）；
      - W_e 为算子 4 平滑权重：√(D_ii D_jj)/√(λ2 + D_self_ii + D_self_jj + ε)
        · (1 + |(M²)_ij|·ln(1 + λ2/α_n)/(α_n + √(D_ii D_jj)))；
      - M 为 SRE 符号矩阵：键 +1、非键 -1、对角 +1（公理 1 无零元）；
      - λ2、α_n 取键图拉普拉斯的 Fiedler 值与谱半径。

    不使用 k-NN；不使用 exp(-D/R_cut) 全连通距离核。
    """
    X = np.asarray(positions_xyz, dtype=np.float64)
    n = len(X)
    if bonds is None:
        elements = elements_from_atomtypes(atomtypes) if atomtypes else None
        bonds = infer_bonds(X, elements)
    bond = np.zeros((n, n), dtype=bool)
    for i, j in bonds:
        bond[i, j] = bond[j, i] = True

    # 键图拉普拉斯（Fiedler / 谱半径）
    A_b = bond.astype(float)
    deg_b = A_b.sum(axis=1)
    L_b = np.diag(deg_b) - A_b
    ev_b = np.linalg.eigvalsh(L_b)
    lam2 = float(ev_b[1]) if n > 1 else 0.0
    alpha = float(ev_b[-1]) if n > 0 else 1.0

    # SRE 符号矩阵 M（公理 1：无零元）
    M = np.where(bond, 1.0, -1.0)
    np.fill_diagonal(M, 1.0)

    D_ii = np.abs(M).sum(axis=1)
    D_self = np.diag(M).copy()
    num = np.sqrt(np.outer(D_ii, D_ii))
    denom = np.sqrt(lam2 + D_self[:, None] + D_self[None, :] + eps_topo)
    M2 = M @ M
    damp = 1.0 + np.abs(M2) * np.log(1.0 + lam2 / max(alpha, 1e-12)) \
        / (alpha + np.sqrt(np.outer(D_ii, D_ii)))
    W_e = (num / denom) * damp
    A_s = W_e * bond.astype(float)
    np.fill_diagonal(A_s, 0.0)
    return A_s


def sre_sign_matrix(A_s: np.ndarray) -> np.ndarray:
    """
    由平滑邻接支撑反推 SRE 符号矩阵 M（流水线场景）：
    M_ij = +1 若 A_s_ij > 0（协同边），否则 -1；对角 +1。
    """
    n = A_s.shape[0]
    M = np.where(A_s > 0, 1.0, -1.0)
    np.fill_diagonal(M, 1.0)
    return M


# ─── Operator 11: Spin-Charge Adjacency (v1.1) ────────────────────────

def compute_spin_polarities(electronegativities: np.ndarray) -> np.ndarray:
    """
    SRE Axiom 1 binary spin（诊断量，v1.1 不参与权重调制）：
    s_i = sign(chi_i - chi_mean)，恰等于均值时取 +1。
    """
    chi_mean = np.mean(electronegativities)
    s = np.sign(electronegativities - chi_mean)
    s[s == 0] = 1.0
    return s


def operator_11_spin_charge_adjacency(A_s: np.ndarray,
                                      electronegativities: np.ndarray,
                                      rho: float = 0.5) -> dict:
    """
    Operator 11 — Spin-Charge Adjacency（v1.1 规范式 (4.1)-(4.6)）。

    权重调制（解耦自旋极性）:
        w_q(i,j)  = |tanh(chi_i - chi_j)|            (4.3)
        A_q(i,j)  = A_s(i,j) * (1 + rho * w_q(i,j))  (4.4)
        L_q       = diag(A_q 1) - A_q                (4.5)
        lambda_2_q = λ2(L_q), alpha_q = max|λ(L_q)|,
        kappa_q    = alpha_q / lambda_2_q             (4.5)

    诊断标量（s/sigma/d 仅用于诊断，不参与调制）:
        s_i        = sign(chi_i - chi_mean)           (4.2)
        sigma_ij   = s_i * s_j, d_ij = (1 - sigma_ij)/2
        q_dispersion      = std(|chi|) / mean(|chi|)  (4.6)
        max_spin_coupling = max_{(i,j) in E+} |sigma_ij * w_q(i,j)|
                          = tanh(max |dchi|)          (定理 11.5)

    Returns:
        A_q, L_q, lambda_2_q, alpha_q, kappa_q,
        q_dispersion, max_spin_coupling, s, sigma, d, wq
    """
    chi = np.asarray(electronegativities, dtype=np.float64)
    N = len(chi)
    s = compute_spin_polarities(chi)
    sigma = np.outer(s, s)
    d = (1.0 - sigma) / 2.0
    wq = np.abs(np.tanh(chi[:, None] - chi[None, :]))

    A_q = A_s * (1.0 + rho * wq)
    np.fill_diagonal(A_q, 0.0)

    deg = A_q.sum(axis=1)
    L_q = np.diag(deg) - A_q
    eigvals = np.linalg.eigvalsh(L_q)
    lambda_2_q = float(eigvals[1]) if N > 1 else 0.0
    alpha_q = float(np.max(np.abs(eigvals)))
    kappa_q = alpha_q / lambda_2_q if lambda_2_q > 1e-12 else float("inf")

    q_dispersion = float(np.std(np.abs(chi)) / (np.mean(np.abs(chi)) + 1e-12))

    support = A_s > 0
    sc_sup = np.abs(sigma * wq)[support]
    max_spin_coupling = float(np.max(sc_sup)) if support.any() else 0.0

    return {
        "A_q": A_q, "L_q": L_q,
        "lambda_2_q": lambda_2_q, "alpha_q": alpha_q, "kappa_q": kappa_q,
        "q_dispersion": q_dispersion, "max_spin_coupling": max_spin_coupling,
        "s": s, "sigma": sigma, "d": d, "wq": wq,
    }


# ─── Operator 12: Topological Closed-Loop Audit (v1.1) ────────────────
# (完整实现在 Operator_12_P.py 中；此处保留接口以便 compute_electronic_fingerprint 调用)

def enumerate_simple_cycles(adj: np.ndarray, N_max: int) -> list:
    """
    DFS 枚举长度 <= N_max 的简单环（无向图）。
    无回溯（路径内顶点不重复）、无重复计数。
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
        rot = c[k:] + c[:k]
        rev = [rot[0]] + rot[:0:-1]
        key = min(tuple(rot), tuple(rev))
        if key not in seen:
            seen.add(key)
            cycles.append(c)
    return cycles


def operator_12_closed_loop_audit(A_q: np.ndarray,
                                  M: np.ndarray = None,
                                  N_max: int = None) -> dict:
    """
    Operator 12 — Topological Closed-Loop Audit（v1.1 规范式 (5.1)-(5.4)）。

    n_loops       = 简单环计数（定义 5.2；定理 12.2 消除回溯污染）
    mobius_ratio  = mean_{k=3..N_max} |tr(M^k)| / n^k（定义 5.3；
                    定理 12.3 符号平衡判据：=1 ⟺ 无 Möbius，<1 ⟺ 有）
    lambda_2_loop = λ2(L_q[S,S])，S = 环原子并集（定义 5.4；
                    定理 12.5 交错：λ2_loop >= λ2_q > 0）
    kappa_loop    = λmax(L_q[S,S]) / λ2(L_q[S,S])（<= kappa_q）

    M 为 SRE 符号矩阵（+-1 无零元）；为 None 时由 A_q 支撑反推。
    """
    N = A_q.shape[0]
    if N_max is None:
        N_max = min(N, 8)
    if M is None:
        M = sre_sign_matrix(A_q)

    cycles = enumerate_simple_cycles(A_q, N_max)
    n_loops = len(cycles)
    loop_atoms = sorted(set(v for c in cycles for v in c))

    # Möbius 相位比（定义 5.3）：在符号矩阵 M 上，|tr(M^k)| / n^k
    ratios = []
    for k in range(3, N_max + 1):
        Mk = np.linalg.matrix_power(M, k)
        tau = np.trace(Mk)
        ratios.append(abs(tau) / float(N ** k))
    mobius_ratio = float(np.mean(ratios)) if ratios else 1.0

    # 环上子图谱量（定义 5.4）
    if len(loop_atoms) >= 3:
        deg = A_q.sum(axis=1)
        L_q = np.diag(deg) - A_q
        sub = np.ix_(loop_atoms, loop_atoms)
        L_loop = L_q[sub]
        ev = np.linalg.eigvalsh(L_loop)
        lambda_2_loop = float(ev[1])
        kappa_loop = float(ev[-1] / ev[1]) if ev[1] > 1e-12 else float("inf")
    else:
        lambda_2_loop = float("nan")
        kappa_loop = float("nan")

    return {
        "n_loops": n_loops,
        "n_closed_loops": n_loops,
        "mobius_ratio": mobius_ratio,
        "lambda_2_loop": lambda_2_loop,
        "kappa_loop": kappa_loop,
        "loop_atoms": loop_atoms,
    }


# ─── Combined Electronic Fingerprint (v1.1, 7 keys) ───────────────────

def compute_electronic_fingerprint(positions_xyz: np.ndarray,
                                   A_smooth: np.ndarray,
                                   electronegativities: np.ndarray,
                                   rho: float = 0.5,
                                   N_max: int = None) -> dict:
    """
    完整电子 SRE 指纹（v1.1，7 键，方案要求；不重叠既有几何 4 键）。

    流水线入口：A_smooth 由上游算子 1/4 输出（SRE 平滑邻接，非 k-NN）。

    Returns 7 个标量:
        lambda_2_q, kappa_q, alpha_q, n_loops, mobius_ratio,
        q_dispersion, max_spin_coupling
    """
    M = sre_sign_matrix(A_smooth)
    op11 = operator_11_spin_charge_adjacency(A_smooth, electronegativities, rho)
    op12 = operator_12_closed_loop_audit(op11["A_q"], M, N_max)
    return {
        "lambda_2_q": op11["lambda_2_q"],
        "kappa_q": op11["kappa_q"],
        "alpha_q": op11["alpha_q"],
        "n_loops": op12["n_loops"],
        "mobius_ratio": op12["mobius_ratio"],
        "q_dispersion": op11["q_dispersion"],
        "max_spin_coupling": op11["max_spin_coupling"],
    }


# ─── Self-test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== SRE Electronic Ops (v1.1) Self-Test ===\n")

    # ── 乙醇（开链，β1 = 0）──────────────────────────────────────────
    atomtypes = ["c3", "c3", "oh", "hc", "hc", "hc", "h1", "h1", "ho"]
    chis = electronegativities_from_atomtypes(atomtypes)
    pos = np.array([
        [0.0, 0.0, 0.0],       # 0 C1 (c3)
        [1.52, 0.0, 0.0],      # 1 C2 (c3)
        [2.15, 1.35, 0.0],     # 2 O  (oh)
        [-0.5, 0.9, 0.3],      # 3 H  (hc)
        [-0.5, -0.9, -0.3],   # 4 H  (hc)
        [-0.5, 0.0, -0.9],    # 5 H  (hc)
        [1.52, -0.9, 0.9],     # 6 H  (h1)
        [1.52, 0.9, -0.9],     # 7 H  (h1)
        [2.15, 1.35, 0.96],    # 8 H5 (ho, O-H)
    ], dtype=np.float64)

    print("--- Ethanol (open chain, beta_1 = 0) ---")
    ethanol_bonds = [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 6), (1, 7), (2, 8)]
    A_s = build_sre_smooth_adjacency(pos, atomtypes=atomtypes, bonds=ethanol_bonds)
    M = sre_sign_matrix(A_s)
    n_edges = int((A_s > 0).sum() // 2)
    print("E+ from topology (bonds):", n_edges, "(expect 8)")
    print("A_s symmetric:", np.allclose(A_s, A_s.T),
          "| nonneg:", float(A_s.min()) >= 0)

    s = compute_spin_polarities(chis)
    print("s_i (diagnostic):", s.astype(int).tolist())

    op11 = operator_11_spin_charge_adjacency(A_s, chis, rho=0.5)
    A_q, wq = op11["A_q"], op11["wq"]
    gain = {(i, j): 1.0 + 0.5 * wq[i, j] for (i, j) in
            [(0, 1), (1, 2), (0, 3), (2, 8)]}
    print("Gain factors:  C-C=%.4f  C-O=%.4f  C-H=%.4f  O-H=%.4f"
          % (gain[(0, 1)], gain[(1, 2)], gain[(0, 3)], gain[(2, 8)]))
    print("max_spin_coupling = %.4f (expect tanh(1.24)=%.4f on O-H)"
          % (op11["max_spin_coupling"], np.tanh(1.24)))
    print("lambda_2_q=%.4f  alpha_q=%.4f  kappa_q=%.4f  q_dispersion=%.4f"
          % (op11["lambda_2_q"], op11["alpha_q"], op11["kappa_q"],
             op11["q_dispersion"]))

    op12 = operator_12_closed_loop_audit(A_q, M, N_max=8)
    print("Ethanol: n_loops=%d  mobius_ratio=%.6f  lambda_2_loop=%s"
          % (op12["n_loops"], op12["mobius_ratio"],
             "NaN" if np.isnan(op12["lambda_2_loop"])
             else "%.6f" % op12["lambda_2_loop"]))

    # ── 苯环（单环，β1 = 1）──────────────────────────────────────────
    print("\n--- Synthetic Benzene Ring (6C, beta_1 = 1) ---")
    angles = np.linspace(0, 2 * np.pi, 7)[:-1]
    benz_pos = np.column_stack([np.cos(angles), np.sin(angles), np.zeros(6)]) * 1.40
    benz_chis = np.array([2.55] * 6)
    benz_A_s = build_sre_smooth_adjacency(benz_pos, atomtypes=["c3"] * 6)
    benz_M = sre_sign_matrix(benz_A_s)
    print("Benzene bonds (E+):", int((benz_A_s > 0).sum() // 2), "(expect 6)")
    print("infer_bonds on benzene (auto):", len(infer_bonds(benz_pos, ["C"] * 6)),
          "(expect 6)")
    benz_op11 = operator_11_spin_charge_adjacency(benz_A_s, benz_chis, rho=0.5)
    benz_op12 = operator_12_closed_loop_audit(benz_op11["A_q"], benz_M, N_max=8)
    print("Benzene: n_loops=%d  mobius_ratio=%.6f  lambda_2_loop=%.6f  kappa_loop=%.6f"
          % (benz_op12["n_loops"], benz_op12["mobius_ratio"],
             benz_op12["lambda_2_loop"], benz_op12["kappa_loop"]))

    # ── 指纹（7 键）──────────────────────────────────────────────────
    print("\n--- Fingerprint (7 keys) ---")
    fp = compute_electronic_fingerprint(pos, A_s, chis, rho=0.5)
    for k, v in fp.items():
        print("  %-18s = %s" % (k, "%.6f" % v if isinstance(v, float) else v))

    # ── 断言（对应《算子-11/12 严格数学规范》v1.1 验证协议）───────────
    fails = []
    def check(desc, cond):
        print(("  [PASS] " if cond else "  [FAIL] ") + desc)
        if not cond:
            fails.append(desc)

    print("\n--- Assertions (spec v1.1) ---")
    check("乙醇 E+（拓扑）= 8 键", n_edges == 8)
    check("A_s 对称且非负", np.allclose(A_s, A_s.T) and float(A_s.min()) >= 0)
    check("增益排序 O-H > C-O > C-H > C-C = 1（定理 11.4）",
          gain[(2, 8)] > gain[(1, 2)] > gain[(0, 3)] > gain[(0, 1)]
          and abs(gain[(0, 1)] - 1.0) < 1e-12)
    check("max_spin_coupling = tanh(1.24) ≈ 0.8455（定理 11.5）",
          abs(op11["max_spin_coupling"] - np.tanh(1.24)) < 1e-3)
    check("乙醇 n_loops = 0（定理 12.2/12.4）", op12["n_loops"] == 0)
    check("苯环 n_loops = 1 = beta_1（定理 12.4）", benz_op12["n_loops"] == 1)
    check("苯环 lambda_2_loop >= lambda_2_q > 0（定理 12.5）",
          benz_op12["lambda_2_loop"] >= benz_op11["lambda_2_q"] - 1e-9
          and benz_op12["lambda_2_loop"] > 0)
    check("指纹返回 7 键且无重叠", len(fp) == 7 and
          set(fp) == {"lambda_2_q", "kappa_q", "alpha_q", "n_loops",
                      "mobius_ratio", "q_dispersion", "max_spin_coupling"})

    # ── 7.3 定理 11.3：Gershgorin 上界 ──────────────────────────────
    print("\n--- 7.3 Theorem 11.3: Gershgorin upper bound ---")
    ev_q = np.linalg.eigvalsh(op11["L_q"])
    d_q = A_q.sum(axis=1)
    gershgorin = op11["alpha_q"] <= 2.0 * float(d_q.max()) + 1e-9
    check("L_q 半正定 (min eig=%.6f)" % float(ev_q.min()), float(ev_q.min()) >= -1e-9)
    check("lambda_2_q=%.4f > 0" % op11["lambda_2_q"], op11["lambda_2_q"] > 0)
    check("alpha_q=%.4f <= 2*max(d_q)=%.4f" % (op11["alpha_q"], 2 * float(d_q.max())),
          gershgorin)

    # ── 7.5 定理 11.6：Weyl 谱摄动上界 / rho→0 退化 ─────────────────
    print("\n--- 7.5 Theorem 11.6: Weyl spectral perturbation bound ---")
    lam2_s = float(np.linalg.eigvalsh(np.diag(A_s.sum(1)) - A_s)[1])
    Delta_max = float(max(np.sum(A_s * wq, axis=1)))
    weyl_bound = 2.0 * 0.5 * Delta_max
    weyl_diff = abs(op11["lambda_2_q"] - lam2_s)
    check("|lambda_2_q - lambda_2_s|=%.6f <= 2*rho*Delta_max=%.6f"
          % (weyl_diff, weyl_bound), weyl_diff <= weyl_bound + 1e-9)
    A_q_rho0 = operator_11_spin_charge_adjacency(A_s, chis, rho=0.0)["A_q"]
    check("rho=0 时 A_q = A_s（连续退化）", np.allclose(A_q_rho0, A_s, atol=1e-12))

    # ── 7.7 定理 12.3：Möbius 符号平衡判据（合成符号矩阵）────────────
    print("\n--- 7.7 Theorem 12.3: Mobius sign-balance criterion ---")
    n7 = 6
    M_bal = np.ones((n7, n7))
    M_neg = np.ones((n7, n7))
    M_neg[0, 1] = M_neg[1, 0] = -1.0
    r_bal = operator_12_closed_loop_audit(np.eye(n7), M_bal, N_max=6)["mobius_ratio"]
    r_neg = operator_12_closed_loop_audit(np.eye(n7), M_neg, N_max=6)["mobius_ratio"]
    check("全 +1 符号矩阵 mobius_ratio=%.6f = 1（无 Mobius）" % r_bal,
          abs(r_bal - 1.0) < 1e-9)
    check("含负环符号矩阵 mobius_ratio=%.6f < 1（Mobius 存在）" % r_neg,
          r_neg < 1.0 - 1e-9)

    # ── 7.10 定理 12.6：审计迹 Lipschitz 鲁棒性 ─────────────────────
    print("\n--- 7.10 Theorem 12.6: Lipschitz robustness ---")
    rng = np.random.default_rng(42)
    n10 = A_q.shape[0]
    E = rng.standard_normal((n10, n10))
    E = (E + E.T) / 2.0
    delta = 1e-3
    B = A_q + delta * E
    Mbar = max(np.linalg.norm(A_q, 2), np.linalg.norm(B, 2))
    lip_ok = True
    for k in range(2, 9):
        tA = np.trace(np.linalg.matrix_power(A_q, k))
        tB = np.trace(np.linalg.matrix_power(B, k))
        lhs = abs(tA - tB)
        rhs = k * Mbar ** (k - 1) * delta * np.linalg.norm(E, 2)
        if lhs > rhs + 1e-9:
            lip_ok = False
            break
    check("|t_k(A)-t_k(B)| <= k*M^(k-1)*delta*||E||_2 对所有 k∈[2,8]",
          lip_ok)

    print("\n" + ("All v1.1 self-tests passed."
                  if not fails else "Failed: %s" % fails))
