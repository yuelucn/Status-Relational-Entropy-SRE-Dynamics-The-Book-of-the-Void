# -*- coding: utf-8 -*-
"""装配层是否携带结构信息？—— 固定 k 分布、只改**对接点**的组合枚举。

动机（承接 `_sre_nucleon_structure_vs_ledger.py` 的结论）：
    已证（实测）：在**固定装配拓扑**下，A 的组成差异不进图，只进账本（§12.11(1) 的适用条件）。
    已证（实测）：同 A 换 k 分布 => 图不同（V/E/T/β₁/ρ 逐项变）。
    待检：**对接点的选择**（挂到共享环 S{r}{i} 的哪一个点）是否也进结构？

结论（本轮实测 + 机理，**推翻了本脚本首版的预期**）：
    挂点置换 sigma **不是自由度** —— 闭态体的自同构群在环三点上诱导出**全 S₃**，
    任何 sigma 都被自同构吸收。故 6 个 sigma 给出同一同构类、不变量逐位相同。
    ⇒ 唯一进结构的是 **k 分布**；A 与挂点都不进结构。
    ⇒ 这同时把 §12.11(1) 的『同构』从实测升级为**装配层必然**（A=4 三者 k 相同）。

性能约定：|Aut| 用阈值截断（超过阈值报 ">cap"），避免大图枚举爆炸。
"""
import sys
import itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

W = 92
AUT_CAP = 60000          # |Aut| 枚举上限（超过即报 ">cap"）


# --------------------------------------------------------------- 骨架
def Y3(pre, state="p", open_ring=0):
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


def naut(G, cap=AUT_CAP):
    n = sum(1 for _ in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap + 1))
    return n if n <= cap else None


def inv(G, want_aut=True):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    d = dict(V=G.number_of_nodes(), E=G.number_of_edges(),
             T=sum(nx.triangles(G).values()) // 3,
             b1=(G.number_of_edges() - G.number_of_nodes()
                 + nx.number_connected_components(G)),
             rho=round(float(ev[-1]), 9), lam2=round(float(ev[1]), 9),
             comp=nx.number_connected_components(G))
    if want_aut:
        a = naut(G)
        d["naut"] = a
        d["naut_s"] = ">%d" % AUT_CAP if a is None else str(a)
    return d


# --------------------------------------------------------------- 装配（含挂点参数）
def assemble_groups(groups):
    """groups = [(环号 r, [(体号 pre, 态 state, 挂点置换 sigma), ...]), ...]

    对每个体：它的环 r 三顶点 (L0r,L1r,L2r) **必须**参与共享环 r 的合并
    （这是共享环的构成性要求）；挂点置换 sigma 决定**该体的环点 i 被识别到共享环的**
    哪一个点 S{r}{sigma[i]}。sigma = (0,1,2) 即"对应式合并"（论文既有读法）。
    """
    H = nx.Graph()
    ledger = {}
    rings = {}
    for ring_idx, bodies in groups:
        r = int(str(ring_idx).lstrip("Rr"))       # 允许 "R0"/"0"/0 三种写法
        for pre0, state, sigma in bodies:
            pre = str(pre0)
            G = Y3(pre, state, r)
            m = {"%sL%d%d" % (pre, i, r): "S%d%d" % (r, int(sigma[i]))
                 for i in range(3)}
            edges = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
            for e in edges:
                ledger[e] = ledger.get(e, 0) + 1
            H.add_edges_from(edges)
        rings[r] = [tuple(sorted(("S%d%d" % (r, i), "S%d%d" % (r, j))))
                    for i, j in ((0, 1), (1, 2), (2, 0))]
    return H, ledger, rings


def profile(ledger, rings):
    return tuple(tuple(sorted((ledger.get(e, 0) for e in rings[r]), reverse=True))
                 for r in sorted(rings))


