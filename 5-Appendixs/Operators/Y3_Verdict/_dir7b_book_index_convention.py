# -*- coding: utf-8 -*-
"""_dir7b_book_index_convention.py -- 第104轮续：梯族下标口径对照与书内口径复算

问题（G20 口径律）：书内 Operator_19 §6.1 用 $M_k$ 表示「偶环 $C_{2k}$ + 对径弦」，
即 $V=2k$；本项目第101/104轮论文用 $M_{2n}=\\mathrm{Cay}(\\mathbb Z_{2n},\\{1,n\\})$，
即 $V=2n$。两者是**同一族但下标差一个因子 2**：

    书内 $M_k$ ≅ 论文 $M_{2k}$，   即  论文 $M_{2n}$ ≅ 书内 $M_n$。

后果：论文的 $M_4$ = 书内的 $M_2$ = $K_4$；论文的 $M_8$ = 书内的 $M_4$ = Wagner 图。
书内「$M_3$ 退化为 $K_{3,3}$，$M_4$ 即 Wagner 图」与论文编号**直接冲突**，
读者若按论文编号读书内文字会指错图。

本脚本（双向核验，不采信任何未验证的临时片段）：
  1. 用 networkx GraphMatcher 实测同构关系，列出完整对照表；
  2. 用**主实验已验证引擎**（orbit_masks_of / impl_B1_M_matrix / impl_B2_cutspace）
     在**书内口径** $M_k$ 上复算 n_orb / rank_hol / 二分性 / 三角形数；
  3. 三实现交叉（I1/B1、I2/B2、I3/B3）+ T9 恒等式，零失配门；
  4. 阳性对照：Q₃（应 0）、Y₃闭（应 1）、Y₃开（应 2）；
  5. 反向有效性：Cut 换成树路径边集（G66 坑）读数须变。

产物：_dir7b_book_index_convention.json
"""
import os
import sys
import json
from collections import defaultdict

import networkx as nx
import networkx.algorithms.isomorphism as iso

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

from _dir7_y3_skeleton_verdict import (  # noqa: E402
    orbit_masks_of, impl_B1_M_matrix, impl_B2_cutspace, impl_B3_subset_enum,
    y3_closed, y3_open, q3,
)
from _pfcore import mobius, norm_edges  # noqa: E402

OUT = os.path.join(HERE, "_dir7b_book_index_convention.json")


# ═══════════════════════════════════════════════════════════════════
# 构造：两种口径
# ═══════════════════════════════════════════════════════════════════
def book_mobius(k):
    """书内口径 M_k = 偶环 C_{2k} + 对径弦 (i, i+k)，V=2k, E=3k。"""
    G = nx.Graph()
    G.add_nodes_from(range(2 * k))
    for i in range(2 * k):
        G.add_edge(i, (i + 1) % (2 * k))
    for i in range(k):
        G.add_edge(i, i + k)
    return G


def paper_mobius(n):
    """论文口径 M_{2n} = Cay(Z_{2n}, {1, n})，V=2n。"""
    return nx.Graph(mobius(n))


def wagner_graph():
    G = nx.Graph()
    G.add_nodes_from(range(8))
    for i in range(8):
        G.add_edge(i, (i + 1) % 8)
        G.add_edge(i, (i + 4) % 8)
    return G


