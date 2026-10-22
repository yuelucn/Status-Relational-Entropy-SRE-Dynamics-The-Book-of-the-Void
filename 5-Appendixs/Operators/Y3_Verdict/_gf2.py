# -*- coding: utf-8 -*-
"""_gf2.py -- F_2 线性方程组的正确实现（RREF + 完整解空间生成）

修正前版 bug：主元变量固定为 rhs，自由变量变化时未回代 => 生成的「解集」不是解集。
正确做法：RREF 后  x_{piv[i]} = rhs_i XOR sum_{c free} R[i][c] * x_c。
"""
from _pfcore import even_cycles_dfs, cycle_ordered


def rref(rows, rhs, m):
    """返回 (pivots, R, rhs_R)，R 为 RREF 系数矩阵（不含 rhs 位），若不一致返回 None。
    行序与 pivots 一一对应。"""
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
            return None
    return piv, [M[i] & ((1 << m) - 1) for i in range(r)], \
           [(M[i] >> m) & 1 for i in range(r)]


def solve(rows, rhs, m):
    """返回 dict(solvable, pivots, R, b, free, particular)"""
    out = rref(rows, rhs, m)
    if out is None:
        return {"solvable": False}
    piv, R, b = out
    freecols = [c for c in range(m) if c not in piv]
    part = 0
    for i, c in enumerate(piv):
        if b[i]:
            part |= 1 << c
    return {"solvable": True, "m": m, "pivots": piv, "R": R, "b": b,
            "free": freecols, "dim_free": len(freecols), "particular": part}


def enumerate_solutions(sol, cap=None):
    """按 RREF 正确枚举解空间。"""
    if not sol["solvable"]:
        return
    m = sol["m"]
    piv, R, b, free = sol["pivots"], sol["R"], sol["b"], sol["free"]
    d = len(free)
    total = 1 << d
    if cap and total > cap:
        return
    for mask in range(total):
        t = 0
        for i, c in enumerate(free):
            if (mask >> i) & 1:
                t |= 1 << c
        for i, c in enumerate(piv):
            s = b[i]
            row = R[i]
            # x_c = rhs XOR sum_free R[i][f]*x_f
            v = row & t
            s ^= bin(v).count("1") & 1
            if s:
                t |= 1 << c
        yield t


# ---------- Pfaffian 定向的线性刻画（修正 rhs 由标定给出） ----------
def build_rows_even_cycles(N, E):
    eidx = {e: i for i, e in enumerate(E)}
    rows = []
    for C in even_cycles_dfs(N, E):
        row = 0
        for e in C:
            row ^= 1 << eidx[e]
        rows.append(row)
    return rows


def pfaffian_lin(N, E, rhs_of_row):
    """rhs_of_row: dict row -> rhs (由标定确定)。"""
    rows = build_rows_even_cycles(N, E)
    rows_u = sorted(set(rows))
    rhs = [rhs_of_row[r] for r in rows_u]
    return solve(rows_u, rhs, len(E))