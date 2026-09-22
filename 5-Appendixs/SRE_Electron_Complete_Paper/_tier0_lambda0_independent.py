# -*- coding: utf-8 -*-
"""
Tier 0 — λ₀ 独立计算（禁止 α 作为输入）
============================================================
路线图判据：脚本在【不输入 α】的前提下，从纯拓扑算出：
  (a) λ₀ = 0.00641954（真空基自旋残留）
  (b) α  = 1/137.035999（允许直接由图谱给出，绕过 λ₀/κ）

符号契约（先于计算冻结，不允许为"趋势好看"改动）
------------------------------------------------------------
[契约 1] n 的先验固定（不得扫描 n 后挑命中值）
    数据源：Maxwell.py 的离散胞腔复形（D_edge, 12×8 边-点关联阵）。
    注意：源码注释称其为 "K_{3,5}"，但 D_edge 实际定义的是
      8 环 (0-1-...-7-0) + 4 条弦 (0,2),(1,3),(2,4),(5,7)，
    并非完全二部图 K_{3,5}（后者 15 边、8 独立环）。
    本脚本以【实际 D_edge】为准重建图（可审计），不沿用错误命名。
    实际：|V|=8, |E|=12（行数）, β1 = E - V + 1 = 5（与 NUM_CYCLES 一致）。
    n ≡ dim(E) × dim(F) = |E| × β1 = 12 × 5 = 60。
    → n=60 由胞腔复形维数决定，与 α 无关。

[契约 2] 光的残余流形（light_3.pdf 公理 II）
    X(φ,w) = ((1+w·cos(φ/2))·cosφ, (1+w·cos(φ/2))·sinφ, w·sin(φ/2))
    闭合周期 4π。n 点等距采样 φ_i = i·4π/n, i=0..n-1。
    小 w 代表"窄微阻抗带"；既有结果显示 w∈[0.05,0.15] 谱量平台，
    本脚本取 w=0.1 为平台代表值，并做平台稳健性检验（不针对 α 调参）。

[契约 3] k=3 的先验依据（不得扫描 k 后挑命中值）
    4π 双覆盖下每个点的近邻结构应为：
      沿链 2 个（φ±Δφ）+ 跨 2π 平移识别的双覆盖伙伴 1 个 = 3。
    本脚本用近邻距离间隙（distance gap）数值确认第 3/4 近邻间断点，
    若间隙不显著，则 k=3 先验依据不成立，如实记录。

[契约 4] λ₀ 的预注册候选（计算前固定，禁止事后新增"恰好命中"的量）
    理论定义：对称态 ρ_A=ρ_B 下残余算子的最小非零本征值（最软拓扑模）。
    C1 = 1D 签名 Möbius 环（4π约定）L=2I-A_signed 的最小本征值
         μ_min = 2 - 2cos(2π/n)            （最规范，无 w、无 k）
    C2 = 同环谱间隙 μ_min/μ_max = tan²(π/n)
    C3 = 3D 点云 kNN(3) 图拉普拉斯的最小非零本征值 ev[1]（原始尺度）
    C4 = 同图谱间隙 ev[1]/ev[-1]
    判定在计算后一次性做出，不追加候选、不乘经验因子。

[契约 5] 参考值仅用于对照，不进入任何计算
    α*  = 1/137.035999084
    λ₀* = 0.00641954（历史反解值，来源：频率公式+α*+κ=0.828）
    这两个数只允许出现在 Section 5 的误差报告里。

成功判据（预注册）
------------------------------------------------------------
PASS-A : C1 或 C3 与 λ₀* 相对误差 < 1%       → λ₀ 独立
PASS-B : C2 或 C4 与 α*  相对误差 < 1%       → α 独立（允许绕过 λ₀）
若 PASS-B 成立而 PASS-A 不成立：
  结论应为"λ₀ 不是独立原语，gap 路径已使 λ₀/κ 成为冗余中间量"，
  不得反凑一个 λ₀ 候选。
"""
import json
import numpy as np
from scipy.spatial.distance import cdist

