import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d = json.load(open(r"C:\mywork\vasp\sre_nucleon_quark_guess_results.json"))
MAGIC = d["magic_numbers"]
A = np.array(list(range(2, 131)))

fig, ax = plt.subplots(1, 2, figsize=(14, 5.2))
styles = [
    ("borrowed_shell", "#1f77b4", "borrowed shell-cap (encodes magic)", "-"),
    ("geometric", "#999999", "geometric packing (NULL)", "-"),
    ("quark_geometric", "#d62728", "quark Z3xZ2 + geometric (GUESS)", "--"),
]
# panel 1: normalized lambda2
for key, c, lab, ls in styles:
    lam = np.array(d["results"][key]["lambda2"], float)
    lam = lam / lam.max()
    ax[0].plot(A, lam, color=c, lw=1.6, ls=ls,
               label=f"{lab}  z={d['results'][key]['z']:.2f}")
for m in MAGIC:
    ax[0].axvline(m, color="orange", ls=":", lw=1.0, alpha=0.6)
ax[0].set_xlabel("mass number A"); ax[0].set_ylabel("normalized  lambda2 / max")
ax[0].set_title("Normalized lambda2(A)  (guess overlaps NULL)")
ax[0].legend(loc="upper left", fontsize=8.5)

# panel 2: relative step |dlambda/lambda|
for key, c, lab, ls in styles:
    lam = np.array(d["results"][key]["lambda2"], float)
    step = np.abs(np.diff(lam) / np.where(lam[:-1] != 0, lam[:-1], 1))
    ax[1].semilogy(A[:-1], step + 1e-6, color=c, lw=1.3, ls=ls, label=lab)
for m in MAGIC:
    ax[1].axvline(m, color="orange", ls=":", lw=1.0, alpha=0.6)
ax[1].set_xlabel("mass number A"); ax[1].set_ylabel("|relative step|  dlambda/lambda")
ax[1].set_title("Relative step magnitude (magic = orange dashed)")
ax[1].legend(loc="upper right", fontsize=8.5)

fig.tight_layout()
fig.savefig(r"C:\mywork\vasp\sre_nucleon_quark_guess_figure.png", dpi=130)
print("[OK] sre_nucleon_quark_guess_figure.png")
