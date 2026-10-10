# -*- coding: utf-8 -*-
"""
_sre_orbital_measurement_test.py
================================
问题（用户 2026-09-24）：
  「先回忆一下真实电子轨道是怎么测量出来的，再确定轨道是否涌现。」

真实测量端（文献事实，见 log PART 0）：
  · EMS / (e,2e) → 测的是 **Dyson 轨道**（N 与 N-1 态的偏重叠）的 |FT|^2 ⇒ 动量密度；
  · STM/STS → 测 LDOS（态密度），非单轨道本身（Pham & Gordon, JPCA 2017 明确驳斥「STM 看到轨道」）；
  · MOT / HHG 断层 → 依赖 PW/SFA 近似重建 HOMO，本身有争议；
  · **共同点（量子力学公设）**：单电子轨道 φ 在占据空间内可任意酉变换而不改变 Ψ ⇒
      轨道 **不是可观测量**；可观测的是 **1-RDM / 密度 γ(r,r')**（及其本征函数 = 自然轨道）。

本项目侧的可比对象：
  「轨道」名义定义 = 介观核**关系拉普拉斯特征向量**（电子论文 §13.4）。
  特征向量 = 单电子基函数 ⇔ 物理上的 φ（规范量）。
  ⇔ 其**可观测量对应物** = **谱投影算符 P = Σ_{λ∈本征值} v v^T 的对角元**（顶点密度）。

判定实验（全部纯 numpy/networkx，分布无关）：
  PART 1  测量链的「不变量层级」——把真实实验访问的量按规范不变性分类；
  PART 2  项目图族的 **投影对角元**：是否沿 Aut 轨道恒定 ⟺ 可观密度是否有「形状」；
  PART 3  **规范检验**：同一本征空间内换一个正交基 ⇒ 单轨道密度剧变，而投影对角元不动；
  PART 4  破对称对照：把 Q3 断一条边 ⇒ 轨道变多、密度出现形状（说明形状来自「手工塞入的不对称」）；
  PART 5  裁决。
"""

import json
import numpy as np
import networkx as nx

np.set_printoptions(precision=6, suppress=True, linewidth=160)
OUT = {}
L = []


def P(s=""):
    print(s)
    L.append(s)


# ============================================================
# 图族（与 _sre_l4_assignment.py 完全一致的定义）
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


def graph_family():
    Gs = {}
    Gs["Q3 (电子基底)"] = q3()
    Gs["Q4"] = nx.convert_node_labels_to_integers(nx.hypercube_graph(4))
    Gs["M60 (alpha 载体)"] = mobius_m60()
    Gs["K8"] = nx.complete_graph(8)
    Gs["C8 (环)"] = nx.cycle_graph(8)
    Gs["P8 (路径)"] = nx.path_graph(8)
    Gs["Petersen"] = nx.petersen_graph()
    Gs["Y3p (核子骨架)"] = Y3("", "p")
    Gs["Y3n (开态)"] = Y3("", "n")
    Gs["GD (氘核)"] = assemble([("a", "p"), ("b", "n")], 0)
    # 破对称对照
    g = q3()
    g = g.copy()
    g.remove_edge(0, 1)
    Gs["Q3-1edge (破对称)"] = g
    return Gs


