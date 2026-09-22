# -*- coding: utf-8 -*-
"""
Tier 1 第 9 项 — δ 与 α* 的数值关联推导
============================================================
前序成果：
  δ = 2sin²(π/30)/α* - 2 - cos(π/30)  （精确代数恒等式）
  gap(60,1) = 2sin²(π/30)/(2+cos(π/30))  （degree-8 代数数）
  gap(60,1) ≈ α*  精度 1.45e-5  （n_α=60.000436）

本项深入挖掘 δ-α* 数值关联的结构。

符号契约
------------------------------------------------------------
[G1] 精确函数关系 + 反函数
    δ = N/α* - C  其中 N = 1-cos(π/15) = 2sin²(π/30), C = 2+cos(π/30)
    反函数: α* = N/(C+δ)
    即: α* × (C+δ) = N  （线性关系！）
    检验: 这个线性关系是否有更深的结构意义。

[G2] 灵敏度分析
    dδ/dα* = -N/α*² = -(C+δ)/α*
    d²δ/dα*² = 2N/α*³ = 2(C+δ)/α*²
    在 α* 的 CODATA 不确定度下，δ 的传播。

[G3] 乘积/比值不变量
    δ×α* = N - C×α*  （= N - gap(60,1)×(C+1) ≈ 0.0219 - 0.0219 ≈ 0!）
    检验: δ×α* 是否接近某个简单量？

[G4] gap(60,1)≈α* 的特殊性
    对所有偶数 n, gap(n,1) 的值序列中, n=60 是否唯一接近 α*？
    比较 gap(n,1) 的分布与 α* 的位置。

[G5] 与其他物理常数的关联
    δ vs m_p/m_e, G (引力常数), ħ, c 等
    检验是否有意外的数值匹配。

[G6] 预测力
    δ-α* 关系能否预言其他 SRE 内部可观测量？
"""
import json
import os
import numpy as np

np.set_printoptions(precision=15, suppress=True)

# Constants
ALPHA_REF = 1.0 / 137.035999084
N0 = 60

# Algebraic constants
x = np.cos(np.pi / 30)  # cos(π/30), degree 8
N_alg = 1.0 - np.cos(np.pi / 15)  # = 2sin²(π/30), numerator
C_alg = 2.0 + np.cos(np.pi / 30)  # denominator constant

# δ
DELTA = N_alg / ALPHA_REF - C_alg

# Physical constants (CODATA 2018 values, dimensionless where possible)
M_P_OVER_M_E = 1836.15267343  # proton/electron mass ratio
G_DIMLESS = 6.7087e-39  # G in natural units (dimensionless coupling)
# These are for comparison only, not used in any computation

R = {"purpose": "Tier 1 item 9: delta-alpha numerical correlation", "delta": float(DELTA)}


class NpEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.integer,)): return int(o)
        if isinstance(o, (np.floating,)): return float(o)
        if isinstance(o, (np.bool_,)): return bool(o)
        if isinstance(o, np.ndarray): return o.tolist()
        return super().default(o)


def ladder_eigs(n, w):
    k = np.arange(n)
    return (2.0 + w) - 2.0 * np.cos(2.0 * np.pi * k / n) - w * ((-1.0) ** k)


def gap_of(n, w):
    mu = ladder_eigs(n, w)
    nz = mu[1:]
    return nz.min() / nz.max()


# ════════════════════════════════════════════════════════════════
# G1 — 精确函数关系 + 反函数
# ════════════════════════════════════════════════════════════════
print("=" * 78)
print("G1  δ-α* 精确函数关系 + 反函数")
print("=" * 78)

print(f"  N = 1-cos(π/15) = 2sin²(π/30) = {N_alg:.15f}")
print(f"  C = 2+cos(π/30) = {C_alg:.15f}")
print(f"  δ = N/α* - C = {N_alg:.15f}/{ALPHA_REF:.15f} - {C_alg:.15f}")
print(f"    = {N_alg/ALPHA_REF:.15f} - {C_alg:.15f}")
print(f"    = {DELTA:.15e}")
print(f"\n  反函数: α* = N/(C+δ)")
print(f"  验证: N/(C+δ) = {N_alg}/{C_alg + DELTA:.15f} = {N_alg/(C_alg+DELTA):.15f}")
print(f"  α* = {ALPHA_REF:.15f}")
print(f"  偏差 = {abs(N_alg/(C_alg+DELTA) - ALPHA_REF):.1e}")

