# -*- coding: utf-8 -*-
"""
Class-2 breakdown-data falsification (step 1)
=============================================

Can the SRE single-parameter chain transition  sigma(Lambda)  reproduce the
real droplet secondary-breakup phase-diagram boundary  We_c(Oh) ?

Real-data side (published, table-ready; formula verified against literature):
  * Pilch & Erdman (1987):   We_c(Oh) = 12 * (1 + 1.077*Oh**1.6)
  * Regime boundaries (low-Oh asymptotes): bag ~18, multimode ~45,
    shear ~100-350, catastrophic ~350-2670  (We axis, shared Oh axis)

SRE side:  sre_core.sweep()  ->  structure density sigma = frac_neg vs Lambda.
           Only ONE control parameter (Lambda) exists in the chain.

Three escalating checks:
  A) monotone direction
  B) transition shape (number of plateaus / width / tail behaviour)
  C) dimensionality (1 scalar control vs a 2-D (Oh, We) regime partition)

METHODOLOGICAL CORRECTION (this run is NOT a falsification):
  * Until Lambda is anchored onto a physical dimensionless number, the shape of
    sigma(Lambda) carries no coordinate-invariant meaning: any monotone
    re-parameterisation of Lambda changes width / plateau structure. Shape
    comparisons below are therefore QUALIFYING observations only.
  * A single parametric curve CAN cover the 1-D boundary We_c(Oh) (a curve, not
    the 2-D regime plane), so the dimension observation limits the *plane*, not
    the boundary curve.
  * Legal status of this run:  UNDERDETERMINED / NOT YET TESTABLE.
    Falsification becomes possible only AFTER anchoring:
        pick  g  with  Lambda = g(Oh, We)
        fit its free coefficients on a subset of experimental points
        test prediction error on held-out points (leave-one-out)
    Only that second stage can support the word "falsified".

Run:  python SRE_v2/analysis/breakup_falsify.py
"""
import os
import sys
import json
import math
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "code"))
import sre_core as core

HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------- SRE side
N = 60
SEEDS = (0, 1, 2, 3, 4)
lams = np.logspace(-3.0, 2.0, 61)            # Lambda in [1e-3, 1e2]
rows = core.sweep(lams, n_steps=N, mode="exogenous", seeds=SEEDS)
lam = np.array([r["lam"] for r in rows])
sig = np.array([r["frac_neg"] for r in rows])
sig_sd = np.array([r["frac_neg_sd"] for r in rows])

# slope of the one-dimensional chiral-field proxy spectrum (for context)
slope = np.array([r["slope"] for r in rows])


def cross(lams_, vals, thr):
    """First Lambda where a monotone-decreasing series drops below thr."""
    idx = np.where(vals <= thr)[0]
    return float(lams_[idx[0]]) if len(idx) else float("nan")


THR = [0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.15, 0.10, 0.05]
lam_c = {t: cross(lam, sig, t) for t in THR}

# ----------------------------------------------------------------- real side
def we_c_pilch(Oh):
    return 12.0 * (1.0 + 1.077 * Oh ** 1.6)

Oh = np.logspace(-3.0, 1.0, 41)              # 0.001 .. 10
We = np.array([we_c_pilch(o) for o in Oh])

# log-log tail exponent
sl_lo = np.polyfit(np.log(Oh[:8]), np.log(We[:8]), 1)[0]
sl_hi = np.polyfit(np.log(Oh[-8:]), np.log(We[-8:]), 1)[0]

# regime boundaries on the We axis (low-Oh asymptotes)
REG = {"bag": 18.0, "multimode": 45.0, "shear": 100.0, "catastrophic": 350.0}


# ------------------------------------------------------------------- checks
res = {}

# ---- A) direction ---------------------------------------------------
res["A_direction"] = {
    "sre_sigma_at_Lam1e-3": float(sig[0]),
    "sre_sigma_at_Lam100": float(sig[-1]),
    "sre_monotone_down": bool(np.all(np.diff(sig[:-1]) <= 5e-3)),
    "real_We_c_at_Oh0.001": float(we_c_pilch(1e-3)),   # ~12 plateau
    "real_We_c_at_Oh10": float(we_c_pilch(10.0)),      # ~527, unbounded
    "real_tail_exponent_highOh": float(sl_hi),         # ~1.6 (power law)
    "real_plateau_exponent_lowOh": float(sl_lo),       # ~0 (saturation)
}

# ---- B) transition shape -----------------------------------------
sig_upper = float(np.nanmean(sig[sig > 0.45])) if np.any(sig > 0.45) else float("nan")
sig_lower = float(np.nanmean(sig[sig < 0.02])) if np.any(sig < 0.02) else float("nan")
w_sre = (math.log10(lam_c[0.05] / lam_c[0.45])
         if (lam_c[0.05] > 0 and lam_c[0.45] > 0) else float("nan"))

# transition width of the real boundary measured the same way:
# Oh span over which We_c climbs from 12.5 to ~100 (a fixed multiplicative band)
def _our_width(oh_lo, oh_hi):
    _l = [o for o in Oh if we_c_pilch(o) >= oh_lo and we_c_pilch(o) <= oh_hi]
    if len(_l) < 2:
        return float("nan")
    return float(math.log10(max(_l) / min(_l)))

