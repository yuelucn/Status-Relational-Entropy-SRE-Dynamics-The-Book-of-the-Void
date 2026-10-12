"""
test_operators_11_19.py
=======================
SRE 新 9 算子 (Op 11-19) 单元测试。

覆盖范围:
  - Op 11  自旋-电荷邻接 (sre_electronic_layer)
  - Op 12  闭合环审计     (sre_electronic_layer)
  - Op 13  Chebyshev 矩   (sre_spectral_solver)
  - Op 14  Hodge 投影     (sre_spectral_solver)
  - Op 15  内生牛顿步     (sre_spectral_solver)
  - Op 16  Hankel 钳制    (sre_spectral_solver)
  - Op 17  审计裁定       (sre_spectral_solver)
  - Op 18  同调实现       (sre_spectral_solver)
  - Op 19  Z2 电荷通道    (sre_charge_channel)

运行: python -m pytest test_operators_11_19.py -v
"""

import numpy as np
import pytest

# ---- 导入三个新算子套件 ----
from sre_electronic_layer import SREElectronicOperatorSuite
from sre_spectral_solver import SRESpectralSolverSuite
from sre_charge_channel import SREChargeChannelSuite

# ============================================================================
# 通用测试 fixture
# ============================================================================

@pytest.fixture
def elec_suite():
    return SREElectronicOperatorSuite(rho=0.5, N_max_default=8, enable_debug_log=False)

@pytest.fixture
def spec_suite():
    return SRESpectralSolverSuite(enable_debug_log=False)

@pytest.fixture
def chan_suite():
    return SREChargeChannelSuite(aut_max_v=22, enable_debug_log=False)

@pytest.fixture
def ring_adj():
    """6-顶点环邻接矩阵 (已知: 6 个简单环, 长度 3-6)"""
    n = 6
    A = np.zeros((n, n))
    for i in range(n):
        A[i, (i + 1) % n] = 1.0
        A[(i + 1) % n, i] = 1.0
    return A

@pytest.fixture
def small_complex():
    """
    小型链复形: 8 顶点环 + 4 条弦, 4 个三角面。
    返回 (D, C): D(m_g,n), C(f,m_g)
    """
    n_node = 8
    edges = []
    # 环边
    for i in range(n_node):
        edges.append((i, (i + 1) % n_node))
    # 4 条弦 (构成三角面)
    edges.append((0, 2)); edges.append((2, 4))
    edges.append((4, 6)); edges.append((6, 0))
    m_g = len(edges)

    D = np.zeros((m_g, n_node))
    for e, (u, v) in enumerate(edges):
        D[e, u] = -1.0
        D[e, v] = +1.0

    # 4 个三角面: (0,1,2), (2,3,4), (4,5,6), (6,7,0)
    faces = [(0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 0)]
    f = len(faces)
    C = np.zeros((f, m_g))
    edge_idx = {(u, v): e for e, (u, v) in enumerate(edges)}
    edge_idx.update({(v, u): e for e, (u, v) in enumerate(edges)})
    for fi, (a, b, c) in enumerate(faces):
        # 面边界 ∂(face) = (a,b) + (b,c) + (c,a); 按 D 的定向赋 ±1
        for x, y in [(a, b), (b, c), (c, a)]:
            e = edge_idx[(x, y)]
            sign = 1.0 if (D[e, x] < 0 and D[e, y] > 0) else -1.0
            C[fi, e] += sign

    # 验证链复形条件: C @ D = 0 (d2∘d1 = 0)
    assert np.allclose(C @ D, 0.0, atol=1e-10), "fixture 不满足链复形条件 C@D=0"
    return D, C


# ============================================================================
# Op 11 — 自旋-电荷邻接
# ============================================================================

