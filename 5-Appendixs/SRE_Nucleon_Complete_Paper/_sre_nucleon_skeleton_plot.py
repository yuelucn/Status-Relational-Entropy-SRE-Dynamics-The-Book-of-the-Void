# -*- coding: utf-8 -*-
"""
核子骨架反演配图：
  (a) 三股 Y 三角闭合骨架的结构示意（闭合态 / 开态）
  (b) 三步筛选漏斗（85 -> 4 -> 2）与稀有度
输出：sre_nucleon_skeleton_structure.png/.svg , sre_nucleon_skeleton_funnel.png/.svg
"""
import json
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

RES = json.load(open("sre_nucleon_skeleton_inversion_results.json", encoding="utf-8"))


# ---------------------------------------------------------------- 骨架构建
def y3(remove_edge=None):
    G = nx.Graph()
    lea = {(i, j): "L%d%d" % (i, j) for i in range(3) for j in range(3)}
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, lea[(i, j)])
    for j in range(3):
        G.add_edge(lea[(0, j)], lea[(1, j)])
        G.add_edge(lea[(1, j)], lea[(2, j)])
        G.add_edge(lea[(2, j)], lea[(0, j)])
    if remove_edge is not None:
        G.remove_edge(*remove_edge)
    return G, lea


def layout(lea):
    pos = {}
    # 3 个外围三角形（环）
    for j in range(3):
        th = np.pi / 2 + 2 * np.pi * j / 3
        cx, cy = 1.15 * np.cos(th), 1.15 * np.sin(th)
        for i in range(3):
            ph = th + 2 * np.pi * i / 3 + np.pi
            pos[lea[(i, j)]] = (cx + 0.42 * np.cos(ph), cy + 0.42 * np.sin(ph))
    # 3 个中心（股心）
    for i in range(3):
        ph = np.pi / 2 + 2 * np.pi * i / 3
        pos["c%d" % i] = (0.42 * np.cos(ph), 0.42 * np.sin(ph))
    return pos


# ---------------------------------------------------------------- 图 (a)
fig, axes = plt.subplots(1, 2, figsize=(12.8, 6.4))
for ax, (tag, rem, title) in zip(axes, [
        ("closed", None, "闭合态 —— 质子候选 p\n(三条通道全部闭合, $\\beta_1$ = %d)" % RES["y3_closed"]["beta1"]),
        ("open", ("L22", "L02"), "开态 —— 中子候选 n\n(一条通道休眠未闭合, $\\beta_1$ = %d)" % RES["y3_open"]["beta1"])]):
    G, lea = y3(rem)
    pos = layout(lea)
    centers = ["c0", "c1", "c2"]
    leaves = [v for v in G if v not in centers]

    # 边分类：股内辐条 / 环边 / 休眠边
    ring = set()
    for j in range(3):
        ring.add(frozenset((lea[(0, j)], lea[(1, j)])))
        ring.add(frozenset((lea[(1, j)], lea[(2, j)])))
        ring.add(frozenset((lea[(2, j)], lea[(0, j)])))
    broken = {frozenset(("L22", "L02"))} if rem else set()

    for u, v in G.edges():
        fs = frozenset((u, v))
        if fs in broken:
            col, lw, ls, z = "#c0392b", 2.6, "--", 2
        elif fs in ring:
            col, lw, ls, z = "#1f77b4", 2.4, "-", 1
        else:
            col, lw, ls, z = "#7f8c8d", 1.6, "-", 0
        xs = [pos[u][0], pos[v][0]]
        ys = [pos[u][1], pos[v][1]]
        ax.plot(xs, ys, color=col, lw=lw, ls=ls, zorder=z, solid_capstyle="round")

    nx.draw_networkx_nodes(G, pos, nodelist=leaves, node_size=430,
                           node_color="#ffffff", edgecolors="#1f77b4", linewidths=2.0, ax=ax)
    nx.draw_networkx_nodes(G, pos, nodelist=centers, node_size=700,
                           node_color="#fdebd0", edgecolors="#d35400", linewidths=2.2, ax=ax)

    ax.set_title(title, fontsize=12.5, pad=14)
    ax.text(0.5, -0.10, "橙色 = 股心(3)   蓝色 = 环上叶点(9)   实线环边 = 闭合通道   红色虚线 = 休眠边",
            transform=ax.transAxes, ha="center", fontsize=9.5, color="#555555")
    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.margins(0.14)

