"""
验证 SRE 理论中 α ≈ 1/137.036 是否从 Möbius 环拓扑涌现。

核心线索: "电子和光都是 Möbius 环的拓扑结构"

Möbius 环的数学特征:
1. 非可定向 — 半扭转 (half-twist)
2. 邻接矩阵是 signed graph: 一条边权重为 -1 (代表扭转)
3. 特征值: λ_k = 2·cos((2k+1)π/n)  [对比普通环: 2·cos(2πk/n)]
4. 奇数次遍历翻转方向 → trace(A^k) 对奇数 k 可能为 0

Möbius 环 Laplacian: L_M = 2I - A_M
  特征值: μ_k = 2 - 2·cos((2k+1)π/n)
  μ_min = 2 - 2·cos(π/n)  (k=0)
  μ_max = 2 + 2·cos(π/n)  (k=n-1)
  gap = μ_min/μ_max = (1-cos(π/n))/(1+cos(π/n)) = tan²(π/(2n))

目标: gap = tan²(π/(2n)) = 1/137.036 = 0.00729735
  → tan(π/(2n)) = √0.00729735 = 0.085424
  → π/(2n) = arctan(0.085424) = 0.085254 rad
  → n = π / (2 × 0.085254) = 18.43

所以 n=18 或 n=19 可能给出接近的值!

同时测试:
- Möbius ratio R(k) = trace(A^{2k}) / (2·trace(A^k))
- 2D Möbius strip meshes
- Klein bottle graphs (闭合 Möbius)
- Möbius ladder graphs
"""
import numpy as np
from itertools import combinations

np.set_printoptions(precision=12, suppress=True)

ALPHA = 1.0 / 137.035999084
print(f"目标: α = 1/137.035999 = {ALPHA:.12f}\n")

results = []

def check(name, val):
    err = abs(val - ALPHA) / ALPHA
    tag = " ★★★" if err < 0.001 else (" ★" if err < 0.01 else (" ~" if err < 0.05 else ""))
    results.append((name, val, err, tag))
    print(f"  {name:<50s} = {val:>16.12f}  (err={err:.4%}){tag}")

# ══════════════════════════════════════════════════════════════
print("=" * 80)
print("1. Möbius Cycle C_n^M (signed graph, 1D)")
print("   邻接: A[0,n-1] = A[n-1,0] = -1 (半扭转), 其余 = 1")
print("   特征值: λ_k = 2·cos((2k+1)π/n)")
print("   Laplacian 特征值: μ_k = 2 - 2·cos((2k+1)π/n)")
print("=" * 80)

for n in range(3, 51):
    # Möbius cycle adjacency (signed)
    A_M = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        if i == n - 1 and j == 0:
            A_M[i, j] = -1  # twist!
            A_M[j, i] = -1
        else:
            A_M[i, j] = 1
            A_M[j, i] = 1

    # Laplacian
    L_M = np.diag([2.0] * n) - A_M
    ev = np.linalg.eigvalsh(L_M)
    ev = np.sort(ev)

    # Spectral gap
    mu_min = ev[0]
    mu_max = ev[-1]
    gap = mu_min / mu_max

    # Analytical
    gap_analytical = (1 - np.cos(np.pi / n)) / (1 + np.cos(np.pi / n))

    if n <= 20 or abs(gap - ALPHA) / ALPHA < 0.05:
        check(f"C_{n}^M: gap = tan²(π/{2*n})", gap)

    # Also check gap²
    if abs(gap**2 - ALPHA) / ALPHA < 0.1:
        check(f"C_{n}^M: gap²", gap**2)

    # 1/cond
    cond = mu_max / mu_min if mu_min > 1e-15 else float('inf')
    if abs(1.0 / cond - ALPHA) / ALPHA < 0.05:
        check(f"C_{n}^M: 1/cond(L)", 1.0 / cond)

    # Möbius ratio R(k) for various k
    for k in range(1, min(n, 10)):
        tr_k = np.trace(np.linalg.matrix_power(A_M, k))
        tr_2k = np.trace(np.linalg.matrix_power(A_M, 2 * k))
        if abs(tr_k) > 1e-10:
            R_k = tr_2k / (2 * tr_k)
            # Check R_k and derived quantities
            if abs(R_k - ALPHA) / ALPHA < 0.05:
                check(f"C_{n}^M: R({k}) = tr(A^{2*k})/(2·tr(A^{k}))", R_k)
            if abs(1.0 / R_k - ALPHA) / ALPHA < 0.05:
                check(f"C_{n}^M: 1/R({k})", 1.0 / R_k)
            if abs(R_k - 1 - ALPHA) / ALPHA < 0.05:
                check(f"C_{n}^M: R({k})-1", R_k - 1)
            if abs(1.0 / (R_k - 1) - ALPHA) / ALPHA < 0.05 if abs(R_k - 1) > 1e-10 else False:
                check(f"C_{n}^M: 1/(R({k})-1)", 1.0 / (R_k - 1))