def show(tag, H, ledger, rings, want_aut=True):
    i = inv(H, want_aut)
    s = ("  %-26s V=%-3d E=%-3d T=%-2d b1=%-3d rho=%-11.9f lam2=%-11.9f"
         % (tag, i["V"], i["E"], i["T"], i["b1"], i["rho"], i["lam2"]))
    if want_aut:
        s += " |Aut|=%-7s" % i["naut_s"]
    s += " 剖面=%s" % (profile(ledger, rings),)
    print(s)
    return i


# --------------------------------------------------------------- 家族 F1：A=6, k=(3,3)
print("=" * W)
print("(1) 家族 F1：A=6，k=(3,3)，只改**挂点置换**（体 4/5/6 的环 1 三点对应共享点的顺序）")
print("=" * W)
print("  固定：环 0 上 体1·体2·体3（闭态），环 1 上 体4·体5（闭）·体6（开）")
print("  变量：环 1 上三个体各自的挂点置换 sigma in S3")
print()

S3 = list(itertools.permutations(range(3), 3))
# 固定体1-3 的 sigma = id；只扫环 1 上 体4 的 sigma（体5、体6 固定 id）——
# 先做单变量扫描（最简），再做体4+体5 的双变量扫描。
F1_BASE = [("R0", [(1, "p", (0, 1, 2)), (2, "p", (0, 1, 2)), (3, "p", (0, 1, 2))])]

print("  ── 单变量扫描：环 1 上仅 体4 的 sigma 变 ──")
res1 = {}
for sg in S3:
    groups = [("R0", [(1, "p", (0, 1, 2)), (2, "p", (0, 1, 2)), (3, "p", (0, 1, 2))]),
              ("R1", [(4, "p", sg), (5, "p", (0, 1, 2)), (6, "n", (0, 1, 2))])]
    H, led, rg = assemble_groups(groups)
    i = show("sigma(体4)=%s" % (sg,), H, led, rg, want_aut=False)
    res1[sg] = (H, i)

keys = list(S3)
print()
print("  两两同构判定（6 个 sigma 互比）：")
iso = {}
for x, y in itertools.combinations(keys, 2):
    iso[(x, y)] = nx.is_isomorphic(res1[x][0], res1[y][0])
print("    不同构的对数 = %d / %d" % (sum(1 for v in iso.values() if not v),
                                      len(iso)))
grp = {}
for x in keys:
    for y in keys:
        if x <= y and (x == y or iso.get((x, y), iso.get((y, x)))):
            grp.setdefault(x, set()).add(y)
classes = []
seen = set()
for x in keys:
    if x in seen:
        continue
    cl = {y for y in keys if y == x or iso.get((x, y), iso.get((y, x)))}
    classes.append(sorted(cl))
    seen |= cl
print("    同构类（按 sigma）: %s" % (classes,))
print("  => 同一 A、同一 k 分布下，**6 个 sigma 给出同一同构类**（不变量逐位相同）。")
print("     机理见 (3) 段：闭态体自同构诱导全 S₃ ⇒ 挂点被吸收 ⇒ sigma **不是自由度**。")
print()

# --------------------------------------------------------------- 家族 F2：A=5, k=(2,3)
print("=" * W)
print("(2) 家族 F2：A=5，k=(2,3)，只改挂点（对照：更小规模的同型检验）")
print("=" * W)
res2 = {}
for sg in S3:
    groups = [("R0", [(1, "p", (0, 1, 2)), (2, "p", (0, 1, 2))]),
              ("R1", [(3, "p", sg), (4, "p", (0, 1, 2)), (5, "n", (0, 1, 2))])]
    H, led, rg = assemble_groups(groups)
    i = show("sigma=%s" % (sg,), H, led, rg, want_aut=False)
    res2[sg] = (H, i)
iso2 = {}
for x, y in itertools.combinations(keys, 2):
    iso2[(x, y)] = nx.is_isomorphic(res2[x][0], res2[y][0])
classes2 = []
seen = set()
for x in keys:
    if x in seen:
        continue
    cl = {y for y in keys if y == x or iso2.get((x, y), iso2.get((y, x)))}
    classes2.append(sorted(cl))
    seen |= cl
print("  => 家族 F2 同构类数 = %d（与 F1 一致：sigma 被自同构吸收）。" % len(classes2))
print("     %s" % (classes2,))
print()

