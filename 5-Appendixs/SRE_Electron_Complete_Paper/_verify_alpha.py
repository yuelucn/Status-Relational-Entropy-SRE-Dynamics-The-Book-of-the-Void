"""
验证 SRE 理论中精细结构常数 α ≡ ρ_spectral(D_edge^T · P_E · Δ_cycle) ≈ 1/137.036

Maxwell.md §1.1 给出的公式:
  α ≡ ρ_spectral(D_edge^T · P_E · Δ_cycle)

其中:
  D_edge = 1st-order boundary matrix (edges × nodes)
  P_E = D_edge · (D_edge^T · D_edge)^† · D_edge^T  (projector onto edge space)
  Δ_cycle = ? (文档未显式定义，需穷举验证)

候选 Δ_cycle 解释:
  A. C_cycle^T          (coboundary: edges ← cycles, 12×5)
  B. C_cycle             (boundary: cycles ← edges, 5×12)
  C. C_cycle^T · C_cycle (cycle down-Laplacian, 12×12)
  D. C_cycle · C_cycle^T (cycle up-Laplacian, 5×5)
  E. Hodge Laplacian L₁ = D_edge·D_edge^T + C_cycle^T·C_cycle (12×12)

对每种解释，计算:
  1. 谱半径（最大 |特征值|）—— 仅对方阵
  2. 最大奇异值 σ_max —— 对任意矩阵
  3. λ_min/λ_max 比率
  4. 1/cond 比率
  5. 各种 trace/det 比率

目标: 找到 ≈ 1/137.035999 ≈ 0.00729735 的量
"""
import numpy as np
np.set_printoptions(precision=10, suppress=True)

# ── K_{3,5} 图的 D_edge 和 C_cycle（来自 Maxwell.py）──
D_edge = np.array([
    [ 1, -1,  0,  0,  0,  0,  0,  0], [ 0,  1, -1,  0,  0,  0,  0,  0],
    [ 0,  0,  1, -1,  0,  0,  0,  0], [ 0,  0,  0,  1, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  1, -1,  0,  0], [ 0,  0,  0,  0,  0,  1, -1,  0],
    [ 0,  0,  0,  0,  0,  0,  1, -1], [-1,  0,  0,  0,  0,  0,  0,  1],
    [ 1,  0, -1,  0,  0,  0,  0,  0], [ 0,  1,  0, -1,  0,  0,  0,  0],
    [ 0,  0,  1,  0, -1,  0,  0,  0], [ 0,  0,  0,  0,  1,  0,  0, -1]
], dtype=np.float64)  # (12, 8)

C_cycle = np.array([
    [ 1,  1,  0,  0, -1,  0,  0,  1,  0,  0,  0,  0],
    [ 0,  1,  1,  0,  0, -1,  0,  0,  1,  0,  0,  0],
    [ 0,  0,  1,  1,  0,  0, -1,  0,  0,  1,  0,  0],
    [ 1,  0,  0,  1,  0,  0,  0, -1,  0,  0,  1,  0],
    [ 0,  0,  0,  0,  1,  1,  1,  0,  0,  0,  0, -1]
], dtype=np.float64)  # (5, 12)

# 构建 P_E 投影矩阵
DtD = D_edge.T @ D_edge
P_E = D_edge @ np.linalg.pinv(DtD) @ D_edge.T  # (12, 12)

# 邻接矩阵 A（K_{3,5} 图）
n_nodes = 8
A = np.zeros((n_nodes, n_nodes))
# K_{3,5}: nodes 0-2 (part A, degree 5) connected to nodes 3-7 (part B, degree 3)
for i in range(3):
    for j in range(3, 8):
        A[i, j] = 1
        A[j, i] = 1
D_diag = np.diag(A.sum(axis=1))
L_graph = D_diag - A  # Graph Laplacian

# Hodge Laplacian on 1-forms (edge space)
L1_hodge = D_edge @ D_edge.T + C_cycle.T @ C_cycle  # (12, 12)

# 精细结构常数目标值
ALPHA_TARGET = 1.0 / 137.035999084
print(f"目标: α = 1/137.035999 = {ALPHA_TARGET:.10f}")
print(f"容差: ±0.0001 (即 {ALPHA_TARGET-0.0001:.6f} ~ {ALPHA_TARGET+0.0001:.6f})")
print()

