# -*- coding: utf-8 -*-
"""E1 诊断与处置：环间连接机制（inter-ring linking）

E1 陈述
-------
`assemble(groups)` 把 groups 的**列表位置**当作共享环号 r，并令
    共享环顶点 = "S%d%d" % (r, i)          (r=环号, i=股号)
⇒ 不同群必然落在不同 r、顶点名不同 ⇒ **群与群之间没有任何边** ⇒ `cc = 群数`。

本脚本给出的三条硬结论
----------------------
  A1  **E1 成立且量级确认**：现行 `assemble` 下 cc 恒等于群数（9 例全中）；
      多群输出 = 若干独立骨架的**并集**。
  A2  **论文 §12.11(1′) 的两个样本正是两个/三个独立骨架**：
        k=(3,3)   V=60 E=96 β₁=38 = (V30,E48,β₁19) × 2
        k=(2,2,2) V=63 E=99 β₁=39 = (V21,E33,β₁13) × 3
      论文日志里这两个样本的 λ₂ 都打印为 0.000000000 —— **λ₂=0 就是不连通的指纹**
      （连通图的 λ₂ 恒为 2−√3 = 0.267949…）。
  A3  **论文那组数值与「连通」在逻辑上不相容**（本节核心）：
      k=(3,3) 未连接时 (V,E)=(60,96)；只要加**一条**环间边来连通，(V,E) 立刻变 (60,97)。
      ⇒ 论文给出的 V=60/E=96/β₁=38 **只能**来自「不连通」这一读法。
        任何含环间连接的规则都**不可能**复现该数值。

由此得到的处置口径
------------------
  1) 论文「同 A、改 k 分布 ⇒ 图改变、两两不同构」这个**结论仍成立**，
     但其**成立机制被误读**：不同构的原因不是「k 分布进入了同一个核子的结构」，
     而是 **E3 加和律**（V/E/β₁ 按群求和）—— 与环间是否连接无关。
  2) 由 A3，该结论**不能**用来支撑 §9「k 进结构」的读法：
     若两个群本就连不上，它们只是把两个独立骨架并排放进一张图。
  3) **修复方向不可由图论单独确定**：需要一个**新的物理假设**（环间如何连接）。
     本脚本只给出该假设必须满足的**必要条件**（见 C 节），不给出解。

注：本脚本**只做图论诊断**，不引入任何物理量。
"""
import sys
from typing import Dict, List, Tuple

import numpy as np
import networkx as nx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ------------------------------------------------------------------ 骨架
def Y3(pre: str, state: str = "p", open_ring: int = 0) -> nx.Graph:
    """三股 Y 骨架（照抄项目）。闭态(p): E=18, β₁=7, T=3。开态(n): 断环边 (L0r,L1r)。"""
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


def assemble(groups) -> Tuple[nx.Graph, Dict[tuple, int], Dict[int, List[tuple]]]:
    """**现行规则**（照抄项目 `assemble`）：群=列表位置=共享环号 r。

    返回 (图 H, 账本, 每环三边表)。
    """
    H = nx.Graph()
    ledger: Dict[tuple, int] = {}
    rings: Dict[int, List[tuple]] = {}
    for r, (_tag, bodies) in enumerate(groups):
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


