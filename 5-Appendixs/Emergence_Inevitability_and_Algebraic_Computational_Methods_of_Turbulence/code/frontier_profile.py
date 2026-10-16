"""
前沿距离剖面分析
=================

核心洞察：算子 1 只读继承 → M[:n,:n] 永远不变！
  - 所有历史节点之间的距离在整个演化中冻结
  - 每步唯一的新信息在前沿行/列 M[n, :n]

所以完全跳过 MDS 重嵌入的噪声问题，直接分析距离矩阵的前沿：

  d_k(n) = 1 - S_kn = 1 - (M_kn + M_nk)/2     k = 0, ..., n-1
  
  这是新节点 n 到所有历史节点 k 的 SRE 距离。

测试指标：
  1. 剖面均值 μ_d(n) = mean(d_k) —— 前沿平均距离
  2. 剖面标准差 σ_d(n) —— 前沿异质性
  3. 剖面偏度 skew(n) —— 前沿方向性（偏向一侧还是均匀）
  4. 剖面"相干半径" —— d_k < threshold 的节点数

扫 Λ 看这些指标是否正确反映层流→湍流过渡。
"""

import numpy as np
import matplotlib.pyplot as plt
from sre_core import evolve, sym_part

plt.rcParams['axes.unicode_minus'] = False

ALPHA = 783.2

print("=" * 60)
print("前沿距离剖面 vs Λ")
print("=" * 60)

lams = np.logspace(-2, 1.5, 31)
seeds = (0, 1, 2)
N_TARGET = 200

results = {
    'lam': [], 'Re': [],
    'front_mean': [], 'front_mean_sd': [],         # 前沿平均距离
    'front_std': [], 'front_std_sd': [],            # 前沿距离异质性
    'front_skew': [], 'front_skew_sd': [],          # 偏度（方向性）
    'front_radius': [], 'front_radius_sd': [],      # 相干半径
    'frac_neg': [],                                  # 结构密度 (参考)
}

import time
t0 = time.time()

print(f"\n  扫 Λ: {len(lams)} 点 × {len(seeds)} 种子 × N={N_TARGET}")
print(f"  指标: 前沿距离剖面 μ, σ, skew, 相干半径")

for lam in lams:
    Re = ALPHA / lam
    fms, fss, fsks, frs, fns = [], [], [], [], []

    for seed in seeds:
        M, _ = evolve(n_steps=N_TARGET, lam=lam, mode='exogenous', seed=seed)
        N = M.shape[0]
        S = sym_part(M)
        D = 1.0 - S   # SRE 距离矩阵 (0=完全相干, 1=完全反相干, 2=无关)
        np.fill_diagonal(D, 0.0)

        # 取最后 ~50 步的前沿剖面（系统已稳态）
        front_profiles = []
        for n in range(max(50, N - 50), N):
            d_front = D[:n, n]   # 前沿节点 n 到历史节点的距离
            front_profiles.append(d_front)

        if not front_profiles:
            continue

        # 逐剖面算指标，再跨时间平均（每个剖面长度不同，不能堆数组）
        p_means = [float(p.mean()) for p in front_profiles]
        p_stds = [float(p.std()) for p in front_profiles]
        fms.append(np.mean(p_means))
        fss.append(np.mean(p_stds))

        sks = []
        for p in front_profiles:
            if p.std() > 1e-10:
                sks.append(float(np.mean(((p - p.mean())/p.std())**3)))
            else:
                sks.append(0.0)
        fsks.append(np.mean(sks))

        fns.append(np.mean([np.mean(p < 0.5) for p in front_profiles]))
        frs.append(np.mean(p_means))

    results['lam'].append(lam)
    results['Re'].append(Re)
    results['front_mean'].append(np.mean(fms))
    results['front_mean_sd'].append(np.std(fms))
    results['front_std'].append(np.mean(fss))
    results['front_std_sd'].append(np.std(fss))
    results['front_skew'].append(np.mean(fsks))
    results['front_skew_sd'].append(np.std(fsks))
    results['front_radius'].append(np.mean(fns))
    results['front_radius_sd'].append(np.std(fns))
    results['frac_neg'].append(float(np.mean(M < 0)))

elapsed = time.time() - t0
print(f"  完成 ({elapsed:.1f}s)")

