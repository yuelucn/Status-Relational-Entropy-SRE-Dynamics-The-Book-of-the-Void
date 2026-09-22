# -*- coding: utf-8 -*-
"""
Tier 0 — 理论重审：n=60 ↔ Möbius 阶梯 M_60 ↔ α 的逻辑地位
============================================================
目的：把 Tier 0 第 4 项 FAIL 之后的"巧合"精确化为可审计命题。
本脚本【不预注册任何新候选谱量】，只做命题刻画：
  S1  gap(M_n)=α 的唯一交叉点 n_α 的精确值
  S2  1% 窗口内的偶整数唯一性 + 先验命中概率
  S3  实验精度窗口宽度（整数 n 原则上能否达到）
  S4  代数性论证：gap(M_n) ∈ 分圆域，α 的相等只能是近似
  S5  梯子结构的几何窗口：w=0.1 时全梯子 n 上界
  S6  残差分析：|gap(60)-α*| 与实验不确定度的量级对比
  S7  Maxwell.py 设计常数来源表（哪些进入 n=60，哪些不进入）
"""
import json
import numpy as np
from scipy.spatial.distance import cdist

np.set_printoptions(precision=12, suppress=True)

ALPHA_2018 = 1.0 / 137.035999084      # CODATA 2018
ALPHA_2022 = 1.0 / 137.035999177      # CODATA 2022
ALPHA_UNC_REL = 1.5e-10               # CODATA 2022 相对不确定度量级

def ladder_gap(n):
    """Möbius 阶梯 M_n（n 偶）组合拉普拉斯谱间隙闭式。"""
    return (2.0 - 2.0 * np.cos(4 * np.pi / n)) / (4.0 + 2.0 * np.cos(2 * np.pi / n))

# ════════════════════════════════════════════════════════════
print("=" * 78)
print("S1  gap(M_n) = α 的唯一交叉点 n_α")
print("=" * 78)
# gap = 2(1-c²)/(2+c) = α  →  2c² + αc + (2α-2) = 0, c = cos(2π/n)
a = ALPHA_2018
c_alpha = (-a + np.sqrt(a * a - 8.0 * (2.0 * a - 2.0))) / 4.0
theta_alpha = np.arccos(c_alpha)
n_alpha = 2 * np.pi / theta_alpha
print(f"  cos θ_α = {c_alpha:.15f}")
print(f"  θ_α     = {theta_alpha:.15f} rad = {np.degrees(theta_alpha):.12f}°")
print(f"  n_α     = 2π/θ_α = {n_alpha:.9f}")
print(f"  n_α − 60 = {n_alpha - 60:.3e}   （交叉点距整数 60 仅 {abs(n_alpha-60)/60:.2e} 相对）")
print(f"  [对照] cos(π/30) = {np.cos(np.pi/30):.15f}  （n=60 的闭式自变量）")

# ════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("S2  1% 窗口内的偶整数唯一性 + 先验命中概率")
print("=" * 78)
evens = np.arange(4, 202, 2)
gaps = np.array([ladder_gap(n) for n in evens])
hits1pct = evens[np.abs(gaps - a) / a < 0.01]
print(f"  偶整数 n∈[4,200] 共 {len(evens)} 个候选")
print(f"  |gap−α|<1% 的命中: {list(hits1pct)}")
# 1% 窗口在 n 空间的宽度（数值求逆）
from scipy.optimize import brentq
n_lo = brentq(lambda n: ladder_gap(n) - a * 1.01, 58, 60)
n_hi = brentq(lambda n: ladder_gap(n) - a * 0.99, 60, 62)
width = n_hi - n_lo
span = 200 - 4
print(f"  1% 窗口: n ∈ ({n_lo:.4f}, {n_hi:.4f})，宽度 {width:.4f}")
print(f"  概率口径 A（n_α 在 [4,200] 均匀未知，特定偶整数被命中）:")
print(f"    P = {width:.4f}/{span} = {width/span*100:.2f}%")
print(f"  概率口径 B（至少一个偶整数命中，99 个窗口不重叠地铺盖数轴）:")
print(f"    P = 99×{width:.4f}/{span} = {99*width/span*100:.1f}%")
print(f"  概率口径 C（胞腔复形积'随机等可能取 99 个偶整数之一'）:")
print(f"    P = 1/99 = {1/99*100:.2f}%   ← 与本问题最对应的口径")

