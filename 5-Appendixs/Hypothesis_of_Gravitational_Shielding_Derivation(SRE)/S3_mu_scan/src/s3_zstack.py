"""S3 z-stack (Phase 3): dedicated z-bin stacking of the SRE chiral
G-oscillation in the f_sigma8 channel -> weak cosmological lower bound on alpha_scale.

Route (fixed by Phase 1 sec.7 + Phase 2 sec.12.2)
-------------------------------------------------
The chiral channel Gamma_chiral = xi(z) sin(.) / (r^2 ln(r/l_P)) has
  * NO sharp P(k) scale feature (Phase 2 sec.12.1: 1/r^2 IS the Newtonian 1/r^2;
    only 1/ln(r/l_P) varies, by 3.4% over two decades in r), and
  * a weak-lensing (kappa / shear) response 2.6-240x WORSE than f_sigma8
    (Phase 2 sec.9-10).
Hence the only surviving probe is f_sigma8(z), and the only way to beat the
existing 22-point compilation is a *dedicated z-bin stack whose bin width is
matched to the oscillation period* P = Delta z_s / theta, so that bin averaging
does not low-pass the signal away.

Data status (IMPORTANT -- read before trusting any number below)
----------------------------------------------------------------
No raw survey catalog (tracers with ra/dec/z) exists in this workspace, so the
literal "stack on the raw catalog" route CANNOT be executed here.  This script
therefore delivers, with NO invented data points:

  (1) a *general, mock-validated* stacking pipeline
          catalog z -> z-bins (width u*P) -> bin-averaged transfer-function
          response -> full-covariance GLS estimate of A -> 95% upper bound
          -> alpha_scale lower bound;
  (2) an HONEST consistency demonstration on the 22-point compilation CSV.
      That file's points are HETEROGENEOUS bins: their edges are not
      commensurate with P, so the bin-edge phase is uncontrolled.  The run
      therefore reproduces the Phase 1 doc-window bound (a cross-check), and is
      explicitly NOT a matched stack.  A real matched stack needs a uniform
      catalog;
  (3) a Fisher forecast answering "how large a survey is needed to reach the
      gate alpha_scale = 8e-4", parameterised by
      (z-range, bin width u*P, per-bin fractional error sigma_frac, f_sky).

Statistics -- conventions kept IDENTICAL to Phase 1 (do not mix conventions)
---------------------------------------------------------------------------
  model      y_i = s8 * U_i * (1 + B1 <R_s>_i + B2 <R_c>_i),  <R> = bin average
             U_i = D'(x_i)/D01  (unit-sigma8 LambdaCDM f_sigma8)
  fit        full-covariance GLS, free (s8, B1, B2)
  A          = hypot(B1, B2) / s8
  95% bound  r95 = sqrt(2.71 / lambda_min(profiled 2x2 info))
             A95_offsetfree  = r95 / s8                (ideal sensitivity)
             A95_frequentist = (|B| + r95) / s8        (honest, same convention
                                                        as the fixed-A gate test)
  gate test  profile chi2 with A fixed at A_gate over (s8, phi); gate_closed
             iff dchi2_gate > 2.71
  alpha_min95 = C_8MPC / A95_frequentist

Self-contained on purpose: Phase 1 (s3_mu_scan.py) stays BYTE-IDENTICAL as the
unoptimised community baseline; Phase 3 re-instantiates the growth-ODE physics
block and is cross-checked against the Phase 1 doc-window response
(6.856450618181618e-3).

Run:  C:\\myapp\\miniconda3\\envs\\ai\\python.exe S3_mu_scan/src/s3_zstack.py
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
DATA_CSV = ROOT / "S3_mu_scan" / "data" / "fs8_compilation_sagredo2018.csv"
RESULTS = ROOT / "S3_mu_scan" / "results"

# --------------------------------------------------------------------------
# theory-tied constants (identical to Phase 1)
# --------------------------------------------------------------------------
THETA = 0.82798
GAMMA = 6.0 / 11.0
OM, OL, OR_ = 0.315, 0.685, 9.2e-5
S8P18 = 0.8110
LP = 1.616255e-35
MPC = 3.0857e22
XI0, WBAR = 0.108, 0.9901
ALPHA_GATE = 8e-4
DZ_DOC = 0.03925
P_DOC = DZ_DOC / THETA
K_DOC = 2.0 * np.pi * THETA / DZ_DOC


def C_amp(r_m):
    """A = C / alpha_scale,  C = xi0 / (2 <W> ln(r/l_P))."""
    return XI0 / (2.0 * WBAR * np.log(r_m / LP))


C_8MPC = C_amp(8 * MPC)
A_GATE = C_8MPC / ALPHA_GATE

# --------------------------------------------------------------------------
# growth ODE in x = ln a :  D'' + P D' = Q D (1 + eps)      [same as Phase 1]
# --------------------------------------------------------------------------
X0, XON = np.log(0.01), np.log(1.0 / 6.0)


def E2(x):
    a = np.exp(x)
    return OM / a ** 3 + OR_ / a ** 4 + OL


def Pcoef(x):
    a = np.exp(x)
    return 2.0 - (3 * OM / a ** 3 + 4 * OR_ / a ** 4) / (2 * E2(x))


def Qcoef(x):
    a = np.exp(x)
    return 1.5 * (OM / a ** 3) / E2(x)


def solve_baseline():
    def rhs(x, y):
        return [y[1], -Pcoef(x) * y[1] + Qcoef(x) * y[0]]
    return solve_ivp(rhs, (X0, 0.0), [0.01, 0.01], method="DOP853",
                     rtol=1e-11, atol=1e-13, dense_output=True).sol


def eps_vec(x, k_arr):
    """unit-amplitude (sin, cos) envelopes for every k; 0 before z=5."""
    if x < XON:
        z = np.zeros_like(k_arr)
        return z, z.copy()
    zz = np.exp(-x) - 1.0
    env = np.exp(0.15 * zz)
    return env * np.sin(k_arr * zz), env * np.cos(k_arr * zz)


BASE = solve_baseline()
D01 = float(BASE(0.0)[0])


def solve_responses(k_arr, xs):
    """f_sigma8 response per unit amplitude of the sin/cos templates.

    f_sigma8_tot / f_sigma8_base - 1 = B1 * Rs + B2 * Rc,  B = A*(cos phi, sin phi)
    Returns (Rs, Rc) each of shape (len(k_arr), len(xs)).  Same physics as Phase 1.
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


