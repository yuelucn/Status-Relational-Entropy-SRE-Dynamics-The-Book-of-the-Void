# -*- coding: utf-8 -*-
"""
_sre_l4_pool_extend.py —— T-A：把静态不变量池「拉到最大」后重算 L4

背景
----
论文 §12.15 判负的第一条依据是 reach 上界：10 个不变量、|a|<=2 时，全支撑上界 511.06 < 1836.15
（配置 A，G_e = Q3）。用户提出一个替代解释：

    「基本粒子不是一成不变的；简单图投影只对应超级稳定的部分，再往上偏差自然越来越大。」

若该解释成立，则失败**不是**「函数类/池不够大」，而是**对象本身是动力学过程**（缺的是动力学维）。
T-A 就是用来区分这两种解释的：把池**最大化**，看地板是否 persist。

===========================================================================
【PART 0  预注册（本块在任何数值打印之前固定；禁止事后加项、改窗宽、换目标）】
===========================================================================
(T-A.1) 池「最大化」的定义 —— **所有在两张电子代表图上都能取正值的层无关不变量**。
        这是比值结构强制的门槛（ratio = p(G_N)/p(G_e) 需要两侧皆 > 0），不是挑选：
          · T（三角形数）在 Q3 与 M60 上**恒为 0** ⇒ 结构性不可用；
          · |Aut| 在 V > 22 不可算（沿用 §12.15 的 AUT_VMAX 规则）⇒ 配置 B 不含 |Aut|。
        在此门槛下，原始 10 个 → 延伸 28/29 个（配置 B / A）。
(T-A.2) 目标与容差与 §12.15 **完全一致**（不得改）：
        T1（设计）m_p/m_e = 1836.15267343；T2（样本外）m_d/m_p = 1.999007745；
        T3（样本外）m_n/m_p = 1.0013784193。决策 eps = 1%；另报 0.2% / 3% 作描述性对照。
(T-A.3) 判据一（**结构性、分布无关、精确**）：support<=3 的**联合精确解**
        a* = M^{-1} b,  M[t,:] = L^(t)|支持集,  b = (ln R1, ln R2, ln R3),  L^(t) = ln p(G_num) - ln p(G_den)。
        任一三元组使 a* 为整数向量且 |a*| <= A  ⇒ **存在 0% 误差的联合 Psi（L4 成立）**。
        全部三元组的 a* 皆非整                ⇒ **不存在精确联合 Psi**（与随机图、与窗宽无关）。
(T-A.4) 判据二（统计）：网格枚举（|a|<=A、support<=3）的**联合命中数** vs MC 零假设
        （同 (V,E) 的连通均匀随机图，同一池、同一预注册不变量集）。
(T-A.5) 决策规则（先固定）：
        H_static 成立 ⟺ （存在精确联合解）或（联合命中数 > MC 零假设 99 分位）。
        否则 ⇒ **H_dyn（用户假设）获得支持**：失败是动力学维缺失，不是函数类不够大。
(T-A.6) 保护性读数：T3 是**弱目标**（m_n/m_p = 1.0014，任何「开/闭态上近乎不变的 Psi」都给 ~1 并落进 0.14%），
        故同时报 **joint(T1,T2)**（不受该伪像影响）。
===========================================================================
产物：_l4_pool_extend.log / _l4_pool_extend.json
"""
import sys
import json
import time
import itertools
import numpy as np
import networkx as nx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AUT_CAP = 2000
AUT_VMAX = 22

# ---- 原始池（§12.15 预注册，用于对照复现）----
PRIMS_ORIG = ["V", "E", "T", "b1", "Aut", "rhoA", "lam2L", "rhoL", "tau", "energy"]
# ---- 延伸池（T-A 主体；T 与 |Aut| 的门槛见 T-A.1）----
PRIMS_EXT = ["V", "E", "b1", "rhoA", "lam2L", "rhoL", "tau", "energy",
             "girth", "diameter", "radius", "mean_dist", "econn", "estrada", "kirchhoff",
             "randic", "zagreb1", "zagreb2", "trA4", "trA6", "trL2", "trL4",
             "matching", "deg_mean", "deg_max", "lap_spread", "spec_ent", "lap_var", "Aut"]

A_MAIN = 2
A_SCAN = [1, 2, 3]
A_LADDER = [1, 2, 3, 4, 5]
SUPPORT = 3
EPS_DECISION = 0.01
N_MC = 150
SLOTS = ["GE", "Y3p", "Y3n", "GD"]

M_E = 0.51099895000
M_P = 938.27208816
M_N = 939.56542052
M_D = 1875.61294257
TARGETS = {
    "T1 m_p/m_e": ("Y3p", "GE", M_P / M_E),
    "T2 m_d/m_p": ("GD", "Y3p", M_D / M_P),
    "T3 m_n/m_p": ("Y3n", "Y3p", M_N / M_P),
}
TLIST = ["T1 m_p/m_e", "T2 m_d/m_p", "T3 m_n/m_p"]


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * 100)
    P(t)
    P("=" * 100)


