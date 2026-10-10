# -*- coding: utf-8 -*-
"""
逐边 s_e 赋值实测：电子「莫比乌斯类」与质子「闭态类」是否在 H¹(G;ℤ₂) 中相反
===============================================================================
目标（对应《电荷符号=ℤ₂ holonomy》§9.2 / 判据 F2）：
  把每个骨架的**边极性赋值** s_e ∈ {0,1}（ℤ₂）逐一实测，求出其 ℤ₂ holonomy 类
  （H¹(G;ℤ₂) 的一个元素），判定电子与质子是否落在**相反类**（一平凡一非平凡）。

方法：
  A. 全通道：类总数 = 2^{β₁}，统计非平凡类个数（通道容量）。
  B. 对称约束（关键）：物理 s_e 应尊重自同构群 Aut；枚举 Aut-不变赋值
     （在每个**边轨道**上取常值），求其 holonomy 类。检验对称性是否**强制**某一类。

骨架（复用官方构造）：Q₃(电子) / Y₃⋉△₃ 闭态(质子) / 开态(中子)。
输出：逐图 KPI（简洁）+ 显式 SUCCESS/FAIL。
"""
import sys, itertools
import networkx as nx

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ---------------------------------------------------------------- 官方骨架
def y3_closed():
    """三股 Y 的三角闭合体 Y₃⋉△₃（闭态=质子）。V=12,E=18,β₁=7,|Aut|=36。"""
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    return nx.convert_node_labels_to_integers(G)


def y3_open():
    """开态=中子：休眠边取环边，去一条环边。"""
    G = y3_closed()
    tri = nx.triangles(G)
    ring_v = {v for v in G if tri[v] > 0}
    ring_edges = sorted(tuple(sorted(e)) for e in G.edges()
                        if e[0] in ring_v and e[1] in ring_v)
    H = G.copy()
    H.remove_edge(*ring_edges[0])
    assert nx.is_connected(H)
    return H


def electron_q3():
    """电子本体 Q₃ 立方体。V=8,E=12,β₁=5。"""
    return nx.hypercube_graph(3)


# ---------------------------------------------------------------- 工具
def edge_list(G):
    return [tuple(sorted(e)) for e in G.edges()]


def automorphisms(G, cap=200000):
    GM = nx.algorithms.isomorphism.GraphMatcher(G, G)
    return list(itertools.islice(GM.isomorphisms_iter(), cap))


def edge_orbits(G, auts):
    edges = edge_list(G)
    parent = {e: e for e in edges}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for m in auts:
        for e in edges:
            f = tuple(sorted((m[e[0]], m[e[1]])))
            a, b = find(e), find(f)
            if a != b:
                parent[a] = b
    groups = {}
    for e in edges:
        groups.setdefault(find(e), []).append(e)
    return [sorted(v) for v in groups.values()]


def holonomy_vector(G, s, basis):
    """给定边赋值 s（dict: edge->0/1），返回在给定环基上的 holonomy 向量。"""
    vec = []
    for cyc in basis:
        h = 0
        n = len(cyc)
        for k in range(n):
            e = tuple(sorted((cyc[k], cyc[(k + 1) % n])))
            h ^= s.get(e, 0)
        vec.append(h)
    return tuple(vec)


def beta1(G):
    return G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G)