# The key structural relation:
# α* × (C + δ) = N
# i.e., α* × (2 + cos(π/30) + δ) = 1 - cos(π/15) = 2sin²(π/30)
print(f"\n  核心结构关系:")
print(f"  α* × (C + δ) = N")
print(f"  α* × (2 + cos(π/30) + δ) = 2sin²(π/30)")
print(f"  这就是 gap = α* 的直接重排（gap = N/(C+δ), w=1+δ）")
print(f"  → δ-α* 关系是 gap 公式的线性代数重排，不携带新信息")

# Factorize the relation
print(f"\n  因子分解:")
print(f"  N = 2sin²(π/30) = 2(1-x²)  其中 x = cos(π/30)")
print(f"  C = 2+x")
print(f"  α* × (2+x+δ) = 2(1-x²) = 2(1-x)(1+x)")
print(f"  α* = 2(1-x)(1+x) / (2+x+δ)")
print(f"  当 δ=0: α*₀ = 2(1-x)(1+x)/(2+x) = gap(60,1) ≈ α*")

# Check: is there a deeper factorization?
# 2(1-x)(1+x) / (2+x) = ?
# If x = cos(π/30) ≈ 0.9945, then 1-x ≈ 0.0055, 1+x ≈ 1.9945
# 2 × 0.0055 × 1.9945 / 2.9945 ≈ 0.00730 ≈ 1/137
# The key question: is 2(1-x)(1+x)/(2+x) ≈ 1/137 a coincidence?
alpha_0 = 2 * (1 - x) * (1 + x) / (2 + x)
print(f"\n  gap(60,1) = 2(1-x)(1+x)/(2+x) = {alpha_0:.15f}")
print(f"  1/137 = {1.0/137:.15f}")
print(f"  1/137.036 = {ALPHA_REF:.15f}")
print(f"  gap vs 1/137 偏差 = {abs(alpha_0 - 1.0/137)/(1.0/137):.6e}")
print(f"  gap vs α* 偏差 = {abs(alpha_0 - ALPHA_REF)/ALPHA_REF:.6e}")

R["G1_exact_relation"] = {
    "N": float(N_alg),
    "C": float(C_alg),
    "delta": float(DELTA),
    "relation": "alpha*(C+delta) = N, i.e., alpha*(2+cos(pi/30)+delta) = 2sin^2(pi/30)",
    "inverse": "alpha* = N/(C+delta)",
    "inverse_verified": bool(abs(N_alg / (C_alg + DELTA) - ALPHA_REF) < 1e-14),
    "verdict": "delta-alpha relation is linear algebraic rearrangement of gap formula; carries no new information beyond gap=alpha"
}

# ════════════════════════════════════════════════════════════════
# G2 — 灵敏度分析
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("G2  灵敏度分析：dδ/dα*, 高阶导数")
print("=" * 78)

# δ = N/α* - C
# dδ/dα* = -N/α*² = -(C+δ)/α*
d1 = -N_alg / ALPHA_REF**2
d1_alt = -(C_alg + DELTA) / ALPHA_REF
print(f"  dδ/dα* = -N/α*² = {d1:.10e}")
print(f"        = -(C+δ)/α* = {d1_alt:.10e}")
print(f"  一致: {abs(d1 - d1_alt) < 1e-20}")

# d²δ/dα*² = 2N/α*³
d2 = 2 * N_alg / ALPHA_REF**3
print(f"  d²δ/dα*² = 2N/α*³ = {d2:.10e}")

# d³δ/dα*³ = -6N/α*⁴
d3 = -6 * N_alg / ALPHA_REF**4
print(f"  d³δ/dα*³ = -6N/α*⁴ = {d3:.10e}")

# Taylor expansion: δ(α*+Δα) ≈ δ + d1·Δα + d2/2·Δα² + ...
alpha_unc = ALPHA_REF * 0.3e-9  # CODATA 0.3 ppb
sigma_delta = abs(d1) * alpha_unc
print(f"\n  α* 不确定度 σ_α = {alpha_unc:.6e} (0.3 ppb)")
print(f"  δ 传播不确定度 σ_δ = |dδ/dα*|·σ_α = {sigma_delta:.6e}")
print(f"  δ 相对不确定度 σ_δ/δ = {sigma_delta/abs(DELTA):.6e}")