class TestOp11SpinCharge:
    def test_basic_shapes(self, elec_suite, ring_adj):
        chi = np.array([2.2, 2.55, 3.04, 3.44, 2.55, 2.2])
        res = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi)
        n = 6
        assert res["A_q"].shape == (n, n)
        assert res["L_q"].shape == (n, n)
        assert res["sigma"].shape == (n, n)
        assert res["wq"].shape == (n, n)
        assert res["s"].shape == (n,)

    def test_Aq_zero_diagonal(self, elec_suite, ring_adj):
        chi = np.array([2.2, 2.55, 3.04, 3.44, 2.55, 2.2])
        res = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi)
        np.testing.assert_array_equal(np.diag(res["A_q"]), 0.0)

    def test_Aq_monotone_in_rho(self, elec_suite, ring_adj):
        """rho 增大 → A_q 边权不减 (因为 wq >= 0)"""
        chi = np.array([2.2, 2.55, 3.04, 3.44, 2.55, 2.2])
        r0 = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi, rho=0.0)
        r1 = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi, rho=0.5)
        r2 = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi, rho=1.0)
        assert np.all(r2["A_q"] >= r1["A_q"] - 1e-12)
        assert np.all(r1["A_q"] >= r0["A_q"] - 1e-12)

    def test_wq_symmetric_bounded(self, elec_suite, ring_adj):
        chi = np.array([2.2, 2.55, 3.04, 3.44, 2.55, 2.2])
        res = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi)
        np.testing.assert_allclose(res["wq"], res["wq"].T, atol=1e-15)
        assert np.all(res["wq"] >= 0.0)
        assert np.all(res["wq"] <= 1.0 + 1e-12)  # |tanh| <= 1

    def test_laplacian_psd(self, elec_suite, ring_adj):
        """L_q 对称半正定"""
        chi = np.array([2.2, 2.55, 3.04, 3.44, 2.55, 2.2])
        res = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi)
        np.testing.assert_allclose(res["L_q"], res["L_q"].T, atol=1e-12)
        ev = np.linalg.eigvalsh(res["L_q"])
        assert np.all(ev >= -1e-10)

    def test_uniform_chi_no_modulation(self, elec_suite, ring_adj):
        """电负性均匀 → wq=0 → A_q = A_s"""
        chi = np.ones(6) * 2.5
        res = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi)
        np.testing.assert_allclose(res["wq"], 0.0, atol=1e-12)
        np.testing.assert_allclose(res["A_q"], ring_adj, atol=1e-12)

    def test_invalid_input_raises(self, elec_suite, ring_adj):
        chi = np.array([2.2, 2.55, 3.04])  # 长度不匹配
        with pytest.raises(ValueError):
            elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi)
        with pytest.raises(ValueError):
            elec_suite.execute_operator_11_spin_charge_adjacency(np.zeros((3, 4)), np.ones(3))


# ============================================================================
# Op 12 — 闭合环审计
# ============================================================================

class TestOp12ClosedLoopAudit:
    def test_ring_has_one_cycle(self, elec_suite, ring_adj):
        """6-环应恰好 1 个简单环 (长度 6)"""
        res = elec_suite.execute_operator_12_closed_loop_audit(ring_adj, N_max=8)
        assert res["n_loops"] == 1
        assert res["n_closed_loops"] == 1

    def test_triangle_graph(self, elec_suite):
        """三角形: 1 个长度 3 的环"""
        A = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)
        res = elec_suite.execute_operator_12_closed_loop_audit(A, N_max=6)
        assert res["n_loops"] == 1
        assert res["loop_atoms"] == [0, 1, 2]

    def test_mobius_ratio_in_range(self, elec_suite, ring_adj):
        res = elec_suite.execute_operator_12_closed_loop_audit(ring_adj, N_max=8)
        assert 0.0 <= res["mobius_ratio"] <= 1.0 + 1e-9

    def test_loop_sublaplacian_lambda2_positive(self, elec_suite, ring_adj):
        res = elec_suite.execute_operator_12_closed_loop_audit(ring_adj, N_max=8)
        assert res["lambda_2_loop"] > 0

    def test_kappa_loop_finite(self, elec_suite, ring_adj):
        res = elec_suite.execute_operator_12_closed_loop_audit(ring_adj, N_max=8)
        assert np.isfinite(res["kappa_loop"])

    def test_nmax_too_small_raises(self, elec_suite, ring_adj):
        with pytest.raises(ValueError):
            elec_suite.execute_operator_12_closed_loop_audit(ring_adj, N_max=2)

    def test_invalid_shape_raises(self, elec_suite):
        with pytest.raises(ValueError):
            elec_suite.execute_operator_12_closed_loop_audit(np.zeros((3, 4)))

    def test_op11_op12_chain(self, elec_suite, ring_adj):
        """Op11 输出可直接喂给 Op12"""
        chi = np.array([2.2, 2.55, 3.04, 3.44, 2.55, 2.2])
        r11 = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi)
        r12 = elec_suite.execute_operator_12_closed_loop_audit(r11["A_q"], N_max=8)
        assert r12["n_loops"] >= 1


