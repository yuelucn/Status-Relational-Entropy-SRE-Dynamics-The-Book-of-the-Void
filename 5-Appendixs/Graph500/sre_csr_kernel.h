/* sre_csr_kernel.h
 * SRE (State-Relation Entropy) 全套 19 算子 — Graph500 集成版
 *
 * HPC 优化:
 *   Op4: SpGEMM 稀疏 2-hop 漫步 O(N*K0^2)
 *   Op6: 无矩阵 Lanczos 迭代 + OpenMP 并行
 *   Op13: Chebyshev 矩三项递推 (无特征分解)
 *   Op14-18: 小维链复形上的谱形方程求解内环
 *   全部: 预分配工作区, 扁平化数组, 零堆分配
 *
 * 纯 C 实现, 不依赖 Eigen/MPI, 可直接嵌入 Graph500.
 */
#ifndef SRE_CSR_KERNEL_H
#define SRE_CSR_KERNEL_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---- SRE 错误码 ---- */
typedef enum {
    SRE_OK = 0,
    SRE_ERR_INVALID_ARG = -1,
    SRE_ERR_INTERNAL = -3,
    SRE_ERR_NOT_CONVERGED = -4,
    SRE_ERR_OVERFLOW = -5
} sre_status_t;

/* ---- SRE 算子参数 ---- */
typedef struct sre_params {
    double lambda_2;
    double alpha_n;
    double epsilon_topo;
    double beta_sre;
    double lambda_0;
    int    num_groups;
    int    k_rank;
    int    overlap_size;
    /* --- Op11 电子自由度 --- */
    double rho;               /* 电负性差调制强度 */
    /* --- Op12 闭合环审计 --- */
    int    N_max;             /* 最大环长度枚举上限 */
    /* --- Op13-18 谱形方程 --- */
    int    spectral_K;        /* Chebyshev 截断阶 (0=内生) */
    int    spectral_max_kappa;/* 谱形方程最大迭代步 */
    double spectral_theta;    /* Hankel 钳制内生阈值 */
    /* --- Op19 电荷通道 --- */
    int    aut_max_v;         /* 自同构顶点数守卫 */
} sre_params_t;

/* ---- SRE 全套结果 ---- */
typedef struct sre_result {
    /* 各算子耗时 (秒) */
    double op1_time;
    double op2_time;
    double op3_time;
    double op4_time;
    double op5_time;
    double op6_time;
    double op7_time;
    double op8_time;
    double op9_time;
    double op10_time;
    double op11_time;
    double op12_time;
    double op13_time;
    double op14_time;
    double op15_time;
    double op16_time;
    double op17_time;
    double op18_time;
    double op19_time;
    double total_time;

    /* === Graph500 v2.1 官方标准字段 === */
    int64_t edge_visit_count;    /* SRE 等效遍历边数 (以 nnz 为基准) */
    double  teps;                /* edge_visit_count / total_time */
    double  per_vertex_us;       /* 单顶点时延 (μs) */

    /* 关键输出校验值 */
    int    op1_expanded_n;       /* Op1 扩张后维度 */
    int    op2_intersection;     /* Op2 交集和 */
    int    op3_y_bool;           /* Op3 NAND 输出 */
    double op4_w_e_trace;        /* Op4 W_e 迹 */
    double op4_w_e_frobenius;    /* Op4 W_e Frobenius 范数 */
    double op5_c_e_mean;         /* Op5 平均时滞 */
    double op6_lambda_2;         /* Op6 Fiedler 估计 */
    double op6_alpha_n;          /* Op6 谱半径 */
    double op6_residual;         /* Op6 残差 */
    double op7_grad_norm;        /* Op7 梯度范数 */
    double op8_delta_Pi;         /* Op8 阀流变化 */
    double op9_trace;            /* Op9 S_dual 迹 */
    double op10_z_eff;           /* Op10 有效阻抗 */
    int    op10_action_gate;     /* Op10 动作门 */
    double op10_p_conduction;    /* Op10 传导概率 */

    /* === Op11 自旋-电荷邻接 === */
    double op11_lambda_2_q;      /* L_q 第二小特征值 */
    double op11_alpha_q;         /* L_q 谱半径 */
    double op11_kappa_q;         /* alpha_q / lambda_2_q */
    double op11_q_dispersion;    /* std(|chi|) / mean(|chi|) */
    double op11_max_spin_coupling; /* max |sigma*wq| over support */

    /* === Op12 闭合环审计 === */
    int    op12_n_loops;         /* 简单环计数 */
    double op12_mobius_ratio;    /* mean |tr(M^k)| / n^k */
    double op12_lambda_2_loop;   /* 环上子图 λ2 */
    double op12_kappa_loop;      /* 环上子图 kappa */

    /* === Op13-18 谱形方程求解 === */
    int    op13_K;               /* Chebyshev 截断阶 */
    double op13_tau_0;           /* tau_0 = 1 */
    double op13_tau_2;           /* tau_2 谱形矩 */
    double op14_grad_norm;       /* Hodge 梯度分量范数 */
    double op14_harm_norm;       /* Hodge 调和分量范数 */
    double op14_curl_norm;       /* Hodge 旋度分量范数 */
    double op15_dM_norm;         /* 牛顿步长范数 */
    double op15_quad;            /* g_tilde^T A^+ g_tilde */
    double op15_trust;           /* 信赖域缩放 */
    double op16_feas_before;     /* Hankel 钳制前可行性 */
    double op16_feas_after;      /* Hankel 钳制后可行性 */
    double op16_t_star;          /* 二分回退 t* */
    int    op17_verdict;         /* 0=CONTINUE,1=SOLVED,2=OBSTRUCTION,3=STALLED */
    double op17_eps;             /* 内生收敛阈值 */
    double op18_h_norm;          /* 同调残差 ||h|| */
    double op18_d_hom;           /* 同调距离 */
    double op18_budget;          /* 恰当残差预算 */

    /* === Op19 Z2 holonomy 电荷通道 === */
    int    op19_V;               /* 顶点数 */
    int    op19_E;               /* 边数 */
    int    op19_c;               /* 连通分支数 */
    int    op19_beta1;           /* β₁ = E - V + c */
    int    op19_deg;             /* deg = β₁ mod 2 */
    int    op19_bipartite;       /* 是否二分图 */
    int    op19_sigma_trivial;   /* σ 类是否平凡 */
    double op19_sigma_canonical; /* +1 / -1 */
    double op19_Q_model;         /* σ_canonical * deg */
    int    op19_channel_type;    /* 0=electron-like,1=nucleon-like,2=unknown */
} sre_result_t;

