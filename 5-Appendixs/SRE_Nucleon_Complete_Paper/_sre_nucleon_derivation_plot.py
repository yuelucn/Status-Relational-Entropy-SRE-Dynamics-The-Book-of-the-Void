# -*- coding: utf-8 -*-
"""
_sre_nucleon_derivation_plot.py
核子拓扑推衍链示意图（浅色主题；数学符号用 mathtext 以避免缺字形）

3 面板：
  A  isospin Z2 双重态：三子核绑定 (u,u,d)/(u,d,d)，T3 反射，电荷 +1/0
  B  绑定算子 R_bind：承接线剔除（幂等+单调收敛），相干复合 vs 退束缚
  C  局部带入反推：逻辑深度 N_e/N_p/N_n（对数轴）+ 只读锚点登记
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

FIG = "sre_nucleon_derivation.png"
SVG = "sre_nucleon_derivation.svg"

# 常量（CODATA 2018，只读锚点）
ME, MP, MN = 0.51099895000, 938.27208816, 939.56542052
ALPHA_INV = 137.035999084
N_E = 1.0e23
N_P = N_E * ME / MP
N_N = N_E * ME / MN


def draw_cube(ax, cx, cy, s=0.30, dz=0.16, color="#185FA5", lw=1.0):
    """在 (cx,cy) 处画一个 8 结点立方体示意（Q3 模板）。"""
    pts = {}
    for k in range(8):
        b0 = (k >> 2) & 1
        b1 = (k >> 1) & 1
        b2 = k & 1
        x = cx + s * (2 * b0 - 1)
        y = cy + s * (2 * b1 - 1) + dz * b2
        pts[k] = (x, y)
    for k in range(8):
        for l in range(k + 1, 8):
            if bin(k ^ l).count("1") == 1:
                x0, y0 = pts[k]
                x1, y1 = pts[l]
                ax.plot([x0, x1], [y0, y1], color=color, lw=lw,
                        alpha=0.55, zorder=1)
    for k, (x, y) in pts.items():
        ax.scatter([x], [y], s=8, color=color, zorder=2)
    return pts


def panel_a(ax):
    """isospin Z2 双重态：p=(u,u,d) 与 n=(u,d,d)，三子核绑定 + T3 反射。"""
    ax.set_title(r"A  isospin $Z_2$ 双重态：三子核绑定", fontsize=12)
    ax.set_xlim(-5.0, 4.0)
    ax.set_ylim(-3.2, 3.4)
    ax.axis("off")

    # 两个复合图：p 在 x=-2.6，n 在 x=+2.6；三个子核位于三角形顶点
    for cx, charge, name in [(-2.6, ["u", "u", "d"], r"$p=(u,u,d)$"),
                             (2.6, ["u", "d", "d"], r"$n=(u,d,d)$")]:
        # 三个子核中心（三角形）
        centers = [(cx, 1.5), (cx - 1.45, -1.1), (cx + 1.45, -1.1)]
        # 承接线（子核间）
        for i in range(3):
            for j in range(i + 1, 3):
                xi, yi = centers[i]
                xj, yj = centers[j]
                ax.plot([xi, xj], [yi, yj], color="#BA7517", lw=1.6, zorder=1)
        for (cx0, cy0), q in zip(centers, charge):
            draw_cube(ax, cx0, cy0, s=0.42, dz=0.22, color="#185FA5")
            # 电荷位型标签
            ax.text(cx0, cy0 + 0.06, q, ha="center", va="center",
                    fontsize=11, color="#A32D2D", zorder=3,
                    bbox=dict(boxstyle="circle,pad=0.12", fc="white", ec="none"))
        # 总电荷标注
        qsum = sum(2.0 / 3.0 if c == "u" else -1.0 / 3.0 for c in charge)
        ax.text(cx, 2.65, r"$Q=+1$" if qsum > 0 else r"$Q=0$",
                ha="center", fontsize=12, color="#0C447C")
        ax.text(cx, -2.6, name, ha="center", fontsize=12, color="#26215C")

    # T3 反射箭头
    ax.annotate("", xy=(1.05, 0.0), xytext=(-1.05, 0.0),
                arrowprops=dict(arrowstyle="->", color="#534AB7", lw=2.0))
    ax.text(0.0, 0.45, r"$T_3$ ($Z_2$: $T_3^2=\mathrm{id}$, 无不动点)",
            ha="center", fontsize=12, color="#534AB7")
    ax.text(0.0, 1.6, r"复合图同构（结构镜像）",
            ha="center", fontsize=10, color="#888780")


def panel_b(ax):
    """绑定算子 R_bind：承接线剔除（幂等+单调），相干复合 vs 退束缚。"""
    ax.set_title(r"B  绑定算子 $R_{\mathrm{bind}}$：幂等 + 单调收敛", fontsize=12)
    ax.set_xlim(-5.0, 5.0)
    ax.set_ylim(-3.2, 3.4)
    ax.axis("off")

    # 左：低阈值 -> 相干复合（承接线存活）
    centers = [(0.0, 1.5), (-1.45, -1.1), (1.45, -1.1)]
    for i in range(3):
        for j in range(i + 1, 3):
            xi, yi = centers[i]
            xj, yj = centers[j]
            ax.plot([xi, xj], [yi, yj], color="#0F6E56", lw=2.0, zorder=1)
    for cx0, cy0 in centers:
        draw_cube(ax, cx0, cy0, s=0.42, dz=0.22, color="#0F6E56")
    ax.text(4.0, 2.6, r"$\varepsilon=0.4$" + "\n相干复合（连通）",
            ha="right", fontsize=11, color="#085041")

    # 幂等标注
    ax.text(0.0, -2.7,
            r"$R_{\mathrm{bind}}^2=R_{\mathrm{bind}}$（幂等）$\;|\;|E|\downarrow$（单调）"
            r"$\Rightarrow$ 迭代一步即达不动点",
            ha="center", fontsize=11, color="#26215C")
    ax.text(0.0, -3.15, r"子核内部边永不剔除 $\cdot$ 承接线按休眠阈值 ε 取舍",
            ha="center", fontsize=10, color="#888780")


def panel_c(ax):
    """局部带入反推：逻辑深度 N_e/N_p/N_n（对数轴）+ 只读锚点。"""
    ax.set_title(r"C  局部带入反推：核子逻辑深度（对数轴）", fontsize=12)
    labels = [r"$N_e$（电子）", r"$N_p$（质子）", r"$N_n$（中子）"]
    vals = [N_E, N_P, N_N]
    cols = ["#1D9E75", "#378ADD", "#378ADD"]
    bars = ax.bar(labels, vals, color=cols, width=0.5)
    ax.set_yscale("log")
    ax.set_ylim(1e18, 3e23)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2.0, v * 1.35, "%.3e" % v,
                ha="center", fontsize=10, color="#26215C")
    ax.set_ylabel("逻辑深度 $N$（无量纲）", fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 只读锚点登记框
    box = (r"只读锚点（非推导）" + "\n" +
           r"$m_p/m_e=1836.15267343$" + "\n" +
           r"$m_n/m_p=1.00137841931$" + "\n" +
           r"$(m_n-m_p)/m_p=1.3784\times10^{-3}$" + "\n" +
           r"$\alpha^{-1}=137.035999084$")
    ax.text(0.97, 0.03, box, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=10, color="#633806",
            bbox=dict(boxstyle="round,pad=0.5", fc="#FAEEDA", ec="#BA7517", lw=1.0))

    ax.text(0.02, 0.97,
            r"$N_p=N_e\cdot(m_e/m_p)\approx5.4462\times10^{19}$" + "\n"
            r"$N_n=N_e\cdot(m_e/m_n)\approx5.4387\times10^{19}$" + "\n"
            r"（对偶自洽：$N_e/N_p=m_p/m_e$，非独立预言）",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=10, color="#0C447C")


def main():
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.8))
    panel_a(axes[0])
    panel_b(axes[1])
    panel_c(axes[2])
    fig.suptitle("核子在 SRE 框架下的拓扑推衍：复合本体 · isospin $Z_2$ 双重态 · 局部带入反推",
                 fontsize=14, y=0.985)
    fig.text(0.5, 0.012,
             "模型内部结构化自洽（C1–C5）；质量类为只读锚点（C6），不作现实物理数值预言。",
             ha="center", fontsize=10, color="#5F5E5A")
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    fig.savefig(FIG, dpi=120, bbox_inches="tight")
    fig.savefig(SVG, bbox_inches="tight")
    print("saved:", FIG, SVG)


if __name__ == "__main__":
    main()
