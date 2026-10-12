# test_sre_core.py
import unittest
import logging
import numpy as np
from sre_commercial_core import SRECommercialCoreSuite

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TestSRECommercialCoreSuite(unittest.TestCase):

    def setUp(self):
        self.Mk = 10
        self.K0 = 30
        self.delta_flt = 1e-16
        self.suite = SRECommercialCoreSuite(
            num_local_edges=self.Mk, 
            k0_horizon=self.K0,
            delta_flt=self.delta_flt,
            enable_debug_log=True
        )

    # =========================================================================
    # 1. 多随机种子覆盖全部 4 个算子 (Operators 7, 8, 9, 10)
    # =========================================================================
    def test_multi_seed_all_operators(self):
        """覆盖多随机种子对算子 7, 8, 9, 10 进行统一 rtol/atol 精度验证"""
        seeds = [0, 1, 42, 100, 2024]
        rtol, atol = 1e-10, 1e-5

        for seed in seeds:
            np.random.seed(seed)
            M = 5
            E_s = np.random.randn(self.Mk)
            B_co = np.random.randn(M, self.Mk)
            
            # 算子 7 测试
            cached_BcoT_Bco = B_co.T @ B_co
            grad_E1, B_half1 = self.suite.evaluate_operator_7_potential(B_co, E_s)
            grad_E2, B_half2 = self.suite.evaluate_operator_7_potential(
                B_co, E_s, cached_BcoT_Bco=cached_BcoT_Bco
            )
            np.testing.assert_allclose(grad_E1, grad_E2, rtol=rtol, atol=atol)
            np.testing.assert_allclose(B_half1, B_half2, rtol=rtol, atol=atol)

            # 算子 8 测试
            A = np.random.randn(self.Mk, self.Mk)
            V_write = A.T @ A + np.eye(self.Mk)
            Phi_opt, delta_Pi_opt = self.suite.execute_operator_8_valve_flow(
                E_s, B_half1, B_co, V_write
            )
            self.assertLessEqual(delta_Pi_opt, 0.0)

            # 算子 9 测试
            Nf = 6
            del_2 = np.random.randn(self.Mk, Nf)
            delta_1 = np.random.randn(Nf, self.Mk)
            S_dual = self.suite.execute_operator_9_stitching(del_2, delta_1, Nf)
            np.testing.assert_allclose(S_dual, S_dual.T, rtol=rtol, atol=atol)

            # 算子 10 测试
            n_nodes = 6
            L_plus = np.random.randn(n_nodes, n_nodes)
            L_plus = L_plus @ L_plus.T
            z_eff, action_gate, p_cond = self.suite.execute_operator_10_firewall(
                1, 2, L_plus, is_bridge=False
            )
            self.assertTrue(0.0 <= z_eff <= 1.0)
            self.assertTrue(0.0 <= p_cond <= 1.0)

    # =========================================================================
    # 2. 算子 7 数值有限差分梯度测试
    # =========================================================================
    def test_operator_7_numerical_gradient(self):
        """补全算子 7 的有限差分梯度校验"""
        M, E_dim = 6, self.Mk
        B_co = np.random.randn(M, E_dim)
        E_s = np.random.randn(E_dim)

        grad_E_analytical, _ = self.suite.evaluate_operator_7_potential(B_co, E_s)

        def compute_potential(E_vec):
            term1 = 0.5 * E_vec.T @ (B_co.T @ B_co) @ E_vec
            term2 = np.sum(np.log(np.cosh(E_vec)))
            return term1 + term2

        eps = 1e-6
        grad_E_numerical = np.zeros_like(E_s)
        for i in range(len(E_s)):
            E_plus = E_s.copy()
            E_minus = E_s.copy()
            E_plus[i] += eps
            E_minus[i] -= eps
            grad_E_numerical[i] = (compute_potential(E_plus) - compute_potential(E_minus)) / (2 * eps)

        np.testing.assert_allclose(grad_E_analytical, grad_E_numerical, rtol=1e-5, atol=1e-5)

    # =========================================================================
    # 3. 算子 9 低秩近似分支测试 (Nf > low_rank_dim_threshold)
    # =========================================================================
    def test_operator_9_low_rank_branch(self):
        """补全算子 9 当 Nf 超过 low_rank_dim_threshold 时的低秩 eigsh 分支测试"""
        Nf_large = 105  # 超过默认 threshold 100
        del_2 = np.random.randn(self.Mk, Nf_large)
        delta_1 = np.random.randn(Nf_large, self.Mk)

        S_dual = self.suite.execute_operator_9_stitching(
            del_2, delta_1, Nf_large, use_low_rank_fallback=True
        )
        self.assertEqual(S_dual.shape, (Nf_large, Nf_large))
        np.testing.assert_allclose(S_dual, S_dual.T, rtol=1e-10, atol=1e-5)

    # =========================================================================
    # 4. 算子 10 全边界测试 (割边、非割边、阻抗极值、临界硬阈值)
    # =========================================================================
    def test_operator_10_full_boundary_mechanics(self):
        """补全算子 10 割边硬拦截、极值导通概率与临界硬阈值逻辑"""
        L_plus = np.eye(5)

        # 1. 割边 (is_bridge=True)
        z_eff, action_gate, p_cond = self.suite.execute_operator_10_firewall(
            0, 1, L_plus, is_bridge=True
        )
        self.assertEqual(z_eff, 1.0)
        self.assertEqual(action_gate, 1)
        self.assertEqual(p_cond, 1.0)

        # 2. 阻抗达到临界阈值 (z_eff >= omega_th)
        L_plus_high = np.eye(5) * 10.0
        z_eff_h, action_gate_h, p_cond_h = self.suite.execute_operator_10_firewall(
            0, 1, L_plus_high, is_bridge=False
        )
        self.assertEqual(z_eff_h, 1.0)
        self.assertEqual(action_gate_h, 1)

        # 3. 阻抗为 0 (同一节点)
        z_eff_zero, action_gate_z, p_cond_z = self.suite.execute_operator_10_firewall(
            2, 2, L_plus, is_bridge=False
        )
        self.assertEqual(z_eff_zero, 0.0)
        self.assertEqual(action_gate_z, 0)
        self.assertAlmostEqual(p_cond_z, 0.5, places=5)

    # =========================================================================
    # 5. 参数非法性全面校验测试
    # =========================================================================
    def test_parameter_validations(self):
        """测试参数合法性校验抛出 ValueError"""
        with self.assertRaises(ValueError):
            SRECommercialCoreSuite(num_local_edges=-1)
        with self.assertRaises(ValueError):
            SRECommercialCoreSuite(delta_flt=-1e-16)
        with self.assertRaises(ValueError):
            SRECommercialCoreSuite(lambda_base=-0.5)
        with self.assertRaises(ValueError):
            SRECommercialCoreSuite(exp_clip_min=100.0, exp_clip_max=-100.0)


if __name__ == "__main__":
    unittest.main()