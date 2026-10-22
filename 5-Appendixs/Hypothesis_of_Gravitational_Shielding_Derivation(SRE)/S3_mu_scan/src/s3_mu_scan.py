"""S3 mu-scan (Phase 1): SRE chiral-channel oscillation search in f_sigma8(z).

Theory template (屏蔽引力推导.md sections 1/4/5/8):
    eps(z) = A * exp(0.15*mu) * sin(2*pi*theta*mu/Delta z_s + phi),   mu ~ z
    theta_conformal = 0.82798;  alpha_0 = theta / Delta z_s
    oscillation period in mu:   P = Delta z_s / theta
    gate criterion (doc 4.2):   alpha_scale <= 8e-4  <=>  A >= A_gate
    A = C / alpha_scale,  C = xi0 / (2 <W> ln(r/l_P)),  xi0 = 0.108, <W> = 0.9901
        r = 8 Mpc (Rank-4 chiral term, cluster scales) -> C = 4.071e-4 -> A_gate = 0.509
        r = 1 m   (doc 4.2 reference)                  -> C = 6.80e-4  -> A_gate = 0.850
    doc-tied window:  Delta z = 0.03925 (SDSS)  ->  P = 0.0474

Statistics: full-covariance GLS; free-A fit (s8, B1, B2) linear; 95% radial bound
from the profiled 2x2 information matrix, quoted both offset-free (ideal sensitivity)
and offset-inclusive (frequentist, honest); gate test = profile chi2 with A fixed at
A_gate over (s8, phi) compared with the free best fit.

Run:  C:\\myapp\\miniconda3\\envs\\ai\\python.exe S3_mu_scan/src/s3_mu_scan.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --------------------------------------------------------------------------
# constants
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
DATA_CSV = ROOT / "S3_mu_scan" / "data" / "fs8_compilation_sagredo2018.csv"
RESULTS = ROOT / "S3_mu_scan" / "results"

THETA = 0.82798
GAMMA = 6.0 / 11.0
OM, OL, OR = 0.315, 0.685, 9.2e-5
S8P18 = 0.8110
LP = 1.616255e-35
MPC = 3.0857e22
XI0, WBAR = 0.108, 0.9901


def C_amp(r_m):
    """A = C / alpha_scale,  C = xi0 / (2 <W> ln(r/l_P))."""
    return XI0 / (2.0 * WBAR * np.log(r_m / LP))


C_8MPC, C_1M = C_amp(8 * MPC), C_amp(1.0)
ALPHA_GATE = 8e-4
A_GATE_8MPC, A_GATE_1M = C_8MPC / ALPHA_GATE, C_1M / ALPHA_GATE
DZ_DOC = 0.03925

# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------
def load_data():
    z, fs8, err, omref, survey = [], [], [], [], []
    for line in DATA_CSV.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        f = line.split(",")
        z.append(float(f[1])); fs8.append(float(f[2]))
        err.append(float(f[3])); omref.append(float(f[4])); survey.append(f[5])
    return (np.array(z), np.array(fs8), np.array(err), np.array(omref), survey)


Z, FS8, ERR, OMREF, SURVEY = load_data()
NZ = Z.size
WZ_IDX = [12, 13, 14]
WZ_C = 1e-3 * np.array([[6.400, 2.570, 0.0],
                        [2.570, 3.969, 2.540],
                        [0.0, 2.540, 5.184]])
COV = np.diag(ERR ** 2)
for i, gi in enumerate(WZ_IDX):
    for j, gj in enumerate(WZ_IDX):
        COV[gi, gj] = WZ_C[i, j]
COVI = np.linalg.inv(COV)


def Omz(z, om0):
    o = om0 * (1 + z) ** 3
    return o / (o + (1 - om0))


CORR = np.array([(Omz(z, OM) / Omz(z, om)) ** GAMMA for z, om in zip(Z, OMREF)])
YOBS = FS8 * CORR

# --------------------------------------------------------------------------
# growth ODE in x = ln a :  D'' + P D' = Q D (1 + eps)
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
        z = np.zeros_like(k_arr)
        return z, z.copy()
    zz = np.exp(-x) - 1.0
    env = np.exp(0.15 * zz)
    return env * np.sin(k_arr * zz), env * np.cos(k_arr * zz)


BASE = solve_baseline()
D01 = float(BASE(0.0)[0])


def solve_responses(k_arr, xs):
    """R(z) per unit amplitude of the sin/cos basis, for all k at once.

    f_sigma8_tot / f_sigma8_base - 1 = c_s * Rs + c_c * Rc
    Returns (Rs, Rc) each of shape (len(k_arr), len(xs)).
    """
    k_arr = np.atleast_1d(np.asarray(k_arr, float))
    xs = np.asarray(xs, float)
    M = k_arr.size

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

    sol = solve_ivp(rhs, (XON, 0.0), np.zeros(4 * M), method="DOP853",
                    rtol=1e-10, atol=1e-14, max_step=2.5e-4, dense_output=True)
    Yx, Y0 = sol.sol(xs), sol.sol(0.0)
    s1_today, c1_today = Y0[0::4], Y0[2::4]
    D0p = np.array([BASE(x)[1] for x in xs])
    s1, s2, c1, c2 = Yx[0::4], Yx[1::4], Yx[2::4], Yx[3::4]
    Rs = ((D0p[None, :] + s2) / D0p[None, :]) * (D01 / (D01 + s1_today))[:, None] - 1.0
    Rc = ((D0p[None, :] + c2) / D0p[None, :]) * (D01 / (D01 + c1_today))[:, None] - 1.0
    return Rs, Rc


def tick(k):
    return 2.0 * np.pi * THETA / k


def validate_response(k, delta=1e-3, basis="sin", max_step=2.5e-4):
    """End-to-end check: finite difference of the FULL nonlinear solution vs the linear response.

    Solves  D'' + P D' = Q D (1 + delta * e^{0.15 z} * sin/cos(k z))  from z=5,
    then compares (f_sigma8_tot / f_sigma8_base - 1)/delta with Rs (or Rc) at the data points.
    """
    def rhs(x, y):
        e_s, e_c = eps_vec(x, np.array([k]))
        e = (e_s[0] if basis == "sin" else e_c[0])
        return [y[1], -Pcoef(x) * y[1] + Qcoef(x) * y[0] * (1.0 + delta * e)]
    y0 = BASE(XON)
    sol = solve_ivp(rhs, (XON, 0.0), [y0[0], y0[1]], method="DOP853",
                    rtol=1e-11, atol=1e-14, max_step=max_step, dense_output=True)
    Dt, Dtp = sol.sol(XZ)
    Dt0 = sol.sol(0.0)[0]
    ratio = (Dtp / Dt) * (Dt / Dt0) / (D0PD / D01) - 1.0
    lin = (RS_D if basis == "sin" else RC_D)[int(np.argmin(np.abs(K_GRID - k)))]
    return ratio / delta, lin


# --------------------------------------------------------------------------
# scan grid  (+ doc-tied SDSS window)
# --------------------------------------------------------------------------
DZS_GRID = np.array(sorted(set(list(np.geomspace(0.035, 2.0, 113)) + [DZ_DOC, 0.24155])))
K_GRID = 2.0 * np.pi * THETA / DZS_GRID
XZ = -np.log(1.0 + Z)
ZDENSE = np.linspace(0.0, 2.0, 201)
XDENSE = -np.log(1.0 + ZDENSE)

XS_ALL = np.concatenate([XZ, XDENSE])
RS_ALL, RC_ALL = solve_responses(K_GRID, XS_ALL)
RS_D, RC_D = RS_ALL[:, :NZ], RC_ALL[:, :NZ]          # at data points
RS_Z, RC_Z = RS_ALL[:, NZ:], RC_ALL[:, NZ:]          # dense z grid

D0D = np.array([BASE(x)[0] for x in XZ])
D0PD = np.array([BASE(x)[1] for x in XZ])
U = D0PD / D01                                        # unit-sigma8 LCDM f_sigma8

# --------------------------------------------------------------------------
# fits
# --------------------------------------------------------------------------
def chi2(y, model):
    r = y - model
    return float(r @ COVI @ r)


col = U.copy()
S8HAT = float(col @ COVI @ YOBS) / float(col @ COVI @ col)
CHI2_LCDM = chi2(YOBS, col * S8HAT)
R18 = YOBS - U * S8P18
CHI2_P18 = float(R18 @ COVI @ R18)
PULL_LCDM = (FS8 - U * S8HAT) / ERR


def fit_free_A(iy, y):
    """3-param linear fit f = s8 U (1 + B1' Rs + B2' Rc); B1 = s8 B1'."""
    Rs, Rc = RS_D[iy], RC_D[iy]
    X = np.column_stack([U, U * Rs, U * Rc])
    M = X.T @ COVI @ X
    beta = np.linalg.solve(M, X.T @ COVI @ y)
    s8, B1, B2 = beta
    B = float(np.hypot(B1, B2))
    Mpp = M[1:, 1:] - np.outer(M[1:, 0], M[0, 1:]) / M[0, 0]
    r95 = float(np.sqrt(2.71 / np.linalg.eigvalsh(Mpp)[0]))
    return {"chi2": chi2(y, X @ beta), "s8": float(s8), "A": float(B / s8),
            "phi": float(np.arctan2(B2, B1)),
            "A95_offsetfree": float(r95 / s8),
            "A95_frequentist": float((B + r95) / s8)}


