# -*- coding: utf-8 -*-
"""
SRE MDS 反演管线：验证"空间是 MDS 反演的涌现产物"。

核心主张（来自 combined_E.md）：底层是 dimension-free 二进制关系图，本身无坐标/无度量；
几何不是被"给定"的，而是从关系距离矩阵 D 经 MDS 反演"求解"出来的同态投影。

本脚本做法：
  1. 用真实分子图（显式 bonds，跳过 infer_bonds 半径兜底）构造 SRE 关系图。
  2. 从关系图生成三种"关系距离矩阵"：
       D_unw  : 纯拓扑最短路径（所有键等长=1）—— 不喂任何长度信息
       D_w    : 按真实键长加权的最短路径
       D_sre  : SRE 平滑邻接 A_s 派生的关系距离 (1/A_s 沿键路径)
  3. 古典 MDS (=mds_coords_from_dmat) 反演 → 重建 3D 坐标 X_rec。
  4. 与真实几何 X0 做 Procrustes 对齐，量化重建保真度（RMSD_Å, 距离矩阵 Pearson r）。
  5. 同时报告"前几何"拓扑不变量（λ2_q, n_loops, κ_q, q_disp），强调它们在任何坐标之前就存在。

运行: python _sre_mds_inversion.py
"""
import sys, json, math
import numpy as np
HERE = r"C:\mywork\vasp"
sys.path.insert(0, HERE)
from _p3_p1a_final_scaffolds import mds_coords_from_dmat
import sre_electronic_ops_v11 as E

# ── 真实分子图（键拓扑来自化学知识，键长取真实几何）─────────────────────────
def ring(n, r, z=0.0):
    a = np.linspace(0, 2*math.pi, n, endpoint=False)
    return [[r*math.cos(t), r*math.sin(t), z] for t in a]

# H2 / He2
h2  = ([[0,0,0],[0.741,0,0]], ["H","H"], [(0,1)])
he2 = ([[0,0,0],[2.97,0,0]],  ["He","He"], [])        # 真实: 无键

# H2O
oh, ang = 0.958, math.radians(104.5)
h2o = ([[0,0,0],[oh,0,0],[oh*math.cos(ang), oh*math.sin(ang), 0]],
       ["O","H","H"], [(0,1),(0,2)])

# 苯 (C-C 1.397, C-H 1.084)
bc, bh = ring(6, 1.397), ring(6, 1.397+1.084)
benz = (bc+bh, ["C"]*6+["H"]*6,
        [(i,(i+1)%6) for i in range(6)] + [(i,6+i) for i in range(6)])

# Fe4S4 立方烷 (边=2s, s=1.35 -> 边 2.7)
s = 1.35
verts = [(sx,sy,sz) for sx in (-s,s) for sy in (-s,s) for sz in (-s,s)]
fe_idx, s_idx = [], []
for i,(x,y,z) in enumerate(verts):
    par = (1 if x>0 else 0)+(1 if y>0 else 0)+(1 if z>0 else 0)
    (fe_idx if par%2==0 else s_idx).append(i)
el = ["Fe"]*8
for i in s_idx: el[i] = "S"
edges = [(i,j) for i in range(8) for j in range(i+1,8)
         if abs(sum(abs(a-b) for a,b in zip(verts[i],verts[j])) - 2*s) < 1e-6]
fe4s4 = (verts, el, edges)

CASES = {
    "H2":  h2, "He2": he2, "H2O": h2o,
    "benzene": benz, "Fe4S4_cubane": fe4s4,
}

# ── 工具 ────────────────────────────────────────────────────────────────
def floyd(bonds, n, wfun):
    D = np.full((n,n), 1e9); np.fill_diagonal(D, 0.0)
    for (i,j) in bonds:
        w = wfun(i,j)
        D[i,j] = D[j,i] = w
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i,k]+D[k,j] < D[i,j]:
                    D[i,j] = D[i,k]+D[k,j]
    return D

def procrustes(X, Y):
    """相似 Procrustes (旋转+最优均匀缩放): 把 X 对齐到 Y, 返回 (X_aligned, rmsd)。
    用均匀缩放是因为纯拓扑 MDS 只恢复形状/连通模式, 不含绝对尺度。"""
    Y = np.asarray(Y, float); X = np.asarray(X, float)
    if X.shape[1] < Y.shape[1]:                       # N=2 时 MDS 只返回 2 列, 补零对齐
        X = np.pad(X, ((0,0),(0, Y.shape[1]-X.shape[1])))
    Xc = X - X.mean(0); Yc = Y - Y.mean(0)
    U,S,Vt = np.linalg.svd(Yc.T @ Xc, full_matrices=False)
    R = U @ Vt
    c = np.trace(R.T @ Yc.T @ Xc) / np.trace(Xc.T @ Xc)   # 最优均匀缩放
    Xa = c * (Xc @ R)
    rmsd = math.sqrt(((Xa - Yc)**2).sum()/len(X))
    return Xa, rmsd