# Higher-order correction to σ_δ
sigma_delta_2nd = abs(d2) / 2 * alpha_unc**2
print(f"  二阶修正 = d²δ/dα*²/2·σ_α² = {sigma_delta_2nd:.6e} (可忽略)")

# Nonlinearity: how much does δ change if α* changes by 1%?
alpha_1pct = ALPHA_REF * 0.01
delta_at_plus = N_alg / (ALPHA_REF * 1.01) - C_alg
delta_at_minus = N_alg / (ALPHA_REF * 0.99) - C_alg
print(f"\n  α* ±1% 时:")
print(f"  δ(+1%) = {delta_at_plus:.10e} (变化 {(delta_at_plus-DELTA)/DELTA*100:.4f}%)")
print(f"  δ(-1%) = {delta_at_minus:.10e} (变化 {(delta_at_minus-DELTA)/DELTA*100:.4f}%)")
print(f"  → δ 对 α* 的弹性 ≈ -1（δ ∝ 1/α* 的线性近似）")
print(f"  → δ 和 α* 的相对变化量级相同（但符号相反）")

R["G2_sensitivity"] = {
    "d1_ddelta_dalpha": float(d1),
    "d2_d2delta_dalpha2": float(d2),
    "d3_d3delta_dalpha3": float(d3),
    "alpha_uncertainty": float(alpha_unc),
    "delta_uncertainty": float(sigma_delta),
    "delta_relative_uncertainty": float(sigma_delta / abs(DELTA)),
    "elasticity": "delta proportional to 1/alpha; relative changes of same magnitude, opposite sign",
}

# ════════════════════════════════════════════════════════════════
# G3 — 乘积/比值不变量
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("G3  乘积/比值不变量搜索")
print("=" * 78)

# δ×α* = N - C×α* = N - C×α*
prod = DELTA * ALPHA_REF
print(f"  δ×α* = {prod:.15e}")
print(f"  N - C×α* = {N_alg - C_alg * ALPHA_REF:.15e}")
print(f"  N = {N_alg:.15f}")
print(f"  C×α* = {C_alg * ALPHA_REF:.15e}")
print(f"  → δ×α* = N - C×α* ≈ {prod:.6e}")
print(f"  → δ×α* ≈ 3.17e-7, 不是简单量")

# But: δ×α* = N - gap(60,1)×C × (1+something)?
# Actually: δ×α* = N - C×α* = N - (N/(C+δ))×C = N×(1 - C/(C+δ)) = N×δ/(C+δ)
# So δ×α* = N×δ/(C+δ) → δ×α*×(C+δ) = N×δ → α*×(C+δ) = N (identity!)
print(f"\n  自洽检验: δ×α* = N×δ/(C+δ)?")
print(f"  N×δ/(C+δ) = {N_alg * DELTA / (C_alg + DELTA):.15e}")
print(f"  δ×α* = {prod:.15e}")
print(f"  → 恒等式（无新信息）")

# Check various combinations
combos = {
    "δ×α*": DELTA * ALPHA_REF,
    "δ/α*": DELTA / ALPHA_REF,
    "δ×α*²": DELTA * ALPHA_REF**2,
    "δ×137": DELTA * 137,
    "δ×137²": DELTA * 137**2,
    "δ×60²": DELTA * 60**2,
    "δ×60⁴": DELTA * 60**4,
    "δ×(C+1)": DELTA * (C_alg + 1),
    "δ×C": DELTA * C_alg,
    "δ/(1-x)": DELTA / (1 - x),
    "δ×(1-x)": DELTA * (1 - x),
    "δ×sin(π/30)²": DELTA * np.sin(np.pi/30)**2,
    "δ/sin(π/30)²": DELTA / np.sin(np.pi/30)**2,
    "δ×tan²(π/30)": DELTA * np.tan(np.pi/30)**2,
    "δ/tan²(π/30)": DELTA / np.tan(np.pi/30)**2,
    "δ×(n_α-60)": DELTA * (60.000436297 - 60),
}
print(f"\n  {'组合':>20} {'值':>16} {'log|值|':>10}")
for name, val in combos.items():
    if abs(val) > 1e-30:
        lv = np.log10(abs(val))
        marker = " ***" if abs(val - round(val)) < 0.01 and abs(val) > 0.1 else ""
        print(f"  {name:>20} {val:>16.10e} {lv:>10.4f}{marker}")

