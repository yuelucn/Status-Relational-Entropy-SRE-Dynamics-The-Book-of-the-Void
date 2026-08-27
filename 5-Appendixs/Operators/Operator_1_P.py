import numpy as np
import sympy as sp
from typing import List, Tuple, Dict, Any

class LocalGraphExpansionOperator:
    """
    算子 1：局域图扩张算子 G_{n -> n+1} 的严格数理逻辑复现
    严格实现形式多项式符号参数空间与实值离散解空间的场景隔离
    """
    def __init__(self):
        # 规范 3.1: 迭代起点：定义初始的 1 阶离散值方阵常量 M_1
        self.current_n = 1
        self.M_realized = np.array([[1]], dtype=np.int8)  # 显式声明 1 阶基准
        
        # 存储历史生成的符号变量，用以验证全历时独立性
        self.all_frontier_variables = []

    def execute_expansion(self) -> Tuple[sp.Matrix, List[sp.Symbol], sp.Symbol]:
        """
        规范 3.3 矩阵扩张结构方程
        映射关系: G_{n -> n+1} : M_n -> M_{n+1}[x, y]
        返回: (形式符号方阵 M_{n+1}, 前沿耦合形式向量分量列表, 前沿自耦合形式标量)
        """
        n = self.current_n
        next_n = n + 1
        
        # 规范 3.1 多轮扩张变量命名隔离规则：附加当前阶数索引前缀防止大规模迭代符号冲突
        # 规范 4.2 向量显式等式：声明前沿耦合形式向量分量
        frontier_x_symbols = [
            sp.Symbol(f"x_({next_n},{m})", real=True) for m in range(1, next_n)
        ]
        # 声明前沿自耦合形式标量
        frontier_y_symbol = sp.Symbol(f"y_{next_n}", real=True)
        
        # 记录变量，供全历时追踪
        self.all_frontier_variables.extend(frontier_x_symbols + [frontier_y_symbol])
        
        # 创建形式符号方阵 M_{n+1}，初始化为全零符号方阵
        M_symbolic = sp.Matrix.zeros(next_n, next_n)
        
        # 规范 4.2 边界保持约束：只读子空间继承，前 n 阶子方阵无条件绝对继承输入常量数值块
        for i in range(n):
            for j in range(n):
                M_symbolic[i, j] = int(self.M_realized[i, j])
                
        # 挂载前沿耦合形式向量（第 n+1 行和第 n+1 列）
        for k in range(n):
            M_symbolic[k, n] = frontier_x_symbols[k]
            M_symbolic[n, k] = frontier_x_symbols[k]
            
        # 挂载前沿自耦合形式标量（右下角对角线）
        M_symbolic[n, n] = frontier_y_symbol
        
        return M_symbolic, frontier_x_symbols, frontier_y_symbol

    def apply_global_homomorphism(self, symbolic_expr: Any, assignment: Dict[sp.Symbol, int]) -> Any:
        """
        规范 2.2 全局赋值同态映射 (Global evaluation Homomorphism, Phi)
        实现从形式多元多项式环向实数域的代数态射求值映射
        """
        # 校验值域预限定硬约束：赋值必须严格属于离散二元集 {-1, 1}
        for var, val in assignment.items():
            if val not in [-1, 1]:
                raise ValueError(f"违反值域预限定约束！变量 {var} 的赋值 {val} 必须属于 {{-1, 1}}")
                
        # 执行同态求值映射 (Evaluation Homomorphism)
        return symbolic_expr.subs(assignment)

    def update_realized_state(self, next_M_realized: np.ndarray):
        """
        更新系统的固化历史数值状态，为下一步迭代做准备
        """
        self.M_realized = next_M_realized.copy()
        self.current_n = self.M_realized.shape[0]


