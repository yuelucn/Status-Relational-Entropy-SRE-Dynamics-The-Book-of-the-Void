# -*- coding: utf-8 -*-
"""
按用户裁决（2026-09-22）重做核子候选 A/B 的过渡结构分析：

  (a) 休眠边取【环边】(ring edge)
      —— 理由：休眠边本身也是同态映射的像，逻辑深度大，故取环边可能性更大；
  (b) 【模的释放】不作为判据
      —— 理由：那只是同态映射的偶然，不是必然的离散量。

本脚本只回答四个问题：
  Q1 环边打开后，A / B 各自的过渡读数（lambda2, rho, T, 连通性）是什么；
  Q2 读数在等价边轨道上是否唯一（自洽性判据，保留）；
  Q3 该判据在全池 85 图中的稀有度，与 Pi1<3% 联合后的命中数；
  Q4 环边读数比（闭合单元计数比）与实测无量纲比的对照。

输出：sre_nucleon_ringedge_transition_results.json
"""
import sys, json, itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

M_P, M_N = 938.27208816, 939.56542052
MU_P, MU_N = 2.79284734, -1.91304273
ALPHA = 1 / 137.035999084
DM = (M_N - M_P) / M_P
KAPPA = DM / ALPHA
MU_RATIO = abs(MU_N / MU_P)

OUT = {}


def y3():
    """三股 Y 三角闭合体 Y3  x  triangle3"""
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    return nx.convert_node_labels_to_integers(G)


def load_B():
    d = json.load(open("sre_nucleon_tiebreak_results.json", encoding="utf-8"))
    return nx.convert_node_labels_to_integers(nx.Graph(d["candidate_B_edges"]))


def lam(G):
    return np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))


def edge_orbits(G, cap=6000):
    edges = [tuple(sorted(e)) for e in G.edges()]
    parent = {e: e for e in edges}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for m in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap):
        for e in edges:
            f = tuple(sorted((m[e[0]], m[e[1]])))
            a, b = find(e), find(f)
            if a != b:
                parent[a] = b
    groups = {}
    for e in edges:
        groups.setdefault(find(e), []).append(e)
    return list(groups.values())


def aut_order(G, cap=20000):
    n = 0
    for _ in GraphMatcher(G, G).isomorphisms_iter():
        n += 1
        if n >= cap:
            break
    return n


def T_of(G):
    return sum(nx.triangles(G).values()) // 3


def ring_vertices(G):
    tri = nx.triangles(G)
    return {v for v in G if tri[v] > 0}


def state_readings(G):
    """逐边轨道打开一条边后的读数"""
    ev = lam(G)
    onring = ring_vertices(G)
    Tc = T_of(G)
    rows = []
    for orb in edge_orbits(G):
        e = orb[0]
        kind = "ring" if (e[0] in onring and e[1] in onring) else "channel"
        H = G.copy()
        H.remove_edge(*e)
        evh = lam(H)
        rows.append({
            "kind": kind, "orbit_size": len(orb), "rep_edge": list(e),
            "lam2": float(evh[1]), "rho": float(evh[-1]),
            "d_lam2": float(evh[1] - ev[1]),
            "T_open": T_of(H), "T_closed": Tc,
            "connected": bool(nx.is_connected(H)),
        })
    return rows


def summarize(G, tag):
    ev = lam(G)
    orbs = edge_orbits(G)
    rows = state_readings(G)
    onring = ring_vertices(G)
    Tc = T_of(G)
    # rho 的全边不变性
    rhos = []
    for e in G.edges():
        H = G.copy()
        H.remove_edge(*e)
        rhos.append(lam(H)[-1])
    lam2s = []
    for e in G.edges():
        H = G.copy()
        H.remove_edge(*e)
        lam2s.append(lam(H)[1])

    ring_rows = [r for r in rows if r["kind"] == "ring"]
    chan_rows = [r for r in rows if r["kind"] == "channel"]

    info = {
        "tag": tag,
        "V": G.number_of_nodes(), "E": G.number_of_edges(),
        "beta1": G.number_of_edges() - G.number_of_nodes() + 1,
        "|Aut|": aut_order(G),
        "T_closed": Tc,
        "n_ring_vertices": len(onring),
        "lam2_closed": float(ev[1]), "rho_closed": float(ev[-1]),
        "Pi1": float(ev[1] / ev[-1]),
        "m_lam2": int(np.sum(np.isclose(ev, ev[1], atol=1e-6))),
        "n_edge_orbits": len(orbs),
        "orbit_sizes": sorted(len(o) for o in orbs),
        "rho_span_all_18": float(max(rhos) - min(rhos)),
        "lam2_readings_all": sorted({round(x, 9) for x in lam2s}),
        "n_lam2_readings_ring": len({round(r["lam2"], 9) for r in ring_rows}),
        "n_T_readings_ring": len({r["T_open"] for r in ring_rows}),
        "ring_open_lam2": sorted({round(r["lam2"], 9) for r in ring_rows}),
        "ring_open_T": sorted({r["T_open"] for r in ring_rows}),
        "channel_open_lam2": sorted({round(r["lam2"], 9) for r in chan_rows}),
        "channel_open_T": sorted({r["T_open"] for r in chan_rows}),
        "rows": rows,
    }
    return info


