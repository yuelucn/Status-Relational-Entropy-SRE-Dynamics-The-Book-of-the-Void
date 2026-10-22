"""S3 Phase 4 (real data): BOSS DR12 CMASSLOWZTOT -> matched narrow z-bin f_sigma8.

Front-end for the Phase 3 matched z-bin stack, now on a REAL catalog:
    FITS(galaxy + random, NGC + SGC) -> survey weights (SYSTOT*CP*NOZ, FKP P0=2e4)
    -> z-bins of width u*P (P = dzs/theta = 0.047402, u = 0.25 -> w = 0.0118506,
       lattice anchored at z = 0.15, 46 full bins up to z = 0.6951)
    -> per (bin, cap): NGP FKP field F = FT[n_d w - alpha n_r w] on one global grid,
       multipoles P0/P2/P4 with LOS = cap centroid, data-driven Gaussian covariance
    -> per (bin, cap): Kaiser fit (b*s8, f*s8) on [P0; P2; P4] with EXACT
       GRID WINDOW-CONVOLUTION design (conv_tables: the ensemble of the
       measured estimator for the slab-cut grid field is the DISCRETE Dirichlet
       window convolution of the source spectrum -- L_l on the shell's ACTUAL
       modes, NGP deconv inside, shot noise subtracted exactly per multipole),
       model linear in theta = (B2, BF, F2) = ((b s8)^2, (b s8)(f s8),
       (f s8)^2)), shot noise free
    -> CSV  results/fs8_boss_bins.csv  (consumed by s3_real_stack.py)

Modelling simplifications (HONEST, flagged; each is conservative or second-order
for a LOWER bound on alpha_scale):
  * linear Kaiser RSD only (no Fingers-of-God / nonlinear damping): known few-%
    per-bin bias; any z-dependent residual leaks into |B| and INCREASES A95
    (frequentist bound (|B|+r95)/s8) -> conservative for alpha_scale lower bound;
  * EH98 (1998) wiggly linear P(k) shape, no Boltzmann code; only the shape enters;
  * bin window = radial top-hat in comoving distance; angular (cap) and FKP-weight
    windows neglected inside a bin (k_perp smearing < dk/2, weight smooth);
  * Gaussian covariance from measured |F(k)|^2, shells assumed independent
    (dk = 0.02 h/Mpc > radial-window half-width); validated by mocks;
  * fiducial cosmology = growth-ODE cosmology (Om = 0.315); AP mismatch vs the
    BOSS fiducial (Om = 0.31) is ~0.2% in distances, absorbed by free s8.
  * normalisation integral I = alpha^2 (sum nr^2 - sum w_r^2) / dx^3 from the
    NGP grid: exact Poisson expectation of sum nr^2 with the self-pair term
    subtracted (Poisson cell-noise floor handled exactly).

Modes
  data   : real BOSS run (default ngrid 512)
  cov    : mock-MC covariance -- nm zero-injection Gaussian light cones through
           the IDENTICAL pipeline (geometry/mask/weights/bins/estimator as data);
           writes results/fs8_cov_mocks_{caps}.npz consumed by data/synth fits
           (the radial top-hat correlates shells, so naive per-shell C is not
           usable; disjoint bins are ~uncorrelated -> per-(bin,cap) blocks)
  synth  : Gaussian-density light cone on the REAL BOSS geometry/mask (positions
           drawn from the real randoms) with Kaiser RSD and an INJECTED SRE
           oscillation in f_sigma8(z); injection-recovery of the whole pipeline
  mock   : run a PATCHY/EZ-style ASCII mock through the identical code path

Run (conda env ai, absolute interpreter):
  C:\\myapp\\miniconda3\\envs\\ai\\python.exe S3_mu_scan/src/s3_fs8_bins.py cov --nm 30
  C:\\myapp\\miniconda3\\envs\\ai\\python.exe S3_mu_scan/src/s3_fs8_bins.py data
  C:\\myapp\\miniconda3\\envs\\ai\\python.exe S3_mu_scan/src/s3_fs8_bins.py synth --A 0.0 --A 0.509
"""
from __future__ import annotations

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import scipy.fft as sfft
from scipy.integrate import solve_ivp
from scipy.ndimage import map_coordinates

trapz = getattr(np, "trapezoid", None) or np.trapz

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "S3_mu_scan" / "data" / "boss_dr12"
RESULTS = ROOT / "S3_mu_scan" / "results"

# --------------------------------------------------------------------------
# theory-tied constants (identical to Phase 1 / Phase 3 -- do not change)
# --------------------------------------------------------------------------
THETA = 0.82798
DZ_DOC = 0.03925
P_DOC = DZ_DOC / THETA                      # 0.047402
K_DOC = 2.0 * np.pi * THETA / DZ_DOC        # 132.54 /z
OM, OL, OR_ = 0.315, 0.685, 9.2e-5          # fiducial (== growth ODE cosmology)
C_H = 2997.92458                            # c/H0 in Mpc/h
XI0, WBAR = 0.108, 0.9901
LP_M = 1.616255e-35
MPC_M = 3.0857e22


def C_amp(r_m):
    return XI0 / (2.0 * WBAR * np.log(r_m / LP_M))


C_8MPC = C_amp(8.0 * MPC_M)                 # 4.071e-4
ALPHA_GATE = 8e-4
A_GATE = C_8MPC / ALPHA_GATE                # 0.509

# survey / estimator configuration
U_BIN = 0.25                                # bin width in units of the period
Z_LO, Z_HI = 0.15, 0.70                     # BOSS CMASSLOWZTOT nominal range
P0_FKP = 2.0e4                              # FKP P0, (Mpc/h)^3
K_LO, K_HI, DK = 0.02, 0.20, 0.02           # h/Mpc
BIN_W = U_BIN * P_DOC                       # 0.0118506
N_BINS = int(np.floor((Z_HI - Z_LO) / BIN_W))
BIN_EDGES = Z_LO + BIN_W * np.arange(N_BINS + 1)   # last edge 0.6951
K_EDGES = np.arange(K_LO, K_HI + 1e-9, DK)
K_CENTERS = 0.5 * (K_EDGES[:-1] + K_EDGES[1:])
NK = K_CENTERS.size

BOSS_FILES = {
    "galaxy_N": DATA_DIR / "galaxy_DR12v5_CMASSLOWZTOT_North.fits.gz",
    "galaxy_S": DATA_DIR / "galaxy_DR12v5_CMASSLOWZTOT_South.fits.gz",
    "random_N": DATA_DIR / "random0_DR12v5_CMASSLOWZTOT_North.fits.gz",
    "random_S": DATA_DIR / "random0_DR12v5_CMASSLOWZTOT_South.fits.gz",
}

# --------------------------------------------------------------------------
# cosmology: comoving distance (Mpc/h) and growth (duplicated from s3_zstack,
# cross-checked against the Phase 3 doc-window response 6.856450618181618e-3)
# --------------------------------------------------------------------------
_ZG_FINE = np.linspace(0.0, 2.0, 24001)
_EZ = np.sqrt(OM * (1 + _ZG_FINE) ** 3 + OR_ * (1 + _ZG_FINE) ** 4 + OL)
_CHI_G = np.concatenate(
    [[0.0], np.cumsum(0.5 * (1.0 / _EZ[1:] + 1.0 / _EZ[:-1]) * np.diff(_ZG_FINE))]) * C_H


def chi_of_z(z):
    return np.interp(z, _ZG_FINE, _CHI_G)


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
    if x < XON:
        z = np.zeros_like(k_arr)
        return z, z.copy()
    zz = np.exp(-x) - 1.0
    env = np.exp(0.15 * zz)
    return env * np.sin(k_arr * zz), env * np.cos(k_arr * zz)


BASE = solve_baseline()
D01 = float(BASE(0.0)[0])


def solve_responses(k_arr, xs):
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
    s1t, c1t = Y0[0::4], Y0[2::4]
    D0p = BASE(xs)[1] if xs.ndim else np.array([BASE(x)[1] for x in xs])
    s1, s2, c1, c2 = Yx[0::4], Yx[1::4], Yx[2::4], Yx[3::4]
    Rs = ((D0p[None, :] + s2) / D0p[None, :]) * (D01 / (D01 + s1t))[:, None] - 1.0
    Rc = ((D0p[None, :] + c2) / D0p[None, :]) * (D01 / (D01 + c1t))[:, None] - 1.0
    return Rs, Rc


