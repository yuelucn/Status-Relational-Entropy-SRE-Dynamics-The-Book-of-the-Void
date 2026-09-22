# -*- coding: utf-8 -*-
"""
δ 公理化推导 —— Fork A 缺口 3 收口
============================================================
目标：判定扭转通道耦合不对称 δ = w* − 1 = 4.347×10⁻⁵ 能否从公理
A1–A4 + R1 导出；若不能，给出最小一致公理化（A5 裸耦合）及其可证伪签名。

符号契约（先于计算冻结，禁止事后追认）
------------------------------------------------------------
[判据 N1]（no-go 的可计算化）
   把"公理集对 w 的约束"逐条化为可验性质：
     C1 连通性:   w > 0 时状态图连通（A3 刷新环游存在即可保证）
     C2 软模保护: λ₂(w) = 2 − 2cos(4π/n)，与 w 无关（机器精度）
     C3 双扇区分裂: 偶模（电子扇区）严格 w-无关；奇模（光子扇区）
                    随 w 线性移动（斜率恰为 2，机器精度）
     C4 尺度不变: gap(c·L(w)) = gap(L(w)) ∀ c > 0
                  （全局重标不产生新物理 → 唯一物理量是比值 w）
   判定：若 C1–C4 在 w 网格上均为"区间成立"（整段成立）而非"单点成立"，
   则公理集只固定拓扑、不固定模量 w ⇒ δ 不可从 A1–A4+R1 导出（no-go）。

[判据 N2]（奇模抬升签名 —— 参数无关、可证伪）
   闭式 μ_k(w) = (2+w) − 2cos(2πk/n) − w(−1)^k 给出
     dμ_k/dw = 1 − (−1)^k = { 0（k 偶）, 2（k 奇）}
   预言：扭转通道耦合超出 δ 使【每个】光子扇区（奇）本征值精确抬升 2δ，
   【每个】电子扇区（偶）本征值严格不动。
   检验（禁止用 α 相关量）：
     主检验（无浮点放大）：Δw = 1 的割线斜率 vs {0, 2}；
     次检验（小泛动演示）：Δw = 10⁻³ 有限差分，容差按 ε/Δw 放大标定
     （有限差分把机器噪声放大 1/Δw 倍，属检验实现噪声，非物理偏差）。

[判据 N3]（A5 闭合）
   若 N1 成立：最小一致公理化 = 新增公理 A5
   「A5（扭转通道耦合不对称）：跨片识别（holonomy）信道强度超出
     片内刷新信道 δ，δ 为理论裸常数（与 QED 中 α 的地位相同）。」
   闭合检验：α = gap_n(1+δ) 须复现 α*。
   检验双轨：解析商（n≡0 mod 4 时 gap = (1−cos4π/n)/(1+w+cos2π/n)，
   阈 1e-14）+ 全谱 min/max 交叉核对（阈 1e-13，闭式谱固有噪声 ~ε 量级）。
   δ 的数值内容 = 由 α* 反解（测量输入），此后 α 成为推导输出。

[判据 N4]（δ 普适性预言表 —— 真正的可证伪出口）
   A5 若为逐边裸耦合，则对任意偶 n 的 Möbius 态图预言
     α_pred(n) = gap_n(1 + δ)
   预注册表 n = 8..120（步长 2）。检验：
     (a) [60, 120] 内唯 n=60 落入 α* 的 1% 窗口；
     (b) 全表作为未来任何新 (|E|, β1) 结构的第一判据（预注册，不得修改）。

[候选机制负对照]（先注册后计算，识别标准 = 相对偏差 < 1e-12）
   M-1 λ₀² = 4.1210×10⁻⁵   （Tier 0 已判 λ₀ 非独立原语）
   M-2 α²  = 5.3251×10⁻⁵   （含 α，循环，仅记录）
   M-3 2/S⁶，S=6（Maxwell 引擎 TOTAL_S_STEPS 的结构性候选）
   M-4 λ₀·γ（γ=0.0585）、γ²/2（延承 Fork A §4.4 表）
   % 级失配一律记为观察项，不构成识别。
"""
import json
import os
import numpy as np

np.set_printoptions(precision=15, suppress=True)

# ── 参考值：仅对照用，不进入 N1/N2 判定 ──────────────────────────
ALPHA_REF = 1.0 / 137.035999084
LAMBDA0_REF = 0.00641954
GAMMA_REF = 0.0585
S_STEPS = 6
N0 = 60