def distmat(X):
    d = np.sqrt(((X[:,None,:]-X[None,:,:])**2).sum(-1))
    return d

def pearson(a, b):
    a = a.ravel(); b = b.ravel()
    if a.std()<1e-12 or b.std()<1e-12: return float("nan")
    return float(np.corrcoef(a,b)[0,1])

def reconstruct(X0, els, bonds, A_s):
    n = len(X0)
    out = {"n_nodes": n, "n_bonds": len(bonds)}
    if len(bonds) == 0:
        out.update({"note": "无关系图 -> 无涌现几何 (孤立节点)",
                    "mds_applicable": False})
        return out, None
    # 真键长
    L = { (min(i,j),max(i,j)): float(np.linalg.norm(np.array(X0[i])-np.array(X0[j])))
          for (i,j) in bonds }
    # 三种关系距离矩阵
    D_uw  = floyd(bonds, n, lambda i,j: 1.0)
    D_w   = floyd(bonds, n, lambda i,j: L[(min(i,j),max(i,j))])
    # SRE 关系距离: 沿键路径, 边权 = 1/A_s (相互作用强度 -> 关系距离)
    D_sre = floyd(bonds, n, lambda i,j: 1.0/max(A_s[i,j], 1e-9))
    # MDS 反演
    Xu, Xw, Xs = (mds_coords_from_dmat(D_uw),
                  mds_coords_from_dmat(D_w),
                  mds_coords_from_dmat(D_sre))
    D0 = distmat(np.array(X0))
    rec = {}
    for tag, Xr, D in [("unweighted_topology", Xu, D_uw),
                       ("weighted_bondlength",  Xw, D_w),
                       ("sre_relation",         Xs, D_sre)]:
        _, rmsd = procrustes(Xr, np.array(X0))
        r_vs_real   = pearson(distmat(Xr), D0)   # 涌现几何 vs 真实化学几何
        r_preserves = pearson(distmat(Xr), D)    # 反演忠诚性: 坐标内距离是否复现输入 D
        rec[tag] = {"rmsd_vs_real_A": round(rmsd,4),
                    "r_emerged_vs_real": round(r_vs_real,4),
                    "r_mds_preserves_D": round(r_preserves,4)}
    out["mds_applicable"] = True
    out["reconstruction"] = rec
    return out, (Xu, Xw, Xs, D_uw, D_w, D_sre)

def pregeometric(X0, els, bonds):
    """前几何不变量：在任何坐标重建之前就从关系图算出。"""
    X = np.asarray(X0, float)
    chis = np.array([E.get_electronegativity(e) for e in els])
    A_s = E.build_sre_smooth_adjacency(X, atomtypes=els, bonds=bonds)
    fp = E.compute_electronic_fingerprint(X, A_s, chis, rho=0.5)
    return {"lambda2_q": round(float(fp["lambda_2_q"]),4),
            "kappa_q": round(float(fp["kappa_q"]),4),
            "n_loops": int(fp["n_loops"]),
            "q_disp": round(float(fp["q_dispersion"]),4),
            "mobius_ratio": round(float(fp["mobius_ratio"]),4)}

# ── 主流程 ────────────────────────────────────────────────────────────
results = {}
print("="*80)
print("SRE MDS 反演：几何从纯关系图涌现 (无坐标输入)")
print("="*80)
for name,(X0,els,bonds) in CASES.items():
    A_s = E.build_sre_smooth_adjacency(np.asarray(X0,float), atomtypes=els, bonds=bonds)
    pre = pregeometric(X0, els, bonds)
    rec, _ = reconstruct(X0, els, bonds, A_s)
    results[name] = {"pre_geometric_invariants": pre, "mds": rec}
    print(f"\n### {name}  (节点={rec.get('n_nodes')}, 键={rec.get('n_bonds')})")
    print(f"  前几何不变量: λ2_q={pre['lambda2_q']}  κ_q={pre['kappa_q']}  "
          f"n_loops={pre['n_loops']}  q_disp={pre['q_disp']}  mobius={pre['mobius_ratio']}")
    if rec.get("mds_applicable"):
        for tag, v in rec["reconstruction"].items():
            print(f"    MDS[{tag:22s}]  RMSD_vs_real={v['rmsd_vs_real_A']:.4f} Å  "
                  f"r(涌现vs真实)={v['r_emerged_vs_real']:+.4f}  "
                  f"r(反演忠诚,坐标距离复现D)={v['r_mds_preserves_D']:+.4f}")
    else:
        print(f"    {rec['note']}")

with open(r"C:\mywork\vasp\sre_mds_inversion_results.json","w",encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\n[OK] -> sre_mds_inversion_results.json")
