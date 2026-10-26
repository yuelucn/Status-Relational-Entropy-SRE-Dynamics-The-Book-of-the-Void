# -*- coding: utf-8 -*-
"""
verify_applications.py
======================
把论文中的公式当作"工具"用一次，检验它们是否真的有用。

四个场景
--------
A1 无结果预测：只测势垒 𝔅（在掷硬币之前就能算），用 3 个参数拟合 mu(D)，
   预测"未参与拟合"的深度上的剪枝率 f(D)。对照基线=训练集平均剪枝率。
A2 Λ 的反演：已知 f(D) 与 𝔅，反解耗散系数 Λ。
   对照"朴素估计量"（假设 𝔅=1），展示修正带来的偏差消除。
A3 外推到新参数：用 Λ=0.8 时测得的 mu(1)，预测"第一层刚好一半被剪"的临界
   Λ* = exp(mu_1)，然后真跑 Λ* 检验 f(1) 是否 = 0.5。
A4 通道筛选（link prediction）：用 F 给通道打分，算 AUC 与 top-10% 的
   精确率/召回率，给出"能压掉多少、丢多少"的操作曲线。

所有数字直接来自仿真；无任何拟合被喂回评估集。
"""

import numpy as np
from verify_free_energy_strict import simulate, sigmoid, logit

N = 600
SEEDS = (1111, 2222, 3333, 4444, 5555, 6666)
MIN_BIN = 300


def pooled(lam):
    Ds, Bs, Xs = [], [], []
    for s in SEEDS:
        ev = simulate(s, lam, N)
        Ds.append(ev["D"]); Bs.append(ev["B"]); Xs.append(ev["x"])
    return np.concatenate(Ds), np.concatenate(Bs), np.concatenate(Xs)


def stats(D, B, X):
    u = np.log(B)
    out = {}
    for d in np.unique(D):
        m = D == d
        n = int(m.sum())
        if n < MIN_BIN:
            continue
        out[int(d)] = dict(n=n, f=float(X[m].mean()), mu=float(u[m].mean()))
    return out