PHI_GRID = np.linspace(0.0, 2 * np.pi, 721, endpoint=False)


def chi2_fixed_A(iy, A, y):
    """chi2 with A fixed, profiled over (s8, phi)."""
    Rs, Rc = RS_D[iy], RC_D[iy]
    cs, cc = A * np.cos(PHI_GRID), A * np.sin(PHI_GRID)
    cols = U[None, :] * (1.0 + cs[:, None] * Rs[None, :] + cc[:, None] * Rc[None, :])
    CM = cols @ COVI                     # (721, NZ)
    cc2 = np.einsum("ij,ij->i", CM, cols)            # col' C^-1 col
    cby = CM @ y
    mu = cby / cc2
    r = y[None, :] - mu[:, None] * cols
    c2 = np.einsum("ij,jk,ik->i", r, COVI, r)
    j = int(np.argmin(c2))
    return float(c2[j]), float(PHI_GRID[j])


rows = []
for i, dzs in enumerate(DZS_GRID):
    f = fit_free_A(i, YOBS)
    c2g, phi_g = chi2_fixed_A(i, A_GATE_8MPC, YOBS)
    rows.append({**f, "dzs": float(dzs), "P": float(dzs / THETA),
                 "dchi2": float(CHI2_LCDM - f["chi2"]),
                 "alpha_min95_8MPC": float(C_8MPC / f["A95_frequentist"]),
                 "dchi2_gate": float(c2g - f["chi2"]), "phi_gate": phi_g,
                 "gate_closed": bool(c2g - f["chi2"] > 2.71)})

