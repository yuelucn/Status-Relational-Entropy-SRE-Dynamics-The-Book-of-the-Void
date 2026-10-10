"""
β(N) 的耗散理论推导与验证
==========================
理论来源: combined_C.md《层级耗散自组织二元网络动力学理论》(v1.1) §二、§四

主方程 (休眠/剪枝概率, §二.2):
    p_prune(d, E) = 1 - 1/(1 + λ·d/(E+1))
    d = n - max(i,j)          (全局动态测地线深度 = 因果拓扑步长)
    E = |Σ_k S_ik·S_kj|       (局部阻挫能量)

推导:
  1) E 是 n 个 ±1 项的随机符号和  →  E ~ c·n^α   (α = 1/2)
  2) C = <p_prune> 在深度 d∈[0,n] 上积分 (固定 γ=λ/n^0 的连续近似):
        C(z) = 1 - ln(1+z)/z,     z ≡ λ·n/(E+1) ~ λ·n^{1-α}/c
  3) β = -d lnC/d lnλ ;  z→∞ 时 β(z) ≈ (ln z - 1)/z  →  β∞ = 0, 收敛极慢

验证:
  A) 随机 ±1 矩阵验证 E ~ √n
  B) 从观测 C(λ,N) 反演 z, 拟合 z = K·λ^p·N^q
  C) 由普适曲线 C(z) 预测 β(N), 与观测 4 点对比; 外推 N→∞
  D) dbeta ratio 预测 (对照: 1/N 模型 = 2.0, 本次实测 ≈ 1.1)
"""
import numpy as np
import pickle
import warnings
from scipy.optimize import brentq, curve_fit

warnings.filterwarnings('ignore')

# ---------------- 观测数据 (一致协议: seeds[0,1], window=60, RE_LO=5000) ----------------
LAMS = np.array([0.01, 0.05, 0.10, 0.20, 0.34])
ALPHA_RE = 783.2
RE = ALPHA_RE / LAMS
RE_LO = 5000.0

OBS_C = {
    1600: np.array([0.3012, 0.6940, 0.8403, 0.9221, 0.9528]),
    3200: np.array([0.3953, 0.7982, 0.9065, 0.9561, 0.9737]),
    6400: np.array([0.4949, 0.8761, 0.9469, 0.9751, 0.9852]),
}
OBS_BETA = {800: 0.5543, 1600: 0.4584, 3200: 0.3739, 6400: 0.2955}


# ---------------- 普适曲线 C(z) = 1 - ln(1+z)/z ----------------
def C_of_z(z):
    z = np.asarray(z, dtype=float)
    return 1.0 - np.log1p(z) / np.maximum(z, 1e-300)


def z_of_C(C):
    """反演 z: 解 ln(1+z)/z = 1-C"""
    t = 1.0 - C
    if t <= 0:
        return np.inf
    f = lambda z: np.log1p(z) / z - t
    return brentq(f, 1e-12, 1e12)


# ---------------- A) E ~ √n 随机矩阵检验 ----------------
def check_E_scaling():
    rng = np.random.default_rng(0)
    ns, med = [], []
    for n in [50, 100, 200, 400, 800]:
        S = rng.choice([-1.0, 1.0], size=(n, n))
        P = S @ S                      # (S²)_{ij} = Σ_k S_ik S_kj
        off = P[~np.eye(n, dtype=bool)]
        ns.append(n)
        med.append(np.median(np.abs(off)))
    ns = np.array(ns, float)
    med = np.array(med)
    alpha = np.polyfit(np.log(ns), np.log(med), 1)
    print("[A] E_local 标度 (随机 ±1 矩阵):")
    for n, m in zip(ns.astype(int), med):
        print(f"    n={n:4d}  median|E|={m:8.3f}   |E|/√n={m/np.sqrt(n):.3f}")
    print(f"    拟合  |E| ~ n^α  →  α = {alpha[0]:.4f}  (理论 1/2)\n")
    return float(alpha[0])


