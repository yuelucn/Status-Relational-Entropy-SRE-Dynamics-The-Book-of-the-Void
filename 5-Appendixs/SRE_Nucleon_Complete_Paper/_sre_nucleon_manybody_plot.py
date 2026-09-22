# -*- coding: utf-8 -*-
"""第 12 章配图：共享环拼接 + 记分卡。

用法：python _sre_nucleon_manybody_plot.py [zh|en]
输出：figures/sre_nucleon_manybody_schematic[_EN].png / .svg
"""
import os
import sys
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import networkx as nx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TXT = {
    "zh": dict(
        title="多体拼接律与共享环：拼接示意、参照模不变性与零参数记分卡",
        a_title="(a) 共享环拼接（单体 → 两体 → 四体）",
        a1="单体（闭态质子）\n三股 Y 三角闭合体（V=12）",
        a2="两体共享环（氘核）\nV=21，账本 (1, 2, 2)",
        a3="四体共享环（$^{4}$He）\nV=39，账本 (2, 4, 4)",
        leg1="实线粗边：共享环上被全体共称的边（k = A）",
        leg2="虚线红边：仅由质子声称的边（k = #p）—— 单方声称边",
        leg3="蓝点：闭态（质子，环边完整）；红点：开态（中子，该位置环边休眠）",
        arrow="拼接：各体把同一环（三点）并入共享区",
        b_title="(b) 参照模不变性与闭合度势",
        b_x="共享环的体数 $k$",
        b_y1="闭合度势 $\\rho$（最大 Laplacian 特征值）",
        b_y2="最低非平凡模 $\\lambda_2$",
        b_note="$\\lambda_2=2-\\sqrt{3}=0.267949$ 与体数无关（参照模）",
        c_title="(c) 拼接律零参数记分卡（读法甲）",
        c_note="读法甲（当且仅当）：$1\\leq g\\leq 2$ 且 $s\\geq 1$ 判为合法。全部 8 项命中 7；A ≤ 3 分区 5/5；唯一失配 $^{4}$Li。",
        ok="√", no="×",
        cols=["体系", "A", "缺口 $g$", "供给 $s$", "判定", "实测", "命中"],
        rows=[["n-p", "2", "1", "1", "合法", "束缚 2.2246 MeV", "√"],
              ["n-n", "2", "2", "0", "非法", "不束缚（虚态）", "√"],
              ["p-p", "2", "0", "2", "非法", "不束缚（虚态）", "√"],
              ["$^{3}$H", "3", "2", "1", "合法", "束缚 8.4820 MeV", "√"],
              ["$^{3}$He", "3", "1", "2", "合法", "束缚 7.7181 MeV", "√"],
              ["$^{4}$He", "4", "2", "2", "合法", "束缚 28.2957 MeV", "√"],
              ["$^{4}$H", "4", "3", "1", "非法", "不束缚（阈上共振）", "√"],
              ["$^{4}$Li", "4", "1", "3", "合法", "不束缚（阈上共振）", "×"]],
        fname="sre_nucleon_manybody_schematic",
    ),
    "en": dict(
        title="Many-body assembly law and shared ring: assembly, reference mode, and zero-parameter scorecard",
        a_title="(a) Shared-ring assembly (monomer → two bodies → four bodies)",
        a1="Monomer (closed proton)\nthree-strand Y triangle closed body (V=12)",
        a2="Two bodies sharing one ring (deuteron)\nV=21, ledger (1, 2, 2)",
        a3="Four bodies sharing one ring ($^{4}$He)\nV=39, ledger (2, 4, 4)",
        leg1="Thick solid edge: shared-ring edge claimed by all bodies (k = A)",
        leg2="Dashed red edge: edge claimed by protons only (k = #p) — single-claim edge",
        leg3="Blue dot: closed state (proton, ring edge intact); red dot: open state (neutron, ring edge dormant)",
        arrow="each body merges the same ring",
        b_title="(b) Reference-mode invariance and closure potential",
        b_x="number of bodies sharing the ring, $k$",
        b_y1="closure potential $\\rho$ (largest Laplacian eigenvalue)",
        b_y2="lowest non-trivial mode $\\lambda_2$",
        b_note="$\\lambda_2=2-\\sqrt{3}=0.267949$ (independent of $k$)",
        c_title="(c) Zero-parameter scorecard of the assembly law (reading A)",
        c_note="Reading A (iff): legal when $1\\leq g\\leq 2$ and $s\\geq 1$. Hits 7 of 8; 5/5 on A ≤ 3; the only mismatch is $^{4}$Li.",
        ok="√", no="×",
        cols=["system", "A", "g", "s", "verdict", "measured", "hit"],
        rows=[["n-p", "2", "1", "1", "legal", "bound 2.2246 MeV", "√"],
              ["n-n", "2", "2", "0", "illegal", "unbound (virtual)", "√"],
              ["p-p", "2", "0", "2", "illegal", "unbound (virtual)", "√"],
              ["$^{3}$H", "3", "2", "1", "legal", "bound 8.4820 MeV", "√"],
              ["$^{3}$He", "3", "1", "2", "legal", "bound 7.7181 MeV", "√"],
              ["$^{4}$He", "4", "2", "2", "legal", "bound 28.2957 MeV", "√"],
              ["$^{4}$H", "4", "3", "1", "illegal", "unbound (resonance)", "√"],
              ["$^{4}$Li", "4", "1", "3", "legal", "unbound (resonance)", "×"]],
        fname="sre_nucleon_manybody_schematic_EN",
    ),
}