# 重点检查 n=18, 19
print("\n--- 重点检查 n=18, 19 ---")
for n in [18, 19]:
    A_M = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        w = -1.0 if (i == n - 1 and j == 0) else 1.0
        A_M[i, j] = w
        A_M[j, i] = w

    L_M = np.diag([2.0] * n) - A_M
    ev = np.sort(np.linalg.eigvalsh(L_M))

    gap = ev[0] / ev[-1]
    print(f"\n  C_{n}^M: μ_min={ev[0]:.10f}  μ_max={ev[-1]:.10f}  gap={gap:.12f}")
    print(f"    tan²(π/{2*n}) = {np.tan(np.pi/(2*n))**2:.12f}")
    print(f"    gap/α = {gap/ALPHA:.6f}  gap-α = {gap-ALPHA:.2e}")

    # Möbius ratios
    for k in range(1, 8):
        tr_k = np.trace(np.linalg.matrix_power(A_M, k))
        tr_2k = np.trace(np.linalg.matrix_power(A_M, 2*k))
        if abs(tr_k) > 1e-10:
            R_k = tr_2k / (2 * tr_k)
            print(f"    R({k}) = {R_k:.12f}  (tr(A^{k})={tr_k:.4f}, tr(A^{2*k})={tr_2k:.4f})")
            if abs(R_k - 1) > 1e-10:
                check(f"C_{n}^M: R({k})-1", R_k - 1)
                check(f"C_{n}^M: 1/(R({k})-1)", 1.0/(R_k - 1))

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("2. 2D Möbius Strip Mesh (w×h grid with twist)")
print("=" * 80)

def build_mobius_strip(w, h):
    """构建 2D Möbius strip 网格图
    w = 宽度, h = 高度
    扭转: (r, 0) ↔ (h-1-r, w-1)
    """
    n = w * h
    node = lambda r, c: r * w + c

    edges = []
    signs = []  # 1 = normal, -1 = twist

    # Horizontal edges
    for r in range(h):
        for c in range(w - 1):
            edges.append((node(r, c), node(r, c + 1)))
            signs.append(1)

    # Vertical edges
    for r in range(h - 1):
        for c in range(w):
            edges.append((node(r, c), node(r + 1, c)))
            signs.append(1)

    # Twist edges (wrap around with reversal)
    for r in range(h):
        a = node(r, w - 1)
        b = node(h - 1 - r, 0)
        if a != b:
            edges.append((a, b))
            signs.append(-1)  # Möbius twist!

    # Build signed adjacency
    A = np.zeros((n, n))
    D = np.zeros((n, n))
    for (a, b), s in zip(edges, signs):
        A[a, b] = s
        A[b, a] = s
        D[a, a] += abs(s)
        D[b, b] += abs(s)

    L = D - A  # Signed Laplacian

    return L, A, n, len(edges)

for w in range(2, 10):
    for h in range(2, 10):
        L, A, nV, nE = build_mobius_strip(w, h)
        ev = np.sort(np.linalg.eigvalsh(L))
        gap = ev[0] / ev[-1]

        if abs(gap - ALPHA) / ALPHA < 0.05:
            print(f"\n  Möbius {w}×{h}: V={nV} E={nE}")
            print(f"    μ_min={ev[0]:.10f}  μ_max={ev[-1]:.10f}  gap={gap:.12f}")
            check(f"Möbius_{w}x{h}: gap", gap)
            check(f"Möbius_{w}x{h}: gap²", gap**2)
            check(f"Möbius_{w}x{h}: 1/cond", 1.0/np.linalg.cond(L))

            # Möbius ratios
            for k in range(1, 6):
                tr_k = np.trace(np.linalg.matrix_power(A, k))
                tr_2k = np.trace(np.linalg.matrix_power(A, 2*k))
                if abs(tr_k) > 1e-10:
                    R_k = tr_2k / (2 * tr_k)
                    check(f"Möbius_{w}x{h}: R({k})", R_k)
                    if abs(R_k - 1) > 1e-10:
                        check(f"Möbius_{w}x{h}: R({k})-1", R_k - 1)
                        check(f"Möbius_{w}x{h}: 1/(R({k})-1)", 1.0/(R_k-1))

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("3. Klein Bottle Graphs (closed Möbius = non-orientable genus 2)")
print("=" * 80)

