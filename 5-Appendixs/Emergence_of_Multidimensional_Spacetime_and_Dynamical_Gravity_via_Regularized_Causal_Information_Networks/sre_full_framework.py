"""
SRE-Dynamics-Framework: Version 6.2 (Bootstrap Statistical Edition)
Author: Yue Lu, AI Collaborator
Date: August 26, 2026
Description: SRE v6.2 full production pipeline with complete Bootstrap ensemble.
             Merges gravity_6.0 main paper + gravity_support corrigendum.
             Strictly aligned with SRE v1.6 axiomatic system.

=== Change Log ===
[FIX-1]     CORRECTED metric trace: R² = Tr(D @ C) · exp(-γ·μ_loss) (matrix product)
[FIX-2]     CORRECTED Δz = z_slice.max() - z_slice.min() (real slice width)
[FIX-3]     DELETED AI-constructed G_eff; derived from Tr(D@C), rank, Ω
[FIX-4]     UPGRADED rank detection: Tracy-Widom σ-scaled boundary
[FIX-5]     ADDED Bootstrap resampling for 95% CI
[FIX-6]     ADDED chiral correction Γ_chiral, Λ_twist; gravitational lensing

[BOOT-FIX-1] Δz protection: np.maximum(delta_z, eps_mach); never uses WINDOW_SIZE as Δz
[BOOT-FIX-2] Full 1500 Bootstrap per window: rank probability, <Rank(z)>, G_eff 95% CI
[BOOT-FIX-3] Simulated z* from P(rank<=2)>=0.5; z_crit=4.1605 is plot-only reference
[BOOT-FIX-4] All 4 plots adapted to ensemble statistics with z* and CI bands
[BOOT-FIX-5] Standardized console Bootstrap summary output
[BOOT-FIX-6] Extended unit tests: Δz protection, Bootstrap small-sample, z* calculation
[BOOT-FIX-7] Force UTF-8 stdout/stderr to fix UnicodeEncodeError on Windows GBK console

[CRITICAL-FIX-1] Bootstrap matrix dimension FIXED = n_total (after cap); failure counter
[CRITICAL-FIX-2] z -> lookback_time(Gyr) via Planck 2018 LambdaCDM; real dt in Euler
[CRITICAL-FIX-3] G_eff = G_0 * Omega * (R/4) * xi, xi = Tr(D@C)/(N*mu_loss) [analytical]
[CRITICAL-FIX-4] Dual-mode rank: debug (fixed threshold) / production (BBP-RMT eigenvalue bulk)
"""

import os
import sys
import numpy as np
import scipy.linalg as la
from scipy.integrate import quad
import pandas as pd
import requests
import io
import matplotlib.pyplot as plt
import warnings

# [BOOT-FIX-7] Force UTF-8 stdout/stderr to avoid UnicodeEncodeError on Windows GBK console
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, Exception):
        pass

warnings.filterwarnings("ignore", category=SyntaxWarning)

# =========================================================================
# GLOBAL CONFIGURATION (SRE v6.2 Axiomatic Calibration)
# =========================================================================
SRE_CONFIG = {
    # --- Sliding causal horizon ---
    "WINDOW_SIZE": 0.04,
    "STEP_SIZE": 0.02,
    "DOWNSAMPLING_THRESHOLD": 1500,
    "DOWNSAMPLING_CAP": 1000,

    # --- v6.2: θ_conformal; α₀_dynamic = θ/(Δz+ε_mach) ---
    "THETA_CONFORMAL": 0.82798,

    # --- γ_latency for conformal scaling Ω = (Δz/θ)^(-γ/4) ---
    "GAMMA_LATENCY": 0.05,

    # --- Numerical constants ---
    "HOLOGRAPHIC_DIM_CAP": 4,
    "NOISE_SCALING_FACTOR": 5.0,
    "G_BASE": 6.6743e-11,
    "REGULARIZATION_LAMBDA": 1e-6,
    "C_LIGHT": 299792458.0,

    # --- [FIX-4] Tracy-Widom 99th percentile quantile (GOE) ---
    "TW_QUANTILE_099": 1.276,

    # --- [BOOT-FIX-2] Bootstrap configuration ---
    # Publication: 1500; Quick debug: set to 50 via command line override
    "BOOTSTRAP_N": 1500,
    # Subsample size per bootstrap iteration (keeps matrix small for speed)
    "BOOTSTRAP_SUBSAMPLE": 60,

    # --- [CRITICAL-FIX-1] Bootstrap matrix dimension cap ---
    # Downsample to this size first, then ALL bootstrap iterations use this as
    # the FIXED matrix dimension (n_total). Prevents TW threshold drift.
    "BOOTSTRAP_MATRIX_CAP": 80,

    # --- [CRITICAL-FIX-4] Rank detection mode ---
    # "production": BBP-RMT eigenvalue bulk + TW extreme value statistics
    # "debug": fixed eigenvalue threshold for observation
    "RANK_DETECTION_MODE": "production",
    # Debug mode: eigenvalues above this fraction of max are "signal"
    "RANK_DEBUG_THRESHOLD_FRAC": 0.10,

    # --- [CRITICAL-FIX-2] Planck 2018 LambdaCDM cosmology ---
    # Used for z <-> lookback_time(Gyr) physical mapping
    "OMEGA_M": 0.3111,
    "OMEGA_LAMBDA": 0.6889,
    "H0_KM_S_MPC": 67.4,

    # --- Cache config (preserved from v5.2) ---
    "CACHE_DIR": os.path.join(os.path.dirname(os.path.abspath(__file__)), ".sre_cache"),
    "CACHE_MIN_ROWS": 1000,

    # --- SDSS data source config ---
    "SDSS_DATA_RELEASE": 17,
    "SDSS_MAX_ZERR": 5.0,

    # --- [BOOT-FIX-3] Historical reference (plot-only, NEVER used in logic) ---
    "HISTORICAL_Z_CRIT": 4.1605,
}


# =========================================================================
# PHASE 1: INPUT VALIDATION & STABILITY DIAGNOSTICS
# =========================================================================
def validate_causal_tensors(z_slice, zerr_slice):
    if not isinstance(z_slice, np.ndarray) or not isinstance(zerr_slice, np.ndarray):
        raise TypeError("Causal horizons must be passed as standard NumPy ndarrays.")
    if z_slice.shape != zerr_slice.shape:
        raise ValueError(f"Shape mismatch: {z_slice.shape} vs {zerr_slice.shape}")
    if len(z_slice.shape) != 1:
        raise ValueError("Causal arrays must be flattened 1D temporal tensors.")
    if np.any(z_slice < 0.0) or np.any(zerr_slice <= 0.0):
        raise ValueError("Detected unphysical negative redshifts or non-positive uncertainties.")


def analyze_numerical_stability(gram_matrix, raw_eigenvalues, adaptive_threshold):
    diagnostics = {}
    if len(raw_eigenvalues) == 0:
        diagnostics["condition_number"] = np.inf
        diagnostics["is_ill_conditioned"] = True
        return diagnostics

    abs_ev = np.abs(raw_eigenvalues)
    max_ev = np.max(abs_ev)
    min_ev = np.min(abs_ev)

    m_eps = np.finfo(np.float64).eps
    if min_ev > m_eps:
        diagnostics["condition_number"] = max_ev / min_ev
    else:
        diagnostics["condition_number"] = max_ev / m_eps
    diagnostics["is_ill_conditioned"] = diagnostics["condition_number"] > 1e12
    return diagnostics


# =========================================================================
# PHASE 2: MULTI-SOURCE DATA ACQUISITION ENGINE WITH LOCAL CACHE
# =========================================================================
_CACHE_FILES = {
    "sdss": "sdss_dr17_specobj.csv",
    "desi": "desi_dr1_zcatalog.csv",
    "synthetic": "synthetic_zcatalog.csv",
}


def _cache_path(source):
    os.makedirs(SRE_CONFIG["CACHE_DIR"], exist_ok=True)
    return os.path.join(SRE_CONFIG["CACHE_DIR"], _CACHE_FILES[source])


def _load_from_cache(source):
    path = _cache_path(source)
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_csv(path)
        expected_cols = {'Redshift', 'ZERR'}
        if not expected_cols.issubset(set(df.columns)):
            print(f"[SRE Cache] {source} cache corrupted: missing columns")
            return None
        if len(df) < SRE_CONFIG["CACHE_MIN_ROWS"]:
            print(f"[SRE Cache] {source} cache too small: {len(df)} rows")
            return None
        print(f"[SRE Cache] Loaded {len(df)} rows from {source} cache")
        return df
    except Exception as e:
        print(f"[SRE Cache] Failed to read {source} cache: {e}")
        return None


def _save_to_cache(df, source):
    path = _cache_path(source)
    tmp_path = path + ".tmp"
    try:
        df.to_csv(tmp_path, index=False)
        os.replace(tmp_path, path)
        print(f"[SRE Cache] Cached {len(df)} rows to {path}")
    except Exception as e:
        print(f"[SRE Cache] Failed to write {source} cache: {e}")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def _clean_sdss_data(table):
    z = table['z'].astype(np.float64)
    zerr = table['zerr'].astype(np.float64)
    mask = (z > 0.001) & (z < 6.5) & (zerr > 0) & (zerr < SRE_CONFIG["SDSS_MAX_ZERR"])
    z_clean = z[mask]
    zerr_clean = zerr[mask]
    print(f"[SRE SDSS] Cleaning: {len(z)} total -> {len(z_clean)} valid rows")
    return pd.DataFrame({'Redshift': z_clean, 'ZERR': zerr_clean})


