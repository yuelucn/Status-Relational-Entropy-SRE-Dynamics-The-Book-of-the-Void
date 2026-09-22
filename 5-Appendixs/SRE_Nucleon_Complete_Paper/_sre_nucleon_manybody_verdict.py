# -*- coding: utf-8 -*-
"""多体拼接律记分卡收口：把"缺口/供给"判据显式实现，逐项对照三种零参数读法，
   并按 A 区间（A<=3 可标定区 / A=4 隔离区）分区统计命中，输出采用的边界声明。

规则（零参数）：
  在同一共享位置上按"同位置"对齐 k 个核子骨架，其中
    n_open   = 开态（中子，该位置环边休眠）者个数，
    n_closed = 闭态（质子，该位置环边完整）者个数；
  定义  缺口 g = n_open ， 供给 s = n_closed 。
  读法甲  （本文裁决采用）：合法 ⟺ 1 <= g <= 2 且 s >= 1
  读法甲' （取消缺口上界的变体）：合法 ⟺ g >= 1 且 s >= 1
  读法乙  （一一配对）        ：合法 ⟺ g == s 且 g >= 1
  合法 ⇒ 预言束缚；非法 ⇒ 预言不束缚。
  仅含实测束缚态与阈上共振两种情形，无自由参数。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# (标签, A, g=缺口, s=供给, 实测是否束缚, 实测说明)
cases = [
    ("n-p",  2, 1, 1, True,  "束缚 2.2246 MeV（氘核）"),
    ("n-n",  2, 2, 0, False, "不束缚（虚态）"),
    ("p-p",  2, 0, 2, False, "不束缚（虚态）"),
    ("3H",   3, 2, 1, True,  "束缚 8.4820 MeV"),
    ("3He",  3, 1, 2, True,  "束缚 7.7181 MeV"),
    ("4He",  4, 2, 2, True,  "束缚 28.2957 MeV"),
    ("4H",   4, 3, 1, False, "不束缚（阈上共振）"),
    ("4Li",  4, 1, 3, False, "不束缚（阈上共振）"),
]

readings = [
    ("甲（采用）", lambda g, s: 1 <= g <= 2 and s >= 1),
    ("甲'（无上界变体）", lambda g, s: g >= 1 and s >= 1),
    ("乙（一一配对）", lambda g, s: g == s and g >= 1),
]

print("=== 多体拼接律零参数记分卡 ===")
print("  %-6s %-3s %-5s %-5s %-12s %-22s" % ("核", "A", "缺口g", "供给s", "实测", "说明"))
for tag, A, g, s, bound, note in cases:
    print("  %-6s %-3d %-5d %-5d %-12s %-22s" %
          (tag, A, g, s, "束缚" if bound else "不束缚", note))

print()
for name, rule in readings:
    print("=== 读法 %s ===" % name)
    hit_all = hit_le3 = 0
    n_all = n_le3 = 0
    misses = []
    print("  %-6s %-3s %-14s %-12s %-8s" % ("核", "A", "判定", "预言", "结果"))
    for tag, A, g, s, bound, note in cases:
        legal = rule(g, s)
        pred = legal
        ok = (pred == bound)
        n_all += 1
        hit_all += ok
        if A <= 3:
            n_le3 += 1
            hit_le3 += ok
        if not ok:
            misses.append((tag, A, legal))
        print("  %-6s %-3d %-14s %-12s %-8s" %
              (tag, A, "合法→束缚" if legal else "非法→不束缚",
               "束缚" if pred else "不束缚", "命中" if ok else "失配"))
    print("     全部 8 项命中 %d/%d；A<=3 分区命中 %d/%d" % (hit_all, n_all, hit_le3, n_le3))
    if misses:
        print("     失配项：%s" % ", ".join("%s(A=%d)" % (t, a) for t, a, _ in misses))
    else:
        print("     失配项：无")
    print()

print("=== 采用的裁决与边界 ===")
print("  1. 取读法甲（1 <= 缺口 <= 2 且 供给 >= 1）。")
print("     理由：甲在可标定区 A<=3 的 5 项上全部命中；乙在 3H（缺口2/供给1）")
print("     即失配，把实测束缚的 3H 判为不束缚，故被排除。")
print("  2. 甲的唯一失配为 4Li（A=4）：缺口1、供给3 → 判合法 → 预言束缚，实测不束缚。")
print("     若取消'缺口 <= 2'附加条款（读法甲'），4H 亦计入失配（缺口3、供给1 →")
print("     判合法 → 预言束缚，实测不束缚）。二者之差仅在 4H 一项，同属 A=4。")
print("  3. 采用的边界：A >= 4 的核束缚性（存在性与结合能数值）不在本层可算。")
print("     依据：定价层在 A=4 的外样本预言同样失败（4H 预言 29.06 MeV、")
print("     4Li 预言 31.42 MeV，均高于 4He 的 28.30 MeV，而二者实测均不束缚），")
print("     与拼接律的失配落在同一区间，构成对同一区间的两次独立标记。")
print("  4. 诚实登记：4He 的命中不构成预言（其结合能已用于定死 psi(4)）；")
print("     4H 与 4Li 共用同一读法，不能只保留其一。")