def build_klein_bottle(w, h):
    """Klein bottle: w×h grid with twist in one direction and periodic in other"""
    n = w * h
    node = lambda r, c: r * w + c

    edges = []
    signs = []
    # Horizontal
    for r in range(h):
        for c in range(w - 1):
            edges.append((node(r, c), node(r, c+1)))
            signs.append(1)
        # Wrap: (r, w-1) → (r, 0) with twist for Klein
        a, b = node(r, w-1), node(r, 0)
        if a != b:
            edges.append((a, b))
            signs.append(-1)  # twist in horizontal wrap

    # Vertical (periodic, no twist)
    for c in range(w):
        for r in range(h - 1):
            edges.append((node(r, c), node(r+1, c)))
            signs.append(1)
        # Wrap: (h-1, c) → (0, c) — no twist
        a, b = node(h-1, c), node(0, c)
        if a != b:
            edges.append((a, b))
            signs.append(1)

    A = np.zeros((n, n))
    D = np.zeros((n, n))
    for (a, b), s in zip(edges, signs):
        A[a, b] = s
        A[b, a] = s
        D[a, a] += abs(s)
        D[b, b] += abs(s)

    return D - A, A, n, len(edges)

for w in range(3, 12):
    for h in range(3, 12):
        L, A, nV, nE = build_klein_bottle(w, h)
        ev = np.sort(np.linalg.eigvalsh(L))
        gap = ev[0] / ev[-1]
        if abs(gap - ALPHA) / ALPHA < 0.03:
            print(f"\n  Klein {w}×{h}: V={nV} E={nE}")
            check(f"Klein_{w}x{h}: gap", gap)
            check(f"Klein_{w}x{h}: gap²", gap**2)
            for k in range(1, 6):
                tr_k = np.trace(np.linalg.matrix_power(A, k))
                tr_2k = np.trace(np.linalg.matrix_power(A, 2*k))
                if abs(tr_k) > 1e-10:
                    R_k = tr_2k / (2 * tr_k)
                    check(f"Klein_{w}x{h}: R({k})", R_k)
                    if abs(R_k - 1) > 1e-10:
                        check(f"Klein_{w}x{h}: R({k})-1", R_k - 1)
                        check(f"Klein_{w}x{h}: 1/(R({k})-1)", 1.0/(R_k-1))

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("4. Projective Plane Graph (simplest non-orientable surface)")
print("   Complete graph K_6 embeds in RP²")
print("=" * 80)

# K_6 on projective plane
# Petersen graph also embeds in RP²
# Try: K_6 with a cross-cap

# K_6 complete graph
K6_edges = list(combinations(range(6), 2))
n = 6
A_K6 = np.zeros((n, n))
for a, b in K6_edges:
    A_K6[a, b] = 1
    A_K6[b, a] = 1
L_K6 = np.diag([5.0]*n) - A_K6
ev_K6 = np.sort(np.linalg.eigvalsh(L_K6))
check("K6(RP²): gap", ev_K6[0] / ev_K6[-1])
check("K6(RP²): gap²", (ev_K6[0] / ev_K6[-1])**2)
for k in range(1, 6):
    tr_k = np.trace(np.linalg.matrix_power(A_K6, k))
    tr_2k = np.trace(np.linalg.matrix_power(A_K6, 2*k))
    if abs(tr_k) > 1e-10:
        R_k = tr_2k / (2 * tr_k)
        check(f"K6(RP²): R({k})", R_k)
        if abs(R_k - 1) > 1e-10:
            check(f"K6(RP²): R({k})-1", R_k - 1)
            check(f"K6(RP²): 1/(R({k})-1)", 1.0/(R_k-1))