# Special: δ×60² = δ×3600
print(f"\n  δ×60² = {DELTA * 3600:.10f}")
print(f"  δ×60⁴ = {DELTA * 3600**2:.10f}")
print(f"  δ/tan²(π/30) = {DELTA / np.tan(np.pi/30)**2:.10e}")

# The key: δ = N/α* - C, so δ is determined by α* and algebraic constants
# δ×α* = N - C×α* which is NOT a constant (depends on α*)
# But: δ/(1/α*) = δ×α* = N - C×α* ≈ N - C/137 ≈ 0.0219 - 0.0219 ≈ 3e-7
# This near-zero is the "near-cancellation" again

R["G3_invariants"] = {
    "delta_times_alpha": float(DELTA * ALPHA_REF),
    "delta_times_137": float(DELTA * 137),
    "delta_times_60_sq": float(DELTA * 3600),
    "delta_over_tan_sq": float(DELTA / np.tan(np.pi/30)**2),
    "verdict": "no simple invariant found; delta*alpha = N - C*alpha is not constant; all relations reduce to gap=alpha identity"
}

# ════════════════════════════════════════════════════════════════
# G4 — gap(60,1)≈α* 的特殊性
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("G4  gap(n,1)≈α* 的特殊性：n=60 在分布中的位置")
print("=" * 78)

# Compute gap(n,1) for all even n in [8, 1000]
n_range = list(range(8, 1002, 2))
gaps_n1 = [gap_of(n, 1.0) for n in n_range]

# Find all n where gap(n,1) is within 1% of alpha
close_n = [(n, g, abs(g - ALPHA_REF)/ALPHA_REF) for n, g in zip(n_range, gaps_n1)
           if abs(g - ALPHA_REF)/ALPHA_REF < 0.01]
print(f"  n ∈ [8, 1000] 偶数中, gap(n,1) 在 α* 1% 以内的:")
for n_val, g_val, err in close_n:
    print(f"    n={n_val:>4}: gap={g_val:.10f}, 误差={err:.6e}")

# How many n give gap within 0.1%?
close_01 = [(n, g, abs(g - ALPHA_REF)/ALPHA_REF) for n, g in zip(n_range, gaps_n1)
            if abs(g - ALPHA_REF)/ALPHA_REF < 0.001]
print(f"\n  0.1% 以内: {len(close_01)} 个")
for n_val, g_val, err in close_01:
    print(f"    n={n_val:>4}: gap={g_val:.10f}, 误差={err:.6e}")

# gap(n,1) is a monotonically decreasing function for large n
# gap → 0 as n → ∞, and gap(8,1) = ?
print(f"\n  gap(n,1) 的极值:")
print(f"  gap(8,1) = {gap_of(8, 1.0):.10f} (最大)")
print(f"  gap(60,1) = {gap_of(60, 1.0):.10f} (≈α*)")
print(f"  gap(1000,1) = {gap_of(1000, 1.0):.10e} (→0)")

# The "density" of n values near alpha
# gap(n,1) ≈ 4π²/(3·n²) for large n (from F4/Tier1 refinement)
# So gap ≈ α* when n ≈ 2π/sqrt(3·α*) ≈ 2π/sqrt(0.0219) ≈ 2π/0.148 ≈ 42.5
# But actual n=60 gives the closest hit. Why?
n_approx = 2 * np.pi / np.sqrt(3 * ALPHA_REF)
print(f"\n  粗估: gap ≈ 4π²/(3n²) = α* → n ≈ {n_approx:.1f}")
print(f"  实际最佳: n=60 (偏差 {abs(60 - n_approx):.1f})")
print(f"  → 粗估给出 n≈42, 但精确公式给出 n_α=60.000436")
print(f"  → 差异来自 cos(2π/n) 项的修正（粗估忽略了它）")

# Distribution analysis: how many n give gap within X% of alpha for various X
for pct in [0.01, 0.1, 0.5, 1.0, 5.0]:
    count = sum(1 for g in gaps_n1 if abs(g - ALPHA_REF)/ALPHA_REF < pct/100)
    print(f"  {pct:.2f}% 窗口: {count} 个 n (密度 {count/len(n_range)*100:.2f}%)")

R["G4_gap_distribution"] = {
    "n_range": [8, 1000],
    "total_even_n": len(n_range),
    "within_1pct": len(close_n),
    "within_01pct": len(close_01),
    "n60_error": float(abs(gap_of(60, 1.0) - ALPHA_REF)/ALPHA_REF),
    "crude_estimate_n": float(n_approx),
    "verdict": "n=60 is the unique closest integer to n_alpha=60.000436; gap(n,1) density near alpha is ~0.2% (within 1%)"
}