# --------------------------------------------------------------------------
# EH98 wiggly transfer function -> unit-sigma8 linear shape p(k), (Mpc/h)^3
# --------------------------------------------------------------------------
def eh98_pshape(k_hmpc, om=OM, ob=0.049, h=0.676, ns=0.965, tcmb=2.7255):
    """Linear P(k) shape normalised to sigma8 = 1 at z = 0 (growth-consistent)."""
    k = np.atleast_1d(np.asarray(k_hmpc, float)) * h          # Mpc^-1
    omhh, obhh, th = om * h * h, ob * h * h, tcmb / 2.726
    f_b = obhh / omhh
    k_eq = 7.46e-2 * omhh * th ** -2
    z_eq = 2.50e4 * omhh * th ** -4
    b1 = 0.313 * omhh ** -0.419 * (1 + 0.607 * omhh ** 0.674)
    b2 = 0.238 * omhh ** 0.223
    z_dr = 1291 * omhh ** 0.251 / (1 + 0.659 * omhh ** 0.828) * (1 + b1 * obhh ** b2)
    R_dr = 31.5 * obhh * th ** -4 * (1000.0 / z_dr)
    R_eq = 31.5 * obhh * th ** -4 * (1000.0 / z_eq)
    s = (2.0 / (3.0 * k_eq)) * np.sqrt(6.0 / R_eq) * \
        np.log((np.sqrt(1 + R_dr) + np.sqrt(R_dr + R_eq)) / (1 + np.sqrt(R_eq)))
    k_silk = 1.6 * obhh ** 0.52 * omhh ** 0.73 * (1 + (10.4 * omhh) ** -0.95)
    a1 = (46.9 * omhh) ** 0.670 * (1 + (32.1 * omhh) ** -0.532)
    a2 = (12.0 * omhh) ** 0.424 * (1 + (45.0 * omhh) ** -0.582)
    al_c = a1 ** (-obhh / omhh) * a2 ** (-(obhh / omhh) ** 3)
    bb1 = 0.944 / (1 + (458 * omhh) ** -0.708)
    bb2 = (0.395 * omhh) ** -0.0266
    be_c = 1.0 / (1 + bb1 * ((1 - obhh / omhh) ** bb2 - 1))
    y = (1 + z_eq) / (1 + z_dr)
    G_y = y * (-6 * np.sqrt(1 + y) + (2 + 3 * y) *
               np.log((np.sqrt(1 + y) + 1) / (np.sqrt(1 + y) - 1)))
    al_b = 2.07 * k_eq * s * (1 + R_dr) ** -0.75 * G_y
    be_b = 0.5 + obhh / omhh + (3 - 2 * obhh / omhh) * np.sqrt((17.2 * omhh) ** 2 + 1)

    def T0(q, al, be):
        C = 14.2 / al + 386.0 / (1 + 69.9 * q ** 1.08)
        lnt = np.log(np.e + 1.8 * be * q)
        return lnt / (lnt + C * q ** 2)

    def Tsq(k_mpc):
        """EH98 T^2 at k in Mpc^-1 (vectorised)."""
        q = k_mpc / (13.41 * k_eq)
        f_c = 1.0 / (1 + (q * s / 5.4) ** 4)
        T_c = f_c * T0(q, al_c, be_c) + (1 - f_c) * T0(q, 1.0, 1.0)
        T_b = (T0(q, 1.0, 1.0) / (1 + (q * s / 5.2) ** 2) +
               al_b / (1 + (be_b / (q * s)) ** 3) * np.exp(-(q / k_silk) ** 1.4))
        T = f_b * T_b + (1 - f_b) * T_c
        return T ** 2

    # P(k_Mpc) = A k_Mpc^ns T^2  [Mpc^3];  P_h(k_h) = h^-3 P(k_h h)  [(Mpc/h)^3]
    # sigma8 (top-hat R = 8 Mpc/h) of the unit-A spectrum, then normalise.
    # T^2 MUST be evaluated on the internal grid: interpolating it from the
    # caller's k sampling makes the normalisation input-dependent (a coarse
    # input like K_CENTERS clamps T^2 above its k_max, inflates sigma8 by 2.4x
    # and shrinks P by 5.9x).
    kkh = np.geomspace(1e-4, 60.0, 4000)                     # h/Mpc
    Ph1 = (kkh * h) ** ns * Tsq(kkh * h) * h ** -3           # A = 1
    x = kkh * 8.0
    W = 3.0 * (np.sin(x) - x * np.cos(x)) / x ** 3
    s8_1 = np.sqrt(trapz(kkh ** 2 * Ph1 * W ** 2, kkh) / (2 * np.pi ** 2))
    A = 1.0 / s8_1 ** 2
    # P(k_Mpc) = A k_Mpc^ns T^2 [Mpc^3]  ->  P_h(k_h) = h^-3 P(k_h h)
    #          = A h^(ns-3) k_h^ns T^2    [(Mpc/h)^3]   (the h^ns factor was
    # missing before, making P 1/h^ns = 1.46x too large at fixed sigma8)
    P_h = A * (k / h) ** ns * Tsq(k) * h ** (ns - 3.0)       # (Mpc/h)^3
    return k / h, P_h


# canonical fine shape table (single source of truth for fields AND tables)
_KK_P, _PK_P = eh98_pshape(np.geomspace(1e-4, 5.0, 4000))
PSHAPE_FINE = lambda k: np.interp(np.abs(np.atleast_1d(k)), _KK_P, _PK_P)


# --------------------------------------------------------------------------
# Kaiser multipoles with EXACT radial bin-window convolution, DISCRETE modes
#   P_obs(k_par, k_perp) = int |W~(k_par - k_par')|^2 P_K(k',mu') dk_par' / int|W~|^2
#   W~(x) = sinc(x*dchi/2)   (top-hat of width dchi in comoving distance)
#   P_K = p(k) * (b + f mu'^2)^2 = p * (B2 + 2 BF mu'^2 + F2 mu'^4)
# linear in theta = (B2, BF, F2) -> per-mode design columns.
#
# WHY DISCRETE (validated by the mock harness): the outer multipole projection
# must be a SUM over the shell's ACTUAL grid modes, not a continuum <L_l>
# integral.  In a discrete FFT shell the mu-distribution is depleted (the
# kz ~ 0 plane dominates low shells), so <L_2>_disc and <L_4>_disc are NOT
# zero -- a continuum table mismodels both the RSD monopole terms and the
# quadrupole/hexadecapole at the 10-20% level in the lowest shells, and the
# same mismatch never cancels because the data carry the identical discrete
# mu-structure.  Evaluating L_l(mu_m) on the true modes removes the bias
# exactly; the shot-noise floor gets the same treatment in measure_multipoles
# (P_shot * <deconv*L_l>_disc, nonzero for l = 2, 4 in discrete shells).
# --------------------------------------------------------------------------
_MU_G = np.linspace(-1.0, 1.0, 401)
_KP_G = np.linspace(-1.2, 1.2, 961)          # k_par' integration grid (h/Mpc)


def _legendre_l(mu):
    return {0: np.ones_like(mu), 2: (3 * mu ** 2 - 1) / 2.0,
            4: (35 * mu ** 4 - 30 * mu ** 2 + 3) / 8.0}


def _conv_bases(kpar_p, kper2, pshape):
    """Per-mode inner convolution of the three theta bases over k_par'.

    kpar_p: source-mode k_par' grid; kper2: (n_modes,) k_perp^2 of the
    measured mode.  Returns conv (n_modes, 3) for bases (1, 2 mu'^2, mu'^4).
    """
    kp2 = kpar_p ** 2
    kk2 = kp2[None, :] + kper2[:, None]                   # (n_modes, n_kp)
    mu2p = np.where(kk2 > 0, kp2[None, :] / np.maximum(kk2, 1e-30), 0.0)
    pk = pshape(np.sqrt(kk2))
    bases = np.stack([np.ones_like(mu2p), 2.0 * mu2p, mu2p ** 2], axis=-1)
    return bases * pk[..., None]                          # (n_modes, n_kp, 3)


