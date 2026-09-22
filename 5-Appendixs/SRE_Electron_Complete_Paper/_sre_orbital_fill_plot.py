# -*- coding: utf-8 -*-
"""
SRE 电子轨道填充规律 — 示意图 (程序生成)
========================================
三面板:
  A  态空间 16 单胞: Q3 8 顶点 x Moebius 双覆盖 2 片; 每单胞容量 1(泡利=单元唯一性)
  B  容量砖墙: 壳层 2n^2 = 2,8,18,32; 累计 = 60 = 电子本体计数(12x5)
  C  Madelung 对角填充图: (n,l) 网格 + 构造次序路径, 以 Z=26 Fe 为例染色

说明: 数学符号用 mathtext ($...$); 中文用系统中文字体(Microsoft YaHei)。
      本图为 SRE 模型内部构造的图示, 非现实轨道填充的直接测量。
"""
import os
import importlib.util

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))

C_FIX   = "#1f77b4"   # 已填充 / 固定(蓝)
C_PLUS  = "#d62728"   # 自旋 + (红)
C_MINUS = "#3182bd"   # 自旋 - (蓝)
C_GREY  = "#999999"
C_EMPTY = "#d9d9d9"

LETTER = {0: "s", 1: "p", 2: "d", 3: "f", 4: "g", 5: "h"}


def setup_cjk_font():
    candidates = ["Microsoft YaHei", "SimHei", "SimSun",
                  "PingFang SC", "Noto Sans CJK SC"]
    avail = {f.name for f in font_manager.fontManager.ttflist}
    for c in candidates:
        if c in avail:
            plt.rcParams["font.sans-serif"] = [c, "DejaVu Sans"]
            plt.rcParams["axes.unicode_minus"] = False
            return c
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
    return None


