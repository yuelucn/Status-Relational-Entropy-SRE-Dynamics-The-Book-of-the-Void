"""
第二验证：使用 Maxwell.md §3.2 显式给出的 L^(3) 矩阵,
以及 ALPHA_0_DYNAMIC=21.09256 等代码常数的组合, 继续搜索 1/137。

§3.2 公式:
  σ_e = Tr(D̂_ij · Ĉ) · det(L^(1)_{[m,m]}) / det(L^(3)_{[m,m]}) · Ω(α_{0,dynamic})

  ALPHA_0_DYNAMIC = 21.09256
  GAMMA_LATENCY = 0.0585
  THETA_CONFORMAL = 0.828

物理关系: α = e²/(4πε₀ℏc) = Z₀·e²/(2h) = Z₀/(2·R_K)
SRE 中 e≡1, h≡1 → α = Z₀/2
若 Z₀ = dim(F)/dim(E) = 5/12 → α = 5/24 ≈ 0.2083 (不是 1/137)

也许 Z₀ 不是简单的维数比, 而是谱加权的比。
"""
import numpy as np
np.set_printoptions(precision=10, suppress=True)

ALPHA_TARGET = 1.0 / 137.035999084
print(f"目标: α = {ALPHA_TARGET:.10f}\n")

# §3.2 显式给出的 L^(3) for K_{3,5}
L3 = np.array([
    [ 9, -2, -2, -2, -3,  0,  0,  0],
    [-2, 15,  0,  0,  0, -4, -5, -4],
    [-2,  0, 11,  0,  0, -3, -3, -3],
    [-2,  0,  0, 11,  0, -3, -3, -3],
    [-3,  0,  0,  0, 12, -3, -3, -3],
    [ 0, -4, -3, -3, -3, 13,  0,  0],
    [ 0, -5, -3, -3, -3,  0, 14,  0],
    [ 0, -4, -3, -3, -3,  0,  0, 13]
], dtype=np.float64)

# D_edge, C_cycle (同前)
D_edge = np.array([
    [ 1, -1,  0,  0,  0,  0,  0,  0], [ 0,  1, -1,  0,  0,  0,  0,  0],
    [ 0,  0,  1, -1,  0,  0,  0,  0], [ 0,  0,  0,  1, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  1, -1,  0,  0], [ 0,  0,  0,  0,  0,  1, -1,  0],
    [ 0,  0,  0,  0,  0,  0,  1, -1], [-1,  0,  0,  0,  0,  0,  0,  1],
    [ 1,  0, -1,  0,  0,  0,  0,  0], [ 0,  1,  0, -1,  0,  0,  0,  0],
    [ 0,  0,  1,  0, -1,  0,  0,  0], [ 0,  0,  0,  0,  1,  0,  0, -1]
], dtype=np.float64)

C_cycle = np.array([
    [ 1,  1,  0,  0, -1,  0,  0,  1,  0,  0,  0,  0],
    [ 0,  1,  1,  0,  0, -1,  0,  0,  1,  0,  0,  0],
    [ 0,  0,  1,  1,  0,  0, -1,  0,  0,  1,  0,  0],
    [ 1,  0,  0,  1,  0,  0,  0, -1,  0,  0,  1,  0],
    [ 0,  0,  0,  0,  1,  1,  1,  0,  0,  0,  0, -1]
], dtype=np.float64)

# 1st-order Graph Laplacian
A = np.zeros((8, 8))
for i in range(3):
    for j in range(3, 8):
        A[i, j] = 1; A[j, i] = 1
L1_graph = np.diag(A.sum(1)) - A

# 代码常量
ALPHA_0 = 21.09256
GAMMA = 0.0585
THETA = 0.828

results = []
def check(name, val):
    err = abs(val - ALPHA_TARGET) / ALPHA_TARGET
    tag = "★ MATCH" if err < 0.01 else ("~ close" if err < 0.1 else "")
    results.append((name, val, err, tag))
    print(f"  {name:<55s} = {val:>14.10f}  (err={err:.2%})  {tag}")

