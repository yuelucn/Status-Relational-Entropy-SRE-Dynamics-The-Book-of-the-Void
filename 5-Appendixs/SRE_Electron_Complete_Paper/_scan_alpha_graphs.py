"""
扫描多种标准图拓扑, 搜索 α ≈ 1/137.036 的涌现。

测试图族:
1. Platonic solids (4种: tetrahedron, cube, octahedron, dodecahedron, icosahedron)
2. Petersen graph
3. Complete bipartite K_{m,n} (多种 m,n)
4. Complete graph K_n
5. Hypercube Q_n
6. Cycle graph C_n (多种 n)
7. Wheel graph W_n
8. Grid graphs

对每个图, 计算 D_edge, C_cycle, 以及所有谱量, 检查是否有任何量 ≈ 1/137.036
"""
import numpy as np
from itertools import combinations

ALPHA = 1.0 / 137.035999084
print(f"目标 α = {ALPHA:.10f}\n")

def build_graph(data):
    """从边列表构建 D_edge 和 C_cycle"""
    edges = data['edges']
    nodes = sorted(set(n for e in edges for n in e))
    n_nodes = len(nodes)
    n_edges = len(edges)
    node_idx = {n: i for i, n in enumerate(nodes)}
    edge_idx = {tuple(sorted(e)): j for j, e in enumerate(edges)}

    # D_edge (n_edges × n_nodes)
    D = np.zeros((n_edges, n_nodes))
    for j, (a, b) in enumerate(edges):
        D[j, node_idx[a]] = 1
        D[j, node_idx[b]] = -1

    # 枚举简单环 (up to length 8)
    A = np.zeros((n_nodes, n_nodes))
    for a, b in edges:
        A[node_idx[a], node_idx[b]] = 1
        A[node_idx[b], node_idx[a]] = 1

    cycles = find_cycles(edges, node_idx, max_len=8)
    n_cycles = len(cycles)

    C = np.zeros((n_cycles, n_edges))
    for i, cyc in enumerate(cycles):
        for k in range(len(cyc)):
            a, b = cyc[k], cyc[(k+1) % len(cyc)]
            j = edge_idx.get(tuple(sorted((a, b))))
            if j is not None:
                # 方向: 如果 (a,b) 与存储方向一致 → +1, 否则 → -1
                stored = edges[j]
                C[i, j] = 1 if (stored == (a, b)) else -1

    return D, C, n_nodes, n_edges, n_cycles

def find_cycles(edges, node_idx, max_len=6):
    """暴力枚举简单环"""
    from collections import defaultdict
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    nodes = list(node_idx.keys())
    cycles_set = set()
    cycles = []

    def dfs(start, current, path, visited):
        if len(path) > max_len:
            return
        for nb in adj[current]:
            if nb == start and len(path) >= 3:
                # 找到环
                key = frozenset(path)
                if key not in cycles_set:
                    cycles_set.add(key)
                    cycles.append(list(path))
            elif nb not in visited and node_idx[nb] > node_idx[start]:
                dfs(start, nb, path + [nb], visited | {nb})

    for n in nodes:
        dfs(n, n, [n], {n})

    return cycles

