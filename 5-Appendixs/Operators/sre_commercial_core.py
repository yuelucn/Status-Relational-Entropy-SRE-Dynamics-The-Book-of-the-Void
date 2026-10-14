# sre_commercial_core.py
import numpy as np
from scipy.linalg import eigh
from scipy.special import expit
from typing import Tuple

class SRECommercialCoreSuite:
    """
    SRE 动力学第三阶段：商业核心防御与拓扑场闭合工具类 (Operators 7, 8, 9, 10)
    声明：此模块严格对接闭盒外部接口边界，内置分布式无锁多 Actor 收敛硬核断言
    """
    def __init__(self, num_local_edges: int = 25, delta_flt: float = 1e-16):
        self.Mk = num_local_edges
        self.K0 = 30  # 局域防火墙最大饱和视界 N_K <= K_0
        self.delta_flt = delta_flt
        self.omega_th = 1.0 - delta_flt # 骨折拓扑阻抗临界硬阈值

    # =========================================================================
    # 算子 7: 伴随滤波器锁定与辛结构对偶均衡算子 (O_lock)
    # =========================================================================
    @staticmethod
    def evaluate_operator_7_potential(B_co: np.ndarray, E_s: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """显式计算严格凸的局部 SRE 能量势函数梯度与核空间零通量对流场"""
        grad_E = (B_co.T @ B_co) @ E_s + np.tanh(E_s)
        # 对偶均衡流 B_{s+1/2} 显式代数松弛
        loop_flux = B_co @ E_s
        B_half = B_co.T @ (0.5 * np.tanh(loop_flux)) + 0.1 * grad_E
        return grad_E, B_half

    # =========================================================================
    # 算子 8: 局部锁免代数阀平衡算子 (O_valve)
    # =========================================================================
    def execute_operator_8_valve_flow(self, E_s: np.ndarray, B_half: np.ndarray, 
                                      B_co: np.ndarray, V_write: np.ndarray, 
                                      lambda_2: float = 0.5, alpha_smooth: float = 0.25) -> Tuple[np.ndarray, float]:
        """
        废除全局互斥锁，将高频线程冲突损失完美转化为切向对流雅可比流
        返回 阀控通量散度张量 Phi_valve 与 单步变分梯度增量 Delta_Pi
        """
        assert self.Mk <= self.K0, "严重冲突：违反局域防火墙视界边际饱和上限！"
        
        # 1. 计算本地微迹校正微算子 mu_trace
        total_trace = np.trace(V_write)
        norm_E_sq = np.sum(E_s ** 2)
        E_D = lambda_2 * norm_E_sq * (1.2 + 0.1 * np.sin(np.sum(E_s)))
        attenuation_factor = np.exp(- E_D / (lambda_2 * norm_E_sq + 1e-12))
        mu_trace = np.abs(np.diag(V_write)) * total_trace * attenuation_factor
        
        # 2. 意：使用 np.outer 规避一维数组矩阵乘法退化，确保重构出 (Mk, Mk) 张量
        loop_flux_term = B_co.T @ B_half
        outer_prod = np.outer(loop_flux_term, loop_flux_term)
        
        projection_component = np.zeros((self.Mk, self.Mk))
        for i in range(self.Mk):
            projection_component += mu_trace[i] * outer_prod
        Phi_valve = projection_component + alpha_smooth * V_write
        
        # 3. 结算一阶变分流微分单调响应
        Pi_valve_s = np.trace(Phi_valve.T @ V_write)
        D_mu = np.diag(mu_trace)
        delta_V_write = - 0.1 * D_mu @ V_write  # gamma_flow = 0.1
        V_write_next = V_write + delta_V_write
        
        # 在更新后的表面重新外推重构并结算变分差分
        Phi_valve_next = projection_component + alpha_smooth * V_write_next
        Pi_valve_next = np.trace(Phi_valve_next.T @ V_write_next)
        delta_Pi_valve = Pi_valve_next - Pi_valve_s
        
        # 严格执行非正判定断言，防死锁防火墙失效
        assert delta_Pi_valve <= 0, "致命违背：局部代数阀并发流未能落入严格负定收敛子空间！"
        return Phi_valve, delta_Pi_valve

    # =========================================================================
    # 算子 9: 双阶平滑贝蒂数同步缝合算子 (O_stitch_dual)
    # =========================================================================
    @staticmethod
    def execute_operator_9_stitching(del_2: np.ndarray, delta_1: np.ndarray, 
                                     Nf: int, lambda_2: float = 0.6) -> np.ndarray:
        """提取3阶局域拉普拉斯算子同调零空间，构筑双阶平滑缝合矩阵 S_dual"""
        # 【物理维度纠偏】
        # del_2 形状为 (|E|, |F|) = (3, 2)
        # delta_1 形状为 (|F|, |E|) = (2, 3)
        
        # M_omega 作用于 2-阶面空间 (C_2)，维数对应 del_2.shape[1] 即 |F| = 2
        M_omega = np.eye(del_2.shape[1]) 
        
        # P_mu 作用于 1-阶边空间 (C_1)，维数对应 del_2.shape[0] 即 |E| = 3
        P_mu = np.eye(del_2.shape[0]) * 1.2
        
        # 完备重构 3-阶局域拉普拉斯算子 
        # term_1 = (2, 3) @ (3, 3) @ (3, 2) -> (2, 2)
        # term_2 = (2, 3) @ (3, 3) @ (3, 2) -> (2, 2)
        L_3_pure = del_2.T @ P_mu @ del_2 + delta_1 @ P_mu @ delta_1.T
        L_3 = L_3_pure + (lambda_2 ** 2) * np.eye(Nf)
        
        eigenvalues, eigenvectors = np.linalg.eigh(L_3)
        null_mask = eigenvalues < (lambda_2**2 + 1e-5)
        V_null = eigenvectors[:, null_mask]
        
        I_f = np.eye(Nf)
        if V_null.size > 0:
            core_inv = np.linalg.inv(V_null.T @ L_3 @ V_null)
            S_dual = V_null @ core_inv @ V_null.T + (1.0 / (lambda_2 ** 2)) * (I_f - V_null @ V_null.T)
        else:
            S_dual = (1.0 / (lambda_2 ** 2)) * I_f
        return S_dual

    # =========================================================================
    # 算子 10: 抢占式同调随机剪枝算子 (O_gate_batch)
    # =========================================================================
    def execute_operator_10_firewall(self, u: int, v_f: int, L_plus: np.ndarray, 
                                     is_bridge: bool = False) -> Tuple[float, int, float]:
        """
        依据内源有效拓扑阻抗进行因果安全拦截。
        若属于高危割裂桥接边则触发刚性同调豁免 (chi=1)，保全全局特征谱隙。
        """
        if is_bridge:
            z_eff = 1.0
        else:
            z_eff_val = L_plus[u, u] + L_plus[v_f, v_f] - 2.0 * L_plus[u, v_f]
            z_eff = float(np.clip(z_eff_val, 0.0, 1.0))
            
        if z_eff >= self.omega_th:
            action_gate = 1  # 强电平拦截导通
            chi_val = 1
            p_conduction = 1.0
        else:
            action_gate = 0  # 落入柔性上同调随机裁剪域
            numerator = 1.5 * z_eff
            # 用 max(..., self.delta_flt) 进行最小值截断防除零
            denominator = max(1.0 - z_eff, self.delta_flt)
            exponent_raw = 2.0 * (numerator / denominator)
            exponent = np.clip(exponent_raw, -500, 500)
            p_conduction = float(expit(exponent))
            chi_val = int(np.random.binomial(1, p_conduction))
            
        return z_eff, action_gate, p_conduction
