# -*- coding: utf-8 -*-
"""可视化: SRE MDS 反演 —— 几何从纯关系图涌现。
生成: benzene / Fe4S4 的 (原始 vs 纯拓扑MDS vs 加权MDS) 3D 对比 + 反演忠诚性柱状图。
依赖 _sre_mds_inversion.py 的等价逻辑(此处自包含, 便于独立出图)。"""
import sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa
HERE = r"C:\mywork\vasp"
sys.path.insert(0, HERE)
from _p3_p1a_final_scaffolds import mds_coords_from_dmat

# ── 分子(与 _sre_mds_inversion 一致)────────────────────────────────────
def ring(n, r, z=0.0):
    a = np.linspace(0, 2*math.pi, n, endpoint=False)
    return [[r*math.cos(t), r*math.sin(t), z] for t in a]

bc, bh = ring(6, 1.397), ring(6, 1.397+1.084)
benzene = (np.array(bc+bh), ["C"]*6+["H"]*6,
           [(i,(i+1)%6) for i in range(6)] + [(i,6+i) for i in range(6)])

s = 1.35
verts = np.array([(sx,sy,sz) for sx in (-s,s) for sy in (-s,s) for sz in (-s,s)])
el = ["Fe"]*8
for i,(x,y,z) in enumerate(verts):
    if ((1 if x>0 else 0)+(1 if y>0 else 0)+(1 if z>0 else 0)) % 2: el[i]="S"
edges = [(i,j) for i in range(8) for j in range(i+1,8)
         if abs(sum(abs(a-b) for a,b in zip(verts[i],verts[j])) - 2*s) < 1e-6]
fe4s4 = (verts, el, edges)

def floyd(bonds, n, wfun):
    D = np.full((n,n), 1e9); np.fill_diagonal(D,0.0)
    for (i,j) in bonds:
        w = wfun(i,j); D[i,j]=D[j,i]=w
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i,k]+D[k,j] < D[i,j]: D[i,j]=D[i,k]+D[k,j]
    return D

def procrustes(X, Y):
    Y=np.asarray(Y,float); X=np.asarray(X,float)
    if X.shape[1]<Y.shape[1]: X=np.pad(X,((0,0),(0,Y.shape[1]-X.shape[1])))
    Xc=X-X.mean(0); Yc=Y-Y.mean(0)
    U,S,Vt=np.linalg.svd(Yc.T@Xc, full_matrices=False); R=U@Vt
    c=np.trace(R.T@Yc.T@Xc)/np.trace(Xc.T@Xc)
    return c*(Xc@R)

def run(X0, bonds):
    X0=np.asarray(X0,float); n=len(X0)
    L={(min(i,j),max(i,j)):float(np.linalg.norm(X0[i]-X0[j])) for (i,j) in bonds}
    Duw=floyd(bonds,n,lambda i,j:1.0)
    Dw =floyd(bonds,n,lambda i,j:L[(min(i,j),max(i,j))])
    return mds_coords_from_dmat(Duw), mds_coords_from_dmat(Dw)

# ── 绘图 ───────────────────────────────────────────────────────────────
def plot_mol(ax, X, bonds, color, title, elev=30, azim=-60):
    xs,ys,zs = X[:,0],X[:,1],X[:,2]
    ax.scatter(xs,ys,zs,c=color,s=40,depthshade=False)
    for (i,j) in bonds:
        ax.plot([xs[i],xs[j]],[ys[i],ys[j]],[zs[i],zs[j]],c=color,lw=1.2,alpha=0.8)
    ax.set_title(title,fontsize=10); ax.set_box_aspect((1,1,1))
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.view_init(elev=elev, azim=azim)

fig = plt.figure(figsize=(13,9))
specs = [("benzene","苯",benzene),("fe4s4",None,fe4s4)]
for row,(key,label,mol) in enumerate(specs):
    X0,els,bonds = mol
    Xu,Xw = run(X0,bonds)
    X0c = X0 - X0.mean(0)                              # 原始(居中)
    Xu_al = procrustes(Xu, X0)                         # 反演结果对齐到原始朝向
    Xw_al = procrustes(Xw, X0)
    ev, az = (90, -90) if key == "benzene" else (22, -58)   # 苯环俯视; 立方体斜视
    ax1=fig.add_subplot(2,3,row*3+1,projection='3d'); plot_mol(ax1,X0c,bonds,'#1f77b4',f"{label or key}\noriginal geometry (coords given)",ev,az)
    ax2=fig.add_subplot(2,3,row*3+2,projection='3d'); plot_mol(ax2,Xu_al,bonds,'#d62728',"MDS from topology only\n(bonds, no coords)",ev,az)
    ax3=fig.add_subplot(2,3,row*3+3,projection='3d'); plot_mol(ax3,Xw_al,bonds,'#2ca02c',"MDS weighted\n(bonds + lengths)",ev,az)
fig.suptitle("SRE MDS inversion: spatial structure emerges from relation graph (blue=orig / red=topology / green=weighted)",fontsize=13)
fig.tight_layout(rect=[0,0,1,0.96])
fig.savefig(r"C:\mywork\vasp\sre_mds_inversion_3d.png",dpi=130)
print("[OK] sre_mds_inversion_3d.png")

# 反演忠诚性柱状图
import json
res=json.load(open(r"C:\mywork\vasp\sre_mds_inversion_results.json"))
names=list(res.keys())
labels=["H2","He2","H2O","benzene","Fe4S4"]
pres=[res[n]["mds"]["reconstruction"]["unweighted_topology"]["r_mds_preserves_D"] if res[n]["mds"].get("mds_applicable") else 0 for n in names]
real=[res[n]["mds"]["reconstruction"]["unweighted_topology"]["r_emerged_vs_real"] if res[n]["mds"].get("mds_applicable") else 0 for n in names]
x=np.arange(len(names)); w=0.35
fig2,ax=plt.subplots(figsize=(9,4.5))
ax.bar(x-w/2,pres,w,label="inversion fidelity r(coord-dist reproduces D)",color="#d62728")
ax.bar(x+w/2,real,w,label="emerged geom vs real chemistry r",color="#1f77b4")
ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0.9,1.005)
ax.set_ylabel("Pearson r"); ax.legend(); ax.set_title("MDS inversion fidelity: geometry solved from relation matrix D")
for i,(p,r) in enumerate(zip(pres,real)):
    ax.text(i-w/2,p+0.002,f"{p:.3f}",ha='center',fontsize=8)
    ax.text(i+w/2,r+0.002,f"{r:.3f}",ha='center',fontsize=8)
fig2.tight_layout(); fig2.savefig(r"C:\mywork\vasp\sre_mds_inversion_fidelity.png",dpi=130)
print("[OK] sre_mds_inversion_fidelity.png")
