# -*- coding: utf-8 -*-
"""_probe_y3_impls.py -- 定位任务 #122：核子骨架 Y3 构造的权威来源与多实现一致性

任务 #122 描述：找到 Round101 莫比乌斯梯 Pfaffian 解集引擎（无偏线性系统＋三道强制门）
与核子骨架 Y3⋊△3 的权威构造脚本，提取精确邻接/定义。

本脚本做三件事（只读勘察，不改任何既有文件）：
  A. 扫描本仓全部 .py，抽取所有名为 y3 / y3_closed / y3_open 的函数体，做 md5 归并，
     给出「同一份实现被复制到几处」的分布（G63 共享引擎律的前置事实）。
  B. 列出 101 轮 Pfaffian 引擎的 API 清单与自检入口，确认「无偏线性系统＋三道强制门」
     在 _pfcore.py 中的确切位置（行号）。
  C. 打印 Y3 闭/开的规范邻接表（确定性排序），作为后续一切实测的**唯一权威邻接**。

作者：WorkBuddy | 2026-10-22
"""
import os
import re
import sys
import hashlib
import json

import os
ROOT = os.environ.get("SRE_Y3_ROOT", os.path.dirname(os.path.abspath(__file__)))

# ---------- A. 扫描 y3 系列实现 ----------
FUNC_RE = re.compile(r"^def (y3_closed|y3_open|y3)\s*\(.*?(?=\n(?:def |# ---|class )|\Z)",
                     re.S | re.M)


def scan_impls():
    hits = {}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "node_modules",
                                    ".workbuddy", "organic_cache", "backup_paper_20260924_164026",
                                    "backup_mass_origin_paper_20260928_153843")]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for m in FUNC_RE.finditer(t):
                body = m.group(0)
                name = m.group(1)
                h = hashlib.md5(body.encode("utf-8")).hexdigest()[:10]
                hits.setdefault((name, h), []).append(
                    os.path.relpath(p, ROOT).replace("\\", "/"))
    return hits


def show_impls():
    hits = scan_impls()
    print("=" * 90)
    print("[A] Y3 构造函数的实现分布（同名 + 同函数体 md5 归并）")
    print("=" * 90)
    rows = []
    for (name, h), files in sorted(hits.items()):
        files = sorted(files)
        print("  %-10s md5=%s  出现 %d 处" % (name, h, len(files)))
        for f in files:
            print("        -", f)
        rows.append(dict(func=name, md5=h, n=len(files), files=files))
    print("\n  合计：%d 个不同实现体（按函数名 × 函数体 md5）" % len(rows))
    return rows


# ---------- B. 101 轮 Pfaffian 引擎 API 清单 ----------
def show_pf_engine():
    print()
    print("=" * 90)
    print("[B] 101 轮 Pfaffian 引擎（code/_pfcore.py + code/_gf2.py）API 定位")
    print("=" * 90)
    out = {}
    for fn in ("code/_pfcore.py", "code/_gf2.py"):
        p = os.path.join(ROOT, fn.replace("/", os.sep))
        t = open(p, encoding="utf-8").read()
        lines = t.splitlines()
        print("  --- %s （%d 行）" % (fn, len(lines)))
        apis = []
        for i, l in enumerate(lines, 1):
            m = re.match(r"^def (\w+)\s*\((.*?)\)", l)
            if m:
                apis.append(dict(line=i, name=m.group(1), sig=m.group(2)))
                print("      L%-4d def %s(%s)" % (i, m.group(1), m.group(2)))
        out[fn] = apis
    # 三道强制门的关键标志
    print("\n  强制门标志串检索：")
    for fn in ("code/_pfcore.py", "code/_bridge101_nucleon.py"):
        t = open(os.path.join(ROOT, fn.replace("/", os.sep)), encoding="utf-8").read()
        for kw, desc in [("cr_count", "Kasteleyn 交叉数（符号源）"),
                         ("unbiased_system", "无偏线性系统（不预设定向）"),
                         ("pfaffian_unbiased", "β 偏移求解（β=0/1 两侧）"),
                         ("pf_expand_cached", "排列展开独立实现（交叉校验）"),
                         ("pf_fast", "Pf 值求值"),
                         ("count_pm", "完美匹配计数"),
                         ("rec_pf", "递归 Pf 独立实现"),
                         ("pf_perm", "排列 Pf 独立实现"),
                         ("selfcheck", "引擎自检入口")]:
            hit = kw in t
            if hit:
                ln = next((i for i, l in enumerate(t.splitlines(), 1) if kw in l), -1)
                print("      %-20s %-28s %s  (L%d)" % (kw, desc, "有", ln))
    return out


# ---------- C. Y3 闭/开的规范邻接表 ----------
def canonical_adjacency():
    import networkx as nx

    def y3_closed():
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
        G = y3_closed()
        tri = nx.triangles(G)
        ring_v = {v for v in G if tri[v] > 0}
        ring_edges = sorted(tuple(sorted(e)) for e in G.edges()
                            if e[0] in ring_v and e[1] in ring_v)
        H = G.copy()
        H.remove_edge(*ring_edges[0])
        assert nx.is_connected(H)
        return H

    print()
    print("=" * 90)
    print("[C] Y3 闭/开 的规范邻接表（权威定义，后续一切实测以此为准）")
    print("=" * 90)
    res = {}
    for tag, G in (("Y3闭", y3_closed()), ("Y3开", y3_open())):
        E = sorted(tuple(sorted(e)) for e in G.edges())
        V = sorted(G.nodes())
        print("  %s: V=%d E=%d" % (tag, len(V), len(E)))
        print("     边集 E =", E)
        res[tag] = dict(V=V, E=E)
    # 闭态的顶点命名还原（说明构造语义）
    G = y3_closed()
    inv = {v: d.get("name", str(v)) for v, d in G.nodes(data=True)}
    print("\n  语义还原：3 个中心 c0,c1,c2 各连 3 个「腿」 Lij；")
    print("            腿按 j 分 3 组，每组 (L0j,L1j,L2j) 成一个三角形。")
    print("  节点标签映射（整数 ← 语义）：")
    for v in sorted(inv):
        print("      %2d ← %s" % (v, inv[v]))
    return res


def main():
    rows = show_impls()
    show_pf_engine()
    adj = canonical_adjacency()
    out = dict(impls=rows, adjacency=adj)
    with open(os.path.join(ROOT, "_probe_y3_impls.json"),
              "w", encoding="utf-8") as fp:
        json.dump(out, fp, ensure_ascii=False, indent=1)
    print("写出 _probe_y3_impls.json")


if __name__ == "__main__":
    main()