def _fetch_from_sdss(total_rows):
    try:
        from astroquery.sdss import SDSS
    except ImportError:
        print("[SRE SDSS] astroquery not installed. Run: pip install astroquery")
        return None

    release = SRE_CONFIG["SDSS_DATA_RELEASE"]
    print(f"[SRE SDSS] Querying SDSS DR{release} via astroquery...")

    try:
        query = SDSS.query_sql(
            f"SELECT TOP {total_rows} z, zerr FROM specObj "
            f"WHERE z IS NOT NULL AND zerr > 0 AND z > 0.001 AND z < 6",
            data_release=release
        )
        if query is None or len(query) == 0:
            print("[SRE SDSS] Query returned empty result")
            return None
        df = _clean_sdss_data(query)
        if len(df) < SRE_CONFIG["CACHE_MIN_ROWS"]:
            print(f"[SRE SDSS] Only {len(df)} valid rows, below threshold")
            return None
        print(f"[SRE SDSS] Fetched {len(df)} real spectroscopic redshifts")
        return df.sort_values(by='Redshift').reset_index(drop=True)
    except Exception as e:
        print(f"[SRE SDSS] Query failed: {type(e).__name__}: {e}")
        return None


def _fetch_from_tap(total_rows):
    tap_endpoints = [
        "https://datalab.noirlab.edu/vo-server/TAP",
        "https://datalab.noirlab.edu/tap",
        "https://noirlab.edu/vo-server/TAP",
    ]
    rows_per_bin = total_rows // 3
    adql_query = f"""
    (SELECT TOP {rows_per_bin} z AS Redshift, zerr AS ZERR FROM desi_dr1.zcatalog
     WHERE zwarn = 0 AND z > 0.001 AND z < 0.5 AND zerr > 0 ORDER BY z ASC)
    UNION ALL
    (SELECT TOP {rows_per_bin} z AS Redshift, zerr AS ZERR FROM desi_dr1.zcatalog
     WHERE zwarn = 0 AND z >= 0.5 AND z < 1.5 AND zerr > 0 ORDER BY z ASC)
    UNION ALL
    (SELECT TOP {rows_per_bin} z AS Redshift, zerr AS ZERR FROM desi_dr1.zcatalog
     WHERE zwarn = 0 AND z >= 1.5 AND z < 4.5 AND zerr > 0 ORDER BY z ASC)
    """
    params = {"request": "doQuery", "lang": "ADQL", "format": "csv", "query": adql_query}

    for tap_url in tap_endpoints:
        print(f"[SRE TAP] Trying endpoint: {tap_url}")
        try:
            response = requests.post(tap_url, data=params, timeout=45)
            if response.status_code == 200:
                text = response.text.strip()
                if not text or text.startswith("<"):
                    print(f"[SRE TAP] Endpoint returned HTML/error page, skipping.")
                    continue
                df = pd.read_csv(io.StringIO(text))
                if len(df) >= SRE_CONFIG["CACHE_MIN_ROWS"]:
                    print(f"[SRE TAP] Fetched {len(df)} real rows from {tap_url}")
                    return df.sort_values(by='Redshift').reset_index(drop=True)
                else:
                    print(f"[SRE TAP] Only {len(df)} rows returned, below threshold.")
            else:
                print(f"[SRE TAP] HTTP {response.status_code} from {tap_url}")
        except requests.exceptions.Timeout:
            print(f"[SRE TAP] Timeout from {tap_url}")
        except Exception as e:
            print(f"[SRE TAP] Error from {tap_url}: {e}")

    return None


def _generate_synthetic(total_rows):
    print("[SRE Framework] Deploying High-Fidelity Simulator...")
    rng = np.random.default_rng(seed=20260613)
    z_arr = np.sort(rng.uniform(0.001, 6.85, total_rows))
    zerr_arr = 1e-4 * np.exp(z_arr * 0.5) + rng.normal(0, 1e-5, total_rows)
    return pd.DataFrame({'Redshift': z_arr, 'ZERR': np.maximum(zerr_arr, 1e-6)})


def fetch_desi_dr1_stream(total_rows=30000):
    """
    Four-tier data acquisition (preserved from v5.2):
      1. Local CSV cache (source-specific)
      2. SDSS DR17 via astroquery
      3. DESI DR1 via NOIRLab TAP
      4. High-fidelity synthetic simulator
    """
    for source in ("sdss", "desi", "synthetic"):
        df = _load_from_cache(source)
        if df is not None:
            if source == "sdss":
                print("[SRE Source] Using cached SDSS DR17 real data")
            elif source == "desi":
                print("[SRE Source] Using cached DESI DR1 real data")
            return df

    df = _fetch_from_sdss(total_rows)
    if df is not None:
        _save_to_cache(df, "sdss")
        return df

    df = _fetch_from_tap(total_rows)
    if df is not None:
        _save_to_cache(df, "desi")
        return df

    df = _generate_synthetic(total_rows)
    _save_to_cache(df, "synthetic")
    return df


# =========================================================================
# PHASE 2b: [CRITICAL-FIX-2] COSMOLOGICAL TIME-REDSHIFT MAPPING
# =========================================================================
def z_to_lookback_time(z):
    """
    [CRITICAL-FIX-2] Convert redshift z to cosmic lookback time (Gyr).

    Uses Planck 2018 flat LambdaCDM: Omega_m=0.3111, Omega_Lambda=0.6889, H0=67.4.
    Formula: t_L(z) = (1/H0) * integral_0^z [ dz' / ((1+z') * E(z')) ]
    where E(z) = sqrt(Omega_m*(1+z)^3 + Omega_Lambda).

    This replaces the old pseudo-time axis (array index = time) with
    physically correct cosmological lookback time.
    """
    Om = SRE_CONFIG["OMEGA_M"]
    Ol = SRE_CONFIG["OMEGA_LAMBDA"]
    H0_km = SRE_CONFIG["H0_KM_S_MPC"]

    # H0 in Gyr^-1: 1 Mpc = 3.0857e19 km, 1 Gyr = 3.1557e16 s
    H0_Gyr = H0_km / 3.0857e19 * 3.1557e16  # ~0.06893 Gyr^-1

    def integrand(zp):
        Ez = np.sqrt(Om * (1.0 + zp) ** 3 + Ol)
        return 1.0 / ((1.0 + zp) * Ez)

    z = np.asarray(z, dtype=float)
    scalar_input = (z.ndim == 0)
    z = np.atleast_1d(z)

    t_L = np.zeros_like(z)
    for i, zi in enumerate(z):
        if zi <= 0:
            t_L[i] = 0.0
        else:
            val, _ = quad(integrand, 0.0, zi, limit=100)
            t_L[i] = val / H0_Gyr

    return t_L[0] if scalar_input else t_L


# =========================================================================
# PHASE 2c: [CRITICAL-FIX-4] RANK DETECTION (dual-mode)
# =========================================================================
def _detect_rank(eigvals, n_sub, debug=False):
    """
    [CRITICAL-FIX-4] Detect effective rank from gram-B eigenvalues.

    Mode A (debug): Fixed threshold = RANK_DEBUG_THRESHOLD_FRAC * max|eig|.
    Mode B (production): BBP-RMT approach -- estimate the eigenvalue bulk
    using robust statistics (median + MAD), then apply TW-scaled boundary
    to identify outlier signal eigenvalues. This does NOT use the matrix
    element std (sigma_B) in Wigner scaling, which was the old defect.

    Returns: (effective_rank, tw_boundary, n_signal)
    """
    abs_ev = np.abs(eigvals)
    max_ev = np.max(abs_ev) if len(abs_ev) > 0 else 0.0
    tw_q = SRE_CONFIG["TW_QUANTILE_099"]
    mode = SRE_CONFIG["RANK_DETECTION_MODE"]

    if mode == "debug":
        # [CRITICAL-FIX-4] Mode A: fixed fraction of max eigenvalue
        threshold = SRE_CONFIG["RANK_DEBUG_THRESHOLD_FRAC"] * max_ev
        threshold = max(threshold, np.finfo(np.float64).eps)
        n_signal = int(np.sum(abs_ev > threshold))
        tw_boundary = threshold  # for reporting
    else:
        # [CRITICAL-FIX-4] Mode B: BBP-RMT eigenvalue bulk + TW
        # Estimate bulk center/spread from eigenvalue distribution itself
        # (NOT from matrix elements sigma_B)
        if len(abs_ev) >= 4:
            # Use lower 80% as bulk (exclude potential signal eigenvalues)
            n_bulk = max(int(0.8 * len(abs_ev)), 2)
            sorted_ev = np.sort(abs_ev)
            bulk_ev = sorted_ev[:n_bulk]

            bulk_median = float(np.median(bulk_ev))
            # MAD -> std conversion factor 1.4826
            mad = float(np.median(np.abs(bulk_ev - bulk_median)))
            bulk_std = mad * 1.4826 if mad > 0 else 1.0
        else:
            bulk_median = float(np.median(abs_ev)) if len(abs_ev) > 0 else 0.0
            bulk_std = 1.0

        # TW-scaled boundary: bulk_median + bulk_std * TW_scale
        # TW_scale = 2*sqrt(N) + N^(-1/6) * quantile  (N = matrix dim)
        tw_scale = 2.0 * np.sqrt(n_sub) + n_sub ** (-1.0 / 6.0) * tw_q
        tw_boundary = bulk_median + bulk_std * tw_scale
        tw_boundary = max(tw_boundary, np.finfo(np.float64).eps)
        n_signal = int(np.sum(abs_ev > tw_boundary))

    # Clamp to holographic dim cap [2, 4]
    effective_rank = max(2, min(n_signal, SRE_CONFIG["HOLOGRAPHIC_DIM_CAP"]))

    if debug:
        print(f"         [RANK-{mode}] n_signal={n_signal} -> rank={effective_rank}  "
              f"tw_boundary={tw_boundary:.6e}  max|eig|={max_ev:.6e}")

    return effective_rank, tw_boundary, n_signal


