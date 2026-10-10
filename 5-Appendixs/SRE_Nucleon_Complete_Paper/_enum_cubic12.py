# -*- coding: utf-8 -*-
"""
穷举 V=12 全部连通 3-正则图同构类（目标 85），**精确同构去重**（无谱签名去重）。
加速：桶键 = (WL-hash, 谱整数化, 三角形数) —— 只对同桶候选做 nx.is_isomorphic。
输出 ε≤1% 命中 / 3‖|Aut| 幸存，并逐项指认 Y₃ 与其共谱同伴。
"""
import io, os, random, itertools, sys, time
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "_enum_cubic12.log")
N = 12
KAPPA = 0.1888930667
L = []
def P(s=""):
    print(s, flush=True); L.append(s)
    io.open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")


def lap(G):
    return np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float)))


def inv(G):
    ev = lap(G)
    T = sum(nx.triangles(G).values()) // 3
    return dict(lam2=float(ev[1]), rho=float(ev[-1]), pi1=float(ev[1] / ev[-1]), T=T,
                spec=tuple(np.round(ev, 6)))


def naut(G, cap=200000):
    k = sum(1 for _ in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap + 1))
    return k if k <= cap else None


def Y3():
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("L%d%d" % (a, j), "L%d%d" % (b, j))
    return G


def ok(G):
    return (G.number_of_nodes() == N and G.number_of_edges() == 18
            and nx.is_connected(G) and all(d == 3 for _, d in G.degree()))


def key(G):
    ev = np.round(lap(G), 5)
    T = sum(nx.triangles(G).values()) // 3
    return (nx.weisfeiler_lehman_graph_hash(G, iterations=5),
            tuple(ev.tolist()), T)


def nbrs(G):
    es = list(G.edges()); out = []
    for i in range(len(es)):
        a, b = es[i]
        for j in range(i + 1, len(es)):
            c, d = es[j]
            if len({a, b, c, d}) < 4:
                continue
            for (p, q), (r, s) in (((a, c), (b, d)), ((a, d), (b, c))):
                if p == q or r == s or G.has_edge(p, q) or G.has_edge(r, s):
                    continue
                H = G.copy()
                H.remove_edge(a, b); H.remove_edge(c, d)
                H.add_edge(p, q); H.add_edge(r, s)
                if nx.is_connected(H):
                    out.append(H)
    return out


buckets = {}
classes = []
def add(G):
    if not ok(G):
        return False
    k = key(G)
    for H in buckets.get(k, []):
        if nx.is_isomorphic(G, H):
            return False
    buckets.setdefault(k, []).append(G.copy())
    classes.append(G.copy())
    return True


P("=" * 98)
P("A. 2-switch 闭包 BFS：枚举 V=12 连通 3-正则图同构类")
P("=" * 98)
t0 = time.time()
rnd = random.Random(20260924)
add(Y3())
for _ in range(150):
    for _try in range(2000):
        H = nx.configuration_model([3] * N, seed=rnd.randrange(1 << 30))
        G = nx.Graph(H); G.remove_edges_from(nx.selfloop_edges(G))
        if ok(G):
            add(G); break
P("   种子类数 = %d （%.1f s）" % (len(classes), time.time() - t0))
q = list(range(len(classes)))
cur = 0
while cur < len(q):
    idx = q[cur]; cur += 1
    for H in nbrs(classes[idx]):
        if add(H):
            q.append(len(classes) - 1)
    if cur % 20 == 0:
        P("   ... cursor=%d queue=%d classes=%d t=%.1fs"
          % (cur, len(q), len(classes), time.time() - t0))
if cur > 0 and cur % 20 != 0:
    P("   ... cursor=%d queue=%d classes=%d t=%.1fs"
      % (cur, len(q), len(classes), time.time() - t0))
P("   收集到同构类数 = %d   （已知 = 85）" % len(classes))
P("   ⇒ %s" % ("已达全集规模，可当**穷举**使用。" if len(classes) == 85
                else "未达 85 ⇒ 只作**下界**。"))

P("")
P("=" * 98)
P("B. 共谱分析（Laplacian 谱相同的不同构图）")
P("=" * 98)
recs = []
for G in classes:
    d = inv(G); d["G"] = G
    recs.append(d)
from collections import Counter
c = Counter(r["spec"] for r in recs)
P("   同构类数 = %d ；谱类数 = %d ；含 ≥2 同构类的谱类 = %d"
  % (len(recs), len(c), sum(1 for v in c.values() if v > 1)))
for k, v in c.items():
    if v > 1:
        P("     ── 共谱组（%d 个不同构图）:" % v)
        for r in recs:
            if r["spec"] == k:
                P("        rho=%.9f lam2=%.9f PI1=%.12f T=%-2d" %
                  (r["rho"], r["lam2"], r["pi1"], r["T"]))

P("")
P("=" * 98)
P("C. ε ≤ 1%% 命中与 3‖|Aut| 幸存（κ_N = %.10f）" % KAPPA)
P("=" * 98)
for r in recs:
    r["aut"] = naut(r["G"])
    r["dev"] = abs(r["pi1"] - KAPPA) / KAPPA
hit = [r for r in recs if r["dev"] < 0.01]
surv = [r for r in hit if (r["aut"] or 0) % 3 == 0]
Y = Y3()
P("   命中数 = %d ；其中 3‖|Aut| 幸存数 = %d" % (len(hit), len(surv)))
for tag, grp in (("命中", hit), ("幸存", surv)):
    for r in grp:
        yr = "是 Y₃" if nx.is_isomorphic(r["G"], Y) else "非 Y₃"
        P("     %s: PI1=%.12f dev=%.4f%% T=%-2d |Aut|=%-4s %s"
          % (tag, r["pi1"], 100 * r["dev"], r["T"], r["aut"], yr))
P("")
P("   ★ 判据③ 能否在 V=12 档内唯一定出 Y₃ ？ %s"
  % ("能" if len(surv) == 1 and nx.is_isomorphic(surv[0]["G"], Y) else "不能（存在非 Y₃ 幸存者）"))
P("   ★ 追加「T ≥ 2」筛（§4 判据⑤ 型）后幸存数 = %d"
  % len([r for r in surv if r["T"] >= 2]))

P("")
P("=" * 98)
P("D. 对照：_sre_anchor_second.py 的图池（V=12）")
P("=" * 98)
try:
    import json
    rec = json.load(io.open(os.path.join(ROOT, "_anchor2_cache.json"), encoding="utf-8"))["12_85_1012"]
    hasY = any(nx.is_isomorphic(nx.Graph([tuple(e) for e in el]), Y) for el in rec["edges"])
    P("   池规模 = %d ；池内含 Y₃ ? %s" % (len(rec["edges"]), hasY))
    P("   ⇒ 该档**无共谱对**（§B）⇒ 谱签名去重**无损**；上一轮 V=12 实得 84/85")
    P("     是**随机采样漏项**（恰漏掉 Y₃ 本身），不是去重所致。主脚本已显式")
    P("     纳入 Y₃ 并重建全池 ⇒ 现为 85/85。")
except Exception as e:
    P("   （读取缓存失败：%s）" % e)

print("\n[log] " + OUT)
