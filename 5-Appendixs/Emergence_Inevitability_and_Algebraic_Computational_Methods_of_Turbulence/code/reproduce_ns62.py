"""
复现 n-s.md §6.2 相图 —— 程序正确性闸门
=====================================
论文 §6.2 声明"所有数值由 sre_core.py 产生"，参数 N=60, seeds 0-4, 模式 A。

若当前优化版 sre_core.evolve 能复现 §6.2 表格，则程序与论文一致，
具备"用数据否定论文"的资格；否则存在代码/版本失配。

论文 §6.2 目标值 (结构密度=frac_neg, 各向异性=classical_mds_anisotropy, 谱斜率=spectral_slope):
  Λ        结构密度    sd       各向异性   谱斜率    sd
  1e-4     0.4915    0.0001    0.4308    -1.851   0.055
  1e-3     0.4901    0.0004    0.3753    -1.847   0.151
  1e-2     0.4764    0.0016    0.3587    -1.824   0.326
  1e-1     0.3809    0.0023    0.3515    -1.566   0.250
  3.16e-1  0.2622    0.0026    0.3510    -0.556   0.935
  1        0.1435    0.0046    0.3501    +0.207   1.414
  3.16     0.0647    0.0026    0.3618    +0.124   0.762
  10       0.0254    0.0024    0.3600    +0.264   1.080
  1e2      0.0026    0.0004    0.3715    +0.442   0.095
"""
import sys, numpy as np
sys.path.insert(0, r'c:\mywork\wei')
from sre_core import evolve, measure

LAMS = [1e-4, 1e-3, 1e-2, 1e-1, 3.16e-1, 1.0, 3.16, 10.0, 1e2]
SEEDS = [0, 1, 2, 3, 4]
N = 60

# 论文 §6.2 目标值
PAPER = {
    1e-4: (0.4915, 0.0001, 0.4308, -1.851, 0.055),
    1e-3: (0.4901, 0.0004, 0.3753, -1.847, 0.151),
    1e-2: (0.4764, 0.0016, 0.3587, -1.824, 0.326),
    1e-1: (0.3809, 0.0023, 0.3515, -1.566, 0.250),
    3.16e-1: (0.2622, 0.0026, 0.3510, -0.556, 0.935),
    1.0: (0.1435, 0.0046, 0.3501, 0.207, 1.414),
    3.16: (0.0647, 0.0026, 0.3618, 0.124, 0.762),
    10.0: (0.0254, 0.0024, 0.3600, 0.264, 1.080),
    1e2: (0.0026, 0.0004, 0.3715, 0.442, 0.095),
}


def main():
    print("=" * 92)
    print(f"复现 n-s.md §6.2 相图 (N={N}, seeds={SEEDS}, mode=A/exogenous)")
    print("=" * 92)
    print(f"{'Λ':>8s} | {'密度(实测)':>10s} {'(论文)':>8s} {'Δ':>8s} | "
          f"{'各向异':>8s} {'(论文)':>8s} {'Δ':>8s} | "
          f"{'斜率':>8s} {'(论文)':>8s} {'Δ':>8s}")
    print("-" * 92)

    max_dens_dev = 0.0
    max_aniso_dev = 0.0
    max_slope_dev = 0.0
    for lam in LAMS:
        dens, aniso, slope = [], [], []
        for s in SEEDS:
            M, _ = evolve(N, lam=lam, mode="exogenous", seed=s)
            m = measure(M)
            dens.append(m["frac_neg"])
            aniso.append(m["anisotropy"])
            slope.append(m["slope"])
        d_m, a_m, s_m = np.nanmean(dens), np.nanmean(aniso), np.nanmean(slope)
        pd, pa, ps, _ = PAPER[lam][0], PAPER[lam][2], PAPER[lam][3], None
        dd, da, ds = d_m - pd, a_m - pa, s_m - ps
        max_dens_dev = max(max_dens_dev, abs(dd))
        max_aniso_dev = max(max_aniso_dev, abs(da))
        max_slope_dev = max(max_slope_dev, abs(ds))
        print(f"{lam:8.4g} | {d_m:10.4f} {pd:8.4f} {dd:+8.4f} | "
              f"{a_m:8.4f} {pa:8.4f} {da:+8.4f} | "
              f"{s_m:8.4f} {ps:8.4f} {ds:+8.4f}")

    print("-" * 92)
    print(f"最大偏差:  密度 {max_dens_dev:.4f}   各向异性 {max_aniso_dev:.4f}   "
          f"谱斜率 {max_slope_dev:.4f}")
    ok = max_dens_dev < 0.01 and max_aniso_dev < 0.02
    print(f"\n判定: {'✅ 程序复现论文 §6.2 (密度/各向异性一致)' if ok else '❌ 与论文 §6.2 不一致'}")
    print("(谱斜率是高阶量, 对 PRNG 敏感, 论文 §6.6 已声明)")


if __name__ == '__main__':
    main()