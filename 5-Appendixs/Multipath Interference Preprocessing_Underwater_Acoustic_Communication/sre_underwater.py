"""
Underwater Acoustic Communication Field Dataset SRE Topology Signal Processing Pipeline
======================================================================================
Strictly follows idea.md design specifications:
  - Reuse SRE ten-operator topology pipeline (Op4/Op5/Op10 core)
  - wav → STFT → frequency×time complex time-frequency matrix → local square matrix → SRE purification → CFAR detection
  - Full matrix vectorization, point-by-point for loops prohibited
  - Three-layer mutually exclusive masks: bridge (direct path) / high-impedance (multipath) / clutter (noise)
  - Output: console statistics + PNG evaluation plots + npy purified data
Dependencies: numpy / scipy / matplotlib / sre_rust
"""

import os
import time
import logging
import numpy as np
import scipy.signal as ssig
import scipy.io.wavfile as wv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# Standard English-safe matplotlib configuration
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Liberation Sans", "Bitstream Vera Sans"]
plt.rcParams["axes.unicode_minus"] = True
from sre_rust import (
    SREFoundationalOperatorSuite,
    SRETransportAlignmentSuite,
    SRECommercialCoreSuite,
)

# =====================================================================
# Module 1: Global Constants
# =====================================================================

# --- SRE Topology Hyperparameters ---
SRE_BETA = 1.2              # Statistical mechanics inverse temperature β
SRE_LAMBDA_0 = 0.9          # Coupling constant
SRE_LAMBDA_2 = 0.5          # Fiedler prior λ₂
SRE_ALPHA_N = 0.8           # Spectral radius prior αₙ
SRE_EPS_TOPO = 1e-6         # Topology regularization lower bound
SRE_MAX_DIM = 512           # Local graph maximum dimension
SRE_C_MAX = 3.0             # Vacuum limit propagation speed
SRE_K0_HORIZON = 30         # Firewall horizon
SRE_LAMBDA_BASE = 0.5       # Base coupling

# --- Underwater Acoustic STFT Dedicated Parameters ---
STFT_NPERSEG = 256          # Samples per segment → F = 129 frequency bins
STFT_NOVERLAP = 192         # 75% overlap → stride 64
STFT_WINDOW = "hann"

# --- Matrix Blocking Parameters ---
BLOCK_N = 128               # Local square matrix dimension N×N (F-1)
BLOCK_STRIDE = 64           # Temporal sliding window stride

# --- CFAR Constant False Alarm Rate Parameters ---
CFAR_GUARD = 3              # Guard cell half-width
CFAR_TRAIN = 8              # Training cell half-width
CFAR_PFA = 1e-3             # Probability of false alarm
CFAR_MIN_PEAK = 1e-6        # Peak lower bound

# --- Mask Attenuation Coefficients (idea.md 3.2.5) ---
ATTEN_BRIDGE = 1.0          # Bridge: keep, no attenuation
ATTEN_HIGH_Z = 0.1          # High-impedance: heavy attenuation
ATTEN_CLUTTER = 0.5         # Clutter: mild attenuation

# --- Mask Thresholds ---
BRIDGE_C_E_FRAC = 0.8       # c_e > 0.8*c_max classified as bridge
HIGH_Z_ABS = 0.5            # |z_eff| > 0.5 classified as high-impedance

# --- Numerical Safeguards ---
EPS = 1e-16
NUM_OFFSET = 1e-12          # Small value offset

# --- Data Paths ---
ROOT = os.path.dirname(os.path.abspath(__file__))
BAND_DIR = {"LF": "LF", "MF": "MF", "HF": "HF"}
ENV_CTD = os.path.join(ROOT, "Environmental", "CTD.csv")
OUT_DIR = os.path.join(ROOT, "sre_output")

# --- TX Transmitter CSV Symbol Paths (actual OFDM modulated symbols per band) ---
TX_SYMBOL_CSV = {
    "LF": os.path.join(ROOT, "TX", "csv", "LF", "OFDM-LF.csv"),
    "MF": os.path.join(ROOT, "TX", "csv", "MF", "OFDM-MF.csv"),
    "HF": os.path.join(ROOT, "TX", "csv", "HF", "OFDM-HF.csv"),
}

# --- Diversity Combining Parameters ---
DIVIDE_MAX_RATIO = 0.3       # R1/R2 energy ratio anomaly detection threshold
DIVIDE_ALPHA = 0.5            # Weighted fusion exponent

# --- BER Estimation Parameters ---
BER_CONST_POINTS = 64        # Constellation points (QPSK=4, simplified to 4-QAM here)
BER_DECISION = 1.0           # Decision boundary threshold

# --- TX A Priori Auxiliary Parameters ---
TX_AIDED_FILTER = True        # Enable TX-aided false alarm filtering
TX_PEAK_TOLERANCE = 0.10      # Peak count tolerance (expected ±10%, tightened from 25%)
TX_MAD_K = 3.0                # MAD robust amplitude threshold coefficient (median - k×MAD)
TX_ROW_OCCUPANCY = 1.0        # Frequency-bin row duty cycle: peaks per row ≤ expected_syms × this coefficient
TX_NBHD_RATIO = 0.10          # Neighborhood consistency: 3×3 2nd-max/max < this value → isolated false alarm

# --- HF High-Frequency Special Parameters (low SNR adaptation) ---
HF_BRIDGE_C_E_FRAC = 0.65    # HF: lower bridge classification threshold (was 0.8)
HF_HIGH_Z_ABS = 0.35         # HF: lower high-impedance threshold (was 0.5)
HF_ATTEN_BRIDGE = 1.0        # HF: keep bridge unattenuated
HF_ATTEN_CLUTTER = 0.3       # HF: stronger clutter suppression (was 0.5)
HF_CFAR_PFA = 5e-4           # HF: lower false alarm probability (was 1e-3)
HF_PRE_DENOISE = True        # HF: enable pre-denoising

# --- QPSK Demodulation Parameters ---
QPSK_CONSTELLATION = np.array([1+1j, -1+1j, 1-1j, -1-1j]) * 0.7071
QPSK_PHASE_OFFSET = np.pi / 4  # π/4 offset QPSK

# --- Deep Fading Frame Interpolation Recovery Enhancement Parameters ---
DF_HIGH_BER_THRESH = 0.5      # Per-frame BER > this value → high error frame, trigger temporal smoothing
DF_TIME_SMOOTH_WIDTH = 3      # Temporal sliding window width (column-wise median filtering)
DF_COMPLEX_INTERP = True       # Complex path interpolation (preserves phase)

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("SRE_Underwater")


# =====================================================================
# Module 2: Utility Functions sig2stft — wav reading + STFT to complex time-frequency matrix
# =====================================================================

def load_sound_speed_profile(ctd_path=ENV_CTD):
    """Read CTD sound-speed profile mean, used to modulate the λ₂ prior."""
    try:
        # CTD.csv contains GBK characters like °C, use csv module for tolerant parsing of column 6 sound speed (index 5)
        import csv
        vals = []
        with open(ctd_path, "r", encoding="latin1", errors="replace") as fp:
            reader = csv.reader(fp)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 6:
                    try:
                        vals.append(float(row[5]))
                    except ValueError:
                        continue
        if not vals:
            raise ValueError("No valid sound speed data")
        c_mean = float(np.nanmean(vals))
        logger.info("CTD sound speed mean = %.2f m/s (n=%d)", c_mean, len(vals))
        return c_mean
    except Exception as e:
        logger.warning("CTD read failed, using reference sound speed 1500 m/s: %s", e)
        return 1500.0


def read_wav_mono(path):
    """Read mono wav, return float64 normalized time-domain sequence and sample rate.

    Supports 24-bit PCM (scipy returns int32, lower 24 bits valid, upper bits need sign extension).
    Supports 16-bit PCM (int16) and 8-bit PCM (uint8).
    """
    fs, data = wv.read(path)

    if data.dtype == np.int32:
        # 24-bit PCM: scipy returns int32, but upper 8 bits may not be properly sign-extended.
        # Correct approach: take lower 24 bits → sign-extend from bit23 → divide by 2^23.
        data = data.astype(np.int32)
        # Mask lower 24 bits
        data = data & 0xFFFFFF
        # Sign extension: if bit23 is 1, set all upper bits to 1
        # Use the (x ^ mask) - mask trick, where mask = 1 << 23
        mask = np.int32(1 << 23)
        data = (data ^ mask) - mask
        data = data.astype(np.float64) / float(1 << 23)
    elif data.dtype == np.int16:
        data = data.astype(np.float64) / float(1 << 15)
    elif data.dtype == np.uint8:
        data = (data.astype(np.float64) - 128.0) / 128.0
    else:
        data = data.astype(np.float64)

    if data.ndim > 1:           # multi-channel take average
        data = data.mean(axis=1)
    return data, fs


def sig2stft(sig, fs,
             nperseg=STFT_NPERSEG, noverlap=STFT_NOVERLAP,
             window=STFT_WINDOW):
    """1D time-domain → 2D complex time-frequency matrix S(F×T).

    Returns:
        S_complex: np.ndarray[complex128], shape=(F, T)
        f: frequency axis
        t: time axis
    """
    f, t, Z = ssig.stft(
        sig, fs=fs, window=window, nperseg=nperseg, noverlap=noverlap,
        boundary=None, padded=False, return_onesided=True,
    )
    # Safeguard: avoid zero matrices and invalid values
    Z = np.where(np.isfinite(Z), Z, 0.0 + 0j)
    return Z.astype(np.complex128), f, t


# =====================================================================
# Module 3: Utility Functions advanced_cfar_and_grouping — CFAR peak detection
# =====================================================================

def advanced_cfar_and_grouping(mat, guard=CFAR_GUARD, train=CFAR_TRAIN,
                               pfa=CFAR_PFA, min_peak=CFAR_MIN_PEAK):
    """2D CA-CFAR constant false alarm rate detection, vectorized implementation.

    Parameters:
        mat: 2D float64 energy/amplitude matrix
        guard: guard cell half-width
        train: training cell half-width
        pfa: probability of false alarm
        min_peak: peak lower bound filter
    Returns:
        peak_mask: bool matrix, True indicates detected peak
        n_peaks: int number of peaks
    """
    M = np.asarray(mat, dtype=np.float64)
    M = np.nan_to_num(M, nan=0.0, posinf=0.0, neginf=0.0) + NUM_OFFSET
    H, W = M.shape
    win = 2 * (guard + train) + 1
    if H < win or W < win:
        # Matrix too small, degenerate to global threshold
        thr = np.percentile(M, 99.9)
        peak_mask = M >= max(thr, min_peak)
        return peak_mask, int(peak_mask.sum())

    # Use uniform convolution kernel to compute training window sum (CA-CFAR)
    # Full window integral - guard window integral = training cell sum
    ker_full = np.ones((win, win), dtype=np.float64)
    ker_guard = np.ones((2 * guard + 1, 2 * guard + 1), dtype=np.float64)
    sum_full = ssig.fftconvolve(M, ker_full, mode="same")
    sum_guard = ssig.fftconvolve(M, ker_guard, mode="same")
    sum_train = sum_full - sum_guard
    n_train = win * win - (2 * guard + 1) ** 2
    n_train = max(n_train, 1)
    noise_mean = sum_train / n_train

    # CA-CFAR threshold factor: T = N * (Pfa^(-1/N) - 1)
    alpha = n_train * (pfa ** (-1.0 / n_train) - 1.0)
    threshold = noise_mean * alpha

    # Local maxima detection (3×3 neighborhood)
    peak_mask = (M > threshold) & (M > min_peak)
    # Use maximum filter to preserve local maxima (3x3 total 9 elements, rank=8 is maximum, 0-indexed)
    max_filt = ssig.order_filter(M, np.ones((3, 3)), 8)
    peak_mask = peak_mask & (M == max_filt)

    # Boundary cleanup
    peak_mask[:guard + train, :] = False
    peak_mask[-(guard + train):, :] = False
    peak_mask[:, :guard + train] = False
    peak_mask[:, -(guard + train):] = False

    n_peaks = int(peak_mask.sum())
    return peak_mask, n_peaks


def tx_aided_peak_filter(peak_mask, mat, band, frame_idx=0):
    """TX-aided false alarm secondary screening (enhanced version, quadruple filtering).

    Uses TX symbol count (LF/MF=42, HF=64) and amplitude priors to perform
    quadruple robust screening on CFAR detected peaks, significantly eliminating R1 false alarm peaks:
      1. MAD robust amplitude filtering: median - k×MAD replaces mean-σ, resistant to outliers
      2. Neighborhood consistency filtering: 3×3 neighborhood 2nd-max/max < threshold → isolated false alarm eliminated
      3. Frequency-bin row duty cycle filtering: if peaks per frequency-bin row exceed expected_syms → keep top
      4. Hard count constraint: top-N × (1+tolerance), tolerance tightened to 10%

    Returns:
        filtered_mask: bool matrix
        n_filtered: int
        filter_info: dict filtering details
    """
    expected_syms = 42 if band in ("LF", "MF") else 64
    mat_arr = np.asarray(mat, dtype=np.float64)
    mat_arr = np.nan_to_num(mat_arr, nan=0.0, posinf=0.0, neginf=0.0)
    H, W = mat_arr.shape

    peak_coords = np.argwhere(peak_mask)
    n_orig = len(peak_coords)
    if n_orig == 0:
        return peak_mask, 0, {"original": 0, "kept": 0, "reason": "no_peaks"}

    peak_vals = np.array([mat_arr[r, c] for r, c in peak_coords])

    # --- Strategy 1: MAD robust amplitude filtering (replaces mean-1.5σ) ---
    p_median = float(np.median(peak_vals))
    mad = float(np.median(np.abs(peak_vals - p_median)))
    # MAD → equivalent σ estimate: σ ≈ 1.4826 × MAD
    sigma_eq = 1.4826 * mad if mad > 0 else float(np.std(peak_vals))
    energy_thr = p_median - TX_MAD_K * sigma_eq
    if energy_thr > 0:
        amp_keep = peak_vals >= energy_thr
    else:
        amp_keep = np.ones(n_orig, dtype=bool)
    n_after_amp = int(amp_keep.sum())

    # --- Strategy 2: Neighborhood consistency filtering (eliminate isolated spike false alarms) ---
    # True symbols have energy spread in 3×3 neighborhood, 2nd-max/max is larger;
    # False alarms are isolated spikes, neighborhood 2nd-max/max is small.
    nbhd_keep = np.ones(n_orig, dtype=bool)
    for i, (r, c) in enumerate(peak_coords):
        if not amp_keep[i]:
            nbhd_keep[i] = False
            continue
        r_lo, r_hi = max(0, r - 1), min(H, r + 2)
        c_lo, c_hi = max(0, c - 1), min(W, c + 2)
        patch = mat_arr[r_lo:r_hi, c_lo:c_hi]
        patch_flat = patch.flatten()
        if len(patch_flat) < 2:
            continue
        max_val = patch_flat.max()
        if max_val <= 0:
            nbhd_keep[i] = False
            continue
        # Second largest value (max after removing maximum)
        sorted_patch = np.sort(patch_flat)[::-1]
        second_val = sorted_patch[1] if len(sorted_patch) > 1 else 0.0
        ratio = second_val / max_val
        if ratio < TX_NBHD_RATIO:
            nbhd_keep[i] = False  # isolated false alarm
    n_after_nbhd = int(nbhd_keep.sum())

    # Combined amplitude + neighborhood filtering
    combined_keep = amp_keep & nbhd_keep
    filtered_mask = np.zeros_like(peak_mask)
    for i, (r, c) in enumerate(peak_coords):
        if combined_keep[i]:
            filtered_mask[r, c] = True

    # --- Strategy 3: Frequency-bin row duty cycle filtering (peaks per row ≤ expected_syms × coefficient) ---
    row_max = max(int(expected_syms * TX_ROW_OCCUPANCY), 1)
    if int(filtered_mask.sum()) > 0:
        rows_present = np.unique(np.argwhere(filtered_mask)[:, 0])
        for rr in rows_present:
            row_cols = np.where(filtered_mask[rr, :])[0]
            if len(row_cols) > row_max:
                # Keep top-row_max peaks for this row
                row_vals = np.array([mat_arr[rr, cc] for cc in row_cols])
                top_idx = np.argsort(row_vals)[-row_max:]
                filtered_mask[rr, :] = False
                for ti in top_idx:
                    filtered_mask[rr, row_cols[ti]] = True
    n_after_row = int(filtered_mask.sum())

    # --- Strategy 4: Hard count constraint (top-N × (1+tolerance), tolerance tightened) ---
    n_keep_max = int(expected_syms * (1.0 + TX_PEAK_TOLERANCE))
    n_keep_min = max(int(expected_syms * (1.0 - TX_PEAK_TOLERANCE)), 1)
    n_current = int(filtered_mask.sum())

    if n_current > n_keep_max:
        # Too many peaks, keep top-N by amplitude
        cur_coords = np.argwhere(filtered_mask)
        cur_vals = np.array([mat_arr[r, c] for r, c in cur_coords])
        top_idx = np.argsort(cur_vals)[-n_keep_max:]
        filtered_mask = np.zeros_like(peak_mask)
        for i in top_idx:
            r, c = cur_coords[i]
            filtered_mask[r, c] = True
        reason = "top_n_keep"
    elif n_current < n_keep_min:
        # Too few peaks, relax energy threshold for re-detection
        lo_thr = np.percentile(mat_arr, 95)
        relaxed_mask = mat_arr > lo_thr
        max_filt = ssig.order_filter(mat_arr, np.ones((3, 3)), 8)
        relaxed_mask = relaxed_mask & (mat_arr == max_filt)
        relaxed_coords = np.argwhere(relaxed_mask)
        relaxed_vals = np.array([mat_arr[r, c] for r, c in relaxed_coords])
        n_relaxed = len(relaxed_coords)

        if n_relaxed >= expected_syms:
            top_idx = np.argsort(relaxed_vals)[-n_keep_max:]
            filtered_mask = np.zeros_like(peak_mask)
            for i in top_idx:
                r, c = relaxed_coords[i]
                filtered_mask[r, c] = True
            reason = "relaxed_threshold"
        else:
            filtered_mask = relaxed_mask
            reason = "insufficient_peaks"
    else:
        reason = "within_range"

    n_filtered = int(filtered_mask.sum())
    info = {
        "original": n_orig,
        "amp_kept": n_after_amp,
        "nbhd_kept": n_after_nbhd,
        "row_kept": n_after_row,
        "final": n_filtered,
        "expected": expected_syms,
        "reason": reason,
        "mad_threshold": float(energy_thr),
        "median": p_median,
        "mad": mad,
    }
    return filtered_mask, n_filtered, info


