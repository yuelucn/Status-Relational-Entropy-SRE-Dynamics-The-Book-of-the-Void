# -*- coding: utf-8 -*-
"""_probe_y3_facts.py -- 探路：测 Y3 骨架若干关键事实（供 104 轮主实验定方案）

只做探测，不下判决。测项：
  1. 19 处 y3 实现是否给出同构图（isomorphism），以及 Y3 闭/开 与 Q3 的桥接边数（min edge deletions）。
  2. Y3闭 的桥（bridge）数、边连通度、3-正则性。
  3. Y3闭 的偶圈清单与「nice even cycle」候选（Kasteleyn 定向的经典障碍）。
  4. Y3闭 与 M12 的严格不变量对照（三角形数、谱、圈数分布、邻接谱）。
  5. Aut(Y3闭) 的群结构（阶、是否可解）与 Aut(M12) 的阶 —— 为「覆盖/商/双覆盖」判决备料。
  6. 可能的自同构计数：Y3闭 的 2 个边轨道各 9 条；Y3开 的 7 轨道。
"""
import sys
import json
import itertools
from collections import Counter

sys.path.insert(0, r"C:\mywork\vasp")
sys.path.insert(0, r"C:\mywork\vasp\code")

import networkx as nx
import numpy as np

from _bridge101_nucleon import y3_closed, y3_open, q3
from _pfcore import mobius, prism, norm_edges


def facts_basic():
    print("=" * 88)
    print("[1] 桥接与边连通度")
    print("=" * 88)
    out = {}
    for tag, G in (("Y3闭", y3_closed()), ("Y3开", y3_open()),
                   ("Q3", q3()), ("M12", nx.Graph(mobius(6)))):
        degs = sorted(dict(G.degree()).values())
        br = list(nx.bridges(G))
        # 边连通度
        try:
            lam = nx.edge_connectivity(G)
        except Exception:
            lam = None
        tri = sum(nx.triangles(G).values()) // 3
        print("  %-6s V=%2d E=%2d  度序列=%s  桥=%d  λ边=%s  三角形=%d  β1=%d" %
              (tag, G.number_of_nodes(), G.number_of_edges(),
               str(Counter(degs)), len(br), lam, tri,
               G.number_of_edges() - G.number_of_nodes() + 1))
        out[tag] = dict(V=G.number_of_nodes(), E=G.number_of_edges(),
                        deg=Counter(degs), bridges=len(br), lam=lam,
                        tri=tri,
                        b1=G.number_of_edges() - G.number_of_nodes() + 1)
    return out


def facts_even_cycles():
    print()
    print("=" * 88)
    print("[2] 偶圈与 nice even cycle 候选（Pfaffian 定向的经典障碍）")
    print("=" * 88)
    for tag, G in (("Y3闭", y3_closed()), ("Y3开", y3_open()),
                   ("M12", nx.Graph(mobius(6)))):
        # 枚举所有简单圈（顶点数小，穷举可行）
        cycles = []
        seen = set()
        for start in G.nodes():
            for cyc in _simple_cycles_from(G, start):
                key = frozenset(frozenset((cyc[i], cyc[(i + 1) % len(cyc)]))
                                for i in range(len(cyc)))
                if len(key) != len(cyc):
                    continue
                # 只保留以 start 为最小代表
                if min(cyc) != start:
                    continue
                if key in seen:
                    continue
                seen.add(key)
                cycles.append(cyc)
        lens = Counter(len(c) for c in cycles)
        print("  %-6s 简单圈总数=%d 长度分布=%s" % (tag, len(cycles), dict(sorted(lens.items()))))
        # nice even cycle: 长度 ≡ 0 mod 4，且每条边恰在 2 个完美匹配中
        nice = []
        for c in cycles:
            L = len(c)
            if L % 4 != 0:
                continue
            ce = set(frozenset((c[i], c[(i + 1) % L])) for i in range(L))
            mpm = _matching_edge_multiplicity(G)
            if all(mpm.get(frozenset(e), 0) == 2 for e in ce):
                nice.append(c)
        print("        nice even cycle (|C|≡0 mod 4 且每边恰在 2 个完美匹配中) = %d 条" % len(nice))
        for c in nice[:6]:
            print("           ", c)
    return


def _simple_cycles_from(G, start):
    """从 start 出发的所有简单圈（DFS，不重复顶点）。"""
    res = []
    n = G.number_of_nodes()
    path = [start]
    used = {start}

    def dfs(v):
        for w in G.neighbors(v):
            if w == start and len(path) >= 3:
                res.append(list(path))
                continue
            if w in used:
                continue
            used.add(w)
            path.append(w)
            dfs(w)
            path.pop()
            used.discard(w)

    dfs(start)
    return res


def _matching_edge_multiplicity(G):
    """每条边出现在多少个完美匹配中。"""
    nodes = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    adj = {v: [] for v in nodes}
    for (u, v) in G.edges():
        adj[u].append(v)
        adj[v].append(u)
    cnt = Counter()
    res = []

    def go(rem, chosen):
        if not rem:
            res.append(tuple(chosen))
            return
        v = min(rem)
        rest = rem - {v}
        for w in sorted(adj[v]):
            if w in rest:
                go(rest - {w}, chosen + [(v, w)])

    go(set(nodes), [])
    for M in res:
        for (u, v) in M:
            cnt[frozenset((u, v))] += 1
    return cnt