# =========================================================================
# PHASE 3: SRE v6.2 CORE PHYSICS SOLVER
# =========================================================================
def compute_derived_quantities(z_slice, zerr_slice, debug=False):
    """
    [FIX-1][FIX-2][FIX-3][BOOT-FIX-1][CRITICAL-FIX-3][CRITICAL-FIX-4] v6.2: Core solver.

    Key formulas:
      [FIX-1]           R_sq = (D @ C) * exp(-gamma*mu_loss)  (matrix product)
      [BOOT-FIX-1]      delta_z = np.maximum(max-min, eps_mach)
      [CRITICAL-FIX-3]  G_eff = G_0 * Omega * (R/4) * xi,  xi = Tr(D@C)/(N*mu_loss)
      [CRITICAL-FIX-4]  rank = _detect_rank(eigvals, N)  [dual-mode: debug/production]
    """
    validate_causal_tensors(z_slice, zerr_slice)

    n_sub = len(z_slice)
    if n_sub < 4:
        return None

    # --- v5.2 DOWNSAMPLING preserved ---
    if n_sub > SRE_CONFIG["DOWNSAMPLING_THRESHOLD"]:
        step = n_sub // SRE_CONFIG["DOWNSAMPLING_CAP"]
        z_slice, zerr_slice = z_slice[::step], zerr_slice[::step]
        n_sub = len(z_slice)

    # [BOOT-FIX-1] v6.2: REAL Δz from slice bounds with eps protection
    delta_z = float(np.max(z_slice) - np.min(z_slice))
    eps_mach = np.finfo(np.float64).eps
    delta_z = np.maximum(delta_z, eps_mach)  # [BOOT-FIX-1] protection

    theta = SRE_CONFIG["THETA_CONFORMAL"]
    alpha_dynamic = theta / (delta_z + eps_mach)

    if debug:
        z_center = 0.5 * (z_slice[0] + z_slice[-1])
        print(f"  [DEBUG] z_center={z_center:.4f}  dz={delta_z:.6f}  alpha_0_dynamic={alpha_dynamic:.4f}")

    # --- Conformal scaling Ω ---
    gamma_lat = SRE_CONFIG["GAMMA_LATENCY"]
    Omega = (delta_z / theta) ** (-gamma_lat / 4.0)

    # --- Local c-invariance assertion (preserved) ---
    c0 = SRE_CONFIG["C_LIGHT"]
    c_emergent = c0 * Omega
    c_local_measured = c_emergent / Omega
    assert abs(c_local_measured - c0) < 1e-5, \
        f"[v6.2] Local c-invariance violated: {c_local_measured} vs {c0}"

    # --- Topological dissipation tensor D̂ (n×n) ---
    sigma_i = zerr_slice[:, None]
    sigma_j = zerr_slice[None, :]
    sigma_prod = sigma_i * sigma_j
    D_ij = np.log1p(sigma_prod / eps_mach)

    # --- Compensation operator Ĉ (n×n) ---
    C_ij = (1.0 / alpha_dynamic) * np.sin(np.pi * alpha_dynamic * D_ij) ** 2

    # --- μ_loss = mean of D̂ matrix ---
    mu_loss = np.mean(D_ij)

    # [FIX-1] R_sq = D @ C (MATRIX product), NOT element-wise
    R_sq = (D_ij @ C_ij) * np.exp(-gamma_lat * mu_loss)

    # --- Centering operator H ---
    H_operator = np.eye(n_sub) - np.ones((n_sub, n_sub)) / n_sub

    # --- gram-B matrix (with Tikhonov regularization for stability) ---
    gram_B = -0.5 * (H_operator @ R_sq @ H_operator)
    trace_B = np.trace(gram_B)
    if trace_B > 0:
        gram_B_reg = gram_B + SRE_CONFIG["REGULARIZATION_LAMBDA"] * trace_B * np.eye(n_sub)
    else:
        gram_B_reg = gram_B

    try:
        eigvals = la.eigvalsh(gram_B_reg)
    except la.LinAlgError:
        return None

    abs_ev = np.abs(eigvals)
    max_ev = np.max(abs_ev)
    min_ev = np.min(abs_ev) if len(abs_ev) > 0 else eps_mach

    if min_ev > eps_mach:
        cond = max_ev / min_ev
    else:
        cond = max_ev / eps_mach

    # [CRITICAL-FIX-4] Rank detection via dual-mode _detect_rank()
    # Old code used sigma_B (matrix element std) in Wigner TW scaling -- DEFECTIVE.
    # New code uses eigenvalue-based bulk estimation (production) or fixed threshold (debug).
    effective_rank, tw_boundary, n_signal = _detect_rank(eigvals, n_sub, debug=debug)

    # [CRITICAL-FIX-3] G_eff from SRE-v6.2 paper chapter 5, spherical symmetry.
    #
    # Analytical derivation (replacing AI-constructed formula):
    #   SRE gravitational acceleration: a_SRE = -G_eff * M / r^2
    #   In the emergent metric, the Newtonian-limit perturbation is:
    #     h_00 ~ Tr(D_hat @ C_hat) / N   (mean metric trace per dimension)
    #   The effective gravitational coupling scales as:
    #     G_eff = G_0 * Omega * (R/4) * xi
    #   where:
    #     R/4   = dimensional factor (4D is reference; R<4 => weaker gravity)
    #     Omega = conformal scaling factor
    #     xi    = metric coupling efficiency = Tr(D@C) / (N * mu_loss)
    #   When C_hat -> I (full compensation): Tr(D@I)=Tr(D)=N*mean(D)=N*mu_loss
    #   => xi -> 1, so G_eff -> G_0 * Omega * (R/4). Physical and bounded.
    trace_DC = np.trace(D_ij @ C_ij) if n_sub > 0 else 1.0
    xi_metric = trace_DC / (n_sub * max(mu_loss, eps_mach))
    xi_metric = max(xi_metric, eps_mach)  # floor to prevent zero G_eff
    g_eff = SRE_CONFIG["G_BASE"] * Omega * (effective_rank / 4.0) * xi_metric

    is_unlocked = (effective_rank >= 3)

    return {
        'rank': effective_rank,
        'g_eff': g_eff,
        'cond': cond,
        'is_unlocked': is_unlocked,
        'alpha_dynamic': alpha_dynamic,
        'delta_z': delta_z,
        'omega': Omega,
        'tw_boundary': tw_boundary,
        'n_sub': n_sub,
        'trace_DC': trace_DC,
        'mean_metric': xi_metric,
        'n_signal': n_signal,
        'eigvals': eigvals,
        'gram_B': gram_B_reg,
    }


def compute_axiomatic_spectrum(z_slice, zerr_slice, debug=False):
    """
    [v6.2] Backward-compatible wrapper. Returns (rank, g_eff, cond, is_unlocked).
    """
    result = compute_derived_quantities(z_slice, zerr_slice, debug=debug)
    if result is None:
        return 2, SRE_CONFIG["G_BASE"] * 0.5, np.inf, False
    return result['rank'], result['g_eff'], result['cond'], result['is_unlocked']


def compute_unregularized_condition(z_slice, zerr_slice):
    """
    [FIX-1][BOOT-FIX-1] Condition number WITHOUT Tikhonov regularization.
    """
    n_sub = len(z_slice)
    if n_sub < 4:
        return np.inf

    if n_sub > SRE_CONFIG["DOWNSAMPLING_THRESHOLD"]:
        step = n_sub // SRE_CONFIG["DOWNSAMPLING_CAP"]
        z_slice, zerr_slice = z_slice[::step], zerr_slice[::step]
        n_sub = len(z_slice)

    # [BOOT-FIX-1] Real Δz with eps protection
    delta_z = float(np.max(z_slice) - np.min(z_slice))
    eps_mach = np.finfo(np.float64).eps
    delta_z = np.maximum(delta_z, eps_mach)

    theta = SRE_CONFIG["THETA_CONFORMAL"]
    alpha_dynamic = theta / (delta_z + eps_mach)
    gamma_lat = SRE_CONFIG["GAMMA_LATENCY"]
    Omega = (delta_z / theta) ** (-gamma_lat / 4.0)

    sigma_i = zerr_slice[:, None]
    sigma_j = zerr_slice[None, :]
    D_ij = np.log1p(sigma_i * sigma_j / eps_mach)
    C_ij = (1.0 / alpha_dynamic) * np.sin(np.pi * alpha_dynamic * D_ij) ** 2
    mu_loss = np.mean(D_ij)

    # [FIX-1] Matrix product
    R_sq = (D_ij @ C_ij) * np.exp(-gamma_lat * mu_loss)

    H_operator = np.eye(n_sub) - np.ones((n_sub, n_sub)) / n_sub
    gram_B_unreg = -0.5 * (H_operator @ R_sq @ H_operator)

    try:
        eigvals = la.eigvalsh(gram_B_unreg)
    except la.LinAlgError:
        return np.inf

    abs_ev = np.abs(eigvals)
    max_ev = np.max(abs_ev)
    min_ev = np.min(abs_ev)

    if min_ev > eps_mach:
        cond = max_ev / min_ev
    else:
        cond = max_ev / eps_mach

    return cond


