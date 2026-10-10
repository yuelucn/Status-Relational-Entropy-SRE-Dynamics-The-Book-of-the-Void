"""SRE 核子线 · 代理求解器（surrogate solver）—— 借用 sre-ai 的 SREAIModule 架构。

角色界定（关键，来自 _sre_nucleon_mlp_feasibility.py 的警告）
------------------------------------------------------------
  这是 **代理求解器**，不是 **物理预测器**。
  · 学的东西：`k 分布 -> 图不变量 (β₁/λ₂/ρ/deg)` —— 本可精确计算的图量；
  · 用途    ：把昂贵的图构造+谱计算替换成快速近似（合法、可验证）；
  · 不学的  ：`k 分布 -> 实测半衰期`（标签无物理真值，4 个样本撑不住）。

  ⇒ 收益是**工程收益**（速度），不是**物理收益**（新知识）。

枚举层的三项实测发现（本轮，非假设）
------------------------------------
  (E1) **多群装配是断开的**。不同 group 的共享环之间**没有边**，故
       `k=(2,2)` 给出 `cc=2`、`k=(2,2,2)` 给出 `cc=3`。
       论文 §12.11(1′) 已记载 A=6 的 k=(3,3) → V=60/E=96/β₁=38 与
       k=(2,2,2) → V=63/E=99/β₁=39，与本次实测逐位一致；只是未点明
       "cc = 群数" 这一事实。**⇒ 环间连接机制在装配规则中是缺失的**
       （见 [未决项]）。
  (E2) **ρ 满足 max 律**：`ρ(多群) = max_i ρ_single(k_i)`，7 组实测全部精确到 1e−9。
       这解释了论文里 k=(3,3) 的 ρ=6.925422918 与 k=(2,2,2) 的 ρ=6.000000000 ——
       它们分别**等于** ρ_single(3) 与 ρ_single(2)，不是新值。
  (E3) **V/E/β₁ 满足严格加和律**：V=Σ(9k+3)、E=Σ(15k+3)、β₁=Σ(6k+1)，
       与群数无关，实测与闭式逐位一致。
  ⇒ 由 (E1)(E2)(E3)：**多群的图信息 = 各分量的信息之并**（谱取 max / 计数取和）。
     故代理求解器的正确任务是**按分量回归**，而非把多群当整体硬塞进 MLP。

  (E4) **共享环内部的位置与开态数不是自由度**：同一共享环内开哪个体 → 同构；
       开态数变化只改变 β₁（且仅当全开时减 1）。描述符只编码 (k 分布, 总开态数)。

描述符（最终）
--------------
  · A = Σk
  · k 分布的多重集：k_max / k_mean / k_std + 直方图 hist_2..hist_12
  · k 的「形状」量：n_group（群数）
  · 开态：n_open（总数）
  —— 不含「开在哪」，因为实测它不是自由度。
"""
from __future__ import annotations

import os
import time
import json
import itertools
from typing import Dict, List, Tuple

import numpy as np
import networkx as nx
import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------------- 项目构造器
def Y3(pre: str, state: str = "p", open_ring: int = 0) -> nx.Graph:
    """三股 Y 骨架。闭态(p): E=18, β₁=7, T=3。开态(n): 断环边 (L0r,L1r)。"""
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


def assemble(groups) -> Tuple[nx.Graph, Dict[tuple, int]]:
    """多共享环装配。groups = [(tag, [(pre,state), ...]), ...]。"""
    H = nx.Graph()
    ledger: Dict[tuple, int] = {}
    for r, (_tag, bodies) in enumerate(groups):
        if len(bodies) < 2:
            raise ValueError("共享环 r=%d 只有 %d 个体（环需 ≥2 体）" % (r, len(bodies)))
        for pre, state in bodies:
            G = Y3(pre, state, r)
            m = {"%sL%d%d" % (pre, i, r): "S%d%d" % (r, i) for i in range(3)}
            edges = {tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()}
            for e in edges:
                ledger[e] = ledger.get(e, 0) + 1
            H.add_edges_from(edges)
    return H, ledger