def test_graph(name, edges):
    """测试一个图的所有谱量"""
    try:
        D, C, nV, nE, nF = build_graph({'edges': edges})
    except Exception as e:
        print(f"  {name}: 构建失败 ({e})")
        return None

    if nF == 0:
        print(f"  {name}: V={nV} E={nE} F=0 (无环, 跳过)")
        return None

    results = []

    # 1. Z_0 = dim(F)/dim(E)
    Z0_dim = nF / nE
    results.append(("Z0_dim", Z0_dim))

    # 2. Z_0 = Tr(C^T·C)/Tr(D^T·D)
    Z0_tr = np.trace(C.T @ C) / np.trace(D.T @ D)
    results.append(("Z0_tr", Z0_tr))

    # 3. Graph Laplacian
    L_node = D.T @ D
    ev_node = np.linalg.eigvalsh(L_node)

    # 4. Cycle Laplacian
    L_cycle = C @ C.T
    ev_cycle = np.linalg.eigvalsh(L_cycle)

    # 5. Hodge Laplacian on 1-forms
    L_hodge = D @ D.T + C.T @ C
    ev_hodge = np.linalg.eigvalsh(L_hodge)

    # 6. 各种谱量
    results.append(("λ₂(L_node)/ρ(L_node)", ev_node[1] / ev_node[-1]))
    results.append(("1/ρ(L_node)", 1.0 / ev_node[-1]))
    results.append(("1/cond(L_node)", 1.0 / np.linalg.cond(L_node)))

    results.append(("λ_min(L_cycle)/ρ(L_cycle)", ev_cycle[0] / ev_cycle[-1]))
    results.append(("1/ρ(L_cycle)", 1.0 / ev_cycle[-1]))

    ev_hodge_nz = ev_hodge[ev_hodge > 1e-10]
    if len(ev_hodge_nz) > 0:
        results.append(("λ_min_nz(L_hodge)/ρ", ev_hodge_nz[0] / ev_hodge[-1]))
        results.append(("√(λ_min_nz/ρ)", np.sqrt(ev_hodge_nz[0] / ev_hodge[-1])))
        results.append(("1/cond(L_hodge)", 1.0 / np.linalg.cond(L_hodge + 1e-12 * np.eye(len(L_hodge)))))

    # 7. D^T · C^T (cross operator)
    M = D.T @ C.T  # (nV × nF)
    sv = np.linalg.svd(M, compute_uv=False)
    results.append(("σ_max(D^T·C^T)", sv[0]))
    results.append(("1/σ_max", 1.0 / sv[0]))
    if sv[-1] > 1e-10:
        results.append(("σ_min/σ_max", sv[-1] / sv[0]))

    # 8. Z_0/2 (= α if e≡1, h≡1)
    results.append(("Z0_dim/2", Z0_dim / 2))
    results.append(("Z0_tr/2", Z0_tr / 2))

    # 9. det ratios
    try:
        det_L1 = np.linalg.det(L_node)
        if nF == nE:  # C is square
            det_Lcycle = np.linalg.det(L_cycle)
            results.append(("det(L_node)/det(L_cycle)", det_L1 / det_Lcycle))
    except:
        pass

    # 10. 谱间隙的幂
    gap = ev_node[1] / ev_node[-1]
    results.append(("gap²", gap**2))
    results.append(("gap³", gap**3))

    # 排序 by 接近 α
    results.sort(key=lambda x: abs(x[1] - ALPHA) / ALPHA)

    # 输出
    print(f"\n  {name}: V={nV} E={nE} F={nF} (β₁={nE-nV+1})")
    print(f"    Z0_dim={Z0_dim:.6f}  Z0_tr={Z0_tr:.6f}")
    print(f"    λ₂(node)={ev_node[1]:.6f}  ρ(node)={ev_node[-1]:.6f}")
    print(f"    λ_min(cycle)={ev_cycle[0]:.6f}  ρ(cycle)={ev_cycle[-1]:.6f}")
    if len(ev_hodge_nz) > 0:
        print(f"    λ_min_nz(hodge)={ev_hodge_nz[0]:.6f}  ρ(hodge)={ev_hodge[-1]:.6f}")

    # 最佳 3 个
    for rname, rval in results[:3]:
        err = abs(rval - ALPHA) / ALPHA * 100
        tag = " ★" if err < 1 else (" ~" if err < 10 else "")
        print(f"    → {rname:<35s} = {rval:.10f}  (err={err:.2f}%){tag}")

    return results

# ══════════════════════════════════════════════════════════════
print("=" * 80)
print("1. Platonic Solids")
print("=" * 80)

# Tetrahedron (K4)
tet_edges = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
test_graph("Tetrahedron (K4)", tet_edges)

# Cube
cube_edges = [(0,1),(1,2),(2,3),(3,0),(0,4),(1,5),(2,6),(3,7),(4,5),(5,6),(6,7),(7,4)]
test_graph("Cube", cube_edges)

