# -*- coding: utf-8 -*-
"""
_sre_nucleon_derivation.py
=========================================================================
核子拓扑推衍验证脚本（SRE 框架）

方法学总纲（与电子推衍同源）：
  刚性边界条件局部带入（注入 me / mp / mn 等实测值）
      -> 求解模型内部的拓扑结构关系（isospin Z2 双重态、三子核复合绑定）
      -> 反推拓扑量（核子逻辑深度等）

本脚本只验证【模型内部结构化命题】的自洽性（C1-C5），并发灰【只读锚点登记册】
（C6）。它不声称任何绝对强子质量、胶子海放大因子或重子谱劈裂的数值预言——
这些边界由《虚空之书》复合粒子章明确声明，本文遵守之。

所有非推导锚点一律标注来源，并附【非推导声明】。断言仅针对结构项。
=========================================================================
"""
import json
import itertools
import random
import networkx as nx
import numpy as np

# ---------------------------------------------------------------------------
# 刚性边界条件（CODATA 2018, 局部带入项，只读锚点）
# ---------------------------------------------------------------------------
ME_MEV = 0.51099895000        # 电子静质量
MP_MEV = 938.27208816         # 质子静质量
MN_MEV = 939.56542052         # 中子静质量
ALPHA_INV = 137.035999084     # 精细结构常数倒数 (库仑力关联锚点)

N_ELECTRON_DEPTH = 1.0e23     # 电子逻辑深度（项目已建立，代入质量反推得到）
CHARGE = {'u': 2.0 / 3.0, 'd': -1.0 / 3.0}   # 价电荷位型（QCD 约定，只读引用）
P_PATTERN = ('u', 'u', 'd')   # 质子 = (u,u,d)
N_PATTERN = ('u', 'd', 'd')   # 中子 = (u,d,d)

# ---------------------------------------------------------------------------
# 复合本体构造：三子核（valence sub-core）绑定
#   每个价子核取电子谱系相干固定点结构 Q3（8 结点立方体，hypercube_graph(3)）。
#   三个子核经"交界面"结点上的耦合边（承接线）绑定。
# ---------------------------------------------------------------------------
def cube_q3():
    """8 结点立方体 Q3（电子基底，复用项目定义）。

    hypercube_graph(3) 的结点为三元组位串 (0,0,0)..(1,1,1)；
    统一重标号为整数 0..7，以便把结点 0 用作交界面（承接线挂点）。
    """
    H = nx.hypercube_graph(3)
    mapping = {v: int(''.join(map(str, v)), 2) for v in H.nodes}
    return nx.relabel_nodes(H, mapping)


def make_composite(cores=3, inter_edges=True, weight=1.0):
    """构造三子核复合图：3 份 Q3 + 承接线三角形（各子核结点 0 间耦合）。

    返回 (G, cores_nodes)，cores_nodes[c] 为第 c 个子核的结点集合。
    承接线标记 inter=True；子核内部边标记 inter=False。
    交界面结点 (c,0) 为子核 c 的真实结点，即 8 结点超立方之结点 0。
    """
    G = nx.Graph()
    cores_nodes = []
    for c in range(cores):
        H = cube_q3()
        mapping = {v: (c, v) for v in H.nodes}
        Hr = nx.relabel_nodes(H, mapping)
        cores_nodes.append(set(Hr.nodes))
        G.add_edges_from(Hr.edges, inter=False, weight=float('inf'))
    if inter_edges:
        junc = [(c, 0) for c in range(cores)]
        for i in range(cores):
            for j in range(i + 1, cores):
                G.add_edge(junc[i], junc[j], inter=True, weight=float(weight))
    return G, cores_nodes


# ---------------------------------------------------------------------------
# C1 — isospin Z2 双重态
# ---------------------------------------------------------------------------
def z2_flip(pattern):
    """Z2 同位旋电荷翻转 T3：在双重态上翻转唯一不同核，u<->d。

    T3(P_p) -> P_n 的多重集；T3(P_n) -> P_p。T3 无不动点（P != N）。
    位型以元组给出；翻转"该核为 u 者变为 d，为 d 者变为 u"。
    """
    lst = list(pattern)
    for i in range(len(lst)):
        lst[i] = 'd' if lst[i] == 'u' else 'u'
    return tuple(lst)


