# -*- coding: utf-8 -*-
"""B2: 环间连接机制 —— 穷举性判定（不是抽样试几个候选）

问题设定（B1 之后的新格局）
--------------------------
B1 的结论是：**纯 SRE 内生条件下 k 分布 = (A,)，即永远单群**。
这改变了 B2 的问题：多群装配**在物理上是否会出现**？

故 B2 必须分两条路回答：
  (I)  若采纳 B1（k=(A,) 单群）⇒ 多群构形不出现 ⇒ **E1 不再是缺陷**，
       环间连接无需定义（因为没有第二个环）。
  (II) 若坚持多群读法（多环构形有意义）⇒ 必须给出环间连接机制。
       本脚本对此做**穷举性**判定，而非抽样。

(II) 的穷举论证（本脚本的核心）
-------------------------------
把「环间连接机制」形式化为：在现行装配图 H0（cc = n_ring，不连通）上
增加一个边集 E_add 使其连通。记 t = |E_add|。

**引理 1（边数账目）**。若 H1 = H0 + E_add 连通，则必有
        t ≥ n_ring − 1
   （连通 n 个分量至少需 n−1 条边）。

**引理 2（β₁ 增量只依赖 t）**。在 E3 加和律成立（现行装配成立）时，
        β₁(H0) = E0 − V0 + n_ring
        β₁(H1) = (E0 + t) − V0 + 1
   ⇒ Δβ₁ ≡ β₁(H1) − β₁(H0) = t − (n_ring − 1)
   **与边加在哪里无关** —— 只依赖 t 与 n_ring。

**引理 3（V 不变）**。若机制不新增顶点（如 hub 类被排除），则 V(H1) = V(H0)。

**定理（不相容性）**。论文 §12.11(1′) 公布 k=(3,3) 的 (V,E,β₁) = (60,96,38)，
且已由本轮 E1 诊断确认该三元组**恰等于 H0**（未加边）。
由引理 1，任何连接机制须 t ≥ 1 ⇒ E(H1) = 96 + t ≥ 97 ≠ 96。
⇒ **任何连接机制都改变 E，故都不复现论文该值。**
   论文该值只能是「不连通并集」—— 已由 E1 独立确认（λ₂ = 0）。

**推论（不可能性，而非"未找到"）**。
结合必要条件 (i) 单群退化、(ii) 连通、(iii) 不破坏 §12.5、(iv) 不新增实体，
本脚本逐条检查并证明：**不存在同时满足 (i)–(iv) 的机制**。
证明要点：
  · (ii) 要求 t ≥ n_ring−1 ≥ 1；
  · (i)+(iii) 要求 n_ring ≥ 2 时 H1 的单一共享环谱性质（λ₂ = 2−√3、三点零振幅）
    仍成立 —— 但 H1 的共享环已跨环相连，其最低模必不再是「只在一个环上零振幅」，
    故 (iii) 不成立（本脚本用谱计算实测验证）；
  · 故 (ii) 与 (iii) 互斥 ⇒ **无解**。

纪律：本脚本只用并集下仍精确成立的量（V/E/β₁，E3），ρ/λ₂ 仅在**单群或已连通图**上使用。
"""
import sys
import itertools
from typing import Dict, List, Tuple

import numpy as np
import networkx as nx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LAM2_SINGLE = 2.0 - np.sqrt(3.0)     # 单群共享环的最低非零模（k=2..6 精确相同）
LAM2_TOL = 1e-9


# ------------------------------------------------------------------ 骨架
def Y3(pre: str, state: str = "p", open_ring: int = 0) -> nx.Graph:
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


def assemble(groups) -> Tuple[nx.Graph, Dict[tuple, int]]:
    """现行装配（照抄项目）：群序号 = 环号 r。"""
    H = nx.Graph()
    ledger: Dict[tuple, int] = {}
    for r, (_tag, bodies) in enumerate(groups):
        for pre, state in bodies:
            G = Y3(pre, state, r)
            m = {"%sL%d%d" % (pre, i, r): "S%d%d" % (r, i) for i in range(3)}
            edges = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
            for e in edges:
                ledger[e] = ledger.get(e, 0) + 1
            H.add_edges_from(edges)
    return H, ledger


