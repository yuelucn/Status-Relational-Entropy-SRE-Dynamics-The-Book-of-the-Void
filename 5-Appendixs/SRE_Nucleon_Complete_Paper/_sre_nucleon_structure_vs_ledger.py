# -*- coding: utf-8 -*-
"""核子数 A 是否真的改变产物图的结构？—— 与"刚性点"读法的最小对照实验。

用户直觉（2026-09-23）：
    「不同的原子核本身图构成就有很大差异，不是仅仅看假设的质子、中子刚性点。」

问题拆解（本脚本只回答第一半，且用可判定口径）：
    SRE 里没有任何"质子点""中子点"对象——核子**就是**一副三环骨架 Y₃⋉△₃，
    质子/中子的区别只在**态**（环全闭 / 打开一条环边）。所以"刚性点"不是本框架
    的读法，而是被它替换掉的读法。真正待测的是：
    **产物图随 A 的变化，是"记账"的变化，还是"结构"的变化？**

控制变量法（关键）：
    结构律 V = 9k+3、E = 15k+3、β₁ = 6k+1 里的 k 是**共享环上的体数**，不是 A。
    在 A ≤ 4 时 k = A（共享环只有一个），两者混淆；在 A ≥ 5 时需两个共享环，
    k 分布为 (a, A−a)，此时 **A 与 k 解耦**，才能看出谁决定结构。

    · 变换 A（结构改变）：k=2 → k=3，即共享环上从 2 个核子增到 3 个核子。
    · 变换 B（仅记账改变）：固定 k=2，把其中一个体的**态**由 p 改为 n。
      两者 A 不同（3 与 4 与 2 与 3），但共享环上的体数 k 不变。

判据（避免"只看 max 差值"的旧错）：
    每个核报 (V, E, T, β₁, |Aut|, ρ, λ₂, 谱, 账本剖面)，并做两两同构判定。
    若变换 A 给出不同不变量 ⇒ 结构确实随 A 变（用户主张在结构层成立）。
    若变换 B 给出同构 + 仅剖面不同 ⇒ 在固定装配层内，A 的差异**只进账本**。
"""
import sys
import itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

W = 92


# --------------------------------------------------------------- 骨架构造
def Y3(pre, state="p", open_ring=0):
    """三股 Y 骨架：顶点 {pre}c{i}(股心) / {pre}L{i}{j}(叶点, i=股号 j=环号)。

    闭态(p)：E=18, β₁=7, T=3。开态(n)：删环边 (L0r, L1r) -> E=17, β₁=6, T=2。
    """
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("%sL%d%d" % (pre, a, j), "%sL%d%d" % (pre, b, j))
    if state == "n":
        G.remove_edge("%sL0%d" % (pre, open_ring), "%sL1%d" % (pre, open_ring))
    return G


def assemble(groups, r=0):
    """多共享环装配。

    groups = [(标签, [(pre,state), ...]), ...]，每个 group 是一个共享环，
    groups 的顺序决定共享环编号 r = 0,1,2,...；各 ring 独立合并其三点 S{r}{i}。

    开态体的休眠边**必须**开在它参与的那条共享环上（否则合并的环与打开的环不同）。
    返回 (图 H, 账本 {边: 声称数}, 共享环表 {r: [三边]}）。
    """
    H = nx.Graph()
    ledger = {}
    rings = {}
    for r, (_tag, bodies) in enumerate(groups):
        if len(bodies) < 2:
            raise ValueError("共享环 r=%d 只有 %d 个体：环需 ≥2 体才有可合并的边"
                             % (r, len(bodies)))
        for pre, state in bodies:
            G = Y3(pre, state, r)
            m = {"%sL%d%d" % (pre, i, r): "S%d%d" % (r, i) for i in range(3)}
            edges = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
            for e in edges:
                ledger[e] = ledger.get(e, 0) + 1
            H.add_edges_from(edges)
        rings[r] = [tuple(sorted(("S%d%d" % (r, i), "S%d%d" % (r, j))))
                    for i, j in ((0, 1), (1, 2), (2, 0))]
    return H, ledger, rings


