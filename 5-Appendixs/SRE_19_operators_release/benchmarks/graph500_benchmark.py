# graph500_benchmark.py
# Graph500 标准测试: C++ 算子 vs Python 算子 性能对比
import os
import sys
import ctypes
import time
import json
import numpy as np
from collections import defaultdict

# 加载 Python 模块
from sre_foundational_layer import SREFoundationalOperatorSuite
from sre_transport_alignment import SRETransportAlignmentSuite
from sre_commercial_core import SRECommercialCoreSuite

# 加载 C++ DLL
ROOT = os.path.dirname(os.path.abspath(__file__))
DLL_PATH = os.path.join(ROOT, "cpp_lib", "build", "Release", "sre_operator.dll")
dll = ctypes.CDLL(DLL_PATH)

# ============================================================================
# 配置 C++ 函数签名
# ============================================================================
def setup_dll_signatures():
    # ---- 稠密版 (原始) ----
    dll.sre_op4_degree.restype = ctypes.c_int
    dll.sre_op4_degree.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int,
                                    ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                    ctypes.POINTER(ctypes.c_double)]

    # ---- 朴素稠密版 (O(N³) 三重循环, 仅用于基准对比) ----
    dll.sre_op4_degree_naive.restype = ctypes.c_int
    dll.sre_op4_degree_naive.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int,
                                          ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                          ctypes.POINTER(ctypes.c_double)]

    dll.sre_op6_splicing.restype = ctypes.c_int
    dll.sre_op6_splicing.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, ctypes.c_int, ctypes.c_double,
                                      ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                      ctypes.POINTER(ctypes.c_double)]

    # ---- CSR 稀疏版 (HPC 优化) ----
    dll.sre_op4_degree_csr.restype = ctypes.c_int
    dll.sre_op4_degree_csr.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                        ctypes.POINTER(ctypes.c_double), ctypes.c_int,
                                        ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                        ctypes.POINTER(ctypes.c_double)]

    dll.sre_op6_splicing_csr.restype = ctypes.c_int
    dll.sre_op6_splicing_csr.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                          ctypes.POINTER(ctypes.c_double), ctypes.c_int,
                                          ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_double,
                                          ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double),
                                          ctypes.POINTER(ctypes.c_double)]

    # ---- CSR 辅助函数 ----
    dll.sre_csr_from_edges.restype = ctypes.c_int
    dll.sre_csr_from_edges.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int, ctypes.c_int,
                                        ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),
                                        ctypes.POINTER(ctypes.POINTER(ctypes.c_int)),
                                        ctypes.POINTER(ctypes.POINTER(ctypes.c_double)),
                                        ctypes.POINTER(ctypes.c_int)]

    dll.sre_csr_free.restype = None
    dll.sre_csr_free.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                  ctypes.POINTER(ctypes.c_double)]

    # ---- 其他算子 (与稠密/稀疏无关) ----
    dll.sre_op7_potential.restype = ctypes.c_int
    dll.sre_op7_potential.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_double),
                                       ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)]

    dll.sre_op9_stitching.restype = ctypes.c_int
    dll.sre_op9_stitching.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_double),
                                       ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                       ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_double)]

    dll.sre_op10_firewall.restype = ctypes.c_int
    dll.sre_op10_firewall.argtypes = [ctypes.c_int, ctypes.c_int,
                                       ctypes.POINTER(ctypes.c_double), ctypes.c_int,
                                       ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                       ctypes.c_double,
                                       ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int),
                                       ctypes.POINTER(ctypes.c_double)]

    dll.sre_op10_firewall_scalar.restype = ctypes.c_int
    dll.sre_op10_firewall_scalar.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                              ctypes.c_int, ctypes.c_double, ctypes.c_double,
                                              ctypes.c_double, ctypes.c_double,
                                              ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int),
                                              ctypes.POINTER(ctypes.c_double)]

setup_dll_signatures()

# ============================================================================
# Graph500 RMAT 图生成器 (简化实现)
# ============================================================================
def generate_rmat_graph(scale, edge_factor, seed=42):
    """
    生成符合 Graph500 标准的 RMAT (Recursive Matrix) 图。
    返回: (num_vertices, edge_list)
    """
    rng = np.random.RandomState(seed)
    n = 2**scale
    m = n * edge_factor

    # RMAT 参数 (a + b + c + d = 1, Graph500 默认 a=0.5)
    a, b, c = 0.57, 0.19, 0.19
    d = 1.0 - a - b - c

    edges = []
    for _ in range(m):
        # RMAT 递归细分
        u, v = 0, 0
        size = n // 2
        while size >= 1:
            r = rng.random()
            if r < a:
                pass  # 左上
            elif r < a + b:
                u += size  # 左下
            elif r < a + b + c:
                v += size  # 右上
            else:
                u += size
                v += size  # 右下
            size //= 2
        if u != v:  # 避免自环
            edges.append((u, v))
    return n, edges