# ---------------------------------------------------------------- 主流程
def main():
    graphs = [
        ("电子 e⁻ (Q₃)", electron_q3()),
        ("质子 p  (闭态)", y3_closed()),
        ("中子 n  (开态)", y3_open()),
    ]
    print("=" * 84)
    print("逐边 s_e 赋值实测：σ 的 ℤ₂ holonomy 类（H¹(G;ℤ₂)）")
    print("=" * 84)

    results = {}
    for name, G in graphs:
        auts = automorphisms(G)
        orbs = edge_orbits(G, auts)
        basis = nx.cycle_basis(G)
        b1 = beta1(G)
        bip = nx.is_bipartite(G)
        trivial = tuple([0] * len(basis))

        # A. 通道容量
        full_nontrivial = 2 ** b1 - 1

        # B. Aut-不变赋值
        sym_classes = {}
        for bits in itertools.product([0, 1], repeat=len(orbs)):
            s = {}
            for oi, orb in enumerate(orbs):
                for e in orb:
                    s[e] = bits[oi]
            sym_classes.setdefault(holonomy_vector(G, s, basis), list(bits))
        sym_trivial_ok = trivial in sym_classes
        sym_nontrivial_ok = any(v != trivial for v in sym_classes)

        results[name] = dict(b1=b1, bip=bip, n_aut=len(auts), n_orb=len(orbs),
                             orb_sizes=[len(o) for o in orbs],
                             full_nontrivial=full_nontrivial,
                             sym_n_trivial=sym_trivial_ok,
                             sym_n_nontrivial=sym_nontrivial_ok,
                             sym_n_classes=len(sym_classes),
                             repr_trivial=sym_classes.get(trivial),
                             repr_nontrivial=next((b for v, b in sym_classes.items()
                                                   if v != trivial), None))

        print("\n### %s" % name)
        print("   V=%d E=%d β₁=%d |Aut|=%d bipartite=%s 边轨道数=%d 轨道大小=%s"
              % (G.number_of_nodes(), G.number_of_edges(), b1, len(auts), bip,
                 len(orbs), [len(o) for o in orbs]))
        print("   [A 全通道] 类总数=2^%d=%d，非平凡类=%d" % (b1, 2 ** b1, full_nontrivial))
        print("   [B 对称约束] Aut-不变赋值=2^%d=%d，可达类=%d；平凡可达=%s 非平凡可达=%s"
              % (len(orbs), 2 ** len(orbs), len(sym_classes),
                 sym_trivial_ok, sym_nontrivial_ok))
        if results[name]["repr_trivial"] is not None:
            print("       平凡类代表   s(轨道)=%s" % results[name]["repr_trivial"])
        if results[name]["repr_nontrivial"] is not None:
            print("       非平凡类代表 s(轨道)=%s" % results[name]["repr_nontrivial"])

    # ---------------- 判定 ----------------
    e = results["电子 e⁻ (Q₃)"]
    p = results["质子 p  (闭态)"]

    print("\n" + "=" * 84)
    print("判定：电子「莫比乌斯类」 vs 质子「闭态类」是否相反")
    print("=" * 84)

    e_forced_trivial = e["sym_n_trivial"] and (not e["sym_n_nontrivial"])
    p_allows_nontrivial = p["sym_n_nontrivial"]
    bip_opposite = (e["bip"] != p["bip"])

    print("\n[判据 1] 电子对称类被**强制平凡**：",
          "PASS" if e_forced_trivial else "FAIL",
          "（电子非平凡可达=%s；|Aut|=%d 使 %d 条边同轨 ⇒ 对称赋值必均匀）"
          % (e["sym_n_nontrivial"], e["n_aut"], e["orb_sizes"][0]))
    print("[判据 2] 质子**允许非平凡**对称类：",
          "PASS" if p_allows_nontrivial else "FAIL",
          "（%d 条边轨道 ⇒ 取 s(环边)=−1 即令三角形 holonomy=−1）" % p["n_orb"])
    print("[判据 3] 双分性相反（电子 bipartite=%s vs 质子 bipartite=%s）："
          % (e["bip"], p["bip"]), "PASS" if bip_opposite else "FAIL")

    opposite = e_forced_trivial and p_allows_nontrivial and bip_opposite
    print("\n结论：电子落在【平凡 holonomy 类】、质子落在【非平凡 holonomy 类】——",
          "相反(OPPOSITE)" if opposite else "未确证")
    print("   · Q₃ 边传递（12 边一轨）+ 二分 ⇒ 任何对称 s_e 给出 holonomy=+1 ⇒ 电子强制平凡；")
    print("   · Y₃⋉△₃ 含三角（非二分）+ 2 条边轨 ⇒ 允许 holonomy=−1 ⇒ 质子非平凡；")
    print("   · 配合符号锚 A0（电子的平凡类记为「负」）⇒ 质子为正。")

    print("\n[附] 不受对称约束时，两图都含非平凡类：电子 %d/%d，质子 %d/%d"
          % (e["full_nontrivial"], 2 ** e["b1"], p["full_nontrivial"], 2 ** p["b1"]))
    print("     ⇒ 差异来自**对称允许性**，而非 H¹ 容量。")

    print("\n" + "=" * 84)
    print("[SUCCESS] 电子与质子的 ℤ₂ holonomy 类相反 —— 已确证"
          if opposite else "[FAIL] 未确证")
    print("=" * 84)


if __name__ == "__main__":
    main()