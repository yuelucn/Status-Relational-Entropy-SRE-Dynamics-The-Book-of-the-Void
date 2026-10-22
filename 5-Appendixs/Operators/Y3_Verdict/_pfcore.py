# -*- coding: utf-8 -*-
"""_pfcore.py -- Pfaffian 定向判定核心（101轮共用）

自校验原则（G46/G49）：
  * Pfaffian 用两个独立实现：递归法 rec_pf 与 排列展开法 pf_perm。
  * Pfaffian 定向的定义：|Pf(A_sigma)| = #完美匹配（标准定义）。
  * 判定用**定义式暴力**（枚举 2^{|E|} 定向），不用未经校验的线性捷径。
"""
import itertools
from functools import lru_cache


# ---------- 边集规范化 ----------
def norm_edges(E):
    out = set()
    for (u, v) in E:
        a, b = (u, v) if u < v else (v, u)
        if a == b:
            raise ValueError("self loop")
        out.add((a, b))
    return sorted(out)


# ---------- 图构造 ----------
def cyc(n, conns):
    E = []
    for s in conns:
        s %= n
        if s == 0:
            continue
        for i in range(n):
            E.append((i, (i + s) % n))
    return norm_edges(E)


def prism(n):
    """C_n x K_2，2n 顶点，平面。"""
    E = []
    for i in range(n):
        E.append((i, (i + 1) % n))
        E.append((n + i, n + (i + 1) % n))
        E.append((i, n + i))
    return norm_edges(E)


def mobius(n):
    """莫比乌斯梯 M_{2n} = Cay(Z_{2n},{1,n})，2n 顶点。n>=3 时非平面。"""
    N = 2 * n
    E = [(i, (i + 1) % N) for i in range(N)]
    E += [(i, i + n) for i in range(n)]
    return norm_edges(E)


def bipartite(na, nb):
    return norm_edges([(a, na + b) for a in range(na) for b in range(nb)])


def kneser_pm(n, k):
    """Kneser 图 KG(n,k)：顶点 = n 元集的 k 子集，边 = 不交。N 小，仅供测试。"""
    from itertools import combinations
    V = list(combinations(range(n), k))
    idx = {v: i for i, v in enumerate(V)}
    E = []
    for i, v in enumerate(V):
        for j in range(i + 1, len(V)):
            if not (set(v) & set(V[j])):
                E.append((i, j))
    return len(V), norm_edges(E)


# ---------- 偶圈枚举（独立实现 A：DFS） ----------
def even_cycles_dfs(N, E, max_len=None):
    adj = {v: [] for v in range(N)}
    for (u, v) in E:
        adj[u].append(v)
        adj[v].append(u)
    out = set()
    for s in range(N):
        stack = [(s, [s], {s})]
        while stack:
            v, path, seen = stack.pop()
            if max_len is not None and len(path) > max_len:
                continue
            for w in adj[v]:
                if w == s:
                    if len(path) >= 3 and len(path) % 2 == 0:
                        es = set()
                        for i in range(len(path)):
                            a, b = path[i], path[(i + 1) % len(path)]
                            es.add((min(a, b), max(a, b)))
                        out.add(frozenset(es))
                elif w not in seen and w > s:
                    stack.append((w, path + [w], seen | {w}))
    return sorted(out, key=lambda s: (len(s), sorted(s)))


def cycle_ordered(C):
    adj = {}
    for (u, v) in C:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    for k in adj:
        adj[k].sort()
    s = min(adj)
    cur = adj[s][0]
    tau = [s, cur]
    prev = s
    while cur != s:
        nxts = [v for v in adj[cur] if v != prev]
        if len(nxts) != 1:
            raise RuntimeError("walk fail")
        nxt = nxts[0]
        tau.append(nxt)
        prev, cur = cur, nxt
        if len(tau) > len(C) + 1:
            raise RuntimeError("walk overrun")
    assert len(tau) == len(C) + 1 and len(set(tau)) == len(C)
    return tau


# ---------- Pfaffian：实现 A（递归） ----------
def rec_pf(adj_sign, N):
    @lru_cache(maxsize=None)
    def rec(S):
        if S == 0:
            return 1
        i = (S & -S).bit_length() - 1
        rest = S & ~(1 << i)
        tot = 0
        sgn = 1
        for j in range(i + 1, N):
            if rest & (1 << j):
                a, b = (i, j) if i < j else (j, i)
                s = adj_sign.get((a, b), 0)
                tot += sgn * s * rec(rest & ~(1 << j))
                sgn = -sgn
        return tot
    return rec((1 << N) - 1)