np.set_printoptions(precision=12, suppress=True)

# ════════════════════════════════════════════════════════════════
# Section 1 — n 的先验固定：从 K_{3,5} 拓扑推出 n=60（无 α）
# ════════════════════════════════════════════════════════════════
print("=" * 78)
print("Section 1  n 的先验固定：Maxwell 胞腔复形 → n = dim(E)×dim(F)")
print("=" * 78)

# 从 Maxwell.py 的【实际 D_edge】重建胞腔复形（12 条边 × 8 个节点）
D_edge = np.array([
    [ 1,-1, 0, 0, 0, 0, 0, 0],[ 0, 1,-1, 0, 0, 0, 0, 0],
    [ 0, 0, 1,-1, 0, 0, 0, 0],[ 0, 0, 0, 1,-1, 0, 0, 0],
    [ 0, 0, 0, 0, 1,-1, 0, 0],[ 0, 0, 0, 0, 0, 1,-1, 0],
    [ 0, 0, 0, 0, 0, 0, 1,-1],[-1, 0, 0, 0, 0, 0, 0, 1],
    [ 1, 0,-1, 0, 0, 0, 0, 0],[ 0, 1, 0,-1, 0, 0, 0, 0],
    [ 0, 0, 1, 0,-1, 0, 0, 0],[ 0, 0, 0, 0, 1, 0, 0,-1]], dtype=float)
E = D_edge.shape[0]
V = D_edge.shape[1]
Ag = (np.abs(D_edge.T) @ np.abs(D_edge) > 0).astype(float)
np.fill_diagonal(Ag, 0)
edges = sorted(tuple(sorted(k)) for k in zip(*np.where(np.triu(Ag, 1) > 0)))
connected = np.linalg.matrix_rank(np.diag(Ag.sum(1)) - Ag) == V - 1
beta1 = E - V + 1 if connected else None
n_fixed = E * beta1
print(f"  实际胞腔图（源码误标 K_{{3,5}}）：8环+4弦")
print(f"  边列表: {edges}")
print(f"  |V|={V}, |E|={E}, 连通={connected}, β1=|E|-|V|+1={beta1}")
print(f"  对照源码 NUM_CYCLES=5：{'一致' if beta1 == 5 else '不一致'}")
print(f"  n ≡ |E| × β1 = {E} × {beta1} = {n_fixed}   （先验固定，不扫描）")
assert n_fixed == 60
# 诚实记录：真正的完全二部图 K_{3,5} 是 15 边、8 环
print(f"  [命名审计] 真正 K_{{3,5}} 应为 15 边、β1=8，与 D_edge 不符；"
      f"后续一律以 D_edge 实图为准。")

# ════════════════════════════════════════════════════════════════
# Section 2 — 规范图构造（无 α、无拟合常数）
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 2  规范图构造")
print("=" * 78)

n = n_fixed
W_PRIORI = 0.1   # 平台代表值，见契约 2

def mobius_points(n, w):
    """4π 闭合 Möbius 残余流形点云（light_3.pdf 公理 II）。"""
    phi = np.linspace(0, 4 * np.pi, n, endpoint=False)
    x = (1 + w * np.cos(phi / 2)) * np.cos(phi)
    y = (1 + w * np.cos(phi / 2)) * np.sin(phi)
    z = w * np.sin(phi / 2)
    return np.column_stack([x, y, z])

def signed_mobius_ring(n):
    """1D 签名 Möbius 环（4π 约定）：闭合边 -1，其余 +1。L=2I-A。"""
    A = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        s = -1.0 if i == n - 1 else 1.0
        A[i, j] = A[j, i] = s
    return np.diag([2.0] * n) - A, A

def knn_laplacian(pts, k):
    """无向 kNN 图组合拉普拉斯 L = D - A。"""
    d = cdist(pts, pts)
    n = len(pts)
    A = np.zeros((n, n))
    for i in range(n):
        for j in np.argsort(d[i])[1:k + 1]:
            A[i, j] = A[j, i] = 1.0
    return np.diag(A.sum(axis=1)) - A, A