/* ============================================================================
 * 全套 SRE 算子流水线 (Op1 ~ Op19)
 *
 * 输入: CSR 格式拉普拉斯矩阵 (row_ptr, col_idx, values, n)
 * 输出: sre_result_t 计时与校验结果
 * ============================================================================ */
sre_status_t sre_run_full_pipeline(
    const int* row_ptr, const int* col_idx, const double* values, int n,
    const sre_params_t* params, sre_result_t* result
);

/* ============================================================================
 * Graph500 v2.1 官方六阶统计量
 *   与 main.c:get_statistics 算法等价, 用于多轮采样的 min/Q1/median/Q3/max/mean/std
 * ============================================================================ */
enum sre_stat_idx {
    SRE_S_MINIMUM = 0,
    SRE_S_FIRSTQUARTILE,
    SRE_S_MEDIAN,
    SRE_S_THIRDQUARTILE,
    SRE_S_MAXIMUM,
    SRE_S_MEAN,
    SRE_S_STDDEV,
    SRE_S_LAST
};
void sre_get_statistics(const double x[], int n, double r[SRE_S_LAST]);

/* ---- 单独算子接口 (供精细测试) ---- */

/* Op1: 局域图扩张 */
sre_status_t sre_op1_expansion(int n_in, int max_n, int* n_out);

/* Op2: 二阶行走干涉 */
sre_status_t sre_op2_metrics(const int* edge_spins, int edge_count,
                              const int* neighbors_f, int nf_count,
                              const int* neighbors_m, int nm_count,
                              int vf_id, int vm_id,
                              int* inter_sum, int* self_sum, int* complete);

/* Op3: NAND 门 */
sre_status_t sre_op3_nand(int A, int B, int* Y_spin, int* Y_bool);

/* Op4: 度规权重 — CSR SpGEMM 版 */
sre_status_t sre_op4_degree_csr(const int* row_ptr, const int* col_idx,
                                const double* values, int n,
                                double lambda_2, double alpha_n,
                                double epsilon_topo, double* W_e);

/* Op5: 时滞校准 */
sre_status_t sre_op5_latency(const double* W_e, int rows, int cols,
                             double c_max, double alpha_n, double w_min,
                             double delta_flt, double* c_e);

/* Op6: 谱拼接 — 矩阵free Lanczos 版 */
sre_status_t sre_op6_splicing_csr(const int* row_ptr, const int* col_idx,
                                  const double* values, int n,
                                  int num_groups, int k_rank, int overlap_size,
                                  double rr_tol_warn,
                                  double* lambda_2_approx,
                                  double* alpha_n_approx,
                                  double* max_residual);