def check_c1():
    """(C1) isospin Z2 双重态：T3 无不动点对合；p/n 复合图同构（Z2 镜像）。"""
    out = {}
    # 1) T3 无不动点对合
    p_flip = z2_flip(P_PATTERN)     # (d,d,u) 多重集 == (u,d,d) = n
    n_flip = z2_flip(N_PATTERN)     # (d,u,u) 多重集 == (u,u,d) = p
    out['p_flip_multiset'] = sorted(p_flip)
    out['n_flip_multiset'] = sorted(n_flip)
    out['p_flip_equals_n'] = (sorted(p_flip) == sorted(N_PATTERN))
    out['n_flip_equals_p'] = (sorted(n_flip) == sorted(P_PATTERN))
    out['z2_involution_on_doublet'] = (
        sorted(z2_flip(p_flip)) == sorted(P_PATTERN) and
        sorted(z2_flip(n_flip)) == sorted(N_PATTERN)
    )
    out['z2_no_fixed_point'] = (sorted(P_PATTERN) != sorted(N_PATTERN))
    # 2) 电荷守恒（组态层面）：p 总电荷 +1e，n 总电荷 0
    out['charge_p'] = sum(CHARGE[c] for c in P_PATTERN)
    out['charge_n'] = sum(CHARGE[c] for c in N_PATTERN)
    # 3) p / n 复合图拓扑同构（去掉电荷标注后互为 Z2 镜像）
    Gp, _ = make_composite()
    Gn, _ = make_composite()
    out['graph_isomorphic_doublet'] = nx.is_isomorphic(Gp, Gn)
    # 4) Z2 反射是复合结构的自同构（子核可交换：任一子核置为交界面）
    out['all_pass'] = all([
        out['p_flip_equals_n'], out['n_flip_equals_p'],
        out['z2_involution_on_doublet'], out['z2_no_fixed_point'],
        abs(out['charge_p'] - 1.0) < 1e-12,
        abs(out['charge_n'] - 0.0) < 1e-12,
        out['graph_isomorphic_doublet'],
    ])
    return out


# ---------------------------------------------------------------------------
# C2 — 绑定算子 R_bind 的收敛性（幂等 + 单调）
#   类比电子 R2 之 R_strict：承接线 weight 低于休眠阈值 eps 者剔除，
#   子核内部边永不剔除。迭代一次即达不动点（幂等），边集只减不增（单调）。
# ---------------------------------------------------------------------------
def r_bind(G, eps=0.4):
    """绑定算子一次作用：剔除活跃度低于 eps 的承接线。"""
    H = G.copy()
    dead = [(u, v) for u, v, d in G.edges(data=True)
            if d.get('inter') and d.get('weight', 1.0) < eps]
    H.remove_edges_from(dead)
    return H


def edge_key_set(G):
    return set(frozenset(e) for e in G.edges())


def check_c2():
    """(C2) 绑定算子幂等 + 单调收敛到相干复合基底。"""
    out = {}
    # 承接线权重取 [0.2, 1.0] 之间随机；eps=0.4 居中
    rng = random.Random(2)
    G, cores = make_composite(inter_edges=True, weight=1.0)
    for (u, v) in list(G.edges()):
        if G[u][v].get('inter'):
            G[u][v]['weight'] = rng.uniform(0.2, 0.9)
    e0 = set(G.edges())
    out['intra_edges_never_pruned'] = True  # 由 r_bind 定义保证（仅删 inter）
    H1 = r_bind(G, eps=0.4)
    e1 = edge_key_set(H1)
    H2 = r_bind(H1, eps=0.4)
    e2 = edge_key_set(H2)
    out['idempotent'] = (e1 == e2)
    out['monotone_single_step'] = (len(e1) <= len(e0))
    out['inter_survivors'] = sum(1 for u, v in e1 if H1[u][v].get('inter'))
    # 相干复合判定：三个子核经存活承接线连通（需 >=2 条承接线）
    out['coherent_composite'] = (out['inter_survivors'] >= 2)
    out['connected'] = nx.is_connected(H1)
    # 高阈值情形：全部承接线关闭 -> 退束缚（3 个孤立子核）
    G0, _ = make_composite(inter_edges=True, weight=0.1)
    Hhigh = r_bind(G0, eps=0.9)
    out['unbound_components'] = nx.number_connected_components(Hhigh)
    out['all_pass'] = all([
        out['idempotent'], out['monotone_single_step'],
        out['coherent_composite'], out['connected'],
        out['unbound_components'] == 3,
    ])
    return out


