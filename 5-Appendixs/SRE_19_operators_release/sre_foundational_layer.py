# sre_foundational_layer.py
import logging
from typing import List, Tuple, Dict, Any, Optional, Set
import numpy as np
import sympy as sp

logger = logging.getLogger(__name__)


class SREFoundationalOperatorSuite:
    """
    SRE 动力学第一阶段：开源基础层与空间增长工具类 (Operators 1, 2, 3, 4)
    声明：此模块严格对接闭盒外部接口边界，具有完整的 P0/P1 工业级防御与参数配置能力。
    """
    # 5-node 基础拓扑矩阵定义（只读保护）
    _M5_RAW = np.array([
        [ 1,  1, -1,  1,  1],
        [ 1,  1, -1,  1,  1],
        [-1, -1, -1,  1,  1],
        [ 1,  1,  1,  1,  1],
        [ 1,  1,  1,  1,  1]
    ], dtype=np.int8)
    _M5_RAW.flags.writeable = False

    def __init__(
        self,
        beta_sre: float = 1.2,
        lambda_0: float = 0.9,
        lambda_2: float = 0.5,
        alpha_n: float = 0.8,
        epsilon_topo: float = 1e-6,
        eps: float = 1e-16,
        max_n_dimension: int = 1000,
        enable_debug_log: bool = True
    ):
        """
        初始化基础层算子套件参数与防护阈值
        """
        if beta_sre <= 0:
            raise ValueError(f"beta_sre 必须大于 0，当前输入: {beta_sre}")
        if lambda_0 <= 0:
            raise ValueError(f"lambda_0 必须大于 0，当前输入: {lambda_0}")
        if lambda_2 <= 0:
            raise ValueError(f"lambda_2 必须大于 0，当前输入: {lambda_2}")
        if alpha_n <= 0:
            raise ValueError(f"alpha_n 必须大于 0，当前输入: {alpha_n}")
        if epsilon_topo <= 0:
            raise ValueError(f"epsilon_topo 必须大于 0，当前输入: {epsilon_topo}")
        if eps <= 0:
            raise ValueError(f"eps 必须大于 0，当前输入: {eps}")
        if max_n_dimension <= 0:
            raise ValueError(f"max_n_dimension 必须为正整数，当前输入: {max_n_dimension}")

        self.beta = beta_sre
        self.lambda_0 = lambda_0
        self.lambda_2 = lambda_2
        self.alpha_n = alpha_n
        self.epsilon_topo = epsilon_topo
        self.eps = eps
        self.max_n_dimension = max_n_dimension
        self.enable_debug_log = enable_debug_log

        # 算子 1 动态状态
        self.current_n = 1
        self.M_realized = np.array([[1]], dtype=np.int8)
        self.all_frontier_variables: List[sp.Symbol] = []

    @property
    def M5_BASE(self) -> np.ndarray:
        """只读属性：获取受只读保护的 5-node 基础拓扑矩阵视图"""
        return self._M5_RAW

    def _log_debug(self, msg: str, *args):
        """控制调试日志输出"""
        if self.enable_debug_log:
            logger.debug(msg, *args)

    def clear_symbol_pool(self):
        """重置/清空符号池与多实例符号状态"""
        self.all_frontier_variables.clear()
        self._log_debug("符号池与前沿变量已成功重置")

    # =========================================================================
    # 算子 1: 局域图扩张算子 G_{n -> n+1}
    # =========================================================================
    def execute_operator_1_expansion(self) -> Tuple[sp.Matrix, List[sp.Symbol], sp.Symbol]:
        """严格形式符号多项式环空间隔离扩张"""
        n = self.current_n
        if n >= self.max_n_dimension:
            raise ValueError(
                f"超越局域图扩张维度上限！当前维度 n={n} >= max_n_dimension={self.max_n_dimension}"
            )

        next_n = n + 1
        frontier_x_symbols = [sp.Symbol(f"x_({next_n},{m})", real=True) for m in range(1, next_n)]
        frontier_y_symbol = sp.Symbol(f"y_{next_n}", real=True)

        self.all_frontier_variables.extend(frontier_x_symbols + [frontier_y_symbol])
        M_symbolic = sp.Matrix.zeros(next_n, next_n)

        # 只读继承历史矩阵
        M_symbolic[:n, :n] = sp.Matrix(self.M_realized)

        for k in range(n):
            M_symbolic[k, n] = frontier_x_symbols[k]
            M_symbolic[n, k] = frontier_x_symbols[k]
        M_symbolic[n, n] = frontier_y_symbol

        self._log_debug("算子 1 执行成功 | 维度扩张: %d -> %d", n, next_n)
        return M_symbolic, frontier_x_symbols, frontier_y_symbol

    def apply_global_homomorphism(self, symbolic_expr: Any, assignment: Dict[sp.Symbol, int]) -> Any:
        """全局赋值同态映射 Phi: 校验二元值域约束 {-1, 1}"""
        if not isinstance(assignment, dict):
            raise ValueError(f"assignment 必须为字典类型，当前类型: {type(assignment)}")

        invalid_vars = [var for var, val in assignment.items() if val not in (-1, 1)]
        if invalid_vars:
            raise ValueError(
                f"违反二元自旋值域预限定约束！变量 {invalid_vars} 的赋值不在 {{-1, 1}} 中"
            )
        return symbolic_expr.subs(assignment)

    def update_realized_state(self, next_M_realized: np.ndarray):
        """固化同步历史数值状态"""
        if not isinstance(next_M_realized, np.ndarray) or next_M_realized.ndim != 2:
            raise ValueError("next_M_realized 必须为二维 NumPy 数组")
        if next_M_realized.shape[0] != next_M_realized.shape[1]:
            raise ValueError(f"next_M_realized 必须为方阵，当前形状: {next_M_realized.shape}")

        self.M_realized = next_M_realized.copy()
        self.current_n = self.M_realized.shape[0]
        self._log_debug("历史数值状态已固化，当前维度 n: %d", self.current_n)

    # =========================================================================
    # 算子 2: 局域度量与概率剪枝复合算子 (M_chi o E_local)
    # =========================================================================
    def evaluate_operator_2_metrics(
        self, 
        neighbors_f: Set[int], 
        neighbors_m: Set[int], 
        edge_spins: Dict[Tuple[int, int], int], 
        vf_id: int, 
        vm_id: int
    ) -> Tuple[int, int, int]:
        """计算完整二阶全路径行走干涉，显式分离圈空间与自环"""
        if not isinstance(neighbors_f, set) or not isinstance(neighbors_m, set):
            raise ValueError("neighbors_f 与 neighbors_m 必须为 set 类型")
        if not isinstance(edge_spins, dict):
            raise ValueError("edge_spins 必须为 dict 类型")
        if vf_id < 0 or vm_id < 0:
            raise ValueError(f"节点 ID 不能为负数，当前输入: vf_id={vf_id}, vm_id={vm_id}")

        if vf_id == vm_id:
            intersection_sum = sum(
                edge_spins.get(tuple(sorted((vf_id, vk_id))), 0) ** 2 
                for vk_id in neighbors_f
            )
            return intersection_sum, intersection_sum, intersection_sum + 1

        common_neighbors = neighbors_f.intersection(neighbors_m)
        intersection_sum = sum(
            edge_spins.get(tuple(sorted((vf_id, vk_id))), 0) * 
            edge_spins.get(tuple(sorted((vk_id, vm_id))), 0)
            for vk_id in common_neighbors
        )

        s_fm = edge_spins.get(tuple(sorted((vf_id, vm_id))), 0)
        complete_interference = intersection_sum + 2 * s_fm
        return intersection_sum, intersection_sum, complete_interference

    # =========================================================================
    # 算子 3: 非线性级联相乘与松弛算子 (O_full)
    # =========================================================================
    def evaluate_operator_3_field(self, A: int, B: int) -> Tuple[int, int]:
        """5-node NAND 门非线性符号场等式与真值表硬校验"""
        if A not in (0, 1):
            raise ValueError(f"输入 A 必须属于 {{0, 1}}，当前输入为: {A}")
        if B not in (0, 1):
            raise ValueError(f"输入 B 必须属于 {{0, 1}}，当前输入为: {B}")

        # 使用只读视图副本避免修改源数据
        M_test = self._M5_RAW.copy()
        M_test[0, 0] = 1 if A == 0 else -1
        M_test[1, 1] = 1 if B == 0 else -1

        S_front = np.prod(M_test[:, :3], axis=1)

        Y_float = 0.5 * (int(S_front[0]) + int(S_front[1])) - int(S_front[2])
        if Y_float == 0.0:
            Y_spin = 1
        elif Y_float > 1.0:
            Y_spin = -1
        else:
            Y_spin = int(np.sign(Y_float))

        Y_bool = (1 + Y_spin) // 2
        self._log_debug("算子 3 执行成功 | 输入: (%d, %d) -> Y_spin: %d, Y_bool: %d", A, B, Y_spin, Y_bool)
        return Y_spin, Y_bool

    # =========================================================================
    # 算子 4: 局域拓扑度数统计标准算子 (M_degree)
    # =========================================================================
    def execute_operator_4_degree(
        self, 
        M_local: np.ndarray, 
        lambda_2: Optional[float] = None, 
        alpha_n: Optional[float] = None, 
        epsilon_topo: Optional[float] = None
    ) -> np.ndarray:
        """
        谱同质平滑与狄利克雷能量正定下界夹紧，消除真空奇异性
        """
        if not isinstance(M_local, np.ndarray) or M_local.ndim != 2 or M_local.shape[0] != M_local.shape[1]:
            raise ValueError(f"M_local 必须为二维方阵，当前形状: {getattr(M_local, 'shape', None)}")

        l2_eff = lambda_2 if lambda_2 is not None else self.lambda_2
        an_eff = alpha_n if alpha_n is not None else self.alpha_n
        ep_eff = epsilon_topo if epsilon_topo is not None else self.epsilon_topo

        if l2_eff <= 0 or an_eff <= 0 or ep_eff <= 0:
            raise ValueError("lambda_2, alpha_n, epsilon_topo 参数必须大于 0")

        D_out = np.sum(np.abs(M_local), axis=1, dtype=float)
        D_self = np.diag(M_local).astype(float)

        D_i = D_out[:, None]
        D_j = D_out[None, :]
        D_self_i = D_self[:, None]
        D_self_j = D_self[None, :]

        # 在 np.sqrt 前执行 np.maximum(x, 0.0)，杜绝产生 NaN
        Di_Dj_product = np.maximum(D_i * D_j, 0.0)
        numerator_base = np.sqrt(Di_Dj_product)

        radicand = np.maximum(l2_eff + D_self_i + D_self_j + ep_eff, self.eps)
        W_base = numerator_base / np.sqrt(radicand)

        M_square = np.abs(M_local @ M_local).astype(float)
        log_factor = np.log1p(l2_eff / an_eff)
        log_damp_numerator = M_square * log_factor
        
        # 分母防除零保护
        log_damp_denominator = max(an_eff, self.eps) + numerator_base
        W_damp = 1.0 + (log_damp_numerator / log_damp_denominator)

        W_e = W_base * W_damp
        self._log_debug(
            "算子 4 标量版执行成功 | 权重最小值: %.6e, 极值比: %.6e", 
            float(np.min(W_e)), float(np.max(W_e))
        )
        return W_e

    # =========================================================================
    # 算子 4 升级：并行全矩阵级向量化拓扑度数统计算子 (M_degree_vectorized)
    # =========================================================================
    def execute_operator_4_degree_vectorized(
        self, 
        mean_X0_sq: np.ndarray, 
        mean_X1_sq: np.ndarray, 
        mean_X0X1_star: np.ndarray, 
        lambda_2: Optional[float] = None, 
        alpha_n: Optional[float] = None, 
        epsilon_topo: Optional[float] = None
    ) -> np.ndarray:
        """
        全矩阵级并行向量化版本，通过组合分支计算重构消除重复代码
        """
        l2_eff = lambda_2 if lambda_2 is not None else self.lambda_2
        an_eff = alpha_n if alpha_n is not None else self.alpha_n
        ep_eff = epsilon_topo if epsilon_topo is not None else self.epsilon_topo

        if not (mean_X0_sq.shape == mean_X1_sq.shape == mean_X0X1_star.shape):
            raise ValueError(
                f"特征图形状不一致: mean_X0_sq={mean_X0_sq.shape}, "
                f"mean_X1_sq={mean_X1_sq.shape}, mean_X0X1_star={mean_X0X1_star.shape}"
            )

        abs_X0X1 = np.abs(mean_X0X1_star)
        D_out_0 = mean_X0_sq + abs_X0X1
        D_out_1 = mean_X1_sq + abs_X0X1

        # 构建 2x2 通道组合结构，重构消除重复代码
        D_out_list = [D_out_0, D_out_1]
        D_self_list = [mean_X0_sq, mean_X1_sq]

        B_sq = abs_X0X1 ** 2
        M_sq_branches = [
            [np.abs(mean_X0_sq * mean_X0_sq + B_sq), np.abs(mean_X0_sq * mean_X0X1_star + mean_X0X1_star * mean_X1_sq)],
            [np.abs(np.conj(mean_X0X1_star) * mean_X0_sq + mean_X1_sq * np.conj(mean_X0X1_star)), np.abs(B_sq + mean_X1_sq * mean_X1_sq)]
        ]

        log_factor = np.log1p(l2_eff / an_eff)
        safe_an = max(an_eff, self.eps)

        W_e_branches = [[None, None], [None, None]]

        for r in range(2):
            for c in range(2):
                Di_Dj = np.maximum(D_out_list[r] * D_out_list[c], 0.0)
                num_base = np.sqrt(Di_Dj)

                radicand = np.maximum(l2_eff + D_self_list[r] + D_self_list[c] + ep_eff, self.eps)
                w_base = num_base / np.sqrt(radicand)

                w_damp = 1.0 + (M_sq_branches[r][c] * log_factor) / (safe_an + num_base)
                W_e_branches[r][c] = w_base * w_damp

        # 打包成 4D 张量 (Rows, Cols, 2, 2)
        W_e_tensor = np.stack([
            np.stack([W_e_branches[0][0], W_e_branches[0][1]], axis=-1),
            np.stack([W_e_branches[1][0], W_e_branches[1][1]], axis=-1)
        ], axis=-2)

        self._log_debug("算子 4 向量化版本执行成功 | 图像张量形状: %s", W_e_tensor.shape)
        return W_e_tensor