def validate_response(k, delta=1e-3, basis="sin", max_step=2.5e-4, zz=(0.2, 0.5, 0.8, 1.1)):
    """FD check: full nonlinear solution vs the linear response at selected z."""
    xv = -np.log(1.0 + np.array(zz))

    def rhs(x, y):
        e = eps_vec(x, np.array([k]))[0 if basis == "sin" else 1][0]
        return [y[1], -Pcoef(x) * y[1] + Qcoef(x) * y[0] * (1.0 + delta * e)]
    y0 = BASE(XON)
    sol = solve_ivp(rhs, (XON, 0.0), [y0[0], y0[1]], method="DOP853",
                    rtol=1e-11, atol=1e-14, max_step=max_step, dense_output=True)
    Dt, Dtp = sol.sol(xv)
    Dt0 = sol.sol(0.0)[0]
    ratio = (Dtp / Dt) * (Dt / Dt0) / (np.array([BASE(x)[1] for x in xv]) / D01) - 1.0
    Rs, Rc = solve_responses(np.array([k]), xv)
    lin = (Rs if basis == "sin" else Rc)[0]
    return ratio / delta, lin


# --------------------------------------------------------------------------
# dense z grid + doc-window f_sigma8 response
# --------------------------------------------------------------------------
ZG = np.linspace(0.0, 2.0, 1601)
XG = -np.log(1.0 + ZG)
D0PG = np.array([BASE(x)[1] for x in XG])
UG = D0PG / D01                                        # unit-sigma8 LambdaCDM f_sigma8