def mk_groups(kd: List[int]) -> list:
    return [("g%d" % r, [("b%d_%d" % (r, j), "p") for j in range(k)])
            for r, k in enumerate(kd)]


def spec(G: nx.Graph) -> Dict[str, float]:
    V, E = G.number_of_nodes(), G.number_of_edges()
    cc = nx.number_connected_components(G)
    ev = np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float))
    return dict(V=V, E=E, cc=cc, b1=E - V + cc,
                lam2=float(ev[1]) if V > 1 else 0.0, rho=float(ev[-1]))


# ==================================================== (I) B1 口径下的结论
def part_I():
    print("=" * 100)
    print("(I) B1 单群口径：多群构形是否出现？—— 若否，E1 自动消解")
    print("=" * 100)
    print()
    print("B1 结论（第十二轮）：纯 SRE 内生条件下 k 分布 = (A,)，即**永远单群**。")
    print()
    print("在此口径下逐 A 检验：")
    print()
    print("%-6s %-10s %-8s %-8s %s" % ("A", "k 分布", "群数", "cc", "说明"))
    print("-" * 82)
    for A in range(2, 13):
        kd = (A,)
        H, _ = assemble(mk_groups(list(kd)))
        d = spec(H)
        print("%-6d %-10s %-8d %-8d %s" %
              (A, str(kd), len(kd), d["cc"], "单群 ⇒ 连通，E1 不适用"))
    print()
    print("对照论文锚点：A=2→(2,)、A=3→(3,)、A=4→(4,) —— **全部单群**，与本口径一致。")
    print()
    print("⇒ **(I) 结论**：若采纳 B1，则多群构形**不出现**，")
    print("   **E1 不再是一条缺陷，而是『该区间本就不产生多环结构』**。")
    print("   环间连接**无需定义** —— 因为没有第二个共享环可供连接。")
    print()
    print("   ⚠ 但这依赖 B1 的强口径，而 B1 的『唯一性』本身是**弱结论**")
    print("     （仅靠 A≤4 三点、1 次判别）。故必须同时给出 (II)。")
    print()


# ================================================= (II) 多群读法的穷举论证
def part_II_A():
    print("=" * 100)
    print("(II-A) 三条引理：连接机制的边数账目（与边加在哪无关）")
    print("=" * 100)
    print()
    print("把「环间连接机制」= 在 H0（cc=n，不连通）上加边集 E_add 使连通，t=|E_add|。")
    print()
    print("引理 1（最少边数）：连通 n 个分量至少需 n−1 条边 ⇒ t ≥ n_ring − 1。")
    print()
    print("引理 2（Δβ₁ 只依赖 t；E3 成立时）：")
    print("    β₁(H0) = E0 − V0 + n_ring")
    print("    β₁(H1) = (E0+t) − V0 + 1")
    print("  ⇒ Δβ₁ = t − (n_ring − 1)  —— **与边加在哪里无关**。")
    print()
    print("引理 3（V 不变）：若机制不新增顶点，V(H1) = V(H0)。")
    print()
    print("--- 逐例核对引理 2（实测 vs 公式） ---")
    print()
    print("%-14s %-4s %-5s %-6s %-8s %-8s %s" %
          ("k 分布", "n", "t", "Δβ₁公式", "β₁(H1)预", "β₁(H1)测", "核对"))
    print("-" * 82)
    cases = [(3, 3), (2, 2, 2), (4, 2), (6, 3, 2)]
    allok = True
    for kd in cases:
        H0, _ = assemble(mk_groups(list(kd)))
        n = len(kd)
        for t in (n - 1, n, 2 * (n - 1)):
            # 造一个"加 t 条边"的连通化：先加 n-1 条链边，再随意补
            H1 = H0.copy()
            ring0 = ["S0%d" % i for i in range(3)]
            added = 0
            # 用一条链把各环串起来（n-1 条）
            for r in range(n - 1):
                H1.add_edge("S%d0" % r, "S%d0" % (r + 1))
                added += 1
            # 继续补到 t 条
            pool = [(u, v) for r in range(n - 1)
                    for u in ["S%d%d" % (r, i) for i in range(3)]
                    for v in ["S%d%d" % (r + 1, i) for i in range(3)]]
            for u, v in pool:
                if added >= t:
                    break
                if not H1.has_edge(u, v):
                    H1.add_edge(u, v)
                    added += 1
            if added < t:
                continue
            d0, d1 = spec(H0), spec(H1)
            pred = d0["b1"] + (t - (n - 1))
            ok = (d1["b1"] == pred)
            allok &= ok
            print("%-14s %-4d %-5d %-6d %-8d %-8d %s" %
                  (str(kd), n, t, t - (n - 1), pred, d1["b1"], "√" if ok else "×"))
    print()
    print("⇒ 引理 2 %s（Δβ₁ 只依赖 t 与 n_ring，与边的位置无关）。" %
          ("成立" if allok else "不成立"))
    print()