# Octahedron
oct_edges = [(0,1),(0,2),(0,3),(0,4),(1,2),(1,4),(1,5),(2,3),(2,5),(3,4),(3,5),(4,5)]
test_graph("Octahedron", oct_edges)

# Icosahedron (12V, 30E, 20F)
# 顶点: (0,±1,±φ), (±1,±φ,0), (±φ,0,±1) — 用简化邻接
ico_nodes = list(range(12))
# Icosahedron 邻接表 (每个顶点连5个)
ico_adj = {
    0: [1,2,3,4,5], 1: [0,2,5,6,7], 2: [0,1,3,7,8],
    3: [0,2,4,8,9], 4: [0,3,5,9,10], 5: [0,1,4,6,10],
    6: [1,5,7,10,11], 7: [1,2,6,8,11], 8: [2,3,7,9,11],
    9: [3,4,8,10,11], 10: [4,5,6,9,11], 11: [6,7,8,9,10]
}
ico_edges = []
for i in range(12):
    for j in ico_adj[i]:
        if i < j:
            ico_edges.append((i, j))
test_graph("Icosahedron", ico_edges)

# Dodecahedron (20V, 30E, 12F)
# 使用标准邻接表
dode_adj = {
    0: [1,4,5], 1: [0,2,7], 2: [1,3,9], 3: [2,4,11], 4: [0,3,13],
    5: [0,6,14], 6: [5,7,15], 7: [1,6,8,16], 8: [7,9,17], 9: [2,8,10,18],
    10: [9,11,19], 11: [3,10,12,20], 12: [11,13,21], 13: [4,12,14,22],
    14: [5,13,23], 15: [6,16,23], 16: [7,15,17,22], 17: [8,16,18,21],
    18: [9,17,19,20], 19: [10,18,23], 20: [11,18,21], 21: [12,17,20,22],
    22: [13,16,21,23], 23: [14,15,19,22]
}
dode_edges = []
for i in range(24):
    if i in dode_adj:
        for j in dode_adj[i]:
            if i < j:
                dode_edges.append((i, j))
test_graph("Dodecahedron", dode_edges)

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("2. Petersen Graph")
print("=" * 80)
# Petersen: outer 5-cycle, inner 5-cycle (star), 5 spokes
pet_edges = [(0,1),(1,2),(2,3),(3,4),(4,0),  # outer
             (5,7),(7,9),(9,6),(6,8),(8,5),  # inner star
             (0,5),(1,6),(2,7),(3,8),(4,9)]  # spokes
test_graph("Petersen", pet_edges)

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("3. Complete Bipartite K_{m,n}")
print("=" * 80)
for m in range(2, 8):
    for n in range(m, 12):
        edges = [(i, m+j) for i in range(m) for j in range(n)]
        test_graph(f"K_{{{m},{n}}}", edges)

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("4. Complete Graph K_n")
print("=" * 80)
for n in range(4, 10):
    edges = list(combinations(range(n), 2))
    test_graph(f"K_{n}", edges)

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("5. Hypercube Q_n")
print("=" * 80)
for dim in range(2, 6):
    n = 2**dim
    edges = []
    for i in range(n):
        for b in range(dim):
            j = i ^ (1 << b)
            if i < j:
                edges.append((i, j))
    test_graph(f"Q_{dim} (n={n})", edges)

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("6. Grid Graphs")
print("=" * 80)
for w in range(2, 8):
    for h in range(2, 8):
        edges = []
        for r in range(h):
            for c in range(w):
                v = r * w + c
                if c < w - 1:
                    edges.append((v, v + 1))
                if r < h - 1:
                    edges.append((v, v + w))
        test_graph(f"Grid {w}×{h}", edges)

# ══════════════════════════════════════════════════════════════
print("\n" + "=" * 80)
print("7. Wheel Graph W_n")
print("=" * 80)
for n in range(4, 12):
    edges = [(i, (i+1) % (n-1)) for i in range(n-1)]
    edges += [(i, n-1) for i in range(n-1)]
    test_graph(f"W_{n}", edges)

