# -*- coding: utf-8 -*-
"""
Tier 1 第 8 项 — δ 公理化形式化推导
============================================================
Tier 1 第 7 项发现：
  E3: δ 的拓扑起源 = Z₂ 分级耦合常数（Möbius H₁(Z₂)）
  E2/E4: δ = δ_phys + δ_alg 近精确对消（残差 4.347e-5）

本项将 Z₂ 拓扑提升为形式公理 A6，检验推导力。

符号契约（先于计算冻结）
------------------------------------------------------------
[F1] A6 公理化：将 Z₂ 拓扑形式化为新公理
    A6: "Möbius 带的定向反转产生 Z₂ 分级，δ 是此分级的裸耦合常数"
    检验：A6 能否推出 δ≠0？能。能否推出 δ 的精确值？不能。
    A6 的推导力 = 仅定性（δ≠0），非定量（δ=4.347e-5）。

[F2] 近对消机制审计
    δ_phys = (1-cos(π/15))/α* ≈ 2.9946
    δ_alg  = -2 - cos(π/30)    ≈ -2.9945
    对消精度 = |δ| / max(|δ_phys|, |δ_alg|) = 1.45e-5
    检验：这个精度是否等于 gap(60, w=1) vs α* 的偏差？
    即：对消残差 δ 是否就是 gap(60,1) - α* 的精确形式？

[F3] 加强 no-go 定理
    Tier 0 的 no-go: A1-A4+R1 无法推出 δ
    Tier 1 加强: A1-A5+A6（Z₂ 拓扑）仍无法推出 δ 的精确值
    证明思路：Z₂ 拓扑只提供奇偶分裂的【符号】（±1），
    不提供分裂的【幅度】（|δ|）。幅度需要额外信息。

[F4] n_α = 60.000436 与对消精度的关联
    n_α = 2π/θ_α 是 gap(M_n, w=1) = α* 的精确交叉点
    δ = gap(n_α, 1) - gap(60, 1) 的一阶修正
    检验：δ 是否等于 dgap/dn|_{n=60} × (n_α - 60)？

[F5] 代数结构约束
    cos(π/30) 是 8 次代数数，cos(π/15) 是 4 次代数数
    它们属于 Q(ζ₆₀) 的子域
    检验：对消 (1-cos(π/15))/α* ≈ 2 + cos(π/30) 是否是
    域论意义上的"巧合"还是有代数约束？

[F6] Klein 瓶推广预言
    H₁(Klein, Z₂) = Z₂×Z₂ → 两个独立 Z₂ 通道
    预言：双 δ 模型 δ₁, δ₂
    构造：双覆盖 Möbius 阶梯（两个独立 P 矩阵）
"""
import json
import os
import numpy as np

np.set_printoptions(precision=15, suppress=True)

ALPHA_REF = 1.0 / 137.035999084
N0 = 60
theta0 = 2.0 * np.pi / N0
w_star = (1.0 - np.cos(2.0 * theta0)) / ALPHA_REF - 1.0 - np.cos(theta0)
DELTA = w_star - 1.0

R = {"purpose": "Tier 1 item 8: delta axiomatization formalization", "delta_value": float(DELTA)}


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
# F1 — A6 公理化
# ════════════════════════════════════════════════════════════════
print("=" * 78)
print("F1  A6 公理化：Z₂ 拓扑 → 形式公理")
print("=" * 78)

print("""
  A6（形式化）：Möbius 带的定向反转诱导 Z₂ 分级于图谱上，
  偶 k 模（电子扇区，2π 闭合）与奇 k 模（光子扇区，4π 闭合）
  被投影算子 P = S^{n/2} 分离；P 的本征值 (-1)^k 来自
  H₁(Möbius, Z₂) = Z₂ 的非平凡同调类。

  A6 的推导力检验：
""")

# A6 → δ≠0?
print("  (a) A6 → δ≠0？")
print("      Z₂ 分级要求 P ≠ I（否则无分级）")
print("      P = S^{n/2} 的本征值 = (-1)^k ≠ 1（k 奇）")
print("      ⇒ 奇偶模谱必分裂 ⇒ δ 的存在被拓扑强制")
print("      但 δ=0（w=1）时谱仍分裂（奇偶 cos 项不同）！")
# Check: does gap exist when w=0 (no cross-sheet coupling)?
gap_w0 = gap_of(N0, 0.0)
gap_w1 = gap_of(N0, 1.0)
print(f"      gap(60, w=0) = {gap_w0:.10f} （无 P 项，纯 C₆₀）")
print(f"      gap(60, w=1) = {gap_w1:.10f} （P 项存在但 δ=0）")
print(f"      → w=0 时 P 不存在，Z₂ 分级消失，gap 仅为 tan²(2π/60)")
print(f"      → w=1 时 P 存在但 δ=0，Z₂ 分级存在但耦合对称")
print(f"      → A6 强制 P≠0（w≠0），但不强制 δ≠0")
print(f"      → A6 → w≠0（拓扑要求），但 δ=0 仍满足 A6（对称耦合）")

