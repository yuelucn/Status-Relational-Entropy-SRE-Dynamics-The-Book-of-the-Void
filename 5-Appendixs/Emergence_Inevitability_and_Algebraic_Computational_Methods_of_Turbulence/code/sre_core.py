"""
SRE 规范参考实现 v2
===================

本文件是论文（n-s.md / Turbulence_generation.md）与实验台（sre_phase_console.html）
共同的**唯一数值基准**。论文中的每一条数值断言都必须能在这里复现。

相对 v1（散见于 N-S.py / b.py / oseen_convergence_dashboard.py）的修正：

 [F1] 判据算子的符号约定
      v1 写作 ΔS = βΛD − αTr(AᵀA) 且 P_active = 1/(1+e^{−ΔS})，却在正文中宣称
      Λ→∞ 时 P_active→0。二者矛盾：该式在 Λ→∞ 时给出 P_active→1。
      修正：保持 Ψ ≡ βΛD − αTr(AᵀA)（抹平项 − 生成项），改用
            P_active = 1/(1 + e^{Ψ})
      于是 Λ→∞ ⇒ Ψ→+∞ ⇒ P_active→0（层流）；Λ→0 ⇒ Ψ<0 ⇒ P_active→1（结构相）。
      临界条件 Ψ=0 给出 Λ_c = αTr(AᵀA)/(βD)，与原论文结论一致。

 [F2] 稳定项 / 失稳项的标注错配
      v1 把 βΛD 标为"失稳项"。但 Λ ∝ 1/Re，Λ 大对应低雷诺数层流，因此
      βΛD 是**有序化（抹平）项**；αTr(AᵀA) 才对应结构再生，是失稳项。已更正。

 [F3] M 的对称性问题
      N-S.py 曾强制 M[v_m,v_f] = −M[v_f,v_m]，使 M 整体反对称；而理论把
      A = (M−Mᵀ)/2 定义为 M 的**反对称部分**。若 M 纯反对称则 A ≡ M，"剪切部分"
      的说法失效，且反对称矩阵无法作为 MDS 的 precomputed 度规（sklearn 报
      "Array must be symmetric"）。
      修正：M 保持一般非对称矩阵。严格二分
            S = (M + Mᵀ)/2  → 拓扑度规，几何重构（MDS）只作用在 S 上
            A = (M − Mᵀ)/2  → 局域自旋算子，手性 / 涡作用量只由 A 承担
      M 非对称 ⟺ A ≠ 0 ⟺ 系统携带手性。

 [F4] Λ 被内生参数取代，导致相变叙事失去把手
      Theorem 7 用谱半径构造 λ(n) = (1/β)·ln(1+ρ(A_{n−1}))/(n+1) 解除了循环依赖，
      但同时也把外生控制量 Λ 挤出了演化方程。
      修正：显式区分二者——Λ 是外生的宏观耗散权威（相变控制量），λ(n) 是内生的
      状态自适应因子。提供两种模式以便对照：
            mode="exogenous" : p = 1 − 1/(1 + Λ·D_s/𝔅)
            mode="adaptive"  : p = 1 − 1/(1 + Λ·λ(n)·D_s/𝔅)
      其中 𝔅 = E_local + exp(sgn(Ẽ)) 为局域相干势垒。

 [F5] 谱斜率的限定
      一维手性场的功率谱斜率只是能量级联的**代理指标**，不等于三维能谱 E(k)。
      实测高 Re 侧稳定在 −1.85 附近，略陡于 −5/3。不得表述为"严格合拢"。
"""

import numpy as np

__all__ = [
    "sym_part", "antisym_part", "spectral_radius", "tracking_parameter",
    "evolve", "measure", "spectral_slope", "classical_mds_anisotropy", "sweep",
]


# ---------------------------------------------------------------- 基本对象

def sym_part(M):
    """S = (M + Mᵀ)/2 —— 拓扑度规部分。几何重构只作用于 S。"""
    return 0.5 * (M + M.T)