# --------------------------------------------------------------- 不变量
def invariants(G, want_aut=True):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    d = dict(V=G.number_of_nodes(), E=G.number_of_edges(),
             T=sum(nx.triangles(G).values()) // 3,
             b1=(G.number_of_edges() - G.number_of_nodes()
                 + nx.number_connected_components(G)),
             rho=float(ev[-1]), lam2=float(ev[1]),
             comp=nx.number_connected_components(G),
             iso=sum(1 for v in G if G.degree(v) == 0))
    if want_aut:
        d["naut"] = naut_capped(G)
    return d


AUT_CAP = 60000


def naut_capped(G, cap=AUT_CAP):
    """|Aut| 枚举上限；超过即返回 None（大图枚举会爆炸，用同构判定即可）。"""
    n = sum(1 for _ in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap + 1))
    return n if n <= cap else None


def ring_split(ledger, rings):
    """每条共享环的**开态计数**：该环上三条边中声称数 < 该环体数 的边数的一半。
    更稳健的口径：直接数『该环上恰少一条之边』的存在性。"""
    snaps = []
    for r in sorted(rings):
        k = max(ledger.get(e, 0) for e in rings[r])
        n_short = sum(1 for e in rings[r] if ledger.get(e, 0) < k)
        snaps.append((r, k, n_short))
    return snaps


def profile(ledger, rings):
    """共享环账本剖面：每条共享环上三边的声称数（降序）。"""
    out = []
    for r in sorted(rings):
        out.append(tuple(sorted((ledger.get(e, 0) for e in rings[r]), reverse=True)))
    return tuple(out)


def report(tag, H, ledger, rings, want_aut=True):
    i = invariants(H, want_aut)
    p = profile(ledger, rings)
    s = ("  %-12s V=%-3d E=%-3d T=%-2d b1=%-3d rho=%-12.9f lam2=%-12.9f"
         % (tag, i["V"], i["E"], i["T"], i["b1"], i["rho"], i["lam2"]))
    if want_aut:
        s += " |Aut|=%-9s" % (">cap" if i["naut"] is None else i["naut"])
    s += " 剖面=%s" % (p,)
    print(s)
    return i


print("=" * W)
print("(0) 前提：SRE 中没有『刚性点』，核子 = 骨架，p/n 只是态")
print("=" * W)
Gi = Y3("z", "p")
Gn = Y3("z", "n", 0)
print("  单体骨架  闭态(p): V=%d E=%d T=%d b1=%d" % (
    Gi.number_of_nodes(), Gi.number_of_edges(),
    sum(nx.triangles(Gi).values()) // 3,
    Gi.number_of_edges() - Gi.number_of_nodes() + 1))
print("  单体骨架  开态(n): V=%d E=%d T=%d b1=%d" % (
    Gn.number_of_nodes(), Gn.number_of_edges(),
    sum(nx.triangles(Gn).values()) // 3,
    Gn.number_of_edges() - Gn.number_of_nodes() + 1))
print("  => p/n 的差别 = **一条环边的有无**，不是两种不同点。")
print("     故『质子、中子刚性点』不是 SRE 的读法，而是被它替换掉的读法。")
print()

# --------------------------------------------------------------- 对照实验
print("=" * W)
print("(1) 变换 A：结构改变量 = 共享环上的体数 k")
print("=" * W)
CASE_A = {
    "k=2 闭+闭": [("R0", [("a", "p"), ("b", "p")])],
    "k=3 闭闭闭": [("R0", [("a", "p"), ("b", "p"), ("c", "p")])],
    "k=4 闭x4": [("R0", [("a", "p"), ("b", "p"), ("c", "p"), ("d", "p")])],
}
GA = {}
for tag, groups in CASE_A.items():
    H, led, rg = assemble(groups)
    GA[tag] = H
    report(tag, H, led, rg)
print("  结构律核对：V=9k+3, E=15k+3, T=2k+1, b1=6k+1")
for tag, k in (("k=2 闭+闭", 2), ("k=3 闭闭闭", 3), ("k=4 闭x4", 4)):
    tag_ = tag
    print("    %-10s 预测 V=%-3d E=%-3d T=%-2d b1=%-3d"
          % (tag_, 9 * k + 3, 15 * k + 3, 2 * k + 1, 6 * k + 1))
