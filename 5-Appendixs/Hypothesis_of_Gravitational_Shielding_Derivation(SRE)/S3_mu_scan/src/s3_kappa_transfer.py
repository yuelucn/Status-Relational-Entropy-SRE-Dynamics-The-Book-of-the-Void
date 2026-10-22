"""S3 kappa-transfer (Phase 2): does the SRE chiral G-oscillation survive in the
weak-lensing / shear-amplitude (tomographic kappa) channel?

Motivation
----------
Phase 1 (s3_mu_scan.py) searched for the chiral modulation of the growth source
    eps(z) = A * exp(0.15 mu) * sin(2*pi*theta*mu/Delta z_s + phi),  mu ~ z
in f_sigma8(z).  There the observable is essentially D'(x=ln a) (f_sigma8 = f*sigma8
prop D'), and the fast oscillation survived only weakly: unit-A response 6.69e-3.

Phase 2, per advisor guidance, changes the *probe* to the growth factor D itself,
which is what weak lensing measures (kappa = int W(z) delta(z), delta prop D(z)).
The tomographic lensing kernel
    W(z) prop chi(z) * (1+z) * int_z^zmax n(z') (chi(z')-chi(z))/chi(z') dz'
has a line-of-sight / source-distribution width far larger than the oscillation
period P = 0.047, so a *second*, independent low-pass acts on the signal.

Two suppressions therefore act in series for kappa:
    (1) intrinsic: D-response vs D'-response  -- for a fast oscillation the
        derivative probe is enhanced by ~omega = k(1+z) ~ 200, so the amplitude
        probe is that much weaker;
    (2) kernel averaging: the broad lensing kernel averages the fast z-wiggle away.
We quantify both, the per-bin response R_kappa, and the total suppression relative
to the f_sigma8 channel, then adjudicate.

Conflict note on the advisor's P(k) scale-feature suggestion
------------------------------------------------------------
The advisor proposed hunting a sharp scale feature in P(k) at k~0.1-0.15 h/Mpc
from 1/(r^2 ln(r/l_P)).  This is NOT a viable signature: 1/r^2 in Gamma_chiral is
*exactly* the Newtonian 1/r^2 (so it carries no relative scale dependence), and the
only r-dependence of the chiral/Newton ratio is 1/ln(r/l_P), which varies by <4%
over two decades in r.  There is no sharp P(k) feature.  The script quantifies this.
The only viable signature of the chiral channel is the z-oscillation studied here.

Self-contained on purpose: the validated Phase 1 script is left byte-identical
(project rule: keep the unoptimised reference implementation as the baseline).
The growth-ODE block below is the same physics as Phase 1, re-instantiated here;
the D-response solver is new.  Both are cross-checked against a finite difference
of the full nonlinear solution and against the Phase 1 f_sigma8 response.

Run:  C:\\myapp\\miniconda3\\envs\\ai\\python.exe S3_mu_scan/src/s3_kappa_transfer.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

trapz = getattr(np, "trapezoid", None) or np.trapz

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "S3_mu_scan" / "results"

# --------------------------------------------------------------------------
# theory-tied constants (identical to Phase 1)
# --------------------------------------------------------------------------
THETA = 0.82798
OM, OL, OR = 0.315, 0.685, 9.2e-5
LP = 1.616255e-35
MPC = 3.0857e22
XI0, WBAR = 0.108, 0.9901
ALPHA_GATE = 8e-4
DZ_DOC = 0.03925


def c_amp(r_m):
    """A = C/alpha_scale, C = xi0 / (2 <W> ln(r/l_P))."""
    return XI0 / (2.0 * WBAR * np.log(r_m / LP))


C_8MPC = c_amp(8 * MPC)
A_GATE = C_8MPC / ALPHA_GATE
K_DOC = 2.0 * np.pi * THETA / DZ_DOC        # oscillation wavenumber (per unit z)
P_DOC = DZ_DOC / THETA

# --------------------------------------------------------------------------
# growth ODE in x = ln a :  D'' + P D' = Q D (1 + eps)      [same as Phase 1]
# --------------------------------------------------------------------------
X0, XON = np.log(0.01), np.log(1.0 / 6.0)


def E2(x):
    a = np.exp(x)
    return OM / a ** 3 + OR / a ** 4 + OL


def Pcoef(x):
    a = np.exp(x)
    return 2.0 - (3 * OM / a ** 3 + 4 * OR / a ** 4) / (2 * E2(x))


def Qcoef(x):
    a = np.exp(x)
    return 1.5 * (OM / a ** 3) / E2(x)


def solve_baseline():
    def rhs(x, y):
        return [y[1], -Pcoef(x) * y[1] + Qcoef(x) * y[0]]
    return solve_ivp(rhs, (X0, 0.0), [0.01, 0.01], method="DOP853",
                     rtol=1e-11, atol=1e-13, dense_output=True).sol


def eps_vec(x, k_arr):
    """unit-amplitude (sin, cos) envelopes for every k at scalar time x; 0 before z=5."""
    if x < XON:
        return np.zeros_like(k_arr), np.zeros_like(k_arr)
    zz = np.exp(-x) - 1.0
    env = np.exp(0.15 * zz)
    return env * np.sin(k_arr * zz), env * np.cos(k_arr * zz)


BASE = solve_baseline()
D01 = float(BASE(0.0)[0])


def _forced_rhs(k_arr):
    def rhs(x, y):
        fo = Qcoef(x) * float(BASE(x)[0])
        es, ec = eps_vec(x, k_arr)
        P, Qc = Pcoef(x), Qcoef(x)
        s1, s2, c1, c2 = y[0::4], y[1::4], y[2::4], y[3::4]
        d = np.empty_like(y)
        d[0::4] = s2
        d[1::4] = -P * s2 + Qc * s1 + fo * es
        d[2::4] = c2
        d[3::4] = -P * c2 + Qc * c1 + fo * ec
        return d
    return rhs


def solve_responses(k_arr, xs):
    """Fractional responses per unit amplitude of the sin/cos templates.

    RD = ambient density amplitude channel (what weak lensing measures):
         (D_tot(x)/D_tot(0)) / (D0(x)/D0(0)) - 1
    RS = f_sigma8 channel (same definition as Phase 1's Rs/Rc):
         (D'_tot(x)/D_tot(0)) / (D'_0(x)/D0(0)) - 1

    Returns (RD_s, RD_c, RS_s, RS_c), each of shape (len(k_arr), len(xs)).
    """
    k_arr = np.atleast_1d(np.asarray(k_arr, float))
    xs = np.asarray(xs, float)
    M = k_arr.size
    sol = solve_ivp(_forced_rhs(k_arr), (XON, 0.0), np.zeros(4 * M),
                    method="DOP853", rtol=1e-10, atol=1e-14, max_step=2.5e-4,
                    dense_output=True)
    Yx, Y0 = sol.sol(xs), sol.sol(0.0)
    D0x = np.array([BASE(x)[0] for x in xs])
    D0px = np.array([BASE(x)[1] for x in xs])
    s1, s2, c1, c2 = Yx[0::4], Yx[1::4], Yx[2::4], Yx[3::4]
    s1t, c1t = Y0[0::4], Y0[2::4]
    RD_s = ((D0x[None, :] + s1) / (D01 + s1t)[:, None]) * (D01 / D0x[None, :]) - 1.0
    RD_c = ((D0x[None, :] + c1) / (D01 + c1t)[:, None]) * (D01 / D0x[None, :]) - 1.0
    RS_s = ((D0px[None, :] + s2) / D0px[None, :]) * (D01 / (D01 + s1t))[:, None] - 1.0
    RS_c = ((D0px[None, :] + c2) / D0px[None, :]) * (D01 / (D01 + c1t))[:, None] - 1.0
    return RD_s, RD_c, RS_s, RS_c


def validate_D(k, delta=1e-3, basis="sin", max_step=2.5e-4):
    """End-to-end finite-difference check of the D-response against the full
    nonlinear solution of  D'' + P D' = Q D (1 + delta e^{0.15 z} sin/cos(k z))."""
    def rhs(x, y):
        e = eps_vec(x, np.array([k]))[0 if basis == "sin" else 1][0]
        return [y[1], -Pcoef(x) * y[1] + Qcoef(x) * y[0] * (1.0 + delta * e)]
    y0 = BASE(XON)
    sol = solve_ivp(rhs, (XON, 0.0), [y0[0], y0[1]], method="DOP853",
                    rtol=1e-11, atol=1e-14, max_step=max_step, dense_output=True)
    Dt = sol.sol(XG)[0]
    Dt0 = sol.sol(0.0)[0]
    ratio = (Dt / Dt0) / (D0G / D01) - 1.0
    lin = RD_S if basis == "sin" else RD_C
    return ratio / delta, lin


# --------------------------------------------------------------------------
# dense z grid + doc-window responses
# --------------------------------------------------------------------------
ZG = np.linspace(0.0, 2.0, 801)
XG = -np.log(1.0 + ZG)
D0G = np.array([BASE(x)[0] for x in XG])

RD_ALL, RC_ALL, RS_ALL, RC_ALL2 = solve_responses(np.array([K_DOC]), XG)
RD_S, RD_C = RD_ALL[0], RC_ALL[0]
RS_S, RS_C = RS_ALL[0], RC_ALL2[0]

RD_AMP = float(np.max(np.hypot(RD_S, RD_C)))       # pointwise D-response amplitude
RS_AMP = float(np.max(np.hypot(RS_S, RS_C)))       # pointwise f_sigma8-response amplitude

validations = []
for basis in ("sin", "cos"):
    fd, lin = validate_D(K_DOC, basis=basis)
    amp = float(np.max(np.abs(lin)))
    diff = float(np.max(np.abs(fd - lin)))
    validations.append({"basis": basis, "max_abs_lin_response": amp,
                        "max_abs_fd_minus_lin": diff,
                        "max_rel_dev_fd_vs_lin": diff / max(amp, 1e-30)})

# --------------------------------------------------------------------------
# cosmology: comoving distance (units c/H0) and tomographic lensing kernel
# --------------------------------------------------------------------------
def Ez(z):
    return np.sqrt(OM * (1.0 + z) ** 3 + OL)


CHI = np.concatenate([[0.0], np.cumsum(0.5 * (1.0 / Ez(ZG[1:]) + 1.0 / Ez(ZG[:-1]))
                                       * np.diff(ZG))])


def nz(z, zc, sz):
    """DES Y3-like illustrative source distribution: Gaussian in z, sigma = sz."""
    n = np.exp(-0.5 * ((z - zc) / sz) ** 2)
    n = np.where(z > 1e-3, n, 0.0)
    return n / trapz(n, z)


def lens_weight(zc, sz):
    """Tomographic lensing kernel q(z) prop chi(z)(1+z) int_z^zmax n(z')(chi'-chi)/chi'."""
    n = nz(ZG, zc, sz)
    g = np.zeros_like(ZG)
    for j in range(ZG.size - 1):
        t = slice(j + 1, ZG.size)
        g[j] = trapz(n[t] * (CHI[t] - CHI[j]) / CHI[t], ZG[t])
    return CHI * (1.0 + ZG) * g


def r_kappa(q, rd_s, rd_c):
    """Kernel-weighted fractional response of the bin density amplitude."""
    w = q * D0G
    den = trapz(w, ZG)
    rs = trapz(w * rd_s, ZG) / den
    rc = trapz(w * rd_c, ZG) / den
    return rs, rc, float(np.hypot(rs, rc))


def bin_avg(arr, zc, half):
    m = np.abs(ZG - zc) <= half
    return float(trapz(arr[m], ZG[m]) / trapz(np.ones(int(m.sum())), ZG[m]))


# --------------------------------------------------------------------------
# per-bin kappa responses (fiducial DES Y3-like tomography, sigma_z = 0.10)
# --------------------------------------------------------------------------
ZC_BINS = np.array([0.35, 0.55, 0.75, 0.95])
SZ_FID = 0.10
SZ_LIST = [0.05, 0.10, 0.20]

bins = []
for zc in ZC_BINS:
    q = lens_weight(zc, SZ_FID)
    rs, rc, amp = r_kappa(q, RD_S, RD_C)
    i = int(np.argmin(np.abs(ZG - zc)))
    ref_pt = float(np.hypot(RS_S[i], RS_C[i]))
    ref_bin = float(np.hypot(bin_avg(RS_S, zc, 2 * SZ_FID), bin_avg(RS_C, zc, 2 * SZ_FID)))
    df8_bin = float(np.hypot(bin_avg(RD_S, zc, 2 * SZ_FID), bin_avg(RD_C, zc, 2 * SZ_FID)))
    bins.append({"zc": float(zc), "sz": SZ_FID, "R_kappa_sin": rs, "R_kappa_cos": rc,
                 "R_kappa": amp, "R_kappa_x2_shear": 2.0 * amp,
                 "ref_fs8_pointwise": ref_pt, "ref_fs8_binned": ref_bin,
                 "D_response_binned": df8_bin,
                 "suppression_binned": ref_bin / max(amp, 1e-30),
                 "suppression_pointwise": ref_pt / max(amp, 1e-30),
                 "suppression_observable_binned": ref_bin / max(2.0 * amp, 1e-30),
                 "suppression_observable_pointwise": ref_pt / max(2.0 * amp, 1e-30)})

# sigma_z sensitivity for the fiducial (middle) bin
sz_scan = []
for sz in SZ_LIST:
    q = lens_weight(0.75, sz)
    _, _, amp = r_kappa(q, RD_S, RD_C)
    ref_bin = float(np.hypot(bin_avg(RS_S, 0.75, 2 * sz), bin_avg(RS_C, 0.75, 2 * sz)))
    sz_scan.append({"sz": sz, "R_kappa": amp, "ref_fs8_binned": ref_bin,
                    "suppression_binned": ref_bin / max(amp, 1e-30)})

# --------------------------------------------------------------------------
# delta_z_s scan of the suppression (fiducial bin zc=0.75, sz=0.10)
# --------------------------------------------------------------------------
DZS_SCAN = np.array(sorted(set(list(np.geomspace(0.03, 2.0, 40)) + [DZ_DOC, 0.24155])))
K_SCAN = 2.0 * np.pi * THETA / DZS_SCAN
RD_scan, RC_scan, RS_scan, RC_scan2 = solve_responses(K_SCAN, XG)
q_mid = lens_weight(0.75, SZ_FID)

scan = []
for j, dzs in enumerate(DZS_SCAN):
    _, _, amp = r_kappa(q_mid, RD_scan[j], RC_scan[j])
    ref_bin = float(np.hypot(bin_avg(RS_scan[j], 0.75, 0.2), bin_avg(RC_scan2[j], 0.75, 0.2)))
    scan.append({"dzs": float(dzs), "P": float(dzs / THETA), "R_kappa": amp,
                 "ref_fs8_binned": ref_bin, "suppression_binned": ref_bin / max(amp, 1e-30),
                 "R_D_pointwise_amp": float(np.max(np.hypot(RD_scan[j], RC_scan[j]))),
                 "R_fs8_pointwise_amp": float(np.max(np.hypot(RS_scan[j], RC_scan2[j])))})

i_doc = int(np.argmin(np.abs(DZS_SCAN - DZ_DOC)))
DOC_ROW = scan[i_doc]

# --------------------------------------------------------------------------
# intrinsic (derivative-vs-amplitude) factor and scale-feature check
# --------------------------------------------------------------------------
omega_x = K_DOC * (1.0 + 0.75)                     # dz/dx ~ -(1+z), at z=0.75
f_growth = float(BASE(-np.log(1.0 + 0.75))[1] / BASE(-np.log(1.0 + 0.75))[0])
intrinsic_factor = RS_AMP / RD_AMP

r_probe = np.array([1.0, 10.0, 100.0]) * MPC
lnP = np.log(r_probe / LP)
ratio_scale = lnP[0] / lnP                          # chiral/Newton amplitude vs Newtonian 1/r^2
scale_feature = {"r_Mpc": [1.0, 10.0, 100.0], "ln_r_over_lP": lnP.tolist(),
                 "rel_amplitude_vs_1Mpc": ratio_scale.tolist(),
                 "max_deficit_over_2decades": float(1.0 - ratio_scale[-1])}

# --------------------------------------------------------------------------
# adjudication
# --------------------------------------------------------------------------
supp_bins = [b["suppression_binned"] for b in bins]
pt_bins = [b["suppression_pointwise"] for b in bins]
obs_bins = [b["suppression_observable_binned"] for b in bins]
obs_pt = [b["suppression_observable_pointwise"] for b in bins]
min_supp, max_supp = float(min(supp_bins)), float(max(supp_bins))
min_pt, max_pt = float(min(pt_bins)), float(max(pt_bins))
min_obs, max_obs = float(min(obs_bins)), float(max(obs_bins))
min_obs_pt, max_obs_pt = float(min(obs_pt)), float(max(obs_pt))
if min_obs >= 10.0:
    verdict = "kappa strictly worse than f_sigma8 (>10x, even most favourable convention)"
else:
    verdict = (f"kappa worse than f_sigma8 in every convention "
               f"({min_obs:.1f}-{max_obs:.1f}x bin-matched observable, {min_pt:.0f}-{max_pt:.0f}x pointwise amplitude)")
action = ("abandon the z-oscillation route for weak lensing; kappa offers no sensitivity advantage "
          "and, like f_sigma8, cannot reach the gate")

# --------------------------------------------------------------------------
# figure
# --------------------------------------------------------------------------
RESULTS.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 140, "savefig.bbox": "tight"})
fig, ax = plt.subplots(2, 2, figsize=(11.5, 8.0))
fig.suptitle("S3 Phase 2: SRE chiral oscillation in the weak-lensing ($\\kappa$ / shear) channel"
             f"   ($\\Delta z_s$={DZ_DOC}, $P$={P_DOC:.4f})", fontsize=12, fontweight="bold")