res["B_shape"] = {
    "sre_upper_plateau": sig_upper,               # 2 plateaus (both ends saturate)
    "sre_lower_plateau": sig_lower,
    "sre_width_decades_45to05": w_sre,
    "real_We_range_decades": float(math.log10(We[-1] / We[0])),
    "real_width_decades_We12to100": _our_width(12.5, 100.0),
    "real_has_upper_plateau": False,   # grows as Oh^1.6, no saturation
    "real_has_lower_plateau": True,    # saturates to We_c = 12 as Oh->0
    "nplateau_sre": 2, "nplateau_real": 1,
}

# ---- C) dimensionality ------------------------------------------------
# On any vertical slice Oh = const, the real regime partition contains
# K distinct boundaries (bag/multimode/shear/catastrophic). A single scalar
# sigma(Lambda) can emit only ONE level per Lambda. The regime structure is a
# first-class output of the breakup phase diagram, not decoration.
res["C_dimensionality"] = {
    "sre_control_dimensions": 1,
    "real_control_dimensions": 2,           # (Oh, We) plane
    "regime_boundaries_on_Oh_slice": len(REG),
    "regime_boundaries_We": REG,
    "sre_levels_per_point": 1,
    "info_discarded_by_projection": "regime class (bag/multimode/shear/"
    "catastrophic) cannot be written as a function of a single scalar",
}

# ---- summary of Lambda_c ladder (the only "boundary" SRE can emit) ----
res["Lambda_c_ladder"] = {("sig<%.2f" % t): lam_c[t] for t in THR}

# ---- legal status -----------------------------------------------------
res["verdict"] = "UNDERDETERMINED / NOT YET TESTABLE (not falsified)"
res["why_not_falsified"] = (
    "Lambda is not yet anchored onto (Oh, We); until it is, sigma(Lambda) has no "
    "coordinate-invariant shape and the model emits no testable prediction. A "
    "single parametric curve can already cover the 1-D boundary We_c(Oh). "
    "Correct order: anchor -> predict -> test (leave-one-out).")
res["falsification_prerequisite"] = (
    "choose Lambda = g(Oh, We), fit g's coefficients on a subset of experimental "
    "points, then measure prediction error on held-out points.")
res["A_direction_note"] = "qualifying only (coordinate-invariant directions DO match)"
res["B_shape_note"] = "qualifying only (shape is not coordinate-invariant pre-anchor)"
res["C_dim_note"] = ("qualifying only: limits the 2-D regime PLANE, not the 1-D "
                     "boundary curve We_c(Oh)")

# write result
out_path = os.path.join(HERE, "breakup_falsify.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, allow_nan=False)

# ----------------------------------------------------------------- print
print("SRE  lambda -> structure-density transition  (N=%d, 5 seeds, mode=exogenous)"
      % N)
print("  Lambda      sigma      sd      slope(1D, ctx)")
for i in range(0, len(lam), 6):
    print("  %9.4g  %7.4f  %7.4f  %+7.2f"
          % (lam[i], sig[i], sig_sd[i], slope[i]))
print("  ...")
print()
print("A) direction")
print("  SRE : sigma(0.001)=%.4f -> sigma(100)=%.4f, monotone down: %s"
      % (sig[0], sig[-1], res["A_direction"]["sre_monotone_down"]))
print("  REAL: We_c(0.001)=%.2f -> We_c(10)=%.2f; tail exponent %.2f"
      % (we_c_pilch(1e-3), we_c_pilch(10.0), sl_hi))
print()
print("B) transition shape")
print("  SRE : plateaus=(%.3f .. %.3f), width %.2f decades (sigma 0.45->0.05)"
      % (sig_upper, sig_lower, w_sre))
print("  REAL: plateau count %d (low-Oh saturates at 12, high-Oh UNBOUNDED ^1.6);"
      % 1)
print("        We span %.2f decades over Oh 1e-3..10"
      % math.log10(We[-1] / We[0]))
print()
print("C) dimensionality (QUALIFYING ONLY)")
print("  SRE controls: 1 (Lambda)   |   REAL controls: 2 (Oh, We)")
print("  regime boundaries on one Oh slice: %d distinct We levels"
      % len(REG))
print("  -> limits the 2-D regime PLANE only; the 1-D boundary We_c(Oh) is a "
      "curve that a single parametric path CAN cover")
print()
print("  Lambda-crossing ladder (the only boundary family SRE can emit):")
for k, v in res["Lambda_c_ladder"].items():
    print("    %s : Lambda_c = %g" % (k, v))
print()
print("VERDICT (methodology-corrected) -------------------------------")
print("  %s" % res["verdict"])
print("  Why: %s" % res["why_not_falsified"])
print("  Falsification becomes possible only after: %s"
      % res["falsification_prerequisite"])
print()
print("  A/B/C above are QUALIFYING observations, not falsifications.")
print("  A: directions match (coordinate-invariant) -> supports anchorability")
print("  B: pre-anchor shape is NOT coordinate-invariant -> do not use")
print("  C: limits the 2-D regime PLANE only; 1-D boundary We_c(Oh) is coverable")
print()
print("wrote", out_path)
