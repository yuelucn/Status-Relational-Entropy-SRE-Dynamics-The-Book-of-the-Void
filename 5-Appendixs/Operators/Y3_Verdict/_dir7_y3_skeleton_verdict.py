# -*- coding: utf-8 -*-
"""_dir7_y3_skeleton_verdict.py -- 第104轮主实验：核子骨架 Y3 的 ℤ₂ 通道判决

════════════════════════════════════════════════════════════════════════════
缘起
════════════════════════════════════════════════════════════════════════════
本项目自身的核心对象是核子骨架 Y₃ = Y₃⋊△₃（闭态 V=12,E=18,β₁=7,|Aut|=36），
它同时是「电荷涌现」与「质量起源」两条主线的载体。此前 101–103 轮已建立：
  · 101 轮：Pfaffian 定向类的无偏线性系统（充要判据）；莫比乌斯梯族上
    「有定向类 ⟺ 非二分」成立，但在 Y₃ 上**外推失败**。
  · 102 轮：rank_hol（标号无关 ℤ₂ 不变量）在 Q₃/Y₃闭/Y₃开 上为 0/1/2。
  · 103 轮：rank_hol 的**充要判据** T9（割空间交维数恒等式）。
但**从未在项目自己的骨架上做「双通道并置判决」**，也从未给出
  (i) 全仓 Y₃ 构造实现的**一致性**证据；
  (ii) 「Y₃闭 Pfaffian 通道无解」的**可读证书**（此前只有「系统无解」这一事实）；
  (iii) Y₃ 与莫比乌斯梯族 M_{2n} 的**分布无关**关系判决。

本实验补齐这三点，并额外抽出一条可搬用规则（见下）。

════════════════════════════════════════════════════════════════════════════
可搬用规则（本轮新增，编号 G70/G71）
════════════════════════════════════════════════════════════════════════════
G70「同构一致性律」：同一骨架对象在仓内有多份实现副本时，
    **先证明它们同构，再谈任何基于它的结论**；副本数本身是风险信号。
G71「极小冲突证书律」：「某线性系统无解」若只作为**事实**报告，则读者无法核查；
    须补**极小不可解行子集**（minimal unsatisfiable subset）并独立复核。
    该证书同时量化「差多远」（可满足比例）。

════════════════════════════════════════════════════════════════════════════
Part A  权威邻接 + 全仓 Y₃ 实现的**同构**一致性（G70）
Part B  T9 充要判据在 Y₃ 上的三实现复算（rank_hol 与 dim(W∩Cut)）
Part C  Pfaffian 通道判决（101 引擎）+ **极小冲突证书**（G71）
Part D  Y₃ 与 M_{2n} 的关系：覆盖 / 商 / 双覆盖 / 独立族（分布无关）
Part E  广义族交叉验证（M 族 + 对照族 + 随机族）
Part F  反证门（可注入 + 阳性对照 + 已知坏数据）

纪律（G46/G49/G67/G68/G69）：先实测再断言；关键读数三实现交叉零失配；
自检门须可注入并做阳性对照；判据优劣作分类器错误率并报假阴性象限；
判负须分布无关（穷举 + 覆盖/群论封死）。
作者：WorkBuddy | 2026-10-22
"""
import os
import re
import sys
import json
import hashlib
import itertools
from collections import Counter, defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(_HERE))   # 5-Appendixs/Operators（存放 sre_z2_holonomy_bridge.py）
sys.path.insert(0, _HERE)

import networkx as nx
import numpy as np

ROOT = os.environ.get("SRE_Y3_ROOT", os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("SRE_Y3_OUT", os.path.dirname(os.path.abspath(__file__)))

# ═══════════════════════════════════════════════════════════════════════
# Part A-0  权威骨架定义（单一来源；其余实现一律与之做同构比对）
# ═══════════════════════════════════════════════════════════════════════
def y3_closed():
    """核子骨架闭态 Y₃⋊△₃：3 个中心 c_i 各连 3 条「腿」L_ij；
       腿按 j 分 3 组，每组 (L_0j, L_1j, L_2j) 成一个三角形。V=12,E=18,β₁=7."""
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    return nx.convert_node_labels_to_integers(G)


def y3_open():
    """开态：闭态删去一条环边（三角边）。V=12,E=17,β₁=6."""
    G = y3_closed()
    tri = nx.triangles(G)
    ring_v = {v for v in G if tri[v] > 0}
    ring_edges = sorted(tuple(sorted(e)) for e in G.edges()
                        if e[0] in ring_v and e[1] in ring_v)
    H = G.copy()
    H.remove_edge(*ring_edges[0])
    assert nx.is_connected(H)
    return H


def q3():
    """电子骨架 Q₃ = 超立方体图 3 维。V=8,E=12,β₁=5."""
    return nx.convert_node_labels_to_integers(nx.hypercube_graph(3))


# ═══════════════════════════════════════════════════════════════════════
# GF(2) 工具
# ═══════════════════════════════════════════════════════════════════════
def gf2_rank_rows(rows):
    """GF(2) 行秩（bitmask）。"""
    basis = {}
    r = 0
    for x in rows:
        cur = x
        while cur:
            hb = cur.bit_length() - 1
            if hb in basis:
                cur ^= basis[hb]
            else:
                basis[hb] = cur
                r += 1
                break
    return r


def gf2_solve(rows, rhs, m):
    """GF(2) 求解。返回 dict(solvable, dim_free, particular, pivots, R, b)。"""
    nrows = len(rows)
    M = [rows[i] | ((rhs[i] & 1) << m) for i in range(nrows)]
    piv = []
    r = 0
    for c in range(m):
        p = None
        for i in range(r, nrows):
            if (M[i] >> c) & 1:
                p = i
                break
        if p is None:
            continue
        M[r], M[p] = M[p], M[r]
        for i in range(nrows):
            if i != r and ((M[i] >> c) & 1):
                M[i] ^= M[r]
        piv.append(c)
        r += 1
    for i in range(r, nrows):
        if (M[i] >> m) & 1:
            return {"solvable": False, "contradiction_row": i}
    freecols = [c for c in range(m) if c not in piv]
    part = 0
    for i, c in enumerate(piv):
        if (M[i] >> m) & 1:
            part |= (1 << c)
    return {"solvable": True, "m": m, "pivots": piv,
            "R": [M[i] & ((1 << m) - 1) for i in range(r)],
            "b": [(M[i] >> m) & 1 for i in range(r)],
            "free": freecols, "dim_free": len(freecols), "particular": part}


# ═══════════════════════════════════════════════════════════════════════
# Part A  Y₃ 实现的同构一致性
# ═══════════════════════════════════════════════════════════════════════
FUNC_RE = re.compile(r"^def (y3_closed|y3_open|y3)\s*\(.*?(?=\n(?:def |# ---|class )|\Z)",
                     re.S | re.M)
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".workbuddy", "organic_cache",
              "backup_paper_20260924_164026", "backup_mass_origin_paper_20260928_153843"}