# ------------------------------------------------------------------ 主流程
A = y3()
B = load_B()

print("=" * 78)
print("实测无量纲比   dm/m_p = %.9f   kappa = %.9f   |mu_n/mu_p| = %.6f"
      % (DM, KAPPA, MU_RATIO))
print("=" * 78)

for tag, G in (("A = Y3 x triangle3", A), ("B", B)):
    s = summarize(G, tag)
    print()
    print("### 候选 %s" % tag)
    print("   V=%d  E=%d  beta1=%d  |Aut|=%d  T_closed=%d  ring_vertices=%d"
          % (s["V"], s["E"], s["beta1"], s["|Aut|"], s["T_closed"], s["n_ring_vertices"]))
    print("   lam2=%.9f  rho=%.9f  Pi1=%.9f  m(lam2)=%d"
          % (s["lam2_closed"], s["rho_closed"], s["Pi1"], s["m_lam2"]))
    print("   边轨道数=%d  轨道大小=%s" % (s["n_edge_orbits"], s["orbit_sizes"]))
    print("   [rho 不变性] 全部 %d 条边逐条打开，rho 极差 = %.3e" % (s["E"], s["rho_span_all_18"]))
    print("   [lambda2] 全部打开读数 = %s" % s["lam2_readings_all"])
    print("   [环边类] 打开后 lambda2 = %s   T = %s   读数种数(lam2=%d, T=%d)"
          % (s["ring_open_lam2"], s["ring_open_T"],
             s["n_lam2_readings_ring"], s["n_T_readings_ring"]))
    print("   [通道类] 打开后 lambda2 = %s   T = %s"
          % (s["channel_open_lam2"], s["channel_open_T"]))
    print("   逐轨道：")
    for r in s["rows"]:
        print("     %-8s |orbit|=%d 边%-10s -> lam2=%.9f  T=%d->%d  连通=%s"
              % (r["kind"], r["orbit_size"], str(r["rep_edge"]),
                 r["lam2"], r["T_closed"], r["T_open"], r["connected"]))
    OUT[tag] = s

# 闭合单元比 与 实测比 对照
print()
print("=" * 78)
print("环边读数比（闭合单元计数）与实测无量纲比对照")
print("=" * 78)
for tag, G in (("A = Y3 x triangle3", A), ("B", B)):
    Tc = T_of(G)
    ring_rows = [r for r in state_readings(G) if r["kind"] == "ring"]
    if not ring_rows:
        print("   %-20s 无环边" % tag)
        continue
    for r in ring_rows:
        if r["orbit_size"] > 1 and r is not ring_rows[0]:
            continue
        ratio = r["T_open"] / Tc if Tc else float("nan")
        dev = abs(ratio - MU_RATIO) / MU_RATIO * 100 if ratio == ratio else float("nan")
        print("   %-20s  T: %d -> %d   比 = %.6f   |mu_n/mu_p|=%.6f  偏 %s"
              % (tag, Tc, r["T_open"], ratio, MU_RATIO,
                 "%.2f%%" % dev if dev == dev else "n/a"))
OUT["measured"] = {"dm_over_mp": DM, "kappa": KAPPA, "mu_ratio": MU_RATIO}

# ------------------------------------------------------------------ 全池稀有度
print()
print("=" * 78)
print("全池 85 图稀有度")
print("=" * 78)


