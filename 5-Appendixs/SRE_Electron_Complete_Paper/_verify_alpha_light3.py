"""
基于 light_3.pdf 的精确公式验证 α

关键发现 from light_3.pdf:
1. 光 = Möbius ribbon, 参数化:
   X(φ,w) = ((1+w·cos(φ/2))·cos(φ), (1+w·cos(φ/2))·sin(φ), w·sin(φ/2))
   
2. 4π 闭合: "complete path must traverse 4π radians (Δφ=4π) before achieving boundary closure"
   → Möbius 的基本周期是 4π, 不是 2π!
   → 这意味着离散化时 n 个节点的角间距 = 4π/n
   → 特征值: λ_k = 2·cos((2k+1)·2π/n)  [4π 周期下的 Möbius]
   
3. 频率公式: f ∝ Δλ = √(Tr(M)² - 4·det(M)) = α · λ₁/(λ₂ + λ₃)
   → α = Δλ · (λ₂ + λ₃) / λ₁
   → 如果能算出 M 的特征值差和 λ₁, λ₂, λ₃, 就能提取 α

4. 四态本征谱矩阵:
   (H,H): λ₁=400β, λ₂-λ₃=0+λ₀'
   (H,L): λ₁=144β, λ₂-λ₃=8γ+λ₀'  
   (L,H): λ₁=144β, λ₂-λ₃=-8γ+λ₀'
   (L,L): λ₁=16β,  λ₂-λ₃=0+λ₀'
   
   公式:
   λ₁ = β·(ρ_A+ρ_B)²
   λ₂ = γ·|ρ_A-ρ_B| + λ₀
   λ₃ = λ₂/(4·(1+κ))

5. Möbius 环拓扑验证置信度: 99.2094%
"""
import numpy as np
np.set_printoptions(precision=12, suppress=True)

ALPHA = 1.0 / 137.035999084
print(f"目标: α = 1/137.035999 = {ALPHA:.12f}\n")

# ══════════════════════════════════════════════════════════════
print("=" * 80)
print("1. 4π 周期 Möbius 环: 特征值重新计算")
print("   连续周期 = 4π, n 节点, 角间距 = 4π/n")
print("   Möbius 签名邻接: A[i, i+1] = 1, A[n-1, 0] = -1")
print("   特征值: λ_k = 2·cos((2k+1)·2π/n)  [4π 周期]")
print("   Laplacian: μ_k = 2 - 2·cos((2k+1)·2π/n)")
print("   gap = μ_min/μ_max = (1-cos(2π/n))/(1+cos(2π/n)) = tan²(π/n)")
print("=" * 80)

# 在 4π 周期下, gap = tan²(π/n) 而非 tan²(π/(2n))
# 之前我用的是 2π 周期, 得到 tan²(π/(2n))
# 现在用 4π 周期: tan²(π/n)

print("\n  4π 周期: gap = tan²(π/n)")
print("  目标: tan²(π/n) = 1/137.036 = 0.00729735")
print(f"  → tan(π/n) = {np.sqrt(ALPHA):.10f}")
print(f"  → π/n = arctan({np.sqrt(ALPHA):.10f}) = {np.arctan(np.sqrt(ALPHA)):.10f}")
print(f"  → n = π / arctan(√α) = {np.pi / np.arctan(np.sqrt(ALPHA)):.6f}")
print(f"  → n ≈ 37 或 38")

for n in [36, 37, 38, 39]:
    gap = np.tan(np.pi / n) ** 2
    err = abs(gap - ALPHA) / ALPHA
    print(f"  n={n}: tan²(π/{n}) = {gap:.12f}  (err={err:.4%})")

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("2. 数值验证 4π Möbius 环 (直接构造签名邻接矩阵)")
print("=" * 80)