i_doc = int(np.argmin(np.abs(DZS_GRID - DZ_DOC)))
DOC = rows[i_doc]
BEST = max(rows, key=lambda r: r["dchi2"])

# --------------------------------------------------------------------------
# diagnostics: response magnitude + injection tests
# --------------------------------------------------------------------------
i_best = int(np.argmax([r["dchi2"] for r in rows]))
resp_doc = float(np.max(np.hypot(RS_Z[i_doc], RC_Z[i_doc])))
resp_best = float(np.max(np.hypot(RS_Z[i_best], RC_Z[i_best])))
zero = fit_free_A(i_doc, U * S8P18)

injections = []
for dzs, A_inj in [(DZ_DOC, A_GATE_8MPC), (DZ_DOC, 2.0), (0.5, 0.5)]:
    ii = int(np.argmin(np.abs(DZS_GRID - dzs)))
    phi_inj = 0.7
    ym = U * S8P18 * (1.0 + A_inj * (np.cos(phi_inj) * RS_D[ii] + np.sin(phi_inj) * RC_D[ii]))
    fr = fit_free_A(ii, ym)
    c2g, _ = chi2_fixed_A(ii, A_GATE_8MPC, ym)
    injections.append({"dzs": dzs, "A_injected": A_inj, "A_recovered": fr["A"],
                       "phi_injected": phi_inj, "phi_recovered": fr["phi"],
                       "dchi2_gate_on_gate_mock": float(c2g - fr["chi2"]),
                       "max_frac_shift_fs8": float(A_inj * np.max(np.hypot(RS_D[ii], RC_D[ii])))})