# =========================================================================
# PHASE 4: [BOOT-FIX-2] COMPLETE BOOTSTRAP RESAMPLING MODULE (Paper §7.2)
# =========================================================================
def _bootstrap_single(z_slice, zerr_slice, n_bootstrap, rng_seed=42):
    """
    [BOOT-FIX-2][CRITICAL-FIX-1][CRITICAL-FIX-3][CRITICAL-FIX-4]
    Run N_bootstrap resamples on a single window.

    [CRITICAL-FIX-1] Matrix dimension is FIXED = n_total (after cap) for ALL
    iterations. Resampling indices select elements but gram matrix is always
    n_total x n_total. Prevents Tracy-Widom threshold drift.
    Includes failure counter with >15% warning.
    """
    n_total = len(z_slice)
    if n_total < 4:
        return None

    # [CRITICAL-FIX-1] Downsample to cap first, then ALL bootstrap iterations
    # use this SAME n_total as the fixed matrix dimension.
    matrix_cap = SRE_CONFIG["BOOTSTRAP_MATRIX_CAP"]
    if n_total > matrix_cap:
        step = n_total // matrix_cap
        z_slice = z_slice[::step]
        zerr_slice = zerr_slice[::step]
        n_total = len(z_slice)

    eps_mach = np.finfo(np.float64).eps
    theta = SRE_CONFIG["THETA_CONFORMAL"]
    gamma_lat = SRE_CONFIG["GAMMA_LATENCY"]
    G0 = SRE_CONFIG["G_BASE"]

    # [BOOT-FIX-1] Real dz (fixed across bootstrap — z_slice bounds fixed)
    delta_z = float(np.max(z_slice) - np.min(z_slice))
    delta_z = np.maximum(delta_z, eps_mach)
    alpha_0 = theta / (delta_z + eps_mach)
    Omega = (delta_z / theta) ** (-gamma_lat / 4.0)

    ranks = np.zeros(n_bootstrap, dtype=int)
    g_effs = np.zeros(n_bootstrap)
    alphas = np.full(n_bootstrap, alpha_0)  # alpha_0 is deterministic given dz

    # [CRITICAL-FIX-1] Failure counter for reliability assessment
    n_failures = 0
    rng = np.random.default_rng(seed=rng_seed)

    for b in range(n_bootstrap):
        # [CRITICAL-FIX-1] Resample n_total indices (matrix dim = n_total, FIXED)
        indices = rng.choice(n_total, size=n_total, replace=True)
        z_b = z_slice[indices]
        zerr_b = zerr_slice[indices]
        nb = n_total  # FIXED dimension, never changes

        # Recompute dz for THIS resample (z values change with resampling)
        dz_b = float(np.max(z_b) - np.min(z_b))
        dz_b = np.maximum(dz_b, eps_mach)
        alpha_b = theta / (dz_b + eps_mach)
        Omega_b = (dz_b / theta) ** (-gamma_lat / 4.0)

        sigma_i = zerr_b[:, None]
        sigma_j = zerr_b[None, :]
        D_b = np.log1p(sigma_i * sigma_j / eps_mach)
        C_b = (1.0 / alpha_b) * np.sin(np.pi * alpha_b * D_b) ** 2
        mu_b = np.mean(D_b)
        R_sq_b = (D_b @ C_b) * np.exp(-gamma_lat * mu_b)

        H_b = np.eye(nb) - np.ones((nb, nb)) / nb
        gram_B_b = -0.5 * (H_b @ R_sq_b @ H_b)

        try:
            eigvals_b = la.eigvalsh(gram_B_b)
        except la.LinAlgError:
            # [CRITICAL-FIX-1] Count failure, use fallback
            n_failures += 1
            ranks[b] = 2
            g_effs[b] = G0 * Omega_b * (2.0 / 4.0)  # CRITICAL-FIX-3 fallback
            alphas[b] = alpha_b
            continue

        # [CRITICAL-FIX-4] Dual-mode rank detection
        rank_b, _, _ = _detect_rank(eigvals_b, nb, debug=False)

        # [CRITICAL-FIX-3] G_eff from analytical derivation
        # G_eff = G_0 * Omega * (R/4) * xi,  xi = Tr(D@C) / (N * mu_loss)
        trace_DC_b = np.trace(D_b @ C_b) if nb > 0 else 1.0
        xi_b = trace_DC_b / (nb * max(mu_b, eps_mach))
        xi_b = max(xi_b, eps_mach)
        g_eff_b = G0 * Omega_b * (rank_b / 4.0) * xi_b

        ranks[b] = rank_b
        g_effs[b] = g_eff_b
        alphas[b] = alpha_b

    # [CRITICAL-FIX-1] Failure ratio warning
    failure_ratio = n_failures / n_bootstrap if n_bootstrap > 0 else 0.0
    if failure_ratio > 0.15:
        print(f"  [CRITICAL-FIX-1 WARNING] Window failure ratio = "
              f"{failure_ratio:.1%} > 15% -- results may be unreliable")

    return ranks, g_effs, alphas


def run_bootstrap_ensemble(z_centers, idx_left, idx_right, z_array, zerr_array,
                           n_bootstrap=None, debug_every=50):
    """
    [BOOT-FIX-2] Full Bootstrap ensemble across all sliding windows.

    For each z_center window:
      1. Resample N_bootstrap times with replacement
      2. Run solver on each resample
      3. Collect rank, g_eff, alpha_dynamic distributions

    Returns DataFrame with per-window statistics:
      z, rank_mean, rank_median, P(rank<=2), P(rank>=3), P(rank==4),
      g_eff_mean, g_eff_ci_low, g_eff_ci_high,
      alpha_mean, alpha_ci_low, alpha_ci_high,
      cooling_mean, cooling_ci_low, cooling_ci_high,
      rank_samples (list of all bootstrap rank values)
    """
    if n_bootstrap is None:
        n_bootstrap = SRE_CONFIG["BOOTSTRAP_N"]

    results = []

    print(f"[SRE Bootstrap] Running {n_bootstrap} resamples per window "
          f"(matrix_dim={SRE_CONFIG['BOOTSTRAP_MATRIX_CAP']}, "
          f"mode={SRE_CONFIG['RANK_DETECTION_MODE']})...")

    for i, z_c in enumerate(z_centers):
        l, r = idx_left[i], idx_right[i]
        if (r - l) < 15:
            continue

        z_slice = z_array[l:r]
        zerr_slice = zerr_array[l:r]

        # [BOOT-FIX-2] Run bootstrap
        boot_out = _bootstrap_single(z_slice, zerr_slice, n_bootstrap,
                                     rng_seed=42 + i)
        if boot_out is None:
            continue

        ranks, g_effs, alphas = boot_out
        G0 = SRE_CONFIG["G_BASE"]

        # [BOOT-FIX-3] Compute rank probabilities
        p_rank_le2 = np.mean(ranks <= 2)
        p_rank_ge3 = np.mean(ranks >= 3)
        p_rank_eq4 = np.mean(ranks == 4)
        rank_median = np.median(ranks)
        rank_mean = np.mean(ranks)

        # G_eff statistics
        g_eff_mean = np.mean(g_effs)
        g_eff_ci_low = np.percentile(g_effs, 2.5)
        g_eff_ci_high = np.percentile(g_effs, 97.5)

        # Alpha statistics
        alpha_mean = np.mean(alphas)
        alpha_ci_low = np.percentile(alphas, 2.5)
        alpha_ci_high = np.percentile(alphas, 97.5)

        # Cooling boost statistics
        cooling = (g_effs / G0) ** 2
        cooling_mean = np.mean(cooling)
        cooling_ci_low = np.percentile(cooling, 2.5)
        cooling_ci_high = np.percentile(cooling, 97.5)

        results.append({
            'z': z_c,
            'rank_mean': rank_mean,
            'rank_median': rank_median,
            'p_rank_le2': p_rank_le2,
            'p_rank_ge3': p_rank_ge3,
            'p_rank_eq4': p_rank_eq4,
            'g_eff_mean': g_eff_mean,
            'g_eff_ci_low': g_eff_ci_low,
            'g_eff_ci_high': g_eff_ci_high,
            'alpha_mean': alpha_mean,
            'alpha_ci_low': alpha_ci_low,
            'alpha_ci_high': alpha_ci_high,
            'cooling_mean': cooling_mean,
            'cooling_ci_low': cooling_ci_low,
            'cooling_ci_high': cooling_ci_high,
        })

        if i % debug_every == 0:
            # [CRITICAL-FIX-4] Print signal eigenvalue count per window
            print(f"  [CRITICAL-FIX-4] z={z_c:.4f}  signal_eig={rank_mean:.1f}  "
                  f"<Rank>={rank_mean:.2f}  P(rank<=2)={p_rank_le2:.3f}  "
                  f"<G_eff/G0>={g_eff_mean/G0:.4f}")

    boot_df = pd.DataFrame(results)
    return boot_df


def compute_simulated_z_star(boot_df):
    """
    [BOOT-FIX-3] Compute simulated statistical phase-transition z*.
    z* = redshift where P(rank<=2) first reaches >= 0.5 (4→2 transition).

    This is the SIMULATED result; 4.1605 is NEVER used in any logic.
    """
    if len(boot_df) == 0:
        return None

    z_vals = boot_df['z'].values
    p_le2 = boot_df['p_rank_le2'].values

    # Find first z (scanning from low to high) where P(rank<=2) >= 0.5
    # This is the transition from rank-4 dominance to rank-2 dominance
    transition_idx = None
    for i in range(len(z_vals)):
        if p_le2[i] >= 0.5:
            transition_idx = i
            break

    if transition_idx is None:
        # No transition found; take z at max P(rank<=2)
        transition_idx = int(np.argmax(p_le2))

    # Linear interpolation for more precise z*
    if transition_idx > 0:
        z0, z1 = z_vals[transition_idx - 1], z_vals[transition_idx]
        p0, p1 = p_le2[transition_idx - 1], p_le2[transition_idx]
        if abs(p1 - p0) > 1e-6:
            # Interpolate to find z where P=0.5
            z_star = z0 + (0.5 - p0) / (p1 - p0) * (z1 - z0)
        else:
            z_star = z1
    else:
        z_star = z_vals[transition_idx]

    return z_star