for n in [36, 37, 38, 39]:
    A = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        w = -1.0 if i == n - 1 else 1.0
        A[i, j] = w; A[j, i] = w
    L = np.diag([2.0]*n) - A
    ev = np.sort(np.linalg.eigvalsh(L))
    gap = ev[0] / ev[-1]
    err = abs(gap - ALPHA) / ALPHA
    tag = " ★" if err < 0.01 else (" ~" if err < 0.05 else "")
    print(f"  C_{n}^M(4π): gap = {gap:.12f}  (err={err:.4%}){tag}")

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("3. 双 Möbius (4π): 电子 × 光子")
print("   gap_e = tan²(π/n_e), gap_p = tan²(π/n_p)")
print("   α = √(gap_e · gap_p) = tan(π/n_e) · tan(π/n_p)")
print("=" * 80)

# 搜索 n_e, n_p 使得 tan(π/n_e) · tan(π/n_p) ≈ 1/137
print(f"\n  目标: tan(π/n_e) · tan(π/n_p) = {ALPHA:.12f}")
print(f"  → 如果 n_p = 2·n_e: tan(π/n) · tan(π/(2n)) = α")

best = None
best_err = 1.0

for n_e in range(3, 60):
    for n_p in range(3, 120):
        g_e = np.tan(np.pi / n_e) ** 2
        g_p = np.tan(np.pi / n_p) ** 2
        val = np.sqrt(g_e * g_p)  # = tan(π/n_e) · tan(π/n_p)
        err = abs(val - ALPHA) / ALPHA
        if err < best_err:
            best_err = err
            best = (n_e, n_p, val, err)
        if err < 0.001:
            print(f"  ★★★ n_e={n_e}, n_p={n_p}: √(gap_e·gap_p) = {val:.12f}  (err={err:.4%})")

print(f"\n  最佳: n_e={best[0]}, n_p={best[1]}: {best[2]:.12f}  (err={best[3]:.4%})")

# 检查 n_p = 2*n_e 的特殊关系
print("\n  n_p = 2·n_e 的结果:")
for n in range(3, 40):
    val = np.tan(np.pi/n) * np.tan(np.pi/(2*n))
    err = abs(val - ALPHA) / ALPHA
    if err < 0.05:
        tag = " ★" if err < 0.01 else " ~"
        print(f"    n_e={n}, n_p={2*n}: tan(π/{n})·tan(π/{2*n}) = {val:.12f}  (err={err:.4%}){tag}")

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("4. 光子 Möbius 参数化 → 图拉普拉斯")
print("   X(φ,w) = ((1+w·cos(φ/2))·cos(φ), (1+w·cos(φ/2))·sin(φ), w·sin(φ/2))")
print("   φ ∈ [0, 4π), 采样 n 个点")
print("=" * 80)

def mobius_pointcloud(n, w=0.3):
    """生成 Möbius strip 点云 (4π 周期)"""
    phi = np.linspace(0, 4*np.pi, n, endpoint=False)
    X = (1 + w * np.cos(phi/2)) * np.cos(phi)
    Y = (1 + w * np.cos(phi/2)) * np.sin(phi)
    Z = w * np.sin(phi/2)
    return np.column_stack([X, Y, Z])

def build_graph_from_points(points, k_neighbors=3):
    """从点云构建 k-NN 图"""
    from scipy.spatial.distance import cdist
    n = len(points)
    D = cdist(points, points)
    # k-NN adjacency
    A = np.zeros((n, n))
    for i in range(n):
        idx = np.argsort(D[i])[1:k_neighbors+1]  # skip self
        for j in idx:
            A[i, j] = 1
            A[j, i] = 1
    L = np.diag(A.sum(axis=1)) - A
    return L, A