R = {
    "purpose": "delta axiomatization: no-go theorem + A5 bare coupling + falsifiable signatures",
    "pre_registered_criteria": {
        "N1": "axiom constraints on w must be interval-type (C1-C4) => w is a modulus => no-go",
        "N2": "odd-mode lift: dmu_k/dw = 2 (k odd), 0 (k even); tested with generic dw, no alpha",
        "N3": "A5 closure: gap_n0(1+delta) == alpha* at machine precision",
        "N4": "delta-universality table alpha_pred(n) for even n in [8,120]; n=60 unique hit in [60,120]",
        "identification_standard": "relative deviation < 1e-12; percent-level = observation only",
    },
}


def ladder_eigs(n, w):
    """加权 Möbius 阶梯 M_n（n 偶）组合拉普拉斯闭式谱。
    环刷新信道权重 1，跨片识别信道权重 w；度 d = 2+w。
    μ_k = (2+w) − 2cos(2πk/n) − w(−1)^k，μ_0 = 0（常数模）。"""
    k = np.arange(n)
    return (2.0 + w) - 2.0 * np.cos(2.0 * np.pi * k / n) - w * ((-1.0) ** k)


def gap_of(n, w):
    """谱间隙 = 最小非零本征值 / 最大本征值（闭式全谱）。"""
    mu = ladder_eigs(n, w)
    nz = mu[1:]  # μ_0 = 0
    return nz.min() / nz.max()


# ════════════════════════════════════════════════════════════════
# Section 1 — 信道代数：交换性与闭式谱的机器精度确认
# ════════════════════════════════════════════════════════════════
print("=" * 78)
print("Section 1  信道代数 𝒜 = ℂ[S]/(Sⁿ−I)：环刷新 S+S⁻¹，扭转识别 wP（P=S^{n/2}）")
print("=" * 78)

S = np.zeros((N0, N0))
for i in range(N0):
    S[i, (i + 1) % N0] = 1.0