RS_ALL, RC_ALL = solve_responses(np.array([K_DOC]), XG)
RS_ZG, RC_ZG = RS_ALL[0], RC_ALL[0]
RESP_POINT = float(np.max(np.hypot(RS_ZG, RC_ZG)))    # pointwise, per unit A

# --------------------------------------------------------------------------
# z-bin machinery: edges matched to the period (bin width u*P)
# --------------------------------------------------------------------------
def make_edges(z_lo, z_hi, u, dzs=DZ_DOC):
    """Bin edges with width u * P (P = dzs/theta), spanning [z_lo, z_hi]."""
    P = dzs / THETA
    w = u * P
    n = max(int(np.floor((z_hi - z_lo) / w)), 1)
    return np.linspace(z_lo, z_hi, n + 1)


def bin_average(edges, arr):
    """Trapezoid mean of arr(ZG) inside each bin."""
    out = np.empty(edges.size - 1)
    for j in range(edges.size - 1):
        z1, z2 = edges[j], edges[j + 1]
        m = (ZG >= z1) & (ZG <= z2)
        out[j] = trapz(arr[m], ZG[m]) / (z2 - z1) if m.sum() >= 2 else np.nan
    return out


def bin_centers(edges):
    return 0.5 * (edges[:-1] + edges[1:])


def bin_theory(edges):
    """Bin-averaged (U, Rs, Rc) for the doc window."""
    return bin_average(edges, UG), bin_average(edges, RS_ZG), bin_average(edges, RC_ZG)


def bin_catalog(z_array, edges):
    """Concrete catalog->bins interface: count tracers per bin (and mean z)."""
    idx = np.digitize(np.asarray(z_array, float), edges) - 1
    n = np.array([int((idx == j).sum()) for j in range(edges.size - 1)])
    zc = bin_centers(edges)
    zbar = np.array([float(np.mean(z_array[idx == j])) if n[j] > 0 else np.nan
                     for j in range(edges.size - 1)])
    return n, zc, zbar


# --------------------------------------------------------------------------
# statistics: full-covariance GLS, 95% bounds, fixed-A gate test (Phase 1口径)
# --------------------------------------------------------------------------
PHI_GRID = np.linspace(0.0, 2 * np.pi, 721, endpoint=False)


def gls_fit(y, cov_inv, U, rs, rc):
    """Free (s8, B1, B2) GLS fit; A = hypot(B1,B2)/s8; profiled 2x2 bound."""
    X = np.column_stack([U, U * rs, U * rc])
    M = X.T @ cov_inv @ X
    beta = np.linalg.solve(M, X.T @ cov_inv @ y)
    s8, B1, B2 = (float(v) for v in beta)
    r = y - X @ beta
    chi2 = float(r @ cov_inv @ r)
    Mpp = M[1:, 1:] - np.outer(M[1:, 0], M[0, 1:]) / M[0, 0]
    r95 = float(np.sqrt(2.71 / np.linalg.eigvalsh(Mpp)[0]))
    B = float(np.hypot(B1, B2))
    A = B / s8 if abs(s8) > 1e-12 else np.inf
    return {"chi2": chi2, "s8": s8, "B1": B1, "B2": B2, "A": A,
            "phi": float(np.arctan2(B2, B1)),
            "A95_offsetfree": r95 / abs(s8) if abs(s8) > 1e-12 else np.inf,
            "A95_frequentist": (B + r95) / abs(s8) if abs(s8) > 1e-12 else np.inf,
            "r95": r95, "lambda_min": float(np.linalg.eigvalsh(Mpp)[0])}


def chi2_fixed_A(A, y, cov_inv, U, rs, rc):
    """chi2 with A fixed, profiled over (s8, phi) on a phi grid."""
    cs, cc = A * np.cos(PHI_GRID), A * np.sin(PHI_GRID)
    cols = U[None, :] * (1.0 + cs[:, None] * rs[None, :] + cc[:, None] * rc[None, :])
    CM = cols @ cov_inv
    cc2 = np.einsum("ij,ij->i", CM, cols)
    cby = CM @ y
    mu = cby / cc2
    r = y[None, :] - mu[:, None] * cols
    c2 = np.einsum("ij,jk,ik->i", r, cov_inv, r)
    j = int(np.argmin(c2))
    return float(c2[j]), float(PHI_GRID[j])