# ---------------------------------------------------------------- 精确标签
# 回归目标：只保留**随结构变化**的量。
# λ₂ 被剔除：实测其取值只有两个——2−√3（连通）与 0（不连通），是**结构常数**而非可学量，
#   且取 0 时会让相对误差除以零（曾出现 6.26e7% 的假误差）。
# V/E/T 也剔除：有精确闭式 V=Σ(9k+3)、E=Σ(15k+3)、β₁=Σ(6k+1)，无需学（改作验证用）。
TARGET_KEYS = ["b1", "rho", "deg_mean", "deg_std"]


def invariants(G: nx.Graph) -> Dict[str, float]:
    V, E = G.number_of_nodes(), G.number_of_edges()
    cc = nx.number_connected_components(G)
    degs = np.array([d for _, d in G.degree()], dtype=float)
    ev = np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray().astype(float))
    return dict(
        V=float(V), E=float(E), b1=float(E - V + cc),
        T=float(sum(nx.triangles(G).values()) // 3),
        lam2=float(ev[1]) if V > 1 else 0.0, rho=float(ev[-1]),
        deg_mean=float(degs.mean()), deg_std=float(degs.std()),
    )


# ---------------------------------------------------------------- 样本枚举
def k_partitions(n: int, minpart: int = 2, maxgroup: int = 3) -> List[Tuple[int, ...]]:
    """把 A 拆成各群 k（每群 k ≥ 2；**群数 ≤ 3**，理由见下）。

    群数上限 = 3：`assemble` 把每个 group 映射到共享环号 r = 位置索引，
    而 `Y3(pre,state,open_ring)` 的**叶点环号只有 j = 0,1,2**（一个核子只有 3 个环）。
    故 r ≥ 3 时 `L{i}{r}` 不存在、映射落空 ⇒ 该 group 的体**不融合**，
    退化成若干个 12 点的孤立 Y₃ 骨架（实测：4 群 → 融合 3 群 + 2 个 12 点分量）。
    ⇒ **任何核子装配最多 3 个共享环**。
    """
    out = []
    def rec(rem, mx, cur):
        if rem == 0:
            if cur:
                out.append(tuple(cur))
            return
        if len(cur) >= maxgroup:
            return
        for x in range(min(mx, rem), minpart - 1, -1):
            rec(rem - x, x, cur + [x])
    rec(n, n, [])
    return out


def descriptor(kdist, n_open: int, A_max: int = 12) -> Dict[str, float]:
    """描述符：k 分布 + 总开态数。**不含「开在哪」**（实测非自由度）。"""
    kd = list(kdist)
    d = dict(A=float(sum(kd)), n_group=float(len(kd)),
             k_max=float(max(kd)), k_mean=float(np.mean(kd)),
             k_std=float(np.std(kd)), n_open=float(n_open),
             open_frac=float(n_open) / max(sum(kd), 1))
    for m in range(2, A_max + 1):
        d["hist_%d" % m] = float(sum(1 for k in kd if k == m))
    return d


def enum_samples(A_min: int = 2, A_max: int = 12) -> Tuple[List[dict], List[dict], List[str]]:
    """枚举样本。**允许非连通图**（多群装配本身就是多个分量，见 E1）。

    描述符（每个样本）：k 分布的多重集统计 + 总开态数。
    标签             ：V/E/β₁（加和量）+ ρ（max 量）+ λ₂（结构常数）。
    """
    X, y, meta = [], [], []
    for A in range(A_min, A_max + 1):
        for kdist in k_partitions(A):
            seen_desc = set()
            for n_open in range(0, A + 1):
                pats = [tuple("p" for _ in range(k)) for k in kdist]
                remaining = n_open
                pat_list = [list(p) for p in pats]
                while remaining > 0:
                    placed = False
                    for gidx in range(len(kdist)):
                        if remaining <= 0:
                            break
                        if "p" in pat_list[gidx]:
                            j = pat_list[gidx].index("p")
                            pat_list[gidx][j] = "n"
                            remaining -= 1
                            placed = True
                    if not placed:
                        break
                if remaining > 0:
                    continue
                pat = [tuple(p) for p in pat_list]
                desc = descriptor(kdist, n_open, A_max)
                key = tuple(sorted(desc.items()))
                if key in seen_desc:
                    continue
                seen_desc.add(key)
                groups = [("grp%d" % gi, [("b%s_%s" % (chr(97 + gi), chr(97 + j)), pat[gi][j])
                                          for j in range(kdist[gi])])
                          for gi in range(len(kdist))]
                try:
                    G, _led = assemble(groups)
                except Exception:
                    continue
                # 注意：**不再要求连通**（多群天然不连通，E1）
                inv = invariants(G)
                X.append(desc)
                y.append({k: inv[k] for k in TARGET_KEYS})
                meta.append("A=%d kdist=%s n_open=%d cc=%d" %
                            (A, kdist, n_open, nx.number_connected_components(G)))
    return X, y, meta


# ---------------------------------------------------------------- 模型
class SurrogateSolver(nn.Module):
    """代理求解器：k 分布描述符 → 图不变量。

    架构对齐 sre_ai.module.SREAIModule：
      · topo_proj : Linear(in_dim, hidden)      —— 对应其拓扑投影层
      · mlp       : num_layers × (Linear→LayerNorm→GELU→Dropout) —— 逐字同构
      · head      : Linear(hidden, n_target)    —— 其 classifier 换成回归头
    """

    def __init__(self, in_dim: int, n_target: int,
                 hidden_dim: int = 64, num_layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.in_dim, self.n_target = in_dim, n_target
        self.topo_proj = nn.Linear(in_dim, hidden_dim)
        layers, d_in = [], hidden_dim
        for _ in range(num_layers):
            layers += [nn.Linear(d_in, hidden_dim), nn.LayerNorm(hidden_dim),
                       nn.GELU(), nn.Dropout(dropout)]
            d_in = hidden_dim
        self.mlp = nn.Sequential(*layers)
        self.head = nn.Linear(hidden_dim, n_target)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.mlp(self.topo_proj(x)))


# ---------------------------------------------------------------- 训练
def train_surrogate(X, y, epochs=4000, lr=3e-3, seed=0, num_layers=2,
                    hidden_dim=64, val_frac=0.2, verbose=True):
    torch.manual_seed(seed); np.random.seed(seed)
    keys = sorted(X[0].keys())
    Xarr = np.array([[r[k] for k in keys] for r in X], dtype=np.float32)
    Yarr = np.array([[r[k] for k in TARGET_KEYS] for r in y], dtype=np.float32)
    xm, xs = Xarr.mean(0), Xarr.std(0) + 1e-8
    ym, ys = Yarr.mean(0), Yarr.std(0) + 1e-8
    Xn, Yn = (Xarr - xm) / xs, (Yarr - ym) / ys

    n = len(Xn)
    perm = np.random.permutation(n)
    n_val = max(1, int(n * val_frac))
    val_idx, tr_idx = perm[:n_val], perm[n_val:]
    Xt, Yt = torch.tensor(Xn[tr_idx]), torch.tensor(Yn[tr_idx])
    Xv, Yv = torch.tensor(Xn[val_idx]), torch.tensor(Yn[val_idx])

    model = SurrogateSolver(len(keys), len(TARGET_KEYS), hidden_dim, num_layers)
    n_param = sum(p.numel() for p in model.parameters())
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)

    best = dict(val=1e9, state=None, epoch=-1)
    for ep in range(epochs):
        model.train(); opt.zero_grad()
        loss = F.mse_loss(model(Xt), Yt)
        loss.backward(); opt.step(); sched.step()
        if ep % max(1, epochs // 10) == 0 or ep == epochs - 1:
            model.eval()
            with torch.no_grad():
                vloss = F.mse_loss(model(Xv), Yv).item()
            if vloss < best["val"]:
                best = dict(val=vloss, epoch=ep,
                            state={k: v.clone() for k, v in model.state_dict().items()})
            if verbose:
                print("  ep %5d  train %.6f  val %.6f" % (ep, loss.item(), vloss), flush=True)
    model.load_state_dict(best["state"])

    model.eval()
    with torch.no_grad():
        pred = model(torch.tensor(Xn)).numpy() * ys + ym
    metrics = {}
    for j, k in enumerate(TARGET_KEYS):
        metrics[k] = dict(
            mae=float(np.abs(pred[:, j] - Yarr[:, j]).mean()),
            rel=float((np.abs(pred[:, j] - Yarr[:, j]) / (np.abs(Yarr[:, j]) + 1e-9)).mean()),
        )
    info = dict(keys=keys, xm=xm, xs=xs, ym=ym, ys=ys, n_param=n_param,
                n_train=len(tr_idx), n_val=n_val, best_val=best["val"], best_epoch=best["epoch"])
    return model, metrics, info


def predict_one(model, info, desc: Dict[str, float]) -> Dict[str, float]:
    x = np.array([desc[k] for k in info["keys"]], dtype=np.float32)
    x = (x - info["xm"]) / info["xs"]
    with torch.no_grad():
        p = model(torch.tensor(x).unsqueeze(0)).numpy()[0] * info["ys"] + info["ym"]
    return dict(zip(TARGET_KEYS, [float(v) for v in p]))


# ---------------------------------------------------------------- 主
def main():
    os.makedirs("figures", exist_ok=True)
    print("=" * 78)
    print("SRE 核子线 · 代理求解器（借 sre-ai 的 SREAIModule 架构）")
    print("=" * 78)
    print()
    print("[0] 角色界定")
    print("    学 : k 分布 -> 图不变量（本可精确算）")
    print("    不学: k 分布 -> 实测半衰期（标签无物理真值）")
    print("    收益: 工程（速度）；非收益: 物理（新知识）")
    print()
    print("    枚举层实测发现（决定描述符设计）：")
    print("      同一共享环内，开哪个体 → 同构；开几个体 → 不变量相同。")
    print("      ⇒ 描述符只编码 (k 分布, 总开态数)，不编码『开在哪』。")
    print()

    t0 = time.time()
    X, y, meta = enum_samples(2, 12)
    print("[1] 样本枚举（SRE 内部，标签精确无噪声）")
    print("    A 范围 2..12（含 d/³H/³He/⁴He 的真实 k 分布），样本 n = %d" % len(X))
    print("    覆盖 A = %s" % sorted({int(r["A"]) for r in X}))
    print("    维度 in_dim = %d，回归目标 %d：%s" % (len(X[0]), len(TARGET_KEYS), TARGET_KEYS))
    print("    样例（前 5）：")
    for i in range(min(5, len(meta))):
        print("      %-38s -> b1=%.1f rho=%.6f"
              % (meta[i], y[i]["b1"], y[i]["rho"]))
    print("    枚举耗时 %.2f s" % (time.time() - t0))

    print()
    print("[2] 训练（架构 = sre-ai SREAIModule：topo_proj → MLP(LayerNorm/GELU/Dropout) → head）")
    model, metrics, info = train_surrogate(X, y)
    print("    参数量 = %d   训练/验证 = %d / %d   样本/参数 = %.2f"
          % (info["n_param"], info["n_train"], info["n_val"], len(X) / info["n_param"]))
    print("    最佳验证 MSE = %.3e (ep %d)" % (info["best_val"], info["best_epoch"]))

    print()
    print("[5] 逐量精度（反标准化，原始量纲）")
    print("    %-10s %-14s %s" % ("量", "MAE", "平均相对误差"))
    for k in TARGET_KEYS:
        print("    %-10s %-14.6f %.4f%%" % (k, metrics[k]["mae"], metrics[k]["rel"] * 100))

    print()
    print("[3] 结构律验证（本轮新发现，与论文 §12.11(1′) 对照）")
    rho_single = {}
    for k in range(2, 13):
        Gk, _ = assemble([("g0", [("a%d" % j, "p") for j in range(k)])])
        rho_single[k] = invariants(Gk)["rho"]
    print("    ρ_single(k) = %s" % {k: round(v, 6) for k, v in rho_single.items() if k <= 7})
    laws_ok = {"加和律 V/E/β₁": True, "max 律 ρ": True, "cc=群数": True}
    # 注意：只测 n_group <= 3 的可构造情形（见 k_partitions 的群数上限说明）
    law_cases = [kd for kd in [(3, 3), (2, 2, 2), (2, 3), (4, 2), (5, 3), (6, 3, 2)]
                 if len(kd) <= 3]
    for kd in law_cases:
        Gk, _ = assemble([("g%d" % gi, [("g%d_%d" % (gi, j), "p") for j in range(k)])
                          for gi, k in enumerate(kd)])
        inv = invariants(Gk)
        cc = nx.number_connected_components(Gk)
        v_ok = abs(inv["V"] - sum(9 * k + 3 for k in kd)) < 1e-9
        e_ok = abs(inv["E"] - sum(15 * k + 3 for k in kd)) < 1e-9
        b_ok = abs(inv["b1"] - sum(6 * k + 1 for k in kd)) < 1e-9
        r_ok = abs(inv["rho"] - max(rho_single[k] for k in kd)) < 1e-9
        c_ok = (cc == len(kd))
        laws_ok["加和律 V/E/β₁"] &= (v_ok and e_ok and b_ok)
        laws_ok["max 律 ρ"] &= r_ok
        laws_ok["cc=群数"] &= c_ok
        print("    k=%-14s cc=%d ρ=%.9f(=%s) V=%d E=%d β₁=%d  %s"
              % (str(kd), cc, inv["rho"], "max ρ_single" if r_ok else "?",
                 int(inv["V"]), int(inv["E"]), int(inv["b1"]),
                 "✓" if (v_ok and e_ok and b_ok and r_ok and c_ok) else "✗"))
    for name, ok in laws_ok.items():
        print("    → %-16s %s" % (name, "成立" if ok else "不成立"))
    print("    ⚠ 未决项：cc = 群数 ⇒ **环间连接机制在装配规则中缺失**（本次新登记）")

    print()
    print("[4] 交叉检验：我们自己的 4 个实测核（A≤4 的真实 k 分布）")
    known = [("d", (2,)), ("³H", (3,)), ("³He", (3,)), ("⁴He", (4,))]
    rows = []
    for name, kd in known:
        G, _l = assemble([("g0", [("g%d" % j, "p") for j in range(k)]) for k in kd])
        inv = invariants(G)
        desc = descriptor(kd, 0)
        p = predict_one(model, info, desc)
        rows.append(dict(name=name, kdist=list(kd), exact={k: inv[k] for k in TARGET_KEYS}, pred=p))
        print("    %-4s k=%-6s 精确 β₁=%-3d ρ=%.6f | 代理 β₁=%.3f ρ=%.6f"
              % (name, str(kd), int(inv["b1"]), inv["rho"], p["b1"], p["rho"]))

    print()
    print("[6] 判读")
    worst = max(metrics[k]["rel"] for k in TARGET_KEYS)
    print("    最差相对误差 = %.4f%%（目标 = %s）" % (worst * 100, TARGET_KEYS))
    print("    → %s" % ("代理求解器成立（工程用途）"
                        if worst < 0.05 else "精度不足，需增加样本或调架构"))
    print("    ⚠ 本品只替代『昂贵图计算』；**不可**用于预测任何实测物理量。")

    result = dict(
        n_samples=len(X), in_dim=len(info["keys"]), n_param=info["n_param"],
        n_train=info["n_train"], n_val=info["n_val"],
        best_val=info["best_val"], best_epoch=info["best_epoch"],
        targets=TARGET_KEYS, metrics=metrics,
        known_cases=rows,
        descriptor_keys=info["keys"],
        note="代理求解器：学 k分布->图不变量。不可用于物理预测。",
    )
    with open("_surrogate_solver_results.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    torch.save(model.state_dict(), "figures/_surrogate_solver.pt")
    print()
    print("[written] _surrogate_solver_results.json, figures/_surrogate_solver.pt")
    print("=" * 78)


if __name__ == "__main__":
    main()