# ════════════════════════════════════════════════════════════════
# G5 — 与其他物理常数的关联
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("G5  δ 与其他物理常数的关联")
print("=" * 78)

# Compare δ with ratios of fundamental constants
print(f"  δ = {DELTA:.10e}")
print(f"  α* = {ALPHA_REF:.10e}")
print(f"  m_p/m_e = {M_P_OVER_M_E:.6f}")
print(f"  G (无量纲) = {G_DIMLESS:.6e}")

# Check if δ has any relation to α* and m_p/m_e
# δ vs α*² × m_p/m_e?
test_combos = {
    "α*²": ALPHA_REF**2,
    "α*×(m_p/m_e)": ALPHA_REF * M_P_OVER_M_E,
    "α*/(m_p/m_e)": ALPHA_REF / M_P_OVER_M_E,
    "α*²×(m_p/m_e)": ALPHA_REF**2 * M_P_OVER_M_E,
    "1/(m_p/m_e)²": 1.0/M_P_OVER_M_E**2,
    "α*³": ALPHA_REF**3,
    "α*×137": ALPHA_REF * 137,
    "1/137²": 1.0/137**2,
    "α*²×137": ALPHA_REF**2 * 137,
    "α*/137": ALPHA_REF / 137,
}
print(f"\n  {'组合':>20} {'值':>16} {'δ/该值':>12}")
for name, val in test_combos.items():
    if abs(val) > 1e-50:
        ratio = DELTA / val
        marker = " ***" if abs(ratio - 1.0) < 0.05 else ""
        print(f"  {name:>20} {val:>16.10e} {ratio:>12.6f}{marker}")

# Check if δ × (m_p/m_e) is simple
print(f"\n  δ×(m_p/m_e) = {DELTA * M_P_OVER_M_E:.10e}")
print(f"  δ×(m_p/m_e)² = {DELTA * M_P_OVER_M_E**2:.10e}")
print(f"  → 无匹配")

# The proton-to-electron mass ratio in SRE context:
# In SRE, electron = soft mode (even k), proton = ?
# There's no direct SRE derivation of m_p/m_e
print(f"\n  SRE 框架内:")
print(f"  电子 = 偶模扇区（soft mode, 2π 闭合）")
print(f"  光子 = 奇模扇区（hard mode, 4π 闭合）")
print(f"  质子 = ？（SRE 未定义）")
print(f"  → δ 与 m_p/m_e 无 SRE 内在关联")

R["G5_other_constants"] = {
    "tested_combinations": {name: float(val) for name, val in test_combos.items()},
    "proton_electron_ratio": float(M_P_OVER_M_E),
    "verdict": "no match with any combination of alpha, m_p/m_e, or G; delta has no relation to other physical constants within SRE"
}

# ════════════════════════════════════════════════════════════════
# G6 — 预测力
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("G6  δ-α* 关系的预测力")
print("=" * 78)

# The relation α* = N/(C+δ) is exact by construction.
# Can it predict anything beyond α* itself?
# Answer: No, because δ is DEFINED as the value that makes gap=α*.
# The relation is a tautology: α* = N/(C+δ) where δ = N/α* - C.

# But: can we use the relation to predict α* from a DIFFERENT observable?
# If we could measure δ independently (without using α*), then α* = N/(C+δ) would be a prediction.
# But δ is currently only derivable through α* (A5 bare constant + alpha input).
# So the relation has zero predictive power for α*.

print(f"  δ-α* 关系: α* = N/(C+δ)")
print(f"  这是否具有预测力？")
print(f"\n  (a) 预测 α*？")
print(f"      δ 需 A5 + α* 输入才能确定 → 用 α* 预测 α*（循环论证）")
print(f"      → 无预测力")
print(f"\n  (b) 预测其他可观测量？")
print(f"      δ-α* 关系只涉及 N, C, δ, α* 四个量")
print(f"      N, C 是 n=60 的代数常数（已知）")
print(f"      δ 或 α* 之一必须是输入 → 无独立预测")
print(f"\n  (c) 预言 universality 表？")
print(f"      已在 Tier 0 Fork A §7.4 中预注册")
print(f"      gap(n, 1+δ_60) ≠ α*（n≠60）— 这是唯一预测")
print(f"      但这是 gap 公式的直接推论，不是 δ-α* 关系的新预测")

