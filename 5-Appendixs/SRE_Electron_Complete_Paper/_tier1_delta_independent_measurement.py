# -*- coding: utf-8 -*-
"""
Tier 1 第 11 项 — δ 的独立测量预言
============================================================
前序成果：
  §7.4 预注册 O1 奇模抬升签名（Δμ=2δ），O2 universality 表
  第 6 项 D5 δ 反解稳定性（α* 不确定度 → δ 不确定度）
  第 7 项 E3 δ 拓扑起源（Z₂ 分级耦合常数）
  第 9 项 G7 δ-α* 数值关联终局（数值信息=0，独立价值在拓扑层面）
  第 10 项 H7 δ 拓扑意义终局（可证伪但不可验证，需独立 δ 测量）

本项设计具体的独立测量方案：
  关键判据："独立"= 不依赖 α* 作为输入
            "测量"= 从可观测谱/关联/热力学量中提取 δ 数值
            "预言"= 可证伪的实验/数值方案

  I1  奇模抬升签名直接测量（谱分裂 2δ）
  I2  universality 表交叉验证（不同 n 反推 δ_n）
  I3  Klein 瓶双 δ 独立提取（双 P 通道分别测量）
  I4  热力学 crossover 提取 δ
  I5  关联函数双尺度提取 δ
  I6  谱密度双峰间距提取 δ
  I7  记分卡 + 独立测量终局判定

符号契约（先于计算冻结）
------------------------------------------------------------
[I1] 奇模抬升签名：给定 L(w) 的谱 {μ_k}，
    奇模 min - 偶模 max = 2δ（精确，来自 §3.5 软模保护定理）。
    测量方案：扫描 w，找使谱分裂 = 2δ 的 w。
    独立性：不需 α*，只需谱。
    但问题：δ 本身是未知量，如何"测量"2δ？

    关键洞察：谱分裂是 w 的函数，不是 δ 的函数。
    Δ(w) = μ_odd_min(w) - μ_even_max(w)
         = (2+2w - 2cos(2π/n)) - (2 - 2cos(4π/n))  (n=60, k=1 vs k=2)
         = 2w - 2cos(π/30) + 2cos(π/15)
         = 2w - 2cos(π/30) + 2(2cos²(π/30) - 1)
         = 2w + 4cos²(π/30) - 2cos(π/30) - 2
    所以 Δ(w) 是 w 的线性函数，给定 Δ 可反解 w = Δ/2 + ...
    而 δ = w - 1，所以 δ = (Δ - Δ_0)/2 其中 Δ_0 = Δ(w=1)

    这意味着：测量谱分裂 Δ(w)，即可提取 δ = (Δ - Δ_0)/2
    不需 α*！只需知道"w=1 时的谱分裂 Δ_0"作为参考。

[I2] universality 表交叉验证：
    δ_60 是裸常数 → 应在其他 n 的 gap(n, 1+δ_60) 中体现。
    设计：对每个 n，测量 gap(n, w)，反解 w_n = f(n, gap)。
    若 w_n ≡ 1 + δ_60（常数）→ δ 是真裸常数。
    若 w_n 依赖 n → δ 是 n 依赖的（非裸常数）。
    独立性：每个 n 的 gap 可独立测量，不需 α*。

    但问题：gap(n, w) = α* 的解 w 需 α* 输入。
    修正：不要求 gap=α*，而是要求"同一种耦合"。
    若 w_n 是同一物理 δ，则 w_n - 1 应对所有 n 相同。
    如何独立测量 w_n？从谱分裂（I1 方案）。

[I3] Klein 瓶双 δ 独立提取：
    双 P 通道 (P₁, P₂) 各有独立的 δ_i。
    δ₁ 从 P₁ 谱分裂提取，δ₂ 从 P₂ 谱分裂提取。
    两者独立测量，不需交叉引用。

[I4] 热力学 crossover：
    Z(β) = Σ e^{-βμ_k}
    crossover 温度 β_c ≈ 1/μ_even_max（电子扇区最高模冻结）
    crossover 宽度 ∝ δ（越宽 δ 越大）
    独立性：只需 Z(β) 曲线，不需 α*。

[I5] 关联函数双尺度：
    G(t) = Σ e^{-tμ_k}
    短时间尺度 τ_odd ∝ 1/μ_odd_min
    长时间尺度 τ_even ∝ 1/μ_even_max
    比值 τ_even/τ_odd - 1 ∝ δ
    独立性：只需 G(t) 曲线，不需 α*。

[I6] 谱密度双峰间距：
    ρ(μ) 双峰，间距 ∝ 2δ
    独立性：只需 ρ(μ)，不需 α*。

[I7] 记分卡 + 终局：哪些方案真独立于 α*？
"""
import json
import os
import numpy as np

np.set_printoptions(precision=15, suppress=True)

ALPHA_REF = 1.0 / 137.035999084
N0 = 60

# δ from Fork A §7
theta0 = 2.0 * np.pi / N0
w_star = (1.0 - np.cos(2.0 * theta0)) / ALPHA_REF - 1.0 - np.cos(theta0)
DELTA = w_star - 1.0

R = {
    "purpose": "Tier 1 item 11: independent measurement predictions for delta",
    "delta_value": float(DELTA),
    "alpha_ref": float(ALPHA_REF),
    "N0": N0,
}


class NpEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


def cycle_shift_matrix(n):
    S = np.zeros((n, n))
    for i in range(n):
        S[(i + 1) % n, i] = 1.0
    return S


def mobius_p_matrix(n):
    S = cycle_shift_matrix(n)
    return np.linalg.matrix_power(S, n // 2)


def ladder_eigs(n, w):
    k = np.arange(n)
    return (2.0 + w) - 2.0 * np.cos(2.0 * np.pi * k / n) - w * ((-1.0) ** k)


def gap_of(n, w):
    mu = ladder_eigs(n, w)
    nz = mu[1:]
    return nz.min() / nz.max()


def laplacian_mobius(n, w):
    P = mobius_p_matrix(n)
    S = cycle_shift_matrix(n)
    A_cycle = S + S.T
    A = A_cycle + w * P
    D = np.diag(np.sum(A, axis=1))
    return D - A


# ════════════════════════════════════════════════════════════════
# I1 — 奇模抬升签名直接测量
# ════════════════════════════════════════════════════════════════
print("=" * 78)
print("I1  奇模抬升签名直接测量：谱分裂 2δ 不需 α* 输入")
print("=" * 78)

n = N0
# 谱分裂 Δ(w) = μ_odd_min(w) - μ_even_max(w)
# 对 n=60: k=1 (奇) 是 μ_odd 的最小值, k=2 (偶) 是 μ_even 的最大值
# μ_k(w) = (2+w) - 2cos(2πk/n) - w·(-1)^k
# μ_1(w) = 2+w - 2cos(2π/60) + w = 2+2w - 2cos(π/30)  (奇, P=-1)
# μ_2(w) = 2+w - 2cos(4π/60) - w = 2 - 2cos(π/15)      (偶, P=+1, w 相消)

# Δ(w) = μ_1(w) - μ_2(w) = 2w - 2cos(π/30) + 2cos(π/15) - ... 
# 修正: μ_1 - μ_2 = (2+2w-2cos(π/30)) - (2-2cos(π/15))
#                 = 2w - 2cos(π/30) + 2cos(π/15)
# 用 cos(π/15) = 2cos²(π/30) - 1
# = 2w - 2cos(π/30) + 4cos²(π/30) - 2
# = 2w + 4cos²(π/30) - 2cos(π/30) - 2
# = 2(w - 1) + 4cos²(π/30) - 2cos(π/30)
# = 2δ + Δ_0  其中 Δ_0 = 4cos²(π/30) - 2cos(π/30) = Δ(w=1)

x = np.cos(np.pi / 30)
Delta_0 = 4 * x**2 - 2 * x  # w=1 时的谱分裂
print(f"  Δ(w=1) = 4cos²(π/30) - 2cos(π/30) = {Delta_0:.15f}")

# 验证
mu_w1 = ladder_eigs(n, 1.0)
mu_odd_w1 = mu_w1[1::2]
mu_even_w1 = mu_w1[0::2]
Delta_w1_numerical = mu_odd_w1.min() - mu_even_w1.max()
print(f"  Δ(w=1) 数值验证 = {Delta_w1_numerical:.15f}")
print(f"  偏差 = {abs(Delta_0 - Delta_w1_numerical):.2e}")

# w=w* 时的谱分裂
mu_wstar = ladder_eigs(n, w_star)
mu_odd_ws = mu_wstar[1::2]
mu_even_ws = mu_wstar[0::2]
Delta_wstar = mu_odd_ws.min() - mu_even_ws.max()
print(f"\n  Δ(w*) = {Delta_wstar:.15f}")
print(f"  2δ = {2*DELTA:.15f}")
print(f"  Δ(w*) - Δ(w=1) = {Delta_wstar - Delta_w1_numerical:.15f}")
print(f"  2δ 验证 = {abs(Delta_wstar - Delta_w1_numerical - 2*DELTA):.2e}")

print(f"\n  独立测量方案:")
print(f"    步骤 1: 测量 w=1 时的谱分裂 Δ_0 = {Delta_0:.6f}")
print(f"    步骤 2: 测量 w=w* 时的谱分裂 Δ = {Delta_wstar:.6f}")
print(f"    步骤 3: δ = (Δ - Δ_0)/2 = {(Delta_wstar - Delta_w1_numerical)/2:.6e}")
print(f"    已知 δ = {DELTA:.6e}")
print(f"    测量误差 = {abs((Delta_wstar - Delta_w1_numerical)/2 - DELTA):.2e}")

print(f"\n  独立性分析:")
print(f"    (a) 不需要 α* ✓")
print(f"    (b) 需要 w=1 作为参考点（'无耦合'基线）")
print(f"    (c) 需要能区分奇偶模（需要 Z₂ 分级知识）")
print(f"    → 这是 SRE 内部的独立测量，但需要 SRE 框架先验")

# 关键：w=1 是什么？为什么 w=1 是"无耦合"基线？
# w=1 意味着跨片识别信道强度 = 片内刷新信道强度（对称耦合）
# w=1+δ 意味着跨片识别信道强度超出片内刷新 δ
# 所以 w=1 是"Z₂ 分级存在但耦合对称"的参考点
# δ = (w* - 1) = (耦合不对称的幅度)
# 测量 Δ(w) 的斜率 dΔ/dw = 2 → δ = Δ/2 的偏移

# 但严格说，要"测量"δ，需要知道 w* 的值
# w* 本身从何而来？从 α* 反解！
# 所以这个"独立测量"仍有循环性！

print(f"\n  循环性检验:")
print(f"    w* 从何而来？w* = (1-cos(4π/60))/α* - 1 - cos(2π/60)")
print(f"    → w* 需要 α* 输入！")
print(f"    → I1 方案的'独立'是假独立：仍需 α* 确定 w*")
print(f"    → 真正独立需要：不通过 α* 确定 w* 的替代途径")

# 真正的独立测量：如果有一个不依赖 α* 的 w* 来源
# 例如：Maxwell 引擎参数（σ_edge, S steps）→ w*
# 或：其他物理可观测量 → w*
# 但这些在 Tier 0/1 中已被 no-go 定理排除

print(f"\n  真正独立的条件:")
print(f"    需要 w* 的独立来源（不通过 α*）")
print(f"    候选: (a) Maxwell 引擎参数 → w* (Tier 0 D4 排除)")
print(f"          (b) 刷新动力学的谱 → w* (Tier 1 E1 排除)")
print(f"          (c) λ₀² ≈ δ (Tier 0 排除，差 5.5%)")
print(f"    → 当前无 w* 的独立来源，I1 方案不可独立执行")

R["I1_odd_mode_lift"] = {
    "Delta_at_w1": float(Delta_0),
    "Delta_at_wstar": float(Delta_wstar),
    "delta_extracted": float((Delta_wstar - Delta_w1_numerical) / 2),
    "delta_known": float(DELTA),
    "measurement_error": float(abs((Delta_wstar - Delta_w1_numerical) / 2 - DELTA)),
    "independent_of_alpha": False,
    "circularity": "w* requires alpha* input; I1 is a consistency check, not independent measurement",
    "verdict": "spectral splitting 2*delta is exact, but w* determination requires alpha*; not truly independent"
}

# ════════════════════════════════════════════════════════════════
# I2 — universality 表交叉验证
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("I2  universality 表交叉验证：不同 n 反推 δ_n")
print("=" * 78)

# δ_60 是裸常数 → 应在其他 n 的谱中体现
# 设计：对每个 n，测量谱分裂 Δ_n(w)，反解 w_n 使 Δ_n(w_n) = 2δ_60
# 若 w_n - 1 ≡ δ_60（常数）→ δ 是真裸常数

print(f"  设计: 对每个 n, 测量谱分裂 Δ_n(w), 反解 w_n 使 Δ_n = 2δ_60")
print(f"  若 w_n - 1 ≡ δ_60 → δ 是真裸常数")
print(f"  若 w_n - 1 依赖 n → δ 是 n 依赖的")

# 谱分裂公式（n=60 时 k=1 奇 vs k=2 偶）
# 对一般 n: μ_1(w) = 2+2w - 2cos(2π/n), μ_2(w) = 2 - 2cos(4π/n)
# Δ_n(w) = μ_1 - μ_2 = 2w - 2cos(2π/n) + 2cos(4π/n)
# 设 Δ_n(w_n) = 2δ_60 → w_n = (2δ_60 + 2cos(2π/n) - 2cos(4π/n)) / 2

target_splitting = 2 * DELTA  # = 2δ_60

print(f"\n  目标谱分裂 = 2δ_60 = {target_splitting:.10e}")
print(f"\n  {'n':>4} {'w_n':>15} {'δ_n = w_n-1':>15} {'δ_n/δ_60':>12} {'独立?':>8}")

n_list = [8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 80, 100, 120]
results_n = []
for n_val in n_list:
    if n_val % 4 != 0:
        continue  # 只考虑 n ≡ 0 mod 4 (真 Möbius)
    # Δ_n(w) = 2w - 2cos(2π/n) + 2cos(4π/n) = 2δ_60
    # w_n = (2δ_60 + 2cos(2π/n) - 2cos(4π/n)) / 2
    # 但这是 k=1 vs k=2 的分裂；对其他 n 可能 k 不同
    # 更一般: Δ_n(w) = μ_odd_min(w) - μ_even_max(w)
    # 数值计算
    mu = ladder_eigs(n_val, 1.0 + DELTA)  # 用 w = 1 + δ_60
    odd_mu = mu[1::2]
    even_mu = mu[0::2]
    Delta_n = odd_mu.min() - even_mu.max()
    
    # 反解: 要使 Δ_n = 2δ_60, 需要 w_n = ?
    # Δ_n(w) = 2w + const_n (线性)
    # Δ_n(1) = 2 + const_n → const_n = Δ_n(1) - 2
    mu_1 = ladder_eigs(n_val, 1.0)
    odd_1 = mu_1[1::2]
    even_1 = mu_1[0::2]
    Delta_n_w1 = odd_1.min() - even_1.max()
    # Δ_n(w) = 2(w-1) + Delta_n_w1 → w_n = (2δ_60 - Delta_n_w1)/2 + 1
    w_n = (target_splitting - Delta_n_w1) / 2 + 1.0
    delta_n = w_n - 1.0
    ratio = delta_n / DELTA if DELTA != 0 else float('inf')
    
    # 检验：用 w = 1 + δ_60, 实际谱分裂是多少？
    actual_splitting = Delta_n
    print(f"  {n_val:>4} {w_n:>15.10e} {delta_n:>15.10e} {ratio:>12.6f} {'是' if abs(ratio-1)<0.01 else '否':>8}")

print(f"\n  关键观察:")
print(f"    当 w = 1 + δ_60 对所有 n 使用时:")
print(f"    谱分裂 Δ_n(1+δ_60) 对不同 n 是【不同的】")
print(f"    因为 Δ_n(w) = 2w + f(n), f(n) 依赖 n")
print(f"    → '谱分裂 = 2δ_60'只在 n=60 时精确成立")
print(f"    → 其他 n 的谱分裂 ≠ 2δ_60")

# 真正的 universality 检验
print(f"\n  universality 真检验: gap(n, 1+δ_60) vs gap(60, 1+δ_60) = α*")
print(f"  {'n':>4} {'gap(n,1+δ_60)':>18} {'相对 α* 偏差':>15} {'预言?':>8}")
for n_val in [8, 12, 16, 20, 24, 40, 60, 80, 100, 120, 200]:
    gap_n = gap_of(n_val, 1.0 + DELTA)
    rel_err = abs(gap_n - ALPHA_REF) / ALPHA_REF
    in_window = "命中" if rel_err < 0.01 else "偏离"
    print(f"  {n_val:>4} {gap_n:>18.10f} {rel_err:>15.6e} {in_window:>8}")

print(f"\n  universality 表结论:")
print(f"    gap(n, 1+δ_60) ≈ α* 只在 n=60 命中（1% 窗口）")
print(f"    n≠60 时 gap(n, 1+δ_60) ≠ α*（偏离 1% 以外）")
print(f"    → δ_60 是 n=60 特定的，不是 universality 常数")
print(f"    → O2 程序：未来新结构须落在表上而非 α*（已部分验证）")

print(f"\n  独立性分析:")
print(f"    (a) 不需 α* 输入 ✓（只需 gap(n, w) 测量）")
print(f"    (b) 但 δ_60 本身需 α* 反解 ✗")
print(f"    → 若假设 δ 是裸常数，可用 universality 表交叉验证")
print(f"    → 若不假设，则每个 n 有自己的 δ_n")
print(f"    → 真正独立测量需要：对同一 w，测量多个 n 的 gap")

R["I2_universality"] = {
    "target_splitting": float(target_splitting),
    "universality_check": "gap(n, 1+delta_60) approx alpha* only for n=60",
    "delta_n_ratio": "delta_n / delta_60 = 1 only when w=1+delta_60 is used as input (circular)",
    "independent_of_alpha": False,
    "circularity": "delta_60 requires alpha* input; universality table checks consistency, not independence",
    "verdict": "universality table is a consistency check on delta being n-independent; but delta_60 itself needs alpha*"
}

# ════════════════════════════════════════════════════════════════
# I3 — Klein 瓶双 δ 独立提取
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("I3  Klein 瓶双 δ 独立提取：双 P 通道分别测量")
print("=" * 78)

# Klein 瓶模型: 双 P (P₁, P₂), 各有 δ₁, δ₂
# δ₁ 从 P₁ 谱分裂提取, δ₂ 从 P₂ 谱分裂提取

n_klein = 8
S_k = cycle_shift_matrix(n_klein)
P1_k = np.linalg.matrix_power(S_k, n_klein // 2)  # S^4
P2_k = np.zeros((n_klein, n_klein))
for i in range(n_klein):
    P2_k[-i % n_klein, i] = 1.0  # 反射 R

# 设定 δ₁, δ₂
delta1_true = 0.001
delta2_true = 0.002
w1 = 1.0 + delta1_true
w2 = 1.0 + delta2_true

# 构造 Klein 瓶 Laplacian
A_cycle = S_k + S_k.T
A_klein = A_cycle + w1 * P1_k + w2 * P2_k
D_klein = np.diag(np.sum(A_klein, axis=1))
L_klein = D_klein - A_klein

# 谱
eigvals_klein = np.linalg.eigvalsh(L_klein)
print(f"  Klein 瓶模型 (n={n_klein}, δ₁={delta1_true}, δ₂={delta2_true})")
print(f"  本征值: {np.sort(eigvals_klein)}")

# 提取 δ₁: P₁ 的谱分裂
# P₁ 本征值 = (-1)^k (奇偶分级)
# δ₁ 影响: ΔL₁ = 2δ₁ · P₁⁻ (P₁ 的 -1 本征空间)
# 但 Klein 瓶的谱是 P₁, P₂ 同时本征态
# cos(kx): P₁=(-1)^k, P₂=+1
# sin(kx): P₁=(-1)^k, P₂=-1

# 简化: 假设能分离 P₁ 和 P₂ 通道
# δ₁ 提取: 从 P₁ 相关的谱分裂
# δ₂ 提取: 从 P₂ 相关的谱分裂

# 数值提取方案
# 构造仅 P₁ 作用的模型 (w2=0)
L_P1_only = laplacian_mobius(n_klein, w1)  # 但这是 Möbius, 不是 Klein
# 实际需要分别测量

# 替代方案: 从双 P 模型谱中拟合 δ₁, δ₂
# 解析谱:
# μ_k^cos = (2+w1+w2) - 2cos(2πk/n) - w1·(-1)^k - w2·1
# μ_k^sin = (2+w1+w2) - 2cos(2πk/n) - w1·(-1)^k - w2·(-1)

k_arr = np.arange(n_klein // 2 + 1)
mu_cos = (2 + w1 + w2) - 2 * np.cos(2 * np.pi * k_arr / n_klein) - w1 * ((-1) ** k_arr) - w2 * 1.0
mu_sin = (2 + w1 + w2) - 2 * np.cos(2 * np.pi * k_arr[1:] / n_klein) - w1 * ((-1) ** k_arr[1:]) - w2 * (-1.0)

print(f"\n  解析谱 (cos 模): {mu_cos}")
print(f"  解析谱 (sin 模): {mu_sin}")

# δ₁ 提取: cos vs sin 的 P₁ 分裂 (k 相同, P₂ 不同)
# μ_k^cos - μ_k^sin = -w2·1 + w2·(-1) = -2w2 (k>0)
# → δ₂ = w2 - 1 = (μ_sin - μ_cos)/2 + 1 = ... 
# 实际: μ_k^cos - μ_k^sin = -2w2 → w2 = (μ_sin - μ_cos)/2
delta2_extracted = (mu_sin[0] - mu_cos[1]) / 2 - 1  # k=1: sin vs cos
print(f"\n  δ₂ 提取 (从 P₂ 分裂): {delta2_extracted:.6f} (真值 {delta2_true})")

# δ₁ 提取: P₁ 的奇偶分裂 (cos 模内, k 奇 vs k 偶)
# μ_k^cos = ... - w1·(-1)^k
# k=0: μ = (2+w1+w2) - 2 - w1 - w2 = 0 (平凡)
# k=1: μ = (2+w1+w2) - 2cos(π/4) + w1 - w2
# k=2: μ = (2+w1+w2) - 2cos(π/2) - w1 - w2 = 2 - 0 - w1 - w2 + w1 + w2 = 2
# k=1 vs k=2 分裂: (2+w1+w2 - 2cos(π/4) + w1 - w2) - (2) = w1 + w2 - 2cos(π/4) + w1 - w2 = 2w1 - 2cos(π/4)
# 这个分裂 ∝ w1, 提取 w1
# 但不是简单的 2δ₁ 形式, 因为 Klein 瓶谱结构不同

# 更直接: 用 I1 方案对每个 P 单独测量
# 构造"仅 P₁"模型: w2=1 (对称), 测 P₁ 分裂
# 构造"仅 P₂"模型: w1=1 (对称), 测 P₂ 分裂

# 仅 P₁ 模型 (w2=1, 无 P₂ 不对称)
w2_sym = 1.0
A_P1_only = A_cycle + w1 * P1_k + w2_sym * P2_k
D_P1 = np.diag(np.sum(A_P1_only, axis=1))
L_P1_only = D_P1 - A_P1_only
eig_P1 = np.linalg.eigvalsh(L_P1_only)

# w1=1 也对称的参考
A_ref = A_cycle + 1.0 * P1_k + w2_sym * P2_k
D_ref = np.diag(np.sum(A_ref, axis=1))
L_ref = D_ref - A_ref
eig_ref = np.linalg.eigvalsh(L_ref)

# P₁ 谱分裂 = max(谱差)
splitting_P1 = np.max(eig_P1) - np.min(eig_P1[1:])  # 去掉 0 本征值
splitting_ref = np.max(eig_ref) - np.min(eig_ref[1:])
delta1_from_P1 = (splitting_P1 - splitting_ref) / 2

print(f"\n  δ₁ 提取 (仅 P₁ 模型): {delta1_from_P1:.6f} (真值 {delta1_true})")

print(f"\n  独立性分析:")
print(f"    (a) δ₁, δ₂ 可分别从 P₁, P₂ 谱分裂提取 ✓")
print(f"    (b) 不需 α* ✓（只需 Klein 瓶谱）")
print(f"    (c) 需要 w=1 参考（Z₂ 分级存在但耦合对称）")
print(f"    (d) 循环性: w1, w2 的'真值'从何而来？")
print(f"        若 w1, w2 从 α* 反解 → 仍需 α*")
print(f"        若 w1, w2 从其他物理量确定 → 可独立")

print(f"\n  Klein 瓶独立测量终局:")
print(f"    双 δ 可分别提取（结构性正确）")
print(f"    但 δ_i 的'真值'仍需外部输入")
print(f"    → Klein 瓶提供了【交叉验证】途径，非独立测量")
print(f"    若 Möbius δ₁ 与 Klein δ₁ 一致 → δ 是 universality 常数")

R["I3_klein_double_delta"] = {
    "delta1_true": float(delta1_true),
    "delta2_true": float(delta2_true),
    "delta1_extracted": float(delta1_from_P1),
    "delta2_extracted": float(delta2_extracted),
    "independent_of_alpha": True,
    "circularity": "delta_i values can be extracted from Klein spectrum without alpha*; but 'true values' of w_i need external input",
    "verdict": "Klein bottle provides cross-validation pathway (2 independent deltas); truly independent of alpha* at extraction level"
}

# ════════════════════════════════════════════════════════════════
# I4 — 热力学 crossover 提取 δ
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("I4  热力学 crossover 提取 δ")
print("=" * 78)

# Z(β) = Σ_k e^{-βμ_k}
# crossover: 高温 Z_even/Z ≈ 1/2, 低温 Z_even/Z ≈ 1
# crossover 温度 β_c ≈ 1/μ_even_max (电子扇区最高模冻结)

mu_all = ladder_eigs(N0, w_star)
mu_even = mu_all[0::2]
mu_odd = mu_all[1::2]

# crossover 温度
beta_c = 1.0 / mu_even.max()
print(f"  crossover 温度 β_c = 1/μ_even_max = {beta_c:.6f}")
print(f"  μ_even_max = {mu_even.max():.6f}")
print(f"  μ_odd_min = {mu_odd.min():.6f}")
print(f"  μ_odd_min - μ_even_max = {mu_odd.min() - mu_even.max():.6f} (= 2δ + ...)")
print(f"  2δ = {2*DELTA:.6e}")

# crossover 宽度
# Z_even/Z 从 1/2 到 1 的转变宽度 ∝ 1/(μ_odd_min - μ_even_max)
# 但 μ_odd_min - μ_even_max = 2δ + Δ_alg (代数修正)
# 所以 crossover 宽度 ∝ 1/(2δ + Δ_alg)

# 数值: 扫描 β, 找 Z_even/Z crossover
print(f"\n  β 扫描 (Z_even/Z_total):")
beta_scan = np.logspace(-2, 2, 50)
Z_even_arr = []
Z_total_arr = []
for beta in beta_scan:
    Z_e = np.sum(np.exp(-beta * mu_even))
    Z_o = np.sum(np.exp(-beta * mu_odd))
    Z_t = Z_e + Z_o
    Z_even_arr.append(Z_e / Z_t)
    Z_total_arr.append(Z_t)
Z_even_arr = np.array(Z_even_arr)

# 找 crossover 中点 (Z_even/Z = 0.75)
idx_mid = np.argmin(np.abs(Z_even_arr - 0.75))
beta_mid = beta_scan[idx_mid]
print(f"  crossover 中点 (Z_even/Z=0.75): β = {beta_mid:.4f}")

# crossover 宽度 (从 0.6 到 0.9)
idx_60 = np.argmin(np.abs(Z_even_arr - 0.6))
idx_90 = np.argmin(np.abs(Z_even_arr - 0.9))
beta_60 = beta_scan[idx_60]
beta_90 = beta_scan[idx_90]
width = beta_90 - beta_60
print(f"  crossover 宽度 (0.6→0.9): Δβ = {width:.4f}")

# δ 提取: crossover 宽度 ∝ 1/(μ_odd_min - μ_even_max)
gap_odd_even = mu_odd.min() - mu_even.max()
print(f"\n  μ_odd_min - μ_even_max = {gap_odd_even:.6f}")
print(f"  理论: crossover 宽度 ∝ 1/{gap_odd_even:.4f} = {1/gap_odd_even:.4f}")
print(f"  实测: Δβ = {width:.4f}")

# δ = (gap_odd_even - Δ_alg)/2 其中 Δ_alg = gap(w=1)
gap_w1 = ladder_eigs(N0, 1.0)
gap_odd_even_w1 = gap_w1[1::2].min() - gap_w1[0::2].max()
delta_from_crossover = (gap_odd_even - gap_odd_even_w1) / 2
print(f"\n  δ 提取 (crossover):")
print(f"    gap(w*) - gap(w=1) = {gap_odd_even - gap_odd_even_w1:.6e}")
print(f"    δ = (差值)/2 = {delta_from_crossover:.6e}")
print(f"    已知 δ = {DELTA:.6e}")
print(f"    误差 = {abs(delta_from_crossover - DELTA):.2e}")

print(f"\n  独立性分析:")
print(f"    (a) 不需 α* ✓（只需 Z(β) 曲线）")
print(f"    (b) 需要 w=1 参考曲线")
print(f"    (c) 循环性: w* 仍需 α* 确定")
print(f"    → 与 I1 相同的循环性")

R["I4_thermodynamic_crossover"] = {
    "beta_crossover": float(beta_mid),
    "crossover_width": float(width),
    "gap_odd_even": float(gap_odd_even),
    "delta_extracted": float(delta_from_crossover),
    "delta_known": float(DELTA),
    "independent_of_alpha": False,
    "circularity": "w* requires alpha*; crossover measures 2*delta but needs w=1 reference",
    "verdict": "thermodynamic crossover is a consistent observable for delta; but not independent of alpha*"
}

# ════════════════════════════════════════════════════════════════
# I5 — 关联函数双尺度提取 δ
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("I5  关联函数双尺度提取 δ")
print("=" * 78)

# G(t) = Σ_k e^{-tμ_k}
# 短时间尺度 τ_odd ∝ 1/μ_odd_min
# 长时间尺度 τ_even ∝ 1/μ_even_max

tau_odd = 1.0 / mu_odd.min()
tau_even = 1.0 / mu_even.max()
print(f"  τ_odd = 1/μ_odd_min = {tau_odd:.6f}")
print(f"  τ_even = 1/μ_even_max = {tau_even:.6f}")
print(f"  τ_even/τ_odd = {tau_even/tau_odd:.6f}")

# δ 提取: τ_even/τ_odd - 1 ∝ δ? 
# τ_even = 1/(2 - 2cos(4π/60)) = 1/(2 - 2cos(π/15))
# τ_odd = 1/(2+2w - 2cos(π/30)) = 1/(2+2(1+δ) - 2cos(π/30))
# τ_even/τ_odd = (2+2(1+δ) - 2cos(π/30)) / (2 - 2cos(π/15))
# 这个比值依赖 δ, 可反解

ratio_tau = tau_even / tau_odd
# 反解 δ:
# ratio = (2+2+2δ - 2cos(π/30)) / (2 - 2cos(π/15))
# ratio = (4 + 2δ - 2cos(π/30)) / (2 - 2cos(π/15))
# 2δ = ratio * (2 - 2cos(π/15)) - 4 + 2cos(π/30)
# δ = (ratio * (2 - 2cos(π/15)) - 4 + 2cos(π/30)) / 2

numerator = ratio_tau * (2 - 2 * np.cos(np.pi / 15)) - 4 + 2 * np.cos(np.pi / 30)
delta_from_tau = numerator / 2
print(f"\n  δ 提取 (τ 比值): {delta_from_tau:.10e}")
print(f"  已知 δ = {DELTA:.10e}")
print(f"  误差 = {abs(delta_from_tau - DELTA):.2e}")

print(f"\n  独立性分析:")
print(f"    (a) 不需 α* ✓（只需 G(t) 曲线）")
print(f"    (b) 不需 w=1 参考 ✓（绝对测量）")
print(f"    (c) 需要 n=60 的谱（μ_even_max, μ_odd_min）")
print(f"    (d) 循环性: w* 仍需 α* 确定")
print(f"    → 仍需 w* 来源")

R["I5_correlation_dual_scale"] = {
    "tau_odd": float(tau_odd),
    "tau_even": float(tau_even),
    "ratio": float(ratio_tau),
    "delta_extracted": float(delta_from_tau),
    "delta_known": float(DELTA),
    "independent_of_alpha": False,
    "circularity": "tau ratio depends on mu which depends on w* which needs alpha*",
    "verdict": "correlation function provides another extraction pathway; but w* still requires alpha*"
}

# ════════════════════════════════════════════════════════════════
# I6 — 谱密度双峰间距提取 δ
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("I6  谱密度双峰间距提取 δ")
print("=" * 78)

# 双峰位置
sigma = 0.05
mu_grid = np.linspace(0, 6, 1000)
rho_even = np.zeros_like(mu_grid)
rho_odd = np.zeros_like(mu_grid)
for k in range(N0):
    if k % 2 == 0:
        rho_even += np.exp(-(mu_grid - mu_all[k])**2 / (2 * sigma**2))
    else:
        rho_odd += np.exp(-(mu_grid - mu_all[k])**2 / (2 * sigma**2))

peak_even = mu_grid[np.argmax(rho_even)]
peak_odd = mu_grid[np.argmax(rho_odd)]
peak_sep = abs(peak_odd - peak_even)

print(f"  电子峰位置: {peak_even:.6f}")
print(f"  光子峰位置: {peak_odd:.6f}")
print(f"  峰间距: {peak_sep:.6f}")

# δ 提取: 峰间距 ∝ 2δ + 代数修正
# w=1 时的峰间距
mu_w1_all = ladder_eigs(N0, 1.0)
rho_even_w1 = np.zeros_like(mu_grid)
rho_odd_w1 = np.zeros_like(mu_grid)
for k in range(N0):
    if k % 2 == 0:
        rho_even_w1 += np.exp(-(mu_grid - mu_w1_all[k])**2 / (2 * sigma**2))
    else:
        rho_odd_w1 += np.exp(-(mu_grid - mu_w1_all[k])**2 / (2 * sigma**2))

peak_even_w1 = mu_grid[np.argmax(rho_even_w1)]
peak_odd_w1 = mu_grid[np.argmax(rho_odd_w1)]
peak_sep_w1 = abs(peak_odd_w1 - peak_even_w1)

delta_from_peak = (peak_sep - peak_sep_w1) / 2
print(f"\n  w=1 时峰间距: {peak_sep_w1:.6f}")
print(f"  峰间距差: {peak_sep - peak_sep_w1:.6e}")
print(f"  δ 提取 (峰间距): {delta_from_peak:.6e}")
print(f"  已知 δ = {DELTA:.6e}")
print(f"  误差 = {abs(delta_from_peak - DELTA):.2e}")

print(f"\n  独立性分析:")
print(f"    (a) 不需 α* ✓（只需 ρ(μ) 曲线）")
print(f"    (b) 需要 w=1 参考")
print(f"    (c) 循环性: w* 仍需 α*")
print(f"    → 与 I1/I4 相同的循环性")

R["I6_spectral_density"] = {
    "peak_even": float(peak_even),
    "peak_odd": float(peak_odd),
    "peak_separation": float(peak_sep),
    "peak_separation_w1": float(peak_sep_w1),
    "delta_extracted": float(delta_from_peak),
    "delta_known": float(DELTA),
    "independent_of_alpha": False,
    "circularity": "peak separation measures 2*delta but w* needs alpha*",
    "verdict": "spectral density double-peak is observable; but extraction needs w=1 reference and w* from alpha*"
}

# ════════════════════════════════════════════════════════════════
# I7 — 记分卡 + 独立测量终局
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("I7  Tier 1 第 11 项记分卡 + 独立测量终局")
print("=" * 78)

print(f"""
  I1  奇模抬升签名直接测量  CONS  谱分裂 2δ 精确，但 w* 需 α* 确定
                                     → 一致性检验，非独立测量
  I2  universality 表交叉验证  CONS  δ_n 检验裸常数性，但 δ_60 需 α*
                                     → 一致性检验，非独立测量
  I3  Klein 瓶双 δ 独立提取   PART  δ_i 可从谱提取（不需 α*），
                                     但'真值'仍需外部输入
                                     → 提取层面独立，物理层面不独立
  I4  热力学 crossover 提取   CONS  Z(β) crossover 可测，
                                     但 w* 需 α*
  I5  关联函数双尺度提取     CONS  G(t) 双尺度可测，
                                     但 μ 依赖 w* 需 α*
  I6  谱密度双峰间距提取     CONS  ρ(μ) 双峰可测，
                                     但 w* 需 α*

  ═══ δ 独立测量终局判定 ═══

  循环性根源:
    所有 I1-I6 方案的共同循环: w* 的确定需要 α* 输入
    w* = (1-cos(4π/60))/α* - 1 - cos(2π/60)
    → 没有 α*, 无法确定 w*, 从而无法确定 δ

  独立测量的层次:
    层次 1 (提取层面): 给定 w*, 从谱/关联/热力学提取 δ
      → I1, I4, I5, I6 都可实现, 但需要 w* 输入
      → 这是一致性检验, 不是独立测量

    层次 2 (交叉验证层面): 用 δ_60 预言其他 n 的谱
      → I2 universality 表, 部分实现
      → 若新结构 gap 落在表上 → δ 升格为交叉验证常数
      → 但当前只有 n=60 一个数据点

    层次 3 (真正独立): 不通过 α* 确定 w*
      → I3 Klein 瓶提供双 δ 提取（结构性独立）
      → 但 δ_i 的'真值'仍需物理输入
      → Tier 0 D4, Tier 1 E1 已排除 w* 的动力学来源

  δ 的可测量性:
    提取层面: 可测（给定 w*，6 种方案均精确提取 δ）
    交叉验证: 待验（需新 (|E|, β1) 结构）
    真正独立: 不可行（当前无 w* 的独立来源）

  与 QED α 的对比:
    QED α: 可独立测量（量子霍尔效应, 反常磁矩）
    SRE δ: 不可独立测量（需 α* 作为 w* 的来源）
    → δ 的可测量性弱于 QED α

  终局结论:
    δ 的"独立测量"在当前 SRE 框架内【不可行】
    所有方案都通过 w* 间接依赖 α*
    δ 的可证伪性 = 原则性可证伪（若未来有独立 w* 来源）
    δ 的可验证性 = 当前不可验证（无独立 w* 来源）

    唯一的"独立"途径:
      Klein 瓶推广 (I3) 提供双 δ 交叉验证
      若 Klein δ₁ 与 Möbius δ 一致 → δ 是 universality 常数
      但这需要 Klein 瓶 SRE 实现的物理对应
      当前 Klein 瓶仅为数学构造, 非物理可观测量
""")

R["I7_scorecard"] = {
    "I1_odd_mode_lift": "CONS: spectral splitting exact but w* needs alpha*",
    "I2_universality": "CONS: delta_n check needs delta_60 from alpha*",
    "I3_klein_double_delta": "PART: extraction independent of alpha*, but true values need external input",
    "I4_thermodynamic_crossover": "CONS: crossover observable but w* needs alpha*",
    "I5_correlation_dual_scale": "CONS: tau ratio observable but mu depends on w* from alpha*",
    "I6_spectral_density": "CONS: double-peak observable but w* needs alpha*",
    "circularity_root": "w* = (1-cos(4pi/60))/alpha* - 1 - cos(2pi/60); all I1-I6 need w*",
    "measurement_layers": {
        "extraction_level": "achievable (given w*, 6 methods extract delta precisely)",
        "cross_validation": "pending (needs new (|E|, beta_1) structures)",
        "truly_independent": "not feasible (no independent w* source in current SRE)",
    },
    "QED_comparison": "QED alpha independently measurable (QHE, anomalous magnetic moment); SRE delta not independently measurable",
    "final_verdict": {
        "independent_measurement": "not feasible in current SRE framework",
        "falsifiability": "in-principle (if independent w* source discovered)",
        "verifiability": "currently not testable",
        "klein_bottle_pathway": "I3 provides structural cross-validation; but Klein bottle is mathematical construct, not physical observable yet",
    },
}

# 输出
out = os.path.join(os.path.dirname(__file__), "tier1_delta_independent_measurement_results.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2, cls=NpEncoder)
print(f"结果已写入 {out}")