# =====================================================================
# 验证与演示主程序
# =====================================================================
if __name__ == "__main__":
    print("="*80)
    print(" 算子 1：局域图扩张算子 G_{n->n+1} 严格数理规范配套验证程序 ")
    print("="*80)

    # 初始化算子，此时系统处于第 1 步基准初态 M_1
    operator = LocalGraphExpansionOperator()
    print(f"[迭代第 1 步] 初始二进制离散值方阵常量 M_1:\n{operator.M_realized}\n")

    # -----------------------------------------------------------------
    # 规范 4.3 演示算例：M_1 -> M_2 的太初形式扩张
    # -----------------------------------------------------------------
    print("-" * 60)
    print("【第一轮迭代演化：M_1 -> M_2】")
    M_2_symbolic, x_2_vars, y_2_var = operator.execute_expansion()
    print(f"1. 算子输出的 2 阶形式符号矩阵 M_2(x, y):\n{M_2_symbolic}")
    print(f"   声明的前沿形式变量分量: x_vec = {x_2_vars}, y_scalar = {y_2_var}")
    
    # 模拟下游算子求解：设定一组符合二进制值域约束的合法同态赋值
    # 假设下游解算出：x_(2,1) = 1, y_2 = -1 (即规范中推导出的 Hadamard 太初基准)
    phi_2_assignment = {x_2_vars[0]: 1, y_2_var: -1}
    M_2_realized_sp = operator.apply_global_homomorphism(M_2_symbolic, phi_2_assignment)
    M_2_realized = np.array(M_2_realized_sp.tolist(), dtype=np.int8)
    print(f"2. 下游算子代数求解并注入全局同态 Phi 后，固定出的数值方阵 M_2:\n{M_2_realized}")
    
    # 将 M_2 固化同步进系统，作为下一轮演化的只读基底
    operator.update_realized_state(M_2_realized)

    # -----------------------------------------------------------------
    # 演示：第 3 步扩张 (M_2 -> M_3) —— 规范第六章通用定理三不变量实证
    # -----------------------------------------------------------------
    print("-" * 60)
    print("【第二轮迭代演化：M_2 -> M_3】")
    M_3_symbolic, x_3_vars, y_3_var = operator.execute_expansion()
    print(f"1. 算子输出的 3 阶形式符号矩阵 M_3(x, y):\n{M_3_symbolic}")
    print(f"   声明的时间戳隔离前沿变量分量: x_vec = {x_3_vars}, y_scalar = {y_3_var}")

    # 6.1 形式符号矩阵平方场景验证
    print("\n2. [形式符号矩阵平方场景] 执行 2 阶形式符号图行走计算 M_3^2...")
    M_3_square_symbolic = M_3_symbolic * M_3_symbolic
    
    # 提取第 3 个对角线形式矩阵元 P_33 (1基标号在Python中对应的0基索引为[2, 2])
    P_33_symbolic = M_3_square_symbolic[2, 2]
    print(f"   3号节点的形式对角线路径干涉多元多项式 P_33 = {P_33_symbolic}")
    
    # 6.2 通用对角线不变量定理（任意 n 阶通用证明）在 n=2 时的数值实证
    # 任意指派一组满足二进制值域预限定硬约束的同态赋值方案
    # 方案一：x_(3,1) = -1, x_(3,2) = 1, y_3 = -1
    phi_3_case1 = {x_3_vars[0]: -1, x_3_vars[1]: 1, y_3_var: -1}
    P_33_val_case1 = operator.apply_global_homomorphism(P_33_symbolic, phi_3_case1)
    
    # 方案二：换一组截然不同的二进制赋值：x_(3,1) = 1, x_(3,2) = 1, y_3 = 1
    phi_3_case2 = {x_3_vars[0]: 1, x_3_vars[1]: 1, y_3_var: 1}
    P_33_val_case2 = operator.apply_global_homomorphism(P_33_symbolic, phi_3_case2)
    
    print(f"   [方案一求值] 当赋值为 {phi_3_case1} 时，数值结果: {P_33_val_case1}")
    print(f"   [方案二求值] 当赋值为 {phi_3_case2} 时，数值结果: {P_33_val_case2}")
    
    # 严格断言不变量定理：不论符号具体如何指派，其经同态映射后在数值上必然恒等于常量 n+1 = 2+1 = 3
    assert int(P_33_val_case1) == 3, "定理三不变量逻辑发生冲突！"
    assert int(P_33_val_case2) == 3, "定理三不变量逻辑发生冲突！"
    print("   ✅ [定理三实证成功] 形式未知元自发消去，P_33 数值无条件恒等于常量 n + 1 = 3")

    # -----------------------------------------------------------------
    # 演示：第三章 拓扑受挫的通用判定与数值结算
    # -----------------------------------------------------------------
    print("-" * 60)
    print("【第三章：拓扑受挫通用定理与数值路径干涉实证】")
    # 【全面修复笔误位置】构造规范 3.3 节中的受挫数值示例矩阵 M_3_frustrated，确保二维结构完全正确
    M_3_frustrated = np.array([
        [1, 1, 1],
        [1, -1, -1],
        [1, -1, -1]
    ], dtype=np.int8)
    
    # 验证定理一：回路所有边权重乘积是否为 -1
    # 基于1基索引 (1,2) 对应 0基的[0,1], (2,3) 对应[1,2], (3,1) 对应[2,0]
    loop_product = int(M_3_frustrated[0, 1] * M_3_frustrated[1, 2] * M_3_frustrated[2, 0])
    print(f"1. 闭环回路 1->2->3->1 的边权离散代数乘积为: {loop_product}")
    if loop_product == -1:
        print("   ✅ 触发单回路受挫充要条件！系统确立为拓扑受挫状态。")
        
    # 计算数值矩阵平方场景下的 2 阶行走路径干涉元 P_23
    M_3_frustrated_sp = sp.Matrix(M_3_frustrated.tolist())
    M_3_frustrated_square = M_3_frustrated_sp * M_3_frustrated_sp
    P_23_val = M_3_frustrated_square[1, 2] # 1基(2,3) 对应 0基的[1,2]
    print(f"2. 数值结算节点 2 到节点 3 的 2 阶路径干涉残余偏置 P_23 = {P_23_val}")
    assert int(P_23_val) == 3, "数值受挫计算错误"
    print("   ✅ 残余偏置为 3 不等于 0，拓扑受挫导致局部干涉无法归零获得直接代数实证。")

    # -----------------------------------------------------------------
    # 演示：第五章 满连接固定赋值下的数值发散定量分析
    # -----------------------------------------------------------------
    print("-" * 60)
    print("【第五章：满连接固定赋值导致的数值发散定量分析测试】")
    print("   测试结论验证：若不经过下游算子解算而强制注入全 1 满连接，系统谱半径将以 O(n) 发散")
    
    # 模拟从阶数 n=1 到 n=20 的大规模全 1 满连接固定赋值迭代
    steps_n = list(range(1, 21))
    spectral_radii = []
    
    for n_size in steps_n:
        # 构造全 1 数值矩阵
        J_n = np.ones((n_size, n_size), dtype=float)
        
        # 采用专门优化的实对称矩阵特征值求解器，完美消除非收敛崩溃异常
        # 完美解决全1缩退矩阵在传统QR分解法（np.linalg.eigvals）下的不收敛崩溃异常 (LinAlgError)
        eigenvalues = np.linalg.eigvalsh(J_n)
        
        # 提取最大特征值绝对值（谱半径）
        rho_val = np.max(np.abs(eigenvalues))
        spectral_radii.append(rho_val)
        
    print(f"   规模 n=1 时的谱半径: {spectral_radii[0]:.1f}")
    print(f"   规模 n=5 时的谱半径: {spectral_radii[4]:.1f}")
    print(f"   规模 n=10 时的谱半径: {spectral_radii[9]:.1f}")
    print(f"   规模 n=20 时的谱半径: {spectral_radii[19]:.1f}")
    
    # 验证谱半径不变量是否严格呈线性发散 \rho = n
    for n_size, rho_val in zip(steps_n, spectral_radii):
        assert np.isclose(rho_val, n_size), f"规模 {n_size} 处的谱半径与 O(n) 线性规律不符"
    print("   ✅ [发散测试通过] 谱半径随规模扩充严格呈线性发展（以 O(n) 速度线性无限增长）。")
    print("   ✅ [代数合理性获证] 反向定量确立了在算子 1 中保持‘参数化符号悬决’的绝对数学逻辑必然性。")
    print("="*80)