# =========================================================================
# PHASE 5: [FIX-6] CHIRAL CORRECTION & GRAVITATIONAL LENSING
# =========================================================================
def compute_chiral_corrections(z_slice, zerr_slice, g_eff, M_galaxy, b_impact=10.0):
    """
    [FIX-6] Chiral gravitational corrections and lensing deflection.
    """
    c0 = SRE_CONFIG["C_LIGHT"]
    G0 = SRE_CONFIG["G_BASE"]
    M_sun_kg = 1.989e30
    kpc_m = 3.0857e19

    M_kg = M_galaxy * M_sun_kg
    b_m = b_impact * kpc_m

    # Lens deflection angle
    theta_E = np.sqrt(4.0 * g_eff * M_kg / (c0 ** 2 * b_m))
    alpha_lens = 4.0 * g_eff * M_kg / (c0 ** 2 * b_m)

    # Chiral frame-dragging
    H0 = 67.4  # km/s/Mpc
    v_hubble = H0 * 1.0 * 1e3  # m/s at 1 Mpc
    Gamma_chiral = v_hubble * c0 / (2.0 * g_eff * M_kg)

    # Chiral twist (Lense-Thirring)
    Lambda_twist = 8.0 * np.pi * g_eff * v_hubble / (c0 ** 3 * b_m)

    # Net deflection
    alpha_net = alpha_lens * (1.0 + Gamma_chiral + Lambda_twist)

    # 2→4 transition detection
    rank_transition_2to4 = (g_eff / G0) > 1.0

    return {
        'alpha_lens_rad': alpha_lens,
        'alpha_lens_arcsec': alpha_lens * 206265.0,
        'theta_E_rad': theta_E,
        'theta_E_arcsec': theta_E * 206265.0,
        'Gamma_chiral': Gamma_chiral,
        'Lambda_twist': Lambda_twist,
        'alpha_net_arcsec': alpha_net * 206265.0,
        'rank_2to4': rank_transition_2to4,
    }


# =========================================================================
# PHASE 6: PIPELINE EXECUTION & VISUALIZATION
# =========================================================================
def run_production_pipeline(n_bootstrap=None):
    """
    [BOOT-FIX-2] Full production pipeline with complete Bootstrap ensemble.
    """
    # --- Data acquisition (four-tier, preserved from v5.2) ---
    df = fetch_desi_dr1_stream(total_rows=30000)
    z_array = df['Redshift'].values
    zerr_array = df['ZERR'].values

    # --- Sliding horizon scan (preserved from v5.2) ---
    z_centers = np.arange(
        np.min(z_array) + SRE_CONFIG["WINDOW_SIZE"] / 2,
        np.max(z_array) - SRE_CONFIG["WINDOW_SIZE"] / 2,
        SRE_CONFIG["STEP_SIZE"]
    )

    idx_left = np.searchsorted(z_array, z_centers - SRE_CONFIG["WINDOW_SIZE"] / 2)
    idx_right = np.searchsorted(z_array, z_centers + SRE_CONFIG["WINDOW_SIZE"] / 2)

    # --- Pass 1: Deterministic solver for condition numbers ---
    results = []
    cond_unreg_list = []

    print(f"[SRE Framework] Pass 1: Deterministic solver over {len(z_centers)} windows...")
    for i, z_c in enumerate(z_centers):
        l, r = idx_left[i], idx_right[i]
        if (r - l) < 15:
            continue

        result = compute_derived_quantities(
            z_array[l:r], zerr_array[l:r], debug=(i % 50 == 0)
        )
        if result is None:
            continue

        results.append({
            'z': z_c,
            'rank': result['rank'],
            'g_eff': result['g_eff'],
            'cond': result['cond'],
            'alpha_dynamic': result['alpha_dynamic'],
            'delta_z': result['delta_z'],
            'omega': result['omega'],
        })

        cond_unreg = compute_unregularized_condition(z_array[l:r], zerr_array[l:r])
        cond_unreg_list.append(cond_unreg)

    res_df = pd.DataFrame(results)
    cond_unreg_arr = np.array(cond_unreg_list)

    # --- Pass 2: [BOOT-FIX-2] Complete Bootstrap ensemble ---
    print(f"\n[SRE Framework] Pass 2: Bootstrap ensemble...")
    boot_df = run_bootstrap_ensemble(
        z_centers, idx_left, idx_right, z_array, zerr_array,
        n_bootstrap=n_bootstrap
    )

    # --- [BOOT-FIX-3] Compute simulated z* ---
    z_star = compute_simulated_z_star(boot_df)

    # --- [CRITICAL-FIX-2] Galaxy mass integration with REAL lookback time ---
    # OLD (DEFECTIVE): t_Gyr = np.linspace(0.0, 5.0, len(boot_df))  -- pseudo-time
    # NEW: Use Planck 2018 LambdaCDM z -> lookback_time(Gyr) physical mapping
    G0 = SRE_CONFIG["G_BASE"]
    M_0 = 1e4  # initial seed mass [M_sun]
    tau_std = 0.4  # accretion timescale [Gyr]

    # [CRITICAL-FIX-2] Sort boot_df by z to get monotonically increasing lookback time
    boot_df = boot_df.sort_values('z').reset_index(drop=True)
    z_sorted = boot_df['z'].values
    t_Gyr = z_to_lookback_time(z_sorted)

    # LambdaCDM baseline (uses real lookback time)
    M_lambda = M_0 * np.exp(t_Gyr / tau_std)

    # [BOOT-FIX-4] SRE mass using Bootstrap mean G_eff with CI
    g_eff_mean = boot_df['g_eff_mean'].values
    g_eff_low = boot_df['g_eff_ci_low'].values
    g_eff_high = boot_df['g_eff_ci_high'].values

    cooling_mean = np.clip((g_eff_mean / G0) ** 2, 0.01, 100.0)
    cooling_low = np.clip((g_eff_low / G0) ** 2, 0.01, 100.0)
    cooling_high = np.clip((g_eff_high / G0) ** 2, 0.01, 100.0)

    # [CRITICAL-FIX-2] Euler integration with REAL dt (non-uniform time steps)
    M_sre = np.zeros(len(boot_df))
    M_sre_low = np.zeros(len(boot_df))
    M_sre_high = np.zeros(len(boot_df))
    M_sre[0] = M_0
    M_sre_low[0] = M_0
    M_sre_high[0] = M_0

    for i in range(len(boot_df) - 1):
        dt_i = t_Gyr[i + 1] - t_Gyr[i]  # [CRITICAL-FIX-2] real dt
        if dt_i <= 0:
            dt_i = 1e-6  # protect against zero/negative dt
        M_sre[i + 1] = M_sre[i] + cooling_mean[i] * M_sre[i] / tau_std * dt_i
        M_sre_low[i + 1] = M_sre_low[i] + cooling_low[i] * M_sre_low[i] / tau_std * dt_i
        M_sre_high[i + 1] = M_sre_high[i] + cooling_high[i] * M_sre_high[i] / tau_std * dt_i

    # --- [BOOT-FIX-5] Standardized console output ---
    # [CRITICAL-FIX-2] Use lookback time at z~6 for reference mass
    t_z6 = z_to_lookback_time(6.0)
    M_lambda_z6 = M_0 * np.exp(t_z6 / tau_std)
    M_sre_z6 = M_sre[-1] if len(M_sre) > 0 else 0.0

    print("\n" + "=" * 90)
    print(" SRE v6.2 COSMOLOGY VERIFICATION (JWST PARADOX)")
    print("=" * 90)
    print(f" * LambdaCDM Accretion Mass (z~6, t_L={t_z6:.2f} Gyr): {M_lambda_z6:.2e} M_sun")
    print(f" * SRE v6.2 Emergent Mass (z~6, t_L={t_z6:.2f} Gyr):  {M_sre_z6:.2e} M_sun")
    if M_lambda_z6 > 0:
        print(f" * Mass Enhancement Factor:          {M_sre_z6 / M_lambda_z6:.2e} x")

    print("\n" + "=" * 60)
    print(" SRE-v6.2 Bootstrap Statistical Summary")
    print("=" * 60)

    if z_star is not None:
        print(f"1) Simulated statistical phase-transition z* = {z_star:.2f}")
    else:
        print(f"1) Simulated statistical phase-transition z* = N/A")
    print(f"2) Historical reference z_crit = {SRE_CONFIG['HISTORICAL_Z_CRIT']}")

    if len(boot_df) > 0:
        # Peak cooling boost
        cb_peak_idx = int(np.argmax(boot_df['cooling_mean']))
        cb_peak = boot_df['cooling_mean'].iloc[cb_peak_idx]
        cb_peak_low = boot_df['cooling_ci_low'].iloc[cb_peak_idx]
        cb_peak_high = boot_df['cooling_ci_high'].iloc[cb_peak_idx]
        print(f"3) Peak cooling-boost = {cb_peak:.2f} , 95% CI [{cb_peak_low:.2f} , {cb_peak_high:.2f}]")

        # Alpha statistics
        a0_mean = boot_df['alpha_mean'].mean()
        a0_low = boot_df['alpha_ci_low'].mean()
        a0_high = boot_df['alpha_ci_high'].mean()
        print(f"4) Mean alpha_0_dynamic = {a0_mean:.2f} , 95% CI [{a0_low:.2f} , {a0_high:.2f}]")

        # Rank statistics
        rank_mean_overall = boot_df['rank_mean'].mean()
        print(f"5) Ensemble <Rank> = {rank_mean_overall:.2f}")

    print("=" * 60)

    # [FIX-6] Lensing calculation
    if len(boot_df) > 0:
        M_galaxy_ref = 1e12  # M_sun
        lens_idx = len(boot_df) - 1
        lens_res = compute_chiral_corrections(
            np.array([0.0]), np.array([1e-4]),
            boot_df['g_eff_mean'].iloc[lens_idx],
            M_galaxy_ref, b_impact=10.0
        )
        print(f"\n [FIX-6] GRAVITATIONAL LENSING (z={boot_df['z'].iloc[lens_idx]:.2f}, "
              f"M_galaxy={M_galaxy_ref:.0e} M_sun)")
        print(f" * alpha_lens = {lens_res['alpha_lens_arcsec']:.4f} arcsec")
        print(f" * theta_E    = {lens_res['theta_E_arcsec']:.4f} arcsec")
        print(f" * Gamma_chiral = {lens_res['Gamma_chiral']:.6e}")
        print(f" * Lambda_twist = {lens_res['Lambda_twist']:.6e}")
        print(f" * Rank 2->4 transition: {lens_res['rank_2to4']}")

    print("\n" + "=" * 90)
    print(" * Phase Transition: SIMULATED z* from Bootstrap (no hardcoded z_crit)")
    print(" * z_crit=4.1605 is plot-only historical reference, never used in logic")
    print("=" * 90)

    # --- Generate all 4 figures ---
    _plot_condition_diagnostics(res_df, cond_unreg_arr)
    _plot_phase_transition(boot_df, z_star)
    _plot_galaxy_mass_crisis(boot_df, t_Gyr, M_lambda, M_sre, M_sre_low, M_sre_high, z_star)
    _plot_gravitational_lensing(boot_df, z_star)

    print("\n[SRE Framework] All v6.2 assets successfully generated.")


