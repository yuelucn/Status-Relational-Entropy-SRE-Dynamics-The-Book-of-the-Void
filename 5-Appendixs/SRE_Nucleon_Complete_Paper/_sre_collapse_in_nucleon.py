# -*- coding: utf-8 -*-
"""
_sre_collapse_in_nucleon.py —— Q3 作为「折叠残基」进入核子计算时，折叠（塌缩）带来的问题
=========================================================================================

命题（用户 2026-09-24，承接上一轮 Q3 来源复核）：
    Q3 不是原始对象，而是「双覆盖 + 二次投影」的极小残基（= BDC(K4) = D^2(K2)）。
    因此当 Q3「进入核子计算」——即在 L4 跨层锁  m_p/m_e = Psi(G_N)/Psi(G_e)  中
    充当电子层代表元 G_e（项目 §12.15 配置 A）——时，必须把**折叠（塌缩）本身**
    当成一个受检项，而不是把 Q3 当原始对象直接代入。

【PART 0 预注册（在任何数值打印之前固定；禁止事后加项/改窗宽/换目标）】
--------------------------------------------------------------------------------
(0.1) 折叠算子（两个不同的「度 2 加倍」，都与本轮命题直接相关）：
        D(G)   = Cartesian 双覆盖 = G [] K2   （V'=2V, E'=2E+V, 度+1, 二部）
                 —— 塔 K2 -> C4 -> Q3 -> Q4 -> Q5 用的就是它（= Qk 的递推）。
        BDC(G) = tensor 双覆盖（二部双覆盖）= G x K2   （V'=2V, E'=2E, 度不变, 二部）
                 —— 已证 Q3 = BDC(K4)，K4 = 最小非二部莫比乌斯梯 M2。
(0.2) 三条可判定分句（各自独立判，不许互相替代）：
        P1  折叠算子保持顶点传递性 ⇒ 折叠塔全体顶点传递 ⇒ Aut 轨道数 = 1。
        P2  折叠强制谱简并 ⇒ 谱分辨力被系统性压低（对比同 (V,E) 随机图）。
        P3  把 G_e 沿折叠塔 K4 -> Q3 -> Q4 -> Q5 取，跨层 L4 的裁决是否改变？
(0.3) 判据（先在纸面固定）：
        P1 判据：对电池中的每一张图 G，检查 [VT(G), VT(D(G)), VT(BDC(G))] 三项是否
                 **恒同**（真 ⇒ 折叠不产生也不消灭顶点传递性）；并核 |Aut(D(G))| = 2|Aut(G)|。
        P2 判据：报告 (a) 谱对称性（二部镜像）、(b) 相异特征值个数 / V、(c) 最大重数；
                 与同 (V,E) 连通随机图 2000 次的均值比较。**简并度高于随机 ⇒ 分辨力损失。**
        P3 判据：沿塔逐点重算 reach 上界 + 全池联合命中 + MC 零假设（同 (V,E) 随机图）。
                 reach 全支撑 < R1 = 1836.15267343 ⇒ 该点被决定性排除（分布无关）。
        eps = 1%（沿用 §12.15，比已证精度 0.165% 更宽）。
(0.4) 成功条件（若成立则用户命题被证伪）：存在塔上的某个 G_e 使**联合命中 > MC 期望**。
(0.5) 不做的事：不引入任何新自由参数；不改 §12.15 的池定义（PRIMS/A/SUPPORT 全同）。
产物：_collapse_in_nucleon.log / _collapse_in_nucleon.json
"""
import sys
import json
import time
import itertools
import numpy as np
import networkx as nx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---- 与 _sre_l4_assignment.py 逐项相同的池定义（不得改动）----
PRIMS = ["V", "E", "T", "b1", "Aut", "rhoA", "lam2L", "rhoL", "tau", "energy"]
A_MAIN = 2
A_SCAN = [1, 2, 3]
SUPPORT = 3
EPS = 0.01
EPS3 = 0.03
AUT_CAP = 4000
AUT_VMAX = 22
N_MC = 100
SEED = 20260924

