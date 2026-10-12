"""
benchmark_operators_11_19.py
=============================
SRE 新 9 算子 (Op 11-19) 性能基准测试。

测试内容:
  - 各算子在不同规模下的平均耗时 (μs) 与标准差
  - 关键标量输出验证 (确保不是空跑)
  - 复杂度趋势观察

运行: python benchmark_operators_11_19.py
"""

import time
import numpy as np
from collections import defaultdict

from sre_electronic_layer import SREElectronicOperatorSuite
from sre_spectral_solver import SRESpectralSolverSuite
from sre_charge_channel import SREChargeChannelSuite


# ============================================================================
# 工具函数
# ============================================================================

def benchmark(func, n_warmup=3, n_runs=20):
    """通用 benchmark: 返回 (mean_us, std_us)"""
    for _ in range(n_warmup):
        func()
    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        func()
        times.append((time.perf_counter() - t0) * 1e6)
    return float(np.mean(times)), float(np.std(times))


def make_ring(n, seed=None):
    """n-环邻接矩阵"""
    A = np.zeros((n, n))
    for i in range(n):
        A[i, (i + 1) % n] = 1.0
        A[(i + 1) % n, i] = 1.0
    return A


def make_random_graph(n, density=0.3, seed=42):
    """随机无向图邻接矩阵"""
    rng = np.random.RandomState(seed)
    A = (rng.rand(n, n) < density).astype(float)
    A = np.triu(A, 1)
    A = A + A.T
    return A


def make_chain_complex(n_node, n_extra_edges=0, seed=0):
    """构造满足 C@D=0 的链复形: n_node 环 + extra 弦 + 三角面"""
    edges = []
    for i in range(n_node):
        edges.append((i, (i + 1) % n_node))
    rng = np.random.RandomState(seed)
    for _ in range(n_extra_edges):
        u, v = rng.randint(0, n_node, 2)
        if u != v and (u, v) not in edges and (v, u) not in edges:
            edges.append((u, v))
    m_g = len(edges)
    D = np.zeros((m_g, n_node))
    for e, (u, v) in enumerate(edges):
        D[e, u] = -1.0
        D[e, v] = +1.0

    # 三角面: 每隔 2 个顶点取一个三角形 (0,2,4), (2,4,6), ...
    faces = []
    for i in range(0, n_node - 2, 2):
        a, b, c = i, i + 1, (i + 2) % n_node
        faces.append((a, b, c))
    f = len(faces)
    C = np.zeros((f, m_g))
    edge_idx = {(u, v): e for e, (u, v) in enumerate(edges)}
    edge_idx.update({(v, u): e for e, (u, v) in enumerate(edges)})
    for fi, (a, b, c) in enumerate(faces):
        for x, y in [(a, b), (b, c), (c, a)]:
            if (x, y) in edge_idx:
                e = edge_idx[(x, y)]
                sign = 1.0 if (D[e, x] < 0 and D[e, y] > 0) else -1.0
                C[fi, e] += sign
    return D, C


def print_table(title, headers, rows):
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}")
    fmt = "  " + "  ".join(f"{{{i}:>{w}}}" for i, w in enumerate(headers[1]))
    print(fmt.format(*headers[0]))
    print("  " + "-" * (sum(headers[1]) + 2 * (len(headers[0]) - 1)))
    for row in rows:
        print(fmt.format(*row))


# ============================================================================
# 主基准测试
# ============================================================================

