# -*- coding: utf-8 -*-
"""共享账本定价：反解 psi(k)、A=4 镜像预言、与拼接律的存在性记分。只做计算。"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MP, MN = 938.27208816, 939.56542052
DM = MN - MP
Bm = {"d": 2.224566, "t": 8.4820, "He3": 7.7181, "a": 28.2957}   # MeV
# 记账：psi(k) = 一条"被 k 个体声称"的重合区边的净贡献（Δm 单位）
# d (1,2,2)  t (1,3,3)  He3 (2,3,3)  a (2,4,4)
eq = {"d": (1, 2, 2), "t": (1, 3, 3), "He3": (2, 3, 3), "a": (2, 4, 4)}
B = {k: v / DM for k, v in Bm.items()}

# 线性系统：Σ n_k psi(k) = B
import itertools
ks = [1, 2, 3, 4]
rows = [[L.count(k) for k in ks] for L in eq.values()]
rhs = [B[x] for x in eq.keys()]
import fractions
from fractions import Fraction as F
A = [[F(int(x)) for x in r] + [F(rhs[i]).limit_denominator(10 ** 12)] for i, r in enumerate(rows)]
n = 4
for c in range(n):
    p = next(r for r in range(c, n) if A[r][c] != 0)
    A[c], A[p] = A[p], A[c]
    pv = A[c][c]
    A[c] = [v / pv for v in A[c]]
    for r in range(n):
        if r != c and A[r][c] != 0:
            f = A[r][c]
            A[r] = [a - f * b for a, b in zip(A[r], A[c])]
sol = [float(A[i][n]) for i in range(n)]
print("=== 反解 psi(k)（重合区一条边被 k 体声称时的净贡献）===")
print("  %-6s %-14s %-14s %-14s" % ("k", "psi(k)/Δm", "psi(k)/MeV", "相对 psi(1)"))
for i, k in enumerate(ks):
    print("  %-6d %+14.6f %+14.4f %+14.4f" %
          (k, sol[i], sol[i] * DM, sol[i] / sol[0]))
print()
print("  逐构形复核（psi1×count1 + ... ）:")
for tag, L in eq.items():
    pred = sum(L.count(k) * sol[i] for i, k in enumerate(ks))
    print("     %-4s 账本 %-10s 预测 %9.6f  实测 %9.6f  残差 %.2e Δm" %
          (tag, str(L), pred, B[tag], abs(pred - B[tag])))
print()
print("  【关键形态】psi 非单调：双占位是税、三/四占位是强增益")
print("     psi(2)/psi(1) = %+.4f  (双占位使该边贡献降到 %.1f%%)" % (sol[1] / sol[0], 100 * sol[1] / sol[0]))
print("     psi(3)/psi(1) = %+.4f ;  psi(4)/psi(1) = %+.4f" % (sol[2] / sol[0], sol[3] / sol[0]))

print()
print("=== A=4 同量异位素：外样本预言（psi 已被 A=2,3 与 4He 定死）===")
cases = {"4He  2p+2n  账本(2,4,4)": (2, 4, 4), "4H   1p+3n  账本(1,4,4)": (1, 4, 4),
         "4Li  3p+1n  账本(3,4,4)": (3, 4, 4)}
status = {"4He  2p+2n  账本(2,4,4)": "束缚 B=28.296 MeV",
          "4H   1p+3n  账本(1,4,4)": "不束缚（共振，阈上）",
          "4Li  3p+1n  账本(3,4,4)": "不束缚（共振，阈上）"}
for tag, L in cases.items():
    pred = sum(L.count(k) * sol[i] for i, k in enumerate(ks))
    print("  %-24s 预测 B = %8.4f Δm = %8.4f MeV   | 实测 %s" %
          (tag, pred, pred * DM, status[tag]))

print()
print("=== 拼接律的定性记分卡（零参数：缺口须由同位置的完整环边补齐）===")
score = [("n-p", "缺口 1，供给 1", "合法", "束缚 2.225 MeV", "✓"),
         ("n-n", "缺口 2，供给 0（同位置）", "非法", "不束缚", "✓"),
         ("p-p", "缺口 0，供给 2", "非法", "不束缚", "✓"),
         ("3H  2n+1p", "缺口 2，供给 1", "合法", "束缚 8.482 MeV", "✓"),
         ("3He 1n+2p", "缺口 1，供给 2", "合法", "束缚 7.718 MeV", "✓"),
         ("4He 2n+2p", "缺口 2，供给 2（可一一配对）", "合法", "束缚 28.296 MeV", "✓"),
         ("4H  3n+1p", "缺口 3，供给 1", "非法", "不束缚", "✓"),
         ("4Li 1n+3p", "缺口 1，供给 3", "合法→预言束缚", "不束缚", "✗")]
for a, b, c, d, e in score:
    print("  %-11s %-26s %-14s %-18s %s" % (a, b, c, d, e))
print()
print("  两个零参数读数并存且不兼容：")
print("    读法甲『供给数 ≥ 缺口数』：3H ✓、4Li ✗（预言束缚）")
print("    读法乙『供给数 = 缺口数（一一配对）』：4Li ✓、3H ✗（预言不束缚）")