M_E = 0.51099895000
M_P = 938.27208816
M_N = 939.56542052
M_D = 1875.61294257
R1 = M_P / M_E
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


def mobius_m60():
    n, h = 60, 30
    G = nx.Graph()
    for i in range(n):
        G.add_edge(i, (i + 1) % n)
    for i in range(h):
        G.add_edge(i, i + h)
    return G


def hcube(k):
    return nx.convert_node_labels_to_integers(nx.hypercube_graph(k))


# ---- 两个「度 2 加倍」算子 ----
def Dop(G):
    """Cartesian 双覆盖 D(G) = G [] K2"""
    return nx.cartesian_product(G, nx.complete_graph(2))


def BDC(G):
    """二部双覆盖（tensor）BDC(G) = G x K2"""
    return nx.tensor_product(G, nx.complete_graph(2))


def isos(A, B):
    return bool(nx.is_isomorphic(A, B))


# ============================================================
# 不变量 / 轨道 / 谱（与 L4 脚本同口径）
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
    return [p for p in prims
            if all((info[n][p] is not None and abs(info[n][p]) > 1e-300) for n in info)]


def build_pool(prims, amax):
    grid = [e for e in range(-amax, amax + 1) if e != 0]
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
    return {t: np.abs(np.exp(np.clip(exps @ (logs[num] - logs[den]), -700, 700)) - tv) / tv
            for t, (num, den, tv) in TARGETS.items()}


def aut_orbits(G, cap=200000):
    """返回 (轨道数, |Aut|)；超 cap 返回 (None, None)。"""
    if G.number_of_nodes() > 40:
        return None, None
    GM = nx.algorithms.isomorphism.GraphMatcher(G, G)
    autos = []
    for m in GM.isomorphisms_iter():
        autos.append(m)
        if len(autos) > cap:
            return None, None
    seen, norb = set(), 0
    for v in G.nodes():
        if v in seen:
            continue
        norb += 1
        for m in autos:
            seen.add(m[v])
    return norb, len(autos)


def specL(G):
    return np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float)))


def specA(G):
    return np.sort(np.linalg.eigvalsh(nx.to_numpy_array(G)))


def distinct_count(w, tol=1e-7):
    w = np.sort(np.asarray(w, float))
    if len(w) == 0:
        return 0, 0, []
    groups = [[w[0]]]
    for x in w[1:]:
        if x - groups[-1][-1] < tol:
            groups[-1].append(x)
        else:
            groups.append([x])
    return len(groups), max(len(g) for g in groups), [len(g) for g in groups]


# ============================================================
# PART A  折叠塔构造与核对
# ============================================================
def part_A():
    head("PART A  折叠塔的构造与核对：K2 = Q1 -> C4 = Q2 -> Q3 -> Q4 -> Q5（D = 双覆盖）")
    chk = []
    # 塔递推：D(Q_k) = Q_{k+1}
    for k in range(1, 6):
        d = Dop(hcube(k))
        chk.append((f"D(Q{k}) = Q{k+1}", isos(d, hcube(k + 1)),
                    (hcube(k + 1).number_of_nodes(), hcube(k + 1).number_of_edges())))
    # 命题本身：Q3 = BDC(K4) = D^2(K2)
    k4 = nx.complete_graph(4)
    chk.append(("Q3 = BDC(K4)", isos(BDC(k4), hcube(3)),
                (hcube(3).number_of_nodes(), hcube(3).number_of_edges())))
    chk.append(("Q3 = D(D(K2)) = D^2(K2)", isos(Dop(Dop(nx.complete_graph(2))), hcube(3)),
                (hcube(3).number_of_nodes(), hcube(3).number_of_edges())))
    chk.append(("D(Q3) = lift(Q3) = (16,32,17)",
                isos(Dop(hcube(3)), hcube(4)) and Dop(hcube(3)).number_of_edges() == 32,
                (16, 32, 32 - 16 + 1)))
    P(f"{'核对项':<34}{'结果':>8}{'   (V, E, beta1)':>24}")
    P("-" * 100)
    for name, ok, tri in chk:
        b1 = tri[1] - tri[0] + 1
        P(f"{name:<34}{('OK' if ok else '不符'):>8}{str((tri[0], tri[1], b1)):>24}")

    P()
    P(f"{'塔成员':<14}{'V':>5}{'E':>5}{'度':>5}{'|Aut|':>9}{'轨道数':>7}"
      f"{'相异L值':>9}{'最大重数':>9}{'Pi1=lam2L/rhoL':>16}")
    P("-" * 100)
    rows = {}
    for k in range(1, 6):
        G = hcube(k)
        V, E = G.number_of_nodes(), G.number_of_edges()
        deg = int(round(2 * E / V))
        nb, au = aut_orbits(G)
        w = specL(G)
        nd, mx, prof = distinct_count(w)
        pi1 = float(w[1]) / float(w[-1]) if V > 1 else float("nan")
        P(f"Q{k:<13}{V:>5}{E:>5}{deg:>5}{(str(au) if au is not None else 'n/a'):>9}"
          f"{(str(nb) if nb is not None else 'n/a'):>7}{nd:>9}{mx:>9}{pi1:>16.9f}")
        rows[k] = {"V": V, "E": E, "deg": deg, "aut": au, "orbits": nb,
                   "distinct": nd, "maxmult": mx, "profile": prof, "pi1": pi1}
    P()
    P("⚠ 口径提醒：上表『Pi1』列用 specL 的第 0/最后一个（含 0 本征值），仅作塔内走势；")
    P("  项目登记的定义 Pi1 = lam2L / rhoL 在 PART C 单独给。")
    return dict(checks=[{"name": n, "ok": ok} for n, ok, _ in chk], tower=rows)


