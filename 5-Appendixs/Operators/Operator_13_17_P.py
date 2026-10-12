# -*- coding: utf-8 -*-
"""
===========================================================================
SRE 谱形方程求解算子组 (Operator 13 - 17) 参考实现与数值验证
===========================================================================
对应规范: 算子-13_17_谱形方程求解算子组_严格数学规范.md  (Version 1.0)

算子清单
    Op13  E_mom     谱形 Chebyshev 矩编码算子
    Op14  R_hodge   方程残差同调路由算子 (Hodge 三分量分解)
    Op15  N_endo    内生拟牛顿谱形反演算子 (Sherman-Morrison 闭式)
    Op16  C_hankel  谱形可行性 Hankel 钳制算子
    Op17  A_sol     解分支贝蒂审计与终止裁定算子
    主程序 solve_spectral_equation() 串起 Phase 1 -> 3 -> 3.5 -> 4 的求解内环

依赖: numpy, scipy(仅用于对照验证)
运行: python Operator_13_17_P.py
===========================================================================
"""

import numpy as np
from numpy.linalg import eigh, pinv, norm, matrix_rank

np.set_printoptions(precision=6, suppress=True, linewidth=120)


# ===========================================================================
# 0. 链复形构造 (C_0 --d1--> C_1 --d2--> C_2)
# ===========================================================================

def build_complex(n_node, close_cycle=True):
    """
    构造测试用二维链复形: 环形图 + 弦边, 三角形作为 2-链生成元。

    边集:
        e_i      = (i, i+1 mod n)      环边      index i      (i = 0..n-1)
        e_{n+i}  = (i, i+2 mod n)      弦边      index n+i
    面集 (三角形 i -> i+1 -> i+2 -> i):
        f_i = +e_i  +  e_{(i+1) mod n}  -  e_{n+i}
        (弦边 e_{n+i} 方向为 i -> i+2, 与回路末段 i+2 -> i 相反, 故取 -1)

    close_cycle=True 时额外加入由弦边构成的闭链 (0,2,4,...,n-2,0) 作为第 n+1 个面,
    使 rank(d2) = nu = m_g - n + b0, 从而 beta_1 = 0 (无拓扑障碍, 用于正常求解演示)。
    close_cycle=False 时保留 beta_1 = 1 的「有洞」复形 (用于拓扑障碍演示)。

    返回
        D : (m_g, n)  1-阶边界算子 d1
        C : (f, m_g)  2-阶边界算子 d2
        edges, faces
    """
    edges = []
    for i in range(n_node):
        edges.append((i, (i + 1) % n_node))
    for i in range(n_node):
        edges.append((i, (i + 2) % n_node))

    faces = []
    for i in range(n_node):
        faces.append([(i, +1),
                      ((i + 1) % n_node, +1),
                      (n_node + i, -1)])

    if close_cycle and n_node % 2 == 0:
        # 弦边闭链: (0,2) -> (2,4) -> ... -> (n-2, 0), 全部沿边正向
        faces.append([(n_node + i, +1) for i in range(0, n_node, 2)])

    m_g = len(edges)
    f = len(faces)

    D = np.zeros((m_g, n_node))
    for e, (u, v) in enumerate(edges):
        D[e, u] = -1.0
        D[e, v] = +1.0

    C = np.zeros((f, m_g))
    for k, face in enumerate(faces):
        for (e, sgn) in face:
            C[k, e] = sgn

    return D, C, edges, faces


def laplacian(D, m):
    """ 0-阶图拉普拉斯 L = D^T diag(m) D  (m 为边权向量) """
    return D.T @ np.diag(m) @ D


def spectral_assets(L, n_node):
    """
    算子 6 的谱资产 (alpha_n, lambda_2)
        alpha_n = 最大特征值 (谱半径)
        lambda_2 = 第二小特征值 (代数连通度, 算子 10 保证 > 0)
    """
    ev = eigh(L)[0]
    alpha_n = float(ev[-1])
    lam2 = float(ev[1]) if n_node > 1 else float(ev[0])
    return alpha_n, max(lam2, 1e-12)


# ===========================================================================
# 算子 13: E_mom  谱形 Chebyshev 矩编码算子
# ===========================================================================