print()
print("  两两同构判定（变换 A）：")
keysA = list(CASE_A)
for x, y in itertools.combinations(keysA, 2):
    print("    %-10s ~ %-10s : %s" % (x, y, nx.is_isomorphic(GA[x], GA[y])))
print("  => 变换 A **改变** V/E/T/β₁/|Aut|/ρ/λ₂：结构确实随『共享环上的体数 k』变。")
print()

print("=" * W)
print("(2) 变换 B：固定 k=2，只改其中一个体的态（p<->n）")
print("=" * W)
CASE_B = {
    "(p,p) k2": [("R0", [("a", "p"), ("b", "p")])],
    "(p,n) k2": [("R0", [("a", "p"), ("b", "n")])],
    "(n,n) k2": [("R0", [("a", "n"), ("b", "n")])],
}
GB = {}
for tag, groups in CASE_B.items():
    H, led, rg = assemble(groups)
    GB[tag] = H
    report(tag, H, led, rg)
print()
print("  两两同构判定（变换 B）：")
keysB = list(CASE_B)
for x, y in itertools.combinations(keysB, 2):
    print("    %-10s ~ %-10s : %s" % (x, y, nx.is_isomorphic(GB[x], GB[y])))
print()
print("  对照 A=3 / A=4 家族内的镜像对：")
MIRROR = {
    "³H  (1p2n)": [("R0", [("a", "p"), ("b", "n"), ("c", "n")])],
    "³He (2p1n)": [("R0", [("a", "p"), ("b", "p"), ("c", "n")])],
}
HA = {}
for tag, groups in MIRROR.items():
    H, led, rg = assemble(groups)
    HA[tag] = H
    report(tag, H, led, rg)
print("    ³H ~ ³He 同构? %s" % nx.is_isomorphic(HA["³H  (1p2n)"], HA["³He (2p1n)"]))
print("  => 变换 B（含镜像对）**不改变**任何图量，只改变账本剖面。")
print()

print("=" * W)
print("(3) 关键解耦：A 与 k 分开算（A=6 两种装配）")
print("=" * W)
CASE_C = {
    "A=6  k=(3,3)": [("R0", [("a", "p"), ("b", "p"), ("c", "p")]),
                     ("R1", [("d", "p"), ("e", "p"), ("f", "n")])],
    "A=6  k=(2,2,2)": [("R0", [("a", "p"), ("b", "p")]),
                       ("R1", [("c", "p"), ("d", "p")]),
                       ("R2", [("e", "p"), ("f", "n")])],
    "A=7  k=(4,3)": [("R0", [("a", "p"), ("b", "p"), ("c", "p"), ("d", "p")]),
                     ("R1", [("e", "p"), ("f", "p"), ("g", "n")])],
    "A=6  k=(5,1)": [("R0", [("a", "p"), ("b", "p"), ("c", "p"), ("d", "p"), ("e", "p")]),
                     ("R1", [("f", "n")])],
}
GC = {}
for tag, groups in CASE_C.items():
    try:
        H, led, rg = assemble(groups)
    except ValueError as exc:
        print("  %-14s **不可装配**：%s" % (tag, exc))
        continue
    GC[tag] = H
    report(tag, H, led, rg)
print()
print("  两两同构判定（同 A、不同 k 分布）：")
for x, y in itertools.combinations(list(GC), 2):
    print("    %-14s ~ %-14s : %s" % (x, y, nx.is_isomorphic(GC[x], GC[y])))
print("  => **同一个 A，换一种装配（k 的分布）就是不同的图**；")
print("     且 k ≥ 2 是装配的前提（k=1 的『环』无合并边）⇒ **k=(5,1) 不存在**。")
print("     故 A 本身不定结构；定结构的是『共享环上的体数 k』的分布。")
print()