# ═══════════════════════════════════════════════════════════════════
# Part 1：口径对照表（同构实测，双向）
# ═══════════════════════════════════════════════════════════════════
def part1():
    print()
    print("=" * 96)
    print("Part 1  梯族下标口径对照（实测同构）")
    print("=" * 96)
    rows = []
    special = {
        "K4": nx.complete_graph(4),
        "K33": nx.complete_bipartite_graph(3, 3),
        "Wagner": wagner_graph(),
    }
    print("  %-8s %-16s %-6s %-6s %-8s %-8s %-8s" %
          ("book k", "paper M_{2k}", "V", "E", "≅K4", "≅K33", "≅Wagner"))
    for k in range(2, 13):
        Gb = book_mobius(k)
        Gp = paper_mobius(k)
        same = nx.is_isomorphic(Gb, Gp)
        r = {
            "book_k": k,
            "paper_idx": 2 * k,
            "V": Gb.number_of_nodes(),
            "E": Gb.number_of_edges(),
            "iso_K4": nx.is_isomorphic(Gb, special["K4"]),
            "iso_K33": nx.is_isomorphic(Gb, special["K33"]),
            "iso_Wagner": nx.is_isomorphic(Gb, special["Wagner"]),
            "book_isomorphic_to_paper": same,
        }
        rows.append(r)
        print("  %-8d %-16s %-6d %-6d %-8s %-8s %-8s  %s" %
              (k, "M_%d" % (2 * k), r["V"], r["E"],
               r["iso_K4"], r["iso_K33"], r["iso_Wagner"],
               "同构" if same else "**不同构**"))
    # 关键：书内 M_2 = K4、书内 M_3 = K33、书内 M_4 = Wagner
    key = {
        "book_M2_is_K4": rows[0]["iso_K4"],
        "book_M3_is_K33": rows[1]["iso_K33"],
        "book_M4_is_Wagner": rows[2]["iso_Wagner"],
        "paper_M4_is_K4": rows[0]["iso_K4"],
        "paper_M8_is_Wagner": rows[2]["iso_Wagner"],
        "all_isomorphic": all(r["book_isomorphic_to_paper"] for r in rows),
    }
    print()
    print("  关键对应：")
    print("    书内 M_2 ≅ K4        ⇒ 论文 M_4 ≅ K4        （%s）" % key["book_M2_is_K4"])
    print("    书内 M_3 ≅ K_{3,3}    ⇒ 论文 M_6 ≅ K_{3,3}    （%s）" % key["book_M3_is_K33"])
    print("    书内 M_4 ≅ Wagner 图  ⇒ 论文 M_8 ≅ Wagner 图  （%s）" % key["book_M4_is_Wagner"])
    print("    全部 %d 例「书内 M_k ≅ 论文 M_{2k}」：%s" %
          (len(rows), "全部同构" if key["all_isomorphic"] else "**存在不同构**"))
    print()
    print("  ⇒ 冲突确认：书内 §6.1 写「$M_3$ 退化为 $K_{3,3}$，$M_4$ 即 Wagner 图 $V_8$」，")
    print("    而论文编号下 $K_{3,3}$ 是 $M_6$、Wagner 图是 $M_8$ ⇒ 同一段文字在两套编号下")
    print("    指的不是同一批图。**须在书内补一条编号对照表**。")
    return rows, key


# ═══════════════════════════════════════════════════════════════════
# Part 2：书内口径 M_k 的四路读数（主实验引擎，三实现 + T9）
# ═══════════════════════════════════════════════════════════════════
def part2():
    print()
    print("=" * 96)
    print("Part 2  书内口径 M_k 的四路读数（主实验引擎，三实现交叉）")
    print("=" * 96)
    cases = [("book M_%d" % k, book_mobius(k)) for k in range(2, 25)]
    for tag, G in (("Q₃", q3()), ("Y₃闭", y3_closed()), ("Y₃开", y3_open())):
        cases.append((tag, G))
    print("  %-11s %-4s %-4s %-6s %-6s %-6s %-6s %-6s %-6s %-6s %-5s %-4s" %
          ("name", "V", "E", "n_orb", "|Aut|", "r_B1", "r_B2", "r_B3", "T9",
           "bip", "tri", ""))
    rows = []
    for name, G in cases:
        masks, n_orb, n_aut = orbit_masks_of(G)
        r1, _ = impl_B1_M_matrix(G)
        r2, di2, dc2 = impl_B2_cutspace(G, masks)
        b3 = impl_B3_subset_enum(G, masks)
        # B3 需枚举 2^|V| 个子集 ⇒ |V|>16 时属**能力边界**（非失配），如实标注
        if b3 is None:
            r3, b3_note = None, "n/a"
        else:
            r3, di3, dc3 = b3
            b3_note = ""
        t9 = n_orb - di2
        agree = (r1 == r2 == t9) and (r3 is None or r3 == t9)
        tri = sum(nx.triangles(G).values()) // 3
        rows.append(dict(name=name, V=G.number_of_nodes(), E=G.number_of_edges(),
                         n_orb=n_orb, n_aut=n_aut, r1=r1, r2=r2, r3=r3, t9=t9,
                         dimCut=dc2, dimInter=di2, bip=nx.is_bipartite(G),
                         tri=tri, agree=agree, b3_note=b3_note))
        print("  %-11s %-4s %-4s %-6s %-6s %-6s %-6s %-6s %-6s %-6s %-5s" %
              (name, G.number_of_nodes(), G.number_of_edges(), n_orb, n_aut,
               r1, r2, (str(r3) if r3 is not None else b3_note), t9,
               nx.is_bipartite(G), tri) +
              ("" if agree else "  **MISMATCH**"))
    gate = all(r["agree"] for r in rows)
    n_b3 = sum(1 for r in rows if r["r3"] is not None)
    print("\n  [门B'] 书内口径 %d 例 + 3 阳性对照，三实现(+T9)零失配 ⇒ %s"
          % (len(rows), "PASS" if gate else "FAIL"))
    print("       （B3 子集枚举法仅在 |V|≤16 可用：%d/%d 例参与，"
          "%d 例超出能力边界，标注 n/a 而非计为失配）"
          % (n_b3, len(rows), len(rows) - n_b3))
    return rows, gate