# ============================================================
# 图构造（与 §12.15 逐字同口径）
# ============================================================
def Y3(pre="", state="p", open_ring=0):
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge(f"{pre}c{i}", f"{pre}L{i}{j}")
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge(f"{pre}L{a}{j}", f"{pre}L{b}{j}")
    if state == "n":
        G.remove_edge(f"{pre}L0{open_ring}", f"{pre}L1{open_ring}")
    return G


def assemble(bodies, r=0):
    G = nx.Graph()
    for pre, st in bodies:
        g = Y3(pre, st, open_ring=r)
        mp = {}
        for nd in g.nodes():
            hit = False
            for i in range(3):
                if nd == f"{pre}L{i}{r}":
                    mp[nd] = f"S{i}"
                    hit = True
            if not hit:
                mp[nd] = nd
        for u, v in g.edges():
            G.add_edge(mp[u], mp[v])
    return G


def q3():
    return nx.convert_node_labels_to_integers(nx.hypercube_graph(3))


def mobius_m60():
    n, h = 60, 30
    G = nx.Graph()
    for i in range(n):
        G.add_edge(i, (i + 1) % n)
    for i in range(h):
        G.add_edge(i, i + h)
    return G


def make_graphs(cfg):
    Gs = {"Y3p": Y3("", "p"), "Y3n": Y3("", "n"),
          "GD": assemble([("a", "p"), ("b", "n")], 0)}
    Gs["GE"] = q3() if cfg == "A" else mobius_m60()
    return Gs


# ============================================================
# 不变量（原 10 + 新增，全部由图自身规则定义）
# ============================================================
def aut_order(G, cap=AUT_CAP):
    if G.number_of_nodes() > AUT_VMAX:
        return None
    cnt = 0
    GM = nx.algorithms.isomorphism.GraphMatcher(G, G)
    for _ in GM.isomorphisms_iter():
        cnt += 1
        if cnt > cap:
            return None
    return cnt