RING = "#1f4e79"          # 共享环 / 闭态
PART = "#c00000"          # 单方声称边 / 开态
SPOKE = "#9aa5b1"         # 股心辐条
BODY_C = "#1f4e79"
BODY_N = "#c00000"


def Y3(pre):
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("%sL%d%d" % (pre, a, j), "%sL%d%d" % (pre, b, j))
    return G


def shared_ring(k):
    G = nx.Graph()
    for b in range(k):
        pre = "b%d_" % b
        m = {"%sL%d0" % (pre, i): "S%d" % i for i in range(3)}
        G.add_edges_from({tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in Y3(pre).edges()})
    return G


def motif(ax, cx, cy, k, n_open, R=1.02, rh=0.46, caption="", profile=""):
    ang = (90, 210, 330)
    V = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in ang]
    # 共享环：边 (v0,v1) 为单方声称边（仅当存在开态体时才画成虚线）
    for (i, j), style in (((0, 1), "part"), ((1, 2), "full"), ((2, 0), "full")):
        x = [V[i][0], V[j][0]]
        y = [V[i][1], V[j][1]]
        if style == "part" and n_open >= 1:
            ax.plot(x, y, ls=(0, (4, 2.5)), lw=2.0, color=PART, zorder=2)
        else:
            ax.plot(x, y, lw=3.4, color=RING, zorder=2)
    # 各体的股心与辐条
    for b in range(k):
        if k == 1:
            hx, hy = cx, cy
        else:
            a0 = 90 if k == 2 else 45
            a = a0 + b * (360.0 / k)
            hx = cx + rh * math.cos(math.radians(a))
            hy = cy + rh * math.sin(math.radians(a))
        for vx, vy in V:
            ax.plot([hx, vx], [hy, vy], lw=0.9, color=SPOKE, zorder=1)
        col = BODY_N if b < n_open else BODY_C
        ax.add_patch(Circle((hx, hy), 0.115, facecolor=col, edgecolor="white", lw=0.8, zorder=4))
    ax.text(cx, cy - R - 0.52, caption, ha="center", va="top", fontsize=9.2, linespacing=1.45)
    if profile:
        ax.text(cx, cy - R - 1.16, profile, ha="center", va="top", fontsize=9.0,
                color="#333333", linespacing=1.4)