# ── L^(3) 谱性质 ──
print("=" * 80)
print("L^(3) 谱性质 (§3.2 显式矩阵)")
print("=" * 40)
ev3 = np.linalg.eigvalsh(L3)
print(f"  特征值: {ev3}")
print(f"  λ_min = {ev3[0]:.6f}")
print(f"  λ_max = {ev3[-1]:.6f}")
print(f"  cond(L3) = {np.linalg.cond(L3):.6f}")
print(f"  det(L3) = {np.linalg.det(L3):.6f}")
print(f"  Tr(L3) = {np.trace(L3):.6f}")
check("L3: 1/ρ", 1.0 / ev3[-1])
check("L3: λ_min/λ_max", ev3[0] / ev3[-1])
check("L3: 1/cond", 1.0 / np.linalg.cond(L3))
check("L3: λ_min/Tr", ev3[0] / np.trace(L3))
check("L3: det(L1)/det(L3)", np.linalg.det(L1_graph) / np.linalg.det(L3))

# ── det 比率 (§3.2 的 σ_e 公式核心) ──
print()
print("=" * 80)
print("det(L^(1)) / det(L^(3)) 比率 (§3.2 σ_e 公式)")
print("=" * 40)
det_L1 = np.linalg.det(L1_graph)
det_L3 = np.linalg.det(L3)
ratio_det = det_L1 / det_L3
print(f"  det(L^(1)) = {det_L1:.6f}")
print(f"  det(L^(3)) = {det_L3:.6f}")
print(f"  det(L1)/det(L3) = {ratio_det:.10f}")
check("det(L1)/det(L3)", ratio_det)
check("1/(det(L1)/det(L3))", 1.0 / ratio_det)
check("sqrt(det(L1)/det(L3))", np.sqrt(ratio_det))

# 对各子矩阵 [m,m] 的余子式
for m in range(8):
    sub1 = np.delete(np.delete(L1_graph, m, 0), m, 1)
    sub3 = np.delete(np.delete(L3, m, 0), m, 1)
    d1 = np.linalg.det(sub1)
    d3 = np.linalg.det(sub3)
    r = d1 / d3
    check(f"det(L1[{m},{m}])/det(L3[{m},{m}])", r)

# ── 代码常数的组合 ──
print()
print("=" * 80)
print("代码常数组合 (ALPHA_0=21.09256, GAMMA=0.0585, THETA=0.828)")
print("=" * 40)
check("1/ALPHA_0", 1.0 / ALPHA_0)
check("GAMMA", GAMMA)
check("1/THETA", 1.0 / THETA)
check("GAMMA/THETA", GAMMA / THETA)
check("GAMMA*THETA", GAMMA * THETA)
check("GAMMA/ALPHA_0", GAMMA / ALPHA_0)
check("1/(ALPHA_0*GAMMA)", 1.0 / (ALPHA_0 * GAMMA))
check("(GAMMA/ALPHA_0)*THETA", (GAMMA / ALPHA_0) * THETA)
check("1/(ALPHA_0*THETA)", 1.0 / (ALPHA_0 * THETA))
check("GAMMA²*ALPHA_0", GAMMA**2 * ALPHA_0)
check("1/(ALPHA_0*GAMMA*THETA)", 1.0 / (ALPHA_0 * GAMMA * THETA))
check("THETA/(ALPHA_0*GAMMA)", THETA / (ALPHA_0 * GAMMA))
# α = 1/137 ≈ 0.0073; GAMMA = 0.0585; 0.0585/8 = 0.00731
check("GAMMA/8", GAMMA / 8)
check("GAMMA/(ALPHA_0-3.0)", GAMMA / (ALPHA_0 - 3.0))
check("GAMMA*ALPHA_0/THETA²", GAMMA * ALPHA_0 / THETA**2)

# ── Z_0 的谱加权 ──
print()
print("=" * 80)
print("Z_0 谱加权 (代替简单维数比)")
print("=" * 40)

# Hodge Laplacian
L_hodge = D_edge @ D_edge.T + C_cycle.T @ C_cycle
ev_H = np.linalg.eigvalsh(L_hodge)
# 节点拉普拉斯
L_node = D_edge.T @ D_edge
ev_N = np.linalg.eigvalsh(L_node)
# 环拉普拉斯
L_cycle = C_cycle @ C_cycle.T
ev_C = np.linalg.eigvalsh(L_cycle)

# Z_0 的谱加权版本
Z0_dim = 5.0 / 12.0
# 用非零特征值之和代替维数
sum_node = np.sum(ev_N[ev_N > 1e-10])
sum_cycle = np.sum(ev_C[ev_C > 1e-10])
sum_hodge_edge = np.sum(ev_H[ev_H > 1e-10])
Z0_spec1 = sum_cycle / sum_node
Z0_spec2 = sum_cycle / sum_hodge_edge
Z0_spec3 = sum_cycle / (sum_node + sum_cycle)

