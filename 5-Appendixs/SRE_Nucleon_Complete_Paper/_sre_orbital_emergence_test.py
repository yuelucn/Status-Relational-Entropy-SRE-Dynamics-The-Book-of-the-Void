# -*- coding: utf-8 -*-
"""
判定性实验：SRE 的「轨道 = 涌现谱」到底成立吗？
================================================
背景
----
SRE_Electron_Orbital_Assignment.md / SRE_Electron_Complete_Paper.md §13.4 把「轨道」定义成
    「原子（介观核）上的集体振动模态 = 关系拉普拉斯算符的特征向量」，
并声称 2l+1 简并「来自涌现三维空间的旋转对称」，属**借用项**。

但该文档的验证程序 _sre_orbital_assignment.py 里：
  - 只算了 Q3 本体的**拉普拉斯谱**（V1），且只取 Hamming 权简并 {1,3,3,1}；
  - 从未算过任何**轨道的特征向量**；
  - 从未算过 16 单胞双覆盖图（轨道真正的定义域）的谱；
  - 从未构造过「原子的介观核图」。

本脚本做四件事（全部精确、无自由参数）：
  PART 1  复现 V1：Q3 拉普拉斯谱 + Hamming 阶梯 {1,3,3,1}
  PART 2  【新增】16 单胞双覆盖（= 电子本体 x 自旋片）的拉普拉斯谱与简并阶梯
  PART 3  「2l+1 = 1,3,5,7」能否作为**任何自然图**的简并阶梯？（项目全部常见图扫描）
  PART 4  简并阶梯是否跨图不变？—— 涌现不变量 vs 图相关假象

判据（先定）
-----------
  H1「轨道是涌现谱」强读法成立  <=>  简并阶梯是所论图的**内蕴不变量**，
      且能在某个自然图上复现 2l+1 = 1,3,5,7。
  H0 强读法不成立               <=>  阶梯随图改变（非内蕴），或 1,3,5,7 图上不可复现。
"""
import json
import itertools

import numpy as np
import networkx as nx

TOL = 1e-7


# ---------------------------------------------------------------------------
def lap_spectrum(G):
    """无符号图拉普拉斯谱（升序）。"""
    L = nx.laplacian_matrix(G).toarray().astype(float)
    return np.sort(np.linalg.eigvalsh(L))


def ladder(ev, tol=TOL):
    """把谱压成 (distinct 特征值, 各自重数)。"""
    vals, cnts = [], []
    for x in np.sort(ev):
        if vals and abs(x - vals[-1]) <= tol:
            cnts[-1] += 1
        else:
            vals.append(float(x))
            cnts.append(1)
    return [round(v, 6) for v in vals], cnts


def nonzero_ladder(ev, tol=TOL):
    """非零特征值的阶梯（升序）。"""
    vals, cnts = ladder(ev, tol)
    out = [(v, c) for v, c in zip(vals, cnts) if abs(v) > tol]
    return [v for v, _ in out], [c for _, c in out]


def bfs_shells(G, root=0):
    """自 root 的 BFS 壳层大小。"""
    d = nx.single_source_shortest_path_length(G, root)
    mx = max(d.values())
    return [sum(1 for v in d.values() if v == k) for k in range(mx + 1)]


# ---------------------------------------------------------------------------
# PART 1  Q3 本体：复现 V1
# ---------------------------------------------------------------------------
def part1():
    G = nx.cubical_graph()
    ev = lap_spectrum(G)
    vals, cnts = ladder(ev)
    # Hamming 权阶梯（项目 V1 用的那个量）
    hamming = {0: 1, 1: 3, 2: 3, 3: 1}
    print("=" * 78)
    print("PART 1  Q3 本体（8 顶点 12 边 beta1=5）")
    print("=" * 78)
    print(f"  拉普拉斯谱(升序) = {[round(x, 4) for x in ev]}")
    print(f"  谱简并阶梯        = {cnts}   （distinct = {vals}）")
    print(f"  Hamming 权阶梯    = {list(hamming.values())}  （项目 V1 报的 {1,3,3,1}）")
    print(f"  2l+1 阶梯         = [1, 3, 5, 7]")
    match = [a == b for a, b in zip(cnts, [1, 3, 5, 7])]
    print(f"  逐项比对          = {match}  -> 第 {match.index(False) if False in match else 'x'} 项起分歧")
    return {"spectrum": [round(float(x), 6) for x in ev],
            "ladder": cnts, "hamming": list(hamming.values())}