# 扫描不同 n 的 Möbius 点云
print("\n  Möbius strip 点云 → k-NN 图拉普拉斯谱:")
for n in range(10, 80):
    for w in [0.1, 0.3, 0.5, 1.0]:
        pts = mobius_pointcloud(n, w=w)
        L, A = build_graph_from_points(pts, k_neighbors=3)
        ev = np.sort(np.linalg.eigvalsh(L))
        gap = ev[1] / ev[-1]  # λ₂/λ_max (skip zero eigenvalue)
        if abs(gap - ALPHA) / ALPHA < 0.02:
            print(f"    n={n}, w={w}: λ₂/ρ = {gap:.12f}  (err={abs(gap-ALPHA)/ALPHA:.4%}) ★")
        gap2 = ev[1]**2 / ev[-1]**2
        if abs(gap2 - ALPHA) / ALPHA < 0.02:
            print(f"    n={n}, w={w}: (λ₂/ρ)² = {gap2:.12f}  (err={abs(gap2-ALPHA)/ALPHA:.4%}) ★")

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("5. 频率公式: α = Δλ · (λ₂ + λ₃) / λ₁")
print("   Δλ = √(Tr(M)² - 4·det(M)) = |μ₁ - μ₂| (2×2 矩阵 M 的特征值差)")
print("=" * 80)

# 从四态矩阵提取参数
# 假设 (H,H) 和 (L,L) 的 λ₂-λ₃ = λ₀' (常数)
# (H,L) 的 λ₂-λ₃ = 8γ + λ₀'
# λ₁(H,H) = 400β, λ₁(L,L) = 16β
# λ₁(H,L) = 144β

# 公式: λ₃ = λ₂/(4·(1+κ))
# 所以: λ₂ - λ₃ = λ₂(1 - 1/(4(1+κ))) = λ₂ · (3+4κ)/(4(1+κ))
# 设 r = (3+4κ)/(4(1+κ)), 则 λ₂-λ₃ = r·λ₂

# 对于 (H,H): λ₂ = γ·0 + λ₀ = λ₀
#   λ₂-λ₃ = r·λ₀ = λ₀'  → λ₀' = r·λ₀

# 对于 (H,L): λ₂ = γ·8 + λ₀
#   λ₂-λ₃ = r·(8γ+λ₀) = 8γ + λ₀'  (from table)
#   r·(8γ+λ₀) = 8γ + r·λ₀
#   8r·γ + r·λ₀ = 8γ + r·λ₀
#   8r·γ = 8γ
#   → r = 1 (if γ ≠ 0)
#   → (3+4κ)/(4(1+κ)) = 1
#   → 3+4κ = 4+4κ
#   → 3 = 4  ← 矛盾!

# 除非 γ = 0... 或者公式理解有误
# 让我重新理解: 也许 λ₃ = λ₂ / (4·(1+κ)) 是独立的, 不参与差值

# 另一种理解: λ₂ 和 λ₃ 是独立定义的
# λ₂ = γ·|ρ_A-ρ_B| + λ₀  (不含 κ)
# λ₃ = λ₂ / (4·(1+κ))    (从 λ₂ 推导)

# 那么 λ₂ + λ₃ = λ₂ · (1 + 1/(4(1+κ))) = λ₂ · (4(1+κ)+1)/(4(1+κ))
# = λ₂ · (5+4κ)/(4+4κ)

# 对于 (H,H):
#   λ₂ = λ₀, λ₃ = λ₀/(4(1+κ))
#   λ₂-λ₃ = λ₀ · (1 - 1/(4(1+κ))) = λ₀ · (3+4κ)/(4(1+κ))
#   表格说 = λ₀' → λ₀' = λ₀ · (3+4κ)/(4(1+κ))

# 对于 (H,L):
#   λ₂ = 8γ+λ₀, λ₃ = (8γ+λ₀)/(4(1+κ))
#   λ₂-λ₃ = (8γ+λ₀)·(3+4κ)/(4(1+κ))
#   表格说 = 8γ+λ₀' = 8γ + λ₀·(3+4κ)/(4(1+κ))

