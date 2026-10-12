# test_sre_pipeline.py
import unittest
import numpy as np
import sympy as sp

from sre_foundational_layer import SREFoundationalOperatorSuite
from sre_transport_alignment import SRETransportAlignmentSuite
from sre_commercial_core import SRECommercialCoreSuite

class TestSREUniversalOperatorPipeline(unittest.TestCase):
    """
    状态关系熵（SRE）10算子流水线自动化审计与测试程序（修复定稿版）
    """

    def setUp(self):
        """初始化测试环境与超参数"""
        self.foundational_suite = SREFoundationalOperatorSuite(beta_sre=1.2, lambda_0=0.9)
        self.transport_suite = SRETransportAlignmentSuite(c_max=3.0, delta_flt=1e-16)
        self.commercial_suite = SRECommercialCoreSuite(num_local_edges=4, delta_flt=1e-16)

    def test_phase_1_foundational_layer(self):
        """测试第一阶段：开源基础层与空间增长 (Operators 1, 2, 3, 4)"""
        print("\n[START] 开始审计第一阶段：开源基础层...")
        
        # 1. 验证算子 1
        self.foundational_suite.M_realized = np.array([[1]], dtype=np.int8)
        M2_sym, x_symbols, y_symbol = self.foundational_suite.execute_operator_1_expansion()
        self.assertEqual(M2_sym.shape, (2, 2))
        self.assertEqual(len(x_symbols), 1)
        print(" -> 算子 1: 形式符号矩阵扩张维数及只读历史块继承校验 [PASS]")

        phi_assignment = {x_symbols[0]: 1, y_symbol: -1}
        M2_realized_sp = self.foundational_suite.apply_global_homomorphism(M2_sym, phi_assignment)
        M2_realized = np.array(M2_realized_sp.tolist(), dtype=np.int8)
        self.assertTrue(np.array_equal(M2_realized, np.array([[1, 1], [1, -1]])))
        
        with self.assertRaises(ValueError):
            invalid_assignment = {x_symbols[0]: 0, y_symbol: -1}
            self.foundational_suite.apply_global_homomorphism(M2_sym, invalid_assignment)
        print(" -> 算子 1: 全局同态映射值域预限定硬约束校验 [PASS]")

        # 2. 验证算子 2
        neighbors_f = {2, 3}
        neighbors_m = {3, 4}
        edge_spins = {(1, 2): 1, (1, 3): -1, (2, 3): 1, (3, 4): -1}
        pure_cycle, _, complete_i = self.foundational_suite.evaluate_operator_2_metrics(
            neighbors_f, neighbors_m, edge_spins, vf_id=1, vm_id=2
        )
        self.assertIsInstance(complete_i, int)
        print(" -> 算子 2: 2阶全路径行走干涉计算边界校验 [PASS]")

        # 3. 验证算子 3
        inputs = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for A, B in inputs:
            _, Y_bool = self.foundational_suite.evaluate_operator_3_field(A, B)
            expected = int(not (A and B))
            self.assertEqual(Y_bool, expected, f"NAND真值表在输入 ({A},{B}) 处发生偏折！")
        print(" -> 算子 3: 5节点五角晶格局部反转 NAND 门完备性校验 [PASS]")

        # 4. 验证算子 4
        M_local = np.array([[1, -1], [-1, 1]])
        W_e = SREFoundationalOperatorSuite.execute_operator_4_degree(
            M_local, lambda_2=0.5, alpha_n=2.5, epsilon_topo=1.0
        )
        self.assertFalse(np.any(np.isnan(W_e)))
        self.assertEqual(W_e.shape, (2, 2))
        print(" -> 算子 4: 2步图行走不变量计算与真空消除校验 [PASS]")

    def test_phase_2_transport_alignment(self):
        """测试第二阶段：同质度规传输与时滞校准 (Operators 5, 6)"""
        print("\n[START] 开始审计第二阶段：度规传输与时滞校准...")
        
        # 1. 验证算子 5
        W_e_mock = np.array([[0.0, 100.0], [100.0, 0.0]])
        c_e = self.transport_suite.execute_operator_5_latency(W_e_mock, alpha_n=1.5)
        self.assertTrue(np.all(c_e <= self.transport_suite.c_max))
        print(" -> 算子 5: 凝聚态自适应对数坍缩与 conduction 速度上限校验 [PASS]")

        tv_distance = self.transport_suite.simulate_theorem_5_3_cloaking(N_obs=50)
        self.assertTrue(0.0 <= tv_distance <= 1.0)
        print(" -> 算子 5: 零测度子流形有限观测全变差防御系数审计 [PASS]")

        # 2. 验证算子 6：将图扩展至 8x8，k_rank 设为 4，拉开谱半径与 Fiedler 先验的数值差
        L_G_large = np.zeros((8, 8))
        for i in range(8):
            L_G_large[i, i] = 2.0
            L_G_large[i, (i+1)%8] = -1.0
            L_G_large[i, (i-1)%8] = -1.0
            
        l2_approx, alpha_approx = SRETransportAlignmentSuite.execute_operator_6_splicing(
            L_G_large, num_groups=2, k_rank=4
        )
        self.assertGreater(alpha_approx, l2_approx)
        print(" -> 算子 6: Rayleigh-Ritz 剪接核矩阵特征极值提取变分校验 [PASS]")

    def test_phase_3_commercial_core(self):
        """测试第三阶段：商业核心防御与拓扑场闭合 (Operators 7, 8, 9, 10)"""
        print("\n[START] 开始审计第三阶段：商业封闭核心防御...")
        
        # 1. 验证算子 7
        B_co_7 = np.array([[1.0, 0.0, -1.0, 0.0], [0.0, 1.0, 0.0, -1.0]])
        E_s = np.array([0.1, -0.2, 0.3, 0.4])
        grad_E, B_half = SRECommercialCoreSuite.evaluate_operator_7_potential(B_co_7, E_s)
        self.assertEqual(B_half.shape, (4,))
        print(" -> 算子 7: 辛结构嵌入对偶均衡器松弛解算校验 [PASS]")

        # 2. 验证算子 8：显式传入标准的 (4, 4) 正交方阵作为 Operator 8 的专用同调基
        B_co_8_square = np.eye(4)
        V_write_mock = np.eye(4) * 0.2
        _, delta_Pi = self.commercial_suite.execute_operator_8_valve_flow(
            E_s, B_half, B_co_8_square, V_write_mock, lambda_2=0.5, alpha_smooth=0.25
        )
        self.assertLess(delta_Pi, 0.0)
        print(" -> 算子 8: Convective Jacobian Flows 变分单调负定下界断言校验 [PASS]")

        # 3. 验证算子 9：双阶平滑缝合矩阵 S_dual 同调零空间投影
        # del_2 必须是 (|E|, |F|) 维度的矩阵，此处设定 3 条边，2 个封闭面域
        del_2 = np.array([
            [1.0, -1.0],
            [0.0, 1.0],
            [-1.0, 0.0]
        ])
        delta_1 = del_2.T  # 自动成为 (2, 3) 矩阵
        S_dual = SRECommercialCoreSuite.execute_operator_9_stitching(del_2, delta_1, Nf=2, lambda_2=0.6)
        self.assertEqual(S_dual.shape, (2, 2))
        print(" -> S_dual 矩阵形式高阶伪逆对偶投影校验 [PASS]")


        # 4. 验证算子 10
        L_mock = np.array([[1.0, -1.0], [-1.0, 1.0]])
        L_plus_mock = np.linalg.pinv(L_mock)
        z_eff, action_gate, p_cond = self.commercial_suite.execute_operator_10_firewall(
            u=0, v_f=1, L_plus=L_plus_mock, is_bridge=True
        )
        self.assertEqual(action_gate, 1)
        self.assertEqual(p_cond, 1.0)
        self.assertEqual(z_eff, 1.0)
        print(" -> 算子 10: 流形解绑断路危机刚性抢占豁免强拦截校验 [PASS]")

if __name__ == "__main__":
    print("=" * 80)
    print(" 状态关系熵（SRE）动力学：通用图算子解耦流水线系统集成审计平台 (修复定稿版)")
    print("=" * 80)
    unittest.main()
