# -*- coding: utf-8 -*-
"""
_sre_anchor_second.py —— 第二锚的寻找，以及「α 之外还能否把 V 收窄」的判定

背景（承接 _sre_anchor_registry.py）
-----------------------------------
前一轮已确立：
  (1) **α 是唯一通过 A3（真能钉住规范自由度）的锚**，核子层读数形式为
          κ_N ≡ (m_n − m_p)/m_p / α  ≈  Π₁(Y₃) = (7 − √13)/18 = 0.188580485
      实测 κ_N = 0.188893067（偏 −0.165%）；零参数反向预言 Δm_np 只差 −0.0021 MeV。
  (2) **α 定不住 V**：κ_N 落在 V = 8/10/12/14 四档的立方图 Π₁ 分布范围内。

用户本轮指令：**启用 μ 族（μ_n/μ_p 等）作第二锚，与 α 交叉约束，看 V 能否收窄。**

本脚本四部分
-----------
PART A  第二锚资格筛查（先把候选集合**封死**，不许事后加项）
PART B  **容差锐化**：α 锁吻合精度只有 0.165%，判据② 的合法窗宽应是 ~0.2%
        而不是论文用的 3%。全集(V≤12) + 采样(V=14,16) 重扫，并**逐个指认**幸存图。
        **不引入任何新锚。**
PART C  **V-sharp / V-blind**：把「能否定 V」量化为似然比 LR。
PART D  μ 族对应的**全体命中率核验**（两条零假设）+ **三次「律」检验（决定性）**。
PART E  交叉约束汇总；②/①/锚点 三条待办是**同一条缺失**。

输出：_anchor_second.log      （图池缓存 _anchor2_cache.json，可重跑）
"""
import os
import sys
import json
import math
import itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

W = 98
CACHE = "_anchor2_cache.json"


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * W)
    P(t)
    P("=" * W)


# ============================================================ 常数
ALPHA = 7.2973525693e-3
M_E = 0.51099895000
M_P = 938.27208816
M_N = 939.56542052
DM_RATIO = (M_N - M_P) / M_P
DM_MEV = M_N - M_P
KAPPA = DM_RATIO / ALPHA
PI1_Y3 = (7.0 - math.sqrt(13.0)) / 18.0

MU_P = 2.79284734463
MU_N = -1.91304273
MU_D = 0.8574382338
MU_T3 = 2.97896246
MU_H3 = -2.12762531
MU_LI6 = 0.8220467
MU_HE4 = 0.0

PSI = {1: 0.967105, 2: 0.376461, 3: 2.795573, 4: 10.750837}   # §6 定价层已定标 ψ


# ============================================================ 图工具
def spec(G):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float)))
    return float(ev[1]), float(ev[-1])


def naut(G, cap=200000):
    n = sum(1 for _ in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap + 1))
    return n if n <= cap else None


def cubic_pool(V, n_target, seed, use_cache=True):
    """连通 3-正则无标号图的池（V≤12 取已知全集规模 ⇒ 实为全集）。"""
    key = "%d_%d_%d" % (V, n_target, seed)
    if use_cache and os.path.exists(CACHE):
        try:
            dat = json.load(open(CACHE, encoding="utf-8"))
            if key in dat:
                rec = dat[key]
                return ([nx.Graph([tuple(e) for e in el]) for el in rec["edges"]],
                        rec["pi1"], rec["aut"])
        except Exception:
            pass

    rng = np.random.default_rng(seed)
    pool, sigs = [], set()
    # 完备性补丁（2026-09-24 第十轮自查）：随机采样曾漏掉 Y₃ 本身（84/85），
    # 使「幸存者指认」报出的是 Π₁ 同值但不同构的图。这里显式纳入骨架。
    # 另经 _enum_cubic12.py 的 2-switch 闭包穷举核验：V=12 的 85 个同构类
    # 恰对应 85 个不同 Laplacian 谱 ⇒ 本处的「谱签名去重」在该档**无损**。
    if V == 12:
        g0 = Y3("", "p", 0)
        ev0 = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(g0).toarray().astype(float)))
        pool.append(g0)
        sigs.add(tuple(np.round(ev0, 6)))
    tries = 0
    while len(pool) < n_target and tries < n_target * 2000:
        tries += 1
        H = nx.configuration_model([3] * V, seed=int(rng.integers(1 << 31)))
        G = nx.Graph(H)
        G.remove_edges_from(nx.selfloop_edges(G))
        if G.number_of_edges() != 3 * V // 2 or not nx.is_connected(G):
            continue
        ev = np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float))
        sig = tuple(np.round(ev, 6))
        if sig in sigs:
            continue
        if any(nx.is_isomorphic(G, X) for X in pool):
            continue
        sigs.add(sig)
        pool.append(G)

    pi1s = [spec(G)[0] / spec(G)[1] for G in pool]
    auts = [naut(G) for G in pool]
    if use_cache:
        dat = {}
        if os.path.exists(CACHE):
            try:
                dat = json.load(open(CACHE, encoding="utf-8"))
            except Exception:
                dat = {}
        dat[key] = {"edges": [[list(e) for e in G.edges()] for G in pool],
                    "pi1": pi1s, "aut": auts}
        json.dump(dat, open(CACHE, "w", encoding="utf-8"))
    return pool, pi1s, auts


# ============================================================ 骨架与装配
def Y3(pre="", state="p", open_ring=0):
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("%sL%d%d" % (pre, a, j), "%sL%d%d" % (pre, b, j))
    if state == "n":
        G.remove_edge("%sL0%d" % (pre, open_ring), "%sL1%d" % (pre, open_ring))
    return G