# ════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("S3  实验精度窗口：整数 n 原则上能否复现 α？")
print("=" * 78)
dgap_dn = (ladder_gap(62) - ladder_gap(58)) / 4.0   # n=60 处数值导数
dn_exp = ALPHA_UNC_REL * a / abs(dgap_dn)
print(f"  |d gap/dn|(n=60) ≈ {abs(dgap_dn):.3e} / 单位 n")
print(f"  实验精度窗口（相对 {ALPHA_UNC_REL:.0e}）: Δn = ±{dn_exp:.2e}")
print(f"  → 要用整数 n 复现 α 至实验精度，需要 n_α 恰为整数到 1e-8 ——")
print(f"    当前 n_α − 60 = {n_alpha-60:.1e}，差 5 个数量级。")
print(f"    结论：该家族【原则上】无法给出实验精度的 α，只能给 0.0015% 级近似。")

# ════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("S4  代数性论证：gap(M_n) 是分圆域代数数")
print("=" * 78)
print("  gap(M_n) = (2−2cos(4π/n))/(4+2cos(2π/n)) ∈ Q(cos(2π/n)) = Q(ζ_n+ζ_n⁻¹)")
phi60 = 60 * (1 - 1/2) * (1 - 1/3) * (1 - 1/5)   # 欧拉函数
print(f"  n=60: [Q(cos(π/30)):Q] = φ(60)/2 = {int(phi60)}//2 = {int(phi60)//2}")
print("  → 对每个偶 n，gap(M_n) 是次数 ≤ φ(n)/2 的代数数；")
print("    除非 α 本身是该类代数数（未知，但无任何证据），")
print("    gap(M_n)=α 只能是近似等式 —— 推导必须包含修正/极限机制。")
print("    而细化极限检验（Tier 0 第 4 项）已证明该家族无 α 极限。")

# ════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("S5  梯子结构的几何窗口（w=0.1）：全梯子 n 上界")
print("=" * 78)

def mobius_points(n, w=0.1):
    phi = np.linspace(0, 4 * np.pi, n, endpoint=False)
    return np.column_stack([
        (1 + w * np.cos(phi / 2)) * np.cos(phi),
        (1 + w * np.cos(phi / 2)) * np.sin(phi),
        w * np.sin(phi / 2)])