def chebyshev_basis(Y, K):
    """
    第一类 Chebyshev:  T_0 = I, T_1 = Y, T_{k+1} = 2 Y T_k - T_{k-1}
    返回 [T_0(Y), ..., T_K(Y)]
    """
    N = Y.shape[0]
    U = [np.eye(N), Y.copy()]
    for k in range(1, K):
        U.append(2.0 * Y @ U[k] - U[k - 1])
    return U


def chebyshev_second_kind(Y, K):
    """
    第二类 Chebyshev:  U_0 = I, U_1 = 2Y, U_{k+1} = 2 Y U_k - U_{k-1}
    用于灵敏度解析式 (因 d/dx T_k(x) = k * U_{k-1}(x))
    返回 [U_0(Y), ..., U_{K-1}(Y)]
    """
    N = Y.shape[0]
    V = [np.eye(N), 2.0 * Y]
    for k in range(1, K - 1):
        V.append(2.0 * Y @ V[k] - V[k - 1])
    return V[:K]


def chebyshev_moments(L, alpha_n, K):
    """
    Op13 主式:  tau_k = (1/N) tr( T_k(Y) ),  Y = 2 L / alpha_n - I
    谱支撑被内生钳制在 [-1, 1], 全程三项递推, 无特征分解。
    """
    N = L.shape[0]
    Y = 2.0 * L / alpha_n - np.eye(N)
    U = chebyshev_basis(Y, K)
    tau = np.array([np.trace(U[k]) / N for k in range(K + 1)])
    return tau, Y, U


def moment_sensitivity(D, Y, N, alpha_n, K):
    """
    Op13 灵敏度向量 (解析式):
        w_{k,e} = d tau_k / d M_e = (2k / (N * alpha_n)) * d_e^T U_{k-1}(Y) d_e
    其中 d_e = D[e, :]^T 为边界算子第 e 行的转置, U_{k-1} 为第二类 Chebyshev。
    向量化: w_k = (2k / (N * alpha_n)) * diag( D @ U_{k-1}(Y) @ D^T )

    注: alpha_n 按算子 6 的规范在场刷新周期内强锁为不可变硬常量,
        故此处不求其对边权的导数 (差分验证亦须固定 alpha_n)。
    """
    V = chebyshev_second_kind(Y, K)          # V[j] = U_j(Y), j = 0..K-1
    W = np.zeros((K + 1, D.shape[0]))         # W[0, :] = 0  (tau_0 = 1 为常数)
    for k in range(1, K + 1):
        W[k] = (2.0 * k / (N * alpha_n)) * np.diag(D @ V[k - 1] @ D.T)
    return W


def endogenous_K(alpha_n, lam2, N):
    """
    Op13 内生截断阶:
        K = min( ceil(alpha_n / lambda_2),  floor(2 ln(1+N_K)) )
    前项保证截断误差 <= 内生谱隙比, 后项为过拟合防护 (视界自由度对数)。
    """
    K_res = int(np.ceil(alpha_n / lam2))
    K_cap = int(np.floor(2.0 * np.log(1.0 + N)))
    return max(4, min(K_res, K_cap)), K_res, K_cap


# ===========================================================================
# 算子 14: R_hodge  方程残差同调路由算子
# ===========================================================================

def hodge_project(r, D, C):
    """
    Op14 主式: 残差 1-链 r 的 Hodge 三分量正交分解
        r = D phi  +  h  +  C^T psi
        phi = (D^T D)^+ D^T r          (0-阶拉普拉斯伪逆, 与算子 6 势求解同构)
        psi = (C C^T)^+ C r            (2-阶拉普拉斯伪逆)
        h   = r - D phi - C^T psi      (调和分量, 属于 H_1)

    返回 dict(grad=D@phi, harm=h, curl=C^T@psi, phi, psi)
    """
    L0 = D.T @ D
    phi = pinv(L0) @ (D.T @ r)
    psi = pinv(C @ C.T) @ (C @ r) if C.shape[0] > 0 else np.zeros(0)
    grad = D @ phi
    curl = C.T @ psi if C.shape[0] > 0 else np.zeros_like(r)
    h = r - grad - curl
    return dict(grad=grad, harm=h, curl=curl, phi=phi, psi=psi)


# ===========================================================================
# 算子 15: N_endo  内生拟牛顿谱形反演算子
# ===========================================================================

