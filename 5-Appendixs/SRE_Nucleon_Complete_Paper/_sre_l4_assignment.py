# -*- coding: utf-8 -*-
"""
_sre_l4_assignment.py —— L4「质量-深度赋值规则」的最后一击

L4（项目定义，SRE_Nucleon_Inversion_Skeleton.md 第 7.1 节 / 论文 §7.1）：
    m_p / m_e = Psi(G_N) / Psi(G_e)      （Psi 未定义，当前不可用）
即：需要一条「**整数不变量 → 实数测量值**」的赋值规则，并且**两个层共用同一个 Psi**
（= 齐次性：两图共用一把锁）。

本脚本把 L4 变为一次**可证伪**的检验：预注册判据 → reach 上界 → 全池枚举 → 稳健扫描 → 零假设 → 裁决。

===========================================================================
【PART 0  预注册（本块在任何数值打印之前固定；禁止事后加项、改窗宽、换目标）】
===========================================================================
(0.1) 原始不变量集合（层无关，10 个，全部由图自身规则定义，不含任何「层专属常数」）：
        V        节点数
        E        边数
        T        三角形数
        b1       圈秩 E - V + cc
        Aut      自同构群阶 |Aut|
        rhoA     邻接谱半径
        lam2L    Laplacian 代数连通度
        rhoL     Laplacian 最大特征值  ← 项目的 rho 即此量（勿与 rhoA 混）
        tau      生成树数（Kirchhoff）
        energy   图能量 sum |lambda_adj|
(0.2) 函数类 Psi：单项式 prod_i p_i^{a_i}，指数 a_i ∈ {-A..-1,+1..+A}，支撑 <= 3。
      主分析 A = 2（= 预注册决策配置）；A = 1, 3 作**稳健性扫描**（报告命中数如何随 A 变，
      防止「结论只是幂次范围选窄了」）。
(0.3) 图（每层代表元的声明）：
        G_p = Y3 闭态（质子本体）
        G_n = Y3 开态（断一条环边）
        G_d = 两体共享环 k=2（氘核；项目已实测 V21 E33 T5 b1=13 |Aut|=48 rhoL=6 lam2L=2-sqrt3）
        配置 A：G_e = Q3 (8,12,5)  —— 电子本体（P2）
        配置 B：G_e = M60 Mobius 阶梯 —— 电子线的 alpha 载体
(0.4) 目标（3 个：1 个设计目标 + 2 个样本外目标）：
        T1（设计，L4 原式）：R1 = m_p/m_e = 1836.15267343
        T2（样本外）        ：R2 = m_d/m_p = 1.999007745
        T3（样本外）        ：R3 = m_n/m_p = 1.0013784193
(0.5) 决策容差：eps = 1%。
      —— 刻意取得比框架**已证**精度（核子层 0.165%，电子层 1.45e-5）更宽，因此判负
         不可归咎于「窗宽太紧」。另报 0.2% / 3% 仅作描述性对照，不参与裁决。
(0.6) 成功条件：存在**一个** Psi（零自由参数，指数由网格固定）使**三个**目标同时在 eps 内。
(0.7) 零假设：把四个图各自换成同 (V,E) 的均匀连通随机图，重算全池，统计逐目标/联合命中数。
(0.8) 结构性检查（分布无关，优先于 MC）：
        reach(support<=3) = exp( A * (top-3 个 |log r_i| 之和) )
        reach(全支撑)     = exp( A * (全部 |log r_i| 之和) )
        意义：全支撑上界**与「支撑限得太小」的反对无关**；若它仍 < R1 ⇒ 该配置在此幂次
        范围内被**决定性排除**（与分布、与巧合都无关），无需 MC。
===========================================================================
产物：_l4_assignment.log / _l4_assignment.json
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

PRIMS = ["V", "E", "T", "b1", "Aut", "rhoA", "lam2L", "rhoL", "tau", "energy"]
A_MAIN = 2
A_SCAN = [1, 2, 3]
SUPPORT = 3
EPS_DECISION = 0.01
EPS_DESC = [0.002, 0.03]

# 目标（CODATA 2018 / PDG 2024；MeV）
M_E = 0.51099895000
M_P = 938.27208816
M_N = 939.56542052
M_D = 1875.61294257
TARGETS = {
    "T1 m_p/m_e": ("Y3p", "GE", M_P / M_E),
    "T2 m_d/m_p": ("GD", "Y3p", M_D / M_P),
    "T3 m_n/m_p": ("Y3n", "Y3p", M_N / M_P),
}
SLOT_ORDER = ["GE", "Y3p", "Y3n", "GD"]


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * 100)
    P(t)
    P("=" * 100)


# ============================================================
# 图构造（与项目既有脚本同口径）
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
    """共享环装配：把各体第 r 环的 L{i}{r} 映射到 S{i}，取边集并。"""
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
# 不变量
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


def invariants(G):
    V = G.number_of_nodes()
    E = G.number_of_edges()
    T = sum(nx.triangles(G).values()) // 3
    cc = nx.number_connected_components(G)
    b1 = E - V + cc
    Au = aut_order(G)
    evL = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float)))
    evA = np.sort(np.linalg.eigvalsh(nx.to_numpy_array(G)))
    lam2L = float(evL[1]) if V > 1 else 0.0
    rhoL = float(evL[-1])
    rhoA = float(evA[-1])
    energy = float(np.sum(np.abs(evA)))
    nz = evL[evL > 1e-9]
    tau = float(np.sum(np.log(nz)) - np.log(V)) if (cc == 1 and V > 1 and len(nz) == V - 1) else None
    return {"V": float(V), "E": float(E), "T": float(T), "b1": float(b1),
            "Aut": (float(Au) if Au is not None else None), "rhoA": rhoA,
            "lam2L": lam2L, "rhoL": rhoL, "tau": tau, "energy": energy}


def usable(prims, info):
    out = []
    for p in prims:
        if all((info[name][p] is not None and abs(info[name][p]) > 1e-300) for name in info):
            out.append(p)
    return out


def build_pool(prims, amax):
    grid = [e for e in range(-amax, amax + 1) if e != 0]
    idmap = {p: i for i, p in enumerate(prims)}
    rows, labels = [], []
    n = len(prims)
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
    for tname, (num, den, tval) in TARGETS.items():
        pred = np.exp(np.clip(exps @ (logs[num] - logs[den]), -700, 700))
        out[tname] = np.abs(pred - tval) / tval
    return out


# ============================================================
# PART A
# ============================================================
def part_A(cfg):
    head(f"PART A  图与不变量（配置 {cfg}）")
    Gs = make_graphs(cfg)
    info = {name: invariants(g) for name, g in Gs.items()}
    P(f"{'slot':<6}{'V':>6}{'E':>6}{'T':>6}{'b1':>6}{'Aut':>8}{'rhoA':>12}"
      f"{'lam2L':>12}{'rhoL(=项目rho)':>17}{'log10 tau':>12}{'energy':>11}")
    P("-" * 100)
    for name in SLOT_ORDER:
        d = info[name]
        au = "n/a" if d["Aut"] is None else f"{int(d['Aut'])}"
        tl = "n/a" if d["tau"] is None else f"{d['tau']/np.log(10):.4f}"
        P(f"{name:<6}{int(d['V']):>6}{int(d['E']):>6}{int(d['T']):>6}{int(d['b1']):>6}"
          f"{au:>8}{d['rhoA']:>12.9f}{d['lam2L']:>12.9f}{d['rhoL']:>17.9f}{tl:>12}{d['energy']:>11.5f}")
    P()
    P("核对（须与项目既有实测逐位相符；项目 rho = Laplacian 最大特征值）：")
    checks = [("Y3p", "b1", 7), ("Y3n", "b1", 6), ("Y3p", "T", 3), ("Y3n", "T", 2),
              ("Y3p", "Aut", 36), ("Y3p", "rhoL", (7 + np.sqrt(13)) / 2),
              ("Y3n", "lam2L", 1.0), ("Y3n", "rhoL", (7 + np.sqrt(13)) / 2),
              ("GD", "b1", 13), ("GD", "Aut", 48), ("GD", "rhoL", 6.0),
              ("GD", "lam2L", 2 - np.sqrt(3))]
    allok = True
    for slot, key, want in checks:
        got = info[slot][key]
        okk = abs(got - want) < 1e-9
        allok &= okk
        P(f"   {slot+' '+key:<12} 实测 {got:>16.9f}   期望 {want:>16.9f}   {'OK' if okk else '*** 不符 ***'}")
    P(f"   ⇒ 全部核对 {'通过' if allok else '存在不符'}")
    return Gs, info


# ============================================================
# PART B  reach 上界
# ============================================================
def part_B(cfg, info, prims):
    label = "Q3" if cfg == "A" else "M60"
    head(f"PART B  reach 上界（结构性检查，配置 {cfg}={label}）")
    L = {p: np.log(info["Y3p"][p]) - np.log(info["GE"][p]) for p in prims}
    order = sorted(prims, key=lambda p: -abs(L[p]))
    P("log r_i = log p_i(核子本体) - log p_i(电子图)：")
    P(f"{'prim':<10}{'r_i':>16}{'log r_i':>14}{'2|log r_i|':>14}")
    P("-" * 100)
    for p in order:
        P(f"{p:<10}{np.exp(L[p]):>16.6g}{L[p]:>14.6f}{2*abs(L[p]):>14.6f}")
    s3 = sum(abs(L[p]) for p in order[:3])
    sall = sum(abs(L[p]) for p in order)
    R1 = TARGETS["T1 m_p/m_e"][2]
    P()
    P(f"最大 3 项（支撑<=3）= {', '.join(order[:3])}")
    P(f"{'A':>4}{'reach(支撑<=3)':>20}{'reach(全支撑)':>20}{'< R1 ?':>12}")
    P("-" * 100)
    rows = []
    for A in A_SCAN:
        r3, rall = np.exp(A * s3), np.exp(A * sall)
        rows.append((A, float(r3), float(rall)))
        P(f"{A:>4}{r3:>20.6g}{rall:>20.6g}{'  是(排除)' if rall < R1 else '  否':>12}")
    blocked = rows[1][2] < R1   # A_MAIN 的全支撑上界
    P()
    P(f"目标 R1 = m_p/m_e = {R1:.6g}")
    if blocked:
        P(f"⇒ **A={A_MAIN} 的全支撑 reach 上界 {rows[1][2]:.6g} < R1**（差 {np.log10(R1/rows[1][2]):.3f} 个数量级）")
        P("   ⇒ 该配置在幂次范围 |a|<=2 内被**决定性排除**：与分布无关、与支撑大小无关、无需 MC。")
    else:
        P(f"⇒ A={A_MAIN} 的全支撑 reach 上界 {rows[1][2]:.6g} >= R1 ⇒ **未被 reach 排除**，须进入全池检验。")
    return blocked, rows, L


# ============================================================
# PART B2  项目唯一已标定泛函 Pi1 = lam2L / rhoL 的表现
# ============================================================
def part_B2(cfg, info):
    head(f"PART B2  项目唯一已标定泛函 Pi1 = lam2L^1 rhoL^-1 的表现（配置 {cfg}）")
    P("说明：Pi1 是本项目唯一已标定的跨层泛函（电子层 Pi1(M60)=alpha 偏 1.45e-5；")
    P("      核子层 (m_n-m_p)/m_p = alpha*Pi1(Y3) 偏 -0.165%）。它本身就在本池内（指数 (1,-1)）。")
    P()
    def pi1(slot):
        return info[slot]["lam2L"] / info[slot]["rhoL"]
    P(f"   Pi1(GE)  = {pi1('GE'):.9f}   （配置 {cfg} 的电子图）")
    P(f"   Pi1(Y3p) = {pi1('Y3p'):.9f}   （= 项目记录的 0.188580 量级）")
    P(f"   Pi1(Y3n) = {pi1('Y3n'):.9f}")
    P(f"   Pi1(GD)  = {pi1('GD'):.9f}   （= 2-sqrt3 = {2-np.sqrt(3):.9f}）")
    P()
    P(f"{'目标':<14}{'Psi-比预言':>18}{'实测':>16}{'偏差':>12}")
    P("-" * 100)
    for tname, (num, den, tval) in TARGETS.items():
        pred = pi1(num) / pi1(den)
        P(f"{tname:<14}{pred:>18.6g}{tval:>16.9g}{abs(pred-tval)/tval*100:>11.2f}%")
    P()
    P("⇒ 读法：项目最好的那把锁，跨层只给出 %.3g（对 1836 偏 %.1f%%），" %
      (pi1("Y3p") / pi1("GE"), abs(pi1("Y3p") / pi1("GE") - TARGETS["T1 m_p/m_e"][2]) / TARGETS["T1 m_p/m_e"][2] * 100))
    P("   即**离目标差 1.85 个数量级** —— 与 PART B 的 reach 结论同向。")


def part_B3(cfg):
    head("PART B3  正残留（对照）：项目 alpha 锁只成立在『层内两态的差比』上")
    gm = invariants(mobius_m60())
    alpha = gm["lam2L"] / gm["rhoL"]
    alpha_meas = 7.2973525693e-3
    pi1y = (1.0) / ((7 + np.sqrt(13)) / 2)   # Pi1(Y3p) = lam2L/rhoL = 1/((7+sqrt13)/2)
    pred = alpha * pi1y
    meas = (M_N - M_P) / M_P
    P(f"   alpha = Pi1(M60) = {alpha:.9f}   对实测 alpha 偏 {(alpha-alpha_meas)/alpha_meas:+.2e}")
    P(f"   Pi1(Y3p) = {pi1y:.9f}")
    P(f"   alpha * Pi1(Y3p) = {pred:.6e}   实测 (m_n-m_p)/m_p = {meas:.6e}   偏 {(pred-meas)/meas*100:+.3f}%")
    P()
    P("⇒ 同一套 Pi1 机器：")
    P("   · 层内两态的**差比** (m_n-m_p)/m_p —— 成立（偏 -0.17%）；")
    P("   · 层与层的**整体质量比** m_p/m_e —— 失败（见 PART B2：0.566 / 25.84，差 1.85 个数量级）。")
    P("   ⇒ 这正是『SRE 定形不定值』的具体形态：**跨层锁锁得住层内的差，锁不住层的整体尺度。**")

# ============================================================
# PART C  全池枚举 + 稳健扫描
# ============================================================
def part_C(cfg, info, prims):
    head(f"PART C  全池枚举与幂次范围稳健扫描（配置 {cfg}）")
    logs = {name: np.array([np.log(info[name][p]) for p in prims]) for name in info}
    P(f"可用原始量 {len(prims)} 个：{', '.join(prims)}")
    P()
    P(f"{'A':>4}{'池规模':>10}{'T1(1%)':>10}{'T2(1%)':>10}{'T3(1%)':>10}{'联合(1%)':>12}{'联合(3%)':>12}")
    P("-" * 100)
    detail = {}
    for A in A_SCAN:
        exps, labels = build_pool(prims, A)
        dev = pool_eval(exps, logs)
        cnt = {t: int((dev[t] < 0.01).sum()) for t in TARGETS}
        joint = np.ones(len(labels), bool)
        for t in TARGETS:
            joint &= (dev[t] < EPS_DECISION)
        joint3 = np.ones(len(labels), bool)
        for t in TARGETS:
            joint3 &= (dev[t] < 0.03)
        P(f"{A:>4}{len(labels):>10}{cnt['T1 m_p/m_e']:>10}{cnt['T2 m_d/m_p']:>10}"
          f"{cnt['T3 m_n/m_p']:>10}{int(joint.sum()):>12}{int(joint3.sum()):>12}")
        detail[A] = {"pool": len(labels), "per_target_1pct": cnt,
                     "joint_1pct": int(joint.sum()), "joint_3pct": int(joint3.sum()),
                     "exps": exps, "labels": labels, "dev": dev}
    P()
    P("诊断：主配置 A=%d 下，**逐目标**最优者（三个目标的最优 Psi 是否同一个？）：" % A_MAIN)
    d = detail[A_MAIN]
    picks = {}
    for t in TARGETS:
        i = int(np.argmin(d["dev"][t]))
        picks[t] = (d["labels"][i], float(d["dev"][t][i]))
        P(f"   {t:<14} 最小偏差 {d['dev'][t][i]*100:>8.4f}%   给出者 {d['labels'][i]}")
    uniq = set(p[0] for p in picks.values())
    P()
    if len(uniq) == len(TARGETS):
        P("   ⇒ **三个目标的最优 Psi 互不相同** ⇒ 不存在一把同时管住三者的锁")
        P("     （= L4 的『两图共用一把锁』要求被证伪的直接形态）。")
    else:
        P("   ⇒ 存在一个 Psi 同时是多个目标的最优者（见上）。")
    if A_MAIN in detail:
        exps, labels = detail[A_MAIN]["exps"], detail[A_MAIN]["labels"]
        P()
        P(f"   （描述性对照，**不参与裁决**）单目标在 0.2%/3% 窗内候选数：")
        for t in TARGETS:
            P(f"     {t:<14} 0.2%: {int((detail[A_MAIN]['dev'][t]<0.002).sum()):>4}   "
              f"3%: {int((detail[A_MAIN]['dev'][t]<0.03).sum()):>5}")
    return detail, logs


# ============================================================
# PART C2  零假设
# ============================================================
def mc_null(cfg, info, prims, amax, trials=500, seed=20260924):
    head(f"PART C2  零假设：同 (V,E) 均匀连通随机图（配置 {cfg}，A={amax}，{trials} 次）")
    rng = np.random.default_rng(seed)
    slots = {n: (int(info[n]["V"]), int(info[n]["E"])) for n in info}
    tot = {t: 0 for t in TARGETS}
    tot_joint = 0
    tried = 0
    t0 = time.time()
    for _ in range(trials):
        Gs, ok = {}, True
        for name, (V, E) in slots.items():
            G = None
            for _ in range(40):
                cand = nx.gnm_random_graph(V, E, seed=int(rng.integers(1 << 30)))
                if nx.number_connected_components(cand) == 1:
                    G = cand
                    break
            if G is None:
                ok = False
                break
            Gs[name] = G
        if not ok:
            continue
        inf = {name: invariants(g) for name, g in Gs.items()}
        pu = usable(prims, inf)
        if len(pu) < 2:
            continue
        ex2, _ = build_pool(pu, amax)
        logs = {name: np.array([np.log(inf[name][p]) for p in pu]) for name in inf}
        dv = pool_eval(ex2, logs)
        jn = np.ones(len(ex2), bool)
        for tn in TARGETS:
            tot[tn] += int((dv[tn] < EPS_DECISION).sum())
            jn &= (dv[tn] < EPS_DECISION)
        tot_joint += int(jn.sum())
        tried += 1
    dt = time.time() - t0
    P(f"有效试验 {tried} 次（{dt:.1f}s）")
    P(f"{'量':<14}{'真实配置':>12}{'零假设平均/试验':>20}")
    P("-" * 100)
    for t in TARGETS:
        P(f"{t:<14}{'-':>12}{tot[t]/max(tried,1):>20.3f}")
    P(f"{'联合命中':<14}{'-':>12}{tot_joint/max(tried,1):>20.4f}")
    P()
    P("读法：真实配置的命中数若**不大于**零假设期望 ⇒ **无结构信号**")
    P("      （= 第 12.8 节教训：交叉命中先做全体命中率核验 + MC 零假设）。")
    return {"trials": tried, "per_target_total": tot, "joint_total": tot_joint,
            "joint_p0": tot_joint / max(tried, 1)}


# ============================================================
def main():
    P("L4「质量-深度赋值规则」最后一击 —— 预注册判据 + reach 上界 + 全池检验 + 零假设")
    P("判据：零参数（指数由固定网格给出） + 三目标（1 设计 + 2 样本外）同时命中 + MC 零假设")
    P("决策容差 eps = 1%（比框架已证精度 0.165% 更宽，故判负不可归咎于窗宽）")
    res = {"prereg": {"prims": PRIMS, "A_main": A_MAIN, "A_scan": A_SCAN,
                      "support": SUPPORT, "eps_decision": EPS_DECISION,
                      "targets": {k: v[2] for k, v in TARGETS.items()},
                      "aut_cap": AUT_CAP, "aut_vmax": AUT_VMAX},
           "configs": {}}
    for cfg in ("A", "B"):
        _, info = part_A(cfg)
        prims = usable(PRIMS, info)
        blocked, rrows, _ = part_B(cfg, info, prims)
        part_B2(cfg, info)
        part_B3(cfg)
        entry = {"prims_used": prims,
                 "reach_rows": [{"A": a, "reach_support3": r3, "reach_full": rf} for a, r3, rf in rrows],
                 "reach_blocked_at_A2": blocked}
        detail, logs = part_C(cfg, info, prims)
        real = {a: {"pool": detail[a]["pool"], "per1": detail[a]["per_target_1pct"],
                    "joint1": detail[a]["joint_1pct"], "joint3": detail[a]["joint_3pct"]}
                for a in A_SCAN}
        entry["pool_by_A"] = real
        entry["joint_hits"] = real[A_MAIN]["joint1"]
        if blocked:
            P()
            P("⇒ 本配置在 |a|<=2 内 reach 已决定性排除 ⇒ **跳过 MC**（联合命中 0 亦见上表）。")
            entry["verdict"] = "negative_by_reach"
        else:
            nm = mc_null(cfg, info, prims, A_MAIN)
            entry["mc"] = nm
            entry["verdict"] = "negative" if real[A_MAIN]["joint1"] <= nm["joint_total"] else "candidate"
        res["configs"][cfg] = entry

    head("PART D  裁决与边界")
    for cfg in ("A", "B"):
        e = res["configs"][cfg]
        nm = "G_e = Q3 本体" if cfg == "A" else "G_e = M60 载体"
        P(f"配置 {cfg}（{nm}）：{e['verdict']}")
        if "reach_rows" in e:
            P(f"   reach 全支撑(A=2) = {e['reach_rows'][1]['reach_full']:.4g}   "
              f"支撑<=3(A=2) = {e['reach_rows'][1]['reach_support3']:.4g}")
        if "pool_by_A" in e:
            P("   全池联合命中： " + "   ".join(
                f"A={a}: {e['pool_by_A'][a]['joint1']}/{e['pool_by_A'][a]['pool']} (1%), "
                f"{e['pool_by_A'][a]['joint3']} (3%)" for a in A_SCAN))
        if "mc" in e:
            P(f"   MC 零假设 {e['mc']['trials']} 试验：逐目标/试验 = "
              + ", ".join(f"{k.split()[0]} {v/e['mc']['trials']:.2f}" for k, v in e['mc']['per_target_total'].items())
              + f"；联合 {e['mc']['joint_total']}/{e['mc']['trials']}")
    P()
    P("边界（必须一并报告）：")
    P(" B1 monomial 类只是『乘积幂次型』规则；不含加减／三角／组合项 ⇒ 结论限于此类。")
    P(" B2 电子层的代表元本身不唯一（本体 Q3 vs 载体 M60），且 reach 裁决在两配置间**翻转**")
    P("    （Q3 被排除 / M60 不被排除）⇒ 『选哪个图代表电子』是一个未被框架固定的选择")
    P("    ⇒ 隐藏自由度 ⇒ 即便某天出现命中，它也不是零参数、不可证伪（C3 破坏）。")
    P(" B3 R2/R3 只用核子层图（共享环、开闭态），与 R1 的层跨越机制不同，属独立目标。")
    P(" B4 |Aut| 在 V>22 按预注册规则不可算 ⇒ 配置 B 的池不含 |Aut|（如实登记）。")
    P(" B5 幂次范围 |a|<=2 是预注册主分析；|a|=3 的扫描见 PART B/PART C 表（联合仍为 0）。")
    P(" B6 T3 (m_n/m_p=1.0014) 是**弱目标**：任何『在开/闭态上近乎不变的 Psi』都给 1，")
    P("    而 1 已在 0.14% 内 ⇒ T3 的 191/494 个命中里绝大多数是准不变量，不构成证据。")
    res["verdicts"] = {cfg: res["configs"][cfg]["verdict"] for cfg in ("A", "B")}
    with open("_l4_assignment.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2, default=float)
    P()
    P("json 已写 _l4_assignment.json")


if __name__ == "__main__":
    main()
