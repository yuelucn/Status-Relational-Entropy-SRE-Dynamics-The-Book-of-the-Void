# -*- coding: utf-8 -*-
"""B1: k 分布由什么决定？—— 候选选择规则的系统检验

背景
----
§12.11(1′) 已确立：**A 不进结构，k 的分布才进结构**。
但「什么机制选定了 k 的分布」完全空白 —— 论文自标为头号新开放问题。

已知标定（论文只用过 A ≤ 4，全是单群）
    A=2 → k=(2,)    氘核 d
    A=3 → k=(3,)    ³H / ³He
    A=4 → k=(4,)    ⁴He / ⁴H / ⁴Li（三者同构，单环 k=4）
    A ≥ 5 → **完全未指定**

检验设计
--------
把「候选规则」写成只依赖 A 的映射，先写死、再检验，不做任何事后调参。

  T1 保真度：能否复现 A ≤ 4 的锚点（必要条件）
  T1b 锚点判别力核算：锚点集合到底能排除多少规则？（关键 —— 决定 B1 能否有定论）
  T2  A ≥ 5 的产物：各规则给出什么？是否满足形式约束（每群 k≥2、群数≤3）
  T3  内生 vs 外源：规则是否含 SRE 之外的自由参数
  T4  判定：k 分布可否由 SRE 内部唯一确定？
  T5  与 §12.12 的 L1 交叉检验：L1 能否替 B1 作结？

⚠ 纪律
  1. 多群样本是**并集**（E1）。故本脚本**只用**「群数 + 各群 k」这一组合结构，
     以及**并集下仍精确成立**的 V/E/β₁（E3 加和律）。
     不使用 ρ / λ₂ —— 它们对多群样本不可靠。
  2. 不引入拟合参数。
"""
import sys
from typing import Dict, List, Optional, Tuple

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANCHORS = {2: (2,), 3: (3,), 4: (4,)}
MAXG = 3   # E4：群数上限（Y3 只有 3 条叶环）


# ================================================================ 基本量
def kparts(n: int, minpart: int = 2, maxgroup: int = MAXG) -> List[Tuple[int, ...]]:
    """A=n 的全部 k 分布（每群 k≥2，群数≤maxgroup，降序，去重）。"""
    out = []

    def rec(rem, mx, cur):
        if rem == 0:
            if cur:
                out.append(tuple(cur))
            return
        if len(cur) >= maxgroup:
            return
        for kk in range(min(mx, rem), minpart - 1, -1):
            rec(rem - kk, kk, cur + [kk])

    rec(n, n, [])
    seen, uniq = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return sorted(uniq, key=lambda t: (-len(t), t))


def invariants_of(kd: Tuple[int, ...]) -> Dict[str, int]:
    """只用并集下仍精确成立的量（E3 加和律）+ 群数。"""
    return dict(V=sum(9 * k + 3 for k in kd),
                E=sum(15 * k + 3 for k in kd),
                b1=sum(6 * k + 1 for k in kd),
                n_group=len(kd), k_max=max(kd), k_min=min(kd))


# ============================================================ 候选规则族
def rule_single(A):
    """R1 单群：所有核子放进同一个共享环。"""
    return (A,) if A >= 2 else None


def rule_min_groups(A):
    """R5 最少群：与 R1 同式（冗余对照）。"""
    return (A,) if A >= 2 else None


def rule_max_groups(A, maxg=MAXG):
    """R2 最多群：尽量拆成 k=2 的小群（余数给一个 3）。"""
    if A < 2:
        return None
    if A == 2:
        return (2,)
    if A == 3:
        return (3,)
    if A == 4:
        return (2, 2)
    rest = A - 3
    if rest % 2:
        return None
    n2 = rest // 2
    if 1 + n2 > maxg:
        return None
    return tuple([3] + [2] * n2)