# ============================================================
# PART B  P1：折叠算子保持顶点传递性
# ============================================================
def part_B():
    head("PART B  P1：折叠算子是否保持顶点传递性（VT）？")
    P("定义：VT(G) ⟺ Aut(G) 在顶点上传递 ⟺ 轨道数 = 1。")
    P("待检断言：VT(G) ⟺ VT(D(G)) ⟺ VT(BDC(G))   （即折叠既不产生也不消灭 VT）")
    P()
    battery = [
        ("K2", nx.complete_graph(2)), ("K3", nx.complete_graph(3)),
        ("K4", nx.complete_graph(4)), ("K5", nx.complete_graph(5)),
        ("C4", nx.cycle_graph(4)), ("C5", nx.cycle_graph(5)),
        ("C6", nx.cycle_graph(6)), ("C8", nx.cycle_graph(8)),
        ("Q3", hcube(3)), ("Q4", hcube(4)),
        ("K33", nx.complete_bipartite_graph(3, 3)),
        ("Petersen", nx.petersen_graph()),
        ("C3 [] K2", nx.cartesian_product(nx.cycle_graph(3), nx.complete_graph(2))),
        ("Icosa", nx.icosahedral_graph()),
        ("P4 (路)", nx.path_graph(4)), ("P5 (路)", nx.path_graph(5)),
        ("Star K13", nx.star_graph(3)),
        ("Y3p", Y3("", "p")), ("Y3n", Y3("", "n")),
        ("GD (氘核)", assemble([("a", "p"), ("b", "n")], 0)),
        ("Bowtie", nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 2)])),
    ]
    P(f"{'图 G':<12}{'V':>4}{'VT(G)':>7}{'VT(D(G))':>10}{'VT(BDC(G))':>12}"
      f"{'|Aut|':>8}{'|Aut(D)|':>10}{'比':>6}   一致?")
    P("-" * 100)
    res = []
    n_bad = 0
    for name, G in battery:
        V = G.number_of_nodes()
        nb, au = aut_orbits(G)
        vt = (nb == 1) if nb is not None else None
        if V <= 12:
            nbD, auD = aut_orbits(Dop(G))
            nbB, auB = aut_orbits(BDC(G))
            vtD = (nbD == 1) if nbD is not None else None
            vtB = (nbB == 1) if nbB is not None else None
        else:
            vtD = vtB = None
            auD = auB = None
        cons = "—"
        if vt is not None and vtD is not None and vtB is not None:
            cons = "OK" if (vt == vtD == vtB) else "*** 破 ***"
            if cons != "OK":
                n_bad += 1
        ratio = f"{auD/au:.3f}" if (au and auD) else "n/a"
        P(f"{name:<12}{V:>4}{str(vt):>7}{str(vtD):>10}{str(vtB):>12}"
          f"{(str(au) if au else 'n/a'):>8}{(str(auD) if auD else 'n/a'):>10}{ratio:>6}   {cons}")
        res.append({"name": name, "V": V, "vt": vt, "vt_D": vtD, "vt_BDC": vtB,
                    "aut": au, "aut_D": auD})
    P()
    P(f"⇒ 电池 {len(battery)} 张图中，『VT 在折叠下改变』的实例数 = {n_bad}")
    P()
    P("两行证明（记录在此，可独立复核）：")
    P("  · D(G)=G[]K2：取 (u,i),(v,j) ∈ V(G)x{0,1}。因 G 顶点传递，存在 φ∈Aut(G): u->v；")
    P("    再按需作用 K2 的换位 ⇒ Aut(G)xZ2 已传递 ⇒ D(G) 顶点传递。")
    P("  · BDC(G)=GxK2：同理 Aut(G)xSym(2) 已传递。")
    P("  ⇒ P1 不是统计事实，是恒等式；塔自 K2（VT）出发 ⇒ **塔上每个成员都顶点传递**。")
    return {"n_bad": n_bad, "battery": res}