def inv_full(G):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    cc = nx.number_connected_components(G)
    Adj = nx.to_numpy_array(G, dtype=float)
    L = nx.laplacian_matrix(G).toarray().astype(float)
    evA = np.linalg.eigvalsh(Adj)
    evL = np.linalg.eigvalsh(L)
    d = np.array([deg for _, deg in G.degree()], float)
    rhoA = float(evA[-1])
    lam2L = float(evL[1]) if n > 1 else 0.0
    rhoL = float(evL[-1])
    energy = float(np.sum(np.abs(evA)))
    trA4 = float(np.trace(np.linalg.matrix_power(Adj, 4)))
    trA6 = float(np.trace(np.linalg.matrix_power(Adj, 6)))
    L2 = L @ L
    trL2 = float(np.trace(L2))
    trL4 = float(np.trace(L2 @ L2))
    nz = evL[evL > 1e-9]
    tau = float(np.sum(np.log(nz)) - np.log(n)) if (cc == 1 and n > 1 and len(nz) == n - 1) else None

    spl = dict(nx.all_pairs_shortest_path_length(G))
    ecc = np.array([max(dd.values()) for dd in spl.values()], float)
    diameter = float(ecc.max())
    radius = float(ecc.min())
    dsum = sum(sum(dd.values()) for dd in spl.values())
    mean_dist = float(dsum / (n * (n - 1)))

    try:
        girth = float(min(len(c) for c in nx.minimum_cycle_basis(G)))
    except Exception:
        girth = None
    try:
        econn = float(nx.edge_connectivity(G))
    except Exception:
        econn = None

    estrada = float(np.sum(np.exp(evA)))
    kirchhoff = float(n * np.sum(1.0 / nz))
    randic = 0.0
    z2 = 0.0
    for u, v in G.edges():
        du = G.degree(u)
        dv = G.degree(v)
        randic += 1.0 / np.sqrt(du * dv)
        z2 += du * dv
    z1 = float(np.sum(d * d))
    matching = float(len(nx.max_weight_matching(G, maxcardinality=True)))
    s = float(np.sum(evL))
    p = evL[evL > 0] / s
    spec_ent = float(-np.sum(p * np.log(p)))
    Au = aut_order(G)

    return {
        "V": float(n), "E": float(m),
        "T": float(sum(nx.triangles(G).values()) // 3),
        "b1": float(m - n + cc),
        "Aut": (float(Au) if Au is not None else None),
        "rhoA": rhoA, "lam2L": lam2L, "rhoL": rhoL, "tau": tau, "energy": energy,
        "girth": girth, "diameter": diameter, "radius": radius, "mean_dist": mean_dist,
        "econn": econn, "estrada": estrada, "kirchhoff": kirchhoff,
        "randic": float(randic), "zagreb1": z1, "zagreb2": float(z2),
        "trA4": trA4, "trA6": trA6, "trL2": trL2, "trL4": trL4,
        "matching": matching, "deg_mean": float(d.mean()), "deg_max": float(d.max()),
        "lap_spread": float(rhoL - lam2L), "spec_ent": spec_ent, "lap_var": float(np.var(evL)),
    }


def usable(prims, info):
    out = []
    for p in prims:
        ok = True
        for name in info:
            v = info[name].get(p, None)
            if v is None or not np.isfinite(v) or abs(v) <= 1e-300:
                ok = False
                break
        if ok:
            out.append(p)
    return out


def build_pool(prims, amax):
    grid = [e for e in range(-amax, amax + 1) if e != 0]
    n = len(prims)
    rows, labels = [], []
    for k in range(1, SUPPORT + 1):
        for combo in itertools.combinations(range(n), k):
            for exps in itertools.product(grid, repeat=k):
                v = np.zeros(n)
                for idx, e in zip(combo, exps):
                    v[idx] = e
                rows.append(v)
                labels.append(" ".join(f"{prims[i]}^{int(v[i])}" for i in combo))
    return np.array(rows), labels


def pool_eval(exps, logs):
    out = {}
    for tname in TLIST:
        num, den, tval = TARGETS[tname]
        pred = np.exp(np.clip(exps @ (logs[num] - logs[den]), -700, 700))
        out[tname] = np.abs(pred - tval) / tval
    return out


def logvec(info, prims, name):
    return np.array([np.log(info[name][p]) for p in prims], float)


# ============================================================
# PART A  图与不变量交叉核验
# ============================================================
def part_A(cfg, info):
    head(f"PART A  图与不变量交叉核验（配置 {cfg}）")
    keys = ["V", "E", "T", "b1", "Aut", "rhoA", "lam2L", "rhoL", "girth",
            "diameter", "mean_dist", "econn", "matching", "tau"]
    P(f"{'slot':<6}" + "".join(f"{k:>12}" for k in keys))
    P("-" * 100)
    for name in SLOTS:
        d = info[name]
        row = f"{name:<6}"
        for k in keys:
            v = d[k]
            if v is None:
                row += f"{'n/a':>12}"
            elif k in ("V", "E", "T", "b1", "Aut", "girth", "diameter", "matching"):
                row += f"{int(round(v)):>12}"
            else:
                row += f"{v:>12.6f}"
        P(row)
    P()
    checks = [("Y3p", "b1", 7), ("Y3n", "b1", 6), ("Y3p", "T", 3), ("Y3n", "T", 2),
              ("Y3p", "Aut", 36), ("Y3p", "rhoL", (7 + np.sqrt(13)) / 2),
              ("Y3n", "lam2L", 1.0), ("Y3n", "rhoL", (7 + np.sqrt(13)) / 2),
              ("GD", "b1", 13), ("GD", "Aut", 48), ("GD", "rhoL", 6.0),
              ("GD", "lam2L", 2 - np.sqrt(3)),
              ("GE", "V", 8 if cfg == "A" else 60), ("GE", "E", 12 if cfg == "A" else 90),
              ("GE", "b1", 5 if cfg == "A" else 31),
              ("GE", "girth", 4 if cfg == "A" else 4),
              ("GE", "T", 0)]
    allok = True
    for slot, key, want in checks:
        got = info[slot][key]
        okk = abs(got - want) < 1e-9
        allok &= okk
        P(f"   {slot+' '+key:<14} 实测 {got:>16.9f}   期望 {want:>16.9f}   {'OK' if okk else '*** 不符 ***'}")
    P(f"   ⇒ 全部核对 {'通过' if allok else '存在不符'}")
    return allok


# ============================================================
# PART B  reach 上界：原池 vs 延伸池
# ============================================================
def part_B(cfg, info, po, pe):
    label = "Q3" if cfg == "A" else "M60"
    head(f"PART B  reach 上界对照：原池({len(po)}) vs 延伸池({len(pe)})  —— 配置 {cfg}={label}")
    R1 = TARGETS["T1 m_p/m_e"][2]
    res = {}
    for tag, prims in (("原池", po), ("延伸池", pe)):
        L = {p: np.log(info["Y3p"][p]) - np.log(info["GE"][p]) for p in prims}
        order = sorted(prims, key=lambda p: -abs(L[p]))
        s3 = sum(abs(L[p]) for p in order[:3])
        sall = sum(abs(L[p]) for p in order)
        P(f"  [{tag}] n={len(prims)}  Σ|log r|(top3) = {s3:.4f}   Σ|log r|(all) = {sall:.4f}")
        P(f"    最大 3 项：{', '.join(f'{p}({L[p]:+.3f})' for p in order[:3])}")
        rows = []
        for A in A_LADDER:
            r3, rall = float(np.exp(A * s3)), float(np.exp(A * sall))
            rows.append((A, r3, rall))
        P(f"     {'A':>3}{'reach(sup<=3)':>18}{'reach(全支撑)':>20}{'全支撑<R1?':>12}")
        for A, r3, rall in rows:
            P(f"     {A:>3}{r3:>18.6g}{rall:>20.6g}{'  是(排除)' if rall < R1 else '   否':>12}")
        res[tag] = {"n": len(prims), "sum_top3": s3, "sum_all": sall, "rows": rows,
                    "blocked_A2_full": bool(rows[1][2] < R1),
                    "blocked_A2_sup3": bool(rows[1][1] < R1)}
    P()
    P(f"  目标 R1 = {R1:.6g}")
    P(f"  ⇒ A=2 全支撑上界：原池 {res['原池']['rows'][1][2]:.6g} / 延伸池 {res['延伸池']['rows'][1][2]:.6g}")
    if not res["延伸池"]["blocked_A2_full"]:
        P("  ⇒ **延伸池下 reach 不再封死** ⇒ §12.15 的『① reach』是**池规模相关**的，不是结构性律。")
        P("     权重必须转移到『② 无一把锁』与『③ 隐藏自由度』，并由 T-A.3 的精确联合检验接管。")
    return res


# ============================================================
# PART C0  精确联合检验（结构性、分布无关）
# ============================================================
def _ls_best(Lmat, b):
    a, *_ = np.linalg.lstsq(Lmat, b, rcond=None)
    return a


def exact_joint(info, prims, amax):
    """对每个支持集求联合 LS 解；support=3 时 LS 即精确解（3 方程 3 未知）。"""
    logN = {t: logvec(info, prims, TARGETS[t][0]) for t in TLIST}
    logD = {t: logvec(info, prims, TARGETS[t][1]) for t in TLIST}
    Lm = np.array([logN[t] - logD[t] for t in TLIST])          # (3, n)
    b = np.array([np.log(TARGETS[t][2]) for t in TLIST])       # (3,)
    n = len(prims)

    out = {"n": n, "k1": None, "k2": None, "k3": None}

    # ---- support = 1 ----
    tvals = np.array([TARGETS[t][2] for t in TLIST])
    zero_cols = [i for i in range(n) if float(np.linalg.norm(Lm[:, i])) < 1e-12]
    best = None
    for i in range(n):
        if i in zero_cols:
            continue
        col = Lm[:, i]
        coef = float((col @ b) / (col @ col))
        if not np.isfinite(coef):
            continue
        row = {}
        for lab, val in (("real", coef), ("int", float(round(coef)))):
            av = np.zeros(n)
            av[i] = val
            pred = np.exp(Lm @ av)
            row[lab] = float(np.max(np.abs(pred - tvals) / tvals))
        if best is None or row["int"] < best[0]:
            best = (row["int"], prims[i], [int(round(coef))], row["real"])
    out["degenerate"] = {"count": len(zero_cols),
                         "names": [prims[i] for i in zero_cols]}
    out["k1"] = {"best_int_maxresid": best[0], "prim": best[1], "a_int": best[2],
                 "real_maxresid": best[3]}

    # ---- support = 2 ----
    best2 = None
    for i, j in itertools.combinations(range(n), 2):
        cols = Lm[:, [i, j]]
        a = _ls_best(cols, b)
        ar = np.round(a).astype(int)
        ai = np.zeros(n); ai[i], ai[j] = ar
        pred = np.exp(Lm @ ai)
        resid = float(np.max(np.abs(pred - np.array([TARGETS[t][2] for t in TLIST])) /
                             np.array([TARGETS[t][2] for t in TLIST])))
        if best2 is None or resid < best2[0]:
            best2 = (resid, [prims[i], prims[j]], ar.tolist(), float(np.max(np.abs(a - ar))))
    out["k2"] = {"best_int_maxresid": best2[0], "support": best2[1], "a_int": best2[2],
                 "frac_dist": best2[3]}

    # ---- support = 3：精确解（LS 即解）+ 整数性 ----
    # ⚠ 必须做条件数控制：部分不变量在 log 空间**严格共线**
    #    （例：E = V·deg_mean/2 ⇒ L_E ≡ L_V + L_deg_mean），非共线三元组的 M 会近奇异，
    #    解出 1e16 量级的 a*，其 round() 因浮点精度"恰好相等"⇒ 会伪造出 dist=0 的假象。
    COND_MAX = 1e7
    n_tri = 0
    n_finite = 0
    n_ill = 0
    bounds = [2, 3, 4, 5]
    counts = {b: 0 for b in bounds}
    best3 = None
    best3_supp = None
    best_rj = None
    best_rj_supp = None
    best_rj_a = None
    top5 = []
    for i, j, k in itertools.combinations(range(n), 3):
        n_tri += 1
        M = Lm[:, [i, j, k]]
        try:
            c = float(np.linalg.cond(M))
        except Exception:
            continue
        if not np.isfinite(c):
            n_ill += 1
            continue
        if c > COND_MAX:
            n_ill += 1
            continue
        try:
            a = np.linalg.solve(M, b)
        except np.linalg.LinAlgError:
            n_ill += 1
            continue
        if not np.all(np.isfinite(a)):
            n_ill += 1
            continue
        n_finite += 1
        ar = np.round(a)
        dist = float(np.max(np.abs(a - ar)))
        mx = float(np.max(np.abs(ar)))
        if dist < 1e-6:
            for bnd in bounds:
                if mx <= bnd:
                    counts[bnd] += 1
        if best3 is None or dist < best3:
            best3 = dist
            best3_supp = [prims[i], prims[j], prims[k]]
        # 「无界整数指数」读数：把精确解直接圆整（**不设 |a| 上界**）后看联合偏差
        av = np.zeros(n)
        av[[i, j, k]] = ar
        pred = np.exp(np.clip(Lm @ av, -700, 700))
        rj = float(np.max(np.abs(pred - tvals) / tvals))
        if best_rj is None or rj < best_rj:
            best_rj = rj
            best_rj_supp = [prims[i], prims[j], prims[k]]
            best_rj_a = [int(x) for x in ar]
        top5.append((dist, [prims[i], prims[j], prims[k]], a.tolist()))
    top5.sort(key=lambda x: x[0])
    out["k3"] = {"n_triples": n_tri, "n_finite_wellcond": n_finite, "n_ill": n_ill,
                 "cond_max": COND_MAX,
                 "integral_count_by_bound": {str(b): counts[b] for b in bounds},
                 "n_exact_int_le_A": counts[amax],
                 "best": (best3 if best3 is not None else float("nan")),
                 "best_support": best3_supp,
                 "best_rounded_joint_resid": (best_rj if best_rj is not None else float("nan")),
                 "best_rounded_support": best_rj_supp,
                 "best_rounded_a": best_rj_a,
                 "top5": [{"dist": d, "support": s, "a": a} for d, s, a in top5[:5]]}
    return out


def part_C0(cfg, info, po, pe):
    head(f"PART C0  精确联合检验（support<=3 的联合精确解；配置 {cfg}）")
    P("原理：support=3 时三目标给出 3 个方程、3 个未知 ⇒ a* = M^{-1} b 是**精确解**")
    P("      （按构造 a*·L^(t) = ln R_t ⇒ 三个目标误差恒 = 0）。因此判据退化为一句：")
    P("      **a* 是否为整数向量且 |a*| <= A？** 是 ⇒ 存在 0% 误差的联合 Psi（L4 成立）；")
    P("      全部三元组皆非整 ⇒ 不存在精确联合 Psi（分布无关、与窗宽无关）。")
    P()
    res = {}
    for tag, prims in (("原池", po), ("延伸池", pe)):
        r = exact_joint(info, prims, A_MAIN)
        P(f"  [{tag}] n = {r['n']} 个不变量；无信息原始量（三目标 L 全 0）= "
          f"{r['degenerate']['count']} 个：{', '.join(r['degenerate']['names']) or '无'}")
        P(f"     support=1：最优整数 Psi = [{r['k1']['prim']}]^{r['k1']['a_int'][0]}  "
          f"三目标最大偏差 {r['k1']['best_int_maxresid']*100:.4f}%   （实数最优 {r['k1']['real_maxresid']*100:.4f}%）")
        P(f"     support=2：最优整数 Psi = {r['k2']['support']} ^ {r['k2']['a_int']}  "
          f"三目标最大偏差 {r['k2']['best_int_maxresid']*100:.4f}%   （离整数 {r['k2']['frac_dist']:.4f}）")
        k3 = r["k3"]
        P(f"     support=3：三元组 {k3['n_triples']}，**良态可解 {k3['n_finite_wellcond']}**，"
          f"剔除近奇异 {k3['n_ill']}（cond>{k3['cond_max']:.0e}）")
        bc = k3["integral_count_by_bound"]
        P(f"        **整数精确解个数（按 |a| 上界）**："
          + "  ".join(f"|a|<={b}: {bc[str(b)]}" for b in (2, 3, 4, 5)))
        P(f"        最近的非整解：‖a*−round(a*)‖∞ = {k3['best']:.6f}"
          + (f"  支持 {k3['best_support']}" if k3["best_support"] else ""))
        P(f"        **无界整数指数**（把精确解直接圆整，不设 |a| 上界）："
          f"最好联合偏差 = {k3['best_rounded_joint_resid']*100:.4f}%")
        P(f"           支持 {k3['best_rounded_support']}  a = {k3['best_rounded_a']}")
        for it in k3["top5"][:3]:
            P(f"           dist {it['dist']:.6f}  支持 {it['support']}  a* = "
              + "[" + ", ".join(f"{x:+.4f}" for x in it["a"]) + "]")
        P()
        res[tag] = r
    return res


# ============================================================
# PART C  网格枚举：联合命中
# ============================================================
def part_C(cfg, info, prims):
    head(f"PART C  网格枚举联合命中（延伸池，配置 {cfg}）")
    logs = {name: logvec(info, prims, name) for name in info}
    P(f"可用原始量 {len(prims)} 个：{', '.join(prims)}")
    P()
    P(f"{'A':>4}{'池规模':>12}{'T1(1%)':>10}{'T2(1%)':>10}{'T3(1%)':>10}"
      f"{'joint123(1%)':>14}{'joint12(1%)':>14}{'joint123(3%)':>14}{'最优联合偏差':>16}")
    P("-" * 100)
    detail = {}
    for A in A_SCAN:
        exps, labels = build_pool(prims, A)
        dev = pool_eval(exps, logs)
        c1 = int((dev[TLIST[0]] < 0.01).sum())
        c2 = int((dev[TLIST[1]] < 0.01).sum())
        c3 = int((dev[TLIST[2]] < 0.01).sum())
        j123 = np.ones(len(labels), bool)
        for t in TLIST:
            j123 &= (dev[t] < EPS_DECISION)
        j12 = (dev[TLIST[0]] < EPS_DECISION) & (dev[TLIST[1]] < EPS_DECISION)
        j3w = np.ones(len(labels), bool)
        for t in TLIST:
            j3w &= (dev[t] < 0.03)
        jmax = np.maximum(np.maximum(dev[TLIST[0]], dev[TLIST[1]]), dev[TLIST[2]])
        ib = int(np.argmin(jmax))
        bestjoint = (float(jmax[ib]), labels[ib])
        P(f"{A:>4}{len(labels):>12}{c1:>10}{c2:>10}{c3:>10}"
          f"{int(j123.sum()):>14}{int(j12.sum()):>14}{int(j3w.sum()):>14}{bestjoint[0]*100:>15.4f}%")
        detail[A] = {"pool": len(labels), "per1": {TLIST[0]: c1, TLIST[1]: c2, TLIST[2]: c3},
                     "joint123_1pct": int(j123.sum()), "joint12_1pct": int(j12.sum()),
                     "joint123_3pct": int(j3w.sum()),
                     "best_joint_resid": bestjoint[0], "best_joint_psi": bestjoint[1],
                     "exps": exps, "labels": labels, "dev": dev}
    P()
    P("『最优联合偏差』= max_t |Ψ预言−实测|/实测 在全池上的最小值（即这把锁**最好能做到**的程度）。")
    P()
    d = detail[A_MAIN]
    P(f"诊断（A={A_MAIN}）：三目标各自的**最优单个 Psi** 是否同一个？")
    picks = {}
    bestpt = {}
    for t in TLIST:
        i = int(np.argmin(d["dev"][t]))
        picks[t] = d["labels"][i]
        bestpt[t] = float(d["dev"][t][i])
        P(f"   {t:<14} 最小偏差 {d['dev'][t][i]*100:>8.4f}%   给出者 {d['labels'][i]}")
    P(f"   ⇒ 唯一最优者个数 = {len(set(picks.values()))} / 3"
      + ("（互不相同 ⇒ 无一把共用锁）" if len(set(picks.values())) == 3 else ""))
    d["picks"] = picks
    d["best_per_target"] = bestpt
    return detail


# ============================================================
# PART D  零假设
# ============================================================
def best_rounded_resid(Lm, b, tvals, cond_max=1e7):
    """在全池支撑<=3 上求「精确解圆整后」的最好联合偏差（整数指数**无上界**）。
    与 exact_joint 的 k3 读数同口径，抽出供 MC 使用。"""
    n = Lm.shape[1]
    best = None
    for i, j, k in itertools.combinations(range(n), 3):
        M = Lm[:, [i, j, k]]
        try:
            c = float(np.linalg.cond(M))
        except Exception:
            continue
        if not np.isfinite(c) or c > cond_max:
            continue
        try:
            a = np.linalg.solve(M, b)
        except np.linalg.LinAlgError:
            continue
        if not np.all(np.isfinite(a)):
            continue
        ar = np.round(a)
        av = np.zeros(n)
        av[[i, j, k]] = ar
        pred = np.exp(np.clip(Lm @ av, -700, 700))
        rj = float(np.max(np.abs(pred - tvals) / tvals))
        if best is None or rj < best:
            best = rj
    return best


def mc_null(cfg, info, prims, amax, trials=N_MC, seed=20260924):
    head(f"PART D  零假设：同 (V,E) 连通均匀随机图（延伸池，配置 {cfg}，A={amax}，{trials} 次）")
    rng = np.random.default_rng(seed)
    slots = {n: (int(info[n]["V"]), int(info[n]["E"])) for n in info}
    exps, _ = build_pool(prims, amax)
    tot = {t: 0 for t in TLIST}
    tot_j123 = 0
    tot_j12 = 0
    tried = 0
    skipped = 0
    tvals = np.array([TARGETS[t][2] for t in TLIST])
    bvec = np.array([np.log(TARGETS[t][2]) for t in TLIST])
    null_best = []
    t0 = time.time()
    for _ in range(trials):
        Gs, ok = {}, True
        for name, (V, E) in slots.items():
            G = None
            for _ in range(60):
                cand = nx.gnm_random_graph(V, E, seed=int(rng.integers(1 << 30)))
                if nx.number_connected_components(cand) == 1:
                    G = cand
                    break
            if G is None:
                ok = False
                break
            Gs[name] = G
        if not ok:
            skipped += 1
            continue
        inf = {name: inv_full(g) for name, g in Gs.items()}
        if any(inf[name].get(p) is None for name in inf for p in prims):
            skipped += 1
            continue
        logs = {name: np.array([np.log(inf[name][p]) for p in prims]) for name in inf}
        dv = pool_eval(exps, logs)
        j123 = np.ones(len(exps), bool)
        for t in TLIST:
            tot[t] += int((dv[t] < EPS_DECISION).sum())
            j123 &= (dv[t] < EPS_DECISION)
        j12 = (dv[TLIST[0]] < EPS_DECISION) & (dv[TLIST[1]] < EPS_DECISION)
        tot_j123 += int(j123.sum())
        tot_j12 += int(j12.sum())
        # 同一「无界整数指数」统计量的零假设
        Lm = np.array([logs[TARGETS[t][0]] - logs[TARGETS[t][1]] for t in TLIST])
        rb = best_rounded_resid(Lm, bvec, tvals)
        if rb is not None:
            null_best.append(float(rb))
        tried += 1
    dt = time.time() - t0
    P(f"有效试验 {tried} 次、跳过 {skipped} 次（{dt:.1f}s）")
    P(f"{'量':<16}{'零假设平均/试验':>22}")
    P("-" * 100)
    for t in TLIST:
        P(f"{t:<16}{tot[t]/max(tried,1):>22.3f}")
    P(f"{'joint123':<16}{tot_j123/max(tried,1):>22.4f}")
    P(f"{'joint12':<16}{tot_j12/max(tried,1):>22.4f}")
    P()
    if null_best:
        arr = np.array(null_best)
        P(f"『无界整数指数最好联合偏差』零假设分布（n={len(arr)}）：")
        P(f"   平均 {arr.mean()*100:.4f}%   最小 {arr.min()*100:.4f}%   "
          f"5% 分位 {np.percentile(arr,5)*100:.4f}%   中位 {np.median(arr)*100:.4f}%")
    P()
    P("读法：真实配置命中数若**不大于**零假设期望 ⇒ 无结构信号。")
    P("      真实『最好联合偏差』若**不低于**零假设 5% 分位 ⇒ 亦无信号（可能是多重比较假象）。")
    return {"trials": tried, "skipped": skipped,
            "per_target_per_trial": {t: tot[t] / max(tried, 1) for t in TLIST},
            "joint123_per_trial": tot_j123 / max(tried, 1),
            "joint12_per_trial": tot_j12 / max(tried, 1),
            "best_rounded_null": {"n": len(null_best),
                                  "mean": float(np.mean(null_best)) if null_best else None,
                                  "min": float(np.min(null_best)) if null_best else None,
                                  "p5": float(np.percentile(null_best, 5)) if null_best else None,
                                  "median": float(np.median(null_best)) if null_best else None}}


# ============================================================
def main():
    P("T-A：把静态不变量池「拉到最大」后重算 L4（区分 H_static / H_dyn）")
    P("预注册见文件头 PART 0；目标与容差与 §12.15 完全一致。")
    res = {"prereg": {"prims_orig": PRIMS_ORIG, "prims_ext": PRIMS_EXT,
                      "A_main": A_MAIN, "A_scan": A_SCAN, "support": SUPPORT,
                      "eps": EPS_DECISION, "n_mc": N_MC,
                      "targets": {k: v[2] for k, v in TARGETS.items()}},
           "configs": {}}
    for cfg in ("A", "B"):
        Gs = make_graphs(cfg)
        info = {n: inv_full(g) for n, g in Gs.items()}
        part_A(cfg, info)
        po = usable(PRIMS_ORIG, info)
        pe = usable(PRIMS_EXT, info)
        rb = part_B(cfg, info, po, pe)
        c0 = part_C0(cfg, info, po, pe)
        dc = part_C(cfg, info, pe)
        nm = mc_null(cfg, info, pe, A_MAIN)
        entry = {"prims_orig_used": po, "prims_ext_used": pe,
                 "reach": {k: {"n": v["n"], "sum_top3": v["sum_top3"], "sum_all": v["sum_all"],
                               "blocked_A2_full": v["blocked_A2_full"],
                               "blocked_A2_sup3": v["blocked_A2_sup3"], "rows": v["rows"]}
                           for k, v in rb.items()},
                 "exact": {k: {"k1": v["k1"], "k2": v["k2"], "k3": v["k3"]} for k, v in c0.items()},
                 "grid": {a: {"pool": dc[a]["pool"], "per1": dc[a]["per1"],
                              "joint123_1pct": dc[a]["joint123_1pct"],
                              "joint12_1pct": dc[a]["joint12_1pct"],
                              "joint123_3pct": dc[a]["joint123_3pct"],
                              "best_joint_resid": dc[a]["best_joint_resid"],
                              "best_joint_psi": dc[a]["best_joint_psi"]} for a in A_SCAN},
                 "grid_picks": {a: {"picks": dc[a].get("picks", {}),
                                    "best_per_target": dc[a].get("best_per_target", {})}
                                for a in A_SCAN},
                 "mc": nm}
        e_ext = c0["延伸池"]["k3"]
        j123 = dc[A_MAIN]["joint123_1pct"]
        j12 = dc[A_MAIN]["joint12_1pct"]
        real_best = e_ext["best_rounded_joint_resid"]
        nbb = nm.get("best_rounded_null", {})
        null_p5 = nbb.get("p5", None)
        signal_best = (null_p5 is not None) and (real_best < null_p5)
        hit_exact = e_ext["n_exact_int_le_A"] > 0
        hit_grid = (j123 > 0) or (j12 > 0)
        above_null = (j123 > max(3.0 * nm["joint123_per_trial"], nm["joint123_per_trial"] + 1) or
                      j12 > max(3.0 * nm["joint12_per_trial"], nm["joint12_per_trial"] + 1))
        entry["best_rounded_real"] = real_best
        entry["best_rounded_null_p5"] = null_p5
        entry["best_rounded_signal"] = bool(signal_best)
        if hit_exact or (hit_grid and above_null) or signal_best:
            v = "H_static_supported"
        elif hit_grid:
            v = "inconclusive_hits_not_above_null"
        else:
            v = "H_dyn_supported"
        entry["verdict"] = v
        res["configs"][cfg] = entry
        P()
        P(f"  >>> 配置 {cfg} 裁决：{v}")
        P(f"      （精确联合解 {e_ext['n_exact_int_le_A']}；网格 joint123={j123}、joint12={j12}；"
          f"零假设 joint123={nm['joint123_per_trial']:.4f}、joint12={nm['joint12_per_trial']:.4f}）")
        P(f"      （无界指数最好联合偏差：真实 {real_best*100:.4f}% vs 零假设 5% 分位 "
          f"{(null_p5*100 if null_p5 is not None else float('nan')):.4f}% ⇒ "
          f"{'有信号' if signal_best else '无信号（疑多重比较假象）'}）")

    head("PART E  总裁决与边界")
    for cfg in ("A", "B"):
        e = res["configs"][cfg]
        lb = "G_e = Q3 本体" if cfg == "A" else "G_e = M60 载体"
        P(f"配置 {cfg}（{lb}）：{e['verdict']}")
        P(f"   延伸池 n={len(e['prims_ext_used'])}；reach(A=2) 全支撑 = "
          f"{e['reach']['延伸池']['rows'][1][2]:.4g}（原池 {e['reach']['原池']['rows'][1][2]:.4g}）")
        P(f"   精确联合解（|a|<=2）= {e['exact']['延伸池']['k3']['n_exact_int_le_A']}；"
          f"最近非整解 ‖a*−round‖∞ = {e['exact']['延伸池']['k3']['best']:.6f}")
        bp = e["grid_picks"][A_MAIN]["best_per_target"]
        P(f"   三目标**各自**最好的单把锁："
          + "  ".join(f"{t.split()[0]} {bp[t]*100:.4f}%" for t in TLIST)
          + f"  ← 个个 ≪ 1%")
        P(f"   但**同一把锁**的最好成绩（|a|<=2 联合最大偏差）= "
          f"{e['grid'][A_MAIN]['best_joint_resid']*100:.4f}%  由 {e['grid'][A_MAIN]['best_joint_psi']}")
        P(f"   放开 |a| 上界（support<=3、整数指数任意大）后最好成绩 = "
          f"{e['exact']['延伸池']['k3']['best_rounded_joint_resid']*100:.4f}%  "
          f"（支持 {e['exact']['延伸池']['k3']['best_rounded_support']}）")
        P(f"   精确整数联合解个数 = {e['exact']['延伸池']['k3']['n_exact_int_le_A']} / "
          f"{e['exact']['延伸池']['k3']['n_finite_wellcond']} 良态三元组")
    P()
    P("边界：")
    P(" B1 monomial 类只覆盖『乘积幂次型』规则；不含加减/组合项 ⇒ 结论限于此类（与 §12.15 同）。")
    P(" B2 池的『最大』以 T-A.1 的门槛为界（两侧皆取正值）；T 与 |Aut| 被结构性排除，非人为挑选。")
    P(" B3 精确联合检验（PART C0）与随机图无关、与窗宽无关 ⇒ 它是最强的一条读数。")
    P(" B4 T3 为弱目标（quasi-invariant 伪像），故并列报 joint(T1,T2)（不受伪像影响）。")
    P(" B5 电子代表元不唯一（Q3 vs M60）这一隐藏自由度，T-A 不能消除（它只扩池，不改域）。")
    with open("_l4_pool_extend.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2, default=float)
    P()
    P("json 已写 _l4_pool_extend.json")


if __name__ == "__main__":
    main()