def rule_balanced(A, maxg=MAXG):
    """R3 均分：群数取 min(maxg, A//2)，再尽量均分。"""
    if A < 2:
        return None
    ng = min(maxg, A // 2)
    q, r = divmod(A, ng)
    parts = [q + 1] * r + [q] * (ng - r)
    parts = [p for p in parts if p >= 2]
    if not parts:
        return None
    return tuple(sorted(parts, reverse=True))


def rule_greedy(A, K_MAX=5):
    """R4 贪心填满：每群先填到 K_MAX 再开新群。**含自由参数 K_MAX**。"""
    if A < 2:
        return None
    parts = []
    rem = A
    while rem > 0:
        if len(parts) >= MAXG:
            return None
        k = min(K_MAX, rem)
        if k < 2:
            return None
        parts.append(k)
        rem -= k
    return tuple(parts)


def rule_alpha_cluster(A):
    """R6 α 团簇：先拆 4（借核物理的 α）。**含外源数字 4**。"""
    if A < 2:
        return None
    parts = []
    rem = A
    while rem >= 4:
        parts.append(4)
        rem -= 4
    if rem == 1:
        return None          # k=1 不可
    if rem >= 2:
        parts.append(rem)
    if not parts or len(parts) > MAXG:
        return None
    return tuple(sorted(parts, reverse=True))


RULES = [
    ("R1 单群 k=(A,)",              rule_single,      "内生",   "只依赖 A，无自由参数"),
    ("R2 最多群 尽量拆 2",           rule_max_groups,  "内生",   "只依赖 A，无自由参数"),
    ("R3 均分 群数=min(3,A//2)",     rule_balanced,    "内生",   "只依赖 A，无自由参数"),
    ("R4 贪心填满 K_MAX=5",          rule_greedy,      "外源",   "含自由参数 K_MAX=5，SRE 内无出处"),
    ("R5 最少群 =R1",                rule_min_groups,  "内生",   "与 R1 同式（冗余）"),
    ("R6 α 团簇 先拆 4",             rule_alpha_cluster, "外源", "借入核物理的 α，数字 4 来自实验"),
]


# ================================================================ T1
def part_T1():
    print("=" * 100)
    print("T1. 保真度：候选规则能否复现 A ≤ 4 的锚点（必要条件）")
    print("=" * 100)
    print()
    print("锚点 = 论文实际用过的全部：A=2→(2,)  A=3→(3,)  A=4→(4,)")
    print()
    print("%-26s %-6s %-6s %s" % ("规则", "保真", "类型", "逐例 (A: 给出 vs 应有)"))
    print("-" * 100)
    res = {}
    for name, rule, kind, _desc in RULES:
        rows = [(A, rule(A), ANCHORS[A]) for A in sorted(ANCHORS)]
        fid = all(got == want for _A, got, want in rows)
        res[name] = fid
        detail = "  ".join("%d:%s%s" % (A, got, "√" if got == want else "×")
                          for A, got, want in rows)
        print("%-26s %-6s %-6s %s" % (name, "是" if fid else "否", kind, detail))
    print()
    npass = sum(1 for v in res.values() if v)
    print("⇒ %d / %d 条规则保真。" % (npass, len(RULES)))
    print()
    print("⚠ **关键观察**：A=2 与 A=3 原本各只有 1 种划分，**没有判别力**；")
    print("   只有 A=4 有 2 种划分 —— 论文选了 (4,) 而非 (2,2)。")
    print("   ⇒ **锚点的全部判别力 = 这一次二元选择**（A=4：单群 还是 多群）。")
    print()
    return res


def part_T1b(res):
    print("=" * 100)
    print("T1b. 锚点判别力的核算（决定 B1 能否有定论）")
    print("=" * 100)
    print()
    print("逐 A 列出全部候选，看锚点池有多大：")
    print()
    for A in sorted(ANCHORS):
        ps = kparts(A)
        print("  A=%d : %d 种候选  %s" % (A, len(ps), ps))
    total = 1
    for A in sorted(ANCHORS):
        total *= len(kparts(A))
    print()
    print("  锚点池总大小 = %d × %d × %d = %d 种（k 分布三元组）" %
          (len(kparts(2)), len(kparts(3)), len(kparts(4)), total))
    print("  ⇒ 锚点最多能区分的规则数 = %d。" % total)
    print()
    print("但**任何合理规则**都被 A=2/A=3 的单一候选吸住，实际自由度只有 A=4：")
    print()
    print("  被 A=4 排除的规则类型：『A=4 时拆成多群』  → R2、R3 落此")
    print("  通过 A=4 的规则类型  ：『A=4 时保持单群』  → R1、R4、R5、R6 落此")
    print()
    print("⇒ **锚点有判别力，但只够做一次二元区分**：")
    print("   它排除了『多群派』，但**无法在『单群派』内部再作区分**。")
    print("   而『单群派』里 R1/R5 是纯内生，R4/R6 含外源输入。")
    print()
    return total


# ================================================================ T2
def part_T2():
    print("=" * 100)
    print("T2. A ≥ 5 的产物：各规则给出什么？是否满足形式约束？")
    print("=" * 100)
    print()
    print("形式约束（已确立，非拟合）：")
    print("  (a) 每群 k ≥ 2     —— k=1 的『环』无可合并之边")
    print("  (b) 群数 ≤ 3       —— E4，Y3 只有 3 条叶环")
    print()
    print("%-26s %s" % ("规则", "A=5..12 给出的 k 分布"))
    print("-" * 100)
    for name, rule, kind, _d in RULES:
        outs = []
        for A in range(5, 13):
            g = rule(A)
            outs.append("%d:%s" % (A, g if g is not None else "—"))
        print("%-26s %s" % (name, " ".join(outs)))
    print()
    print("（『—』表示该规则在此 A 不成形：或群数 >3、或出现 k=1）")
    print()


# ================================================================ T3
def part_T3():
    print("=" * 100)
    print("T3. 内生 vs 外源：规则是否含 SRE 之外的自由参数？")
    print("=" * 100)
    print()
    print("%-26s %-6s %s" % ("规则", "类型", "说明"))
    print("-" * 100)
    for name, _r, kind, desc in RULES:
        print("%-26s %-6s %s" % (name, kind, desc))
    print()
    print("⇒ **纯内生且无自由参数**的规则：R1 / R2 / R3（R5 与 R1 重复，不计）。")
    print("  R4 的 K_MAX、R6 的『4』都是外源输入 ⇒ 不算 SRE 内部规则。")
    print()
    print("⇒ 三条内生规则中，**R2 / R3 已被 A=4 锚点排除**（它们在 A=4 给多群）。")
    print("  剩下的**唯一**内生候选 = **R1（单群，k=(A,)）**。")
    print()


# ================================================================ T4
def part_T4(res):
    print("=" * 100)
    print("T4. 判定：k 分布可否由 SRE 内部唯一确定？")
    print("=" * 100)
    print()
    print("把『保真（过 T1）』与『内生（过 T3）』同时作为必要条件：")
    print()
    surv_raw = [n for n, r, k, _d in RULES if res[n] and k == "内生"]
    print("  保真且内生的规则（原始列表）= %s" % surv_raw)
    # 去重：按规则函数在 A=5..12 上的输出签名合并等价规则
    def sig(rule):
        return tuple(rule(A) for A in range(5, 13))
    seen, survivors = {}, []
    for n in surv_raw:
        rule = [r for nn, r, _k, _d in RULES if nn == n][0]
        s = sig(rule)
        if s in seen:
            print("    （%s 与 %s 输出签名相同 ⇒ 等价，合并）" % (n, seen[s]))
        else:
            seen[s] = n
            survivors.append(n)
    print()
    print("  去重后存活 = {%s}" % ", ".join(survivors))
    print()
    if len(survivors) > 1:
        print("  多解 ⇒ 不可唯一确定。")
    elif len(survivors) == 1:
        s = survivors[0]
        print("  **唯一存活**：%s" % s)
        print()
        outs = [RULES[[n for n, _r, _k, _d in RULES].index(s)][1](A)
                for A in range(5, 13)]
        print("  它在 A = 5..12 上给出：%s" % ", ".join(str(o) for o in outs))
        print()
        print("  ⚠ **但这个『唯一』须诚实限定**，理由有二：")
        print("    (1) 它靠的锚点是 **A ≤ 4 的 3 个点、且只有 1 次有效判别**（T1b）；")
        print("        样本极少 ⇒ 『唯一』是**弱结论**，不是强判别。")
        print("    (2) 被排除的 R4 / R6 是**因为含外源输入**被排除的，")
        print("        不是因为它们与实测冲突。若允许外源输入（这在本层是合理的），")
        print("        R4 / R6 在 A ≥ 5 上给出**与 R1 不同**的 k 分布 ⇒ **重新多解**。")
        print()
        print("  ⇒ 故正确的判定是：")
        print("    · **在『纯 SRE 内生』这一严格限制下**：k 分布 = (A,)，即**永远单群**。")
        print("      这是一个**可陈述的结论**（虽为弱结论）。")
        print("    · **一旦允许把核物理先验当输入**（如 α 团簇的 4、或 k 上限 K_MAX）：")
        print("      k 分布**不可由 SRE 内部唯一确定**。")
    print()


# ================================================================ T5
def part_T5():
    print("=" * 100)
    print("T5. 与 §12.12 的 L1 交叉检验：L1 能否替 B1 作结？")
    print("=" * 100)
    print()
    print("观察：**k 只记录『哪些核子的环合并了』，完全不记录 p/n 的分配。**")
    print("     故 (A, k 分布) 与 (A, #p) 是两个**独立**的自由度。")
    print()
    print("验证：A=6 的 4 种 k 分布，每种都能配满足 L1（|n_n−n_p| ≤ 1）的组成：")
    for kd in kparts(6):
        pairs = [(p, 6 - p) for p in range(7) if abs((6 - p) - p) <= 1]
        print("    k=%-12s  可实现组成: %s" %
              (str(kd), ", ".join("(#p=%d,#n=%d)" % (p, n) for p, n in pairs)))
    print()
    print("⇒ **k 分布与 L1 正交**：L1 管『p/n 怎么分』，k 管『谁跟谁共享环』。")
    print("   二者互不蕴含 ⇒ **L1 不能替 B1 作结**，B1 必须单独面对。")
    print("   （这也解释了为何 §12.12 能收口『存在性』却收不了『结构』。）")
    print()


def main():
    print("#" * 100)
    print("# B1: k 分布由什么决定？—— 候选选择规则的系统检验")
    print("#" * 100)
    print()
    print("问题：§12.11(1′) 留下『k 进结构』之后，")
    print("      **是什么机制选定了每个 A 对应哪个 k 分布？**")
    print()
    res = part_T1()
    total = part_T1b(res)
    part_T2()
    part_T3()
    part_T4(res)
    part_T5()
    print("=" * 100)
    print("结论摘要：")
    print("  1) 锚点池 = %d 种，但 A=2/A=3 无判别力，**有效判别只有 1 次**（A=4 单群 vs 多群）。" % total)
    print("  2) 该判别的**唯一作用**：排除『A=4 拆成多群』⇒ 排除 R2/R3。")
    print("  3) 剩下 R1/R4/R5/R6 都在 A=4 保真；其中 R4/R6 含外源输入，R5 = R1。")
    print("  4) ⇒ **严格内生条件下唯一存活的是 R1：k 分布 = (A,)，即永远单群。**")
    print("     但这是**弱结论**（锚点太少），且一旦允许核物理先验，R4/R6 重新入场 ⇒ 多解。")
    print("  5) ⇒ 最终判定分两种口径：")
    print("     · 纯 SRE 内生：k = (A,)（单群）—— 可陈述，但为弱结论；")
    print("     · 允许外源先验：k 分布**不可由 SRE 内部唯一确定**（与 §12.12 的 λ 同型）。")
    print("  6) L1 与 k 分布**正交**，L1 不能替 B1 作结。")
    print()
    print("  值得注意的正面含义：若取 R1（单群），则**所有 A 的 k 分布都是单群** ⇒")
    print("   §12.11(1′) 里 k=(3,3)、k=(2,2,2) 那类**多群样本并非物理构形**，")
    print("   它们从来就不是『某个核』的结构 —— 与 E1 的结论相互印证。")
    print("=" * 100)


if __name__ == "__main__":
    main()