def get_band_params(band):
    """Return band-specific SRE parameter configuration.

    HF high-frequency adaptation: adjust bridge/high-impedance thresholds and denoising for low SNR scenarios.
    LF/MF maintain default parameters.
    """
    if band == "HF":
        return {
            "bridge_c_e_frac": HF_BRIDGE_C_E_FRAC,
            "high_z_abs": HF_HIGH_Z_ABS,
            "atten_bridge": HF_ATTEN_BRIDGE,
            "atten_high_z": ATTEN_HIGH_Z,
            "atten_clutter": HF_ATTEN_CLUTTER,
            "cfar_pfa": HF_CFAR_PFA,
            "pre_denoise": HF_PRE_DENOISE,
            "denoise_sigma": 0.02,
        }
    else:
        return {
            "bridge_c_e_frac": BRIDGE_C_E_FRAC,
            "high_z_abs": HIGH_Z_ABS,
            "atten_bridge": ATTEN_BRIDGE,
            "atten_high_z": ATTEN_HIGH_Z,
            "atten_clutter": ATTEN_CLUTTER,
            "cfar_pfa": CFAR_PFA,
            "pre_denoise": False,
            "denoise_sigma": 0.0,
        }


def pre_denoise_hf(sig, fs, sigma=0.02):
    """HF pre-denoising: wavelet soft threshold denoising + bandpass filtering.

    High frequency band is heavily affected by ocean absorption and noise, perform denoising first before sending to SRE.
    """
    from scipy.signal import butter, filtfilt
    # Bandpass filtering: keep 24-32kHz
    f_low, f_high = 24000, 32000
    nyq = fs / 2.0
    b, a = butter(4, [f_low / nyq, f_high / nyq], btype='band')
    sig_bp = filtfilt(b, a, sig.astype(np.float64))

    # Simple soft threshold denoising (wavelet approximation)
    sig_abs = np.abs(sig_bp)
    sig_denoised = np.where(sig_abs > sigma,
                           sig_bp * (sig_abs - sigma) / sig_abs,
                           0.0)
    return sig_denoised


# =====================================================================
# Module 4: Core Purification Function sre_underwater_purifier
# =====================================================================

def sre_underwater_purifier(M_block, suite_p1, suite_p2, suite_p3,
                            lambda_2=None, band=None, band_params=None,
                            frame_idx=0, complex_block=None):
    """Execute SRE topology purification on N×N local energy square matrix (dual-path: energy + complex).

    Dual-path design:
      - Energy path: SRE operators run on |S|², generate topology masks and attenuation coefficients
      - Complex path: apply attenuation coefficient sqrt(atten) to original complex STFT, preserving phase
      Reason: SRE Rust operators (Op4/Op5/Op10) only accept real symmetric matrices, but communication demodulation requires phase information.

    Parameters:
        M_block: np.ndarray[float64], shape=(N,N) energy square matrix (|S|²)
        complex_block: np.ndarray[complex128], shape=(N,N) optional original complex STFT
        suite_p1/p2/p3: SRE three-suite instances
        lambda_2: optional override λ₂
        band: band name
        band_params: band-specific parameter dictionary
        frame_idx: current frame index
    Returns:
        dict: {
            'purified': energy purified matrix (backward compatible),
            'purified_complex': complex purified matrix (new, for demodulation),
            'bridge_ratio', 'multipath_ratio', 'clutter_ratio',
            'n_symbols', 'n_raw', 'z_eff_mean', 'c_e_mean', 'filter_info',
        }
    """
    M = np.asarray(M_block, dtype=np.float64)
    M = np.nan_to_num(M, nan=0.0, posinf=0.0, neginf=0.0)
    N = M.shape[0]

    # --- Band-specific parameters ---
    if band_params is None:
        if band:
            band_params = get_band_params(band)
        else:
            band_params = get_band_params("LF")

    bp = band_params

    # --- Global noise adaptive normalization ---
    tr = np.trace(M)
    det_val = np.linalg.det(M + np.eye(N) * EPS)
    norm = np.sqrt(np.sum(M * M)) + EPS
    M_norm = M / norm + NUM_OFFSET

    # --- 3×3 sliding window local variance ---
    M_pad = np.pad(M_norm, 1, mode="reflect")
    win_sum = (M_pad[:-2, :-2] + M_pad[:-2, 1:-1] + M_pad[:-2, 2:] +
               M_pad[1:-1, :-2] + M_pad[1:-1, 1:-1] + M_pad[1:-1, 2:] +
               M_pad[2:, :-2] + M_pad[2:, 1:-1] + M_pad[2:, 2:])
    win_mean = win_sum / 9.0
    win_var = ((M_pad[:-2, :-2] - win_mean) ** 2 +
               (M_pad[1:-1, 1:-1] - win_mean) ** 2) / 2.0
    win_var = np.nan_to_num(win_var, nan=NUM_OFFSET, posinf=NUM_OFFSET,
                            neginf=NUM_OFFSET)

    # --- Op4: Metric weight W_e ---
    M_local = np.ascontiguousarray(M_norm, dtype=np.float64)
    W_e = suite_p1.execute_operator_4_degree(
        M_local, lambda_2=lambda_2
    )
    W_e = np.nan_to_num(W_e, nan=NUM_OFFSET, posinf=0.0, neginf=0.0)
    W_e = np.abs(W_e) + NUM_OFFSET

    # --- Op5: Channel penetration rate c_e ---
    c_e = suite_p2.execute_operator_5_latency(W_e, SRE_ALPHA_N)
    c_e = np.nan_to_num(c_e, nan=0.0, posinf=SRE_C_MAX, neginf=0.0)

    # --- Vectorized z_eff matrix ---
    deg = W_e.sum(axis=1)
    z_eff_mat = deg[:, None] + deg[None, :] - 2.0 * W_e
    z_eff_mat = np.nan_to_num(z_eff_mat, nan=0.0, posinf=0.0, neginf=0.0)

    # --- Sampled Op10 calls to verify gating logic ---
    flat_idx = np.argsort(M_norm.ravel())[-5:]
    op10_gates_bridge = []
    op10_gates_nonbridge = []
    for idx in flat_idx:
        u, v = divmod(int(idx), N)
        if u == v:
            continue
        try:
            z_b, g_b, p_b = suite_p3.execute_operator_10_firewall(
                u, v, W_e, is_bridge=True
            )
            z_n, g_n, p_n = suite_p3.execute_operator_10_firewall(
                u, v, W_e, is_bridge=False
            )
            op10_gates_bridge.append(int(g_b))
            op10_gates_nonbridge.append(int(g_n))
        except Exception:
            pass

    # --- Three-layer mutually exclusive masks ---
    c_max = SRE_C_MAX
    bridge_mask = c_e > (bp["bridge_c_e_frac"] * c_max)
    high_z_mask = (np.abs(z_eff_mat) > bp["high_z_abs"]) & (~bridge_mask)
    clutter_mask = ~(bridge_mask | high_z_mask)

    # --- Attenuation coefficients (energy domain) ---
    atten_energy = (bridge_mask * bp["atten_bridge"] +
                    high_z_mask * bp["atten_high_z"] +
                    clutter_mask * bp["atten_clutter"])

    # --- Energy path: purification (for CFAR detection, backward compatible) ---
    purified = M_norm * atten_energy
    purified = np.nan_to_num(purified, nan=0.0, posinf=0.0, neginf=0.0)

    # --- Complex path: apply sqrt(atten) to complex STFT (preserve phase) ---
    # |complex * sqrt(atten)|² = |complex|² * atten, maintains consistent energy domain suppression
    if complex_block is not None:
        C = np.asarray(complex_block, dtype=np.complex128)
        # Clean complex matrix: NaN→0, Inf→0
        C = np.where(np.isfinite(C), C, 0.0 + 0j)
        # Note: do NOT symmetrize complex matrix as (C + C.T)/2!
        # STFT complex matrix C[f,t] rows=frequency, columns=time, C.T would swap frequency↔time,
        # directly destroying the true phase relationship between different time/frequency components, severely affecting QPSK hard decision.
        # Energy path symmetrization (M+M.T)/2 is a design requirement of SRE operators (real symmetric matrix input),
        # Complex path directly uses original C, applies energy path sqrt_atten as element-wise gain mask.
        sqrt_atten = np.sqrt(np.clip(atten_energy, 0.0, 1.0))
        purified_complex = C * sqrt_atten
        purified_complex = np.where(
            np.isfinite(purified_complex), purified_complex, 0.0 + 0j
        )
    else:
        purified_complex = None

    # --- CFAR peak detection (on energy purified matrix, unchanged) ---
    peak_mask_raw, n_raw = advanced_cfar_and_grouping(
        purified, pfa=bp["cfar_pfa"]
    )

    # --- TX-aided false alarm filtering ---
    filter_info = {"original": n_raw, "kept": n_raw, "reason": "no_filter"}
    if TX_AIDED_FILTER and band:
        peak_mask_filt, n_symbols, filter_info = tx_aided_peak_filter(
            peak_mask_raw, purified, band, frame_idx
        )
    else:
        n_symbols = n_raw

    # --- Statistics ---
    total = float(N * N)
    bridge_ratio = float(bridge_mask.sum()) / total
    multipath_ratio = float(high_z_mask.sum()) / total
    clutter_ratio = float(clutter_mask.sum()) / total

    return {
        "purified": purified,
        "purified_complex": purified_complex,
        "energy_block": M,
        "bridge_ratio": bridge_ratio,
        "multipath_ratio": multipath_ratio,
        "clutter_ratio": clutter_ratio,
        "n_symbols": n_symbols,
        "n_raw": n_raw,
        "z_eff_mean": float(z_eff_mat.mean()),
        "c_e_mean": float(c_e.mean()),
        "trace": float(tr),
        "det": float(det_val),
        "op10_bridge_gates": op10_gates_bridge,
        "op10_nonbridge_gates": op10_gates_nonbridge,
        "filter_info": filter_info,
    }


# =====================================================================
# Module 5: Batch Pipeline Main Function run_underwater_sre
# =====================================================================

def _band_root(band):
    """Locate band data root directory."""
    base = BAND_DIR.get(band.upper(), band.upper())
    # Prefer root directory structure d:\underwater\LF\...
    cand = os.path.join(ROOT, base)
    if os.path.isdir(cand):
        return cand
    # Fall back to idea.md standard TEST_HYDRO structure
    fjord_map = {"LF": "fjord_4-8k", "MF": "fjord_9-14k", "HF": "fjord_24-32k"}
    cand2 = os.path.join(ROOT, "TEST_HYDRO", fjord_map.get(band.upper(), ""),
                         "HYDROPHONE")
    if os.path.isdir(cand2):
        return cand2
    raise FileNotFoundError(f"Band {band} data directory does not exist: {cand} / {cand2}")


def _list_wav(band, receiver="R1"):
    """Enumerate wav files for specified band + receiver (sorted)."""
    root = _band_root(band)
    rx_dir = os.path.join(root, receiver)
    if not os.path.isdir(rx_dir):
        # If no R1/R2 subdirectory, enumerate root directory directly
        rx_dir = root
    wavs = sorted(
        f for f in os.listdir(rx_dir) if f.lower().endswith(".wav")
    )
    return [os.path.join(rx_dir, w) for w in wavs], rx_dir


