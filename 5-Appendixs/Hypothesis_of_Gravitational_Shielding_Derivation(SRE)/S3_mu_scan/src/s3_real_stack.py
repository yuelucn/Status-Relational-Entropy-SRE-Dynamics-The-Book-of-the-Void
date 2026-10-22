"""S3 Phase 4 driver: matched z-bin f_sigma8 (real BOSS bins or synth) ->
GLS estimate of the SRE amplitude A -> honest alpha_scale lower bound.

Conventions kept IDENTICAL to Phase 1 / Phase 3 (s3_mu_scan.py / s3_zstack.py):
  model   y_i = s8 * U_i * (1 + B1' Rs_i + B2' Rc_i),  U = D'(ln a)/D0
  fit     full-covariance GLS (here diagonal per-bin sigma; the within-bin
          P0/P2 covariance was already folded into sigma_fs8 by the delta
          method; cross-bin/cross-cap covariances are negligible at k<=0.2
          for disjoint top-hat bins separated by >2pi/k in comoving distance)
  A       = hypot(B1, B2) / s8
  95%     r95 = sqrt(2.71 / lambda_min(profiled 2x2 info))
          A95_offsetfree  = r95 / s8
          A95_frequentist = (|B| + r95) / s8     (Rice-consistent, honest)
  gate    profile chi2 with A fixed at A_gate over (s8, phi); closed iff dchi2>2.71
  bound   alpha_min95 = C_8MPC / A95_frequentist

Inputs : results/fs8_boss_bins.csv          (mode=data, real BOSS)
         results/fs8_synth_A{0.0,0.509}.csv (mode=synth, validation)
Run:  C:\\myapp\\miniconda3\\envs\\ai\\python.exe S3_mu_scan/src/s3_real_stack.py data
      C:\\myapp\\miniconda3\\envs\\ai\\python.exe S3_mu_scan/src/s3_real_stack.py synth
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s3_fs8_bins as fb            # noqa: E402  (physics + constants, cross-checked)

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "S3_mu_scan" / "results"

PHI_GRID = np.linspace(0.0, 2 * np.pi, 721, endpoint=False)

# dense theory grids (same as Phase 3)
ZG = np.linspace(0.0, 2.0, 1601)
XG = -np.log1p(ZG)
RS_ALL, RC_ALL = fb.solve_responses(np.array([fb.K_DOC]), XG)
RS_ZG, RC_ZG = RS_ALL[0], RC_ALL[0]
UG = np.array([fb.BASE(x)[1] for x in XG]) / fb.D01


def bin_avg(z1, z2, arr):
    m = (ZG >= z1) & (ZG <= z2)
    return np.trapezoid(arr[m], ZG[m]) / (z2 - z1)


def load_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if not r.get("fs8"):
                continue
            out = {}
            for k, v in r.items():
                if k == "cap":
                    out[k] = v
                    continue
                try:
                    out[k] = float(v)
                except (TypeError, ValueError):
                    pass          # skip non-scalar columns (theta list, etc.)
            if not (np.isfinite(out.get("fs8", np.nan)) and
                    np.isfinite(out.get("sigma_fs8", np.nan))):
                continue
            rows.append(out)
    return rows


def theory_cols(rows):
    U, Rs, Rc = [], [], []
    for r in rows:
        U.append(bin_avg(r["z_lo"], r["z_hi"], UG))
        Rs.append(bin_avg(r["z_lo"], r["z_hi"], RS_ZG))
        Rc.append(bin_avg(r["z_lo"], r["z_hi"], RC_ZG))
    return np.array(U), np.array(Rs), np.array(Rc)


def gls_fit(y, sig, U, Rs, Rc):
    W = np.diag(1.0 / np.asarray(sig) ** 2)
    X = np.column_stack([U, U * Rs, U * Rc])
    M = X.T @ W @ X
    beta = np.linalg.solve(M, X.T @ W @ y)
    s8, B1p, B2p = beta
    B = float(np.hypot(B1p, B2p))
    Mpp = M[1:, 1:] - np.outer(M[1:, 0], M[0, 1:]) / M[0, 0]
    r95 = float(np.sqrt(2.71 / np.linalg.eigvalsh(Mpp)[0]))
    r = y - X @ beta
    chi2 = float(r @ W @ r)

    def chi2_fixed(A):
        cs, cc = A * np.cos(PHI_GRID), A * np.sin(PHI_GRID)
        cols = U[None, :] * (1.0 + cs[:, None] * Rs[None, :] + cc[:, None] * Rc[None, :])
        CM = cols @ W
        cc2 = np.einsum("ij,ij->i", CM, cols)
        cby = CM @ y
        mu = cby / cc2
        rr = y[None, :] - mu[:, None] * cols
        c2 = np.einsum("ij,jk,ik->i", rr, W, rr)
        j = int(np.argmin(c2))
        return float(c2[j]), float(PHI_GRID[j])

    chi2_gate, phi_gate = chi2_fixed(fb.A_GATE)
    return {"s8": float(s8), "B1p": float(B1p), "B2p": float(B2p), "A": float(B / s8),
            "phi": float(np.arctan2(B2p, B1p)), "chi2": chi2, "dof": int(y.size - 3),
            "r95": r95, "A95_offsetfree": float(r95 / s8),
            "A95_frequentist": float((B + r95) / s8),
            "chi2_gate": chi2_gate, "phi_gate": phi_gate,
            "dchi2_gate": chi2_gate - chi2,
            "gate_closed": bool(chi2_gate - chi2 > 2.71),
            "alpha_min95": float(fb.C_8MPC / ((B + r95) / s8))}


def analyze(path, tag):
    rows = load_rows(path)
    y = np.array([r["fs8"] for r in rows])
    sig = np.array([r["sigma_fs8"] for r in rows])
    U, Rs, Rc = theory_cols(rows)
    res = gls_fit(y, sig, U, Rs, Rc)
    res.update({"n_rows": int(y.size), "tag": tag,
                "mean_sigma_frac": float(np.mean(sig / y))})
    # per-point pulls
    X = np.column_stack([U, U * Rs, U * Rc])
    model = X @ np.array([res["s8"], res["B1p"], res["B2p"]])
    res["max_abs_pull"] = float(np.max(np.abs((y - model) / sig)))
    if "fs8_true" in rows[0]:
        yt = np.array([r["fs8_true"] for r in rows])
        res["bias_vs_true"] = {"mean_over_sigma": float(np.mean((y - yt) / sig)),
                               "rms_over_sigma": float(np.sqrt(np.mean(((y - yt) / sig) ** 2))),
                               "max_frac_dev": float(np.max(np.abs(y / yt - 1.0)))}
    return res, rows, (U, Rs, Rc)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "data"
    out = {}
    if mode == "synth":
        for fname, tag in (("fs8_synth_A0.0.csv", "synth_A0"),
                           ("fs8_synth_A0.509.csv", "synth_Agate")):
            p = RESULTS / fname
            if not p.exists():
                print(f"missing {p}, skip")
                continue
            res, rows, _ = analyze(p, tag)
            out[tag] = res
            a_true = 0.0 if tag == "synth_A0" else fb.A_GATE
            print(f"[{tag}] Â={res['A']:.4f} (true {a_true:.3f})  "
                  f"A95_freq={res['A95_frequentist']:.3f}  dchi2_gate={res['dchi2_gate']:.2f}  "
                  f"sigma_frac={res['mean_sigma_frac']:.4f}")
            if "bias_vs_true" in res:
                b = res["bias_vs_true"]
                print(f"        per-bin bias: mean={b['mean_over_sigma']:+.3f} sigma, "
                      f"rms={b['rms_over_sigma']:.3f} sigma, max|f/fs8t-1|={b['max_frac_dev']:.3%}")
    else:
        p = RESULTS / "fs8_boss_bins.csv"
        res, rows, (U, Rs, Rc) = analyze(p, "boss_real")
        out["boss_real"] = res
        print(f"[BOSS real] Â={res['A']:.4f}  A95_freq={res['A95_frequentist']:.4f}  "
              f"A95_off={res['A95_offsetfree']:.4f}  dchi2_gate={res['dchi2_gate']:.3f}  "
              f"gate_closed={res['gate_closed']}")
        print(f"            alpha_min95 = {res['alpha_min95']:.3e}  "
              f"(gate 8e-4, gap x{8e-4 / res['alpha_min95']:.1f})")
        print(f"            s8={res['s8']:.4f}  chi2/dof={res['chi2'] / res['dof']:.2f}  "
              f"n={res['n_rows']}  <sigma_frac>={res['mean_sigma_frac']:.4f}")
        # figure: per-bin f_sigma8 + gate-signal template
        zc = np.array([r["z_center"] for r in rows])
        y = np.array([r["fs8"] for r in rows])
        sig = np.array([r["sigma_fs8"] for r in rows])
        zt = np.linspace(0.14, 0.72, 600)
        Ut, Rst, Rct = (np.interp(zt, ZG, g) for g in (UG, RS_ZG, RC_ZG))
        fig, ax = plt.subplots(2, 1, figsize=(8.5, 8.0), sharex=True,
                               gridspec_kw={"height_ratios": [2, 1]})
        th = np.array([res["s8"], res["B1p"], res["B2p"]])
        fs8_fit = (Ut * (1.0 + th[1] * Rst + th[2] * Rct)) * th[0]
        fs8_gate = Ut * (1.0 + fb.A_GATE * (np.cos(res["phi_gate"]) * Rst +
                                            np.sin(res["phi_gate"]) * Rct)) * res["s8"]
        ax[0].errorbar(zc, y, yerr=sig, fmt="o", ms=4, lw=1, color="#1565c0",
                       label="BOSS DR12 matched bins (this work)")
        ax[0].plot(zt, fs8_fit, color="#455a64", lw=1.2, label="GLS best fit")
        ax[0].plot(zt, fs8_gate, color="#e65100", lw=1.0, ls="--",
                   label=f"gate-open signal (A={fb.A_GATE:.3f})")
        ax[0].set_ylabel(r"$f\sigma_8(z)$")
        ax[0].legend(frameon=False, fontsize=9)
        ax[0].set_title("SRE chiral channel: BOSS DR12 matched z-bin stack\n"
                        f"95% lower bound $\\alpha_{{scale}}> {res['alpha_min95']:.1e}$ "
                        f"(gate $8\\times10^{{-4}}$: no discrimination)")
        pull = (y - np.interp(zc, zt, fs8_fit)) / sig
        ax[1].axhline(0, color="#455a64", lw=0.8)
        ax[1].plot(zc, pull, "o", ms=4, color="#6a1b9a")
        ax[1].set_ylabel(r"pull / $\sigma$")
        ax[1].set_xlabel("z")
        fig.tight_layout()
        fig.savefig(RESULTS / "fig_s3_boss_stack.png", dpi=160)
        fig.savefig(RESULTS / "fig_s3_boss_stack.svg")
        print(f"figure -> {RESULTS / 'fig_s3_boss_stack.png'}")
    (RESULTS / "real_stack.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"wrote {RESULTS / 'real_stack.json'}")


if __name__ == "__main__":
    main()