# Petersen graph
pet_edges = [(0,1),(1,2),(2,3),(3,4),(4,0),
             (5,7),(7,9),(9,6),(6,8),(8,5),
             (0,5),(1,6),(2,7),(3,8),(4,9)]
n = 10
A_P = np.zeros((n, n))
for a, b in pet_edges:
    A_P[a, b] = 1
    A_P[b, a] = 1
L_P = np.diag([3.0]*n) - A_P
ev_P = np.sort(np.linalg.eigvalsh(L_P))
check("Petersen(RP²): gap", ev_P[0] / ev_P[-1])
check("Petersen(RP²): gap²", (ev_P[0] / ev_P[-1])**2)
for k in range(1, 6):
    tr_k = np.trace(np.linalg.matrix_power(A_P, k))
    tr_2k = np.trace(np.linalg.matrix_power(A_P, 2*k))
    if abs(tr_k) > 1e-10:
        R_k = tr_2k / (2 * tr_k)
        check(f"Petersen(RP²): R({k})", R_k)
        if abs(R_k - 1) > 1e-10:
            check(f"Petersen(RP²): R({k})-1", R_k - 1)
            check(f"Petersen(RP²): 1/(R({k})-1)", 1.0/(R_k-1))

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("5. 双 Möbius 环交互 (electron × photon)")
print("   如果电子和光都是 Möbius 环, α 可能来自二者的交互")
print("=" * 80)

# 电子 = C_n^M, 光子 = C_m^M
# 交互 = 张量积? 直积? 谱比?

# 尝试: gap_electron × gap_photon
# 或: spectral radius of A_electron ⊗ A_photon
# 或: gap(A_e ⊗ A_p) / ρ(A_e ⊗ A_p)

best_combo = None
best_err = 1.0

for n_e in range(3, 30):
    for n_p in range(3, 30):
        # Electron Möbius cycle
        A_e = np.zeros((n_e, n_e))
        for i in range(n_e):
            j = (i + 1) % n_e
            s = -1.0 if (i == n_e - 1) else 1.0
            A_e[i, j] = s
            A_e[j, i] = s
        L_e = np.diag([2.0]*n_e) - A_e
        ev_e = np.sort(np.linalg.eigvalsh(L_e))
        gap_e = ev_e[0] / ev_e[-1]

        # Photon Möbius cycle
        A_p = np.zeros((n_p, n_p))
        for i in range(n_p):
            j = (i + 1) % n_p
            s = -1.0 if (i == n_p - 1) else 1.0
            A_p[i, j] = s
            A_p[j, i] = s
        L_p = np.diag([2.0]*n_p) - A_p
        ev_p = np.sort(np.linalg.eigvalsh(L_p))
        gap_p = ev_p[0] / ev_p[-1]

        # Various combinations
        combos = [
            ("gap_e·gap_p", gap_e * gap_p),
            ("gap_e/gap_p", gap_e / gap_p if gap_p > 0 else 0),
            ("gap_e+gap_p", gap_e + gap_p),
            ("√(gap_e·gap_p)", np.sqrt(gap_e * gap_p)),
            ("gap_e·gap_p/(gap_e+gap_p)", gap_e * gap_p / (gap_e + gap_p) if (gap_e + gap_p) > 0 else 0),
        ]

        for cname, cval in combos:
            err = abs(cval - ALPHA) / ALPHA
            if err < best_err:
                best_err = err
                best_combo = (f"e=C_{n_e}^M, p=C_{n_p}^M: {cname}", cval, err)