def kaiser_tables_modes(grid, dchi, pshape, los, kpar_grid=None, node_dk=0.003,
                        chunk=4096):
    """Discrete-mode Kaiser tables: {(l, j): array(NK)} for l in (0, 2, 4).

    c[(l, j)][s] = (2l+1)/cnt_s * sum_{m in shell s} L_l(mu_m) * conv_j(m)
    with conv_j the top-hat-window convolution of theta basis j evaluated at
    the measured mode m (k_perp fixed, k_par' integrated; mu' = k_par'/k').

    The outer sum runs over the shell's ACTUAL grid modes.  Modes are grouped
    onto a (k_par, k_perp) node lattice of spacing node_dk: L_l(mu_m) is
    accumulated EXACTLY per mode (bincount), while the k'-convolution is
    evaluated once per node (the first-order interpolation error cancels for
    a smooth mode population; residual is second order, <0.3%).  This makes
    the production grid (5e5 modes/shell) affordable at per-node cost.

    The inner integral is continuum (kernel width pi/dchi >> dk_grid) unless
    kpar_grid is given, in which case it is an EXACT sum over the field's
    aligned k_par modes (LOS = z-hat; used by the mock harness).
    Rows are rank-1 per multipole in the continuum limit: P0 and P2 constrain
    two combinations of (B2, BF, F2) -- the P4 rows (Kaiser: P4 = (8/35) F2 p,
    no B2/BF term) supply the third and lift the exact degeneracy of a
    P0+P2-only thin-slab fit.
    """
    lo = np.asarray(los, float)
    lo = lo / np.linalg.norm(lo)
    nz = int(np.fft.rfftfreq(grid.N, d=grid.dx).size)
    kx_f = 2 * np.pi * np.fft.fftfreq(grid.N, d=grid.dx)
    kz_f = 2 * np.pi * np.fft.rfftfreq(grid.N, d=grid.dx)
    if kpar_grid is not None:
        kpp = np.asarray(kpar_grid, float)
        dkp = float(kpp[1] - kpp[0])
    else:
        kpp = _KP_G
    kid, inshell, cnt = grid.kidx_h, grid.inshell_h, grid.cnt_h
    if kpar_grid is None:
        Knorm = 1.0 / trapz(np.sinc(_KP_G * dchi / 2.0 / np.pi) ** 2, _KP_G)
    # node lattice for (k_par, k_perp): modes -> node index (round to nearest)
    par0 = -(K_HI + 2 * node_dk)
    nper = int(np.ceil((K_HI + 2 * node_dk) / node_dk)) + 2

    def node_conv(kpar_n, kper2_n):
        """theta-basis convolution at node modes, (n_nodes, 3)."""
        conv = np.empty((kpar_n.size, 3))
        for a in range(0, kpar_n.size, chunk):
            sl = slice(a, min(a + chunk, kpar_n.size))
            if kpar_grid is not None:
                W2 = np.sinc((kpar_n[sl, None] - kpp[None, :]) * dchi / 2.0
                             / np.pi) ** 2
                W2 /= W2.sum(axis=1, keepdims=True) * dkp
                cb = _conv_bases(kpp, kper2_n[sl], pshape)
                conv[sl] = (W2[:, :, None] * cb).sum(axis=1) * dkp
            else:
                W2 = np.sinc((kpar_n[sl, None] - kpp[None, :]) * dchi / 2.0
                             / np.pi) ** 2 * Knorm
                cb = _conv_bases(kpp, kper2_n[sl], pshape)
                conv[sl] = trapz(W2[:, :, None] * cb, _KP_G, axis=1)
        return conv

    out = {(l, j): np.zeros(NK) for l in (0, 2, 4) for j in range(3)}
    for s in range(NK):
        sel = np.where(inshell & (kid == s))[0]
        if sel.size == 0:
            continue
        ix, iy, iz = sel // (grid.N * nz), (sel // nz) % grid.N, sel % nz
        kpar_m = kx_f[ix] * lo[0] + kx_f[iy] * lo[1] + kz_f[iz] * lo[2]
        kmag_m = np.sqrt(grid.kmag.ravel()[sel].astype(np.float64) ** 2)
        kper_m = np.sqrt(np.maximum(kmag_m ** 2 - kpar_m ** 2, 0.0))
        mu_m = kpar_m / np.maximum(kmag_m, 1e-12)
        Lm = _legendre_l(mu_m)
        # node grouping: exact per-mode L_l accumulation, conv once per node
        ip = np.round((kpar_m - par0) / node_dk).astype(np.int64)
        iq = np.round(kper_m / node_dk).astype(np.int64)
        key = ip * nper + iq
        uniq, inv = np.unique(key, return_inverse=True)
        kpar_n = par0 + (uniq // nper) * node_dk
        kper_n = (uniq % nper) * node_dk
        conv_n = node_conv(kpar_n, kper_n ** 2)
        for l in (0, 2, 4):
            acc = np.bincount(inv, weights=Lm[l], minlength=uniq.size)
            for j in range(3):
                out[(l, j)][s] = (2 * l + 1) * float(acc @ conv_n[:, j]) / cnt[s]
    return out


def conv_cache(grid, los, pshape):
    """LOS/pshape-dependent constants of conv_tables_raw, built ONCE.

    Rebuilding them per (bin, cap) call costs ~3 s at N=384 (three 384^3
    float32 Legendre products plus 9 full-grid multiplies); they depend only on
    (grid, los, pshape).  Also pre-gathers (deconv * L_l) onto the inshell
    modes so the table loop multiplies 5.6M-vectors instead of 57M-grids.
    """
    lo = np.asarray(los, float)
    lo = lo / np.linalg.norm(lo)
    N, dx = grid.N, grid.dx
    nz = int(np.fft.rfftfreq(N, d=dx).size)
    fx = 2 * np.pi * np.fft.fftfreq(N, d=dx).astype(np.float32)
    K2 = (fx ** 2)[:, None, None] + (fx ** 2)[None, :, None] + (fx ** 2)[None, None, :]
    kp = (fx * lo[0])[:, None, None] + (fx * lo[1])[None, :, None] \
        + (fx * lo[2])[None, None, :]
    mu2 = np.where(K2 > 0, kp ** 2 / np.maximum(K2, 1e-30), 0.0).astype(np.float32)
    del kp
    kk = np.sqrt(np.maximum(K2, 1e-30)).astype(np.float32)
    pk = np.asarray(pshape(kk), np.float32)
    pk = np.where(kk < 1e-6, 0.0, pk)          # DC source removed (alpha-proj)
    B_r = [sfft.rfftn(np.ascontiguousarray(b))
           for b in (pk, 2.0 * mu2 * pk, mu2 ** 2 * pk)]
    del K2, mu2, kk, pk
    fzh = 2 * np.pi * np.fft.rfftfreq(N, d=dx).astype(np.float32)
    km2h = (fx ** 2)[:, None, None] + (fx ** 2)[None, :, None] + (fzh ** 2)[None, None, :]
    muh = ((fx * lo[0])[:, None, None] + (fx * lo[1])[None, :, None]
           + (fzh * lo[2])[None, None, :]) / np.sqrt(np.maximum(km2h, 1e-12))
    Ld = {0: np.ones_like(muh), 2: (3 * muh ** 2 - 1) / 2.0,
          4: (35 * muh ** 4 - 30 * muh ** 2 + 3) / 8.0}
    del km2h, muh
    inshell = grid.inshell_h
    decL = {l: np.ascontiguousarray((grid.deconv * Ld[l]).ravel()[inshell])
            for l in (0, 2, 4)}
    del Ld
    return {"B_r": B_r, "decL": decL, "nz": nz, "kid_ins": grid.kidx_h[inshell]}


def conv_tables_raw(grid, wf, pshape, los, B_r=None, A_floor=0.0, cache=None):
    """RAW exact-grid window-convolution rows {(l, j): array(NK)} WITHOUT the
    1/I normalization (consumed by run_cov where I varies per realization);
    conv_tables below wraps this with the 1/I_val factor.

    wf = survey window as EXPECTED WEIGHTED COUNTS PER CELL (e.g. the NGP
    binned weighted randoms times alpha).  A_floor = white-noise floor of the
    window estimate (e.g. sum(n_r w^2) of the randoms counts), subtracted from
    |Wf~|^2 before the convolution (a constant subtracts A_floor * basis(m)).
    """
    import scipy.fft as sfft

    lo = np.asarray(los, float)
    lo = lo / np.linalg.norm(lo)
    N, dx = grid.N, grid.dx
    Vb = float(grid.L) ** 3
    if cache is None:
        nz = int(np.fft.rfftfreq(N, d=dx).size)
        if B_r is None:
            fx = 2 * np.pi * np.fft.fftfreq(N, d=dx).astype(np.float32)
            K2 = (fx ** 2)[:, None, None] + (fx ** 2)[None, :, None] \
                + (fx ** 2)[None, None, :]
            # TRUE mu'^2 = (k.lo)^2/k^2 on the FULL k-grid (cross terms
            # included); the old sum_i lo_i^2 k_i^2 form dropped the cross terms
            # and is only exact for an axis-aligned LOS (as in the los=(0,0,1)
            # harness).
            kp = (fx * lo[0])[:, None, None] + (fx * lo[1])[None, :, None] \
                + (fx * lo[2])[None, None, :]
            mu2 = np.where(K2 > 0, kp ** 2 / np.maximum(K2, 1e-30),
                           0.0).astype(np.float32)
            del kp
            kk = np.sqrt(np.maximum(K2, 1e-30)).astype(np.float32)
            pk = np.asarray(pshape(kk), np.float32)
            pk = np.where(kk < 1e-6, 0.0, pk)      # DC source removed (alpha-proj)
            B = [pk, 2.0 * mu2 * pk, mu2 ** 2 * pk]
            del K2, mu2, kk, pk
            B_r = [sfft.rfftn(np.ascontiguousarray(b)) for b in B]
            del B
        fxh = 2 * np.pi * np.fft.fftfreq(N, d=dx).astype(np.float32)
        fzh = 2 * np.pi * np.fft.rfftfreq(N, d=dx).astype(np.float32)
        km2h = (fxh ** 2)[:, None, None] + (fxh ** 2)[None, :, None] \
            + (fzh ** 2)[None, None, :]
        # Legendre moments around the CAP LOS (identical to measure_multipoles);
        # the old fzh/|k| form decomposed around the GRID z-axis and silently
        # mismatched the measurement for any non-axial LOS.
        muh = ((fxh * lo[0])[:, None, None] + (fxh * lo[1])[None, :, None]
               + (fzh * lo[2])[None, None, :]) / np.sqrt(np.maximum(km2h, 1e-12))
        Ld = {0: np.ones_like(muh), 2: (3 * muh ** 2 - 1) / 2.0,
              4: (35 * muh ** 4 - 30 * muh ** 2 + 3) / 8.0}
        del km2h, muh
        inshell = grid.inshell_h
        decL = {l: np.ascontiguousarray((grid.deconv * Ld[l]).ravel()[inshell])
                for l in (0, 2, 4)}
        del Ld
        kid_ins = grid.kidx_h[inshell]
        cnt = grid.cnt_h
    else:
        B_r, decL, kid_ins, cnt = cache["B_r"], cache["decL"], cache["kid_ins"], \
            grid.cnt_h
    # float32 window FFT (identical to 1e-7; halves the transient allocation)
    wf32 = np.ascontiguousarray(np.asarray(wf).reshape(N, N, N), dtype=np.float32)
    A = sfft.fftn(wf32, workers=-1)
    del wf32
    A = (A.real ** 2 + A.imag ** 2).astype(np.float32)
    if A_floor:
        A -= np.float32(A_floor)
    Ar = sfft.rfftn(A)
    del A
    ins_g = grid.inshell_h
    out = {}
    for j in range(3):
        C = sfft.irfftn(Ar * B_r[j], s=(N, N, N), workers=-1)
        Ch_ins = np.ascontiguousarray(C[:, :, :B_r[j].shape[2]].ravel()[ins_g])
        del C
        for l in (0, 2, 4):
            acc = np.bincount(kid_ins, weights=decL[l] * Ch_ins, minlength=NK)
            out[(l, j)] = (2 * l + 1) * acc / (cnt * Vb)
        del Ch_ins
    return out


def conv_tables(grid, wf, I_val, pshape, los, B_r=None, A_floor=0.0, cache=None):
    """Normalized exact-grid window-convolution Kaiser tables {(l, j): array(NK)}
    (see conv_tables_raw for the model definition)."""
    raw = conv_tables_raw(grid, wf, pshape, los, B_r=B_r, A_floor=A_floor,
                          cache=cache)
    return {k: v / I_val for k, v in raw.items()}


# --------------------------------------------------------------------------
# FFT grid + estimators
# --------------------------------------------------------------------------
class Grid:
    def __init__(self, pos, ngrid):
        """pos: (Npts,3) observer-frame positions (Mpc/h) of ALL tracers used."""
        lo, hi = pos.min(axis=0) - 120.0, pos.max(axis=0) + 120.0
        self.L = float((hi - lo).max())
        self.center = 0.5 * (lo + hi)
        self.N = int(ngrid)
        self.dx = self.L / self.N
        fx = 2 * np.pi * np.fft.fftfreq(self.N, d=self.dx)
        fz = 2 * np.pi * np.fft.rfftfreq(self.N, d=self.dx)
        kx = fx[:, None, None].astype(np.float32)
        ky = fx[None, :, None].astype(np.float32)
        kz = fz[None, None, :].astype(np.float32)
        self.kmag = np.sqrt(kx ** 2 + ky ** 2 + kz ** 2)
        self.kidx = np.digitize(self.kmag.ravel(), K_EDGES) - 1
        self.kidx = self.kidx.astype(np.int32)
        self.inshell = (self.kidx >= 0) & (self.kidx < NK)
        # half-space (rfftn) variants: axes (x full, y full, z half)
        kmag_h = self.kmag[:, :, :fz.size]
        self.kidx_h = np.digitize(kmag_h.ravel(), K_EDGES) - 1
        self.kidx_h = self.kidx_h.astype(np.int32)
        self.inshell_h = (self.kidx_h >= 0) & (self.kidx_h < NK)
        self.cnt_h = np.bincount(self.kidx_h[self.inshell_h],
                                 minlength=NK).astype(np.float64)
        # NGP assignment window |W|^2 = prod sinc^2(k_i dx/2); store its INVERSE
        s = np.sinc(fx * self.dx / 2.0 / np.pi) ** 2
        sy = np.sinc(fx * self.dx / 2.0 / np.pi) ** 2
        sz = np.sinc(fz * self.dx / 2.0 / np.pi) ** 2
        self.deconv = (1.0 / (s[:, None, None] * sy[None, :, None] * sz[None, None, :])).astype(np.float32)

    def cell_index(self, pos):
        c = np.floor((pos - (self.center - self.L / 2.0)) / self.dx).astype(np.int64)
        np.clip(c, 0, self.N - 1, out=c)
        return (c[:, 0] * self.N + c[:, 1]) * self.N + c[:, 2]


XFER_POWER = 2.7   # mock-construction pre-compensation exponent (see xfer_corr)
                   # calibrated at N=384 by requiring measured/model = 1: p=3
                   # overshot by 12% in B2 and BF, p=2 gave 0.77, hence 2.70.

B_MOCK = 2.0       # linear galaxy bias of the displacement-mode mocks (Zel'dovich
                   # Psi amplitude).  Self-calibrated from the DATA: the per-bin
                   # Kaiser fits give B2_med = 1.708 -> b = sqrt(B2)/s_ref =
                   # 1.307/0.6475 = 2.02, consistent with the BOSS CMASS
                   # literature (b ~= 2.0).  The covariance must be built at the
                   # SAME bias as the data: with the old b = 0.5 the signal part
                   # of (P + shot)^2 was underestimated by up to (2.0/0.5)^4 ~=
                   # 256x, which shrunk sigma_fs8 ~10x and faked chi2/dof ~ 78
                   # plus a spurious gate_closed=True.  (b = 0.5 mocks remain
                   # available via --bmock for pipeline regression tests.)


def xfer_corr(grid, p=XFER_POWER, clamp=1.35):
    """Mock-construction pre-compensation 1/W^p, W = prod sinc(k_i dx / 2).

    The pool is placed by interpolating the grid-sampled Zel'dovich field, so
    the injected contrast is attenuated by two windows that the measurement
    does NOT undo: the interpolation kernel itself (prod sinc^2 for trilinear)
    and a residual top-hat of the cell-quantised construction.  Measured on the
    N=384 harness (dx = 11.31, diag15-20) the net measured/model transfer is
    W^2 in power, i.e. one power of W in amplitude, on top of the interpolant's
    prod sinc^2 -> p = 3.

    The clamp is applied to 1/W PER AXIS (not to the total): 1/W = 1.25 at the
    highest analysed k = 0.20 for dx = 11.3, while the 3-axis corner reaches
    3.9.  Capping at 1.35 keeps the k <= 0.20 correction exact while preventing
    the corner modes (k_3D > 0.4) from being amplified ~50x.
    """
    N, dx = grid.N, grid.dx
    fx = 2 * np.pi * np.fft.fftfreq(N, d=dx)
    fz = 2 * np.pi * np.fft.rfftfreq(N, d=dx)
    s = np.abs(np.sinc(fx * dx / 2 / np.pi))
    sz = np.abs(np.sinc(fz * dx / 2 / np.pi))
    inv = (np.minimum(1.0 / np.maximum(s, 1e-6), clamp)[:, None, None]
           * np.minimum(1.0 / np.maximum(s, 1e-6), clamp)[None, :, None]
           * np.minimum(1.0 / np.maximum(sz, 1e-6), clamp)[None, None, :])
    return (inv ** p).astype(np.float32)


def assign_ngp(grid, pos, w):
    idx = grid.cell_index(pos)
    w = np.asarray(w, np.float64)
    if idx.size < grid.N ** 3 // 64:
        # sparse cloud: build the float32 grid directly instead of a 1.07 GB
        # float64 bincount buffer (same values, halved transient memory -- this
        # matters when several measure_multipoles run concurrently)
        uc, inv = np.unique(idx, return_inverse=True)
        f = np.zeros(grid.N ** 3, np.float32)
        f[uc] = np.bincount(inv, weights=w)
        return f.reshape(grid.N, grid.N, grid.N)
    f = np.bincount(idx, weights=w, minlength=grid.N ** 3)
    return f.reshape(grid.N, grid.N, grid.N).astype(np.float32)


def measure_cache(grid, los):
    """LOS-dependent constants of measure_multipoles, built ONCE per cap.

    Building mu and the three Legendre arrays on the full half grid costs
    ~1.7 s per call at N=512 (three 512x512x257 float32 arrays).  They depend
    only on (grid, los), so the compressed per-shell versions are cached and
    every per-bin measurement reuses them.
    """
    fx = 2 * np.pi * np.fft.fftfreq(grid.N, d=grid.dx).astype(np.float32)
    fz = 2 * np.pi * np.fft.rfftfreq(grid.N, d=grid.dx).astype(np.float32)
    mu = fx[:, None, None] * los[0] + fx[None, :, None] * los[1] \
        + fz[None, None, :] * los[2]
    mu = mu / np.maximum(grid.kmag[:, :, :fz.size], 1e-12)
    L = {0: np.ones_like(mu), 2: (3 * mu ** 2 - 1) / 2.0,
         4: (35 * mu ** 4 - 30 * mu ** 2 + 3) / 8.0}
    del mu
    kid, inshell, cnt = grid.kidx_h, grid.inshell_h, grid.cnt_h
    kid_ins = kid[inshell]
    dc_ins = grid.deconv.ravel()[inshell]
    dconv_mean = np.bincount(kid_ins, weights=dc_ins.astype(np.float64),
                             minlength=NK) / cnt
    # white-floor projection <deconv * L_l> per shell (q-independent)
    white_floor = {}
    for l in (0, 2, 4):
        white_floor[l] = np.bincount(
            kid_ins, weights=(grid.deconv * L[l]).ravel()[inshell].astype(np.float64),
            minlength=NK) / cnt
    Lins = {l: np.ascontiguousarray(L[l].ravel()[inshell]) for l in (0, 2, 4)}
    del L, dc_ins
    return {"kid_ins": kid_ins, "Lins": Lins, "dconv_mean": dconv_mean,
            "white_floor": white_floor}


def randoms_cache(grid, pos_r, w_r):
    """Realization-INDEPENDENT randoms quantities for measure_multipoles.

    The randoms grid, its squared sum and the self-pair term do not change
    across mock realizations (or A injections), yet they cost ~0.65 s per call
    at N=512 (a 512^3 float64 bincount plus two float64 passes).  Store the
    collapsed occupied cells instead (a few MB) and scatter them into the data
    grid, which reproduces nr exactly where it is non-zero.
    """
    w_r = np.asarray(w_r, np.float64)
    idx = grid.cell_index(pos_r)
    uc, inv = np.unique(idx, return_inverse=True)
    uw = np.bincount(inv, weights=w_r).astype(np.float32)
    return {"uc": uc.astype(np.int32), "uw": uw,
            "sum_nr2": float((uw.astype(np.float64) ** 2).sum()),
            "sum_nr": float(uw.astype(np.float64).sum()),
            "sum_w2": float(np.sum(w_r ** 2))}


def measure_multipoles(grid, pos_d, w_d, pos_r, w_r, los, cache=None, rcache=None):
    """One (bin, cap) measurement: returns P_l(NK) for l=0,2,4 and covariance.

    The returned C is the NAIVE Gaussian covariance (independent-shell-modes
    approximation, effective mode count N_ind = V_eff * 4pi k^2 dk / (2pi)^3
    with V_eff from the weighted randoms grid).  Within a bin the radial
    top-hat window correlates shells with |dk_z| <~ 2pi/dchi >> dk, so C
    UNDERSTATES the true errors; the FINAL analysis therefore replaces C by
    the mock-MC covariance blocks (run_cov).  C stays as a diagnostic and for
    the fit when no MC blocks are available.
    """
    w_d = np.asarray(w_d, float)
    w_r = np.asarray(w_r, float)
    alpha = w_d.sum() / w_r.sum()
    if cache is None:
        cache = measure_cache(grid, los)
    if rcache is None:
        rcache = randoms_cache(grid, pos_r, w_r)
    # G = ng - alpha*nr; nr is non-zero only on the cached occupied cells
    G = assign_ngp(grid, pos_d, w_d)
    G.ravel()[rcache["uc"]] -= (alpha * rcache["uw"]).astype(np.float32)
    # scipy float32 FFT: 0.43 s vs 2.41 s for numpy's float64 upcast at N=512
    # (relative difference ~1e-7, far below the statistical error)
    F = sfft.rfftn(G, workers=1)
    q = (F.real ** 2 + F.imag ** 2) * grid.deconv
    del F, G
    # FKP normalisation I = alpha^2 * int n_r,smooth^2 d^3x, in DFT grid units.
    # Poisson point cloud: E[sum c^2] = sum mu^2 + sum_i w_i^2, so the self-pair
    # term MUST be subtracted (at BOSS randoms occupancy mu ~ 0.2-1 the bias
    # would be 2-6x).  All randoms-only terms are realization-independent and
    # come from rcache.
    I = alpha ** 2 * (rcache["sum_nr2"] - rcache["sum_w2"]) / grid.dx ** 3
    if not np.isfinite(I) or I <= 0:
        I = alpha ** 2 * rcache["sum_nr2"] / grid.dx ** 3
    S = float(np.sum(w_d ** 2) + alpha ** 2 * rcache["sum_w2"])
    P_shot = S / I
    denom = max(rcache["sum_nr2"] - rcache["sum_w2"], 1e-30)
    V_eff = rcache["sum_nr"] ** 2 / denom * grid.dx ** 3
    N_ind = V_eff * (4.0 * np.pi * K_CENTERS ** 2 * DK) / (2.0 * np.pi) ** 3
    cnt = grid.cnt_h
    nsh = NK
    kid_ins = cache["kid_ins"]
    Lins = cache["Lins"]

    def shell_sum(w1):
        """bincount over k-shells on the pre-selected inshell modes."""
        return np.bincount(kid_ins, weights=w1, minlength=nsh)

    dconv_mean = cache["dconv_mean"]
    q_ins = np.ascontiguousarray(q.ravel()[grid.inshell_h])
    del q
    q2 = q_ins * q_ins
    P = {}
    for l in (0, 2, 4):
        P[l] = (2 * l + 1) * shell_sum(q_ins * Lins[l]) / cnt / I
    # Poisson white floor S/I: exact per-shell white-floor contribution for
    # every multipole (the discrete mu-sampling makes <L_l> != 0 on a shell)
    for l in (0, 2, 4):
        P[l] -= (2 * l + 1) * P_shot * cache["white_floor"][l]
    C = {}
    for (l, lp) in ((0, 0), (0, 2), (0, 4), (2, 2), (2, 4), (4, 4)):
        M = shell_sum(q2 * Lins[l] * Lins[lp])          # sum over modes = cnt*<q^2 L L'>
        # Gaussian field: <|F|^4> = 2<|F|^2>^2 -> factor 2; N_ind independent modes
        C[(l, lp)] = 2.0 * (2 * l + 1) * (2 * lp + 1) * M / (cnt * I ** 2 * N_ind)
    meta = {"alpha": float(alpha), "S": S, "I": I, "P_shot": float(P_shot),
            "deconv_mean": [float(v) for v in dconv_mean],
            "N_gal": int(pos_d.shape[0]), "N_rand": int(pos_r.shape[0])}
    return P, C, meta


# --------------------------------------------------------------------------
# per-bin Kaiser fit (linear in theta, exact covariance, delta-method sigma)
# --------------------------------------------------------------------------
COV_SHRINK = 0.3   # LOO-calibrated shrinkage of MC cov blocks (see fit_bin)


def fit_bin(P0, P2, P4, C, tables, cov_block=None):
    """GLS fit of (B2, BF, F2) to (P0, P2, P4); returns f_sigma8 +/- sigma.

    tables: exact-grid window-convolution design columns from conv_tables,
            {(l, j): (NK,)} for l in (0, 2, 4), j = 0, 1, 2 <-> (B2, BF, F2).
    C:      naive covariance dict {(l, lp): (NK,)} from measure_multipoles
            (used only when no MC block is given).
    cov_block: optional (3NK, 3NK) covariance of [P0; P2; P4] shells from the
            mock MC (run_cov) -- replaces the naive block-diagonal S.
            Order: [P0(0..NK-1); P2(NK..2NK-1); P4(2NK..3NK-1)].

    A P0+P2-only fit is rank-2 (both multipole rows are k-independent
    combinations of theta in the continuum limit) and cannot separate
    (B2, BF, F2); the P4 rows (Kaiser: only F2) supply the missing rank.
    """
    Cm = np.column_stack([np.concatenate([tables[(l, j)] for l in (0, 2, 4)])
                          for j in range(3)])
    d = np.concatenate([np.asarray(P0, float), np.asarray(P2, float),
                        np.asarray(P4, float)])
    if cov_block is not None:
        S = np.asarray(cov_block, float)
        # Ledoit-Wolf-style shrinkage toward the diagonal, rho = 0.3: with only
        # 30 mocks the raw 27-dim precision matrix is Wishart-noise dominated
        # (LOO whitening chi2/dof = 20.9).  rho = 0.3 was calibrated by
        # leave-one-out on the mocks themselves -> LOO chi2/dof = 1.01, i.e.
        # errors for INDEPENDENT data (synth / real) are then calibrated.
        # No extra Hartlap factor: the LOO test already absorbs it.
        S = (1.0 - COV_SHRINK) * S + COV_SHRINK * np.diag(np.diag(S))
    else:
        # NAIVE diagnostic covariance: independent shells, diagonal blocks
        # only (the measured cross-multipole C02/C04/C24 from the SAME
        # realization is CIRCULAR and would leak that realization's noise
        # into the weights).  MC cov blocks from run_cov carry the true
        # window correlations and replace S in production.
        S = np.zeros((3 * NK, 3 * NK))
        for i, k in enumerate(range(NK)):
            S[i, i] = C[(0, 0)][k]
            S[NK + i, NK + i] = C[(2, 2)][k]
            S[2 * NK + i, 2 * NK + i] = C[(4, 4)][k]
    Si = np.linalg.pinv(S)
    A = Cm.T @ Si @ Cm
    theta = np.linalg.solve(A, Cm.T @ Si @ d)
    cov = np.linalg.inv(A)
    r = d - Cm @ theta
    chi2 = float(r @ Si @ r)
    B2, BF, F2 = (float(v) for v in theta)
    if B2 > 0 and abs(BF) > 0:
        fs8 = BF / np.sqrt(B2)
        bs8 = np.sqrt(B2)
        # delta method: f = th2 * th1^{-1/2}
        a, b = 1.0 / np.sqrt(B2), -0.5 * BF * B2 ** -1.5
        var_f = a * a * cov[1, 1] + b * b * cov[0, 0] + 2 * a * b * cov[0, 1]
        sig_f = float(np.sqrt(max(var_f, 0.0)))
        var_b = 0.25 / B2 * cov[0, 0]
        sig_b = float(np.sqrt(max(var_b, 0.0)))
    else:
        fs8 = bs8 = sig_f = sig_b = float("nan")
    beta = BF / (2 * B2) if B2 > 0 else float("nan")
    return {"fs8": fs8, "sigma_fs8": sig_f, "bs8": bs8, "sigma_bs8": sig_b,
            "beta": beta, "chi2": chi2, "dof": 3 * NK - 3, "theta": theta.tolist(),
            "B2": B2, "BF": BF, "F2": F2}


# --------------------------------------------------------------------------
# catalog loading (BOSS DR12v5 LSS, astropy; gzip decompressed to disk first)
# --------------------------------------------------------------------------
def ensure_decompressed(path_gz):
    path = path_gz.with_suffix("")          # strip .gz
    if path.exists():
        return path
    import gzip
    t0 = time.time()
    print(f"  decompressing {path_gz.name} ...", flush=True)
    with gzip.open(path_gz, "rb") as fi, open(path, "wb") as fo:
        while True:
            chunk = fi.read(1 << 22)
            if not chunk:
                break
            fo.write(chunk)
    print(f"  done in {time.time()-t0:.0f}s -> {path.name}", flush=True)
    return path


def load_boss(path, is_random):
    from astropy.io import fits
    p = ensure_decompressed(path) if path.suffix == ".gz" else path
    with fits.open(p, memmap=True) as hdul:
        d = hdul[1].data
        ra = np.asarray(d["RA"], float)
        dec = np.asarray(d["DEC"], float)
        z = np.asarray(d["Z"], float)
        nz = np.asarray(d["NZ"], float)
        if not is_random:
            # data: total systematic weight (DR12v5 LSS catalog)
            w_ic = (np.asarray(d["WEIGHT_SYSTOT"], float) *
                    np.asarray(d["WEIGHT_CP"], float) * np.asarray(d["WEIGHT_NOZ"], float))
            if "ZWARNING" in getattr(d.columns, "names", []):
                # per-chunk catalogs: keep only good redshifts
                zw = np.asarray(d["ZWARNING"], int)
                keep = zw == 0
            else:
                # DR12v5 COMBINED catalog (CMASSLOWZTOT): already redshift-clean,
                # no ZWARNING column -> keep all
                keep = np.ones(z.size, bool)
        else:
            # randoms carry the imaging systematics through the mask -> unit weight
            w_ic = np.ones(z.size)
            keep = np.ones(z.size, bool)
        w_fkp = 1.0 / (1.0 + nz * P0_FKP)
    w = w_ic * w_fkp
    ra, dec, z, nz, w = ra[keep], dec[keep], z[keep], nz[keep], w[keep]
    # observer-frame cartesian (Mpc/h); observer at origin, x points at (RA=0,Dec=0)
    ra_r, dec_r = np.radians(ra), np.radians(dec)
    ch = chi_of_z(z)
    pos = np.column_stack([ch * np.cos(dec_r) * np.cos(ra_r),
                           ch * np.cos(dec_r) * np.sin(ra_r),
                           ch * np.sin(dec_r)])
    return {"pos": pos, "z": z, "w": w, "nz": nz, "ra": ra, "dec": dec}


# --------------------------------------------------------------------------
# mock-MC covariance blocks (produced by run_cov, consumed by data/synth fits)
# --------------------------------------------------------------------------
def load_cov_blocks(caps):
    """Per-(bin, cap) covariance blocks of [P0 shells; P2 shells] from run_cov.

    Returns (blocks, meta) where blocks maps (bin_index, cap_letter) -> (2NK, 2NK)
    array, or (None, None) if the npz for these caps does not exist.
    """
    tag = "".join(caps)
    p = RESULTS / f"fs8_cov_mocks_{tag}.npz"
    if not p.exists():
        print(f"  [cov] no MC blocks ({p.name}) -> naive per-shell C "
              f"(underestimates within-bin window correlation; run mode `cov` first)")
        return None, None
    z = np.load(p, allow_pickle=True)
    meta = json.loads(str(z["meta"]))
    caps_l = list(meta["caps"])
    blocks = {(int(b), caps_l[int(c)]): z["blocks"][i]
              for i, (b, c) in enumerate(zip(z["bins"], z["capids"]))}
    print(f"  [cov] loaded {z['blocks'].shape[0]} MC cov blocks "
          f"({meta['nm']} mocks, ngrid={meta['ngrid']}) from {p.name}")
    return blocks, meta


# --------------------------------------------------------------------------
# mode: data
# --------------------------------------------------------------------------
def run_data(ngrid, caps=("N", "S")):
    RESULTS.mkdir(parents=True, exist_ok=True)
    print("loading BOSS catalogs ...", flush=True)
    cats = {}
    for cap in caps:
        cats[("g", cap)] = load_boss(BOSS_FILES[f"galaxy_{cap}"], is_random=False)
        cats[("r", cap)] = load_boss(BOSS_FILES[f"random_{cap}"], is_random=True)
        gd, gr = cats[("g", cap)], cats[("r", cap)]
        print(f"  cap {cap}: {gd['z'].size} galaxies, {gr['z'].size} randoms", flush=True)
    # grid from data+randoms positions
    allpos = np.vstack([cats[("g", c)]["pos"] for c in caps] +
                       [cats[("r", c)]["pos"] for c in caps])
    print(f"setting up grid (ngrid={ngrid}) ...", flush=True)
    grid = Grid(allpos, ngrid)
    print(f"  L = {grid.L:.0f} Mpc/h, dx = {grid.dx:.2f}, k_Ny = {np.pi/grid.dx:.3f}", flush=True)
    # LOS per cap: centroid direction of randoms
    los = {}
    for cap in caps:
        cvec = cats[("r", cap)]["pos"].mean(axis=0)
        los[cap] = cvec / np.linalg.norm(cvec)
    # p(k) shape
    pshape = PSHAPE_FINE
    pshape_all = PSHAPE_FINE
    blocks, covmeta = load_cov_blocks(caps)
    mcache = {cap: measure_cache(grid, los[cap]) for cap in caps}
    ccache = {cap: conv_cache(grid, los[cap], pshape_all) for cap in caps}
    rows = []
    t0 = time.time()
    for j in range(N_BINS):
        z1, z2 = BIN_EDGES[j], BIN_EDGES[j + 1]
        dchi = float(chi_of_z(z2) - chi_of_z(z1))
        for cap in caps:
            gd, gr = cats[("g", cap)], cats[("r", cap)]
            md = (gd["z"] >= z1) & (gd["z"] < z2)
            mr = (gr["z"] >= z1) & (gr["z"] < z2)
            if md.sum() < 200 or mr.sum() < 5000:
                continue
            rcache = randoms_cache(grid, gr["pos"][mr], gr["w"][mr])
            P, C, meta = measure_multipoles(grid, gd["pos"][md], gd["w"][md],
                                            gr["pos"][mr], gr["w"][mr], los[cap],
                                            cache=mcache[cap], rcache=rcache)
            # exact-grid window tables: wf = alpha * (NGP weighted randoms field)
            cells = grid.cell_index(gr["pos"][mr])
            wfc = np.bincount(cells, weights=gr["w"][mr],
                              minlength=grid.N ** 3).astype(np.float32)
            w2c = np.bincount(cells, weights=gr["w"][mr] ** 2,
                              minlength=grid.N ** 3)
            tables = conv_tables(grid, meta["alpha"] * wfc, meta["I"], pshape_all,
                                 los[cap], A_floor=meta["alpha"] ** 2 * float(w2c.sum()),
                                 cache=ccache[cap])
            cb = blocks.get((j, cap)) if blocks else None
            fit = fit_bin(P[0], P[2], P[4], C, tables, cov_block=cb)
            zc = 0.5 * (z1 + z2)
            zbar = float(gd["z"][md].mean())
            row = {"cap": cap, "bin": j, "z_lo": z1, "z_hi": z2, "z_center": zc,
                   "z_eff": zbar, "dchi": dchi, **meta, **fit}
            rows.append(row)
        print(f"  bin {j+1}/{N_BINS} done ({time.time()-t0:.0f}s elapsed)", flush=True)
    # write CSV
    import csv
    out = RESULTS / "fs8_boss_bins.csv"
    keys = list(rows[0].keys())
    with open(out, "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=keys)
        wr.writeheader()
        for r in rows:
            wr.writerow(r)
    print(f"wrote {out} ({len(rows)} rows)", flush=True)
    return rows


# --------------------------------------------------------------------------
# mode: synth (Gaussian light cone on real BOSS geometry, oscillation injected)
# --------------------------------------------------------------------------
def real_ngal(caps):
    """Post-cut galaxy counts of the REAL BOSS catalogs, per cap.  Mocks must
    reproduce these (not a round number) so the Poisson shot noise inside the
    MC covariance equals the data measurement's.  Measured by loading the same
    catalogs through the same cuts as run_data: N = 876772, S = 340562."""
    return {cap: int(load_boss(BOSS_FILES[f"galaxy_{cap}"], is_random=False)["z"].size)
            for cap in caps}


def run_synth(ngrid, A_list, phi=0.7, seed=20261019, ngal=None, sigma8_0=0.8,
              caps=("N", "S")):
    """Gaussian-density light cone on the REAL BOSS geometry/mask with Kaiser RSD
    and an INJECTED SRE oscillation in f_sigma8(z).

    Positions are drawn from the REAL randoms (exact mask + n(z)); the density
    field has P(k) = s_ref^2 p(k) with s_ref = sigma8_0 D(z_ref)/D(0), z_ref = 0.4
    (light-cone growth variation inside the field is neglected -- flagged); RSD
    enters as an EXACT Kaiser SELECTION field per cap: galaxy contrast =
    0.5*delta + (f_sigma8_true(z)/s_ref) * g_cap with g_hat = mu'^2 delta_hat
    (LOS = cap centroid, per-galaxy f), NO particle displacement -- grid-native
    fields, so the NGP deconvolution of the measurement is exact for both.
    f_sigma8_true(z) = sigma8_0 U(z) (1 + A(Rs cos phi + Rc sin phi)).  NOTE: the
    mock is Gaussian and bias-free by construction; it validates the
    estimator/windows/covariance, NOT nonlinear-RSD systematics.
    """
    RESULTS.mkdir(parents=True, exist_ok=True)
    print("loading randoms for geometry ...", flush=True)
    rands = {cap: load_boss(BOSS_FILES[f"random_{cap}"], is_random=True) for cap in caps}
    allpos = np.vstack([rands[c]["pos"] for c in caps])
    grid = Grid(allpos, ngrid)
    print(f"  L = {grid.L:.0f}, dx = {grid.dx:.2f}", flush=True)
    origin = grid.center - grid.L / 2.0
    # reference amplitude at z_ref = 0.4 (field-level growth approximation)
    x_ref = -np.log(1.4)
    s_ref = sigma8_0 * float(BASE(x_ref)[0]) / D01
    def P_of_k(k):
        return s_ref ** 2 * np.interp(np.abs(k), _KK_P, _PK_P)
    rng = np.random.default_rng(seed)
    print("drawing Gaussian density + per-cap RSD selection fields ...", flush=True)
    Wk = np.fft.rfftn(rng.standard_normal((grid.N, grid.N, grid.N)).astype(np.float32))
    Pk_grid = P_of_k(grid.kmag).astype(np.float32)
    # Gaussian field convention (validated by direct-DFT: P_out == P_in):
    #   delta = irfftn(Wk * sqrt(P V / N^3)) * (N^3 / V)
    Vb = grid.L ** 3
    coef = np.sqrt(Pk_grid * Vb / grid.N ** 3).astype(np.float32)
    Wc = (Wk * coef.astype(np.complex64)).astype(np.complex128)
    del Wk, Pk_grid, coef
    if XFER_POWER:
        Wc *= xfer_corr(grid, XFER_POWER)
        print(f"  construction pre-compensation 1/W^{XFER_POWER:g}", flush=True)
    # LOS per cap = centroid of randoms (identical to the measurement).
    fx = 2 * np.pi * np.fft.fftfreq(grid.N, d=grid.dx).astype(np.float32)
    fz = 2 * np.pi * np.fft.rfftfreq(grid.N, d=grid.dx).astype(np.float32)
    K2 = (fx ** 2)[:, None, None] + (fx ** 2)[None, :, None] + (fz ** 2)[None, None, :]
    K2s = np.maximum(K2, 1e-30)
    del K2
    los = {}
    for cap in caps:
        cv = rands[cap]["pos"].mean(axis=0)
        los[cap] = cv / np.linalg.norm(cv)
    # Displacement-mode mock construction (literature standard, cf. Zel'dovich
    # mocks / PTchallenge): a Poisson pool drawn from the randoms is
    # DETERMINISTICALLY displaced by
    #   Psi   = b * IFT[i k_i/k^2 * delta_hat]            (Zel'dovich, b = 0.5)
    #   D_los = (fs8_true(z)/s_ref) * IFT[i (k.los)/k^2 * delta_hat]  (RSD)
    # A Poisson process under a deterministic map stays Poisson with intensity
    # n_bar(x)*(1 - b div Psi - dD/dlos) = n_bar*(1 + b delta + f mu'^2 delta)
    # -- the EXACT linear Kaiser contrast with NO acceptance clipping.  (The
    # previous pacc = clip((1+dg)/2) rejection sampling rectified the cell-level
    # negative tail and destroyed ~25% of the contrast power at dx ~ 11 Mpc.)
    # Psi/Gmu are evaluated at the pool positions by TRILINEAR interpolation of
    # the same band-limited fields the measurement deconvolves (NGP lookup
    # quantises the displacement to dx = 11 Mpc, which diffuses mass over a
    # cell and damps the high-k contrast; the interpolant's own prod sinc^2 is
    # folded into XFER_POWER).
    Psi = []
    for ax in range(3):
        kax = fx if ax < 2 else fz
        shp = [(grid.N, 1, 1), (1, grid.N, 1), (1, 1, fz.size)][ax]
        op = kax.reshape(shp) / K2s
        Psi.append((np.fft.irfftn(Wc * (1j * op), s=(grid.N, grid.N, grid.N),
                                  axes=(0, 1, 2)).astype(np.float32)
                    * (grid.N ** 3 / Vb) * B_MOCK))
        del op
    Gmu = {}
    for cap in caps:
        lv = los[cap]
        kp = (fx * lv[0])[:, None, None] + (fx * lv[1])[None, :, None] \
            + (fz * lv[2])[None, None, :]
        op = (kp / K2s).astype(np.float32)                # (k.los)/k^2, DC -> 0
        del kp
        Gmu[cap] = (np.fft.irfftn(Wc * (1j * op), s=(grid.N, grid.N, grid.N),
                                  axes=(0, 1, 2)).astype(np.float32)
                    * (grid.N ** 3 / Vb))
        del op
    del K2s, Wc
    # smooth n(z) per cap (median in fine z bins) and truth templates on sorted grid
    zt = np.linspace(0.10, 0.80, 14001)
    nz_t = {}
    for cap in caps:
        o = np.argsort(rands[cap]["z"])
        zs, nzs = rands[cap]["z"][o], rands[cap]["nz"][o]
        zb = np.linspace(0.10, 0.80, 701)
        ib = np.clip(np.digitize(zs, zb) - 1, 0, zb.size - 2)
        med = np.array([np.median(nzs[ib == q]) if np.any(ib == q) else np.nan
                        for q in range(zb.size - 1)])
        ok = np.isfinite(med)
        nz_t[cap] = np.interp(zt, 0.5 * (zb[:-1][ok] + zb[1:][ok]), med[ok])
    xt = -np.log1p(zt)
    RS_t, RC_t = solve_responses(np.array([K_DOC]), xt)
    RS_t, RC_t = RS_t[0], RC_t[0]
    U_t = BASE(xt)[1] / D01
    if ngal is None:
        ngal = real_ngal(caps)   # per-cap real counts -> exact data shot noise
    pshape = PSHAPE_FINE
    blocks, covmeta = load_cov_blocks(caps)
    # per-cap LOS constants and per-(bin,cap) randoms quantities are shared by
    # every A injection -> build them once
    mcache = {cap: measure_cache(grid, los[cap]) for cap in caps}
    ccache = {cap: conv_cache(grid, los[cap], pshape) for cap in caps}
    rcaches = {}
    for j in range(N_BINS):
        z1, z2 = BIN_EDGES[j], BIN_EDGES[j + 1]
        for cap in caps:
            r = rands[cap]
            mr = (r["z"] >= z1) & (r["z"] < z2)
            if mr.sum() >= 5000:
                rcaches[(j, cap)] = randoms_cache(grid, r["pos"][mr], r["w"][mr])
    rows_out = {}
    for A_inj in A_list:
        print(f"--- synth run A={A_inj} ---", flush=True)
        fs8_true_grid = sigma8_0 * U_t * (1.0 + A_inj * (np.cos(phi) * RS_t + np.sin(phi) * RC_t))
        gals = {}
        for cap in caps:
            r = rands[cap]
            # iid categorical draw WITH REPLACEMENT from the randoms (mask + n(z));
            # an independent pool keeps the estimator's Poisson shot formula S/I
            # exact (a Bernoulli thinning of the randoms would correlate data and
            # randoms).  searchsorted == multinomial marginal, but O(n log N).
            # Every pool galaxy is kept and displaced (no acceptance step).
            cum = np.cumsum(r["w"]) / r["w"].sum()
            idx = np.minimum(np.searchsorted(cum, rng.random(ngal[cap] if isinstance(ngal, dict) else ngal), side="right"),
                             r["z"].size - 1)
            pos, zg = r["pos"][idx], r["z"][idx]
            # Zel'dovich + RSD displacement; the RSD amplitude carries the
            # injected oscillation through fs8_true(z); fs8 = BF/sqrt(B2) is
            # bias-independent
            ci = grid.cell_index(pos)
            coords = ((pos - origin) / grid.dx).T
            dvec = np.column_stack([map_coordinates(Psi[0], coords, order=1,
                                                    mode="nearest"),
                                    map_coordinates(Psi[1], coords, order=1,
                                                    mode="nearest"),
                                    map_coordinates(Psi[2], coords, order=1,
                                                    mode="nearest")])
            dlos = (np.interp(zg, zt, fs8_true_grid) / s_ref) * map_coordinates(
                Gmu[cap], coords, order=1, mode="nearest")
            del ci
            pos = pos + dvec + np.outer(dlos, los[cap])
            zg = np.interp(np.sqrt((pos ** 2).sum(axis=1)), _CHI_G, _ZG_FINE)
            wfkp = 1.0 / (1.0 + np.interp(zg, zt, nz_t[cap]) * P0_FKP)
            gals[cap] = {"pos": pos, "z": zg, "w": wfkp}
            print(f"  cap {cap}: {zg.size} galaxies", flush=True)
        rows = []
        for j in range(N_BINS):
            z1, z2 = BIN_EDGES[j], BIN_EDGES[j + 1]
            dchi = float(chi_of_z(z2) - chi_of_z(z1))
            mt = (zt >= z1) & (zt < z2)
            fs8_true = float(fs8_true_grid[mt].mean()) if mt.any() else float("nan")
            for cap in caps:
                g, r = gals[cap], rands[cap]
                md = (g["z"] >= z1) & (g["z"] < z2)
                mr = (r["z"] >= z1) & (r["z"] < z2)
                if md.sum() < 200 or mr.sum() < 5000:
                    continue
                P, C, meta = measure_multipoles(grid, g["pos"][md], g["w"][md],
                                                r["pos"][mr], r["w"][mr], los[cap],
                                                cache=mcache[cap],
                                                rcache=rcaches.get((j, cap)))
                cells = grid.cell_index(r["pos"][mr])
                wfc = np.bincount(cells, weights=r["w"][mr],
                                  minlength=grid.N ** 3).astype(np.float32)
                w2c = np.bincount(cells, weights=r["w"][mr] ** 2,
                                  minlength=grid.N ** 3)
                tables = conv_tables(grid, meta["alpha"] * wfc, meta["I"], pshape,
                                     los[cap], A_floor=meta["alpha"] ** 2 * float(w2c.sum()),
                                     cache=ccache[cap])
                cb = blocks.get((j, cap)) if blocks else None
                fit = fit_bin(P[0], P[2], P[4], C, tables, cov_block=cb)
                rows.append({"cap": cap, "bin": j, "z_lo": z1, "z_hi": z2,
                             "z_center": 0.5 * (z1 + z2), "z_eff": float(g["z"][md].mean()),
                             "fs8_true": fs8_true, **meta, **fit})
        rows_out[A_inj] = rows
        import csv
        out = RESULTS / f"fs8_synth_A{A_inj}.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            wr.writeheader()
            for rr in rows:
                wr.writerow(rr)
        print(f"  wrote {out}", flush=True)
    return rows_out


# --------------------------------------------------------------------------
# mode: cov (mock-MC covariance blocks through the synth pipeline, A = 0)
# --------------------------------------------------------------------------
def run_cov(ngrid, nm=30, seed0=91001, ngal=None, sigma8_0=0.8, caps=("N", "S"),
            threads=3):
    """Empirical per-(bin, cap) covariance of [P0 shells; P2 shells] from nm
    zero-injection Gaussian light-cone realizations run through the IDENTICAL
    pipeline as run_synth (A=0): same geometry/mask (real randoms), same linear
    NGP selection, same Kaiser RSD, same FKP weights, same matched bins, same
    measure_multipoles.

    WHY: the radial top-hat of each bin correlates modes with |dk_par| <~
    2pi/dchi >> dk, so the measured shells are NOT independent and the naive
    per-shell C underestimates the errors.  Disjoint bins have ~zero
    cross-covariance (their masks do not overlap), so per-(bin, cap) blocks
    suffice for the block-diagonal GLS.

    The MC P(k) is EH98 linear at sigma8 = sigma8_0; the real universe's
    nonlinear boost at k>0.15 (+20-40%) is a second-order effect on (P+shot)^2
    (documented simplification).  Shot noise, FKP weights and windows enter
    exactly as in the data path.

    Saves results/fs8_cov_mocks_{caps}.npz: blocks (ncb,3NK,3NK), means, vecs
    (nm,ncb,3NK), per-realization fit diagnostics, meta.
    """
    RESULTS.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    print(f"run_cov: nm={nm} ngrid={ngrid} caps={caps} seed0={seed0}", flush=True)
    rands = {cap: load_boss(BOSS_FILES[f"random_{cap}"], is_random=True) for cap in caps}
    allpos = np.vstack([rands[c]["pos"] for c in caps])
    grid = Grid(allpos, ngrid)
    print(f"  L = {grid.L:.0f}, dx = {grid.dx:.2f}", flush=True)
    origin = grid.center - grid.L / 2.0
    x_ref = -np.log(1.4)
    s_ref = sigma8_0 * float(BASE(x_ref)[0]) / D01
    P_of_k = lambda k: s_ref ** 2 * np.interp(np.abs(k), _KK_P, _PK_P)
    Vb = grid.L ** 3
    Pk_grid = P_of_k(grid.kmag).astype(np.float32)
    coef = np.sqrt(Pk_grid * Vb / grid.N ** 3).astype(np.float32)
    fx = 2 * np.pi * np.fft.fftfreq(grid.N, d=grid.dx).astype(np.float32)
    fz = 2 * np.pi * np.fft.rfftfreq(grid.N, d=grid.dx).astype(np.float32)
    # smooth n(z) per cap and truth templates (same as run_synth)
    zt = np.linspace(0.10, 0.80, 14001)
    nz_t = {}
    for cap in caps:
        o = np.argsort(rands[cap]["z"])
        zs, nzs = rands[cap]["z"][o], rands[cap]["nz"][o]
        zb = np.linspace(0.10, 0.80, 701)
        ib = np.clip(np.digitize(zs, zb) - 1, 0, zb.size - 2)
        med = np.array([np.median(nzs[ib == q]) if np.any(ib == q) else np.nan
                        for q in range(zb.size - 1)])
        ok = np.isfinite(med)
        nz_t[cap] = np.interp(zt, 0.5 * (zb[:-1][ok] + zb[1:][ok]), med[ok])
    xt = -np.log1p(zt)
    RS_t, RC_t = solve_responses(np.array([K_DOC]), xt)
    RS_t, RC_t = RS_t[0], RC_t[0]
    U_t = BASE(xt)[1] / D01
    if ngal is None:
        ngal = real_ngal(caps)   # per-cap real counts -> exact data shot noise
    pshape = PSHAPE_FINE
    los = {}
    for cap in caps:
        cv = rands[cap]["pos"].mean(axis=0)
        los[cap] = cv / np.linalg.norm(cv)
    cumw = {cap: np.cumsum(rands[cap]["w"]) / rands[cap]["w"].sum() for cap in caps}
    # precompute randoms bin masks
    rmask = {}
    for cap in caps:
        zr = rands[cap]["z"]
        for j in range(N_BINS):
            z1, z2 = BIN_EDGES[j], BIN_EDGES[j + 1]
            mr = (zr >= z1) & (zr < z2)
            if mr.sum() >= 5000:
                rmask[(j, cap)] = mr
    ncb_list = sorted(rmask.keys())
    ncb = len(ncb_list)
    # exact-grid window rows: B_r per cap once; RAW rows per (bin, cap) with the
    # window = NGP weighted randoms field (NO alpha -- the alpha^2/I factor is
    # applied per realization from the measure_multipoles meta)
    fx = 2 * np.pi * np.fft.fftfreq(grid.N, d=grid.dx).astype(np.float32)
    fz = 2 * np.pi * np.fft.rfftfreq(grid.N, d=grid.dx).astype(np.float32)
    # per-cap conv cache (B_r + pre-gathered Legendre*deconv): built once and
    # reused by every (bin, cap) window row
    ccache = {cap: conv_cache(grid, los[cap], pshape) for cap in caps}
    raw_rows = {}
    for (j, cap) in ncb_list:
        mr = rmask[(j, cap)]
        cells = grid.cell_index(rands[cap]["pos"][mr])
        wfc = np.bincount(cells, weights=rands[cap]["w"][mr],
                          minlength=grid.N ** 3).astype(np.float32)
        w2c = float(np.bincount(cells, weights=rands[cap]["w"][mr] ** 2,
                                minlength=grid.N ** 3).sum())
        raw_rows[(j, cap)] = conv_tables_raw(grid, wfc, pshape, los[cap],
                                             A_floor=w2c, cache=ccache[cap])
    print(f"  {ncb} (bin,cap) cells; exact-grid window rows done ({time.time()-t0:.0f}s)",
          flush=True)
    # displacement operators: K2s = k^2 on the rfft half grid (DC guard 1e-30;
    # the operators i k_i/k^2 and i (k.los)/k^2 are zero there anyway).  Used
    # per realization to build the Zel'dovich Psi and per-cap RSD field Gmu --
    # same displacement-mode mocks as run_synth (no acceptance clipping).
    K2 = (fx ** 2)[:, None, None] + (fx ** 2)[None, :, None] + (fz ** 2)[None, None, :]
    K2s = np.maximum(K2, 1e-30)
    del K2

    # caches shared by ALL realizations: per-cap LOS constants, per-(bin,cap)
    # randoms grid/scalars (realization-independent)
    mcache = {cap: measure_cache(grid, los[cap]) for cap in caps}
    rcaches = {key: randoms_cache(grid, rands[key[1]]["pos"][rmask[key]],
                                  rands[key[1]]["w"][rmask[key]])
               for key in ncb_list}
    print(f"  measure caches built ({time.time()-t0:.0f}s)", flush=True)

    vecs = np.zeros((nm, ncb, 3 * NK), np.float32)
    alphas = np.zeros((nm, ncb))
    Ivals = np.zeros((nm, ncb))
    zeff = np.zeros((ncb,))
    for m in range(nm):
        rng = np.random.default_rng(seed0 + m)
        Wk = np.fft.rfftn(rng.standard_normal((grid.N,) * 3).astype(np.float32))
        Wc = (Wk * coef.astype(np.complex64)).astype(np.complex128)
        del Wk
        if XFER_POWER:
            Wc *= xfer_corr(grid, XFER_POWER)
        # displacement-mode mocks (A = 0 null), same scheme as run_synth: pool
        # from the randoms, then Zel'dovich + RSD displacement -- no acceptance
        # clipping, exact linear Kaiser contrast
        Psi = []
        for ax in range(3):
            kax = fx if ax < 2 else fz
            shp = [(grid.N, 1, 1), (1, grid.N, 1), (1, 1, fz.size)][ax]
            op = kax.reshape(shp) / K2s
            Psi.append((np.fft.irfftn(Wc * (1j * op), s=(grid.N, grid.N, grid.N),
                                      axes=(0, 1, 2)).astype(np.float32)
                        * (grid.N ** 3 / Vb) * B_MOCK))
            del op
        gals = {}
        for cap in caps:
            r = rands[cap]
            idx = np.minimum(np.searchsorted(cumw[cap], rng.random(ngal[cap] if isinstance(ngal, dict) else ngal), side="right"),
                             r["z"].size - 1)
            pos, zg = r["pos"][idx], r["z"][idx]
            lv = np.asarray(los[cap], float)
            kp = (fx * lv[0])[:, None, None] + (fx * lv[1])[None, :, None] \
                + (fz * lv[2])[None, None, :]
            op = (kp / K2s).astype(np.float32)
            del kp
            gmu = (np.fft.irfftn(Wc * (1j * op), s=(grid.N, grid.N, grid.N),
                                 axes=(0, 1, 2)).astype(np.float32)
                   * (grid.N ** 3 / Vb))
            del op
            coords = ((pos - origin) / grid.dx).T
            dvec = np.column_stack([map_coordinates(Psi[0], coords, order=1,
                                                    mode="nearest"),
                                    map_coordinates(Psi[1], coords, order=1,
                                                    mode="nearest"),
                                    map_coordinates(Psi[2], coords, order=1,
                                                    mode="nearest")])
            dlos = (sigma8_0 * np.interp(zg, zt, U_t) / s_ref) * map_coordinates(
                gmu, coords, order=1, mode="nearest")
            pos = pos + dvec + np.outer(dlos, los[cap])
            zg = np.interp(np.sqrt((pos ** 2).sum(axis=1)), _CHI_G, _ZG_FINE)
            wfkp = 1.0 / (1.0 + np.interp(zg, zt, nz_t[cap]) * P0_FKP)
            gals[cap] = {"pos": pos, "z": zg, "w": wfkp}
            del gmu
        del Wc, Psi
        def _cell(item):
            i, (j, cap) = item
            g, r = gals[cap], rands[cap]
            mr = rmask[(j, cap)]
            z1, z2 = BIN_EDGES[j], BIN_EDGES[j + 1]
            md = (g["z"] >= z1) & (g["z"] < z2)
            if md.sum() < 200:
                return
            P, C, meta = measure_multipoles(grid, g["pos"][md], g["w"][md],
                                            r["pos"][mr], r["w"][mr], los[cap],
                                            cache=mcache[cap], rcache=rcaches[(j, cap)])
            vecs[m, i, :NK] = P[0]
            vecs[m, i, NK:2 * NK] = P[2]
            vecs[m, i, 2 * NK:] = P[4]
            alphas[m, i] = meta["alpha"]
            Ivals[m, i] = meta["I"]
            if m == 0:
                zeff[i] = float(g["z"][md].mean())

        # (bin,cap) cells are independent -> measure them concurrently; the
        # per-call work is memory-bandwidth bound, so the speedup is sub-linear
        # (~2x at 4 threads) but the 512-grid job still drops from ~1 h to ~30 min
        with ThreadPoolExecutor(max_workers=threads) as ex:
            list(ex.map(_cell, list(enumerate(ncb_list))))
        print(f"  realization {m+1}/{nm} done ({time.time()-t0:.0f}s)", flush=True)

    blocks = np.zeros((ncb, 3 * NK, 3 * NK))
    means = vecs.mean(axis=0)
    for i in range(ncb):
        blocks[i] = np.cov(vecs[:, i, :].astype(np.float64), rowvar=False, ddof=1)
    fits_fs8 = np.full((nm, ncb), np.nan)
    fits_sig = np.full((nm, ncb), np.nan)
    fits_chi2 = np.full((nm, ncb), np.nan)
    z1z2 = {}
    for i, (j, cap) in enumerate(ncb_list):
        z1, z2 = BIN_EDGES[j], BIN_EDGES[j + 1]
        z1z2[i] = (z1, z2)
        for m in range(nm):
            t_m = {k: (alphas[m, i] ** 2 / Ivals[m, i]) * v
                   for k, v in raw_rows[(j, cap)].items()}
            fit = fit_bin(vecs[m, i, :NK].astype(np.float64),
                          vecs[m, i, NK:2 * NK].astype(np.float64),
                          vecs[m, i, 2 * NK:].astype(np.float64),
                          None, t_m, cov_block=blocks[i])
            fits_fs8[m, i] = fit["fs8"]
            fits_sig[m, i] = fit["sigma_fs8"]
            fits_chi2[m, i] = fit["chi2"] / fit["dof"]
    # null-distribution diagnostics (in-sample cov: slightly optimistic sigma)
    pull = (fits_fs8 - fits_fs8.mean(axis=0)) / fits_sig
    ok = np.isfinite(pull)
    print(f"  null fs8 pull: rms={np.sqrt(np.mean(pull[ok]**2)):.3f} "
          f"(expect ~1), n={ok.sum()}")
    print(f"  per-cell fit chi2/dof median = {np.median(fits_chi2):.2f}")
    # BIAS vs truth (the mean-subtracted pull above CANNOT see a common bias --
    # this is the check that would have caught the grid-z Legendre bug):
    # injected truth is f_sigma8(z) = sigma8_0 * U(z) (A = 0 null).
    truth = sigma8_0 * np.interp(zeff, zt, U_t)
    okc = np.isfinite(fits_fs8).any(axis=0)
    bias_sig = np.full(ncb, np.nan)
    frac = np.full(ncb, np.nan)
    for i in range(ncb):
        col = fits_fs8[:, i]
        good = np.isfinite(col)
        if good.sum() < 3 or not okc[i]:
            continue
        bias_sig[i] = (col[good].mean() - truth[i]) / (col[good].std(ddof=1)
                                                       / np.sqrt(good.sum()))
        frac[i] = col[good].mean() / truth[i] - 1.0
    print(f"  null fs8 BIAS vs truth: median {np.nanmedian(frac) * 100:+.2f}% "
          f"(max {np.nanmax(np.abs(frac)) * 100:.2f}%), "
          f"median t = {np.nanmedian(bias_sig):+.2f}, "
          f"max|t| = {np.nanmax(np.abs(bias_sig)):.2f}")
    meta = json.dumps({"nm": nm, "ngrid": ngrid, "seed0": seed0,
                       "ngal": ({k: int(v) for k, v in ngal.items()}
                                if isinstance(ngal, dict) else int(ngal)),
                       "b_mock": float(B_MOCK),
                       "sigma8_0": sigma8_0, "s_ref": s_ref, "caps": list(caps),
                       "NK": int(NK), "k_edges": K_EDGES.tolist()})
    out = RESULTS / f"fs8_cov_mocks_{''.join(caps)}.npz"
    np.savez_compressed(out, blocks=blocks, means=means, vecs=vecs,
                        bins=np.array([j for j, _ in ncb_list]),
                        capids=np.array([caps.index(c) for _, c in ncb_list]),
                        zeff=zeff, alphas=alphas, Ivals=Ivals,
                        fits_fs8=fits_fs8, fits_sig=fits_sig,
                        fits_chi2=fits_chi2, meta=meta)
    print(f"wrote {out}", flush=True)
    return out


# --------------------------------------------------------------------------
# mode: mock (PATCHY/EZ-style ASCII: ra dec z [cols...]; column sniffing)
# --------------------------------------------------------------------------
def run_mock(mock_path, random_cap="N", ngrid=256, extra_weight_col=None):
    RESULTS.mkdir(parents=True, exist_ok=True)
    ra, dec, z, wextra = _read_ascii_xyz(mock_path)
    w_ic = np.ones(z.size) if wextra is None else wextra
    ch = chi_of_z(z)
    rr, dd = np.radians(ra), np.radians(dec)
    pos = np.column_stack([ch * np.cos(dd) * np.cos(rr),
                           ch * np.cos(dd) * np.sin(rr), ch * np.sin(dd)])
    rand = load_boss(BOSS_FILES[f"random_{random_cap}"], is_random=True)
    nz_of_z = lambda zz: np.interp(zz, _ZG_FINE,
                                   np.interp(_ZG_FINE, rand["z"], rand["nz"]))
    w = w_ic / (1.0 + nz_of_z(z) * P0_FKP)
    allpos = np.vstack([pos, rand["pos"]])
    grid = Grid(allpos, ngrid)
    cv = rand["pos"].mean(axis=0)
    los = cv / np.linalg.norm(cv)
    pshape = PSHAPE_FINE
    ccache = conv_cache(grid, los, pshape)
    rows = []
    for j in range(N_BINS):
        z1, z2 = BIN_EDGES[j], BIN_EDGES[j + 1]
        md = (z >= z1) & (z < z2)
        mr = (rand["z"] >= z1) & (rand["z"] < z2)
        if md.sum() < 200 or mr.sum() < 5000:
            continue
        P, C, meta = measure_multipoles(grid, pos[md], w[md],
                                        rand["pos"][mr], rand["w"][mr], los)
        cells = grid.cell_index(rand["pos"][mr])
        wfc = np.bincount(cells, weights=rand["w"][mr],
                          minlength=grid.N ** 3).astype(np.float32)
        w2c = np.bincount(cells, weights=rand["w"][mr] ** 2,
                          minlength=grid.N ** 3)
        tables = conv_tables(grid, meta["alpha"] * wfc, meta["I"], pshape,
                             los, A_floor=meta["alpha"] ** 2 * float(w2c.sum()),
                             cache=ccache)
        fit = fit_bin(P[0], P[2], P[4], C, tables)
        rows.append({"cap": random_cap, "bin": j, "z_lo": z1, "z_hi": z2,
                     "z_center": 0.5 * (z1 + z2), "z_eff": float(z[md].mean()),
                     **meta, **fit})
    return rows


def _read_ascii_xyz(path):
    cols = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            cols.append([float(v) for v in line.split()])
            if len(cols) >= 200000:
                break
    arr = np.array(cols)
    return arr[:, 0], arr[:, 1], arr[:, 2], None


# --------------------------------------------------------------------------
def main():
    global XFER_POWER, B_MOCK
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["data", "synth", "mock", "cov"])
    ap.add_argument("--ngrid", type=int, default=None)
    ap.add_argument("--A", type=float, nargs="*", default=[0.0, 0.509])
    ap.add_argument("--ngal", type=int, default=None,
                    help="per-cap pool size (default: real catalog counts)")
    ap.add_argument("--nm", type=int, default=30)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--seed0", type=int, default=91001)
    ap.add_argument("--xfer", type=float, default=XFER_POWER,
                    help="mock-construction pre-compensation exponent (0 = off)")
    ap.add_argument("--bmock", type=float, default=B_MOCK,
                    help="mock linear bias (Zel'dovich Psi amplitude)")
    ap.add_argument("--mock", type=str, default=None)
    ap.add_argument("--cap", type=str, default="NS")
    args = ap.parse_args()
    XFER_POWER = float(args.xfer)
    B_MOCK = float(args.bmock)
    caps = tuple(args.cap.replace(",", ""))
    t0 = time.time()
    if args.mode == "data":
        run_data(args.ngrid or 512, caps=caps)
    elif args.mode == "synth":
        run_synth(args.ngrid or 256, args.A, ngal=args.ngal, caps=caps)
    elif args.mode == "cov":
        run_cov(args.ngrid or 256, nm=args.nm, seed0=args.seed0,
                ngal=args.ngal, caps=caps, threads=args.threads)
    else:
        rows = run_mock(args.mock, caps[0], args.ngrid or 256)
        print(json.dumps(rows[:2], indent=1))
    print(f"total {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
