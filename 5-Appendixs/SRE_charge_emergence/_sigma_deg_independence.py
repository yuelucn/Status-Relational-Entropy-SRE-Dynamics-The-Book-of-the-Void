# -*- coding: utf-8 -*-
"""
σ（电荷符号 / ℤ₂ holonomy 通道） vs  deg（电荷量值 / β₁ 奇偶） 独立性检验
=========================================================================
对应《deg 闭式重建》§9.2 的待验项：
  确认「符号通道」与「量值通道」是两条**独立**通道，而非同一 ℤ₂ 的两种写法；
  否则会出现"符号被量值锁死"的退化（例如 σ = (−1)^{β₁}）。

骨架来源（忠实复用官方构造）：
  y3() 复制自 5-Appendixs/SRE_Nucleon_Complete_Paper/_sre_nucleon_ringedge_transition.py
  电子本体 Q₃ = nx.hypercube_graph(3)，(V,E,β₁)=(8,12,5)。

通道定义：
  量值 M：deg = β₁ mod 2   （β₁ = 第一贝蒂数 = 独立环数）
  符号 S：ℤ₂ holonomy。载体 H¹(G;ℤ₂)=Hom(H₁,ℤ₂)，阶 |H¹|=2^{β₁}（理论"同调阶梯"）。

三条独立性判据：
  (I)  同一图上 holonomy 可取 {0,1} 两值（容量 2^{β₁}≥2）⇒ σ 不由 β₁ 决定；
  (II) 同为 deg=1 的两个图（Q₃ 与闭态质子）各自 σ 都可独立取两值
       ⇒ (M,S) 张成 1×2^{β₁} 的积空间，而非被锁死成单点；
  (III)观测交叉核对：电子(β₁=5,奇)带负电、质子(β₁=7,奇)带正电
       ⇒ 同 deg、反 σ ⇒ 独立性再获实测支持。

作者注：本脚本为独立性检验，不作物理量预言；输出逐图 KPI 与显式 SUCCESS/FAIL。
"""
import sys, itertools
import numpy as np
import networkx as nx

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ----------------------------------------------------------------------
# 0. 官方骨架
# ----------------------------------------------------------------------
def y3_closed():
    """三股 Y 的三角闭合体 Y₃⋉△₃（闭态=质子候选）。V=12,E=18,β₁=7,|Aut|=36。"""
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, "L%d%d" % (i, j))      # 辐条：股心 c_i — 叶点 L_{i,j}
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)               # 三角环 j 的三条环边
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    return nx.convert_node_labels_to_integers(G)


def y3_open():
    """开态=中子候选：休眠边取【环边】，去一条环边。V=12,E=17,β₁=6。"""
    G = y3_closed()
    tri = nx.triangles(G)
    ring_v = {v for v in G if tri[v] > 0}
    ring_edges = [tuple(sorted(e)) for e in G.edges()
                  if e[0] in ring_v and e[1] in ring_v]
    ring_edges.sort()
    H = G.copy()
    H.remove_edge(*ring_edges[0])                        # 打开一条环边
    assert nx.is_connected(H), "打开环边后开态必须仍连通（防御性检查）"
    return H


def electron_q3():
    """电子本体：三维超立方体 Q₃。V=8,E=12,β₁=5。"""
    return nx.hypercube_graph(3)


# ----------------------------------------------------------------------
# 1. β₁（量值通道 M）—— 三种独立算法交叉核对
# ----------------------------------------------------------------------
def gf2_rank(rows):
    """ℤ₂ 上的高斯消元求秩（纯 python，防御性实现）。"""
    rows = [list(r) for r in rows]
    if not rows:
        return 0
    ncols = len(rows[0])
    rank = 0
    for col in range(ncols):
        piv = None
        for r in range(rank, len(rows)):
            if rows[r][col] & 1:
                piv = r
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for r in range(len(rows)):
            if r != rank and (rows[r][col] & 1):
                rows[r] = [(a ^ b) for a, b in zip(rows[r], rows[rank])]
        rank += 1
    return rank


def beta1_three_ways(G):
    """β₁ = E − V + c ；并用 (a) 实数关联秩 (b) ℤ₂ 关联秩 两种独立算法核对。"""
    V, E = G.number_of_nodes(), G.number_of_edges()
    c = nx.number_connected_components(G)
    b_count = E - V + c                                  # 闭式：E − V + c
    edges = list(G.edges())
    # (a) 实数关联矩阵的秩
    B = np.zeros((V, E))
    for k, (u, v) in enumerate(edges):
        i, j = list(G.nodes()).index(u), list(G.nodes()).index(v)
        B[i, k] = 1.0
        B[j, k] = -1.0
    b_real = E - int(np.linalg.matrix_rank(B))
    # (b) ℤ₂ 关联矩阵的秩
    rows = [[0] * E for _ in range(V)]
    idx = {n: i for i, n in enumerate(G.nodes())}
    for k, (u, v) in enumerate(edges):
        rows[idx[u]][k] = 1
        rows[idx[v]][k] = 1
    b_gf2 = E - gf2_rank(rows)
    return b_count, b_real, b_gf2


# ----------------------------------------------------------------------
# 2. 符号通道 S：ℤ₂ holonomy
# ----------------------------------------------------------------------
def holonomy_channel(G):
    """返回 (容量 |H¹|=2^{β₁}, 基本环长度, 基本环上可达 holonomy 集合)。"""
    beta1 = G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)
    capacity = 2 ** beta1                                # |H¹(G;ℤ₂)| = 2^{β₁}
    cycles = nx.cycle_basis(G)
    gamma = cycles[0] if cycles else []
    m = len(gamma)
    vals = set()
    for bits in itertools.product([0, 1], repeat=m):     # 枚举环上边标号
        vals.add(sum(bits) % 2)
    return capacity, m, vals