# ============================================================================
# Op 13 — Chebyshev 矩
# ============================================================================

class TestOp13Chebyshev:
    def test_tau0_equals_one(self, spec_suite):
        """tau_0 = tr(I)/N = 1"""
        L = np.array([[1, -1, 0], [-1, 2, -1], [0, -1, 1]], dtype=float)
        tau, Y, U = spec_suite.execute_operator_13_chebyshev_moments(L, alpha_n=4.0, K=4)
        np.testing.assert_allclose(tau[0], 1.0, atol=1e-12)

    def test_Y_spectrum_in_range(self, spec_suite):
        """Y = 2L/alpha - I, 若 alpha >= lambda_max(L) 则 Y 谱在 [-1, 1]"""
        L = np.diag([1.0, 2.0, 3.0])
        tau, Y, U = spec_suite.execute_operator_13_chebyshev_moments(L, alpha_n=6.0, K=3)
        ev = np.linalg.eigvalsh(Y)
        assert np.all(ev >= -1.0 - 1e-10)
        assert np.all(ev <= 1.0 + 1e-10)

    def test_chebyshev_recurrence(self, spec_suite):
        """T_k(Y) 满足递推: T_{k+1} = 2 Y T_k - T_{k-1}"""
        L = np.diag([1.0, 2.0, 3.0])
        tau, Y, U = spec_suite.execute_operator_13_chebyshev_moments(L, alpha_n=6.0, K=5)
        for k in range(1, 5):
            expected = 2.0 * Y @ U[k] - U[k - 1]
            np.testing.assert_allclose(U[k + 1], expected, atol=1e-10)

    def test_U_shapes(self, spec_suite):
        n = 4
        L = np.eye(n) * 2.0
        tau, Y, U = spec_suite.execute_operator_13_chebyshev_moments(L, alpha_n=4.0, K=3)
        assert len(U) == 4  # K+1
        for u in U:
            assert u.shape == (n, n)

    def test_invalid_alpha_raises(self, spec_suite):
        L = np.eye(3)
        with pytest.raises(ValueError):
            spec_suite.execute_operator_13_chebyshev_moments(L, alpha_n=0.0, K=3)

    def test_invalid_K_raises(self, spec_suite):
        L = np.eye(3)
        with pytest.raises(ValueError):
            spec_suite.execute_operator_13_chebyshev_moments(L, alpha_n=4.0, K=0)

    def test_endogenous_K_bounds(self, spec_suite):
        K, K_res, K_cap = spec_suite.endogenous_K(alpha_n=10.0, lam2=2.0, N=100)
        assert K >= 4
        assert K <= K_cap
        assert K == min(K_res, K_cap)


# ============================================================================
# Op 14 — Hodge 投影
# ============================================================================