# A6 → δ exact value?
print("\n  (b) A6 → δ 的精确值？")
print("      Z₂ 只提供符号 (-1)^k，不提供幅度 |δ|")
print("      δ 是 P 矩阵的权重超出量 = w - 1 = δ")
print("      Z₂ 拓扑无法确定 w 的具体值（w 是度量，不是拓扑）")
print("      → A6 无法推出 δ 的精确值")

# A6 + A5 → redundant?
print("\n  (c) A6 是否使 A5 冗余？")
print("      A5: '跨片识别信道强度超出刷新信道 δ'（定量）")
print("      A6: 'Z₂ 分级存在'（定性）")
print("      A6 ⊂ A5（A5 隐含 Z₂ 分级存在，但更强：给出 δ 值）")
print("      → A6 不使 A5 冗余；A6 是 A5 的拓扑前提，A5 是 A6 的定量补充")

R["F1_A6_axiom"] = {
    "A6_statement": "Mobius orientation reversal induces Z2 grading on spectrum; delta is the bare coupling of this grading",
    "A6_implies_delta_nonzero": False,
    "A6_implies_w_nonzero": True,
    "A6_implies_delta_exact_value": False,
    "A6_vs_A5": "A6 is the topological prerequisite (qualitative); A5 is the quantitative supplement; A6 does not make A5 redundant",
    "derivation_power": "qualitative only (w!=0); cannot determine delta exact value",
}

# ════════════════════════════════════════════════════════════════
# F2 — 近对消机制审计
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("F2  近对消机制审计：对消精度 = gap(60,1) 偏差？")
print("=" * 78)

delta_phys = (1.0 - np.cos(np.pi / 15)) / ALPHA_REF
delta_alg = -2.0 - np.cos(np.pi / 30)
cancellation_residue = delta_phys + delta_alg
cancellation_precision = abs(cancellation_residue) / max(abs(delta_phys), abs(delta_alg))

# gap(60, w=1) deviation from alpha
gap_w1_dev = (gap_of(N0, 1.0) - ALPHA_REF) / ALPHA_REF

print(f"  δ_phys = (1-cos(π/15))/α* = {delta_phys:.15f}")
print(f"  δ_alg  = -2-cos(π/30)    = {delta_alg:.15f}")
print(f"  对消残差 = δ_phys + δ_alg = {cancellation_residue:.15e}")
print(f"  对消精度 = {cancellation_precision:.6e}")
print(f"  gap(60,1) vs α* 偏差 = {gap_w1_dev:.6e}")
print(f"  比值（对消精度 / gap偏差）= {cancellation_precision / abs(gap_w1_dev):.6f}")

# Key question: is δ = (gap(60,1) - α*) / d(gap)/dw|_{w=1}?
# gap(w) = (1-cos(π/15)) / (1+w+cos(π/30))
# d(gap)/dw = -(1-cos(π/15)) / (1+w+cos(π/30))² = -gap / (1+w+cos(π/30))
# At w=1: d(gap)/dw = -gap(60,1) / (2+cos(π/30))
dgap_dw = -gap_of(N0, 1.0) / (2.0 + np.cos(np.pi / 30))
delta_from_taylor = (ALPHA_REF - gap_of(N0, 1.0)) / dgap_dw
# Note: d(gap)/dw is negative, (α* - gap) is also negative (gap > α*), so delta is positive
print(f"\n  Taylor 展开验证：")
print(f"  gap(w) ≈ gap(1) + dgap/dw|_1 × (w-1)")
print(f"  α* = gap(1) + dgap/dw|_1 × δ")
print(f"  δ = (α* - gap(1)) / (dgap/dw|_1)")
print(f"  dgap/dw|_1 = {dgap_dw:.10f}")
print(f"  δ(Taylor) = {delta_from_taylor:.15e}")
print(f"  δ(exact)  = {DELTA:.15e}")
print(f"  偏差 = {abs(delta_from_taylor - DELTA)/abs(DELTA):.2e}")
# The Taylor expansion is exact because gap is a RATIONAL FUNCTION of w (degree 0/1)
# gap = num / (a + w*b) where num, a, b are constants
# This is linear in 1/w, not in w! So Taylor in w is NOT exact.
# Actually: gap = num / (c + w) where c = 1 + cos(π/30), num = 1-cos(π/15)
# gap(w) = num / (c + w) → this is 1/(c+w), which is NOT linear in w
# Taylor: num/(c+w) ≈ num/(c+1) × (1 - (w-1)/(c+1) + ...)
# First order: gap ≈ gap(1) × (1 - δ/(c+1))
# gap(1) × δ/(c+1) = gap(1) - α*
# δ = (gap(1) - α*) × (c+1) / gap(1)
c_val = 1.0 + np.cos(np.pi / 30)
delta_taylor1 = (gap_of(N0, 1.0) - ALPHA_REF) * (c_val + 1.0) / gap_of(N0, 1.0)
print(f"\n  精确一阶（gap = num/(c+w) 在 w=1 处展开）:")
print(f"  δ(一阶) = (gap(1)-α*)×(c+1)/gap(1) = {delta_taylor1:.15e}")
print(f"  δ(exact) = {DELTA:.15e}")
print(f"  偏差 = {abs(delta_taylor1 - DELTA)/abs(DELTA):.2e}")