print("\n" + "=" * 80)
print("全局汇总: 所有图中最接近 α 的前 20 名")
print("=" * 80)

# 重新收集所有结果
all_results = []

def test_graph_collect(name, edges):
    try:
        D, C, nV, nE, nF = build_graph({'edges': edges})
    except:
        return
    if nF == 0:
        return
    L_node = D.T @ D
    ev_node = np.linalg.eigvalsh(L_node)
    L_cycle = C @ C.T
    ev_cycle = np.linalg.eigvalsh(L_cycle)
    L_hodge = D @ D.T + C.T @ C
    ev_hodge = np.linalg.eigvalsh(L_hodge)
    ev_hodge_nz = ev_hodge[ev_hodge > 1e-10]

    M = D.T @ C.T
    sv = np.linalg.svd(M, compute_uv=False)

    candidates = [
        (f"{name}: Z0_dim", nF / nE),
        (f"{name}: Z0_tr", np.trace(C.T @ C) / np.trace(D.T @ D)),
        (f"{name}: Z0_dim/2", nF / (2 * nE)),
        (f"{name}: Z0_tr/2", np.trace(C.T @ C) / (2 * np.trace(D.T @ D))),
        (f"{name}: λ₂/ρ(node)", ev_node[1] / ev_node[-1]),
        (f"{name}: 1/ρ(node)", 1.0 / ev_node[-1]),
        (f"{name}: λ_min/ρ(cycle)", ev_cycle[0] / ev_cycle[-1]),
        (f"{name}: 1/σ_max(D^T·C^T)", 1.0 / sv[0] if sv[0] > 0 else 999),
        (f"{name}: gap²", (ev_node[1] / ev_node[-1])**2),
        (f"{name}: gap³", (ev_node[1] / ev_node[-1])**3),
    ]
    if len(ev_hodge_nz) > 0:
        candidates.append((f"{name}: √(λmin_nz/ρ(hodge))", np.sqrt(ev_hodge_nz[0] / ev_hodge[-1])))
        candidates.append((f"{name}: 1/cond(hodge)", 1.0 / np.linalg.cond(L_hodge + 1e-12*np.eye(len(L_hodge)))))

    for cname, cval in candidates:
        all_results.append((cname, cval, abs(cval - ALPHA) / ALPHA))

# 重新运行收集
all_graphs = [
    ("Tet(K4)", tet_edges),
    ("Cube", cube_edges),
    ("Octa", oct_edges),
    ("Icosa", ico_edges),
    ("Dodeca", dode_edges),
    ("Petersen", pet_edges),
]
for m in range(2, 8):
    for n in range(m, 12):
        edges = [(i, m+j) for i in range(m) for j in range(n)]
        all_graphs.append((f"K_{m},{n}", edges))
for n in range(4, 10):
    all_graphs.append((f"K_{n}", list(combinations(range(n), 2))))
for dim in range(2, 6):
    n = 2**dim
    edges = []
    for i in range(n):
        for b in range(dim):
            j = i ^ (1 << b)
            if i < j:
                edges.append((i, j))
    all_graphs.append((f"Q_{dim}", edges))
for w in range(2, 8):
    for h in range(2, 8):
        edges = []
        for r in range(h):
            for c in range(w):
                v = r * w + c
                if c < w - 1:
                    edges.append((v, v + 1))
                if r < h - 1:
                    edges.append((v, v + w))
        all_graphs.append((f"Grid{w}x{h}", edges))

for name, edges in all_graphs:
    test_graph_collect(name, edges)

all_results.sort(key=lambda x: x[2])
for cname, cval, err in all_results[:20]:
    tag = " ★★★" if err < 0.001 else (" ★" if err < 0.01 else (" ~" if err < 0.1 else ""))
    print(f"  {cval:>14.10f}  (err={err:.4%})  {cname:<35s}{tag}")

print(f"\n目标: {ALPHA:.10f}")
best = all_results[0]
print(f"全局最佳: {best[1]:.10f}  (err={best[2]:.4%})  {best[0]}")