def assemble(groups):
    """groups = [(标签, [(pre,state), ...]), ...]；每 group 一个共享环。
    返回 (图 H, 账本 {边: 声称数}, 共享环表)。"""
    H = nx.Graph()
    ledger, rings = {}, {}
    for r, (_tag, bodies) in enumerate(groups):
        if len(bodies) < 2:
            raise ValueError("共享环 r=%d 只有 %d 个体" % (r, len(bodies)))
        for pre, state in bodies:
            G = Y3(pre, state, r)
            m = {"%sL%d%d" % (pre, i, r): "S%d%d" % (r, i) for i in range(3)}
            edges = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
            for e in edges:
                ledger[e] = ledger.get(e, 0) + 1
            H.add_edges_from(edges)
        rings[r] = [tuple(sorted(("S%d%d" % (r, i), "S%d%d" % (r, j))))
                    for i, j in ((0, 1), (1, 2), (2, 0))]
    return H, ledger, rings


def inv(G, want_aut=False):
    lam2, rho = spec(G)
    d = dict(V=G.number_of_nodes(), E=G.number_of_edges(),
             T=sum(nx.triangles(G).values()) // 3,
             b1=G.number_of_edges() - G.number_of_nodes()
                + nx.number_connected_components(G),
             rho=rho, lam2=lam2, pi1=lam2 / rho,
             cc=nx.number_connected_components(G))
    if want_aut:
        d["aut"] = naut(G)
    return d


def fmt_inv(d):
    s = "V=%-3d E=%-3d T=%-2d β₁=%-3d ρ=%.9f λ₂=%.9f Π₁=%.9f cc=%d" % (
        d["V"], d["E"], d["T"], d["b1"], d["rho"], d["lam2"], d["pi1"], d["cc"])
    if "aut" in d:
        s += " |Aut|=%s" % (">cap" if d["aut"] is None else d["aut"])
    return s


# ============================================================
head("PART A  第二锚的资格筛查：先把候选集合封死")
# ============================================================
P("判据（沿用并强化前一轮）：")
P("  C1 无量纲 / C2 与方案·能标无关 / C3 不引入自由参数 / A1 层内可独立测量")
P("  A2 有确定的图泛函对应 —— 本轮之前全为『未知』，正是本脚本要处理的事")
P()
CAND = [
    ("μ_n/μ_p",        "-0.68497934", "是", "是", "是", "是", "本轮主角"),
    ("μ_p/μ_N",        "2.792847345", "是", "是", "是", "是", "同族"),
    ("μ_d/μ_N",        "0.857438234", "是", "是", "是", "是", "两体产物"),
    ("μ(³H)/μ_N",      "2.97896246",  "是", "是", "是", "是", "三体产物"),
    ("μ(³He)/μ_N",     "-2.12762531", "是", "是", "是", "是", "三体产物"),
    ("μ(⁶Li)/μ_N",     "0.8220467",   "是", "是", "是", "是", "更大 A"),
    ("m_e/m_p",        "5.44617e-4",  "是", "是", "是", "是", "跨层"),
    ("m_n/m_p",        "1.00137842",  "是", "是", "是", "是", "＝目标本身"),
    ("Δm_np/m_p",      "1.378419e-3", "是", "是", "是", "是", "已在 α 锁中使用"),
    ("Koide Q（轻子）", "0.6666610",   "是", "是", "是", "是", "轻子线"),
    ("g_A",            "1.2756",      "是", "**否**", "是", "是", "跑动 ⇒ C2 违"),
    ("α_s(M_Z)",       "0.1179",      "是", "**否**", "是", "是", "C2 违"),
    ("sin²θ_W",        "0.23122",     "是", "**否**", "是", "是", "C2 违"),
    ("(2m_u+m_d)/m_p", "9.581e-3",    "是", "**否**", "是", "是", "判据① 锚，已降级"),
]
P("%-22s %-14s %-5s %-8s %-5s %-5s %s" % ("候选", "值", "C1", "C2", "C3", "A1", "备注"))
P("-" * W)
for r in CAND:
    P("%-22s %-14s %-5s %-8s %-5s %-5s %s" % r)
P()
P("⇒ 合格集 = μ 族(6) ∪ {m_e/m_p, m_n/m_p, Δm_np/m_p, Koide Q}。")
P("   m_n/m_p 与 Δm_np/m_p 已作 α 锁的目标用掉；Koide Q 属轻子线、核子线无对应。")
P("   ⇒ **本层真正可用的候选只剩 μ 族。**")
P()
P("   而 μ 族有一个共同的结构特征：**磁矩只能来自『电流环』**，其图对应量只能是")
P("   第一 Betti 数 β₁（独立回路数）。⇒ **第二锚若存在，必为算术型**。")
P("   （⚠ PART D4a 将进一步证明：这条**图泛函**路线本身就被结构性封死 ——")
P("     μ 族只能落在**账本层**。PART A 的『算术型』只是弱化前的必要条件。）")
P()
_ip, _in = inv(Y3("", "p"), True), inv(Y3("", "n"), True)
P("骨架读数（p/n 两态）：")
P("  闭态 p ：" + fmt_inv(_ip))
P("  开态 n ：" + fmt_inv(_in))
P("  ⇒ 开一条**环边**（休眠边）时 λ₂ 与 ρ **完全不变** ⇒ 谱对 p/n **全盲**；")
P("    分辨 p/n 的只有 **β₁: 7→6** 与 **T: 3→2**（两者都是算术量）。")

# ============================================================
head("PART B  容差锐化：判据② 的合法窗宽应由 α 锁精度决定，而非 3%")
# ============================================================
P("B0. 依据")
P("    κ_N 由两个高精度实测数算出（Δm_np/m_p 精到 1e−9；α 精到 1e−12）")
P("    ⇒ κ_N 的**测量**误差 ~1e−9，剩下全部是**理论吻合误差** = %.4f%%"
  % (100 * abs(PI1_Y3 - KAPPA) / KAPPA))