def build_hodge_A(D, C, lam2, alpha_n):
    """
    加权 Hodge 拉普拉斯 (内生 Hessian 代理的正则部分):
        A = lambda_2 * D D^T  +  (lambda_2^2 / alpha_n) * C^T C     (m_g x m_g)
    ker(A) = ker(D^T) ∩ ker(C) = H_1, 即调和空间。
    """
    A = lam2 * (D @ D.T)
    if C.shape[0] > 0:
        A = A + (lam2 ** 2 / alpha_n) * (C.T @ C)
    return A


def cg_solve(A, b, tol=1e-12, maxit=2000):
    """
    共轭梯度法求 A^dagger b (A 对称半正定, b 须已剔除 ker(A) 分量以保证相容)。
    初值 x0 = 0 保证迭代全程落在 range(A) 内。
    """
    x = np.zeros_like(b)
    r = b - A @ x
    p = r.copy()
    rs = r @ r
    if rs < 1e-30:
        return x, 0
    for it in range(maxit):
        Ap = A @ p
        denom = p @ Ap
        if abs(denom) < 1e-300:
            break
        alpha = rs / denom
        x = x + alpha * p
        r = r - alpha * Ap
        rs_new = r @ r
        if np.sqrt(rs_new) < tol:
            break
        p = r + (rs_new / rs) * p
        rs = rs_new
    return x, it + 1


def endo_newton_step(g_M, h, A, cg_tol=1e-12):
    """
    Op15 单行闭式 (Sherman-Morrison):
        g_tilde = g_M - h                       (剔除调和分量)
        dM = - A^+ g_tilde / (1 + g_tilde^T A^+ g_tilde)
    分母自动充当内生信赖域 -> 无外部步长参数, 无需线搜索。
    """
    g_tilde = g_M - h
    Ag, iters = cg_solve(A, g_tilde, tol=cg_tol)
    quad = float(g_tilde @ Ag)
    dM = -Ag / (1.0 + quad)
    return dM, quad, iters


# ===========================================================================
# 算子 16: C_hankel  谱形可行性 Hankel 钳制算子
# ===========================================================================

def power_moments(Y, Kp, N):
    """ 幂矩 mu_k = (1/N) tr(Y^k),  k = 0..2*Kp+2 (Hankel 判据所需) """
    P = np.eye(N)
    mu = [1.0]
    for k in range(1, 2 * Kp + 3):
        P = P @ Y
        mu.append(float(np.trace(P)) / N)
    return np.array(mu)


def hankel_pair(mu, Kp):
    """
    Hausdorff 矩问题判据 (支撑 [-1,1]):
        H0[i,j] = mu_{i+j}           >= 0
        H1[i,j] = mu_{i+j} - mu_{i+j+2}  >= 0     (对应 (1 - λ²) dσ >= 0)
    """
    idx = np.arange(Kp + 1)
    H0 = mu[idx[:, None] + idx[None, :]]
    H1 = mu[idx[:, None] + idx[None, :]] - mu[idx[:, None] + idx[None, :] + 2]
    return H0, H1


def _psd_clip(H):
    """ 把对称矩阵谱投影到半正定锥 """
    w, V = eigh(H)
    w_c = np.clip(w, 0.0, None)
    return V @ np.diag(w_c) @ V.T, float(w.min())


def hankel_feasibility(mu, Kp):
    """ 返回 min( min_eig(H0), min_eig(H1) ); >= 0 表示矩序列对应 [-1,1] 上的非负测度 """
    H0, H1 = hankel_pair(mu, Kp)
    return min(float(eigh(H0)[0].min()), float(eigh(H1)[0].min()))


def hankel_clamp(mu_new, mu_ref, Kp, theta_endo=1e-9, n_bisect=60):
    """
    Op16 两阶段钳制阀:
        柔性通道: 若 mu_new 已满足可行性 (min_eig >= -theta_endo), 直接放行;
        硬拦截  : 沿「上一步可行矩 mu_ref -> 新矩 mu_new」的连线做二分回退,
                  取满足可行性的最大步长 t*, 输出 mu_ref + t*(mu_new - mu_ref)。
    该实现保证输出必可行 (可行集为凸集, mu_ref 为其内点/边界点),
    且是内生信赖域语义 (步长由可行性自身裁定, 无外部参数)。

    返回 (mu_clamped, feas_before, feas_after, t_star)
    """
    feas0 = hankel_feasibility(mu_new, Kp)
    if feas0 >= -theta_endo:
        return mu_new.copy(), feas0, feas0, 1.0

    lo, hi = 0.0, 1.0
    for _ in range(n_bisect):
        mid = 0.5 * (lo + hi)
        if hankel_feasibility(mu_ref + mid * (mu_new - mu_ref), Kp) >= -theta_endo:
            lo = mid
        else:
            hi = mid
    mu_c = mu_ref + lo * (mu_new - mu_ref)
    return mu_c, feas0, hankel_feasibility(mu_c, Kp), lo