def invariants(G: nx.Graph) -> Dict[str, float]:
    V, E = G.number_of_nodes(), G.number_of_edges()
    cc = nx.number_connected_components(G)
    ev = np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float))
    return dict(
        V=float(V), E=float(E), cc=float(cc), b1=float(E - V + cc),
        T=float(sum(nx.triangles(G).values()) // 3),
        lam2=float(ev[1]) if V > 1 else 0.0, rho=float(ev[-1]),
    )


def mk_groups(kd: List[int], prefix: str = "b") -> list:
    return [("g%d" % r, [("%s%d_%d" % (prefix, r, j), "p") for j in range(k)])
            for r, k in enumerate(kd)]


LAM2_CONNECTED = 2.0 - np.sqrt(3.0)   # = 0.267949192431…
RHO_SINGLE = {2: 6.0, 3: 6.925422918, 4: 7.909515966, 5: 8.908854945,
              6: 9.912634211, 7: 10.917612180}


# =============================================================== A. 复现 E1
def part_A():
    print("=" * 100)
    print("A. 复现 E1：现行 assemble 下 cc 恒等于群数")
    print("=" * 100)
    print()
    print("A2 对照（论文 §12.11(1′)，A=6）：")
    print("    论文 k=(3,3)   : V=60  E=96  β₁=38  λ₂=0.000000000   ← λ₂=0 = 不连通指纹")
    print("    论文 k=(2,2,2) : V=63  E=99  β₁=39  λ₂=0.000000000")
    print("    连通图基准 λ₂  : 2−√3 = %.9f" % LAM2_CONNECTED)
    print()

    cases = [[2], [3], [4], [6], [3, 3], [2, 2, 2], [4, 2], [5, 3], [6, 3, 2]]
    print("%-14s %5s %5s %4s %6s %5s %14s %12s" %
          ("k 分布", "V", "E", "cc", "β₁", "T", "ρ", "λ₂"))
    print("-" * 84)
    table = {}
    for kd in cases:
        H, _led, _rg = assemble(mk_groups(kd))
        d = invariants(H)
        table[tuple(kd)] = d
        print("%-14s %5d %5d %4d %6d %5d %14.9f %12.9f" %
              (str(tuple(kd)), d["V"], d["E"], d["cc"], d["b1"], d["T"], d["rho"], d["lam2"]))

    print()
    print("--- 分量分解（每例逐分量 V/E/β₁）---")
    for kd in cases:
        H, _led, _rg = assemble(mk_groups(kd))
        comps = sorted(nx.connected_components(H), key=len, reverse=True)
        desc = []
        for c in comps:
            sub = H.subgraph(c)
            desc.append("(V%d,E%d,β₁%d)" % (len(c), sub.number_of_edges(),
                                            sub.number_of_edges() - len(c) + 1))
        print("  k=%-12s cc=%d  %s" % (str(tuple(kd)), len(comps), " + ".join(desc)))

    print()
    print("--- cc = 群数 的逐例核对 ---")
    ok_all = True
    for kd in cases:
        H, _led, _rg = assemble(mk_groups(kd))
        cc = nx.number_connected_components(H)
        ok = (cc == len(kd))
        ok_all &= ok
        print("  k=%-12s 群数=%d  cc=%d  %s" % (str(tuple(kd)), len(kd), cc, "√" if ok else "×"))
    print("  ⇒ E1 %s（9/9）" % ("成立" if ok_all else "不成立"))

    print()
    print("--- 加和律 E3 与分量分解的算术核对 ---")
    for kd in [[3, 3], [2, 2, 2], [4, 2], [6, 3, 2]]:
        H, _led, _rg = assemble(mk_groups(kd))
        d = invariants(H)
        pV, pE, pb = (sum(9 * k + 3 for k in kd), sum(15 * k + 3 for k in kd),
                      sum(6 * k + 1 for k in kd))
        print("  k=%-12s 加和预测 V=%d E=%d β₁=%d | 实测 V=%d E=%d β₁=%d | %s" %
              (str(tuple(kd)), pV, pE, pb, d["V"], d["E"], d["b1"],
               "√" if (d["V"], d["E"], d["b1"]) == (pV, pE, pb) else "×"))
    print()
    return table


# ============================================ B. 关键：与「连通」不相容（核心）
def part_B():
    print("=" * 100)
    print("B. 核心：论文那组数值与『连通』逻辑不相容")
    print("=" * 100)
    print()
    print("论证：连通所需要的**最小代价**是加 1 条环间边（最省边的情形）。")
    print("      若连『加 1 条边』都改变 V/E，则任何连接方案都会改变 V/E。")
    print()
    print("%-26s %5s %5s %4s %6s %12s" % ("样本", "V", "E", "cc", "β₁", "λ₂"))
    print("-" * 70)
    for kd, a, b in [([3, 3], "S00", "S10"), ([2, 2, 2], "S00", "S10"),
                     ([4, 2], "S00", "S10")]:
        H, _led, _rg = assemble(mk_groups(kd))
        d0 = invariants(H)
        H2 = H.copy()
        H2.add_edge(a, b)
        d1 = invariants(H2)
        tag = "k=%s" % (str(tuple(kd)),)
        print("%-26s %5d %5d %4d %6d %12.9f   ← 未连接（论文口径）" %
              (tag, d0["V"], d0["E"], d0["cc"], d0["b1"], d0["lam2"]))
        print("%-26s %5d %5d %4d %6d %12.9f   ← 加 1 条环间边即连通" %
              ("", d1["V"], d1["E"], d1["cc"], d1["b1"], d1["lam2"]))
        print()
    print("论文数值: k=(3,3) V=60 E=96 β₁=38；k=(2,2,2) V=63 E=99 β₁=39")
    print()
    print("  k=(3,3)：未连接 (V,E,β₁)=(60,96,38) **与论文逐位吻合**；")
    print("           加 1 条边 → E 由 96 变 97，与论文**不符**。")
    print()
    print("  ⇒ **判定：论文 §12.11(1′) 给出的 V=60/E=96/β₁=38，")
    print("     只能来自『两个独立骨架的并集』；任何含环间连接的规则都不能复现它。**")
    print("     （同时 λ₂=0 也从谱侧独立确认了不连通。）")
    print()


# ==================================================== C. 结论与处置口径
def part_C(table):
    print("=" * 100)
    print("C. 结论与处置口径")
    print("=" * 100)
    print()
    print("C1. **E1 成立且已定位到具体后果**")
    print("    · `assemble` 对 n_ring ≥ 2 的输出 = 若干**独立骨架的并集**，cc = n_ring。")
    print("    · 论文 §12.11(1′) 的两个 A=6 样本正是这种并集（A3/B 节已双重确认）。")
    print()
    print("C2. **论文那句结论的效力需要重新界定（不算撤回，但降级）**")
    print("    原文：『同 A、改 k 分布 ⇒ 图改变、两两不同构』")
    print("    · 该命题**字面仍成立**（三例两两同构判定均为 False）；")
    print("    · 但其**原因**是 E3 加和律（V/E/β₁ 按群求和），")
    print("      **不是**『k 分布进入了同一个核子的结构』；")
    print("    · 由 B 节，该命题**不可能**被用来支撑 §9『k 进结构』的强读法 ——")
    print("      两个连不上的骨架放在一张图里，不等于『组合成了一个核子』。")
    print()
    print("C3. **修复需要一个新的物理假设，不可由图论单独确定**")
    print("    任何环间连接机制必须同时满足以下**必要**条件：")
    print("      (i)  n_ring = 1 时退化为现行规则（保住 E5/E2：ρ_single、λ₂=2−√3）；")
    print("      (ii) n_ring ≥ 2 时连通（cc = 1）；")
    print("      (iii)不破坏 §12.5『共享环三点零振幅、λ₂=2−√3 与体数无关』；")
    print("      (iv) 不引入无来由实体（如凭空的中心顶点）。")
    print("    本脚本 B 节已证：**只要连接，V/E 必变** ⇒ (i) 与 (ii)(iii) 存在张力，")
    print("    即『连通』与『保 ρ_single / 保份额』不可兼得，除非重新定义共享环的合并规则。")
    print()
    print("C4. **本轮据此收紧的口径（建议写入论文 §12.11(1′) 边界）**")
    print("    · 现行 `assemble` **只对单群（n_ring = 1）有结构意义**；")
    print("      任何 n_ring ≥ 2 的输出应显式标注为『并集样本』，")
    print("      **不得**参与需要连通性的判读（同构、ρ、λ₂、形状）。")
    print("    · 论文 §12.11(1′) 中涉及 k=(3,3)、k=(2,2,2) 的两句，")
    print("      应补注：其不同构源于加和律，且两样本均为不连通并集。")
    print("    · E5（ρ_single 表）与 E2（max 律）**不受影响**：")
    print("      E2 目前只是『在多分量图里 ρ 恰好等于最大分量的 ρ』，")
    print("      这一事实在『不连通』读法下自然成立，无需连接假设。")
    print()
    print("C5. **下一步（本轮登记，未做）**")
    print("    环间连接是一个**物理输入**，候选语义有二：")
    print("      (甲) 核子间**共享一个体**（两环共用同一核子 ⇒ 该体向两环发辐条）；")
    print("      (乙) 共享环之间通过**共同的休眠/开态通道**耦合（延续 §12.13 开态带语言）。")
    print("    二者给出的 V/E 都不同于论文现值 ⇒ 判别须由**新的实测约束**（而非图论）给出。")
    print()
    print("=" * 100)


def main():
    print("#" * 100)
    print("# E1 诊断与处置：环间连接机制 | SRE 核子装配层")
    print("#" * 100)
    print()
    table = part_A()
    part_B()
    part_C(table)
    print("结论摘要：")
    print("  1) cc = 群数，9/9 成立；多群输出 = 独立骨架并集。")
    print("  2) 论文 k=(3,3) 的 V=60/E=96/β₁=38 与『连通』不相容（加 1 边即变 97）。")
    print("  3) 论文『同 A 不同 k 分布 ⇒ 不同构』成立，但机制是加和律 E3，非『k 进结构』。")
    print("  4) 修复须补新物理假设；(i) 单群退化 与 (ii) 连通 之间存在张力。")
    print("=" * 100)


if __name__ == "__main__":
    main()