def diag_cov_inv(sig):
    return np.diag(1.0 / np.asarray(sig, float) ** 2)


# --------------------------------------------------------------------------
# (2) consistency demonstration on the 22-point compilation (HETEROGENEOUS bins)
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
WZ_IDX, WZ_C = [12, 13, 14], 1e-3 * np.array([[6.400, 2.570, 0.0],
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
XZ = -np.log(1.0 + Z)
RS_DT, RC_DT = solve_responses(np.array([K_DOC]), XZ)
RS_D, RC_D = RS_DT[0], RC_DT[0]
U_D = np.array([BASE(x)[1] for x in XZ]) / D01

COMP = gls_fit(YOBS, COVI, U_D, RS_D, RC_D)          # POINT responses (Phase 1口径)
c2g, phi_g = chi2_fixed_A(A_GATE, YOBS, COVI, U_D, RS_D, RC_D)
COMP["dchi2_gate"] = float(c2g - COMP["chi2"])
COMP["phi_gate"] = phi_g
COMP["gate_closed"] = bool(c2g - COMP["chi2"] > 2.71)
COMP["alpha_min95_8MPC"] = float(C_8MPC / COMP["A95_frequentist"])
COMP["note"] = ("HETEROGENEOUS compilation bins; point responses; NOT a matched "
                "stack (bin edges not commensurate with P) -- Phase 1 consistency check")

# --------------------------------------------------------------------------
# (1) mock validation of the stacking pipeline (matched bins)
# --------------------------------------------------------------------------
MOCK_U, MOCK_ZLO, MOCK_ZHI, MOCK_SFRAC = 0.25, 0.05, 1.20, 0.01
MOCK_EDGES = make_edges(MOCK_ZLO, MOCK_ZHI, MOCK_U)
MOCK_U_B, MOCK_RS_B, MOCK_RC_B = bin_theory(MOCK_EDGES)
MOCK_ZC = bin_centers(MOCK_EDGES)
MOCK_NB = MOCK_EDGES.size - 1


def mock_run(A_inj, phi_inj, s8_inj, sig_frac, edges=None, n_real=0, seed=12345):
    """Run the stacking fit on a synthetic matched stack.

    n_real=0 -> single noiseless run; n_real>0 -> Monte-Carlo over Gaussian noise.
    Returns dict with recovered A (mean/std over realisations) and the gate test.
    """
    e = MOCK_EDGES if edges is None else edges
    Ub, rsb, rcb = bin_theory(e)
    base = s8_inj * Ub
    sig = sig_frac * base
    cvi = diag_cov_inv(sig)
    signal = 1.0 + A_inj * (np.cos(phi_inj) * rsb + np.sin(phi_inj) * rcb)
    y0 = base * signal
    if n_real <= 0:
        fr = gls_fit(y0, cvi, Ub, rsb, rcb)
        c2g, _ = chi2_fixed_A(A_GATE, y0, cvi, Ub, rsb, rcb)
        return {"A_recovered": fr["A"], "phi_recovered": fr["phi"], "A_std": 0.0,
                "chi2": fr["chi2"], "dchi2_gate": float(c2g - fr["chi2"]),
                "A95_frequentist": fr["A95_frequentist"], "A95_offsetfree": fr["A95_offsetfree"]}
    rng = np.random.default_rng(seed)
    Ah, AP, PH = [], [], []
    for _ in range(n_real):
        y = y0 + rng.normal(0.0, sig)
        fr = gls_fit(y, cvi, Ub, rsb, rcb)
        Ah.append(fr["A"]); AP.append(fr["A95_frequentist"]); PH.append(fr["phi"])
    return {"A_recovered": float(np.mean(Ah)), "A_std": float(np.std(Ah)),
            "A95_frequentist": float(np.mean(AP)), "phi_recovered": float(np.mean(PH)),
            "n_real": n_real,
            "phi_circ_std": float(np.std(np.exp(1j * np.array(PH))))}


PHI_INJ = 0.7
mock_zero = mock_run(0.0, 0.0, S8P18, MOCK_SFRAC)
mock_gate = mock_run(A_GATE, PHI_INJ, S8P18, MOCK_SFRAC)
mock_gate_fine = mock_run(A_GATE, PHI_INJ, S8P18, MOCK_SFRAC, edges=make_edges(MOCK_ZLO, MOCK_ZHI, 0.125))
mock_2 = mock_run(2.0, PHI_INJ, S8P18, MOCK_SFRAC)

# Monte-Carlo unbiasedness (matched stack, realistic per-bin scatter)
mc_sigma = MOCK_SFRAC
mc_zero = mock_run(0.0, 0.0, S8P18, mc_sigma, n_real=500)
mc_inj = mock_run(A_GATE, PHI_INJ, S8P18, mc_sigma, n_real=500)

# injection-recovery linearity curve (noiseless, matched stack)
A_GRID = np.geomspace(0.01, 3.0, 25)
inj_curve = [{"A_inj": float(a), "A_rec": float(mock_run(a, PHI_INJ, S8P18, MOCK_SFRAC)["A_recovered"])}
             for a in A_GRID]

# independent FD validation of the response used in the stack
validations = []
for basis in ("sin", "cos"):
    fd, lin = validate_response(K_DOC, basis=basis)
    amp = float(np.max(np.abs(lin)))
    dev = float(np.max(np.abs(fd - lin))) / max(amp, 1e-30)
    validations.append({"basis": basis, "max_abs_lin_response": amp,
                        "max_rel_dev_fd_vs_lin": dev})

# --------------------------------------------------------------------------
# (3) Fisher forecast: how big a survey to reach the gate?
# --------------------------------------------------------------------------
def comoving_chi(z):
    """Comoving distance in Mpc/h (c/H0 = 2997.9 Mpc/h), flat LCDM."""
    zz = np.linspace(0.0, max(float(np.max(z)), 1e-6), 2000)
    Ezi = 1.0 / np.sqrt(OM * (1 + zz) ** 3 + OL)
    inv = np.concatenate([[0.0], np.cumsum(0.5 * (Ezi[1:] + Ezi[:-1]) * np.diff(zz))])
    return np.interp(z, zz, inv) * 2997.9


def forecast(dzs, u, z_lo, z_hi, sig_frac, s8=S8P18):
    """Projected 95% upper bound on A and alpha_scale lower bound for a survey.

    Assumes a uniform per-bin fractional error sig_frac over bins of width u*P.
    Returns projected (offset-free = median frequentist) A95 and the exact
    per-bin sigma_frac that would be needed to reach the gate.
    """
    k = 2.0 * np.pi * THETA / dzs
    edges = make_edges(z_lo, z_hi, u, dzs)
    rs_a, rc_a = solve_responses(np.array([k]), -np.log(1.0 + ZG))
    rs_b, rc_b = bin_average(edges, rs_a[0]), bin_average(edges, rc_a[0])
    Sss, Scc, Ssc = float(np.sum(rs_b ** 2)), float(np.sum(rc_b ** 2)), float(np.sum(rs_b * rc_b))
    I0 = np.array([[Sss, Ssc], [Ssc, Scc]])
    lam0 = float(np.linalg.eigvalsh(I0)[0])
    A95 = sig_frac * np.sqrt(2.71 / lam0) / s8 if lam0 > 0 else np.inf
    sig_req = A_GATE * s8 * np.sqrt(lam0 / 2.71)
    return {"dzs": float(dzs), "P": float(dzs / THETA), "u": float(u),
            "z_lo": float(z_lo), "z_hi": float(z_hi), "N_bins": int(edges.size - 1),
            "N_cycles": float((z_hi - z_lo) / (dzs / THETA)),
            "lambda_min0": lam0, "sum_rs2": Sss, "sum_rc2": Scc,
            "sig_frac": float(sig_frac), "A95_projected": float(A95),
            "alpha_min95_8MPC": float(C_8MPC / A95) if A95 > 0 else np.inf,
            "sigma_frac_for_gate": float(sig_req),
            "gate_reachable": bool(A95 < A_GATE)}


FC_BINWIDTH = [forecast(DZ_DOC, u, 0.05, 1.20, 0.01) for u in (0.125, 0.25, 0.5, 1.0)]
FC_SIG = [forecast(DZ_DOC, 0.25, 0.05, 1.20, s) for s in np.geomspace(2e-3, 0.3, 24)]
FC_DZS = [forecast(dzs, 0.25, 0.05, 1.20, 0.01) for dzs in np.geomspace(0.02, 0.30, 24)]
FC_ZRANGE = [forecast(DZ_DOC, 0.25, 0.05, zh, 0.01) for zh in np.linspace(0.4, 2.4, 17)]

# survey-size mapping: dry statistical mode count (illustrative, assumption stated)
F_SKY_REF, K_MAX = 0.10, 0.20            # 4000 deg^2, k_max = 0.2 h/Mpc


def modes_per_bin(zc, dz_bin):
    chi_lo, chi_hi = comoving_chi(max(zc - 0.5 * dz_bin, 0.0)), comoving_chi(zc + 0.5 * dz_bin)
    V = (4.0 / 3.0) * np.pi * (chi_hi ** 3 - chi_lo ** 3) * F_SKY_REF
    return float(V * K_MAX ** 3 / (6.0 * np.pi ** 2))


SURVEY_MAP = []
for row in FC_SIG[::4]:
    zc = 0.55
    Nm = modes_per_bin(zc, row["u"] * P_DOC)
    sig_stat = float(np.sqrt(2.0 / Nm)) if Nm > 0 else np.inf
    SURVEY_MAP.append({"sig_frac": row["sig_frac"], "A95_projected": row["A95_projected"],
                       "alpha_min95_8MPC": row["alpha_min95_8MPC"],
                       "N_modes_per_bin_at_z055": Nm, "sigma_stat_from_modes": sig_stat,
                       "f_sky_ref": F_SKY_REF, "k_max_ref": K_MAX})

GATE_SIG_25 = forecast(DZ_DOC, 0.25, 0.05, 1.20, 0.0)["sigma_frac_for_gate"]
GATE_SIG_125 = forecast(DZ_DOC, 0.125, 0.05, 1.20, 0.0)["sigma_frac_for_gate"]

# --------------------------------------------------------------------------
# figure
# --------------------------------------------------------------------------
RESULTS.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 140, "savefig.bbox": "tight"})
fig, ax = plt.subplots(2, 2, figsize=(11.5, 8.0))
fig.suptitle("S3 Phase 3: dedicated $z$-bin stacking of the SRE chiral oscillation "
             "($f\\sigma_8$ channel, $" + f"\\Delta z_s$={DZ_DOC}, $P$={P_DOC:.4f})",
             fontsize=12, fontweight="bold")