class TestOp14Hodge:
    def test_three_components_sum_to_r(self, spec_suite, small_complex):
        D, C = small_complex
        m_g = D.shape[0]
        r = np.random.RandomState(0).randn(m_g)
        res = spec_suite.execute_operator_14_hodge_project(r, D, C)
        recon = res["grad"] + res["harm"] + res["curl"]
        np.testing.assert_allclose(recon, r, atol=1e-8)

    def test_components_orthogonal(self, spec_suite, small_complex):
        D, C = small_complex
        m_g = D.shape[0]
        r = np.random.RandomState(1).randn(m_g)
        res = spec_suite.execute_operator_14_hodge_project(r, D, C)
        g, h, c = res["grad"], res["harm"], res["curl"]
        # grad = D phi, curl = C^T psi, harm 应与两者正交
        assert abs(g @ h) < 1e-8
        assert abs(c @ h) < 1e-8

    def test_harm_is_homology(self, spec_suite, small_complex):
        """调和分量 h 满足 D^T h = 0 且 C h = 0"""
        D, C = small_complex
        m_g = D.shape[0]
        r = np.random.RandomState(2).randn(m_g)
        res = spec_suite.execute_operator_14_hodge_project(r, D, C)
        h = res["harm"]
        np.testing.assert_allclose(D.T @ h, 0.0, atol=1e-8)
        np.testing.assert_allclose(C @ h, 0.0, atol=1e-8)

    def test_grad_is_exact(self, spec_suite, small_complex):
        D, C = small_complex
        r = np.ones(D.shape[0])
        res = spec_suite.execute_operator_14_hodge_project(r, D, C)
        # grad = D phi → 应在 D 的列空间
        g = res["grad"]
        phi = res["phi"]
        np.testing.assert_allclose(D @ phi, g, atol=1e-8)

    def test_shape_mismatch_raises(self, spec_suite, small_complex):
        D, C = small_complex
        r = np.zeros(5)  # 维度不匹配
        with pytest.raises(ValueError):
            spec_suite.execute_operator_14_hodge_project(r, D, C)


# ============================================================================
# Op 15 — 内生牛顿步
# ============================================================================

class TestOp15Newton:
    def test_dM_shape(self, spec_suite, small_complex):
        D, C = small_complex
        m_g = D.shape[0]
        A = spec_suite.build_hodge_A(D, C, lam2=1.0, alpha_n=4.0)
        g = np.ones(m_g)
        h = np.zeros(m_g)
        dM, quad, iters, trust = spec_suite.execute_operator_15_endo_newton_step(g, h, A)
        assert dM.shape == (m_g,)

    def test_quad_nonnegative(self, spec_suite, small_complex):
        D, C = small_complex
        m_g = D.shape[0]
        A = spec_suite.build_hodge_A(D, C, lam2=1.0, alpha_n=4.0)
        g = np.random.RandomState(0).randn(m_g)
        h = np.zeros(m_g)
        dM, quad, iters, trust = spec_suite.execute_operator_15_endo_newton_step(g, h, A)
        assert quad >= 0.0

    def test_trust_in_unit_interval(self, spec_suite, small_complex):
        D, C = small_complex
        m_g = D.shape[0]
        A = spec_suite.build_hodge_A(D, C, lam2=0.5, alpha_n=4.0)
        g = np.random.RandomState(1).randn(m_g) * 100.0
        h = np.zeros(m_g)
        dM, quad, iters, trust = spec_suite.execute_operator_15_endo_newton_step(
            g, h, A, F=1.0, D=D, lam2=0.5
        )
        assert 0.0 < trust <= 1.0 + 1e-12

    def test_trust_region_cap(self, spec_suite, small_complex):
        """信赖域: ||D^T diag(dM) D||_F <= 0.5 * lam2"""
        D, C = small_complex
        m_g = D.shape[0]
        lam2 = 0.5
        A = spec_suite.build_hodge_A(D, C, lam2=lam2, alpha_n=4.0)
        g = np.random.RandomState(2).randn(m_g) * 1000.0
        h = np.zeros(m_g)
        dM, quad, iters, trust = spec_suite.execute_operator_15_endo_newton_step(
            g, h, A, F=1.0, D=D, lam2=lam2
        )
        dL = D.T @ np.diag(dM) @ D
        assert np.linalg.norm(dL, 'fro') <= 0.5 * lam2 + 1e-9

    def test_zero_gradient_gives_zero_dM(self, spec_suite, small_complex):
        D, C = small_complex
        m_g = D.shape[0]
        A = spec_suite.build_hodge_A(D, C, lam2=1.0, alpha_n=4.0)
        g = np.zeros(m_g)
        h = np.zeros(m_g)
        dM, quad, iters, trust = spec_suite.execute_operator_15_endo_newton_step(g, h, A)
        np.testing.assert_allclose(dM, 0.0, atol=1e-12)


# ============================================================================
# Op 16 — Hankel 钳制
# ============================================================================