# ========== 打印关键点 ==========
print("\n--- 关键 Λ 点 ---")
key_lams = [5.0, 1.0, 0.34, 0.1, 0.03, 0.01]
for kl in key_lams:
    idx = np.argmin(np.abs(np.array(results['lam']) - kl))
    lam = results['lam'][idx]
    Re = results['Re'][idx]
    regime = "层流" if lam > 0.5 else "过渡" if lam > 0.1 else "湍流"
    print(f"  Λ={lam:.3f} (Re≈{Re:.0f}, {regime}):")
    print(f"    μ_front={results['front_mean'][idx]:.3f}, σ_front={results['front_std'][idx]:.3f}")
    print(f"    skew={results['front_skew'][idx]:.3f}, 相干半径={results['front_radius'][idx]:.3f}")
    print(f"    frac_neg={results['frac_neg'][idx]:.3f}")

# ========== 可视化 ==========
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('前沿距离剖面 vs Λ\n(跳过 MDS，直接分析 D[:n,n])',
             fontsize=13, fontweight='bold')

lam_arr = np.array(results['lam'])
lo_re, hi_re = 1500, 3500
lo_lam = ALPHA / hi_re
hi_lam = ALPHA / lo_re

# (a) 前沿平均距离
ax = axes[0, 0]
ax.semilogx(lam_arr, results['front_mean'], 'bo-', lw=2, markersize=5)
ax.fill_between(lam_arr,
                np.array(results['front_mean']) - np.array(results['front_mean_sd']),
                np.array(results['front_mean']) + np.array(results['front_mean_sd']),
                alpha=0.2, color='blue')
ax.axvspan(lo_lam, hi_lam, color='orange', alpha=0.2)
ax.set_xlabel('Λ'); ax.set_ylabel('前沿平均距离 μ_d')
ax.set_title('(a) 前沿平均距离'); ax.grid(True, alpha=0.3)

# (b) 前沿异质性
ax = axes[0, 1]
ax.semilogx(lam_arr, results['front_std'], 'ro-', lw=2, markersize=5)
ax.fill_between(lam_arr,
                np.array(results['front_std']) - np.array(results['front_std_sd']),
                np.array(results['front_std']) + np.array(results['front_std_sd']),
                alpha=0.2, color='red')
ax.axvspan(lo_lam, hi_lam, color='orange', alpha=0.2)
ax.set_xlabel('Λ'); ax.set_ylabel('前沿距离标准差 σ_d')
ax.set_title('(b) 前沿异质性 (方向性代理？)'); ax.grid(True, alpha=0.3)

# (c) 前沿偏度
ax = axes[1, 0]
ax.semilogx(lam_arr, results['front_skew'], 'go-', lw=2, markersize=5)
ax.fill_between(lam_arr,
                np.array(results['front_skew']) - np.array(results['front_skew_sd']),
                np.array(results['front_skew']) + np.array(results['front_skew_sd']),
                alpha=0.2, color='green')
ax.axvspan(lo_lam, hi_lam, color='orange', alpha=0.2)
ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
ax.set_xlabel('Λ'); ax.set_ylabel('距离剖面偏度')
ax.set_title('(c) 偏度 (0=对称, ≠0=方向性)'); ax.grid(True, alpha=0.3)

# (d) 相干半径 + frac_neg 对比
ax = axes[1, 1]
ax.semilogx(lam_arr, results['front_radius'], 'mo-', lw=2, markersize=5, label='相干半径 (d<0.5)')
ax2 = ax.twinx()
ax2.semilogx(lam_arr, results['frac_neg'], 'k--', lw=2, label='frac_neg (Φ)')
ax.set_xlabel('Λ')
ax.set_ylabel('相干半径 (占比)')
ax2.set_ylabel('结构密度 Φ')
ax.set_title('(d) 相干半径 vs Φ')
ax.legend(fontsize=8, loc='upper left')
ax2.legend(fontsize=8, loc='upper right')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('frontier_distance_profile.png', dpi=150, bbox_inches='tight')
print(f"\n看板已保存: frontier_distance_profile.png")

print(f"""
{'='*60}
前沿剖面分析解读
{'='*60}

  这是 Operator-invariant 的物理量——不依赖任何坐标嵌入！
  
  如果 σ_d 在层流侧低、湍流侧高:
    → 层流 = 前沿距离均匀 (像平面波传播)
    → 湍流 = 前沿不均匀 (像混沌传播)
  
  如果 skew 在层流侧非零、湍流侧接近 0:
    → 层流 = 有方向性偏好
    → 湍流 = 各向同性
  
  如果这些有正确的 Λ 依赖 → Landmark MDS 值得做
  如果没有 → SRE 的物理信息确实完全在算子代数层，
             距离矩阵本身就是最底层的实体
""")