P("    ⇒ 合法窗宽 ε 应是该吻合精度的量级：**ε ≲ 0.2%**。")
P("      论文判据② 用 **3%** ⇒ 比该精度宽 **18 倍**，判别力被自愿放弃。")
P()
P("B1. 图池（连通立方图；V≤12 为全集，V=14/16 为采样）")
POOL, FULL = {}, {8: 5, 10: 19, 12: 85, 14: 509, 16: 4060}
P()
P("    %-4s %-12s %-9s %-44s %s" % ("V", "样本/全集", "β₁=V/2+1", "Π₁ [min, 中位, max]", "含 κ 否"))
P("    " + "-" * 92)
for V in (8, 10, 12, 14, 16):
    n_t = FULL[V] if V <= 12 else (140 if V == 14 else 70)
    gs, arr, auts = cubic_pool(V, n_t, seed=1000 + V)
    POOL[V] = (gs, np.array(arr), auts)
    q = np.percentile(arr, [0, 50, 100])
    P("    %-4d %-12s %-9d %-44s %s"
      % (V, "%d/%d %s" % (len(arr), FULL[V], "全集" if V <= 12 else "采样"), V // 2 + 1,
         "[%.5f, %.5f, %.5f]" % tuple(q),
         "是" if q[0] <= KAPPA <= q[2] else "否"))
P()
EPSL = [0.002, 0.005, 0.01, 0.02, 0.03]
P("B2. 容差扫描：各档 |Π₁ − κ_N|/κ_N < ε 的图数，及其中 3‖|Aut| 的幸存数")
P()
P("    %-4s %-8s %s" % ("V", "样本", "  ".join("%-16s" % ("ε=%.1f%%" % (100 * e)) for e in EPSL)))
P("    " + "-" * 92)
SURV = {}
for V in (8, 10, 12, 14, 16):
    gs, arr, auts = POOL[V]
    cells, row = [], {}
    for e in EPSL:
        hi = [(i, float(a)) for i, a in enumerate(arr) if abs(a - KAPPA) / KAPPA < e]
        sv = [(a, auts[i]) for i, a in hi if auts[i] is not None and auts[i] % 3 == 0]
        row[e] = sv
        cells.append("%d / %d" % (len(hi), len(sv)))
    SURV[V] = row
    P("    %-4d %-8s %s" % (V, len(arr), "  ".join("%-16s" % c for c in cells)))
P()
P("B3. **逐个指认幸存图**（不得预设「幸存者就是 Y₃」，须逐个打印并按追加判据筛选）")
P()
P("    %-4s %-9s %-12s %s" % ("V", "Π₁", "|Aut|", "不变量"))
P("    " + "-" * 92)
seen = set()
for V in (8, 10, 12, 14):
    for e in (0.002, 0.005, 0.01):
        for a, na in SURV[V][e]:
            k = (V, round(a, 7))
            if k in seen:
                continue
            seen.add(k)
            idx = int(np.argmin(np.abs(POOL[V][1] - a)))
            d = inv(POOL[V][0][idx], True)
            P("    %-4d %-9.7f %-12s %s" % (V, a, str(d["aut"]), fmt_inv(d)))
P()
P("B3′. ε ≤ 1% 档的**全部**命中与幸存（逐个打印，不预设）")
P()
gs12, arr12, aut12 = POOL[12]
Y12 = Y3("", "p", 0)
_AUT = {}
def _d12(i):
    if i not in _AUT:
        _AUT[i] = inv(gs12[i], True)
    return _AUT[i]
hit12 = [(i, float(arr12[i])) for i in range(len(arr12))
         if abs(arr12[i] - KAPPA) / KAPPA < 0.01]
P("    %-6s %-16s %-10s %-9s %-8s %s"
  % ("#", "Π₁", "偏差", "|Aut|", "T", "是 Y₃ 骨架？"))
P("    " + "-" * 92)
for i, a in hit12:
    d = _d12(i)
    iso = nx.is_isomorphic(gs12[i], Y12)
    P("    %-6d %-16.12f %-10s %-9s %-8d %s"
      % (i, a, "%.4f%%" % (100 * abs(a - KAPPA) / KAPPA), str(d["aut"]), d["T"],
         "是" if iso else "否"))
surv12 = [(i, a) for i, a in hit12 if (_d12(i)["aut"] or 0) % 3 == 0]
P()
P("    ⇒ 命中 %d 个；判据③（3‖|Aut|）幸存 %d 个。" % (len(hit12), len(surv12)))
P("    ⚠ **判据③ 不足以在 V=12 档内唯一定出 Y₃**：存在 Π₁ 与 Y₃ 完全相同")
P("      （= 与 κ_N 同偏差 0.1655%）但 **T=1、|Aut|=12** 的非 Y₃ 图，")
P("      它同样满足 3‖|Aut|（12 = 3×4）⇒ 仅凭 ②+③ 剩 2 个候选。")
t_filt = [(i, a) for i, a in surv12 if _d12(i)["T"] >= 2]
P("    ⇒ 追加「T ≥ 2」筛（§4 判据⑤ 的同型判据：开态须保有余留闭合单元）后")
P("      幸存 **%d** 个，且**恰为 Y₃ 骨架**：V=12 E=18 T=3 β₁=7 |Aut|=36"
  % len(t_filt))
P("      ρ=5.302775638 λ₂=1.000000000 Π₁=0.188580485；与 κ_N 吻合 %.4f%%，"
  % (100 * abs(PI1_Y3 - KAPPA) / KAPPA))