a0 = ax[0, 0]
a0.plot(ZG, np.hypot(RS_ZG, RC_ZG), "-", color="#1565c0", lw=1.2, label="point $|R|$ per unit $A$")
for u, c in ((0.25, "#c62828"), (0.5, "#ef6c00")):
    e = make_edges(0.05, 1.20, u)
    a0.step(bin_centers(e), np.hypot(bin_average(e, RS_ZG), bin_average(e, RC_ZG)),
            where="mid", color=c, lw=1.2, label=f"bin-averaged, $u$={u}$P$")
a0.set_xlim(0, 1.3); a0.set_xlabel("redshift $z$"); a0.set_ylabel("$f\\sigma_8$ response per unit $A$")
a0.legend(fontsize=7.5)
a0.set_title(f"(a) reviewer-matched bins keep the fast wiggle (peak $\\approx${RESP_POINT:.2e})", fontsize=9.5)

a1 = ax[0, 1]
a1.loglog([r["A_inj"] for r in inj_curve], [r["A_rec"] for r in inj_curve],
          "o-", ms=3.5, lw=1.2, color="#2e7d32", label="matched stack, noiseless")
a1.loglog(A_GRID, A_GRID, "--", color="#999", lw=1.1, label="1:1")
a1.axhline(A_GATE, color="#ef6c00", lw=1.3, label=f"gate $A$={A_GATE:.3f}")
a1.set_xlabel("injected $A$"); a1.set_ylabel("recovered $\\hat A$")
a1.legend(fontsize=7.5, loc="upper left")
a1.set_title("(b) injection-recovery: unbiased over 2 decades", fontsize=9.5)