# ---- independent validation of the linear response (finite difference) -----
validations = []
for dzs, basis, step in [(DZ_DOC, "sin", 2.5e-4), (DZ_DOC, "cos", 2.5e-4),
                         (DZ_DOC, "sin", 6.25e-5), (2.0, "sin", 2.5e-4)]:
    k = 2.0 * np.pi * THETA / dzs
    fd, lin = validate_response(k, basis=basis, max_step=step)
    denom = np.maximum(np.abs(lin), 1e-12)
    validations.append({"dzs": dzs, "basis": basis, "max_step": step,
                        "max_abs_lin_response": float(np.max(np.abs(lin))),
                        "max_rel_dev_fd_vs_lin": float(np.max(np.abs(fd - lin) / denom))})

# --------------------------------------------------------------------------
# figure
# --------------------------------------------------------------------------
RESULTS.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 140, "savefig.bbox": "tight"})
fig, ax = plt.subplots(2, 2, figsize=(11.5, 8.0))
fig.suptitle("S3 $\\mu$-scan: SRE chiral-channel oscillation search in $f\\sigma_8(z)$"
             f"  (N={NZ} RSD points, Planck18 $\\Lambda$CDM growth)", fontsize=12, fontweight="bold")

zg = np.linspace(0.0, 2.05, 240)
xg = -np.log(1 + zg)
Ugrid = np.array([BASE(x)[1] / D01 for x in xg])
RSg, RCg = solve_responses(np.array([K_GRID[i_doc]]), xg)
gate_curve = S8HAT * Ugrid * (1 + A_GATE_8MPC * (np.cos(DOC["phi"]) * RSg[0] + np.sin(DOC["phi"]) * RCg[0]))

a0 = ax[0, 0]
a0.errorbar(Z, FS8, yerr=ERR, fmt="o", ms=4, color="#263238", ecolor="#78909c",
            capsize=2, lw=1, label="RSD compilation (Sagredo+2018)")
a0.plot(zg, S8HAT * Ugrid, "-", color="#1976d2", lw=1.8, label=f"$\\Lambda$CDM fit ($\\sigma_8$={S8HAT:.3f})")
a0.plot(zg, S8P18 * Ugrid, "--", color="#c62828", lw=1.3, label="Planck18 ($\\sigma_8$=0.811)")
a0.plot(zg, gate_curve, "-", color="#ef6c00", lw=1.1, label=f"SRE gate-open ($\\alpha$=8e-4, $\\Delta z_s$={DZ_DOC})")
a0.set_xlim(0, 2.05); a0.set_ylim(0.22, 0.63)
a0.set_xlabel("redshift $z$  ($\\mu\\approx z$)"); a0.set_ylabel("$f\\sigma_8(z)$")
a0.legend(fontsize=7.5, loc="upper right")
a0.set_title(f"(a) gate-open wiggle = {100*A_GATE_8MPC*resp_doc:.3f}% of $f\\sigma_8$: invisible here",
             fontsize=9.5)