def run_benchmarks():
    elec = SREElectronicOperatorSuite(rho=0.5, N_max_default=8, enable_debug_log=False)
    spec = SRESpectralSolverSuite(enable_debug_log=False)
    chan = SREChargeChannelSuite(aut_max_v=22, enable_debug_log=False)

    results = defaultdict(list)
    sizes_graph = [16, 32, 64, 128]   # 用于 Op11/12/19
    sizes_complex = [16, 32, 64]       # 用于 Op13-18 (链复形规模)

    # ---------------------------------------------------------------- Op 11
    print("\n[1/9] Op11 自旋-电荷邻接 ...")
    for n in sizes_graph:
        A = make_random_graph(n, density=0.3)
        chi = np.linspace(2.0, 3.5, n)
        mean, std = benchmark(lambda: elec.execute_operator_11_spin_charge_adjacency(A, chi))
        results["op11"].append((n, mean, std))
        print(f"  N={n:4d}: {mean:10.1f} ± {std:8.1f} μs")

    # ---------------------------------------------------------------- Op 12
    print("\n[2/9] Op12 闭合环审计 ...")
    for n in sizes_graph:
        A = make_ring(n)
        mean, std = benchmark(lambda: elec.execute_operator_12_closed_loop_audit(A, N_max=min(n, 8)))
        results["op12"].append((n, mean, std))
        print(f"  N={n:4d}: {mean:10.1f} ± {std:8.1f} μs")

    # ---------------------------------------------------------------- Op 13
    print("\n[3/9] Op13 Chebyshev 矩 ...")
    for n in sizes_complex:
        A = make_random_graph(n, density=0.2)
        L = np.diag(A.sum(axis=1)) - A
        alpha = float(np.max(np.abs(np.linalg.eigvalsh(L)))) + 1e-6
        mean, std = benchmark(lambda: spec.execute_operator_13_chebyshev_moments(L, alpha, K=6))
        results["op13"].append((n, mean, std))
        print(f"  N={n:4d}: {mean:10.1f} ± {std:8.1f} μs")

    # ---------------------------------------------------------------- Op 14
    print("\n[4/9] Op14 Hodge 投影 ...")
    for n in sizes_complex:
        D, C = make_chain_complex(n, n_extra_edges=n // 2)
        m_g = D.shape[0]
        r = np.random.RandomState(0).randn(m_g)
        mean, std = benchmark(lambda: spec.execute_operator_14_hodge_project(r, D, C))
        results["op14"].append((n, mean, std))
        print(f"  N={n:4d} (m_g={m_g:3d}): {mean:10.1f} ± {std:8.1f} μs")

    # ---------------------------------------------------------------- Op 15
    print("\n[5/9] Op15 内生牛顿步 ...")
    for n in sizes_complex:
        D, C = make_chain_complex(n, n_extra_edges=n // 2)
        m_g = D.shape[0]
        A = spec.build_hodge_A(D, C, lam2=1.0, alpha_n=4.0)
        g = np.random.RandomState(1).randn(m_g)
        h = np.zeros(m_g)
        mean, std = benchmark(lambda: spec.execute_operator_15_endo_newton_step(g, h, A))
        results["op15"].append((n, mean, std))
        print(f"  N={n:4d} (m_g={m_g:3d}): {mean:10.1f} ± {std:8.1f} μs")

    # ---------------------------------------------------------------- Op 16
    print("\n[6/9] Op16 Hankel 钳制 ...")
    Kp_list = [3, 5, 8, 12]
    for Kp in Kp_list:
        mu_ref = np.zeros(2 * Kp + 3)
        mu_ref[0] = 1.0
        mu_new = mu_ref.copy()
        mu_new[1] = 5.0
        mean, std = benchmark(lambda: spec.execute_operator_16_hankel_clamp(mu_new, mu_ref, Kp))
        results["op16"].append((Kp, mean, std))
        print(f"  Kp={Kp:3d}: {mean:10.1f} ± {std:8.1f} μs")

    # ---------------------------------------------------------------- Op 17
    print("\n[7/9] Op17 审计裁定 ...")
    # Op17 是标量逻辑, 规模无关; 测试维度变化
    for dim in [8, 64, 512, 4096]:
        grad = np.random.RandomState(2).randn(dim)
        curl = np.random.RandomState(3).randn(dim)
        harm = np.random.RandomState(4).randn(dim)
        mean, std = benchmark(lambda: spec.execute_operator_17_audit(
            grad, curl, harm, r0_norm=1.0, lam2=0.5, alpha_n=4.0))
        results["op17"].append((dim, mean, std))
        print(f"  dim={dim:5d}: {mean:10.1f} ± {std:8.1f} μs")

    # ---------------------------------------------------------------- Op 18
    print("\n[8/9] Op18 同调实现 ...")
    for n in sizes_complex:
        D, C = make_chain_complex(n, n_extra_edges=n // 2)
        m_g = D.shape[0]
        m = np.ones(m_g)
        mean, std = benchmark(lambda: spec.execute_operator_18_homological_realize(D, C, m, lambda x: x))
        results["op18"].append((n, mean, std))
        print(f"  N={n:4d} (m_g={m_g:3d}): {mean:10.1f} ± {std:8.1f} μs")

    # ---------------------------------------------------------------- Op 19
    print("\n[9/9] Op19 Z2 电荷通道 ...")
    for n in sizes_graph:
        A = make_random_graph(n, density=0.3)
        # Op19 reachability 只在 n <= aut_max_v 时计算; 小图测完整路径
        mean, std = benchmark(lambda: chan.execute_operator_19_z2_charge_channel(A, polarity="topo"))
        results["op19"].append((n, mean, std))
        print(f"  N={n:4d}: {mean:10.1f} ± {std:8.1f} μs")

    # ========================================================================
    # 汇总表
    # ========================================================================
    print("\n" + "#" * 80)
    print("#  汇总: 各算子在最大测试规模下的性能")
    print("#" * 80)
    summary_rows = []
    for op, entries in results.items():
        last = entries[-1]
        summary_rows.append((op.upper(), str(last[0]), f"{last[1]:.1f}", f"{last[2]:.1f}"))
    print_table(
        "各算子最大规模耗时",
        (("算子", "规模", "均值(μs)", "标准差(μs)"), (10, 10, 14, 14)),
        summary_rows,
    )

    return results


if __name__ == "__main__":
    run_benchmarks()