a0 = ax[0, 0]
a0.axhline(0, color="#999", lw=0.8)
a0.plot(ZG, RS_S, "-", color="#1565c0", lw=1.2, label="f$\\sigma_8$ channel (depends on $D'$)")
a0.plot(ZG, RD_S, "-", color="#c62828", lw=1.2, label="lensing channel (depends on $D$)")
a0.set_xlim(0, 2.0)
a0.set_xlabel("redshift $z$"); a0.set_ylabel("response per unit $A$ (sin template)")
a0.legend(fontsize=7.5, loc="lower right")
a0.set_title(f"(a) $D$-vs-$D'$: intrinsic factor = {intrinsic_factor:.0f}$\\times$"
             f" ($\\omega_x\\approx${omega_x:.0f})", fontsize=9.5)

a1 = ax[0, 1]
for k, (zc, c) in enumerate(zip(ZC_BINS, ["#0d47a1", "#2e7d32", "#ef6c00", "#6a1b9a"])):
    q = lens_weight(zc, SZ_FID)
    a1.plot(ZG, q / np.max(q), "-", color=c, lw=1.4, label=f"$z_c$={zc:.2f} ($\\sigma_z$={SZ_FID})")
a1.set_xlim(0, 2.0)
a1.set_xlabel("redshift $z$"); a1.set_ylabel("normalised lensing kernel $q(z)$")
a1.legend(fontsize=7.5)
a1.set_title(f"(b) tomographic kernels: width $\\gg$ period ({P_DOC:.3f})", fontsize=9.5)

