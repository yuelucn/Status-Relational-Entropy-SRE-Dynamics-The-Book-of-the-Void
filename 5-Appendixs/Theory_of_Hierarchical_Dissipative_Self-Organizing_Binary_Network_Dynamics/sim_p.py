import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import MDS

def hierarchical_dissipation_binary_network_final(steps=200, lam=0.8, seed=None):
    """【2026理论严格终审定版】核心演化算法"""
    if seed is not None:
        np.random.seed(seed)
        
    # 第一公理：一阶非零单点种子源 M_1 = [[1]]，严格二维矩阵
    M = np.array([[1]], dtype=int)

    for n in range(1, steps):
        size = n + 1
        new_M = np.empty((size, size), dtype=int)
        new_M[:n, :n] = M  # 第一公理：无0态历史完美继承
        
        E_local_matrix = np.abs(M @ M)
        i_idx = np.arange(n)[:, None]
        j_idx = np.arange(n)[None, :]
        d_matrix = n - np.maximum(i_idx, j_idx)
        
        ratio = (lam * d_matrix) / (E_local_matrix + 1)
        p_matrix = 1.0 - 1.0 / (1.0 + ratio)
        
        rand_matrix = np.random.rand(n, n)
        rand_matrix = np.triu(rand_matrix) + np.triu(rand_matrix, 1).T
        activate_matrix = rand_matrix >= p_matrix
        
        mask_M = np.where(activate_matrix, M, 1)
        new_boundary = np.prod(mask_M, axis=1)
        
        has_active_link = np.any(activate_matrix, axis=1)
        new_boundary = np.where(has_active_link, new_boundary, 1)
        
        new_M[:n, n] = new_boundary
        new_M[n, :n] = new_boundary
        
        total_sum = np.sum(new_M[:n, :n])
        new_M[n, n] = -1 if total_sum >= 0 else 1
        
        M = new_M
    return M