check("Z0_spec1 = Σλ_cycle/Σλ_node", Z0_spec1)
check("Z0_spec2 = Σλ_cycle/Σλ_hodge", Z0_spec2)
check("Z0_spec3 = Σλ_cycle/Σ(node+cycle)", Z0_spec3)

# α = Z0/2 的各种版本
check("Z0_dim/2", Z0_dim / 2)
check("Z0_spec1/2", Z0_spec1 / 2)
check("Z0_spec2/2", Z0_spec2 / 2)
check("Z0_spec3/2", Z0_spec3 / 2)

# 也许 Z_0 = Tr(C^T·C)/Tr(D^T·D) 是对的但需要不同图
# 物理上 Z_0 = 376.73Ω, α = e²Z_0/(2h) = Z_0/(2R_K), R_K = h/e² = 25812.8Ω
# α = Z_0/(2·25812.8) = 376.73/51625.6 = 0.007297
# 在 SRE: e≡1, h≡1, R_K = 1/1 = 1, α = Z_0/2
# 若 Z_0 = 5/12 → α = 5/24 = 0.2083 (不对)
# 需要 Z_0 ≈ 0.014594 → dim(F)/dim(E) ≈ 1/68.5

# 也许 α 不是从 Z_0/2 来, 而是独立量
# α ≈ 1/(π·11³) ? No, π·11³ = 4181
# 1/137 in various powers: 137 = 1/α
# 137 ≈ 1/(2π·Z₀·(e/h)²) ??

# ── 谱间隙比 ──
print()
print("=" * 80)
print("谱间隙比 (各种 Laplacian)")
print("=" * 40)

# 图拉普拉斯谱间隙
gap_graph = ev_N[1] / ev_N[-1]  # λ₂/λ_max
gap_hodge = ev_H[ev_H > 1e-10][0] / ev_H[-1]
gap_cycle = ev_C[0] / ev_C[-1]
gap_L3 = ev3[0] / ev3[-1]

check("gap(L_graph) = λ₂/ρ", gap_graph)
check("gap(L_hodge) = λ_min_nz/ρ", gap_hodge)
check("gap(L_cycle) = λ_min/ρ", gap_cycle)
check("gap(L3) = λ_min/ρ", gap_L3)

# 谱间隙的幂
check("gap(L_graph)²", gap_graph**2)
check("gap(L_hodge)²", gap_hodge**2)
check("gap(L3)²", gap_L3**2)
check("gap(L3)³", gap_L3**3)
check("gap(L_graph)³", gap_graph**3)

# det 比率 × 谱间隙
check("det(L1)/det(L3) · gap(L3)", ratio_det * gap_L3)
check("det(L1)/det(L3) · gap(L_graph)", ratio_det * gap_graph)

# ── 更复杂的组合 ──
print()
print("=" * 80)
print("复杂组合 (det比 × 谱量 × 常数)")
print("=" * 40)
check("det_ratio · GAMMA", ratio_det * GAMMA)
check("det_ratio · GAMMA · THETA", ratio_det * GAMMA * THETA)
check("det_ratio · gap(L3) · GAMMA", ratio_det * gap_L3 * GAMMA)
check("det_ratio / ALPHA_0", ratio_det / ALPHA_0)
check("det_ratio · GAMMA / ALPHA_0", ratio_det * GAMMA / ALPHA_0)
check("GAMMA · gap(L3) / ALPHA_0", GAMMA * gap_L3 / ALPHA_0)
check("GAMMA · gap(L_hodge) / ALPHA_0", GAMMA * gap_hodge / ALPHA_0)
check("GAMMA · gap(L_graph) / ALPHA_0", GAMMA * gap_graph / ALPHA_0)
check("GAMMA / (ALPHA_0 · THETA)", GAMMA / (ALPHA_0 * THETA))
check("GAMMA · THETA / ALPHA_0", GAMMA * THETA / ALPHA_0)
check("1 / (ALPHA_0 · GAMMA · THETA)", 1.0 / (ALPHA_0 * GAMMA * THETA))

# ── 总结 ──
print()
print("=" * 80)
print("汇总: 最接近 1/137.036 的前 15 名")
print("=" * 80)
results.sort(key=lambda x: x[2])
for name, val, err, tag in results[:15]:
    print(f"  {val:>14.10f}  (err={err:.4%})  {tag:<8s} {name}")

print(f"\n目标: {ALPHA_TARGET:.10f}")
best = results[0]
print(f"最佳: {best[1]:.10f}  (err={best[2]:.2%})  {best[0]}")