a2 = ax[1, 0]
for u, c in ((0.125, "#0d47a1"), (0.25, "#2e7d32"), (0.5, "#ef6c00"), (1.0, "#6a1b9a")):
    fc = forecast(DZ_DOC, u, 0.05, 1.20, 0.01)
    sig = np.geomspace(2e-3, 0.3, 60)
    A95 = [sig_i * np.sqrt(2.71 / fc["lambda_min0"]) / S8P18 for sig_i in sig]
    a2.loglog(sig, A95, "-", color=c, lw=1.3, label=f"$u$={u}$P$, $N_b$={fc['N_bins']}")
a2.axhline(A_GATE, color="#ef6c00", lw=1.5, label=f"gate $A$={A_GATE:.3f}")
a2.axvline(GATE_SIG_25, color="#c62828", ls=":", lw=1.2)
a2.axvline(GATE_SIG_125, color="#0d47a1", ls=":", lw=1.2)
a2.set_xlabel("per-bin fractional error $\\sigma_{f\\sigma_8}$")
a2.set_ylabel("projected $A_{95}$")
a2.legend(fontsize=7)
a2.set_title(f"(c) gate needs $\\sigma_{{bin}}\\lesssim${100*GATE_SIG_25:.2f}% ($u$=0.25$P$)", fontsize=9.5)

