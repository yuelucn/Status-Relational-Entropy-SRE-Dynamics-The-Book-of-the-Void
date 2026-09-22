# -*- coding: utf-8 -*-
"""影子解（变体 D）的处置。只做计算。

三件待判事项：
(1) "变体 D"（三点全同贴环）是否真的是孤立影子解，还是第 12.5 节 k 体共享环家族
    在 k=2 时的成员？——若是，则"影子解"这一命名不成立。
(2) 原则 2 原文为"闭合体不可重叠"，带空间语义；而 SRE 本体论没有空间维度。
    能否把它改写为一个纯账本的、可判别的条件，并复现同样的排除？
(3) 变体 A（两点对接，仅一条边共享）与 D 型（三点重合，三条边共享）的账本差异。
"""
import sys
import itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ----------------------------------------------------------------- 骨架构造
def Y3(pre, state="p"):
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("%sL%d%d" % (pre, a, j), "%sL%d%d" % (pre, b, j))
    if state == "n":
        G.remove_edge("%sL00" % pre, "%sL10" % pre)
    return G


def build_sharedring(bodies, ring=0):
    """k 体共享同一个环 ring：该环三顶点合并为共享环 S 的三点。返回 (图, 账本)。"""
    H = nx.Graph()
    ledger = {}
    for pre, state in bodies:
        G = Y3(pre, state)
        m = {"%sL%d%d" % (pre, i, ring): "S%d" % i for i in range(3)}
        E = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
        for e in E:
            ledger[e] = ledger.get(e, 0) + 1
        H.add_edges_from(E)
    return H, ledger


def _ring0_edges(G, pre):
    """取 pre 号体环 0 的边。顶点命名为 %sL{i}{j}，其中 j 为环号、i 为股号，
    故环 0 的顶点名以 0 结尾（L00/L10/L20）。"""
    f = lambda v: str(v).startswith("%sL" % pre) and str(v).endswith("0")
    return {tuple(sorted((u, v))) for u, v in G.edges() if f(u) and f(v)}


def build_two_point(npre, ppre):
    """变体 A：中子缺口两端识别到质子的一条完整环边两端（两点对接）。"""
    N, P = Y3(npre, "n"), Y3(ppre, "p")
    rep = {"%sL00" % npre: "%sL00" % ppre, "%sL10" % npre: "%sL10" % ppre}
    H = nx.Graph()
    presence = {}
    for G in (N, P):
        for u, v in G.edges():
            e = tuple(sorted((rep.get(u, u), rep.get(v, v))))
            H.add_edge(*e)
            presence[e] = presence.get(e, 0) + 1
    # 环 0 的"位置需求"：中子环 0 与质子环 0 识别后各自需要哪三条边位置
    nv = [rep.get("%sL%d0" % (npre, i), "%sL%d0" % (npre, i)) for i in range(3)]
    pv = ["%sL%d0" % (ppre, i) for i in range(3)]
    nring = {tuple(sorted(e)) for e in itertools.combinations(nv, 2)}
    pring = {tuple(sorted(e)) for e in itertools.combinations(pv, 2)}
    served = {}
    for e in nring | pring:
        served[e] = (e in nring) + (e in pring)
    return H, presence, served, nring, pring


def inv(G, aut=True):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    d = dict(V=G.number_of_nodes(), E=G.number_of_edges(),
             T=sum(nx.triangles(G).values()) // 3,
             b1=G.number_of_edges() - G.number_of_nodes() + 1,
             rho=float(ev[-1]), lam2=float(ev[1]))
    if aut:
        d["naut"] = sum(1 for _ in itertools.islice(
            GraphMatcher(G, G).isomorphisms_iter(), 200000))
    return d


def show(tag, G, note="", aut=True):
    i = inv(G, aut)
    s = ("%-26s V=%-3d E=%-3d T=%-2d b1=%-3d rho=%-12.9f lam2=%-12.9f"
         % (tag, i["V"], i["E"], i["T"], i["b1"], i["rho"], i["lam2"]))
    if aut:
        s += " |Aut|=%-5d" % i["naut"]
    print(s + ("   %s" % note if note else ""))
    return i


def _is_ring_edge(e):
    return all(len(str(v)) > 1 and str(v)[0] == "S" and str(v)[1:].isdigit() for v in e)


def ledger_line(tag, ledger):
    items = sorted(((e, k) for e, k in ledger.items() if _is_ring_edge(e)),
                   key=lambda t: str(t[0]))
    prof = tuple(k for _, k in items)
    print("    %-22s 共享环三条边（被多少体声称）: %s   剖面=%s"
          % (tag, ", ".join("%s→%d" % (str(e), k) for e, k in items), prof))
    return prof


print("=" * 88)
print("(1) 变体 D 是否 = 第 12.5 节 k=2 成员？")
print("=" * 88)
D_np, L_np = build_sharedring([("a", "n"), ("b", "p")])
iD = show("D 型两体（n+p 共环0）", D_np, note="对照第 12.3 节登记值")
show("第 12.5 节 k=2（两闭体共环0）", build_sharedring([("a", "p"), ("b", "p")])[0])
print("    两者同构?", nx.is_isomorphic(D_np, build_sharedring([("a", "p"), ("b", "p")])[0]))
print("    D 登记值 V=21 E=33 T=5 b1=13 |Aut|=48 rho=6.000000 lam2=2-sqrt(3)=%.9f"
      % (2 - 3 ** 0.5))
print("    核验: rho 与整数 6 之差 %.2e ; lam2 与 2-sqrt(3) 之差 %.2e"
      % (abs(iD["rho"] - 6.0), abs(iD["lam2"] - (2 - 3 ** 0.5))))
print("    => 结论：D 不是孤立影子解，它就是共享环家族 k=2 的成员（与氘核同一构形）。")