if __name__ == "__main__":
    print("=" * 80)
    print(" 开始运行《层级耗散自组织二元网络动力学理论》矩阵、序参量、3D流形[3次全景对比]验证...")
    print("=" * 80)
    
    # 统一步数规模 N = 100 (9张图同时计算MDS，100阶可在2分钟内完成，完美兼顾精度与耗时)
    STEPS = 300
    LAMBDA = 0.8
    NUM_SAMPLES = 20  # 用于计算序参量方差的独立样本数
    
    # 定义 3 次对比运行的核心随机种子
    run_seeds = [1111, 2222, 3333]
    
    # 创建一个 3行3列 的超大科学画布
    fig = plt.figure(figsize=(18, 16))
    fig.suptitle(f"Theory of Hierarchical Dissipation Unified Verification (3 Comparative Runs, N={STEPS}, $\lambda$={LAMBDA})", 
                 fontsize=16, y=0.99, fontweight='bold')
    
    for row_idx, current_seed in enumerate(run_seeds):
        run_num = row_idx + 1
        print(f"\n🚀 [第 {run_num}/3 次大轮演化启动] 正在注入随机种子 Seed: {current_seed}...")
        
        # ----------------------------------------------------
        # 1. 演化当前行对应的主矩阵
        # ----------------------------------------------------
        print(f"  -> 正在生成主样本矩阵...")
        M_main = hierarchical_dissipation_binary_network_final(steps=STEPS, lam=LAMBDA, seed=current_seed)
        
        # ----------------------------------------------------
        # 2. 计算当前种子扰动下的 序参量 Phi(N) 收敛曲线数据
        # ----------------------------------------------------
        print(f"  -> 正在并行演化 {NUM_SAMPLES} 个局部扰动样本群落以计算方差...")
        all_samples = []
        for s in range(NUM_SAMPLES):
            # 将主种子作为偏移基底，确保其既包含主运行特性又具备群落统计随机性
            local_seed = current_seed + s * 7
            all_samples.append(hierarchical_dissipation_binary_network_final(steps=STEPS, lam=LAMBDA, seed=local_seed))
            
        print("  -> 正在结算各有限标度下的序参量 Phi(N)...")
        N_range = np.arange(15, STEPS)
        phi_N_curve = []
        for N in N_range:
            k = int(np.floor(0.2 * N))
            k = max(2, k)
            traces = [np.trace(all_samples[s][:k, :k]) for s in range(NUM_SAMPLES)]
            phi_N_curve.append(1.0 - (np.var(traces) / (k ** 2)))
            
        # ----------------------------------------------------
        # 3. 驱动 MDS 重整化解构三维坐标
        # ----------------------------------------------------
        print("  -> 正在驱动 MDS 重整化算子抽取 3D 几何流形坐标...")
        distance_matrix = np.sqrt(2.0 - 2.0 * (M_main / 1.0))
        mds = MDS(n_components=3, dissimilarity='precomputed', random_state=current_seed, n_init=4)
        coordinates_3d = mds.fit_transform(distance_matrix)
        
        # ----------------------------------------------------
        # 4. 图表装填与子画布渲染 (第 row_idx 行)
        # ----------------------------------------------------
        print(f"  -> 正在装填第 {run_num} 行子图画布...")
        
        # --- 子图 1：二维实对称星系矩阵 (位于第 row_idx 行的第 1 列) ---
        ax1 = fig.add_subplot(3, 3, row_idx * 3 + 1)
        ax1.imshow(M_main, cmap='gray', origin='lower')
        ax1.set_title(f"Run {run_num} (Seed {current_seed}): Matrix Heatmap", fontsize=11, fontweight='bold')
        ax1.axis('off')
        
        # --- 子图 2：定理 1 序参量 Phi(N) 收敛线 (位于第 row_idx 行的第 2 列) ---
        ax2 = fig.add_subplot(3, 3, row_idx * 3 + 2)
        ax2.plot(N_range, phi_N_curve, color='#1f77b4', lw=2.2, label=r'Empirical $\Phi(N)$')
        phi_M_0 = float(np.mean(phi_N_curve[-15:]))
        ax2.axhline(y=phi_M_0, color='r', linestyle='--', label=r'Limit $\Phi_0 \approx ' + f'{phi_M_0:.4f}$')
        ax2.set_title(f"Run {run_num}: $\Phi(N)$ Convergence", fontsize=11, fontweight='bold')
        ax2.set_xlabel("Steps ($N$)", fontsize=9)
        ax2.set_ylabel(r"Coherence $\Phi(N)$", fontsize=9)
        ax2.grid(True, linestyle=':', alpha=0.5)
        ax2.legend(fontsize=9, loc='lower right')
        
        # --- 子图 3：定理 2 涌现之 3D 空间粒子流形 (位于第 row_idx 行的第 3 列) ---
        ax3 = fig.add_subplot(3, 3, row_idx * 3 + 3, projection='3d')
        x, y, z = coordinates_3d[:, 0], coordinates_3d[:, 1], coordinates_3d[:, 2]
        colors = np.arange(STEPS)
        scatter = ax3.scatter(x, y, z, c=colors, cmap='viridis', s=20, edgecolors='w', alpha=0.7)
        ax3.plot(x, y, z, color='gray', lw=0.4, alpha=0.3)
        ax3.set_title(f"Run {run_num}: Emergent 3D Manifold", fontsize=11, fontweight='bold')
        ax3.set_xlabel("X", fontsize=8)
        ax3.set_ylabel("Y", fontsize=8)
        ax3.set_zlabel("Z", fontsize=8)
        ax3.view_init(elev=22, azim=40)
        
        # 为每一行的 3D 粒子流形独立添加颜色侧边条指示演化阶数
        cbar = fig.colorbar(scatter, ax=ax3, pad=0.08, shrink=0.65)
        cbar.ax.tick_params(labelsize=8)
        if row_idx == 0:
            cbar.set_label("Node Order ($n$)", fontsize=9)
            
    # ----------------------------------------------------
    # 全局大图保存与展示
    # ----------------------------------------------------
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.22, hspace=0.25)
    
    output_png = "3_runs_complete_comparison.png"
    plt.savefig(output_png, dpi=200, bbox_inches='tight')
    print("\n" + "=" * 80)
    print(f"【全面实证大功告成】3行×3列九图全景对比大图已成功保存至本地：{output_png}")
    print("正在呼出本地交互图形视窗...")
    print("=" * 80)
    
    plt.show()