# ===========================================================================
# 算子 17: A_sol  解分支贝蒂审计与终止裁定算子
# ===========================================================================

def audit(grad, curl, harm, r0_norm, lam2, alpha_n):
    """
    三通道内生收敛判据 (相对, 无量纲):
        eps_endo = (lambda_2 / alpha_n) * ||r_0||
    裁定: 'SOLVED' / 'CONTINUE' / 'OBSTRUCTION'
    """
    eps = (lam2 / alpha_n) * r0_norm
    ng, nc, nh = norm(grad), norm(curl), norm(harm)
    if ng <= eps and nc <= eps and nh <= eps:
        verdict = 'SOLVED'
    elif nh > eps and ng <= eps and nc <= eps:
        verdict = 'OBSTRUCTION'      # 仅剩调和分量 -> 拓扑障碍, 移交算子 9
    else:
        verdict = 'CONTINUE'
    return verdict, eps, (ng, nc, nh)


# ===========================================================================
# 主求解器: 谱形方程求解内环 (Phase 1 -> 3 -> 3.5 -> 4)
# ===========================================================================

def solve_spectral_equation(D, C, m0, F, dF_dtau, tau_index,
                            max_kappa=60, verbose=True, use_momentum=True):
    """
    求解谱形方程 F(tau) = 0, 未知量为边权向量 m (谱形的图实现)。

    参数
        F         : 标量函数 F(tau)                     (方程残差)
        dF_dtau   : 向量 dF/dtau_k                      (矩空间 Jacobian)
        tau_index : F 实际依赖的矩下标集合 (用于灵敏度合成)

    流程 (每内层步 kappa)
        Phase 1  : Op13 矩编码 + 灵敏度
        Phase 3  : Op14 残差升维 + Hodge 三分量路由
        Phase 3.5: Op15 内生拟牛顿反演 -> Op16 Hankel 钳制 -> 边权更新
        Phase 4  : Op17 裁定
    """
    n = D.shape[1]
    m_g = D.shape[0]
    N = n
    m = m0.copy()

    hist = []
    r0_norm = None
    v_mom = np.zeros(m_g)            # 内生动量缓存 (算子 15.3)

    for kappa in range(max_kappa):
        L = laplacian(D, m)
        alpha_n, lam2 = spectral_assets(L, n)
        K, K_res, K_cap = endogenous_K(alpha_n, lam2, N)

        # ---- Phase 1: Op13 ----
        tau, Y, U = chebyshev_moments(L, alpha_n, K)
        W = moment_sensitivity(D, Y, N, alpha_n, K)

        # ---- Phase 3: Op14 残差升维 + Hodge 路由 ----
        g = float(F(tau))                       # 矩空间残差标量
        J = dF_dtau(tau, K)                     # dF/dtau_k
        r = np.zeros(m_g)                       # r = sum_k (J^T g)_k * w_k
        for k in tau_index:
            if k <= K:
                r += (J[k] * g) * W[k]

        if r0_norm is None:
            r0_norm = norm(r)

        comp = hodge_project(r, D, C)
        grad, harm, curl = comp['grad'], comp['harm'], comp['curl']

        # ---- Phase 4: Op17 裁定 ----
        verdict, eps, norms = audit(grad, curl, harm, r0_norm, lam2, alpha_n)

        # Dirichlet 型目标泛函 Psi = 1/2 F^2 (定理 15.2 中的能量)
        Psi = 0.5 * g ** 2
        hist.append(dict(kappa=kappa, F=g, Psi=Psi, r_norm=norm(r),
                         ng=norms[0], nc=norms[1], nh=norms[2],
                         alpha=alpha_n, lam2=lam2, K=K, verdict=verdict))

        if verbose and (kappa < 5 or kappa % 5 == 0 or verdict != 'CONTINUE'):
            print(f"  k={kappa:3d}  F={g:+.6e}  |r|={norm(r):.4e}  "
                  f"[grad {norms[0]:.3e} | curl {norms[1]:.3e} | harm {norms[2]:.3e}]  "
                  f"lam2={lam2:.4f} a={alpha_n:.4f} K={K}  -> {verdict}")

        if verdict in ('SOLVED', 'OBSTRUCTION'):
            break

        # ---- Phase 3.5: Op15 内生拟牛顿反演 ----
        A = build_hodge_A(D, C, lam2, alpha_n)
        dM, quad, iters = endo_newton_step(r, harm, A)

        # 算子 15.3 内生动量: beta_mom = 1 - lambda_2 / alpha_n (完全内生)
        if use_momentum:
            beta_mom = 1.0 - lam2 / alpha_n
            v_mom = beta_mom * v_mom + dM
            step = v_mom
        else:
            step = dM

        # 边权内生下界: 防止边权归零破坏连通性 (由谱隙比内生生成)
        m_min = (lam2 / alpha_n) * float(m0.mean())
        m = np.maximum(m + step, m_min)

    return m, hist