# 所以: (8γ+λ₀)·(3+4κ)/(4(1+κ)) = 8γ + λ₀·(3+4κ)/(4(1+κ))
# 8γ·(3+4κ)/(4(1+κ)) + λ₀·(3+4κ)/(4(1+κ)) = 8γ + λ₀·(3+4κ)/(4(1+κ))
# 8γ·(3+4κ)/(4(1+κ)) = 8γ
# (3+4κ)/(4(1+κ)) = 1
# 3+4κ = 4+4κ → 3=4 矛盾

# 这说明我对公式的理解有问题
# 也许 λ₃ 不是 λ₂/(4(1+κ)), 而是独立的
# 或者表格里的 "8γ+λ₀'" 不是 λ₂-λ₃ 的精确公式

# 让我换个角度: 直接用四态矩阵的数值
# 假设 α 出现在 (H,L) → (L,L) 的跃迁中

# (H,L) state: ρ_A=10, ρ_B=2
#   λ₁ = β·12² = 144β
#   λ₂ = 8γ+λ₀  
#   λ₃ = (8γ+λ₀)/(4(1+κ))
#   λ₂+λ₃ = (8γ+λ₀)·(5+4κ)/(4+4κ)

# (L,L) state: ρ_A=2, ρ_B=2  
#   λ₁ = β·4² = 16β
#   λ₂ = λ₀
#   λ₃ = λ₀/(4(1+κ))
#   λ₂+λ₃ = λ₀·(5+4κ)/(4+4κ)

# 频率比: f_HL / f_LL = (α·λ₁_HL/(λ₂+λ₃)_HL) / (α·λ₁_LL/(λ₂+λ₃)_LL)
#   = (λ₁_HL / λ₁_LL) · ((λ₂+λ₃)_LL / (λ₂+λ₃)_HL)
#   = (144β/16β) · (λ₀/(8γ+λ₀))
#   = 9 · λ₀/(8γ+λ₀)

# 这不含 α! α 在频率比中消掉了
# 所以 α 只在绝对频率值中出现

# 要提取 α, 需要知道 M 矩阵的具体形式
# light_3.pdf 说 M 是 "2×2 cross-spectral response matrix"
# 但没有给出 M 的显式构造

# 尝试: M 可能是从 λ₁, λ₂ 构成的 2×2 矩阵
# 例如 M = [[λ₁, 0], [0, λ₂]], 则 Δλ = |λ₁-λ₂|
# α = |λ₁-λ₂| · (λ₂+λ₃) / λ₁

# 对于 (L,L) state:
# α = |16β - λ₀| · (λ₀·(5+4κ)/(4+4κ)) / (16β)
# = |16β - λ₀| · λ₀ · (5+4κ) / (16β · (4+4κ))

# 这需要知道 β, λ₀, κ 的值
# 从 Maxwell.py: ALPHA_0_DYNAMIC=21.09256, GAMMA_LATENCY=0.0585, THETA_CONFORMAL=0.828

# 尝试: β = ALPHA_0_DYNAMIC = 21.09256?
# κ = THETA_CONFORMAL = 0.828?
# γ = GAMMA_LATENCY = 0.0585?
# λ₀ = ?

print("\n  尝试用代码常数提取 α:")
beta = 21.09256
gamma = 0.0585
theta = 0.828  # κ?

