# -*- coding: utf-8 -*-
"""
核子骨架并列候选打破 v2 —— 可判定性诊断 + 状态对泛函
=========================================================
背景：判据 ②③ 之后剩两个候选 A（Y3⋉△3，|Aut|=36）与 B（|Aut|=12），
      二者在 Pi_1 = lambda_2/rho 上完全相同，故 Pi_1 无法区分。

本脚本做三件事，全部为"诊断"，不做任何拟合：

  (1) 可判定性诊断：检验 A、B 是否同谱（邻接谱 / 组合 Laplacian 谱 /
      无符号 Laplacian 谱 / 归一化 Laplacian 谱）。若同谱，则一切仅以谱为
      自变量的泛函在原理上不可分辨二者——这决定了只能走非谱判据。

  (2) 泛函池判别力表：对 V=12 立方图全池（85 个）计算一批泛函，
      给出 A、B 取值、分离度、以及 A 值在全池中的稀有度（同值图数）。
      用于回答"哪些泛函真的能分开 A/B，以及分得干净不干净"。

  (3) 状态对泛函：核子侧天然可用的实测比（|r_n^2|/r_p^2、|mu_n/mu_p| 等）
      是"同一骨架 开态/闭态 之比"。因此泛函应当定义在状态对上，而不是
      单个图不变量。对 A、B 各自枚举断边（闭态 beta_1=7 -> 开态 beta_1=6），
      计算各泛函的开/闭比值分布，并与实测状态对比对。

输出：sre_nucleon_tiebreak_v2_results.json
运行：/c/myapp/miniconda3/envs/ai/python.exe _sre_nucleon_tiebreak_v2.py
"""

import sys
import json
import itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

M_P = 938.27208816
M_N = 939.56542052
M_E = 0.51099895
ALPHA = 1.0 / 137.035999084
KAPPA = ((M_N - M_P) / M_P) / ALPHA

OUT = {}
LOG = []


def P(s=""):
    LOG.append(str(s))
    print(s)


# ------------------------------------------------------------------ 图构造
def y3():
    """候选 A：三股 Y 的三角闭合体 Y3⋉△3（手构）"""
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    return nx.convert_node_labels_to_integers(G)


def build_pool(n_target=85, tries=40000, seed=11):
    """枚举 / 采样 V=12 的连通立方图全池（同构去重）"""
    rng = np.random.default_rng(seed)
    buckets, pool = {}, []
    for _ in range(tries):
        H = nx.configuration_model([3] * 12, seed=int(rng.integers(1 << 31)))
        G = nx.Graph(H)
        G.remove_edges_from(nx.selfloop_edges(G))
        if G.number_of_edges() != 18 or not nx.is_connected(G):
            continue
        k = fingerprint(G)
        b = buckets.setdefault(k, [])
        if any(nx.is_isomorphic(G, X) for X in b):
            continue
        b.append(G)
        pool.append(G)
        if len(pool) >= n_target:
            break
    return pool


def fingerprint(G):
    A = nx.to_numpy_array(G)
    return (tuple(np.round(np.linalg.eigvalsh(A), 6)),
            tuple(sorted(nx.triangles(G).values())),
            tuple(sorted(np.diag(np.linalg.matrix_power(A, 4)).astype(int))))


def aut_order(G, cap=4000):
    n = 0
    for _ in GraphMatcher(G, G).isomorphisms_iter():
        n += 1
        if n >= cap:
            break
    return n


def orbit_count(G, cap=4000):
    maps = list(itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap))
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    parent = list(range(len(nodes)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for m in maps:
        for v, w in m.items():
            a, b = find(idx[v]), find(idx[w])
            if a != b:
                parent[a] = b
    return len({find(i) for i in range(len(nodes))})


# ------------------------------------------------------------------ 谱工具
def lap_eigs(G):
    return np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))


def adj_eigs(G):
    return np.sort(np.linalg.eigvalsh(nx.to_numpy_array(G)))


def signless_eigs(G):
    A = nx.to_numpy_array(G)
    D = np.diag(A.sum(axis=1))
    return np.sort(np.linalg.eigvalsh(D + A))