results = []

def check(name, value):
    """检查是否接近 1/137"""
    diff = abs(value - ALPHA_TARGET)
    rel_err = diff / ALPHA_TARGET
    match = "★ MATCH" if rel_err < 0.01 else ""
    results.append((name, value, rel_err, match))
    print(f"  {name:<55s} = {value:>14.10f}  (err={rel_err:.2%})  {match}")

# ═══════════════════════════════════════════════════════════════
print("=" * 90)
print("A. Δ_cycle = C_cycle^T  (coboundary, 12×5)")
print("=" * 50)
M_A = D_edge.T @ P_E @ C_cycle.T  # (8, 12) @ (12, 12) @ (12, 5) = (8, 5)
# 简化: D_edge^T @ P_E = D_edge^T (pseudoinverse identity)
M_A_simplified = D_edge.T @ C_cycle.T  # (8, 5)
# 验证简化
print(f"  验证 ||D^T·P_E·C^T - D^T·C^T|| = {np.linalg.norm(M_A - M_A_simplified):.2e}")
# 非方阵: 用奇异值
sv_A = np.linalg.svd(M_A, compute_uv=False)
print(f"  奇异值: {sv_A}")
check("A1. σ_max(D^T·P_E·C^T)", sv_A[0])
check("A2. σ_min/σ_max", sv_A[-1] / sv_A[0])
check("A3. 1/σ_max", 1.0 / sv_A[0])
# M^T·M 的特征值 (5×5)
MtM_A = M_A.T @ M_A  # (5, 5)
ev_A = np.linalg.eigvalsh(MtM_A)
check("A4. λ_min(M^T·M)", ev_A[0])
check("A5. λ_min/λ_max(M^T·M)", ev_A[0] / ev_A[-1])
check("A6. 1/λ_max(M^T·M)", 1.0 / ev_A[-1])
check("A7. √(λ_min/λ_max)", np.sqrt(ev_A[0] / ev_A[-1]))

print()
print("=" * 90)
print("B. Δ_cycle = C_cycle  (boundary, 5×12)")
print("=" * 50)
# D^T (8×12) @ P_E (12×12) @ C_cycle (5×12) — 维度不匹配 (12×12)·(5×12)
# 只能做 D^T @ C_cycle，但 D^T (8×12) @ C_cycle (5×12) 也不匹配
# 需要 C_cycle^T 才能匹配... 跳过 B
print("  维度不匹配, 跳过")

print()
print("=" * 90)
print("C. Δ_cycle = C_cycle^T · C_cycle  (cycle down-Laplacian, 12×12)")
print("=" * 50)
Delta_C = C_cycle.T @ C_cycle  # (12, 12)
M_C = D_edge.T @ P_E @ Delta_C  # (8, 12) @ (12, 12) @ (12, 12) = (8, 12)
# 简化
M_C_simp = D_edge.T @ Delta_C  # (8, 12)
print(f"  验证简化: ||M - M_simp|| = {np.linalg.norm(M_C - M_C_simp):.2e}")
sv_C = np.linalg.svd(M_C, compute_uv=False)
print(f"  奇异值: {sv_C}")
check("C1. σ_max", sv_C[0])
check("C2. σ_min/σ_max", sv_C[-1] / sv_C[0])
check("C3. 1/σ_max", 1.0 / sv_C[0])
# M·M^T 特征值 (8×8)
MtM_C = M_C @ M_C.T  # (8, 8)
ev_C = np.linalg.eigvalsh(MtM_C)
check("C4. λ_min(M·M^T)", ev_C[0])
check("C5. λ_min/λ_max(M·M^T)", ev_C[0] / ev_C[-1])
check("C6. 1/λ_max(M·M^T)", 1.0 / ev_C[-1])
check("C7. √(λ_min/λ_max)", np.sqrt(ev_C[0] / ev_C[-1]))