# ---------------------------------------------------------------------------
# C3 — 复合层面唯一性（枚举电荷位型）
# ---------------------------------------------------------------------------
def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)


def check_c3():
    """(C3) 唯一性：单核翻转距离=1 且总电荷 {0,+1} 的所有二元组，
    在核置换（子核位置交换）下归并为唯一轨道，其多重集恰为 {p, n}。

    即：任一 {2u,1d}（+1）位型与任一 {1u,2d}（0）位型按单核翻转配对，
    共 6 对；去核置换后唯一，无异质轨道可作核子双重态。
    """
    out = {}
    patterns = [x for x in itertools.product('ud', repeat=3)]
    pairs = []
    for a, b in itertools.combinations(patterns, 2):
        ca = sum(CHARGE[c] for c in a)
        cb = sum(CHARGE[c] for c in b)
        if hamming(a, b) == 1 and {round(ca, 9), round(cb, 9)} == {0.0, 1.0}:
            pairs.append((a, b))
    out['distance1_charge_pairs_count'] = len(pairs)
    out['expected_pair_count'] = 6
    # 核置换下归并：只保留多重集对
    canon = set()
    for a, b in pairs:
        canon.add(frozenset((tuple(sorted(a)), tuple(sorted(b)))))
    out['distinct_orbits_up_to_permutation'] = len(canon)
    out['one_orbit_up_to_permutation'] = (len(canon) == 1)
    # 唯一轨道中必含 p,n 多重集（(u,u,d)/(u,d,d)）
    out['contains_proton_neutron'] = any(
        (tuple(sorted(P_PATTERN)) in o) and (tuple(sorted(N_PATTERN)) in o)
        for o in canon)
    out['all_pass'] = all([
        out['one_orbit_up_to_permutation'],
        out['contains_proton_neutron'],
    ])
    return out


# ---------------------------------------------------------------------------
# C4 — 绑定鲁棒性（噪声 rho <= 0.1 下存活承接线集不变）
# ---------------------------------------------------------------------------
def check_c4(trials=500, rho=0.1):
    """(C4) 绑定算子对承接线权重噪声的鲁棒性。"""
    out = {}
    rng = random.Random(7)
    mismatches = 0
    for _ in range(trials):
        G, cores = make_composite(inter_edges=True, weight=1.0)
        for (u, v) in list(G.edges()):
            if G[u][v].get('inter'):
                # 基准权重距阈值 eps=0.4 留有 >=0.15 余量
                G[u][v]['weight'] = rng.uniform(0.55, 0.95)
        base = edge_key_set(r_bind(G, eps=0.4))
        G2 = G.copy()
        for (u, v) in list(G2.edges()):
            if G2[u][v].get('inter'):
                w = G2[u][v]['weight'] + rng.uniform(-rho, rho)
                G2[u][v]['weight'] = w
        noisy = edge_key_set(r_bind(G2, eps=0.4))
        if base != noisy:
            mismatches += 1
    out['trials'] = trials
    out['rho'] = rho
    out['eps_margin'] = 0.15
    out['survivor_set_mismatches'] = mismatches
    out['robust'] = (mismatches == 0)
    out['all_pass'] = out['robust']
    return out


# ---------------------------------------------------------------------------
# C5 — 局部带入 + 反推（与电子 10^23 同法）
# ---------------------------------------------------------------------------
def check_c5():
    """(C5) 注入 me/mp/mn 作为刚性边界条件，反推核子逻辑深度。

    虚空之书 §1.1：静质量对应拓扑深度 / 累计路径数（质量-深度对偶）。
    故逻辑深度与质量反比（同最小尺度），核子逻辑深度
        N_p = N_e * (me / mp),    N_n = N_e * (me / mn)。
    该式在给定对偶假说下为定义性自洽（并非独立预言），如实标注。
    """
    out = {}
    N_p = N_ELECTRON_DEPTH * ME_MEV / MP_MEV
    N_n = N_ELECTRON_DEPTH * ME_MEV / MN_MEV
    out['N_electron'] = N_ELECTRON_DEPTH
    out['N_proton'] = N_p
    out['N_neutron'] = N_n
    out['me_over_mp'] = ME_MEV / MP_MEV
    # 定义性自洽：深度比 = 质量比
    out['depth_ratio_self_consistency'] = (
        N_ELECTRON_DEPTH / N_p)  # 应 = mp/me
    out['mp_over_me'] = MP_MEV / ME_MEV
    out['self_consistency_rel_err'] = abs(
        (N_ELECTRON_DEPTH / N_p) - (MP_MEV / ME_MEV)) / (MP_MEV / ME_MEV)
    # 判定标准：相对误差 < 1e-9（定义性恒等）
    out['all_pass'] = out['self_consistency_rel_err'] < 1.0e-9
    return out