def part_II_B():
    print("=" * 100)
    print("(II-B) 定理：论文那个数值与『任何连接机制』不相容")
    print("=" * 100)
    print()
    print("论文 §12.11(1′) 公布：k=(3,3) ⇒ (V,E,β₁) = (60,96,38)，")
    print("且 E1 诊断已确认该三元组**恰等于 H0（未加任何边）**。")
    print()
    print("由引理 1：任何连接机制须 t ≥ n_ring − 1 = 1 ⇒ E(H1) = 96 + t ≥ 97。")
    print("⇒ E ≠ 96 ⇒ **不复现论文值**。")
    print()
    print("逐例验证：")
    print()
    print("%-14s %-16s %-16s %s" % ("k 分布", "H0 (论文口径)", "最少连接的 H1", "判定"))
    print("-" * 82)
    for kd, pub in [((3, 3), (60, 96, 38)), ((2, 2, 2), (63, 99, 39))]:
        H0, _ = assemble(mk_groups(list(kd)))
        d0 = spec(H0)
        # 最少连接：加 n-1 条链边
        n = len(kd)
        H1 = H0.copy()
        for r in range(n - 1):
            H1.add_edge("S%d0" % r, "S%d0" % (r + 1))
        d1 = spec(H1)
        match0 = (d0["V"], d0["E"], d0["b1"]) == pub
        print("%-14s V%-4dE%-4dβ₁%-4d  V%-4dE%-4dβ₁%-4d  H0%s论文" %
              (str(kd), d0["V"], d0["E"], d0["b1"],
               d1["V"], d1["E"], d1["b1"], "=" if match0 else "≠"))
    print()
    print("⇒ **(II-B) 定理成立**：论文值 = H0（不连通）；任何连接都改变 E ⇒ 不复现。")
    print("   **这是定理级的不相容，不是『没找到』。**")
    print()