for lambda_0 in [0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
    for kappa in [theta, 0.828, 0.5, 1.0, 0.0]:
        # (L,L) state
        l1 = beta * 4**2  # = 16β = 337.48
        l2 = lambda_0  # |2-2|=0
        l3 = lambda_0 / (4 * (1 + kappa))
        l23 = l2 + l3
        
        # M = diag(l1, l2), Δλ = |l1 - l2|
        dlambda = abs(l1 - l2)
        alpha_val = dlambda * l23 / l1
        
        err = abs(alpha_val - ALPHA) / ALPHA
        if err < 0.1:
            print(f"    λ₀={lambda_0}, κ={kappa}: α = {alpha_val:.10f}  (err={err:.4%})")

# 更系统地搜索: 需要什么 λ₀, κ 才能得到 α?
print("\n  逆向求解: 在 (L,L) 态, α = |16β-λ₀|·λ₀·(5+4κ)/(16β·(4+4κ))")
print(f"    16β = {16*beta:.6f}")

# 设 α = (16β-λ₀)·λ₀·(5+4κ) / (16β·(4+4κ))  [假设 16β > λ₀]
# 这是一个关于 λ₀ 和 κ 的二元方程
# 令 x = λ₀, y = κ
# α = (16β-x)·x·(5+4y) / (16β·(4+4y))
# = x·(16β-x)·(5+4y) / (16β·4·(1+y))
# = x·(16β-x)·(5+4y) / (64β·(1+y))

# 固定 y = 0.828 (THETA_CONFORMAL):
y = 0.828
# α = x·(337.48-x)·(5+4·0.828) / (337.48·4·1.828)
# = x·(337.48-x)·8.312 / 2468.6
coeff = (5 + 4*y) / (64 * beta * (1+y))
print(f"    固定 κ=0.828: α = {coeff:.10f} · x · ({16*beta:.2f} - x)")
print(f"    系数 = {coeff:.10f}")
print(f"    需要: {coeff:.10f} · x · ({16*beta:.2f} - x) = {ALPHA:.10f}")
# x·(337.48-x) = α / coeff
target_product = ALPHA / coeff
print(f"    x · ({16*beta:.2f} - x) = {target_product:.6f}")
# x² - 337.48x + 842.1 = 0
a, b = 1, -16*beta
c = target_product
disc = b**2 - 4*a*c
if disc >= 0:
    x1 = (-b + np.sqrt(disc)) / 2
    x2 = (-b - np.sqrt(disc)) / 2
    print(f"    解: λ₀ = {x1:.6f} 或 {x2:.6f}")
    
    # 验证
    for x in [x1, x2]:
        alpha_calc = coeff * x * (16*beta - x)
        print(f"      λ₀={x:.6f}: α = {alpha_calc:.12f}  (err={abs(alpha_calc-ALPHA)/ALPHA:.4%})")

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("6. 直接从 Möbius 参数化计算波长和频率")
print("   λ_wave = ∮ ds = ∫₀^{4π} ||∂X/∂φ|| dφ")
print("   f ∝ Δλ = α · λ₁/(λ₂+λ₃)")
print("=" * 80)

# 计算 Möbius strip 的弧长
from scipy.integrate import quad

def mobius_arc_length_element(phi, w=0.3):
    """||∂X/∂φ|| for Möbius parametrization"""
    # X = ((1+w·cos(φ/2))·cos(φ), (1+w·cos(φ/2))·sin(φ), w·sin(φ/2))
    # dX/dφ = (-(1+w·cos(φ/2))·sin(φ) - (w/2)·sin(φ/2)·cos(φ),
    #           (1+w·cos(φ/2))·cos(φ) - (w/2)·sin(φ/2)·sin(φ),
    #           (w/2)·cos(φ/2))
    cos_half = np.cos(phi/2)
    sin_half = np.sin(phi/2)
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)
    
    dXdphi_x = -(1 + w*cos_half)*sin_phi - (w/2)*sin_half*cos_phi
    dXdphi_y = (1 + w*cos_half)*cos_phi - (w/2)*sin_half*sin_phi
    dXdphi_z = (w/2)*cos_half
    
    return np.sqrt(dXdphi_x**2 + dXdphi_y**2 + dXdphi_z**2)