# --- 契约 3 的数值确认：k=3 先验依据 —— 近邻距离间隙 ---
pts = mobius_points(n, W_PRIORI)
D = cdist(pts, pts)
d0 = np.sort(D[0])
print(f"\n  节点0 的前 7 近邻距离（w={W_PRIORI}）：")
for r in range(1, 8):
    print(f"    第{r}近邻: {d0[r]:.6f}")
g34 = (d0[4] - d0[3]) / d0[3]
# 契约 3 的正确检验：双覆盖伙伴（i → i+n/2）是否属于 k=3 近邻壳，
# 而非必须恰好是第 3 名；k=3 壳 = {伙伴, 链上+1, 链上-1}。
order = np.argsort(D[0])
shell3 = set(int(x) for x in order[1:4])
partner = n // 2
chain_pm = {1, n - 1}
k3_predicted = {partner} | chain_pm
k3_ok = shell3 == k3_predicted
print(f"  第3→第4近邻相对跳变: {g34*100:.1f}%（距离壳间隙）")
print(f"  k=3 近邻壳 = {sorted(shell3)}")
print(f"  契约3预言 = {{2π伙伴 {partner}, 链上 1/{n-1}}} = {sorted(k3_predicted)}")
print(f"  k=3 先验依据：{'成立（2链邻 + 1双覆盖识别伙伴，且壳间隙显著）' if k3_ok and g34 > 0.2 else '不成立'}")
j3 = int(order[3])

L_ring, A_ring = signed_mobius_ring(n)
ev_ring = np.sort(np.linalg.eigvalsh(L_ring))
L_knn, A_knn = knn_laplacian(pts, 3)
ev_knn = np.sort(np.linalg.eigvalsh(L_knn))

# ════════════════════════════════════════════════════════════════
# Section 3 — 预注册候选谱量（α 不参与，计算一次性完成）
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 3  预注册候选（纯拓扑，无 α 输入）")
print("=" * 78)

# C1: 1D 签名环最小本征值；闭式 μ_min = 2-2cos(2π/n)
C1 = float(2.0 - 2.0 * np.cos(2.0 * np.pi / n))
# C2: 1D 签名环谱间隙；闭式 tan²(π/n)
C2 = float(np.tan(np.pi / n) ** 2)
# C3: kNN(3) 最小非零本征值（原始尺度）
C3 = float(ev_knn[1])
# C4: kNN(3) 谱间隙
C4 = float(ev_knn[1] / ev_knn[-1])

print(f"  C1 = 2-2cos(2π/n)            = {C1:.10f}   （签名环最软模）")
print(f"  C2 = tan²(π/n)               = {C2:.10f}   （签名环间隙）")
print(f"  C3 = ev[1] of kNN(3) L       = {C3:.10f}   （3D图最软模，原始尺度）")
print(f"  C4 = ev[1]/ev[-1] of kNN(3)  = {C4:.10f}   （3D图间隙）")
print(f"  附：kNN 谱半径 ev[-1]        = {float(ev_knn[-1]):.6f}")

# ════════════════════════════════════════════════════════════════
# Section 4 — 稳健性（证明 C4 不是对 w/采样调参的产物）
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 4  C4 稳健性（w 平台 / 采样抖动；n 固定不扫描）")
print("=" * 78)
c4_w = {}
for w in [0.05, 0.08, 0.10, 0.12, 0.15]:
    Lw, _ = knn_laplacian(mobius_points(n, w), 3)
    evw = np.sort(np.linalg.eigvalsh(Lw))
    c4_w[w] = float(evw[1] / evw[-1])
vals = np.array(list(c4_w.values()))
print(f"  w∈[0.05,0.15] 的 C4: "
      f"min={vals.min():.10f}, max={vals.max():.10f}, "
      f"相对展宽={(vals.max()-vals.min())/vals.mean()*100:.4f}%")