a1 = ax[0, 1]
a1.axhline(0, color="#999", lw=1)
for v in (-3, 3):
    a1.axhline(v, color="#eee", lw=1)
a1.errorbar(Z, PULL_LCDM, fmt="o", ms=3.5, color="#455a64", ecolor="#b0bec5", capsize=2)
a1.set_xlim(0, 2.05); a1.set_ylim(-4, 4)
a1.set_xlabel("redshift $z$"); a1.set_ylabel("pull")
a1.set_title(f"(b) pull vs $\\Lambda$CDM fit (max |pull| = {np.max(np.abs(PULL_LCDM)):.1f}$\\sigma$)", fontsize=9.5)

a2 = ax[1, 0]
a2.semilogx(DZS_GRID, [r["dchi2"] for r in rows], "o-", ms=3, lw=1, color="#1565c0")
a2.axhline(2.71, color="#c62828", ls="--", lw=1.2, label="95% (2 dof)")
a2.axvline(DZ_DOC, color="#2e7d32", ls=":", lw=1.2)
a2.annotate("doc window\n$\\Delta z_s$=0.03925", (DZ_DOC, 7.6), fontsize=7.5, color="#2e7d32", ha="center")
a2.plot(BEST["dzs"], BEST["dchi2"], "o", ms=9, mfc="none", mec="#c62828", mew=1.6)
a2.annotate(f"max $\\Delta\\chi^2$={BEST['dchi2']:.2f}\n$\\Delta z_s$={BEST['dzs']:.3f}", (BEST["dzs"], BEST["dchi2"]),
            textcoords="offset points", xytext=(6, 6), fontsize=7.5, color="#c62828")
a2.set_ylim(0, 9)
a2.set_xlabel("window width $\\Delta z_s$ (log scale)"); a2.set_ylabel("$\\Delta\\chi^2$ (2 extra params)")
a2.legend(fontsize=7.5, loc="upper left")
a2.set_title("(c) period scan: no significant oscillation", fontsize=9.5)

a3 = ax[1, 1]
a3.semilogx(DZS_GRID, [r["A95_offsetfree"] for r in rows], "o-", ms=3, lw=1,
            color="#8e24aa", label="95% (offset-free)")
a3.semilogx(DZS_GRID, [r["A95_frequentist"] for r in rows], "o-", ms=3, lw=1,
            color="#6a1b9a", label="95% frequentist $|A|$")
a3.axhline(A_GATE_8MPC, color="#ef6c00", lw=1.6, label="gate $A$=0.509 ($\\alpha$=8e-4, r=8 Mpc)")
a3.axhline(A_GATE_1M, color="#ef6c00", lw=1.1, ls="--", label="gate $A$=0.850 ($r$=1 m)")
a3.axvline(DZ_DOC, color="#2e7d32", ls=":", lw=1.2)
a3.set_yscale("log"); a3.set_ylim(0.08, 90)
a3.set_xlabel("window width $\\Delta z_s$ (log scale)"); a3.set_ylabel("$A$ = amplitude of $\\delta G/G$")
a3.legend(fontsize=7, loc="upper left")
a3.set_title("(d) sensitivity ceiling (below the gate line = gate excluded)", fontsize=9.5)

fig.tight_layout()
fig.savefig(RESULTS / "fig_s3_fs8.png")
fig.savefig(RESULTS / "fig_s3_fs8.svg")
plt.close(fig)

# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------
out = {
    "meta": {"theta_conformal": THETA, "N_points": int(NZ), "A_coef_8Mpc": C_8MPC,
             "A_coef_1m": C_1M, "alpha_gate": ALPHA_GATE, "A_gate_8Mpc": A_GATE_8MPC,
             "A_gate_1m": A_GATE_1M, "doc_window_dzs": DZ_DOC, "doc_period": DZ_DOC / THETA,
             "grid_points": int(DZS_GRID.size)},
    "lcdm_fit": {"sigma8": S8HAT, "chi2": CHI2_LCDM, "dof": int(NZ - 1), "chi2_dof": CHI2_LCDM / (NZ - 1)},
    "planck18_fixed": {"chi2_fullcov": CHI2_P18, "dof": int(NZ), "chi2_dof": CHI2_P18 / NZ},
    "doc_window_row": DOC,
    "best_oscillation": BEST,
    "diagnostics": {"max_response_per_unit_A_doc_window": resp_doc,
                    "max_response_per_unit_A_best_period": resp_best,
                    "zero_injection_A_recovered": zero["A"],
                    "zero_injection_chi2": zero["chi2"],
                    "injections": injections,
                    "linear_response_validations": validations,
                    "min_A95_frequentist": float(min(r["A95_frequentist"] for r in rows)),
                    "min_A95_at_dzs": float(min(rows, key=lambda r: r["A95_frequentist"])["dzs"]),
                    "n_gate_closed_periods": int(sum(r["gate_closed"] for r in rows))},
    "residuals": [{"z": float(Z[i]), "survey": SURVEY[i], "fs8": float(FS8[i]),
                   "err": float(ERR[i]), "fs8_lcdm": float(U[i] * S8HAT),
                   "pull": float(PULL_LCDM[i])} for i in range(NZ)],
    "scan": rows,
}
(RESULTS / "scan_results.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

NA = np.newaxis
print("=== S3 mu-scan (Python, conda env ai) ===")
print(f"LCDM fit        : sigma8 = {S8HAT:.4f}   chi2/dof = {CHI2_LCDM/(NZ-1):.3f}  ({CHI2_LCDM:.2f}/{NZ-1})")
print(f"Planck18 fixed  : chi2(full cov) = {CHI2_P18:.2f}   chi2/dof = {CHI2_P18/NZ:.3f}")
print(f"max |pull|      : {np.max(np.abs(PULL_LCDM)):.2f} sigma")
print(f"best oscillation: dchi2 = {BEST['dchi2']:.2f} at dzs = {BEST['dzs']:.4f} (P = {BEST['P']:.4f}) A = {BEST['A']:.2f}")
print(f"doc window      : dzs = {DZ_DOC}  dchi2 = {DOC['dchi2']:.2f}  dchi2_gate = {DOC['dchi2_gate']:.2f}"
      f"  gate_closed = {DOC['gate_closed']}")
print(f"  A95 offset-free = {DOC['A95_offsetfree']:.2f} | A95 frequentist = {DOC['A95_frequentist']:.2f}"
      f" | alpha_min95 = {DOC['alpha_min95_8MPC']:.2e}")
print(f"gate-closed periods: {out['diagnostics']['n_gate_closed_periods']} / {DZS_GRID.size}"
      f"   (min A95 = {out['diagnostics']['min_A95_frequentist']:.2f} at dzs = {out['diagnostics']['min_A95_at_dzs']:.3f})")
print(f"response per unit A (doc window): {100*resp_doc:.4f} % of fsigma8 at z<=2")
print(f"zero injection A: {zero['A']:.2e}  (chi2 = {zero['chi2']:.2e})")
for v in validations:
    print(f"validation dzs={v['dzs']:.5f} basis={v['basis']} max_step={v['max_step']:.2e}"
          f" -> max|R|={v['max_abs_lin_response']:.3e}  max rel dev (FD vs linear) ="
          f" {100*v['max_rel_dev_fd_vs_lin']:.2f}%")
for inj in injections:
    print(f"inject dzs={inj['dzs']:.5f} A={inj['A_injected']:.3f} -> A_hat={inj['A_recovered']:.3f}"
          f" phi_hat={inj['phi_recovered']:+.3f} dchi2_gate={inj['dchi2_gate_on_gate_mock']:.2f}"
          f" frac_shift={100*inj['max_frac_shift_fs8']:.4f}%")
print("files: results/scan_results.json, results/fig_s3_fs8.png|svg")