# ---------------- B) 反演 z, 拟合 z = K λ^p N^q ----------------
def fit_z_scaling():
    pts = []
    for N, Cs in OBS_C.items():
        for lam, C in zip(LAMS, Cs):
            z = z_of_C(C)
            pts.append((lam, N, z))
    lam = np.array([p[0] for p in pts])
    N = np.array([p[1] for p in pts], float)
    z = np.array([p[2] for p in pts])

    def model(X, logK, p, q):
        l, NN = X
        return logK + p * np.log(l) + q * np.log(NN)

    popt, _ = curve_fit(model, (lam, N), np.log(z), p0=[0.0, 1.0, 0.5])
    logK, p, q = popt
    fit = model((lam, N), *popt)
    ss_res = np.sum((np.log(z) - fit) ** 2)
    ss_tot = np.sum((np.log(z) - np.log(z).mean()) ** 2)
    R2 = 1 - ss_res / ss_tot

    print("[B] 反演 z(λ,N) = K·λ^p·N^q:")
    print(f"    K = {np.exp(logK):.3g}   p = {p:.3f}   q = {q:.3f}   R²(log z) = {R2:.4f}")
    print(f"    → z 随 N 增长 (q={q:.2f}>0) ⇒ β 随 N 下降")
    print(f"    → 注意 q<1: z 增长慢于 N ⇒ C 收敛慢 ⇒ 非 1/N\n")
    # 逐 N 展示反演 z
    for N in sorted(OBS_C):
        zs = [z_of_C(C) for C in OBS_C[N]]
        print(f"    N={N:5d}: z(λ=0.01..0.34) = " +
              ", ".join(f"{v:.2f}" for v in zs))
    print()
    return np.exp(logK), p, q, R2


# ---------------- C) 由 C(z) 预测 β(N) ----------------
def predict_beta(K, p, q, Ns):
    out = {}
    for N in Ns:
        z = K * LAMS ** p * N ** q
        C = C_of_z(z)
        m = RE >= RE_LO
        lx = np.log10(RE[m])
        ly = np.log10(1.0 / C[m])
        slope = np.polyfit(lx, ly, 1)[0]
        out[N] = slope
    return out


def main():
    print("=" * 68)
    print("β(N) 耗散理论推导与验证")
    print("=" * 68 + "\n")

    alpha = check_E_scaling()
    K, p, q, R2 = fit_z_scaling()

    print("[C] 由普适曲线 C(z) 预测 β(N) vs 观测:")
    pred = predict_beta(K, p, q, [800, 1600, 3200, 6400])
    print(f"    {'N':>7s} {'β_obs':>9s} {'β_pred':>9s} {'差':>9s}")
    for N in [800, 1600, 3200, 6400]:
        bo = OBS_BETA.get(N, np.nan)
        bp = pred[N]
        print(f"    {N:7d} {bo:9.4f} {bp:9.4f} {bp-bo:+9.4f}")
    print()

    # D) 外推
    print("[D] 外推 (理论预测 β∞ = 0, 慢收敛):")
    extrap = predict_beta(K, p, q, [12800, 25600, 51200, 102400])
    for N in [800, 1600, 3200, 6400, 12800, 25600, 51200, 102400]:
        b = extrap.get(N, pred.get(N))
        print(f"    N={N:7d}  β_pred={b:.4f}")
    print(f"    N→∞        β_pred→0   (>1/N 幂律的 ln(z)/z 慢衰减)\n")

    # dbeta ratio 预测 vs 观测
    print("[E] dbeta ratio (每 2×N):")
    Nlist = [800, 1600, 3200, 6400]
    bpred = [pred[N] for N in Nlist]
    bobs = [OBS_BETA[N] for N in Nlist]
    for i in range(len(Nlist) - 2):
        rp = (bpred[i] - bpred[i + 1]) / (bpred[i + 1] - bpred[i + 2])
        ro = (bobs[i] - bobs[i + 1]) / (bobs[i + 1] - bobs[i + 2])
        print(f"    [{Nlist[i]}→{Nlist[i+1]}]/[{Nlist[i+1]}→{Nlist[i+2]}]: "
              f"pred={rp:.3f}  obs={ro:.3f}")

    out = dict(alpha=alpha, K=K, p=p, q=q, R2_z=R2,
               beta_pred=pred, beta_extrap=extrap, obs_beta=OBS_BETA,
               obs_C=OBS_C)
    with open('beta_dissipation_theory.pkl', 'wb') as f:
        pickle.dump(out, f)
    print("\n已保存: beta_dissipation_theory.pkl")


if __name__ == '__main__':
    main()