"""
耗散理论闭环验证
================
用 evolve 中实际的 barrier 分布, 直接计算 p_prune 并与实测 C 对比.

理论: p_prune(d) = 1 - 1/(1 + λ·d/barrier(d))
实测: C = <p_prune>  在窗口内对 d 求平均

若两者吻合, 则耗散理论主方程在真实 SRE 演化中成立,
β∞=0 的结论有坚实基础.
"""
import sys, numpy as np, pickle
sys.path.insert(0, r'c:\mywork\wei')
from sre_core import evolve


def compute_C_from_M(M, lam):
    """直接从 M 用主方程算 C, 与 compute_C 对比"""
    n = M.shape[0]
    vf = n - 1
    # 对每个 vm 算 barrier, 再算 p_prune
    ps = []
    for vm in range(n):
        if vm > 0:
            row_seg = M[vf, :vm]
            hist_col = M[:vm, vm]
            mask = (row_seg != 1.0) & (hist_col != 1.0)
            inter = float(np.dot(row_seg[mask], hist_col[mask]))
        else:
            inter = 0.0
        E_tilde = inter + 2.0 * M[vf, vm]
        sign_E = np.sign(E_tilde) if E_tilde != 0 else 1.0
        barrier = abs(E_tilde) + np.exp(sign_E)
        d = n - vm   # D_s = (n+1)-(vm+1) = n-vm
        p = 1.0 - 1.0 / (1.0 + lam * d / barrier)
        ps.append(p)
    return float(np.mean(ps))


def main():
    print("=" * 68)
    print("耗散理论闭环验证: p_prune(主方程) vs C(实测)")
    print("=" * 68 + "\n")

    LAMS = [0.01, 0.05, 0.10, 0.20, 0.34]
    # 用 N=1600 seed=0 的单个 M, 验证 C(λ) 曲线
    N = 1600
    M, _ = evolve(n_steps=N, lam=0.05, mode='exogenous', seed=0)

    print(f"N={N}, seed=0 (演化用 λ=0.05, 但 C 计算可扫任意 λ)\n")
    print(f"{'λ':>7s} {'C_measured':>12s} {'C_theory':>10s} {'diff':>8s}")
    print("-" * 42)
    for lam in LAMS:
        # 实测 C: 用 compute_C 的定义
        Cs = []
        for n in range(max(2, N - 60), N):
            Cs.append(np.sum((M[:n, n] > 0) & (M[n, :n] > 0)) / n)
        C_meas = np.mean(Cs)
        # 理论 C: 用主方程在最终前沿层算
        C_theory = compute_C_from_M(M, lam)
        print(f"{lam:7.2f} {C_meas:12.4f} {C_theory:10.4f} {C_theory-C_meas:+8.4f}")

    # 注意: C_measured 不随 λ 变化 (因为 M 已固定), 但 C_theory 随 λ 变化
    # 这说明 C_measured 是固定 M 的结构性质, 而 C_theory 是用主方程预测
    # 正确的验证: 对每个 λ 演化一个 M, 再比较
    print("\n--- 正确验证: 每个 λ 独立演化 ---")
    print(f"{'λ':>7s} {'C_measured':>12s} {'C_theory':>10s} {'diff':>8s} {'β_meas':>8s} {'β_theory':>9s}")
    print("-" * 62)
    C_m_list, C_t_list = [], []
    for lam in LAMS:
        M, _ = evolve(n_steps=N, lam=lam, mode='exogenous', seed=0)
        Cs = []
        for n in range(max(2, N - 60), N):
            Cs.append(np.sum((M[:n, n] > 0) & (M[n, :n] > 0)) / n)
        C_meas = np.mean(Cs)
        C_theory = compute_C_from_M(M, lam)
        C_m_list.append(C_meas)
        C_t_list.append(C_theory)
        print(f"{lam:7.2f} {C_meas:12.4f} {C_theory:10.4f} {C_theory-C_meas:+8.4f}")

    # 算 β
    ALPHA = 783.2
    Re = ALPHA / np.array(LAMS)
    m = Re >= 5000
    b_meas = np.polyfit(np.log10(Re[m]), np.log10(1.0/np.array(C_m_list)[m]), 1)[0]
    b_theory = np.polyfit(np.log10(Re[m]), np.log10(1.0/np.array(C_t_list)[m]), 1)[0]
    print(f"\n  β_measured = {b_meas:.4f}")
    print(f"  β_theory   = {b_theory:.4f}")
    print(f"  差异       = {abs(b_meas-b_theory):.4f}")

    # 对 N=3200, 6400 也验证
    print("\n--- 多 N 验证 (λ=0.05) ---")
    print(f"{'N':>6s} {'C_measured':>12s} {'C_theory':>10s} {'diff':>8s}")
    for N in [800, 1600, 3200]:
        M, _ = evolve(n_steps=N, lam=0.05, mode='exogenous', seed=0)
        Cs = [np.sum((M[:n, n] > 0) & (M[n, :n] > 0)) / n
              for n in range(max(2, N - 60), N)]
        C_meas = np.mean(Cs)
        C_theory = compute_C_from_M(M, 0.05)
        print(f"{N:6d} {C_meas:12.4f} {C_theory:10.4f} {C_theory-C_meas:+8.4f}")

    print("\n结论: 若 C_theory ≈ C_measured, 则耗散主方程在真实演化中成立.")


if __name__ == '__main__':
    main()