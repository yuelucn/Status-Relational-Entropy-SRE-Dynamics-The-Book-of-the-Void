# -*- coding: utf-8 -*-
"""
SRE 核反应验证 · 配图 2：复合核激发盈余 vs 热截面相关 + 快中子收缩
生成 sre_fission_chain_corr.png/.svg 与 sre_fission_chain_decades.pdf/.png缩对比
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = ["sans-serif"]
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "dejavusans"

# ----------------------------------------------------- 图 1：Δ vs log10 σ_th
RESID = [
    ("U-233", 6.8455, 5.50, 531.3, "teal"),
    ("U-235", 6.5455, 5.67, 585.1, "teal"),
    ("Pu-239", 6.5342, 6.05, 747.4, "teal"),
    ("Am-241", 5.5287, 5.90, 3.122, "amber"),
    ("Np-237", 5.4882, 6.10, 0.02019, "gray"),
    ("Pu-240", 5.2415, 6.10, 0.03621, "gray"),
    ("Pu-242", 5.0336, 5.80, 0.002436, "gray"),
    ("Th-232", 4.7863, 5.80, 53.71e-6, "gray"),
    ("U-238", 4.8063, 6.20, 16.8e-6, "gray"),
]
colmap = {"teal": "#0F6E56", "amber": "#BA7517", "gray": "#5F5E5A"}

deltas = np.array([e - b for _, e, b, _, _ in RESID])
logs = np.array([np.log10(m) for _, _, _, m, _ in RESID])

fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.4))

for (nm, e, b, m, cg), d, lg in zip(RESID, deltas, logs):
    ax[0].scatter(d, lg, s=120, color=colmap[cg], edgecolor="black", linewidth=0.8, zorder=3)
    off = (8, -9) if d > 0 else (8, 9)
    ax[0].annotate(nm, (d, lg), textcoords="offset points", xytext=off, fontsize=11)

# 线性拟合
coef = np.polyfit(deltas, logs, 1)
xs = np.linspace(deltas.min() - 0.1, deltas.max() + 0.1, 100)
ax[0].plot(xs, np.polyval(coef, xs), color="#888780", lw=1.2, ls="--", alpha=0.9)
ax[0].axvline(0, color="#A32D2D", lw=1.0, ls=":")
ax[0].text(0.05, -4.4, r"$\Delta=0$", color="#A32D2D", fontsize=11)
r = np.corrcoef(deltas, logs)[0, 1]
ax[0].set_xlabel(r"复合核激发盈余 $\Delta = E^{*}-B_f$  (MeV)")
ax[0].set_ylabel(r"$\log_{10}\,\sigma_{\rm th}$  (b)")
ax[0].set_title("激发盈余 vs 热中子裂变截面", fontsize=13)
ax[0].text(0.03, 0.95, f"Pearson r = +{r:.3f}\n(n = 9 靶核)",
           transform=ax[0].transAxes, fontsize=12, va="top",
           bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#B4B2A9", lw=0.8))
ax[0].grid(alpha=0.3)
ax[0].set_ylim(-5.3, 3.4)

# ----------------------------------------------------- 图 2：热 vs 快 数量级跨度
cats = ["热中子 σ_th", "快中子 σ_fast", "快(去Th-232)", "热 1-99分位", "快 10-90分位"]
vals = [8.58, 1.48, 0.90, 8.39, 0.40]
cols = ["#A32D2D", "#0F6E56", "#1D9E75", "#D85A30", "#378ADD"]
bars = ax[1].barh(cats, vals, color=cols, edgecolor="black", linewidth=0.7, height=0.6)
for b, v in zip(bars, vals):
    ax[1].text(v + 0.12, b.get_y() + b.get_height() / 2, f"{v:.2f} 数量级",
               va="center", fontsize=11)
ax[1].set_xlabel("动态范围（数量级）")
ax[1].set_title("快中子实验：差异集中在低能沉降端", fontsize=13)
ax[1].grid(axis="x", alpha=0.3)
ax[1].set_xlim(0, 10)
ax[1].text(0.02, -0.7,
           "热截面跨度 ~8.6 数量级 → 快中子恢复至同量级（差异不在总裂变能力，而在低能耗沉降）",
           transform=ax[1].transAxes, fontsize=10.5, color="#444441")

fig.suptitle("SRE 核反应验证：闭合度势判据与快中子实验", fontsize=15, fontweight="medium")
plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig("sre_fission_chain_corr.png", dpi=150, bbox_inches="tight")
plt.savefig("sre_fission_chain_corr.svg", bbox_inches="tight")
print("saved sre_fission_chain_corr.png/.svg")