rng = np.random.default_rng(42)
jit = []
for _ in range(5):
    phi = np.linspace(0, 4*np.pi, n, endpoint=False)
    phi += rng.normal(0, 0.01 * (4*np.pi/n), n)
    p = np.column_stack([
        (1 + W_PRIORI*np.cos(phi/2))*np.cos(phi),
        (1 + W_PRIORI*np.cos(phi/2))*np.sin(phi),
        W_PRIORI*np.sin(phi/2)])
    Lj, _ = knn_laplacian(p, 3)
    evj = np.sort(np.linalg.eigvalsh(Lj))
    jit.append(evj[1]/evj[-1])
jit = np.array(jit)
print(f"  5 次随机抖动 C4: 展宽={(jit.max()-jit.min())/jit.mean()*100:.4f}%")

# ════════════════════════════════════════════════════════════════
# Section 5 — 对照（参考值在此处才出现，绝不进入上面的计算）
# ════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 5  与参考值对照（参考值不参与 Section 1-4 的任何计算）")
print("=" * 78)
ALPHA_REF = 1.0 / 137.035999084
LAMBDA0_REF = 0.00641954

def err(x, ref):
    return abs(x - ref) / ref

rows = [
    ("C1 → λ₀", C1, LAMBDA0_REF, "PASS-A"),
    ("C3 → λ₀", C3, LAMBDA0_REF, "PASS-A"),
    ("C2 → α",  C2, ALPHA_REF,  "PASS-B"),
    ("C4 → α",  C4, ALPHA_REF,  "PASS-B"),
]
print(f"  {'候选':<10}{'计算值':>16}{'参考值':>16}{'相对误差':>12}  判定")
for name, val, ref, gate in rows:
    e = err(val, ref)
    verdict = "PASS" if e < 0.01 else "FAIL"
    print(f"  {name:<10}{val:>16.10f}{ref:>16.10f}{e*100:>11.4f}%  {gate}: {verdict}")

passA = err(C1, LAMBDA0_REF) < 0.01 or err(C3, LAMBDA0_REF) < 0.01
passB = err(C2, ALPHA_REF) < 0.01 or err(C4, ALPHA_REF) < 0.01
print("\n  预注册总判定：")
print(f"    PASS-A（λ₀ 独立）: {'是' if passA else '否'}")
print(f"    PASS-B（α 独立） : {'是' if passB else '否'}")
if passB and not passA:
    print("    → λ₀ 非独立原语；gap 路径绕过 λ₀/κ 直接给出 α。")

out = {
    "n_fixed_from": "Maxwell.py D_edge cell complex (8-cycle+4 chords): n=|E|*beta1=12*5=60 (a priori); NOTE: not a true K_{3,5} (which has 15 edges, beta1=8)",
    "w_priori": W_PRIORI, "k_priori": 3,
    "knn_k3_justification_gap34_pct": float(g34*100),
    "k3_shell_matches_2chain_plus_partner": bool(k3_ok),
    "k3_shell": sorted(shell3), "predicted_shell": sorted(k3_predicted),
    "candidates_no_alpha_input": {
        "C1_signed_ring_evmin": C1, "C2_signed_ring_gap": C2,
        "C3_knn_evmin": C3, "C4_knn_gap": C4},
    "C4_robustness": {
        "w_plateau_values": {str(k): float(v) for k, v in c4_w.items()},
        "w_plateau_spread_pct": float((vals.max()-vals.min())/vals.mean()*100),
        "jitter_spread_pct": float((jit.max()-jit.min())/jit.mean()*100)},
    "reference_only_for_comparison": {"alpha_ref": ALPHA_REF, "lambda0_ref": LAMBDA0_REF},
    "verdict": {"PASS_A_lambda0_independent": bool(passA),
                "PASS_B_alpha_independent": bool(passB)},
}
with open(r"c:\mywork\vasp\tier0_lambda0_results.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n  已保存 tier0_lambda0_results.json")