def norm_lap_eigs(G):
    A = nx.to_numpy_array(G)
    d = A.sum(axis=1)
    Dm = np.diag(1.0 / np.sqrt(d))
    L = np.eye(len(d)) - Dm @ A @ Dm
    return np.sort(np.linalg.eigvalsh(L))


def resistance_matrix(G):
    L = nx.laplacian_matrix(G).toarray().astype(float)
    Lp = np.linalg.pinv(L)
    n = G.number_of_nodes()
    R = np.zeros((n, n))
    for i in range(n):
        R[i, i] = 0.0
        for j in range(i + 1, n):
            R[i, j] = R[j, i] = Lp[i, i] + Lp[j, j] - 2 * Lp[i, j]
    return R


# ------------------------------------------------------------------ 泛函池
def functionals(G):
    """一批泛函（谱类 + 组合类），全部为无量纲或纯整数"""
    A = nx.to_numpy_array(G)
    n = G.number_of_nodes()
    e = G.number_of_edges()
    b1 = e - n + 1
    lev = lap_eigs(G)
    aev = adj_eigs(G)
    T = sum(nx.triangles(G).values()) // 3
    R = resistance_matrix(G)
    tri = nx.triangles(G)
    # 谱熵（归一化 Laplacian 谱）
    nl = norm_lap_eigs(G)
    p = nl / nl.sum()
    p = p[p > 1e-12]
    spect_ent = float(-(p * np.log(p)).sum() / np.log(n))
    # 生成树数（Kirchhoff 树定理，属谱类）
    st = float(np.prod(lev[1:]) / n)
    # Estrada 指数（邻接谱）
    estrada = float(np.exp(aev).sum())
    d = dict(
        # 组合类（非谱）
        T_triangles=T,
        T_over_E=T / e,
        T_over_beta1=T / b1,
        T_over_V=T / n,
        max_tri_per_vertex=int(max(tri.values())),
        n_vertices_in_triangles=int(sum(1 for v in tri if tri[v] > 0)),
        Wiener=float(nx.wiener_index(G)),
        diameter=float(nx.diameter(G)),
        mean_resistance=float(R.sum() / (n * (n - 1))),
        max_resistance=float(R.max()),
        Kirchhoff=float(R.sum() / 2),
        resistance_hetero=float(R[np.triu_indices(n, 1)].std() / R[np.triu_indices(n, 1)].mean()),
        # 谱类
        lambda2=float(lev[1]),
        rho=float(lev[-1]),
        Pi1=float(lev[1] / lev[-1]),
        Pi2_lam2_over_lam4=float(lev[1] / lev[3]),
        Pi3_lam3_over_lam2=float(lev[2] / lev[1]),
        n_distinct_eigs=int(len(set(np.round(lev, 6)))),
        spectral_entropy=spect_ent,
        n_spanning_trees=st,
        log_spanning_trees=float(np.log(st)) if st > 0 else 0.0,
        estrada=estrada,
        adj_lambda2=float(aev[-2]),
        adj_spectral_gap=float(aev[-1] - aev[-2]),
    )
    return d


def report_funct_table(dA, dB, pool_d):
    keys = list(dA.keys())
    rows = []
    for k in keys:
        va, vb = dA[k], dB[k]
        scale = max(abs(va), abs(vb), 1e-12)
        sep = abs(va - vb) / scale
        vals = np.array([pool_d[g][k] for g in range(len(pool_d))], dtype=float)
        tol = 1e-9 * scale + 1e-12
        n_same_A = int(np.sum(np.abs(vals - va) <= tol))
        lo, hi = min(va, vb), max(va, vb)
        n_between = int(np.sum((vals > lo + tol) & (vals < hi - tol)))
        # A 的百分位
        pct = float(np.mean(vals <= va))
        rows.append(dict(name=k, A=float(va), B=float(vb), sep=float(sep),
                         n_pool_same_as_A=n_same_A, n_pool_between=n_between,
                         pct_A=pct))
    rows.sort(key=lambda r: -r["sep"])
    return rows


def edge_orbit_count(G, cap=4000):
    """边的自同构轨道数：结构上"不同种类的边"有几类"""
    edges = [tuple(sorted(e)) for e in G.edges()]
    maps = itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap)
    parent = {e: e for e in edges}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for m in maps:
        for e in edges:
            f = tuple(sorted((m[e[0]], m[e[1]])))
            a, b = find(e), find(f)
            if a != b:
                parent[a] = b
    return len({find(e) for e in edges})


