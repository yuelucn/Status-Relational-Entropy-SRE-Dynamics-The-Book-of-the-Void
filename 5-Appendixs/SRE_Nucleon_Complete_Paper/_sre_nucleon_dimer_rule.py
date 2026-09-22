# -*- coding: utf-8 -*-
"""两体拼接律标定：按"开-闭互补"规则构造氘核图，算拓扑与谱。
不写论文，只做结构枚举与数值对照。
"""
import sys, json, itertools
import numpy as np
import networkx as nx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

M_P = 938.27208816
M_N = 939.56542052
DM = M_N - M_P
ALPHA = 1.0 / 137.035999084
B_D = 2.224566

T_DM = B_D / DM                    # 1.720027
T_ALPHA = B_D / (ALPHA * M_P)      # 0.324903
RHO_C = (7 + 13 ** 0.5) / 2.0
PI1_C = 1.0 / RHO_C


def sec(t):
    print("\n" + "=" * 74 + "\n" + t + "\n" + "=" * 74)


def Y3():
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    return G


P = Y3()
N = nx.relabel_nodes(P.copy(), {v: "n_" + v for v in P.nodes()})
N.remove_edge("n_L02", "n_L22")
DORM = ("n_L02", "n_L12", "n_L22")     # 开态缺口路径（三点）


def topo(G):
    V, E = G.number_of_nodes(), G.number_of_edges()
    c = nx.number_connected_components(G)
    return V, E, E - V + c, sum(nx.triangles(G).values()) // 3, c


def lam_rho(G):
    V, E, b1, T, c = topo(G)
    if c != 1:
        return None
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    return ev[1], ev[-1], ev[1] / ev[-1], b1, T, V, E


def amalgam(P, N, pairs):
    """pairs: [(P顶点, N顶点), ...] -> 把 N 顶点识别到 P 顶点上"""
    m = {}
    for pv, nv in pairs:
        m[nv] = pv
    H = nx.Graph()
    for u, v in P.edges():
        H.add_edge(u, v)
    for u, v in N.edges():
        uu, vv = m.get(u, u), m.get(v, v)
        if uu != vv:
            H.add_edge(uu, vv)
    return H


def dedup(gs):
    out = []
    for G in gs:
        if any(nx.is_isomorphic(G, H) for H in out):
            continue
        out.append(G)
    return out


def run(title, plist, note=""):
    print("\n--- %s ---" % title)
    if note:
        print("    " + note)
    gs = [amalgam(P, N, pr) for pr in plist]
    uniq = dedup(gs)
    print("    构造 %d 个 -> 同构类 %d 个" % (len(gs), len(uniq)))
    rows = []
    for G in uniq:
        r = lam_rho(G)
        if r is None:
            continue
        rows.append(r)
    for l2, rho, pi1, b1, T, V, E in sorted(rows):
        print("    V=%2d E=%2d b1=%2d T=%d | lam2=%9.6f rho=%9.6f Pi1=%.9f rho/rhoP=%.6f"
              % (V, E, b1, T, l2, rho, pi1, rho / RHO_C))
    return uniq


sec("[0] 两个核子的骨架")
for tag, G in (("P 闭态(质子)", P), ("N 开态(中子)", N)):
    V, E, b1, T, c = topo(G)
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    print("  %-14s V=%2d E=%2d beta1=%d T=%d | lam2=%.9f rho=%.9f Pi1=%.9f"
          % (tag, V, E, b1, T, ev[1], ev[-1], ev[1] / ev[-1]))
print()
print("  目标对照：B_d/dm_np = %.6f   B_d/(alpha*m_p) = %.6f" % (T_DM, T_ALPHA))
print("  未被合并(两个自由核子)的谱和：")

ring_edges = [e for e in P.edges() if e[0].startswith("L") and e[1].startswith("L")]
spoke_edges = [e for e in P.edges() if e[0].startswith("c") or e[1].startswith("c")]

sec("[1] 变体 A：缺口两端 → P 的一条环边两端")
run("缺口-环边对接", [((e[0], "n_L02"), (e[1], "n_L22")) for e in ring_edges],
    "规则：开态缺口两端识别到闭合环的一条边上")

sec("[2] 变体 B：缺口两端 → P 的一条辐条两端")
run("缺口-辐条对接", [((e[0], "n_L02"), (e[1], "n_L22")) for e in spoke_edges])

sec("[3] 变体 C：单点接触")
run("单点接触", [((v, "n_L02"),) for v in P.nodes()])

sec("[4] 变体 D：开放路径三点 → P 的某个环三点")
plist = []
for j in range(3):
    ring_v = ("L0%d" % j, "L1%d" % j, "L2%d" % j)
    for perm in itertools.permutations(ring_v):
        plist.append(((perm[0], "n_L02"), (perm[1], "n_L12"), (perm[2], "n_L22")))
run("开放路径贴环", plist)

sec("[5] 变体 E：缺口两端 → P 的同一顶点（强行并点）")
run("并到同一顶点", [((v, "n_L02"), (v, "n_L22")) for v in P.nodes()])

sec("[6] 规则可行性：n-n 与 p-p")
print("  规则要求的一侧是【缺口】、另一侧是【完整闭合环边】。")
print("  n-n : 两侧都是缺口 -> 无\"完整环边\"可对接 -> 规则不适用 -> 不形成共享单元")
print("  p-p : 两侧都无缺口  -> 无\"缺口\"可用      -> 规则不适用 -> 不形成共享单元")
print("  n-p : 缺口 + 完整环边 各一 -> 规则适用     -> 形成 1 个共享单元")
print("  => 唯一可对接的组合是 n-p，与实测（唯一束缚两体系统为氘核）一致。")

sec("[7] 关键对照表")
print("  B_d/dm_np            = %.6f" % T_DM)
print("  B_d/(alpha*m_p)      = %.6f" % T_ALPHA)
print("  V/beta1(闭)          = %.6f" % (12 / 7))
print("  sqrt3                = %.6f" % (3 ** 0.5))
print("  1/3                  = %.6f" % (1 / 3))
print("  rho/3                = %.6f" % (RHO_C / 3))
print("  1/rho                = %.6f" % PI1_C)
print()

sec("[8] 释放量口径检验")
print("  beta1(P)+beta1(N) = %d ；粘合后 beta1 见各表（均为整数）" % (7 + 6))
print("  T(P)+T(N)         = %d ；粘合后 T 亦为整数" % (3 + 2))
print("  => 整数型拓扑量只能给出整数比；B_d/dm_np = 1.720 非整数")
print("  => \"质量差单位 dm_np\" 不能直接当\"结合能单位\"（框架需修正，见讨论）")
print("\n[done]")