class TestOp16Hankel:
    def _feasible_moments(self, Kp):
        """构造一个已知可行的矩序列 (Y=0 的幂矩: mu=[1,0,0,...])"""
        return np.zeros(2 * Kp + 3)

    def test_feasible_passes_through(self, spec_suite):
        Kp = 3
        mu_feas = self._feasible_moments(Kp)
        mu_feas[0] = 1.0
        mu_ref = mu_feas.copy()
        mu_clamped, fb, fa, t = spec_suite.execute_operator_16_hankel_clamp(mu_feas, mu_ref, Kp)
        np.testing.assert_allclose(mu_clamped, mu_feas, atol=1e-12)
        assert fb >= -1e-9
        assert t == 1.0

    def test_hankel_feasibility_range(self, spec_suite):
        Kp = 3
        # Y = 0 对应的矩序列全零(除 mu0=1) → Hankel 矩阵 PSD
        mu = np.zeros(2 * Kp + 3)
        mu[0] = 1.0
        feas = spec_suite.hankel_feasibility(mu, Kp)
        assert feas >= -1e-10

    def test_clamp_improves_feasibility(self, spec_suite):
        """钳制后 feas_after >= feas_before"""
        Kp = 3
        mu_ref = np.zeros(2 * Kp + 3)
        mu_ref[0] = 1.0
        # 构造不可行的 mu_new: 大的奇数矩
        mu_new = mu_ref.copy()
        mu_new[1] = 10.0
        mu_new[3] = 10.0
        mu_c, fb, fa, t = spec_suite.execute_operator_16_hankel_clamp(mu_new, mu_ref, Kp)
        assert fa >= fb - 1e-12
        assert 0.0 <= t <= 1.0

    def test_t_star_in_unit_interval(self, spec_suite):
        Kp = 3
        mu_ref = np.zeros(2 * Kp + 3)
        mu_ref[0] = 1.0
        mu_new = mu_ref.copy()
        mu_new[1] = 5.0
        _, _, _, t = spec_suite.execute_operator_16_hankel_clamp(mu_new, mu_ref, Kp)
        assert 0.0 <= t <= 1.0

    def test_clamped_moment_interpolation(self, spec_suite):
        """mu_clamped 应在 mu_ref 和 mu_new 的连线段上"""
        Kp = 3
        mu_ref = np.zeros(2 * Kp + 3)
        mu_ref[0] = 1.0
        mu_new = mu_ref.copy()
        mu_new[1] = 5.0
        mu_c, _, _, t = spec_suite.execute_operator_16_hankel_clamp(mu_new, mu_ref, Kp)
        expected = mu_ref + t * (mu_new - mu_ref)
        np.testing.assert_allclose(mu_c, expected, atol=1e-10)


# ============================================================================
# Op 17 — 审计裁定
# ============================================================================

class TestOp17Audit:
    def test_solved_when_all_below_eps_and_exhausted(self, spec_suite):
        eps = 0.01
        grad = np.zeros(8)
        curl = np.zeros(8)
        harm = np.zeros(8)
        verdict, e, norms, info = spec_suite.execute_operator_17_audit(
            grad, curl, harm, r0_norm=1.0, lam2=0.5, alpha_n=4.0,
            f_prev=1.0, f_now=0.99  # exhausted: |f_now| >= (1-gamma)*|f_prev|
        )
        assert verdict == 'SOLVED'

    def test_continue_when_above_eps(self, spec_suite):
        grad = np.ones(8) * 10.0
        curl = np.zeros(8)
        harm = np.zeros(8)
        verdict, e, norms, info = spec_suite.execute_operator_17_audit(
            grad, curl, harm, r0_norm=1.0, lam2=0.5, alpha_n=4.0
        )
        assert verdict == 'CONTINUE'

    def test_obstruction_when_harm_dominates(self, spec_suite):
        grad = np.zeros(8)
        curl = np.zeros(8)
        harm = np.ones(8) * 10.0  # 调和分量大
        verdict, e, norms, info = spec_suite.execute_operator_17_audit(
            grad, curl, harm, r0_norm=1.0, lam2=0.5, alpha_n=4.0, step_dead=True
        )
        assert verdict == 'OBSTRUCTION'

    def test_eps_formula(self, spec_suite):
        """eps = (lam2 / alpha_n) * r0_norm"""
        grad = np.zeros(8)
        _, eps, _, _ = spec_suite.execute_operator_17_audit(
            grad, grad, grad, r0_norm=2.0, lam2=1.0, alpha_n=4.0
        )
        np.testing.assert_allclose(eps, 0.5, atol=1e-12)

    def test_verdict_in_known_set(self, spec_suite):
        grad = np.zeros(8)
        verdict, _, _, _ = spec_suite.execute_operator_17_audit(
            grad, grad, grad, r0_norm=1.0, lam2=1.0, alpha_n=4.0
        )
        assert verdict in ('SOLVED', 'OBSTRUCTION', 'STALLED', 'CONTINUE')


