# sre_spectral_solver.py
import logging
from typing import Tuple, Optional, Dict, Any, List, Callable
import numpy as np
from numpy.linalg import eigh, pinv, norm, matrix_rank

logger = logging.getLogger(__name__)


class SRESpectralSolverSuite:
    """
    SRE 动力学第六层：谱形方程求解层 (Operators 13, 14, 15, 16, 17, 18)
    声明：此模块通过 Chebyshev 矩编码、Hodge 三分量路由、内生拟牛顿反演、
    Hankel 可行性钳制、解分支贝蒂审计与同调解实现，求解谱形方程 F(tau) = 0。
    依赖：numpy（scipy 仅用于验证，核心算子不依赖）。
    """

    def __init__(
        self,
        cg_tol: float = 1e-12,
        cg_maxit: int = 2000,
        hankel_bisect: int = 60,
        theta_endo: float = 1e-9,
        max_kappa: int = 60,
        enable_debug_log: bool = True,
    ):
        """
        初始化谱形方程求解套件参数

        参数:
            cg_tol: float, 共轭梯度法收敛容差
            cg_maxit: int, 共轭梯度法最大迭代次数
            hankel_bisect: int, Hankel 钳制二分回退次数
            theta_endo: float, Hankel 可行性内生阈值
            max_kappa: int, 谱形方程求解最大迭代步数
            enable_debug_log: bool, 是否启用调试日志
        """
        if cg_tol <= 0:
            raise ValueError(f"cg_tol 必须大于 0，当前输入: {cg_tol}")
        if cg_maxit <= 0:
            raise ValueError(f"cg_maxit 必须为正整数，当前输入: {cg_maxit}")
        if hankel_bisect <= 0:
            raise ValueError(f"hankel_bisect 必须为正整数，当前输入: {hankel_bisect}")
        if theta_endo <= 0:
            raise ValueError(f"theta_endo 必须大于 0，当前输入: {theta_endo}")
        if max_kappa <= 0:
            raise ValueError(f"max_kappa 必须为正整数，当前输入: {max_kappa}")

        self.cg_tol = cg_tol
        self.cg_maxit = cg_maxit
        self.hankel_bisect = hankel_bisect
        self.theta_endo = theta_endo
        self.max_kappa = max_kappa
        self.enable_debug_log = enable_debug_log

    def _log_debug(self, msg: str, *args):
        """控制调试日志输出"""
        if self.enable_debug_log:
            logger.debug(msg, *args)

    # =========================================================================
    # 0. 链复形构造与谱资产（辅助工具）
    # =========================================================================
    @staticmethod
    def laplacian(D: np.ndarray, m: np.ndarray) -> np.ndarray:
        """0-阶图拉普拉斯 L = D^T diag(m) D"""
        return D.T @ np.diag(m) @ D

    @staticmethod
    def spectral_assets(L: np.ndarray, n_node: int) -> Tuple[float, float]:
        """
        算子 6 的谱资产 (alpha_n, lambda_2)
            alpha_n = 最大特征值 (谱半径)
            lambda_2 = 第二小特征值 (代数连通度)
        """
        ev = eigh(L)[0]
        alpha_n = float(ev[-1])
        lam2 = float(ev[1]) if n_node > 1 else float(ev[0])
        return alpha_n, max(lam2, 1e-12)

    # =========================================================================
    # 算子 13: E_mom  谱形 Chebyshev 矩编码算子
    # =========================================================================
    @staticmethod
    def chebyshev_basis(Y: np.ndarray, K: int) -> List[np.ndarray]:
        """第一类 Chebyshev: T_0=I, T_1=Y, T_{k+1}=2 Y T_k - T_{k-1}"""
        N = Y.shape[0]
        U = [np.eye(N), Y.copy()]
        for k in range(1, K):
            U.append(2.0 * Y @ U[k] - U[k - 1])
        return U

    @staticmethod
    def chebyshev_second_kind(Y: np.ndarray, K: int) -> List[np.ndarray]:
        """第二类 Chebyshev: U_0=I, U_1=2Y, U_{k+1}=2 Y U_k - U_{k-1}"""
        N = Y.shape[0]
        V = [np.eye(N), 2.0 * Y]
        for k in range(1, K - 1):
            V.append(2.0 * Y @ V[k] - V[k - 1])
        return V[:K]

    def execute_operator_13_chebyshev_moments(
        self, L: np.ndarray, alpha_n: float, K: int
    ) -> Tuple[np.ndarray, np.ndarray, List[np.ndarray]]:
        """
        Op13 主式: tau_k = (1/N) tr( T_k(Y) ),  Y = 2 L / alpha_n - I
        谱支撑被内生钳制在 [-1, 1], 全程三项递推, 无特征分解。

        参数:
            L: np.ndarray, 图拉普拉斯矩阵 (N, N)
            alpha_n: float, 谱半径（算子 6 输出）
            K: int, Chebyshev 截断阶数

        返回 (tau, Y, U):
            tau: np.ndarray, (K+1,) 谱形矩向量
            Y: np.ndarray, (N, N) 归一化拉普拉斯
            U: list[np.ndarray], Chebyshev 多项式矩阵列表
        """
        if not isinstance(L, np.ndarray) or L.ndim != 2 or L.shape[0] != L.shape[1]:
            raise ValueError(f"L 必须为二维方阵，当前形状: {getattr(L, 'shape', None)}")
        if alpha_n <= 0:
            raise ValueError(f"alpha_n 必须大于 0，当前输入: {alpha_n}")
        if K < 1:
            raise ValueError(f"K 必须至少为 1，当前输入: {K}")

        N = L.shape[0]
        Y = 2.0 * L / alpha_n - np.eye(N)
        U = self.chebyshev_basis(Y, K)
        tau = np.array([np.trace(U[k]) / N for k in range(K + 1)])
        self._log_debug("算子 13 执行成功 | K=%d, tau_0=%.6f, tau_2=%.6f", K, float(tau[0]), float(tau[2]))
        return tau, Y, U

    def moment_sensitivity(
        self, D: np.ndarray, Y: np.ndarray, N: int, alpha_n: float, K: int
    ) -> np.ndarray:
        """
        Op13 灵敏度向量 (解析式):
            w_{k,e} = d tau_k / d M_e = (2k / (N * alpha_n)) * d_e^T U_{k-1}(Y) d_e
        """
        V = self.chebyshev_second_kind(Y, K)
        W = np.zeros((K + 1, D.shape[0]))
        for k in range(1, K + 1):
            W[k] = (2.0 * k / (N * alpha_n)) * np.diag(D @ V[k - 1] @ D.T)
        return W

    @staticmethod
    def endogenous_K(alpha_n: float, lam2: float, N: int) -> Tuple[int, int, int]:
        """
        Op13 内生截断阶:
            K = min( ceil(alpha_n / lambda_2),  floor(2 ln(1+N)) )
        """
        K_res = int(np.ceil(alpha_n / lam2))
        K_cap = int(np.floor(2.0 * np.log(1.0 + N)))
        return max(4, min(K_res, K_cap)), K_res, K_cap

    # =========================================================================
    # 算子 14: R_hodge  方程残差同调路由算子
    # =========================================================================
    def execute_operator_14_hodge_project(
        self, r: np.ndarray, D: np.ndarray, C: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """
        Op14 主式: 残差 1-链 r 的 Hodge 三分量正交分解
            r = D phi  +  h  +  C^T psi
            phi = (D^T D)^+ D^T r          (0-阶拉普拉斯伪逆)
            psi = (C C^T)^+ C r            (2-阶拉普拉斯伪逆)
            h   = r - D phi - C^T psi      (调和分量, 属于 H_1)

        参数:
            r: np.ndarray, (m_g,) 残差 1-链
            D: np.ndarray, (m_g, n) 1-阶边界算子 d1
            C: np.ndarray, (f, m_g) 2-阶边界算子 d2

        返回 (dict):
            grad, harm, curl, phi, psi
        """
        if r.ndim != 1:
            raise ValueError(f"r 必须为一维向量，当前形状: {r.shape}")
        if D.ndim != 2 or C.ndim != 2:
            raise ValueError("D 与 C 必须为二维矩阵")
        if D.shape[0] != r.shape[0]:
            raise ValueError(f"D 边维度 ({D.shape[0]}) 与 r 维度 ({r.shape[0]}) 不匹配")

        L0 = D.T @ D
        phi = pinv(L0) @ (D.T @ r)
        psi = pinv(C @ C.T) @ (C @ r) if C.shape[0] > 0 else np.zeros(0)
        grad = D @ phi
        curl = C.T @ psi if C.shape[0] > 0 else np.zeros_like(r)
        h = r - grad - curl

        self._log_debug(
            "算子 14 执行成功 | ||grad||=%.6e, ||harm||=%.6e, ||curl||=%.6e",
            float(norm(grad)), float(norm(h)), float(norm(curl))
        )
        return dict(grad=grad, harm=h, curl=curl, phi=phi, psi=psi)

    # =========================================================================
    # 算子 15: N_endo  内生拟牛顿谱形反演算子
    # =========================================================================
    @staticmethod
    def build_hodge_A(D: np.ndarray, C: np.ndarray, lam2: float, alpha_n: float) -> np.ndarray:
        """
        加权 Hodge 拉普拉斯 (内生 Hessian 代理的正则部分):
            A = lambda_2 * D D^T  +  (lambda_2^2 / alpha_n) * C^T C
        ker(A) = ker(D^T) ∩ ker(C) = H_1
        """
        A = lam2 * (D @ D.T)
        if C.shape[0] > 0:
            A = A + (lam2 ** 2 / alpha_n) * (C.T @ C)
        return A

    def cg_solve(self, A: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, int]:
        """共轭梯度法求 A^dagger b（A 对称半正定, b 须已剔除 ker(A) 分量）"""
        x = np.zeros_like(b)
        r = b - A @ x
        p = r.copy()
        rs = r @ r
        if rs < 1e-30:
            return x, 0
        for it in range(self.cg_maxit):
            Ap = A @ p
            denom = p @ Ap
            if abs(denom) < 1e-300:
                break
            alpha = rs / denom
            x = x + alpha * p
            r = r - alpha * Ap
            rs_new = r @ r
            if np.sqrt(rs_new) < self.cg_tol:
                break
            p = r + (rs_new / rs) * p
            rs = rs_new
        return x, it + 1

    def execute_operator_15_endo_newton_step(
        self,
        g_M: np.ndarray,
        h: np.ndarray,
        A: np.ndarray,
        F: Optional[float] = None,
        D: Optional[np.ndarray] = None,
        lam2: Optional[float] = None,
    ) -> Tuple[np.ndarray, float, int, float]:
        """
        Op15 单行闭式 (内生拟牛顿 + 内生信赖域), 定理 15.1'

            g_tilde = g_M - h                          剔除调和分量
            dM_raw  = - A^+ g_tilde                    方向: 按 Hodge 通道加权
            eta_N   = F^2 / (g_tilde^T A^+ g_tilde)    内生牛顿步长

        内生信赖域 (公设 3): 步长不得跨越半个谱隙。

        参数:
            g_M: np.ndarray, (m_g,) 矩空间梯度
            h: np.ndarray, (m_g,) 调和分量
            A: np.ndarray, (m_g, m_g) 加权 Hodge 拉普拉斯
            F: float, 标量残差（用于内生步长）
            D: np.ndarray, 边界算子（用于信赖域）
            lam2: float, 谱隙（用于信赖域）

        返回 (dM, quad, iters, trust_scale)
        """
        g_tilde = g_M - h
        Ag, iters = self.cg_solve(A, g_tilde)
        quad = float(g_tilde @ Ag)

        if F is None or quad <= 1e-300:
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

        self._log_debug("算子 15 执行成功 | eta=%.6e, trust=%.6e", eta, trust)
        return dM, quad, iters, trust

    # =========================================================================
    # 算子 16: C_hankel  谱形可行性 Hankel 钳制算子
    # =========================================================================
    @staticmethod
    def power_moments(Y: np.ndarray, Kp: int, N: int) -> np.ndarray:
        """幂矩 mu_k = (1/N) tr(Y^k), k = 0..2*Kp+2"""
        P = np.eye(N)
        mu = [1.0]
        for k in range(1, 2 * Kp + 3):
            P = P @ Y
            mu.append(float(np.trace(P)) / N)
        return np.array(mu)

    @staticmethod
    def hankel_pair(mu: np.ndarray, Kp: int) -> Tuple[np.ndarray, np.ndarray]:
        """Hausdorff 矩问题判据 (支撑 [-1,1]): H0[i,j]=mu_{i+j}, H1=H0-shift"""
        idx = np.arange(Kp + 1)
        H0 = mu[idx[:, None] + idx[None, :]]
        H1 = mu[idx[:, None] + idx[None, :]] - mu[idx[:, None] + idx[None, :] + 2]
        return H0, H1

    @staticmethod
    def hankel_feasibility(mu: np.ndarray, Kp: int) -> float:
        """返回 min(min_eig(H0), min_eig(H1)); >= 0 表示可行"""
        H0, H1 = SRESpectralSolverSuite.hankel_pair(mu, Kp)
        return min(float(eigh(H0)[0].min()), float(eigh(H1)[0].min()))

    def execute_operator_16_hankel_clamp(
        self,
        mu_new: np.ndarray,
        mu_ref: np.ndarray,
        Kp: int,
        theta_endo: Optional[float] = None,
    ) -> Tuple[np.ndarray, float, float, float]:
        """
        Op16 两阶段钳制阀:
            柔性通道: 若 mu_new 已满足可行性 (min_eig >= -theta_endo), 直接放行;
            硬拦截  : 沿「mu_ref -> mu_new」的连线做二分回退。

        参数:
            mu_new: np.ndarray, 新矩序列
            mu_ref: np.ndarray, 上一步可行矩
            Kp: int, Hankel 判据阶数
            theta_endo: float, 内生阈值（默认取 __init__ 的 theta_endo）

        返回 (mu_clamped, feas_before, feas_after, t_star)
        """
        theta = theta_endo if theta_endo is not None else self.theta_endo
        feas0 = self.hankel_feasibility(mu_new, Kp)
        if feas0 >= -theta:
            return mu_new.copy(), feas0, feas0, 1.0

        lo, hi = 0.0, 1.0
        for _ in range(self.hankel_bisect):
            mid = 0.5 * (lo + hi)
            if self.hankel_feasibility(mu_ref + mid * (mu_new - mu_ref), Kp) >= -theta:
                lo = mid
            else:
                hi = mid
        mu_c = mu_ref + lo * (mu_new - mu_ref)
        feas_after = self.hankel_feasibility(mu_c, Kp)
        self._log_debug("算子 16 执行成功 | feas: %.3e -> %.3e, t*=%.4f", feas0, feas_after, lo)
        return mu_c, feas0, feas_after, lo

    # =========================================================================
    # 算子 17: A_sol  解分支贝蒂审计与终止裁定算子
    # =========================================================================
    def execute_operator_17_audit(
        self,
        grad: np.ndarray,
        curl: np.ndarray,
        harm: np.ndarray,
        r0_norm: float,
        lam2: float,
        alpha_n: float,
        f_prev: Optional[float] = None,
        f_now: Optional[float] = None,
        step_dead: bool = False,
    ) -> Tuple[str, float, Tuple[float, float, float], Dict[str, Any]]:
        """
        三通道内生收敛判据 (相对, 无量纲):
            gamma    = lambda_2 / alpha_n                可分辨的相对改善因子
            eps_endo = gamma * ||r_0||                   分辨下限
        裁定: 'SOLVED' / 'OBSTRUCTION' / 'STALLED' / 'CONTINUE'

        参数:
            grad, curl, harm: np.ndarray, Hodge 三分量
            r0_norm: float, 初始残差范数
            lam2: float, 谱隙
            alpha_n: float, 谱半径
            f_prev, f_now: float, 上一步/当前标量残差（用于「已榨干」判据）
            step_dead: bool, 方向是否已耗尽

        返回 (verdict, eps, (ng, nc, nh), info)
        """
        gamma = lam2 / alpha_n
        eps = gamma * r0_norm
        ng, nc, nh = float(norm(grad)), float(norm(curl)), float(norm(harm))
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
        self._log_debug("算子 17 执行成功 | verdict=%s, eps=%.6e", verdict, eps)
        return verdict, eps, (ng, nc, nh), info

    # =========================================================================
    # 算子 18: R_homo  同调解实现算子
    # =========================================================================
    def execute_operator_18_homological_realize(
        self,
        D: np.ndarray,
        C: np.ndarray,
        m: np.ndarray,
        residual_fn: Callable[[np.ndarray], np.ndarray],
        M_init: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        算子 18 (R_homo) 同调解实现: 输出规范代表 + 三项证书
            证书1: 同调残差   ||h(M)||            —— 是否为同调解
            证书2: 同调距离   ||h(M) - h(M_init)|| —— 与参照实现是否同调等价
            证书3: 恰当残差预算 ||D phi|| + ||C^T psi|| —— 精确解还需消掉的恰当部分
            规范代表: 同调等价类内 Dirichlet 能 E = ||D phi||^2 最小者

        参数:
            D: np.ndarray, (m_g, n) 1-阶边界算子
            C: np.ndarray, (f, m_g) 2-阶边界算子
            m: np.ndarray, (m_g,) 边权向量
            residual_fn: callable, 残差函数 residual_fn(m) -> r
            M_init: np.ndarray, 参照实现的边权向量

        返回 (dict):
            m_star, h_norm, h_vec, d_hom, budget, dirichlet
        """
        r = residual_fn(m)
        comp = self.execute_operator_14_hodge_project(r, D, C)
        h_cur = comp['harm']

        if M_init is not None:
            comp0 = self.execute_operator_14_hodge_project(residual_fn(M_init), D, C)
            d_hom = float(norm(h_cur - comp0['harm']))
        else:
            d_hom = float('nan')

        result = dict(
            m_star=m.copy(),
            h_norm=float(norm(h_cur)),
            h_vec=h_cur,
            d_hom=d_hom,
            budget=float(norm(comp['grad']) + norm(comp['curl'])),
            dirichlet=float(norm(comp['grad']) ** 2),
        )
        self._log_debug("算子 18 执行成功 | ||h||=%.6e, d_hom=%.6e", result['h_norm'], result['d_hom'])
        return result

    # =========================================================================
    # 主求解器: 谱形方程求解内环 (Phase 1 -> 3 -> 3.5 -> 4)
    # =========================================================================
    def _eval_F(self, D, m, F, alpha_n, lam2, K, encode=None):
        """在给定边权处求标量残差 F(tau(m))"""
        L = self.laplacian(D, m)
        if encode is None:
            tau, _, _ = self.execute_operator_13_chebyshev_moments(L, alpha_n, K)
        else:
            tau, _ = encode(D, m, L, alpha_n, lam2, K)
        return float(F(tau))

    def solve_spectral_equation(
        self,
        D: np.ndarray,
        C: np.ndarray,
        m0: np.ndarray,
        F: Callable,
        dF_dtau: Callable,
        tau_index: List[int],
        max_kappa: Optional[int] = None,
        verbose: bool = True,
        use_momentum: bool = False,
        mode: str = 'exact',
        freeze: Optional[Tuple[float, float]] = None,
        encode: Optional[Callable] = None,
    ) -> Tuple[np.ndarray, List[Dict]]:
        """
        求解谱形方程 F(tau) = 0, 未知量为边权向量 m。

        参数:
            D: np.ndarray, (m_g, n) 1-阶边界算子
            C: np.ndarray, (f, m_g) 2-阶边界算子
            m0: np.ndarray, (m_g,) 初始边权
            F: callable, 标量残差函数 F(tau)
            dF_dtau: callable, 矩空间 Jacobian dF/dtau_k
            tau_index: list[int], F 依赖的矩下标
            max_kappa: int, 最大迭代步数
            mode: str, 'exact' 或 'homological'
            freeze: tuple, (alpha_n, lam2) 冻结内生尺度
            encode: callable, 可选编码钩子

        返回 (m, hist)
        """
        max_k = max_kappa if max_kappa is not None else self.max_kappa
        n = D.shape[1]
        m_g = D.shape[0]
        N = n
        m = m0.copy()

        hist = []
        r0_norm = None
        f_prev = None
        step_dead_prev = False
        v_mom = np.zeros(m_g)

        if freeze is not None:
            alpha_n, lam2 = freeze
            L_ref = None
        else:
            L = self.laplacian(D, m)
            alpha_n, lam2 = self.spectral_assets(L, n)
            L_ref = L.copy()

        for kappa in range(max_k):
            L = self.laplacian(D, m)
            if L_ref is not None:
                drift = norm(L - L_ref, 'fro') / alpha_n
                if drift > lam2 / alpha_n:
                    alpha_n, lam2 = self.spectral_assets(L, n)
                    L_ref = L.copy()
            K, _, _ = self.endogenous_K(alpha_n, lam2, N)

            # Phase 1: Op13
            if encode is None:
                tau, Y, U = self.execute_operator_13_chebyshev_moments(L, alpha_n, K)
                W = self.moment_sensitivity(D, Y, N, alpha_n, K)
            else:
                tau, W = encode(D, m, L, alpha_n, lam2, K)

            # Phase 3: Op14
            g = float(F(tau))
            J = dF_dtau(tau, K)
            r = np.zeros(m_g)
            for k in tau_index:
                if k < min(len(J), len(W)):
                    r += (J[k] * g) * W[k]

            if r0_norm is None:
                r0_norm = norm(r)

            comp = self.execute_operator_14_hodge_project(r, D, C)
            grad, harm, curl = comp['grad'], comp['harm'], comp['curl']

            # Phase 4: Op17
            verdict, eps, norms, ainfo = self.execute_operator_17_audit(
                grad, curl, harm, r0_norm, lam2, alpha_n,
                f_prev=f_prev, f_now=g, step_dead=step_dead_prev)
            f_prev = g

            if mode == 'homological':
                if norms[2] <= eps and (ainfo['exhausted'] or ainfo['step_dead']):
                    verdict = 'SOLVED'
                elif norms[2] <= eps:
                    verdict = 'CONTINUE'

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

            # Phase 3.5: Op15
            A = self.build_hodge_A(D, C, lam2, alpha_n)
            dM, quad, iters, trust = self.execute_operator_15_endo_newton_step(
                r, harm, A, F=g, D=D, lam2=lam2)
            hist[-1].update(dM_norm=norm(dM), quad=quad, trust=trust,
                            eta=(float(g) ** 2 / quad) if quad > 1e-300 else 0.0,
                            cg_iters=iters)

            if use_momentum:
                beta_mom = 1.0 - lam2 / alpha_n
                v_mom = beta_mom * v_mom + dM
                step = v_mom
            else:
                step = dM

            m_min = (lam2 / alpha_n) * float(m0.mean())

            # 内生回溯线搜索
            t_acc, n_back = 1.0, 0
            t_floor = 1e-14
            while True:
                m_try = np.maximum(m + t_acc * step, m_min)
                g_try = self._eval_F(D, m_try, F, alpha_n, lam2, K, encode)
                if abs(g_try) < abs(g) or t_acc <= t_floor:
                    break
                t_acc *= 0.5
                n_back += 1
            step_dead = (t_acc <= t_floor) or (norm(t_acc * step) <= 1e-12 * m_min)
            hist[-1].update(t_ls=t_acc, n_backtrack=n_back, step_dead=bool(step_dead))
            step_dead_prev = step_dead
            m = np.maximum(m + t_acc * step, m_min)

        return m, hist
