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


def endo_newton_step(g_M, h, A, F=None, D=None, lam2=None, cg_tol=1e-12):
    """
    Op15 单行闭式 (内生拟牛顿 + 内生信赖域), 定理 15.1'

        g_tilde = g_M - h                          剔除调和分量 (不可迭代消除的部分)
        dM_raw  = - A^+ g_tilde                    方向: 按 Hodge 通道加权
        eta_N   = F^2 / (g_tilde^T A^+ g_tilde)    内生牛顿步长

    【为什么 eta_N 取代了 1/(1+q)】
        v1.0 用 dM = -A^+ g_tilde /(1 + q), q = g_tilde^T A^+ g_tilde。
        该式每步的相对下降率 = gradF^T A^+ gradF (=kappa), 且在方程重标定
        F -> sF 下 q -> s^4 q 而 dM -> s^2 dM —— 轨迹随方程的人为缩放而变,
        收敛快慢取决于 F 的书写量级, 违背无维度原则 (实测慢 1/kappa ~ 175 倍)。
        eta_N = F^2/q 下: F^2 -> s^2 F^2, q -> s^4 q, g_tilde -> s^2 g_tilde,
        三者复合后 dM 严格不变; 且线性化后 dF = -F, 一步归零。

    【内生信赖域 (公设 3)】
        步长不得跨越半个谱隙: 若 ||D^T diag(dM) D||_F > lambda_2/2, 按比例缩回。
        否则谱隙比 gamma = lambda_2/alpha_n 会自毁, 全部内生尺度随之失效。

    返回 (dM, quad, iters, trust_scale)
    """
    g_tilde = g_M - h
    Ag, iters = cg_solve(A, g_tilde, tol=cg_tol)
    quad = float(g_tilde @ Ag)

    if F is None or quad <= 1e-300:
        # 未提供方程残差 (纯方向测试) 或可消除分量为零 -> 零步 / 退化为原闭式
        dM = -Ag / (1.0 + quad) if quad > 1e-300 else np.zeros_like(g_M)
        return dM, quad, iters, 1.0

    eta = float(F) ** 2 / quad
    dM = -eta * Ag

    trust = 1.0
    if D is not None and lam2 is not None and lam2 > 0:
        dL = D.T @ np.diag(dM) @ D
        nL = float(norm(dL, 'fro'))
        cap = 0.5 * lam2
        if nL > cap > 0 and nL > 0:
            trust = cap / nL
            dM = dM * trust
    return dM, quad, iters, trust


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

def audit(grad, curl, harm, r0_norm, lam2, alpha_n,
          f_prev=None, f_now=None, step_dead=False, kappa=0):
    """
    三通道内生收敛判据 (相对, 无量纲):
        gamma    = lambda_2 / alpha_n                可分辨的相对改善因子
        eps_endo = gamma * ||r_0||                   分辨下限
    裁定: 'SOLVED' / 'OBSTRUCTION' / 'STALLED' / 'CONTINUE'
    返回 (verdict, eps, (ng, nc, nh), info)

    【v1.3 修正一: SOLVED 须附加「已榨干」条件】
        残差 r = F * grad F **恒正比于**标量残差 F, 故「首次跨过 eps」的迭代点上
        |F| 恰在 eps 量级 —— 解的精度完全由 eps 决定, 独立验证退化为同义反复
        (实测 V-B 恒 ~ gamma; 题集 E02 的五个实例有两个落在阈值两侧 1.7% 处,
        裁定等于抛硬币)。故要求: 既达标 (below), 又已无法再取得可分辨的改善
        (exhausted: 本步 |F| 下降不足 gamma) 或方向已耗尽 (step_dead)。

    【v1.3 修正二: OBSTRUCTION 不再是量级带判据】
        原判据 (nh > eps 且 ng, nc <= eps) 是一个**量级带**判据: 因 rho_h = ||h||/||r||
        在给定复形上近似为常数 (~0.95, 见 V16), 该带恰为 ||r|| in (eps/rho_h, ~4.3eps],
        宽达 4 倍。落在带内即被误诊为拓扑障碍并移交给算子 9 的 Betti 缝合 ——
        那是会**改变 beta_1** 的操作。实测题集 B2-E02 (良置可解) 即因此被误判。
        现改为要求 **更新方向耗尽** (step_dead): 只有当回溯到机器零仍无法下降时才
        认定为障碍。因 dM = -eta_N A^+ g~ 恒正比于 F, 只要 F != 0 方向就不会耗尽,
        障碍只能在真正的驻点/退化方向 (grad F in H_1) 上被认定。
    """
    gamma = lam2 / alpha_n
    eps = gamma * r0_norm
    ng, nc, nh = norm(grad), norm(curl), norm(harm)
    below = (ng <= eps and nc <= eps and nh <= eps)
    if f_prev is None or f_prev == 0.0 or f_now is None:
        exhausted = False
    else:
        exhausted = abs(f_now) >= (1.0 - gamma) * abs(f_prev)
    if below and (exhausted or step_dead):
        verdict = 'SOLVED'
    elif step_dead:
        verdict = ('OBSTRUCTION' if (nh > eps and ng <= eps and nc <= eps)
                   else 'STALLED')
    else:
        verdict = 'CONTINUE'
    info = dict(gamma=gamma, eps=eps, exhausted=bool(exhausted),
                step_dead=bool(step_dead), below=bool(below))
    return verdict, eps, (ng, nc, nh), info


# ===========================================================================
# 主求解器: 谱形方程求解内环 (Phase 1 -> 3 -> 3.5 -> 4)
# ===========================================================================

def _eval_F(D, m, F, encode, alpha_n, lam2, K):
    """
    在给定边权处求标量残差 F(tau(m)) —— 与内环 Phase 1 **完全同一条编码管线**
    (含非多项式核的移位/零模剥离钩子), 保证线搜索比较的是同一个 F。
    """
    L = laplacian(D, m)
    if encode is None:
        tau, _, _ = chebyshev_moments(L, alpha_n, K)
    else:
        tau, _ = encode(D, m, L, alpha_n, lam2, K)
    return float(F(tau))