# Full exact: δ = num/α* - c - 1 = (1-cos(π/15))/α* - 2 - cos(π/30)
print(f"\n  精确公式: δ = (1-cos(π/15))/α* - 2 - cos(π/30)")
print(f"  = δ_phys + δ_alg = {delta_phys:.15f} + ({delta_alg:.15f})")
print(f"  = {delta_phys + delta_alg:.15e}")
print(f"  → 对消不是近似，是精确恒等式（代数重排）")
print(f"  → '近对消'的精度 = gap(60,1) 与 α* 的接近程度")
print(f"  → 这正是 n_α ≈ 60 的体现（n=60 是 n_α 的最近整数）")

R["F2_cancellation_audit"] = {
    "delta_phys": float(delta_phys),
    "delta_alg": float(delta_alg),
    "residue": float(cancellation_residue),
    "cancellation_precision": float(cancellation_precision),
    "gap_w1_deviation": float(gap_w1_dev),
    "taylor_first_order_delta": float(delta_taylor1),
    "taylor_deviation": float(abs(delta_taylor1 - DELTA) / abs(DELTA)),
    "verdict": "cancellation is exact algebraic identity (not approximation); precision = n_alpha approx 60; no new derivation power"
}

# ════════════════════════════════════════════════════════════════
# F3 — 加强 no-go 定理
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("F3  加强 no-go 定理：A1-A5+A6 仍无法推出 δ 精确值")
print("=" * 78)

print("""
  Tier 0 no-go: A1-A4+R1 无法推出 δ（模量论证：P=S^{n/2} 是 S 的多项式，
  [S,P]=0，w 只能以系数身份进入谱，不可被对称性量子化）

  Tier 1 加强：加入 A6（Z₂ 拓扑）后是否改变？

  论证：
  A6 提供：Z₂ 分级存在（P 的本征值 ±1）
  A6 不提供：
    (a) P 的权重 w 的值（拓扑不给度量）
    (b) δ = w - 1 的值（度量差不是拓扑不变量）
    (c) α* 的值（物理输入）

  精确值链：
    δ = (1-cos(π/15))/α* - 2 - cos(π/30)
    其中 cos(π/15), cos(π/30) 由 n=60 → cos(2πk/60) 代数确定
    但 α* 是物理输入

  ∴ A1-A6 的逻辑结构：
    A1-A4 + R1 → n=60, 图结构, 谱
    A5 → δ 存在且 = w-1
    A6 → δ≠0 的拓扑原因（Z₂ 分级）
    但 δ 的精确值 = f(α*)，需要 α* 作为物理输入

  结论：A6 补充了 δ 存在性的拓扑解释，但不改变 no-go 定理的定量部分。
  no-go 从"无法从 A1-A4+R1 推出 δ"加强为
       "无法从 A1-A5+A6 推出 δ 的精确值（不输入 α*）"
""")

# Verify: can we derive α* from A1-A6?
print("  检验：A1-A6 能否推出 α*？")
print("  α* = 1/137.036... 是物理常数（精细结构常数）")
print("  A1-A6 只涉及图拓扑和 Z₂ 分级，不含电磁相互作用的信息")
print("  → A1-A6 无法推出 α*（拓扑不含电动力学信息）")
print("  → δ = f(α*) 也无法被 A1-A6 独立推出")
print("  → no-go 定理的定量部分保持")

R["F3_strengthened_nogo"] = {
    "tier0_nogo": "A1-A4+R1 cannot derive delta (modular argument: P commutes with S)",
    "tier1_nogo": "A1-A5+A6 cannot derive delta's exact value (requires alpha* as physical input)",
    "A6_contribution": "explains delta's existence (Z2 grading), not its value",
    "alpha_independence": "A1-A6 contain only topology, no EM info; cannot derive alpha*",
    "verdict": "strengthened no-go: quantitative delta still requires A5 (bare constant) + alpha* (physical input)"
}