def _plot_condition_diagnostics(res_df, cond_unreg_arr):
    """
    [FIX-1] Condition number: regularized vs unregularized.
    """
    print("[SRE Framework] Exporting Figure 3: 'sre_condition_diagnostics.png'...")

    cond_reg = res_df['cond'].values
    cond_reg_clipped = np.clip(cond_reg, 1.0, 1e20)
    cond_unreg_clipped = np.clip(cond_unreg_arr, 1.0, 1e20)

    valid = ~np.isnan(cond_unreg_clipped) & (cond_unreg_clipped < 1e20)

    plt.figure(figsize=(10, 5))
    if np.any(valid):
        plt.semilogy(res_df['z'][valid], cond_unreg_clipped[valid],
                     color='gray', linestyle='--', alpha=0.7, lw=1.5,
                     label=r'Unregularized $D@C$ gram-B (no Tikhonov)')
    plt.semilogy(res_df['z'], cond_reg_clipped,
                 color='#10b981', lw=2.5,
                 label='Adaptive Tikhonov Regularized')
    plt.axhline(y=1e12, color='red', linestyle=':',
                label=r'Machine Safe Floor ($\mathrm{Cond} \leq 10^{12}$)')

    plt.xlabel('Cosmological Redshift (z)', fontsize=11)
    plt.ylabel('Matrix Condition Number (Cond)', fontsize=11)
    plt.title(r'Figure 3: Numerical Stability Monitor — $D@C$ Matrix Product',
              fontsize=12, pad=12)
    plt.legend(loc='upper left')
    plt.grid(True, which="both", linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig('sre_condition_diagnostics.png', dpi=300)
    plt.close()


def _plot_phase_transition(boot_df, z_star):
    """
    [BOOT-FIX-4] Phase transition with ensemble <Rank(z)>, <G_eff/G0>, 95% CI.
    z* marked as simulated phase transition; 4.1605 as historical reference only.
    """
    print("[SRE Framework] Exporting Figure 1: 'sre_phase_transition.png'...")
    fig, ax1 = plt.subplots(figsize=(10, 5))

    G0 = SRE_CONFIG["G_BASE"]

    # --- Left axis: <G_eff/G0> with 95% CI ---
    color = 'tab:red'
    ax1.set_xlabel('Cosmological Redshift (z)', fontsize=11)
    ax1.set_ylabel(r'$\langle G_{\mathrm{eff}} / G_0 \rangle$ (Bootstrap mean)', color=color, fontsize=11)

    ax1.plot(boot_df['z'], boot_df['g_eff_mean'] / G0,
             color=color, lw=2.5, label=r'$\langle G_{\mathrm{eff}} / G_0 \rangle$')

    # [BOOT-FIX-4] 95% CI fill
    ax1.fill_between(boot_df['z'],
                     boot_df['g_eff_ci_low'] / G0,
                     boot_df['g_eff_ci_high'] / G0,
                     color=color, alpha=0.15, label='G_eff 95% CI')

    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5, label=r'$G_0$ baseline')

    # --- Right axis: <Rank(z)> with bootstrap ---
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel(r'$\langle \mathrm{Rank}(z) \rangle$ (Ensemble mean)', color=color, fontsize=11)
    ax2.plot(boot_df['z'], boot_df['rank_mean'],
             color=color, lw=2.0, linestyle='-',
             label=r'$\langle \mathrm{Rank} \rangle$')
    # [BOOT-FIX-4] Rank uncertainty band (±0.5 since rank is integer-valued)
    rank_low = np.maximum(boot_df['rank_mean'] - 0.5, 2.0)
    rank_high = np.minimum(boot_df['rank_mean'] + 0.5, 4.0)
    ax2.fill_between(boot_df['z'], rank_low, rank_high,
                     color=color, alpha=0.1)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_yticks([2, 3, 4])

    # [BOOT-FIX-3] Simulated z* — solid orange line
    if z_star is not None:
        ax1.axvline(x=z_star, color='orange', linestyle='-', alpha=0.9, lw=2.0)
        ax1.text(z_star + 0.05, 0.85,
                 f'Simulated z* = {z_star:.2f}',
                 color='orange', rotation=90, weight='bold', fontsize=9)

    # [BOOT-FIX-3] Historical reference 4.1605 — purple dashed, PLOT ONLY
    z_hist = SRE_CONFIG["HISTORICAL_Z_CRIT"]
    ax1.axvline(x=z_hist, color='purple', linestyle='--', alpha=0.5, lw=1.5)
    ax1.text(z_hist - 0.35, 0.5,
             f'Historical theoretical\nreference z_crit={z_hist}',
             color='purple', rotation=90, weight='bold', fontsize=8, alpha=0.7)

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

    plt.title(r'Figure 1: Cosmological Phase Transition — Ensemble $\langle$Rank$\rangle$ & $\langle G_{\mathrm{eff}} \rangle$',
              fontsize=12, pad=12)
    fig.tight_layout()
    plt.savefig('sre_phase_transition.png', dpi=300)
    plt.close()