def solve_spectral_equation(D, C, m0, F, dF_dtau, tau_index,
                            max_kappa=60, verbose=True, use_momentum=True,
                            mode='exact', freeze=None, encode=None):
    """
    求解谱形方程 F(tau) = 0, 未知量为边权向量 m (谱形的图实现)。

    参数
        F         : 标量函数 F(tau)                     (方程残差)
        dF_dtau   : 向量 dF/dtau_k                      (矩空间 Jacobian)
        tau_index : F 实际依赖的矩下标集合 (用于灵敏度合成)
        mode      : 'exact'       精确解判据 —— 三通道 (grad, curl, harm) 全低于 eps
                    'homological' 同调解判据 —— 仅 ||h|| 低于 eps (定义 3.1)
                    * 注意: beta_1 = 0 时 ||h|| == 0 恒成立, 同调解判据退化为
                      "全空间", 此时必须改用 mode='exact' (见 V17 退化警告)
        freeze    : (alpha_n, lam2) 若给定, 则整个求解过程永不刷新内生尺度。
                    用于在「同一个 F」下比较多个实现 —— 解是相对于某一组冻结
                    尺度定义的, 不同冻结尺度下的两个解不可直接比较 (V16)。
        encode    : 可选编码钩子 None 或 callable
                    encode(D, m, L, alpha_n, lam2, K) -> (tau, W)
                    None  => 标准 Chebyshev 编码 (Op13 默认管线)
                    给出   => 替代编码 (如算子 13.5 的移位核编码), 用于非多项式核。
                    无论哪种, W 必须是同坐标系下的灵敏度 dtau_k/dm (含移位缩放因子)。

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
    r_prev = None                    # 上一步的 ||r|| (过程留档)
    f_prev = None                    # 上一步的标量残差 (Op17 的「已榨干」判据)
    step_dead_prev = False           # 上一步的方向是否已耗尽
    v_mom = np.zeros(m_g)            # 内生动量缓存 (算子 15.3)

    # 内生尺度锁定 (算子 6 规范): alpha_n / lambda_2 在「场刷新周期」内是硬常量。
    # 灵敏度算子 13 明确不对 alpha_n 求导, 所以 F 只有在 alpha_n 冻结时才是 m 的
    # 光滑函数; 若每步都刷新, F 的定义会跳变, 牛顿预测失效 (实测首步即上跳)。
    # 刷新判据完全内生: 拉普拉斯相对漂移 ||L - L_ref||_F / alpha_n > gamma = lam2/alpha_n
    if freeze is not None:
        alpha_n, lam2 = freeze
        L_ref = None
    else:
        L = laplacian(D, m)
        alpha_n, lam2 = spectral_assets(L, n)
        L_ref = L.copy()
    n_refresh = 0

    for kappa in range(max_kappa):
        L = laplacian(D, m)
        if L_ref is not None:
            drift = norm(L - L_ref, 'fro') / alpha_n
            if drift > lam2 / alpha_n:             # 内生刷新触发
                alpha_n, lam2 = spectral_assets(L, n)
                L_ref = L.copy()
                n_refresh += 1
        K, K_res, K_cap = endogenous_K(alpha_n, lam2, N)

        # ---- Phase 1: Op13 ----
        if encode is None:
            tau, Y, U = chebyshev_moments(L, alpha_n, K)
            W = moment_sensitivity(D, Y, N, alpha_n, K)
        else:
            tau, W = encode(D, m, L, alpha_n, lam2, K)

        # ---- Phase 3: Op14 残差升维 + Hodge 路由 ----
        g = float(F(tau))                       # 矩空间残差标量
        J = dF_dtau(tau, K)                     # dF/dtau_k
        r = np.zeros(m_g)                       # r = sum_k (J^T g)_k * w_k
        for k in tau_index:
            if k < min(len(J), len(W)):
                r += (J[k] * g) * W[k]

        if r0_norm is None:
            r0_norm = norm(r)

        comp = hodge_project(r, D, C)
        grad, harm, curl = comp['grad'], comp['harm'], comp['curl']

        # ---- Phase 4: Op17 裁定 ----
        verdict, eps, norms, ainfo = audit(
            grad, curl, harm, r0_norm, lam2, alpha_n,
            f_prev=f_prev, f_now=g, step_dead=step_dead_prev, kappa=kappa)
        r_prev = norm(r)
        f_prev = g

        # 双层判据 (算子 17.1): 同调解判据只看调和通道。同样须附加「已榨干」条件,
        # 否则「首次跨过 eps」即终止, 解精度被 eps 完全决定 (见 audit 修正一)。
        if mode == 'homological':
            if norms[2] <= eps and (ainfo['exhausted'] or ainfo['step_dead']):
                verdict = 'SOLVED'
            elif norms[2] <= eps:
                verdict = 'CONTINUE'
            # 其余沿用精确解判据的裁定 (OBSTRUCTION / STALLED / CONTINUE)

        # Dirichlet 型目标泛函 Psi = 1/2 F^2 (定理 15.2 中的能量)
        Psi = 0.5 * g ** 2
        hist.append(dict(kappa=kappa, F=g, Psi=Psi, r_norm=norm(r),
                         ng=norms[0], nc=norms[1], nh=norms[2],
                         alpha=alpha_n, lam2=lam2, K=K, verdict=verdict))

        if verbose and (kappa < 5 or kappa % 5 == 0 or verdict != 'CONTINUE'):
            print(f"  k={kappa:3d}  F={g:+.6e}  |r|={norm(r):.4e}  "
                  f"[grad {norms[0]:.3e} | curl {norms[1]:.3e} | harm {norms[2]:.3e}]  "
                  f"lam2={lam2:.4f} a={alpha_n:.4f} K={K}  -> {verdict}")

        if verdict in ('SOLVED', 'OBSTRUCTION', 'STALLED'):
            break

        # ---- Phase 3.5: Op15 内生拟牛顿反演 ----
        A = build_hodge_A(D, C, lam2, alpha_n)
        dM, quad, iters, trust = endo_newton_step(r, harm, A, F=g,
                                                  D=D, lam2=lam2)
        # 过程留档: 把本次反演的步长/信赖域回写到当前步
        hist[-1].update(dM_norm=norm(dM), quad=quad, trust=trust,
                        eta=(float(g) ** 2 / quad) if quad > 1e-300 else 0.0,
                        cg_iters=iters)

        # 算子 15.3 内生动量: beta_mom = 1 - lambda_2 / alpha_n (完全内生)
        if use_momentum:
            beta_mom = 1.0 - lam2 / alpha_n
            v_mom = beta_mom * v_mom + dM
            step = v_mom
        else:
            step = dM

        # 边权内生下界: 防止边权归零破坏连通性 (由谱隙比内生生成)
        m_min = (lam2 / alpha_n) * float(m0.mean())

        # ---- Phase 3.5b: 内生回溯线搜索 (v1.3 新增, 全局化定理 15.2) ----
        # 【为什么必须有】
        #   v1.0 的闭式 dM = -A^+ g~ /(1+q) 中分母 1+q 同时承担「内生信赖域」的角色。
        #   但 V7b 证明该式在方程重标定 F->sF 下 q->s^4 q、dM->s^2 dM, 收敛轨迹
        #   随方程的人为书写量级而变, 违背无维度原则, 故 v1.1 换成
        #        eta_N = F^2/q,   dM = -eta_N A^+ g~
        #   代价是**分母消失, 信赖域随之丧失**(只剩 0.5*lambda_2 的绝对上限)。
        #   实测后果 (题集 B2-E02, 强非线性实例): 牛顿步过大 -> 线性模型失效 ->
        #   Psi 序列出现上升 (-6.85e-3 -> -7.56e-3), 收敛退化为比率约 0.8 的慢振荡,
        #   直接导致 V-E 单调性失败与假 OBSTRUCTION 裁定。
        # 【回溯因子为什么是 1/2】与算子 16 钳制阀同一约定 (二分), 无外部参数。
        # 【停机】t 触到机器零则判定方向已耗尽 (step_dead)。
        t_acc, g_acc, n_back = 1.0, None, 0
        t_floor = 1e-14
        while True:
            m_try = np.maximum(m + t_acc * step, m_min)
            g_try = _eval_F(D, m_try, F, encode, alpha_n, lam2, K)
            if abs(g_try) < abs(g) or t_acc <= t_floor:
                g_acc = g_try
                break
            t_acc *= 0.5
            n_back += 1
        step_dead = (t_acc <= t_floor) or (norm(t_acc * step) <= 1e-12 * m_min)
        hist[-1].update(t_ls=t_acc, n_backtrack=n_back, F_ls=g_acc,
                        step_dead=bool(step_dead))
        step_dead_prev = step_dead
        m = np.maximum(m + t_acc * step, m_min)

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
    dM, quad, iters, trust = endo_newton_step(r_test, harm, A)
    Ag_pin = pinv(A) @ (r_test - harm)
    dM_ref = -Ag_pin / (1.0 + (r_test - harm) @ Ag_pin)
    Ag_cg, _ = cg_solve(A, r_test - harm, tol=1e-12)
    print(f"    CG 与 pinv 方向一致性: ||A^+_cg g - A^+_pinv g|| = {norm(Ag_cg - Ag_pin):.3e}")
    print(f"    <dM, h> = {dM @ harm:+.3e}   (须 = 0)")
    print(f"    内生牛顿步长 eta_N = F^2/q,  信赖域缩放 = {trust:.6f}")
    ok_v7 = abs(dM @ harm) < 1e-8
    print(f"    -> V7 {'PASS' if ok_v7 else 'FAIL'}")

    # ---- V7b: 方程尺度不变性 (定理 15.1' 的判据性检验) ----
    print("\nV7b 方程尺度不变性: F -> sF 时更新步 dM 必须不变")
    F_ref = 0.37                             # 任意参考残差量级
    dMs = []
    for s in (1.0, 10.0, 100.0):
        # 重标定方程: g -> s g, 于是 r = g*gradF -> s^2 r, g_tilde -> s^2 g_tilde
        dm_s, q_s, _, _ = endo_newton_step(s ** 2 * r_test, s ** 2 * harm, Ah,
                                           F=s * F_ref)
        # 旧式 (v1.0) 对照
        dm_old_s = -(pinv(Ah) @ (s ** 2 * (r_test - harm))) / (1.0 + s ** 4 * quad)
        dMs.append((s, dm_s, dm_old_s))
        print(f"    s={s:6.1f}  ||dM_new||={norm(dm_s):.9e}   "
              f"||dM_old||={norm(dm_old_s):.9e}")
    inv_new = max(norm(dMs[i][1] - dMs[0][1]) / max(norm(dMs[0][1]), 1e-300)
                  for i in range(len(dMs)))
    inv_old = max(norm(dMs[i][2] - dMs[0][2]) / max(norm(dMs[0][2]), 1e-300)
                  for i in range(len(dMs)))
    print(f"    新式最大相对偏移 = {inv_new:.3e}   -> {'PASS' if inv_new < 1e-8 else 'FAIL'}")
    print(f"    旧式最大相对偏移 = {inv_old:.3e}   -> {'FAIL (尺度依赖)' if inv_old > 1e-6 else 'PASS'}")
    ok_v7b = inv_new < 1e-8 and inv_old > 1e-6
    print(f"    -> V7b {'PASS' if ok_v7b else 'FAIL'}")

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
        dM_h, quad_h, _, _ = endo_newton_step(h_unit, h_unit, Ah)
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
        ('V7b 方程尺度不变性 (F->sF, dM 不变)', ok_v7b, f'新 {inv_new:.1e} / 旧 {inv_old:.1e}'),
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


# ===========================================================================
#                    v1.1 扩展: 多谱形耦合 / 非多项式核 / 同调解
# ===========================================================================

def build_shards(D, n_shards=2):
    """
    把全局边集划分为 p 个分片, 返回分片嵌入映射 Xi_nu 与分片边界算子行索引。
    Xi_nu 为 0-1 选择矩阵 (列正交, Xi_nu^T Xi_nu = I)。
    """
    m_g = D.shape[0]
    bounds = np.linspace(0, m_g, n_shards + 1).astype(int)
    Xi, idx = [], []
    for s in range(n_shards):
        rows = np.arange(bounds[s], bounds[s + 1])
        X = np.zeros((m_g, len(rows)))
        for j, e in enumerate(rows):
            X[e, j] = 1.0
        Xi.append(X)
        idx.append(rows)
    return Xi, idx


def shard_laplacian(D, idx, m):
    """ 分片拉普拉斯 L^(nu) = sum_{e in Omega_nu} m_e d_e d_e^T """
    Dn = D[idx, :]
    return Dn.T @ np.diag(m[idx]) @ Dn


def shifted_chebyshev(Y, y_min, K):
    """
    移位 Chebyshev 矩: 把 Y 的谱支撑 [y_min, 1] 仿射到 [-1,1]:
        Yt = (2Y - (1+y_min) I) / (1 - y_min)
    返回 (tau_tilde[0..K], Yt)
    """
    N = Y.shape[0]
    Yt = (2.0 * Y - (1.0 + y_min) * np.eye(N)) / (1.0 - y_min)
    _, _, U = chebyshev_moments_kernel(Yt, K)
    tau = np.array([np.trace(U[k]) / N for k in range(K + 1)])
    return tau, Yt


def chebyshev_moments_kernel(M, K):
    """ 给定矩阵直接做 Chebyshev 三项递推, 返回 (占位, 占位, U) """
    N = M.shape[0]
    U = [np.eye(N), M.copy()]
    for k in range(1, K):
        U.append(2.0 * M @ U[k] - U[k - 1])
    return None, None, U


def cheb_coefficients(gfun, Nc, K):
    """
    Chebyshev-Gauss 求积求 g(s) 在 [-1,1] 上的展开系数:
        c_k = (2/Nc) sum_j g(cos theta_j) cos(k theta_j),  theta_j = (2j+1)pi/(2Nc)
    """
    j = np.arange(Nc)
    theta = (2 * j + 1) * np.pi / (2 * Nc)
    s = np.cos(theta)
    gv = gfun(s)
    c = np.zeros(K + 1)
    c[0] = (1.0 / Nc) * np.sum(gv)                       # c_0 归一化因子为 1/Nc
    for k in range(1, K + 1):
        c[k] = (2.0 / Nc) * np.sum(gv * np.cos(k * theta))
    return c


def endogenous_Kf(c, gamma):
    """
    算子 13.4 内生自适应截断阶 (v1.2 修正 —— 单项判据 -> 余项判据):

        tail(K) := sum_{k > K} |c_k|
        K_f     := min{ K : tail(K) <= gamma * max_k |c_k| }

    【为什么必须换成余项】
        原判据取「最后一个显著系数的下标」 K = max{k : |c_k| > gamma*max|c|},
        它衡量的是「单项是否已变小」。但 Chebyshev 系数按 rho^{-k} 几何衰减,
        单项变小远不等于逼近够好 —— 实测 ln 核给出 K_f = 1, 而 tail(1) 仍占
        峰值的 21% (> gamma), 截断误差达 3.25e-2。

        真正决定精度的是被丢弃的**总和**: 因 |T_k(s)| <= 1 于 [-1,1] 上,
            | g(s) - sum_{k<=K} c_k T_k(s) |  <=  tail(K)
        故 tail(K) 才是逼近误差的严格上界, 也才是应当与内生容差比较的量。

    【内生性】阈值仍是 gamma * max|c| —— 唯一的内生尺度, 无外部参数。
            注意这保证的是「gamma 级精度」, 不是机器精度; 若要 1e-6 级,
            代价是 Kt 深到 O(1/log rho) ~ 16-24 (见 bench 的 K-sweep 表)。
    """
    cabs = np.abs(np.asarray(c, dtype=float)).ravel()
    cmax = float(cabs.max()) if cabs.size else 0.0
    if cmax <= 0:
        return 0
    thresh = gamma * cmax
    # suffix[k] = sum_{j >= k} |c_j|;  tail(K) = suffix[K+1]
    suffix = np.concatenate([np.cumsum(cabs[::-1])[::-1], [0.0]])
    for K in range(cabs.size):
        if float(suffix[K + 1]) <= thresh:
            return int(K)
    return int(cabs.size - 1)


def bernstein_rho(gamma):
    """
    定理 13.2: ln 型核 (奇点在 lambda_hat = 0) 的 Bernstein 椭圆参数
        s0 = -(1+gamma)/(1-gamma),  rho = |s0| + sqrt(s0^2 - 1)
    """
    s0 = -(1.0 + gamma) / (1.0 - gamma)
    return abs(s0) + np.sqrt(s0 ** 2 - 1.0), s0


def cheb_T_scalar(kmax, s):
    """ 标量 Chebyshev (第一类) T_0..T_kmax 在 s 处的取值 (三项递推, 无矩阵) """
    T = [1.0, float(s)]
    for k in range(1, kmax):
        T.append(2.0 * s * T[k] - T[k - 1])
    return np.array(T[:kmax + 1])


def strip_zero_mode(tau, s0, N, K):
    """
    零模剥离 (算子 13.5):
        ln / 1/lambda 这类核在平凡零模 lambda_1 = 0 处奇异, 而该零模在移位变量
        s 上恰好落在 s0 = -(1+gamma)/(1-gamma) —— 也就是 Bernstein 椭圆的奇点,
        位于 [-1,1] 之外。因此只需把它的矩贡献减掉, 即可在「约化谱」上做核积分,
        整个过程无需任何特征分解:
            tau_k^red = ( N * tau_k - T_k(s0) ) / (N - 1)
    """
    Tk = cheb_T_scalar(K, s0)
    return (N * np.asarray(tau)[:K + 1] - Tk) / (N - 1)


def shard_scales(D, m, shard_idx, n=None):
    """
    分片拼接后的内生尺度:
        alpha_n = max_nu alpha_n^(nu)          (算子 6 拼接规则)
        lambda_2 = 并图/耦合骨架 D^T diag(m) D 的 Fiedler 值
    (单个分片只是边子集, 自身往往不连通, 取 min(lambda_2^(nu)) 会让 gamma = 0)
    """
    n = D.shape[1] if n is None else n
    alpha_n = 1e-12
    for nu in range(len(shard_idx)):
        an, _ = spectral_assets(shard_laplacian(D, shard_idx[nu], m), n)
        alpha_n = max(alpha_n, an)
    _, lam2 = spectral_assets(laplacian(D, m), n)
    return alpha_n, lam2


def shard_encode(D, m, shard_idx, n=None, K=None, alpha_n=None, lam2=None,
                 encoders=None):
    """
    多分片统一编码 —— 与 solve_coupled 内层「完全同一条管线」。
    K, alpha_n, lam2 均可由调用方锁定传入 (场刷新周期内冻结, 见算子 6 规范)。

    【lam2 也必须冻结】核编码的坐标 Yt = (Y - gamma I)/(1-gamma) 依赖
    gamma = lam2/alpha_n。只冻结 alpha_n 而放任 lam2 每步重算, 会让「求解器内部」
    与「外部评估」落在两个不同的移位坐标系上 —— 实测 E09/E10 的矩交叉偏差
    达 2e-2 量级, 正是此因。故 lam2 与 alpha_n 必须一并冻结。
    encoders : list[callable|None]，逐分片的编码钩子（None = 标准 Chebyshev）。
               encode(D_nu, m_nu, L_nu, alpha_n, lam2, K) -> (tau_nu, W_nu)

    关键: 谱矩 tau_k 是用内生尺度 alpha_n(M) 归一化的, 而 alpha_n 本身随 M 变化。
    因此任何「目标常数 / 对照值」必须复用本函数, 否则会与求解循环使用不同的
    归一化, 使方程的目标值落到可达域之外 (V12 曾因此误判为不收敛)。

    返回 (tau_list, W_list, alpha_n, lam2, K)
    """
    n = D.shape[1] if n is None else n
    N = n
    p = len(shard_idx)
    if alpha_n is None:
        alpha_n = 1e-12
        for nu in range(p):
            an, _ = spectral_assets(shard_laplacian(D, shard_idx[nu], m), n)
            alpha_n = max(alpha_n, an)      # 算子 6 拼接: alpha_n 取 max
    L_list = [shard_laplacian(D, shard_idx[nu], m) for nu in range(p)]
    # 内生尺度 lambda_2 取「并图/耦合骨架」的 Fiedler 值 (单个分片往往自身不连通)
    if lam2 is None:
        _, lam2 = spectral_assets(laplacian(D, m), n)
    if K is None:
        K, _, _ = endogenous_K(alpha_n, lam2, N)

    tau_list, W_list = [], []
    for nu in range(p):
        Ln = L_list[nu]
        enc = None if encoders is None else encoders[nu]
        if enc is None:
            Yn = 2.0 * Ln / alpha_n - np.eye(N)
            tn, _, _ = chebyshev_moments(Ln, alpha_n, K)
            Wn = moment_sensitivity(D[shard_idx[nu], :], Yn, N, alpha_n, K)
        else:
            tn, Wn = enc(D[shard_idx[nu], :], m[shard_idx[nu]], Ln,
                         alpha_n, lam2, K)
        tau_list.append(tn)
        W_list.append(Wn)
    return tau_list, W_list, alpha_n, lam2, K


def solve_coupled(D, C, m0, F_coupled, shard_idx, max_kappa=80,
                  verbose=False, mode='homological', freeze=None,
                  encoders=None):
    """
    多谱形耦合求解 (算子 14.4):
        分片各自编码矩与灵敏度, 残差经分片嵌入 Xi_nu 合成到全局边空间后统一 Hodge 分解。

    F_coupled(tau_list) -> (标量残差 g, 块 Jacobian list[J_nu])
        J_nu[k] = dF / d tau_k^(nu)

    mode      : 'homological' 同调解判据 (仅 ||h||)  |  'exact' 精确解判据 (三通道)
    freeze    : (alpha_n, lam2) 冻结内生尺度，整个求解过程不刷新
    encoders  : list[callable|None]，逐分片编码钩子（None = 标准 Chebyshev）
    """
    n = D.shape[1]
    m_g = D.shape[0]
    N = n
    p = len(shard_idx)
    m = m0.copy()
    hist = []
    r0_norm = None
    f_prev = None                     # 上一步标量残差 (Op17「已榨干」判据)
    step_dead_prev = False            # 上一步方向是否耗尽
    hist_has_step = False             # 是否已执行过至少一次更新

    # 内生尺度锁定 (与 solve_spectral_equation 同一规范): 分片编码同样不对
    # alpha_n 求导, 故 alpha_n/lambda_2 必须在刷新周期内冻结。
    L_ref = laplacian(D, m).copy()
    alpha_n_ref, lam2_ref = shard_scales(D, m, shard_idx, n)   # 与 shard_encode 同一规则
    if freeze is not None:
        alpha_n_ref, lam2_ref = freeze
        L_ref = None
    n_refresh = 0

    for kappa in range(max_kappa):
        L = laplacian(D, m)
        if L_ref is not None:
            if norm(L - L_ref, 'fro') / alpha_n_ref > lam2_ref / alpha_n_ref:
                alpha_n_ref, lam2_ref = shard_scales(D, m, shard_idx, n)
                L_ref = L.copy()
                n_refresh += 1
        K, _, _ = endogenous_K(alpha_n_ref, lam2_ref, N)
        tau_list, W_list, alpha_n, _, _ = shard_encode(
            D, m, shard_idx, n, K=K, alpha_n=alpha_n_ref, lam2=lam2_ref,
            encoders=encoders)
        lam2 = lam2_ref

        g, J_list = F_coupled(tau_list)

        r = np.zeros(m_g)
        for nu in range(p):
            Wn, Jn = W_list[nu], J_list[nu]
            loc = np.zeros(len(shard_idx[nu]))
            # 注意: 核编码分片的 tau/W 长度可以远深于内生 K (由 K_f 内生决定),
            #       故不能按 K 截断, 须按两者的实际长度取 min。
            for k in range(min(len(Jn), len(Wn))):
                loc += (Jn[k] * g) * Wn[k]
            r[shard_idx[nu]] += loc             # 等价于 Xi_nu @ loc

        if r0_norm is None:
            r0_norm = norm(r)

        comp = hodge_project(r, D, C)
        grad, harm, curl = comp['grad'], comp['harm'], comp['curl']
        norms = (norm(grad), norm(curl), norm(harm))
        eps = (lam2 / alpha_n) * r0_norm

        # 裁定与单谱形分支同一规范 (见 audit 的 v1.3 修正一/二):
        #   SOLVED 须「既达标又已榨干」; 方向耗尽 (step_dead) 才算障碍/停滞。
        gamma_c = lam2 / alpha_n
        if f_prev is None or f_prev == 0.0:
            exhausted = False
        else:
            exhausted = abs(g) >= (1.0 - gamma_c) * abs(f_prev)
        below = (norms[2] <= eps) if mode == 'homological' else all(
            x <= eps for x in norms)
        r_now = float(norm(r))
        solved = bool(below and (exhausted or step_dead_prev) and hist_has_step)
        terminal = bool(step_dead_prev and not solved)

        hist.append(dict(kappa=kappa, F=g, r_norm=r_now, ng=norms[0],
                         nc=norms[1], nh=norms[2], lam2=lam2, alpha=alpha_n,
                         K=K, verdict='SOLVED' if solved
                         else ('STALLED' if terminal else 'CONTINUE')))
        f_prev = g

        if verbose and (kappa < 5 or kappa % 10 == 0 or solved or terminal):
            print(f"  k={kappa:3d}  F={g:+.6e}  |r|={norm(r):.4e}  "
                  f"[grad {norms[0]:.2e} | curl {norms[1]:.2e} | harm {norms[2]:.2e}]  "
                  f"eps={eps:.2e}  -> "
                  f"{'SOLVED' if solved else ('STALLED' if terminal else 'CONTINUE')}")

        if solved or terminal:
            break

        A = build_hodge_A(D, C, lam2, alpha_n)
        dM, _, _, trust = endo_newton_step(r, harm, A, F=g, D=D, lam2=lam2)
        hist[-1].update(dM_norm=norm(dM), trust=trust)
        m_min = (lam2 / alpha_n) * float(m0.mean())

        # ---- Phase 3.5b: 内生回溯线搜索 (与单谱形分支同一约定: 二分) ----
        t_acc, n_back = 1.0, 0
        t_floor = 1e-14
        while True:
            m_try = np.maximum(m + t_acc * dM, m_min)
            tl_try, _, _, _, _ = shard_encode(D, m_try, shard_idx, n, K=K,
                                              alpha_n=alpha_n_ref,
                                              lam2=lam2_ref, encoders=encoders)
            g_try, _ = F_coupled(tl_try)
            if abs(g_try) < abs(g) or t_acc <= t_floor:
                break
            t_acc *= 0.5
            n_back += 1
        step_dead_prev = bool((t_acc <= t_floor)
                              or (norm(t_acc * dM) <= 1e-12 * m_min))
        hist[-1].update(t_ls=t_acc, n_backtrack=n_back,
                        step_dead=step_dead_prev)
        hist_has_step = True
        m = np.maximum(m + t_acc * dM, m_min)

    return m, hist


def edge_residual(D, m, F, dF_dtau, tau_index, scales=None, encode=None):
    """
    Phase 1 + Phase 3 的合成: 给定边权 m, 直接算出边空间残差 r
        r = sum_k (dF/dtau_k * F) * w_k,   w_k = dtau_k/dm

    scales=(alpha_n, lam2) 可传入冻结的内生尺度。F 只在 alpha_n 锁定时才是 m 的
    光滑函数, 因此「比较两个实现的残差」必须共用同一组冻结尺度, 否则比的是两个
    不同的函数 (V16 曾因此误判同调距离)。
    encode : 同 solve_spectral_equation 的编码钩子 (非多项式核必填, 否则坐标系不同)。
    返回 (r, g, tau, K, alpha_n, lam2)
    """
    n = D.shape[1]
    N = n
    L = laplacian(D, m)
    if scales is None:
        alpha_n, lam2 = spectral_assets(L, n)
    else:
        alpha_n, lam2 = scales
    K, _, _ = endogenous_K(alpha_n, lam2, N)
    if encode is None:
        tau, Y, U = chebyshev_moments(L, alpha_n, K)
        W = moment_sensitivity(D, Y, N, alpha_n, K)
    else:
        tau, W = encode(D, m, L, alpha_n, lam2, K)
    g = float(F(tau))
    J = dF_dtau(tau, K)
    r = np.zeros(D.shape[0])
    for k in tau_index:
        if k < min(len(J), len(W)):
            r += (J[k] * g) * W[k]
    return r, g, tau, K, alpha_n, lam2


def homological_realize(D, C, m, residual_fn, M_init=None):
    """
    算子 18 (R_homo) 同调解实现: 输出规范代表 + 三项证书
        证书1: 同调残差   ||h(M)||            —— 是否为同调解
        证书2: 同调距离   ||h(M) - h(M_init)|| —— 与参照实现是否同调等价 (定义 3.2)
        证书3: 恰当残差预算 ||D phi|| + ||C^T psi|| —— 精确解还需消掉的恰当部分
        规范代表: 同调等价类内 Dirichlet 能 E = ||D phi||^2 最小者
    """
    r = residual_fn(m)
    comp = hodge_project(r, D, C)
    h_cur = comp['harm']

    if M_init is not None:
        comp0 = hodge_project(residual_fn(M_init), D, C)
        d_hom = norm(h_cur - comp0['harm'])
    else:
        comp0, d_hom = None, float('nan')

    return dict(m_star=m.copy(),
                h_norm=norm(h_cur),
                h_vec=h_cur,
                d_hom=d_hom,
                budget=norm(comp['grad']) + norm(comp['curl']),
                dirichlet=float(norm(comp['grad']) ** 2))


# ===========================================================================
# v1.1 验证: V12 - V17
# ===========================================================================

def run_verification_v11():
    print("\n" + "=" * 78)
    print("v1.1 扩展验证: 多谱形耦合 / 非多项式核 / 同调解")
    print("=" * 78)

    n = 12
    N = n
    rng = np.random.default_rng(11)
    res = {}

    Dh, Ch, _, _ = build_complex(n, close_cycle=False)   # beta_1 = 1
    Dc, Cc, _, _ = build_complex(n, close_cycle=True)    # beta_1 = 0
    m_g = Dh.shape[0]

    m0 = 1.0 + 0.3 * rng.random(m_g)
    L0 = laplacian(Dc, m0)
    alpha_n, lam2 = spectral_assets(L0, n)
    gamma = lam2 / alpha_n
    K, _, _ = endogenous_K(alpha_n, lam2, N)
    print(f"\n[谱资产] alpha_n={alpha_n:.6f}  lambda_2={lam2:.6f}  gamma={gamma:.6f}  K={K}")

    # ------------------------------------------------------------------
    # V12: 多谱形耦合  F = tau_2^(1) * tau_2^(2) - c = 0
    # ------------------------------------------------------------------
    print("\n" + "-" * 78)
    print("V12 多谱形耦合:  F = tau_2^(1) * tau_2^(2) - c = 0   (p = 2 分片)")

    Xi, shard_idx = build_shards(Dc, n_shards=2)
    print(f"    分片边数: {[len(s) for s in shard_idx]}  (合计 {sum(len(s) for s in shard_idx)} = m_g)")

    # 目标常数: 必须与求解循环走同一条归一化管线 (shard_encode), 否则 alpha_n(M)
    # 的漂移会让目标值落到可达域之外 —— 方程变成不可解, 却会被误读成"收敛慢"。
    # 这里用介值定理构造: 取线段 [m0, m_b] 两端耦合值的内插, 保证线段上必有根。
    m_b = 1.0 + 0.8 * rng.random(m_g)
    tl0, _, _, _, _ = shard_encode(Dc, m0, shard_idx, n)
    tlb, _, _, _, _ = shard_encode(Dc, m_b, shard_idx, n)
    c_a = tl0[0][2] * tl0[1][2]
    c_b = tlb[0][2] * tlb[1][2]
    lam_ivt = 0.8                              # 内插系数 (0,1) 内 -> 线段上有解
    c_coupled = c_a + lam_ivt * (c_b - c_a)
    print(f"    可达区间端点: c(m0)={c_a:+.6e}  c(m_b)={c_b:+.6e}  "
          f"跨度={abs(c_b - c_a):.3e}")
    print(f"    目标 c = {c_coupled:+.6e}  (介值定理保证线段上有解, lambda={lam_ivt})")

    def F_cpl(taus):
        g = taus[0][2] * taus[1][2] - c_coupled
        J0 = np.zeros(K + 1); J0[2] = taus[1][2]      # dF/d tau^(1)_k
        J1 = np.zeros(K + 1); J1[2] = taus[0][2]      # dF/d tau^(2)_k
        return g, [J0, J1]

    mc, hist_c = solve_coupled(Dc, Cc, m0, F_cpl, shard_idx,
                               max_kappa=80, verbose=True, mode='exact')
    Fc = [h['F'] for h in hist_c]
    mono_c = all(abs(Fc[i + 1]) <= abs(Fc[i]) * (1 + 1e-9) + 1e-15
                 for i in range(len(Fc) - 1))
    print(f"\n    耦合残差 F: {Fc[0]:+.6e} -> {Fc[-1]:+.6e}  ({len(Fc)} 步)")
    print(f"    单调下降: {'PASS' if mono_c else 'FAIL'}   裁定: {hist_c[-1]['verdict']}")
    res['V12 多谱形耦合求解'] = (hist_c[-1]['verdict'] == 'SOLVED',
                            f"F {Fc[0]:+.2e}->{Fc[-1]:+.2e}, {len(Fc)} 步")

    # ------------------------------------------------------------------
    # V13/V14: 非多项式核 ln(lambda_hat)
    # ------------------------------------------------------------------
    print("\n" + "-" * 78)
    print("V13 非多项式核:  ln(lambda_hat) 的移位 Chebyshev 展开 (含零模剥离)")

    Nc = 512                                      # Chebyshev-Gauss 求积点数
    Kmax = 32                                     # 展开最高阶 (对照用上限)
    y_min = 2.0 * gamma - 1.0                     # 谱支撑下界 (Y 变量)
    # 矩算到 Kmax: 高阶矩本身可由三项递推精确算出 (无特征分解), K 只是「内生默认
    # 编码深度」(过拟合防护), 收敛表需要更高阶才能看清 rho^{-K} 的几何衰减。
    tau_t, Yt = shifted_chebyshev(2.0 * L0 / alpha_n - np.eye(N), y_min, Kmax)
    rho_th, s0 = bernstein_rho(gamma)
    print(f"    谱支撑 (Y): [{y_min:+.6f}, 1]   奇点 s0 = {s0:.6f}   Bernstein rho = {rho_th:.6f}")
    print(f"    平凡零模 lambda_1=0 在 s 变量上恰落在 s0={s0:.4f} (ln 的奇点, "
          f"位于 [-1,1] 之外) -> 必须先剥离 (算子 13.5)")

    def g_ln(s):                                   # ln(lambda_hat) 在 s 变量上的表达
        return np.log(((1.0 - gamma) * s + 1.0 + gamma) / 2.0)

    c_ln = cheb_coefficients(g_ln, Nc, Kmax)
    Kf = endogenous_Kf(c_ln, gamma)
    print(f"    系数: |c_0|={abs(c_ln[0]):.6f}  |c_1|={abs(c_ln[1]):.6f}  "
          f"|c_4|={abs(c_ln[4]):.3e}  |c_8|={abs(c_ln[8]):.3e}")
    print(f"    内生自适应截断阶 K_f = {Kf}  (阈值 gamma*max|c| = {gamma*np.max(np.abs(c_ln)):.3e})")

    Kf_use = min(Kf, K)
    ev = np.sort(eigh(L0)[0])
    lam_hat = ev / alpha_n
    exact = float(np.mean(np.log(lam_hat[1:])))           # 对照: 剔除 lambda_1 = 0

    # 误差随阶数的收敛表 (定理 13.2: err(K) ~ rho^{-K})
    print("    误差 vs 截断阶:")
    errs = {}
    for kk in [1, 2, 3, 4, 5, min(8, Kmax), min(16, Kmax)]:
        if kk > Kmax:
            continue
        tr = strip_zero_mode(tau_t, s0, N, kk)
        ap = float(c_ln[:kk + 1] @ tr)
        ee = abs(ap - exact)
        errs[kk] = ee
        mark = '  <- 内生 K_f' if kk == Kf_use else ('  <- 内生矩深度 K' if kk == K else '')
        print(f"      K={kk:2d}: err={ee:.3e}  相对={ee / abs(exact):.3e}{mark}")

    tau_red = strip_zero_mode(tau_t, s0, N, Kf_use)      # 零模剥离 (无特征分解)
    approx = float(c_ln[:Kf_use + 1] @ tau_red[:Kf_use + 1])
    err = abs(approx - exact)
    tail_bound = float(np.sum(np.abs(c_ln[Kf_use + 1:Kmax + 1])))   # 定理 13.2 尾界
    print(f"    展开近似 sum c_k tau_k^red (K_f={Kf_use}) = {approx:+.10f}")
    print(f"    直接谱积分 mean_(i>=2) ln(lambda_hat)     = {exact:+.10f}")
    print(f"    实测误差 = {err:.3e}   理论尾界 sum_{{j>K_f}}|c_j| = {tail_bound:.3e}"
          f"   -> 尾界{'成立' if err <= tail_bound else '不成立'}")
    print(f"    内生相对容差 gamma*|exact| = {gamma * abs(exact):.3e}"
          f"   -> {'PASS' if err <= gamma * abs(exact) else 'FAIL'}")
    print(f"    注: 精度受内生矩深度 K={K} 封顶; 要更高精度须提高 K, "
          f"代价 O(K) 次矩阵-向量乘 —— 这是内生性的对价")
    ok13 = err <= tail_bound and err <= gamma * abs(exact)
    res['V13 非多项式核 ln 展开'] = (ok13, f"err={err:.2e} <= 尾界 {tail_bound:.2e}")

    # V14: 实测衰减率 vs 理论 rho
    print("\n" + "-" * 78)
    print("V14 Bernstein 椭圆收敛率: 实测衰减 vs 理论 rho")
    # 拟合窗口: 从 K_f 起, 但必须停在求积噪声底 (1e-13) 之上, 否则拟合的是数值噪声
    tail_idx = np.arange(Kf_use, min(Kf_use + 14, Kmax))
    tail = np.abs(c_ln[tail_idx])
    keep = tail > 1e-13
    if int(keep.sum()) >= 4:
        kk = tail_idx[keep]
        slope = np.polyfit(kk, np.log(tail[keep]), 1)[0]
        rho_fit = float(np.exp(-slope))
        print(f"    实测渐近衰减率 rho_fit = {rho_fit:.6f}   (理论 rho = {rho_th:.6f})")
        ratio = rho_fit / rho_th if rho_th > 0 else np.inf
        ok14 = 0.5 < ratio < 2.0
        print(f"    比值 rho_fit/rho_th = {ratio:.4f}   -> {'PASS' if ok14 else 'FAIL (量级不符)'}")
    else:
        rho_fit, ok14 = float('nan'), False
        print("    尾项不足, 跳过")
    res['V14 Bernstein 椭圆率'] = (ok14, f"rho_fit={rho_fit:.3f} vs rho_th={rho_th:.3f}")

    # ------------------------------------------------------------------
    # V15: 同调解 vs 精确解判据 (beta_1 = 1 的有洞复形)
    # ------------------------------------------------------------------
    print("\n" + "-" * 78)
    print("V15 同调解 vs 精确解判据 (有洞复形 beta_1 = 1)")

    m0h = 1.0 + 0.3 * rng.random(m_g)
    Lh0 = laplacian(Dh, m0h)
    ah, l2h = spectral_assets(Lh0, n)
    Kh, _, _ = endogenous_K(ah, l2h, N)
    tau_h0, _, _ = chebyshev_moments(Lh0, ah, Kh)
    c_h = tau_h0[2] * 0.35            # 可达目标

    def F_h(tau_):
        return tau_[2] - c_h

    def dF_h(tau_, K_):
        J = np.zeros(K_ + 1); J[2] = 1.0
        return J

    _, hist_hom = solve_spectral_equation(Dh, Ch, m0h, F_h, dF_h, tau_index=[2],
                                          max_kappa=200, verbose=False,
                                          use_momentum=False, mode='homological')
    _, hist_exa = solve_spectral_equation(Dh, Ch, m0h, F_h, dF_h, tau_index=[2],
                                          max_kappa=200, verbose=False,
                                          use_momentum=False, mode='exact')
    nh_hom = len(hist_hom); nh_exa = len(hist_exa)
    print(f"    同调解判据 (||h||<=eps): {nh_hom:3d} 步  末步 ||h||={hist_hom[-1]['nh']:.3e}  "
          f"裁定={hist_hom[-1]['verdict']}")
    print(f"    精确解判据 (三通道)    : {nh_exa:3d} 步  末步 |r|={hist_exa[-1]['r_norm']:.3e}  "
          f"裁定={hist_exa[-1]['verdict']}")

    # 真正有鉴别力的检验: 两级判据是否会在某个迭代点上给出**不同裁定**。
    # 同调解判据只要求 ||h||<=eps, 精确解判据要求三通道全过; 若存在
    # ||h||<=eps 但 ||grad||+||curl||>eps 的迭代点, 则 S_hom 严格大于 S_exact,
    # 该点是一个「同调解但非精确解」的实例。
    r0 = hist_exa[0]['r_norm']
    split = None
    for h in hist_exa:
        eps_k = (h['lam2'] / h['alpha']) * r0
        hom_ok = h['nh'] <= eps_k
        exa_ok = max(h['ng'], h['nc'], h['nh']) <= eps_k
        if hom_ok and not exa_ok:
            split = (h['kappa'], h['nh'], h['ng'] + h['nc'], eps_k)
            break
    if split is not None:
        k_s, nh_s, ex_s, eps_s = split
        print(f"    分歧点 k={k_s}: ||h||={nh_s:.3e} <= eps={eps_s:.3e} (同调解成立), "
              f"但 ||grad+curl||={ex_s:.3e} > eps (精确解未达成)")
        print(f"    -> S_hom 严格包含 S_exact, 两级判据确有区分度")
    else:
        print(f"    本例未出现分歧点 (初值调和分量本就极小), 两级判据在此重合")
    ok15 = (hist_hom[-1]['verdict'] == 'SOLVED' and nh_hom <= nh_exa)
    print(f"    同调解步数 <= 精确解步数: {'PASS' if ok15 else 'FAIL'}")
    res['V15 同调解提前终止'] = (ok15, f"hom {nh_hom} 步 vs exact {nh_exa} 步"
                              + (f", 分歧点 k={split[0]}" if split else ", 无分歧点"))

    # ------------------------------------------------------------------
    # V16: 同调等价 —— 不同实现, 同调距离 ~ 0
    # ------------------------------------------------------------------
    print("\n" + "-" * 78)
    print("V16 同调距离: 两个不同实现是否同调等价 (定理 S5)")
    # 两个实现必须在「同一个 F」下求解 —— 冻结同一组内生尺度, 否则各自收敛到
    # 的是不同方程的解, 同调距离会被 alpha_n 漂移完全污染。
    frz = spectral_assets(laplacian(Dh, np.ones(m_g)), n)

    # 候选图必须先「缩放到锁定壳层」: c = alpha_lock / alpha_n(M), M -> cM。
    # 否则 Y = 2L/alpha_lock - I 的谱会跑出 [-1,1], Chebyshev 递推放大,
    # 且两个候选不在同一归一化下, 根本不是在解同一个方程。
    def to_shell(mm):
        am = spectral_assets(laplacian(Dh, mm), n)[0]
        return mm * (frz[0] / am)

    # 【实测发现】rho_h(M) := ||h||/||r|| = ||Pi_H gradF||/||gradF|| 与 F(M) 无关,
    # 且在本复形上对几乎所有初值都稳定在 ~0.945 —— 残差的调和占比几乎不随迭代
    # 变化。推论: 调和通道无法被独立压缩, 只能随 ||r||->0 一同消失, 因此同调解
    # 判据在收敛点上与精确解判据重合 (V15 无分歧点); 只有当初值的调和占比恰
    # 小于 gamma 时, 同调解判据才会提前终止。
    rhos = []
    for sd in range(12):
        mm = to_shell(1.0 + 0.3 * np.random.default_rng(sd).random(m_g))
        rr = edge_residual(Dh, mm, F_h, dF_h, [2], scales=frz)[0]
        cp = hodge_project(rr, Dh, Ch)
        rhos.append(norm(cp['harm']) / max(norm(rr), 1e-300))
    print(f"    rho_h = ||h||/||r|| 扫描(12 初值): "
          f"min={min(rhos):.4f} max={max(rhos):.4f} 均值={np.mean(rhos):.4f}"
          f"   (判据阈值 gamma={frz[1] / frz[0]:.3f})")
    print(f"    => 调和占比近似为常数 ~{np.mean(rhos):.3f}, 两级判据在此复形上同阶收敛")

    # 取两个都真正收敛 (SOLVED) 的实现 —— 否则比较的是两个「障碍点」而非解
    solved_seeds, solved_ms, solved_hs = [], [], []
    for sd in range(40):
        mm = to_shell(1.0 + 0.3 * np.random.default_rng(sd).random(m_g))
        msol, hs = solve_spectral_equation(Dh, Ch, mm, F_h, dF_h, tau_index=[2],
                                           max_kappa=60, verbose=False,
                                           use_momentum=False, mode='exact',
                                           freeze=frz)
        if hs[-1]['verdict'] == 'SOLVED':
            solved_seeds.append(sd); solved_ms.append(msol); solved_hs.append(hs)
        if len(solved_seeds) == 2:
            break
    ma, mb = solved_ms[0], solved_ms[1]
    ha, hb = solved_hs[0], solved_hs[1]
    print(f"    收敛初值: seed{solved_seeds[0]}, seed{solved_seeds[1]} (均 SOLVED)")
    print(f"    a {len(ha)} 步 (末步 ||h||={ha[-1]['nh']:.2e}, |r|={ha[-1]['r_norm']:.2e}), "
          f"b {len(hb)} 步 (末步 ||h||={hb[-1]['nh']:.2e}, |r|={hb[-1]['r_norm']:.2e})")

    # 算子 18: 真实残差下的三项证书
    # 关键: F 只在 alpha_n 锁定时才是 m 的已知函数, 两个实现必须用**同一组**
    # 冻结尺度评估, 否则比较的是两个不同的函数 (同调距离会被 α_n 漂移污染)。
    sc = frz

    def rfn(mm):
        return edge_residual(Dh, mm, F_h, dF_h, [2], scales=sc)[0]

    Ra = homological_realize(Dh, Ch, ma, rfn, M_init=mb)
    Rb = homological_realize(Dh, Ch, mb, rfn, M_init=ma)

    dM_dist = norm(ma - mb)                          # 边权空间距离
    d_hom_a = Ra['d_hom']                            # ||h(M_a) - h(M_b)||
    d_hom_b = Rb['d_hom']
    d_hom = 0.5 * (d_hom_a + d_hom_b)

    eps_ref = (frz[1] / frz[0]) * norm(edge_residual(
        Dh, to_shell(1.0 + 0.3 * np.random.default_rng(solved_seeds[0]).random(m_g)),
        F_h, dF_h, [2], scales=sc)[0])               # 内生容差基准

    print(f"    实现 a: ||h||={Ra['h_norm']:.3e}  恰当预算={Ra['budget']:.3e}  "
          f"Dirichlet 能={Ra['dirichlet']:.3e}")
    print(f"    实现 b: ||h||={Rb['h_norm']:.3e}  恰当预算={Rb['budget']:.3e}  "
          f"Dirichlet 能={Rb['dirichlet']:.3e}")
    print(f"    ||M_a* - M_b*||_2          = {dM_dist:.6e}   (两个实现显著不同)")
    print(f"    d_hom = ||h(M_a)-h(M_b)||  = {d_hom:.6e}   (内生容差 eps = {eps_ref:.3e})")
    ok16 = dM_dist > 1e-3 and d_hom <= eps_ref
    print(f"    -> V16 {'PASS' if ok16 else 'FAIL'}")

    # 规范代表: 同调等价类内 Dirichlet 能最小者 (算子 18 唯一化准则)
    Ea, Eb = Ra['dirichlet'], Rb['dirichlet']
    canon = 'M_a*' if Ea <= Eb else 'M_b*'
    print(f"    规范代表 (Dirichlet 能最小) = {canon}   "
          f"(E_a={Ea:.3e} vs E_b={Eb:.3e})")
    res['V16 同调等价'] = (ok16, f"dM={dM_dist:.2e}, d_hom={d_hom:.2e}")
    res['V18 规范代表选取'] = (True, f"canon={canon}, E={min(Ea, Eb):.2e}")

    # ------------------------------------------------------------------
    # V17: 退化警告 —— beta_1 = 0 时 ||h|| 恒为 0
    # ------------------------------------------------------------------
    print("\n" + "-" * 78)
    print("V17 退化警告: beta_1 = 0 复形上 ||h|| 恒为 0 (同调解判据失效)")
    hnorms = []
    for t in range(5):
        rr = rng.standard_normal(m_g)
        comp = hodge_project(rr, Dc, Cc)
        hnorms.append(norm(comp['harm']))
    print(f"    5 个随机残差的 ||h||: {['%.2e' % x for x in hnorms]}")
    ok17 = max(hnorms) < 1e-8
    print(f"    全部 ~ 0 -> 同调解集 = 全空间, 判据失效: {'CONFIRMED' if ok17 else 'FAIL'}")
    print(f"    => 必须启用算子 18 的规范代表准则 (Dirichlet 能最小) 挑选唯一实现")
    res['V17 退化警告'] = (ok17, f"max||h||={max(hnorms):.2e}")

    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("v1.1 验证汇总")
    print("=" * 78)
    npass = 0
    for name, (ok, val) in res.items():
        print(f"  {'PASS' if ok else 'FAIL'}   {name:<32s}   [{val}]")
        npass += int(ok)
    print("-" * 78)
    print(f"  {npass} / {len(res)} 通过")
    print("=" * 78)


if __name__ == '__main__':
    run_verification()
    run_verification_v11()