# ------------------------------------------------------------------ 主流程
P("=" * 78)
P("[0] 建立 V=12 立方连通图全池")
P("=" * 78)
pool = build_pool()
P("  池内不同构图数 = %d" % len(pool))
A = y3()
B = nx.Graph()
B.add_edges_from(json.load(open("sre_nucleon_tiebreak_results.json",
                                encoding="utf-8"))["candidate_B_edges"])
B = nx.convert_node_labels_to_integers(B)
in_pool = [nx.is_isomorphic(A, G) for G in pool]
P("  A 在池内：%s ；B 在池内：%s" % (any(in_pool), any(nx.is_isomorphic(B, G) for G in pool)))
OUT["pool_size"] = len(pool)

P("")
P("=" * 78)
P("[1] 可判定性诊断：A 与 B 是否同谱")
P("=" * 78)
spec = {}
for name, fn in (("adjacency", adj_eigs), ("Laplacian", lap_eigs),
                 ("signless_L", signless_eigs), ("normalized_L", norm_lap_eigs)):
    ea, eb = np.round(fn(A), 8), np.round(fn(B), 8)
    same = bool(np.allclose(ea, eb, atol=1e-7))
    spec[name] = dict(cospectral=same, max_diff=float(np.abs(ea - eb).max()),
                      A=[float(x) for x in ea])
    P("  %-14s 同谱 = %-5s   最大特征值差 = %.3e" % (name, same, np.abs(ea - eb).max()))
OUT["cospectral"] = {k: dict(cospectral=v["cospectral"], max_diff=v["max_diff"])
                     for k, v in spec.items()}
P("")
P("  组合 Laplacian 谱（A）: " + ", ".join("%.4f" % x for x in spec["Laplacian"]["A"]))
P("  组合 Laplacian 谱（B）: " + ", ".join("%.4f" % x for x in np.round(lap_eigs(B), 8)))
# 全池中与 A 同谱的图有几个
lA = np.round(lap_eigs(A), 6)
n_cospec = sum(1 for G in pool if np.allclose(np.round(lap_eigs(G), 6), lA, atol=1e-7))
P("  全池中与 A 同（Laplacian）谱的图数 = %d" % n_cospec)
OUT["n_pool_cospectral_with_A"] = int(n_cospec)

P("")
P("=" * 78)
P("[2] 泛函池判别力：哪些泛函能分开 A/B")
P("=" * 78)
dA, dB = functionals(A), functionals(B)
pool_d = [functionals(G) for G in pool]
tab = report_funct_table(dA, dB, pool_d)
P("  %-24s %14s %14s %10s %8s %8s" % ("泛函", "A", "B", "分离度", "池内同A", "A百分位"))
for r in tab:
    P("  %-24s %14.6f %14.6f %9.2e %8d %7.1f%%"
      % (r["name"], r["A"], r["B"], r["sep"], r["n_pool_same_as_A"], 100 * r["pct_A"]))
OUT["functional_table"] = tab
sep_ok = [r["name"] for r in tab if r["sep"] > 1e-6]
P("")
P("  可分离 A/B 的泛函数量 = %d / %d" % (len(sep_ok), len(tab)))
P("  其中谱类可分离者 = %s"
  % [n for n in sep_ok if n.startswith(("lambda", "rho", "Pi", "adj", "estrada", "n_distinct",
                                        "spectral", "spanning"))])
OUT["separable_functionals"] = sep_ok

P("")
P("  候选 A 的谱类/组合类特征：T=%d, beta1=%d, T/beta1=%.4f, |Aut|=%d, orbits=%d"
  % (dA["T_triangles"], 7, dA["T_over_beta1"], aut_order(A), orbit_count(A)))
P("  候选 B 的谱类/组合类特征：T=%d, beta1=%d, T/beta1=%.4f, |Aut|=%d, orbits=%d"
  % (dB["T_triangles"], 7, dB["T_over_beta1"], aut_order(B), orbit_count(B)))
OUT["candidates"] = dict(
    A=dict(aut=aut_order(A), orbits=orbit_count(A), **{k: float(v) for k, v in dA.items()}),
    B=dict(aut=aut_order(B), orbits=orbit_count(B), **{k: float(v) for k, v in dB.items()}))