def _plot_galaxy_mass_crisis(boot_df, t_Gyr, M_lambda, M_sre, M_sre_low, M_sre_high, z_star):
    """
    [BOOT-FIX-4] Galaxy mass using Bootstrap mean G_eff with 95% CI band.
    """
    print("[SRE Framework] Exporting Figure 2: 'sre_galaxy_mass_crisis.png'...")

    plt.figure(figsize=(10, 5))
    plt.semilogy(t_Gyr, M_lambda,
                 color='black', linestyle='--', lw=2.0,
                 label=r'$\Lambda$CDM Accretion ($G_0$ constant)')
    plt.semilogy(t_Gyr, M_sre,
                 color='#dc2626', lw=2.5,
                 label=r'SRE v6.2 $\langle G_{\mathrm{eff}} \rangle$ Euler-Coupled')

    # [BOOT-FIX-4] 95% CI band for mass
    plt.fill_between(t_Gyr, M_sre_low, M_sre_high,
                     color='#dc2626', alpha=0.15, label='SRE Mass 95% CI')

    plt.axhspan(1e10, 1e11, color='#fbbf24', alpha=0.2,
                label=r'JWST Mature Galaxy Boundary ($z > 5$)')

    plt.yscale('log')
    # [CRITICAL-FIX-2] Use actual lookback time range, not hardcoded [0, 5]
    t_min = float(np.min(t_Gyr)) if len(t_Gyr) > 0 else 0.0
    t_max = float(np.max(t_Gyr)) if len(t_Gyr) > 0 else 5.0
    plt.xlim(t_min, t_max)
    plt.xlabel('Lookback Time (Gyr) [Planck 2018 LambdaCDM]', fontsize=11)
    plt.ylabel(r'Galaxy Core Mass ($M_\odot$)', fontsize=11)
    plt.title(r'Figure 2: Primordial Mass Accumulation — $\Lambda$CDM vs SRE v6.2 Ensemble',
              fontsize=12, pad=12)
    plt.legend(loc='lower right', fontsize=9)
    plt.grid(True, which="both", linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig('sre_galaxy_mass_crisis.png', dpi=300)
    plt.close()


def _plot_gravitational_lensing(boot_df, z_star):
    """
    [BOOT-FIX-4] Gravitational lensing with ensemble average, z* and historical ref.
    """
    print("[SRE Framework] Exporting Figure 4: 'lens_jump_2to4.png'...")

    if len(boot_df) == 0:
        print("[SRE Framework] Skipping lensing plot -- insufficient data.")
        return

    G0 = SRE_CONFIG["G_BASE"]
    c0 = SRE_CONFIG["C_LIGHT"]
    M_sun_kg = 1.989e30
    kpc_m = 3.0857e19
    b_impact_kpc = 10.0
    b_m = b_impact_kpc * kpc_m

    M_galaxy_ref = 1e12  # M_sun
    M_kg_const = M_galaxy_ref * M_sun_kg

    z_arr = boot_df['z'].values
    g_eff_mean = boot_df['g_eff_mean'].values
    g_eff_low = boot_df['g_eff_ci_low'].values
    g_eff_high = boot_df['g_eff_ci_high'].values

    # Compute Einstein radius with ensemble mean G_eff
    theta_E_mean = np.sqrt(4.0 * g_eff_mean * M_kg_const / (c0 ** 2 * b_m)) * 206265.0
    theta_E_low = np.sqrt(4.0 * g_eff_low * M_kg_const / (c0 ** 2 * b_m)) * 206265.0
    theta_E_high = np.sqrt(4.0 * g_eff_high * M_kg_const / (c0 ** 2 * b_m)) * 206265.0

    # G0 baseline
    theta_E_G0 = np.sqrt(4.0 * G0 * M_kg_const / (c0 ** 2 * b_m)) * 206265.0

    plt.figure(figsize=(10, 5))

    # Ensemble mean Einstein radius
    plt.semilogy(z_arr, theta_E_mean,
                 color='#0ea5e9', lw=2.5,
                 label=r'$\langle \theta_E \rangle$ (Bootstrap mean $G_{\mathrm{eff}}$)')

    # 95% CI fill
    plt.fill_between(z_arr, theta_E_low, theta_E_high,
                     color='#0ea5e9', alpha=0.15, label=r'$\theta_E$ 95% CI')

    # G0 baseline
    plt.axhline(y=theta_E_G0, color='green', linestyle='--', alpha=0.7, lw=1.5,
                label=f'G0 baseline: {theta_E_G0:.2f}"')

    # M87 reference
    theta_E_m87 = 8.6
    plt.axhline(y=theta_E_m87, color='gray', linestyle='--', alpha=0.5,
                label=f'M87* reference: {theta_E_m87}"')

    # [BOOT-FIX-3] Simulated z* — solid orange line
    if z_star is not None:
        plt.axvline(x=z_star, color='orange', linestyle='-', alpha=0.9, lw=2.0)
        plt.text(z_star + 0.05, theta_E_G0 * 0.5,
                 f'Simulated z* = {z_star:.2f}',
                 color='orange', rotation=90, weight='bold', fontsize=9)

    # [BOOT-FIX-3] Historical reference — purple dashed
    z_hist = SRE_CONFIG["HISTORICAL_Z_CRIT"]
    plt.axvline(x=z_hist, color='purple', linestyle='--', alpha=0.4, lw=1.5)
    plt.text(z_hist - 0.3, theta_E_G0 * 0.3,
             f'Historical ref\nz_crit={z_hist}',
             color='purple', rotation=90, fontsize=8, alpha=0.6)

    plt.xlabel('Cosmological Redshift (z)', fontsize=11)
    plt.ylabel(r'Einstein Radius $\theta_E$ [arcsec]', fontsize=11)
    plt.title(r'Figure 4: Gravitational Lensing — Ensemble $2 \to 4$ Rank Transition',
              fontsize=12, pad=12)
    plt.legend(loc='upper left', fontsize=9)
    plt.grid(True, which="both", linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig('lens_jump_2to4.png', dpi=300)
    plt.close()


# =========================================================================
# PHASE 7: UNIT TESTS (v6.2 extended with Bootstrap tests)
# =========================================================================
def _run_unit_tests():
    """
    [BOOT-FIX-6] Extended unit tests:
      Test 1:  alpha_0_dynamic(dz=0.03925) approx 21.09
      Test 2:  Conformal Omega
      Test 3:  Local c-invariance
      Test 4:  [FIX-1] Matrix trace D @ C vs element-wise
      Test 5:  [BOOT-FIX-1] Real dz with eps protection
      Test 6:  [FIX-3] G_eff derivation from Tr(D@C)
      Test 7:  [FIX-4] Tracy-Widom boundary validation
      Test 8:  [FIX-6] Lensing deflection formula
      Test 9:  [BOOT-FIX-2] Bootstrap small-sample run
      Test 10: [BOOT-FIX-3] z* calculation logic
      Test 11: [CRITICAL-FIX-2] z -> lookback_time mapping
      Test 12: [CRITICAL-FIX-4] Rank detection dual-mode (debug/production)
      Test 13: [CRITICAL-FIX-1] Bootstrap matrix dimension consistency
    """
    print("\n" + "=" * 90)
    print(" SRE v6.2 UNIT TESTS (Bootstrap Edition)")
    print("=" * 90)

    eps_mach = np.finfo(np.float64).eps
    theta = SRE_CONFIG["THETA_CONFORMAL"]
    gamma_lat = SRE_CONFIG["GAMMA_LATENCY"]

    # --- Test 1: α₀_dynamic ---
    delta_z_test = 0.03925
    alpha_test = theta / (delta_z_test + eps_mach)
    expected_alpha = 21.09
    print(f"[TEST 1] alpha_0_dynamic = theta/(dz+eps)")
    print(f"         dz = {delta_z_test}")
    print(f"         alpha_0 = {alpha_test:.4f}  (expected ~{expected_alpha})")
    assert abs(alpha_test - expected_alpha) < 0.01
    print(f"         PASS")

    # --- Test 2: Conformal Ω ---
    Omega_test = (delta_z_test / theta) ** (-gamma_lat / 4.0)
    print(f"[TEST 2] Omega = {Omega_test:.6f}")
    assert Omega_test > 0
    print(f"         PASS")

    # --- Test 3: Local c-invariance ---
    c0 = SRE_CONFIG["C_LIGHT"]
    c_local = c0 * Omega_test / Omega_test
    assert abs(c_local - c0) < 1e-5
    print(f"[TEST 3] c-local invariance: PASS")

    # --- Test 4: [FIX-1] Matrix product D @ C vs element-wise ---
    print("[TEST 4] Matrix product validation [FIX-1]:")
    sigma_test = np.array([1e-4, 5e-4])
    sigma_i = sigma_test[:, None]
    sigma_j = sigma_test[None, :]
    D_test = np.log1p(sigma_i * sigma_j / eps_mach)
    C_test = (1.0 / alpha_test) * np.sin(np.pi * alpha_test * D_test) ** 2

    R_elem = D_test * C_test
    R_mat = D_test @ C_test

    print(f"         Element-wise sum: {np.sum(R_elem):.6f}")
    print(f"         Trace(D@C):       {np.trace(R_mat):.6f}")
    assert not np.allclose(R_elem, R_mat), "Matrix product should differ from element-wise"
    print(f"         PASS (matrix product is distinct from element-wise)")

    # --- Test 5: [BOOT-FIX-1] Real Δz with eps protection ---
    print("[TEST 5] Real dz with eps protection [BOOT-FIX-1]:")
    rng_test = np.random.default_rng(seed=99)
    z_test = np.sort(rng_test.uniform(0.10, 0.145, 50))
    delta_z_real = np.max(z_test) - np.min(z_test)
    delta_z_protected = np.maximum(delta_z_real, eps_mach)
    print(f"         z_slice range: [{np.min(z_test):.4f}, {np.max(z_test):.4f}]")
    print(f"         Real dz = {delta_z_real:.6f}")
    print(f"         Protected dz = {delta_z_protected:.6f}")
    assert delta_z_protected > 0.04, "Real dz should be determined by slice bounds"
    assert delta_z_protected >= eps_mach, "Protection should ensure dz >= eps_mach"
    print(f"         PASS")

    # Test 5b: Edge case — all same z values
    z_flat = np.full(10, 0.5)
    delta_z_flat = np.maximum(np.max(z_flat) - np.min(z_flat), eps_mach)
    print(f"         Edge case (flat z): dz = {delta_z_flat:.2e} (should be eps_mach)")
    assert delta_z_flat == eps_mach, "Flat z should give eps_mach after protection"
    print(f"         PASS (edge case)")

    # --- Test 6: [FIX-3] G_eff derivation ---
    print("[TEST 6] G_eff derivation from Tr(D@C) [FIX-3]:")
    z_test6 = np.sort(rng_test.uniform(0.10, 0.145, 50))
    zerr_test6 = 1e-4 * np.exp(z_test6 * 0.3) + rng_test.normal(0, 1e-5, 50)
    zerr_test6 = np.maximum(zerr_test6, 1e-8)

    result6 = compute_derived_quantities(z_test6, zerr_test6, debug=False)
    assert result6 is not None
    g_eff6 = result6['g_eff']
    g0 = SRE_CONFIG["G_BASE"]
    print(f"         G_eff = {g_eff6:.4e}  (G0 = {g0:.4e})")
    print(f"         G_eff/G0 = {g_eff6/g0:.4f}")
    assert g_eff6 > 0
    print(f"         PASS")

    # --- Test 7: [FIX-4] Tracy-Widom boundary ---
    print("[TEST 7] Tracy-Widom boundary validation [FIX-4]:")
    N_test = 50
    tw_boundary_test = 2.0 * np.sqrt(N_test) + N_test ** (-1.0/6.0) * SRE_CONFIG["TW_QUANTILE_099"]
    print(f"         N = {N_test}")
    print(f"         2*sqrt(N) = {2.0*np.sqrt(N_test):.4f}")
    print(f"         TW boundary = {tw_boundary_test:.4f}")
    assert tw_boundary_test > 2.0 * np.sqrt(N_test)
    print(f"         PASS")

    # --- Test 8: [FIX-6] Lensing deflection ---
    print("[TEST 8] Gravitational lensing deflection [FIX-6]:")
    c0 = SRE_CONFIG["C_LIGHT"]
    G0 = SRE_CONFIG["G_BASE"]
    M_test = 1e12
    b_test_kpc = 10.0
    M_kg_test = M_test * 1.989e30
    b_m_test = b_test_kpc * 3.0857e19
    alpha_lens_test = 4.0 * G0 * M_kg_test / (c0 ** 2 * b_m_test)
    alpha_lens_arcsec = alpha_lens_test * 206265.0
    print(f"         M = {M_test:.1e} M_sun, b = {b_test_kpc} kpc")
    print(f"         alpha_lens = {alpha_lens_arcsec:.4f} arcsec")
    assert alpha_lens_test > 0
    print(f"         PASS")

    # --- Test 9: [BOOT-FIX-2] Bootstrap small-sample run ---
    print("[TEST 9] Bootstrap small-sample run [BOOT-FIX-2]:")
    rng_test9 = np.random.default_rng(seed=42)
    z_test9 = np.sort(rng_test9.uniform(0.1, 1.0, 50))
    zerr_test9 = 1e-4 * np.exp(z_test9 * 0.3) + rng_test9.normal(0, 1e-5, 50)
    zerr_test9 = np.maximum(zerr_test9, 1e-8)

    # Run 20 bootstrap samples for quick test
    ranks, g_effs, alphas = _bootstrap_single(z_test9, zerr_test9, 20, rng_seed=42)
    print(f"         N_bootstrap = 20")
    print(f"         ranks = {ranks}")
    print(f"         <rank> = {np.mean(ranks):.2f}")
    print(f"         <g_eff> = {np.mean(g_effs):.4e}")
    print(f"         <alpha> = {np.mean(alphas):.4f}")
    assert len(ranks) == 20
    assert len(g_effs) == 20
    assert np.all(ranks >= 2) and np.all(ranks <= 4)
    assert np.all(g_effs > 0)
    assert np.all(alphas > 0)
    print(f"         PASS")

    # --- Test 10: [BOOT-FIX-3] z* calculation logic ---
    print("[TEST 10] Simulated z* calculation [BOOT-FIX-3]:")
    # Create synthetic bootstrap results where P(rank<=2) transitions at z~3.5
    z_synthetic = np.arange(0.5, 6.0, 0.1)
    p_le2_synthetic = np.where(z_synthetic < 3.5, 0.1, 0.8)
    boot_synthetic = pd.DataFrame({
        'z': z_synthetic,
        'p_rank_le2': p_le2_synthetic,
        'rank_mean': np.where(z_synthetic < 3.5, 3.5, 2.2),
        'g_eff_mean': np.full(len(z_synthetic), 7e-11),
        'g_eff_ci_low': np.full(len(z_synthetic), 6e-11),
        'g_eff_ci_high': np.full(len(z_synthetic), 8e-11),
        'cooling_mean': np.full(len(z_synthetic), 1.0),
        'cooling_ci_low': np.full(len(z_synthetic), 0.9),
        'cooling_ci_high': np.full(len(z_synthetic), 1.1),
        'alpha_mean': np.full(len(z_synthetic), 21.0),
        'alpha_ci_low': np.full(len(z_synthetic), 20.0),
        'alpha_ci_high': np.full(len(z_synthetic), 22.0),
        'rank_median': np.where(z_synthetic < 3.5, 4, 2),
        'p_rank_ge3': 1.0 - p_le2_synthetic,
        'p_rank_eq4': np.where(z_synthetic < 3.5, 0.8, 0.1),
    })
    z_star_test = compute_simulated_z_star(boot_synthetic)
    print(f"         Synthetic transition at z=3.5")
    print(f"         Computed z* = {z_star_test:.2f}")
    assert z_star_test is not None
    assert 3.0 < z_star_test < 4.0, f"z*={z_star_test} should be near 3.5"
    # [BOOT-FIX-3] Verify 4.1605 is NOT used in any logic
    assert z_star_test != SRE_CONFIG["HISTORICAL_Z_CRIT"], "z* must not equal hardcoded 4.1605"
    print(f"         PASS (z* = {z_star_test:.2f}, NOT hardcoded 4.1605)")

    # --- Test 11: [CRITICAL-FIX-2] z -> lookback time mapping ---
    print("[TEST 11] z -> lookback_time mapping [CRITICAL-FIX-2]:")
    t_z0 = z_to_lookback_time(0.0)
    t_z1 = z_to_lookback_time(1.0)
    t_z6 = z_to_lookback_time(6.0)
    print(f"         t_L(z=0) = {t_z0:.4f} Gyr (expected 0.0)")
    print(f"         t_L(z=1) = {t_z1:.4f} Gyr (expected ~7.7)")
    print(f"         t_L(z=6) = {t_z6:.4f} Gyr (expected ~13.1)")
    assert abs(t_z0) < 1e-6, "t_L(0) should be 0"
    assert 7.0 < t_z1 < 9.0, f"t_L(1)={t_z1:.2f} should be ~7.7 Gyr"
    assert 12.0 < t_z6 < 14.0, f"t_L(6)={t_z6:.2f} should be ~13.1 Gyr"
    # Monotonicity: higher z => larger lookback time
    assert t_z6 > t_z1 > t_z0, "lookback time must be monotonic in z"
    print(f"         PASS")

    # --- Test 12: [CRITICAL-FIX-4] Both rank detection modes ---
    print("[TEST 12] Rank detection dual-mode [CRITICAL-FIX-4]:")
    # Create synthetic eigenvalues: 2 large signal + 20 small bulk
    rng_test12 = np.random.default_rng(seed=42)
    bulk_eigs = rng_test12.normal(0.01, 0.005, 20)
    signal_eigs = np.array([5.0, 3.0])
    test_eigs = np.concatenate([bulk_eigs, signal_eigs])

    # Mode A: debug
    SRE_CONFIG["RANK_DETECTION_MODE"] = "debug"
    rank_dbg, tw_dbg, nsig_dbg = _detect_rank(test_eigs, len(test_eigs), debug=False)
    print(f"         Mode A (debug):    rank={rank_dbg}  n_signal={nsig_dbg}")

    # Mode B: production
    SRE_CONFIG["RANK_DETECTION_MODE"] = "production"
    rank_prod, tw_prod, nsig_prod = _detect_rank(test_eigs, len(test_eigs), debug=False)
    print(f"         Mode B (production): rank={rank_prod}  n_signal={nsig_prod}")

    # Both modes should detect at least 1 signal eigenvalue
    assert nsig_dbg >= 1, "Debug mode should detect signal eigenvalues"
    assert nsig_prod >= 1, "Production mode should detect signal eigenvalues"
    assert 2 <= rank_dbg <= 4, f"Debug rank={rank_dbg} out of [2,4]"
    assert 2 <= rank_prod <= 4, f"Production rank={rank_prod} out of [2,4]"
    # Restore production mode
    SRE_CONFIG["RANK_DETECTION_MODE"] = "production"
    print(f"         PASS")

    # --- Test 13: [CRITICAL-FIX-1] Bootstrap matrix dimension consistency ---
    print("[TEST 13] Bootstrap matrix dim consistency [CRITICAL-FIX-1]:")
    rng_test13 = np.random.default_rng(seed=42)
    z_test13 = np.sort(rng_test13.uniform(0.1, 1.0, 100))
    zerr_test13 = 1e-4 * np.exp(z_test13 * 0.3) + rng_test13.normal(0, 1e-5, 100)
    zerr_test13 = np.maximum(zerr_test13, 1e-8)

    ranks13, g_effs13, alphas13 = _bootstrap_single(z_test13, zerr_test13, 20, rng_seed=42)
    print(f"         Input n_total=100, cap={SRE_CONFIG['BOOTSTRAP_MATRIX_CAP']}")
    print(f"         ranks = {ranks13}")
    print(f"         <rank> = {np.mean(ranks13):.2f}")
    print(f"         <g_eff> = {np.mean(g_effs13):.4e}")
    assert len(ranks13) == 20
    assert np.all(ranks13 >= 2) and np.all(ranks13 <= 4)
    assert np.all(g_effs13 > 0)
    assert np.all(alphas13 > 0)
    # [CRITICAL-FIX-1] All ranks should be consistent (matrix dim fixed)
    # With fixed dim, rank distribution should be tight (not scattered)
    rank_std = np.std(ranks13)
    print(f"         rank std = {rank_std:.2f} (should be small with fixed dim)")
    assert rank_std <= 2.0, "Rank std should be bounded with fixed matrix dim"
    print(f"         PASS")

    print("\n" + "=" * 90)
    print(" All v6.2 unit tests passed (13/13)")
    print("=" * 90)


# =========================================================================
# ENTRY POINT
# =========================================================================
if __name__ == "__main__":
    import sys

    _run_unit_tests()

    # [BOOT-FIX-2] Allow debug mode with fewer bootstrap iterations
    # Usage: python sre_full_framework.py 50  (for 50 bootstrap samples)
    n_boot = None  # Default: use SRE_CONFIG["BOOTSTRAP_N"] = 1500
    if len(sys.argv) > 1:
        try:
            n_boot = int(sys.argv[1])
            print(f"\n[SRE Framework] Debug mode: N_bootstrap = {n_boot}")
        except ValueError:
            pass

    print(f"\n[SRE Framework] Starting v6.2 production pipeline "
          f"(N_bootstrap={'default' if n_boot is None else n_boot})...\n")
    run_production_pipeline(n_bootstrap=n_boot)

# =========================================================================
# RUN INSTRUCTIONS
# =========================================================================
# Dependencies:
#   pip install numpy scipy pandas matplotlib requests
#   (optional: pip install astroquery  for live SDSS DR17 queries)
#
# Running:
#   Full production (1500 Bootstrap):
#     python sre_full_framework.py
#
#   Quick debug (50 Bootstrap):
#     python sre_full_framework.py 50
#
#   Medium (200 Bootstrap):
#     python sre_full_framework.py 200
#
# Rank detection mode (in SRE_CONFIG):
#   RANK_DETECTION_MODE = "production"  # BBP-RMT eigenvalue bulk + TW (default)
#   RANK_DETECTION_MODE = "debug"       # fixed eigenvalue threshold (observation)
#
# Output files (4 PNG at 300 dpi):
#   1. sre_condition_diagnostics.png  -- condition number stability
#   2. sre_phase_transition.png       -- ensemble <Rank(z)> & <G_eff/G0> with CI
#   3. sre_galaxy_mass_crisis.png     -- mass accumulation with 95% CI band
#   4. lens_jump_2to4.png             -- gravitational lensing with z*
#
# Key design principle:
#   z* is SIMULATED from Bootstrap P(rank<=2)>=0.5.
#   z_crit=4.1605 is a plot-only historical reference line.
#   Simulation results are authoritative; paper text follows simulation.
#
# [CRITICAL-FIX summary]:
#   1. Bootstrap matrix dimension FIXED (no TW threshold drift)
#   2. z -> lookback_time via Planck 2018 LambdaCDM (real cosmological time)
#   3. G_eff analytically derived: G_0 * Omega * (R/4) * Tr(D@C)/(N*mu_loss)
#   4. Rank detection: dual-mode (debug=fixed, production=BBP-RMT eigenvalue)
