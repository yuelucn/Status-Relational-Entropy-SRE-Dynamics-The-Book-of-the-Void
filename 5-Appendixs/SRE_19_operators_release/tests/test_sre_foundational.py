# test_sre_foundational.py
import unittest
import logging
import numpy as np
import sympy as sp
from sre_foundational_layer import SREFoundationalOperatorSuite

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TestSREFoundationalOperatorSuite(unittest.TestCase):

    def setUp(self):
        self.suite = SREFoundationalOperatorSuite(
            beta_sre=1.2, 
            lambda_0=0.9,
            enable_debug_log=True
        )

    # =========================================================================
    # 1. 多随机种子与全算子基本功能覆盖
    # =========================================================================
    def test_multi_seed_all_operators(self):
        """测试算子 1~4 基本流程，验证结构正确性"""
        seeds = [0, 1, 42, 100, 2024]
        for seed in seeds:
            np.random.seed(seed)
            suite = SREFoundationalOperatorSuite(max_n_dimension=100)

            # 算子 1
            M_sym, x_syms, y_sym = suite.execute_operator_1_expansion()
            self.assertEqual(M_sym.shape, (2, 2))

            # 算子 2
            edge_spins = {(0, 1): 1, (0, 2): -1, (1, 2): 1}
            s_inter, _, c_inter = suite.evaluate_operator_2_metrics({1, 2}, {0, 2}, edge_spins, 0, 1)
            self.assertEqual(s_inter, -1)

            # 算子 3
            Y_spin, Y_bool = suite.evaluate_operator_3_field(1, 1)
            self.assertEqual(Y_bool, 0)

            # 算子 4
            M_local = np.array([[2.0, -1.0], [-1.0, 3.0]], dtype=float)
            W_e = suite.execute_operator_4_degree(M_local)
            self.assertEqual(W_e.shape, (2, 2))
            self.assertTrue((W_e > 0).all())

    # =========================================================================
    # 2. P0 阻断测试: 只读属性、拦截非法赋值与参数校验
    # =========================================================================
    def test_p0_read_only_and_validations(self):
        """验证 M5_BASE 只读保护、同态非法赋值拦截及参数合法性校验"""
        # 1. 测试 M5_BASE 只读保护（标志位必须为 False，且修改时抛出异常）
        self.assertFalse(self.suite.M5_BASE.flags.writeable)
        with self.assertRaises((ValueError, TypeError)):
            self.suite.M5_BASE[0, 0] = 99

        # 2. 测试算子 3 非 0/1 非法输入拦截
        with self.assertRaises(ValueError):
            self.suite.evaluate_operator_3_field(A=2, B=0)
        with self.assertRaises(ValueError):
            self.suite.evaluate_operator_3_field(A=0, B=-1)

        # 3. 测试算子 1 最大维度截断 (当 current_n >= max_n_dimension 时精准拦截)
        suite_small = SREFoundationalOperatorSuite(max_n_dimension=1)
        with self.assertRaises(ValueError):
            suite_small.execute_operator_1_expansion()

        # 测试符号池重置功能
        suite_small.clear_symbol_pool()
        self.assertEqual(len(suite_small.all_frontier_variables), 0)

        # 4. 测试算子 4 NaN 防范与分母防除零（零矩阵输入）
        M_zero = np.zeros((3, 3), dtype=float)
        W_zero = self.suite.execute_operator_4_degree(M_zero)
        self.assertFalse(np.isnan(W_zero).any())
        self.assertFalse(np.isinf(W_zero).any())

    # =========================================================================
    # 3. 测试 算子 3 全量 NAND 真值表覆盖
    # =========================================================================
    def test_operator_3_full_nand_truth_table(self):
        """测试算子 3 是否完全符合标准的 2-input NAND 逻辑"""
        truth_table = [
            (0, 0, 1),
            (0, 1, 1),
            (1, 0, 1),
            (1, 1, 0)
        ]
        for A, B, expected in truth_table:
            _, Y_bool = self.suite.evaluate_operator_3_field(A, B)
            self.assertEqual(Y_bool, expected)

    # =========================================================================
    # 4. 测试 算子 4 标量版与并行向量化版的逐元素等价性
    # =========================================================================
    def test_operator_4_scalar_vs_vectorized_equivalence(self):
        """校验算子 4 标量版本与重构后的向量化版本等价"""
        M_local = np.array([[2.0, -1.0], [-1.0, 3.0]], dtype=float)
        W_single = self.suite.execute_operator_4_degree(M_local)

        mean_X0_sq = np.array([[2.0]])
        mean_X1_sq = np.array([[3.0]])
        mean_X0X1_star = np.array([[-1.0]])

        W_vec_tensor = self.suite.execute_operator_4_degree_vectorized(
            mean_X0_sq, mean_X1_sq, mean_X0X1_star
        )
        W_vec_single = W_vec_tensor[0, 0]

        np.testing.assert_allclose(W_single, W_vec_single, rtol=1e-12, atol=1e-12)


if __name__ == "__main__":
    unittest.main()