def build_laplacian(n, edges):
    """从边列表构建拉普拉斯矩阵 L = D - A"""
    A = np.zeros((n, n), dtype=np.float64)
    for u, v in edges:
        if u < n and v < n:
            A[u, v] += 1
            A[v, u] += 1
    D = np.diag(A.sum(axis=1))
    L = D - A
    return L

# ============================================================================
# 基准测试核心
# ============================================================================
def benchmark_pipeline_python(L, py_p1, py_p2, py_p3):
    """Python 算子流水线: Op4 -> Op6 -> Op7 -> Op9 -> Op10"""
    n = L.shape[0]
    times = {}

    # Op4: 度规权重
    t0 = time.perf_counter()
    W_e = py_p1.execute_operator_4_degree(L)
    times['Op4'] = time.perf_counter() - t0

    # 构造 B_co 和 E_s (模拟图上的局域操作)
    M = min(10, n)
    Mk = min(8, n)
    B_co = np.random.randn(M, Mk)
    E_s = np.random.randn(Mk)

    # Op6: 谱拼接 (全图)
    t0 = time.perf_counter()
    if n >= 4:
        r6 = py_p2.execute_operator_6_splicing(L, num_groups=min(n//4, 4), k_rank=4, overlap_size=2)
    else:
        r6 = py_p2.execute_operator_6_splicing(L, num_groups=1, k_rank=2, overlap_size=0)
    times['Op6'] = time.perf_counter() - t0

    # Op7: 伴随滤波
    t0 = time.perf_counter()
    g7, bh7 = py_p3.evaluate_operator_7_potential(B_co, E_s)
    times['Op7'] = time.perf_counter() - t0

    # Op9: 缝合
    t0 = time.perf_counter()
    Nf = min(10, n)
    E_rows = min(15, n)
    d2 = np.random.randn(E_rows, Nf)
    d1 = np.random.randn(Nf, E_rows)
    # Need to ensure Nf and E_rows match
    Nf = min(Nf, E_rows)
    E_rows = Nf
    d2 = np.random.randn(E_rows, Nf)
    d1 = np.random.randn(Nf, E_rows)
    S9 = py_p3.execute_operator_9_stitching(d2, d1, Nf, lambda_2=0.5)
    times['Op9'] = time.perf_counter() - t0

    # Op10: 防火墙
    t0 = time.perf_counter()
    u, vf = 0, min(1, n-1)
    L_plus = np.eye(n) + 0.1 * np.random.randn(n, n)
    L_plus = (L_plus + L_plus.T) / 2
    r10 = py_p3.execute_operator_10_firewall(u, vf, L_plus, is_bridge=False)
    times['Op10'] = time.perf_counter() - t0

    return times

def build_csr_from_edges(n, edges):
    """
    从边表构建 CSR (Compressed Sparse Row) 格式。
    edges: list of (u, v) 无向边
    返回: (row_ptr, col_idx, values) 均为 numpy 数组 (int32 / float64)
    """
    from collections import defaultdict
    row_dict = defaultdict(list)
    for u, v in edges:
        row_dict[u].append((v, 1.0))
        row_dict[v].append((u, 1.0))

    # 构建拉普拉斯: L = D - A, 对角线 = 度数, 非对角线 = -1 (边权重为1时)
    row_ptr = np.zeros(n + 1, dtype=np.int32)
    col_idx_list = []
    values_list = []

    for i in range(n):
        neighbors = row_dict.get(i, [])
        # 对角线: 度数
        degree = len(neighbors)
        # 先加对角线
        col_idx_list.append(i)
        values_list.append(float(degree))
        # 加邻居 (负值)
        for (j, w) in neighbors:
            col_idx_list.append(j)
            values_list.append(-float(w))
        row_ptr[i + 1] = row_ptr[i] + 1 + len(neighbors)

    col_idx = np.array(col_idx_list, dtype=np.int32)
    values = np.array(values_list, dtype=np.float64)
    return row_ptr, col_idx, values


def benchmark_pipeline_cpp_dense(L):
    """C++ 稠密版算子流水线 (原始实现) — Op4+Op6 使用稠密矩阵"""
    n = L.shape[0]
    times = {}
    L_c = L.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    # Op4 稠密版
    W4 = np.zeros((n, n))
    W4_c = W4.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    t0 = time.perf_counter()
    dll.sre_op4_degree(L_c, n, 0.5, 0.8, 1e-6, W4_c)
    times['Op4'] = time.perf_counter() - t0

    # Op6 稠密版
    l2_6 = ctypes.c_double()
    an_6 = ctypes.c_double()
    mr_6 = ctypes.c_double()
    t0 = time.perf_counter()
    ng = min(n // 4, 4)
    if ng < 1:
        ng = 1
    dll.sre_op6_splicing(L_c, n, ng, min(4, n - 1), 2, 1e-2,
                         ctypes.byref(l2_6), ctypes.byref(an_6), ctypes.byref(mr_6))
    times['Op6'] = time.perf_counter() - t0

    # Op7/Op9/Op10 (稠密版, 与稀疏版相同)
    for name, fn in [('Op7', benchmark_op7), ('Op9', benchmark_op9), ('Op10', benchmark_op10)]:
        times[name] = fn(n)

    return times


def benchmark_pipeline_cpp_csr(row_ptr, col_idx, values, n):
    """C++ CSR 稀疏版算子流水线 (HPC 优化) — Op4+Op6 使用 CSR 格式"""
    times = {}

    rp_c = row_ptr.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
    ci_c = col_idx.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
    va_c = values.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    # Op4 CSR 版
    W4 = np.zeros((n, n))
    W4_c = W4.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    t0 = time.perf_counter()
    dll.sre_op4_degree_csr(rp_c, ci_c, va_c, n, 0.5, 0.8, 1e-6, W4_c)
    times['Op4'] = time.perf_counter() - t0

    # Op6 CSR 版 (矩阵free Lanczos)
    l2_6 = ctypes.c_double()
    an_6 = ctypes.c_double()
    mr_6 = ctypes.c_double()
    t0 = time.perf_counter()
    ng = min(n // 4, 4)
    if ng < 1:
        ng = 1
    dll.sre_op6_splicing_csr(rp_c, ci_c, va_c, n, ng, min(4, n - 1), 2, 1e-2,
                              ctypes.byref(l2_6), ctypes.byref(an_6), ctypes.byref(mr_6))
    times['Op6'] = time.perf_counter() - t0

    # Op7/Op9/Op10 (与稠密版相同)
    for name, fn in [('Op7', benchmark_op7), ('Op9', benchmark_op9), ('Op10', benchmark_op10)]:
        times[name] = fn(n)

    return times


# ---- 辅助算子基准 (与稠密/稀疏无关) ----

def benchmark_op7(n):
    M = min(10, n)
    Mk = min(8, n)
    B_co = np.random.randn(M, Mk)
    E_s = np.random.randn(Mk)
    g7 = np.zeros(Mk)
    bh7 = np.zeros(M)
    t0 = time.perf_counter()
    dll.sre_op7_potential(
        B_co.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        M, Mk,
        E_s.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        g7.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        bh7.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    )
    return time.perf_counter() - t0


def benchmark_op9(n):
    Nf = min(10, n)
    E_rows = min(15, n)
    Nf = min(Nf, E_rows)
    E_rows = Nf
    d2 = np.random.randn(E_rows, Nf)
    d1 = np.random.randn(Nf, E_rows)
    S9 = np.zeros((Nf, Nf))
    t0 = time.perf_counter()
    dll.sre_op9_stitching(
        d2.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        E_rows, Nf,
        d1.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        0.5, 1.2, 1e-5, 1e-16, 100, 20,
        S9.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    )
    return time.perf_counter() - t0


def benchmark_op10(n):
    L_plus = np.eye(n) + 0.1 * np.random.randn(n, n)
    L_plus = (L_plus + L_plus.T) / 2
    z10 = ctypes.c_double()
    a10 = ctypes.c_int()
    p10 = ctypes.c_double()
    t0 = time.perf_counter()
    dll.sre_op10_firewall(
        0, min(1, n - 1),
        L_plus.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
        n, 0,
        0.9999999999999999, -500.0, 500.0, 1e-16,
        ctypes.byref(z10), ctypes.byref(a10), ctypes.byref(p10)
    )
    return time.perf_counter() - t0


# 保留向后兼容
def benchmark_pipeline_cpp(L):
    """C++ 稠密版算子流水线 (向后兼容)"""
    return benchmark_pipeline_cpp_dense(L)


# ============================================================================
# 朴素稠密版 Op4 (O(N³) 三重循环) — 用于真实基准对比
# ============================================================================
def benchmark_op4_naive(L):
    """Op4 朴素稠密版: O(N³) 三重循环矩阵乘法"""
    n = L.shape[0]
    L_c = L.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    W4 = np.zeros((n, n))
    W4_c = W4.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    t0 = time.perf_counter()
    dll.sre_op4_degree_naive(L_c, n, 0.5, 0.8, 1e-6, W4_c)
    return time.perf_counter() - t0


def benchmark_op4_dense(L):
    """Op4 稠密版 (实际为 CSR 包装器): dense→CSR→CSR 实现"""
    n = L.shape[0]
    L_c = L.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    W4 = np.zeros((n, n))
    W4_c = W4.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    t0 = time.perf_counter()
    dll.sre_op4_degree(L_c, n, 0.5, 0.8, 1e-6, W4_c)
    return time.perf_counter() - t0


def benchmark_op4_csr(row_ptr, col_idx, values, n):
    """Op4 CSR 稀疏版: SpGEMM O(N·K₀²)"""
    rp_c = row_ptr.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
    ci_c = col_idx.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
    va_c = values.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    W4 = np.zeros((n, n))
    W4_c = W4.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    t0 = time.perf_counter()
    dll.sre_op4_degree_csr(rp_c, ci_c, va_c, n, 0.5, 0.8, 1e-6, W4_c)
    return time.perf_counter() - t0


def benchmark_op6_dense(L):
    """Op6 稠密版 (实际为 CSR 包装器): dense→CSR→CSR 实现"""
    n = L.shape[0]
    L_c = L.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    l2 = ctypes.c_double()
    an = ctypes.c_double()
    mr = ctypes.c_double()
    ng = min(n // 4, 4)
    if ng < 1:
        ng = 1
    t0 = time.perf_counter()
    dll.sre_op6_splicing(L_c, n, ng, min(4, n - 1), 2, 1e-2,
                          ctypes.byref(l2), ctypes.byref(an), ctypes.byref(mr))
    return time.perf_counter() - t0


def benchmark_op6_csr(row_ptr, col_idx, values, n):
    """Op6 CSR 矩阵free版: Lanczos 迭代"""
    rp_c = row_ptr.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
    ci_c = col_idx.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
    va_c = values.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    l2 = ctypes.c_double()
    an = ctypes.c_double()
    mr = ctypes.c_double()
    ng = min(n // 4, 4)
    if ng < 1:
        ng = 1
    t0 = time.perf_counter()
    dll.sre_op6_splicing_csr(rp_c, ci_c, va_c, n, ng, min(4, n - 1), 2, 1e-2,
                              ctypes.byref(l2), ctypes.byref(an), ctypes.byref(mr))
    return time.perf_counter() - t0

# ============================================================================
# 主基准测试流程
# ============================================================================
def main():
    print("=" * 80)
    print("Graph500 标准测试: SRE 算子 HPC 优化验证")
    print("=" * 80)

    edge_factor = 16
    iterations = 3

    # ---- 小规模 (Scale 6-10): Python vs C++ dense 对比 ----
    small_scales = [6, 8, 10]
    py_p1 = SREFoundationalOperatorSuite(
        beta_sre=1.2, lambda_0=0.9, lambda_2=0.5, alpha_n=0.8,
        epsilon_topo=1e-6, max_n_dimension=10000, enable_debug_log=False
    )
    py_p2 = SRETransportAlignmentSuite(
        c_max=3.0, delta_flt=1e-16, w_min=1e-12, rr_tol_warn=1e-2,
        beta_a=2.0, beta_b=5.0, kde_sample_points=1000, noise_std=0.05,
        enable_debug_log=False
    )
    py_p3 = SRECommercialCoreSuite(
        num_local_edges=8, k0_horizon=20, delta_flt=1e-16, lambda_base=0.5,
        smooth_alpha=0.25, exp_clip_min=-500.0, exp_clip_max=500.0,
        eig_null_tol=1e-5, gamma_flow=0.1, p_mu_scale=1.2,
        op7_tanh_coeff=0.5, op7_grad_coeff=0.1,
        op8_ed_scale1=1.2, op8_ed_scale2=0.1,
        low_rank_dim_threshold=100, low_rank_k_evals=20,
        atol_convergence=1e-12, enable_debug_log=False
    )

    results_small = []
    for scale in small_scales:
        n = 2**scale
        print(f"\n--- Scale={scale} (vertices={n}) ---")
        print(f"  Generating RMAT graph...", end=" ", flush=True)
        num_verts, edges = generate_rmat_graph(scale, edge_factor, seed=scale * 100)
        print(f"edges={len(edges)}")

        print(f"  Building Laplacian...", end=" ", flush=True)
        L = build_laplacian(num_verts, edges)
        print(f"done. Shape={L.shape}")

        # C++ 稠密版
        print(f"  Running C++ dense ({iterations} iters)...", end=" ", flush=True)
        cpp_dense_list = []
        for _ in range(iterations):
            cpp_dense_list.append(benchmark_pipeline_cpp_dense(L))
        cpp_dense_avg = {k: np.mean([t[k] for t in cpp_dense_list]) for k in cpp_dense_list[0]}
        print("done.")

        # Python 版
        print(f"  Running Python ({iterations} iters)...", end=" ", flush=True)
        py_list = []
        for _ in range(iterations):
            py_list.append(benchmark_pipeline_python(L, py_p1, py_p2, py_p3))
        py_avg = {k: np.mean([t[k] for t in py_list]) for k in py_list[0]}
        print("done.")

        total_py = sum(py_avg.values())
        total_cpp = sum(cpp_dense_avg.values())
        speedup_total = total_py / total_cpp if total_cpp > 0 else float('inf')

        print(f"\n  {'算子':<12s} {'Python(s)':>12s} {'C++ dense(s)':>12s} {'加速比':>10s}")
        print(f"  {'-'*46}")
        for op in cpp_dense_avg:
            sp = py_avg[op] / cpp_dense_avg[op] if cpp_dense_avg[op] > 0 else float('inf')
            print(f"  {op:<12s} {py_avg[op]:>12.4f} {cpp_dense_avg[op]:>12.4f} {sp:>9.2f}x")
        print(f"  {'-'*46}")
        print(f"  {'TOTAL':<12s} {total_py:>12.4f} {total_cpp:>12.4f} {speedup_total:>9.2f}x")
        print(f"  单节点耗时: {total_cpp/n*1e6:.2f} μs/vertex")

        results_small.append({
            'scale': scale, 'vertices': n,
            'python_time': total_py, 'cpp_dense_time': total_cpp,
            'speedup_vs_python': speedup_total,
            'per_node_us': total_cpp / n * 1e6,
            'per_op_py': py_avg, 'per_op_cpp': cpp_dense_avg
        })

    # ---- Scale 12: 原始 C++ dense vs 优化后 C++ CSR (核心验证) ----
    print("\n" + "=" * 80)
    print("Scale 12 (4096 节点) HPC 优化验证")
    print("=" * 80)

    scale = 12
    n = 2**scale  # 4096
    print(f"\n--- Scale={scale} (vertices={n}) ---")
    print(f"  Generating RMAT graph...", end=" ", flush=True)
    num_verts, edges = generate_rmat_graph(scale, edge_factor, seed=scale * 100)
    print(f"edges={len(edges)}")

    print(f"  Building Laplacian (dense, {n*n*8/1024/1024:.1f} MB)...", end=" ", flush=True)
    L = build_laplacian(num_verts, edges)
    print(f"done.")

    print(f"  Building CSR format...", end=" ", flush=True)
    row_ptr, col_idx, values = build_csr_from_edges(n, edges)
    nnz = len(values)
    print(f"done. nnz={nnz}, CSR 内存={nnz*8/1024:.1f} KB")

    # ---- Phase A: 原始 C++ 稠密版 (基准) ----
    print(f"\n  [A] 原始 C++ 稠密版 (O(N³) Op4 + O(N²) Op6)...")
    print(f"      (这可能需要 10-30 秒, 请耐心等待...)")
    dense_times_list = []
    for i in range(iterations):
        print(f"      迭代 {i+1}/{iterations}...", end=" ", flush=True)
        t0_iter = time.perf_counter()
        dense_times_list.append(benchmark_pipeline_cpp_dense(L))
        elapsed = time.perf_counter() - t0_iter
        print(f" {elapsed:.2f}s")
    dense_avg = {k: np.mean([t[k] for t in dense_times_list]) for k in dense_times_list[0]}

    # ---- Phase B: 优化后 C++ CSR 版 ----
    print(f"\n  [B] 优化后 C++ CSR 版 (SpGEMM Op4 + Matrix-free Lanczos Op6)...")
    csr_times_list = []
    for i in range(iterations):
        print(f"      迭代 {i+1}/{iterations}...", end=" ", flush=True)
        t0_iter = time.perf_counter()
        csr_times_list.append(benchmark_pipeline_cpp_csr(row_ptr, col_idx, values, n))
        elapsed = time.perf_counter() - t0_iter
        print(f" {elapsed:.2f}s")
    csr_avg = {k: np.mean([t[k] for t in csr_times_list]) for k in csr_times_list[0]}

    # ---- 速度对比 ----
    total_dense = sum(dense_avg.values())
    total_csr = sum(csr_avg.values())
    speedup_total = total_dense / total_csr if total_csr > 0 else float('inf')

    print(f"\n  {'='*70}")
    print(f"  Scale 12 (4096 节点) 性能对比报告")
    print(f"  {'='*70}")
    print(f"\n  {'算子':<12s} {'原始稠密(s)':>12s} {'优化CSR(s)':>12s} {'加速比':>10s}")
    print(f"  {'-'*48}")
    for op in dense_avg:
        sp = dense_avg[op] / csr_avg[op] if csr_avg[op] > 0 else float('inf')
        print(f"  {op:<12s} {dense_avg[op]:>12.4f} {csr_avg[op]:>12.4f} {sp:>9.2f}x")
    print(f"  {'-'*48}")
    print(f"  {'TOTAL':<12s} {total_dense:>12.4f} {total_csr:>12.4f} {speedup_total:>9.2f}x")

    per_node_dense = total_dense / n * 1e6
    per_node_csr = total_csr / n * 1e6
    print(f"\n  单节点耗时 (原始): {per_node_dense:.2f} μs/vertex")
    print(f"  单节点耗时 (优化): {per_node_csr:.2f} μs/vertex")
    print(f"  单节点加速比:     {per_node_dense/per_node_csr:.1f}x")

    # Op4/Op6 专项分析
    op4_speedup = dense_avg['Op4'] / csr_avg['Op4'] if csr_avg['Op4'] > 0 else float('inf')
    op6_speedup = dense_avg['Op6'] / csr_avg['Op6'] if csr_avg['Op6'] > 0 else float('inf')
    print(f"\n  Op4 专项加速比: {op4_speedup:.1f}x (稠密 O(N³) → CSR SpGEMM O(N·K₀²))")
    print(f"  Op6 专项加速比: {op6_speedup:.1f}x (稠密特征分解 → 矩阵free Lanczos)")

    if speedup_total >= 44.0:
        print(f"\n  ✅ 结论: Scale 12 加速比 {speedup_total:.1f}x >= 44x 目标!")
    else:
        print(f"\n  ⚠️  结论: Scale 12 加速比 {speedup_total:.1f}x 未达 44x 目标 (但仍有显著提升)")

    # ---- 汇总 ----
    print("\n" + "=" * 80)
    print("全程可扩展性分析")
    print("=" * 80)
    print(f"\n{'Scale':<8s} {'Vertices':>10s} {'C++ dense(s)':>12s} {'C++ CSR(s)':>12s} {'加速比':>10s} {'μs/节点':>12s}")
    print(f"{'-'*68}")
    for r in results_small:
        print(f"{r['scale']:<8d} {r['vertices']:>10d} {r['cpp_dense_time']:>12.4f} {'---':>12s} {r['speedup_vs_python']:>9.2f}x {r['per_node_us']:>11.2f}")

    print(f"{12:<8d} {n:>10d} {total_dense:>12.4f} {total_csr:>12.4f} {speedup_total:>9.2f}x {per_node_csr:>11.2f}")

    # 保存结果
    output_file = os.path.join(ROOT, "graph500_results.json")
    all_results = {
        'small_scales': results_small,
        'scale_12': {
            'scale': 12, 'vertices': n,
            'dense_time': total_dense, 'csr_time': total_csr,
            'speedup': speedup_total,
            'per_node_dense_us': per_node_dense,
            'per_node_csr_us': per_node_csr,
            'op4_speedup': op4_speedup,
            'op6_speedup': op6_speedup,
            'dense_per_op': dense_avg,
            'csr_per_op': csr_avg
        }
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n详细结果已保存至: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