def panel_a(ax, T):
    ax.set_xlim(0, 12.6)
    ax.set_ylim(-1.85, 2.75)
    ax.axis("off")
    motif(ax, 1.75, 1.35, 1, 0, caption=T["a1"])
    motif(ax, 6.3, 1.35, 2, 1, caption=T["a2"])
    motif(ax, 10.55, 1.35, 4, 2, caption=T["a3"])
    for x0, x1 in ((3.6, 4.45), (8.2, 9.0)):
        ax.annotate("", xy=(x1, 1.35), xytext=(x0, 1.35),
                    arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#444444"))
    ax.text(4.02, 1.75, T["arrow"], ha="center", fontsize=8.4, color="#444444")
    ax.text(0.05, -0.95, "\n".join(["● " + T["leg1"], "● " + T["leg2"], "● " + T["leg3"]]),
            ha="left", va="top", fontsize=8.6, linespacing=1.7, color="#222222")
    ax.set_title(T["a_title"], loc="left", fontsize=10.5, fontweight="bold")


def panel_b(ax, T):
    ks = [2, 3, 4, 5, 6]
    rho, lam = [], []
    for k in ks:
        ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(shared_ring(k)).toarray()))
        rho.append(float(ev[-1]))
        lam.append(float(ev[1]))
    print("  体数 k=%s" % ks)
    print("  rho   =%s" % ["%.6f" % v for v in rho])
    print("  lam2  =%s" % ["%.9f" % v for v in lam])
    print("  lam2 - (2-sqrt3) 最大偏差 = %.2e" % max(abs(v - (2 - math.sqrt(3))) for v in lam))
    ax.plot(ks, rho, "o-", color=RING, lw=2.0, ms=6.5, label="$\\rho$")
    ax.set_xlabel(T["b_x"], fontsize=9.5)
    ax.set_ylabel(T["b_y1"], fontsize=9.5)
    ax.set_ylim(5.4, 10.6)
    ax.grid(alpha=0.25)
    ax2 = ax.twinx()
    ax2.plot(ks, lam, "s--", color=PART, lw=1.8, ms=6.0, label="$\\lambda_2$")
    ax2.axhline(2 - math.sqrt(3), color=PART, lw=0.9, ls=":", alpha=0.7)
    ax2.set_ylim(0.0, 1.4)
    ax2.yaxis.set_major_locator(plt.MultipleLocator(0.2))
    ax2.set_ylabel(T["b_y2"], fontsize=9.5)
    ax2.text(2.02, 0.035, T["b_note"], fontsize=8.6, color=PART)
    ax.set_title(T["b_title"], loc="left", fontsize=10.5, fontweight="bold")
    ax.set_xticks(ks)


def panel_c(ax, T):
    ax.axis("off")
    tbl = ax.table(cellText=T["rows"], colLabels=T["cols"], loc="upper center",
                   cellLoc="center", colWidths=[0.12, 0.055, 0.10, 0.10, 0.10, 0.33, 0.075])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8.6)
    tbl.scale(1.0, 1.55)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("#b8c2cc")
        if r == 0:
            cell.set_facecolor("#e8eef5")
            cell.set_text_props(fontweight="bold")
        elif c == 6:
            ok = cell.get_text().get_text() == T["ok"]
            cell.set_text_props(color="#1a7f37" if ok else PART, fontweight="bold", fontsize=11)
            if not ok:
                cell.set_facecolor("#fdecea")
        else:
            cell.set_facecolor("#ffffff" if r % 2 else "#f7f9fb")
    ax.set_title(T["c_title"], loc="left", fontsize=10.5, fontweight="bold")
    ax.text(0.0, 0.03, T["c_note"], transform=ax.transAxes, fontsize=8.6,
            va="bottom", color="#333333")


def main(lang="zh"):
    T = TXT[lang]
    if lang == "zh":
        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    else:
        plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    os.makedirs("figures", exist_ok=True)

    fig = plt.figure(figsize=(12.8, 9.4), dpi=150)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], width_ratios=[1.0, 1.42],
                          hspace=0.24, wspace=0.22)
    axA = fig.add_subplot(gs[0, :])
    axB = fig.add_subplot(gs[1, 0])
    axC = fig.add_subplot(gs[1, 1])

    panel_a(axA, T)
    panel_b(axB, T)
    panel_c(axC, T)

    fig.suptitle(T["title"], fontsize=12.5, y=0.985)
    out = os.path.join("figures", T["fname"])
    for ext in ("png", "svg"):
        fig.savefig("%s.%s" % (out, ext), bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("已生成: %s.png / %s.svg" % (out, out))
    print("done")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "zh")
