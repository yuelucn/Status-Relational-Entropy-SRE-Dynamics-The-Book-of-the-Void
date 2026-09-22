"""
SRE 核子原语猜测与验证 —— 夸克/色-同位旋映射 (Z3 x Z2)
============================================================
这是"先猜测、后验证"循环在原子核上的对应物（电子 60 映射的核子版）。

[猜测 G_multi] 核子原语 Γ_N = Z3(色) x Z2(同位旋/自旋) 三角棱柱图 (6 节点)。
组合规则 = SRE 原生自组织壳：核子逐个加入，壳内连成 环+弦(degree=4)，
当壳内代数连通度 λ2_shell 跌破单一阈值 T (T 来自 Γ_N 的 λ2_prim) 即开新壳，
新壳与旧壳以弱链(0.3)相连。不含任何预装壳容量。

[验证目标] 扫描 A=2..130，λ2(A) 是否在幻数 2,8,20,28,50,82,126 出现相位变。
[对照]   shell_borrowed = 借来的壳容量(阳性) ; geometric = 纯几何堆积(阴性)。

判据：SNR = mean(|step| at magic) / mean(|step| at non-magic), step 为相对变分。
"""
import numpy as np
import json
import math

MAGIC = [2, 8, 20, 28, 50, 82, 126]
SHELL_CAP = [2, 6, 12, 8, 22, 32, 44, 58]   # 阳性对照(借来的)


# ---------- 基础图工具 ----------
def laplacian_lambda2(A):
    A = np.asarray(A, float)
    n = A.shape[0]
    if n <= 1:
        return 0.0
    d = A.sum(1)
    L = np.diag(d) - A
    w = np.linalg.eigvalsh(L)
    w.sort()
    return float(w[1]) if n > 1 else 0.0


def n_loops_estimate(A):
    """粗略环数估计：利用 trace(L^k) 或简单用边数-节点+连通分量(≠真实环基)。
    这里用 cyclomatic number = E - V + C 作为下界代理。"""
    A = np.asarray(A, float)
    n = A.shape[0]
    E = int((A > 0).sum()) // 2
    # 连通分量
    seen = set()
    comp = 0
    Ad = (A > 0).astype(int)
    for s in range(n):
        if s not in seen:
            comp += 1
            st = [s]
            seen.add(s)
            while st:
                u = st.pop()
                for v in range(n):
                    if Ad[u, v] and v not in seen:
                        seen.add(v)
                        st.append(v)
    return max(0, E - n + comp)


# ---------- 猜测 G：核子原语 Z3 x Z2 三角棱柱 ----------
def nucleon_primitive():
    """6 节点三角棱柱 (Z3 color x Z2 spin)：色环 0-1-2, 自旋环 3-4-5, 横边 0-3,1-4,2-5。"""
    A = np.zeros((6, 6))
    for i, j in [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]:
        A[i, j] = A[j, i] = 1.0
    return A


LAM2_PRIM = laplacian_lambda2(nucleon_primitive())


# ---------- 阳性对照：借来的壳容量 ----------
def graph_shell_borrowed(M):
    V = M
    A = np.zeros((V, V))
    shell_id = np.zeros(V, int)
    cap = SHELL_CAP
    idx = 0
    s = 0
    while idx < V:
        size = min(cap[s], V - idx)
        for a in range(idx, idx + size):
            shell_id[a] = s
        # 壳内团
        for a in range(idx, idx + size):
            for b in range(idx, idx + size):
                if a != b:
                    A[a, b] = 1.0
        idx += size
        s += 1
        if s >= len(cap):
            # 超出容量表：继续按最后容量堆叠
            cap = cap + [cap[-1]]
    # 相邻壳弱耦合
    for a in range(V):
        for b in range(V):
            if shell_id[a] + 1 == shell_id[b]:
                A[a, b] = 0.3
                A[b, a] = 0.3
    return A