a3 = ax[1, 1]
for sf, c in ((0.005, "#2e7d32"), (0.01, "#ef6c00"), (0.02, "#c62828")):
    rows = [forecast(DZ_DOC, 0.25, 0.05, zh, sf) for zh in np.linspace(0.4, 2.4, 17)]
    a3.plot([r["z_hi"] for r in rows], [r["A95_projected"] for r in rows],
            "o-", ms=3.5, lw=1.2, color=c, label=f"$\\sigma_{{bin}}$={100*sf:.1f}%")
a3.axhline(A_GATE, color="#ef6c00", lw=1.5, label=f"gate $A$={A_GATE:.3f}")
a3.set_xlabel("survey depth $z_{max}$"); a3.set_ylabel("projected $A_{95}$")
a3.legend(fontsize=7.5)
a3.set_title("(d) depth helps only as $\\sqrt{N_{cycles}}$; width floor dominates", fontsize=9.5)

fig.tight_layout()
fig.savefig(RESULTS / "fig_s3_zstack.png")
fig.savefig(RESULTS / "fig_s3_zstack.svg")
plt.close(fig)

# --------------------------------------------------------------------------
# outputs
# --------------------------------------------------------------------------
out = {
    "meta": {"theta_conformal": THETA, "doc_window_dzs": DZ_DOC, "doc_period": P_DOC,
             "k_doc": K_DOC, "A_coef_8Mpc": C_8MPC, "A_gate_8Mpc": A_GATE,
             "alpha_gate": ALPHA_GATE, "s8_fiducial": S8P18,
             "data_status": "no raw catalog in workspace; dual-track (mock-validated "
                            "pipeline + Fisher forecast); no invented data",
             "response_point_per_unit_A": RESP_POINT},
    "compilation_consistency": COMP,
    "mock_validation": {
        "setup": {"u": MOCK_U, "z_lo": MOCK_ZLO, "z_hi": MOCK_ZHI, "sig_frac": MOCK_SFRAC,
                  "N_bins": MOCK_NB, "N_cycles": (MOCK_ZHI - MOCK_ZLO) / P_DOC},
        "zero_injection_noiseless": mock_zero,
        "gate_injection_noiseless": mock_gate,
        "gate_injection_noiseless_u0125": mock_gate_fine,
        "A2_injection_noiseless": mock_2,
        "monte_carlo_zero": mc_zero,
        "monte_carlo_gate": mc_inj,
        "injection_recovery_curve": inj_curve,
        "finite_difference_validations": validations},
    "fisher": {"binwidth_scan": FC_BINWIDTH, "sigma_scan": FC_SIG,
               "dzs_scan": FC_DZS, "zrange_scan": FC_ZRANGE,
               "survey_size_mapping": SURVEY_MAP,
               "sigma_frac_for_gate_u025": GATE_SIG_25,
               "sigma_frac_for_gate_u0125": GATE_SIG_125},
}
(RESULTS / "zstack.json").write_text(json.dumps(out, indent=1), encoding="utf-8")

