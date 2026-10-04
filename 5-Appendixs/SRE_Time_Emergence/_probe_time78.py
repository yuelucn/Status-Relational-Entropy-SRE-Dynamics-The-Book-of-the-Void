# -*- coding: utf-8 -*-
"""第78轮探针：涌现时间 T = ∫Ω dn 中的 Ω(n) = ⟨改写率⟩ 的形态。

源码语义（务必对齐并被反复引用）：
    ratio = λ·d/(E+1),  ret(dorm) = 1/(1+ratio)      —— **保留率**
    p_matrix = 1 - ret                                —— **改写率（复位概率）**
    activate = rand >= p_matrix  ⇒ P(act) = ret ⇒ 保留率控制改写与否。
注意：名实反转已登记（源码变量 dorm 名「休眠」实为「历史保留率」）。
"""
import numpy as np

LAM = 0.8


def run(steps, lam=LAM, seed=1111, rec=()):
    np.random.seed(seed)
    M = np.array([[1]], dtype=np.int64)
    rows = []
    prof = {}
    for n in range(1, steps):
        E = np.abs(M.astype(np.float64) @ M.astype(np.float64))
        idx = np.arange(n)
        d = n - np.maximum(idx[:, None], idx[None, :])
        ratio = lam * d / (E + 1.0)
        ret = 1.0 / (1.0 + ratio)
        a = 1.0 - ret
        rows.append((n, float(a.mean()), float(ret.mean()),
                     float(np.median(ret)), float(E.mean())))
        if n in rec:
            df = d.ravel()
            cnt = np.bincount(df, minlength=n + 1)[1:].astype(float)
            sE = np.bincount(df, weights=E.ravel(), minlength=n + 1)[1:]
            sR = np.bincount(df, weights=ret.ravel(), minlength=n + 1)[1:]
            prof[n] = (cnt, sE / cnt, sR / cnt)
        rm = np.random.rand(n, n)
        rm = np.triu(rm) + np.triu(rm, 1).T
        act = rm >= a
        mask = np.where(act, M, 1)
        nb = np.prod(mask, axis=1)
        nb = np.where(np.any(act, axis=1), nb, 1)
        new_M = np.empty((n + 1, n + 1), dtype=np.int64)
        new_M[:n, :n] = M
        new_M[:n, n] = nb
        new_M[n, :n] = nb
        new_M[n, n] = -1 if np.sum(new_M[:n, :n]) >= 0 else 1
        M = new_M
    return rows, prof


if __name__ == "__main__":
    rows, prof = run(420, rec=(100, 400))
    print("  %-6s %-12s %-12s %-12s %-10s"
          % ("n", "Omega", "1-Omega", "ret_mean", "meanE"))
    show = (1, 2, 3, 5, 10, 20, 50, 100, 150, 200, 300, 400, 419)
    for r in rows:
        if r[0] in show:
            print("  %-6d %-12.6f %-12.6f %-12.6f %-10.4f"
                  % (r[0], r[1], r[2], r[3], r[4]))
    ns = np.array([r[0] for r in rows if r[0] >= 100], dtype=float)
    ys = np.array([r[2] for r in rows if r[0] >= 100])
    sl, _ = np.polyfit(np.log(ns), np.log(ys), 1)
    print()
    print("  log-log slope of (1-Omega) vs n  = %.4f" % sl)
    for name, f in (("n^-0.5", ns ** -0.5), ("ln n / n^0.5", np.log(ns) / np.sqrt(ns)),
                    ("n^-0.4", ns ** -0.4), ("n^-0.6", ns ** -0.6)):
        c = float(np.sum(ys * f) / np.sum(f * f))
        resid = ys - c * f
        print("    %-14s c=%-10.6f max rel resid = %7.3f%%"
              % (name, c, 100 * float(np.max(np.abs(resid) / ys))))

    print()
    print("  per-age profile at n=400 (d, count, meanE, mean_ret):")
    cnt, mE, mR = prof[400]
    step = 40
    for i in range(0, 400, step):
        print("    d=%-5d cnt=%-8.0f E=%-9.4f ret=%-9.6f"
              % (i + 1, cnt[i], mE[i], mR[i]))