# ---------- 阴性对照：纯几何堆积(无内部结构) ----------
def geometric_positions(M, r0=1.2, d=1.6, seed=0):
    R = r0 * M ** (1.0 / 3.0)
    dd = d
    pts = []
    # 自适应缩小间距直到候选点足够
    for _ in range(20):
        n = int(math.ceil(2 * R / dd)) + 1
        cand = []
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                for k in range(-n, n + 1):
                    p = np.array([i, j, k], float) * dd
                    if np.linalg.norm(p) <= R + 1e-9:
                        cand.append(p)
        if len(cand) >= M:
            break
        dd *= 0.8
    pts = np.array(cand if cand else [np.zeros(3)])
    dist = np.linalg.norm(pts, axis=1)
    idx = np.argsort(dist)[:M]
    return pts[idx]


def graph_geometric(M, cut=1.9):
    pos = geometric_positions(M)
    V = M
    A = np.zeros((V, V))
    D = np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=2)
    dm = D[D > 0].mean()
    c = cut * dm
    for i in range(V):
        for j in range(V):
            if i != j and D[i, j] <= c:
                A[i, j] = 1.0
    return A


# ---------- 猜测 G：核子原语 + SRE 原生自组织壳 ----------
def graph_quark_spectral_shell(M, T=None, degree=4, weak=0.3):
    """核子逐个加入；壳内连成 环+弦(degree)，壳内 λ2 跌破阈值 T 即开新壳。
    T 默认 = LAM2_PRIM (来自 Γ_N 的唯一自由参数)。"""
    if T is None:
        T = LAM2_PRIM
    prim = nucleon_primitive()
    p = 6
    shells = []          # list of lists of global node-ids
    node_shell = []      # per global node -> shell index
    A = np.zeros((p * M, p * M))
    for a in range(M):
        base = a * p
        A[base:base + p, base:base + p] = prim          # 内部 Z3xZ2 原语
        # 决定此核子归入哪个壳
        place_new_shell = False
        if not shells:
            place_new_shell = True
        else:
            sid = len(shells) - 1
            # 当前壳内部(仅核子锚点间)的 λ2
            anc = shells[sid]                            # 锚点 = 每个核子的 node 0
            if len(anc) >= 2:
                sub = A[np.ix_(anc, anc)]
                lam2_shell = laplacian_lambda2(sub)
            else:
                lam2_shell = 0.0
            if lam2_shell < T:
                place_new_shell = True
        if place_new_shell:
            shells.append([])
        sid = len(shells) - 1
        # 锚点 node 0
        anchor = base
        shells[sid].append(anchor)
        node_shell.append(sid)
        # 壳内：锚点连成 环+弦 (degree=4 -> 连到壳内前后 2 个)
        members = shells[sid]
        k = degree // 2
        for off in range(1, k + 1):
            if len(members) > off:
                A[anchor, members[-1 - off]] = 1.0
                A[members[-1 - off], anchor] = 1.0
        # 与新壳上一个核子弱耦合到上一壳的代表(最后一个锚点)
        if sid > 0:
            prev = shells[sid - 1][-1]
            A[anchor, prev] = weak
            A[prev, anchor] = weak
    return A


def graph_quark_geometric(M):
    """猜测 G 的另一种组合：原语内部 Z3xZ2 + 核子间几何堆积(锚点相连)。阴性变体。"""
    prim = nucleon_primitive()
    p = 6
    pos = geometric_positions(M)
    A = np.zeros((p * M, p * M))
    for a in range(M):
        base = a * p
        A[base:base + p, base:base + p] = prim
    D = np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=2)
    dm = D[D > 0].mean()
    c = 1.9 * dm
    for a in range(M):
        for b in range(M):
            if a != b and D[a, b] <= c:
                A[a * p, b * p] = 1.0      # 锚点相连
                A[b * p, a * p] = 1.0
    return A


# ---------- 扫描 + SNR 判据 ----------
def step_seq(lam):
    """相对变分序列 (lam[i+1]-lam[i])/lam[i]"""
    return [((lam[i + 1] - lam[i]) / lam[i]) if lam[i] != 0 else 0.0
            for i in range(len(lam) - 1)]