print("=== S3 z-stack (Phase 3, conda env ai) ===")
print(f"doc window: dzs={DZ_DOC}  P={P_DOC:.4f}  k={K_DOC:.2f}/z")
print(f"point response per unit A (peak) = {RESP_POINT:.6e}")
print(f"PD validation: sin dev {100*validations[0]['max_rel_dev_fd_vs_lin']:.3f}% | "
      f"cos dev {100*validations[1]['max_rel_dev_fd_vs_lin']:.3f}%")
print("-- compilation consistency (HETEROGENEOUS bins, point responses) --")
print(f"  A = {COMP['A']:.2f}  A95_off = {COMP['A95_offsetfree']:.2f}  "
      f"A95_freq = {COMP['A95_frequentist']:.2f}  dchi2_gate = {COMP['dchi2_gate']:.2f}  "
      f"gate_closed = {COMP['gate_closed']}  alpha_min95 = {COMP['alpha_min95_8MPC']:.2e}")
print("-- mock validation (matched stack) --")
print(f"  setup: u={MOCK_U}P ({MOCK_NB} bins, {out['mock_validation']['setup']['N_cycles']:.1f} cycles), "
      f"sigma_frac={MOCK_SFRAC}")
for name, m in (("zero", mock_zero), ("gate(0.509)", mock_gate),
                ("gate u=0.125P", mock_gate_fine), ("A=2.0", mock_2)):
    print(f"  {name:14s}: A_hat = {m['A_recovered']:.4f}  phi_hat = {m.get('phi_recovered', float('nan')):+.3f}  "
          f"chi2 = {m.get('chi2', float('nan')):.2e}")
print(f"  Monte-Carlo (N=500): zero -> <A> = {mc_zero['A_recovered']:.2e} +/- {mc_zero['A_std']:.2e} | "
      f"gate -> <A> = {mc_inj['A_recovered']:.4f} +/- {mc_inj['A_std']:.4f} "
      f"(injected {A_GATE:.3f})")
print("-- Fisher forecast (projected A95; gate = %.3f) --" % A_GATE)
for r in FC_BINWIDTH:
    print(f"  u={r['u']}P: N_b={r['N_bins']}, cycles={r['N_cycles']:.1f}, "
          f"lam_min0={r['lambda_min0']:.3e} -> A95(sig=1%)={r['A95_projected']:.3f}, "
          f"sig_req_gate={r['sigma_frac_for_gate']:.4f}")
print(f"  gate thresholds: sig_frac <= {100*GATE_SIG_25:.3f}% (u=0.25P) | "
      f"{100*GATE_SIG_125:.3f}% (u=0.125P)")
print("  illustrative mode count (f_sky=%.2f, k_max=%.1f h/Mpc) at z=0.55:" % (F_SKY_REF, K_MAX))
for s in SURVEY_MAP:
    print(f"    sig={100*s['sig_frac']:.2f}% -> N_modes/bin={s['N_modes_per_bin_at_z055']:.3e}, "
          f"stat sigma={s['sigma_stat_from_modes']:.2e}, A95={s['A95_projected']:.3f}")
print("files: results/zstack.json, results/fig_s3_zstack.png|svg")