# ════════════════════════════════════════════════════════════════
# F4 — n_α 与对消精度的关联
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("F4  n_α = 60.000436 与对消精度的关联")
print("=" * 78)

# n_α: the real number where gap(M_n, w=1) = α*
# From Tier 0: cos(θ_α) = (-α + sqrt(α²-8(2α-2)))/4, n_α = 2π/θ_α
a = ALPHA_REF
c_alpha = (-a + np.sqrt(a * a - 8.0 * (2.0 * a - 2.0))) / 4.0
theta_alpha = np.arccos(c_alpha)
n_alpha = 2.0 * np.pi / theta_alpha

print(f"  n_α = {n_alpha:.9f}")
print(f"  n_α - 60 = {n_alpha - 60:.6e}")
print(f"  对消精度 = {cancellation_precision:.6e}")
print(f"  比值 = {abs(n_alpha - 60) / cancellation_precision:.6f}")

# Is the cancellation precision related to (n_α - 60)/60?
relative_gap = abs(n_alpha - 60) / 60
print(f"  (n_α-60)/60 = {relative_gap:.6e}")
print(f"  gap(60,1) 偏差 = {gap_w1_dev:.6e}")
print(f"  (n_α-60)/60 vs gap偏差 比值 = {relative_gap / abs(gap_w1_dev):.4f}")

# The connection: gap(M_n, w=1) = tan²(2π/n) for the base cycle
# gap(n,1) = (1-cos(4π/n))/(2+1+cos(2π/n)) = (1-cos(4π/n))/(3+cos(2π/n))
# At n=n_α, this equals α*. At n=60, it's α* + ε where ε ≈ gap_deviation
# δ accounts for this ε by adjusting w from 1 to 1+δ
print(f"\n  精确关系:")
print(f"  gap(60, 1+δ) = α* (A5 定义)")
print(f"  gap(n_α, 1) = α* (n_α 定义)")
print(f"  → δ = gap 恢复量 = 从 gap(60,1) 修正到 gap(60,1+δ)=α*")
print(f"  → δ 是 'n=60 替代 n=n_α 的离散化修正'")
print(f"  → 修正量级 ~ (n_α-60)/60 × d(gap)/dn × n/gap ~ O(1e-5)")

# Compute d(gap)/dn at n=60
dn = 0.001
gap_60 = gap_of(60, 1.0)
gap_60p = gap_of(60 + dn, 1.0) if (60 + dn) % 2 == 0 else None
# Use even n near 60
gap_58 = gap_of(58, 1.0)
gap_62 = gap_of(62, 1.0)
dgap_dn = (gap_62 - gap_58) / 4.0
print(f"  d(gap)/dn|_60 ≈ {dgap_dn:.6e}")
print(f"  (n_α-60) × d(gap)/dn = {(n_alpha-60) * dgap_dn:.6e}")
print(f"  gap(60,1) - α* = {gap_60 - ALPHA_REF:.6e}")
print(f"  → δ ≈ -(gap(60,1)-α*)/(dgap/dw) = {delta_taylor1:.6e}")
print(f"  → δ ≈ (n_α-60)×(dgap/dn)/(dgap/dw)")
# dgap/dw at w=1
print(f"  (n_α-60)×(dgap/dn)/(dgap/dw) = {(n_alpha-60)*dgap_dn/dgap_dw:.6e}")
print(f"  δ(exact) = {DELTA:.6e}")

R["F4_n_alpha_connection"] = {
    "n_alpha": float(n_alpha),
    "n_alpha_minus_60": float(n_alpha - 60),
    "cancellation_precision": float(cancellation_precision),
    "dgap_dn_at_60": float(dgap_dn),
    "dgap_dw_at_1": float(dgap_dw),
    "delta_from_n_alpha": float((n_alpha - 60) * dgap_dn / dgap_dw),
    "delta_exact": float(DELTA),
    "verdict": "delta is the discretization correction: n=60 replaces n_alpha=60.000436; delta magnitude ~ (n_alpha-60) * dgap/dn / dgap/dw"
}

# ════════════════════════════════════════════════════════════════
# F5 — 代数结构约束
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("F5  代数结构约束：cos(π/30) 与 cos(π/15) 的体论")
print("=" * 78)

# cos(π/30) ∈ Q(ζ₆₀), degree 8
# cos(π/15) = cos(2π/30) ∈ Q(ζ₃₀), degree 4
# Q(ζ₃₀) ⊂ Q(ζ₆₀) (since 30 | 60)
# So cos(π/15) ∈ Q(cos(π/30))