def antisym_part(M):
    """A = (M − Mᵀ)/2 —— 局域自旋算子（手性 / 涡作用量）。"""
    return 0.5 * (M - M.T)


def spectral_radius(M, iters=60, seed=0):
    """幂迭代估计谱半径 ρ(M)。M 可以是非对称实矩阵。"""
    n = M.shape[0]
    if n == 1:
        return abs(M[0, 0])
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(n)
    v /= np.linalg.norm(v)
    lam = 0.0
    for _ in range(iters):
        w = M @ v
        nw = np.linalg.norm(w)
        if nw < 1e-14:
            return 0.0
        # Rayleigh quotient on the non-symmetric matrix
        lam = float(v @ w)
        v = w / nw
    return abs(lam)


def tracking_parameter(M_prev, beta=1.1):
    """Theorem 7 —— 解耦跟踪参数 λ(n) = (1/β)·ln(1+ρ(A_{n−1}))/(n+1).

    用上一轮已实现子图的谱半径替代对当前状态的依赖，从而消除算子间的循环死锁。
    """
    n = M_prev.shape[0]
    rho = spectral_radius(M_prev)
    return (1.0 / beta) * np.log(1.0 + rho) / (n + 1.0)


# ---------------------------------------------------------------- 演化

def evolve(n_steps, lam=0.01, mode="exogenous", beta=1.1, seed=0):
    """算子 1（块扩张 + 只读继承）× 算子 2（极大熵剪枝）。

    返回 (M, history)，history 每步记录 (n, 存活通道数, λ(n))。
    """
    if mode not in ("exogenous", "adaptive"):
        raise ValueError("mode must be 'exogenous' or 'adaptive'")

    rng = np.random.default_rng(seed)
    M = np.array([[1.0]])
    history = []

    for n in range(1, n_steps):
        Mn = np.ones((n + 1, n + 1))
        Mn[:n, :n] = M                       # 算子 1：只读历史子块继承

        if mode == "adaptive":
            lam_n = tracking_parameter(M, beta=beta)
            gain = lam * lam_n
        else:
            lam_n = 1.0
            gain = lam

        vf = n
        active = 0

        for vm in range(n):
            D_s = (n + 1) - (vm + 1)         # 无量纲因果拓扑深度

            # 2 步图游走干涉项（Theorem 3 的局域多回路多项式）
            inter = 0.0
            for k in range(n):
                if Mn[vf, k] != 1.0 and Mn[k, vm] != 1.0:
                    inter += Mn[vf, k] * Mn[k, vm]
            E_tilde = inter + 2.0 * Mn[vf, vm]
            E_local = abs(E_tilde)
            barrier = E_local + np.exp(np.sign(E_tilde) if E_tilde != 0 else 1.0)

            # 极大熵剪枝主方程（Theorem 6）
            p_prune = 1.0 - 1.0 / (1.0 + gain * D_s / barrier)

            if rng.random() >= p_prune:      # χ = 1：通道存活，注入手性剪切
                if vf > vm:
                    Mn[vf, vm] = -1.0 if (vf - vm) % 3 == 0 else 1.0
                    Mn[vm, vf] = -Mn[vf, vm]
                active += 1
            else:                            # χ = 0：Paradigm B，强制自旋 +1
                Mn[vf, vm] = 1.0
                Mn[vm, vf] = 1.0

        Mn[vf, vf] = 1.0                     # Theorem 3：对角锁定
        history.append((n + 1, active, lam_n))
        M = Mn

    return M, history


# ---------------------------------------------------------------- 度量