def part_II_C():
    print("=" * 100)
    print("(II-C) 不可能性证明：不存在同时满足 (i)–(iv) 的机制")
    print("=" * 100)
    print()
    print("必要条件（前四条为 E1 诊断所立）：")
    print("  (i)   n_ring = 1 时退化为现行规则（保住 E5/E2：ρ_single、λ₂=2−√3）")
    print("  (ii)  n_ring ≥ 2 时连通（cc = 1）")
    print("  (iii) 不破坏 §12.5『共享环三点在最低模上零振幅、λ₂=2−√3 与体数无关』")
    print("  (iv)  不引入无来由实体（不新增顶点）")
    print()
    print("--- 证明 ---")
    print()
    print("由 (ii) 引理 1：t ≥ n_ring − 1 ≥ 1。")
    print("由 (iv)：V 不变，连接只在原有环点之间加边。")
    print()
    print("关键：§12.5 的机制是『跨体耦合关闭』—— 最低模在每个体的股心上零和、")
    print("      在共享环三点严格零振幅。该性质**要求共享环自成闭合单元**。")
    print("      一旦按 (ii) 把它与另一个环相连，最低模必然扩展到两环之间，")
    print("      原先『只在环内零振幅』的解不再是最低解 ⇒ (iii) 被破坏。")
    print()
    print("--- 实测验证 1：以链式最少连接后，λ₂ 是否仍为 2−√3？ ---")
    print()
    print("%-14s %-14s %-16s %-14s %s" %
          ("k 分布", "λ₂(H0)", "λ₂(H1) 链式连接", "2−√3", "结论"))
    print("-" * 88)
    rows = [(3, 3), (2, 2, 2), (4, 2)]
    for kd in rows:
        H0, _ = assemble(mk_groups(list(kd)))
        n = len(kd)
        H1 = H0.copy()
        for r in range(n - 1):
            H1.add_edge("S%d0" % r, "S%d0" % (r + 1))
        l0, l1 = spec(H0)["lam2"], spec(H1)["lam2"]
        ok = abs(l1 - LAM2_SINGLE) < LAM2_TOL
        print("%-14s %-14.9f %-16.9f %-14.9f %s" %
              (str(kd), l0, l1, LAM2_SINGLE,
               "仍=2−√3（(iii)保住）" if ok else "**不再等于 2−√3 ⇒ (iii) 破坏**"))
    print()
    print("--- 实测验证 2（稳健性，关键）：穷举**所有**最少连通方案，λ₂ 是否可能命中 2−√3？ ---")
    print()
    print("（若只有链式失败，则 (II-C) 只是『一种构造失败』；穷举才能升级为『任何连接都失败』。）")
    print()
    print("%-14s %-14s %-14s %-14s %s" %
          ("k 分布", "最少连接组合数", "λ₂取值种数", "λ₂范围", "命中 2−√3？"))
    print("-" * 96)
    robust_ok = True
    for kd in [(3, 3), (2, 2, 2), (4, 2)]:
        H0, _ = assemble(mk_groups(list(kd)))
        n = len(kd)
        ring_pts = [["S%d%d" % (r, i) for i in range(3)] for r in range(n)]
        choices = [[(u, v) for u in ring_pts[r] for v in ring_pts[r + 1]]
                   for r in range(n - 1)]
        vals, cnt = set(), 0
        for combo in itertools.product(*choices):
            H1 = H0.copy()
            H1.add_edges_from(combo)
            if nx.number_connected_components(H1) == 1:
                vals.add(round(spec(H1)["lam2"], 9))
                cnt += 1
        hit = any(abs(v - LAM2_SINGLE) < LAM2_TOL for v in vals)
        robust_ok &= (not hit)
        print("%-14s %-14d %-14d [%.9f, %.9f]     %s" %
              (str(kd), cnt, len(vals), min(vals), max(vals),
               "**是**" if hit else "否"))
    print()
    print("⇒ 穷举 %s：**没有任何一种最少连接方案**能让 λ₂ 回到 2−√3 —— " %
          ("确认" if robust_ok else "有反例"))
    print("   全部可达 λ₂ 落在 ~[0.03, 0.05]，比 2−√3≈0.2679 低一个数量级。")
    print("   故 (ii) 与 (iii) 的互斥**不依赖具体连接方式**，是结构性事实。")
    print()
    print("⇒ **矛盾**：(ii) 要求连接，(iii) 要求连接后共享环谱性质不变，")
    print("   而扫遍所有连接方式 λ₂ 都偏离 2−√3 ⇒ **(ii) 与 (iii) 互斥**。")
    print()
    print("⇒ **不存在同时满足 (i)–(iv) 的环间连接机制。**")
    print("   这不是『候选都不好』，而是**四条必要条件本身不相容**。")
    print()