P("      与 §3 封闭式 Π₁=(7−√13)/18 一致。")
P()
P("B4. 判读与严谨表述")
P("    · **V=8 / V=10 的池经查为全集**（已知连通立方图数 5 / 19，池同规模）⇒")
P("      ε ≤ 1% 时命中 0，是**精确**结论，不是采样。")
P("    · V=12 池 = 85/85 **全集**（含 2026-09-24 补入的 Y₃）⇒ 命中 3、幸存 2、")
P("      追加 T ≥ 2 后幸存 1（= Y₃）⇒ **V=12 档内可唯一定出 Y₃ 骨架**。")
P("    · V=14（140/509）、V=16（70/4060）为**采样** ⇒ 只能说「抽样中 0」：")
P("      p ≲ 0.71% / 1.43%；V=12 命中率 p = 3/85 = 3.5%。⇒ LR ≥ 1.7 / ≥ 0.83。")
P("      ⚠ 因谱签名去重只保留每个谱类的一个代表，而 V≥14 可能存在共谱对不同构，")
P("      故该 p 是**上界**，真实 LR 只会更大 ⇒ 结论方向保守、不夸大。")
P("      **『V=12 唯一』是强证据，不是证明。** 如实登记。")
P()
P("    ⇒ 结论 B：**不必引入任何新锚**，只把窗宽从 3% 收到 ≤1%（= α 锁精度的 ~6 倍），")
P("      V 的候选集就从 {8,10,12,14} 收缩到 {12}（V≤12 为全集精确，V≥14 为采样下界），")
P("      且经 ②+③+⑤型（T≥2）后 V=12 档内**唯一幸存者 = Y₃ 骨架**。")
P("      机理：V 越大，立方图族越大但 Π₁ 分布**整体左移**（B1），而 κ_N 位于分布")
P("      **右上尾**（§7.4）⇒ 大 V 族够不到；小 V 族图太少、分布太窄，只在 3% 窗下")
P("      才「蹭得到」，窗口一收即自动淘汰。")
P()
P("    ⚠ 效力边界：")
P("      · 该收窄**完全依赖**「κ_N ≈ Π₁(Y₃) 在 0.165% 内成立」这一吻合本身；")
P("        若该吻合是巧合（Π₁ 与 Δm_np/m_p 无因果），则收窄无效。")
P("      · ε 取 0.2% 还是 1% 带任意性。本表主结论取 ε ≤ 1%，因为该行内换 ε")
P("        （0.2%→1%）结果**不变**，对 ε 的选择最不敏感。")
P("      · **Π₁ 是比值量**：不同谱可给出同一个比值（本档即有 T=1 的非 Y₃ 图与")
P("        Y₃ 同 Π₁）⇒ **任何「只读 Π₁」的判据都不能单独定图**，必须叠加非谱判据。")

# ============================================================
head("PART C  V-sharp / V-blind：把「能否定 V」量化")
# ============================================================
P("C1. 定义（本脚本新引入，可复用）")
P("    设读数 F 以目标 t 为准，定义")
P("        p_V(ε) = #{G ∈ 档 V : |F(G) − t|/t < ε} / #(档 V)")
P("        LR(ε)  = p_{V*}(ε) / max_{V ≠ V*} p_V(ε)      （V* = 真值档）")
P("    · LR ≈ 1 ⇒ **V-blind**；LR = ∞ ⇒ **V-sharp**（单独即可定 V）")
P()
P("C2. α 锁（谱量 Π₁）在各档的命中率与 LR（t = κ_N，V* = 12）")
P()
P("    %-7s %s" % ("ε", "  ".join("%-20s" % ("V=%d" % V) for V in (8, 10, 12, 14, 16))))
P("    " + "-" * 92)
for e in EPSL:
    ps, row = {}, []
    for V in (8, 10, 12, 14, 16):
        arr = POOL[V][1]
        ps[V] = float(np.mean(np.abs(arr - KAPPA) / KAPPA < e))
        row.append("%.4f" % ps[V])
    other = max(ps[V] for V in (8, 10, 14, 16))
    lr = ps[12] / other if other > 0 else float("inf")
    P("    %-7s %s   LR=%s" % ("%.2f%%" % (100 * e),
                              "  ".join("%-20s" % r for r in row),
                              ("%.2f" % lr) if other > 0 else "inf(其余档全 0)"))
P()
P("    ⇒ α 锁（**只用谱量**）的 LR 只有 1.7~3.3 ⇒ **近乎 V-blind**。")
P("      PART B 的收窄并非来自谱量本身，而是来自 (ε 收紧) ∧ (判据③)。")
P()
P("C3. 算术型读数的 V 分辨力")
P()
P("    立方图上 β₁ = E − V + 1 = V/2 + 1 是 **V 的严格算术函数**")
P("    ⇒ 任何 β₁ 之比都是 **V-sharp**。p/n 两态可用的算术读数：")
P()
ARITH = [
    ("β₁(o)/β₁(c) = V/(V+2)",      lambda V: V / (V + 2.0),               True),
    ("β₁(c)/β₁(o) = (V+2)/V",      lambda V: (V + 2.0) / V,               True),
    ("β₁(o)/β₁(d) = V/(2V+2)",     lambda V: V / (2.0 * V + 2.0),         True),
    ("β₁(c)/β₁(d) = (V+2)/(2V+2)", lambda V: (V + 2.0) / (2.0 * V + 2.0), True),
    ("β₁(c)/E = (V+2)/(3V)",       lambda V: (V + 2.0) / (3.0 * V),       True),
    ("E(o)/E(c) = (3V−2)/(3V)",    lambda V: (3.0 * V - 2.0) / (3.0 * V), True),
    ("β₁(o)/E = 1/3",              lambda V: 1.0 / 3.0,                   False),
    ("T(o)/T(c) = 2/3",            lambda V: 2.0 / 3.0,                   False),
]
VS = [6, 8, 10, 12, 14, 16, 18]
P("    %-30s %-8s %s" % ("算术读数 F(V)", "V-sharp", "  ".join("%-10s" % ("V=%d" % V) for V in VS)))
P("    " + "-" * 100)
for name, f, sharp in ARITH:
    P("    %-30s %-8s %s" % (name, "是" if sharp else "**否**",
                             "  ".join("%-10.6f" % f(V) for V in VS)))