print()
print("=" * 90)
print("D. Δ_cycle = C_cycle · C_cycle^T  (cycle up-Laplacian, 5×5)")
print("=" * 50)
# D^T (8×12) @ P_E (12×12) @ (C·C^T) (5×5) — 维度不匹配
# 只能直接算 C·C^T 的谱
Delta_D = C_cycle @ C_cycle.T  # (5, 5)
ev_D = np.linalg.eigvalsh(Delta_D)
print(f"  C·C^T 特征值: {ev_D}")
check("D1. ρ(C·C^T)", ev_D[-1])
check("D2. λ_min/λ_max", ev_D[0] / ev_D[-1])
check("D3. 1/λ_max", 1.0 / ev_D[-1])
check("D4. 1/ρ", 1.0 / ev_D[-1])

print()
print("=" * 90)
print("E. Hodge Laplacian L₁ = D·D^T + C^T·C  (12×12)")
print("=" * 50)
ev_E = np.linalg.eigvalsh(L1_hodge)
print(f"  L₁ 特征值: {np.sort(ev_E)}")
check("E1. ρ(L₁)", ev_E[-1])
check("E2. λ_min(L₁)", ev_E[0])
check("E3. λ_min/λ_max(L₁)", ev_E[0] / ev_E[-1])
check("E4. 1/ρ(L₁)", 1.0 / ev_E[-1])
check("E5. 1/cond(L₁)", 1.0 / np.linalg.cond(L1_hodge))

# 非零特征值
ev_E_nz = ev_E[ev_E > 1e-10]
check("E6. λ_min_nonzero/λ_max", ev_E_nz[0] / ev_E[-1])
check("E7. 1/(λ_max/λ_min_nonzero)", ev_E_nz[0] / ev_E[-1])
check("E8. √(λ_min_nonzero/λ_max)", np.sqrt(ev_E_nz[0] / ev_E[-1]))

print()
print("=" * 90)
print("F. Graph Laplacian L_graph = D - A  (8×8)")
print("=" * 50)
ev_F = np.linalg.eigvalsh(L_graph)
print(f"  L_graph 特征值: {ev_F}")
check("F1. λ₂(L_graph)", ev_F[1])
check("F2. λ_max(L_graph)", ev_F[-1])
check("F3. λ₂/λ_max", ev_F[1] / ev_F[-1])
check("F4. 1/(λ_max/λ₂)", ev_F[1] / ev_F[-1])
check("F5. 1/cond(L_graph)", 1.0 / np.linalg.cond(L_graph))

print()
print("=" * 90)
print("G. 组合算子: D·C^T, C·D, D^T·C^T·C·D 等")
print("=" * 50)

# G1: C_cycle · D_edge  (5×12 · 12×8 = 5×8)
M_G1 = C_cycle @ D_edge
sv_G1 = np.linalg.svd(M_G1, compute_uv=False)
check("G1. σ_max(C·D)", sv_G1[0])
check("G2. σ_min/σ_max(C·D)", sv_G1[-1] / sv_G1[0])
check("G3. 1/σ_max(C·D)", 1.0 / sv_G1[0])

# G2: D_edge^T · C_cycle^T · C_cycle · D_edge  (8×8)
M_G2 = D_edge.T @ C_cycle.T @ C_cycle @ D_edge  # (8×8)
ev_G2 = np.linalg.eigvalsh(M_G2)
check("G4. ρ(D^T·C^T·C·D)", ev_G2[-1])
check("G5. λ_min/λ_max(D^T·C^T·C·D)", ev_G2[0] / ev_G2[-1])
check("G6. 1/ρ(D^T·C^T·C·D)", 1.0 / ev_G2[-1])

# G3: 组合 D^T·D + C·C^T 的特征值比 (node + cycle Laplacians)
L_node = D_edge.T @ D_edge  # (8, 8) = graph Laplacian
L_cycle = C_cycle @ C_cycle.T  # (5, 5)
ev_node = np.linalg.eigvalsh(L_node)
ev_cycle = np.linalg.eigvalsh(L_cycle)
check("G7. λ₂(node)/ρ(cycle)", ev_node[1] / ev_cycle[-1])
check("G8. λ₂(cycle)/ρ(node)", ev_cycle[0] / ev_node[-1])
check("G9. λ₂(node)·λ₂(cycle)/(ρ_node·ρ_cycle)",
      (ev_node[1] * ev_cycle[0]) / (ev_node[-1] * ev_cycle[-1]))

print()
print("=" * 90)
print("H. 归一化算子 (D/||D||, C/||C|| 等)")
print("=" * 50)