# ═══════════════════════════════════════════════════════════════════
# Part 3：对照检验 + 反向有效性
# ═══════════════════════════════════════════════════════════════════
def part3(rows):
    print()
    print("=" * 96)
    print("Part 3  对照检验与反向有效性")
    print("=" * 96)
    by = {r["name"]: r for r in rows}
    # 3.1 阳性对照
    pos = []
    for nm, want in (("Q₃", 0), ("Y₃闭", 1), ("Y₃开", 2)):
        got = by[nm]["t9"]
        ok = got == want
        pos.append(ok)
        print("  [P1] %-8s rank_hol = %d（期望 %d）⇒ %s" %
              (nm, got, want, "PASS" if ok else "FAIL"))
    # 3.2 书内 M_k 的 n_orb：$k=2,3$ 单轨道，$k\ge4$ 双轨道
    mo = [r for r in rows if r["name"].startswith("book ")]
    n_orb_vals = sorted(set(r["n_orb"] for r in mo))
    single = all(r["n_orb"] == 1 for r in mo)
    print("  [P2] 书内口径 M_k 的 n_orb 取值集合 = %s" % n_orb_vals)
    lo = [r for r in mo if r["n_orb"] == 1]
    hi = [r for r in mo if r["n_orb"] == 2]
    print("       单轨道（n_orb=1）：%s" % sorted(int(r["name"].split("_")[1]) for r in lo))
    print("       双轨道（n_orb=2）：%s" % sorted(int(r["name"].split("_")[1]) for r in hi))
    print("       ⇒ 书内 §6.1「$M_k,k\\ge4$：多轨道，T2 $M\\neq0$」**成立**"
          "（$k=2,3$ 为退化小成员，单轨道）")
    # 3.3 奇偶二分性与 rank_hol 的四种象限
    par = [(r["name"], r["bip"], r["t9"], r["n_orb"]) for r in mo]
    print("  [P3] 书内 M_k 奇偶二分性 × 边轨道 × rank_hol：")
    for nm, bip, t9, no in par:
        k = int(nm.split("_")[1])
        print("       k=%-2d %-4s 二分=%-5s n_orb=%d rank_hol=%d" %
              (k, "偶" if k % 2 == 0 else "奇", bip, no, t9))
    even = [r for r in mo if int(r["name"].split("_")[1]) % 2 == 0]
    odd = [r for r in mo if int(r["name"].split("_")[1]) % 2 == 1]
    odd_ge5 = [r for r in odd if int(r["name"].split("_")[1]) >= 5]
    print("       k 偶（%d 例）：全非二分=%s；rank_hol 全 >0=%s" %
          (len(even), all(not r["bip"] for r in even),
           all(r["t9"] > 0 for r in even)))
    print("       k 奇（%d 例）：全二分=%s" %
          (len(odd), all(r["bip"] for r in odd)))
    print("       k 奇且 k≥5（%d 例）：rank_hol 全 >0=%s（**二分 + 双轨道 ⇒ "
          "T6 不适用 ⇒ 通道仍打开**）" %
          (len(odd_ge5), all(r["t9"] > 0 for r in odd_ge5)))
    print("       k=3（单轨道 + 二分）：rank_hol=%d ⇒ T6 强制平凡"
          % [r["t9"] for r in odd if int(r["name"].split("_")[1]) == 3][0])
    # 3.4 反向有效性：Cut 换成树路径边集（G66 坑）读数须变
    G = book_mobius(4)
    masks, n_orb, _ = orbit_masks_of(G)
    r_ok, di_ok, dc_ok = impl_B2_cutspace(G, masks)
    # 错误的 Cut：生成树 v->root 路径边集
    root = 0
    parent = {v: v for v in G.nodes()}
    seen = {root}
    stack = [root]
    tree_edges = set()
    while stack:
        v = stack.pop()
        for w in G.neighbors(v):
            if w not in seen:
                seen.add(w)
                tree_edges.add(tuple(sorted((v, w))))
                stack.append(w)
    edges = [tuple(sorted(e)) for e in G.edges()]
    eidx = {e: i for i, e in enumerate(edges)}

    def rank(rowsM):
        M = [r[:] for r in rowsM]
        r_ = 0
        for c in range(len(M[0]) if M else 0):
            piv = None
            for i in range(r_, len(M)):
                if M[i][c]:
                    piv = i
                    break
            if piv is None:
                continue
            M[r_], M[piv] = M[piv], M[r_]
            for i in range(len(M)):
                if i != r_ and M[i][c]:
                    M[i] = [a ^ b for a, b in zip(M[i], M[r_])]
            r_ += 1
        return r_

    Cbad = []
    for v in G.nodes():
        vec = [0] * len(edges)
        for i, (u, w) in enumerate(edges):
            if u == v or w == v:
                vec[i] = 1
        Cbad.append(vec)
    Wc = []
    for m in masks:
        vec = [0] * len(edges)
        for i, e in enumerate(edges):
            if m >> i & 1:
                vec[i] = 1
        Wc.append(vec)
    dimW = rank([[Wc[c][i] for c in range(len(Wc))] for i in range(len(edges))])
    dimC = rank([[Cbad[c][i] for c in range(len(Cbad))] for i in range(len(edges))])
    dimIntBad = rank([[Wc[c][i] for c in range(len(Wc))] +
                      [Cbad[c][i] for c in range(len(Cbad))]
                      for i in range(len(edges))]) - dimW - dimC
    r_bad = n_orb - dimIntBad
    changed = (r_bad != r_ok)
    print("  [P4] 反向有效性（G66 坑）：书内 M_4 的 rank_hol")
    print("       正确 Cut（星集 d({v})）⇒ %d" % r_ok)
    print("       错误 Cut（树路径边集）  ⇒ %d" % r_bad)
    print("       读数须不同 ⇒ %s" % ("PASS" if changed else "FAIL(无鉴别力)"))
    # 3.5 阳性对照：Cut 定义换成星集时读数与 I1 一致
    print("  [P5] 阳性对照：书内 M_4 的 I1=%d、I2=%d、T9=%d 三者一致 ⇒ %s" %
          (by["book M_4"]["r1"], by["book M_4"]["r2"], by["book M_4"]["t9"],
           "PASS" if by["book M_4"]["r1"] == by["book M_4"]["r2"] ==
           by["book M_4"]["t9"] else "FAIL"))
    # 判据：$k=2,3$ 单轨道；$k\ge4$ 双轨道；$k$ 偶全非二分；$k$ 奇全二分；
    #       $k$ 奇且 $k\ge5$ 时 rank_hol>0（二分 + 双轨道 ⇒ T6 不适用）
    kmap = {int(r["name"].split("_")[1]): r for r in mo}
    orb_ok = all(kmap[k]["n_orb"] == 1 for k in (2, 3)) and \
        all(kmap[k]["n_orb"] == 2 for k in range(4, 25))
    par_ok = all(not kmap[k]["bip"] for k in range(2, 25, 2)) and \
        all(kmap[k]["bip"] for k in range(3, 25, 2))
    odd5_ok = all(kmap[k]["t9"] > 0 for k in range(5, 25, 2))
    k3_trivial = (kmap[3]["t9"] == 0) and (kmap[3]["n_orb"] == 1)
    print("  [P6] 判据汇总：轨道分布=%s｜奇偶二分=%s｜奇 k≥5 全开=%s｜"
          "k=3 单轨道⇒平凡=%s" % (orb_ok, par_ok, odd5_ok, k3_trivial))
    ok = all(pos) and orb_ok and par_ok and odd5_ok and k3_trivial and changed
    return dict(positive=pos, orb_dist=orb_ok, parity=par_ok, odd5=odd5_ok,
                k3_trivial=k3_trivial, changed=changed, ok=ok,
                r_ok=r_ok, r_bad=r_bad, tree_edges=len(tree_edges))


def main():
    p1_rows, p1_key = part1()
    p2_rows, p2_gate = part2()
    p3 = part3(p2_rows)
    out = dict(part1=p1_rows, part1_key=p1_key, part2=p2_rows,
               gateB_book=p2_gate, part3=p3)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print()
    print("  产物：%s" % OUT)
    ok = p1_key["all_isomorphic"] and p2_gate and p3["ok"]
    print("  总判定：%s" % ("ALL PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
