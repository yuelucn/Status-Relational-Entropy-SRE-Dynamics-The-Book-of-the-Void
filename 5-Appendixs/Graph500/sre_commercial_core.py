# sre_commercial_core.py
import logging
from typing import Tuple, Optional
import numpy as np
from scipy.special import expit
from scipy.sparse.linalg import eigsh

logger = logging.getLogger(__name__)


class SRECommercialCoreSuite:
    """
    SRE 动力学第三阶段：商业核心防御与拓扑场闭合工具类 (Operators 7, 8, 9, 10)
    声明：此模块严格对接闭盒外部接口边界，内置分布式无锁多 Actor 收敛硬核异常校验。
    """
    def __init__(
        self,
        num_local_edges: int = 25,
        delta_flt: float = 1e-16,
        k0_horizon: int = 30,
        lambda_base: float = 0.5,
        smooth_alpha: float = 0.25,
        exp_clip_min: float = -500.0,
        exp_clip_max: float = 500.0,
        eig_null_tol: float = 1e-5,
        gamma_flow: float = 0.1,
        p_mu_scale: float = 1.2,
        # 硬编码常数提取配置
        op7_tanh_coeff: float = 0.5,
        op7_grad_coeff: float = 0.1,
        op8_ed_scale1: float = 1.2,
        op8_ed_scale2: float = 0.1,
        # 算子 9 低秩配置与收敛容差配置
        low_rank_dim_threshold: int = 100,
        low_rank_k_evals: int = 20,
        atol_convergence: float = 1e-12,
        enable_debug_log: bool = True
    ):
        """
        初始化 SRE 商业核心套件参数，并进行全量参数合法性校验
        """
        if num_local_edges <= 0:
            raise ValueError(f"num_local_edges 必须为正整数，当前输入: {num_local_edges}")
        if k0_horizon <= 0:
            raise ValueError(f"k0_horizon 必须为正整数，当前输入: {k0_horizon}")
        if num_local_edges > k0_horizon:
            raise ValueError(
                f"严重冲突：局域边数 num_local_edges ({num_local_edges}) 超过局域防火墙视界上限 K0 ({k0_horizon})！"
            )
        if delta_flt <= 0:
            raise ValueError(f"delta_flt 必须大于 0，当前输入: {delta_flt}")
        if lambda_base <= 0:
            raise ValueError(f"lambda_base 必须大于 0，当前输入: {lambda_base}")
        if exp_clip_min >= exp_clip_max:
            raise ValueError(f"截断下限 exp_clip_min ({exp_clip_min}) 必须小于截断上限 exp_clip_max ({exp_clip_max})")
        if low_rank_dim_threshold <= 0 or low_rank_k_evals <= 0:
            raise ValueError("low_rank_dim_threshold 与 low_rank_k_evals 必须为正整数")

        self.Mk = num_local_edges
        self.K0 = k0_horizon
        self.delta_flt = delta_flt
        self.omega_th = 1.0 - delta_flt

        # 常数与权重参数化
        self.lambda_base = lambda_base
        self.smooth_alpha = smooth_alpha
        self.exp_clip_min = exp_clip_min
        self.exp_clip_max = exp_clip_max
        self.eig_null_tol = eig_null_tol
        self.gamma_flow = gamma_flow
        self.p_mu_scale = p_mu_scale

        # 算子 7 & 8 硬编码提取
        self.op7_tanh_coeff = op7_tanh_coeff
        self.op7_grad_coeff = op7_grad_coeff
        self.op8_ed_scale1 = op8_ed_scale1
        self.op8_ed_scale2 = op8_ed_scale2

        # 低秩与容差配置
        self.low_rank_dim_threshold = low_rank_dim_threshold
        self.low_rank_k_evals = low_rank_k_evals
        self.atol_convergence = atol_convergence
        self.enable_debug_log = enable_debug_log

    def _log_debug(self, msg: str, *args):
        """仅在 enable_debug_log 为 True 时输出调试日志"""
        if self.enable_debug_log:
            logger.debug(msg, *args)

    # =========================================================================
    # 算子 7: 伴随滤波器锁定与辛结构对偶均衡算子 (O_lock)
    # =========================================================================
    def evaluate_operator_7_potential(
        self, 
        B_co: np.ndarray, 
        E_s: np.ndarray,
        cached_BcoT_Bco: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        显式计算严格凸的局部 SRE 能量势函数梯度与核空间零通量对流场

        参数:
            B_co: np.ndarray, 形状为 (M, Mk)，上同调回路生成矩阵
            E_s: np.ndarray, 形状为 (Mk,)，1-链传导误差向量
            cached_BcoT_Bco: Optional[np.ndarray], 预计算缓存的 (B_co.T @ B_co)

        返回:
            grad_E: np.ndarray, 形状为 (Mk,)，能量势函数梯度
            B_half: np.ndarray, 形状为 (M,)，对偶回路空间向量
        """
        if B_co.ndim != 2:
            raise ValueError(f"B_co 维度必须为 2，当前形状: {B_co.shape}")
        if E_s.ndim != 1:
            raise ValueError(f"E_s 维度必须为 1，当前形状: {E_s.shape}")
        
        M, Mk = B_co.shape
        if Mk != self.Mk or E_s.shape[0] != self.Mk:
            raise ValueError(
                f"张量 shape 不匹配: B_co 边维度 ({Mk}) 与 E_s 维度 ({E_s.shape[0]}) 必须等于 Mk ({self.Mk})"
            )

        if cached_BcoT_Bco is not None:
            if cached_BcoT_Bco.shape != (Mk, Mk):
                raise ValueError(
                    f"缓存矩阵 cached_BcoT_Bco 形状异常: 期望 ({Mk}, {Mk})，实际 {cached_BcoT_Bco.shape}"
                )
            BcoT_Bco = cached_BcoT_Bco
        else:
            BcoT_Bco = B_co.T @ B_co

        grad_E = BcoT_Bco @ E_s + np.tanh(E_s)
        loop_flux = B_co @ E_s
        B_half = self.op7_tanh_coeff * np.tanh(loop_flux) + self.op7_grad_coeff * (B_co @ grad_E)

        self._log_debug(
            "算子 7 执行成功 | grad_E L2范数: %.6e, B_half L2范数: %.6e", 
            float(np.linalg.norm(grad_E)), float(np.linalg.norm(B_half))
        )

        return grad_E, B_half

    # =========================================================================
    # 算子 8: 局部锁免代数阀平衡算子 (O_valve)
    # =========================================================================
    def execute_operator_8_valve_flow(
        self, 
        E_s: np.ndarray, 
        B_half: np.ndarray, 
        B_co: np.ndarray, 
        V_write: np.ndarray, 
        lambda_2: Optional[float] = None, 
        alpha_smooth: Optional[float] = None
    ) -> Tuple[np.ndarray, float]:
        """
        废除全局互斥锁，将高频线程冲突损失完美转化为切向对流雅可比流

        参数:
            E_s: np.ndarray, 形状为 (Mk,)
            B_half: np.ndarray, 形状为 (M,) 或 (Mk,)
            B_co: np.ndarray, 形状为 (M, Mk)
            V_write: np.ndarray, 形状为 (Mk, Mk)
            lambda_2: Optional[float], 代数松弛因子
            alpha_smooth: Optional[float], 平滑扩散系数

        返回:
            Phi_valve: np.ndarray, 形状为 (Mk, Mk)，阀控通量散度张量
            delta_Pi_valve: float, 单步变分梯度增量 (必须 <= 0)
        """
        if self.Mk > self.K0:
            raise ValueError(f"严重冲突：违反局域防火墙视界边际饱和上限！Mk ({self.Mk}) > K0 ({self.K0})")

        lambda_eff = lambda_2 if lambda_2 is not None else self.lambda_base
        alpha_eff = alpha_smooth if alpha_smooth is not None else self.smooth_alpha

        if E_s.ndim != 1 or E_s.shape[0] != self.Mk:
            raise ValueError(f"E_s 形状异常: 期望 ({self.Mk},)，实际 {E_s.shape}")
        if B_co.ndim != 2 or B_co.shape[1] != self.Mk:
            raise ValueError(f"B_co 形状异常: 期望 (*, {self.Mk})，实际 {B_co.shape}")
        if V_write.shape != (self.Mk, self.Mk):
            raise ValueError(f"V_write 形状异常: 期望 ({self.Mk}, {self.Mk})，实际 {V_write.shape}")
        
        M = B_co.shape[0]
        if B_half.ndim != 1 or (B_half.shape[0] != M and B_half.shape[0] != self.Mk):
            raise ValueError(f"B_half 形状异常: 期望 ({M},) 或 ({self.Mk},)，实际 {B_half.shape}")

        total_trace = np.trace(V_write)
        norm_E_sq = np.dot(E_s, E_s)
        
        # 替换分母判断逻辑为 max(..., delta_flt) 最小值截断
        denom = max(lambda_eff * norm_E_sq, self.delta_flt)

        E_D = lambda_eff * norm_E_sq * (self.op8_ed_scale1 + self.op8_ed_scale2 * np.sin(np.sum(E_s)))
        exponent = np.clip(- E_D / denom, self.exp_clip_min, self.exp_clip_max)
        attenuation_factor = np.exp(exponent)
        
        mu_trace = np.abs(np.diagonal(V_write)) * total_trace * attenuation_factor
        mu_trace = np.clip(mu_trace, 0.0, 1e8)

        if B_half.shape[0] == M:
            loop_flux_term = B_co.T @ B_half
        else:
            loop_flux_term = B_half

        outer_prod = np.outer(loop_flux_term, loop_flux_term)
        projection_component = np.sum(mu_trace) * outer_prod
        Phi_valve = projection_component + alpha_eff * V_write

        Pi_valve_s = np.sum(Phi_valve * V_write)
        delta_V_write = - self.gamma_flow * (mu_trace[:, None] * V_write)
        V_write_next = V_write + delta_V_write

        Phi_valve_next = projection_component + alpha_eff * V_write_next
        Pi_valve_next = np.sum(Phi_valve_next * V_write_next)
        delta_Pi_valve = float(Pi_valve_next - Pi_valve_s)

        # 变分负定判定：使用配置的 atol_convergence 容差
        if delta_Pi_valve > 0.0 and not np.isclose(delta_Pi_valve, 0.0, atol=self.atol_convergence):
            raise ValueError(
                f"致命违背：局部代数阀并发流未能落入严格负定收敛子空间！delta_Pi_valve = {delta_Pi_valve:.8e} > 0"
            )

        self._log_debug(
            "算子 8 执行成功 | mu_trace 均值: %.6e, Phi_valve 范数: %.6e, delta_Pi_valve: %.6e",
            float(np.mean(mu_trace)), float(np.linalg.norm(Phi_valve)), delta_Pi_valve
        )

        return Phi_valve, delta_Pi_valve

    # =========================================================================
    # 算子 9: 双阶平滑贝蒂数同步缝合算子 (O_stitch_dual)
    # =========================================================================
    def execute_operator_9_stitching(
        self, 
        del_2: np.ndarray, 
        delta_1: np.ndarray, 
        Nf: int, 
        lambda_2: Optional[float] = None,
        use_low_rank_fallback: bool = True
    ) -> np.ndarray:
        """
        提取 3 阶局域拉普拉斯算子同调零空间，构筑双阶平滑缝合矩阵 S_dual

        参数:
            del_2: np.ndarray, 形状为 (|E|, Nf)
            delta_1: np.ndarray, 形状为 (Nf, |E|)
            Nf: int, 2-阶面空间维数 |F|
            lambda_2: Optional[float], 谱正则化底
            use_low_rank_fallback: bool, 是否在高维场景启用低秩截断加速

        返回:
            S_dual: np.ndarray, 形状为 (Nf, Nf)，双阶平滑缝合矩阵
        """
        lambda_eff = lambda_2 if lambda_2 is not None else self.lambda_base
        if lambda_eff <= 0:
            raise ValueError(f"正则化参数 lambda_2 必须大于 0，当前为: {lambda_eff}")

        if del_2.ndim != 2:
            raise ValueError(f"del_2 维度必须为 2，当前形状: {del_2.shape}")
        if delta_1.ndim != 2:
            raise ValueError(f"delta_1 维度必须为 2，当前形状: {delta_1.shape}")
        if del_2.shape[1] != Nf or delta_1.shape[0] != Nf:
            raise ValueError(
                f"张量 shape 不匹配: del_2.shape[1] ({del_2.shape[1]}) 与 delta_1.shape[0] ({delta_1.shape[0]}) 必须等于 Nf ({Nf})"
            )

        # 重用预计算变量与单位阵
        lam2_sq = lambda_eff ** 2
        inv_lambda_sq = 1.0 / lam2_sq
        I_f = np.eye(Nf)

        L_3_pure = self.p_mu_scale * (del_2.T @ del_2 + delta_1 @ delta_1.T)
        L_3 = L_3_pure + lam2_sq * I_f

        # 低秩近似降级分支与特征值求解
        if use_low_rank_fallback and Nf > self.low_rank_dim_threshold:
            k_evals = min(Nf - 1, self.low_rank_k_evals)
            eigenvalues, eigenvectors = eigsh(L_3, k=k_evals, which='SA')
        else:
            eigenvalues, eigenvectors = np.linalg.eigh(L_3)

        null_threshold = lam2_sq + self.eig_null_tol
        null_mask = eigenvalues < null_threshold
        V_null = eigenvectors[:, null_mask]

        if V_null.size > 0:
            null_lambdas = eigenvalues[null_mask]
            # 最小阈值截断除零保护
            null_lambdas_safe = np.maximum(null_lambdas, self.delta_flt)
            core_inv_diag = 1.0 / null_lambdas_safe
            
            V_core_inv = V_null * core_inv_diag
            S_dual = V_core_inv @ V_null.T + inv_lambda_sq * (I_f - V_null @ V_null.T)
        else:
            S_dual = inv_lambda_sq * I_f

        # 结果误差/有效性校验
        if np.isnan(S_dual).any() or np.isinf(S_dual).any():
            raise ValueError("算子 9 结算输出出现 nan 或 inf 特异点！")

        self._log_debug(
            "算子 9 执行成功 | Nf: %d, 提取零空间维数: %d, S_dual 迹: %.6e",
            Nf, V_null.shape[1] if V_null.size > 0 else 0, float(np.trace(S_dual))
        )

        return S_dual

    # =========================================================================
    # 算子 10: 抢占式同调随机剪枝算子 (O_gate_batch)
    # =========================================================================
    def execute_operator_10_firewall(
        self, 
        u: int, 
        v_f: int, 
        L_plus: np.ndarray, 
        is_bridge: bool = False
    ) -> Tuple[float, int, float]:
        """
        依据内源有效拓扑阻抗进行因果安全拦截。

        参数:
            u: int, 节点 u 的索引
            v_f: int, 前沿节点 v_f 的索引
            L_plus: np.ndarray, 形状为 (N_nodes, N_nodes)，图拉普拉斯 Moore-Penrose 伪逆矩阵
            is_bridge: bool, 是否属于割裂桥接边 (默认 False)

        返回:
            z_eff: float, 内源有效拓扑阻抗 [0, 1]
            action_gate: int, 1 表示强电平硬拦截导通，0 表示柔性剪枝域
            p_conduction: float, 导通概率 [0, 1]
        """
        if L_plus.ndim != 2 or L_plus.shape[0] != L_plus.shape[1]:
            raise ValueError(f"L_plus 必须为二维方阵，当前形状: {L_plus.shape}")

        N_nodes = L_plus.shape[0]
        if u < 0 or u >= N_nodes:
            raise ValueError(f"节点索引 u ({u}) 越界: 有效范围 [0, {N_nodes - 1}]")
        if v_f < 0 or v_f >= N_nodes:
            raise ValueError(f"节点索引 v_f ({v_f}) 越界: 有效范围 [0, {N_nodes - 1}]")

        if is_bridge:
            z_eff = 1.0
        else:
            z_eff_val = L_plus[u, u] + L_plus[v_f, v_f] - 2.0 * L_plus[u, v_f]
            z_eff = float(np.clip(z_eff_val, 0.0, 1.0))

        if z_eff >= self.omega_th:
            action_gate = 1
            p_conduction = 1.0
        else:
            action_gate = 0
            numerator = 1.5 * z_eff
            # 用 max(..., self.delta_flt) 进行最小值截断防除零
            denominator = max(1.0 - z_eff, self.delta_flt)

            exponent_raw = 2.0 * (numerator / denominator)
            exponent = np.clip(exponent_raw, self.exp_clip_min, self.exp_clip_max)
            p_conduction = float(expit(exponent))

        self._log_debug(
            "算子 10 执行成功 | (u=%d, v_f=%d), z_eff: %.6f, action_gate: %d, p_conduction: %.6f",
            u, v_f, z_eff, action_gate, p_conduction
        )

        return z_eff, action_gate, p_conduction