# ============================================================================
# Op 18 — 同调实现
# ============================================================================

class TestOp18Homological:
    def test_output_keys(self, spec_suite, small_complex):
        D, C = small_complex
        m_g = D.shape[0]
        m = np.ones(m_g)
        res = spec_suite.execute_operator_18_homological_realize(
            D, C, m, residual_fn=lambda x: x
        )
        for key in ("m_star", "h_norm", "h_vec", "d_hom", "budget", "dirichlet"):
            assert key in res

    def test_h_norm_nonnegative(self, spec_suite, small_complex):
        D, C = small_complex
        m = np.ones(D.shape[0])
        res = spec_suite.execute_operator_18_homological_realize(D, C, m, lambda x: x)
        assert res["h_norm"] >= 0.0

    def test_budget_nonnegative(self, spec_suite, small_complex):
        D, C = small_complex
        m = np.ones(D.shape[0])
        res = spec_suite.execute_operator_18_homological_realize(D, C, m, lambda x: x)
        assert res["budget"] >= 0.0

    def test_dirichlet_nonnegative(self, spec_suite, small_complex):
        D, C = small_complex
        m = np.ones(D.shape[0])
        res = spec_suite.execute_operator_18_homological_realize(D, C, m, lambda x: x)
        assert res["dirichlet"] >= 0.0

    def test_d_hom_with_init(self, spec_suite, small_complex):
        D, C = small_complex
        m_g = D.shape[0]
        m = np.ones(m_g)
        res = spec_suite.execute_operator_18_homological_realize(
            D, C, m, lambda x: x, M_init=np.zeros(m_g)
        )
        assert np.isfinite(res["d_hom"])
        assert res["d_hom"] >= 0.0

    def test_m_star_preserved(self, spec_suite, small_complex):
        D, C = small_complex
        m = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0,
                       9.0, 10.0, 11.0, 12.0])
        res = spec_suite.execute_operator_18_homological_realize(D, C, m, lambda x: x)
        np.testing.assert_array_equal(res["m_star"], m)


# ============================================================================
# Op 19 — Z2 电荷通道
# ============================================================================

