# -*- coding: utf-8 -*-
"""第78轮补探针：T6 两项未过之后的追查。

(a) c(λ) 的标度：窗体太小会不会把斜率拉偏离 -1？把窗口推到 n>=200、上限 800 再看。
(b) 变体核 ratio'=λd/(E+1)^2 的 Ω 是否真的走向 0（猜想：失控冻结，
    因为改写越少 ⇒ M 越偏 +1 ⇒ E 越大 ⇒ 分母平方更大 ⇒ 改写更少）。
"""
import math

import numpy as np

import _time_emergence as TE


def part_a():
    print("=" * 74)
    print("(a) c(λ) 的标度随观察窗的移动")
    print("=" * 74)
    print("  %-6s %-12s %-12s %-12s" % ("λ", "c(窗口100-399)", "c(窗口200-799)", "比值"))
    rows = []
    for lam in (0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0):
        h, _ = TE.evolve(steps=800, lam=lam, seed=1111)
        cs = {}
        for lo, hi in ((100, 400), (200, 800)):
            ns = np.array([x["n"] for x in h if lo <= x["n"] < hi], dtype=float)
            ys = np.array([1 - x["omega"] for x in h if lo <= x["n"] < hi])
            f = np.log(ns) / np.sqrt(ns)
            cs[lo] = float(np.sum(ys * f) / np.sum(f * f))
        rows.append((lam, cs[100], cs[200]))
        print("  %-6.1f %-12.5f %-12.5f %-12.4f" % (lam, cs[100], cs[200],
                                                   cs[200] / cs[100]))
    for tag, col in (("窗口 100-399", 1), ("窗口 200-799", 2)):
        ls = np.array([r[0] for r in rows])
        cs = np.array([r[col] for r in rows])
        sl, inter = np.polyfit(np.log(ls), np.log(cs), 1)
        print("  %s：ln c 对 ln λ 的斜率 = %.4f  截距 %.4f" % (tag, sl, inter))
    print()


def part_b():
    print("=" * 74)
    print("(b) 变体核 ratio' = λd/(E+1)^2 ：是否失控冻结")
    print("=" * 74)
    print("  %-8s %-12s %-12s %-12s" % ("n", "Ω'", "⟨E⟩", "对照组 Ω"))
    hv, _ = TE.evolve_variant(steps=1100, exponent=2)
    h0, _ = TE.evolve(steps=1100)
    ov = {x["n"]: x["omega"] for x in hv}
    ev = {x["n"]: x["mean_E"] for x in hv}
    o0 = {x["n"]: x["omega"] for x in h0}
    for n in (100, 200, 400, 600, 800, 1000, 1099):
        print("  %-8d %-12.6f %-12.6f %-12.6f" % (n, ov[n], ev[n], o0[n]))
    print()
    sub = [x for x in hv if x["n"] >= 200]
    ns = np.array([x["n"] for x in sub], dtype=float)
    ys = np.array([x["omega"] for x in sub])
    sl, inter = np.polyfit(np.log(ns), np.log(ys), 1)
    print("  变体核 ln Ω' 对 ln n 的斜率 = %.4f" % sl)
    print("  若为负且不趋于平稳 ⇒ Ω' → 0 ⇒ 涌现时间确实停摆（相变到冻结相）。")
    print()


if __name__ == "__main__":
    np.seterr(all="ignore")
    part_a()
    part_b()