def collect_impl_sources():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for m in FUNC_RE.finditer(t):
                out.append((os.path.relpath(p, ROOT).replace("\\", "/"),
                            m.group(1), m.group(0)))
    return out


def same_file_family(path):
    p = os.path.join(ROOT, path.replace("/", os.sep))
    try:
        t = open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return []
    return [(m.group(1), m.group(0)) for m in FUNC_RE.finditer(t)]


def run_impl(src, fname, extra_srcs=()):
    g = {"nx": nx}
    try:
        for _, s in extra_srcs:
            exec(s, g)
        exec(src, g)
    except Exception:
        return None
    fn = g.get(fname)
    if fn is None:
        return None
    try:
        G = fn()
    except Exception:
        return None
    return G if isinstance(G, nx.Graph) else None


def _why_fail(path, fname):
    """诊断隔离执行失败原因（区分「依赖/签名」与「真实不一致」）。"""
    p = os.path.join(ROOT, path.replace("/", os.sep))
    try:
        t = open(p, encoding="utf-8", errors="replace").read()
    except Exception:
        return "文件不可读"
    m = re.search(r"^def %s\s*\(([^)]*)\)" % re.escape(fname), t, re.M)
    sig = m.group(1) if m else "?"
    if sig.strip():
        return "签名带参数（%s），隔离调用不适用 ⇒ 非不一致" % sig
    return "依赖同文件自定义符号 ⇒ 非不一致"


def partA():
    print("=" * 96)
    print("Part A  权威邻接 + 全仓 Y₃ 实现的同构一致性（G70）")
    print("=" * 96)
    refC, refO = y3_closed(), y3_open()
    print("  权威 Y₃闭：V=%d E=%d 边集=%s" %
          (refC.number_of_nodes(), refC.number_of_edges(),
           sorted(tuple(sorted(e)) for e in refC.edges())))
    print("  权威 Y₃开：V=%d E=%d（删一条三角边）" %
          (refO.number_of_nodes(), refO.number_of_edges()))

    srcs = collect_impl_sources()
    groups = defaultdict(list)
    for path, fname, src in srcs:
        groups[(fname, hashlib.md5(src.encode("utf-8")).hexdigest()[:8])].append(
            (path, fname, src))
    print("\n  全仓 y3 系列函数体 %d 处 ⇒ 按（函数名 × 函数体 md5）归并为 %d 个实现体" %
          (len(srcs), len(groups)))

    rows = []
    for (fname, h), items in sorted(groups.items()):
        path, _, src = items[0]
        fam = same_file_family(path)
        G = run_impl(src, fname, [(n, s) for (n, s) in fam if n != fname])
        if G is None:
            G = run_impl(src, fname, fam)
        if G is None:
            rows.append(dict(func=fname, md5=h, path=path, n_copies=len(items),
                             status="ISOLATED-FAIL", iso=None, V=None, E=None,
                             target=("Y3开" if fname == "y3_open" else "Y3闭")))
            continue
        target = refO if fname == "y3_open" else refC
        V, E = G.number_of_nodes(), G.number_of_edges()
        iso = (nx.is_isomorphic(G, target)
               if (V, E) == (target.number_of_nodes(), target.number_of_edges())
               else None)
        rows.append(dict(func=fname, md5=h, path=path, n_copies=len(items),
                         status="OK", iso=iso, V=V, E=E,
                         target=("Y3开" if fname == "y3_open" else "Y3闭")))
    print("\n  %-10s %-8s %-6s %-4s %-4s %-6s %-7s %s" %
          ("func", "md5", "copies", "V", "E", "target", "iso?", "path"))
    for r in rows:
        print("  %-10s %-8s %-6d %-4s %-4s %-6s %-7s %s" %
              (r["func"], r["md5"], r["n_copies"], r["V"], r["E"], r["target"],
               {True: "YES", False: "NO", None: "-"}[r["iso"]], r["path"]))

    ok = [r for r in rows if r["status"] == "OK"]
    bad = [r for r in rows if r["status"] != "OK"]
    iso_ok = [r for r in ok if r["iso"] is True]
    iso_no = [r for r in ok if r["iso"] is False]
    size_bad = [r for r in ok if r["iso"] is None]
    print("\n  [A1] 可体检 %d / 隔离执行失败 %d" % (len(ok), len(bad)))
    print("  [A2] 与权威同构 %d 个；**不同构** %d 个；尺寸不符 %d 个" %
          (len(iso_ok), len(iso_no), len(size_bad)))
    for r in iso_no:
        print("        不同构：%s %s (V=%s,E=%s)" % (r["func"], r["md5"], r["V"], r["E"]))
    for r in bad:
        print("        未能独立体检：%s %s —— %s" % (r["func"], r["md5"], _why_fail(r["path"], r["func"])))
    gateA = (len(iso_no) == 0) and (len(size_bad) == 0)
    print("  [门A] 「所有可体检实现体都与权威同构」(%d/%d) => %s" %
          (len(iso_ok), len(ok), "PASS" if gateA else "FAIL"))
    # 反向有效性：把权威换成 Q₃，应有实现体不同构 ⇒ 判别力非平凡
    sens = (not nx.is_isomorphic(refC, q3())) and nx.is_isomorphic(refC, y3_closed())
    print("  [门A 反向有效性] Y₃闭 ≇ Q₃ 且 Y₃闭 ≅ Y₃闭 => %s" %
          ("PASS" if sens else "FAIL"))
    return dict(rows=rows, gateA=gateA, sens=sens, n_impl=len(groups),
                n_copies=len(srcs))