def magic_snr(lam):
    steps = step_seq(lam)
    mag_steps = [abs(steps[m - 2]) for m in MAGIC if 2 <= m <= len(lam)]
    non = [abs(s) for i, s in enumerate(steps)
           if (i + 2) not in MAGIC and abs(s) > 1e-9]
    if not non:
        return float("nan")
    return float(np.mean(mag_steps) / np.mean(non))


def magic_snr_randomized(lam, n_perm=2000, seed=12345):
    """严格化：真实幻数 SNR vs 随机 7 元组位置的 SNR 分布 -> z 分数。
    若真实 SNR 不显著超出随机分布，则该图并未'看到'幻数。"""
    rng = np.random.default_rng(seed)
    real = magic_snr(lam)
    N = len(lam)
    pool = list(range(2, N))            # 与幻数同域
    dist = []
    for _ in range(n_perm):
        fake = sorted(rng.choice(pool, size=len(MAGIC), replace=False))
        steps = step_seq(lam)
        mag_steps = [abs(steps[m - 2]) for m in fake]
        non = [abs(s) for i, s in enumerate(steps)
               if (i + 2) not in fake and abs(s) > 1e-9]
        if non and mag_steps:
            dist.append(np.mean(mag_steps) / np.mean(non))
    dist = np.array(dist)
    mean_r, std_r = dist.mean(), dist.std()
    z = (real - mean_r) / std_r if std_r > 1e-12 else float("nan")
    p = float(np.mean(dist >= real))    # 单尾 p（真实 SNR 排位）
    return {"real_snr": real, "rand_mean": float(mean_r),
            "rand_std": float(std_r), "z": float(z), "p_one_tail": p}


def scan(graph_fn, label, **kw):
    lam = []
    for M in range(2, 131):
        A = graph_fn(M, **kw)
        lam.append(laplacian_lambda2(A))
    snr = magic_snr(lam)
    # 方向(负=跌落, 与硼 binary 同向)
    dirs = {m: ("down" if lam[m - 1] > lam[m - 2] else "up") for m in MAGIC if m <= len(lam)}
    return {"label": label, "lambda2": lam, "snr": snr, "magic_dir": dirs}


def main():
    print(f"\u0393_N = Z3xZ2 triangular prism, \u03bb2_prim = {LAM2_PRIM:.4f}\n")
    graphs = {
        "borrowed_shell": (graph_shell_borrowed, "borrowed shell-cap (POS ctrl)"),
        "geometric": (graph_geometric, "geometric packing (NEG ctrl)"),
        "quark_geometric": (graph_quark_geometric, "quark Z3xZ2 + geometric (GUESS)"),
    }
    out = {"magic_numbers": MAGIC,
           "gamma_N": "Z3(color) x Z2(isospin) triangular prism, 6 nodes",
           "lambda2_prim": LAM2_PRIM, "results": {}}
    print(f"{'graph':42s} {'SNR':>7s} {'z':>7s} {'p(>rand)':>9s}  magic_dir")
    for key, (fn, label) in graphs.items():
        lam = [laplacian_lambda2(fn(M)) for M in range(2, 131)]
        r = magic_snr_randomized(lam, n_perm=2000)
        dirs = {m: ("down" if lam[m - 1] > lam[m - 2] else "up") for m in MAGIC if m <= len(lam)}
        out["results"][key] = {"label": label, "lambda2": lam,
                               "snr": r["real_snr"], "z": r["z"],
                               "p_one_tail": r["p_one_tail"], "magic_dir": dirs}
        dirstr = ",".join(f"{m}:{d[0]}" for m, d in dirs.items())
        print(f"{label:42s} {r['real_snr']:7.3f} {r['z']:7.2f} {r['p_one_tail']:9.3f}  {dirstr}")

    with open(r"C:\mywork\vasp\sre_nucleon_quark_guess_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\n[OK] sre_nucleon_quark_guess_results.json")


if __name__ == "__main__":
    main()