# Also try Kronecker product spectrum
for n_e in range(3, 25):
    for n_p in range(3, 25):
        A_e = np.zeros((n_e, n_e))
        for i in range(n_e):
            j = (i + 1) % n_e
            s = -1.0 if (i == n_e - 1) else 1.0
            A_e[i, j] = s; A_e[j, i] = s
        A_p = np.zeros((n_p, n_p))
        for i in range(n_p):
            j = (i + 1) % n_p
            s = -1.0 if (i == n_p - 1) else 1.0
            A_p[i, j] = s; A_p[j, i] = s

        # Kronecker product
        A_kron = np.kron(A_e, A_p)
        ev_kron = np.sort(np.linalg.eigvalsh(A_kron))
        rho = np.max(np.abs(ev_kron))

        L_kron = np.kron(np.diag([2.0]*n_e) - A_e, np.diag([2.0]*n_p) - A_p)
        ev_Lkron = np.sort(np.linalg.eigvalsh(L_kron))
        gap_kron = ev_Lkron[0] / ev_Lkron[-1]

        for val, name in [(rho, "ρ(A_e⊗A_p)"),
                          (1.0/rho if rho > 0 else 0, "1/ρ(A_e⊗A_p)"),
                          (gap_kron, "gap(L_e⊗L_p)"),
                          (gap_kron**2, "gap²(L_e⊗L_p)")]:
            err = abs(val - ALPHA) / ALPHA
            if err < best_err:
                best_err = err
                best_combo = (f"e=C_{n_e}^M, p=C_{n_p}^M: {name}", val, err)

print(f"\n  最佳双 Möbius 组合:")
if best_combo:
    print(f"    {best_combo[0]} = {best_combo[1]:.12f}  (err={best_combo[2]:.4%})")
    check(best_combo[0], best_combo[1])

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("6. Möbius 环 + Hodge 结构 (D_edge + C_cycle with twist)")
print("=" * 80)

# 构建 Möbius cycle 的 D_edge 和 C_cycle
# 对于 C_n^M, 只有一个 "Möbius 环" (不可定向)
def build_mobius_cycle_sre(n):
    """Möbius cycle 的 SRE 算子"""
    # D_edge: n edges × n nodes
    D = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        D[i, i] = 1
        D[i, j] = -1 if (i == n - 1) else -1  # boundary is always [1, -1]

    # Signed adjacency
    A = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        s = -1.0 if (i == n - 1) else 1.0
        A[i, j] = s; A[j, i] = s

    # The Möbius cycle is a single non-orientable cycle
    # C_cycle: 1 × n (the Möbius loop itself)
    C = np.zeros((1, n))
    for i in range(n):
        C[0, i] = 1  # all edges belong to the Möbius loop

    # P_E projector
    DtD = D.T @ D
    P_E = D @ np.linalg.pinv(DtD) @ D.T

    return D, C, A, P_E

print("\n  Möbius cycle D_edge + C_cycle + §1.1 公式:")
for n in range(3, 40):
    D, C, A, P_E = build_mobius_cycle_sre(n)

    # §1.1: α = ρ_spectral(D^T · P_E · Δ_cycle)
    # Try different Δ_cycle interpretations

    # Δ = C^T
    M1 = D.T @ P_E @ C.T  # (n, 1)
    sv1 = np.linalg.svd(M1, compute_uv=False)
    if sv1[0] > 1e-10:
        val = 1.0 / sv1[0]
        if abs(val - ALPHA) / ALPHA < 0.05:
            check(f"C_{n}^M: 1/σ_max(D^T·P_E·C^T)", val)

    # Δ = C^T·C (1×1, scalar)
    M2 = C.T @ C  # (n, n)
    M2_full = D.T @ P_E @ M2  # (n, n)
    ev2 = np.linalg.eigvalsh(M2_full)
    rho2 = np.max(np.abs(ev2))
    if rho2 > 1e-10:
        if abs(1.0/rho2 - ALPHA) / ALPHA < 0.05:
            check(f"C_{n}^M: 1/ρ(D^T·P_E·C^T·C)", 1.0/rho2)

    # Hodge L1
    L1 = D @ D.T + C.T @ C
    ev_H = np.sort(np.linalg.eigvalsh(L1))
    gap_H = ev_H[ev_H > 1e-10][0] / ev_H[-1] if len(ev_H[ev_H > 1e-10]) > 0 else 0
    if abs(gap_H - ALPHA) / ALPHA < 0.05:
        check(f"C_{n}^M: gap(Hodge L1)", gap_H)
        check(f"C_{n}^M: √gap(Hodge)", np.sqrt(gap_H))

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("全局汇总: 最接近 α 的前 25 名")
print("=" * 80)
results.sort(key=lambda x: x[2])
for name, val, err, tag in results[:25]:
    print(f"  {val:>16.12f}  (err={err:.4%})  {tag:<5s} {name}")

print(f"\n目标: {ALPHA:.12f}")
best = results[0]
print(f"最佳: {best[1]:.12f}  (err={best[2]:.4%})  {best[0]}")