# 归一化 D_edge 和 C_cycle
D_norm = D_edge / np.linalg.norm(D_edge, 'fro')
C_norm = C_cycle / np.linalg.norm(C_cycle, 'fro')

# H1: 归一化后的 D^T · C^T
M_H1 = D_norm.T @ C_norm.T  # (8, 5)
sv_H1 = np.linalg.svd(M_H1, compute_uv=False)
check("H1. σ_max(D̃^T·C̃^T)", sv_H1[0])
check("H2. σ_min/σ_max", sv_H1[-1] / sv_H1[0])
check("H3. 1/σ_max", 1.0 / sv_H1[0])

# H2: 归一化 Hodge Laplacian
L1_norm = (D_norm @ D_norm.T + C_norm.T @ C_norm)
ev_H2 = np.linalg.eigvalsh(L1_norm)
check("H4. λ_min_nonzero/λ_max(L̃₁)", ev_H2[ev_H2 > 1e-10][0] / ev_H2[-1])

# H3: 行归一化
D_rownorm = D_edge / np.linalg.norm(D_edge, axis=1, keepdims=True)
C_rownorm = C_cycle / np.linalg.norm(C_cycle, axis=1, keepdims=True)
M_H3 = D_rownorm.T @ C_rownorm.T
sv_H3 = np.linalg.svd(M_H3, compute_uv=False)
check("H5. σ_max(row-norm D^T·C^T)", sv_H3[0])
check("H6. 1/σ_max", 1.0 / sv_H3[0])

print()
print("=" * 90)
print("I. Z_0 比率 + 谱组合")
print("=" * 50)
Z0 = np.trace(C_cycle.T @ C_cycle) / np.trace(D_edge.T @ D_edge)
print(f"  Z_0 = Tr(C^T·C)/Tr(D^T·D) = {Z0:.6f}")
print(f"  dim(F)/dim(E) = {C_cycle.shape[0]}/{D_edge.shape[0]} = {C_cycle.shape[0]/D_edge.shape[0]:.6f}")

# Z_0 的物理值 (无量纲化)
Z0_phys = 376.730  # ohms, but dimensionless in SRE
print(f"  物理 Z_0 = {Z0_phys:.3f} (但 SRE 声称无量纲)")

# 组合 Z_0 与谱量
check("I1. Z_0 · λ₂(L)/ρ(L)", Z0 * ev_F[1] / ev_F[-1])
check("I2. Z_0 / ρ(L₁)", Z0 / ev_E[-1])
check("I3. Z_0 · 1/cond(L_graph)", Z0 / np.linalg.cond(L_graph))

# α 与 Z_0 的物理关系: α = Z_0 / (2·R_K) = Z_0 · e²/(2·h) 
# 在 SRE 中 e≡1, h≡1, 所以 α = Z_0/2
check("I4. Z_0/2", Z0 / 2)
check("I5. Z_0/(2·137)", Z0 / (2 * 137))

# 也许 α = Z_0 · (某个谱比)
for name, val in [
    ("Z_0·λ₂/ρ²", Z0 * ev_F[1] / ev_F[-1]**2),
    ("Z_0·(λ₂/ρ)²", Z0 * (ev_F[1] / ev_F[-1])**2),
    ("Z_0²·λ₂/ρ", Z0**2 * ev_F[1] / ev_F[-1]),
    ("(dim_F/dim_E)·λ₂/ρ", (5/12) * ev_F[1] / ev_F[-1]),
    ("(dim_F/dim_E)²·λ₂/ρ", (5/12)**2 * ev_F[1] / ev_F[-1]),
    ("(dim_F/dim_E)·1/cond(L₁)", (5/12) / np.linalg.cond(L1_hodge)),
]:
    check(f"I6. {name}", val)

# ═══════════════════════════════════════════════════════════════
print()
print("=" * 90)
print("汇总: 最接近 1/137.036 的候选")
print("=" * 90)
# 排序 by relative error
results.sort(key=lambda x: x[2])
for name, value, rel_err, match in results[:20]:
    print(f"  {value:>14.10f}  (err={rel_err:.4%})  {name}")

print()
print(f"目标值: {ALPHA_TARGET:.10f}")
best = results[0]
print(f"最佳:   {best[1]:.10f}  (相对误差={best[2]:.4%})  {best[0]}")