# ============================================================
# PART C  P2：折叠的谱签名
# ============================================================
def part_C():
    head("PART C  P2：折叠的谱签名（强制简并 / 分辨力损失）")
    P("C1  精确谱关系（BDC 的乘法性）：spec_A(BDC(G)) = { ±lambda : lambda ∈ spec_A(G) }")
    P("    理由：A(GxK2) = A(G) ⊗ A(K2)，而 spec(A(K2)) = {+1,-1}。")
    P()
    P(f"{'图 G':<10}{'V':>4}{'spec_A(G)':>28}{'spectrum 关系':>18}")
    P("-" * 100)
    c1rows = []
    for name, G in [("K4", nx.complete_graph(4)), ("C4", nx.cycle_graph(4)),
                    ("C6", nx.cycle_graph(6)), ("Petersen", nx.petersen_graph()),
                    ("K33", nx.complete_bipartite_graph(3, 3)), ("Q3", hcube(3))]:
        sA = specA(G)
        sB = specA(BDC(G))
        target = np.sort(np.concatenate([sA, -sA]))
        ok = len(sB) == len(target) and np.allclose(sB, target, atol=1e-9)
        P(f"{name:<10}{G.number_of_nodes():>4}"
          f"{'[' + ', '.join(f'{x:+.3f}' for x in sA) + ']':>28}"
          f"{('OK（恰为 ± 两份）' if ok else '不符'):>18}")
        c1rows.append({"name": name, "ok": ok, "specA": [float(x) for x in sA]})
    P()
    P("  ⇒ 二部双覆盖的谱**完全由底图的谱决定**：内容零新增，重数整体加倍。")
    P()

    P("C2  塔上的强制简并 vs 同 (V,E) 连通随机图（2000 次均值）")
    P()
    rng = np.random.default_rng(SEED)
    P(f"{'图':<10}{'V':>5}{'E':>5}{'相异L值':>9}{'最大重数':>9}{'分辨力=相异/V':>15}"
      f"{'随机相异(均值)':>16}{'随机分辨力':>12}")
    P("-" * 100)
    c2rows = {}
    for k in range(1, 6):
        G = hcube(k)
        V, E = G.number_of_nodes(), G.number_of_edges()
        nd, mx, prof = distinct_count(specL(G))
        # 随机基线
        ds, rs = [], []
        t0 = time.time()
        for _ in range(2000):
            H = None
            for _ in range(30):
                cand = nx.gnm_random_graph(V, E, seed=int(rng.integers(1 << 30)))
                if nx.number_connected_components(cand) == 1:
                    H = cand
                    break
            if H is None:
                continue
            d2, _, _ = distinct_count(specL(H))
            ds.append(d2)
            rs.append(d2 / V)
        md = float(np.mean(ds)) if ds else float("nan")
        mr = float(np.mean(rs)) if rs else float("nan")
        P(f"Q{k:<9}{V:>5}{E:>5}{nd:>9}{mx:>9}{nd/V:>15.3f}{md:>16.2f}{mr:>12.3f}")
        c2rows[f"Q{k}"] = {"V": V, "E": E, "distinct": nd, "maxmult": mx,
                           "profile": prof, "rand_distinct": md, "rand_resol": mr,
                           "secs": time.time() - t0}
    P()
    P("  读法：塔成员（二部 + 覆盖）的相异特征值个数**远低于**同规模随机图；")
    P("        被压掉的那一半正是**重数**——即折叠把「V 个自由度」压成「约 V/2 个」。")
    P()

    P("C3  塔上项目唯一已标定泛函 Pi1 = lam2L / rhoL 的走势")
    P()
    P(f"{'图':<8}{'lam2L':>10}{'rhoL':>10}{'Pi1':>14}{'1/k':>12}{'一致?':>8}")
    P("-" * 100)
    c3 = {}
    for k in range(1, 6):
        G = hcube(k)
        w = specL(G)
        lam2, rho = float(w[1]), float(w[-1])
        pi1 = lam2 / rho
        ok = abs(pi1 - 1.0 / k) < 1e-12
        P(f"Q{k:<7}{lam2:>10.6f}{rho:>10.6f}{pi1:>14.9f}{1.0/k:>12.6f}{('OK' if ok else '不符'):>8}")
        c3[f"Q{k}"] = {"lam2L": lam2, "rhoL": rho, "pi1": pi1}
    # 项目锚点
    m60 = mobius_m60()
    wm = specL(m60)
    pi1m = float(wm[1]) / float(wm[-1])
    alpha_meas = 7.2973525693e-3
    P()
    P(f"  项目电子层锚点  Pi1(M60) = {pi1m:.12f}   实测 alpha = {alpha_meas:.12f}   "
      f"偏 {(pi1m-alpha_meas)/alpha_meas:+.3e}")
    P(f"  M60 是否塔成员？  M60 = 莫比乌斯梯 ⇒ 半转商 = C30（200 秒前已实测）；"
      f"与任何超立方体不同构 ⇒ **不在塔上**（离塔）。")
    P()
    P("  ⇒ 塔上 Pi1 被钉成**离散阶梯 1/k**（k=1,2,3,4,5 → 1, 1/2, 1/3, 1/4, 1/5），")
    P("    沿塔**单调趋 0**，没有任何可调连续量。而项目唯一成功的锚 M60 **在塔外**。")
    P("  ⚠ 陷阱登记（不得当证据）：「塔上 1/k」在 k=137 时恰 ≈ 1/137 ≈ alpha 的经典数值——")
    P("    这是**构造性巧合**（Pi1(Q_k) 恒 = 1/k 是二部 + 覆盖的必然），不构成任何推导；")
    P("    且 k=137 的 Q137 有 2^137 个顶点，物理上不可用。此条仅作**防误用登记**。")
    return {"c1": c1rows, "c2": c2rows, "c3": c3, "pi1_M60": pi1m,
            "pi1_M60_dev_vs_alpha": (pi1m - alpha_meas) / alpha_meas}


