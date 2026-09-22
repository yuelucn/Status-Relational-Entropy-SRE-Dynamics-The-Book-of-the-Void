"""独立验证 sre_electronic_ops_v11.py 的关键数值（闭式解对照）。

验证项：
V1. 苯环 SRE 符号矩阵 M = 2(I+A_b) - J 的特征值 = {0, 4, 4, -2, 0, 0}（闭式解）
V2. 苯环 mobius_ratio = mean_k |tr(M^k)|/6^k（逐 k 闭式解对照）
V3. 苯环 lambda_2_loop = w（均匀权重 6-环的 Fiedler 值 = 边权重，闭式解）
V4. 苯环 kappa_loop = 4（均匀 6-环 κ = λmax/λ2 = 4w/w = 4，精确值）
V5. 乙醇增益因子排序定理 11.4：tanh 值闭式解
V6. A_s = W_e ⊙ P+ 与 op11 A_q 的一致性（L_q 谱 vs 手工构建）
"""
import numpy as np
import sys
sys.path.insert(0, r"c:\mywork\vasp")
from sre_electronic_ops_v11 import (
    build_sre_smooth_adjacency, sre_sign_matrix,
    operator_11_spin_charge_adjacency, operator_12_closed_loop_audit,
)

ok = True
def check(desc, cond):
    global ok
    print(("  [PASS] " if cond else "  [FAIL] ") + desc)
    if not cond:
        ok = False

print("=== 独立闭式解验证 v1.1 ===\n")

# ── V1: 苯环 M 特征值闭式解 ──
A_b = np.zeros((6, 6))
for i in range(6):
    A_b[i, (i + 1) % 6] = 1
    A_b[(i + 1) % 6, i] = 1
J = np.ones((6, 6))
M_theory = 2 * (np.eye(6) + A_b) - J
ev_theory = np.sort(np.linalg.eigvalsh(M_theory))
print("V1. 苯环 M 特征值（闭式解 2+4cos(2πm/6) − 6·δ）:")
print("     sorted:", np.round(ev_theory, 6).tolist())
# 闭式: 度2环 → M·1 = (2+4-6)·1 = 0; Fourier 模: 2+4cos(2πm/6), m=1..5
# = {0, 4, 4, -2, 0, 0}
expect = np.sort([0, 2+4*np.cos(np.pi/3), 2+4*np.cos(2*np.pi/3),
                  2+4*np.cos(np.pi), 2+4*np.cos(4*np.pi/3), 2+4*np.cos(5*np.pi/3)])
check("苯环 M 特征值 = 2+4cos(2πm/6) 闭式解", np.allclose(ev_theory, expect))

# ── V2: mobius_ratio 逐 k 闭式解 ──
# tr(M^k) = Σ λ_i^k = 2·4^k + (-2)^k（特征值 {4,4,-2,0,0,0}）
print("\nV2. 苯环 mobius_ratio（闭式解 2·4^k+(-2)^k）:")
theory_ratios = []
for k in range(3, 9):
    tr = 2 * 4.0**k + (-2.0)**k
    theory_ratios.append(abs(tr) / 6.0**k)
    print("     k=%d: |tr|/6^k = %.6f" % (k, theory_ratios[-1]))
benz_mobius_theory = float(np.mean(theory_ratios))

angles = np.linspace(0, 2 * np.pi, 7)[:-1]
benz_pos = np.column_stack([np.cos(angles), np.sin(angles), np.zeros(6)]) * 1.40
benz_A_s = build_sre_smooth_adjacency(benz_pos, atomtypes=["c3"] * 6)
benz_M = sre_sign_matrix(benz_A_s)
benz_op11 = operator_11_spin_charge_adjacency(benz_A_s, np.array([2.55]*6), rho=0.5)
benz_op12 = operator_12_closed_loop_audit(benz_op11["A_q"], benz_M, N_max=8)
print("     程序输出 mobius_ratio = %.6f, 闭式解 = %.6f" %
      (benz_op12["mobius_ratio"], benz_mobius_theory))
check("苯环 mobius_ratio 与闭式解一致 (<1e-9)",
      abs(benz_op12["mobius_ratio"] - benz_mobius_theory) < 1e-9)

# ── V3: 苯环 lambda_2_loop 闭式解 ──
# 均匀权重 w 的 6-环拉普拉斯特征值: w(2-2cos(2πm/6)) → λ2 = w·1, λmax = w·4
# 苯环全同原子, A_q = A_s（增益=1）, 子图=全图 → lambda_2_loop = λ2(L_q) = w
print("\nV3. 苯环 lambda_2_loop（闭式解 = 均匀边权重 w）:")
w_edge = benz_A_s[0, 1]  # 相邻键权重（对称）
print("     A_s 键权重 w = %.6f" % w_edge)
print("     程序 lambda_2_loop = %.6f" % benz_op12["lambda_2_loop"])
check("lambda_2_loop = w（均匀 6-环 Fiedler 值 = 边权重）",
      abs(benz_op12["lambda_2_loop"] - w_edge) < 1e-9)