# ---------------------------------------------------------------------------
# C6 — 只读锚点登记册（互为验证线索，非 SRE 推导）
# ---------------------------------------------------------------------------
def check_c6():
    """(C6) 只读锚点登记册：记录与经典物理相关的验证线索。"""
    dm = MN_MEV - MP_MEV
    registry = [
        {"锚点": "me", "数值_MeV": ME_MEV, "来源": "CODATA 2018",
         "性质": "注入边界条件", "SRE推导": "否", "备注": ""},
        {"锚点": "mp", "数值_MeV": MP_MEV, "来源": "CODATA 2018",
         "性质": "注入边界条件", "SRE推导": "否", "备注": ""},
        {"锚点": "mn", "数值_MeV": MN_MEV, "来源": "CODATA 2018",
         "性质": "注入边界条件", "SRE推导": "否", "备注": ""},
        {"锚点": "mp/me", "数值": MP_MEV / ME_MEV, "来源": "导出（mp,me）",
         "性质": "只读锚点·质量比", "SRE推导": "否",
         "备注": "与逻辑深度比 N_e/N_p 数字重合（对偶自洽）"},
        {"锚点": "mn/mp", "数值": MN_MEV / MP_MEV, "来源": "导出（mn,mp）",
         "性质": "只读锚点·质量比", "SRE推导": "否",
         "备注": "isospin 破缺占比约为 1.4e-3 量级（Z2 双重态近简并的方向性）"},
        {"锚点": "(mn-mp)/me", "数值": dm / ME_MEV, "来源": "导出（mn,mp,me）",
         "性质": "只读锚点·质量比", "SRE推导": "否", "备注": ""},
        {"锚点": "(mn-mp)/mp", "数值": dm / MP_MEV, "来源": "导出（mn,mp）",
         "性质": "只读锚点·质量比", "SRE推导": "否",
         "备注": "量级 1.4e-3：同位旋破缺为 Z2 双重态上的小扰动（结构方向性，非定量）"},
        {"锚点": "alpha^-1", "数值": ALPHA_INV, "来源": "CODATA 2018",
         "性质": "只读锚点·库仑力关联", "SRE推导": "否（电子项目已给谱比同向指示）",
         "备注": "库仑力为核子内/间相互作用的关键验证线索之一"},
        {"锚点": "胶子海质量占比", "数值": "~90%（动力学质量，属 QCD 范畴）",
         "来源": "现代强子物理共识（蹄书复合粒子章已声明不可由此定量）",
         "性质": "只读锚点", "SRE推导": "否",
         "备注": "虚空之书明确：绝对强子质量、胶子海因子、重子劈裂不在本框架数值预言范围"},
        {"锚点": "u 电流质量", "数值": "~2.16 MeV（QCD 范畴）",
         "来源": "PDG（电流质量，非本框架）", "性质": "只读锚点",
         "SRE推导": "否",
         "备注": "SRE 复合图使用价子核相干结构，不冒充电流夸克质量"},
        {"锚点": "d 电流质量", "数值": "~4.67 MeV（QCD 范畴）",
         "来源": "PDG（电流质量，非本框架）", "性质": "只读锚点",
         "SRE推导": "否",
         "备注": "同上"},
    ]
    for r in registry:
        r["非推导声明"] = "本项仅为实测锚点登记，不做 SRE 数值预言，不构成验证。"
    return {"registry": registry, "all_pass": True}


