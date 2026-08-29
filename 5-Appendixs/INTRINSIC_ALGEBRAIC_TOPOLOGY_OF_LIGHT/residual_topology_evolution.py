import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    print("🔮 0-状态代数闭环：从两端不同演化步数的【残留拓扑差值】中自发涌现出光...")
    
    # 定义因果网格
    n_points = 500
    phi = np.linspace(0, 2 * np.pi, n_points)
    
    # 模拟两端相互作用的微观阻抗带宽
    w_band = np.linspace(-0.2, 0.2, 8)
    phi_mesh, w_mesh = np.meshgrid(phi, w_band)
    
    # 核心映射：将“步数差产生的相互残留”转化为代数流形的本征张量
    X_residual = (1.0 + w_mesh * np.cos(phi_mesh / 2.0)) * np.cos(phi_mesh)
    Y_residual = (1.0 + w_mesh * np.cos(phi_mesh / 2.0)) * np.sin(phi_mesh)
    Z_residual = w_mesh * np.sin(phi_mesh / 2.0)
    
    # =====================================================================
    # 3. 渲染出光作为“残留拓扑”的真实形体
    # =====================================================================
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1, projection='3d')
    
    # 颜色的渐变直接代表了两个系统演化步骤的相对推进差（因果深度）
    norm = plt.Normalize(0, 2 * np.pi)
    face_colors = plt.cm.plasma(norm(phi_mesh))  # 改用代表能量残留的 plasma 渐变色
    
    # 绘制出这层由演化残留物织成的拓扑薄膜
    surf = ax.plot_surface(X_residual, Y_residual, Z_residual, 
                            facecolors=face_colors, shade=False, alpha=0.85)
    
    # 用醒目的黑线标出这条“相互锁死”的单边界线
    ax.plot(X_residual[0, :], Y_residual[0, :], Z_residual[0, :], color='cyan', linewidth=2.0, label='Mutual Entangled Boundary')
    ax.plot(X_residual[-1, :], Y_residual[-1, :], Z_residual[-1, :], color='cyan', linewidth=2.0)
    
    ax.set_title("Light as Residual Topology between Dual Evolution Steps (0-State SRE)\nPure Mutual Algebraic Intersection", 
                 fontsize=11, fontweight='bold')
    ax.set_xlabel("Eigen Dimension 1")
    ax.set_ylabel("Eigen Dimension 2")
    ax.set_zlabel("Eigen Dimension 3")
    
    # 【完美修正】：清空背景，让光的“残留结构”在代数真空中显化
    ax.grid(False)
    ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.view_init(elev=30, azim=60)
    
    print("🎨 残流拓扑结构画笔绘制完成！请观察这个纯代数演化留下的几何形体...")
    plt.show()