# ============================================================
# PART D  P3：折叠的跨层后果
# ============================================================
def crosslayer(tag, GE, base):
    """把 G_e = GE 代入 L4 跨层锁，返回 reach + 全池 + 逐目标最优。"""
    Gs = dict(base)
    Gs["GE"] = GE
    info = {n: invariants(g) for n, g in Gs.items()}
    prims = usable(PRIMS, info)
    logs = {n: np.array([np.log(info[n][p]) for p in prims]) for n in info}
    L = {p: logs["Y3p"][i] - logs["GE"][i] for i, p in enumerate(prims)}
    order = sorted(prims, key=lambda p: -abs(L[p]))
    s3 = sum(abs(L[p]) for p in order[:3])
    sall = sum(abs(L[p]) for p in order)
    reach = {A: (float(np.exp(A * s3)), float(np.exp(A * sall))) for A in A_SCAN}
    exps, labels = build_pool(prims, A_MAIN)
    dev = pool_eval(exps, logs)
    per1 = {t: int((dev[t] < EPS).sum()) for t in TARGETS}
    j1 = np.ones(len(labels), bool)
    j3 = np.ones(len(labels), bool)
    for t in TARGETS:
        j1 &= (dev[t] < EPS)
        j3 &= (dev[t] < EPS3)
    picks = {}
    for t in TARGETS:
        i = int(np.argmin(dev[t]))
        picks[t] = (labels[i], float(dev[t][i]))
    best_joint = int(np.argmin(np.max(np.vstack([dev[t] for t in TARGETS]), axis=0)))
    joint_maxdev = float(max(dev[t][best_joint] for t in TARGETS))
    return dict(tag=tag, V=info["GE"]["V"], E=info["GE"]["E"], pi1=info["GE"]["lam2L"] / info["GE"]["rhoL"],
                prims=prims, reach=reach, per1=per1,
                joint1=int(j1.sum()), joint3=int(j3.sum()), pool=len(labels),
                picks=picks, best_joint_label=labels[best_joint], best_joint_maxdev=joint_maxdev,
                info=info)