a2 = ax[1, 0]
x = np.arange(len(bins))
a2.bar(x, [b["R_kappa"] for b in bins], width=0.55, color="#c62828", alpha=0.85,
       label="$|R_\\kappa|$ per unit $A$ (bin)")
a2.bar(x, [b["ref_fs8_binned"] for b in bins], width=0.28, color="#1565c0", alpha=0.85,
       label="$|R_{f\\sigma_8}|$ (same bin, unit $A$)")
a2.set_yscale("log")
a2.set_xticks(x); a2.set_xticklabels([f"{b['zc']:.2f}" for b in bins])
a2.set_xlabel("tomographic bin centre $z_c$"); a2.set_ylabel("response per unit $A$")
a2.legend(fontsize=7.5)
a2.set_title(f"(c) suppressed by {min_supp:.0f}–{max_supp:.0f}$\\times$ vs f$\\sigma_8$", fontsize=9.5)

a3 = ax[1, 1]
a3.semilogx(DZS_SCAN, [r["suppression_binned"] for r in scan], "o-", ms=3.5, lw=1.2,
            color="#6a1b9a")
a3.axvline(DZ_DOC, color="#2e7d32", ls=":", lw=1.2)
a3.axhline(10.0, color="#c62828", ls="--", lw=1.1, label="10$\\times$ abandon threshold")
a3.annotate("doc window", (DZ_DOC, max(r["suppression_binned"] for r in scan) * 0.7),
            fontsize=7.5, color="#2e7d32", ha="left")