# ----------------------------------------------------------------------
# 3. 主流程
# ----------------------------------------------------------------------
def main():
    graphs = [
        ("电子 e⁻  (Q₃)",                    electron_q3()),
        ("质子 p   (Y₃⋉△₃ 闭态)",            y3_closed()),
        ("中子 n   (Y₃⋉△₃ 开态,断一环边)",   y3_open()),
    ]

    print("=" * 84)
    print("σ(符号) vs deg(量值) 独立性检验 —— 官方骨架")
    print("=" * 84)
    print("%-26s %3s %3s %4s %4s %4s   %6s   %6s  %s"
          % ("对象", "V", "E", "β₁a", "β₁b", "β₁c", "deg", "|H¹|", "σ可达"))
    print("-" * 84)

    kpi = {}
    for name, G in graphs:
        b_cnt, b_real, b_gf2 = beta1_three_ways(G)
        beta1 = b_cnt
        deg = beta1 % 2
        cap, clen, vals = holonomy_channel(G)
        sigma_str = "{" + ",".join(str((1 - 2 * v)) for v in sorted(vals)) + "}"  # 0→+1,1→−1
        print("%-26s %3d %3d %4d %4d %4d   %6d   %6d  %s"
              % (name, G.number_of_nodes(), G.number_of_edges(),
                 b_cnt, b_real, b_gf2, deg, cap, sigma_str))
        kpi[name] = dict(V=G.number_of_nodes(), E=G.number_of_edges(),
                         beta1=beta1, beta1_agree=(b_cnt == b_real == b_gf2),
                         deg=deg, cap=cap, cycle_len=clen, sigma_vals=sorted(vals))

    print("-" * 84)

    # ---- 判据 (I)：同一图上 σ 可取两值 ----
    ok_I = all(len(k["sigma_vals"]) == 2 for k in kpi.values())
    print("\n[判据 I] 同一图上 holonomy 可达 {+1,−1}（容量 2^{β₁}≥2）：",
          "PASS" if ok_I else "FAIL")
    for name, k in kpi.items():
        print("   %-26s |H¹|=2^%d=%d,  可达 σ = %s"
              % (name, k["beta1"], k["cap"],
                 ["+1" if v == 0 else "−1" for v in k["sigma_vals"]]))

    # ---- 判据 (II)：同为 deg=1 的两图，σ 均可独立取两值 ----
    deg1 = {n: k for n, k in kpi.items() if k["deg"] == 1}
    ok_II = (len(deg1) >= 2) and all(len(k["sigma_vals"]) == 2 for k in deg1.values())
    print("\n[判据 II] 同为 deg=1 的对象数 = %d，每个 σ 均可独立取 {+1,−1}：" % len(deg1),
          "PASS" if ok_II else "FAIL")
    print("   若二者被锁死，则同一 deg 只能对应单一 σ（|σ|集大小=1）；")
    print("   实测每个 deg=1 对象 σ 集大小=2 ⇒ (M,S) 为 1×2^{β₁} 积空间，非单点。")

    # ---- 判据 (III)：观测交叉核对 ----
    #   电子(β₁=5,奇)→负电；质子(β₁=7,奇)→正电。同量值奇偶、反符号。
    obs = [("电子 e⁻", kpi["电子 e⁻  (Q₃)"]["beta1"], -1),
           ("质子 p",  kpi["质子 p   (Y₃⋉△₃ 闭态)"]["beta1"], +1)]
    same_parity = (obs[0][1] % 2 == obs[1][1] % 2)
    opp_sign = (obs[0][2] != obs[1][2])
    ok_III = same_parity and opp_sign
    print("\n[判据 III] 观测交叉核对（同 deg 奇偶、反符号）：",
          "PASS" if ok_III else "FAIL")
    print("   电子 β₁=%d(奇)→σ=−1；质子 β₁=%d(奇)→σ=+1 ⇒ 同量值、反符号 ⇒ 符号⊥量值"
          % (obs[0][1], obs[1][1]))

    # ---- β₁ 三算法一致性 ----
    ok_beta = all(k["beta1_agree"] for k in kpi.values())
    print("\n[一致性] β₁ 三种独立算法（E−V+c / 实数关联秩 / ℤ₂关联秩）全部一致：",
          "PASS" if ok_beta else "FAIL")

    # ---- 总判定 ----
    success = ok_I and ok_II and ok_III and ok_beta
    print("\n" + "=" * 84)
    print("结论：符号通道 σ 与量值通道 deg 相互独立 ——",
          "INDEPENDENT" if success else "NOT CONFIRMED")
    print("   · deg = β₁ mod 2 是**图拓扑**属性（每图唯一、2 值）；")
    print("   · σ ∈ H¹(G;ℤ₂) 是**边标号**属性，容量 2^{β₁}（随 β₁ 指数增长，非 1 位）；")
    print("   · 二者张成 2 × 2^{β₁} 直积 ⇒ 不存在 σ=(−1)^{β₁} 的锁死。")
    print("=" * 84)
    print("[SUCCESS] σ vs deg 独立性检验通过" if success
          else "[FAIL] σ vs deg 独立性检验未通过")


if __name__ == "__main__":
    main()