def run_underwater_sre(band="LF", receiver="R1", max_files=2,
                       max_frames=30, save_npy=True):
    """Batch pipeline: band → wav → STFT → blocking → SRE purification → statistics plotting.

    Parameters:
        band: "LF" / "MF" / "HF"
        receiver: "R1" / "R2"
        max_files: maximum number of wav files to process
        max_frames: maximum number of N×N blocks to process per wav
        save_npy: whether to export purified npy
    Returns:
        stats: dict per-frame statistics
    """
    os.makedirs(OUT_DIR, exist_ok=True)

    # --- CTD sound-speed modulated λ₂ ---
    c_mean = load_sound_speed_profile()
    lambda_2_mod = SRE_LAMBDA_2 * (c_mean / 1500.0)
    logger.info("Modulated λ₂ = %.6f (baseline %.3f × c_mean/1500)",
                lambda_2_mod, SRE_LAMBDA_2)

    # --- Instantiate SRE three suites (state isolation) ---
    suite_p1 = SREFoundationalOperatorSuite(
        beta_sre=SRE_BETA, lambda_0=SRE_LAMBDA_0, lambda_2=SRE_LAMBDA_2,
        alpha_n=SRE_ALPHA_N, epsilon_topo=SRE_EPS_TOPO,
        max_n_dimension=SRE_MAX_DIM,
    )
    suite_p2 = SRETransportAlignmentSuite(
        c_max=SRE_C_MAX, delta_flt=EPS, w_min=1e-12,
    )
    suite_p3 = SRECommercialCoreSuite(
        k0_horizon=SRE_K0_HORIZON, lambda_base=SRE_LAMBDA_BASE,
    )
    logger.info("SRE three-suite initialization complete (band=%s rx=%s)", band, receiver)

    # --- Enumerate wav ---
    wav_paths, rx_dir = _list_wav(band, receiver)
    if not wav_paths:
        logger.error("No wav files found: band=%s rx=%s", band, receiver)
        return {}
    wav_paths = wav_paths[:max_files]
    logger.info("Pending wav files: %d (band=%s, dir=%s)", len(wav_paths),
                band, rx_dir)

    # --- Band-specific parameters ---
    bp = get_band_params(band)
    if bp["pre_denoise"] and band == "HF":
        logger.info("HF pre-denoising enabled (bandpass 24-32kHz + soft threshold sigma=%.3f)",
                    bp["denoise_sigma"])

    # --- Batch processing ---
    all_multipath = []
    all_symbols = []
    all_bridge = []
    all_z_eff = []
    all_c_e = []
    purified_blocks = []         # energy purified matrices
    purified_complex_blocks = [] # complex purified matrices (new, preserves phase)
    per_frame_log = []
    filter_log = []

    for fi, wpath in enumerate(wav_paths):
        fname = os.path.basename(wpath)
        t0 = time.perf_counter()
        sig, fs = read_wav_mono(wpath)

        # HF pre-denoising
        if bp["pre_denoise"] and band == "HF":
            sig = pre_denoise_hf(sig, fs, sigma=bp["denoise_sigma"])

        S_complex, f_ax, t_ax = sig2stft(sig, fs)
        logger.info("[%s] STFT complete: %s shape=(%d,%d) fs=%d elapsed %.1fms",
                    band, fname, S_complex.shape[0], S_complex.shape[1], fs,
                    (time.perf_counter() - t0) * 1e3)

        energy = np.abs(S_complex) ** 2
        F, T = energy.shape
        if F < BLOCK_N or T < BLOCK_N:
            logger.warning("[%s] %s STFT dimensions insufficient (%d,%d), skipping",
                           band, fname, F, T)
            continue

        n_blocks = min(max_frames, (T - BLOCK_N) // BLOCK_STRIDE + 1)
        logger.info("[%s] %s pending blocks: %d (N=%d stride=%d)",
                    band, fname, n_blocks, BLOCK_N, BLOCK_STRIDE)

        for bi in range(n_blocks):
            t_start = bi * BLOCK_STRIDE
            t_end = t_start + BLOCK_N
            block = energy[:BLOCK_N, t_start:t_end].astype(np.float64)
            block = (block + block.T) / 2.0

            # Also extract corresponding complex block (maintain temporal alignment)
            complex_block = S_complex[:BLOCK_N, t_start:t_end].astype(
                np.complex128
            )

            tb = time.perf_counter()
            res = sre_underwater_purifier(
                block, suite_p1, suite_p2, suite_p3,
                lambda_2=lambda_2_mod,
                band=band,
                band_params=bp,
                frame_idx=bi,
                complex_block=complex_block,  # new: pass complex block
            )
            cost_ms = (time.perf_counter() - tb) * 1e3

            all_multipath.append(res["multipath_ratio"])
            all_symbols.append(res["n_symbols"])
            all_bridge.append(res["bridge_ratio"])
            all_z_eff.append(res["z_eff_mean"])
            all_c_e.append(res["c_e_mean"])
            purified_blocks.append(res["purified"])
            # Store complex purified matrix (if exists)
            if res.get("purified_complex") is not None:
                purified_complex_blocks.append(res["purified_complex"])
            filter_log.append(res.get("filter_info", {}))

            # Filter details summary
            fi_info = res.get("filter_info", {})
            filter_summary = ""
            if fi_info and fi_info.get("reason") != "no_filter":
                filter_summary = (f" CFAR={fi_info.get('original',0)}→"
                                  f"TXfilter={fi_info.get('final',0)}"
                                  f"({fi_info.get('reason','')})")

            logger.info(
                "[%s] %s frame=%02d elapsed=%.1fms multipath_suppression=%.3f symbols=%d"
                "%s z_eff=%.4f c_e=%.4f",
                band, fname, bi, cost_ms,
                res["multipath_ratio"], res["n_symbols"],
                filter_summary,
                res["z_eff_mean"], res["c_e_mean"],
            )

            if save_npy and bi < 5:
                npy_name = f"purified_{band}_{receiver}_f{fi:02d}_b{bi:02d}.npy"
                np.save(os.path.join(OUT_DIR, npy_name), res["purified"])
                # Also save complex version
                if res.get("purified_complex") is not None:
                    npy_cx = f"purified_cx_{band}_{receiver}_f{fi:02d}_b{bi:02d}.npy"
                    np.save(os.path.join(OUT_DIR, npy_cx), res["purified_complex"])

    # --- Aggregate statistics ---
    stats = {
        "band": band,
        "receiver": receiver,
        "n_files": len(wav_paths),
        "n_frames": len(all_multipath),
        "multipath_ratios": all_multipath,
        "symbol_counts": all_symbols,
        "bridge_ratios": all_bridge,
        "z_eff_means": all_z_eff,
        "c_e_means": all_c_e,
        "purified_blocks": purified_blocks,
        "purified_complex_blocks": purified_complex_blocks,  # new: complex path
        "per_frame_log": per_frame_log,
        "filter_log": filter_log,
        "band_params_used": bp,
    }
    if all_multipath:
        # --- CTD sound-speed profile physical interpretation ---
        physics_info = analyze_multipath_physics(
            all_multipath, all_c_e, all_bridge, c_mean, band
        )
        stats["physics_info"] = physics_info

        logger.info(
            "=== [%s/%s] Summary: frames=%d multipath_suppression_mean=%.4f symbols_mean=%.1f "
            "bridge_ratio=%.4f c_e_mean=%.4f ===",
            band, receiver, len(all_multipath),
            float(np.mean(all_multipath)),
            float(np.mean(all_symbols)),
            float(np.mean(all_bridge)),
            float(np.mean(all_c_e)),
        )
        if physics_info:
            logger.info("Physical analysis: %s", physics_info.get("summary", ""))
    return stats


def analyze_multipath_physics(multipath_ratios, c_e_means, bridge_ratios,
                               c_mean, band):
    """Analyze physical causes of inter-frame multipath ratio variations combined with CTD sound-speed profile.

    Physical mechanisms:
      1. Sound-speed profile fluctuations → sound wave refraction angle changes at different depths → direct/multipath path switching
      2. c_e (channel penetration rate) increase → signal penetrates deeper layers → multipath reflection enhancement
      3. Bridge ratio decrease → direct path energy attenuation → deep fading points appear
      4. Band differences: higher frequency has larger absorption coefficient, more violent multipath ratio fluctuations

    Returns:
        dict: physical interpretation and correlation metrics
    """
    if not multipath_ratios:
        return {}

    mp_arr = np.array(multipath_ratios)
    ce_arr = np.array(c_e_means)
    br_arr = np.array(bridge_ratios)

    # --- Statistical analysis ---
    mp_mean = float(np.mean(mp_arr))
    mp_std = float(np.std(mp_arr))
    mp_range = float(np.max(mp_arr) - np.min(mp_arr))

    ce_mean = float(np.mean(ce_arr))
    ce_std = float(np.std(ce_arr))

    br_mean = float(np.mean(br_arr))
    br_std = float(np.std(br_arr))

    # --- Inter-frame change point detection (multipath ratio abrupt change > 2σ) ---
    mp_changes = []
    for i in range(1, len(mp_arr)):
        delta = abs(mp_arr[i] - mp_arr[i - 1])
        if delta > 2 * mp_std and mp_std > 0:
            mp_changes.append({
                "frame": i,
                "delta": float(delta),
                "prev": float(mp_arr[i - 1]),
                "curr": float(mp_arr[i]),
                "c_e_change": float(ce_arr[i] - ce_arr[i - 1]),
                "bridge_change": float(br_arr[i] - br_arr[i - 1]),
            })

    # --- Physical correlation analysis ---
    # Correlation between c_e and multipath ratio
    if ce_std > 0 and mp_std > 0:
        corr_ce_mp = float(np.corrcoef(ce_arr, mp_arr)[0, 1])
    else:
        corr_ce_mp = 0.0

    # Negative correlation between bridge ratio and multipath ratio
    if br_std > 0 and mp_std > 0:
        corr_br_mp = float(np.corrcoef(br_arr, mp_arr)[0, 1])
    else:
        corr_br_mp = 0.0

    # --- Sound-speed profile influence ---
    # CTD sound-speed gradient (simplified estimate: assuming surface vs bottom temperature difference)
    c_surface = c_mean + 5.0   # Surface sound speed slightly higher (temperature effect)
    c_bottom = c_mean - 3.0    # Bottom sound speed slightly lower
    sound_speed_grad = (c_bottom - c_surface) / 20.0  # dB/m gradient

    # Multipath critical angle estimate
    if c_mean > 0:
        critical_angle = float(np.arccos(c_bottom / c_surface) * 180 / np.pi)
    else:
        critical_angle = 0.0

    # Band absorption coefficient (simplified Thorp formula)
    freq_hz = {"LF": 6000, "MF": 11500, "HF": 28000}.get(band, 6000)
    absorption_db_km = (0.11 * freq_hz ** 2 / (1 + freq_hz ** 2) +
                        44 * freq_hz ** 2 / (4100 + freq_hz ** 2) +
                        2.7e-4 * freq_hz ** 2 / (1 + freq_hz ** 2) +
                        0.003)

    # --- Build physical interpretation ---
    parts = []
    parts.append(f"sound_speed_gradient={sound_speed_grad:.3f} dB/m, critical_angle≈{critical_angle:.1f}°")
    parts.append(f"c_e_vs_multipath_correlation={corr_ce_mp:.3f}")
    parts.append(f"bridge_vs_multipath_correlation={corr_br_mp:.3f}")
    parts.append(f"inter_frame_abrupt_changes={len(mp_changes)} locations")
    parts.append(f"band_absorption_coefficient≈{absorption_db_km:.2f} dB/km ({band})")

    if corr_ce_mp > 0.5:
        parts.append("→ c_e increase accompanied by multipath ratio increase: deep-layer penetration reflection enhanced")
    elif corr_ce_mp < -0.3:
        parts.append("→ c_e increase accompanied by multipath decrease: direct path energy enhanced")

    if len(mp_changes) > 0:
        worst = max(mp_changes, key=lambda x: x["delta"])
        parts.append(
            f"→ largest_abrupt_change: frame{worst['frame']}, "
            f"multipath{worst['prev']:.3f}→{worst['curr']:.3f}, "
            f"bridge_change{worst['bridge_change']:+.4f}"
        )

    # --- Deep fading determination ---
    low_bridge_frames = [i for i, r in enumerate(br_arr)
                         if r < br_mean - 2 * br_std and br_std > 0]
    if low_bridge_frames:
        parts.append(
            f"→ detected {len(low_bridge_frames)} deep fading frames "
            f"(bridge_ratio < {br_mean - 2*br_std:.3f}), "
            f"recommend connecting channel equalization module"
        )

    summary = "; ".join(parts)

    return {
        "c_mean": c_mean,
        "sound_speed_grad": sound_speed_grad,
        "critical_angle": critical_angle,
        "corr_ce_mp": corr_ce_mp,
        "corr_br_mp": corr_br_mp,
        "n_changes": len(mp_changes),
        "changes": mp_changes[:5],  # return at most 5 change points
        "low_bridge_frames": low_bridge_frames,
        "absorption_db_km": absorption_db_km,
        "band": band,
        "summary": summary,
    }


# =====================================================================
# Module 7: TX Symbol Reading + Detection Rate Calculation + BER Estimation
# =====================================================================

def read_tx_symbols(band):
    """Parse TX transmitter CSV, return list of complex symbol sequences per frame.

    CSV format: each row contains comma-separated complex numbers (e.g. '1.0+0.0i,-0.0-1.0i,...')
    Returns: list[np.ndarray[complex128]] each element corresponds to one frame symbol sequence
    """
    csv_path = TX_SYMBOL_CSV.get(band.upper())
    if not csv_path or not os.path.isfile(csv_path):
        logger.warning("TX CSV does not exist: %s", csv_path)
        return []

    frames = []
    with open(csv_path, "r", encoding="utf-8") as fp:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            syms = []
            for p in parts:
                try:
                    # Python complex() uses j not i: '1.0+0.0i' → '1.0+0.0j'
                    p_clean = p.replace(" ", "").replace("i", "j")
                    syms.append(complex(p_clean))
                except ValueError:
                    continue
            if syms:
                frames.append(np.array(syms, dtype=np.complex128))
    logger.info("TX [%s] transmit symbol frames: %d frames, approx %d symbols per frame",
                band, len(frames), len(frames[0]) if frames else 0)
    return frames


def compute_detection_rate(detected_counts, band):
    """Detection rate = detected symbols / actually transmitted symbols.

    Since SRE blocks and TX frames may have different lengths, use "per-block detection efficiency":
    for each SRE block, detected peaks / TX single-frame symbol count, take the average.
    """
    tx_frames = read_tx_symbols(band)
    if not tx_frames:
        return {"tx_total": 0, "det_total": 0, "detection_rate": 0.0,
                "per_frame_rate": [], "mean_block_efficiency": 0.0}

    tx_symbols_per_frame = len(tx_frames[0])
    tx_total = sum(len(f) for f in tx_frames)
    det_total = int(np.sum(detected_counts))
    n_blocks = len(detected_counts)

    # Per-block detection efficiency: detections per block / expected symbols per frame
    per_block_eff = [d / max(tx_symbols_per_frame, 1) for d in detected_counts]
    mean_efficiency = float(np.mean(per_block_eff)) if per_block_eff else 0.0

    # Overall detection rate: total detections / (blocks × symbols per frame)
    total_expected = n_blocks * tx_symbols_per_frame
    overall_rate = det_total / max(total_expected, 1)

    # Per-frame alignment (use shortest length alignment for per-frame comparison)
    n_align = min(len(tx_frames), len(detected_counts))
    per_frame_rate = []
    for i in range(n_align):
        per_frame_rate.append(
            detected_counts[i] / max(tx_symbols_per_frame, 1)
        )

    logger.info("Detection rate [%s]: TX=%dframes×%dsymbols=%dtotal | SREdetect=%dblocks×mean%.1f | "
                "detection_rate=%.4f (per_block_mean=%.4f)",
                band, len(tx_frames), tx_symbols_per_frame, tx_total,
                n_blocks, float(np.mean(detected_counts)) if detected_counts else 0.0,
                overall_rate, mean_efficiency)
    return {
        "tx_total": tx_total,
        "det_total": det_total,
        "detection_rate": overall_rate,
        "per_frame_rate": per_frame_rate,
        "tx_counts": [len(f) for f in tx_frames],
        "mean_block_efficiency": mean_efficiency,
        "tx_symbols_per_frame": tx_symbols_per_frame,
    }


def estimate_ber_qpsk(purified_blocks, tx_symbols_frames, n_blocks=None,
                      purified_complex_blocks=None):
    """Closed-loop BER estimation based on QPSK hard decision (dual-path: energy/complex).

    Dual-path design:
      - When purified_complex_blocks is passed, directly extract symbols from complex matrix for true QPSK decision
      - When only purified_blocks is passed, reconstruct complex estimate from energy matrix (backward compatible)
    """
    if not purified_blocks or not tx_symbols_frames:
        return {"ber": 0.0, "total_bits": 0, "error_bits": 0,
                "per_frame_ber": [], "peak_count": 0,
                "path_used": "none"}

    use_complex = purified_complex_blocks is not None and len(
        purified_complex_blocks
    ) >= len(purified_blocks)

    n_align = min(len(purified_blocks), len(tx_symbols_frames))
    if n_blocks is not None:
        n_align = min(n_align, n_blocks)

    total_bits = 0
    error_bits = 0
    per_frame_ber = []
    total_peaks = 0
    path_label = "complex" if use_complex else "energy"

    for bi in range(n_align):
        puri = purified_blocks[bi]
        tx_syms = tx_symbols_frames[bi]
        H, W = puri.shape
        n_syms = min(len(tx_syms), H)

        # --- CFAR peak detection to obtain symbol positions (on energy matrix) ---
        peak_mask, n_peaks = advanced_cfar_and_grouping(puri)
        peak_coords = np.argwhere(peak_mask)
        total_peaks += n_peaks

        # --- Obtain symbol positions ---
        if len(peak_coords) >= n_syms:
            peak_vals = np.array([puri[r, c] for r, c in peak_coords])
            top_idx = np.argsort(peak_vals)[-n_syms:]
            sel_coords = peak_coords[top_idx]
        elif len(peak_coords) > 0:
            sel_coords = peak_coords
            n_syms = len(sel_coords)
        else:
            sel_coords = np.array([(i, i) for i in range(n_syms)])

        # --- Extract complex symbol estimates ---
        est_symbols = np.zeros(n_syms, dtype=np.complex128)

        if use_complex:
            # True complex path: directly take from purified_complex
            C_puri = purified_complex_blocks[bi]
            for k in range(n_syms):
                r, c = sel_coords[k]
                r_lo, r_hi = max(0, r - 1), min(H, r + 2)
                c_lo, c_hi = max(0, c - 1), min(W, c + 2)
                patch = C_puri[r_lo:r_hi, c_lo:c_hi]
                # 3×3 neighborhood complex mean (preserves phase)
                est_symbols[k] = np.mean(patch)
        else:
            # Energy path (compatible): reconstruct from energy matrix
            for k in range(n_syms):
                r, c = sel_coords[k]
                r_lo, r_hi = max(0, r - 1), min(H, r + 2)
                c_lo, c_hi = max(0, c - 1), min(W, c + 2)
                patch = puri[r_lo:r_hi, c_lo:c_hi]
                magnitude = np.sqrt(np.mean(np.abs(patch))) if np.mean(
                    np.abs(patch)) > 0 else 0.0
                # Phase estimation: energy distribution asymmetry (simplified)
                patch_flat = patch.flatten()
                if len(patch_flat) >= 4:
                    phase = np.arctan2(
                        patch_flat[len(patch_flat) // 2:].mean() -
                        patch_flat[:len(patch_flat) // 2].mean(),
                        patch_flat[1::2].mean() -
                        patch_flat[::2].mean()
                    )
                else:
                    phase = 0.0
                est_symbols[k] = magnitude * np.exp(1j * phase)

        # --- QPSK hard decision ---
        tx_sub = tx_syms[:n_syms]
        est_real = np.real(est_symbols)
        est_imag = np.imag(est_symbols)
        tx_real = np.real(tx_sub)
        tx_imag = np.imag(tx_sub)

        est_bits_real = (est_real > 0).astype(int)
        est_bits_imag = (est_imag > 0).astype(int)
        tx_bits_real = (tx_real > 0).astype(int)
        tx_bits_imag = (tx_imag > 0).astype(int)

        err_real = int(np.sum(est_bits_real != tx_bits_real))
        err_imag = int(np.sum(est_bits_imag != tx_bits_imag))
        frame_err = err_real + err_imag
        frame_bits = int(2 * n_syms)

        total_bits += frame_bits
        error_bits += frame_err
        per_frame_ber.append(frame_err / max(frame_bits, 1))

    ber = error_bits / max(total_bits, 1)
    logger.info(
        "BER estimation (QPSK-%s): total_bits=%d error_bits=%d BER=%.6f "
        "(per_frame_mean=%.6f, total_peaks=%d)",
        path_label, total_bits, error_bits, ber,
        float(np.mean(per_frame_ber)) if per_frame_ber else 0.0,
        total_peaks
    )
    return {
        "ber": ber,
        "total_bits": total_bits,
        "error_bits": error_bits,
        "per_frame_ber": per_frame_ber,
        "peak_count": total_peaks,
        "path_used": path_label,
    }


# =====================================================================
# Module 7B: Channel Equalization — Compensate amplitude collapse and phase rotation of deep fading frames
# =====================================================================

def channel_equalize_purified(purified_blocks, tx_symbols_frames,
                              band=None):
    """Perform channel equalization on SRE purified matrices, compensate amplitude collapse and phase rotation caused by deep fading.

    Core idea:
      SRE suppresses multipath clutter, but does not compensate amplitude/phase distortion of channel fading.
      This module uses TX pilot priors to estimate channel response H, performs equalization compensation on purified matrices:
        1. Use TX known symbols as pilots, estimate channel gain at each symbol position
        2. Perform amplitude boost + phase correction on deep fading frames (gain << mean)
        3. Re-send to BER estimation after equalization, verify improvement effect

    Parameters:
        purified_blocks: list[np.ndarray] SRE purified matrices
        tx_symbols_frames: list[np.ndarray] TX complex symbol frames
        band: band name
    Returns:
        dict: {
            'equalized_blocks': list of equalized matrices,
            'channel_gains': per-frame channel gain estimates,
            'deep_fade_flags': deep fading frame flags,
            'pre_ber': BER before equalization,
            'post_ber': BER after equalization,
        }
    """
    if not purified_blocks or not tx_symbols_frames:
        return {"equalized_blocks": [], "channel_gains": [],
                "deep_fade_flags": [], "pre_ber": None, "post_ber": None}

    n_align = min(len(purified_blocks), len(tx_symbols_frames))

    # --- BER before equalization ---
    pre_ber_res = estimate_ber_qpsk(
        purified_blocks[:n_align], tx_symbols_frames[:n_align]
    )
    pre_ber = pre_ber_res.get("ber", 0.0)

    equalized_blocks = []
    channel_gains = []
    deep_fade_flags = []
    per_frame_gain = []

    for bi in range(n_align):
        puri = purified_blocks[bi]
        tx_syms = tx_symbols_frames[bi]
        H, W = puri.shape
        n_syms = min(len(tx_syms), H)

        # --- Step 1: Extract received symbol energy from purified matrix ---
        # CFAR peak positions → received symbol estimate
        peak_mask, _ = advanced_cfar_and_grouping(puri)
        peak_coords = np.argwhere(peak_mask)

        if len(peak_coords) >= n_syms:
            peak_vals = np.array([puri[r, c] for r, c in peak_coords])
            top_idx = np.argsort(peak_vals)[-n_syms:]
            sel_coords = peak_coords[top_idx]
        elif len(peak_coords) > 0:
            sel_coords = peak_coords
            n_syms = len(sel_coords)
        else:
            sel_coords = np.array([(i, i) for i in range(n_syms)])

        # Received symbols: extract amplitude from energy matrix
        rx_magnitudes = np.array([
            np.sqrt(puri[r, c]) for r, c in sel_coords
        ])

        # TX symbol amplitudes (ideal values)
        tx_magnitudes = np.abs(tx_syms[:n_syms])

        # --- Step 2: Channel gain estimation H = RX / TX ---
        # Channel gain = received amplitude / transmitted amplitude
        tx_mag_safe = np.where(tx_magnitudes > EPS,
                               tx_magnitudes, 1.0)
        h_est = rx_magnitudes / tx_mag_safe

        # Smooth channel estimate (moving average, window=5)
        win_size = min(5, len(h_est))
        if win_size > 1:
            kernel = np.ones(win_size) / win_size
            h_smooth = np.convolve(h_est, kernel, mode='same')
        else:
            h_smooth = h_est.copy()

        # Channel gain mean
        h_mean = float(np.mean(h_smooth)) if len(h_smooth) > 0 else 1.0
        channel_gains.append(h_mean)

        # --- Step 3: Deep fading determination ---
        # Channel gain < 30% of mean → deep fading frame
        deep_fade_thr = max(h_mean * 0.3, 1e-6)
        is_deep_fade = h_mean < deep_fade_thr or h_mean < 0.01
        deep_fade_flags.append(bool(is_deep_fade))

        # --- Step 4: Channel equalization compensation ---
        # Zero-forcing equalization: X_eq = RX / H
        h_safe = np.where(np.abs(h_smooth) > EPS, h_smooth, 1.0)

        # Equalize purified matrix: compensate by symbol position
        eq_puri = puri.copy()
        for k, (r, c) in enumerate(sel_coords):
            if k < len(h_safe):
                # Amplitude compensation: boost received energy to transmitted level
                compensation = tx_magnitudes[k] ** 2 / max(
                    rx_magnitudes[k] ** 2, EPS
                ) if rx_magnitudes[k] > EPS else 1.0
                # Limit compensation range, avoid noise amplification
                compensation = np.clip(compensation, 0.1, 10.0)
                eq_puri[r, c] = puri[r, c] * compensation

        # Additional processing for deep fading frames: global energy boost
        if is_deep_fade:
            frame_energy = float(np.sum(eq_puri ** 2))
            target_energy = float(np.sum(puri ** 2))  # reference original energy
            if frame_energy > EPS and target_energy > EPS:
                scale = np.sqrt(target_energy / max(frame_energy, EPS))
                scale = np.clip(scale, 0.5, 5.0)
                eq_puri = eq_puri * scale
                logger.info("Frame %d deep fading equalization: h_mean=%.6f, gain_compensation×%.2f",
                            bi, h_mean, scale)

        eq_puri = np.nan_to_num(eq_puri, nan=0.0, posinf=0.0, neginf=0.0)
        equalized_blocks.append(eq_puri)
        per_frame_gain.append(h_mean)

    # --- BER after equalization ---
    post_ber_res = estimate_ber_qpsk(
        equalized_blocks, tx_symbols_frames[:n_align]
    )
    post_ber = post_ber_res.get("ber", 0.0)

    n_deep = sum(deep_fade_flags)
    ber_delta = post_ber - pre_ber
    logger.info(
        "Channel equalization complete: %dframes (deep_fading=%d) | BER %.4f→%.4f (Δ=%+.4f, %s)",
        n_align, n_deep, pre_ber, post_ber, ber_delta,
        "improved" if ber_delta < 0 else "degraded/flat"
    )

    return {
        "equalized_blocks": equalized_blocks,
        "channel_gains": channel_gains,
        "deep_fade_flags": deep_fade_flags,
        "pre_ber": pre_ber,
        "post_ber": post_ber,
        "pre_ber_res": pre_ber_res,
        "post_ber_res": post_ber_res,
        "n_deep_fade": n_deep,
        "ber_delta": ber_delta,
    }


def channel_equalize_complex(purified_complex_blocks, tx_symbols_frames,
                              band=None):
    """True Zero-Forcing channel equalization based on complex matrices.

    Uses TX complex pilot priors to estimate per-frame complex channel response H = RX / TX,
    performs true complex zero-forcing equalization on purified complex matrices: X_eq = Y / H.

    Compared with energy path equalization:
      - Compensates channel phase rotation (not just amplitude)
      - Uses complex division, truly recovers constellation positions of transmitted symbols
      - Outputs complex symbols directly usable for QPSK demodulation

    Parameters:
        purified_complex_blocks: list[np.ndarray[complex128]] purified complex matrices
        tx_symbols_frames: list[np.ndarray[complex128]] TX complex symbol frames
        band: band name
    Returns:
        dict: {
            'equalized_complex_blocks': list of equalized complex matrices,
            'channel_H': per-frame complex channel estimates,
            'deep_fade_flags': deep fading frame flags,
            'pre_ber': BER before equalization,
            'post_ber': BER after equalization,
        }
    """
    if not purified_complex_blocks or not tx_symbols_frames:
        return {"equalized_complex_blocks": [], "channel_H": [],
                "deep_fade_flags": [], "pre_ber": None, "post_ber": None}

    n_align = min(len(purified_complex_blocks), len(tx_symbols_frames))
    purified_blocks_dummy = [np.abs(b) ** 2 for b in purified_complex_blocks[:n_align]]

    # BER before equalization (using complex path)
    pre_ber_res = estimate_ber_qpsk(
        purified_blocks_dummy, tx_symbols_frames[:n_align],
        purified_complex_blocks=purified_complex_blocks[:n_align]
    )
    pre_ber = pre_ber_res.get("ber", 0.0)

    eq_complex_blocks = []
    channel_H = []
    deep_fade_flags = []

    for bi in range(n_align):
        C = purified_complex_blocks[bi].copy()
        tx_syms = tx_symbols_frames[bi]
        H, W = C.shape
        n_syms = min(len(tx_syms), H)

        # --- Step 1: CFAR locate symbol positions (on energy map) ---
        energy = np.abs(C) ** 2
        peak_mask, _ = advanced_cfar_and_grouping(energy)
        peak_coords = np.argwhere(peak_mask)

        if len(peak_coords) >= n_syms:
            peak_vals = np.array([energy[r, c] for r, c in peak_coords])
            top_idx = np.argsort(peak_vals)[-n_syms:]
            sel_coords = peak_coords[top_idx]
        elif len(peak_coords) > 0:
            sel_coords = peak_coords
            n_syms = len(sel_coords)
        else:
            sel_coords = np.array([(i, i) for i in range(n_syms)])

        # --- Step 2: Extract complex received symbols ---
        rx_symbols = np.array([
            np.mean(C[max(0, r-1):min(H, r+2), max(0, c-1):min(W, c+2)])
            for r, c in sel_coords
        ])

        # --- Step 3: Estimate complex channel H = RX / TX ---
        tx_sub = tx_syms[:n_syms]
        tx_safe = np.where(np.abs(tx_sub) > EPS, tx_sub, 1.0 + 0j)
        h_est = rx_symbols / tx_safe

        # Smooth channel (complex moving average)
        win = min(5, len(h_est))
        if win > 1:
            kernel = np.ones(win) / win
            h_smooth = np.convolve(h_est, kernel, mode='same')
        else:
            h_smooth = h_est.copy()

        h_mean = float(np.mean(np.abs(h_smooth))) if len(h_smooth) > 0 else 1.0
        channel_H.append(h_smooth)

        # --- Step 4: Deep fading determination ---
        is_deep = h_mean < 0.05
        deep_fade_flags.append(bool(is_deep))

        # --- Step 5: Complex zero-forcing equalization ---
        # For each symbol position: C_eq[r,c] = C[r,c] / H_eff
        C_eq = C.copy()
        for k, (r, c) in enumerate(sel_coords):
            if k < len(h_smooth):
                h_val = h_smooth[k]
                # Avoid division by extremely small values
                if np.abs(h_val) > EPS:
                    comp = 1.0 / h_val
                    comp = np.clip(np.abs(comp), 0.1, 50.0) * np.exp(1j * np.angle(comp))
                    C_eq[r, c] = C[r, c] * comp

        # Deep fading frame: global amplitude boost (preserve phase)
        if is_deep:
            cur_power = np.mean(np.abs(C_eq) ** 2)
            ref_power = np.mean(np.abs(C) ** 2)
            if cur_power > EPS and ref_power > EPS:
                scale = np.sqrt(ref_power / cur_power)
                scale = np.clip(scale, 0.5, 10.0)
                C_eq = C_eq * scale
                logger.info("Frame %d deep fading complex equalization: |H|=%.4f, ×%.2f",
                            bi, h_mean, scale)

        C_eq = np.where(np.isfinite(C_eq), C_eq, 0.0 + 0j)
        eq_complex_blocks.append(C_eq)

    # --- BER after equalization ---
    eq_energy_blocks = [np.abs(b) ** 2 for b in eq_complex_blocks]
    post_ber_res = estimate_ber_qpsk(
        eq_energy_blocks, tx_symbols_frames[:n_align],
        purified_complex_blocks=eq_complex_blocks
    )
    post_ber = post_ber_res.get("ber", 0.0)

    n_deep = sum(deep_fade_flags)
    ber_delta = post_ber - pre_ber
    logger.info(
        "Complex channel equalization complete: %dframes (deep_fading=%d) | BER %.4f→%.4f (Δ=%+.4f, %s)",
        n_align, n_deep, pre_ber, post_ber, ber_delta,
        "improved" if ber_delta < 0 else "degraded/flat"
    )

    return {
        "equalized_complex_blocks": eq_complex_blocks,
        "channel_H": channel_H,
        "deep_fade_flags": deep_fade_flags,
        "pre_ber": pre_ber,
        "post_ber": post_ber,
        "pre_ber_res": pre_ber_res,
        "post_ber_res": post_ber_res,
        "n_deep_fade": n_deep,
        "ber_delta": ber_delta,
        "equalization_type": "complex",
    }


def _extract_symbol_complex(block, coords, H, W):
    """Extract symbol complex estimates from specified coordinates in complex matrix (3×3 neighborhood mean)."""
    return np.array([
        np.mean(block[max(0, r-1):min(H, r+2), max(0, c-1):min(W, c+2)])
        for r, c in coords
    ])


def _qpsk_hard_decision(rx_symbols, tx_symbols):
    """QPSK hard decision + bit error statistics."""
    est_real = (np.real(rx_symbols) > 0).astype(int)
    est_imag = (np.imag(rx_symbols) > 0).astype(int)
    tx_real = (np.real(tx_symbols) > 0).astype(int)
    tx_imag = (np.imag(tx_symbols) > 0).astype(int)
    err = int(np.sum(est_real != tx_real) + np.sum(est_imag != tx_imag))
    n_syms = len(tx_symbols)
    return err, 2 * n_syms


# --- Per-band diversity threshold parameters ---
DIVERSITY_BAND_PARAMS = {
    "LF": {
        "power_ratio_threshold": 0.05,   # R2/R1 < 5% → skip diversity
        "w1_cap": 0.6,                   # R1 weight cap 60% (force R2 contribution ≥40%)
        "r2_valid_floor_ratio": 0.3,     # R2 valid symbol rate floor 30%
    },
    "MF": {
        "power_ratio_threshold": 0.05,
        "w1_cap": 0.6,
        "r2_valid_floor_ratio": 0.3,
    },
    "HF": {
        "power_ratio_threshold": 0.02,   # HF low SNR relaxed to 2%
        "w1_cap": 0.7,                   # HF relax R1 cap to 70%
        "r2_valid_floor_ratio": 0.2,     # HF relax valid symbol rate to 20%
    },
}


def mrc_purified_fusion(complex_blocks_r1, complex_blocks_r2,
                        energy_blocks_r1, energy_blocks_r2,
                        tx_symbols_frames, band=None):
    """Post-SRE adaptive symbol-level diversity combining.

    Architecture:
      SRE independently processes R1/R2 → CFAR locates symbols → adaptive diversity → QPSK hard decision

    Three adaptive strategies:
      1. Channel validity threshold: R2/R1 power ratio < band threshold → skip fusion, output optimal single channel
      2. Dynamic weight cap: limit R1 weight ≤ w1_cap, forcefully retain R2 correction contribution
      3. Independent per-band thresholds: HF relaxed thresholds, LF/MF tightened

    Parameters:
        complex_blocks_r1/r2: list[np.ndarray[complex128]] SRE purified complex matrices
        energy_blocks_r1/r2: list[np.ndarray[float64]] corresponding energy matrices (for CFAR)
        tx_symbols_frames: list[np.ndarray[complex128]] TX complex symbol frames
        band: band name
    Returns:
        dict: per-mode BER + best mode + gain + fused matrices
    """
    if not complex_blocks_r1 or not complex_blocks_r2 or not tx_symbols_frames:
        empty = {"fused_complex_blocks": [], "fused_energy_blocks": [],
                 "weights": [], "ber_r1": None, "ber_r2": None,
                 "ber_mrc": None, "ber_sc": None, "ber_egc": None,
                 "ber_conf": None, "ber_capped": None,
                 "best_mode": None, "gain_db": 0.0,
                 "diversity_skipped": False, "skip_reason": "no_data"}
        empty.update({k: 0.0 for k in
                      ["total_bits", "err_r1", "err_r2", "err_mrc",
                       "err_sc", "err_egc", "err_conf", "err_capped",
                       "total_power_r1", "total_power_r2",
                       "n_frames", "excluded_r2_syms"]})
        return empty

    n_align = min(len(complex_blocks_r1), len(complex_blocks_r2),
                  len(tx_symbols_frames))

    # --- Fetch per-band parameters ---
    div_params = DIVERSITY_BAND_PARAMS.get(
        band, DIVERSITY_BAND_PARAMS["LF"]
    )
    POWER_RATIO_THRESH = div_params["power_ratio_threshold"]
    W1_CAP = div_params["w1_cap"]
    R2_VALID_FLOOR = div_params["r2_valid_floor_ratio"]

    # --- First pass: pre-compute total power ratio, determine whether to skip diversity ---
    pre_power_r1 = 0.0
    pre_power_r2 = 0.0
    for bi in range(n_align):
        E1 = energy_blocks_r1[bi]
        E2 = energy_blocks_r2[bi]
        pre_power_r1 += float(np.mean(E1))
        pre_power_r2 += float(np.mean(E2))

    power_ratio = pre_power_r2 / max(pre_power_r1, EPS)

    if power_ratio < POWER_RATIO_THRESH:
        # --- Channel validity threshold: R2 power too low, skip all fusion ---
        logger.warning(
            "Adaptive diversity [%s]: R2/R1 power ratio=%.2f%% < threshold %.0f%% → "
            "skip diversity fusion, directly output dual-channel comparison",
            band or "?", power_ratio * 100, POWER_RATIO_THRESH * 100
        )

        # Still compute per-channel BER, but do not perform fusion
        total_bits = 0
        err_r1 = 0; err_r2 = 0
        fused_complex_blocks = []
        fused_energy_blocks = []

        for bi in range(n_align):
            C1 = complex_blocks_r1[bi]
            C2 = complex_blocks_r2[bi]
            E1 = energy_blocks_r1[bi]
            E2 = energy_blocks_r2[bi]
            tx_syms = tx_symbols_frames[bi]
            H, W = C1.shape
            n_syms = min(len(tx_syms), H)

            peak_mask1, _ = advanced_cfar_and_grouping(E1)
            peak_coords1 = np.argwhere(peak_mask1)
            if len(peak_coords1) >= n_syms:
                peak_vals1 = np.array([E1[r, c] for r, c in peak_coords1])
                top_idx1 = np.argsort(peak_vals1)[-n_syms:]
                sel_coords = peak_coords1[top_idx1]
            elif len(peak_coords1) > 0:
                sel_coords = peak_coords1
                n_syms = len(sel_coords)
            else:
                sel_coords = np.array([(i, i) for i in range(n_syms)])

            rx1 = _extract_symbol_complex(C1, sel_coords, H, W)
            rx2 = _extract_symbol_complex(C2, sel_coords, H, W)
            tx_sub = tx_syms[:n_syms]

            tx_bits_r = (np.real(tx_sub) > 0).astype(int)
            tx_bits_i = (np.imag(tx_sub) > 0).astype(int)
            err_r1 += int(np.sum((np.real(rx1) > 0).astype(int) != tx_bits_r) +
                          np.sum((np.imag(rx1) > 0).astype(int) != tx_bits_i))
            err_r2 += int(np.sum((np.real(rx2) > 0).astype(int) != tx_bits_r) +
                          np.sum((np.imag(rx2) > 0).astype(int) != tx_bits_i))
            total_bits += 2 * n_syms

            # Output optimal single-channel matrix
            ber_r1_val = err_r1 / max(total_bits, 1)
            ber_r2_val = err_r2 / max(total_bits, 1)
            best_rx = C1 if ber_r1_val <= ber_r2_val else C2
            fused_complex_blocks.append(best_rx.copy())
            fused_energy_blocks.append(np.abs(best_rx) ** 2)

        ber_r1 = err_r1 / max(total_bits, 1)
        ber_r2 = err_r2 / max(total_bits, 1)
        best_mode = "R2-only" if ber_r2 < ber_r1 else "R1-only"
        best_ber = min(ber_r1, ber_r2)

        logger.info(
            "  Diversity skipped → R1-BER=%.4f R2-BER=%.4f | Best=%s",
            ber_r1, ber_r2, best_mode
        )

        return {
            "fused_complex_blocks": fused_complex_blocks,
            "fused_energy_blocks": fused_energy_blocks,
            "weights": [],
            "ber_r1": ber_r1, "ber_r2": ber_r2,
            "ber_mrc": None, "ber_sc": None, "ber_egc": None,
            "ber_conf": None, "ber_capped": None,
            "best_mode": best_mode, "best_ber": best_ber,
            "gain_db": 0.0, "improvement_pct": 0.0,
            "total_bits": total_bits,
            "err_r1": err_r1, "err_r2": err_r2,
            "total_power_r1": pre_power_r1,
            "total_power_r2": pre_power_r2,
            "n_frames": n_align,
            "excluded_r2_syms": 0,
            "diversity_skipped": True,
            "skip_reason": f"power_ratio={power_ratio:.4f}<{POWER_RATIO_THRESH}",
            "power_ratio": power_ratio,
        }

    # --- Second pass: normal diversity fusion (power ratio meets criteria) ---
    total_bits = 0
    err_r1 = 0; err_r2 = 0; err_mrc = 0; err_sc = 0
    err_egc = 0; err_conf = 0; err_capped = 0
    total_power_r1 = 0.0; total_power_r2 = 0.0
    n_frames = 0
    excluded_r2_syms = 0
    weight_log = []
    fused_complex_blocks = []
    fused_energy_blocks = []

    for bi in range(n_align):
        C1 = complex_blocks_r1[bi].copy()
        C2 = complex_blocks_r2[bi].copy()
        E1 = energy_blocks_r1[bi]
        E2 = energy_blocks_r2[bi]
        tx_syms = tx_symbols_frames[bi]
        H, W = C1.shape
        n_syms = min(len(tx_syms), H)
        n_syms_actual = n_syms

        # --- Step 1: dual-channel independent CFAR symbol localization ---
        peak_mask1, _ = advanced_cfar_and_grouping(E1)
        peak_coords1 = np.argwhere(peak_mask1)
        if len(peak_coords1) >= n_syms:
            peak_vals1 = np.array([E1[r, c] for r, c in peak_coords1])
            top_idx1 = np.argsort(peak_vals1)[-n_syms:]
            sel_coords1 = peak_coords1[top_idx1]
        elif len(peak_coords1) > 0:
            sel_coords1 = peak_coords1
            n_syms_actual = len(sel_coords1)
        else:
            sel_coords1 = np.array([(i, i) for i in range(n_syms)])
            n_syms_actual = n_syms

        peak_mask2, _ = advanced_cfar_and_grouping(E2)
        peak_coords2 = np.argwhere(peak_mask2)
        n_r2_peaks = len(peak_coords2)

        # --- Step 2: extract dual-channel complex symbols ---
        rx1 = _extract_symbol_complex(C1, sel_coords1, H, W)

        if n_r2_peaks > 0:
            peak_vals2 = np.array([E2[r, c] for r, c in peak_coords2])
            r2_sorted = np.argsort(peak_vals2)[::-1]
            peak_coords2_sorted = peak_coords2[r2_sorted]
            n_r2_use = min(n_syms_actual, len(peak_coords2_sorted))
            if n_r2_use > 0:
                rx2 = _extract_symbol_complex(
                    C2, peak_coords2_sorted[:n_r2_use], H, W
                )
                if n_r2_use < n_syms_actual:
                    repeats = (n_syms_actual + n_r2_use - 1) // n_r2_use
                    rx2 = np.tile(rx2, repeats)[:n_syms_actual]
            else:
                rx2 = np.zeros(n_syms_actual, dtype=np.complex128)
        else:
            rx2 = np.zeros(n_syms_actual, dtype=np.complex128)
            n_r2_use = 0

        # --- Step 3: channel estimation + power calculation ---
        tx_sub = tx_syms[:n_syms_actual]
        tx_abs = np.abs(tx_sub)
        tx_safe = np.where(tx_abs > EPS, tx_sub, 1.0 + 0j)
        h1 = rx1 / tx_safe
        h2 = rx2 / tx_safe
        p1 = np.abs(h1) ** 2
        p2 = np.abs(h2) ** 2

        # R2 validity determination
        r2_valid_ratio = n_r2_use / max(n_syms_actual, 1)
        r2_valid_mask = np.ones(n_syms_actual, dtype=bool)
        if r2_valid_ratio < R2_VALID_FLOOR:
            r2_valid_mask[:] = False
        else:
            r2_valid_mask = (p2 > p1 * 0.01)

        n_r2_valid = int(np.sum(r2_valid_mask))
        excluded_r2_syms += (n_syms_actual - n_r2_valid)

        total_power_r1 += float(np.mean(p1))
        total_power_r2 += float(np.mean(p2))

        # --- Step 4: multi-mode fusion weights ---
        # 4a: standard MRC
        p_sum = p1 + p2 + EPS
        w1_mrc = p1 / p_sum
        w2_mrc = p2 / p_sum
        w1_mrc = np.where(r2_valid_mask, w1_mrc, 1.0)
        w2_mrc = np.where(r2_valid_mask, w2_mrc, 0.0)
        y_mrc = w1_mrc * rx1 + w2_mrc * rx2

        # 4b: SC (select stronger channel)
        w1_sc = np.where(p1 >= p2, 1.0, 0.0)
        w2_sc = 1.0 - w1_sc
        w1_sc = np.where(r2_valid_mask, w1_sc, 1.0)
        w2_sc = np.where(r2_valid_mask, w2_sc, 0.0)
        y_sc = w1_sc * rx1 + w2_sc * rx2

        # 4c: EGC (equal gain)
        w1_egc = np.where(r2_valid_mask, 0.5, 1.0)
        w2_egc = np.where(r2_valid_mask, 0.5, 0.0)
        y_egc = w1_egc * rx1 + w2_egc * rx2

        # 4d: confidence-weighted
        conf1 = np.abs(np.real(rx1)) + np.abs(np.imag(rx1))
        conf2 = np.abs(np.real(rx2)) + np.abs(np.imag(rx2))
        conf_sum = conf1 + conf2 + EPS
        w1_conf = conf1 / conf_sum
        w2_conf = conf2 / conf_sum
        w1_conf = np.where(r2_valid_mask, w1_conf, 1.0)
        w2_conf = np.where(r2_valid_mask, w2_conf, 0.0)
        y_conf = w1_conf * rx1 + w2_conf * rx2

        # 4e: dynamic weight cap MRC (Capped-MRC)
        # Limit w1 ≤ W1_CAP, forcefully retain R2 correction contribution
        w1_capped = np.minimum(w1_mrc, W1_CAP)
        w2_capped = 1.0 - w1_capped
        w1_capped = np.where(r2_valid_mask, w1_capped, 1.0)
        w2_capped = np.where(r2_valid_mask, w2_capped, 0.0)
        y_capped = w1_capped * rx1 + w2_capped * rx2

        weight_log.append({
            "mean_w1_mrc": float(np.mean(w1_mrc)),
            "mean_w2_mrc": float(np.mean(w2_mrc)),
            "mean_w1_capped": float(np.mean(w1_capped)),
            "mean_w2_capped": float(np.mean(w2_capped)),
            "r2_valid_count": n_r2_valid,
            "r2_total": n_syms_actual,
            "r2_valid_ratio": float(n_r2_valid) / max(n_syms_actual, 1),
            "n_symbols": n_syms_actual,
            "p1_mean": float(np.mean(p1)),
            "p2_mean": float(np.mean(p2)),
            "r2_peaks": n_r2_peaks,
        })

        # --- Step 5: QPSK hard decision ---
        tx_bits_real = (np.real(tx_sub) > 0).astype(int)
        tx_bits_imag = (np.imag(tx_sub) > 0).astype(int)

        est_r1_r = (np.real(rx1) > 0).astype(int)
        est_r1_i = (np.imag(rx1) > 0).astype(int)
        est_r2_r = (np.real(rx2) > 0).astype(int)
        est_r2_i = (np.imag(rx2) > 0).astype(int)
        est_mrc_r = (np.real(y_mrc) > 0).astype(int)
        est_mrc_i = (np.imag(y_mrc) > 0).astype(int)
        est_sc_r = (np.real(y_sc) > 0).astype(int)
        est_sc_i = (np.imag(y_sc) > 0).astype(int)
        est_egc_r = (np.real(y_egc) > 0).astype(int)
        est_egc_i = (np.imag(y_egc) > 0).astype(int)
        est_conf_r = (np.real(y_conf) > 0).astype(int)
        est_conf_i = (np.imag(y_conf) > 0).astype(int)
        est_cap_r = (np.real(y_capped) > 0).astype(int)
        est_cap_i = (np.imag(y_capped) > 0).astype(int)

        err_r1 += int(np.sum(est_r1_r != tx_bits_real) +
                       np.sum(est_r1_i != tx_bits_imag))
        err_r2 += int(np.sum(est_r2_r != tx_bits_real) +
                       np.sum(est_r2_i != tx_bits_imag))
        err_mrc += int(np.sum(est_mrc_r != tx_bits_real) +
                       np.sum(est_mrc_i != tx_bits_imag))
        err_sc += int(np.sum(est_sc_r != tx_bits_real) +
                      np.sum(est_sc_i != tx_bits_imag))
        err_egc += int(np.sum(est_egc_r != tx_bits_real) +
                       np.sum(est_egc_i != tx_bits_imag))
        err_conf += int(np.sum(est_conf_r != tx_bits_real) +
                        np.sum(est_conf_i != tx_bits_imag))
        err_capped += int(np.sum(est_cap_r != tx_bits_real) +
                          np.sum(est_cap_i != tx_bits_imag))
        total_bits += 2 * n_syms_actual
        n_frames += 1

        # --- Step 6: construct fused complex matrix (using Capped-MRC weights) ---
        C_fused = np.zeros_like(C1, dtype=np.complex128)
        for k, (r, c) in enumerate(sel_coords1):
            r_lo, r_hi = max(0, r-1), min(H, r+2)
            c_lo, c_hi = max(0, c-1), min(W, c+2)
            C_fused[r_lo:r_hi, c_lo:c_hi] = (
                w1_capped[k] * C1[r_lo:r_hi, c_lo:c_hi] +
                w2_capped[k] * C2[r_lo:r_hi, c_lo:c_hi]
            )
        mask_filled = np.zeros((H, W), dtype=bool)
        for r, c in sel_coords1:
            r_lo, r_hi = max(0, r-1), min(H, r+2)
            c_lo, c_hi = max(0, c-1), min(W, c+2)
            mask_filled[r_lo:r_hi, c_lo:c_hi] = True
        C_fused[~mask_filled] = C1[~mask_filled]
        C_fused = np.where(np.isfinite(C_fused), C_fused, 0.0 + 0j)
        fused_complex_blocks.append(C_fused)
        fused_energy_blocks.append(np.abs(C_fused) ** 2)

    # --- Compute per-mode BER ---
    ber_r1 = err_r1 / max(total_bits, 1)
    ber_r2 = err_r2 / max(total_bits, 1)
    ber_mrc = err_mrc / max(total_bits, 1)
    ber_sc = err_sc / max(total_bits, 1)
    ber_egc = err_egc / max(total_bits, 1)
    ber_conf = err_conf / max(total_bits, 1)
    ber_capped = err_capped / max(total_bits, 1)

    # --- Select best mode ---
    mode_bers = {"MRC": ber_mrc, "SC": ber_sc, "EGC": ber_egc,
                 "Conf-MRC": ber_conf, "Capped-MRC": ber_capped,
                 "R1-only": ber_r1, "R2-only": ber_r2}
    best_mode = min(mode_bers, key=mode_bers.get)
    best_ber = mode_bers[best_mode]

    # --- Diversity gain (best fusion mode vs best single channel, negative = diversity degradation) ---
    # Note: best_single only takes min(ber_r1, ber_r2), EPS serves only as division lower bound,
    # must NOT be included in min() otherwise denominator=1e-16 causes dB to explode to -160 range.
    best_single = min(ber_r1, ber_r2)
    # Best fusion mode BER (exclude single channel, measure gain/degradation of diversity itself)
    fusion_bers = {"MRC": ber_mrc, "SC": ber_sc, "EGC": ber_egc,
                   "Conf-MRC": ber_conf, "Capped-MRC": ber_capped}
    best_fusion_mode = min(fusion_bers, key=fusion_bers.get)
    best_fusion_ber = fusion_bers[best_fusion_mode]
    # gain_db > 0: diversity outperforms single channel; gain_db < 0: diversity degrades
    gain_db = -10.0 * np.log10(
        max(best_fusion_ber, EPS) / max(best_single, EPS)
    ) if best_fusion_ber > 0 else 0.0

    # Improvement percentage (negative = degradation)
    improvement_pct = (
        (best_single - best_fusion_ber) / max(best_single, EPS) * 100
    )

    actual_ratio = total_power_r2 / max(total_power_r1, EPS)
    logger.info(
        "Adaptive diversity [%s]: R1=%.4f R2=%.4f → MRC=%.4f SC=%.4f EGC=%.4f "
        "Conf=%.4f Capped=%.4f | Best=%s Best_fusion=%s(%.4f) "
        "Diversity_gain=%+.2fdB Improvement=%+.2f%% | R2/R1=%.2f%%",
        band or "?", ber_r1, ber_r2, ber_mrc, ber_sc, ber_egc,
        ber_conf, ber_capped, best_mode,
        best_fusion_mode, best_fusion_ber,
        gain_db, improvement_pct, actual_ratio * 100
    )

    if best_fusion_ber < best_single:
        logger.info("Diversity success: %s reduced BER from %.4f to %.4f (%.2f%% improvement)",
                    best_fusion_mode, best_single, best_fusion_ber,
                    improvement_pct)
    else:
        logger.warning("Diversity degradation: best_fusion=%s(%.4f) > best_single=%.4f "
                       "(%.2f%% degradation, %+.2fdB)",
                       best_fusion_mode, best_fusion_ber, best_single,
                       -improvement_pct, gain_db)

    return {
        "fused_complex_blocks": fused_complex_blocks,
        "fused_energy_blocks": fused_energy_blocks,
        "weights": weight_log,
        "ber_r1": ber_r1,
        "ber_r2": ber_r2,
        "ber_mrc": ber_mrc,
        "ber_sc": ber_sc,
        "ber_egc": ber_egc,
        "ber_conf": ber_conf,
        "ber_capped": ber_capped,
        "best_mode": best_mode,
        "best_ber": best_ber,
        "best_fusion_mode": best_fusion_mode,
        "best_fusion_ber": best_fusion_ber,
        "best_single_ber": best_single,
        "gain_db": gain_db,
        "improvement_pct": improvement_pct,
        "total_bits": total_bits,
        "err_r1": err_r1,
        "err_r2": err_r2,
        "err_mrc": err_mrc,
        "err_sc": err_sc,
        "err_egc": err_egc,
        "err_capped": err_capped,
        "total_power_r1": total_power_r1,
        "total_power_r2": total_power_r2,
        "n_frames": n_frames,
        "excluded_r2_syms": excluded_r2_syms,
        "diversity_skipped": False,
        "power_ratio": actual_ratio,
    }


# =====================================================================
# Module 7C: Communication Prior Decision Filtering — Demodulation-level False Alarm Screening
# =====================================================================

def communication_prior_filter(purified_blocks, tx_symbols_frames,
                               band=None):
    """Secondary false alarm screening based on demodulation results.

    Core idea:
      Topology+CFAR can only suppress false alarms in time-frequency domain, cannot distinguish
      "noise peaks on real signals" from "false connections formed by pure noise". This module introduces communication priors:
        1. Perform QPSK demodulation on CFAR detected peaks
        2. Use TX known symbols for correlation matching
        3. Peaks with correlation below threshold are judged as false alarms and removed
        4. Output "communication-level" symbol count (distinct from "detection-level" symbol count)

    Returns:
        dict: {
            'comm_symbols': per-frame communication-level symbol count,
            'false_alarm_removed': per-frame removed false alarm count,
            'comm_detection_rate': communication-level detection rate,
            'correlation_scores': per-frame correlation matching scores,
        }
    """
    if not purified_blocks or not tx_symbols_frames:
        return {"comm_symbols": [], "false_alarm_removed": [],
                "comm_detection_rate": 0.0, "correlation_scores": []}

    n_align = min(len(purified_blocks), len(tx_symbols_frames))
    expected_syms = 42 if band in ("LF", "MF") else 64

    comm_symbols = []
    false_alarm_removed = []
    corr_scores = []

    # Correlation matching threshold: normalized correlation > 0.3 judged as real symbol
    CORR_THRESHOLD = 0.3

    for bi in range(n_align):
        puri = purified_blocks[bi]
        tx_syms = tx_symbols_frames[bi]
        H, W = puri.shape
        n_syms = min(len(tx_syms), H)

        # CFAR peak detection
        peak_mask, n_raw = advanced_cfar_and_grouping(puri)
        peak_coords = np.argwhere(peak_mask)

        if len(peak_coords) == 0:
            comm_symbols.append(0)
            false_alarm_removed.append(0)
            corr_scores.append(0.0)
            continue

        # Take peaks with highest energy
        peak_vals = np.array([puri[r, c] for r, c in peak_coords])
        n_select = min(len(peak_coords), expected_syms * 2)
        top_idx = np.argsort(peak_vals)[-n_select:]
        sel_coords = peak_coords[top_idx]
        sel_vals = peak_vals[top_idx]

        # Perform QPSK demodulation + correlation matching on each peak
        n_confirmed = 0
        for k in range(len(sel_coords)):
            r, c = sel_coords[k]
            # Extract peak neighborhood features
            r_lo, r_hi = max(0, r - 1), min(H, r + 2)
            c_lo, c_hi = max(0, c - 1), min(W, c + 2)
            patch = puri[r_lo:r_hi, c_lo:c_hi]
            rx_mag = np.sqrt(np.mean(patch)) if np.mean(patch) > 0 else 0.0

            # Estimate phase (simplified: use energy distribution asymmetry)
            patch_flat = patch.flatten()
            if len(patch_flat) >= 4:
                phase_est = np.arctan2(
                    patch_flat[len(patch_flat) // 2:].mean() -
                    patch_flat[:len(patch_flat) // 2].mean(),
                    patch_flat[1::2].mean() -
                    patch_flat[::2].mean()
                )
            else:
                phase_est = 0.0

            est_sym = rx_mag * np.exp(1j * phase_est)

            # Correlation matching with TX symbol library
            tx_lib = tx_syms[:n_syms]
            if len(tx_lib) == 0:
                continue
            # Per-symbol normalized correlation (est_sym is scalar, tx_lib is array)
            corr_vals = np.abs(est_sym * np.conj(tx_lib)) / (
                np.abs(est_sym) * np.abs(tx_lib) + EPS
            )
            max_corr = float(np.max(corr_vals))

            if max_corr > CORR_THRESHOLD:
                n_confirmed += 1

        n_removed = len(sel_coords) - n_confirmed
        comm_symbols.append(n_confirmed)
        false_alarm_removed.append(n_removed)
        mean_corr = float(np.mean(sel_vals)) / (
            float(np.mean(puri)) + EPS
        )
        corr_scores.append(mean_corr)

    total_comm = sum(comm_symbols)
    total_expected = n_align * expected_syms
    comm_rate = total_comm / max(total_expected, 1)

    logger.info(
        "Communication prior filter: %dframes | Comm_level_symbols=%d (expected=%d) | "
        "Detection_rate=%.4f | False_alarms_removed=%d",
        n_align, total_comm, total_expected, comm_rate,
        sum(false_alarm_removed)
    )

    return {
        "comm_symbols": comm_symbols,
        "false_alarm_removed": false_alarm_removed,
        "comm_detection_rate": comm_rate,
        "correlation_scores": corr_scores,
        "total_comm": total_comm,
        "total_removed": sum(false_alarm_removed),
    }


# =====================================================================
# Module 7D: Deep Fading Frame Recovery Strategy
# =====================================================================

def _time_axis_median_smooth(mat_complex, width=DF_TIME_SMOOTH_WIDTH):
    """Median smoothing along time axis (column direction), preserving phase.

    Performs 2D median filtering with kernel=(1, width) on real/imaginary parts of complex matrix separately,
    equivalent to 1D median smoothing along time axis. Pure matrix arithmetic, no semantic labels introduced.

    Used for time-domain interpolation smoothing of high BER frames, suppresses burst error floor.
    """
    if width < 3 or width % 2 == 0:
        width = max(3, width | 1)  # force odd
    H, W = mat_complex.shape
    if W < width:
        return mat_complex
    real_part = np.real(mat_complex)
    imag_part = np.imag(mat_complex)
    real_smooth = ssig.medfilt2d(real_part, kernel_size=(1, width))
    imag_smooth = ssig.medfilt2d(imag_part, kernel_size=(1, width))
    out = real_smooth + 1j * imag_smooth
    return np.where(np.isfinite(out), out, mat_complex)


def deep_fade_recovery(purified_blocks, channel_gains, deep_fade_flags,
                       band=None, per_frame_ber=None,
                       purified_complex_blocks=None):
    """Recovery and link strategy recommendation after deep fading frame identification (enhanced version).

    Enhancements (mid-term 2):
      A. BER trigger: frames with per-frame BER > DF_HIGH_BER_THRESH also trigger recovery
      B. Complex path: when purified_complex_blocks is passed, perform interpolation on complex matrix,
         preserve phase information (for subsequent QPSK demodulation)
      C. Time-domain sliding window median smoothing: perform width=3 median filtering along time axis
         for high BER frames, suppress burst error floor

    Recovery strategies:
      1. Deep fading frames (channel gain collapse): complex linear interpolation compensation from preceding/succeeding normal frames
      2. High BER frames (signal exists but BER is high): intra-frame time-domain median smoothing
      3. Retransmission/power/diversity link recommendations

    Parameters:
        purified_blocks: list[np.ndarray[float64]] energy purified matrices
        channel_gains: list[float] per-frame channel gains
        deep_fade_flags: list[bool] deep fading flags
        per_frame_ber: list[float] per-frame BER (optional, triggers high BER smoothing)
        purified_complex_blocks: list[np.ndarray[complex128]] complex purified matrices
            (optional, enables complex path interpolation to preserve phase)
    Returns:
        dict: recovery strategies and recommendations (including recovered_blocks / recovered_complex_blocks)
    """
    n_frames = len(purified_blocks)
    if n_frames == 0:
        return {}

    deep_flags = list(deep_fade_flags) if deep_fade_flags else \
        [False] * n_frames
    deep_indices = [i for i, f in enumerate(deep_flags) if f]
    n_deep = len(deep_indices)

    # --- High BER frame identification (BER trigger) ---
    high_ber_indices = []
    if per_frame_ber and len(per_frame_ber) >= n_frames:
        high_ber_indices = [
            i for i, b in enumerate(per_frame_ber)
            if b > DF_HIGH_BER_THRESH and not deep_flags[i]
        ]
    n_high_ber = len(high_ber_indices)

    # Frames requiring recovery (deep fading + high BER)
    repair_indices = sorted(set(deep_indices + high_ber_indices))

    use_complex = (
        DF_COMPLEX_INTERP
        and purified_complex_blocks is not None
        and len(purified_complex_blocks) >= n_frames
    )

    if not repair_indices:
        logger.info("Deep fading recovery: no recovery needed (deep_fading=%d, high_BER=%d)",
                    n_deep, n_high_ber)
        result = {
            "n_deep_fade": 0,
            "deep_fade_indices": [],
            "high_ber_indices": [],
            "retransmit_indices": [],
            "power_boost_indices": [],
            "diversity_indices": [],
            "interpolated": [],
            "time_smoothed": [],
            "recovered_blocks": [p.copy() for p in purified_blocks],
            "strategy": "none_needed",
        }
        if use_complex:
            result["recovered_complex_blocks"] = [
                c.copy() for c in purified_complex_blocks
            ]
        return result

    recovered_blocks = [p.copy() for p in purified_blocks]
    recovered_complex = (
        [c.copy() for c in purified_complex_blocks] if use_complex else None
    )
    interpolated = []
    time_smoothed = []

    # --- Recovery loop ---
    for idx in repair_indices:
        is_deep = deep_flags[idx]

        if is_deep:
            # --- Strategy A: deep fading frame → complex linear interpolation from preceding/succeeding normal frames ---
            prev_good = None
            next_good = None
            for j in range(idx - 1, -1, -1):
                if not deep_flags[j]:
                    prev_good = j
                    break
            for j in range(idx + 1, n_frames):
                if not deep_flags[j]:
                    next_good = j
                    break

            if prev_good is not None and next_good is not None:
                alpha = (idx - prev_good) / max(next_good - prev_good, 1)
                if use_complex:
                    interp_c = (
                        (1 - alpha) * purified_complex_blocks[prev_good] +
                        alpha * purified_complex_blocks[next_good]
                    )
                    recovered_complex[idx] = interp_c
                    recovered_blocks[idx] = np.abs(interp_c) ** 2
                else:
                    interp_e = (
                        (1 - alpha) * purified_blocks[prev_good] +
                        alpha * purified_blocks[next_good]
                    )
                    recovered_blocks[idx] = interp_e
                interpolated.append(idx)
                logger.info(
                    "Frame %d deep_fading→complex_interp (prev=%d, next=%d, α=%.2f, %s)",
                    idx, prev_good, next_good, alpha,
                    "complex" if use_complex else "energy"
                )
            elif prev_good is not None:
                if use_complex:
                    recovered_complex[idx] = purified_complex_blocks[prev_good].copy()
                    recovered_blocks[idx] = purified_blocks[prev_good].copy()
                else:
                    recovered_blocks[idx] = purified_blocks[prev_good].copy()
                interpolated.append(idx)
                logger.info("Frame %d deep_fading→prev_frame_substitution (prev=%d)", idx, prev_good)
            elif next_good is not None:
                if use_complex:
                    recovered_complex[idx] = purified_complex_blocks[next_good].copy()
                    recovered_blocks[idx] = purified_blocks[next_good].copy()
                else:
                    recovered_blocks[idx] = purified_blocks[next_good].copy()
                interpolated.append(idx)
                logger.info("Frame %d deep_fading→next_frame_substitution (next=%d)", idx, next_good)
            else:
                # No normal reference frame → fallback to intra-frame time-domain median smoothing, suppress floor BER
                if use_complex:
                    smoothed_c = _time_axis_median_smooth(
                        recovered_complex[idx], DF_TIME_SMOOTH_WIDTH
                    )
                    recovered_complex[idx] = smoothed_c
                    recovered_blocks[idx] = np.abs(smoothed_c) ** 2
                else:
                    smoothed_e = _time_axis_median_smooth(
                        recovered_blocks[idx].astype(np.complex128),
                        DF_TIME_SMOOTH_WIDTH
                    )
                    recovered_blocks[idx] = np.real(smoothed_e)
                time_smoothed.append(idx)
                logger.warning(
                    "Frame %d deep_fading→no_ref_frame, fallback time-domain_median_smooth (width=%d, %s)",
                    idx, DF_TIME_SMOOTH_WIDTH,
                    "complex" if use_complex else "energy"
                )
        else:
            # --- Strategy B: high BER frame → intra-frame time-domain median smoothing (suppress burst errors) ---
            if use_complex:
                smoothed_c = _time_axis_median_smooth(
                    recovered_complex[idx], DF_TIME_SMOOTH_WIDTH
                )
                recovered_complex[idx] = smoothed_c
                recovered_blocks[idx] = np.abs(smoothed_c) ** 2
            else:
                # Directly smooth energy matrix (real)
                smoothed_e = _time_axis_median_smooth(
                    recovered_blocks[idx].astype(np.complex128),
                    DF_TIME_SMOOTH_WIDTH
                )
                recovered_blocks[idx] = np.real(smoothed_e)
            time_smoothed.append(idx)
            logger.info("Frame %d high_BER→time-domain_median_smooth (BER=%.3f, width=%d, %s)",
                        idx,
                        per_frame_ber[idx] if per_frame_ber else 0.0,
                        DF_TIME_SMOOTH_WIDTH,
                        "complex" if use_complex else "energy")

    # --- Link-level recommendations ---
    retransmit_indices = list(deep_indices)
    if channel_gains:
        cg_mean = float(np.mean(channel_gains))
        power_boost_indices = [
            i for i, g in enumerate(channel_gains)
            if g < cg_mean * 0.5
        ]
    else:
        power_boost_indices = []
    diversity_indices = list(deep_indices)

    strategy_parts = [
        f"deep_fading={n_deep}frames",
        f"high_BER_smoothed={n_high_ber}frames",
        f"interp_recovered={len(interpolated)}frames",
        f"time_smoothed={len(time_smoothed)}frames",
        f"recommend_retransmit={len(retransmit_indices)}frames",
        f"recommend_power_boost={len(power_boost_indices)}frames",
        f"recommend_diversity={len(diversity_indices)}frames",
    ]
    logger.info("Deep fading recovery strategy: %s", ", ".join(strategy_parts))

    result = {
        "n_deep_fade": n_deep,
        "deep_fade_indices": deep_indices,
        "high_ber_indices": high_ber_indices,
        "interpolated": interpolated,
        "time_smoothed": time_smoothed,
        "recovered_blocks": recovered_blocks,
        "retransmit_indices": retransmit_indices,
        "power_boost_indices": power_boost_indices,
        "diversity_indices": diversity_indices,
        "strategy": "interp+time_smooth+retransmit+power_ctrl+diversity",
        "summary": ", ".join(strategy_parts),
    }
    if use_complex:
        result["recovered_complex_blocks"] = recovered_complex
    return result


# =====================================================================
# Module 8: Dual-Channel R1+R2 Diversity Fusion
# =====================================================================

def dual_channel_fusion(sig1, sig2, fs,
                        mode="mrc", alpha=DIVIDE_ALPHA):
    """Dual-channel diversity fusion.

    Supports 4 modes:
      - 'egc': equal gain combining (energy domain fusion, preserves primary channel symbols)
      - 'mrc': maximum ratio combining (weighted by energy, optimal SNR gain)
      - 'selection': selection combining (choose the path with higher energy)
      - 'mrc_full': full-bandwidth MRC (weighted by frequency point, outperforms time-domain weighting)

    Parameters:
        sig1, sig2: two time-domain signals
        fs: sampling rate
        mode: combining mode
        alpha: weighting exponent (egc mode)
    Returns:
        Fused signal + STFT matrix + fusion metadata
    """
    s1 = np.asarray(sig1, dtype=np.float64)
    s2 = np.asarray(sig2, dtype=np.float64)
    min_len = min(len(s1), len(s2))
    s1, s2 = s1[:min_len], s2[:min_len]

    e1 = float(np.sum(s1 * s1)) + EPS
    e2 = float(np.sum(s2 * s2)) + EPS
    ratio = min(e1, e2) / max(e1, e2)

    if mode == "mrc_full":
        # Full-bandwidth MRC: weight in frequency domain by SNR of each frequency point
        from scipy.signal import stft as scipy_stft
        f1, t1, S1 = scipy_stft(s1, fs=fs, nperseg=STFT_NPERSEG,
                                noverlap=STFT_NOVERLAP, window=STFT_WINDOW)
        f2, t2, S2 = scipy_stft(s2, fs=fs, nperseg=STFT_NPERSEG,
                                noverlap=STFT_NOVERLAP, window=STFT_WINDOW)
        # Frequency-domain MRC: weight each frequency point by energy
        E1 = np.abs(S1) ** 2 + EPS
        E2 = np.abs(S2) ** 2 + EPS
        W1 = E1 / (E1 + E2)
        W2 = E2 / (E1 + E2)
        S_fused = W1 * S1 + W2 * S2
        # Inverse STFT back to time domain
        from scipy.signal import istft
        _, fused = istft(S_fused, fs=fs, nperseg=STFT_NPERSEG,
                         noverlap=STFT_NOVERLAP, window=STFT_WINDOW)
    elif mode == "mrc":
        # Time-domain MRC: weighted by total energy
        w1 = e1 / (e1 + e2)
        w2 = e2 / (e1 + e2)
        fused = w1 * s1 + w2 * s2
    elif mode == "selection":
        fused = s1 if e1 >= e2 else s2
    else:
        # EGC energy domain fusion
        mag1 = np.abs(s1)
        mag2 = np.abs(s2)
        fused_mag = mag1 ** alpha + mag2 ** alpha
        sign = np.sign(s1) if e1 >= e2 else np.sign(s2)
        sign = np.where(sign == 0, np.sign(s1), sign)
        fused = fused_mag * sign

    if ratio < DIVIDE_MAX_RATIO:
        logger.warning("Diversity energy ratio %.3f abnormal, fusion may degrade (mode=%s)",
                       ratio, mode)
        if e1 > e2 * 5:
            fused = s1
            logger.warning("Fallback: using R1 channel only")
        elif e2 > e1 * 5:
            fused = s2
            logger.warning("Fallback: using R2 channel only")

    S_complex, f_ax, t_ax = sig2stft(fused, fs)
    return fused, S_complex, f_ax, t_ax, {"e1": e1, "e2": e2, "ratio": ratio,
                                          "mode": mode}


def run_dual_channel_sre(band="LF", max_files=2, max_frames=30):
    """Dual-channel R1+R2 diversity SRE processing (Post-SRE MRC + multi-mode comparison).

    Core flow:
      1. R1/R2 independent SRE purification → preserve purified_complex_blocks
      2. Post-SRE MRC: perform symbol-level maximum ratio combining on purified complex matrices
      3. Pre-SRE fusion (egc/mrc/mrc_full/selection) as baseline
      4. Three-path BER comparison: R1-only vs R2-only vs MRC-fused
    """
    logger.info("=" * 40)
    logger.info("Dual-channel diversity processing: band=%s files=%d frames=%d",
                band, max_files, max_frames)
    logger.info("=" * 40)

    rx_stats = {}
    for rx in ("R1", "R2"):
        stats = run_underwater_sre(
            band=band, receiver=rx,
            max_files=max_files, max_frames=max_frames,
            save_npy=False,
        )
        if stats:
            rx_stats[rx] = stats

    stats_r1 = rx_stats.get("R1", {})
    stats_r2 = rx_stats.get("R2", {})

    # --- Post-SRE MRC: perform symbol-level MRC fusion on purified complex matrices ---
    mrc_result = {}
    if stats_r1 and stats_r2:
        tx_frames = read_tx_symbols(band)
        pcx_r1 = stats_r1.get("purified_complex_blocks", [])
        pcx_r2 = stats_r2.get("purified_complex_blocks", [])
        pur_r1 = stats_r1.get("purified_blocks", [])
        pur_r2 = stats_r2.get("purified_blocks", [])

        if pcx_r1 and pcx_r2 and tx_frames:
            min_blocks = min(len(pcx_r1), len(pcx_r2))
            mrc_result = mrc_purified_fusion(
                pcx_r1[:min_blocks], pcx_r2[:min_blocks],
                pur_r1[:min_blocks], pur_r2[:min_blocks],
                tx_frames[:min_blocks], band=band,
            )
            _bm = mrc_result.get("best_mode", "?")
            _sk = mrc_result.get("diversity_skipped", False)
            if _sk:
                logger.info(
                    "[%s] Adaptive diversity: fusion skipped (R2/R1 power ratio too low) "
                    "→ R1=%.4f R2=%.4f Best=%s",
                    band,
                    mrc_result.get("ber_r1", 0),
                    mrc_result.get("ber_r2", 0),
                    _bm,
                )
            else:
                logger.info(
                    "[%s] Adaptive diversity: R1=%.4f R2=%.4f "
                    "→ MRC=%.4f SC=%.4f EGC=%.4f Capped=%.4f | Best=%s "
                    "Best_fusion=%s(%.4f) Gain=%+.2fdB",
                    band,
                    mrc_result.get("ber_r1", 0),
                    mrc_result.get("ber_r2", 0),
                    mrc_result.get("ber_mrc", 0) or 0,
                    mrc_result.get("ber_sc", 0) or 0,
                    mrc_result.get("ber_egc", 0) or 0,
                    mrc_result.get("ber_capped", 0) or 0,
                    _bm,
                    mrc_result.get("best_fusion_mode", "?"),
                    mrc_result.get("best_fusion_ber", 0),
                    mrc_result.get("gain_db", 0),
                )
        else:
            logger.warning("[%s] Post-SRE MRC skipped: insufficient complex matrices or TX symbols", band)
    else:
        logger.warning("[%s] Post-SRE MRC skipped: insufficient R1/R2 SRE results", band)

    # --- Pre-SRE multi-mode fusion comparison (baseline) ---
    band_root = _band_root(band)
    fusion_modes = ["egc", "mrc", "mrc_full", "selection"]
    all_mode_results = {}

    suite_p1 = SREFoundationalOperatorSuite(
        beta_sre=SRE_BETA, lambda_0=SRE_LAMBDA_0, lambda_2=SRE_LAMBDA_2,
        alpha_n=SRE_ALPHA_N, epsilon_topo=SRE_EPS_TOPO,
        max_n_dimension=SRE_MAX_DIM,
    )
    suite_p2 = SRETransportAlignmentSuite(
        c_max=SRE_C_MAX, delta_flt=EPS, w_min=1e-12,
    )
    suite_p3 = SRECommercialCoreSuite(
        k0_horizon=SRE_K0_HORIZON, lambda_base=SRE_LAMBDA_BASE,
    )

    lambda_2_mod = SRE_LAMBDA_2 * (1486.71 / 1500.0)
    wav_r1, _ = _list_wav(band, "R1")
    wav_r2, _ = _list_wav(band, "R2")
    wav_r1 = wav_r1[:max_files]
    wav_r2 = wav_r2[:max_files]
    n_pairs = min(len(wav_r1), len(wav_r2))

    bp = get_band_params(band)

    for mode in fusion_modes:
        mode_multipath = []
        mode_symbols = []

        for fi in range(n_pairs):
            sig1, fs = read_wav_mono(wav_r1[fi])
            sig2, _ = read_wav_mono(wav_r2[fi])

            fused, S_fused, _, _, div_info = dual_channel_fusion(
                sig1, sig2, fs, mode=mode,
            )
            fname = os.path.basename(wav_r1[fi])
            logger.info("[%s] %s [%s]fusion e1=%.2f e2=%.2f ratio=%.3f",
                        band, fname, mode, div_info["e1"], div_info["e2"],
                        div_info["ratio"])

            energy = np.abs(S_fused) ** 2
            F, T = energy.shape
            if F < BLOCK_N or T < BLOCK_N:
                continue

            n_blocks = min(max_frames, (T - BLOCK_N) // BLOCK_STRIDE + 1)
            for bi in range(n_blocks):
                t_start = bi * BLOCK_STRIDE
                block = energy[:BLOCK_N, t_start:t_start + BLOCK_N].astype(np.float64)
                block = (block + block.T) / 2.0
                complex_block = S_fused[:BLOCK_N, t_start:t_start + BLOCK_N].astype(
                    np.complex128
                )
                res = sre_underwater_purifier(
                    block, suite_p1, suite_p2, suite_p3,
                    lambda_2=lambda_2_mod,
                    band=band,
                    band_params=bp,
                    frame_idx=bi,
                    complex_block=complex_block,
                )
                mode_multipath.append(res["multipath_ratio"])
                mode_symbols.append(res["n_symbols"])

        all_mode_results[mode] = {
            "multipath": mode_multipath,
            "symbols": mode_symbols,
            "mean_symbols": float(np.mean(mode_symbols)) if mode_symbols else 0.0,
            "mean_multipath": float(np.mean(mode_multipath)) if mode_multipath else 0.0,
        }

    # --- Compare different modes (symbol count + BER) ---
    r1_syms = stats_r1.get("symbol_counts", []) if stats_r1 else []
    r1_mean = float(np.mean(r1_syms)) if r1_syms else 0.0

    best_mode = "mrc"
    best_imp = -999.0
    for mode in fusion_modes:
        mr = all_mode_results[mode]
        if r1_mean > 0:
            imp = (mr["mean_symbols"] - r1_mean) / r1_mean * 100.0
        else:
            imp = 0.0
        mr["improvement_pct"] = imp
        if imp > best_imp:
            best_imp = imp
            best_mode = mode

        logger.info("[%s] Pre-SRE_diversity[%s]: R1=%.1f Fused=%.1f Improvement=%.1f%%",
                    band, mode, r1_mean, mr["mean_symbols"], imp)

    # Post-SRE MRC vs Pre-SRE best comparison
    mrc_imp = mrc_result.get("improvement_pct", 0)
    if mrc_imp > 0:
        logger.info("[%s] ★ Post-SRE MRC improvement_rate=%.2f%% (Pre-SRE_best=%s %.2f%%)",
                    band, mrc_imp, best_mode, best_imp)

    best_result = all_mode_results.get(best_mode, {"mean_symbols": 0})

    return {
        "band": band,
        "r1_stats": stats_r1,
        "r2_stats": stats_r2,
        "post_sre_mrc": mrc_result,
        "fused_multipath": best_result.get("multipath", []),
        "fused_symbols": best_result.get("symbols", []),
        "improvement_pct": best_result.get("improvement_pct", 0.0),
        "best_mode": best_mode,
        "all_modes": all_mode_results,
    }


# =====================================================================
# Module 9: Multi-band Batch Comparison + Comprehensive Plotting
# =====================================================================

def run_multi_band(bands=None, max_files=2, max_frames=30,
                   include_dual=True):
    """Batch run LF/MF/HF bands, generate comprehensive comparison report."""
    if bands is None:
        bands = ["LF", "MF", "HF"]

    results = {}
    dual_results = {}

    for band in bands:
        logger.info("\n" + "=" * 50)
        logger.info("▶ Processing band: %s", band)
        logger.info("=" * 50)
        stats = run_underwater_sre(
            band=band, receiver="R1",
            max_files=max_files, max_frames=max_frames,
            save_npy=True,
        )
        if stats:
            # Detection rate
            det_rate = compute_detection_rate(
                stats["symbol_counts"], band
            )
            stats["detection_rate"] = det_rate

            # BER estimation (dual path)
            tx_frames = read_tx_symbols(band)
            n_align = min(len(stats.get("purified_blocks", [])),
                          len(tx_frames))
            if n_align > 0:
                puri_blocks = stats["purified_blocks"][:n_align]
                complex_blocks = stats.get("purified_complex_blocks", [])
                puri_complex = complex_blocks[:n_align] if complex_blocks else None
                tx_aligned = tx_frames[:n_align]

                # Original BER (energy path)
                ber_energy = estimate_ber_qpsk(puri_blocks, tx_aligned)
                stats["ber_energy"] = ber_energy

                # Complex path BER (preserve phase)
                if puri_complex:
                    ber_complex = estimate_ber_qpsk(
                        puri_blocks, tx_aligned,
                        purified_complex_blocks=puri_complex
                    )
                    stats["ber"] = ber_complex
                    stats["ber_complex"] = ber_complex
                else:
                    stats["ber"] = ber_energy

                # Channel equalization → post-equalization BER
                # Prioritize complex path for true zero-forcing equalization
                if puri_complex:
                    eq_res = channel_equalize_complex(
                        puri_complex, tx_aligned, band=band
                    )
                else:
                    eq_res = channel_equalize_purified(
                        puri_blocks, tx_aligned, band=band
                    )
                stats["equalization"] = eq_res

                # Deep fading recovery strategy (enhanced: BER trigger + complex path + time-domain smoothing)
                ber_ref = stats.get("ber_complex") or stats.get("ber_energy") or {}
                recovery_res = deep_fade_recovery(
                    puri_blocks,
                    eq_res.get("channel_gains", []),
                    eq_res.get("deep_fade_flags", []),
                    band=band,
                    per_frame_ber=ber_ref.get("per_frame_ber"),
                    purified_complex_blocks=puri_complex,
                )
                stats["recovery"] = recovery_res

                # Post-recovery BER (prioritize complex path)
                rec_blocks = recovery_res.get("recovered_blocks")
                if rec_blocks:
                    rec_complex = recovery_res.get("recovered_complex_blocks")
                    if rec_complex:
                        recovered_ber = estimate_ber_qpsk(
                            rec_blocks[:n_align],
                            tx_aligned,
                            purified_complex_blocks=rec_complex[:n_align],
                        )
                    else:
                        recovered_ber = estimate_ber_qpsk(
                            rec_blocks[:n_align],
                            tx_aligned,
                        )
                    stats["recovered_ber"] = recovered_ber

                # Communication prior decision filtering
                comm_res = communication_prior_filter(
                    puri_blocks, tx_aligned, band=band
                )
                stats["comm_filter"] = comm_res

        results[band] = stats

        if include_dual:
            dual = run_dual_channel_sre(
                band=band, max_files=max_files, max_frames=max_frames,
            )
            dual_results[band] = dual

    # --- Comprehensive comparison plot ---
    _plot_multi_band_comparison(results, dual_results)

    # --- Comprehensive numerical report ---
    _print_summary_report(results, dual_results)

    return results, dual_results


def _plot_multi_band_comparison(results, dual_results):
    """Generate multi-band comprehensive comparison PNG."""
    bands = [b for b in ("LF", "MF", "HF") if b in results]
    if not bands:
        return

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    colors = {"LF": "#1f77b4", "MF": "#2ca02c", "HF": "#d62728"}

    # (1) Multipath suppression ratio comparison
    ax = axes[0, 0]
    for band in bands:
        mp = results[band].get("multipath_ratios", [])
        if mp:
            ax.plot(mp, "-o", color=colors[band], markersize=3,
                    label=f"{band} (mean={np.mean(mp):.3f})")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Multipath Suppression Ratio")
    ax.set_title("Multi-band Multipath Interference Suppression Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (2) Symbol detection count comparison
    ax = axes[0, 1]
    for band in bands:
        sy = results[band].get("symbol_counts", [])
        if sy:
            ax.plot(sy, "-s", color=colors[band], markersize=3,
                    label=f"{band} (mean={np.mean(sy):.1f})")
    ax.set_xlabel("Frame Index")
    ax.set_ylabel("Detected Symbol Count")
    ax.set_title("Multi-band Effective Communication Symbol Detection Comparison")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (3) Detection rate comparison
    ax = axes[1, 0]
    bar_bands = []
    bar_rates = []
    bar_colors = []
    for band in bands:
        dr = results[band].get("detection_rate", {})
        rate = dr.get("mean_block_efficiency", 0.0) if dr else 0.0
        if rate > 0:
            bar_bands.append(band)
            bar_rates.append(rate * 100)
            bar_colors.append(colors[band])
    if bar_bands:
        bars = ax.bar(bar_bands, bar_rates, color=bar_colors, alpha=0.8)
        for bar, rate in zip(bars, bar_rates):
            ax.text(bar.get_x() + bar.get_width() / 2.0,
                    bar.get_height() + 0.5,
                    f"{rate:.1f}%", ha="center", va="bottom",
                    fontsize=9)
    ax.set_ylabel("Detection Rate (%)")
    ax.set_title("Multi-band TX Symbol Detection Efficiency Comparison")
    ax.grid(True, alpha=0.3, axis="y")

    # (4) Post-SRE MRC diversity gain comparison (best fusion vs best single channel)
    ax = axes[1, 1]
    mrc_bands = []
    mrc_gains = []
    mrc_colors = []
    for band in bands:
        dual = dual_results.get(band, {})
        mrc = dual.get("post_sre_mrc", {})
        # Skip bands where diversity was skipped (R2 power too low no fusion)
        if mrc.get("diversity_skipped", False):
            continue
        gain = mrc.get("gain_db", 0.0)
        mrc_bands.append(band)
        mrc_gains.append(gain)
        mrc_colors.append(colors[band])
    if mrc_bands:
        bars2 = ax.bar(mrc_bands, mrc_gains, color=mrc_colors, alpha=0.8)
        for bar, g in zip(bars2, mrc_gains):
            offset = 0.05 if g >= 0 else -0.15
            ax.text(bar.get_x() + bar.get_width() / 2.0,
                    bar.get_height() + offset,
                    f"{g:+.2f}dB", ha="center",
                    va="bottom" if g >= 0 else "top",
                    fontsize=9)
        # y-axis dynamic range: centered on max absolute value, 50% margin, ensure small negative values visible
        g_arr = np.array(mrc_gains)
        g_abs_max = max(np.max(np.abs(g_arr)), 0.5)
        ax.set_ylim(-g_abs_max * 1.5, g_abs_max * 1.5)
    ax.set_ylabel("Diversity Gain (dB)")
    ax.set_title("Post-SRE Diversity Gain (Best Fusion vs Best Single Channel)")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    out_path = os.path.join(
        OUT_DIR, f"multi_band_comparison_{int(time.time())}.png"
    )
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Multi-band comprehensive comparison plot: %s", out_path)
    return out_path


def _print_summary_report(results, dual_results):
    """Print comprehensive numerical report (including full post-processing pipeline)."""
    bands = [b for b in ("LF", "MF", "HF") if b in results]
    print("\n" + "=" * 120)
    print("  SRE Underwater Acoustic Communication Comprehensive Evaluation Report (Dual-path + Symbol-level Diversity MRC/SC/EGC)")
    print("=" * 120)
    print(f"  {'Band':<6} {'Multipath':>9} {'Symbols':>7} "
          f"{'DetectRate':>10} {'CxBER':>8} {'EqBER':>8} "
          f"{'MRC':>8} {'SC':>8} {'EGC':>8} {'Conf':>8} {'Capped':>8} "
          f"{'Best':>10} {'Gain':>8}")
    print("  " + "-" * 134)
    for band in bands:
        r = results[band]
        mp_mean = np.mean(r.get("multipath_ratios", [0]))
        sy_mean = np.mean(r.get("symbol_counts", [0]))
        dr = r.get("detection_rate", {}).get("mean_block_efficiency", 0.0)
        ber_cx = r.get("ber_complex", {}).get("ber", 0.0)
        eq = r.get("equalization", {})
        eq_ber = eq.get("post_ber", 0.0)

        # Post-SRE diversity data
        dual = dual_results.get(band, {})
        mrc = dual.get("post_sre_mrc", {})
        ber_mrc = mrc.get("ber_mrc")
        ber_sc = mrc.get("ber_sc")
        ber_egc = mrc.get("ber_egc")
        ber_conf = mrc.get("ber_conf")
        ber_capped = mrc.get("ber_capped")
        best_mode = mrc.get("best_mode", "N/A")
        best_ber = mrc.get("best_ber", 0.0)
        mrc_gain = mrc.get("gain_db", 0.0)
        ber_r1_mrc = mrc.get("ber_r1", 0.0)
        ber_r2_mrc = mrc.get("ber_r2", 0.0)
        skipped = mrc.get("diversity_skipped", False)

        def _fmt(val):
            return f"{val:.4f}" if val is not None and val > 0 else "skip"

        ber_cx_s = f"{ber_cx:.4f}" if ber_cx > 0 else "N/A"
        eq_s = f"{eq_ber:.4f}" if eq_ber > 0 else "N/A"
        mrc_s = _fmt(ber_mrc)
        sc_s = _fmt(ber_sc)
        egc_s = _fmt(ber_egc)
        conf_s = _fmt(ber_conf)
        cap_s = _fmt(ber_capped)
        best_s = f"{best_mode}" if best_ber > 0 else "N/A"
        # Gain display: with sign, 0 also shown (diversity flat)
        bf_mode = mrc.get("best_fusion_mode", "?")
        bf_ber = mrc.get("best_fusion_ber", 0.0)
        bs_ber = mrc.get("best_single_ber", 0.0)
        if skipped:
            gain_s = "skip"
        else:
            gain_s = f"{mrc_gain:+.2f}dB"

        print(f"  {band:<6} {mp_mean:>9.4f} {sy_mean:>7.1f} "
              f"{dr*100:>9.1f}% {ber_cx_s:>8} {eq_s:>8} "
              f"{mrc_s:>8} {sc_s:>8} {egc_s:>8} {conf_s:>8} {cap_s:>8} "
              f"{best_s:>10} {gain_s:>8}")

        # --- Physics analysis ---
        pi = r.get("physics_info", {})
        if pi:
            print(f"    └ Physics: {pi.get('summary', 'N/A')}")

        # --- Equalization details ---
        if eq:
            n_deep = eq.get("n_deep_fade", 0)
            delta = eq.get("ber_delta", 0)
            eq_type = eq.get("equalization_type", "energy")
            print(f"    └ Equalization[{eq_type}]: deep_fading={n_deep}frames, BER Δ={delta:+.4f} "
                  f"({'improved' if delta < 0 else 'degraded/flat'})")

        # --- Adaptive diversity details ---
        if mrc and mrc.get("total_bits", 0) > 0:
            if skipped:
                print(f"    └ Diversity[skipped]: R2/R1 power_ratio={mrc.get('power_ratio',0)*100:.2f}% "
                      f"< threshold → directly output optimal single channel")
                print(f"      R1={ber_r1_mrc:.4f} R2={ber_r2_mrc:.4f} "
                      f"→ Best={best_mode} (BER={best_ber:.4f})")
            else:
                print(f"    └ Diversity[{best_mode}]: R1={ber_r1_mrc:.4f} R2={ber_r2_mrc:.4f}")
                print(f"      MRC={mrc_s} SC={sc_s} EGC={egc_s} "
                      f"Conf={conf_s} Capped={cap_s}")
                print(f"      Best_fusion={bf_mode}({bf_ber:.4f}) "
                      f"Best_single={bs_ber:.4f} "
                      f"Gain={mrc_gain:+.2f}dB Improvement={mrc.get('improvement_pct',0):+.2f}%")
                print(f"      Power_ratio R2/R1={mrc.get('power_ratio',0)*100:.2f}% "
                      f"Excluded_R2_weak_symbols={mrc.get('excluded_r2_syms',0)} "
                      f"Frames={mrc.get('n_frames',0)}")
                w_log = mrc.get("weights", [])
                if w_log:
                    avg_w1 = float(np.mean([w.get("mean_w1_capped", 0.5) for w in w_log]))
                    avg_w2 = float(np.mean([w.get("mean_w2_capped", 0.5) for w in w_log]))
                    avg_ratio = float(np.mean([w.get("r2_valid_ratio", 0) for w in w_log]))
                    n_valid = sum(w.get("r2_valid_count", 0) for w in w_log)
                    n_total = sum(w.get("r2_total", 0) for w in w_log)
                    print(f"      Capped_weights: R1={avg_w1:.3f} R2={avg_w2:.3f} "
                          f"R2_valid_rate={avg_ratio*100:.1f}% ({n_valid}/{n_total})")

        # --- Deep fading recovery ---
        rec = r.get("recovery", {})
        if rec and rec.get("n_deep_fade", 0) > 0:
            print(f"    └ Recovery: {rec.get('summary', 'N/A')}")
            rt = rec.get("retransmit_indices", [])
            pb = rec.get("power_boost_indices", [])
            if rt:
                print(f"    └ Link_strategy: retransmit_recommended_frames={rt[:8]}, "
                      f"power_boost_frames={pb[:8]}")

        # --- Communication prior ---
        comm = r.get("comm_filter", {})
        if comm:
            print(f"    └ Comm_prior: removed_false_alarms={comm.get('total_removed', 0)}, "
                  f"comm_level_symbols={comm.get('total_comm', 0)}")

    print("  " + "-" * 134)
    print("  Pipeline: SRE_purification → Complex_path_preserve → Adaptive_symbol-level_diversity → Equalization → QPSK_demodulation")
    print("  Note: CxBER=direct decision after SRE purification | EqBER=after complex zero-forcing equalization")
    print("        MRC=max_ratio_combining | SC=select_strong_channel | EGC=equal_gain | Conf=confidence | Capped=weight_cap")
    print("        skip=diversity skipped due to low R2 power | Best=optimal_mode | Gain=diversity_gain(dB)")
    print("=" * 120 + "\n")


# =====================================================================
# Module 10: Program Entry — Enhanced Version
# =====================================================================

def plot_evaluation(stats, out_path=None):
    """Generate two subplot PNGs as required by idea.md Section 5.2."""
    if not stats or not stats.get("multipath_ratios"):
        logger.warning("No statistical data available for plotting")
        return
    mp = np.asarray(stats["multipath_ratios"], dtype=np.float64)
    sy = np.asarray(stats["symbol_counts"], dtype=np.float64)
    frames = np.arange(1, len(mp) + 1)
    mp_mean = mp.mean()
    sy_mean = sy.mean()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    band = stats.get("band", "?")
    rx = stats.get("receiver", "?")

    # Plot 1: Multipath interference suppression ratio
    axes[0].plot(frames, mp, "-o", color="#d62728", markersize=4,
                 label="Per-frame multipath suppression ratio")
    axes[0].axhline(mp_mean, color="#7f7f7f", linestyle="--",
                    label=f"Mean = {mp_mean:.4f}")
    axes[0].set_xlabel("Frame Index")
    axes[0].set_ylabel("Multipath Suppression Ratio")
    axes[0].set_title(f"[{band}/{rx}] Per-frame Multipath Interference Suppression Ratio")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.3)
    axes[0].set_ylim(-0.02, 1.02)

    # Plot 2: Effective communication symbol detection count
    axes[1].plot(frames, sy, "-s", color="#1f77b4", markersize=4,
                 label="Per-frame symbol detection count")
    axes[1].axhline(sy_mean, color="#7f7f7f", linestyle="--",
                    label=f"Mean = {sy_mean:.1f}")
    axes[1].set_xlabel("Frame Index")
    axes[1].set_ylabel("Detected Symbol Count")
    axes[1].set_title(f"[{band}/{rx}] Per-frame Effective Communication Symbol Detection")
    axes[1].legend(loc="best")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    if out_path is None:
        out_path = os.path.join(OUT_DIR,
                                f"eval_{band}_{rx}_{int(time.time())}.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Evaluation plot saved: %s", out_path)
    return out_path


def main():
    """Program entry: fixed random seed, supports three running modes.

    Environment variables:
        SRE_MODE: 'single' (single band) / 'multi' (multi-band comparison) / 'dual' (diversity)
        SRE_BAND: band LF/MF/HF
        SRE_RX: receiver R1/R2
        SRE_BANDS: multi-band list (default 'LF,MF,HF')
        SRE_MAX_FILES: max file count
        SRE_MAX_FRAMES: max frame count
    """
    np.random.seed(20260811)
    t_start = time.perf_counter()

    mode = os.environ.get("SRE_MODE", "single")
    max_files = int(os.environ.get("SRE_MAX_FILES", "2"))
    max_frames = int(os.environ.get("SRE_MAX_FRAMES", "30"))

    if mode == "multi":
        # --- Multi-band batch comparison ---
        bands_str = os.environ.get("SRE_BANDS", "LF,MF,HF")
        bands = [b.strip().upper() for b in bands_str.split(",")]
        logger.info("=" * 60)
        logger.info("Multi-band comparison mode: bands=%s files=%d frames=%d",
                    bands, max_files, max_frames)
        logger.info("=" * 60)
        results, dual_results = run_multi_band(
            bands=bands, max_files=max_files, max_frames=max_frames,
            include_dual=True,
        )

    elif mode == "dual":
        # --- Dual-channel diversity mode ---
        band = os.environ.get("SRE_BAND", "LF").upper()
        logger.info("=" * 60)
        logger.info("Dual-channel diversity mode: band=%s files=%d frames=%d",
                    band, max_files, max_frames)
        logger.info("=" * 60)
        dual = run_dual_channel_sre(
            band=band, max_files=max_files, max_frames=max_frames,
        )
        # Generate single-channel comparison
        stats_r1 = run_underwater_sre(
            band=band, receiver="R1",
            max_files=max_files, max_frames=max_frames,
            save_npy=True,
        )
        if stats_r1:
            plot_evaluation(stats_r1)
            det_rate = compute_detection_rate(
                stats_r1["symbol_counts"], band
            )
            logger.info("R1 detection rate: %.4f", det_rate.get("detection_rate", 0))

    else:
        # --- Single-band mode (default) ---
        band = os.environ.get("SRE_BAND", "LF").upper()
        receiver = os.environ.get("SRE_RX", "R1")
        logger.info("=" * 60)
        logger.info("SRE Underwater Data Pipeline Started: band=%s rx=%s files=%d frames=%d",
                    band, receiver, max_files, max_frames)
        logger.info("=" * 60)

        stats = run_underwater_sre(
            band=band, receiver=receiver,
            max_files=max_files, max_frames=max_frames,
            save_npy=True,
        )

        if stats:
            plot_evaluation(stats)
            # Detection rate
            det_rate = compute_detection_rate(
                stats["symbol_counts"], band
            )
            tx_frames = read_tx_symbols(band)
            n_align = min(len(stats.get("purified_blocks", [])),
                          len(tx_frames))
            if n_align > 0:
                puri_blocks = stats["purified_blocks"][:n_align]
                complex_blocks = stats.get("purified_complex_blocks", [])
                puri_complex = complex_blocks[:n_align] if complex_blocks else None
                tx_aligned = tx_frames[:n_align]

                # Energy path BER
                ber_energy = estimate_ber_qpsk(puri_blocks, tx_aligned)
                logger.info("SRE-BER (energy): %.6f", ber_energy.get("ber", 0))

                # Complex path BER
                if puri_complex:
                    ber_complex = estimate_ber_qpsk(
                        puri_blocks, tx_aligned,
                        purified_complex_blocks=puri_complex
                    )
                    logger.info("SRE-BER (complex): %.6f",
                                ber_complex.get("ber", 0))
                    logger.info("→ Phase preservation improvement: Δ=%.6f",
                                ber_energy.get("ber", 0) -
                                ber_complex.get("ber", 0))

                # Channel equalization (prioritize complex path)
                if puri_complex:
                    eq_res = channel_equalize_complex(
                        puri_complex, tx_aligned, band=band
                    )
                else:
                    eq_res = channel_equalize_purified(
                        puri_blocks, tx_aligned, band=band
                    )
                logger.info("Post-equalization BER: %.6f (Δ=%+.6f, type=%s)",
                            eq_res.get("post_ber", 0),
                            eq_res.get("ber_delta", 0),
                            eq_res.get("equalization_type", "energy"))

                # Deep fading recovery (enhanced: BER trigger + complex path + time-domain smoothing)
                ber_ref = ber_complex if puri_complex else ber_energy
                recovery_res = deep_fade_recovery(
                    puri_blocks,
                    eq_res.get("channel_gains", []),
                    eq_res.get("deep_fade_flags", []),
                    band=band,
                    per_frame_ber=ber_ref.get("per_frame_ber"),
                    purified_complex_blocks=puri_complex,
                )
                rec_blocks = recovery_res.get("recovered_blocks")
                if rec_blocks:
                    rec_complex = recovery_res.get("recovered_complex_blocks")
                    if rec_complex:
                        rec_ber = estimate_ber_qpsk(
                            rec_blocks[:n_align],
                            tx_aligned,
                            purified_complex_blocks=rec_complex[:n_align],
                        )
                    else:
                        rec_ber = estimate_ber_qpsk(
                            rec_blocks[:n_align],
                            tx_aligned,
                        )
                    logger.info("Post-recovery BER: %.6f (deep_fading=%d, high_BER_smoothed=%d, %s)",
                                rec_ber.get("ber", 0),
                                recovery_res.get("n_deep_fade", 0),
                                len(recovery_res.get("high_ber_indices", [])),
                                recovery_res.get("strategy", "?"))

                # Communication prior filter
                comm_res = communication_prior_filter(
                    puri_blocks, tx_aligned, band=band
                )
                logger.info("Comm-level detection rate: %.4f (false_alarms_removed=%d)",
                            comm_res.get("comm_detection_rate", 0),
                            comm_res.get("total_removed", 0))

    elapsed = time.perf_counter() - t_start
    logger.info("=== Pipeline Complete! Total elapsed %.2f seconds ===", elapsed)


if __name__ == "__main__":
    main()