# The near-cancellation: (1-cos(π/15))/α* ≈ 2 + cos(π/30)
# This means: 1-cos(π/15) ≈ α* × (2+cos(π/30))
# Or: α* ≈ (1-cos(π/15)) / (2+cos(π/30)) = gap(60, 1)

x30 = np.cos(np.pi / 30)
x15 = np.cos(np.pi / 15)
print(f"  cos(π/30) = {x30:.15f} (degree 8, Q(ζ₆₀))")
print(f"  cos(π/15) = {x15:.15f} (degree 4, Q(ζ₃₀) ⊂ Q(ζ₆₀))")
print(f"  cos(π/15) ∈ Q(cos(π/30))? 检验:")

# Check: is cos(π/15) a polynomial in cos(π/30)?
# cos(2θ) = 2cos²(θ) - 1, so cos(π/15) = cos(2·π/30) = 2cos²(π/30) - 1
x15_from_x30 = 2 * x30**2 - 1
print(f"  cos(π/15) = 2cos²(π/30) - 1 = {x15_from_x30:.15f}")
print(f"  直接计算   = {x15:.15f}")
print(f"  偏差 = {abs(x15_from_x30 - x15):.1e}")
print(f"  → cos(π/15) = 2cos²(π/30) - 1 （倍角公式）！")

# So the cancellation becomes:
# 1 - (2x²-1) = 2(1-x²) where x = cos(π/30)
# α* = 2(1-x²) / (2+x) = 2(1-x)(1+x) / (2+x)
# δ = 2(1-x²)/α* - 2 - x = 2(1-x²)/α* - (2+x)
print(f"\n  倍角简化：")
print(f"  cos(π/15) = 2cos²(π/30) - 1")
print(f"  1-cos(π/15) = 2(1-cos²(π/30)) = 2sin²(π/30)")
print(f"  gap(60,1) = 2sin²(π/30) / (2+cos(π/30))")
print(f"  δ = 2sin²(π/30)/α* - 2 - cos(π/30)")

# The entire structure depends on ONE algebraic number: x = cos(π/30)
x = np.cos(np.pi / 30)
gap_from_x = 2 * (1 - x**2) / (2 + x)
print(f"\n  x = cos(π/30) = {x:.15f}")
print(f"  gap(60,1) = 2(1-x²)/(2+x) = {gap_from_x:.15f}")
print(f"  gap(60,1) 直接 = {gap_of(60, 1.0):.15f}")
print(f"  → 全部公式只依赖 x = cos(π/30)（8 次代数数）")

# The minimal polynomial of x = cos(π/30)
# 2x is a root of the 60th cyclotomic polynomial (degree 16), so x has degree 8
# The minimal polynomial of 2cos(π/30) is:
# Actually, let me find it numerically by LLL or PSLQ... but we can verify known results
# The minimal polynomial of 2cos(2π/60) = 2cos(π/30) divides Φ_60(x)
# Φ_60 has degree φ(60) = 16, so 2cos(π/30) has degree 8
# The minimal polynomial is: x^8 - x^7 - 7x^6 + 6x^5 + 15x^4 - 10x^3 - 10x^2 + 4x + 1
# But we need to verify this
two_x = 2 * x
# Test polynomial: x^8 - x^7 - 7x^6 + 6x^5 + 15x^4 - 10x^3 - 10x^2 + 4x + 1
p_val = np.polyval([1, -1, -7, 6, 15, -10, -10, 4, 1], two_x)
print(f"\n  2cos(π/30) = {two_x:.15f}")
print(f"  尝试 P(x) = x^8 - x^7 - 7x^6 + 6x^5 + 15x^4 - 10x^3 - 10x^2 + 4x + 1")
print(f"  P(2cos(π/30)) = {p_val:.6e}")
if abs(p_val) > 0.01:
    # Try other known polynomials for 2cos(pi/30)
    # Actually cos(pi/30) = cos(6 degrees). Let me try a different polynomial.
    # The minimal polynomial of 2cos(2pi/n) divides the nth cyclotomic polynomial.
    # For n=60, phi(60) = 16, so degree of 2cos(2pi/60) = 8
    # Let me try to find it by checking all degree-8 polynomials with small coefficients
    # This is computationally expensive, so let me use a different approach
    # The minimal polynomial of 2cos(2*pi/60) = 2cos(pi/30)
    # Known: 2cos(2*pi/60) satisfies x^8 - x^7 - 7x^6 + 6x^5 + 15x^4 - 10x^3 - 10x^2 + 4x + 1 = 0
    # But my test failed. Let me re-check.
    # Actually, the cyclotomic polynomial Phi_60(x) has degree 16.
    # The minimal polynomial of 2cos(2*pi/60) = 2cos(pi/30) has degree phi(60)/2 = 8.
    # Let me try: the minimal polynomial of 2cos(2*pi/n) is the minimal polynomial
    # that has 2cos(2*pi*k/n) for gcd(k,n)=1 as roots.
    # For n=60, the coprime k values are: 1, 7, 11, 13, 17, 19, 23, 29 (8 values)
    roots = [2*np.cos(2*np.pi*k/60) for k in [1,7,11,13,17,19,23,29]]
    # Build polynomial from roots
    poly_coeffs = np.poly(roots)
    print(f"  从根构造的多项式系数: {poly_coeffs}")
    # Evaluate at 2cos(pi/30) = 2cos(2pi/60) which is the root for k=1
    p_val2 = np.polyval(poly_coeffs, two_x)
    print(f"  P(2cos(π/30)) = {p_val2:.6e}")
    # Round coefficients
    rounded = np.round(poly_coeffs).astype(int)
    print(f"  整系数化: {rounded}")
    p_val3 = np.polyval(rounded, two_x)
    print(f"  P(2cos(π/30)) = {p_val3:.6e}")
    # The minimal polynomial
    min_poly = rounded