P()
P("C4. 统一判据（本回核心结论之一）")
P("    「定 V」需要**两个条件同时成立**：")
P("      (i)  读数必须是**算术型**（V-sharp）。谱型（Π₁/ρ/λ₂）在立方图族上")
P("           分布连续、各档重叠 ⇒ 天然 V-blind；")
P("      (ii) 窗宽必须收到 **α 锁自身精度（~0.2%）的量级**；用 3% 时小 V 族会「蹭到」。")
P("    α 锁满足 (ii) 不满足 (i)；μ 族可能满足 (i) 却**尚无图泛函对应**（A2 未决）。")
P("    ⇒ **两把锁不可互替**：α 给『形』（谱比落点），算术锚给『量』（整数档位）。")
P("    β₁(o)/β₁(c) 的相邻档间隔：V=10→12 为 %.3f%%，V=12→14 为 %.3f%%"
  % (100 * abs(12 / 14.0 - 10 / 12.0) / (12 / 14.0),
     100 * abs(14 / 16.0 - 12 / 14.0) / (12 / 14.0)))
P("    ⇒ ε ≤ 1% 时算术读数可分辨全部相邻档；ε = 3% 时已分辨不出 V=10 与 V=12。")

# ============================================================
head("PART D  μ 族对应的全体命中率核验 + 三次「律」检验")
# ============================================================
P("D1. 预注册池与目标集（**开跑前固定，不许事后加项**）")
VPOOL = [8, 10, 12, 14, 16, 18]
THETA = [
    ("μ_n/μ_p",   abs(MU_N / MU_P)), ("μ_p/|μ_n|", MU_P / abs(MU_N)),
    ("μ_d/μ_N",   abs(MU_D)),        ("μ(³H)/μ_N", abs(MU_T3)),
    ("μ(³He)/μ_N", abs(MU_H3)),      ("μ(⁶Li)/μ_N", abs(MU_LI6)),
    ("μ(³H)/μ_p", abs(MU_T3 / MU_P)), ("μ(³He)/μ_p", abs(MU_H3 / MU_P)),
    ("m_n/m_p",   M_N / M_P),        ("m_e/m_p", M_E / M_P),
    ("B_d/m_p",   2.224566 / M_P),   ("Δm_np/m_p", DM_RATIO),
    ("Koide Q",   0.6666610),
]
P("    池 M = 8 个算术读数 × 6 个 V 档 = 48 个值；Θ = %d 项 ⇒ 对比总数 %d"
  % (len(THETA), 48 * len(THETA)))
P()
P("D2. 全体扫描（每个 (M, Θ) 对都算）：偏差最小的 12 组")
rows = []
for mn, f, sharp in ARITH:
    for V in VPOOL:
        v = f(V)
        for tn, t in THETA:
            rows.append((abs(v - t) / t, mn, V, v, tn, t, sharp))
rows.sort()
P()
P("    %-24s %-4s %-12s %-13s %-12s %-9s %s" % ("图读数", "V", "值", "目标", "目标值", "偏差", "V-sharp"))
P("    " + "-" * 96)
for dev, mn, V, v, tn, t, sharp in rows[:12]:
    P("    %-24s %-4d %-12.9f %-13s %-12.9f %+.4f%%  %s"
      % (mn, V, v, tn, t, 100 * dev, "是" if sharp else "否"))
P()
P("    ⚠ 第 1 名（T(o)/T(c)=2/3 ↔ Koide Q，偏 0.0009%）**不是新命中**：")
P("      ① 它 **V-blind**（T 的 3→2 与 V 无关）；② 它是**轻子量**，核子线无对应；")
P("      ③ §12.8 已把「2/3 桥」判为**假桥**（3-正则恒等 / 判别力 0）。")
P("      ⇒ 它出现在榜首，正说明**池内存在超紧巧合**，也正是必须做全体核验的理由。")
P()
P("D3. 两条蒙特卡洛零假设（V-sharp 子池用于排除 2/3）")
rows_s = [r for r in rows if r[6]]
best_s = rows_s[0]
rng = np.random.default_rng(7)
NMC = 40000
allvals = np.unique(np.round([f(V) for _, f, _ in ARITH for V in VPOOL], 12))
shvals = np.unique(np.round([f(V) for _, f, sh in ARITH if sh for V in VPOOL], 12))
b_all = np.empty(NMC)
b_sh = np.empty(NMC)
for i in range(NMC):
    t = 10.0 ** rng.uniform(math.log10(1e-3), math.log10(3.0), size=len(THETA))
    b_all[i] = (np.abs(allvals[:, None] - t[None, :]) / t[None, :]).min()
    b_sh[i] = (np.abs(shvals[:, None] - t[None, :]) / t[None, :]).min()
p_all = float(np.mean(b_all <= rows[0][0]))
p_sh = float(np.mean(b_sh <= best_s[0]))
P("    去重后：全池值 %d 个；V-sharp 子池 %d 个" % (len(allvals), len(shvals)))
P("    (a) 全池最小偏差 %.5f%%（%s, V=%d, %s）"
  % (100 * rows[0][0], rows[0][1], rows[0][2], rows[0][4]))
P("    (b) **V-sharp 子池**最小偏差 %.5f%%（%s, V=%d, %s）"
  % (100 * best_s[0], best_s[1], best_s[2], best_s[4]))
