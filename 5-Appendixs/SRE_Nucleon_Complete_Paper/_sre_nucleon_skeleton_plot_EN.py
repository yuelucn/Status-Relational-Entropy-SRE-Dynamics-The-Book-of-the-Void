# -*- coding: utf-8 -*-
"""
Nucleon skeleton inversion illustration (English version):
  (a) Structural schematic of tripartite Y-shaped triangular closure (closed / open states)
  (b) Three-step screening funnel (85 -> 4 -> 2) and rarity
Output: figures/sre_nucleon_skeleton_structure_EN.png/.svg ,
        figures/sre_nucleon_skeleton_funnel_EN.png/.svg
"""
import os
import json
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.unicode_minus"] = False

os.makedirs("figures", exist_ok=True)
RES = json.load(open("sre_nucleon_skeleton_inversion_results.json", encoding="utf-8"))


# ---------------------------------------------------------------- Skeleton construction
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
    # 3 peripheral triangles (rings)
    for j in range(3):
        th = np.pi / 2 + 2 * np.pi * j / 3
        cx, cy = 1.15 * np.cos(th), 1.15 * np.sin(th)
        for i in range(3):
            ph = th + 2 * np.pi * i / 3 + np.pi
            pos[lea[(i, j)]] = (cx + 0.42 * np.cos(ph), cy + 0.42 * np.sin(ph))
    # 3 centers (core strands)
    for i in range(3):
        ph = np.pi / 2 + 2 * np.pi * i / 3
        pos["c%d" % i] = (0.42 * np.cos(ph), 0.42 * np.sin(ph))
    return pos


# ---------------------------------------------------------------- Figure (a)
fig, axes = plt.subplots(1, 2, figsize=(12.8, 6.4))
for ax, (tag, rem, title) in zip(axes, [
        ("closed", None, "Closed State - Proton Candidate p\n(All three channels closed, $\\beta_1$ = %d)" % RES["y3_closed"]["beta1"]),
        ("open", ("L22", "L02"), "Open State - Neutron Candidate n\n(One channel dormant, $\\beta_1$ = %d)" % RES["y3_open"]["beta1"])]):
    G, lea = y3(rem)
    pos = layout(lea)
    centers = ["c0", "c1", "c2"]
    leaves = [v for v in G if v not in centers]

    # Edge classification: spoke edges / ring edges / dormant edges
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
    ax.text(0.5, -0.11, "Orange = Center Nodes (3)   Blue = Leaf Nodes on Rings (9)\n"
                        "Solid Ring Edges = Closed Channels   Red Dashed = Dormant Edges",
            transform=ax.transAxes, ha="center", va="top", fontsize=9.0,
            linespacing=1.5, color="#555555")
    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.margins(0.14)

fig.suptitle("Nucleon Skeleton Candidate: Tripartite Y-shaped Triangular Closure   "
             "$\\mathrm{Y}_3\\ltimes\\triangle_3$   "
             "($V$=%d, $E$=%d, $|\\mathrm{Aut}|$=%d, $\\lambda_2/\\rho$=%.6f)"
             % (RES["y3_closed"]["V"], RES["y3_closed"]["E"],
                RES["y3_closed"]["aut"], RES["y3_closed"]["lambda2_over_rho"]),
             fontsize=14, y=0.99)
fig.tight_layout(rect=[0, 0.03, 1, 0.90])
for ext in ("png", "svg"):
    fig.savefig("figures/sre_nucleon_skeleton_structure_EN.%s" % ext, dpi=170, bbox_inches="tight")
plt.close(fig)

# ---------------------------------------------------------------- Figure (b) Funnel
fig, ax = plt.subplots(figsize=(11.2, 6.2))
steps = [
    ("$V$=12 Cubic Connected Graphs\n(All Non-Isomorphic)",
     RES["criterion_2_pool"]["n_graphs"], "#95a5a6",
     "Criterion 1 fixes $V$=12"),
    ("Criterion 2 Spectral Ratio\n$\\lambda_2/\\rho$ within 3% of target",
     RES["criterion_3"]["n_after_crit2"], "#2980b9",
     "Target $\\kappa=(m_n-m_p)/m_p\\div\\alpha$ = %.6f" % RES["targets"]["kappa"]),
    ("Criterion 3 Tripartite Symmetry\n$3\\mid|\\mathrm{Aut}|$",
     RES["criterion_3"]["n_after_crit3"], "#c0392b",
     "Structural requirement of the tripartite skeleton"),
]

ymax = steps[0][1]
xs = [0.06, 0.38, 0.70]
hs = 0.15          # box height
pitch = 0.32       # vertical pitch between consecutive stages
y0 = 0.70          # top box bottom edge
centers = []
for i, (lab, n, col, note) in enumerate(steps):
    w = 0.32 * (n / ymax) ** 0.45 + 0.12
    y = y0 - i * pitch
    centers.append(xs[i] + w / 2)
    ax.add_patch(FancyBboxPatch((xs[i], y), w, hs,
                                boxstyle="round,pad=0.012,rounding_size=0.04",
                                facecolor=col, edgecolor="none", alpha=0.90))
    ax.text(xs[i] + w / 2, y + hs / 2, "n = %d" % n,
            ha="center", va="center", fontsize=14, color="white", fontweight="bold")
    # caption block placed fully inside the gap between this box and the next one
    n_lab = lab.count("\n") + 1
    ax.text(xs[i] + w / 2, y - 0.030, lab,
            ha="center", va="top", fontsize=9.5, color="#222222", linespacing=1.35)
    ax.text(xs[i] + w / 2, y - 0.030 - 0.046 * n_lab, note,
            ha="center", va="top", fontsize=7.5, color="#666666")

# vertical flow arrows drawn at the centre of the downstream box (never crosses captions)
for i in range(len(steps) - 1):
    xa = centers[i + 1]
    ax.annotate("",
                xy=(xa, y0 - (i + 1) * pitch + hs + 0.008),
                xytext=(xa, y0 - i * pitch - 0.008),
                arrowprops=dict(arrowstyle="-|>", color="#888888", lw=1.6))

ax.text(0.06, 0.97, "Nucleon Skeleton Three-Step Screening (Criteria Precede Values, Not Post-Hoc Fitting)",
        fontsize=13.5, fontweight="bold")
ax.text(0.06, 0.905, "Joint rarity: criteria 2+3 hit rate %.3f ; times V bin 1/5  ->  p ~ %.1e"
        % (RES["rarity"]["p_crit23"], RES["rarity"]["p_joint"]), fontsize=11, color="#b03a2e")
ax.set_xlim(0, 1.05)
ax.set_ylim(-0.14, 1.02)
ax.set_axis_off()
for ext in ("png", "svg"):
    fig.savefig("figures/sre_nucleon_skeleton_funnel_EN.%s" % ext, dpi=170, bbox_inches="tight")
plt.close(fig)

print("English figures written")