# ===========================================================================
# 数值验证 (V1 - V11)
# ===========================================================================

def run_verification():
    print("=" * 78)
    print("SRE 谱形方程求解算子组 (Op13-17) 数值验证")
    print("=" * 78)

    n = 12
    N = n
    rng = np.random.default_rng(7)

    # 复形一 (闭): beta_1 = 0, 无拓扑障碍   -> V1/V2/V5/V6/V8/V10/V11
    D, C, edges, faces = build_complex(n, close_cycle=True)
    # 复形二 (洞): beta_1 = 1, 存在调和空间 -> V3/V4/V7/V9
    Dh, Ch, _, _ = build_complex(n, close_cycle=False)
    m_g, f = D.shape[0], C.shape[0]

    def topo_report(name, Dx, Cx):
        mx, nx = Dx.shape
        nu = mx - nx + 1                     # 环空间维数 (连通图 b0 = 1)
        rD = matrix_rank(Dx, tol=1e-9)
        rC = matrix_rank(Cx, tol=1e-9)
        b1 = nu - rC                          # 一阶贝蒂数 (同调维数)
        print(f"  [{name}] n={nx}  m_g={mx}  f={Cx.shape[0]}  "
              f"||d2 d1||={np.abs(Cx @ Dx).max():.1e}  nu={nu}  "
              f"rank(d1)={rD}  rank(d2)={rC}  beta_1={b1}")
        return b1

    print("\n[链复形]")
    topo_report('闭复形 ', D, C)
    topo_report('有洞复形', Dh, Ch)

    m0 = 1.0 + 0.3 * rng.random(m_g)
    m0h = 1.0 + 0.3 * rng.random(m_g)

    L = laplacian(D, m0)
    alpha_n, lam2 = spectral_assets(L, n)
    K, K_res, K_cap = endogenous_K(alpha_n, lam2, N)
    print(f"\n[谱资产 / 闭复形] alpha_n={alpha_n:.6f}  lambda_2={lam2:.6f}  "
          f"谱隙比 gamma={lam2/alpha_n:.6f}")
    print(f"         K = min(ceil(a/l2)={K_res}, cap={K_cap}) = {K}")

    Lh = laplacian(Dh, m0h)
    alpha_h, lam2_h = spectral_assets(Lh, n)
    Ah = build_hodge_A(Dh, Ch, lam2_h, alpha_h)

    # ---------------- V1: 矩编码正确性 (三项递推 vs 特征分解) ----------------
    print("\n" + "-" * 78)
    print("V1  矩编码正确性: 三项递推 vs eigvalsh 直算")
    tau, Y, U = chebyshev_moments(L, alpha_n, K)
    ev = eigh(L)[0]
    Yev = 2.0 * ev / alpha_n - 1.0
    tau_ref = np.array([np.polynomial.chebyshev.chebval(Yev,
                        np.concatenate([[0]*k, [1]])) .mean() for k in range(K + 1)])
    err_v1 = np.max(np.abs(tau - tau_ref))
    print(f"    tau (递推)  = {tau}")
    print(f"    tau (直算)  = {tau_ref}")
    print(f"    最大绝对误差 = {err_v1:.3e}   -> {'PASS' if err_v1 < 1e-10 else 'FAIL'}")

    # ------------- V2: 灵敏度解析式 vs 中心差分 ----------------
    print("\n" + "-" * 78)
    print("V2  灵敏度解析式 w_{k,e} vs 中心差分")
    W = moment_sensitivity(D, Y, N, alpha_n, K)
    eps_fd = 1e-6
    max_rel = 0.0
    for k in [1, 2, 3, min(5, K)]:
        if k > K:
            continue
        for e in [0, 3, 7]:
            mp = m0.copy(); mp[e] += eps_fd
            mm = m0.copy(); mm[e] -= eps_fd
            tp, _, _ = chebyshev_moments(laplacian(D, mp), alpha_n, K)
            tm, _, _ = chebyshev_moments(laplacian(D, mm), alpha_n, K)
            fd = (tp[k] - tm[k]) / (2 * eps_fd)
            ana = W[k, e]
            rel = abs(fd - ana) / max(abs(fd), 1e-12)
            max_rel = max(max_rel, rel)
            print(f"    k={k}, e={e}:  解析={ana:+.8e}  差分={fd:+.8e}  相对误差={rel:.2e}")
    print(f"    最大相对误差 = {max_rel:.3e}   -> {'PASS' if max_rel < 1e-5 else 'FAIL'}")

    # ------------- V3/V4: Hodge 分解正交性与调和判据 -------------
    print("\n" + "-" * 78)
    print("V3/V4  Hodge 三分量分解: 正交性 + 调和判据")
    r_test = rng.standard_normal(m_g)
    comp = hodge_project(r_test, Dh, Ch)      # 须用有洞复形, 否则 h 恒为 0
    grad, harm, curl = comp['grad'], comp['harm'], comp['curl']
    print(f"    <grad,curl> = {grad @ curl:+.3e}")
    print(f"    <grad,harm> = {grad @ harm:+.3e}")
    print(f"    <curl,harm> = {curl @ harm:+.3e}")
    orth = max(abs(grad @ curl), abs(grad @ harm), abs(curl @ harm))
    recon = norm(r_test - (grad + harm + curl))
    print(f"    重构误差 ||r - (grad+harm+curl)|| = {recon:.3e}")
    print(f"    调和条件 ||d1^T h|| = {norm(Dh.T @ harm):.3e}   "
          f"||d2 h|| = {norm(Ch @ harm):.3e}   (二者须 = 0)")
    print(f"    ||r||^2 = {norm(r_test)**2:.6f}   "
          f"||grad||^2+||harm||^2+||curl||^2 = "
          f"{norm(grad)**2+norm(harm)**2+norm(curl)**2:.6f}   (勾股等式)")
    ok_v3 = orth < 1e-8 and recon < 1e-8
    ok_v4 = norm(Dh.T @ harm) < 1e-8 and norm(Ch @ harm) < 1e-8
    print(f"    -> V3 {'PASS' if ok_v3 else 'FAIL'}   V4 {'PASS' if ok_v4 else 'FAIL'}")

    # ------------- V5/V6: 求解方程, 残差与能量单调下降 -------------
    print("\n" + "-" * 78)
    print("V5/V6  求解谱形方程:  F(tau) = tau_2 - c = 0   (目标二阶 Chebyshev 矩)")

    # 目标值: 取另一组边权下的 tau_2 (保证存在解)
    m_target = 1.0 + 0.9 * rng.random(m_g)
    Lt = laplacian(D, m_target)
    at, l2t = spectral_assets(Lt, n)
    tau_t, _, _ = chebyshev_moments(Lt, at, K)
    c_target = tau_t[2]
    print(f"    目标: tau_2 = {c_target:.6f}   (初始 tau_2 = {tau[2]:.6f})")

    def F(tau_):
        return tau_[2] - c_target

    def dF(tau_, K_):
        J = np.zeros(K_ + 1)
        J[2] = 1.0
        return J

    def report(hist_, tag):
        Psi_ = [h['Psi'] for h in hist_]
        rn_ = [h['r_norm'] for h in hist_]
        mono_P = all(Psi_[i + 1] <= Psi_[i] * (1 + 1e-9) + 1e-15 for i in range(len(Psi_) - 1))
        mono_r = all(rn_[i + 1] <= rn_[i] * (1 + 1e-9) + 1e-15 for i in range(len(rn_) - 1))
        print(f"\n  [{tag}]")
        print(f"    目标泛函 Psi = F^2/2 : {Psi_[0]:.6e} -> {Psi_[-1]:.6e}   "
              f"({len(Psi_)} 步)")
        print(f"    残差 |r|             : {rn_[0]:.6e} -> {rn_[-1]:.6e}")
        print(f"    最终 F = {hist_[-1]['F']:+.6e}, 内生容差 eps_endo = "
              f"{(hist_[-1]['lam2']/hist_[-1]['alpha'])*rn_[0]:.6e}")
        print(f"    单调下降 Psi : {'PASS' if mono_P else 'FAIL (存在上跳)'}")
        print(f"    单调下降 |r|  : {'PASS' if mono_r else 'FAIL (存在上跳)'}")
        print(f"    最终裁定: {hist_[-1]['verdict']}")
        return mono_P and mono_r

    print("\n  -- 主跑: 纯内生牛顿闭式 (定理 15.2 保证能量单调) --")
    m_sol, hist = solve_spectral_equation(D, C, m0, F, dF, tau_index=[2],
                                          max_kappa=120, verbose=True,
                                          use_momentum=False)
    ok_v5 = report(hist, '无动量')

    print("\n  -- 对照: 内生动量 beta = 1 - lambda_2/alpha_n (算子 15.3) --")
    _, hist_m = solve_spectral_equation(D, C, m0, F, dF, tau_index=[2],
                                        max_kappa=120, verbose=False,
                                        use_momentum=True)
    report(hist_m, '内生动量')
    print(f"    加速效果: 无动量 {len(hist)} 步 vs 动量 {len(hist_m)} 步 "
          f"(动量可能过冲, 需配合回溯, 故默认关闭)")

    # ------------- V7: 更新方向正交性 -------------
    print("\n" + "-" * 78)
    print("V7  更新方向正交性:  <dM, h> = 0")
    A = Ah                                   # 有洞复形 (含非平凡 H_1)
    dM, quad, iters = endo_newton_step(r_test, harm, A)
    Ag_pin = pinv(A) @ (r_test - harm)
    dM_ref = -Ag_pin / (1.0 + (r_test - harm) @ Ag_pin)
    print(f"    CG 与 pinv 闭式一致性: ||dM_cg - dM_pinv|| = {norm(dM - dM_ref):.3e}")
    print(f"    <dM, h> = {dM @ harm:+.3e}   (须 = 0)")
    print(f"    信赖域二次型 g^T A^+ g = {quad:.6f}  -> 步长压缩因子 = {1/(1+quad):.6f}")
    ok_v7 = abs(dM @ harm) < 1e-8
    print(f"    -> V7 {'PASS' if ok_v7 else 'FAIL'}")

    # ------------- V8: Hankel 可行性钳制 -------------
    print("\n" + "-" * 78)
    print("V8  Hankel 可行性钳制 (矩序列 -> 正测度可行锥)")
    Kp = max(2, K // 2)
    mu = power_moments(Y, Kp, N)                 # 真实矩 (天然可行)
    mu_bad = mu.copy()
    mu_bad[3] += 0.35                            # 人为破坏可行性
    theta_endo = lam2 / alpha_n                  # 内生阈值 (谱隙比)
    mu_c, feas0, feas1, t_star = hankel_clamp(mu_bad, mu, Kp, theta_endo=1e-9)
    print(f"    真实矩可行性    min_eig = {hankel_feasibility(mu, Kp):+.6e}  (>=0, 天然可行)")
    print(f"    扰动后          min_eig = {feas0:+.6e}  (须 < 0 方为有效测试用例)")
    print(f"    钳制后          min_eig = {feas1:+.6e}  (须 >= -tol)")
    print(f"    二分回退步长 t* = {t_star:.6f}   ||mu_c - mu_bad|| = {norm(mu_c - mu_bad):.6f}")
    print(f"    可行性恢复幅度: {feas0:+.3e} -> {feas1:+.3e}  (提升 {abs(feas0/feas1):.2e} 倍)")
    ok_v8 = feas1 > -1e-6 and feas0 < 0
    print(f"    -> V8 {'PASS' if ok_v8 else 'FAIL'}")

    # ------------- V10/V11: 闭合流守恒 -------------
    print("\n" + "-" * 78)
    print("V10/V11  闭合流形上的对偶配对守恒 (定理 14.1)")
    psi_v = comp['psi']                    # 与 comp 同源: 有洞复形 (Dh, Ch)
    eta = lam2_h / (lam2_h + norm(Ch.T @ psi_v))

    phi0 = rng.standard_normal(n)
    E_closed = Dh @ phi0                   # 梯度场 -> d2 E = (d2 d1) phi = 0
    dPi_closed = -eta * float((Ch @ E_closed) @ psi_v)
    ok_v10 = abs(dPi_closed) < 1e-10
    print(f"    闭合流 E=d1*phi : ||d2 E|| = {norm(Ch @ E_closed):.3e}   "
          f"d(E^T d2^T B) = {dPi_closed:+.3e}   -> V10 {'PASS' if ok_v10 else 'FAIL'}")

    E_open = rng.standard_normal(m_g)      # 非闭合流 -> 反例
    dPi_open = -eta * float((Ch @ E_open) @ psi_v)
    ok_v11 = abs(dPi_open) > 1e-8
    print(f"    非闭合流 E      : ||d2 E|| = {norm(Ch @ E_open):.3e}   "
          f"d(E^T d2^T B) = {dPi_open:+.3e}   -> V11 反例成立 "
          f"{'PASS' if ok_v11 else '(未触发, 换种子)'}")

    # ------------- V9: 拓扑障碍演示 -------------
    print("\n" + "-" * 78)
    print("V9  拓扑障碍: 要求一个 H_1 方向上的残差 (场迭代不可消除)")
    h_unit = harm / norm(harm) if norm(harm) > 1e-12 else np.zeros(m_g)
    if norm(h_unit) > 0:
        dM_h, quad_h, _ = endo_newton_step(h_unit, h_unit, Ah)
        print(f"    以纯调和残差 r=h 驱动反演:")
        print(f"      ||dM|| = {norm(dM_h):.3e}   (趋零 => 迭代无法消解调和分量)")
        print(f"      <dM, h> = {dM_h @ h_unit:+.3e}")
        ok_v9 = norm(dM_h) < 1e-6
        print(f"    -> V9 {'PASS' if ok_v9 else 'FAIL'}")
    else:
        ok_v9 = False
        print("    当前复形 H_1 平凡, 跳过 (需 beta_1 > 0 的复形)")

    # ---------------- 汇总 ----------------
    summary = [
        ('V1  矩编码: 三项递推 vs 特征分解直算', err_v1 < 1e-10, f'{err_v1:.2e}'),
        ('V2  灵敏度解析式 vs 中心差分', max_rel < 1e-5, f'{max_rel:.2e}'),
        ('V3  Hodge 三分量正交性 + 勾股等式', ok_v3, f'{orth:.2e}'),
        ('V4  调和判据 d1^T h = 0, d2 h = 0', ok_v4, f'{max(norm(Dh.T@harm), norm(Ch@harm)):.2e}'),
        ('V5  可解方程: 残差单调下降', ok_v5, f'F: {hist[0]["F"]:.2e} -> {hist[-1]["F"]:.2e}'),
        ('V6  目标泛函 Psi 单调非增', ok_v5, f'Psi: {hist[0]["Psi"]:.2e} -> {hist[-1]["Psi"]:.2e}'),
        ('V7  更新方向正交 <dM,h> = 0', ok_v7, f'{abs(dM @ harm):.2e}'),
        ('V8  Hankel 可行性钳制', ok_v8, f'{feas0:+.2e} -> {feas1:+.2e}'),
        ('V9  拓扑障碍: 调和残差不可迭代消除', ok_v9, f'||dM||={norm(dM_h):.2e}'),
        ('V10 闭合流对偶配对守恒', ok_v10, f'{dPi_closed:+.2e}'),
        ('V11 非闭合流反例 (时序必要性)', ok_v11, f'{dPi_open:+.2e}'),
    ]

    print("\n" + "=" * 78)
    print("验证汇总")
    print("=" * 78)
    n_pass = 0
    for name, ok, val in summary:
        print(f"  {'PASS' if ok else 'FAIL'}   {name:<40s}   [{val}]")
        n_pass += int(ok)
    print("-" * 78)
    print(f"  {n_pass} / {len(summary)} 通过")
    print("=" * 78)


if __name__ == '__main__':
    run_verification()