P("    零假设：Θ 各项是**同量级的随机无量纲数**（log-uniform 于 [1e−3, 3]）；MC %d 次。" % NMC)
P("      (a) 中位 %.4f%%，5%% 分位 %.4f%% ⇒ **p = %.3f**"
  % (100 * np.median(b_all), 100 * np.percentile(b_all, 5), p_all))
P("      (b) 中位 %.4f%%，5%% 分位 %.4f%% ⇒ **p = %.3f**"
  % (100 * np.median(b_sh), 100 * np.percentile(b_sh, 5), p_sh))
P("    判读：(a) 的 p 很小但**完全由 2/3↔Koide 这一已知假桥贡献**，不构成证据；")
P("          (b) 排除 V-blind 项后 p = %.3f。" % p_sh)
NIND = 8
b_sh2 = np.empty(NMC)
for i in range(NMC):
    t = 10.0 ** rng.uniform(math.log10(1e-3), math.log10(3.0), size=NIND)
    b_sh2[i] = (np.abs(shvals[:, None] - t[None, :]) / t[None, :]).min()
p_sh2 = float(np.mean(b_sh2 <= best_s[0]))
P("          (c) **稳健性**：Θ 内部并不独立（μ(³H)、μ(³He)、μ(³H)/μ_p、μ(³He)/μ_p 互为复合），")
P("              故把目标数从 13 降到 %d（只留互不复合者）重做 MC：" % NIND)
P("              p = %.3f ⇒ **p 值主要受『有效独立目标数』支配，不是稳健量**。" % p_sh2)
P()

P("D4. 三次「律」检验（决定性）")
P("    一个『锚』必须是一个**律**，不是一次数值巧合。形式化：")
P("      律的形态必然是 μ_X/μ_N = c·F(X)（c 为单位，非自由参数）")
P("      ⇒ 对任意 X,Y 必有 **μ_X/μ_Y = F(X)/F(Y)**（**零自由参数**）")
P("      ⇒ 候选 F 必须在**全家族**上同时成立。")
P()
STRUCTS = [
    ("p",   Y3("a", "p"),  MU_P,    1, 1),
    ("n",   Y3("b", "n"),  MU_N,    0, 1),
    ("d",   assemble([("d", [("a", "p"), ("b", "n")])])[0], MU_D, 1, 2),
    ("³H",  assemble([("t", [("a", "p"), ("b", "n"), ("c", "n")])])[0], MU_T3, 1, 3),
    ("³He", assemble([("t", [("a", "p"), ("b", "p"), ("c", "n")])])[0], MU_H3, 2, 3),
    ("⁴He", assemble([("l", [("a", "p"), ("b", "p"), ("c", "n"), ("e", "n")])])[0], MU_HE4, 2, 4),
]
sinfo = {}
P("    结构集（实测 μ/μ_N 与图不变量）：")
P()
P("    %-6s %-12s %-16s %s" % ("结构", "μ/μ_N", "账本(#p, A)", "图不变量"))
P("    " + "-" * 92)
for nm, G, mu, zp, A in STRUCTS:
    d = inv(G, True)
    sinfo[nm] = (d, abs(mu), zp, A)
    P("    %-6s %-12.6f %-16s %s" % (nm, mu, "(%d, %d)" % (zp, A), fmt_inv(d)))
P()
P("D4a. **图论阻塞**（与统计无关的结构性结论）")
P()
GD = {nm: G for nm, G, *_ in STRUCTS}
iso = nx.is_isomorphic(GD["³H"], GD["³He"])
P("    ³H 与 ³He 是否同构？**%s**" % ("是" if iso else "否"))
P("    二者账本：³H=(#p=1, A=3) 有一条**双开**共享环边；³He=(#p=2, A=3) 只有**单开**。")
P("    但图的**边集**相同（三体的边集 = 各体边集之并）⇒ 图层面完全一致。")
P("    ⇒ **任何图泛函 F 都给 F(³H) = F(³He)** ⇒ 预言 |μ(³H)|/|μ(³He)| = 1。")
obs = abs(MU_T3 / MU_H3)
P("      实测 |μ(³H)|/|μ(³He)| = %.6f ；偏差 %.2f%% —— **每一个**图泛函律都差同样多。"
  % (obs, 100 * abs(1.0 - obs) / obs))
P("      同理 (p,p) ≅ (p,n)（§9）：d 与「n-n 假想体」不可分。")
P("    ⇒ **结论：μ 族不可能由『图泛函』承载。它只能是『账本泛函』。**")
P("      这与 §9「产物图不记得伙伴态 ⇒ 只能由账本承载」是同一结论的第二次出现。")
P()
P("D4b. 账本**符号趋势**：sign(μ) 与 #p 奇偶")
P()
P("    实测符号：p(+) n(−) d(+) ³H(+) ³He(−)；另 ⁴He(#p=2, A=4) μ = 0（奇偶律给不出『零』）。")
zw = [(nm, zp, A, mu) for nm, G, mu, zp, A in STRUCTS if mu != 0]
n_ok = 0
for nm, zp, A, mu in zw:
    pred = "+" if zp % 2 == 1 else "−"
    real = "+" if mu > 0 else "−"
    ok = (pred == real)
    n_ok += ok
    P("      %-5s #p=%d(%s) A=%d ⇒ 律预言 %s ；实测 %s  %s"
      % (nm, zp, "奇" if zp % 2 else "偶", A, pred, real, "√" if ok else "×"))
