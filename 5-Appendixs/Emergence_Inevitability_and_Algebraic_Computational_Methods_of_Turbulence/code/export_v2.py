"""Generate the authoritative v2 dataset: dual-mode Lambda sweep + finite-size check.

Run from anywhere:  python code/export_v2.py
"""
import json
import math
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sre_core as core

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sanitize(o):
    """NaN / Infinity are not valid JSON — Python's json.dump writes them anyway,
    which breaks every strict parser (including JSON.parse in the browser).
    Convert them to null so the emitted file is always well-formed."""
    if isinstance(o, dict):
        return {k: sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [sanitize(v) for v in o]
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    return o

N = 60
SEEDS = (0, 1, 2, 3, 4)
LAMS = list(np.logspace(-4, 4, 17))

out = {"n": N, "seeds": len(SEEDS), "modes": {}}

for mode in ("exogenous", "adaptive"):
    rows = core.sweep(LAMS, n_steps=N, mode=mode, seeds=SEEDS)
    out["modes"][mode] = rows
    print("=== %s ===" % mode)
    print("%11s %10s | %8s %8s | %8s %8s | %8s" %
          ("Lambda", "Re~1/L", "frac_neg", "sd", "aniso", "sd", "slope"))
    for r in rows:
        print("%11.4g %10.4g | %8.4f %8.4f | %8.4f %8.4f | %8.3f" % (
            r["lam"], r["re"], r["frac_neg"], r["frac_neg_sd"],
            r["anisotropy"], r["anisotropy_sd"], r["slope"]))
    print()

# finite-size check: is the transition an artefact of N=60?
print("=== finite-size check (mode=exogenous) ===")
fs = []
for n_steps in (40, 60, 80, 100):
    for lam in (0.001, 0.1, 1.0):
        rows = core.sweep([lam], n_steps=n_steps, mode="exogenous", seeds=SEEDS)
        fs.append(dict(n=n_steps, lam=lam, frac_neg=rows[0]["frac_neg"],
                       slope=rows[0]["slope"], anisotropy=rows[0]["anisotropy"]))
        print("N=%3d  Lambda=%-6g  frac_neg=%.4f  slope=%+.3f  aniso=%.4f" % (
            n_steps, lam, rows[0]["frac_neg"], rows[0]["slope"], rows[0]["anisotropy"]))
out["finite_size"] = fs

with open(os.path.join(ROOT, "data", "phase_data_v2.json"), "w", encoding="utf-8") as f:
    json.dump(sanitize(out), f, indent=1, allow_nan=False)
print("\nwrote data/phase_data_v2.json")