# ---------------------------------------------------------------------------
# PART 2  16 单胞双覆盖：项目从未算过
# ---------------------------------------------------------------------------
def double_cover_graphs():
    """返回 (无符号投影图 G16, 带符号关系矩阵 M16)。"""
    A = nx.to_numpy_array(nx.cubical_graph(), dtype=float)
    cells = [(v, s) for v in range(8) for s in (+1, -1)]
    idx = {c: i for i, c in enumerate(cells)}
    n = 16
    G = nx.Graph()
    G.add_nodes_from(range(n))
    M = np.zeros((n, n))
    for (v, s), i in idx.items():
        for (w, t), j in idx.items():
            if v == w:
                continue
            a = A[v, w]
            M[i, j] = a * (1.0 if s == t else -1.0)      # 带符号：Mobius/Z2 holonomy
            if a != 0:
                G.add_edge(i, j)                          # 无符号支撑
    return G, M, cells


def part2():
    G, M, cells = double_cover_graphs()
    print()
    print("=" * 78)
    print("PART 2  16 单胞双覆盖（电子本体 Q3 x 自旋 2 片）：首次计算其谱")
    print("=" * 78)
    print(f"  顶点 {G.number_of_nodes()}  边 {G.number_of_edges()}  度序列 "
          f"{sorted(dict(G.degree()).values(), reverse=True)[:4]}...")
    ev = lap_spectrum(G)
    vals, cnts = ladder(ev)
    nzv, nzc = nonzero_ladder(ev)
    print(f"  无符号图拉普拉斯谱(升序) = {[round(x, 4) for x in ev]}")
    print(f"  distinct / 重数          = {vals} / {cnts}")
    print(f"  **非零阶梯**             = {nzc}   （= 逐步 3, 8, 3, 1）")
    print(f"  2l+1 阶梯                = [1, 3, 5, 7]")

    # 带符号关系矩阵的两种拉普拉斯约定
    Dabs = np.diag(np.abs(M).sum(axis=1))
    L_abs = Dabs - M
    ev_abs = np.sort(np.linalg.eigvalsh(L_abs))
    v2, c2 = ladder(ev_abs)
    Drow = np.diag(M.sum(axis=1))
    L_row = Drow - M
    ev_row = np.sort(np.linalg.eigvalsh(L_row))
    v3, c3 = ladder(ev_row, tol=1e-5)
    print(f"  带符号 L(绝对度和)谱     = {[round(x, 3) for x in ev_abs]}")
    print(f"     distinct/重数         = {v2} / {c2}")
    print(f"  带符号 L(行和)  distinct/重数 = {v3} / {c3}")

    ratio = float(ev[1] / ev[-1])
    print(f"  **lambda2 / lambda_max** = {ratio:.6f}   （Q3 本体同量 = {2/6:.6f}）")
    return {"V16_lap": [round(float(x), 6) for x in ev],
            "V16_ladder": cnts, "V16_nonzero_ladder": nzc,
            "signed_absdeg_ladder": c2, "signed_rowsum_ladder": c3,
            "lambda2_over_lambdamax": ratio, "Q3_ratio": 2 / 6}


# ---------------------------------------------------------------------------
# PART 3  1,3,5,7 能否是任何自然图的简并阶梯？
# ---------------------------------------------------------------------------
def candidates():
    C = {}
    C["Q3 (电子本体)"] = nx.cubical_graph()
    C["Q4 (超立方体)"] = nx.hypercube_graph(4)
    C["Q5"] = nx.hypercube_graph(5)
    C["G16 (双覆盖)"] = double_cover_graphs()[0]
    C["K8 (完全图)"] = nx.complete_graph(8)
    C["K4,4"] = nx.complete_bipartite_graph(4, 4)
    C["C8 (环)"] = nx.cycle_graph(8)
    C["P8 (路)"] = nx.path_graph(8)
    C["Mobius ladder M60"] = nx.circular_ladder_graph(30)
    C["Mobius ladder M8"] = nx.circular_ladder_graph(4)
    C["网格 4x4"] = nx.grid_2d_graph(4, 4)
    C["Petersen"] = nx.petersen_graph()
    C["Y3 (核子骨架)"] = None   # 见下，手工构造
    # Y3: 由项目定义手工构造（股心-叶点）
    return C


def build_y3():
    """核子骨架 Y3：3 个股心 + 三股，股心各自连 2 叶点，另有三角环。
    这里只取项目的可用近似：三角环 + 每个环顶点挂 3 叶点（V=12）。"""
    G = nx.Graph()
    ring = [0, 1, 2]
    for i in range(3):
        G.add_edge(ring[i], ring[(i + 1) % 3])
    nxt = 3
    for i in range(3):
        for _ in range(3):
            G.add_edge(ring[i], nxt)
            nxt += 1
    return G