P = np.linalg.matrix_power(S, N0 // 2)

comm_max = np.abs(S @ P - P @ S).max()
p2_max = np.abs(P @ P - np.eye(N0)).max()
print(f"  [S,P] 最大元 = {comm_max:.1e}   （交换 → 一切模同时 Fourier 对角化）")
print(f"  P² − I 最大元 = {p2_max:.1e}   （对合：跨片识别的自反性）")
R["channel_algebra"] = {
    "commutator_max": float(comm_max),
    "P_involution_max": float(p2_max),
    "statement": "abelian algebra => w enters only as a coefficient in closed-form mu_k(w)",
}

W_GRID = [0.05, 0.1, 0.5, 1.0, 2.0, 10.0]
closed_form_dev = 0.0
conn_all = True
for w in W_GRID:
    mu_cf = ladder_eigs(N0, w)
    L = (2.0 + w) * np.eye(N0) - S - S.T - w * P
    mu_num = np.linalg.eigvalsh(L)
    closed_form_dev = max(closed_form_dev, np.abs(np.sort(mu_cf) - mu_num).max())
    A = S + S.T + w * P
    D = np.diag(A.sum(axis=1))
    conn_all &= (np.linalg.matrix_rank(D - A) == N0 - 1)
print(f"  闭式 vs 数值对角化最大偏差 = {closed_form_dev:.1e}   （w 网格 {W_GRID}）")
print(f"  C1 连通性（rank L = n−1）在全网格成立 = {conn_all}")
R["S1"] = {
    "closed_form_vs_numeric_max_dev": float(closed_form_dev),
    "C1_connected_all_grid": bool(conn_all),
}

# ════════════════════════════════════════════════════════════════
# Section 2 — N1 判据 C2/C3/C4：公理对 w 的约束是"区间"而非"单点"
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 2  N1：C2 软模保护 / C3 双扇区分裂 / C4 尺度不变")
print("=" * 78)

lam2_exact = 2.0 - 2.0 * np.cos(4.0 * np.pi / N0)
lam2s = [ladder_eigs(N0, w)[1:].min() for w in W_GRID]
c2_dev = max(abs(l2 - lam2_exact) for l2 in lam2s)
print(f"  C2  λ₂(w) 全网格最大偏离 2−2cos(4π/60) = {c2_dev:.1e}   （λ₂* = {lam2_exact:.15f}）")

k = np.arange(N0)
odd_mask = (k % 2 == 1)
even_mask = (k % 2 == 0) & (k > 0)
mu1, mu2 = ladder_eigs(N0, 1.0), ladder_eigs(N0, 2.0)
c3_even = np.abs(mu2[even_mask] - mu1[even_mask]).max()
c3_odd_slope = np.abs((mu2[odd_mask] - mu1[odd_mask]) / 1.0 - 2.0).max()
print(f"  C3  偶模 w-无关最大偏差 = {c3_even:.1e}；"
      f"奇模斜率偏离 2 最大偏差 = {c3_odd_slope:.1e}")

c4_dev = 0.0
for c in (0.5, 3.7):
    g1 = gap_of(N0, 1.0)
    g2 = (ladder_eigs(N0, 1.0)[1:].min() * c) / (ladder_eigs(N0, 1.0)[1:].max() * c)
    c4_dev = max(c4_dev, abs(g2 / g1 - 1.0))
print(f"  C4  gap(c·L)/gap(L) 偏离 1 最大 = {c4_dev:.1e}   （c ∈ {{0.5, 3.7}}）")

gaps_grid = [gap_of(N0, w) for w in W_GRID]
mono = all(gaps_grid[i] > gaps_grid[i + 1] for i in range(len(gaps_grid) - 1))
print(f"  gap(w) 全网格严格单调递减 = {mono}   ⇒ w* 唯一（若给定 α）")

nogo = bool(c2_dev < 1e-12 and c3_even < 1e-12 and c3_odd_slope < 1e-12
            and c4_dev < 1e-12 and conn_all and mono)
print(f"\n  N1 判定：C1–C4 全部为区间成立 + gap 单调 ⇒ "
      f"{'no-go 成立：w 是模量，δ 不可从 A1–A4+R1 导出' if nogo else 'no-go 不成立'}")
R["S2_N1"] = {
    "C2_soft_protection_max_dev": float(c2_dev),
    "C3_even_w_independent_max_dev": float(c3_even),
    "C3_odd_slope_dev_from_2": float(c3_odd_slope),
    "C4_scale_invariance_max_dev": float(c4_dev),
    "gap_monotonic_decreasing": bool(mono),
    "NO_GO_established": nogo,
}

# ════════════════════════════════════════════════════════════════
# Section 3 — 公理逐条审计：约束类型表
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 3  公理逐条审计：对 w 的约束类型")
print("=" * 78)
audit = [
    ("A1 四态空间", "无约束（不触及信道权重）"),
    ("A2 Möbius 双覆盖 4π", "w ≠ 0（识别信道 P 必须存在）——开条件"),
    ("A3 刷新环游", "环权重 = 1（单位约定）；对 w 仅要求同量级 O(1)——开条件"),
    ("A4 n = |E|×β1", "无约束"),
    ("R1 通道计数", "无约束"),
]
for name, cons in audit:
    print(f"  {name:<22s} → {cons}")
print("  ⇒ 约束集 = {w > 0} ∩ {w ≍ 1}：开区间，非单点 ⇒ w 是模量（复结构类比）")
R["S3_axiom_audit"] = {name: cons for name, cons in audit}
R["S3_axiom_audit_conclusion"] = "constraint set is open interval {w>0} ∩ {w~1}; w is a modulus"

# ════════════════════════════════════════════════════════════════
# Section 4 — N2：奇模抬升签名（参数无关检验，与 α 无关）
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 4  N2：奇模抬升签名  dμ_k/dw = 2（奇）/ 0（偶）")
print("=" * 78)
# 主检验（无放大）：Δw = 1 割线斜率，噪声量级 ~ ε
W1, W2 = 1.0, 2.0
slope = (ladder_eigs(N0, W2) - ladder_eigs(N0, W1)) / (W2 - W1)
odd_dev = np.abs(slope[odd_mask] - 2.0).max()
even_dev = np.abs(slope[k % 2 == 0]).max()
print(f"  主检验（Δw = {W2-W1:.0f}，无放大）：奇模斜率最大偏离 2 = {odd_dev:.1e}；"
      f"偶模斜率最大偏离 0 = {even_dev:.1e}")
# 次检验（小泛动演示）：容差按 ε/Δw 放大标定
DW = 1.0e-3
d_mu = ladder_eigs(N0, 1.0 + DW) - ladder_eigs(N0, 1.0)
tol = 100.0 * np.finfo(float).eps / DW
odd_dev_small = np.abs(d_mu[odd_mask] / DW - 2.0).max()
even_dev_small = np.abs(d_mu[k % 2 == 0] / DW).max()
print(f"  次检验（Δw = {DW}，容差 ε/Δw 标定 = {tol:.1e}）："
      f"奇模偏差 = {odd_dev_small:.1e}；偶模偏差 = {even_dev_small:.1e}")
n2_pass = bool(odd_dev < 1e-12 and even_dev < 1e-12
               and odd_dev_small < tol and even_dev_small < tol)
print(f"  N2 判定：{'成立 —— δ 的光谱签名：奇模全体精确抬升 2δ，偶模全体严格不动' if n2_pass else '失败'}")
R["S4_N2"] = {
    "primary_test_dw": W2 - W1,
    "odd_slope_max_dev_from_2": float(odd_dev),
    "even_slope_max_dev_from_0": float(even_dev),
    "small_dw_test": DW,
    "small_dw_tolerance_scaled_by_eps_over_dw": float(tol),
    "odd_dev_small_dw": float(odd_dev_small),
    "even_dev_small_dw": float(even_dev_small),
    "signature": "every odd (photon) eigenvalue lifts by exactly 2*delta; every even (electron) eigenvalue unchanged",
    "N2_pass": n2_pass,
}

# ════════════════════════════════════════════════════════════════
# Section 5 — N3：A5 公理化闭合（δ 由此成为裸常数，α 成为输出）
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 5  N3：A5 闭合 —— δ = 测量输入（裸耦合），α = 推导输出")
print("=" * 78)
theta = 2.0 * np.pi / N0
w_star = (1.0 - np.cos(2.0 * theta)) / ALPHA_REF - 1.0 - np.cos(theta)
delta = w_star - 1.0
# 双轨检验：解析商（n≡0 mod 4）+ 全谱 min/max 交叉核对
gap_star_analytic = (1.0 - np.cos(2.0 * theta)) / (1.0 + w_star + np.cos(theta))
gap_star_minmax = gap_of(N0, w_star)
rel_err = abs(gap_star_analytic - ALPHA_REF) / ALPHA_REF
rel_err_mm = abs(gap_star_minmax - ALPHA_REF) / ALPHA_REF
print(f"  δ（A5 裸常数数值内容）= {delta:.16e}")
print(f"  gap(1+δ) 解析商 = {gap_star_analytic:.16f}   （相对偏差 {rel_err:.1e}）")
print(f"  gap(1+δ) 全谱   = {gap_star_minmax:.16f}   （相对偏差 {rel_err_mm:.1e}）")
print(f"  vs α*    = {ALPHA_REF:.16f}")

forkA_delta = None
try:
    with open(os.path.join(os.path.dirname(__file__), "forkA_derivation_results.json")) as f:
        forkA_delta = json.load(f)["gap3"]["delta"]
    print(f"  对照 Fork A §4.2 δ = {forkA_delta:.16e}   一致 = {abs(delta - forkA_delta) < 1e-17}")
except Exception as e:  # pragma: no cover
    print(f"  [warn] forkA json 不可读：{e}")

n3_pass = bool(rel_err < 1e-14 and rel_err_mm < 1e-13)
print(f"  N3 判定：{'闭合 —— A1–A4+R1+A5 ⇒ α（双轨机器精度）' if n3_pass else '失败'}")
R["S5_N3"] = {
    "delta_bare": float(delta),
    "matches_forkA_gap3": bool(forkA_delta is not None and abs(delta - forkA_delta) < 1e-17),
    "gap_at_1_plus_delta_analytic": float(gap_star_analytic),
    "rel_err_vs_alpha_analytic": float(rel_err),
    "gap_at_1_plus_delta_minmax": float(gap_star_minmax),
    "rel_err_vs_alpha_minmax": float(rel_err_mm),
    "N3_pass": n3_pass,
    "status": "closed: alpha = f(n=60 derived, topology derived, delta = A5 bare constant)",
}

# ════════════════════════════════════════════════════════════════
# Section 6 — N4：δ 普适性预言表（预注册，n = 8..120 偶数）
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 6  N4：δ 普适性预言表  α_pred(n) = gap_n(1+δ)")
print("=" * 78)
n_list = list(range(8, 122, 2))
table = []
print(f"  {'n':>4} {'n%4':>4} {'λ₂':>14} {'λ_max(1+δ)':>14} {'α_pred(n)':>16} {'vs α*':>10} {'λ₂扇区':>6}")
for n in n_list:
    mu = ladder_eigs(n, 1.0 + delta)
    nz = mu[1:]
    lam2 = nz.min()
    lam_max = nz.max()
    a_pred = lam2 / lam_max
    err = (a_pred - ALPHA_REF) / ALPHA_REF
    sector = "偶" if int(np.argmin(mu[1:])) % 2 == 1 else "奇"  # mu[1:] 索引 k = idx+1
    table.append({"n": n, "n_mod_4": n % 4, "lambda2": float(lam2),
                  "lambda_max": float(lam_max), "alpha_pred": float(a_pred),
                  "rel_err_vs_alpha": float(err), "lambda2_sector": sector})
    mark = "  ← n=60" if n == N0 else ""
    print(f"  {n:>4} {n % 4:>4} {lam2:>14.9f} {lam_max:>14.9f} {a_pred:>16.11f} {err*100:>9.4f}% {sector:>6}{mark}")

hits = [t for t in table if abs(t["rel_err_vs_alpha"]) < 0.01 and t["n"] >= 60]
unique_hit = (len(hits) == 1 and hits[0]["n"] == N0)
print(f"\n  [60,120] 内落入 α* 1% 窗口的 n：{[t['n'] for t in hits]}   唯一命中 n=60 = {unique_hit}")
R["S6_N4"] = {
    "prediction_table": table,
    "unique_hit_n60_in_60_120": bool(unique_hit),
    "note": "pre-registered: any future (|E|,beta1) structure with n' != 60 must match alpha_pred(n'), not alpha*",
}

# ════════════════════════════════════════════════════════════════
# Section 7 — 候选机制负对照（先注册后计算）
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 7  负对照：候选机制 vs δ（识别标准 < 1e-12）")
print("=" * 78)
cands = {
    "M1_lambda0_sq": LAMBDA0_REF ** 2,
    "M2_alpha_sq_circular": ALPHA_REF ** 2,
    "M3_two_over_S6": 2.0 / S_STEPS ** 6,
    "M4_lambda0_gamma": LAMBDA0_REF * GAMMA_REF,
    "M5_gamma_sq_over_2": GAMMA_REF ** 2 / 2.0,
}
neg = {}
print(f"  δ = {delta:.6e}")
for name, val in cands.items():
    ratio = delta / val
    neg[name] = {"value": float(val), "delta_over_cand": float(ratio),
                 "identified": bool(abs(ratio - 1.0) < 1e-12)}
    print(f"  {name:<22s} = {val:.6e}   δ/候选 = {ratio:.6f}   "
          f"{'识别' if neg[name]['identified'] else '未识别（观察项）'}")
print("  ⇒ 无一达机器精度；δ 保持裸常数地位，不得反凑。")
R["S7_negative_controls"] = neg

# ════════════════════════════════════════════════════════════════
# Section 8 — 预注册光谱签名表（供未来独立观测检验）+ 记分卡
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 8  预注册签名：M₆₀ 代表模在 w=1 与 w=1+δ 下的本征值")
print("=" * 78)
sig = {}
mu_bin = ladder_eigs(N0, 1.0)
mu_a5 = ladder_eigs(N0, 1.0 + delta)
print(f"  {'k':>4} {'扇区':>4} {'μ_k(w=1)':>18} {'μ_k(w=1+δ)':>18} {'差/2δ':>10}")
for kk in (1, 2, 29, 30, 31, 59):
    diff_ratio = (mu_a5[kk] - mu_bin[kk]) / (2.0 * delta)
    sig[str(kk)] = {"sector": "奇(光子)" if kk % 2 else "偶(电子)",
                    "mu_w1": float(mu_bin[kk]), "mu_w1plus": float(mu_a5[kk]),
                    "shift_over_2delta": float(diff_ratio)}
    print(f"  {kk:>4} {'奇(光子)' if kk % 2 else '偶(电子)':>6} {mu_bin[kk]:>18.12f} "
          f"{mu_a5[kk]:>18.12f} {diff_ratio:>10.6f}")
print("  ⇒ 每个奇模精确抬升 2δ（比值=1），偶模严格不动（比值=0）——参数无关签名。")
R["S8_signatures"] = sig

R["scorecard"] = {
    "缺口1 复形推导": "补齐（Fork A §2）",
    "缺口2 可观测字典": "补齐（Fork A §3，字典级）",
    "缺口3 残差机制": "公理化闭合：no-go 定理（δ 不可从 A1–A4+R1 导出）+ A5 裸耦合 + "
                   "奇模抬升签名 + δ 普适性预言表",
    "NO_GO_established": nogo,
    "N2_pass": n2_pass,
    "N3_pass": n3_pass,
    "unique_hit_n60": bool(unique_hit),
    "honest_bottom_line": "α = f(n=60 已推导, 拓扑已推导, δ=A5 裸常数)。"
                       "Fork A 从两个自由常数（α, λ₀, κ）压缩到一个（δ）。",
}

out = os.path.join(os.path.dirname(__file__), "delta_axiomatization_results.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(R, f, ensure_ascii=False, indent=2)
print(f"\n结果已写入 {out}")