P("")
P("  池内三角环数分布：")
from collections import Counter
cnt = Counter(functionals(G)["T_triangles"] for G in pool)
for k in sorted(cnt):
    P("    T=%2d : %2d 个图 (%.1f%%)" % (k, cnt[k], 100 * cnt[k] / len(pool)))
OUT["pool_triangle_dist"] = {str(k): int(v) for k, v in cnt.items()}

# 池内同时满足 Pi1 3% 内 的图
near = [(G, abs(functionals(G)["Pi1"] - KAPPA) / KAPPA) for G in pool]
near = [(G, d) for G, d in near if d < 0.03]
P("")
P("  池内同时满足 [Pi1 偏差<3%%] 的图数 = %d" % len(near))
for G, d in near:
    f = functionals(G)
    P("    dev=%6.3f%%  T=%d  T/beta1=%.4f  |Aut|=%s"
      % (100 * d, f["T_triangles"], f["T_over_beta1"],
         aut_order(G) if d < 0.005 else "-"))
OUT["near_pool"] = [dict(dev=float(d), T=int(functionals(G)["T_triangles"]),
                         aut=aut_order(G)) for G, d in near]

P("")
P("=" * 78)
P("[3] 状态对泛函：开态/闭态 之比（核子侧实测比天生是这一结构）")
P("=" * 78)
targets = {
    "|r_n^2|/r_p^2": abs(-0.1161) / 0.84075 ** 2,
    "|mu_n/mu_p|": 1.9130 / 2.7928,
}
for k, v in targets.items():
    P("  实测 %-16s = %.6f" % (k, v))

state_rows = []
for tag, G in (("A", A), ("B", B)):
    closed = functionals(G)
    seen = []
    for e in G.edges():
        H = G.copy()
        H.remove_edge(*e)
        if not nx.is_connected(H):
            continue
        op = functionals(H)
        ratios = {}
        for k in closed:
            cv, ov = closed[k], op[k]
            if abs(cv) > 1e-12:
                ratios[k] = ov / cv
        seen.append((tuple(e), ratios))
    P("")
    P("  候选 %s ：闭态 beta1=7 -> 可断边 %d 条（均保持连通）" % (tag, len(seen)))
    for fn in ("Pi1", "lambda2", "rho", "mean_resistance", "Wiener", "Kirchhoff",
               "spectral_entropy", "T_triangles", "T_over_beta1"):
        vals = np.array([r[1][fn] for r in seen])
        P("    %-18s 开/闭 = min %.6f  max %.6f  mean %.6f  (闭态值 %.6f)"
          % (fn, vals.min(), vals.max(), vals.mean(), closed[fn]))
        for tname, tv in targets.items():
            dev = np.abs(vals - tv) / tv
            i = int(np.argmin(dev))
            state_rows.append(dict(candidate=tag, func=fn, target=tname,
                                   best_dev=float(dev[i]), best_val=float(vals[i]),
                                   edge=list(seen[i][0])))
    # 断边在自同构下的轨道数（结构上"不同种类的断法"有几类）
    eorb = edge_orbit_count(G)
    P("    断边轨道数（自同构等价类）= %d" % eorb)
    OUT["state_pair_%s" % tag] = dict(n_edge_removals=len(seen), edge_orbits=eorb)
P("")
P("  状态对比对（每个泛函只取最贴近实测的一组，登记为线索）：")
state_rows.sort(key=lambda r: r["best_dev"])
for r in state_rows[:14]:
    P("    %-3s %-18s <- %-16s 偏差 %6.3f%%  值 %.6f  断边 %s"
      % (r["candidate"], r["func"], r["target"], 100 * r["best_dev"],
         r["best_val"], r["edge"]))
OUT["state_pair_matches"] = state_rows
P("")
P("  比对基数 = 2 候选 x 9 泛函 x 2 实测 = %d 次；<5%% 阈值下偶然期望 %.1f 次"
  % (len(state_rows), 0.05 * len(state_rows)))

with open("sre_nucleon_tiebreak_v2_results.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P("")
P("已写出 sre_nucleon_tiebreak_v2_results.json")