/* Op7: 伴随滤波 */
sre_status_t sre_op7_potential(const double* B_co, int M, int Mk,
                               const double* E_s, double* grad_E, double* B_half);

/* Op8: 代数阀流 */
sre_status_t sre_op8_valve_flow(const double* E_s, int Mk,
                                const double* B_half, int B_half_len,
                                const double* B_co, int M,
                                const double* V_write,
                                double lambda_2, double gamma_flow,
                                double smooth_alpha, double delta_flt,
                                double* Phi_valve, double* delta_Pi);

/* Op9: 双阶缝合 */
sre_status_t sre_op9_stitching(const double* del_2, int E, int Nf,
                               const double* delta_1,
                               double lambda_2, double p_mu_scale,
                               double eig_null_tol, double delta_flt,
                               double* S_dual);

/* Op10: 防火墙 — 标量版 */
sre_status_t sre_op10_firewall_scalar(double L_uu, double L_vv, double L_uv,
                                      int is_bridge, double omega_th,
                                      double exp_clip_min, double exp_clip_max,
                                      double delta_flt,
                                      double* z_eff, int* action_gate,
                                      double* p_conduction);

/* ---- Op11: 自旋-电荷邻接 ---- */
/* A_q = A_s * (1 + rho * |tanh(chi_i - chi_j)|), L_q, lambda_2_q, alpha_q, kappa_q */
sre_status_t sre_op11_spin_charge(const double* A_s, const double* chi, int n,
                                  double rho,
                                  double* lambda_2_q, double* alpha_q,
                                  double* kappa_q, double* q_dispersion,
                                  double* max_spin_coupling, double* A_q_out);

/* ---- Op12: 闭合环审计 ---- */
/* 简单环计数 + Möbius 相位比 mean|tr(M^k)|/n^k */
sre_status_t sre_op12_closed_loop_audit(const double* A_q, int n, int N_max,
                                        int* n_loops, double* mobius_ratio,
                                        double* lambda_2_loop, double* kappa_loop);

/* ---- Op13: Chebyshev 矩编码 ---- */
/* tau_k = (1/N) tr(T_k(Y)), Y = 2L/alpha_n - I */
sre_status_t sre_op13_chebyshev_moments(const double* L, int n, double alpha_n,
                                        int K, double* tau, double* Y_out);

/* ---- Op14: Hodge 三分量投影 ---- */
/* r = D*phi + h + C^T*psi */
sre_status_t sre_op14_hodge_project(const double* r, const double* D,
                                    int m_g, int n_node,
                                    const double* C, int n_face,
                                    double* grad, double* harm, double* curl);

/* ---- Op15: 内生拟牛顿步 ---- */
/* dM = -A^+ (g_M - h), eta = F^2/quad, 信赖域 cap at 0.5*lam2 */
sre_status_t sre_op15_endo_newton(const double* g_M, const double* h,
                                  const double* A, int m_g,
                                  double F, const double* D, int n_node,
                                  double lam2,
                                  double* dM, double* quad, double* trust);

/* ---- Op16: Hankel 可行性钳制 ---- */
sre_status_t sre_op16_hankel_clamp(const double* mu_new, const double* mu_ref,
                                   int mu_len, int Kp, double theta_endo,
                                   double* mu_clamped,
                                   double* feas_before, double* feas_after,
                                   double* t_star);

/* ---- Op17: 解分支审计裁定 ---- */
/* 返回 verdict: 0=CONTINUE,1=SOLVED,2=OBSTRUCTION,3=STALLED */
sre_status_t sre_op17_audit(double grad_norm, double curl_norm, double harm_norm,
                            double r0_norm, double lam2, double alpha_n,
                            double f_prev, double f_now, int step_dead,
                            int* verdict, double* eps);

/* ---- Op18: 同调解实现 ---- */
sre_status_t sre_op18_homological_realize(const double* D, int m_g, int n_node,
                                          const double* C, int n_face,
                                          const double* m, const double* m_init,
                                          double* h_norm, double* d_hom,
                                          double* budget);

/* ---- Op19: Z2 holonomy 电荷通道 ---- */
sre_status_t sre_op19_z2_charge_channel(const double* A_s, int n,
                                        const double* chi,
                                        int* V, int* E, int* c,
                                        int* beta1, int* deg,
                                        int* bipartite, int* sigma_trivial,
                                        double* sigma_canonical,
                                        double* Q_model, int* channel_type);

#ifdef __cplusplus
}
#endif

#endif /* SRE_CSR_KERNEL_H */