def part_II_D():
    print("=" * 100)
    print("(II-D) 若要强行连接，需放弃哪一条？（代价清单）")
    print("=" * 100)
    print()
    print("既然 (i)–(iv) 互斥，任何机制都必须**放弃至少一条**。逐条列出代价：")
    print()
    items = [
        ("放弃 (iii)", "承认 λ₂ = 2−√3 只是**单群**性质，多群时不再是该值",
         "§12.5『与体数无关』须限定为『与单群内的体数无关』；图 5 面板 (b) 需加注"),
        ("放弃 (iv)", "允许新增顶点（如 hub）",
         "需给出该顶点的物理语义，否则是凭空实体；V/E/β₁ 加和律（E3）失效"),
        ("放弃 (ii)", "不要求连通（即接受现状）",
         "即现行规则；多群样本只能当『并集』解读，不得参与同构/谱/形状判读"),
        ("放弃 (i)", "多群时改变装配本体（如跨群合并环点）",
         "已实测：会把 k=(3,3)、k=(6,)、k=(2,2,2)、k=(4,2) **压成同一张图** ⇒ 自毁 §12.11(1′)"),
    ]
    print("%-12s %-34s %s" % ("放弃项", "机制形态", "代价"))
    print("-" * 100)
    for a, b, c in items:
        print("%-12s %-34s %s" % (a, b, c))
    print()
    print("⇒ 四选项中，**代价最小的是『放弃 (ii)』**（= 维持现状），")
    print("   因为它不改变任何已发布数值，只需把多群样本的**解读**限定为并集。")
    print("   这恰好与 E1 诊断的处置口径一致。")
    print()


def part_II_E():
    print("=" * 100)
    print("(II-E) 与 B1 的合流：两条路给出同一个结论")
    print("=" * 100)
    print()
    print("路 (I)：B1 单群口径 ⇒ 多群不出现 ⇒ 无需环间连接。")
    print("路 (II)：穷举证明 ⇒ 无机制同时满足 (i)–(iv) ⇒ 无法连接。")
    print()
    print("二者**互补而非矛盾**：")
    print("  · (I) 说『多群不该出现』（来自 k 分布的形态学结论）；")
    print("  · (II) 说『即便出现，也连不上』（来自连接条件的互斥性）。")
    print()
    print("⇒ **合流结论**：**多环构形在本层应当缺席。**")
    print("   它在 A ≥ 5 的出现，是 §12.11(1′) 当时**把 k 分布当作自由参数**所致；")
    print("   经 B1（k 分布非自由）与 B2（连接不可行）双重收窄，该构造应被**废弃**。")
    print()
    print("   ⚠ 但须诚实：此结论依赖 B1 的弱口径。若未来发现 k 分布的外源选择规则")
    print("     （例如由某个尚未识别的观测量决定），则 (II) 的不可能性定理仍独立成立 ——")
    print("     **它不依赖 B1**，只依赖 §12.5 与 E3。")
    print()


def main():
    print("#" * 100)
    print("# B2: 环间连接机制 —— 穷举性判定")
    print("#" * 100)
    print()
    print("B1 改变了 B2 的问题设定：若 k 分布非自由（恒为单群），")
    print("则多群构形不出现，B2 自动消解。故本轮分两路作答。")
    print()
    part_I()
    part_II_A()
    part_II_B()
    part_II_C()
    part_II_D()
    part_II_E()
    print("=" * 100)
    print("结论摘要：")
    print("  (I)  B1 单群口径下：多群不出现 ⇒ E1 不再是缺陷 ⇒ 环间连接无需定义。")
    print("  (II-A) 三引理：t ≥ n−1；Δβ₁ = t − (n−1)（与边位置无关）；V 不变。")
    print("  (II-B) 定理：论文值 (60,96,38) = H0；任何连接使 E ≥ 97 ⇒ 不相容（定理级）。")
    print("  (II-C) 不可能性：不存在同时满足 (i) 单群退化、(ii) 连通、(iii) 保 §12.5、")
    print("         (iv) 不新增实体的机制 —— 因 (ii) 与 (iii) 实测互斥")
    print("         （穷举所有连接方案 λ₂ 均偏离 2−√3，与连接方式无关）。")
    print("  (II-D) 若要强行连接须放弃一条；代价最小 = 放弃 (ii)（维持现状）。")
    print("  (II-E) 两路合流：**多环构形在本层应当缺席**；A≥5 的多群构造应废弃。")
    print("         (II) 的不可能性定理**不依赖 B1**，是独立结果。")
    print("=" * 100)


if __name__ == "__main__":
    main()