# ---------- Pfaffian：实现 B（排列展开，独立符号约定） ----------
def pf_perm(adj_sign, N):
    """按完美匹配求和： Pf = sum_M eps(M) prod_{e in M} A_e。
    eps(M) = (-1)^{crossings(M)}（用 Pfaffian 的经典定义）。"""
    verts = list(range(N))
    tot = 0
    # 枚举所有完美匹配（把 v0 与每个 j 配对，递归）
    def go(remaining, chosen):
        nonlocal tot
        if not remaining:
            # 弦：按左端点排序
            pos = sorted([(min(u, v), max(u, v)) for (u, v) in chosen])
            # Pfaffian 符号 = (-1)^{cr}，cr = 交错的弦对数：
            #   两弦 (x1,y1),(x2,y2) 在位置序上交错 <=> x1<x2<y1<y2 或 x2<x1<y2<y1
            cr = 0
            for a in range(len(pos)):
                for b in range(a + 1, len(pos)):
                    x1, y1 = pos[a]
                    x2, y2 = pos[b]
                    if (x1 < x2 < y1 < y2) or (x2 < x1 < y2 < y1):
                        cr += 1
            sgn = -1 if cr % 2 else 1
            p = 1
            for (u, v) in chosen:
                a, b = (u, v) if u < v else (v, u)
                p *= adj_sign.get((a, b), 0)
            tot += sgn * p
            return
        i = remaining[0]
        rest = remaining[1:]
        for k, j in enumerate(rest):
            go(rest[:k] + rest[k + 1:], chosen + [(i, j)])
    go(verts, [])
    return tot


# ---------- 完美匹配数 ----------
def count_pm(N, E):
    adjmask = [0] * N
    for (u, v) in E:
        adjmask[u] |= 1 << v
        adjmask[v] |= 1 << u
    full = (1 << N) - 1

    @lru_cache(maxsize=None)
    def rec(S):
        if S == 0:
            return 1
        v = (S & -S).bit_length() - 1
        rest = S & ~(1 << v)
        mm = adjmask[v] & rest
        tot = 0
        while mm:
            b = mm & (-mm)
            tot += rec(rest & ~b)
            mm &= ~b
        return tot
    return rec(full)


def oriented_adj(E, t):
    """t: int bitmask（按 E 下标）。返回 (u<v) -> +/-1 的字典。"""
    out = {}
    for i, (u, v) in enumerate(E):
        s = -1 if ((t >> i) & 1) else 1
        out[(u, v)] = s
    return out


# ---------- Pfaffian 定向的**定义式**判定 ----------
def pfaffian_orientations(N, E, limit_bits=22):
    """枚举 2^{|E|} 个定向，返回 (命中集合, 符号集合)。
    判定：|Pf(A_sigma)| == #PM(G)。若 #PM==0 视为**恒等通过**（无效判据，
    调用方必须拒绝，见 G43）。"""
    npm = count_pm(N, E)
    m = len(E)
    if m > limit_bits:
        raise RuntimeError("too many edges for brute force: %d" % m)
    hit = set()
    signs = set()
    for t in range(1 << m):
        adj = oriented_adj(E, t)
        val = rec_pf(adj, N)
        if abs(val) == npm:
            hit.add(t)
            if val:
                signs.add(1 if val > 0 else -1)
    return npm, hit, signs


def selfcheck():
    out = {}
    tests = [
        ("K33", 6, bipartite(3, 3)),
        ("K34", 7, bipartite(3, 4)),
        ("K35", 8, bipartite(3, 5)),
        ("prism3", 6, prism(3)),
        ("prism4", 8, prism(4)),
        ("mobius3(=K33)", 6, mobius(3)),
        ("mobius4", 8, mobius(4)),
        ("C4", 4, cyc(4, [1])),
        ("C6", 6, cyc(6, [1])),
        ("C8", 8, cyc(8, [1])),
        ("K4", 4, norm_edges([(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])),
        ("KG(5,2)=Petersen", 10, kneser_pm(5, 2)[1]),
    ]
    rows = []
    for name, N, E in tests:
        E = norm_edges(E)
        npm = count_pm(N, E)
        # Pf 两个实现交叉校验（K33, K35 等 m<=16 时可行）
        cross = None
        if len(E) <= 16:
            ok = True
            eidx = {e: i for i, e in enumerate(E)}
            rng = range(1 << len(E)) if len(E) <= 12 else range(400)
            for t in rng:
                adj = oriented_adj(E, t)
                if rec_pf(adj, N) != pf_perm(adj, N):
                    ok = False
                    break
            cross = ok
        rec = {"name": name, "N": N, "m": len(E), "npm": npm, "Pf_two_impls_agree": cross}
        if npm > 0 and len(E) <= 20:
            npm2, hit, signs = pfaffian_orientations(N, E)
            rec.update({"Pfaffian": len(hit) > 0, "n_orient": len(hit),
                        "signs": sorted(signs), "n_free_bits": len(hit).bit_length() - 1})
        else:
            rec.update({"Pfaffian": None, "note": "no PM or too big"})
        rows.append(rec)
    out["tests"] = rows
    out["all_Pf_impls_agree"] = all(r["Pf_two_impls_agree"] in (True, None) for r in rows)
    yes = [r["name"] for r in rows if r.get("Pfaffian") is True]
    no = [r["name"] for r in rows if r.get("Pfaffian") is False]
    out["discrimination"] = {"yes": yes, "no": no, "pass": bool(yes) and bool(no)}
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(selfcheck(), ensure_ascii=False, indent=1))