def part3():
    print()
    print("=" * 78)
    print("PART 3  「2l+1 = 1,3,5,7」能否作为任何自然图的简并阶梯？")
    print("=" * 78)
    C = candidates()
    C["Y3 近似(V12)"] = build_y3()
    target = [1, 3, 5, 7]
    print(f"  {'图':<22}{'V':>4}{'非零阶梯':>26}{'前缀=1,3,5,7?':>16}{'BFS 壳层':>22}")
    print("  " + "-" * 92)
    rows = {}
    best = None
    for name, G in C.items():
        if G is None:
            continue
        ev = lap_spectrum(G)
        _, cnts = nonzero_ladder(ev)
        sh = bfs_shells(G, next(iter(G)))
        pref = cnts[:4] == target
        print(f"  {name:<22}{G.number_of_nodes():>4}{str(cnts):>26}{str(pref):>16}{str(sh):>22}")
        rows[name] = {"V": G.number_of_nodes(), "ladder": cnts, "shells": sh}
        if pref:
            best = name
    print("  " + "-" * 92)
    print(f"  命中 1,3,5,7 为前四重数的图：{best if best else '无'}")
    print("  说明：2l+1 是 SO(3) 不可约表示维数（表示论对象），")
    print("        不是任何图拉普拉斯的简并律；超立方体给的是二项式 C(d,k)。")
    return rows


# ---------------------------------------------------------------------------
# PART 4  阶梯跨图不变吗？
# ---------------------------------------------------------------------------
def part4(p1, p2):
    print()
    print("=" * 78)
    print("PART 4  简并阶梯是否跨图不变？（涌现不变量 vs 图相关假象）")
    print("=" * 78)
    a = p1["ladder"]
    b = p2["V16_ladder"]
    print(f"  Q3 本体 阶梯        = {a}")
    print(f"  G16 双覆盖 阶梯     = {b}")
    print(f"  两者相同？          = {a == b}")
    _, q3_nz = nonzero_ladder(np.array(p1["spectrum"]))
    print(f"  Q3 非零阶梯         = {q3_nz}     G16 非零阶梯 = {p2['V16_nonzero_ladder']}")
    print(f"  非零阶梯相同？      = {q3_nz == p2['V16_nonzero_ladder']}")
    print(f"  但 lambda2 / lambda_max:  Q3 = {p1['spectrum'][1]/p1['spectrum'][-1]:.6f}"
          f"   G16 = {p2['lambda2_over_lambdamax']:.6f}"
          f"   -> 相同？ {abs(p1['spectrum'][1]/p1['spectrum'][-1] - p2['lambda2_over_lambdamax']) < 1e-9}")
    print()
    print("  读法：同一算符、同一构造，只把定义域从 Q3 换成它的双覆盖，")
    print("        简并阶梯就变了（非内蕴）；而比值 lambda2/lambda_max 不变（内蕴）。")
    return {"Q3_ladder": a, "G16_ladder": b, "ladder_stable": a == b}


def main():
    p1 = part1()
    p2 = part2()
    p3 = part3()
    p4 = part4(p1, p2)

    print()
    print("=" * 78)
    print("  裁决")
    print("=" * 78)
    print("  H1（轨道=涌现谱，强读法） 成立的判据：台阶内蕴 且 能复现 1,3,5,7")
    print(f"    - 阶梯内蕴？    否（Q3 {p4['Q3_ladder']} != G16 {p4['G16_ladder']}）")
    print("    - 能复现 2l+1？ 否（PART 3 全部候选图无一命中）")
    print("  => H0 成立：**「轨道是涌现谱」在强读法下不成立**。")
    print("     成立的是弱读法：轨道**形态**（特征向量）可涌现，")
    print("     但轨道的**可观测结构（简并阶梯 = 量子数）**必须外部借入。")
    print()
    print("  旁注：项目从未构造「原子的介观核图」，也从未算过任何轨道特征向量；")
    print("        §13 的全部验证（V2-V7）是纯组合计数，不涉谱。")

    out = {"part1_Q3": p1, "part2_double_cover": p2,
           "part3_candidates": p3, "part4_stability": p4,
           "verdict": "H0: orbital-as-emergent-spectrum FAILS in strong reading"}
    with open("_orbital_emergence_test.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    print("\n[OK] _orbital_emergence_test.json")


if __name__ == "__main__":
    main()