def facts_invariants():
    print()
    print("=" * 88)
    print("[3] Y3闭 vs M12 严格不变量对照")
    print("=" * 88)
    A = y3_closed()
    B = nx.Graph(mobius(6))
    for tag, G in (("Y3闭", A), ("M12", B)):
        ev = np.linalg.eigvalsh(nx.to_numpy_array(G))
        ev = np.sort(ev)
        cyc_len = Counter()
        for start in G.nodes():
            for c in _simple_cycles_from(G, start):
                if min(c) != start:
                    continue
                key = frozenset(frozenset((c[i], c[(i + 1) % len(c)]))
                                for i in range(len(c)))
                if len(key) == len(c):
                    cyc_len[len(c)] += 1
        print("  %-6s 谱=%s" % (tag, np.round(ev, 4)))
        print("         圈长分布=%s  邻接谱和=%s  自同构数=%d" %
              (dict(sorted(cyc_len.items())), round(float(ev.sum()), 6),
               sum(1 for _ in nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())))
    print("  同构? ", nx.is_isomorphic(A, B))


def facts_aut():
    print()
    print("=" * 88)
    print("[4] 自同构群与覆盖/商判决备料")
    print("=" * 88)
    for tag, G in (("Y3闭", y3_closed()), ("Y3开", y3_open()),
                   ("M12", nx.Graph(mobius(6))), ("Q3", q3())):
        GM = nx.algorithms.isomorphism.GraphMatcher(G, G)
        auts = list(GM.isomorphisms_iter())
        # 自同构诱导的边轨道
        edges = [tuple(sorted(e)) for e in G.edges()]
        par = {e: e for e in edges}

        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]
                x = par[x]
            return x

        for m in auts:
            for e in edges:
                f = tuple(sorted((m[e[0]], m[e[1]])))
                a, b = find(e), find(f)
                if a != b:
                    par[a] = b
        orb = {}
        for e in edges:
            orb.setdefault(find(e), []).append(e)
        sizes = sorted(len(v) for v in orb.values())
        print("  %-6s |Aut|=%-4d 边轨道数=%d 轨道大小=%s" %
              (tag, len(auts), len(orb), sizes))
    # 覆盖关系：等顶点数覆盖 => 同构
    print()
    print("  覆盖/商/双覆盖的初判：")
    print("    · Y3闭(V=12) 与 M12(V=12) 顶点数相同 ⇒ 若存在覆盖 Y3闭↠M12")
    print("      则为 1-覆盖 ⇒ 必为同构 ⇒ 由谱/三角形数不同知不存在。")


def facts_mfamily():
    print()
    print("=" * 88)
    print("[5] 莫比乌斯梯全族的 nice even cycle 计数 vs Pfaffian 实测")
    print("=" * 88)
    sys.path.insert(0, r"C:\mywork\vasp\code")
    from _bridge101_nucleon import pfaffian_classes
    print("  %-8s %-4s %-4s %-6s %-9s %-9s %-7s" %
          ("name", "V", "E", "bip", "nice_cnt", "|O_Pf|", "Pf?"))
    rows = []
    for k in range(2, 11):
        E = norm_edges(mobius(k))
        N = 2 * k
        G = nx.Graph()
        G.add_nodes_from(range(N))
        G.add_edges_from(E)
        nice = _nice_cycles(G)
        ispf, dim, cp, cm, npf, cert, npm = pfaffian_classes(N, E)
        bip = nx.is_bipartite(G)
        print("  M%-7d %-4d %-4d %-6s %-9d %-9d %-7s" %
              (N, N, len(E), bip, len(nice), npf, "Y" if ispf else "N"))
        rows.append(dict(name="M%d" % N, V=N, E=len(E), bip=bip,
                         nice=len(nice), is_pf=ispf, npf=npf))
    # 对照：非梯族
    print()
    print("  对照族：")
    for tag, G in (("Y3闭", y3_closed()), ("Y3开", y3_open()),
                   ("Q3", q3()), ("Petersen", nx.petersen_graph()),
                   ("K33", nx.complete_bipartite_graph(3, 3)),
                   ("K4", nx.complete_graph(4)),
                   ("Heawood", nx.heawood_graph()),
                   ("prism4", nx.Graph(prism(4)))):
        E = norm_edges(G.edges())
        N = G.number_of_nodes()
        nice = _nice_cycles(G)
        ispf, dim, cp, cm, npf, cert, npm = pfaffian_classes(N, E)
        print("  %-9s %-4d %-4d %-6s %-9d %-9d %-7s" %
              (tag, N, len(E), nx.is_bipartite(G), len(nice), npf,
               "Y" if ispf else "N"))
        rows.append(dict(name=tag, V=N, E=len(E), bip=nx.is_bipartite(G),
                         nice=len(nice), is_pf=ispf, npf=npf))
    return rows


def _nice_cycles(G):
    """nice even cycle: |C| ≡ 0 mod 4 且每条边恰在 2 个完美匹配中。"""
    if G.number_of_nodes() % 2 != 0:
        return []
    mpm = _matching_edge_multiplicity(G)
    res = []
    seen = set()
    for start in G.nodes():
        for c in _simple_cycles_from(G, start):
            L = len(c)
            if L % 4 != 0 or L < 4:
                continue
            if min(c) != start:
                continue
            key = frozenset(frozenset((c[i], c[(i + 1) % L])) for i in range(L))
            if len(key) != L or key in seen:
                continue
            seen.add(key)
            if all(mpm.get(frozenset(e), 0) == 2 for e in key):
                res.append(c)
    return res


def main():
    facts_basic()
    facts_even_cycles()
    facts_invariants()
    facts_aut()
    facts_mfamily()


if __name__ == "__main__":
    main()