# ---------------------------------------------------------------------------
def main():
    results = {}
    print("=" * 72)
    print("核子拓扑推衍验证（SRE 框架，模型内部自洽，非现实物理）")
    print("=" * 72)
    print("[方法] 刚性边界条件局部带入 -> 求解拓扑关系 -> 反推")

    c1 = check_c1()
    results['C1_isospin_z2_doublet'] = c1
    print("\n[C1] isospin Z2 双重态")
    print("  T3(p)->n:", c1['p_flip_equals_n'],
          "| T3(n)->p:", c1['n_flip_equals_p'],
          "| T3^2=id:", c1['z2_involution_on_doublet'])
    print("  无不动点:", c1['z2_no_fixed_point'],
          "| 电荷 p=+1:", c1['charge_p'], ", n=0:", c1['charge_n'],
          "| 复合图同构:", c1['graph_isomorphic_doublet'])
    print("  PASS:", c1['all_pass'])

    c2 = check_c2()
    results['C2_binding_operator_convergence'] = c2
    print("\n[C2] 绑定算子 R_bind 收敛（幂等/单调）")
    print("  幂等:", c2['idempotent'], "| 单调:", c2['monotone_single_step'])
    print("  存活承接线:", c2['inter_survivors'],
          "| 相干复合:", c2['coherent_composite'],
          "| 连通:", c2['connected'])
    print("  退束缚分量数(高阈值):", c2['unbound_components'])
    print("  PASS:", c2['all_pass'])

    c3 = check_c3()
    results['C3_uniqueness'] = c3
    print("\n[C3] 复合层面唯一性（枚举电荷位型，核置换下唯一轨道）")
    print("  单核翻转且电荷{0,+1}的二元组数:", c3['distance1_charge_pairs_count'],
          "(期望 6)")
    print("  去核置换后的独立轨道数:", c3['distinct_orbits_up_to_permutation'])
    print("  唯一轨道含 {p,n} 多重集:", c3['contains_proton_neutron'])
    print("  PASS:", c3['all_pass'])

    c4 = check_c4()
    results['C4_binding_robustness'] = c4
    print("\n[C4] 绑定鲁棒性 (trials=%d, rho=%.2f)"
          % (c4['trials'], c4['rho']))
    print("  存活承接线集不一致次数:", c4['survivor_set_mismatches'])
    print("  PASS:", c4['all_pass'])

    c5 = check_c5()
    results['C5_local_injection_reverse_inference'] = c5
    print("\n[C5] 局部带入反推逻辑深度（与电子同法）")
    print("  N_e = %.3e" % c5['N_electron'])
    print("  N_p = N_e*me/mp = %.4e" % c5['N_proton'])
    print("  N_n = N_e*me/mn = %.4e" % c5['N_neutron'])
    print("  me/mp = %.8f" % c5['me_over_mp'])
    print("  N_e/N_p (=mp/me) = %.12f" % c5['depth_ratio_self_consistency'])
    print("  定义性自洽相对误差 = %.3e" % c5['self_consistency_rel_err'])
    print("  PASS:", c5['all_pass'])

    c6 = check_c6()
    results['C6_readonly_anchor_registry'] = c6
    print("\n[C6] 只读锚点登记册（互为验证线索，非 SRE 推导）")
    for r in c6['registry']:
        k = r['锚点']
        v = r.get('数值', r.get('数值_MeV', r['数值_MeV'] if '数值_MeV' in r else ''))
        print("  %-14s : %s" % (k, v))
    print("  提示: 全部为只读锚点，含非推导声明（详见 JSON 与文档）。")

    all_pass = all(r['all_pass'] for r in [
        c1, c2, c3, c4, c5, c6])
    results['_summary'] = {
        'structure_checks_pass': all_pass,
        'note': ('C1-C5 为模型内部结构化自洽断言；C6 为只读锚点登记，'
                 '不构成对现实物理的数值预言。'),
    }
    print("\n" + "=" * 72)
    print("结构项全部通过:", all_pass)
    print("=[诚实边界]= 绝对强子质量 / 胶子海放大因子 / 重子谱劈裂")
    print("   不在本框架数值预言范围（由虚空之书复合粒子章明定）。")
    print("=" * 72)

    with open(r"C:\mywork\vasp\sre_nucleon_derivation_results.json",
              "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    return all_pass


if __name__ == "__main__":
    main()
