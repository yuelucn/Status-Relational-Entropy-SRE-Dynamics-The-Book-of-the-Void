/* sre_graph500_main.c
 * Graph500 v2.1 官方标准格式 + SRE 全套 19 算子扩展 Kernel
 *
 * 编译:
 *   gcc -O3 -fopenmp -Wall -Wextra -DGRAPH_GENERATOR_OMP \
 *       sre_graph500_main.c sre_csr_kernel.c \
 *       ../generator/graph_generator.c ../generator/make_graph.c \
 *       ../generator/splittable_mrg.c ../generator/utils.c \
 *       -o sre_graph500.exe -lm
 *
 * 运行:
 *   ./sre_graph500.exe [SCALE] [edgefactor] [NBFS]
 *     SCALE       = log2(顶点数), 默认 12
 *     edgefactor  = 边/顶点比, 默认 16
 *     NBFS        = 采样轮数 (与官方 num_bfs_roots 对齐), 默认 64
 *
 * 输出: 严格按 Graph500 官方字段名, 兼容 octave/verify.m 与官方 parse 脚本.
 *       SRE 扩展段以 '# SRE Extended Kernel' 分隔, 跑分脚本自动忽略.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <stdint.h>

#include "../generator/make_graph.h"
#include "../generator/graph_generator.h"
#include "sre_csr_kernel.h"

#ifdef _OPENMP
#include <omp.h>
#else
static double omp_get_wtime(void) { return (double)clock() / CLOCKS_PER_SEC; }
static int omp_get_max_threads(void) { return 1; }
#endif

/* ============================================================================
 * 从 Graph500 边表构建 CSR 拉普拉斯矩阵 (与官方 make_graph_data_structure 对齐)
 * ============================================================================ */
static void build_csr_laplacian(
    const packed_edge* edges, int64_t nedges,
    int64_t nverts,
    int** row_ptr_out, int** col_idx_out, double** values_out, int* n_out
) {
    int n = (int)nverts;
    *n_out = n;

    /* 统计每行非零数 (度数 + 1 对角线) */
    int* degree = (int*)calloc((size_t)n, sizeof(int));
    for (int64_t i = 0; i < nedges; i++) {
        int64_t v0 = get_v0_from_edge(&edges[i]);
        int64_t v1 = get_v1_from_edge(&edges[i]);
        if (v0 == v1) continue;
        if (v0 >= 0 && v0 < n) degree[v0]++;
        if (v1 >= 0 && v1 < n) degree[v1]++;
    }

    int* row_ptr = (int*)malloc((size_t)(n + 1) * sizeof(int));
    row_ptr[0] = 0;
    for (int i = 0; i < n; i++)
        row_ptr[i + 1] = row_ptr[i] + degree[i] + 1;  /* +1 对角线 */

    int nnz = row_ptr[n];
    int* col_idx = (int*)malloc((size_t)nnz * sizeof(int));
    double* values = (double*)malloc((size_t)nnz * sizeof(double));

    int* pos = (int*)malloc((size_t)n * sizeof(int));
    for (int i = 0; i < n; i++) pos[i] = row_ptr[i];

    /* 对角线 = degree, 邻居 = -1 */
    for (int i = 0; i < n; i++) {
        col_idx[pos[i]] = i;
        values[pos[i]] = (double)degree[i];
        pos[i]++;
    }
    for (int64_t i = 0; i < nedges; i++) {
        int64_t v0 = get_v0_from_edge(&edges[i]);
        int64_t v1 = get_v1_from_edge(&edges[i]);
        if (v0 == v1) continue;
        if (v0 >= 0 && v0 < n && v1 >= 0 && v1 < n) {
            col_idx[pos[v0]] = (int)v1;  values[pos[v0]] = -1.0;  pos[v0]++;
            col_idx[pos[v1]] = (int)v0;  values[pos[v1]] = -1.0;  pos[v1]++;
        }
    }

    free(degree); free(pos);
    *row_ptr_out = row_ptr;
    *col_idx_out = col_idx;
    *values_out  = values;
}

/* ============================================================================
 * 主函数: Graph500 v2.1 官方流程 + SRE 扩展
 * ============================================================================ */