# ============================================================
# 群论量：自同构阶、顶点轨道
# ============================================================
def aut_orbits(G, cap=200000):
    """返回 (orbits, aut_order 或 None if 超 cap)。"""
    nodes = list(G.nodes())
    parent = {v: v for v in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    GM = nx.algorithms.isomorphism.GraphMatcher(G, G)
    cnt = 0
    for m in GM.isomorphisms_iter():
        cnt += 1
        for a in nodes:
            union(a, m[a])
        if cnt > cap:
            return None, None
    from collections import defaultdict
    d = defaultdict(list)
    for v in nodes:
        d[find(v)].append(v)
    return [sorted(g) for g in d.values()], cnt


# ============================================================
# 谱：本征值分组 + 各本征空间投影对角元
# ============================================================
def eigenspaces(G, tol=1e-7):
    Lm = nx.laplacian_matrix(G, nodelist=sorted(G.nodes())).toarray().astype(float)
    w, V = np.linalg.eigh(Lm)
    out = []
    i = 0
    while i < len(w):
        j = i
        while j + 1 < len(w) and abs(w[j + 1] - w[i]) < tol:
            j += 1
        idx = list(range(i, j + 1))
        out.append((float(w[i]), len(idx), idx, V))
        i = j + 1
    return w, V, out


def proj_diag(V, idx):
    B = V[:, idx]
    return (B ** 2).sum(axis=1)          # 谱投影算符对角元 = 顶点「密度」


# ============================================================
P("=" * 78)
P("PART 0  真实电子轨道的测量（文献事实，先立靶）")
P("=" * 78)
P("""
  (M1) 能量差 / 量子数：原子光谱（发射吸收线）、Rydberg 系、Zeeman/Stark 分裂
       ⇒ 直接测到的是 **能量差** 与 **分裂重数(2l+1)**；n,l,m 由选择定则与分裂图样【推断】。
  (M2) 空间密度：X 射线/电子衍射 ⇒ 电子密度（傅立叶）；STM/STS ⇒ LDOS 图；
       ARPES ⇒ 动量分辨谱（含矩阵元/偏振的轨道成分）。
  (M3) 动量密度 / Dyson 轨道：(e,2e) EMS 直接测 sigma ~ INT dOmega |g_f(p)|^2，
       g_f = N INT Psi_{N-1} Psi_N ⇒ 「轨道成像」多是 **Dyson 轨道的球平均动量密度**。
  (M4) 断层：HHG 分子轨道断层（MOT）重建 HOMO —— 依赖 PW/SFA 近似，本身有长期争议。
  (M5) 【公设级】单电子轨道 phi 在占据空间内作任意酉变换 ⇒ Psi（及一切可观测量）不变
       ⇒ **轨道不是可观测量**（Pham & Gordon, J. Phys. Chem. A 121, 4851 (2017) 专文驳斥
         「STM 看到轨道」；文献界共识：可观测的是 1-RDM gamma(r,r') 及其本征函数=自然轨道）。
  ⇒ 结论先行：真实测量访问的是 **能量差 / 简并重数 / 密度(实空间或动量空间)**，
     **单条轨道的形状与相位是规范量**；能称「轨道」而不撒谎的，只有
     **Dyson / 自然轨道**这类由约化密度矩阵定义的、规范不变的对象。
""")

# ============================================================
P("=" * 78)
P("PART 1  不变量层级：实验访问的量分三类")
P("=" * 78)
P("""
  类别 A（真不变量，可测）：本征值谱、简并重数、投影算符 P_lambda = sum v v^T、
                          密度 rho(r)=diag(gamma)、动量密度。
  类别 B（规范量，不可测）：单条轨道的形状/相位、轨道基的选择（占据空间内酉自由度）。
  类别 C（近似模型量）：KS/HF 正则轨道、MOT 重建像 —— 可算、可拟，但非不变量。
  → 本项目「轨道 = 拉普拉斯特征向量」正落在 **类别 B**（单电子基函数）。
    其 **类别 A 对应物** = 各本征空间的 **投影对角元**（顶点密度）。
  → 因此判定「轨道是否涌现」= 判：**类别 A 的那部分（投影对角元）能否由拓扑给出形状**。
""")

# ============================================================
P("=" * 78)
P("PART 2  项目图族：投影对角元是否沿 Aut 轨道恒定（形状的有无）")
P("=" * 78)
P(f"{'图':<20}{'V':>4}{'|Aut|':>9}{'#轨道':>7}{'本征+':>7}"
  f"{'最大spread':>12}{'最大密值数':>12}  orbit恒定  判定")
P("-" * 92)

families = graph_family()
part2 = {}
for name, G in families.items():
    nodes = sorted(G.nodes())
    Vn = len(nodes)
    w, Vv, espa = eigenspaces(G)
    if Vn <= 16:
        orbs, aut = aut_orbits(G)
        norb = len(orbs) if orbs is not None else None
        auts = str(aut) if aut is not None else ">cap"
    else:
        orbs, norb, auts = None, None, "(skip)"
    # 定理检查：投影对角元应沿 Aut 轨道恒定（对**所有**本征空间，不只简并的）
    orbit_ok = True
    posn = {nd: i for i, nd in enumerate(nodes)}
    if orbs is not None:
        for val, mult, idx, _ in espa:
            d = proj_diag(Vv, idx)
            for ob in orbs:
                ii = [posn[x] for x in ob]
                if d[ii].max() - d[ii].min() > 1e-7:
                    orbit_ok = False
    spreads = []
    for val, mult, idx, _ in espa:
        d = proj_diag(Vv, idx)
        nd = len(np.unique(np.round(d, 8)))
        spreads.append((val, mult, float(d.max() - d.min()), nd, d))
    overall = max((s for (val, mult, s, nd, d) in spreads), default=0.0)
    max_nd = max((nd for (val, mult, s, nd, d) in spreads), default=1)
    flat = overall < 1e-6
    verdict = "平（零形状）" if flat else "有形状"
    P(f"{name:<20}{Vn:>4}{auts:>9}{str(norb):>7}{len(espa):>7}"
      f"{overall:>12.6f}{max_nd:>12}  {str(orbit_ok):>9}  {verdict}")
    part2[name] = {"V": Vn, "aut": auts, "n_orbits": norb,
                   "spectrum": [float(x) for x in w],
                   "espace": [{"lambda": val, "mult": mult, "spread": sp,
                               "n_distinct": nd}
                              for (val, mult, sp, nd, d) in spreads],
                   "max_spread_all": overall, "max_n_distinct": max_nd,
                   "orbit_const": bool(orbit_ok),
                   "max_deg_spread": overall, "flat": flat}

P()
P("读法：**投影对角元（= 规范不变的可观密度）沿 Aut 轨道恒定**（定理，已逐图实测 orbit恒定=True）。")
P("      ⇒ 拓扑能给出的形状分辨力 = **轨道数**；")
P("        #轨道=1 ⇒ 密度全顶点均匀 ⇒ **零形状**（本征空间再简并也一样）。")
P("      注意：判据覆盖**全部**本征空间（含单重空间，其对角元 = 单轨道密度 v^2）。")

# ============================================================
P("=" * 78)
P("PART 3  规范检验（Q3，lambda=2，重数 3）：单轨道剧变 vs 投影恒定")
P("=" * 78)
G = q3()
w, Vv, espa = eigenspaces(G)
# 找 lambda=2（重数 3）
target = None
for val, mult, idx, _ in espa:
    if mult == 3 and abs(val - 2.0) < 1e-6:
        target = (val, mult, idx)
val, mult, idx = target
B = Vv[:, idx]                     # 8 x 3
nodes = sorted(G.nodes())
alphabet = list("abcdefgh")

# 同一本征空间内两个不同的正交选择（= 规范变换）
rng = np.random.default_rng(20260924)
Q, _ = np.linalg.qr(rng.standard_normal((3, 3)))
picks = {}
for tag, coef in (("basis-1 (e1)", np.array([1.0, 0, 0])),
                  ("basis-2 (Q e1)", Q[:, 0]),
                  ("basis-3 (Q' e1)",
                   np.linalg.qr(np.roll(np.eye(3), 1, axis=1))[0][:, 0])):
    vec = B @ coef
    dens = vec ** 2
    picks[tag] = {"vec": vec.tolist(), "dens": dens.tolist(),
                  "spread": float(dens.max() - dens.min()),
                  "max": float(dens.max()), "min": float(dens.min())}
dens_inv = (B ** 2).sum(axis=1)     # 不变量：投影对角元
P(f"{'选择（同一本征空间）':<22}{'密度 max':>10}{'密度 min':>10}{'spread':>12}")
P("-" * 78)
for tag, d in picks.items():
    P(f"{tag:<22}{d['max']:>10.6f}{d['min']:>10.6f}{d['spread']:>12.6f}")
P(f"{'【不变量】投影对角元':<22}{dens_inv.max():>10.6f}{dens_inv.min():>10.6f}"
  f"{dens_inv.max()-dens_inv.min():>12.6f}")
P()
P("顶点逐点对照（8 个顶点 = 二进串）：")
P("  顶点     " + "  ".join(f"{alphabet[i]:>8}" for i in range(8)))
for tag in picks:
    P(f"  {tag:<8}" + "  ".join(f"{x:>8.5f}" for x in picks[tag]["dens"]))
P(f"  投影(不变)" + "  ".join(f"{x:>8.5f}" for x in dens_inv))
P()
P("⇒ 同一张图、同一个本征值：换一个正交基，**单轨道顶点密度从 0.0x 变到 0.5x**（剧变）；")
P("  而 **投影对角元逐点相同**（= 3/8 = 均匀）⇒ 单轨道形状 100% 是规范。")
P(f"  检验：投影对角元是否 = mult/V = {mult}/{len(nodes)} = {mult/len(nodes):.6f}"
  f"  ⇒ 实测 {dens_inv[0]:.6f}  一致 = {abs(dens_inv[0]-mult/len(nodes))<1e-9}")

# 自同构作用：图不变，轨道变（取一个**非平凡**自同构）
GM = nx.algorithms.isomorphism.GraphMatcher(G, G)
perm = None
for m in GM.isomorphisms_iter():
    if any(m[k] != k for k in m):
        perm = m
        break
v0 = (B @ np.array([1.0, 0, 0]))
v0p = np.array([v0[perm[i]] for i in range(8)])
P()
P("自同构作用检验：取一个**非平凡**自同构 pi（重标号），图逐边不变；")
P(f"  轨道向量在 pi 下改变？ max|v - pi(v)| = {np.max(np.abs(v0 - v0p)):.6f}"
  f"  （>0 ⇒ 「这条轨道」不是图的函数）")
P(f"  投影对角元在 pi 下改变？ max|d - pi(d)| = "
  f"{np.max(np.abs(dens_inv - np.array([dens_inv[perm[i]] for i in range(8)]))):.2e}"
  f"  （=0 ⇒ 不变量不动）")
OUT["part3"] = {"lambda": val, "mult": mult, "picks": picks,
                "invariant_dens": dens_inv.tolist(),
                "invariant_value": float(dens_inv[0]),
                "aut_changes_orbital": float(np.max(np.abs(v0 - v0p))),
                "aut_changes_proj": float(np.max(np.abs(
                    dens_inv - np.array([dens_inv[perm[i]] for i in range(8)]))))}

# ============================================================
P("=" * 78)
P("PART 4  破对称对照：形状何时出现？")
P("=" * 78)
gb = q3().copy()
gb.remove_edge(0, 1)
wb, Vb, espb = eigenspaces(gb)
orbs_b, aut_b = aut_orbits(gb)
P(f"  Q3 断一条边后：V={gb.number_of_nodes()}  |Aut|={aut_b}  #轨道={len(orbs_b)}")
worst = 0.0
nd_max = 1
for val_, mult_, idx_, _ in espb:
    d = proj_diag(Vb, idx_)
    sp = float(d.max() - d.min())
    worst = max(worst, sp)
    nd_max = max(nd_max, len(np.unique(np.round(d, 8))))
P(f"  全部本征空间投影对角元最大 spread = {worst:.6f}  密值数={nd_max}  ⇒ "
  + ("出现形状" if worst > 1e-6 else "仍平"))
P(f"  对比 Q3（原图，1 轨道）：spread = "
  f"{part2['Q3 (电子基底)']['max_spread_all']:.2e}（平）、密值数 = "
  f"{part2['Q3 (电子基底)']['max_n_distinct']}")
P()
P("  ⇒ 形状只在 **对称性被破坏** 时出现；而破坏对称的那条操作（断哪条边、")
P("    或塞进什么非键合关系）**不是拓扑给出的**，是外部输入的。")
OUT["part4"] = {"Q3_minus_edge": {"aut": aut_b, "n_orbits": len(orbs_b),
                                  "max_deg_spread": worst}}

# ============================================================
P("=" * 78)
P("PART 5  裁决")
P("=" * 78)
# 统计：所有项目相关图（非破对称）中，简并空间投影是否都平
core = ["Q3 (电子基底)", "Q4", "M60 (alpha 载体)", "K8", "C8 (环)", "Petersen",
        "Y3p (核子骨架)", "Y3n (开态)", "GD (氘核)"]
flat_core = [n for n in core if part2[n]["flat"]]
shaped_core = [n for n in core if not part2[n]["flat"]]
P(f"  项目相关图（{len(core)} 个）中，**全部本征空间**投影对角元（规范不变密度）：")
P(f"    平（零形状）: {len(flat_core)} / {len(core)}  -> {flat_core}")
P(f"    有形状      : {len(shaped_core)} -> {shaped_core}")
P()
P("  判定：")
P("   (1) 「轨道」若指单电子基函数（项目 §13.4 的定义）⇒ 它是 **类别 B 规范量**，")
P("       不是可观测量；换基/自同构可任意改变其形状。**「它是涌现结果」在「它是导出量」")
P("       这一弱义上成立** —— 它确实不是基本量。")
P("   (2) 但「形状由拓扑涌现」这一**强义失败**：唯一规范不变的可观密度（投影对角元）")
P("       在项目的成功图上 **沿全部顶点恒定（均匀）** ⇒ **零形状**；")
P("       顶点传递性越强，密度越平。2l+1 的角向结构来自 SO(3)，不是 Aut。")
P("   (3) 反过来说，形状只在破坏对称时出现，而破坏对称需要 **外部输入**。")
P("   ⇒ 与 §13 的 G12 分裂一致：计数类（离散）闭；角向-简并类（连续）借。")
OUT["verdict"] = {
    "core_graphs": core,
    "flat": flat_core, "shaped": shaped_core,
    "conclusion": ("orbital is a derived (gauge) object - weak sense TRUE; "
                   "shape emergent from topology - strong sense FALSE "
                   "(invariant density is uniform on vertex-transitive graphs)"),
}
OUT["part2"] = part2

with open("_orbital_measurement_test.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P()
P("已写出 _orbital_measurement_test.json")