P("    ⇒ **A≤4 范围内 5/5 成立**。")
P()
P("    ⚠ 但必须立刻做**外部样本证伪**（项目纪律：断言前先实测；不许拿 5 点当律）：")
EXT = [("¹H", 1, +2.792847), ("²H", 1, +0.857438), ("³H", 1, +2.978962),
       ("³He", 2, -2.127625), ("⁶Li", 3, +0.822047), ("⁷Li", 3, +3.256424),
       ("⁹Be", 4, -1.177432), ("¹¹B", 5, +2.688649), ("¹³C", 6, +0.702412),
       ("¹⁴N", 7, +0.571000), ("¹⁵N", 7, -0.283189), ("¹⁷O", 8, -1.893790),
       ("¹⁹F", 9, +2.628868), ("²³Na", 11, +2.217520), ("²⁷Al", 13, +3.641507),
       ("³¹P", 15, +1.131600)]
bad = []
for nm, Z, mu in EXT:
    pred = 1 if Z % 2 == 1 else -1
    if pred * mu < 0:
        bad.append((nm, Z, mu))
P("      在 %d 个真实核上重测「sign(μ) = (−1)^{Z+1}」：命中 %d / %d"
  % (len(EXT), len(EXT) - len(bad), len(EXT)))
for nm, Z, mu in bad:
    P("        反例：%s（Z=%d，%s）μ = %+.6f ⇒ 预言符号 %s，实测相反"
      % (nm, Z, "奇" if Z % 2 else "偶", mu, "+" if Z % 2 else "−"))
P("      ⇒ 该「律」在 **A≥13 立即失效**（¹³C、¹⁵N）。")
P("      它是**统计趋势**（14/16 = 87.5%，非 50%）而**不是零参数律**。")
P("      ⇒ **不得登记为锚**；只能登记为『账本能承载符号差异』这一**定性**事实。")
P("      同时注意 **⁴He（#p=2, A=4）μ = 0**：奇偶律只给符号、给不出'零'，")
P("      故幅度侧仍需独立条件 —— 这正是缺口所在。")
P()
P("D4c. 账本**幅度律**：比值检验")
P()

LEDF = [
    ("#p",            lambda zp, A: float(zp)),
    ("A",             lambda zp, A: float(A)),
    ("#n = A−#p",     lambda zp, A: float(A - zp)),
    ("A−2#p = #n−#p", lambda zp, A: float(A - 2 * zp)),
    ("2#p",           lambda zp, A: float(2 * zp)),
    ("ψ(#p)",         lambda zp, A: PSI.get(zp, float("nan"))),
    ("ψ(#p)+2ψ(A)",   lambda zp, A: PSI.get(zp, float("nan")) + 2 * PSI.get(A, float("nan"))),
]
ACT = ["p", "n", "d", "³H", "³He"]
pairs = [(x, y) for i, x in enumerate(ACT) for y in ACT[i + 1:]]
P("    账本泛函 F ∈ {%s}；在 %d 个结构对上做零参数比值检验（容差 1%%）："
  % (", ".join(n for n, _ in LEDF), len(pairs)))
P()
P("    %-18s %-22s %-11s %s" % ("F", "最差的一对", "最差偏差", "通过数(≤1%)"))
P("    " + "-" * 92)
res = []
for fname, f in LEDF:
    worst, wp, npass, nt = 0.0, "", 0, 0
    for x, y in pairs:
        zx, ax = sinfo[x][2], sinfo[x][3]
        zy, ay = sinfo[y][2], sinfo[y][3]
        vx, vy = f(zx, ax), f(zy, ay)
        if not np.isfinite(vx) or not np.isfinite(vy) or vy == 0 or vx == 0:
            continue
        nt += 1
        pred = vx / vy
        o = sinfo[x][1] / sinfo[y][1]
        dv = abs(pred - o) / o
        if dv < 0.01:
            npass += 1
        if dv > worst:
            worst, wp = dv, "%s/%s" % (x, y)
    res.append((npass, worst, fname, wp, nt))
res.sort(key=lambda z: (-z[0], z[1]))
for npass, worst, fname, wp, nt in res:
    P("    %-18s %-22s %-11.3f%% %d / %d" % (fname, wp or "—", 100 * worst, npass, nt))
P()
P("    ⇒ **没有任何账本泛函通过全部配对**；最好者通过 %d / %d。"
  % (res[0][0], res[0][4]))
P()
P("    针对性检验（把头号 V-sharp 命中放进『律』的框架）：")
P("      命中：β₁(o)/β₁(c)|_{V=12} = 6/7 = 0.857143 ↔ μ_d/μ_N = 0.857438（偏 0.034%）")
P("      若它是律，则同一读法须同时给出 μ_p、μ_n。三条最自然的『β₁ 型』读法：")
for nm, expr in [("β₁(X)/V(X)", "7/12=0.5833（p）、6/12=0.5（n）"),
                 ("β₁(X)/β₁(p)", "7/7=1（p）、6/7=0.857（n）"),
                 ("β₁(X)/β₁(d)", "7/13=0.538（p）、6/13=0.462（n）")]:
    P("        %-14s → %s" % (nm, expr))
P("      实测 μ_p/μ_N = 2.7928、|μ_n/μ_N| = 1.9130：三条读法都只给 O(1) 量级，")
P("      相差 3~5 倍 ⇒ **『6/7 ↔ μ_d』无法嵌入任何自洽的 β₁ 律，是孤立命中。**")
P()
P("D5. 判定")
P("    · **第二锚：尚未找到。** μ 族是唯一合格候选集；最强 V-sharp 单点命中偏 %.4f%%"
  % (100 * best_s[0]))
P("      （V-sharp 子池 MC p = %.3f / %.3f，随有效独立目标数在 0.04~0.2 间摆动 ⇒ 只算**边际**），"
  % (p_sh, p_sh2))