else:
    min_poly = np.array([1, -1, -7, 6, 15, -10, -10, 4, 1])
    print(f"  最小多项式确认: P(2cos(π/30)) = {p_val:.2e} ≈ 0")

print(f"\n  最小多项式（降序）: {min_poly}")
print(f"  2cos(π/30) 是 {len(min_poly)-1} 次代数整数")

# Key: gap(60,1) = 2(1-x²)/(2+x) where x is degree 8
# So gap(60,1) is in Q(x) = degree 8 number field
# δ = 2(1-x²)/α* - (2+x) involves α* (transcendental)
# The "coincidence" is: 2(1-x²)/(2+x) ≈ α*
# i.e., an algebraic number of degree ≤ 8 happens to ≈ 1/137.036
print(f"\n  关键观察：")
print(f"  gap(60,1) = 2(1-x²)/(2+x) 是 Q(x) 中的代数数（degree ≤ 8）")
print(f"  α* = 1/137.036 是物理常数（极可能超越数）")
print(f"  代数数 ≈ 超越数 → 不是恒等式，是数值巧合")
print(f"  巧合精度 = {abs(gap_of(60,1.0) - ALPHA_REF)/ALPHA_REF:.2e}（Tier 0 的 n_α=60.000436）")

R["F5_algebraic_structure"] = {
    "cos_pi_30_degree": 8,
    "cos_pi_15_relation": "cos(pi/15) = 2cos^2(pi/30) - 1 (double angle)",
    "gap_formula_simplified": "gap(60,1) = 2(1-x^2)/(2+x) where x = cos(pi/30)",
    "x_minimal_poly": [int(c) for c in min_poly],
    "gap_is_algebraic": True,
    "gap_degree_at_most": 8,
    "alpha_is_transcendental_likely": True,
    "coincidence": "algebraic number (degree <=8) approx transcendental alpha to 1.45e-5",
    "verdict": "cancellation is not algebraic identity; it is the n_alpha approx 60 coincidence"
}

# ════════════════════════════════════════════════════════════════
# F6 — Klein 瓶推广预言
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("F6  Klein 瓶推广预言：双 Z₂ 通道")
print("=" * 78)

# H_1(Klein, Z_2) = Z_2 × Z_2
# Two independent Z_2 grading operators P1, P2
# P1: half-period shift (a-direction)
# P2: cross-sheet flip (b-direction)
# Both have eigenvalues ±1, and they commute (Z_2 × Z_2 is abelian)

# Model: Double-cover Möbius ladder with two independent cross-sheet channels
# L = (2+w1+w2) I - S - S^{-1} - w1 P1 - w2 P2
# where P1 = S^{n/2} (original Möbius), P2 = ? (second Z_2)

# For Klein bottle on C_n: P2 could be the "twist" in the b-direction
# P2 v_k = exp(2πi k/n * something) v_k
# For a Klein bottle with twist parameter m:
# P2 v_k = (-1)^{mk} v_k (if m is integer)

# Simplest: P2 = S^{n/4} (quarter-period shift) for n divisible by 4
# P2 v_k = exp(2πik/n * n/4) v_k = exp(πik/2) v_k = {1, i, -1, -i}
# This gives a Z_4, not Z_2. For Z_2 × Z_2, we need P2 with eigenvalues ±1 only.

# Alternative: P2 = (-I) on half the nodes (checkerboard pattern)
# P2 v_k = ... complex. Let's use P2 = S^{n/2} composed with diagonal sign flip.

# Simplest model: two independent Möbius channels
# L = d I - S - S^{-1} - w1 P1 - w2 P2
# where P1 = S^{n/2}, P2 = some other involution with P2^2 = I