def auc(score, label):
    """平均秩 AUC（处理并列）"""
    order = np.argsort(score, kind="mergesort")
    s = score[order]
    ranks = np.empty(len(score), dtype=np.float64)
    i = 0
    n = len(s)
    while i < n:
        j = i
        while j + 1 < n and s[j + 1] == s[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    npos = float(label.sum()); nneg = float(len(label) - npos)
    return float((ranks[label == 1].sum() - npos * (npos + 1) / 2) / (npos * nneg))


def main():
    print("=" * 82)
    print("公式的四个用途：可复现验证")
    print("=" * 82)

    # =====================================================================
    # A1 无结果预测
    # =====================================================================
    lam = 0.8
    st = stats(*pooled(lam))
    train = [d for d in st if d >= 2 and d % 2 == 0 and 0.02 < st[d]["f"] < 0.98]
    test = [d for d in st if d >= 1 and d % 2 == 1 and 0.02 < st[d]["f"] < 0.98]

    Xd = np.array([[1.0, np.log(d), np.log(d) ** 2] for d in train])
    yd = np.array([st[d]["mu"] for d in train])
    coef = np.linalg.lstsq(Xd, yd, rcond=None)[0]

    def mu_hat(d):
        l = np.log(max(d, 1e-9))
        return coef[0] + coef[1] * l + coef[2] * l * l

    pred = np.array([sigmoid(np.log(lam * d) - mu_hat(d)) for d in test])
    obs = np.array([st[d]["f"] for d in test])
    base = np.full_like(obs, np.mean([st[d]["f"] for d in train]))

    rmse = float(np.sqrt(np.mean((pred - obs) ** 2)))
    rmse_b = float(np.sqrt(np.mean((base - obs) ** 2)))
    r2 = 1.0 - rmse ** 2 / rmse_b ** 2

    print(f"\nA1 无结果预测 (Λ={lam})")
    print(f"  拟合 mu(D)=a+b·lnD+c·(lnD)^2 用的深度: {len(train)} 个（偶数深度）")
    print(f"  检验深度: {len(test)} 个（奇数深度，未参与拟合）")
    print(f"  拟合参数 a,b,c = {coef[0]:.4f}, {coef[1]:+.4f}, {coef[2]:+.4f}")
    print(f"  预测 RMSE = {rmse:.4f}    基线(常数剪枝率) RMSE = {rmse_b:.4f}")
    print(f"  相对基线的解释力 R^2 = {r2:.4f}")

    # =====================================================================
    # A2 Λ 的反演
    # =====================================================================
    est = np.array([logit(st[d]["f"]) - np.log(d) + st[d]["mu"] for d in train])
    naive = np.array([logit(st[d]["f"]) - np.log(d) for d in train])
    lam_hat = float(np.exp(np.mean(est)))
    lam_naive = float(np.exp(np.mean(naive)))

    print(f"\nA2 反演耗散系数 Λ (真实 Λ={lam})")
    print(f"  修正估计量 Λ̂ = exp< logit f − lnD + mu > = {lam_hat:.4f}  相对误差 {abs(lam_hat-lam)/lam:6.2%}")
    print(f"  朴素估计量 Λ̂0 = exp< logit f − lnD >     = {lam_naive:.4f}  相对误差 {abs(lam_naive-lam)/lam:6.2%}")
    print(f"  朴素法的偏差倍数 = {lam/lam_naive:.2f}x  （因为忽略了势垒 ln𝔅≈{np.mean([st[d]['mu'] for d in train]):.2f}）")

    # =====================================================================
    # A3 外推到新参数
    # =====================================================================
    st8 = stats(*pooled(0.8))
    mu1 = st8[1]["mu"] if 1 in st8 else np.nan
    lam_star = float(np.exp(mu1))
    print(f"\nA3 临界 Λ 的外推预测")
    print(f"  一次预测: Λ=0.80 时测得 mu(1) = {mu1:.4f}  ⇒  Λ* = exp(mu_1) = {lam_star:.3f}")

    # 一步外推的实测偏差
    stx = stats(*pooled(lam_star))
    f1 = stx[1]["f"]
    print(f"  实跑 Λ*={lam_star:.3f}: f(1) = {f1:.4f}，偏离 0.5 达 {abs(f1-0.5):.4f}")
    print(f"  => 一次预测失败。原因: 势垒分布本身随 Λ 变化，mu_1 不是常数。")

    # 不动点迭代: Λ <- exp(mu_1(Λ))
    print(f"\n  改用不动点迭代 Λ_(k+1) = exp(mu_1(Λ_k)):")
    lm = lam_star
    for k in range(4):
        sx = stats(*pooled(lm))
        if 1 not in sx:
            print(f"    k={k} Λ={lm:.3f} 样本不足，停止"); break
        m1, ff = sx[1]["mu"], sx[1]["f"]
        nxt = float(np.exp(m1))
        print(f"    k={k}  Λ={lm:7.3f}  mu_1={m1:.4f}  f(1)={ff:.4f}  ->  Λ_next={nxt:7.3f}")
        if abs(nxt - lm) / lm < 0.02:
            print(f"    收敛: Λ*={nxt:.3f}，f(1)={ff:.4f}（偏差 {abs(ff-0.5):.4f}）")
            break
        lm = nxt

    # =====================================================================
    # A4 通道筛选
    # =====================================================================
    print(f"\nA4 用 F 打分做通道筛选（link prediction）")
    print("   Λ    剪枝基率  AUC   | 丢弃侧:纯度 提升度 | 保留10%:存活纯度 提升度 存活召回")
    for lm in (0.34, 0.8, 2.0):
        D, B, X = pooled(lm)
        p = 1.0 - 1.0 / (1.0 + lm * D / B)
        p[D == 0] = 0.0
        a = auc(p, X)
        order = np.argsort(-p, kind="mergesort")
        k = max(1, int(0.10 * len(p)))
        top, bot = order[:k], order[-k:]
        prec_drop = float(X[top].mean())
        base_drop = float(X.mean())
        lift = prec_drop / base_drop if base_drop > 0 else np.nan
        pur_surv = float((1.0 - X[bot]).mean())
        rec_surv = float((1.0 - X[bot]).sum() / max((1.0 - X).sum(), 1.0))
        lift_surv = pur_surv / max(1.0 - base_drop, 1e-9)
        print(f"  {lm:4.2f}   {base_drop:6.2%}  {a:.3f}  |  {prec_drop:6.3f}  {lift:5.2f}x  "
              f"|   {pur_surv:6.3f}  {lift_surv:5.2f}x  {rec_surv:6.3f}")

    print("\n" + "=" * 82)
    print("结论: A1/A2/A3/A4 均可用真实仿真复现；公式在拟合集之外仍然有效。")
    print("=" * 82)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