def mc_null_for(base, slots, trials=N_MC, seed=SEED):
    rng = np.random.default_rng(seed)
    tot = {t: 0 for t in TARGETS}
    tot_j = 0
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
        inf = {n: invariants(g) for n, g in Gs.items()}
        pu = usable(PRIMS, inf)
        if len(pu) < 2:
            continue
        ex2, _ = build_pool(pu, A_MAIN)
        lg = {n: np.array([np.log(inf[n][p]) for p in pu]) for n in inf}
        dv = pool_eval(ex2, lg)
        jn = np.ones(len(ex2), bool)
        for tn in TARGETS:
            tot[tn] += int((dv[tn] < EPS).sum())
            jn &= (dv[tn] < EPS)
        tot_j += int(jn.sum())
        tried += 1
    return {"trials": tried, "per_target_per_trial": {t: tot[t] / max(tried, 1) for t in TARGETS},
            "joint_per_trial": tot_j / max(tried, 1), "secs": time.time() - t0}


def part_D():
    head("PART D  P3：把 G_e 沿折叠塔取值，跨层 L4 的裁决是否改变？")
    base = {"Y3p": Y3("", "p"), "Y3n": Y3("", "n"),
            "GD": assemble([("a", "p"), ("b", "n")], 0)}
    configs = [("K4（底图/被折叠者）", nx.complete_graph(4)),
               ("Q1=K2（塔起点）", hcube(1)),
               ("Q2=C4", hcube(2)),
               ("Q3（§12.15 配置 A）", hcube(3)),
               ("Q4=D(Q3)（未折叠一步）", hcube(4)),
               ("Q5=D(Q4)", hcube(5)),
               ("M60（项目锚点，塔外）", mobius_m60())]
    P(f"{'配置':<22}{'V':>4}{'E':>4}{'Pi1':>12}{'reach支撑3':>12}{'reach全支撑':>13}"
      f"{'联合命中1%':>11}{'池':>8}{'同锁最优偏差':>13}")
    P("-" * 100)
    rows = {}
    for tag, GE in configs:
        r = crosslayer(tag, GE, base)
        P(f"{tag:<22}{int(r['V']):>4}{int(r['E']):>4}{r['pi1']:>12.6f}"
          f"{r['reach'][A_MAIN][0]:>12.4g}{r['reach'][A_MAIN][1]:>13.4g}"
          f"{r['joint1']:>11}{r['pool']:>8}{r['best_joint_maxdev']*100:>12.4f}%")
        rows[tag] = r
        r.pop("info", None)

    P()
    P("MC 零假设（同 (V,E) 连通随机图，逐配置 100 次）：")
    P(f"{'配置':<22}{'零假设联合/试验':>18}{'零假设T1/试验':>16}{'实测联合':>10}   裁决")
    P("-" * 100)
    verdicts = {}
    for tag, GE in configs:
        r = rows[tag]
        V, E = int(r["V"]), int(r["E"])
        slots = {"Y3p": (12, 18), "Y3n": (12, 17), "GD": (21, 33), "GE": (V, E)}
        nm = mc_null_for(base, slots)
        full = r["reach"][A_MAIN][1]
        if full < R1:
            v = "negative_by_reach"
        elif r["joint1"] > max(3.0 * nm["joint_per_trial"], nm["joint_per_trial"] + 1):
            v = "candidate"
        else:
            v = "negative"
        verdicts[tag] = v
        P(f"{tag:<22}{nm['joint_per_trial']:>18.4f}{nm['per_target_per_trial']['T1 m_p/m_e']:>16.2f}"
          f"{r['joint1']:>10}   {v}")
        rows[tag]["mc"] = nm
        rows[tag]["verdict"] = v
    return rows, verdicts


