"""v1.3 FINAL: authoritative 6-point chains (local + global), fits, seed-sigma, and main figure.
Consumes beta38_final_local.pkl, beta38_N12800.pkl, beta38_N12800_seed2.pkl, beta38_N25600.pkl.
Writes beta38_v13_final_output.txt and beta38_v13_main.png.
"""
import pickle, os
import numpy as np
from scipy.optimize import curve_fit
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE = r'c:\mywork\wei'; ALPHA = 783.2
OUT = os.path.join(BASE, 'beta38_v13_final_output.txt')
lines = []
def log(s=''):
    print(s); lines.append(str(s))
def load(f): return pickle.load(open(os.path.join(BASE, f), 'rb'))

# ---------- local beta helper ----------
def blocal(c1, c2):  # Lambda pair (0.005, 0.008) = two highest Re
    return -np.log(c1 / c2) / np.log((ALPHA / 0.005) / (ALPHA / 0.008))

d = load('beta38_final_local.pkl'); res = d['results']
locs, sig = {}, {}
for N in d['N_LIST']:
    vals = [blocal(res[(N, s, 0.005)], res[(N, s, 0.008)])
            for s in (0, 1) if (N, s, 0.005) in res and (N, s, 0.008) in res]
    locs[int(N)] = float(np.mean(vals))
    sig[int(N)] = float(np.std(vals, ddof=1)) if len(vals) > 1 else float('nan')

d0 = load('beta38_N12800.pkl'); ds = load('beta38_N12800_seed2.pkl'); d25 = load('beta38_N25600.pkl')
b128 = [float(d0['beta_local']), float(ds['beta_local'])]
locs[12800] = float(np.mean(b128)); sig[12800] = float(np.std(b128, ddof=1))
locs[25600] = float(d25['beta_local']); sig[25600] = float('nan')

N6 = np.array([800, 1600, 3200, 6400, 12800, 25600], float)
B6 = np.array([locs[int(n)] for n in N6])

log("=" * 74)
log("AUTHORITATIVE 6-POINT LOCAL-BETA CHAIN  (Lambda pair 0.005/0.008)")
log("=" * 74)
log(f"  {'N':>6s} {'beta_local':>10s} {'seed_sigma':>11s}  per-seed")
for i, N in enumerate(N6):
    if N == 12800:
        ps = [f"{b128[0]:.4f}", f"{b128[1]:.4f}"]
    elif N <= 6400:
        ps = [f"{blocal(res[(int(N),s,0.005)],res[(int(N),s,0.008)]):.4f}" for s in (0,1)]
    else:
        ps = [f"{locs[25600]:.4f} (1 seed)"]
    log(f"  {int(N):>6d} {B6[i]:>10.4f} {sig[int(N)]:>11.5f}  {ps}")
log(f"\n  N=12800 is now a 2-seed point: seed0={b128[0]:.4f}, seed2={b128[1]:.4f}, mean={locs[12800]:.4f} (sigma={sig[12800]:.5f})")

db = -np.diff(B6)
log("\n  Delta beta:")
for i in range(len(db)):
    r = f"  ratio={db[i]/db[i+1]:.3f}" if i < len(db) - 1 else ""
    log(f"    {int(N6[i])}->{int(N6[i+1])}: {db[i]:.4f}{r}")
log(f"  mean Delta beta (N>=3200) = {np.mean(db[2:]):.4f}")

# ---------- fits ----------
def r2(y, yp): return 1 - np.sum((y - yp) ** 2) / np.sum((y - y.mean()) ** 2)
m_log = lambda N, bi, a: bi + a / np.log(N)
m_pow = lambda N, bi, a, p: bi + a * N ** (-p)
m_p025 = lambda N, bi, a: bi + a * N ** (-0.25)
m_inv = lambda N, bi, a: bi + a / N
log("\n" + "=" * 74); log("6-POINT FITS"); log("=" * 74)
for name, m, p0, bd in [
    ("log   b_inf+a/logN", m_log, [0, 5], [(-2, 0), (2, 30)]),
    ("power free p", m_pow, [.2, 3, .28], [(-2, 0, .01), (3, 100, 3)]),
    ("power p=0.25", m_p025, [.2, 3], [(-2, 0), (3, 100)]),
    ("1/N", m_inv, [.4, 300], [(-2, 0), (5, 5000)]),
]:
    popt, pcov = curve_fit(m, N6, B6, p0=p0, bounds=bd, maxfev=500000)
    err = np.sqrt(np.diag(pcov)); yp = m(N6, *popt)
    extra = f", p={popt[2]:.4f}+/-{err[2]:.4f}" if name == "power free p" else ""
    log(f"  [{name}]  R2={r2(B6,yp):.6f}  b_inf={popt[0]:.4f}+/-{err[0]:.4f}{extra}  pred(25600)={float(m(25600,*popt)):.4f}")