# However: the relation CAN be used to compute α* if we had an independent δ measurement
# This is the "falsifiability" angle: if an independent experiment measured δ,
# the relation would predict α* and could be cross-checked
print(f"\n  (d) 可证伪性:")
print(f"      若未来有独立实验测量'Z₂ 耦合不对称'（δ 的物理对应物）")
print(f"      则 α* = N/(C+δ_measured) 可作为交叉验证")
print(f"      但当前无独立 δ 测量途径 → 可证伪但不可验证")

R["G6_predictive_power"] = {
    "predict_alpha": "circular (delta requires alpha input)",
    "predict_other": "no other observable; relation only involves N, C, delta, alpha",
    "universality_table": "already pre-registered in Fork A 7.4; gap(n,1+delta_60) != alpha for n!=60",
    "falsifiability": "if independent delta measurement exists, alpha=N/(C+delta) is cross-checkable; currently no independent measurement",
    "verdict": "delta-alpha relation has zero predictive power (tautology by construction); falsifiable in principle but not testable currently"
}

# ════════════════════════════════════════════════════════════════
# G7 — 记分卡 + 终局判定
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("G7  Tier 1 第 9 项记分卡 + δ-α* 关系终局")
print("=" * 78)

print(f"""
  G1  精确函数关系       INFO  α*(C+δ)=N 是 gap=α* 的线性代数重排（无新信息）
  G2  灵敏度分析         PASS  dδ/dα*=-(C+δ)/α*≈-410; σ_δ/δ≈1.0e-5
  G3  乘积/比值不变量     FAIL  无简单不变量（δ×α*=N-C×α* 非常数）
  G4  gap(n,1)≈α* 特殊性 INFO  n=60 是 n_α=60.000436 的唯一最近整数（0.2% 密度）
  G5  其他物理常数        FAIL  无匹配（δ 与 m_p/m_e, G 等无关联）
  G6  预测力             FAIL  δ-α* 是构造性的恒等式，零预测力（可证伪但不可验证）

  ═══ δ-α* 关系终局判定 ═══

  数学结构:
    α* × (2 + cos(π/30) + δ) = 2sin²(π/30)
    线性关系，δ 是 α* 的有理函数（δ = N/α* - C）

  物理意义:
    δ 是 gap(60,1) ≈ α* 的离散化修正
    n=60 是 n_α=60.000436 的最近偶整数
    δ 补偿 gap(60,1) 与 α* 的差（~1.45e-5 相对偏差）

  信息含量:
    δ-α* 关系是 gap 公式的重排，不携带超越 gap=α* 的新信息
    δ 的精确值需要 α* 作为输入（A5 裸公理）
    δ 无法独立预测 α*（循环论证）

  可证伪性:
    若有独立 δ 测量 → α* = N/(C+δ) 可交叉验证
    当前无独立测量途径 → 可证伪但不可验证

  结论:
    δ-α* 的数值关联是 SRE 框架内 gap=α* 的代数重排，
    不产生超越已知结构的新信息或新预测。
    δ 的独立信息含量 = 0（相对于 α*），
    但 ≠ 0（相对于拓扑：Z₂ 分级耦合常数）。
""")

R["G7_scorecard"] = {
    "G1_exact_relation": "INFO: linear rearrangement of gap=alpha, no new info",
    "G2_sensitivity": "PASS: d_delta/d_alpha = -(C+delta)/alpha, sigma_delta/delta ~ 1e-5",
    "G3_invariants": "FAIL: no simple invariant found",
    "G4_gap_speciality": "INFO: n=60 is nearest integer to n_alpha=60.000436",
    "G5_other_constants": "FAIL: no match with m_p/m_e, G, etc.",
    "G6_predictive_power": "FAIL: tautology by construction, zero predictive power",
    "final_verdict": {
        "mathematical": "alpha*(C+delta)=N is linear rearrangement of gap=alpha",
        "physical": "delta is discretization correction for n=60 vs n_alpha=60.000436",
        "information": "delta-alpha relation carries zero info beyond gap=alpha; delta's independent info is purely topological (Z2 grading)",
        "falsifiability": "falsifiable in principle (independent delta measurement) but not testable currently",
    }
}

out = os.path.join(os.path.dirname(__file__), "tier1_delta_alpha_correlation_results.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2, cls=NpEncoder)
print(f"结果已写入 {out}")
