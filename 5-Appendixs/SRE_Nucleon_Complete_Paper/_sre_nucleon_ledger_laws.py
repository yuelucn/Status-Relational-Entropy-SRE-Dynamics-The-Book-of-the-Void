# -*- coding: utf-8 -*-
"""共享账本定价层：psi(k) 反解、两种简约定价律的偏差、A=4 外样本预言。只做计算。

记账模型：核的共享环上有 3 条重合边，每条按其"被多少个体声称"（k）定价 psi(k)；
核的结合能（单位 Delta m_np）即三条边价格之和。四个已测核的账本：
    d   (1,2,2)      t   (1,3,3)      He3 (2,3,3)      a(4He) (2,4,4)
四个方程恰好定死 psi(1..4)，故该层零预测余量；唯一有效检验是 A=4 的外样本。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from fractions import Fraction as F

MP, MN = 938.27208816, 939.56542052
DM = MN - MP
Bm = {"d": 2.224566, "t": 8.4820, "He3": 7.7181, "a": 28.2957}   # MeV
B = {k: v / DM for k, v in Bm.items()}
LED = {"d": (1, 2, 2), "t": (1, 3, 3), "He3": (2, 3, 3), "a": (2, 4, 4)}
KS = [1, 2, 3, 4]


def solve_psi():
    rows = [[L.count(k) for k in KS] for L in LED.values()]
    rhs = [B[x] for x in LED.keys()]
    A = [[F(int(x)) for x in r] + [F(rhs[i]).limit_denominator(10 ** 12)]
         for i, r in enumerate(rows)]
    n = 4
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0)
        A[c], A[p] = A[p], A[c]
        pv = A[c][c]
        A[c] = [v / pv for v in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]
                A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [float(A[i][n]) for i in range(n)]


psi = solve_psi()
print("=== 1. 反解 psi(k)：重合区一条边被 k 体声称时的净贡献 ===")
print("  %-4s %-14s %-14s %-14s" % ("k", "psi(k)/Δm", "psi(k)/MeV", "相对 psi(1)"))
for i, k in enumerate(KS):
    print("  %-4d %+14.6f %+14.4f %+14.4f" % (k, psi[i], psi[i] * DM, psi[i] / psi[0]))
print("  逐构形复核：")
for tag, L in LED.items():
    pred = sum(L.count(k) * psi[i] for i, k in enumerate(KS))
    print("     %-4s 账本 %-11s 预测 %9.6f  实测 %9.6f  残差 %.1e Δm"
          % (tag, str(L), pred, B[tag], abs(pred - B[tag])))
print("  形态：psi(2)/psi(1)=%+.4f（双占位使该边贡献降至 %.1f%%）、"
      "psi(3)/psi(1)=%+.4f、psi(4)/psi(1)=%+.4f"
      % (psi[1] / psi[0], 100 * psi[1] / psi[0], psi[2] / psi[0], psi[3] / psi[0]))


def report(name, psi_f):
    c = B["d"] / sum(LED["d"].count(k) * psi_f(k) for k in KS)
    print("  【%s】以氘核定标 c = %.6f" % (name, c))
    out = {}
    for tag, L in LED.items():
        pred = sum(L.count(k) * c * psi_f(k) for k in KS)
        out[tag] = pred
        dev = (pred - B[tag]) / B[tag] * 100
        print("     %-4s 预测 %8.4f Δm = %8.4f MeV  实测 %8.4f MeV  偏差 %+8.2f%%"
              % (tag, pred, pred * DM, Bm[tag], dev))
    return out


print()
print("=== 2. 两种简约定价律（只用氘核定一个常数）===")
report("律A 对 k 线性：psi(k)=k·c", lambda k: k)
print()
report("律B 对 k 逐对计数：psi(k)=c·C(k,2)", lambda k: k * (k - 1) / 2.0)

print()
print("=== 3. A=4 外样本：psi 已由 d/t/He3/4He 定死 ===")
cases = {"4He  2p+2n 账本(2,4,4)": ("a", "束缚 28.2957 MeV"),
         "4H   1p+3n 账本(1,4,4)": (None, "不束缚（阈上共振）"),
         "4Li  3p+1n 账本(3,4,4)": (None, "不束缚（阈上共振）")}
LED4 = {"a": (2, 4, 4), "4H": (1, 4, 4), "4Li": (3, 4, 4)}
for tag in ("4He  2p+2n 账本(2,4,4)", "4H   1p+3n 账本(1,4,4)", "4Li  3p+1n 账本(3,4,4)"):
    key = {"4He  2p+2n 账本(2,4,4)": "a", "4H   1p+3n 账本(1,4,4)": "4H",
           "4Li  3p+1n 账本(3,4,4)": "4Li"}[tag]
    L = LED4[key]
    pred = sum(L.count(k) * psi[i] for i, k in enumerate(KS))
    print("  %-24s 预测 B = %8.4f Δm = %8.4f MeV  | 实测 %s"
          % (tag, pred, pred * DM, cases[tag][1]))
print("  注：4He 的结合能已用于定死 psi(4)，故其'命中'不构成预言；")
print("      4H 与 4Li 为真正的零参数外样本，二者预言均高于 4He 而实测均不束缚。")

print()
print("=== 4. 结构层的模型无关事实（对照引用）===")
print("  线性律：V=9k+3, E=15k+3, T=2k+1, beta1=6k+1, |Aut|=6*2^k*k!  (k=2,3,4)")
for k in (2, 3, 4):
    import math
    print("     k=%d  V=%2d E=%2d T=%d beta1=%2d |Aut|=%4d"
          % (k, 9 * k + 3, 15 * k + 3, 2 * k + 1, 6 * k + 1, 6 * 2 ** k * math.factorial(k)))
print("  最低模：lambda2 = 2-sqrt(3) = %.12f，与体数 k 无关；(2-3^0.5)=%.12f"
      % (2 - 3 ** 0.5, 2 - 3 ** 0.5))
