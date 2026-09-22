# -*- coding: utf-8 -*-
"""三体/四体：结构律核验 + 共享账本定价反演 + 候选定价律的残差。只做计算。"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MP, MN = 938.27208816, 939.56542052
DM = MN - MP                                   # 1.293332 MeV
B = {"d": 2.224566, "t": 8.4820, "He3": 7.7181, "a": 28.2957}
Bd = {k: v / DM for k, v in B.items()}
print("实测结合能（单位 Δm_np = %.6f MeV）:" % DM)
for k, v in Bd.items():
    print("   B(%-3s) = %8.6f   (%.4f MeV)" % (k, v, B[k]))

print()
print("=== 1. 结构律核验（v = 体数 k）===")
# 实测（_trimer.log）
obs = {"d": dict(k=2, V=21, E=33, T=5, b1=13, aut=48, lam2=0.267949192, rho=6.0),
       "t": dict(k=3, V=30, E=48, T=7, b1=19, aut=288, lam2=0.267949192, rho=6.925422918),
       "a": dict(k=4, V=39, E=63, T=9, b1=25, aut=2304, lam2=0.267949192, rho=7.909515966)}
print("  %-4s %-8s %-8s %-8s %-8s %-10s %-12s %-12s" %
      ("体", "V", "E", "T", "beta1", "|Aut|", "lam2", "rho"))
for k, o in obs.items():
    print("  %-4s %-8d %-8d %-8d %-8d %-10d %-12.9f %-12.9f" %
          (k, o["V"], o["E"], o["T"], o["b1"], o["aut"], o["lam2"], o["rho"]))
print()
print("  闭式检验：")
ok = True
for kk, o in obs.items():
    n = o["k"]
    f = {"V": 9 * n + 3, "E": 15 * n + 3, "T": 2 * n + 1, "b1": 6 * n + 1,
         "aut": 6 * (2 ** n) * __import__("math").factorial(n)}
    for key, val in f.items():
        if o[key] != val:
            ok = False
            print("     %s(%-3s) 实测 %d != 预测 %d" % (key, kk, o[key], val))
print("     V=9k+3, E=15k+3, T=2k+1, beta1=6k+1, |Aut|=6*2^k*k!  全部成立: %s" % ok)
print("     lam2 = 2-sqrt(3) = %.9f  对 k=2,3,4 完全相同: %s" %
      (2 - 3 ** 0.5, all(abs(o["lam2"] - (2 - 3 ** 0.5)) < 1e-9 for o in obs.values())))

print()
print("=== 2. 定价反演：B = G - Σ_e phi(k_e)，phi(1)=0 ===")
print("  各构形的账本（重合区三条边被多少体声称）:")
led = {"d": (1, 2, 2), "t": (1, 3, 3), "He3": (2, 3, 3), "a": (2, 4, 4)}
for k, L in led.items():
    print("     %-4s k 剖面 %s  -> Σphi = %s" % (k, L, " + ".join("phi(%d)" % x for x in L)))
print()
# 三条重叠区边之外，d/t/He3/a 的 phi(1)=0，其余边 k=1 不收费
print("  方程（phi(1)=0 已用掉）:")
print("     B_d          = G - 2phi(2)            = %.6f" % Bd["d"])
print("     B_t          = G - 2phi(3)            = %.6f" % Bd["t"])
print("     B_He3        = G - phi(2) - 2phi(3)   = %.6f" % Bd["He3"])
print("     B_a          = G - phi(2) - 2phi(4)   = %.6f" % Bd["a"])
p2 = Bd["t"] - Bd["He3"]
G = Bd["d"] + 2 * p2
p3 = (G - Bd["t"]) / 2
p4 = (G - p2 - Bd["a"]) / 2
print()
print("  解（前两条确定 phi(2)，第三条复核 phi(3)，第四条给出 phi(4)）:")
print("     phi(2) = B_t - B_He3            = %+.6f  Δm = %+.4f MeV" % (p2, p2 * DM))
print("     G      = B_d + 2phi(2)          = %+.6f  Δm = %+.4f MeV" % (G, G * DM))
print("     phi(3) = (G - B_t)/2            = %+.6f  Δm = %+.4f MeV" % (p3, p3 * DM))
print("     phi(4) = (G - phi(2) - B_a)/2   = %+.6f  Δm = %+.4f MeV" % (p4, p4 * DM))
print()
print("  自洽性复核 B_He3 预估值: %.6f  vs 实测 %.6f" % (G - p2 - 2 * p3, Bd["He3"]))
print("  价格比:  phi(3)/phi(2) = %+.4f ;  phi(4)/phi(2) = %+.4f" % (p3 / p2, p4 / p2))

print()
print("=== 3. 候选定价律的残差（用 d 定标，再预测 t / He3 / a）===")
def report(name, pred):
    print("  %-34s" % name)
    for kk in ("d", "t", "He3", "a"):
        d = (pred[kk] - Bd[kk]) / Bd[kk] * 100
        print("     %-4s 预测 %8.4f  实测 %8.4f  偏差 %+8.2f%%" % (kk, pred[kk], Bd[kk], d))

# 律1：逐边按 k 收费（phi(k) 自由）—— 上面已完全拟合，残差 0
p = {"d": G - 2 * p2, "t": G - 2 * p3, "He3": G - p2 - 2 * p3, "a": G - p2 - 2 * p4}
report("律1 逐边 · phi(k) 自由（必完美）", p)

# 律2：逐边按 k 线性收费 phi(k)=k*c
c = None
for kk in ("d",):
    c = (6.0 - Bd[kk]) / 4.0  # 6 = 2*n_closed(3)
print()
print("  【律2】增益=2×闭合边数=6，逐边收费 phi(k)=k·c，c 由 d 定:")
print("     c = (6 - B_d)/4 = %.6f" % c)
p = {"d": 6 - 4 * c, "t": 6 - 6 * c, "He3": 6 - 2 * c - 6 * c, "a": 6 - 2 * c - 8 * c}
report("律2 逐边线性收费", p)

# 律3：逐对收费 phi(k)=p*C(k,2)
p_ = (6.0 - Bd["d"]) / 2.0
print()
print("  【律3】增益=6，逐对收费 phi(k)=p·C(k,2)，p 由 d 定:")
print("     p = (6 - B_d)/2 = %.6f" % p_)
C = lambda k: k * (k - 1) / 2
p = {"d": 6 - 2 * p_ * C(2), "t": 6 - 2 * p_ * C(3), "He3": 6 - p_ * C(2) - 2 * p_ * C(3),
     "a": 6 - p_ * C(2) - 2 * p_ * C(4)}
report("律3 逐对收费", p)

print()
print("=== 4. 超可加性：结合能 / 逐对计数 ===")
for kk in ("d", "t", "a"):
    n = obs[kk]["k"]
    print("   %-4s k=%d  C(k,2)=%d  B/C(k,2) = %.4f" % (kk, n, C(n), Bd[kk] / C(n)))
print("   （若结合能只由'体数两两成对'决定，此列应恒定；实测 0.860 -> 1.093 -> 1.823，单调上升）")