for w in [0.1, 0.3, 0.5, 1.0, 2.0]:
    arc_len, _ = quad(mobius_arc_length_element, 0, 4*np.pi, args=(w,))
    # 中心线周长 (w=0) = 4π (因为 cos(φ) 在 [0, 4π) 走两圈)
    center_len = 4 * np.pi  # 2 * 2π = 4π
    ratio = arc_len / center_len
    print(f"  w={w}: arc_len = {arc_len:.6f}, center = {center_len:.6f}, ratio = {ratio:.6f}")
    
    # 也许 α = 1/(arc_len / (some_constant))
    # 或者 α = w² / arc_len²
    if w > 0:
        alpha_cand = w**2 / arc_len**2
        err = abs(alpha_cand - ALPHA) / ALPHA
        if err < 0.5:
            print(f"    w²/arc² = {alpha_cand:.10f}  (err={err:.2%})")
        
        alpha_cand2 = 1.0 / (arc_len / (2*np.pi))**2
        err2 = abs(alpha_cand2 - ALPHA) / ALPHA
        if err2 < 0.5:
            print(f"    1/(arc/2π)² = {alpha_cand2:.10f}  (err={err2:.2%})")

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("7. Möbius 环的精确弧长比 α")
print("   如果弧长 = 2π·R, 则波数 k = 2π/λ = 1/R")
print("   α 可能 = (w/R)² 或 (w/λ)² 的某个幂")
print("=" * 80)

# Möbius 中心线: R=1, 周长 = 4π (两圈)
# 微扰: w << 1, 弧长 ≈ 4π·√(1 + (w/2)²) (近似)
# 精确弧长 = 4π·(1 + O(w²))

# 对于 w << 1:
# arc ≈ 4π·(1 + w²/8)  (一阶修正)
# 所以 (arc - 4π)/4π ≈ w²/8

# 如果 α = w²/8, 则 w = √(8α) = √(8/137) = 0.2418
w_for_alpha = np.sqrt(8 * ALPHA)
print(f"  如果 α = w²/8, 则 w = {w_for_alpha:.6f}")
arc_check, _ = quad(mobius_arc_length_element, 0, 4*np.pi, args=(w_for_alpha,))
ratio_check = (arc_check - 4*np.pi) / (4*np.pi)
print(f"    验证: w={w_for_alpha:.6f}, arc={arc_check:.6f}, (arc-4π)/4π = {ratio_check:.10f}")
print(f"    α = {ALPHA:.10f}, w²/8 = {w_for_alpha**2/8:.10f}")

# 更一般: α = (arc - 4π) / (4π) × (something)
for w in [0.01, 0.1, 0.2418, 0.3, 0.5, 1.0]:
    arc, _ = quad(mobius_arc_length_element, 0, 4*np.pi, args=(w,))
    delta = (arc - 4*np.pi) / (4*np.pi)
    if abs(delta) > 1e-15:
        ratio_to_alpha = delta / ALPHA
        print(f"  w={w:8.4f}: (arc-4π)/4π = {delta:.10f}, ratio to α = {ratio_to_alpha:.4f}")

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("汇总")
print("=" * 80)
print(f"\n  4π 周期 Möbius 环 gap = tan²(π/n):")
print(f"    n=37: {np.tan(np.pi/37)**2:.12f} (err={abs(np.tan(np.pi/37)**2-ALPHA)/ALPHA:.4%})")
print(f"    n=38: {np.tan(np.pi/38)**2:.12f} (err={abs(np.tan(np.pi/38)**2-ALPHA)/ALPHA:.4%})")

print(f"\n  双 Möbius (4π) √(gap_e·gap_p) = tan(π/n_e)·tan(π/n_p):")
ne, np_ = best[0], best[1]
print(f"    n_e={ne}, n_p={np_}: {best[2]:.12f} (err={best[3]:.4%})")

print(f"\n  Möbius 弧长修正:")
print(f"    w=√(8α)={w_for_alpha:.6f}, (arc-4π)/4π = {ratio_check:.10f}")
print(f"    需要的修正因子 = {ratio_check / ALPHA:.4f}")