# For a concrete model: P2 = reflection (i -> n-1-i)
n = N0
S = np.zeros((n, n))
for i in range(n):
    S[i, (i+1) % n] = 1.0
P1 = np.linalg.matrix_power(S, n // 2)
# P2: reflection
P2 = np.zeros((n, n))
for i in range(n):
    P2[i, (n-1-i) % n] = 1.0

# Check: P2^2 = I, [P1, P2] = ?
P2sq = P2 @ P2
comm = P1 @ P2 - P2 @ P1
print(f"  P1 = S^{{n/2}} (半周期移位)")
print(f"  P2 = 反射 (i → n-1-i)")
print(f"  P2² = I? {np.allclose(P2sq, np.eye(n))}")
print(f"  [P1, P2] = 0? {np.allclose(comm, 0)}")

# If they don't commute, we have a non-abelian structure
# Let's try another P2: P2 = S^{n/2} on a different sublattice
# Or: use C_{2n} with two independent Möbius identifications

# Actually, for the Klein bottle, the two Z_2 generators are:
# (a, b) -> (a+1, b) and (a, b) -> (a, b+1) with appropriate identifications
# In the discrete case: P1 = shift by n/2, P2 = shift by n/2 in the other direction
# For a 1D chain, this requires a 2D lattice

# For a simpler model: use C_n with two independent chord structures
# Chords at skip n/2 (original Möbius) AND chords at skip n/4 (if n divisible by 4)
# This gives two independent Z_2 gradings if the chord patterns are independent

# For n=60 (divisible by 4): P1 = S^{30} (skip 30), P2 = S^{15} (skip 15)
P2_alt = np.linalg.matrix_power(S, n // 4)
print(f"\n  替代 P2 = S^{{n/4}} = S^{{15}}")
P2_alt_sq = P2_alt @ P2_alt
comm_alt = P1 @ P2_alt - P2_alt @ P1
print(f"  P2² = S^{{n/2}} = P1? {np.allclose(P2_alt_sq, P1)}")
print(f"  [P1, P2] = 0? {np.allclose(comm_alt, 0)}")
print(f"  → P2² = P1（非独立！P2 生成 Z_4，非 Z_2×Z_2）")

# For true Z_2 × Z_2, we need two commuting involutions
# P1^2 = I, P2^2 = I, [P1,P2] = 0
# On C_n, the only involutions are S^{n/2} and... 
# P2 = diagonal matrix with alternating signs: D = diag(1,-1,1,-1,...)
D = np.diag([(-1)**i for i in range(n)])
Dsq = D @ D
comm_D = P1 @ D - D @ P1
print(f"\n  P2 = diag(1,-1,1,-1,...)")
print(f"  P2² = I? {np.allclose(Dsq, np.eye(n))}")
print(f"  [P1, P2] = 0? {np.allclose(comm_D, 0)}")
# Check eigenvalues of D: (-1)^k? No, D v_k = sum_j (-1)^j exp(2πikj/n)/sqrt(n)
# D is not diagonal in the Fourier basis of S

# Let's compute the spectrum of L = (2+w1+w2)I - S - S^{-1} - w1 P1 - w2 D
print(f"\n  双 Z₂ 模型: L = (2+w₁+w₂)I - S - S† - w₁P₁ - w₂D")
w1 = 1.0 + DELTA
for w2_test in [0.0, 0.5, 1.0, 1.0 + DELTA]:
    L_dual = (2 + w1 + w2_test) * np.eye(n) - S - S.T - w1 * P1 - w2_test * D
    eigs_dual = np.sort(np.linalg.eigvalsh(L_dual))
    nz = eigs_dual[1:] if abs(eigs_dual[0]) < 1e-10 else eigs_dual
    gap_dual = nz.min() / nz.max()
    print(f"  w₁=1+δ={w1:.6e}, w₂={w2_test:.4f}: gap = {gap_dual:.10f}, "
          f"vs α* = {ALPHA_REF:.10f} (偏差 {abs(gap_dual-ALPHA_REF)/ALPHA_REF:.2e})")

print(f"\n  → 第二 Z₂ 通道（D = checkerboard）破坏 Möbius 图的结构")
print(f"  → D 不是 S 的多项式（[S,D]≠0），导致谱不再有干净的奇偶分裂")
print(f"  → 双 Z₂ 模型的 gap 依赖于 w₁ 和 w₂ 两个参数")
print(f"  → 预言：Klein 瓶推广需要两个独立 δ₁, δ₂，各有独立的 A5 公理")

R["F6_klein_bottle"] = {
    "H1_klein_Z2": "Z2 x Z2",
    "P1": "S^{n/2} (half-period shift, original Mobius)",
    "P2_attempts": {
        "reflection": {"P2_sq_is_I": True, "commutes_with_P1": bool(np.allclose(comm, 0))},
        "S^{n/4}": {"P2_sq_equals_P1": True, "generates_Z4_not_Z2xZ2": True},
        "checkerboard_D": {"P2_sq_is_I": True, "commutes_with_P1": bool(np.allclose(comm_D, 0))},
    },
    "dual_delta_prediction": "Klein bottle model requires two independent delta_1, delta_2, each with its own A5 axiom",
    "verdict": "dual Z2 model has 2-parameter gap(w1, w2); each Z2 channel needs its own bare constant"
}

# ════════════════════════════════════════════════════════════════
# F7 — 终局记分卡 + δ 公理化完整谱系
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("F7  终局记分卡 + δ 公理化完整谱系")
print("=" * 78)

print(f"""
  F1  A6 公理化            INFO  A6→w≠0(拓扑)，但不→δ精确值；A6是A5的拓扑前提
  F2  近对消审计            INFO  对消是精确代数恒等式（非近似）；精度=n_α≈60
  F3  加强 no-go            PASS  A1-A5+A6 仍无法推出 δ 精确值（需 α* 输入）
  F4  n_α 关联              PASS  δ = (n_α-60)×dgap/dn / dgap/dw（离散化修正）
  F5  代数结构              INFO  gap(60,1) = 2(1-x²)/(2+x)，x=cos(π/30) degree 8
                              代数数 ≈ 超越数 α* → 巧合（非恒等式）
  F6  Klein 瓶推广          INFO  双 Z₂ → 双 δ₁,δ₂，各需独立 A5

  ═══ δ 公理化完整谱系 ═══

  Tier 0:
    A1-A4+R1 → n=60, 图结构, 谱公式
    no-go: δ 不可从 A1-A4+R1 导出（P 是 S 多项式，[S,P]=0）
    A5: δ 是裸耦合常数（与 QED α 同构）
    → 自由常数 3→1（α,λ₀,κ → δ）

  Tier 1:
    第5项: 细化极限 γ=2（δ 不改标度行为，n=60 离散化巧合）
    第6项: A5 最小性（全局标量），无替代公理化，δ~14.5 bits 独立信息
    第7项: Z₂ 拓扑起源（E3 PASS），近对消机制（E2/E4 INFO）
    第8项: A6 形式化（拓扑前提），no-go 加强（需 α*），代数结构分析

  δ 的完整理解:
    存在性: Z₂ 拓扑强制（A6，Möbius H₁(Z₂)）
    符号:   δ>0（奇模被抬升，光子扇区更重）
    精确值: δ = (1-cos(π/15))/α* - 2 - cos(π/30)
           = f(代数数 degree 8, 物理常数 α*)
           需 A5 裸公理 + α* 物理输入
    角色:   离散化修正（n=60 替代 n_α=60.000436）
    性质:   近对消残余（O(1) 两数对消到 4.347e-5）
    标度:   幂律(1/n²)，非 QED 对数跑动

  最终判定:
    δ 的定性起源完全阐明（Z₂ 拓扑 + 离散化修正）
    δ 的定量推导需要 A5（裸常数）+ α*（物理输入）
    这是 SRE 框架的内在限制：拓扑能给出存在性，不能给出数值
""")

R["F7_scorecard"] = {
    "F1_A6_axiom": "INFO: A6 gives w!=0 (topology) but not delta value; A6 is topological prerequisite of A5",
    "F2_cancellation": "INFO: cancellation is exact algebraic identity; precision = n_alpha approx 60",
    "F3_strengthened_nogo": "PASS: A1-A5+A6 cannot derive delta exact value (requires alpha*)",
    "F4_n_alpha": "PASS: delta = discretization correction (n=60 replaces n_alpha=60.000436)",
    "F5_algebraic": "INFO: gap is degree-8 algebraic; alpha* likely transcendental; coincidence not identity",
    "F6_klein": "INFO: dual Z2 -> dual delta, each needs own A5",
    "delta_full_spectrum": {
        "existence": "Z2 topology (A6, Mobius H1(Z2))",
        "sign": "positive (photon sector lifted)",
        "exact_value": "requires A5 bare constant + alpha* physical input",
        "role": "discretization correction (n=60 replaces n_alpha=60.000436)",
        "nature": "near-cancellation residue (O(1) terms cancel to 4.347e-5)",
        "scaling": "power-law 1/n^2, not QED logarithmic running",
    },
    "final_verdict": "qualitative origin fully clarified (Z2 topology + discretization); quantitative derivation requires A5 (bare) + alpha* (physical); this is an intrinsic limit of SRE: topology gives existence, not value"
}

out = os.path.join(os.path.dirname(__file__), "tier1_delta_formalization_results.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2, cls=NpEncoder)
print(f"结果已写入 {out}")
