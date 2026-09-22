"""核子图验证绘图：λ2(M)/λ2_q(M) 壳层图 vs 几何负对照 + MDS 涌现几何。"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = json.load(open(r"C:\mywork\vasp\sre_nucleon_graph_results.json"))
scan = R["scan"]
sh = scan["shell_graph_scan"]
ge = scan["geometric_graph_scan"]
MAGIC = scan["magic_numbers"]

Ms = [r["M"] for r in sh]
l2s = [r["lambda2"] for r in sh]
l2sq = [r["lambda2_q_sre_weighted"] for r in sh]
nl = [r["n_loops"] for r in sh]
l2g = [r["lambda2"] for r in ge]
l2gq = [r["lambda2_q_sre_weighted"] for r in ge]

# ---- Fig A: two panels, bare λ2 (registers magic) vs SRE λ2_q (washed out) ----
fig, (axa, axb) = plt.subplots(1, 2, figsize=(14, 5))

axa.plot(Ms, l2s, "-o", ms=3, color="#c0392b", label="shell/pairing graph")
axa.plot(Ms, l2g, "-s", ms=3, color="#2980b9", label="geometric graph (neg. control)")
for m in MAGIC:
    axa.axvline(m, color="gray", ls=":", lw=0.8, alpha=0.6)
    axa.text(m, max(l2s) * 0.98, f"{m}", color="gray", fontsize=8, rotation=90, va="top")
axa.set_xlabel("nucleon count M"); axa.set_ylabel("algebraic connectivity  λ₂")
axa.set_title("(a) bare binary-graph λ₂\nshell closures appear as steps; geometric control is flat")
axa.legend(fontsize=8, loc="upper right"); axa.grid(alpha=0.25)

axb.plot(Ms, l2sq, "-o", ms=3, color="#c0392b", label="shell/pairing graph")
axb.plot(Ms, l2gq, "-s", ms=3, color="#2980b9", label="geometric graph (neg. control)")
for m in MAGIC:
    axb.axvline(m, color="gray", ls=":", lw=0.8, alpha=0.6)
axb.set_xlabel("nucleon count M"); axb.set_ylabel("SRE smooth-adjacency  λ₂ᵩ")
axb.set_title("(b) SRE operator λ₂ᵩ\nsize-dominated → magic signature washed out")
axb.legend(fontsize=8, loc="upper left"); axb.grid(alpha=0.25)

fig.tight_layout()
fig.savefig(r"C:\mywork\vasp\sre_nucleon_lambda2_scan.png", dpi=130)
print("[OK] sre_nucleon_lambda2_scan.png")

# ---- Fig B: n_loops(M) shell ----
fig2, ax2 = plt.subplots(figsize=(11, 4))
ax2.plot(Ms, nl, "-", color="#27ae60", lw=1.5)
for m in MAGIC:
    ax2.axvline(m, color="gray", ls=":", lw=0.8, alpha=0.6)
ax2.set_xlabel("nucleon count M")
ax2.set_ylabel("cyclomatic number  n_loops (E − V + C)")
ax2.set_title("shell-graph n_loops grows monotonically — NOT a magic-number discriminator")
ax2.grid(alpha=0.25)
fig2.tight_layout()
fig2.savefig(r"C:\mywork\vasp\sre_nucleon_nloops.png", dpi=130)
print("[OK] sre_nucleon_nloops.png")

# ---- Fig C: MDS emergent geometry ----
mn = R["mds_nuclei"]
fig3 = plt.figure(figsize=(12, 4))
for ci, (name, d) in enumerate(mn.items()):
    X = np.array(d["mds_coords"])
    Z = d["Z"]
    ax3 = fig3.add_subplot(1, 3, ci + 1, projection="3d")
    ax3.scatter(X[:Z, 0], X[:Z, 1], X[:Z, 2], c="#c0392b", s=50, label="proton")
    ax3.scatter(X[Z:, 0], X[Z:, 1], X[Z:, 2], c="#2980b9", s=50, label="neutron")
    ax3.set_title(f"{name} (Z={Z}, N={d['N']})\nMDS from pure relation graph, no coords")
    ax3.set_box_aspect((1, 1, 1))
    ax3.set_xticks([]); ax3.set_yticks([]); ax3.set_zticks([])
    ax3.legend(fontsize=7, loc="upper left")
fig3.suptitle("Geometry emerges from nucleon relation graph via MDS inversion "
              "(high shell symmetry → symmetric embedding)", fontsize=11)
fig3.tight_layout(rect=[0, 0, 1, 0.92])
fig3.savefig(r"C:\mywork\vasp\sre_nucleon_mds.png", dpi=130)
print("[OK] sre_nucleon_mds.png")
