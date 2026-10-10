"""
验证脚本 (更新论文前的最后验证)
================================
V1. 口径冲突: N=800, seeds[0-4], 一致协议 → 确认 5-seed 与 2-seed 是否一致
     (此前 5-seed Test A=0.5139 vs 2-seed=0.5543, 决定 1/N 误判根因)

V2. 谱斜率有限尺寸检验: N=800/1600/3200/6400 低 Λ 平台
     论文 §6.6 声称 slope≈-1.85 且随 N 变陡; 检验是否有限尺寸效应
"""
import sys, time, pickle
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

ALPHA = 783.2
FIXED_WINDOW = 60
RE_LO = 5000.0


def evolve_and_measure(args):
    """返回 (tag, N, lam, seed, C, slope, frac_neg, aniso)"""
    sys.path.insert(0, r'c:\mywork\wei')
    from sre_core import evolve, measure
    tag, N, lam, seed = args
    M, _ = evolve(int(N), lam=float(lam), mode='exogenous', seed=int(seed))
    # C = 剪枝比例 (窗口平均)
    n_start = max(2, M.shape[0] - FIXED_WINDOW)
    Cs = []
    for n in range(n_start, N):
        if n < 2:
            continue
        Cs.append(np.sum((M[:n, n] > 0) & (M[n, :n] > 0)) / n)
    C = float(np.mean(Cs))
    m = measure(M)
    return (tag, int(N), float(lam), int(seed), C, m['slope'],
            m['frac_neg'], m['anisotropy'])


def fit_beta_from_C(C_by_lam, lams):
    Re = np.array([ALPHA / l for l in lams])
    C = np.array([C_by_lam[l] for l in lams])
    invC = 1.0 / C
    m = Re >= RE_LO
    lx = np.log10(Re[m]); ly = np.log10(invC[m])
    return float(np.polyfit(lx, ly, 1)[0])


def main():
    print("=" * 78, flush=True)
    print("更新论文前验证 V1(口径冲突) + V2(大N谱斜率)", flush=True)
    print("=" * 78, flush=True)

    PROTO_LAMS = [0.01, 0.05, 0.10, 0.20, 0.34]
    PROTO_SEEDS = [0, 1, 2, 3, 4]
    SLOPE_LAMS = [1e-3, 1e-2]
    SLOPE_NS = [800, 1600, 3200, 6400]
    SLOPE_SEEDS = [0, 1]

    tasks = []
    # V1: N=800 一致协议, 5 seeds
    for s in PROTO_SEEDS:
        for l in PROTO_LAMS:
            tasks.append(("V1", 800, l, s))
    # V2: 大 N 谱斜率 (N=6400 只用 Λ=1e-2 省时)
    for N in SLOPE_NS:
        lams = [1e-3, 1e-2] if N < 6400 else [1e-2]
        for l in lams:
            for s in SLOPE_SEEDS:
                tasks.append(("V2", N, l, s))

    print(f"总任务: {len(tasks)} (并行 max_workers=6)\n", flush=True)
    res = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(evolve_and_measure, t) for t in tasks]
        done = 0
        for fu in as_completed(futs):
            r = fu.result()
            res.append(r)
            done += 1
            if done % 5 == 0 or done == len(tasks):
                print(f"  [{done}/{len(tasks)}] {r[0]} N={r[1]} Λ={r[2]:.0e} "
                      f"s={r[3]} C={r[4]:.4f} slope={r[5]:+.4f} "
                      f"({time.time()-t0:.0f}s)", flush=True)

    # ---------------- V1 ----------------
    print("\n" + "=" * 78, flush=True)
    print("V1: N=800 一致协议 (window=60, RE_LO=5000) — 口径冲突", flush=True)
    print("=" * 78, flush=True)
    v1 = [r for r in res if r[0] == "V1"]
    C_by = {(r[3], r[2]): r[4] for r in v1}
    # per-seed β
    betas = {}
    for s in PROTO_SEEDS:
        betas[s] = fit_beta_from_C({l: C_by[(s, l)] for l in PROTO_LAMS}, PROTO_LAMS)
    print(f"  per-seed β(N=800): " +
          "  ".join(f"s{s}={betas[s]:.4f}" for s in PROTO_SEEDS), flush=True)
    b_all = np.array([betas[s] for s in PROTO_SEEDS])
    b_2 = np.array([betas[0], betas[1]])
    print(f"  5-seed mean β = {b_all.mean():.4f} ± {b_all.std():.4f}", flush=True)
    print(f"  2-seed(0,1) β = {b_2.mean():.4f} ± {b_2.std():.4f}", flush=True)
    print(f"  参考: 旧 5-seed Test A=0.5139, 一致协议(2seed)=0.5543", flush=True)
    print(f"  结论: {'口径冲突来自协议差异(非同协议)' if abs(b_all.mean()-0.5543)<0.02 else '需进一步排查'}", flush=True)

    # ---------------- V2 ----------------
    print("\n" + "=" * 78, flush=True)
    print("V2: 大 N 谱斜率 (论文 §6.6 声 -1.85 且随 N 变陡)", flush=True)
    print("=" * 78, flush=True)
    print(f"  {'N':>6s} {'Λ':>8s} {'slope(seed0)':>13s} {'slope(seed1)':>13s} {'mean':>9s} {'frac_neg':>9s}", flush=True)
    v2 = [r for r in res if r[0] == "V2"]
    slope_by = {}
    for N in SLOPE_NS:
        lams = [1e-3, 1e-2] if N < 6400 else [1e-2]
        for l in lams:
            ss = {r[3]: r[5] for r in v2 if r[1] == N and abs(r[2] - l) < 1e-12}
            fn = {r[3]: r[6] for r in v2 if r[1] == N and abs(r[2] - l) < 1e-12}
            s0 = ss.get(0, np.nan); s1 = ss.get(1, np.nan)
            mean = np.nanmean([s0, s1])
            slope_by[(N, l)] = mean
            print(f"  {N:6d} {l:8.0e} {s0:13.4f} {s1:13.4f} {mean:9.4f} "
                  f"{np.mean(list(fn.values())):9.4f}", flush=True)
    print("\n  论文 §6.6 (N=40..100, Λ=1e-3): -1.767, -1.847, -1.899, -1.932", flush=True)
    print("  → 检验: N 继续增大时 slope 是否继续变陡(有限尺寸效应)?", flush=True)

    out = dict(betas=betas, beta_5seed=float(b_all.mean()),
               beta_2seed=float(b_2.mean()), slope_by=slope_by,
               res=res)
    with open('verify_paper_claims.pkl', 'wb') as f:
        pickle.dump(out, f)
    print("\n已保存: verify_paper_claims.pkl", flush=True)


if __name__ == '__main__':
    main()