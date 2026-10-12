import numpy as np
import sympy as sp
from typing import List, Tuple, Dict, Any

class SREFoundationalOperatorSuite:
    """
    SRE 动力学第一阶段：开源基础层与空间增长工具类 (Operators 1, 2, 3, 4)
    """
    def __init__(self, beta_sre: float = 1.2, lambda_0: float = 0.9):
        # 算子 1 初始化基准
        self.current_n = 1
        self.M_realized = np.array([[1]], dtype=np.int8) 
        self.all_frontier_variables = []
        
        # 算子 2 统计力学常数
        self.beta = beta_sre
        self.lambda_0 = lambda_0

    # =========================================================================
    # 算子 1: 局域图扩张算子 G_{n -> n+1}
    # =========================================================================
    def execute_operator_1_expansion(self) -> Tuple[sp.Matrix, List[sp.Symbol], sp.Symbol]:
        """严格形式符号多项式环空间隔离扩张"""
        n = self.current_n
        next_n = n + 1
        frontier_x_symbols = [sp.Symbol(f"x_({next_n},{m})", real=True) for m in range(1, next_n)]
        frontier_y_symbol = sp.Symbol(f"y_{next_n}", real=True)
        
        self.all_frontier_variables.extend(frontier_x_symbols + [frontier_y_symbol])
        M_symbolic = sp.Matrix.zeros(next_n, next_n)
        
        # 边界保持约束：只读历史继承
        for i in range(n):
            for j in range(n):
                M_symbolic[i, j] = int(self.M_realized[i, j])
                
        for k in range(n):
            M_symbolic[k, n] = frontier_x_symbols[k]
            M_symbolic[n, k] = frontier_x_symbols[k]
        M_symbolic[n, n] = frontier_y_symbol
        return M_symbolic, frontier_x_symbols, frontier_y_symbol

    def apply_global_homomorphism(self, symbolic_expr: Any, assignment: Dict[sp.Symbol, int]) -> Any:
        """全局赋值同态映射 Phi: 校验二元值域约束 {-1, 1}"""
        for var, val in assignment.items():
            if val not in [-1, 1]:
                raise ValueError(f"违反值域预限定约束！变量 {var} 的赋值 {val} 必须属于 {{-1, 1}}")
        return symbolic_expr.subs(assignment)

    def update_realized_state(self, next_M_realized: np.ndarray):
        """固化同步历史数值状态"""
        self.M_realized = next_M_realized.copy()
        self.current_n = self.M_realized.shape[0]

    # =========================================================================
    # 算子 2: 局域度量与概率剪枝复合算子 (M_chi o E_local)
    # =========================================================================
    def evaluate_operator_2_metrics(self, neighbors_f: set, neighbors_m: set, 
                                    edge_spins: dict, vf_id: int, vm_id: int) -> Tuple[int, int, int]:
        """计算完整二阶全路径行走干涉，显式分离圈空间与自环"""
        if vf_id == vm_id:
            intersection_sum = 0
            for vk_id in neighbors_f:
                key = tuple(sorted((vf_id, vk_id)))
                s_fk = edge_spins.get(key, 0)
                intersection_sum += (s_fk * s_fk)
            return intersection_sum, intersection_sum, intersection_sum + 1
        
        common_neighbors = neighbors_f.intersection(neighbors_m)
        intersection_sum = 0
        for vk_id in common_neighbors:
            s_fk = edge_spins.get(tuple(sorted((vf_id, vk_id))), 0)
            s_km = edge_spins.get(tuple(sorted((vk_id, vm_id))), 0)
            intersection_sum += s_fk * s_km
            
        s_fm = edge_spins.get(tuple(sorted((vf_id, vm_id))), 0)
        complete_interference = intersection_sum + s_fm * (1 + 1) # 两端点自环常数归一化为1
        return intersection_sum, intersection_sum, complete_interference

    # =========================================================================
    # 算子 3: 非线性级联相乘与松弛算子 (O_full)
    # =========================================================================
    def evaluate_operator_3_field(self, A: int, B: int) -> Tuple[int, int]:
        """5-node NAND 门非线性符号场等式与真值表硬校验"""
        M5_base = np.array([
            [ 1,  1, -1,  1,  1],
            [ 1,  1, -1,  1,  1],
            [-1, -1, -1,  1,  1],
            [ 1,  1,  1,  1,  1],
            [ 1,  1,  1,  1,  1]
        ], dtype=np.int8)
        chi = np.array([1, 1, 1, 0, 0], dtype=np.int8)
        
        M_test = M5_base.copy()
        M_test[0, 0] = 1 if A == 0 else -1
        M_test[1, 1] = 1 if B == 0 else -1
        
        S_front = np.zeros(5, dtype=np.int8)
        for i in range(5):
            prod = 1
            for j in range(5):
                term = int(chi[j]) * int(M_test[i, j]) + (1 - int(chi[j])) * 1
                prod *= term
            S_front[i] = prod
            
        Y_float = 0.5 * (int(S_front[0]) + int(S_front[1])) - int(S_front[2])
        if Y_float == 0.0:
            Y_spin = 1
        elif Y_float > 1.0:
            Y_spin = -1
        else:
            Y_spin = int(np.sign(Y_float))
            
        Y_bool = int((1 + Y_spin) / 2)
        return Y_spin, Y_bool

    # =========================================================================
    # 算子 4: 局域拓扑度数统计标准算子 (M_degree)
    # =========================================================================
    @staticmethod
    def execute_operator_4_degree(M_local: np.ndarray, lambda_2: float, 
                                  alpha_n: float, epsilon_topo: float) -> np.ndarray:
        """谱同质平滑与狄利克雷能量正定下界夹紧，消除真空奇异性"""
        D_out = np.sum(np.abs(M_local), axis=1, dtype=float)
        D_self = np.diag(M_local).astype(float)
        
        D_i = D_out[:, None]
        D_j = D_out[None, :]
        D_self_i = D_self[:, None]
        D_self_j = D_self[None, :]
        
        numerator_base = np.sqrt(D_i * D_j)
        radicand = lambda_2 + D_self_i + D_self_j + epsilon_topo
        W_base = numerator_base / np.sqrt(radicand)
        
        M_square = np.abs(M_local @ M_local).astype(float)
        log_damp_numerator = M_square * np.log(1.0 + lambda_2 / alpha_n)
        log_damp_denominator = alpha_n + numerator_base
        W_damp = 1.0 + (log_damp_numerator / log_damp_denominator)
        
        return W_base * W_damp