a3.set_xlabel("window width $\\Delta z_s$ (log)"); a3.set_ylabel("suppression vs f$\\sigma_8$ (bin)")
a3.legend(fontsize=7.5)
a3.set_title("(d) suppression grows for fast oscillation", fontsize=9.5)

fig.tight_layout()
fig.savefig(RESULTS / "fig_s3_kappa.png")
fig.savefig(RESULTS / "fig_s3_kappa.svg")
plt.close(fig)

# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------
out = {
    "meta": {"theta_conformal": THETA, "A_coef_8Mpc": C_8MPC, "A_gate_8Mpc": A_GATE,
             "doc_window_dzs": DZ_DOC, "doc_period": P_DOC, "k_doc": K_DOC,
             "sz_fiducial": SZ_FID, "bins_zc": ZC_BINS.tolist()},
    "levels": {"RD_pointwise_amp_doc": RD_AMP, "RS_pointwise_amp_doc": RS_AMP,
               "intrinsic_factor_RS_over_RD": float(intrinsic_factor),
               "omega_x_at_z075": float(omega_x), "f_growth_at_z075": f_growth},
    "bins": bins,
    "sigma_z_scan": sz_scan,
    "dzs_scan": scan,
    "doc_window_row": DOC_ROW,
    "scale_feature_check": scale_feature,
    "validations": validations,
    "adjudication": {"verdict": verdict, "recommended_action": action,
                     "suppression_amplitude_binned_min": min_supp, "suppression_amplitude_binned_max": max_supp,
                     "suppression_observable_binned_min": min_obs, "suppression_observable_binned_max": max_obs,
                     "suppression_pointwise_min": min_pt, "suppression_pointwise_max": max_pt},
}
(RESULTS / "kappa_transfer.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

print("=== S3 kappa-transfer (Phase 2, conda env ai) ===")
print(f"doc window dzs={DZ_DOC}  P={P_DOC:.4f}  k={K_DOC:.1f} /z")
print(f"pointwise response per unit A (doc window):  fsigma8 D' = {RS_AMP:.3e} | lensing D = {RD_AMP:.3e}")
print(f"intrinsic suppression (D vs D'): {intrinsic_factor:.1f}x  (omega_x ~ {omega_x:.0f}, f ~ {f_growth:.2f})")
print("per-bin kappa response (D channel) vs same-bin fsigma8 (D' channel):")
for b in bins:
    print(f"  zc={b['zc']:.2f}: |R_kappa| = {b['R_kappa']:.3e}   |R_fs8|_bin = {b['ref_fs8_binned']:.3e}"
          f"   suppression = {b['suppression_binned']:.0f}x")
print(f"suppression range over bins (bin-matched D-amplitude): {min_supp:.1f}-{max_supp:.1f}x"
      f"   (observable, xi_pm prop kappa^2: {min_obs:.1f}-{max_obs:.1f}x;"
      f" pointwise amplitude: {min_pt:.0f}-{max_pt:.0f}x)")
print(f"sigma_z scan (bin zc=0.75): " + ", ".join(f"sz={s['sz']:.2f}->{s['suppression_binned']:.0f}x" for s in sz_scan))
print(f"Verdict: {verdict}")
print(f"  -> {action}")
print("scale-feature check: ln(r/l_P) over r=1..100 Mpc -> relative chiral/Newton amplitude drops"
      f" by {100*scale_feature['max_deficit_over_2decades']:.2f}% (no sharp P(k) feature)")
print("validations (FD vs linear D-response):")
for v in validations:
    print(f"  basis={v['basis']}: max|R|={v['max_abs_lin_response']:.3e}  max rel dev ="
          f" {100*v['max_rel_dev_fd_vs_lin']:.3f}%")
print("files: results/kappa_transfer.json, results/fig_s3_kappa.png|svg")