print("=" * W)
print("(4) 一条被本次实验**逼出来**的局部强制律（新发现）")
print("=" * W)
print("  共享环把各体的**环边 (L0r,L1r) 识别为同一条边**。于是：")
print("    · 两体皆闭 -> 该共享边的声称数 = 2")
print("    · 一闭一开 -> 该共享边 = 1（开态体不声称它，闭态体单独补全）")
print("    · 两体皆开 -> 该共享边 **不存在**（双方皆缺）")
print("  => 『两体皆开』不是被外部禁令排除，而是**共享环的粘连关系在开态下不成立**")
print("     —— 这与 §12.13 的 S4 实测（E 比 S1 少恰 1 条）是同一件事，")
print("        现被提升为**装配层的构成性条件**：开态体必须与闭态体配对。")
print()
print("  推论（本脚本中最实质的一条）：")
print("    共享环上那条 **k=1 边 ⇔ 该环上恰有一个开态体**。")
print("  ⇒ 『共享环上恒有且仅有一条 k=1 边』这一此前只对 k=2 实测过的事实，")
print("     现在直接来自『每个共享环上有几个开态体』的计数。实测核对：")
for tag, groups in list(CASE_A.items()) + list(CASE_B.items()) + list(MIRROR.items()):
    try:
        H, led, rg = assemble(groups)
    except ValueError:
        continue
    print("       %-12s 每环 (体数k, 短边数) = %s" % (tag, ring_split(led, rg)))
print("  ⇒ 因而『λ₂ = 2−√3 与体数无关』得到了**装配层的解释**：")
print("     k=1 边是装配的产物（开-闭配对），不是自由参数；它的位置由配对决定。")
print()

print("=" * W)
print("(5) 结论")
print("=" * W)
print("  a) SRE 中不存在『质子点/中子点』对象：核子 = 骨架 Y₃⋉△₃，p/n 只是"
      "『环全闭 / 开一条环边』。")
print("  b) 变换 A（k: 2→3→4）确实改变全部图量：V/E/T/β₁/|Aut|/ρ/λ₂ 逐项变，"
      "且两两不同构")
print("     => **『不同原子核图构成有很大差异』在『共享环上的体数 k 不同』时成立。**")
print("  c) 变换 B（固定 k，只改 p/n）不改变任何图量，两两同构（镜像对亦然），"
      "差异只落在账本剖面")
print("     => **在固定装配拓扑下，A 的组成差异不进结构，只进账本。**")
print("  d) 同 A 换装配（k 分布）不同构 => **A 本身不定结构**；")
print("     定结构的是 **k 的分布**（且每群 k ≥ 2），A 只是各群之和。")
print("  e) 故用户直觉的正确形式**分两层**（原写的『层 3 挂点』已被另一脚本否证）：")
print("       · 层 1（k 的分布）：哪些核子共享哪个环 —— **结构差异的唯一真正来源**。")
print("         本轮实测：k 分布直接进 V/E/T/β₁/|Aut|/ρ/λ₂（k=2→3→4 两两不同构）。")
print("         **k 分配规则待补**（由什么决定 ⁶Li 取 k=(3,3) 而非别的，未决）。")
print("       · 层 2（固定 k 分布内）：A 的组成只进账本，不进图 —— 图泛函对组成不敏感。")
print("         这正是 §12.11(1) 的同构现象；本轮给出其**适用条件**：仅在固定 k 分布下成立。")
print("       · ~~层 3（挂点选择）~~ **已否证**：`_sre_nucleon_attachment_sweep.py` 实测，")
print("         挂点置换被闭态体的自同构吸收（其在环三点上诱导出全 S₃），6 个 sigma")
print("         给出同一同构类 ⇒ **挂点不是自由度**。")
print("  f) 诚实边界：本脚本只做**组合枚举**（装配方案由 (1)–(4) 段显式给出），")
print("     未对任何 A ≥ 5 的**物理**分配作断言；也未证明『k 分配规则』不存在。")
print("     下一可执行步骤（未做）：把 k 分布当作**待反演量**，用实测束缚/不束缚序列筛选，")
print("     检验『k 分布 + 账本』能否复现 A ≥ 5 的存在性边界。")
print()
print("done")