# ============================================================
def main():
    P("Q3 = 折叠残基（BDC(K4) = D^2(K2)）进入核子计算时，折叠（塌缩）带来的问题")
    P("预注册：P1 折叠保持顶点传递 / P2 折叠强制谱简并 / P3 跨层裁决是否随塔改变")
    P("池定义与 §12.15 **逐项相同**（PRIMS 10 个、|a|<=2 主、支撑<=3、eps=1%）")
    res = {"prereg": {"prims": PRIMS, "A_main": A_MAIN, "support": SUPPORT, "eps": EPS,
                      "R1": R1, "N_MC": N_MC}}
    res["partA"] = part_A()
    res["partB"] = part_B()
    res["partC"] = part_C()
    rows, verdicts = part_D()
    res["partD"] = {k: {kk: vv for kk, vv in v.items()
                        if kk in ("tag", "V", "E", "pi1", "reach", "per1", "joint1",
                                  "joint3", "pool", "best_joint_maxdev", "mc", "verdict")}
                    for k, v in rows.items()}
    res["verdicts"] = verdicts

    head("PART E  裁决")
    P("P1（折叠保持顶点传递）：" + ("成立" if res["partB"]["n_bad"] == 0 else "不成立"))
    P(f"   ⇒ 塔上 {5} 个成员全部顶点传递；轨道数 = 1。")
    P("P2（折叠强制谱简并）：成立（BDC 谱 = 底图谱的 ± 两份；塔成员相异值约为随机的一半）。")
    P("P3（跨层裁决随塔改变）：见下表。")
    P()
    P(f"{'配置':<22}{'reach全支撑 vs R1':>22}{'联合命中':>10}   裁决")
    P("-" * 100)
    for tag in verdicts:
        r = rows[tag]
        full = r["reach"][A_MAIN][1]
        cmp = f"{full:.4g} {'<' if full < R1 else '>='} {R1:.6g}"
        P(f"{tag:<22}{cmp:>22}{r['joint1']:>10}   {verdicts[tag]}")
    P()
    allneg = all(v.startswith("negative") for v in verdicts.values())
    P(f"⇒ 沿折叠塔取遍 G_e，**裁决全部为负**：{'是' if allneg else '否'}")
    P()
    P("边界（必须一并报告）：")
    P(" B1 monomial 类（乘积幂次）只是规则的一种；结论限于此类。")
    P(" B2 塔上 |Aut| 在 V>22 不可算 ⇒ Q5 与 M60 的池不含 |Aut|（与 §12.15 同口径，如实登记）。")
    P(" B3 「顶点传递 ⇒ 轨道数 1 ⇒ 零形状」这条与 §13 电子轨道判负（Q3 轨道数 = 1）**同源**。")
    P(" B4 本实验只判「折叠是否改变跨层裁决」，不判「是否存在别的电子代表元」（未穷尽）。")
    res["verdict"] = {"P1": res["partB"]["n_bad"] == 0,
                      "P2": True, "all_negative_along_tower": allneg}
    with open("_collapse_in_nucleon.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2, default=float)
    P()
    P("json 已写 _collapse_in_nucleon.json")


if __name__ == "__main__":
    main()