def ladder_node_fraction(n, w=0.1):
    d = cdist(mobius_points(n, w), mobius_points(n, w))
    cnt = 0
    for i in range(n):
        shell = set(int(j) for j in np.argsort(d[i])[1:4])
        if shell == {(i - 1) % n, (i + 1) % n, (i + n // 2) % n}:
            cnt += 1
    return cnt / n

rows = []
for n in range(8, 202, 2):
    rows.append((n, ladder_node_fraction(n)))
full = [n for n, f in rows if f == 1.0]
mixed = [(n, f) for n, f in rows if 0.0 < f < 1.0]
none_ladder = [n for n, f in rows if f == 0.0]
# 压缩输出：连续段
def ranges(xs):
    out, s = [], None
    for i, x in enumerate(xs):
        if s is None:
            s = p = x
        elif x == p + 2:
            p = x
        else:
            out.append((s, p)); s = p = x
    if s is not None:
        out.append((s, p))
    return out
print(f"  全梯子段（100% 节点壳={{±1, partner}}）: "
      f"{[f'{a_}-{b_}' if a_ != b_ else f'{a_}' for a_, b_ in ranges(full)]}")
print(f"  零梯子段: {[f'{a_}-{b_}' if a_ != b_ else f'{a_}' for a_, b_ in ranges(none_ladder)]}")
print(f"  混合段: {[f'{a_}-{b_}' if a_ != b_ else f'{a_}' for a_, b_ in ranges([n for n, _ in mixed])]}")
print(f"  [机理] 小 n 区（如 n=8-18）链近邻间距 ~1.4-1.6 大于'对角'近邻（±3 步、小半径），")
print(f"         k=3 壳被对角节点占据 → 非梯子；中段 n 恢复梯子，直至 ~112。")
print(f"  n=60 属全梯子段（与 Section 1 逐边审计 60/60 一致），且 n_α={n_alpha:.4f} 落在其中。")
print(f"  → 梯子结构本身不承担巧合；承担巧合的只有：胞腔复形积 |E|·β1 = 60")
print(f"    落入 α 交叉窗口（1% 窗口内唯一偶整数）。")

# ════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("S6  残差分析")
print("=" * 78)
g60 = ladder_gap(60)
print(f"  gap(M_60)          = {g60:.15f}")
print(f"  α (CODATA 2018)    = {a:.15f}")
print(f"  α (CODATA 2022)    = {ALPHA_2022:.15f}")
print(f"  残差（绝对）        = {g60 - a:.3e}")
print(f"  残差（相对 2018）   = {(g60 - a) / a:.3e}")
print(f"  残差（相对 2022）   = {(g60 - ALPHA_2022) / ALPHA_2022:.3e}")
print(f"  残差 / 实验不确定度 ≈ {(g60 - a) / a / ALPHA_UNC_REL:.1e} 倍")
print(f"  → 残差比实验精度大 ~5 个数量级，不是舍入噪声；")
print(f"    任何'真推导'解释必须产生恰好该尺寸的修正，目前无候选机制。")

# ════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("S7  Maxwell.py 设计常数来源表（来源审计，非计算）")
print("=" * 78)
sigma_num = [13, 13, 0, 11, 12, 12, 10, 10, 13, 11, 12, 8]
print(f"  σ_edge = k/38，k ∈ {sigma_num}（12 条边），Σk = {sum(sigma_num)}")
prov = [
    ("|V|=8, |E|=12, β1=5 (D_edge 结构)", "作者设计输入", "是（n=|E|×β1=60）"),
    ("σ_edge = k/38", "作者设计输入（38 来源未明）", "否（不进入 n）"),
    ("ALPHA_0_DYNAMIC = 21.09256", "作者设计输入", "否"),
    ("GAMMA_LATENCY = 0.0585", "作者设计输入", "否"),
    ("THETA_CONFORMAL = κ = 0.828", "作者设计输入（3 位有效数字）", "否（仅进入 λ₀ 链）"),
]
for name, src, enters_n in prov:
    print(f"  {name:<38} | {src:<28} | 进入 n=60: {enters_n}")
print("  → n=60 的先验性在'脚本层面'成立，但 (8,12,5) 本身是设计选择，")
print("    尚无从 SRE 公理出发的独立推导。")

out = {
    "purpose": "Tier0 theory re-audit: exact characterization of the n=60 / M_60 gap / alpha coincidence",
    "n_alpha_exact": float(n_alpha),
    "n_alpha_minus_60": float(n_alpha - 60),
    "one_pct_window": [float(n_lo), float(n_hi)],
    "one_pct_window_width": float(width),
    "prob_specific_even_integer_hit_pct": float(width / span * 100),
    "prob_at_least_one_even_hit_pct": float(99 * width / span * 100),
    "prob_cell_complex_product_is_the_hit_pct": float(100 / 99),
    "unique_even_hits_1pct": [int(x) for x in hits1pct],
    "exp_precision_window_dn": float(dn_exp),
    "integer_n_can_reach_exp_precision": False,
    "gap_M60_algebraic_degree_le": int(phi60) // 2,
    "ladder_full_segments_w01": [list(r) for r in ranges(full)],
    "ladder_zero_segments_w01": [list(r) for r in ranges(none_ladder)],
    "ladder_mixed_segments_w01": [list(r) for r in ranges([n for n, _ in mixed])],
    "residual_abs": float(g60 - a),
    "residual_rel_2018": float((g60 - a) / a),
    "residual_rel_2022": float((g60 - ALPHA_2022) / ALPHA_2022),
    "residual_over_exp_unc": float((g60 - a) / a / ALPHA_UNC_REL),
    "maxwell_design_constants": {
        "sigma_edge_numerators": sigma_num, "denominator": 38,
        "alpha0_dynamic": 21.09256, "gamma_latency": 0.0585,
        "theta_conformal_kappa": 0.828,
        "enter_n60": ["|V|=8", "|E|=12", "beta1=5"]},
}
with open(r"c:\mywork\vasp\tier0_theoryreaudit_results.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n  已保存 tier0_theoryreaudit_results.json")