fig.suptitle("核子骨架候选：三股 Y 的三角闭合体   $\\mathrm{Y}_3\\ltimes\\triangle_3$   "
             "($V$=%d, $E$=%d, $|\\mathrm{Aut}|$=%d, $\\lambda_2/\\rho$=%.6f)"
             % (RES["y3_closed"]["V"], RES["y3_closed"]["E"],
                RES["y3_closed"]["aut"], RES["y3_closed"]["lambda2_over_rho"]),
             fontsize=14, y=0.99)
fig.tight_layout(rect=[0, 0.02, 1, 0.95])
for ext in ("png", "svg"):
    fig.savefig("sre_nucleon_skeleton_structure.%s" % ext, dpi=170, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- 图 (b) 漏斗
fig, ax = plt.subplots(figsize=(11.2, 6.0))
steps = [
    ("$V$=12 立方连通图\n(不同构全体)",
     RES["criterion_2_pool"]["n_graphs"], "#95a5a6",
     "由判据 ① 定出 $V$=12"),
    ("判据 ② 谱比\n$\\lambda_2/\\rho$ 落在目标 3% 内",
     RES["criterion_3"]["n_after_crit2"], "#2980b9",
     "目标 $\\kappa=(m_n-m_p)/m_p\\div\\alpha$ = %.6f" % RES["targets"]["kappa"]),
    ("判据 ③ 三重对称\n$3\\mid|\\mathrm{Aut}|$",
     RES["criterion_3"]["n_after_crit3"], "#c0392b",
     "三股骨架的结构要求"),
]
ymax = steps[0][1]
xs = [0.06, 0.38, 0.70]
for i, (lab, n, col, note) in enumerate(steps):
    w = 0.30 * (n / ymax) ** 0.45 + 0.10
    h = 0.16
    y = 0.66 - i * 0.24
    ax.add_patch(FancyBboxPatch((xs[i], y), w, h, boxstyle="round,pad=0.008,rounding_size=0.03",
                                facecolor=col, edgecolor="none", alpha=0.90))
    ax.text(xs[i] + w / 2, y + h / 2 + 0.045, "n = %d" % n,
            ha="center", va="center", fontsize=15, color="white", fontweight="bold")
    ax.text(xs[i] + w / 2, y - 0.045, lab, ha="center", va="top", fontsize=10.5, color="#222222")
    ax.text(xs[i] + w / 2, y - 0.105, note, ha="center", va="top", fontsize=9, color="#666666")
    if i < len(steps) - 1:
        ax.annotate("", xy=(xs[i + 1] - 0.015, y - 0.24 + h / 2), xytext=(xs[i] + w, y + h / 2),
                    arrowprops=dict(arrowstyle="-|>", color="#888888", lw=1.6))

ax.text(0.06, 0.94, "核子骨架三步筛选（判据先于数值，非事后拟合）", fontsize=14, fontweight="bold")
ax.text(0.06, 0.87, "联合稀有度：判据 ②③ 命中率 %.3f ；再乘 V 档 1/5 → p ≈ %.1e"
        % (RES["rarity"]["p_crit23"], RES["rarity"]["p_joint"]), fontsize=11, color="#b03a2e")
ax.set_xlim(0, 1.05)
ax.set_ylim(-0.16, 1.0)
ax.set_axis_off()
for ext in ("png", "svg"):
    fig.savefig("sre_nucleon_skeleton_funnel.%s" % ext, dpi=170, bbox_inches="tight")
plt.close(fig)

print("figures written")