print()
print("=" * 88)
print("(2) 原则 2 的非空间化改写与判别力")
print("=" * 88)
print("    原表述『闭合体不可重叠』含空间语义；SRE 本体论无空间维度，须改写为账本条件。")
print("    改写为：共享环上至少存在一条『单方声称边』（k=1）——即两体的映像在共享区可分辨。")
print()
cases = {
    "n-p": ([("a", "n"), ("b", "p")], "应有解"),
    "n-n": ([("a", "n"), ("b", "n")], "应无解（同位置双缺口）"),
    "p-p": ([("a", "p"), ("b", "p")], "应无解（无缺口可补）"),
}
graphs = {}
for tag, (bodies, expect) in cases.items():
    G, led = build_sharedring(bodies)
    graphs[tag] = G
    show("  两体 %s" % tag, G, note=expect, aut=True)
    prof = ledger_line(tag, led)
    closed = len(prof) == 3
    n1 = sum(1 for k in prof if k == 1)
    print("      共享环闭合 = %-5s（边数 %d）  k=1 单方声称边 %d 条 -> 可分辨 = %s"
          % (closed, len(prof), n1, closed and n1 >= 1))
    print("      判定：%s" % ("合法（预言束缚）" if (closed and n1 >= 1) else "非法（预言不束缚）"))
print()
print("    判定结果：")
print("      n-p：共享环 3 条边齐备，剖面 (1,2,2) 含 k=1 -> 合法")
print("      n-n：两侧同位置同休眠，重合后该边仍缺 -> 共享区只剩 2 条边，环不闭合 -> 非法")
print("      p-p：3 条边均被双方声称 (2,2,2)，无 k=1 -> 两体映像不可分辨 -> 非法")
print("    => 改写后的原则 2 复现了原有的全部排除，且不出现『重叠/位置』等空间词汇。")
print()
print("    关键对照：n-p 与 p-p 的图是否同构?", nx.is_isomorphic(graphs["n-p"], graphs["p-p"]))
print("    （同构 = 图本身不记得谁休眠；p-p 只能靠账本排除，不能靠图的任何不变量排除）")

print()
print("=" * 88)
print("(3) 变体 A（两点对接、单边共享）与 D 型（三点重合、三边共享）")
print("=" * 88)
HA, pres, served, nring, pring = build_two_point("n_", "p_")
show("  变体 A（n 缺口接 p 一条边）", HA, note="第 12.1 节登记值 V=22 E=35 b1=14 rho=6.681330644")
print("    A 的共享边——按『边同时出现在两个体的边集中』计: %s（%d 条）"
      % (sorted(str(e) for e, v in pres.items() if v == 2),
         len([1 for v in pres.values() if v == 2])))
print("    A 的共享边——按『一条边同时闭合两个环』（环服务）计: %s"
      % sorted(str(e) for e, v in served.items() if v == 2))
print("    中子环 0 的三条边: %s" % sorted(str(e) for e in nring))
print("    质子环 0 的三条边: %s" % sorted(str(e) for e in pring))
nA = len([1 for e, v in served.items() if v == 2])
print("    A 的双服务边数 = %d 条（只有借来的那一条同时闭合两个环）" % nA)
print("    D 型的共享边数 = 3 条（三条全由全体声称）")
print("    => 第 12.6 节的『共享环三条边各有声称数』记账，描述的只能是 D 型；")
print("       A 型只有一条共享边，无法承载 (1,2,2) 那样的三边剖面。")

print()
print("=" * 88)
print("(4) A=4 三种组成是否同一同构类？（记账层差异能否由图承载）")
print("=" * 88)
G_He4, L_He4 = build_sharedring([("a", "p"), ("b", "p"), ("c", "n"), ("d", "n")])
G_H4, L_H4 = build_sharedring([("a", "p"), ("b", "n"), ("c", "n"), ("d", "n")])
G_Li4, L_Li4 = build_sharedring([("a", "p"), ("b", "p"), ("c", "p"), ("d", "n")])
iHe4 = show("  4He  p,p,n,n", G_He4)
iH4 = show("  4H   1p,3n ", G_H4)
iLi4 = show("  4Li  3p,1n ", G_Li4)
print("    4He~4H 同构? %s ; 4He~4Li 同构? %s"
      % (nx.is_isomorphic(G_He4, G_H4), nx.is_isomorphic(G_He4, G_Li4)))
ledger_line("4He", L_He4)
ledger_line("4H ", L_H4)
ledger_line("4Li", L_Li4)
print("    => 三者的图（V/E/T/b1/rho/lam2/|Aut|）完全相同：A=4 同量异位素是同一同构类。")
print("       结合能若有差别，只能由账本承载，不可能由任何图泛函承载。")

print()
print("=" * 88)
print("(5) 影子解的处置结论")
print("=" * 88)
print("  a) D 不是影子解：它是共享环家族（第 12.5 节）k=2 的成员，与氘核同构同账本。")
print("  b) 原则 2 改写为账本条件（存在 k=1 单方声称边）后，D 不再是非法构形；")
print("     n-n、p-p 的排除由改写后的条件自动复现，且无需空间词汇。")
print("  c) 变体 A 作为『单边共享』构形仍合法但被氘核结合能定量排除（偏高 16.3%，第 12.2 节）。")
print("  d) 因此正确表述是：氘核的结构解为共享环构形（D 型），A 型被定量排除；")
print("     『影子解』这一命名与『违反原则 2』的旧说明应当撤回。")
print("  e) D 的保留价值仍在：rho=6 为精确整数、lam2=2-sqrt(3) 与体数无关，")
print("     后者即第 12.5 节『参照模』的 k=2 实例 —— 反概率特征由命名争议之外的事实承载。")
print()
print("done")