# 交叉验证: 直接对 A_q 构造 L 并算 λ2
L_q = np.diag(benz_op11["A_q"].sum(axis=1)) - benz_op11["A_q"]
lam2_q = np.linalg.eigvalsh(L_q)[1]
check("lambda_2_loop = lambda_2_q（苯环全原子在环上）",
      abs(benz_op12["lambda_2_loop"] - lam2_q) < 1e-9)

# ── V4: kappa_loop = 4 精确值 ──
print("\nV4. 苯环 kappa_loop（闭式解 λmax/λ2 = 4w/w = 4）:")
print("     程序 kappa_loop = %.6f" % benz_op12["kappa_loop"])
check("kappa_loop = 4（精确）", abs(benz_op12["kappa_loop"] - 4.0) < 1e-9)

# ── V5: 增益因子 tanh 闭式解 ──
print("\nV5. 定理 11.4 增益排序（tanh 闭式解）:")
tOH = np.tanh(3.44 - 2.20)   # O-H: 0.8455
tCO = np.tanh(3.44 - 2.55)   # C-O: 0.7114
tCH = np.tanh(2.55 - 2.20)   # C-H: 0.3364
print("     tanh(1.24)=%.4f  tanh(0.89)=%.4f  tanh(0.35)=%.4f" % (tOH, tCO, tCH))
print("     增益: O-H=%.4f  C-O=%.4f  C-H=%.4f  C-C=1.0000" %
      (1+0.5*tOH, 1+0.5*tCO, 1+0.5*tCH))
check("O-H > C-O > C-H > C-C 增益排序",
      1+0.5*tOH > 1+0.5*tCO > 1+0.5*tCH > 1.0)

# ── V6: D1 修正验证——异核键一律增益（不再衰减）──
print("\nV6. D1 修正: 异核键增益 (原版 O-H 被衰减 0.577 → v1.1 增益 1.423):")
atomtypes = ["c3", "c3", "oh", "hc", "hc", "hc", "h1", "h1", "ho"]
chis = electronegativities_from_atomtypes = None
from sre_electronic_ops_v11 import electronegativities_from_atomtypes
chis = electronegativities_from_atomtypes(atomtypes)
pos = np.array([
    [0.0, 0.0, 0.0], [1.52, 0.0, 0.0], [2.15, 1.35, 0.0],
    [-0.5, 0.9, 0.3], [-0.5, -0.9, -0.3], [-0.5, 0.0, -0.9],
    [1.52, -0.9, 0.9], [1.52, 0.9, -0.9], [2.15, 1.35, 0.96],
])
ethanol_bonds = [(0,1),(0,3),(0,4),(0,5),(1,2),(1,6),(1,7),(2,8)]
A_s = build_sre_smooth_adjacency(pos, atomtypes=atomtypes, bonds=ethanol_bonds)
M_e = sre_sign_matrix(A_s)
op11 = operator_11_spin_charge_adjacency(A_s, chis, rho=0.5)
wq = op11["wq"]
gOH = 1 + 0.5 * wq[2, 8]
check("乙醇 O-H 增益 > 1（异核键增益而非衰减）", gOH > 1.0)
check("乙醇 O-H 增益 = 1.4228 = 1+0.5·tanh(1.24)",
      abs(gOH - (1 + 0.5 * np.tanh(1.24))) < 1e-12)
# D2: 权重与均值无关——平移所有 χ 不改变 A_q
chis_shift = chis + 100.0
op11_shift = operator_11_spin_charge_adjacency(A_s, chis_shift, rho=0.5)
check("D2: A_q 对 χ 平移不变（权重只依赖键内差）",
      np.allclose(op11["A_q"], op11_shift["A_q"]))
# 但诊断标量 max_spin_coupling 应保持 = tanh(max|dchi|)（定理 11.5）
check("max_spin_coupling = tanh(1.24)（定理 11.5）",
      abs(op11["max_spin_coupling"] - np.tanh(1.24)) < 1e-12)

# ── V7: D3 修正——乙醇开链无假阳性 ──
op12_e = operator_12_closed_loop_audit(op11["A_q"], M_e, N_max=8)
print("\nV7. D3 修正: 乙醇开链 n_loops = %d（原版 trace 法曾给假阳性共振）" % op12_e["n_loops"])
check("乙醇 n_loops = 0（树, β1=0）", op12_e["n_loops"] == 0)
check("苯环 n_loops = 1（β1=1）", benz_op12["n_loops"] == 1)

print("\n" + ("✅ 独立验证全部通过" if ok else "❌ 存在失败项"))