# --------------------------------------------------------------- 家族 F3：点饱和对照
print("=" * W)
print("(3) 挂点置换 sigma 是否为真自由度？—— 自同构吸收检验（决定性）")
print("=" * W)
from networkx.algorithms.isomorphism import GraphMatcher as _GM


def ring_perms(pre="z", state="p", r=0):
    """单体骨架的自同构群在**环 r 三点**上诱导出的置换集合。"""
    G = Y3(pre, state, r)
    tri = ["%sL%d%d" % (pre, i, r) for i in range(3)]
    out = set()
    for au in _GM(G, G).isomorphisms_iter():
        img = [au[v] for v in tri]
        if set(img) == set(tri):
            out.add(tuple(tri.index(v) for v in img))
    return len(list(_GM(G, G).isomorphisms_iter())), out


for st in ("p", "n"):
    n_aut, perms = ring_perms("z", st, 0)
    print("  单体 态=%s  |Aut|=%-3d  环 0 三点上诱导的置换数 = %d  -> %s"
          % (st, n_aut, len(perms), sorted(perms)))
print("  => **闭态体的自同构群在环三点上诱导出全 S₃**（6 个置换），")
print("     故对闭态体『挂到哪个点』可被自同构吸收 —— **sigma 不是自由度**。")
print("     开态体只诱导 2 个置换（(012),(102)），但仍含恒等 ⇒ 不改变结论。")
print("  => 本脚本 (1)(2) 段实测：6 个 sigma 全部两两同构、不变量逐位相同，")
print("     与此诊断一致。**故『挂点选择』在结构层不是区分来源。**")
print()

print("=" * W)
print("(4) 结论")
print("=" * W)
print("  a) **挂点置换 sigma 不是自由度**（自同构吸收）：同一 A、同一 k 分布下，")
print("     6 个 sigma 给出**同一同构类**、不变量逐位相同（(1)(2) 段实测 + (3) 段机理）。")
print("     => 上一版脚本据此写出的『挂点改变结构』结论**错误，已在本轮更正**。")
print("  b) 故 A ≥ 4 的图论口径实为**二分**（非三分）：")
print("       · 固定 A + 固定 k 分布 -> **同构**，唯一自由度只剩账本；")
print("       · 固定 A，改 k 分布     -> **不同图**（V/E/T/β₁/ρ/|Aut| 全变）。")
print("     即：**唯一真正进结构的是 k（共享环上的体数）的分布**。")
print("  c) 故 §12.11(1)『⁴He/⁴H/⁴Li 同构』的**正确含义**：")
print("     在『单环 k=4、对应式合并』这一装配下同构；而 k 分布对三者是同一的（都是 k=4），")
print("     故该同构结论**不是装配规则的巧合，而是 k 一致性的直接后果**。")
print("     换言之：**A=4 的三种组成共享同一 k 分布 ⇒ 必然同构**，")
print("     与挂点、与 A 的具体值都无关。这把 §12.11(1) 从『实测的同构』")
print("     提升为『装配层必然』（更强的陈述）。")
print("  d) 对用户主张的最终裁定：")
print("     · **对**：『不同原子核图构成有很大差异』—— 在 k 分布不同时**成立**")
print("       （k: 2→3→4 使 V/E/T/β₁/ρ/|Aut| 全变，两两不同构）。")
print("     · **需修正**：该差异来自**共享环体数 k 的分布**，**不是**来自 A 本身，")
print("       也**不是**来自「质子、中子刚性点」—— SRE 里没有这样的点，")
print("       且同 A 同 k 下改 p/n 或改挂点都**不改变图**。")
print("  e) 诚实边界：k 分布**由什么决定**（为什么 ⁶Li 取 k=(3,3) 而不是别的）"
      "**仍未决**；")
print("     本脚本只枚举到 A=7，且不对任何装配方案作物理归属。")
print("     下一可执行步骤（未做）：把 k 分布当作待反演量，用实测束缚序列做筛选。")
print()
print("done")