# ---------- 3/8 rejection ----------
log("\n" + "=" * 74); log("3/8 REJECTION"); log("=" * 74)
seed_vals = [sig[int(n)] for n in N6 if np.isfinite(sig[int(n)])]
sig_ref = float(np.mean(seed_vals))
gap = B6[-1] - 0.375
log(f"  beta(25600)={B6[-1]:.4f}  3/8=0.3750  gap={gap:.4f}")
log(f"  mean seed-sigma (finite points) = {sig_ref:.5f}  -> gap = {gap/sig_ref:.1f} sigma")
extra_doublings = (B6[-1] - 0.375) / np.mean(db[2:])
log(f"  mean Delta beta (N>=3200)={np.mean(db[2:]):.4f}  -> need {extra_doublings:.2f} more doublings -> N ~ {25600*2**extra_doublings:.0f}")
log(f"  (N=51200 would need ~31 GB, infeasible)")

# ---------- global chain (appendix) ----------
log("\n" + "=" * 74); log("APPENDIX: GLOBAL-beta chain (curvature-contaminated, for cross-check)"); log("=" * 74)
gb = d['betas_global']
G6 = np.array([gb[800], gb[1600], gb[3200], gb[6400], float(d0['beta_global']), float(d25['beta_global'])])
log(f"  N:    {[int(n) for n in N6]}")
log(f"  global beta: {[f'{g:.4f}' for g in G6]}")
log(f"  -> at N=25600 the contaminated global chain reads {G6[-1]:.4f}, CLOSER to 3/8 than the clean local chain {B6[-1]:.4f}.")
log(f"     This is exactly why the old 3/8 claim was an artifact of the global (concave-curvature) fit.")

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(9.2, 6), dpi=150)
Nd = np.logspace(np.log10(800), np.log10(200000), 300)
for (name, m, p0, bd), c in zip(
        [("log", m_log, [0, 5], [(-2, 0), (2, 30)]),
         ("power free p", m_pow, [.2, 3, .28], [(-2, 0, .01), (3, 100, 3)]),
         ("p=0.25", m_p025, [.2, 3], [(-2, 0), (3, 100)]),
         ("1/N", m_inv, [.4, 300], [(-2, 0), (5, 5000)])],
        ['#1f77b4', '#d62728', '#2ca02c', '#7f7f7f']):
    popt, _ = curve_fit(m, N6, B6, p0=p0, bounds=bd, maxfev=500000)
    ax.plot(Nd, m(Nd, *popt), '-', color=c, lw=1.8, label=f"{name}  R2={r2(B6,m(N6,*popt)):.4f}")
ax.plot(N6, B6, 'ko-', ms=7, lw=2.3, label='clean local-beta chain (N=800..25600)')
ax.plot(N6, G6, 's--', ms=6, lw=1.5, color='#ff7f0e', label='global-beta chain (contaminated, appendix)')
ax.axhline(0.375, color='#8b0000', ls='--', lw=1.6)
ax.text(880, 0.379, '3/8 = 0.375  (v1.2 claim) -> rejected', color='#8b0000', fontsize=9)
ax.annotate(f'  {B6[-1]:.4f}\n  (+16% vs 3/8)', (25600, B6[-1]), fontsize=9, va='center')
ax.set_xscale('log'); ax.set_xlabel('N (system size)')
ax.set_ylabel(r'$\beta$  (local exponent of $1/C$ vs Re)')
ax.set_title('SRE finite-size scaling of $\\beta$ (v1.3): clean local chain vs contaminated global chain')
ax.grid(True, which='both', alpha=0.3); ax.legend(fontsize=8.5, loc='upper right'); ax.set_xlim(800, 200000)
plt.tight_layout(); plt.savefig(os.path.join(BASE, 'beta38_v13_main.png'), bbox_inches='tight')
log("\n[saved] beta38_v13_main.png")
open(OUT, 'w', encoding='utf-8').write("\n".join(lines) + "\n")
print(f"[saved] {OUT}")