int main(int argc, char** argv) {
    int SCALE        = 12;
    int edgefactor   = 16;
    int NBFS         = 64;  /* 与官方 num_bfs_roots=64 对齐 */

    if (argc >= 2) SCALE       = atoi(argv[1]);
    if (argc >= 3) edgefactor  = atoi(argv[2]);
    if (argc >= 4) NBFS        = atoi(argv[3]);

    if (SCALE <= 0 || edgefactor <= 0 || NBFS <= 0) {
        fprintf(stderr,
            "Usage: %s [SCALE] [edgefactor] [NBFS]\n"
            "  SCALE       = log2(vertices), default 12\n"
            "  edgefactor  = edges/vertex,  default 16\n"
            "  NBFS        = sample runs,   default 64 (align with official num_bfs_roots)\n",
            argv[0]);
        return 1;
    }

    int64_t nverts        = (int64_t)1 << SCALE;
    int64_t desired_nedges = (int64_t)edgefactor << SCALE;

    /* ---- stderr: 进度信息 (官方规范, 不计入结果) ---- */
    fprintf(stderr, "Graph500 v2.1 + SRE Extended Kernel\n");
    fprintf(stderr, "  SCALE=%d  vertices=%lld  edges=%lld  NBFS=%d  threads=%d\n",
            SCALE, (long long)nverts, (long long)desired_nedges,
            NBFS, omp_get_max_threads());

    /* ---- Stage 1: Graph Generation (官方 Kernel 0) ---- */
    double t_gen_start = omp_get_wtime();
    int64_t nedges;
    packed_edge* edges;
    make_graph(SCALE, desired_nedges, 2, 3, &nedges, &edges);
    double make_graph_time = omp_get_wtime() - t_gen_start;
    fprintf(stderr, "graph_generation:               %g s (edges=%lld)\n",
            make_graph_time, (long long)nedges);

    /* ---- Stage 2: CSR Build (官方 construction_time) ---- */
    double t_csr_start = omp_get_wtime();
    int* row_ptr = NULL;  int* col_idx = NULL;  double* values = NULL;
    int n = 0;
    build_csr_laplacian(edges, nedges, nverts, &row_ptr, &col_idx, &values, &n);
    double construction_time = omp_get_wtime() - t_csr_start;
    int64_t nnz = row_ptr[n];
    fprintf(stderr, "construction_time:              %g s (n=%d, nnz=%lld)\n",
            construction_time, n, (long long)nnz);
    free(edges);

    /* ---- Stage 3: SRE Pipeline 多轮采样 ---- */
    sre_params_t params;
    params.lambda_2     = 0.5;
    params.alpha_n      = 0.8;
    params.epsilon_topo = 1e-6;
    params.beta_sre     = 1.2;
    params.lambda_0     = 0.9;
    params.num_groups   = (nverts / 4 > 1) ? 4 : 1;
    if (params.num_groups > 64) params.num_groups = 64;
    params.k_rank       = 4;
    params.overlap_size = 2;
    /* Op11-19 参数 */
    params.rho               = 0.5;
    params.N_max             = 6;
    params.spectral_K        = 6;
    params.spectral_max_kappa = 20;
    params.spectral_theta    = 1e-9;
    params.aut_max_v         = 22;

    double* sre_times        = (double*)malloc((size_t)NBFS * sizeof(double));
    double* sre_edge_counts  = (double*)malloc((size_t)NBFS * sizeof(double));
    sre_result_t  last_result;
    memset(&last_result, 0, sizeof(last_result));

    /* warmup (官方规范: 第0轮不计时, 用于预热 cache/TLB) */
    sre_run_full_pipeline(row_ptr, col_idx, values, n, &params, &last_result);

    for (int i = 0; i < NBFS; ++i) {
        sre_result_t r;
        memset(&r, 0, sizeof(r));
        sre_status_t st = sre_run_full_pipeline(
            row_ptr, col_idx, values, n, &params, &r);
        if (st != SRE_OK) {
            fprintf(stderr, "SRE pipeline error at run %d: %d\n", i, (int)st);
            sre_times[i] = 0.0;
            sre_edge_counts[i] = 0.0;
            continue;
        }
        sre_times[i]       = r.total_time;
        sre_edge_counts[i] = (double)r.edge_visit_count;
        last_result = r;  /* 保留最后一轮结果用于扩展段输出 */
        if ((i + 1) % 16 == 0)
            fprintf(stderr, "  SRE run %d/%d  t=%.4f s  TEPS=%.3e\n",
                    i + 1, NBFS, r.total_time, r.teps);
    }

    free(row_ptr); free(col_idx); free(values);

    /* ====================================================================
     * Stage 4: 严格按 Graph500 v2.1 官方格式输出到 stdout
     *   字段名与 main.c:490-570 完全对齐 (前缀 sre 替代 bfs/sssp)
     *   harmonic_mean_TEPS 行带 '!' 标记, 与官方排名指标一致
     * ==================================================================== */
    double stats[SRE_S_LAST];

    printf("SCALE:                          %d\n", SCALE);
    printf("edgefactor:                     %d\n", edgefactor);
    printf("NBFS:                           %d\n", NBFS);
    printf("graph_generation:               %g\n", make_graph_time);
    printf("num_mpi_processes:              %d\n", 1);
    printf("num_omp_threads:                %d\n", omp_get_max_threads());
    printf("construction_time:              %g\n", construction_time);
    printf("num_vertices:                   %lld\n", (long long)nverts);
    printf("num_edges:                      %lld\n", (long long)nedges);
    printf("nnz:                            %lld\n", (long long)nnz);

    /* SRE 时间六阶统计 */
    sre_get_statistics(sre_times, NBFS, stats);
    printf("sre_min_time:                   %g\n", stats[SRE_S_MINIMUM]);
    printf("sre_firstquartile_time:         %g\n", stats[SRE_S_FIRSTQUARTILE]);
    printf("sre_median_time:                %g\n", stats[SRE_S_MEDIAN]);
    printf("sre_thirdquartile_time:         %g\n", stats[SRE_S_THIRDQUARTILE]);
    printf("sre_max_time:                   %g\n", stats[SRE_S_MAXIMUM]);
    printf("sre_mean_time:                  %g\n", stats[SRE_S_MEAN]);
    printf("sre_stddev_time:                %g\n", stats[SRE_S_STDDEV]);

    /* 等效边数六阶统计 (SRE 以 nnz 为基准, 见说明段) */
    sre_get_statistics(sre_edge_counts, NBFS, stats);
    printf("min_nedge:                      %.11g\n", stats[SRE_S_MINIMUM]);
    printf("firstquartile_nedge:            %.11g\n", stats[SRE_S_FIRSTQUARTILE]);
    printf("median_nedge:                   %.11g\n", stats[SRE_S_MEDIAN]);
    printf("thirdquartile_nedge:            %.11g\n", stats[SRE_S_THIRDQUARTILE]);
    printf("max_nedge:                      %.11g\n", stats[SRE_S_MAXIMUM]);
    printf("mean_nedge:                     %.11g\n", stats[SRE_S_MEAN]);
    printf("stddev_nedge:                   %.11g\n", stats[SRE_S_STDDEV]);

    /* TEPS: 1/(secs_per_edge) 的六阶统计, harmonic_mean 带 ! 主指标 */
    double* secs_per_edge = (double*)malloc((size_t)NBFS * sizeof(double));
    for (int i = 0; i < NBFS; ++i)
        secs_per_edge[i] = (sre_edge_counts[i] > 0.0)
                           ? sre_times[i] / sre_edge_counts[i]
                           : 0.0;
    sre_get_statistics(secs_per_edge, NBFS, stats);
    printf("sre_min_TEPS:                   %g\n", 1.0 / stats[SRE_S_MAXIMUM]);
    printf("sre_firstquartile_TEPS:         %g\n", 1.0 / stats[SRE_S_THIRDQUARTILE]);
    printf("sre_median_TEPS:                %g\n", 1.0 / stats[SRE_S_MEDIAN]);
    printf("sre_thirdquartile_TEPS:         %g\n", 1.0 / stats[SRE_S_FIRSTQUARTILE]);
    printf("sre_max_TEPS:                   %g\n", 1.0 / stats[SRE_S_MINIMUM]);
    /* 主排名指标: harmonic mean TEPS (与 main.c:531 一致带 ! 标记) */
    printf("sre_harmonic_mean_TEPS:     !   %g\n", 1.0 / stats[SRE_S_MEAN]);
    /* harmonic stddev (Nilan Norris 1940 公式, 与 main.c:540 一致) */
    printf("sre_harmonic_stddev_TEPS:       %g\n",
           stats[SRE_S_STDDEV] /
           (stats[SRE_S_MEAN] * stats[SRE_S_MEAN] * sqrt((double)(NBFS - 1))));

    /* per-vertex 时延 */
    double* per_vertex = (double*)malloc((size_t)NBFS * sizeof(double));
    for (int i = 0; i < NBFS; ++i)
        per_vertex[i] = (nverts > 0) ? sre_times[i] / (double)nverts * 1e6 : 0.0;
    sre_get_statistics(per_vertex, NBFS, stats);
    printf("sre_min_per_vertex_us:          %g\n", stats[SRE_S_MINIMUM]);
    printf("sre_median_per_vertex_us:       %g\n", stats[SRE_S_MEDIAN]);
    printf("sre_max_per_vertex_us:          %g\n", stats[SRE_S_MAXIMUM]);
    printf("sre_mean_per_vertex_us:         %g\n", stats[SRE_S_MEAN]);

    free(secs_per_edge); free(per_vertex);
    free(sre_times); free(sre_edge_counts);

    /* ====================================================================
     * SRE 扩展段: 非官方字段, 以 '#' 注释行分隔
     *   官方 parse 脚本遇到不识别行会跳过, 不污染主指标
     * ==================================================================== */
    printf("\n");
    printf("# SRE Extended Kernel (non-standard, ignored by official parser)\n");
    printf("# op1_time=%.6e op2_time=%.6e op3_time=%.6e\n",
           last_result.op1_time, last_result.op2_time, last_result.op3_time);
    printf("# op4_time=%.6e op5_time=%.6e op6_time=%.6e\n",
           last_result.op4_time, last_result.op5_time, last_result.op6_time);
    printf("# op7_time=%.6e op8_time=%.6e op9_time=%.6e op10_time=%.6e\n",
           last_result.op7_time, last_result.op8_time,
           last_result.op9_time, last_result.op10_time);
    printf("# op11_time=%.6e op12_time=%.6e op13_time=%.6e op14_time=%.6e\n",
           last_result.op11_time, last_result.op12_time,
           last_result.op13_time, last_result.op14_time);
    printf("# op15_time=%.6e op16_time=%.6e op17_time=%.6e op18_time=%.6e op19_time=%.6e\n",
           last_result.op15_time, last_result.op16_time,
           last_result.op17_time, last_result.op18_time, last_result.op19_time);
    printf("# op4_w_e_trace=%.6f op4_w_e_frobenius=%.6f\n",
           last_result.op4_w_e_trace, last_result.op4_w_e_frobenius);
    printf("# op5_c_e_mean=%.6f\n", last_result.op5_c_e_mean);
    printf("# op6_lambda_2=%.6e op6_alpha_n=%.6e op6_residual=%.6e\n",
           last_result.op6_lambda_2, last_result.op6_alpha_n, last_result.op6_residual);
    printf("# op7_grad_norm=%.6e op8_delta_Pi=%.6e op9_trace=%.6f\n",
           last_result.op7_grad_norm, last_result.op8_delta_Pi, last_result.op9_trace);
    printf("# op10_z_eff=%.6f op10_action_gate=%d op10_p_conduction=%.6f\n",
           last_result.op10_z_eff, last_result.op10_action_gate,
           last_result.op10_p_conduction);
    /* Op11-12 电子自由度 */
    printf("# op11_lambda_2_q=%.6e op11_alpha_q=%.6e op11_kappa_q=%.6e\n",
           last_result.op11_lambda_2_q, last_result.op11_alpha_q,
           last_result.op11_kappa_q);
    printf("# op11_q_dispersion=%.6e op11_max_spin_coupling=%.6e\n",
           last_result.op11_q_dispersion, last_result.op11_max_spin_coupling);
    printf("# op12_n_loops=%d op12_mobius_ratio=%.6e\n",
           last_result.op12_n_loops, last_result.op12_mobius_ratio);
    /* Op13-18 谱形方程 */
    printf("# op13_K=%d op13_tau_0=%.6f op13_tau_2=%.6f\n",
           last_result.op13_K, last_result.op13_tau_0, last_result.op13_tau_2);
    printf("# op14_grad_norm=%.6e op14_harm_norm=%.6e op14_curl_norm=%.6e\n",
           last_result.op14_grad_norm, last_result.op14_harm_norm,
           last_result.op14_curl_norm);
    printf("# op15_dM_norm=%.6e op15_quad=%.6e op15_trust=%.6f\n",
           last_result.op15_dM_norm, last_result.op15_quad, last_result.op15_trust);
    printf("# op16_feas_before=%.6e op16_feas_after=%.6e op16_t_star=%.6f\n",
           last_result.op16_feas_before, last_result.op16_feas_after,
           last_result.op16_t_star);
    printf("# op17_verdict=%d op17_eps=%.6e\n",
           last_result.op17_verdict, last_result.op17_eps);
    printf("# op18_h_norm=%.6e op18_d_hom=%.6e op18_budget=%.6e\n",
           last_result.op18_h_norm, last_result.op18_d_hom, last_result.op18_budget);
    /* Op19 电荷通道 */
    printf("# op19_V=%d op19_E=%d op19_c=%d op19_beta1=%d op19_deg=%d\n",
           last_result.op19_V, last_result.op19_E, last_result.op19_c,
           last_result.op19_beta1, last_result.op19_deg);
    printf("# op19_bipartite=%d op19_sigma_trivial=%d op19_sigma_canonical=%.1f op19_Q_model=%.1f op19_channel_type=%d\n",
           last_result.op19_bipartite, last_result.op19_sigma_trivial,
           last_result.op19_sigma_canonical, last_result.op19_Q_model,
           last_result.op19_channel_type);

    return 0;
}