P("      且 **D4a 结构性证明**：该命中连『图泛函律』都不可能存在（³H ≅ ³He ⇒ 任何图泛函")
P("      都预言 |μ(³H)|/|μ(³He)| = 1，实测 1.4001）。")
P("      ⇒ 统计上的边际显著 + 结构上的必败 ⇒ **合起来判为巧合**。")
P("    · 但本轮把它的**形状锁死**为两条必要条件：")
P("      ① 必须定义在**账本层**（图泛函层已被 D4a 结构性封死）；")
P("      ② 必须能在**全家族**上以零自由参数复现（D4b/D4c 的检验形式）。")
P("    · 副产品（真正的正结果）：**符号侧有内容** ——「sign(μ) 随 #p 奇偶翻转」在")
P("      A≤4 上 5/5；外部样本把它降级为**趋势（14/16）而非律**。这是一次")
P("      「先发现、再自我证伪」的完整闭环，也是项目首次把「巧合 vs 律」做成可执行检验。")

# ============================================================
head("PART E  交叉约束汇总与三条待办的归并")
# ============================================================
P("E1. V 的候选集在四道约束下的收缩")
P()
P("    %-4s %-42s %s" % ("步", "约束", "V 候选集"))
P("    " + "-" * 92)
P("    %-4s %-42s %s" % ("0", "起点（论文 §7.6）", "连续可调"))
P("    %-4s %-42s %s" % ("1", "β₁ = V/2+1 为整数（3-正则恒等）", "{6,8,10,12,14,16,18}"))
P("    %-4s %-42s %s" % ("2", "α 锁：Π₁(Y₃) 落在族内，ε = 3%", "{8,10,12,14}"))
P("    %-4s %-42s %s" % ("3", "再加判据③ 3‖|Aut|（ε = 3%）", "{10,12}  ← 前一轮结论"))
E2 = sorted(V for V in (8, 10, 12, 14, 16) if SURV[V][0.005])
P("    %-4s %-42s %s" % ("4", "**本轮**：ε ≤ 1% + 判据③（不用新锚）",
                            "{%s}" % ",".join(map(str, E2))))
_s12 = [i for i, a in hit12 if _d12(i)["T"] >= 2]
P("    %-4s %-42s %s" % ("4′", "**本轮**：再追加 T ≥ 2（判据⑤ 同型）",
                            "档内唯一：V=12, %s" % ("Y₃ 骨架" if len(_s12) == 1 else "见 B3′")))
P("    %-4s %-42s %s" % ("5", "（第二锚：须为账本层算术律）", "仍待机制，见 D4/D5"))
P()
P("E2. 三句结论")
P("    ① **不用第二锚，V 也能收窄到 {12}** —— 只需把判据② 的窗宽从 3% 收到 ≤1%，")
P("       使其与 α 锁自身的吻合精度（0.165%）同量级。前一轮登记的「V=12 不唯一」")
P("       （论文 v1.6 §7.6 限定）**可以撤销**，条件是同时写明窗宽及其理由。")
P("       ⚠ **但「V=12」不等于「已定出 Y₃」**：V=12 档内 ε 收到 0.2% 仍有 2 个候选")
P("         共享同一 Π₁（Y₃ 与一个 T=1、|Aut|=12 的图）⇒ Π₁ 是**比值量**，")
P("         收紧 ε **在原理上**分不开它们；必须叠加非谱判据（T ≥ 2，§4 判据⑤ 同型）。")
P("    ② **第二锚尚未找到，且已证明它不能在『图泛函层』存在**（D4a）；")
P("       它若存在必在**账本层**、且必须通过**家族律检验**。")
P("       『加一个锚』不如『把窗宽收到与锚精度同量级』有效 —— 后者已足。")
P("    ③ **三条待办是同一条缺失**：")
P("       · ② 拉丁方：**离散同构类 → 连续 CKM 角**")
P("       · ① 轻子　：**代指标 → (n,w) 权重**")
P("       · 锚点　　：**整数 β₁ → 实测无量纲比**")
P("       ⇒ SRE 缺的不是数据、也不是方程，而是「**整数不变量 → 实数测量值**」的")
P("         赋值/量子化规则。三条待办是该缺失在三个层上的同一投影。")
P()
P("E3. 边界（诚实登记）")
P("    · PART B 的 V=14/16 为抽样（140 / 70；全集 509 / 4060），V=8/10/12 为**全集**")
P("      （5 / 19 / 85，均与已知连通立方图数一致）。故「V=12 唯一」对 V≤12 是")
P("      **精确**的，对 V≥14 只是 p ≲ 0.7% / 1.4% 的**界**。")
P("    · **完备性核验**（`_enum_cubic12.py`）：对 V=12 用 2-switch 闭包 BFS 穷举出")
P("      **85 个同构类 = 85 个不同 Laplacian 谱**（无共谱对）⇒ 本脚本的「谱签名去重」")
P("      在 V=12 档无损；但该去重在 V≥14 **未必**无损，故 V≥14 的 p 应读作上界。")
P("    · PART D3 的 MC 零假设用 log-uniform[1e−3, 3]；换抽样分布会改 p 值 ⇒")
P("      p 值只应读作**量级判据**。且 Θ 各项**不独立**（μ(³H)、μ(³He)、μ(³H)/μ_p、")
P("      μ(³He)/μ_p 互为复合）⇒ 有效独立目标数在 8~13 之间，p 随之为 0.04~0.2。")
P("      **真正决定 D5 的是 D4a（与分布无关）**，不是 p 值。")
P("    · PART D4a 的同构判定用边集并的装配规则；若改装配规则，结论须重测。")
P("    · PART D4b 的外部样本取自标准核磁矩表；若样例选择有偏，趋势比例会变，")
P("      但**反例的存在**足以否定「零参数律」这一结论（反例不受样例规模影响）。")
P("    · 本轮未引入任何新物理假设；μ 族的 A2（图泛函对应）已被 D4a **判否**。")
P()
P("DONE")