class TestOp19ChargeChannel:
    def test_ring_invariants(self, chan_suite, ring_adj):
        """6-环: V=6, E=6, c=1, beta1=1 (E-V+c=1)"""
        res = chan_suite.execute_operator_19_z2_charge_channel(ring_adj, polarity="topo")
        assert res["V"] == 6
        assert res["E"] == 6
        assert res["c"] == 1
        assert res["beta1"] == res["E"] - res["V"] + res["c"]
        assert res["beta1"] == 1

    def test_deg_parity(self, chan_suite, ring_adj):
        """deg = beta1 mod 2 ∈ {0, 1}"""
        res = chan_suite.execute_operator_19_z2_charge_channel(ring_adj, polarity="topo")
        assert res["deg"] in (0, 1)
        assert res["deg"] == res["beta1"] % 2

    def test_topo_polarity_trivial(self, chan_suite, ring_adj):
        """topo 极性所有边 s_e=+1 → holonomy 平凡"""
        res = chan_suite.execute_operator_19_z2_charge_channel(ring_adj, polarity="topo")
        assert res["sigma_trivial"] is True
        assert res["sigma_canonical"] == +1.0

    def test_Q_model_formula(self, chan_suite, ring_adj):
        """Q_model = sigma_canonical * deg"""
        res = chan_suite.execute_operator_19_z2_charge_channel(ring_adj, polarity="topo")
        assert abs(res["Q_model"] - res["sigma_canonical"] * res["deg"]) < 1e-12

    def test_spin_polarity_requires_chi(self, chan_suite, ring_adj):
        with pytest.raises(ValueError):
            chan_suite.execute_operator_19_z2_charge_channel(ring_adj, polarity="spin")

    def test_invalid_polarity_raises(self, chan_suite, ring_adj):
        with pytest.raises(ValueError):
            chan_suite.execute_operator_19_z2_charge_channel(ring_adj, polarity="bad")

    def test_invalid_shape_raises(self, chan_suite):
        with pytest.raises(ValueError):
            chan_suite.execute_operator_19_z2_charge_channel(np.zeros((3, 4)))

    def test_bipartite_ring(self, chan_suite, ring_adj):
        """偶环是二分图"""
        res = chan_suite.execute_operator_19_z2_charge_channel(ring_adj, polarity="topo")
        assert res["bipartite"] is True
        assert res["has_odd_cycle"] is False

    def test_triangle_not_bipartite(self, chan_suite):
        A = np.array([[0, 1, 1], [1, 0, 1], [1, 1, 0]], dtype=float)
        res = chan_suite.execute_operator_19_z2_charge_channel(A, polarity="topo")
        assert res["bipartite"] is False
        assert res["has_odd_cycle"] is True
        assert res["beta1"] == 1  # E-V+c = 3-3+1 = 1

    def test_charge_channel_keys(self, chan_suite, ring_adj):
        res = chan_suite.execute_operator_19_z2_charge_channel(ring_adj, polarity="topo")
        keys = chan_suite.charge_channel_keys(res)
        for k in ("z2_beta1", "z2_deg", "z2_bipartite", "z2_sigma_trivial",
                   "z2_Q_model", "z2_channel_type"):
            assert k in keys


# ============================================================================
# 跨算子一致性测试 (端到端)
# ============================================================================

class TestEndToEndChain:
    def test_op11_12_chain_preserves_support(self, elec_suite, ring_adj):
        chi = np.array([2.2, 2.55, 3.04, 3.44, 2.55, 2.2])
        r11 = elec_suite.execute_operator_11_spin_charge_adjacency(ring_adj, chi)
        r12 = elec_suite.execute_operator_12_closed_loop_audit(r11["A_q"], N_max=8)
        # A_q 支撑应包含 A_s 支撑 (rho>=0, wq>=0)
        assert np.all((r11["A_q"] > 0) >= (ring_adj > 0))
        assert r12["n_loops"] == 1

    def test_op14_18_consistency(self, spec_suite, small_complex):
        D, C = small_complex
        m_g = D.shape[0]
        r = np.random.RandomState(3).randn(m_g)
        # Op14 直接分解
        h14 = spec_suite.execute_operator_14_hodge_project(r, D, C)["harm"]
        # Op18 通过 residual_fn 间接分解
        r18 = spec_suite.execute_operator_18_homological_realize(D, C, r, lambda x: r)
        np.testing.assert_allclose(r18["h_vec"], h14, atol=1e-8)

    def test_full_pipeline_op11_to_19(self, elec_suite, spec_suite, chan_suite):
        """完整链路 Op11→12→19 与 Op13→18 不抛异常"""
        n = 8
        A = np.zeros((n, n))
        for i in range(n):
            A[i, (i + 1) % n] = 1.0
            A[(i + 1) % n, i] = 1.0
        chi = np.linspace(2.0, 3.5, n)

        # 电子层
        r11 = elec_suite.execute_operator_11_spin_charge_adjacency(A, chi)
        r12 = elec_suite.execute_operator_12_closed_loop_audit(r11["A_q"], N_max=8)

        # 谱形层 (用小链复形)
        L = np.diag(A.sum(axis=1)) - A
        alpha = float(np.max(np.abs(np.linalg.eigvalsh(L)))) + 1e-6
        tau, Y, U = spec_suite.execute_operator_13_chebyshev_moments(L, alpha, K=4)

        # 电荷通道
        r19 = chan_suite.execute_operator_19_z2_charge_channel(A, polarity="topo")

        assert r11["lambda_2_q"] >= 0
        assert r12["n_loops"] >= 1
        assert abs(tau[0] - 1.0) < 1e-10
        assert r19["sigma_trivial"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