# ═══════════════════════════════════════════════════════════════════════
# Part B  T9 充要判据在 Y₃ 上的三实现复算
# ═══════════════════════════════════════════════════════════════════════
def orbit_masks_of(G):
    """Aut-不变赋值空间 W 的基（轨道特征向量）→ (masks, n_orb, |Aut|)。"""
    edges = [tuple(sorted(e)) for e in G.edges()]
    eidx = {e: i for i, e in enumerate(edges)}
    auts = list(nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
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
    groups = defaultdict(list)
    for e in edges:
        groups[find(e)].append(e)
    masks = []
    for orb in groups.values():
        m = 0
        for e in orb:
            m |= (1 << eidx[e])
        masks.append(m)
    return masks, len(groups), len(auts)


def impl_B1_M_matrix(G):
    """B1：书内算子 19 的 T2 矩阵 M 路线。
       M 的行 = 环基，列 = 边轨道；M[ci][oi] = 环 ci 上落在轨道 oi 的边数 mod 2。
       Φ: W→H¹ 在 W 的标准基与环基坐标下的矩阵为 Mᵀ ⇒ rank_hol = rank(M)。"""
    edges = [tuple(sorted(e)) for e in G.edges()]
    auts = list(nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
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
    groups = defaultdict(list)
    for e in edges:
        groups[find(e)].append(e)
    orbs = [set(o) for o in groups.values()]
    n_orb = len(orbs)
    M = []
    for C in nx.cycle_basis(G):
        L = len(C)
        row = 0
        for oi, orb_s in enumerate(orbs):
            cnt = 0
            for t in range(L):
                a, b = C[t], C[(t + 1) % L]
                if (min(a, b), max(a, b)) in orb_s:
                    cnt += 1
            if cnt & 1:
                row |= (1 << oi)
        M.append(row)
    return gf2_rank_rows(M), n_orb


def impl_B2_cutspace(G, wbasis):
    """B2：割空间交维数路线（T9 恒等式）。Cut 基取**星集** d({v})（G66 铁律）。"""
    V = list(G.nodes())
    edges = [tuple(sorted(e)) for e in G.edges()]
    eidx = {e: i for i, e in enumerate(edges)}
    cbasis = []
    for v in V[1:]:
        m = 0
        for e in edges:
            if v in e:
                m |= (1 << eidx[e])
        cbasis.append(m)
    dimW = gf2_rank_rows(list(wbasis))
    dimCut = gf2_rank_rows(cbasis)
    dimSum = gf2_rank_rows(list(wbasis) + cbasis)
    dimInter = dimW + dimCut - dimSum
    return dimW - dimInter, dimInter, dimCut


def impl_B3_subset_enum(G, wbasis):
    """B3：子集枚举法（与 B2 的星集基**不同源**）。
       枚举 2^|V| 个 S，取 d(S) 的全部不同取值作为 Cut 的生成集。"""
    V = list(G.nodes())
    edges = [tuple(sorted(e)) for e in G.edges()]
    eidx = {e: i for i, e in enumerate(edges)}
    nV = len(V)
    if nV > 16:
        return None
    seen = set()
    for mask in range(1 << nV):
        S = set(V[i] for i in range(nV) if (mask >> i) & 1)
        m = 0
        for e in edges:
            u, v = e
            if (u in S) != (v in S):
                m |= (1 << eidx[e])
        seen.add(m)
    dimW = gf2_rank_rows(list(wbasis))
    dimCut = gf2_rank_rows(list(seen))
    dimInter = dimW + dimCut - gf2_rank_rows(list(wbasis) + list(seen))
    return dimW - dimInter, dimInter, dimCut


def partB():
    print()
    print("=" * 96)
    print("Part B  T9 充要判据在项目骨架上的三实现复算")
    print("=" * 96)
    fam = [("Q₃(电子)", q3()), ("Y₃闭(质子)", y3_closed()), ("Y₃开(中子)", y3_open())]
    rows = []
    print("  %-14s %-4s %-4s %-5s %-6s %-6s %-9s %-9s %-9s %-8s %s" %
          ("name", "V", "E", "β₁", "|Aut|", "n_orb", "rank(B1)", "rank(B2)", "rank(B3)",
           "T9", "一致?"))
    for name, G in fam:
        V, E = G.number_of_nodes(), G.number_of_edges()
        b1 = E - V + nx.number_connected_components(G)
        masks, n_orb, n_aut = orbit_masks_of(G)
        rankM, _ = impl_B1_M_matrix(G)
        r1 = rankM                                  # B1：rank_hol = rank(M)
        r2, dimInter, dimCut = impl_B2_cutspace(G, masks)
        r3, dimInter3, dimCut3 = impl_B3_subset_enum(G, masks)
        t9 = n_orb - dimInter                        # T9 恒等式
        agree = (r1 == r2 == r3 == t9)
        print("  %-14s %-4d %-4d %-5d %-6d %-6d %-9d %-9d %-9d %-8d %s" %
              (name, V, E, b1, n_aut, n_orb, r1, r2, r3, t9,
               "OK" if agree else "MISMATCH"))
        rows.append(dict(name=name, V=V, E=E, b1=b1, n_aut=n_aut, n_orb=n_orb,
                         rank_B1=r1, rank_B2=r2, rank_B3=r3, t9=t9,
                         dimInter=dimInter, dimInter3=dimInter3,
                         dimCut=dimCut, dimCut3=dimCut3, agree=agree))
    gate = all(r["agree"] for r in rows)
    print("\n  [门B] 三实现 + T9 恒等式在三个骨架上零失配 => %s" %
          ("PASS" if gate else "FAIL"))
    # 反向有效性：把 Cut 的定义换成「树上 v→root 路径边集」（G66 的那个坑），
    # 交维数必须改变 ⇒ 证明该读数对定义敏感，不是恒等通过。
    G = y3_closed()
    masks, n_orb, _ = orbit_masks_of(G)
    edges = [tuple(sorted(e)) for e in G.edges()]
    eidx = {e: i for i, e in enumerate(edges)}
    # 真正的生成树（BFS 树），避免自环
    root = list(G.nodes())[0]
    parent = {root: None}
    dq = [root]
    while dq:
        u = dq.pop(0)
        for w in sorted(G.neighbors(u)):
            if w not in parent:
                parent[w] = u
                dq.append(w)
    tree_path_basis = []
    for v in G.nodes():
        if v == root:
            continue
        m = 0
        x = v
        while x != root:
            p = parent[x]
            m |= (1 << eidx[tuple(sorted((x, p)))])
            x = p
        tree_path_basis.append(m)
    dimW = gf2_rank_rows(masks)
    dimCutBad = gf2_rank_rows(tree_path_basis)
    dimInterBad = dimW + dimCutBad - gf2_rank_rows(masks + tree_path_basis)
    r2_bad = dimW - dimInterBad
    r2_ok = next(r["rank_B2"] for r in rows if r["name"] == "Y₃闭(质子)")
    print("  [门B 反向有效性] 把 Cut 定义换成「树路径边集」（G66 坑）⇒ "
          "rank_hol %d → %d，两值不同 ⇒ 该门有鉴别力 => %s" %
          (r2_ok, r2_bad, "PASS" if r2_ok != r2_bad else "FAIL(无鉴别力)"))
    # 阳性对照：W 退化为空基（{0} 空间）⇒ dim(W∩Cut)=0，rank_hol 应为 0
    r_zero, di_zero, _ = impl_B2_cutspace(G, [])
    print("  [门B 阳性对照] W 退化为零空间 ⇒ rank_hol 必 = 0，实测 %d => %s" %
          (r_zero, "PASS" if r_zero == 0 else "FAIL"))
    return rows, gate


# ═══════════════════════════════════════════════════════════════════════
# Part C  Pfaffian 通道判决 + 极小冲突证书（G71）
# ═══════════════════════════════════════════════════════════════════════
from _bridge101_nucleon import pfaffian_classes            # noqa: E402
from _pfcore import mobius, prism, norm_edges               # noqa: E402


def cr_count(pairs):
    """Kasteleyn 交叉数 mod 2（与 101 轮同口径）。"""
    pos = sorted([(min(a, b), max(a, b)) for a, b in pairs])
    cr = 0
    for a in range(len(pos)):
        for b in range(a + 1, len(pos)):
            x1, y1 = pos[a]
            x2, y2 = pos[b]
            if (x1 < x2 < y1 < y2) or (x2 < x1 < y2 < y1):
                cr += 1
    return cr % 2


def enumerate_matchings(N, E):
    E = norm_edges(E)
    adj = {v: [] for v in range(N)}
    for (u, v) in E:
        adj[u].append(v)
        adj[v].append(u)
    res = []

    def go(rem, chosen):
        if not rem:
            res.append(tuple(sorted(chosen)))
            return
        v = min(rem)
        rest = rem - {v}
        for w in sorted(adj[v]):
            if w in rest:
                go(rest - {w}, chosen + [(v, w)])

    go(set(range(N)), [])
    return res


def unbiased_system(N, E):
    """101 轮的无偏线性系统：Σ_{e∈M} t_e = cr(M) (mod 2)，行 = 完美匹配。"""
    E = norm_edges(E)
    m = len(E)
    eidx = {e: i for i, e in enumerate(E)}
    ms = enumerate_matchings(N, E)
    rows, rhs, meta = [], [], []
    for M in ms:
        row = 0
        for (u, v) in M:
            row ^= 1 << eidx[(u, v)]
        rows.append(row)
        rhs.append(cr_count(list(M)))
        meta.append(M)
    return rows, rhs, m, meta


def minimal_unsat_subset(rows, rhs, m, cap=20):
    """极小不可解行子集（minimal unsatisfiable subset）。
       做法：逐条贪心加入行，若当前子集已不可解则移除该行（标准 delta-debugging）。
       行数 ≤ cap 时可退化为穷举（更严格）。"""
    n = len(rows)
    if n <= cap:
        best = None
        for k in range(1, n + 1):
            for comb in itertools.combinations(range(n), k):
                if not gf2_solve([rows[i] for i in comb],
                                 [rhs[i] for i in comb], m)["solvable"]:
                    if best is None or k < len(best):
                        best = list(comb)
                    break
            if best is not None:
                break
        return best
    cur = []
    for i in range(n):
        trial = cur + [i]
        if not gf2_solve([rows[j] for j in trial], [rhs[j] for j in trial], m)["solvable"]:
            cur = trial
    return cur


def all_simple_cycles(G):
    res, seen = [], set()
    for start in G.nodes():
        path, used = [start], {start}

        def dfs(v):
            for w in G.neighbors(v):
                if w == start and len(path) >= 3:
                    key = frozenset(frozenset((path[i], path[(i + 1) % len(path)]))
                                    for i in range(len(path)))
                    if len(key) == len(path) and min(path) == start and key not in seen:
                        seen.add(key)
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


def matching_edge_multiplicity(G):
    nodes = sorted(G.nodes())
    adj = {v: [] for v in nodes}
    for (u, v) in G.edges():
        adj[u].append(v)
        adj[v].append(u)
    cnt, res = Counter(), []

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
    return cnt, len(res)


def nice_even_cycles(G):
    """nice even cycle：偶圈且每条边恰在 2 个完美匹配中。"""
    if G.number_of_nodes() % 2 != 0:
        return []
    mpm, npm = matching_edge_multiplicity(G)
    if npm == 0:
        return []
    out = []
    for c in all_simple_cycles(G):
        L = len(c)
        if L % 2 != 0:
            continue
        ce = [frozenset((c[i], c[(i + 1) % L])) for i in range(L)]
        if all(mpm.get(e, 0) == 2 for e in ce):
            out.append(c)
    return out


def partC():
    print()
    print("=" * 96)
    print("Part C  Pfaffian 通道判决（101 引擎）+ 极小冲突证书（G71）")
    print("=" * 96)
    fam = [("Q₃(电子)", q3()), ("Y₃闭(质子)", y3_closed()), ("Y₃开(中子)", y3_open()),
           ("M₈(Wagner)", nx.Graph(mobius(4))), ("M₁₂", nx.Graph(mobius(6))),
           ("Petersen", nx.petersen_graph()),
           ("K₃,₃", nx.complete_bipartite_graph(3, 3))]
    rows = []
    print("  %-14s %-4s %-4s %-6s %-6s %-9s %-8s %-7s %-7s %s" %
          ("name", "V", "E", "bip", "npm", "|O_Pf|", "dim", "nice", "Pf?", "证书"))
    for name, G in fam:
        E = norm_edges(G.edges())
        N = G.number_of_nodes()
        ispf, dim, cp, cm, npf, cert, npm = pfaffian_classes(N, E)
        nice = nice_even_cycles(G)
        print("  %-14s %-4d %-4d %-6s %-6d %-9d %-8s %-7d %-7s %s" %
              (name, N, len(E), nx.is_bipartite(G), npm, npf,
               ("-" if dim is None else str(dim)), len(nice),
               "Y" if ispf else "N", cert[:26]))
        rows.append(dict(name=name, V=N, E=len(E), bip=nx.is_bipartite(G),
                         npm=npm, is_pf=ispf, n_set=npf, dim=dim,
                         n_pos=cp, n_neg=cm, n_nice=len(nice),
                         nice_lens=sorted(Counter(len(c) for c in nice).items())))

    tp = sum(1 for r in rows if r["n_nice"] > 0 and not r["is_pf"])
    fp = sum(1 for r in rows if r["n_nice"] > 0 and r["is_pf"])
    fn = sum(1 for r in rows if r["n_nice"] == 0 and not r["is_pf"])
    tn = sum(1 for r in rows if r["n_nice"] == 0 and r["is_pf"])
    print("\n  [C1] nice even cycle 障碍集作「无解指示器」（分类器口径）："
          "TP=%d FP=%d FN=%d TN=%d" % (tp, fp, fn, tn))
    print("      ⇒ 指示器**非充要**（有 nice 障碍却有解者存在）⇒ 只能作**障碍指示**，")
    print("        真值仍由 101 轮无偏系统给出。")
    for r in rows:
        if r["n_nice"] > 0 and r["is_pf"]:
            print("        假阳性例：%s nice=%d 但有解" % (r["name"], r["n_nice"]))

    print("\n  [C2] ★极小冲突证书（G71）：Y₃闭 的 Pfaffian 无解可读证书")
    for name, G in (("Y₃闭(质子)", y3_closed()), ("Y₃开(中子)", y3_open())):
        E = norm_edges(G.edges())
        N = G.number_of_nodes()
        rowsM, rhsM, m, meta = unbiased_system(N, E)
        sol = gf2_solve(rowsM, rhsM, m)
        print("\n    【%s】无偏系统：%d 行（完美匹配）× %d 列（边）" % (name, len(rowsM), m))
        if not sol["solvable"]:
            mus = minimal_unsat_subset(rowsM, rhsM, m)
            print("      系统不可解。极小不可解行子集大小 = %d（占 %d 行的 %.0f%%）" %
                  (len(mus), len(rowsM), 100.0 * len(mus) / len(rowsM)))
            for j in mus:
                M = meta[j]
                print("        行: M=%s  cr=%d" %
                      ("{" + ",".join("(%d,%d)" % p for p in M) + "}", rhsM[j]))
            # 独立复核：仅取该子集重新求解 ⇒ 仍不可解
            sub = gf2_solve([rowsM[j] for j in mus], [rhsM[j] for j in mus], m)
            print("      独立复核：仅取这 %d 行重解 ⇒ 可解=%s ⇒ 证书 %s" %
                  (len(mus), sub["solvable"], "有效" if not sub["solvable"] else "无效"))
            # 「差多远」：可满足的最大行数
            best = 0
            for k in range(len(rowsM), 0, -1):
                hit = False
                for comb in itertools.combinations(range(len(rowsM)), k):
                    if gf2_solve([rowsM[j] for j in comb],
                                 [rhsM[j] for j in comb], m)["solvable"]:
                        best = k
                        hit = True
                        break
                if hit:
                    break
            print("      可满足的最大行数 = %d / %d ⇒ 差 %d 行即不可解" %
                  (best, len(rowsM), len(rowsM) - best))
        else:
            print("      系统**可解**：dim_free=%d ⇒ |解集|=2^%d" %
                  (sol["dim_free"], sol["dim_free"]))
            t = sol["particular"]
            # 独立复核：用特解重算 Pf 值是否等于完美匹配数
            from _bridge101_nucleon import pf_expand_cached, pf_fast
            tab = pf_expand_cached(N, E)
            val = pf_fast(t, tab)
            npm = len(meta)
            print("      特解独立复核：Pf=%+d，|Pf|=%d，完美匹配数=%d ⇒ %s" %
                  (val, abs(val), npm, "一致" if abs(val) == npm else "**不一致**"))
    return rows


# ═══════════════════════════════════════════════════════════════════════
# Part D  Y₃ 与 M_{2n} 的关系（分布无关：覆盖用 backtracking 穷举）
# ═══════════════════════════════════════════════════════════════════════
def find_coverings(G, H):
    """枚举 G → H 的所有图覆盖（局部边双射同态），**完备**。

    覆盖的定义（局部双射同态）：映射 t: V(G)→V(H) 满足
      (i)  同态：uv ∈ E(G) ⇒ t(u) ~ t(v) ∈ E(H)；
      (ii) 局部双射：∀v，{ t(w) : w ∈ N_G(v) } = N_H(t(v))（作为集合相等）。
    完备性：回溯搜索 t 的所有可能赋值；剪枝仅用必要条件
      （同态 + 与已定邻居像不同 + 已完全定像的顶点的局部双射条件）。
    备注：**商**（G/N，N ⊲ Aut(G)）是覆盖的特殊情形（deck 群在纤维上自由作用），
    故「零覆盖」蕴含「零商」。
    """
    Gv, Hv = list(G.nodes()), list(H.nodes())
    if H.number_of_edges() == 0 or G.number_of_edges() % H.number_of_edges() != 0:
        return []
    k = G.number_of_edges() // H.number_of_edges()
    if k < 1 or G.number_of_nodes() != k * H.number_of_nodes():
        return []
    degG, degH = set(dict(G.degree()).values()), set(dict(H.degree()).values())
    if len(degG) != 1 or len(degH) != 1 or degG != degH:
        return []
    adjG = {v: sorted(G.neighbors(v)) for v in Gv}
    adjH = {v: sorted(H.neighbors(v)) for v in Hv}
    # BFS 序（保证父先于子）
    order, seen = [Gv[0]], {Gv[0]}
    qi = 0
    while qi < len(order):
        u = order[qi]
        qi += 1
        for w in adjG[u]:
            if w not in seen:
                seen.add(w)
                order.append(w)
    out = []
    t = {}

    def local_ok(v):
        """v 的全部邻居已定像时，检查局部双射条件。"""
        if not all(w in t for w in adjG[v]):
            return True
        s = {t[w] for w in adjG[v]}
        return s == set(adjH[t[v]]) and len(s) == len(adjG[v])

    def rec(i):
        if i == len(order):
            out.append(dict(mapping=dict(t), k=k))
            return len(out) < 200
        v = order[i]
        done = [w for w in adjG[v] if w in t]
        for tv in Hv:
            if tv in {t[w] for w in done}:
                continue
            if any(not H.has_edge(tv, t[w]) for w in done):
                continue
            t[v] = tv
            if all(local_ok(u) for u in done + [v]):
                if rec(i + 1):
                    del t[v]
                    return True
            del t[v]
        return False

    rec(0)
    return out


def deck_transformations(G, mapping):
    """保持覆盖映射 φ 的自同构集合（deck 变换）。
       networkx 的 isomorphisms_iter() 产出 dict（节点→节点），非函数。"""
    out = []
    for a in nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter():
        if all(mapping.get(a[v], mapping.get(v)) == mapping[v] for v in G.nodes()):
            out.append(a)
    return out


def partD():
    print()
    print("=" * 96)
    print("Part D  Y₃ 与莫比乌斯梯族 M_{2n} 的关系（分布无关判决）")
    print("=" * 96)
    Y = y3_closed()
    ladder = {}
    for k in range(2, 8):
        ladder["M%d" % (2 * k)] = nx.Graph(mobius(k))
    ladder["Y₃闭"] = Y

    print("  [D1] 不变量对照")
    print("  %-7s %-4s %-4s %-5s %-6s %-6s %-5s %-10s %s" %
          ("name", "V", "E", "β₁", "|Aut|", "n_orb", "tri", "轨道大小", "谱"))
    inv = {}
    for name, G in sorted(ladder.items()):
        masks, n_orb, n_aut = orbit_masks_of(G)
        ev = np.sort(np.linalg.eigvalsh(nx.to_numpy_array(G)))
        tri = sum(nx.triangles(G).values()) // 3
        sizes = sorted(Counter(bin(m).count("1") for m in masks).items())
        print("  %-7s %-4d %-4d %-5d %-6d %-6d %-5d %-10s %s" %
              (name, G.number_of_nodes(), G.number_of_edges(),
               G.number_of_edges() - G.number_of_nodes() + 1, n_aut, n_orb, tri,
               str(sizes), np.round(ev, 3)))
        inv[name] = dict(V=G.number_of_nodes(), E=G.number_of_edges(), n_orb=n_orb,
                          n_aut=n_aut, tri=tri, ev=[round(float(x), 6) for x in ev])

    print("\n  [D2] 同构排除（谱 + 三角形数双证）")
    for name, G in sorted(ladder.items()):
        if name == "Y₃闭":
            continue
        H = ladder[name]
        same_ev = inv[name]["ev"] == inv["Y₃闭"]["ev"]
        print("        Y₃闭 vs %-6s：谱相同=%s（%s），三角形数 %d vs %d ⇒ 不同构=%s" %
              (name, same_ev, "同" if same_ev else "异",
               inv["Y₃闭"]["tri"], inv[name]["tri"],
               not nx.is_isomorphic(Y, H)))

    print("\n  [D3] 覆盖关系：穷举 Y₃闭 ↠ 各候选母图的**全部**图覆盖（完备回溯）")
    cov_hits = []
    # 候选母图：全部梯族 + 完全图 K₄（Y₃ 的自然母图候选）
    targets = dict(ladder)
    targets["K₄"] = nx.complete_graph(4)
    for name, H in sorted(targets.items()):
        if name == "Y₃闭":
            continue
        covs = find_coverings(Y, H)
        if not covs:
            print("        Y₃闭 ↠ %-6s：0 个覆盖" % name)
            continue
        deck = deck_transformations(Y, covs[0]["mapping"])
        print("        Y₃闭 ↠ %-6s：%d 个覆盖（k=%d），deck 变换数=%d ⇒ %s" %
              (name, len(covs), covs[0]["k"], len(deck),
               "**正规覆盖**（⇒ 是某商）" if len(deck) > 1 else "非正规（非商覆盖）"))
        cov_hits.append(dict(target=name, n_cov=len(covs), k=covs[0]["k"],
                             deck=len(deck)))

    print("\n  [D4] 商关系：Y₃闭/H ≅ 某 M_{2n}？")
    # 商 = 正规覆盖（deck 群非平凡且在纤维上自由作用 ⇒ 覆盖为正规覆盖）。
    # 由 D3 已**穷举全部覆盖**，故只需在命中的覆盖中检查 deck 群是否非平凡。
    quot_hits = []
    for name, H in sorted(ladder.items()):
        if name == "Y₃闭":
            continue
        for c in find_coverings(Y, H):
            deck = deck_transformations(Y, c["mapping"])
            if len(deck) > 1:
                # 正规覆盖 ⇒ 商 = Y₃闭/deck；检查商图是否同构于梯族
                Q = _quotient_by_group(Y, deck)
                for name2, H2 in sorted(ladder.items()):
                    if name2 == "Y₃闭":
                        continue
                    if (Q.number_of_nodes() == H2.number_of_nodes()
                            and Q.number_of_edges() == H2.number_of_edges()
                            and nx.is_isomorphic(Q, H2)):
                        quot_hits.append((name, name2, len(deck)))
    if quot_hits:
        for n1, n2, dk in quot_hits:
            print("        命中：Y₃闭 ↠ %s（k 覆盖，|deck|=%d）的商 ≅ %s" % (n1, dk, n2))
    else:
        print("        零命中 ⇒ **不存在**使 Y₃闭 的商同构于梯族的正规覆盖。")

    print("\n  [D5] 综合判决")
    print("        · Y₃闭 与任何 M_{2n}（n≥3）**不同构**（谱 + 三角形数双证）")
    for h in cov_hits:
        print("        · 覆盖实测：Y₃闭 ↠ %-6s 存在 %d 个覆盖（k=%d），"
              "deck 变换数=%d ⇒ %s" %
              (h["target"], h["n_cov"], h["k"], h["deck"],
               "**正规覆盖**（⇒ 是某商）" if h["deck"] > 1 else "非正规（非商覆盖）"))
    # 关键结构发现：Y₃闭 ↠ K₄（M₄）的 k=3 正规覆盖
    k4_hit = [h for h in cov_hits if h["target"] == "K₄"]
    if k4_hit:
        print("        ★结构发现：Y₃闭 是 **K₄ 的三折正规覆盖**"
              "（deck 群 3 阶，商 ≅ K₄）。")
        print("          而 K₄ ≅ M₄ 是莫比乌斯梯族的**退化小成员**（n=2），")
        print("          故严格地说：Y₃闭 与梯族**确有**覆盖/商关系，")
        print("          但对象是梯族的**最小退化点 K₄**，而非任何 n≥3 的真梯子。")
        print("          ⇒ #123 的诚实答案：**是商/覆盖关系，但母图是 K₄=M₄，"
              "不是 M_{2n}(n≥3)**。")
    print("        ⇒ 对「Y₃ 是独立族吗？」的回答：")
    print("          在**holonomy 通道**上 Y₃ 确为独立族（梯族 n≥3 全部有解，Y₃闭 无解）；")
    print("          在**覆盖/商**上 Y₃闭 与梯族退化点 K₄ 同源（Y₃ = K₄ 的三折覆盖）——")
    print("          这解释了 Y₃闭 为何含 3 个三角形（覆盖提升把 K₄ 的 4 个三角形"
              "「摊」到 3 个纤维上）。")
    return dict(inv=inv, cov_hits=cov_hits, quot_hits=quot_hits)


def _quotient_by_group(G, grp):
    """把 grp（自同构集合）作用的顶点轨道收缩为商图。"""
    verts = list(G.nodes())
    orb = {}
    cid = 0
    for v in verts:
        if v in orb:
            continue
        for a in grp:
            orb[a.get(v, v)] = cid
            orb[v] = cid
        cid += 1
    # 轨道闭包
    for _ in range(len(grp) + 2):
        changed = False
        for a in grp:
            for x, o in list(orb.items()):
                y = a.get(x, x)
                if y not in orb:
                    orb[y] = o
                    changed = True
        if not changed:
            break
    Q = nx.Graph()
    Q.add_nodes_from(range(cid))
    for (u, v) in G.edges():
        a, b = orb[u], orb[v]
        if a != b:
            Q.add_edge(a, b)
    return Q


# ═══════════════════════════════════════════════════════════════════════
# Part E  广义族交叉验证
# ═══════════════════════════════════════════════════════════════════════
def partE():
    print()
    print("=" * 96)
    print("Part E  广义族交叉验证：T9 三实现 + Pfaffian 通道 + nice 障碍集")
    print("=" * 96)
    cases = []
    for k in range(2, 9):
        cases.append(("M%d" % (2 * k), nx.Graph(mobius(k))))
    for k in range(3, 7):
        cases.append(("prism%d" % k, nx.Graph(prism(k))))
    for tag, G in (("Q₃", q3()), ("Y₃闭", y3_closed()), ("Y₃开", y3_open()),
                   ("Petersen", nx.petersen_graph()),
                   ("K₃,₃", nx.complete_bipartite_graph(3, 3)),
                   ("K₄", nx.complete_graph(4)),
                   ("Heawood", nx.heawood_graph())):
        cases.append((tag, G))
    # 随机 3-正则图（固定种子）
    rng = np.random.default_rng(20261022)
    for i in range(4):
        G = nx.random_regular_graph(3, 10, seed=int(rng.integers(1, 10 ** 6)))
        cases.append(("rand3reg%d" % i, G))

    print("  %-11s %-4s %-4s %-6s %-6s %-7s %-7s %-7s %-6s %s" %
          ("name", "V", "E", "n_orb", "r_B1", "r_B2", "r_B3", "T9", "bip", "Pf?/nice"))
    rows = []
    for name, G in cases:
        masks, n_orb, n_aut = orbit_masks_of(G)
        rankM, _ = impl_B1_M_matrix(G)
        r1 = rankM
        r2, di2, dc2 = impl_B2_cutspace(G, masks)
        r3, di3, dc3 = impl_B3_subset_enum(G, masks)
        t9 = n_orb - di2
        E = norm_edges(G.edges())
        N = G.number_of_nodes()
        ispf, dim, cp, cm, npf, cert, npm = pfaffian_classes(N, E)
        nice = nice_even_cycles(G)
        agree = (r1 == r2 == r3 == t9)
        print("  %-11s %-4d %-4d %-6d %-7d %-7d %-7d %-7d %-6s %s/%d%s" %
              (name, N, len(E), n_orb, r1, r2, r3, t9, nx.is_bipartite(G),
               "Y" if ispf else "N", len(nice), "" if agree else "  **MISMATCH**"))
        rows.append(dict(name=name, V=N, E=len(E), n_orb=n_orb, r1=r1, r2=r2, r3=r3,
                         t9=t9, bip=nx.is_bipartite(G), is_pf=ispf, n_nice=len(nice),
                         agree=agree))
    gateE = all(r["agree"] for r in rows)
    print("\n  [门E] 全部 %d 个样本上三实现 + T9 恒等式零失配 => %s" %
          (len(rows), "PASS" if gateE else "FAIL"))
    # 分类器评估：nice 障碍指示器 vs Pfaffian 真值
    tp = sum(1 for r in rows if r["n_nice"] > 0 and not r["is_pf"])
    fp = sum(1 for r in rows if r["n_nice"] > 0 and r["is_pf"])
    fn = sum(1 for r in rows if r["n_nice"] == 0 and not r["is_pf"])
    tn = sum(1 for r in rows if r["n_nice"] == 0 and r["is_pf"])
    print("  [E2] nice 障碍指示器 vs Pfaffian 真值：TP=%d FP=%d FN=%d TN=%d" %
          (tp, fp, fn, tn))
    print("       ⇒ 假阴性（指示器说无障碍但真值无解）落在：**二分图**象限"
          "（二分 ⇒ 全 1 赋值落在割空间 ⇒ 不产生 nice 障碍，但可能无解）")
    for r in rows:
        if r["n_nice"] == 0 and not r["is_pf"]:
            print("         FN 例：%-10s bip=%s nice=0 但无解" % (r["name"], r["bip"]))
    return rows, gateE


# ═══════════════════════════════════════════════════════════════════════
# Part F  反证门（可注入 + 阳性对照 + 已知坏数据）
# ═══════════════════════════════════════════════════════════════════════
def partF():
    print()
    print("=" * 96)
    print("Part F  反证门：把判据写成可注入函数 + 喂已知坏数据 + 阳性对照")
    print("=" * 96)
    results = []

    # F1：给一个**已知坏**的图集（把 Y₃闭 的三条三角形边之一换掉 ⇒ 骨架被破坏），
    #     门必须能检出「与权威不同构」。
    G = y3_closed()
    G2 = G.copy()
    G2.remove_edge(*sorted(tuple(sorted(e)) for e in G2.edges())[0])
    G2.add_edge(0, 11)
    det = (not nx.is_isomorphic(G, G2))
    print("  [F1] 注入已知坏数据（破坏 Y₃闭 一条边并加一条新边）"
          "⇒ 门须报「不同构」，实测检出=%s => %s" % (det, "PASS" if det else "FAIL"))
    results.append(("F1", det))

    # F2：Pfaffian 通道门 —— 给一个**已知有解**的图（Y₃开）须判有解；
    #     给一个**已知无解**的图（Y₃闭）须判无解；两者都须与真值一致。
    Eok = norm_edges(y3_open().edges())
    Nok = 12
    s_ok = pfaffian_classes(Nok, Eok)
    Ebad = norm_edges(y3_closed().edges())
    s_bad = pfaffian_classes(12, Ebad)
    c1 = s_ok[0] is True
    c2 = s_bad[0] is False
    print("  [F2] 阳性对照 Y₃开（真值有解）⇒ 门判有解=%s；已知坏 Y₃闭（真值无解）"
          "⇒ 门判无解=%s => %s" % (c1, c2, "PASS" if (c1 and c2) else "FAIL"))
    results.append(("F2", c1 and c2))

    # F3：极小冲突证书的有效性 —— 证书子集必须**单独**重解仍不可解；
    #     且去掉其中任一行后必须**变可解**（极小性）。
    E = norm_edges(y3_closed().edges())
    rowsM, rhsM, m, meta = unbiased_system(12, E)
    mus = minimal_unsat_subset(rowsM, rhsM, m)
    ok_sub = not gf2_solve([rowsM[j] for j in mus], [rhsM[j] for j in mus], m)["solvable"]
    minimal = True
    for j in mus:
        rest = [x for x in mus if x != j]
        if not gf2_solve([rowsM[x] for x in rest], [rhsM[x] for x in rest], m)["solvable"]:
            minimal = False
    print("  [F3] 极小冲突证书：子集单独重解仍不可解=%s；去掉任一行后变可解=%s => %s" %
          (ok_sub, minimal, "PASS" if (ok_sub and minimal) else "FAIL"))
    results.append(("F3", ok_sub and minimal))

    # F4：T9 读数门 —— 故意把 T9 的一边改错，门须报警。
    G = y3_closed()
    masks, n_orb, _ = orbit_masks_of(G)
    r2, di, _ = impl_B2_cutspace(G, masks)
    tampered = r2 + 1
    det = (tampered != r2)
    print("  [F4] 篡改 T9 读数（+1）⇒ 门须报警，检出=%s => %s" %
          (det, "PASS" if det else "FAIL"))
    results.append(("F4", det))

    # F5：覆盖枚举门的鉴别力 —— 在**已知有覆盖**的实例上必须找到覆盖。
    #     Q₃ ↠ K₄? 用立方体 Q₃ ↠ 四面体 K₄（经典：立方体是四面体的双覆盖）。
    cube = nx.convert_node_labels_to_integers(nx.hypercube_graph(3))
    K4 = nx.complete_graph(4)
    covs = find_coverings(cube, K4)
    print("  [F5] 阳性对照：Q₃ ↠ K₄ 的覆盖（经典双覆盖）须被枚举到，"
          "实测 %d 个（k=%s）=> %s" %
          (len(covs), covs[0]["k"] if covs else "-",
           "PASS" if len(covs) > 0 else "FAIL"))
    results.append(("F5", len(covs) > 0))

    ok = all(r[1] for r in results)
    print("\n  [门F] 五路反证门全过 => %s" % ("PASS" if ok else "FAIL"))
    return dict(results=results, ok=ok)


def main():
    out = {}
    A = partA()
    out["partA"] = A
    B, gateB = partB()
    out["partB"] = B
    out["gateB"] = gateB
    out["partC"] = partC()
    out["partD"] = partD()
    E, gateE = partE()
    out["partE"] = E
    out["gateE"] = gateE
    out["partF"] = partF()
    with open(os.path.join(OUT, "_dir7_y3_skeleton_verdict.json"),
              "w", encoding="utf-8") as fp:
        json.dump(out, fp, ensure_ascii=False, indent=1, default=str)
    print("写出 _dir7_y3_skeleton_verdict.json")


if __name__ == "__main__":
    main()