def fingerprint(G):
    M = nx.to_numpy_array(G)
    return (tuple(np.round(np.linalg.eigvalsh(M), 6)),
            tuple(sorted(nx.triangles(G).values())),
            tuple(sorted(np.diag(np.linalg.matrix_power(M, 4)).astype(int))))


def build_pool(n=85):
    rng = np.random.default_rng(11)
    buckets, pool = {}, []
    for _ in range(40000):
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
        if len(pool) >= n:
            break
    return pool


pool = build_pool(85)
print("池大小 =", len(pool))

stat = []
for G in pool:
    ev = lam(G)
    Tc = T_of(G)
    onring = ring_vertices(G)
    ring_edges = [e for e in G.edges() if e[0] in onring and e[1] in onring]
    lam2r, Tr = [], []
    for e in ring_edges:
        H = G.copy()
        H.remove_edge(*e)
        lam2r.append(round(lam(H)[1], 9))
        Tr.append(T_of(H))
    stat.append({
        "Pi1": float(ev[1] / ev[-1]),
        "T": Tc,
        "n_ring_edges": len(ring_edges),
        "n_lam2_readings": len(set(lam2r)),
        "n_T_readings": len(set(Tr)),
        "T_open_min": min(Tr) if Tr else None,
        "all_connected": all(nx.is_connected(G.copy().subgraph(G.nodes())) for _ in [0]),
    })

in3 = [s for s in stat if abs(s["Pi1"] - KAPPA) / KAPPA < 0.03]
print("Pi1<3%% 的图数 = %d" % len(in3))

c_ringunique = [s for s in stat if s["n_ring_edges"] > 0 and s["n_T_readings"] == 1]
print("[环边读数唯一的 T] 全池 %d / 85" % len(c_ringunique))
j1 = [s for s in in3 if s["n_ring_edges"] > 0 and s["n_T_readings"] == 1]
print("[Pi1<3%%] AND [环边 T 读数唯一] = %d" % len(j1))

c_keep = [s for s in stat if s["T"] >= 2 and s["n_ring_edges"] > 0 and s["n_T_readings"] == 1]
print("[T_closed>=2] AND [环边 T 读数唯一] 全池 %d / 85" % len(c_keep))
j2 = [s for s in in3 if s["T"] >= 2 and s["n_ring_edges"] > 0 and s["n_T_readings"] == 1]
print("[Pi1<3%%] AND [T_closed>=2] AND [环边 T 读数唯一] = %d" % len(j2))

c_open_alive = [s for s in stat if s["T"] >= 1 and s["n_ring_edges"] > 0 and s["T_open_min"] >= 1]
print("[开态仍保有闭合单元 T_open>=1] 全池 %d / 85" % len(c_open_alive))
j3 = [s for s in in3 if s["T"] >= 1 and s["n_ring_edges"] > 0 and s["T_open_min"] >= 1]
print("[Pi1<3%%] AND [开态 T_open>=1] = %d" % len(j3))
for s in j3:
    print("    Pi1=%.6f  T=%d  ring_edges=%d  T_open_min=%d"
          % (s["Pi1"], s["T"], s["n_ring_edges"], s["T_open_min"]))

from collections import Counter
print()
print("池内 T_closed 分布：", dict(sorted(Counter(s["T"] for s in stat).items())))
print("满足 Pi1<3%% 的图（%d 个）明细：" % len(in3))
for s in sorted(in3, key=lambda x: x["Pi1"]):
    print("    Pi1=%.6f  T=%d  ring_edges=%d  n_lam2_read=%d  n_T_read=%d  T_open_min=%s"
          % (s["Pi1"], s["T"], s["n_ring_edges"], s["n_lam2_readings"],
             s["n_T_readings"], s["T_open_min"]))

OUT["pool"] = {
    "n": len(pool),
    "n_Pi1_in3pct": len(in3),
    "n_ring_T_unique": len(c_ringunique),
    "joint_Pi1_ring_T_unique": len(j1),
    "joint_Pi1_T2_ring_T_unique": len(j2),
    "joint_Pi1_open_alive": len(j3),
    "T_dist": dict(sorted(Counter(s["T"] for s in stat).items())),
    "near_detail": sorted(in3, key=lambda x: x["Pi1"]),
}

json.dump(OUT, open("sre_nucleon_ringedge_transition_results.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=str)
print()
print("[OK] written sre_nucleon_ringedge_transition_results.json")