def load_assignment():
    spec = importlib.util.spec_from_file_location(
        "orb", os.path.join(HERE, "_sre_orbital_assignment.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ A: 16 单胞
def panel_cells(ax, mod):
    ax.set_title("A  态空间 16 单胞 = $Q_3$ 八顶点 $\\times$ Möbius 双覆盖两片\n"
                 "$(v,\\sigma)$, $v\\in\\{0,1\\}^{3}$, $\\sigma\\in\\{+1,-1\\}$;\n"
                 "每单胞容量 1 (泡利 = 单元唯一性)",
                 fontsize=10, pad=8)
    Q = nx.hypercube_graph(3)
    pos = {}
    for nd in Q.nodes():
        b0, b1, b2 = nd
        pos[nd] = (b0 + 0.35 * b1, b2 + 0.35 * b1)
    pos = nx.rescale_layout_dict(pos)
    for u, v in Q.edges():
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
                color=C_GREY, lw=1.1, zorder=1)
    # 每个顶点画两个自旋片单元(±偏移)
    for nd in Q.nodes():
        x, y = pos[nd]
        for sgn, dx, c in [("+", -0.06, C_PLUS), ("-", 0.06, C_MINUS)]:
            ax.add_patch(plt.Circle((x + dx, y), 0.060, fc="white",
                                    ec=c, lw=1.4, zorder=3))
    # 例: 显示一对自旋受限的已占单胞(如 000 顶点两片均占)
    ex = pos[(0, 0, 0)]
    ax.add_patch(plt.Circle((ex[0] - 0.06, ex[1]), 0.075, fc=C_PLUS,
                            ec="black", lw=1.2, zorder=4))
    ax.add_patch(plt.Circle((ex[0] + 0.06, ex[1]), 0.075, fc=C_MINUS,
                            ec="black", lw=1.2, zorder=4))
    ax.annotate("一轨道两片可并占(自旋相反)\n仍守每单胞容量 1",
                xy=(ex[0], ex[1]), xytext=(ex[0] + 0.5, ex[1] - 0.6),
                fontsize=7, color="#333333",
                arrowprops=dict(arrowstyle="-|>", color="#333333", lw=0.9))
    ax.text(0.0, -1.05, "忠实覆盖: 16 行关系模式两两不同;\n强制双占 -> 覆盖退化(全同行)",
            ha="center", fontsize=7.5, color=C_GREY)
    ax.set_xlim(-1.3, 1.3); ax.set_ylim(-1.35, 1.25)
    ax.set_aspect("equal"); ax.axis("off")


# ------------------------------------------------------------- B: 容量砖墙 -> 60
def panel_capacity(ax):
    ax.set_title("B  容量砖墙: $2n^2=\\sum_{\\ell<n}(4\\ell+2)$; 累计至 $n{=}4$ = $60$\n"
                 "(= 电子本体 $|E|\\times\\beta_{1}=12\\times5$; 同向指示, 非证明)",
                 fontsize=10, pad=8)
    nmax = 4
    xoff = 0.0
    rowlabels = {}
    for n in range(1, nmax + 1):
        x = xoff
        row_sum = 0
        for l in range(n):
            cap = 4 * l + 2
            w = cap / 4.0
            c = [C_FIX, "#ff7f0e", "#8c564b", "#2ca02c"][l]
            ax.add_patch(plt.Rectangle((x, nmax - n), w, 0.82, fc=c,
                                       ec="white", alpha=0.85))
            ax.text(x + w / 2, nmax - n + 0.41,
                    f"$\\ell{l}$\n${cap}$", ha="center", va="center",
                    fontsize=7, color="white")
            x += w + 0.06
            row_sum += cap
        rowlabels[nmax - n + 0.41] = f"$n={n}$: ${row_sum} (=2n^2)$"
        xoff = max(xoff, x)
    for y, s in rowlabels.items():
        ax.text(xoff + 0.1, y, s, ha="left", va="center", fontsize=7.5,
                color="#333333")
    ax.annotate("", xy=(xoff, 0.2), xytext=(xoff, nmax - 0.1),
                arrowprops=dict(arrowstyle="-|>", color=C_PLUS, lw=1.6))
    ax.text(xoff + 0.14, nmax / 2, "累计\n$2+8+18+32=60$",
            ha="left", va="center", fontsize=8.5, color=C_PLUS,
            fontweight="bold")
    ax.set_xlim(-0.3, xoff + 2.3)
    ax.set_ylim(-0.2, nmax + 0.5)
    ax.axis("off")


# ------------------------------------------------ C: Madelung 对角填充 (Z=26)
def panel_madelung(ax):
    mod = load_assignment()
    Z = 26
    occ, _ = mod.config_for_Z(Z)
    path = mod.aufbau_sequence(nmax=8)
    ax.set_title("C  Madelung 对角构造: $Z{=}26$ (Fe) 的 $(n,\\ell)$ 网格\n"
                 "红折线 = 构造序 (按 $n+\\ell$ 升序);  灰带 = 同 $n+\\ell$ 层级",
                 fontsize=10, pad=8)
    nmax, lmax = 8, 5
    for d in range(2, nmax + lmax + 1):
        ax.axvspan(d - 0.5, d + 0.5, color="#f2f2f2", zorder=0)
        ax.text(d, nmax + 0.55, f"$n+\\ell={d}$", ha="center",
                fontsize=6.5, color="#aaaaaa")
    # 格子
    for n in range(1, nmax + 1):
        for l in range(min(lmax, n)):
            x, y = n + l, n
            filled = occ.get((n, l), 0)
            ccap = mod.subshell_capacity(l)
            frac = filled / ccap
            if (n, l) in occ and frac >= 1.0:
                col = C_FIX
            elif (n, l) in occ:
                col = "#a6c8e8"
            else:
                col = C_EMPTY
            ax.add_patch(plt.Rectangle((x - 0.42, y - 0.42), 0.84, 0.84,
                                       fc=col, ec="#666666", lw=0.6, zorder=2))
            txt = f"${n}$ {LETTER.get(l, str(l))}  ${filled}/{ccap}$"
            ax.text(x, y, txt, ha="center", va="center", fontsize=6.2,
                    color="#111111" if (n, l) in occ else "#888888", zorder=3)
    # 构造序红色折线(仅经过填充过的子壳)
    fill_seq = [(n, l) for n, l in path if (n, l) in occ]
    pts = [(n + l, n) for n, l in fill_seq]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], "o-", color=C_PLUS,
            lw=1.1, ms=3, alpha=0.8, zorder=1)
    ax.set_xlim(0.5, nmax + lmax + 0.7)
    ax.set_ylim(-0.7, nmax + 0.10)
    ax.set_xlabel("$n+\\ell$  (对角坐标)", fontsize=8.5)
    ax.set_ylabel("$n$  (壳层)", fontsize=8.5)
    ax.set_yticks(range(1, nmax + 1))
    ax.tick_params(labelsize=7)


def main():
    font = setup_cjk_font()
    print(f"[font] CJK font resolved: {font}", flush=True)

    mod = load_assignment()
    fig = plt.figure(figsize=(17, 7.5), dpi=160)
    gs = fig.add_gridspec(1, 3, wspace=0.32,
                          left=0.03, right=0.99, top=0.79, bottom=0.13)

    axa = fig.add_subplot(gs[0]); panel_cells(axa, mod)
    axb = fig.add_subplot(gs[1]); panel_capacity(axb)
    axc = fig.add_subplot(gs[2]); panel_madelung(axc)

    fig.suptitle("SRE 框架下的电子轨道分配规律:\n"
                 "泡利(单元唯一性) + 容量($2n^2$) + 构造序(开放项)",
                 fontsize=15, fontweight="bold", y=0.99, color="#0b3d66")
    fig.text(0.5, 0.032,
             "本图为 SRE 模型内部构造的示意图: A/B 为模型内部推导项, C 的 (n+ℓ) 次序为借用项。"
             "不构成现实轨道填充的直接测量陈述。",
             ha="center", fontsize=8, color="#666666")

    png = os.path.join(HERE, "sre_electron_orbital_fill.png")
    svg = os.path.join(HERE, "sre_electron_orbital_fill.svg")
    fig.savefig(png, dpi=160, bbox_inches="tight", facecolor="white")
    fig.savefig(svg, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"[OK] {png}", flush=True)
    print(f"[OK] {svg}", flush=True)


if __name__ == "__main__":
    main()