def spectral_slope(M):
    """手性场沿因果序的一维功率谱在 log-log 下的斜率。

    注意 [F5]：这是一维代理谱，不是三维能谱 E(k)。
    """
    n = M.shape[0]
    A = antisym_part(M)
    sig = A.sum(axis=1)
    sig = sig - sig.mean()
    if np.std(sig) < 1e-12:
        return np.nan
    P = np.abs(np.fft.rfft(sig)) ** 2
    k = np.arange(1, len(P))
    P = P[1:]
    lo = max(1, len(k) // 8)
    hi = max(2, len(k) // 2)
    kk, PP = k[lo:hi], P[lo:hi]
    if len(kk) < 3 or np.any(PP <= 0):
        return np.nan
    return float(np.polyfit(np.log(kk), np.log(PP), 1)[0])


def classical_mds_anisotropy(M):
    """在对称部分 S 上做经典 MDS（Torgerson），返回 λ₁/Σλ。

    1/3 表示三个方向完全均分（各向同性）；→1 表示坍缩为一维刚性轴。
    """
    n = M.shape[0]
    S = sym_part(M)
    D2 = np.clip(2.0 - 2.0 * S, 0.0, 4.0)
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ D2 @ J
    ev = np.clip(np.linalg.eigvalsh(B)[::-1][:3], 0.0, None)
    if ev.sum() < 1e-12:
        return np.nan
    return float(ev[0] / ev.sum())


def measure(M):
    """返回一组无量纲观测量。所有量都由 M 的对称 / 反对称二分严格导出。"""
    n = M.shape[0]
    S = sym_part(M)
    A = antisym_part(M)
    return dict(
        frac_neg=float(np.mean(M < 0)),                       # 结构密度
        spin_energy=float(np.trace(A.T @ A)),                 # Tr(AᵀA)，涡作用量
        antisym_share=float(np.trace(A.T @ A) /
                            (np.trace(M.T @ M) + 1e-12)),     # 手性占比
        anisotropy=classical_mds_anisotropy(M),
        slope=spectral_slope(M),
        sym_defect=float(np.abs(M - M.T).max()),              # 非对称度
        n=n,
    )


# ---------------------------------------------------------------- 扫掠

def sweep(lams, n_steps=60, mode="exogenous", seeds=(0, 1, 2, 3, 4), beta=1.1):
    """对 Λ 列表做多种子扫掠，返回统计后的列表。"""
    keys = ["frac_neg", "spin_energy", "antisym_share", "anisotropy", "slope"]
    out = []
    for lam in lams:
        acc = {k: [] for k in keys}
        for s in seeds:
            M, _ = evolve(n_steps, lam, mode=mode, beta=beta, seed=s)
            m = measure(M)
            for k in keys:
                acc[k].append(m[k])
        row = dict(lam=float(lam), re=float(1.0 / lam), mode=mode)
        for k in keys:
            row[k] = float(np.nanmean(acc[k]))
            row[k + "_sd"] = float(np.nanstd(acc[k]))
        out.append(row)
    return out


# ---------------------------------------------------------------- 自测

def _selftest():
    """最小自测：两种模式在若干 Λ 上的关键观测量，用于确认环境与可复现性。"""
    print("sre_core self-test  (N=60, 5 seeds)")
    print("%-10s %10s | %9s %9s | %9s" %
          ("mode", "Lambda", "frac_neg", "anisotropy", "slope"))
    for mode in ("exogenous", "adaptive"):
        for lam in (1e-3, 1e-1, 1.0, 10.0):
            rows = sweep([lam], n_steps=60, mode=mode, seeds=(0, 1, 2, 3, 4))
            r = rows[0]
            print("%-10s %10.4g | %9.4f %9.4f | %+9.3f" % (
                mode, r["lam"], r["frac_neg"], r["anisotropy"], r["slope"]))
    M, _ = evolve(60, 0.01, mode="exogenous", seed=0)
    m = measure(M)
    print()
    print("symmetry check: max|M - M^T| = %.3f  (0 would mean M is symmetric)" %
          m["sym_defect"])
    print("antisymmetric energy share = %.4f" % m["antisym_share"])
    print()
    print("expected: frac_neg decreases monotonically with Lambda in both modes;")
    print("          slope ~ -1.85 at low Lambda, -> ~0 at high Lambda.")


if __name__ == "__main__":
    _selftest()
