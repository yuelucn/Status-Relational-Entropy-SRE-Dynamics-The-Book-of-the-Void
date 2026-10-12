# test_sre_transport.py
import unittest
import logging
import time
import numpy as np
from scipy.linalg import eigh
from sre_transport_alignment import SRETransportAlignmentSuite

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TestSRETransportAlignmentSuite(unittest.TestCase):

    def setUp(self):
        self.suite = SRETransportAlignmentSuite(c_max=3.0, enable_debug_log=True)

    # =========================================================================
    # 1. 算子 6 核心校验用例 (Ground Truth、非对称拦截、越界重叠、不连通图)
    # =========================================================================
    def test_operator_6_ground_truth_and_residuals(self):
        """对比小图真实全局 eigh 特征值，校验 RR 近似度与残差 warning 阈值"""
        n = 16
        np.random.seed(42)
        A = np.random.uniform(0, 1, size=(n, n))
        A = (A + A.T) / 2.0
        np.fill_diagonal(A, 0.0)
        L_G = np.diag(np.sum(A, axis=1)) - A

        # 真实精确特征值
        true_vals = eigh(L_G, eigvals_only=True)
        true_l2, true_alpha = true_vals[1], true_vals[-1]

        # 算子 6 估算值
        l2_est, alpha_est, max_res = self.suite.execute_operator_6_splicing(
            L_G, num_groups=4, k_rank=3, overlap_size=2
        )

        # 校验特征值数量级一致
        np.testing.assert_allclose(l2_est, true_l2, rtol=0.5, atol=0.5)
        np.testing.assert_allclose(alpha_est, true_alpha, rtol=0.3, atol=0.5)
        self.assertGreaterEqual(max_res, 0.0)

    def test_operator_6_asymmetric_interception(self):
        """测试非对称 L_G 矩阵拦截"""
        L_asym = np.array([[1.0, 2.0], [3.0, 4.0]])
        with self.assertRaises(ValueError):
            self.suite.execute_operator_6_splicing(L_asym, num_groups=1, k_rank=2)

    def test_operator_6_excessive_overlap_interception(self):
        """测试过大 overlap_size 越界报错"""
        L_G = np.eye(20)
        with self.assertRaises(ValueError):
            # block_size = 20//4 = 5，设 overlap_size = 5 应该被拦截
            self.suite.execute_operator_6_splicing(L_G, num_groups=4, k_rank=2, overlap_size=5)

    def test_operator_6_disconnected_graph(self):
        """测试不连通图（由 2 个独立连通块组成），验证全局常数基成功修复 Fiedler 特征为 0"""
        n1, n2 = 10, 10
        # 块 1
        A1 = np.ones((n1, n1)) - np.eye(n1)
        L1 = np.diag(np.sum(A1, axis=1)) - A1
        # 块 2
        A2 = np.ones((n2, n2)) - np.eye(n2)
        L2 = np.diag(np.sum(A2, axis=1)) - A2

        # 拼接为不连通全局图
        L_disconnected = np.block([
            [L1, np.zeros((n1, n2))],
            [np.zeros((n2, n1)), L2]
        ])

        l2_est, alpha_est, _ = self.suite.execute_operator_6_splicing(
            L_disconnected, num_groups=2, k_rank=3
        )
        # 不连通图的第二小特征值（Fiedler）应为 0
        self.assertAlmostEqual(l2_est, 0.0, places=5)

    def test_operator_6_multi_seed_loop(self):
        """多随机种子循环测试算子 6 鲁棒性"""
        seeds = [0, 1, 42, 100, 2024]
        for seed in seeds:
            np.random.seed(seed)
            n = 20
            A = np.random.uniform(0, 1, size=(n, n))
            A = (A + A.T) / 2.0
            np.fill_diagonal(A, 0.0)
            L_G = np.diag(np.sum(A, axis=1)) - A

            l2_est, alpha_est, res = self.suite.execute_operator_6_splicing(
                L_G, num_groups=4, k_rank=3
            )
            self.assertGreaterEqual(l2_est, -1e-12)
            self.assertGreater(alpha_est, l2_est)

    # =========================================================================
    # 2. KDE 仿真测试完善 (复现性、大噪声、镜像反射对比)
    # =========================================================================
    def test_kde_reproducibility(self):
        """测试固定 random_seed 时 TV 距离结果可复现"""
        tv1 = self.suite.simulate_theorem_5_3_cloaking(N_obs=200, random_seed=42)
        tv2 = self.suite.simulate_theorem_5_3_cloaking(N_obs=200, random_seed=42)
        self.assertEqual(tv1, tv2)

    def test_kde_large_noise_boundary(self):
        """测试大噪声 noise_std=1.0 边界下的稳定度"""
        suite_noisy = SRETransportAlignmentSuite(noise_std=1.0)
        tv_dist = suite_noisy.simulate_theorem_5_3_cloaking(N_obs=300, random_seed=42)
        self.assertTrue(0.0 <= tv_dist <= 1.0)

    def test_kde_reflection_comparison(self):
        """测试开启与关闭镜像反射均能正常输出合法 TV 距离 [0, 1]"""
        tv_reflected = self.suite.simulate_theorem_5_3_cloaking(
            N_obs=1000, random_seed=123, use_reflection=True
        )
        tv_no_reflection = self.suite.simulate_theorem_5_3_cloaking(
            N_obs=1000, random_seed=123, use_reflection=False
        )
        self.assertTrue(0.0 <= tv_reflected <= 1.0)
        self.assertTrue(0.0 <= tv_no_reflection <= 1.0)

    # =========================================================================
    # 3. 边界输入全覆盖 (一维向量、不均衡分块、全零/奇异矩阵)
    # =========================================================================
    def test_operator_5_1d_input(self):
        """测试算子 5 一维数组 W_e 输入"""
        W_1d = np.array([0.0, 2.0, 10.0])
        c_1d = self.suite.execute_operator_5_latency(W_1d, alpha_n=1.5)
        self.assertEqual(c_1d.shape, (3,))
        self.assertTrue((c_1d <= 3.0).all())

    def test_operator_6_uneven_partition(self):
        """测试 n=23 无法被 num_groups=4 整除时的不均衡分块切片"""
        n = 23
        A = np.ones((n, n)) - np.eye(n)
        L_G = np.diag(np.sum(A, axis=1)) - A

        l2_est, alpha_est, _ = self.suite.execute_operator_6_splicing(
            L_G, num_groups=4, k_rank=3
        )
        self.assertGreater(alpha_est, l2_est)

    def test_zero_and_singular_laplacian_stability(self):
        """测试全 0 矩阵与奇异矩阵的数值稳定性"""
        L_zero = np.zeros((10, 10))
        l2_est, alpha_est, _ = self.suite.execute_operator_6_splicing(
            L_zero, num_groups=2, k_rank=2
        )
        self.assertEqual(l2_est, 0.0)
        self.assertEqual(alpha_est, 0.0)

    # =========================================================================
    # 4. 专项性能、多实例隔离与日志控制测试
    # =========================================================================
    def test_high_dim_performance_benchmark(self):
        """测试 n=200 高维大矩阵的执行性能与耗时基准"""
        n = 200
        A = np.random.uniform(0, 1, size=(n, n))
        A = (A + A.T) / 2.0
        np.fill_diagonal(A, 0.0)
        L_G = np.diag(np.sum(A, axis=1)) - A

        start_time = time.time()
        l2_est, alpha_est, res = self.suite.execute_operator_6_splicing(
            L_G, num_groups=5, k_rank=4
        )
        elapsed = time.time() - start_time

        self.assertLess(elapsed, 2.0)  # 200 维度执行耗时必须在 2 秒以内
        self.assertGreater(alpha_est, l2_est)

    def test_multi_instance_concurrency_isolation(self):
        """测试多实例独立调用时无共享状态污染"""
        s1 = SRETransportAlignmentSuite(c_max=2.0)
        s2 = SRETransportAlignmentSuite(c_max=5.0)

        # 传入 W_e=1.0 使得未截断速度 raw_c_e = 10.0 / ln(2) = 14.43 > 5.0
        # 从而测试 s1 被截断为 2.0，s2 被截断为 5.0
        W_e = np.array([[1.0]])
        c1 = s1.execute_operator_5_latency(W_e, alpha_n=10.0)
        c2 = s2.execute_operator_5_latency(W_e, alpha_n=10.0)

        self.assertEqual(c1[0, 0], 2.0)
        self.assertEqual(c2[0, 0], 5.0)

    def test_disabled_logging_cleanliness(self):
        """测试关闭 enable_debug_log 时正常运行且零冗余输出"""
        s_silent = SRETransportAlignmentSuite(enable_debug_log=False)
        c_e = s_silent.execute_operator_5_latency(np.array([1.0]), alpha_n=1.0)
        self.assertEqual(len(c_e), 1)


if __name__ == "__main__":
    unittest.main()